"""Track A imaging study - one command:

    python imaging/run_imaging.py [--reuse] [--only paths,i1,val,i2,i3] [--no-csv] [--quick] [--jobs N]

Reads data/sims.csv + data/raw (shared loader, glitch masking ON), runs
  paths : data-driven propagation-path test (k = 3 question) on HFSS ring couplings
  i1    : DAS / DMAS / MVDR radar imaging of dS
  val   : forward-model (a) validation (polarisation, harmonics convergence, dS prediction)
  i2    : sensitivity maps + linearised radial / voxel inversions (HFSS fields if present,
          otherwise forward-model fields, labelled SURROGATE)
  i3    : 9-parameter model-based nonlinear inversion, identifiability, CSF-thickness classifier
and writes results/imaging/{report.md, metrics_imaging.csv, figures/*.png}.
--reuse loads cached study results from results/imaging/cache/ (not committed).
Tuning is done on Mild only; Moderate and Severe are reported.
"""
from __future__ import annotations

import argparse
import pickle
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

from imaging import paths, study_i1, study_i2, study_i3  # noqa: E402
from imaging.common import OUT, load_config, load_stages  # noqa: E402

CACHE = OUT / "cache"


def cached(name, fn, reuse):
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{name}.pkl"
    if reuse and p.exists():
        with p.open("rb") as fh:
            return pickle.load(fh)
    t = time.time()
    r = fn()
    print(f"[{name}] {time.time() - t:.0f} s", flush=True)
    with p.open("wb") as fh:
        pickle.dump(r, fh)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument("--only", default="paths,i1,val,i2,i3")
    ap.add_argument("--no-csv", action="store_true")
    ap.add_argument("--quick", action="store_true", help="few draws (smoke test)")
    ap.add_argument("--jobs", type=int, default=1,
                    help="parallel worker processes for the I3 fits (e.g. $SLURM_CPUS_PER_TASK)")
    a = ap.parse_args()
    only = set(a.only.split(","))
    cfg = load_config()
    sd = load_stages(cfg)
    print("stages:", {s: sd.files[s] for s in sd.S}, "grid", sd.f_hz[0], sd.f_hz[-1], len(sd.f_hz))
    nd = 4 if a.quick else None
    R = {}
    if "paths" in only:
        R["paths"] = cached("paths", lambda: paths.run(sd), a.reuse)
    if "i1" in only:
        R["i1"] = cached("i1", lambda: study_i1.run(sd, cfg, n_draw=nd or 20), a.reuse)
    if {"val", "i2", "i3"} & only:
        f_fit = sd.f_hz[::4]
        model, val = study_i3.validate(sd, f_fit)
        R["val"] = val
    if "i2" in only:
        R["i2"] = cached("i2", lambda: study_i2.run(sd, model, n_draw=nd or 30), a.reuse)
    if "i3" in only:
        R["i3"] = cached("i3", lambda: study_i3.run(sd, model, val, n_draw=nd or 20,
                                                     n_starts=3 if a.quick else 6,
                                                     n_jobs=a.jobs), a.reuse)
    from imaging import report
    report.write(R, sd, cfg, write_csv=not a.no_csv)
    print("wrote", OUT / "report.md")


if __name__ == "__main__":
    main()
