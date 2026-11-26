#!/usr/bin/env bash
# Full pipeline: models -> reqdens -> latency -> energy -> cost -> macros -> figures -> pdflatex / bibtex / pdflatex x2.
# Run from anywhere with the project venv active:  source .venv/bin/activate && ./run_all.sh
# Does not touch git (no add, no checkout); figures/*.pdf change only in /CreationDate.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd -P)"

# Never read or write a stale cached params.pyc: Apple's Python keeps bytecode outside the
# repo (~/Library/Caches/com.apple.python) and validates it by size + mtime in whole seconds.
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPYCACHEPREFIX="$(mktemp -d)"
trap 'rm -rf "$PYTHONPYCACHEPREFIX"' EXIT

# --- the python on PATH must be the project venv -----------------------------------------
VENV="$ROOT/.venv"
PY="$(command -v python || true)"
if [[ -z "$PY" ]]; then
    echo "ERROR: no 'python' on PATH. Run: source .venv/bin/activate" >&2
    exit 1
fi
PY_PREFIX="$(python -c 'import os, sys; print(os.path.realpath(sys.prefix))' 2>/dev/null || echo '<python failed to start>')"
if [[ "$PY" != "$VENV/bin/python" || "$PY_PREFIX" != "$(cd "$VENV" && pwd -P)" ]]; then
    echo "ERROR: python is $PY (sys.prefix $PY_PREFIX), not the project venv $VENV." >&2
    echo "       Run: source .venv/bin/activate" >&2
    exit 1
fi
echo "python: $PY ($(python --version 2>&1))"

# --- models and figures ------------------------------------------------------------------
python models.py
python reqdens.py
python latency.py
python energy.py
python cost.py
python macros.py
python figures.py   # DejaVu Sans (ships with matplotlib), no fallback-font warnings (#36)

# --- poster ----------------------------------------------------------------------------------
latex() {
    pdflatex -halt-on-error -interaction=nonstopmode poster.tex > /dev/null || {
        echo "ERROR: pdflatex failed; last lines of poster.log:" >&2
        tail -20 poster.log >&2
        exit 1
    }
}
latex
# bibtex exits 2 while references.bib has repeated entries (REVIEW #34). Only bibtex's own
# warning/error codes (1, 2) are tolerated; 3+ (fatal, e.g. missing .aux) stops the run.
set +e
BIBOUT="$(bibtex poster 2>&1)"
BIB=$?
set -e
if (( BIB != 0 )); then
    echo "bibtex exit $BIB (bkz. REVIEW #34)"
    grep -E 'Repeated entry|error message' <<< "$BIBOUT" || true
    if (( BIB >= 3 )); then
        echo "ERROR: bibtex fatal error:" >&2
        echo "$BIBOUT" >&2
        exit 1
    fi
fi
latex
latex

# --- independent model checks (tests/check_model.py) ---------------------------------------
python tests/check_model.py

# --- summary -------------------------------------------------------------------------------
echo "Overfull/Underfull: $(grep -c 'Overfull\|Underfull' poster.log || true)"
echo "Undefined: $(grep -c 'Undefined' poster.log || true)"
echo "poster.pdf: $ROOT/poster.pdf"
