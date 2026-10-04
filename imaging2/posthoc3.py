"""POST HOC, round 3 (after Null_rot31 / Null_rot43 arrived; the pre-registered evaluation is imaging2.nullrulers at
a295006, run unchanged). Everything here is post hoc and labelled so; nothing is adopted as a new reference or rule.

    python -m imaging2.posthoc3 verify      # ratios / ring numbers of the rotated nulls vs H6; H6 typicality
    python -m imaging2.posthoc3 meanref     # the mean of the six healthy meshes as one more reference (not adopted)
-> results/imaging2/posthoc3/*.json, *.md
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from . import posthoc as PH
from .data import OUT, PATH_TYPE, freq, git_rev, paths_of
from .figures import detuning_values

OUT3 = OUT / "posthoc3"
HEALTHY = ["H6", "H7", "rot07", "rot19", "rot31", "rot43"]
for _k in ("rot31", "rot43"):
    PH.FILES.setdefault(_k, f"new_with_slices_Null_{_k}.s6p")


def class_db(S):
    """Band power per path (trapezoid over 3.2-4.2 GHz of |S|^2), geometric mean over each ring class, in dB."""
    f = freq()
    P = np.trapezoid(np.abs(paths_of(S)) ** 2, f, axis=1)
    return {k: float(np.mean(10 * np.log10(P[PATH_TYPE == k]))) for k in range(4)}


def ratios(S):
    c = class_db(S)
    return dict(R31=c[3] - c[1], R21=c[2] - c[1], R32=c[3] - c[2])


def ring_stats(S, Sref):
    r = -detuning_values(np.log(paths_of(S) / paths_of(Sref)), freq())
    return dict(ring=r.tolist(), ring_mean=float(r.mean()), ring_spread=float(r.max() - r.min()),
                left_minus_right=float(np.mean(r[[1, 2]]) - np.mean(r[[4, 5]])))


def verify():
    OUT3.mkdir(parents=True, exist_ok=True)
    S = {k: PH.S(k) for k in HEALTHY}
    out = dict(code=git_rev(), label="POST HOC", vs_H6={}, typicality={})
    r6 = ratios(S["H6"])
    for k in HEALTHY[2:]:
        rk = ratios(S[k])
        out["vs_H6"][k] = dict(dR31=rk["R31"] - r6["R31"], dR21=rk["R21"] - r6["R21"], dR32=rk["R32"] - r6["R32"],
                               **ring_stats(S[k], S["H6"]))
    # each healthy mesh against the mean of the other five (ratios: mean of the others' values; ring: complex mean S)
    R = {k: ratios(S[k]) for k in HEALTHY}
    for k in HEALTHY:
        others = [o for o in HEALTHY if o != k]
        row = {}
        for q in ("R31", "R21", "R32"):
            vals = np.array([R[o][q] for o in others])
            row[q] = dict(value_minus_mean_others=float(R[k][q] - vals.mean()), sd_others=float(vals.std(ddof=1)),
                          z=float((R[k][q] - vals.mean()) / vals.std(ddof=1)),
                          rank_among_six=int(1 + sum(R[o][q] < R[k][q] for o in others)))
        Smean = np.mean([S[o] for o in others], axis=0)
        rs = ring_stats(S[k], Smean)
        row["ring_mean_phase_vs_mean_others"] = rs["ring_mean"]
        row["ring_spread_vs_mean_others"] = rs["ring_spread"]
        out["typicality"][k] = row
    # spread of the per-mesh ring means, to judge H6
    rm = np.array([out["typicality"][k]["ring_mean_phase_vs_mean_others"] for k in HEALTHY])
    out["ring_mean_summary"] = dict(values=dict(zip(HEALTHY, rm.tolist())))
    (OUT3 / "verify.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    L = ["# POST HOC: rotated nulls vs H6, and is H6 typical?", "",
         "Ratios: band power per path (trapezoid over 3.2–4.2 GHz, glitch-masked), geometric mean over each ring class; "
         "R31 = opposite / neighbour, R21 = second-neighbour / neighbour, R32 = opposite / second-neighbour (dB). Ring: "
         "per-antenna neighbour-path phase delay, 3.30–3.65 GHz.", "",
         "| rotated null vs H6 | ΔR31 dB | ΔR21 dB | ΔR32 dB | ring spread ° | ring mean ° | left − right ° |",
         "|---|---|---|---|---|---|---|"]
    for k, v in out["vs_H6"].items():
        L.append(f"| {k} | {v['dR31']:+.3f} | {v['dR21']:+.3f} | {v['dR32']:+.3f} | {v['ring_spread']:.2f} | "
                 f"{v['ring_mean']:+.2f} | {v['left_minus_right']:+.2f} |")
    L += ["", "Each healthy mesh against the mean of the other five (z = difference / SD of the other five; rank 1 = lowest):",
          "", "| mesh | R31: Δ (z, rank) | R21: Δ (z, rank) | R32: Δ (z, rank) | ring-mean phase vs mean of others ° | ring spread ° |",
          "|---|---|---|---|---|---|"]
    for k, v in out["typicality"].items():
        L.append(f"| {k} | " + " | ".join(f"{v[q]['value_minus_mean_others']:+.3f} ({v[q]['z']:+.1f}, {v[q]['rank_among_six']})"
                                         for q in ("R31", "R21", "R32"))
                 + f" | {v['ring_mean_phase_vs_mean_others']:+.2f} | {v['ring_spread_vs_mean_others']:.2f} |")
    (OUT3 / "verify.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return out


# ---------------------------------------------------------------- mean of the six healthy meshes as a reference
MR_TARGETS = [("Mild_p5", "Mild_lobe", "Mild5"), ("Mild_p6", "Mild_lobe", "Mild6"), ("Moderate_p5", "Moderate_lobe", "Mod5"),
              ("Moderate_p6", "Moderate_lobe", "Mod6"), ("Severe_p5", "Severe_lobe", "Sev5"), ("Severe_p6", "Severe_lobe", "Sev6"),
              ("LeftOnly_p6", "LeftOnly", "LeftOnly"), ("RightOnly", "LeftOnly", "RightOnly"), ("Test_B", "__blind__", "Test_B")]


def _mr_job(args):
    tag, g, key = args
    from . import lodo as LO
    from .nullrulers import VARIANTS, truth_calls_stage
    PH.register()
    fold = LO.fit_fold(g)
    Smean = np.mean([PH.S(k) for k in HEALTHY], axis=0)
    Ld = np.log(paths_of(PH.S(key)) / paths_of(Smean))
    tc, ts = truth_calls_stage(key)
    rows = []
    for var in VARIANTS:
        sm = PH.short(PH.summarize_run(PH.posterior(fold, variant=var), Ld))
        rows.append(dict(target=tag, reference="mean of 6 healthy meshes", variant=var, stage=sm["stage"],
                         P_stage=sm["P_stage"], calls=sm["calls"], fit=sm["fit"], e_med=sm["e_med"],
                         wrong_lobes=int(sum(a != b for a, b in zip(sm["calls"], tc))), stage_ok=sm["stage"] == ts))
    return rows


def meanref(procs=6):
    OUT3.mkdir(parents=True, exist_ok=True)
    with Pool(procs) as pool:
        rows = sum(pool.map(_mr_job, MR_TARGETS), [])
    (OUT3 / "meanref.json").write_text(json.dumps(dict(code=git_rev(), label="POST HOC; not adopted", rows=rows), indent=1),
                                       encoding="utf-8")
    from .data import N, SECTOR_SHORT
    L = ["# POST HOC (not adopted): the complex mean of the six healthy meshes as the reference", "",
         "| target | variant | stage (P) | stage ok | lobes called | wrong lobes | fit |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        calls = ", ".join(SECTOR_SHORT[k].split()[0] for k in range(N) if r["calls"][k]) or "none"
        L.append(f"| {r['target']} | {r['variant']} | {r['stage']} ({r['P_stage']:.2f}) | {'yes' if r['stage_ok'] else '**no**'} | "
                 f"{calls} | {r['wrong_lobes']} | {r['fit']:.2f} |")
    (OUT3 / "meanref.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return rows


# ---------------------------------------------------------------- which affected lobes miss their interval (R11 detail)
def coverage_detail():
    """Reproduces nullrulers.coverage_three_ways (same samples, same exclusions, same runs) and lists every affected
    lobe whose 90% interval misses the truth, for each of the three ways. Post hoc diagnostic."""
    from . import lodo as LO
    from .data import DESIGNS, N
    from .noise import smooth
    from .nullrulers import TARGETS, available
    PH.register()
    rot = available()
    base = {"H7/H6 (7 vs 6 passes)": PH.L("H7", "H6"), "Mild 5/6": PH.L("Mild5", "Mild6"),
            "Moderate 5/6": PH.L("Mod5", "Mod6"), "Severe 5/6": PH.L("Sev5", "Sev6"),
            "RightOnly/mirror(LeftOnly) (5 vs 6)": PH.L_mirror("RightOnly", "LeftOnly")}
    rots = {f"{r}/H6": PH.L(r, "H6") for r in rot}
    ways = {"all nulls": list(rots), "all without rot19": [k for k in rots if not k.startswith("rot19")],
            "rot19 alone": [k for k in rots if k.startswith("rot19")]}
    folds, out = {}, {}
    for wname, keys in ways.items():
        samples = {**base, **{k: rots[k] for k in keys}}
        misses, n_aff, n_cov = [], 0, 0
        for tag, g, key in TARGETS:
            if g not in folds:
                folds[g] = LO.fit_fold(g)
            fold = folds[g]
            smp = [v for k, v in samples.items() if k not in PH.EXCLUDE.get(tag, [])]
            F = smp[0].shape[1]
            vr, vi = np.zeros((4, F)), np.zeros((4, F))
            for t in range(4):
                sel = PATH_TYPE == t
                vr[t] = np.mean([np.mean(x[sel].real ** 2, 0) for x in smp], 0)
                vi[t] = np.mean([np.mean(x[sel].imag ** 2, 0) for x in smp], 0)
            s_re = np.sqrt(fold["s_re"] ** 2 + smooth(vr)[PATH_TYPE])
            s_im = np.sqrt(fold["s_im"] ** 2 + smooth(vi)[PATH_TYPE])
            ref = "H6" if key not in ("Mild6", "Mod6", "Sev6") else "H7"
            sm = PH.summarize_run(PH.posterior(fold, s_re, s_im), PH.L(key, ref))
            e_true = next(d for d in DESIGNS if d.file == PH.FILES[key]).truth.e if key != "H7" else np.zeros(N)
            for k, sec in enumerate(sm["sectors"]):
                if e_true[k] > 0:
                    n_aff += 1
                    ok = bool(sec["e_q05"] <= e_true[k] <= sec["e_q95"])
                    n_cov += ok
                    if not ok:
                        misses.append(dict(target=tag, sector=k + 1, e_true=float(e_true[k]), e_med=sec["e_median"],
                                           interval=[sec["e_q05"], sec["e_q95"]]))
        out[wname] = dict(affected=n_aff, covered=n_cov, misses=misses)
    (OUT3 / "coverage_detail.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for w, v in out.items():
        print(w, f"{v['covered']}/{v['affected']}", [(m["target"], f"S{m['sector']}", m["e_true"], m["e_med"], m["interval"]) for m in v["misses"]])
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["verify", "meanref", "coverage"])
    a = ap.parse_args()
    {"verify": verify, "meanref": meanref, "coverage": coverage_detail}[a.cmd]()
