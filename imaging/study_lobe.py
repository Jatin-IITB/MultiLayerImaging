"""Lobe-sector phantom (set lobe_v1): sector-level localisation with the HFSS-field Born kernels.

Data: data/raw/new_with_slices_<Design>.s6p (3.2-4.2 GHz), read directly (Touchstone parser +
glitch masking of the shared package), reference for every difference = Healthy_sliced.
Background fields: the v2 Normal design exports (data/fields). At e = 0 the sliced head is the
same head geometrically (the skull inner surface was set explicitly to 83.5 mm in the sliced
project, and the mesh differs); these fields are therefore an approximation of the sliced
background, stated in the report.

Every lobe change depends only on radius r and on the azimuth sector, so the Born product is
integrated over the polar angle once:
    P_ab(r_i, phi_j, f) = sum_theta E_a . E_b r^2 dr dOmega        (0.25 mm x 5 deg cells)
Any regional kernel or true d eps map is then a weighted sum over that (r, phi) table. All
interface radii of the designs and the sector edges (multiples of 60 deg) fall on cell edges.

Antenna order T1..T6 (file T#), azimuth -90 + 60 (t-1) deg; sector Sk spans
[-120 + 60 (k-1), -60 + 60 (k-1)] deg, centred on Tk. Port -> antenna map from config.
"""
from __future__ import annotations

import numpy as np

from .beamform import Imager, pair_signals, plane_points
from .common import MATS, N_ANT, PROFILES, ROOT, load_config
from .fields import hfss_fields_at, load_hfss_fields
from .mie import EPS0
from .study_i2 import pair_sigma_f
from .study_i2_hfss import born_abs
from .study_ratios import ant_matrix
from .timedomain import pair_list

PAIRS = pair_list(N_ANT)                         # (a <= b), antenna order T1..T6
LOBES = ["S1 frontal", "S2 temporal L", "S3 parietal L", "S4 occipital", "S5 parietal R", "S6 temporal R"]
SECT_AZ = np.array([-90.0 + 60 * k for k in range(N_ANT)])      # sector centre = antenna azimuth
F_C = 3.6e9
DESIGNS = {  # e_S1..e_S6 (mm), r_hip (mm), material stage
    "Healthy_sliced": ((0, 0, 0, 0, 0, 0), 25.0, "Normal"),
    "MCI_lobe": ((0, 0, 0, 0, 0, 0), 21.25, "MCI"),
    "Mild_lobe": ((0, 7.5, 11.5, 0, 11.5, 7.5), 17.5, "Mild"),
    "Moderate_lobe": ((11.5, 12.5, 15.5, 0, 15.5, 12.5), 12.5, "Moderate"),
    "Severe_lobe": ((15.5, 17.5, 18, 11.5, 18, 17.5), 7.5, "Severe"),
    "LeftOnly_test": ((0, 7.5, 11.5, 0, 0, 0), 17.5, "Mild"),
}
AVAILABLE = ("Healthy_sliced", "Mild_lobe", "Moderate_lobe", "Severe_lobe")
BLIND = ("LeftOnly_test", "MCI_lobe")
DR, DPHI, NTH = 0.25, 5.0, 64
R_EDGES = np.arange(0.0, 83.5 + 1e-9, DR)
R_MID = 0.5 * (R_EDGES[1:] + R_EDGES[:-1])
PHI_MID = np.arange(-180.0 + DPHI / 2, 180.0, DPHI)


def sector_of(phi_deg):
    return (np.floor((np.asarray(phi_deg) + 120.0) / 60.0).astype(int)) % N_ANT


SECT_OF_PHI = sector_of(PHI_MID)


def ring_k(a, b):
    d = abs(a - b) % N_ANT
    return min(d, N_ANT - d)


def pair_label(a, b):
    kind = {0: "reflection", 1: "neighbour", 2: "second-neighbour", 3: "opposite"}[ring_k(a, b)]
    return f"T{a + 1}" + (" refl." if a == b else f"–T{b + 1}") + f" ({kind})"


# ----------------------------------------------------------------------------------------------
# truth
# ----------------------------------------------------------------------------------------------
def _mat(stage, tissue):
    if stage == "MCI":
        return (40.3, 5.203) if tissue == "hip" else MATS["Normal"][tissue]
    return MATS[stage][tissue]


def eps_map(design, f_hz):
    """Complex eps (HFSS convention) on the (r, phi) table: (F, n_r, n_phi)."""
    e, r_hip, st = DESIGNS[design]
    w = 2 * np.pi * np.atleast_1d(f_hz)[:, None, None]
    er = np.zeros((len(R_MID), len(PHI_MID)))
    sg = np.zeros_like(er)
    r = R_MID[:, None]
    for k in range(N_ANT):
        cols = SECT_OF_PHI == k
        ek = e[k]
        aff = ek > 0
        gw = (_mat(st, "gray") if aff else MATS["Normal"]["gray"],
              _mat(st, "white") if aff else MATS["Normal"]["white"])
        csf = _mat(st, "csf")
        hip = _mat(st, "hip")
        layers = [(r_hip, hip), (25.0, csf), (76.0 - ek, gw[1]), (83.0 - ek, gw[0]), (83.5, csf)]
        inner = 0.0
        for ro, (ev, sv) in layers:
            sel = (r >= inner) & (r < ro)
            sel = np.broadcast_to(sel, er.shape) & cols[None, :]
            er[sel], sg[sel] = ev, sv
            inner = ro
    return er[None] - 1j * sg[None] / (w * EPS0)


def delta_map(design, f_hz):
    return eps_map(design, f_hz) - eps_map("Healthy_sliced", f_hz)


# ----------------------------------------------------------------------------------------------
# regions
# ----------------------------------------------------------------------------------------------
def region_masks(split=False):
    """dict name -> boolean (n_r, n_phi) mask. split: each sector shell -> gap 76-83.5 / deep 60-76."""
    out = {}
    r = R_MID[:, None]
    for k in range(N_ANT):
        cols = (SECT_OF_PHI == k)[None, :]
        if split:
            out[f"{LOBES[k]} gap"] = ((r >= 76.0) & (r < 83.5)) & cols
            out[f"{LOBES[k]} deep"] = ((r >= 60.0) & (r < 76.0)) & cols
        else:
            out[LOBES[k]] = ((r >= 70.0) & (r < 83.5)) & cols
    out["core"] = np.broadcast_to(r < 25.0, (len(R_MID), len(PHI_MID)))
    return out


# ----------------------------------------------------------------------------------------------
# Born table
# ----------------------------------------------------------------------------------------------
def born_table(grids, fh, chunk=12, log=print):
    """P (21 pairs, F, n_r, n_phi) complex: sum over theta of E_a.E_b dV (m^3) times born_abs(f)."""
    x, wx = np.polynomial.legendre.leggauss(NTH)            # cos(theta) nodes
    th = np.arccos(x)
    ph = np.deg2rad(PHI_MID)
    dphi = np.deg2rad(DPHI)
    pre = born_abs(fh)
    P = np.zeros((len(PAIRS), len(fh), len(R_MID), len(PHI_MID)), complex)
    TH, PH = np.meshgrid(th, ph, indexing="ij")             # (nth, nphi)
    W = np.broadcast_to(wx[:, None] * dphi, TH.shape)
    u = np.stack([np.sin(TH) * np.cos(PH), np.sin(TH) * np.sin(PH), np.cos(TH)], -1)   # (nth, nphi, 3)
    for c0 in range(0, len(R_MID), chunk):
        rs = R_MID[c0:c0 + chunk]
        pts = (rs[:, None, None, None] * u[None]).reshape(-1, 3)
        E = np.nan_to_num(hfss_fields_at(grids, pts))       # (6, F, Q, 3)
        E = E.reshape(N_ANT, len(fh), len(rs), len(th), len(ph), 3)
        dv = (rs ** 2 * DR)[:, None, None] * W[None] * 1e-9  # (nr, nth, nphi) m^3
        for p_i, (a, b) in enumerate(PAIRS):
            prod = np.einsum("frtpc,frtpc->frtp", E[a], E[b]) * dv[None]
            P[p_i, :, c0:c0 + len(rs)] = prod.sum(2) * pre[:, None, None]
    log(f"lobe: Born table {P.shape}")
    return P


def region_kernels(P, masks):
    """K (21, F, n_region) complex: response to a unit complex d eps uniform in each region."""
    return np.stack([np.einsum("pfrj,rj->pf", P, m.astype(float)) for m in masks.values()], -1)


def predict(P, deps, kappa):
    """dS (21, F) for a d eps map (F, n_r, n_phi)."""
    return np.einsum("pfrj,frj->pf", P, deps) * kappa[None, :]


# ----------------------------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------------------------
def load_design(name, f_ref=None, mask=True):
    """Antenna-order S (F, 6, 6) of a sliced design, glitch-masked, and f (Hz)."""
    from adstage.io.masking import mask_glitches
    from adstage.io.touchstone import read_touchstone
    cfg = load_config()
    t = read_touchstone(ROOT / "data" / "raw" / f"new_with_slices_{name}.s6p")
    s = mask_glitches(t.f_hz, t.s, float(cfg["qc"].get("glitch_thr_db", -30.0)))[0] if mask else t.s
    if f_ref is not None and (len(t.f_hz) != len(f_ref) or np.max(np.abs(t.f_hz - f_ref)) > 1):
        raise ValueError(f"{name}: frequency grid differs from the reference")
    return ant_matrix(s, cfg["ring"]["port_to_ant"]), t.f_hz


def recip(S):
    """(F, 6, 6) -> (21, F) reciprocal-pair values (S_ab + S_ba)/2, antenna order."""
    return np.stack([S[:, a, b] if a == b else 0.5 * (S[:, a, b] + S[:, b, a]) for a, b in PAIRS])


def mirror_perm():
    """x -> -x maps azimuth phi -> 180 - phi: T1<->T1, T4<->T4, T2<->T6, T3<->T5."""
    return np.array([0, 5, 4, 3, 2, 1])


def permute(S, perm):
    """S'(a, b) = S(perm[a], perm[b])."""
    return S[:, perm[:, None], perm[None, :]]


# ----------------------------------------------------------------------------------------------
# linear model for the regional unknowns
# ----------------------------------------------------------------------------------------------
class RegionModel:
    """Unknowns x = [d eps_r (n_reg), d eps''_c (n_reg)], d eps(f) = d eps_r - j d eps''_c (f_c/f).

    Data = 21 reciprocal pairs x F frequencies, complex. kind = 'dS' (difference data, whitened by
    the measurement-noise std) or 'log' (complex log-ratio ln S_stage - ln S_ref, projected onto the
    complement of the per-port, per-frequency complex gain subspace: gain-invariant)."""

    def __init__(self, K, fh, kappa, sig, S_ref=None, kind="dS"):
        self.fh, self.kind = np.asarray(fh), kind
        nreg = K.shape[-1]
        Kc = K * kappa[None, :, None]                               # (21, F, nreg)
        Kc = np.concatenate([Kc, -1j * Kc * (F_C / self.fh)[None, :, None]], -1)   # (21, F, 2 nreg)
        self.nreg = nreg
        if kind == "dS":
            self.w = 1 / (sig / np.sqrt(2))                          # (21, F)
            self.Jc = Kc * self.w[..., None]
            self.P = None
        else:
            Sr = recip(S_ref)                                        # (21, F) at the fit freqs
            self.Sr = Sr
            Jl = Kc / Sr[..., None]
            self.w = 1 / (sig / np.abs(Sr) / np.sqrt(2))
            self.Pg = self._gain_projector()
            self.Jc = np.stack([self.Pg @ (Jl[:, fi] * self.w[:, fi, None]) for fi in range(len(fh))], 1)
        self.J = np.concatenate([self.Jc.real.reshape(-1, 2 * nreg), self.Jc.imag.reshape(-1, 2 * nreg)], 0)

    def _gain_projector(self):
        A = np.zeros((len(PAIRS), N_ANT))
        for i, (a, b) in enumerate(PAIRS):
            A[i, a] += 1
            A[i, b] += 1
        return np.eye(len(PAIRS)) - A @ np.linalg.pinv(A)

    def data(self, dS=None, S_stage=None, S_ref=None):
        if self.kind == "dS":
            d = dS * self.w
        else:
            y = np.log(recip(S_stage)) - np.log(recip(S_ref))
            y = y - 2j * np.pi * np.round(np.imag(y) / (2 * np.pi))  # principal branch
            d = np.stack([self.Pg @ (y[:, fi] * self.w[:, fi]) for fi in range(len(self.fh))], 1)
        return np.r_[d.real.ravel(), d.imag.ravel()]

    def tikhonov(self, d, lam):
        A = self.J.T @ self.J + lam ** 2 * np.eye(self.J.shape[1])
        return np.linalg.solve(A, self.J.T @ d)

    def bounded(self, d, lam=0.0):
        """d eps'' >= 0 in every region (every AD material here has a higher conductivity than the
        healthy tissue it replaces); d eps_r is left free because the stage CSF permittivity is
        higher than healthy gray matter at Mild (55.25) and about equal at Moderate (48.75)."""
        from scipy.optimize import lsq_linear
        n = self.nreg
        lb = np.r_[np.full(n, -np.inf), np.zeros(n)]
        ub = np.r_[np.full(n, np.inf), np.full(n, np.inf)]
        if lam > 0:
            A = np.vstack([self.J, lam * np.eye(2 * n)])
            b = np.r_[d, np.zeros(2 * n)]
        else:
            A, b = self.J, d
        return lsq_linear(A, b, bounds=(lb, ub), method="bvls").x

    def gcv_lambda(self, d, lams):
        U, s, Vt = np.linalg.svd(self.J, full_matrices=False)
        b = U.T @ d
        r_perp = max(d @ d - b @ b, 0.0)
        g = []
        for lam in lams:
            fi = s ** 2 / (s ** 2 + lam ** 2)
            g.append((np.sum(((1 - fi) * b) ** 2) + r_perp) / (len(d) - fi.sum()) ** 2)
        return float(lams[int(np.argmin(g))])

    def crlb(self, gain_prior_db=None, S_ref=None, sig=None):
        """CRLB sd of the unknowns. gain_prior_db: per-port amplitude-gain nuisance (constant over f)
        with this prior sd, only for kind='dS' (needs S_ref)."""
        Fm = self.J.T @ self.J
        if gain_prior_db is None:
            C = np.linalg.pinv(Fm)
            return np.sqrt(np.clip(np.diag(C), 0, None))
        # dS gains: S_meas = g_a g_b S -> d dS / d ln g_t = (1 + [a == b]) S_ab for pairs touching t
        Sr = recip(S_ref)
        G = np.zeros((len(PAIRS), len(self.fh), N_ANT), complex)
        for i, (a, b) in enumerate(PAIRS):
            G[i, :, a] += Sr[i]
            G[i, :, b] += Sr[i]
        G = G * self.w[..., None]
        Gr = np.concatenate([G.real.reshape(-1, N_ANT), G.imag.reshape(-1, N_ANT)], 0)
        Ja = np.hstack([self.J, Gr])
        sg = gain_prior_db * np.log(10) / 20
        prior = np.zeros(Ja.shape[1])
        prior[self.J.shape[1]:] = 1 / sg ** 2
        C = np.linalg.pinv(Ja.T @ Ja + np.diag(prior))
        return np.sqrt(np.clip(np.diag(C)[:self.J.shape[1]], 0, None))


# ----------------------------------------------------------------------------------------------
# scoring helpers
# ----------------------------------------------------------------------------------------------
def truth_regions(design, f_hz, P, masks):
    """Sensitivity-weighted and volume-weighted region means of the true d eps_r and d eps''_c."""
    dm = delta_map(design, np.array([F_C]))[0]                   # complex at f_c
    wsens = np.abs(P).sum((0, 1))                                 # (n_r, n_phi)
    vol = (R_MID ** 2)[:, None] * np.ones(len(PHI_MID))[None]
    out = {}
    for key, wts in (("sens", wsens), ("vol", vol)):
        er, ep = [], []
        for m in masks.values():
            w_ = wts * m
            er.append(float(np.sum(w_ * dm.real) / np.sum(w_)))
            ep.append(float(np.sum(w_ * (-dm.imag)) / np.sum(w_)))
        out[key] = np.r_[er, ep]
    return out


def pattern_scores(x6, e_true, affected):
    """Pearson correlation of the recovered 6-sector change indicator (d eps'', conductivity
    increase: larger = more affected) with the true CSF expansion e_k; top-k accuracy of the
    affected set (k = number affected) using the largest values."""
    x6 = np.asarray(x6, float)
    e = np.asarray(e_true, float)
    corr = float(np.corrcoef(x6, e)[0, 1]) if np.std(e) > 0 and np.std(x6) > 0 else float("nan")
    k = int(np.sum(affected))
    if 0 < k < N_ANT:
        top = set(np.argsort(-x6)[:k])
        topk = len(top & set(np.flatnonzero(affected))) / k
    else:
        topk = float("nan")
    return corr, topk


# ----------------------------------------------------------------------------------------------
def nulls(S_H, stages_S, f, fi, prof, n_meas=40, seed=8800):
    """Noise-only dS inputs (full frequency grid) for the null distribution:
    (1) Healthy_sliced circulant residual under the 6 rotations x 2 reflections;
    (2) each mirror-symmetric stage's antisymmetric (mirror) part under the same 12 maps;
    (3) measurement-noise draws (typical profile) of Healthy_sliced minus Healthy_sliced."""
    from adstage.noise.model import realise
    n = N_ANT
    circ = np.zeros_like(S_H)
    idx = np.arange(n)
    for a in range(n):
        for b in range(n):
            k = (b - a) % n
            circ[:, a, b] = np.mean([S_H[:, t, (t + k) % n] for t in idx], 0)
    res_c = S_H - circ
    maps = [np.roll(idx, r) for r in range(n)] + [np.roll(idx[::-1], r) for r in range(n)]
    out = {"circulant": [permute(res_c, m) for m in maps]}
    mp = mirror_perm()
    for nm, S in stages_S.items():
        anti = 0.5 * (S - permute(S, mp))
        out[f"mirror {nm}"] = [permute(anti, m) for m in maps]
    rng = np.random.default_rng(seed)
    A = realise(f, S_H, prof, n_meas, rng)
    B = realise(f, S_H, prof, n_meas, rng)
    out["measurement"] = list(A - B)
    return out


def radar(f, dS_full, S_H, port_to_ant, t_ant_ns=0.5, z_ring=48.0):
    """DAS / DMAS images of dS on the ring plane (layered delays, v2-tuned t_ant)."""
    from .common import HeadParams, antenna_positions_mm
    lay = [(r, e) for (r, e, s) in HeadParams.stage("Normal").layers()]
    ppos = antenna_positions_mm()                                 # antenna order T1..T6
    pts, mask, u = plane_points("ring", z_ring, step=2.0)
    sig = pair_sigma_from(S_H)
    im = Imager(f, ppos, pts, lay, t_ant_s=t_ant_ns * 1e-9)
    out = {"pts": pts, "mask": mask, "u": u}
    for nm, dS in dS_full.items():
        x = pair_signals(dS, sig)
        out[nm] = {m: im.image(m, x) for m in ("DAS", "DMAS")}
    return out


def pair_sigma_from(S_H, profile="typical"):
    v = pair_sigma_f(S_H, PROFILES[profile])
    return np.sqrt(np.mean(v ** 2, 1))


def angular_stats(img, pts, r_lo=40.0, r_hi=80.0):
    """Azimuth of the image maximum (outside r_lo) and circular mean direction / resultant of the
    image energy in the annulus r_lo..r_hi."""
    r = np.linalg.norm(pts[:, :2], axis=1)
    az = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
    sel = (r >= r_lo) & (r <= r_hi)
    i_max = int(np.argmax(np.where(r >= r_lo, img, -np.inf)))
    w = img[sel]
    z = np.sum(w * np.exp(1j * np.deg2rad(az[sel]))) / np.sum(w)
    return dict(peak_az_deg=float(az[i_max]), peak_r_mm=float(r[i_max]),
                global_peak_r_mm=float(r[int(np.argmax(img))]),
                mean_dir_deg=float(np.degrees(np.angle(z))), resultant=float(np.abs(z)))


def true_centroid(design):
    e = np.array(DESIGNS[design][0], float)
    z = np.sum(e * np.exp(1j * np.deg2rad(SECT_AZ))) / max(np.sum(e), 1e-9)
    return dict(dir_deg=float(np.degrees(np.angle(z))), resultant=float(np.abs(z)))
