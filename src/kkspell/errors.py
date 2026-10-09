"""Kazakh-specific synthetic spelling errors.

Every error is exactly *one* edit of one of six types, so an evaluation set can be built from any plain text and the
label ("this word was corrupted") comes from the injection, never from a dictionary.

====================  ==========================================================================
``diacritic``         a Kazakh letter typed as its Russian-keyboard look-alike (қалай -> калай)
``harmony``           a vowel of the ending switched to the wrong harmony class (мектепке -> мектепка)
``transpose``         two adjacent different letters swapped
``delete``            one letter dropped (words of at least four letters)
``insert``            one letter added (duplicate of the previous letter or a random letter)
``substitute``        one letter replaced by a different random letter
====================  ==========================================================================
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional, Sequence

from .textutil import KK_ALPHABET

DIACRITIC_LOSS = {"ә": "а", "ғ": "г", "қ": "к", "ң": "н", "ө": "о", "ұ": "у", "ү": "у", "һ": "х", "і": "и"}
HARMONY_SWAP = {"а": "е", "е": "а", "ы": "і", "і": "ы", "о": "ө", "ө": "о", "ұ": "ү", "ү": "ұ", "ә": "а"}
ERROR_TYPES = ("diacritic", "harmony", "transpose", "delete", "insert", "substitute")


def corrupt(word: str, error_type: str, rng: random.Random) -> Optional[str]:
    """Return ``word`` with one error of ``error_type``, or ``None`` if that error cannot be applied to ``word``."""
    if error_type == "diacritic":
        pos = [i for i, c in enumerate(word) if c in DIACRITIC_LOSS]
        if not pos:
            return None
        i = rng.choice(pos)
        return word[:i] + DIACRITIC_LOSS[word[i]] + word[i + 1:]
    if error_type == "harmony":
        pos = [i for i in range(max(0, len(word) - 4), len(word)) if word[i] in HARMONY_SWAP]
        if not pos:
            return None
        i = rng.choice(pos)
        return word[:i] + HARMONY_SWAP[word[i]] + word[i + 1:]
    if error_type == "transpose":
        pos = [i for i in range(len(word) - 1) if word[i] != word[i + 1]]
        if not pos:
            return None
        i = rng.choice(pos)
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    if error_type == "delete":
        if len(word) < 4:
            return None
        i = rng.randrange(len(word))
        return word[:i] + word[i + 1:]
    if error_type == "insert":
        i = rng.randrange(len(word) + 1)
        letter = word[i - 1] if (i > 0 and rng.random() < 0.5) else rng.choice(KK_ALPHABET)
        return word[:i] + letter + word[i:]
    if error_type == "substitute":
        i = rng.randrange(len(word))
        letter = rng.choice(KK_ALPHABET)
        return None if letter == word[i] else word[:i] + letter + word[i + 1:]
    raise ValueError(f"unknown error type: {error_type!r}")


@dataclass(frozen=True)
class Item:
    """One evaluation item: a word, its label (1 = corrupted) and where it came from."""

    word: str
    label: int
    error_type: str
    original: str
    prev: str


def make_eval_set(sentences: Sequence[Sequence[str]], n_valid: int, n_error: int, seed: int = 0, min_len: int = 3) -> list[Item]:
    """Build a shuffled evaluation set of ``n_valid`` untouched words and ``n_error`` corrupted words.

    ``sentences`` is a list of token lists. Words are sampled from running text (so frequent words appear more often),
    which mirrors what a typist actually writes. The same ``seed`` always gives the same set.
    """
    if not sentences or not any(len(s) for s in sentences):
        raise ValueError("need at least one non-empty sentence")
    rng = random.Random(seed)

    def pick() -> tuple[str, str]:
        for _ in range(10_000):
            sent = sentences[rng.randrange(len(sentences))]
            if not sent:
                continue
            i = rng.randrange(len(sent))
            if len(sent[i]) >= min_len:
                return sent[i], (sent[i - 1] if i else "^")
        raise ValueError("no word of the required length found in the sentences")

    items = []
    for _ in range(n_valid):
        word, prev = pick()
        items.append(Item(word, 0, "valid", word, prev))
    produced = 0
    while produced < n_error:
        word, prev = pick()
        etype = rng.choice(ERROR_TYPES)
        bad = corrupt(word, etype, rng)
        if bad and bad != word and len(bad) >= 2:
            items.append(Item(bad, 1, etype, word, prev))
            produced += 1
    rng.shuffle(items)
    return items
