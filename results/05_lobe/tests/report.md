# Pre-registered test designs of the lobe phantom: LeftOnly_test and MCI_lobe (code e1b3629)

Designs (HFSS convergence tables, user 2026-10-04; header variables checked by the user):
| design | kind | stop_rule | passes | final_dS | elements | notes |
|---|---|---|---|---|---|---|
| Healthy_sliced | stage | 2 | 7 | 0.0092 | 1349491 | sliced healthy head |
| Healthy_sliced_new | stage | 1 | 6 | 0.0155 | 1081728 | sliced healthy head |
| MCI_lobe_c3 | test | 1 | 6 | 0.013948 | 981160 | MCI_lobe: e = 0, r_hip 21.25; HIP_MCI only, CSF healthy; extra Ventricle_CSF sphere (meshing fix) |
| LeftOnly_test_c3 | test | 1 | 6 | 0.014686 | 941358 | LeftOnly_test: e = 0/7.5/11.5/0/0/0 mm, r_hip 17.5; CSF_Mild everywhere (0.5 mm layer on the right) |

Predictions: `results/05_lobe/predictions.md` / `.csv`, committed at cf56de8 before LeftOnly_test existed. Unchanged since cf56de8: **True** (git). LeftOnly is scored against Healthy_sliced (primary, as pre-registered) and Healthy_sliced_new (stop-rule and pass matched) alongside.

**Caveats (recorded before scoring):**
- The predictions were derived from the lobe_v1 pair (Healthy_sliced, stop rule 2, 7 passes, against Mild_lobe, stop rule 1, 5 passes), so mesh is part of their per-path 'Mild change'.
- LeftOnly_test carries CSF_Mild everywhere (CSF is one object): on the right it is only the 0.5 mm layer (e_S5 = e_S6 = 0). The prediction model treats the right lobes as fully healthy.
- The gain-invariant cross-ratio test was agreed after cf56de8 (2026-10-03); its predicted values are derived from the committed per-path predictions without new parameters, and its decision rule is fixed in this script before the first run.
- Prediction 2 says 'no front-back asymmetry beyond the floor' without a numeric rule; it is scored as |index| <= the stated floor (strict), with |index| < 3x floor reported alongside.
- LeftOnly_test_c3 has 6 passes (stop rule 1; pass 5 missed 0.02 by ~0.002); the matched reference is Healthy_sliced_new (6 passes, stop rule 1).
- One solve per design: within-simulation noise robustness, not generalisation. Lobe placement is schematic.

**Rulers** (for a difference of two designs; `scripts/08_lobe_mesh.py`): noise SD (typical noise and setup perturbation, no per-port calibration error), one-pass mesh yardstick (largest of Healthy 6->7, Mild 5->6, Moderate 5->6, Severe 5->6; families floored at their rms), symmetry floor (mirror residual of the six mirror-symmetric stage designs), measurement-error spread (±0.5 dB per-port gain; ±2 dB gain + ±10° phase). **Label**: hit = committed rule holds and the effect is separable (>= 3x clean ruler = max(yardstick, floor)), or a predicted null/level is confirmed; miss = committed rule fails by >= 3x the clean ruler; not separable = otherwise. 'measured' = the same with max(yardstick, floor (+) ±0.5 dB spread).

## 0. QC
Parsing, passivity, reciprocity and port-map search for Healthy_sliced_new + the two test designs: `results/05_lobe/tests/qc/qc_report.md` (rows labelled by manifest class: Mild = LeftOnly_test_c3, MCI = MCI_lobe_c3); the c3 stage designs: `results/05_lobe/lobe_B/qc/qc_report.md`. Points masked by the frozen recipe in the four new files (`results/05_lobe/qc/masked_points.csv`):
| file | f_GHz | ports | path | type | |Sij| dB | |Sji| dB | reciprocity error dB (re band level) | masked |
|---|---|---|---|---|---|---|---|---|
| new_with_slices_LeftOnly_test_c3.s6p | 3.85 | 2-5 | T3-T6 | opposite | -54.36 | -54.41 | -25.85 | True |
| new_with_slices_Moderate_lobe_c3.s6p | 3.85 | 1-4 | T1-T4 | opposite | -55.91 | -56.23 | -29.23 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.23 | 2-6 | T3-T5 | second-neighbour | -57.88 | -57.60 | -29.63 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.23 | 2-6 | T3-T5 | second-neighbour | -57.50 | -57.17 | -28.36 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.23 | 2-6 | T3-T5 | second-neighbour | -57.15 | -56.77 | -27.42 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.24 | 2-6 | T3-T5 | second-neighbour | -56.81 | -56.40 | -26.77 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.25 | 2-6 | T3-T5 | second-neighbour | -56.49 | -56.07 | -26.36 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.25 | 2-6 | T3-T5 | second-neighbour | -56.20 | -55.76 | -26.16 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.25 | 2-6 | T3-T5 | second-neighbour | -55.92 | -55.49 | -26.16 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.26 | 2-6 | T3-T5 | second-neighbour | -55.66 | -55.25 | -26.33 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.27 | 2-6 | T3-T5 | second-neighbour | -55.42 | -55.04 | -26.69 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.27 | 2-6 | T3-T5 | second-neighbour | -55.20 | -54.85 | -27.20 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.27 | 2-6 | T3-T5 | second-neighbour | -54.99 | -54.67 | -27.88 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.28 | 2-6 | T3-T5 | second-neighbour | -54.79 | -54.51 | -28.73 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.29 | 2-6 | T3-T5 | second-neighbour | -54.60 | -54.36 | -29.75 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.83 | 3-6 | T2-T5 | opposite | -61.80 | -60.93 | -27.88 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.83 | 3-6 | T2-T5 | opposite | -52.25 | -54.68 | -5.60 | True |
| new_with_slices_Severe_lobe_c3.s6p | 3.84 | 3-6 | T2-T5 | opposite | -56.90 | -56.63 | -25.54 | True |

Integrity (tests set):
| class | recip_rel_band_max_db | n_glitch_pts | col_power_max | sigma_max | passive |
|---|---|---|---|---|---|
| Normal | -41.1 | 0 | 0.905 | 0.952 | True |
| MCI | -42.5 | 0 | 0.905 | 0.952 | True |
| Mild | -25.8 | 0 | 0.904 | 0.951 | True |

## 1. LeftOnly_test: committed predictions 1-6 (scored blind, cf56de8 unchanged)
| reference | prediction | predicted dB | committed rule | observed dB | committed verdict | label | label (measured) | label (±2 dB) | / noise SD | / yardstick | / symmetry floor | / spread ±0.5 dB | / spread ±2 dB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced (7 passes, primary) | 1 left-right index | 0.232 | sign + and |index| >= 3 x 0.071 dB | 0.023 | incorrect | not separable | not separable | not separable | 0.098 | 0.364 | 0.226 | 0.045 | 0.012 |
| Healthy_sliced (7 passes, primary) | 2 front-back index | 0.038 | |index| <= floor 0.084 dB (strict; < 3x floor: True) | 0.068 | correct | hit | hit | hit | 0.246 | 0.976 | 0.557 | 0.108 | 0.029 |
| Healthy_sliced (7 passes, primary) | 3 right paths ~0 | n/a | per path (see section 1) | n/a | 7/7 correct | 7 hit, 0 miss, 0 not separable | 7 hit, 0 miss, 0 not separable |  | n/a | n/a | n/a | n/a | n/a |
| Healthy_sliced (7 passes, primary) | 4 left paths ~ full Mild | n/a | per path (see section 1) | n/a | 4/7 correct | 1 hit, 0 miss, 6 not separable | 1 hit, 0 miss, 6 not separable |  | n/a | n/a | n/a | n/a | n/a |
| Healthy_sliced (7 passes, primary) | locality model vs no-locality baseline | n/a | locality wins if its rms error over all 21 paths is lower | n/a | locality loses (rms 0.166 vs 0.135 dB) | miss | on the 14 paths where the models differ: 0.148 vs 0.089 dB |  | n/a | n/a | n/a | n/a | n/a |
| Healthy_sliced_new (6 passes, matched) | 1 left-right index | 0.232 | sign + and |index| >= 3 x 0.071 dB | -0.029 | incorrect | not separable | not separable | not separable | 0.124 | 0.460 | 0.285 | 0.057 | 0.015 |
| Healthy_sliced_new (6 passes, matched) | 2 front-back index | 0.038 | |index| <= floor 0.084 dB (strict; < 3x floor: True) | 0.137 | incorrect | not separable | not separable | not separable | 0.499 | 1.976 | 1.127 | 0.219 | 0.058 |
| Healthy_sliced_new (6 passes, matched) | 3 right paths ~0 | n/a | per path (see section 1) | n/a | 4/7 correct | 4 hit, 0 miss, 3 not separable | 4 hit, 0 miss, 3 not separable |  | n/a | n/a | n/a | n/a | n/a |
| Healthy_sliced_new (6 passes, matched) | 4 left paths ~ full Mild | n/a | per path (see section 1) | n/a | 4/7 correct | 1 hit, 0 miss, 6 not separable | 1 hit, 0 miss, 6 not separable |  | n/a | n/a | n/a | n/a | n/a |
| Healthy_sliced_new (6 passes, matched) | locality model vs no-locality baseline | n/a | locality wins if its rms error over all 21 paths is lower | n/a | locality loses (rms 0.189 vs 0.144 dB) | miss | on the 14 paths where the models differ: 0.198 vs 0.130 dB |  | n/a | n/a | n/a | n/a | n/a |
| (absolute value) | 5 R31 level | -15.220 | within 0.3 dB | -15.445 | correct | hit | hit | hit | 6.275 | 1.664 | n/a | 5.791 | 5.839 |
| (absolute value) | 5 R21 level | -20.240 | within 0.3 dB | -20.200 | correct | hit | hit | hit | 0.682 | 0.367 | n/a | 0.606 | 0.577 |
| (absolute value) | 5 R32 level | 5.030 | within 0.3 dB | 4.755 | correct | hit | hit | hit | 4.330 | 1.710 | n/a | 3.578 | 3.530 |
| (noisy measurements) | 6 frozen detection label UNCERTAIN | n/a | >= 80% of noisy measurements labelled UNCERTAIN | n/a | 0.00 UNCERTAIN (±2 dB/±10°: 0.00); R31 -15.44 dB vs tau -15.27 ± 0.08 | miss |  |  | n/a | n/a | n/a | n/a | n/a |

Joint rule as committed ('Predictions 5-6 hold if R31/R21/R32 lie within 0.3 dB ... and the frozen-rule label matches for >= 80%'): **fails** (5: True, 6: False).
Post hoc, not pre-registered: the same halfway model re-derived from the matched pair (Healthy_sliced_new, Mild_lobe) gives R31 -15.28, R21 -20.27, R32 4.99 dB; observed R31 -15.44, R21 -20.20, R32 4.75 dB.

## 2. Per-path predictions (both references)
| reference | path | type | prediction | Mild change dB (cf56de8) | predicted (locality) dB | baseline (no locality) dB | observed dB | committed tolerance dB | committed verdict | label | label (measured) | / noise SD | / yardstick | / symmetry floor | / spread ±0.5 dB | / spread ±2 dB | |obs - pred| / clean ruler |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced (7 passes, primary) | T1 refl. | reflection | half of Mild (both models) | 0.020 | 0.010 | 0.010 | -0.006 | 0.014 | incorrect | not separable | not separable | 0.016 | 0.226 | 0.686 | 0.007 | 0.002 | 0.608 |
| Healthy_sliced (7 passes, primary) | T1-T2 | neighbour | 4: left (~ full Mild) | 0.019 | 0.019 | 0.009 | 0.047 | 0.161 | correct | not separable | not separable | 0.192 | 0.990 | 0.426 | 0.079 | 0.020 | 0.258 |
| Healthy_sliced (7 passes, primary) | T1-T3 | second-neighbour | 4: left (~ full Mild) | 0.594 | 0.594 | 0.297 | 0.379 | 0.297 | correct | not separable | not separable | 1.314 | 3.498 | 1.749 | 0.591 | 0.155 | 0.990 |
| Healthy_sliced (7 passes, primary) | T1-T4 | opposite | half of Mild (both models) | -0.912 | -0.456 | -0.456 | -0.633 | 0.127 | correct | hit | not separable | 2.361 | 5.019 | 5.384 | 1.013 | 0.267 | 1.402 |
| Healthy_sliced (7 passes, primary) | T1-T5 | second-neighbour | 3: right (~0) | 0.442 | 0.000 | 0.221 | 0.188 | 0.297 | correct | hit | hit | 0.698 | 1.080 | 0.868 | 0.309 | 0.080 | 0.868 |
| Healthy_sliced (7 passes, primary) | T1-T6 | neighbour | 3: right (~0) | 0.090 | 0.000 | 0.045 | -0.083 | 0.161 | correct | hit | hit | 0.320 | 0.879 | 0.742 | 0.128 | 0.036 | 0.742 |
| Healthy_sliced (7 passes, primary) | T2 refl. | reflection | 4: left (~ full Mild) | -0.026 | -0.026 | -0.013 | -0.062 | 0.014 | incorrect | not separable | not separable | 0.175 | 1.675 | 7.309 | 0.071 | 0.018 | 0.981 |
| Healthy_sliced (7 passes, primary) | T2-T3 | neighbour | 4: left (~ full Mild) | 0.086 | 0.086 | 0.043 | 0.109 | 0.161 | correct | not separable | not separable | 0.460 | 1.658 | 0.982 | 0.180 | 0.046 | 0.209 |
| Healthy_sliced (7 passes, primary) | T2-T4 | second-neighbour | 4: left (~ full Mild) | 0.459 | 0.459 | 0.229 | 0.084 | 0.297 | incorrect | not separable | not separable | 0.298 | 0.476 | 0.388 | 0.141 | 0.036 | 1.728 |
| Healthy_sliced (7 passes, primary) | T2-T5 | opposite | half of Mild (both models) | -1.244 | -0.622 | -0.622 | -0.870 | 0.127 | correct | hit | not separable | 3.371 | 5.980 | 7.409 | 1.428 | 0.385 | 1.707 |
| Healthy_sliced (7 passes, primary) | T2-T6 | second-neighbour | half of Mild (both models) | 1.144 | 0.572 | 0.572 | 0.401 | 0.297 | correct | not separable | not separable | 1.552 | 2.223 | 1.850 | 0.604 | 0.164 | 0.787 |
| Healthy_sliced (7 passes, primary) | T3 refl. | reflection | 4: left (~ full Mild) | -0.037 | -0.037 | -0.018 | -0.056 | 0.014 | incorrect | not separable | not separable | 0.150 | 1.602 | 6.567 | 0.060 | 0.017 | 0.541 |
| Healthy_sliced (7 passes, primary) | T3-T4 | neighbour | 4: left (~ full Mild) | 0.003 | 0.003 | 0.002 | -0.124 | 0.161 | correct | hit | hit | 0.478 | 3.039 | 1.113 | 0.196 | 0.055 | 1.145 |
| Healthy_sliced (7 passes, primary) | T3-T5 | second-neighbour | half of Mild (both models) | 0.753 | 0.376 | 0.376 | 0.566 | 0.297 | correct | not separable | not separable | 2.063 | 4.353 | 2.609 | 0.897 | 0.256 | 0.873 |
| Healthy_sliced (7 passes, primary) | T3-T6 | opposite | half of Mild (both models) | -1.333 | -0.666 | -0.666 | -1.004 | 0.127 | incorrect | not separable | not separable | 4.033 | 8.284 | 8.547 | 1.460 | 0.437 | 2.787 |
| Healthy_sliced (7 passes, primary) | T4 refl. | reflection | half of Mild (both models) | 0.033 | 0.017 | 0.017 | -0.015 | 0.014 | incorrect | not separable | not separable | 0.039 | 0.568 | 1.756 | 0.017 | 0.004 | 1.206 |
| Healthy_sliced (7 passes, primary) | T4-T5 | neighbour | 3: right (~0) | 0.012 | 0.000 | 0.006 | 0.076 | 0.161 | correct | hit | hit | 0.294 | 0.935 | 0.682 | 0.121 | 0.034 | 0.682 |
| Healthy_sliced (7 passes, primary) | T4-T6 | second-neighbour | 3: right (~0) | 0.106 | 0.000 | 0.053 | 0.225 | 0.297 | correct | hit | hit | 0.781 | 0.871 | 1.037 | 0.367 | 0.101 | 0.871 |
| Healthy_sliced (7 passes, primary) | T5 refl. | reflection | 3: right (~0) | -0.040 | -0.000 | -0.020 | 0.008 | 0.014 | correct | hit | hit | 0.022 | 0.240 | 0.959 | 0.009 | 0.003 | 0.240 |
| Healthy_sliced (7 passes, primary) | T5-T6 | neighbour | 3: right (~0) | 0.090 | 0.000 | 0.045 | -0.026 | 0.161 | correct | hit | hit | 0.094 | 0.429 | 0.234 | 0.041 | 0.012 | 0.234 |
| Healthy_sliced (7 passes, primary) | T6 refl. | reflection | 3: right (~0) | -0.022 | -0.000 | -0.011 | -0.003 | 0.014 | correct | hit | hit | 0.008 | 0.076 | 0.351 | 0.003 | 0.001 | 0.076 |
| Healthy_sliced_new (6 passes, matched) | T1 refl. | reflection | half of Mild (both models) | 0.020 | 0.010 | 0.010 | -0.017 | 0.014 | incorrect | not separable | not separable | 0.047 | 0.670 | 2.037 | 0.019 | 0.005 | 1.052 |
| Healthy_sliced_new (6 passes, matched) | T1-T2 | neighbour | 4: left (~ full Mild) | 0.019 | 0.019 | 0.009 | 0.086 | 0.161 | correct | not separable | not separable | 0.349 | 1.795 | 0.773 | 0.144 | 0.036 | 0.605 |
| Healthy_sliced_new (6 passes, matched) | T1-T3 | second-neighbour | 4: left (~ full Mild) | 0.594 | 0.594 | 0.297 | 0.397 | 0.297 | correct | not separable | not separable | 1.375 | 3.661 | 1.830 | 0.618 | 0.162 | 0.908 |
| Healthy_sliced_new (6 passes, matched) | T1-T4 | opposite | half of Mild (both models) | -0.912 | -0.456 | -0.456 | -0.507 | 0.127 | correct | hit | not separable | 1.890 | 4.019 | 4.311 | 0.811 | 0.213 | 0.402 |
| Healthy_sliced_new (6 passes, matched) | T1-T5 | second-neighbour | 3: right (~0) | 0.442 | 0.000 | 0.221 | 0.363 | 0.297 | incorrect | not separable | not separable | 1.345 | 2.080 | 1.672 | 0.595 | 0.154 | 1.672 |
| Healthy_sliced_new (6 passes, matched) | T1-T6 | neighbour | 3: right (~0) | 0.090 | 0.000 | 0.045 | -0.067 | 0.161 | correct | hit | hit | 0.258 | 0.710 | 0.599 | 0.103 | 0.029 | 0.599 |
| Healthy_sliced_new (6 passes, matched) | T2 refl. | reflection | 4: left (~ full Mild) | -0.026 | -0.026 | -0.013 | -0.076 | 0.014 | incorrect | not separable | not separable | 0.215 | 2.053 | 8.956 | 0.087 | 0.022 | 1.359 |
| Healthy_sliced_new (6 passes, matched) | T2-T3 | neighbour | 4: left (~ full Mild) | 0.086 | 0.086 | 0.043 | 0.097 | 0.161 | correct | not separable | not separable | 0.407 | 1.468 | 0.870 | 0.159 | 0.041 | 0.097 |
| Healthy_sliced_new (6 passes, matched) | T2-T4 | second-neighbour | 4: left (~ full Mild) | 0.459 | 0.459 | 0.229 | -0.004 | 0.297 | incorrect | not separable | not separable | 0.013 | 0.021 | 0.017 | 0.006 | 0.002 | 2.133 |
| Healthy_sliced_new (6 passes, matched) | T2-T5 | opposite | half of Mild (both models) | -1.244 | -0.622 | -0.622 | -0.747 | 0.127 | correct | hit | not separable | 2.892 | 5.131 | 6.357 | 1.225 | 0.331 | 0.858 |
| Healthy_sliced_new (6 passes, matched) | T2-T6 | second-neighbour | half of Mild (both models) | 1.144 | 0.572 | 0.572 | 0.352 | 0.297 | correct | not separable | not separable | 1.360 | 1.949 | 1.621 | 0.529 | 0.144 | 1.015 |
| Healthy_sliced_new (6 passes, matched) | T3 refl. | reflection | 4: left (~ full Mild) | -0.037 | -0.037 | -0.018 | -0.073 | 0.014 | incorrect | not separable | not separable | 0.197 | 2.107 | 8.635 | 0.080 | 0.022 | 1.046 |
| Healthy_sliced_new (6 passes, matched) | T3-T4 | neighbour | 4: left (~ full Mild) | 0.003 | 0.003 | 0.002 | -0.124 | 0.161 | correct | hit | hit | 0.480 | 3.050 | 1.117 | 0.197 | 0.055 | 1.149 |
| Healthy_sliced_new (6 passes, matched) | T3-T5 | second-neighbour | half of Mild (both models) | 0.753 | 0.376 | 0.376 | 0.664 | 0.297 | correct | hit | not separable | 2.421 | 5.109 | 3.062 | 1.053 | 0.300 | 1.326 |
| Healthy_sliced_new (6 passes, matched) | T3-T6 | opposite | half of Mild (both models) | -1.333 | -0.666 | -0.666 | -0.883 | 0.127 | correct | hit | not separable | 3.547 | 7.284 | 7.516 | 1.283 | 0.384 | 1.787 |
| Healthy_sliced_new (6 passes, matched) | T4 refl. | reflection | half of Mild (both models) | 0.033 | 0.017 | 0.017 | -0.026 | 0.014 | incorrect | not separable | not separable | 0.067 | 0.984 | 3.043 | 0.030 | 0.008 | 1.622 |
| Healthy_sliced_new (6 passes, matched) | T4-T5 | neighbour | 3: right (~0) | 0.012 | 0.000 | 0.006 | -0.005 | 0.161 | correct | hit | hit | 0.020 | 0.065 | 0.048 | 0.008 | 0.002 | 0.048 |
| Healthy_sliced_new (6 passes, matched) | T4-T6 | second-neighbour | 3: right (~0) | 0.106 | 0.000 | 0.053 | 0.363 | 0.297 | incorrect | not separable | not separable | 1.260 | 1.404 | 1.672 | 0.592 | 0.162 | 1.404 |
| Healthy_sliced_new (6 passes, matched) | T5 refl. | reflection | 3: right (~0) | -0.040 | -0.000 | -0.020 | -0.012 | 0.014 | correct | hit | hit | 0.031 | 0.340 | 1.360 | 0.013 | 0.004 | 0.340 |
| Healthy_sliced_new (6 passes, matched) | T5-T6 | neighbour | 3: right (~0) | 0.090 | 0.000 | 0.045 | -0.055 | 0.161 | correct | hit | hit | 0.200 | 0.913 | 0.498 | 0.088 | 0.025 | 0.498 |
| Healthy_sliced_new (6 passes, matched) | T6 refl. | reflection | 3: right (~0) | -0.022 | -0.000 | -0.011 | -0.020 | 0.014 | incorrect | not separable | not separable | 0.055 | 0.525 | 2.415 | 0.023 | 0.006 | 0.525 |

## 3. Gain-invariant left-right cross-ratios (primary test, as agreed; derived from cf56de8)
A = chi_n - s chi_mirror(n) for each mirror pair of the 45 cross-ratios: zero for any mirror-symmetric head, independent of per-port gain. Predicted A from the committed per-path predictions (locality model) and from the no-locality baseline. Decision rule (fixed in the script before the first run): (a) >= 1 A beyond 3x the measured ruler, (b) locality rms error < baseline rms error, (c) sign agreement >= 80% where the predicted A exceeds 3x the clean ruler.
| reference | left-right cross-ratios | >= 3x clean ruler | >= 3x measured ruler (±0.5 dB) | >= 3x measured ruler (±2 dB) | rms error locality dB | rms error baseline dB | predicted >= 3x clean ruler | sign agrees | best | best observed dB | best / measured ruler | primary test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced (7 passes, primary) | 22 | 0 | 0 | 0 | 0.678 | 0.465 | 0 | 0/0 | T1T3·T4T5 / T1T5·T3T4 | 0.782 | 1.458 | fails |
| Healthy_sliced_new (6 passes, matched) | 22 | 0 | 0 | 0 | 0.931 | 0.622 | 0 | 0/0 | T2T3·T4T6 / T2T4·T3T6 | 1.021 | 1.990 | fails |

All left-right cross-ratios (largest observed first):
| reference | left-right cross-ratio | predicted (locality) dB | baseline (no locality) dB | observed dB | / noise SD | / yardstick | / symmetry floor | / spread ±0.5 dB | / spread ±2 dB | / clean ruler | / measured ruler |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced (7 passes, primary) | T1T3·T4T5 / T1T5·T3T4 | 1.18 | 0.16 | 0.78 | 2.60 | 1.65 | 1.84 | 2.40 | 2.37 | 1.65 | 1.46 |
| Healthy_sliced (7 passes, primary) | T1T2·T4T5 / T1T5·T2T4 | 0.15 | -0.13 | 0.66 | 3.01 | 1.98 | 1.56 | 3.04 | 2.85 | 1.56 | 1.39 |
| Healthy_sliced (7 passes, primary) | T2T3·T4T6 / T2T4·T3T6 | -0.79 | -0.31 | 0.55 | 1.70 | 1.17 | 1.29 | 1.92 | 1.67 | 1.17 | 1.07 |
| Healthy_sliced (7 passes, primary) | T2T3·T4T5 / T2T4·T3T5 | -0.38 | -0.17 | 0.48 | 2.86 | 1.82 | 1.12 | 3.19 | 2.77 | 1.12 | 1.06 |
| Healthy_sliced (7 passes, primary) | T2T3·T4T6 / T2T6·T3T4 | -0.38 | -0.17 | 0.48 | 2.86 | 1.82 | 1.12 | 3.19 | 2.77 | 1.12 | 1.06 |
| Healthy_sliced (7 passes, primary) | T1T3·T4T6 / T1T4·T3T6 | 0.18 | -0.06 | 0.47 | 2.03 | 2.29 | 1.09 | 2.15 | 1.95 | 1.09 | 0.98 |
| Healthy_sliced (7 passes, primary) | T2T3·T4T5 / T2T5·T3T4 | 0.03 | -0.04 | 0.40 | 3.03 | 1.64 | 0.94 | 3.12 | 2.84 | 0.94 | 0.90 |
| Healthy_sliced (7 passes, primary) | T1T3·T4T5 / T1T4·T3T5 | 0.59 | 0.08 | 0.39 | 2.60 | 1.65 | 0.92 | 2.40 | 2.37 | 0.92 | 0.86 |
| Healthy_sliced (7 passes, primary) | T1T2·T4T6 / T1T6·T2T4 | -0.88 | -0.42 | 0.54 | 1.64 | 0.80 | 1.27 | 1.80 | 1.64 | 0.80 | 0.80 |
| Healthy_sliced (7 passes, primary) | T1T3·T2T5 / T1T5·T2T3 | 1.15 | 0.20 | 0.38 | 1.19 | 1.16 | 0.90 | 1.15 | 1.15 | 0.90 | 0.71 |
| Healthy_sliced (7 passes, primary) | T1T2·T4T6 / T1T4·T2T6 | -0.44 | -0.21 | 0.27 | 1.64 | 0.80 | 0.64 | 1.80 | 1.64 | 0.64 | 0.60 |
| Healthy_sliced (7 passes, primary) | T1T2·T3T4 / T1T4·T2T3 | -0.06 | -0.04 | -0.20 | 2.65 | 1.01 | 0.48 | 2.65 | 2.69 | 0.48 | 0.47 |
| Healthy_sliced (7 passes, primary) | T1T2·T4T5 / T1T4·T2T5 | -0.03 | -0.08 | 0.20 | 1.86 | 0.96 | 0.46 | 1.96 | 1.72 | 0.46 | 0.45 |
| Healthy_sliced (7 passes, primary) | T1T2·T3T6 / T1T3·T2T6 | -0.62 | -0.16 | -0.19 | 1.10 | 0.96 | 0.46 | 1.10 | 1.03 | 0.46 | 0.42 |
| Healthy_sliced (7 passes, primary) | T1T2·T3T5 / T1T3·T2T5 | -0.62 | -0.16 | -0.19 | 1.10 | 0.96 | 0.46 | 1.10 | 1.03 | 0.46 | 0.42 |
| Healthy_sliced (7 passes, primary) | T1T2·T3T5 / T1T5·T2T3 | 0.53 | 0.04 | 0.19 | 1.10 | 0.91 | 0.44 | 1.06 | 1.10 | 0.44 | 0.40 |
| Healthy_sliced (7 passes, primary) | T1T2·T5T6 / T1T5·T2T6 | 0.53 | 0.04 | 0.19 | 1.10 | 0.91 | 0.44 | 1.06 | 1.10 | 0.44 | 0.40 |
| Healthy_sliced (7 passes, primary) | T1T2·T3T4 / T1T3·T2T4 | -1.03 | -0.29 | -0.12 | 0.53 | 0.25 | 0.28 | 0.53 | 0.51 | 0.25 | 0.25 |
| Healthy_sliced (7 passes, primary) | T1T3·T2T4 / T1T4·T2T3 | 0.97 | 0.25 | -0.08 | 0.37 | 0.21 | 0.20 | 0.38 | 0.37 | 0.20 | 0.18 |
| Healthy_sliced (7 passes, primary) | T2T4·T3T5 / T2T5·T3T4 | 0.41 | 0.14 | -0.07 | 0.41 | 0.24 | 0.18 | 0.45 | 0.40 | 0.18 | 0.16 |
| Healthy_sliced (7 passes, primary) | T2T4·T3T6 / T2T6·T3T4 | 0.41 | 0.14 | -0.07 | 0.41 | 0.24 | 0.18 | 0.45 | 0.40 | 0.18 | 0.16 |
| Healthy_sliced (7 passes, primary) | T1T2·T3T6 / T1T6·T2T3 | -0.09 | -0.11 | -0.01 | 0.07 | 0.04 | 0.02 | 0.07 | 0.07 | 0.02 | 0.02 |
| Healthy_sliced_new (6 passes, matched) | T2T3·T4T6 / T2T4·T3T6 | -0.79 | -0.31 | 1.02 | 3.15 | 2.17 | 2.40 | 3.56 | 3.09 | 2.17 | 1.99 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T4T6 / T1T6·T2T4 | -0.88 | -0.42 | 1.04 | 3.14 | 1.53 | 2.44 | 3.45 | 3.15 | 1.53 | 1.53 |
| Healthy_sliced_new (6 passes, matched) | T2T3·T4T6 / T2T6·T3T4 | -0.38 | -0.17 | 0.64 | 3.83 | 2.44 | 1.50 | 4.28 | 3.72 | 1.50 | 1.41 |
| Healthy_sliced_new (6 passes, matched) | T2T3·T4T5 / T2T4·T3T5 | -0.38 | -0.17 | 0.64 | 3.83 | 2.44 | 1.50 | 4.28 | 3.72 | 1.50 | 1.41 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T4T5 / T1T5·T2T4 | 0.15 | -0.13 | 0.67 | 3.06 | 2.02 | 1.58 | 3.09 | 2.90 | 1.58 | 1.41 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T4T6 / T1T4·T2T6 | -0.44 | -0.21 | 0.52 | 3.14 | 1.53 | 1.22 | 3.45 | 3.15 | 1.22 | 1.15 |
| Healthy_sliced_new (6 passes, matched) | T1T3·T4T6 / T1T4·T3T6 | 0.18 | -0.06 | 0.54 | 2.34 | 2.64 | 1.26 | 2.48 | 2.25 | 1.26 | 1.13 |
| Healthy_sliced_new (6 passes, matched) | T1T3·T2T4 / T1T4·T2T3 | 0.97 | 0.25 | -0.48 | 2.13 | 1.21 | 1.14 | 2.19 | 2.11 | 1.14 | 1.01 |
| Healthy_sliced_new (6 passes, matched) | T2T4·T3T5 / T2T5·T3T4 | 0.41 | 0.14 | -0.38 | 2.10 | 1.24 | 0.90 | 2.32 | 2.05 | 0.90 | 0.84 |
| Healthy_sliced_new (6 passes, matched) | T2T4·T3T6 / T2T6·T3T4 | 0.41 | 0.14 | -0.38 | 2.10 | 1.24 | 0.90 | 2.32 | 2.05 | 0.90 | 0.84 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T3T4 / T1T3·T2T4 | -1.03 | -0.29 | 0.37 | 1.61 | 0.75 | 0.86 | 1.61 | 1.56 | 0.75 | 0.75 |
| Healthy_sliced_new (6 passes, matched) | T1T3·T4T5 / T1T5·T3T4 | 1.18 | 0.16 | 0.31 | 1.02 | 0.65 | 0.72 | 0.94 | 0.93 | 0.65 | 0.57 |
| Healthy_sliced_new (6 passes, matched) | T2T3·T4T5 / T2T5·T3T4 | 0.03 | -0.04 | 0.25 | 1.92 | 1.04 | 0.60 | 1.98 | 1.80 | 0.60 | 0.57 |
| Healthy_sliced_new (6 passes, matched) | T1T3·T4T5 / T1T4·T3T5 | 0.59 | 0.08 | 0.15 | 1.02 | 0.65 | 0.36 | 0.94 | 0.93 | 0.36 | 0.34 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T4T5 / T1T4·T2T5 | -0.03 | -0.08 | 0.14 | 1.28 | 0.67 | 0.32 | 1.35 | 1.19 | 0.32 | 0.31 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T3T4 / T1T4·T2T3 | -0.06 | -0.04 | -0.12 | 1.53 | 0.58 | 0.28 | 1.53 | 1.56 | 0.28 | 0.27 |
| Healthy_sliced_new (6 passes, matched) | T1T3·T2T5 / T1T5·T2T3 | 1.15 | 0.20 | 0.05 | 0.16 | 0.16 | 0.12 | 0.16 | 0.16 | 0.12 | 0.10 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T3T5 / T1T5·T2T3 | 0.53 | 0.04 | 0.03 | 0.21 | 0.17 | 0.08 | 0.20 | 0.21 | 0.08 | 0.08 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T5T6 / T1T5·T2T6 | 0.53 | 0.04 | 0.03 | 0.21 | 0.17 | 0.08 | 0.20 | 0.21 | 0.08 | 0.08 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T3T6 / T1T3·T2T6 | -0.62 | -0.16 | -0.02 | 0.10 | 0.09 | 0.04 | 0.10 | 0.09 | 0.04 | 0.04 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T3T5 / T1T3·T2T5 | -0.62 | -0.16 | -0.02 | 0.10 | 0.09 | 0.04 | 0.10 | 0.09 | 0.04 | 0.04 |
| Healthy_sliced_new (6 passes, matched) | T1T2·T3T6 / T1T6·T2T3 | -0.09 | -0.11 | 0.02 | 0.13 | 0.07 | 0.04 | 0.14 | 0.13 | 0.04 | 0.04 |

## 4. MCI_lobe (Prompt 07 §3.5): is MCI - Healthy_sliced_new larger than the rulers on any feature?
Expectation: no (the hippocampus lies deeper than the array's sensing depth). 228 quantities: ring averages and ratios, front-back / left-right indices, 21 paths, 45 cross-ratios and their (rotational and left-right) asymmetry parts, and the remaining ring features (sub-band spectra). **0** exceed 3x the clean ruler, **0** 3x the measured ruler (many comparisons: with a yardstick from four one-pass pairs, a few chance exceedances are possible).
| family | n | >= 3x clean ruler | >= 3x measured ruler | max / clean ruler | max / measured ruler |
|---|---|---|---|---|---|
| asymmetry cross-ratio | 45 | 0 | 0 | 1.98 | 1.98 |
| cross-ratio | 45 | 0 | 0 | 1.98 | 1.98 |
| index | 6 | 0 | 0 | 1.31 | 0.38 |
| left-right cross-ratio | 22 | 0 | 0 | 1.98 | 1.98 |
| path (neighbour) | 6 | 0 | 0 | 1.47 | 0.27 |
| path (opposite) | 3 | 0 | 0 | 0.37 | 0.07 |
| path (reflection) | 6 | 0 | 0 | 0.86 | 0.03 |
| path (second-neighbour) | 6 | 0 | 0 | 1.13 | 0.45 |
| ring average / ratio | 6 | 0 | 0 | 1.71 | 0.25 |
| ring feature (sub-band) | 83 | 0 | 0 | 1.08 | 0.55 |

Largest (by clean ruler):
| quantity | family | MCI - Healthy_sliced_new dB | / noise SD | / yardstick | / symmetry floor | / spread ±0.5 dB | / clean ruler | / measured ruler | MCI - Healthy_sliced (7 passes) dB |
|---|---|---|---|---|---|---|---|---|---|
| asym chi T1T2·T4T6 / T1T6·T2T4 | asymmetry cross-ratio | 0.672 | 4.072 | 1.979 | 2.308 | 4.464 | 1.979 | 1.979 | 0.424 |
| chi T1T2·T4T6 / T1T6·T2T4 | cross-ratio | 0.672 | 4.072 | 1.979 | 2.339 | 4.464 | 1.979 | 1.979 | 0.424 |
| lr chi T1T2·T4T6 / T1T6·T2T4 | left-right cross-ratio | 1.344 | 4.072 | 1.979 | 3.161 | 4.464 | 1.979 | 1.979 | 0.847 |
| asym chi T1T5·T4T6 / T1T6·T4T5 | asymmetry cross-ratio | 0.559 | 4.468 | 1.863 | 1.921 | 4.288 | 1.863 | 1.753 | 0.302 |
| lr chi T2T3·T4T6 / T2T4·T3T6 | left-right cross-ratio | 0.873 | 2.696 | 1.856 | 2.053 | 3.041 | 1.856 | 1.701 | 0.403 |
| asym chi T1T3·T4T6 / T1T6·T3T4 | asymmetry cross-ratio | 0.508 | 4.028 | 1.727 | 1.745 | 4.334 | 1.727 | 1.619 | 0.488 |
| C1 neighbour | ring average / ratio | 0.020 | 0.146 | 1.714 | n/a | 0.057 | 1.714 | 0.057 | 0.032 |
| chi T1T3·T4T6 / T1T4·T3T6 | cross-ratio | 0.501 | 3.063 | 1.654 | 1.744 | 3.054 | 1.654 | 1.514 | 0.593 |
| chi T2T3·T4T6 / T2T4·T3T6 | cross-ratio | 0.483 | 2.847 | 1.594 | 1.683 | 3.123 | 1.594 | 1.482 | 0.392 |
| lr chi T1T2·T4T6 / T1T4·T2T6 | left-right cross-ratio | 0.672 | 4.072 | 1.979 | 1.580 | 4.464 | 1.580 | 1.490 | 0.424 |
| asym chi T1T2·T4T6 / T1T4·T2T6 | asymmetry cross-ratio | 0.587 | 3.634 | 1.567 | 2.018 | 4.003 | 1.567 | 1.567 | 0.353 |
| asym chi T2T5·T4T6 / T2T6·T4T5 | asymmetry cross-ratio | 0.538 | 3.358 | 1.565 | 1.848 | 3.709 | 1.565 | 1.565 | 0.281 |

## 5. Frozen rule (unchanged) on the test designs
300 noisy measurements per condition; gate as in Prompt 07 (gain-invariant mode, Normal window from the v2 Normal).
| condition | design | rule | Normal | AD | Mild+Moderate | UNCERTAIN |
|---|---|---|---|---|---|---|
| typical, ±0.5 dB gain | LeftOnly_test_c3 | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | LeftOnly_test_c3 | three | 1.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | LeftOnly_test_c3 | three_merged | 0.990 | 0.000 | 0.003 | 0.007 |
| typical, ±0.5 dB gain | MCI_lobe_c3 | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | MCI_lobe_c3 | three | 1.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | MCI_lobe_c3 | three_merged | 1.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | LeftOnly_test_c3 | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | LeftOnly_test_c3 | three | 1.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | LeftOnly_test_c3 | three_merged | 0.990 | 0.000 | 0.007 | 0.003 |
| ±2 dB gain + ±10° phase | MCI_lobe_c3 | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | MCI_lobe_c3 | three | 1.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | MCI_lobe_c3 | three_merged | 1.000 | 0.000 | 0.000 | 0.000 |

Figure `figures/leftonly_mci_maps.png`.

## Claims
| claim | number | baseline | verdict |
|---|---|---|---|
| the LeftOnly predictions were scored unchanged (cf56de8) | predictions.md / .csv identical to cf56de8: True | git | holds |
| LeftOnly prediction 1 left-right index (Healthy_sliced (7 passes, primary)) | observed +0.023 dB vs predicted +0.232; incorrect | sign + and |index| >= 3 x 0.071 dB | not separable (measured: not separable) |
| LeftOnly prediction 2 front-back index (Healthy_sliced (7 passes, primary)) | observed +0.068 dB vs predicted +0.038; correct | |index| <= floor 0.084 dB (strict; < 3x floor: True) | hit (measured: hit) |
| LeftOnly prediction 3 right paths ~0 (Healthy_sliced (7 passes, primary)) | 7/7 correct | per path (see section 1) | 7 hit, 0 miss, 0 not separable (measured: 7 hit, 0 miss, 0 not separable) |
| LeftOnly prediction 4 left paths ~ full Mild (Healthy_sliced (7 passes, primary)) | 4/7 correct | per path (see section 1) | 1 hit, 0 miss, 6 not separable (measured: 1 hit, 0 miss, 6 not separable) |
| LeftOnly prediction locality model vs no-locality baseline (Healthy_sliced (7 passes, primary)) | locality loses (rms 0.166 vs 0.135 dB) | locality wins if its rms error over all 21 paths is lower | miss |
| LeftOnly prediction 1 left-right index (Healthy_sliced_new (6 passes, matched)) | observed -0.029 dB vs predicted +0.232; incorrect | sign + and |index| >= 3 x 0.071 dB | not separable (measured: not separable) |
| LeftOnly prediction 2 front-back index (Healthy_sliced_new (6 passes, matched)) | observed +0.137 dB vs predicted +0.038; incorrect | |index| <= floor 0.084 dB (strict; < 3x floor: True) | not separable (measured: not separable) |
| LeftOnly prediction 3 right paths ~0 (Healthy_sliced_new (6 passes, matched)) | 4/7 correct | per path (see section 1) | 4 hit, 0 miss, 3 not separable (measured: 4 hit, 0 miss, 3 not separable) |
| LeftOnly prediction 4 left paths ~ full Mild (Healthy_sliced_new (6 passes, matched)) | 4/7 correct | per path (see section 1) | 1 hit, 0 miss, 6 not separable (measured: 1 hit, 0 miss, 6 not separable) |
| LeftOnly prediction locality model vs no-locality baseline (Healthy_sliced_new (6 passes, matched)) | locality loses (rms 0.189 vs 0.144 dB) | locality wins if its rms error over all 21 paths is lower | miss |
| LeftOnly prediction 5 R31 level ((absolute value)) | observed -15.445 dB vs predicted -15.220; correct | within 0.3 dB | hit (measured: hit) |
| LeftOnly prediction 5 R21 level ((absolute value)) | observed -20.200 dB vs predicted -20.240; correct | within 0.3 dB | hit (measured: hit) |
| LeftOnly prediction 5 R32 level ((absolute value)) | observed +4.755 dB vs predicted +5.030; correct | within 0.3 dB | hit (measured: hit) |
| LeftOnly prediction 6 frozen detection label UNCERTAIN ((noisy measurements)) | 0.00 UNCERTAIN (±2 dB/±10°: 0.00); R31 -15.44 dB vs tau -15.27 ± 0.08 | >= 80% of noisy measurements labelled UNCERTAIN | miss |
| gain-invariant left-right cross-ratios: LeftOnly asymmetry detected and in the predicted direction (Healthy_sliced (7 passes, primary)) | 0/22 beyond 3x measured ruler (±2 dB: 0); rms error locality 0.678 vs baseline 0.465 dB; sign agrees 0/0 | decision rule fixed before the first run; derived from cf56de8 | fails |
| gain-invariant left-right cross-ratios: LeftOnly asymmetry detected and in the predicted direction (Healthy_sliced_new (6 passes, matched)) | 0/22 beyond 3x measured ruler (±2 dB: 0); rms error locality 0.931 vs baseline 0.622 dB; sign agrees 0/0 | decision rule fixed before the first run; derived from cf56de8 | fails |
| descriptive (post hoc): frozen rules on LeftOnly_test (one-sided mild atrophy) | detection 1.00 AD, R31 margin to tau -0.17 dB = 1.3x the R31 yardstick; three 1.00 Normal, three_merged 0.99 Normal | frozen rule unchanged (typical, ±0.5 dB gain) | AD on this mesh, but the margin is < 2x the yardstick; both staging rules say Normal (inconsistent with detection) |
| MCI_lobe - Healthy_sliced_new exceeds the rulers on any feature (expected: no) | 0/228 beyond 3x clean ruler, 0/228 beyond 3x measured ruler; largest asym chi T1T2·T4T6 / T1T6·T2T4 +0.672 dB (2.0x clean) | clean / measured ruler | no (as expected) |
| frozen binary_R31 labels MCI_lobe as Normal | 1.00 Normal, 0.00 UNCERTAIN, 0.00 INVALID | frozen rule unchanged (typical, ±0.5 dB gain) | holds |
| frozen three labels MCI_lobe as Normal | 1.00 Normal, 0.00 UNCERTAIN, 0.00 INVALID | frozen rule unchanged (typical, ±0.5 dB gain) | holds |
| frozen three_merged labels MCI_lobe as Normal | 1.00 Normal, 0.00 UNCERTAIN, 0.00 INVALID | frozen rule unchanged (typical, ±0.5 dB gain) | holds |

One solve per design and stop rule: within-simulation noise robustness, not generalisation.