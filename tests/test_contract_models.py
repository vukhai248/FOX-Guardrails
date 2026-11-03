"""B1 contracts: validation, JSON compatibility, independent mutable defaults."""

import pytest
from pydantic import ValidationError

from fox_guard.types import Decision, Finding, GuardContext


def test_context_json_roundtrip_preserves_all_fields():
    context = GuardContext(
        session_id="synthetic-session", user_ref="synthetic-user", station="context",
        source="review", intent="product_qa", lang="vi", arm="FOX",
    )
    assert GuardContext.model_validate_json(context.model_dump_json()) == context


def test_finding_json_roundtrip_preserves_span():
    finding = Finding(
        detector="unicode:invisible", kind="unicode", severity="medium", score=0.8,
        span=(0, 2), evidence="2 ký tự vô hình", technique="T3.1",
    )
    assert Finding.model_validate_json(finding.model_dump_json()) == finding


def test_decision_json_roundtrip_preserves_nested_findings():
    decision = Decision(
        decision_id="synthetic-decision", action="allow", text="Xin chào", risk="low",
        findings=[Finding(detector="unicode:test", kind="unicode", severity="low", evidence="test")],
        reasons=["Ví dụ tổng hợp"], latency_ms=1.5, degraded=True, flags=["harden_prompt"],
    )
    assert Decision.model_validate_json(decision.model_dump_json()) == decision


@pytest.mark.parametrize("span", [(-1, 0), (3, 2)])
def test_finding_rejects_invalid_clean_coordinates(span):
    with pytest.raises(ValidationError, match="span"):
        Finding(detector="test", kind="unicode", severity="low", span=span, evidence="test")


def test_finding_enforces_evidence_limit_and_accepts_boundaries():
    with pytest.raises(ValidationError, match="evidence"):
        Finding(detector="test", kind="unicode", severity="low", evidence="x" * 121)
    finding = Finding(detector="test", kind="unicode", severity="low", span=(0, 0), evidence="x" * 120)
    assert len(finding.evidence) == 120
    assert finding.span == (0, 0)


def test_decision_list_defaults_are_independent():
    values = dict(decision_id="synthetic", action="allow", text="", risk="low", latency_ms=0.0)
    first, second = Decision(**values), Decision(**values)
    first.findings.append(Finding(detector="test", kind="unicode", severity="low", evidence="test"))
    first.reasons.append("test")
    first.flags.append("test")
    assert second.findings == second.reasons == second.flags == []
