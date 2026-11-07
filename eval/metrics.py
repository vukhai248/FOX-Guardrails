"""Metrics for Phần C (docs/plans/C-du-lieu-va-thuc-nghiem.md §3.2, §3.5).

Rates carry a Wilson 95% interval; F1 carries a bootstrap (1,000 resamples, fixed seed) interval.
PII spans match when the entity group agrees and the prediction covers ≥ 50% of the gold characters.
"""

import math
import random
from dataclasses import asdict, dataclass

Z = 1.959963984540054  # 95%


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / denom
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


@dataclass
class BinaryReport:
    n_pos: int
    n_neg: int
    tp: int
    fp: int
    precision: float
    recall: float
    recall_ci: tuple[float, float]
    f1: float
    f1_ci: tuple[float, float]
    fpr: float
    fpr_ci: tuple[float, float]

    def as_dict(self) -> dict:
        return {k: (round(v, 4) if isinstance(v, float) else [round(x, 4) for x in v] if isinstance(v, tuple) else v)
                for k, v in asdict(self).items()}


def binary(labels: list[bool], preds: list[bool], seed: int = 20261107, resamples: int = 1000) -> BinaryReport:
    """labels/preds: True = attack / flagged."""
    tp = sum(y and p for y, p in zip(labels, preds, strict=True))
    fp = sum((not y) and p for y, p in zip(labels, preds, strict=True))
    fn = sum(y and not p for y, p in zip(labels, preds, strict=True))
    n_pos, n_neg = sum(labels), len(labels) - sum(labels)
    precision, recall, f1 = prf(tp, fp, fn)
    rng = random.Random(seed)
    pairs = list(zip(labels, preds, strict=True))
    scores = []
    for _ in range(resamples):
        sample = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        s_tp = sum(y and p for y, p in sample)
        s_fp = sum((not y) and p for y, p in sample)
        s_fn = sum(y and not p for y, p in sample)
        scores.append(prf(s_tp, s_fp, s_fn)[2])
    scores.sort()
    f1_ci = (scores[int(0.025 * resamples)], scores[int(0.975 * resamples) - 1]) if pairs else (0.0, 0.0)
    return BinaryReport(n_pos, n_neg, tp, fp, precision, recall, wilson(tp, n_pos), f1, f1_ci,
                        fp / n_neg if n_neg else 0.0, wilson(fp, n_neg))


def rate(flags: list[bool]) -> dict:
    k, n = sum(flags), len(flags)
    return {"n": n, "k": k, "rate": round(k / n, 4) if n else 0.0, "ci": [round(x, 4) for x in wilson(k, n)]}


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


# ------------------------------------------------------------------ PII span matching
def overlap_ok(pred: tuple[int, int], gold: tuple[int, int]) -> bool:
    covered = max(0, min(pred[1], gold[1]) - max(pred[0], gold[0]))
    return covered >= 0.5 * (gold[1] - gold[0])


def span_prf(cases: list[dict], compatible) -> dict:
    """cases: {"gold": [(group, start, end)], "pred": [(group, start, end)]}. Per-group P/R/F1."""
    groups = sorted({g for c in cases for g, *_ in c["gold"]} | {g for c in cases for g, *_ in c["pred"]})
    out = {}
    for group in groups + ["ALL"]:
        tp = fp = fn = 0
        for case in cases:
            gold = [s for s in case["gold"] if group in ("ALL", s[0])]
            pred = [s for s in case["pred"] if group in ("ALL", s[0])]
            used = set()
            for g in gold:
                hit = next((i for i, p in enumerate(pred) if i not in used and compatible(p[0], g[0])
                            and overlap_ok(p[1:], g[1:])), None)
                if hit is None:
                    fn += 1
                else:
                    used.add(hit)
                    tp += 1
            fp += len(pred) - len(used)
        p, r, f = prf(tp, fp, fn)
        out[group] = {"tp": tp, "fp": fp, "fn": fn, "precision": round(p, 4), "recall": round(r, 4),
                      "f1": round(f, 4)}
    return out
