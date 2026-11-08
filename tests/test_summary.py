"""C4 summary: every number in SUMMARY.md comes from the committed result files (eval/summary.py)."""

from eval import summary


def test_per_case_files_match_official_reports():
    assert summary.check_consistency() == []


def test_summary_md_is_up_to_date():
    assert summary.SUMMARY.read_text("utf-8") == summary.build_markdown(), (
        "SUMMARY.md lệch dữ liệu: chạy python -X utf8 -m eval.summary"
    )


def test_vietnamese_number_format():
    assert summary.pct(0.2159) == "21,6%"
    assert summary.num(0.95, 2) == "0,95"
    assert summary.pval(0.020074) == "p = 0,020"
    assert summary.pval(1e-9) == "p < 0,001"
    assert (
        summary.rate_cell({"n": 50, "k": 6, "rate": 0.12, "ci": [0.0562, 0.238]}) == "12,0% (6/50) [5,6–23,8]"
    )


def test_significance_wording_follows_p():
    assert summary.significant(0.02) == "khác biệt có ý nghĩa thống kê"
    assert summary.significant(0.38) == "khác biệt không có ý nghĩa thống kê"


def test_detector_pairs_use_identical_cases():
    for a, b in summary.DETECTOR_PAIRS:
        res = summary.paired(a, b, "bipia", ("attack",))
        assert res["n"] == 300
        assert res["a_only"] + res["b_only"] <= res["n"]


def test_hand_written_claims_still_hold():
    """Sentences in SUMMARY.md that are not f-strings rely on these facts; fail loudly if the data changes."""
    for arm in ("R", "R-noNorm"):  # "luật không bắt được BIPIA/JBB", "RQ2 với injection chưa đo được"
        d = summary.detector_arm(arm)
        assert d["bipia"]["overall"]["tp"] == 0 and d["jbb"]["overall"]["tp"] == 0
    for arm in ("M-deberta", "M-pg2"):  # "cả hai classifier đều yếu với BIPIA"
        assert summary.detector_arm(arm)["bipia"]["overall"]["recall"] < 0.2
    pg2 = summary.detector_arm("H-pg2")  # "JBB chặn nhầm của PG2 cao hơn mục tiêu 2%"
    assert pg2["jbb"]["overall"]["fpr"] > 0.02
