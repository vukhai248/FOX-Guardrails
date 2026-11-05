"""SDK contract with the real normalizer; no policy blocking in wave 1."""

from pathlib import Path
from time import perf_counter
from uuid import UUID

import pytest

from fox_guard import Decision, Finding, Guard, GuardContext


@pytest.mark.parametrize("station", ["input", "context", "output"])
def test_check_stations_allow_clean_text_and_return_measured_decisions(station):
    guard = Guard.from_config(Path(__file__).resolve().parents[1] / "fox-guard.yaml")
    context = GuardContext(session_id="synthetic-session", station=station)
    start = perf_counter()
    decision = getattr(guard, f"check_{station}")("Tie\u0302\u0301ng Vie\u0323\u0302t", context)
    elapsed_ms = (perf_counter() - start) * 1000
    assert isinstance(decision, Decision)
    assert decision.text == "Tiếng Việt"
    assert decision.action == "allow"
    assert decision.risk == "low"
    assert decision.findings == decision.reasons == decision.flags == []
    assert decision.degraded is False
    assert 0 < decision.latency_ms <= elapsed_ms
    assert UUID(hex=decision.decision_id).version == 4
    assert len(decision.decision_id) == 32


def test_guard_reports_maximum_signal_risk_without_blocking():
    tags = "".join(chr(0xE0000 + ord(char)) for char in "SYSTEM")
    context = GuardContext(session_id="synthetic-session", station="input")
    decision = Guard().check_input("a\u200bb" + tags, context)
    assert decision.action == "allow"
    assert decision.text == "ab"
    assert decision.risk == "high"
    assert all(isinstance(finding, Finding) for finding in decision.findings)
    assert len(decision.reasons) == len(decision.findings) >= 2
    assert all(reason for reason in decision.reasons)
    assert {finding.detector for finding in decision.findings} >= {"unicode:tags", "unicode:invisible"}
    assert all(finding.span is None or finding.span[1] <= len(decision.text) for finding in decision.findings)


def test_guard_applies_configured_normalization_limit(tmp_path):
    path = tmp_path / "guard.yaml"
    path.write_text("normalize:\n  max_chars: 4\n  decode_max_depth: 0\n", encoding="utf-8")
    decision = Guard.from_config(path).check_input(
        "abcdefgh", GuardContext(session_id="synthetic-session", station="input"),
    )
    assert decision.text == "abcd"
    assert any(finding.detector.endswith("oversize") for finding in decision.findings)


def test_log_normalization_and_restore_wave1_contract():
    guard = Guard()
    context = GuardContext(session_id="synthetic-session", station="output")
    assert guard.redact_for_log("a\u200bb", context) == "ab"
    assert guard.restore("<PHONE_1> a\u200bb", context) == "<PHONE_1> a\u200bb"


def test_decision_ids_are_unique_per_check():
    guard = Guard()
    context = GuardContext(session_id="synthetic-session", station="input")
    assert guard.check_input("", context).decision_id != guard.check_input("", context).decision_id
