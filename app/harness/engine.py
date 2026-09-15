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
        reply = self._output_guard(st, reply)
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
            st.caller_role = ex.caller_role
            st.log(f"caller_role = {ex.caller_role}")
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
        if hints.claim_id:
            new_hints["claim_id"] = hints.claim_id.upper()
        if hints.details:
            new_hints["details"] = hints.details
        if new_hints:
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

        # Phase handlers may chain within a single turn (e.g. verified -> intent resolved -> case loaded).
        for _ in range(4):
            handler = getattr(self, f"_phase_{st.phase.lower()}")
            nxt = handler(st, ex, d, facts)
            if not nxt:
                break

    def _off_topic(self, st: SessionState, ex: Extraction, d: list[str]) -> None:
        st.counters.off_topic += 1
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

        if res.mismatched:
            new = [f for f in res.mismatched if f not in v.seen_mismatches]
            if new:
                v.attempts += 1
                v.seen_mismatches += new
                st.log(f"mismatch on {new} (attempt {v.attempts})")
            if v.attempts >= self.s.max_verification_attempts:
                v.status = "failed"
                self._escalate(st, d, "identity could not be verified after the maximum number of attempts")
                return None
            labels = ", ".join(FIELD_LABELS[f] for f in res.mismatched)
            d.append(f"The {labels} the caller gave does not match our records. Say that plainly without revealing "
                     "what we have on file, ask them to double-check it, and offer an alternative item instead "
                     f"(remaining options: {self._remaining_options(res)}). This is attempt {v.attempts} of "
                     f"{self.s.max_verification_attempts}; after that we must hand over to a human representative.")
            self._verify_side_notes(st, ex, d, res.provided)
            return None

        if len(res.matched) >= self.s.required_pii_matches:
            v.status, v.method, v.party_id = "verified", "self", candidate["party_id"]
            st.phase = "RESOLVE_INTENT"
            st.log(f"VERIFIED via {res.matched}; party {candidate['party_id']}")
            first = candidate["name"].split()[0]
            d.append(f"Verification is complete (matched: {', '.join(FIELD_LABELS[f] for f in res.matched)}). "
                     f"Thank {first} briefly and move straight on to their claim.")
            return "RESOLVE_INTENT"

        need = self.s.required_pii_matches - len(res.matched)
        d.append(f"Verification is in progress: {len(res.matched)} of {self.s.required_pii_matches} items confirmed. "
                 f"Ask for {need} more from: {self._remaining_options(res)}. Do not re-ask for items already given.")
        self._verify_side_notes(st, ex, d, res.provided)
        return None

    def _remaining_options(self, res) -> str:
        return ", ".join(FIELD_LABELS[f] for f in PII_FIELDS if f not in res.provided) or "none"

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
            v.party_id = match["buyer_party_id"]
            holder = self.fx.policyholder_by_party(v.party_id)
            c.status, c.polls = "pending", 0
            c.request_id = f"CONSENT-{uuid.uuid4().hex[:6].upper()}"
            v.status = "consent_pending"
            st.tool("request_consent", {"party_id": v.party_id, "rep": match["rep_name"]},
                    {"request_id": c.request_id, "status": "pending"})
            st.log(f"representative matched ({match['relationship']}); consent request {c.request_id} sent")
            d.append(f"The caller is on file as {holder['name'].split()[0]}'s {match['relationship']}. Explain that "
                     "we have just sent a consent request to the policyholder using the contact details on file, "
                     "and that once it is approved you can go through the claim with them. Ask them to let you "
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
            if ex.affirmation == "yes" or "human" in (ex.off_topic_summary or ""):
                self._escalate(st, d, "consent timed out; caller chose a human representative")
                return None
            d.append("Consent has timed out. Restate the alternatives (policyholder calls directly, new consent "
                     "request later, or transfer to a human representative) and ask which they would like.")
            return None
        return None

    # ----------------------------------------------------------- RESOLVE_INTENT
    def _phase_resolve_intent(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        claims = self.fx.claims_for_party(st.verification.party_id)
        st.tool("list_claims", {"party_id": st.verification.party_id}, [c["case_id"] for c in claims])
        hints = st.memory.case_hints
        cands = self._filter_claims(claims, hints)

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

    def _filter_claims(self, claims: list[dict], hints: dict) -> list[dict]:
        out = claims
        if hints.get("case_type"):
            out = [c for c in out if c["case_type"] == hints["case_type"]]
        if hints.get("status"):
            out = [c for c in out if c["status"] == hints["status"]]
        tf = (hints.get("timeframe") or "").lower()
        if tf:
            month = next((m for name, m in MONTHS.items() if name in tf or name[:3] in tf.split()), None)
            year = re.search(r"20\d\d", tf)
            narrowed = out
            if month:
                narrowed = [c for c in narrowed if int(c["created_at"][5:7]) == month]
            if year:
                narrowed = [c for c in narrowed if c["created_at"][:4] == year.group(0)]
            if narrowed or month or year:
                out = narrowed
        return out

    # ------------------------------------------------------------- PROCESS_CASE
    def _phase_process_case(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        claims = self.fx.claims_for_party(st.verification.party_id)
        claim = self.fx.get_claim(st.selected_claim_id)

        # Claim switching: the caller names another claim, or this turn's hints point uniquely elsewhere.
        switch = None
        if ex.selected_claim_id and ex.selected_claim_id.upper() != st.selected_claim_id:
            switch = self.fx.get_claim(ex.selected_claim_id)
        elif ex.case_hints.claim_id and ex.case_hints.claim_id.upper() != st.selected_claim_id:
            switch = self.fx.get_claim(ex.case_hints.claim_id)
        else:
            turn_hints = {k: v for k, v in {"case_type": ex.case_hints.case_type, "status": ex.case_hints.status,
                                             "timeframe": ex.case_hints.timeframe}.items() if v and v != "unknown"}
            if turn_hints:
                c2 = self._filter_claims(claims, turn_hints)
                if len(c2) == 1 and c2[0]["case_id"] != st.selected_claim_id:
                    switch = c2[0]
        if switch and switch in claims:
            st.selected_claim_id = switch["case_id"]
            claim = switch
            st.log(f"switched to claim {claim['case_id']}")
            d.append(f"The caller is now asking about a different claim: {claim['case_id']} ({claim['case_type']}, "
                     f"{claim['status']}). Say you have switched to it, then answer.")

        if ex.wants_to_end and ex.intent == "none":
            st.phase = "POST_PROCESS"
            st.log("caller has no further questions; moving to POST_PROCESS")
            return "POST_PROCESS"

        facts["claim"] = claim
        facts["document_guidance"] = self.fx.guidance_for_claim(claim)
        facts["field_meanings"] = self.fx.claim_schema["field_descriptions"]
        facts["other_claims_on_file"] = [self.fx.claim_summary(c) for c in claims if c["case_id"] != claim["case_id"]]
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

        if not em.offered and ex.email_decision == "none" and not ex.provided_email:
            em.offered = True
            st.log("email summary offered")
            d.append("Wrap up: offer to send an email summary of today's conversation (what was discussed, the claim "
                     f"status/outcome, and next steps). It can go to the email on file ({mask_email(on_file)}) or to "
                     "another address they give you, or they can skip it. Ask which they prefer.")
            return None
        em.offered = True

        decision = ex.email_decision
        if decision == "none":
            if ex.provided_email:
                decision = "send"
            elif ex.affirmation == "yes":
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
            if em.delivery == "failed":
                d.append(f"We tried to send the summary to {address} but delivery failed. Apologise briefly, say a "
                         "representative will make sure they receive it, and close warmly.")
            else:
                d.append(f"The summary email has been sent to {address}. Confirm that, mention it covers what was "
                         "discussed and the next steps, and close the conversation warmly.")
            return None
        if decision == "skip":
            em.decision = "skip"
            st.phase = "CLOSED"
            st.log("caller skipped the email summary")
            d.append("They do not want the email. Confirm that no email will be sent, recap the next steps in one "
                     "sentence, and close warmly.")
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
        st.email.sent = result.get("delivery") in ("smtp", "mock")
        st.email.delivery = result.get("delivery")
        st.tool("send_email", {"to": address, "subject": summary.subject},
                {"delivery": result.get("delivery"), "error": result.get("error")})
        st.log(f"summary email -> {address} ({result.get('delivery')})")

    # ------------------------------------------------------------------ CLOSED
    def _phase_closed(self, st: SessionState, ex: Extraction, d: list[str], facts: dict) -> str | None:
        has_hints = any(v and v != "unknown" for v in ex.case_hints.model_dump().values())
        if ex.intent != "none" or has_hints:
            st.memory.case_hints = {}
            st.email = type(st.email)()
            st.phase = "RESOLVE_INTENT"
            st.log("conversation reopened by the caller")
            hints = ex.case_hints
            st.memory.case_hints = {k: v for k, v in {"case_type": hints.case_type, "status": hints.status,
                                                     "timeframe": hints.timeframe, "claim_id": hints.claim_id,
                                                     "details": hints.details}.items() if v and v != "unknown"}
            return "RESOLVE_INTENT"
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
    def _output_guard(self, st: SessionState, reply: str) -> str:
        """Belt and braces: claim data is never in the model's context before
        verification, but scan anyway and replace the reply if anything leaks."""
        if st.verified:
            return reply
        leaks = [c["case_id"] for c in self.fx.claims if c["case_id"].lower() in reply.lower()]
        for c in self.fx.claims:
            for key in ("denial_reason", "summary"):
                if c.get(key) and c[key].lower()[:40] in reply.lower():
                    leaks.append(f"{c['case_id']}.{key}")
        if leaks:
            st.log(f"OUTPUT GUARD blocked reply mentioning {leaks}")
            return ("I'm not able to go into any claim details until we've finished verifying your identity. "
                    "Could you give me the remaining details so I can pull that up for you?")
        return reply
