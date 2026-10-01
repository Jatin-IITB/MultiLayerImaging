"""Track A imaging study - one command:

    python imaging/run_imaging.py [--reuse] [--only paths,i1,val,i2,i3] [--no-csv] [--quick]
                                  [--jobs N] [--fallback SIM_SET]

Data = the current config (MLI_CONFIG overlay honoured, default config.yaml -> data/sims.csv).
Runs
  paths : data-driven propagation-path test (k = 3 question) on HFSS ring couplings
  i1    : DAS / DMAS / MVDR radar imaging of dS
  val   : forward-model (a) validation (polarisation, harmonics convergence, dS prediction)
  i2    : sensitivity maps + linearised radial / voxel inversions. With the HFSS field exports in
          data/fields/ (study_i2_hfss): HFSS Green's function + k = 3 path; otherwise forward-model
          fields, labelled SURROGATE (study_i2)
  i3    : 9-parameter model-based nonlinear inversion, identifiability, CSF-thickness classifier
and writes results/imaging/{report.md, metrics_imaging.csv, figures/*.png}.

Caches live in results/imaging/cache/<sim_set>/ (not committed); --reuse loads them.
--fallback SIM_SET fills the report sections that were not computed for the current data from
that set's caches (each section is labelled with the data it used). Metrics rows are written
only for studies computed in this run on the current data.
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

from imaging import paths, study_i1, study_i2, study_i2_hfss, study_i3  # noqa: E402
from imaging.common import OUT, data_tag, load_config, load_stages  # noqa: E402
from imaging.fields import fields_available  # noqa: E402

V1_TAG = dict(sim_set="hfss-v1-masked", config="config.yaml (v1, before 2026-10-01)",
              files={"Normal": "brain_sevem_layer_Healthy.s6p", "Mild": "Brain_sevem_layer_MildAD.s6p",
                     "Moderate": "Brain_sevem_layer_ModerateAD.s6p", "Severe": "brain_sevem_layer_SevereAD.s6p"},
              band_GHz="3.2-4.2")


def cache_dir(sim_set):
    d = OUT / "cache" / sim_set
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_cached(sim_set, name):
    p = OUT / "cache" / sim_set / f"{name}.pkl"
    if not p.exists():
        return None
    with p.open("rb") as fh:
        r = pickle.load(fh)
    if isinstance(r, dict) and "_data" not in r and sim_set == V1_TAG["sim_set"]:
        r["_data"] = V1_TAG                     # caches written before results were tagged
    return r


def cached(name, fn, reuse, sim_set, tag):
    if reuse and (r := load_cached(sim_set, name)) is not None:
        return r
    t = time.time()
    r = fn()
    if isinstance(r, dict):
        r["_data"] = tag
    print(f"[{name}] {time.time() - t:.0f} s", flush=True)
    with (cache_dir(sim_set) / f"{name}.pkl").open("wb") as fh:
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
    ap.add_argument("--fallback", default=None,
                    help="sim_set whose cached results fill sections not computed for the current data")
    a = ap.parse_args()
    only = set(a.only.split(","))
    cfg = load_config()
    sd = load_stages(cfg)
    ss = cfg["metrics"]["sim_set"]
    tag = data_tag(sd, cfg)
    print("data:", tag)
    nd = 4 if a.quick else None
    R, fresh = {}, set()

    def go(name, fn):
        R[name] = cached(name, fn, a.reuse, ss, tag)
        fresh.add(name)

    if "paths" in only:
        go("paths", lambda: paths.run(sd))
    if "i1" in only:
        go("i1", lambda: study_i1.run(sd, cfg, n_draw=nd or 20))
    model = val = None
    if {"val", "i3"} & only or ("i2" in only and not fields_available()):
        f_fit = sd.f_hz[::4]
        go("val", lambda: dict(zip(("model", "val"), study_i3.validate(sd, f_fit))))
        model, val = R["val"]["model"], R["val"]["val"]
    if "i2" in only:
        if fields_available():
            go("i2", lambda: study_i2_hfss.run(sd, n_draw=nd or 30))
        else:
            go("i2", lambda: study_i2.run(sd, model, n_draw=nd or 30))
    if "i3" in only:
        go("i3", lambda: study_i3.run(sd, model, val, n_draw=nd or 20,
                                      n_starts=3 if a.quick else 6, n_jobs=a.jobs,
                                      ck_dir=cache_dir(ss)))
    if a.fallback:
        for name in ("paths", "i1", "val", "i2", "i3"):
            if name not in R and (r := load_cached(a.fallback, name)) is not None:
                R[name] = r
    if "val" in R and isinstance(R["val"], dict) and "val" in R["val"]:
        R["val"] = dict(R["val"]["val"], _data=R["val"].get("_data", tag))
    from imaging import report
    report.write(R, sd, cfg, write_csv=not a.no_csv, fresh=fresh)
    print("wrote", OUT / "report.md")


if __name__ == "__main__":
    main()
