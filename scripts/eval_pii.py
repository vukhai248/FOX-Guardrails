"""Per-entity recall/precision of Lớp 3 recognizers on a labelled PII JSONL + hard negatives.

Usage: python -X utf8 scripts/eval_pii.py POSITIVE.jsonl NEGATIVE.jsonl
"""
import json
import sys
from collections import Counter

from fox_guard.normalize import normalize
from fox_guard.pii.recognizers import detect_pii


def load(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


hit, total, wrong = Counter(), Counter(), Counter()
misses = []
for case in load(sys.argv[1]):
    found = detect_pii(normalize(case["text"]))
    total[case["entity"]] += 1
    ok = any(m.entity == case["entity"] and case["value"] in m.value or m.value in case["value"]
             and m.entity == case["entity"] and len(m.value) >= len(case["value"]) // 2 for m in found)
    if ok:
        hit[case["entity"]] += 1
    else:
        misses.append((case["id"], case["entity"], case["text"], [(m.entity, m.value) for m in found]))
    for m in found:
        if m.entity != case["entity"]:
            wrong[m.entity] += 1
negatives = load(sys.argv[2])
false_pos = [(c["id"], c["text"], [(m.entity, m.value) for m in found])
             for c in negatives if (found := detect_pii(normalize(c["text"])))]
caught, cases = sum(hit.values()), sum(total.values())
print(f"recall {caught}/{cases} = {caught / cases:.1%};"
      f" hard-negative false positives {len(false_pos)}/{len(negatives)};"
      f" extra wrong-type hits {sum(wrong.values())}")
for entity in sorted(total):
    print(f"  {entity:20s} {hit[entity]}/{total[entity]}")
print("MISSES:", *misses, sep="\n  ")
print("HARD-NEGATIVE HITS:", *false_pos, sep="\n  ")
print("WRONG-TYPE:", dict(wrong))
