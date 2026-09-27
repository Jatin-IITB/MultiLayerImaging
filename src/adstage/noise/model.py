"""Measurement-noise model for S-parameter spectra.

Per realisation, applied to every entry (f, i, j) independently (a VNA measures Sij and Sji
separately):

    S' = S(f - δ) · 10^(g/20) · e^{jφ} + a,
    g ~ N(0, σ_dB),  φ ~ N(0, σ_deg),  a ~ CN(0, 10^(L_dB/10))   (complex floor, rms 10^(L/20))
    δ ~ N(0, σ_MHz)  — one global frequency shift per realisation (session / placement drift).

Shifts are evaluated by a cubic spline on Re/Im over the available grid with edge hold
beyond it (``shift_spectrum``).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicSpline


@dataclass(frozen=True)
class NoiseProfile:
    name: str
    sigma_db: float
    sigma_deg: float
    floor_db: float
    jitter_mhz: float = 0.0


PROFILES = {p.name: p for p in [
    NoiseProfile("ideal", 0.05, 0.5, -90, 0),
    NoiseProfile("good", 0.1, 1, -80, 0),
    NoiseProfile("typical", 0.25, 2, -70, 0),
    NoiseProfile("noisy", 0.5, 5, -60, 0),
    NoiseProfile("very_noisy", 1.0, 10, -50, 0),
    NoiseProfile("typical_jitter", 0.25, 2, -70, 3),
]}


def shift_spectrum(f: np.ndarray, S: np.ndarray, delta_hz: float | np.ndarray) -> np.ndarray:
    """S_shifted(f) = S(f - δ). S: (F, ...) or batch; δ scalar or (R,) -> (R, F, ...)."""
    cs_re = CubicSpline(f, S.real, axis=0)
    cs_im = CubicSpline(f, S.imag, axis=0)
    d = np.atleast_1d(delta_hz)
    x = np.clip(f[None, :] - d[:, None], f[0], f[-1])            # (R, F), edge hold
    out = cs_re(x) + 1j * cs_im(x)                                # (R, F, ...)
    return out if np.ndim(delta_hz) else out[0]


def realise(f: np.ndarray, S: np.ndarray, prof: NoiseProfile, n: int,
            rng: np.random.Generator) -> np.ndarray:
    """n noisy copies of S (F, N, N) -> (n, F, N, N)."""
    if prof.jitter_mhz > 0:
        base = shift_spectrum(f, S, rng.normal(0, prof.jitter_mhz * 1e6, n))
    else:
        base = np.broadcast_to(S, (n, *S.shape))
    shp = base.shape
    g = 10 ** (rng.normal(0, prof.sigma_db, shp) / 20)
    ph = np.exp(1j * np.deg2rad(rng.normal(0, prof.sigma_deg, shp)))
    fl = 10 ** (prof.floor_db / 20) / np.sqrt(2)
    a = fl * (rng.standard_normal(shp) + 1j * rng.standard_normal(shp))
    return base * g * ph + a
