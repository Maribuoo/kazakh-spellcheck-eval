"""Text helpers for Kazakh (Cyrillic) text: tokenisation and sentence splitting."""
from __future__ import annotations

import re

#: Lower-case letters of the Kazakh Cyrillic alphabet (Russian letters plus ә ғ қ ң ө ұ ү һ і).
KK_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяәғқңөұүһі"

#: Letters that exist only in Kazakh; their presence is a cheap hint that a word is Kazakh.
KK_SPECIFIC = frozenset("әғқңөұүһі")

_TOKEN = re.compile(r"[а-яёәғқңөұүһі]+")
_SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+(?=[\"«(]?[А-ЯӘҒҚҢӨҰҮҺІ])")


def tokenize(text: str) -> list[str]:
    """Lower-case ``text`` and return its Cyrillic word tokens (punctuation and digits are dropped)."""
    return _TOKEN.findall(text.lower())


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into sentences after ``. ! ? …`` when the next sentence starts with a capital letter."""
    out = []
    for line in text.splitlines():
        for sent in _SENT_SPLIT.split(line.strip()):
            sent = re.sub(r"\s+", " ", sent).strip()
            if sent:
                out.append(sent)
    return out
