"""Scalar signal metrics M0-M8 (shared method IDs). M9 (full spectrum) lives in prompt 03.

Conventions
-----------
* ``S`` has shape (..., F, N, N) in **ring order** (use ``to_ring_order``): S[..., u, t] is the
  wave out of antenna u when antenna t is driven (column t = driven antenna).
* Power quantities, driven antenna i:  R_i = |S_ii|^2,  T_ji = |S_ji|^2.
* Band averages <P>_B = (1/Δf) ∫_B P df by trapezoid, with P linearly interpolated at band
  edges so the result is continuous in the band limits (needed for the band-choice tests).
* Every metric returns an array (..., n_ant): one value per driven antenna ("per_ant"), or
  (..., 1) for whole-matrix quantities ("matrix"). The simulation-level scalar is the mean
  over the last axis. In this symmetric ring the spread across antennas is numerical noise.

Notes recorded with the definitions
-----------------------------------
* M0 is not a physical quantity. S_ii and S_ij are complex amplitudes of waves leaving
  different ports under different excitations; their sum depends on each port's
  reference-plane phase. Dividing by VSWR, a nonlinear function of |S_ii| that diverges as
  |S_ii| -> 1, mixes scales arbitrarily. The Σ_j runs over j != i.
* M3: A = 1 - |Γ|^2 is already a power ratio, so the mismatch loss is ML = -10 log10(1 - |Γ|^2),
  not 20 log10. <A>_B = 1 - <R>_B exactly, so M3's <A> is affinely identical to M2 and has
  the same separability. It is listed for completeness.
* M4: N_i = 1 - Σ_j T_ji is everything not returned to any port. That is head absorption
  plus radiation escaping to the HFSS radiation boundary plus antenna/substrate loss. It is
  **not** head absorption alone.
* M8: 1 - s_k^2 and 1 - |λ_m|^2 are affine in s_k^2 and |λ_m|^2 (identical separability), so
  only the power forms are listed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

Band = tuple[float, float]


# ----------------------------------------------------------------------------- helpers
def to_ring_order(S: np.ndarray, port_to_ant: np.ndarray) -> np.ndarray:
    """Reorder ports so index a is antenna T(a+1) (consecutive around the ring)."""
    order = np.argsort(np.asarray(port_to_ant))          # order[a] = port index of antenna a+1
    return S[..., order[:, None], order[None, :]]


def band_avg(f: np.ndarray, P: np.ndarray, band: Band) -> np.ndarray:
    """Band average along the frequency axis, which is axis -1 of P (shape (..., F))."""
    lo, hi = max(band[0], f[0]), min(band[1], f[-1])
    inner = (f > lo) & (f < hi)
    fe = np.concatenate([[lo], f[inner], [hi]])
    lo_v = _interp_at(f, P, lo)
    hi_v = _interp_at(f, P, hi)
    Pe = np.concatenate([lo_v[..., None], P[..., inner], hi_v[..., None]], axis=-1)
    return np.trapezoid(Pe, fe, axis=-1) / (hi - lo)


def _interp_at(f: np.ndarray, P: np.ndarray, x: float) -> np.ndarray:
    k = int(np.clip(np.searchsorted(f, x) - 1, 0, len(f) - 2))
    w = (x - f[k]) / (f[k + 1] - f[k])
    return (1 - w) * P[..., k] + w * P[..., k + 1]


def _fa(x: np.ndarray) -> np.ndarray:
    """(..., F, n) -> (..., n, F) so band_avg can integrate the last axis."""
    return np.moveaxis(x, -2, -1)


def ring_distance_matrix(n: int) -> np.ndarray:
    a = np.arange(n)
    d = np.abs(a[:, None] - a[None, :]) % n
    return np.minimum(d, n - d)


def circulant_projection(S: np.ndarray) -> np.ndarray:
    """Replace each entry by the ring mean of its ring distance (symmetrised reference)."""
    n = S.shape[-1]
    d = ring_distance_matrix(n)
    out = np.empty_like(S)
    for k in range(n // 2 + 1):
        m = d == k
        out[..., m] = S[..., m].mean(-1, keepdims=True)
    return out


# ----------------------------------------------------------------------------- spectra
def power_spectra(S: np.ndarray) -> dict[str, np.ndarray]:
    """Per-antenna power spectra, each shaped (..., F, n_ant)."""
    P = np.abs(S) ** 2
    n = S.shape[-1]
    R = np.diagonal(P, axis1=-2, axis2=-1)
    col = P.sum(-2)                                   # Σ_j T_ji (column sums)
    out = {"R": R, "A": 1 - R, "N": 1 - col, "C": col - R}
    for k in range(1, n // 2 + 1):
        idx = np.arange(n)
        out[f"C{k}"] = 0.5 * (P[..., (idx + k) % n, idx] + P[..., (idx - k) % n, idx])
    return out


def modal_reflections(S: np.ndarray) -> np.ndarray:
    """Per-antenna circulant modal values λ_m^(t)(f) = Σ_k S(t+k, t) e^{-j2πmk/N}.

    Returns (..., F, N_modes=N, n_ant). For an exactly circulant S these are the
    eigenvalues and do not depend on t. Their spread over t is the port noise."""
    n = S.shape[-1]
    idx = np.arange(n)
    cols = np.stack([S[..., (idx + k) % n, idx] for k in range(n)], -2)  # (..., F, k, t)
    W = np.exp(-2j * np.pi * np.outer(np.arange(n), np.arange(n)) / n)  # (m, k)
    return np.einsum("mk,...kt->...mt", W, cols)


# ----------------------------------------------------------------------------- catalogue
@dataclass(frozen=True)
class Metric:
    name: str                 # unique scalar name, e.g. "M5.C3[k3]"
    method_id: str            # shared method ID
    desc: str
    level: str                # "per_ant" | "matrix"
    band: str                 # key into the band dict ("full", "k3", "sb3.20", ...)
    fn: Callable              # fn(ctx, band) -> (..., n_ant) or (..., 1)
    note: str = ""


class Context:
    """Lazy per-batch cache of spectra, so many metrics share one computation."""

    def __init__(self, f: np.ndarray, S: np.ndarray, ref: np.ndarray | None):
        self.f, self.S, self.ref = f, S, ref
        self._c: dict = {}

    def get(self, key, fn):
        if key not in self._c:
            self._c[key] = fn()
        return self._c[key]

    @property
    def spec(self):
        return self.get("spec", lambda: power_spectra(self.S))

    @property
    def sv2(self):
        return self.get("sv2", lambda: np.linalg.svd(self.S, compute_uv=False) ** 2)

    @property
    def modal2(self):
        return self.get("modal2", lambda: np.abs(modal_reflections(self.S)) ** 2)


def _avg(ctx, key, b):
    return band_avg(ctx.f, _fa(ctx.spec[key]), b)


def _m0(ctx, b):
    S = ctx.S
    n = S.shape[-1]
    g = np.abs(np.diagonal(S, axis1=-2, axis2=-1))                    # (..., F, n)
    vswr = (1 + g) / np.maximum(1 - g, 1e-12)
    sii = np.diagonal(S, axis1=-2, axis2=-1)[..., :, None]            # (..., F, i, 1)
    tot = np.abs(sii + S)                                             # |S_ii + S_ij|
    tot = tot.sum(-1) - np.abs(2 * np.diagonal(S, axis1=-2, axis2=-1))  # drop j = i
    return band_avg(ctx.f, _fa(tot / vswr), b)


def _m1(ctx, b):
    sii = np.abs(np.diagonal(ctx.S, axis1=-2, axis2=-1))
    return band_avg(ctx.f, _fa(20 * np.log10(np.maximum(sii, 1e-12))), b)


def _centroid(ctx, key, b, what):
    f = ctx.f
    P = _fa(ctx.spec[key])
    w0 = band_avg(f, P, b)
    w1 = band_avg(f, P * f, b)
    fc = w1 / w0
    if what == "fc":
        return fc / 1e9
    w2 = band_avg(f, P * f ** 2, b)
    return np.sqrt(np.maximum(w2 / w0 - fc ** 2, 0)) / 1e6


def _d_complex(ctx, b, k=None):
    diff = np.abs(ctx.S - ctx.ref) ** 2                               # (..., F, u, t)
    n = diff.shape[-1]
    if k is None:
        per = diff.sum(-2)
    else:
        idx = np.arange(n)
        per = 0.5 * (diff[..., (idx + k) % n, idx] + diff[..., (idx - k) % n, idx])
    return band_avg(ctx.f, _fa(per), b)


def _d_power(ctx, b):
    diff = (np.abs(ctx.S) ** 2 - np.abs(ctx.ref) ** 2) ** 2
    return band_avg(ctx.f, _fa(diff.sum(-2)), b)


def _sv(ctx, b, k):
    return band_avg(ctx.f, ctx.sv2[..., k], b)[..., None]


def _modal(ctx, b, m):
    M = ctx.modal2                                                    # (..., F, m, t)
    n = M.shape[-2]
    x = M[..., m, :] if m in (0, n // 2) else 0.5 * (M[..., m, :] + M[..., n - m, :])
    return band_avg(ctx.f, _fa(x), b)


def build_catalogue(f: np.ndarray, k3_band: Band, subband_hz: float, n: int = 6
                    ) -> tuple[list[Metric], dict[str, Band]]:
    full = (float(f[0]), float(f[-1]))
    bands = {"full": full, "k3": tuple(k3_band)}
    edges = np.arange(full[0], full[1] - 1, subband_hz)
    for lo in edges:
        bands[f"sb{lo / 1e9:.2f}"] = (lo, min(lo + subband_hz, full[1]))

    M: list[Metric] = [
        Metric("M0.old_score", "M0", "mean_B Σ_{j≠i}|S_ii+S_ij|/VSWR_i", "per_ant", "full", _m0,
               "baseline only; not a physical quantity"),
        Metric("M1.Sii_dBavg", "M1", "mean_B 20log10|S_ii|", "per_ant", "full", _m1,
               "dB averaging; shown for fragility"),
        Metric("M2.R", "M2", "<|S_ii|^2>_B", "per_ant", "full", lambda c, b: _avg(c, "R", b)),
        Metric("M2.R[k3]", "M2", "<|S_ii|^2> over k3 window", "per_ant", "k3",
               lambda c, b: _avg(c, "R", b)),
        Metric("M3.A", "M3", "<1-|S_ii|^2>_B", "per_ant", "full", lambda c, b: _avg(c, "A", b),
               "affine copy of M2.R (identical separability)"),
        Metric("M3.ML_of_powavg", "M3", "-10log10<A>_B (dB)", "per_ant", "full",
               lambda c, b: -10 * np.log10(_avg(c, "A", b))),
        Metric("M3.ML_dBavg", "M3", "<-10log10 A>_B (dB-averaged ML)", "per_ant", "full",
               lambda c, b: band_avg(c.f, _fa(-10 * np.log10(np.maximum(c.spec["A"], 1e-12))), b),
               "dB averaging; comparison only"),
        Metric("M4.N", "M4", "<1-Σ_j|S_ji|^2>_B (absorbed+radiated+loss)", "per_ant", "full",
               lambda c, b: _avg(c, "N", b)),
        Metric("M4.N[k3]", "M4", "<N> over k3 window", "per_ant", "k3",
               lambda c, b: _avg(c, "N", b)),
    ]
    for bn in ("full", "k3"):
        sfx = "" if bn == "full" else "[k3]"
        M.append(Metric(f"M5.C{sfx}", "M5", f"<Σ_(j≠i)|S_ji|^2> ({bn})", "per_ant", bn,
                        lambda c, b: _avg(c, "C", b)))
        for k in range(1, n // 2 + 1):
            M.append(Metric(f"M5.C{k}{sfx}", "M5", f"<|S_(i±{k},i)|^2> ({bn})", "per_ant", bn,
                            lambda c, b, k=k: _avg(c, f"C{k}", b)))
    M.append(Metric("M5.C3_dBavg[k3]", "M5", "mean over k3 window of 10log10|S_(i+3,i)|^2",
                    "per_ant", "k3",
                    lambda c, b: band_avg(c.f, _fa(10 * np.log10(np.maximum(c.spec["C3"], 1e-30))), b),
                    "dB averaging; comparison only"))
    for key in ("A", "N"):
        M.append(Metric(f"M6.fc_{key}", "M6", f"power-weighted centroid of {key}(f) [GHz]",
                        "per_ant", "full", lambda c, b, key=key: _centroid(c, key, b, "fc")))
        M.append(Metric(f"M6.spread_{key}", "M6", f"spectral spread of {key}(f) [MHz]",
                        "per_ant", "full", lambda c, b, key=key: _centroid(c, key, b, "sd")))
    for bn in bands:
        if bn.startswith("sb"):
            for key in ("A", "N"):
                M.append(Metric(f"M6.{key}[{bn[2:]}]", "M6", f"<{key}> in 50 MHz sub-band from "
                                f"{bn[2:]} GHz", "per_ant", bn,
                                lambda c, b, key=key: _avg(c, key, b)))
    M += [
        Metric("M7.D", "M7", "<Σ_j|S_ji - S_ref,ji|^2>_B, ref = circulant(Normal)", "per_ant",
               "full", lambda c, b: _d_complex(c, b)),
        Metric("M7.D_pow", "M7", "<Σ_j(|S_ji|^2 - |S_ref,ji|^2)^2>_B (phase-free)", "per_ant",
               "full", _d_power),
    ]
    for k in range(n // 2 + 1):
        M.append(Metric(f"M7.D{k}", "M7", f"<|S_(i±{k},i) - ref|^2>_B", "per_ant", "full",
                        lambda c, b, k=k: _d_complex(c, b, k)))
    M.append(Metric("M7.D3[k3]", "M7", "<|S_(i+3,i) - ref|^2> over k3 window", "per_ant", "k3",
                    lambda c, b: _d_complex(c, b, 3)))
    for k in range(n):
        M.append(Metric(f"M8.s{k + 1}^2", "M8", f"<s_{k + 1}(S)^2>_B (singular value)",
                        "matrix", "full", lambda c, b, k=k: _sv(c, b, k),
                        "matrix-level: no per-antenna port-noise estimate"))
    for bn in ("full", "k3"):
        sfx = "" if bn == "full" else "[k3]"
        for m in range(n // 2 + 1):
            M.append(Metric(f"M8.lam{m}^2{sfx}", "M8", f"<|λ_{m}|^2> circulant mode {m} ({bn})",
                            "per_ant", bn, lambda c, b, m=m: _modal(c, b, m)))
    return M, bands


def compute(metrics: list[Metric], bands: dict[str, Band], f: np.ndarray, S: np.ndarray,
            ref: np.ndarray | None, band_fn: Callable[[Band], Band] | None = None
            ) -> dict[str, np.ndarray]:
    """Evaluate every metric on a batch S (..., F, N, N) in ring order."""
    ctx = Context(f, S, ref)
    out = {}
    for m in metrics:
        b = bands[m.band] if band_fn is None else band_fn(bands[m.band])
        out[m.name] = m.fn(ctx, b)
    return out
