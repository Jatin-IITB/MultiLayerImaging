"""Adversarial review of the lobe blind result (questions B1-B9 of 5 Oct):

    python imaging/lobe_review.py [--n 200]

Every number is recomputed from the raw .s6p files and the frozen state (lobe_frozen.json, read only).
Writes results/imaging/lobe_review.json and results/imaging/lobe_review.md.
"""
from __future__ import annotations

import argparse
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
import pandas as pd  # noqa: E402
from scipy.stats import norm  # noqa: E402

from imaging import lobe_A as LA  # noqa: E402
from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_rulers as LR  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, PROFILES, ROOT, git_hash  # noqa: E402
from imaging.lobe_review_md import write_md  # noqa: E402

MP = SL.mirror_perm()
MS = np.array([0, 5, 4, 3, 2, 1])                          # sector mirror S2<->S6, S3<->S5
PM = np.array([SL.PAIRS.index(tuple(sorted((int(MP[a]), int(MP[b]))))) for a, b in SL.PAIRS])
H7, H6, LEFT, MCI = "Healthy_sliced", "Healthy_sliced_new", "LeftOnly_test_c3", "MCI_lobe_c3"
REFS = {"H7 (frozen, primary)": H7, "H6 (matched)": H6}
METH = (RL.METHODS[0], RL.METHODS[2], LR.WNAME)
SH = LR.SHORTM


def mir(S):
    return S[..., MP[:, None], MP[None, :]]


def bar(r):
    return "established (≥ 3×)" if r >= 3 else ("sensitive (2–3×)" if r >= 2 else "not separable (< 2×)")


def plabel(a, b):
    return f"T{a + 1} refl." if a == b else f"T{a + 1}-T{b + 1}"


# ----------------------------------------------------------------------------------------------
def scalar_rulers(ctx, est, stage, ref, floor_stage):
    """Rulers of a scalar estimator est(S_stage_fi, S_ref_fi) for (stage - ref)."""
    fi, S = ctx.fi, ctx.S
    R = S[ref]
    clean = float(est(S[stage][fi], R[fi]))
    yard = max(abs(est((R + sg * (S[a] - S[b]))[fi], R[fi])) for a, b in C3.ONE_PASS.values() for sg in (1, -1))

    def fl(d):
        return float(np.sqrt(np.mean([est((R + sg * SL.permute(ctx.E[d], mm))[fi], R[fi]) ** 2
                                      for mm in ctx.maps for sg in (1, -1)])))
    fs = max(fl(d) for d in floor_stage) if isinstance(floor_stage, (tuple, list)) else fl(floor_stage)
    floor = float(np.hypot(fs, fl(ref)))
    out = dict(clean=clean, yard=float(yard), floor=floor)
    for kind in ("noise",) + tuple(LR.GAIN):
        A, B = ctx.dr(stage, kind), ctx.dr(ref, kind)
        v = np.array([est(a, b) for a, b in zip(A, B)])
        out[f"sd_{kind}"] = float(v.std(ddof=1))
    g05 = list(LR.GAIN)[0]
    out["ruler_clean"] = max(out["yard"], out["floor"])
    out["ruler_meas_quad"] = max(out["yard"], float(np.hypot(out["floor"], out[f"sd_{g05}"])))
    out["ruler_meas_max_old"] = max(out["sd_noise"], out["yard"], out["floor"], out[f"sd_{g05}"])
    for k in ("clean", "meas_quad", "meas_max_old"):
        out[f"ratio_{k}"] = abs(clean) / out[f"ruler_{k}"]
    return out


def lr_est(ctx, m, ref, models=None):
    fx = C3.make_x(models or ctx.model(ref), m, ctx.lam)
    return lambda a, b: RL.contrasts(fx(a, b))["LR"]


def fb_est(ctx, m, ref):
    fx = C3.make_x(ctx.model(ref), m, ctx.lam)
    return lambda a, b: RL.contrasts(fx(a, b))["FB"]


# ----------------------------------------------------------------------------------------------
def b1(ctx):
    """One bar for LR (LeftOnly) and FB (Moderate), both ruler definitions."""
    sym_a = ("Healthy_sliced_new", "Mild_lobe", "Moderate_lobe", "Severe_lobe", "MCI_lobe_c3")
    rows = []
    for rname, ref in REFS.items():
        for m in METH:
            r = scalar_rulers(ctx, lr_est(ctx, m, ref), LEFT, ref, sym_a)
            rows.append(dict(quantity="LR", comparison=f"LeftOnly − {rname}", floor_from="max of lobe_A symmetric designs",
                             method=SH[m], **r))
            r = scalar_rulers(ctx, lr_est(ctx, m, ref), LEFT, ref, ("Healthy_sliced_new", "MCI_lobe_c3"))
            rows.append(dict(quantity="LR", comparison=f"LeftOnly − {rname}", floor_from="pass-matched p6 designs (H6, MCI_c3)",
                             method=SH[m], **r))
    for m in METH:
        for st, ref, lab in (("Moderate_lobe", H6, "Moderate − H6 (lobe_A)"), ("Moderate_lobe", "Mild_lobe", "Moderate − Mild (lobe_A)"),
                             ("Moderate_lobe_c3", H7, "Moderate − H7 (lobe_B)"),
                             ("Moderate_lobe_c3", "Mild_lobe_new", "Moderate − Mild (lobe_B)"),
                             ("Mild_lobe", H6, "Mild − H6 (lobe_A, truth 0)"), ("Severe_lobe", H6, "Severe − H6 (lobe_A, truth 0)")):
            r = scalar_rulers(ctx, fb_est(ctx, m, ref), st, ref, st)
            rows.append(dict(quantity="FB", comparison=lab, floor_from="own design", method=SH[m], **r))
    fl = []
    for rname, ref in REFS.items():
        for m in METH:
            est = lr_est(ctx, m, ref)
            R = ctx.S[ref]
            for d in sym_a:
                v = [est((R + sg * SL.permute(ctx.E[d], mm))[ctx.fi], R[ctx.fi]) for mm in ctx.maps for sg in (1, -1)]
                fl.append(dict(reference=rname, method=SH[m], design=d, LR_floor_rms=float(np.sqrt(np.mean(np.square(v))))))
    ctx.lr_floors = fl
    for r in rows:
        r["bar_clean"] = bar(r["ratio_clean"])
        r["bar_meas"] = bar(r["ratio_meas_quad"])
    return rows


def b2a(ctx):
    rows = []
    for rname, ref in REFS.items():
        for m in METH:
            est = lr_est(ctx, m, ref)
            for d in ("Healthy_sliced_new", "Healthy_sliced", "Mild_lobe", "Moderate_lobe", "Severe_lobe",
                      "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3", "MCI_lobe_c3"):
                if d == ref:
                    continue
                rows.append(dict(reference=rname, method=SH[m], design=d,
                                 LR=float(est(ctx.S[d][ctx.fi], ctx.S[ref][ctx.fi]))))
    return rows


def sym_models(ctx, ref):
    """Exactly mirror-symmetrised kernels and noise weights (reference symmetrised for the weights)."""
    K = ctx.K6
    Ks = 0.5 * (K + K[PM][:, :, MS])
    Rs = 0.5 * (ctx.S[ref] + mir(ctx.S[ref]))
    M = LA.models(Ks, ctx.fh, ctx.fi, ctx.kappa, Rs, LA.KEEP_ALL)
    sig = SL.pair_sigma_f(Rs, PROFILES["typical"])[:, ctx.fi]
    M["wlog"] = LR.WhitenedLog(Ks, ctx.fh, ctx.kappa, sig, LA.KEEP_ALL, Rs[ctx.fi])
    asym = float(np.linalg.norm(K - K[PM][:, :, MS]) / np.linalg.norm(K))
    return M, asym


def mirror_rows(ctx, models_fn, tag):
    out = []
    fi, S = ctx.fi, ctx.S
    for rname, ref in REFS.items():
        Ms = models_fn(ref)
        for m in METH:
            fx = C3.make_x(Ms, m, ctx.lam)
            R = S[ref]
            xL = fx(S[LEFT][fi], R[fi])
            xM = fx(mir(S[LEFT])[fi], R[fi])
            xMM = fx(mir(S[LEFT])[fi], mir(R)[fi])
            cL, cM, cMM = RL.contrasts(xL), RL.contrasts(xM), RL.contrasts(xMM)
            out.append(dict(kernels=tag, reference=rname, method=SH[m], LR_left=cL["LR"], LR_mirror=cM["LR"],
                            LR_sum=cL["LR"] + cM["LR"], LR_anti=(cL["LR"] - cM["LR"]) / 2,
                            LR_mirror_both=cMM["LR"],
                            S2=xL[7], S3=xL[8], S5=xL[10], S6=xL[11],
                            mirror_S2=xM[7], mirror_S3=xM[8], mirror_S5=xM[10], mirror_S6=xM[11],
                            FB_left=cL["FB"], FB_mirror=cM["FB"]))
    return out


def b3_rulers(ctx):
    sym_a = ("Healthy_sliced_new", "Mild_lobe", "Moderate_lobe", "Severe_lobe", "MCI_lobe_c3")
    rows = []
    for rname, ref in REFS.items():
        for m in METH:
            lr = lr_est(ctx, m, ref)
            anti = (lambda lr_: (lambda a, b: (lr_(a, b) - lr_(mir(a), b)) / 2))(lr)
            ssum = (lambda lr_: (lambda a, b: lr_(a, b) + lr_(mir(a), b)))(lr)
            for nm, est in (("LR_anti = (LR − LR_mirror)/2", anti), ("LR_sum = LR + LR_mirror", ssum)):
                for fl_name, fl_set in (("max of lobe_A symmetric designs", sym_a),
                                        ("pass-matched p6 designs (H6, MCI_c3)", ("Healthy_sliced_new", "MCI_lobe_c3"))):
                    r = scalar_rulers(ctx, est, LEFT, ref, fl_set)
                    rows.append(dict(reference=rname, method=SH[m], estimator=nm, floor_from=fl_name, **r,
                                     bar_clean=bar(r["ratio_clean"]), bar_meas=bar(r["ratio_meas_quad"])))
    return rows


def b4(ctx):
    rows = []
    fz = ctx.fz
    for m in RL.METHODS:
        for rname, ref in REFS.items():
            fx = C3.make_x(ctx.model(ref), m, ctx.lam)
            x = fx(ctx.S[LEFT][ctx.fi], ctx.S[ref][ctx.fi])
            c = RL.apply_rules(x, fz["rules"][m])
            ok = c["side"] == "left" and c["affected"][1] and c["affected"][2] and not c["affected"][4] and not c["affected"][5]
            part = c["side"] == "left" and c["affected"][2] and not c["affected"][4] and not c["affected"][5]
            rows.append(dict(method=m, reference=rname, S2=x[7], S3=x[8], T_abs=fz["rules"][m]["T_abs"],
                             LR=c["LR"], side=c["side"],
                             called=" ".join(f"S{k + 1}" for k in range(6) if c["affected"][k]) or "none",
                             preregistered="SUCCESS" if ok else ("PARTIAL" if part else "FAIL")))
    # mechanism: the reference shift equals the Healthy 7-6 one-pass inversion (linear methods)
    fxm = C3.make_x(ctx.model(H6), RL.METHODS[0], ctx.lam)
    R = ctx.S[H6]
    shift_pred = fxm((R - (ctx.S[H7] - R))[ctx.fi], R[ctx.fi])[6:12]          # -(H7 - H6) as a stage
    xa = fxm(ctx.S[LEFT][ctx.fi], R[ctx.fi])[6:12]
    fxp = C3.make_x(ctx.model(H7), RL.METHODS[0], ctx.lam)
    xb = fxp(ctx.S[LEFT][ctx.fi], ctx.S[H7][ctx.fi])[6:12]
    return rows, dict(x_H7=xb.tolist(), x_H6=xa.tolist(), shift_observed=(xa - xb).tolist(),
                      shift_from_one_pass=shift_pred.tolist())


def b5(ctx, b1rows):
    w = [r for r in b1rows if r["quantity"] == "LR" and r["method"] == SH[LR.WNAME]
         and r["floor_from"].startswith("max")]
    looks = 5 * 2                      # methods (4 frozen + whitened) x references, all scored on LeftOnly LR
    out = []
    for r in w:
        for k in ("clean", "meas_quad", "meas_max_old"):
            z = r[f"ratio_{k}"]
            p1 = float(norm.sf(z))
            out.append(dict(comparison=r["comparison"], ruler=k, ratio=z, p_one_sided_if_gaussian=p1,
                            p_bonferroni=min(1.0, looks * p1)))
    c9182 = subprocess.run(["git", "log", "-1", "--format=%ci", "9182afd"], capture_output=True, text=True,
                           cwd=ROOT).stdout.strip()
    mt = datetime.fromtimestamp(os.path.getmtime(ROOT / "data" / "raw" / f"new_with_slices_{LEFT}.s6p")).isoformat(" ", "seconds")
    return out, dict(looks=looks, whitened_commit="9182afd", whitened_commit_time=c9182, leftonly_file_mtime=mt)


def b6(ctx):
    """Born (kappa-scaled) prediction of dS from the true sector changes vs HFSS dS, per path class."""
    rows = []
    fi = ctx.fi
    ones = np.ones(len(ctx.fh))
    for d, stem in (("Mild_lobe", "Mild_lobe"), ("Moderate_lobe", "Moderate_lobe"), ("Severe_lobe", "Severe_lobe"),
                    ("LeftOnly_test", LEFT), ("MCI_lobe", MCI)):
        pred = ctx.kappa * SL.predict(ctx.P, SL.delta_map(d, ctx.fh), ones)              # (21, F)
        for rname, ref in REFS.items():
            obs = SL.recip(ctx.S[stem] - ctx.S[ref])[:, fi]
            row = dict(design=d, reference=rname)
            for k, cls in enumerate(LA.CLASSES):
                sel = np.array([SL.ring_k(a, b) == k for a, b in SL.PAIRS])
                row[cls] = float(np.linalg.norm(pred[sel] - obs[sel]) / np.linalg.norm(obs[sel]))
            row["all"] = float(np.linalg.norm(pred - obs) / np.linalg.norm(obs))
            anti_o = obs - obs[PM]
            anti_p = pred - pred[PM]
            row["antisym part: |pred − obs| / |obs|"] = float(np.linalg.norm(anti_p - anti_o) / max(np.linalg.norm(anti_o), 1e-30))
            # what the reconstruction makes of the model error
            for m in (RL.METHODS[0], RL.METHODS[2]):
                fx = C3.make_x(ctx.model(ref), m, ctx.lam)
                R = ctx.S[ref][fi]
                Ssyn = R.copy()
                for i, (a, b) in enumerate(SL.PAIRS):
                    Ssyn[:, a, b] += pred[i]
                    if a != b:
                        Ssyn[:, b, a] += pred[i]
                xp = fx(Ssyn, R)
                xo = fx(ctx.S[stem][fi], R)
                row[f"LR pred {SH[m]}"] = RL.contrasts(xp)["LR"]
                row[f"LR obs {SH[m]}"] = RL.contrasts(xo)["LR"]
            rows.append(row)
    # size of the model error vs the LeftOnly signal (whitened, primary model, H7)
    M = ctx.model(H7)["dS"]
    R = ctx.S[H7]
    pM = ctx.kappa * SL.predict(ctx.P, SL.delta_map("Mild_lobe", ctx.fh), ones)
    eM = np.linalg.norm(M.data(dS=pM - SL.recip(ctx.S["Mild_lobe"] - R)[:, fi]))
    sL = np.linalg.norm(M.data(dS=SL.recip(ctx.S[LEFT] - R)[:, fi]))
    aL = np.linalg.norm(M.data(dS=(SL.recip(ctx.S[LEFT] - R)[:, fi] - SL.recip(ctx.S[LEFT] - R)[:, fi][PM]) / 2))
    eM_anti = np.linalg.norm(M.data(dS=((pM - SL.recip(ctx.S["Mild_lobe"] - R)[:, fi])
                                        - (pM - SL.recip(ctx.S["Mild_lobe"] - R)[:, fi])[PM]) / 2))
    return rows, dict(mild_model_error=float(eM), leftonly_signal=float(sL), leftonly_antisym=float(aL),
                      mild_model_error_antisym=float(eM_anti))


def b7(ctx):
    """Fit-frequency dependence: subsets of the field frequencies and linearly interpolated kernels."""
    fh, K6, kappa = ctx.fh, ctx.K6, ctx.kappa
    fgrid = ctx.f

    def kern_at(fq):
        if np.any(np.isclose(fh, fq)):
            j = int(np.argmin(np.abs(fh - fq)))
            return K6[:, j], kappa[j]
        j = int(np.searchsorted(fh, fq)) - 1
        t = (fq - fh[j]) / (fh[j + 1] - fh[j])
        return (1 - t) * K6[:, j] + t * K6[:, j + 1], (1 - t) * kappa[j] + t * kappa[j + 1]
    sets = {"3.4/3.6/3.8 (frozen)": [3.4, 3.6, 3.8], "3.4": [3.4], "3.6": [3.6], "3.8": [3.8],
            "3.4/3.6": [3.4, 3.6], "3.4/3.8": [3.4, 3.8], "3.6/3.8": [3.6, 3.8],
            "3.5/3.7 (interp.)": [3.5, 3.7], "3.45/3.55/3.65/3.75 (interp.)": [3.45, 3.55, 3.65, 3.75],
            "3.4–3.8 step 0.1 (3.5, 3.7 interp.)": [3.4, 3.5, 3.6, 3.7, 3.8]}
    rows = []
    for sname, fl in sets.items():
        fq = np.array(fl) * 1e9
        KK, kk = zip(*[kern_at(q) for q in fq])
        Kf = np.stack(KK, 1)
        kf = np.array(kk)
        fif = np.array([int(np.argmin(np.abs(fgrid - q))) for q in fq])
        for rname, ref in REFS.items():
            R = ctx.S[ref]
            M = LA.models(Kf, fq, fif, kf, R, LA.KEEP_ALL)
            sig = SL.pair_sigma_f(R, PROFILES["typical"])[:, fif]
            M["wlog"] = LR.WhitenedLog(Kf, fq, kf, sig, LA.KEEP_ALL, R[fif])
            for m in METH:
                fx = C3.make_x(M, m, ctx.lam)
                x = fx(ctx.S[LEFT][fif], R[fif])
                xm = fx(mir(ctx.S[LEFT])[fif], R[fif])
                row = dict(frequencies=sname, reference=rname, method=SH[m], S2=x[7], S3=x[8], S5=x[10], S6=x[11],
                           LR=RL.contrasts(x)["LR"], LR_anti=(RL.contrasts(x)["LR"] - RL.contrasts(xm)["LR"]) / 2)
                if m in RL.METHODS:
                    c = RL.apply_rules(x, ctx.fz["rules"][m])
                    row.update(side=c["side"], S3_called=bool(c["affected"][2]), S2_called=bool(c["affected"][1]))
                else:
                    row.update(side="n/a", S3_called="n/a", S2_called="n/a")
                rows.append(row)
    # validation of kernel interpolation: predict the 3.6 GHz kernel from 3.4 and 3.8 GHz
    Ki = 0.5 * (K6[:, 0] + K6[:, 2])
    ki = 0.5 * (kappa[0] + kappa[2])
    val = dict(kernel_rel_err_mid=float(np.linalg.norm(Ki - K6[:, 1]) / np.linalg.norm(K6[:, 1])),
               kernel_phase_rot_deg_median=float(np.median(np.degrees(np.abs(np.angle(K6[:, 1] / K6[:, 0]))))))
    R = ctx.S[H7]
    fi6 = np.array([ctx.fi[1]])
    for lab_, Kf, kf in (("true", K6[:, 1:2], kappa[1:2]), ("interp", Ki[:, None], np.array([ki]))):
        M = LA.models(Kf, fh[1:2], fi6, kf, R, LA.KEEP_ALL)
        for m in (RL.METHODS[0], RL.METHODS[2]):
            x = C3.make_x(M, m, ctx.lam)(ctx.S[LEFT][fi6], R[fi6])
            val[f"LR_3.6_{lab_}_{SH[m]}"] = RL.contrasts(x)["LR"]
    # data: phase / amplitude left-right asymmetry of the mirror pairs across the band (no kernels involved)
    band = []
    rho = SL.recip(ctx.S[LEFT]) / SL.recip(ctx.S[H7])
    left_pairs = [i for i in range(len(SL.PAIRS)) if PM[i] != i and
                  any(t in (1, 2) for t in SL.PAIRS[i]) and not any(t in (4, 5) for t in SL.PAIRS[i])]
    for fq in np.arange(3.30, 3.901, 0.05):
        k = int(np.argmin(np.abs(fgrid - fq * 1e9)))
        row = dict(f_GHz=round(fq, 2))
        for i in left_pairs:
            a, b = SL.PAIRS[i]
            row[f"{plabel(a, b)} − {plabel(*SL.PAIRS[PM[i]])} (deg)"] = float(
                np.degrees(np.angle(rho[i, k])) - np.degrees(np.angle(rho[PM[i], k])))
        band.append(row)
    return rows, val, band


def b8(ctx):
    """Re-derive kappa, lambda and the calling rules on lobe_A with the frozen recipe (diagnostic only)."""
    S, f, fh, fi, P = ctx.S, ctx.f, ctx.fh, ctx.fi, ctx.P
    prof = PROFILES["typical"]
    H = S[H6]
    stages = ("Mild_lobe", "Moderate_lobe", "Severe_lobe")
    obs = {d: SL.recip(S[d] - H)[:, fi] for d in stages}
    sig = SL.pair_sigma_f(H, prof)[:, fi]
    p1 = SL.predict(P, SL.delta_map("Mild_lobe", fh), np.ones(len(fh)))
    w = 1 / sig ** 2
    kappa = np.sum(w * np.conj(p1) * obs["Mild_lobe"], 0) / np.sum(w * np.abs(p1) ** 2, 0)
    M = RL.models({"Healthy_sliced": H}, fh, fi, P, kappa, prof)
    lams = np.logspace(-4, 3, 71)
    lam = {"dS": M["dS"].gcv_lambda(M["dS"].data(dS=obs["Mild_lobe"]), lams),
           "log": M["log"].gcv_lambda(M["log"].data(S_stage=S["Mild_lobe"][fi], S_ref=H[fi]), lams)}

    def fit(Mx, m, a, b):
        lm = lam["dS"] if m.endswith("dS") else lam["log"]
        return RL.invert(Mx, m, lm, S_stage_fi=a, S_ref_fi=b, dS_fi=SL.recip(a - b))
    fits = {m: {d: fit(M, m, S[d][fi], H[fi]) for d in stages} for m in RL.METHODS}
    nl = SL.nulls(H, {d: S[d] for d in stages}, f, fi, prof)
    rules = {}
    for m in RL.METHODS:
        allx = np.concatenate([np.array([fit(M, m, (H + dn)[fi], H[fi]) for dn in lst]) for lst in nl.values()])
        t_null = float(np.quantile(np.max(allx[:, 6:12], 1), 0.95))
        cn = np.array([list(RL.contrasts(x).values()) for x in allx])
        xm = fits[m]["Mild_lobe"][6:12]
        aff = np.array(SL.DESIGNS["Mild_lobe"][0]) > 0
        lo, hi = float(xm[~aff].max()), float(xm[aff].min())
        t_mild = 0.5 * (lo + hi) if hi > lo else float("nan")
        lr_sym = max(abs(RL.contrasts(fits[m][d])["LR"]) for d in stages)
        rules[m] = dict(T_null=t_null, T_mild=t_mild, T_abs=float(np.nanmax([t_null, t_mild])),
                        T_LR=float(max(np.quantile(np.abs(cn[:, 0]), 0.95), lr_sym)),
                        T_FB=float(max(np.quantile(np.abs(cn[:, 1]), 0.95), abs(RL.contrasts(fits[m]["Mild_lobe"])["FB"]))))
    rows = []
    cases = [("LeftOnly", LEFT, H6), ("LeftOnly", LEFT, H7), ("MCI", MCI, H6), ("MCI", MCI, H7),
             ("Mild (B)", "Mild_lobe_new", H7), ("Moderate (B)", "Moderate_lobe_c3", H7), ("Severe (B)", "Severe_lobe_c3", H7)]
    for lab, st, ref in cases:
        Ma = RL.models({"Healthy_sliced": S[ref]}, fh, fi, P, kappa, prof)
        Mf = ctx.model(ref)
        for m in RL.METHODS:
            xa = fit(Ma, m, S[st][fi], S[ref][fi])
            lmf = ctx.lam["dS"] if m.endswith("dS") else ctx.lam["log"]
            xf = RL.invert(Mf, m, lmf, S_stage_fi=S[st][fi], S_ref_fi=S[ref][fi], dS_fi=SL.recip(S[st] - S[ref])[:, fi])
            ca, cf = RL.apply_rules(xa, rules[m]), RL.apply_rules(xf, ctx.fz["rules"][m])

            def s(c):
                return (" ".join(f"S{k + 1}" for k in range(6) if c["affected"][k]) or "none") + f" | {c['side']} | {c['frontback']}"
            rows.append(dict(design=lab, reference="H6" if ref == H6 else "H7", method=m, frozen=s(cf), lobe_A_rules=s(ca),
                             flip=s(cf) != s(ca), S3_frozen=xf[8], S3_lobeA=xa[8], LR_frozen=cf["LR"], LR_lobeA=ca["LR"]))
    return rows, dict(kappa_abs=np.abs(kappa).tolist(), kappa_frozen_abs=np.abs(ctx.kappa).tolist(),
                      lam=lam, lam_frozen=ctx.lam, rules=rules, rules_frozen=ctx.fz["rules"])


def b9(ctx):
    """Which paths carry the LR estimate: exact linear decomposition into per-path amplitude / phase terms."""
    main = pd.read_csv(ROOT / "results" / "05_lobe" / "tests" / "1_leftonly_paths.csv", encoding="utf-8")
    main.columns = [c.replace("±", "+-") for c in main.columns]
    fi = ctx.fi
    F = len(fi)
    g = np.zeros(12)
    g[[7, 8]], g[[10, 11]] = 0.5, -0.5
    lab = [plabel(a, b) for a, b in SL.PAIRS]
    kind = [LA.CLASSES[SL.ring_k(a, b)] for a, b in SL.PAIRS]
    out, tops = {}, []
    for rname, ref in REFS.items():
        R, L = ctx.S[ref], ctx.S[LEFT]
        rho = SL.recip(L)[:, fi] / SL.recip(R)[:, fi]
        y = np.log(rho)
        y = y - 2j * np.pi * np.round(y.imag / (2 * np.pi))
        Mall = ctx.model(ref)
        for m in METH:
            if m == LR.WNAME:
                mdl, lam = Mall["wlog"], ctx.lam["log"]
            else:
                mdl, lam = Mall["dS" if m.endswith("dS") else "log"], ctx.lam["dS" if m.endswith("dS") else "log"]
            A = mdl.J.T @ mdl.J + lam ** 2 * np.eye(12)
            wv = mdl.J @ np.linalg.solve(A, g)                            # LR = wv . d
            n = len(SL.PAIRS) * F
            wre, wim = wv[:n].reshape(len(SL.PAIRS), F), wv[n:].reshape(len(SL.PAIRS), F)
            if m.endswith("dS"):
                Sr = SL.recip(R)[:, fi]
                W = mdl.w
                # dS = Sr (e^y - 1); amplitude part Sr (|rho| - 1), phase part the rest
                dS = SL.recip(L - R)[:, fi]
                d_amp = Sr * (np.abs(rho) - 1)
                d_ph = dS - d_amp
                c_amp = (wre * (W * d_amp).real + wim * (W * d_amp).imag).sum(1)
                c_ph = (wre * (W * d_ph).real + wim * (W * d_ph).imag).sum(1)
                eff_w = np.sqrt(np.sum((wre * W * np.abs(Sr)) ** 2 + (wim * W * np.abs(Sr)) ** 2, 1))
            else:
                ure = np.zeros((len(SL.PAIRS), F))
                uim = np.zeros((len(SL.PAIRS), F))
                for k in range(F):
                    Pk = mdl.Pf[k] if m == LR.WNAME else mdl.Pg
                    ure[:, k] = mdl.w[:, k] * (Pk.T @ wre[:, k])
                    uim[:, k] = mdl.w[:, k] * (Pk.T @ wim[:, k])
                c_amp = (ure * y.real).sum(1)
                c_ph = (uim * y.imag).sum(1)
                eff_w = np.sqrt(np.sum(ure ** 2 + uim ** 2, 1))
            total = c_amp + c_ph
            fx = C3.make_x(Mall, m, ctx.lam)
            lr_true = RL.contrasts(fx(L[fi], R[fi]))["LR"]
            out[(rname, m)] = dict(sum_paths=float(total.sum()), LR=float(lr_true), amp=float(c_amp.sum()),
                                   phase=float(c_ph.sum()))
            order = np.argsort(-np.abs(total))[:5]
            for i in order:
                a, b = SL.PAIRS[i]
                bp = 10 * np.log10(np.mean(np.abs(SL.recip(L)[i]) ** 2) / np.mean(np.abs(SL.recip(R)[i]) ** 2))
                yd = [np.degrees(np.angle(SL.recip(ctx.S[p])[i, fi] / SL.recip(ctx.S[q])[i, fi]))
                      for p, q in C3.ONE_PASS.values()]
                ya = [20 * np.log10(np.abs(SL.recip(ctx.S[p])[i, fi] / SL.recip(ctx.S[q])[i, fi])) for p, q in C3.ONE_PASS.values()]
                mm = main[(main["path"] == lab[i]) & (main["reference"].str.startswith(ref + " ("))]
                mrow = mm.iloc[0] if len(mm) else None
                tops.append(dict(reference=rname, method=SH[m], path=lab[i], type=kind[i], mirror=lab[PM[i]],
                                 contribution=float(total[i]), from_amplitude=float(c_amp[i]), from_phase=float(c_ph[i]),
                                 mirror_contribution=float(total[PM[i]]), weight=float(eff_w[i]),
                                 amp_change_dB_fit=", ".join(f"{20 * np.log10(abs(rho[i, k])):+.2f}" for k in range(F)),
                                 phase_change_deg_fit=", ".join(f"{np.degrees(np.angle(rho[i, k])):+.1f}" for k in range(F)),
                                 one_pass_max_amp_dB_fit=float(np.max(np.abs(ya))),
                                 one_pass_max_phase_deg_fit=float(np.max(np.abs(yd))),
                                 band_power_dB=float(bp),
                                 main_observed_dB=float(mrow["observed dB"]) if mrow is not None else np.nan,
                                 main_over_yardstick=float(mrow["/ yardstick"]) if mrow is not None else np.nan,
                                 main_over_floor=float(mrow["/ symmetry floor"]) if mrow is not None else np.nan,
                                 main_over_spread_05=float(mrow["/ spread +-0.5 dB"]) if mrow is not None else np.nan))
    anti = []
    left_pairs = [i for i in range(len(SL.PAIRS)) if PM[i] != i and
                  any(t in (1, 2) for t in SL.PAIRS[i]) and not any(t in (4, 5) for t in SL.PAIRS[i])]
    for rname, ref in REFS.items():
        rho = SL.recip(ctx.S[LEFT])[:, fi] / SL.recip(ctx.S[ref])[:, fi]
        for i in left_pairs:
            j = PM[i]
            ph = np.degrees(np.angle(rho[i]) - np.angle(rho[j]))
            am = 20 * np.log10(np.abs(rho[i]) / np.abs(rho[j]))
            op_ph = max(np.max(np.abs(np.degrees(np.angle(SL.recip(ctx.S[p])[i, fi] / SL.recip(ctx.S[q])[i, fi])
                                                 - np.angle(SL.recip(ctx.S[p])[j, fi] / SL.recip(ctx.S[q])[j, fi]))))
                        for p, q in C3.ONE_PASS.values())
            fls = {d: float(np.max(np.abs(np.degrees(np.angle(SL.recip(ctx.S[d])[i, fi] / SL.recip(ctx.S[d])[j, fi]))))
                            * np.sqrt(2))
                   for d in ("Healthy_sliced_new", "Mild_lobe", "Moderate_lobe", "Severe_lobe", "MCI_lobe_c3")}
            fl_ph = max(fls.values())
            fl_p6 = max(fls["Healthy_sliced_new"], fls["MCI_lobe_c3"])
            anti.append(dict(reference=rname, pair=f"{lab[i]} vs {lab[j]}",
                             anti_phase_deg_fit=", ".join(f"{v:+.1f}" for v in ph),
                             anti_amp_dB_fit=", ".join(f"{v:+.2f}" for v in am),
                             one_pass_anti_phase_max_deg=float(op_ph), floor_anti_phase_max_deg=float(fl_ph),
                             floor_set_by=max(fls, key=fls.get), floor_p6_deg=float(fl_p6),
                             ratio_to_max_ruler=float(np.max(np.abs(ph)) / max(op_ph, fl_ph)),
                             ratio_with_p6_floor=float(np.max(np.abs(ph)) / max(op_ph, fl_p6))))
    return {f"{k[0]}|{k[1]}": v for k, v in out.items()}, tops, anti


# ----------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    a = ap.parse_args()
    ctx = C3.Ctx(a.n)
    res = dict(code=git_hash(ROOT), frozen_code=ctx.fz["code"], n_draws=a.n)
    res["b1"] = b1(ctx)
    res["b1_floors"] = ctx.lr_floors
    res["b2a"] = b2a(ctx)
    Ms_cache = {}

    def frozen_models(ref):
        return ctx.model(ref)

    def symmetric_models(ref):
        if ref not in Ms_cache:
            Ms_cache[ref], res["kernel_asym"] = sym_models(ctx, ref)
        return Ms_cache[ref]
    res["b3"] = mirror_rows(ctx, frozen_models, "frozen (HFSS field exports)")
    res["b2b"] = mirror_rows(ctx, symmetric_models, "mirror-symmetrised")
    res["b3_rulers"] = b3_rulers(ctx)
    res["b4"], res["b4_mech"] = b4(ctx)
    res["b5"], res["b5_meta"] = b5(ctx, res["b1"])
    res["b6"], res["b6_size"] = b6(ctx)
    res["b7"], res["b7_val"], res["b7_band"] = b7(ctx)
    res["b8"], res["b8_meta"] = b8(ctx)
    res["b9_sum"], res["b9_top"], res["b9_anti"] = b9(ctx)
    res["field_files"] = sorted(x.name for x in (ROOT / "data" / "fields").glob("E_Normal_T1_*.fld"))
    (RL.CACHE / "lobe_review.pkl").write_bytes(pickle.dumps(res))
    (OUT / "lobe_review.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item")
                                                     else (o.tolist() if hasattr(o, "tolist") else str(o))),
                                          encoding="utf-8")
    write_md(res)
    print("done")


if __name__ == "__main__":
    main()
