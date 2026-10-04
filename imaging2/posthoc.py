"""POST HOC analyses, computed after the Test_B truth was revealed (user message of 2026-10-04).
Nothing here changes a committed estimate, protocol, threshold, prediction or verdict; every number written by
this module is post hoc. Outputs: results/imaging2/posthoc/ (posthoc.json, posthoc.md) and two *_pres figures.

    python -m imaging2.posthoc all
"""
from __future__ import annotations

import argparse
import copy
import json

import numpy as np

from . import figures as FG
from . import invert as IV
from . import lodo as LO
from . import noise as NO
from . import render as RE
from .data import (CACHE, DESIGNS, FIG, H6, H7, HEALTHY_LOBE, MIRROR, N, OUT, PATH_TYPE, SECTOR_SHORT, TYPE_NAMES,
                   Design, apply_group, freq, git_rev, load_external, lobe, paths_of)

OUT_PH = OUT / "posthoc"
SWEEPS, BURN, SEED = 600, 150, 0
FILES = {"H6": H6, "H7": H7,
         "rot07": "new_with_slices_Null_rot07.s6p", "rot19": "new_with_slices_Null_rot19.s6p",
         "LeftOnly": "new_with_slices_LeftOnly_test_c3.s6p", "RightOnly": "new_with_slices_RightOnly_test.s6p",
         "Test_B": "new_with_slices_Test_B.s6p", "MCI": "new_with_slices_MCI_lobe_c3.s6p",
         "Mild5": "new_with_slices_Mild_lobe.s6p", "Mild6": "new_with_slices_Mild_lobe_new.s6p",
         "Mod5": "new_with_slices_Moderate_lobe.s6p", "Mod6": "new_with_slices_Moderate_lobe_c3.s6p",
         "Sev5": "new_with_slices_Severe_lobe.s6p", "Sev6": "new_with_slices_Severe_lobe_c3.s6p"}
# convergence data as supplied by the user (HFSS tables); kind = role in imaging2
NEW = [("RightOnly", "replication", lobe([0, 0, 0, 0, 11.5, 7.5], "Mild", 17.5), 5, 0.019742, 789241),
       ("Test_B", "blind (scored)", lobe([0, 11.5, 0, 0, 7.5, 0], "Mild", 17.5), 6, 0.012597, 903758),
       ("rot07", "null (healthy rotated 7 deg)", copy.deepcopy(HEALTHY_LOBE), 6, 0.014650, 1045101),
       ("rot19", "null (healthy rotated 19 deg)", copy.deepcopy(HEALTHY_LOBE), 6, 0.014495, 939082)]
_S: dict = {}


def S(key):
    if key not in _S:
        _S[key] = load_external(FILES[key])[1]
    return _S[key]


def L(a, b):
    """complex log-ratio ln(S_a / S_b) per path (21, F)."""
    return np.log(paths_of(S(a)) / paths_of(S(b)))


def L_mirror(a, b):
    """ln(S_a / mirror(S_b)): b's paths relabelled by the x -> -x mirror."""
    return np.log(paths_of(S(a)) / apply_group(paths_of(S(b)), MIRROR))     # ratio first: no 2-pi phase wraps


def register():
    for key, role, tr, *_ in NEW:
        if not any(d.file == FILES[key] for d in DESIGNS):
            DESIGNS.append(Design(key, FILES[key], "p6", H6, tr, "new_with_slices_posthoc", key, "target"))


def truth_of_key(key):
    return next(t for k, _, t, *_ in NEW if k == key)


# ---------------------------------------------------------------- posterior variants
class PosteriorRingPhase(IV.Posterior):
    """POST HOC variant: the ring-mean phase of every path type is removed at every frequency (from the data and
    from every model contribution), i.e. a uniform phase offset of each path class cannot affect the fit. Amplitude
    is untouched. Routed through Posterior.project by setting gain_free."""

    def __init__(self, *a, **k):
        k["gain_free"] = True
        super().__init__(*a, **k)

    def project(self, R):
        R = np.asarray(R)
        im = R.imag.copy()
        for t in range(4):
            sel = PATH_TYPE == t
            im[..., sel, :] -= im[..., sel, :].mean(axis=-2, keepdims=True)
        return R.real + 1j * im


def posterior(fold, s_re=None, s_im=None, variant="standard"):
    s_re = fold["s_re"] if s_re is None else s_re
    s_im = fold["s_im"] if s_im is None else s_im
    args = (fold["sur"], s_re, s_im, fold["ell"], fold["f"], fold["cfg"][0])
    if variant == "ringphase":
        return PosteriorRingPhase(*args)
    return IV.Posterior(*args, gain_free=(variant == "gainfree"))


def summarize_run(post, Ld, tag=None):
    res = post.run(Ld, n_sweep=SWEEPS, burn=BURN, seed=SEED)
    Ps, marg = IV.sector_marginals(res)
    if tag:
        np.save(CACHE / f"marg_{tag}.npy", marg)
    sm = IV.summarize(Ps=Ps, marg=marg)
    sm.update(chi2_per_dof=float(res["_gof_raw"]), tau=float(res["_tau"]),
              calls=[int(s["P_affected"] > 0.5) for s in sm["sectors"]],
              stage_MAP=max(sm["P_stage"], key=sm["P_stage"].get))
    return sm


def short(sm):
    return dict(stage=sm["stage_MAP"], P_stage=round(sm["P_stage"][sm["stage_MAP"]], 3),
                P_stage_all={k: round(v, 3) for k, v in sm["P_stage"].items()},
                calls=sm["calls"], P_aff=[round(s["P_affected"], 3) for s in sm["sectors"]],
                e_med=[s["e_median"] for s in sm["sectors"]], e_int=[[s["e_q05"], s["e_q95"]] for s in sm["sectors"]],
                fit=round(sm["chi2_per_dof"], 3))


# ---------------------------------------------------------------- noise: solve-to-solve offsets of every twin pair
def twin_samples():
    return {"H7/H6 (7 vs 6 passes)": L("H7", "H6"),
            "rot07/H6 (6 vs 6, rotated mesh)": L("rot07", "H6"),
            "rot19/H6 (6 vs 6, rotated mesh)": L("rot19", "H6"),
            "Mild 5/6": L("Mild5", "Mild6"), "Moderate 5/6": L("Mod5", "Mod6"), "Severe 5/6": L("Sev5", "Sev6"),
            "RightOnly/mirror(LeftOnly) (5 vs 6)": L_mirror("RightOnly", "LeftOnly")}


EXCLUDE = {"Healthy_p7": ["H7/H6 (7 vs 6 passes)"], "Mild_p5": ["Mild 5/6"], "Mild_p6": ["Mild 5/6"],
           "Moderate_p5": ["Moderate 5/6"], "Moderate_p6": ["Moderate 5/6"], "Severe_p5": ["Severe 5/6"],
           "Severe_p6": ["Severe 5/6"], "LeftOnly_p6": ["RightOnly/mirror(LeftOnly) (5 vs 6)"],
           "RightOnly": ["RightOnly/mirror(LeftOnly) (5 vs 6)"], "MCI_p6": [], "Test_B": [],
           "rot07": ["rot07/H6 (6 vs 6, rotated mesh)"], "rot19": ["rot19/H6 (6 vs 6, rotated mesh)"]}


def augmented(fold, target):
    """fold noise (mesh ruler + model error) + variance of the twin offsets, the target's own twin excluded. Each
    twin difference is taken as one sample of an observation's solve-to-solve error (no 1/sqrt 2: conservative)."""
    smp = [v for k, v in twin_samples().items() if k not in EXCLUDE[target]]
    F = smp[0].shape[1]
    vr, vi = np.zeros((4, F)), np.zeros((4, F))
    for t in range(4):
        sel = PATH_TYPE == t
        vr[t] = np.mean([np.mean(x[sel].real ** 2, 0) for x in smp], 0)
        vi[t] = np.mean([np.mean(x[sel].imag ** 2, 0) for x in smp], 0)
    vr, vi = NO.smooth(vr)[PATH_TYPE], NO.smooth(vi)[PATH_TYPE]
    return np.sqrt(fold["s_re"] ** 2 + vr), np.sqrt(fold["s_im"] ** 2 + vi)


# ---------------------------------------------------------------- the analyses
def all_(only=None):
    OUT_PH.mkdir(parents=True, exist_ok=True)
    register()
    out = dict(code=git_rev(), label="POST HOC (after the Test_B truth)", new_files=[
        dict(design=k, file=FILES[k], role=r, passes=p, final_dS=d, elements=e) for k, r, _, p, d, e in NEW])
    folds = {g: LO.fit_fold(g) for g in ["__blind__", "LeftOnly", "Healthy", "Mild_lobe", "Moderate_lobe",
                                          "Severe_lobe", "MCI_lobe"]}
    full, lof = folds["__blind__"], folds["LeftOnly"]
    out["masking"] = {k: len(load_external(FILES[k])[2]) for k in ("rot07", "rot19", "RightOnly", "Test_B")}

    # A. nulls as targets (full training set; nulls never in training)
    A = {}
    for nk in ("rot07", "rot19"):
        for ref in ("H6", "H7"):
            for var in ("standard", "gainfree"):
                A[f"{nk} vs {ref} [{var}]"] = short(summarize_run(posterior(full, variant=var), L(nk, ref),
                                                                  tag=f"PH_{nk}_vs{ref}_{var}"))
    out["A_nulls_as_targets"] = A

    # B. each null as the healthy reference
    B = {}
    for tgt, fold in (("Test_B", full), ("LeftOnly", lof), ("RightOnly", lof)):
        for nk in ("rot07", "rot19"):
            for var in ("standard", "gainfree"):
                B[f"{tgt} vs {nk} [{var}]"] = short(summarize_run(posterior(fold, variant=var), L(tgt, nk)))
    out["B_nulls_as_references"] = B

    # C. pass gap: LeftOnly vs mirrored RightOnly against the three 5-vs-6 twins (and the other twins for context)
    out["C_pass_gap"] = pass_gap()

    # D. rulers rebuilt with the rotated nulls
    out["D_rulers"] = rulers(A)

    # E. augmented noise model: coverage before / after, and the P challenge
    out["E_noise"] = noise_and_coverage(folds)

    # F. ring-mean-phase variant
    out["F_ringphase"] = ringphase(folds)

    (OUT_PH / "posthoc.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT_PH / "posthoc.md").write_text(report(out), encoding="utf-8")
    return out


def _stats(D, sel_f):
    rows = {}
    for t in range(4):
        sel = PATH_TYPE == t
        X = D[sel][:, sel_f]
        rows[TYPE_NAMES[t]] = dict(rms_dB=float(np.sqrt(np.mean((X.real * 8.686) ** 2))),
                                   rms_deg=float(np.sqrt(np.mean(np.degrees(X.imag) ** 2))),
                                   mean_dB=float(8.686 * X.real.mean()), mean_deg=float(np.degrees(X.imag.mean())))
    return rows


def pass_gap():
    f = freq()
    bands = {"3.2-4.2 GHz": np.ones(len(f), bool), "3.30-3.65 GHz": (f >= 3.30e9) & (f <= 3.65e9)}
    pairs = {"RightOnly vs mirror(LeftOnly) (5 vs 6)": L_mirror("RightOnly", "LeftOnly"),
             "Mild 5 vs 6": L("Mild5", "Mild6"), "Moderate 5 vs 6": L("Mod5", "Mod6"), "Severe 5 vs 6": L("Sev5", "Sev6"),
             "Healthy 6 vs 7 (context)": L("H6", "H7"), "rot07 vs H6 (context, 6 vs 6)": L("rot07", "H6"),
             "rot19 vs H6 (context, 6 vs 6)": L("rot19", "H6")}
    out = {}
    for bn, sel_f in bands.items():
        st = {k: _stats(v, sel_f) for k, v in pairs.items()}
        verdict = {}
        for t in TYPE_NAMES:
            for m in ("rms_dB", "rms_deg", "mean_dB", "mean_deg"):
                tw = [abs(st[k][t][m]) for k in ("Mild 5 vs 6", "Moderate 5 vs 6", "Severe 5 vs 6")]
                x = abs(st["RightOnly vs mirror(LeftOnly) (5 vs 6)"][t][m])
                verdict[f"{t} {m}"] = dict(value=x, twin_min=min(tw), twin_max=max(tw), ratio_to_twin_max=x / max(tw),
                                           within=x <= max(tw))
        out[bn] = dict(stats=st, verdict=verdict)
    # model-free ring: uniform offset and spread of the per-antenna neighbour-path phase difference
    ring = {}
    for k, v in pairs.items():
        r = -FG.detuning_values(v, f)
        ring[k] = dict(values=r.tolist(), mean=float(r.mean()), spread=float(r.max() - r.min()))
    out["ring"] = ring
    # signal SIZE: rms of each design's change against the same reference H6, second solve / first solve
    size = {}
    for nm, a, b in (("RightOnly / LeftOnly (5 / 6)", L("RightOnly", "H6"), apply_group(L("LeftOnly", "H6"), MIRROR)),
                     ("Mild 5 / 6", L("Mild5", "H6"), L("Mild6", "H6")), ("Moderate 5 / 6", L("Mod5", "H6"), L("Mod6", "H6")),
                     ("Severe 5 / 6", L("Sev5", "H6"), L("Sev6", "H6"))):
        size[nm] = {TYPE_NAMES[t]: dict(
            amp=float(np.sqrt(np.mean(a[PATH_TYPE == t].real ** 2)) / np.sqrt(np.mean(b[PATH_TYPE == t].real ** 2))),
            phase=float(np.sqrt(np.mean(a[PATH_TYPE == t].imag ** 2)) / np.sqrt(np.mean(b[PATH_TYPE == t].imag ** 2))))
            for t in range(4)}
    out["size_ratio"] = size
    # reconstruction level: |e(second) - e(first)| per sector (primary variant, committed runs)
    post = json.loads((OUT / "posteriors.json").read_text())["targets"]
    ro = json.loads((OUT / "rightonly" / "rightonly.json").read_text(encoding="utf-8"))["runs"]
    lo_m = [post["LeftOnly_p6"]["sectors"][int(np.flatnonzero(MIRROR == k)[0])]["e_median"] for k in range(N)]
    de = {"RightOnly vs mirror(LeftOnly)": [abs(s["e_median"] - lo_m[k]) for k, s in enumerate(ro["RightOnly_p6"]["sectors"])]}
    for nm, a, b in (("Mild 5 vs 6", "Mild_p5", "Mild_p6"), ("Moderate 5 vs 6", "Moderate_p5", "Moderate_p6"),
                     ("Severe 5 vs 6", "Severe_p5", "Severe_p6")):
        de[nm] = [abs(x["e_median"] - y["e_median"]) for x, y in zip(post[a]["sectors"], post[b]["sectors"])]
    out["e_change"] = de
    return out


def rulers(A):
    """R1c (floor = largest |null|) rebuilt: old nine mirror-symmetric designs + the two rotated nulls."""
    f = freq()
    post = json.loads((OUT / "posteriors.json").read_text())["targets"]
    ro = json.loads((OUT / "rightonly" / "rightonly.json").read_text(encoding="utf-8"))["runs"]
    tb = json.loads((OUT / "blind" / "Test_B" / "report.json").read_text(encoding="utf-8"))["variants"]

    def lre(e):
        return float(np.mean(e[1:3]) - np.mean(e[4:6]))

    old = {t: [s["e_median"] for s in post[t]["sectors"]] for t in
           ["Healthy_p7", "MCI_p6", "Mild_p5", "Mild_p6", "Moderate_p5", "Moderate_p6", "Severe_p5", "Severe_p6"]}
    old["Healthy_p6_vsH7"] = [s["e_median"] for s in ro["Healthy_p6_vsH7"]["sectors"]]
    rot = {k: A[f"{k} vs H6 [standard]"]["e_med"] for k in ("rot07", "rot19")}
    calls_old = {t: [int(s["P_affected"] > 0.5) for s in post[t]["sectors"]] for t in old if t in post}
    calls_old["Healthy_p6_vsH7"] = ro["Healthy_p6_vsH7"]["calls"]
    calls_rot = {k: A[f"{k} vs H6 [standard]"]["calls"] for k in ("rot07", "rot19")}

    def onesided(c):
        return bool((c[1] or c[2]) != (c[4] or c[5]))

    lre_floor_old = max(abs(lre(e)) for e in old.values())
    lre_floor_new = max(lre_floor_old, max(abs(lre(e)) for e in rot.values()))
    designs = {"LeftOnly_p6": [s["e_median"] for s in post["LeftOnly_p6"]["sectors"]],
               "RightOnly (primary)": [s["e_median"] for s in ro["RightOnly_p6"]["sectors"]],
               "Test_B (primary)": [s["e_median"] for s in tb["standard_H6"]["sectors"]]}
    rec = dict(LR_e=dict(floor_old=lre_floor_old, floor_new=lre_floor_new,
                         rot_values={k: lre(e) for k, e in rot.items()},
                         designs={k: dict(value=lre(e), ratio_old=abs(lre(e)) / lre_floor_old,
                                          ratio_new=abs(lre(e)) / lre_floor_new) for k, e in designs.items()}),
               onesided_calls=dict(old_nulls=sum(onesided(c) for c in calls_old.values()), n_old=len(calls_old),
                                   rot_nulls={k: onesided(c) for k, c in calls_rot.items()},
                                   any_call_in_rot_nulls={k: int(sum(c)) for k, c in calls_rot.items()}))
    # model-free ring statistics
    obs = {"H7 vs H6": L("H7", "H6"), "H6 vs H7": L("H6", "H7"), "MCI vs H6": L("MCI", "H6"),
           "rot07 vs H6": L("rot07", "H6"), "rot19 vs H6": L("rot19", "H6"),
           "Mild5 vs H6": L("Mild5", "H6"), "Mild6 vs H7": L("Mild6", "H7"), "Mod5 vs H6": L("Mod5", "H6"),
           "Mod6 vs H7": L("Mod6", "H7"), "Sev5 vs H6": L("Sev5", "H6"), "Sev6 vs H7": L("Sev6", "H7"),
           "LeftOnly vs H6": L("LeftOnly", "H6"), "RightOnly vs H6": L("RightOnly", "H6"), "Test_B vs H6": L("Test_B", "H6"),
           "Moderate5 vs H6 (FB)": L("Mod5", "H6")}
    ring = {k: -FG.detuning_values(v, f) for k, v in obs.items()}

    def lr_c(r):
        return float(np.mean(r[[1, 2]]) - np.mean(r[[4, 5]]))

    def diag_max(r):  # largest elevation of any of the three diagonal antenna pairs over the other four
        return max(float(np.mean(r[[a, a + 3]]) - np.mean(np.delete(r, [a, a + 3]))) for a in range(3))

    healthy_nulls_old = ["H7 vs H6", "H6 vs H7", "MCI vs H6"]
    rot_nulls = ["rot07 vs H6", "rot19 vs H6"]
    sym_old = healthy_nulls_old + ["Mild5 vs H6", "Mild6 vs H7", "Mod5 vs H6", "Mod6 vs H7", "Sev5 vs H6", "Sev6 vs H7"]
    stats = {}
    for name, fn, nulls_old, tests in [
            ("ring LR contrast (left T2,T3 - right T5,T6), deg", lr_c, sym_old,
             ["LeftOnly vs H6", "RightOnly vs H6", "Test_B vs H6"]),
            ("ring spread (max - min), deg", lambda r: float(r.max() - r.min()), healthy_nulls_old,
             ["Test_B vs H6"]),
            ("ring diagonal-pair elevation (largest of 3 pairs), deg", diag_max, healthy_nulls_old, ["Test_B vs H6"]),
            ("ring T2,T5 elevation (Test_B's pair, chosen after seeing it), deg",
             lambda r: float(np.mean(r[[1, 4]]) - np.mean(r[[0, 2, 3, 5]])), healthy_nulls_old, ["Test_B vs H6"])]:
        fo = max(abs(fn(ring[k])) for k in nulls_old)
        fnw = max(fo, max(abs(fn(ring[k])) for k in rot_nulls))
        stats[name] = dict(null_values={k: fn(ring[k]) for k in nulls_old + rot_nulls}, floor_old=fo, floor_new=fnw,
                           tests={k: dict(value=fn(ring[k]), ratio_old=abs(fn(ring[k])) / fo,
                                          ratio_new=abs(fn(ring[k])) / fnw) for k in tests})
    rec["ring"] = stats
    rec["ring_values"] = {k: v.tolist() for k, v in ring.items()}
    return rec


def _targets_lodo():
    return [("Healthy_p7", "Healthy", "new_with_slices_Healthy_sliced.s6p"),
            ("Mild_p5", "Mild_lobe", "new_with_slices_Mild_lobe.s6p"),
            ("Mild_p6", "Mild_lobe", "new_with_slices_Mild_lobe_new.s6p"),
            ("Moderate_p5", "Moderate_lobe", "new_with_slices_Moderate_lobe.s6p"),
            ("Moderate_p6", "Moderate_lobe", "new_with_slices_Moderate_lobe_c3.s6p"),
            ("Severe_p5", "Severe_lobe", "new_with_slices_Severe_lobe.s6p"),
            ("Severe_p6", "Severe_lobe", "new_with_slices_Severe_lobe_c3.s6p"),
            ("LeftOnly_p6", "LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p"),
            ("MCI_p6", "MCI_lobe", "new_with_slices_MCI_lobe_c3.s6p")]


def _coverage(rows):
    allc = [r["covered"] for r in rows]
    aff = [r["covered"] for r in rows if r["e_true"] > 0]
    calls = [r["call_ok"] for r in rows]
    return dict(n=len(allc), coverage_all=float(np.mean(allc)), n_affected=len(aff), coverage_affected=float(np.mean(aff)),
                calls_correct=float(np.mean(calls)))


def _cov_rows(tag, sectors, e_true):
    out = []
    for k, s in enumerate(sectors):
        out.append(dict(target=tag, sector=SECTOR_SHORT[k], e_true=float(e_true[k]),
                        covered=bool(s["e_q05"] <= e_true[k] <= s["e_q95"]),
                        call_ok=bool((s["P_affected"] > 0.5) == (e_true[k] > 0)), P_affected=s["P_affected"],
                        e_med=s["e_median"], e_int=[s["e_q05"], s["e_q95"]]))
    return out


def noise_and_coverage(folds):
    from .data import DESIGNS as DS
    post = json.loads((OUT / "posteriors.json").read_text())["targets"]
    ro = json.loads((OUT / "rightonly" / "rightonly.json").read_text(encoding="utf-8"))["runs"]
    tb = json.loads((OUT / "blind" / "Test_B" / "report.json").read_text(encoding="utf-8"))["variants"]
    truth = {t: next(d for d in DS if d.file == fn).truth.e for t, _, fn in _targets_lodo()}
    truth["RightOnly"] = truth_of_key("RightOnly").e
    truth["Test_B"] = truth_of_key("Test_B").e
    before, after, runs_after = [], [], {}
    for t, g, fn in _targets_lodo():
        before += _cov_rows(t, post[t]["sectors"], truth[t])
        d = next(x for x in DS if x.file == fn)
        s_re, s_im = augmented(folds[g], t)
        sm = summarize_run(posterior(folds[g], s_re, s_im), LO.observation(d), tag=f"PH_aug_{t}")
        runs_after[t] = short(sm)
        after += _cov_rows(t, sm["sectors"], truth[t])
    before += _cov_rows("RightOnly", ro["RightOnly_p6"]["sectors"], truth["RightOnly"])
    before += _cov_rows("Test_B", tb["standard_H6"]["sectors"], truth["Test_B"])
    variants = {}
    for tgt, fold, ref in (("RightOnly", folds["LeftOnly"], "H6"), ("Test_B", folds["__blind__"], "H6")):
        s_re, s_im = augmented(fold, tgt)
        for var, rf in (("standard", ref), ("gainfree", ref), ("standard", "H7")):
            sm = summarize_run(posterior(fold, s_re, s_im, var), L(tgt, rf), tag=f"PH_aug_{tgt}_{var}_{rf}")
            variants[f"{tgt} {var} vs {rf}"] = short(sm)
            if var == "standard" and rf == "H6":
                runs_after[tgt] = short(sm)
                after += _cov_rows(tgt, sm["sectors"], truth[tgt])
    cov_b, cov_a = _coverage(before), _coverage(after)
    # calibration of high-confidence calls (P >= 0.99 or <= 0.01), before and after
    ro_sec = {"RightOnly gainfree": ro["RightOnly_gainfree"], "RightOnly vs H7": ro["RightOnly_vsH7"]}
    tb_sec = {"Test_B gainfree": tb["gainfree_H6"], "Test_B vs H7": tb["standard_H7"]}
    hi_b = [r for r in before]
    for k, v in ro_sec.items():
        hi_b += _cov_rows(k, v["sectors"], truth["RightOnly"])
    for k, v in tb_sec.items():
        hi_b += _cov_rows(k, v["sectors"], truth["Test_B"])
    hi_a = list(after)
    for k, v in variants.items():
        if not k.endswith("standard vs H6"):
            tg = k.split()[0]
            hi_a += [dict(call_ok=bool((p > 0.5) == (e > 0)), P_affected=p) for p, e in zip(v["P_aff"], truth[tg])]

    def calib(rows):
        conf = [r for r in rows if r["P_affected"] >= 0.99 or r["P_affected"] <= 0.01]
        return dict(n_confident=len(conf), wrong=int(sum(not r["call_ok"] for r in conf)),
                    n_all=len(rows), wrong_all=int(sum(not r["call_ok"] for r in rows)))
    smp = twin_samples()
    sizes = {k: dict(rms_dB={TYPE_NAMES[t]: float(np.sqrt(np.mean((v[PATH_TYPE == t].real * 8.686) ** 2))) for t in range(4)},
                     rms_deg={TYPE_NAMES[t]: float(np.sqrt(np.mean(np.degrees(v[PATH_TYPE == t].imag) ** 2))) for t in range(4)})
             for k, v in smp.items()}
    return dict(twin_sample_sizes=sizes, coverage_before=cov_b, coverage_after=cov_a, rows_before=before, rows_after=after,
                runs_after=runs_after, variants_after=variants, calibration_before=calib(hi_b), calibration_after=calib(hi_a))


def ringphase(folds):
    from .data import DESIGNS as DS
    cases = [("Test_B", folds["__blind__"], lambda: L("Test_B", "H6")),
             ("RightOnly", folds["LeftOnly"], lambda: L("RightOnly", "H6")),
             ("LeftOnly_p6", folds["LeftOnly"], lambda: L("LeftOnly", "H6")),
             ("Healthy_p7", folds["Healthy"], lambda: L("H7", "H6")),
             ("MCI_p6", folds["MCI_lobe"], lambda: L("MCI", "H6")),
             ("rot07", folds["__blind__"], lambda: L("rot07", "H6")),
             ("rot19", folds["__blind__"], lambda: L("rot19", "H6")),
             ("Mild_p5", folds["Mild_lobe"], lambda: L("Mild5", "H6")),
             ("Moderate_p5", folds["Moderate_lobe"], lambda: L("Mod5", "H6")),
             ("Severe_p5", folds["Severe_lobe"], lambda: L("Sev5", "H6"))]
    out = {}
    for tag, fold, getL in cases:
        out[tag] = {"ringphase (fold noise)": short(summarize_run(posterior(fold, variant="ringphase"), getL(),
                                                                tag=f"PH_ring_{tag}"))}
        if tag in ("Test_B", "RightOnly"):
            s_re, s_im = augmented(fold, tag)
            out[tag]["ringphase (augmented noise)"] = short(summarize_run(posterior(fold, s_re, s_im, "ringphase"), getL()))
    return out


# ---------------------------------------------------------------- report
def _calls_txt(c):
    return ", ".join(SECTOR_SHORT[k] for k in range(N) if c[k]) or "none"


def report(o):
    L_ = ["# POST HOC analyses after the Test_B truth (imaging2)", "",
          f"Code {o['code']}. **Everything in this file is post hoc.** Committed estimates, the blind protocol "
          "(595e9cb), its verdict (PASS, f88236c), thresholds and predictions are unchanged.", "",
          "## 0. New files (imaging2 set file: `results/imaging2/sets.csv`)", "",
          "| design | file | role | passes | final ΔS | elements | glitch-masked points |", "|---|---|---|---|---|---|---|"]
    for r in o["new_files"]:
        L_.append(f"| {r['design']} | `{r['file']}` | {r['role']} | {r['passes']} | {r['final_dS']} | {r['elements']:,} | "
                  f"{o['masking'][r['design']]} |")
    L_ += ["", "## A. Rotated nulls as targets (training = every lobe design; nulls never in training)", "",
           "| run | stage (P) | lobes called | P(affected) S1…S6 | fit |", "|---|---|---|---|---|"]
    for k, v in o["A_nulls_as_targets"].items():
        L_.append(f"| {k} | {v['stage']} ({v['P_stage']:.2f}) | {_calls_txt(v['calls'])} | {' / '.join(f'{p:.2f}' for p in v['P_aff'])} | {v['fit']:.2f} |")
    L_ += ["", "## B. Each rotated null as the healthy reference", "",
           "| run | stage (P) | lobes called | ê S1…S6 (mm) | fit |", "|---|---|---|---|---|"]
    for k, v in o["B_nulls_as_references"].items():
        L_.append(f"| {k} | {v['stage']} ({v['P_stage']:.2f}) | {_calls_txt(v['calls'])} | "
                  f"{' / '.join(f'{e:.1f}' for e in v['e_med'])} | {v['fit']:.2f} |")
    pg = o["C_pass_gap"]
    L_ += ["", "## C. Pass gap: RightOnly vs mirror(LeftOnly) against the three pass-5 vs pass-6 twins", "",
           "Same statistics, same frequencies: per path class, rms and band mean of the complex log-ratio between the two "
           "solves (amplitude dB, phase °). 'within' = |RightOnly − mirror(LeftOnly)| ≤ the largest of the three 5-vs-6 twins.", ""]
    for bn in ("3.2-4.2 GHz", "3.30-3.65 GHz"):
        L_ += [f"**{bn}**", "", "| statistic | RO − mirror(LO) | twins 5 vs 6 (min–max) | / twin max | within |", "|---|---|---|---|---|"]
        for k, v in pg[bn]["verdict"].items():
            L_.append(f"| {k} | {v['value']:.3f} | {v['twin_min']:.3f}–{v['twin_max']:.3f} | {v['ratio_to_twin_max']:.2f} | "
                      f"{'yes' if v['within'] else '**no**'} |")
        L_.append("")
    L_ += ["Model-free ring of each pair (per-antenna neighbour-path phase difference, 3.30–3.65 GHz): mean and spread (°)", "",
           "| pair | T1…T6 | mean | spread |", "|---|---|---|---|"]
    for k, v in pg["ring"].items():
        L_.append(f"| {k} | {' / '.join(f'{x:.2f}' for x in v['values'])} | {v['mean']:+.2f} | {v['spread']:.2f} |")
    L_ += ["", "Signal size: rms of the change against H6, second solve / first solve (RightOnly / mirrored LeftOnly; "
           "pass-5 / pass-6 for the twins). 1.00 = same size.", "",
           "| pair | " + " | ".join(f"{t} amp / phase" for t in TYPE_NAMES) + " |", "|---|---|---|---|---|"]
    for k, v in pg["size_ratio"].items():
        L_.append(f"| {k} | " + " | ".join(f"{v[t]['amp']:.2f} / {v[t]['phase']:.2f}" for t in TYPE_NAMES) + " |")
    L_ += ["", "Reconstruction: |ê(second solve) − ê(first solve)| per sector (mm; committed primary runs).", "",
           "| pair | S1…S6 | max |", "|---|---|---|"]
    for k, v in pg["e_change"].items():
        L_.append(f"| {k} | {' / '.join(f'{x:.1f}' for x in v)} | {max(v):.1f} |")
    D = o["D_rulers"]
    L_ += ["", "## D. Rulers rebuilt with the rotated nulls (R1c: floor = largest |null|; ≥ 3x established, 2–3x sensitive, "
           "< 2x not separable)", "", "**Reconstruction statistics.**", "",
           f"- LR_e (ê left − right): floor old {D['LR_e']['floor_old']:.2f} → new {D['LR_e']['floor_new']:.2f} mm "
           f"(rotated nulls: {', '.join(f'{k} {v:+.2f}' for k, v in D['LR_e']['rot_values'].items())})."]
    for k, v in D["LR_e"]["designs"].items():
        L_.append(f"  - {k}: {v['value']:+.2f} mm → {v['ratio_old']:.2f}x old, {v['ratio_new']:.2f}x new")
    oc = D["onesided_calls"]
    L_.append(f"- One-sided call patterns among nulls: old {oc['old_nulls']}/{oc['n_old']}; rotated nulls one-sided: "
              f"{oc['rot_nulls']}; lobes called in the rotated nulls: {oc['any_call_in_rot_nulls']}.")
    L_ += ["", "**Model-free ring statistics** (vs the matched healthy reference; 3.30–3.65 GHz window is itself post hoc).", ""]
    for name, v in D["ring"].items():
        L_.append(f"- {name}: floor old {v['floor_old']:.2f} → new {v['floor_new']:.2f}; nulls "
                  + ", ".join(f"{k} {x:+.2f}" for k, x in v["null_values"].items()))
        for k, t in v["tests"].items():
            L_.append(f"  - {k}: {t['value']:+.2f} → {t['ratio_old']:.2f}x old, **{t['ratio_new']:.2f}x new**")
    E = o["E_noise"]
    L_ += ["", "## E. Noise model with every solve-to-solve offset, coverage before / after", "",
           "Twin samples (each taken as one sample of an observation's solve-to-solve error; the target's own twin "
           "excluded): rms per path class:", "", "| twin | refl dB / ° | neighbour dB / ° | 2nd-nb dB / ° | opposite dB / ° |",
           "|---|---|---|---|---|"]
    for k, v in E["twin_sample_sizes"].items():
        L_.append(f"| {k} | " + " | ".join(f"{v['rms_dB'][t]:.2f} / {v['rms_deg'][t]:.1f}" for t in TYPE_NAMES) + " |")
    cb, ca = E["coverage_before"], E["coverage_after"]
    L_ += ["", "| | sectors | 90% coverage, all sectors | affected sectors | 90% coverage, affected | lobe calls correct |",
           "|---|---|---|---|---|---|",
           f"| before (committed noise model) | {cb['n']} | {cb['coverage_all']:.0%} | {cb['n_affected']} | {cb['coverage_affected']:.0%} | {cb['calls_correct']:.0%} |",
           f"| after (+ solve-to-solve offsets) | {ca['n']} | {ca['coverage_all']:.0%} | {ca['n_affected']} | {ca['coverage_affected']:.0%} | {ca['calls_correct']:.0%} |",
           "", "Targets: 9 leave-one-out designs + RightOnly + Test_B (primary variant).", "",
           "| target (after) | stage | lobes called | ê S1…S6 [90%] | fit |", "|---|---|---|---|---|"]
    for k, v in E["runs_after"].items():
        L_.append(f"| {k} | {v['stage']} ({v['P_stage']:.2f}) | {_calls_txt(v['calls'])} | "
                  + " / ".join(f"{e:.1f} [{a:.1f}–{b:.1f}]" for e, (a, b) in zip(v["e_med"], v["e_int"])) + f" | {v['fit']:.2f} |")
    L_ += ["", "**Challenge: P(affected) with the augmented noise model**", "", "| run | P(affected) S1…S6 | lobes called |", "|---|---|---|"]
    for k, v in E["variants_after"].items():
        L_.append(f"| {k} | {' / '.join(f'{p:.2f}' for p in v['P_aff'])} | {_calls_txt(v['calls'])} |")
    L_ += ["", f"Calibration of confident calls (P ≥ 0.99 or ≤ 0.01): before {E['calibration_before']['wrong']} wrong of "
           f"{E['calibration_before']['n_confident']} (all calls: {E['calibration_before']['wrong_all']} wrong of "
           f"{E['calibration_before']['n_all']}); after {E['calibration_after']['wrong']} of {E['calibration_after']['n_confident']} "
           f"(all: {E['calibration_after']['wrong_all']} of {E['calibration_after']['n_all']})."]
    L_ += ["", "## F. Ring-mean-phase variant (phase ring mean of every path class removed at every frequency)", "",
           "| target | noise | stage (P) | P(stage) Healthy/Mild/Moderate/Severe | lobes called | ê S1…S6 [90%] | fit |",
           "|---|---|---|---|---|---|---|"]
    for k, vv in o["F_ringphase"].items():
        for nm, v in vv.items():
            L_.append(f"| {k} | {nm} | {v['stage']} ({v['P_stage']:.2f}) | "
                      f"{' / '.join(f'{x:.2f}' for x in v['P_stage_all'].values())} | {_calls_txt(v['calls'])} | "
                      + " / ".join(f"{e:.1f} [{a:.1f}–{b:.1f}]" for e, (a, b) in zip(v["e_med"], v["e_int"])) + f" | {v['fit']:.2f} |")
    return "\n".join(L_) + "\n"


def write_sets():
    """imaging2's own set file: every file it uses, its role, and whether it is in any training set."""
    import csv
    rows = [("Healthy_sliced_new", H6, "reference (H6); zero-change pair with H7 in training", 1, 6, 0.0155, 1081728, "ref"),
            ("Healthy_sliced", H7, "train + target (H7 vs H6); secondary reference", 2, 7, 0.0092, 1349491, "yes"),
            ("Mild_lobe", FILES["Mild5"], "train + LODO target", 1, 5, 0.0186, 739774, "yes"),
            ("Mild_lobe", FILES["Mild6"], "train + LODO target", 2, 6, 0.0150, 878656, "yes"),
            ("Moderate_lobe", FILES["Mod5"], "train + LODO target", 1, 5, 0.0194, 796281, "yes"),
            ("Moderate_lobe", FILES["Mod6"], "train + LODO target", 2, 6, 0.014593, 949865, "yes"),
            ("Severe_lobe", FILES["Sev5"], "train + LODO target", 1, 5, 0.019999, 690077, "yes"),
            ("Severe_lobe", FILES["Sev6"], "train + LODO target", 2, 6, 0.011567, 819294, "yes"),
            ("LeftOnly_test", FILES["LeftOnly"], "train + LODO target", 1, 6, 0.014686, 941358, "yes"),
            ("MCI_lobe", FILES["MCI"], "train + LODO target", 1, 6, 0.013948, 981160, "yes"),
            ("RightOnly_test", FILES["RightOnly"], "replication target (LeftOnly fold); never trained on", 1, 5, 0.019742, 789241, "no"),
            ("Test_B", FILES["Test_B"], "blind target (scored); never trained on", 1, 6, 0.012597, 903758, "no"),
            ("Null_rot07", FILES["rot07"], "null target / alternative reference (post hoc); never trained on", 1, 6, 0.014650, 1045101, "no"),
            ("Null_rot19", FILES["rot19"], "null target / alternative reference (post hoc); never trained on", 1, 6, 0.014495, 939082, "no"),
            ("Uniform v2 (new_*.s6p)", "new_Healthy/MCI/MildAD/ModerateAD/SevereAD.s6p", "not used (own-project mesh noise)", "", "", "", "", "no")]
    with open(OUT / "sets.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["design", "file", "imaging2 role", "stop_rule", "passes", "final_dS", "elements", "in_training"])
        w.writerows(rows)


# ---------------------------------------------------------------- presentation figures
def pres_figures():
    """TestB_vs_truth_pres.png (z = 50 overview with truth) and TestB_stack_truth_pres.png (stack with truth contours).
    New files only; blind/ is not modified (its marginals are copied into the cache under new names)."""
    import shutil

    import matplotlib.pyplot as plt
    register()
    blind = OUT / "blind" / "Test_B"
    rep = json.loads((blind / "report.json").read_text(encoding="utf-8"))
    tags = {"standard_H6": "TestB_standard", "gainfree_H6": "TestB_gainfree", "standard_H7": "TestB_vsH7"}
    titles = {"TestB_standard": "standard (primary)", "TestB_gainfree": "gain-removing",
              "TestB_vsH7": "ref.: repeat healthy simulation"}
    extra = {}
    for v, t in tags.items():
        shutil.copyfile(blind / f"marg_{v}.npy", CACHE / f"marg_{t}.npy")
        sv = rep["variants"][v]
        extra[t] = dict(sv, file=FILES["Test_B"], transform=None, gof=dict(chi2_per_dof=sv["chi2_per_dof"], tau=sv["tau"]))
    post = FG.load_post()
    post["targets"].update(extra)
    saved = dict(FG.TITLES)
    FG.TITLES.update(titles)
    nr = RE.noise_rel_at_field_freqs()
    FG.fig_overview(list(tags.values()), post, nr, "sig", 50.0, fn=FIG / "TestB_vs_truth_pres.png",
                    suptitle="Blind Test_B (truth revealed after the estimates): σ change, z = 50 mm")
    FG.TITLES.clear()
    FG.TITLES.update(saved)
    # stack with truth contours
    zs = RE.Z_SLICES
    names = list(tags.values())
    fig, axs = plt.subplots(1 + len(names), len(zs), figsize=(1.95 * len(zs) + 1.6, 2.0 * (1 + len(names)) + 1.0))
    tr = truth_of_key("Test_B")
    for j, z in enumerate(zs):
        X, Y, Z, ext = FG.display_grid("axial", z, 0.75)
        tru = RE.truth_maps(tr, X, Y, Z)
        dt = tru["sig"] - tru["sig0"]
        FG.show_change(axs[0, j], dt, ext, "sig")
        FG.decorate(axs[0, j], "axial", z, labels=False)
        axs[0, j].set_title(f"z = {z:.0f} mm" + (" (ring)" if z == 50 else ""), fontsize=10)
        alpha = RE.fade_alpha(RE.snr_at(X, Y, Z, nr) * RE.BAND_FACTOR)
        alpha[np.sqrt(X ** 2 + Y ** 2 + Z ** 2) > 83.5] = 1.0
        U = np.linspace(ext[0], ext[1], X.shape[1])
        V = np.linspace(ext[2], ext[3], X.shape[0])
        for i, n in enumerate(names):
            M = RE.posterior_maps(np.load(CACHE / f"marg_{n}.npy"), X, Y, Z)
            a = axs[1 + i, j]
            FG.show_change(a, M["sig"] - M["sig0"], ext, "sig", alpha)
            # 1.0 S/m: the affected lobes' CSF gap and shifted gray matter (>= 2.5 S/m), not the whole-head
            # CSF_Mild layer (+0.64 S/m everywhere)
            a.contour(U, V, dt, levels=[1.0], colors=[FG.INK], linewidths=0.9)
            FG.decorate(a, "axial", z, labels=False)
    axs[0, 0].set_ylabel("TRUE change\n(revealed after)", fontsize=8.5)
    for i, n in enumerate(names):
        lab = {"TestB_standard": "standard (primary)", "TestB_gainfree": "gain-removing",
               "TestB_vsH7": "reference: repeat\nhealthy simulation"}[n]
        axs[1 + i, 0].set_ylabel(lab + "\n(black: true outline)", fontsize=8.0, color=FG.BLUE)
    cax = fig.add_axes([0.93, 0.3, 0.01, 0.4])
    fig.colorbar(plt.cm.ScalarMappable(cmap=FG.DIV, norm=plt.Normalize(-FG.LIM["sig"], FG.LIM["sig"])), cax=cax,
                 label="change in conductivity σ (S/m)")
    fig.suptitle("Blind Test_B: reconstructed conductivity change slice by slice, true affected region outlined "
                 "(front at top, subject's left on the right).\nHatched = not measured. Estimates committed before the "
                 "truth was revealed.", fontsize=10.5, y=0.995)
    fig.subplots_adjust(left=0.1, right=0.92, top=0.9, bottom=0.005, wspace=0.03, hspace=0.05)
    fn = FIG / "TestB_stack_truth_pres.png"
    fig.savefig(fn, dpi=110)
    plt.close(fig)
    return [FIG / "TestB_vs_truth_pres.png", fn]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["all", "figs"])
    a = ap.parse_args()
    if a.cmd == "all":
        write_sets()
        all_()
    else:
        print(pres_figures())
