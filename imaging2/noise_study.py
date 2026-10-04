"""How the reconstructions degrade under measurement noise (numerical noise = the second mesh and
the other reference, see posteriors.json).

Conditions (applied to BOTH the baseline healthy scan and the follow-up scan, independently):
  typical      : shared instrument model 'typical' (0.25 dB, 2 deg, -70 dB floor, per entry and frequency)
  noisy        : shared model 'noisy' (0.5 dB, 5 deg, -60 dB floor)  [the brief's +-0.5 dB, +-5 deg]
  noisy+drift  : 'noisy' + per-port gain/phase drift between the two scans, U(+-0.5 dB) x U(+-5 deg),
                 constant over frequency; standard inversion (drift not modelled)
  noisy+drift, gain-free : same data; inversion projects out per-port log-gains (nuisance)
The likelihood adds the instrument's own log-ratio noise variance (estimated from noise-only draws,
i.e. known instrument specs, not the target). K realisations per target and condition.

    python -m imaging2.noise_study [--k 12]
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool

import numpy as np

from .data import CACHE, OUT, ROOT

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

TARGETS = [("Healthy_p7", "Healthy", "new_with_slices_Healthy_sliced.s6p"),
           ("Mild_p5", "Mild_lobe", "new_with_slices_Mild_lobe.s6p"),
           ("Moderate_p5", "Moderate_lobe", "new_with_slices_Moderate_lobe.s6p"),
           ("Severe_p5", "Severe_lobe", "new_with_slices_Severe_lobe.s6p"),
           ("LeftOnly_p6", "LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p"),
           ("MCI_p6", "MCI_lobe", "new_with_slices_MCI_lobe_c3.s6p")]
CONDS = [("typical", "typical", False, False), ("noisy", "noisy", False, False),
         ("noisy+drift", "noisy", True, False), ("noisy+drift gain-free", "noisy", True, True)]


def drift(S, rng, db=0.5, deg=5.0):
    g = 10 ** (rng.uniform(-db, db, 6) / 20) * np.exp(1j * np.radians(rng.uniform(-deg, deg, 6)))
    return S * g[None, :, None] * g[None, None, :]


def instrument_var(f, Sref, prof, n=40, seed=99):
    """Per-path variance of the log-ratio of two independent noisy scans of the same head."""
    from adstage.noise.model import PROFILES, realise
    from .data import log_ratio
    rng = np.random.default_rng(seed)
    a = realise(f, Sref, PROFILES[prof], n, rng)
    b = realise(f, Sref, PROFILES[prof], n, rng)
    L = np.stack([log_ratio(0.5 * (x + x.transpose(0, 2, 1)), 0.5 * (y + y.transpose(0, 2, 1))) for x, y in zip(a, b)])
    return L.real.var(0), L.imag.var(0)


def one_target(args):
    ti, tag, grp, fn, K, sweeps = args
    from adstage.noise.model import PROFILES, realise
    from . import invert as IV
    from . import lodo as LO
    from .data import load_file, log_ratio
    fold = LO.fit_fold(grp)
    d = next(x for x in LO.lobe_designs() if x.file == fn)
    f = fold["f"]
    S, Sref = load_file(fn)[1], load_file(d.ref)[1]
    rows, margs = [], {}
    for ci, (cname, prof, use_drift, gain_free) in enumerate(CONDS):
        vr, vi = instrument_var(f, Sref, prof)
        s_re = np.sqrt(fold["s_re"] ** 2 + vr)
        s_im = np.sqrt(fold["s_im"] ** 2 + vi)
        post = IV.Posterior(fold["sur"], s_re, s_im, fold["ell"], f, fold["cfg"][0], gain_free=gain_free)
        rng = np.random.default_rng(1000 + 17 * ci + 101 * ti)
        acc = np.zeros((len(IV.STAGES), 6, IV.N_CAND))
        for k in range(K):
            a = realise(f, S, PROFILES[prof], 1, rng)[0]
            b = realise(f, Sref, PROFILES[prof], 1, rng)[0]
            if use_drift:
                a = drift(a, rng)
            a, b = 0.5 * (a + a.transpose(0, 2, 1)), 0.5 * (b + b.transpose(0, 2, 1))
            L = log_ratio(a, b)
            res = post.run(L, n_sweep=sweeps, burn=sweeps // 4, seed=k)
            Ps, marg = IV.sector_marginals(res)
            acc += marg / K
            if k == 0:
                np.save(CACHE / f"marg_noise_{tag}_{ci}.npy", marg)
            sm = IV.summarize(Ps=Ps, marg=marg)
            pa = [s["P_affected"] for s in sm["sectors"]]
            em = [s["e_median"] for s in sm["sectors"]]
            rows.append(dict(target=tag, condition=cname, k=k, stage=max(sm["P_stage"], key=sm["P_stage"].get),
                             P_aff=[round(x, 3) for x in pa], e_med=em,
                             calls=[int(x > 0.5) for x in pa]))
        np.save(CACHE / f"marg_noisemean_{tag}_{ci}.npy", acc)
    return rows


def main(K=12, sweeps=300, procs=6):
    jobs = [(i, t, g, fn, K, sweeps) for i, (t, g, fn) in enumerate(TARGETS)]
    with Pool(procs) as pool:
        allrows = sum(pool.map(one_target, jobs), [])
    (OUT / "noise_study.json").write_text(json.dumps(dict(K=K, sweeps=sweeps, conditions=[c[0] for c in CONDS],
                                                          rows=allrows), indent=0))
    return allrows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=12)
    ap.add_argument("--sweeps", type=int, default=300)
    a = ap.parse_args()
    main(a.k, a.sweeps)
