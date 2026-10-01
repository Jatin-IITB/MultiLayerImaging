"""I1 study: DAS / DMAS / MVDR images of dS = S_stage - S_Normal on HFSS data.

Tuning on Mild only: the antenna delay t_ant and the effective permittivity eps_eff are chosen
by the largest signal-to-clutter ratio (Mild image peak / mean noise-only image peak), a
criterion that does not use the true change location. Moderate and Severe are reported; MCI is
imaged as an extra stage (its detectability against the noise-only floor is reported).
"""
from __future__ import annotations

import numpy as np

from .beamform import Imager, pair_noise_sigma, pair_signals, plane_points, radial_points
from .common import PROFILES, HeadParams, noisy, port_positions_mm, true_delta

METHODS = ("DAS", "DMAS", "MVDR")
R_PROF = np.arange(1.0, 88.0, 2.0)


def _layers(mode, eps_eff):
    if mode == "eff":
        return [(88.0, eps_eff)]
    return [(r, e) for (r, e, s) in HeadParams.stage("Normal").layers()]


def noise_diffs(sd, profile, n, seed):
    """n noise-only difference tensors (Normal draw - independent Normal draw)."""
    a = noisy(sd.f_hz, sd.S["Normal"], profile, n, seed)
    b = noisy(sd.f_hz, sd.S["Normal"], profile, n, seed + 1)
    return a - b


def stage_diffs(sd, stage, profile, n, seed):
    a = noisy(sd.f_hz, sd.S[stage], profile, n, seed)
    b = noisy(sd.f_hz, sd.S["Normal"], profile, n, seed + 1)
    return a - b


def radial_profile(img, n_dir):
    return img.reshape(len(R_PROF), n_dir).mean(1)


def _tune_one(f, ppos, rpts, layers, mode, eps, ta, x_mild, noise_x6, n_dir):
    im = Imager(f, ppos, rpts, layers, t_ant_s=ta * 1e-9)
    rows = []
    for m in METHODS:
        img = im.image(m, x_mild)
        nz_pk = np.mean([im.image(m, x).max() for x in noise_x6])
        rows.append(dict(mode=mode, eps_eff=eps, t_ant_ns=ta, method=m,
                         scr_db=10 * np.log10(img.max() / nz_pk),
                         peak_r_mm=float(R_PROF[np.argmax(radial_profile(img, n_dir))])))
    return rows


def _report_one(f, ppos, rpts, planes, mode, m, b, stages, x_clean, x_draws, noise_x,
                noise_x_test, n_dir):
    """All reported quantities for one (delay model, method) with its Mild-tuned setting."""
    L = _layers(mode, b["eps_eff"])
    im = Imager(f, ppos, rpts, L, t_ant_s=b["t_ant_ns"] * 1e-9)
    nz_img = [im.image(m, x) for x in noise_x]
    nz_pk = np.array([v.max() for v in nz_img])
    nz_test = [float(im.image(m, x).max()) for x in noise_x_test]
    out = {"profiles": {"noise": np.mean([radial_profile(v, n_dir) for v in nz_img], 0).tolist()},
           "stages": {}, "detect": {}, "planes": {}}
    for s in stages:
        img = im.image(m, x_clean[s])
        pr = radial_profile(img, n_dir)
        out["profiles"][s] = pr.tolist()
        dr = np.array([im.image(m, x).max() for x in x_draws[s]])
        out["stages"][s] = dict(
            peak_r_mm=float(R_PROF[np.argmax(pr)]),
            scr_db=float(10 * np.log10(img.max() / nz_pk.mean())),
            scr_noisy_db=float(10 * np.log10(np.mean(dr) / nz_pk.mean())),
            frac_draws_above_noise_p95=float(np.mean(dr > np.quantile(nz_pk, 0.95))))
        out["detect"][s] = dict(stage=dr.tolist(), noise=nz_pk.tolist(), noise_test=nz_test)
    if mode == "layered":                      # plane images, layered delays only
        for pl, (pts, mask, u) in planes.items():
            imp = Imager(f, ppos, pts, L, t_ant_s=b["t_ant_ns"] * 1e-9)
            o = {"noise": imp.image(m, noise_x[0])}
            for s in stages:
                o[s] = imp.image(m, x_clean[s])
            out["planes"][pl] = dict(mask=mask, u=u, **o)
    return out


def run(sd, cfg, profile="typical", n_draw=20, n_dir=120, seed=1100, log=print, n_jobs=1):
    """n_jobs > 1: the tuning settings and the reported (delay model, method) combinations run
    in parallel worker processes (identical results)."""
    from joblib import Parallel, delayed
    f = sd.f_hz
    ppos = port_positions_mm(sd.port_to_ant)
    prof = PROFILES[profile]
    sig = pair_noise_sigma(sd.S["Normal"], prof)
    rpts = radial_points(R_PROF, n_dir)
    stages = [s for s in ("MCI", "Mild", "Moderate", "Severe") if s in sd.S]
    noise_x = [pair_signals(d, sig) for d in noise_diffs(sd, profile, n_draw, seed)]
    noise_x_test = [pair_signals(d, sig) for d in noise_diffs(sd, profile, n_draw, seed + 500)]
    x_clean = {s: pair_signals(sd.dS(s), sig) for s in stages}
    x_draws = {s: [pair_signals(d, sig) for d in stage_diffs(sd, s, profile, n_draw, seed + 10 + i)]
               for i, s in enumerate(stages)}
    par = Parallel(n_jobs=n_jobs)

    # ---- tuning on Mild (SCR criterion) ---------------------------------------------------
    t_grid = [0.0, 0.5, 1.0, 1.5, 2.0]
    e_grid = [20.0, 30.0, 40.0, 50.0]
    settings = [(mode, eps, ta) for mode in ("eff", "layered")
                for eps in (e_grid if mode == "eff" else [None]) for ta in t_grid]
    tune = sum(par(delayed(_tune_one)(f, ppos, rpts, _layers(mode, eps), mode, eps, ta,
                                      x_clean["Mild"], noise_x[:6], n_dir)
                   for mode, eps, ta in settings), [])
    best = {}
    for mode in ("eff", "layered"):
        for m in METHODS:
            c = [t for t in tune if t["mode"] == mode and t["method"] == m]
            best[(mode, m)] = max(c, key=lambda t: t["scr_db"])
    log(f"I1 tuning on Mild: {len(tune)} settings")

    # ---- report on all stages with the tuned settings --------------------------------------
    res = {"tune": tune, "best": {f"{k[0]}|{k[1]}": v for k, v in best.items()}, "stages": {},
           "profiles": {}, "planes": {}, "detect": {}, "stage_list": stages}
    z_ring = 97.55 * np.cos(np.deg2rad(60.5))
    planes = {pl: plane_points(pl, z_ring) for pl in ("ring", "vertical")}
    res["true_prof"] = {s: np.abs(true_delta(s, R_PROF)[0]).tolist() for s in stages}
    combos = [(mode, m) for mode in ("eff", "layered") for m in METHODS]
    outs = par(delayed(_report_one)(f, ppos, rpts, planes, mode, m, best[(mode, m)], stages,
                                    x_clean, x_draws, noise_x, noise_x_test, n_dir)
               for mode, m in combos)
    for (mode, m), o in zip(combos, outs):
        key = f"{mode}|{m}"
        res["profiles"][key] = o["profiles"]
        for s in stages:
            res["stages"][f"{key}|{s}"] = o["stages"][s]
            res["detect"][f"{key}|{s}"] = o["detect"][s]
        for pl, v in o["planes"].items():
            res["planes"][f"{pl}|{m}"] = v
    # peak radius vs t_ant (ambiguity demo; layered delays, DAS)
    amb = []
    for ta in np.arange(0.0, 3.01, 0.25):
        im = Imager(f, ppos, rpts, _layers("layered", None), t_ant_s=ta * 1e-9)
        row = {"t_ant_ns": float(ta)}
        for s in stages:
            row[s] = float(R_PROF[np.argmax(radial_profile(im.image("DAS", x_clean[s]), n_dir))])
        amb.append(row)
    res["t_ant_ambiguity"] = amb
    im = Imager(f, ppos, rpts[:5], _layers("layered", None))
    im.das(x_clean["Mild"])
    res["pulse_width_ns"] = float(im.pulse_ns)
    res["window_ns"] = float(im.win_ns)
    res["psf"] = point_psf(f, ppos)
    return res


def point_psf(f, ppos, eps=40.0):
    """Array point-spread test: ideal point scatterer (flat spectrum, homogeneous eps) at a few
    depths on the ring plane, along the direction of T1 (azimuth -90 deg, i.e. -y); -3 dB
    extents along x (azimuthal here), y (radial here) and z (elevation)."""
    from .timedomain import delay_layered
    lay = [(88.0, eps)]
    z0 = 97.55 * np.cos(np.deg2rad(60.5))
    out = []
    for r in (10.0, 30.0, 50.0, 65.0):
        tgt = np.array([0.0, -r, z0])
        tau = np.stack([delay_layered(a, tgt[None], lay)[0] for a in ppos])
        x = np.stack([np.exp(-2j * np.pi * f * (tau[i] + tau[j]))
                      for i in range(len(ppos)) for j in range(i, len(ppos))])
        g = np.arange(-60.0, 60.01, 2.0)
        for m in METHODS:
            prof = {}
            for ax in range(3):
                P = np.repeat(tgt[None], g.size, 0)
                P[:, ax] = tgt[ax] + g
                keep = np.linalg.norm(P, axis=1) < 88.0
                I = np.full(g.size, np.nan)
                I[keep] = Imager(f, ppos, P[keep], lay).image(m, x)
                I /= np.nanmax(I)
                above = g[I >= 0.5]
                prof["xyz"[ax]] = dict(peak_offset_mm=float(g[np.nanargmax(I)]),
                                       width_3dB_mm=float(above.max() - above.min() + 2.0))
            out.append(dict(r_mm=r, method=m, **{f"{k}_{q}": v[q] for k, v in prof.items() for q in v}))
    return out


def detection_accuracy(stat_train_pos, stat_train_neg, stat_test_pos, stat_test_neg):
    """Threshold (x > tau -> AD) tuned for balanced accuracy on train, applied to test."""
    cand = np.unique(np.concatenate([stat_train_pos, stat_train_neg]))
    best, tau = -1, None
    for c in cand:
        ba = 0.5 * (np.mean(stat_train_pos > c) + np.mean(stat_train_neg <= c))
        if ba > best:
            best, tau = ba, c
    sens = np.mean(np.asarray(stat_test_pos) > tau)
    spec = np.mean(np.asarray(stat_test_neg) <= tau)
    n_pos, n_neg = len(stat_test_pos), len(stat_test_neg)
    acc = (sens * n_pos + spec * n_neg) / (n_pos + n_neg)
    # macro F1 over the two classes
    tp, fn = sens * n_pos, (1 - sens) * n_pos
    tn, fp = spec * n_neg, (1 - spec) * n_neg
    f1p = 2 * tp / max(2 * tp + fp + fn, 1e-12)
    f1n = 2 * tn / max(2 * tn + fn + fp, 1e-12)
    return dict(tau=float(tau), sens=float(sens), spec=float(spec), acc=float(acc),
                bal_acc=float(0.5 * (sens + spec)), macro_f1=float(0.5 * (f1p + f1n)))
