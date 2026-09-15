"""Fixture-backed "tools". In production these would be CRM / claims-system
calls; here they read the JSON fixtures shipped with the assessment. The
engine only ever hands the LLM data that comes out of these functions, which
is what keeps answers grounded."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def norm_name(s: str | None) -> str:
    return re.sub(r"[^a-z ]", "", (s or "").lower()).strip()


def name_tokens(s: str | None) -> set[str]:
    return set(norm_name(s).split())


class Fixtures:
    def __init__(self, fixtures_dir: Path):
        self.dir = Path(fixtures_dir)
        self.policyholders: list[dict] = self._load("policyholders.json")
        self.claims: list[dict] = self._load("claims.json")
        self.representatives: list[dict] = self._load("representatives.json")
        self.consent_scenarios: dict = self._load("consent_scenarios.json")
        self.doc_guideline: dict = self._load("required_document_guideline.json")
        self.claim_schema: dict = self._load("claim_schema.json")

    def _load(self, name: str) -> Any:
        with open(self.dir / name, encoding="utf-8") as f:
            return json.load(f)

    # ---- policyholders -------------------------------------------------
    def policyholder_by_party(self, party_id: str) -> dict | None:
        return next((p for p in self.policyholders if p["party_id"] == party_id), None)

    def policyholder_by_policy(self, policy_number: str | None) -> dict | None:
        key = re.sub(r"[^A-Z0-9]", "", (policy_number or "").upper())
        if not key:
            return None
        for p in self.policyholders:
            if re.sub(r"[^A-Z0-9]", "", p["policy_number"].upper()) == key:
                return p
        return None

    def policyholders_by_name(self, name: str | None) -> list[dict]:
        """Token-set match (order-insensitive) against the name and its aliases."""
        want = name_tokens(name)
        if not want:
            return []
        out = []
        for p in self.policyholders:
            names = [p["name"], *p.get("name_aliases", [])]
            if any(name_tokens(n) == want for n in names):
                out.append(p)
        return out

    def policyholder_by_phone(self, phone: str | None) -> dict | None:
        d = re.sub(r"\D", "", phone or "")[-10:]
        if len(d) < 7:
            return None
        for p in self.policyholders:
            for ph in [p["phone"], *p.get("phone_aliases", [])]:
                if re.sub(r"\D", "", ph)[-10:] == d:
                    return p
        return None

    def policyholder_by_email(self, email: str | None) -> dict | None:
        e = (email or "").strip().lower()
        if not e:
            return None
        for p in self.policyholders:
            if e in [x.lower() for x in [p["email"], *p.get("email_aliases", [])]]:
                return p
        return None

    # ---- representatives -------------------------------------------------
    def find_representative(self, rep_name: str | None, policyholder_name: str | None,
                            relationship: str | None) -> dict | None:
        for r in self.representatives:
            if name_tokens(r["rep_name"]) != name_tokens(rep_name):
                continue
            holder = self.policyholder_by_party(r["buyer_party_id"])
            holder_names = [r["buyer_name"]]
            if holder:
                holder_names += [holder["name"], *holder.get("name_aliases", [])]
            if not any(name_tokens(n) == name_tokens(policyholder_name) for n in holder_names):
                continue
            if relationship and norm_name(relationship) != norm_name(r["relationship"]):
                continue
            return r
        return None

    # ---- claims ---------------------------------------------------------
    def claims_for_party(self, party_id: str) -> list[dict]:
        return [c for c in self.claims if c["party_id"] == party_id]

    def get_claim(self, case_id: str | None) -> dict | None:
        key = (case_id or "").upper().replace(" ", "")
        if not key:
            return None
        return next((c for c in self.claims if c["case_id"].upper() == key), None)

    @staticmethod
    def claim_summary(c: dict) -> dict:
        """Safe listing used only after verification, before a claim is selected."""
        return {"case_id": c["case_id"], "case_type": c["case_type"],
                "created_at": c["created_at"], "status": c["status"]}

    # ---- document guidance -----------------------------------------------
    def guidance_for_claim(self, claim: dict) -> dict:
        g = self.doc_guideline
        docs = claim.get("documents_needed", [])
        per_doc = {}
        for d in docs:
            entry = {"guidance": None, "if_unavailable": None}
            for key, val in g["document_guidance"].items():
                if d.lower() in key.lower() or key.lower() in d.lower():
                    entry["guidance"] = val["en"]
            for key, val in g["document_alternative_guidance"].items():
                if key != "default" and (d.lower() in key.lower() or key.lower() in d.lower()):
                    entry["if_unavailable"] = val["en"]
            if entry["if_unavailable"] is None:
                entry["if_unavailable"] = g["document_alternative_guidance"]["default"]["en"]
            per_doc[d] = entry
        avg = g["claim_followup_settings"]["average_processing_time_after_submission"]["en"]
        docs_text = ", ".join(docs) if docs else "the requested documents"
        followups = []
        for item in g["claim_followup_guidance"]:
            if item.get("requires_documents") and not docs:
                continue
            followups.append({
                "topic": item["topic"],
                "answer": item["en"].format(case_id=claim["case_id"], documents=docs_text,
                                            average_processing_time_after_submission=avg),
            })
        return {
            "general_submission_guidance": g["default_guidance"]["en"],
            "case_type_guidance": g["case_type_guidance"].get(claim["case_type"], {}).get("en"),
            "documents_needed": per_doc,
            "average_processing_time_after_submission": avg,
            "human_review_policy": g["claim_followup_settings"]["human_review_after_document_alternatives_exhausted"]["en"],
            "followup_answers": followups,
            "fallback_if_no_rule": g["claim_followup_fallback"]["en"],
        }

    # ---- consent ----------------------------------------------------------
    def consent_sequence(self, scenario: str | None) -> list[str]:
        sc = self.consent_scenarios.get(scenario or "default") or self.consent_scenarios["default"]
        return list(sc["status_sequence"])
