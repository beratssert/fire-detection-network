# Design decisions

One row per decision that more than one team member depends on: the interface contracts between firmware, gateway,
logger and analysis, and the shared tools. An open decision is filled in by a pull request that also updates the
document it affects; the rules are in [WORKFLOW.md](../management/WORKFLOW.md#interface-contracts). Until a decision is
made, code must not assume an answer.

| ID | Decision | Affects | Status | Decision and reason | Pull request |
|---|---|---|---|---|---|
| D1 | Python version for new code | logger, analysis, scripts | decided | Python 3.12; `poster/` stays on 3.9 with its pinned packages. 3.9 is no longer supported. | initial set-up |
| D2 | Merge method of pull requests | everyone | decided | *Rebase and merge*: atomic, tested commits stay one by one in a linear history. | initial set-up |
| D3 | Test run ID format | logger, analysis, `data/` | decided | `<UTC start>_<site>_<number>` ([data-model.md](data-model.md)); allowed as a folder name on every system. | initial set-up |
| D4 | Byte layout and byte order of the 12-byte data field | firmware, logger | open | | |
| D5 | Bytes authenticated as associated data (AAD) in AES-256-CCM | firmware, logger | open | | |
| D6 | Key derivation function (master key + node ID → node key) | firmware, gateway, key tools | open | | |
| D7 | How keys are loaded onto the boards and the gateway | firmware, key tools | open | | |
| D8 | Format and authentication of the synchronisation beacon | firmware | open | | |
| D9 | Gateway → laptop serial protocol | gateway firmware, logger | open | | |
| D10 | Format and location of shared test vectors | firmware tests, logger tests | open | | |
| D11 | Types and units of the `frames.csv` columns and `run.json` fields | logger, analysis | open | | |
| D12 | Firmware build system and tool versions | firmware, CI | open | | |

Status values: open, decided, replaced (by a newer row; the old row stays).
