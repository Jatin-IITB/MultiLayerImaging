"""Run every leave-one-design-out inversion and the controls; write posteriors.

    python -m imaging2.run_lobe2 [--sweeps 400]

Outputs: results/imaging2/posteriors.json (summaries, stage probabilities, goodness of fit,
selected model per fold) and results/imaging2/cache/marg_<tag>.npy (joint P(stage, x_k)).
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np

from . import invert as IV
from . import lodo as LO
from .data import CACHE, G, MIRROR, OUT, apply_group, git_rev

TARGETS = [  # (tag, group, file, reference or None = matched)
    ("Healthy_p7", "Healthy", "new_with_slices_Healthy_sliced.s6p", None),
    ("Mild_p5", "Mild_lobe", "new_with_slices_Mild_lobe.s6p", None),
    ("Mild_p6", "Mild_lobe", "new_with_slices_Mild_lobe_new.s6p", None),
    ("Moderate_p5", "Moderate_lobe", "new_with_slices_Moderate_lobe.s6p", None),
    ("Moderate_p6", "Moderate_lobe", "new_with_slices_Moderate_lobe_c3.s6p", None),
    ("Severe_p5", "Severe_lobe", "new_with_slices_Severe_lobe.s6p", None),
    ("Severe_p6", "Severe_lobe", "new_with_slices_Severe_lobe_c3.s6p", None),
    ("LeftOnly_p6", "LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p", None),
    ("MCI_p6", "MCI_lobe", "new_with_slices_MCI_lobe_c3.s6p", None),
]
CONTROLS = [  # (tag, group/fold, file, transform)
    ("LeftOnly_mirrored", "LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p", "mirror"),
    ("LeftOnly_rot180", "LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p", "rot3"),
    ("Mild_p6_shuffled", "Mild_lobe", "new_with_slices_Mild_lobe_new.s6p", "shuffle"),
    ("LeftOnly_vsH7", "LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p", "refH7"),
]


def transform(L, how, seed=0):
    if how == "mirror":
        return apply_group(L, MIRROR)
    if how == "rot3":
        return apply_group(L, G[3])
    if how == "shuffle":                       # random relabelling of the 21 paths (breaks physics)
        rng = np.random.default_rng(seed)
        return L[rng.permutation(L.shape[0])]
    return L


def main(sweeps=400):
    from .data import H7, DESIGNS
    t0 = time.time()
    out = dict(code=git_rev(), sweeps=sweeps, folds={}, targets={})
    folds = {}
    for tag, grp, fn, ref in TARGETS + [(c[0], c[1], c[2], None) for c in CONTROLS]:
        if grp not in folds:
            fold = LO.fit_fold(grp, verbose=True)
            fold["post"] = IV.Posterior(fold["sur"], fold["s_re"], fold["s_im"], fold["ell"], fold["f"], fold["cfg"][0])
            folds[grp] = fold
            out["folds"][grp] = dict(cfg=list(fold["cfg"]), ell=fold["ell"], train=fold["train_files"],
                                     inner_scores={f"{k[0]}/{k[1]:g}": v for k, v in fold["scores"].items()})
    for tag, grp, fn, how in [(t[0], t[1], t[2], None) for t in TARGETS] + CONTROLS:
        fold = folds[grp]
        d = next(x for x in LO.lobe_designs() if x.file == fn)
        L = LO.observation(d, H7 if how == "refH7" else None)
        L = transform(L, how)
        res = fold["post"].run(L, n_sweep=sweeps, burn=sweeps // 4)
        Ps, marg = IV.sector_marginals(res)
        np.save(CACHE / f"marg_{tag}.npy", marg)
        sm = IV.summarize(res)
        raw = IV.summarize(Ps=IV.sector_marginals(res["_raw"])[0], marg=IV.sector_marginals(res["_raw"])[1])             if "_raw" in res else None
        sm.update(group=grp, file=fn, transform=how, ref=(H7 if how == "refH7" else d.ref),
                  logZ={s: float(res[s]["logZ"]) for s in IV.STAGES},
                  gof=dict(chi2_per_dof=float(res["_gof_raw"]), tau=float(res["_tau"])), untempered=raw,
                  truth_e=d.truth.e.tolist(), truth_stage=d.truth.tissue_stage)
        out["targets"][tag] = sm
        print(f"{tag:20s} P_stage {[round(sm['P_stage'][s], 3) for s in IV.STAGES]} "
              f"P_aff {[round(s['P_affected'], 2) for s in sm['sectors']]} "
              f"e_med {[s['e_median'] for s in sm['sectors']]} gof {sm['gof']['chi2_per_dof']:.2f} tau {sm['gof']['tau']:.2f} "
              f"({time.time() - t0:.0f}s)", flush=True)
    # the prior alone, rendered like a target (what the method draws when the data say nothing)
    Ps, marg = IV.prior_marginals()
    np.save(CACHE / "marg_Prior_only.npy", marg)
    sm = IV.summarize(Ps=Ps, marg=marg)
    sm.update(group="none", file="new_with_slices_Healthy_sliced_new.s6p", transform="prior", ref=None,
              logZ={}, gof=dict(stage="-", chi2_per_dof=float("nan"), dof_eff=0.0), truth_e=[0.0] * 6,
              truth_stage="Healthy")
    out["targets"]["Prior_only"] = sm
    (OUT / "posteriors.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweeps", type=int, default=400)
    main(ap.parse_args().sweeps)
