"""Phantom geometry and materials: render eps_r / sigma of any design state on a grid.

Lobe phantom (HFSS audit of Healthy_sliced): skin 87.5-88, fat 86.5-87.5, skull 83.5-86.5;
one CSF sphere r 83.5 fills every gap; in sector k gray 76-e_k .. 83-e_k, white 25 .. 76-e_k;
hippocampus sphere r_hip (the shell r_hip..25 is CSF). Uniform phantoms: gray r_white..r_gray,
white r_hip..r_white, CSF r_gray..83.5.

Materials: Shehab et al. 2025 Table 5 (VERIFIED in the HFSS material editor, MODEL_CARD 5.2).
Skin/fat/skull values are NOT recorded anywhere in the repo (MODEL_CARD Part 2, OPEN-GUI); the
values below are the literature assumptions used by the earlier imaging session. They are the
same in every design, so no change map depends on them; only the baseline image does.
"""
from __future__ import annotations

import numpy as np

from .data import N, Truth

EPS0 = 8.854187817e-12
R_SKIN, R_FAT, R_SKULL, R_CSF = 88.0, 87.5, 86.5, 83.5
R_GM0, R_WM0, R_HIP0 = 83.0, 76.0, 25.0

MAT = {  # (eps_r, sigma S/m): gray, white, hippocampus, CSF
    "Healthy": {"gm": (47.7, 2.42), "wm": (35.3, 1.65), "hip": (47.7, 2.42), "csf": (65.0, 4.27)},
    "Mild": {"gm": (40.3, 5.203), "wm": (31.77, 2.39), "hip": (39.11, 5.687), "csf": (55.25, 4.91)},
    "Moderate": {"gm": (39.11, 5.687), "wm": (31.064, 2.722), "hip": (38.39, 5.92), "csf": (48.75, 5.337)},
    "Severe": {"gm": (38.39, 5.92), "wm": (30.35, 2.88), "hip": (37.2, 6.413), "csf": (32.5, 6.405)},
    "MCI": {"hip": (40.3, 5.203)},
}
FIXED = {"skull": (10.8, 0.61), "fat": (10.5, 0.42), "skin": (37.0, 2.0)}   # ASSUMED (see above)
STAGES = ["Healthy", "Mild", "Moderate", "Severe"]


def sector_of(az_deg):
    """Sector index 0..5 (S1..S6) of azimuth (deg): S1 = [-120, -60), centred on T1 at -90."""
    return (np.floor(((np.asarray(az_deg) + 120.0) % 360.0) / 60.0)).astype(int) % N


def radii(t: Truth, k: int):
    """(r_gm_out, r_gm_in (= r_wm_out), r_wm_in, r_hip) of sector k."""
    if t.kind == "uniform":
        return t.r_gray, t.r_white, t.r_hip, t.r_hip
    e = float(t.e[k])
    return R_GM0 - e, R_WM0 - e, R_HIP0, t.r_hip


def sector_materials(t: Truth, k: int):
    tis = t.tissue_stage if t.affected[k] else "Healthy"
    return (MAT[tis]["gm"], MAT[tis]["wm"], MAT[t.csf_stage]["csf"],
            MAT[t.hip_stage]["hip"] if t.hip_stage in MAT and "hip" in MAT[t.hip_stage] else MAT["Healthy"]["hip"])


def profile(t: Truth, k: int, r):
    """eps_r(r), sigma(r) along radius r (mm) inside sector k (outside the skin: air)."""
    r = np.asarray(r, float)
    er = np.ones_like(r)
    sg = np.zeros_like(r)
    rgo, rgi, rwi, rh = radii(t, k)
    gm, wm, csf, hip = sector_materials(t, k)
    # paint outside-in; later assignments override
    for lo, hi, m in [(R_FAT, R_SKIN, FIXED["skin"]), (R_SKULL, R_FAT, FIXED["fat"]),
                      (R_CSF, R_SKULL, FIXED["skull"]), (0.0, R_CSF, csf),
                      (rwi, rgi, wm), (rgi, rgo, gm), (0.0, rh, hip)]:
        sel = (r >= lo) & (r < hi)
        er[sel], sg[sel] = m
    return er, sg


def render(t: Truth, X, Y, Z):
    """eps_r, sigma on arbitrary point arrays (mm)."""
    X, Y, Z = np.broadcast_arrays(np.asarray(X, float), np.asarray(Y, float), np.asarray(Z, float))
    r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
    sec = sector_of(np.degrees(np.arctan2(Y, X)))
    er = np.ones(r.shape)
    sg = np.zeros(r.shape)
    for k in range(N):
        sel = sec == k
        er[sel], sg[sel] = profile(t, k, r[sel])
    return er, sg


def tissue_label(t: Truth, X, Y, Z):
    """Integer tissue map: 0 air, 1 skin, 2 fat, 3 skull, 4 CSF, 5 gray, 6 white, 7 hippocampus."""
    X, Y, Z = np.broadcast_arrays(np.asarray(X, float), np.asarray(Y, float), np.asarray(Z, float))
    r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
    sec = sector_of(np.degrees(np.arctan2(Y, X)))
    lab = np.zeros(r.shape, int)
    for k in range(N):
        sel = sec == k
        rr = r[sel]
        rgo, rgi, rwi, rh = radii(t, k)
        lk = np.zeros(rr.shape, int)
        for lo, hi, v in [(R_FAT, R_SKIN, 1), (R_SKULL, R_FAT, 2), (R_CSF, R_SKULL, 3), (0.0, R_CSF, 4),
                          (rwi, rgi, 6), (rgi, rgo, 5), (0.0, rh, 7)]:
            lk[(rr >= lo) & (rr < hi)] = v
        lab[sel] = lk
    return lab


def depth_profile(t: Truth, k: int, d):
    """(d eps_r, d sigma) of sector k against the healthy lobe head at depth d = 83.5 - r (mm)."""
    from .data import HEALTHY_LOBE
    r = R_CSF - np.asarray(d, float)
    e1, s1 = profile(t, k, r)
    e0, s0 = profile(HEALTHY_LOBE, k, r)
    return e1 - e0, s1 - s0
