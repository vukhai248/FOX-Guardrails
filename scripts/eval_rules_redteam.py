"""Measure Lớp 2 rules on a red-team JSONL (id, label, station, group, text).

Usage: python -X utf8 scripts/eval_rules_redteam.py FILE
"""
import json
import sys
from collections import defaultdict

from fox_guard.detectors.rules import run_rules
from fox_guard.normalize import normalize

path = sys.argv[1]
cases = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
tp = fn = fp = tn = 0
by_group = defaultdict(lambda: [0, 0])
misses, false_pos = [], []
for c in cases:
    found = [f.detector for f in run_rules(normalize(c["text"]), c["station"])]
    if c["label"] == "attack":
        by_group[c["group"]][1] += 1
        if found:
            tp += 1
            by_group[c["group"]][0] += 1
        else:
            fn += 1
            misses.append((c["id"], c["group"], c["station"], c["text"][:110]))
    else:
        if found:
            fp += 1
            false_pos.append((c["id"], c["station"], found, c["text"][:110]))
        else:
            tn += 1
recall = tp / max(tp + fn, 1)
fpr = fp / max(fp + tn, 1)
precision = tp / max(tp + fp, 1)
print(f"attacks={tp + fn} benign={fp + tn} recall={recall:.2%} precision={precision:.2%} FPR={fpr:.2%}")
print("recall by group:", {g: f"{a}/{n}" for g, (a, n) in sorted(by_group.items())})
print("MISSES:")
for m in misses:
    print("  ", m)
print("FALSE POSITIVES:")
for f in false_pos:
    print("  ", f)
