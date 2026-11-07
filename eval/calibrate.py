"""Choose classifier thresholds on the DEV split only (Phần C §2.5, DU-AN §4.5.1).

theta_high: smallest threshold whose false-positive rate on dev benign text is <= 2%;
theta_low : smallest threshold whose false-positive rate is <= 10%.
Dev benign = VI CSKH dev (hard-benign + clean) + BIPIA dev clean contexts. Scores are computed the
way the guard computes them (guard_score: views, decoded-view filter, window budget).

python -X utf8 -m eval.calibrate [--use secondary|primary] [--device cpu|cuda|groq]
Writes eval/reports/thresholds_<model>.json; the test split is never read here.
"""

import argparse
import json
from datetime import date
from pathlib import Path

from fox_guard.config import ClassifierConfig
from fox_guard.detectors.classifier import get_classifier, guard_score
from fox_guard.normalize import normalize

from .metrics import binary

ROOT = Path(__file__).resolve().parents[1]


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]


def score_as_guard(model, text: str) -> float:
    """Exactly the guard's rule (views, decoded-view filter, window budget): detectors/classifier.py."""
    return guard_score(model, normalize(text), ClassifierConfig().max_windows)[0]


def threshold_for(benign: list[float], max_fpr: float) -> float:
    """Smallest t with FPR(score >= t) <= max_fpr; candidates are just above observed scores."""
    candidates = sorted({0.5, *[min(1.0, s + 1e-6) for s in benign]})
    for t in candidates:
        if sum(s >= t for s in benign) / len(benign) <= max_fpr:
            return round(t, 6)
    return 1.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--use", default="secondary", choices=["primary", "secondary"])
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if args.device == "groq":  # eval-only API backend for Prompt Guard 2 (eval/groq_pg2.py)
        from .groq_pg2 import register

        register()
    model = get_classifier(ClassifierConfig(enabled=True, use=args.use, device=args.device))
    cskh = [c for c in read(ROOT / "eval/datasets/vi_cskh/cases.jsonl") if c["split"] == "dev"]
    bipia = read(ROOT / "data/processed/bipia/dev.jsonl")
    rows = []
    for c in cskh:
        text = c["user_query"] if c["source"] == "chat" else c["carrier_text"]
        rows.append({"set": f"cskh_{c['label']}", "label": c["label"] == "attack", "score": score_as_guard(model, text)})
    for c in bipia:
        rows.append({"set": f"bipia_{c['label']}", "label": c["label"] == "attack", "score": score_as_guard(model, c["text"])})
    benign = [r["score"] for r in rows if not r["label"]]
    theta_high, theta_low = threshold_for(benign, 0.02), threshold_for(benign, 0.10)
    report = {"date": date.today().isoformat(), "model": model.model_id, "split": "dev",
              "n_benign": len(benign), "theta_low": theta_low, "theta_high": theta_high, "per_set": {}}
    for name in sorted({r["set"] for r in rows}):
        scores = [r["score"] for r in rows if r["set"] == name]
        report["per_set"][name] = {"n": len(scores), "ge_theta_low": sum(s >= theta_low for s in scores),
                                   "ge_theta_high": sum(s >= theta_high for s in scores),
                                   "median": round(sorted(scores)[len(scores) // 2], 4)}
    attack = [r for r in rows if r["set"].startswith("bipia")]
    report["bipia_dev_at_theta_high"] = binary([r["label"] for r in attack],
                                               [r["score"] >= theta_high for r in attack]).as_dict()
    out = ROOT / "eval/reports" / f"thresholds_{model.short_name}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
