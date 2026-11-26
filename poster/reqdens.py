"""
Required density (nodes / ha) for DETECT_TARGET_P detection within T minutes (M3).
Exact Poisson integral (detect.py): lam = -ln(1 - p) / I(T). No Monte Carlo, no import of models.py.
Grid: heat-only (r_T) and gas (r_G x r_T) designs x ROS x T, plus a plume half-angle sweep at the base case.
"""
import csv, math
import detect
import params

rows = []
def add(kind, rg, rt, v, T, theta_deg):
    kw = dict(T=T, v=v, r_T=rt, Ts_heat=params.TS_HEAT_MIN, r_G=rg, Ts_gas=params.TS_GAS_MIN,
              t_resp=params.GAS_RESP_MIN, theta=math.radians(theta_deg) if rg > 0 else 0.0, dr=params.DET_DR_M)
    rows.append(dict(design=kind, r_G_m=rg, r_T_m=rt, ros=v, T_min=T, theta_deg=theta_deg if rg > 0 else 0,
                     req_density_per_ha=round(detect.required_density_ha(params.DETECT_TARGET_P, **kw), 3)))

theta0 = round(math.degrees(params.THETA))
for v in params.ROS_SCEN:
    for T in params.T_SCEN:
        for rt in params.R_T_SCEN:
            add("heat", 0.0, rt, v, T, 0)
            for rg in params.R_G_SCEN:
                add("gas", rg, rt, v, T, theta0)
for th in params.THETA_SWEEP_DEG:                     # sensitivity to the plume half-angle (base case)
    if th == theta0:
        continue
    for rg in params.R_G_SCEN:
        add("gas", rg, params.R_T_BASE, params.ROS_BASE, params.T_BASE, th)
with open("results/required_density.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"reqdens: {len(rows)} rows")

# A6 sensitivity (does not touch the base CSV): gas transport delay t_adv = min(r, r_G) / U at the base case
adv = []
for rg in params.ADV_RG_M:
    base_kw = dict(T=params.T_BASE, v=params.ROS_BASE, r_T=params.R_T_BASE, Ts_heat=params.TS_HEAT_MIN, r_G=rg,
                   Ts_gas=params.TS_GAS_MIN, t_resp=params.GAS_RESP_MIN, theta=params.THETA, dr=params.DET_DR_M)
    d0 = detect.required_density_ha(params.DETECT_TARGET_P, **base_kw)
    for U in params.ADV_U_MPS:
        d1 = detect.required_density_ha(params.DETECT_TARGET_P, adv_U_mps=U, **base_kw)
        adv.append(dict(r_G_m=rg, U_mps=U, ros=params.ROS_BASE, T_min=params.T_BASE, r_T_m=params.R_T_BASE,
                        req_density_base=round(d0, 3), req_density_adv=round(d1, 3), change_pct=round((d1 / d0 - 1) * 100, 1)))
with open("results/sensitivity_adv.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=adv[0].keys()); w.writeheader(); w.writerows(adv)
print(f"sensitivity_adv: {len(adv)} rows")
