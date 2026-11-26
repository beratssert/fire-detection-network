#!/usr/bin/env python3
"""
Preliminary models for a low-cost forest-fire sensor network.

Everything here is a MODEL with stated, literature-derived parameters;
nothing is a field measurement. Outputs: results/*.csv, figures/*.pdf.
Deterministic: SEED = 2026.

Models
  1. Link budget -> radio range per LoRa spreading factor (log-distance
     path loss with log-normal shadowing) for two deployments (trunk-mounted,
     scattered) and two radio scenarios (optimistic, conservative).
  2. Multi-hop connectivity of a Poisson-scattered network to G gateways
     vs density (Monte Carlo, shadowed links, BFS hop counts, relay load).
  3. Detection probability vs density (exact Poisson integral, detect.py):
     heat-only vs heat + downwind gas sensing, fire as a disc growing at v.
  4. Energy budget: see energy.py (M5).
  5. Security overhead: airtime cost of AEAD tag length.
"""
import csv, math, os
import numpy as np
from scipy.spatial import cKDTree
from scipy.stats import norm
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import params

SEED = params.SEED
rng = np.random.default_rng(SEED)
os.makedirs("results", exist_ok=True)
os.makedirs("figures", exist_ok=True)

# ------------------------------------------------------------------ #
# PARAMETERS (values, sources and labels live in params.py)
# ------------------------------------------------------------------ #
F_MHZ      = params.F_MHZ
PL0_DB     = params.PL0_DB
TX_DBM     = params.TX_DBM
ANT_DB     = params.ANT_DB
DETUNE_DB  = params.DETUNE_DB
SIGMA_DB   = params.SIGMA_DB
FADE_Q     = params.FADE_Q
SENS       = params.SENS

def link_range(sf, n, margin_db, detune_db=DETUNE_DB):
    budget = TX_DBM - SENS[sf] + ANT_DB + detune_db - margin_db - PL0_DB
    return 10 ** (budget / (10 * n))

from lora import toa_ms     # LoRa time on air (Semtech AN1200.13)

# ------------------------------------------------------------------ #
# 1. RANGE (M1): per deployment (M trunk / S scattered) and radio scenario (opt / cons)
#    range50: median link range (no fade margin); range90: 90 % link reliability (FADE_Q sigma);
#    range90_rear: 90 % range when the link leaves through the node's own trunk (rear_db extra loss).
# ------------------------------------------------------------------ #
rows = []
for dep in params.DEPLOYS:
    for scen in params.SCENS:
        rp = params.RADIO[(dep, scen)]
        for sf in SENS:
            rows.append(dict(deploy=dep, scen=scen, n=rp["n"], sigma_db=rp["sigma_db"], sf=sf,
                             sens_dbm=round(SENS[sf], 1),
                             range50_m=round(link_range(sf, rp["n"], 0.0, rp["detune_db"]), 1),
                             range90_m=round(link_range(sf, rp["n"], FADE_Q * rp["sigma_db"], rp["detune_db"]), 1),
                             range90_rear_m=round(link_range(sf, rp["n"], FADE_Q * rp["sigma_db"] + rp["rear_db"], rp["detune_db"]), 1),
                             toa_hb_ms=round(toa_ms(sf, params.HB_PAYLOAD_B), 1)))
with open("results/range.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

# ------------------------------------------------------------------ #
# 2. CONNECTIVITY (M2): multi-hop reach to G gateways, Monte Carlo, shadowed links
#    Nodes: Poisson in a square. Link u-v exists if PL(d) + X + rear_u + rear_v <= budget,
#    X ~ N(0, sigma) per link, rear_* = rear_db with prob. REAR_FRACTION (trunk-mounted only).
#    Metric: fraction of nodes with a multi-hop path to any gateway (BFS from all gateways).
#    Relay load: nodes routed through each first-hop node (random shortest-path tree).
#    Mean degree <k> (single definition): analytic expected number of neighbours in the
#    infinite plane, lam * pi * r0^2 * exp(2 beta^2) * E[10^(-2 R / 10 n)], beta = sigma ln10 / (10 n).
# ------------------------------------------------------------------ #
from scipy.sparse.csgraph import shortest_path
SIDE_M = params.SIDE_M
crng = np.random.default_rng(params.CONN_SEED)

def gateways(side, g):
    if g == 1:
        return np.array([[side / 2, side / 2]])
    q = side / 4
    return np.array([[q, q], [3 * q, q], [q, 3 * q], [3 * q, 3 * q]])

def mean_degree(lam_ha, r0, rp):
    n, sig, rear = rp["n"], rp["sigma_db"], rp["rear_db"]
    beta = sig * math.log(10) / (10 * n)
    pr = params.REAR_FRACTION if rear > 0 else 0.0
    # E[10^(-2 R/(10 n))] with R = rear*(B1 + B2), B ~ Bernoulli(pr)
    e1 = (1 - pr) + pr * 10 ** (-2 * rear / (10 * n))
    return lam_ha / 1e4 * math.pi * r0 ** 2 * math.exp(2 * beta ** 2) * e1 ** 2

def conn_trial(lam_ha, r0, rp, side, gw):
    n, sig, rear = rp["n"], rp["sigma_db"], rp["rear_db"]
    N = crng.poisson(lam_ha * side ** 2 / 1e4)
    G = len(gw)
    pts = np.vstack([gw, crng.uniform(0, side, size=(N, 2))])
    is_node = np.r_[np.zeros(G, bool), np.ones(N, bool)]
    rear_on = is_node & (crng.random(G + N) < (params.REAR_FRACTION if rear > 0 else 0.0))
    dmax = r0 * 10 ** (params.DMAX_SIGMA_K * sig / (10 * n))
    pairs = cKDTree(pts).query_pairs(dmax, output_type="ndarray")
    if len(pairs):
        d = np.maximum(np.linalg.norm(pts[pairs[:, 0]] - pts[pairs[:, 1]], axis=1), params.LINK_D_MIN_M)
        extra = rear * (rear_on[pairs[:, 0]].astype(float) + rear_on[pairs[:, 1]])
        loss = 10 * n * np.log10(d / r0) + extra + crng.normal(0, sig, len(d))
        pairs = pairs[loss <= 0]
    M = G + N
    A = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(M, M)).tocsr()
    hops = shortest_path(A, directed=False, unweighted=True, indices=np.arange(G)).min(axis=0)[G:]
    ok = np.isfinite(hops)
    reach = ok.mean() if N else 0.0
    h = hops[ok]
    # random shortest-path tree: each node with hop k >= 2 picks a parent among neighbours with hop k-1
    hp = np.r_[np.zeros(G), hops]
    load = np.zeros(M)
    if len(pairs) and ok.any():
        u, v = pairs[:, 0], pairs[:, 1]
        cu = np.r_[u, v]; cv = np.r_[v, u]                 # child, candidate parent
        m = np.isfinite(hp[cu]) & (hp[cv] == hp[cu] - 1) & is_node[cu]
        cu, cv = cu[m], cv[m]
        order = crng.permutation(len(cu))
        cu, cv = cu[order], cv[order]
        first = np.unique(cu, return_index=True)[1]
        parent = np.full(M, -1); parent[cu[first]] = cv[first]
        load[G:][ok] = 1.0
        for k in range(int(h.max()), 0, -1):              # push subtree sizes up, deepest level first
            lvl = np.where(is_node & (hp == k))[0]
            np.add.at(load, parent[lvl], load[lvl]) if k > 1 else None
        first_hop = np.where(is_node & (hp == 1))[0]
        lmax = load[first_hop].max() if len(first_hop) else 0.0
        lmean = load[first_hop].mean() if len(first_hop) else 0.0
    else:
        lmax = lmean = 0.0
    return reach, (h.mean() if len(h) else np.nan), (np.quantile(h, 0.95) if len(h) else np.nan), \
        (h.max() if len(h) else np.nan), lmax, lmean

def ci95(x):
    x = np.asarray(x, float)
    return 1.96 * x.std(ddof=1) / math.sqrt(len(x))

conn_rows = []
def run_conn(dep, scen, sf, side, g, dens_list):
    rp = params.RADIO[(dep, scen)]
    r0 = link_range(sf, rp["n"], 0.0, rp["detune_db"])          # median range without rear loss
    for lam in dens_list:
        trials = params.TRIALS if lam * side ** 2 / 1e4 <= params.TRIALS_LARGE_N else params.TRIALS_LARGE
        res = np.array([conn_trial(lam, r0, rp, side, gateways(side, g)) for _ in range(trials)], float)
        reach = res[:, 0]
        conn_rows.append(dict(deploy=dep, scen=scen, sf=sf, gw=g, area_ha=round(side ** 2 / 1e4), density_per_ha=lam, trials=trials,
                              r0_m=round(r0, 1), mean_degree=round(mean_degree(lam, r0, rp), 2),
                              reach_mean=round(float(reach.mean()), 4), reach_ci95=round(float(ci95(reach)), 4),
                              hop_mean=round(float(np.nanmean(res[:, 1])), 2), hop_p95=round(float(np.nanmean(res[:, 2])), 2),
                              hop_max=round(float(np.nanmean(res[:, 3])), 2),
                              relay_load_max=round(float(np.mean(res[:, 4])), 1),
                              relay_load_mean=round(float(np.mean(res[:, 5])), 1)))

if __name__ == "__main__":       # connectivity is the slow part; never run it on import
    for dep in params.DEPLOYS:
        for scen in params.SCENS:
            for sf in params.CONN_SFS:
                dl = [x for x in params.DENS if sf != 12 or x <= params.CONN_SF12_MAX_DENS]
                for g in params.GW_COUNTS:
                    run_conn(dep, scen, sf, SIDE_M, g, dl)
    for dep in params.DEPLOYS:                                # edge-effect control (1600 ha, G = 4)
        run_conn(dep, "cons", params.CTRL_SF, params.CTRL_SIDE_M, params.CTRL_GW, params.DENS)
    with open("results/connectivity.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=conn_rows[0].keys()); w.writeheader(); w.writerows(conn_rows)

# ------------------------------------------------------------------ #
# 3. DETECTION (M3): exact Poisson integral (detect.py); P(detected by T) vs density
#    Base: ROS_BASE, T_BASE; heat-only for each r_T, gas designs at R_T_BASE.
# ------------------------------------------------------------------ #
import detect
det_rows = []
designs = [("heat", 0.0, rt) for rt in params.R_T_SCEN] + [("gas", rg, params.R_T_BASE) for rg in params.R_G_SCEN]
for kind, rg, rt in designs:
    kw = dict(T=params.T_BASE, v=params.ROS_BASE, r_T=rt, Ts_heat=params.TS_HEAT_MIN, r_G=rg,
              Ts_gas=params.TS_GAS_MIN, t_resp=params.GAS_RESP_MIN, theta=params.THETA if rg > 0 else 0.0,
              dr=params.DET_DR_M)
    I = detect.coverage_integral(**kw)
    mada = params.VENDOR_DRYAD_MADA_SENSORS / params.VENDOR_DRYAD_MADA_HA
    for lam in sorted(params.DET_DENS + [round(mada, 3)]):
        det_rows.append(dict(design=kind, r_G_m=rg, r_T_m=rt, ros=params.ROS_BASE, T_min=params.T_BASE,
                             density_per_ha=lam, p_detect=round(1 - math.exp(-lam / 1e4 * I), 4)))
with open("results/detection.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=det_rows[0].keys()); w.writeheader(); w.writerows(det_rows)

# ------------------------------------------------------------------ #
# 4. ENERGY: moved to energy.py (M5; needs the relay load from connectivity.csv)
# ------------------------------------------------------------------ #
V = params.V
I_TX14 = params.I_TX14

# ------------------------------------------------------------------ #
# 5. SECURITY (M6): AEAD tag airtime cost, forgery probability per try, key security, nonce layout
#    tag = 0 is a baseline WITHOUT authentication (CCM has no tag-less mode; SP 800-38C needs >= 4 B).
#    forgery_prob_per_try = 2^-(8 * tag) (SP 800-38C App. B.1). Key security against exhaustive search:
#    key_bits classically, about key_bits / 2 against Grover. AES energy is an ASSUMPTION (no source).
# ------------------------------------------------------------------ #
nonce_b = sum(b for _, b in params.SEC_NONCE_FIELDS)
nonce_txt = " || ".join(f"{n}({b})" for n, b in params.SEC_NONCE_FIELDS)
sec_rows = []
for tag in params.SEC_TAGS_B:
    for sf in params.SEC_SFS:
        pl = params.SEC_DATA_B + params.SEC_HDR_B + tag          # 12 B data + 7 B header (params.SEC_HDR_FIELDS)
        sec_rows.append(dict(cipher=params.SEC_CIPHER_LABEL if tag else "none (no authentication)",
                             tag_bytes=tag, sf=sf, phy_payload=pl,
                             toa_ms=round(toa_ms(sf, pl), 1),
                             tx_energy_mJ=round(I_TX14 * V * toa_ms(sf, pl), 2),
                             forgery_prob_per_try=(f"{2.0 ** (-8 * tag):.3g}" if tag else "1 (no check)"),
                             key_security_bits=(params.SEC_KEY_BITS if tag else 0),
                             key_security_grover_bits=(int(params.SEC_KEY_BITS * params.SEC_GROVER_FACTOR) if tag else 0),
                             nonce_bytes=(nonce_b if tag else 0), nonce_structure=(nonce_txt if tag else "-"),
                             aes_energy_uJ_assumed=(round(params.AES_I_A * V * (params.AES_CYCLES / params.AES_CLK_HZ) * 1e6, 4) if tag else 0.0)))
with open("results/security.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=sec_rows[0].keys()); w.writeheader(); w.writerows(sec_rows)

print("done")
