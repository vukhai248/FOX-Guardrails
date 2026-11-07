"""BIPIA → detector-level cases (Phần C §2.1). Indirect prompt injection, English.

Dev  = train contexts × attack-TRAIN instructions; Test = test contexts × attack-TEST instructions.
BIPIA's train and test attack files contain different attack categories, so the split is "by attack
type" as the spec requires. Positives insert one attack instruction at the start, middle or end of a
clean context (the positions BIPIA uses); negatives are the clean contexts of the same split.

Output: data/processed/bipia/{dev,test}.jsonl (not committed: redistribute only via the builder).
python -X utf8 -m eval.datasets.external.bipia
"""

import json
import random
from collections import Counter
from pathlib import Path

from ..common import write_jsonl

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "bipia"
OUT = ROOT / "data" / "processed" / "bipia"
SEED = 20261107
POSITIONS = ("start", "middle", "end")
PLAN = {"dev": {"attacks_per_instruction": 2, "negatives": {"email": 50, "table": 100}},
        "test": {"attacks_per_instruction": 4, "negatives": {"email": 50, "table": 100}}}


def load_contexts(split: str) -> dict[str, list[dict]]:
    name = "train" if split == "dev" else "test"
    return {task: [json.loads(line) for line in (RAW / task / f"{name}.jsonl").read_text("utf-8").splitlines()
                   if line.strip()] for task in ("email", "table")}


def load_attacks(split: str) -> list[tuple[str, str]]:
    name = "train" if split == "dev" else "test"
    data = json.loads((RAW / f"text_attack_{name}.json").read_text("utf-8"))
    return [(category, text) for category, items in data.items() for text in items]


def insert(context: str, attack: str, position: str) -> str:
    if position == "start":
        return f"{attack}\n{context}"
    if position == "end":
        return f"{context}\n{attack}"
    lines = context.split("\n")
    if len(lines) > 2:
        cut = len(lines) // 2
        return "\n".join([*lines[:cut], attack, *lines[cut:]])
    sentences = context.split(". ")
    cut = max(1, len(sentences) // 2)
    return ". ".join(sentences[:cut]) + ". " + attack + " " + ". ".join(sentences[cut:])


def build(split: str) -> list[dict]:
    rng = random.Random(f"{SEED}:{split}")
    contexts = load_contexts(split)
    pool = [(task, i, row) for task in ("email", "table") for i, row in enumerate(contexts[task])]
    rng.shuffle(pool)
    cases, k = [], 0
    for a_index, (category, attack) in enumerate(load_attacks(split)):
        for rep in range(PLAN[split]["attacks_per_instruction"]):
            task, c_index, row = pool[k % len(pool)]
            position = POSITIONS[(a_index + rep) % 3]
            k += 1
            cases.append({"case_id": f"bipia-{split}-{task}{c_index}-a{a_index}-{position}", "split": split,
                          "label": "attack", "task": task, "attack_category": category, "position": position,
                          "question": row["question"], "text": insert(row["context"], attack, position),
                          "attack": attack})
    for task, n in PLAN[split]["negatives"].items():
        chosen = rng.sample(range(len(contexts[task])), min(n, len(contexts[task])))
        for c_index in sorted(chosen):
            row = contexts[task][c_index]
            cases.append({"case_id": f"bipia-{split}-{task}{c_index}-clean", "split": split, "label": "clean",
                          "task": task, "attack_category": None, "position": None,
                          "question": row["question"], "text": row["context"], "attack": None})
    return cases


def main() -> dict:
    summary = {}
    for split in ("dev", "test"):
        cases = build(split)
        write_jsonl(OUT / f"{split}.jsonl", cases)
        summary[split] = {"labels": dict(Counter(c["label"] for c in cases)),
                          "tasks": dict(Counter(c["task"] for c in cases)),
                          "positions": dict(Counter(c["position"] for c in cases if c["position"])),
                          "attack_categories": len({c["attack_category"] for c in cases if c["attack_category"]})}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return summary


if __name__ == "__main__":
    main()
