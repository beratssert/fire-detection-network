#!/usr/bin/env python3
"""
Independent checks of the model outputs (results/*.csv, results/macros.tex).

Each check re-derives a quantity with its own code path (stdlib math, no import of
models.py) from the inputs in params.py and compares it with what the pipeline wrote.
Run from the repo root after ./run_all.sh:   python tests/check_model.py
Exit code 0 if every check is OK, 1 otherwise.

Model atoms append their own checks below (one function per check, registered in CHECKS).
"""
import csv, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import params as P

C_LIGHT = 299_792_458.0   # m/s, exact (SI definition)
RES = "results"

def rows(name, **where):
    with open(os.path.join(RES, name), newline="") as f:
        return [r for r in csv.DictReader(f) if all(r[k] == str(v) for k, v in where.items())]

def one(name, **where):
    r = rows(name, **where)
    if len(r) != 1:
        raise AssertionError(f"{name} {where}: {len(r)} rows")
    return r[0]

def close(a, b, rel=None, abs_=None):
    if abs_ is not None and abs(a - b) <= abs_:
        return True
    if rel is not None and abs(a - b) <= rel * max(abs(a), abs(b)):
        return True
    return False

CHECKS = []
def check(fn):
    CHECKS.append(fn); return fn

# ------------------------------------------------------------------ #
# P0-2: checks of the baseline model
# ------------------------------------------------------------------ #
def toa_s(sf, pl, bw=125e3, cr=1, npre=8, crc=1, ih=0):
    """LoRa time on air, Semtech AN1200.13 eq. (Tsym, preamble, payload symbols)."""
    de = 1 if sf >= 11 else 0
    tsym = 2.0 ** sf / bw
    nsym = 8 + max(math.ceil((8 * pl - 4 * sf + 28 + 16 * crc - 20 * ih) / (4 * (sf - 2 * de))) * (cr + 4), 0)
    return (npre + 4.25) * tsym + nsym * tsym

@check
def fresnel_200m():
    """First Fresnel radius at mid-path of a 200 m link at F_MHZ; poster prints 4.15 m (typed)."""
    lam = C_LIGHT / (P.F_MHZ * 1e6)
    r1 = math.sqrt(lam * 100.0 * 100.0 / 200.0)
    return close(r1, 4.15, abs_=0.02), f"r1 = {r1:.3f} m (poster 4.15 m)"

@check
def toa_security_csv():
    bad = []
    for r in rows("security.csv"):
        t = 1e3 * toa_s(int(r["sf"]), int(r["phy_payload"]))
        if not close(t, float(r["toa_ms"]), abs_=0.051):
            bad.append((r["sf"], r["phy_payload"], t, r["toa_ms"]))
    n = len(rows("security.csv"))
    return not bad, f"{n} rows recomputed with AN1200.13; mismatches {bad[:3]}"

@check
def toa_range_csv():
    bad = []
    for r in rows("range.csv"):
        t = 1e3 * toa_s(int(r["sf"]), P.HB_PAYLOAD_B)
        if not close(t, float(r["toa_hb_ms"]), abs_=0.051):
            bad.append((r["sf"], t, r["toa_hb_ms"]))
    return not bad, f"range.csv toa_hb_ms; mismatches {bad[:3]}"

@check
def link_budget_range():
    """d = 10^((Ptx - S + G + detune - margin - FSPL(1 m)) / 10n); FSPL(1 m) from Friis; per (deploy, scen, sf)."""
    fspl1 = 20 * math.log10(4 * math.pi * P.F_MHZ * 1e6 / C_LIGHT)
    sens = {7: -124.0, 12: -137.0}          # SX1261/2 DS Rev 1.2 Table 3-8 (typed here on purpose: independent of params)
    bad, n = [], 0
    for r in rows("range.csv"):
        rp = P.RADIO[(r["deploy"], r["scen"])]
        sf = int(r["sf"])
        s_dbm = sens.get(sf, sens[7] + (sens[12] - sens[7]) * (sf - 7) / 5)
        budget = P.TX_DBM - s_dbm + P.ANT_GAIN_DBI * P.N_ANT + rp["detune_db"] - fspl1
        d50 = 10 ** (budget / (10 * rp["n"]))
        d90 = 10 ** ((budget - P.FADE_Q * rp["sigma_db"]) / (10 * rp["n"]))
        d90r = 10 ** ((budget - P.FADE_Q * rp["sigma_db"] - rp["rear_db"]) / (10 * rp["n"]))
        n += 1
        if not all(close(a, float(r[c]), rel=2e-3) for a, c in ((d50, "range50_m"), (d90, "range90_m"), (d90r, "range90_rear_m"))):
            bad.append((r["deploy"], r["scen"], sf, round(d90, 1), r["range90_m"]))
    return not bad and n == 24, f"{n} rows; FSPL(1 m) = {fspl1:.2f} dB; mismatches {bad[:3]}"

def expected_detectors(lam_ha, v, T, rt, Ts_h, rg=0.0, Ts_g=1.0, t_resp=0.0, theta=0.0, h=0.02, U=None):
    """
    Independent scalar implementation (trapezoid, own loop) of E[# nodes detected by T]:
    heat everywhere within rt (sampling U(0, Ts_h)); gas only in the downwind sector (fraction theta/pi)
    within rg after t_resp + U(0, Ts_g); the two phases independent.
    """
    lam = lam_ha / 1e4
    def ph(r): return min(max((T - max(r - rt, 0.0) / v) / Ts_h, 0.0), 1.0)
    def pg(r):
        adv = 0.0 if U is None else min(r, rg) / U / 60.0
        return min(max((T - t_resp - adv - max(r - rg, 0.0) / v) / Ts_g, 0.0), 1.0)
    f = theta / math.pi if rg > 0 else 0.0
    rmax = max(rt, rg) + v * T + 1.0
    s, r, prev = 0.0, 0.0, None
    while r <= rmax:
        val = (1 - f) * ph(r) + (f * (1 - (1 - ph(r)) * (1 - pg(r))) if rg > 0 else 0.0)
        cur = val * 2 * math.pi * r
        if prev is not None:
            s += 0.5 * (prev + cur) * h
        prev, r = cur, r + h
    return lam * s

@check
def required_density_analytic():
    """required_density.csv vs independent integral: lam = ln(1/(1-p)) / (E(1/ha)) (tolerance 0.5 %)."""
    bad, n = [], 0
    for r in rows("required_density.csv"):
        n += 1
        if n % 3:                         # every third row keeps the check fast
            continue
        rg, rt, v, T = float(r["r_G_m"]), float(r["r_T_m"]), float(r["ros"]), float(r["T_min"])
        e1 = expected_detectors(1.0, v, T, rt, P.TS_HEAT_MIN, rg, P.TS_GAS_MIN, P.GAS_RESP_MIN,
                                math.radians(float(r["theta_deg"])))
        lam = -math.log(1 - P.DETECT_TARGET_P) / e1
        if not close(lam, float(r["req_density_per_ha"]), rel=5e-3):
            bad.append((r["design"], rg, rt, v, T, round(lam, 3), r["req_density_per_ha"]))
    return not bad, f"{n} rows, every 3rd checked; mismatches {bad[:3]}"

@check
def advection_sensitivity():
    """A6: sensitivity_adv.csv vs the independent integral with t_adv = min(r, r_G)/U; base CSV row must equal req_density_base."""
    bad = []
    for r in rows("sensitivity_adv.csv"):
        rg, U = float(r["r_G_m"]), float(r["U_mps"])
        e0 = expected_detectors(1.0, 1.0, 15.0, 2.0, P.TS_HEAT_MIN, rg, P.TS_GAS_MIN, P.GAS_RESP_MIN, P.THETA)
        e1 = expected_detectors(1.0, 1.0, 15.0, 2.0, P.TS_HEAT_MIN, rg, P.TS_GAS_MIN, P.GAS_RESP_MIN, P.THETA, U=U)
        l0, l1 = math.log(10) / e0, math.log(10) / e1
        base = float(one("required_density.csv", design="gas", r_G_m=rg, r_T_m=2.0, ros=1.0, T_min=15.0, theta_deg=30)["req_density_per_ha"])
        if not (close(l0, float(r["req_density_base"]), rel=5e-3) and close(l1, float(r["req_density_adv"]), rel=5e-3)
                and close(base, float(r["req_density_base"]), abs_=0.002)):
            bad.append((rg, U, round(l1, 3), r["req_density_adv"]))
    return not bad, f"mismatches {bad}"

@check
def detection_monte_carlo():
    """Small independent Monte Carlo (point ignition, Poisson nodes) vs detection.csv at two points (4 sigma)."""
    import random
    rnd = random.Random(11)
    out, ok = [], True
    for design, rg, lam_ha in (("gas", 50.0, 5), ("heat", 0.0, 20)):
        row = one("detection.csv", design=design, r_G_m=rg, r_T_m=P.R_T_BASE if design == "gas" else 2.0,
                  density_per_ha=lam_ha)
        p_csv, trials, hits = float(row["p_detect"]), 4000, 0
        R = max(rg, P.R_T_BASE) + P.ROS_BASE * P.T_BASE + 5
        lam = lam_ha / 1e4
        for _ in range(trials):
            # Poisson count by inversion-free sum of exponentials
            n, acc, mean = 0, 0.0, lam * math.pi * R * R
            while True:
                acc += rnd.expovariate(1.0)
                if acc > mean: break
                n += 1
            det = False
            for _ in range(n):
                r = R * math.sqrt(rnd.random()); phi = rnd.uniform(-math.pi, math.pi)
                th = P.T_BASE
                t_h = max(r - P.R_T_BASE, 0) / P.ROS_BASE + rnd.uniform(0, P.TS_HEAT_MIN)
                t = t_h
                if rg > 0 and abs(phi) < P.THETA:
                    t = min(t, P.GAS_RESP_MIN + max(r - rg, 0) / P.ROS_BASE + rnd.uniform(0, P.TS_GAS_MIN))
                if t <= th: det = True; break
            hits += det
        p_mc = hits / trials
        sd = math.sqrt(p_csv * (1 - p_csv) / trials)
        out.append((design, rg, lam_ha, p_csv, round(p_mc, 4)))
        ok &= abs(p_mc - p_csv) <= 4 * sd + 1e-3
    return ok, f"(design, r_G, density, analytic, MC) {out}"

@check
def energy_recompute():
    """energy.csv: average current from datasheet-style parts with own ToA; AA life; supercap autonomy (M5)."""
    bad, n = [], 0
    tsym = 2 ** 7 / 125e3
    for r in rows("energy.csv"):
        if r["role"] == "gnss_fix":
            continue
        tw = float(r["T_w_s"]); fwd = float(r["forwarded"])
        i = (P.I_SLEEP_T[r["temp"]]
             + (P.I_TX14 * toa_s(7, P.HB_PAYLOAD_B) + P.I_MCU_A * P.T_MCU_S) / 3600
             + (P.I_RX_A * (P.CAD_SYMBOLS * tsym + 190e-6) + P.I_MCU_A * P.T_MCU_WAKE_S) / tw
             + P.I_RX_A * (toa_s(7, P.SYNC_PAYLOAD_B) + 2 * P.CLOCK_PPM * 1e-6 * 3600 + 190e-6) / 3600
             + fwd * ((P.I_RX_A + P.I_TX14) * toa_s(7, P.HB_PAYLOAD_B) + P.I_MCU_A * P.T_MCU_S) / 3600
             + P.I_TEMP_A * P.T_TEMP_MEAS_S / 60
             + (P.I_GAS_AVG_A if r["design"] == "gas" else 0.0))
        p_w = i * P.V
        cap_c = 2.6 * 0.7 * 3600
        yrs = cap_c / (i * 365.25 * 86400 + 0.01 * cap_c)
        aut_h = 0.5 * P.SC_F * (P.SC_V_MAX ** 2 - P.SC_V_MIN ** 2) / p_w / 3600
        n += 1
        cells = math.ceil(i * 365.25 * 86400 * 10 / (2.6 * 0.7 * 3600 * (1 - 0.01 * 10)))
        if not (close(i * 1e6, float(r["i_avg_uA"]), abs_=0.002) and close(yrs, float(r["life_LiSOCl2_yr"]), abs_=0.006)
                and close(aut_h, float(r["sc_autonomy_h"]), abs_=0.06) and cells == int(r["aa_cells_10yr"])):
            bad.append((r["deploy"], r["gw"], r["role"], r["slot"], r["temp"], r["design"]))
    return not bad and n == 96, f"{n} rows; mismatches {bad[:3]}"

@check
def security_columns():
    """tag=0 has no authentication; forgery = 2^-(8 tag); Grover bits = key/2; nonce 7..13 B (SP 800-38C)."""
    bad = []
    for r in rows("security.csv"):
        t = int(r["tag_bytes"])
        if t == 0:
            ok = r["cipher"].startswith("none") and r["key_security_bits"] == "0"
        else:
            ok = (abs(float(r["forgery_prob_per_try"]) - 2.0 ** (-8 * t)) <= 1e-3 * 2.0 ** (-8 * t)
                  and int(r["key_security_grover_bits"]) * 2 == int(r["key_security_bits"])
                  and 7 <= int(r["nonce_bytes"]) <= 13 and t in (4, 6, 8, 10, 12, 14, 16))
        if not ok:
            bad.append((t, r["sf"]))
    return not bad, f"violations {bad[:3]}"

@check
def upper_bound_vs_boonlom():
    """A1: the upper-bound scenario's path loss vs Boonlom's measured forest fit (0 dBi), within 1.5 dB at 250 m and 1.2 km."""
    f1 = 20 * math.log10(4 * math.pi * 868e6 / C_LIGHT)
    n = P.RADIO[P.RADIO_UPPER]["n"]
    out = []
    for d in (250.0, 1200.0):
        meas = 14.0 - (-16.62 - 32.24 * math.log10(d))      # Boonlom 2026 fit, typed here on purpose
        model = f1 + 10 * n * math.log10(d)
        out.append((d, round(meas, 1), round(model, 1)))
    return all(abs(m - mo) <= 1.5 for _, m, mo in out), f"(d, measured, model) {out}"

@check
def frame_header():
    """A2: header = node ID 2 + epoch LSB 1 + counter 4 = 7 B; every security.csv frame = 12 B data + 7 B + tag."""
    bad = [r for r in rows("security.csv") if int(r["phy_payload"]) != 12 + 7 + int(r["tag_bytes"])]
    lat = [r for r in rows("latency.csv") if abs(float(r["toa_alarm_ms"]) - round(1e3 * toa_s(7, 12 + 7 + 8), 1)) > 0.051]
    return not bad and not lat and P.SEC_HDR_B == 7, f"bad frames {len(bad)}, latency ToA mismatches {len(lat)}"

# ------------------------------------------------------------------ #
# M2: connectivity
# ------------------------------------------------------------------ #
def q_func(x):
    return 0.5 * math.erfc(x / math.sqrt(2))

@check
def mean_degree_numeric():
    """<k> = lam * integral of P(link at d) 2 pi d dd, P = Q((10 n log10(d/r0) + R)/sigma), R over rear combinations."""
    bad, n_rows = [], 0
    for r in rows("connectivity.csv"):
        if r["density_per_ha"] != "1.0" or r["area_ha"] != "400":
            continue
        rp = P.RADIO[(r["deploy"], r["scen"])]
        r0, lam = float(r["r0_m"]), 1.0 / 1e4
        pr = P.REAR_FRACTION if rp["rear_db"] > 0 else 0.0
        combos = [(0.0, (1 - pr) ** 2), (rp["rear_db"], 2 * pr * (1 - pr)), (2 * rp["rear_db"], pr ** 2)]
        k = 0.0
        for extra, w in combos:
            if w == 0: continue
            h, d, acc = r0 / 2000, r0 / 4000, 0.0
            while d < r0 * 60:
                acc += q_func((10 * rp["n"] * math.log10(d / r0) + extra) / rp["sigma_db"]) * 2 * math.pi * d * h
                d += h
            k += w * lam * acc
        n_rows += 1
        if not close(k, float(r["mean_degree"]), rel=0.01):
            bad.append((r["deploy"], r["scen"], r["sf"], round(k, 2), r["mean_degree"]))
    return not bad and n_rows > 0, f"{n_rows} rows at 1/ha; mismatches {bad[:3]}"

@check
def conn_sanity():
    """reach non-decreasing in density (within 2 CI); G=4 hop_p95 <= G=1 hop_p95 where both reach the target."""
    import itertools
    bad = []
    rs = rows("connectivity.csv", area_ha=400)
    key = lambda r: (r["deploy"], r["scen"], r["sf"], r["gw"])
    for k, grp in itertools.groupby(sorted(rs, key=key), key=key):
        g = sorted(grp, key=lambda r: float(r["density_per_ha"]))
        for a, b in zip(g, g[1:]):
            if float(b["reach_mean"]) + 2 * float(b["reach_ci95"]) + 1e-9 < float(a["reach_mean"]) - 2 * float(a["reach_ci95"]):
                bad.append(("reach", k, a["density_per_ha"]))
    idx = {(r["deploy"], r["scen"], r["sf"], r["gw"], r["density_per_ha"]): r for r in rs}
    for (d, sc, sf, gw, lam), r in idx.items():
        if gw == "1" and (d, sc, sf, "4", lam) in idx:
            r4 = idx[(d, sc, sf, "4", lam)]
            # hop statistics are conditional on reaching a gateway: compare only where both reach the target
            if min(float(r["reach_mean"]), float(r4["reach_mean"])) < P.CONN_REACH_TARGET:
                continue
            if float(r4["hop_p95"]) > float(r["hop_p95"]) + 0.5:
                bad.append(("hops", d, sc, sf, lam))
    return not bad, f"{len(rs)} rows; violations {bad[:4]}"

# ------------------------------------------------------------------ #
# M4: latency
# ------------------------------------------------------------------ #
@check
def latency_recompute():
    """report delays and relay duty-cycle share recomputed from connectivity.csv with own ToA."""
    bad, n = [], 0
    for r in rows("latency.csv"):
        c = one("connectivity.csv", deploy=r["deploy"], scen=r["scen"], sf=P.LAT_SF, gw=r["gw"], area_ha=400,
                density_per_ha=P.LAT_DENS)
        tw = float(r["T_w_s"]); ta = toa_s(P.LAT_SF, P.SEC_DATA_B + P.SEC_HDR_B + 8); th = toa_s(P.LAT_SF, P.HB_PAYLOAD_B)
        exp_mean = float(c["hop_mean"]) * (tw / 2 + ta)
        exp_95 = float(c["hop_p95"]) * (tw + ta)
        exp_dc = (1 + float(c["relay_load_max"])) * th / (0.01 * 3600)
        n += 1
        if not (close(exp_mean, float(r["report_mean_s"]), abs_=0.06) and close(exp_95, float(r["report_p95hops_worst_s"]), abs_=0.06)
                and close(exp_dc, float(r["relay_dc_frac_max"]), abs_=6e-4)):
            bad.append((r["deploy"], r["scen"], r["gw"], r["slot"]))
    return not bad and n > 0, f"{n} rows; mismatches {bad[:3]}"

# ------------------------------------------------------------------ #
# M7: cost
# ------------------------------------------------------------------ #
@check
def cost_recompute():
    """capex per ha = (n (unit + install) + G (gateway + mast)) / area; unit = sum of listed parts; replacements from life."""
    parts = {"A": ["radio_mcu", "temp_rh", "battery_aa", "enclosure_pcb_antenna"],
             "B gas 50 m, AA": ["radio_mcu", "bme688", "temp_rh", "battery_aa", "enclosure_pcb_antenna"]}
    pv = ["radio_mcu", "bme688", "temp_rh", "pv_cell", "supercap", "enclosure_pcb_antenna"]
    bad, n = [], 0
    for r in rows("cost.csv"):
        b = 0 if r["bound"] == "low" else 1
        plist = parts["A"] if r["design"][0] in "AE" else (parts["B gas 50 m, AA"] if "AA" in r["design"] else pv)
        gn = (P.GNSS_MODULE_USD[b] + P.GNSS_ANTENNA_USD[b] + P.GNSS_EXTRA_USD[b]) if r["pos_option"] == "gnss_once" else 0.0
        leaf = sum(P.COST[k][b] for k in plist) + gn
        relay = leaf - sum(P.COST[k][b] for k in plist if k in ("battery_aa", "pv_cell", "supercap")) + int(r["relay_pack_aa"]) * P.COST["battery_aa"][b]
        sh = float(r["relay_share"])
        unit = (1 - sh) * leaf + sh * relay
        nodes = float(r["nodes_per_ha"]) * 400
        g = int(r["gateways"])
        cap = (nodes * (unit + P.COST["install_" + r["deploy"]][b]) + g * (P.COST["gateway"][b] + P.COST["gw_solar_mast"][b])) / 400
        n += 1
        if not (close(unit, float(r["node_unit_usd"]), abs_=0.02) and close(cap, float(r["capex_usd_per_ha"]), rel=0.01)):
            bad.append((r["design"], r["deploy"], r["bound"], round(cap, 1), r["capex_usd_per_ha"]))
        if r["battery_life_yr"]:
            if int(r["replacements_10yr"]) != max(math.ceil(10 / float(r["battery_life_yr"])) - 1, 0):
                bad.append(("repl", r["design"], r["deploy"]))
    return not bad and n == 36, f"{n} rows; mismatches {bad[:3]}"

@check
def gnss_fix_energy():
    """A7: attempt energy = t * 9.2 mA * 3.3 V; expected attempts (1-(1-p)^3)/p; charge from empty = (C Vmin^2/2 + E1)/P_pv."""
    bad, n = [], 0
    for r in rows("energy.csv", role="gnss_fix"):
        t, p = float(r["gnss_fix_s"]), float(r["gnss_p_fix"])
        e1 = t * (7.0e-3 + 2.2e-3) * 3.3
        tries = (1 - (1 - p) ** 3) / p
        ch = (0.5 * 10 * 1.8 ** 2 + e1) / (0.105e-3 * 5 / 24) / 3600
        n += 1
        if not (close(e1, float(r["gnss_e_attempt_J"]), abs_=0.006) and close(tries, float(r["gnss_attempts_exp"]), abs_=0.006)
                and close(ch, float(r["gnss_charge_h_low"]), abs_=0.06)):
            bad.append((t, p))
    # cost ordering reported honestly: S+GNSS vs M per design and bound
    order = []
    for r in rows("cost.csv", deploy="S", pos_option="gnss_once"):
        m = one("cost.csv", design=r["design"], deploy="M", pos_option="record_at_install", bound=r["bound"])
        order.append(float(r["capex_usd_per_ha"]) > float(m["capex_usd_per_ha"]))
    return not bad and n == 9, f"{n} rows; mismatches {bad}; S+GNSS dearer than M in {sum(order)}/{len(order)} cases"

@check
def limitation_numbers():
    """D3: two-node confirmation lambda*I, clock drift, SF7 preamble, 30/ha heartbeat load, recomputed from first principles."""
    import re
    mac = open(os.path.join(RES, "macros.tex")).read()
    get = lambda k: float(re.search(r"pv@" + re.escape(k) + r"\\endcsname\{([^}]*)\}", mac).group(1))
    x2 = get("k2.x2")
    ok = abs((1 - math.exp(-x2) * (1 + x2)) - 0.9) < 1e-3 and abs(get("k2.x1") - math.log(10)) < 0.006
    ok &= abs(get("drift.ms") - 2 * 20e-6 * 3600 * 1e3) < 0.6
    ok &= abs(get("pre.ms") - (8 + 4.25) * 128 / 125e3 * 1e3) < 0.06
    ok &= abs(get("load.pct") - 30 * 400 * toa_s(7, 12 + 7 + 8) / 3600 * 100) < 0.6
    return ok, f"x2={x2}, drift={get('drift.ms')} ms, preamble={get('pre.ms')} ms, load={get('load.pct')} %"

# ------------------------------------------------------------------ #
def main():
    ok_all = True
    for fn in CHECKS:
        try:
            ok, msg = fn()
        except Exception as e:      # a crash is a failure, not a skip
            ok, msg = False, f"{type(e).__name__}: {e}"
        ok_all &= bool(ok)
        print(f"{'OK  ' if ok else 'FAIL'} {fn.__name__}: {msg}")
    print("ALL OK" if ok_all else "SOME CHECKS FAILED")
    return 0 if ok_all else 1

if __name__ == "__main__":
    sys.exit(main())
