"""Lobe-sector phantom study (Prompt 08) - one command:

    python imaging/run_lobe.py [--reuse] [--blind] [--no-csv]

Stage 1 (default): kernels, CRLB, sector inversions, nulls, radar, and the PRE-REGISTERED
predictions for the blind designs -> results/imaging/lobe_report.md, lobe_predictions.md,
results/imaging/figures/lobe_*.png. The frozen pipeline state (kappa, lambdas, thresholds) is
written to results/imaging/lobe_frozen.json.
Stage 2 (--blind, only after lobe_predictions.md is committed): loads the frozen state, runs the
unchanged pipeline on LeftOnly_test and MCI_lobe, scores them against the predictions, and
appends the outcome to lobe_report.md.
Cache: results/imaging/cache/lobe_v1-masked/ (not committed).
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402

from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, PROFILES, git_hash, ROOT  # noqa: E402

CACHE = OUT / "cache" / "lobe_v1-masked"
FROZEN = OUT / "lobe_frozen.json"
METHODS = ("tikhonov dS", "bounded dS", "tikhonov log (gain-inv.)", "bounded log (gain-inv.)")


def cached(name, fn, reuse):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{name}.pkl"
    if reuse and p.exists():
        return pickle.loads(p.read_bytes())
    r = fn()
    p.write_bytes(pickle.dumps(r))
    return r


def build(reuse=False, log=print):
    S = {}
    f = None
    for d in SL.AVAILABLE:
        S[d], f_ = SL.load_design(d, f)
        f = f_ if f is None else f
    fh, grids = SL.load_hfss_fields()
    fi = np.array([int(np.argmin(np.abs(f - q))) for q in fh])
    P = cached("born_table", lambda: SL.born_table(grids, fh, log=log), reuse)
    return S, f, fh, fi, P


def models(S, fh, fi, P, kappa, prof):
    H = S["Healthy_sliced"]
    sig = SL.pair_sigma_f(H, prof)[:, fi]
    masks = SL.region_masks()                                           # 6 sectors + core
    K = SL.region_kernels(P, masks)
    K6 = K[..., :6]                                                     # inversion unknowns: sectors only
    out = {"masks": masks, "K": K, "sig": sig,
           "dS7": SL.RegionModel(K, fh, kappa, sig, kind="dS"),
           "log7": SL.RegionModel(K, fh, kappa, sig, S_ref=H[fi], kind="log"),
           "dS": SL.RegionModel(K6, fh, kappa, sig, kind="dS"),
           "log": SL.RegionModel(K6, fh, kappa, sig, S_ref=H[fi], kind="log")}
    ms = SL.region_masks(split=True)
    ms = {k: v for k, v in ms.items() if k != "core"}
    Ks = SL.region_kernels(P, ms)
    out.update(masks_split=ms, K_split=Ks,
               dS_split=SL.RegionModel(Ks, fh, kappa, sig, kind="dS"),
               log_split=SL.RegionModel(Ks, fh, kappa, sig, S_ref=H[fi], kind="log"))
    return out


def contrasts(x):
    """Left-right and front-back contrasts of the recovered sector conductivity change d eps''."""
    pp = np.asarray(x)[6:12]
    return {"LR": float(np.mean(pp[[1, 2]]) - np.mean(pp[[4, 5]])), "FB": float(pp[0] - pp[3])}


def apply_rules(x, rule):
    """Frozen calls: R1 sector affected if d eps'' > T_abs = max(null 95 % family-wise, Mild-tuned);
    R2 side = left / right if |LR| > T_LR (null 95 % and the largest |LR| of the mirror-symmetric
    designs); R3 front / back if |FB| > T_FB (null 95 % and |FB| of Mild, whose S1 and S4 are both healthy)."""
    pp = np.asarray(x)[6:12]
    c = contrasts(x)
    side = "left" if c["LR"] > rule["T_LR"] else ("right" if c["LR"] < -rule["T_LR"] else "none")
    fbv = "front" if c["FB"] > rule["T_FB"] else ("back" if c["FB"] < -rule["T_FB"] else "none")
    return dict(affected=(pp > rule["T_abs"]).tolist(), LR=c["LR"], FB=c["FB"], side=side, frontback=fbv)


def invert(M, method, lam, S_stage_fi=None, S_ref_fi=None, dS_fi=None):
    """method in METHODS; dS_fi = (21, F) reciprocal-pair difference at the fit frequencies."""
    if method.endswith("dS"):
        d = M["dS"].data(dS=dS_fi)
        mdl = M["dS"]
    else:
        d = M["log"].data(S_stage=S_stage_fi, S_ref=S_ref_fi)
        mdl = M["log"]
    if method.startswith("tikhonov"):
        return mdl.tikhonov(d, lam)
    return mdl.bounded(d, lam)


def run_stage1(reuse=False, log=print):
    prof = PROFILES["typical"]
    S, f, fh, fi, P = build(reuse, log)
    H = S["Healthy_sliced"]
    stages = ("Mild_lobe", "Moderate_lobe", "Severe_lobe")
    obs = {d: SL.recip(S[d] - H)[:, fi] for d in stages}               # (21, F)
    # ---- kappa(f) on Mild only, frozen
    sig = SL.pair_sigma_f(H, prof)[:, fi]
    pred1 = {d: SL.predict(P, SL.delta_map(d, fh), np.ones(len(fh))) for d in SL.DESIGNS if d != "Healthy_sliced"}
    w = 1 / sig ** 2
    kappa = np.sum(w * np.conj(pred1["Mild_lobe"]) * obs["Mild_lobe"], 0) / np.sum(w * np.abs(pred1["Mild_lobe"]) ** 2, 0)
    lin = {d: dict(born_abs_over_hfss=float(np.linalg.norm(pred1[d]) / np.linalg.norm(obs[d])),
                   rel_err_kappa=float(np.linalg.norm(kappa * pred1[d] - obs[d]) / np.linalg.norm(obs[d])),
                   corr=float(np.abs(np.vdot(kappa * pred1[d], obs[d])) / np.linalg.norm(pred1[d] * kappa)
                              / np.linalg.norm(obs[d])))
           for d in stages}
    M = models(S, fh, fi, P, kappa, prof)
    res = {"f": fh, "kappa": kappa, "lin": lin, "code": git_hash(ROOT)}

    # ---- 3.1 kernels
    K36 = M["K"][:, int(np.argmin(np.abs(fh - 3.6e9)))]
    res["kernel_abs_36"] = np.abs(K36) / np.abs(K36).max()
    names = list(M["masks"])
    res["region_names"] = names
    for key in ("dS7", "log7", "dS", "log", "dS_split", "log_split"):
        s = np.linalg.svd(M[key].J, compute_uv=False)
        res[f"sv_{key}"] = s
    Jr = M["dS7"].J[:, :len(names)]                                       # d eps_r columns, whitened
    nJ = Jr / np.linalg.norm(Jr, axis=0)
    res["col_cos"] = nJ.T @ nJ
    Js = M["dS_split"].J[:, :len(M["masks_split"])]
    nS = Js / np.linalg.norm(Js, axis=0)
    res["col_cos_split"] = nS.T @ nS
    res["split_names"] = list(M["masks_split"])

    # ---- 3.2 truth and CRLB
    truth = {d: SL.truth_regions(d, fh, P, M["masks"]) for d in SL.DESIGNS if d != "Healthy_sliced"}
    truth_split = {d: SL.truth_regions(d, fh, P, M["masks_split"]) for d in stages}
    res["truth"], res["truth_split"] = truth, truth_split
    res["crlb7"] = {"dS (no gain error)": M["dS7"].crlb(),
                    "dS + 0.5 dB port gains": M["dS7"].crlb(0.5, S_ref=H[fi]),
                    "log, gain-invariant": M["log7"].crlb()}
    res["crlb"] = {"dS (no gain error)": M["dS"].crlb(),
                   "dS + 0.5 dB port gains": M["dS"].crlb(0.5, S_ref=H[fi]),
                   "log, gain-invariant": M["log"].crlb()}
    res["crlb_split"] = {"dS (no gain error)": M["dS_split"].crlb(),
                         "log, gain-invariant": M["log_split"].crlb()}

    # ---- 3.3 frozen lambdas (GCV on Mild) and inversions
    lams = np.logspace(-4, 3, 71)
    lam = {"dS": M["dS"].gcv_lambda(M["dS"].data(dS=obs["Mild_lobe"]), lams),
           "log": M["log"].gcv_lambda(M["log"].data(S_stage=S["Mild_lobe"][fi], S_ref=H[fi]), lams)}
    res["lambda"] = lam

    def lam_of(m):
        return lam["dS"] if m.endswith("dS") else lam["log"]

    def fit(m, S_stage_fi, S_ref_fi):
        return invert(M, m, lam_of(m), S_stage_fi=S_stage_fi, S_ref_fi=S_ref_fi,
                      dS_fi=SL.recip(S_stage_fi - S_ref_fi))

    res["fits"] = {m: {d: fit(m, S[d][fi], H[fi]) for d in stages} for m in METHODS}

    # ---- 3.5 nulls and the frozen calling rules
    nl = SL.nulls(H, {d: S[d] for d in stages}, f, fi, prof)
    null_x = {m: {} for m in METHODS}
    for src, lst in nl.items():
        for m in METHODS:
            null_x[m][src] = np.array([fit(m, (H + dn)[fi], H[fi]) for dn in lst])
    res["null_x"] = null_x
    rules = {}
    for m in METHODS:
        allx = np.concatenate(list(null_x[m].values()))
        pp = allx[:, 6:12]
        t_null = float(np.quantile(np.max(pp, 1), 0.95))                 # family-wise 5 %, one-sided
        cn = np.array([list(contrasts(x).values()) for x in allx])
        xm = res["fits"][m]["Mild_lobe"][6:12]
        aff_m = np.array(SL.DESIGNS["Mild_lobe"][0]) > 0
        lo, hi = float(xm[~aff_m].max()), float(xm[aff_m].min())
        t_mild = 0.5 * (lo + hi) if hi > lo else float("nan")
        lr_sym = max(abs(contrasts(res["fits"][m][d])["LR"]) for d in stages)   # all mirror-symmetric
        rules[m] = dict(T_null=t_null, T_mild=t_mild,
                        T_abs=float(np.nanmax([t_null, t_mild])),
                        T_LR=float(max(np.quantile(np.abs(cn[:, 0]), 0.95), lr_sym)),
                        T_LR_null=float(np.quantile(np.abs(cn[:, 0]), 0.95)), LR_sym_max=float(lr_sym),
                        T_FB=float(max(np.quantile(np.abs(cn[:, 1]), 0.95),
                                       abs(contrasts(res["fits"][m]["Mild_lobe"])["FB"]))),
                        T_FB_null=float(np.quantile(np.abs(cn[:, 1]), 0.95)))
    res["rules"] = rules
    res["threshold"] = {m: rules[m]["T_abs"] for m in METHODS}

    # ---- scores
    sc = []
    for m in METHODS:
        for d in stages:
            x = res["fits"][m][d]
            e = np.array(SL.DESIGNS[d][0], float)
            aff = e > 0
            corr_e, topk = SL.pattern_scores(x[6:12], e, aff)
            tr = truth[d]["sens"][7:13]                                  # true d eps'' of the 6 sectors
            corr_t = float(np.corrcoef(x[6:12], tr)[0, 1])
            corr_r = float(np.corrcoef(x[:6], truth[d]["sens"][:6])[0, 1])
            c = apply_rules(x, rules[m])
            calls = np.array(c["affected"])
            null_only = x[6:12] > rules[m]["T_null"]
            sc.append(dict(method=m, stage=d, corr_e=corr_e, corr_truth=corr_t, topk=topk,
                           called=" ".join(f"S{k + 1}" for k in np.flatnonzero(calls)) or "none",
                           called_null_only=" ".join(f"S{k + 1}" for k in np.flatnonzero(null_only)) or "none",
                           true_set=" ".join(f"S{k + 1}" for k in np.flatnonzero(aff)),
                           correct_calls=int(np.sum(calls == aff)), LR=c["LR"], side=c["side"],
                           FB=c["FB"], frontback=c["frontback"], corr_eps_r_truth=corr_r))
    res["scores"] = sc
    # front/back for Moderate (S1 affected, S4 not)
    fb = []
    for m in METHODS:
        x = res["fits"][m]["Moderate_lobe"]
        cr = res["crlb"]["log, gain-invariant" if "log" in m else "dS (no gain error)"]
        c = apply_rules(x, rules[m])
        fb.append(dict(method=m, S1=float(x[6]), S4=float(x[9]), crlb_S1=float(cr[6]), crlb_S4=float(cr[9]),
                       FB=c["FB"], T_FB=rules[m]["T_FB"], verdict=c["frontback"],
                       S1_called=bool(c["affected"][0]), S4_called=bool(c["affected"][3])))
    res["front_back"] = fb

    # ---- 3.4 radar
    dS_full = {d: S[d] - H for d in stages}
    rad = SL.radar(f, dS_full, H, None)
    stats = []
    for d in stages:
        for m in ("DAS", "DMAS"):
            st = SL.angular_stats(rad[d][m], rad["pts"])
            tc = SL.true_centroid(d)
            stats.append(dict(stage=d, method=m, **st, true_dir_deg=tc["dir_deg"], true_resultant=tc["resultant"]))
    res["radar"], res["radar_stats"] = rad, stats

    # ---- blind predictions (frozen pipeline on Born-simulated data + noise)
    from adstage.noise.model import realise
    rng = np.random.default_rng(9900)
    pred = {}
    for d in SL.BLIND:
        dS_syn = (kappa * pred1[d])                                      # (21, F) at fh
        Ssyn = H[fi].copy()
        for i, (a, b) in enumerate(SL.PAIRS):
            Ssyn[:, a, b] += dS_syn[i]
            if a != b:
                Ssyn[:, b, a] += dS_syn[i]
        draws = realise(fh, Ssyn, prof, 40, rng)
        draws0 = realise(fh, H[fi], prof, 40, rng)
        pred[d] = {}
        for m in METHODS:
            xs = np.array([invert(M, m, lam_of(m), S_stage_fi=a, S_ref_fi=b, dS_fi=SL.recip(a - b))
                           for a, b in zip(draws, draws0)])
            clean = invert(M, m, lam_of(m), S_stage_fi=Ssyn, S_ref_fi=H[fi], dS_fi=dS_syn)
            cs = [apply_rules(x, rules[m]) for x in xs]
            pred[d][m] = dict(clean=clean, clean_calls=apply_rules(clean, rules[m]), mean=xs.mean(0), sd=xs.std(0),
                              p_called=np.mean([c_["affected"] for c_ in cs], 0),
                              p_left=float(np.mean([c_["side"] == "left" for c_ in cs])),
                              p_right=float(np.mean([c_["side"] == "right" for c_ in cs])),
                              LR_mean=float(np.mean([c_["LR"] for c_ in cs])),
                              LR_sd=float(np.std([c_["LR"] for c_ in cs])),
                              p_any=float(np.mean([any(c_["affected"]) for c_ in cs])),
                              p_fb=float(np.mean([c_["frontback"] != "none" for c_ in cs])))
    res["blind_pred"] = pred
    res["frozen"] = dict(code=res["code"], kappa_re=kappa.real.tolist(), kappa_im=kappa.imag.tolist(),
                         lambda_dS=lam["dS"], lambda_log=lam["log"], rules=rules,
                         f_GHz=(fh / 1e9).tolist(), regions=names)
    return res, M


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--blind", action="store_true")
    a = ap.parse_args()
    from imaging import report_lobe
    if not a.blind:
        res, M = run_stage1(a.reuse)
        (CACHE / "stage1.pkl").write_bytes(pickle.dumps(res))
        FROZEN.write_text(json.dumps(res["frozen"], indent=1), encoding="utf-8")
        report_lobe.write_stage1(res)
        print("wrote", OUT / "lobe_report.md", OUT / "lobe_predictions.md", FROZEN)
    else:
        report_lobe.run_blind()


if __name__ == "__main__":
    main()
