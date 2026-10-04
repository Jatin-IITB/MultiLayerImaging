# Test_B (blind): estimates under the committed protocol

Protocol `results/imaging/testb_protocol.md`, committed in `24aa0c4` before Test_B was loaded. Run: `python imaging/score_testb.py --n 200` at code `24aa0c4-dirty`. Frozen pipeline `lobe_frozen.json` (fb5b775). Estimates only; the truth is held by the user.

## QC (S-parameters only)

| points | f_min_GHz | f_max_GHz | same_grid | max_singular_value | passive | max_recip_err_dB_re_band | max_amp_nonrecip_dB | n_masked | masked_at_fit_freq |
|---|---|---|---|---|---|---|---|---|---|
| 201 | 3.20 | 4.20 | True | 0.9512 | True | -25.9 | 0.39 | 3 | False |

Masked points:

| f_GHz | ports | recip_err_dB | at_fit_freq |
|---|---|---|---|
| 3.840 | 4-6 | -28.5 | False |
| 3.845 | 4-6 | -25.9 | False |
| 3.850 | 4-6 | -27.3 | False |

## Data-level size (context, not a gate)

Whitened dS norm of Test_B − reference against the largest one-pass mesh difference (bar ≥ 3× established, 2–3× sensitive, < 2× not separable). Known designs' norms are shown alongside; LeftOnly is only 1.25–1.59×:

| reference | data_norm | one_pass_max_norm | ratio | label | norm Mild_lobe | norm Moderate_lobe | norm Severe_lobe | norm Mild_lobe_new | norm Moderate_lobe_c3 | norm Severe_lobe_c3 | norm LeftOnly_test_c3 | norm RightOnly_test | norm MCI_lobe_c3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 (Healthy_sliced, 7 passes) | 14.87 | 9.23 | 1.61 | not separable | 27.97 | 28.77 | 40.28 | 20.99 | 23.35 | 36.53 | 14.66 | 23.63 | 6.58 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | 11.75 | 9.22 | 1.27 | not separable | 23.64 | 25.10 | 37.53 | 17.42 | 20.70 | 34.53 | 11.55 | 19.24 | 3.90 |

## Sector map, LR, FB, frozen calls, fit residual

dε'' per sector (and dεr). Calls: frozen R1–R3. Residual = whitened relative misfit; rejected if > 1.5× the largest residual of the known cortical designs (Mild_lobe, Moderate_lobe, Severe_lobe, Mild_lobe_new, Moderate_lobe_c3, Severe_lobe_c3, LeftOnly_test_c3, RightOnly_test).

| reference | method | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | LR | LR_ratio | FB | FB_ratio | called | side | frontback | residual | residual_known_max | rejected |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 (Healthy_sliced, 7 passes) | Tikhonov dS | +4.90 | +14.67 | +6.52 | +4.17 | +13.12 | +6.55 | +0.76 | 0.19 | +0.73 | 0.19 | S2 | none | none | 0.513 | 0.578 | False |
| H7 (Healthy_sliced, 7 passes) | bounded dS | +4.90 | +14.67 | +6.52 | +4.17 | +13.12 | +6.55 | +0.76 | 0.19 | +0.73 | 0.19 | S2 | none | none | 0.513 | 0.578 | False |
| H7 (Healthy_sliced, 7 passes) | frozen log | +4.80 | +13.78 | +6.11 | +3.18 | +13.97 | +5.96 | -0.02 | 0.00 | +1.62 | 0.36 | S2 S5 | none | none | 0.524 | 0.545 | False |
| H7 (Healthy_sliced, 7 passes) | frozen bounded log | +4.80 | +13.78 | +6.11 | +3.18 | +13.97 | +5.96 | -0.02 | 0.00 | +1.62 | 0.36 | S2 S5 | none | none | 0.524 | 0.545 | False |
| H7 (Healthy_sliced, 7 passes) | whitened log (POST-HOC) | +3.94 | +13.56 | +5.60 | +2.81 | +12.98 | +5.45 | +0.36 | 0.12 | +1.13 | 0.23 | n/a (no frozen thresholds) | n/a | n/a | 0.552 | 0.567 | False |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | +2.76 | +12.71 | +3.78 | +1.98 | +10.71 | +3.53 | +1.13 | 0.32 | +0.77 | 0.20 | none | none | none | 0.546 | 0.549 | False |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | +2.76 | +12.71 | +3.78 | +1.98 | +10.71 | +3.53 | +1.13 | 0.32 | +0.77 | 0.20 | none | none | none | 0.546 | 0.549 | False |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | +3.07 | +12.69 | +4.23 | +1.80 | +12.25 | +3.85 | +0.41 | 0.12 | +1.27 | 0.31 | none | none | none | 0.540 | 0.524 | False |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | +3.07 | +12.69 | +4.23 | +1.80 | +12.25 | +3.85 | +0.41 | 0.12 | +1.27 | 0.31 | none | none | none | 0.540 | 0.524 | False |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log (POST-HOC) | +2.61 | +12.53 | +3.89 | +1.68 | +11.63 | +3.82 | +0.48 | 0.16 | +0.93 | 0.19 | n/a (no frozen thresholds) | n/a | n/a | 0.566 | 0.547 | False |

dεr (context):

| reference | method | eps_r S1 Fr | eps_r S2 TL | eps_r S3 PL | eps_r S4 Oc | eps_r S5 PR | eps_r S6 TR |
|---|---|---|---|---|---|---|---|
| H7 (Healthy_sliced, 7 passes) | Tikhonov dS | -1.49 | -3.51 | -1.06 | -1.49 | -1.88 | -2.76 |
| H7 (Healthy_sliced, 7 passes) | bounded dS | -1.49 | -3.51 | -1.06 | -1.49 | -1.88 | -2.76 |
| H7 (Healthy_sliced, 7 passes) | frozen log | -1.52 | -2.26 | -0.37 | -0.06 | -1.16 | -0.59 |
| H7 (Healthy_sliced, 7 passes) | frozen bounded log | -1.52 | -2.26 | -0.37 | -0.06 | -1.16 | -0.59 |
| H7 (Healthy_sliced, 7 passes) | whitened log (POST-HOC) | -1.79 | -2.37 | -0.64 | -0.54 | -1.26 | -0.52 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | -1.41 | -3.44 | -1.66 | -2.26 | -2.73 | -3.08 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | -1.41 | -3.44 | -1.66 | -2.26 | -2.73 | -3.08 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | -1.92 | -2.83 | -1.56 | -1.21 | -3.14 | -1.97 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | -1.92 | -2.83 | -1.56 | -1.21 | -3.14 | -1.97 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log (POST-HOC) | -2.11 | -2.57 | -1.61 | -1.23 | -2.86 | -1.43 |

Rulers (R1c: max(one-pass yardstick, largest |value| over the null designs)); sector floor from Healthy_sliced, Healthy_sliced_new, MCI_lobe_c3; LR floor from the nine symmetric solves; FB floor from Healthy_sliced, Healthy_sliced_new, MCI_lobe_c3, Mild_lobe, Mild_lobe_new, Severe_lobe, Severe_lobe_c3:

| reference | method | ruler S1 Fr | ruler S2 TL | ruler S3 PL | ruler S4 Oc | ruler S5 PR | ruler S6 TR | ruler_LR | ruler_FB | yard_LR | floor_LR | yard_FB | floor_FB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 (Healthy_sliced, 7 passes) | Tikhonov dS | 3.14 | 4.19 | 2.93 | 3.39 | 5.15 | 5.15 | 3.92 | 3.88 | 2.18 | 3.92 | 0.67 | 3.88 |
| H7 (Healthy_sliced, 7 passes) | bounded dS | 3.14 | 4.19 | 2.93 | 3.39 | 5.15 | 5.15 | 3.92 | 3.88 | 2.18 | 3.92 | 0.67 | 3.88 |
| H7 (Healthy_sliced, 7 passes) | frozen log | 2.47 | 2.83 | 2.07 | 2.27 | 4.14 | 3.59 | 3.93 | 4.53 | 2.25 | 3.93 | 1.00 | 4.53 |
| H7 (Healthy_sliced, 7 passes) | frozen bounded log | 2.42 | 2.83 | 1.98 | 2.27 | 4.14 | 3.59 | 3.93 | 4.53 | 2.25 | 3.93 | 1.00 | 4.53 |
| H7 (Healthy_sliced, 7 passes) | whitened log | 1.64 | 2.62 | 1.91 | 2.29 | 3.08 | 2.89 | 3.08 | 5.00 | 1.68 | 3.08 | 1.23 | 5.00 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 3.54 | 3.85 | 2.14 | 3.54 | 0.71 | 3.85 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 3.54 | 3.85 | 2.14 | 3.54 | 0.71 | 3.85 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | 2.46 | 2.87 | 2.01 | 1.88 | 4.05 | 3.61 | 3.55 | 4.14 | 2.23 | 3.55 | 0.91 | 4.14 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | 2.42 | 2.87 | 1.92 | 1.59 | 4.05 | 3.59 | 3.55 | 4.14 | 2.23 | 3.55 | 0.91 | 4.14 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log | 1.59 | 2.64 | 1.90 | 1.57 | 3.02 | 2.91 | 2.98 | 4.86 | 1.66 | 2.98 | 1.16 | 4.86 |

Reference-free LR_anti (R1c ruler, rank p against the nine symmetric solves):

| reference | method | LR_anti | yardstick | null_max | ruler | ratio | label | rank_p |
|---|---|---|---|---|---|---|---|---|
| H7 (Healthy_sliced, 7 passes) | Tikhonov dS | +0.18 | 2.14 | 4.07 | 4.07 | 0.04 | not separable | 0.90 |
| H7 (Healthy_sliced, 7 passes) | bounded dS | +0.18 | 2.14 | 4.07 | 4.07 | 0.04 | not separable | 0.90 |
| H7 (Healthy_sliced, 7 passes) | frozen log | -0.43 | 2.38 | 3.72 | 3.72 | 0.12 | not separable | 0.80 |
| H7 (Healthy_sliced, 7 passes) | frozen bounded log | -0.43 | 2.38 | 3.72 | 3.72 | 0.12 | not separable | 0.70 |
| H7 (Healthy_sliced, 7 passes) | whitened log (POST-HOC) | -0.14 | 1.98 | 3.14 | 3.14 | 0.04 | not separable | 1.00 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | +0.20 | 2.12 | 4.04 | 4.04 | 0.05 | not separable | 0.90 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | +0.20 | 2.12 | 4.04 | 4.04 | 0.05 | not separable | 0.70 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | -0.40 | 2.38 | 3.76 | 3.76 | 0.11 | not separable | 0.80 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | -0.40 | 2.38 | 3.76 | 3.76 | 0.11 | not separable | 0.70 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log (POST-HOC) | -0.09 | 1.97 | 3.17 | 3.17 | 0.03 | not separable | 1.00 |

Measurement-level context (Prompt 07 model, ±0.5 dB, primary method, SD over draws; not part of the reading):

| reference | sd S1 Fr | sd S2 TL | sd S3 PL | sd S4 Oc | sd S5 PR | sd S6 TR | sd LR | sd FB |
|---|---|---|---|---|---|---|---|---|
| H7 (Healthy_sliced, 7 passes) | 21.11 | 19.67 | 22.13 | 20.59 | 19.85 | 22.76 | 26.96 | 35.45 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | 18.69 | 19.26 | 21.33 | 17.18 | 18.51 | 19.92 | 26.17 | 30.67 |

Known designs through the same primary pipeline (context for the reader; not used by the reading rule):

| reference | design | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | LR | FB |
|---|---|---|---|---|---|---|---|---|---|
| H7 (Healthy_sliced, 7 passes) | Mild_lobe | +11.38 | +20.22 | +17.61 | +7.59 | +16.24 | +21.66 | -0.04 | +3.78 |
| H7 (Healthy_sliced, 7 passes) | Moderate_lobe | +17.65 | +15.07 | +16.64 | +7.51 | +18.64 | +20.92 | -3.92 | +10.14 |
| H7 (Healthy_sliced, 7 passes) | Severe_lobe | +20.62 | +17.42 | +19.77 | +16.74 | +17.73 | +21.06 | -0.80 | +3.88 |
| H7 (Healthy_sliced, 7 passes) | Mild_lobe_new | +8.24 | +16.03 | +15.19 | +5.13 | +13.68 | +16.50 | +0.52 | +3.11 |
| H7 (Healthy_sliced, 7 passes) | Moderate_lobe_c3 | +16.05 | +12.08 | +14.33 | +5.25 | +13.49 | +16.40 | -1.74 | +10.80 |
| H7 (Healthy_sliced, 7 passes) | Severe_lobe_c3 | +18.53 | +15.51 | +18.30 | +14.89 | +14.82 | +18.17 | +0.41 | +3.64 |
| H7 (Healthy_sliced, 7 passes) | LeftOnly_test_c3 | +5.17 | +13.11 | +15.02 | +5.62 | +4.97 | +6.19 | +8.48 | -0.45 |
| H7 (Healthy_sliced, 7 passes) | RightOnly_test | +10.71 | +8.99 | +10.06 | +9.21 | +16.37 | +22.34 | -9.83 | +1.50 |
| H7 (Healthy_sliced, 7 passes) | MCI_lobe_c3 | +2.53 | +3.36 | +2.93 | +3.39 | +2.11 | +2.14 | +1.02 | -0.86 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Mild_lobe | +9.22 | +18.24 | +14.87 | +5.37 | +13.78 | +18.64 | +0.35 | +3.85 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Moderate_lobe | +15.48 | +13.09 | +13.93 | +5.32 | +16.19 | +17.91 | -3.54 | +10.16 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Severe_lobe | +18.42 | +15.47 | +17.07 | +14.58 | +15.27 | +18.13 | -0.43 | +3.84 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Mild_lobe_new | +6.08 | +14.04 | +12.44 | +2.94 | +11.26 | +13.48 | +0.87 | +3.14 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Moderate_lobe_c3 | +13.87 | +10.12 | +11.60 | +3.06 | +11.10 | +13.41 | -1.40 | +10.80 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Severe_lobe_c3 | +16.34 | +13.56 | +15.57 | +12.73 | +12.40 | +15.25 | +0.74 | +3.61 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | LeftOnly_test_c3 | +3.00 | +11.14 | +12.28 | +3.40 | +2.57 | +3.22 | +8.82 | -0.40 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | RightOnly_test | +8.54 | +7.03 | +7.36 | +7.00 | +13.92 | +19.35 | -9.44 | +1.53 |
| H6 (Healthy_sliced_new, 6 passes, stop rule 1) | MCI_lobe_c3 | +0.37 | +1.37 | +0.24 | +1.21 | -0.31 | -0.83 | +1.37 | -0.84 |

## Stated reading (protocol reading rule, primary method)

- **Affected lobes** (above the frozen T_abs in every reference that passed the gate and was not rejected: H7 (Healthy_sliced, 7 passes), H6 (Healthy_sliced_new, 6 passes, stop rule 1)): **none**.
- **Possible** (above T_abs in one reference only): S2 TL.
- **Side:** none (smallest LR_anti ratio over the references 0.04×).
- **Front/back:** none (smallest FB ratio 0.19×).
- **Ranking** of the six sectors by mean dε'': S2 TL > S5 PR > S3 PL > S6 TR > S1 Fr > S4 Oc (S1 Fr +3.8, S2 TL +13.7, S3 PL +5.2, S4 Oc +3.1, S5 PR +11.9, S6 TR +5.0).
- Caveats from round 2 apply: sector values carry Born and reference error of several units; calls near T_abs are fragile; the reading is a sector-level estimate of where the change sits under the cap of the array (sensitivity ≥ 54 % above z = 40 mm), not an anatomical lobe diagnosis.

The whitened-log rows are **POST-HOC** (no frozen thresholds, not used by the reading).
