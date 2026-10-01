"""I2 study: sensitivity maps and linearised inversions.

Field source: HFSS exports if data/fields/ is complete, otherwise the forward model's own
fields (layered sphere + tangential point dipoles), labelled SURROGATE everywhere.

Radial problem (b): unknowns d eps_r and d eps'' on 2 mm shells (r < 83.5 mm); columns are the
exact Frechet derivatives of the layered-sphere model (finite difference of the exact solution;
equal to the Born integral to ~1e-4, see tests). Voxel problem (a): 3 mm voxels, Born columns
J_ij = -j k0^3 E_i.E_j dV. Data are ring modes (radial) or reciprocal pairs (voxel), whitened
by the measurement-noise std; complex rows are split into real and imaginary parts.
"""
from __future__ import annotations

import numpy as np

from .beamform import fibonacci_dirs, pair_signals
from .common import N_ANT, PROFILES, HeadParams, R_CSF, noisy, ring_modes, true_delta
from .fields import fields_available, load_hfss_fields, model_fields
from .forward import KernelRingModel, ring_from_ant
from .linear import TikhonovSVD, born_prefactor, fista_l1, sigma_from_epp, tv1d_irls
from .mie import EPS0
from .timedomain import pair_list

F_C = 3.7e9
SHELL_EDGES = np.r_[np.arange(0.0, 83.0, 2.0), R_CSF]          # 42 shells, last 82-83.5
SHELL_MID = 0.5 * (SHELL_EDGES[1:] + SHELL_EDGES[:-1])


# ----------------------------------------------------------------------------------------------
# noise (measurement-noise model, HFSS units)
# ----------------------------------------------------------------------------------------------
def _entry_var(S, prof):
    sg = prof.sigma_db * np.log(10) / 20
    sp = np.deg2rad(prof.sigma_deg)
    return 2 * (np.abs(S) ** 2 * (sg ** 2 + sp ** 2) + 10 ** (prof.floor_db / 10))


def ring_sigma(S_ref, p2a, prof):
    """(F, 4) std of the ring-mode difference dS_k (mean over the n_k ordered pairs)."""
    from .common import pairs_at_distance
    v = _entry_var(S_ref, prof)
    out = []
    for k in range(4):
        pr = pairs_at_distance(p2a, k)
        out.append(np.sqrt(np.mean([v[:, i, j] for i, j in pr], 0) / len(pr)))
    return np.stack(out, -1)


def pair_sigma_f(S_ref, prof):
    """(21, F) std of the reciprocal-pair difference signals."""
    v = _entry_var(S_ref, prof)
    return np.stack([np.sqrt(v[:, i, j]) if i == j else 0.5 * np.sqrt(v[:, i, j] + v[:, j, i])
                     for i, j in pair_list(S_ref.shape[-1])])


# ----------------------------------------------------------------------------------------------
# truth on shells / voxels
# ----------------------------------------------------------------------------------------------
def shell_truth(stage):
    """[d eps_r ; d eps''_c] averaged over each shell (fine sampling)."""
    xr, xi = [], []
    for a, b in zip(SHELL_EDGES[:-1], SHELL_EDGES[1:]):
        r = np.linspace(a, b, 41)[:-1] + (b - a) / 80
        w = r ** 2
        de, ds = true_delta(stage, r)
        xr.append(np.sum(w * de) / w.sum())
        xi.append(np.sum(w * ds) / w.sum() / (2 * np.pi * F_C * EPS0))
    return np.r_[xr, xi]


def voxel_truth(stage, pts):
    de, ds = true_delta(stage, np.linalg.norm(pts, axis=1))
    return np.r_[de, ds / (2 * np.pi * F_C * EPS0)]


# ----------------------------------------------------------------------------------------------
# Jacobians
# ----------------------------------------------------------------------------------------------
def radial_jacobian(model: KernelRingModel, f, delta=1e-3):
    """Complex (F*4, 2*n_shell) ring-mode sensitivities (HFSS convention), rows f-major."""
    p = HeadParams.stage("Normal")
    V0 = ring_from_ant(model.scattered(p, f))
    cols_r, cols_i = [], []
    for a, b in zip(SHELL_EDGES[:-1], SHELL_EDGES[1:]):
        for de, cols in ((delta * np.ones(len(f)), cols_r), (1j * delta * F_C / f, cols_i)):
            V1 = ring_from_ant(model.scattered(p, f, extra_layers=[(a, b, de)]))
            cols.append(((V1 - V0) / delta).ravel())
    return np.array(cols_r + cols_i).T


def voxel_jacobian(E, f, dv_m3, port_to_ant):
    """Complex (F*21, 2*P) Born sensitivities from fields E (6 ant, F, P, 3); rows f-major,
    pairs = reciprocal port pairs (i <= j)."""
    a = np.asarray(port_to_ant) - 1
    pre = born_prefactor(f)
    rows = []
    for fi in range(len(f)):
        for i, j in pair_list(N_ANT):
            rows.append(pre[fi] * dv_m3 * np.einsum("pc,pc->p", E[a[i], fi], E[a[j], fi]))
    Jc = np.array(rows)
    return np.concatenate([Jc, Jc * (-1j) * (F_C / np.repeat(f, 21))[:, None]], 1)


def to_real(Jc, sig):
    """Whiten complex rows by sig (rows,) and split -> real (2 rows, cols)."""
    W = Jc / (sig / np.sqrt(2))[:, None]
    return np.concatenate([W.real, W.imag], 0)


def data_real(d, sig):
    w = d / (sig / np.sqrt(2))
    return np.r_[w.real, w.imag]


# ----------------------------------------------------------------------------------------------
# sensitivity maps
# ----------------------------------------------------------------------------------------------
def sensitivity(E, f, port_to_ant, kmat):
    """Sum over pairs at ring distance k and over f of |J_ij(r)| -> (4, P)."""
    a = np.asarray(port_to_ant) - 1
    pre = np.abs(born_prefactor(f))
    out = np.zeros((4, E.shape[2]))
    for i in range(N_ANT):
        for j in range(N_ANT):
            k = kmat[i, j]
            out[k] += np.einsum("f,fp->p", pre, np.abs(np.einsum("fpc,fpc->fp", E[a[i]], E[a[j]])))
    return out


def detectability(E, f, port_to_ant, kmat, kappa, sig_pair, dv=1e-6, deps=10.0):
    """SNR of a small blob (volume dv m^3, |d eps| = deps) at every point, from the reciprocal
    pairs at each ring distance k and in total: sqrt(sum_{pairs, f} |kappa J dv deps|^2 / sigma^2).
    Returns (5, P): k = 0..3 and total."""
    a = np.asarray(port_to_ant) - 1
    pre = born_prefactor(f)
    out = np.zeros((5, E.shape[2]))
    for p_idx, (i, j) in enumerate(pair_list(N_ANT)):
        k = kmat[i, j]
        J = pre[:, None] * np.einsum("fpc,fpc->fp", E[a[i]], E[a[j]])
        out[k] += np.sum(np.abs(kappa[:, None] * J * dv * deps / sig_pair[p_idx][:, None]) ** 2, 0)
    out[4] = out[:4].sum(0)
    return np.sqrt(out)


def block_test(model: KernelRingModel, f, radii=(20, 40, 55, 65, 75, 80, 82)):
    """Relative change of the TOTAL ring couplings when everything inside r_b is made a
    strong absorber (eps 40, sigma 40 S/m): how much of each path depends on the core."""
    p = HeadParams.stage("Normal")
    base = ring_from_ant(model.scattered(p, f) + model.direct(f))
    out = []
    for rb in radii:
        from .mie import eps_complex
        eps_in = HeadParams.stage("Normal")
        de = []
        # replace each background layer inside rb by the absorber: implemented as a perturbation
        # shell [0, rb] with d eps = eps_abs - eps_background (piecewise), layer by layer
        inner = 0.0
        for (ro, e, s) in eps_in.layers():
            a, b = inner, min(ro, rb)
            if b > a:
                de.append((a, b, eps_complex(40.0, 40.0, f) - eps_complex(e, s, f)))
            inner = ro
        V = ring_from_ant(model.scattered(p, f, extra_layers=de) + model.direct(f))
        out.append(dict(r_block_mm=rb, **{f"k{k}": float(np.linalg.norm(V[:, k] - base[:, k])
                                                      / np.linalg.norm(base[:, k]))
                                          for k in range(4)}))
    return out


# ----------------------------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------------------------
def run(sd, model: KernelRingModel, profile="typical", n_draw=30, seed=2200, log=print,
        vox_step=3.0, f_vox=(3.2e9, 3.4e9, 3.6e9, 3.8e9, 4.0e9, 4.2e9)):
    res = {}
    f_all = sd.f_hz
    f = f_all[::4]                                                  # 20 MHz for the radial fits
    fi = np.searchsorted(f_all, f)
    prof = PROFILES[profile]
    p2a, kmat = sd.port_to_ant, sd.kmat
    stages = [s for s in ("Mild", "Moderate", "Severe") if s in sd.S]
    hfss = False          # HFSS exports are handled by study_i2_hfss (this study = surrogate)
    res["field_source"] = "HFSS" if hfss else "SURROGATE (forward-model fields; data/fields absent)"
    log(f"I2 field source: {res['field_source']}")

    # ---------------- sensitivity maps (planes + radial) ------------------------------------
    f_map = np.array([3.4e9, 3.6e9, 3.8e9])
    z_ring = 97.55 * np.cos(np.deg2rad(60.5))
    u = np.arange(-90.0, 90.0 + 1e-9, 3.0)
    A, B = np.meshgrid(u, u, indexing="xy")
    planes = {"ring": np.stack([A, B, np.full_like(A, z_ring)], -1),
              "vertical": np.stack([A, np.zeros_like(A), B], -1)}
    r_prof = np.arange(1.0, 88.0, 2.0)
    dirs = fibonacci_dirs(150)
    prof_pts = (r_prof[:, None, None] * dirs[None]).reshape(-1, 3)
    if hfss:
        # HFSS exports: sample the export grid (nearest node) at the export frequencies
        from scipy.spatial import cKDTree
        fh, pts_h, Eh = load_hfss_fields()
        tree = cKDTree(pts_h)
        f_map = fh
        f_vox = tuple(fh)

        def get_fields(pts, freqs):
            _, idx = tree.query(pts)
            fi_ = [int(np.argmin(np.abs(fh - q))) for q in freqs]
            return Eh[:, fi_][:, :, idx]
    else:
        def get_fields(pts, freqs):
            return model_fields(model, HeadParams.stage("Normal"), np.asarray(freqs), pts)
    res["maps"] = {}
    E_maps = {}
    for name, P in planes.items():
        m = np.linalg.norm(P, axis=-1) < 88.0
        E = get_fields(P[m], f_map)
        E_maps[name] = E
        sens = sensitivity(E, f_map, p2a, kmat)
        res["maps"][name] = dict(u=u, mask=m, sens=sens)
    E = get_fields(prof_pts, f_map)
    E_maps["radial"] = E
    sens = sensitivity(E, f_map, p2a, kmat).reshape(4, len(r_prof), -1).mean(-1)
    res["sens_radial"] = dict(r=r_prof, sens=sens)
    log("I2 sensitivity maps done")
    # depth at which each k's sensitivity falls 20/40 dB below its maximum (radial profile)
    depth = {}
    for k in range(4):
        s = sens[k] / sens[k].max()
        rmax = r_prof[np.argmax(sens[k])]
        d = {}
        for lvl in (10, 20, 40):
            below = r_prof[(10 * np.log10(s) < -lvl) & (r_prof < rmax)]
            d[f"r_{lvl}dB"] = float(below.max()) if below.size else float("nan")
        depth[f"k{k}"] = dict(r_peak=float(rmax), **d)
    res["sens_depth"] = depth
    # fraction of k=3 sensitivity inside r < 60 mm vs the outer brain (volume-weighted)
    w = r_prof ** 2
    res["sens_fraction_core60"] = {f"k{k}": float(np.sum((w * sens[k])[r_prof < 60]) / np.sum(w * sens[k]))
                                   for k in range(4)}
    res["block"] = block_test(model, f)
    log("I2 block test done")

    # ---------------- radial problem --------------------------------------------------------
    Jc = radial_jacobian(model, f)                                   # rows (f, k)
    xt = {s: shell_truth(s) for s in stages}
    dV_lin = {s: (Jc @ xt[s]).reshape(len(f), 4) for s in stages}
    V0 = ring_from_ant(model.scattered(HeadParams.stage("Normal"), f))
    dV_ex = {s: ring_from_ant(model.scattered(HeadParams.stage(s), f)) - V0 for s in stages}
    res["lin_err_model"] = {s: [float(np.linalg.norm(dV_lin[s][:, k] - dV_ex[s][:, k])
                                      / np.linalg.norm(dV_ex[s][:, k])) for k in range(4)]
                            for s in stages}
    # kappa(f) calibration on Mild (HFSS dS vs Born prediction), noise-weighted over k
    Sr = {s: ring_modes(sd.S[s], p2a)[fi] for s in sd.S}
    dS = {s: Sr[s] - Sr["Normal"] for s in stages}
    sig_h = ring_sigma(sd.S["Normal"], p2a, prof)[fi]                # (F, 4) HFSS units
    wgt = 1 / sig_h ** 2
    m = dV_lin["Mild"]
    kappa = np.sum(wgt * np.conj(m) * dS["Mild"], 1) / np.sum(wgt * np.abs(m) ** 2, 1)
    res["kappa"] = dict(f=f, kappa=kappa)
    res["lin_err_hfss"] = {s: [float(np.linalg.norm(kappa * dV_lin[s][:, k] - dS[s][:, k])
                                     / np.linalg.norm(dS[s][:, k])) for k in range(4)]
                           for s in stages}
    sig_m = (sig_h / np.abs(kappa)[:, None]).ravel()                 # model units, (f, k)
    # detectability: SNR of a 1 cm^3 blob with |d eps| = 10 at each point, per ring distance and
    # total, using kappa (HFSS scale) and the per-pair measurement-noise std
    kap_map = kappa[np.searchsorted(f, f_map)]
    sigp = pair_sigma_f(sd.S["Normal"], prof)[:, np.searchsorted(f_all, f_map)]      # (21, Fm)
    for name, E in E_maps.items():
        snr = detectability(E, f_map, p2a, kmat, kap_map, sigp)
        if name == "radial":
            res["snr_radial"] = dict(r=r_prof, snr=snr.reshape(5, len(r_prof), -1))
        else:
            res["maps"][name]["snr"] = snr
    Jr = to_real(Jc, sig_m)
    tik = TikhonovSVD(Jr)
    lams = np.logspace(-3, 3, 61) * tik.s[0] * 1e-2
    rng = np.random.default_rng(seed)

    def cnoise(n):
        return (rng.standard_normal((n, sig_m.size)) + 1j * rng.standard_normal((n, sig_m.size))) \
            * sig_m / np.sqrt(2)

    datasets = {}
    nz = cnoise(3)
    for s in stages:
        datasets[f"synthetic-linear|{s}"] = dV_lin[s].ravel() + nz[0]
        datasets[f"synthetic-nonlinear|{s}"] = dV_ex[s].ravel() + nz[1]
        datasets[f"HFSS|{s}"] = (dS[s] / kappa[:, None]).ravel()
    datasets["noise-only"] = nz[2]
    # TV lambda tuned on Mild (synthetic-nonlinear, error vs truth), applied to all
    blocks = [np.arange(len(SHELL_MID)), len(SHELL_MID) + np.arange(len(SHELL_MID))]
    d_m = data_real(datasets["synthetic-nonlinear|Mild"], sig_m)
    tv_grid = np.logspace(-2, 3, 11)
    tv_err = [np.linalg.norm(tv1d_irls(Jr, d_m, l, blocks) - xt["Mild"]) for l in tv_grid]
    lam_tv = float(tv_grid[int(np.argmin(tv_err))])
    lam_gcv_mild = float(tik.pick(d_m, lams, "gcv"))
    res["radial"] = {"lam_tv": lam_tv, "lam_gcv_mild": lam_gcv_mild, "sol": {}, "err": {},
                     "truth": {s: xt[s] for s in stages}, "r": SHELL_MID}
    for key, d in datasets.items():
        dr = data_real(d, sig_m)
        lg = tik.pick(dr, lams, "gcv")
        ll = tik.pick(dr, lams, "lcurve")
        sols = {"tikhonov-gcv": tik.solve(dr, lg), "tikhonov-lcurve": tik.solve(dr, ll),
                "tv": tv1d_irls(Jr, dr, lam_tv, blocks)}
        res["radial"]["sol"][key] = {k: v for k, v in sols.items()}
        res["radial"]["sol"][key]["lam_gcv"] = float(lg)
        res["radial"]["sol"][key]["lam_lcurve"] = float(ll)
        st = key.split("|")[-1]
        if st in xt:
            res["radial"]["err"][key] = {k: _err(v, xt[st]) for k, v in sols.items()}
    # model-resolution matrix (whitened, lambda = GCV on Mild synthetic)
    Rm = tik.resolution(lam_gcv_mild)
    n = len(SHELL_MID)
    res["radial"]["resolution_diag"] = dict(eps_r=np.diag(Rm)[:n], eps_pp=np.diag(Rm)[n:])
    res["radial"]["resolution"] = Rm
    res["radial"]["singular_values"] = tik.s
    log("I2 radial inversions done")

    # detection statistic: norm of the recovered profile in 70-83.5 mm (Tikhonov, lambda fixed
    # = GCV on Mild HFSS), from noisy HFSS draws
    lam_det = tik.pick(data_real(datasets["HFSS|Mild"], sig_m), lams, "gcv")
    outer = np.r_[SHELL_MID >= 70, SHELL_MID >= 70]

    def stat_radial(dS_ring):
        x = tik.solve(data_real((dS_ring / kappa[:, None]).ravel(), sig_m), lam_det)
        return float(np.linalg.norm(x[outer]))
    res["radial"]["detect"] = _draw_stats(sd, profile, n_draw, seed, stages, fi,
                                          lambda S: ring_modes(S, p2a), stat_radial)

    # ---------------- voxel problem ---------------------------------------------------------
    f_vox = np.array(f_vox)
    g = np.arange(-90.0, 90.0 + 1e-9, vox_step)
    X, Y, Z = np.meshgrid(g, g, g, indexing="ij")
    P = np.stack([X, Y, Z], -1).reshape(-1, 3)
    keep = np.linalg.norm(P, axis=1) < R_CSF
    vox = P[keep]
    log(f"I2 voxel grid: {len(vox)} voxels, {len(f_vox)} freqs")
    Ev = get_fields(vox, f_vox)
    Jv = voxel_jacobian(Ev, f_vox, (vox_step * 1e-3) ** 3, p2a)
    del Ev
    kv_ = np.searchsorted(f_all, f_vox)
    sigp_v = pair_sigma_f(sd.S["Normal"], prof)[:, kv_]                  # (21, Fv) HFSS units
    xv = {s: voxel_truth(s, vox) for s in stages}
    # kappa(f) for this Jacobian, fitted on Mild (per frequency, noise-weighted over pairs):
    # with surrogate fields it reproduces the radial kappa; with HFSS fields it sets their scale
    pred = (Jv @ xv["Mild"]).reshape(len(f_vox), 21)
    obs = pair_signals(sd.dS("Mild")[kv_]).T                               # (Fv, 21)
    w_ = 1 / sigp_v.T ** 2
    kap_f = np.sum(w_ * np.conj(pred) * obs, 1) / np.sum(w_ * np.abs(pred) ** 2, 1)
    res["kappa_voxel"] = dict(f=f_vox, kappa=kap_f)
    kap_v = np.repeat(kap_f, 21)
    sig_v = sigp_v.T.ravel() / np.abs(kap_v)
    Jvr64 = to_real(Jv, sig_v)
    tv_ = TikhonovSVD(Jvr64)
    Lv = float(tv_.s[0] ** 2)
    lams_v = np.logspace(-4, 2, 61) * tv_.s[0]
    rng2 = np.random.default_rng(seed + 7)
    nvx = (rng2.standard_normal((2, sig_v.size)) + 1j * rng2.standard_normal((2, sig_v.size))) \
        * sig_v / np.sqrt(2)
    vdata = {}
    for s in stages:
        vdata[f"synthetic-linear|{s}"] = Jv @ xv[s] + nvx[0]
        dSp = pair_signals(sd.dS(s)[np.searchsorted(f_all, f_vox)])            # (21, Fv)
        vdata[f"HFSS|{s}"] = (dSp.T.ravel()) / kap_v
    vdata["noise-only"] = nvx[1]
    # L1 lambda tuned on Mild synthetic (error vs truth)
    dmv = data_real(vdata["synthetic-linear|Mild"], sig_v)
    l1_grid = np.logspace(-3, 0, 7) * np.abs(Jvr64.T @ dmv).max()
    l1_err = [np.linalg.norm(fista_l1(Jvr64, dmv, l, 150, L=Lv) - xv["Mild"]) for l in l1_grid]
    lam_l1 = float(l1_grid[int(np.argmin(l1_err))])
    res["voxel"] = {"n_vox": int(len(vox)), "lam_l1": lam_l1, "sol": {}, "err": {}, "prof": {},
                    "grid": g, "keep": keep, "singular_values": tv_.s}
    rv = np.linalg.norm(vox, axis=1)
    for key, d in vdata.items():
        dr = data_real(d, sig_v)
        lg = tv_.pick(dr, lams_v, "gcv")
        sols = {"tikhonov-gcv": tv_.solve(dr, lg), "l1": fista_l1(Jvr64, dr, lam_l1, 300, L=Lv)}
        res["voxel"]["sol"][key] = sols
        res["voxel"]["prof"][key] = {k: _vox_profile(v, rv, len(vox)) for k, v in sols.items()}
        st = key.split("|")[-1]
        if st in xv:
            res["voxel"]["err"][key] = {k: _err(v, xv[st]) for k, v in sols.items()}
    res["voxel"]["truth_prof"] = {s: _vox_profile(xv[s], rv, len(vox)) for s in stages}
    # point-spread functions along the ring-plane radius toward antenna T1 (azimuth 0)
    lam_psf = tv_.pick(dmv, lams_v, "gcv")
    psf = []
    for rr in (20.0, 40.0, 60.0, 70.0, 80.0):
        tgt = np.array([rr, 0.0, 0.0])
        j = int(np.argmin(np.linalg.norm(vox - tgt, axis=1)))
        e = np.zeros(2 * len(vox))
        e[j] = 1.0
        col = tv_.V @ (tv_.filter(lam_psf) * (tv_.V.T @ e))
        c = np.abs(col[:len(vox)])
        half = vox[c >= 0.5 * c.max()]
        psf.append(dict(r_mm=rr, diag=float(col[j]), peak_at_mm=vox[int(np.argmax(c))].tolist(),
                        n_vox_above_half=int(len(half)),
                        extent_mm=float(np.ptp(np.linalg.norm(half, axis=1))) if len(half) else 0.0))
    res["voxel"]["psf"] = psf
    # voxel detection statistic
    kv = np.searchsorted(f_all, f_vox)
    lam_det_v = tv_.pick(data_real(vdata["HFSS|Mild"], sig_v), lams_v, "gcv")
    outer_v = np.r_[rv >= 70, rv >= 70]

    def stat_vox(dS_full):
        d = pair_signals(dS_full[kv]).T.ravel() / kap_v
        x = tv_.solve(data_real(d, sig_v), lam_det_v)
        return float(np.sqrt(np.mean(x[outer_v] ** 2)))
    res["voxel"]["detect"] = _draw_stats(sd, profile, n_draw, seed + 50, stages, None, None,
                                         stat_vox)
    res["voxel"]["vox"] = vox
    log("I2 voxel inversions done")
    return res


def _err(x, xt):
    n = len(xt) // 2
    return dict(rel_err_eps_r=float(np.linalg.norm(x[:n] - xt[:n]) / np.linalg.norm(xt[:n])),
                rel_err_eps_pp=float(np.linalg.norm(x[n:] - xt[n:]) / np.linalg.norm(xt[n:])),
                corr_eps_r=float(np.corrcoef(x[:n], xt[:n])[0, 1]),
                corr_eps_pp=float(np.corrcoef(x[n:], xt[n:])[0, 1]))


def _vox_profile(x, rv, n):
    edges = np.arange(0.0, 84.0, 3.0)
    out = {"r": 0.5 * (edges[1:] + edges[:-1])}
    for name, v in (("eps_r", x[:n]), ("eps_pp", x[n:])):
        out[name] = np.array([v[(rv >= a) & (rv < b)].mean() if np.any((rv >= a) & (rv < b)) else np.nan
                              for a, b in zip(edges[:-1], edges[1:])])
    return out


def _draw_stats(sd, profile, n, seed, stages, fi, reduce, stat):
    """Statistic on noisy draws: Normal-vs-Normal (train/test) and each stage vs Normal."""
    def diffs(stage, s0):
        a = noisy(sd.f_hz, sd.S[stage], profile, n, s0)
        b = noisy(sd.f_hz, sd.S["Normal"], profile, n, s0 + 1)
        return a - b

    def apply(D):
        out = []
        for d in D:
            if reduce is not None:
                d = reduce(d)[fi]
            out.append(stat(d))
        return out
    res = {"noise": apply(diffs("Normal", seed)), "noise_test": apply(diffs("Normal", seed + 500))}
    for i, s in enumerate(stages):
        res[s] = apply(diffs(s, seed + 10 * (i + 1)))
    return res
