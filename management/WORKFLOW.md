# Team workflow

All four members are equally responsible for all work packages. This document describes how we plan, branch, commit,
review, test and release.

## Development methodology

- **Iterations of two weeks**, aligned with the supervisor meetings. Each meeting is the review of the iteration.
- **Planning board:** a GitHub Projects board with the columns *Backlog → Ready → In progress → In review → Done*.
- **One issue per task**, labelled with its work package (`WP1` … `WP5`) and assigned to a milestone (`M1` … `M6`).
- **Critical path first:** single link → multi-hop network → security layer (see [MILESTONES.md](MILESTONES.md)).
- **Measure and compare:** every measurement is stored with its run metadata in [`data/`](../data/); in WP5 the
  preliminary model is copied from the frozen archive [`poster/`](../poster/) to [`analysis/`](../analysis/), and each
  measured value replaces the corresponding assumption in that copy together with its source run.

### Definition of Done

A task is done when:

1. its code is merged into the milestone branch through a reviewed pull request;
2. all commits build and all tests pass (local hooks and CI);
3. the quality gate passes;
4. documentation is updated (README of the folder, docs if the design changed);
5. measurement data, if any, is committed with its `run.json`.

## Branching model

```
main ──────────────●────────────────────────────●──────────   (only finished milestones, tagged)
                    \                          /
milestone/m1-…        ●────●────●────●────●────●                (integration branch of one milestone)
                       \  /      \       /
m1/<topic>              ●●        ●──●──●                       (one branch per task)
```

- `main`: only finished, working milestones. Every milestone merge into `main` gets a tag (`m1-single-link`, …). The only
  other changes on `main` are urgent fixes, which are not tagged.
- `milestone/m<N>-<name>`: one integration branch per milestone, created from `main`. Only one milestone branch is
  active at a time (exception: M5 may run in parallel once its hardware arrives).
- `m<N>/<topic>`: one short-lived branch per task, created from the milestone branch, e.g. `m1/radio-tx`,
  `m1/gateway-uart`, `m1/logger-csv`.
- `fix/<topic>`: an urgent fix for `main`; after it is merged, `main` is merged into the active milestone branch.

**Merging**

| From → to | How | Why |
|---|---|---|
| `m<N>/<topic>` → `milestone/m<N>-…` | pull request, 1 approval, **Rebase and merge** | atomic, tested commits stay one by one in a linear history |
| `milestone/m<N>-…` → `main` | pull request when the milestone works as expected, **merge commit** (`--no-ff`), then tag | the milestone stays visible as one block; all history reaches `main` |
| `fix/<topic>` → `main` | pull request, 1 approval, **Rebase and merge** | small changes need no merge commit |
| `main` → `milestone/m<N>-…` | pull request, 1 approval, **merge commit** | the commits of `main` keep their hashes; a rebase would duplicate them |

Before opening a pull request, rebase the task branch on the latest milestone branch.

## Commits

- **Atomic:** one logical change per commit. A commit must build and pass the tests; **commit only when the tests are
  green.** Do not mix refactoring, formatting and behaviour changes in one commit.
- **Message:** `[TAG] short description in the imperative`, at most 72 characters in the first line.

  | Tag | Use |
  |---|---|
  | `[WP1]` … `[WP5]` | work on a work package |
  | `[MODEL]` | the copy of the preliminary model in `analysis/` (WP5); `poster/` itself is frozen |
  | `[DATA]` | measurement data (raw files are never edited afterwards) |
  | `[DOCS]` | documentation only |
  | `[CI]` | workflows, hooks, tooling |
  | `[FIX]` | a fix on `main` |

  Example: `[WP1] Send first LoRa frame from node to gateway`.
- **Review fixes:** a fix for an earlier commit of the task branch is made with `git commit --fixup <commit>`; the
  local hook accepts it, so the reviewer sees the change on its own. CI rejects `fixup!`/`squash!`/`amend!` commits, so
  before the merge they are folded into their commits with `git rebase -i --autosquash <milestone branch>`.
- **No large files:** files over 5 MiB are rejected (`scripts/check_file_size.py`); a file stays in the history even
  after it is deleted.
- **Frozen files:** CI rejects a pull request that changes `poster/` or a committed raw data file in `data/runs/` (new
  test runs may be added; [`scripts/check-frozen.sh`](../scripts/check-frozen.sh)). A deliberate change needs a pull
  request that first changes this rule.
- Never commit keys, build outputs or personal files (see [docs/key-management.md](../docs/key-management.md) and
  `.gitignore`).

## Interface contracts

The firmware, the gateway, the logger and the analysis are written by different people in parallel, so the interfaces
between them are fixed in contract documents: [frame-format.md](../docs/frame-format.md),
[serial-protocol.md](../docs/serial-protocol.md) and [data-model.md](../docs/data-model.md). Shared design decisions
are listed in [decisions.md](../docs/decisions.md).

- Code follows the contract. If something is missing or open, the contract is completed first; code does not assume
  an answer.
- A contract changes only through a pull request that updates the contract document and its row in `decisions.md`
  (decision and reason). The pull request needs the approval of **two** team members, among them one who works on
  the other side of the interface.
- An open decision is decided the same way.

## AI coding agents

Rules for AI agents are in [AGENTS.md](../AGENTS.md); Claude Code reads it through `CLAUDE.md`, GitHub Copilot and
Antigravity read it directly. [`.claude/settings.json`](../.claude/settings.json) additionally stops Claude Code from
reading `secrets/` and from skipping the hooks. This is a convenience, not a protection: other tools, and commands such
as `grep -r` or a script that opens files itself, are not covered. The protection is the same for everyone: the hooks,
CI and the ruleset.

## Tests

| Part | Tests | Where they run |
|---|---|---|
| Python tools (logger, analysis) | `pytest` | pre-commit hook, CI |
| Firmware logic without hardware (frame encoding, nonce, replay window, duty-cycle accounting, airtime) | host unit tests | pre-commit hook, CI |
| Firmware build for the STM32WLE5 | cross-compiler build | CI |
| Behaviour on the boards | manual test run, recorded in `data/` | on the bench |

[`scripts/test.sh`](../scripts/test.sh) runs every automatic check that applies to the files in the repository.

## Local set-up

Install first:

| System | Needed |
|---|---|
| Windows | [Git for Windows](https://git-scm.com/download/win) (includes Git Bash) and Python 3.12 or newer |
| macOS | Git (Command Line Tools) and Python 3.12 or newer (the system `python3` of macOS is older) |
| Linux | Git and Python 3.12 or newer with the `venv` module (on Debian/Ubuntu the package `python3-venv`) |

Then, once per clone, in a terminal (**Git Bash** on Windows):

```bash
bash scripts/setup.sh     # creates .venv, installs the check tools, enables the git hooks
bash scripts/test.sh      # runs all checks
```

The hooks and scripts find `.venv` by themselves; it does not have to be activated. Another interpreter can be named in
the `PYTHON` environment variable. Firmware host tests will also need CMake and a C compiler; the tools and their
versions are fixed together with the first firmware code.

- `pre-commit` hook: runs `scripts/test.sh` on a copy of the **staged** files, so unstaged changes do not hide errors;
  the commit is not made if a check fails. The slower end-to-end tests of the hooks run only when `.githooks/` or
  `scripts/` change; CI always runs them.
- `commit-msg` hook: checks the message format (`fixup!` commits are allowed locally, see *Commits*).
- `pre-push` hook: runs the secret check and the file size check on the files of **every commit that is new to the
  remote**, also commits made by rebase, cherry-pick, merge or with `--no-verify`. CI runs only after a push; a key that
  reaches a public repository has to be replaced, even if it is deleted at once.
- Editor: **SonarQube for IDE** (formerly SonarLint) in VS Code or STM32CubeIDE/Eclipse, in connected mode with the
  project on SonarQube Cloud, so that the editor shows the same issues as the quality gate.

Hooks can be skipped with `--no-verify`; CI repeats every check, so a skipped hook only moves the failure to the pull
request.

## CI/CD and the quality gate

| Workflow | Runs on | Checks |
|---|---|---|
| `ci.yml` | every pull request; pushes to `main` and `milestone/*` | `scripts/test.sh` (secret check, file size check, ruff lint and format, pytest, host tests), gitleaks secret scan, SonarQube Cloud analysis; set-up, checks and hooks on Linux, Windows and macOS |
| `commits.yml` | every pull request | frozen files unchanged; message format **and** `scripts/test.sh` for **each commit** in the pull request |
| `poster.yml` | manual only | re-runs the archived model and builds the poster PDF (artifact); reproducibility diff of `poster/results/` (report only) |
| `firmware.yml` | added with the first firmware code | host unit tests, cross-compiled build, static analysis, firmware binaries built with the all-zero key template (artifact) |
| `release.yml` | milestone tags | GitHub release with generated notes; firmware binaries are attached once the firmware workflow exists |

**Quality gate.** SonarQube Cloud analyses every pull request and reports a "Quality Gate" status (check
`SonarCloud Code Analysis`). A GitHub ruleset on `main` and `milestone/*` requires a pull request with one approval,
the checks `ci`, `commits`, the three `setup` checks (later also `firmware`) and the quality gate, and forbids force
pushes and branch deletion. Code that does not pass cannot be merged. Pushes to task branches are not blocked by
quality on GitHub.com; the gate applies when the branch is merged.

**Action versions.** GitHub's own actions (`actions/*`) are used by major version; third-party actions are pinned to a
commit SHA with the version in a comment. There is no automatic update: when GitHub warns about an action (for example a
deprecated runtime) or a new version is needed, a `[CI]` pull request updates it.

**Deployment.** The firmware is flashed onto the boards by hand with the ST-LINK/V2; the steps are in
[`firmware/`](../firmware/). A release collects the binaries of a milestone.

## One-time repository set-up (maintainer)

1. Repository visibility: public.
2. SonarQube Cloud: sign in with GitHub, import the repository, choose CI-based analysis, add the token as the
   repository secret `SONAR_TOKEN`, set the repository variable `SONAR_ENABLED=true`, and check that
   `sonar-project.properties` matches the project and organization keys. Adjust the quality gate if the default
   coverage condition does not fit firmware code.
3. Ruleset for `main` and `milestone/*`: require a pull request (1 approval), required status checks, block force
   pushes. Allow *Rebase and merge* and *Merge commit*; disable *Squash and merge*.
4. Create the milestones M1–M6, the labels `WP1`–`WP5` and the Projects board.
5. Under the code security settings, check that secret scanning and push protection are enabled, and enable private
   vulnerability reporting ([SECURITY.md](../SECURITY.md)).
6. Add the team members as collaborators; every member enables two-factor authentication.
