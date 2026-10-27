# Dockerfile for kkspell (Assignment 5 — practical part)
#
# kkspell has no third-party runtime dependencies (pure Python standard
# library — see pyproject.toml: dependencies = []), so the image only needs
# the package itself installed. The [dev] extras (pytest, pytest-cov, ruff)
# are installed too, but only so the test suite can run as part of the
# build itself: if lint or tests fail, `docker build` fails too, so a
# broken commit can never produce a working-looking image. This mirrors the
# exact commands already used in .github/workflows/ci.yml, so the image
# build is a second, independent confirmation of the same checks.

FROM python:3.11-slim

WORKDIR /app

# Give pip more patience on a slow network: longer timeout and automatic
# retries instead of failing on one slow package download.
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_RETRIES=5

# Copy packaging metadata first so the dependency layer is cached
# separately from source-code changes.
COPY pyproject.toml README.md ./
COPY src/ src/
COPY tests/ tests/
COPY data/ data/

RUN pip install --no-cache-dir -e ".[dev]"

# Safety gate: same lint + coverage-gated test run as CI's `test` job.
RUN ruff check . && pytest --cov=kkspell --cov-report=term-missing --cov-fail-under=90

ENTRYPOINT ["python", "-m", "kkspell"]
CMD ["evaluate", "data/sample_corpus_kk.txt"]
