# Round-2 review (imaging session), 5 Oct

Every number was recomputed by `python imaging/lobe_round2.py --n 200` at code `66c04db`, from the raw `.s6p` files, the HFSS field exports and `lobe_frozen.json` (read only); keys refer to `results/imaging/lobe_round2.json`. The R3, C4 and C6 predictions were committed first (`results/imaging/round2_predictions.md`, `0ceb626`). The predictions and frozen files are untouched. Items A14–A28 are the main session's and are not answered here.

**POST-HOC.** Every statement about the *phase* origin of the left/right signal is post-hoc. The frozen imaging pipeline (fb5b775) inverts complex ΔS, so its LR was pre-registered. The decomposition into phase and magnitude, the mirror statistic LR_anti and the cross-ratio phases were all built after unblinding. The primary pre-registered imaging answer stays: blind test PARTIAL with the frozen 7-pass reference, FAIL with the matched one.

## R1. The floor rule for left/right

Statistic: LR_anti(X) = ½[LR(X) − LR(mirror X)], the asymmetry-free LR of the frozen inversion (reference only sets the weights). Key `r1.stats`: null = the nine mirror-symmetric solves.

(a) **Empirical null, normality, rank p.** Values per design:

| design | H7 Tikhonov dS | H7 frozen log | H7 whitened log | H6 Tikhonov dS | H6 frozen log | H6 whitened log |
|---|---|---|---|---|---|---|
| Healthy_sliced | -0.86 | -0.88 | -0.84 | -0.85 | -0.90 | -0.87 |
| Healthy_sliced_new | -1.15 | -1.06 | -0.79 | -1.14 | -1.09 | -0.81 |
| MCI_lobe_c3 | +0.21 | -0.22 | -0.21 | +0.22 | -0.21 | -0.20 |
| Mild_lobe | -0.37 | -0.66 | -0.42 | -0.36 | -0.64 | -0.38 |
| Mild_lobe_new | +0.05 | -0.30 | -0.21 | +0.05 | -0.29 | -0.19 |
| Moderate_lobe | -4.07 | -3.72 | -3.14 | -4.04 | -3.76 | -3.17 |
| Moderate_lobe_c3 | -1.93 | -1.35 | -1.16 | -1.92 | -1.38 | -1.19 |
| Severe_lobe | -0.97 | -0.44 | -0.34 | -0.95 | -0.47 | -0.37 |
| Severe_lobe_c3 | +0.23 | +0.43 | +0.36 | +0.25 | +0.43 | +0.36 |

| reference | method | T | mean | rms | max_abs | rms_without_max | shapiro_W | shapiro_p | rank_p_two_sided | yardstick | ratio_rms_rule | ratio_max_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | Tikhonov dS | 7.860 | -0.985 | 1.617 | 4.071 | 0.933 | 0.837 | 0.054 | 0.100 | 2.143 | 3.668 | 1.930 |
| Healthy_sliced | frozen log | 8.754 | -0.910 | 1.435 | 3.723 | 0.763 | 0.816 | 0.031 | 0.100 | 2.376 | 3.684 | 2.351 |
| Healthy_sliced | whitened log | 8.690 | -0.751 | 1.205 | 3.143 | 0.632 | 0.806 | 0.024 | 0.100 | 1.978 | 4.393 | 2.765 |
| Healthy_sliced_new | Tikhonov dS | 7.857 | -0.970 | 1.605 | 4.042 | 0.924 | 0.838 | 0.055 | 0.100 | 2.123 | 3.701 | 1.944 |
| Healthy_sliced_new | frozen log | 8.822 | -0.923 | 1.452 | 3.757 | 0.780 | 0.822 | 0.036 | 0.100 | 2.375 | 3.715 | 2.348 |
| Healthy_sliced_new | whitened log | 8.773 | -0.756 | 1.218 | 3.168 | 0.644 | 0.811 | 0.027 | 0.100 | 1.974 | 4.444 | 2.769 |

The null is not Gaussian. Shapiro–Wilk gives W = 0.81–0.84, p = 0.024–0.055. One value (Moderate_lobe, -4.07) is 2.1× the next largest, and without it the rms falls from 1.62 to 0.93. LeftOnly (+7.86) lies beyond all nine, so its rank p-value is 0.10 for every method and reference. That is the smallest p nine null solves can give, whatever the rms says.

(b) **Why Moderate_lobe.** Key `r1.mirror_residual`: band-rms mirror residual |S_p − S_mirror(p)| / |S_p| (dB) of each mirror path pair:

| design | T1-T2 vs T1-T6 dB | T1-T3 vs T1-T5 dB | T2 refl. vs T6 refl. dB | T2-T3 vs T5-T6 dB | T2-T4 vs T4-T6 dB | T2-T5 vs T3-T6 dB | T3 refl. vs T5 refl. dB | T3-T4 vs T4-T5 dB |
|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | -33.9 | -26.1 | -44.3 | -37.9 | -26.9 | -33.9 | -43.3 | -36.3 |
| Healthy_sliced_new | -29.6 | -29.1 | -40.7 | -33.5 | -26.8 | -30.8 | -39.6 | -36.7 |
| Mild_lobe | -31.7 | -19.8 | -36.3 | -34.6 | -19.6 | -22.2 | -38.2 | -37.7 |
| Mild_lobe_new | -31.2 | -19.1 | -40.2 | -37.4 | -25.0 | -23.4 | -44.6 | -36.3 |
| Moderate_lobe | -24.8 | -20.3 | -34.5 | -23.7 | -25.5 | -26.0 | -39.9 | -25.6 |
| Moderate_lobe_c3 | -27.1 | -21.2 | -38.2 | -27.9 | -28.1 | -24.6 | -46.1 | -34.9 |
| Severe_lobe | -29.1 | -27.1 | -39.1 | -25.6 | -27.3 | -28.7 | -44.7 | -22.5 |
| Severe_lobe_c3 | -28.9 | -24.2 | -42.4 | -24.1 | -21.5 | -27.1 | -43.4 | -26.8 |
| MCI_lobe_c3 | -27.6 | -22.3 | -41.8 | -36.6 | -23.3 | -28.4 | -43.9 | -32.8 |

Moderate_lobe has the largest residual on the two neighbour pairs that dominate LR: T2–T3 vs T5–T6 -23.7 dB, against −27.9 to −37.9 dB elsewhere except Severe. Its LR_anti decomposes into T2–T3 -1.32 and T5–T6 -1.29 (total -4.07). **Mechanism: mesh asymmetry of that one file.** The same design re-solved one pass further (Moderate_lobe_c3, 6 passes) halves it: total -1.93, T2–T3 -0.67, T5–T6 -0.61. Severe_lobe has a similar residual on T3–T4 vs T4–T5 (−22.5 dB), but it projects weakly onto LR (−0.97). The residual is numerical, and it shrinks with convergence.

(c) **Floor rule, fixed now without reference to LeftOnly.** For any reference-free left/right statistic, clean ruler = max(one-pass yardstick of that statistic, largest |value| over all available mirror-symmetric solves, none excluded). The rank p-value is reported alongside. Why the maximum and not the rms: (1) n = 9 is too small to estimate a tail, and this null is measurably non-Gaussian with one large outlier; (2) the maximum is the only distribution-free envelope n = 9 provides; (3) excluding Moderate_lobe would mean choosing the null after seeing it, since it is a legitimate solve under the stop rule. Applied to both sessions' numbers:

| statistic | value | rms rule (main) | max rule (fixed) |
|---|---|---|---|
| imaging LR_anti, Tikhonov dS | +7.86 | 3.67 | 1.93 |
| imaging LR_anti, frozen log | +8.75 | 3.68 | 2.35 |
| imaging LR_anti, whitened log | +8.69 | 4.39 | 2.76 |

Main's phase cross-ratios (band mean): 16/22 ≥ 3× under the rms rule (reproduced exactly), but only 4/22 under the fixed rule. With the 4 duplicates removed: 12/18 and 3/18.
**Verdict: CHANGED.** Main's 3.7× for the imaging LR_anti becomes 1.93× (Tikhonov dS; 2.76× whitened log). Under the fixed rule that is not separable / sensitive. Rank p = 0.1 for every method: LeftOnly is beyond all nine nulls, and nine nulls cannot say more than that. **CANNOT TELL** at p < 0.1. Settling it needs at least 19 independent mirror-symmetric solves, for example Healthy_sliced re-solved with head and array rotated by k × 7° (k = 1…10), which gives the same geometry on independent meshes.

## R2. One phase quantity, one ruler

The two sides used different quantities. **Main:** band-mean (3.2–4.2 GHz, 201 points) left/right phase of the complex cross-ratios, ruler max(null rms, one-pass yardstick). **Imaging round 1 (b9_anti):** single-path-pair phase differences at 3.4/3.6/3.8 GHz, ruler max(one-pass, √2 × largest mirror residual). Below, both are on the same rulers. Key `r2.views`, cross-ratio phases (18 distinct, plus main's 22):

| set | view | n | left_ge3_rms_rule | left_ge3_max_rule | left_beyond_null_max | left_ge3_yard | best_ratio_rms_rule | best_ratio_max_rule | median_abs_left_deg | median_yard_deg | median_null_rms_deg | median_null_max_deg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18 distinct | band mean 3.2-4.2 GHz (main session's quantity) | 18 | 12 | 3 | 12 | 12 | 6.91 | 4.03 | 5.13 | 1.50 | 1.50 | 2.76 |
| 18 distinct | 3.4 GHz | 18 | 9 | 4 | 12 | 9 | 4.88 | 4.26 | 6.39 | 2.17 | 1.36 | 2.77 |
| 18 distinct | 3.6 GHz | 18 | 0 | 0 | 9 | 0 | 2.52 | 1.77 | 5.55 | 5.17 | 4.04 | 6.39 |
| 18 distinct | 3.8 GHz | 18 | 0 | 0 | 1 | 0 | 1.66 | 1.23 | 4.80 | 12.26 | 8.55 | 16.03 |
| 18 distinct | band mean 3.30-3.65 GHz | 18 | 12 | 7 | 14 | 13 | 6.73 | 4.05 | 7.86 | 1.69 | 1.87 | 3.55 |
| 22 (main filter) | band mean 3.2-4.2 GHz (main session's quantity) | 22 | 16 | 4 | 16 | 16 | 6.91 | 4.03 | 5.13 | 1.48 | 1.50 | 2.76 |

Key `r2.pairs`, the imaging pair quantity on the same rulers:

| view | pair | left | yard | null_rms | null_max | null_max_design | ratio_rms_rule | ratio_max_rule |
|---|---|---|---|---|---|---|---|---|
| band mean 3.2-4.2 GHz | T1-T2 vs T1-T6 | -2.00 | 0.61 | 0.73 | 1.74 | Moderate_lobe | 2.73 | 1.15 |
| band mean 3.2-4.2 GHz | T1-T3 vs T1-T5 | 3.43 | 1.27 | 1.38 | 3.26 | Moderate_lobe | 2.49 | 1.05 |
| band mean 3.2-4.2 GHz | T2 refl. vs T6 refl. | -0.00 | 0.17 | 0.21 | 0.39 | Moderate_lobe | 0.01 | 0.01 |
| band mean 3.2-4.2 GHz | T2-T3 vs T5-T6 | -3.38 | 1.46 | 1.01 | 2.23 | Moderate_lobe | 2.31 | 1.52 |
| band mean 3.2-4.2 GHz | T2-T4 vs T4-T6 | 3.30 | 1.66 | 1.33 | 2.89 | Severe_lobe_c3 | 1.99 | 1.14 |
| band mean 3.2-4.2 GHz | T3 refl. vs T5 refl. | -0.03 | 0.12 | 0.07 | 0.13 | Mild_lobe | 0.29 | 0.26 |
| band mean 3.2-4.2 GHz | T3-T4 vs T4-T5 | -1.54 | 0.82 | 0.60 | 1.08 | Moderate_lobe | 1.87 | 1.43 |
| 3.4 GHz | T1-T2 vs T1-T6 | -2.90 | 0.56 | 0.82 | 1.36 | Mild_lobe | 3.52 | 2.13 |
| 3.4 GHz | T1-T3 vs T1-T5 | 2.87 | 1.84 | 1.08 | 2.31 | Moderate_lobe | 1.56 | 1.24 |
| 3.4 GHz | T2 refl. vs T6 refl. | 4.84 | 0.05 | 0.46 | 0.57 | Moderate_lobe | 10.45 | 8.46 |
| 3.4 GHz | T2-T3 vs T5-T6 | -5.58 | 1.48 | 0.74 | 2.05 | Moderate_lobe | 3.77 | 2.72 |
| 3.4 GHz | T2-T4 vs T4-T6 | 4.34 | 2.48 | 1.30 | 3.22 | Severe_lobe_c3 | 1.75 | 1.35 |
| 3.4 GHz | T3 refl. vs T5 refl. | 4.94 | 0.27 | 0.24 | 0.35 | Mild_lobe | 18.65 | 13.97 |
| 3.4 GHz | T3-T4 vs T4-T5 | -3.32 | 0.42 | 0.34 | 0.63 | Healthy_sliced | 7.97 | 5.26 |
| 3.6 GHz | T1-T2 vs T1-T6 | -1.84 | 0.79 | 1.03 | 1.76 | Moderate_lobe | 1.78 | 1.05 |
| 3.6 GHz | T1-T3 vs T1-T5 | 7.24 | 4.67 | 4.54 | 7.47 | Severe_lobe_c3 | 1.55 | 0.97 |
| 3.6 GHz | T2 refl. vs T6 refl. | -0.80 | 0.47 | 0.69 | 1.27 | MCI_lobe_c3 | 1.16 | 0.63 |
| 3.6 GHz | T2-T3 vs T5-T6 | -4.19 | 2.07 | 1.14 | 2.19 | Moderate_lobe | 2.02 | 1.91 |
| 3.6 GHz | T2-T4 vs T4-T6 | -0.94 | 4.28 | 2.04 | 3.98 | Mild_lobe | 0.22 | 0.22 |
| 3.6 GHz | T3 refl. vs T5 refl. | -0.15 | 0.27 | 0.79 | 1.10 | Mild_lobe | 0.18 | 0.13 |
| 3.6 GHz | T3-T4 vs T4-T5 | -3.55 | 2.38 | 1.33 | 2.51 | Severe_lobe | 1.49 | 1.41 |

**One answer.** Mesh error (one-pass) is cleared: at band mean 12/18 cross-ratio phases are ≥ 3× their one-pass yardstick. The numerical floor is cleared only under the rms rule (12/18). Under the fixed max rule it is 3/18 at band mean and 7/18 at 3.30–3.65 GHz. At 3.6 and 3.8 GHz alone, nothing clears either rule. The strongest single effects are the reflection pairs at 3.4 GHz: T2 vs T6 8.5× and T3 vs T5 14.0× under the max rule. Main's 16/22 contains 4 exact algebraic duplicates; the distinct count is 12/18.
**Verdict: CHANGED.** The disagreement was the quantity (band mean vs single frequency) and the floor (rms vs max), not the data. On one quantity and one rule: clears mesh error, and clears the numerical floor only partly (3/18 at band mean).

## R3. Detuning hypothesis (predictions in 0ceb626)

Key `r3.resonance`: frequency and depth of min |S_ii|, parabolic-refined:

| design | T1 f_res GHz | T1 depth dB | T2 f_res GHz | T2 depth dB | T3 f_res GHz | T3 depth dB | T4 f_res GHz | T4 depth dB | T5 f_res GHz | T5 depth dB | T6 f_res GHz | T6 depth dB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced_new | 3.658 | -21.094 | 3.658 | -21.206 | 3.659 | -21.024 | 3.657 | -21.099 | 3.658 | -20.895 | 3.657 | -20.755 |
| Healthy_sliced | 3.659 | -20.943 | 3.659 | -21.236 | 3.660 | -20.977 | 3.658 | -21.077 | 3.659 | -21.017 | 3.659 | -20.862 |
| LeftOnly_test_c3 | 3.658 | -20.587 | 3.657 | -20.174 | 3.659 | -20.166 | 3.656 | -21.022 | 3.656 | -20.769 | 3.656 | -20.787 |
| Mild_lobe | 3.654 | -20.472 | 3.657 | -20.440 | 3.655 | -20.991 | 3.655 | -20.193 | 3.655 | -20.145 | 3.653 | -19.914 |
| MCI_lobe_c3 | 3.656 | -21.065 | 3.658 | -21.343 | 3.658 | -21.043 | 3.657 | -20.638 | 3.657 | -20.641 | 3.657 | -20.823 |

One-pass change of resonance frequency (MHz): T1 1.7, T2 1.4, T3 1.6, T4 1.9, T5 2.6, T6 2.4; of depth (dB): T1 0.37, T2 0.29, T3 0.16, T4 0.25, T5 0.35, T6 0.58.

Key `r3.per_port`: least-squares per-port model Δln S_ab ≈ g_a + g_b (one complex factor per antenna), LeftOnly − H6. Shown: the share of the mirror-antisymmetric transmission change it explains, the observed T2–T3 minus T5–T6 phase, and the reflection-product prediction ½(Δln S_aa + Δln S_bb):

| f_GHz | antisym_energy_explained_by_per_port | antisym_phase_explained_by_per_port | obs_T23_minus_T56_deg | per_port_fit_T23_minus_T56_deg | reflection_product_pred_deg | g_phase_deg |
|---|---|---|---|---|---|---|
| 3.30 | 0.11 | 0.08 | -5.00 | -0.87 | 0.43 | T1 -0.3, T2 +0.0, T3 -0.4, T4 -0.4, T5 +0.2, T6 +0.3 |
| 3.35 | 0.06 | 0.14 | -5.88 | -0.87 | 1.74 | T1 -0.3, T2 +0.0, T3 -0.3, T4 -0.0, T5 +0.1, T6 +0.6 |
| 3.40 | -0.08 | -0.15 | -5.78 | 0.99 | 4.79 | T1 -0.3, T2 +1.0, T3 +0.7, T4 +0.0, T5 +0.1, T6 +0.7 |
| 3.45 | -0.21 | -0.12 | -5.41 | 1.95 | 5.05 | T1 +0.3, T2 +1.8, T3 +1.3, T4 -0.2, T5 +0.6, T6 +0.6 |
| 3.50 | -0.01 | -0.00 | -5.68 | -1.27 | -2.47 | T1 +0.6, T2 +0.6, T3 -0.1, T4 +0.4, T5 +1.2, T6 +0.6 |
| 3.55 | 0.11 | 0.00 | -6.56 | -0.11 | -2.08 | T1 +1.2, T2 +1.7, T3 +1.0, T4 +1.2, T5 +1.5, T6 +1.3 |
| 3.60 | 0.17 | 0.18 | -5.85 | -1.47 | -0.49 | T1 -0.7, T2 -0.9, T3 -1.7, T4 -0.5, T5 -1.6, T6 +0.5 |
| 3.65 | 0.17 | 0.31 | -2.79 | -0.97 | 0.50 | T1 -1.0, T2 -0.3, T3 -1.7, T4 -0.1, T5 -1.8, T6 +0.7 |
| 3.70 | 0.19 | 0.26 | -1.27 | -0.80 | -1.78 | T1 -0.3, T2 -0.4, T3 -1.8, T4 +0.6, T5 -2.7, T6 +1.3 |
| 3.75 | 0.18 | 0.06 | -2.29 | 0.89 | -0.73 | T1 +0.2, T2 +0.6, T3 -1.7, T4 +1.1, T5 -2.4, T6 +0.3 |
| 3.80 | 0.09 | 0.04 | -1.94 | -0.05 | -0.52 | T1 +0.2, T2 -1.1, T3 -1.4, T4 +0.2, T5 -1.6, T6 -0.8 |
| 3.85 | 0.49 | 0.46 | -1.89 | -0.11 | -0.61 | T1 +4.6, T2 -1.8, T3 +1.3, T4 +5.6, T5 +2.9, T6 -3.4 |
| 3.90 | 0.19 | 0.03 | -3.89 | -0.50 | -0.30 | T1 -0.1, T2 -0.6, T3 -1.5, T4 +0.5, T5 -1.2, T6 -0.4 |

**Measured against the predictions:**
1. Resonance frequency: no antenna moves beyond its one-pass change (LeftOnly T2 3.657, T3 3.659, T5 3.656, T6 3.656 GHz, against 3.658–3.659 healthy). The depth does change on the left only: T2 +1.03, T3 +0.86 dB, against T5 +0.13, T6 -0.03 dB (one-pass ≤ 0.29 dB). That is a real near-field loading effect, but not a detuning in frequency.
2. Per-port model: explains -21% to 19% of the antisymmetric transmission energy at 3.30–3.80 GHz (prediction: < 30 %). Holds.
3. Reflection product: wrong sign where the asymmetry is largest (3.40–3.45 GHz: +4.8° predicted vs -5.8° observed). Fails, against H_det.
Consistent with this: the whitened log, which removes any per-port complex factor exactly, keeps the full LR (≈ +9.3).
**Verdict: CHANGED (hypothesis tested and rejected for transmissions).** The transmission phase asymmetry is not per-antenna detuning. The left reflections change too (depth ≈ 1 dB; phase +6–7° at 3.4 GHz), so the left antennas' near field is loaded. Plain statement: localisation here means 'the sensitivity volume of the left neighbour paths', 56 % of which lies in the outer gap layer under T2/T3 (0ceb626). That is a few millimetres to about a centimetre below the skull, not a lobe.

## R4. R31 vs R21 (shown, not adopted)

Key `r4` (read-only, `adstage.features.ring_features`, frozen recipe with the −30 dB mask). τ31 = -15.273 dB (frozen). τ21 = -19.871 dB is an **illustration only**: the midpoint of v2 Normal and the mean of v2 Mild/Moderate/Severe, not a rule. One-pass yardstick: R31 0.135, R21 0.110 dB.

| family | file | R31 | R21 | R31 label | R31 margin / yard | R21 label (illustr.) | R21 margin / yard |
|---|---|---|---|---|---|---|---|
| v2 uniform | new_Healthy | -14.674 | -20.722 | Normal | -4.4 | Normal | -7.7 |
| v2 uniform | new_MCI | -14.614 | -20.685 | Normal | -4.9 | Normal | -7.4 |
| v2 uniform | new_MildAD | -16.058 | -19.479 | AD | +5.8 | AD | +3.6 |
| v2 uniform | new_ModerateAD | -16.168 | -19.526 | AD | +6.6 | AD | +3.1 |
| v2 uniform | new_SevereAD | -15.851 | -18.058 | AD | +4.3 | AD | +16.5 |
| lobe | new_with_slices_Healthy_sliced | -14.609 | -20.507 | Normal | -4.9 | Normal | -5.8 |
| lobe | new_with_slices_Healthy_sliced_new | -14.744 | -20.567 | Normal | -3.9 | Normal | -6.3 |
| lobe | new_with_slices_Mild_lobe | -15.822 | -19.974 | AD | +4.1 | Normal | -0.9 |
| lobe | new_with_slices_Mild_lobe_new | -15.856 | -19.940 | AD | +4.3 | Normal | -0.6 |
| lobe | new_with_slices_Moderate_lobe | -16.008 | -19.451 | AD | +5.4 | AD | +3.8 |
| lobe | new_with_slices_Moderate_lobe_c3 | -16.012 | -19.451 | AD | +5.5 | AD | +3.8 |
| lobe | new_with_slices_Severe_lobe | -15.533 | -18.002 | AD | +1.9 | AD | +17.0 |
| lobe | new_with_slices_Severe_lobe_c3 | -15.584 | -17.892 | AD | +2.3 | AD | +18.0 |
| lobe | new_with_slices_LeftOnly_test_c3 | -15.445 | -20.200 | AD | +1.3 | Normal | -3.0 |
| lobe | new_with_slices_MCI_lobe_c3 | -14.773 | -20.555 | Normal | -3.7 | Normal | -6.2 |

**Mechanism.** R21 is monotonic with severity (lobe: Normal −20.5/−20.6, Mild −19.96, Moderate −19.45, Severe −17.9 dB) and R31 is not (Moderate −16.0, Severe −15.5/−15.6). R31 separates Normal from uniform Mild and Moderate by 4–7 yardsticks, but lobe Severe by only 1.9–2.3 and LeftOnly by 1.3. R21 separates Severe by 17–18 and Moderate by 3.8, but lobe Mild by < 1 and LeftOnly not at all.
**Verdict: CONFIRMED (the frozen choice is defensible on the data it was trained on, fragile off it).** On v2 uniform every AD stage clears τ31 by ≥ 4.3 yardsticks. No single feature determines every lobe design (R31 fails Severe/LeftOnly at 3×; R21 fails Mild/LeftOnly). A pair rule is a new rule: it must be pre-registered and tested on a new blind design. The detection rule itself is the main session's.

## R5. Should sector-level imaging be reported?

Evidence against sector-level values, all re-derived: model error of 6–8 per sector against a CRLB of 3.2–3.3 (B21); calls flip with λ × 0.3 / × 3 in every design except MCI (B17), with the reference (B23), and with re-calibration (round-1 B8, 14/28); kernel grid sensitivity 24 % (B14); a deep change is invisible and the same sector value means different things for gap and material changes (B16); each sector value is ≈ 80 % its own antenna (B25).
**Verdict: CHANGED.** Sector values and per-sector calls are not results and are not reported as such. Reportable: the **sign** of left/right (POST-HOC phase attribution; size not established, R1) and the bias-corrected front/back contrast with its set dependence (B24). Ranked by expected benefit per cost:

| rank | step | benefit | cost |
|---|---|---|---|
| 1 | ≥ 19 independent mirror-symmetric solves (rotated meshes) | settles the floor (R1, C3) | low (HFSS runs) |
| 2 | Field exports at 3.3/3.5/3.7/3.9 GHz on a 1 mm grid near the cortex | frequency selection (B18), grid error (B14) | low–moderate |
| 3 | Data-driven sector model: 6 single-sector HFSS designs as empirical kernel columns | removes Born error in the sector basis | moderate (6–12 solves) |
| 4 | Mirror replication design (RightOnly_test, C6) | tests mesh vs signal for the sign | low (1 solve) |
| 5 | Second, lower ring of antennas | temporal-lobe coverage (G5: ≤ 4 % sensitivity below z = 0) | high (redesign) |
| 6 | Iterative DBIM / Gauss–Newton with HFSS-updated fields | quantitative values | high (fields per iteration) |
| 7 | Wider band | more independent data | moderate (antenna redesign) |

## R6. 'Robust' detection ruler

The A1 ruler and the detection claims are the main session's. Imaging makes no detection claim. The imaging rulers already include the measurement spread, in quadrature (max(yardstick, floor ⊕ ±0.5 dB spread), round 1). The effective sample size of the imaging thresholds is one Mild solve and the null files listed in B19. **Verdict: not applicable to imaging** (answer belongs to the main session).

## R7 / G8. Field-export geometry

Key `fields.grid`: 3 frequencies [3.4, 3.6, 3.8] GHz; volume x [-90.0, 90.0], y [-90.0, 90.0], z [-90.0, 90.0] mm, step 3.0 mm, [61, 61, 61] nodes; NaN fraction inside r < 83.5 mm 0%. Every file header reads 'Grid Output Min [−90 −90 −90] Max [90 90 90] Grid Size [3 3 3] mm' (one extra `_wide` file: ±120 mm, 4 mm). `study_lobe.born_table` integrates over full spherical shells (64 Gauss–Legendre θ nodes, 5° φ, 0.25 mm r).
**Verdict: CONFIRMED.** Every kernel, depth and sensitivity result used the 3-D volume, not the z = −9.09 mm `field_cutplane` sheet. The array (feeds at z = 56.1 mm, r = 97.15 mm) is outside the export box (|x|, |y| ≤ 90). The head is fully inside it.

## B14. Kernels and Born error

Kernels: HFSS v2 Normal design (unsliced, `new_Healthy`), E-field volume exports for each of the six excitations at 3.4/3.6/3.8 GHz, 3 mm grid; the v2 mesh is the 6-pass unconverged one (MODEL_CARD).

Born error per path class (key `b14_born.rows`; κ-scaled prediction from the true sector maps vs HFSS ΔS):

| design | reference | reflection | neighbour | second-neighbour | opposite | all | antisym part: |pred − obs| / |obs| | LR pred Tikhonov dS | LR obs Tikhonov dS |
|---|---|---|---|---|---|---|---|---|---|
| Mild_lobe | H7 (frozen, primary) | 0.59 | 0.42 | 0.97 | 1.23 | 0.59 | 1.18 | 0.16 | -0.04 |
| Mild_lobe | H6 (matched) | 0.57 | 0.34 | 0.97 | 1.25 | 0.57 | 1.17 | 0.15 | 0.35 |
| Moderate_lobe | H7 (frozen, primary) | 0.56 | 0.30 | 0.72 | 1.10 | 0.56 | 1.20 | 0.35 | -3.92 |
| Moderate_lobe | H6 (matched) | 0.60 | 0.33 | 0.75 | 0.95 | 0.60 | 1.18 | 0.33 | -3.54 |
| Severe_lobe | H7 (frozen, primary) | 0.61 | 0.39 | 0.87 | 1.08 | 0.61 | 1.29 | 1.14 | -0.80 |
| Severe_lobe | H6 (matched) | 0.66 | 0.42 | 0.94 | 0.95 | 0.65 | 1.08 | 1.11 | -0.43 |
| LeftOnly_test | H7 (frozen, primary) | 0.57 | 0.39 | 0.70 | 0.99 | 0.57 | 0.96 | 15.01 | 8.48 |
| LeftOnly_test | H6 (matched) | 0.67 | 0.60 | 0.65 | 0.85 | 0.67 | 0.92 | 15.00 | 8.82 |
| MCI_lobe | H7 (frozen, primary) | 1.00 | 1.00 | 1.01 | 1.01 | 1.00 | 1.00 | 0.01 | 1.02 |
| MCI_lobe | H6 (matched) | 1.00 | 1.00 | 1.01 | 1.01 | 1.00 | 1.00 | 0.01 | 1.37 |

LeftOnly split into mirror-symmetric and antisymmetric parts (key `b14_born.leftonly_parts`): Healthy_sliced: symmetric 0.50, antisymmetric 0.96 (antisym/sym size 0.35); Healthy_sliced_new: symmetric 0.58, antisymmetric 0.92 (antisym/sym size 0.54). Zero-LR designs: Born predicts LR Mild +0.16, Moderate +0.35, Severe +1.14, MCI +0.01 against observed -0.04, -3.92, -0.80, +1.02.
Grid sensitivity (key `fields.b14_grid`): the T1 reflection kernel from the 4 mm `_wide` export differs from the 3 mm one by 24% overall (per sector 23%, 26%, 24%, 42%, 25%, 6%).
**Verdict: CHANGED.** The Born error is about 50–60 % on the symmetric part and above 90 % on the antisymmetric part of LeftOnly. On zero-LR designs, the Born model's LR (κ-scaled kernel asymmetry) is ≤ 1.2, and the observed values (up to −3.9) are the files' numerical asymmetry. The kernel grid alone moves kernels by about 24 %. Every sector value is model-dependent at that level.

## B15. Kernel mirror asymmetry

Key `fields.b15`: voxel-wise mirror asymmetry of the field exports inside the head (|E_a − M E_b(−x)| / |E_a|), and the same norm for a pure 0.8° azimuth rotation of the field (the audit shows the array at −0.4° from nominal, so a mirror image is offset by 0.8°):

| pair | mirror_rel_diff | rotation_0p8deg_rel_diff |
|---|---|---|
| T1 vs mirror(T1) | 0.209 | 0.095 |
| T2 vs mirror(T6) | 0.217 | 0.132 |
| T3 vs mirror(T5) | 0.230 | 0.128 |
| T4 vs mirror(T4) | 0.224 | 0.095 |

**Mechanism.** The voxel-level asymmetry is 21–23 %. A 0.8° rotation alone produces 10–13 %, so roughly half is the array offset. The rest is the asymmetric tetrahedral mesh of the v2 solve and its interpolation onto the 3 mm grid; the export grid itself is exactly mirror-symmetric (nodes at ±x). After integration over 60° sectors this leaves 6.4 % kernel asymmetry. Effect (round 1, b2b): symmetrising the kernels changes LR by +0.32, LR_anti by +0.07 and FB by ≤ 0.05. Symmetrising does not hide real asymmetry because real asymmetry lives in the data, which are not touched. The symmetrised pipeline maps mirror(data) exactly to −LR (round 1).
**Verdict: CONFIRMED (effect negligible), cause CHANGED.** Cause: about half array offset, half v2 mesh (not 'unknown').

## B16. Sector model vs depth (Born-internal)

Key `b16`: synthetic data from the healthy-field Born model, three changes confined to S3 with nothing elsewhere, inverted by the frozen pipeline (matched reference). 'true_S3' is the sensitivity-weighted dε'' over the whole S3 column.

| change | method | true_S3_sensweighted | S1 | S2 | S3 | S4 | S5 | S6 | LR |
|---|---|---|---|---|---|---|---|---|---|
| S3 gap only (CSF replaces gray 71.5-83 mm, healthy materials) | Tikhonov dS | +6.05 | -0.17 | +0.10 | +14.93 | +0.77 | -0.36 | +0.06 | +7.66 |
| S3 gap only (CSF replaces gray 71.5-83 mm, healthy materials) | frozen log | +6.05 | -0.87 | +0.76 | +14.69 | +1.59 | -1.22 | +0.85 | +7.91 |
| S3 gap only (CSF replaces gray 71.5-83 mm, healthy materials) | whitened log | +6.05 | -1.01 | +0.75 | +14.64 | +1.49 | -1.27 | +0.96 | +7.85 |
| S3 materials only (gray, white -> Mild, no geometry change) | Tikhonov dS | +8.33 | -0.03 | +0.35 | +8.32 | +0.45 | -0.14 | +0.11 | +4.35 |
| S3 materials only (gray, white -> Mild, no geometry change) | frozen log | +8.33 | -0.35 | +0.65 | +8.48 | +0.84 | -0.54 | +0.40 | +4.64 |
| S3 materials only (gray, white -> Mild, no geometry change) | whitened log | +8.33 | -0.35 | +0.56 | +8.48 | +0.76 | -0.50 | +0.45 | +4.55 |
| S3 deep white only (25-60 mm -> Mild) | Tikhonov dS | +0.30 | +0.06 | -0.08 | -0.48 | -0.05 | +0.03 | +0.00 | -0.30 |
| S3 deep white only (25-60 mm -> Mild) | frozen log | +0.30 | +0.10 | -0.09 | -0.50 | -0.07 | +0.07 | -0.03 | -0.32 |
| S3 deep white only (25-60 mm -> Mild) | whitened log | +0.30 | +0.11 | -0.09 | -0.49 | -0.08 | +0.08 | -0.03 | -0.32 |

**Mechanism.** The unknown is a 70–83.5 mm shell. A gap change sitting in that shell reads 2.5× its column-average truth, a material change of the whole column reads 1.0×, and a deep white-matter change (25–60 mm) reads ≈ 0 with the wrong sign. Leakage to the other sectors is ≤ 1.6.
**Verdict: CHANGED.** One 'sector value' does not measure one physical quantity; its meaning depends on the depth profile, and deep change is invisible. The real-data test would be an HFSS design with S3 materials changed and no CSF expansion (e = 0). It is listed as an open limitation, not built here.

## B17. Regularisation

κ: noise-weighted least squares of the Born prediction against Mild_lobe − Healthy_sliced (lobe_v1), per frequency. λ: GCV on Mild only (dS 0.158, log 0.126). Both are frozen. Key `b17`: calls (sectors | side | front/back) at λ × 0.3, 1, 3:

| design | reference | method | lambda x0.3 | lambda x1.0 | lambda x3.0 | flips |
|---|---|---|---|---|---|---|
| Mild | H7 | tikhonov dS | S2 S3 S5 S6 | none | none | S2 S3 S5 S6 | none | none | none | none | none | True |
| Mild | H7 | tikhonov log (gain-inv.) | S2 S3 S5 S6 | none | none | S2 S3 S5 S6 | none | none | none | none | none | True |
| Moderate | H7 | tikhonov dS | S1 S2 S3 S5 S6 | right | front | S1 S2 S3 S5 S6 | none | front | none | none | none | True |
| Moderate | H7 | tikhonov log (gain-inv.) | S1 S2 S3 S5 S6 | right | front | S1 S2 S3 S5 S6 | none | front | S6 | none | none | True |
| Severe | H7 | tikhonov dS | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | none | none | none | True |
| Severe | H7 | tikhonov log (gain-inv.) | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | S1 S3 S5 S6 | none | none | True |
| Mild (A) | H6 | tikhonov dS | S2 S3 S5 S6 | none | none | S2 S3 S6 | none | none | none | none | none | True |
| Mild (A) | H6 | tikhonov log (gain-inv.) | S2 S3 S5 S6 | none | none | S2 S3 S5 S6 | none | none | none | none | none | True |
| Moderate (A) | H6 | tikhonov dS | S1 S3 S5 S6 | right | front | S1 S3 S5 S6 | none | front | none | none | none | True |
| Moderate (A) | H6 | tikhonov log (gain-inv.) | S1 S2 S3 S5 S6 | right | front | S1 S2 S3 S5 S6 | none | front | none | none | none | True |
| Severe (A) | H6 | tikhonov dS | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | none | none | none | True |
| Severe (A) | H6 | tikhonov log (gain-inv.) | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | none | none | none | True |
| LeftOnly | H7 | tikhonov dS | S2 S3 | left | none | S3 | left | none | none | left | none | True |
| LeftOnly | H7 | tikhonov log (gain-inv.) | S2 S3 | left | none | S3 | left | none | none | left | none | True |
| LeftOnly | H6 | tikhonov dS | S3 | left | none | none | left | none | none | left | none | True |
| LeftOnly | H6 | tikhonov log (gain-inv.) | S3 | left | none | S3 | left | none | none | left | none | True |
| MCI | H7 | tikhonov dS | none | none | none | none | none | none | none | none | none | False |
| MCI | H7 | tikhonov log (gain-inv.) | none | none | none | none | none | none | none | none | none | False |
| MCI | H6 | tikhonov dS | none | none | none | none | none | none | none | none | none | False |
| MCI | H6 | tikhonov log (gain-inv.) | none | none | none | none | none | none | none | none | none | False |

**Verdict: CHANGED.** Sector calls flip with λ in 16 of 20 cases; only MCI is stable. At λ × 3 nearly every sector call disappears (shrinkage). At λ × 0.3, Moderate gains a false 'right' call. LeftOnly's side stays 'left' at every λ for both references. Sector calls are not results; the LeftOnly side call is λ-robust.

## B18. Fit frequencies and weighting

The three fit frequencies are the only ones with field exports (`data/fields`: 3p4, 3p6, 3p8). Weighting: each path, frequency and Re/Im component is whitened by its own typical-noise σ, so the frequencies are not weighted by hand. The exports that would settle frequency selection: `E_Normal_T{1..6}_{3p3,3p5,3p7,3p9}GHz.fld` (24 files) on the same ±90 mm volume, ideally 1 mm inside r 60–88 mm. Better still, exports of Healthy_sliced_new rather than the unsliced v2 Normal. Round 1 (b7_val) showed that interpolating kernels across 200 MHz is invalid.
**Verdict: CONFIRMED (why these three); CANNOT TELL (other frequencies)** until those exports exist.

## B19. Thresholds: from what, and when

From `lobe_frozen.json`: T_abs = max(T_null, T_mild). T_mild = midpoint between Mild's largest healthy sector (S1 11.4) and smallest affected sector (S5 16.2) against Healthy_sliced, which gives 13.81. T_LR = max(95 % of |LR| over the null inputs, largest |LR| of the symmetric Mild/Moderate/Severe) = 4.06. Null inputs: Healthy_sliced circulant residual, mirror residuals of Mild/Moderate/Severe, typical-noise draws.
Dates: pipeline frozen 2026-10-03 22:36:42 +0530 (fb5b775), predictions committed 2026-10-03 22:37:24 +0530 (62709e0). LeftOnly_test_c3 file written 2026-10-04 09:27:31, MCI_lobe_c3 2026-10-04 09:27:23, scored 2026-10-04 09:44:39 +0530. Mild_lobe file 2026-10-03 21:07:10. Glitch rule in `src/adstage/io/masking.py` since 89d4f23 2026-09-27 23:17:47 +0530.
**Verdict: CONFIRMED** that no threshold saw LeftOnly or MCI (frozen about 11 h before those files existed). **CHANGED** in wording: T_abs is tuned on Mild of the same head, array and mesh family, and it absorbs that geometry's healthy-sector bias (5–10). Mild, Moderate and Severe 'correct calls' are therefore in-sample (Mild) or same-family. That is a tuned classifier, not a geometry-free threshold.

## B20. Method count and family-wise view

Evaluated on the lobe data across §5–§8 and rounds 1–2: methods {Tikhonov dS, bounded dS, frozen log, frozen bounded log, whitened log (post-hoc)}; path sets {all 21, without opposite}; references {H7, H6}; calibrations {frozen, lobe_A}; fit-frequency subsets (7); λ × {0.3, 1, 3}; estimators {LR, LR_anti}; sets {lobe_v1, lobe_A, lobe_B}.
Key `b20`: 168 variants (4 frozen methods × 2 references × 7 frequency subsets × 3 λ), each applied to LeftOnly and to 7 symmetric null designs. LeftOnly: {'left': 121, 'right': 0, 'none': 47}. Null designs, 'left' calls: {'Mild_lobe': 2, 'Mild_lobe_new': 0, 'Moderate_lobe': 0, 'Moderate_lobe_c3': 0, 'Severe_lobe': 0, 'Severe_lobe_c3': 6, 'MCI_lobe_c3': 3} (total 11 of 1176, 0.9%); 'right' calls: {'Mild_lobe': 3, 'Mild_lobe_new': 2, 'Moderate_lobe': 51, 'Moderate_lobe_c3': 10, 'Severe_lobe': 4, 'Severe_lobe_c3': 0, 'MCI_lobe_c3': 0} (total 70, 6.0%).
**Family-wise.** Under the null, the expected number of 'left' calls among the 168 variants is 1.6 per design. LeftOnly has 121, and no null design exceeds 6. But 3 of 7 null designs get at least one 'left' call and 7 of them at least one side call. Reporting 'a left call exists in some variant' would therefore be meaningless. The pre-registered single variant is the test.
**Verdict: CHANGED (family-wise view added).** LeftOnly's left-call rate across variants (72%) is far outside the null rates (≤ 3.6%). Any single 'hit' picked from the variants carries no weight.

## B21. CRLB vs model error vs measurement

CRLB: Fisher information JᵀJ of the whitened Jacobian (typical-noise σ on both measurements, κ frozen, no model error, no gain error). Model error: max over Mild/Moderate/Severe of |x(HFSS data) − x(Born data from the truth)| per sector. Measurement SD: Prompt 07 model (±0.5 dB), primary method. Key `b21`:

| sector | crlb_dS | crlb_whitened_log | noise_sd_MC | meas_sd_05dB | model_error_max |
|---|---|---|---|---|---|
| S1 | 3.33 | 4.07 | 2.54 | 21.06 | 6.53 |
| S2 | 3.24 | 4.02 | 2.66 | 21.22 | 7.88 |
| S3 | 3.30 | 4.11 | 2.67 | 21.23 | 5.97 |
| S4 | 3.27 | 4.08 | 2.58 | 19.31 | 6.20 |
| S5 | 3.26 | 4.04 | 2.45 | 19.70 | 6.39 |
| S6 | 3.22 | 4.01 | 2.29 | 23.95 | 6.35 |

**Verdict: CHANGED.** The CRLB (3.2–4.1) understates the real uncertainty. Model error (6–8) is about twice the CRLB, and with the frozen dS method under measurement errors the SD is 12–26, as large as the changes (13–20). In simulation, sectors are identifiable only at the 2× model-error level (> ~16). In measurement, no sector is identifiable with the frozen dS method.

## B22. Floors

Moderate_lobe's floor is explained in R1(b): mesh asymmetry of that pass-5 file, halved at pass 6. Under the 4.0 floor, LeftOnly LR_anti is 1.93× (Tikhonov dS): **not separable**; frozen log 2.35×, whitened log 2.76× (sensitive). **Verdict: CONFIRMED** (round-1 label stands; cause now explained).

## B23. Matched reference

Re-derived in round 1 (lobe_review.json b4) and unchanged. With Healthy_sliced_new the primary method calls **nothing** (S2 11.1, S3 12.3 < 13.8): pre-registered verdict **FAIL**. Frozen log: PARTIAL. The shift equals the Healthy 7−6 one-pass inversion (≤ 0.05 difference per sector). The 7-pass reference should **not** be believed more. It is primary only because it was pre-registered and T_abs lives in its frame; neither reference makes the sector calls robust. **Verdict: CONFIRMED** (as stated in round 1).

## B24. Bias-corrected front/back

Bias = mean front/back of Mild and Severe in the same set and reference (true FB ≈ 0); uncertainty = half-range of the two ⊕ clean ruler of Moderate's FB. Key `b24`:

| set | method | FB_Moderate | FB_Mild | FB_Severe | FB_MCI | bias | bias_halfrange | clean_ruler | corrected | uncertainty | ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lobe_A | Tikhonov dS | +10.16 | +3.85 | +3.84 | -0.84 | +3.85 | +0.00 | +4.58 | +6.31 | +4.58 | +1.38 |
| lobe_A | frozen log | +10.44 | +3.92 | +4.14 | -0.30 | +4.03 | +0.11 | +4.07 | +6.41 | +4.07 | +1.58 |
| lobe_A | whitened log | +10.30 | +2.30 | +4.86 | -0.74 | +3.58 | +1.28 | +3.34 | +6.72 | +3.57 | +1.88 |
| lobe_B | Tikhonov dS | +10.80 | +3.11 | +3.64 | -0.86 | +3.38 | +0.26 | +2.30 | +7.42 | +2.31 | +3.21 |
| lobe_B | frozen log | +10.86 | +3.81 | +3.60 | -0.06 | +3.71 | +0.11 | +1.80 | +7.16 | +1.80 | +3.98 |
| lobe_B | whitened log | +10.25 | +2.69 | +3.94 | -0.65 | +3.32 | +0.62 | +1.63 | +6.93 | +1.75 | +3.97 |

**Verdict: CHANGED.** Something is left: corrected Moderate FB 6.3–7.4 (truth +14.6, so about half is recovered). In lobe_B it is 3.2–4.0× its clean uncertainty (established); in lobe_A 1.4–1.9× (not separable). Front/back after bias correction is **set-dependent**. It is established only on the better converged set, so it is mesh-sensitive, and it is not separable with measurement errors for the frozen methods.

## B25. Per-port contributions

Exact decomposition of each quantity of the primary method into paths, with reflections assigned to their port and transmissions split half/half between the two ends. Key `b25`:

| design | quantity | value | T1 | T2 | T3 | T4 | T5 | T6 | largest_port | largest_share |
|---|---|---|---|---|---|---|---|---|---|---|
| LeftOnly | S2 | +13.11 | +1.20 | +11.59 | +0.70 | -0.65 | +0.15 | +0.12 | T2 | 0.80 |
| LeftOnly | S3 | +15.02 | -0.26 | +0.76 | +12.45 | +1.73 | +0.11 | +0.23 | T3 | 0.80 |
| LeftOnly | LR | +8.48 | +0.78 | +6.47 | +6.78 | +0.92 | -3.25 | -3.22 | T3 | 0.32 |
| Moderate (A) | S1 | +15.48 | +15.05 | +1.23 | -0.61 | +0.42 | -1.05 | +0.43 | T1 | 0.80 |
| Moderate (A) | FB | +10.16 | +14.83 | +2.17 | +0.46 | -9.47 | +0.33 | +1.84 | T1 | 0.51 |

**Mechanism.** Every sector value is about 80 % from its own antenna (S2 ← T2, S3 ← T3, S1 ← T1). That is geometric, since each sector is centred on its antenna, and it is the 'which antenna sits over the change' reading of R3. LR is spread over T2/T3 (+) and T5/T6 (−), with no port above 32 %. A per-port gain, phase or mismatch bias of the single-layer kind cannot produce LR: the whitened log, which is exactly invariant to per-port complex factors, gives the same LR (+9.3).
**Verdict: CONFIRMED** that LR does not exploit per-port biases. **CHANGED** in meaning: each sector call is essentially that antenna's own local measurement.

## G. Geometry and antennas

**G1 Layers.** From the audit (`data/hfss_geometry_audit_Healthy_sliced.txt`): r_skin 88, r_fat 87.5, r_skull 86.5, r_csf_outer 83.5, gray 83 − e_k, white 76 − e_k, r_hip 25 mm; thicknesses skin 0.5, fat 1.0, skull 3.0, CSF 0.5, gray 7, white 51 mm. `imaging/common.py` uses the same radii. (a) Shehab 2025 Table 6 is not in the repository, so the source is **UNVERIFIED**. G7 shows Table 5's materials equal Gabriel at 3.25 GHz, so the material source is a literature model. (b) With 2 mm CSF and a 6 mm skull, every quantitative imaging result would change: kernels, gap-layer sensitivity share, Born error. Mechanism: the CSF layer (εr 65, σ 4.3) is where most of the near-field sensitivity sits (gap share 0.56 for T2–T3). **CANNOT TELL** the size without re-simulation. Model limitation.
**G2 Leftover variables.** Confirmed defined in the audit (r_brain 95, r_csf 95.5, r_gray 70.55, r_white 17.5, r_brain_ad 61.68, r_csf_inner 61.68, r_csf_expanded 64.6, ant_dist 115) and not used by the listed sliced objects. Which variables the v1/v2 objects used is **UNVERIFIED** (no audit of v2). Imaging depends on it through the kernels (v2 Normal fields as background) and the old §5b comparison (superseded).
**G3 Array / polarisation.** Feeds at r = 97.15 mm, z = 56.1 mm, polar 54.7°; port sheets at r = 97.70, z = 48.06; the patch faces the head (feed 97.15 < ground 97.65). Measured polarisation just inside the skin in front of each antenna (key `fields.g3`): E along the meridian (θ̂) 27.3–27.6, along the ring (φ̂) ≤ 0.56, radial 3.8–6.5. Ring share 0.0004. **CHANGED**: the polarisation is meridional, not the 65/35 θ/φ mix assumed in `common.py` (that figure was for a region, not boresight). z_ebg: **UNVERIFIED**; no imaging result uses it (fields come from HFSS).
**G4 Port ↔ position.** Key `fields.g4`: the field maximum on the r = 85 mm shell of each export file lies at its antenna's azimuth: T1 -90°, T2 -30°, T3 +30°, T4 +90°, T5 +150°, T6 -150° (z ≈ 49 mm). This covers files 3, 5, 6 as well. With the audit's excitation order (FEED_3_T4, T3, T2, T1, T6, T5 = Port 1..6) the left/right convention is **CONFIRMED** for every port.
**G5 Height coverage.** Key `fields.g5` (|E_a·E_b| over head voxels, 3.6 GHz): z > 40 mm 54%–70%, 0–40 mm 27%–44%, z < 0 ≤ 4%. **CHANGED (meaning)**: the 'lobes' are azimuthal wedges of the upper head. 'Temporal L' is the cap wedge above the left temporal lobe, not the temporal lobe itself.
**G6 Inner structure.** The audit confirms GM_Sk radius 83 mm − e_Sk, WM_Sk 76 mm − e_Sk, CSF_outer = r_csf_outer, hippocampus r_hip. MCI_lobe's Ventricle_CSF and the v2 skull hole are **UNVERIFIED** (no audit). Depends on them: the kernels (v2 background) and the Born error.
**G7 Materials.** Key `g7`: my Gabriel 1996 four-pole parameters reproduce the published 1 GHz values exactly (gray 52.28/0.985, white 38.58/0.622, CSF 68.44/2.455). The Shehab healthy constants match Gabriel at 3.24–3.25 GHz, so the HFSS materials are the 3.25 GHz values held constant over 3.2–4.2 GHz. Dispersion over the band:

| tissue | shehab_eps | shehab_sigma | gabriel_1GHz | published_1GHz | best_match_GHz | Gabriel 3.2 GHz | Gabriel 3.7 GHz | Gabriel 4.2 GHz |
|---|---|---|---|---|---|---|---|---|
| gray | 47.7 | 2.42 | 52.28 / 0.985 | 52.28 / 0.985 | 3.25 | 47.7 / 2.38 | 47.0 / 2.81 | 46.3 / 3.28 |
| white | 35.3 | 1.65 | 38.58 / 0.622 | 38.58 / 0.622 | 3.24 | 35.3 / 1.63 | 34.8 / 1.94 | 34.3 / 2.27 |
| csf | 65 | 4.27 | 68.44 / 2.455 | 68.44 / 2.455 | 3.24 | 65.1 / 4.22 | 64.2 / 4.81 | 63.4 / 5.46 |

εr changes by about 3 %, σ by +29 to +38 % across the band. The simulation is self-consistent, so no result inside it is affected, but realism above 3.3 GHz is. AD values: provenance and uncertainty **UNVERIFIED**. CSF is one object, so LeftOnly carries CSF_Mild on the right too (the imaging truth includes it).
**G8.** See R7: volume exports, no cut-plane. **CONFIRMED.**

## C. Phase finding (POST-HOC throughout)

**C1.** Labelled POST-HOC in the first line of this file, of `lobe_report.md` §9 and of the claims table. The pre-registered imaging answer (PARTIAL / FAIL by reference) stays primary.
**C2. Phase convergence.** Key `c2_paths`: per path, level (dB) and one-pass phase changes at 3.4/3.6/3.8 GHz:

| path | type | level_dB_fit | Healthy 7 − 6 phase deg | Mild 6 − 5 phase deg | Moderate 6 − 5 phase deg | Severe 6 − 5 phase deg | LeftOnly − H6 phase deg |
|---|---|---|---|---|---|---|---|
| T1 refl. | reflection | -8.7, -10.4, -6.0 | -1.2, +1.9, +0.8 | -1.7, +1.4, +1.1 | -1.6, +1.8, +0.6 | -1.5, +2.1, +0.9 | +1.3, +0.2, -0.5 |
| T1-T2 | neighbour | -38.8, -32.7, -35.5 | +1.4, +1.2, +2.1 | +2.4, +2.7, +5.2 | +1.8, +1.9, +3.2 | +1.6, +2.9, +2.6 | -5.5, -4.5, -0.2 |
| T1-T3 | second-neighbour | -51.7, -58.5, -61.7 | +1.0, -0.6, +6.5 | +3.5, +3.0, -1.0 | +1.5, +3.7, +10.8 | +1.1, +6.6, +17.7 | +4.0, +0.8, +0.1 |
| T1-T4 | opposite | -47.4, -48.2, -56.6 | +2.1, +1.8, +1.2 | +2.9, +4.0, +1.3 | +2.4, +3.5, +1.4 | +2.5, +5.6, -3.5 | +0.4, +2.7, -0.0 |
| T1-T5 | second-neighbour | -51.8, -58.4, -62.6 | +1.2, +2.4, +5.2 | +3.8, +4.7, +5.4 | +3.4, +3.1, +1.6 | +1.8, +1.9, +10.8 | +0.4, -7.9, -1.9 |
| T1-T6 | neighbour | -38.8, -32.5, -35.7 | +1.5, +2.0, +2.2 | +2.6, +2.9, +6.3 | +2.4, +1.9, +4.6 | +1.3, +2.6, +4.0 | -1.8, -1.9, -0.2 |
| T2 refl. | reflection | -8.7, -10.3, -6.1 | -1.2, +1.6, +0.6 | -2.5, +2.1, +0.4 | -1.6, +1.4, +0.5 | -1.6, +1.3, +0.6 | +6.4, -1.1, -2.0 |
| T2-T3 | neighbour | -38.8, -32.6, -35.7 | +1.7, +0.8, +2.1 | +1.8, +2.8, +5.6 | +1.9, +2.2, +4.7 | +1.5, +2.8, +5.3 | -8.5, -7.6, -2.4 |
| T2-T4 | second-neighbour | -51.7, -58.0, -61.7 | +1.1, +2.7, +0.8 | +4.4, +4.3, +12.9 | +2.7, +1.3, +2.4 | +0.2, +3.6, +15.0 | +5.9, -2.4, +1.0 |
| T2-T5 | opposite | -47.5, -48.4, -57.0 | +3.2, +2.6, +2.5 | +3.1, +5.8, +3.1 | +3.3, +5.4, +3.4 | +2.2, +5.7, +8.9 | +0.6, +3.1, -3.5 |
| T2-T6 | second-neighbour | -51.6, -58.8, -62.4 | +1.0, +4.1, +10.2 | +3.3, +3.5, +14.0 | +3.5, +3.1, +10.0 | +4.2, +5.1, +17.1 | +5.1, +1.6, -4.0 |
| T3 refl. | reflection | -8.7, -10.2, -5.9 | -1.1, +1.6, +0.9 | -1.9, +1.4, +1.1 | -1.8, +1.9, +0.7 | -1.7, +1.6, +0.1 | +7.0, -1.9, -0.8 |
| T3-T4 | neighbour | -38.7, -32.5, -35.7 | +1.5, +1.8, +1.9 | +2.4, +1.9, +3.0 | +1.8, +1.0, +3.4 | +1.5, +2.0, +4.6 | -6.1, -5.0, +0.2 |
| T3-T5 | second-neighbour | -51.7, -58.0, -62.4 | +1.7, -0.1, +5.3 | +3.8, +6.9, +8.0 | +3.0, +4.4, +10.0 | +7.2, +3.4, +13.4 | +3.6, -8.1, -9.9 |
| T3-T6 | opposite | -47.4, -48.4, -57.7 | +3.0, +3.4, +2.5 | +3.0, +6.6, +4.5 | +3.5, +5.8, +4.4 | +2.5, +5.9, -2.8 | +1.0, +5.2, -2.1 |
| T4 refl. | reflection | -8.8, -10.4, -6.1 | -1.1, +1.5, +0.9 | -1.8, +1.2, +0.8 | -2.2, +2.9, +1.2 | -1.6, +1.9, +1.4 | +1.5, -0.5, -0.8 |
| T4-T5 | neighbour | -38.7, -32.5, -35.4 | +1.3, +0.9, +1.8 | +2.8, +2.6, +3.9 | +1.9, +3.4, +5.8 | +1.6, +3.1, +3.6 | -2.4, -1.7, -0.6 |
| T4-T6 | second-neighbour | -51.9, -58.6, -61.9 | +2.1, +1.6, +5.1 | +6.3, +5.9, +10.4 | +3.0, +5.5, +7.4 | +2.7, +3.5, +15.2 | +1.8, -1.5, -1.7 |
| T5 refl. | reflection | -8.8, -10.4, -6.0 | -1.3, +1.8, +0.8 | -1.8, +1.3, +0.8 | -2.1, +2.0, +0.9 | -1.4, +1.7, +0.9 | +1.7, -0.8, -0.4 |
| T5-T6 | neighbour | -38.9, -32.5, -35.5 | +1.9, +1.8, +3.0 | +2.5, +2.8, +5.3 | +3.4, +4.3, +6.3 | +1.7, +3.2, +5.8 | -2.7, -1.7, -0.5 |
| T6 refl. | reflection | -8.9, -10.5, -5.9 | -1.1, +1.6, +0.9 | -2.5, +2.2, +1.0 | -1.5, +0.9, +0.4 | -1.6, +1.6, +0.8 | +2.1, -1.3, -1.4 |

Key `c2_lr`: amplitude and phase parts of LR for every one-pass difference and for LeftOnly:

| difference | method | LR | LR_amp_part | LR_phase_part |
|---|---|---|---|---|
| Healthy 7 − 6 | Tikhonov dS | +0.34 | -0.18 | +0.53 |
| Healthy 7 − 6 | frozen log | +0.29 | -0.12 | +0.41 |
| Healthy 7 − 6 | whitened log | -0.07 | -0.27 | +0.21 |
| Mild 6 − 5 | Tikhonov dS | +0.52 | -0.19 | +0.75 |
| Mild 6 − 5 | frozen log | +0.68 | -0.14 | +0.82 |
| Mild 6 − 5 | whitened log | +0.19 | -0.36 | +0.56 |
| Moderate 6 − 5 | Tikhonov dS | +2.14 | +0.01 | +2.08 |
| Moderate 6 − 5 | frozen log | +2.17 | +0.27 | +1.90 |
| Moderate 6 − 5 | whitened log | +1.59 | +0.21 | +1.38 |
| Severe 6 − 5 | Tikhonov dS | +1.17 | +0.67 | +0.51 |
| Severe 6 − 5 | frozen log | +1.10 | +0.69 | +0.41 |
| Severe 6 − 5 | whitened log | +0.78 | +0.76 | +0.03 |
| LeftOnly − H6 | Tikhonov dS | +8.82 | +1.14 | +7.54 |
| LeftOnly − H6 | frozen log | +9.70 | +1.15 | +8.55 |
| LeftOnly − H6 | whitened log | +9.41 | +1.24 | +8.17 |

For the neighbour paths that carry LR, the one-pass phase change is 0.8–6.3°. LeftOnly's T2–T3 change is −8.5/−7.6° at 3.4/3.6 GHz (4.5× and 2.7× the largest one-pass change) but −2.4° at 3.8 GHz (below it). The weak second-neighbour entries (−52 to −62 dB) have one-pass phase changes up to 17.7°, which is where ΔS 0.02 gives no control, as the objection says. The phase part of LR is +7.54 against at most 2.08 for any one-pass difference (3.6×). **Verdict: CHANGED (quantified).** At 3.4/3.6 GHz the effect is not mesh at the one-pass level; at 3.8 GHz and on weak paths it is.
**C3. Null distribution.** Key `r2.views.per_file`: for each symmetric file, the number of the 18 statistics ≥ 3× a leave-one-out ruler from the other eight. Band mean, rms rule: Healthy_sliced 0, Healthy_sliced_new 0, Mild_lobe 0, Mild_lobe_new 0, Moderate_lobe 0, Moderate_lobe_c3 0, Severe_lobe 0, Severe_lobe_c3 0, MCI_lobe_c3 0. Max rule: all 0. LeftOnly: 12 (rms) / 3 (max). **Verdict: CONFIRMED** that LeftOnly's count lies outside the null distribution (no null file above 1/18). Its rank among the ten files is first, so p = 0.1: the same limit as R1.
**C4. Physical sign** (predicted in 0ceb626: negative, −5 to −25°; not blind). Key `c4`:

| f_GHz | T2-T3 dphi vs Healthy_sliced_new | T5-T6 dphi vs Healthy_sliced_new | T2-T3 dphi vs Healthy_sliced | T5-T6 dphi vs Healthy_sliced | |S22| dB | |S66| dB | |S23| dB | |S56| dB |
|---|---|---|---|---|---|---|---|---|
| 3.20 | -3.3 | -0.9 | -3.9 | -1.4 | -1.2 | -1.2 | -52.9 | -52.9 |
| 3.25 | -5.0 | -1.4 | -5.8 | -2.0 | -1.8 | -1.8 | -49.4 | -49.4 |
| 3.30 | -7.0 | -2.0 | -7.9 | -2.9 | -2.9 | -2.9 | -45.7 | -45.7 |
| 3.35 | -8.4 | -2.5 | -9.6 | -3.9 | -4.9 | -4.9 | -41.9 | -41.9 |
| 3.40 | -8.5 | -2.7 | -10.2 | -4.6 | -8.7 | -8.9 | -38.8 | -38.9 |
| 3.45 | -7.7 | -2.3 | -9.3 | -4.1 | -14.1 | -14.4 | -37.1 | -37.1 |
| 3.50 | -7.7 | -2.0 | -8.8 | -3.5 | -12.0 | -12.1 | -36.1 | -36.0 |
| 3.55 | -9.0 | -2.4 | -9.6 | -4.6 | -9.6 | -9.6 | -34.8 | -34.6 |
| 3.60 | -7.6 | -1.7 | -8.4 | -3.6 | -10.3 | -10.5 | -32.6 | -32.5 |
| 3.65 | -6.0 | -3.2 | -8.2 | -6.5 | -19.6 | -19.7 | -30.1 | -30.2 |
| 3.70 | -4.8 | -3.5 | -7.0 | -7.1 | -9.2 | -9.0 | -30.8 | -30.8 |
| 3.75 | -4.1 | -1.8 | -5.8 | -4.7 | -5.1 | -5.0 | -34.0 | -34.0 |
| 3.80 | -2.4 | -0.5 | -4.5 | -3.5 | -6.1 | -5.9 | -35.7 | -35.5 |
| 3.85 | -1.7 | +0.2 | -3.5 | -2.7 | -4.5 | -4.5 | -41.9 | -41.7 |
| 3.90 | -4.5 | -0.6 | -5.3 | -2.1 | -1.9 | -1.9 | -51.5 | -51.4 |
| 3.95 | -6.6 | -0.6 | -7.2 | -1.8 | -1.2 | -1.2 | -57.4 | -57.2 |
| 4.00 | -6.9 | -0.9 | -7.4 | -1.9 | -0.8 | -0.8 | -60.3 | -60.2 |
| 4.05 | -6.6 | -0.9 | -7.0 | -1.8 | -0.7 | -0.7 | -62.4 | -62.3 |
| 4.10 | -6.2 | -0.9 | -6.5 | -1.7 | -0.6 | -0.6 | -64.1 | -64.0 |
| 4.15 | -5.8 | -0.8 | -6.1 | -1.6 | -0.5 | -0.5 | -65.4 | -65.4 |
| 4.20 | -5.5 | -0.8 | -5.6 | -1.6 | -0.4 | -0.4 | -66.5 | -66.5 |

Notches (local minima ≥ 6 dB below the band median) on T2–T3, T5–T6, T1–T2, T3–T4: none. Resonances: all six antennas at 3.656–3.660 GHz (R3).
Measured T2–T3 change (vs H6): −7.0 to −9.0° at 3.30–3.60 GHz, which is the predicted sign and inside the predicted range. The mirror path T5–T6 changes −1.7 to −2.7°: the CSF_Mild layer on the right, plus wrap-around. **Band dependence:** the asymmetry is present at 3.2–3.65 GHz, dips at 3.70–3.85 GHz (just above the common antenna resonance at 3.657 GHz, where |S23| peaks), and returns at 3.9–4.2 GHz, where the paths are weak (−51 to −66 dB). There is no notch. **Verdict: CONFIRMED (sign and size as predicted, not blind); CHANGED (band):** 'gone at 3.70–3.85' holds only for that window; the asymmetry is back above 3.9 GHz.
**C5. Measurement level.** Cross-ratios cancel per-port complex gain and phase (exactly, including cable flex that is constant over the sweep). They do not cancel per-entry noise, frequency error, antenna position error or frequency-dependent cable flex. Under the Prompt 07 model (per-entry 0.25 dB / 2°, 1 MHz jitter, per-port gain and phase), the median SD of the band-mean cross-ratio phase is 2.3°. Statistics ≥ 3× the measured ruler: ±0.5 dB gain: 0/18 (rms) / 0/18 (max); ±2 dB gain, ±10° phase: 0/18 (rms) / 0/18 (max). Imaging LR_anti with measurement errors: ≤ 2.2× (round 1). Position error and frequency-dependent flex are not modelled: **CANNOT TELL**, settled by HFSS re-solves with each antenna displaced ±1 mm.
**C6. Replication.** Proposed and committed before computing (0ceb626): **RightOnly_test** (e = 0/0/0/0/11.5/7.5, r_hip 17.5, Mild materials, CSF_Mild, stop rule 1). Imaging prediction: LR = −6.9 ± 3.9 vs Healthy_sliced_new, > 70 % phase; replicated if the sign is right and |LR| ≥ 2 × largest |null|. Not coordinated with the main session.

## Final table

| item | verdict | change | evidence |
|---|---|---|---|
| R1 floor rule | CHANGED; CANNOT TELL (p < 0.1) | 3.7× (rms) vs 1.81× → one rule (max): 1.93×; rank p 0.1; Moderate outlier = file mesh (-4.07 → -1.93 at +1 pass) | lobe_round2.json: r1 |
| R2 same quantity | CHANGED | 16/22 (rms) vs pair 0.9× → 12/18 distinct ≥3× rms, 3/18 max rule; 12/18 ≥3× one-pass | lobe_round2.json: r2 |
| R3 detuning | CHANGED (rejected for transmissions) | untested → per-port factors explain ≤ 19% of the antisymmetric change; no resonance shift; left reflection depth +0.9–1.0 dB | lobe_round2.json: r3 |
| R4 detection feature | CONFIRMED (defensible on training data; fragile) | R31 margins: lobe Severe 1.9–2.3, LeftOnly 1.3 yard; R21 monotonic but lobe Mild < 1 yard | lobe_round2.json: r4 |
| R5 report sectors? | CHANGED | sector values reported → only signs (LR) and bias-corrected FB | lobe_round2.json: b17, b21, b16, b25 |
| R6 detection ruler | n/a (main) | imaging rulers include measurement spread (quadrature) | lobe_review.json: b1 |
| R7/G8 field geometry | CONFIRMED | volume ±90 mm, 3 mm, z −90…+90; no cut-plane | lobe_round2.json: fields.grid; file headers |
| B14 kernels/Born | CHANGED | Born error sym 0.50–0.58, antisym 0.92–0.96; grid 24 % | lobe_round2.json: b14_born, fields.b14_grid |
| B15 kernel asymmetry | CONFIRMED (effect ≤ 0.3); cause identified | unknown → ½ array −0.4° offset, ½ v2 mesh | lobe_round2.json: fields.b15 |
| B16 sector vs depth | CHANGED; real-design test CANNOT TELL | gap reads 2.5×, materials 1.0×, deep ≈ 0 | lobe_round2.json: b16 |
| B17 λ | CHANGED | calls flip in 16/20; LeftOnly side stable; Moderate false 'right' at ×0.3 | lobe_round2.json: b17 |
| B18 fit frequencies | CONFIRMED; CANNOT TELL (others) | only exports; 24 named exports needed | data/fields; lobe_review.json: b7_val |
| B19 thresholds | CONFIRMED (dates) / CHANGED (wording) | ‘not tuned on test’ → tuned on Mild of the same family; Mild calls in-sample | lobe_frozen.json; git dates |
| B20 method count | CHANGED | none → 168 variants: LeftOnly left 121/168, nulls ≤ 6/168 | lobe_round2.json: b20 |
| B21 CRLB | CHANGED | CRLB 3.3 → model error 6–8, measured SD 12–26 (dS) | lobe_round2.json: b21 |
| B22 floors | CONFIRMED | LeftOnly 1.93× under floor 4.0 (not separable) | lobe_round2.json: r1 |
| B23 matched reference | CONFIRMED | primary: PARTIAL (H7) / FAIL (H6); H7 not more credible | lobe_review.json: b4 |
| B24 FB bias-corrected | CHANGED | 'not established' → corrected 6.3–7.4; lobe_B 3.2–4.0×, lobe_A 1.4–1.9× | lobe_round2.json: b24 |
| B25 per-port | CONFIRMED (no port bias) / CHANGED (meaning) | sector ≈ 80 % own antenna; LR max port share 0.32 | lobe_round2.json: b25 |
| G1 layers | CONFIRMED (radii); UNVERIFIED (Table 6 source) | skin 0.5, skull 3, CSF 0.5 mm; thick-layer effect CANNOT TELL | audit; imaging/common.py |
| G2 leftovers | CONFIRMED (unused); v2 UNVERIFIED | — | audit |
| G3 polarisation | CHANGED | 65/35 θ/φ mix → meridional (ring share ≈ 0) | lobe_round2.json: fields.g3 |
| G4 port ↔ position | CONFIRMED | all six files at their antenna azimuth | lobe_round2.json: fields.g4 |
| G5 height | CHANGED (meaning) | z > 40 mm 54–70 %, z < 0 ≤ 4 % | lobe_round2.json: fields.g5 |
| G6 inner | CONFIRMED (sliced); UNVERIFIED (MCI ventricle, v2 skull) | — | audit |
| G7 materials | CHANGED | unknown frequency → Gabriel at 3.25 GHz, constant; σ +29–38 % over band | lobe_round2.json: g7 |
| C1 post-hoc label | CHANGED | unlabelled → POST-HOC first line; pre-registered PARTIAL/FAIL primary | this file; lobe_report §9 |
| C2 phase convergence | CHANGED (quantified) | LR phase part +7.54 = 3.6× one-pass; T2–T3 4.5×/2.7× at 3.4/3.6, < 1× at 3.8; weak paths 18° | lobe_round2.json: c2_paths, c2_lr |
| C3 null distribution | CONFIRMED (outside); p ≥ 0.1 | nulls ≤ 1/18 vs LeftOnly 12/18 (rms), 3/18 (max) | lobe_round2.json: r2.views.per_file |
| C4 physical sign | CONFIRMED (sign); CHANGED (band) | predicted −5…−25°, observed −7…−9°; asymmetry returns above 3.9 GHz | lobe_round2.json: c4; round2_predictions.md |
| C5 measurement level | CHANGED; CANNOT TELL (position) | 0/18 (rms), 0/18 (max) at ±0.5 dB | lobe_round2.json: r2.measured |
| C6 replication design | proposed | RightOnly_test + decision rule | round2_predictions.md (0ceb626) |

## Claims table (rebuilt from scratch: CONFIRMED / CHANGED items only)

| claim | verdict | items |
|---|---|---|
| Kernels come from 3-D volume field exports (±90 mm, 3 mm, 3.4/3.6/3.8 GHz, six excitations) of the v2 Normal head; no cut-plane was used | CONFIRMED | R7/G8 |
| Each field export peaks at its antenna's azimuth; the Port 1..6 = T4,T3,T2,T1,T6,T5 order and +X = subject's left hold for all ports | CONFIRMED | G4 |
| The array's sensitivity lies 54–70 % above z = 40 mm and ≤ 4 % below z = 0; 'lobes' are azimuthal wedges of the upper head | CHANGED | G5 |
| The antenna near field in front of each antenna is meridionally polarised | CHANGED | G3 |
| HFSS tissue values equal Gabriel 1996 at 3.25 GHz, held constant; true σ rises 29–38 % over 3.2–4.2 GHz | CHANGED | G7 |
| Born linearisation error: 50–58 % on the symmetric and 92–96 % on the antisymmetric part of LeftOnly; kernels move 24 % with the export grid | CHANGED | B14 |
| Sector values and per-sector calls are not results: they flip with λ, reference and calibration, depend on depth profile, and are ≈ 80 % their own antenna | CHANGED | R5, B16, B17, B21, B25 |
| Pre-registered blind test: PARTIAL with the frozen 7-pass reference, FAIL with the matched reference; neither reference is more credible | CONFIRMED | B23 |
| [POST-HOC] LeftOnly left/right sign is in the data (mirror test) and stable over λ, references and kernel symmetrisation; size 1.93× (Tikhonov dS) to 2.77× (whitened log) the clean ruler under the fixed max-floor rule: not established; rank p = 0.1 with nine nulls | CHANGED | R1, B22 |
| [POST-HOC] 85–88 % of the LeftOnly LR comes from phase; it is not per-antenna detuning (per-port factors explain ≤ 20 %) | CHANGED | R3, C2 |
| [POST-HOC] Cross-ratio phases: 12/18 distinct statistics ≥ 3× under the rms rule, 3/18 under the max rule; no symmetric file exceeds 1/18; with measurement errors (±0.5 dB) 0/18 (rms) and 0/18 (max) | CHANGED | R2, C3, C5 |
| Moderate_lobe's large mirror residual is mesh asymmetry of that pass-5 file (halved one pass later) | CHANGED | R1 |
| Left antennas' reflection depth changes by 0.9–1.0 dB (3–6× one-pass); resonance frequencies do not move | CHANGED | R3 |
| Phase change of the left neighbour path is negative (delay), −7 to −9° at 3.30–3.60 GHz, as the CSF-gap physics predicts | CONFIRMED | C4 |
| Bias-corrected Moderate front/back is 6.3–7.4 (truth 14.6): established in lobe_B (3.2–4.0×), not in lobe_A (1.4–1.9×); mesh-sensitive | CHANGED | B24 |
| MCI_lobe shows nothing beyond the rulers in any variant (never flips with λ, reference or calibration) | CONFIRMED | B17, round 1 |
| R31 detection is defensible on the uniform training data and fragile on lobe Severe/LeftOnly; no single feature determines every lobe design | CONFIRMED | R4 |
| Thresholds were frozen before LeftOnly/MCI existed but tuned on Mild of the same head; Mild calls are in-sample | CHANGED | B19 |

## Open limitations (CANNOT TELL / UNVERIFIED)

- Floor significance: nine symmetric solves cap the rank p at 0.1; ≥ 19 independent symmetric solves (rotated meshes) needed (R1, C3).
- Fit frequencies other than 3.4/3.6/3.8 GHz: needs 24 named field exports (B18).
- Antenna position error and frequency-dependent cable flex at measurement level: needs ±1 mm displaced-antenna re-solves (C5).
- Realistic layers (2 mm CSF, 6 mm skull) and the Shehab Table 6 source: needs the paper and re-simulation (G1).
- v1/v2 radius variables and v2 skull hole; MCI_lobe Ventricle_CSF: needs geometry audits of those designs (G2, G6).
- AD material provenance and uncertainty (G7).
- Sector model vs real depth profiles on HFSS data: needs an S3 materials-only design (B16).
- Replication of the left/right sign on an independent mesh: RightOnly_test (C6) pending.
- z_ebg geometry meaning (G3): unverified, no imaging result depends on it.
- Items A14–A28 (data handling, statistics, staging of the frozen rule): main session.

