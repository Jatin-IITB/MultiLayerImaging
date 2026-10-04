"""Numerical-noise ruler from the mesh pairs (two meshes of one design, each against its own
stop-rule-matched healthy reference).

For a design with meshes a, b: dd = (L_a - L_b), L = ln(S / S_ref,matched). If one observation
carries noise sd s, Var(dd) = 2 s^2. The healthy pair gives L = ln(H7 / H6) directly (one sample
of an observation of 'no change'). Per path type (reflection, neighbour, 2nd neighbour, opposite)
and frequency: s_re (amplitude, Np) and s_im (phase, rad), smoothed over +-25 MHz.
"""
from __future__ import annotations

import numpy as np

from .data import DESIGNS, H6, H7, PATH_TYPE, load_file, log_ratio

PAIRS = {"Mild_lobe": ("new_with_slices_Mild_lobe.s6p", "new_with_slices_Mild_lobe_new.s6p"),
         "Moderate_lobe": ("new_with_slices_Moderate_lobe.s6p", "new_with_slices_Moderate_lobe_c3.s6p"),
         "Severe_lobe": ("new_with_slices_Severe_lobe.s6p", "new_with_slices_Severe_lobe_c3.s6p")}


def _L(fn):
    d = next(x for x in DESIGNS if x.file == fn)
    return log_ratio(load_file(fn)[1], load_file(d.ref)[1])


def noise_samples(exclude=()):
    """List of (21, F) complex samples of one observation's numerical error."""
    out = []
    for g, (a, b) in PAIRS.items():
        if g in exclude:
            continue
        out.append((_L(a) - _L(b)) / np.sqrt(2))
    if "Healthy" not in exclude:
        out.append(log_ratio(load_file(H7)[1], load_file(H6)[1]))
    return out


def smooth(v, half=5):
    k = np.ones(2 * half + 1) / (2 * half + 1)
    vp = np.pad(v, ((0, 0), (half, half)), mode="edge")
    return np.stack([np.convolve(r, k, mode="valid") for r in vp])


def noise_sd(exclude=(), extra=None):
    """-> s_re, s_im (21, F): per-path-type sd broadcast to the 21 paths. extra: list of further
    (21, F) residual samples (e.g. surrogate model error) added in quadrature (as variances)."""
    smp = noise_samples(exclude)
    F = smp[0].shape[1]
    vr = np.zeros((4, F))
    vi = np.zeros((4, F))
    for t in range(4):
        sel = PATH_TYPE == t
        vr[t] = np.mean([np.mean(s[sel].real ** 2, 0) for s in smp], 0)
        vi[t] = np.mean([np.mean(s[sel].imag ** 2, 0) for s in smp], 0)
    vr, vi = smooth(vr), smooth(vi)
    s_re, s_im = vr[PATH_TYPE], vi[PATH_TYPE]
    if extra:
        er = np.zeros((4, F))
        ei = np.zeros((4, F))
        for t in range(4):
            sel = PATH_TYPE == t
            er[t] = np.mean([np.mean(s[sel].real ** 2, 0) for s in extra], 0)
            ei[t] = np.mean([np.mean(s[sel].imag ** 2, 0) for s in extra], 0)
        s_re = s_re + smooth(er)[PATH_TYPE]
        s_im = s_im + smooth(ei)[PATH_TYPE]
    floor_re, floor_im = (0.01 / 8.686) ** 2, np.radians(0.1) ** 2
    return np.sqrt(np.maximum(s_re, floor_re)), np.sqrt(np.maximum(s_im, floor_im))


def corr_length(samples, s_re, s_im):
    """Frequency correlation length (samples) of the whitened noise: lag where the mean
    autocorrelation first drops below 1/e."""
    acs = []
    for s in samples:
        for z in ((s.real / s_re), (s.imag / s_im)):
            z = z - z.mean(1, keepdims=True)
            F = z.shape[1]
            ac = np.array([np.mean(np.sum(z[:, :F - l] * z[:, l:], 1) / np.maximum(np.sum(z * z, 1), 1e-30))
                           for l in range(30)])
            acs.append(ac)
    ac = np.mean(acs, 0)
    below = np.flatnonzero(ac < np.exp(-1))
    return int(below[0]) if below.size else 30, ac
