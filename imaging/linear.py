"""I2 - linearised (Born) inversion machinery.

Sensitivity (HFSS convention e^{+jωt}, fields in the forward model's unit):
    dS_ij(f) = kappa(f) * J_ij(r; f) . [d eps(r)] ,   J_ij(r) = -j k0^3 E_i(r) . E_j(r)  (no conjugate)
with d eps = d eps_r - j d sigma / (omega eps0). With HFSS field exports (1 W, matched ports) the
same expression is -(j omega eps0 / (4 a_i a_j)) E_i . E_j; the unknown complex scale kappa(f)
absorbs the difference and is calibrated per frequency against the simulated dS (Mild).

Unknown vector x = [d eps_r ; d eps''] with d eps'' = d sigma / (omega_c eps0) at the band centre
(both O(1-10)); the model maps x to the complex d eps(f) = d eps_r - j d eps'' (f_c / f).
Complex rows are split into real and imaginary parts.
"""
from __future__ import annotations

import numpy as np

from .mie import EPS0

C0 = 299_792_458.0


def born_prefactor(f_hz):
    k0 = 2 * np.pi * np.asarray(f_hz) / C0
    return -1j * k0 ** 3


def realify(Jc: np.ndarray, f_hz: np.ndarray, f_c: float) -> np.ndarray:
    """Complex J (R, F?, V) with rows (pair, f) flattened -> real (2R, 2V) acting on
    [d eps_r ; d eps''_c]. Jc: (n_rows, V); f_hz: (n_rows,) frequency of each row."""
    s = (f_c / np.asarray(f_hz))[:, None]
    A = np.concatenate([Jc, -1j * Jc * s], 1)                      # complex (R, 2V)
    return np.concatenate([A.real, A.imag], 0)


def sigma_from_epp(epp, f_c):
    return epp * 2 * np.pi * f_c * EPS0


# ----------------------------------------------------------------------------------------------
# Regularised solvers
# ----------------------------------------------------------------------------------------------
class TikhonovSVD:
    """x_lambda = argmin |Jx - d|^2 + lambda^2 |x|^2 via thin SVD of J (rows << cols ok)."""

    def __init__(self, J: np.ndarray):
        if J.shape[0] <= J.shape[1]:
            G = J @ J.T
            ev, U = np.linalg.eigh(G)
            ev = np.clip(ev, 0, None)
            idx = np.argsort(ev)[::-1]
            ev, U = ev[idx], U[:, idx]
            s = np.sqrt(ev)
            keep = s > s[0] * 1e-13
            self.U, self.s = U[:, keep], s[keep]
            self.V = (J.T @ self.U) / self.s
        else:
            U, s, Vt = np.linalg.svd(J, full_matrices=False)
            self.U, self.s, self.V = U, s, Vt.T
        self.m = J.shape[0]

    def solve(self, d, lam):
        b = self.U.T @ d
        return self.V @ (self.s / (self.s ** 2 + lam ** 2) * b)

    def filter(self, lam):
        return self.s ** 2 / (self.s ** 2 + lam ** 2)

    def gcv(self, d, lams):
        b = self.U.T @ d
        r_perp = max(np.sum(d ** 2) - np.sum(b ** 2), 0.0)
        out = []
        for lam in lams:
            fi = self.filter(lam)
            res = np.sum(((1 - fi) * b) ** 2) + r_perp
            out.append(res / (self.m - np.sum(fi)) ** 2)
        return np.array(out)

    def lcurve(self, d, lams):
        b = self.U.T @ d
        r_perp = max(np.sum(d ** 2) - np.sum(b ** 2), 0.0)
        res = np.array([np.sum(((1 - self.filter(l)) * b) ** 2) + r_perp for l in lams])
        sol = np.array([np.sum((self.s / (self.s ** 2 + l ** 2) * b) ** 2) for l in lams])
        return np.sqrt(res), np.sqrt(sol)

    def pick(self, d, lams, rule="gcv"):
        if rule == "gcv":
            return lams[int(np.argmin(self.gcv(d, lams)))]
        rho, eta = self.lcurve(d, lams)
        x, y = np.log(rho), np.log(eta)                      # max curvature of the L-curve
        dx, dy = np.gradient(x), np.gradient(y)
        ddx, ddy = np.gradient(dx), np.gradient(dy)
        kappa = (dx * ddy - ddx * dy) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-30)
        k = kappa.copy()
        k[:2] = k[-2:] = -np.inf
        return lams[int(np.argmax(k))]

    def resolution(self, lam):
        """Model-resolution matrix R = V F V^T (only for small problems)."""
        return (self.V * self.filter(lam)) @ self.V.T


def fista_l1(J, d, lam, n_iter=400, x0=None, L=None):
    """min 0.5|Jx - d|^2 + lam |x|_1 (sparsity) by FISTA. L = |J|_2^2 (computed if None)."""
    L = np.linalg.norm(J, 2) ** 2 if L is None else L
    x = np.zeros(J.shape[1]) if x0 is None else x0.copy()
    y, t = x.copy(), 1.0
    for _ in range(n_iter):
        g = J.T @ (J @ y - d)
        z = y - g / L
        xn = np.sign(z) * np.maximum(np.abs(z) - lam / L, 0)
        tn = 0.5 * (1 + np.sqrt(1 + 4 * t * t))
        y = xn + (t - 1) / tn * (xn - x)
        x, t = xn, tn
    return x


def tv1d_irls(J, d, lam, blocks, n_iter=30, eps=1e-3):
    """min |Jx - d|^2 + lam sum |D x| (1-D total variation inside each block of unknowns) by
    iteratively reweighted least squares. blocks: list of index arrays (e.g. eps_r, eps'')."""
    n = J.shape[1]
    rows = []
    for b in blocks:
        b = np.asarray(b)
        for i in range(len(b) - 1):
            r = np.zeros(n)
            r[b[i]], r[b[i + 1]] = -1, 1
            rows.append(r)
    D = np.array(rows)
    x = np.linalg.lstsq(np.vstack([J, 1e-3 * np.eye(n)]), np.concatenate([d, np.zeros(n)]),
                        rcond=None)[0]
    JtJ, Jtd = J.T @ J, J.T @ d
    for _ in range(n_iter):
        w = 1 / np.sqrt((D @ x) ** 2 + eps ** 2)
        A = JtJ + lam * (D.T * w) @ D + 1e-10 * np.eye(n)
        x = np.linalg.solve(A, Jtd)
    return x
