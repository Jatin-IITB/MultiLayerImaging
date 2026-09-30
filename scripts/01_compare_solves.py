"""Compare two solves of the same stages: how much does a re-solve move the data, compared with
the disease effect?

    python scripts/01_compare_solves.py [--old data/archive/v1_mixed_projects]

Old set = the archived folder (raw/ + sims.csv); new set = config.yaml data.raw_dir / manifest.
Both are put on their common band at the coarser step. Writes results/qc/solve_comparison.md.

Two kinds of quantity are compared:
  * whole-spectrum shape: rms over frequency of the dB difference of each ring mode k = 0..3
  * band-averaged scalars used by the classifier: M5.C3 (opposite-path power, dB) and M5.R31
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

from adstage.config import load_config, out_dir  # noqa: E402
from adstage.features.floor import r31  # noqa: E402
from adstage.features.metrics import band_avg, to_ring_order  # noqa: E402
from adstage.io.dataset import common_grid, load_manifest, resample  # noqa: E402
from adstage.io.touchstone import read_touchstone  # noqa: E402


def load_set(folder_raw: Path, manifest: Path):
    man = load_manifest(manifest)
    return {c: read_touchstone(folder_raw / f) for f, c in zip(man["file"], man["class"])}


def md(df, fmt=".2f"):
    head = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    rows = ["| " + " | ".join(format(v, fmt) if isinstance(v, float) else str(v) for v in r) + " |"
            for r in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", default="data/archive/v1_mixed_projects")
    args = ap.parse_args()
    cfg = load_config(ROOT)
    old_dir = ROOT / args.old
    old = load_set(old_dir / "raw", old_dir / "sims.csv")
    new = load_set(ROOT / cfg["data"]["raw_dir"], ROOT / cfg["data"]["manifest"])
    p2a = np.asarray(cfg["ring"]["port_to_ant"])
    f = common_grid([t.f_hz for t in list(old.values()) + list(new.values())])
    band = (float(f[0]), float(f[-1]))
    O = {c: to_ring_order(resample(t.f_hz, t.s, f), p2a) for c, t in old.items()}
    N = {c: to_ring_order(resample(t.f_hz, t.s, f), p2a) for c, t in new.items()}
    n = next(iter(N.values())).shape[-1]
    idx = np.arange(n)
    ref = cfg["classes"]["reference"]

    def mode_db(S, k):
        return 20 * np.log10(np.abs(S[:, (idx + k) % n, idx].mean(1)))

    def shape_diff(A, B):
        return {f"k{k} rms dB": float(np.sqrt(np.mean((mode_db(A, k) - mode_db(B, k)) ** 2)))
                for k in range(n // 2 + 1)}

    def c3(S):
        p = np.abs(S[:, (idx + n // 2) % n, idx]) ** 2
        return float(10 * np.log10(band_avg(f, p.T, band).mean()))

    def ratio(S):
        return float(10 * np.log10(r31(f, S[None], np.zeros(1), band)[0]))

    rows = []
    for c in [c for c in N if c in O]:
        rows.append({"comparison": f"{c}: old vs new solve", **shape_diff(O[c], N[c])})
    for c in [c for c in N if c != ref]:
        rows.append({"comparison": f"new {ref} vs new {c}", **shape_diff(N[ref], N[c])})
    shape = pd.DataFrame(rows)
    scal = pd.DataFrame([{"stage": c,
                          "C3 old dB": c3(O[c]) if c in O else np.nan, "C3 new dB": c3(N[c]),
                          "C3 shift dB": c3(N[c]) - c3(O[c]) if c in O else np.nan,
                          "R31 old dB": ratio(O[c]) if c in O else np.nan, "R31 new dB": ratio(N[c]),
                          "R31 shift dB": ratio(N[c]) - ratio(O[c]) if c in O else np.nan}
                         for c in N])
    ad = [c for c in N if c not in (ref, "MCI")]
    gap_c3 = [c3(N[ref]) - c3(N[c]) for c in ad]
    gap_r = [ratio(N[ref]) - ratio(N[c]) for c in ad]
    L = [f"# Solve comparison: {args.old} (old) vs {cfg['data']['raw_dir']} (new)", "",
         f"Common band {band[0] / 1e9:.2f}-{band[1] / 1e9:.2f} GHz, {f.size} points. No glitch masking "
         "(raw solver output).", "",
         "## Whole-spectrum shape (rms over frequency of the ring-mode dB difference)", md(shape), "",
         "## Band-averaged scalars (classifier features)", md(scal), "",
         f"New-set {ref} vs AD gap: C3 {min(gap_c3):.2f}-{max(gap_c3):.2f} dB, "
         f"R31 {min(gap_r):.2f}-{max(gap_r):.2f} dB. Largest old-to-new shift of the same stage: "
         f"C3 {np.nanmax(np.abs(scal['C3 shift dB'])):.2f} dB, R31 {np.nanmax(np.abs(scal['R31 shift dB'])):.2f} dB."]
    out = out_dir(ROOT, cfg, "qc") / "solve_comparison.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
