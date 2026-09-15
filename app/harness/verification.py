"""Deterministic identity matching. The LLM extracts what the caller *said*;
this module decides whether it matches the record. No model involvement, so
the gate cannot be talked around."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime

from .fixtures import Fixtures, name_tokens

PII_FIELDS = ["full_name", "dob", "phone", "email", "id_last4"]
FIELD_LABELS = {
    "full_name": "full name",
    "dob": "date of birth",
    "phone": "phone number on file",
    "email": "email address on file",
    "id_last4": "last four digits of SSN or national ID",
}


def norm_dob(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d %B %Y", "%B %d %Y", "%B %d, %Y", "%b %d %Y", "%b %d, %Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s.lower()


def norm_phone(s: str | None) -> str | None:
    d = re.sub(r"\D", "", s or "")
    return d[-10:] if len(d) >= 7 else None


def norm_email(s: str | None) -> str | None:
    return (s or "").strip().lower() or None


def norm_last4(s: str | None) -> str | None:
    d = re.sub(r"\D", "", s or "")
    return d[-4:] if len(d) >= 4 else None


@dataclass
class MatchResult:
    provided: list[str] = field(default_factory=list)
    matched: list[str] = field(default_factory=list)
    mismatched: list[str] = field(default_factory=list)


def find_candidate(identity: dict, fx: Fixtures) -> tuple[dict | None, str]:
    """Locate the record to compare against. Policy number is a *lookup key*
    only; it never counts toward the three required PII matches."""
    if identity.get("policy_number"):
        p = fx.policyholder_by_policy(identity["policy_number"])
        if p:
            return p, "policy_number"
    if identity.get("full_name"):
        hits = fx.policyholders_by_name(identity["full_name"])
        if len(hits) == 1:
            return hits[0], "full_name"
        if len(hits) > 1:
            # disambiguate with any other provided field
            for p in hits:
                r = match_record(identity, p)
                if len(r.matched) >= 2 and not r.mismatched:
                    return p, "full_name+other"
            return None, "ambiguous_name"
    if identity.get("phone"):
        p = fx.policyholder_by_phone(identity["phone"])
        if p:
            return p, "phone"
    if identity.get("email"):
        p = fx.policyholder_by_email(identity["email"])
        if p:
            return p, "email"
    return None, "not_found"


def match_record(identity: dict, record: dict) -> MatchResult:
    res = MatchResult()
    checks = {
        "full_name": lambda v: name_tokens(v) in [name_tokens(n) for n in [record["name"], *record.get("name_aliases", [])]],
        "dob": lambda v: norm_dob(v) == record["dob"],
        "phone": lambda v: norm_phone(v) is not None and norm_phone(v) in [norm_phone(x) for x in [record["phone"], *record.get("phone_aliases", [])]],
        "email": lambda v: norm_email(v) in [x.lower() for x in [record["email"], *record.get("email_aliases", [])]],
        "id_last4": lambda v: norm_last4(v) == record["id_last4"],
    }
    for f in PII_FIELDS:
        v = identity.get(f)
        if not v:
            continue
        res.provided.append(f)
        (res.matched if checks[f](v) else res.mismatched).append(f)
    return res


def mask_email(e: str | None) -> str | None:
    if not e or "@" not in e:
        return e
    user, dom = e.split("@", 1)
    return f"{user[0]}{'*' * max(3, len(user) - 1)}@{dom}"
