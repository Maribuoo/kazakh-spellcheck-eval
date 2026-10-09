"""Command line: ``python -m kkspell evaluate CORPUS`` and ``python -m kkspell check CORPUS WORD [WORD ...]``."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from . import __version__
from .checkers import CharLM, SuffixStrip, VocabLookup
from .corpus import build_splits, read_blocks
from .errors import make_eval_set
from .evaluate import evaluate


def _cmd_evaluate(args: argparse.Namespace) -> int:
    splits = build_splits(read_blocks(args.corpus, block_size=args.block_size))
    result = evaluate(splits, n_eval=args.n_eval, seed=args.seed, bootstrap=args.bootstrap)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    setup = result["setup"]
    print(f"train tokens: {setup['train_tokens']}  vocabulary: {setup['vocab']}  test items: {setup['test_items']}")
    print(f"{'method':14s} {'precision':>9s} {'recall':>7s} {'F1':>6s} {'F1 95% CI':>16s} {'false alarms':>13s}")
    for name, m in result["methods"].items():
        lo, hi = m["f1_ci95"]
        print(f"{name:14s} {m['precision']:9.3f} {m['recall']:7.3f} {m['f1']:6.3f} [{lo:.3f}, {hi:.3f}] {m['fpr']:13.3f}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    splits = build_splits(read_blocks(args.corpus, block_size=args.block_size))
    counts = Counter(w for s in splits["train"] + splits["dev"] + splits["test"] for w in s)
    lm = CharLM(list(counts), order=4)
    dev = make_eval_set(splits["train"] or splits["test"], 300, 300, seed=1)
    lm.fit_threshold([(i.word, i.label) for i in dev])
    checkers = {"vocabulary": VocabLookup(counts), "suffix-strip": SuffixStrip(counts), "char-LM": lm}
    for word in args.words:
        verdicts = {name: ("ok" if c.is_valid(word.lower()) else "ERROR") for name, c in checkers.items()}
        print(word, verdicts)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="kkspell", description=__doc__)
    parser.add_argument("--version", action="version", version=f"kkspell {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    ev = sub.add_parser("evaluate", help="compare the checkers on a corpus")
    ev.add_argument("corpus")
    ev.add_argument("--n-eval", type=int, default=500, help="valid and corrupted words per split (default 500)")
    ev.add_argument("--seed", type=int, default=0)
    ev.add_argument("--bootstrap", type=int, default=1000, help="bootstrap resamples for the F1 interval")
    ev.add_argument("--block-size", type=int, default=5, help="lines per block for plain-text corpora")
    ev.add_argument("--json", action="store_true", help="print the full result as JSON")
    ev.set_defaults(func=_cmd_evaluate)
    ck = sub.add_parser("check", help="check single words against a corpus vocabulary")
    ck.add_argument("corpus")
    ck.add_argument("words", nargs="+")
    ck.add_argument("--block-size", type=int, default=5)
    ck.set_defaults(func=_cmd_check)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
