"""Noisy measurement draws = setup perturbation + prompt-02 measurement noise.

Setup perturbation, per draw (physically motivated, reciprocity preserved):
    S_ij' = g_i g_j S_ij(f - δ),   g_i = (1 + ε_i) e^{jφ_i}
    ε_i ~ N(0, amp_sd)     cable/connector amplitude variation per antenna (±1-2 %)
    G_i ~ U(-X, X) dB      optional per-port amplitude calibration error (gain_err_db = X)
    φ_i ~ N(0, phase_sd)   residual reference-plane phase per port (frequency independent)
    δ   ~ N(0, jitter)     small frequency jitter (added to the profile's own jitter)
Then the NoiseProfile (magnitude, phase, complex floor, profile jitter) is applied.

No mixing between classes and no synthetic heads. Views ("one per driven antenna") are
produced later by indexing the antenna axis of the features. They are NOT independent
samples: they share the simulation, and by reciprocity they share paths.
"""
from __future__ import annotations

import numpy as np

from ..noise.model import NoiseProfile, realise, shift_spectrum


def setup_perturb(f, S, n, rng, amp_sd=0.015, phase_sd_deg=10.0, jitter_mhz=1.0, gain_err_db=0.0,
                  phase_err_deg=0.0):
    """S (F, N, N) -> (n, F, N, N). phase_err_deg: extra per-port phase error, uniform ±X deg."""
    N = S.shape[-1]
    base = shift_spectrum(f, S, rng.normal(0, jitter_mhz * 1e6, n)) if jitter_mhz > 0 else \
        np.broadcast_to(S, (n, *S.shape)).copy()
    g = (1 + rng.normal(0, amp_sd, (n, N))) * np.exp(1j * np.deg2rad(rng.normal(0, phase_sd_deg, (n, N))))
    if gain_err_db > 0:
        g = g * 10 ** (rng.uniform(-gain_err_db, gain_err_db, (n, N)) / 20)
    if phase_err_deg > 0:
        g = g * np.exp(1j * np.deg2rad(rng.uniform(-phase_err_deg, phase_err_deg, (n, N))))
    return base * g[:, None, :, None] * g[:, None, None, :]


def draws(f, S, prof: NoiseProfile, n, rng, acfg: dict | None = None):
    """n full noisy measurements of one simulation -> (n, F, N, N)."""
    acfg = acfg or {}
    out = np.empty((n, *S.shape), complex)
    pert = setup_perturb(f, S, n, rng, float(acfg.get("amp_sd", 0.015)),
                         float(acfg.get("phase_sd_deg", 10.0)), float(acfg.get("jitter_mhz", 1.0)),
                         float(acfg.get("gain_err_db", 0.0)), float(acfg.get("phase_err_deg", 0.0)))
    for i in range(n):                        # profile noise (and profile jitter) per draw
        out[i] = realise(f, pert[i], prof, 1, rng)[0]
    return out
