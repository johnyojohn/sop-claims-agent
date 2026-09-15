from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.emailer import Emailer  # noqa: E402
from app.harness.engine import Engine  # noqa: E402
from app.harness.fixtures import Fixtures  # noqa: E402
from app.harness.schemas import CaseHints, EmailSummary, Extraction, Identity, Representative  # noqa: E402


def ex(**over) -> Extraction:
    """Build an Extraction with neutral defaults; override what the turn 'says'."""
    base = dict(
        identity=Identity(full_name=None, dob=None, phone=None, email=None, id_last4=None, policy_number=None),
        caller_role="unknown",
        representative=Representative(name=None, relationship=None, policyholder_name=None),
        case_hints=CaseHints(case_type="unknown", status="unknown", timeframe=None, claim_id=None, details=None),
        intent="none", in_scope=True, is_small_talk=False, off_topic_summary=None,
        emotion="neutral", emotion_intensity="low", refuses_verification=False, questions_why_verify=False,
        wants_human=False, affirmation="unclear", email_decision="none", provided_email=None,
        selected_claim_id=None, wants_to_end=False,
    )
    for k, v in over.items():
        if k == "identity":
            base["identity"] = Identity(**{**base["identity"].model_dump(), **v})
        elif k == "case_hints":
            base["case_hints"] = CaseHints(**{**base["case_hints"].model_dump(), **v})
        elif k == "representative":
            base["representative"] = Representative(**{**base["representative"].model_dump(), **v})
        else:
            base[k] = v
    return Extraction(**base)


class StubLLM:
    """Returns queued extractions; records every system prompt the responder saw."""

    def __init__(self):
        self.queue: list[Extraction] = []
        self.systems: list[str] = []

    def extract(self, system, user):
        return self.queue.pop(0)

    def respond(self, system, messages):
        self.systems.append(system)
        return "(stub reply)"

    def summarize(self, system, user):
        return EmailSummary(subject="Summary of your call", body="stub body")


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    return get_settings()


@pytest.fixture
def fx(settings):
    return Fixtures(settings.fixtures_dir)


@pytest.fixture
def harness(settings, fx):
    llm = StubLLM()
    engine = Engine(llm, fx, settings, Emailer(settings))
    return engine, llm
