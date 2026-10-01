"""Report section 4 and figures for I2 with the HFSS field exports (study_i2_hfss)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .common import FIG, R_CSF  # noqa: E402
from .study_i2_hfss import Z_RING  # noqa: E402

REPORTED = ("Moderate", "Severe")
C_ST = {"Mild": "#4C78A8", "Moderate": "#F58518", "Severe": "#E45756"}


def _circle(ax, r, **kw):
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(r * np.cos(t), r * np.sin(t), **kw)


def _rmin(r, v, thr):
    ok = v >= thr
    if not ok[-1]:
        return float("nan")
    i = len(r) - 1
    while i > 0 and ok[i - 1]:
        i -= 1
    return float(r[i])


def _first_below(r, v, thr):
    """Largest radius (scanning inward from the surface) where v drops below thr."""
    for i in range(len(r) - 1, -1, -1):
        if v[i] < thr:
            return float(r[i])
    return float("nan")


def _ranges(r):
    if len(r) == 0:
        return "none"
    out, start, prev = [], r[0], r[0]
    for x in r[1:]:
        if x - prev > 2.01:
            out.append(f"{start:.0f}–{prev:.0f}")
            start = x
        prev = x
    out.append(f"{start:.0f}–{prev:.0f}")
    return ", ".join(out)


# ----------------------------------------------------------------------------------------------
def figures(R2):
    # sensitivity maps (relative per k) and absolute detectability (all pairs)
    fig, ax = plt.subplots(2, 5, figsize=(17, 7))
    for i, (name, lab) in enumerate((("ring", f"ring plane z = {R2['maps']['ring']['plane_value_mm']:+.0f} mm"),
                                     ("vertical", "plane x = 0 (through T1 and T4)"))):
        M = R2["maps"][name]
        u, v, mask = M["u"], M["v"], M["mask"]
        for k in range(5):
            img = np.full(mask.shape, np.nan)
            if k < 4:
                img[mask] = 10 * np.log10(M["sens"][k] / M["sens"][k].max())
                im = ax[i, k].imshow(img.T, origin="lower", extent=[u[0], u[-1], v[0], v[-1]],
                                     vmin=-40, vmax=0, cmap="viridis")
                ax[i, k].set_title(f"k={k}: sum|J| (dB rel. max)\n{lab}", fontsize=8)
            else:
                img[mask] = np.log10(np.maximum(M["snr_kappa"][4], 1e-4))
                im2 = ax[i, k].imshow(img.T, origin="lower", extent=[u[0], u[-1], v[0], v[-1]],
                                      vmin=-3, vmax=1, cmap="magma")
                ax[i, k].set_title(f"log10 SNR, 1 cm³ |dε|=10, all pairs\n(κ-calibrated) {lab}", fontsize=8)
            if name == "ring":
                _circle(ax[i, k], np.sqrt(83.5 ** 2 - Z_RING ** 2), color="w", lw=0.6)
            else:
                _circle(ax[i, k], 83.5, color="w", lw=0.6)
            ax[i, k].set_xticks([])
            ax[i, k].set_yticks([])
    fig.colorbar(im, ax=ax[:, :4], shrink=0.6, label="dB rel. max (per k)")
    fig.colorbar(im2, ax=ax[:, 4], shrink=0.6, label="log10 SNR")
    fig.suptitle("I2 with HFSS fields (Normal design, 3.4/3.6/3.8 GHz): where can the array see?")
    fig.savefig(FIG / "i2h_sensitivity_maps.png", dpi=110)
    plt.close(fig)

    sn = R2["snr_radial"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for j, (key, lab) in enumerate((("snr", "absolute 1 V Born scale"), ("snr_kappa", "κ(f) calibrated on Mild"))):
        for k, name in enumerate(["k=0", "k=1", "k=2", "k=3", "all pairs"]):
            l = ax[j].semilogy(sn["r"], np.max(sn[key][k], -1), lw=2.5 if k == 4 else 1.2, label=f"{name} best dir.")
            ax[j].semilogy(sn["r"], np.median(sn[key][k], -1), lw=2.5 if k == 4 else 1.2, ls=":",
                           color=l[0].get_color(), label=f"{name} median" if k == 4 else None)
        ax[j].axhline(1, color="k", lw=0.6)
        ax[j].axvline(83.5, color="k", lw=0.5)
        ax[j].set_title(f"SNR of a 1 cm³ blob, |dε| = 10 ({lab})", fontsize=9)
        ax[j].set_xlabel("radius (mm)")
    ax[0].set_ylabel("SNR (typical noise, both measurements)")
    ax[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "i2h_detectability_radial.png", dpi=120)
    plt.close(fig)

    kp = R2["k3_path"]
    fig, ax = plt.subplots(1, 4, figsize=(19, 4.8))
    px = kp["plane_x0"]
    for j, (q, lab) in enumerate((("E1", "|E_T1| (dB rel. max)"), ("prod", "|E_T1 · E_T4| (dB rel. max)"))):
        A = np.where(np.isfinite(px[q]), px[q], np.nan)
        img = 20 * np.log10(A / np.nanmax(A)) if q == "E1" else 10 * np.log10(A / np.nanmax(A))
        im = ax[j].imshow(img.T, origin="lower", extent=[px["u"][0], px["u"][-1], px["v"][0], px["v"][-1]],
                          vmin=-60, vmax=0, cmap="inferno")
        for r_, c_ in ((88, "w"), (83.5, "c"), (97.55, "w")):
            _circle(ax[j], r_, color=c_, lw=0.5, ls="--" if r_ > 90 else "-")
        ax[j].set_title(f"{lab}, plane x = 0, 3.6 GHz (wide export)", fontsize=8)
        ax[j].set_xlabel("y (mm)")
        ax[j].set_ylabel("z (mm)")
        fig.colorbar(im, ax=ax[j], shrink=0.75)
    pr = kp["plane_ring"]
    A = pr["prod"]
    im = ax[2].imshow((10 * np.log10(A / np.nanmax(A))).T, origin="lower",
                      extent=[pr["u"][0], pr["u"][-1], pr["v"][0], pr["v"][-1]], vmin=-60, vmax=0, cmap="inferno")
    _circle(ax[2], np.sqrt(88 ** 2 - pr["z_mm"] ** 2), color="w", lw=0.5)
    _circle(ax[2], np.sqrt(83.5 ** 2 - pr["z_mm"] ** 2), color="c", lw=0.5)
    ax[2].set_title(f"|E_T1 · E_T4| (dB), ring plane z = {pr['z_mm']:.0f} mm", fontsize=8)
    fig.colorbar(im, ax=ax[2], shrink=0.75)
    ax[3].plot(kp["t"], kp["arc_dB"], label="arc over the top, r = 91 mm (air)")
    ax[3].plot(kp["t"], kp["chord_dB"], label="straight chord T1→T4 (through head)")
    ax3 = ax[3].twinx()
    ax3.plot(kp["t"], kp["chord_r"], "k:", lw=0.8)
    ax3.set_ylabel("chord radius (mm, dotted)")
    ax[3].set_xlabel("fraction of the way from T1 to T4")
    ax[3].set_ylabel("|E_T1| (dB rel. arc start)")
    ax[3].legend(fontsize=7)
    ax[3].set_title("Field of T1 along two routes to T4", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "i2h_k3_path.png", dpi=110)
    plt.close(fig)

    rad = R2["radial"]
    r = rad["r"]
    n = len(r)
    fig, ax = plt.subplots(2, 4, figsize=(17, 7), sharex=True)
    for j, key in enumerate(("synthetic-linear", "HFSS", "noise-only")):
        for s in (REPORTED if key != "noise-only" else ("noise",)):
            kk = key if key == "noise-only" else f"{key}|{s}"
            sol = rad["sol"][kk]
            col = C_ST.get(s, "k")
            for i, sl in enumerate((slice(0, n), slice(n, 2 * n))):
                ax[i, j].plot(r, sol["tikhonov-lcurve"][sl], color=col, label=f"{s} Tikh. L-curve")
                ax[i, j].plot(r, sol["tv"][sl], color=col, ls="--", label=f"{s} TV")
                if key != "noise-only":
                    ax[i, j].plot(r, rad["truth"][s][sl], color=col, lw=2.5, alpha=0.35, label=f"{s} truth")
        ax[0, j].set_title(key, fontsize=10)
        ax[1, j].set_xlabel("radius (mm)")
    ax[0, 0].set_ylabel("d eps_r")
    ax[1, 0].set_ylabel("d eps'' (3.7 GHz)")
    ax[0, 0].legend(fontsize=6)
    ax[0, 3].plot(r, rad["resolution_diag"]["eps_r"], label="d eps_r")
    ax[0, 3].plot(r, rad["resolution_diag"]["eps_pp"], label="d eps''")
    ax[0, 3].axhline(0.5, color="k", lw=0.5)
    ax[0, 3].set_title("resolution-matrix diagonal", fontsize=10)
    ax[0, 3].legend(fontsize=7)
    vx = R2["voxel"]
    ax[1, 3].plot([p["r_mm"] for p in vx["psf"]], [p["peak_offset_mm"] for p in vx["psf"]], "o-")
    ax[1, 3].set_ylabel("voxel PSF peak offset (mm)")
    ax[1, 3].set_xlabel("voxel radius (mm)")
    fig.suptitle("I2 radial inversion (2 mm shells) and voxel PSFs, HFSS Green's function")
    fig.tight_layout()
    fig.savefig(FIG / "i2h_inversions.png", dpi=110)
    plt.close(fig)

    vox = vx["vox"]
    nv = len(vox)
    fig, ax = plt.subplots(2, 3, figsize=(13, 8))
    cases = [("synthetic-linear|Severe", "tikhonov-gcv"), ("HFSS|Severe", "tikhonov-gcv"),
             ("noise-only", "tikhonov-gcv")]
    for j, (key, meth) in enumerate(cases):
        x = vx["sol"][key][meth][:nv]
        lim = np.nanmax(np.abs(x)) or 1.0
        for i, (sel, a_, b_, lab) in enumerate(((np.abs(vox[:, 2] - Z_RING) < 1.6, 0, 1, "ring plane"),
                                                (np.abs(vox[:, 0]) < 1.6, 1, 2, "x = 0"))):
            sc = ax[i, j].scatter(vox[sel, a_], vox[sel, b_], c=x[sel], s=10, marker="s", cmap="RdBu_r",
                                  vmin=-lim, vmax=lim)
            ax[i, j].set_aspect("equal")
            ax[i, j].set_title(f"{key} {meth}, {lab} (d eps_r)", fontsize=8)
            ax[i, j].set_xticks([])
            ax[i, j].set_yticks([])
            fig.colorbar(sc, ax=ax[i, j], shrink=0.7)
    fig.suptitle("I2 voxel inversion (3 mm grid nodes), HFSS Green's function")
    fig.tight_layout()
    fig.savefig(FIG / "i2h_voxel.png", dpi=110)
    plt.close(fig)


# ----------------------------------------------------------------------------------------------
def section(R2, t, label, R2_surrogate=None):
    """Markdown lines of report section 4. t = the table helper of report.py."""
    L = ["## 4. I2 — HFSS numerical Green's function: sensitivity maps and linearised inversion", "",
         label, ""]
    L += ["**Source.** HFSS 2024.2 calculator exports of complex E for the Normal design (project "
          "`new`, design `Healthy`), one file per driven terminal (1 V incident, 0°, others matched "
          "50 Ω, port post-processing off), at 3.4 / 3.6 / 3.8 GHz on a 3 mm grid (−90…90 mm), plus "
          "a ±120 mm / 4 mm export of T1 at 3.6 GHz. Background S-parameters: the matching v2 Normal "
          "`new_Healthy.s6p`. All Jacobians therefore have 3 frequency rows (the S data have 281).", ""]
    # ---- checks
    ck = R2["checks"]
    full = all(c.get("full_grid") is True for c in ck)
    L += ["### 4.0 Field-file checks", "",
          f"- All {len(ck)} files present: {all(c['present'] for c in ck)}. Every file: "
          f"{ck[0].get('shape')} nodes (= 61³ rows: {all(c.get('rows') == 61 ** 3 for c in ck)}), full "
          f"regular grid: {full}, z varies fastest: {all(c.get('z_fastest') for c in ck)}.",
          "- NaN nodes per file: " + ", ".join(sorted({str(c.get('n_nan')) for c in ck}))
          + "; radii " + ", ".join(sorted({c.get('nan_r_mm', '-') for c in ck}))
          + " mm (antenna metal). Finite everywhere inside r < 88 mm: "
          + f"{all(c.get('finite_inside_r88') for c in ck)}.",
          "- Re/Im pairing (median |div E|·h / |E| over air nodes; a wrong pairing is not divergence-"
          "free): " + "; ".join(f"{k}: interleaved {v['interleaved']:.3f} vs blocked {v['blocked']:.3f}"
                                for k, v in R2["divergence"].items())
          + ". The stated pairing (x y z, Ex_re Ex_im, Ey_re Ey_im, Ez_re Ez_im) is the one used. "
          "The residual is the 3 mm finite-difference error near the antennas.", ""]
    L += ["**Antennas located from their own fields** (|E|-weighted centroid of the strongest air "
          "nodes at r = 89–93 mm; θ-fraction = |E·θ̂| / (|E·θ̂| + |E·φ̂|) there):", "",
          t(R2["antennas"], ["T", "azimuth_deg", "field_centroid_polar_deg", "theta_fraction"],
            {"azimuth_deg": ".1f", "field_centroid_polar_deg": ".1f", "theta_fraction": ".2f"}), "",
          "- This settles two OPEN items of the model card. The ring is at **+z**: every centroid "
          "is in the upper hemisphere (≈55°; the field centroid sits slightly above the 60.5° feed, "
          "which is used for geometry). T1…T6 are consecutive at 60° steps, with **T1 at azimuth "
          "≈ −90°** (not 0° as assumed in the I1/I3 geometry; immaterial for S of a symmetric head, "
          "but it means the plane through T1 and T4 is x = 0).",
          "- Near-field polarisation is mixed, ≈ 65 % θ̂ / 35 % φ̂ in amplitude. The point-dipole "
          "model in §3/§5 had chosen φ̂ from the Normal couplings. Neither pure orientation is right; "
          "this is part of the antenna-model mismatch found in §3.", ""]
    L += ["**Ring symmetry at field level** (inside r < 88 mm). Relative rms difference between an "
          "antenna's field and its opposite antenna's field rotated by 180° about z; rms amplitude "
          "of each antenna relative to the mean of all six:", "",
          t(R2["symmetry"], ["f_GHz", "pair", "rel_rms_diff"], {"f_GHz": ".1f", "rel_rms_diff": ".3f"}), "",
          "Amplitude ratios at 3.6 GHz: " + ", ".join(f"T{a['T']} {a['rms_rel_mean']:.3f}"
                                                     for a in R2["amplitude"] if abs(a["f_GHz"] - 3.6) < 1e-6)
          + ". The fields are symmetric to 11–16 % (rms), the field-level counterpart of the "
          "S-parameter port asymmetry. Any image feature below that level is not trustworthy.", ""]
    # ---- scale
    kap = R2["kappa"]
    rows = [dict(f_GHz=f / 1e9, abs_kappa=float(abs(k)), phase_deg=float(np.degrees(np.angle(k))),
                 abs_kappa_voxel=float(abs(kv)))
            for f, k, kv in zip(kap["f"], kap["kappa"], R2["kappa_voxel"]["kappa"])]
    L += ["### 4.1 Absolute scale and linearisation", "",
          "With 1 V incident on every 50 Ω port the Born sensitivity is absolute: "
          "dS_ij = −(jωε0 Z0 / 4V²) ∫ dε E_i·E_j dV. κ(f) is the complex factor that best maps this "
          "prediction (true dε of Mild, radial shells or voxels) onto the HFSS dS of Mild. κ = 1 would "
          "mean exact Born agreement in absolute units.", "",
          t(rows, ["f_GHz", "abs_kappa", "phase_deg", "abs_kappa_voxel"],
            {"f_GHz": ".1f", "abs_kappa": ".2f", "phase_deg": ".0f", "abs_kappa_voxel": ".2f"}), ""]
    le = R2["lin_err_hfss"]
    rows = []
    for s, v in le.items():
        for k in range(4):
            rows.append(dict(stage=s, k=k, born_over_hfss=v["ratio_born_over_hfss"][k],
                             err_abs_scale=v["abs_scale"][k], err_kappa_mild=v["kappa_mild"][k]))
    kr, kv = np.abs(kap["kappa"]), np.abs(R2["kappa_voxel"]["kappa"])
    ph = np.degrees(np.unwrap(np.angle(kap["kappa"])))
    dph = float(np.mean(np.diff(ph)) / (np.mean(np.diff(kap["f"])) / 1e9))           # deg per GHz
    bo = [x["born_over_hfss"] for x in rows]
    ek = [x["err_kappa_mild"] for x in rows if x["stage"] in REPORTED]
    L += [t(rows, ["stage", "k", "born_over_hfss", "err_abs_scale", "err_kappa_mild"],
            {c: ".2f" for c in ["born_over_hfss", "err_abs_scale", "err_kappa_mild"]}), "",
          "Reading:",
          f"- At 3.4 and 3.6 GHz |κ| = {kv[0]:.2f} and {kv[1]:.2f} (voxel Jacobian, fields taken at the "
          f"grid nodes) and {kr[0]:.2f} and {kr[1]:.2f} (radial Jacobian, fields interpolated onto thin shells). "
          "So the absolute 1 V Born scale holds to within a factor of ~2. The spread between the two "
          "shows how much the result depends on how the 3 mm grid samples the fields at the thin "
          f"CSF/skull interfaces. At 3.8 GHz |κ| = {kv[2]:.0f}–{kr[2]:.0f}: there the Born prediction "
          "misses the HFSS dS badly (the k = 2 couplings have deep nulls near 3.8 GHz).",
          f"- The phase of κ turns by about {dph * 0.2:.0f}° per 200 MHz, i.e. a residual delay of "
          f"~{abs(dph) / 360:.1f} ns between the field-export phase reference and the S-parameter "
          "reference plane. A feed line in front of each patch would do this, but it was not "
          "measured, so treat it as unexplained.",
          f"- The Born prediction of the true change is only {min(bo):.2f}–{max(bo):.2f} of the HFSS dS "
          "(column born_over_hfss, radial Jacobian, absolute scale). Even with κ fitted on Mild, the "
          f"errors for Moderate/Severe are {min(ek):.1f}–{max(ek):.1f}. The AD change (12–21 mm of "
          "gray/white replaced by CSF) is far from a small perturbation, so a linear inversion can at "
          "best be qualitative.", ""]
    # ---- where can it see
    sn = R2["snr_radial"]
    rows = []
    for key, lab in (("snr", "absolute"), ("snr_kappa", "κ-calibrated")):
        for k, name in enumerate(["k=0", "k=1", "k=2", "k=3", "all 21 pairs"]):
            v = np.max(sn[key][k], -1)
            m = np.median(sn[key][k], -1)
            rows.append(dict(scale=lab, path=name, best_at_83=float(np.interp(83.0, sn["r"], v)),
                             best_at_75=float(np.interp(75.0, sn["r"], v)),
                             best_at_60=float(np.interp(60.0, sn["r"], v)),
                             best_at_20=float(np.interp(20.0, sn["r"], v)), median_max=float(m.max()),
                             r_min_snr1=_rmin(sn["r"], v, 1.0)))
    L += ["### 4.2 Where can this array see? (HFSS fields)", "",
          "SNR of a 1 cm³ blob with |dε| = 10 (≈ the gray→CSF contrast) at radius r, on the Normal "
          "background, under the typical noise on both measurements, summed over the 3 frequencies. "
          "best = the direction closest to the antennas, median = over all directions. r_min_snr1 = "
          "the smallest radius down to which SNR ≥ 1 holds continuously from the surface (n/a = never "
          "reached).", "",
          t(rows, ["scale", "path", "best_at_83", "best_at_75", "best_at_60", "best_at_20", "median_max",
                   "r_min_snr1"], {c: ".2g" for c in ["best_at_83", "best_at_75", "best_at_60", "best_at_20",
                                                      "median_max"]}), "",
          "Volume-weighted fraction of the (relative) sensitivity inside r < 60 mm: "
          + ", ".join(f"{k} {v:.1%}" for k, v in R2["sens_fraction_core60"].items()) + ".", "",
          f"- Best direction, all pairs: SNR ≥ 1 down to r ≈ {rows[4]['r_min_snr1']:.0f} mm on the "
          f"absolute scale and r ≈ {rows[9]['r_min_snr1']:.0f} mm κ-calibrated: between the "
          f"outermost ~{max(83.5 - rows[4]['r_min_snr1'], 1):.0f} mm and the outer "
          f"~{83.5 - rows[9]['r_min_snr1']:.0f} mm of brain, and only right under an antenna. The κ-calibrated values are an upper bound: they include "
          "3.8 GHz, where |κ| ≈ 8–11 because Born fails (§4.1).",
          f"- In the median direction the SNR never exceeds {rows[4]['median_max']:.2f} (absolute) / "
          f"{rows[9]['median_max']:.2f} (κ). At r = 60 mm even the best direction gives "
          f"{rows[4]['best_at_60']:.2f} / {rows[9]['best_at_60']:.2f}, and at r = 20 mm "
          f"{rows[4]['best_at_20']:.3f} / {rows[9]['best_at_20']:.3f}. A localised change deeper "
          "than ~1.5 cm is below the noise everywhere.",
          "- Figures: `figures/i2h_sensitivity_maps.png`, `figures/i2h_detectability_radial.png`.", ""]
    # ---- k3 path
    kp = R2["k3_path"]
    rf, bd = kp["region_fraction"], kp["brain_depth_fraction"]
    mid = len(kp["t"]) // 2
    L += ["### 4.3 The k = 3 (opposite-antenna) path, from the wide export", "",
          "The wide file holds only T1. The opposite antenna's field is obtained by the ring "
          "symmetry, E_T4 = R180 E_T1, which agrees with the actual T4 export to "
          f"{kp['sym_check_rel_rms']:.0%} rms inside the head. |E_T1·E_T4| is the Born sensitivity of "
          "the T1–T4 coupling to a permittivity change at each point, including points in air.", "",
          t([{"region": k, "share_of_k3_sensitivity": v} for k, v in rf.items()],
            ["region", "share_of_k3_sensitivity"], {"share_of_k3_sensitivity": ".2%"}), "",
          "Inside the brain, the k = 3 sensitivity by depth: " + ", ".join(f"{k} {v:.0%}" for k, v in bd.items())
          + ".", "",
          f"Field of T1 on the way to T4 (antennas {kp['sep_deg']:.0f}° apart): at the half-way "
          f"point it is {kp['arc_dB'][mid]:.0f} dB (arc over the top, in air at r = 91 mm) vs "
          f"{kp['chord_dB'][mid]:.0f} dB (straight chord, deepest point r = {kp['chord_r'].min():.0f} mm), "
          "relative to the field near T1.", "",
          f"**Verdict (HFSS fields).** {rf['air gap 88-97'] + rf['air r>=97 (incl. antennas)']:.0%} of "
          f"the k = 3 sensitivity is in air and {rf['brain r<83.5']:.1%} is in the brain. Half-way, "
          f"the through-head route is {kp['arc_dB'][mid] - kp['chord_dB'][mid]:.0f} dB weaker than the "
          "around-the-head route. This confirms the delay-based verdict of §1 with the real "
          "antennas: **the opposite-antenna signal travels around the head in air**. The small part "
          f"that touches the brain sits in its outer layer ({bd['78-83.5 mm'] + bd['70-78 mm']:.0%} "
          "within 13.5 mm of the brain surface). That is why k = 3 reacts to CSF/cortex changes "
          "and to nothing deeper. Figure: `figures/i2h_k3_path.png`.", ""]
    # ---- radial inversion
    rad = R2["radial"]
    rows = []
    for key, v in rad["err"].items():
        ds, s = key.split("|")
        for meth, e in v.items():
            rows.append(dict(data=ds, stage=s, method=meth, **e))
    rd = rad["resolution_diag"]
    good = rad["r"][(rd["eps_r"] >= 0.5) | (rd["eps_pp"] >= 0.5)]
    L += ["### 4.4 Radial inversion (2 mm shells; d eps_r and d eps'')", "",
          f"{rad['n_data_real']} real data (4 ring modes × 3 frequencies × Re/Im) for "
          f"{rad['n_unknowns']} unknowns. Fields trilinearly interpolated onto a shell quadrature (the "
          "3 mm grid under-resolves the 0.5 mm Normal CSF layer). Tikhonov (GCV, L-curve) and 1-D TV "
          f"(λ = {rad['lam_tv']:.2g}, tuned on Mild synthetic data). Errors vs the true shell profile:", "",
          t(rows, ["data", "stage", "method", "rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"],
            {c: ".2f" for c in ["rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"]}), "",
          f"Resolution-matrix diagonal (GCV λ on Mild synthetic) ≥ 0.5 at r ∈ {_ranges(good)} mm "
          f"(max {max(rd['eps_r'].max(), rd['eps_pp'].max()):.2f}). Scanning inward, it falls below "
          f"0.3 at r ≈ {_first_below(rad['r'], np.maximum(rd['eps_r'], rd['eps_pp']), 0.3):.0f} mm and "
          f"below 0.1 at r ≈ {_first_below(rad['r'], np.maximum(rd['eps_r'], rd['eps_pp']), 0.1):.0f} mm. "
          "Only the outer ~1 cm has any depth resolution.",
          f"- Even noise-perturbed **Born-consistent** synthetic data are not recovered: rel. errors "
          f"{min(min(x['rel_err_eps_r'], x['rel_err_eps_pp']) for x in rows if x['data'] == 'synthetic-linear'):.2f}–"
          f"{max(max(x['rel_err_eps_r'], x['rel_err_eps_pp']) for x in rows if x['data'] == 'synthetic-linear'):.2f}, "
          f"correlations ≤ {max(max(x['corr_eps_r'], x['corr_eps_pp']) for x in rows if x['data'] == 'synthetic-linear'):.2f}. "
          "On HFSS data, GCV is near zero for Mild and blows up for Moderate/Severe (the data are not "
          "Born-consistent, §4.1). The L-curve returns ≈ 0, and TV is mostly anti-correlated with "
          "the truth. Figure: `figures/i2h_inversions.png`.", ""]
    vx = R2["voxel"]
    rows = []
    for key, v in vx["err"].items():
        ds, s = key.split("|")
        for meth, e in v.items():
            rows.append(dict(data=ds, stage=s, method=meth, **e))
    L += ["### 4.5 Voxel inversion (3 mm grid nodes, r < 83.5 mm)", "",
          f"{vx['n_vox']} voxels × (dε_r, dε''), {vx['n_data_real']} real data (21 pairs × 3 "
          "frequencies × Re/Im). Tikhonov-GCV and L1 (λ tuned on Mild synthetic).", "",
          t(rows, ["data", "stage", "method", "rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"],
            {c: ".2f" for c in ["rel_err_eps_r", "rel_err_eps_pp", "corr_eps_r", "corr_eps_pp"]}), "",
          "Point-spread functions (resolution-matrix columns) for voxels along T1's feed direction:", "",
          t(vx["psf"], ["r_mm", "voxel_mm", "diag", "peak_at_mm", "peak_offset_mm", "n_vox_above_half"],
            {"diag": ".1e", "peak_offset_mm": ".0f"}), "",
          "- Point images, inward along T1's feed direction: "
          + "; ".join(f"r = {p['r_mm']:.0f} mm → peak {p['peak_offset_mm']:.0f} mm away (diag {p['diag']:.0e})"
                      for p in vx["psf"])
          + ". Only the voxel just under the brain surface is imaged near its place, and even that "
          "recovers well under 1 % of a unit change. Deeper voxels are imaged outward toward the "
          "surface: depth is not resolved.",
          "- The L1 solution is the all-zero image (no sparse pattern beats zero on Mild). Tikhonov "
          "images of HFSS data are uncorrelated with the truth (corr ≤ "
          f"{max(x['corr_eps_r'] for x in rows if x['data'] == 'HFSS' and x['method'] == 'tikhonov-gcv'):.2f}). "
          "Figure: `figures/i2h_voxel.png`.", ""]
    if R2_surrogate is not None:
        s2 = R2_surrogate
        sn2 = s2.get("snr_radial")
        rows = [dict(quantity="SNR≥1 (best dir.) down to r, mm",
                     surrogate_v1=_rmin(sn2["r"], np.max(sn2["snr"][4], -1), 1.0) if sn2 else float("nan"),
                     hfss_abs=_rmin(sn["r"], np.max(sn["snr"][4], -1), 1.0),
                     hfss_kappa=_rmin(sn["r"], np.max(sn["snr_kappa"][4], -1), 1.0)),
                dict(quantity="radial resolution diag max",
                     surrogate_v1=float(max(s2["radial"]["resolution_diag"]["eps_r"].max(),
                                            s2["radial"]["resolution_diag"]["eps_pp"].max())),
                     hfss_abs=float("nan"), hfss_kappa=float(max(rd["eps_r"].max(), rd["eps_pp"].max()))),
                dict(quantity="k3 sensitivity share r < 60 mm",
                     surrogate_v1=s2["sens_fraction_core60"]["k3"], hfss_abs=float("nan"),
                     hfss_kappa=R2["sens_fraction_core60"]["k3"])]
        L += ["### 4.6 HFSS vs the earlier surrogate (point-dipole fields, v1 data)", "",
              t(rows, ["quantity", "surrogate_v1", "hfss_abs", "hfss_kappa"],
                {"surrogate_v1": ".3g", "hfss_abs": ".3g", "hfss_kappa": ".3g"}), "",
              "The surrogate used 51 frequencies (3.2–4.2 GHz). HFSS fields exist at 3 frequencies, "
              "which costs √17 ≈ 4× in SNR for broadband sums, but the HFSS fields describe the real "
              "antennas. Both say the same thing: only the outer ~1 cm under the antennas is "
              "visible, and nothing is localised in depth.", ""]
    return L
