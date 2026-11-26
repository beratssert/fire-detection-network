# Work plan

The project is divided into work packages over at most 12 months. The order of the milestones and their progress are
tracked in [management/MILESTONES.md](../management/MILESTONES.md).

## WP1 — Single link and logging infrastructure

Preparation of the node boards and sensors and set-up of the software development environment; sending the first frame
from a single node to the gateway; the gateway writes the time stamp, source, hop count, RSSI, SNR and authentication
result of every frame to a file on the laptop; temperature/humidity sampling (1 min) and gas sensor sampling (5 min) and
sending an alarm when a threshold is exceeded; comparison of the frame airtime with the calculation and the first current
profiles of the node in its operating states; definition, with the supervisor, of the campus and laboratory measurement
method and of the safety rules for the small, controlled gas/smoke source; preparation, through the supervisor and with a
university letter, of the permit application for the forest measurements.

## WP2 — Multi-hop network

The nodes carry alarms and hourly heartbeats to the gateway over at least two hops using periodic short listen slots
(synchronous listening); the 1 % duty-cycle limit in the 868.0–868.6 MHz band is checked from the transmission log; the
clock drift between node pairs is measured and the guard window is set from the measured drift; the 3–5 node network
runs for 24 hours.

## WP3 — Security layer

Implementation of keys derived from the master key for every node; frames with an 8-byte authentication tag in AES-256
CCM mode; the nonce generated from the counter, the epoch and the node ID; the replay window at the gateway; and writing
the epoch to non-volatile memory at every start-up. Tests with forged, modified and replayed frames; measurement of the
airtime and energy overhead of security.

## WP4 — Measurement campaigns

On a green area of the campus and in the laboratory: measurement of path loss and delivery ratio at at least 5 distances
with at least 100 frames per point, at two data-rate settings and in two placements (on the trunk at 2.5 m height and at
ground level); measurement of per-hop and end-to-end delay from at least 200 alarms; current measurement with the power
profiler over one heartbeat hour; recording of the gas sensor response to the small, controlled source. If permission is
obtained, the radio measurements are repeated in a *Pinus brutia* stand.

## WP5 — Comparison of measurements and assumptions

Every measured quantity is tabulated next to the value assumed in the team's preliminary analyses; the measured values
are entered into the parameter file and the node-density and battery-life estimates are recalculated; the assumptions
that were not confirmed and the reasons for the differences are reported; the measurement data and analysis code are
organised.

## Mapping to objectives

| Work package | Objectives |
|---|---|
| WP1 | 1 |
| WP2 | 2 |
| WP3 | 3 |
| WP4 | 4, 5, 6, 7 |
| WP5 | 8 |

## Fallback plans named in the method

| Risk | Fallback |
|---|---|
| The hardware AES unit does not support CCM | A software library is used and the AES cost is reported separately. |
| The power profiler cannot be obtained in time | A shunt resistor and an oscilloscope are used. |
| No permission for forest measurements (stage B) | Stage A (campus and laboratory) is sufficient to complete the project; forest-specific values remain marked as assumptions. |
