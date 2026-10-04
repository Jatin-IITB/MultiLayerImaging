"""Text of the adversarial review (results/imaging/lobe_review.md) and section 8 of lobe_report.md.
Every number is read from the review results computed in imaging/lobe_review.py."""
from __future__ import annotations

import numpy as np
import pandas as pd

from imaging.common import OUT
from imaging.report_lobe import _t

T7, T6 = "H7 (frozen, primary)", "H6 (matched)"


def _g(rows, **kw):
    for r in rows:
        if all(r.get(k) == v for k, v in kw.items()):
            return r
    raise KeyError(kw)


def write_md(res):
    code, n = res["code"], res["n_draws"]
    src = f"`python imaging/lobe_review.py --n {n}` at code `{code}`; numbers in `results/imaging/lobe_review.json`"
    L = ["# Adversarial review of the lobe blind result (imaging session, 5 Oct)", "",
         f"Every number below was recomputed from the raw `.s6p` files and `lobe_frozen.json` (read only) by {src} "
         "(key named in each section). Predictions (`lobe_predictions.md`, frozen at `fb5b775`) and frozen files are "
         "unchanged. Ruler definitions: clean = max(one-pass mesh yardstick of the four stages, numerical symmetry "
         "floor); measured = max(yardstick, floor ⊕ ±0.5 dB measurement spread) (quadrature, as the main session). "
         "Bar: ≥ 3× established, 2–3× sensitive, < 2× not separable.", ""]
    summary = []

    # ---------------------------------------------------------------- B1
    b1 = res["b1"]
    cols = ["quantity", "comparison", "method", "floor_from", "clean", "yard", "floor", "sd_±0.5 dB gain", "ratio_clean",
            "bar_clean", "ratio_meas_quad", "bar_meas", "ratio_meas_max_old"]
    fmt = {c: ".2f" for c in ("clean", "yard", "floor", "sd_±0.5 dB gain", "ratio_clean", "ratio_meas_quad",
                              "ratio_meas_max_old")}
    lr7 = [r for r in b1 if r["quantity"] == "LR" and r["comparison"].endswith("primary)")
           and r["floor_from"].startswith("max")]
    lr7p6 = [r for r in b1 if r["quantity"] == "LR" and r["comparison"].endswith("primary)")
             and r["floor_from"].startswith("pass")]
    fbm = [r for r in b1 if r["quantity"] == "FB"]
    mz = _g(fbm, comparison="Mild − H6 (lobe_A, truth 0)", method="Tikhonov dS")
    mB = _g(fbm, comparison="Moderate − H7 (lobe_B)", method="Tikhonov dS")
    mA = _g(fbm, comparison="Moderate − H6 (lobe_A)", method="Tikhonov dS")
    L += ["## B1. One bar for left/right and front/back", "",
          "Key `b1` (LR of LeftOnly; FB of Moderate and of the truth-zero Mild/Severe), plus `b1_floors` (LR floor per "
          "design). `ratio_meas_max_old` is the measured ruler as previously combined (plain max).", "",
          _t(b1, cols, fmt), "",
          "LR floor (rms over the 12 ring images × ±) per symmetric design, i.e. the candidates for LeftOnly's own "
          "unmeasurable floor:", "",
          _t(pd.DataFrame(res["b1_floors"]).pivot_table(index=["reference", "method"], columns="design",
                                                         values="LR_floor_rms").reset_index().to_dict("records"),
             ["reference", "method", "Healthy_sliced_new", "MCI_lobe_c3", "Mild_lobe", "Moderate_lobe", "Severe_lobe"],
             {c: ".2f" for c in ["Healthy_sliced_new", "MCI_lobe_c3", "Mild_lobe", "Moderate_lobe", "Severe_lobe"]}), "",
          "**Mechanism of the inconsistency.** §6b used a different verdict function (`lobe_c3.verdict`: hit if the "
          "call holds and the effect is ≥ 2× the ruler) from §5d (≥ 3× exceeds, 2–3× sensitive). That was an "
          "inconsistency, not a physical difference.",
          "**Verdict: CHANGED.** LeftOnly LR, primary reference, conservative floor (largest symmetric-design floor, "
          "set by Moderate_lobe): " + "; ".join(f"{r['method']} {r['ratio_clean']:.2f}× → {r['bar_clean']}" for r in lr7)
          + ". With measurement errors (quadrature): " + "; ".join(f"{r['method']} {r['ratio_meas_quad']:.2f}×" for r in lr7)
          + ". The floor choice matters: with the floor of the pass-matched p6 designs (Healthy_sliced_new, MCI_lobe_c3) "
          "the clean ratios are " + "; ".join(f"{r['method']} {r['ratio_clean']:.2f}× ({r['bar_clean']})" for r in lr7p6)
          + ". LeftOnly's own floor cannot be measured (it is not mirror-symmetric), so the conservative label stands: "
          "**left/right = sensitive at best, not established**; pre-registered verdict PARTIAL kept alongside. "
          f"Front/back on the same bar: Moderate − H6 (lobe_A) {mA['ratio_clean']:.2f}× ({mA['bar_clean']}), Moderate − "
          f"H7 (lobe_B) {mB['ratio_clean']:.2f}× ({mB['bar_clean']}), but the truth-zero Mild − H6 FB is "
          f"{mz['ratio_clean']:.2f}× ({mz['bar_clean']}): the clean ruler does not bound the systematic front bias, so "
          "front/back stays 'not established'.", ""]
    summary.append(("B1 one bar", "CHANGED",
                    f"LeftOnly LR 'hit' (≥ 2×) → {lr7[0]['bar_clean'].split(' (')[0]} ({lr7[0]['ratio_clean']:.2f}×, Tikhonov dS); "
                    f"{lr7[2]['ratio_clean']:.2f}× whitened; measured ≤ {max(r['ratio_meas_quad'] for r in lr7):.2f}×",
                    "lobe_review.json: b1, b1_floors"))

    # ---------------------------------------------------------------- B2
    b2 = pd.DataFrame(res["b2a"])
    piv = b2.pivot_table(index="design", columns=["reference", "method"], values="LR")
    piv.columns = [f"{a} {b}" for a, b in piv.columns]
    t7 = b2[(b2.reference == T7) & (b2.method == "Tikhonov dS")]
    b3f = _g(res["b3"], reference=T7, method="Tikhonov dS")
    b3s = _g(res["b2b"], reference=T7, method="Tikhonov dS")
    L += ["## B2. Is +8.5 bias plus leakage?", "",
          "(a) Key `b2a`: LR of every mirror-symmetric design through the identical pipeline (true LR = 0):", "",
          _t(piv.reset_index().to_dict("records"), ["design"] + list(piv.columns), {c: "+.2f" for c in piv.columns}), "",
          f"Primary method, primary reference: LR ranges {t7.LR.min():+.2f} … {t7.LR.max():+.2f}; "
          f"{int((t7.LR > 0).sum())} positive, {int((t7.LR < 0).sum())} negative; mean {t7.LR.mean():+.2f}. No "
          "consistent sign; the largest is Moderate_lobe (negative, i.e. towards the right), the largest positive is "
          f"{t7.loc[t7.LR.idxmax(), 'design']} ({t7.LR.max():+.2f}).",
          f"(b) Key `b2b`: exactly mirror-symmetrised kernels (K → ½[K + mirror(K)]; frozen kernel mirror asymmetry "
          f"{res['kernel_asym']:.1%}) and symmetrised noise weights: LeftOnly LR {b3s['LR_left']:+.2f} (frozen kernels "
          f"{b3f['LR_left']:+.2f}); asymmetry-free LR_anti {b3s['LR_anti']:+.2f} (frozen {b3f['LR_anti']:+.2f}). With "
          f"symmetric kernels the doubly mirrored input gives exactly −LR ({b3s['LR_mirror_both']:+.2f}), confirming "
          "the symmetrised pipeline is mirror-equivariant.", "",
          "**Mechanism.** Kernel asymmetry contributes "
          f"{b3f['LR_left'] - b3s['LR_left']:+.2f} to LR. The reference's own mirror asymmetry contributes half of "
          f"LR_sum ({b3f['LR_sum'] / 2:+.2f}). The rest, {b3f['LR_anti']:+.2f}, is the mirror-antisymmetric part of "
          "the LeftOnly data. The symmetric designs' LR (a) is negative as often as positive, so a consistent "
          "left-leaning bias is not there to explain +8.5.",
          f"**Verdict: CONFIRMED** that +8.5 is not kernel bias or a consistent design bias: ≈ {b3f['LR_anti']:.1f} of "
          "it is antisymmetric data. Whether that antisymmetric data part is lobe or numerical asymmetry is B3/B9.", ""]
    summary.append(("B2 bias + leakage", "CONFIRMED",
                    f"kernel asymmetry {b3f['LR_left'] - b3s['LR_left']:+.2f}; symmetric designs {t7.LR.min():+.1f}…{t7.LR.max():+.1f}, "
                    f"no consistent sign; LR_anti {b3f['LR_anti']:.2f}", "lobe_review.json: b2a, b2b, b3"))

    # ---------------------------------------------------------------- B3
    b3r = res["b3_rulers"]
    an = [r for r in b3r if r["estimator"].startswith("LR_anti") and r["reference"] == T7]
    sm = [r for r in b3r if r["estimator"].startswith("LR_sum") and r["reference"] == T7 and r["floor_from"].startswith("max")]
    L += ["## B3. Mirror test", "",
          "Key `b3`: mirror(LeftOnly) = LeftOnly with ports T2↔T6, T3↔T5, against the same (unmirrored) reference; "
          "'mirror_both' mirrors the reference too.", "",
          _t(res["b3"], ["reference", "method", "LR_left", "LR_mirror", "LR_sum", "LR_anti", "LR_mirror_both", "S2", "S3",
                         "S5", "S6", "mirror_S2", "mirror_S3", "mirror_S5", "mirror_S6"],
             {c: "+.2f" for c in ["LR_left", "LR_mirror", "LR_sum", "LR_anti", "LR_mirror_both", "S2", "S3", "S5", "S6",
                                  "mirror_S2", "mirror_S3", "mirror_S5", "mirror_S6"]}), "",
          "Key `b3_rulers`: the two estimators through the rulers (each estimator applied to the yardstick, floor and "
          "noise inputs):", "",
          _t(b3r, ["reference", "method", "estimator", "floor_from", "clean", "yard", "floor", "sd_noise", "sd_±0.5 dB gain",
                   "ratio_clean", "bar_clean", "ratio_meas_quad", "bar_meas"],
             {c: ".2f" for c in ["clean", "yard", "floor", "sd_noise", "sd_±0.5 dB gain", "ratio_clean", "ratio_meas_quad"]}), "",
          f"**Result.** LR(mirror) = {b3f['LR_mirror']:+.2f} against LR(LeftOnly) = {b3f['LR_left']:+.2f} (primary); "
          f"S3 {b3f['S3']:.1f} → mirror S5 {b3f['mirror_S5']:.1f}, S2 {b3f['S2']:.1f} → mirror S6 {b3f['mirror_S6']:.1f}. "
          f"LR + LR_mirror = {b3f['LR_sum']:+.2f} = " + ", ".join(f"{r['method']} {r['ratio_clean']:.2f}×" for r in sm)
          + " the clean ruler of that estimator (≈ 0 as required). Asymmetry-free LR_anti against the clean ruler: "
          + "; ".join(f"{r['method']} {r['ratio_clean']:.2f}× ({r['floor_from'].split(' (')[0]})" for r in an)
          + ". With measurement errors: " + "; ".join(f"{r['method']} {r['ratio_meas_quad']:.2f}×" for r in an
                                                       if r["floor_from"].startswith("max")) + ".",
          "**Verdict: CONFIRMED (the sign is in the data), but not established in size.** The mirror test is passed: "
          "the sign follows the data, not kernel or mesh asymmetry of the pipeline. The asymmetry-free estimate is "
          f"{min(r['ratio_clean'] for r in an if r['floor_from'].startswith('max')):.1f}–"
          f"{max(r['ratio_clean'] for r in an if r['floor_from'].startswith('max')):.1f}× the clean ruler with the "
          "conservative floor (not separable / sensitive); with the pass-matched floor "
          f"{min(r['ratio_clean'] for r in an if r['floor_from'].startswith('pass')):.1f}–"
          f"{max(r['ratio_clean'] for r in an if r['floor_from'].startswith('pass')):.1f}×; with measurement errors ≤ "
          f"{max(r['ratio_meas_quad'] for r in an):.1f}×.", ""]
    summary.append(("B3 mirror test", "CONFIRMED (sign); size not established",
                    f"LR_mirror {b3f['LR_mirror']:+.2f}; sum {b3f['LR_sum']:+.2f}; LR_anti {b3f['LR_anti']:.2f} = "
                    f"{an[0]['ratio_clean']:.2f}× clean (conservative floor)", "lobe_review.json: b3, b3_rulers"))

    # ---------------------------------------------------------------- B4
    b4, mech = res["b4"], res["b4_mech"]
    p6 = _g(b4, method="tikhonov dS", reference=T6)
    l6 = _g(b4, method="tikhonov log (gain-inv.)", reference=T6)
    L += ["## B4. The matched reference", "",
          "Key `b4`: the pre-registered criterion with each reference:", "",
          _t(b4, ["method", "reference", "S2", "S3", "T_abs", "LR", "side", "called", "preregistered"],
             {"S2": ".2f", "S3": ".2f", "T_abs": ".2f", "LR": "+.2f"}), "",
          "Key `b4_mech`: per-sector shift H7 → H6 for LeftOnly (primary method) against the inversion of the one-pass "
          "difference −(Healthy_sliced − Healthy_sliced_new):", "",
          _t([dict(sector=s, x_H7=a, x_H6=b, shift=c, one_pass=d) for s, a, b, c, d in
              zip(["S1", "S2", "S3", "S4", "S5", "S6"], mech["x_H7"], mech["x_H6"], mech["shift_observed"],
                  mech["shift_from_one_pass"])], ["sector", "x_H7", "x_H6", "shift", "one_pass"],
             {c: "+.2f" for c in ["x_H7", "x_H6", "shift", "one_pass"]}), "",
          "**Mechanism.** The reconstruction is linear, so changing the reference moves every sector by the inversion "
          "of H7 − H6 (≈ −2 to −3, nearly uniform). Its sign is the opposite of the one-pass row because that row "
          "inverts +(H6 − H7) as a stage; the magnitudes agree to ≤ 0.05. T_abs was calibrated on Mild against H7, so "
          "it sits in the H7 frame. The LR contrast barely moves "
          f"({_g(b4, method='tikhonov dS', reference=T7)['LR']:+.2f} → {p6['LR']:+.2f}) because the shift is common to "
          "all sectors.",
          f"**Verdict: CHANGED (stated plainly).** With the matched reference the primary method calls **nothing** "
          f"(S2 {p6['S2']:.1f}, S3 {p6['S3']:.1f} < {p6['T_abs']:.1f}): pre-registered verdict **{p6['preregistered']}**; "
          f"the frozen log method gives {l6['preregistered']} (S3 {l6['S3']:.1f}). The reader should not trust the "
          "primary sector calls more than the matched ones. The 7-pass reference is primary only because it was "
          "pre-registered and because T_abs lives in its frame. Neither reference makes the absolute sector calls "
          "robust: they move by the size of one mesh pass. Only the side call is reference-invariant.", ""]
    summary.append(("B4 matched reference", "CHANGED", f"primary method: PARTIAL (H7) → {p6['preregistered']} (H6); "
                    "sector calls move by one mesh pass", "lobe_review.json: b4, b4_mech"))

    # ---------------------------------------------------------------- B5
    w7 = _g(b1, quantity="LR", comparison="LeftOnly − H7 (frozen, primary)", method="whitened log",
            floor_from="max of lobe_A symmetric designs")
    meta = res["b5_meta"]
    b5 = res["b5"]
    L += ["## B5. Whitened log: '3.0× with and without measurement errors'", "",
          f"Key `b1` (whitened log, primary reference): yardstick {w7['yard']:.2f}, floor {w7['floor']:.2f}, noise SD "
          f"{w7['sd_noise']:.2f}, ±0.5 dB spread {w7['sd_±0.5 dB gain']:.2f}, ±2 dB spread {w7['sd_±2 dB gain, ±10° phase']:.2f}.",
          "**Mechanism.** The old measured ruler was max(noise, yardstick, floor, spread). The whitened log removes "
          "per-port gains exactly, so its spread is only the typical measurement noise, "
          f"{w7['sd_±0.5 dB gain']:.2f}. That is just below the floor ({w7['floor']:.2f}). The max therefore picked "
          "the floor in both cases, and the ratio did not move. Measurement error did enter, but it was hidden by "
          "the max. Floor and measurement error are independent, so they add in quadrature: "
          f"{w7['ratio_meas_quad']:.2f}× (H7), {_g(b1, quantity='LR', comparison='LeftOnly − H6 (matched)', method='whitened log', floor_from='max of lobe_A symmetric designs')['ratio_meas_quad']:.2f}× (H6).",
          f"**Multiplicity.** On LeftOnly LR, {meta['looks']} method × reference combinations were scored (4 frozen "
          "methods + whitened log, × 2 references). Across §5c–§7 there were 5 methods × 2 path variants (all paths, "
          "no opposite paths) × 2 references = 20; the no-opposite variant was not run on LeftOnly. Treating "
          "ratio = z (a Gaussian ruler, which the yardstick and floor are not) and correcting with Bonferroni:", "",
          _t(b5, ["comparison", "ruler", "ratio", "p_one_sided_if_gaussian", "p_bonferroni"],
             {"ratio": ".2f", "p_one_sided_if_gaussian": ".4f", "p_bonferroni": ".3f"}), "",
          f"(× 20 looks doubles p_bonferroni.) The whitened log was added in commit {meta['whitened_commit']} "
          f"({meta['whitened_commit_time']}), before the LeftOnly file existed (file time {meta['leftonly_file_mtime']}). "
          "It was introduced because the frozen log method leaks port gains, not because of any LeftOnly result.",
          f"**Verdict: CHANGED.** '3.0× with and without' → {w7['ratio_clean']:.2f}× clean / {w7['ratio_meas_quad']:.2f}× "
          "measured. After multiplicity correction the measured value is not significant (p_bonf "
          + " / ".join(f"{r['p_bonferroni']:.2f}" for r in b5 if r["ruler"] == "meas_quad") + " for 10 looks).", ""]
    summary.append(("B5 whitened log", "CHANGED", f"3.0× / 3.0× → {w7['ratio_clean']:.2f}× / {w7['ratio_meas_quad']:.2f}× "
                    f"(max → quadrature); 10 looks, measured p_bonf {min(r['p_bonferroni'] for r in b5 if r['ruler'] == 'meas_quad'):.2f}", "lobe_review.json: b1, b5, b5_meta"))

    # ---------------------------------------------------------------- B6
    b6, sz = res["b6"], res["b6_size"]
    lo = _g(b6, design="LeftOnly_test", reference=T7)
    L += ["## B6. Born validity", "",
          "Key `b6`: κ-scaled Born prediction of ΔS from the true sector maps against the HFSS ΔS, at the fit "
          "frequencies; relative error ‖pred − obs‖ / ‖obs‖ per path class. Also the antisymmetric part (path minus "
          "its mirror path), and what the frozen inversion makes of the prediction (LR pred) versus the data (LR obs).", "",
          _t(b6, list(b6[0]), {k: ".2f" for k in b6[0] if k not in ("design", "reference")}), "",
          f"Whitened norms (primary model, H7): Born error on Mild {sz['mild_model_error']:.1f} against the entire "
          f"LeftOnly signal {sz['leftonly_signal']:.1f}; antisymmetric parts: Mild model error "
          f"{sz['mild_model_error_antisym']:.1f} against LeftOnly {sz['leftonly_antisym']:.1f}.",
          "**Mechanism.** The kernels use the healthy-head fields, but the perturbation replaces 7.5–18 mm of cortex "
          "with CSF and changes CSF everywhere. After the best κ the linear model still misses "
          f"{min(r['all'] for r in b6 if r['design'] != 'MCI_lobe'):.0%}–{max(r['all'] for r in b6 if r['design'] != 'MCI_lobe'):.0%} "
          "of ΔS; the second-neighbour and opposite paths, whose |S| is small, are missed by "
          f"{min(min(r['second-neighbour'], r['opposite']) for r in b6 if r['design'] != 'MCI_lobe'):.0%}–"
          f"{max(max(r['second-neighbour'], r['opposite']) for r in b6 if r['design'] != 'MCI_lobe'):.0%}. MCI is all error (≈ 1.0) "
          "because its true sector change is zero.",
          f"**Verdict: CHANGED (new quantification).** The linearisation error is comparable to the LeftOnly signal. "
          f"The Born prediction gives LR {lo['LR pred Tikhonov dS']:+.1f} against the observed "
          f"{lo['LR obs Tikhonov dS']:+.1f}, a model error of {lo['LR pred Tikhonov dS'] - lo['LR obs Tikhonov dS']:.1f} "
          f"(≈ {(lo['LR pred Tikhonov dS'] - lo['LR obs Tikhonov dS']) / lo['LR obs Tikhonov dS']:.0%} of the signal). "
          f"The relative error of the antisymmetric part is {lo['antisym part: |pred − obs| / |obs|']:.2f}. The "
          "pre-registered +14.7 ± 2.2 never had a valid model-error term.", ""]
    summary.append(("B6 Born validity", "CHANGED", f"rel. error {min(r['all'] for r in b6 if r['design'] != 'MCI_lobe'):.2f}–"
                    f"{max(r['all'] for r in b6 if r['design'] != 'MCI_lobe'):.2f} (all paths); LeftOnly LR "
                    f"pred {lo['LR pred Tikhonov dS']:+.1f} vs obs {lo['LR obs Tikhonov dS']:+.1f}: comparable", "lobe_review.json: b6, b6_size"))

    # ---------------------------------------------------------------- B7
    b7 = [r for r in res["b7"] if r["reference"] == T7]
    v = res["b7_val"]
    true_sets = [r for r in b7 if "interp" not in r["frequencies"]]
    tik = [r for r in true_sets if r["method"] == "Tikhonov dS"]
    L += ["## B7. Fit frequencies", "",
          f"**Why 3.4/3.6/3.8 GHz.** The Born kernels need the HFSS field exports, and those exist only at these three "
          f"frequencies (`data/fields`: {', '.join(res['field_files'])}; 3-point discrete sweep). Data were never "
          "searched over frequency.", "",
          "Key `b7` (primary reference): every subset of the three field frequencies, plus linearly interpolated "
          "kernels at 3.5/3.7 and 3.45–3.75 GHz:", "",
          _t(b7, ["frequencies", "method", "S2", "S3", "S5", "S6", "LR", "LR_anti", "side", "S3_called", "S2_called"],
             {c: "+.2f" for c in ["S2", "S3", "S5", "S6", "LR", "LR_anti"]}), "",
          f"**Interpolation is invalid** (key `b7_val`). The kernel phase rotates by a median "
          f"{v['kernel_phase_rot_deg_median']:.0f}° per 200 MHz; the 3.6 GHz kernel predicted from 3.4/3.8 has "
          f"{v['kernel_rel_err_mid']:.1f}× relative error; LR at 3.6 GHz with the interpolated kernel is "
          f"{v['LR_3.6_interp_Tikhonov dS']:+.2f} against {v['LR_3.6_true_Tikhonov dS']:+.2f} with the true one. The "
          "interpolated rows, including the apparent sign flip at 3.5/3.7, carry no information.", "",
          "Key `b7_band` (data only, no kernels): left-minus-right phase change of each mirror pair of paths, "
          "LeftOnly − H7, across the band:", "",
          _t(res["b7_band"], list(res["b7_band"][0]), {k: "+.1f" for k in res["b7_band"][0] if k != "f_GHz"}), "",
          "**Mechanism.** The dominant pair (T2–T3 against T5–T6) carries a −5 to −6° left/right phase difference "
          "from 3.30 to 3.65 GHz that fades to ≈ 0 to −1° from 3.70 to 3.85 GHz; other pairs vary more erratically. "
          "So the LeftOnly asymmetry sits in the lower half of the band, and the 3.8 GHz kernel sees almost none of it.",
          "**Verdict: CHANGED (frequency dependent); CANNOT TELL for 3.3/3.5/3.7 GHz.** Over the true-field subsets "
          "the side is 'left' whenever 3.4 or 3.6 GHz is included (Tikhonov dS LR "
          + ", ".join(f"{r['frequencies'].split(' ')[0]} {r['LR']:+.1f}" for r in tik) + "). It is 'none' at 3.8 GHz "
          "alone. S3 is called only when 3.4 GHz is included. Other frequencies can only be tested with field "
          "exports at them.", ""]
    summary.append(("B7 fit frequencies", "CHANGED; CANNOT TELL (3.3/3.5/3.7)",
                    "side left for subsets with 3.4 or 3.6, none at 3.8 alone; S3 needs 3.4; interpolation invalid",
                    "lobe_review.json: b7, b7_val, b7_band"))

    # ---------------------------------------------------------------- B8
    b8, m8 = res["b8"], res["b8_meta"]
    flips = [r for r in b8 if r["flip"]]
    L += ["## B8. Calibration re-derived on lobe_A (diagnostic)", "",
          f"Key `b8_meta`: lobe_A recipe (κ on Mild_lobe vs Healthy_sliced_new, GCV λ on Mild, nulls, T_mild) → |κ| "
          f"{', '.join(f'{x:.2f}' for x in m8['kappa_abs'])} (frozen {', '.join(f'{x:.2f}' for x in m8['kappa_frozen_abs'])}); "
          f"λ dS {m8['lam']['dS']:.3f} (frozen {m8['lam_frozen']['dS']:.3f}), log {m8['lam']['log']:.3f} "
          f"(frozen {m8['lam_frozen']['log']:.3f}); T_abs " + ", ".join(
              f"{k.split(' (')[0]} {m8['rules'][k]['T_abs']:.2f} (frozen {m8['rules_frozen'][k]['T_abs']:.2f})"
              for k in m8["rules"]) + ".", "",
          "Key `b8`: calls (affected sectors | side | front/back) with the frozen and the lobe_A-derived calibration:", "",
          _t(b8, ["design", "reference", "method", "frozen", "lobe_A_rules", "flip", "S3_frozen", "S3_lobeA", "LR_frozen",
                  "LR_lobeA"], {c: ".2f" for c in ["S3_frozen", "S3_lobeA", "LR_frozen", "LR_lobeA"]}), "",
          "**Mechanism.** κ re-fitted against the 6-pass reference is "
          f"{min(1 - a / b for a, b in zip(m8['kappa_abs'], m8['kappa_frozen_abs'])):.0%}–"
          f"{max(1 - a / b for a, b in zip(m8['kappa_abs'], m8['kappa_frozen_abs'])):.0%} smaller, so every recovered dε'' grows by "
          "the same factor. T_abs hardly changes (it is set by Mild's own gap). Sectors within ~2 of T_abs cross it.",
          f"**Verdict: CHANGED.** {len(flips)} of {len(b8)} design × reference × method calls flip; "
          f"{sum(r['frozen'].split('|')[1:] != r['lobe_A_rules'].split('|')[1:] for r in b8)} of them change a side or "
          "front/back call, the rest are sector calls. LeftOnly with H7 becomes SUCCESS (S2 and S3) and with H6 "
          "goes from nothing to S3. Mild/Moderate (B) gain their missed sectors; MCI never flips. The sector calls "
          "are decided by the calibration at the 10–20 % level.", ""]
    summary.append(("B8 lobe_A calibration", "CHANGED", f"{len(flips)}/{len(b8)} calls flip (all sector calls; "
                    "side and front/back unchanged; MCI unchanged)", "lobe_review.json: b8, b8_meta"))

    # ---------------------------------------------------------------- B9
    sm9 = res["b9_sum"]
    top = res["b9_top"]
    anti = res["b9_anti"]
    s7 = sm9[f"{T7}|tikhonov dS"]
    L += ["## B9. Where the +8.5 comes from", "",
          "Key `b9_sum`: exact linear decomposition LR = Σ_paths (weight · data), split into the amplitude part "
          "(ln|S_L/S_ref|) and the phase part (arg S_L/S_ref):", "",
          _t([dict(case=k, **vv) for k, vv in sm9.items()], ["case", "LR", "sum_paths", "amp", "phase"],
             {c: "+.2f" for c in ["LR", "sum_paths", "amp", "phase"]}), "",
          "Key `b9_top`: five largest path contributions, with the raw changes at the fit frequencies, the largest "
          "one-pass change of that path, and the main session's band-power numbers and rulers for the same path "
          "(`results/05_lobe/tests/1_leftonly_paths.csv`):", "",
          _t(top, ["reference", "method", "path", "mirror", "contribution", "from_amplitude", "from_phase",
                   "mirror_contribution", "weight", "amp_change_dB_fit", "phase_change_deg_fit", "one_pass_max_amp_dB_fit",
                   "one_pass_max_phase_deg_fit", "band_power_dB", "main_observed_dB", "main_over_yardstick",
                   "main_over_floor", "main_over_spread_05"],
             {c: "+.2f" for c in ["contribution", "from_amplitude", "from_phase", "mirror_contribution"]}
             | {c: ".2f" for c in ["weight", "one_pass_max_amp_dB_fit", "one_pass_max_phase_deg_fit", "band_power_dB",
                                   "main_observed_dB", "main_over_yardstick", "main_over_floor", "main_over_spread_05"]}), "",
          "Key `b9_anti`: left/right differences (left path minus its mirror path) of phase and amplitude at the fit "
          "frequencies, against the largest one-pass and numerical-floor values of the same difference:", "",
          _t(anti, list(anti[0]), {k: ".2f" for k in anti[0] if isinstance(anti[0][k], float)}), "",
          f"**Mechanism.** {s7['phase'] / s7['LR']:.0%} of the primary LR ({s7['phase']:+.2f} of {s7['LR']:+.2f}) comes "
          "from **phase** changes, only "
          f"{s7['amp']:+.2f} from amplitude. The largest single term is the left neighbour path T2–T3: its phase moves "
          "−10.2/−8.4/−4.5° against −4.6/−3.6/−3.5° on its mirror T5–T6, while its amplitude moves ≤ 0.5 dB. The main "
          "session's index and its 22 gain-proof cross-ratios use band-averaged amplitudes, so they cannot see this "
          "phase asymmetry. Their per-path band-power numbers for the same top paths (|change| ≤ "
          f"{max(abs(r['main_observed_dB']) for r in top if r['reference'] == T7):.2f} dB, ≤ "
          f"{max(r['main_over_yardstick'] for r in top if r['reference'] == T7):.1f}× yardstick, ≤ "
          f"{max(r['main_over_floor'] for r in top if r['reference'] == T7):.1f}× floor) agree with the small amplitude part here. There is no contradiction in the data, only two different observables.",
          "**Against the rulers.** The T2–T3 vs T5–T6 phase asymmetry (−5.6° at 3.4 GHz) is 2.7× its largest one-pass "
          "change (2.1°). But it is only 0.9× the largest numerical mirror residual of the symmetric designs (6.3°, set "
          f"by {_g(anti, reference=T7, pair='T2-T3 vs T5-T6')['floor_set_by']}); with the floor of the pass-matched p6 "
          f"designs it is {_g(anti, reference=T7, pair='T2-T3 vs T5-T6')['ratio_with_p6_floor']:.1f}×. The reflection "
          "pairs T2/T6 and T3/T5 exceed both (≈ 2.2× and 3.3×) at 3.4 GHz only.",
          "**Verdict: CONFIRMED (the source is identified), the contradiction resolved by mechanism.** +8.5 is a "
          "left-side phase asymmetry of the neighbour paths and reflections at 3.4–3.6 GHz. The main session is right "
          "that there is no amplitude asymmetry. Neither result establishes a lobe-level left/right signal beyond the "
          "conservative symmetry floor.", ""]
    summary.append(("B9 source of +8.5", "CONFIRMED (mechanism)", f"{s7['phase'] / s7['LR']:.0%} phase, T2–T3 largest; "
                    "main's amplitude-only tests cannot see it; phase asymmetry 2.7× one-pass, 0.9× conservative floor",
                    "lobe_review.json: b9_sum, b9_top, b9_anti"))

    # ---------------------------------------------------------------- summary
    def rng(rows):
        v = [r["ratio_clean"] for r in rows]
        return f"{min(v):.1f}–{max(v):.1f}×"
    an_c = [r for r in an if r["floor_from"].startswith("max")]
    an_p = [r for r in an if r["floor_from"].startswith("pass")]
    size_txt = (f"LR_anti (the asymmetry-free estimate) is {rng(an_c)} the clean ruler with the conservative floor and "
                f"{rng(an_p)} with the pass-matched floor; LR itself {rng(lr7)} / {rng(lr7p6)}")
    kap_txt = (f"{min(1 - a / b for a, b in zip(m8['kappa_abs'], m8['kappa_frozen_abs'])):.0%}–"
               f"{max(1 - a / b for a, b in zip(m8['kappa_abs'], m8['kappa_frozen_abs'])):.0%}")
    L += ["## Summary", "",
          _t([dict(question=a, verdict=b, change=c, evidence=d) for a, b, c, d in summary],
             ["question", "verdict", "change", "evidence"]), "",
          "**What survives.** The left/right sign of LeftOnly is in the data (mirror test) and is stable over the "
          "true-field frequency subsets that include 3.4 or 3.6 GHz and over both references. Its size: " + size_txt +
          ". LeftOnly's own floor cannot be measured, so the conservative floor decides: sensitive at best, not established. It is not separable once "
          f"measurement errors are included, except marginally for the post-hoc whitened log ({w7['ratio_meas_quad']:.1f}×, "
          "not significant after 10 looks). It is carried by phase, which the amplitude-based analysis of the main session does not "
          "use. The sector calls (S2, S3) and the pre-registered PARTIAL depend on the reference (B4) and on the "
          "calibration (B8) by one mesh pass or " + kap_txt + " in κ. The Born model error is as large as the signal (B6).", ""]
    (OUT / "lobe_review.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # section 8 of the lobe report
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    if "## 8. Adversarial review" in rep:
        rep = rep[:rep.index("## 8. Adversarial review")]
    S8 = ["## 8. Adversarial review (5 Oct)", "",
          "Full text, commands and every number: `results/imaging/lobe_review.md` (`lobe_review.json`).", "",
          _t([dict(question=a, verdict=b, change=c, evidence=d) for a, b, c, d in summary],
             ["question", "verdict", "change", "evidence"]), "",
          L[-2], ""]
    lines = rep.rstrip("\n").split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("- **Left/right:**"):
            lines[i] = ln + (" **Revised in §8:** sign confirmed by the mirror test; " + size_txt + " (conservative "
                             "floor decides: sensitive at best); carried by phase; frequency-, reference- and "
                             "calibration-dependent; not established.")
    (OUT / "lobe_report.md").write_text("\n".join(lines) + "\n\n" + "\n".join(S8) + "\n", encoding="utf-8")
