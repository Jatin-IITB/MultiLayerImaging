"""I3 study: forward-model validation and targeted model-based nonlinear inversion.

Unknowns (9): gray / white / hippocampus outer radii, (eps_r, sigma) of gray, white and CSF.
Skin, fat, skull fixed (assumed values); hippocampus material tied to gray matter (flagged: it
is invisible anyway). Bounded physics ranges enforced by a sigmoid reparameterisation so that
unconstrained Levenberg-Marquardt (MINPACK) can be used:
    CSF thickness t_c = 83.5 - r_gray in (0.1, 40) mm, gray thickness in (0.5, 30) mm,
    r_hip / r_white in (0.02, 0.95), eps_r in (10, 80), sigma in (0.2, 8) S/m.
Data: ring-mode differences dS_k(f), k = 0..3, 20 MHz grid, whitened by the measurement-noise
std of the ring mean. Model: dS_k = c_k(f) [V_k(theta) - V_k(theta_Normal)].
"""
from __future__ import annotations

import dataclasses

import numpy as np
from scipy.optimize import least_squares

from .common import (PROFILES, HeadParams, R_CSF, noisy, pairs_at_distance, ring_modes)
from .forward import KernelRingModel, ant_to_port, ring_from_ant
from .study_i1 import detection_accuracy
from .study_i2 import ring_sigma

NAMES = ["r_gray", "r_white", "r_hip", "eps_gray", "sig_gray", "eps_white", "sig_white",
         "eps_csf", "sig_csf"]
UNITS = ["mm", "mm", "mm", "", "S/m", "", "S/m", "", "S/m"]


def theta_of(p: HeadParams) -> np.ndarray:
    return np.array([p.r_gray, p.r_white, p.r_hip, *p.gray, *p.white, *p.csf])


def params_of(th) -> HeadParams:
    return HeadParams(th[0], th[1], th[2], (th[3], th[4]), (th[5], th[6]), (th[7], th[8]),
                      (th[3], th[4]))


def _sg(u):
    return 1 / (1 + np.exp(-u))


def _lg(y):
    y = np.clip(y, 1e-9, 1 - 1e-9)
    return np.log(y / (1 - y))


def u_to_theta(u):
    tc = 0.1 + 39.9 * _sg(u[0])
    rg = R_CSF - tc
    rw = rg - (0.5 + 29.5 * _sg(u[1]))
    rh = rw * (0.02 + 0.93 * _sg(u[2]))
    e = lambda v: 10 + 70 * _sg(v)            # noqa: E731
    s = lambda v: 0.2 + 7.8 * _sg(v)          # noqa: E731
    return np.array([rg, rw, rh, e(u[3]), s(u[4]), e(u[5]), s(u[6]), e(u[7]), s(u[8])])


def theta_to_u(th):
    rg, rw, rh = th[:3]
    return np.array([_lg((R_CSF - rg - 0.1) / 39.9), _lg((rg - rw - 0.5) / 29.5),
                     _lg((rh / rw - 0.02) / 0.93),
                     _lg((th[3] - 10) / 70), _lg((th[4] - 0.2) / 7.8),
                     _lg((th[5] - 10) / 70), _lg((th[6] - 0.2) / 7.8),
                     _lg((th[7] - 10) / 70), _lg((th[8] - 0.2) / 7.8)])


class Problem:
    def __init__(self, model: KernelRingModel, f, cal, sig):
        """cal: (F, 4) complex c_k(f); sig: (F, 4) noise std of the data (HFSS units)."""
        self.m, self.f, self.cal, self.sig = model, f, cal, sig
        self.V0 = self.V(theta_of(HeadParams.stage("Normal")))

    def V(self, th):
        return ring_from_ant(self.m.scattered(params_of(th), self.f))

    def predict(self, th):
        return self.cal * (self.V(th) - self.V0)

    def resid_theta(self, th, d):
        r = (self.predict(th) - d) / (self.sig / np.sqrt(2))
        return np.r_[r.real.ravel(), r.imag.ravel()]

    def fit(self, d, starts, max_nfev=400):
        best = None
        for u0 in starts:
            try:
                sol = least_squares(lambda u: self.resid_theta(u_to_theta(u), d), u0,
                                    method="lm", max_nfev=max_nfev, x_scale=1.0)
            except Exception:                               # pragma: no cover
                continue
            if best is None or sol.cost < best.cost:
                best = sol
        th = u_to_theta(best.x)
        return th, 2 * best.cost, best

    def jac_theta(self, th, d, rel=1e-4):
        """Whitened residual Jacobian w.r.t. physical parameters (central differences)."""
        cols = []
        for i in range(len(th)):
            h = rel * max(abs(th[i]), 1.0)
            a, b = th.copy(), th.copy()
            a[i] += h
            b[i] -= h
            cols.append((self.resid_theta(a, d) - self.resid_theta(b, d)) / (2 * h))
        return np.array(cols).T


def identifiability(J, names=NAMES):
    """CRLB std, correlation matrix and Fisher eigen-structure from a whitened Jacobian."""
    Fm = J.T @ J
    try:
        C = np.linalg.inv(Fm)
    except np.linalg.LinAlgError:                           # pragma: no cover
        C = np.linalg.pinv(Fm)
    sd = np.sqrt(np.clip(np.diag(C), 0, None))
    corr = C / np.outer(sd, sd)
    # eigen-structure of the Fisher matrix in parameter units scaled by the prior range
    ev, evec = np.linalg.eigh(Fm)
    return dict(sd=sd, corr=corr, fisher_eig=ev, fisher_vec=evec, cond=float(ev.max() / max(ev.min(), 1e-300)))


RANGES = np.array([40.0, 30.0, 70.0, 70.0, 7.8, 70.0, 7.8, 70.0, 7.8])   # prior widths


def verdict(sd, corr, true_change):
    out = []
    for i, n in enumerate(NAMES):
        others = np.abs(np.delete(corr[i], i))
        tc = abs(true_change[i])
        if sd[i] > 0.5 * RANGES[i]:
            v = "not determined (CRLB > half the prior range)"
        elif tc > 0 and sd[i] > tc:
            v = "not resolved (CRLB > true change)"
        elif others.max(initial=0) > 0.95:
            v = f"degenerate (|corr| {others.max():.2f} with {NAMES[int(np.argmax(np.abs(np.where(np.arange(len(NAMES)) == i, 0, corr[i]))))]})"
        else:
            v = "determined"
        out.append(v)
    return out


# ----------------------------------------------------------------------------------------------
def validate(sd, f, log=print):
    """Polarisation choice (Normal only), n convergence, dS prediction error (calibrations)."""
    p2a = sd.port_to_ant
    fi = np.searchsorted(sd.f_hz, f)
    Sr = {s: ring_modes(sd.S[s], p2a)[fi] for s in sd.S}
    stages = [s for s in ("Mild", "Moderate", "Severe") if s in sd.S]
    out = {"pol": {}, "conv": [], "table": []}
    models = {}
    for pol in ("theta", "phi"):
        m = KernelRingModel("point", pol)
        models[pol] = m
        Vt = ring_from_ant(m.scattered(HeadParams.stage("Normal"), f) + m.direct(f))
        # Normal-only criterion: one common complex antenna factor a^2(f) for k = 1..3
        A, B = Vt[:, 1:], Sr["Normal"][:, 1:]
        w = 1 / np.mean(np.abs(B) ** 2, 0)
        a2 = np.sum(w * np.conj(A) * B, 1) / np.sum(w * np.abs(A) ** 2, 1)
        out["pol"][pol] = float(np.sqrt(np.sum(w * np.abs(a2[:, None] * A - B) ** 2)
                                        / np.sum(w * np.abs(B) ** 2)))
    pol = min(out["pol"], key=out["pol"].get)
    out["pol_chosen"] = pol
    model = models[pol]
    # convergence in the number of harmonics (Mild dV, ring modes)
    ref = None
    for nm in (150, 30, 50, 70, 90, 110, 130):
        mm = KernelRingModel("point", pol, nmax=nm)
        dv = ring_from_ant(mm.scattered(HeadParams.stage("Mild"), f)
                           - mm.scattered(HeadParams.stage("Normal"), f))
        if ref is None:
            ref = dv
            continue
        out["conv"].append(dict(nmax=nm, **{f"k{k}": float(np.linalg.norm(dv[:, k] - ref[:, k])
                                                          / np.linalg.norm(ref[:, k]))
                                           for k in range(4)}))
    # calibrations
    V = {s: ring_from_ant(model.scattered(HeadParams.stage(s), f)) for s in sd.S}
    Vt = V["Normal"] + ring_from_ant(model.direct(f))
    calA = Sr["Normal"] / Vt
    calA[:, 0] = calA[:, 1]
    dS = {s: Sr[s] - Sr["Normal"] for s in stages}
    dV = {s: V[s] - V["Normal"] for s in stages}
    w = 1 / np.mean(np.abs(dS["Mild"]) ** 2, 0)
    a2 = np.sum(w * np.conj(dV["Mild"]) * dS["Mild"], 1) / np.sum(w * np.abs(dV["Mild"]) ** 2, 1)
    calB = np.repeat(a2[:, None], 4, 1)
    for s in stages:
        for k in range(4):
            nrm = np.linalg.norm(dS[s][:, k])
            out["table"].append(dict(
                stage=s, k=k,
                calA_rel_err=float(np.linalg.norm(calA[:, k] * dV[s][:, k] - dS[s][:, k]) / nrm),
                calB_rel_err=float(np.linalg.norm(calB[:, k] * dV[s][:, k] - dS[s][:, k]) / nrm),
                shape_corr=float(np.abs(np.vdot(calA[:, k] * dV[s][:, k], dS[s][:, k]))
                                 / np.linalg.norm(calA[:, k] * dV[s][:, k]) / nrm),
                trivial_rel_err=(float(np.linalg.norm(dS["Mild"][:, k] - dS[s][:, k]) / nrm)
                                 if s != "Mild" else float("nan")),
                model_growth_vs_mild=float(np.linalg.norm(dV[s][:, k]) / np.linalg.norm(dV["Mild"][:, k])),
                hfss_growth_vs_mild=float(nrm / np.linalg.norm(dS["Mild"][:, k]))))
    out["calA"], out["calB"] = calA, calB
    # antenna-model variant (patch aperture) for the mismatch test
    patch = KernelRingModel("patch", pol)
    Vp = {s: ring_from_ant(patch.scattered(HeadParams.stage(s), f)) for s in ("Normal", "Mild")}
    dVp = Vp["Mild"] - Vp["Normal"]
    a2p = np.sum(w * np.conj(dVp) * dS["Mild"], 1) / np.sum(w * np.abs(dVp) ** 2, 1)
    out["patch"], out["calB_patch"] = patch, np.repeat(a2p[:, None], 4, 1)
    log(f"I3 validation: pol={pol} (Normal a^2 misfit {out['pol']})")
    return model, out


def _fit_task(prob, d, starts, max_nfev, with_jac):
    """One independent fit (module level so it can run in a worker process)."""
    th, chi2, _ = prob.fit(d, starts, max_nfev=max_nfev)
    if with_jac:
        return th, chi2, prob.jac_theta(th, d)
    return th


def run(sd, model, val, profile="typical", n_draw=20, n_starts=6, seed=3300, log=print,
        n_jobs=1, ck_dir=None):
    """n_jobs > 1 runs the independent fits in parallel worker processes (joblib); results
    are identical to the serial run (each fit is deterministic given its data and starts)."""
    f_all = sd.f_hz
    f = f_all[::4]
    fi = np.searchsorted(f_all, f)
    p2a = sd.port_to_ant
    prof = PROFILES[profile]
    sig = ring_sigma(sd.S["Normal"], p2a, prof)[fi]
    stages = [s for s in ("Mild", "Moderate", "Severe") if s in sd.S]
    th_true = {s: theta_of(HeadParams.stage(s)) for s in ["Normal"] + stages}
    rng = np.random.default_rng(seed)
    starts = [theta_to_u(th_true["Normal"])] + [rng.normal(0, 1.2, 9) for _ in range(n_starts - 1)]
    Sr = {s: ring_modes(sd.S[s], p2a)[fi] for s in sd.S}
    res = {"fits": [], "ident": {}, "classify": {}, "f": f}

    probA = Problem(model, f, val["calA"], sig)
    probB = Problem(model, f, val["calB"], sig)

    # every fit is checkpointed, so an interrupted run resumes where it stopped (data draws are
    # deterministic from the seeds; only fit results are stored)
    import pickle
    from .common import OUT
    ck_path = (ck_dir or OUT / "cache") / f"i3_checkpoint_n{n_draw}_s{n_starts}_seed{seed}.pkl"
    ck_path.parent.mkdir(parents=True, exist_ok=True)
    ck = pickle.loads(ck_path.read_bytes()) if ck_path.exists() else {}
    if ck:
        log(f"I3 resuming from checkpoint: {len(ck)} fits already done")

    def save():
        tmp = ck_path.with_suffix(".tmp")
        tmp.write_bytes(pickle.dumps(ck))
        tmp.replace(ck_path)

    def memo(key, fn):
        if key not in ck:
            ck[key] = fn()
            save()
        return ck[key]

    def prefetch(tasks):
        """tasks: [(key, prob, d, starts, max_nfev, with_jac)]; runs the missing ones, in
        parallel when n_jobs > 1, saving the checkpoint after every chunk."""
        todo = [t for t in tasks if t[0] not in ck]
        if not todo or n_jobs <= 1:
            return
        from joblib import Parallel, delayed
        chunk = 2 * n_jobs
        for i in range(0, len(todo), chunk):
            part = todo[i:i + chunk]
            out = Parallel(n_jobs=n_jobs)(delayed(_fit_task)(*t[1:]) for t in part)
            for t, o in zip(part, out):
                ck[t[0]] = o
            save()
            log(f"  I3 parallel: {min(i + chunk, len(todo))}/{len(todo)} fits of this batch done")

    def record(dataset, stage, prob, d, starts_):
        th, chi2, J = memo(("rec", dataset, stage),
                           lambda: _fit_task(prob, d, starts_, 400, True))
        idf = identifiability(J)
        row = dict(dataset=dataset, stage=stage, chi2_per_dof=float(chi2 / max(J.shape[0] - 9, 1)),
                   theta=th, sd=idf["sd"], truth=th_true.get(stage, th_true["Normal"]),
                   csf_thickness=float(R_CSF - th[0]), csf_thickness_sd=float(idf["sd"][0]))
        res["fits"].append(row)
        log(f"  I3 {dataset:28s} {stage:9s} chi2/dof {row['chi2_per_dof']:9.3g}  t_csf "
            f"{row['csf_thickness']:6.2f}±{row['csf_thickness_sd']:.2f} (true {R_CSF - row['truth'][0]:.2f})")
        return row

    recs = []                                  # (dataset, stage, prob, d), in report order
    # --- HFSS data: calibration A (brief: per ring distance from Normal) and B (Mild-tuned)
    for s in stages:
        d = Sr[s] - Sr["Normal"]
        recs.append(("HFSS calA (Normal cal.)", s, probA, d))
        recs.append(("HFSS calB (Mild-tuned a2)", s, probB, d))
    # noise-only (Normal draw - Normal draw), HFSS
    nz = noisy(f_all, sd.S["Normal"], profile, 1, seed)[0] - noisy(f_all, sd.S["Normal"], profile, 1, seed + 1)[0]
    recs.append(("HFSS calA (Normal cal.)", "noise-only", probA, ring_modes(nz, p2a)[fi]))

    # --- synthetic: model data (calibration B magnitudes) + measurement noise --------------
    kmat = sd.kmat

    def synth_S(stage, mdl, cal):
        dv = cal * (ring_from_ant(mdl.scattered(HeadParams.stage(stage), f_all))
                    - ring_from_ant(mdl.scattered(HeadParams.stage("Normal"), f_all)))
        return sd.S["Normal"] + dv[..., kmat]                    # (F, 6, 6) port order

    cal_full = np.repeat(np.interp(f_all, f, val["calB"][:, 0].real)[:, None]
                         + 1j * np.interp(f_all, f, val["calB"][:, 0].imag)[:, None], 4, 1)
    cal_full_p = np.repeat(np.interp(f_all, f, val["calB_patch"][:, 0].real)[:, None]
                           + 1j * np.interp(f_all, f, val["calB_patch"][:, 0].imag)[:, None], 4, 1)
    Ssyn = {s: synth_S(s, model, cal_full) for s in stages}
    Spat = {s: synth_S(s, val["patch"], cal_full_p) for s in stages}
    for s in stages:
        a = noisy(f_all, Ssyn[s], profile, 1, seed + 20)[0]
        b = noisy(f_all, sd.S["Normal"], profile, 1, seed + 21)[0]
        recs.append(("synthetic (same model)", s, probB, ring_modes(a - b, p2a)[fi]))
        a = noisy(f_all, Spat[s], profile, 1, seed + 30)[0]
        recs.append(("synthetic (patch antenna)", s, probB, ring_modes(a - b, p2a)[fi]))
    recs.append(("synthetic (same model)", "noise-only", probB, ring_modes(nz, p2a)[fi]))
    prefetch([(("rec", ds, st), pr, d, starts, 400, True) for ds, st, pr, d in recs])
    for ds, st, pr, d in recs:
        record(ds, st, pr, d, starts)

    # --- identifiability at the truth (CRLB, synthetic, noise-free Jacobian) ---------------
    for s in stages:
        d0 = probB.predict(th_true[s])
        idf = identifiability(probB.jac_theta(th_true[s], d0))
        change = th_true[s] - th_true["Normal"]
        res["ident"][s] = dict(sd=idf["sd"], corr=idf["corr"], cond=idf["cond"],
                               fisher_eig=idf["fisher_eig"], fisher_vec=idf["fisher_vec"],
                               change=change, verdict=verdict(idf["sd"], idf["corr"], change))
    log("I3 identifiability done")

    # --- classifier: recovered CSF thickness vs the k=3 scalar metric ----------------------
    k3 = pairs_at_distance(p2a, 3)

    def k3_metric(S):
        return float(10 * np.log10(np.mean([np.mean(np.abs(S[:, i, j]) ** 2) for i, j in k3])))

    start_draw = [theta_to_u(th_true["Normal"])]
    sets = (("HFSS", sd.S, probA), ("synthetic", {**Ssyn, "Normal": sd.S["Normal"]}, probB))
    groups = (("Normal_train", "Normal", 100), ("Normal_test", "Normal", 200),
              *[(st, st, 300 + 10 * i) for i, st in enumerate(stages)])
    draws = {}
    for dataset, Sset, prob in sets:
        for name, stage, s0 in groups:
            draws[(dataset, name)] = (noisy(f_all, Sset[stage], profile, n_draw, seed + s0),
                                      noisy(f_all, sd.S["Normal"], profile, n_draw, seed + s0 + 1))
    prefetch([(("cls", dataset, name, i_d), prob, ring_modes(a - b, p2a)[fi], start_draw, 150, False)
              for dataset, _, prob in sets for name, _, _ in groups
              for i_d, (a, b) in enumerate(zip(*draws[(dataset, name)]))])
    for dataset, Sset, prob in sets:
        feats = {}
        for name, stage, s0 in groups:
            A, B = draws[(dataset, name)]
            tc, m3 = [], []
            for i_d, (a, b) in enumerate(zip(A, B)):
                th = memo(("cls", dataset, name, i_d),
                          lambda: _fit_task(prob, ring_modes(a - b, p2a)[fi], start_draw, 150, False))
                tc.append(float(R_CSF - th[0]))
                m3.append(k3_metric(a))
            feats[name] = dict(t_csf=tc, k3_db=m3)
        test_pos = sum((feats[s]["t_csf"] for s in stages if s != "Mild"), [])
        acc_t = detection_accuracy(np.array(feats["Mild"]["t_csf"]), np.array(feats["Normal_train"]["t_csf"]),
                                   np.array(test_pos), np.array(feats["Normal_test"]["t_csf"]))
        # k3: lower power -> AD, so use the negative
        k3pos = sum((feats[s]["k3_db"] for s in stages if s != "Mild"), [])
        acc_k = detection_accuracy(-np.array(feats["Mild"]["k3_db"]), -np.array(feats["Normal_train"]["k3_db"]),
                                   -np.array(k3pos), -np.array(feats["Normal_test"]["k3_db"]))
        res["classify"][dataset] = dict(feats=feats, t_csf=acc_t, k3=acc_k)
        log(f"I3 classify {dataset}: t_csf bal.acc {acc_t['bal_acc']:.3f}, k3 bal.acc {acc_k['bal_acc']:.3f}")
    return res
