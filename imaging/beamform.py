"""I1 - multistatic radar beamforming of dS(f) = S_stage - S_Normal: DAS, DMAS, MVDR.

Signals: the 21 reciprocal pairs (6 monostatic S_ii + 15 bistatic (S_ij + S_ji)/2).
Whitening: each pair is divided by its measurement-noise std (noise model, 'typical'), so
pairs enter in proportion to their SNR instead of their raw level (S_ii is 40-60 dB above the
transmission pairs and would otherwise be the whole image).

Pair delay: tau_p(r) = tau_i(r) + tau_j(r) + 2 t_ant, one-way delays from the delay model
(single effective eps, or straight rays through the Normal layers), t_ant = antenna/feed delay.

DAS : E(r) = sum_{t' in window} |sum_p h_p(tau_p(r) + t')|^2  (analytic signals; window =
      1/4 of the -6 dB pulse width around the focal delay, 5 samples)
DMAS: s_p = Re h_p; g_p = sign(s_p) sqrt|s_p|;  y = sum_{p<q} g_p g_q = ((sum g)^2 - sum g^2)/2,
      E(r) = sum_{t'} y^2  (pairwise sign-preserving sqrt of products, O(P) per sample)
MVDR: frequency-domain Capon. Focused spectra x~_p(f) = W(f) x_p(f) e^{+j2 pi f tau_p(r)}.
      With one measurement per pair there is only ONE snapshot of the 21-channel vector; its
      outer product is rank 1 and not invertible. We use the F frequency bins of the focused
      spectra as snapshots: R = X~ X~^H / F (rank <= min(21, F)), diagonal loading
      delta = gamma tr(R)/21, w = R^-1 1 / (1^H R^-1 1), E(r) = |sum_f w^H x~(f)|^2.
      This assumes the focused response is frequency-flat, which holds only approximately
      (band-limited, lossy media), so R mixes frequency structure with spatial structure.
"""
from __future__ import annotations

import numpy as np

from .timedomain import TimeResponse, delay_layered, pair_list


def pair_signals(dS: np.ndarray, sigma: np.ndarray | None = None) -> np.ndarray:
    """(F, N, N) -> (21, F) reciprocal-pair spectra, optionally divided by sigma (21,)."""
    pl = pair_list(dS.shape[-1])
    x = np.stack([dS[:, i, j] if i == j else 0.5 * (dS[:, i, j] + dS[:, j, i]) for i, j in pl])
    return x if sigma is None else x / sigma[:, None]


def pair_noise_sigma(S_ref: np.ndarray, prof) -> np.ndarray:
    """Band-rms noise std of each reciprocal-pair difference signal under a noise profile.

    Per measured entry: var = |S|^2 (s_g^2 + s_phi^2) + floor^2 (s_g = sigma_dB ln10/20);
    a difference of two independent measurements doubles it; averaging S_ij, S_ji halves it."""
    sg = prof.sigma_db * np.log(10) / 20
    sp = np.deg2rad(prof.sigma_deg)
    fl2 = 10 ** (prof.floor_db / 10)
    var = 2 * (np.abs(S_ref) ** 2 * (sg ** 2 + sp ** 2) + fl2)          # (F, N, N)
    out = []
    for i, j in pair_list(S_ref.shape[-1]):
        v = var[:, i, j] if i == j else 0.25 * (var[:, i, j] + var[:, j, i])
        out.append(np.sqrt(np.mean(v)))
    return np.array(out)


class Imager:
    def __init__(self, f_hz, port_pos_mm, pts_mm, layers, t_ant_s=0.0, win="hann",
                 win_ns=None, n_tw=5, gamma=0.1):
        self.f = np.asarray(f_hz, float)
        self.pts = np.asarray(pts_mm, float)
        self.pl = pair_list(len(port_pos_mm))
        tau1 = np.stack([delay_layered(a, self.pts, layers) for a in port_pos_mm])   # (N, P)
        self.tau = np.stack([tau1[i] + tau1[j] for i, j in self.pl]) + 2 * t_ant_s   # (21, P)
        self.win, self.n_tw, self.gamma = win, n_tw, gamma
        self.win_ns = win_ns

    def _tr(self, x):
        tr = TimeResponse(self.f, x, self.win)
        if self.win_ns is None:                      # short window: 1/4 of the -6 dB pulse width
            self.win_ns = 0.25 * tr.pulse_width() * 1e9
            self.pulse_ns = tr.pulse_width() * 1e9
        return tr

    def _samples(self, x):
        tr = self._tr(x)
        tw = np.linspace(-0.5, 0.5, self.n_tw) * self.win_ns * 1e-9
        tau = self.tau[:, :, None] + tw[None, None, :]                       # (21, P, K)
        h = tr(tau.reshape(len(self.pl), -1)).reshape(tau.shape)
        return h

    def das(self, x: np.ndarray) -> np.ndarray:
        h = self._samples(x)
        return np.sum(np.abs(h.sum(0)) ** 2, -1)

    def dmas(self, x: np.ndarray) -> np.ndarray:
        s = self._samples(x).real
        g = np.sign(s) * np.sqrt(np.abs(s))
        y = 0.5 * (g.sum(0) ** 2 - (g ** 2).sum(0))
        return np.sum(y ** 2, -1)

    def mvdr(self, x: np.ndarray, chunk: int = 2000) -> np.ndarray:
        W = self._tr(x).w
        C = len(self.pl)
        one = np.ones(C)
        out = np.empty(self.pts.shape[0])
        for s in range(0, out.size, chunk):
            tau = self.tau[:, s:s + chunk]                                    # (C, p)
            xf = (x * W)[:, None, :] * np.exp(2j * np.pi * self.f[None, None, :] * tau[..., None])
            xf = np.moveaxis(xf, 1, 0)                                         # (p, C, F)
            R = np.einsum("pcf,pdf->pcd", xf, np.conj(xf)) / self.f.size
            load = self.gamma * np.real(np.einsum("pcc->p", R)) / C
            R = R + load[:, None, None] * np.eye(C)
            Ri1 = np.linalg.solve(R, np.broadcast_to(one, (R.shape[0], C))[..., None])[..., 0]
            w = Ri1 / np.einsum("c,pc->p", one, Ri1)[:, None]
            y = np.einsum("pc,pcf->p", np.conj(w), xf)
            out[s:s + chunk] = np.abs(y) ** 2
        return out

    def image(self, method: str, x: np.ndarray) -> np.ndarray:
        return {"DAS": self.das, "DMAS": self.dmas, "MVDR": self.mvdr}[method](x)


def fibonacci_dirs(n: int) -> np.ndarray:
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], -1)


def radial_points(r_mm: np.ndarray, n_dir: int = 200) -> np.ndarray:
    d = fibonacci_dirs(n_dir)
    return (np.asarray(r_mm)[:, None, None] * d[None]).reshape(-1, 3)


def plane_points(plane: str, z_ring_mm: float, step=3.0, lim=90.0, r_max=88.0):
    """Grid points of the ring plane (z = z_ring) or the vertical plane x = 0 (through T1 at
    azimuth -90 deg and T4 at +90 deg), inside r_max.

    Returns (pts (P, 3), mask (n, n) of kept points, axes u)."""
    u = np.arange(-lim, lim + 1e-9, step)
    A, B = np.meshgrid(u, u, indexing="xy")
    if plane == "ring":
        P = np.stack([A, B, np.full_like(A, z_ring_mm)], -1)
    elif plane == "vertical":
        P = np.stack([np.zeros_like(A), A, B], -1)          # (x=0, y=A, z=B)
    else:
        raise ValueError(plane)
    m = np.linalg.norm(P, axis=-1) < r_max
    return P[m], m, u
