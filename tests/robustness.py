"""Frequency-robustness table (prompt 02 §2), runnable on its own.

    python tests/robustness.py [--no-mask]

Prints, per metric and perturbation, |Δ metric| in units of the Normal-Mild gap, and writes
results/02/robustness_standalone.csv. scripts/02_metrics.py runs the same code and also
applies the per-scheme "frequency-robust" criterion (< 0.25 × smallest class gap).
Not collected by pytest (file name has no test_ prefix).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adstage.features.metrics import build_catalogue, circulant_projection, to_ring_order  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.robustness import perturbed_values  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-mask", action="store_true")
    args = ap.parse_args()
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    ds = load_dataset(cfg, ROOT, mask=not args.no_mask)
    S = to_ring_order(ds.S, ds.port_to_ant)
    ref = circulant_projection(S[ds.classes.index("Normal")])
    metrics, bands = build_catalogue(ds.f_hz, tuple(float(v) for v in cfg["metrics"]["k3_band_hz"]),
                                     float(cfg["metrics"]["subband_hz"]))
    pert = perturbed_values(metrics, bands, ds.f_hz, list(S), ref, seed=cfg["seed"])
    iN, iM = ds.classes.index("Normal"), ds.classes.index("Mild")
    rows = []
    for m in metrics:
        o = pert["orig"][m.name]
        gap = abs(o[iN] - o[iM])
        rows.append({"metric": m.name, **{p: np.nanmax(np.abs(v[m.name] - o)) / gap
                                          for p, v in pert.items() if p != "orig"}})
    df = pd.DataFrame(rows)
    out = ROOT / "results" / "02"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "robustness_standalone.csv", index=False)
    with pd.option_context("display.max_rows", 200, "display.width", 250,
                           "display.float_format", "{:.2g}".format):
        print(df)


if __name__ == "__main__":
    main()
