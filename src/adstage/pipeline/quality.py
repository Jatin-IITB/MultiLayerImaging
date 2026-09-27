"""Measurement quality gate. Runs before any classification; a failed gate -> INVALID + reasons.

All checks are vectorised over a batch of full measurements S (n, F, N, N) in ring order.
Thresholds live in config.yaml (gate:). The checks are class-agnostic (no disease labels),
but the thresholds were set by looking at clean noisy copies of these four simulations.

Checks
------
open_short   any antenna with band power-average <|S_ii|^2> > R_max (≈ -1 dB), or |S_ii| nearly
             constant across the band (std_f |S_ii| < flat_sd). Per antenna, so a single
             open / short / lifted antenna is caught.
passivity    column power sum Σ_j |S_ji|^2 > 1 + tol in any 50 MHz sub-band. Sub-band averaging
             stops ordinary amplitude noise near |S_ii| ≈ 0.95 from triggering it.
reciprocity  median over f and ring-neighbour pairs of |S_ij - S_ji| / mean(|S_ij|, |S_ji|)
             > recip_rel_max (broken cable / swapped port / floor-dominated coupling).
symmetry     (ring only) median over f of std_t 20log10|S(t+k,t)| > sym_db[k] for k = 0, 1:
             one antenna behaving unlike the others (placement / contact error).
detune       ring-mean accepted-power centroid outside μ_Normal ± max(k·σ_Normal, w_min),
             μ and σ learned from Normal training data (fit_detune).
Modes
-----
full            all checks above (assumes a calibrated instrument).
gain_invariant  only checks that per-port gain errors (S_ij -> g_i g_j S_ij) cannot trip, for
                calibration-free features (M5.R31): open/short by RELATIVE flatness
                std_f|S_ii| / mean_f|S_ii| < flat_rel (gain-free), reciprocity (g_i g_j is
                symmetric), floor, and detune by the ring-median NOTCH frequency
                (argmin_f |S_ii|, unchanged by a frequency-independent gain) instead of
                the accepted-power centroid. Absolute reflection level, passivity and
                symmetry assume calibrated magnitudes and are skipped.

floor        instrument floor too high: the measurement's own floor estimate
             (features.floor.floor_power, from reciprocal-pair differences) must be at least
             floor_margin_db below the decision threshold τ of the transmission feature
             (set_floor_limit(τ); τ comes from training data).
"""
from __future__ import annotations

import numpy as np

from ..features.floor import floor_power
from ..features.metrics import band_avg

REASONS = ["open_short", "passivity", "reciprocity", "symmetry", "detune", "floor"]


def _db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-15))


class QualityGate:
    def __init__(self, gcfg: dict, f: np.ndarray, subband_hz: float = 50e6, mode: str = "full"):
        if mode not in ("full", "gain_invariant"):
            raise ValueError(mode)
        self.mode = mode
        self.c = {k: (float(v) if not isinstance(v, (list, dict)) else v) for k, v in gcfg.items()}
        self.f = f
        self.band = (float(f[0]), float(f[-1]))
        edges = np.arange(f[0], f[-1] - 1, subband_hz)
        self.subbands = [(lo, min(lo + subband_hz, f[-1])) for lo in edges]
        self.fc_mu = self.fc_sd = None
        self.floor_limit_db = None

    def set_floor_limit(self, tau_db: float) -> "QualityGate":
        self.floor_limit_db = float(tau_db) - float(self.c.get("floor_margin_db", 8.0))
        return self

    # ------------------------------------------------------------------ helpers
    def fc_ring(self, S: np.ndarray) -> np.ndarray:
        if self.mode == "gain_invariant":                                 # notch frequency, gain-free
            sii = np.abs(np.diagonal(S, axis1=-2, axis2=-1))              # (n, F, N)
            return np.median(self.f[np.argmin(sii, axis=-2)], axis=-1)
        A = 1 - np.abs(np.diagonal(S, axis1=-2, axis2=-1)) ** 2          # (n, F, N)
        A = np.moveaxis(A, -2, -1)                                        # (n, N, F)
        fc = band_avg(self.f, A * self.f, self.band) / band_avg(self.f, A, self.band)
        return fc.mean(-1)

    def fit_detune(self, S_normal: np.ndarray) -> "QualityGate":
        fc = self.fc_ring(S_normal)
        self.fc_mu, self.fc_sd = float(fc.mean()), float(fc.std(ddof=1))
        return self

    # ------------------------------------------------------------------ checks
    def check(self, S: np.ndarray) -> dict[str, np.ndarray]:
        """-> {reason: (n,) bool (True = failed)} plus 'invalid' and 'bad_antenna' (n, N)."""
        c = self.c
        n_ant = S.shape[-1]
        sii = np.abs(np.diagonal(S, axis1=-2, axis2=-1))                  # (n, F, N)
        R = band_avg(self.f, np.moveaxis(sii ** 2, -2, -1), self.band)    # (n, N)
        if self.mode == "full":
            bad_ant = (R > c["open_short_R"]) | (sii.std(-2) < c["flat_sd"])
        else:
            bad_ant = sii.std(-2) / np.maximum(sii.mean(-2), 1e-12) < c.get("flat_rel", 0.1)
        out = {"open_short": bad_ant.any(-1)}

        col = np.moveaxis((np.abs(S) ** 2).sum(-2), -2, -1)               # (n, N, F)
        sb = np.stack([band_avg(self.f, col, b) for b in self.subbands], -1)
        out["passivity"] = (sb > 1 + c["passivity_tol"]).any(axis=(-1, -2))

        idx = np.arange(n_ant)
        a = S[..., (idx + 1) % n_ant, idx]                                # S(t+1, t)
        b = S[..., idx, (idx + 1) % n_ant]                                # S(t, t+1)
        rel = np.abs(a - b) / np.maximum(0.5 * (np.abs(a) + np.abs(b)), 1e-15)
        out["reciprocity"] = np.median(rel.reshape(rel.shape[0], -1), -1) > c["recip_rel_max"]

        sym = np.zeros(S.shape[0], bool)
        for k, thr in enumerate(c["sym_db"]):
            x = _db(S[..., (idx + k) % n_ant, idx])                       # (n, F, N)
            sym |= np.median(x.std(-1), -1) > float(thr)
        out["symmetry"] = sym

        if self.mode == "gain_invariant":
            for r in ("passivity", "symmetry"):
                out[r] = np.zeros(S.shape[0], bool)
        if self.fc_mu is None:
            out["detune"] = np.zeros(S.shape[0], bool)
        else:
            w = max(c["detune_k_sigma"] * self.fc_sd, c["detune_min_window_hz"])
            out["detune"] = np.abs(self.fc_ring(S) - self.fc_mu) > w
        floor_db = 10 * np.log10(np.maximum(floor_power(S), 1e-30))
        out["floor"] = (floor_db > self.floor_limit_db if self.floor_limit_db is not None
                        else np.zeros(S.shape[0], bool))
        out["invalid"] = np.any([out[r] for r in REASONS], axis=0)
        out["floor_db"] = floor_db
        out["bad_antenna"] = bad_ant
        return out
