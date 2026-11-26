"""
Node energy budget (M5). Reads results/connectivity.csv (first-hop relay load at RELAY_DENS) and writes
results/energy.csv. Average current = sleep + own heartbeat + mesh listening (one CAD per slot T_w)
+ hourly sync beacon (with clock-drift guard window) + relaying (receive + retransmit of forwarded
heartbeats) + temperature sampling + gas sampling (gas designs). Then: Li-SOCl2 AA lifetime, whether the
24 h PV average covers the load (low / high canopy-light case), supercapacitor autonomy and the
capacitance needed for SC_AUTONOMY_H hours without sun.
"""
import csv, math
import params as P
from lora import toa_ms

sf = P.ENERGY_SF
tsym = 2 ** sf / P.LORA_BW_HZ
toa_hb = toa_ms(sf, P.HB_PAYLOAD_B) / 1e3
toa_sync = toa_ms(sf, P.SYNC_PAYLOAD_B) / 1e3
e_sc = 0.5 * P.SC_F * (P.SC_V_MAX ** 2 - P.SC_V_MIN ** 2)                  # J usable

def components(temp, tw, fwd, gas):
    c = {}
    c["sleep"] = P.I_SLEEP_T[temp]
    c["own_tx"] = (P.I_TX14 * toa_hb + P.Q_MCU) / P.HEARTBEAT_S
    c["listen"] = (P.I_RX_A * (P.CAD_SYMBOLS * tsym + P.T_WAKE_RADIO_S) + P.I_MCU_A * P.T_MCU_WAKE_S) / tw
    guard = 2 * P.CLOCK_PPM * 1e-6 * P.SYNC_PERIOD_S
    c["sync"] = P.I_RX_A * (toa_sync + guard + P.T_WAKE_RADIO_S) / P.SYNC_PERIOD_S
    c["relay"] = fwd * ((P.I_RX_A + P.I_TX14) * toa_hb + P.Q_MCU) / P.HEARTBEAT_S
    c["temp"] = P.Q_TEMP / P.T_TEMP
    c["gas"] = P.Q_GAS / P.GAS_P_SELECTED_S if gas else 0.0
    return c

def lifetime_years(i, cap_ah, sd):
    cap_c = cap_ah * 3600
    return cap_c / (i * P.YEAR + sd * cap_c)

with open("results/connectivity.csv", newline="") as f:
    conn = {(r["deploy"], r["gw"]): r for r in csv.DictReader(f)
            if r["scen"] == "cons" and r["sf"] == str(sf) and r["area_ha"] == "400"
            and float(r["density_per_ha"]) == P.RELAY_DENS}
rows = []
cap, sd = P.BATT["Li-SOCl2 AA (2.6 Ah)"]
for (dep, gw), cr in sorted(conn.items()):
    for role in P.ENERGY_ROLES:
        load = 0.0 if role == "leaf" else float(cr["relay_load_" + role.split("_")[1]])
        fwd = max(load - 1.0, 0.0)                                         # load counts the relay itself
        for slot, tw in P.SLOT_TW_S.items():
            for temp in P.I_SLEEP_T:
                for design in ("heat", "gas"):
                    c = components(temp, tw, fwd, design == "gas")
                    i = sum(c.values())
                    p_mw = i * P.V * 1e3
                    row = dict(deploy=dep, scen="cons", gw=int(gw), role=role, forwarded=round(fwd, 1), slot=slot,
                               T_w_s=tw, temp=temp, design=design)
                    row.update({f"i_{k}_uA": round(v * 1e6, 3) for k, v in c.items()})
                    row.update(i_avg_uA=round(i * 1e6, 3), p_avg_mW=round(p_mw, 4),
                               life_LiSOCl2_yr=round(lifetime_years(i, cap, sd), 2),
                               pv_low_ok=int(p_mw <= P.P_HARVEST_MW["low"]), pv_high_ok=int(p_mw <= P.P_HARVEST_MW["high"]),
                               sc_autonomy_h=round(e_sc / (p_mw / 1e3) / 3600, 1),
                               sc_needed_F=round(2 * (p_mw / 1e3) * P.SC_AUTONOMY_H * 3600 / (P.SC_V_MAX ** 2 - P.SC_V_MIN ** 2), 1),
                               # A3: parallel Li-SOCl2 AA cells for RELAY_PACK_YEARS (each cell self-discharges sd/yr)
                               aa_cells_10yr=math.ceil(i * P.YEAR * P.RELAY_PACK_YEARS / (cap * 3600 * (1 - sd * P.RELAY_PACK_YEARS))),
                               # A3: PV cells of the assumed size needed for energy neutrality in high / low light
                               pv_cells_high=math.ceil(p_mw / P.P_HARVEST_MW["high"]),
                               pv_cells_low=math.ceil(p_mw / P.P_HARVEST_MW["low"]))
                    rows.append(row)
# A7: one-shot GNSS fix for scattered nodes (role = gnss_fix rows; other columns empty)
aa_j = cap * 3600 * P.V                                                     # usable AA energy (J)
pv_w = {k: v / 1e3 for k, v in P.P_HARVEST_MW.items()}
e_to_vmin = 0.5 * P.SC_F * P.SC_V_MIN ** 2                                 # empty supercap up to the regulator floor (J)
for t_fix in P.GNSS_FIX_S:
    for p_fix in P.GNSS_P_FIX:
        e1 = t_fix * P.GNSS_I_ACQ_A * P.V                                   # one attempt (J)
        tries = (1 - (1 - p_fix) ** P.GNSS_MAX_TRIES) / p_fix              # expected attempts, capped at MAX_TRIES
        e_exp = e1 * tries
        rows.append(dict(deploy="S", role="gnss_fix", gnss_fix_s=t_fix, gnss_p_fix=p_fix,
                         gnss_e_attempt_J=round(e1, 2), gnss_attempts_exp=round(tries, 2), gnss_e_exp_J=round(e_exp, 2),
                         gnss_p_fallback=round((1 - p_fix) ** P.GNSS_MAX_TRIES, 3),
                         gnss_aa_share_pct=round(e_exp / aa_j * 100, 3),
                         gnss_attempt_over_sc=round(e1 / e_sc, 2),
                         gnss_charge_h_low=round((e_to_vmin + e1) / pv_w["low"] / 3600, 1),
                         gnss_charge_h_high=round((e_to_vmin + e1) / pv_w["high"] / 3600, 1)))
fields = list(dict.fromkeys(k for r in rows for k in r))
with open("results/energy.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f"energy: {len(rows)} rows (incl. gnss_fix)")
