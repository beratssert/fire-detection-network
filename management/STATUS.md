# Status

_Last updated: 25.11.2026. Update this file at every supervisor meeting._

## Now

- **Active milestone:** M1 single link and logger, target 11.12.2026 (set for the supervisor meeting on 27.11.2026).
- **Done so far:** preliminary model and poster; project proposal; midterm report; TÜBİTAK 2209-A application;
  hardware ordered, delivered and soldered; development plan (single link → multi-hop network → security layer).
- **Next supervisor meeting:** 27.11.2026.

## Hardware

| In hand | Missing |
|---|---|
| 4 × Seeed Wio-E5 mini (STM32WLE5JC) | temperature/humidity sensor |
| 1 × ST-LINK/V2 programmer (clone) | gas/VOC sensor |
| | power profiler (fallback: shunt resistor + oscilloscope) |

The missing parts are not planned for the near term. Milestones M1–M4 need only the hardware in hand; M5 waits for
the sensors and a way to measure current ([MILESTONES.md](MILESTONES.md)).

## Open points

- First flash: check whether the clone ST-LINK/V2 works with the STM32WLE5 and whether the factory firmware of the
  Wio-E5 is read-protected; record the procedure in [`firmware/`](../firmware/).
- TÜBİTAK 2209-A: decision pending (as of 30.10.2026).
- Forest measurements (stage B): permit request to be prepared through the supervisor.
- Measurement method and safety rules for the small, controlled gas/smoke source: to be defined with the supervisor.
