"""Detector-level evaluation (Phần C2): FOX-Guard on the C1 datasets, offline, no LLM calls.

Arms available before Lớp 5:
  R         Lớp 1–4: normalization + rules + PII + solicitation + link guard + policy (no classifier)
  R-noNorm  same, but the normalizer is replaced by raw text in every view (ablation for RQ2)

A case is "flagged" when the guard's action is `block` or `review` (for INPUT/CONTEXT: what reaches
the LLM is refused or hardened). PII is measured on the recognizer itself (`detect_pii`).

python -X utf8 -m eval.run_detectors --split dev|test [--arm R|R-noNorm|all]
"""

import argparse
import hashlib
import json
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

from fox_guard import Guard, GuardContext
from fox_guard.config import GuardConfig
from fox_guard.normalize import normalize
from fox_guard.normalize.views import NormalizedText
from fox_guard.pii.recognizers import detect_pii

from .metrics import binary, percentile, rate, span_prf

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "eval" / "reports"
CONFIG = {"links": {"allowlist": ["shop.example"]}}


def raw_view(text: str) -> NormalizedText:
    """Every view = the raw text; no decoding, no hidden-character handling (arm R-noNorm)."""
    return NormalizedText(raw=text, sha256=hashlib.sha256(text.encode()).hexdigest(), base=text, clean=text,
                          nfkc=text, skeleton=text, vi_nodiac=text, vi_teencode=text, digits=text,
                          digits_map=list(range(len(text))), hidden_tags="", decoded=[], signals=[],
                          _digits_ends=list(range(1, len(text) + 1)))


class NoNormGuard(Guard):
    def _normalize(self, text: str) -> NormalizedText:  # noqa: D401 - ablation hook
        return raw_view(text[: self.config.normalize.max_chars])


def make_guard(arm: str) -> Guard:
    config = GuardConfig.model_validate(CONFIG)
    return NoNormGuard(config) if arm == "R-noNorm" else Guard(config)


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]


def run_cases(guard: Guard, cases: list[dict], station_of, text_of) -> list[dict]:
    out = []
    for i, case in enumerate(cases):
        station = station_of(case)
        ctx = GuardContext(session_id=f"bench-{i}", user_ref="bench-user", station=station)
        started = time.perf_counter()
        decision = getattr(guard, f"check_{station}")(text_of(case), ctx)
        out.append({**case, "flagged": decision.action in ("block", "review"), "action": decision.action,
                    "ms": (time.perf_counter() - started) * 1000,
                    "detectors": sorted({f.detector for f in decision.findings})})
    return out


def latency(results: list[dict]) -> dict:
    ms = [r["ms"] for r in results]
    return {"p50_ms": round(percentile(ms, 0.5), 2), "p95_ms": round(percentile(ms, 0.95), 2)}


def eval_bipia(guard: Guard, split: str) -> dict:
    results = run_cases(guard, read(ROOT / "data/processed/bipia" / f"{split}.jsonl"),
                        lambda c: "context", lambda c: c["text"])
    report = {"overall": binary([r["label"] == "attack" for r in results], [r["flagged"] for r in results]).as_dict(),
              **latency(results)}
    for key in ("position", "task", "attack_category"):
        groups = defaultdict(list)
        for r in results:
            if r["label"] == "attack":
                groups[r[key]].append(r["flagged"])
        report[f"recall_by_{key}"] = {k: rate(v) for k, v in sorted(groups.items())}
    return report


def eval_jbb(guard: Guard) -> dict:
    results = run_cases(guard, read(ROOT / "data/processed/jbb/test.jsonl"), lambda c: "input", lambda c: c["text"])
    main = [r for r in results if r["label"] in ("attack", "benign")]
    report = {"overall": binary([r["label"] == "attack" for r in main], [r["flagged"] for r in main]).as_dict(),
              "recall_jailbroken_only": rate([r["flagged"] for r in results if r["label"] == "attack" and r["jailbroken"]]),
              "flag_rate_harmful_bare": rate([r["flagged"] for r in results if r["label"] == "harmful_bare"]),
              **latency(results)}
    groups = defaultdict(list)
    for r in results:
        if r["label"] == "attack":
            groups[f"{r['method']}/{r['target_model']}"].append(r["flagged"])
    report["recall_by_method"] = {k: rate(v) for k, v in sorted(groups.items())}
    return report


def eval_cskh(guard: Guard, split: str) -> dict:
    cases = [c for c in read(ROOT / "eval/datasets/vi_cskh/cases.jsonl") if c["split"] == split]
    results = run_cases(guard, cases, lambda c: "input" if c["source"] == "chat" else "context",
                        lambda c: c["user_query"] if c["source"] == "chat" else c["carrier_text"])
    report = {**latency(results)}
    for label in ("hard_benign", "clean", "attack"):
        subset = [r for r in results if r["label"] == label]
        if not subset:
            continue
        key = "recall" if label == "attack" else f"fpr_{label}"
        report[key] = rate([r["flagged"] for r in subset])
        by_source = defaultdict(list)
        for r in subset:
            by_source[r["source"]].append(r["flagged"])
        report[f"{key}_by_source"] = {k: rate(v) for k, v in sorted(by_source.items())}
    report["false_positive_examples"] = [{"case_id": r["case_id"], "detectors": r["detectors"]}
                                         for r in results if r["label"] != "attack" and r["flagged"]][:15]
    return report


# FOX entity → canonical group used by both PII sets.
FOX_GROUP = {"VN_PHONE": "PHONE", "EMAIL": "EMAIL", "VN_CCCD": "CCCD", "VN_CMND": "CMND", "CREDIT_CARD": "CARD",
             "VN_BANK_ACCOUNT": "BANK_ACCOUNT", "VN_TAX_ID": "TAX_ID", "VN_PASSPORT": "PASSPORT",
             "VN_LICENSE_PLATE": "PLATE", "VN_HEALTH_INSURANCE": "BHYT", "OTP": "OTP", "PASSWORD": "PASSWORD",
             "PERSON": "PERSON", "VN_ADDRESS": "ADDRESS"}
OPENPII_GROUP = {"PERSON": "PERSON", "VN_ADDRESS": "ADDRESS", "VN_ID": "ID", "VN_PHONE": "PHONE", "EMAIL": "EMAIL",
                 "CREDIT_CARD": "CARD", "VN_TAX_ID": "TAX_ID", "VN_PASSPORT": "PASSPORT"}


def pii_predictions(text: str, arm: str, id_group: bool) -> list[tuple[str, int, int]]:
    normalized = raw_view(text) if arm == "R-noNorm" else normalize(text)
    preds = []
    for m in detect_pii(normalized):
        group = FOX_GROUP[m.entity]
        if id_group and group in ("CCCD", "CMND"):
            group = "ID"
        preds.append((group, m.start, m.end))
    return preds


def eval_pii(arm: str, split: str) -> dict:
    cases = [c for c in read(ROOT / "eval/datasets/pii/cases.jsonl") if c["split"] == split]
    scored, negatives, ms = [], [], []
    for c in cases:
        started = time.perf_counter()
        pred = pii_predictions(c["text"], arm, id_group=False)
        ms.append((time.perf_counter() - started) * 1000)
        if c["label"] == "hard_negative":
            negatives.append(bool(pred))
            continue
        scored.append({"gold": [(s["entity"], s["start"], s["end"]) for s in c["spans"]], "pred": pred,
                       "obfuscated": bool(c.get("obfuscation"))})
    report = {"by_entity": span_prf(scored, lambda a, b: a == b),
              "obfuscated_T3_12": span_prf([s for s in scored if s["obfuscated"]], lambda a, b: a == b)["ALL"],
              "false_mask_rate_hard_negative": rate(negatives),
              "p50_ms": round(percentile(ms, 0.5), 2), "p95_ms": round(percentile(ms, 0.95), 2)}
    return report


def eval_openpii(arm: str) -> dict:
    path = ROOT / "data/processed/openpii/test.jsonl"
    if not path.exists():
        return {"skipped": "data/processed/openpii/test.jsonl missing"}
    scored = []
    for c in read(path):
        scored.append({"gold": [(OPENPII_GROUP[s["entity"]], s["start"], s["end"]) for s in c["spans"]],
                       "pred": [p for p in pii_predictions(c["text"], arm, id_group=True)
                                if p[0] in set(OPENPII_GROUP.values())]})
    return {"by_entity": span_prf(scored, lambda a, b: a == b), "note": "only entity types openpii also labels"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "test"], required=True)
    parser.add_argument("--arm", default="all", choices=["R", "R-noNorm", "all"])
    args = parser.parse_args()
    arms = ["R", "R-noNorm"] if args.arm == "all" else [args.arm]
    out = {"date": date.today().isoformat(), "split": args.split, "arms": {}}
    for arm in arms:
        guard = make_guard(arm)
        res = {"bipia": eval_bipia(guard, args.split), "cskh_vi": eval_cskh(guard, args.split),
               "pii_synthetic": eval_pii(arm, args.split)}
        if args.split == "test":  # JBB and openpii are test-only
            res["jbb"] = eval_jbb(guard)
            res["openpii_vi"] = eval_openpii(arm)
        out["arms"][arm] = res
        print(f"{arm}: done")
    REPORTS.mkdir(parents=True, exist_ok=True)
    target = REPORTS / f"detector_{out['date']}_{args.split}.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
