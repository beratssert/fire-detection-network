# Project description

Sources are listed in [references.md](references.md).

## Significance

Forest fires in the Mediterranean belt are a serious problem for Türkiye. The 2021 Manavgat fire burned about
60,000 ha, started at four separate points, and took ten days to two weeks to bring under control (Ekberzade et al.,
2025). Türkiye monitors its forests with 776 lookout towers, 184 of which are operated as smart towers, and the average
first-response time is reported as 11 minutes (T.C. Tarım ve Orman Bakanlığı, 2025). The satellite-based MODIS sensor
routinely detects fires of about 1,000 m², only at satellite overpass times, and its probability of detecting fires
under tree cover remains very low (Giglio et al., 2021). Tower and camera systems notice the fire only after the smoke
has become visible from a distance. What is missing is the first minutes, while the fire is still small and under the
canopy.

In some fire types, especially in the pyrolysis and smouldering phase, gases and volatile organic compounds are
released before visible smoke (Fonollosa et al., 2018). Gas sensors at ground level can therefore report the fire in
the first minutes, before visible smoke forms (Khan et al., 2022). However, for the forests of Türkiye it is uncertain
how many nodes this approach needs, how long the batteries last, how fast the alarm arrives and what protection against
the injection of forged or replayed alarms costs. Analytical studies relate the number of sensors to the detection time
(Fierens, 2009), but they rest on simplifying assumptions such as a constant fire spread rate and detection only when
the fire reaches the sensor position, whereas the detection distances measured in the field vary widely from study to
study. In experiments with hydrogen sensors in a forest, a smouldering fire of about 2 m² produced a clear signal at
sensors 25 m and 105 m away, but detection depended strongly on the wind direction (Nörthemann et al., 2013). In a
machine-learning-supported sensor network study, a 5 m sensing range of the node was reported as the result of many
trials, without measurement details (Dampage et al., 2022). To our knowledge, no measured data exist for 868 MHz radio
path loss, clock drift between nodes, the real current consumption of a node or the authentication overhead in a
Calabrian pine (*Pinus brutia*) forest.

In our team's preliminary analyses, if 90 % of fires are to be detected within 15 minutes and the spread rate is
1 m/min (surface fire spread rates of 0.3–3.75 m/min were measured in young *Pinus brutia* stands (Küçük et al., 2012)),
3.2–17 nodes per hectare are needed with gas-sensing nodes and 19–30 nodes per hectare with heat-only nodes. The radio
network, on the other hand, becomes connected at 0.5 nodes per hectare. Because these results rest on unmeasured
assumptions, a wrong assumption could be carried unchanged into a real deployment.

## Research question

When the key performance parameters of a low-power, authenticated, multi-hop sensor network prototype — link loss,
packet delivery ratio, per-hop delay, clock drift, current consumption, security overhead and gas sensor response —
are measured on real hardware, how far do they agree with the values assumed in the preliminary analyses, and how does
the difference change the estimates of node density and battery life?

## Hypotheses

- **Hypothesis 1.** The path-loss exponent under tree cover is clearly higher than in open terrain.
- **Hypothesis 2.** The clock drift is large enough to require a guard time in synchronous listen slots.
- **Hypothesis 3.** An 8-byte authentication tag increases the airtime of an alarm frame from about 51.5 ms to
  66.8 ms, but the duty-cycle limit is respected.

## Relation to priority areas

The topic is directly related to "disaster management technologies" and the "Internet of Things" in TÜBİTAK's list of
priority areas, and, because the alarm frames are authenticated, also to "cyber security". The measured inputs will
give forest administrations and network designers estimates of node count, battery life and alarm delay that rest on
measurement rather than on vendor claims.

## Aim and objectives

The aim of the project is to develop a small prototype of a low-power, authenticated, multi-hop wireless sensor network
designed for the early detection of forest fires, and to measure its key performance quantities — link quality, delay,
energy consumption, security overhead and gas sensing response — on real hardware, so that the node-density and
battery-life estimates, which so far rest on assumptions, are tested against measured values.

| # | Objective | Success criterion |
|---|---|---|
| 1 | Build a prototype network of 3–5 sensor nodes and 1 gateway with long-range, low-power radios in the 868 MHz band and temperature/humidity and gas sensors. | — |
| 2 | Implement a synchronous relay protocol that carries alarms and hourly heartbeats to the gateway over at least two hops, within the 1 % duty-cycle limit of the 868.0–868.6 MHz band. | The node – relay – gateway path runs without interruption for 24 hours, and the delivery ratio is reported together with the numbers of sent and received frames. |
| 3 | Implement a security layer in which every frame is protected with per-node derived keys and AES-256-CCM with an 8-byte authentication tag, and the gateway has a replay window. | None of at least 1,000 forged, modified and replayed frames is accepted, while valid frames are accepted. |
| 4 | Measure radio path loss and packet delivery at at least 5 distances, with at least 100 frames per point, at two data-rate settings and in two placements (trunk-mounted at 2.5 m height and at ground level); compute the path-loss exponent and the shadowing value with confidence intervals. | — |
| 5 | Measure the per-hop delay distribution from at least 200 alarms and the clock drift between node pairs in ppm. | — |
| 6 | Measure the current of the node in each operating state with a power profiler and compute the battery life of a heat-only leaf node from these measurements. | — |
| 7 | Record the response of the gas sensor (response time and signal change) to a small, safe and controlled source. | — |
| 8 | Put every measured quantity next to the value assumed in the team's preliminary analyses, recalculate the node-density and battery-life estimates with the measured values, and report which assumptions were not confirmed. | — |

The project will be considered successful based on the honest and complete reporting of the measurements.

## Outputs, impact and benefits

**Scientific/academic outputs.** At least one paper with the measurement data and the comparison of measurements with
assumptions will be prepared from the project results and submitted to a national or international peer-reviewed
journal or conference. The paper will present the radio path loss, per-hop delay, clock drift between nodes, node
current, and the airtime and energy overhead of authenticated frames measured in a *Pinus brutia* forest and on campus,
compared with the assumptions of the team's preliminary analyses. A final project report with all technical details and
measurement results will also be prepared. Publishing measured values will give a basis to the assumption-based work in
this field.

**Economic/commercial/social outputs.** A working prototype network (3–5 sensor nodes and 1 gateway), the node and
gateway software, the frame logging tool, raw measurement data, field notes and analysis code will be shared in an open
code repository. These outputs will allow forest administrations and network designers to base estimates of node
count, battery life and alarm delay on measured values rather than on vendor claims. With these measured inputs, the
social benefit of early fire warning for forest and environmental safety can be planned more realistically. No
commercial product, patent or utility model output is foreseen.

**Outputs towards new projects.** The measured values and the assumptions that could not be confirmed will be the
starting point for a larger field trial with many nodes in a forest. At the end of the project, the aim is to prepare a
project idea based on estimates updated with measured inputs, in cooperation with forest administrations, which could be
submitted to a national R&D support programme. In addition, the response of the gas sensor as a function of real fire
size is out of scope in this project and will be reported as an open research question for a follow-up project.
