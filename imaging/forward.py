"""Forward model (a): layered sphere + 6 tangential point dipoles -> ring couplings V_k(f).

V_k(f) = p_{t+k} . E_t(r_{t+k})  (reaction between dipoles; unit omega^2 mu0 ik = 1), HFSS
e^{+jωt} convention. By the C6 symmetry of the ideal ring V depends only on the ring distance k.
Calibration to HFSS: S_k(f) ~ c_k(f) V_k(f) with a per-ring-distance complex factor c_k(f)
fitted on the Normal simulation (k = 1..3). For k = 0 the antenna's own mismatch dominates S_ii
and is not modelled; only differences dS_ii are modelled, with c_0 = c_1 (flagged), or a
frequency-independent complex c_0 / c_1 ratio fitted on Mild when ``fit_k0`` is used.
"""
from __future__ import annotations

import numpy as np

from .common import HeadParams, antenna_positions_mm, dipole_dirs
from .mie import (LayeredSolution, Sphere, eps_complex, free_space_field, internal_field,
                  receiver_field_scattered, rotation_to_pole, to_hfss)

NMAX = 90


def sphere_of(p: HeadParams, f_hz: np.ndarray, extra_layers=None) -> Sphere:
    """Layered sphere of the head. extra_layers: optional list of (r_in_mm, r_out_mm,
    d_eps_complex (F,)) perturbation shells added on top of the background."""
    lay = p.layers()
    radii = [lay[0][0]]
    eps = [eps_complex(lay[0][1], lay[0][2], f_hz)]
    for (ro, e, s) in lay[1:]:
        radii.append(ro)
        eps.append(eps_complex(e, s, f_hz))
    radii, eps = np.array(radii), list(eps)
    if extra_layers:
        for (ri, ro, de) in extra_layers:
            radii, eps = _insert_shell(radii, eps, ri, ro, de)
    return Sphere(radii * 1e-3, np.array(eps), np.asarray(f_hz, float))


def _insert_shell(radii, eps, ri, ro, de):
    """Split layers so that [ri, ro] is its own layer with eps + de."""
    for cut in (ri, ro):
        if cut <= 0 or np.any(np.isclose(radii, cut)):
            continue
        j = int(np.searchsorted(radii, cut))
        radii = np.insert(radii, j, cut)
        eps.insert(j, eps[j].copy())
    inner = np.concatenate([[0.0], radii[:-1]])
    for j in range(len(radii)):
        if inner[j] >= ri - 1e-9 and radii[j] <= ro + 1e-9:
            eps[j] = eps[j] + de
    return radii, eps


class RingModel:
    """Precomputes geometry for one polarisation; evaluates V_k(f) for any head."""

    def __init__(self, pol: str = "theta", nmax: int = NMAX):
        self.pol, self.nmax = pol, nmax
        pos = antenna_positions_mm() * 1e-3
        d = dipole_dirs(pol, antenna_positions_mm())
        self.Rm = rotation_to_pole(pos[0], d[0])
        self.pos_rot = pos[:4] @ self.Rm.T                       # antennas 1..4 = k 0..3
        self.dir_rot = d[:4] @ self.Rm.T
        self.r_src = float(np.linalg.norm(pos[0]))
        self.pos, self.dirs = pos, d

    def solve(self, sph: Sphere) -> LayeredSolution:
        return LayeredSolution(sph, self.nmax)

    def scattered(self, sol: LayeredSolution) -> np.ndarray:
        E = receiver_field_scattered(sol, self.r_src, self.pos_rot, self.nmax)   # (F, 4, 3)
        return to_hfss(np.einsum("fkc,kc->fk", E, self.dir_rot))

    def direct(self, f_hz) -> np.ndarray:
        k0 = 2 * np.pi * np.asarray(f_hz) / 299_792_458.0
        E = free_space_field(k0, self.pos_rot[0], np.array([1.0, 0, 0]), self.pos_rot[1:])
        v = np.einsum("fkc,kc->fk", E, self.dir_rot[1:])
        return to_hfss(np.concatenate([np.zeros((len(k0), 1)), v], 1))

    def V(self, p: HeadParams, f_hz, extra_layers=None, total=False) -> np.ndarray:
        """(F, 4) scattered reaction (total = + free-space direct coupling for k >= 1)."""
        v = self.scattered(self.solve(sphere_of(p, f_hz, extra_layers)))
        return v + self.direct(f_hz) if total else v

    def fields(self, p: HeadParams, f_hz, pts_mm: np.ndarray, ant: int) -> np.ndarray:
        """Total E inside the head for antenna `ant` (0-based T#-1) at global points (P,3) mm.

        Returns (F, P, 3), HFSS convention, same unit as V."""
        pos = self.pos[ant]
        R = rotation_to_pole(pos, self.dirs[ant])
        sol = self.solve(sphere_of(p, f_hz))
        E = internal_field(sol, float(np.linalg.norm(pos)), (pts_mm * 1e-3) @ R.T, self.nmax)
        return to_hfss(E @ R)                                     # back to the global frame


def calibrate(S_ring_normal: np.ndarray, V_total_normal: np.ndarray) -> np.ndarray:
    """c_k(f) = S_k / V_k for k = 1..3; c_0 := c_1 (antenna self-term not modelled)."""
    c = S_ring_normal / V_total_normal
    c[:, 0] = c[:, 1]
    return c


def ring_to_matrix(v_ring: np.ndarray, kmat: np.ndarray) -> np.ndarray:
    """(..., F, 4) ring values -> (..., F, N, N) port matrix via the ring-distance map."""
    return v_ring[..., kmat]


# ----------------------------------------------------------------------------------------------
# Kernel-based ring model: any antenna = set of tangential dipole elements on r = r_s.
# kind="point": one dipole at the feed (the brief's model).
# kind="patch": L x W aperture of elements, cos(pi u / L) weighting along the current
#               (a crude extended-aperture variant, used only as a sensitivity check).
# ----------------------------------------------------------------------------------------------
from .mie import coupling_kernels, internal_field_general, projections, scattered_reaction  # noqa: E402
from .common import N_ANT, R_FEED_MM  # noqa: E402


def antenna_elements(kind="point", pol="theta", r_s_mm=R_FEED_MM, L_mm=42.0, W_mm=35.0,
                     n_el=5):
    """List over antennas T1..T6 of (pos (E,3) m, dirs (E,3), w (E,))."""
    pos0 = antenna_positions_mm()
    pos0 = pos0 / np.linalg.norm(pos0, axis=1)[:, None]
    d0 = dipole_dirs(pol, pos0)
    out = []
    for t in range(N_ANT):
        u = pos0[t]
        p = d0[t]
        q = np.cross(u, p)
        if kind == "point":
            offs = [(0.0, 0.0, 1.0)]
        else:
            g = (np.arange(n_el) + 0.5) / n_el - 0.5
            offs = [(a * L_mm, b * W_mm, np.cos(np.pi * a)) for a in g for b in g]
        P, D, Wt = [], [], []
        for (a, b, w) in offs:
            v = u + (a * p + b * q) / r_s_mm                  # small-angle map onto the sphere
            v /= np.linalg.norm(v)
            dd = p - v * (p @ v)
            dd /= np.linalg.norm(dd)
            P.append(v * r_s_mm * 1e-3)
            D.append(dd)
            Wt.append(w)
        Wt = np.array(Wt) / np.sum(Wt)
        out.append((np.array(P), np.array(D), Wt))
    return out


class KernelRingModel:
    """V[f, a, b] (antenna order T1..T6) for any HeadParams; kernels precomputed once."""

    def __init__(self, kind="point", pol="theta", r_s_mm=R_FEED_MM, nmax=NMAX, **kw):
        self.kind, self.pol, self.nmax = kind, pol, nmax
        self.r_s = r_s_mm * 1e-3
        self.el = antenna_elements(kind, pol, r_s_mm, **kw)
        self.P = [projections(nmax, *e) for e in self.el]
        KTE = np.zeros((N_ANT, N_ANT, nmax), complex)
        KTM = np.zeros_like(KTE)
        for a in range(N_ANT):
            for b in range(N_ANT):
                KTE[a, b], KTM[a, b] = coupling_kernels(self.P[a], self.P[b])
        self.KTE, self.KTM = KTE, KTM

    def scattered(self, p: HeadParams, f_hz, extra_layers=None) -> np.ndarray:
        sol = LayeredSolution(sphere_of(p, f_hz, extra_layers), self.nmax)
        V = scattered_reaction(sol, self.r_s, self.KTE, self.KTM)          # (6, 6, F)
        return to_hfss(np.moveaxis(V, -1, 0))

    def direct(self, f_hz) -> np.ndarray:
        k0 = 2 * np.pi * np.asarray(f_hz) / 299_792_458.0
        V = np.zeros((k0.size, N_ANT, N_ANT), complex)
        for a in range(N_ANT):
            for b in range(N_ANT):
                if a == b:
                    continue
                Pa, Da, Wa = self.el[a]
                Pb, Db, Wb = self.el[b]
                for e in range(len(Wa)):
                    E = free_space_field(k0, Pa[e], Da[e], Pb)                # (F, Eb, 3)
                    V[:, a, b] += Wa[e] * np.einsum("fec,ec,e->f", E, Db, Wb)
        return to_hfss(V)

    def fields(self, p: HeadParams, f_hz, pts_mm: np.ndarray, ant: int) -> np.ndarray:
        sol = LayeredSolution(sphere_of(p, f_hz), self.nmax)
        if self.kind == "point":           # rotate the dipole to the pole: only |m| <= 1 needed
            pos, d, w = self.el[ant]
            R = rotation_to_pole(pos[0], d[0])
            E = internal_field(sol, self.r_s, (pts_mm * 1e-3) @ R.T, self.nmax) @ R * w[0]
        else:
            E = internal_field_general(sol, self.r_s, self.P[ant], pts_mm * 1e-3)
        return to_hfss(E)


def ring_from_ant(V: np.ndarray) -> np.ndarray:
    """(..., F, 6, 6) antenna-order matrix -> (..., F, 4) ring modes (mean over t)."""
    return np.stack([np.mean([V[..., t, (t + k) % N_ANT] for t in range(N_ANT)], 0)
                     for k in range(4)], -1)


def ant_to_port(V: np.ndarray, port_to_ant) -> np.ndarray:
    """Antenna-order (.., 6, 6) -> Touchstone port order."""
    a = np.asarray(port_to_ant) - 1
    return V[..., a[:, None], a[None, :]]
