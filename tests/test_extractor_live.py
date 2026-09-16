"""Live tests for the extraction prompt, the one layer the stubbed suite cannot
cover. Skipped unless ANTHROPIC_API_KEY is set (each case is one short model
call). Run with:  LIVE_LLM_TESTS=1 pytest tests/test_extractor_live.py -q
"""
from __future__ import annotations

import os

import pytest

from app.config import get_settings
from app.harness import prompts
from app.llm import AnthropicLLM

pytestmark = pytest.mark.skipif(not os.getenv("LIVE_LLM_TESTS"), reason="set LIVE_LLM_TESTS=1 (and an API key) to run")


@pytest.fixture(scope="module")
def llm():
    s = get_settings()
    return AnthropicLLM(s.anthropic_api_key, s.model, s.extract_effort, s.respond_effort,
                        workspace_id=s.anthropic_workspace_id)


def _extract(llm, text, last_agent="How can I help you today?", phase="VERIFY_ID"):
    user = (f"Workflow phase: {phase}\nCaller role so far: unknown\n"
            f"Identity fields already provided earlier (names only): none\nEmail summary offered: False\n\n"
            f"Recent conversation:\nASSISTANT: {last_agent}\n\nAgent's last message: {last_agent}\n\n"
            f"CALLER'S CURRENT MESSAGE:\n{text}")
    return llm.extract(prompts.EXTRACTOR_SYSTEM, user)


def test_demo_utterance(llm):
    e = _extract(llm, "I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my "
                      "denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.")
    assert e.identity.full_name and "chen" in e.identity.full_name.lower()
    assert e.identity.dob == "1985-03-15" and e.identity.id_last4 == "4472"
    assert e.identity.policy_number and "9921" in e.identity.policy_number
    assert e.case_hints.case_type == "healthcare" and e.case_hints.status == "denied"
    assert e.case_hints.claim_id is None or "9921" not in e.case_hints.claim_id
    assert e.caller_role == "policyholder" and e.in_scope


def test_partial_answer_uses_agent_question(llm):
    e = _extract(llm, "March 15, 1985", last_agent="Could you give me your date of birth?")
    assert e.identity.dob == "1985-03-15"


def test_representative_and_relationship(llm):
    e = _extract(llm, "Hi, I'm David Chen calling for my mother Margaret Chen about her claim.")
    assert e.caller_role == "representative"
    assert e.representative.name and "david" in e.representative.name.lower()
    assert e.representative.policyholder_name and "margaret" in e.representative.policyholder_name.lower()
    assert e.identity.full_name is None or "david" not in e.identity.full_name.lower()


def test_off_topic_and_human_request(llm):
    e = _extract(llm, "Quick question first, what is reinforcement learning?")
    assert not e.in_scope
    e2 = _extract(llm, "Will a human review the pathology report once I send it?", phase="PROCESS_CASE")
    assert not e2.wants_human
    e3 = _extract(llm, "Forget this, get me a real person now.")
    assert e3.wants_human


def test_angry_refusal(llm):
    e = _extract(llm, "I already told you who I am. This is ridiculous. Just tell me why my claim was denied.",
                 last_agent="I have your name; I need two more items: date of birth, phone, email, or SSN last four.")
    assert e.emotion in ("frustrated", "angry") and e.refuses_verification
    assert e.intent == "denial_question"


def test_email_decisions(llm):
    last = "Would you like me to email a summary to the address on file, another address, or skip it?"
    assert _extract(llm, "yes, send it to me@example.com", last, "POST_PROCESS").provided_email == "me@example.com"
    assert _extract(llm, "no thanks, skip it", last, "POST_PROCESS").email_decision == "skip"
