"""Report section 4.7 and figure: the Track A ratio lead tested with the HFSS-field Born Jacobian."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from .common import FIG, ROOT  # noqa: E402

Q = ["C1", "C2", "C3", "R21", "R31", "R32"]
AD = ("Mild", "Moderate", "Severe")


def figure(RR):
    k = RR["kernel"]
    r = k["r"]
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.3))
    for q, c in (("C1", "#4C78A8"), ("C2", "#F58518"), ("R21", "k")):
        ax[0].plot(r, k[q], color=c, lw=2 if q == "R21" else 1.2, label=f"d{q}/d eps_r")
    for rb, lab in ((76, "white|gray"), (83, "gray|CSF"), (83.5, "CSF|skull"), (86.5, "skull|fat"), (88, "skin|air")):
        ax[0].axvline(rb, color="0.6", lw=0.6)
    ax[0].set_xlim(60, 90)
    ax[0].set_xlabel("radius (mm)")
    ax[0].set_ylabel("dB per unit d eps_r per 0.25 mm shell (κ on Mild)")
    ax[0].set_title("Sensitivity kernels of C1, C2 and R21 = C2 − C1 (HFSS fields, 3 freqs)", fontsize=9)
    ax[0].legend(fontsize=8)
    w = RR["wide"]
    for kk, c in (("k1", "#4C78A8"), ("k2", "#F58518"), ("k3", "#E45756")):
        prof = w["prof"][kk]["abs"]
        ax[1].semilogy(w["r"], prof / prof.max(), color=c, label=f"{kk} path |kernel| (3.6 GHz, wide export)")
    for rb in (83.5, 88, 97.55):
        ax[1].axvline(rb, color="0.6", lw=0.6)
    ax[1].set_ylim(1e-5, 2)
    ax[1].set_xlabel("radius (mm)")
    ax[1].set_ylabel("shell-integrated |sensitivity| (rel. max)")
    ax[1].set_title("Where the k = 1, 2, 3 power is sensitive, including air (feeds at 97.55 mm)", fontsize=9)
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "ratios_kernels.png", dpi=120)
    plt.close(fig)


def _track_a_v2():
    p = ROOT / "results" / "04" / "per_solve_values.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    d = d[d["set"] == "v2"]
    return {r["stage"]: r for _, r in d.iterrows()}


def section(RR, t, label):
    figure(RR)
    hf, pr, pl = RR["hfss3f"], RR["pred"], RR["pred_lin"]
    stages = list(hf)
    L = ["### 4.7 The Track A ratio lead (R21 = C2/C1, R31 = C3/C1, R32 = C3/C2) tested physically", "",
         label, "",
         "C_k = geometric mean over the ring of the band-averaged |S(t+k, t)|²; ratios in dB (as Track A's "
         "`scripts/04_likelihood.py`, clean data, no floor). The Born prediction uses the HFSS-field "
         f"Jacobian on {RR['dr_mm']} mm shells and each stage's known Δε; κ(f) is fitted on **Mild only** "
         f"(|κ| = {', '.join(f'{abs(k):.2f}' for k in RR['kappa'])} at "
         f"{', '.join(f'{f / 1e9:.1f}' for f in RR['f'])} GHz). Fields exist at those 3 frequencies only, so "
         "predicted and HFSS values below are both means over the same 3 frequencies (HFSS@3f); the "
         "3.2–4.2 GHz HFSS values are listed for reference.", ""]
    ta = _track_a_v2()
    abs32 = RR["hfss_32_42_abs"]
    if ta:
        rows = [dict(stage=s, R21_here=abs32[s]["R21"], R21_trackA=float(ta[s]["R21"]),
                     R32_here=abs32[s]["R32"], R32_trackA=float(ta[s]["R32"])) for s in abs32 if s in ta]
        dmax = max(max(abs(r_["R21_here"] - r_["R21_trackA"]), abs(r_["R32_here"] - r_["R32_trackA"])) for r_ in rows)
        L += [f"Definition check (3.2–4.2 GHz, clean data here vs Track A's noisy-draw means): agree to "
              f"{dmax:.2f} dB.", "",
              t(rows, ["stage", "R21_here", "R21_trackA", "R32_here", "R32_trackA"], {c: ".2f" for c in rows[0] if c != "stage"}), ""]
    # ---- Q1
    rows = []
    for s in stages:
        rows.append(dict(stage=s, kind="HFSS@3f", **{q: hf[s][q] for q in Q}))
        rows.append(dict(stage=s, kind="Born, κ Mild", **{q: pr[s][q] for q in Q}))
        rows.append(dict(stage=s, kind="Born, 1st order", **{q: pl[s][q] for q in Q}))
        rows.append(dict(stage=s, kind="HFSS 3.2–4.2", **{q: RR["hfss_32_42"][s][q] for q in Q}))
    L += ["**1. Predicted vs HFSS changes from Normal (dB).**", "",
          t(rows, ["stage", "kind"] + Q, {q: "+.2f" for q in Q}), ""]
    errs, signs, gaps = {}, {}, {}
    for q in Q:
        h = np.array([hf[s][q] for s in AD])
        p = np.array([pr[s][q] for s in AD])
        errs[q] = float(np.linalg.norm(p - h) / np.linalg.norm(h))
        signs[q] = int(np.sum(np.sign(p) == np.sign(h)))
        gaps[q] = dict(h_sev=hf["Severe"][q] - hf["Mild"][q], h_mm=hf["Moderate"][q] - hf["Mild"][q],
                       p_sev=pr["Severe"][q] - pr["Mild"][q], p_mm=pr["Moderate"][q] - pr["Mild"][q])
    rows = [dict(quantity=q, rel_err_AD=errs[q], sign_agree_of_3=signs[q],
                 HFSS_Sev_minus_Mild=gaps[q]["h_sev"], HFSS_Mod_minus_Mild=gaps[q]["h_mm"],
                 pred_Sev_minus_Mild=gaps[q]["p_sev"], pred_Mod_minus_Mild=gaps[q]["p_mm"]) for q in Q]
    L += [t(rows, ["quantity", "rel_err_AD", "sign_agree_of_3", "HFSS_Sev_minus_Mild", "HFSS_Mod_minus_Mild",
                   "pred_Sev_minus_Mild", "pred_Mod_minus_Mild"],
            {"rel_err_AD": ".2f", "HFSS_Sev_minus_Mild": "+.2f", "HFSS_Mod_minus_Mild": "+.2f",
             "pred_Sev_minus_Mild": "+.2f", "pred_Mod_minus_Mild": "+.2f"}), ""]
    g = gaps["R21"]
    sev_sep = abs(g["p_sev"]) > 3 * abs(g["p_mm"]) and np.sign(g["p_sev"]) == np.sign(g["h_sev"])
    ratio_q = [q for q in ("R21", "R31", "R32")]
    power_q = [q for q in ("C1", "C2", "C3")]
    better = np.mean([errs[q] for q in ratio_q]) < np.mean([errs[q] for q in power_q])
    expl = RR["explained"]
    L += ["- **Does linear theory reproduce \"Severe separates, Mild ≈ Moderate\" for R21?** "
          + ("Yes, qualitatively" if sev_sep else "No")
          + f": predicted Severe − Mild {g['p_sev']:+.2f} dB vs Moderate − Mild {g['p_mm']:+.2f} dB "
          f"(HFSS@3f: {g['h_sev']:+.2f} vs {g['h_mm']:+.2f}). The predicted gap is "
          f"{g['p_sev'] / g['h_sev']:.0%} of the HFSS gap.",
          f"- R32: predicted Severe − Mild {gaps['R32']['p_sev']:+.2f} dB vs HFSS {gaps['R32']['h_sev']:+.2f} dB; "
          f"C3: Severe {pr['Severe']['C3']:+.2f} predicted vs {hf['Severe']['C3']:+.2f} dB in HFSS.",
          f"- **Ratios vs raw powers.** Mean relative error over the AD stages: ratios "
          f"{np.mean([errs[q] for q in ratio_q]):.2f}, powers {np.mean([errs[q] for q in power_q]):.2f}; "
          f"best-predicted quantity {min(errs, key=errs.get)} ({min(errs.values()):.2f}), worst "
          f"{max(errs, key=errs.get)} ({max(errs.values()):.2f}). The ratios are "
          + ("**better** predicted than the raw powers" if better else "**not** better predicted than the raw powers")
          + ". Common errors in the antenna factor cancel in a ratio of path powers, which a single "
          "complex κ(f) cannot fully calibrate.",
          "- Context: with κ on Mild the Born model reproduces "
          + ", ".join(f"{s} {expl[s]['norm_ratio']:.0%}" for s in AD if s in expl)
          + " of the size of the HFSS dS, but its shape errors are ≥ "
          f"{min(expl[s]['rel_err'] for s in AD if s in expl):.2f} (relative), so the agreement on R21 is "
          "partial cancellation, not a validated model.", ""]
    # ---- Q2
    rows = []
    for s in AD:
        tot = pr[s]["R21"]
        mat = pr[f"{s} | material only"]["R21"]
        geo = pr[f"{s} | geometry only"]["R21"]
        csf = pr[f"{s} | CSF material only (Normal geometry)"]["R21"]
        rows.append(dict(stage=s, total=tot, material_only=mat, geometry_only=geo, interaction=tot - mat - geo,
                         CSF_material_in_Normal_geometry=csf))
    L += ["**2. What drives ΔR21?** Predicted ΔR21 (dB, κ on Mild) of each stage split into a material-only "
          "part (Normal radii, stage materials), a geometry-only part (stage radii, Normal materials) and "
          "the interaction (total − both).", "",
          t(rows, ["stage", "total", "material_only", "geometry_only", "interaction", "CSF_material_in_Normal_geometry"],
            {c: "+.2f" for c in rows[0] if c != "stage"}), ""]
    sw = [dict(scenario=n, R21=pr[n]["R21"], R32=pr[n]["R32"]) for n in pr if n.startswith("Severe with")]
    sev, mild = pr["Severe"]["R21"], pr["Mild"]["R21"]
    sw_m = pr.get("Severe with Mild CSF material", {}).get("R21", np.nan)
    sw_n = pr.get("Severe with Normal CSF material", {}).get("R21", np.nan)
    share = (sev - sw_m) / (sev - mild) if sev != mild else np.nan
    L += ["CSF-material swaps (Severe geometry and gray/white materials, CSF permittivity of another stage):", "",
          t(sw + [dict(scenario="Severe (actual)", R21=sev, R32=pr["Severe"]["R32"]),
                  dict(scenario="Mild (actual)", R21=mild, R32=pr["Mild"]["R32"])],
            ["scenario", "R21", "R32"], {"R21": "+.2f", "R32": "+.2f"}), "",
          f"- Giving Severe the Mild CSF permittivity removes {share:.0%} of the predicted Severe − Mild R21 "
          f"gap ({sev - mild:+.2f} dB). With Normal CSF material Severe's ΔR21 falls from {sev:+.2f} to "
          f"{sw_n:+.2f} dB. "
          + ("**Confirmed (at the linear level):** the CSF permittivity drop at Severe (εr 55.25/48.75 → "
             "32.5) drives Severe's separation on R21. It acts through the thick CSF layer of the "
             "atrophied head: in the Normal geometry (0.5 mm CSF) the same material change does almost "
             "nothing (last column above), so this is a material × geometry interaction."
             if share > 0.5 else
             "**Not confirmed:** the CSF permittivity drop explains less than half of the predicted gap."),
          "- Across the AD stages the material-only and geometry-only parts are "
          + ", ".join(f"{r_['stage']} {r_['material_only']:+.2f}/{r_['geometry_only']:+.2f}" for r_ in rows)
          + " dB, with interaction terms "
          + ", ".join(f"{r_['interaction']:+.2f}" for r_ in rows) + " dB: the two parts are not additive.", ""]
    # ---- Q3
    kr = RR["kernel_regions"]
    rows = [dict(region=rg, **{q: kr[q][rg] for q in ("C1", "C2", "R21")}) for rg in kr["C1"]]
    wr = RR["wide"]["regions"]
    rows_w = [dict(region=rg, **{k: wr[k][rg] for k in ("k1", "k2", "k3")}) for rg in wr["k1"]]
    L += ["**3. Where R21 is sensitive.** Fraction of ∫|kernel| per region. Left: C1, C2 and R21 inside "
          "r ≤ 89.75 mm (3 mm export, 3 frequencies). Right: the k = 1, 2, 3 path power over all space to "
          "118 mm (wide export, 3.6 GHz; T2, T3, T4 by rotating T1).", "",
          t(rows, ["region", "C1", "C2", "R21"], {q: ".1%" for q in ("C1", "C2", "R21")}), "",
          t(rows_w, ["region", "k1", "k2", "k3"], {q: ".2%" for q in ("k1", "k2", "k3")}), "",
          f"- Within the head volume, the R21 kernel is {kr['R21']['fat + skin (86.5-88)'] + kr['R21']['air gap (88-89.75)']:.0%} "
          f"in skin/fat and the first 1.75 mm of air, {kr['R21']['skull (83.5-86.5)']:.0%} in the skull, "
          f"{kr['R21']['CSF (83-83.5)']:.1%} in the (Normal, 0.5 mm) CSF and "
          f"{kr['R21']['gray matter / cortex (76-83)'] + kr['R21']['white matter + hippocampus (<76)']:.0%} in the brain.",
          f"- Over all space, {wr['k1']['air gap (88-97)'] + wr['k1']['air incl. antennas (97-118)']:.0%} (k = 1) and "
          f"{wr['k2']['air gap (88-97)'] + wr['k2']['air incl. antennas (97-118)']:.0%} (k = 2) of the path-power "
          "sensitivity lies in air, mostly around the antennas. **R21 is not specifically a CSF probe**: it "
          "responds to the CSF/cortex change only through the small in-tissue share, and it is dominated by "
          "the air gap and the skin, so it should also respond to antenna stand-off and head size.", ""]
    # ---- Q4
    gap_h = hf["Severe"]["R21"] - hf["Mild"]["R21"]
    gap_32 = RR["hfss_32_42"]["Severe"]["R21"] - RR["hfss_32_42"]["Mild"]["R21"]
    gap_p = pl["Severe"]["R21"] - pl["Mild"]["R21"]
    fr = [n for n in pl if n.startswith("stand-off") or n.startswith("head scale")]
    rows = [dict(scenario=n, dR21_first_order=pl[n]["R21"], times_HFSS_gap=pl[n]["R21"] / gap_h,
                 times_pred_gap=pl[n]["R21"] / gap_p, dR21_power_of_linear_field=pr[n]["R21"]) for n in fr]
    worst = max(abs(pl[n]["R21"]) for n in fr)
    L += [f"**4. Predicted fragility.** Severe − Mild R21 gap: HFSS@3f {gap_h:+.2f} dB, HFSS 3.2–4.2 GHz "
          f"{gap_32:+.2f} dB, Born first order {gap_p:+.2f} dB. Setup changes, first order in Δε (κ on Mild):", "",
          t(rows, ["scenario", "dR21_first_order", "times_HFSS_gap", "times_pred_gap", "dR21_power_of_linear_field"],
            {"dR21_first_order": "+.2f", "times_HFSS_gap": "+.1f", "times_pred_gap": "+.1f",
             "dR21_power_of_linear_field": "+.2f"}), "",
          (f"- **Plausible setup variations move R21 as much as the disease does, or more:** the largest "
           f"first-order shift is {worst:.1f} dB, {worst / abs(gap_h):.1f}× the HFSS Severe − Mild gap. "
           if worst >= 0.5 * abs(gap_h) else
           f"- Setup variations move R21 by at most {worst:.2f} dB, below the Severe − Mild gap. ")
          + "These Δε are skin↔air contrasts (|Δε| ≈ 36) at the most sensitive radius, far outside "
          "the Born regime, so the numbers are order-of-magnitude slopes, not predictions; the "
          "\"power of linear field\" column shows how unstable they are. A direct HFSS check (re-solve "
          "Normal with ±1 mm stand-off and ±2 % head scale) is needed before R21 is used across heads or "
          "sessions.", ""]
    # ---- Q5
    so = RR.get("solve", {})
    if "born_MCI_kappa_over_solve" in so:
        L += [f"**5. MCI.** The Born-predicted dS of the hippocampal change alone (25 → 21.25 mm), κ on Mild, "
              f"over the 21 reciprocal pairs at the 3 frequencies, is **{so['born_MCI_kappa_over_solve']:.1e}** "
              f"of the measured solve-to-solve difference (v2 − v1 Normal, same pairs and frequencies; "
              f"{20 * np.log10(so['born_MCI_kappa_over_solve']):.0f} dB; absolute scale "
              f"{so['born_MCI_abs_over_solve']:.1e}). For comparison Mild's predicted dS is "
              f"{so['born_Mild_kappa_over_solve']:.2f} and Severe's {so['born_Severe_kappa_over_solve']:.2f} of "
              "the solve-to-solve difference. **MCI is physically undetectable with this array**: its signal "
              f"is {-np.log10(so['born_MCI_kappa_over_solve']):.1f} orders of magnitude below the variation "
              "between two solves of the same head.", ""]
    # ---- caveats
    L += ["**What the linearisation error means for each conclusion.**", "",
          f"- (1) The linear model explains {min(expl[s]['norm_ratio'] for s in AD):.0%}–{max(expl[s]['norm_ratio'] for s in AD):.0%} "
          "of the size of the HFSS dS with poor shape, so the *ordering* conclusions (Severe separates on R21; "
          "R32/C3 ordering not reproduced) are qualitative; the *magnitudes* are not trustworthy beyond a "
          "factor of ~2–3.",
          "- (2) The material/geometry split is exact algebra within the linear model, but the AD change is "
          "not small, so the interaction term and the CSF attribution could change sign in a full solve. "
          "A decisive test is an HFSS re-solve of Severe with Mild CSF permittivity.",
          "- (3) Kernel region fractions are derivatives at the Normal head and are the least affected by "
          "nonlinearity; their main limit is field sampling (3–4 mm grids under-resolve the 0.5 mm CSF and "
          "1 mm fat layers, and fields are interpolated across interfaces).",
          "- (4) The fragility numbers extrapolate the slope to skin↔air contrasts; they indicate scale "
          "(R21 is at least as sensitive to the setup as to the disease) but not values. Only the "
          "HFSS re-solves above can settle it.",
          "- (5) The MCI ratio is robust: the hippocampal change is ≥ 75 mm from every antenna, its Born "
          "signal is tiny, and the Born error at that depth would have to be "
          + (f"~{1 / so['born_MCI_kappa_over_solve']:.0e}× " if 'born_MCI_kappa_over_solve' in so else "very large ")
          + "to change the conclusion.",
          "", "Figure: `figures/ratios_kernels.png`.", ""]
    return L
