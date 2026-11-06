"""Shared helpers for Phần C datasets: deterministic dev/test split by template, duplicate checks.

Rules (docs/plans/C-du-lieu-va-thuc-nghiem.md §2.5):
- split by `template_id`: a template and all its variants stay on one side (dev 30% / test 70%);
- exact duplicates (NFKC + lowercase + collapsed spaces) and near duplicates (Jaccard of character
  5-grams ≥ 0.8) across dev/test are moved to one side, and the script reports how many.
"""

import hashlib
import json
import unicodedata
from pathlib import Path

DEV_SHARE = 30  # percent of templates in dev
SALT = "fox-c1-2026-11-07"  # fixed: changing it reshuffles the split


def split_of(template_id: str) -> str:
    bucket = int(hashlib.sha256(f"{SALT}:{template_id}".encode()).hexdigest(), 16) % 100
    return "dev" if bucket < DEV_SHARE else "test"


def norm_key(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).lower().split())


def shingles(text: str, n: int = 5) -> set[str]:
    t = norm_key(text)
    return {t[i : i + n] for i in range(max(1, len(t) - n + 1))}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def resolve_leaks(cases: list[dict], text_of, threshold: float = 0.8) -> dict:
    """Move whole template groups so no exact or near duplicate spans dev and test.

    A test template whose text duplicates a dev template is moved to dev (dev may grow; test stays
    clean). Returns counts for SPLIT_REPORT.md.
    """
    by_template: dict[str, list[dict]] = {}
    for case in cases:
        by_template.setdefault(case["template_id"], []).append(case)
    dev_keys, dev_shingles = set(), []
    for case in cases:
        if case["split"] == "dev":
            dev_keys.add(norm_key(text_of(case)))
            dev_shingles.append(shingles(text_of(case)))
    moved_exact, moved_near = set(), set()
    for template_id, group in by_template.items():
        if group[0]["split"] != "test":
            continue
        for case in group:
            key = norm_key(text_of(case))
            if key in dev_keys:
                moved_exact.add(template_id)
                break
            sh = shingles(text_of(case))
            if any(jaccard(sh, other) >= threshold for other in dev_shingles):
                moved_near.add(template_id)
                break
    for template_id in moved_exact | moved_near:
        for case in by_template[template_id]:
            case["split"] = "dev"
    return {"moved_exact": len(moved_exact), "moved_near": len(moved_near)}


def within_split_duplicates(cases: list[dict], text_of) -> int:
    seen, dups = set(), 0
    for case in cases:
        key = (case["split"], norm_key(text_of(case)))
        dups += key in seen
        seen.add(key)
    return dups


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
