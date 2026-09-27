"""Frequency-robustness and fault tests for scalar metrics (prompt 02, section 2).

Every perturbation is applied to the noise-free (masked) simulations. For each metric we
report the largest change of the simulation-level value (ring mean) over all simulations, in
units of the class gaps. Fault cases (open / short / one antenna open) report whether the
value stays defined and whether it lands inside the range of real class values, where it
would be silently classified.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter1d

from .features.metrics import compute
from .noise.model import shift_spectrum

SHIFTS_MHZ = [-20, -10, -5, -2, 2, 5, 10, 20]
FREQ_ROBUST_SET = ["shift-10", "shift-5", "shift-2", "shift+2", "shift+5", "shift+10",
                   "band_shrink10", "band_lo10", "band_hi10"]


def _band_perturbations(full):
    def shrink(b):
        w = b[1] - b[0]
        return (b[0] + 0.05 * w, b[1] - 0.05 * w)

    def move(sign):
        def fn(b):
            w = b[1] - b[0]
            lo, hi = b[0] + sign * 0.1 * w, b[1] + sign * 0.1 * w
            return (max(lo, full[0]), min(hi, full[1]))       # clipped to available data
        return fn

    def replace(new):
        return lambda b: new if b == full else b                # full-band metrics only

    return {"band_shrink10": shrink, "band_lo10": move(-1), "band_hi10": move(+1),
            "band_3.3-4.1": replace((3.3e9, 4.1e9)), "band_3.4-3.9": replace((3.4e9, 3.9e9)),
            "band_3.2-3.5_nodip": replace((3.2e9, 3.5e9))}


def _flatten(f, S, window_hz=60e6):
    """|S_ii| -> running max over window (removes the notch), phase kept."""
    n = S.shape[-1]
    w = int(round(window_hz / np.median(np.diff(f)))) + 1
    out = S.copy()
    for i in range(n):
        s = S[:, i, i]
        out[:, i, i] = maximum_filter1d(np.abs(s), w, mode="nearest") * np.exp(1j * np.angle(s))
    return out


def _fault(S, kind, rng, antennas=None):
    F, n, _ = S.shape
    out = S.copy()
    ants = range(n) if antennas is None else antennas
    gam = {"open": 1.0, "short": -1.0}[kind]
    for i in ants:
        out[:, i, i] = gam * (1 + 0.01 * rng.standard_normal(F)) * np.exp(1j * 0.02 * rng.standard_normal(F))
        for j in range(n):
            if j != i:
                fl = 10 ** (-90 / 20) / np.sqrt(2) * (rng.standard_normal(F) + 1j * rng.standard_normal(F))
                out[:, i, j] = fl
                out[:, j, i] = fl
    return out


def perturbed_values(metrics, bands, f, S_sims, ref, seed=0):
    """-> {perturbation: {metric: (n_sims,) ring-mean values}} incl. 'orig'."""
    rng = np.random.default_rng(seed)
    full = bands["full"]

    def ev(Ss, band_fn=None):
        vals = [compute(metrics, bands, f, s, ref, band_fn) for s in Ss]
        return {m.name: np.array([v[m.name].mean() for v in vals]) for m in metrics}

    out = {"orig": ev(S_sims)}
    for d in SHIFTS_MHZ:
        out[f"shift{d:+d}"] = ev([shift_spectrum(f, s, d * 1e6) for s in S_sims])
    for name, fn in _band_perturbations(full).items():
        out[name] = ev(S_sims, fn)
    out["flatten_notch"] = ev([_flatten(f, s) for s in S_sims])
    for d in (-200, 200):
        out[f"detune{d:+d}"] = ev([shift_spectrum(f, s, d * 1e6) for s in S_sims])
    out["open_all"] = ev([_fault(s, "open", rng) for s in S_sims])
    out["short_all"] = ev([_fault(s, "short", rng) for s in S_sims])
    out["one_open"] = ev([_fault(s, "open", rng, antennas=[0]) for s in S_sims])
    return out
