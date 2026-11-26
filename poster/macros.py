#!/usr/bin/env python3
"""
Write results/macros.tex: numbers used in poster.tex, taken from results/*.csv
(group A) and params.py (group B). No values are typed here; this script only
selects a CSV cell or a parameter and formats it the way the poster prints it.

Usage in poster.tex:  \\input{results/macros.tex}  ...  \\pv{range90.M.opt.sf7}\\,m
An unknown key stops the LaTeX run with an error.

Rounding uses Decimal with ROUND_HALF_UP (Python's round() is banker's rounding).
Run after models.py and reqdens.py.
"""
import csv, math
from decimal import Decimal, ROUND_HALF_UP
import params

def pick(fname, col, **where):
    """Return the CSV text in column `col` of the single row matching `where` (string compare)."""
    with open(f"results/{fname}", newline="") as f:
        rows = [r for r in csv.DictReader(f) if all(r[k] == v for k, v in where.items())]
    if len(rows) != 1:
        raise ValueError(f"{fname} {where}: {len(rows)} rows match, expected 1")
    return rows[0][col]

def fmt(x, step):
    """Round x (CSV text, Decimal or float) to `step` ("10", "1", "0.1", "0.01") and return text."""
    d = x if isinstance(x, Decimal) else Decimal(x if isinstance(x, str) else repr(x))
    q = d.quantize(Decimal(step) if step != "10" else Decimal("1E1"), rounding=ROUND_HALF_UP)
    return str(int(q)) if step in ("10", "1") else str(q)

V = {}   # key -> (text, source comment)
def put(key, text, src):
    if key in V:
        raise KeyError(f"duplicate key {key}")
    V[key] = (text, src)

# ------------------------------------------------------------------ #
# SELECTIONS: by label or value, never by index; a missing entry is an error
# ------------------------------------------------------------------ #
def by_value(seq, value, name):
    """Return the element of params.<name> equal to `value` (keeps the params type)."""
    seq = list(seq)
    if value not in seq:
        raise ValueError(f"params.{name} has no element {value!r}")
    return seq[seq.index(value)]

TAG_NONE  = by_value(params.SEC_TAGS_B, 0, "SEC_TAGS_B")
TAG_SHORT = by_value(params.SEC_TAGS_B, 4, "SEC_TAGS_B")
TAG_ALARM = by_value(params.SEC_TAGS_B, 8, "SEC_TAGS_B")
SF_RANGE  = [by_value(params.SENS, sf, "SENS") for sf in (7, 12)]
SF_SEC    = [by_value(params.SEC_SFS, sf, "SEC_SFS") for sf in (7, 10)]

# CSV text of the selectors. csv.DictWriter writes str(value), so the text
# depends on the Python type that the producing script used:
#   float -> str(float): 1.0 -> "1.0", 15.0 -> "15.0"
#   int   -> str(int):   5 -> "5", 300 -> "300"
def csv_int(x, name):
    if x != int(x):
        raise ValueError(f"{name}={x!r} is not a whole number")
    return str(int(x))
def csv_float(x):
    return str(float(x))

# ------------------------------------------------------------------ #
# A. FROM results/*.csv
# ------------------------------------------------------------------ #
# range.csv (M1): one row per (deploy, scen, sf).
for dep in params.DEPLOYS:
    for scen in params.SCENS:
        for sf in SF_RANGE:
            raw = pick("range.csv", "range90_m", deploy=dep, scen=scen, sf=csv_int(sf, "sf"))
            put(f"range90.{dep}.{scen}.sf{sf}", fmt(raw, "10"), f"range.csv {dep} {scen} sf={sf} range90_m={raw}, nearest 10")
for sf in SF_RANGE:
    raw = pick("range.csv", "range90_rear_m", deploy="M", scen="cons", sf=csv_int(sf, "sf"))
    put(f"range90rear.M.cons.sf{sf}", fmt(raw, "10"), f"range.csv M cons sf={sf} range90_rear_m={raw}, nearest 10")

# connectivity.csv (M2): threshold = lowest simulated density whose lower 95 % CI of the reach fraction
# is >= CONN_REACH_TARGET; hop counts and relay load at RELAY_DENS. All SF7.
def conn_rows_for(dep, scen, sf, gw, area):
    with open("results/connectivity.csv", newline="") as f:
        rs = [r for r in csv.DictReader(f) if (r["deploy"], r["scen"], r["sf"], r["gw"], r["area_ha"]) ==
              (dep, scen, str(sf), str(gw), str(area))]
    return sorted(rs, key=lambda r: float(r["density_per_ha"]))
area400 = csv_int(params.SIDE_M ** 2 / 1e4, "area")
area_ctrl = csv_int(params.CTRL_SIDE_M ** 2 / 1e4, "area")
for dep in params.DEPLOYS:
    for scen in params.SCENS:
        for gw in params.GW_COUNTS:
            rs = conn_rows_for(dep, scen, 7, gw, area400)
            hit = [r for r in rs if float(r["reach_mean"]) - float(r["reach_ci95"]) >= params.CONN_REACH_TARGET]
            if not hit:
                raise ValueError(f"no density reaches the target for {dep} {scen} G={gw}")
            floor = "$\\le$" if float(hit[0]["density_per_ha"]) == min(params.DENS) else ""
            put(f"thr.{dep}.{scen}.g{gw}", floor + hit[0]["density_per_ha"],
                f"connectivity.csv {dep} {scen} sf7 G={gw}: first density with reach_mean-ci95 >= {params.CONN_REACH_TARGET}")
            if scen == "cons" and gw == 1:
                put(f"kdeg.{dep}.cons.thr", fmt(hit[0]["mean_degree"], "1"), f"connectivity.csv mean_degree at that density")
    rs = conn_rows_for(dep, "cons", params.CTRL_SF, params.CTRL_GW, area_ctrl)
    hit = [r for r in rs if float(r["reach_mean"]) - float(r["reach_ci95"]) >= params.CONN_REACH_TARGET]
    put(f"thr.{dep}.cons.ctrl", ("$\\le$" if float(hit[0]["density_per_ha"]) == min(params.DENS) else "") + hit[0]["density_per_ha"], f"connectivity.csv {dep} cons 1600 ha G=4 threshold")
    for gw in params.GW_COUNTS:
        r = pick("connectivity.csv", "hop_p95", deploy=dep, scen="cons", sf="7", gw=str(gw), area_ha=area400,
                 density_per_ha=csv_float(params.RELAY_DENS))
        put(f"hop95.{dep}.cons.g{gw}", fmt(r, "1"), f"connectivity.csv {dep} cons sf7 G={gw} density={params.RELAY_DENS} hop_p95={r}")
        r = pick("connectivity.csv", "relay_load_mean", deploy=dep, scen="cons", sf="7", gw=str(gw), area_ha=area400,
                 density_per_ha=csv_float(params.RELAY_DENS))
        put(f"relay.{dep}.cons.g{gw}", fmt(r, "1"), f"connectivity.csv {dep} cons sf7 G={gw} relay_load_mean={r}")
put("relay.dens", fmt(params.RELAY_DENS, "1"), f"params.RELAY_DENS={params.RELAY_DENS!r}")
put("reach.target.pct", fmt(params.CONN_REACH_TARGET * 100, "1"), "params.CONN_REACH_TARGET*100")
put("conn.trials", fmt(params.TRIALS, "1"), "params.TRIALS")
put("ctrl.ha", fmt(params.CTRL_SIDE_M ** 2 / 1e4, "1"), "params.CTRL_SIDE_M**2/1e4")

# required_density.csv (M3): every row of the main grid and the theta sweep.
def vtxt(v):
    return fmt(v, "0.01").rstrip("0").rstrip(".")
with open("results/required_density.csv", newline="") as f:
    for r in csv.DictReader(f):
        d = "heat" if r["design"] == "heat" else f"gas{int(float(r['r_G_m']))}"
        th = "" if int(r["theta_deg"]) in (0, round(math.degrees(params.THETA))) else f".th{r['theta_deg']}"
        key = f"rd.{d}.rt{vtxt(r['r_T_m'])}.v{vtxt(r['ros'])}.T{int(float(r['T_min']))}{th}"
        val = float(r["req_density_per_ha"])
        put(key, fmt(r["req_density_per_ha"], "1" if val >= 10 else "0.1"), f"required_density.csv -> {r['req_density_per_ha']}")
# detection.csv: P(detected within T_BASE) at the Dryad Mada density (VENDOR)
mada = round(params.VENDOR_DRYAD_MADA_SENSORS / params.VENDOR_DRYAD_MADA_HA, 3)
put("mada.perha", fmt(mada, "0.1"), "VENDOR Dryad Mada 91 sensors / 78 ha")
with open("results/detection.csv", newline="") as f:
    for r in csv.DictReader(f):
        if float(r["density_per_ha"]) == mada:
            d = "heat" if r["design"] == "heat" else f"gas{int(float(r['r_G_m']))}"
            put(f"pdet.mada.{d}.rt{vtxt(r['r_T_m'])}", fmt(float(r["p_detect"]) * 100, "1"), f"detection.csv p_detect={r['p_detect']} at {mada}/ha, percent")

# latency.csv (M4)
with open("results/latency.csv", newline="") as f:
    for r in csv.DictReader(f):
        k = f"{r['deploy']}.{r['scen']}.g{r['gw']}.{r['slot']}"
        put(f"lat95.{k}", fmt(r["report_p95hops_worst_s"], "1"), f"latency.csv report_p95hops_worst_s={r['report_p95hops_worst_s']}")
        put(f"latmean.{k}", fmt(r["report_mean_s"], "1"), f"latency.csv report_mean_s={r['report_mean_s']}")
        if r["slot"] == "opt":
            put(f"dcmax.{r['deploy']}.{r['scen']}.g{r['gw']}", fmt(float(r["relay_dc_frac_max"]) * 100, "1"),
                f"latency.csv relay_dc_frac_max={r['relay_dc_frac_max']} -> percent of the hourly budget")
for name, tw in params.SLOT_TW_S.items():
    put(f"tw.{name}.s", fmt(tw, "1"), f"params.SLOT_TW_S[{name}]")
put("dc.pct", fmt(params.DC_LIMIT * 100, "1"), "params.DC_LIMIT*100")
put("dc.budget.s", fmt(params.DC_LIMIT * params.DC_TOBS_S, "1"), "DC_LIMIT*DC_TOBS_S seconds per hour")
put("lat.dens", fmt(params.LAT_DENS, "1"), "params.LAT_DENS")
put("hb.B", str(params.HB_PAYLOAD_B), "params.HB_PAYLOAD_B")
# D3 statements (derived from params, no new model)
put("drift.ms", fmt(2 * params.CLOCK_PPM * 1e-6 * params.SYNC_PERIOD_S * 1e3, "1"), "2 * CLOCK_PPM * SYNC_PERIOD_S")
_tsym7 = 2 ** 7 / params.LORA_BW_HZ
put("pre.ms", fmt((params.LORA_N_PRE + 4.25) * _tsym7 * 1e3, "0.1"), "(LORA_N_PRE + 4.25) Tsym at SF7")
put("pre.sym", str(params.LORA_N_PRE), "params.LORA_N_PRE")
_lo, _hi = 0.0, 50.0
for _ in range(200):                                   # solve P(N >= 2) = target for Poisson mean x
    _m = (_lo + _hi) / 2
    if 1 - math.exp(-_m) * (1 + _m) >= params.DETECT_TARGET_P: _hi = _m
    else: _lo = _m
_x1 = -math.log(1 - params.DETECT_TARGET_P)
put("k2.x2", fmt(_hi, "0.01"), "lambda*I for P(N>=2) = target"); put("k2.x1", fmt(_x1, "0.01"), "lambda*I for P(N>=1) = target")
put("k2.ratio", fmt(_hi / _x1, "0.1"), "ratio two-node / one-node confirmation")
from lora import toa_ms as _toa
put("load.dens", fmt(params.LOAD_EXAMPLE_DENS, "1"), "params.LOAD_EXAMPLE_DENS")
put("load.pct", fmt(params.LOAD_EXAMPLE_DENS * params.SIDE_M ** 2 / 1e4 * _toa(7, params.HB_PAYLOAD_B) / 1e3 / 3600 * 100, "1"), "LOAD_EXAMPLE_DENS * 400 ha * ToA(HB_PAYLOAD_B, SF7) / 3600 s")

# cost.csv (M7)
def dkey(d):
    return {"A heat, AA": "A", "B gas 50 m, PV": "Bpv", "C gas 100 m, PV": "Cpv", "B gas 50 m, AA": "Baa",
            "D Dryad density, PV": "D", "E heat 60 min, AA": "E"}[d]
with open("results/cost.csv", newline="") as f:
    for r in csv.DictReader(f):
        k = f"cost.{dkey(r['design'])}.{r['deploy']}.{r['bound']}" + ("" if r["pos_option"] != "gnss_once" else ".gnss")
        put(k + ".capha", fmt(r["capex_usd_per_ha"], "10" if float(r["capex_usd_per_ha"]) >= 100 else "1"), f"cost.csv capex_usd_per_ha={r['capex_usd_per_ha']}")
        put(k + ".tot", fmt(r["total_10yr_usd_per_ha_yr"], "1"), f"cost.csv total_10yr_usd_per_ha_yr={r['total_10yr_usd_per_ha_yr']}")
        put(k + ".share", fmt(float(r["relay_share"]) * 100, "1"), "cost.csv relay_share x100")
        put(k + ".pack", r["relay_pack_aa"], "cost.csv relay_pack_aa")
        if r["battery_life_yr"]:
            put(k + ".life", fmt(r["battery_life_yr"], "0.01"), "cost.csv battery_life_yr (2 decimals)")
        if r["replacements_10yr"] not in ("0", ""):
            put(k + ".repl", r["replacements_10yr"], "cost.csv replacements_10yr")
put("nsw.aud.ha.yr", fmt(params.NSW_CAMERA_AUD / params.NSW_CAMERA_YEARS / params.NSW_CAMERA_HA, "0.01"), "NSW camera network AUD per ha per year (upper bound of the funding)")
put("nsw.m.aud", fmt(params.NSW_CAMERA_AUD / 1e6, "0.1"), "NSW AUD millions"); put("nsw.yr", str(params.NSW_CAMERA_YEARS), "NSW years")
put("nsw.mha", fmt(params.NSW_CAMERA_HA / 1e6, "0.1"), "NSW Mha")
put("fg.eur.ha.yr", fmt(params.VENDOR_FORESTGUARD_EUR_PER_M2_YR * 1e4, "1"), "VENDOR ForestGuard EUR/m2/yr x 1e4")
put("cost.years", str(params.COST_YEARS), "params.COST_YEARS")
put("gnss.tries", str(params.GNSS_MAX_TRIES), "params.GNSS_MAX_TRIES")
put("gnss.pfix", "/".join(str(int(p * 100)) for p in params.GNSS_P_FIX), "params.GNSS_P_FIX x100")
put("gnss.ttff.s", fmt(params.GNSS_TTFF_COLD_S, "1"), "params.GNSS_TTFF_COLD_S")
put("gnss.mA", fmt(params.GNSS_I_ACQ_A * 1e3, "0.1"), "params.GNSS_I_ACQ_A x1e3")
put("gnss.usd.lo", fmt(params.GNSS_MODULE_USD[0] + params.GNSS_ANTENNA_USD[0] + params.GNSS_EXTRA_USD[0], "1"), "GNSS module+antenna+extra low")
put("gnss.usd.hi", fmt(params.GNSS_MODULE_USD[1] + params.GNSS_ANTENNA_USD[1] + params.GNSS_EXTRA_USD[1], "1"), "GNSS module+antenna+extra high")
put("relay.pack.years", str(params.RELAY_PACK_YEARS), "params.RELAY_PACK_YEARS")

# sensitivity_adv.csv (A6)
with open("results/sensitivity_adv.csv", newline="") as f:
    for r in csv.DictReader(f):
        put(f"adv.rg{int(float(r['r_G_m']))}.U{vtxt(r['U_mps'])}.pct", fmt(r["change_pct"], "1"), f"sensitivity_adv.csv change_pct={r['change_pct']}")
put("adv.U.lo", vtxt(min(params.ADV_U_MPS)), "min(params.ADV_U_MPS)"); put("adv.U.hi", vtxt(max(params.ADV_U_MPS)), "max(params.ADV_U_MPS)")

# security.csv: tag_bytes and sf are ints.
for sf in SF_SEC:
    for tag in (TAG_NONE, TAG_SHORT, TAG_ALARM):
        raw = pick("security.csv", "toa_ms", tag_bytes=csv_int(tag, "tag"), sf=csv_int(sf, "sf"))
        put(f"toa.tag{tag}.sf{sf}", raw, f"security.csv tag_bytes={tag} sf={sf} toa_ms (CSV text)")
sf_lo, sf_hi = SF_SEC
raw = pick("security.csv", "toa_ms", tag_bytes=csv_int(TAG_ALARM, "tag"), sf=csv_int(sf_lo, "sf"))
put(f"toa.tag{TAG_ALARM}.sf{sf_lo}.ms", fmt(raw, "1"), f"security.csv tag_bytes={TAG_ALARM} sf={sf_lo} toa_ms={raw}, integer (#3)")
t0 = Decimal(pick("security.csv", "toa_ms", tag_bytes=csv_int(TAG_NONE, "tag"), sf=csv_int(sf_hi, "sf")))
t8 = Decimal(pick("security.csv", "toa_ms", tag_bytes=csv_int(TAG_ALARM, "tag"), sf=csv_int(sf_hi, "sf")))
put(f"tagcost.tag{TAG_ALARM}.sf{sf_hi}.pct", fmt((t8 / t0 - 1) * 100, "1"), f"security.csv sf={sf_hi}: {t8}/{t0} - 1, percent")

# energy.csv (M5): every row; key en.<deploy>.g<G>.<role>.<slot>.<temp>.<design>.<quantity>
with open("results/energy.csv", newline="") as f:
    for r in csv.DictReader(f):
        if r["role"] == "gnss_fix":
            k = f"gnss.t{int(float(r['gnss_fix_s']))}.p{int(float(r['gnss_p_fix']) * 100)}"
            put(k + ".J", fmt(r["gnss_e_attempt_J"], "0.1"), "energy.csv gnss_e_attempt_J")
            put(k + ".sc", fmt(float(r["gnss_attempt_over_sc"]) * 100, "1"), "energy.csv gnss_attempt_over_sc x100")
            put(k + ".chlo", fmt(float(r["gnss_charge_h_low"]) / 24, "1"), "energy.csv gnss_charge_h_low / 24 (days)")
            put(k + ".chhi", fmt(r["gnss_charge_h_high"], "1"), "energy.csv gnss_charge_h_high (h)")
            put(k + ".fb", fmt(float(r["gnss_p_fallback"]) * 100, "0.1"), "energy.csv gnss_p_fallback x100")
            put(k + ".aa", fmt(r["gnss_aa_share_pct"], "0.01"), "energy.csv gnss_aa_share_pct")
            continue
        k = f"en.{r['deploy']}.g{r['gw']}.{r['role']}.{r['slot']}.{r['temp']}.{r['design']}"
        put(k + ".uW", fmt(float(r["p_avg_mW"]) * 1000, "1"), f"energy.csv p_avg_mW={r['p_avg_mW']} x1000")
        put(k + ".yr", fmt(r["life_LiSOCl2_yr"], "0.1" if float(r["life_LiSOCl2_yr"]) < 10 else "1"), f"energy.csv life_LiSOCl2_yr={r['life_LiSOCl2_yr']}")
        put(k + ".sch", fmt(r["sc_autonomy_h"], "1"), f"energy.csv sc_autonomy_h={r['sc_autonomy_h']}")
        put(k + ".scF", fmt(r["sc_needed_F"], "1"), f"energy.csv sc_needed_F={r['sc_needed_F']}")
        put(k + ".fwd", fmt(r["forwarded"], "1"), f"energy.csv forwarded={r['forwarded']}")
        put(k + ".aa", r["aa_cells_10yr"], "energy.csv aa_cells_10yr")
        put(k + ".pvh", r["pv_cells_high"], "energy.csv pv_cells_high")
        if r["role"] == "leaf" and r["deploy"] == "S" and r["gw"] == "1" and r["temp"] == "25C" and r["design"] == "heat":
            for comp in ("sleep", "own_tx", "listen", "sync", "temp"):
                put(f"ia.{comp}.{r['slot']}", fmt(r[f"i_{comp}_uA"], "0.1"), f"energy.csv i_{comp}_uA={r[f'i_{comp}_uA']}")

# ------------------------------------------------------------------ #
# B. FROM params.py
# ------------------------------------------------------------------ #
put("f.mhz", fmt(params.F_MHZ, "1"), f"params.F_MHZ={params.F_MHZ!r}")
put("tx.dbm", fmt(params.TX_DBM, "1"), f"params.TX_DBM={params.TX_DBM!r}")
for (dep, scen), rp in params.RADIO.items():
    put(f"nexp.{dep}.{scen}", fmt(rp["n"], "0.01") if rp["n"] != round(rp["n"], 1) else fmt(rp["n"], "0.1"),
        f"params.RADIO[{dep},{scen}].n={rp['n']!r}")
for scen in params.SCENS:
    put(f"sigma.{scen}.db", fmt(params.RADIO[("M", scen)]["sigma_db"], "0.1"), f"params.RADIO[M,{scen}].sigma_db")
    put(f"rear.{scen}.db", fmt(params.RADIO[("M", scen)]["rear_db"], "1"), f"params.RADIO[M,{scen}].rear_db")
# A1 anchors: measured total path loss vs the upper-bound scenario (868 MHz FSPL(1 m) intercept)
_f1 = 20 * math.log10(4 * math.pi * params.F_MHZ * 1e6 / 299792458.0)
_nu = params.RADIO[params.RADIO_UPPER]["n"]
for d in (params.FERREIRA_D_MAX_M, params.BOONLOM_D_MAX_M):
    meas = params.TX_DBM + params.ANCHOR_ANT_DBI_BOONLOM - (params.BOONLOM_RSSI_A_DBM - params.BOONLOM_RSSI_B_DB * math.log10(d))
    put(f"bl.pl.{int(d)}", fmt(meas, "1"), f"Boonlom fit PL at {d} m with 0 dBi antennas (ASSUMPTION)")
    put(f"up.pl.{int(d)}", fmt(_f1 + 10 * _nu * math.log10(d), "1"), f"upper-bound model PL at {d} m")
fe_lo = params.TX_DBM - params.FERREIRA_RSSI_DBM
put("fe.pl.lo", fmt(fe_lo, "1"), "Ferreira PL at 250 m, 0 dBi")
put("fe.pl.hi", fmt(fe_lo + 2 * params.FERREIRA_ANT_DBI, "1"), "Ferreira PL at 250 m, 7 dBi both ends")
put("fe.d.m", fmt(params.FERREIRA_D_MAX_M, "1"), "params.FERREIRA_D_MAX_M")
put("bl.d.m", fmt(params.BOONLOM_D_MAX_M, "1"), "params.BOONLOM_D_MAX_M")
put("trunk.h.m", fmt(params.TRUNK_H_M, "0.1"), f"params.TRUNK_H_M={params.TRUNK_H_M!r}")
put("fresnel.d.m", fmt(params.RANGE_FRESNEL_D_M, "1"), f"params.RANGE_FRESNEL_D_M={params.RANGE_FRESNEL_D_M!r}")
lam_m = 299792458.0 / (params.F_MHZ * 1e6)
r1 = math.sqrt(lam_m * (params.RANGE_FRESNEL_D_M / 2) ** 2 / params.RANGE_FRESNEL_D_M)
put("fresnel.r1.m", fmt(r1, "0.1"), f"first Fresnel radius at mid-path, d={params.RANGE_FRESNEL_D_M} m, f={params.F_MHZ} MHz: {r1!r}")
put("dryad.spacing.m", fmt(params.VENDOR_DRYAD_SPACING_MAX_M, "1"), "params.VENDOR_DRYAD_SPACING_MAX_M (VENDOR)")
put("ros.base", vtxt(params.ROS_BASE), "params.ROS_BASE m/min")
put("ros.lo", vtxt(params.ROS_SCEN[0]), "params.ROS_SCEN[0] (Kucuk 2012 lower end)")
put("ros.hi", vtxt(params.ROS_SCEN[-1]), "params.ROS_SCEN[-1] (Kucuk 2012 upper end)")
put("ros.wind.kmh", vtxt(params.ROS_WIND_DRIVEN_KMH), "params.ROS_WIND_DRIVEN_KMH (Coskuner 2026)")
put("ros.wind.mpm", fmt(params.ROS_WIND_DRIVEN_KMH * 1000 / 60, "1"), "km/h -> m/min")
put("side.ha", fmt(params.SIDE_M ** 2 / 1e4, "1"), f"params.SIDE_M**2/1e4={params.SIDE_M ** 2 / 1e4!r}")
put("rt.lo", vtxt(params.R_T_SCEN[0]), "params.R_T_SCEN[0]"); put("rt.base", vtxt(params.R_T_BASE), "params.R_T_BASE")
put("rt.hi", vtxt(params.R_T_SCEN[-1]), "params.R_T_SCEN[-1]")
for i, rg in enumerate(params.R_G_SCEN):
    put(f"rg.{i}", fmt(rg, "1"), f"params.R_G_SCEN[{i}]")
put("theta.deg", fmt(math.degrees(params.THETA), "1"), f"degrees(params.THETA)={math.degrees(params.THETA)!r}")
put("ts.heat.min", fmt(params.TS_HEAT_MIN, "1"), "params.TS_HEAT_MIN")
put("ts.gas.min", fmt(params.TS_GAS_MIN, "1"), "params.TS_GAS_MIN")
put("gas.resp.s", fmt(params.GAS_RESP_MIN * 60, "1"), "params.GAS_RESP_MIN*60 (BME688 ULP tau33-63)")
for T in params.T_SCEN:
    put(f"T.{int(T)}", fmt(T, "1"), "params.T_SCEN element")
put("t1.min", fmt(params.T_BASE, "1"), "params.T_BASE")
put("target.pct", fmt(params.DETECT_TARGET_P * 100, "1"), f"params.DETECT_TARGET_P*100={params.DETECT_TARGET_P * 100!r}")
put("fire.r.base.m", fmt(params.ROS_BASE * params.T_BASE, "1"), "ROS_BASE*T_BASE: fire radius at the base deadline")
put("fire.r.hi.m", fmt(params.ROS_SCEN[-1] * params.T_BASE, "1"), "ROS_SCEN[-1]*T_BASE")
put("fire.r.lo.m", fmt(params.ROS_SCEN[0] * params.T_BASE, "0.1"), "ROS_SCEN[0]*T_BASE")
for t, i in params.I_SLEEP_T.items():
    put(f"sleep.{t}.uA", fmt(i * 1e6, "0.1"), f"params.I_SLEEP_T[{t}]")
put("stop2.uA", fmt(params.STM32_STOP2_RTC_UA, "0.01"), "params.STM32_STOP2_RTC_UA (SNIPPET_ONLY source)")
put("tx.mA", fmt(params.I_TX14 * 1e3, "1"), f"params.I_TX14*1e3={params.I_TX14 * 1e3!r}")
# E9: per-frame energy, radio vs AES (SF7 alarm frame without tag and with the 8 B tag; AES from params ASSUMPTIONs #22)
for _nm, _tag in (("lo", TAG_NONE), ("hi", TAG_ALARM)):
    put(f"tx.frame.mJ.{_nm}", fmt(params.I_TX14 * params.V * _toa(params.LAT_SF, params.SEC_DATA_B + params.SEC_HDR_B + _tag) / 1e3 * 1e3, "0.1"),
        f"I_TX14 * V * ToA(SF{params.LAT_SF}, {params.SEC_DATA_B}+{params.SEC_HDR_B}+{_tag} B), mJ")
put("aes.uJ", fmt(params.AES_I_A * params.V * params.AES_CYCLES / params.AES_CLK_HZ * 1e6, "0.1"), "AES_I_A * V * AES_CYCLES / AES_CLK_HZ, uJ (ASSUMPTION #22)")
put("aes.mA", fmt(params.AES_I_A * 1e3, "1"), "params.AES_I_A"); put("aes.cyc", str(params.AES_CYCLES), "params.AES_CYCLES")
put("aes.MHz", fmt(params.AES_CLK_HZ / 1e6, "1"), "params.AES_CLK_HZ")
put("rx.mA", fmt(params.I_RX_A * 1e3, "0.1"), "params.I_RX_A*1e3")
put("temp.min", fmt(params.T_TEMP / 60, "1"), f"params.T_TEMP/60={params.T_TEMP / 60!r}")
put("qgas.mC", fmt(params.Q_GAS * 1e3, "1"), f"params.Q_GAS*1e3={params.Q_GAS * 1e3!r}")
put("igas.mA", fmt(params.I_GAS_AVG_A * 1e3, "0.01"), "params.I_GAS_AVG_A*1e3")
put("gas.uW.33", fmt(params.I_GAS_AVG_A * params.V * 1e6, "1"), "I_GAS_AVG_A * V (model)")
put("gas.uW.buck", fmt(params.I_GAS_AVG_A * params.GAS_VDD_LOW_V / params.BUCK_EFF * 1e6, "1"), "I_GAS_AVG_A * 1.8 V / BUCK_EFF (sensitivity)")
put("vsup", fmt(params.V, "0.1"), "params.V")
put("gas.vdd", fmt(params.GAS_VDD_LOW_V, "0.1"), "params.GAS_VDD_LOW_V"); put("buck.eff", fmt(params.BUCK_EFF * 100, "1"), "params.BUCK_EFF x100")
put("dens.min", str(min(params.DENS)), "min(params.DENS)"); put("dens.max", str(max(params.DENS)), "max(params.DENS)")
put("gasp.min", fmt(params.GAS_P_SELECTED_S / 60, "1"), f"params.GAS_P_SELECTED_S/60")
for k, v in params.PV_PEAK_MW.items():
    put(f"pv.peak.{k}.mW", fmt(v, "0.001"), f"params.PV_PEAK_MW[{k}]")
    put(f"pv.avg.{k}.uW", fmt(params.P_HARVEST_MW[k] * 1000, "1"), f"params.P_HARVEST_MW[{k}] x1000")
put("pv.h", fmt(params.PV_HARVEST_H, "1"), "params.PV_HARVEST_H")
_cap, _sd = params.BATT["Li-SOCl2 AA (2.6 Ah)"]
put("aa10.uW", fmt((_cap * 3600 / (10 * params.YEAR) - _sd * _cap * 3600 / params.YEAR) * params.V * 1e6, "1"), "power that empties one AA in 10 yr (same formula as figures.py)")
put("sc.F", fmt(params.SC_F, "1"), "params.SC_F"); put("sc.vmax", fmt(params.SC_V_MAX, "0.1"), "params.SC_V_MAX")
put("sc.vmin", fmt(params.SC_V_MIN, "0.1"), "params.SC_V_MIN"); put("sc.auto.h", fmt(params.SC_AUTONOMY_H, "1"), "params.SC_AUTONOMY_H")
put("sync.h", fmt(params.SYNC_PERIOD_S / 3600, "1"), "params.SYNC_PERIOD_S/3600"); put("sync.s", fmt(params.SYNC_PERIOD_S, "1"), "params.SYNC_PERIOD_S"); put("clock.ppm", fmt(params.CLOCK_PPM, "1"), "params.CLOCK_PPM")
for tag in (TAG_SHORT, TAG_ALARM):
    raw = pick("security.csv", "forgery_prob_per_try", tag_bytes=csv_int(tag, "tag"), sf="7")
    put(f"forge.tag{tag}.exp", str(8 * tag), f"security.csv forgery_prob_per_try={raw} = 2^-{8 * tag}")
put("key.bits", str(params.SEC_KEY_BITS), "params.SEC_KEY_BITS")
put("key.grover.bits", str(int(params.SEC_KEY_BITS * params.SEC_GROVER_FACTOR)), "SEC_KEY_BITS*SEC_GROVER_FACTOR")
put("nonce.B", str(sum(b for _, b in params.SEC_NONCE_FIELDS)), "sum of params.SEC_NONCE_FIELDS bytes")
for nm, b in params.SEC_NONCE_FIELDS:
    put(f"nonce.{nm}.B", str(b), f"params.SEC_NONCE_FIELDS {nm}")
put("th.lo", str(min(params.THETA_SWEEP_DEG)), "min(params.THETA_SWEEP_DEG)")
put("th.hi", str(max(params.THETA_SWEEP_DEG)), "max(params.THETA_SWEEP_DEG)")
put("detune.db", fmt(-params.RADIO[("S", "cons")]["detune_db"], "1"), "-params.RADIO[S,*].detune_db (printed with a minus sign)")
put("cad.sym", str(params.CAD_SYMBOLS), "params.CAD_SYMBOLS")
put("hdr.B", fmt(params.SEC_HDR_B, "1"), "params.SEC_HDR_B")
for nm, b in params.SEC_HDR_FIELDS:
    put(f"hdr.{nm}.B", str(b), f"params.SEC_HDR_FIELDS {nm}")
put("flash.kcycles", str(params.STM32_FLASH_ENDURANCE_KCYCLES), "params.STM32_FLASH_ENDURANCE_KCYCLES")
put("tag.short", fmt(TAG_SHORT, "1"), f"params.SEC_TAGS_B element {TAG_SHORT!r} B")
put("tag.alarm", fmt(TAG_ALARM, "1"), f"params.SEC_TAGS_B element {TAG_ALARM!r} B")
put("data.B", fmt(params.SEC_DATA_B, "1"), f"params.SEC_DATA_B={params.SEC_DATA_B!r}")
# B+ (bound on request; values still unverified)

# ------------------------------------------------------------------ #
# WRITE
# ------------------------------------------------------------------ #
with open("results/macros.tex", "w") as f:
    f.write("% GENERATED by macros.py from results/*.csv and params.py. Do not edit.\n")
    f.write("\\newcommand{\\pv}[1]{\\ifcsname pv@#1\\endcsname\\csname pv@#1\\endcsname"
            "\\else\\PackageError{macros}{Undefined value key '#1'}{Run macros.py; check the key.}\\fi}\n")
    for key, (text, src) in V.items():
        f.write(f"\\expandafter\\def\\csname pv@{key}\\endcsname{{{text}}}% {src}\n")
print(f"macros: {len(V)} keys")
