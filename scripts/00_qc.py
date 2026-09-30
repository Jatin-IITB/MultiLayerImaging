"""Prompt 01A: parse all files, integrity checks, symmetry noise floor, confound assessment.

Usage:  python scripts/00_qc.py [--include-moderate]   (QC always loads every file in sims.csv;
        the flag only affects which classes appear in the class-level confound figure.)
Writes: results/qc/*.csv, results/qc/qc_report.md, results/figures/qc_*.png,
        data/processed/common_grid.npz
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adstage import qc                                   # noqa: E402
from adstage.config import load_config, out_dir  # noqa: E402
from adstage.io.dataset import load_dataset             # noqa: E402
from adstage.ring import pairs_at_distance, ring_average  # noqa: E402

OUT = ROOT / "results" / "qc"
FIG = ROOT / "results" / "figures"
# Ordinal blue ramp (dataviz palette, light steps 250 -> 700) : Normal ... Severe
STAGE_COLOR = {"Normal": "#86b6ef", "MCI": "#5598e7", "Mild": "#2a78d6",
               "Moderate": "#1c5cab", "Severe": "#0d366b"}


def md(df: pd.DataFrame, floatfmt=".3g") -> str:
    def cell(v):
        if isinstance(v, (float, np.floating)):
            return format(v, floatfmt)
        return str(v)
    head = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    body = ["| " + " | ".join(cell(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-moderate", action="store_true")
    args = ap.parse_args()
    cfg = load_config(ROOT)
    global OUT, FIG
    OUT, FIG = out_dir(ROOT, cfg, "qc"), out_dir(ROOT, cfg, "figures")
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    ds = load_dataset(cfg, ROOT, mask=False)  # QC describes the raw files (no glitch masking)
    p2a = ds.port_to_ant
    n = ds.S.shape[-1]
    proj = dict(zip(ds.files, ds.manifest["project"]))
    try:
        from adstage.results import git_hash
        gh = git_hash(ROOT)
    except Exception:                       # noqa: BLE001 - report runs without git too
        gh = "no-git"
    rep = [f"# QC report - track {cfg['track']} ({cfg['model_id']}), code {gh}", ""]

    # ---------- 1. parse summary (native grids) ----------
    rows = []
    for c, t in zip(ds.classes, ds.raw):
        df_ = np.diff(t.f_hz)
        rows.append({"class": c, "file": Path(t.path).name, "N": t.n_ports,
                     "F_native": t.f_hz.size, "f_min_GHz": t.f_hz[0] / 1e9,
                     "f_max_GHz": t.f_hz[-1] / 1e9, "step_MHz": np.median(df_) / 1e6,
                     "uniform": bool(np.ptp(df_) < 1.0), "option_line": t.option_line,
                     "values_per_f": 2 * t.n_ports ** 2})
    parse = pd.DataFrame(rows)
    parse.to_csv(OUT / "parse.csv", index=False)
    rep += ["## Parsed files (native grids)", md(parse, ".4g"),
            f"\nCommon grid: {ds.f_hz[0]/1e9:.3f}-{ds.f_hz[-1]/1e9:.3f} GHz, "
            f"{ds.f_hz.size} points, step {np.diff(ds.f_hz)[0]/1e6:.1f} MHz. "
            f"S tensor shape {ds.S.shape} (sims, F, N, N).\n"]

    # ---------- 2. integrity (native grids) ----------
    rows, circ_rows = [], []
    for c, t in zip(ds.classes, ds.raw):
        r = {"class": c, **qc.reciprocity(t.s, t.f_hz), **qc.passivity(t.s, cfg["qc"]["passivity_tol"])}
        on_grid = np.isin(np.round(ds.f_hz), np.round(t.f_hz)).all()
        r["resampled"] = not on_grid
        if not on_grid:
            r.update(qc.interp_error(t.f_hz, t.s))
        rows.append(r)
    for s_i, c in enumerate(ds.classes):
        for k, v in qc.circulant_spread(ds.S[s_i], p2a).items():
            circ_rows.append({"class": c, "k": k, "n_pairs": len(pairs_at_distance(p2a, k)), **v})
    integ = pd.DataFrame(rows)
    glitches = integ[["class", "glitch_f_GHz"]]
    integ = integ.drop(columns="glitch_f_GHz")
    circ = pd.DataFrame(circ_rows)
    integ.to_csv(OUT / "integrity.csv", index=False)
    circ.to_csv(OUT / "circulant_spread.csv", index=False)
    rep += ["## Integrity (native grids)",
            "recip_rel_band_* = |Sij - Sji| / band-rms|Sij| over off-diagonal entries (dB). "
            "n_glitch_pts = (f, pair) points with local |Sij - Sji|/|Sij| > -20 dB. "
            "Passive = column power sum and largest singular value <= 1 + tol. "
            "interp_* = leave-every-other-out spline error / band-rms level (dB).",
            md(integ), "", "Glitch frequencies (GHz):", "",
            *[f"- {c}: {g}" for c, g in glitches.itertuples(index=False)], "",
            "## Circulant symmetry spread per ring distance k (common grid)",
            "mag_spread = max-min of |S(t,t+k)| across t in dB; cplx_rel = rms complex "
            "deviation from the ring mean relative to its magnitude (dB, noise-to-signal).",
            md(circ), ""]

    # ---------- 3. port -> antenna mapping check ----------
    map_rows = []
    cfg_err = {}
    for c, t in zip(ds.classes, ds.raw):
        res = qc.mapping_search(t.s)
        cfg_err[c] = qc.circulant_error(t.s, p2a)
        rank = 1 + sum(e < cfg_err[c] - 1e-12 for e, _ in res)
        map_rows.append({"class": c, "config_mapping_error_db": cfg_err[c],
                         "config_rank_of_60": rank,
                         "best_mapping": "-".join(str(int(v)) for v in res[0][1]),
                         "best_error_db": res[0][0], "2nd_best_error_db": res[1][0],
                         "worst_error_db": res[-1][0]})
    maps = pd.DataFrame(map_rows)
    maps.to_csv(OUT / "port_mapping_search.csv", index=False)
    rep += ["## Port-to-antenna mapping check",
            "All 60 distinct ring orderings (720 permutations mod rotation/reflection) scored by "
            "circulant error = mean over f and k>=1 of std_t |S(t,t+k)| (dB). Config mapping "
            f"port_to_ant = {[int(v) for v in p2a]} (equivalent under reflection/rotation "
            "to 1-2-3-4-5-6, i.e. ports in file order are consecutive around the ring).",
            md(maps), ""]

    # ---------- 4. orientation: resonance and shoulder (native grids) ----------
    lo, hi = cfg["qc"]["shoulder_band_hz"]
    res_rows = []
    for c, t in zip(ds.classes, ds.raw):
        band = (t.f_hz >= lo) & (t.f_hz <= hi)
        for p in range(n):
            sii = t.s[:, p, p]
            res_rows.append({"class": c, "port": p + 1,
                             "f_res_MHz": qc.resonance(t.f_hz, sii) / 1e6,
                             "min_dB": qc.db(sii).min(),
                             "shoulder_pow_dB": 10 * np.log10(np.mean(np.abs(sii[band]) ** 2))})
    reso = pd.DataFrame(res_rows)
    reso.to_csv(OUT / "resonance_per_port.csv", index=False)
    agg = reso.groupby("class", sort=False).agg(
        f_res_mean_MHz=("f_res_MHz", "mean"), f_res_min=("f_res_MHz", "min"),
        f_res_max=("f_res_MHz", "max"), notch_min_dB=("min_dB", "min"),
        notch_max_dB=("min_dB", "max"), shoulder_mean_dB=("shoulder_pow_dB", "mean"),
        shoulder_spread_dB=("shoulder_pow_dB", np.ptp)).reset_index()
    rep += ["## Orientation re-derivation (native grids, per-port min |Sii|, parabolic refine)",
            f"Shoulder = power average of |Sii|^2 over {lo/1e9:.2f}-{hi/1e9:.2f} GHz.",
            md(agg, ".5g"), ""]

    # ---------- 5. confound assessment (common grid) ----------
    C = ring_average(ds.S, p2a)                         # (sims, F, 4)
    noise = np.empty((len(ds.files), n // 2 + 1))
    noise_db = np.empty_like(noise)
    for s_i in range(len(ds.files)):
        for k in range(n // 2 + 1):
            pr = pairs_at_distance(p2a, k)
            x = np.stack([ds.S[s_i, :, i, j] for i, j in pr], -1)
            noise[s_i, k] = np.sqrt(np.mean(np.abs(x - C[s_i, :, k, None]) ** 2))
            noise_db[s_i, k] = np.sqrt(np.mean(qc.db(x).std(-1) ** 2))
    band = (ds.f_hz >= lo) & (ds.f_hz <= hi)
    rows = []
    for a, b in itertools.combinations(range(len(ds.files)), 2):
        r = {"pair": f"{ds.classes[a]}-{ds.classes[b]}",
             "same_project": proj[ds.files[a]] == proj[ds.files[b]]}
        for k in range(n // 2 + 1):
            d = np.sqrt(np.mean(np.abs(C[a, :, k] - C[b, :, k]) ** 2))
            nz = np.sqrt((noise[a, k] ** 2 + noise[b, k] ** 2) / 2)
            ddb = np.sqrt(np.mean((qc.db(C[a, :, k]) - qc.db(C[b, :, k])) ** 2))
            r[f"k{k}_diff/noise"] = d / nz
            r[f"k{k}_rms_dB_diff"] = ddb
        r["k0_shoulder_dB_diff"] = (10 * np.log10(np.mean(np.abs(C[b, band, 0]) ** 2))
                                    - 10 * np.log10(np.mean(np.abs(C[a, band, 0]) ** 2)))
        rows.append(r)
    conf = pd.DataFrame(rows)
    conf.to_csv(OUT / "confound.csv", index=False)
    nz_tab = pd.DataFrame({"class": ds.classes,
                           **{f"k{k}_port_noise_rms_dB": noise_db[:, k] for k in range(n // 2 + 1)}})
    rep += ["## Confound assessment (common grid)",
            "Ring-mode c_k(f) = mean_t S(t,t+k). diff/noise = rms_f|c_k^a - c_k^b| divided by the "
            "pooled rms port-to-port deviation (complex). rms_dB_diff = rms_f of dB difference "
            "of |c_k|. Project membership is from the model card (sims.csv), not from file headers.",
            md(conf), "", "Within-file port-to-port noise (rms over f of std_t in dB):",
            md(nz_tab), ""]
    (OUT / "qc_report.md").write_text("\n".join(rep), encoding="utf-8")
    np.savez_compressed(ROOT / cfg["data"]["processed_dir"] / "common_grid.npz",
                        f_hz=ds.f_hz, S=ds.S, classes=np.array(ds.classes),
                        files=np.array(ds.files), port_to_ant=p2a)

    # ---------- 6. figure ----------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.color": "#e4e3de", "grid.linewidth": 0.6,
                         "axes.edgecolor": "#8a8981", "axes.labelcolor": "#3d3d3a",
                         "xtick.color": "#5f5e59", "ytick.color": "#5f5e59"})
    show = [c for c in ["Normal", "MCI", "Mild", "Moderate", "Severe"]
            if c in ds.classes and (args.include_moderate or c != "Moderate")]
    titles = ["k=0  reflection |S(t,t)|", "k=1  neighbour |S(t,t+1)|",
              "k=2  |S(t,t+2)|", "k=3  opposite |S(t,t+3)|"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), sharex=True)
    for k, ax in enumerate(axes.flat):
        for c in show:
            s_i = ds.classes.index(c)
            pr = pairs_at_distance(p2a, k)
            x = qc.db(np.stack([ds.S[s_i, :, i, j] for i, j in pr], -1))
            f = ds.f_hz / 1e9
            ax.fill_between(f, x.min(-1), x.max(-1), color=STAGE_COLOR[c], alpha=0.18, lw=0)
            ax.plot(f, qc.db(C[s_i, :, k]), color=STAGE_COLOR[c], lw=2, label=c)
        if k == 0:
            ax.axvspan(lo / 1e9, hi / 1e9, color="#f0efec", zorder=0)
        ax.set_title(titles[k], loc="left", fontsize=9.5, color="#1f1e1c")
        ax.set_ylabel("dB")
    for ax in axes[1]:
        ax.set_xlabel("Frequency (GHz)")
    axes[0, 0].legend(frameon=False, loc="lower left")
    fig.suptitle("Ring-mode S-parameters by stage (line = ring mean, band = port-to-port "
                 "min-max; grey = shoulder band)", x=0.01, ha="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "qc_ring_modes.png", dpi=150)
    print((OUT / "qc_report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
