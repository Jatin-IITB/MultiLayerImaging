"""Leave-one-design-out (LODO) folds with nested model selection.

For a target design X (both meshes left out):
  1. training groups T = every other lobe design (Healthy pair = zero-change example, MCI, ...);
  2. nested choice of (feature set, ridge lambda) by an inner LODO over T only;
  3. surrogate refitted on T; model-error samples = the inner held-out residuals;
  4. noise = mesh-pair ruler without X's own pair, plus model error (quadrature);
  5. frequency correlation length from the whitened inner residuals.
Nothing derived from X (data or truth) enters steps 1-5.
"""
from __future__ import annotations

import numpy as np

from . import noise as NO
from .data import DESIGNS, all_designs, freq, load_file, log_ratio
from .surrogate import SurrogateF, stack_features

CONFIGS = [(s, l) for s in ("tm0", "tm0_tm2", "tm0_te2_tm2") for l in (1e-3, 1e-2, 1e-1)]
_FEATS: dict = {}


def lobe_designs():
    all_designs()
    return [d for d in DESIGNS if d.project == "new_with_slices" and d.role != "reference"]


def observation(d, ref=None):
    return log_ratio(d.S, load_file(ref or d.ref)[1])


def feats(d, sset):
    key = (d.file, sset)
    if key not in _FEATS:
        _FEATS[key] = stack_features(d.truth, freq(), sset)
    return _FEATS[key]


def _chi(L, P, s_re, s_im):
    R = L - P
    return float(np.mean((R.real / s_re) ** 2 + (R.imag / s_im) ** 2) / 2)


def fit_fold(target_group, configs=CONFIGS, verbose=False, exclude=()):
    """exclude: further groups removed from training (leave-one-STAGE-out variant)."""
    des = lobe_designs()
    train = [d for d in des if d.group != target_group and d.group not in exclude]
    groups = sorted({d.group for d in train})
    s_re0, s_im0 = NO.noise_sd(exclude=(target_group, *exclude))
    w_re, w_im = 1 / s_re0 ** 2, 1 / s_im0 ** 2
    scores = {}
    resid = {}
    for cfg in configs:
        sset, lam = cfg
        chis, res = [], []
        for h in groups:
            tr = [d for d in train if d.group != h]
            te = [d for d in train if d.group == h]
            sur = SurrogateF(sset, lam).fit([feats(d, sset) for d in tr], [observation(d) for d in tr], w_re, w_im)
            for d in te:
                L = observation(d)
                P = sur.predict(feats(d, sset))
                chis.append(_chi(L, P, s_re0, s_im0))
                res.append(L - P)
        scores[cfg] = float(np.mean(chis))
        resid[cfg] = res
    best = min(scores, key=scores.get)
    sset, lam = best
    sur = SurrogateF(sset, lam).fit([feats(d, sset) for d in train], [observation(d) for d in train], w_re, w_im)
    s_re, s_im = NO.noise_sd(exclude=(target_group, *exclude), extra=resid[best])
    ell, _ = NO.corr_length(resid[best], s_re, s_im)
    if verbose:
        print(target_group, "selected", best, "inner chi2", {f"{k[0]}/{k[1]:g}": round(v, 2) for k, v in scores.items()},
              "ell", ell)
    return dict(sur=sur, s_re=s_re, s_im=s_im, ell=max(ell, 1), cfg=best, scores=scores,
                train_files=[d.file for d in train], f=freq())
