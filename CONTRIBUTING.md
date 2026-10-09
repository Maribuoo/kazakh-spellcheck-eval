# Contributing

1. Open an issue (bug report or feature request) so the change can be discussed.
2. Create a branch from `main`: `feature/<short-name>` or `fix/<short-name>`.
3. Install for development: `pip install -e ".[dev]"`.
4. Keep the checks green locally: `ruff check .` and `pytest --cov=kkspell`.
5. Add or update tests for every behaviour change; public functions need a docstring.
6. Commit with a clear message in the imperative mood ("Add bootstrap interval"), push the branch and open a pull
   request that references the issue (`Closes #N`). The CI workflow must pass before merging.

Versions follow [Semantic Versioning](https://semver.org/); user-visible changes go to `CHANGELOG.md`.
