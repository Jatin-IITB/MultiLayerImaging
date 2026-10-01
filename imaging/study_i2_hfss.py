"""I2 with the HFSS numerical Green's function (data/fields/, Normal design, 1 V incident).

Born sensitivity in absolute units (e^{+jwt}, peak phasors, incident wave a = V_inc / sqrt(Z0)):
    dS_ij(f) = -(j w eps0 / (4 a_i a_j)) * integral d eps(r) E_i(r) . E_j(r) dV
             = -(j w eps0 Z0 / (4 V_inc^2)) * integral ...          (all ports 1 V, 50 ohm)
d eps = d eps_r - j d sigma/(w eps0). A complex scale kappa(f) is still fitted on Mild (the brief);
kappa ~ 1 checks the absolute scale, |kappa - 1| measures the Born + field-sampling error.

Fields exist only at 3.4 / 3.6 / 3.8 GHz, so every Jacobian here has 3 frequency rows.
Radial (2 mm shells): fields trilinearly interpolated from the 3 mm grid onto a shell quadrature
(4 Gauss-Legendre radii x 500 directions). Voxel: the grid nodes themselves (no interpolation).
The wide T1 file (+-120 mm, 4 mm) shows the k = 3 path; E_T4 = R_180 E_T1 by the ring symmetry
(checked against the T4 export inside +-90 mm).
"""
from __future__ import annotations

import numpy as np

from .beamform import fibonacci_dirs, pair_signals
from .common import N_ANT, PROFILES, R_CSF, pairs_at_distance, ring_modes
from .fields import (FIELD_DIR, V_INC, WIDE_FILE, Z0, Grid, check_files, divergence_ratio,
                     hfss_fields_at, load_hfss_fields, locate_antennas, read_fld)
from .linear import TikhonovSVD, fista_l1, tv1d_irls
from .mie import EPS0
from .study_i2 import (F_C, SHELL_EDGES, SHELL_MID, _draw_stats, _err, _vox_profile, data_real,
                       pair_sigma_f, ring_sigma, shell_truth, to_real, voxel_truth)
from .timedomain import pair_list

Z_RING = 97.55 * np.cos(np.deg2rad(60.5))       # +48.0 mm (sign confirmed from the fields)


def born_abs(f):
    return -1j * 2 * np.pi * np.asarray(f) * EPS0 * Z0 / (4 * V_INC ** 2)


def rot180(E_grid):
    """Field of the opposite antenna by the ring symmetry: E'(x,y,z) = R E(-x,-y,z), R=diag(-1,-1,1)."""
    return E_grid[::-1, ::-1, :, :] * np.array([-1.0, -1.0, 1.0])


def _pairs_by_k(p2a, kmat):
    out = {k: [] for k in range(4)}
    for i in range(N_ANT):
        for j in range(N_ANT):
            out[kmat[i, j]].append((i, j))
    return out


def _sens_and_snr(Ep, f, kmat, sig_pair, kappa=None, dv=1e-6, deps=10.0):
    """Ep: (6 ports, F, P, 3). Returns relative sensitivity (4, P) and the SNR (5, P) of a
    1 cm^3 blob with |d eps| = 10; kappa=None -> absolute 1 V Born scale, else scaled by kappa(f)."""
    pre = born_abs(f) * (1.0 if kappa is None else np.asarray(kappa))
    sens = np.zeros((4, Ep.shape[2]))
    snr = np.zeros((5, Ep.shape[2]))
    for i in range(N_ANT):
        for j in range(N_ANT):
            sens[kmat[i, j]] += np.sum(np.abs(pre[:, None] * np.einsum("fpc,fpc->fp", Ep[i], Ep[j])), 0)
    for p_idx, (i, j) in enumerate(pair_list(N_ANT)):
        J = pre[:, None] * np.einsum("fpc,fpc->fp", Ep[i], Ep[j])
        snr[kmat[i, j]] += np.sum(np.abs(J * dv * deps / sig_pair[p_idx][:, None]) ** 2, 0)
    snr[4] = snr[:4].sum(0)
    return sens, np.sqrt(snr)


def run(sd, profile="typical", n_draw=30, seed=4400, log=print):
    res = {"field_source": "HFSS"}
    f_all, p2a, kmat = sd.f_hz, sd.port_to_ant, sd.kmat
    prof = PROFILES[profile]
    stages = [s for s in ("MCI", "Mild", "Moderate", "Severe") if s in sd.S]
    a_of_port = np.asarray(p2a) - 1

    # ---------------- checks ------------------------------------------------------------------
    res["checks"] = check_files()
    res["divergence"] = {n: divergence_ratio(FIELD_DIR / n)
                         for n in ("E_Normal_T1_3p6GHz.fld", "E_Normal_T4_3p4GHz.fld", WIDE_FILE)}
    fh, grids = load_hfss_fields()
    fi = np.array([int(np.argmin(np.abs(f_all - q))) for q in fh])
    if np.max(np.abs(f_all[fi] - fh)) > 1.0:
        raise ValueError(f"field frequencies {fh} not on the S-parameter grid")
    u_c, pol = locate_antennas(grids)
    az = np.arctan2(u_c[:, 1], u_c[:, 0])
    th0 = np.deg2rad(60.5)                       # feed polar angle (model card); the field
    u = np.stack([np.sin(th0) * np.cos(az), np.sin(th0) * np.sin(az),   # centroid sits at ~55 deg
                  np.full_like(az, np.cos(th0))], -1)
    res["antennas"] = [dict(T=t + 1, field_centroid_polar_deg=float(np.degrees(np.arccos(v[2]))),
                            azimuth_deg=float(np.degrees(np.arctan2(v[1], v[0]))), theta_fraction=float(p))
                       for t, (v, p) in enumerate(zip(u_c, pol))]
    P = grids[0][0].points()
    r_grid = np.linalg.norm(P, axis=-1)
    inside = r_grid < 88.0
    sym, amp = [], []
    for fi_, f in enumerate(fh):
        ref = np.sqrt(np.mean([np.mean(np.abs(grids[t][fi_].E[inside]) ** 2) for t in range(N_ANT)]))
        for t in range(N_ANT):
            amp.append(dict(f_GHz=f / 1e9, T=t + 1,
                            rms_rel_mean=float(np.sqrt(np.mean(np.abs(grids[t][fi_].E[inside]) ** 2)) / ref)))
        for a_, b_ in ((0, 3), (1, 4), (2, 5)):
            Ea, Eb = rot180(grids[a_][fi_].E), grids[b_][fi_].E
            sym.append(dict(f_GHz=f / 1e9, pair=f"T{b_ + 1} vs R180(T{a_ + 1})",
                            rel_rms_diff=float(np.sqrt(np.mean(np.abs(Eb[inside] - Ea[inside]) ** 2)
                                                       / np.mean(np.abs(Eb[inside]) ** 2)))))
    res["symmetry"], res["amplitude"] = sym, amp
    log("I2-HFSS: field checks done")

    # ---------------- radial Jacobian (2 mm shells), ring-mode rows ---------------------------
    xg, wg = np.polynomial.legendre.leggauss(4)
    dq = fibonacci_dirs(500)
    pk = _pairs_by_k(p2a, kmat)
    cols = []
    pre = born_abs(fh)
    for a_, b_ in zip(SHELL_EDGES[:-1], SHELL_EDGES[1:]):
        rr = 0.5 * (b_ - a_) * xg + 0.5 * (a_ + b_)
        wr = 0.5 * (b_ - a_) * wg
        pts = (rr[:, None, None] * dq[None]).reshape(-1, 3)
        wq = (wr[:, None] * rr[:, None] ** 2 * np.full(len(dq), 4 * np.pi / len(dq))[None]).ravel() * 1e-9
        Eq = hfss_fields_at(grids, pts)[a_of_port]                          # (6, 3, Q, 3)
        Eq = np.nan_to_num(Eq)
        Jk = np.zeros((3, 4), complex)
        for k in range(4):
            Jk[:, k] = np.mean([np.einsum("fqc,fqc,q->f", Eq[i], Eq[j], wq) for i, j in pk[k]], 0)
        cols.append(pre[:, None] * Jk)                                     # (3, 4) per unit d eps
    Jc_r = np.array([c.ravel() for c in cols]).T                            # rows f-major (f, k)
    Jc = np.concatenate([Jc_r, Jc_r * (-1j) * np.repeat(F_C / fh, 4)[:, None]], 1)
    xt = {s: shell_truth(s) for s in stages}
    Sr = {s: ring_modes(sd.S[s], p2a)[fi] for s in sd.S}
    dS = {s: Sr[s] - Sr["Normal"] for s in stages}
    born = {s: (Jc @ xt[s]).reshape(3, 4) for s in stages}
    sig_h = ring_sigma(sd.S["Normal"], p2a, prof)[fi]                       # (3, 4)
    wgt = 1 / sig_h ** 2
    kappa = np.sum(wgt * np.conj(born["Mild"]) * dS["Mild"], 1) / np.sum(wgt * np.abs(born["Mild"]) ** 2, 1)
    res["kappa"] = dict(f=fh, kappa=kappa)
    res["lin_err_hfss"] = {s: dict(
        abs_scale=[float(np.linalg.norm(born[s][:, k] - dS[s][:, k]) / np.linalg.norm(dS[s][:, k])) for k in range(4)],
        kappa_mild=[float(np.linalg.norm(kappa * born[s][:, k] - dS[s][:, k]) / np.linalg.norm(dS[s][:, k])) for k in range(4)],
        ratio_born_over_hfss=[float(np.linalg.norm(born[s][:, k]) / np.linalg.norm(dS[s][:, k])) for k in range(4)])
        for s in stages}
    sigp = pair_sigma_f(sd.S["Normal"], prof)[:, fi]                       # (21, 3)
    # ---------------- maps: ring plane z = +48 mm, vertical plane x = 0 (through T1 and T4) ----
    ax = grids[0][0].axes
    iz = int(np.argmin(np.abs(ax[2] - Z_RING)))
    ix = int(np.argmin(np.abs(ax[0] - 0.0)))
    res["maps"] = {}
    for name, sl, coords in (("ring", (slice(None), slice(None), iz), (0, 1)),
                             ("vertical", (ix, slice(None), slice(None)), (1, 2))):
        Pp = P[sl]
        m = np.linalg.norm(Pp, axis=-1) < 88.0
        Ep = np.stack([np.stack([grids[a_][k].E[sl][m] for k in range(3)]) for a_ in a_of_port])
        sens, snr = _sens_and_snr(Ep, fh, kmat, sigp)
        _, snr_k = _sens_and_snr(Ep, fh, kmat, sigp, kappa)
        res["maps"][name] = dict(u=ax[coords[0]], v=ax[coords[1]], mask=m, sens=sens, snr=snr, snr_kappa=snr_k,
                                 plane_value_mm=float(ax[2][iz] if name == "ring" else ax[0][ix]))
    r_prof = np.arange(1.0, 88.0, 2.0)
    dirs = fibonacci_dirs(150)
    prof_pts = (r_prof[:, None, None] * dirs[None]).reshape(-1, 3)
    Epr = hfss_fields_at(grids, prof_pts)[a_of_port]                         # ports
    sens, snr = _sens_and_snr(Epr, fh, kmat, sigp)
    _, snr_k = _sens_and_snr(Epr, fh, kmat, sigp, kappa)
    res["sens_radial"] = dict(r=r_prof, sens=sens.reshape(4, len(r_prof), -1).mean(-1))
    res["snr_radial"] = dict(r=r_prof, snr=snr.reshape(5, len(r_prof), -1),
                             snr_kappa=snr_k.reshape(5, len(r_prof), -1))
    w = r_prof ** 2
    sr = res["sens_radial"]["sens"]
    res["sens_fraction_core60"] = {f"k{k}": float(np.sum((w * sr[k])[r_prof < 60]) / np.sum(w * sr[k]))
                                   for k in range(4)}
    log("I2-HFSS: maps done")

    # whitened size (matched-filter SNR, 3 frequencies, ring modes) of the Born-predicted dS of
    # each stage's TRUE change vs the actual HFSS dS: does the simulated change explain the data?
    res["born_snr"] = {s: dict(pred_abs=float(np.linalg.norm(born[s] / sig_h)),
                               pred_kappa=float(np.linalg.norm(kappa[:, None] * born[s] / sig_h)),
                               hfss=float(np.linalg.norm(dS[s] / sig_h)))
                       for s in stages}
    sig_m = (sig_h / np.abs(kappa)[:, None]).ravel()
    Jr = to_real(Jc, sig_m)
    tik = TikhonovSVD(Jr)
    lams = np.logspace(-3, 3, 61) * tik.s[0] * 1e-2
    rng = np.random.default_rng(seed)
    nz = (rng.standard_normal((2, sig_m.size)) + 1j * rng.standard_normal((2, sig_m.size))) * sig_m / np.sqrt(2)
    datasets = {}
    for s in stages:
        datasets[f"synthetic-linear|{s}"] = Jc @ xt[s] + nz[0]
        datasets[f"HFSS|{s}"] = (dS[s] / kappa[:, None]).ravel()
    datasets["noise-only"] = nz[1]
    blocks = [np.arange(len(SHELL_MID)), len(SHELL_MID) + np.arange(len(SHELL_MID))]
    d_m = data_real(datasets["synthetic-linear|Mild"], sig_m)
    tv_grid = np.logspace(-2, 3, 11)
    lam_tv = float(tv_grid[int(np.argmin([np.linalg.norm(tv1d_irls(Jr, d_m, l, blocks) - xt["Mild"])
                                          for l in tv_grid]))])
    lam_gcv_mild = float(tik.pick(d_m, lams, "gcv"))
    rad = {"lam_tv": lam_tv, "lam_gcv_mild": lam_gcv_mild, "sol": {}, "err": {},
           "truth": xt, "r": SHELL_MID, "n_data_real": int(Jr.shape[0]), "n_unknowns": int(Jr.shape[1])}
    for key, d in datasets.items():
        dr = data_real(d, sig_m)
        lg, ll = tik.pick(dr, lams, "gcv"), tik.pick(dr, lams, "lcurve")
        sols = {"tikhonov-gcv": tik.solve(dr, lg), "tikhonov-lcurve": tik.solve(dr, ll),
                "tv": tv1d_irls(Jr, dr, lam_tv, blocks)}
        rad["sol"][key] = dict(sols, lam_gcv=float(lg), lam_lcurve=float(ll))
        st = key.split("|")[-1]
        if st in xt:
            rad["err"][key] = {k: _err(v, xt[st]) for k, v in sols.items()}
    Rm = tik.resolution(lam_gcv_mild)
    n = len(SHELL_MID)
    rad["resolution_diag"] = dict(eps_r=np.diag(Rm)[:n], eps_pp=np.diag(Rm)[n:])
    rad["singular_values"] = tik.s
    lam_det = tik.pick(data_real(datasets["HFSS|Mild"], sig_m), lams, "gcv")
    outer = np.r_[SHELL_MID >= 70, SHELL_MID >= 70]

    def stat_radial(dS_ring):
        x = tik.solve(data_real((dS_ring / kappa[:, None]).ravel(), sig_m), lam_det)
        return float(np.linalg.norm(x[outer]))
    rad["detect"] = _draw_stats(sd, profile, n_draw, seed, stages, fi, lambda S: ring_modes(S, p2a),
                                stat_radial)
    res["radial"] = rad
    log("I2-HFSS: radial inversions done")

    # ---------------- voxel problem (grid nodes, r < 83.5 mm) ---------------------------------
    Pf = P.reshape(-1, 3)
    keep = np.linalg.norm(Pf, axis=1) < R_CSF
    vox = Pf[keep]
    Ev = np.stack([np.stack([grids[a_][k].E.reshape(-1, 3)[keep] for k in range(3)]) for a_ in a_of_port])
    dv = (grids[0][0].step * 1e-3) ** 3
    rows = [born_abs(fh)[k] * dv * np.einsum("pc,pc->p", Ev[i, k], Ev[j, k])
            for k in range(3) for i, j in pair_list(N_ANT)]
    Jv = np.array(rows)
    Jv = np.concatenate([Jv, Jv * (-1j) * np.repeat(F_C / fh, 21)[:, None]], 1)
    del Ev
    xv = {s: voxel_truth(s, vox) for s in stages}
    sigp_v = sigp                                                             # (21, 3)
    pred = (Jv @ xv["Mild"]).reshape(3, 21)
    obs = pair_signals(sd.dS("Mild")[fi]).T
    w_ = 1 / sigp_v.T ** 2
    kap_f = np.sum(w_ * np.conj(pred) * obs, 1) / np.sum(w_ * np.abs(pred) ** 2, 1)
    res["kappa_voxel"] = dict(f=fh, kappa=kap_f)
    kap_v = np.repeat(kap_f, 21)
    sig_v = sigp_v.T.ravel() / np.abs(kap_v)
    Jvr = to_real(Jv, sig_v)
    tv_ = TikhonovSVD(Jvr)
    Lv = float(tv_.s[0] ** 2)
    lams_v = np.logspace(-4, 2, 61) * tv_.s[0]
    rng2 = np.random.default_rng(seed + 7)
    nvx = (rng2.standard_normal((2, sig_v.size)) + 1j * rng2.standard_normal((2, sig_v.size))) * sig_v / np.sqrt(2)
    vdata = {}
    for s in stages:
        vdata[f"synthetic-linear|{s}"] = Jv @ xv[s] + nvx[0]
        vdata[f"HFSS|{s}"] = pair_signals(sd.dS(s)[fi]).T.ravel() / kap_v
    vdata["noise-only"] = nvx[1]
    dmv = data_real(vdata["synthetic-linear|Mild"], sig_v)
    l1_grid = np.logspace(-3, 0, 7) * np.abs(Jvr.T @ dmv).max()
    lam_l1 = float(l1_grid[int(np.argmin([np.linalg.norm(fista_l1(Jvr, dmv, l, 150, L=Lv) - xv["Mild"])
                                          for l in l1_grid]))])
    vx = {"n_vox": int(len(vox)), "lam_l1": lam_l1, "sol": {}, "err": {}, "prof": {},
          "singular_values": tv_.s, "vox": vox, "n_data_real": int(Jvr.shape[0])}
    rv = np.linalg.norm(vox, axis=1)
    for key, d in vdata.items():
        dr = data_real(d, sig_v)
        lg = tv_.pick(dr, lams_v, "gcv")
        sols = {"tikhonov-gcv": tv_.solve(dr, lg), "l1": fista_l1(Jvr, dr, lam_l1, 300, L=Lv)}
        vx["sol"][key] = sols
        vx["prof"][key] = {k: _vox_profile(v, rv, len(vox)) for k, v in sols.items()}
        st = key.split("|")[-1]
        if st in xv:
            vx["err"][key] = {k: _err(v, xv[st]) for k, v in sols.items()}
    vx["truth_prof"] = {s: _vox_profile(xv[s], rv, len(vox)) for s in stages}
    # PSFs along the feed direction of T1 (from the fields)
    lam_psf = tv_.pick(dmv, lams_v, "gcv")
    u1 = u[0]
    psf = []
    for rr in (20.0, 40.0, 60.0, 70.0, 80.0):
        j = int(np.argmin(np.linalg.norm(vox - rr * u1, axis=1)))
        e = np.zeros(2 * len(vox))
        e[j] = 1.0
        col = tv_.V @ (tv_.filter(lam_psf) * (tv_.V.T @ e))
        c = np.abs(col[:len(vox)])
        half = vox[c >= 0.5 * c.max()]
        psf.append(dict(r_mm=rr, voxel_mm=np.round(vox[j], 1).tolist(), diag=float(col[j]),
                        peak_at_mm=np.round(vox[int(np.argmax(c))], 1).tolist(),
                        peak_offset_mm=float(np.linalg.norm(vox[int(np.argmax(c))] - vox[j])),
                        n_vox_above_half=int(len(half))))
    vx["psf"] = psf
    lam_det_v = tv_.pick(data_real(vdata["HFSS|Mild"], sig_v), lams_v, "gcv")
    outer_v = np.r_[rv >= 70, rv >= 70]

    def stat_vox(dS_full):
        d = pair_signals(dS_full[fi]).T.ravel() / kap_v
        x = tv_.solve(data_real(d, sig_v), lam_det_v)
        return float(np.sqrt(np.mean(x[outer_v] ** 2)))
    vx["detect"] = _draw_stats(sd, profile, n_draw, seed + 50, stages, None, None, stat_vox)
    res["voxel"] = vx
    log("I2-HFSS: voxel inversions done")

    # ---------------- k = 3 path from the wide T1 export --------------------------------------
    gw = Grid(*read_fld(FIELD_DIR / WIDE_FILE))
    E1 = gw.E
    E4 = rot180(E1)
    Pw = gw.points()
    rw = np.linalg.norm(Pw, axis=-1)
    prod = np.abs(np.einsum("xyzc,xyzc->xyz", E1, E4))
    # check the symmetry assumption against the real T4 export (3.6 GHz) on the common nodes
    g4 = grids[3][1]
    Pc = g4.points().reshape(-1, 3)
    m_c = np.all(np.isin(np.round(Pc, 6), np.round(gw.axes[0], 6)), axis=1) & (np.linalg.norm(Pc, axis=1) < 88)
    E4w = Grid(Pw.reshape(-1, 3), E4.reshape(-1, 3)).sample(Pc[m_c])
    E4h = g4.E.reshape(-1, 3)[m_c]
    ok = np.all(np.isfinite(E4w), 1)
    sym_w = float(np.sqrt(np.mean(np.abs(E4w[ok] - E4h[ok]) ** 2) / np.mean(np.abs(E4h[ok]) ** 2)))
    regions = {"brain r<83.5": rw < 83.5, "CSF/skull/fat/skin 83.5-88": (rw >= 83.5) & (rw < 88),
               "air gap 88-97": (rw >= 88) & (rw < 97), "air r>=97 (incl. antennas)": rw >= 97}
    fin = np.isfinite(prod)
    tot = np.sum(prod[fin])
    frac = {k: float(np.sum(prod[m & fin]) / tot) for k, m in regions.items()}
    # inside the brain: depth distribution of the k = 3 product
    brain = (rw < 83.5) & fin
    depth_frac = {f"{lo}-{hi} mm": float(np.sum(prod[brain & (rw >= lo) & (rw < hi)]) / np.sum(prod[brain]))
                  for lo, hi in ((0, 40), (40, 60), (60, 70), (70, 78), (78, 83.5))}
    # field magnitude along two T1 -> T4 routes (3.6 GHz): straight chord and the arc over the
    # top (great circle through +z) just outside the skin (r = 91 mm)
    uT1, uT4 = u[0], u[3]
    a1, a4 = 97.55 * uT1, 97.55 * uT4
    tch = np.linspace(0, 1, 61)
    chord = a1[None] + tch[:, None] * (a4 - a1)[None]
    ang = np.arccos(np.clip(uT1 @ uT4, -1, 1))
    nrm = np.cross(uT1, uT4)
    nrm /= np.linalg.norm(nrm)
    arc = np.array([91.0 * (np.cos(t) * uT1 + np.sin(t) * np.cross(nrm, uT1)) for t in tch * ang])
    gwg = Grid(Pw.reshape(-1, 3), E1.reshape(-1, 3))
    m_chord = np.linalg.norm(gwg.sample(chord), axis=1)
    m_arc = np.linalg.norm(gwg.sample(arc), axis=1)
    ref = np.nanmax(m_arc[:5])
    res["k3_path"] = dict(
        grid=dict(axes=gw.axes, step=gw.step), sym_check_rel_rms=sym_w, region_fraction=frac,
        brain_depth_fraction=depth_frac, t=tch, sep_deg=float(np.degrees(ang)),
        chord_dB=20 * np.log10(m_chord / ref), arc_dB=20 * np.log10(m_arc / ref),
        chord_r=np.linalg.norm(chord, axis=1),
        plane_x0=dict(u=gw.axes[1], v=gw.axes[2],
                      E1=np.linalg.norm(E1[int(np.argmin(np.abs(gw.axes[0])))], axis=-1),
                      prod=prod[int(np.argmin(np.abs(gw.axes[0])))]),
        plane_ring=dict(u=gw.axes[0], v=gw.axes[1],
                        E1=np.linalg.norm(E1[:, :, int(np.argmin(np.abs(gw.axes[2] - Z_RING)))], axis=-1),
                        prod=prod[:, :, int(np.argmin(np.abs(gw.axes[2] - Z_RING)))],
                        z_mm=float(gw.axes[2][int(np.argmin(np.abs(gw.axes[2] - Z_RING)))])))
    log("I2-HFSS: k=3 path done")
    return res
