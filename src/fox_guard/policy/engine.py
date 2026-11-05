"""Lớp 4 policy (plan B6.1–B6.2): merge findings into one risk, then pick an action per station.

PII never drives blocking (it is masked by Lớp 3). Only injection-like signals, solicitation, links and
unknown placeholders count towards risk. Without the Lớp 5 classifier, "two independent signals" from
B6.1 cannot happen yet, so rule severity is used as is: structural/concealed rules are high, the rest
medium.
"""

from dataclasses import dataclass, field

from fox_guard.types import Finding

_RANK = {"low": 0, "medium": 1, "high": 2}


@dataclass
class PolicyTexts:
    refusal: str
    context_hidden: str
    output_safe: str
    solicitation: str


@dataclass
class Verdict:
    action: str
    text: str
    risk: str
    flags: list[str] = field(default_factory=list)


def merge_risk(findings: list[Finding]) -> str:
    risky = [f for f in findings if f.kind != "pii" or f.detector == "pii:unknown_placeholder"]
    return max((f.severity for f in risky), key=_RANK.__getitem__, default="low")


def decide(station: str, findings: list[Finding], text: str, pii_changed: bool, link_edited: bool,
           texts: PolicyTexts) -> Verdict:
    risk = merge_risk(findings)
    detectors = {f.detector for f in findings}
    if station == "input":
        if risk == "high":
            return Verdict("block", texts.refusal, risk)
        if risk == "medium":
            return Verdict("review", text, risk, ["harden_prompt", "session_flagged"])
    elif station == "context":
        if risk == "high":
            # Without sentence-level localisation (Lớp 5) the whole segment is withheld from the LLM.
            return Verdict("block", texts.context_hidden, risk, ["require_confirmation"])
        if risk == "medium":
            return Verdict("review", text, risk, ["require_confirmation"])
    else:  # output
        if "solicitation" in detectors:
            return Verdict("block", texts.solicitation, risk)
        if "link:exfil" in detectors:
            return Verdict("block", texts.output_safe, risk)
        if risk == "high" and not link_edited:
            return Verdict("block", texts.output_safe, risk)
        if link_edited:
            # External/look-alike links were removed in place; the rest of the answer is still useful.
            return Verdict("mask", text, risk)
        if risk == "medium":
            return Verdict("review", text, risk)
    return Verdict("mask" if pii_changed else "allow", text, risk)
