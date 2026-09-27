"""Detect and mask frequency-sweep glitches on the native grid.

A glitch is a (f, i, j) point where the pair violates reciprocity by more than ``thr_db``
relative to the pair's band-RMS level: |Sij - Sji| > 10^(thr_db/20) * rms_f(|S|) (geometric
mean of the two entries' levels). Normalising by the band level, not the local |Sij|, stops
deep nulls from triggering. In these HFSS files glitches appear as contiguous bumps of
3-8 points on a single antenna pair.

Masking: both Sij and Sji are replaced over each contiguous run by complex linear
interpolation between the nearest unflagged neighbours (edge hold at band ends).
"""
from __future__ import annotations

import numpy as np


def detect_glitches(s: np.ndarray, thr_db: float = -30.0) -> np.ndarray:
    """Boolean (F, N, N) mask, symmetric in (i, j), diagonal always False."""
    lvl = np.sqrt((np.abs(s) ** 2).mean(0))
    lvl = np.sqrt(lvl * lvl.T)
    err = np.abs(s - s.transpose(0, 2, 1)) / np.maximum(lvl, 1e-30)
    bad = err > 10 ** (thr_db / 20)
    n = s.shape[1]
    bad[:, np.arange(n), np.arange(n)] = False
    return bad


def _runs(idx: np.ndarray) -> list[np.ndarray]:
    if idx.size == 0:
        return []
    return np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1)


def mask_glitches(f_hz: np.ndarray, s: np.ndarray, thr_db: float = -30.0
                  ) -> tuple[np.ndarray, list[dict]]:
    """Return (masked copy of s, log rows). Log has one row per masked (f, i, j), i < j."""
    bad = detect_glitches(s, thr_db)
    out = s.copy()
    log = []
    lvl = np.sqrt((np.abs(s) ** 2).mean(0))
    n = s.shape[1]
    for i in range(n):
        for j in range(i + 1, n):
            good = ~bad[:, i, j]
            for run in _runs(np.flatnonzero(bad[:, i, j])):
                lo, hi = run[0] - 1, run[-1] + 1
                for (a, b) in ((i, j), (j, i)):
                    if lo >= 0 and hi < len(f_hz):
                        w = (f_hz[run] - f_hz[lo]) / (f_hz[hi] - f_hz[lo])
                        out[run, a, b] = (1 - w) * s[lo, a, b] + w * s[hi, a, b]
                    else:                                   # run touches a band edge
                        k = hi if lo < 0 else lo
                        out[run, a, b] = s[k, a, b]
                ref = np.sqrt(lvl[i, j] * lvl[j, i])
                for q in run:
                    log.append({"f_GHz": f_hz[q] / 1e9, "port_i": i + 1, "port_j": j + 1,
                                "recip_err_db": 20 * np.log10(abs(s[q, i, j] - s[q, j, i]) / ref),
                                "Sij_before": s[q, i, j], "Sji_before": s[q, j, i],
                                "S_after": out[q, i, j], "run_start_GHz": f_hz[run[0]] / 1e9,
                                "run_len": len(run)})
            assert good.any()
    return out, log
