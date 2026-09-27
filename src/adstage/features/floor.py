"""Instrument noise-floor estimate and floor-free path powers.

Floor estimate (per complete measurement, no extra hardware):
    For reciprocal pairs, S_ij - S_ji removes the signal. It also removes any per-port gain
    or phase error, since g_i g_j multiplies both entries. What remains are the two independent
    additive floor samples (plus multiplicative noise, which scales with |S| and is negligible
    on weak paths). So E|S_ij - S_ji|^2 = 2 P_floor on the weakest paths. The estimate uses the
    weakest `frac` of the off-diagonal (f, pair) points, ranked by |S_ij||S_ji|. If a dedicated
    noise measurement (ports terminated) is available, its band-averaged |S|^2 replaces this.
    Checked on the noise model: -89.6 / -69.9 / -60.1 / -51.3 dB for true floors of
    -90 / -70 / -60 / -50 dB. The estimate is biased low only once the floor swamps most paths.

Floor subtraction: E|S_meas|^2 = |S|^2 + P_floor, so band-averaged path powers are
debiased as <|S|^2> - P_floor (clipped at CLIP), before taking dB.

M5.R31 (calibration-free):
    R31 = GM_t <|S(t+3,t)|^2> / GM_t <|S(t+1,t)|^2>   (floor-subtracted band averages, GM over
    the ring; reported in dB). A per-port gain g_i multiplies |S_ij|^2 by |g_i|^2 |g_j|^2. Each
    port occurs exactly twice in the product over t of the opposite paths and exactly twice in
    the product of the neighbour paths, so every |g_i| cancels in the ratio. It is one value
    per complete measurement, not per antenna view.
"""
from __future__ import annotations

import numpy as np

from .metrics import band_avg

CLIP = 1e-10          # -100 dB: floor for debiased powers (never take log of <= 0)


def floor_power(D: np.ndarray, frac: float = 0.5) -> np.ndarray:
    """D: (n, F, N, N) -> (n,) estimated floor power per entry (linear)."""
    n, F, N, _ = D.shape
    iu = np.triu_indices(N, 1)
    a, b = D[:, :, iu[0], iu[1]], D[:, :, iu[1], iu[0]]
    d2 = (np.abs(a - b) ** 2).reshape(n, -1)
    lvl = (np.abs(a) * np.abs(b)).reshape(n, -1)
    k = max(1, int(frac * d2.shape[1]))
    sel = np.argpartition(lvl, k - 1, axis=1)[:, :k]
    return np.take_along_axis(d2, sel, 1).mean(1) / 2


def path_power(f: np.ndarray, D: np.ndarray, k: int, band) -> np.ndarray:
    """Band-averaged |S(t+k, t)|^2 per view: (n, N)."""
    N = D.shape[-1]
    idx = np.arange(N)
    p = np.abs(D[..., (idx + k) % N, idx]) ** 2
    return band_avg(f, np.moveaxis(p, -2, -1), band)


def r31(f: np.ndarray, D: np.ndarray, pf: np.ndarray, band) -> np.ndarray:
    """Calibration-free opposite/neighbour ratio (linear), one per measurement: (n,)."""
    N = D.shape[-1]
    c3 = np.maximum(path_power(f, D, N // 2, band) - pf[:, None], CLIP)
    c1 = np.maximum(path_power(f, D, 1, band) - pf[:, None], CLIP)
    return np.exp(np.log(c3).mean(1) - np.log(c1).mean(1))
