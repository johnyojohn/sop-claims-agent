"""Thin adapter over the Anthropic SDK. Three calls per conversation turn at
most: extract (structured JSON), respond (free text), and, once, summarise
(structured JSON for the email). The harness never lets the model decide
phase transitions; it only reads the extractor's fields."""
from __future__ import annotations

import logging
from typing import Protocol

import anthropic

from .harness.schemas import EmailSummary, Extraction

log = logging.getLogger(__name__)


class LLMProtocol(Protocol):
    def extract(self, system: str, user: str) -> Extraction: ...
    def respond(self, system: str, messages: list[dict]) -> str: ...
    def summarize(self, system: str, user: str) -> EmailSummary: ...


class AnthropicLLM:
    def __init__(self, api_key: str, model: str, extract_effort: str = "low", respond_effort: str = "low",
                 workspace_id: str | None = None):
        headers = {"anthropic-workspace-id": workspace_id} if workspace_id else None
        self.client = anthropic.Anthropic(api_key=api_key, default_headers=headers)
        self.model = model
        self.extract_effort = extract_effort
        self.respond_effort = respond_effort

    def extract(self, system: str, user: str) -> Extraction:
        resp = self.client.messages.parse(
            model=self.model,
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=Extraction,
            output_config={"effort": self.extract_effort},
        )
        if resp.parsed_output is None:
            raise RuntimeError(f"extractor returned no parsed output (stop_reason={resp.stop_reason})")
        return resp.parsed_output

    def respond(self, system: str, messages: list[dict]) -> str:
        kwargs = dict(
            model=self.model,
            max_tokens=4000,
            system=system,
            messages=messages,
            output_config={"effort": self.respond_effort},
        )
        try:
            resp = self.client.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs
            )
        except anthropic.BadRequestError as e:
            # Fallback parameter not accepted on this account / model: retry plain.
            log.warning("beta fallback request rejected (%s); retrying without", e.message)
            resp = self.client.messages.create(**kwargs)
        if resp.stop_reason == "refusal":
            return "I'm sorry, I can't help with that part. Let's get back to your claim."
        return "".join(b.text for b in resp.content if b.type == "text").strip()

    def summarize(self, system: str, user: str) -> EmailSummary:
        resp = self.client.messages.parse(
            model=self.model,
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_format=EmailSummary,
            output_config={"effort": "medium"},
        )
        if resp.parsed_output is None:
            raise RuntimeError("summariser returned no parsed output")
        return resp.parsed_output
