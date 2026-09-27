"""Ring-geometry helpers. Port-to-antenna mapping comes from config, never from file headers."""
from __future__ import annotations

import numpy as np


def ring_distance(port_to_ant: np.ndarray) -> np.ndarray:
    """(N, N) matrix of ring distances k = 0..N//2 between ports."""
    a = np.asarray(port_to_ant) - 1
    n = a.size
    d = np.abs(a[:, None] - a[None, :]) % n
    return np.minimum(d, n - d)


def pairs_at_distance(port_to_ant: np.ndarray, k: int) -> list[tuple[int, int]]:
    """Ordered (i, j) port pairs (0-based) with ring distance k."""
    d = ring_distance(port_to_ant)
    return [(i, j) for i in range(d.shape[0]) for j in range(d.shape[1]) if d[i, j] == k]


def ring_average(S: np.ndarray, port_to_ant: np.ndarray) -> np.ndarray:
    """Average S(t, t+k) over t for each k -> (..., F, N//2 + 1). The circulant 'mode'."""
    n = S.shape[-1]
    out = [np.mean(np.stack([S[..., i, j] for i, j in pairs_at_distance(port_to_ant, k)], -1), -1)
           for k in range(n // 2 + 1)]
    return np.stack(out, -1)
