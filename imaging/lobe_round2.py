"""Round-2 adversarial review (imaging session): items R1-R7, B14-B25, G1-G8, C1-C6.

    python imaging/lobe_round2.py [--n 200]

Every number is recomputed from the raw .s6p files, the HFSS field exports and lobe_frozen.json (read only).
Predictions for R3 / C4 / C6 were committed first (results/imaging/round2_predictions.md, 0ceb626).
Writes results/imaging/lobe_round2.json; the text is written by imaging/lobe_round2_md.py.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import pickle
import subprocess
import sys
import warnings
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402
from scipy.stats import shapiro  # noqa: E402

from imaging import lobe_A as LA  # noqa: E402
from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_review as RV  # noqa: E402
from imaging import lobe_rulers as LR  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import MATS, OUT, PROFILES, ROOT, git_hash  # noqa: E402

EPS_0 = 8.8541878128e-12
H7, H6, LEFT, MCI = "Healthy_sliced", "Healthy_sliced_new", "LeftOnly_test_c3", "MCI_lobe_c3"
NULL9 = C3.SYMMETRIC                      # the nine mirror-symmetric solves
METH = (RL.METHODS[0], RL.METHODS[2], LR.WNAME)
SH = LR.SHORTM
MP, PM, mir = RV.MP, RV.PM, RV.mir
FIT = np.array([3.4e9, 3.6e9, 3.8e9])


def git_date(c):
    return subprocess.run(["git", "log", "-1", "--format=%ci", c], capture_output=True, text=True, cwd=ROOT).stdout.strip()


def mtime(stem):
    return datetime.fromtimestamp(os.path.getmtime(ROOT / "data" / "raw" / f"new_with_slices_{stem}.s6p")).isoformat(" ", "seconds")


# ======================================================================== shared estimators
def fx_of(ctx, m, ref, models=None, lam=None):
    return C3.make_x(models or ctx.model(ref), m, lam or ctx.lam)


def anti_lr(ctx, m, ref):
    """Reference-free mirror statistic: T(X) = (LR(X) - LR(mirror X)) / 2 (LR of the frozen inversion)."""
    fx = fx_of(ctx, m, ref)
    R = ctx.S[ref][ctx.fi]

    def T(X):
        return (RL.contrasts(fx(X[ctx.fi], R))["LR"] - RL.contrasts(fx(mir(X)[ctx.fi], R))["LR"]) / 2
    return T


def null_stats(vals, T):
    v = np.asarray(vals, float)
    a = np.abs(v)
    return dict(null=v.tolist(), mean=float(v.mean()), rms=float(np.sqrt(np.mean(v ** 2))), max_abs=float(a.max()),
                shapiro_W=float(shapiro(v).statistic), shapiro_p=float(shapiro(v).pvalue),
                rms_without_max=float(np.sqrt(np.mean(np.sort(v ** 2)[:-1]))),
                rank_p_two_sided=float((1 + np.sum(a >= abs(T))) / (len(v) + 1)),
                T=float(T), T_over_rms=float(abs(T) / np.sqrt(np.mean(v ** 2))), T_over_max=float(abs(T) / a.max()))


# ======================================================================== R1
def r1(ctx):
    out = {"stats": [], "per_design": []}
    for ref in (H7, H6):
        for m in METH:
            T = anti_lr(ctx, m, ref)
            nv = [T(ctx.S[d]) for d in NULL9]
            tl = T(ctx.S[LEFT])
            yard = max(abs(T(ctx.S[a]) - T(ctx.S[b])) for a, b in C3.ONE_PASS.values())
            st = null_stats(nv, tl)
            st.update(reference=ref, method=SH[m], yardstick=float(yard),
                      ruler_rms=max(yard, st["rms"]), ruler_max=max(yard, st["max_abs"]))
            st["ratio_rms_rule"] = abs(tl) / st["ruler_rms"]
            st["ratio_max_rule"] = abs(tl) / st["ruler_max"]
            out["stats"].append(st)
            for d, v in zip(NULL9, nv):
                out["per_design"].append(dict(reference=ref, method=SH[m], design=d, T=float(v)))
    # (b) per-path mirror residual of each symmetric file, band 3.2-4.2 GHz
    res = []
    for d in NULL9:
        S = SL.recip(ctx.S[d])
        row = dict(design=d)
        for i in range(len(SL.PAIRS)):
            j = PM[i]
            if j <= i:
                continue
            num = np.sqrt(np.mean(np.abs(S[i] - S[j]) ** 2))
            den = np.sqrt(np.mean(np.abs(S[i]) ** 2))
            ph = np.degrees(np.angle(S[i] / S[j]))
            lab = f"{RV.plabel(*SL.PAIRS[i])} vs {RV.plabel(*SL.PAIRS[j])}"
            row[f"{lab} dB"] = float(20 * np.log10(num / den))
            row[f"{lab} phase@fit deg"] = ", ".join(f"{ph[k]:+.1f}" for k in ctx.fi)
        res.append(row)
    out["mirror_residual"] = res
    # where Moderate_lobe's statistic comes from: per-path decomposition of its antisymmetric data (primary)
    out["moderate_decomp"] = path_decomp(ctx, RL.METHODS[0], H7, (ctx.S["Moderate_lobe"] - mir(ctx.S["Moderate_lobe"])) / 2)
    out["moderate_c3_decomp"] = path_decomp(ctx, RL.METHODS[0], H7,
                                            (ctx.S["Moderate_lobe_c3"] - mir(ctx.S["Moderate_lobe_c3"])) / 2)
    return out


def path_decomp(ctx, m, ref, dS_full):
    """Per-path contribution to LR of a dS input (Tikhonov dS model, exact)."""
    mdl = ctx.model(ref)["dS"]
    g = np.zeros(12)
    g[[7, 8]], g[[10, 11]] = 0.5, -0.5
    A = mdl.J.T @ mdl.J + ctx.lam["dS"] ** 2 * np.eye(12)
    wv = mdl.J @ np.linalg.solve(A, g)
    F = len(ctx.fi)
    n = len(SL.PAIRS) * F
    d = mdl.data(dS=SL.recip(dS_full)[:, ctx.fi])
    c = (wv[:n] * d[:n] + wv[n:] * d[n:]).reshape(len(SL.PAIRS), F).sum(1)
    order = np.argsort(-np.abs(c))[:5]
    return dict(total=float(c.sum()), top=[dict(path=RV.plabel(*SL.PAIRS[i]), contribution=float(c[i])) for i in order])


# ======================================================================== R2 / C2 / C3 / C5: phase statistics
def cross_ratios(S):
    """45 complex cross-ratios S_ab S_cd / (S_ac S_bd) etc. of a (..., F, 6, 6) array (reciprocal-averaged)."""
    Sb = 0.5 * (S + np.swapaxes(S, -1, -2))
    out = []
    for a, b, c, d in itertools.combinations(range(6), 4):
        prs = [Sb[..., a, b] * Sb[..., c, d], Sb[..., a, c] * Sb[..., b, d], Sb[..., a, d] * Sb[..., b, c]]
        nm = [f"T{a + 1}T{b + 1}·T{c + 1}T{d + 1}", f"T{a + 1}T{c + 1}·T{b + 1}T{d + 1}", f"T{a + 1}T{d + 1}·T{b + 1}T{c + 1}"]
        for i, j in itertools.combinations(range(3), 2):
            out.append((f"{nm[i]} / {nm[j]}", prs[i] / prs[j]))
    return out


def phase_cr_stats(S, fsel):
    """Left-right phase of every complex cross-ratio: arg(cr(S) / cr(mirror S)), degrees, mean over fsel."""
    a, b = cross_ratios(S), cross_ratios(mir(S))
    return np.array([np.degrees(np.angle(za[..., fsel] / zb[..., fsel])).mean(-1) for (_, za), (_, zb) in zip(a, b)]), \
        [n for n, _ in a]


def independent_cr(ctx):
    """18 algebraically distinct left-right phase statistics, and the 22 kept by the main session's filter
    (skip self-mirror with s = +1 and the second member of each mirror pair), which contains 4 exact duplicates."""
    rng = np.random.default_rng(3)
    Z = rng.normal(size=(6, 6)) + 1j * rng.normal(size=(6, 6))
    Z = 0.5 * (Z + Z.T)
    a = [z for _, z in cross_ratios(Z[None])]
    b = [z for _, z in cross_ratios(mir(Z)[None])]
    names = [n for n, _ in cross_ratios(Z[None])]
    MM = {}
    for n in range(45):
        for m in range(45):
            if np.allclose(b[n], a[m]):
                MM[n] = (m, 1)
            elif np.allclose(b[n], 1 / a[m]):
                MM[n] = (m, -1)
    keep22 = [n for n, (m, s_) in MM.items() if not ((m == n and s_ == 1) or (m != n and m < n))]
    v = {n: float(abs(np.angle(a[n] / b[n]))[0]) for n in keep22}
    keep18, seen = [], []
    for n in keep22:
        if any(abs(v[n] - x) < 1e-9 for x in seen):
            continue
        seen.append(v[n])
        keep18.append(n)
    return keep18, keep22, names


def r2(ctx):
    keep18, keep22, names = independent_cr(ctx)
    band = np.flatnonzero((ctx.f >= 3.2e9 - 1) & (ctx.f <= 4.2e9 + 1))
    out = {"n_distinct": len(keep18), "n_main_filter": len(keep22), "views": []}
    vlist = [("18 distinct", keep18, vn, fs) for vn, fs in
             (("band mean 3.2-4.2 GHz (main session's quantity)", band),
              ("3.4 GHz", ctx.fi[:1]), ("3.6 GHz", ctx.fi[1:2]), ("3.8 GHz", ctx.fi[2:]),
              ("band mean 3.30-3.65 GHz", np.flatnonzero((ctx.f >= 3.3e9 - 1) & (ctx.f <= 3.65e9 + 1))))] +         [("22 (main filter)", keep22, "band mean 3.2-4.2 GHz (main session's quantity)", band)]
    for setname, keep, vname, fsel in vlist:
        def st(X):
            return phase_cr_stats(X, fsel)[0][keep]
        tl = st(ctx.S[LEFT])
        nulls = np.array([st(ctx.S[d]) for d in NULL9])
        yard = np.max([np.abs(st(ctx.S[a]) - st(ctx.S[b])) for a, b in C3.ONE_PASS.values()], 0)
        rms = np.sqrt(np.mean(nulls ** 2, 0))
        mx = np.max(np.abs(nulls), 0)
        r_rms = np.abs(tl) / np.maximum(yard, rms)
        r_max = np.abs(tl) / np.maximum(yard, mx)
        # C3: the same count for every null file, ruler from the other eight (leave-one-out)
        per_file = []
        for k, d in enumerate(NULL9):
            oth = np.delete(nulls, k, 0)
            rr = np.abs(nulls[k]) / np.maximum(yard, np.sqrt(np.mean(oth ** 2, 0)))
            rm = np.abs(nulls[k]) / np.maximum(yard, np.max(np.abs(oth), 0))
            per_file.append(dict(design=d, n_ge3_rms_rule=int(np.sum(rr >= 3)), n_ge3_max_rule=int(np.sum(rm >= 3))))
        out["views"].append(dict(set=setname, view=vname, n=len(keep), left_ge3_rms_rule=int(np.sum(r_rms >= 3)),
                                 left_ge3_max_rule=int(np.sum(r_max >= 3)), left_beyond_null_max=int(np.sum(np.abs(tl) > mx)),
                                 left_ge3_yard=int(np.sum(np.abs(tl) >= 3 * yard)),
                                 best_ratio_rms_rule=float(r_rms.max()), best_ratio_max_rule=float(r_max.max()),
                                 median_yard_deg=float(np.median(yard)), median_null_max_deg=float(np.median(mx)),
                                 median_null_rms_deg=float(np.median(rms)), median_abs_left_deg=float(np.median(np.abs(tl))),
                                 per_file=per_file,
                                 top=[dict(name=names[keep[i]], left=float(tl[i]), yard=float(yard[i]), null_rms=float(rms[i]),
                                           null_max=float(mx[i]), ratio_rms=float(r_rms[i]), ratio_max=float(r_max[i]))
                                      for i in np.argsort(-r_rms)[:5]]))
    # the imaging pair quantity (b9_anti) on the same rulers: mirror-pair phase difference, per view
    pairs = []
    for vname, fsel in (("band mean 3.2-4.2 GHz", band), ("3.4 GHz", ctx.fi[:1]), ("3.6 GHz", ctx.fi[1:2])):
        def pst(X):
            S = SL.recip(X)
            return np.array([np.degrees(np.angle(S[i, fsel] / S[PM[i], fsel])).mean() for i in RV_LEFT])
        tl = pst(ctx.S[LEFT])
        nulls = np.array([pst(ctx.S[d]) for d in NULL9])
        yard = np.max([np.abs(pst(ctx.S[a]) - pst(ctx.S[b])) for a, b in C3.ONE_PASS.values()], 0)
        for k, i in enumerate(RV_LEFT):
            pairs.append(dict(view=vname, pair=f"{RV.plabel(*SL.PAIRS[i])} vs {RV.plabel(*SL.PAIRS[PM[i]])}",
                              left=float(tl[k]), yard=float(yard[k]), null_rms=float(np.sqrt(np.mean(nulls[:, k] ** 2))),
                              null_max=float(np.max(np.abs(nulls[:, k]))), null_max_design=NULL9[int(np.argmax(np.abs(nulls[:, k])))],
                              ratio_rms_rule=float(abs(tl[k]) / max(yard[k], np.sqrt(np.mean(nulls[:, k] ** 2)))),
                              ratio_max_rule=float(abs(tl[k]) / max(yard[k], np.max(np.abs(nulls[:, k]))))))
    out["pairs"] = pairs
    # C5: measurement level for the cross-ratio phases (band mean), Prompt 07 model draws of LeftOnly
    keep = keep18
    meas = {}
    for g in LR.GAIN:
        D = ctx._draws(ctx.f, ctx.S[LEFT], ctx.prof, max(ctx.n // 2, 20), np.random.default_rng([2026, 1005, 7]),
                       {**ctx.acfg, **LR.GAIN[g]})
        vals = np.array([phase_cr_stats(x, band)[0][keep] for x in D])
        sd = vals.std(0, ddof=1)
        tl = phase_cr_stats(ctx.S[LEFT], band)[0][keep]
        nulls = np.array([phase_cr_stats(ctx.S[d], band)[0][keep] for d in NULL9])
        yard = np.max([np.abs(phase_cr_stats(ctx.S[a], band)[0][keep] - phase_cr_stats(ctx.S[b], band)[0][keep])
                       for a, b in C3.ONE_PASS.values()], 0)
        r_rms = np.abs(tl) / np.maximum(yard, np.hypot(np.sqrt(np.mean(nulls ** 2, 0)), sd))
        r_max = np.abs(tl) / np.maximum(yard, np.hypot(np.max(np.abs(nulls), 0), sd))
        meas[g] = dict(median_sd_deg=float(np.median(sd)), n_ge3_rms_rule=int(np.sum(r_rms >= 3)),
                       n_ge3_max_rule=int(np.sum(r_max >= 3)), best_rms=float(r_rms.max()), best_max=float(r_max.max()))
    out["measured"] = meas
    return out


RV_LEFT = [i for i in range(len(SL.PAIRS)) if PM[i] != i and any(t in (1, 2) for t in SL.PAIRS[i])
           and not any(t in (4, 5) for t in SL.PAIRS[i])]


def c2(ctx):
    """Phase convergence of the exact quantities: per path, |S| level and the one-pass phase change at the fit
    frequencies; and the amplitude / phase parts of LR for every one-pass difference."""
    rows = []
    for i, (a, b) in enumerate(SL.PAIRS):
        S6 = SL.recip(ctx.S[H6])[i]
        row = dict(path=RV.plabel(a, b), type=LA.CLASSES[SL.ring_k(a, b)],
                   level_dB_fit=", ".join(f"{20 * np.log10(abs(S6[k])):.1f}" for k in ctx.fi))
        for nm, (p, q) in C3.ONE_PASS.items():
            dph = np.degrees(np.angle(SL.recip(ctx.S[p])[i, ctx.fi] / SL.recip(ctx.S[q])[i, ctx.fi]))
            row[f"{nm} phase deg"] = ", ".join(f"{v:+.1f}" for v in dph)
        lo = np.degrees(np.angle(SL.recip(ctx.S[LEFT])[i, ctx.fi] / SL.recip(ctx.S[H6])[i, ctx.fi]))
        row["LeftOnly − H6 phase deg"] = ", ".join(f"{v:+.1f}" for v in lo)
        rows.append(row)
    lr = []
    for nm, (p, q) in list(C3.ONE_PASS.items()) + [("LeftOnly − H6", (LEFT, H6))]:
        for m in METH:
            fx = fx_of(ctx, m, H6)
            R = ctx.S[H6]
            X = R + ctx.S[p] - ctx.S[q]
            amp = np.abs(X) * np.exp(1j * np.angle(R))
            pha = np.abs(R) * np.exp(1j * np.angle(X))
            lr.append(dict(difference=nm, method=SH[m], LR=RL.contrasts(fx(X[ctx.fi], R[ctx.fi]))["LR"],
                           LR_amp_part=RL.contrasts(fx(amp[ctx.fi], R[ctx.fi]))["LR"],
                           LR_phase_part=RL.contrasts(fx(pha[ctx.fi], R[ctx.fi]))["LR"]))
    return rows, lr


# ======================================================================== R3 / C4: detuning, resonances, sign
def resonance(f, s):
    k = int(np.argmin(np.abs(s)))
    if 0 < k < len(f) - 1:                       # parabolic refinement on |s| in dB
        y = 20 * np.log10(np.abs(s[k - 1:k + 2]))
        den = y[0] - 2 * y[1] + y[2]
        dk = 0.5 * (y[0] - y[2]) / den if den != 0 else 0.0
    else:
        dk = 0.0
    return float((f[k] + dk * (f[1] - f[0])) / 1e9), float(20 * np.log10(np.abs(s[k])))


def r3(ctx):
    f = ctx.f
    res = []
    for d in (H6, H7, LEFT, "Mild_lobe", MCI):
        row = dict(design=d)
        for a in range(6):
            fr, dp = resonance(f, ctx.S[d][:, a, a])
            row[f"T{a + 1} f_res GHz"], row[f"T{a + 1} depth dB"] = fr, dp
        res.append(row)
    yard_fr, yard_dp = {}, {}
    for a in range(6):
        yard_fr[f"T{a + 1}"] = max(abs(resonance(f, ctx.S[p][:, a, a])[0] - resonance(f, ctx.S[q][:, a, a])[0])
                                   for p, q in C3.ONE_PASS.values())
        yard_dp[f"T{a + 1}"] = max(abs(resonance(f, ctx.S[p][:, a, a])[1] - resonance(f, ctx.S[q][:, a, a])[1])
                                   for p, q in C3.ONE_PASS.values())
    # per-port (detuning) model of the complex log-change, LeftOnly vs H6, per frequency
    A = np.zeros((len(SL.PAIRS), 6))
    for i, (a, b) in enumerate(SL.PAIRS):
        A[i, a] += 1
        A[i, b] += 1
    trans = np.array([a != b for a, b in SL.PAIRS])
    per_f = []
    for fq in np.arange(3.30, 3.901, 0.05):
        k = int(np.argmin(np.abs(f - fq * 1e9)))
        y = np.log(SL.recip(ctx.S[LEFT])[:, k] / SL.recip(ctx.S[H6])[:, k])
        g, *_ = np.linalg.lstsq(A, y, rcond=None)
        fit = A @ g
        ya = (y - y[PM]) / 2
        fa = (fit - fit[PM]) / 2
        expl = 1 - np.sum(np.abs((ya - fa)[trans]) ** 2) / np.sum(np.abs(ya[trans]) ** 2)
        expl_ph = 1 - np.sum(((ya - fa).imag[trans]) ** 2) / np.sum((ya.imag[trans]) ** 2)
        i23, i56 = SL.PAIRS.index((1, 2)), SL.PAIRS.index((4, 5))
        refl = lambda a, b: 0.5 * (y[SL.PAIRS.index((a, a))] + y[SL.PAIRS.index((b, b))])  # noqa: E731
        obs = np.degrees(y[i23].imag - y[i56].imag)
        pred = np.degrees(refl(1, 2).imag - refl(4, 5).imag)
        per_f.append(dict(f_GHz=round(float(fq), 2), antisym_energy_explained_by_per_port=float(expl),
                          antisym_phase_explained_by_per_port=float(expl_ph),
                          obs_T23_minus_T56_deg=float(obs), per_port_fit_T23_minus_T56_deg=float(np.degrees(fa[i23].imag - fa[i56].imag) * 1),
                          reflection_product_pred_deg=float(pred),
                          g_phase_deg=", ".join(f"T{a + 1} {np.degrees(g[a].imag):+.1f}" for a in range(6))))
    return dict(resonance=res, resonance_one_pass_max_MHz={k: v * 1e3 for k, v in yard_fr.items()},
                depth_one_pass_max_dB=yard_dp, per_port=per_f)


def c4(ctx):
    f = ctx.f
    i23, i56 = SL.PAIRS.index((1, 2)), SL.PAIRS.index((4, 5))
    rows = []
    for fq in np.arange(3.20, 4.201, 0.05):
        k = int(np.argmin(np.abs(f - fq * 1e9)))
        row = dict(f_GHz=round(float(fq), 2))
        for ref in (H6, H7):
            r = SL.recip(ctx.S[LEFT])[:, k] / SL.recip(ctx.S[ref])[:, k]
            row[f"T2-T3 dphi vs {ref}"] = float(np.degrees(np.angle(r[i23])))
            row[f"T5-T6 dphi vs {ref}"] = float(np.degrees(np.angle(r[i56])))
        S6 = ctx.S[H6][k]
        row.update({"|S22| dB": float(20 * np.log10(abs(S6[1, 1]))), "|S66| dB": float(20 * np.log10(abs(S6[5, 5]))),
                    "|S23| dB": float(20 * np.log10(abs(S6[1, 2]))), "|S56| dB": float(20 * np.log10(abs(S6[4, 5])))})
        rows.append(row)
    # notches of the two transmission paths (local minima of |S| below the path's band median - 6 dB)
    notch = {}
    for lab, (a, b) in (("T2-T3", (1, 2)), ("T5-T6", (4, 5)), ("T1-T2", (0, 1)), ("T3-T4", (2, 3))):
        s = np.abs(ctx.S[H6][:, a, b])
        sdB = 20 * np.log10(s)
        mins = [float(f[k] / 1e9) for k in range(1, len(f) - 1) if s[k] < s[k - 1] and s[k] < s[k + 1]
                and sdB[k] < np.median(sdB) - 6]
        notch[lab] = mins
    return rows, notch


# ======================================================================== R4: R31 / R21 (read-only, shown not adopted)
def r4(ctx):
    from adstage.features.ring_features import features
    from adstage.io.masking import mask_glitches
    from adstage.io.touchstone import read_touchstone
    from imaging.common import load_config
    cfg = load_config()
    rule = json.loads((ROOT / "results" / "04" / "frozen_rule.json").read_text(encoding="utf-8"))
    band = rule["feature_spec"]["band_hz"]
    tau = rule["detection_binary_R31"]["tau_dB"]
    rows = []
    files = [("v2 uniform", f"new_{n}") for n in ("Healthy", "MCI", "MildAD", "ModerateAD", "SevereAD")] + \
            [("lobe", f"new_with_slices_{s}") for s, *_ in C3.REGISTRY]
    for fam, stem in files:
        t = read_touchstone(ROOT / "data" / "raw" / f"{stem}.s6p")
        s = mask_glitches(t.f_hz, t.s, float(cfg["qc"].get("glitch_thr_db", -30.0)))[0]
        S = SL.ant_matrix(s, cfg["ring"]["port_to_ant"])
        sel = (t.f_hz >= band[0] - 1) & (t.f_hz <= band[1] + 1)
        X, names, _, _ = features(t.f_hz[sel], S[None, sel])
        rows.append(dict(family=fam, file=stem, R31=float(X[0, names.index("R31")]), R21=float(X[0, names.index("R21")])))
    v = {r["file"]: r for r in rows}
    n_r21 = v["new_Healthy"]["R21"]
    ad_r21 = np.mean([v[f"new_{n}"]["R21"] for n in ("MildAD", "ModerateAD", "SevereAD")])
    tau21 = 0.5 * (n_r21 + ad_r21)                     # illustration only, NOT a frozen rule
    yard = {}
    for q in ("R31", "R21"):
        yard[q] = max(abs(v[f"new_with_slices_{a}"][q] - v[f"new_with_slices_{b}"][q]) for a, b in C3.ONE_PASS.values())
    for r in rows:
        r["R31 label"] = "AD" if r["R31"] < tau else "Normal"
        r["R31 margin / yard"] = (tau - r["R31"]) / yard["R31"]
        r["R21 label (illustr.)"] = "AD" if r["R21"] > tau21 else "Normal"
        r["R21 margin / yard"] = (r["R21"] - tau21) / yard["R21"]
    return dict(rows=rows, tau31=tau, tau21_illustration=float(tau21), yard=yard)


# ======================================================================== B14 / B15 / G3 / G4 / G5: fields
def field_items(ctx):
    from imaging.fields import Grid, read_fld
    fh, grids = SL.load_hfss_fields()
    out = {}
    g0 = grids[0][1]
    out["grid"] = dict(x=[float(g0.axes[0][0]), float(g0.axes[0][-1])], y=[float(g0.axes[1][0]), float(g0.axes[1][-1])],
                       z=[float(g0.axes[2][0]), float(g0.axes[2][-1])], step_mm=g0.step, n=[len(a) for a in g0.axes],
                       freqs_GHz=(fh / 1e9).tolist())
    P = g0.points()
    r = np.linalg.norm(P, axis=-1)
    head = r < 83.5
    z = P[..., 2]
    nanfrac = float(np.mean(~np.isfinite(np.abs(g0.E[head]).sum(-1))))
    out["grid"]["nan_fraction_in_head"] = nanfrac
    # G4: azimuth of the strongest field on the r = 85 mm shell, per file
    th, ph = np.meshgrid(np.radians(np.arange(30, 91, 5)), np.radians(np.arange(-180, 180, 2)), indexing="ij")
    shell = 85 * np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)], -1).reshape(-1, 3)
    g4 = []
    for t in range(6):
        E = np.nan_to_num(grids[t][1].sample(shell))
        k = int(np.argmax(np.sum(np.abs(E) ** 2, 1)))
        p = shell[k]
        g4.append(dict(file=f"E_Normal_T{t + 1}_3p6GHz.fld", az_deg=float(np.degrees(np.arctan2(p[1], p[0]))),
                       z_mm=float(p[2]), expected_az_deg=-90.0 + 60 * t))
    out["g4"] = g4
    # G3: polarisation just inside the skin in front of each antenna (r = 85 mm along the feed direction)
    feeds = {0: (-0.50, -79.32, 56.10), 1: (68.44, -40.09, 56.10), 2: (68.94, 39.23, 56.10), 3: (0.50, 79.32, 56.10),
             4: (-68.44, 40.09, 56.10), 5: (-68.94, -39.23, 56.10)}
    g3 = []
    for t, fc in feeds.items():
        u = np.array(fc) / np.linalg.norm(fc)
        p = 85 * u
        E = np.nan_to_num(grids[t][1].sample(p[None]))[0]
        rh = u
        phh = np.array([-u[1], u[0], 0.0]) / np.hypot(u[0], u[1])
        thh = np.cross(phh, rh)
        g3.append(dict(antenna=f"T{t + 1}", E_r=float(abs(E @ rh)), E_theta_meridian=float(abs(E @ thh)),
                       E_phi_ring=float(abs(E @ phh)),
                       ring_fraction=float(abs(E @ phh) ** 2 / (abs(E @ phh) ** 2 + abs(E @ thh) ** 2))))
    out["g3"] = g3
    # G5: share of each path's sensitivity |E_a . E_b| in z bands (head voxels, 3.6 GHz)
    g5 = []
    Eh = [np.nan_to_num(grids[t][1].E[head]) for t in range(6)]
    zh = z[head]
    for (a, b) in SL.PAIRS:
        s = np.abs(np.sum(Eh[a] * Eh[b], -1))
        tot = s.sum()
        g5.append(dict(path=RV.plabel(a, b), type=LA.CLASSES[SL.ring_k(a, b)], z_gt_40=float(s[zh > 40].sum() / tot),
                       z_0_40=float(s[(zh >= 0) & (zh <= 40)].sum() / tot), z_lt_0=float(s[zh < 0].sum() / tot)))
    out["g5"] = g5
    # B15: mirror asymmetry of the field exports, and what a 0.8 deg azimuth offset alone would give
    Pm = P.copy()
    Pm[..., 0] *= -1
    Mv = np.array([-1.0, 1.0, 1.0])
    b15 = []
    for a, b in ((0, 0), (1, 5), (2, 4), (3, 3)):
        Ea = grids[a][1].E[head]
        Eb_m = (grids[b][1].sample(Pm[head].reshape(-1, 3)) * Mv)
        num = np.linalg.norm(np.nan_to_num(Ea - Eb_m))
        rot = np.radians(0.8)
        R = np.array([[np.cos(rot), -np.sin(rot), 0], [np.sin(rot), np.cos(rot), 0], [0, 0, 1]])
        Er = grids[a][1].sample(P[head].reshape(-1, 3) @ R) @ R.T          # E'(p) = R E(R^T p)
        rnum = np.linalg.norm(np.nan_to_num(Ea - Er))
        den = np.linalg.norm(np.nan_to_num(Ea))
        b15.append(dict(pair=f"T{a + 1} vs mirror(T{b + 1})", mirror_rel_diff=float(num / den),
                        rotation_0p8deg_rel_diff=float(rnum / den)))
    out["b15"] = b15
    # B14: grid sensitivity of the kernel (T1 reflection at 3.6 GHz: 3 mm export vs the 4 mm 'wide' export)
    gw = Grid(*read_fld(ROOT / "data" / "fields" / "E_Normal_T1_3p6GHz_wide.fld"))
    xg, wg = np.polynomial.legendre.leggauss(SL.NTH)
    thg = np.arccos(xg)
    phg = np.deg2rad(SL.PHI_MID)
    TH, PH = np.meshgrid(thg, phg, indexing="ij")
    W = wg[:, None] * np.deg2rad(SL.DPHI)
    u = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)], -1)
    k3, k4 = [], []
    for rr in SL.R_MID[::4]:
        pts = (rr * u).reshape(-1, 3)
        for g, acc in ((grids[0][1], k3), (gw, k4)):
            E = np.nan_to_num(g.sample(pts)).reshape(len(thg), len(phg), 3)
            acc.append(np.sum(np.sum(E * E, -1) * W, 0) * rr ** 2)      # (n_phi,)
    k3, k4 = np.array(k3), np.array(k4)
    sec = SL.SECT_OF_PHI
    out["b14_grid"] = dict(rel_diff_total=float(np.linalg.norm(k3 - k4) / np.linalg.norm(k3)),
                           per_sector_rel_diff=[float(abs(k3[:, sec == s].sum() - k4[:, sec == s].sum()) / abs(k3[:, sec == s].sum()))
                                                for s in range(6)])
    return out


def b14_born(ctx):
    rows, size = RV.b6(ctx)
    ones = np.ones(len(ctx.fh))
    pred = ctx.kappa * SL.predict(ctx.P, SL.delta_map("LeftOnly_test", ctx.fh), ones)
    sym = {}
    for ref in (H7, H6):
        obs = SL.recip(ctx.S[LEFT] - ctx.S[ref])[:, ctx.fi]
        ps, os_ = (pred + pred[PM]) / 2, (obs + obs[PM]) / 2
        pa, oa = (pred - pred[PM]) / 2, (obs - obs[PM]) / 2
        sym[ref] = dict(symmetric_part_rel_err=float(np.linalg.norm(ps - os_) / np.linalg.norm(os_)),
                        antisymmetric_part_rel_err=float(np.linalg.norm(pa - oa) / np.linalg.norm(oa)),
                        antisym_over_sym_obs=float(np.linalg.norm(oa) / np.linalg.norm(os_)))
    return dict(rows=rows, size=size, leftonly_parts=sym)


# ======================================================================== B16: depth dependence (Born-internal)
def b16(ctx):
    fh = ctx.fh
    w = 2 * np.pi * fh[:, None, None]
    r = SL.R_MID[:, None]
    cols = (SL.SECT_OF_PHI == 2)[None, :]

    def ce(m):
        return m[0] - 1j * m[1] / (w * EPS_0)
    N, Mi = MATS["Normal"], MATS["Mild"]
    e = 11.5
    maps = {}
    d = np.zeros((len(fh), len(SL.R_MID), len(SL.PHI_MID)), complex)
    sel = ((r >= 83 - e) & (r < 83)) & cols
    d[:, sel] = (ce(N["csf"]) - ce(N["gray"]))[:, :, 0]
    maps["S3 gap only (CSF replaces gray 71.5-83 mm, healthy materials)"] = d.copy()
    d = np.zeros_like(d)
    sel = ((r >= 76) & (r < 83)) & cols
    d[:, sel] = (ce(Mi["gray"]) - ce(N["gray"]))[:, :, 0]
    sel = ((r >= 25) & (r < 76)) & cols
    d[:, sel] = (ce(Mi["white"]) - ce(N["white"]))[:, :, 0]
    maps["S3 materials only (gray, white -> Mild, no geometry change)"] = d.copy()
    d = np.zeros_like(d)
    sel = ((r >= 25) & (r < 60)) & cols
    d[:, sel] = (ce(Mi["white"]) - ce(N["white"]))[:, :, 0]
    maps["S3 deep white only (25-60 mm -> Mild)"] = d.copy()
    out = []
    wsens = np.abs(ctx.P).sum((0, 1))
    R = ctx.S[H6]
    for nm, dm in maps.items():
        pred = SL.predict(ctx.P, dm, ctx.kappa)
        Ssyn = R[ctx.fi].copy()
        for i, (a, b) in enumerate(SL.PAIRS):
            Ssyn[:, a, b] += pred[i]
            if a != b:
                Ssyn[:, b, a] += pred[i]
        m3 = np.broadcast_to(cols & (r < 83.5), wsens.shape)
        true_s3 = float(np.sum(wsens * m3 * (-dm[1].imag)) / np.sum(wsens * m3))
        for m in METH:
            x = fx_of(ctx, m, H6)(Ssyn, R[ctx.fi])
            out.append(dict(change=nm, method=SH[m], true_S3_sensweighted=true_s3,
                            **{s: float(x[6 + k]) for k, s in enumerate(["S1", "S2", "S3", "S4", "S5", "S6"])},
                            LR=RL.contrasts(x)["LR"]))
    return out


# ======================================================================== B17: lambda
def b17(ctx):
    rows = []
    cases = [("Mild", "Mild_lobe", H7), ("Moderate", "Moderate_lobe", H7), ("Severe", "Severe_lobe", H7),
             ("Mild (A)", "Mild_lobe", H6), ("Moderate (A)", "Moderate_lobe", H6), ("Severe (A)", "Severe_lobe", H6),
             ("LeftOnly", LEFT, H7), ("LeftOnly", LEFT, H6), ("MCI", MCI, H7), ("MCI", MCI, H6)]
    for lab, st, ref in cases:
        for m in RL.METHODS[:1] + RL.METHODS[2:3]:
            calls = {}
            for s in (0.3, 1.0, 3.0):
                lam = {k: v * s for k, v in ctx.lam.items()}
                x = fx_of(ctx, m, ref, lam=lam)(ctx.S[st][ctx.fi], ctx.S[ref][ctx.fi])
                c = RL.apply_rules(x, ctx.fz["rules"][m])
                calls[s] = (" ".join(f"S{k + 1}" for k in range(6) if c["affected"][k]) or "none") + f" | {c['side']} | {c['frontback']}"
            rows.append(dict(design=lab, reference="H7" if ref == H7 else "H6", method=m, **{f"lambda x{s}": v for s, v in calls.items()},
                             flips=len(set(calls.values())) > 1))
    return rows


# ======================================================================== B20: family-wise chance of a side call
def b20(ctx):
    variants = 0
    left_null = {d: 0 for d in NULL9 if d not in (H7, H6)}
    right_null = dict(left_null)
    leftonly = {"left": 0, "right": 0, "none": 0}
    sets = {"3.4/3.6/3.8": [0, 1, 2], "3.4": [0], "3.6": [1], "3.8": [2], "3.4/3.6": [0, 1], "3.4/3.8": [0, 2], "3.6/3.8": [1, 2]}
    for ref in (H7, H6):
        R = ctx.S[ref]
        for sn, idx in sets.items():
            idx = np.array(idx)
            fif = ctx.fi[idx]
            M = LA.models(ctx.K6[:, idx], ctx.fh[idx], fif, ctx.kappa[idx], R, LA.KEEP_ALL)
            for m in RL.METHODS:
                for s in (0.3, 1.0, 3.0):
                    lam = {k: v * s for k, v in ctx.lam.items()}
                    fx = C3.make_x(M, m, lam)
                    variants += 1
                    c = RL.apply_rules(fx(ctx.S[LEFT][fif], R[fif]), ctx.fz["rules"][m])
                    leftonly[c["side"]] += 1
                    for d in left_null:
                        if d == ref:
                            continue
                        c = RL.apply_rules(fx(ctx.S[d][fif], R[fif]), ctx.fz["rules"][m])
                        left_null[d] += c["side"] == "left"
                        right_null[d] += c["side"] == "right"
    return dict(variants=variants, leftonly=leftonly, null_left_calls=left_null, null_right_calls=right_null)


# ======================================================================== B21: CRLB vs model error vs measurement
def b21(ctx):
    rows = []
    for ref in (H7,):
        M = ctx.model(ref)
        cr_dS = M["dS"].crlb()[6:12]
        cr_w = np.sqrt(np.clip(np.diag(np.linalg.pinv(M["wlog"].J.T @ M["wlog"].J)), 0, None))[6:12]
        ones = np.ones(len(ctx.fh))
        R = ctx.S[ref]
        me = []
        for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe"):
            pred = ctx.kappa * SL.predict(ctx.P, SL.delta_map(d, ctx.fh), ones)
            Ssyn = R[ctx.fi].copy()
            for i, (a, b) in enumerate(SL.PAIRS):
                Ssyn[:, a, b] += pred[i]
                if a != b:
                    Ssyn[:, b, a] += pred[i]
            fx = fx_of(ctx, RL.METHODS[0], ref)
            me.append(np.abs(fx(ctx.S[d][ctx.fi], R[ctx.fi])[6:12] - fx(Ssyn, R[ctx.fi])[6:12]))
        me = np.max(me, 0)
        r = ctx.rulers("Mild_lobe", ref, RL.METHODS[0])
        meas = r[f"sd_{list(LR.GAIN)[0]}"][:6]
        noise = r["sd_noise"][:6]
        for k in range(6):
            rows.append(dict(sector=f"S{k + 1}", crlb_dS=float(cr_dS[k]), crlb_whitened_log=float(cr_w[k]),
                             noise_sd_MC=float(noise[k]), meas_sd_05dB=float(meas[k]), model_error_max=float(me[k])))
    return rows


# ======================================================================== B24: bias-corrected front/back
def b24(ctx):
    rows = []
    for setn, ref, mild, mod, sev in (("lobe_A", H6, "Mild_lobe", "Moderate_lobe", "Severe_lobe"),
                                      ("lobe_B", H7, "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3")):
        for m in METH:
            fx = fx_of(ctx, m, ref)
            R = ctx.S[ref][ctx.fi]
            fb = {d: RL.contrasts(fx(ctx.S[d][ctx.fi], R))["FB"] for d in (mild, mod, sev, MCI)}
            bias = 0.5 * (fb[mild] + fb[sev])
            bias_u = 0.5 * abs(fb[mild] - fb[sev])
            r = ctx.rulers(mod, ref, m)
            clean = max(r["yard"][7], r["floor"][7])
            corr = fb[mod] - bias
            u = float(np.hypot(bias_u, clean))
            rows.append(dict(set=setn, method=SH[m], FB_Moderate=fb[mod], FB_Mild=fb[mild], FB_Severe=fb[sev], FB_MCI=fb[MCI],
                             bias=bias, bias_halfrange=bias_u, clean_ruler=clean, corrected=corr, uncertainty=u,
                             ratio=abs(corr) / u))
    return rows


# ======================================================================== B25: per-port contributions
def b25(ctx):
    rows = []
    g_sel = {"S2": np.eye(12)[7], "S3": np.eye(12)[8], "S1": np.eye(12)[6],
             "LR": np.r_[np.zeros(7), 0.5, 0.5, 0, -0.5, -0.5], "FB": np.r_[np.zeros(6), 1, 0, 0, -1, 0, 0]}
    F = len(ctx.fi)
    n = len(SL.PAIRS) * F
    for lab, st, ref, qs in (("LeftOnly", LEFT, H7, ("S2", "S3", "LR")), ("Moderate (A)", "Moderate_lobe", H6, ("S1", "FB"))):
        mdl = ctx.model(ref)["dS"]
        A = mdl.J.T @ mdl.J + ctx.lam["dS"] ** 2 * np.eye(12)
        d = mdl.data(dS=SL.recip(ctx.S[st] - ctx.S[ref])[:, ctx.fi])
        for q in qs:
            wv = mdl.J @ np.linalg.solve(A, g_sel[q])
            c = (wv[:n] * d[:n] + wv[n:] * d[n:]).reshape(len(SL.PAIRS), F).sum(1)
            port = np.zeros(6)
            for i, (a, b) in enumerate(SL.PAIRS):
                if a == b:
                    port[a] += c[i]
                else:
                    port[a] += c[i] / 2
                    port[b] += c[i] / 2
            tot = c.sum()
            rows.append(dict(design=lab, quantity=q, value=float(tot), **{f"T{a + 1}": float(port[a]) for a in range(6)},
                             largest_port=f"T{int(np.argmax(np.abs(port))) + 1}",
                             largest_share=float(np.max(np.abs(port)) / np.sum(np.abs(port)))))
    return rows


# ======================================================================== G1/G2/G6/G7
def geometry_audit():
    txt = (ROOT / "data" / "hfss_geometry_audit_Healthy_sliced.txt").read_text(encoding="utf-8", errors="replace")
    keys = ["r_skin", "r_fat", "r_skull", "r_csf_outer", "r_hip", "r_brain", "r_csf ", "r_gray ", "r_white ",
            "r_brain_ad", "r_csf_inner", "r_csf_expanded", "ant_dist", "z_ebg", "r_gray_healthy", "r_white_healthy"]
    lines = [ln.strip() for ln in txt.splitlines() if " var " in ln and any(k.strip() in ln for k in keys)]
    objs = [ln.strip() for ln in txt.splitlines() if ("radius=" in ln or "WM_" in ln or "CSF" in ln or "Hippo" in ln)][:30]
    return dict(vars=lines, objects=objs)


def gabriel(tissue, f):
    """Gabriel et al. 1996 (Part III) four-pole Cole-Cole; parameters as transcribed here (validated below
    against the published 1 GHz values)."""
    P = {"gray": (4.0, [(45.0, 7.958e-12, 0.10), (400, 15.915e-9, 0.15), (2.0e5, 106.103e-6, 0.22), (4.5e7, 5.305e-3, 0.0)], 0.02),
         "white": (4.0, [(32.0, 7.958e-12, 0.10), (100, 7.958e-9, 0.10), (4.0e4, 53.052e-6, 0.30), (3.5e7, 7.958e-3, 0.02)], 0.02),
         "csf": (4.0, [(65.0, 7.958e-12, 0.10), (40, 1.592e-9, 0.0)], 2.0)}
    einf, poles, sig = P[tissue]
    w = 2 * np.pi * np.asarray(f, float)
    e = einf + sum(de / (1 + (1j * w * tau) ** (1 - a)) for de, tau, a in poles) + sig / (1j * w * EPS_0)
    return e.real, -e.imag * w * EPS_0


def g7():
    check = {t: gabriel(t, 1e9) for t in ("gray", "white", "csf")}
    ref1g = {"gray": (52.28, 0.985), "white": (38.58, 0.622), "csf": (68.44, 2.455)}   # published 1 GHz values
    rows = []
    for t, key in (("gray", "gray"), ("white", "white"), ("csf", "csf")):
        er, sg = MATS["Normal"][key]
        fgrid = np.linspace(1e9, 6e9, 501)
        ge, gs = gabriel(t, fgrid)
        fbest = float(fgrid[int(np.argmin((ge - er) ** 2 / er ** 2 + (gs - sg) ** 2 / sg ** 2))] / 1e9)
        row = dict(tissue=t, shehab_eps=er, shehab_sigma=sg, gabriel_1GHz=f"{check[t][0]:.2f} / {check[t][1]:.3f}",
                   published_1GHz=f"{ref1g[t][0]} / {ref1g[t][1]}", best_match_GHz=fbest)
        for fq in (3.2e9, 3.7e9, 4.2e9):
            e_, s_ = gabriel(t, fq)
            row[f"Gabriel {fq / 1e9:.1f} GHz"] = f"{float(e_):.1f} / {float(s_):.2f}"
        rows.append(row)
    return rows


# ======================================================================== main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    a = ap.parse_args()
    ctx = C3.Ctx(a.n)
    res = dict(code=git_hash(ROOT), frozen_code=ctx.fz["code"], n_draws=a.n)
    res["r1"] = r1(ctx)
    res["r2"] = r2(ctx)
    res["c2_paths"], res["c2_lr"] = c2(ctx)
    res["r3"] = r3(ctx)
    res["c4"], res["c4_notches"] = c4(ctx)
    res["r4"] = r4(ctx)
    res["fields"] = field_items(ctx)
    res["b14_born"] = b14_born(ctx)
    res["b16"] = b16(ctx)
    res["b17"] = b17(ctx)
    res["b20"] = b20(ctx)
    res["b21"] = b21(ctx)
    res["b24"] = b24(ctx)
    res["b25"] = b25(ctx)
    res["g_audit"] = geometry_audit()
    res["g7"] = g7()
    res["dates"] = dict(frozen_commit=git_date("fb5b775"), predictions_commit=git_date("62709e0"),
                        c3_scoring_commit=git_date("7944508"), round2_predictions_commit=git_date("0ceb626"),
                        leftonly_mtime=mtime(LEFT), mci_mtime=mtime(MCI), mild_mtime=mtime("Mild_lobe"),
                        glitch_rule_first_commit=subprocess.run(["git", "log", "--diff-filter=A", "--format=%h %ci", "--",
                                                                 "src/adstage/io/masking.py"], capture_output=True,
                                                                text=True, cwd=ROOT).stdout.strip())
    (RL.CACHE / "lobe_round2.pkl").write_bytes(pickle.dumps(res))
    (OUT / "lobe_round2.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item")
                                                     else (o.tolist() if hasattr(o, "tolist") else str(o))), encoding="utf-8")
    from imaging.lobe_round2_md import write_md
    write_md(res)
    print("done")


if __name__ == "__main__":
    main()
