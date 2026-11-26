#!/usr/bin/env bash
# Every automatic check that applies to the files in the repository.
# Used by the pre-commit hook (.githooks/pre-commit) and by CI. Exit code 0 only if all checks pass.
# It checks the directory it lies in, which may be an export of the staged files without .git.
# poster/ is a frozen archive; it is not linted or tested (see poster/README.md).
set -euo pipefail
cd "$(dirname "$0")/.."
PY="$(bash scripts/find-python.sh)"

echo "== secret check"
"$PY" scripts/check_secrets.py

echo "== file size check"
"$PY" scripts/check_file_size.py

echo "== ruff (lint, format)"
"$PY" -m ruff check .
"$PY" -m ruff format --check .

test_files="$(find . \( -path ./poster -o -path './.*' -o -path ./build -o -name venv -o -name env \) -prune -o \
    \( -name 'test_*.py' -o -name '*_test.py' \) -print)"
if [[ -n "$test_files" ]]; then
    echo "== pytest"
    "$PY" -m pytest -q
fi

if [[ -f firmware/tests/CMakeLists.txt ]]; then
    echo "== firmware host unit tests"
    # --config and -C are needed by multi-configuration generators (Visual Studio); others ignore them
    cmake -S firmware/tests -B build/host-tests > /dev/null
    cmake --build build/host-tests --config Debug > /dev/null
    ctest --test-dir build/host-tests -C Debug --output-on-failure
fi

echo "All checks passed."
