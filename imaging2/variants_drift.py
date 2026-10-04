"""POST HOC: drift test of every inversion variant on identical noisy draws (for the hardware recommendation).

Conditions as in imaging2/noise_study.py: 'noisy' instrument model (0.5 dB, 5 deg, -60 dB floor) on both scans, plus a
per-port gain/phase drift U(+-0.5 dB) x U(+-5 deg) between baseline and follow-up. The same draws are used for every
variant (one rng per target). Variants: standard, gain-removing, ring-mean-phase, gain-removing + ring-mean-phase.

    python -m imaging2.variants_drift [--k 12]   -> results/imaging2/posthoc/variants_drift.json / .md
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from . import invert as IV
from . import posthoc as PH
from .data import OUT, N, SECTOR_SHORT

TARGETS = [("Healthy_p7", "Healthy", "H7"), ("Mild_p5", "Mild_lobe", "Mild5"), ("Moderate_p5", "Moderate_lobe", "Mod5"),
           ("Severe_p5", "Severe_lobe", "Sev5"), ("LeftOnly_p6", "LeftOnly", "LeftOnly"), ("MCI_p6", "MCI_lobe", "MCI"),
           ("RightOnly", "LeftOnly", "RightOnly"), ("Test_B", "__blind__", "Test_B")]
VARIANTS = ["standard", "gainfree", "ringphase", "gain+ring"]


class PosteriorGainRing(PH.PosteriorRingPhase):
    """Per-port log-gains projected out, then the ring-mean phase of every path class."""

    def project(self, R):
        return PH.PosteriorRingPhase.project(self, IV.Posterior.project(self, R))


def make_post(fold, s_re, s_im, var):
    args = (fold["sur"], s_re, s_im, fold["ell"], fold["f"], fold["cfg"][0])
    if var == "gain+ring":
        return PosteriorGainRing(*args)
    return PH.posterior(fold, s_re, s_im, var)


def _job(args):
    ti, tag, g, key, K, sweeps = args
    from adstage.noise.model import PROFILES, realise
    from . import lodo as LO
    from .data import log_ratio
    from .noise_study import drift, instrument_var
    from .nullrulers import truth_calls_stage
    PH.register()
    fold = LO.fit_fold(g)
    S, Sref = PH.S(key), PH.S("H6")
    vr, vi = instrument_var(fold["f"], Sref, "noisy")
    s_re, s_im = np.sqrt(fold["s_re"] ** 2 + vr), np.sqrt(fold["s_im"] ** 2 + vi)
    posts = {v: make_post(fold, s_re, s_im, v) for v in VARIANTS}
    rng = np.random.default_rng(5000 + 101 * ti)
    tc, ts = truth_calls_stage(key)
    rows = []
    for k in range(K):
        a = realise(fold["f"], S, PROFILES["noisy"], 1, rng)[0]
        b = realise(fold["f"], Sref, PROFILES["noisy"], 1, rng)[0]
        a = drift(a, rng)
        a, b = 0.5 * (a + a.transpose(0, 2, 1)), 0.5 * (b + b.transpose(0, 2, 1))
        L = log_ratio(a, b)
        for v, post in posts.items():
            res = post.run(L, n_sweep=sweeps, burn=sweeps // 4, seed=k)
            Ps, marg = IV.sector_marginals(res)
            sm = IV.summarize(Ps=Ps, marg=marg)
            calls = [int(s["P_affected"] > 0.5) for s in sm["sectors"]]
            stage = max(sm["P_stage"], key=sm["P_stage"].get)
            rows.append(dict(target=tag, variant=v, k=k, calls=calls, stage=stage, exact=calls == tc,
                             wrong_lobes=int(sum(x != y for x, y in zip(calls, tc))), stage_ok=stage == ts))
    return rows


def main(K=12, sweeps=300, procs=6):
    jobs = [(i, t, g, key, K, sweeps) for i, (t, g, key) in enumerate(TARGETS)]
    with Pool(procs) as pool:
        rows = sum(pool.map(_job, jobs), [])
    summ = {}
    for v in VARIANTS:
        summ[v] = {}
        for t, _, _ in TARGETS:
            rs = [r for r in rows if r["variant"] == v and r["target"] == t]
            summ[v][t] = dict(exact=float(np.mean([r["exact"] for r in rs])), stage_ok=float(np.mean([r["stage_ok"] for r in rs])),
                              wrong_lobes_per_draw=float(np.mean([r["wrong_lobes"] for r in rs])))
        rs = [r for r in rows if r["variant"] == v]
        summ[v]["ALL"] = dict(exact=float(np.mean([r["exact"] for r in rs])), stage_ok=float(np.mean([r["stage_ok"] for r in rs])),
                              wrong_lobes_per_draw=float(np.mean([r["wrong_lobes"] for r in rs])))
    out = dict(label="POST HOC drift test of every variant (identical draws)", K=K, sweeps=sweeps, summary=summ, rows=rows)
    (OUT / "posthoc" / "variants_drift.json").write_text(json.dumps(out, indent=0), encoding="utf-8")
    L = ["# POST HOC: noisy (0.5 dB, 5°) + per-port drift (±0.5 dB, ±5°), every variant on identical draws", "",
         f"K = {K} draws per target; cell = exact lobe pattern / stage correct / mean wrong lobes per draw.", "",
         "| target | " + " | ".join(VARIANTS) + " |", "|---|" + "---|" * len(VARIANTS)]
    for t in [t for t, _, _ in TARGETS] + ["ALL"]:
        L.append(f"| {t} | " + " | ".join(f"{summ[v][t]['exact']:.0%} / {summ[v][t]['stage_ok']:.0%} / "
                                          f"{summ[v][t]['wrong_lobes_per_draw']:.2f}" for v in VARIANTS) + " |")
    (OUT / "posthoc" / "variants_drift.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))




# ---------------------------------------------------------------- cross-reference table for gain+ring (post hoc)
def _xref_job(args):
    tag, fold_name, key, refs = args
    from . import lodo as LO
    from .nullrulers import truth_calls_stage
    PH.register()
    fold = LO.fit_fold(fold_name)
    tc, ts = truth_calls_stage(key)
    rows = []
    for ref in refs:
        if ref == key:
            continue
        sm = PH.short(PH.summarize_run(make_post(fold, fold["s_re"], fold["s_im"], "gain+ring"), PH.L(key, ref)))
        rows.append(dict(target=tag, reference=ref, variant="gain+ring", stage=sm["stage"], calls=sm["calls"],
                         wrong_lobes=int(sum(a != b for a, b in zip(sm["calls"], tc))), stage_ok=sm["stage"] == ts, fit=sm["fit"]))
    return rows


def xref(procs=6):
    from .nullrulers import TARGETS as NT, available
    refs = ["H6", "H7"] + available()
    jobs = [(t, g, k, refs) for t, g, k in NT] + [(r, "__blind__", r, refs) for r in available()]
    with Pool(procs) as pool:
        rows = sum(pool.map(_xref_job, jobs), [])
    (OUT / "posthoc" / "xref_gainring.json").write_text(json.dumps(rows, indent=0), encoding="utf-8")
    by = {}
    for r in rows:
        b = by.setdefault(r["reference"], [0, 0, 0])
        b[0] += r["wrong_lobes"]
        b[1] += int(not r["stage_ok"])
        b[2] += 1
    print("gain+ring cross-reference: runs", len(rows), "wrong lobes", sum(r["wrong_lobes"] for r in rows),
          "runs with wrong lobe", sum(r["wrong_lobes"] > 0 for r in rows), "wrong stage", sum(not r["stage_ok"] for r in rows),
          "by ref (wrong lobes / wrong stage / runs)", by)
    for r in rows:
        if r["wrong_lobes"] or not r["stage_ok"]:
            print("  ", r["target"], r["reference"], r["stage"], r["calls"], r["fit"])
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="drift", choices=["drift", "xref"])
    ap.add_argument("--k", type=int, default=12)
    a = ap.parse_args()
    if a.cmd == "drift":
        main(a.k)
    else:
        xref()
