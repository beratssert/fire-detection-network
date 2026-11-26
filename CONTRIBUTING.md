# Contributing

The team workflow — branching model, atomic commits, commit message tags, tests, pull requests, Definition of Done and
the quality gate — is described in [management/WORKFLOW.md](management/WORKFLOW.md).

Quick rules:

- Branch from the active milestone branch: `m<N>/<topic>`; open the pull request against `milestone/m<N>-…`.
- One logical change per commit; commit only when `scripts/test.sh` is green.
- Commit messages: `[WP1]`…`[WP5]`, `[MODEL]`, `[DATA]`, `[DOCS]`, `[CI]`, `[FIX]` + an imperative sentence.
- Set up every clone once: `bash scripts/setup.sh` (Git Bash on Windows). It also enables the local hooks.
- Real keys and tokens belong only in `secrets/` ([docs/key-management.md](docs/key-management.md)).
- Interface contracts and shared decisions ([docs/decisions.md](docs/decisions.md)) change only through a pull request
  with two approvals ([WORKFLOW](management/WORKFLOW.md#interface-contracts)).
- AI coding agents follow [AGENTS.md](AGENTS.md).
