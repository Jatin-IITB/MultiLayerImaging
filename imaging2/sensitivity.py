"""Array sensitivity from the HFSS E-field exports (v2 Normal head, unsliced; 3.4 / 3.6 / 3.8 GHz;
1 V incident on one terminal, others matched; 3 mm grid, x, y, z in [-90, 90] mm).

What the exports are (checked here, see README): full 3-D volumes, 61^3 nodes, every antenna,
three frequencies, plus a +-120 mm / 4 mm T1 export at 3.6 GHz. They cover the array region
(z 44-78 mm) and the whole head; they are NOT only the z = -9 mm cut plane. They are the fields of
the HEALTHY head only: no field exists for any diseased design, so an iterative (DBIM) update of
the background is impossible without re-solving.

Born sensitivity (e^{+jwt}, peak phasors, a = V/sqrt(Z0)):
    dS_ij(f) = -(j w eps0 Z0 / 4) * integral d eps*(r) E_i . E_j dV,  d eps* = d eps_r - j d sigma/(w eps0)
Relative (log-ratio) sensitivity of path p: K_p / S_p.
"""
from __future__ import annotations

import numpy as np

from .data import CACHE, N, PATHS, PI, PJ, load_file, paths_of
from .phantom import EPS0

FREQS = np.array([3.4e9, 3.6e9, 3.8e9])
Z0 = 50.0
STEP_MM = 3.0
R_KEEP = 89.0          # keep nodes inside the head (+1 mm)


def load_fields():
    """-> pts (P, 3) mm (r <= 89 mm), E (6, 3, P, 3) complex64. Cached."""
    fn = CACHE / "fields_head.npz"
    if fn.exists():
        z = np.load(fn)
        return z["pts"], z["E"]
    import sys
    from .data import ROOT
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from imaging.fields import load_hfss_fields          # read-only reuse of the earlier reader
    f, grids = load_hfss_fields("Normal")
    assert np.allclose(f, FREQS)
    P = grids[0][0].points().reshape(-1, 3)
    r = np.linalg.norm(P, axis=1)
    keep = r <= R_KEEP
    E = np.stack([np.stack([g.E.reshape(-1, 3)[keep] for g in row]) for row in grids]).astype(np.complex64)
    pts = P[keep].astype(np.float32)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(fn, pts=pts, E=E)
    return pts, E


def born_kernels(E):
    """(21, 3, P) complex: dS_p per unit d eps* per m^3 at each node: -(j w eps0 Z0/4) E_i.E_j."""
    c = -1j * 2 * np.pi * FREQS * EPS0 * Z0 / 4.0
    K = np.einsum("pfxc,pfxc->pfx", E[PI], E[PJ])
    return K * c[None, :, None]


def ref_paths_at_field_freqs():
    """S_p of the v2 healthy head (the design the fields belong to) at 3.4/3.6/3.8 GHz -> (21, 3)."""
    f, S, _ = load_file("new_Healthy.s6p")
    idx = [int(np.argmin(abs(f - fq))) for fq in FREQS]
    return paths_of(S)[:, idx]


def voxel_snr(K, noise_rel, deps=20.0, vol_mm3=1000.0):
    """SNR (quadrature over 21 paths x 3 freqs x re/im) of a change d eps* = deps (complex magnitude,
    worst phase) filling vol_mm3 around each node, with relative noise noise_rel (21, 3) per path.
    -> (P,)."""
    Sref = ref_paths_at_field_freqs()
    rel = K / Sref[:, :, None] * (vol_mm3 * 1e-9) * deps          # change of ln S
    z = np.abs(rel) / noise_rel[:, :, None]
    return np.sqrt((z ** 2).sum((0, 1)) / 2.0)                     # /2: worst-case split re/im


def radial_kernels(pts, K, sector=0, r_edges=None):
    """Sector-integrated Born kernel per path and frequency in radial bins:
    -> r_mid, (21, 3, nbins) complex sum K dV over nodes of the wedge of `sector` in each shell."""
    from .phantom import sector_of
    r_edges = np.arange(25.0, 87.0, 3.0) if r_edges is None else r_edges
    r = np.linalg.norm(pts, axis=1)
    sec = sector_of(np.degrees(np.arctan2(pts[:, 1], pts[:, 0])))
    out = np.zeros((K.shape[0], K.shape[1], len(r_edges) - 1), complex)
    dV = (STEP_MM * 1e-3) ** 3
    for b in range(len(r_edges) - 1):
        sel = (sec == sector) & (r >= r_edges[b]) & (r < r_edges[b + 1])
        out[:, :, b] = K[:, :, sel].sum(-1) * dV
    return 0.5 * (r_edges[1:] + r_edges[:-1]), out
