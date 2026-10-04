"""Load all simulations, attach class labels, mask glitches, put them on one frequency grid."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

from .masking import mask_glitches
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
    defaults = {"project": "", "head_id": "h0", "role": "primary", "repeat_of": ""}
    for col, v in defaults.items():
        df[col] = df[col].fillna(v).astype(str) if col in df else v
    if bad := set(df["role"]) - {"primary", "mesh_repeat"}:
        raise ValueError(f"{path}: unknown role {bad}")
    rep = df[df["role"] == "mesh_repeat"]
    if missing := set(rep["repeat_of"]) - set(df["file"]):
        raise ValueError(f"{path}: repeat_of refers to unknown files {missing}")
    return df


def native_step(f: np.ndarray) -> float:
    return float(np.median(np.diff(f)))


def common_grid(freqs: list[np.ndarray], step_hz: float | None = None,
                f_min_hz: float | None = None, f_max_hz: float | None = None) -> np.ndarray:
    """Common grid over the intersection band, never finer than the coarsest file.

    step_hz=None: use the coarsest file's native nodes inside the band (that file is not
    resampled; finer files are downsampled onto it). An explicit step finer than any file's
    native step raises, because that would be upsampling."""
    lo = max(f.min() for f in freqs)
    hi = min(f.max() for f in freqs)
    lo = lo if f_min_hz is None else max(lo, f_min_hz)
    hi = hi if f_max_hz is None else min(hi, f_max_hz)
    if hi <= lo:
        raise ValueError("Files have no overlapping band")
    steps = [native_step(f) for f in freqs]
    if step_hz is None:
        f0 = freqs[int(np.argmax(steps))]
        return np.round(f0[(f0 >= lo - 1) & (f0 <= hi + 1)])
    if step_hz < max(steps) - 1:
        raise ValueError(f"step {step_hz:g} Hz is finer than the coarsest file "
                         f"({max(steps):g} Hz): that would upsample")
    n = int(np.floor((hi - lo) / step_hz + 1e-9)) + 1
    return np.round(lo + step_hz * np.arange(n))       # integer Hz, no float drift


def resample(f_src: np.ndarray, s: np.ndarray, f_dst: np.ndarray) -> np.ndarray:
    """Downsample onto a coarser grid. Shared nodes are copied exactly; other target points
    (at most half a native step from a node) use a cubic spline on Re and Im."""
    if f_dst.min() < f_src.min() - 1 or f_dst.max() > f_src.max() + 1:
        raise ValueError("Target grid extends outside source band (no extrapolation)")
    if f_dst.size > 1 and native_step(f_dst) < native_step(f_src) - 1:
        raise ValueError("Refusing to upsample onto a finer grid")
    src, dst = np.round(f_src), np.round(f_dst)
    if np.isin(dst, src).all():
        return s[np.searchsorted(src, dst)].copy()
    re_ = CubicSpline(f_src, s.real, axis=0)(f_dst)
    im_ = CubicSpline(f_src, s.imag, axis=0)(f_dst)
    return re_ + 1j * im_


@dataclass
class Dataset:
    f_hz: np.ndarray                  # (F,) common grid
    S: np.ndarray                     # (n_sims, F, N, N), glitch-masked if enabled
    classes: list[str]                # stage labels from sims.csv
    files: list[str]
    port_to_ant: np.ndarray           # port_to_ant[p] = antenna (1-based) on port p+1; config
    manifest: pd.DataFrame
    raw: list[Touchstone] = field(repr=False, default_factory=list)
    masked_log: pd.DataFrame = field(repr=False, default_factory=pd.DataFrame)
    masking: bool = False

    @property
    def y(self) -> np.ndarray:
        return np.array([STAGES.index(c) for c in self.classes])

    def subset(self, classes: list[str]) -> "Dataset":
        keep = [i for i, c in enumerate(self.classes) if c in classes]
        files = [self.files[i] for i in keep]
        log = self.masked_log
        if len(log):
            log = log[log["file"].isin(files)].reset_index(drop=True)
        return Dataset(self.f_hz, self.S[keep], [self.classes[i] for i in keep], files,
                       self.port_to_ant, self.manifest.iloc[keep].reset_index(drop=True),
                       [self.raw[i] for i in keep], log, self.masking)


def load_dataset(cfg: dict, root: str | Path = ".", classes: list[str] | None = None,
                 mask: bool | None = None) -> Dataset:
    """mask=None -> cfg['qc']['mask_glitches']."""
    root = Path(root)
    dcfg, gcfg, qcfg = cfg["data"], cfg["grid"], cfg["qc"]
    raw_dir = root / dcfg["raw_dir"]
    man_path = root / dcfg["manifest"]
    if man_path.exists():
        man = load_manifest(man_path)
    else:
        files = sorted(p.name for p in raw_dir.glob("*.s*p"))
        man = pd.DataFrame({"file": files, "class": [class_from_filename(f) for f in files],
                            "head_scale": 1.0, "standoff_mm": np.nan, "notes": ""})
    if dcfg.get("set") is not None:                      # rows whose space-separated `set` lists it
        man = man[man["set"].astype(str).str.split().apply(lambda v: dcfg["set"] in v)].reset_index(drop=True)
        if man.empty:
            raise ValueError(f"{man_path}: no rows in set {dcfg['set']}")
    if dcfg.get("kind") is not None and "kind" in man:   # e.g. stage designs only, test designs excluded
        man = man[man["kind"].astype(str) == dcfg["kind"]].reset_index(drop=True)
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
    band = tuple(float(v) for v in qcfg["expected_band_hz"])
    for t in ts:
        if probs := plausibility(t, band):
            raise ValueError(f"{Path(t.path).name}: implausible decode: {probs}")

    mask = bool(qcfg.get("mask_glitches", False)) if mask is None else mask
    native, logs = [], []
    for fname, t in zip(man["file"], ts):
        if mask:
            s, log = mask_glitches(t.f_hz, t.s, float(qcfg.get("glitch_thr_db", -30.0)))
            logs += [{"file": fname, **r} for r in log]
        else:
            s = t.s
        native.append(s)

    opt = lambda v: None if v in (None, "auto") else float(v)     # noqa: E731
    f = common_grid([t.f_hz for t in ts], opt(gcfg.get("step_hz")), opt(gcfg.get("f_min_hz")),
                    opt(gcfg.get("f_max_hz")))
    S = np.stack([resample(t.f_hz, s, f) for t, s in zip(ts, native)])
    log_df = pd.DataFrame(logs)
    if len(log_df):
        log_df["in_common_band"] = ((log_df["f_GHz"] * 1e9 >= f[0] - 1)
                                    & (log_df["f_GHz"] * 1e9 <= f[-1] + 1))
    p2a = np.asarray(cfg["ring"]["port_to_ant"])
    if sorted(p2a) != list(range(1, n.pop() + 1)):
        raise ValueError(f"config ring.port_to_ant {p2a} is not a permutation of the ports")
    return Dataset(f, S, list(man["class"]), list(man["file"]), p2a, man, ts, log_df, mask)
