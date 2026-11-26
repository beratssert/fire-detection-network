"""
Cost model (M7): capital cost per ha and 10-year total for designs A-E and both deployments.
Inputs: params.COST (USD, low/high; SOURCE prices from search summaries or ESTIMATE ranges),
required_density.csv (base case), energy.csv (leaf lifetime for battery replacements).
Writes results/cost.csv. Every output is a model estimate, not a quote.
"""
import csv, math
import params as P

def pick(fname, **w):
    with open(f"results/{fname}", newline="") as f:
        rs = [r for r in csv.DictReader(f) if all(r[k] == str(v) for k, v in w.items())]
    assert len(rs) == 1, (fname, w, len(rs))
    return rs[0]

base = dict(r_T_m=P.R_T_BASE, ros=P.ROS_BASE, T_min=P.T_BASE)
dens = {
    "A heat, AA":       float(pick("required_density.csv", design="heat", r_G_m=0.0, theta_deg=0, **base)["req_density_per_ha"]),
    "B gas 50 m, PV":   float(pick("required_density.csv", design="gas", r_G_m=50.0, theta_deg=30, **base)["req_density_per_ha"]),
    "C gas 100 m, PV":  float(pick("required_density.csv", design="gas", r_G_m=100.0, theta_deg=30, **base)["req_density_per_ha"]),
    "B gas 50 m, AA":   float(pick("required_density.csv", design="gas", r_G_m=50.0, theta_deg=30, **base)["req_density_per_ha"]),
    "D Dryad density, PV": P.VENDOR_DRYAD_MADA_SENSORS / P.VENDOR_DRYAD_MADA_HA,
    "E heat 60 min, AA": float(pick("required_density.csv", design="heat", r_G_m=0.0, theta_deg=0,
                                    **dict(base, T_min=P.DESIGN_E_T_MIN))["req_density_per_ha"]),   # E6: as A, 60 min deadline
}
parts = {
    "A heat, AA":       ["radio_mcu", "temp_rh", "battery_aa", "enclosure_pcb_antenna"],
    "B gas 50 m, PV":   ["radio_mcu", "bme688", "temp_rh", "pv_cell", "supercap", "enclosure_pcb_antenna"],
    "C gas 100 m, PV":  ["radio_mcu", "bme688", "temp_rh", "pv_cell", "supercap", "enclosure_pcb_antenna"],
    "B gas 50 m, AA":   ["radio_mcu", "bme688", "temp_rh", "battery_aa", "enclosure_pcb_antenna"],
    "D Dryad density, PV": ["radio_mcu", "bme688", "temp_rh", "pv_cell", "supercap", "enclosure_pcb_antenna"],
    "E heat 60 min, AA": ["radio_mcu", "temp_rh", "battery_aa", "enclosure_pcb_antenna"],
}
rows = []
for design, lam in dens.items():
  for dep in P.DEPLOYS:
    for pos in P.POS_OPTIONS[dep]:
          g = P.COST_GW[dep]
          # leaf battery life (T_w optimistic = more listening, 25 C) for battery designs
          life = None
          if "AA" in design:
              e = pick("energy.csv", deploy=dep, gw=g, role="leaf", slot="opt", temp="25C",
                       design="heat" if design[0] in "AE" else "gas")
              life = float(e["life_LiSOCl2_yr"])
          # A3: first-hop relays = nodes / mean relay load (ratio independent of density); each relay gets a Li-SOCl2 AA pack
          # sized for the busiest relay (energy.csv, T_w optimistic = more listening, 25 C) instead of its leaf power parts
          cr = pick("connectivity.csv", deploy=dep, scen="cons", sf=7, gw=g, area_ha=400, density_per_ha=P.RELAY_DENS)
          relay_share = 1.0 / float(cr["relay_load_mean"])
          er = pick("energy.csv", deploy=dep, gw=g, role=P.RELAY_SIZING_ROLE, slot="opt", temp="25C",
                    design="heat" if design[0] in "AE" else "gas")
          pack = int(er["aa_cells_10yr"])
          for b, bound in enumerate(("low", "high")):
              n = lam * P.COST_AREA_HA
              gnss = (P.GNSS_MODULE_USD[b] + P.GNSS_ANTENNA_USD[b] + P.GNSS_EXTRA_USD[b]) if pos == "gnss_once" else 0.0
              leaf_unit = sum(P.COST[k][b] for k in parts[design]) + gnss
              power_parts = [k for k in parts[design] if k in ("battery_aa", "pv_cell", "supercap")]
              relay_unit = leaf_unit - sum(P.COST[k][b] for k in power_parts) + pack * P.COST["battery_aa"][b]
              unit = (1 - relay_share) * leaf_unit + relay_share * relay_unit
              inst = P.COST["install_" + dep][b]
              capex_nodes = n * (unit + inst)
              capex_gw = g * (P.COST["gateway"][b] + P.COST["gw_solar_mast"][b])
              repl = max(math.ceil(P.COST_YEARS / life) - 1, 0) if life else 0
              per_repl = (P.COST["battery_aa"][b] + P.COST["service_visit"][b]) if dep == "M" else (leaf_unit + inst)  # S: re-scatter a leaf
              opex = n * (1 - relay_share) * repl * per_repl + g * P.COST["gw_data_month"][b] * 12 * P.COST_YEARS \
                  + n * 24 * 365.25 * P.COST_YEARS / 1e6 * P.CLOUD_USD_PER_MILLION_MSG
              capex = capex_nodes + capex_gw
              rows.append(dict(design=design, deploy=dep, pos_option=pos, bound=bound, nodes_per_ha=round(lam, 2), nodes_400ha=round(n),
                               gateways=g, relay_share=round(relay_share, 3), relay_pack_aa=pack,
                               leaf_unit_usd=round(leaf_unit, 2), relay_unit_usd=round(relay_unit, 2),
                               node_unit_usd=round(unit, 2), install_usd_per_node=inst,
                               battery_life_yr=(life if life else ""), replacements_10yr=repl,
                               capex_usd=round(capex), capex_usd_per_ha=round(capex / P.COST_AREA_HA, 1),
                               opex_10yr_usd=round(opex),
                               total_10yr_usd_per_ha_yr=round((capex + opex) / P.COST_AREA_HA / P.COST_YEARS, 2)))
with open("results/cost.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"cost: {len(rows)} rows")
