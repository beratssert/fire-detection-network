#!/usr/bin/env bash
# CI: check the message of every commit in BASE..HEAD and run scripts/test.sh on each commit.
# Usage: check-commits.sh <base-sha> <head-sha>   (run a copy of this file: it checks out other commits)
set -euo pipefail
base="$1"; head="$2"
root="$(git rev-parse --show-toplevel)"
cd "$root"
check_msg="$(mktemp)"; cp scripts/check-commit-msg.sh "$check_msg"
fail=0
for c in $(git rev-list --reverse --no-merges "$base..$head"); do
    echo "::group::$(git log -1 --format='%h %s' "$c")"
    bash "$check_msg" "$(git log -1 --format=%B "$c")" || fail=1
    git checkout -q "$c"
    bash scripts/test.sh || { echo "Tests fail at $c" >&2; fail=1; }
    echo "::endgroup::"
done
git checkout -q "$head"
exit "$fail"
