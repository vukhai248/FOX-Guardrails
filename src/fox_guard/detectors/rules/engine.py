"""Lớp 2: YAML prompt-injection rules evaluated on Lớp 1 views (no I/O at check time)."""

import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

import regex
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from fox_guard.normalize import NormalizedText, normalize
from fox_guard.normalize.unicode import load_confusables
from fox_guard.normalize.vietnamese import no_diacritics
from fox_guard.types import Finding

PACKS = Path(__file__).resolve().parent / "packs"
View = Literal["clean", "nfkc", "vi_nodiac", "vi_teencode", "latin"]
Station = Literal["input", "context", "output"]
# Per-search guard against pathological backtracking; a timed-out rule is skipped, never fatal.
_TIMEOUT_S = 0.05
_LATIN = regex.compile(r"\p{Script=Latin}|\P{L}")


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z]+\.[a-z_]+\.\d{2}$")
    group: int = Field(ge=1, le=8)
    technique: str = Field(pattern=r"^T\d\.\d{1,2}$")
    stations: list[Station] = Field(min_length=1)
    views: list[View] = Field(min_length=1)
    severity: Literal["medium", "high"]
    reason: str = Field(min_length=1)
    pattern: str
    examples_pos: list[str] = Field(min_length=2)
    examples_neg: list[str] = Field(min_length=2)

    @field_validator("pattern")
    @classmethod
    def compiles(cls, value: str) -> str:
        try:
            regex.compile(value)
        except regex.error as error:
            raise ValueError(f"invalid pattern: {error}") from error
        return value


@dataclass(frozen=True)
class CompiledRule:
    rule: Rule
    compiled: regex.Pattern


def latin_view(nfkc: str) -> str:
    """Fold only non-Latin look-alike letters to Latin, then drop diacritics and lowercase.

    Unlike the UTS #39 skeleton, real Latin letters are never rewritten (no "m" -> "rn"),
    so rule patterns can be written as ordinary words.
    """
    table = load_confusables()
    out = []
    for ch in nfkc:
        if _LATIN.fullmatch(ch):
            out.append(ch)
            continue
        target = table.get(ord(ch))
        out.append(target if target and target.isascii() and target.isalpha() else ch)
    return no_diacritics(unicodedata.normalize("NFC", "".join(out))).lower()


@lru_cache(maxsize=4)
def load_rules(packs_dir: str = str(PACKS)) -> tuple[CompiledRule, ...]:
    """Load every *.yaml pack once; duplicate ids or invalid rules fail loudly."""
    compiled = []
    seen = set()
    for path in sorted(Path(packs_dir).glob("*.yaml")):
        entries = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(entries, list):
            raise ValueError(f"{path.name} must contain a YAML list of rules")
        for entry in entries:
            rule = Rule.model_validate(entry)
            if rule.id in seen:
                raise ValueError(f"Duplicate rule id {rule.id}")
            seen.add(rule.id)
            compiled.append(CompiledRule(rule, regex.compile(rule.pattern, regex.IGNORECASE)))
    return tuple(compiled)


def rule_reasons(rules: tuple[CompiledRule, ...] | None = None) -> dict[str, str]:
    reasons = {f"rules:{c.rule.id}": c.rule.reason for c in (rules or load_rules())}
    reasons["rules:timeout"] = "Một số luật chạy quá thời gian nên chưa kiểm hết văn bản; cần xem lại."
    return reasons


def _node_views(node: NormalizedText) -> dict[str, str]:
    return {"clean": node.clean, "nfkc": node.nfkc, "vi_nodiac": node.vi_nodiac,
            "vi_teencode": node.vi_teencode, "latin": latin_view(node.nfkc)}


def _mask_evidence(text: str) -> str:
    # Rules never need digits as evidence; masking them keeps accidental PII out of audit.
    return regex.sub(r"\d", "*", " ".join(text.split()))[:120]


def run_rules(normalized: NormalizedText, station: Station,
              rules: tuple[CompiledRule, ...] | None = None) -> list[Finding]:
    """One finding per matching rule.

    Hidden text (decoded Unicode Tags) and decoded views are searched first: a match there
    means the instruction was deliberately concealed, so severity is raised to high.
    Spans are given only when the matched view is index-aligned with clean.
    """
    rules = rules if rules is not None else load_rules()
    concealed = [child for child in normalized.decoded]
    if normalized.hidden_tags:
        concealed.insert(0, normalize(normalized.hidden_tags, decode_max_depth=0))
    nodes = [(child, True) for child in concealed] + [(normalized, False)]
    views = [(node, hidden, _node_views(node)) for node, hidden in nodes]
    findings = []
    timed_out = []
    for item in rules:
        rule = item.rule
        if station not in rule.stations:
            continue
        for node, hidden, texts in views:
            match, view = None, None
            for view in rule.views:
                try:
                    match = item.compiled.search(texts[view], timeout=_TIMEOUT_S)
                except TimeoutError:
                    # Never skip silently: an attacker could craft text that stalls a rule.
                    timed_out.append(rule.id)
                    match = None
                if match:
                    break
            if not match:
                continue
            aligned = not hidden and len(texts[view]) == len(node.clean)
            findings.append(Finding(
                detector=f"rules:{rule.id}", kind="injection",
                severity="high" if hidden else rule.severity,
                span=match.span() if aligned else None,
                evidence=_mask_evidence(match.group()), technique=rule.technique,
            ))
            break
    if timed_out:
        findings.append(Finding(
            detector="rules:timeout", kind="injection", severity="medium",
            evidence=f"Rule search timed out: {', '.join(sorted(set(timed_out)))}"[:120],
        ))
    return findings
