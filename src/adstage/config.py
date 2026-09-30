"""Config loading with a single-level overlay mechanism.

The config file is chosen by the MLI_CONFIG environment variable (default config.yaml, relative to
the repo root). A config may say `extends: <other.yaml>`; it is then deep-merged onto that base.
`results.out_root` (default "results") is where 02/, 03/, qc/ and figures/ are written;
results/metrics.csv is always the shared, append-only log.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(root: str | Path, name: str | None = None) -> dict:
    root = Path(root)
    path = root / (name or os.environ.get("MLI_CONFIG", "config.yaml"))
    cfg = yaml.safe_load(path.read_text())
    if "extends" in cfg:
        base = load_config(root, cfg.pop("extends"))
        cfg = _merge(base, cfg)
    cfg.setdefault("results", {}).setdefault("out_root", "results")
    cfg["_config_file"] = path.name
    return cfg


def out_dir(root: str | Path, cfg: dict, *parts: str) -> Path:
    """<root>/<results.out_root>/<parts...>, created if missing."""
    p = Path(root) / cfg["results"]["out_root"]
    for s in parts:
        p = p / s
    p.mkdir(parents=True, exist_ok=True)
    return p
