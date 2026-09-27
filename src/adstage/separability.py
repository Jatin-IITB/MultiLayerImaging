"""Two-class separability of a scalar under noise (Gaussian approximations)."""
from __future__ import annotations

import itertools

import numpy as np


def fisher(ma, sa, mb, sb) -> float:
    return (ma - mb) ** 2 / max(sa ** 2 + sb ** 2, 1e-300)


def bhattacharyya(ma, sa, mb, sb) -> float:
    va, vb = max(sa ** 2, 1e-300), max(sb ** 2, 1e-300)
    v = 0.5 * (va + vb)
    return 0.125 * (ma - mb) ** 2 / v + 0.5 * np.log(v / np.sqrt(va * vb))


def bayes_error(ma, sa, mb, sb, n: int = 20001) -> float:
    """Error of the Bayes rule for two equal-prior Gaussians: 0.5 ∫ min(p_a, p_b) dx."""
    sa, sb = max(sa, 1e-300), max(sb, 1e-300)
    lo = min(ma - 10 * sa, mb - 10 * sb)
    hi = max(ma + 10 * sa, mb + 10 * sb)
    x = np.linspace(lo, hi, n)
    pa = np.exp(-0.5 * ((x - ma) / sa) ** 2) / (sa * np.sqrt(2 * np.pi))
    pb = np.exp(-0.5 * ((x - mb) / sb) ** 2) / (sb * np.sqrt(2 * np.pi))
    return float(0.5 * np.trapezoid(np.minimum(pa, pb), x))


def pairwise(groups: dict[str, list[int]], noisy: dict[int, np.ndarray],
             clean_per_ant: dict[int, np.ndarray]) -> list[dict]:
    """Pairwise stats between class groups for one scalar metric.

    groups:        class name -> simulation indices
    noisy:         sim -> (R,) ring-mean values over noise realisations
    clean_per_ant: sim -> (n_ant,) noise-free per-antenna values (n_ant = 1 for matrix-level)

    J_meas  = Fisher ratio from the pooled noisy realisations (measurement noise, plus the
              between-simulation spread inside merged classes).
    port_sd = rms over the group's sims of the across-antenna std (numerical asymmetry).
    gap_over_port = |Δμ| / sqrt((port_sd_a^2 + port_sd_b^2) / 2).
    J_eff   = Δμ^2 / (σ_a^2 + σ_b^2 + port_sd_a^2 + port_sd_b^2), which treats the numerical
              asymmetry as extra per-measurement variance (conservative).
    """
    stats = {}
    for g, sims in groups.items():
        x = np.concatenate([noisy[s] for s in sims])
        pa = [clean_per_ant[s] for s in sims]
        port = (np.sqrt(np.mean([np.var(p, ddof=1) for p in pa]))
                if all(p.size > 1 for p in pa) else np.nan)
        stats[g] = (x.mean(), x.std(ddof=1), port)
    rows = []
    for a, b in itertools.combinations(groups, 2):
        ma, sa, pa = stats[a]
        mb, sb, pb = stats[b]
        gap = abs(ma - mb)
        rows.append({
            "pair": f"{a}|{b}", "mu_a": ma, "mu_b": mb, "sd_a": sa, "sd_b": sb, "gap": gap,
            "J_meas": fisher(ma, sa, mb, sb), "bhatt": bhattacharyya(ma, sa, mb, sb),
            "bayes_err": bayes_error(ma, sa, mb, sb),
            "port_sd_a": pa, "port_sd_b": pb,
            "gap_over_port": gap / np.sqrt(0.5 * (pa ** 2 + pb ** 2)) if np.isfinite(pa + pb) else np.nan,
            "J_eff": (gap ** 2 / (sa ** 2 + sb ** 2 + pa ** 2 + pb ** 2)
                      if np.isfinite(pa + pb) else np.nan),
        })
    return rows
