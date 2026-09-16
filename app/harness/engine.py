"""The SOP harness.

Each user turn runs the same pipeline:

  1. extract   - one structured LLM call turns the message into typed fields
  2. remember  - every useful field is merged into session memory, regardless
                 of phase (this is how "denied healthcare claim from January"
                 said during verification survives to RESOLVE_INTENT)
  3. gate      - deterministic code decides: scope, escalation, phase logic,
                 phase transitions, and exactly which facts the model may see
  4. respond   - one LLM call phrases the reply, constrained by the phase rules,
                 this turn's directives, and the allowed facts
  5. guard     - a final regex check that no claim data leaked pre-verification

The model never chooses the phase. It cannot leak claim details before
verification because they are not in its context until the gate opens.
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import date

from ..config import Settings
from ..emailer import Emailer
from ..llm import LLMProtocol
from . import prompts
from .fixtures import Fixtures
from .schemas import Extraction
from .state import SessionState
from .verification import FIELD_LABELS, PII_FIELDS, find_candidate, mask_email, match_record

GREETING = ("Hi, thanks for calling Northwind Insurance claims support, this is Ava. "
            "How can I help you today?")

MONTHS = {m.lower(): i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], start=1)}


class TurnResult:
    def __init__(self, reply: str, state: SessionState):
        self.reply = reply
        self.state = state


class Engine:
    def __init__(self, llm: LLMProtocol, fixtures: Fixtures, settings: Settings, emailer: Emailer):
        self.llm = llm
        self.fx = fixtures
        self.s = settings
        self.emailer = emailer

    def _today(self) -> str:
        return self.s.demo_today or date.today().isoformat()

    # ------------------------------------------------------------------ API
    def new_session(self, consent_scenario: str = "default") -> SessionState:
        st = SessionState()
        st.consent.scenario = consent_scenario if consent_scenario in self.fx.consent_scenarios else "default"
        st.transcript.append({"role": "assistant", "content": GREETING})
        return st

    def handle(self, st: SessionState, text: str) -> TurnResult:
        st.counters.turns += 1
        st.transcript.append({"role": "user", "content": text})
        try:
            ex = self.llm.extract(prompts.EXTRACTOR_SYSTEM, self._extract_input(st, text))
            st.last_extraction = ex.model_dump()
            self._remember(st, ex)

            directives: list[str] = []
            facts: dict = {}
            self._run_gates(st, ex, directives, facts)

            st.last_directives = directives
            st.last_facts_keys = list(facts.keys())
            system = self._responder_system(st, ex, directives, facts)
            reply = self.llm.respond(system, self._api_messages(st))
        except Exception:
            # Leave the transcript as it was so a retry does not duplicate the message.
            st.transcript.pop()
            st.counters.turns -= 1
            raise
        reply = self._output_guard(st, reply)
        reply = self._grounding_guard(st, reply, facts, system)
        st.transcript.append({"role": "assistant", "content": reply})
        return TurnResult(reply, st)

    # ------------------------------------------------------------ step 1: extract
    def _extract_input(self, st: SessionState, text: str) -> str:
        last_agent = next((m["content"] for m in reversed(st.transcript[:-1]) if m["role"] == "assistant"), "")
        recent = st.transcript[-7:-1]
        convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in recent)
        known = [f for f in PII_FIELDS + ["policy_number"] if st.identity.get(f)]
        return (
            f"Workflow phase: {st.phase}\n"
            f"Caller role so far: {st.caller_role}\n"
            f"Identity fields already provided earlier (names only): {known or 'none'}\n"
            f"Email summary offered: {st.email.offered}\n\n"
            f"Recent conversation:\n{convo}\n\n"
            f"Agent's last message: {last_agent}\n\n"
            f"CALLER'S CURRENT MESSAGE:\n{text}"
        )

    # ----------------------------------------------------------- step 2: remember
    def _remember(self, st: SessionState, ex: Extraction) -> None:
        for k, v in ex.identity.model_dump().items():
            if v:
                if st.identity.get(k) and st.identity[k] != v:
                    st.log(f"identity.{k} updated by caller")
                st.identity[k] = v.strip()
        if ex.caller_role != "unknown" and st.caller_role != ex.caller_role and st.verification.status != "verified":
            if st.caller_role != "unknown":
                # A mid-verification role change invalidates everything gathered for the old path.
                st.representative = {}
                st.consent = type(st.consent)(scenario=st.consent.scenario)
                st.verification = type(st.verification)()
                st.log(f"caller_role changed {st.caller_role} -> {ex.caller_role}; verification progress reset")
            else:
                st.log(f"caller_role = {ex.caller_role}")
            st.caller_role = ex.caller_role
        for k, v in ex.representative.model_dump().items():
            if v:
                st.representative[k] = v.strip()
        hints = ex.case_hints
        new_hints = {}
        if hints.case_type != "unknown":
            new_hints["case_type"] = hints.case_type
        if hints.status != "unknown":
            new_hints["status"] = hints.status
        if hints.timeframe:
            new_hints["timeframe"] = hints.timeframe
        cid = self._clean_claim_id(st, hints.claim_id)
        if cid:
            new_hints["claim_id"] = cid
        if hints.details:
            new_hints["details"] = hints.details
        if new_hints:
            old = st.memory.case_hints
            topic_changed = any(k in new_hints and old.get(k) and old[k] != new_hints[k] for k in ("case_type", "claim_id"))
            if topic_changed:
                # The caller is now talking about a different claim: stale status/timeframe must not survive.
                st.log(f"case hints replaced (topic changed): {old} -> {new_hints}")
                st.memory.case_hints = dict(new_hints)
            else:
                st.memory.case_hints.update(new_hints)
            if st.phase == "VERIFY_ID":
                st.memory.notes.append(f"Remembered during verification: {new_hints}")
                st.log(f"stored case hints for later: {new_hints}")
        if ex.intent != "none":
            if st.memory.intent != ex.intent:
                st.log(f"intent = {ex.intent}")
            st.memory.intent = ex.intent
        st.emotion = {"label": ex.emotion, "intensity": ex.emotion_intensity}

    # ---------------------------------------------------------------- step 3: gates
    def _run_gates(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> None:
        if st.phase == "ESCALATED":
            d.append("The caller has already been transferred. Reassure them briefly that a human representative "
                     "will pick this up; do not restart verification or discuss the claim.")
            return

        if ex.wants_human:
            self._escalate(st, d, "caller asked for a human representative")
            return

        if not ex.in_scope and not ex.is_small_talk:
            self._off_topic(st, ex, d)
            if st.phase == "ESCALATED":
                return
            d.append(self._phase_reminder(st))
            self._phase_facts(st, facts)
            return
        if not ex.is_small_talk and st.counters.off_topic:
            st.counters.on_topic_streak += 1
            if st.counters.on_topic_streak >= 2:   # two real turns in a row clears the strikes; alternating does not
                st.counters.off_topic = 0
                st.counters.on_topic_streak = 0

        # Phase handlers may chain within a single turn (e.g. verified -> intent resolved -> case loaded).
        for _ in range(4):
            handler = getattr(self, f"_phase_{st.phase.lower()}")
            nxt = handler(st, ex, d, facts)
            if not nxt:
                break

    def _off_topic(self, st: SessionState, ex: Extraction, d: list[str]) -> None:
        st.counters.off_topic += 1
        st.counters.on_topic_streak = 0
        n, limit = st.counters.off_topic, self.s.off_topic_limit
        topic = ex.off_topic_summary or "that topic"
        st.log(f"off-topic request #{n} ({topic})")
        if n > limit:
            self._escalate(st, d, f"repeated off-topic requests ({n})")
            return
        if n == limit:
            d.append(f"The caller has asked about unrelated topics {n} times ({topic}). Decline politely in one "
                     "sentence, explain that this line only handles insurance policy and claim matters, and "
                     "ask directly whether they would like to be transferred to a human representative or "
                     "continue with their claim. Do not answer the unrelated question.")
        else:
            d.append(f"The caller asked about something unrelated ({topic}). Do not answer it. Decline in one "
                     "friendly sentence, then steer back to the current step.")

    def _escalate(self, st: SessionState, d: list[str], reason: str) -> None:
        st.phase = "ESCALATED"
        st.escalation_reason = reason
        st.log(f"ESCALATED: {reason}")
        st.tool("transfer_to_human", {"reason": reason, "verified": st.verified},
                {"ticket": f"HR-{uuid.uuid4().hex[:6].upper()}", "queue": "claims_support"})
        extra = ("Because identity was not verified, tell them the representative will complete verification "
                 "first. " if not st.verified else "")
        d.append(f"Transfer the caller to a human representative now (reason: {reason}). Say it warmly and "
                 f"briefly: a claims representative will take over this conversation and follow up using the "
                 f"contact details on file. {extra}Do not discuss claim details.")

    def _phase_reminder(self, st: SessionState) -> str:
        return {
            "VERIFY_ID": "Then return to verification: restate which identity items are still needed.",
            "RESOLVE_INTENT": "Then ask again which claim or question they need help with.",
            "PROCESS_CASE": "Then ask if there is anything else about their claim you can help with.",
            "POST_PROCESS": "Then repeat the email summary offer briefly.",
            "CLOSED": "Then close warmly.",
        }.get(st.phase, "")

    def _phase_facts(self, st: SessionState, facts: dict) -> None:
        """Facts appropriate to the current phase, used when the turn is spent on scope handling."""
        if st.phase == "PROCESS_CASE" and st.selected_claim_id:
            facts["claim"] = self.fx.get_claim(st.selected_claim_id)

    # -------------------------------------------------------------- VERIFY_ID
    def _phase_verify_id(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        v = st.verification
        if st.caller_role == "representative":
            return self._verify_representative(st, ex, d)

        ident = st.identity
        candidate, via = find_candidate(ident, self.fx)
        st.tool("lookup_policyholder", {k: ("***" if k == "id_last4" else val) for k, val in ident.items()},
                {"found": bool(candidate), "via": via})

        if candidate is None:
            provided = [f for f in PII_FIELDS if ident.get(f)]
            if via == "ambiguous_name":
                d.append("More than one record matches that name. Ask for the policy number or the phone number "
                         "on file to locate the right account.")
            elif ident.get("full_name") or ident.get("policy_number"):
                v.attempts += 1
                st.log(f"no record located (attempt {v.attempts})")
                if v.attempts >= self.s.max_verification_attempts:
                    self._escalate(st, d, "could not locate a matching policy after several attempts")
                    return None
                d.append("We could not locate an account with the details given. Do not say whether a person "
                         "or policy exists. Ask them to double-check the spelling of the full name as it appears "
                         "on the policy, or to provide the policy number, and offer the phone number or email on "
                         f"file as alternatives. (Locate attempt {v.attempts} of {self.s.max_verification_attempts}.)")
            else:
                d.append("Ask for the caller's full name (and policy number if they have it handy), plus two "
                         "more of: date of birth, phone number on file, email on file, or last four of SSN/ID. "
                         "If they have already given some of these, only ask for what is missing.")
            self._verify_side_notes(st, ex, d, provided)
            return None

        res = match_record(ident, candidate)
        v.matched, v.mismatched, v.lookup_via = res.matched, res.mismatched, via
        st.tool("verify_identity", {"fields": res.provided},
                {"matched": res.matched, "mismatched": res.mismatched})

        # Three matching items is the rule; a stray mismatch on a fourth item does not block.
        if len(res.matched) >= self.s.required_pii_matches:
            v.status, v.method, v.party_id = "verified", "self", candidate["party_id"]
            st.phase = "RESOLVE_INTENT"
            st.log(f"VERIFIED via {res.matched}; party {candidate['party_id']}")
            first = candidate["name"].split()[0]
            d.append(f"Verification is complete (matched: {', '.join(FIELD_LABELS[f] for f in res.matched)}). "
                     f"Thank {first} briefly and move straight on to their claim.")
            return "RESOLVE_INTENT"

        if res.mismatched:
            if self._charge_mismatch(st, ex, res.mismatched):
                st.log(f"mismatch on {res.mismatched} (attempt {v.attempts})")
            if v.attempts >= self.s.max_verification_attempts:
                v.status = "failed"
                self._escalate(st, d, "identity could not be verified after the maximum number of attempts")
                return None
            labels = ", ".join(FIELD_LABELS[f] for f in res.mismatched)
            d.append(f"The {labels} the caller gave does not match our records. Say that plainly without revealing "
                     "what we have on file and without confirming that any account was located; ask them to "
                     "double-check it, or offer another item instead "
                     f"(options: {self._remaining_options(res)}). This is attempt {v.attempts} of "
                     f"{self.s.max_verification_attempts}; after that we must hand over to a human representative.")
            self._verify_side_notes(st, ex, d, res.provided)
            return None

        need = self.s.required_pii_matches - len(res.matched)
        d.append(f"Verification is in progress: {len(res.matched)} of {self.s.required_pii_matches} items confirmed. "
                 f"Ask for {need} more from: {self._remaining_options(res)}. Do not re-ask for items already given, "
                 "and do not say that an account or policy was found.")
        self._verify_side_notes(st, ex, d, res.provided)
        return None

    def _charge_mismatch(self, st: SessionState, ex: Extraction, mismatched: list[str]) -> bool:
        """One attempt per turn in which the caller asserts a value that does not
        match, including restating the same wrong value. A turn that only supplies
        other items is not charged for a mismatch reported earlier."""
        v = st.verification
        asserted = [f for f in mismatched if getattr(ex.identity, f, None)]
        if not asserted:
            return False
        v.seen_mismatches = sorted(set(v.seen_mismatches) | set(asserted))
        v.attempts += 1
        return True

    def _remaining_options(self, res) -> str:
        return ", ".join(FIELD_LABELS[f] for f in PII_FIELDS if f not in res.matched) or "none"

    def _verify_side_notes(self, st: SessionState, ex: Extraction, d: list[str], provided: list[str]) -> None:
        """Emotion, pushback, and memory acknowledgements that ride along with verification."""
        if ex.refuses_verification:
            st.counters.pushback += 1
            st.log(f"verification pushback #{st.counters.pushback}")
        if ex.refuses_verification or ex.questions_why_verify:
            d.append("The caller is pushing back on verification. Acknowledge the frustration genuinely, then "
                     "explain in one or two sentences why it matters: claim details are protected personal "
                     "information and we are required to confirm we are speaking with the policyholder before "
                     "sharing anything, which also protects them. Make it easy: name exactly what is still "
                     "needed and the alternatives they can choose from.")
        if st.counters.pushback >= self.s.pushback_limit:
            d.append("They have pushed back more than once. Stop persuading. Offer a clear choice: continue with "
                     "any of the remaining identity items, or be transferred to a human representative (who will "
                     "also need to verify identity). Do not disclose anything.")
        if st.memory.case_hints and not ex.refuses_verification:
            gist = st.memory.case_hints.get("details") or json.dumps(st.memory.case_hints)
            d.append(f"The caller already mentioned what they are calling about ({gist}). Acknowledge in a few "
                     "words that you have noted it and will pull it up as soon as verification is done. Do not "
                     "confirm or discuss anything about it.")

    # ------------------------------------------------------- representative path
    def _verify_representative(self, st: SessionState, ex: Extraction, d: list[str]) -> str | None:
        v, c, rep = st.verification, st.consent, st.representative
        missing = [k for k in ("name", "relationship", "policyholder_name") if not rep.get(k)]
        if missing and c.status is None:
            labels = {"name": "the caller's own full name", "relationship": "their relationship to the policyholder",
                      "policyholder_name": "the policyholder's full name"}
            d.append("The caller is contacting us on behalf of a policyholder. Explain that we can help an "
                     "authorised representative once the policyholder consents, and ask for: "
                     + ", ".join(labels[m] for m in missing) + ".")
            self._verify_side_notes(st, ex, d, [])
            return None

        if c.status is None:
            match = self.fx.find_representative(rep.get("name"), rep.get("policyholder_name"), rep.get("relationship"))
            st.tool("lookup_representative", dict(rep), {"found": bool(match)})
            if not match:
                v.attempts += 1
                if v.attempts >= self.s.max_verification_attempts:
                    self._escalate(st, d, "caller is not on file as an authorised representative")
                    return None
                d.append("We do not have the caller on file as an authorised representative for that policyholder. "
                         "Do not confirm whether the policyholder or policy exists. Explain the options: the "
                         "policyholder can call us directly, or can add them as an authorised representative, or "
                         "a human representative can review. Ask them to double-check the names given.")
                return None
            holder = self.fx.policyholder_by_party(match["buyer_party_id"])
            # Being named on file is not identity. The representative must still pass the
            # same three-item check against the policyholder's record before we contact anyone.
            ident = dict(st.identity)
            ident.setdefault("full_name", rep.get("policyholder_name"))
            res = match_record(ident, holder)
            v.matched, v.mismatched = res.matched, res.mismatched
            st.tool("verify_identity", {"fields": res.provided, "on_behalf_of": holder["party_id"]},
                    {"matched": res.matched, "mismatched": res.mismatched})
            if len(res.matched) < self.s.required_pii_matches:
                if res.mismatched and self._charge_mismatch(st, ex, res.mismatched):
                    st.log(f"representative gave mismatching {res.mismatched} (attempt {v.attempts})")
                if v.attempts >= self.s.max_verification_attempts:
                    self._escalate(st, d, "representative could not verify the policyholder's details")
                    return None
                need = self.s.required_pii_matches - len(res.matched)
                bad = (f" The {', '.join(FIELD_LABELS[f] for f in res.mismatched)} given does not match our records; "
                       "say so without revealing what we hold." if res.mismatched else "")
                d.append(f"The caller says they are {rep.get('name')}, {rep.get('relationship')} of "
                         f"{rep.get('policyholder_name')}. Before we can send the policyholder a consent request we "
                         f"need {need} more of the policyholder's details from: {self._remaining_options(res)}.{bad} "
                         "Do not confirm whether the policyholder, the policy, or the representative is on file.")
                self._verify_side_notes(st, ex, d, res.provided)
                return None
            v.party_id = match["buyer_party_id"]
            c.status, c.polls = "pending", 0
            c.request_id = f"CONSENT-{uuid.uuid4().hex[:6].upper()}"
            v.status = "consent_pending"
            st.tool("request_consent", {"party_id": v.party_id, "rep": match["rep_name"]},
                    {"request_id": c.request_id, "status": "pending"})
            st.log(f"representative matched ({match['relationship']}); consent request {c.request_id} sent")
            d.append("The policyholder's details check out. Explain that we have just sent a consent request "
                     "to the policyholder using the contact details on file, and that once it is approved you "
                     "can go through the claim with them. Do not say whether the caller is listed as a "
                     "representative; that is confirmed only by the policyholder's consent. Ask them to let you "
                     "know when to check on it (the policyholder usually responds within a minute or two).")
            return None

        if c.status == "pending":
            seq = self.fx.consent_sequence(c.scenario)
            status = seq[c.polls] if c.polls < len(seq) else "timeout"
            c.polls += 1
            st.tool("poll_consent", {"request_id": c.request_id, "poll": c.polls}, {"status": status})
            if status == "approved":
                c.status = "approved"
                v.status, v.method = "verified", "representative"
                st.phase = "RESOLVE_INTENT"
                st.log("consent approved; representative verified")
                holder = self.fx.policyholder_by_party(v.party_id)
                d.append(f"Consent from {holder['name']} has been received and the caller is now verified as their "
                         "authorised representative. Say so briefly and move on to the claim.")
                return "RESOLVE_INTENT"
            if status == "timeout":
                c.status = "timeout"
                st.log("consent request timed out")
                d.append("The consent request has not been approved and has now timed out. Do not disclose any "
                         "claim details. Explain the alternatives kindly: the policyholder can call us directly, "
                         "or can respond to a new consent request later, or you can hand this to a human "
                         "representative. Ask which they prefer.")
                return None
            d.append(f"Consent is still pending (checked {c.polls} time(s)). Say you have checked and it has not "
                     "come through yet; offer to check again in a moment, and reassure them. Do not disclose "
                     "any claim details.")
            return None

        if c.status == "timeout":
            # An explicit request for a human is handled by the global gate; anything else re-offers the options.
            d.append("Consent has timed out. Restate the alternatives (policyholder calls directly, new consent "
                     "request later, or transfer to a human representative) and ask which they would like. "
                     "Do not disclose any claim details.")
            return None
        return None

    # ----------------------------------------------------------- RESOLVE_INTENT
    def _phase_resolve_intent(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        if ex.wants_to_end:
            if st.selected_claim_id:
                st.phase = "POST_PROCESS"
                return "POST_PROCESS"
            st.phase = "CLOSED"
            st.log("caller ended the conversation before choosing a claim")
            d.append("The caller wants to leave without going into a claim. Close warmly and invite them to reach "
                     "out again; no email summary is needed since nothing was discussed.")
            return None

        claims = self.fx.claims_for_party(st.verification.party_id)
        st.tool("list_claims", {"party_id": st.verification.party_id}, [c["case_id"] for c in claims])
        hints = st.memory.case_hints
        cands = self._filter_claims(claims, hints)
        if hints and not cands:
            # Cumulative hints can contradict each other after a correction; fall back to this turn only.
            turn_hints = self._turn_hints(ex)
            turn_hints["claim_id"] = self._clean_claim_id(st, turn_hints.get("claim_id"))
            turn_hints = {k: v for k, v in turn_hints.items() if v}
            if turn_hints:
                cands = self._filter_claims(claims, turn_hints)
                if cands:
                    st.memory.case_hints = dict(turn_hints)
                    hints = st.memory.case_hints
                    st.log(f"stale hints discarded; using this turn's: {turn_hints}")

        chosen = None
        if ex.selected_claim_id and self.fx.get_claim(ex.selected_claim_id) in claims:
            chosen = self.fx.get_claim(ex.selected_claim_id)
        elif hints.get("claim_id") and self.fx.get_claim(hints["claim_id"]) in claims:
            chosen = self.fx.get_claim(hints["claim_id"])
        elif len(cands) == 1 and (hints or len(claims) == 1):
            chosen = cands[0]

        if chosen:
            st.selected_claim_id = chosen["case_id"]
            st.phase = "PROCESS_CASE"
            how = "from what the caller told you earlier" if hints else "the only claim on file"
            st.log(f"claim {chosen['case_id']} selected ({how})")
            d.append(f"You have located the claim the caller means ({how}): {chosen['case_id']}, "
                     f"{chosen['case_type']}, opened {chosen['created_at']}, status {chosen['status']}. Confirm in "
                     "one short line that this is the claim you have pulled up, then address their need directly.")
            return "PROCESS_CASE"

        facts["claims_on_file"] = [self.fx.claim_summary(c) for c in claims]
        if hints and not cands:
            d.append(f"None of the claims on file match what the caller described ({hints}). Say so gently, list the "
                     "claims on file (id, type, date, status) and ask which one they mean.")
        elif len(cands) > 1:
            facts["matching_claims"] = [self.fx.claim_summary(c) for c in cands]
            d.append("More than one claim matches what they described. List the matching claims briefly (id, type, "
                     "date, status) and ask which one they mean.")
        else:
            d.append("Ask what they need help with today. You may list the claims on file (id, type, date, status) "
                     "to help them pick one. Do not discuss any claim's details yet.")
        return None

    def _clean_claim_id(self, st: SessionState, raw: str | None) -> str | None:
        """The extractor sometimes files a policy number under claim_id. Only keep values
        that look like a claim reference and are not the caller's policy number."""
        if not raw:
            return None
        cid = raw.strip().upper().replace(" ", "")
        pol = re.sub(r"[^A-Z0-9]", "", (st.identity.get("policy_number") or "").upper())
        if pol and re.sub(r"[^A-Z0-9]", "", cid) == pol:
            st.log(f"ignored claim_id {cid}: it is the policy number")
            return None
        if not re.match(r"^CL-?\d+$", cid):
            st.log(f"ignored claim_id {cid}: not a claim reference")
            return None
        return cid if cid.startswith("CL-") else "CL-" + cid[2:]

    def _turn_hints(self, ex: Extraction) -> dict:
        h = ex.case_hints
        return {k: v for k, v in {"case_type": h.case_type, "status": h.status, "timeframe": h.timeframe,
                                  "claim_id": h.claim_id}.items()
                if v and v != "unknown"}

    def _filter_claims(self, claims: list[dict], hints: dict) -> list[dict]:
        out = claims
        if hints.get("case_type"):
            out = [c for c in out if c["case_type"] == hints["case_type"]]
        if hints.get("status"):
            out = [c for c in out if c["status"] == hints["status"]]
        tf = (hints.get("timeframe") or "").lower()
        if tf:
            month = year = None
            iso = re.search(r"\b(20\d\d)-(\d\d)\b", tf)            # "2026-01"
            if iso:
                year, month = iso.group(1), int(iso.group(2))
            else:
                month = next((m for name, m in MONTHS.items()
                              if re.search(rf"\b{name}\b|\b{name[:3]}\b", tf)), None)
                y = re.search(r"\b20\d\d\b", tf)
                year = y.group(0) if y else None
            narrowed = out
            if month:
                narrowed = [c for c in narrowed if int(c["created_at"][5:7]) == month]
            if year:
                narrowed = [c for c in narrowed if c["created_at"][:4] == year]
            if narrowed:                     # a timeframe that matches nothing is treated as noise, not a veto
                out = narrowed
        return out

    # ------------------------------------------------------------- PROCESS_CASE
    def _phase_process_case(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        claims = self.fx.claims_for_party(st.verification.party_id)
        claim = self.fx.get_claim(st.selected_claim_id)

        # Claim switching: the caller names another claim, or this turn's hints point uniquely elsewhere.
        switch = None
        named = self._clean_claim_id(st, ex.selected_claim_id or ex.case_hints.claim_id) or ""
        if named and named != st.selected_claim_id:
            switch = self.fx.get_claim(named)
            if switch not in claims:
                st.log(f"caller named {named}, which is not on this account")
                d.append(f"The caller mentioned claim {named}, which is not on this account. Say you do not see a "
                         "claim with that reference on file and ask them to double-check it; continue with the "
                         "current claim otherwise.")
                switch = None
        else:
            turn_hints = {k: v for k, v in self._turn_hints(ex).items() if k != "claim_id"}
            if turn_hints:
                c2 = self._filter_claims(claims, turn_hints)
                if len(c2) == 1 and c2[0]["case_id"] != st.selected_claim_id:
                    switch = c2[0]
        if switch:
            st.selected_claim_id = switch["case_id"]
            claim = switch
            st.log(f"switched to claim {claim['case_id']}")
            d.append(f"The caller is now asking about a different claim: {claim['case_id']} ({claim['case_type']}, "
                     f"{claim['status']}). Say you have switched to it, then answer.")

        if ex.wants_to_end:
            st.phase = "POST_PROCESS"
            st.log("caller has no further questions; moving to POST_PROCESS")
            return "POST_PROCESS"

        if claim["case_id"] not in st.discussed_claim_ids:
            st.discussed_claim_ids.append(claim["case_id"])
        facts["claim"] = claim
        facts["document_guidance"] = self.fx.guidance_for_claim(claim)
        facts["field_meanings"] = self.fx.claim_schema["field_descriptions"]
        facts["other_claims_on_file"] = [self.fx.claim_summary(c) for c in claims if c["case_id"] != claim["case_id"]]
        earlier = [self.fx.get_claim(cid) for cid in st.discussed_claim_ids if cid != claim["case_id"]]
        if earlier:
            # Records already disclosed to this verified caller stay available, so the model never
            # "retracts" a correct earlier answer just because the focus moved to another claim.
            facts["claims_already_discussed_this_call"] = earlier
        st.tool("get_claim", {"case_id": claim["case_id"]}, {"status": claim["status"]})

        intent = ex.intent if ex.intent != "none" else st.memory.intent
        d.append({
            "denial_question": "Explain why the claim was denied using the denial_reason, which documents are needed, "
                               "how to submit them, and the appeal deadline. Offer the document guidance if useful.",
            "status_inquiry": "Give the current status and what it means; for a denied claim include what would move "
                              "it forward and the deadline.",
            "document_submission": "Explain exactly which documents are needed, what each must contain, how to submit "
                                   "them, and what happens after submission (processing time).",
            "next_steps": "Lay out the concrete next steps and any deadlines.",
            "appeal": "Explain what is needed to have the denial reconsidered (documents, submission, deadline) and "
                      "that review restarts once the documents are received.",
            "general_claim_question": "Answer the question from the claim record and guidance.",
        }.get(intent, "Answer the caller's question from the claim record and guidance."))
        d.append("If they ask something the grounding data does not cover, say you do not have that detail and "
                 "offer to have a claims representative follow up. If they cannot obtain a required document, use "
                 "the 'if_unavailable' guidance, and mention human review only when the alternatives are exhausted.")
        return None

    # ------------------------------------------------------------- POST_PROCESS
    def _phase_post_process(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        em = st.email
        holder = self.fx.policyholder_by_party(st.verification.party_id)
        on_file = holder["email"] if holder else None

        if not em.offered:
            em.offered = True
            st.log("email summary offered")
            if ex.email_decision == "skip":
                # "That's all, and no email please" in one breath: honour it without re-asking.
                em.decision = "skip"
                st.phase = "CLOSED"
                st.log("caller declined the email summary up front")
                d.append("They have said they do not want an email summary. Confirm that no email will be sent "
                         "and close warmly. Do not invent follow-ups.")
                return None
            hint = ""
            if ex.provided_email:
                em.address = ex.provided_email.strip()
                hint = f" They mentioned {em.address}; offer to use that address, but wait for a yes."
            d.append("Wrap up: offer to send an email summary of today's conversation (what was discussed, the claim "
                     f"status/outcome, and next steps). It can go to the email on file ({mask_email(on_file)}) or to "
                     f"another address they give you, or they can skip it. Ask which they prefer.{hint}")
            return None

        # The offer has been made; only now can an address or a yes trigger a send.
        decision = ex.email_decision
        if decision == "none":
            if ex.provided_email or ex.affirmation == "yes":
                decision = "send"
            elif ex.affirmation == "no" or ex.wants_to_end:
                decision = "skip"
        if ex.provided_email:
            em.address = ex.provided_email.strip()

        if decision == "send":
            address = em.address or on_file
            if not address:
                d.append("Ask which email address the summary should go to.")
                return None
            em.address, em.decision = address, "send"
            self._send_summary(st, address)
            st.phase = "CLOSED"
            facts["email_summary"] = {"to": address, "subject": em.subject, "delivery": em.delivery}
            verb = "sent" if em.delivery in ("smtp", "brevo") else "prepared and queued for delivery"
            d.append(f"The summary email has been {verb} to {address}. Confirm that, mention it covers what was "
                     "discussed and the next steps, and close the conversation warmly.")
            return None
        if decision == "skip":
            em.decision = "skip"
            st.phase = "CLOSED"
            st.log("caller skipped the email summary")
            d.append("They do not want the email. Confirm that no email will be sent and close warmly. You may "
                     "restate a next step only if one was actually discussed; do not invent follow-ups.")
            return None
        if ex.intent != "none" and ex.in_scope:
            st.phase = "PROCESS_CASE"
            st.log("new claim question during wrap-up; back to PROCESS_CASE")
            return "PROCESS_CASE"
        d.append("It is unclear whether they want the summary email. Ask again briefly: send to the address on file, "
                 "a different address, or skip.")
        return None

    def _send_summary(self, st: SessionState, address: str) -> None:
        claim = self.fx.get_claim(st.selected_claim_id) if st.selected_claim_id else None
        holder = self.fx.policyholder_by_party(st.verification.party_id)
        convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in st.transcript)
        payload = json.dumps({
            "caller_first_name": (st.representative.get("name") or holder["name"]).split()[0],
            "policyholder": holder["name"],
            "claim": claim, "document_guidance": self.fx.guidance_for_claim(claim) if claim else None,
            "today": self._today(),
        }, indent=2)
        summary = self.llm.summarize(prompts.SUMMARY_SYSTEM, f"DATA:\n{payload}\n\nTRANSCRIPT:\n{convo}")
        result = self.emailer.send(address, summary.subject, summary.body)
        st.email.subject, st.email.body = summary.subject, summary.body
        st.email.sent = result.get("delivery") in ("smtp", "brevo", "mock")
        st.email.delivery = result.get("delivery")
        st.tool("send_email", {"to": address, "subject": summary.subject},
                {"delivery": result.get("delivery"), "note": result.get("note"), "error": result.get("error")})
        st.log(f"summary email -> {address} ({result.get('delivery')})")

    # ------------------------------------------------------------------ CLOSED
    def _phase_closed(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        turn_hints = self._turn_hints(ex)
        turn_hints["claim_id"] = self._clean_claim_id(st, turn_hints.get("claim_id"))
        turn_hints = {k: v for k, v in turn_hints.items() if v}
        identifiers = {k: v for k, v in turn_hints.items() if k in ("case_type", "claim_id", "timeframe")}
        if ex.intent != "none" or turn_hints:
            st.email = type(st.email)()
            st.log("conversation reopened by the caller")
            if identifiers or not st.selected_claim_id:
                # They are pointing at a (possibly different) claim: resolve it again from this turn only.
                st.memory.case_hints = dict(turn_hints)
                if ex.case_hints.details:
                    st.memory.case_hints["details"] = ex.case_hints.details
                st.phase = "RESOLVE_INTENT"
                return "RESOLVE_INTENT"
            # A follow-up about the claim we just discussed: keep it, no need to ask which one.
            st.phase = "PROCESS_CASE"
            return "PROCESS_CASE"
        d.append("The conversation is complete. Reply briefly and warmly.")
        return None

    # ----------------------------------------------------------- step 4: respond
    def _responder_system(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str:
        parts = [prompts.RESPONDER_BASE.format(today=self._today()),
                 "", prompts.PHASE_RULES[st.phase], ""]
        ctx = ["CALLER CONTEXT:"]
        if st.verified:
            holder = self.fx.policyholder_by_party(st.verification.party_id)
            who = holder["name"]
            if st.verification.method == "representative":
                who = f"{st.representative.get('name')} ({st.representative.get('relationship')} of {holder['name']}, consent on file)"
            ctx.append(f"- Verified caller: {who}")
        else:
            given = st.identity.get("full_name") or st.representative.get("name")
            ctx.append(f"- Caller NOT verified. Name they gave: {given or 'not given yet'} (you may use the first name).")
        ctx.append(f"- Caller emotion this message: {ex.emotion} ({ex.emotion_intensity})")
        if ex.emotion in prompts.EMOTION_GUIDANCE and ex.emotion_intensity != "low":
            ctx.append("- " + prompts.EMOTION_GUIDANCE[ex.emotion])
        parts += ctx + [""]
        parts.append("INSTRUCTIONS FOR THIS TURN:")
        parts += [f"- {x}" for x in d]
        parts.append("")
        parts.append("GROUNDING DATA (the only policy/claim facts you may state; empty means you know nothing yet):")
        parts.append(json.dumps(facts, indent=2) if facts else "{}")
        return "\n".join(parts)

    def _api_messages(self, st: SessionState) -> list[dict]:
        msgs = st.transcript[-16:]
        while msgs and msgs[0]["role"] != "user":   # API requires the first message to be from the user
            msgs = msgs[1:]
        return [{"role": m["role"], "content": m["content"]} for m in msgs]

    # ------------------------------------------------------------- step 5: guard
    _MONTHS_RE = "january|february|march|april|may|june|july|august|september|october|november|december"

    def _grounding_guard(self, st: SessionState, reply: str, facts: dict, system: str) -> str:
        """After verification the model may only state figures and dates that exist in the
        grounding data. Any other amount or date triggers one regeneration that names the
        offending values; if it persists, the values are replaced with a safe phrase."""
        if not st.verified or not facts:
            return reply
        blob = json.dumps(facts).lower()
        allowed_dates = set(re.findall(r"\d{4}-\d{2}-\d{2}", blob)) | {self._today()}
        allowed_amounts = {a.replace(",", "") for a in re.findall(r"\d[\d,]*\.\d{2}", blob)}

        def unsupported(text: str) -> list[str]:
            bad = []
            for iso in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text):
                if iso not in allowed_dates:
                    bad.append(iso)
            for m in re.finditer(rf"\b({self._MONTHS_RE})\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b", text, re.I):
                iso = f"{m.group(3)}-{MONTHS[m.group(1).lower()]:02d}-{int(m.group(2)):02d}"
                if iso not in allowed_dates:
                    bad.append(m.group(0))
            for a in re.findall(r"\$?\d[\d,]*\.\d{2}\b", text):
                if a.lstrip("$").replace(",", "") not in allowed_amounts:
                    bad.append(a)
            return bad

        bad = unsupported(reply)
        if not bad:
            return reply
        st.log(f"GROUNDING GUARD: unsupported values {bad}; regenerating")
        retry_system = system + ("\n\nCORRECTION: your previous draft contained figures or dates that are not in "
                                 f"the grounding data: {bad}. Rewrite the reply without them. If the caller asked "
                                 "for that information, say you do not have it on file and offer a follow-up.")
        reply2 = self.llm.respond(retry_system, self._api_messages(st))
        bad2 = unsupported(reply2)
        if not bad2:
            return reply2
        st.log(f"GROUNDING GUARD: still unsupported {bad2}; redacting")
        for v in bad2:
            reply2 = reply2.replace(v, "[not on file]")
        return reply2

    def _output_guard(self, st: SessionState, reply: str) -> str:
        """Belt and braces: claim data is never in the model's context before
        verification, but scan anyway and replace the reply if anything leaks."""
        if st.verified:
            return reply
        low = reply.lower()
        leaks = [c["case_id"] for c in self.fx.claims if c["case_id"].lower() in low]
        for c in self.fx.claims:
            for key in ("denial_reason", "summary"):
                if c.get(key) and c[key].lower()[:40] in low:
                    leaks.append(f"{c['case_id']}.{key}")
            for key in ("appeal_deadline", "allowed_max_amount", "net_pay", "expected_reimbursement_amount"):
                val = str(c.get(key, "")).lower()
                if val and val not in ("0.00",) and val in low:
                    leaks.append(f"{c['case_id']}.{key}")
        if leaks:
            st.log(f"OUTPUT GUARD blocked reply mentioning {leaks}")
            return ("I'm not able to go into any claim details until we've finished verifying your identity. "
                    "Could you give me the remaining details so I can pull that up for you?")
        return reply
