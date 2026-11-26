# How the preliminary results are computed

The model answers one question: **how sparse can a forest-fire sensor network be?** It chains seven sub-models. Each
one reads its inputs from [`params.py`](params.py) and writes a CSV to [`results/`](results/). All numbers below are taken
from those CSVs (through [`results/macros.tex`](results/macros.tex)); none is a field measurement.

## Pipeline

```
params.py ──> models.py ──> range.csv, connectivity.csv, detection.csv, security.csv
          ──> reqdens.py ─> required_density.csv, sensitivity_adv.csv
              latency.py ─> latency.csv        (reads connectivity.csv)
              energy.py ──> energy.csv         (reads connectivity.csv)
              cost.py ────> cost.csv           (reads required_density.csv, energy.csv, connectivity.csv)
              macros.py ──> macros.tex         (every number printed on the poster)
              figures.py ─> figures/f1–f5
tests/check_model.py: independent re-derivation of the main outputs
```

Two deployments are modelled: **trunk-mounted** nodes at 2.5 m (`M`) and **scattered** nodes on the forest floor (`S`).
Each has an optimistic and a conservative radio scenario.

## 1. Radio range (`models.py`, `range.csv`)

Log-distance path loss with log-normal shadowing at 868 MHz:

  PL(d) = PL(1 m) + 10 · n · log10(d / 1 m) + X,  X ~ N(0, σ)

with PL(1 m) = 31.2 dB (free space). A link works if PL(d) ≤ P_TX − S_SF + G_ant + detuning, with P_TX = 14 dBm,
S_SF the SX1262 sensitivity for each spreading factor and G_ant = −4 dB (two antennas of −2 dBi). The **90 % link
range** keeps a margin of 1.28 σ.

| Scenario | n | σ (dB) | Basis |
|---|---|---|---|
| trunk, conservative | 4.0 | 8.7 | n assumed; σ from ITU-R P.833-10 forest measurements |
| scattered, optimistic / conservative | 4.0 / 4.5 | 6.0 / 8.7 | n assumed; −2 dB near-ground detuning assumed |
| trunk, upper bound | 3.22 | 6.0 | n from a 923 MHz forest link to an 8 m gateway (Boonlom et al. 2026); not used for network results |

Result (90 % range at SF7, SF12 in brackets): trunk-mounted 200 m (410 m), conservative; scattered 100–210 m
(190–450 m); upper bound 900 m (2280 m). No 868 MHz path-loss data for *Pinus brutia* were found, which is why the
prototype measures n and σ (Hypothesis 1).

## 2. Multi-hop connectivity (`models.py`, `connectivity.csv`)

Monte Carlo over a 400 ha square: nodes are a Poisson field of density λ, with G = 1 gateway at the centre or G = 4 at
the quadrant centres. Every node pair gets its own shadowing draw; a link exists if its loss fits the budget. A
breadth-first search from the gateways gives the share of nodes with a multi-hop path and the hop counts; a random
shortest-path tree gives the load carried by each first-hop relay.

Result: the lowest density at which the lower 95 % confidence bound of the reached share is ≥ 95 % (SF7):
trunk-mounted 0.3/ha (conservative), scattered 0.2–0.5/ha.

## 3. Detection (`detect.py`, `detection.csv`, `required_density.csv`)

A point ignition grows as a disc at constant speed v (surface fire spread in young *Pinus brutia*: 0.3–3.75 m/min,
Küçük et al. 2012; base 1 m/min). A node at distance r detects:

- by **heat** when the fire edge is within r_T (1–5 m, assumed), sampled every 1 min;
- by **gas**, only inside the downwind sector of half-angle θ = 30°, when the edge is within r_G (25–100 m, assumed),
  sampled every 5 min plus the 92 s BME688 response time.

For one node, the detection probability by time T is
p_X(r) = clip((T − t_X − max(r − r_X, 0)/v) / T_s,X, 0, 1).
For a Poisson field, the expected number of detecting nodes is λ·I(T) with

  I(T) = ∫₀^∞ [(1 − θ/π) p_T + (θ/π)(1 − (1 − p_T)(1 − p_G))] 2πr dr,

so P(detected by T) = 1 − exp(−λ I(T)) and 90 % detection needs λ = ln 10 / I(T). This integral is computed exactly
(no Monte Carlo).

Result: for 90 % of fires detected within 15 min at 1 m/min, **3.2–17 nodes/ha with gas sensing** (r_G = 100–25 m) and
**19–30 nodes/ha with heat only** (r_T = 5–1 m), while the radio mesh is already connected at 0.5 nodes/ha:
**sensing reach, not radio range, sets the density.** r_G is the most sensitive and least known input.

## 4. Alarm delay (`latency.py`, `latency.csv`)

Nodes listen once per synchronous slot T_w = 2–30 s (assumed). Each hop costs a wait U(0, T_w) plus the frame airtime.
With the 95th-percentile hop count at 5 nodes/ha (conservative radio), the worst-case wait is 5–70 s (trunk) and
8–120 s (scattered) with G = 1. The 1 % duty cycle of the 868.0–868.6 MHz band is checked against the busiest relay.

## 5. Energy (`energy.py`, `energy.csv`)

Average current = sleep + own hourly heartbeat + listening (one channel-activity check per slot) + hourly sync beacon
+ relaying + sensor sampling. Currents come from datasheets (SX1262, STM32WLE5, BME688) or are assumed.
Result (scattered, conservative radio, G = 1, 25 °C): heat-only leaf 14–40 µW, 15–33 years on one Li-SOCl₂ AA;
gas leaf 337 µW, 2.0 years; the busiest first-hop relay 700 µW. The listen-slot clock drift is not yet in the budget.

## 6. Security overhead (`models.py`, `security.csv`)

Frame = 12 B data + 7 B header + authentication tag. At SF7 the alarm frame takes 51.5 ms without a tag and 66.8 ms with
the 8-byte tag (LoRa time-on-air formula, Semtech AN1200.13) — Hypothesis 3 of the project.
Timing: two nodes with ±20 ppm clocks drift apart by up to 2 × 20 ppm × 3600 s = 144 ms per hourly sync, more than the
12.5 ms SF7 preamble — Hypothesis 2.

## 7. Cost (`cost.py`, `cost.csv`)

Capital cost per hectare (nodes, gateways, installation) and a 10-year total, from the required densities and the
energy results; prices are retail listings or estimates (USD), not quotes.

## Checks

[`tests/check_model.py`](tests/check_model.py) re-derives the main outputs (time on air, ranges, energy, latency, cost,
frame sizes, limitation numbers) with its own code from `params.py` and compares them with the CSVs.

## What the prototype will replace

| Assumed in the model | Measured in the project |
|---|---|
| path-loss exponent n, shadowing σ | WP4: ≥ 5 distances, ≥ 100 frames per point, 2 data rates, 2 placements |
| listen-slot timing, ±20 ppm drift | WP2: drift between node pairs (ppm), guard window |
| per-hop delay U(0, T_w) + airtime | WP4: ≥ 200 alarms |
| node currents from datasheets | WP1/WP4: power profiler, every operating state |
| airtime of authenticated frames | WP1/WP3: on the board |
| gas reach r_G, response 92 s | WP4: response to a small, controlled source only (real fire size is out of scope) |
