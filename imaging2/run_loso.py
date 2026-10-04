"""Leave-one-STAGE-out variant: Mild_lobe and LeftOnly share the Mild material table, so each is also
imaged with the other removed from training (no Mild-material design left). Moderate and Severe are
already leave-one-stage-out in the main run (no other design uses their materials).

    python -m imaging2.run_loso   -> results/imaging2/posteriors_loso.json, cache/marg_LOSO_<tag>.npy
"""
from __future__ import annotations

import json

import numpy as np

from . import invert as IV
from . import lodo as LO
from .data import CACHE, OUT, git_rev

RUNS = [("Mild_p5", "Mild_lobe", "new_with_slices_Mild_lobe.s6p", ("LeftOnly",)),
        ("Mild_p6", "Mild_lobe", "new_with_slices_Mild_lobe_new.s6p", ("LeftOnly",)),
        ("LeftOnly_p6", "LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p", ("Mild_lobe",))]


def main(sweeps=600):
    out = dict(code=git_rev(), sweeps=sweeps, targets={})
    folds = {}
    for tag, grp, fn, excl in RUNS:
        key = (grp, excl)
        if key not in folds:
            fold = LO.fit_fold(grp, verbose=True, exclude=excl)
            fold["post"] = IV.Posterior(fold["sur"], fold["s_re"], fold["s_im"], fold["ell"], fold["f"], fold["cfg"][0])
            folds[key] = fold
        fold = folds[key]
        d = next(x for x in LO.lobe_designs() if x.file == fn)
        res = fold["post"].run(LO.observation(d), n_sweep=sweeps, burn=sweeps // 4)
        Ps, marg = IV.sector_marginals(res)
        np.save(CACHE / f"marg_LOSO_{tag}.npy", marg)
        sm = IV.summarize(Ps=Ps, marg=marg)
        sm.update(file=fn, excluded=[grp, *excl], train=fold["train_files"], cfg=list(fold["cfg"]),
                  gof=dict(chi2_per_dof=float(res["_gof_raw"]), tau=float(res["_tau"])), truth_e=d.truth.e.tolist(),
                  transform=None)
        out["targets"][f"LOSO_{tag}"] = sm
        print(f"LOSO {tag:12s} P_stage {[round(sm['P_stage'][s], 3) for s in IV.STAGES]} "
              f"P_aff {[round(s['P_affected'], 2) for s in sm['sectors']]} e_med {[s['e_median'] for s in sm['sectors']]} "
              f"q05-95 {[(s['e_q05'], s['e_q95']) for s in sm['sectors']]} gof {sm['gof']['chi2_per_dof']:.2f}", flush=True)
    (OUT / "posteriors_loso.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
