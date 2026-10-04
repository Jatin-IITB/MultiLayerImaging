"""Sector-superposition surrogate: S-parameter log-ratios from a physical description of each sector.

Model (per frequency f, per reciprocal path p):
    L_p(f) = ln(S_p / S_p,healthy) = sum_k sum_m C_{o(p,k), m}(f) * phi_{k,m}
  * phi_{k,m}: physics features of sector k = depth-weighted integrals of the true change of the
    dielectric profile under the skull, d eps_r(d) and d sigma(d) (d = 83.5 - r), with weights
    exp(-d / delta_m). They follow exactly from (stage material table, e_k) by the phantom geometry;
    the global CSF-material change (the 0.5 mm layer present in every sector) is part of every
    sector's profile.
  * o(p, k): the orbit of the (path, sector) pair under the ring's D6 symmetry (13 orbits). Sharing
    coefficients across an orbit is the symmetry augmentation: every solved design is used in all
    12 of its rotated / mirrored copies at once.
  * C: complex, fitted by ridge regression (real and imaginary parts separately, noise-weighted)
    on the solved designs of the training fold only.
"""
from __future__ import annotations

import numpy as np

from .data import N, N_ORBIT, ORBIT, Truth
from .phantom import depth_profile

D_GRID = np.arange(0.0, 83.5, 0.05) + 0.025            # depth midpoints (mm)
DD = 0.05

FEATURE_SETS = {
    "es8": [("eps", 8.0), ("sig", 8.0)],
    "es4_12": [("eps", 4.0), ("sig", 4.0), ("eps", 12.0), ("sig", 12.0)],
    "es3_8_20": [("eps", 3.0), ("sig", 3.0), ("eps", 8.0), ("sig", 8.0), ("eps", 20.0), ("sig", 20.0)],
    "es6_15": [("eps", 6.0), ("sig", 6.0), ("eps", 15.0), ("sig", 15.0)],
}


def sector_features(t: Truth, k: int, fset: str) -> np.ndarray:
    de, ds = depth_profile(t, k, D_GRID)
    out = []
    for comp, delta in FEATURE_SETS[fset]:
        w = np.exp(-D_GRID / delta) / delta
        out.append(float(((de if comp == "eps" else ds) * w).sum() * DD))
    return np.array(out)


def features(t: Truth, fset: str) -> np.ndarray:
    """(6, M) features of a design."""
    return np.stack([sector_features(t, k, fset) for k in range(N)])


def design_rows(phi: np.ndarray) -> np.ndarray:
    """phi (6, M) -> X (21, N_ORBIT * M) with X[p, o*M + m] = sum_{k: o(p,k) = o} phi[k, m]."""
    M = phi.shape[1]
    X = np.zeros((ORBIT.shape[0], N_ORBIT, M))
    for k in range(N):
        np.add.at(X, (np.arange(ORBIT.shape[0]), ORBIT[:, k]), phi[k][None, :])
    return X.reshape(ORBIT.shape[0], N_ORBIT * M)


class Surrogate:
    def __init__(self, fset: str, lam: float = 1e-2):
        self.fset, self.lam = fset, lam

    def fit(self, phis, Ls, w_re, w_im):
        """phis: list of (6, M); Ls: list of (21, F) complex; w_*: (21, F) inverse noise variances."""
        X = np.concatenate([design_rows(p) for p in phis])                 # (E*21, P)
        Y = np.concatenate(Ls)                                             # (E*21, F)
        Wr = np.concatenate([w_re] * len(Ls))
        Wi = np.concatenate([w_im] * len(Ls))
        self.scale = np.sqrt((X ** 2).mean(0)) + 1e-12
        Xs = X / self.scale
        P = Xs.shape[1]
        F = Y.shape[1]
        self.C = np.zeros((P, F), complex)
        for f in range(F):
            for part, W, y in ((0, Wr[:, f], Y[:, f].real), (1, Wi[:, f], Y[:, f].imag)):
                A = Xs.T @ (W[:, None] * Xs)
                lam = self.lam * np.trace(A) / P
                c = np.linalg.solve(A + lam * np.eye(P), Xs.T @ (W * y))
                if part == 0:
                    self.C[:, f] += c
                else:
                    self.C[:, f] += 1j * c
        self.C /= self.scale[:, None]
        self.M = phis[0].shape[1]
        return self

    def predict(self, phi):
        return design_rows(phi) @ self.C                                    # (21, F)

    def sector_gain(self, k):
        """(21, M, F): contribution of sector k per unit feature."""
        Cr = self.C.reshape(N_ORBIT, self.M, -1)
        return Cr[ORBIT[:, k]]


# ----------------------------------------------------------------------------------------------
# Layered-stack features: exact 1-D multilayer reflection change of each sector's tissue column
# ----------------------------------------------------------------------------------------------
C0 = 299792458.0
MU0 = 4e-7 * np.pi


def sector_stack(t: Truth, k: int):
    """Layers from the skin inwards: [(thickness m, eps_r, sigma)], last one semi-infinite."""
    from .phantom import FIXED, R_CSF, R_FAT, R_SKIN, R_SKULL, radii, sector_materials
    rgo, rgi, rwi, rh = radii(t, k)
    gm, wm, csf, _ = sector_materials(t, k)
    lay = [((R_SKIN - R_FAT), *FIXED["skin"]), ((R_FAT - R_SKULL), *FIXED["fat"]),
           ((R_SKULL - R_CSF), *FIXED["skull"]), ((R_CSF - rgo), *csf), ((rgo - rgi), *gm),
           (np.inf, *wm)]
    return [(d * 1e-3, e, s) for d, e, s in lay]


def stack_gamma(layers, f, kt_rel=0.0, pol="TM"):
    """Reflection coefficient at the skin surface (from air) of a planar layer stack, plane wave
    with transverse wavenumber kt = kt_rel * k0. e^{+jwt}; kz with Im(kz) <= 0."""
    w = 2 * np.pi * f
    k0 = w / C0
    kt = kt_rel * k0

    def kz_of(epsc):
        kz = np.sqrt(k0 ** 2 * epsc - kt ** 2 + 0j)
        return np.where(kz.imag > 0, -kz, kz)

    def Z_of(epsc, kz):
        return (w * MU0 / kz) if pol == "TE" else (kz / (w * 8.854187817e-12 * epsc))

    d_last, e_last, s_last = layers[-1]
    epsc = e_last - 1j * s_last / (w * 8.854187817e-12)
    ZL = Z_of(epsc, kz_of(epsc))
    for d, e, s in reversed(layers[:-1]):
        if d <= 0:
            continue
        epsc = e - 1j * s / (w * 8.854187817e-12)
        kz = kz_of(epsc)
        Zi = Z_of(epsc, kz)
        th = np.tanh(1j * kz * d)
        ZL = Zi * (ZL + Zi * th) / (Zi + ZL * th)
    Z0a = Z_of(np.ones_like(f) + 0j, kz_of(np.ones_like(f) + 0j))
    return (ZL - Z0a) / (ZL + Z0a)


STACK_SETS = {
    "tm0": [("TM", 0.0)],
    "tm0_tm2": [("TM", 0.0), ("TM", 2.0)],
    "tm0_te2_tm2": [("TM", 0.0), ("TE", 2.0), ("TM", 2.0)],
    "tm0_tm2_tm4": [("TM", 0.0), ("TM", 2.0), ("TM", 4.0)],
}


def stack_features(t: Truth, f, sset: str):
    """(6, 2*n, F) real features: Re/Im of d Gamma (state - healthy) per sector and frequency."""
    from .data import HEALTHY_LOBE
    out = np.zeros((N, 2 * len(STACK_SETS[sset]), len(f)))
    for k in range(N):
        lay, lay0 = sector_stack(t, k), sector_stack(HEALTHY_LOBE, k)
        for m, (pol, kt) in enumerate(STACK_SETS[sset]):
            dg = stack_gamma(lay, f, kt, pol) - stack_gamma(lay0, f, kt, pol)
            out[k, 2 * m], out[k, 2 * m + 1] = dg.real, dg.imag
    return out


def design_rows_f(phi):
    """phi (6, M, F) -> X (21, N_ORBIT*M, F)."""
    M, F = phi.shape[1], phi.shape[2]
    X = np.zeros((ORBIT.shape[0], N_ORBIT, M, F))
    for k in range(N):
        np.add.at(X, (np.arange(ORBIT.shape[0]), ORBIT[:, k]), phi[k][None])
    return X.reshape(ORBIT.shape[0], N_ORBIT * M, F)


class SurrogateF(Surrogate):
    """Same model with frequency-dependent features phi (6, M, F)."""

    def fit(self, phis, Ls, w_re, w_im):
        X = np.concatenate([design_rows_f(p) for p in phis])               # (E*21, P, F)
        Y = np.concatenate(Ls)
        Wr = np.concatenate([w_re] * len(Ls))
        Wi = np.concatenate([w_im] * len(Ls))
        self.scale = np.sqrt((X ** 2).mean((0, 2))) + 1e-12
        Xs = X / self.scale[None, :, None]
        P, F = Xs.shape[1], Y.shape[1]
        self.C = np.zeros((P, F), complex)
        for f in range(F):
            for part, W, y in ((0, Wr[:, f], Y[:, f].real), (1, Wi[:, f], Y[:, f].imag)):
                A = Xs[:, :, f].T @ (W[:, None] * Xs[:, :, f])
                lam = self.lam * np.trace(A) / P
                c = np.linalg.solve(A + lam * np.eye(P), Xs[:, :, f].T @ (W * y))
                self.C[:, f] += c if part == 0 else 1j * c
        self.C /= self.scale[:, None]
        self.M = phis[0].shape[1]
        return self

    def predict(self, phi):
        X = design_rows_f(phi)
        return np.einsum("pqf,qf->pf", X, self.C)
