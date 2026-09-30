"""Prompt 02: power-based metrics, frequency-robustness, separability under noise.

Usage:  python scripts/02_metrics.py [--include-moderate] [--no-mask] [--n 500] [--no-csv]
Writes: results/metrics.csv (append, classifier=none-fisher), results/02/*.csv,
        results/02/report.md, results/figures/02_*.png, results/qc/masked_points.csv
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

from adstage.classes import active_schemes, pair_is_ad_only, scheme_groups, scheme_label  # noqa: E402
from adstage.noise.reference import mesh_pairs, mesh_sd  # noqa: E402
from adstage.config import load_config, out_dir  # noqa: E402
from adstage.features.metrics import (build_catalogue, circulant_projection, compute,  # noqa: E402
                                      power_spectra, to_ring_order)
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.noise.model import PROFILES, realise  # noqa: E402
from adstage.results import append_row, git_hash  # noqa: E402
from adstage.robustness import FREQ_ROBUST_SET, perturbed_values  # noqa: E402
from adstage.separability import pairwise  # noqa: E402

OUT = ROOT / "results" / "02"
FIG = ROOT / "results" / "figures"
STAGE_COLOR = {"Normal": "#86b6ef", "MCI": "#5598e7", "Mild": "#2a78d6", "Moderate": "#1c5cab", "Severe": "#0d366b"}
MESH_NOTE = "AD-vs-AD pairs unverified against mesh noise"


def md(df: pd.DataFrame, floatfmt=".3g") -> str:
    def cell(v):
        if isinstance(v, (float, np.floating)):
            return "n/a" if not np.isfinite(v) else format(v, floatfmt)
        return str(v)
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    body = ["| " + " | ".join(cell(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def group_means(values: np.ndarray, groups: dict[str, list[int]]) -> np.ndarray:
    return np.array([np.mean([values[s] for s in v]) for v in groups.values()])


def main():
    np.seterr(all="ignore")          # open/short faults make some metrics undefined (NaN) by design
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-moderate", action="store_true")
    ap.add_argument("--no-mask", action="store_true")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--no-csv", action="store_true", help="do not append to metrics.csv")
    args = ap.parse_args()
    cfg = load_config(ROOT)
    global OUT, FIG
    OUT, FIG = out_dir(ROOT, cfg, "02"), out_dir(ROOT, cfg, "figures")
    mcfg = cfg["metrics"]
    n_real = args.n or int(mcfg["n_realisations"])
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)

    ds = load_dataset(cfg, ROOT, mask=not args.no_mask)
    sim_set = mcfg["sim_set"] if ds.masking else mcfg["sim_set"].replace("-masked", "-unmasked")
    if ds.masking:
        ds.masked_log.to_csv(out_dir(ROOT, cfg, "qc") / "masked_points.csv", index=False)
    f = ds.f_hz
    S = to_ring_order(ds.S, ds.port_to_ant)
    n_sims = len(ds.files)
    normal_idx = [i for i, c in enumerate(ds.classes) if c == cfg["classes"]["reference"]]
    ref = np.mean([circulant_projection(S[i]) for i in normal_idx], 0)
    metrics, bands = build_catalogue(f, tuple(float(v) for v in mcfg["k3_band_hz"]),
                                     float(mcfg["subband_hz"]))
    mby = {m.name: m for m in metrics}
    print(f"code {gh}; {n_sims} sims; {len(metrics)} scalar metrics; {n_real} realisations")

    # ---- noise-free values ----------------------------------------------------------
    clean = [compute(metrics, bands, f, S[s], ref) for s in range(n_sims)]

    # ---- noisy realisations -----------------------------------------------------------
    noisy: dict[str, list[dict]] = {}
    spec_q = {}                                         # typical-profile spectra quantiles
    for pi, (pname, prof) in enumerate(PROFILES.items()):
        noisy[pname] = []
        for s in range(n_sims):
            rng = np.random.default_rng([cfg["seed"], pi, s])
            R = realise(f, S[s], prof, n_real, rng)
            v = compute(metrics, bands, f, R, ref)
            noisy[pname].append({k: x.mean(-1) for k, x in v.items()})
            if pname == "typical":
                sp = power_spectra(R)
                spec_q[s] = {k: np.percentile(sp[k].mean(-1), [5, 95], axis=0)
                             for k in ("R", "A", "N", "C", "C3")}
        print(f"  noise profile {pname} done")

    # ---- robustness -------------------------------------------------------------------
    pert = perturbed_values(metrics, bands, f, list(S), ref, seed=cfg["seed"])
    rob_rows = []
    for m in metrics:
        orig = pert["orig"][m.name]
        cm = {c: np.mean([orig[i] for i in range(n_sims) if ds.classes[i] == c]) for c in set(ds.classes)}
        gap_nmi = abs(cm["Normal"] - cm["Mild"])
        stage_vals = np.array(list(cm.values()))
        span = stage_vals.max() - stage_vals.min()
        for p, pv in pert.items():
            if p == "orig":
                continue
            vals = pv[m.name]
            not_applicable = p.startswith("band_3") and m.band != "full"
            d = np.abs(vals - orig)
            row = {"metric": m.name, "method_id": m.method_id, "perturbation": p,
                   "max_abs_delta": np.nan if not_applicable else np.nanmax(d),
                   "gap_N_Mi": gap_nmi,
                   "ratio_to_gap_N_Mi": np.nan if not_applicable else np.nanmax(d) / gap_nmi}
            if p in ("open_all", "short_all", "one_open"):
                finite = bool(np.all(np.isfinite(vals)))
                inside = bool(np.any((vals >= stage_vals.min() - 0.5 * span)
                                     & (vals <= stage_vals.max() + 0.5 * span)))
                row.update(finite=finite, lands_in_class_range=inside)
            rob_rows.append(row)
    rob = pd.DataFrame(rob_rows)
    rob.to_csv(OUT / "robustness.csv", index=False)

    # ---- separability per scheme ------------------------------------------------------
    schemes, skipped = active_schemes(cfg, ds.classes, args.include_moderate)
    mpairs = mesh_pairs(ds.files, ds.manifest)
    if skipped:
        print(f"skipped schemes: {skipped}")
    pair_rows, rank_tables = [], {}
    for scheme in schemes:
        groups_st = scheme_groups(cfg, scheme)
        groups = {g: [i for i, c in enumerate(ds.classes) if c in st] for g, st in groups_st.items()}
        groups = {g: v for g, v in groups.items() if v}
        nspc = "|".join(f"{g}:{len(v)}" for g, v in groups.items())
        summ = []
        for pname in PROFILES:
            for m in metrics:
                rows = pairwise(groups, {s: noisy[pname][s][m.name] for s in range(n_sims)},
                                {s: clean[s][m.name] for s in range(n_sims)})
                msd = mesh_sd(pert["orig"][m.name], mpairs)
                for r in rows:
                    a, b = r["pair"].split("|")
                    r.update(scheme=scheme, profile=pname, metric=m.name, method_id=m.method_id,
                             ad_only=pair_is_ad_only(groups_st, a, b), gap_over_mesh=r["gap"] / msd)
                pair_rows += rows
                df = pd.DataFrame(rows)
                w = df.loc[df["J_meas"].idxmin()]
                # smallest clean gap between groups (for the robustness criterion)
                gv = group_means(pert["orig"][m.name], groups)
                iu = np.triu_indices(len(gv), 1)
                gaps = (gv[:, None] - gv[None, :])[iu]
                min_gap = np.min(np.abs(gaps))
                rsub = rob[rob.metric == m.name].set_index("perturbation")["max_abs_delta"]
                shift_move = rsub[[p for p in FREQ_ROBUST_SET if p.startswith("shift")]].max()
                band_move = rsub[[p for p in FREQ_ROBUST_SET if p.startswith("band")]].max()
                robust = bool(max(shift_move, band_move) < 0.25 * min_gap)
                # does the class gap survive a ±10 % band change? (signed: < 0 = order flips)
                ret = min(np.min((gp[:, None] - gp[None, :])[iu] / gaps)
                          for gp in (group_means(pert[p][m.name], groups)
                                     for p in FREQ_ROBUST_SET if p.startswith("band")))
                summ.append({"scheme": scheme, "profile": pname, "metric": m.name,
                             "method_id": m.method_id, "min_J_meas": df["J_meas"].min(),
                             "weakest_pair": w["pair"], "min_J_eff": df["J_eff"].min(),
                             "min_gap_over_port": df["gap_over_port"].min(),
                             "min_bhatt": df["bhatt"].min(), "max_bayes_err": df["bayes_err"].max(),
                             "shift_move_over_min_gap": shift_move / min_gap,
                             "shift_robust": bool(shift_move < 0.25 * min_gap),
                             "band_move_over_min_gap": band_move / min_gap,
                             "band_gap_retention": ret, "freq_robust": robust,
                             "any_ad_pair": bool(df["ad_only"].any()), "note": m.note})
                if not args.no_csv:
                    notes = [f"weakest={w['pair']}", f"J_eff_min={df['J_eff'].min():.3g}",
                             f"gap/port_min={df['gap_over_port'].min():.3g}",
                             (f"gap/mesh_min={df['gap_over_mesh'].min():.3g}" if mpairs else "gap/mesh=pending"),
                             f"bayes_err_max={df['bayes_err'].max():.3g}",
                             f"shift_robust={'yes' if shift_move < 0.25 * min_gap else 'no'}",
                             f"band_gap_retention={ret:.2f}",
                             f"freq_robust={'yes' if robust else 'no'}"]
                    if df["ad_only"].any() and not mpairs:
                        notes.append(MESH_NOTE)
                    if m.note:
                        notes.append(m.note)
                    append_row(ROOT / cfg["results"]["metrics_csv"], {
                        "git_hash": gh, "track": cfg["track"], "model_id": cfg["model_id"],
                        "sim_set": sim_set, "classes": scheme_label(cfg, scheme),
                        "method_id": m.method_id, "feature_desc": f"{m.name}: {m.desc}",
                        "feature_dim": 1, "classifier": "none-fisher", "noise_profile": pname,
                        "cv_scheme": "none (noisy realisations of 1 sim/stage)",
                        "n_sims_per_class": nspc, "n_test": n_real * sum(map(len, groups.values())),
                        "min_pairwise_fisher": df["J_meas"].min(),
                        "min_pairwise_bhattacharyya": df["bhatt"].min(), "notes": "; ".join(notes)})
        sdf = pd.DataFrame(summ)
        sdf.to_csv(OUT / f"separability_{scheme}.csv", index=False)
        rank_tables[scheme] = sdf
    pairs = pd.DataFrame(pair_rows)
    pairs.to_csv(OUT / "separability_pairs.csv", index=False)

    # ---- ordinality: stage steps in port-noise units (all four stages) ----------------
    order = [c for c in ["Normal", "MCI", "Mild", "Moderate", "Severe"] if c in ds.classes]
    ordl = []
    for m in metrics:
        mu = np.array([np.mean([clean[i][m.name].mean() for i in range(n_sims)
                                if ds.classes[i] == c]) for c in order])
        pa = [clean[i][m.name] for i in range(n_sims)]
        sd = np.sqrt(np.mean([np.var(p, ddof=1) for p in pa])) if pa[0].size > 1 else np.nan
        d = np.diff(mu)
        ordl.append({"metric": m.name, "monotone": bool(np.all(d > 0) or np.all(d < 0)),
                     **{f"{a}->{b} / port": d[k] / sd for k, (a, b) in enumerate(zip(order, order[1:]))}})
    ordinality = pd.DataFrame(ordl)
    ordinality.to_csv(OUT / "ordinality.csv", index=False)

    # ---- M0 decomposition: the same score with all couplings zeroed -------------------
    m0 = [mby["M0.old_score"]]
    diag_only = np.zeros_like(S)
    idn = np.arange(S.shape[-1])
    diag_only[..., idn, idn] = S[..., idn, idn]
    m0_full = [compute(m0, bands, f, S[s], ref)["M0.old_score"].mean() for s in range(n_sims)]
    m0_refl = [compute(m0, bands, f, diag_only[s], ref)["M0.old_score"].mean() for s in range(n_sims)]
    m0_dec = pd.DataFrame({"stage": ds.classes, "M0": m0_full, "M0_couplings_zeroed": m0_refl})

    report(cfg, ds, gh, sim_set, metrics, rank_tables, pairs, rob, schemes, ordinality, m0_dec)
    figures(cfg, ds, f, S, clean, noisy, spec_q, metrics, bands, rank_tables, rob, schemes)
    print((OUT / "report.md").read_text(encoding="utf-8")[:6000])


# ======================================================================== report
def report(cfg, ds, gh, sim_set, metrics, rank_tables, pairs, rob, schemes, ordinality, m0_dec):
    prof = cfg["metrics"]["ranking_profile"]
    L = [f"# Prompt 02 - metric separability (track A, code {gh}, sim_set {sim_set})", "",
         "J_meas = min pairwise Fisher ratio from noisy realisations (ranking key). "
         "J_eff adds the port-to-port asymmetry as extra variance. gap/port = class gap / "
         "port-to-port std. gap/mesh = pending (mesh-repeat not yet available). "
         "shift_move = largest change under ±2/5/10 MHz resonance shifts / smallest class gap. "
         "band_gap_retention = worst (gap after ±10 % band change) / (original gap); < 0 means "
         "the class order flips. freq_robust (brief's literal criterion) = shift AND band value "
         "changes < 0.25 × smallest gap. " + MESH_NOTE + ".", ""]
    if ds.masking and len(ds.masked_log):
        ml = ds.masked_log
        inb = ml[ml["in_common_band"]]
        L += [f"Glitch masking ON: {len(inb)} in-band (f, pair) points masked in "
              f"{inb.groupby(['file', 'port_i', 'port_j', 'run_start_GHz']).ngroups} runs "
              "(results/qc/masked_points.csv).", ""]
    cols = ["metric", "min_J_meas", "weakest_pair", "min_J_eff", "min_gap_over_port",
            "max_bayes_err", "shift_move_over_min_gap", "band_gap_retention", "freq_robust"]
    for scheme in schemes:
        t = rank_tables[scheme]
        t = t[t.profile == prof].sort_values("min_J_meas", ascending=False).reset_index(drop=True)
        t.insert(0, "rank", np.arange(1, len(t) + 1))
        keep = t.head(15)
        extra = t[t.metric.isin(["M0.old_score", "M1.Sii_dBavg", "M2.R", "M5.C3[k3]"])
                  & ~t.metric.isin(keep.metric)]
        L += [f"## Ranking - scheme `{scheme}` ({scheme_label(cfg, scheme)}), profile `{prof}`",
              md(pd.concat([keep, extra])[["rank"] + cols]), ""]
        te = t.dropna(subset=["min_J_eff"]).sort_values("min_J_eff", ascending=False).head(10)
        L += [f"Top 10 by J_eff (port asymmetry included), scheme `{scheme}`:",
              md(te[["rank"] + cols]), ""]

    # power vs dB
    comp = [("M1.Sii_dBavg", "M2.R"), ("M3.ML_dBavg", "M3.ML_of_powavg"),
            ("M5.C3_dBavg[k3]", "M5.C3[k3]")]
    rows = []
    for scheme in schemes:
        t = rank_tables[scheme]
        for dbm, pwm in comp:
            for p in PROFILES:
                a = t[(t.metric == dbm) & (t.profile == p)].iloc[0]
                b = t[(t.metric == pwm) & (t.profile == p)].iloc[0]
                rows.append({"scheme": scheme, "pair": f"{dbm} vs {pwm}", "profile": p,
                             "J_dB": a.min_J_meas, "J_pow": b.min_J_meas,
                             "ratio_pow/dB": b.min_J_meas / a.min_J_meas,
                             "shift_move_dB": a.shift_move_over_min_gap,
                             "shift_move_pow": b.shift_move_over_min_gap})
    comp_df = pd.DataFrame(rows)
    comp_df.to_csv(OUT / "power_vs_db.csv", index=False)
    L += ["## Power averaging vs dB averaging (min pairwise J_meas)",
          md(comp_df[comp_df.profile.isin(["good", "typical", "very_noisy", "typical_jitter"])]), ""]

    # robustness summary for selected metrics
    sel = ["M0.old_score", "M1.Sii_dBavg", "M2.R", "M3.ML_of_powavg", "M4.N", "M5.C", "M5.C3",
           "M5.C3[k3]", "M6.fc_A", "M6.spread_A", "M7.D", "M7.D_pow", "M7.D3[k3]",
           "M8.s1^2", "M8.lam0^2", "M8.lam0^2[k3]", "M8.lam3^2[k3]"]
    pv = rob[rob.metric.isin(sel)].pivot(index="metric", columns="perturbation",
                                         values="ratio_to_gap_N_Mi").reindex(sel)
    ptypes = ["shift-2", "shift+10", "shift-20", "band_shrink10", "band_lo10", "band_3.4-3.9",
              "band_3.2-3.5_nodip", "flatten_notch", "detune+200", "one_open"]
    L += ["## Robustness: |Δ metric| / |Normal - Mild gap| (selected)",
          md(pv[ptypes].reset_index(), ".2g"), ""]
    fl = rob[rob.perturbation.isin(["open_all", "short_all", "one_open"]) & rob.metric.isin(sel)]
    fl = fl.pivot(index="metric", columns="perturbation",
                  values="lands_in_class_range").reindex(sel)
    fin = rob[rob.perturbation.isin(["open_all", "short_all"]) & rob.metric.isin(sel)].pivot(
        index="metric", columns="perturbation", values="finite").reindex(sel)
    fl.columns = [f"{c}: in class range" for c in fl.columns]
    fin.columns = [f"{c}: finite" for c in fin.columns]
    L += ["## Faults (open / short all antennas, one antenna open)",
          md(pd.concat([fin, fl], axis=1).reset_index()), ""]
    sel_o = ["M0.old_score", "M2.R", "M5.C", "M5.C3", "M5.C3[k3]", "M6.A[3.40]", "M6.A[3.45]",
             "M7.D3", "M7.D3[k3]", "M8.lam0^2[k3]", "M8.lam3^2[k3]"]
    L += ["## Ordinality: stage-to-stage steps in port-noise units (noise-free, all 4 stages)",
          f"{int(ordinality.monotone.sum())} of {len(ordinality)} metrics are monotone over "
          "Normal < Mild < Moderate < Severe. Normal->Mild and Moderate->Severe cross HFSS "
          "projects; Mild->Moderate does not (see summary caveat).",
          md(ordinality.set_index("metric").loc[sel_o].reset_index(), ".2g"), "",
          "## M0 decomposition (couplings zeroed)",
          "M0 = mean_B Σ_(j≠i)|S_ii + S_ij| / VSWR_i. With every S_ij set to 0 the score is "
          "almost unchanged, i.e. M0 is in practice (N-1)·<|Γ|/VSWR>: a reflection-only "
          "quantity with an arbitrary weighting.", md(m0_dec, ".5g"), ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")


# ======================================================================== figures
def figures(cfg, ds, f, S, clean, noisy, spec_q, metrics, bands, rank_tables, rob, schemes):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.color": "#e4e3de", "grid.linewidth": 0.5,
                         "axes.edgecolor": "#8a8981", "axes.labelcolor": "#3d3d3a",
                         "xtick.color": "#5f5e59", "ytick.color": "#5f5e59",
                         "axes.titlesize": 8.5, "axes.titlelocation": "left"})
    seq = LinearSegmentedColormap.from_list("blue", ["#f7fafe", "#cde2fb", "#86b6ef", "#3987e5",
                                                     "#1c5cab", "#0d366b"])
    order = [c for c in ["Normal", "MCI", "Mild", "Moderate", "Severe"] if c in ds.classes]
    idx = {c: ds.classes.index(c) for c in order}
    fg = f / 1e9
    k3 = [v / 1e9 for v in bands["k3"]]

    # 1. spectra
    qs = [("R", "Reflected R=|Sii|²"), ("A", "Accepted A=1-R"), ("N", "Not returned N"),
          ("C", "Coupled C=Σ|Sji|²"), ("C3", "Opposite |S(i+3,i)|²")]
    fig, ax = plt.subplots(2, 5, figsize=(15, 6), sharex=True)
    for j, (k, title) in enumerate(qs):
        for c in order:
            s = idx[c]
            y = power_spectra(S[s])[k].mean(-1)
            lo, hi = spec_q[s][k]
            for row, tf in ((0, lambda x: x), (1, lambda x: 10 * np.log10(np.maximum(x, 1e-12)))):
                a = ax[row, j]
                a.fill_between(fg, tf(lo), tf(hi), color=STAGE_COLOR[c], alpha=0.2, lw=0)
                a.plot(fg, tf(y), color=STAGE_COLOR[c], lw=1.6, label=c)
        ax[0, j].set_title(title)
        for row in (0, 1):
            if k == "C3":
                ax[row, j].axvspan(*k3, color="#f0efec", zorder=0)
        ax[1, j].set_xlabel("Frequency (GHz)")
    ax[0, 0].set_ylabel("linear power")
    ax[1, 0].set_ylabel("dB")
    ax[0, 0].legend(frameon=False)
    fig.suptitle("Ring-mean power spectra per stage; band = 5-95 % under 'typical' noise; "
                 "grey = k3 window", x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(FIG / "02_spectra.png", dpi=140)
    plt.close(fig)

    # 2. violins (non-sub-band scalars) under typical noise
    ms = [m for m in metrics if not m.band.startswith("sb")]
    ncol = 8
    nrow = int(np.ceil(len(ms) / ncol))
    fig, ax = plt.subplots(nrow, ncol, figsize=(2.1 * ncol, 1.75 * nrow))
    for a, m in zip(ax.flat, ms):
        for x, c in enumerate(order):
            v = noisy["typical"][idx[c]][m.name]
            parts = a.violinplot(v, positions=[x], widths=0.8, showextrema=False)
            for b in parts["bodies"]:
                b.set_facecolor(STAGE_COLOR[c])
                b.set_alpha(0.75)
            pa = clean[idx[c]][m.name]
            if pa.size > 1:
                a.plot(np.full(pa.size, x + 0.42), pa, ".", ms=2.5, color="#5f5e59")
        a.set_title(m.name, fontsize=7)
        a.set_xticks(range(len(order)), [c[:3] for c in order], fontsize=6)
        a.tick_params(axis="y", labelsize=5.5)
        a.yaxis.get_offset_text().set_fontsize(5.5)
    for a in ax.flat[len(ms):]:
        a.axis("off")
    fig.suptitle("Scalar metrics per stage under 'typical' noise (violin = ring mean over 500 "
                 "realisations; grey dots = noise-free per-antenna values = port noise)",
                 x=0.01, ha="left", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "02_violins_typical.png", dpi=130)
    plt.close(fig)

    # 3. heatmap metric x profile -> log10 min pairwise J_meas, per scheme
    names = [m.name for m in metrics]
    profs = list(PROFILES)
    fig, ax = plt.subplots(1, len(schemes), figsize=(3.3 * len(schemes) + 1, 15), sharey=True)
    ax = np.atleast_1d(ax)
    for a, scheme in zip(ax, schemes):
        t = rank_tables[scheme]
        Z = t.pivot(index="metric", columns="profile", values="min_J_meas").reindex(index=names, columns=profs)
        G = t.pivot(index="metric", columns="profile", values="min_gap_over_port").reindex(index=names, columns=profs)
        im = a.imshow(np.log10(Z.values), aspect="auto", cmap=seq, vmin=-2, vmax=3)
        yy, xx = np.where(G.values < 1)
        a.plot(xx, yy, "x", ms=3, color="#eb6834", mew=0.8)
        a.set_xticks(range(len(profs)), profs, rotation=45, ha="right")
        a.set_yticks(range(len(names)), names, fontsize=5.5)
        a.set_title(scheme)
        a.grid(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.4, pad=0.01)
    cb.set_label("log10 min pairwise Fisher J_meas")
    fig.suptitle("Min pairwise Fisher ratio per metric and noise profile (× = weakest gap "
                 "< port-to-port noise)", x=0.01, ha="left")
    fig.savefig(FIG / "02_fisher_heatmap.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # 4. robustness heatmap
    ptypes = [p for p in rob.perturbation.unique() if p not in ("open_all", "short_all")]
    Z = rob.pivot(index="metric", columns="perturbation", values="ratio_to_gap_N_Mi").reindex(
        index=names, columns=ptypes)
    fig, a = plt.subplots(figsize=(10, 15))
    im = a.imshow(np.log10(Z.values), aspect="auto", cmap=seq, vmin=-3, vmax=2)
    yy, xx = np.where(Z.values >= 0.25)
    a.plot(xx, yy, "x", ms=3, color="#eb6834", mew=0.8)
    a.set_xticks(range(len(ptypes)), ptypes, rotation=60, ha="right")
    a.set_yticks(range(len(names)), names, fontsize=5.5)
    a.grid(False)
    cb = fig.colorbar(im, ax=a, shrink=0.4, pad=0.01)
    cb.set_label("log10 |Δ metric| / |Normal - Mild gap|")
    a.set_title("Metric change under perturbation, in Normal-Mild gap units (× = ≥ 0.25 gap; "
                "blank = not applicable)")
    fig.savefig(FIG / "02_robustness_heatmap.png", dpi=130, bbox_inches="tight")
    plt.close(fig)

    # 5. sub-band view: where in frequency does the information sit?
    sbs = [b for b in bands if b.startswith("sb")]
    xc = np.array([np.mean(bands[b]) / 1e9 for b in sbs])
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
    for c in order:
        s = idx[c]
        y = [noisy["typical"][s][f"M6.A[{b[2:]}]"] for b in sbs]
        ax[0].errorbar(xc, [v.mean() for v in y], yerr=[v.std() for v in y], color=STAGE_COLOR[c],
                       lw=1.6, capsize=0, label=c)
    ax[0].set_title("Accepted power ⟨A⟩ per 50 MHz sub-band (typical noise ±1σ)")
    ax[0].set_xlabel("Sub-band centre (GHz)")
    ax[0].legend(frameon=False)
    for scheme, ls in zip(schemes, ["-", "--", ":", "-."]):
        t = rank_tables[scheme]
        t = t[t.profile == "typical"].set_index("metric")
        ax[1].semilogy(xc, [t.loc[f"M6.A[{b[2:]}]", "min_J_meas"] for b in sbs], ls, color="#2a78d6",
                       lw=1.6, label=scheme)
    ax[1].axhline(1, color="#8a8981", lw=0.8)
    ax[1].set_title("Min pairwise Fisher of sub-band ⟨A⟩ (typical)")
    ax[1].set_xlabel("Sub-band centre (GHz)")
    ax[1].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "02_subbands.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
