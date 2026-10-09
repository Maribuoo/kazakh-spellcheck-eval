"""Evaluation metrics for a binary "is this word corrupted?" decision (1 = corrupted = positive class)."""
from __future__ import annotations

import random
from typing import Sequence


def prf(predicted: Sequence[bool], labels: Sequence[int]) -> dict[str, float]:
    """Precision, recall, F1 and false-alarm rate (fraction of valid words flagged) of ``predicted`` against ``labels``."""
    if len(predicted) != len(labels):
        raise ValueError("predicted and labels must have the same length")
    tp = sum(1 for p, y in zip(predicted, labels, strict=True) if p and y)
    fp = sum(1 for p, y in zip(predicted, labels, strict=True) if p and not y)
    fn = sum(1 for p, y in zip(predicted, labels, strict=True) if not p and y)
    tn = sum(1 for p, y in zip(predicted, labels, strict=True) if not p and not y)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "fpr": fp / (fp + tn) if fp + tn else 0.0}


def bootstrap_f1_ci(predicted: Sequence[bool], labels: Sequence[int], n_resamples: int = 1000, seed: int = 0,
                    alpha: float = 0.05) -> tuple[float, float]:
    """Percentile bootstrap confidence interval (default 95 %) for F1, resampling the evaluation items."""
    if not predicted:
        raise ValueError("cannot bootstrap an empty evaluation")
    rng = random.Random(seed)
    n = len(predicted)
    scores = []
    for _ in range(n_resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        scores.append(prf([predicted[i] for i in idx], [labels[i] for i in idx])["f1"])
    scores.sort()
    lo = scores[int((alpha / 2) * n_resamples)]
    hi = scores[min(n_resamples - 1, int((1 - alpha / 2) * n_resamples))]
    return lo, hi
