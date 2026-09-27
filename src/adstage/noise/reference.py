"""Noise reference for class gaps: between-mesh spread if mesh repeats exist, else port-to-port.

A mesh repeat is a second solve of the same design with different mesh settings (sims.csv
role = mesh_repeat, repeat_of = <primary file>). For a scalar metric with simulation-level
values v, the between-mesh standard deviation is estimated from the repeat pairs as
sqrt(mean((v_repeat - v_primary)^2) / 2).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def mesh_pairs(files: list[str], manifest: pd.DataFrame) -> list[tuple[int, int]]:
    """(index of primary, index of repeat) into `files` for every mesh-repeat row present."""
    idx = {f: i for i, f in enumerate(files)}
    pairs = []
    for _, r in manifest.iterrows():
        if r.get("role", "primary") == "mesh_repeat" and r["file"] in idx and r["repeat_of"] in idx:
            pairs.append((idx[r["repeat_of"]], idx[r["file"]]))
    return pairs


def mesh_sd(values: np.ndarray, pairs: list[tuple[int, int]]) -> float:
    if not pairs:
        return np.nan
    d = np.array([values[b] - values[a] for a, b in pairs])
    return float(np.sqrt(np.mean(d ** 2) / 2))


def reference_label(pairs) -> str:
    return "mesh" if pairs else "port"
