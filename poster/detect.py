"""
Detection model (M3): exact Poisson integral, no Monte Carlo.

Fire: a disc growing from a point ignition at constant rate of spread v (m/min).
Nodes: Poisson field of density lam (nodes / m^2). A node at distance r detects
  - by heat when the fire edge is within r_T of it, after a uniform sampling delay U(0, Ts_heat);
  - by gas (gas designs only, and only if it lies in the downwind sector of half-angle theta)
    when the edge is within r_G, after a response delay t_resp plus U(0, Ts_gas).
The two sampling phases are independent. For one node,
  p_heat(r, T) = clip((T - max(r - r_T, 0)/v) / Ts_heat, 0, 1)
  p_gas(r, T)  = clip((T - t_resp - max(r - r_G, 0)/v) / Ts_gas, 0, 1)
Expected number of nodes that have detected by T:
  E = lam * [ (1 - f) * Int p_heat dA + f * Int (1 - (1 - p_heat)(1 - p_gas)) dA ],  f = theta/pi (0 for heat-only)
P(detected by T) = 1 - exp(-E); required density for target p: lam = -ln(1 - p) / I, I = E / lam.
Report (radio) delay is not included here; see the latency model (M4).
The base model has no gas transport delay; adv_U_mps adds t_adv = min(r, r_G) / U for the A6 sensitivity only.
"""
import math
import numpy as np

def _clip01(x):
    return np.clip(x, 0.0, 1.0)

def coverage_integral(T, v, r_T, Ts_heat, r_G=0.0, Ts_gas=1.0, t_resp=0.0, theta=0.0, dr=0.01, adv_U_mps=None):
    """I(T) in m^2: expected detecting nodes per unit density (lam = 1 node / m^2)."""
    r_max = max(r_G, r_T) + v * T + dr
    r = np.arange(0.0, r_max, dr) + dr / 2                      # midpoint rule
    ring = 2 * math.pi * r * dr
    p_h = _clip01((T - np.maximum(r - r_T, 0.0) / v) / Ts_heat)
    if r_G <= 0:
        return float(np.sum(p_h * ring))
    t_adv = 0.0 if adv_U_mps is None else np.minimum(r, r_G) / adv_U_mps / 60.0   # A6 sensitivity only: gas travel from the
    # fire edge (at most r_G away when it enters the node's gas range) to the node at under-canopy wind U (min)
    p_g = _clip01((T - t_resp - t_adv - np.maximum(r - r_G, 0.0) / v) / Ts_gas)
    f = theta / math.pi
    both = 1 - (1 - p_h) * (1 - p_g)
    return float(np.sum(((1 - f) * p_h + f * both) * ring))

def p_detect(lam_ha, **kw):
    return 1.0 - math.exp(-lam_ha / 1e4 * coverage_integral(**kw))

def required_density_ha(target, **kw):
    return -math.log(1.0 - target) / coverage_integral(**kw) * 1e4
