"""Raw-data detectability of each stage against the noise-only floor (no imaging).

For a stage, x = whitened reciprocal-pair difference spectra dS / sigma, sigma = std of the
difference of two noisy measurements (noise model, 'typical'). Reported:
  * matched-filter SNR  = |x_clean| (known signal shape; the best any detector can do);
  * energy detector     = |x_draw|^2 of noisy draws vs noise-only draws: AUC and the fraction of
                          stage draws above the 95th percentile of noise-only draws;
  * k = 3 scalar (M5.C3, full-band opposite-antenna power, dB): AUC Normal-vs-stage draws.
Context: the same whitened size for the difference between two HFSS solves of the *same* Normal
design (v2 re-solve minus the archived v1 solve, on their common band). It is an upper bound on
solve-to-solve (mesh/sweep) variation; what else changed between the solves is not recorded.
"""
from __future__ import annotations

import numpy as np

from .beamform import pair_signals
from .common import N_ANT, ROOT, load_stages, noisy, pairs_at_distance
from .study_i2 import pair_sigma_f
from .timedomain import pair_list
from .common import PROFILES


def _auc(pos, neg):
    """P(pos > neg) (Mann-Whitney), ties count half."""
    pos, neg = np.asarray(pos), np.asarray(neg)
    gt = (pos[:, None] > neg[None, :]).mean()
    eq = (pos[:, None] == neg[None, :]).mean()
    return float(gt + 0.5 * eq)


def _norms(x, kp):
    """|x| over all pairs and per ring distance; x (21, F)."""
    out = {"all": float(np.linalg.norm(x))}
    for k in range(4):
        out[f"k{k}"] = float(np.linalg.norm(x[kp[k]]))
    return out


def run(sd, profile="typical", n_draw=200, seed=5500, v1_config="imaging/configs/v1_archive.yaml"):
    prof = PROFILES[profile]
    f = sd.f_hz
    sig = pair_sigma_f(sd.S["Normal"], prof)                              # (21, F)
    pl = pair_list(N_ANT)
    kp = {k: [i for i, (a, b) in enumerate(pl) if sd.kmat[a, b] == k] for k in range(4)}
    k3 = pairs_at_distance(sd.port_to_ant, 3)
    stages = [s for s in ("MCI", "Mild", "Moderate", "Severe") if s in sd.S]

    def c3(S):
        return float(10 * np.log10(np.mean([np.mean(np.abs(S[:, i, j]) ** 2) for i, j in k3])))

    nN = noisy(f, sd.S["Normal"], profile, n_draw, seed)
    nN2 = noisy(f, sd.S["Normal"], profile, n_draw, seed + 1)
    noise_e = np.array([np.sum(np.abs(pair_signals(a - b) / sig) ** 2) for a, b in zip(nN, nN2)])
    noise_c3 = np.array([c3(a) for a in nN])
    res = {"n_draw": n_draw, "n_entries": int(sig.size), "noise_energy_mean": float(noise_e.mean()),
           "noise_energy_p95": float(np.quantile(noise_e, 0.95)), "stages": {}}
    for i, s in enumerate(stages):
        x = pair_signals(sd.dS(s)) / sig
        A = noisy(f, sd.S[s], profile, n_draw, seed + 10 * (i + 1))
        B = noisy(f, sd.S["Normal"], profile, n_draw, seed + 10 * (i + 1) + 1)
        e = np.array([np.sum(np.abs(pair_signals(a - b) / sig) ** 2) for a, b in zip(A, B)])
        cs = np.array([c3(a) for a in A])
        res["stages"][s] = dict(
            mf_snr=_norms(x, kp),
            energy_auc=_auc(e, noise_e),
            energy_frac_above_noise_p95=float(np.mean(e > np.quantile(noise_e, 0.95))),
            energy_excess_over_noise_sd=float((e.mean() - noise_e.mean()) / noise_e.std()),
            c3_gap_db=float(c3(sd.S[s]) - c3(sd.S["Normal"])),
            c3_noise_sd_db=float(noise_c3.std()),
            c3_auc_lower=_auc(-cs, -noise_c3))                              # AD: lower k3 power
    # solve-to-solve context (Normal v2 - Normal v1, common band)
    try:
        from adstage.config import load_config
        sd1 = load_stages(load_config(ROOT, v1_config))
        common = np.intersect1d(np.round(f), np.round(sd1.f_hz))
        i2 = np.searchsorted(np.round(f), common)
        i1 = np.searchsorted(np.round(sd1.f_hz), common)
        x_solve = pair_signals(sd.S["Normal"][i2] - sd1.S["Normal"][i1]) / sig[:, i2]
        res["solve_to_solve"] = dict(band_GHz=f"{common[0] / 1e9:.1f}-{common[-1] / 1e9:.1f}",
                                     mf_snr_normal_v2_minus_v1=_norms(x_solve, kp),
                                     mf_snr_stages_same_band={s: _norms(pair_signals(sd.dS(s)[i2]) / sig[:, i2], kp)
                                                              for s in stages})
    except Exception as e:                                                  # pragma: no cover
        res["solve_to_solve"] = {"error": repr(e)}
    return res
