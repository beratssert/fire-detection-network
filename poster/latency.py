"""
Alarm reporting latency over the mesh and duty-cycle load of first-hop relays (M4).
Reads results/connectivity.csv (hop counts, relay load at LAT_DENS) and writes results/latency.csv.
Per hop: wait for the receiver's next listen slot, U(0, T_w), plus frame airtime.
  mean report delay  = hop_mean * (T_w / 2 + ToA)
  p95-hop worst case = hop_p95  * (T_w + ToA)
Relay duty cycle: (1 + relay_load) heartbeats per hour, each of ToA(heartbeat), against DC_LIMIT * T_obs.
"""
import csv, math
import params
from lora import toa_ms

alarm_b = params.SEC_DATA_B + params.SEC_HDR_B + 8           # 12 B data + 7 B header + 8 B tag
toa_a = toa_ms(params.LAT_SF, alarm_b) / 1e3
toa_hb = toa_ms(params.LAT_SF, params.HB_PAYLOAD_B) / 1e3
budget = params.DC_LIMIT * params.DC_TOBS_S
rows = []
with open("results/connectivity.csv", newline="") as f:
    conn = [r for r in csv.DictReader(f) if r["sf"] == str(params.LAT_SF) and r["area_ha"] == "400"
            and float(r["density_per_ha"]) == params.LAT_DENS]
for r in conn:
    for tw_name, tw in params.SLOT_TW_S.items():
        hm, h95, hmax = float(r["hop_mean"]), float(r["hop_p95"]), float(r["hop_max"])
        lmean, lmax = float(r["relay_load_mean"]), float(r["relay_load_max"])
        rows.append(dict(deploy=r["deploy"], scen=r["scen"], gw=r["gw"], slot=tw_name, T_w_s=tw,
                         hop_mean=hm, hop_p95=h95, hop_max=hmax, toa_alarm_ms=round(toa_a * 1e3, 1),
                         report_mean_s=round(hm * (tw / 2 + toa_a), 1),
                         report_p95hops_worst_s=round(h95 * (tw + toa_a), 1),
                         report_maxhops_worst_s=round(hmax * (tw + toa_a), 1),
                         relay_airtime_mean_s_per_h=round((1 + lmean) * toa_hb, 2),
                         relay_airtime_max_s_per_h=round((1 + lmax) * toa_hb, 2),
                         relay_dc_frac_max=round((1 + lmax) * toa_hb / budget, 3)))
with open("results/latency.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"latency: {len(rows)} rows")
