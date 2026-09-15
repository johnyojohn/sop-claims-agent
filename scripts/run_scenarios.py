"""Drive scripted conversations through the engine against the real model and
write transcripts to docs/transcripts/. Usage:

    python scripts/run_scenarios.py                # all scenarios
    python scripts/run_scenarios.py demo angry     # by name

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
        "title": "Bonus: frustrated caller demanding claim details before verification",
        "turns": [
            "Hi, it's Margaret Chen. I'm calling about my denied healthcare claim.",
            "I already told you who I am. This is ridiculous. Just tell me why my claim was denied.",
            "Fine. Born March 15 1985, last four of my social is 4472.",
        ],
    },
    "partial": {
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
        "title": "Mismatched field, then correction; a policy number is lookup-only",
        "turns": [
            "Margaret Chen, policy POL-9921, DOB 1985-03-16, last four 4472.",
            "Oh sorry, it's the 15th, 1985-03-15.",
        ],
    },
    "offtopic": {
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
        "title": "Refusal to verify, persuasion, then request for a human",
        "turns": [
            "Margaret Chen. I want to know about my claim.",
            "I'm not giving you my social security number over chat.",
            "No. I don't trust this. Get me a real person.",
        ],
    },
    "rep_ok": {
        "title": "Representative with consent (default scenario approves on the second check)",
        "consent": "default",
        "turns": [
            "Hi, I'm David Chen calling for my mother Margaret Chen about her denied healthcare claim.",
            "Sure, I'm her son.",
            "Ok, can you check if she approved it?",
            "Great. So what documents does she need to send?",
            "No that's all. And no email needed, thanks.",
        ],
    },
    "rep_timeout": {
        "title": "Representative, consent never arrives (timeout scenario)",
        "consent": "timeout",
        "turns": [
            "This is David Chen, son of Margaret Chen, calling about her claim.",
            "Any update?",
            "Still nothing?",
            "Check again please.",
            "Ugh. And again?",
            "Once more.",
            "Fine, transfer me to a person.",
        ],
    },
    "switch": {
        "title": "Ambiguous claim, choose from list, switch claims mid-conversation, skip email",
        "turns": [
            "Hi, Margaret Chen, POL-9921, DOB 1985-03-15, email margaret@email.com. I have a question about a claim.",
            "The dental one from last year.",
            "Ok and what about my auto claim, what's the status there?",
            "that's it, thanks. no email.",
        ],
    },
}


def run(name: str, sc: dict, engine: Engine, out_dir: Path) -> None:
    st = engine.new_session(sc.get("consent", "default"))
    lines = [f"# {name}: {sc['title']}", "", f"AGENT: {st.transcript[0]['content']}", ""]
    print(f"\n=== {name} ===")
    for t in sc["turns"]:
        t0 = time.time()
        res = engine.handle(st, t)
        dt = time.time() - t0
        lines += [f"CALLER: {t}", "", f"AGENT: {res.reply}", "",
                  f"    [phase={st.phase} verified={st.verified} claim={st.selected_claim_id} "
                  f"hints={st.memory.case_hints} emotion={st.emotion['label']}/{st.emotion['intensity']} "
                  f"facts={st.last_facts_keys} {dt:.1f}s]", ""]
        print(f"CALLER: {t}\nAGENT: {res.reply}\n   -> {st.phase} ({dt:.1f}s) facts={st.last_facts_keys}")
    lines += ["## Harness events", ""] + [f"- {e}" for e in st.events]
    if st.email.sent:
        lines += ["", "## Email", "", f"To: {st.email.address} ({st.email.delivery})", f"Subject: {st.email.subject}", "", st.email.body]
    (out_dir / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    s = get_settings()
    if not s.anthropic_api_key:
        sys.exit("ANTHROPIC_API_KEY not set")
    engine = Engine(AnthropicLLM(s.anthropic_api_key, s.model, s.extract_effort, s.respond_effort,
                                 workspace_id=s.anthropic_workspace_id),
                    Fixtures(s.fixtures_dir), s, Emailer(s))
    out = Path(__file__).resolve().parent.parent / "docs" / "transcripts"
    out.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(SCENARIOS)
    for n in names:
        run(n, SCENARIOS[n], engine, out)


if __name__ == "__main__":
    main()
