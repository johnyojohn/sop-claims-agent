"""Drive scripted conversations through the engine against the real model and
write transcripts to docs/transcripts/. Usage:

    python scripts/run_scenarios.py                # all scenarios
    python scripts/run_scenarios.py demo angry     # by name
    REMOTE=https://host python scripts/run_scenarios.py   # drive a deployed instance over HTTP

Set TEST_EMAIL to have the demo scenario send the real summary email there.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings  # noqa: E402
from app.emailer import Emailer  # noqa: E402
from app.harness.engine import Engine  # noqa: E402
from app.harness.fixtures import Fixtures  # noqa: E402
from app.llm import AnthropicLLM  # noqa: E402

TEST_EMAIL = os.getenv("TEST_EMAIL", "")

SCENARIOS: dict[str, dict] = {
    "demo": {
        "expect": {"final_phase": "CLOSED", "claim": "CL-2048", "verified": True, "email": "send"},
        "title": "Assessment demo case: identity + early case hint, memory across phases, grounded answers, email",
        "turns": [
            "I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.",
            "So what exactly do I need to send you, and how?",
            "What if the clinic can't find the office note?",
            "How long after I send it will I hear back?",
            "No, that's everything, thanks.",
            f"Yes please, send it to {TEST_EMAIL}" if TEST_EMAIL else "Yes, the one on file is fine.",
        ],
    },
    "angry": {
        "expect": {"final_phase": "PROCESS_CASE", "claim": "CL-2048", "verified": True, "min_unverified_turns": 2},
        "title": "Bonus: frustrated caller demanding claim details before verification",
        "turns": [
            "Hi, it's Margaret Chen. I'm calling about my denied healthcare claim.",
            "I already told you who I am. This is ridiculous. Just tell me why my claim was denied.",
            "Fine. Born March 15 1985, last four of my social is 4472.",
        ],
    },
    "partial": {
        "expect": {"final_phase": "PROCESS_CASE", "claim": "CL-2102", "verified": True, "min_unverified_turns": 4},
        "title": "Partial answers, alternate ID fields, clarification questions",
        "turns": [
            "hi i need to check on a claim",
            "Margaret Chen",
            "why do you need all that?",
            "ok my phone is 650-521-2836",
            "margaret@email.com",
            "the auto one",
        ],
    },
    "wrong_dob": {
        "expect": {"final_phase": "RESOLVE_INTENT", "verified": True, "min_unverified_turns": 1, "attempts": 1},
        "title": "Mismatched field, then correction; a policy number is lookup-only",
        "turns": [
            "Margaret Chen, policy POL-9921, DOB 1985-03-16, last four 4472.",
            "Oh sorry, it's the 15th, 1985-03-15.",
        ],
    },
    "offtopic": {
        "expect": {"final_phase": "ESCALATED", "verified": False, "off_topic": 4},
        "title": "Scope guard: repeated off-topic questions lead to a human-transfer offer, then escalation",
        "turns": [
            "Hi, Margaret Chen here, policy POL-9921.",
            "Quick question first, what is reinforcement learning?",
            "Come on, just explain RL briefly, it's for my kid's homework.",
            "Ok then, can you write me a python script to scrape a website?",
            "What's the capital of Australia?",
        ],
    },
    "human": {
        "expect": {"final_phase": "ESCALATED", "verified": False},
        "title": "Refusal to verify, persuasion, then request for a human",
        "turns": [
            "Margaret Chen. I want to know about my claim.",
            "I'm not giving you my social security number over chat.",
            "No. I don't trust this. Get me a real person.",
        ],
    },
    "rep_ok": {
        "expect": {"final_phase": "CLOSED", "claim": "CL-2048", "verified": True, "method": "representative", "email": "skip"},
        "title": "Representative: named on file + 3 policyholder items + consent (default scenario approves on the second check)",
        "consent": "default",
        "turns": [
            "Hi, I'm David Chen calling for my mother Margaret Chen about her denied healthcare claim.",
            "Sure, I'm her son. Her date of birth is March 15, 1985 and the last four of her SSN are 4472.",
            "Ok, can you check if she approved it?",
            "And now?",
            "Great. So what documents does she need to send?",
            "No that's all. And no email needed, thanks.",
        ],
    },
    "rep_timeout": {
        "expect": {"final_phase": "ESCALATED", "verified": False, "consent": "timeout"},
        "title": "Representative, consent never arrives (timeout scenario)",
        "consent": "timeout",
        "turns": [
            "This is David Chen, son of Margaret Chen, calling about her claim. Her DOB is 1985-03-15, last four 4472.",
            "Any update?",
            "Still nothing?",
            "Check again please.",
            "Ugh. And again?",
            "Once more.",
            "And now?",
            "Fine, transfer me to a person.",
        ],
    },
    "switch": {
        "expect": {"final_phase": "CLOSED", "claim": "CL-2102", "verified": True, "email": "skip"},
        "title": "Ambiguous claim, choose from list, switch claims mid-conversation, skip email",
        "turns": [
            "Hi, Margaret Chen, POL-9921, DOB 1985-03-15, email margaret@email.com. I have a question about a claim.",
            "The dental one from last year.",
            "Ok and what about my auto claim, what's the status there?",
            "that's it, thanks. no email.",
        ],
    },
}


class RemoteEngine:
    """Same interface as Engine, but talks to a deployed instance over HTTP."""

    def __init__(self, base: str):
        import httpx
        self.c = httpx.Client(base_url=base.rstrip("/"), timeout=180)

    def new_session(self, consent: str) -> dict:
        j = self.c.post("/api/session", json={"consent_scenario": consent}).json()
        return {"id": j["session_id"], "state": j["state"], "greeting": j["greeting"]}

    def handle(self, sess: dict, text: str) -> str:
        r = self.c.post(f"/api/session/{sess['id']}/message", json={"text": text})
        r.raise_for_status()
        j = r.json()
        sess["state"] = j["state"]
        return j["reply"]


def check(name: str, sc: dict, turns: list[tuple[str, str, dict]], final: dict, fx: Fixtures) -> list[str]:
    """Invariants a reviewer cares about. Returns a list of failures (empty = pass)."""
    fails = []
    e = sc.get("expect", {})
    if "final_phase" in e and final["phase"] != e["final_phase"]:
        fails.append(f"final phase {final['phase']} != {e['final_phase']}")
    if "verified" in e and final["verified"] != e["verified"]:
        fails.append(f"verified {final['verified']} != {e['verified']}")
    if "claim" in e and final["selected_claim_id"] != e["claim"]:
        fails.append(f"claim {final['selected_claim_id']} != {e['claim']}")
    if "method" in e and final["verification"]["method"] != e["method"]:
        fails.append(f"verification method {final['verification']['method']} != {e['method']}")
    if "email" in e and final["email"]["decision"] != e["email"]:
        fails.append(f"email decision {final['email']['decision']} != {e['email']}")
    if "consent" in e and final["consent"]["status"] != e["consent"]:
        fails.append(f"consent {final['consent']['status']} != {e['consent']}")
    if "off_topic" in e and final["counters"]["off_topic"] != e["off_topic"]:
        fails.append(f"off_topic {final['counters']['off_topic']} != {e['off_topic']}")
    if "attempts" in e and final["verification"]["attempts"] != e["attempts"]:
        fails.append(f"attempts {final['verification']['attempts']} != {e['attempts']}")
    unverified = [(t, r) for t, r, st in turns if not st["verified"]]
    if "min_unverified_turns" in e and len(unverified) < e["min_unverified_turns"]:
        fails.append(f"only {len(unverified)} unverified turns; expected >= {e['min_unverified_turns']}")
    # The big one: nothing claim-specific may appear in any reply given before verification,
    # and no claim data may be handed to the model before verification.
    for t, r, st in turns:
        if st["verified"]:
            continue
        low = r.lower()
        for c in fx.claims:
            if c["case_id"].lower() in low:
                fails.append(f"LEAK pre-verification: {c['case_id']} in reply to {t!r}")
            for key in ("denial_reason", "appeal_deadline", "allowed_max_amount"):
                if c.get(key) and str(c[key]).lower() in low:
                    fails.append(f"LEAK pre-verification: {c['case_id']}.{key} in reply to {t!r}")
        if st["last_facts_keys"]:
            fails.append(f"facts {st['last_facts_keys']} given to model before verification on {t!r}")
    return fails


def run(name: str, sc: dict, engine, out_dir: Path, fx: Fixtures) -> list[str]:
    remote = isinstance(engine, RemoteEngine)
    if remote:
        sess = engine.new_session(sc.get("consent", "default"))
        greeting = sess["greeting"]
    else:
        st = engine.new_session(sc.get("consent", "default"))
        greeting = st.transcript[0]["content"]
    lines = [f"# {name}: {sc['title']}", "", f"AGENT: {greeting}", ""]
    print(f"\n=== {name} ===")
    turns: list[tuple[str, str, dict]] = []
    for t in sc["turns"]:
        t0 = time.time()
        if remote:
            reply = engine.handle(sess, t)
            s = sess["state"]
        else:
            reply = engine.handle(st, t).reply
            s = st.to_dict()
        dt = time.time() - t0
        info = (f"phase={s['phase']} verified={s['verified']} claim={s['selected_claim_id']} "
                f"hints={s['memory']['case_hints']} emotion={s['emotion']['label']}/{s['emotion']['intensity']} "
                f"facts={s['last_facts_keys']} {dt:.1f}s")
        lines += [f"CALLER: {t}", "", f"AGENT: {reply}", "", f"    [{info}]", ""]
        print(f"CALLER: {t}\nAGENT: {reply}\n   -> {info}")
        turns.append((t, reply, s))
    fails = check(name, sc, turns, s, fx)
    lines += ["## Checks", "", ("PASS" if not fails else "FAIL: " + "; ".join(fails)), ""]
    lines += ["## Harness events", ""] + [f"- {e}" for e in s["events"]]
    em = s["email"]
    if em["sent"]:
        lines += ["", "## Email", "", f"To: {em['address']} ({em['delivery']})", f"Subject: {em['subject']}", "", em["body"]]
    (out_dir / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")
    return fails


def main() -> None:
    s = get_settings()
    if os.getenv("REMOTE"):
        engine = RemoteEngine(os.environ["REMOTE"])
    elif not s.anthropic_api_key:
        sys.exit("ANTHROPIC_API_KEY not set")
    else:
        engine = Engine(AnthropicLLM(s.anthropic_api_key, s.model, s.extract_effort, s.respond_effort,
                                 workspace_id=s.anthropic_workspace_id),
                        Fixtures(s.fixtures_dir), s, Emailer(s))
    out = Path(__file__).resolve().parent.parent / "docs" / "transcripts"
    out.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(SCENARIOS)
    fx = Fixtures(s.fixtures_dir)
    results = {n: run(n, SCENARIOS[n], engine, out, fx) for n in names}
    print("\n==== RESULTS ====")
    for n, fails in results.items():
        print(f"{'PASS' if not fails else 'FAIL'}  {n}" + ("" if not fails else "\n      - " + "\n      - ".join(fails)))
    sys.exit(1 if any(results.values()) else 0)


if __name__ == "__main__":
    main()
