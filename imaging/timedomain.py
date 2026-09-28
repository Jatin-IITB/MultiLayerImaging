"""Frequency -> time domain transform and propagation-delay models for radar imaging.

Convention: HFSS e^{+jωt}. A path delay tau appears in S(f) as exp(-j 2 pi f tau), so the
time response h(t) = sum_f W(f) S(f) exp(+j 2 pi f t) peaks at t = tau.
"""
from __future__ import annotations

import numpy as np
from scipy.signal.windows import kaiser

C0 = 299_792_458.0


def window(n: int, kind: str = "hann", beta: float = 6.0) -> np.ndarray:
    if kind == "hann":
        return np.hanning(n + 2)[1:-1]            # strictly positive, symmetric
    if kind == "kaiser":
        return kaiser(n, beta)
    if kind == "rect":
        return np.ones(n)
    raise ValueError(kind)


class TimeResponse:
    """Band-limited analytic time response of spectra X (..., F) on a uniform grid f.

    h(t) = sum_f W(f) X(f) e^{j 2 pi f t} = e^{j 2 pi fc t} * env(t), env from a zero-padded
    IFFT of the spectrum shifted to the band centre fc; the slowly varying env is interpolated
    linearly and the carrier re-applied exactly, so h can be evaluated at arbitrary delays."""

    def __init__(self, f_hz: np.ndarray, X: np.ndarray, kind: str = "hann", nfft: int = 8192,
                 beta: float = 6.0):
        f = np.asarray(f_hz, float)
        df = np.diff(f)
        if not np.allclose(df, df[0], rtol=1e-6):
            raise ValueError("frequency grid must be uniform")
        self.f0, self.df, self.nfft = f[0], df[0], nfft
        self.w = window(f.size, kind, beta)
        Xw = X * self.w
        env = np.fft.ifft(Xw, nfft, axis=-1) * nfft             # sum_f Xw e^{j2pi (f-f0) t}
        self.t = np.arange(nfft) / (nfft * self.df)             # [0, 1/df) periodic
        self.fc = 0.5 * (f[0] + f[-1])
        # centred envelope (slowly varying): env_c = sum_f Xw e^{j2pi (f-fc) t}
        self.env = env * np.exp(-2j * np.pi * (self.fc - self.f0) * self.t)
        self.T = 1 / self.df

    def __call__(self, tau: np.ndarray) -> np.ndarray:
        """h at delays tau [s]. X was (C, F) -> tau (C, K) gives (C, K); X (F,) -> tau (K,)."""
        tau = np.asarray(tau, float)
        if tau.ndim != self.env.ndim:
            raise ValueError("tau must have the same number of dims as X (last axis = delays)")
        u = np.mod(tau, self.T) / (self.T / self.nfft)
        i0 = np.floor(u).astype(int) % self.nfft
        a = u - np.floor(u)
        e0 = np.take_along_axis(self.env, i0, -1)
        e1 = np.take_along_axis(self.env, (i0 + 1) % self.nfft, -1)
        return ((1 - a) * e0 + a * e1) * np.exp(2j * np.pi * self.fc * tau)

    def pulse_width(self) -> float:
        """-6 dB (amplitude) full width of the window's time response [s]."""
        h = np.abs(np.fft.ifft(self.w, self.nfft) * self.nfft)
        h = np.fft.fftshift(h) / h.max()
        return np.sum(h >= 0.5) * self.T / self.nfft


# ----------------------------------------------------------------------------------------------
# Delays
# ----------------------------------------------------------------------------------------------
def delay_effective(a_mm: np.ndarray, pts_mm: np.ndarray, eps_eff: float,
                    r_skin_mm: float = 88.0) -> np.ndarray:
    """One-way delay antenna a -> points (P, 3): vacuum to the skin, eps_eff inside the head
    along the straight line (same ray split as the layered model)."""
    return delay_layered(a_mm, pts_mm, [(r_skin_mm, eps_eff)])


def delay_layered(a_mm: np.ndarray, pts_mm: np.ndarray, layers) -> np.ndarray:
    """One-way straight-ray delay [s] from a (3,) to points (P, 3) through concentric shells.

    layers: [(outer radius mm, eps_r)] core first; vacuum outside the last radius. Each
    segment's length is found from the ray-sphere intersections; speed = c / sqrt(eps_r)."""
    a = np.asarray(a_mm, float)
    P = np.asarray(pts_mm, float).reshape(-1, 3)
    d = P - a
    L = np.linalg.norm(d, axis=1)
    u = d / np.maximum(L, 1e-12)[:, None]
    radii = np.array([r for r, _ in layers], float)
    n_idx = np.sqrt(np.array([e for _, e in layers], float))
    n_out = np.concatenate([n_idx[1:], [1.0]])       # index outside each radius
    # optical path = integral n ds = n_vac*L + sum_l (n_l - n_{l+1}) * chord_len inside r_l
    opl = L.copy()
    b = u @ a                                        # (P,)
    cc = a @ a
    for r, n_in, n_o in zip(radii, n_idx, n_out):
        disc = b ** 2 - (cc - r ** 2)
        ok = disc > 0
        s = np.sqrt(np.where(ok, disc, 0))
        t1 = np.clip(-b - s, 0, L)
        t2 = np.clip(-b + s, 0, L)
        opl += np.where(ok, (n_in - n_o) * (t2 - t1), 0.0)
    return opl * 1e-3 / C0


def pair_list(n: int = 6):
    """21 reciprocal pairs (i <= j), 0-based ports."""
    return [(i, j) for i in range(n) for j in range(i, n)]
