"""Adversarial review, round 2 (main session): R1-R4, R6, A14-A16, A19-A24, A26, A28, C2, C3, C5.

    python scripts/11_review2.py [--n 300]

Writes results/05_lobe/review2/{report_stats.md, *.csv, figures/}. Reads, never writes, the predictions
(results/05_lobe/predictions.*) and frozen rules (results/04/frozen_rule.json, results/imaging/lobe_frozen.json).
Predictions for R3 and C4 were committed before this script first ran (review2/predictions_R3_C4.md).

FLOOR RULE (R1c, fixed here before any round-2 number was computed, justified without LeftOnly):
  For a statistic whose true value is 0 for every mirror-symmetric design, the null is the set of the nine
  mirror-symmetric designs (two healthy heads, six stages, MCI). The floor is the LARGEST |value| among them
  (leave-one-out when a null design itself is evaluated). Reasons: (1) nine samples cannot support a tail model,
  and a value beyond all nine has a rank p of 1/10 at best; (2) the observed null is not shown to be Gaussian, so
  an rms floor would assume a tail shape; (3) every new solve has its own mesh, so the worst numerical asymmetry
  already seen is a realistic outcome for the next file. Clean ruler = max(floor, one-pass yardstick); the bar is
  the same as everywhere: >= 3x established, 2-3x sensitive, < 2x not separable. The rank p is reported alongside.
One solve per design: within-simulation noise robustness, not generalisation.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adstage.config import load_config  # noqa: E402
from adstage.features.metrics import to_ring_order  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.frozen import apply_rule  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.io.masking import mask_glitches  # noqa: E402
from adstage.io.touchstone import read_touchstone  # noqa: E402
from adstage.noise.model import PROFILES, NoiseProfile  # noqa: E402
from adstage.noise.reference import mesh_pairs, mesh_sd  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.pipeline.classify import Threshold1D  # noqa: E402
from adstage.pipeline.quality import QualityGate  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
L9 = _load("lobe09", "09_lobe_tests.py")
R10 = _load("rev10", "10_lobe_review.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "review2"
FIG = OUT / "figures"
ANT, MIR, DIST, MM = L7.ANT, L7.MIRROR, L7.DIST, L7.mirror_map()
LO, MCI, H6, H7 = "LeftOnly_test_c3", "MCI_lobe_c3", L8.H6, L8.H7
SYM = R10.SYM
STAGES = {"lobe_A": [H6, "Mild_lobe", "Moderate_lobe", "Severe_lobe"],
          "lobe_B": [H7, "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3"], "tests": [LO, MCI]}
LOBE_ALL = STAGES["lobe_A"] + STAGES["lobe_B"] + STAGES["tests"]
BANDS = {"3.2-3.5": (3.2e9, 3.5e9), "3.5-3.8": (3.5e9, 3.8e9), "3.8-4.2": (3.8e9, 4.2e9)}
LRBAND = (3.30e9, 3.65e9)
md = L7.md
tier = R10.tier


# ======================================================================== helpers
def sbar(S):
    return 0.5 * (S + np.swapaxes(S, -1, -2))


def lr_cr_phase(S):
    """Left-right antisymmetric phase of the complex cross-ratios, per frequency (deg), reference-free."""
    cr = R10.complex_cr(sbar(S))
    out = {}
    for n, (m, s) in MM.items():
        if (m == n and s == 1) or (m != n and m < n):
            continue
        z = cr[n] * (np.conj(cr[m]) if s == 1 else cr[m])
        out[n] = np.degrees(np.angle(z))
    return out


def pair_phase(S):
    """Phase of each mirror path pair, left path minus its mirror image, per frequency (deg)."""
    Sb = sbar(S)
    return {R10.pair_name(i, j): np.degrees(np.angle(Sb[..., i, j] * np.conj(Sb[..., MIR[i], MIR[j]])))
            for i, j in R10.PAIR_LIST}


def fmask(f, band):
    return (f >= band[0] - 1) & (f <= band[1] + 1)


def floor_rule(lo, null, yard):
    null = np.abs(np.asarray(null, float))
    fl = float(null.max())
    ruler = max(fl, float(yard))
    r = abs(lo) / ruler
    return {"floor (max |null|)": fl, "yardstick": float(yard), "clean ruler": ruler, "ratio": r,
            "verdict": tier(r).replace("robust", "established").replace("not determined", "not separable"),
            "rank p": float((1 + np.sum(null >= abs(lo))) / (len(null) + 1)),
            "ratio to null rms": abs(lo) / float(np.sqrt(np.mean(null ** 2)))}


def separable(Y):
    """Least-squares per-antenna model Y_ab = g_a + g_b over the 15 transmission paths (Y complex, (..., 15)).
    Returns fitted and residual (same shape)."""
    pairs = [(i, j) for i in range(6) for j in range(i + 1, 6)]
    A = np.zeros((15, 6))
    for k, (i, j) in enumerate(pairs):
        A[k, i] = A[k, j] = 1
    P = A @ np.linalg.pinv(A)
    fit = Y @ P.T
    return fit, Y - fit, pairs


def tpaths(S):
    """(..., F, 15) reciprocal transmission entries in (i<j) order."""
    Sb = sbar(S)
    return np.stack([Sb[..., i, j] for i in range(6) for j in range(i + 1, 6)], -1)


def lr_pairs_idx():
    pairs = [(i, j) for i in range(6) for j in range(i + 1, 6)]
    out = []
    for i, j in R10.PAIR_LIST:
        if i == j:
            continue
        mi, mj = sorted((MIR[i], MIR[j]))
        out.append((pairs.index((i, j)), pairs.index((mi, mj)), R10.pair_name(i, j)))
    return out


def resonance(f, S):
    """Per antenna: resonance (min |Sii|, parabolic refinement) in MHz and depth in dB."""
    out = []
    for t in range(6):
        y = 20 * np.log10(np.abs(S[:, t, t]))
        k = int(np.clip(np.argmin(y), 1, len(f) - 2))
        a, b, c = y[k - 1], y[k], y[k + 1]
        den = a - 2 * b + c
        dx = 0.5 * (a - c) / den if den != 0 else 0.0
        out.append((float((f[k] + dx * (f[1] - f[0])) / 1e6), float(b - 0.25 * (a - c) * dx)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    FIG.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT, "config_lobe.yaml")
    gh = git_hash(ROOT)
    f, Sd, man, _ = L8.load_all(cfg)
    rule = json.loads((ROOT / "results/04/frozen_rule.json").read_text())
    tau, m_det = rule["detection_binary_R31"]["tau_dB"], rule["detection_binary_R31"]["margin_dB"]
    R = L8.rulers(f, Sd, cfg, args.n, qfn=L9.ext_quantities)
    Q = R["Q"]
    g = lambda d, k: float(Q[d][k][0])                       # noqa: E731
    L = [f"# Adversarial review round 2, main session: statistics (code {gh})", "",
         "Every number is recomputed from the raw files by `scripts/11_review2.py`. Floor rule (R1c) and verdict bar are "
         "in the script docstring and were fixed before any round-2 number existed. One solve per design: "
         "within-simulation noise robustness, not generalisation.", ""]
    summ = []

    # ================================================================== R1 floor dispute
    IM = R10.Imaging(f)
    Simg = {d: IM.SL.load_design(d, f)[0] for d in SYM + [LO]}
    r1, nullrows = [], []
    from scipy.stats import shapiro
    for mth in IM.methods:
        for rn, ref in (("Healthy_sliced (7 passes)", H7), ("Healthy_sliced_new (6 passes)", H6)):
            Sr = Simg[ref]
            Tn = np.array([IM.T(Simg[d], Sr, mth) for d in SYM])
            Tlo = IM.T(Simg[LO], Sr, mth)
            yd = max(abs(IM.T(Simg[b], Sr, mth) - IM.T(Simg[a], Sr, mth)) for a, b in L8.PAIRS.values())
            W, p_sw = shapiro(Tn)
            W8, p_sw8 = shapiro(np.delete(Tn, SYM.index("Moderate_lobe")))
            fr = floor_rule(Tlo, Tn, yd)
            r1.append({"method": mth, "reference": rn, "T(LeftOnly)": Tlo, **fr,
                       "null mean": float(Tn.mean()), "Shapiro-Wilk W": W, "Shapiro-Wilk p": p_sw,
                       "SW p without Moderate_lobe": p_sw8,
                       "one-sided rank p (T_LO > all null)": float((1 + np.sum(Tn >= Tlo)) / (len(Tn) + 1))})
            for d, v in zip(SYM, Tn):
                nullrows.append({"method": mth, "reference": rn, "design": d, "T": v})
    r1t = pd.DataFrame(r1)
    r1n = pd.DataFrame(nullrows)
    r1t.to_csv(OUT / "R1a_imaging_null.csv", index=False)
    r1n.to_csv(OUT / "R1a_imaging_null_values.csv", index=False)
    # R1b: why Moderate_lobe; per-path decomposition of T (dS method is linear in dS) and per-path mirror residuals
    dec = []
    Sr = Simg[H6]
    mth0 = "Tikhonov dS (primary)"
    for d in SYM + [LO]:
        D = Simg[d] - R10.mirror(Simg[d])
        tot = 0.0
        for i in range(6):
            for j in range(i, 6):
                Dp = np.zeros_like(D)
                Dp[:, i, j] = D[:, i, j]
                Dp[:, j, i] = D[:, j, i]
                c = 0.5 * IM.lr(Sr + Dp, Sr, mth0)
                tot += c
                dec.append({"design": d, "path": f"T{i + 1}-T{j + 1}" if i != j else f"T{i + 1} refl.",
                            "contribution to T": c})
        dec.append({"design": d, "path": "SUM (= T)", "contribution to T": tot})
    dect = pd.DataFrame(dec)
    dect.to_csv(OUT / "R1b_T_decomposition.csv", index=False)
    piv = dect.pivot(index="path", columns="design", values="contribution to T")
    mres = []
    pp = {d: pair_phase(Sd[d]) for d in SYM + [LO]}
    fi = IM.fi
    for d in SYM + [LO]:
        bp = L7.db(L7.band_power(f, Sd[d][None]))[0]
        row = {"design": d}
        mi = man.set_index("design").loc[d]
        row.update(passes=int(mi.passes), elements=int(mi.elements), final_dS=float(mi.final_dS))
        for i, j in R10.PAIR_LIST:
            nm = R10.pair_name(i, j)
            row[f"power {nm} dB"] = float(bp[i, j] - bp[MIR[i], MIR[j]])
            row[f"phase {nm} deg (3.4 GHz)"] = float(pp[d][nm][fi[0]])
        mres.append(row)
    mrt = pd.DataFrame(mres)
    mrt.to_csv(OUT / "R1b_mirror_residuals.csv", index=False)
    top_mod = piv["Moderate_lobe"].drop("SUM (= T)").abs().sort_values(ascending=False).head(4)
    # R1c applied to the main session's statistics (band-mean reference-free mirror statistics)
    MS = {d: R10.mirror_stats(f, Sd[d]) for d in SYM + [LO]}
    rows = []
    for k in MS[LO]:
        null = [float(MS[d][k][0]) for d in SYM]
        yd = max(abs(float(MS[b][k][0] - MS[a][k][0])) for a, b in L8.PAIRS.values())
        rows.append({"statistic": k, "family": R10.fam_of(k), "LeftOnly": float(MS[LO][k][0]),
                     **floor_rule(float(MS[LO][k][0]), null, yd)})
    r1c = pd.DataFrame(rows)
    r1c.to_csv(OUT / "R1c_main_statistics_floor_rule.csv", index=False)
    fam1c = r1c.groupby("family").agg(n=("statistic", "size"), est=("ratio", lambda v: int((v >= 3).sum())),
                                      sens=("ratio", lambda v: int(((v >= 2) & (v < 3)).sum())),
                                      best=("ratio", "max"), beyond=("rank p", lambda v: int((v <= 0.1).sum()))).reset_index()
    fam1c.columns = ["family", "n", ">= 3x (established)", "2-3x (sensitive)", "best ratio", "beyond all 9 (rank p 0.1)"]
    L += ["## R1. The floor dispute",
          "**(a) Empirical null of the imaging mirror-test LR (T = (LR(S) - LR(mirror S))/2) over the nine mirror-symmetric "
          "designs**, normality and rank p:", md(r1t, ".3f"), "",
          "Null values (Healthy_sliced_new reference):",
          md(r1n[r1n.reference.str.startswith("Healthy_sliced_new")].pivot(index="design", columns="method",
                                                                            values="T").reset_index(), ".2f"), "",
          f"**(b) Why Moderate_lobe.** Its T is decomposed exactly into path contributions (Tikhonov dS is linear in dS). "
          f"Largest Moderate_lobe contributions: " + ", ".join(f"{p} {piv.loc[p, 'Moderate_lobe']:+.2f}" for p in top_mod.index)
          + ". Path contributions of every design:", md(piv.reset_index(), ".2f"), "",
          "Per-pair mirror residuals (power dB, band mean; phase deg at 3.4 GHz) with mesh data:",
          md(mrt, ".3f"), "",
          "**(c) One floor rule** (script docstring): floor = max |value| over the nine mirror-symmetric designs; clean "
          "ruler = max(floor, one-pass yardstick); >= 3x established, 2-3x sensitive, < 2x not separable. Applied to the "
          "main session's reference-free statistics:", md(fam1c, ".2f"), ""]
    prim = r1t[(r1t.method == mth0) & r1t.reference.str.startswith("Healthy_sliced_new")].iloc[0]
    summ.append({"item": "R1 floor dispute", "verdict": "CHANGED (main label)",
                 "old -> new": f"imaging LR 3.7x (null rms) -> {prim['ratio']:.2f}x under the max-floor rule "
                               f"({prim.verdict}); Shapiro-Wilk p = {prim['Shapiro-Wilk p']:.3f} "
                               f"({prim['SW p without Moderate_lobe']:.2f} without Moderate_lobe); rank p "
                               f"{prim['one-sided rank p (T_LO > all null)']:.2f}; Moderate's T driven by "
                               f"{', '.join(top_mod.index[:2])}",
                 "evidence": "review2/R1a_imaging_null.csv, R1b_*.csv, R1c_*.csv"})

    # ================================================================== R2 same quantity, same ruler
    cp = {d: lr_cr_phase(Sd[d]) for d in SYM + [LO]}
    variants = {"band mean 3.2-4.2": np.ones(len(f), bool), "3.30-3.65 GHz": fmask(f, LRBAND)}
    for fhz, idx in zip(IM.fh, fi):
        v = np.zeros(len(f), bool)
        v[idx] = True
        variants[f"{fhz / 1e9:.1f} GHz"] = v
    r2 = []
    for qname, src in (("pair phase (left minus mirror path)", pp), ("cross-ratio phase", cp)):
        for vname, msk in variants.items():
            for k in src[LO]:
                val = lambda d: float(np.mean(src[d][k][msk]))       # noqa: E731
                null = [val(d) for d in SYM]
                yd = max(abs(val(b) - val(a)) for a, b in L8.PAIRS.values())
                r2.append({"quantity": qname, "frequencies": vname, "statistic": k, "LeftOnly": val(LO),
                           **floor_rule(val(LO), null, yd)})
    r2t = pd.DataFrame(r2)
    r2t.to_csv(OUT / "R2_same_quantity.csv", index=False)
    r2s = r2t.groupby(["quantity", "frequencies"]).agg(n=("statistic", "size"),
                                                       est=("ratio", lambda v: int((v >= 3).sum())),
                                                       sens=("ratio", lambda v: int(((v >= 2) & (v < 3)).sum())),
                                                       best=("ratio", "max")).reset_index()
    r2s.columns = ["quantity", "frequencies", "n", ">= 3x", "2-3x", "best ratio"]
    # why cross-ratios and pairs differ: separable (per-antenna) share of the reference-free mirror residual
    sep = []
    lrp = lr_pairs_idx()
    for d in SYM + [LO]:
        S = Sd[d]
        Y = np.log(tpaths(S)) - np.log(tpaths(R10.mirror(S)))
        Y = Y.real + 1j * np.angle(np.exp(1j * Y.imag))
        fit, res, _ = separable(Y)
        msk = variants["3.30-3.65 GHz"]
        a_tot = np.array([np.degrees(Y.imag[msk, i]) for i, _, _ in lrp])
        a_res = np.array([np.degrees(res.imag[msk, i]) for i, _, _ in lrp])
        sep.append({"design": d, "rms LR phase asymmetry, all (deg)": float(np.sqrt(np.mean(a_tot ** 2))),
                    "rms per-antenna (separable) part (deg)": float(np.sqrt(np.mean((a_tot - a_res) ** 2))),
                    "rms non-separable part (deg)": float(np.sqrt(np.mean(a_res ** 2))),
                    "separable share of power": float(1 - np.mean(a_res ** 2) / np.mean(a_tot ** 2))})
    sept = pd.DataFrame(sep)
    sept.to_csv(OUT / "R2_separable_share.csv", index=False)
    L += ["## R2. Main 16/22 against imaging b9_anti: one quantity, one ruler",
          "Both families evaluated reference-free (design against its own port mirror) at the band mean, at 3.30-3.65 GHz "
          "and at the three imaging fit frequencies, with the R1c floor rule:", md(r2s, ".2f"), "",
          "Why the two families disagree: share of the reference-free left-right phase asymmetry (3.30-3.65 GHz) explained "
          "by per-antenna (separable) terms, which cancel in cross-ratios but not in single path pairs:",
          md(sept, ".2f"), ""]
    cb = r2s[(r2s.quantity == "cross-ratio phase")].set_index("frequencies")
    pb = r2s[(r2s.quantity.str.startswith("pair"))].set_index("frequencies")
    summ.append({"item": "R2 16/22 vs b9_anti", "verdict": "CHANGED (one answer)",
                 "old -> new": f"16/22 (rms ruler) vs 0.9x (max floor, one pair) -> same max-floor rule: cross-ratio phase "
                               f"{int(cb.loc['band mean 3.2-4.2', '>= 3x'])}/22 >= 3x at band mean, "
                               f"{int(cb.loc['3.30-3.65 GHz', '>= 3x'])}/22 at 3.30-3.65 GHz; pair phase "
                               f"{int(pb.loc['band mean 3.2-4.2', '>= 3x'])}/8 (band), "
                               f"{int(pb.loc['3.4 GHz', '>= 3x'])}/8 (3.4 GHz); separable (per-antenna) share of the "
                               f"reference-free LR phase asymmetry: null median "
                               f"{sept[sept.design != LO]['separable share of power'].median():.2f}, LeftOnly "
                               f"{sept.set_index('design').loc[LO, 'separable share of power']:.2f}",
                 "evidence": "review2/R2_*.csv"})

    # ================================================================== R3 detuning
    res_rows = []
    for d in SYM + [LO]:
        rs = resonance(f, Sd[d])
        row = {"design": d}
        for t in range(6):
            row[f"T{t + 1} f_res MHz"], row[f"T{t + 1} depth dB"] = rs[t]
        row["left-right f_res MHz"] = (rs[1][0] + rs[2][0]) / 2 - (rs[5][0] + rs[4][0]) / 2
        row["left-right depth dB"] = (rs[1][1] + rs[2][1]) / 2 - (rs[5][1] + rs[4][1]) / 2
        res_rows.append(row)
    rst = pd.DataFrame(res_rows)
    rst.to_csv(OUT / "R3_resonances.csv", index=False)
    nul = rst[rst.design != LO]
    lo_r = rst.set_index("design").loc[LO]
    det = []
    for rn, ref in (("Healthy_sliced", H7), ("Healthy_sliced_new", H6)):
        Y = np.log(tpaths(Sd[LO])) - np.log(tpaths(Sd[ref]))
        Y = Y.real + 1j * np.angle(np.exp(1j * Y.imag))
        fit, res, pairs = separable(Y)
        G = np.linalg.pinv(np.array([[1 if t in pr else 0 for t in range(6)] for pr in pairs])) @ Y.T   # (6, F)
        refl = np.array([np.log(Sd[LO][:, t, t] / Sd[ref][:, t, t]) for t in range(6)])          # (6, F)
        for bn, msk in (("3.2-4.2", variants["band mean 3.2-4.2"]), ("3.30-3.65", variants["3.30-3.65 GHz"])):
            a_tot = np.array([np.degrees(Y.imag[msk, i] - Y.imag[msk, j]) for i, j, _ in lrp])
            a_res = np.array([np.degrees(res.imag[msk, i] - res.imag[msk, j]) for i, j, _ in lrp])
            gph = np.degrees(G.imag[:, msk].mean(1))
            rph = np.degrees(np.angle(np.exp(1j * refl.imag[:, msk])).mean(1))
            det.append({"reference": rn, "band": bn,
                        "rms LR phase asymmetry of transmissions (deg)": float(np.sqrt(np.mean(a_tot ** 2))),
                        "separable (per-antenna) share": float(1 - np.mean(a_res ** 2) / np.mean(a_tot ** 2)),
                        "per-antenna phase terms T1..T6 (deg)": ", ".join(f"{v:+.2f}" for v in gph),
                        "reflection phase change T1..T6 (deg)": ", ".join(f"{v:+.2f}" for v in rph),
                        "corr(per-antenna term, reflection phase change)": float(np.corrcoef(gph, rph)[0, 1])})
    dett = pd.DataFrame(det)
    dett.to_csv(OUT / "R3_separable_fit.csv", index=False)
    lr_f = float(lo_r["left-right f_res MHz"])
    nul_f = float(nul["left-right f_res MHz"].abs().max())
    sh = dett[(dett.reference == "Healthy_sliced_new") & (dett.band == "3.30-3.65")].iloc[0]
    L += ["## R3. Detuning hypothesis (predictions committed in predictions_R3_C4.md before this ran)",
          "Reflection resonance (min |Sii|) and depth per antenna; left - right = mean(T2, T3) - mean(T6, T5):",
          md(rst, ".2f"), "",
          f"LeftOnly left-right resonance shift {lr_f:+.2f} MHz against the largest of the symmetric designs {nul_f:.2f} MHz.",
          "Per-antenna (separable) model of the LeftOnly transmission change, ln S_ab(LO)/S_ab(ref) = g_a + g_b + r_ab:",
          md(dett, ".2f"), ""]
    det_ok = sh["separable (per-antenna) share"] >= 0.8 and abs(lr_f) > nul_f
    summ.append({"item": "R3 detuning", "verdict": "CHANGED (tested; " + ("detuning supported" if det_ok else
                 "first-order detuning does not explain the asymmetry") + ")",
                 "old -> new": f"untested -> left-right resonance shift {lr_f:+.2f} MHz (symmetric designs <= {nul_f:.2f}); "
                               f"separable share of the LR transmission phase asymmetry {sh['separable (per-antenna) share']:.2f} "
                               f"(3.30-3.65 GHz, matched reference); corr(per-antenna term, reflection change) "
                               f"{sh['corr(per-antenna term, reflection phase change)']:+.2f}",
                 "evidence": "review2/R3_*.csv"})

    # ================================================================== training draws (03 replication) for R4, A21, A22
    cfg_u = load_config(ROOT, "config_repeats.yaml")
    du = load_dataset(cfg_u, ROOT)
    fu = du.f_hz
    Su = to_ring_order(du.S, du.port_to_ant)
    ccfg = cfg_u["classify"]
    pi = list(PROFILES).index("typical")
    feats_u, names_u = {}, None
    for s in range(len(du.classes)):
        Xs = []
        for split, off in (("train", 0), ("test", 1)):
            rng = np.random.default_rng([cfg_u["seed"], 3, pi, s, off])
            D = draws(fu, Su[s], PROFILES["typical"], int(ccfg[f"n_{split}_draws"]), rng, dict(cfg_u.get("augment", {})))
            X, names_u, _, _ = features(fu, D)
            Xs.append(X)
        feats_u[s] = np.concatenate(Xs)
    col = lambda k: names_u.index(k)                          # noqa: E731
    ucls = list(du.classes)
    ufile = [Path(str(x)).name for x in du.files]
    Xu_clean, _, _, _ = features(fu, Su)
    N_ = [s for s, c in enumerate(ucls) if c == "Normal"]
    AD_ = [s for s, c in enumerate(ucls) if c in ("Mild", "Moderate", "Severe")]
    T03 = _load("cls03", "03_classify.py")
    pairs_u = mesh_pairs(du.files, du.manifest)

    # ================================================================== R4 detection feature choice (shown, not adopted)
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    hv21 = {s: 10 ** (feats_u[s][:, col("R21")] / 10) for s in range(len(ucls))}
    vals21 = np.array([10 * np.log10(np.mean(hv21[s])) for s in range(len(ucls))])
    t21 = T03.thresholds(hv21, {"Normal": N_, "AD": AD_}, float(ccfg["p_star"]), float(ccfg["screening_prior_normal"]),
                         int(ccfg["n_boot"]), cfg_u["seed"], mesh_sd(vals21, pairs_u))
    o21 = 1 if np.mean([vals21[s] for s in AD_]) > np.mean([vals21[s] for s in N_]) else -1
    Xtr = np.concatenate([feats_u[s][:, [col("R31"), col("R21")]] for s in N_ + AD_])
    ytr = np.concatenate([np.full(len(feats_u[s]), int(s in AD_)) for s in N_ + AD_])
    lda = LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto", priors=[0.5, 0.5]).fit(Xtr, ytr)
    w, b0 = lda.coef_[0], float(lda.intercept_[0])
    nw = float(np.linalg.norm(w))
    yd31, yd21 = R["yard"]["R31"], R["yard"]["R21"]
    yd_pair = max(abs(float(w @ np.array([g(bb, "R31") - g(aa, "R31"), g(bb, "R21") - g(aa, "R21")]))) / nw
                  for aa, bb in L8.PAIRS.values())
    r4 = []

    def lab21(x):
        if o21 > 0:
            return "AD" if x > t21["tau_dB"] + t21["margin_dB"] else ("Normal" if x < t21["tau_dB"] - t21["margin_dB"] else "UNCERTAIN")
        return "AD" if x < t21["tau_dB"] - t21["margin_dB"] else ("Normal" if x > t21["tau_dB"] + t21["margin_dB"] else "UNCERTAIN")
    designs = [(st, d, g(d, "R31"), g(d, "R21")) for st, ds_ in STAGES.items() for d in ds_]
    designs += [("uniform (training)", ufile[s], float(Xu_clean[s][col("R31")]), float(Xu_clean[s][col("R21")]))
                for s in range(len(ucls))]
    for st, d, x31, x21 in designs:
        l31, m31 = R10.edge_margin(rule, "binary", x31)
        e21 = min(abs(x21 - (t21["tau_dB"] + t21["margin_dB"])), abs(x21 - (t21["tau_dB"] - t21["margin_dB"])))
        dist = (float(w @ np.array([x31, x21])) + b0) / nw
        r4.append({"set": st, "design": d, "R31": x31, "R21": x21,
                   "R31 frozen: label": l31, "R31: / yardstick": abs(m31) / yd31,
                   "R21 alone: label": lab21(x21), "R21: / yardstick": e21 / yd21,
                   "(R31, R21) LDA: label": "AD" if dist > 0 else "Normal",
                   "pair: distance dB": dist, "pair: / projected yardstick": abs(dist) / yd_pair})
    r4t = pd.DataFrame(r4)
    r4t.to_csv(OUT / "R4_feature_choice.csv", index=False)
    lob = r4t[~r4t.set.str.startswith("uniform")]
    L += ["## R4. Detection feature choice (shown, not adopted; any new rule needs pre-registration and a new blind design)",
          f"R21 alone, fitted exactly like tau (03 code, same training draws): tau21 = {t21['tau_dB']:.3f} dB, margin "
          f"{t21['margin_dB']:.3f} dB. (R31, R21) pair: LDA (lsqr, Ledoit-Wolf, equal priors) on the same draws; distance to "
          f"its boundary in dB along the normal; projected one-pass yardstick {yd_pair:.3f} dB. Uniform designs are training "
          "data (in-sample).", md(r4t, ".3f"), "",
          "Why R31 was frozen: on the training solves it had the widest Normal-AD gap of the calibration-free ratios "
          "(closest solves: v2 Normal and the Severe solves). That choice was made on 2026-09-28 (6eca5d7), "
          "before any lobe file existed.", ""]
    n31 = int((lob["R31: / yardstick"] >= 3).sum())
    n21 = int((lob["R21: / yardstick"] >= 3).sum())
    np_ = int((lob["pair: / projected yardstick"] >= 3).sum())
    summ.append({"item": "R4 detection feature", "verdict": "CONFIRMED (defensible on training data; fragile)",
                 "old -> new": f"not compared -> lobe designs with >= 3x margin: R31 {n31}/10, R21 alone {n21}/10, "
                               f"(R31, R21) pair {np_}/10; R21 alone puts LeftOnly "
                               f"{lob.set_index('design').loc[LO, 'R21 alone: label']} and lobe-Mild near its threshold",
                 "evidence": "review2/R4_feature_choice.csv"})

    # ================================================================== R6 / A28 rulers incl. measurement spread, boundary bootstrap
    rng = np.random.default_rng([cfg["seed"], 111])
    db31 = {s: feats_u[s][:, col("R31")] for s in range(len(ucls))}

    def tau_of(ns, as_):
        xn = np.concatenate([db31[s] for s in ns])
        xa = np.concatenate([db31[s] for s in as_])
        return float(Threshold1D().fit(np.r_[xn, xa][:, None], np.r_[np.zeros(len(xn)), np.ones(len(xa))]).tau_)
    tb = np.array([tau_of(rng.choice(N_, len(N_)), rng.choice(AD_, len(AD_))) for _ in range(3000)])
    bdefs = {"three": ("R21", [["Normal"], ["Mild"], ["Severe"]]),
             "three_merged": ("R32", [["Normal"], ["Mild", "Moderate"], ["Severe"]])}
    bboot, bfro = {}, {}
    for sch, (ft, cls) in bdefs.items():
        sols = [[s for s, c in enumerate(ucls) if c in mem] for mem in cls]
        bb = []
        for _ in range(3000):
            mu = [np.mean([float(Xu_clean[s][col(ft)]) for s in rng.choice(ss, len(ss))]) for ss in sols]
            bb.append(sorted(0.5 * (mu[i] + mu[i + 1]) for i in range(2)))
        bboot[sch] = np.array(bb)
    fro = {k: sorted(float(p.split(" at ")[1]) for p in v.split(", ")) for k, v in L7.boundaries(rule).items()}
    bfro = {"three": fro["three (R21)"], "three_merged": fro["three_merged (R32)"]}
    sdm = {nm: R["sd"][nm] for nm in L8.NOISE}
    r6 = []
    for st, ds_ in STAGES.items():
        for d in ds_:
            for sch, ft in (("binary", "R31"), ("three", "R21"), ("three_merged", "R32")):
                x = g(d, ft)
                lab, mg = R10.edge_margin(rule, sch, x)
                if sch == "binary":
                    sb = float(tb.std(ddof=1))
                    labs = np.where(x < tb - m_det, "AD", np.where(x > tb + m_det, "Normal", "UNCERTAIN"))
                    pflip = float((labs != lab).mean())
                else:
                    k = int(np.argmin([abs(x - b) for b in bfro[sch]]))
                    sb = float(bboot[sch][:, k].std(ddof=1))
                    shift = bboot[sch] - np.array(bfro[sch])
                    pflip = float(np.mean([R10.rule_label(rule, sch, x - sft[k])[0] != lab for sft in shift]))
                yd = R["yard"][ft]
                s05 = sdm["spread ±0.5 dB"][ft] / np.sqrt(2)
                s2 = sdm["spread ±2 dB ±10°"][ft] / np.sqrt(2)
                r6.append({"set": st, "design": d, "rule": sch, "label": lab, "edge margin dB": mg,
                           "yardstick": yd, "boundary SD": sb, "meas SD ±0.5 dB": s05, "meas SD ±2 dB ±10°": s2,
                           "A1 ratio max(yard, bSD)": abs(mg) / max(yd, sb),
                           "quadrature ±0.5 dB": abs(mg) / np.sqrt(yd ** 2 + sb ** 2 + s05 ** 2),
                           "quadrature ±2 dB ±10°": abs(mg) / np.sqrt(yd ** 2 + sb ** 2 + s2 ** 2),
                           "P(label differs | boundary bootstrap)": pflip})
    r6t = pd.DataFrame(r6)
    r6t.to_csv(OUT / "R6_A28_rulers.csv", index=False)
    cnt = {c: int((r6t[c] >= 3).sum()) for c in ("A1 ratio max(yard, bSD)", "quadrature ±0.5 dB", "quadrature ±2 dB ±10°")}
    nd_boot = r6t[r6t["P(label differs | boundary bootstrap)"] > 0.025]
    L += ["## R6 / A28. Label margins with every ruler",
          "Margins to the label edge against (A1) max(yardstick, boundary bootstrap SD), and with the single-measurement "
          "spread added in quadrature. Effective sample size: the boundary SD resamples the training solves, but the "
          "v1/v2 solves of a stage differ only in sweep settings and very likely share a mesh, so there is effectively one "
          "healthy design behind tau; its head-to-head uncertainty is not estimable from these data (the SD is a lower "
          "bound).", md(r6t, ".3f"), "",
          f"Labels >= 3x: A1 {cnt['A1 ratio max(yard, bSD)']}/{len(r6t)}, quadrature ±0.5 dB {cnt['quadrature ±0.5 dB']}, "
          f"quadrature ±2 dB ±10° {cnt['quadrature ±2 dB ±10°']}. Labels that change somewhere inside the boundary's "
          f"bootstrap distribution (P > 0.025): {len(nd_boot)} of {len(r6t)}: "
          + ", ".join(f"{r.design} {r.rule}" for _, r in nd_boot.iterrows()) + ".", ""]
    summ.append({"item": "R6 robust detection", "verdict": "CHANGED",
                 "old -> new": f"3.3-4.9x with max(yard, bSD) -> quadrature with ±0.5 dB measurement spread: "
                               + ", ".join(f"{r.design} {r['quadrature ±0.5 dB']:.2f}x" for _, r in
                                           r6t[(r6t.rule == 'binary') & ~r6t.design.isin([LO, MCI])].iterrows()),
                 "evidence": "review2/R6_A28_rulers.csv"})
    summ.append({"item": "A28 tau and boundary intervals", "verdict": "CHANGED (count)",
                 "old -> new": f"-> tau 95% {np.quantile(tb, 0.025):.3f} to {np.quantile(tb, 0.975):.3f} dB; "
                               f"{len(nd_boot)} of {len(r6t)} lobe labels change inside a boundary's bootstrap distribution",
                 "evidence": "review2/R6_A28_rulers.csv"})

    # ================================================================== A14 port map: what the symmetry search can and cannot decide
    def circ_score(S, order):
        Sp = S[:, order][:, :, order]
        P = 20 * np.log10(np.abs(Sp))
        return float(np.mean([np.std(P[:, DIST == k], axis=1).mean() for k in range(1, 4)]))
    raw = read_touchstone(ROOT / "data/raw/new_with_slices_Healthy_sliced.s6p")
    p2a = np.asarray(cfg["ring"]["port_to_ant"])
    order = np.argsort(p2a)                                   # ring position t -> port index
    mirrored = order[MIR]
    a14 = pd.DataFrame([{"assignment": "config: Port1..6 = T4,T3,T2,T1,T6,T5", "circulant score dB": circ_score(raw.s, order)},
                        {"assignment": "mirror image (T2<->T6, T3<->T5)", "circulant score dB": circ_score(raw.s, mirrored)}])
    a14.to_csv(OUT / "A14_symmetry_search.csv", index=False)
    L += ["## A14. Port map",
          "The symmetry search scores every ring ordering by how circulant |S| becomes. A mirrored assignment gives "
          "exactly the same score (Healthy_sliced):", md(a14, ".6f"), "",
          "So the search cannot decide left from right. The assignment is fixed by geometry: (1) HFSS audit "
          "(data/hfss_geometry_audit_Healthy_sliced.txt): excitations in order FEED_3_T4, T3, T2, T1, T6, T5 and lumped-port "
          "sheets Rectangle1..6 at azimuth +89.6, +29.6, -30.4, -90.4, -150.4, +149.6 deg; the user's GUI check ties "
          "excitation 2 (FEED_3_T3) to Rectangle2 (+29.6 deg); (2) the field exports E_Normal_T#, located from their own "
          "fields (scripts/12_review2_fields.py). A mirrored map would flip the sign of every left-right statistic; it "
          "does not change whether an asymmetry exists.", ""]
    summ.append({"item": "A14 port map", "verdict": "CONFIRMED (by geometry, not by the search)",
                 "old -> new": f"symmetry search -> the search is mirror-blind (scores {a14.iloc[0, 1]:.6f} = "
                               f"{a14.iloc[1, 1]:.6f}); audit excitation order + port-sheet azimuths + field centroids fix it",
                 "evidence": "review2/A14_symmetry_search.csv; data/hfss_geometry_audit_Healthy_sliced.txt"})

    # ================================================================== A15 masking
    files = {d: ROOT / "data/raw" / f"new_with_slices_{d}.s6p" for d in LOBE_ALL}
    mk = []
    variants15 = {"mask -30 dB (frozen)": -30.0, "mask off": None, "mask -36 dB (2x stricter)": -36.0}
    S15 = {}
    for vn, thr in variants15.items():
        S15[vn] = {}
        for d, p in files.items():
            t = read_touchstone(p)
            s = t.s
            if thr is not None:
                s, log = mask_glitches(t.f_hz, t.s, thr)
                if vn != "mask off":
                    cnt_p = pd.Series([f"{r['port_i']}-{r['port_j']}" for r in log]).value_counts()
                    mk.append({"threshold": vn, "file": d, "masked points": len(log),
                               "per port pair": ", ".join(f"{k}: {v}" for k, v in cnt_p.items())})
            S15[vn][d] = to_ring_order(s[None], p2a)[0]
    mkt = pd.DataFrame(mk)
    mkt.to_csv(OUT / "A15_mask_counts.csv", index=False)
    hl = []
    for vn in variants15:
        Sv = S15[vn]
        for d in LOBE_ALL:
            X, nm, _, _ = features(f, Sv[d][None])
            row = {"variant": vn, "design": d}
            for ft in ("R31", "R21", "R32"):
                row[ft] = float(X[0][nm.index(ft)])
            row["detection label"], row["detection edge margin"] = R10.edge_margin(rule, "binary", row["R31"])
            hl.append(row)
        cpv = {d: lr_cr_phase(Sv[d]) for d in SYM + [LO]}
        n3 = 0
        for k in cpv[LO]:
            null = [float(cpv[d][k].mean()) for d in SYM]
            yd = max(abs(float(cpv[bb][k].mean() - cpv[aa][k].mean())) for aa, bb in L8.PAIRS.values())
            n3 += floor_rule(float(cpv[LO][k].mean()), null, yd)["ratio"] >= 3
        hl.append({"variant": vn, "design": "LeftOnly phase cross-ratios >= 3x (R1c)", "R31": float(n3)})
    hlt = pd.DataFrame(hl)
    hlt.to_csv(OUT / "A15_masking_headlines.csv", index=False)
    base = hlt[hlt.variant == "mask -30 dB (frozen)"].set_index("design")
    dmax = {}
    for vn in variants15:
        if vn.startswith("mask -30"):
            continue
        other = hlt[hlt.variant == vn].set_index("design")
        dd = [(d, ft, abs(other.loc[d, ft] - base.loc[d, ft]) / R["yard"][ft]) for d in LOBE_ALL for ft in ("R31", "R21", "R32")]
        dmax[vn] = max(dd, key=lambda t: t[2])
    L += ["## A15. Glitch masking",
          "Threshold: |Sij - Sji| > -30 dB of the pair's band-rms level (config.yaml qc.glitch_thr_db, commit 89d4f23, "
          "2026-09-27, six days before the first lobe file, 7ccec7f 2026-10-03). Masked points per file:", md(mkt), "",
          "Headline numbers with masking off and with a 2x stricter threshold (-36 dB):",
          md(hlt.pivot_table(index="design", columns="variant", values=["R31", "R21", "R32"]).reset_index(), ".3f"), "",
          "Largest change of any ratio, in units of its one-pass yardstick: " + "; ".join(
              f"{vn}: {d} {ft} {r:.2f}x" for vn, (d, ft, r) in dmax.items()) + ".", ""]
    summ.append({"item": "A15 masking", "verdict": "CHANGED (one dependency found)" if max(t[2] for t in dmax.values()) > 1
                 else "CONFIRMED",
                 "old -> new": "; ".join(f"{vn}: largest move {d} {ft} = {r:.2f}x yardstick" for vn, (d, ft, r) in dmax.items())
                               + "; threshold fixed 2026-09-27, before the lobe files",
                 "evidence": "review2/A15_*.csv"})

    # ================================================================== A16 sub-bands
    a16 = []
    for bn, band in BANDS.items():
        mu = fmask(f, band)
        mu_u = fmask(fu, band)
        Xb, nmb, _, _ = features(f[mu], np.stack([Sd[d][mu] for d in LOBE_ALL]))
        Xub, nmub, _, _ = features(fu[mu_u], Su[:, mu_u])
        vb = {d: {ft: float(Xb[i][nmb.index(ft)]) for ft in ("R31", "R21", "R32")} for i, d in enumerate(LOBE_ALL)}
        yd = {ft: max(abs(vb[bb][ft] - vb[aa][ft]) for aa, bb in L8.PAIRS.values()) for ft in ("R31", "R21", "R32")}
        r31u = [float(Xub[s][nmub.index("R31")]) for s in range(len(ucls))]
        gap_u = min(r31u[s] for s in N_) - max(r31u[s] for s in AD_)
        row = {"band": bn, "uniform: min Normal R31 - max AD R31 (dB)": gap_u, "R31 one-pass yardstick": yd["R31"],
               "uniform gap / yardstick": gap_u / yd["R31"]}
        for st in ("lobe_A", "lobe_B"):
            h = STAGES[st][0]
            gaps = [vb[h]["R31"] - vb[d]["R31"] for d in STAGES[st][1:]]
            row[f"{st}: min(Normal - stage) R31 / yardstick"] = min(gaps) / yd["R31"]
            r21s = [vb[d]["R21"] for d in STAGES[st]]
            r32s = [vb[d]["R32"] for d in STAGES[st]]
            row[f"{st}: R21 monotone"] = bool(np.all(np.diff(r21s) > 0))
            row[f"{st}: R32 monotone"] = bool(np.all(np.diff(r32s) < 0))
            row[f"{st}: Mild-Severe R21 gap / yardstick"] = (vb[STAGES[st][3]]["R21"] - vb[STAGES[st][1]]["R21"]) / yd["R21"]
        row["LeftOnly - Healthy_new R31 / yardstick"] = (vb[H6]["R31"] - vb[LO]["R31"]) / yd["R31"]
        cpb = {d: {k: float(v[mu].mean()) for k, v in cp[d].items()} for d in SYM + [LO]}
        n3 = 0
        for k in cpb[LO]:
            null = [cpb[d][k] for d in SYM]
            yd_ = max(abs(cpb[bb][k] - cpb[aa][k]) for aa, bb in L8.PAIRS.values())
            n3 += floor_rule(cpb[LO][k], null, yd_)["ratio"] >= 3
        row["LeftOnly phase cross-ratios >= 3x (R1c)"] = n3
        a16.append(row)
    a16t = pd.DataFrame(a16)
    a16t.to_csv(OUT / "A16_subbands.csv", index=False)
    L += ["## A16. Disjoint sub-bands (no refitting; effect sizes against the sub-band's own one-pass yardstick)",
          md(a16t, ".2f"), ""]
    summ.append({"item": "A16 sub-bands", "verdict": "CHANGED (frequency dependence stated)",
                 "old -> new": "3.2-4.2 only -> " + "; ".join(
                     f"{r.band}: uniform gap {r['uniform gap / yardstick']:.1f}x, lobe_A min {r['lobe_A: min(Normal - stage) R31 / yardstick']:.1f}x, "
                     f"lobe_B min {r['lobe_B: min(Normal - stage) R31 / yardstick']:.1f}x, phase CR {r['LeftOnly phase cross-ratios >= 3x (R1c)']}/22"
                     for _, r in a16t.iterrows()),
                 "evidence": "review2/A16_subbands.csv"})

    # ================================================================== A19 2x noise
    prof2 = NoiseProfile("typical_2x", 0.5, 4.0, -64.0, 0.0)
    aug = dict(cfg.get("augment", {}))
    aug2 = {**aug, "amp_sd": 2 * aug.get("amp_sd", 0), "phase_sd_deg": 2 * aug.get("phase_sd_deg", 0),
            "jitter_mhz": 2 * aug.get("jitter_mhz", 0)}
    cfg_v = load_config(ROOT, "config_repeats.yaml")
    dv = load_dataset(cfg_v, ROOT)
    Sv2 = to_ring_order(dv.S, dv.port_to_ant)
    iH = dv.files.index("new_Healthy.s6p")
    gate = QualityGate(cfg["gate"], f, mode="gain_invariant")
    gate.fit_detune(draws(f, Sv2[iH], PROFILES["typical"], 200, np.random.default_rng([cfg["seed"], 70]),
                          {**aug, "gain_err_db": 0.5}))
    thr_ = pd.read_csv(ROOT / "results/v2_with_v1_repeats/03/thresholds.csv")
    gate.set_floor_limit(float(thr_[(thr_.feature == "M5.C3") & (thr_.profile == "typical")].tau_dB.iloc[0]))
    conds = {"1x: typical, ±0.5 dB": (PROFILES["typical"], {**aug, "gain_err_db": 0.5}),
             "2x: noise, ±1 dB": (prof2, {**aug2, "gain_err_db": 1.0}),
             "2x: noise, ±4 dB ±20°": (prof2, {**aug2, "gain_err_db": 4.0, "phase_err_deg": 20.0})}
    expect = {H6: "Normal", H7: "Normal", MCI: "Normal"}
    a19 = []
    for ci, (cn, (pr, ac)) in enumerate(conds.items()):
        for di, d in enumerate(LOBE_ALL):
            D = draws(f, Sd[d], pr, args.n, np.random.default_rng([cfg["seed"], 119, ci, di]), ac)
            inv = gate.check(D)["invalid"]
            lab = apply_rule(ROOT / "results/04/frozen_rule.json", f, D)
            bl = np.where(inv, "INVALID", lab["binary_R31"])
            want = expect.get(d, "AD")
            a19.append({"condition": cn, "design": d, "expected": want, "fraction expected": float((bl == want).mean()),
                        "UNCERTAIN": float((bl == "UNCERTAIN").mean()), "INVALID": float(inv.mean())})
        D = draws(f, Sd[LO], pr, args.n, np.random.default_rng([cfg["seed"], 129, ci]), ac)
        cpn = lr_cr_phase(D)
        n3m = 0
        for k in cpn:
            null = [float(cp[d][k].mean()) for d in SYM]
            yd_ = max(abs(float(cp[bb][k].mean() - cp[aa][k].mean())) for aa, bb in L8.PAIRS.values())
            fr = floor_rule(float(cp[LO][k].mean()), null, yd_)
            n3m += abs(float(cp[LO][k].mean())) / max(fr["clean ruler"], float(np.std(cpn[k].mean(-1), ddof=1))) >= 3
        a19.append({"condition": cn, "design": "LeftOnly phase cross-ratios >= 3x measured (R1c)", "expected": "",
                    "fraction expected": float(n3m)})
    a19t = pd.DataFrame(a19)
    a19t.to_csv(OUT / "A19_noise_2x.csv", index=False)
    L += ["## A19. Noise model at 2x",
          "Provenance: the noise profiles (per-entry 0.25 dB / 2 deg / -70 dB floor for 'typical') and the setup "
          "perturbation (1.5% amplitude, 10 deg per port, 1 MHz jitter) were chosen in Prompt 02 (89d4f23, 2026-09-27); "
          "the ±0.5 / ±2 dB and ±10 deg calibration errors were chosen in the Prompt 03 follow-ups (6eca5d7). None comes "
          "from a measured VNA/antenna dataset. Every claim is conditional on them. At 2x (per-entry 0.5 dB / 4 deg / -64 dB, "
          "setup 3% / 20 deg / 2 MHz, calibration ±1 dB or ±4 dB ±20 deg):",
          md(a19t.pivot_table(index="design", columns="condition", values="fraction expected").reset_index(), ".3f"), "",
          md(a19t[a19t.condition.str.startswith("2x")][["condition", "design", "UNCERTAIN", "INVALID"]], ".3f"), ""]
    lab2 = a19t[a19t.condition.str.startswith("2x: noise, ±4") & ~a19t.design.str.startswith("LeftOnly phase")]
    summ.append({"item": "A19 noise model", "verdict": "CHANGED (conditional claims stated)",
                 "old -> new": "unstated -> chosen, not measured; at 2x noise and ±4 dB/±20°: detection fraction expected "
                               + ", ".join(f"{r.design} {r['fraction expected']:.2f}" for _, r in lab2.iterrows()),
                 "evidence": "review2/A19_noise_2x.csv"})

    # ================================================================== A20 04 between-solve covariance regularisation
    L04 = _load("l04", "04_likelihood.py")
    acfg4 = {**dict(cfg_u.get("augment", {})), "gain_err_db": 0.5}
    X4 = {}
    for s in range(len(ucls)):
        rng4 = np.random.default_rng([cfg_u["seed"], 40, s, 0])
        X4[s], nm4, grp4, sing4 = features(fu, draws(fu, Su[s], PROFILES["typical"], 150, rng4, acfg4))
    sc = np.concatenate([X4[s] - X4[s].mean(0) for s in X4]).std(0, ddof=1)
    fsets = {k: v for k, v in {**grp4, **sing4}.items() if k in ("G_ratio", "G_coup", "R31", "C3", "C2")}
    a20 = []
    stage_of = dict(enumerate(ucls))
    for gname, idx in fsets.items():
        D = {s: (X4[s] / sc)[:, idx] for s in X4}
        means = {s: D[s].mean(0) for s in D}
        W = np.array([(means[bb] - means[aa]) / np.sqrt(2) for aa, bb in pairs_u])
        Sb0, lv, lr = L04.shrink_between(W)
        for scale in (0.1, 1.0, 10.0):
            mu, cov = {}, {}
            for c in ("Normal", "MCI", "Mild", "Moderate", "Severe", "AD"):
                sols = [s for s in D if (ucls[s] == c or (c == "AD" and ucls[s] in ("Mild", "Moderate", "Severe")))]
                Zc = np.concatenate([D[s] - means[s] for s in sols])
                Sm = L04.ledoit_wolf(Zc)[0]
                sm = {}
                for s in sols:
                    sm.setdefault(stage_of[s], []).append(means[s])
                smv = np.array([np.mean(v, 0) for v in sm.values()])
                m_ = smv.mean(0)
                Sst = ((smv - m_).T @ (smv - m_)) / len(smv) if len(smv) > 1 else 0
                mu[c], cov[c] = m_, Sm + scale * Sb0 + Sst
            for a, bb in (("Normal", "AD"), ("Mild", "Severe"), ("Normal", "Mild"), ("MCI", "Normal")):
                J, B = L04.divergences(mu[a], cov[a], mu[bb], cov[bb])
                a20.append({"features": gname, "dim": len(idx), "pair": f"{a}|{bb}", "between-cov scale": scale,
                            "J (sym. KL)": J, "B (Bhattacharyya)": B, "repeat pairs": len(W),
                            "lambda_var": lv, "lambda_corr": lr,
                            "cond(Sigma_b)": float(np.linalg.cond(Sb0)) if Sb0.ndim == 2 and Sb0.shape[0] > 1 else 1.0})
    a20t = pd.DataFrame(a20)
    a20t.to_csv(OUT / "A20_between_cov.csv", index=False)
    a20p = a20t.pivot_table(index=["features", "pair"], columns="between-cov scale", values="J (sym. KL)").reset_index()
    L += ["## A20. Between-solve covariance (Prompt 04 model)",
          f"Sigma_b is estimated from the {len(pairs_u)} v1/v2 repeat pairs (d/sqrt2), i.e. at most rank {len(pairs_u)}, shrunk "
          "toward median variances (Opgen-Rhein & Strimmer) and zero correlations (Schafer & Strimmer). Symmetric KL J with "
          "Sigma_b scaled x0.1 / x1 / x10:", md(a20p, ".3g"), ""]
    rat = a20p.assign(r=lambda t: t[0.1] / t[10.0])
    summ.append({"item": "A20 between-solve covariance", "verdict": "CHANGED (sensitivity stated)",
                 "old -> new": f"single shrunk estimate from {len(pairs_u)} pairs -> J changes by a factor "
                               f"{rat.r.min():.1f}-{rat.r.max():.0f} between x0.1 and x10; Normal|AD for R31: "
                               + ", ".join(f"x{s}: {a20p[(a20p.features == 'R31') & (a20p.pair == 'Normal|AD')][s].iloc[0]:.0f}"
                                           for s in (0.1, 1.0, 10.0)),
                 "evidence": "review2/A20_between_cov.csv"})

    # ================================================================== A21 leave-one-solve-out, per fold
    a21 = []
    for s_out in N_ + AD_:
        ns = [s for s in N_ if s != s_out] or N_
        as_ = [s for s in AD_ if s != s_out]
        t_ = tau_of(ns, as_)
        x = db31[s_out]
        want = "Normal" if s_out in N_ else "AD"
        lab = np.where(x < t_ - m_det, "AD", np.where(x > t_ + m_det, "Normal", "UNCERTAIN"))
        a21.append({"rule": "detection (R31)", "held out": ufile[s_out], "class": ucls[s_out], "training solves": len(ns) + len(as_),
                    "Normal solves in training": len(ns), "boundary dB": t_, "fraction correct": float((lab == want).mean()),
                    "UNCERTAIN": float((lab == "UNCERTAIN").mean())})
    for sch, (ft, cls) in bdefs.items():
        members = [s for s, c in enumerate(ucls) if any(c in mm for mm in cls)]
        for s_out in members:
            mu = []
            for mm in cls:
                ss = [s for s, c in enumerate(ucls) if c in mm and s != s_out]
                mu.append(np.mean([float(Xu_clean[s][col(ft)]) for s in ss]) if ss else np.nan)
            want = next(i for i, mm in enumerate(cls) if ucls[s_out] in mm)
            if np.isnan(mu).any():
                a21.append({"rule": sch, "held out": ufile[s_out], "class": ucls[s_out], "fraction correct": np.nan,
                            "note": "class has no training solve left"})
                continue
            x = feats_u[s_out][:, col(ft)]
            lab = np.argmin(np.abs(x[:, None] - np.array(mu)[None]), 1)
            a21.append({"rule": sch, "held out": ufile[s_out], "class": ucls[s_out], "training solves": len(members) - 1,
                        "boundary dB": ", ".join(f"{0.5 * (mu[i] + mu[i + 1]):.2f}" for i in range(2)),
                        "fraction correct": float((lab == want).mean())})
    a21t = pd.DataFrame(a21)
    a21t.to_csv(OUT / "A21_loso_folds.csv", index=False)
    fails = a21t[a21t["fraction correct"] < 0.95]
    L += ["## A21. Leave-one-solve-out, every fold (training: uniform v1/v2 solves; held-out solve's 120 noisy draws)",
          md(a21t, ".3f"), ""]
    summ.append({"item": "A21 LOSO per fold", "verdict": "CHANGED (per-fold shown)" if len(fails) else "CONFIRMED",
                 "old -> new": f"averages -> {len(fails)} of {len(a21t)} folds below 0.95: "
                               + ", ".join(f"{r.rule} {r['held out']} {r['fraction correct']:.2f}" for _, r in fails.iterrows()),
                 "evidence": "review2/A21_loso_folds.csv"})

    # ================================================================== A22 univariate separability with solve bootstrap
    fts = ["R31", "R21", "R32", "k1_band", "k2_band", "k3_band", "logN"]
    pairs22 = {"Normal|AD": (["Normal"], ["Mild", "Moderate", "Severe"]), "Normal|Mild": (["Normal"], ["Mild"]),
               "Mild|Severe": (["Mild"], ["Severe"]), "Mild|Moderate": (["Mild"], ["Moderate"])}
    within = {ft: np.mean([feats_u[s][:, col(ft)].var(ddof=1) for s in range(len(ucls))]) for ft in fts}
    smean = {ft: np.array([feats_u[s][:, col(ft)].mean() for s in range(len(ucls))]) for ft in fts}

    def metrics(ft, A_, B_, sols_A, sols_B):
        bvar = np.mean([(smean[ft][bb] - smean[ft][aa]) ** 2 / 2 for aa, bb in pairs_u])
        def cls_stats(sols, stages):
            per = [np.mean([smean[ft][s] for s in sols if ucls[s] == st]) for st in stages if any(ucls[s] == st for s in sols)]
            return np.mean(per), within[ft] + bvar + (np.var(per) if len(per) > 1 else 0)
        mA, vA = cls_stats(sols_A, A_)
        mB, vB = cls_stats(sols_B, B_)
        dm2 = (mA - mB) ** 2
        F = dm2 / (vA + vB)
        Bh = dm2 / (4 * (vA + vB)) + 0.5 * np.log((vA + vB) / (2 * np.sqrt(vA * vB)))
        J = 0.5 * (vA / vB + vB / vA - 2) + 0.5 * dm2 * (1 / vA + 1 / vB)
        return F, Bh, J
    a22 = []
    for pn, (A_, B_) in pairs22.items():
        sA = [s for s, c in enumerate(ucls) if c in A_]
        sB = [s for s, c in enumerate(ucls) if c in B_]
        for ft in fts:
            pt = metrics(ft, A_, B_, sA, sB)
            bs = np.array([metrics(ft, A_, B_, list(rng.choice(sA, len(sA))), list(rng.choice(sB, len(sB))))
                           for _ in range(1000)])
            row = {"pair": pn, "feature": ft}
            for i, mn in enumerate(("Fisher", "Bhattacharyya", "sym. KL")):
                row[mn] = pt[i]
                row[f"{mn} 2.5%"], row[f"{mn} 97.5%"] = np.quantile(bs[:, i], [0.025, 0.975])
            a22.append(row)
    a22t = pd.DataFrame(a22)
    a22t.to_csv(OUT / "A22_separability.csv", index=False)
    from scipy.stats import spearmanr
    agree = []
    for pn in pairs22:
        sub = a22t[a22t.pair == pn]
        agree.append({"pair": pn, "rho(Fisher, Bhattacharyya)": spearmanr(sub.Fisher, sub.Bhattacharyya)[0],
                      "rho(Fisher, sym. KL)": spearmanr(sub.Fisher, sub["sym. KL"])[0],
                      "top feature (Fisher / B / KL)": " / ".join(sub.sort_values(m, ascending=False).feature.iloc[0]
                                                                  for m in ("Fisher", "Bhattacharyya", "sym. KL"))})
    agt = pd.DataFrame(agree)
    L += ["## A22. Separability metrics (univariate; class = mean of solve means; variance = within-solve noise + "
          "between-solve variance from the repeat pairs + stage scatter of merged classes; 95% bootstrap over solves)",
          "Fisher = dmu^2/(v1+v2); Bhattacharyya = dmu^2/(4(v1+v2)) + 0.5 ln((v1+v2)/(2 sqrt(v1 v2))); symmetric KL = "
          "0.5(v1/v2 + v2/v1 - 2) + 0.5 dmu^2 (1/v1 + 1/v2).", md(a22t, ".3g"), "", "Ranking agreement:", md(agt, ".2f"), ""]
    summ.append({"item": "A22 separability", "verdict": "CHANGED (intervals added)",
                 "old -> new": "point values -> " + "; ".join(f"{r.pair}: top {r['top feature (Fisher / B / KL)']}, rho "
                                                             f"{r['rho(Fisher, sym. KL)']:.2f}" for _, r in agt.iterrows()),
                 "evidence": "review2/A22_separability.csv"})

    # ================================================================== A23 R31 non-monotonic
    a23 = []
    for st, ds_ in (("lobe_A", STAGES["lobe_A"]), ("lobe_B", STAGES["lobe_B"])):
        for d in ds_:
            a23.append({"set": st, "design": d, "C1 neighbour": g(d, "C1 neighbour"), "C3 opposite": g(d, "C3 opposite"),
                        "R31": g(d, "R31"), "dC1 vs healthy": g(d, "C1 neighbour") - g(ds_[0], "C1 neighbour"),
                        "dC3 vs healthy": g(d, "C3 opposite") - g(ds_[0], "C3 opposite")})
    for s in range(len(ucls)):
        a23.append({"set": "uniform", "design": ufile[s], "C1 neighbour": float(Xu_clean[s][col("k1_band")]),
                    "C3 opposite": float(Xu_clean[s][col("k3_band")]), "R31": float(Xu_clean[s][col("R31")])})
    a23t = pd.DataFrame(a23)
    a23t.to_csv(OUT / "A23_R31_components.csv", index=False)
    need = {d: (tau - m_det) - g(d, "R31") for d in ("Severe_lobe", "Severe_lobe_c3")}
    L += ["## A23. Why R31 turns back at Severe",
          "R31 = C3 - C1 (dB). Components against the healthy head of the same set:", md(a23t, ".3f"), "",
          "From Moderate to Severe the opposite path C3 barely moves while the neighbour path C1 drops (CSF gaps of "
          "15.5-18 mm under every antenna reach the neighbour paths, which are flat below ~10 mm; round-1 dose-response, "
          "review/A6_neighbour_dose_response.csv). Severe would reach the edge of the AD zone (tau - m) after a further R31 "
          "rise of " + ", ".join(f"{d} {v:+.2f} dB" for d, v in need.items()) + ", i.e. a further C1 drop of that size with C3 "
          "fixed. With the measured neighbour slope beyond 10 mm that corresponds to roughly one more Moderate-to-Severe "
          "step of atrophy. This is an extrapolation, not a measurement.", ""]
    summ.append({"item": "A23 R31 non-monotonic", "verdict": "CHANGED (mechanism measured; claim narrowed)",
                 "old -> new": "'detection' -> robust detection is Mild/Moderate in the lobe set (Severe 1.4-1.7x); mechanism: "
                               f"C1 drop at Severe (lobe_A {a23t[(a23t.design == 'Severe_lobe')]['dC1 vs healthy'].iloc[0]:+.2f} dB) "
                               f"with C3 nearly flat; crossing needs a further {min(need.values()):.2f}-{max(need.values()):.2f} dB",
                 "evidence": "review2/A23_R31_components.csv"})

    # ================================================================== A24 R21 on one axis
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows24 = []
    for s in range(len(ucls)):
        rows24.append({"set": "uniform v1" if du.manifest.loc[s, "role"] == "mesh_repeat" else "uniform v2",
                       "design": ufile[s], "stage": ucls[s], "R21": float(Xu_clean[s][col("R21")])})
    stg_of = {H6: "Normal", H7: "Normal", "Mild_lobe": "Mild", "Mild_lobe_new": "Mild", "Moderate_lobe": "Moderate",
              "Moderate_lobe_c3": "Moderate", "Severe_lobe": "Severe", "Severe_lobe_c3": "Severe", LO: "LeftOnly", MCI: "MCI"}
    for st in ("lobe_v1", "lobe_A", "lobe_B", "tests"):
        ds_ = L8.V1.values() if st == "lobe_v1" else STAGES[st]
        for d in ds_:
            rows24.append({"set": st, "design": d, "stage": stg_of[d], "R21": g(d, "R21")})
    r24 = pd.DataFrame(rows24)
    r24.to_csv(OUT / "A24_R21_all.csv", index=False)
    onepass = {"Normal": abs(R["Y"]["Healthy 6->7"]["R21"]), "Mild": abs(R["Y"]["Mild 5->6"]["R21"]),
               "Moderate": abs(R["Y"]["Moderate 5->6"]["R21"]), "Severe": abs(R["Y"]["Severe 5->6"]["R21"])}
    uni = {st: abs(r24[(r24.set == "uniform v1") & (r24.stage == st)].R21.iloc[0] - r24[(r24.set == "uniform v2") & (r24.stage == st)].R21.iloc[0])
           for st in ("Normal", "Mild", "Moderate", "Severe")}
    adj = []
    for st in ("uniform v1", "uniform v2", "lobe_v1", "lobe_A", "lobe_B"):
        sub = r24[r24.set == st].set_index("stage")
        yy = uni if st.startswith("uniform") else onepass
        for a, bb in (("Normal", "Mild"), ("Mild", "Moderate"), ("Moderate", "Severe"), ("Mild", "Severe")):
            gap = float(sub.loc[bb, "R21"] - sub.loc[a, "R21"])
            adj.append({"set": st, "pair": f"{a}|{bb}", "R21 gap dB": gap, "sum of the two yardsticks": yy[a] + yy[bb],
                        "gap / sum": abs(gap) / (yy[a] + yy[bb]) if yy[a] + yy[bb] > 0 else np.inf,
                        "yardstick used": "v1-v2 sweep difference" if st.startswith("uniform") else "one-pass change"})
    adjt = pd.DataFrame(adj)
    adjt.to_csv(OUT / "A24_R21_pairs.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    sets_order = ["uniform v1", "uniform v2", "lobe_v1", "lobe_A", "lobe_B", "tests"]
    colors = {"Normal": "#1c5cab", "MCI": "#86b6ef", "Mild": "#eb6834", "Moderate": "#a8452b", "Severe": "#5a1f12",
              "LeftOnly": "#2f8f5b"}
    for i, st in enumerate(sets_order):
        sub = r24[r24.set == st]
        for _, r in sub.iterrows():
            ax.plot(r.R21, i, "o", color=colors[r.stage], ms=7)
            ax.annotate(r.stage[:3], (r.R21, i), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=7)
    for k_, bvals in enumerate(bfro["three"]):
        lo_q, hi_q = np.quantile(bboot["three"][:, k_], [0.025, 0.975])
        ax.axvspan(lo_q, hi_q, color="#e4e3de", zorder=0)
        ax.axvline(bvals, color="#5f5e59", ls="--", lw=1)
    ax.set_yticks(range(len(sets_order)), sets_order)
    ax.set_xlabel("R21 = second-neighbour / neighbour power (dB); dashed: frozen three-stage boundaries, grey: solve-bootstrap 95%")
    fig.savefig(FIG / "A24_R21_axis.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    close = adjt[adjt["gap / sum"] < 1]
    L += ["## A24. R21 on one axis", "Figure `figures/A24_R21_axis.png`.", md(r24, ".3f"), "",
          "Stage pairs against the sum of their yardsticks (lobe: one-pass change per stage; uniform: v1-v2 sweep "
          "difference):", md(adjt, ".3f"), "",
          "The frozen boundaries were fitted on the uniform solves on 2026-10-02 (2baddee/5192287), before the lobe files "
          "existed (2026-10-03); they were not placed after seeing the lobe designs. They were placed after seeing the "
          "uniform designs, which are their training data.", ""]
    summ.append({"item": "A24 R21 staging", "verdict": "CHANGED (pairs inside yardsticks listed)",
                 "old -> new": f"{len(close)} stage pairs separated by less than the sum of their yardsticks: "
                               + ", ".join(f"{r.set} {r.pair}" for _, r in close.iterrows()),
                 "evidence": "review2/A24_*.csv, figures/A24_R21_axis.png"})

    # ================================================================== A26 absorbed power
    def nmet(S):
        P = np.abs(S) ** 2
        Nt = 1 - P.sum(-2)                                    # (F, 6): power not returned to any port, per driven port
        refl = 1 - np.stack([P[:, t, t] for t in range(6)], -1)
        coup = Nt - refl                                      # = -sum over u != t |S_ut|^2
        return float(10 * np.log10(Nt.mean())), float(10 * np.log10(refl.mean())), float(-coup.mean())
    nu_ = {s: nmet(Su[s]) for s in range(len(ucls))}
    gapN = np.mean([nu_[s][0] for s in AD_]) - np.mean([nu_[s][0] for s in N_])
    sdN = float(np.sqrt(np.mean([(nu_[bb][0] - nu_[aa][0]) ** 2 / 2 for aa, bb in pairs_u])))
    bsN = []
    for _ in range(2000):
        pp_ = [pairs_u[i] for i in rng.integers(0, len(pairs_u), len(pairs_u))]
        sd_b = np.sqrt(np.mean([(nu_[bb][0] - nu_[aa][0]) ** 2 / 2 for aa, bb in pp_]))
        gb = np.mean([nu_[s][0] for s in rng.choice(AD_, len(AD_))]) - np.mean([nu_[s][0] for s in rng.choice(N_, len(N_))])
        bsN.append(abs(gb) / sd_b if sd_b > 0 else np.nan)
    a26 = pd.DataFrame([{"solve": ufile[s], "class": ucls[s], "N (not returned) dB": nu_[s][0],
                         "1 - reflection dB": nu_[s][1], "coupled power returned to other ports": nu_[s][2]}
                        for s in range(len(ucls))])
    a26.to_csv(OUT / "A26_absorbed.csv", index=False)
    L += ["## A26. 'Absorbed' power (power not returned to any port)",
          "N_t = 1 - sum_u |S_ut|^2 (driven port t; ring and band mean; it includes radiation to the HFSS boundary and "
          "antenna loss, not head absorption alone):", md(a26, ".4g"), "",
          f"AD - Normal gap {gapN:+.3f} dB against the solve-to-solve SD {sdN:.3f} dB (repeat pairs): {abs(gapN) / sdN:.2f}x "
          f"(bootstrap 95% {np.nanquantile(bsN, 0.025):.2f}-{np.nanquantile(bsN, 0.975):.2f}x). The coupled power is "
          f"~{np.mean([nu_[s][2] for s in nu_]):.1e} of the incident power, so N = 1 - reflection to within that; the weak "
          "(opposite, second-neighbour) entries cannot move N. The '0.89x' figure was not found anywhere in the repository.", ""]
    summ.append({"item": "A26 absorbed power", "verdict": "CHANGED (re-derived; 0.89x not found)",
                 "old -> new": f"'0.89x' -> {abs(gapN) / sdN:.2f}x (95% {np.nanquantile(bsN, 0.025):.2f}-{np.nanquantile(bsN, 0.975):.2f}x); "
                               f"N = 1 - reflection within ~1e-3, so weak-entry convergence cannot be the cause; N's "
                               f"solve-to-solve SD ({sdN:.3f} dB) is the reflection's",
                 "evidence": "review2/A26_absorbed.csv"})

    # ================================================================== C2 / C3 / C5 phase finding
    c2 = []
    heat = []
    for k in cp[LO]:
        lo_f = cp[LO][k]
        yd_f = np.max([np.abs(cp[bb][k] - cp[aa][k]) for aa, bb in L8.PAIRS.values()], 0)
        nmax_f = np.max([np.abs(cp[d][k]) for d in SYM], 0)
        ratio_f = np.abs(lo_f) / np.maximum(yd_f, nmax_f)
        heat.append(ratio_f)
        c2.append({"combination": k, "median one-pass yardstick (deg)": float(np.median(yd_f)),
                   "median |LeftOnly| (deg)": float(np.median(np.abs(lo_f))),
                   "frequencies >= 3x max(yard, null max)": int((ratio_f >= 3).sum()),
                   "of which in 3.30-3.65 GHz": int((ratio_f[variants['3.30-3.65 GHz']] >= 3).sum()),
                   "median yardstick 3.30-3.65 (deg)": float(np.median(yd_f[variants['3.30-3.65 GHz']])),
                   "median |LO| 3.30-3.65 (deg)": float(np.median(np.abs(lo_f[variants['3.30-3.65 GHz']])))})
    c2t = pd.DataFrame(c2)
    c2t.to_csv(OUT / "C2_phase_convergence.csv", index=False)
    fig, ax = plt.subplots(figsize=(11, 5))
    im = ax.imshow(np.array(heat), aspect="auto", cmap="viridis", vmin=0, vmax=4,
                   extent=[f[0] / 1e9, f[-1] / 1e9, len(heat) - 0.5, -0.5])
    ax.set_yticks(range(len(heat)), list(cp[LO]), fontsize=6)
    ax.set_xlabel("frequency (GHz)")
    fig.colorbar(im, ax=ax, label="|LeftOnly| / max(one-pass yardstick, largest symmetric design), per frequency")
    fig.savefig(FIG / "C2_phase_ratio_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    c3 = []
    for X in SYM + [LO]:
        others = [d for d in SYM if d != X]
        n_rms = n_max = 0
        for k in cp[LO]:
            v = float(cp[X][k].mean())
            null = np.array([float(cp[d][k].mean()) for d in others])
            yd_ = max(abs(float(cp[bb][k].mean() - cp[aa][k].mean())) for aa, bb in L8.PAIRS.values())
            n_rms += abs(v) / max(float(np.sqrt(np.mean(null ** 2))), yd_) >= 3
            n_max += abs(v) / max(float(np.abs(null).max()), yd_) >= 3
        c3.append({"file": X, ">= 3x (round-1 rule: max(null rms, yard))": n_rms, ">= 3x (R1c: max(null max, yard))": n_max})
    c3t = pd.DataFrame(c3)
    c3t.to_csv(OUT / "C3_null_counts.csv", index=False)
    nul3 = c3t[c3t.file != LO]
    L += ["## C. Phase finding (post hoc: found after unblinding with a statistic built after unblinding)",
          "**C2. Convergence per combination and frequency** (figure `figures/C2_phase_ratio_heatmap.png`):",
          md(c2t, ".2f"), "",
          "**C3. The identical statistic on every file** (each file judged against the other eight; 22 correlated "
          "combinations):", md(c3t), ""]
    lo3 = c3t.set_index("file").loc[LO]
    summ.append({"item": "C2 phase convergence", "verdict": "CHANGED (per frequency)",
                 "old -> new": f"band-mean yardstick -> per frequency: median one-pass yardstick "
                               f"{c2t['median one-pass yardstick (deg)'].median():.2f} deg vs median |LO| "
                               f"{c2t['median |LeftOnly| (deg)'].median():.2f} deg; cells >= 3x: "
                               f"{int(c2t['frequencies >= 3x max(yard, null max)'].sum())} of {len(c2t) * len(f)}",
                 "evidence": "review2/C2_phase_convergence.csv, figures/C2_phase_ratio_heatmap.png"})
    summ.append({"item": "C3 null distribution", "verdict": "CHANGED (count recomputed per file)",
                 "old -> new": f"16/22 -> LeftOnly {int(lo3.iloc[0])}/22 (round-1 rule) and {int(lo3.iloc[1])}/22 (R1c); "
                               f"symmetric files max {int(nul3.iloc[:, 1].max())} and {int(nul3.iloc[:, 2].max())}",
                 "evidence": "review2/C3_null_counts.csv"})

    st_ = pd.DataFrame(summ)
    st_.to_csv(OUT / "summary_stats.csv", index=False)
    L += ["## Summary (statistics part)", md(st_), ""]
    (OUT / "report_stats.md").write_text("\n".join(L), encoding="utf-8")
    print((OUT / "report_stats.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
