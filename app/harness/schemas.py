"""Structured-output schema for the per-turn extractor. Every field is
required-but-nullable so the schema works with strict JSON output."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Identity(BaseModel):
    full_name: str | None
    dob: str | None          # normalised to YYYY-MM-DD when possible
    phone: str | None
    email: str | None
    id_last4: str | None     # last 4 of SSN or national ID
    policy_number: str | None


class Representative(BaseModel):
    name: str | None
    relationship: str | None
    policyholder_name: str | None


class CaseHints(BaseModel):
    case_type: Literal["healthcare", "dental", "auto", "unknown"]
    status: Literal["denied", "open", "closed", "unknown"]
    timeframe: str | None   # month name and/or year as the caller said it, e.g. "January", "Jan 2026", "last year"
    claim_id: str | None
    details: str | None     # free-text gist of what the caller wants


Intent = Literal[
    "denial_question", "status_inquiry", "document_submission", "next_steps",
    "appeal", "general_claim_question", "none",
]


class Extraction(BaseModel):
    identity: Identity
    caller_role: Literal["policyholder", "representative", "unknown"]
    representative: Representative
    case_hints: CaseHints
    intent: Intent
    in_scope: bool
    is_small_talk: bool
    off_topic_summary: str | None
    emotion: Literal["neutral", "frustrated", "angry", "anxious", "confused", "sad"]
    emotion_intensity: Literal["low", "medium", "high"]
    refuses_verification: bool
    questions_why_verify: bool
    wants_human: bool
    affirmation: Literal["yes", "no", "unclear"]
    email_decision: Literal["send", "skip", "none"]
    provided_email: str | None
    selected_claim_id: str | None
    wants_to_end: bool


class EmailSummary(BaseModel):
    subject: str
    body: str
