"""Quantitative scores of every reconstruction against the design truth (truth used ONLY here).

Per sector: true e_k, posterior median e, |error| (mm), P(affected), call (P > 0.5) correct,
90% interval covers truth. Per design: MAE, pattern correlation of e (Pearson over the 6 sectors;
undefined when the truth is constant), sector calls correct (of 6), stage (MAP) correct,
image correlation and relative error of the sigma-change map in the sensed brain region
(3-D grid, 3 mm, fade opacity >= 0.5) and in the whole brain.
"""
from __future__ import annotations

import numpy as np

from . import render as RE
from .data import CACHE, N, SECTOR_SHORT
from .figures import truth_of
from .invert import STAGES


def sector_rows(tag, post):
    t = post["targets"][tag]
    tr, _ = truth_of(tag, post)
    rows = []
    for k in range(N):
        s = t["sectors"][k]
        te = float(tr.e[k])
        aff = bool(tr.affected[k])
        rows.append(dict(target=tag, sector=SECTOR_SHORT[k], e_true=te, e_median=s["e_median"],
                         e_q05=s["e_q05"], e_q95=s["e_q95"], abs_err_mm=abs(s["e_median"] - te),
                         P_affected=round(s["P_affected"], 3), affected_true=aff,
                         call_correct=(s["P_affected"] > 0.5) == aff,
                         covered_90=s["e_q05"] <= te <= s["e_q95"]))
    return rows


_GRID = None


def volume_grid():
    global _GRID
    if _GRID is None:
        ax = np.arange(-84.0, 84.1, 3.0)
        X, Y, Z = np.meshgrid(ax, ax, ax, indexing="ij")
        r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
        brain = (r < 83.5) & (r > 25.0)
        nr = RE.noise_rel_at_field_freqs()
        alpha = RE.fade_alpha(RE.snr_at(X, Y, Z, nr) * RE.BAND_FACTOR)
        _GRID = (X[brain], Y[brain], Z[brain], alpha[brain])
    return _GRID


def image_scores(tag, post):
    X, Y, Z, alpha = volume_grid()
    marg = np.load(CACHE / f"marg_{tag}.npy")
    est = RE.posterior_maps(marg, X, Y, Z)
    tr, _ = truth_of(tag, post)
    tru = RE.truth_maps(tr, X, Y, Z)
    out = {}
    for q in ("sig", "eps"):
        de = est[q] - est[q + "0"]
        dt = tru[q] - tru[q + "0"]
        for nm, sel in (("sensed", alpha >= 0.5), ("brain", np.ones_like(alpha, bool))):
            a, b = de[sel], dt[sel]
            nt = np.linalg.norm(b)
            out[f"{q}_{nm}_relerr"] = float(np.linalg.norm(a - b) / nt) if nt > 0 else float("nan")
            out[f"{q}_{nm}_corr"] = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan")
            out[f"{q}_{nm}_rms_est"] = float(np.sqrt(np.mean(a ** 2)))
            out[f"{q}_{nm}_rms_true"] = float(np.sqrt(np.mean(b ** 2)))
    out["sensed_fraction_of_brain"] = float((alpha >= 0.5).mean())
    return out


def design_row(tag, post):
    t = post["targets"][tag]
    tr, _ = truth_of(tag, post)
    rows = sector_rows(tag, post)
    med = np.array([r["e_median"] for r in rows])
    te = tr.e.astype(float)
    corr = float(np.corrcoef(med, te)[0, 1]) if te.std() > 0 and med.std() > 0 else float("nan")
    ps = t["P_stage"]
    stage_map = max(ps, key=ps.get)
    true_stage = tr.tissue_stage if tr.affected.any() else "Healthy"
    row = dict(target=tag, stage_true=true_stage, stage_est=stage_map, P_stage_est=round(ps[stage_map], 3),
               stage_correct=stage_map == true_stage, sector_calls_correct=int(sum(r["call_correct"] for r in rows)),
               mae_e_mm=float(np.mean([r["abs_err_mm"] for r in rows])),
               mae_e_affected_mm=float(np.mean([r["abs_err_mm"] for r in rows if r["affected_true"]]))
               if tr.affected.any() else float("nan"),
               e_pattern_corr=corr, covered_90=int(sum(r["covered_90"] for r in rows)),
               gof_chi2_per_dof=round(t["gof"]["chi2_per_dof"], 3),
               left_minus_right_e=float(np.mean(med[[1, 2]]) - np.mean(med[[4, 5]])),
               left_minus_right_true=float(np.mean(te[[1, 2]]) - np.mean(te[[4, 5]])),
               front_minus_back_e=float(med[0] - med[3]), front_minus_back_true=float(te[0] - te[3]))
    row.update(image_scores(tag, post))
    return row, rows
