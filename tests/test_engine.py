"""Harness behaviour with a stubbed model: phase order, gates, memory, scope,
escalation, representative consent, and the no-leak guarantee."""
from conftest import ex

MARGARET_ID = {"full_name": "Margaret Chen", "dob": "1985-03-15", "id_last4": "4472", "policy_number": "POL-9921"}
DENIED_HINT = {"case_type": "healthcare", "status": "denied", "timeframe": "January", "details": "denied healthcare claim from January"}


def test_demo_case_verifies_remembers_and_resolves(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity=MARGARET_ID, caller_role="policyholder", case_hints=DENIED_HINT, intent="denial_question"))
    engine.handle(st, "I'm Margaret Chen ... denied healthcare claim from January ...")
    assert st.verified and st.verification.method == "self"
    assert st.memory.case_hints["status"] == "denied"
    # hint was used: phase chained VERIFY_ID -> RESOLVE_INTENT -> PROCESS_CASE in one turn
    assert st.phase == "PROCESS_CASE" and st.selected_claim_id == "CL-2048"
    assert "claim" in st.last_facts_keys and "document_guidance" in st.last_facts_keys
    assert "the review file did not include the pathology report" in llm.systems[-1]


def test_no_claim_data_before_verification(harness, fx):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity={"full_name": "Margaret Chen"}, caller_role="policyholder",
                        case_hints=DENIED_HINT, intent="denial_question", emotion="frustrated", emotion_intensity="high",
                        refuses_verification=True))
    engine.handle(st, "I already told you who I am. Just tell me why my claim was denied.")
    assert st.phase == "VERIFY_ID" and not st.verified
    assert st.last_facts_keys == []
    system = llm.systems[-1]
    for c in fx.claims:
        assert c["case_id"] not in system
        assert not c.get("denial_reason") or c["denial_reason"] not in system
    assert "pushing back" in system and st.memory.case_hints["status"] == "denied"


def test_output_guard_blocks_leak(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity={"full_name": "Margaret Chen"}, caller_role="policyholder"))
    llm.respond = lambda system, messages: "Your claim CL-2048 was denied because ..."
    res = engine.handle(st, "hi")
    assert "CL-2048" not in res.reply
    assert any("OUTPUT GUARD" in e for e in st.events)


def test_mismatch_attempts_then_escalation(harness):
    engine, llm = harness
    st = engine.new_session()
    bad = {**MARGARET_ID, "dob": "1985-03-16"}
    llm.queue.append(ex(identity=bad, caller_role="policyholder"))
    engine.handle(st, "wrong dob")
    assert st.verification.attempts == 1 and st.verification.mismatched == ["dob"]
    llm.queue.append(ex(identity={"dob": "1985-03-15"}))
    engine.handle(st, "sorry, the 15th")
    assert st.verified


def test_three_failed_lookups_escalate(harness):
    engine, llm = harness
    st = engine.new_session()
    for i in range(3):
        llm.queue.append(ex(identity={"full_name": f"Nobody {i}"}, caller_role="policyholder"))
        engine.handle(st, "name")
    assert st.phase == "ESCALATED" and st.tool_log[-1]["tool"] == "transfer_to_human"


def test_off_topic_counter_and_escalation(harness):
    engine, llm = harness
    st = engine.new_session()
    for i in range(3):
        llm.queue.append(ex(in_scope=False, off_topic_summary="reinforcement learning"))
        engine.handle(st, "what is RL?")
    assert st.counters.off_topic == 3 and st.phase == "VERIFY_ID"
    assert "transferred to a human representative" in llm.systems[-1]
    llm.queue.append(ex(in_scope=False, off_topic_summary="capital cities"))
    engine.handle(st, "capital of australia?")
    assert st.phase == "ESCALATED"


def test_human_request_escalates_anywhere(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(wants_human=True))
    engine.handle(st, "get me a person")
    assert st.phase == "ESCALATED" and "verification first" in llm.systems[-1]


def test_representative_consent_flow(harness):
    engine, llm = harness
    st = engine.new_session("default")
    llm.queue.append(ex(caller_role="representative",
                        representative={"name": "David Chen", "relationship": "son", "policyholder_name": "Margaret Chen"},
                        case_hints={"case_type": "healthcare", "status": "denied"}))
    engine.handle(st, "I'm David Chen calling for my mom Margaret Chen")
    assert st.verification.status == "consent_pending" and st.consent.status == "pending"
    llm.queue.append(ex(affirmation="yes"))
    engine.handle(st, "can you check?")           # poll 1 -> pending
    assert st.consent.status == "pending"
    llm.queue.append(ex(affirmation="yes"))
    engine.handle(st, "check again")              # poll 2 -> approved, chains to PROCESS_CASE
    assert st.verified and st.verification.method == "representative"
    assert st.phase == "PROCESS_CASE" and st.selected_claim_id == "CL-2048"


def test_representative_consent_timeout(harness):
    engine, llm = harness
    st = engine.new_session("timeout")
    llm.queue.append(ex(caller_role="representative",
                        representative={"name": "David Chen", "relationship": "son", "policyholder_name": "Margaret Chen"}))
    engine.handle(st, "David Chen for Margaret Chen")
    for _ in range(6):
        llm.queue.append(ex())
        engine.handle(st, "again?")
    assert st.consent.status == "timeout" and not st.verified and st.last_facts_keys == []


def test_intent_resolution_lists_and_switches(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity=MARGARET_ID, caller_role="policyholder"))
    engine.handle(st, "verify me")
    assert st.phase == "RESOLVE_INTENT" and "claims_on_file" in st.last_facts_keys
    llm.queue.append(ex(case_hints={"case_type": "dental", "timeframe": "last year"}, intent="status_inquiry"))
    engine.handle(st, "the dental one")
    assert st.phase == "PROCESS_CASE" and st.selected_claim_id == "CL-1899"
    llm.queue.append(ex(case_hints={"case_type": "auto"}, intent="status_inquiry"))
    engine.handle(st, "and my auto claim?")
    assert st.selected_claim_id == "CL-2102"


def test_post_process_email_and_skip(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(identity=MARGARET_ID, caller_role="policyholder", case_hints=DENIED_HINT, intent="denial_question"))
    engine.handle(st, "...")
    llm.queue.append(ex(wants_to_end=True))
    engine.handle(st, "that's all")
    assert st.phase == "POST_PROCESS" and st.email.offered
    llm.queue.append(ex(email_decision="send", provided_email="me@example.com"))
    engine.handle(st, "send to me@example.com")
    assert st.phase == "CLOSED" and st.email.sent and st.email.delivery == "mock" and st.email.address == "me@example.com"

    st2 = engine.new_session()
    llm.queue.append(ex(identity=MARGARET_ID, caller_role="policyholder", case_hints=DENIED_HINT))
    engine.handle(st2, "...")
    llm.queue.append(ex(wants_to_end=True))
    engine.handle(st2, "done")
    llm.queue.append(ex(email_decision="skip"))
    engine.handle(st2, "no thanks")
    assert st2.phase == "CLOSED" and not st2.email.sent and st2.email.decision == "skip"
