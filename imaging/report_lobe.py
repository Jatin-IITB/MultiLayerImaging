"""Lobe study report: lobe_report.md, lobe_predictions.md, figures/lobe_*.png, blind-test scoring."""
from __future__ import annotations

import json
import pickle
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Wedge  # noqa: E402

from . import study_lobe as SL  # noqa: E402
from .common import FIG, OUT, ROOT, git_hash  # noqa: E402

STAGES = ("Mild_lobe", "Moderate_lobe", "Severe_lobe")
PRIMARY = "tikhonov dS"
SECOND = "tikhonov log (gain-inv.)"
SHORT = ["S1 Fr", "S2 TL", "S3 PL", "S4 Oc", "S5 PR", "S6 TR"]


def _t(rows, cols, fmt=None):
    fmt = fmt or {}
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, (float, np.floating)):
                v = format(v, fmt.get(c, ".3g")) if np.isfinite(v) else "n/a"
            cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


# ----------------------------------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------------------------------
def _lobe_ax(ax, vals, vmin, vmax, cmap, title, mark=None):
    cm = plt.get_cmap(cmap)
    for k in range(6):
        a0 = -120 + 60 * k
        v = (vals[k] - vmin) / (vmax - vmin) if vmax > vmin else 0.5
        ax.add_patch(Wedge((0, 0), 1.0, a0, a0 + 60, width=0.45, facecolor=cm(np.clip(v, 0, 1)),
                           edgecolor="0.5", lw=0.5))
        if mark is not None and mark[k]:
            ax.add_patch(Wedge((0, 0), 1.07, a0 + 2, a0 + 58, width=0.05, facecolor="tab:blue", edgecolor="none"))
        c = np.deg2rad(a0 + 30)
        ax.text(0.77 * np.cos(c), 0.77 * np.sin(c), f"{SHORT[k]}\n{vals[k]:.1f}", ha="center", va="center", fontsize=6.5)
    ax.text(0, -1.17, "front (nose, T1)", ha="center", fontsize=6)
    ax.text(0, 1.1, "back (T4)", ha="center", fontsize=6)
    ax.text(1.12, 0, "subject's\nleft", ha="left", va="center", fontsize=6)
    ax.text(-1.12, 0, "subject's\nright", ha="right", va="center", fontsize=6)
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8)


def fig_maps(res):
    cols = ["truth", PRIMARY, "bounded dS", SECOND]
    fig, ax = plt.subplots(len(STAGES), len(cols), figsize=(4.0 * len(cols), 3.4 * len(STAGES)))
    vmax = max(max(res["truth"][d]["sens"][7:13].max() for d in STAGES),
               max(res["fits"][m][d][6:12].max() for m in cols[1:] for d in STAGES))
    for i, d in enumerate(STAGES):
        aff = np.array(SL.DESIGNS[d][0]) > 0
        for j, c in enumerate(cols):
            if c == "truth":
                v = res["truth"][d]["sens"][7:13]
                ttl = (f"{d}: TRUE conductivity change\n(blue arc = affected; e = "
                       f"{'/'.join(str(x) for x in SL.DESIGNS[d][0])} mm)")
                mark = aff
            else:
                v = res["fits"][c][d][6:12]
                calls = next(s for s in res["scores"] if s["method"] == c and s["stage"] == d)["called"].split()
                mark = np.array([f"S{k + 1}" in calls for k in range(6)])
                ttl = f"{d}: recovered dε'' — {c}\n(blue arc = called affected, frozen rule R1)"
            _lobe_ax(ax[i, j], v, 0, vmax, "Reds", ttl, mark)
    fig.suptitle("Lobe maps: conductivity increase per sector (dε'' = dσ/(ωε0) at 3.6 GHz). "
                 "Seen from above, nose at the bottom.", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "lobe_maps.png", dpi=110)
    plt.close(fig)


def fig_kernels(res):
    K = res["kernel_abs_36"]
    labels = [SL.pair_label(a, b) for a, b in SL.PAIRS]
    fig, ax = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw=dict(width_ratios=[1.3, 1]))
    im = ax[0].imshow(20 * np.log10(np.maximum(K, 1e-6)), aspect="auto", cmap="viridis", vmin=-60, vmax=0)
    ax[0].set_yticks(range(len(labels)))
    ax[0].set_yticklabels(labels, fontsize=7)
    ax[0].set_xticks(range(len(res["region_names"])))
    ax[0].set_xticklabels([n.replace(" ", "\n", 1) for n in res["region_names"]], fontsize=7)
    fig.colorbar(im, ax=ax[0], label="|kernel| (dB rel. max), 3.6 GHz")
    ax[0].set_title("Born sensitivity of each antenna pair to a unit dε in each region\n"
                    "(outer cortex 70–83.5 mm per lobe sector; core r < 25 mm)", fontsize=9)
    for key, lab in (("sv_dS7", "6 sectors + core, dS"), ("sv_dS", "6 sectors, dS"),
                     ("sv_log", "6 sectors, gain-invariant log"), ("sv_dS_split", "12 (gap/deep), dS")):
        s = res[key]
        ax[1].semilogy(np.arange(1, len(s) + 1), s / s[0], "o-", label=lab)
    ax[1].set_xlabel("singular value index")
    ax[1].set_ylabel("singular value (rel. largest)")
    ax[1].set_title("Singular values of the noise-whitened kernel matrix\n(3 freqs × 21 pairs × Re/Im)", fontsize=9)
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "lobe_kernels.png", dpi=110)
    plt.close(fig)


def fig_radar(res):
    rad = res["radar"]
    mask, u = rad["mask"], rad["u"]
    z = 48.0
    fig, ax = plt.subplots(2, 3, figsize=(13, 8.5))
    for j, d in enumerate(STAGES):
        aff = np.array(SL.DESIGNS[d][0]) > 0
        for i, m in enumerate(("DAS", "DMAS")):
            img = np.full(mask.shape, np.nan)
            img[mask] = rad[d][m]
            a = ax[i, j]
            h = a.imshow(10 * np.log10(img / np.nanmax(img)), origin="lower", extent=[u[0], u[-1], u[0], u[-1]],
                         vmin=-10, vmax=0, cmap="magma")
            rr = np.sqrt(83.5 ** 2 - z ** 2)
            for k in range(6):
                a0 = np.deg2rad(-120 + 60 * k)
                a.plot([0, 90 * np.cos(a0)], [0, 90 * np.sin(a0)], color="w", lw=0.4)
                c = np.deg2rad(-90 + 60 * k)
                a.text(80 * np.cos(c), 80 * np.sin(c), SHORT[k], color="tab:blue" if aff[k] else "0.3", fontsize=7,
                       ha="center", va="center")
            t = np.linspace(0, 2 * np.pi, 200)
            a.plot(rr * np.cos(t), rr * np.sin(t), "c", lw=0.5)
            st = next(s for s in res["radar_stats"] if s["stage"] == d and s["method"] == m)
            a.plot(st["peak_r_mm"] * np.cos(np.deg2rad(st["peak_az_deg"])),
                   st["peak_r_mm"] * np.sin(np.deg2rad(st["peak_az_deg"])), "g+", ms=12, mew=2)
            a.set_title(f"{d} {m}\npeak (r ≥ 40 mm, green +) at {st['peak_az_deg']:.0f}°; "
                        f"affected-lobe centroid {st['true_dir_deg']:.0f}°", fontsize=8)
            a.set_xlabel("x (mm, + = subject's left)")
            a.set_ylabel("y (mm, − = front)")
    fig.colorbar(h, ax=ax, shrink=0.6, label="dB rel. max")
    fig.suptitle("Radar images of dS (stage − Healthy_sliced), ring plane z = +48 mm; blue labels = affected lobes")
    fig.savefig(FIG / "lobe_radar.png", dpi=110)
    plt.close(fig)


def fig_null(res):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    for j, m in enumerate((PRIMARY, SECOND)):
        allx = np.concatenate(list(res["null_x"][m].values()))
        lr = [0.5 * (x[7] + x[8]) - 0.5 * (x[10] + x[11]) for x in allx]
        ax[j].hist(lr, bins=30, color="0.6", label="null inputs (noise only)")
        for d in STAGES:
            c = 0.5 * (res["fits"][m][d][7] + res["fits"][m][d][8]) - 0.5 * (res["fits"][m][d][10] + res["fits"][m][d][11])
            ax[j].axvline(c, label=f"{d} (mirror-symmetric)", lw=1)
        bp = res["blind_pred"]["LeftOnly_test"][m]
        ax[j].axvspan(bp["LR_mean"] - 2 * bp["LR_sd"], bp["LR_mean"] + 2 * bp["LR_sd"], color="g", alpha=0.25,
                      label="LeftOnly predicted (±2 sd)")
        T = res["rules"][m]["T_LR"]
        ax[j].axvline(T, color="r", ls="--", label="frozen threshold ±T_LR")
        ax[j].axvline(-T, color="r", ls="--")
        ax[j].set_xlabel("left−right contrast of recovered dε'' (left lobes − right lobes)")
        ax[j].set_title(m, fontsize=9)
        ax[j].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "lobe_null_lr.png", dpi=120)
    plt.close(fig)


# ----------------------------------------------------------------------------------------------
def write_stage1(res):
    FIG.mkdir(parents=True, exist_ok=True)
    fig_maps(res)
    fig_kernels(res)
    fig_radar(res)
    fig_null(res)
    names = res["region_names"]
    L = [f"# Lobe-sector phantom (set lobe_v1): sector-level localisation and imaging (code {res['code']}, {date.today()})", "",
         "Regenerate: `python imaging/run_lobe.py` (blind stage: `python imaging/run_lobe.py --blind`, only after "
         "`lobe_predictions.md` is committed). This section is new; the v1/v2 imaging results in `report.md` are unchanged.", "",
         "## 0. Data, background, scope", "",
         "- Designs (project `new_with_slices`, one solve each, 3.2–4.2 GHz, 201 points, glitch masking ON): "
         + ", ".join(f"`{d}`" for d in SL.AVAILABLE) + ". Every difference is dS = S(stage) − S(Healthy_sliced) "
         "(same project, setup and mesh recipe). LeftOnly_test and MCI_lobe are the blind set (§6).",
         "- **Background fields.** The Born kernels use the HFSS field exports of the *unsliced* v2 Normal design "
         "(`data/fields`, 3.4/3.6/3.8 GHz). At e = 0 the sliced head is the same head geometrically, except that "
         "its skull inner surface was set explicitly to 83.5 mm and its mesh differs; the kernels are therefore an "
         "approximation of the sliced background.",
         "- **One simulation per design and one head.** Everything below is within-simulation capability under the "
         "stated noise, not generalisation to other heads or setups.",
         f"- **Calibration.** κ(f) is fitted on Mild only and frozen: |κ| = "
         + ", ".join(f"{abs(k):.2f}" for k in res["kappa"]) + " at 3.4/3.6/3.8 GHz. With κ the linear model reproduces "
         + ", ".join(f"{d.split('_')[0]} {v['corr']:.2f}" for d, v in res["lin"].items())
         + " (shape correlation with HFSS dS) but with relative errors "
         + ", ".join(f"{v['rel_err_kappa']:.2f}" for v in res["lin"].values())
         + "; the absolute Born prediction is " + ", ".join(f"{v['born_abs_over_hfss']:.2f}" for v in res["lin"].values())
         + " of the HFSS dS size. The AD changes are far from Born-small.",
         "- **Which quantity marks an affected lobe.** The brief assumed AD only lowers ε. That is true for "
         "conductivity-weighted loss but **not for εr at Mild and Moderate**: their CSF permittivity (55.25, "
         "48.75) is higher than or equal to healthy gray matter (47.7), so the true sensitivity-weighted dεr of an "
         "affected sector is " + ", ".join(f"{d.split('_')[0]} {np.mean(res['truth'][d]['sens'][:6][np.array(SL.DESIGNS[d][0]) > 0]):+.1f}"
                                         for d in STAGES)
         + ". What rises in every affected sector is the conductivity: dε'' = dσ/(ωε0) = "
         + ", ".join(f"{d.split('_')[0]} {np.mean(res['truth'][d]['sens'][7:13][np.array(SL.DESIGNS[d][0]) > 0]):+.1f}"
                     for d in STAGES)
         + " in affected sectors vs ≤ " + f"{max(res['truth'][d]['sens'][7:13][np.array(SL.DESIGNS[d][0]) == 0].max() for d in STAGES[:2]):.1f}"
         + " in healthy ones. The sector calls therefore use dε''; the bounded fit constrains dε'' ≥ 0 only.", ""]

    # ---- 1. kernels
    K = res["kernel_abs_36"]
    rows = []
    for i, (a, b) in enumerate(SL.PAIRS):
        rows.append(dict(pair=SL.pair_label(a, b), **{n.split(" ")[0]: K[i, j] for j, n in enumerate(names)}))
    cos = res["col_cos"]
    s7, s6 = res["sv_dS7"], res["sv_dS"]
    L += ["## 1. Sector sensitivity kernels (3.1)", "",
          "Born sensitivity of each reciprocal antenna pair to a unit complex dε uniform in each region: the six "
          "outer-cortex sector shells (r 70–83.5 mm inside each 60° wedge, full height) and the core (r < 25 mm). "
          "|K| at 3.6 GHz, normalised to the largest entry:", "",
          _t(rows, ["pair"] + [n.split(" ")[0] for n in names], {n.split(" ")[0]: ".2g" for n in names}), "",
          "Singular values of the noise-whitened kernel matrix (21 pairs × 3 frequencies × Re/Im; unknowns dεr and "
          "dε'' per region), relative to the largest:", "",
          f"- 6 sectors + core: {', '.join(f'{v:.3f}' for v in s7 / s7[0])} → condition number {s7[0] / s7[-1]:.0f}. "
          "The two smallest belong to the core.",
          f"- 6 sectors only: condition number {s6[0] / s6[-1]:.1f} (gain-invariant log data "
          f"{res['sv_log'][0] / res['sv_log'][-1]:.1f}); 12 regions with the gap/deep split: "
          f"{res['sv_dS_split'][0] / res['sv_dS_split'][-1]:.0f}.", "",
          "Similarity of the region kernels (cosine between whitened dεr columns; 1 = indistinguishable):", "",
          _t([dict(region=n, **{names[j].split(" ")[0]: cos[i, j] for j in range(len(names))}) for i, n in enumerate(names)],
             ["region"] + [n.split(" ")[0] for n in names], {n.split(" ")[0]: ".2f" for n in names}), "",
          f"- **All six sectors are distinguishable** with 6 antennas on one ring: no two sector kernels are collinear "
          f"(largest cosine {np.max(cos[:6, :6] - np.eye(6)):.2f}, between neighbouring sectors). The mirror pairs "
          f"S2/S6 ({cos[1, 5]:.2f}) and S3/S5 ({cos[2, 4]:.2f}) are nearly orthogonal in pair space: each is seen by "
          "a different set of antenna pairs (its own ring position), which is what allows a left/right call.",
          f"- **The core is not**: its kernel is tiny (singular values {s7[-2] / s7[0]:.3f}, {s7[-1] / s7[0]:.3f} of the "
          "largest) — the hippocampus is invisible, as in v2.", "",
          "Figure: `figures/lobe_kernels.png`.", ""]

    # ---- 2. CRLB
    tr = res["truth"]
    rows = []
    for v, lab in ((0, "dεr"), (1, "dε''")):
        for k, n in enumerate(names):
            r_ = dict(quantity=lab, region=n)
            for key, c7 in res["crlb7"].items():
                r_[key] = c7[k + v * len(names)]
            for d in STAGES:
                r_[f"true {d.split('_')[0]}"] = tr[d]["sens"][k + v * len(names)]
            rows.append(r_)
    det = []
    for d in STAGES:
        c6 = res["crlb"]["log, gain-invariant"]
        cd = res["crlb"]["dS (no gain error)"]
        aff = np.array(SL.DESIGNS[d][0]) > 0
        true_pp = tr[d]["sens"][7:13]
        det.append(dict(stage=d, affected=" ".join(f"S{k + 1}" for k in np.flatnonzero(aff)),
                        determined_dS=" ".join(f"S{k + 1}" for k in range(6) if aff[k] and cd[6 + k] < 0.5 * abs(true_pp[k])) or "none",
                        determined_gain_inv=" ".join(f"S{k + 1}" for k in range(6) if aff[k] and c6[6 + k] < 0.5 * abs(true_pp[k])) or "none",
                        core_crlb_over_change=res["crlb7"]["dS (no gain error)"][13] / max(abs(tr[d]["sens"][13]), 1e-9)))
    ts = res["truth_split"]
    sn = res["split_names"]
    rows_s = []
    for k, n in enumerate(sn):
        r_ = dict(region=n, crlb_dS=res["crlb_split"]["dS (no gain error)"][12 + k],
                  crlb_gain_inv=res["crlb_split"]["log, gain-invariant"][12 + k])
        for d in STAGES:
            r_[f"true {d.split('_')[0]}"] = ts[d]["sens"][12 + k]
        rows_s.append(r_)
    gd_cos = [res["col_cos_split"][2 * k, 2 * k + 1] for k in range(6)]
    det_s = []
    for d in STAGES:
        r_ = dict(stage=d)
        for key, lab in (("dS (no gain error)", "dS"), ("log, gain-invariant", "gain-inv")):
            cr = res["crlb_split"][key][12:]
            tv = ts[d]["sens"][12:]
            ok = [n for i, n in enumerate(sn) if abs(tv[i]) > 1 and cr[i] < 0.5 * abs(tv[i])]
            r_[f"gap determined ({lab})"] = " ".join(n.split(" ")[0] for n in ok if n.endswith("gap")) or "none"
            r_[f"deep determined ({lab})"] = " ".join(n.split(" ")[0] for n in ok if n.endswith("deep")) or "none"
        det_s.append(r_)
    L += ["## 2. Identifiability before any fit (CRLB, 3.2)", "",
          "Typical noise on both measurements (0.25 dB, 2°, −70 dB floor), κ frozen. Three variants: no gain error; "
          "±0.5 dB per-port amplitude gain (6 nuisance parameters, constant over frequency, 0.5 dB prior); and "
          "gain-invariant data (complex log-ratios projected onto the complement of all per-port, per-frequency "
          "complex gains = cross-ratios). Columns 'true': sensitivity-weighted mean true change of the region.", "",
          _t(rows, ["quantity", "region"] + list(res["crlb7"]) + [f"true {d.split('_')[0]}" for d in STAGES],
             {**{k: ".2g" for k in res["crlb7"]}, **{f"true {d.split('_')[0]}": "+.1f" for d in STAGES}}), "",
          "Affected sectors determined (CRLB of dε'' < half the true change), 6-sector model:", "",
          _t(det, ["stage", "affected", "determined_dS", "determined_gain_inv", "core_crlb_over_change"],
             {"core_crlb_over_change": ".1f"}), "",
          f"- Sector conductivity is determined in every affected sector, with or without per-port gain errors "
          f"(the ±0.5 dB gain prior raises the CRLB by "
          f"{np.max(res['crlb']['dS + 0.5 dB port gains'] / res['crlb']['dS (no gain error)'] - 1):.0%} at most; "
          f"the fully gain-invariant data by {np.max(res['crlb']['log, gain-invariant'] / res['crlb']['dS (no gain error)'] - 1):.0%}).",
          "- The core is not determined: its CRLB is many times its change.", "",
          "**Depth.** Each sector split into an under-skull gap (76–83.5 mm) and a deeper part (60–76 mm), dε'':", "",
          _t(rows_s, ["region", "crlb_dS", "crlb_gain_inv"] + [f"true {d.split('_')[0]}" for d in STAGES],
             {"crlb_dS": ".1f", "crlb_gain_inv": ".1f", **{f"true {d.split('_')[0]}": "+.1f" for d in STAGES}}), "",
          "Determined (CRLB < half the true change) in the 12-region model:", "",
          _t(det_s, list(det_s[0])), "",
          f"- Gap and deep kernels of one sector are not collinear (cosine {min(gd_cos):.2f}…{max(gd_cos):.2f}), but "
          f"the deep CRLB ({np.min(res['crlb_split']['dS (no gain error)'][12:][1::2]):.0f}–"
          f"{np.max(res['crlb_split']['dS (no gain error)'][12:][1::2]):.0f}) is 2–3× the gap CRLB "
          f"({np.min(res['crlb_split']['dS (no gain error)'][12:][0::2]):.1f}–"
          f"{np.max(res['crlb_split']['dS (no gain error)'][12:][0::2]):.1f}). By the brief's criterion the deeper "
          "cortex (60–76 mm) is not determined in any sector at any stage; the under-skull gap is determined "
          "only where listed. The ring sees the outermost ~8 mm of cortex; depth beyond that is not resolved.", ""]

    # ---- 3. inversion
    rows = []
    for m in res["fits"]:
        for d in STAGES:
            x = res["fits"][m][d]
            rows.append(dict(method=m, stage=d, **{f"dε'' {SHORT[k]}": x[6 + k] for k in range(6)}))
    for d in STAGES:
        rows.append(dict(method="TRUTH (sens.-weighted)", stage=d, **{f"dε'' {SHORT[k]}": tr[d]["sens"][7 + k] for k in range(6)}))
    sc = res["scores"]
    lam = res["lambda"]
    L += ["## 3. Sector inversion (3.3)", "",
          f"Unknowns: dεr and dε'' of the six sector shells (core excluded: §1–2). λ chosen by GCV on Mild only and "
          f"frozen: dS fits {lam['dS']:.3g}, gain-invariant fits {lam['log']:.3g}. Methods: (a) Tikhonov on dS; (b) "
          "bounded (dε'' ≥ 0) on dS; (c) Tikhonov and bounded on gain-invariant log-ratio data (no per-port "
          "calibration needed). Recovered conductivity change per sector:", "",
          _t(rows, ["method", "stage"] + [f"dε'' {s}" for s in SHORT], {f"dε'' {s}": ".1f" for s in SHORT}), "",
          "Scores. corr_e = Pearson correlation of recovered dε'' with the true CSF expansion e_k; corr_truth = with "
          "the true dε''; top-k = fraction of the k truly affected sectors among the k largest recovered values "
          "(undefined for Severe, where all are affected). Calls use the frozen rule R1 (§5); 'null only' uses the "
          "noise-null threshold alone.", "",
          _t(sc, ["method", "stage", "corr_e", "corr_truth", "topk", "called", "called_null_only", "true_set",
                  "correct_calls", "LR", "side", "FB", "frontback"],
             {"corr_e": ".2f", "corr_truth": ".2f", "topk": ".2f", "LR": "+.1f", "FB": "+.1f"}), "",
          "**Front/back (Moderate: frontal S1 affected, occipital S4 healthy):**", "",
          _t(res["front_back"], ["method", "S1", "S4", "crlb_S1", "crlb_S4", "FB", "T_FB", "verdict", "S1_called", "S4_called"],
             {"S1": ".1f", "S4": ".1f", "crlb_S1": ".1f", "crlb_S4": ".1f", "FB": "+.1f", "T_FB": ".1f"}), "",
          "Reading:",
          "- The bounded fits equal the Tikhonov fits on the real designs: the bound dε'' ≥ 0 is never active "
          "(all recovered dε'' are positive). The bound matters only for the null inputs (different T_null, T_FB).",
          "- Severe: every sector is affected with nearly equal true dε'' (20.1–20.3), so corr_truth there "
          "(≈ 0.55) measures noise in a flat map, not localisation.",
          f"- The **pattern** is recovered: corr_truth {min(s['corr_truth'] for s in sc if s['stage'] != 'Severe_lobe'):.2f}–"
          f"{max(s['corr_truth'] for s in sc if s['stage'] != 'Severe_lobe'):.2f} for Mild/Moderate and top-k = "
          f"{min(s['topk'] for s in sc if s['stage'] != 'Severe_lobe'):.2f} in every method: the affected lobes are "
          "always the most changed ones.",
          f"- The **absolute level** is not: healthy sectors come out at dε'' ≈ "
          f"{min(res['fits'][m][d][6 + k] for m in res['fits'] for d in STAGES[:2] for k in range(6) if SL.DESIGNS[d][0][k] == 0):.0f}–"
          f"{max(res['fits'][m][d][6 + k] for m in res['fits'] for d in STAGES[:2] for k in range(6) if SL.DESIGNS[d][0][k] == 0):.0f} "
          "instead of ≈ 0.3 (Born model error and leakage from the neighbouring affected sectors, kernel cosine ≈ 0.4). "
          "A threshold from noise-only inputs therefore calls every sector affected ('called_null_only'); the frozen "
          "rule R1 adds a threshold tuned on Mild, and with it every call on Mild, Moderate and Severe is correct.",
          f"- **Front/back:** Moderate's frontal lobe is recovered at {res['front_back'][0]['S1']:.1f} and the occipital "
          f"at {res['front_back'][0]['S4']:.1f} (CRLB {res['front_back'][0]['crlb_S1']:.1f}); the contrast "
          f"{res['front_back'][0]['FB']:+.1f} exceeds its frozen threshold in every method → **front**. "
          "On Mild (S1, S4 both healthy) and Severe (both affected, frontal expansion 15.5 mm vs occipital "
          "11.5 mm, nearly equal conductivity) the call should be none: "
          + "; ".join(f"{s['method']} Severe {s['frontback']} (FB {s['FB']:+.1f} vs T_FB {res['rules'][s['method']]['T_FB']:.1f})"
                      for s in sc if s["stage"] == "Severe_lobe" and s["frontback"] != "none")
          + (". These are marginal false/ambiguous calls; the threshold was not changed after seeing them."
             if any(s["stage"] == "Severe_lobe" and s["frontback"] != "none" for s in sc) else "; all none."),
          "- dεr is recovered with the wrong sign at Mild/Moderate (corr with the true dεr "
          + ", ".join(f"{s['corr_eps_r_truth']:+.2f}" for s in sc if s["method"] == PRIMARY)
          + " for Mild/Moderate/Severe, primary method): the permittivity part is not usable here.",
          "", "Figure: `figures/lobe_maps.png` (truth beside the recovered maps).", ""]

    # ---- 4. radar
    rs = res["radar_stats"]
    L += ["## 4. Radar imaging of the asymmetric change (3.4)", "",
          "DAS and DMAS of dS (whitened 21 reciprocal pairs, layered straight-ray delays, t_ant = 0.5 ns as tuned on v2 "
          "Mild) on the ring plane. Peak = maximum outside r = 40 mm; mean direction / resultant = circular mean of "
          "the image energy in the annulus 40–80 mm (resultant 0 = isotropic, 1 = all energy at one azimuth). True "
          "centroid = e-weighted mean direction of the affected sectors (S1 front = −90°, S4 back = +90°).", "",
          _t(rs, ["stage", "method", "global_peak_r_mm", "peak_az_deg", "peak_r_mm", "mean_dir_deg", "resultant",
                  "true_dir_deg", "true_resultant"],
             {"global_peak_r_mm": ".0f", "peak_az_deg": ".0f", "peak_r_mm": ".0f", "mean_dir_deg": ".0f",
              "resultant": ".3f", "true_dir_deg": ".0f", "true_resultant": ".2f"}), "",
          f"- The global maximum stays at the centre (r ≈ {np.median([s['global_peak_r_mm'] for s in rs]):.0f} mm) in "
          f"{sum(s['global_peak_r_mm'] < 25 for s in rs)} of {len(rs)} images: the symmetric-ring artefact of v2 persists, because most of each stage's change is still "
          "shared by all sectors (every sector's thin CSF layer and the core change with the stage).",
          f"- The image energy is nearly isotropic (resultant ≤ {max(s['resultant'] for s in rs):.3f}); its direction "
          "does not follow the true centroid consistently (table). The images are speckle-dominated, as the v2 "
          "ring-plane images were (`figures/i1_ring_plane.png`). **Radar imaging does not localise the lobes**; the "
          "regional inversion does.", "", "Figure: `figures/lobe_radar.png`.", ""]

    # ---- 5. nulls and rules
    rules = res["rules"]
    nsrc = {k: len(v) for k, v in res["null_x"][PRIMARY].items()}
    L += ["## 5. Noise floors, null distributions and the frozen calling rules (3.5)", "",
          "Null inputs (dS that contain no lobe change), each passed through the frozen inversion: "
          + "; ".join(f"{k} ({v})" for k, v in nsrc.items())
          + ". 'circulant' = the Healthy_sliced deviation from its own rotational symmetry, mapped through the 6 "
          "rotations × 2 reflections of the ring; 'mirror <stage>' = the part of each mirror-symmetric stage that "
          "is antisymmetric under x → −x (numerical noise), under the same 12 maps; 'measurement' = typical-noise "
          "draws of Healthy_sliced minus Healthy_sliced.", "",
          "Frozen rules (per method):", "",
          "- **R1 sector affected** if dε''_k > T_abs = max(T_null, T_mild). T_null = 95th percentile of the largest "
          "sector value over all null inputs (family-wise 5 %). T_mild = midway between the largest healthy and the "
          "smallest affected sector of Mild (tuned on Mild only).",
          "- **R2 side** = left if LR = mean(S2, S3) − mean(S5, S6) > T_LR, right if LR < −T_LR. T_LR = max(95th "
          "percentile of |LR| over the null inputs, largest |LR| of the three mirror-symmetric designs).",
          "- **R3 front/back** = front if FB = S1 − S4 > T_FB, back if < −T_FB. T_FB = max(95th percentile of |FB| "
          "over the nulls, |FB| of Mild, whose S1 and S4 are both healthy).", "",
          _t([dict(method=m, **v) for m, v in rules.items()],
             ["method", "T_null", "T_mild", "T_abs", "T_LR_null", "LR_sym_max", "T_LR", "T_FB_null", "T_FB"],
             {c: ".2f" for c in ["T_null", "T_mild", "T_abs", "T_LR_null", "LR_sym_max", "T_LR", "T_FB_null", "T_FB"]}), "",
          "Figure: `figures/lobe_null_lr.png` (null distribution of the left−right contrast, the mirror-symmetric "
          "designs, the threshold and the pre-registered LeftOnly prediction).", ""]

    # ---- 7 blind (placeholder) + verdict
    L += ["## 6. Blind test (pre-registered, §4 of the brief)", "",
          "Pipeline frozen in `results/imaging/lobe_frozen.json` and predictions written to "
          "`results/imaging/lobe_predictions.md` before LeftOnly_test or MCI_lobe were opened. Outcome: **pending** "
          "(the two designs are still solving). Run `python imaging/run_lobe.py --blind` when they arrive; this "
          "section will then be replaced by the scored outcome.", ""]
    L += _verdict(res)
    (OUT / "lobe_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    write_predictions(res)


def _verdict(res, blind=None):
    sc = res["scores"]
    fb = res["front_back"][0]
    bp = res["blind_pred"]["LeftOnly_test"][PRIMARY]
    pa = OUT / "lobe_A.json"
    A = json.loads(pa.read_text(encoding="utf-8")).get("summary") if pa.exists() else None
    mp = OUT / "lobe_mesh_yardstick.json"
    mesh = json.loads(mp.read_text(encoding="utf-8")) if (mp.exists() and A is None) else None
    ms = mesh["summary"][0] if mesh else None
    if A:
        va, vn = A["all 21 paths"], A["without opposite paths"]
        cor = [c for v in (va, vn) for m in (PRIMARY, SECOND) for c in v["corr"][m][:2]]
        pat_txt = (f"- **Which lobes (pattern):** yes, as a ranking. On the mesh-matched set lobe_A (§5c) the recovered "
                   f"sector conductivity correlates {min(cor):.2f}–{max(cor):.2f} with the truth for Mild and Moderate "
                   "(all four methods, with and without the opposite paths) and the affected lobes are the most changed. "
                   f"Absolute 'affected' calls depend on a threshold calibrated on Mild and are fragile: a one-pass change "
                   f"of the reference mesh shifts every sector by about 2–3, enough to move sectors near T_abs = "
                   f"{A['T_abs']:.1f} across it (primary, all paths: {', '.join(f'{k}/6' for k in va['correct'][PRIMARY])} "
                   f"correct for Mild/Moderate/Severe; without opposite paths: "
                   f"{', '.join(f'{k}/6' for k in vn['correct'][PRIMARY])}). Healthy lobes are biased upward by about "
                   "5–10, more than a one-pass mesh change; Born model error and leakage are the likely cause.")
        fb_txt = (f"- **Front/back:** yes for Moderate on lobe_A: FB = {va['FB_mod'][PRIMARY]:+.1f} (all paths) / "
                  f"{vn['FB_mod'][PRIMARY]:+.1f} (without opposite paths), primary method, against a one-pass mesh "
                  f"yardstick of |FB| ≤ {max(va['yard_FB'], vn['yard_FB']):.1f}; front is called by every method in both "
                  "path sets. A front-positive bias of about 4 is present in every stage (also Mild and Severe, where S1 "
                  "and S4 are equal in truth); it is not mesh, and the frozen T_FB absorbs it except for the bounded-dS fit.")
        lr_add = (f" One-pass mesh yardstick: |LR| ≤ {max(va['yard_LR'], vn['yard_LR']):.1f}; the mirror-symmetric "
                  f"designs give up to {max(va['max_sym_LR'], vn['max_sym_LR']):.1f} on lobe_A, below the frozen T_LR = "
                  f"{A['T_LR']:.1f}.")
        opp_txt = (f"- **Opposite paths:** they carry {A['info_opp'][0]:.0%}–{A['info_opp'][1]:.0%} of the information "
                   "per sector; removing them shifts sector values by "
                   f"{A['noopp_minus_all'][0]:+.1f} to {A['noopp_minus_all'][1]:+.1f} and flips only near-threshold "
                   "calls. No conclusion depends on them (both versions in §5c).")
        cav_mesh = ("; lobe_A matches the stop rule, not the pass count (reference 6 passes, stages 5), and the "
                    "yardstick is a single extra pass, so mesh error relative to a converged solution is not bounded "
                    "by it (§5c).")
    else:
        pat_txt = (f"- **Which lobes (pattern):** yes, as a ranking. The recovered sector conductivity correlates "
                   f"{min(s['corr_truth'] for s in sc if s['stage'] != 'Severe_lobe'):.2f}–"
                   f"{max(s['corr_truth'] for s in sc if s['stage'] != 'Severe_lobe'):.2f} with the truth and the affected "
                   "lobes are always the most changed. Absolute 'affected' calls need a threshold calibrated on a known "
                   "stage (Mild), because healthy lobes are biased upward by model error, leakage"
                   + (" and the unmatched meshes (a mesh difference alone lifts every sector above the threshold, §5b)."
                      if mesh else "."))
        if mesh:
            fb_txt = (f"- **Front/back:** Moderate's frontal lobe is recovered above its occipital lobe (frontal "
                      f"{fb['S1']:.1f} vs occipital {fb['S4']:.1f}, contrast {fb['FB']:+.1f} > frozen {fb['T_FB']:.1f}), "
                      f"but a mesh difference alone gives |FB| up to {ms['max_abs_FB']:.1f} (§5b). **Not separable "
                      "from mesh** until the designs are re-solved on matched meshes.")
        else:
            fb_txt = (f"- **Front/back:** yes for Moderate (frontal {fb['S1']:.1f} vs occipital {fb['S4']:.1f}, contrast "
                      f"{fb['FB']:+.1f} > {fb['T_FB']:.1f}).")
        lr_add = (f" Mesh yardstick: a mesh difference alone gives |LR| up to {ms['max_abs_LR']:.1f} (threshold "
                  f"{ms['T_LR']:.1f}), so only a left/right contrast well above {ms['max_abs_LR']:.1f} can be attributed "
                  "to the lobes." if mesh else "")
        opp_txt = None
        cav_mesh = "; the healthy reference and the stages are on different meshes (§5b)." if mesh else "."
    L = ["## 7. Verdict — can this 6-antenna ring localise lobe-level AD?", "",
         "Within these simulations (one head, one solve per design, typical noise, Born kernels on the v2 Normal fields):", "",
         pat_txt,
         fb_txt,
         "- **Left/right:** "
         + (f"{blind}" if blind else
            f"not testable on the available designs (all mirror-symmetric). The frozen pipeline predicts LR = "
            f"{bp['LR_mean']:+.1f} ± {bp['LR_sd']:.1f} for LeftOnly_test (left in {bp['p_left']:.0%} of noisy draws); "
            "the blind test decides.")
         + lr_add,
         "- **Depth:** no, beyond the outermost cortex. The under-skull gap (76–83.5 mm) is determined where it "
         "changes; the deeper cortex (60–76 mm) has a 2–3× larger CRLB and is not determined in any sector at any "
         "stage (§2); the core (hippocampus) is not determined at all.",
         "- **Radar imaging:** no — it still peaks at the centre and its energy direction does not track the lobes."]
    if opp_txt:
        L.append(opp_txt)
    L += ["- **Caveats:** the Born model explains only about a quarter to a third of the dS size (κ ≈ 3 absorbs it) and "
          "the background fields come from the unsliced design; the lobe placement is schematic (azimuthal wedges at "
          "the ring height); everything is within one simulated head" + cav_mesh, ""]
    return L


def write_predictions(res):
    fz = res["frozen"]
    bp = res["blind_pred"]
    L = ["# Pre-registered predictions for the blind lobe designs (imaging session)", "",
         f"Written {date.today()} by `imaging/run_lobe.py` at code `{fz['code']}`, **before LeftOnly_test or MCI_lobe "
         "were opened**. The pipeline state is frozen in `results/imaging/lobe_frozen.json` (κ, λ, thresholds). "
         "Do not edit after the blind files arrive.", "",
         "## Frozen pipeline", "",
         f"- κ(f) (fitted on Mild only): " + ", ".join(f"{complex(r, i):.3f}" for r, i in zip(fz["kappa_re"], fz["kappa_im"]))
         + f" at {fz['f_GHz']} GHz. λ (GCV on Mild): dS {fz['lambda_dS']:.4g}, gain-invariant {fz['lambda_log']:.4g}.",
         f"- Primary method: **{PRIMARY}**; secondary (no per-port calibration): **{SECOND}**. Rules R1–R3 as in "
         "`lobe_report.md` §5:", "",
         _t([dict(method=m, **v) for m, v in fz["rules"].items()],
            ["method", "T_abs", "T_LR", "T_FB"], {"T_abs": ".2f", "T_LR": ".2f", "T_FB": ".2f"}), "",
         "## Expected outcomes", "",
         "**LeftOnly_test** (truth: S2 left temporal and S3 left parietal affected, S1, S4, S5, S6 healthy; core as Mild).",
         "Success criterion (from the brief, fixed now): with the primary method, R2 side = **left**, and R1 calls "
         "S2 and S3 affected and S5 and S6 healthy. Partial success: side = left with S3 affected and S5, S6 healthy.", ""]
    rows = []
    for m in (PRIMARY, "bounded dS", SECOND, "bounded log (gain-inv.)"):
        q = bp["LeftOnly_test"][m]
        rows.append(dict(method=m, **{f"P(called) {SHORT[k]}": q["p_called"][k] for k in range(6)},
                         LR=f"{q['LR_mean']:+.1f} ± {q['LR_sd']:.1f}", p_left=q["p_left"], p_right=q["p_right"],
                         p_front_or_back=q["p_fb"]))
    L += ["What the frozen pipeline returns on Born-simulated LeftOnly data (true dε map, frozen κ) plus 40 typical-"
          "noise draws:", "",
          _t(rows, ["method"] + [f"P(called) {s}" for s in SHORT] + ["LR", "p_left", "p_right", "p_front_or_back"],
             {**{f"P(called) {s}": ".2f" for s in SHORT}, "p_left": ".2f", "p_right": ".2f",
              "p_front_or_back": ".2f"}), "",
          "Predicted: side = **left**; S3 affected; S2 affected in most draws (it is the weaker of the two: e = 7.5 "
          "mm vs 11.5 mm); S1, S4, S5, S6 healthy; front/back none (spurious front/back in 5–25 % of noisy draws, "
          "highest for the bounded fits). Caveat: the simulated data follow the linear model, while the "
          "HFSS changes are only partly linear (§0 of the report), so the real values will scatter more than these "
          "draws.", "",
          "**MCI_lobe** (truth: only the hippocampus, 25 → 21.25 mm; CSF healthy).", ""]
    rows = []
    for m in (PRIMARY, "bounded dS", SECOND, "bounded log (gain-inv.)"):
        q = bp["MCI_lobe"][m]
        rows.append(dict(method=m, p_any_called=q["p_any"], p_left=q["p_left"], p_right=q["p_right"],
                         p_front_or_back=q["p_fb"], LR=f"{q['LR_mean']:+.1f} ± {q['LR_sd']:.1f}"))
    L += ["Success criterion (fixed now): with the primary method, no sector called, side none, front/back none.", "",
          _t(rows, ["method", "p_any_called", "p_left", "p_right", "p_front_or_back", "LR"],
             {"p_any_called": ".2f", "p_left": ".2f", "p_right": ".2f", "p_front_or_back": ".2f"}), "",
          "Predicted: **no sector called, side none, front/back none** (nothing beyond the noise floor; under noise "
          "a spurious front/back call is expected in "
          f"{min(q['p_fb'] for q in bp['MCI_lobe'].values()):.0%}–{max(q['p_fb'] for q in bp['MCI_lobe'].values()):.0%} "
          "of draws, a spurious side call in ≤ 8 %). The "
          "hippocampal change is invisible to the array (CRLB of the core ≫ its change).", ""]
    (OUT / "lobe_predictions.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------------------------
def run_blind():
    """Stage 2: unchanged frozen pipeline on the blind designs; appends the outcome to the report."""
    from imaging import run_lobe as RL
    fz = json.loads((OUT / "lobe_frozen.json").read_text(encoding="utf-8"))
    present = [d for d in SL.BLIND if (ROOT / "data" / "raw" / f"new_with_slices_{d}.s6p").exists()]
    if not present:
        print("blind designs not present yet:", SL.BLIND)
        return
    res = pickle.loads((RL.CACHE / "stage1.pkl").read_bytes())
    S, f, fh, fi, P = RL.build(reuse=True)
    kappa = np.array(fz["kappa_re"]) + 1j * np.array(fz["kappa_im"])
    from .common import PROFILES
    M = RL.models(S, fh, fi, P, kappa, PROFILES["typical"])
    H = S["Healthy_sliced"]
    lam = {"dS": fz["lambda_dS"], "log": fz["lambda_log"]}
    out = []
    for d in present:
        Sd, _ = SL.load_design(d, f)
        for m in RL.METHODS:
            lm = lam["dS"] if m.endswith("dS") else lam["log"]
            x = RL.invert(M, m, lm, S_stage_fi=Sd[fi], S_ref_fi=H[fi], dS_fi=SL.recip(Sd[fi] - H[fi]))
            c = RL.apply_rules(x, fz["rules"][m])
            calls = " ".join(f"S{k + 1}" for k in range(6) if c["affected"][k]) or "none"
            if d == "LeftOnly_test":
                ok = (c["side"] == "left" and c["affected"][1] and c["affected"][2]
                      and not c["affected"][4] and not c["affected"][5])
                partial = c["side"] == "left" and c["affected"][2] and not c["affected"][4] and not c["affected"][5]
                verdict = "SUCCESS" if ok else ("PARTIAL" if partial else "FAIL")
            else:
                ok = not any(c["affected"]) and c["side"] == "none" and c["frontback"] == "none"
                verdict = "SUCCESS" if ok else "FAIL"
            out.append(dict(design=d, method=m, **{f"dε'' {SHORT[k]}": x[6 + k] for k in range(6)},
                            called=calls, LR=c["LR"], side=c["side"], FB=c["FB"], frontback=c["frontback"],
                            verdict=verdict))
    L = ["## 6. Blind test outcome (pre-registered)", "",
         f"Frozen at code `{fz['code']}`; predictions in `lobe_predictions.md`. Scored now at code `{git_hash(ROOT)}` "
         "with the unchanged frozen κ, λ and thresholds.", "",
         _t(out, ["design", "method"] + [f"dε'' {s}" for s in SHORT] + ["called", "LR", "side", "FB", "frontback", "verdict"],
            {**{f"dε'' {s}": ".1f" for s in SHORT}, "LR": "+.1f", "FB": "+.1f"}), ""]
    prim = {o["design"]: o for o in out if o["method"] == PRIMARY}
    blind_txt = None
    if "LeftOnly_test" in prim:
        o = prim["LeftOnly_test"]
        blind_txt = (f"**blind test {o['verdict']}** (primary method): LeftOnly_test side = {o['side']}, "
                     f"LR = {o['LR']:+.1f}, called {o['called']}.")
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    i0 = rep.index("## 6. Blind test")
    i1 = rep.index("## 7. Verdict")
    rep = rep[:i0] + "\n".join(L) + "\n" + "\n".join(_verdict(res, blind_txt)) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
    (OUT / "lobe_blind_outcome.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print("blind outcome written for", present)
