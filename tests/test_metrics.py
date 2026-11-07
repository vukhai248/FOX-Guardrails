"""Phần C metrics: Wilson interval, P/R/F1, PII span matching."""

from eval.metrics import binary, overlap_ok, prf, span_prf, wilson


def test_wilson_known_values():
    low, high = wilson(0, 84)
    assert low == 0.0 and 0.043 < high < 0.045  # matches the C2 report (0–4.4%)
    low, high = wilson(50, 100)
    assert 0.40 < low < 0.41 and 0.59 < high < 0.60


def test_prf_and_binary():
    assert prf(8, 2, 2) == (0.8, 0.8, 0.8000000000000002) or abs(prf(8, 2, 2)[2] - 0.8) < 1e-9
    report = binary([True, True, False, False], [True, False, True, False])
    assert (report.tp, report.fp, report.recall, report.fpr) == (1, 1, 0.5, 0.5)
    assert report.f1_ci[0] <= report.f1 <= report.f1_ci[1]


def test_span_matching_needs_half_the_gold_characters():
    assert overlap_ok((0, 5), (0, 10))
    assert not overlap_ok((0, 4), (0, 10))
    cases = [{"gold": [("PHONE", 0, 10)], "pred": [("PHONE", 0, 10), ("EMAIL", 20, 30)]}]
    out = span_prf(cases, lambda a, b: a == b)
    assert out["PHONE"]["tp"] == 1 and out["EMAIL"]["fp"] == 1 and out["ALL"]["precision"] == 0.5
