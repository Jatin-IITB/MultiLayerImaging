"""Multilayer concentric sphere + point dipoles: exact (vector spherical-wave) solution.

Conventions (internal): time dependence e^{-iωt}, complex relative permittivity
ε = εr + iσ/(ωε0), host = vacuum. Everything returned to the rest of the code is converted to
the engineering convention e^{+jωt} used by HFSS by complex conjugation (``to_hfss``).

Vector spherical waves (orthonormal, Jackson-type angular functions):
    Y_nm              scalar spherical harmonic (scipy ``sph_harm_y``, Condon-Shortley phase)
    X_nm = L Y_nm / sqrt(n(n+1)),   L = -i r x grad
    M_nm(kr) = z_n(kr) X_nm
    N_nm(kr) = (1/k) curl M_nm = [zeta_n'(kr)/(kr)] (r^ x X_nm) + [i sqrt(n(n+1)) z_n(kr)/(kr)] Y_nm r^
with zeta_n(x) = x z_n(x) (Riccati function; psi_n = x j_n, xi_n = x h_n^(1)).
Free-space dyadic Green's function for r < r' (verified against the closed form in the tests):
    G0(r, r') = ik sum_nm [ RgM_nm(r) (x) M~_nm(r') + RgN_nm(r) (x) N~_nm(r') ],
where ~ means: complex-conjugate the angular part (including the i of the radial N term), keep
h_n unconjugated. The field of a dipole p at r' is E = omega^2 mu0 G.p.

Scattering by the layered sphere: outgoing = T_n * incoming with T^M = -b_n, T^N = -a_n
(Bohren-Huffman coefficients). a_n, b_n and the field inside every layer are computed with
logarithmic derivatives D1 = psi'/psi, D3 = xi'/xi and log-magnitude Riccati functions
(Yang 2003, Appl. Opt. 42:1710 recursion, rewritten in log form), so there is no overflow for
n up to a few hundred and strongly lossy layers.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import sph_harm_y

C0 = 299_792_458.0
EPS0 = 8.8541878128e-12
MU0 = 1.25663706212e-6


def eps_complex(eps_r, sigma, f_hz):
    """e^{-iωt} complex relative permittivity (Im >= 0 for a lossy medium)."""
    return np.asarray(eps_r) + 1j * np.asarray(sigma) / (2 * np.pi * np.asarray(f_hz) * EPS0)


def to_hfss(x):
    """e^{-iωt} phasor -> e^{+jωt} phasor (HFSS / engineering convention)."""
    return np.conj(x)


# ----------------------------------------------------------------------------------------------
# Riccati-Bessel machinery (arrays: leading axis n = 0..nmax, trailing axes = z.shape)
# ----------------------------------------------------------------------------------------------
def _d1(z: np.ndarray, nmax: int) -> np.ndarray:
    """D1_n(z) = psi_n'/psi_n by downward recurrence (stable), n = 0..nmax."""
    z = np.asarray(z, complex)
    nst = int(max(nmax, np.abs(z).max(initial=0.0))) + 30
    D = np.zeros(z.shape, complex)
    out = np.empty((nmax + 1,) + z.shape, complex)
    for n in range(nst, 0, -1):
        D = n / z - 1.0 / (D + n / z)            # D_{n-1}
        if n - 1 <= nmax:
            out[n - 1] = D
    return out


def riccati(z: np.ndarray, nmax: int):
    """Return D1, D3, log psi, log xi, each (nmax+1, *z.shape).

    log values are complex logarithms (any branch); only their differences are exponentiated.
    psi_n = psi_{n-1} (n/z - D1_{n-1}),  xi_n = xi_{n-1} (n/z - D3_{n-1}),
    D3_n = D1_n + i/(psi_n xi_n),        psi_n xi_n recurred upward (Yang 2003)."""
    z = np.asarray(z, complex)
    D1 = _d1(z, nmax)
    D3 = np.empty_like(D1)
    lpsi = np.empty_like(D1)
    lxi = np.empty_like(D1)
    e2 = np.exp(2j * z)
    px = 0.5 * (1 - e2)                             # psi_0 xi_0
    D3[0] = 1j
    lpsi[0] = -1j * z + np.log((e2 - 1) / 2j)      # log sin z, stable for Im z >> 0
    lxi[0] = np.log(-1j) + 1j * z
    for n in range(1, nmax + 1):
        a1 = n / z - D1[n - 1]
        a3 = n / z - D3[n - 1]
        px = px * a1 * a3
        D3[n] = D1[n] + 1j / px
        lpsi[n] = lpsi[n - 1] + np.log(a1)
        lxi[n] = lxi[n - 1] + np.log(a3)
    return D1, D3, lpsi, lxi


# ----------------------------------------------------------------------------------------------
# Layered sphere
# ----------------------------------------------------------------------------------------------
@dataclass
class Sphere:
    radii_m: np.ndarray        # (L,) outer radius of each layer, ascending (core first)
    eps: np.ndarray            # (L, F) complex relative permittivity, e^{-iωt}
    f_hz: np.ndarray           # (F,)

    @property
    def k0(self):
        return 2 * np.pi * self.f_hz / C0


class LayeredSolution:
    """Mie coefficients and per-layer standing-wave parameters for n = 1..nmax, all F."""

    def __init__(self, sph: Sphere, nmax: int):
        r = np.asarray(sph.radii_m, float)
        if np.any(np.diff(r) <= 0):
            raise ValueError("radii must be strictly ascending")
        self.sph, self.nmax = sph, nmax
        k0 = sph.k0                                            # (F,)
        m = np.sqrt(sph.eps.astype(complex))                   # (L, F), Im >= 0
        self.m = m
        L = r.size
        n = np.arange(nmax + 1)[:, None]
        # per layer: z_in, z_o and the coefficient c (u = psi - c R(z_in) xi) for TM (a) and TE (b)
        self.c = {"a": [np.zeros((nmax + 1, k0.size), complex)],
                  "b": [np.zeros((nmax + 1, k0.size), complex)]}
        self.lR_in = [np.full((nmax + 1, k0.size), -np.inf + 0j)]
        # all Riccati evaluations in one batched call: rows [z_o(0), z_in(1), z_o(1), ..., x]
        Z = [m[0] * k0 * r[0]]
        for l in range(1, L):
            Z += [m[l] * k0 * r[l - 1], m[l] * k0 * r[l]]
        Z.append((k0 * r[-1]).astype(complex))
        RD1, RD3, RLP, RLX = riccati(np.array(Z), nmax)          # (nmax+1, 2L, F)
        H = {"a": RD1[:, 0].copy(), "b": RD1[:, 0].copy()}
        for l in range(1, L):
            ii, io = 2 * l - 1, 2 * l
            D1i, D3i, lpi, lxi_ = RD1[:, ii], RD3[:, ii], RLP[:, ii], RLX[:, ii]
            D1o, D3o, lpo, lxo = RD1[:, io], RD3[:, io], RLP[:, io], RLX[:, io]
            lR_in = lpi - lxi_
            lQ = lR_in - (lpo - lxo)                            # log R(z_in)/R(z_o)
            self.lR_in.append(lR_in)
            for t in ("a", "b"):
                ratio = m[l] / m[l - 1] if t == "a" else m[l - 1] / m[l]
                T = ratio * H[t]
                c = (D1i - T) / (D3i - T)
                self.c[t].append(c)
                cq = c * np.exp(lQ)
                H[t] = (D1o - cq * D3o) / (1 - cq)
        self.H = H
        x = k0 * r[-1]
        mL = m[-1]
        D1x, D3x, lpx, lxx = RD1[:, -1], RD3[:, -1], RLP[:, -1], RLX[:, -1]
        ga = (H["a"] / mL - D1x) / (H["a"] / mL - D3x)
        gb = (mL * H["b"] - D1x) / (mL * H["b"] - D3x)
        lRx = lpx - lxx
        self.log_a = lRx + np.log(ga)                          # a_n = exp(log_a)
        self.log_b = lRx + np.log(gb)
        self.ga, self.gb = ga, gb
        self.air = dict(x=x, D1=D1x, D3=D3x, lpsi=lpx, lxi=lxx)
        self.n = n

    @property
    def a(self):
        return np.exp(self.log_a)

    @property
    def b(self):
        return np.exp(self.log_b)


# ----------------------------------------------------------------------------------------------
# Angular functions (Cartesian components)
# ----------------------------------------------------------------------------------------------
def _cart_to_sph(p):
    p = np.asarray(p, float)
    r = np.linalg.norm(p, axis=-1)
    th = np.arccos(np.clip(p[..., 2] / np.where(r > 0, r, 1), -1, 1))
    ph = np.arctan2(p[..., 1], p[..., 0])
    return r, th, ph


def angular(nmax: int, ms, rhat: np.ndarray):
    """Y_nm r^, X_nm and r^ x X_nm at unit vectors rhat (P, 3), n = 1..nmax, m in ms.

    Returns Y (N, M, P), X (N, M, P, 3), rX (N, M, P, 3) with N = nmax (index n-1)."""
    _, th, ph = _cart_to_sph(rhat)
    n = np.arange(1, nmax + 1)[:, None, None]
    ms = np.asarray(ms)[None, :, None]

    def Y(mm):
        out = sph_harm_y(n, mm, th[None, None, :], ph[None, None, :])
        return np.where(np.abs(mm) <= n, out, 0.0)

    y0, yp, ym = Y(ms), Y(ms + 1), Y(ms - 1)
    Lp = np.sqrt(np.clip((n - ms) * (n + ms + 1), 0, None)) * yp
    Lm = np.sqrt(np.clip((n + ms) * (n - ms + 1), 0, None)) * ym
    nn = np.sqrt(n * (n + 1.0))
    X = np.stack([(Lp + Lm) / 2, (Lp - Lm) / 2j, ms * y0], -1) / nn[..., None]
    rh = np.broadcast_to(rhat, X.shape)
    rX = np.cross(rh, X)
    return y0, X, rX


def rotation_to_pole(u: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Rows (p, u x p, u): maps position direction u -> z^ and dipole direction p -> x^."""
    u = u / np.linalg.norm(u)
    p = p - u * (p @ u)
    p = p / np.linalg.norm(p)
    return np.stack([p, np.cross(u, p), u])


# ----------------------------------------------------------------------------------------------
# Dipole source at the north pole (x-directed, in its own frame)
# ----------------------------------------------------------------------------------------------
def _source_angular(nmax: int):
    """Angular source factors for p = x^ at r^ = z^: only m = -1, 0, +1 are non-zero."""
    ms = np.array([-1, 0, 1])
    y, X, rX = angular(nmax, ms, np.array([[0.0, 0.0, 1.0]]))
    p = np.array([1.0, 0.0, 0.0])
    angM = np.conj(X[..., 0, :]) @ p                        # (N, 3)   X~ . p
    angNt = np.conj(rX[..., 0, :]) @ p                      #          (z^ x X~) . p
    angNr = np.conj(y[..., 0]) * 0.0                        #          Y~ (z^.p) = 0 (tangential p)
    return ms, angM, angNt, angNr


def _log_src(sol: LayeredSolution, x_s: np.ndarray):
    """log of the source radial factor xi_n(x_s)/x_s, D3_n(x_s) and x_s. x_s: (F,)."""
    D1, D3, lp, lx = riccati(x_s.astype(complex), sol.nmax)
    return lx - np.log(x_s), D3, x_s


def receiver_field_scattered(sol: LayeredSolution, r_src: float, pts: np.ndarray,
                             nmax: int | None = None) -> np.ndarray:
    """Scattered E at points outside the sphere, source = x^ dipole at (0,0,r_src).

    pts (P, 3) in the source frame [m]; returns (F, P, 3), e^{-iωt}, unit omega^2 mu0 ik = 1
    (i.e. E / (omega^2 mu0 ik))."""
    nmax = nmax or sol.nmax
    k0 = sol.sph.k0
    ms, angM, angNt, angNr = _source_angular(nmax)
    r, _, _ = _cart_to_sph(pts)
    rhat = pts / r[:, None]
    y, X, rX = angular(nmax, ms, rhat)                      # (N, 3, P[,3])
    ls, D3s, xs = _log_src(sol, k0 * r_src)
    nn = np.sqrt(np.arange(nmax + 1) * (np.arange(nmax + 1) + 1.0))[1:, None]
    out = np.zeros((k0.size, len(pts), 3), complex)
    for ip in range(len(pts)):
        x = k0 * r[ip]
        D1x, D3x, lpx, lxx = riccati(x.astype(complex), nmax)
        # per n (1..nmax), F
        base_b = np.exp(ls[1:nmax + 1] + lxx[1:] + sol.log_b[1:nmax + 1]) / x      # b h(x_s) xi(x)/x
        base_a = np.exp(ls[1:nmax + 1] + lxx[1:] + sol.log_a[1:nmax + 1]) / x
        fTE = -base_b                                                           # -b xi(x)/x
        fTMt = -base_a * D3x[1:]                                                # -a xi'(x)/x
        fTMr = -base_a * 1j * nn / x                                            # -a i sqrt xi/x^2
        srcN = D3s[1:nmax + 1]                                                        # xi'(x_s)/xi(x_s)
        # angular sums over m for this point: (N, 3comp)
        AM = np.einsum("nm,nmc->nc", angM, X[:, :, ip, :])
        ANt = np.einsum("nm,nmc->nc", angNt, rX[:, :, ip, :])
        ANr = np.einsum("nm,nm->n", angNt, y[:, :, ip])[:, None] * rhat[ip][None, :]
        out[:, ip, :] = (np.einsum("nf,nc->fc", fTE, AM)
                         + np.einsum("nf,nc->fc", fTMt * srcN, ANt)
                         + np.einsum("nf,nc->fc", fTMr * srcN, ANr))
    return out


def free_space_field(k0: np.ndarray, r_src_vec: np.ndarray, p: np.ndarray, pts: np.ndarray):
    """Closed-form E of a dipole p at r_src in vacuum, in the same unit (E/(omega^2 mu0 ik)).

    G0 = e^{ikR}/(4 pi R) [(1 + i/kR - 1/(kR)^2) I + (-1 - 3i/kR + 3/(kR)^2) R^R^]."""
    Rv = pts[None, :, :] - r_src_vec[None, None, :]
    R = np.linalg.norm(Rv, axis=-1)
    Rh = Rv / R[..., None]
    kR = k0[:, None] * R
    g = np.exp(1j * kR) / (4 * np.pi * R)
    A = 1 + 1j / kR - 1 / kR ** 2
    B = -1 - 3j / kR + 3 / kR ** 2
    Gp = g[..., None] * (A[..., None] * p + B[..., None] * Rh * (Rh @ p)[..., None])
    return Gp / (1j * k0[:, None, None])


# ----------------------------------------------------------------------------------------------
# Fields inside the sphere
# ----------------------------------------------------------------------------------------------
def _layer_shape(sol: LayeredSolution, l: int, r: np.ndarray, t: str, nmax: int):
    """Shape functions of layer l at radii r (R,) for mode type t ('a' TM or 'b' TE).

    Returns (u(z)/u(z_o), u'(z)/u(z_o), z/z_o, z) with z = m_l k0 r, each (nmax+1, F, R)."""
    sph = sol.sph
    k0 = sph.k0
    m = sol.m[l]
    r_o = sph.radii_m[l]
    z = (m * k0)[:, None] * r[None, :]                             # (F, R)
    z_o = (m * k0 * r_o)
    D1, D3, lp, lx = riccati(z, nmax)
    D1o, D3o, lpo, lxo = riccati(z_o, nmax)
    lpo_, lxo_, D1o_, D3o_ = (v[..., None] for v in (lpo, lxo, D1o, D3o))
    c = sol.c[t][l][: nmax + 1, :, None]
    lRin = sol.lR_in[l][: nmax + 1, :, None]
    A = np.exp(lp - lpo_)
    if l == 0:
        B = np.zeros_like(A)
        Cc = np.zeros_like(A)
    else:
        B = np.exp(lRin + lx - lpo_)
        Cc = np.exp(lRin + lxo_ - lpo_)
    den = 1 - c * Cc
    u = (A - c * B) / den
    du = (A * D1 - c * B * D3) / den
    du_o = (D1o_ - c * Cc * D3o_) / den                             # u'(z_o)/u(z_o)
    return u, du, du_o, z, z_o


def internal_field(sol: LayeredSolution, r_src: float, pts: np.ndarray,
                   nmax: int | None = None, r_step: float = 2.5e-4) -> np.ndarray:
    """Total E inside the sphere (|r| <= outer radius) for the x^ dipole at (0,0,r_src).

    Radial functions are computed on a fine 1-D radial grid (step r_step) and interpolated
    (cubic in r) to the points; angular functions exactly. Same units as
    receiver_field_scattered. pts (P, 3) [m]; returns (F, P, 3)."""
    nmax = nmax or sol.nmax
    sph = sol.sph
    k0 = sph.k0
    F = k0.size
    radii = np.asarray(sph.radii_m)
    L = radii.size
    ms, angM, angNt, _ = _source_angular(nmax)
    ls, D3s, xs = _log_src(sol, k0 * r_src)
    ar = sol.air
    nn = np.sqrt(np.arange(nmax + 1) * (np.arange(nmax + 1) + 1.0))[:, None]
    # E_t at the outer surface per unit incident coefficient, times the source factor.
    # TE: [psi - b xi]/x ; TM: [psi D1 - a xi D3]/x   (x = k0 R)
    x = ar["x"]
    sl = slice(0, nmax + 1)
    lsrc = ls[sl] + ar["lpsi"][sl] - np.log(x)
    EtR = {"b": np.exp(lsrc) * (1 - sol.gb[sl]),
           "a": np.exp(lsrc) * (ar["D1"][sl] - sol.ga[sl] * ar["D3"][sl]) * D3s[sl]}
    # walk inwards: E_t at each layer's outer boundary
    radial = {}
    r_all, _, _ = _cart_to_sph(pts)
    r_all = np.maximum(r_all, 1e-7)
    Et_o = {t: EtR[t] for t in "ab"}
    for l in range(L - 1, -1, -1):
        r_lo = 0.0 if l == 0 else radii[l - 1]
        sel = (r_all <= radii[l] + 1e-12) & (r_all > r_lo)
        n_g = max(int(np.ceil((radii[l] - r_lo) / r_step)) + 1, 4)
        rg = np.linspace(max(r_lo, 1e-6), radii[l], n_g)
        for t in "ab":
            u, du, du_o, z, z_o = _layer_shape(sol, l, rg, t, nmax)
            zo = z_o[None, :, None]
            if t == "b":            # TE: E_t ∝ u/z
                ft = Et_o[t][..., None] * u * zo / z[None]
                radial[(l, t, "t")] = (rg, ft)
                Et_next = ft[..., 0]
            else:                   # TM: E_t ∝ u'/z, E_r ∝ i sqrt(n(n+1)) u / z^2
                den = du_o[..., :1] if False else du_o
                ft = Et_o[t][..., None] * (du / den) * zo / z[None]
                fr = Et_o[t][..., None] * (1j * nn[..., None] * u / den) * zo / z[None] ** 2
                radial[(l, t, "t")] = (rg, ft)
                radial[(l, t, "r")] = (rg, fr)
                Et_next = ft[..., 0]
            Et_o[t] = Et_next
        radial[(l, "sel")] = sel
    rhat = pts / r_all[:, None]
    y, X, rX = angular(nmax, ms, rhat)
    AM = np.einsum("nm,nmpc->npc", angM, X)                     # (N, P, 3)
    ANt = np.einsum("nm,nmpc->npc", angNt, rX)
    ANr = np.einsum("nm,nmp->np", angNt, y)[..., None] * rhat[None]
    out = np.zeros((F, len(pts), 3), complex)
    from scipy.interpolate import CubicSpline
    for l in range(L):
        sel = radial[(l, "sel")]
        if not sel.any():
            continue
        rp = r_all[sel]

        def interp(key):
            rg, fv = radial[key]
            return CubicSpline(rg, fv[1:], axis=-1)(rp)           # (N, F, P_l)
        fTE, fTMt, fTMr = interp((l, "b", "t")), interp((l, "a", "t")), interp((l, "a", "r"))
        out[:, sel, :] = (np.einsum("nfp,npc->fpc", fTE, AM[:, sel])
                          + np.einsum("nfp,npc->fpc", fTMt, ANt[:, sel])
                          + np.einsum("nfp,npc->fpc", fTMr, ANr[:, sel]))
    return out


# ----------------------------------------------------------------------------------------------
# General (non-rotated) formulation: sources = sets of tangential dipole elements on the
# sphere r = r_s. Projections onto the vector spherical harmonics make every coupling a sum
# over n of (Mie coefficient x radial factor x angular kernel), with the kernels
# frequency-independent (precomputed once per antenna model).
# ----------------------------------------------------------------------------------------------
def projections(nmax: int, pos: np.ndarray, dirs: np.ndarray, w: np.ndarray):
    """P_TE[n-1, m+nmax] = sum_e w_e X~_nm(r^_e).p_e ; P_TM with (r^ x X~_nm).p_e.

    pos, dirs (E, 3), w (E,). Returns two (nmax, 2 nmax + 1) complex arrays (0 for |m| > n)."""
    ms = np.arange(-nmax, nmax + 1)
    r = np.linalg.norm(pos, axis=1)
    rhat = pos / r[:, None]
    PTE = np.zeros((nmax, ms.size), complex)
    PTM = np.zeros((nmax, ms.size), complex)
    step = 20
    for n0 in range(1, nmax + 1, step):
        n1 = min(n0 + step - 1, nmax)
        y, X, rX = _angular_block(n0, n1, ms, rhat)
        PTE[n0 - 1:n1] = np.einsum("nmec,ec,e->nm", np.conj(X), dirs, w)
        PTM[n0 - 1:n1] = np.einsum("nmec,ec,e->nm", np.conj(rX), dirs, w)
    return PTE, PTM


def _angular_block(n0, n1, ms, rhat):
    """angular() for n = n0..n1 only."""
    _, th, ph = _cart_to_sph(rhat)
    n = np.arange(n0, n1 + 1)[:, None, None]
    ms = np.asarray(ms)[None, :, None]

    def Y(mm):
        ok = np.abs(mm) <= n
        out = sph_harm_y(n, np.where(ok, mm, 0), th[None, None, :], ph[None, None, :])
        return np.where(ok, out, 0.0)

    y0, yp, ym = Y(ms), Y(ms + 1), Y(ms - 1)
    Lp = np.sqrt(np.clip((n - ms) * (n + ms + 1), 0, None)) * yp
    Lm = np.sqrt(np.clip((n + ms) * (n - ms + 1), 0, None)) * ym
    nn = np.sqrt(n * (n + 1.0))
    X = np.stack([(Lp + Lm) / 2, (Lp - Lm) / 2j, ms * y0], -1) / nn[..., None]
    rX = np.cross(np.broadcast_to(rhat, X.shape), X)
    return y0, X, rX


def coupling_kernels(PA, PB):
    """K_TE(n), K_TM(n) = sum_m P_A conj(P_B): reaction angular kernels, (nmax,) each."""
    return (np.einsum("nm,nm->n", PA[0], np.conj(PB[0])),
            np.einsum("nm,nm->n", PA[1], np.conj(PB[1])))


def scattered_reaction(sol: LayeredSolution, r_s: float, K_TE: np.ndarray, K_TM: np.ndarray):
    """Scattered reaction between two element sets on r = r_s (e^{-iωt}, unit omega^2 mu0 ik).

    V = sum_n [-b_n (xi_n(x)/x)^2 K_TE(n) - a_n (xi_n'(x)/x)^2 K_TM(n)],  x = k0 r_s.
    K_* may carry extra leading axes (..., nmax); returns (..., F)."""
    nmax = K_TE.shape[-1]
    x = sol.sph.k0 * r_s
    D1, D3, lp, lx = riccati(x.astype(complex), nmax)
    sl = slice(1, nmax + 1)
    base = 2 * (lx[sl] - np.log(x))
    te = -np.exp(base + sol.log_b[sl])                         # (nmax, F)
    tm = -np.exp(base + sol.log_a[sl]) * D3[sl] ** 2
    return np.einsum("...n,nf->...f", K_TE, te) + np.einsum("...n,nf->...f", K_TM, tm)


def internal_field_general(sol: LayeredSolution, r_s: float, P, pts: np.ndarray,
                           r_step: float = 2.5e-4) -> np.ndarray:
    """Total E inside the sphere for an element set with projections P = (P_TE, P_TM) on
    r = r_s. pts (Q, 3) [m]. Returns (F, Q, 3), e^{-iωt}, unit omega^2 mu0 ik."""
    PTE, PTM = P
    nmax = PTE.shape[0]
    sph = sol.sph
    k0 = sph.k0
    F = k0.size
    radii = np.asarray(sph.radii_m)
    L = radii.size
    D1s, D3s, lps, lxs = riccati((k0 * r_s).astype(complex), nmax)
    ls = lxs - np.log(k0 * r_s)
    ar = sol.air
    x = ar["x"]
    sl = slice(0, nmax + 1)
    lsrc = ls[sl] + ar["lpsi"][sl] - np.log(x)
    Et_o = {"b": np.exp(lsrc) * (1 - sol.gb[sl]),
            "a": np.exp(lsrc) * (ar["D1"][sl] - sol.ga[sl] * ar["D3"][sl]) * D3s[sl]}
    nn = np.sqrt(np.arange(nmax + 1) * (np.arange(nmax + 1) + 1.0))[:, None]
    r_all = np.maximum(np.linalg.norm(pts, axis=1), 1e-7)
    rhat = pts / r_all[:, None]
    from scipy.interpolate import CubicSpline
    fun = np.zeros((3, nmax, F, len(pts)), complex)             # fTE, fTMt, fTMr at points
    for l in range(L - 1, -1, -1):
        r_lo = 0.0 if l == 0 else radii[l - 1]
        sel = (r_all <= radii[l] + 1e-12) & (r_all > r_lo)
        n_g = max(int(np.ceil((radii[l] - r_lo) / r_step)) + 1, 4)
        rg = np.linspace(max(r_lo, 1e-6), radii[l], n_g)
        res = {}
        for t in "ab":
            u, du, du_o, z, z_o = _layer_shape(sol, l, rg, t, nmax)
            zo = z_o[None, :, None]
            if t == "b":
                ft = Et_o[t][..., None] * u * zo / z[None]
                res["TE"] = ft
            else:
                ft = Et_o[t][..., None] * (du / du_o) * zo / z[None]
                fr = Et_o[t][..., None] * (1j * nn[..., None] * u / du_o) * zo / z[None] ** 2
                res["TMt"], res["TMr"] = ft, fr
            Et_o[t] = ft[..., 0]
        if sel.any():
            for i, key in enumerate(("TE", "TMt", "TMr")):
                fun[i][:, :, sel] = CubicSpline(rg, res[key][1:], axis=-1)(r_all[sel])
    out = np.zeros((F, len(pts), 3), complex)
    ms = np.arange(-nmax, nmax + 1)
    step = 10
    for n0 in range(1, nmax + 1, step):
        n1 = min(n0 + step - 1, nmax)
        y, X, rX = _angular_block(n0, n1, ms, rhat)             # (nb, M, Q[,3])
        s = slice(n0 - 1, n1)
        AM = np.einsum("nm,nmqc->nqc", PTE[s], X)
        ANt = np.einsum("nm,nmqc->nqc", PTM[s], rX)
        ANr = np.einsum("nm,nmq->nq", PTM[s], y)[..., None] * rhat[None]
        out += (np.einsum("nfq,nqc->fqc", fun[0][s], AM)
                + np.einsum("nfq,nqc->fqc", fun[1][s], ANt)
                + np.einsum("nfq,nqc->fqc", fun[2][s], ANr))
    return out
