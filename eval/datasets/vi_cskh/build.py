"""Build the Vietnamese customer-service bench (Phần C §2.3) from hand-written templates.

Inputs  eval/datasets/vi_cskh/templates/{attack,benign}_templates.jsonl  (reviewed by the owner)
Outputs eval/datasets/vi_cskh/cases.jsonl       every case with labels and split
        eval/datasets/vi_cskh/seed_cases.jsonl  only what the web DB needs (carrier text + target)
        eval/datasets/vi_cskh/SPLIT_REPORT.md

python -X utf8 -m eval.datasets.vi_cskh.build
"""

import random
from collections import Counter
from pathlib import Path

from ..common import read_jsonl, resolve_leaks, split_of, within_split_duplicates, write_jsonl
from .transforms import TRANSFORMS

HERE = Path(__file__).resolve().parent
SEED = 20261107
VARIANT_SHARE = 0.40  # share of attack templates that also get one T3 evasion variant
KEYS = (
    "template_id",
    "source",
    "label",
    "technique",
    "attack_goal",
    "user_query",
    "carrier_text",
    "canary",
    "expected_task",
    "gold_facts",
    "notes",
)


def attack_text_field(case: dict) -> str:
    return "user_query" if case["source"] == "chat" else "carrier_text"


def text_of(case: dict) -> str:
    return case["carrier_text"] or case["user_query"]


def validate(template: dict) -> None:
    missing = set(KEYS) - set(template)
    if missing:
        raise ValueError(f"{template.get('template_id')}: missing {sorted(missing)}")
    if template["label"] not in ("attack", "hard_benign", "clean"):
        raise ValueError(f"{template['template_id']}: bad label {template['label']}")
    if template["source"] not in ("review", "order_note", "ticket_note", "chat"):
        raise ValueError(f"{template['template_id']}: bad source {template['source']}")


def build(templates: list[dict]) -> list[dict]:
    rng = random.Random(SEED)
    cases = []
    for template in templates:
        validate(template)
        split = split_of(template["template_id"])
        base = {
            **template,
            "case_id": f"{template['template_id']}-base",
            "split": split,
            "generated_by": "template",
            "technique": list(template["technique"]),
        }
        cases.append(base)
        if template["label"] == "attack" and rng.random() < VARIANT_SHARE:
            code = rng.choice(sorted(TRANSFORMS))
            field = attack_text_field(template)
            variant = {
                **base,
                "case_id": f"{template['template_id']}-{code.replace('.', '')}",
                "technique": [*base["technique"], code],
                "generated_by": f"transform:{code}",
            }
            variant[field] = TRANSFORMS[code](template[field], random.Random(f"{SEED}:{variant['case_id']}"))
            cases.append(variant)
    return cases


def report(cases: list[dict], leaks: dict, dups: int, sources: dict) -> str:
    lines = [
        "# SPLIT_REPORT — bộ CSKH tiếng Việt",
        "",
        f"Seed `{SEED}`, chia theo `template_id` (dev ≈ 30% mẫu gốc). Nguồn mẫu: "
        + ", ".join(f"`{k}` {v} mẫu" for k, v in sources.items())
        + ".",
        "",
        "| split | label | source | số ca |",
        "| --- | --- | --- | --- |",
    ]
    for (split, label, source), n in sorted(
        Counter((c["split"], c["label"], c["source"]) for c in cases).items()
    ):
        lines.append(f"| {split} | {label} | {source} | {n} |")
    variants = Counter(c["generated_by"] for c in cases if c["generated_by"] != "template")
    lines += [
        "",
        f"Biến thể T3: {sum(variants.values())} ca ({', '.join(f'{k} {v}' for k, v in sorted(variants.items()))}).",
        f"Kiểm trùng giữa dev/test: chuyển {leaks['moved_exact']} mẫu trùng hẳn và {leaks['moved_near']} mẫu gần trùng "
        f"(Jaccard 5-gram ≥ 0,8) sang dev. Trùng trong cùng một tập: {dups} ca.",
        "",
    ]
    if not any(c["label"] == "attack" for c in cases):
        lines += [
            "**Chưa có ca tấn công**: `templates/attack_templates.jsonl` chưa có. Xem ghi chú trong PR.",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    sources, templates = {}, []
    for name in ("attack_templates.jsonl", "benign_templates.jsonl"):
        path = HERE / "templates" / name
        if path.exists():
            rows = read_jsonl(path)
            sources[name] = len(rows)
            templates += rows
    cases = build(templates)
    leaks = resolve_leaks(cases, text_of)
    dups = within_split_duplicates(cases, text_of)
    write_jsonl(
        HERE / "cases.jsonl", [{k: c[k] for k in ("case_id", "split", *KEYS, "generated_by")} for c in cases]
    )
    seeds = [
        {"case_id": c["case_id"], "source": c["source"], "carrier_text": c["carrier_text"]}
        for c in cases
        if c["source"] != "chat"
    ]
    write_jsonl(HERE / "seed_cases.jsonl", seeds)
    (HERE / "SPLIT_REPORT.md").write_text(report(cases, leaks, dups, sources), encoding="utf-8")
    print((HERE / "SPLIT_REPORT.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
