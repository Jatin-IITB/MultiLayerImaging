"""Ring-symmetrised measurement-level features used by prompt 04 and the frozen rule.

features(f, D) -> X (n, p), names, groups, singles  (see scripts/04_likelihood.py docstring)
ratios(f, D, bands) -> dict of R31, R21, R32 (dB) on an arbitrary union of bands
"""
from __future__ import annotations

import numpy as np

from .floor import CLIP, floor_power
from .metrics import band_avg, ring_distance_matrix


def features(f, D, subband_hz=50e6):
    """D (n, F, N, N) ring order -> X (n, p), names, groups."""
    n, F, N, _ = D.shape
    band = (float(f[0]), float(f[-1]))
    sbs = [(lo, min(lo + subband_hz, f[-1])) for lo in np.arange(f[0], f[-1] - 1, subband_hz)]
    P = np.abs(D) ** 2
    pf = floor_power(D)
    dist = ring_distance_matrix(N)
    cols, names = [], []
    groups = {"G_refl": [], "G_coup": [], "G_ratio": [], "G_all": []}

    def add(v, name, grp):
        groups[grp].append(len(names))
        groups["G_all"].append(len(names))
        cols.append(v)
        names.append(name)

    for k in range(N // 2 + 1):
        Pk = P[:, :, dist == k].mean(-1)                           # (n, F) ring-symmetrised
        if k:
            Pk = np.maximum(Pk - pf[:, None], CLIP)
        grp = "G_refl" if k == 0 else "G_coup"
        for lo, hi in sbs:
            add(10 * np.log10(band_avg(f, Pk, (lo, hi))), f"k{k}_sb{lo / 1e9:.2f}", grp)
        add(10 * np.log10(band_avg(f, Pk, band)), f"k{k}_band", grp)
    idx = np.arange(N)

    def path(k):                                                  # one direction, per antenna
        p = P[:, :, (idx + k) % N, idx]                            # (n, F, N)
        return np.maximum(band_avg(f, np.moveaxis(p, 1, 2), band) - pf[:, None], CLIP)

    lg = {k: np.log(path(k)).mean(1) for k in (1, 2, 3)}          # log geometric means
    for a, b in ((3, 1), (2, 1), (3, 2)):
        add(10 / np.log(10) * (lg[a] - lg[b]), f"R{a}{b}", "G_ratio")
    Nabs = band_avg(f, (1 - P.sum(-2)).mean(-1), band)
    add(Nabs, "N", "G_refl")
    add(10 * np.log10(np.maximum(Nabs, 1e-12)), "logN", "G_refl")
    X = np.stack(cols, 1)
    singles = {"R31": [names.index("R31")], "C3": [names.index("k3_band")],
               "C2": [names.index("k2_band")]}
    return X, names, groups, singles



def ratios(f, D, bands):
    """R31, R21, R32 (dB) per draw, with path powers averaged over a union of bands
    (width-weighted) and floor-subtracted before the geometric means."""
    N = D.shape[-1]
    P = np.abs(D) ** 2
    pf = floor_power(D)
    idx = np.arange(N)
    w = np.array([hi - lo for lo, hi in bands])

    def path(k):
        p = np.moveaxis(P[:, :, (idx + k) % N, idx], 1, 2)          # (n, N, F)
        avg = sum(wi * band_avg(f, p, b) for wi, b in zip(w, bands)) / w.sum()
        return np.maximum(avg - pf[:, None], CLIP)

    lg = {k: np.log(path(k)).mean(1) for k in (1, 2, 3)}
    c = 10 / np.log(10)
    return {"R31": c * (lg[3] - lg[1]), "R21": c * (lg[2] - lg[1]), "R32": c * (lg[3] - lg[2])}
