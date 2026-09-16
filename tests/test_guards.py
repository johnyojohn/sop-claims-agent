"""Guards added after review: claim-id hygiene, post-verification grounding,
and the consecutive-strike rule for off-topic messages."""
from conftest import ex

MARGARET_ID = {"full_name": "Margaret Chen", "dob": "1985-03-15", "id_last4": "4472", "policy_number": "POL-9921"}


def _verify(engine, llm, st, **kw):
    llm.queue.append(ex(identity=MARGARET_ID, caller_role="policyholder", **kw))
    engine.handle(st, "verify me")


def test_policy_number_is_never_treated_as_a_claim_id(harness):
    engine, llm = harness
    st = engine.new_session()
    _verify(engine, llm, st, case_hints={"claim_id": "POL-9921", "case_type": "auto"}, intent="status_inquiry")
    assert st.phase == "PROCESS_CASE" and st.selected_claim_id == "CL-2102"
    assert "claim_id" not in st.memory.case_hints or st.memory.case_hints["claim_id"] != "POL-9921"
    llm.queue.append(ex(case_hints={"claim_id": "POL-9921"}, intent="status_inquiry"))
    engine.handle(st, "my policy is POL-9921")
    assert not any("not on this account" in d for d in st.last_directives)


def test_claim_id_shapes(harness):
    engine, _ = harness
    st = engine.new_session()
    assert engine._clean_claim_id(st, "cl-2048") == "CL-2048"
    assert engine._clean_claim_id(st, "CL 2048") == "CL-2048"
    assert engine._clean_claim_id(st, "CL2048") == "CL-2048"
    assert engine._clean_claim_id(st, "healthcare") is None
    assert engine._clean_claim_id(st, None) is None


def test_grounding_guard_regenerates_unsupported_figures(harness):
    engine, llm = harness
    st = engine.new_session()
    replies = iter(["Your deductible is $250.00 and the check clears on April 3, 2026.",
                    "I don't have the deductible or a payment date on file; I can have a representative confirm."])
    llm.respond = lambda system, messages: next(replies)
    _verify(engine, llm, st, case_hints={"case_type": "auto"}, intent="status_inquiry")
    assert "250.00" not in st.transcript[-1]["content"] and "April 3" not in st.transcript[-1]["content"]
    assert any("GROUNDING GUARD" in e for e in st.events)


def test_grounding_guard_allows_facts_and_redacts_persistent_inventions(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.respond = lambda system, messages: "Expected reimbursement is $3,200.00 and the deductible is $99.99."
    _verify(engine, llm, st, case_hints={"case_type": "auto"}, intent="status_inquiry")
    out = st.transcript[-1]["content"]
    assert "$3,200.00" in out and "$99.99" not in out and "[not on file]" in out


def test_grounding_guard_inactive_before_verification(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.respond = lambda system, messages: "Sure, could you give me your date of birth?"
    llm.queue.append(ex(identity={"full_name": "Margaret Chen"}, caller_role="policyholder"))
    engine.handle(st, "hi")
    assert not any("GROUNDING GUARD" in e for e in st.events)


def test_alternating_off_topic_still_escalates(harness):
    engine, llm = harness
    st = engine.new_session()
    for i in range(4):
        llm.queue.append(ex(in_scope=False, off_topic_summary="trivia"))
        engine.handle(st, "trivia?")
        if st.phase == "ESCALATED":
            break
        llm.queue.append(ex(identity={"full_name": "Margaret Chen"}, caller_role="policyholder"))
        engine.handle(st, "ok, Margaret Chen")
    assert st.phase == "ESCALATED"


def test_two_real_turns_clear_strikes(harness):
    engine, llm = harness
    st = engine.new_session()
    llm.queue.append(ex(in_scope=False, off_topic_summary="trivia"))
    engine.handle(st, "trivia?")
    for _ in range(2):
        llm.queue.append(ex(identity={"full_name": "Margaret Chen"}, caller_role="policyholder"))
        engine.handle(st, "Margaret Chen")
    assert st.counters.off_topic == 0
