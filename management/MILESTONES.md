# Milestones

Milestones are ordered by what the hardware in hand allows, so that each one can be finished and merged before the next
starts (see [WORKFLOW.md](WORKFLOW.md#branching-model)). The work packages (WP1–WP5) are defined in
[docs/work-plan.md](../docs/work-plan.md).

| # | Milestone | Content | WP / objectives | Hardware needed | Status | Due / tag |
|---|---|---|---|---|---|---|
| M0 | Preparation and design | Preliminary model and poster, project proposal, midterm report, TÜBİTAK 2209-A application, hardware ordered, delivered and soldered | — | — | done | — |
| M1 | Single link and logger | Toolchain; first flash; first frame from a node to the gateway; gateway logs every frame over USB (time stamp, source, hop count, RSSI, SNR, authentication result); quick check that the frame airtime agrees with the calculation (not a formal measurement); sensor interface with a simulated source and the alarm threshold logic | WP1 (part) / 1 | in hand | in progress | 11.12.2026, `m1-single-link` |
| M2 | Multi-hop network | Synchronous listen slots; at least two hops; duty-cycle check from the transmission log; clock drift between node pairs (ppm); guard window; 3–4 boards running for 24 h | WP2 / 2 | in hand | planned | `m2-multi-hop` |
| M3 | Security layer | Per-node derived keys; AES-256-CCM with 8-byte tag (software library if the hardware unit does not fit); counter/epoch/node-ID nonce; replay window; epoch written at start-up; ≥ 1,000 forged, modified and replayed frames sent from the fourth board; airtime overhead | WP3 / 3 | in hand | planned | `m3-security` |
| M4 | Radio and timing measurements (stage A) | Frame airtime measured on the board and compared with the calculation (moved from WP1); path loss and delivery: ≥ 5 distances, ≥ 100 frames per point, 2 data rates, 2 placements; delay from ≥ 200 alarms; drift; repeated in a *Pinus brutia* stand if permitted | WP4 (part), WP1 airtime / 1, 4, 5 | in hand | planned | `m4-radio-timing` |
| M5 | Sensors and energy | Temperature/humidity (1 min) and gas (5 min) sampling; alarm on threshold; current profiles in every operating state (moved from WP1); gas sensor response to a small, controlled source; security energy overhead | WP1, WP4 (rest) / 1, 6, 7 | **sensors and power profiler (or shunt + oscilloscope)** | blocked: hardware | `m5-sensors-energy` |
| M6 | Measurements vs assumptions | Preliminary model copied from the frozen `poster/` to `analysis/`; measured values into its parameter file; node-density and battery-life estimates recalculated; comparison tables; unconfirmed assumptions; paper draft | WP5 / 8 | — | planned | `m6-comparison` |

**Deviation from the TÜBİTAK work plan.** WP1 in [docs/work-plan.md](../docs/work-plan.md) also contains the first
airtime and current measurements. Here they are moved to the measurement milestones: the formal airtime measurement to
M4 and the current profiles to M5. Reasons: a current measurement is not possible with the hardware in hand, and
measurements taken before the firmware is stable would have to be repeated (for example, the frame grows from 19 B to
27 B when the authentication tag is added in M3). M1 keeps only a quick airtime check to catch configuration errors
early. This deviation is to be explained to the supervisor and in any TÜBİTAK progress report.

Status values: planned, in progress, blocked, done. Update this table when a milestone starts or is merged into `main`.
