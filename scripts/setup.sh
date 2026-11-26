#!/usr/bin/env bash
# One-time set-up of a clone on Linux, macOS or Windows (run it in Git Bash). Safe to run again.
#   bash scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# Python 3.12 or newer (docs/decisions.md, D1)
new_enough='import sys; sys.exit(sys.version_info < (3, 12))'
if [[ -d .venv ]]; then
    if [[ -x .venv/bin/python ]]; then venv_python=.venv/bin/python; else venv_python=.venv/Scripts/python.exe; fi
    if ! "$venv_python" -c "$new_enough" > /dev/null 2>&1; then
        echo ".venv uses a Python older than 3.12. Delete the .venv folder and run this script again." >&2
        exit 1
    fi
else
    base=""
    for py in python3 python python3.14 python3.13 python3.12; do
        # on Windows "python3" may be a placeholder that only opens the Microsoft Store, so try to run it
        if "$py" -c "$new_enough" > /dev/null 2>&1; then base="$py"; break; fi
    done
    if [[ -z "$base" ]]; then
        echo "Python 3.12 or newer is required and was not found (python3 / python / python3.1x)." >&2
        exit 1
    fi
    echo "== creating .venv"
    "$base" -m venv .venv
fi

if [[ -x .venv/bin/python ]]; then venv_python=.venv/bin/python; else venv_python=.venv/Scripts/python.exe; fi
echo "== installing the check tools"
"$venv_python" -m pip install --quiet -r requirements-dev.txt

echo "== enabling the git hooks"
git config core.hooksPath .githooks

email="$(git config user.email || true)"
if [[ "$email" != *@users.noreply.github.com ]]; then
    echo "Note: your commit e-mail is '${email:-not set}'. It will be visible in a public repository."
    echo "      To hide it, use the noreply address shown on GitHub under Settings > Emails."
fi
echo "Set-up finished. Run the checks with: bash scripts/test.sh"
