"""Load all simulations, attach class labels, resample onto one common frequency grid."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

from .touchstone import Touchstone, plausibility, read_touchstone

STAGES = ["Normal", "MCI", "Mild", "Moderate", "Severe"]     # ordinal order
_ALIASES = {"healthy": "Normal", "normal": "Normal", "mci": "MCI", "mild": "Mild",
            "moderate": "Moderate", "severe": "Severe"}


def class_from_filename(name: str) -> str:
    stem = Path(name).stem.lower()
    for tok in reversed(re.split(r"[_\-\s.]+", stem)):
        tok = re.sub(r"ad$", "", tok)          # MildAD -> mild
        if tok in _ALIASES:
            return _ALIASES[tok]
    raise ValueError(f"No stage label found in file name {name!r}; add it to sims.csv")


def load_manifest(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    need = {"file", "class", "head_scale", "standoff_mm", "notes"}
    if missing := need - set(df.columns):
        raise ValueError(f"{path}: manifest missing columns {missing}")
    if bad := set(df["class"]) - set(STAGES):
        raise ValueError(f"{path}: unknown classes {bad}")
    return df


def common_grid(freqs: list[np.ndarray], step_hz: float,
                f_min_hz: float | None = None, f_max_hz: float | None = None) -> np.ndarray:
    lo = max(f.min() for f in freqs)
    hi = min(f.max() for f in freqs)
    lo = lo if f_min_hz is None else max(lo, f_min_hz)
    hi = hi if f_max_hz is None else min(hi, f_max_hz)
    if hi <= lo:
        raise ValueError("Files have no overlapping band")
    n = int(np.floor((hi - lo) / step_hz + 1e-9)) + 1
    return np.round(lo + step_hz * np.arange(n))       # integer Hz, no float drift


def resample(f_src: np.ndarray, s: np.ndarray, f_dst: np.ndarray) -> np.ndarray:
    """Cubic spline on Re and Im along frequency. Exact at shared grid points."""
    if f_dst.min() < f_src.min() - 1 or f_dst.max() > f_src.max() + 1:
        raise ValueError("Target grid extends outside source band (no extrapolation)")
    if f_src.size == f_dst.size and np.allclose(f_src, f_dst, atol=1.0):
        return s.copy()
    re_ = CubicSpline(f_src, s.real, axis=0)(f_dst)
    im_ = CubicSpline(f_src, s.imag, axis=0)(f_dst)
    return re_ + 1j * im_


@dataclass
class Dataset:
    f_hz: np.ndarray                  # (F,) common grid
    S: np.ndarray                     # (n_sims, F, N, N)
    classes: list[str]
    files: list[str]
    port_to_ant: np.ndarray           # port_to_ant[p] = antenna (1-based) on port p+1; config
    manifest: pd.DataFrame
    raw: list[Touchstone] = field(repr=False, default_factory=list)

    @property
    def y(self) -> np.ndarray:
        return np.array([STAGES.index(c) for c in self.classes])

    def subset(self, classes: list[str]) -> "Dataset":
        keep = [i for i, c in enumerate(self.classes) if c in classes]
        return Dataset(self.f_hz, self.S[keep], [self.classes[i] for i in keep],
                       [self.files[i] for i in keep], self.port_to_ant,
                       self.manifest.iloc[keep].reset_index(drop=True),
                       [self.raw[i] for i in keep])


def load_dataset(cfg: dict, root: str | Path = ".", classes: list[str] | None = None) -> Dataset:
    root = Path(root)
    dcfg, gcfg = cfg["data"], cfg["grid"]
    raw_dir = root / dcfg["raw_dir"]
    man_path = root / dcfg["manifest"]
    if man_path.exists():
        man = load_manifest(man_path)
    else:
        files = sorted(p.name for p in raw_dir.glob("*.s*p"))
        man = pd.DataFrame({"file": files, "class": [class_from_filename(f) for f in files],
                            "head_scale": 1.0, "standoff_mm": np.nan, "notes": ""})
    if classes is not None:
        man = man[man["class"].isin(classes)].reset_index(drop=True)
    man = man.assign(_o=man["class"].map(STAGES.index)).sort_values(["_o", "file"])
    man = man.drop(columns="_o").reset_index(drop=True)

    ts = [read_touchstone(raw_dir / f) for f in man["file"]]
    n = {t.n_ports for t in ts}
    if len(n) != 1:
        raise ValueError(f"Inconsistent port count across files: {n}")
    if len({t.z0 for t in ts}) != 1:
        raise ValueError("Files use different reference impedances")
    band = tuple(float(v) for v in cfg["qc"]["expected_band_hz"])
    for t in ts:
        if probs := plausibility(t, band):
            raise ValueError(f"{Path(t.path).name}: implausible decode: {probs}")

    opt = lambda v: None if v is None else float(v)
    f = common_grid([t.f_hz for t in ts], float(gcfg["step_hz"]), opt(gcfg.get("f_min_hz")),
                    opt(gcfg.get("f_max_hz")))
    S = np.stack([resample(t.f_hz, t.s, f) for t in ts])
    p2a = np.asarray(cfg["ring"]["port_to_ant"])
    if sorted(p2a) != list(range(1, n.pop() + 1)):
        raise ValueError(f"config ring.port_to_ant {p2a} is not a permutation of the ports")
    return Dataset(f, S, list(man["class"]), list(man["file"]), p2a, man, ts)
