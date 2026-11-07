"""JailbreakBench → detector-level cases (Phần C §2.2). Direct jailbreak prompts, English; test only.

- attack       : every prompt in the PAIR/GCG artifacts (an attack attempt, successful or not; the
                 `jailbroken` flag is kept so results can also be reported on successful ones only);
- benign       : the 100 benign behaviors (goal text);
- harmful_bare : the 100 harmful goals without any jailbreak wrapper. Reported separately: FOX is a
                 prompt-injection/jailbreak guard, not a harmful-content filter.

Output: data/processed/jbb/test.jsonl (not committed). python -X utf8 -m eval.datasets.external.jbb
"""

import csv
import json
from collections import Counter
from pathlib import Path

from ..common import norm_key, write_jsonl

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "jbb"
OUT = ROOT / "data" / "processed" / "jbb"


def build() -> list[dict]:
    cases, seen = [], set()
    for path in sorted((RAW / "artifacts").glob("*/*/*.json")):
        data = json.loads(path.read_text("utf-8"))
        method, model = data["parameters"]["method"], data["parameters"]["model"]
        for item in data["jailbreaks"]:
            prompt = item.get("prompt")
            if not prompt or norm_key(prompt) in seen:
                continue
            seen.add(norm_key(prompt))
            cases.append({"case_id": f"jbb-{method}-{model}-{item['index']}", "split": "test", "label": "attack",
                          "method": method, "target_model": model, "category": item.get("category"),
                          "jailbroken": str(item.get("jailbroken")) == "True", "text": prompt})
    for name, label in (("benign-behaviors.csv", "benign"), ("harmful-behaviors.csv", "harmful_bare")):
        with (RAW / name).open(encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                cases.append({"case_id": f"jbb-{label}-{row['Index']}", "split": "test", "label": label,
                              "method": None, "target_model": None, "category": row["Category"],
                              "jailbroken": None, "text": row["Goal"]})
    return cases


def main() -> dict:
    cases = build()
    write_jsonl(OUT / "test.jsonl", cases)
    summary = {"labels": dict(Counter(c["label"] for c in cases)),
               "attack_by_method": dict(Counter(f"{c['method']}/{c['target_model']}" for c in cases if c["method"])),
               "attack_jailbroken": sum(1 for c in cases if c["jailbroken"])}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return summary


if __name__ == "__main__":
    main()
