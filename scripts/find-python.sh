#!/usr/bin/env bash
# Print the Python interpreter for the checks. Works on Linux, macOS and Windows (Git Bash).
# Order: $PYTHON, the active virtual environment, .venv of this clone, python3, python.
root="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -n "${PYTHON:-}" ]]; then
    candidates=("$PYTHON")
else
    candidates=()
    for venv in "${VIRTUAL_ENV:-}" "$root/.venv"; do
        if [[ -n "$venv" ]]; then candidates+=("$venv/bin/python" "$venv/Scripts/python.exe"); fi
    done
    candidates+=(python3 python)
fi
for py in "${candidates[@]}"; do
    # a relative path is made absolute, because the checks may run in another directory
    case "$py" in
        /* | [A-Za-z]:*) ;;
        */*) py="$PWD/$py" ;;
    esac
    if "$py" -c 'import ruff, pytest' > /dev/null 2>&1; then
        printf '%s\n' "$py"
        exit 0
    fi
done
echo "No Python with the check tools (ruff, pytest) was found. Run: bash scripts/setup.sh" >&2
exit 1
