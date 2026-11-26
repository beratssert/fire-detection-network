"""
Single source of model parameters for models.py, reqdens.py and figures.py.

Pure constants: no numpy, no random numbers, no I/O. Importing this module must
not change the global RNG stream in models.py (SEED is only stored here).

Values and expressions are copied verbatim from the baseline scripts (tag
baseline-v1), including values that REVIEW.md flags as wrong or unverified;
fixing them is a separate step. Expressions keep their original operand order
so that floats stay bit-identical.

Labels
  SOURCE           a source is named in a comment (not independently verified)
  ASSUMPTION       no source given
  UNVERIFIED(#n)   REVIEW.md lists it as unverified or wrong (item number)
  DERIVED          computed from other constants
  UNUSED           defined in the baseline but never used; kept on purpose
  FIG-INDEPENDENT  typed into a figure by hand, not read from the model
"""
import math

# ------------------------------------------------------------------ #
# 0. REPRODUCIBILITY
# ------------------------------------------------------------------ #
SEED = 2026                 # ASSUMPTION; models.py builds its rng from this
REQDENS_UNUSED_SEED = 7     # UNUSED (#28): reqdens.py creates rng(7) but never draws from it

# ------------------------------------------------------------------ #
# 1. RADIO: link budget and LoRa time on air
# ------------------------------------------------------------------ #
F_MHZ      = 868.0                          # SOURCE: ETSI EN 300 220 band
PL0_DB     = 20*math.log10(F_MHZ) - 27.55   # DERIVED: free-space loss at 1 m = 31.2 dB
TX_DBM     = 14.0       # UNVERIFIED (REVIEW §9 [20]): "ETSI EN 300 220 band M: 25 mW e.r.p."
ANT_GAIN_DBI = -2.0     # ASSUMPTION: cheap antennas, -2 dBi each end
N_ANT        = 2        # ASSUMPTION: one antenna at each end of the link
ANT_DB     = ANT_GAIN_DBI * N_ANT           # DERIVED: -2.0 * 2
DETUNE_DB  = -2.0       # ASSUMPTION: near-ground detuning (M1: now per scenario in RADIO[...]["detune_db"]; kept for reference)
SIGMA_DB   = 6.0        # UNVERIFIED (§9 [23], #28): shadowing; Wu et al. 2020 (~5 dB); M1: used only by the old connectivity block until M2
FADE_Q     = 1.28       # DERIVED: 90 % link reliability margin = 1.28 sigma
SENS_SF7_DBM  = -124.0  # SOURCE: SX1261/2 DS Rev 1.2, Table 3-8 (BW 125 kHz, Rx Boosted gain); RESEARCH R2
SENS_SF12_DBM = -137.0  # SOURCE: SX1261/2 DS Rev 1.2, Table 3-8 (BW 125 kHz, Rx Boosted gain); RESEARCH R2
# DERIVED (M1): SF8-11 are not in the SX1262 datasheet; linear interpolation between SF7 and SF12
SENS = {sf: SENS_SF7_DBM + (SENS_SF12_DBM - SENS_SF7_DBM) * (sf - 7) / 5 for sf in range(7, 13)}
# M1: radio scenarios = deployment (M: hand-mounted on trunks at TRUNK_H_M; S: scattered from the air,
# ground or low branches, random height) x radio assumption (opt: optimistic, cons: conservative).
# No 868 MHz path-loss measurement for P. brutia / Mediterranean pine was found (RESEARCH R1: NOT FOUND),
# so every value below is either borrowed from a different frequency/forest (SOURCE, mismatch noted) or an ASSUMPTION.
TRUNK_H_M = 2.5            # ASSUMPTION: trunk mounting height (Dryad states tree/pole mounting; height not on its page)
RADIO = {
    # key: (deploy, scen) -> n (path-loss exponent), sigma_db (log-normal shadowing), detune_db (near-ground
    # antenna detuning, added to the budget), rear_db (extra loss when the link leaves through the node's own trunk)
    ("M", "opt"):  dict(n=3.22, sigma_db=6.0, detune_db=0.0,  rear_db=5.0),   # n: SOURCE Boonlom 2026 (923 MHz, tropical forest, Tx 1.7 m / GW 8 m); sigma: UNVERIFIED Wu 2020 (~5 dB, NOT_ACCESSIBLE); rear: SOURCE Anzum 2022 Table 5 (433 MHz, palm, ~5.0 dB per trunk at SF10-12)
    ("M", "cons"): dict(n=4.0,  sigma_db=8.7, detune_db=0.0,  rear_db=10.0),  # n: ASSUMPTION (baseline "brush" value); sigma: SOURCE P.833-10 sec 2.1 Mulhouse (900-2200 MHz, Rx 1.6 m); rear: ASSUMPTION (above Anzum's 7.6 dB max at 433 MHz)
    ("S", "opt"):  dict(n=4.0,  sigma_db=6.0, detune_db=-2.0, rear_db=0.0),   # n: ASSUMPTION; detune: ASSUMPTION (baseline DETUNE_DB)
    ("S", "cons"): dict(n=4.5,  sigma_db=8.7, detune_db=-2.0, rear_db=0.0),   # n: ASSUMPTION (baseline ground value); sigma: SOURCE P.833-10 Mulhouse
}
RADIO_UPPER = ("M", "opt")   # M1/A1: this scenario reproduces the measured total loss of an ELEVATED-gateway forest link
                            # (Boonlom 2026, Tx 1.7 m -> GW 8 m) but not near-ground forest data (Ferreira 2020);
                            # shown as an unverified upper bound for node-to-node links, not used in headline ranges
# A1 measured anchors (SOURCE)
BOONLOM_RSSI_A_DBM = -16.62     # SOURCE: Boonlom 2026, forest fit RSSI = A - B log10(d)
BOONLOM_RSSI_B_DB = 32.24       # SOURCE: same fit
BOONLOM_D_MAX_M = 1200.0        # SOURCE: longest measured link (SF10, GW 8 m)
BOONLOM_SF = 10                 # SOURCE
FERREIRA_D_MAX_M = 250.0        # SOURCE: Ferreira 2020 sec 5.1.1, SF12 range limit in the rainforest (915 MHz, BW 500 kHz)
FERREIRA_RSSI_DBM = -124.0      # SOURCE: same section
FERREIRA_SF = 12                # SOURCE
FERREIRA_ANT_DBI = 7.0          # SOURCE: monopole 7 dBi (whether at one or both ends was not stated in the part read)
ANCHOR_ANT_DBI_BOONLOM = 0.0    # ASSUMPTION: Boonlom antenna gains not read -> 0 dBi total
REAR_FRACTION = 0.5        # ASSUMPTION: share of bearings for which a trunk-mounted antenna looks through its own trunk
DEPLOYS = ("M", "S")
SCENS = ("opt", "cons")
RANGE_FRESNEL_D_M = 200.0  # ASSUMPTION: link length at which the poster quotes the first Fresnel radius

# LoRa time-on-air defaults (Semtech SX1276/AN1200.13)
LORA_BW_HZ     = 125e3  # SOURCE: AN1200.13 (BW 125 kHz)
LORA_CR        = 1      # SOURCE: coding rate 4/5
LORA_N_PRE     = 8      # SOURCE: preamble symbols
LORA_CRC       = 1      # SOURCE: CRC on
LORA_IH        = 0      # SOURCE: explicit header
LORA_DE_MIN_SF = 11     # SOURCE: low-data-rate optimisation from SF11

# HB_PAYLOAD_B (heartbeat / range-table payload) is defined in section 5: same authenticated frame as an alarm (E3).

# ------------------------------------------------------------------ #
# 2. CONNECTIVITY: Monte Carlo, shadowed links, square region
# ------------------------------------------------------------------ #
SIDE_M       = 2000.0   # ASSUMPTION: 2 km x 2 km = 400 ha
CONN_SEED    = 2027     # ASSUMPTION (M2): separate RNG for connectivity so detection results do not shift with radio inputs (#28)
DENS = [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]   # ASSUMPTION: nodes / ha
TRIALS       = 100      # ASSUMPTION (#30): Monte Carlo trials per point (was 40); 95 % CI reported
TRIALS_LARGE = 30       # ASSUMPTION: trials when the expected node count exceeds TRIALS_LARGE_N (CI still reported)
TRIALS_LARGE_N = 1000   # ASSUMPTION
CONN_SF12_MAX_DENS = 1.0   # ASSUMPTION: SF12 simulated only up to this density (reach is already 1 there)
LINK_D_MIN_M = 1.0      # ASSUMPTION: distances below 1 m are clamped in p_link
DMAX_SIGMA_K = 3.1      # DERIVED: p_link < 1e-3 beyond r0 * 10**(3.1 sigma / 10 n)
CONN_SFS     = (7, 12)  # ASSUMPTION: spreading factors simulated (order fixes RNG use)
# M2: gateways. G = 1 at the centre; G = 4 at the centres of the four quadrants. Every node routes to the gateway
# with the fewest hops (multi-source BFS). Gateway antenna uses the same link model as a node (ASSUMPTION; a mast
# would lengthen gateway links).
GW_COUNTS    = (1, 4)
CONN_REACH_TARGET = 0.95   # ASSUMPTION: "connected" = at least 95 % of nodes reach a gateway (lower 95 % CI bound)
# Edge-effect control: 4 x the area with G = 4 (each gateway serves 400 ha, like G = 1 on 400 ha)
CTRL_SIDE_M  = 4000.0   # ASSUMPTION: 1600 ha control
CTRL_GW      = 4
CTRL_SF      = 7
RELAY_DENS   = 5.0      # ASSUMPTION: density at which relay load is reported (load per first-hop relay is ~density-independent, see models.py)

# ------------------------------------------------------------------ #
# 3. DETECTION (M3): exact Poisson integral in detect.py (no Monte Carlo)
#    Fire: disc growing at constant ROS from a point ignition (no acceleration, no spotting; see Limitations).
# ------------------------------------------------------------------ #
R_T_SCEN = (1.0, 2.0, 5.0)  # ASSUMPTION: heat-detection reach (m). No temperature-only field measurement found (RESEARCH R3);
                            # 5 m = Dampage 2022 multi-sensor node range (method not shown); Chan et al. saw no T change at 10 m
R_T_BASE = 2.0              # ASSUMPTION: middle value used for figures and the headline
R_G_SCEN = (25.0, 50.0, 100.0)   # ASSUMPTION: downwind gas reach (m). No MOx/BME688 field value found; context: H2 sensor
                            # 0.5 m^2 fire at 25 m at detection limit (Noerthemann 2013), CO2 threshold <= 40 m (De Rango 2025)
THETA = math.radians(30)    # ASSUMPTION: plume half-angle (downwind sector fraction theta/pi)
THETA_SWEEP_DEG = (15, 30, 45)   # ASSUMPTION: sensitivity sweep (#28)
ROS_SCEN = (0.3, 1.0, 3.75) # SOURCE (ends): Kucuk et al. 2012, 0.3-3.75 m/min surface fires, young P. brutia (range, not a median; #11);
                            # 1.0 = ASSUMPTION "typical" inside that range
ROS_BASE = 1.0              # ASSUMPTION
ROS_WIND_DRIVEN_KMH = 5.0   # SOURCE: Coskuner et al. 2026 (Fire 9:86), mean ROS of a wind-driven P. brutia fire; outside this model
T_SCEN = (15.0, 30.0, 60.0) # ASSUMPTION: detection deadlines (min)
T_BASE = 15.0               # ASSUMPTION
DESIGN_E_T_MIN = 60.0       # ASSUMPTION (D5/E6): design E = heat only with this deadline (must be in T_SCEN)
DETECT_TARGET_P = 0.9       # ASSUMPTION: required detection probability
TS_HEAT_MIN = 1.0           # ASSUMPTION: temperature sampling period (min); equals T_TEMP / 60
TS_GAS_MIN = 5.0            # SOURCE: BME688 ULP mode update rate 300 s (DS Rev 1.3)
GAS_RESP_MIN = 92 / 60      # SOURCE + ASSUMPTION: BME688 ULP response time tau33-63 = 92 s (DS Rev 1.3 Table 2), taken as extra gas delay
DET_DENS = [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3, 5, 8, 12, 20, 30]   # ASSUMPTION: densities for Fig. 3 (nodes / ha)
ADV_U_MPS = (0.5, 2.0)      # ASSUMPTION (A6): under-canopy wind for the gas-transport sensitivity (one pine snippet: <=0.8 m/s at 4 m)
ADV_RG_M = (50.0, 100.0)    # A6: r_G values for the sensitivity
DET_DR_M = 0.01             # ASSUMPTION: radial step of the integral (m)

# ------------------------------------------------------------------ #
# 3b. ALARM LATENCY (M4): synchronous slotted mesh
#     Every node listens (CAD) once per slot period T_w; a frame waits for the next listen slot of
#     the receiver, then takes its airtime. Per hop: U(0, T_w) + ToA. No ACK/retransmission modelled.
# ------------------------------------------------------------------ #
SLOT_TW_S = {"opt": 2.0, "cons": 30.0}   # ASSUMPTION: listen-slot period (s); trades latency against listening energy (M5)
LAT_SF = 7                  # ASSUMPTION: mesh spreading factor for alarms and heartbeats
DC_LIMIT = 0.01             # REGULATION: 868.0-868.6 MHz, <= 1 % duty cycle (EN 300 220-2 V3.2.1 Table B.1 band M; BTK row 20)
DC_TOBS_S = 3600.0          # REGULATION: observation period 1 h (EN 300 220-1 V3.1.1 sec 5.4.1)
LAT_DENS = 5.0              # ASSUMPTION: density whose hop counts are used (same as RELAY_DENS)
BACKHAUL_S = 0.0            # ASSUMPTION: gateway -> cloud delay not modelled (LTE/satellite; Limitations)


# ------------------------------------------------------------------ #
# M5: node power = sleep + own heartbeat + mesh listening (CAD each slot) + sync beacon + relaying + sensors.
V = 3.3                     # ASSUMPTION (#4): supply voltage
I_SLEEP_T = {"25C": 2.5e-6, "50C": 8.5e-6}   # ASSUMPTION (#4): node sleep budget (MCU Stop2 + RTC + sensors idle + regulator);
                            # STM32WLE5 Stop2+RTC alone 1.07 uA @3 V (DS13105 Rev 2 cover, SNIPPET_ONLY); temperature table NOT_ACCESSIBLE;
                            # 8.5 uA at 50 C is the poster's earlier unsourced figure, kept as the hot scenario
I_SLEEP = I_SLEEP_T["25C"]  # kept for the 25 C reference
STM32_FLASH_ENDURANCE_KCYCLES = 10   # SOURCE: DS13105 Rev 6 Table 66 (READ_FULL); quoted, not a model input
STM32_STOP2_RTC_UA = 1.07   # SOURCE (SNIPPET_ONLY): STM32WLE5 DS13105 Rev 2 cover page, Stop2 + RTC at VDD 3 V; quoted, not a model input
I_TX14 = 45e-3              # SOURCE: SX1261/2 DS Rev 1.2 Table 3-6, SX1262 +14 dBm optimal settings (868/915 MHz)
I_RX_A = 5.3e-3             # SOURCE: SX1261/2 DS Rev 1.2 Table 3-5, Rx Boosted LoRa 125 kHz, DC-DC (the gain used for the sensitivities)
T_WAKE_RADIO_S = 190e-6     # SOURCE: SX1261/2 DS Rev 1.2 Table 3-7: XOSC wake-up 150 us + synthesizer 40 us
CAD_SYMBOLS = 2             # ASSUMPTION: CAD length (DS sec 6.1.5 allows 1, 2, 4, 8, 16 symbols)
I_MCU_A = 5e-3              # ASSUMPTION: MCU active current
T_MCU_WAKE_S = 1e-3         # ASSUMPTION: MCU time per listen slot (wake, start radio, back to Stop2)
T_MCU_S = 0.050             # ASSUMPTION: MCU active time per heartbeat (build frame, AES, start TX)
Q_MCU = I_MCU_A * T_MCU_S   # DERIVED
SYNC_PERIOD_S = 3600.0      # ASSUMPTION: one time-sync beacon per hour
CLOCK_PPM = 20.0            # ASSUMPTION: 32.768 kHz crystal tolerance (no datasheet read)
LOAD_EXAMPLE_DENS = 30.0    # ASSUMPTION (D3): density at which the single-channel heartbeat load is quoted
SYNC_PAYLOAD_B = 12         # ASSUMPTION: beacon payload incl. authentication
I_TEMP_A = 320e-6           # SOURCE: SHT4x high repeatability (datasheet not re-read in this revision)
T_TEMP_MEAS_S = 8.3e-3      # SOURCE: SHT4x high repeatability
Q_TEMP = I_TEMP_A * T_TEMP_MEAS_S   # DERIVED: 320e-6 * 8.3e-3
T_TEMP = TS_HEAT_MIN * 60.0  # DERIVED: s, temperature sampling period (same as detection model)
I_GAS_AVG_A = 0.09e-3       # SOURCE: BME688 DS Rev 1.3 Table 2, ULP average 0.09 mA (VDD <= 1.8 V, 25 C; 3.3 V not specified)
GAS_REF_PERIOD_S = 300      # SOURCE: BME688 ULP update rate 300 s
GAS_MODEL_NOTE = "0.09 mA drawn from the 3.3 V rail (as if fed by a linear regulator)"   # ASSUMPTION (A5): supply model for I_GAS_AVG_A
GAS_VDD_LOW_V = 1.8         # SOURCE: BME688 DS Table 2 condition (VDD <= 1.8 V) for the 0.09 mA figure
BUCK_EFF = 0.85             # ASSUMPTION (A5): efficiency of a 3.3 V -> 1.8 V buck converter for the sensitivity case
Q_GAS = I_GAS_AVG_A * GAS_REF_PERIOD_S   # DERIVED: 27 mC per scan
GAS_P_SELECTED_S = 300      # SOURCE: ULP mode period, used for the gas designs
HEARTBEAT_S = 3600.0        # ASSUMPTION: s
YEAR = 365.25 * 86400       # DERIVED: s per year
BATT = {"Li-SOCl2 AA (2.6 Ah)": (2.6 * 0.7, 0.01)}   # ASSUMPTION (#28): (usable Ah, self-discharge/yr); derating unsourced
ENERGY_SF = 7               # ASSUMPTION: mesh SF for energy (same as LAT_SF)
ENERGY_ROLES = ("leaf", "relay_mean", "relay_max")   # leaf: forwards nothing; relays: first-hop load from connectivity.csv
# PV under canopy: only figure found is a 0.5 W mono module under high canopy closure, 200-1800 lux:
# peak 0.105-2.145 mW (Electronics 8(12):1409, 2019; SNIPPET_ONLY). Panel area not read; Dryad uses 8 x 8 cm (vendor).
PV_PEAK_MW = {"low": 0.105, "high": 2.145}   # SOURCE (SNIPPET_ONLY), see above
PV_HARVEST_H = 5.0          # ASSUMPTION (#5): equivalent full-peak hours per day (NOT FOUND)
P_HARVEST_MW = {k: v * PV_HARVEST_H / 24.0 for k, v in PV_PEAK_MW.items()}   # DERIVED: 24 h average
SC_F = 10.0                 # ASSUMPTION: supercapacitor (F)
SC_V_MAX = 2.5              # ASSUMPTION: charge limit, derated from 2.7 V for summer heat (Eaton guideline, SNIPPET_ONLY)
SC_V_MIN = 1.8              # ASSUMPTION: regulator dropout floor
SC_AUTONOMY_H = 72.0        # ASSUMPTION: dark/overcast period the store must bridge
GNSS_I_ACQ_A = 7.0e-3 + 2.2e-3      # SOURCE: MAX-M10S DS UBX-20035208 R02 Table 13, acquisition GPS+GAL: VCC 7.0 mA + V_IO 2.2 mA
GNSS_TTFF_COLD_S = 29.0             # SOURCE: same DS Table 1, cold start GPS+GAL, open sky (-130 dBm)
GNSS_FIX_S = (29.0, 120.0, 300.0)   # 29 s SOURCE (open sky); 120 / 300 s ASSUMPTION for under-canopy cold starts (NOT FOUND)
GNSS_P_FIX = (0.5, 0.8, 1.0)        # ASSUMPTION (A7): probability that one attempt yields a fix under the canopy (NOT FOUND)
GNSS_MAX_TRIES = 3                  # ASSUMPTION: attempts before falling back to gateway-level position
RELAY_SIZING_ROLE = "relay_max"   # ASSUMPTION (A3): every first-hop relay gets a battery pack sized for the busiest relay
RELAY_PACK_YEARS = 10       # ASSUMPTION (A3): relay pack must last this long without service

# ------------------------------------------------------------------ #
# 5. SECURITY OVERHEAD
# ------------------------------------------------------------------ #
SEC_TAGS_B = (0, 4, 8, 16)  # ASSUMPTION: AEAD tag lengths (bytes)
SEC_SFS = (7, 10, 12)       # ASSUMPTION
SEC_DATA_B = 12             # ASSUMPTION (#6): 12 B data
SEC_HDR_FIELDS = (("node_id", 2), ("epoch_lsb", 1), ("counter", 4))   # ASSUMPTION (A2): frame header; the receiver rebuilds the
                            # full epoch from its stored high bytes + the transmitted LSB (tolerates up to 255 unreported reboots)
SEC_HDR_B = sum(b for _, b in SEC_HDR_FIELDS)   # DERIVED: 7 B (was 6 B before A2)
HB_TAG_B = 8                # ASSUMPTION (E3): heartbeats carry the alarm tag length
HB_PAYLOAD_B = SEC_DATA_B + SEC_HDR_B + HB_TAG_B   # DERIVED (E3): 12 B data + 7 B header + 8 B tag = 27 B (was 25 B, #3)
SEC_CIPHER_LABEL = "AES-256-CCM"   # ASSUMPTION (#27): 256-bit key, 128-bit block, CCM mode (SP 800-38C)
SEC_KEY_BITS = 256          # ASSUMPTION: AES key length
SEC_GROVER_FACTOR = 0.5     # SOURCE: Grover 1996, O(sqrt N) key search -> about half the key bits against a quantum attacker
# CCM nonce: n in {7..13} bytes, unique per key (SP 800-38C sec 5.3, App. A.2). Fields (name, bytes), most significant first:
SEC_NONCE_FIELDS = (("counter", 4), ("epoch", 3), ("node_id", 2))   # ASSUMPTION (#6): counter || epoch || node ID (user design brief)
# A2: the counter lives in RAM (SRAM is retained in Stop2, DS13105 Rev 6 sec 3) and restarts at 0 after a power loss;
# the epoch lives in flash and is advanced once per boot (flash endurance 10 kcycles, DS13105 Rev 6 Table 66).
AES_I_A = 5e-3              # ASSUMPTION (#22): AES peripheral current; STM32WL reference manual NOT_ACCESSIBLE
AES_CYCLES = 280            # ASSUMPTION (#22): cycles per CCM frame; NOT FOUND
AES_CLK_HZ = 48e6           # ASSUMPTION (#22): clock

# ------------------------------------------------------------------ #
# 7. COST (M7). Unit prices in USD, (low, high). SOURCE = distributor/vendor price seen in a web search
#    summary on 2026-10-06 (SNIPPET_ONLY, quantity noted); ESTIMATE = no source found, reasoned range.
# ------------------------------------------------------------------ #
COST = {
    "radio_mcu":   (6.49, 9.11),    # SOURCE: Wio-E5 (STM32WLE5JC) module, Seeed $6.49 .. Mouser $9.11, qty 1
    "bme688":      (5.76, 8.65),    # SOURCE: DigiKey $5.76 (3000, reel) .. Mouser $8.65 (qty 1)
    "temp_rh":     (1.0, 3.0),      # ESTIMATE: SHT4x-class T/RH sensor; price NOT FOUND
    "battery_aa":  (10.0, 18.0),    # SOURCE: Li-SOCl2 AA (Saft LS14500), "around $10-$18" retail (search summary)
    "pv_cell":     (3.0, 6.0),      # ESTIMATE: 0.5 W ~55x70 mm panel listed at GBP 3.74 / AUD 5.80; USD price NOT FOUND
    "supercap":    (2.0, 8.0),      # ESTIMATE: 10-60 F, 2.7 V EDLC; price NOT FOUND
    "enclosure_pcb_antenna": (10.0, 30.0),   # ESTIMATE: IP-rated box, PCB, antenna, assembly; NOT FOUND
    "gateway":     (372.0, 525.0),  # SOURCE: RAK7289 WisGate Edge Pro (8/16 ch, LTE option) "$372.00 to $525.00"
    "gw_solar_mast": (200.0, 500.0),  # ESTIMATE: solar panel, battery, mast for an off-grid gateway; NOT FOUND
    "gw_data_month": (5.0, 15.0),   # ESTIMATE: LTE IoT data plan per gateway and month; NOT FOUND
    "install_M":   (5.0, 15.0),     # ESTIMATE: hand mounting per node (walk-in, strap, GNSS fix); NOT FOUND
    "install_S":   (1.0, 5.0),      # ESTIMATE: share of a drone sortie per scattered node; NOT FOUND
    "service_visit": (5.0, 15.0),   # ESTIMATE: battery swap per node (trunk-mounted only)
}
# A7: position. M: recorded at installation (labour inside install_M, no GNSS on the node); S: optional one-shot GNSS.
POS_OPTIONS = {"M": ("record_at_install",), "S": ("gnss_once", "none")}   # ASSUMPTION; "none" = reference without position
GNSS_MODULE_USD = (21.0, 21.0)      # SOURCE (SNIPPET_ONLY): u-blox MAX-M10S-00B, DigiKey USD 21.00 qty 1 (no volume price seen)
GNSS_ANTENNA_USD = (5.0, 19.0)      # SOURCE (SNIPPET_ONLY): Taoglas 25x25 mm GNSS patch antennas, USD 5.00-19.00
GNSS_EXTRA_USD = (1.0, 3.0)         # ESTIMATE: load switch, matching, larger PCB; NOT FOUND
CLOUD_USD_PER_MILLION_MSG = 1.00   # SOURCE: AWS IoT Core messaging, first 1 billion, EU (Ireland) example (SNIPPET_ONLY)
COST_YEARS = 10                    # ASSUMPTION: horizon for the 10-year total
COST_AREA_HA = 400.0               # ASSUMPTION: same 400 ha as the connectivity model
COST_GW = {"M": 1, "S": 4}         # ASSUMPTION: gateways per 400 ha (G = 1 trunk, G = 4 scattered: relay load, M2/M5)
NSW_CAMERA_AUD = 1.4e6      # SOURCE (READ_FULL via WebFetch): NSW Government release 18 Sep 2025, "up to $1.4 million over 5 years"
NSW_CAMERA_YEARS = 5        # SOURCE: same release
NSW_CAMERA_HA = 1.2e6       # SOURCE: same release, 22 sites covering 1.2 million hectares
VENDOR_FORESTGUARD_EUR_PER_M2_YR = 0.006   # VENDOR: nowildfire.com "EUR 0.006 / m2 / year" (EUR; not converted)

# ------------------------------------------------------------------ #
# 6. FIGURES: values shown in figures.py
#    Style (colours, fonts, positions, ticks, limits) stays in figures.py.
# ------------------------------------------------------------------ #
# Fig. 1, range
FIG1_CURVES = [(("M", "opt"), "trunk, upper bound (unverified)"), (("M", "cons"), "trunk 2.5 m, conservative"),
               (("S", "opt"), "scattered, optimistic"), (("S", "cons"), "scattered, conservative")]   # labels FIG-INDEPENDENT
FIG1_XLABEL = "LoRa spreading factor (BW 125 kHz, 14 dBm)"   # FIG-INDEPENDENT: repeats LORA_BW_HZ, TX_DBM
VENDOR_DRYAD_MADA_SENSORS = 91    # VENDOR: dryad.net/case-studies/mada, 91 sensors
VENDOR_DRYAD_MADA_HA = 78         # VENDOR: same page, 78 ha
VENDOR_DRYAD_SPACING_MAX_M = 300   # VENDOR: dryad.net/wildfiresensor "Up to 300m (depending on risk)", accessed 2026-10-06 (sensor spacing, not radio range; #32)
# Fig. 2, connectivity
FIG2_CURVES = [(("M", "cons"), 1), (("M", "cons"), 4), (("S", "cons"), 1), (("S", "cons"), 4)]   # SF7 curves shown
FIG2_SF = 7

# Fig. 3 / Fig. 4: built from detection.csv and required_density.csv (base: ROS_BASE, T_BASE, R_T_BASE)

# Fig. 5, energy
FIG5_CASES = [("heat", "leaf"), ("gas", "leaf"), ("gas", "relay_mean"), ("gas", "relay_max")]   # S cons, G=1, T_w opt, 25 C
