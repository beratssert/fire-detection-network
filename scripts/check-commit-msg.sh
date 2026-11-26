#!/usr/bin/env bash
# Check one commit message (first line). Usage: check-commit-msg.sh [--allow-fixup] "<message>"
# Allowed: [WP1]..[WP5], [MODEL], [DATA], [DOCS], [CI], [FIX] + text, at most 72 characters; Git's Merge/Revert lines.
# With --allow-fixup (the local commit-msg hook) also the "fixup! ", "squash! " and "amend! " commits of
# git commit --fixup/--squash. Without it (CI) they are rejected, so they are squashed before a merge.
allow_fixup=0
if [[ "${1:-}" == --allow-fixup ]]; then
    allow_fixup=1
    shift
fi
first="$(printf '%s\n' "$1" | head -n 1)"
first="${first%$'\r'}"
if [[ "$first" =~ ^(Merge|Revert)\  ]]; then exit 0; fi
if [[ "$first" =~ ^(fixup|squash|amend)!\  ]]; then
    if ((allow_fixup)); then exit 0; fi
    echo "Squash this commit before the merge (git rebase -i --autosquash <milestone branch>): $first" >&2
    exit 1
fi
if [[ ! "$first" =~ ^\[(WP[1-5]|MODEL|DATA|DOCS|CI|FIX)\]\ .+ ]]; then
    echo "Commit message must start with [WP1]..[WP5], [MODEL], [DATA], [DOCS], [CI] or [FIX]: $first" >&2
    exit 1
fi
# count characters, not bytes, in every locale: drop the UTF-8 continuation bytes, then count
length=$(( $(printf '%s' "$first" | LC_ALL=C tr -d '\200-\277' | wc -c) ))
if (( length > 72 )); then
    echo "First line is longer than 72 characters (${length}): $first" >&2
    exit 1
fi
