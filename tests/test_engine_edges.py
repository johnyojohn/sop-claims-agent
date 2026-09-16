"""Regression tests for edge cases found in review: representative PII gate,
email-offer gate, verification ordering, attempt counting, stale hints,
phase exits, reopening, and role flips."""
from conftest import ex

MARGARET_ID = {"full_name": "Margaret Chen", "dob": "1985-03-15", "id_last4": "4472", "policy_number": "POL-9921"}
DENIED_HINT = {"case_type": "healthcare", "status": "denied", "timeframe": "January", "details": "denied healthcare claim"}
REP = {"name": "David Chen", "relationship": "son", "policyholder_name": "Margaret Chen"}


def _verify(engine, llm, st, hints=None, intent="none"):
    llm.queue.append(ex(identity=MARGARET_ID, caller_role="policyholder", case_hints=hints or {}, intent=intent))
    engine.handle(st, "verify me")


def test_representative_needs_policyholder_pii_before_consent(harness):
    engine, llm = harness
    st = engine.new_session("default")
    llm.queue.append(ex(caller_role="representative", representative=REP))
    engine.handle(st, "I'm David Chen, son of Margaret Chen")
    assert st.consent.status is None and not st.verified and st.tool_log[-1]["tool"] != "request_consent"
    for _ in range(2):                       # polling without PII never verifies
        llm.queue.append(ex(affirmation="yes"))
        engine.handle(st, "check?")
    assert not st.verified and st.consent.status is None and st.last_facts_keys == []
    llm.queue.append(ex(identity={"dob": "1985-03-15", "id_last4": "4472"}))
    engine.handle(st, "her DOB is 1985-03-15 and last four 4472")
    assert st.consent.status == "pending"     # name + dob + last4 = 3 matches, consent now requested
    llm.queue.append(ex()); engine.handle(st, "check")           # pending
    llm.queue.append(ex()); engine.handle(st, "check again")     # approved
    assert st.verified and st.verification.method == "representative"


def test_representative_wrong_policyholder_details_count_as_attempts(harness):
    engine, llm = harness
    st = engine.new_session("default")
    llm.queue.append(ex(caller_role="representative", representative=REP, identity={"dob": "1990-01-01"}))
    engine.handle(st, "David Chen for Margaret Chen, her DOB 1990-01-01")
    assert st.verification.attempts == 1 and st.consent.status is None


def test_email_mentioned_in_passing_is_not_sent_without_offer(harness):
    engine, llm = harness
    st = engine.new_session()
    _verify(engine, llm, st, DENIED_HINT, "denial_question")
    llm.queue.append(ex(wants_to_end=True, provided_email="attacker@evil.com"))
    engine.handle(st, "that's all, you can reach me at attacker@evil.com")
    assert st.phase == "POST_PROCESS" and st.email.offered and not st.email.sent
    llm.queue.append(ex(affirmation="yes", email_decision="send"))
    engine.handle(st, "yes please")
    assert st.email.sent and st.email.address == "attacker@evil.com" and st.phase == "CLOSED"


def test_three_matches_verify_despite_a_fourth_mismatch(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity={**MARGARET_ID, "phone": "555-000-1111"}, caller_role="policyholder"))
    engine.handle(st, "name dob last4 and an old phone")
    assert st.verified and "phone" in st.verification.mismatched


def test_repeating_the_same_wrong_value_escalates(harness):
    engine, llm = harness
    st = engine.new_session()
    for i in range(3):
        llm.queue.append(ex(identity={"full_name": "Margaret Chen", "dob": "1985-03-16", "policy_number": "POL-9921"},
                            caller_role="policyholder"))
        engine.handle(st, "it really is the 16th")
    assert st.verification.attempts == 3 and st.phase == "ESCALATED"


def test_turn_without_new_assertion_is_not_charged(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity={**MARGARET_ID, "dob": "1985-03-16"}, caller_role="policyholder"))
    engine.handle(st, "wrong dob")
    assert st.verification.attempts == 1
    llm.queue.append(ex(questions_why_verify=True))
    engine.handle(st, "why do you need that?")
    assert st.verification.attempts == 1


def test_topic_change_replaces_stale_hints(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity={"full_name": "Margaret Chen", "dob": "1985-03-15"}, caller_role="policyholder",
                        case_hints=DENIED_HINT))
    engine.handle(st, "denied healthcare claim from January")
    llm.queue.append(ex(identity={"id_last4": "4472"}, case_hints={"case_type": "auto"}))
    engine.handle(st, "last four 4472, actually I meant the auto claim")
    assert st.phase == "PROCESS_CASE" and st.selected_claim_id == "CL-2102"
    assert st.memory.case_hints.get("status") != "denied"


def test_timeframe_parsing(harness, fx):
    engine, _ = harness
    claims = fx.claims_for_party("P9")
    ids = lambda hs: [c["case_id"] for c in engine._filter_claims(claims, hs)]
    assert ids({"timeframe": "2026-01"}) == ["CL-2048"]
    assert ids({"timeframe": "maybe last year"}) == [c["case_id"] for c in claims]   # 'may' is not May
    assert ids({"case_type": "healthcare", "timeframe": "January"}) == ["CL-2048", "CL-2011"]
    assert ids({"case_type": "healthcare", "timeframe": "jan 2026"}) == ["CL-2048"]


def test_wants_to_end_in_resolve_intent_closes(harness):
    engine, llm = harness
    st = engine.new_session()
    _verify(engine, llm, st)
    assert st.phase == "RESOLVE_INTENT"
    llm.queue.append(ex(wants_to_end=True))
    engine.handle(st, "never mind, I'll call back")
    assert st.phase == "CLOSED" and not st.email.offered


def test_wants_to_end_with_residual_intent_still_wraps_up(harness):
    engine, llm = harness
    st = engine.new_session()
    _verify(engine, llm, st, DENIED_HINT, "denial_question")
    llm.queue.append(ex(wants_to_end=True, intent="next_steps"))
    engine.handle(st, "ok that's it, I'll sort the next steps")
    assert st.phase == "POST_PROCESS"


def test_reopen_keeps_the_claim_just_discussed(harness):
    engine, llm = harness
    st = engine.new_session()
    _verify(engine, llm, st, DENIED_HINT, "denial_question")
    llm.queue.append(ex(wants_to_end=True, email_decision="skip"))
    engine.handle(st, "that's all, no email")
    assert st.phase == "CLOSED"
    llm.queue.append(ex(intent="status_inquiry"))
    engine.handle(st, "oh wait, how do I check the status later?")
    assert st.phase == "PROCESS_CASE" and st.selected_claim_id == "CL-2048"
    llm.queue.append(ex(wants_to_end=True, email_decision="skip"))
    engine.handle(st, "ok thanks, no email")
    llm.queue.append(ex(case_hints={"case_type": "auto"}, intent="status_inquiry"))
    engine.handle(st, "and my auto claim?")
    assert st.phase == "PROCESS_CASE" and st.selected_claim_id == "CL-2102"


def test_role_flip_resets_progress(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(caller_role="representative", representative=REP, identity={"dob": "1985-03-15", "id_last4": "4472"}))
    engine.handle(st, "David Chen for my mother Margaret Chen, dob 1985-03-15, last four 4472")
    assert st.consent.status == "pending"
    llm.queue.append(ex(caller_role="policyholder", identity={"full_name": "Margaret Chen"}))
    engine.handle(st, "sorry, it's my own policy, I'm Margaret")
    assert st.consent.status is None and st.representative == {} and st.caller_role == "policyholder"


def test_off_topic_counter_resets_on_real_turn(harness):
    engine, llm = harness
    st = engine.new_session()
    for _ in range(2):
        llm.queue.append(ex(in_scope=False, off_topic_summary="trivia"))
        engine.handle(st, "trivia?")
    llm.queue.append(ex(identity={"full_name": "Margaret Chen"}, caller_role="policyholder"))
    engine.handle(st, "ok, Margaret Chen")
    assert st.counters.off_topic == 2            # one real turn is not enough (alternating must not evade)
    llm.queue.append(ex(identity={"dob": "1985-03-15"}))
    engine.handle(st, "DOB 1985-03-15")
    assert st.counters.off_topic == 0            # two consecutive real turns clear the strikes


def test_failed_turn_leaves_transcript_clean(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.extract = lambda system, user: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        engine.handle(st, "hello")
    except RuntimeError:
        pass
    assert [m["role"] for m in st.transcript] == ["assistant"] and st.counters.turns == 0


def test_state_view_masks_sensitive_values(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity=MARGARET_ID, caller_role="policyholder"))
    engine.handle(st, "...")
    d = st.to_dict()
    assert d["identity"]["id_last4"] == "**72"
    assert d["last_extraction"]["identity"]["id_last4"] is True
