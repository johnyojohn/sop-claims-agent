# SOP-Guided Insurance Claims Support Agent

A conversational claims-support agent that follows a fixed four-phase business
workflow, **VERIFY_ID → RESOLVE_INTENT → PROCESS_CASE → POST_PROCESS**, while
still talking like a person. The LLM interprets and phrases; a deterministic
harness owns the phase order, the safety gates, the allowed actions, and what
facts the model is allowed to see on each turn.

- **Hosted demo:** https://claims-sop-agent.onrender.com (free tier: first request after idle takes about a minute to wake)
- **Stack:** Python 3.12, FastAPI, Anthropic SDK (Claude Opus 5 by default), one static HTML page. No database, no framework magic.

---

## 1. Quick start

You need an Anthropic API key. Email delivery is optional (see §5).

### Run with Docker

```bash
docker build -t sop-agent .
docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-ant-... sop-agent
```

Open http://localhost:8000.

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # put your key in ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

### Auth token

The model token is read from `ANTHROPIC_API_KEY`. The test UI also has an
"API key override" box that sends an `X-API-Key` header when a session is
created, so a reviewer can run the hosted demo on their own key (the key is
bound to that session). If your key is not scoped to a workspace, Anthropic
requires `ANTHROPIC_WORKSPACE_ID` as well. To gate the app itself, set
`APP_ACCESS_TOKEN`; every `/api` route then requires `Authorization: Bearer
<token>`. The public demo leaves this unset so reviewers can just open it.

### Tests

```bash
pytest                                   # harness tests, no API calls (stubbed model)
python scripts/run_scenarios.py          # scripted end-to-end conversations + invariants, real model
REMOTE=https://claims-sop-agent.onrender.com python scripts/run_scenarios.py   # same, against the deployment
```

The scenario runner writes transcripts to `docs/transcripts/`.

---

## 2. Try it in 60 seconds

Paste the assessment's test utterance into the chat:

> I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

Watch the right-hand panel: verification matches three items (name, DOB,
SSN-4), the "denied / healthcare / January" hint is stored during
verification, and on the same turn the harness chains through RESOLVE_INTENT
to PROCESS_CASE with claim CL-2048 loaded. Then ask follow-ups ("what do I need
to send?", "what if the clinic can't find the office note?"), say "that's
all", and accept or skip the email summary.

The sample buttons above the composer cover the other scenarios: partial
answers, an angry caller, a wrong DOB, alternate ID fields, a representative
calling on Margaret's behalf (consent scenario selectable in the header),
off-topic questions, and a request for a human.

Test data (from the fixtures): Margaret Chen, POL-9921, DOB 1985-03-15,
SSN-4 4472, phone +1 650 521 2836, margaret@email.com. Representative on
file: David Chen (son).

---

## 3. How it works

### One turn, five steps

```
user text
   │
   ▼
1. EXTRACT   one structured LLM call → typed fields (identity items, caller role,
             case hints, intent, emotion, scope, refusal, yes/no, email choice…)
   │
   ▼
2. REMEMBER  every useful field is merged into session memory regardless of
             phase. "Denied healthcare claim from January" said during
             verification is stored here and used after verification.
   │
   ▼
3. GATE      deterministic Python. Scope guard, human-transfer, then the phase
             handler. Handlers decide transitions and chain within one turn
             (VERIFY_ID → RESOLVE_INTENT → PROCESS_CASE) when they can. They
             emit *directives* (what to do this turn) and *facts* (the only
             policy/claim data the model may state).
   │
   ▼
4. RESPOND   one LLM call. System prompt = persona + phase rules + directives +
             facts JSON. Messages = recent transcript. The model phrases; it
             does not choose the phase.
   │
   ▼
5. GUARD     before verification, a substring scan rejects any reply containing
             a claim id, the opening of a claim summary or denial reason, a
             deadline, or an amount (belt and braces: that data is not in the
             model's context in the first place, which is the real guarantee).
```

Code map: [`app/harness/engine.py`](app/harness/engine.py) (the harness),
[`app/harness/verification.py`](app/harness/verification.py) (matching),
[`app/harness/fixtures.py`](app/harness/fixtures.py) (claims/policy "tools"),
[`app/harness/prompts.py`](app/harness/prompts.py) (all prompt text),
[`app/harness/schemas.py`](app/harness/schemas.py) (extractor schema),
[`app/llm.py`](app/llm.py) (Anthropic calls), [`app/emailer.py`](app/emailer.py),
[`app/main.py`](app/main.py) (API), [`static/index.html`](static/index.html) (test UI).

### Different freedom per phase

| Phase | Who decides what | What the model can see |
|---|---|---|
| VERIFY_ID (strict) | Harness: lookup, field matching, attempt counting, consent polling, escalation. Model only phrases and handles conversation (clarifications, partial answers, refusals, alternate fields). | No policy or claim data at all. The caller's own claimed values, plus which of them matched or did not. |
| RESOLVE_INTENT (flexible) | Harness pre-filters the caller's claims using remembered hints; if exactly one matches it auto-selects. Otherwise the model asks, listing claims by id/type/date/status. | Claim summaries (id, type, date, status) for the verified party only. |
| PROCESS_CASE (flexible, grounded) | Model interprets messy questions, resolves ambiguity, answers follow-ups, and can switch claims when the caller names another one. | Full selected claim record, document guidance and alternatives, follow-up rules, field meanings. Nothing else. |
| POST_PROCESS (bounded) | Harness makes the email offer, then reads the caller's choice (send / other address / skip). An address mentioned before the offer is remembered but never used until the caller says yes. The summary is generated from the transcript and claim record. | Claim record and transcript (for the summary). |

### Verification rules

- At least **three matching items** from: full name, date of birth, phone on file, email on file, last four of SSN or national ID.
- The **policy number is a lookup key only**. It locates the record but does not count as one of the three (it is printed on cards and mail, so it proves little about who is speaking). The demo utterance still verifies with exactly three.
- Matching handles name aliases, phone/email aliases, several date formats, and formatting noise. Two fixture policyholders have a national ID instead of an SSN, so the agent asks for "SSN or national ID".
- Three matches verify even if a fourth item is off (an old phone number, say).
- Every turn in which the caller asserts a value that does not match counts as an attempt, including restating the same wrong value; a turn that only adds other items is not charged. **Three failed attempts** hand the caller to a human. A failed lookup (no such name or policy) is charged the same way.
- Feedback policy, chosen deliberately: the agent says *which* item did not match so a typo can be corrected, but never what is on file, and never that an account or policy was found. The trade-off (a small existence oracle, bounded by the three-attempt cap) is the same one most call centres make; the stricter "something didn't match" variant is a one-line change to the directive in `_phase_verify_id`.
- Case hints, intent, and emotion are captured during verification but never acted on until the gate opens.

### Representative flow (from the fixtures)

If the caller is acting for someone else, the harness looks them up in
`representatives.json` (name, relationship, policyholder) **and** requires the
same three matching items about the policyholder (their name plus two of DOB,
phone, email, ID last four) before anything happens. Being named on file is
authorisation, not identity. Only then does it send a simulated consent
request to the policyholder. Each subsequent turn polls the
consent status following `consent_scenarios.json`: `default` approves on the
second check; `timeout` never approves, in which case the agent explains the
alternatives (policyholder calls directly, new request later, human review)
and does not disclose anything. The scenario is selectable in the UI header.

### Scope guard

The extractor flags out-of-scope messages. The agent declines politely and
steers back. On the third off-topic message it asks whether the caller wants a
human representative; a fourth transfers them. Greetings, thanks, and questions
about the process itself are in scope.

### Emotional support and SOP recovery (bonus)

The extractor labels emotion and intensity, and whether the caller is refusing
or questioning verification. The responder gets emotion-specific guidance
(acknowledge once, do not over-apologise, one clear next action). The harness
tracks pushback: on the first pushback it explains *why* verification protects
the caller and lists the alternatives; after two it stops persuading and
offers a human transfer. An explicit request for a human is honoured in any
phase. Escalations record a transfer ticket in the tool log.

### Memory across phases

`SessionState.memory` holds case hints (type, status, timeframe, claim id,
gist), intent, and notes. It is written on every turn and read by
RESOLVE_INTENT, which is why the demo utterance goes straight to the right
claim instead of asking again.

---

## 4. Test UI

Left: the chat. Right: a live view of the harness so a reviewer can see the
SOP working: phase stepper, identity gate (given / matched / mismatched /
attempts / consent), memory, caller signals (emotion, off-topic count,
pushback, and *which fact keys were given to the model this turn*), the
controller's directives for the turn, harness events, tool calls, and the
email that was sent.

---

## 5. Configuration

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | **Required.** Model auth token. |
| `ANTHROPIC_WORKSPACE_ID` | Only if the key is not workspace-scoped. |
| `APP_ACCESS_TOKEN` | Optional bearer token required on every `/api` route. Unset on the public demo. |
| `LLM_MODEL` | Default `claude-opus-5`. |
| `LLM_EXTRACT_EFFORT`, `LLM_RESPOND_EFFORT` | Thinking effort per call, default `low` for latency. |
| `BREVO_API_KEY`, `EMAIL_FROM` | Real email delivery over HTTPS via Brevo (needed on hosts that block outbound SMTP, such as Render's free tier). |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM` | Real email delivery over SMTP (a Gmail app password works locally). Implicit TLS on 465 first, then STARTTLS. |
| _(neither set)_ | The summary is captured in an on-screen mock outbox instead, so the demo never breaks. |
| `DEMO_TODAY` | The fixtures are dated early 2026, so the demo clock defaults to `2026-03-02` to keep the appeal deadline in the future. Set it empty to use the real date. |

The hosted demo runs on Render's free tier, which blocks outbound SMTP, so
there the summary lands in the on-screen mock outbox (the debug panel shows
the full email and the delivery status). Run it locally or in Docker with
SMTP settings and the same email is actually delivered.

### Deploying to Render

`render.yaml` is included. New → Blueprint → pick the repo, fill in the secret
env vars, deploy. Free instances sleep after 15 minutes idle and take about a
minute to wake on the first request.

---

## 6. Requirements checklist

How each requirement in the brief maps to code and evidence.

| Requirement | Where | Evidence |
|---|---|---|
| Fixed 4-phase workflow, LLM converses naturally | `engine.py` phase handlers; `prompts.py` phase rules | every transcript in `docs/transcripts/` |
| VERIFY_ID: no disclosure and no advance before 3 PII matches (self and representative paths) | `verification.py` (`match_record`, `find_candidate`), `engine._phase_verify_id`, `engine._verify_representative`; claim data absent from the model's context pre-verification; `engine._output_guard` | `tests/test_engine.py::test_no_claim_data_before_verification`, `::test_output_guard_blocks_leak`, `tests/test_engine_edges.py::test_representative_needs_policyholder_pii_before_consent`; scenario runner leak invariant (see §6) |
| Policy number is a locator, not one of the 3 | `verification.find_candidate` | `tests/test_verification.py::test_policy_number_is_lookup_only` |
| Natural conversation during verification: clarifications, partial answers, refusals, alternate fields | extractor fields `refuses_verification`, `questions_why_verify`, per-field prompting; `engine._verify_side_notes` | `partial.md`, `angry.md`, `human.md`, `wrong_dob.md` |
| RESOLVE_INTENT / PROCESS_CASE: interpret messy language, resolve ambiguity, bounded paths | extractor `intent` enum and `case_hints`; `engine._phase_resolve_intent`, `_filter_claims`, claim switching in `_phase_process_case` | `switch.md`, `partial.md`; `test_intent_resolution_lists_and_switches` |
| Answers only from grounded claim/tool data | `fixtures.py` tools; `facts` dict is the only claim data in the responder prompt; prompt rule 1 | `demo.md` (document guidance, processing time, deadline all from fixtures) |
| POST_PROCESS: offer email summary; send or skip | `engine._phase_post_process`, `_send_summary`; `emailer.py` | `demo.md` (send), `rep_ok.md` and `switch.md` (skip); `test_post_process_email_and_skip` |
| Reject out-of-scope politely; escalate to human after repeated retries | extractor `in_scope`; `engine._off_topic` with 3-strike rule | `offtopic.md`; `test_off_topic_counter_and_escalation` |
| Remember useful info from any phase and use it later | `engine._remember` writes memory every turn (replacing stale hints when the caller changes topic); `_phase_resolve_intent` reads it; reopening a closed conversation keeps the claim just discussed | `demo.md`, `angry.md`, `rep_ok.md` (hint captured during verification, claim auto-selected after); `test_demo_case_verifies_remembers_and_resolves` |
| Demo test case behaves as specified | all of the above | `demo.md`, first turn |
| Bonus: recognise emotion, de-escalate, explain why, persuade without bypass, offer alternatives, know when to stop | extractor `emotion`/`emotion_intensity`; `prompts.EMOTION_GUIDANCE`; pushback counter with human-transfer offer; `wants_human` honoured anywhere | `angry.md`, `human.md`, `rep_timeout.md`; `test_human_request_escalates_anywhere` |
| Representative and consent (implied by the fixtures) | `engine._verify_representative`; `fixtures.consent_sequence` | `rep_ok.md`, `rep_timeout.md`; consent tests |
| Hosted demo, API token, simple test UI, full workflow visible | Render deployment; `ANTHROPIC_API_KEY` / `X-API-Key`; `static/index.html` with harness debug panel | live URL above |

### Scenario suite with invariants

`scripts/run_scenarios.py` drives nine scripted conversations through the
engine (locally, or against a deployed instance with `REMOTE=<url>`), writes
each transcript to `docs/transcripts/`, and checks invariants: the expected
final phase, verification outcome and method, selected claim, email decision,
consent status, off-topic count, and, on every turn before verification, that
the reply contains no claim id, denial reason, deadline, or amount and that no
claim facts were handed to the model. It exits non-zero on any failure, so it
doubles as an end-to-end regression test against the real model.

## 7. Design notes and trade-offs

- **Why two LLM calls per turn instead of one tool-using agent?** Separating
  *understanding* (structured extraction) from *speaking* (constrained
  generation) lets plain code sit in between and make every policy decision.
  The model cannot skip verification, because the transition is a Python
  branch, and cannot leak claim data, because it never receives it early.
- **Grounding by construction.** The responder's system prompt contains a
  `GROUNDING DATA` JSON block that the harness fills per phase. The prompt
  forbids stating anything else. In PROCESS_CASE the model gets the claim,
  the document guidance for that claim's missing documents, alternative
  guidance, and the follow-up rules from `required_document_guideline.json`
  with placeholders already filled.
- **Attempt and counter policies are explicit numbers** in `Settings`
  (3 verification attempts, 3 off-topic strikes, 2 pushbacks) so they can be
  tuned without touching prompts.
- **Sessions are in memory** (capped at 500, oldest evicted). Fine for a
  demo; a real deployment would persist `SessionState` (it is a plain
  dataclass) and put real authentication in front of the API.
- **State returned to the browser is masked.** ID last-four digits are
  masked and raw extractor output is reduced to booleans, so the debug panel
  never echoes sensitive values back.
- **Failed turns roll back.** If a model call fails, the user's message is
  removed from the transcript and the UI restores it to the composer, so a
  retry never duplicates it.
- **Simulated backends.** Policyholders, claims, representatives, and consent
  are the assessment fixtures; email is real SMTP when configured.
- **Latency.** Two Opus 5 calls at low effort take a few seconds per turn.
  `LLM_MODEL=claude-sonnet-5` is a drop-in faster option.
