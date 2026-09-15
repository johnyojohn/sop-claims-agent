"""Email delivery. Real SMTP (Gmail app password works) when configured,
otherwise a mock outbox that the UI displays. Either way the harness records
what was sent so the demo is inspectable."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from .config import Settings

log = logging.getLogger(__name__)


class Emailer:
    def __init__(self, settings: Settings):
        self.s = settings

    @property
    def configured(self) -> bool:
        return self.s.smtp_configured

    def send(self, to: str, subject: str, body: str) -> dict:
        record = {"to": to, "subject": subject, "body": body}
        if not self.configured:
            record["delivery"] = "mock"
            record["note"] = "SMTP not configured; email captured in mock outbox"
            return record
        msg = EmailMessage()
        msg["From"] = self.s.email_from or self.s.smtp_user
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        try:
            with smtplib.SMTP(self.s.smtp_host, self.s.smtp_port, timeout=20) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.s.smtp_user, self.s.smtp_password)
                smtp.send_message(msg)
            record["delivery"] = "smtp"
        except Exception as e:  # noqa: BLE001 - surface any delivery failure to the UI
            log.exception("SMTP send failed")
            record["delivery"] = "failed"
            record["error"] = str(e)
        return record
