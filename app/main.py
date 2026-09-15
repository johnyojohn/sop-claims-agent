"""FastAPI entry point: serves the test UI and a small JSON API.

  POST /api/session                 -> new session (body: {consent_scenario?})
  POST /api/session/{id}/message    -> {reply, state}
  GET  /api/session/{id}            -> state
  GET  /api/health                  -> config status (no secrets)

An API auth token is read from ANTHROPIC_API_KEY. A request may also carry
X-API-Key to use a different token for that session (handy for reviewers who
run the hosted demo with their own key)."""
from __future__ import annotations

import logging
import threading
from pathlib import Path

import anthropic
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import ROOT, get_settings
from .emailer import Emailer
from .harness.engine import Engine
from .harness.fixtures import Fixtures
from .harness.state import SessionState
from .llm import AnthropicLLM

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app")

settings = get_settings()
fixtures = Fixtures(settings.fixtures_dir)
emailer = Emailer(settings)

app = FastAPI(title="Insurance Claims SOP Agent")
STATIC = ROOT / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

_sessions: dict[str, tuple[SessionState, Engine]] = {}
_locks: dict[str, threading.Lock] = {}


def _engine_for(api_key: str | None) -> Engine:
    key = api_key or settings.anthropic_api_key
    if not key:
        raise HTTPException(503, "No API token configured. Set ANTHROPIC_API_KEY or send an X-API-Key header.")
    llm = AnthropicLLM(key, settings.model, settings.extract_effort, settings.respond_effort,
                       workspace_id=settings.anthropic_workspace_id)
    return Engine(llm, fixtures, settings, emailer)


class NewSession(BaseModel):
    consent_scenario: str | None = "default"


class Message(BaseModel):
    text: str


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "model": settings.model,
        "llm_token_configured": bool(settings.anthropic_api_key),
        "smtp_configured": emailer.configured,
        "consent_scenarios": list(fixtures.consent_scenarios.keys()),
        "policyholders": [{"name": p["name"], "policy_number": p["policy_number"]} for p in fixtures.policyholders],
    }


@app.post("/api/session")
def new_session(body: NewSession, x_api_key: str | None = Header(default=None)):
    engine = _engine_for(x_api_key)
    st = engine.new_session(body.consent_scenario or "default")
    _sessions[st.session_id] = (st, engine)
    _locks[st.session_id] = threading.Lock()
    return {"session_id": st.session_id, "greeting": st.transcript[0]["content"], "state": st.to_dict()}


@app.get("/api/session/{sid}")
def get_session(sid: str):
    if sid not in _sessions:
        raise HTTPException(404, "unknown session")
    return {"state": _sessions[sid][0].to_dict()}


@app.post("/api/session/{sid}/message")
def post_message(sid: str, body: Message):
    if sid not in _sessions:
        raise HTTPException(404, "unknown session")
    text = body.text.strip()
    if not text:
        raise HTTPException(400, "empty message")
    st, engine = _sessions[sid]
    with _locks[sid]:
        try:
            result = engine.handle(st, text)
        except anthropic.AuthenticationError:
            raise HTTPException(401, "The API token was rejected by Anthropic.")
        except anthropic.RateLimitError:
            raise HTTPException(429, "Rate limited by the model provider; try again in a moment.")
        except anthropic.APIStatusError as e:
            log.exception("model call failed")
            raise HTTPException(502, f"Model provider error ({e.status_code}).")
        except Exception as e:  # noqa: BLE001
            log.exception("turn failed")
            raise HTTPException(500, f"Turn failed: {type(e).__name__}: {e}")
    return {"reply": result.reply, "state": st.to_dict()}


@app.delete("/api/session/{sid}")
def delete_session(sid: str):
    _sessions.pop(sid, None)
    _locks.pop(sid, None)
    return JSONResponse({"ok": True})
