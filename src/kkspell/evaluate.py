"""Compare the word-form checkers on a corpus: tune on dev, report on test with bootstrap confidence intervals."""
from __future__ import annotations

from collections import Counter
from typing import Any

from .checkers import CharLM, SuffixStrip, VocabLookup
from .errors import make_eval_set
from .metrics import bootstrap_f1_ci, prf


def evaluate(splits: dict[str, list[list[str]]], n_eval: int = 500, seed: int = 0, bootstrap: int = 1000) -> dict[str, Any]:
    """Run the comparison and return ``{"setup": ..., "methods": {name: metrics}}``.

    ``n_eval`` valid and ``n_eval`` corrupted words are drawn from each of dev and test. All tuning (minimum
    frequency, character-LM threshold) uses dev only; every reported number comes from test.
    """
    for part in ("train", "dev", "test"):
        if not splits.get(part):
            raise ValueError(f"the {part!r} split is empty; the corpus is too small for a block split")
    counts = Counter(w for sentence in splits["train"] for w in sentence)
    dev = make_eval_set(splits["dev"], n_eval, n_eval, seed=seed + 1)
    test = make_eval_set(splits["test"], n_eval, n_eval, seed=seed + 2)
    labels_dev, labels_test = [i.label for i in dev], [i.label for i in test]

    def best_min_freq(cls) -> int:
        scored = [(prf([not cls(counts, m).is_valid(i.word) for i in dev], labels_dev)["f1"], -m) for m in (1, 2, 3, 5)]
        return -max(scored)[1]

    lm = CharLM([w for w, c in counts.items() if c >= 2] or list(counts), order=4)
    lm.fit_threshold([(i.word, i.label) for i in dev])
    checkers = {
        "vocabulary": VocabLookup(counts, best_min_freq(VocabLookup)),
        "suffix-strip": SuffixStrip(counts, best_min_freq(SuffixStrip)),
        "char-LM": lm,
    }
    methods = {}
    for name, checker in checkers.items():
        predicted = [not checker.is_valid(i.word) for i in test]
        result = prf(predicted, labels_test)
        result["f1_ci95"] = bootstrap_f1_ci(predicted, labels_test, n_resamples=bootstrap, seed=seed)
        methods[name] = result
    return {"setup": {"train_tokens": sum(counts.values()), "vocab": len(counts), "test_items": len(test), "seed": seed},
            "methods": methods}
