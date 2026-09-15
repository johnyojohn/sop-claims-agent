"""Runtime settings. Everything is driven by environment variables so the same
image runs locally, in Docker, and on Render without code changes."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str | None
    anthropic_workspace_id: str | None
    model: str
    extract_effort: str
    respond_effort: str
    smtp_host: str | None
    smtp_port: int
    smtp_user: str | None
    smtp_password: str | None
    email_from: str | None
    brevo_api_key: str | None
    fixtures_dir: Path
    demo_today: str | None = None   # pin 'today' so fixture deadlines read as upcoming
    max_verification_attempts: int = 3
    off_topic_limit: int = 3
    pushback_limit: int = 2
    required_pii_matches: int = 3

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)


def get_settings() -> Settings:
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
        anthropic_workspace_id=os.getenv("ANTHROPIC_WORKSPACE_ID") or None,
        model=os.getenv("LLM_MODEL", "claude-opus-5"),
        extract_effort=os.getenv("LLM_EXTRACT_EFFORT", "low"),
        respond_effort=os.getenv("LLM_RESPOND_EFFORT", "low"),
        smtp_host=os.getenv("SMTP_HOST") or None,
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER") or None,
        smtp_password=(os.getenv("SMTP_PASSWORD") or "").replace(" ", "") or None,
        email_from=os.getenv("EMAIL_FROM") or os.getenv("SMTP_USER") or None,
        brevo_api_key=os.getenv("BREVO_API_KEY") or None,
        fixtures_dir=Path(os.getenv("FIXTURES_DIR", ROOT / "apps" / "insurance_claims" / "fixtures")),
        demo_today=os.getenv("DEMO_TODAY", "2026-03-02") or None,
    )
