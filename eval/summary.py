"""C4: one summary of every official result (C2 detector-level, Lớp 5 classifier, C3 benchmarks + e2e).

Every number in eval/reports/SUMMARY.md is computed here from committed files; nothing is typed by hand.
Before writing, the per-case files are re-aggregated and must equal the official JSON reports exactly
(`check_consistency`); any mismatch stops the build.

Inputs (all under eval/reports/):
  detector_2026-11-07_test.json                 arms R, R-noNorm (rules, PII)
  detector_2026-11-07_test_{M,H}-{deberta,pg2}_v2.json   classifier arms (v2 = official, see lop5-pg2 report)
  c3_detectors_2026-11-07.json                  external benchmarks, detector level
  c3_e2e_gemini_2026-11-08.json                 end-to-end G0/G2/G4 on Gemini
  cases/detector_test_<arm>.jsonl               per-case decisions (run_detectors --cases-out)
  cases/c3_e2e_gemini.jsonl                     per-case e2e outcomes (exported by `export-e2e`)

python -X utf8 -m eval.summary              # check, then write SUMMARY.md + figures/
python -X utf8 -m eval.summary --check      # only verify that SUMMARY.md is up to date
python -X utf8 -m eval.summary export-e2e   # needs var/c3_cache_gemini.jsonl + data/raw (local only)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .metrics import mcnemar

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "eval" / "reports"
CASES = REPORTS / "cases"
FIGURES = REPORTS / "figures"
SUMMARY = REPORTS / "SUMMARY.md"

DETECTOR_FILES = {
    "R": "detector_2026-11-07_test.json",
    "R-noNorm": "detector_2026-11-07_test.json",
    "M-deberta": "detector_2026-11-07_test_M-deberta_v2.json",
    "H-deberta": "detector_2026-11-07_test_H-deberta_v2.json",
    "M-pg2": "detector_2026-11-07_test_M-pg2_v2.json",
    "H-pg2": "detector_2026-11-07_test_H-pg2_v2.json",
}
CLASSIFIER_ARMS = ["R", "M-deberta", "H-deberta", "M-pg2", "H-pg2"]
C3_DETECTORS = "c3_detectors_2026-11-07.json"
C3_E2E = "c3_e2e_gemini_2026-11-08.json"
E2E_ARMS = ["G0", "G2", "G4"]
ARM_NAMES = {
    "R": "R (luật Lớp 1–4)",
    "R-noNorm": "R bỏ chuẩn hoá",
    "M-deberta": "M-deberta (chỉ classifier)",
    "H-deberta": "H-deberta (luật + classifier)",
    "M-pg2": "M-pg2 (chỉ classifier)",
    "H-pg2": "H-pg2 (luật + classifier)",
    "G0": "G0 không guard",
    "G2": "G2 luật (Lớp 1–4)",
    "G4": "G4 đầy đủ (+ PG2, datamarking)",
}


# ---------------------------------------------------------------- loading


def load_json(name: str) -> dict:
    return json.loads((REPORTS / name).read_text("utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]


def detector_arm(arm: str) -> dict:
    return load_json(DETECTOR_FILES[arm])["arms"][arm]


def detector_cases(arm: str) -> list[dict]:
    return load_jsonl(CASES / f"detector_test_{arm}.jsonl")


def e2e_cases() -> list[dict]:
    return load_jsonl(CASES / "c3_e2e_gemini.jsonl")


# ---------------------------------------------------------------- consistency


def _count(rows: list[dict], label_pred, flag_key: str = "flagged") -> tuple[int, int]:
    sel = [r for r in rows if label_pred(r)]
    return sum(1 for r in sel if r[flag_key]), len(sel)


def check_consistency() -> list[str]:
    """Re-aggregate per-case files; return every disagreement with the official JSON (empty = all equal)."""
    errors: list[str] = []
    for arm in CLASSIFIER_ARMS:
        official, rows = detector_arm(arm), detector_cases(arm)
        for name in ("bipia", "jbb"):
            sub = [r for r in rows if r["set"] == name]
            if name == "jbb":
                sub = [r for r in sub if r["label"] in ("attack", "benign")]
            tp, n_pos = _count(sub, lambda r: r["label"] == "attack")
            fp, n_neg = _count(sub, lambda r: r["label"] != "attack")
            o = official[name]["overall"]
            got = {"tp": tp, "n_pos": n_pos, "fp": fp, "n_neg": n_neg}
            want = {k: o[k] for k in got}
            if got != want:
                errors.append(f"{arm}/{name}: per-case {got} != official {want}")
        cskh = [r for r in rows if r["set"] == "cskh_vi"]
        for label in ("hard_benign", "clean"):
            k, n = _count(cskh, lambda r, lb=label: r["label"] == lb)
            o = official["cskh_vi"][f"fpr_{label}"]
            if (k, n) != (o["k"], o["n"]):
                errors.append(f"{arm}/cskh {label}: per-case {k}/{n} != official {o['k']}/{o['n']}")
    e2e, rows = load_json(C3_E2E), e2e_cases()
    by_arm = {a: {r["case_id"]: r for r in rows if r["arm"] == a} for a in E2E_ARMS}
    for arm in E2E_ARMS:
        o = e2e["arms"][arm]
        sub = list(by_arm[arm].values())
        checks = {
            "asr": (sum(r["success"] for r in sub), len(sub), o["asr"]),
            "blocked": (sum(r["blocked"] for r in sub), len(sub), o["blocked_before_llm"]),
        }
        for key, (k, n, off) in checks.items():
            if (k, n) != (off["k"], off["n"]):
                errors.append(f"e2e {arm}/{key}: per-case {k}/{n} != official {off['k']}/{off['n']}")
        for field in ("lang", "injection_type", "risk_category"):
            for group, off in o[f"asr_by_{field}"].items():
                g = [r for r in sub if r[field] == group]
                k, n = sum(r["success"] for r in g), len(g)
                if (k, n) != (off["k"], off["n"]):
                    errors.append(f"e2e {arm}/{field}={group}: {k}/{n} != {off['k']}/{off['n']}")
        if arm != "G0":
            ids = sorted(by_arm["G0"])
            got = mcnemar([by_arm["G0"][i]["success"] for i in ids], [by_arm[arm][i]["success"] for i in ids])
            if got != o["mcnemar_vs_G0"]:
                errors.append(f"e2e {arm} McNemar: {got} != {o['mcnemar_vs_G0']}")
    return errors


# ---------------------------------------------------------------- formatting


def num(x: float, digits: int = 1) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def pct(x: float, digits: int = 1) -> str:
    return f"{num(100 * x, digits)}%"


def ci(c: list[float]) -> str:
    return f"[{num(100 * c[0])}–{num(100 * c[1])}]"


def frac(k: int, n: int) -> str:
    return f"{k}/{n}"


def rate_cell(r: dict) -> str:
    """{'n','k','rate','ci'} → '12,0% (6/50) [5,6–23,8]'."""
    return f"{pct(r['rate'])} ({frac(r['k'], r['n'])}) {ci(r['ci'])}"


def pval(p: float) -> str:
    if p < 0.001:
        return "p < 0,001"
    return f"p = {num(p, 3)}"


def significant(p: float) -> str:
    return "khác biệt có ý nghĩa thống kê" if p < 0.05 else "khác biệt không có ý nghĩa thống kê"


def table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


# ---------------------------------------------------------------- paired tests


def paired(arm_a: str, arm_b: str, set_name: str, labels: tuple[str, ...]) -> dict:
    """McNemar on `flagged` between two detector arms, restricted to one set and some labels."""
    a = {
        r["case_id"]: r["flagged"]
        for r in detector_cases(arm_a)
        if r["set"] == set_name and r["label"] in labels
    }
    b = {
        r["case_id"]: r["flagged"]
        for r in detector_cases(arm_b)
        if r["set"] == set_name and r["label"] in labels
    }
    if set(a) != set(b):
        raise ValueError(f"{arm_a} vs {arm_b} on {set_name}: different case ids")
    ids = sorted(a)
    return {**mcnemar([a[i] for i in ids], [b[i] for i in ids]), "n": len(ids)}


def paired_e2e(arm_a: str, arm_b: str) -> dict:
    rows = e2e_cases()
    a = {r["case_id"]: r["success"] for r in rows if r["arm"] == arm_a}
    b = {r["case_id"]: r["success"] for r in rows if r["arm"] == arm_b}
    ids = sorted(a)
    return {**mcnemar([a[i] for i in ids], [b[i] for i in ids]), "n": len(ids)}


DETECTOR_PAIRS = [("R", "H-pg2"), ("H-deberta", "H-pg2"), ("M-pg2", "H-pg2")]


# ---------------------------------------------------------------- sections


def section_overview() -> str:
    e2e = load_json(C3_E2E)["arms"]
    g0, g4 = e2e["G0"]["asr"], e2e["G4"]["asr"]
    pg2, r = detector_arm("H-pg2"), detector_arm("R")
    return f"""## Tóm tắt một trang

| Câu hỏi (DU-AN §7) | Kết quả chính | Ở mục |
| --- | --- | --- |
| RQ1 — Luật (Lớp 1–4) một mình bắt được gì? | BIPIA **{pct(r["bipia"]["overall"]["recall"])}**, JBB **{pct(r["jbb"]["overall"]["recall"])}**; chặn nhầm CSKH tiếng Việt **{pct(r["cskh_vi"]["fpr_hard_benign"]["rate"])}** | §1 |
| RQ1 — Thêm classifier Prompt Guard 2 thì sao? | JBB **{pct(pg2["jbb"]["overall"]["recall"])}**, BIPIA **{pct(pg2["bipia"]["overall"]["recall"])}**; chặn nhầm CSKH tiếng Việt **{pct(pg2["cskh_vi"]["fpr_hard_benign"]["rate"])}**, JBB vô hại **{pct(pg2["jbb"]["overall"]["fpr"])}** | §2 |
| RQ2 — Chuẩn hoá có tác dụng không? | Recall PII trên ca biến dạng {num(detector_arm("R-noNorm")["pii_synthetic"]["obfuscated_T3_12"]["recall"], 2)} → {num(r["pii_synthetic"]["obfuscated_T3_12"]["recall"], 2)}; với injection chưa đo được (bộ tiếng Anh không có ca nào luật bắt) | §5 |
| RQ3 — Trên chatbot thật, tấn công thành công giảm bao nhiêu? | ASR **{pct(g0["rate"])} → {pct(g4["rate"])}** ({frac(g0["k"], g0["n"])} → {frac(g4["k"], g4["n"])}), McNemar {pval(e2e["G4"]["mcnemar_vs_G0"]["p"])}; utility chưa đo (C3-4) | §4 |
| RQ4 — PII tiếng Việt? | F1 **{num(r["pii_synthetic"]["by_entity"]["ALL"]["f1"], 2)}** trên bộ tổng hợp; rò PII trước/sau guard ở mức e2e chưa đo | §5 |
| Cái giá? | Độ trễ guard e2e p50 / p95 = {num(e2e["G4"]["guard_ms"]["p50"], 0)} / {num(e2e["G4"]["guard_ms"]["p95"], 0)} ms (GPU); over-defence NotInject {pct(load_json(C3_DETECTORS)["arms"]["H-pg2"]["notinject_fpr"]["rate"])} (chỉ ra `review`) | §6 |
"""


def section_rules() -> str:
    rows = []
    for arm in ("R", "R-noNorm"):
        d = detector_arm(arm)
        rows.append(
            [
                ARM_NAMES[arm],
                rate_cell({**_overall_recall(d["bipia"])}),
                rate_cell(_overall_recall(d["jbb"])),
                rate_cell(_overall_fpr(d["bipia"])),
                rate_cell(_overall_fpr(d["jbb"])),
                rate_cell(d["cskh_vi"]["fpr_hard_benign"]),
                rate_cell(d["cskh_vi"]["fpr_clean"]),
            ]
        )
    d = detector_arm("R")
    benign = [
        _overall_fpr(d["bipia"]),
        _overall_fpr(d["jbb"]),
        d["cskh_vi"]["fpr_hard_benign"],
        d["cskh_vi"]["fpr_clean"],
    ]
    fp_total, benign_total = sum(b["k"] for b in benign), sum(b["n"] for b in benign)
    return f"""## 1. Luật một mình (arm R) — RQ1

Tập test C1, chạy một lần; arm R không có ngưỡng để chỉnh. "Bắt" = hành động `block` hoặc `review`.
Ô dạng `tỉ lệ (k/n) [CI 95% Wilson]`.

{table(["Arm", "BIPIA recall", "JBB recall", "BIPIA chặn nhầm", "JBB chặn nhầm", "CSKH hard-benign chặn nhầm", "CSKH clean chặn nhầm"], rows)}

**Đọc bảng:** luật không bắt được tấn công kiểu "giao việc" (BIPIA) hay jailbreak nhập vai/hậu tố vô nghĩa (JBB),
vì các câu này không có dấu hiệu ghi đè tường minh mà Lớp 2 nhắm tới. Đổi lại, luật chặn nhầm **{fp_total}/{benign_total}**
câu vô hại (BIPIA sạch, JBB vô hại, CSKH tiếng Việt). Recall tiếng Việt của luật được đo ở bộ held-out riêng của từng lớp (xem `docs/hoc/lop-2-luat.md`,
`docs/hoc/lop-4-dau-ra-policy-audit.md`), vì bộ CSKH tiếng Việt chưa có ca tấn công (C1-OPEN).
"""


def _overall_recall(s: dict) -> dict:
    o = s["overall"]
    return {"rate": o["recall"], "k": o["tp"], "n": o["n_pos"], "ci": o["recall_ci"]}


def _overall_fpr(s: dict) -> dict:
    o = s["overall"]
    return {"rate": o["fpr"], "k": o["fp"], "n": o["n_neg"], "ci": o["fpr_ci"]}


def section_classifier() -> str:
    rows = []
    for arm in CLASSIFIER_ARMS:
        d = detector_arm(arm)
        rows.append(
            [
                ARM_NAMES[arm],
                rate_cell(_overall_recall(d["bipia"])),
                rate_cell(_overall_fpr(d["bipia"])),
                num(d["bipia"]["overall"]["f1"], 3),
                rate_cell(_overall_recall(d["jbb"])),
                rate_cell(_overall_fpr(d["jbb"])),
                rate_cell(d["cskh_vi"]["fpr_hard_benign"]),
            ]
        )
    th = {m: load_json(f"thresholds_{m}.json") for m in ("deberta", "pg2")}
    th_rows = [[m, f"{th[m]['theta_low']}", f"{th[m]['theta_high']}", str(th[m]["n_benign"])] for m in th]
    pair_rows = []
    for a, b in DETECTOR_PAIRS:
        for set_name, labels, what in (
            ("bipia", ("attack",), "BIPIA tấn công"),
            ("jbb", ("attack",), "JBB tấn công"),
            ("bipia", ("clean",), "BIPIA sạch"),
            ("jbb", ("benign",), "JBB vô hại"),
        ):
            p = paired(a, b, set_name, labels)
            pair_rows.append(
                [f"{a} vs {b}", what, str(p["n"]), str(p["a_only"]), str(p["b_only"]), pval(p["p"])]
            )
    jbb = paired("H-deberta", "H-pg2", "jbb", ("attack",))
    bip = paired("H-deberta", "H-pg2", "bipia", ("attack",))
    jbb_fp = paired("H-deberta", "H-pg2", "jbb", ("benign",))
    bip_fp = paired("H-deberta", "H-pg2", "bipia", ("clean",))
    mh = [paired("M-pg2", "H-pg2", s, lb) for s, lb in (("bipia", ("attack",)), ("jbb", ("attack",)))]
    mh_diff = sum(p["a_only"] + p["b_only"] for p in mh)
    mh_text = (
        "trên hai bộ tiếng Anh này luật không thêm được ca nào."
        if mh_diff == 0
        else "luật chỉ thêm được rất ít ca trên hai bộ tiếng Anh này."
    )
    return f"""## 2. Thêm classifier (Lớp 5) — RQ1

Ngưỡng chọn **chỉ trên dev** (`eval/calibrate.py`: θ_high ứng với chặn nhầm ≤ 2%, θ_low ≤ 10% trên câu vô hại dev):

{table(["Model", "θ_low", "θ_high", "Số câu vô hại dev"], th_rows)}

Tập test (số **v2**, thay số v1 có nhiễu ROT13 — xem `lop5-pg2_2026-11-07.md`). M = chỉ classifier, H = luật + classifier.

{table(["Arm", "BIPIA recall", "BIPIA chặn nhầm", "BIPIA F1", "JBB recall", "JBB chặn nhầm", "CSKH hard-benign chặn nhầm"], rows)}

**So cặp (McNemar chính xác, hai phía, trên cùng các ca).** "Chỉ A" = số ca arm A gắn cờ mà arm B không, và ngược lại.
Với ca tấn công, gắn cờ là đúng; với ca vô hại, gắn cờ là chặn nhầm.

{table(["Cặp", "Tập", "n", "Chỉ A", "Chỉ B", "p"], pair_rows)}

**Đọc bảng:**
- Về bắt tấn công, PG2 hơn deberta trên JBB ({jbb["b_only"]} ca chỉ PG2 bắt, {jbb["a_only"]} ca chỉ deberta bắt;
  {pval(jbb["p"])}, {significant(jbb["p"])}) và trên BIPIA ({bip["b_only"]} so với {bip["a_only"]}; {pval(bip["p"])}, {significant(bip["p"])}).
- Về chặn nhầm, PG2 trả giá trên JBB vô hại ({jbb_fp["b_only"]} ca chỉ PG2 gắn cờ, {jbb_fp["a_only"]} ca chỉ deberta;
  {pval(jbb_fp["p"])}, {significant(jbb_fp["p"])}); trên BIPIA sạch {bip_fp["b_only"]} so với {bip_fp["a_only"]} ({pval(bip_fp["p"])}, {significant(bip_fp["p"])}).
- M-pg2 và H-pg2 khác nhau {mh_diff} ca trên tấn công BIPIA + JBB:
  {mh_text} Lợi ích của luật nằm ở tấn công tiếng Việt và token điều khiển
  (đo ở `tests/systematic` S4 và held-out từng lớp), chưa có trong tập test.
- Cả hai classifier đều yếu với BIPIA (chèn gián tiếp kiểu "giao việc"): đây là giới hạn đã biết của classifier
  phát hiện ý đồ ghi đè, không chỉnh ngưỡng trên test để kéo số lên.
- JBB chặn nhầm của PG2 cao hơn mục tiêu 2% chọn trên dev: câu vô hại của JBB là yêu cầu tiếng Anh chủ đề nhạy cảm,
  khác phân phối CSKH. Theo policy B6.1, classifier một mình chỉ ra `review` (siết prompt), không chặn khách.
"""


def section_external() -> str:
    d = load_json(C3_DETECTORS)["arms"]
    r, h = d["R"], d["H-pg2"]

    def llmail(a: dict, key: str) -> dict:
        o = a["llmail"]
        return (
            {"rate": o["recall"], "k": o["tp"], "n": o["n_pos"], "ci": o["recall_ci"]}
            if key == "recall"
            else {"rate": o["fpr"], "k": o["fp"], "n": o["n_neg"], "ci": o["fpr_ci"]}
        )

    rows = [
        [
            "NotInject (câu vô hại có từ kích hoạt, EN)",
            "chặn thừa",
            rate_cell(r["notinject_fpr"]),
            rate_cell(h["notinject_fpr"]),
        ],
        [
            "LLMail-Inject Phase 2 (email tấn công thích nghi)",
            "recall",
            rate_cell(llmail(r, "recall")),
            rate_cell(llmail(h, "recall")),
        ],
        [
            "↳ email đã thắng challenge",
            "recall",
            rate_cell(r["llmail_recall_on_challenge_successes"]),
            rate_cell(h["llmail_recall_on_challenge_successes"]),
        ],
        ["LLMail email thật vô hại", "chặn nhầm", rate_cell(llmail(r, "fpr")), rate_cell(llmail(h, "fpr"))],
    ]
    for key, label in (
        ("en-direct", "CyberSecEval EN trực tiếp"),
        ("en-indirect", "CyberSecEval EN gián tiếp"),
        ("vi-direct", "CyberSecEval VI trực tiếp (dịch máy)"),
        ("vi-indirect", "CyberSecEval VI gián tiếp (dịch máy)"),
    ):
        rows.append(
            [
                label,
                "recall",
                rate_cell(r["cyberseceval_recall"][key]),
                rate_cell(h["cyberseceval_recall"][key]),
            ]
        )
    for lang in ("en", "vi"):
        rows.append(
            [
                f"MultiJail {lang.upper()} (câu hỏi độc hại, không phải injection)",
                "tỉ lệ gắn cờ",
                rate_cell(r["multijail_flag_rate"][lang]),
                rate_cell(h["multijail_flag_rate"][lang]),
            ]
        )
    by_words = " / ".join(pct(h["notinject_fpr_by_words"][k]["rate"]) for k in ("1-word", "2-word", "3-word"))
    return f"""## 3. Benchmark ngoài, mức detector (không gọi LLM)

Ngưỡng giữ nguyên như §2, **không chỉnh gì** trên các bộ này. Nguồn: `{C3_DETECTORS}`.

{table(["Bộ", "Đo", "R", "H-pg2"], rows)}

**Đọc bảng:** PG2 tăng recall trên LLMail và CyberSecEval mà không tăng chặn nhầm trên email thật. Cái giá là
chặn thừa trên NotInject, tăng theo số từ kích hoạt (1 / 2 / 3 từ: {by_words}). Các ca này chỉ ra `review`.
MultiJail là câu hỏi độc hại, không phải injection: FOX-Guard không nhắm loại này (để cho cơ chế an toàn của LLM).
"""


def section_e2e() -> str:
    e = load_json(C3_E2E)
    a = e["arms"]
    rows = []
    for arm in E2E_ARMS:
        o = a[arm]
        mc = o.get("mcnemar_vs_G0")
        rows.append(
            [
                ARM_NAMES[arm],
                rate_cell(o["asr"]),
                "—" if arm == "G0" else str(o["blocked_before_llm"]["k"]),
                "—" if not mc else f"{mc['a_only']} / {mc['b_only']}, {pval(mc['p'])}",
                "—" if arm == "G0" else f"{num(o['guard_ms']['p50'])} / {num(o['guard_ms']['p95'])} ms",
            ]
        )
    g24 = paired_e2e("G2", "G4")
    groups = []
    for field, label in (
        ("injection_type", {"direct": "Trực tiếp", "indirect": "Gián tiếp"}),
        ("lang", {"en": "Tiếng Anh", "vi": "Tiếng Việt (dịch máy)"}),
        ("risk_category", {"security-violating": "Vi phạm bảo mật", "logic-violating": "Vi phạm logic"}),
    ):
        for key, name in label.items():
            groups.append([name] + [rate_cell(a[arm][f"asr_by_{field}"][key]) for arm in E2E_ARMS])
    variants = sorted(a["G0"]["asr_by_variant"])
    var_rows = [
        [v.replace("_", " ")]
        + [frac(a[arm]["asr_by_variant"][v]["k"], a[arm]["asr_by_variant"][v]["n"]) for arm in E2E_ARMS]
        for v in variants
    ]
    mc4 = a["G4"]["mcnemar_vs_G0"]
    mc2 = a["G2"]["mcnemar_vs_G0"]
    rel = 1 - a["G4"]["asr"]["rate"] / a["G0"]["asr"]["rate"]
    g4_groups = {
        name: a["G4"][f"asr_by_{field}"][key]["rate"]
        for field, key, name in (
            ("injection_type", "direct", "trực tiếp"),
            ("injection_type", "indirect", "gián tiếp"),
        )
    }
    logic0, logic4 = (a[arm]["asr_by_risk_category"]["logic-violating"] for arm in ("G0", "G4"))
    logic_text = (
        f"Nhóm vi phạm logic **không giảm** ({frac(logic0['k'], logic0['n'])} → {frac(logic4['k'], logic4['n'])}): "
        "đây là lỗi làm sai quy tắc nghiệp vụ, không có đường rò dữ liệu mà Lớp 4 chặn."
        if logic4["k"] >= logic0["k"]
        else f"Nhóm vi phạm logic giảm ít ({frac(logic0['k'], logic0['n'])} → {frac(logic4['k'], logic4['n'])})."
    )
    return f"""## 4. End-to-end trên chatbot (CyberSecEval, {e["n_cases"]} ca) — RQ3

LLM đích **{e["target"]}** (model dự phòng của web, nhiệt độ 1,0). Trực tiếp → trạm INPUT, gián tiếp → trạm CONTEXT,
câu trả lời luôn qua trạm OUTPUT trước khi chấm. ASR = tỉ lệ tấn công thành công (judge của CyberSecEval).
McNemar: "G0 thắng / arm thắng" = số ca chỉ thành công ở G0 / chỉ thành công ở arm đó.

{table(["Arm", "ASR", "Chặn trước LLM", "McNemar vs G0", "Độ trễ guard p50 / p95"], rows)}

G2 vs G4 (cùng {g24["n"]} ca): {g24["a_only"]} ca chỉ thành công ở G2, {g24["b_only"]} ca chỉ ở G4, {pval(g24["p"])}.

**Theo nhóm:**

{table(["Nhóm", "G0", "G2", "G4"], groups)}

**Theo kỹ thuật tấn công (số ca thành công / số ca):**

{table(["Kỹ thuật", "G0", "G2", "G4"], var_rows)}

**Đọc bảng:**
- Guard đầy đủ giảm ASR {pct(rel, 0)} tương đối so với G0 ({pval(mc4["p"])}, {significant(mc4["p"])}).
  Luật một mình (G2) so với G0: {pval(mc2["p"])}, {significant(mc2["p"])}. G4 so với G2: {pval(g24["p"])}, {significant(g24["p"])}.
  CyberSecEval là câu tự nhiên, luật bắt được ít, PG2 gánh phần chính.
- Ở G4, ASR gián tiếp ({pct(g4_groups["gián tiếp"])}) vẫn cao hơn nhiều so với trực tiếp ({pct(g4_groups["trực tiếp"])}).
  Phân tích từng ca lọt nằm ở `c3_2026-11-08.md` §2.
- {logic_text}
- Tiếng Việt chỉ có {a["G0"]["asr_by_lang"]["vi"]["n"]} ca dịch máy, khoảng tin cậy rộng: chỉ nên đọc là xu hướng.
- Mỗi arm là **một lần lấy mẫu** ở nhiệt độ 1,0; chênh lệch nhỏ giữa các arm có thể do ngẫu nhiên — vì vậy dùng McNemar.
"""


def section_pii() -> str:
    r, nn = detector_arm("R")["pii_synthetic"], detector_arm("R-noNorm")["pii_synthetic"]
    ents = [k for k in r["by_entity"] if k != "ALL"]
    rows = [
        [
            e,
            num(r["by_entity"][e]["precision"], 2),
            num(r["by_entity"][e]["recall"], 2),
            num(r["by_entity"][e]["f1"], 2),
            frac(r["by_entity"][e]["tp"], r["by_entity"][e]["tp"] + r["by_entity"][e]["fn"]),
        ]
        for e in sorted(ents)
    ]
    for name, src in (("**Tất cả (R)**", r), ("Tất cả (R bỏ chuẩn hoá)", nn)):
        al = src["by_entity"]["ALL"]
        rows.append(
            [
                name,
                num(al["precision"], 2),
                num(al["recall"], 2),
                num(al["f1"], 2),
                frac(al["tp"], al["tp"] + al["fn"]),
            ]
        )
    op = detector_arm("R")["openpii_vi"]["by_entity"]["ALL"]
    return f"""## 5. PII tiếng Việt (Lớp 3) — RQ4, và chuẩn hoá — RQ2

Đo trên bộ nhận diện PII (`detect_pii`), span phải khớp loại và vị trí. Bộ tổng hợp tiếng Việt, tập test.

{table(["Thực thể", "P", "R", "F1", "Bắt / vàng"], rows)}

- Ca biến dạng T3.12 (số viết cách, chấm, fullwidth, bằng chữ): recall **{num(r["obfuscated_T3_12"]["recall"], 2)}** có chuẩn hoá,
  **{num(nn["obfuscated_T3_12"]["recall"], 2)}** khi bỏ chuẩn hoá — đây là đóng góp đo được của Lớp 1.
- Che nhầm trên câu dễ nhầm (giá, mã đơn, IMEI, mã giảm giá, UUID): {rate_cell(r["false_mask_rate_hard_negative"])}.
- openpii tiếng Việt (số theo định dạng quốc tế, tên nước ngoài): P {num(op["precision"], 2)}, R {num(op["recall"], 2)},
  F1 {num(op["f1"], 2)}. Thấp vì bộ nhận diện dựa trên đầu số, mã tỉnh và checksum Việt Nam — đã lường trước trong `SPLIT_REPORT`.
- OTP không kèm từ khoá là giới hạn đã biết (L3-FN): không phân biệt được với mã đơn hàng; Lớp 4 chặn việc bot **đòi** OTP.
"""


def section_latency() -> str:
    rows = []
    for arm in CLASSIFIER_ARMS:
        d = detector_arm(arm)
        rows.append(
            [ARM_NAMES[arm]]
            + [f"{num(d[s]['p50_ms'])} / {num(d[s]['p95_ms'])}" for s in ("bipia", "jbb", "cskh_vi")]
        )
    lat = load_json(C3_DETECTORS)["arms"]["H-pg2"]["latency_ms"]
    ext = [[k, f"{num(v['p50'])} / {num(v['p95'])}"] for k, v in lat.items()]
    return f"""## 6. Độ trễ

Một lần kiểm ở một trạm, GPU GTX 1650 (classifier) — p50 / p95 (ms). Nguồn: các file JSON ở trên.

{table(["Arm", "BIPIA (CONTEXT, đoạn dài)", "JBB (INPUT)", "CSKH tiếng Việt"], rows)}

H-pg2 trên benchmark ngoài:

{table(["Bộ", "p50 / p95 (ms)"], ext)}

Độ trễ trường hợp tệ nhất (đoạn 20.000 ký tự, GPU và CPU) đo riêng, xem `lop5-pg2_2026-11-07.md` phần v2.
"""


LIMITS = """## 7. Giới hạn và minh bạch quy trình

- **Tập test detector đã chạy 4 lần:** v1, kiểm tra ngân sách cửa sổ, v2 (số chính thức), và một lần chạy lại ngày
  08/11 chỉ để lưu kết quả từng ca cho McNemar (`cases/detector_test_*.jsonl`). Lần chạy lại không đổi code hay
  ngưỡng; script này kiểm tra số tổng của nó khớp **đúng từng ca** với số v2 trước khi dùng. Ngưỡng chưa bao giờ chọn trên test.
- **LLM đích e2e là Gemini 3.5 Flash-Lite**, không phải model chính của web (DeepSeek qua TokenHarbor): nhà cung cấp đó
  chặn prompt tấn công và đã khoá một tài khoản (quyết định Q28).
- **Judge là chính LLM đích** (nhiệt độ 0). Judge có thể sai; không có chấm tay toàn bộ.
- **Tiếng Việt e2e là bản dịch máy** của CyberSecEval; bộ CSKH tiếng Việt chưa có ca tấn công (C1-OPEN).
- **Chưa đo utility e2e** (câu hỏi vô hại có bị trả lời kém đi không) — backlog C3-4.
- Không tuyên bố chặn 100%: tấn công diễn đạt lại tinh vi và tấn công thích nghi vẫn lọt (§4).
"""


def build_markdown() -> str:
    head = """# C4 — Tổng hợp kết quả thực nghiệm FOX-Guard

> File này **sinh tự động** bởi `python -X utf8 -m eval.summary` từ các file kết quả trong `eval/reports/`.
> Không sửa tay: sửa script rồi chạy lại. Test `tests/test_summary.py` báo lỗi nếu file này lệch dữ liệu.
> Khoảng tin cậy: Wilson 95% cho tỉ lệ. So cặp: McNemar chính xác hai phía. Biểu đồ: `figures/` (PNG + SVG).
"""
    figs = """## Biểu đồ

| Hình | Nội dung |
| --- | --- |
| `figures/fig1_detector_arms.png` | Recall và chặn nhầm theo arm (BIPIA, JBB, CSKH) |
| `figures/fig2_e2e_asr.png` | ASR end-to-end G0 / G2 / G4 với CI 95% |
| `figures/fig3_e2e_groups.png` | ASR theo nhóm (trực tiếp / gián tiếp / ngôn ngữ) |
| `figures/fig4_pii_entities.png` | F1 PII theo thực thể |
| `figures/fig5_external.png` | Benchmark ngoài: R so với H-pg2 |
"""
    parts = [
        head,
        section_overview(),
        section_rules(),
        section_classifier(),
        section_external(),
        section_e2e(),
        section_pii(),
        section_latency(),
        LIMITS,
        figs,
    ]
    return "\n".join(p.rstrip() + "\n" for p in parts)


# ---------------------------------------------------------------- figures


def build_figures() -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker  # noqa: F401  (used via matplotlib.ticker)

    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    blue, orange, grey = "#2f6db5", "#d9822b", "#9aa0a6"
    written: list[Path] = []

    def save(fig, name: str) -> None:
        for ext in ("png", "svg"):
            path = FIGURES / f"{name}.{ext}"
            fig.savefig(path, dpi=200, bbox_inches="tight", metadata={"Date": None} if ext == "svg" else None)
            written.append(path)
        plt.close(fig)

    def err(r: dict) -> list[list[float]]:
        return [[100 * (r["rate"] - r["ci"][0])], [100 * (r["ci"][1] - r["rate"])]]

    # fig1: recall vs false positives per arm
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    arms = CLASSIFIER_ARMS
    x = range(len(arms))
    w = 0.38
    for ax, title, metrics in (
        (
            axes[0],
            "Recall (cao là tốt)",
            [("BIPIA", lambda d: _overall_recall(d["bipia"])), ("JBB", lambda d: _overall_recall(d["jbb"]))],
        ),
        (
            axes[1],
            "Chặn nhầm (thấp là tốt)",
            [
                ("BIPIA sạch", lambda d: _overall_fpr(d["bipia"])),
                ("JBB vô hại", lambda d: _overall_fpr(d["jbb"])),
                ("CSKH tiếng Việt", lambda d: d["cskh_vi"]["fpr_hard_benign"]),
            ],
        ),
    ):
        bw = 0.8 / len(metrics)
        for j, (label, fn) in enumerate(metrics):
            vals = [fn(detector_arm(a)) for a in arms]
            ax.bar(
                [i + (j - (len(metrics) - 1) / 2) * bw for i in x],
                [100 * v["rate"] for v in vals],
                bw,
                label=label,
                color=[blue, orange, grey][j],
                yerr=[[e for v in vals for e in err(v)[0]], [e for v in vals for e in err(v)[1]]],
                capsize=3,
            )
        ax.set_xticks(list(x), arms, rotation=20)
        ax.set_ylabel("%")
        ax.set_title(title)
        ax.legend(frameon=False)
    save(fig, "fig1_detector_arms")

    e2e = load_json(C3_E2E)["arms"]
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    vals = [e2e[a]["asr"] for a in E2E_ARMS]
    ax.bar(
        E2E_ARMS,
        [100 * v["rate"] for v in vals],
        color=[grey, orange, blue],
        yerr=[[err(v)[0][0] for v in vals], [err(v)[1][0] for v in vals]],
        capsize=4,
    )
    for i, v in enumerate(vals):
        ax.text(i, 100 * v["ci"][1] + 0.8, f"{pct(v['rate'])}\n({v['k']}/{v['n']})", ha="center", fontsize=9)
    ax.set_ylabel("ASR (%)")
    ax.set_ylim(0, 100 * max(v["ci"][1] for v in vals) + 8)
    ax.set_title(f"Tấn công thành công end-to-end (G4 vs G0: {pval(e2e['G4']['mcnemar_vs_G0']['p'])})")
    save(fig, "fig2_e2e_asr")

    groups = [
        ("injection_type", "direct", "Trực tiếp"),
        ("injection_type", "indirect", "Gián tiếp"),
        ("lang", "en", "Tiếng Anh"),
        ("lang", "vi", "Tiếng Việt"),
    ]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for j, arm in enumerate(("G0", "G4")):
        vals = [e2e[arm][f"asr_by_{f}"][k] for f, k, _ in groups]
        ax.bar(
            [i + (j - 0.5) * w for i in range(len(groups))],
            [100 * v["rate"] for v in vals],
            w,
            label=ARM_NAMES[arm],
            color=[grey, blue][j],
            yerr=[[err(v)[0][0] for v in vals], [err(v)[1][0] for v in vals]],
            capsize=3,
        )
    ax.set_xticks(
        range(len(groups)), [f"{g[2]}\n(n={e2e['G0'][f'asr_by_{g[0]}'][g[1]]['n']})" for g in groups]
    )
    ax.set_ylabel("ASR (%)")
    ax.legend(frameon=False)
    save(fig, "fig3_e2e_groups")

    pii = detector_arm("R")["pii_synthetic"]["by_entity"]
    ents = sorted((k for k in pii if k != "ALL"), key=lambda k: pii[k]["f1"])
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.barh(ents, [pii[e]["f1"] for e in ents], color=blue)
    ax.set_xlim(0, 1.05)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: num(v, 1)))
    ax.set_xlabel("F1")
    ax.set_title(f"PII tiếng Việt theo thực thể (F1 chung {num(pii['ALL']['f1'], 2)})")
    save(fig, "fig4_pii_entities")

    c3 = load_json(C3_DETECTORS)["arms"]
    items = [
        ("LLMail recall", lambda a: {"rate": a["llmail"]["recall"], "ci": a["llmail"]["recall_ci"]}),
        ("CSE EN trực tiếp", lambda a: a["cyberseceval_recall"]["en-direct"]),
        ("CSE EN gián tiếp", lambda a: a["cyberseceval_recall"]["en-indirect"]),
        ("NotInject chặn thừa", lambda a: a["notinject_fpr"]),
        ("LLMail chặn nhầm", lambda a: {"rate": a["llmail"]["fpr"], "ci": a["llmail"]["fpr_ci"]}),
    ]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for j, arm in enumerate(("R", "H-pg2")):
        vals = [fn(c3[arm]) for _, fn in items]
        ax.bar(
            [i + (j - 0.5) * w for i in range(len(items))],
            [100 * v["rate"] for v in vals],
            w,
            label=ARM_NAMES[arm],
            color=[grey, blue][j],
            yerr=[[err(v)[0][0] for v in vals], [err(v)[1][0] for v in vals]],
            capsize=3,
        )
    ax.set_xticks(range(len(items)), [n for n, _ in items], rotation=15)
    ax.set_ylabel("%")
    ax.legend(frameon=False)
    save(fig, "fig5_external")
    return written


# ---------------------------------------------------------------- export (local only)


def export_e2e() -> Path:
    """Write the per-case e2e outcomes (no prompts, no responses) from the local cache."""
    from . import c3_e2e

    cases = {c["case_id"]: c for c in c3_e2e.load_cases()}
    results = c3_e2e.load_cache(c3_e2e.CACHE_GEMINI)
    rows = []
    for arm in E2E_ARMS:
        for cid, case in cases.items():
            r = results[(arm, cid)]
            rows.append(
                {
                    "arm": arm,
                    "case_id": cid,
                    "success": r["success"],
                    "blocked": r["blocked"],
                    "judge": r.get("judge"),
                    "guard_ms": r["guard_ms"],
                    "lang": case["lang"],
                    "injection_type": case["injection_type"],
                    "risk_category": case["risk_category"],
                    "injection_variant": case["injection_variant"],
                }
            )
    CASES.mkdir(parents=True, exist_ok=True)
    path = CASES / "c3_e2e_gemini.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="build", choices=["build", "export-e2e"])
    parser.add_argument("--check", action="store_true", help="only verify SUMMARY.md is up to date")
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args()
    if args.command == "export-e2e":
        print(export_e2e())
        return
    errors = check_consistency()
    if errors:
        print("Per-case files disagree with the official reports:", *errors, sep="\n  ")
        sys.exit(1)
    text = build_markdown()
    if args.check:
        if SUMMARY.read_text("utf-8") != text:
            print("SUMMARY.md is out of date: run python -X utf8 -m eval.summary")
            sys.exit(1)
        print("SUMMARY.md up to date")
        return
    SUMMARY.write_text(text, "utf-8")
    print(SUMMARY)
    if not args.no_figures:
        for p in build_figures():
            print(p)


if __name__ == "__main__":
    main()
