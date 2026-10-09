"""Word-form checkers: does a Kazakh word look correctly spelled?

All checkers expose ``is_valid(word) -> bool``; ``CharLM`` additionally gives a continuous score.
They are deliberately small and dependency-free so that they can be compared, tested and run on any machine:

* :class:`VocabLookup`  - the word occurs at least ``min_freq`` times in the training text;
* :class:`SuffixStrip`  - the word, or its stem after removing one common suffix, is in the vocabulary;
* :class:`CharLM`       - interpolated Witten-Bell character n-gram language model with a score threshold;
* :class:`FstAnalyzer`  - optional wrapper for the Apertium-kaz finite-state analyzer (needs ``hfst``).
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Iterable, Mapping, Optional

#: Frequent Kazakh suffixes (plural, case, possessive, person) used by :class:`SuffixStrip`; longest first.
COMMON_SUFFIXES = (
    "дарымыздың", "терімізің", "ларымыздың", "сыздар", "сіздер", "дарың", "терің",
    "мын", "мін", "быз", "біз", "сың", "сің", "сыз", "сіз", "ның", "нің", "дың", "дің", "тың", "тің",
    "лар", "лер", "дар", "дер", "тар", "тер", "ды", "ді", "ты", "ті", "ны", "ні",
    "ым", "ім", "ың", "ің", "ы", "і", "ба", "бе", "па", "пе", "ма", "ме",
)


class VocabLookup:
    """Valid iff the word occurs at least ``min_freq`` times in ``counts``."""

    def __init__(self, counts: Mapping[str, int], min_freq: int = 1):
        if min_freq < 1:
            raise ValueError("min_freq must be >= 1")
        self.counts = counts
        self.min_freq = min_freq

    def is_valid(self, word: str) -> bool:
        return self.counts.get(word, 0) >= self.min_freq


class SuffixStrip:
    """Valid iff the word, or the word minus one common suffix, is in the vocabulary."""

    def __init__(self, counts: Mapping[str, int], min_freq: int = 1, suffixes: Iterable[str] = COMMON_SUFFIXES):
        self.counts = counts
        self.min_freq = min_freq
        self.suffixes = tuple(suffixes)

    def is_valid(self, word: str) -> bool:
        if self.counts.get(word, 0) >= self.min_freq:
            return True
        for suffix in self.suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 1:
                if self.counts.get(word[: -len(suffix)], 0) >= self.min_freq:
                    return True
        return False


class CharLM:
    """Interpolated Witten-Bell character n-gram model, trained on word *types*.

    Training on types (one count per distinct word) makes the model learn how Kazakh words are built, not which words
    are frequent. ``score(word)`` is the average log2-probability per character, so higher means more word-like.
    """

    def __init__(self, words: Iterable[str], order: int = 5, threshold: Optional[float] = None):
        if order < 2:
            raise ValueError("order must be >= 2")
        self.order = order
        self.threshold = threshold
        self._counts: dict[str, Counter] = defaultdict(Counter)
        for word in set(words):
            padded = "^" * (order - 1) + word + "$"
            for i in range(order - 1, len(padded)):
                for k in range(order):  # history length k = 0 .. order-1
                    self._counts[padded[i - k:i]][padded[i]] += 1
        if not self._counts:
            raise ValueError("CharLM needs at least one training word")
        self._total = {h: sum(c.values()) for h, c in self._counts.items()}
        self._types = {h: len(c) for h, c in self._counts.items()}
        self._vocab = len(self._counts[""]) + 1

    def _prob(self, history: str, char: str) -> float:
        p = 1.0 / self._vocab
        for k in range(len(history) + 1):
            h = history[len(history) - k:] if k else ""
            counts = self._counts.get(h)
            if not counts:
                break
            lam = self._total[h] / (self._total[h] + self._types[h])
            p = lam * counts.get(char, 0) / self._total[h] + (1 - lam) * p
        return p

    def score(self, word: str) -> float:
        padded = "^" * (self.order - 1) + word + "$"
        logp = 0.0
        for i in range(self.order - 1, len(padded)):
            logp += math.log2(self._prob(padded[i - self.order + 1:i], padded[i]))
        return logp / (len(padded) - self.order + 1)

    def fit_threshold(self, labelled: Iterable[tuple[str, int]]) -> float:
        """Choose the score threshold that maximises F1 on ``(word, label)`` pairs (label 1 = corrupted)."""
        scored = sorted((self.score(w), y) for w, y in labelled)
        positives = sum(y for _, y in scored)
        if positives == 0:
            raise ValueError("need at least one corrupted word to fit a threshold")
        best_f1, best_thr, tp, fp = -1.0, scored[0][0], 0, 0
        for score, y in scored:  # predict "corrupted" for every score <= this one
            tp += y
            fp += 1 - y
            precision, recall = tp / (tp + fp), tp / positives
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
            if f1 > best_f1:
                best_f1, best_thr = f1, score
        self.threshold = best_thr + 1e-9
        return self.threshold

    def is_valid(self, word: str) -> bool:
        if self.threshold is None:
            raise RuntimeError("call fit_threshold() or pass threshold= first")
        return self.score(word) >= self.threshold


class FstAnalyzer:
    """Optional wrapper for the Apertium-kaz transducer (HFST). Valid iff the word has at least one analysis.

    Requires ``pip install hfst turkicnlp`` (Python <= 3.12) and the analyzer file; it is GPL-3.0 and therefore not
    bundled with this package.
    """

    def __init__(self, path: str):
        import hfst  # imported lazily: the rest of the package has no third-party dependencies

        self._transducer = hfst.HfstInputStream(path).read()
        self._transducer.lookup_optimize()

    def is_valid(self, word: str) -> bool:
        return bool(self._transducer.lookup(word) or self._transducer.lookup(word.capitalize()))
