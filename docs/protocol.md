# Evaluation protocol

This page describes exactly how `kkspell evaluate` produces its numbers, so that a result can be reproduced or challenged.

## 1. Corpus and split
- Text is tokenised into lower-case Cyrillic words (`kkspell.textutil.tokenize`).
- The corpus is cut into **blocks** (a block header `#id` in block format, or `--block-size` consecutive lines in plain text).
- A block goes to `train`, `dev` or `test` by `md5(block id) mod 100` (test < 10, dev < 20, otherwise train), so a text is
  never split between parts and the split is identical on every machine.
- Sentences shorter than three tokens are dropped. Exact duplicates are removed from train; a dev or test sentence that also
  occurs in train is dropped (no credit for memorising seen text).

## 2. Evaluation items
- `n_eval` valid words and `n_eval` corrupted words are sampled from the *running text* of dev and of test (frequent words
  are sampled more often, as in real typing). Words shorter than three letters are not used.
- A corrupted word has exactly one error of one of six types (`diacritic`, `harmony`, `transpose`, `delete`, `insert`,
  `substitute`). The label comes from the injection, never from a dictionary.
- The same `--seed` always yields the same items.

## 3. Tuning and reporting
- Tuned on **dev only**: the minimum frequency of `VocabLookup` and `SuffixStrip` (1, 2, 3 or 5) and the score threshold of
  `CharLM` (chosen to maximise F1).
- Every reported number is computed on **test**. The F1 interval is a 95 % percentile bootstrap over the test items
  (`--bootstrap` resamples).

## 4. Known limitations
- Errors are synthetic and limited to one edit; real typing mistakes are more varied.
- Some injected errors accidentally spell another real word; the label still says "corrupted".
- On a very small corpus the splits are tiny and the numbers are only a smoke test.
