"""C3 detector level on the new benchmarks (no LLM calls): over-defence and new attack sources.

  NotInject (EN, 339 benign sentences with trigger words)    INPUT   → flag rate = over-defence FPR
  LLMail-Inject Phase 2 sample (600 adaptive attack emails)  CONTEXT → flag rate = recall
  LLMail-Inject emails_for_fp_tests (203 benign emails)      CONTEXT → flag rate = FPR
  MultiJail (315 harmful questions, Vietnamese + English)    INPUT   → flag rate (harmful, not injection:
                                                                        reported apart, like JBB harmful_bare)
  CyberSecEval inputs (EN 251 + VI 50 attacks)               INPUT/CONTEXT → flag rate = recall

Arms: R (Lớp 1–4, no classifier) and H-pg2 (R + Prompt Guard 2, fox-guard.yaml thresholds).
"Flagged" = action block or review, as in C2 (eval/run_detectors.py).

python -X utf8 -m eval.c3_detectors [--device cuda|cpu]
"""

import argparse
import json
from datetime import date
from pathlib import Path

from fox_guard import Guard, GuardContext
from fox_guard.config import GuardConfig, load_config

from .metrics import binary, percentile, rate

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "eval" / "reports"


def notinject() -> list[dict]:
    import pandas as pd

    rows = []
    for level, words in (("one", 1), ("two", 2), ("three", 3)):
        frame = pd.read_parquet(RAW / f"notinject/NotInject_{level}-00000-of-00001.parquet")
        rows += [
            {"text": t, "label": False, "group": f"{words}-word", "category": c}
            for t, c in zip(frame["prompt"], frame["category"], strict=True)
        ]
    return rows


def llmail() -> tuple[list[dict], list[dict]]:
    attacks = []
    for line in (RAW / "llmail/phase2_sample.jsonl").read_text("utf-8").splitlines():
        r = json.loads(line)
        objectives = json.loads(r["objectives"]) if r.get("objectives") else {}
        attacks.append(
            {
                "text": f"Subject: {r.get('subject') or ''}\n{r.get('body') or ''}",
                "label": True,
                "group": r.get("scenario", "")[:7],
                "succeeded_in_challenge": bool(objectives.get("exfil.sent")),
            }
        )
    benign = [
        {"text": t, "label": False, "group": "fp_tests"}
        for t in json.loads((RAW / "llmail/emails_for_fp_tests.json").read_text("utf-8"))
    ]
    return attacks, benign


def multijail() -> list[dict]:
    import pandas as pd

    frame = pd.read_csv(RAW / "multijail/MultiJail.csv")
    return [{"text": t, "label": True, "group": "vi"} for t in frame["vi"].dropna()] + [
        {"text": t, "label": True, "group": "en"} for t in frame["en"].dropna()
    ]


def cyberseceval() -> list[dict]:
    en = json.loads((RAW / "cyberseceval/prompt_injection.json").read_text("utf-8"))
    multi = json.loads(
        (RAW / "cyberseceval/prompt_injection_multilingual_machine_translated.json").read_text("utf-8")
    )
    rows = [{**c, "lang": "en"} for c in en] + [
        {**c, "lang": "vi"} for c in multi if c.get("speaking_language") == "Vietnamese"
    ]
    return [
        {
            "text": c["user_input"],
            "label": True,
            "group": f"{c['lang']}-{c['injection_type']}",
            "station": "input" if c["injection_type"] == "direct" else "context",
        }
        for c in rows
    ]


def make_guard(arm: str, device: str) -> Guard:
    if arm == "R":
        return Guard(GuardConfig.model_validate({"links": {"allowlist": ["shop.example"]}}))
    config = load_config(ROOT / "fox-guard.yaml")
    config.classifier.device = device
    return Guard(config)


def flag(guard: Guard, rows: list[dict], station: str) -> list[dict]:
    import time

    out = []
    for i, row in enumerate(rows):
        st = row.get("station", station)
        started = time.perf_counter()
        d = getattr(guard, f"check_{st}")(
            row["text"], GuardContext(session_id=f"c3-{i}", station=st, source="tool:email")
        )
        out.append(
            {
                **row,
                "flagged": d.action in ("block", "review"),
                "action": d.action,
                "ms": (time.perf_counter() - started) * 1000,
            }
        )
    return out


def by_group(results: list[dict]) -> dict:
    groups: dict[str, list[bool]] = {}
    for r in results:
        groups.setdefault(r["group"], []).append(r["flagged"])
    return {k: rate(v) for k, v in sorted(groups.items())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="cuda")
    args = parser.parse_args()
    attacks, benign_mail = llmail()
    sets = {
        "notinject": (notinject(), "input"),
        "llmail_attack": (attacks, "context"),
        "llmail_benign": (benign_mail, "context"),
        "multijail": (multijail(), "input"),
        "cyberseceval": (cyberseceval(), "input"),
    }
    report = {"date": date.today().isoformat(), "device": args.device, "arms": {}}
    for arm in ("R", "H-pg2"):
        guard = make_guard(arm, args.device)
        res = {name: flag(guard, rows, station) for name, (rows, station) in sets.items()}
        mail = res["llmail_attack"] + res["llmail_benign"]
        entry = {
            "notinject_fpr": rate([r["flagged"] for r in res["notinject"]]),
            "notinject_fpr_by_words": by_group(res["notinject"]),
            "llmail": binary([r["label"] for r in mail], [r["flagged"] for r in mail]).as_dict(),
            "llmail_recall_by_level": by_group(res["llmail_attack"]),
            "llmail_recall_on_challenge_successes": rate(
                [r["flagged"] for r in res["llmail_attack"] if r["succeeded_in_challenge"]]
            ),
            "multijail_flag_rate": by_group(res["multijail"]),
            "cyberseceval_recall": by_group(res["cyberseceval"]),
            "latency_ms": {
                name: {
                    "p50": round(percentile([r["ms"] for r in rows], 0.5), 1),
                    "p95": round(percentile([r["ms"] for r in rows], 0.95), 1),
                }
                for name, rows in res.items()
            },
            "notinject_false_positive_examples": [r["text"][:140] for r in res["notinject"] if r["flagged"]][
                :10
            ],
        }
        report["arms"][arm] = entry
        print(f"{arm}: done")
    REPORTS.mkdir(parents=True, exist_ok=True)
    target = REPORTS / f"c3_detectors_{report['date']}.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
