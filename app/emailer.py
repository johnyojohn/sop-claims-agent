"""Email delivery. Real SMTP (Gmail app password works) when configured,
otherwise a mock outbox that the UI displays. Either way the harness records
what was sent so the demo is inspectable.

Delivery tries implicit TLS on port 465 first (STARTTLS on 587 is blocked by
several hosting providers), then falls back to STARTTLS on the configured
port."""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import Settings

log = logging.getLogger(__name__)


class Emailer:
    def __init__(self, settings: Settings):
        self.s = settings

    @property
    def configured(self) -> bool:
        return self.s.smtp_configured

    def _attempts(self):
        ports = [465] + ([self.s.smtp_port] if self.s.smtp_port != 465 else [])
        for port in ports:
            yield port, ("ssl" if port == 465 else "starttls")

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
        errors = []
        for port, mode in self._attempts():
            try:
                if mode == "ssl":
                    smtp = smtplib.SMTP_SSL(self.s.smtp_host, port, timeout=15, context=ssl.create_default_context())
                else:
                    smtp = smtplib.SMTP(self.s.smtp_host, port, timeout=15)
                    smtp.ehlo()
                    smtp.starttls()
                with smtp:
                    smtp.login(self.s.smtp_user, self.s.smtp_password)
                    smtp.send_message(msg)
                record["delivery"] = "smtp"
                record["via"] = f"{self.s.smtp_host}:{port} ({mode})"
                return record
            except Exception as e:  # noqa: BLE001 - try the next transport, then surface the failure
                log.warning("SMTP %s:%s (%s) failed: %s", self.s.smtp_host, port, mode, e)
                errors.append(f"{port}/{mode}: {type(e).__name__}: {e}")
        record["delivery"] = "failed"
        record["error"] = "; ".join(errors)
        return record
