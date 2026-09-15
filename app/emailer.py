"""Email delivery with three transports, tried in this order:

  1. Brevo HTTPS API   - set BREVO_API_KEY (+ EMAIL_FROM). Works on hosts that
                         block outbound SMTP (Render's free tier does).
  2. SMTP              - set SMTP_HOST/USER/PASSWORD. Implicit TLS on 465 first,
                         then STARTTLS on the configured port.
  3. Mock outbox       - nothing configured: the summary is captured and shown
                         in the UI so the demo never breaks.

The harness records the outcome in the tool log either way."""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

import httpx

from .config import Settings

log = logging.getLogger(__name__)


class Emailer:
    def __init__(self, settings: Settings):
        self.s = settings

    @property
    def configured(self) -> bool:
        return bool(self.s.brevo_api_key) or self.s.smtp_configured

    @property
    def transport(self) -> str:
        if self.s.brevo_api_key:
            return "brevo"
        if self.s.smtp_configured:
            return "smtp"
        return "mock"

    def send(self, to: str, subject: str, body: str) -> dict:
        record = {"to": to, "subject": subject, "body": body}
        errors: list[str] = []
        if self.s.brevo_api_key:
            try:
                self._send_brevo(to, subject, body)
                record["delivery"] = "brevo"
                return record
            except Exception as e:  # noqa: BLE001
                log.warning("Brevo send failed: %s", e)
                errors.append(f"brevo: {type(e).__name__}: {e}")
        if self.s.smtp_configured:
            err = self._send_smtp(to, subject, body)
            if err is None:
                record["delivery"] = "smtp"
                return record
            errors.append(err)
        if not errors:
            record["delivery"] = "mock"
            record["note"] = "No email transport configured; captured in mock outbox"
            return record
        record["delivery"] = "failed"
        record["error"] = "; ".join(errors)
        return record

    # ---- transports ------------------------------------------------------
    def _send_brevo(self, to: str, subject: str, body: str) -> None:
        sender = self.s.email_from or self.s.smtp_user
        r = httpx.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": self.s.brevo_api_key, "content-type": "application/json"},
            json={"sender": {"name": "Northwind Insurance Claims", "email": sender},
                  "to": [{"email": to}], "subject": subject, "textContent": body},
            timeout=20,
        )
        if r.status_code >= 300:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")

    def _send_smtp(self, to: str, subject: str, body: str) -> str | None:
        msg = EmailMessage()
        msg["From"] = self.s.email_from or self.s.smtp_user
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        ports = [465] + ([self.s.smtp_port] if self.s.smtp_port != 465 else [])
        errors = []
        for port in ports:
            mode = "ssl" if port == 465 else "starttls"
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
                return None
            except Exception as e:  # noqa: BLE001
                log.warning("SMTP %s:%s (%s) failed: %s", self.s.smtp_host, port, mode, e)
                errors.append(f"smtp {port}/{mode}: {type(e).__name__}: {e}")
        return "; ".join(errors)
