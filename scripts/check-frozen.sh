#!/usr/bin/env bash
# CI: reject a pull request that changes the frozen archive poster/ or a committed raw data file in data/runs/
# (new test runs may be added). Usage: check-frozen.sh <base-sha> <head-sha>
# A deliberate change needs a pull request that first changes this rule (management/WORKFLOW.md).
set -euo pipefail
base="$1"
head="$2"
changed="$(
    git diff --name-only --no-renames "$base...$head" -- poster
    git diff --name-only --no-renames --diff-filter=MDT "$base...$head" -- data/runs
)"
if [[ -n "$changed" ]]; then
    echo "These files are frozen (poster/ archive or raw data in data/runs/) and must not change:" >&2
    printf '%s\n' "$changed" | sed 's/^/  /' >&2
    exit 1
fi
