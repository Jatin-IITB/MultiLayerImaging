"""Physical test of the Track A ratio lead (R21 = C2/C1, R31 = C3/C1, R32 = C3/C2) with the
HFSS-field Born Jacobian.

Definitions (as scripts/04_likelihood.py / src/adstage/features/floor.py, clean data so no floor):
    P_t^k = mean over the band of |S(t+k, t)|^2 (ring order = T1..T6),
    C_k   = geometric mean over t of P_t^k,  R21 = C2/C1, R31 = C3/C1, R32 = C3/C2 (dB).
The HFSS fields exist at 3.4 / 3.6 / 3.8 GHz only, so every predicted quantity is a mean over those
3 frequencies and is compared with the HFSS value computed in exactly the same way ("HFSS@3f").
The full-band HFSS values (as Track A uses) are listed for reference.

Born model. The head and every change considered are spherically symmetric, so dS_ab(f) =
kappa(f) * sum_shell J_ab(shell, f) * d eps(shell, f), with J_ab(shell, f) =
-(j w eps0 Z0 / 4V^2) * integral_shell E_a . E_b dV evaluated on 0.25 mm shells (4 Gauss-Legendre
radii x n_dir directions; fields trilinearly interpolated from the 3 mm export grid, r <= 89.75 mm).
kappa(f) is fitted on Mild only (noise-weighted over the 21 reciprocal pairs).
Predicted powers use |S_Normal + dS_pred|^2 (the linear field change, exact power).
"""
from __future__ import annotations

import dataclasses

import numpy as np

from .beamform import fibonacci_dirs, pair_signals
from .common import (FIXED, N_ANT, PROFILES, HeadParams, R_CSF, R_FAT, R_SKIN, R_SKULL, ring_modes)
from .fields import FIELD_DIR, WIDE_FILE, Grid, hfss_fields_at, load_hfss_fields, read_fld
from .mie import EPS0
from .study_i2 import pair_sigma_f
from .study_i2_hfss import born_abs
from .timedomain import pair_list

PAIRS = pair_list(N_ANT)                       # reciprocal antenna pairs (a <= b), antenna order


# ----------------------------------------------------------------------------------------------
# permittivity profiles (HFSS convention eps_r - j sigma / (w eps0)), vacuum outside the skin
# ----------------------------------------------------------------------------------------------
def eps_c(p: HeadParams, r_mm, f_hz, scale=1.0, r_out=None):
    """Complex permittivity on radii r (mm) for head p; scale multiplies every radius."""
    r = np.asarray(r_mm, float)
    out = np.ones((len(np.atleast_1d(f_hz)), r.size), complex)
    w = 2 * np.pi * np.atleast_1d(f_hz)[:, None]
    inner = 0.0
    lay = p.layers() if r_out is None else r_out
    for (ro, e, s) in lay:
        ro *= scale
        sel = (r >= inner) & (r < ro)
        out[:, sel] = e - 1j * s / (w * EPS0)
        inner = ro
    return out


def _with(p: HeadParams, **kw) -> HeadParams:
    return dataclasses.replace(p, **kw)


def scenarios(stages):
    """name -> (head params, scale). Each scenario's d eps = eps(scenario) - eps(Normal)."""
    N = HeadParams.stage("Normal")
    sc = {}
    for s in stages:
        S = HeadParams.stage(s)
        sc[f"{s}"] = (S, 1.0)
        if s == "MCI":
            continue
        sc[f"{s} | material only"] = (_with(N, gray=S.gray, white=S.white, csf=S.csf, hip=S.hip), 1.0)
        sc[f"{s} | geometry only"] = (_with(S, gray=N.gray, white=N.white, csf=N.csf, hip=N.hip), 1.0)
        sc[f"{s} | CSF material only (Normal geometry)"] = (_with(N, csf=S.csf), 1.0)
    if "Severe" in stages:
        S = HeadParams.stage("Severe")
        for other in ("Mild", "Moderate", "Normal"):
            sc[f"Severe with {other} CSF material"] = (_with(S, csf=HeadParams.stage(other).csf), 1.0)
    sc["head scale +2 %"] = (N, 1.02)
    sc["head scale -2 %"] = (N, 0.98)
    return sc


def standoff_deps(f_hz, r_mid, delta_mm):
    """Antenna stand-off change as an air-shell change at the skin: +1 mm -> the outer 1 mm of
    the head becomes air; -1 mm -> a 1 mm skin shell is added outside the skin."""
    N = HeadParams.stage("Normal")
    e0 = eps_c(N, r_mid, f_hz)
    if delta_mm > 0:
        e1 = e0.copy()
        sel = (r_mid >= R_SKIN - delta_mm) & (r_mid < R_SKIN)
        e1[:, sel] = 1.0
    else:
        e1 = e0.copy()
        sel = (r_mid >= R_SKIN) & (r_mid < R_SKIN - delta_mm)
        es, ss = FIXED["skin"]
        e1[:, sel] = es - 1j * ss / (2 * np.pi * np.atleast_1d(f_hz)[:, None] * EPS0)
    return e1 - e0


# ----------------------------------------------------------------------------------------------
def ant_matrix(S_port, port_to_ant):
    """(F, N, N) port order -> antenna order T1..T6."""
    a2p = np.argsort(np.asarray(port_to_ant) - 1)
    return S_port[..., a2p[:, None], a2p[None, :]]


def ck_ratios(S_ant):
    """C1, C2, C3 and R21, R31, R32 in dB from antenna-order S (F, 6, 6) (mean over F)."""
    out = {}
    idx = np.arange(N_ANT)
    for k in (1, 2, 3):
        P = np.mean(np.abs(S_ant[:, (idx + k) % N_ANT, idx]) ** 2, 0)      # (6,)
        out[f"C{k}"] = float(10 * np.log10(np.exp(np.mean(np.log(P)))))
    out["R21"] = out["C2"] - out["C1"]
    out["R31"] = out["C3"] - out["C1"]
    out["R32"] = out["C3"] - out["C2"]
    return out


def shell_jacobian(grids, fh, a_of_ant=None, dr=0.25, r_max=89.75, n_dir=300, chunk=30, log=print):
    """J (21 pairs, F, n_shell) complex, shell mid radii (mm). Antenna order = file T#."""
    edges = np.arange(0.0, r_max + 1e-9, dr)
    mids = 0.5 * (edges[1:] + edges[:-1])
    xg, wg = np.polynomial.legendre.leggauss(4)
    dq = fibonacci_dirs(n_dir)
    pre = born_abs(fh)
    J = np.zeros((len(PAIRS), len(fh), len(mids)), complex)
    for c0 in range(0, len(mids), chunk):
        sl = slice(c0, min(c0 + chunk, len(mids)))
        pts, wts, sid = [], [], []
        for si in range(sl.start, sl.stop):
            a_, b_ = edges[si], edges[si + 1]
            rr = 0.5 * (b_ - a_) * xg + 0.5 * (a_ + b_)
            wr = 0.5 * (b_ - a_) * wg
            pts.append((rr[:, None, None] * dq[None]).reshape(-1, 3))
            wts.append((wr[:, None] * rr[:, None] ** 2 * np.full(len(dq), 4 * np.pi / len(dq))[None]).ravel() * 1e-9)
            sid.append(np.full(len(rr) * len(dq), si - sl.start))
        pts, wts, sid = np.concatenate(pts), np.concatenate(wts), np.concatenate(sid)
        E = np.nan_to_num(hfss_fields_at(grids, pts))                      # (6, F, Q, 3)
        for p_i, (a, b) in enumerate(PAIRS):
            prod = np.einsum("fqc,fqc->fq", E[a], E[b]) * wts[None]
            for fi_ in range(len(fh)):
                J[p_i, fi_, sl] = pre[fi_] * np.bincount(sid, prod[fi_].real, sl.stop - sl.start) \
                    + 1j * pre[fi_] * np.bincount(sid, prod[fi_].imag, sl.stop - sl.start)
    log(f"ratio study: shell Jacobian {J.shape}")
    return J, mids


def run(sd, profile="typical", dr=0.25, n_dir=300, log=print):
    prof = PROFILES[profile]
    fh, grids = load_hfss_fields()
    f_all = sd.f_hz
    fi = np.array([int(np.argmin(np.abs(f_all - q))) for q in fh])
    stages = [s for s in ("MCI", "Mild", "Moderate", "Severe") if s in sd.S]
    p2a = sd.port_to_ant
    J, r_mid = shell_jacobian(grids, fh, dr=dr, n_dir=n_dir, log=log)
    N = HeadParams.stage("Normal")
    eN = eps_c(N, r_mid, fh)

    def dS_pred(deps, kappa):
        """(F, 6, 6) antenna-order predicted dS (symmetric) for d eps (F, n_shell)."""
        d = np.einsum("pfs,fs->pf", J, deps) * kappa[None, :]
        M = np.zeros((len(fh), N_ANT, N_ANT), complex)
        for p_i, (a, b) in enumerate(PAIRS):
            M[:, a, b] = M[:, b, a] = d[p_i]
        return M

    S_ant = {s: ant_matrix(sd.S[s][fi], p2a) for s in sd.S}
    # kappa(f) on Mild only: noise-weighted over the 21 reciprocal pairs
    sig = pair_sigma_f(ant_matrix(sd.S["Normal"], p2a), prof)[:, fi]        # (21, F) antenna-order pairs
    deps = {}
    for name, (p, scale) in scenarios(stages).items():
        deps[name] = eps_c(p, r_mid, fh, scale) - eN
    deps["stand-off +1 mm (outer 1 mm of head -> air)"] = standoff_deps(fh, r_mid, +1.0)
    deps["stand-off -1 mm (1 mm skin shell added)"] = standoff_deps(fh, r_mid, -1.0)
    one = np.ones(len(fh), complex)
    pred_mild = np.stack([dS_pred(deps["Mild"], one)[:, a, b] for a, b in PAIRS])     # (21, F)
    obs_mild = np.stack([0.5 * (S_ant["Mild"][:, a, b] + S_ant["Mild"][:, b, a]
                                - S_ant["Normal"][:, a, b] - S_ant["Normal"][:, b, a]) for a, b in PAIRS])
    w = 1 / sig ** 2
    kappa = np.sum(w * np.conj(pred_mild) * obs_mild, 0) / np.sum(w * np.abs(pred_mild) ** 2, 0)
    res = {"f": fh, "kappa": kappa, "dr_mm": dr, "n_dir": n_dir}

    ref_hf = ck_ratios(S_ant["Normal"])
    res["hfss3f"] = {s: {k: v - ref_hf[k] for k, v in ck_ratios(S_ant[s]).items()} for s in stages}
    res["hfss3f_abs"] = {s: ck_ratios(S_ant[s]) for s in sd.S}
    # full band (and Track A's 3.2-4.2 GHz) HFSS values for reference
    for tag, lo, hi in (("hfss_full", f_all[0], f_all[-1]), ("hfss_32_42", 3.2e9, 4.2e9)):
        sel = (f_all >= lo - 1) & (f_all <= hi + 1)
        Sb = {s: ant_matrix(sd.S[s][sel], p2a) for s in sd.S}
        rf = ck_ratios(Sb["Normal"])
        res[tag] = {s: {k: v - rf[k] for k, v in ck_ratios(Sb[s]).items()} for s in stages}
        res[tag + "_abs"] = {s: ck_ratios(Sb[s]) for s in sd.S}
    # predictions for every scenario (kappa from Mild, and absolute kappa = 1).
    # "pred": power of the linearly perturbed field |S + dS|^2; "pred_lin": first order in dS,
    # d ln P_t = mean_f 2 Re(S* dS) / P_t (exactly linear in d eps; the slope for the fragility tests)
    res["pred"], res["pred_abs"], res["pred_lin"], res["dS_norm"] = {}, {}, {}, {}
    idx_ = np.arange(N_ANT)

    def first_order(dS):
        out = {}
        for k in (1, 2, 3):
            S0 = S_ant["Normal"][:, (idx_ + k) % N_ANT, idx_]
            d = dS[:, (idx_ + k) % N_ANT, idx_]
            P = np.mean(np.abs(S0) ** 2, 0)
            out[f"C{k}"] = float(10 / np.log(10) * np.mean(np.mean(2 * np.real(np.conj(S0) * d), 0) / P))
        out["R21"], out["R31"], out["R32"] = out["C2"] - out["C1"], out["C3"] - out["C1"], out["C3"] - out["C2"]
        return out

    for name, de in deps.items():
        for key, kap in (("pred", kappa), ("pred_abs", one)):
            Sp = S_ant["Normal"] + dS_pred(de, kap)
            res[key][name] = {k: v - ref_hf[k] for k, v in ck_ratios(Sp).items()}
        res["pred_lin"][name] = first_order(dS_pred(de, kappa))
        d = np.stack([dS_pred(de, kappa)[:, a, b] for a, b in PAIRS])
        res["dS_norm"][name] = dict(norm=float(np.linalg.norm(d)), whitened=float(np.linalg.norm(d / sig)))
    # how much of the HFSS dS the linear model explains, per stage
    res["explained"] = {}
    for s in stages:
        d_p = np.stack([dS_pred(deps[s], kappa)[:, a, b] for a, b in PAIRS])
        d_o = np.stack([0.5 * (S_ant[s][:, a, b] + S_ant[s][:, b, a]
                               - S_ant["Normal"][:, a, b] - S_ant["Normal"][:, b, a]) for a, b in PAIRS])
        res["explained"][s] = dict(norm_ratio=float(np.linalg.norm(d_p) / np.linalg.norm(d_o)),
                                   rel_err=float(np.linalg.norm(d_p - d_o) / np.linalg.norm(d_o)))

    # ---- R21 / C_k sensitivity kernels on the shells (relative power change per unit d eps_r)
    idx = np.arange(N_ANT)
    pair_id = {(a, b): i for i, (a, b) in enumerate(PAIRS)}
    K = {}
    for k in (1, 2, 3):
        acc = np.zeros(len(r_mid))
        acc_c = np.zeros(len(r_mid), complex)
        for t in idx:
            a, b = sorted(((t + k) % N_ANT, t))
            Jp = J[pair_id[(a, b)]] * kappa[:, None]                           # (F, shell)
            Sab = S_ant["Normal"][:, (t + k) % N_ANT, t]
            P = np.mean(np.abs(Sab) ** 2)
            g = np.mean(2 * np.real(np.conj(Sab)[:, None] * Jp), 0) / P        # d ln P / d eps_r
            acc += g / N_ANT
            acc_c += np.mean(2 * np.real(np.conj(Sab)[:, None] * (-1j) * Jp), 0) / P / N_ANT
        K[f"C{k}"] = acc * 10 / np.log(10)                                      # dB per unit eps_r per shell
        K[f"C{k}_pp"] = np.real(acc_c) * 10 / np.log(10)                        # dB per unit eps''
    K["R21"] = K["C2"] - K["C1"]
    K["R21_pp"] = K["C2_pp"] - K["C1_pp"]
    res["kernel"] = dict(r=r_mid, **K)
    regions = {"white matter + hippocampus (<76)": (0, 76.0), "gray matter / cortex (76-83)": (76.0, 83.0),
               "CSF (83-83.5)": (83.0, R_CSF), "skull (83.5-86.5)": (R_CSF, R_SKULL),
               "fat + skin (86.5-88)": (R_SKULL, R_SKIN), "air gap (88-89.75)": (R_SKIN, 90.0)}
    res["kernel_regions"] = {
        q: {rg: float(np.sum(np.abs(K[q])[(r_mid >= lo) & (r_mid < hi)]) / np.sum(np.abs(K[q])))
            for rg, (lo, hi) in regions.items()} for q in ("C1", "C2", "C3", "R21")}
    log("ratio study: kernels done")

    # ---- full-space sensitivity of the k = 1 and k = 2 paths from the wide T1 export (3.6 GHz)
    gw = Grid(*read_fld(FIELD_DIR / WIDE_FILE))
    f36 = int(np.argmin(np.abs(fh - 3.6e9)))
    edges = np.arange(0.0, 118.0 + 1e-9, 0.5)
    mids = 0.5 * (edges[1:] + edges[:-1])
    dq = fibonacci_dirs(400)
    xg, wg = np.polynomial.legendre.leggauss(3)

    def rot(deg):
        c, s_ = np.cos(np.deg2rad(deg)), np.sin(np.deg2rad(deg))
        return np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1.0]])

    wide = {}
    for k in (1, 2, 3):
        Rk = rot(60.0 * k)                       # T(1+k) = T1 rotated by +60 k degrees
        Sab = S_ant["Normal"][f36, k, 0]
        prof_abs = np.zeros(len(mids))
        prof_sig = np.zeros(len(mids))
        for si in range(len(mids)):
            rr = 0.5 * (edges[si + 1] - edges[si]) * xg + mids[si]
            wr = 0.5 * (edges[si + 1] - edges[si]) * wg
            pts = (rr[:, None, None] * dq[None]).reshape(-1, 3)
            wq = (wr[:, None] * rr[:, None] ** 2 * np.full(len(dq), 4 * np.pi / len(dq))[None]).ravel() * 1e-9
            E1 = gw.sample(pts)
            Ek = gw.sample(pts @ Rk) @ Rk.T                                 # E_T1 rotated to T(1+k)
            ok = np.all(np.isfinite(E1), 1) & np.all(np.isfinite(Ek), 1)
            dens = born_abs(fh[f36]) * kappa[f36] * np.einsum("qc,qc->q", E1[ok], Ek[ok]) * wq[ok]
            g = 2 * np.real(np.conj(Sab) * dens) / np.abs(Sab) ** 2
            prof_abs[si] = np.sum(np.abs(g))
            prof_sig[si] = np.sum(g)
        wide[f"k{k}"] = dict(abs=prof_abs, signed=prof_sig)
    regions_w = dict(regions)
    regions_w.pop("air gap (88-89.75)")
    regions_w.update({"air gap (88-97)": (R_SKIN, 97.0), "air incl. antennas (97-118)": (97.0, 118.0)})
    res["wide"] = dict(r=mids, prof=wide, regions={
        f"k{k}": {rg: float(np.sum(wide[f"k{k}"]["abs"][(mids >= lo) & (mids < hi)]) / np.sum(wide[f"k{k}"]["abs"]))
                  for rg, (lo, hi) in regions_w.items()} for k in (1, 2, 3)})
    log("ratio study: wide-field regions done")

    # ---- MCI: Born dS of the hippocampal change vs the solve-to-solve difference (same 3 f)
    try:
        from adstage.config import load_config
        from .common import ROOT, load_stages
        sd1 = load_stages(load_config(ROOT, "imaging/configs/v1_archive.yaml"))
        i1 = np.array([int(np.argmin(np.abs(sd1.f_hz - q))) for q in fh])
        S1 = ant_matrix(sd1.S["Normal"][i1], p2a)
        d_solve = np.stack([0.5 * (S_ant["Normal"][:, a, b] + S_ant["Normal"][:, b, a]
                                   - S1[:, a, b] - S1[:, b, a]) for a, b in PAIRS])
        res["solve"] = dict(norm=float(np.linalg.norm(d_solve)), whitened=float(np.linalg.norm(d_solve / sig)),
                            ratios={k: v - ck_ratios(S1)[k] for k, v in ck_ratios(S_ant["Normal"]).items()})
        for nm in ("MCI", "Mild", "Severe"):
            if nm in deps:
                for key, kap in (("kappa", kappa), ("abs", one)):
                    d = np.stack([dS_pred(deps[nm], kap)[:, a, b] for a, b in PAIRS])
                    res["solve"][f"born_{nm}_{key}_over_solve"] = float(np.linalg.norm(d) / np.linalg.norm(d_solve))
    except Exception as e:                                                   # pragma: no cover
        res["solve"] = {"error": repr(e)}
    return res
