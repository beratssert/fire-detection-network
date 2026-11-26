# Instructions for AI coding agents

This file is the single source of rules for AI agents working in this repository (Claude Code reads it through
[CLAUDE.md](CLAUDE.md); GitHub Copilot and Antigravity read it directly). The rules apply to humans as well; they are
written out in [CONTRIBUTING.md](CONTRIBUTING.md) and [management/WORKFLOW.md](management/WORKFLOW.md). If this file and
those documents disagree, the documents win and this file must be fixed.

## Project

Graduation project: a multi-hop LoRa sensor network for early forest-fire detection (Seeed Wio-E5 mini, STM32WLE5JC),
built to measure quantities that earlier analyses had to assume. Results are to be published in a paper, so every
measurement must stay traceable and reproducible.

| Read first | For |
|---|---|
| [README.md](README.md) | what the project is, repository layout |
| [docs/architecture.md](docs/architecture.md) | components and their interfaces |
| [docs/decisions.md](docs/decisions.md) | decided and open design decisions |
| [docs/frame-format.md](docs/frame-format.md), [docs/serial-protocol.md](docs/serial-protocol.md), [docs/data-model.md](docs/data-model.md) | the interface contracts |
| [docs/key-management.md](docs/key-management.md) | keys and secrets |
| [management/WORKFLOW.md](management/WORKFLOW.md) | branches, commits, tests, pull requests |

## Never

- Never read, print, copy or create files in `secrets/`, and never write a real key, token or password into any other
  file, a commit message, an issue or a pull request ([docs/key-management.md](docs/key-management.md)).
- Never change `poster/` (frozen archive) or a committed file under `data/runs/` (raw data). CI rejects such changes.
- Never skip or disable checks: no `--no-verify`, no change of `core.hooksPath`, no editing a check to make it pass.
  If a check fails, fix the cause or ask a team member.
- Never push to `main` or `milestone/*` directly, and never force-push a branch that is not your own task branch
  (on your own task branch use `--force-with-lease`).
- Never fill in an open decision of [docs/decisions.md](docs/decisions.md) or an "Open" section of a contract on your
  own. Ask; the team decides in a pull request.

## Always

- Set-up once per clone: `bash scripts/setup.sh` (Git Bash on Windows). Before every commit: `bash scripts/test.sh`
  must pass; the hooks run it again.
- Work on a task branch `m<N>/<topic>` from the active milestone branch; pull requests are merged with
  *Rebase and merge*, so every commit must be atomic and pass the tests on its own.
- Commit messages: `[TAG] Imperative sentence`, at most 72 characters in the first line; tags `[WP1]`…`[WP5]`,
  `[MODEL]`, `[DATA]`, `[DOCS]`, `[CI]`, `[FIX]`. Review fixes: `git commit --fixup <commit>`, squashed with
  `git rebase -i --autosquash` before the merge.
- Write code, comments, documentation and commit messages in English.
- Python: target Python 3.12 (except `poster/`, which stays on 3.9); build paths with `pathlib`; ruff settings are in
  [pyproject.toml](pyproject.toml).
- Firmware: keep logic that does not touch the hardware (frame encoding, nonce, replay window, duty-cycle accounting,
  airtime) separate from the hardware code, so that it is unit tested on the host ([firmware/](firmware/README.md)).
- Do not name files `keys.c`, `secrets.json` and the like: these names are reserved for secrets and are rejected
  (see [scripts/check_secrets.py](scripts/check_secrets.py)).
- A change of a contract document needs an entry in [docs/decisions.md](docs/decisions.md) and the approval of two
  team members ([WORKFLOW](management/WORKFLOW.md#interface-contracts)).
