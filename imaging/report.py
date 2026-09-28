"""Figures, results/imaging/report.md and metrics_imaging.csv from the study results."""
from __future__ import annotations

import json
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .common import (ASSUMPTIONS, FIG, OUT, R_CSF, HeadParams, git_hash, ROOT, true_delta,  # noqa: E402
                     write_metric)
from .fields import FIELD_DIR, fields_available  # noqa: E402
from .study_i1 import R_PROF, detection_accuracy  # noqa: E402
from .study_i3 import NAMES, UNITS  # noqa: E402

REPORTED = ("Moderate", "Severe")
STAGES = ("Mild", "Moderate", "Severe")
C_ST = {"Mild": "#4C78A8", "Moderate": "#F58518", "Severe": "#E45756", "noise": "#888888"}


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


def _fisher(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float((a.mean() - b.mean()) ** 2 / max(a.var() + b.var(), 1e-300))


def _bhatt(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = max(a.var(), 1e-300), max(b.var(), 1e-300)
    v = 0.5 * (va + vb)
    return float(0.125 * (a.mean() - b.mean()) ** 2 / v + 0.5 * np.log(v / np.sqrt(va * vb)))


def _metric_row(method_id, desc, det, notes, sim_set=None, cfg=None, write=True):
    """Binary Normal vs AD: threshold tuned on Mild vs Normal draws, tested on Moderate+Severe
    vs fresh Normal draws. Returns the accuracy dict."""
    pos = np.concatenate([det[s] for s in REPORTED if s in det])
    acc = detection_accuracy(np.asarray(det["Mild"]), np.asarray(det["noise"]), pos,
                             np.asarray(det["noise_test"]))
    row = dict(classes="Normal|AD(Moderate+Severe); tuned on Mild", method_id=method_id,
               feature_desc=desc, feature_dim=1, classifier="THR (tau tuned on Mild vs Normal draws)",
               noise_profile="typical", cv_scheme="train Mild+Normal draws / test Moderate+Severe+fresh Normal draws",
               n_sims_per_class=1, n_test=int(len(pos) + len(det["noise_test"])),
               accuracy=round(acc["acc"], 4), balanced_accuracy=round(acc["bal_acc"], 4),
               macro_f1=round(acc["macro_f1"], 4),
               min_pairwise_fisher=round(_fisher(pos, det["noise_test"]), 4),
               min_pairwise_bhattacharyya=round(_bhatt(pos, det["noise_test"]), 4),
               reject_rate=0.0, accuracy_on_accepted=round(acc["acc"], 4), notes=notes)
    if sim_set:
        row["sim_set"] = sim_set
    if write:
        write_metric(row, cfg)
    return acc


# ----------------------------------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------------------------------
def _circle(ax, r, **kw):
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(r * np.cos(t), r * np.sin(t), **kw)


def fig_paths(P, sd):
    from .common import ring_modes
    from .timedomain import TimeResponse
    f = sd.f_hz
    t = np.arange(0, 10e-9, 10e-12)
    c = {s: ring_modes(sd.S[s], sd.port_to_ant) for s in sd.S}
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
    for k in range(4):
        h = np.abs(TimeResponse(f, c["Normal"][:, k][None])(t[None]))[0]
        ax[0].plot(t * 1e9, 20 * np.log10(h / h.max()), label=f"k={k}")
        d = c["Mild"][:, k] - c["Normal"][:, k]
        h = np.abs(TimeResponse(f, d[None])(t[None]))[0]
        ax[1].plot(t * 1e9, 20 * np.log10(h / h.max()), label=f"k={k}")
    for r in P["paths"]:
        if r["k"] == 3:
            for a in ax:
                a.axvline(r["pred_creep_ns"], color="k", ls="--", lw=0.8)
                a.axvline(r["pred_straight_ns"], color="k", ls=":", lw=0.8)
    ax[0].set_title("HFSS Normal ring modes |h_k(t)| (Hann, 3.2-4.2 GHz)")
    ax[1].set_title("dS_k = Mild - Normal; k=3 predictions: -- air/creeping, : through head")
    for a in ax:
        a.set_xlabel("t (ns)")
        a.set_ylim(-40, 2)
        a.legend(fontsize=8)
    ax[0].set_ylabel("dB (norm.)")
    fig.tight_layout()
    fig.savefig(FIG / "k3_path_time.png", dpi=130)
    plt.close(fig)


def fig_i1(R1):
    key_best = "layered"
    for pl in ("ring", "vertical"):
        fig, ax = plt.subplots(3, 4, figsize=(12, 9))
        for i, m in enumerate(("DAS", "DMAS", "MVDR")):
            P = R1["planes"].get(f"{pl}|{m}")
            if P is None:
                continue
            u, mask = P["u"], P["mask"]
            vmax = max(np.max(P[s]) for s in STAGES)
            for j, s in enumerate(("noise",) + tuple(STAGES)):
                img = np.full(mask.shape, np.nan)
                img[mask] = P[s]
                im = ax[i, j].imshow(10 * np.log10(np.maximum(img / vmax, 1e-6)), origin="lower",
                                     extent=[u[0], u[-1], u[0], u[-1]], vmin=-15, vmax=0, cmap="magma")
                if pl == "ring":
                    z = 97.55 * np.cos(np.deg2rad(60.5))
                    _circle(ax[i, j], np.sqrt(88 ** 2 - z ** 2), color="w", lw=0.6)
                    _circle(ax[i, j], np.sqrt(83.5 ** 2 - z ** 2), color="c", lw=0.6)
                else:
                    _circle(ax[i, j], 88, color="w", lw=0.6)
                    _circle(ax[i, j], 83.5, color="c", lw=0.6)
                ax[i, j].set_title(f"{m} {s if s != 'noise' else 'noise-only'}", fontsize=9)
                ax[i, j].set_xticks([])
                ax[i, j].set_yticks([])
        fig.colorbar(im, ax=ax, shrink=0.6, label="dB rel. max over stages")
        fig.suptitle(f"I1 {pl} plane ({'z = +48 mm' if pl == 'ring' else 'y = 0'}), "
                     f"{key_best} delays, settings tuned on Mild; cyan = brain surface")
        fig.savefig(FIG / f"i1_{pl}_plane.png", dpi=110)
        plt.close(fig)
    fig, ax = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    for i, mode in enumerate(("eff", "layered")):
        for j, m in enumerate(("DAS", "DMAS", "MVDR")):
            pr = R1["profiles"][f"{mode}|{m}"]
            ref = max(np.max(pr[s]) for s in STAGES)
            for s in STAGES:
                ax[i, j].plot(R_PROF, np.asarray(pr[s]) / ref, color=C_ST[s], label=s)
            ax[i, j].plot(R_PROF, np.asarray(pr["noise"]) / ref, color=C_ST["noise"], ls="--",
                          label="noise-only (mean)")
            for s in REPORTED:
                tp = np.asarray(R1["true_prof"][s])
                ax[i, j].fill_between(R_PROF, 0, tp / tp.max() * 0.3, color=C_ST[s], alpha=0.12)
            ax[i, j].axvline(83.5, color="k", lw=0.6)
            ax[i, j].set_title(f"{m}, {'eff. eps' if mode == 'eff' else 'layered rays'}", fontsize=9)
            ax[i, j].set_xlabel("radius (mm)")
    ax[0, 0].legend(fontsize=7)
    fig.suptitle("I1 azimuthally averaged radial profiles (shaded: true |d eps_r|(r), Moderate/Severe)")
    fig.tight_layout()
    fig.savefig(FIG / "i1_radial_profiles.png", dpi=120)
    plt.close(fig)


def fig_i2(R2):
    maps = R2["maps"]
    fig, ax = plt.subplots(2, 4, figsize=(14, 7))
    for i, pl in enumerate(("ring", "vertical")):
        M = maps[pl]
        u, mask = M["u"], M["mask"]
        for k in range(4):
            img = np.full(mask.shape, np.nan)
            img[mask] = M["sens"][k]
            im = ax[i, k].imshow(10 * np.log10(img / np.nanmax(img)), origin="lower",
                                 extent=[u[0], u[-1], u[0], u[-1]], vmin=-40, vmax=0, cmap="viridis")
            if pl == "ring":
                z = 97.55 * np.cos(np.deg2rad(60.5))
                _circle(ax[i, k], np.sqrt(83.5 ** 2 - z ** 2), color="w", lw=0.6)
            else:
                _circle(ax[i, k], 83.5, color="w", lw=0.6)
            ax[i, k].set_title(f"k={k}, {pl} plane", fontsize=9)
            ax[i, k].set_xticks([])
            ax[i, k].set_yticks([])
    fig.colorbar(im, ax=ax, shrink=0.6, label="sum |J| (dB rel. max per k)")
    fig.suptitle(f"I2 sensitivity maps, 3.4/3.6/3.8 GHz, {R2['field_source'].split(' (')[0]} fields")
    fig.savefig(FIG / "i2_sensitivity_maps.png", dpi=110)
    plt.close(fig)
    sr = R2["sens_radial"]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for k in range(4):
        ax[0].plot(sr["r"], 10 * np.log10(sr["sens"][k] / sr["sens"][k].max()), label=f"k={k}")
    ax[0].axvline(83.5, color="k", lw=0.6)
    ax[0].set_ylim(-80, 3)
    ax[0].set_xlabel("radius (mm)")
    ax[0].set_ylabel("shell-averaged sum |J| (dB rel. max)")
    ax[0].legend()
    ax[0].set_title("shape: sensitivity rel. to own max")
    if "snr_radial" in R2:
        sn = R2["snr_radial"]
        fig2, bx = plt.subplots(figsize=(6, 4))
        for k, lab in enumerate(["k=0", "k=1", "k=2", "k=3", "all pairs"]):
            ln = bx.semilogy(sn["r"], np.median(sn["snr"][k], -1), lw=2.5 if k == 4 else 1.2,
                             label=f"{lab} (median dir.)")
            bx.semilogy(sn["r"], np.max(sn["snr"][k], -1), lw=2.5 if k == 4 else 1.2, ls="--",
                        color=ln[0].get_color(), label=f"{lab} (best dir.)" if k in (0, 4) else None)
        bx.axhline(1, color="k", lw=0.6)
        bx.axhline(3, color="k", lw=0.6, ls="--")
        bx.axvline(83.5, color="k", lw=0.5)
        bx.set_xlabel("radius (mm)")
        bx.set_ylabel("SNR (solid: median, dashed: best direction)")
        bx.set_title("Detectability: 1 cm^3 blob, |d eps| = 10, typical noise")
        bx.legend(fontsize=8)
        fig2.tight_layout()
        fig2.savefig(FIG / "i2_detectability_radial.png", dpi=120)
        plt.close(fig2)
    b = R2["block"]
    for k in range(4):
        ax[1].semilogy([x["r_block_mm"] for x in b], [max(x[f"k{k}"], 1e-12) for x in b], "o-", label=f"k={k}")
    ax[1].set_xlabel("absorber fills r < r_b (mm)")
    ax[1].set_ylabel("|V_k(blocked) - V_k| / |V_k| (total coupling)")
    ax[1].legend()
    ax[1].set_title("Block-the-core test (model)")
    fig.tight_layout()
    fig.savefig(FIG / "i2_sensitivity_radial.png", dpi=120)
    plt.close(fig)
    rad = R2["radial"]
    r = rad["r"]
    n = len(r)
    fig, ax = plt.subplots(2, 3, figsize=(14, 7), sharex=True)
    for j, key in enumerate(("synthetic-nonlinear", "HFSS", "noise-only")):
        for s in REPORTED:
            kk = key if key == "noise-only" else f"{key}|{s}"
            sol = rad["sol"][kk]
            for i, (sl, lab) in enumerate(((slice(0, n), "d eps_r"), (slice(n, 2 * n), "d eps''(3.7 GHz)"))):
                ax[i, j].plot(r, sol["tikhonov-gcv"][sl], color=C_ST[s] if key != "noise-only" else "k",
                              label=f"{s} Tikhonov-GCV" if key != "noise-only" else "noise-only")
                ax[i, j].plot(r, sol["tv"][sl], color=C_ST[s] if key != "noise-only" else "k", ls="--",
                              label=f"{s} TV" if key != "noise-only" else None)
                if key != "noise-only":
                    ax[i, j].plot(r, rad["truth"][s][sl], color=C_ST[s], lw=2.5, alpha=0.35,
                                  label=f"{s} truth")
                ax[i, j].set_ylabel(lab)
            if key == "noise-only":
                break
        ax[0, j].set_title(key, fontsize=10)
        ax[1, j].set_xlabel("radius (mm)")
    ax[0, 0].legend(fontsize=7)
    fig.suptitle("I2 radial inversions (2 mm shells), " + R2["field_source"].split(" (")[0])
    fig.tight_layout()
    fig.savefig(FIG / "i2_radial_inversion.png", dpi=120)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(r, rad["resolution_diag"]["eps_r"], label="d eps_r")
    ax.plot(r, rad["resolution_diag"]["eps_pp"], label="d eps''")
    ax.set_xlabel("shell radius (mm)")
    ax.set_ylabel("diag of model-resolution matrix")
    ax.axhline(0.5, color="k", lw=0.5)
    ax.legend()
    ax.set_title("I2 radial resolution (Tikhonov, GCV lambda on Mild)")
    fig.tight_layout()
    fig.savefig(FIG / "i2_resolution.png", dpi=120)
    plt.close(fig)
    vx = R2["voxel"]
    g, keep, vox = vx["grid"], vx["keep"], vx["vox"]
    nv = len(vox)
    z_ring = 97.55 * np.cos(np.deg2rad(60.5))
    fig, ax = plt.subplots(2, 4, figsize=(14, 7))
    cases = [("synthetic-linear|Severe", "tikhonov-gcv"), ("HFSS|Severe", "tikhonov-gcv"),
             ("HFSS|Severe", "l1"), ("noise-only", "tikhonov-gcv")]
    for j, (key, meth) in enumerate(cases):
        x = vx["sol"][key][meth][:nv]
        for i, (sel, lab) in enumerate(((np.abs(vox[:, 2] - z_ring) < 1.6, "ring plane"),
                                        (np.abs(vox[:, 1]) < 1.6, "y = 0"))):
            pts = vox[sel]
            a, b = (pts[:, 0], pts[:, 1]) if i == 0 else (pts[:, 0], pts[:, 2])
            sc = ax[i, j].scatter(a, b, c=x[sel], s=9, marker="s", cmap="RdBu_r",
                                  vmin=-np.abs(x).max(), vmax=np.abs(x).max())
            ax[i, j].set_aspect("equal")
            ax[i, j].set_title(f"{key} {meth}\n{lab} (d eps_r)", fontsize=8)
            ax[i, j].set_xticks([])
            ax[i, j].set_yticks([])
            fig.colorbar(sc, ax=ax[i, j], shrink=0.7)
    fig.suptitle("I2 voxel inversions (3 mm), " + R2["field_source"].split(" (")[0])
    fig.tight_layout()
    fig.savefig(FIG / "i2_voxel.png", dpi=110)
    plt.close(fig)


def fig_i3(R3):
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for j, ds in enumerate(("HFSS", "synthetic")):
        c = R3["classify"].get(ds)
        if c is None:
            continue
        feats = c["feats"]
        groups = ["Normal_test", *STAGES]
        ax[j].boxplot([feats[g]["t_csf"] for g in groups], tick_labels=groups)
        for i, s in enumerate(STAGES):
            ax[j].plot(i + 2, R_CSF - HeadParams.stage(s).r_gray, "r_", ms=20)
        ax[j].plot(1, R_CSF - HeadParams.stage("Normal").r_gray, "r_", ms=20)
        ax[j].set_title(f"I3 recovered CSF thickness, {ds} draws (red = truth)")
        ax[j].set_ylabel("mm")
    fig.tight_layout()
    fig.savefig(FIG / "i3_csf_thickness.png", dpi=120)
    plt.close(fig)


# ----------------------------------------------------------------------------------------------
def write(R, sd, cfg, write_csv=True):
    FIG.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)
    L = [f"# Track A — imaging / localisation study (`imaging/`, code {gh}, {date.today()})", ""]
    L += ["Regenerate: `python imaging/run_imaging.py` (tests: `python -m pytest imaging/tests -q`).",
          "Everything here comes from **one HFSS simulation per stage**: it shows what is recoverable "
          "from these simulations under the stated noise, **not** generalisation to new heads. "
          "Between-mesh noise is unmeasured, so every AD-vs-AD statement is **unverified against mesh noise**.",
          "**Tuning protocol:** every free choice (antenna delay, effective permittivity, regularisation "
          "weights, calibration scale kappa(f), thresholds) is set on **Mild**; results are reported on "
          "**Moderate and Severe**. Noise floor = 'typical' profile (0.25 dB, 2 deg, -70 dB floor) on "
          "both the stage and the Normal measurement.", ""]
    L += ["## 0. Data, assumptions, blocked items", ""]
    L += [f"- Files: " + ", ".join(f"{s}: `{sd.files[s]}`" for s in sd.S)
          + f". Common grid {sd.f_hz[0]/1e9:.1f}-{sd.f_hz[-1]/1e9:.1f} GHz, {len(sd.f_hz)} points, "
          "glitch masking ON (shared loader)."]
    L += [f"- Assumption: {a}" for a in ASSUMPTIONS]
    L += ["- The brief names `reference/dbim_reference.m`; the repository holds "
          "`references/imaging_code.m` (a 2-D incident/total-field script). Not used beyond inspiration.",
          f"- **`data/fields/` HFSS field exports: {'present' if fields_available() else 'ABSENT'}.** "
          + ("" if fields_available() else
             "Blocked: I2 with the numerical (HFSS) Green's function, i.e. HFSS sensitivity maps, "
             "HFSS-field Jacobians and their inversions. The field reader (`imaging/fields.py`, header-"
             "driven column order) is implemented and unit-tested on a synthetic file. Everything in I2 "
             "below uses the **forward-model fields as a SURROGATE** Green's function, labelled as such.")]
    L += [""]

    # ------------------------------------------------------------------ paths
    if "paths" in R:
        P = R["paths"]
        fig_paths(P, sd)
        L += ["## 1. The k = 3 path question — direct evidence from the HFSS couplings", ""]
        L += ["Group delay = slope of the unwrapped phase over 3.2–4.2 GHz. The unknown antenna/feed "
              "delay is removed with the neighbour path (k = 1). Its straight line only grazes the "
              f"skin (closest approach {P['paths'][0]['chord_closest_to_centre_mm']:.1f} mm), so it "
              f"travels in air: 2 t_ant = gd(k1) − chord/c = **{P['two_t_ant_ns']:.2f} ns**.", ""]
        L += [_t(P["paths"], ["k", "sep_deg", "chord_mm", "chord_closest_to_centre_mm", "creep_len_mm",
                              "pred_straight_ns", "pred_creep_ns", "measured_gd_Normal_ns"],
                 {c: ".2f" for c in ["sep_deg", "chord_mm", "chord_closest_to_centre_mm", "creep_len_mm",
                                     "pred_straight_ns", "pred_creep_ns", "measured_gd_Normal_ns"]}), ""]
        m = P["measured"]
        L += [_t([{"stage": s, **{k: v for k, v in m[s].items() if k.startswith("gd")}} for s in m],
                 ["stage"] + [k for k in m["Mild"] if k.startswith("gd")],
                 {k: ".2f" for k in m["Mild"]}), ""]
        k3 = P["paths"][2]
        L += [f"**Verdict (k = 3).** Measured group delay {k3['measured_gd_Normal_ns']:.2f} ns. The "
              f"air/creeping path predicts {k3['pred_creep_ns']:.2f} ns "
              f"(Δ = {abs(k3['pred_creep_ns'] - k3['measured_gd_Normal_ns']):.2f} ns). The straight "
              f"path through the head predicts {k3['pred_straight_ns']:.2f} ns "
              f"(Δ = {k3['pred_straight_ns'] - k3['measured_gd_Normal_ns']:.1f} ns). The same holds "
              "for Mild/Moderate/Severe (table). So the opposite-antenna signal **travels around the "
              "head** (air side of the skin: creeping, or guided along the nearly closed ring of AMC "
              "reflectors), not through the brain. dS_k3 has about the same delay as the k3 wave "
              "itself. So the stage information on k = 3 is a modification of that surface-guided "
              "wave by the near-surface layers (CSF/cortex below the skull), not an echo from depth. "
              "Figure: `figures/k3_path_time.png`.",
              "- Caveats: (i) with a resonant patch/AMC antenna the group delay is frequency-dependent. "
              "The single slope is a band average, uncertain by a few tenths of a ns. The 2.4 ns "
              "margin is well outside that. (ii) k = 2 does not fit either prediction cleanly "
              "(4.87 ns): its coupling has deep nulls near 3.8 GHz (two unequal paths around the "
              "ring interfere), so its slope is unreliable.", ""]

    # ------------------------------------------------------------------ I1
    if "i1" in R:
        R1 = R["i1"]
        fig_i1(R1)
        L += ["## 2. I1 — radar beamforming of dS (DAS, DMAS, MVDR)", ""]
        L += ["- Signals: the 21 reciprocal pairs, each whitened by its noise std (else S_ii, 40–60 dB "
              "above the transmissions, is the whole image). Hann window, zero-padded IFFT (8192), "
              f"-6 dB pulse width {R1['pulse_width_ns']:.2f} ns; DAS/DMAS energy over a "
              f"{R1['window_ns']:.2f} ns window at the focal delay.",
              "- Delays: (a) one effective eps inside the skin; (b) straight rays through the Normal "
              "layers. Pair delay tau_i + tau_j + 2 t_ant.",
              "- MVDR: see `imaging/beamform.py`. With **one** measurement per pair, the 21×21 "
              "covariance of a single snapshot is rank 1 and not invertible. The F = 201 focused "
              "frequency bins are used as snapshots (rank ≤ 21, assumes a frequency-flat focused "
              "response), with diagonal loading 0.1·tr(R)/21. With loading → ∞ it reduces to DAS.",
              "- Tuned on Mild: t_ant ∈ {0, 0.5, 1, 1.5, 2} ns and eps_eff ∈ {20, 30, 40, 50}, chosen "
              "by the largest signal-to-clutter ratio (SCR = Mild image peak / mean noise-only peak). "
              "SCR does not use the true change location.", ""]
        L += [_t([{"setting": k, **v} for k, v in R1["best"].items()],
                 ["setting", "eps_eff", "t_ant_ns", "scr_db", "peak_r_mm"], {"scr_db": ".1f"}), ""]
        L += ["**Point-target test (ideal flat-spectrum scatterer, homogeneous eps = 40, ring plane).** "
              "This is the array's intrinsic resolution: −3 dB widths along x (radial), y (azimuthal) "
              "and z (elevation), and the peak offset.", ""]
        L += [_t(R1["psf"], ["r_mm", "method", "x_peak_offset_mm", "x_width_3dB_mm", "y_peak_offset_mm",
                             "y_width_3dB_mm", "z_peak_offset_mm", "z_width_3dB_mm"], {}), "",
              "An ideal point scatterer is focused at the right place in-plane by all three methods; "
              "widths of 2 mm are the grid-sampling limit. This test is noise-free, so the MVDR "
              "widths are optimistic. Elevation is the weak axis (DAS/DMAS 16–82 mm), as expected "
              "for one ring. So the failure on the real dS below is not a beamformer bug. A "
              "spherically symmetric change gives the same signal on every pair at a given k, and "
              "those add coherently at the equidistant centre. The echo delays also contain the "
              "unknown antenna response.", ""]
        rows = []
        for k, v in R1["stages"].items():
            mode, m, s = k.split("|")
            rows.append(dict(delays=mode, method=m, stage=s, **v))
        L += ["**Results.** The true change of every AD stage is a set of shells: the outermost starts "
              "at the brain surface (83 mm, gray → CSF; 83–83.5 mm CSF material). The changed band "
              "spans 57–83.5 mm (Severe), plus the hippocampus. peak_r = radius of the maximum of "
              "the azimuthally averaged profile. SCR = clean stage image peak / mean noise-only peak. "
              "scr_noisy = the same with noise on both measurements.", ""]
        L += [_t(rows, ["delays", "method", "stage", "peak_r_mm", "scr_db", "scr_noisy_db",
                        "frac_draws_above_noise_p95"], {"scr_db": ".1f", "scr_noisy_db": ".1f",
                                                        "frac_draws_above_noise_p95": ".2f"}), ""]
        L += ["Peak radius vs assumed antenna delay (DAS, layered rays). The depth the image assigns "
              "is set by t_ant, which the data cannot fix (§1: transmission carries ~3 ns of antenna "
              "delay that reflection does not show):", ""]
        L += [_t(R1["t_ant_ambiguity"], ["t_ant_ns"] + [s for s in STAGES], {"t_ant_ns": ".2f"}), ""]
        L += ["Figures: `figures/i1_ring_plane.png`, `figures/i1_vertical_plane.png`, "
              "`figures/i1_radial_profiles.png`.", ""]

    # ------------------------------------------------------------------ validation
    if "val" in R:
        V = R["val"]
        L += ["## 3. Forward model (a): layered-sphere Mie solution + point dipoles — validation", ""]
        L += ["Exact vector-spherical-wave solution for the 7-layer sphere. Each antenna is a "
              "tangential electric point dipole at its feed (97.55 mm, polar 60.5°). The dyadic "
              "Green's function expansion, the Mie coefficients, field continuity, reciprocity and "
              "Born-vs-exact are unit-tested: free-space limit 1e-10, Mie vs direct 1e-12, "
              "reciprocity 1e-15, Born = exact thin-shell derivative to 3e-5.", "",
              f"- Polarisation chosen on **Normal only**: misfit of one common complex antenna factor "
              f"a²(f) to the HFSS k = 1..3 couplings — theta {V['pol']['theta']:.2f}, phi "
              f"{V['pol']['phi']:.2f} → **{V['pol_chosen']}**.",
              "- Convergence in the number of harmonics (relative change of dV_Mild vs n = 150):", ""]
        L += [_t(V["conv"], ["nmax", "k0", "k1", "k2", "k3"], {f"k{k}": ".1e" for k in range(4)}), ""]
        L += ["- dS prediction. calA = the brief's per-ring-distance correction c_k(f) = S_k/V_k fitted "
              "on the Normal total coupling (c_0 := c_1). calB = one complex a²(f) per frequency, "
              "fitted to dS_Mild over all k (tuned on Mild). trivial = predicting dS_stage by "
              "dS_Mild. rel_err = |pred − HFSS| / |HFSS|, so 1.0 is as bad as predicting zero. "
              "shape_corr = |<pred, HFSS>| over frequency. growth = |dS_stage| / |dS_Mild|.", ""]
        L += [_t(V["table"], ["stage", "k", "calA_rel_err", "calB_rel_err", "shape_corr", "trivial_rel_err",
                              "model_growth_vs_mild", "hfss_growth_vs_mild"], {c: ".2f" for c in V["table"][0]}), ""]
        L += ["**Verdict: the validation FAILS beyond the neighbour path.** Findings:", "",
              "- With the brief's Normal calibration, the model predicts Mild dS only on k = 1 "
              "(shape correlation ≈ 0.9). k = 0 and k = 2 are wrong in shape (corr 0.1–0.5), and k = 3 "
              "is off in amplitude.",
              "- The model's k = 3 total coupling is a deep shadow (−83…−99 dB). HFSS has −55 dB. HFSS "
              "carries an opposite-antenna path the point-dipole model lacks, consistent with §1 "
              "(around-the-head air path; the six AMC reflectors nearly close a ring).",
              "- The model predicts Severe dS ≈ 2× Mild on every path. HFSS shows ≈ 1.3–1.4×. Even the "
              "most flexible calibration fitted on Mild does not beat the trivial predictor on "
              "Moderate/Severe.",
              "- A patch-sized aperture (5×5 dipoles, cos taper) and phase-centre radii 92–105 mm were "
              "also tried. None fixes this (rel. err ≈ 0.8–1.2). The mismatch is in the antenna/"
              "array structure, not the head model.",
              "- Consequence: every inversion that needs a forward model (I2 with surrogate fields, "
              "I3) is reported twice: on HFSS data (model-mismatch limited) and on model-generated "
              "synthetic data with the same noise (the array's intrinsic capability if the antenna "
              "were modelled correctly).", ""]

    # ------------------------------------------------------------------ I2
    if "i2" in R:
        R2 = R["i2"]
        fig_i2(R2)
        L += ["## 4. I2 — sensitivity maps and linearised inversion", "",
              f"**Field source: {R2['field_source']}.** J_ij(r) = −j k0³ E_i·E_j (no conjugate, "
              "e^{+jωt}). With HFSS exports this becomes −(jωε0/4a_ia_j)E_i·E_j; a complex scale "
              "kappa(f) per frequency is calibrated on Mild in both cases.", ""]
        L += ["### 4.1 Where can this array see?", "",
              "Shell-averaged sensitivity (sum over pairs at distance k and 3.4/3.6/3.8 GHz). "
              "r_peak = radius of maximum sensitivity; r_XdB = the largest radius below r_peak where it "
              "is X dB under that maximum.", ""]
        L += [_t([{"k": k, **v} for k, v in R2["sens_depth"].items()], ["k", "r_peak", "r_10dB", "r_20dB", "r_40dB"],
                 {c: ".0f" for c in ["r_peak", "r_10dB", "r_20dB", "r_40dB"]}), ""]
        if "snr_radial" in R2:
            sn = R2["snr_radial"]
            rows = []
            for k, lab in enumerate(["k=0", "k=1", "k=2", "k=3", "all 21 pairs"]):
                for stat, fn in (("median dir.", np.median), ("best dir.", np.max)):
                    v = fn(sn["snr"][k], -1)
                    rows.append(dict(path=lab, over=stat, snr_at_83=float(np.interp(83.0, sn["r"], v)),
                                     snr_at_70=float(np.interp(70.0, sn["r"], v)),
                                     snr_at_50=float(np.interp(50.0, sn["r"], v)),
                                     snr_at_20=float(np.interp(20.0, sn["r"], v)),
                                     r_min_snr1=_rmin(sn["r"], v, 1.0), r_min_snr3=_rmin(sn["r"], v, 3.0)))
            L += ["**Detectability (absolute).** A relative profile only shows shape. What matters is the SNR "
                  "a localised change would produce. Here: a 1 cm³ blob with |d eps| = 10 (about the "
                  "gray→CSF contrast) at radius r, on the Normal background, typical noise on both "
                  "measurements, scale kappa(f) from Mild, 3 frequencies. r_min_snrX = the smallest "
                  "radius down to which SNR ≥ X holds continuously from the surface. Figure: "
                  "`figures/i2_detectability_radial.png`.", "",
                  _t(rows, ["path", "over", "snr_at_83", "snr_at_70", "snr_at_50", "snr_at_20", "r_min_snr1",
                            "r_min_snr3"], {c: ".2g" for c in ["snr_at_83", "snr_at_70", "snr_at_50", "snr_at_20"]}),
                  "",
                  "Relative (shape) profile: k = 3 is the flattest in depth, because both opposite fields "
                  "are weak everywhere. In absolute terms every path has the same tiny sensitivity at the "
                  "centre (all six fields are equal there). k = 3 simply has far less surface "
                  "sensitivity and far lower noise than k = 0.", ""]
        L += ["Volume-weighted fraction of the sensitivity inside r < 60 mm: "
              + ", ".join(f"{k} {v:.1e}" for k, v in R2["sens_fraction_core60"].items()) + ".", ""]
        L += ["Block-the-core test (model): everything inside r_b is replaced by a strong absorber "
              "(eps 40, 40 S/m). Entries are the relative change of the TOTAL coupling of each path:", ""]
        L += [_t(R2["block"], ["r_block_mm", "k0", "k1", "k2", "k3"], {f"k{k}": ".1e" for k in range(4)}), ""]
        bl = {b["r_block_mm"]: b for b in R2["block"]}
        L += [f"- In the model, every path is dominated by the outer ~1 cm. Replacing everything "
              f"inside r < 55 mm by an absorber changes the total couplings by only "
              f"{min(bl[55][f'k{k}'] for k in range(4)):.0%}–{max(bl[55][f'k{k}'] for k in range(4)):.0%}. "
              f"The same test inside r < 75 mm changes them by "
              f"{min(bl[75][f'k{k}'] for k in range(4)):.0%}–{max(bl[75][f'k{k}'] for k in range(4)):.0%}. "
              "k = 3 is not special in depth once measured in absolute terms. Together with §1 "
              "(measured delay = air path), **k = 3 is a surface/air path, not a through-centre "
              "path**. Its stage sensitivity comes from the near-surface layers (CSF/cortex below "
              "the skull).",
              "- Relative-profile table: n/a = the profile never falls that far below its own "
              "maximum (the product of two weak fields is weak everywhere); use the absolute "
              "detectability table instead.",
              "- Figures: `figures/i2_sensitivity_maps.png` (ring + vertical planes, per k), "
              "`figures/i2_sensitivity_radial.png`.", ""]
        L += ["### 4.2 Linearisation error", "",
              "Model-internal: |Born(true d eps) − exact dV| / |exact dV|. HFSS: "
              "|kappa·Born(true d eps) − dS_HFSS| / |dS_HFSS|, with kappa(f) fitted on Mild.", ""]
        rows = [dict(stage=s, **{f"model_k{k}": R2["lin_err_model"][s][k] for k in range(4)},
                     **{f"hfss_k{k}": R2["lin_err_hfss"][s][k] for k in range(4)}) for s in R2["lin_err_model"]]
        L += [_t(rows, list(rows[0].keys()), {c: ".2f" for c in rows[0]}), "",
              "- The Normal→AD change replaces 12–21 mm of gray/white matter by CSF (|d eps| up to 20). "
              "That is far outside the Born regime, so the linear model is not a quantitative "
              "description of any stage.", ""]
        rad = R2["radial"]
        L += ["### 4.3 Radial (spherically symmetric) inversion — 2 mm shells, d eps_r and d eps''", "",
              f"Tikhonov with GCV and L-curve lambda, and 1-D TV (lambda tuned on Mild synthetic = "
              f"{rad['lam_tv']:.2g}). Errors are relative L2 against the true shell-averaged profile. "
              "corr = Pearson correlation with the truth.", ""]
        rows = []
        for key, v in rad["err"].items():
            ds, s = key.split("|")
            for meth, e in v.items():
                rows.append(dict(data=ds, stage=s, method=meth, **e))
        L += [_t(rows, ["data", "stage", "method", "rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"],
                 {c: ".2f" for c in ["rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"]}), ""]
        rd = rad["resolution_diag"]
        r = rad["r"]
        good_r = r[rd["eps_r"] >= 0.5]
        good_p = r[rd["eps_pp"] >= 0.5]
        L += [f"Model-resolution matrix (whitened, GCV lambda on Mild): diag ≥ 0.5 for d eps_r at "
              f"r ∈ {_ranges(good_r)} mm and for d eps'' at r ∈ {_ranges(good_p)} mm. "
              f"Largest diag: {rd['eps_r'].max():.2f} / {rd['eps_pp'].max():.2f}. "
              f"Number of singular values within 1e-3 of the largest: "
              f"{int(np.sum(rad['singular_values'] > 1e-3 * rad['singular_values'][0]))} of "
              f"{len(rad['singular_values'])}. Only the outermost shell (82–83.5 mm) is resolved; "
              "below it the radial inversion returns a smeared, strongly damped copy. 1-D TV (a "
              "piecewise-constant prior that matches the true layered profile) is the only method "
              "that recovers a correlated shape on synthetic data. Figure: `figures/i2_resolution.png`, "
              "`figures/i2_radial_inversion.png`.", ""]
        vx = R2["voxel"]
        L += ["### 4.4 Voxel inversion — 3 mm voxels in r < 83.5 mm", "",
              f"{vx['n_vox']} voxels × (d eps_r, d eps''), 21 pairs × 6 frequencies (3.2–4.2 GHz). "
              f"Tikhonov-GCV and L1 sparsity (FISTA, lambda tuned on Mild synthetic).", ""]
        rows = []
        for key, v in vx["err"].items():
            ds, s = key.split("|")
            for meth, e in v.items():
                rows.append(dict(data=ds, stage=s, method=meth, **e))
        L += [_t(rows, ["data", "stage", "method", "rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"],
                 {c: ".2f" for c in ["rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"]}), "",
              "- Tikhonov-GCV on the HFSS data (radial and voxel): the HFSS data are inconsistent with "
              "the surrogate Jacobian (§3, §4.2). GCV then picks a tiny lambda and the solution "
              "blows up (errors of 10–2000×). The L-curve lambda returns an almost-zero image "
              "instead. Neither is an image of the change.",
              "- L1 (sparsity) with lambda tuned on Mild: the lambda with the lowest error on Mild "
              "gave the all-zero image. No sparse voxel pattern recovered the true change better than "
              "zero, so L1 reports nothing (rel. err 1.00, corr undefined).",
              "", "Point-spread functions (columns of the resolution matrix, lambda = GCV on Mild "
              "synthetic) for voxels on the x-axis (z = 0, azimuth of T1) at radius r_mm. "
              "diag = the fraction of a unit change recovered in place. peak_at = where its image "
              "actually peaks:", ""]
        L += [_t(vx["psf"], ["r_mm", "diag", "peak_at_mm", "n_vox_above_half", "extent_mm"], {"diag": ".2e"}), "",
              "Figure: `figures/i2_voxel.png`.", ""]

    # ------------------------------------------------------------------ I3
    if "i3" in R:
        R3 = R["i3"]
        fig_i3(R3)
        L += ["## 5. I3 — targeted model-based nonlinear inversion (9 parameters)", "",
              "Unknowns: r_gray, r_white, r_hip, eps/sigma of gray, white and CSF (hippocampus "
              "material tied to gray). Bounded by a sigmoid map; MINPACK Levenberg–Marquardt; 6 "
              "starts (the Normal truth + 5 random). Data: ring-mode dS_k, k = 0..3, 51 frequencies, "
              "whitened by the typical-noise std. Uncertainty = CRLB from the whitened Jacobian at "
              "the solution.", ""]
        L += ["### 5.1 Identifiability at the truth (synthetic, calB scale, typical noise)", ""]
        for s in REPORTED:
            idf = R3["ident"][s]
            rows = [dict(param=f"{n} [{u}]" if u else n, truth=float(t), change=float(c), crlb_sd=float(sdv),
                         verdict=v) for n, u, t, c, sdv, v in
                    zip(NAMES, UNITS, [*_theta(s)], idf["change"], idf["sd"], idf["verdict"])]
            L += [f"**{s}** (Fisher condition number {idf['cond']:.1e})", "",
                  _t(rows, ["param", "truth", "change", "crlb_sd", "verdict"],
                     {"truth": ".3g", "change": ".3g", "crlb_sd": ".2g"}), ""]
            ev, vec = idf["fisher_eig"], idf["fisher_vec"]
            weak = vec[:, 0]
            L += ["Weakest Fisher direction (smallest eigenvalue "
                  f"{ev[0]:.1e}): " + ", ".join(f"{n} {w:+.2f}" for n, w in zip(NAMES, weak) if abs(w) > 0.2)
                  + "; strongest: " + ", ".join(f"{n} {w:+.2f}" for n, w in zip(NAMES, vec[:, -1]) if abs(w) > 0.2),
                  ""]
        L += ["### 5.2 Fits", "",
              "t_csf = 83.5 − r_gray (true: Normal 0.5, Mild 12.95, Moderate 17.45, Severe 21.25 mm). "
              "chi2/dof ≈ 1 means the model explains the data to within the noise.", ""]
        rows = []
        for f_ in R3["fits"]:
            row = dict(dataset=f_["dataset"], stage=f_["stage"], chi2_dof=f_["chi2_per_dof"],
                       t_csf=f"{f_['csf_thickness']:.1f} ± {f_['csf_thickness_sd']:.1f}",
                       t_csf_true=R_CSF - f_["truth"][0])
            for i, n in enumerate(NAMES[1:], 1):
                row[n] = f"{f_['theta'][i]:.3g} ({f_['truth'][i]:.3g})"
            rows.append(row)
        L += [_t(rows, ["dataset", "stage", "chi2_dof", "t_csf", "t_csf_true"] + NAMES[1:],
                 {"chi2_dof": ".3g", "t_csf_true": ".2f"}), "",
              "(parameter: estimate (truth))", ""]
        syn = [f_ for f_ in R3["fits"] if f_["dataset"] == "synthetic (same model)"]
        dev = [f"{f_['stage']} {abs(f_['theta'][7] - f_['truth'][7]) / max(f_['sd'][7], 1e-9):.1f}σ"
               for f_ in syn]
        hf = [f_["chi2_per_dof"] for f_ in R3["fits"] if f_["dataset"].startswith("HFSS")
              and f_["stage"] != "noise-only"]
        L += ["Reading the fits:",
              f"- **Synthetic, same model (inverse crime, noise only):** every fit reaches chi2/dof ≈ 1, "
              "yet CSF thickness and the deeper parameters land far from the truth. Many different "
              "layered heads explain the same data: the degeneracy seen in §5.1. eps_csf, the "
              "parameter §5.1 calls determined, deviates from its truth by " + ", ".join(dev)
              + " (|est − truth| / CRLB at the fit). It is recovered within its uncertainty for "
              "the AD stages. On noise-only data, however, the fit settles in a different minimum, "
              "because the misfit surface is multimodal. Only the effective material of the "
              "outermost layer is measured; its geometry is not.",
              f"- **HFSS:** chi2/dof {min(hf):.0f}–{max(hf):.0f}. The model cannot reproduce the "
              "HFSS dS (antenna-model mismatch, §3). Parameters sit on bounds and change with the "
              "calibration choice (calA vs calB), so they carry no physical meaning.",
              "- **Antenna-mismatch test:** data made with the patch-aperture antenna and inverted "
              "with the point-dipole model give chi2/dof 3–8 and wrong CSF thickness. A modest "
              "antenna-model error alone is enough to break I3.", ""]
        L += ["### 5.3 CSF thickness as a feature vs the k = 3 scalar metric", "",
              "One LM fit per noisy draw, started at the Normal truth. Threshold tuned on Mild vs "
              "Normal draws; tested on Moderate + Severe vs fresh Normal draws. k3 metric = full-band "
              "mean opposite-antenna power in dB (M5.C3; lower → AD). For k3, tau is printed "
              "sign-flipped: the threshold is −tau dB.", ""]
        rows = []
        for ds, c in R3["classify"].items():
            for feat in ("t_csf", "k3"):
                rows.append(dict(data=ds, feature=feat, **c[feat]))
        L += [_t(rows, ["data", "feature", "tau", "sens", "spec", "bal_acc", "macro_f1"],
                 {c: ".3f" for c in ["tau", "sens", "spec", "bal_acc", "macro_f1"]}), "",
              "Figure: `figures/i3_csf_thickness.png`.", ""]

    L += _verdict_section(R)
    L += _array_section()

    # ------------------------------------------------------------------ metrics CSV
    rows = []
    if write_csv:
        if "i1" in R:
            for m in ("DAS", "DMAS", "MVDR"):
                det = R["i1"]["detect"]
                d = {"Mild": det[f"layered|{m}|Mild"]["stage"], "noise": det[f"layered|{m}|Mild"]["noise"],
                     "noise_test": det[f"layered|{m}|Mild"]["noise_test"],
                     **{s: det[f"layered|{m}|{s}"]["stage"] for s in REPORTED}}
                b = R["i1"]["best"][f"layered|{m}"]
                acc = _metric_row(f"I1-{m}", f"peak of whitened multistatic {m} image of dS (layered "
                                  f"straight rays, t_ant {b['t_ant_ns']} ns)", d,
                                  "detection of any change vs Normal baseline; no localisation claim; "
                                  "needs a Normal baseline of the same head", cfg=cfg)
                rows.append(dict(method=f"I1-{m}", **acc))
        if "i2" in R:
            src = "SURROGATE model fields" if "SURROGATE" in R["i2"]["field_source"] else "HFSS fields"
            acc = _metric_row("I2-radial", "|recovered d eps| in 70-83.5 mm, radial Tikhonov (2 mm shells)",
                              R["i2"]["radial"]["detect"], f"{src}; kappa(f) and lambda from Mild", cfg=cfg)
            rows.append(dict(method="I2-radial", **acc))
            acc = _metric_row("I2-voxel", "rms recovered d eps in 70-83.5 mm, voxel Tikhonov (3 mm)",
                              R["i2"]["voxel"]["detect"], f"{src}; kappa(f) and lambda from Mild", cfg=cfg)
            rows.append(dict(method="I2-voxel", **acc))
        if "i3" in R:
            for ds, c in R["i3"]["classify"].items():
                feats = c["feats"]
                d = {"Mild": feats["Mild"]["t_csf"], "noise": feats["Normal_train"]["t_csf"],
                     "noise_test": feats["Normal_test"]["t_csf"],
                     **{s: feats[s]["t_csf"] for s in REPORTED}}
                acc = _metric_row("I3", "recovered CSF thickness 83.5 - r_gray (9-param LM, 1 start)", d,
                                  f"{ds} data; forward model = layered sphere + point dipoles; "
                                  + ("calA (Normal) calibration" if ds == "HFSS" else "model-generated dS + noise (inverse crime)"),
                                  sim_set=None if ds == "HFSS" else "model-synthetic-pointdipole", cfg=cfg)
                rows.append(dict(method=f"I3 ({ds})", **acc))
        L += ["## 8. Rows written to `results/imaging/metrics_imaging.csv`", "",
              "Binary detection Normal | AD with the method's scalar output (threshold tuned on Mild, "
              "tested on Moderate + Severe and fresh Normal draws, typical noise). These rows measure "
              "**detection of a change**, not localisation.", ""]
        L += [_t(rows, ["method", "tau", "sens", "spec", "acc", "bal_acc", "macro_f1"],
                 {c: ".3f" for c in ["tau", "sens", "spec", "acc", "bal_acc", "macro_f1"]}), ""]
    (OUT / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    _summary_json(R)


def _rmin(r, v, thr):
    """Smallest radius r0 such that v >= thr for all r >= r0 (r ascending); nan if none."""
    ok = v >= thr
    if not ok[-1]:
        return float("nan")
    i = len(r) - 1
    while i > 0 and ok[i - 1]:
        i -= 1
    return float(r[i])


def _theta(s):
    from .study_i3 import theta_of
    return theta_of(HeadParams.stage(s))


def _ranges(r):
    if len(r) == 0:
        return "∅"
    out, start, prev = [], r[0], r[0]
    for x in r[1:]:
        if x - prev > 2.01:
            out.append(f"{start:.0f}–{prev:.0f}")
            start = x
        prev = x
    out.append(f"{start:.0f}–{prev:.0f}")
    return ", ".join(out)


def _verdict_section(R):
    L = ["## 6. Verdict — what 6 antennas on one ring at 3.2–4.2 GHz can and cannot localise", ""]
    can, cannot = [], []
    if "i1" in R:
        st = R["i1"]["stages"]
        scr = [v["scr_db"] for k, v in st.items() if k.split("|")[1] in ("DAS", "DMAS") and k.split("|")[2] in REPORTED]
        pk = sorted({v["peak_r_mm"] for k, v in st.items() if k.split("|")[2] in REPORTED})
        can.append(f"**Detect that something changed** relative to a Normal baseline of the same head. "
                   f"DAS/DMAS image energy sits {min(scr):.0f}–{max(scr):.0f} dB above the noise-only "
                   "image for Moderate/Severe, in every noisy draw (§2, §8). This is detection, not "
                   "localisation.")
        cannot.append(f"**Place the change with radar imaging (I1).** Every method and delay model puts "
                      f"the radial peak at r = {', '.join(f'{p:.0f}' for p in pk)} mm. That is the centre, "
                      "where all 21 pair delays coincide for a ring of equidistant antennas: a symmetric-"
                      "array artefact. The true change lies at 57–83.5 mm. The depth scale also hinges "
                      "on an antenna delay the data cannot fix (§1: ~3 ns in transmission, ~0 in "
                      "reflection). The ideal point target has an elevation width of several cm (§2 "
                      "table).")
    if "i2" in R and "snr_radial" in R["i2"]:
        sn = R["i2"]["snr_radial"]
        best = np.max(sn["snr"][4], -1)
        med = np.median(sn["snr"][4], -1)
        r1 = _rmin(sn["r"], best, 1.0)
        can.append(f"**See the outer ~{83.5 - r1:.0f} mm of brain, and only near the antennas.** A 1 cm³ "
                   f"change of |d eps| = 10 reaches SNR ≥ 1 down to r ≈ {r1:.0f} mm in the best direction. "
                   f"In the median direction the SNR is ≤ {med.max():.2f} at every depth (§4.1, surrogate "
                   "fields, Mild-calibrated scale).")
        cannot.append(f"**See deep structures.** The hippocampus (r < 25 mm) and white matter beyond "
                      f"~{83.5 - r1:.0f} mm under the cortex are invisible: SNR ≈ "
                      f"{float(np.interp(20.0, sn['r'], best)):.2f} at r = 20 mm even in the best "
                      "direction. The hippocampal shrinkage cannot be recovered by any method here.")
    if "i2" in R:
        rd = R["i2"]["radial"]["resolution_diag"]
        cannot.append(f"**Resolve depth structure (I2).** In the radial inversion only the outermost "
                      f"shell (82–83.5 mm) has resolution-matrix diagonal ≥ 0.5 (max "
                      f"{max(rd['eps_r'].max(), rd['eps_pp'].max()):.2f}). Voxel point-spread functions "
                      "have diagonals ~1e-5 and peak tens of mm from the true voxel. Voxel images on HFSS "
                      "data are noise or zero.")
    if "i3" in R:
        idf = {s: R["i3"]["ident"][s]["verdict"] for s in REPORTED}
        det = sorted({n for s in REPORTED for n, v in zip(NAMES, idf[s]) if v == "determined"})
        can.append(f"**Estimate the effective material of the layer right under the skull.** Of the 9 "
                   f"phantom parameters, only {', '.join(det) or 'none'} are identifiable (CRLB at the "
                   "truth, synthetic data, typical noise). The array measures one surface impedance, "
                   "not a layered structure.")
        hf = [f_ for f_ in R["i3"]["fits"] if f_["dataset"].startswith("HFSS") and f_["stage"] in REPORTED]
        chis = [f_["chi2_per_dof"] for f_ in hf]
        cannot.append("**Recover CSF thickness (atrophy), gray/white radii or deeper materials (I3).** "
                      "They are not identifiable even with a perfect forward model (CRLB > prior "
                      "range). On HFSS data the model cannot fit the data (chi2/dof "
                      f"{min(chis):.0f}–{max(chis):.0f}; §3). The recovered CSF thickness does not "
                      "separate the classes; the k = 3 scalar metric does (§5.3).")
    cannot.append("**Lateral / lobe localisation.** Impossible in this phantom by construction: the "
                  "head and every change are spherically symmetric, so any azimuthal structure in an "
                  "image is an array artefact. With six antennas on one ring it would also be "
                  "impossible in an anatomical head (§7).")
    cannot.append("**Separate AD stages.** The model predicts Severe dS ≈ 2× Mild; HFSS shows "
                  "≈ 1.3–1.4×. AD-vs-AD differences are 0.5–3× the port asymmetry, and the mesh noise "
                  "is unmeasured: **unverified against mesh noise**.")
    L += ["**Can (in these simulations, under typical noise):**", ""]
    L += [f"{i}. {c}" for i, c in enumerate(can, 1)]
    L += ["", "**Cannot:**", ""]
    L += [f"{i}. {c}" for i, c in enumerate(cannot, 1)]
    L += ["", "**Imaging vs the scalar metric.** No imaging or inversion method recovered the known "
          "changes better than the k = 3 band-averaged power. That scalar remains the best "
          "Normal-vs-AD discriminator. Section 1 explains why it works: the opposite-antenna wave "
          "skims the head surface, and the near-surface CSF/cortex change is exactly what it samples.",
          ""]
    return L


def _array_section():
    from .mie import C0, EPS0
    # gray matter: this project's static value at 3.5 GHz; lower frequencies: approximate
    # IT'IS / Gabriel values (flagged)
    gm = [(1.0e9, 52.3, 0.99), (1.5e9, 51.1, 1.21), (2.0e9, 50.1, 1.43), (3.5e9, 47.7, 2.42)]
    rows = []
    for f, e, s in gm:
        w = 2 * np.pi * f
        n = np.sqrt(e - 1j * s / (w * EPS0))
        att = 8.686 * w / C0 * abs(n.imag) / 100                     # dB/cm, one way
        lam = C0 / f / n.real * 1e3
        rows.append(dict(f_GHz=f / 1e9, eps_r=e, sigma=s, lambda_mm=lam, att_dB_cm=att,
                         two_way_loss_3cm_dB=2 * 3 * att, xrange_res_mm=lam / 2))
    bw = [dict(band="3.2-4.2 GHz (this array)", B_GHz=1.0), dict(band="2.8-4.2 GHz (re-run)", B_GHz=1.4),
          dict(band="0.7-2.2 GHz", B_GHz=1.5), dict(band="0.5-2.5 GHz", B_GHz=2.0)]
    for b in bw:
        b["range_res_mm"] = C0 / (2 * b["B_GHz"] * 1e9 * np.sqrt(45.0)) * 1e3
    L = ["## 7. What array would lobe-level localisation need? (for the CST voxel model)", "",
         "Target: tell apart changes of order 2–3 cm in extent located in different lobes, at cortical "
         "depths 1–4 cm under the skull, in a head that is **not** spherically symmetric. That needs "
         "three things this array lacks: lateral (angular) sampling, elevation sampling, and depth "
         "(range) information that is not killed by loss.", "",
         "**Loss and wavelength in gray matter** (3.5 GHz: this project's value; 1–2 GHz: approximate "
         "IT'IS/Gabriel values, flagged):", "",
         _t(rows, ["f_GHz", "eps_r", "sigma", "lambda_mm", "att_dB_cm", "two_way_loss_3cm_dB", "xrange_res_mm"],
            {"f_GHz": ".1f", "lambda_mm": ".1f", "att_dB_cm": ".1f", "two_way_loss_3cm_dB": ".0f",
             "xrange_res_mm": ".0f"}), "",
         "**Range resolution** c/(2B·sqrt(eps)), eps ≈ 45:", "",
         _t(bw, ["band", "B_GHz", "range_res_mm"], {"range_res_mm": ".0f"}), "",
         "Reasoning and minimum requirements:",
         "1. **Frequency.** At 3.5 GHz, two-way loss to 3 cm of cortex is ~35 dB on top of the skin/skull "
         "mismatch. That is why every path here sees only the outer ~1–2 cm (§4.1). A band of about "
         "0.7–2.2 GHz (2–3 dB/cm, λ ≈ 3–4 cm in tissue) roughly halves the loss per cm and keeps a "
         "half-wavelength lateral resolution of ~1.5–2 cm. Imaging systems for stroke use this band "
         "for the same reason.",
         "2. **Bandwidth.** ≥ 1.5 GHz (fractional bandwidth ≳ 100 %) for ~1.5 cm range resolution. "
         "This needs genuinely wideband antennas (not a resonant patch whose ~3 ns transmission group "
         "delay (§1) blurs range), plus per-antenna de-embedding measured on a phantom.",
         "3. **Angular sampling.** Around a ~55 cm head circumference, lobe-scale lateral resolution "
         "(~2 cm) needs element spacing ≲ λ_medium/2. With a coupling medium (eps ≈ 20–40) at "
         "≤ 2 GHz that is 16–24 antennas per ring. Six antennas give only 4 independent ring modes "
         "for a symmetric target, and 21 pairs at most otherwise.",
         "4. **Elevation.** A single ring cannot place anything in z. §2's point-target test gives an "
         "elevation width of several cm even for an ideal scatterer. At least 2–3 rings (or a "
         "helmet), with ~2–3 cm vertical spacing over the fronto-parietal-temporal region: "
         "**≈ 32–64 antennas** in total, multistatic, all pairs measured.",
         "5. **Coupling medium / matching.** An immersion or matching layer (eps ≈ 20–40, low loss) "
         "between antennas and skin suppresses the skin reflection (the dominant |S_ii|) and the "
         "around-the-head air path, which here carries the k = 3 signal (§1). This forces energy "
         "through the skull.",
         "6. **Forward model.** Model-based inversion needs each antenna's own incident field in the "
         "head (HFSS/CST field exports per port, as planned for I2), not a point-dipole idealisation. "
         "§3 shows that the idealisation fails even on this simple phantom. Then use a DBIM/Gauss–Newton "
         "loop with an anatomical (MRI-template) prior. Microwave data alone will not give "
         "voxel-level lobe maps; a regional parameterisation (per-lobe d eps, like I3 here) is "
         "realistic.",
         "7. **Calibration against mesh noise.** Lobe-level differences are small. Between-mesh and "
         "repeat-measurement noise must be measured first (Normal mesh-repeat), because the "
         "port-asymmetry floor here is already 0.5–3× the AD-vs-AD differences.", ""]
    return L


def _summary_json(R):
    out = {}
    if "paths" in R:
        out["paths"] = R["paths"]
    if "i1" in R:
        out["i1_stages"] = R["i1"]["stages"]
        out["i1_best"] = R["i1"]["best"]
    if "val" in R:
        out["val_table"] = R["val"]["table"]
        out["pol"] = R["val"]["pol"]
    if "i2" in R:
        out["i2_depth"] = R["i2"]["sens_depth"]
        out["i2_block"] = R["i2"]["block"]
        out["i2_radial_err"] = R["i2"]["radial"]["err"]
        out["i2_voxel_err"] = R["i2"]["voxel"]["err"]
    if "i3" in R:
        out["i3_fits"] = [{k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in f.items()}
                          for f in R["i3"]["fits"]]
        out["i3_classify"] = {ds: {k: v for k, v in c.items() if k != "feats"} for ds, c in R["i3"]["classify"].items()}
    (OUT / "summary.json").write_text(json.dumps(out, indent=1, default=lambda o: o.tolist()
                                                  if isinstance(o, np.ndarray) else str(o)), encoding="utf-8")
