"""Integrity checks on S-parameter tensors (F, N, N)."""
from __future__ import annotations

import itertools

import numpy as np
from scipy.interpolate import CubicSpline

from .ring import pairs_at_distance


def db(x):
    return 20 * np.log10(np.abs(x))


def reciprocity(s: np.ndarray, f_hz: np.ndarray | None = None, glitch_db: float = -20.0) -> dict:
    """Reciprocity error |Sij - Sji|, absolute and normalised by the band-rms level of Sij
    (so deep nulls do not inflate it). Points with local relative error > glitch_db are
    counted as 'glitches' (isolated non-reciprocal frequency points, typically sweep
    interpolation artefacts); their frequencies are returned."""
    diff = np.abs(s - s.transpose(0, 2, 1))
    n = s.shape[1]
    off = ~np.eye(n, dtype=bool)
    lvl = np.sqrt((np.abs(s[:, off]) ** 2).mean(0))            # band-rms per entry
    rel_band = diff[:, off] / lvl
    rel_local = diff[:, off] / np.maximum(np.abs(s[:, off]), 1e-30)
    bad = rel_local > 10 ** (glitch_db / 20)
    out = {"recip_abs_max": diff.max(), "recip_rel_band_max_db": db(rel_band.max()),
           "recip_rel_band_p99_db": db(np.percentile(rel_band, 99)),
           "recip_rel_band_median_db": db(np.median(rel_band)),
           "n_glitch_pts": int(bad.sum()), "n_pts": bad.size}
    if f_hz is not None:
        out["glitch_f_GHz"] = sorted({round(float(v) / 1e9, 4) for v in f_hz[bad.any(1)]})
    return out


def passivity(s: np.ndarray, tol: float = 1e-3) -> dict:
    col = (np.abs(s) ** 2).sum(axis=1)                 # sum_i |S_ij|^2 per column j
    sv = np.linalg.svd(s, compute_uv=False)[:, 0]
    return {"col_power_max": col.max(), "sigma_max": sv.max(),
            "passive": bool(col.max() <= 1 + tol and sv.max() <= 1 + tol)}


def circulant_spread(s: np.ndarray, port_to_ant: np.ndarray) -> dict:
    """Spread of S(t, t+k) across t, per ring distance k.

    mag_spread_db: max-min of |S| in dB across pairs (per freq) -> median / p95 / max.
    mag_std_db:    std of |S| in dB across pairs, median over freq.
    cplx_rel_db:   rms_t |S_t - mean| / |mean|, median over freq, in dB (= noise-to-signal).
    """
    out = {}
    n = s.shape[1]
    for k in range(n // 2 + 1):
        x = np.stack([s[:, i, j] for i, j in pairs_at_distance(port_to_ant, k)], -1)
        m = db(x)
        spread = m.max(-1) - m.min(-1)
        mean = x.mean(-1, keepdims=True)
        rel = np.sqrt((np.abs(x - mean) ** 2).mean(-1)) / np.abs(mean[..., 0])
        out[k] = {"mag_spread_db_median": np.median(spread),
                  "mag_spread_db_p95": np.percentile(spread, 95),
                  "mag_spread_db_max": spread.max(),
                  "mag_std_db_median": np.median(m.std(-1)),
                  "cplx_rel_db_median": db(np.median(rel)),
                  "level_db_median": np.median(m)}
    return out


def circulant_error(s: np.ndarray, port_to_ant) -> float:
    """Scalar circulant error: mean over f and k>=1 of std_t(|S(t,t+k)| in dB)."""
    n = s.shape[1]
    m = db(s)
    errs = [m[:, [i for i, _ in p], [j for _, j in p]].std(-1).mean()
            for k in range(1, n // 2 + 1) if (p := pairs_at_distance(port_to_ant, k))]
    return float(np.mean(errs))


def mapping_search(s: np.ndarray) -> list[tuple[float, tuple[int, ...]]]:
    """Circulant error for every distinct port->antenna assignment (mod rotation/reflection)."""
    n = s.shape[1]
    seen, res = set(), []
    for perm in itertools.permutations(range(1, n + 1)):
        a = np.asarray(perm) - 1
        canon = min(tuple(((sgn * a + r) % n) + 1) for r in range(n) for sgn in (1, -1))
        if canon in seen:
            continue
        seen.add(canon)
        res.append((circulant_error(s, np.asarray(canon)), canon))
    return sorted(res)


def interp_error(f: np.ndarray, s: np.ndarray) -> dict:
    """Leave-every-other-point-out cubic-spline test on the native grid (spacing doubled,
    so conservative for resampling a 2 MHz grid onto 5 MHz). Error relative to the band-rms
    level of each entry, dB."""
    fit, test = slice(0, None, 2), slice(1, None, 2)
    ft, st = f[fit], s[fit]
    inside = f[test] <= ft[-1]
    pred = (CubicSpline(ft, st.real, axis=0)(f[test][inside])
            + 1j * CubicSpline(ft, st.imag, axis=0)(f[test][inside]))
    true = s[test][inside]
    lvl = np.sqrt((np.abs(s) ** 2).mean(0))                    # band-rms per entry
    rel = np.abs(pred - true) / lvl
    n = s.shape[1]
    diag = rel[:, np.arange(n), np.arange(n)]
    off = rel[:, ~np.eye(n, dtype=bool)]
    return {"interp_rel_diag_max_db": db(diag.max()), "interp_rel_diag_median_db": db(np.median(diag)),
            "interp_rel_off_max_db": db(off.max()), "interp_rel_off_median_db": db(np.median(off))}


def resonance(f: np.ndarray, sii: np.ndarray) -> float:
    """Frequency of min |Sii| with parabolic refinement in dB."""
    m = db(sii)
    i = int(np.argmin(m))
    if 0 < i < len(m) - 1:
        y0, y1, y2 = m[i - 1:i + 2]
        den = y0 - 2 * y1 + y2
        delta = 0.5 * (y0 - y2) / den if den > 0 else 0.0
        return float(f[i] + delta * (f[i + 1] - f[i]))
    return float(f[i])
