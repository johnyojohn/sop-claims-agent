"""Session state. Plain dataclasses so the whole thing serialises to JSON for
the debug panel and for tests."""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

PHASES = ["VERIFY_ID", "RESOLVE_INTENT", "PROCESS_CASE", "POST_PROCESS"]
TERMINAL = ["CLOSED", "ESCALATED"]


@dataclass
class Verification:
    status: str = "pending"            # pending | consent_pending | verified | failed
    method: str | None = None          # self | representative
    party_id: str | None = None
    lookup_via: str | None = None
    matched: list[str] = field(default_factory=list)
    mismatched: list[str] = field(default_factory=list)
    seen_mismatches: list[str] = field(default_factory=list)
    attempts: int = 0


@dataclass
class Consent:
    scenario: str = "default"
    status: str | None = None          # None | pending | approved | timeout
    polls: int = 0
    request_id: str | None = None


@dataclass
class Memory:
    case_hints: dict = field(default_factory=dict)   # case_type, status, timeframe, claim_id, details
    intent: str | None = None
    notes: list[str] = field(default_factory=list)   # human-readable log of things remembered early


@dataclass
class EmailState:
    offered: bool = False
    decision: str | None = None        # send | skip
    address: str | None = None
    sent: bool = False
    delivery: str | None = None        # smtp | brevo | mock
    subject: str | None = None
    body: str | None = None


@dataclass
class Counters:
    off_topic: int = 0
    pushback: int = 0
    turns: int = 0


@dataclass
class SessionState:
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    phase: str = "VERIFY_ID"
    caller_role: str = "unknown"
    identity: dict = field(default_factory=dict)      # values the caller CLAIMED
    representative: dict = field(default_factory=dict)
    verification: Verification = field(default_factory=Verification)
    consent: Consent = field(default_factory=Consent)
    memory: Memory = field(default_factory=Memory)
    selected_claim_id: str | None = None
    discussed_claim_ids: list[str] = field(default_factory=list)   # claims already disclosed this session
    emotion: dict = field(default_factory=lambda: {"label": "neutral", "intensity": "low"})
    counters: Counters = field(default_factory=Counters)
    email: EmailState = field(default_factory=EmailState)
    escalation_reason: str | None = None
    transcript: list[dict] = field(default_factory=list)   # {role, content}
    events: list[str] = field(default_factory=list)        # harness decisions, for the debug panel
    tool_log: list[dict] = field(default_factory=list)
    last_directives: list[str] = field(default_factory=list)
    last_facts_keys: list[str] = field(default_factory=list)
    last_extraction: dict | None = None

    @property
    def verified(self) -> bool:
        return self.verification.status == "verified"

    def log(self, msg: str) -> None:
        self.events.append(f"[turn {self.counters.turns}] {msg}")

    def tool(self, name: str, args: dict, result) -> None:
        self.tool_log.append({"turn": self.counters.turns, "tool": name, "args": args, "result": result})

    def to_dict(self) -> dict:
        """JSON view for the UI. Sensitive identifiers are masked; raw extraction output is not exposed."""
        d = asdict(self)
        d["verified"] = self.verified
        if d["identity"].get("id_last4"):
            d["identity"]["id_last4"] = "**" + str(d["identity"]["id_last4"])[-2:]
        if d.get("last_extraction"):
            d["last_extraction"]["identity"] = {k: bool(v) for k, v in d["last_extraction"]["identity"].items()}
        return d
