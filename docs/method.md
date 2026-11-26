# Method

Sources are listed in [references.md](references.md).

## Research design

The study is an experimental, measurement-based prototype study. First the link between a single node and the gateway
is established, then the multi-hop network, and last the security layer; this keeps the critical path short and allows
measurements at every stage. All nodes run the same software, and the role (leaf node, relay, gateway) is set by
configuration. The prototype consists of node boards with a microcontroller, a long-range low-power 868 MHz radio and a
hardware AES unit on one chip, a temperature/humidity sensor and a gas/volatile-organic-compound sensor. The gateway is
connected to a laptop over USB, and for every received frame the time stamp, source, hop count, RSSI and SNR values and
the authentication result are written to a file.

## Communication protocol

Alarms and hourly heartbeats are carried to the gateway over at least two hops through synchronous listen slots, in
which the nodes listen periodically for a short time. Each node operates in the 868.0–868.6 MHz band within the maximum
of 25 mW e.r.p. allowed in this band (with a transmitter output of about 14 dBm, taking the antenna gain into account)
and transmits at most 36 seconds in a one-hour observation window (1 % duty cycle) (Bilgi Teknolojileri ve İletişim
Kurumu, n.d.; ETSI, 2017; ETSI, 2018). The expected per-hop delay is predicted as a uniform distribution over the listen
slot plus the airtime of the frame; the measurements will be compared with this prediction.

## Security layer

Each frame consists of a 7-byte header (node ID, epoch byte, counter), 12 bytes of data and an 8-byte authentication
tag. Node keys are derived from a master key with the node ID (Zhu et al., 2006); frames are protected with AES-256 in
CCM mode (Dworkin, 2004), and the nonce is generated from the counter, the epoch and the node ID. The gateway applies a
counter window against replay attacks, and the epoch is written to non-volatile memory at every start-up. If the
hardware AES unit does not support CCM, a software library is used and the AES cost is reported separately.

## Variables

**Independent variables:** distance between node and gateway (at least 5 different values); node placement (on the
trunk at 2.5 m height and at ground level); radio data-rate setting (fastest and slowest setting); number of hops (1 and
2); listen-slot duration (2–30 s); presence or absence of the authentication tag in the frame; type of frame sent
(valid, forged, modified, replayed).

**Dependent variables:** path loss, RSSI and SNR, packet delivery ratio, per-hop and end-to-end delay, clock drift between
node pairs (ppm), current and average power in each operating state, airtime of the frame, number of forged frames
accepted by the gateway, response time and signal change of the gas sensor.

## Measurements

Measurements are made first on a green area of the campus and in the laboratory (stage A) and, if permission can be
obtained, in a *Pinus brutia* stand (stage B). Stage A is sufficient to complete the project; if stage B cannot be done,
the forest-specific values remain marked as assumptions. Smoke and gas response is tested only with a very small, safe
and controlled source, outdoors or in a ventilated room; the method and the safety rules are approved with the
supervisor and under the department's laboratory rules. No real fire experiment is carried out. Current measurements
are taken with a power profiler over one heartbeat hour; if the profiler cannot be obtained in time, a shunt resistor
and an oscilloscope are used.

## Statistical methods

- **Path loss** is fitted to the log-distance model with log-normal shadowing by least-squares regression; the
  path-loss exponent and the standard deviation of the shadowing are given with 95 % confidence intervals and compared
  with the range of the team's preliminary analyses (exponent 4.0–4.5; shadowing 6.0–8.7 dB).
- **Packet delivery ratio:** Wilson confidence interval.
- **Delay:** mean, median and 95th percentile from at least 200 alarms; the agreement of the measured distribution with
  the predicted distribution is tested with the Kolmogorov–Smirnov test.
- **Clock drift** is computed in ppm from the slope of a linear regression on the difference of the time stamps of two
  nodes.
- **Battery life** is obtained from the average power, found by multiplying the measured currents by the durations of
  the states and summing.
- **Security test:** if none of at least 1,000 forged, modified and replayed frames is accepted, then by the "rule of
  three" the probability of a false acceptance is below about 0.3 % with 95 % confidence.

Measurements are repeated at every installation, and the results are shared together with the raw data in an open
repository.

## Preliminary work

Our team has previously developed preliminary analysis software that calculates node density, the radio network,
detection time and energy together for *Pinus brutia* forests ([`poster/`](../poster/)). This software collects its
inputs in a single parameter file and labels each input as measured, manufacturer's claim or assumption. In that work it
was calculated that the 8-byte tag increases the airtime of an alarm at SF7 from 51.5 ms to 66.8 ms, and that a drift of
144 ms per hour between two nodes stays larger than the 12.5 ms preamble; therefore the timing of the listen slots will
be solved experimentally in this project. Every measured value will replace the corresponding assumption in the parameter
file, and the preliminary analyses will be run again.

## Relation to the work packages

The method is divided into five work packages: WP1 single link and logging infrastructure (first airtime and current
measurements); WP2 multi-hop network, clock drift and guard window; WP3 security layer and tests with forged frames; WP4
measurement campaigns (path loss, delay, energy, gas sensor response); WP5 comparison of the measurements with the
preliminary analyses and recalculation of the estimates. WP1, WP2 and WP3 serve objectives 1–3 respectively, WP4 serves
objectives 4–7, and WP5 serves objective 8. See [work-plan.md](work-plan.md).
