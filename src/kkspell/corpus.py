"""Reading a Kazakh text corpus and splitting it by *block* into train / dev / test.

Two input formats are accepted:

* **block format** - a block starts with a header line ``#<integer id>`` followed by one sentence per line;
  blocks are separated by empty lines (this is the format of the research corpus);
* **plain text** - one sentence per line; every ``block_size`` consecutive lines then form a block.

The split is made by a hash of the block id (80 / 10 / 10), so neighbouring sentences of one text never end up in
different parts and the split is the same on every machine.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Union

from .textutil import tokenize

_HEADER = re.compile(r"^#(\d+)$")
Block = tuple[int, list[str]]


def read_blocks(path: Union[str, Path], block_size: int = 5) -> list[Block]:
    """Read ``path`` and return a list of ``(block_id, sentences)``."""
    blocks: list[Block] = []
    plain: list[str] = []
    current_id, current = None, []
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            header = _HEADER.match(line)
            if header:
                if current_id is not None and current:
                    blocks.append((current_id, current))
                current_id, current = int(header.group(1)), []
            elif line.strip():
                (current if current_id is not None else plain).append(line.strip())
    if current_id is not None and current:
        blocks.append((current_id, current))
    for i in range(0, len(plain), block_size):  # plain-text lines (only used when there are no headers)
        chunk = plain[i:i + block_size]
        block_id = int(hashlib.md5(f"{Path(path).name}#{i // block_size}".encode()).hexdigest()[:12], 16)
        blocks.append((block_id, chunk))
    return blocks


def split_of(block_id: int) -> str:
    """Return ``"train"``, ``"dev"`` or ``"test"`` for a block id (80 / 10 / 10 by hash)."""
    h = int(hashlib.md5(str(block_id).encode()).hexdigest(), 16) % 100
    return "test" if h < 10 else ("dev" if h < 20 else "train")


def build_splits(blocks: list[Block], min_tokens: int = 3) -> dict[str, list[list[str]]]:
    """Tokenise the blocks and assign them to splits.

    Exact duplicate sentences are removed from train, and a dev/test sentence that also occurs in train is dropped,
    so a method cannot get credit for memorising a sentence it has already seen.
    """
    splits: dict[str, list[list[str]]] = {"train": [], "dev": [], "test": []}
    seen_train: set[str] = set()
    for block_id, sentences in blocks:
        part = split_of(block_id)
        for sentence in sentences:
            tokens = tokenize(sentence)
            if len(tokens) < min_tokens:
                continue
            key = " ".join(tokens)
            if part == "train":
                if key in seen_train:
                    continue
                seen_train.add(key)
            splits[part].append(tokens)
    for part in ("dev", "test"):
        splits[part] = [t for t in splits[part] if " ".join(t) not in seen_train]
    return splits
