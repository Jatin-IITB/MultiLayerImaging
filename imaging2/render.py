"""Slice rendering: baseline, true and estimated heads, posterior-mean change maps, sensitivity fade.

Estimated head = healthy baseline with, in each sector, the posterior mixture over (stage, x_k):
gray/white moved inward by e_k, the gap filled with CSF of the stage, diseased gray/white material
where affected, CSF material of the stage everywhere. The posterior MEAN of eps_r / sigma is shown,
so an uncertain boundary appears blurred (honest), and the posterior SD map is available.
The hippocampus (r_hip) is not estimated: the array has no sensitivity there; the estimate keeps
the baseline core and the core is hatched in every figure.
"""
from __future__ import annotations

import numpy as np

from .data import HEALTHY_LOBE, N, lobe
from .invert import E_GRID, N_CAND, STAGES
from .phantom import profile, render, sector_of

Z_SLICES = [80.0, 70.0, 60.0, 50.0, 40.0, 20.0, 0.0]
HALF = 95.0
STEP = 0.5
R_CORE_HATCH = 30.0


def slice_grid(z, step=STEP, half=HALF):
    ax = np.arange(-half, half + 1e-9, step)
    X, Y = np.meshgrid(ax, ax, indexing="xy")
    return X, Y, np.full_like(X, z)


def coronal_grid(y=0.0, step=STEP, half=HALF):
    ax = np.arange(-half, half + 1e-9, step)
    X, Z = np.meshgrid(ax, ax, indexing="xy")
    return X, np.full_like(X, y), Z


def sagittal_grid(x=0.0, step=STEP, half=HALF):
    ax = np.arange(-half, half + 1e-9, step)
    Y, Z = np.meshgrid(ax, ax, indexing="xy")
    return np.full_like(Y, x), Y, Z


def cand_truth(stage, c):
    e = np.zeros(N)
    if c > 0:
        e[0] = E_GRID[c - 1]
    t = lobe(e, stage, 25.0, affected=np.r_[c > 0, np.zeros(N - 1, bool)])
    t.tissue_stage, t.csf_stage, t.hip_stage = stage, stage, "Healthy"
    return t


def posterior_maps(marg, X, Y, Z, pmin=1e-4):
    """marg (4, 6, N_CAND) joint P(stage, x_k). -> mean and SD of eps_r and sigma on the points.
    The core keeps the baseline (hip not estimated)."""
    X, Y, Z = np.broadcast_arrays(X, Y, Z)
    r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
    sec = sector_of(np.degrees(np.arctan2(Y, X)))
    e0, s0 = render(HEALTHY_LOBE, X, Y, Z)
    m_e, m_s = np.zeros(r.shape), np.zeros(r.shape)
    q_e, q_s = np.zeros(r.shape), np.zeros(r.shape)
    healthy_p = marg[0, 0, 0] if marg.ndim == 3 else 0.0
    for k in range(N):
        sel = sec == k
        rr = r[sel]
        acc_e = np.zeros(rr.shape)
        acc_s = np.zeros(rr.shape)
        acc_e2 = np.zeros(rr.shape)
        acc_s2 = np.zeros(rr.shape)
        tot = 0.0
        for i, st in enumerate(STAGES):
            for c in range(N_CAND):
                p = marg[i, k, c]
                if p < pmin:
                    continue
                if st == "Healthy":
                    er, sg = profile(HEALTHY_LOBE, k, rr)
                else:
                    er, sg = profile(cand_truth(st, c), 0, rr)
                acc_e += p * er
                acc_s += p * sg
                acc_e2 += p * er ** 2
                acc_s2 += p * sg ** 2
                tot += p
        acc_e, acc_s, acc_e2, acc_s2 = acc_e / tot, acc_s / tot, acc_e2 / tot, acc_s2 / tot
        m_e[sel], m_s[sel] = acc_e, acc_s
        q_e[sel] = np.sqrt(np.maximum(acc_e2 - acc_e ** 2, 0))
        q_s[sel] = np.sqrt(np.maximum(acc_s2 - acc_s ** 2, 0))
    core = r < 25.0
    m_e[core], m_s[core] = e0[core], s0[core]
    q_e[core], q_s[core] = 0.0, 0.0
    return dict(eps=m_e, sig=m_s, eps_sd=q_e, sig_sd=q_s, eps0=e0, sig0=s0)


def truth_maps(t, X, Y, Z):
    e1, s1 = render(t, X, Y, Z)
    e0, s0 = render(HEALTHY_LOBE, X, Y, Z)
    return dict(eps=e1, sig=s1, eps0=e0, sig0=s0)


# ----------------------------------------------------------------------------------------------
# Sensitivity (from the HFSS fields of the healthy head)
# ----------------------------------------------------------------------------------------------
_SNR = None


def snr_volume(noise_rel):
    """-> (axes, SNR on the full 61^3 grid; 0 outside r 89). noise_rel (21, 3)."""
    global _SNR
    if _SNR is not None:
        return _SNR
    from .sensitivity import born_kernels, load_fields, voxel_snr
    pts, E = load_fields()
    K = born_kernels(E)
    snr = voxel_snr(K, noise_rel)
    ax = np.arange(-90.0, 90.0 + 1e-9, 3.0)
    vol = np.zeros((61, 61, 61))
    idx = np.rint((pts + 90.0) / 3.0).astype(int)
    vol[idx[:, 0], idx[:, 1], idx[:, 2]] = snr
    _SNR = (ax, vol)
    return _SNR


def snr_at(X, Y, Z, noise_rel):
    from scipy.interpolate import RegularGridInterpolator
    ax, vol = snr_volume(noise_rel)
    f = RegularGridInterpolator((ax, ax, ax), np.log10(np.maximum(vol, 1e-6)), bounds_error=False, fill_value=-6)
    P = np.stack(np.broadcast_arrays(X, Y, Z), -1).reshape(-1, 3)
    return 10 ** f(P).reshape(np.shape(X))


# The field exports exist at 3 frequencies; the data use 201 with a measured noise correlation
# length of ~15 samples (lodo folds: ell = 15-16), i.e. ~13 independent frequencies. The 3-frequency
# SNR is scaled by sqrt(13 / 3) to the whole band (same sensitivity assumed between field freqs).
BAND_FACTOR = float(np.sqrt((201 / 15) / 3))


def noise_rel_at_field_freqs():
    """(21, 3) per-path noise sd (Np, mean of amplitude/phase parts) at 3.4/3.6/3.8 GHz, mesh ruler."""
    from .data import freq
    from .noise import noise_sd
    from .sensitivity import FREQS
    s_re, s_im = noise_sd()
    f = freq()
    idx = [int(np.argmin(abs(f - x))) for x in FREQS]
    return np.sqrt((s_re[:, idx] ** 2 + s_im[:, idx] ** 2) / 2)


def fade_alpha(snr, lo=0.5, hi=4.0):
    """Opacity of the estimate: 1 where a 1 cm^3 change of |d eps*| = 20 gives band SNR >= hi,
    0 where <= lo (log-linear between)."""
    a = (np.log10(np.maximum(snr, 1e-9)) - np.log10(lo)) / (np.log10(hi) - np.log10(lo))
    return np.clip(a, 0, 1)
