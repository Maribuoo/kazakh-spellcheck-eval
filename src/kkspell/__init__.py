"""kkspell - evaluate how well simple methods detect spelling errors in Kazakh words."""
from .checkers import COMMON_SUFFIXES, CharLM, FstAnalyzer, SuffixStrip, VocabLookup
from .corpus import build_splits, read_blocks, split_of
from .errors import ERROR_TYPES, Item, corrupt, make_eval_set
from .evaluate import evaluate
from .metrics import bootstrap_f1_ci, prf
from .textutil import KK_ALPHABET, split_sentences, tokenize

__version__ = "0.1.0"
__all__ = [
    "COMMON_SUFFIXES", "CharLM", "ERROR_TYPES", "FstAnalyzer", "Item", "KK_ALPHABET", "SuffixStrip", "VocabLookup",
    "bootstrap_f1_ci", "build_splits", "corrupt", "evaluate", "make_eval_set", "prf", "read_blocks", "split_of",
    "split_sentences", "tokenize",
]
