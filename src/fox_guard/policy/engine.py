"""Lớp 4 policy (plan B6.1–B6.2): merge findings into one risk, then pick an action per station.

PII never drives blocking (it is masked by Lớp 3). Only injection-like signals, solicitation, links and
unknown placeholders count towards risk. Rule severity is used as is (structural/concealed rules are
high, the rest medium); with the Lớp 5 classifier on, a medium rule plus a classifier score >= theta_low
becomes high, and the classifier alone never exceeds medium (see merge_risk).
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
    """Highest severity, plus the B6.1 combination (docs/DU-AN.md §4.4.3):

    a medium rule AND a classifier score >= theta_low (any classifier finding) → high.
    A classifier finding alone stays at its own level (medium at most): it never blocks alone."""
    risky = [f for f in findings if f.kind != "pii" or f.detector == "pii:unknown_placeholder"]
    risk = max((f.severity for f in risky), key=_RANK.__getitem__, default="low")
    rule_medium = any(f.detector.startswith("rules:") and f.severity == "medium" for f in risky)
    classifier_hit = any(f.detector.startswith("classifier:") for f in risky)
    if rule_medium and classifier_hit:
        return "high"
    return risk


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
        # A removed link excuses only link findings (look-alike hosts are high but already removed).
        # Any other high finding still blocks, with or without a link (systematic run 1, S4c).
        if any(f.severity == "high" and not f.detector.startswith("link:") and
               (f.kind != "pii" or f.detector == "pii:unknown_placeholder") for f in findings):
            return Verdict("block", texts.output_safe, risk)
        if link_edited:
            # External/look-alike links were removed in place; the rest of the answer is still useful.
            return Verdict("mask", text, risk)
        if risk == "medium":
            return Verdict("review", text, risk)
    return Verdict("mask" if pii_changed else "allow", text, risk)
