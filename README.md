# kkspell: evaluating spelling-error detection for Kazakh

[![CI](https://github.com/Maribuoo/kazakh-spellcheck-eval/actions/workflows/ci.yml/badge.svg)](https://github.com/Maribuoo/kazakh-spellcheck-eval/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`kkspell` is a small, dependency-free Python package that answers one question: **how well do simple methods tell
that a Kazakh word is misspelled?** It builds a reproducible evaluation set from any Kazakh text by injecting
Kazakh-specific errors, runs three checkers, and reports precision, recall, F1 and a bootstrap confidence interval.

## Why this exists (link to the dissertation)

The package is the reusable core of the experiments for the author's master's dissertation on a **hybrid typing
assistant for Kazakh** (spelling check, ending check and next-word suggestion). In that research the
word-checking component has to be chosen among several methods; this module is the part of the evaluation code that
is cleaned up, tested and published so that anyone can repeat the comparison on their own corpus.
The full research corpus is not public and is not part of this repository.

| Method | Idea | Cost |
|---|---|---|
| `VocabLookup` | the word occurs in the training text | ~1 µs |
| `SuffixStrip` | the word, or its stem after one common suffix, occurs in the training text | ~1 µs |
| `CharLM` | Witten–Bell character n-gram model of how Kazakh words are built | ~10 µs |
| `FstAnalyzer` (optional) | the Apertium-kaz finite-state analyzer has an analysis (needs `hfst`, GPL, not bundled) | ~10 µs |

Error types (exactly one edit each): `diacritic` (қ→к), `harmony` (wrong vowel class in the ending), `transpose`,
`delete`, `insert`, `substitute`.

## Install and use

```bash
git clone https://github.com/Maribuoo/kazakh-spellcheck-eval.git
cd kazakh-spellcheck-eval
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python -m kkspell evaluate data/sample_corpus_kk.txt          # table of results
python -m kkspell evaluate data/sample_corpus_kk.txt --json   # the same, machine readable
python -m kkspell check data/sample_corpus_kk.txt мектепке мектепка
```

From Python:

```python
from kkspell import read_blocks, build_splits, evaluate

splits = build_splits(read_blocks("my_corpus.txt"))      # split by block, no sentence leaks into test
result = evaluate(splits, n_eval=1000, seed=0)
print(result["methods"]["char-LM"]["f1"], result["methods"]["char-LM"]["f1_ci95"])
```

`data/sample_corpus_kk.txt` is a tiny demo text (a few hundred short sentences). Results on it only show that the
pipeline runs; use a real corpus (millions of tokens) for meaningful numbers.

## Corpus format

Plain text with one sentence per line, or "block format": a header `#<integer id>`, then sentences, blocks separated by
an empty line. The 80/10/10 train/dev/test split is made **by block** (hash of the id), duplicates are removed from
train and no dev/test sentence may also occur in train.

## Development

```bash
pytest --cov=kkspell      # 49 tests
ruff check .              # lint
```

Continuous integration (`.github/workflows/ci.yml`) runs lint and tests on Python 3.10–3.12 for every push and pull
request. Pushing a tag such as `v0.1.0` runs `.github/workflows/release.yml`, which builds the package and publishes a
GitHub Release with the wheel and source archive. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and
[CHANGELOG.md](CHANGELOG.md) for versions.

## License

MIT, see [LICENSE](LICENSE). The optional Apertium-kaz analyzer has its own license (GPL-3.0) and is not distributed here.
