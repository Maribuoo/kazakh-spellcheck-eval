# Changelog

## [0.1.0] - 2026-10-09
### Added
- Kazakh-specific error injection (six one-edit error types) and reproducible evaluation sets.
- Checkers: vocabulary lookup, suffix stripping, character n-gram language model, optional Apertium-kaz wrapper.
- Block-level 80/10/10 corpus split with duplicate control.
- Metrics (precision, recall, F1, false-alarm rate) and bootstrap confidence intervals.
- Command line interface (`python -m kkspell evaluate | check`).
- Test suite, lint configuration and GitHub Actions CI/CD.
- Documentation of the evaluation protocol (`docs/protocol.md`).
