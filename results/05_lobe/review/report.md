# Adversarial review of the lobe results, A1-A9 (code 2f143e4)

Every number below is recomputed from the raw files by `scripts/10_lobe_review.py`; nothing is copied from earlier reports. One verdict bar everywhere: >= 3x the stated ruler. One solve per design: within-simulation noise robustness, not generalisation.

## A9. Uncertainty of the frozen boundaries
tau is re-derived with the 03 code and the same seeds (config_repeats.yaml, typical profile, 2 Normal + 6 AD solves): **-15.2728 dB** vs frozen -15.2728 dB. 03's own CI (bootstrap over solves within class, then draws): -15.368 to -15.165 dB. Solve-only bootstrap (4000x): SD **0.055 dB**, 95% -15.368 to -15.165 dB. tau is the midpoint between the closest draws of the two classes, so it is set by v2 Normal and the two Severe solves:
| left out | class | tau dB |
|---|---|---|
| brain_sevem_layer_Healthy.s6p | Normal | -15.273 |
| new_Healthy.s6p | Normal | -15.165 |
| Brain_sevem_layer_MildAD.s6p | Mild | -15.273 |
| new_MildAD.s6p | Mild | -15.273 |
| Brain_sevem_layer_ModerateAD.s6p | Moderate | -15.273 |
| new_ModerateAD.s6p | Moderate | -15.273 |
| brain_sevem_layer_SevereAD.s6p | Severe | -15.281 |
| new_SevereAD.s6p | Severe | -15.273 |

Staging boundaries (1-D LDA with equal priors = midpoint of class means; re-derived from the solves and bootstrapped over solves within class):
| rule | boundary | frozen dB | re-derived midpoint dB | bootstrap SD dB | 2.5% dB | 97.5% dB |
|---|---|---|---|---|---|---|
| three (R21) | 1 | -19.980 | -19.976 | 0.065 | -20.100 | -19.851 |
| three (R21) | 2 | -18.750 | -18.752 | 0.035 | -18.822 | -18.683 |
| three_merged (R32) | 1 | 2.770 | 2.775 | 0.035 | 2.706 | 2.840 |
| three_merged (R32) | 2 | 4.640 | 4.635 | 0.037 | 4.564 | 4.707 |

Labels against the tau bootstrap (frozen margin m kept):
| design | R31 dB | frozen label | distance to tau dB | distance to label edge dB | P(label differs | solve bootstrap of tau) |
|---|---|---|---|---|---|
| LeftOnly_test_c3 | -15.445 | AD | -0.172 | 0.094 | 0.064 |
| Severe_lobe | -15.533 | AD | -0.261 | 0.183 | 0.000 |
| Severe_lobe_c3 | -15.584 | AD | -0.312 | 0.234 | 0.000 |
| Mild_lobe | -15.822 | AD | -0.549 | 0.471 | 0.000 |
| Mild_lobe_new | -15.856 | AD | -0.583 | 0.506 | 0.000 |
| Moderate_lobe | -16.008 | AD | -0.735 | 0.657 | 0.000 |
| Moderate_lobe_c3 | -16.012 | AD | -0.739 | 0.661 | 0.000 |
| Healthy_sliced_new | -14.744 | Normal | 0.529 | -0.450 | 0.000 |
| Healthy_sliced | -14.609 | Normal | 0.664 | -0.586 | 0.000 |
| MCI_lobe_c3 | -14.773 | Normal | 0.500 | -0.422 | 0.000 |

## A1. One bar for every label
The detection and localisation tiers come from the same commit, aff9d56 (before the c3 files existed); they are numerically the same (>= 3x unqualified, 2-3x 'mesh-sensitive', < 2x 'not separable'):
```
cl = ("exceeds mesh yardstick and symmetry floor (>= 3x)" if c >= 3 else "mesh-sensitive (2-3x)" if c >= 2
"verdict": ("holds" if fc >= 0.95 and mv >= 3 else "holds; margin mesh-sensitive (2-3x)"
if fc >= 0.95 and mv >= 2 else "holds on this mesh; margin < 2x yardstick (one more "
```
The inconsistency was the word 'holds' put in front of a sub-3x detection margin, and margins measured to tau instead of to the label edge (tau - m for AD). Below, every frozen-rule label of every lobe design, with the margin to the nearest point where the label changes, against max(feature yardstick, bootstrap SD of that boundary):
| set | design | rule | feature dB | frozen label | distance to label edge dB | feature yardstick dB | boundary bootstrap SD dB | / yardstick | / boundary SD | / max(yardstick, boundary SD) | verdict (one bar) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lobe_A | Healthy_sliced_new | binary | -14.744 | Normal | -0.450 | 0.135 | 0.055 | 3.334 | 8.196 | 3.334 | robust (>= 3x) |
| lobe_A | Healthy_sliced_new | three | -20.567 | Normal | 0.580 | 0.110 | 0.065 | 5.280 | 8.858 | 5.280 | robust (>= 3x) |
| lobe_A | Healthy_sliced_new | three_merged | 5.823 | Normal | -1.184 | 0.161 | 0.037 | 7.361 | 31.682 | 7.361 | robust (>= 3x) |
| lobe_A | Mild_lobe | binary | -15.822 | AD | 0.471 | 0.135 | 0.055 | 3.486 | 8.569 | 3.486 | robust (>= 3x) |
| lobe_A | Mild_lobe | three | -19.974 | UNCERTAIN | 0.007 | 0.110 | 0.065 | 0.059 | 0.099 | 0.059 | not determined (< 2x) |
| lobe_A | Mild_lobe | three_merged | 4.152 | Mild+Moderate | 0.481 | 0.161 | 0.037 | 2.987 | 12.857 | 2.987 | sensitive (2-3x) |
| lobe_A | Moderate_lobe | binary | -16.008 | AD | 0.657 | 0.135 | 0.055 | 4.862 | 11.953 | 4.862 | robust (>= 3x) |
| lobe_A | Moderate_lobe | three | -19.451 | Mild | -0.517 | 0.110 | 0.065 | 4.711 | 7.903 | 4.711 | robust (>= 3x) |
| lobe_A | Moderate_lobe | three_merged | 3.443 | Mild+Moderate | -0.660 | 0.161 | 0.035 | 4.103 | 19.051 | 4.103 | robust (>= 3x) |
| lobe_A | Severe_lobe | binary | -15.533 | AD | 0.183 | 0.135 | 0.055 | 1.351 | 3.320 | 1.351 | not determined (< 2x) |
| lobe_A | Severe_lobe | three | -18.002 | Severe | -0.743 | 0.110 | 0.035 | 6.770 | 21.107 | 6.770 | robust (>= 3x) |
| lobe_A | Severe_lobe | three_merged | 2.469 | Severe | 0.298 | 0.161 | 0.035 | 1.853 | 8.602 | 1.853 | not determined (< 2x) |
| lobe_B | Healthy_sliced | binary | -14.609 | Normal | -0.586 | 0.135 | 0.055 | 4.337 | 10.661 | 4.337 | robust (>= 3x) |
| lobe_B | Healthy_sliced | three | -20.507 | Normal | 0.520 | 0.110 | 0.065 | 4.734 | 7.941 | 4.734 | robust (>= 3x) |
| lobe_B | Healthy_sliced | three_merged | 5.898 | Normal | -1.259 | 0.161 | 0.037 | 7.827 | 33.689 | 7.827 | robust (>= 3x) |
| lobe_B | Mild_lobe_new | binary | -15.856 | AD | 0.506 | 0.135 | 0.055 | 3.741 | 9.196 | 3.741 | robust (>= 3x) |
| lobe_B | Mild_lobe_new | three | -19.940 | Mild | -0.028 | 0.110 | 0.065 | 0.255 | 0.428 | 0.255 | not determined (< 2x) |
| lobe_B | Mild_lobe_new | three_merged | 4.084 | Mild+Moderate | 0.549 | 0.161 | 0.037 | 3.410 | 14.677 | 3.410 | robust (>= 3x) |
| lobe_B | Moderate_lobe_c3 | binary | -16.012 | AD | 0.661 | 0.135 | 0.055 | 4.888 | 12.016 | 4.888 | robust (>= 3x) |
| lobe_B | Moderate_lobe_c3 | three | -19.451 | Mild | -0.517 | 0.110 | 0.065 | 4.711 | 7.903 | 4.711 | robust (>= 3x) |
| lobe_B | Moderate_lobe_c3 | three_merged | 3.440 | Mild+Moderate | -0.656 | 0.161 | 0.035 | 4.078 | 18.936 | 4.078 | robust (>= 3x) |
| lobe_B | Severe_lobe_c3 | binary | -15.584 | AD | 0.234 | 0.135 | 0.055 | 1.728 | 4.248 | 1.728 | not determined (< 2x) |
| lobe_B | Severe_lobe_c3 | three | -17.892 | Severe | -0.852 | 0.110 | 0.035 | 7.768 | 24.218 | 7.768 | robust (>= 3x) |
| lobe_B | Severe_lobe_c3 | three_merged | 2.308 | Severe | 0.459 | 0.161 | 0.035 | 2.854 | 13.249 | 2.854 | sensitive (2-3x) |
| tests | LeftOnly_test_c3 | binary | -15.445 | AD | 0.094 | 0.135 | 0.055 | 0.696 | 1.710 | 0.696 | not determined (< 2x) |
| tests | LeftOnly_test_c3 | three | -20.200 | Normal | 0.212 | 0.110 | 0.065 | 1.932 | 3.241 | 1.932 | not determined (< 2x) |
| tests | LeftOnly_test_c3 | three_merged | 4.755 | Normal | -0.116 | 0.161 | 0.037 | 0.721 | 3.104 | 0.721 | not determined (< 2x) |
| tests | MCI_lobe_c3 | binary | -14.773 | Normal | -0.422 | 0.135 | 0.055 | 3.123 | 7.677 | 3.123 | robust (>= 3x) |
| tests | MCI_lobe_c3 | three | -20.555 | Normal | 0.568 | 0.110 | 0.065 | 5.176 | 8.682 | 5.176 | robust (>= 3x) |
| tests | MCI_lobe_c3 | three_merged | 5.783 | Normal | -1.144 | 0.161 | 0.037 | 7.112 | 30.611 | 7.112 | robust (>= 3x) |

## A2. Could the registered tests pass?
The ~0.43 dB clean ruler of the left-right cross-ratios is max(one-pass yardstick, symmetry floor); its floor part is sqrt2 x the rms of the left-right cross-ratios of the mirror-symmetric stages (a per-band, band-averaged 3.2-4.2 GHz power quantity). The test and its floor were added in 08a9a53, after cf56de8, but the same floor can be computed from the lobe_v1 stages that existed before cf56de8:
| item | value |
|---|---|
| cf56de8 committed (predictions) | cf56de8 2026-10-03 21:25:18 +0530 |
| 08a9a53 committed (left-right cross-ratio test and its floor) | 08a9a53 2026-10-04 09:40:17 +0530 |
| LR-index floor of a difference known at cf56de8 (staged 0.071 (+) healthy, dB) | 0.094 |
| prediction 1: P(rule passes | locality model exactly right) | 0.58 |
| left-right cross-ratio floor of a difference from the lobe_v1 stages only (dB) | 0.434 |
| same floor as used at scoring (six stages incl. c3, dB) | 0.425 |
| largest predicted left-right cross-ratio (from cf56de8 paths, dB) | 1.181 |
| largest predicted / lobe_v1-era floor | 2.72 |

So both registered left-right tests were under-powered by design: prediction 1's pass threshold (3 x 0.071 = 0.213 dB) sat 8% below its own predicted value (0.232 dB), and no predicted power cross-ratio reached 3x a floor computable before registration. That is a design flaw of the registration (mine), knowable at cf56de8; no power check was run.

## A3. Mirror test (reference-free)
For the band-power LR index the mirror test is algebraically the earlier index: index(S - mirror(S)) = 2 index(S), and index(LO) - index(ref) is what was reported. Numerically:
| reference | index(LO) - index(ref) | index(LO - mirror LO) / 2 | index(ref - mirror ref) / 2 |
|---|---|---|---|
| Healthy_sliced | 0.0232 | -0.0148 | -0.0379 |
| Healthy_sliced_new | -0.0292 | -0.0148 | 0.0145 |

Null = the nine mirror-symmetric designs (Healthy_sliced, Healthy_sliced_new, Mild_lobe, Mild_lobe_new, Moderate_lobe, Moderate_lobe_c3, Severe_lobe, Severe_lobe_c3, MCI_lobe_c3). Per family, how many LeftOnly statistics exceed 3x the clean ruler (max(null rms, one-pass yardstick)), 3x the measured rulers, and the largest null value:
| family | n | >= 3x clean ruler | >= 3x measured (±0.5 dB) | >= 3x measured (±2 dB ±10°) | beyond null max | best / clean ruler |
|---|---|---|---|---|---|---|
| phase LR index | 3 | 0 | 0 | 0 | 2 | 2.39 |
| phase cross-ratio | 22 | 16 | 2 | 2 | 16 | 6.91 |
| phase pair | 8 | 0 | 0 | 0 | 5 | 2.73 |
| power LR index | 3 | 0 | 0 | 0 | 0 | 0.23 |
| power cross-ratio | 22 | 0 | 0 | 0 | 4 | 1.80 |
| power pair | 8 | 2 | 0 | 0 | 3 | 6.92 |

Largest (by clean ruler):
| statistic | LeftOnly | null rms | null max |.| | one-pass yardstick | spread ±0.5 dB gain | spread ±2 dB gain ±10° phase | / clean ruler | / measured ruler (±0.5 dB) | / measured ruler (±2 dB ±10°) |
|---|---|---|---|---|---|---|---|---|---|
| power pair T2 refl. vs T6 refl. | -0.06 | 0.01 | 0.02 | 0.01 | 0.92 | 3.18 | 6.92 | 0.07 | 0.02 |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | 10.11 | 1.46 | 2.51 | 1.46 | 3.03 | 3.11 | 6.91 | 3.34 | 3.25 |
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | -10.27 | 1.75 | 2.93 | 1.50 | 3.07 | 3.17 | 5.86 | 3.35 | 3.23 |
| power pair T3 refl. vs T5 refl. | -0.07 | 0.01 | 0.01 | 0.01 | 0.90 | 3.43 | 5.77 | 0.08 | 0.02 |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | -10.30 | 2.19 | 4.35 | 2.23 | 3.60 | 3.98 | 4.61 | 2.86 | 2.59 |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | -5.14 | 0.72 | 1.28 | 1.12 | 2.21 | 2.49 | 4.59 | 2.33 | 2.07 |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | -5.14 | 0.72 | 1.28 | 1.12 | 2.21 | 2.49 | 4.59 | 2.33 | 2.07 |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | 9.93 | 2.31 | 3.88 | 1.77 | 3.59 | 3.57 | 4.31 | 2.77 | 2.78 |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | 9.94 | 2.35 | 4.36 | 1.91 | 3.71 | 3.76 | 4.23 | 2.68 | 2.65 |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | 4.97 | 1.17 | 2.18 | 0.95 | 2.27 | 2.38 | 4.23 | 2.19 | 2.09 |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | -10.59 | 2.64 | 5.49 | 2.10 | 3.60 | 3.84 | 4.01 | 2.94 | 2.76 |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | -5.29 | 1.32 | 2.75 | 1.05 | 2.27 | 2.44 | 4.01 | 2.34 | 2.17 |

## A4. The imaging left-right estimate, evaluated with these rulers
The imaging operator is rebuilt read-only (cached Born table, frozen kappa and lambda; max |S| difference between its loader and this pipeline 0.0e+00). LR = mean(S2, S3) - mean(S5, S6) of the recovered sector d eps''; it is linear in the complex dS at 3.4/3.6/3.8 GHz. T = (LR(S) - LR(mirror S))/2 is its mirror test.
| method | reference | LR (stage - ref) | LR magnitude part | LR phase part | mirror-test T(LeftOnly) | null T mean | null T rms | null T max |.| | one-pass yardstick | spread noise + setup, no calibration error | spread ±0.5 dB gain | spread ±2 dB gain ±10° phase | T / null rms | T / null max | T / clean ruler | T / measured ruler (±0.5 dB) | T / measured ruler (±2 dB ±10°) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tikhonov dS (primary) | Healthy_sliced (7 passes) | 8.48 | 1.29 | 6.97 | 7.86 | -0.99 | 1.62 | 4.07 | 2.14 | 18.23 | 19.98 | 22.59 | 4.86 | 1.93 | 3.67 | 0.39 | 0.35 |
| Tikhonov dS (primary) | Healthy_sliced_new (6 passes) | 8.82 | 1.14 | 7.54 | 7.86 | -0.97 | 1.60 | 4.04 | 2.12 | 17.89 | 19.61 | 22.20 | 4.90 | 1.94 | 3.70 | 0.40 | 0.35 |
| Tikhonov log (gain-inv.) | Healthy_sliced (7 passes) | 9.25 | 1.11 | 8.13 | 8.75 | -0.91 | 1.43 | 3.72 | 2.38 | 7.40 | 8.16 | 7.93 | 6.10 | 2.35 | 3.68 | 1.07 | 1.10 |
| Tikhonov log (gain-inv.) | Healthy_sliced_new (6 passes) | 9.70 | 1.15 | 8.55 | 8.82 | -0.92 | 1.45 | 3.76 | 2.38 | 7.49 | 8.26 | 8.03 | 6.07 | 2.35 | 3.71 | 1.07 | 1.10 |
| whitened log (post-hoc) | Healthy_sliced (7 passes) | 9.27 | 1.33 | 7.93 | 8.69 | -0.75 | 1.21 | 3.14 | 1.98 | 1.90 | 1.93 | 1.97 | 7.21 | 2.76 | 4.39 | 4.39 | 4.39 |
| whitened log (post-hoc) | Healthy_sliced_new (6 passes) | 9.41 | 1.24 | 8.17 | 8.77 | -0.76 | 1.22 | 3.17 | 1.97 | 1.91 | 1.94 | 2.00 | 7.20 | 2.77 | 4.44 | 4.44 | 4.39 |

Where the LR comes from (Tikhonov dS; stage minus Healthy_sliced_new):
| design (vs Healthy_sliced_new) | LR full | magnitude part | phase part |
|---|---|---|---|
| Mild_lobe | 0.35 | -0.04 | 0.29 |
| Moderate_lobe | -3.54 | -1.26 | -2.38 |
| Severe_lobe | -0.43 | -0.98 | 0.62 |
| MCI_lobe_c3 | 1.37 | 0.31 | 1.06 |
| LeftOnly_test_c3 | 8.82 | 1.14 | 7.54 |

The band-power indices (A3) are blind to it because the left-right signal is mostly in phase: LeftOnly's LR +8.82 = magnitude +1.14 + phase +7.54 (first order). The inversion does not manufacture it: the mirror test puts LeftOnly at 4.9x the null rms and 1.9x the largest symmetric design, consistent with the independent phase cross-ratios of A3.

## A5. Locality vs no-locality, with uncertainty
Both the observed LeftOnly changes and the Mild changes the predictions were built from carry numerical error; each path is perturbed by N(0, clean ruler) (max(one-pass yardstick, symmetry floor) of that path), both models are rebuilt from the perturbed Mild change with the committed rules, and the rms difference is recomputed (20000x). A bootstrap over the 21 paths is shown alongside.
| reference | rms(locality) - rms(baseline) dB | ruler perturbation 2.5% | ruler perturbation 97.5% | P(locality wins) under rulers | path bootstrap 2.5% | path bootstrap 97.5% | verdict |
|---|---|---|---|---|---|---|---|
| Healthy_sliced (7 passes, primary) | 0.031 | -0.029 | 0.087 | 0.189 | 0.000 | 0.070 | no preference (interval contains 0) |
| Healthy_sliced_new (6 passes, matched) | 0.045 | -0.017 | 0.095 | 0.093 | 0.001 | 0.089 | no preference (interval contains 0) |

## A6. Mechanism: LeftOnly against Mild, per path class and side
Ratio = LeftOnly change / Mild change of the same path against the same healthy head; only paths whose Mild change is >= 2x the path's clean ruler give a usable ratio (inverse-variance weighted per class and side). Locality predicts 1 on the left, 0 on the right, 0.5 across; no locality predicts 0.5 everywhere.
| comparison | type | side | paths | usable (Mild >= 2x ruler) | weighted ratio LeftOnly/Mild | SE | locality predicts | no-locality predicts |
|---|---|---|---|---|---|---|---|---|
| as predicted (vs Healthy_sliced) | neighbour | left | 3 | 0 | n/a | n/a | 1.00 | 0.50 |
| as predicted (vs Healthy_sliced) | neighbour | right | 3 | 0 | n/a | n/a | 0.00 | 0.50 |
| as predicted (vs Healthy_sliced) | opposite | cross (left-right) | 2 | 2 | 0.73 | 0.09 | 0.50 | 0.50 |
| as predicted (vs Healthy_sliced) | opposite | self-mirror | 1 | 1 | 0.69 | 0.17 | 0.50 | 0.50 |
| as predicted (vs Healthy_sliced) | reflection | left | 2 | 0 | n/a | n/a | 1.00 | 0.50 |
| as predicted (vs Healthy_sliced) | reflection | right | 2 | 0 | n/a | n/a | 0.00 | 0.50 |
| as predicted (vs Healthy_sliced) | reflection | self-mirror | 2 | 0 | n/a | n/a | 0.50 | 0.50 |
| as predicted (vs Healthy_sliced) | second-neighbour | cross (left-right) | 2 | 2 | 0.45 | 0.18 | 0.50 | 0.50 |
| as predicted (vs Healthy_sliced) | second-neighbour | left | 2 | 2 | 0.43 | 0.32 | 1.00 | 0.50 |
| as predicted (vs Healthy_sliced) | second-neighbour | right | 2 | 1 | 0.43 | 0.53 | 0.00 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | neighbour | left | 3 | 0 | n/a | n/a | 1.00 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | neighbour | right | 3 | 0 | n/a | n/a | 0.00 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | opposite | cross (left-right) | 2 | 2 | 0.70 | 0.10 | 0.50 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | opposite | self-mirror | 1 | 1 | 0.64 | 0.19 | 0.50 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | reflection | left | 2 | 0 | n/a | n/a | 1.00 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | reflection | right | 2 | 0 | n/a | n/a | 0.00 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | reflection | self-mirror | 2 | 0 | n/a | n/a | 0.50 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | second-neighbour | cross (left-right) | 2 | 2 | 0.46 | 0.18 | 0.50 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | second-neighbour | left | 2 | 1 | 0.65 | 0.42 | 1.00 | 0.50 |
| rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new) | second-neighbour | right | 2 | 1 | 0.59 | 0.41 | 0.00 | 0.50 |

Per path, with the phase changes (degrees, band-mean of the wrapped difference):
| path | type | side | LeftOnly change dB | Mild change dB | clean ruler dB | Mild change / ruler | ratio LeftOnly / Mild | ratio SD | LeftOnly phase change deg | Mild phase change deg | phase clean ruler deg | LeftOnly phase / ruler |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 refl. | reflection | self-mirror | -0.02 | 0.01 | 0.03 | 0.32 | n/a | n/a | -0.09 | -0.47 | 0.43 | 0.20 |
| T1-T2 | neighbour | left | 0.09 | 0.06 | 0.11 | 0.51 | n/a | n/a | -3.94 | -7.65 | 2.83 | 1.39 |
| T1-T3 | second-neighbour | left | 0.40 | 0.61 | 0.22 | 2.82 | 0.65 | 0.42 | 3.39 | -0.88 | 3.77 | 0.90 |
| T1-T4 | opposite | self-mirror | -0.51 | -0.79 | 0.13 | 6.23 | 0.64 | 0.19 | 1.00 | -1.82 | 2.19 | 0.46 |
| T1-T5 | second-neighbour | right | 0.36 | 0.62 | 0.22 | 2.84 | 0.59 | 0.41 | -0.47 | -1.68 | 3.50 | 0.14 |
| T1-T6 | neighbour | right | -0.07 | 0.11 | 0.11 | 0.95 | n/a | n/a | -1.58 | -7.46 | 2.59 | 0.61 |
| T2 refl. | reflection | left | -0.08 | -0.04 | 0.04 | 1.07 | n/a | n/a | -0.03 | -0.60 | 0.54 | 0.06 |
| T2-T3 | neighbour | left | 0.10 | 0.07 | 0.11 | 0.66 | n/a | n/a | -6.03 | -9.51 | 2.75 | 2.19 |
| T2-T4 | second-neighbour | left | -0.00 | 0.37 | 0.22 | 1.71 | n/a | n/a | 4.21 | 0.01 | 3.17 | 1.33 |
| T2-T5 | opposite | cross (left-right) | -0.75 | -1.12 | 0.15 | 7.70 | 0.67 | 0.16 | -0.41 | -3.21 | 3.28 | 0.12 |
| T2-T6 | second-neighbour | cross (left-right) | 0.35 | 1.09 | 0.22 | 5.04 | 0.32 | 0.21 | 1.96 | -3.04 | 3.72 | 0.53 |
| T3 refl. | reflection | left | -0.07 | -0.05 | 0.03 | 1.57 | n/a | n/a | -0.13 | -0.25 | 0.41 | 0.32 |
| T3-T4 | neighbour | left | -0.12 | 0.00 | 0.11 | 0.03 | n/a | n/a | -3.71 | -6.35 | 2.34 | 1.58 |
| T3-T5 | second-neighbour | cross (left-right) | 0.66 | 0.85 | 0.22 | 3.92 | 0.78 | 0.32 | -0.58 | -2.60 | 3.90 | 0.15 |
| T3-T6 | opposite | cross (left-right) | -0.88 | -1.21 | 0.12 | 9.99 | 0.73 | 0.12 | 0.21 | -4.78 | 3.56 | 0.06 |
| T4 refl. | reflection | self-mirror | -0.03 | 0.02 | 0.03 | 0.86 | n/a | n/a | -0.05 | -0.59 | 0.53 | 0.10 |
| T4-T5 | neighbour | right | -0.01 | -0.07 | 0.11 | 0.63 | n/a | n/a | -1.75 | -6.00 | 2.57 | 0.68 |
| T4-T6 | second-neighbour | right | 0.36 | 0.24 | 0.26 | 0.94 | n/a | n/a | 0.30 | -1.11 | 3.97 | 0.08 |
| T5 refl. | reflection | right | -0.01 | -0.06 | 0.03 | 1.77 | n/a | n/a | -0.03 | -0.31 | 0.41 | 0.07 |
| T5-T6 | neighbour | right | -0.06 | 0.06 | 0.11 | 0.55 | n/a | n/a | -1.56 | -8.70 | 3.57 | 0.44 |
| T6 refl. | reflection | right | -0.02 | -0.04 | 0.04 | 1.02 | n/a | n/a | -0.23 | -0.68 | 0.51 | 0.45 |

Neighbour paths, dose-response over every stage design (change against the CSF widening of the two lobes the path faces):
| bin | paths | mean_change | max_abs |
|---|---|---|---|
| (-0.1, 0.1] | 3 | -0.042 | 0.067 |
| (0.1, 6.0] | 10 | 0.020 | 0.124 |
| (6.0, 10.0] | 9 | -0.003 | 0.171 |
| (10.0, 13.0] | 4 | -0.289 | 0.346 |
| (13.0, 16.0] | 8 | -0.543 | 0.899 |
| (16.0, 19.0] | 8 | -0.826 | 0.991 |

What kind of change each path type sees (Mild - Healthy_sliced_new, median over the paths of each type; magnitude and phase changes are band-means of the absolute per-frequency change):
| path type | |S| band-rms dB | |dS| band-rms (Mild - healthy) dB | |dS| / |S| dB | mean |magnitude change| dB | mean |phase change| deg |
|---|---|---|---|---|---|
| reflection | -3.61 | -29.90 | -26.29 | 0.34 | 2.86 |
| neighbour | -36.85 | -51.77 | -14.88 | 0.40 | 7.55 |
| second-neighbour | -57.44 | -70.82 | -13.40 | 1.00 | 6.49 |
| opposite | -51.63 | -67.19 | -15.56 | 0.74 | 4.96 |

Neighbour paths, power against phase (LeftOnly and Mild minus Healthy_sliced_new):
| path | side | LeftOnly change dB | Mild change dB | clean ruler dB | LeftOnly phase change deg | Mild phase change deg | phase clean ruler deg | LeftOnly phase / ruler |
|---|---|---|---|---|---|---|---|---|
| T1-T2 | left | 0.09 | 0.06 | 0.11 | -3.94 | -7.65 | 2.83 | 1.39 |
| T1-T6 | right | -0.07 | 0.11 | 0.11 | -1.58 | -7.46 | 2.59 | 0.61 |
| T2-T3 | left | 0.10 | 0.07 | 0.11 | -6.03 | -9.51 | 2.75 | 2.19 |
| T3-T4 | left | -0.12 | 0.00 | 0.11 | -3.71 | -6.35 | 2.34 | 1.58 |
| T4-T5 | right | -0.01 | -0.07 | 0.11 | -1.75 | -6.00 | 2.57 | 0.68 |
| T5-T6 | right | -0.06 | 0.06 | 0.11 | -1.56 | -8.70 | 3.57 | 0.44 |

## A7. MCI cross-ratios against the circulant symmetry of each file
Both MCI_lobe and the healthy heads are rotationally symmetric by construction, so any non-circulant part of their band powers is numerical. Circulant residual of each file:
| file | path type | circulant residual rms dB |
|---|---|---|
| MCI_lobe_c3 | reflection | 0.009 |
| MCI_lobe_c3 | neighbour | 0.049 |
| MCI_lobe_c3 | second-neighbour | 0.163 |
| MCI_lobe_c3 | opposite | 0.044 |
| Healthy_sliced_new | reflection | 0.004 |
| Healthy_sliced_new | neighbour | 0.047 |
| Healthy_sliced_new | second-neighbour | 0.076 |
| Healthy_sliced_new | opposite | 0.048 |
| Healthy_sliced | reflection | 0.003 |
| Healthy_sliced | neighbour | 0.027 |
| Healthy_sliced | second-neighbour | 0.091 |
| Healthy_sliced | opposite | 0.049 |

Each cross-ratio of MCI - Healthy_sliced_new split into the change of the circulant projection (physics a symmetric head can produce) and the change of the residual (numerical), with the same-design mesh-only difference Healthy_sliced - Healthy_sliced_new alongside:
| cross-ratio | MCI - Healthy_new dB | circulant part dB | non-circulant (residual) part dB | / noise SD | Healthy_sliced - Healthy_new (same design, mesh only) dB | mesh-only / noise SD |
|---|---|---|---|---|---|---|
| T1T2·T4T6 / T1T6·T2T4 | 0.672 | 0.000 | 0.672 | 4.072 | 0.248 | 1.504 |
| T1T5·T4T6 / T1T6·T4T5 | 0.582 | 0.023 | 0.559 | 4.062 | 0.377 | 2.635 |
| T1T2·T4T6 / T1T4·T2T6 | 0.616 | 0.028 | 0.587 | 3.669 | 0.100 | 0.594 |
| T1T3·T4T6 / T1T6·T3T4 | 0.530 | 0.023 | 0.508 | 3.567 | 0.140 | 0.941 |
| T1T2·T5T6 / T1T6·T2T5 | 0.283 | 0.028 | 0.254 | 3.529 | -0.130 | 1.627 |
| T2T5·T4T6 / T2T6·T4T5 | 0.509 | -0.028 | 0.538 | 3.153 | 0.392 | 2.426 |
| T1T3·T4T6 / T1T4·T3T6 | 0.501 | 0.080 | 0.421 | 3.063 | -0.092 | 0.562 |
| T1T3·T5T6 / T1T6·T3T5 | 0.446 | 0.000 | 0.446 | 2.964 | -0.126 | 0.836 |
| T2T3·T4T6 / T2T6·T3T4 | 0.457 | 0.000 | 0.457 | 2.908 | 0.175 | 1.115 |
| T2T3·T4T6 / T2T4·T3T6 | 0.483 | 0.028 | 0.455 | 2.847 | 0.092 | 0.541 |
| T1T4·T5T6 / T1T5·T4T6 | -0.406 | -0.051 | -0.355 | 2.601 | -0.215 | 1.381 |
| T2T3·T5T6 / T2T6·T3T5 | 0.373 | -0.023 | 0.395 | 2.412 | -0.091 | 0.586 |

## A8. Lobe-Mild under the three-stage rule
Distance of R21 to the nearest point where the frozen three-stage label changes, against the R21 yardstick and the bootstrap SD of that boundary (A9):
| set | design | rule | feature dB | frozen label | distance to label edge dB | feature yardstick dB | boundary bootstrap SD dB | / yardstick | / boundary SD | / max(yardstick, boundary SD) | verdict (one bar) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lobe_A | Mild_lobe | three | -19.974 | UNCERTAIN | 0.007 | 0.110 | 0.065 | 0.059 | 0.099 | 0.059 | not determined (< 2x) |
| lobe_B | Mild_lobe_new | three | -19.940 | Mild | -0.028 | 0.110 | 0.065 | 0.255 | 0.428 | 0.255 | not determined (< 2x) |

Neither set clears 2x: the 0.41 vs 0.69 difference between the sets is what an undetermined label looks like. 'weakened' for lobe_B came from the fraction-correct tier (>= 0.5), which ignores mesh and boundary uncertainty; under the one bar it is 'not determined', i.e. retracted in both sets.

## Summary
| question | verdict | old -> new | evidence |
|---|---|---|---|
| A9 tau uncertainty | CHANGED (new number) | not reported -> tau SD 0.055 dB (solve bootstrap), 95% CI width 0.20 dB; P(label changes): LeftOnly 0.06, Severe_lobe 0.00, Severe_lobe_c3 0.00 | results/05_lobe/review/A9_boundaries.csv |
| A1 one bar | CHANGED (labels); the bar itself was one bar (aff9d56) | 'holds' for sub-3x detection margins -> Mild_lobe three 0.1x (not determined (< 2x)); Mild_lobe three_merged 3.0x (sensitive (2-3x)); Severe_lobe binary 1.4x (not determined (< 2x)); Severe_lobe three_merged 1.9x (not determined (< 2x)); Mild_lobe_new three 0.3x (not determined (< 2x)); Severe_lobe_c3 binary 1.7x (not determined (< 2x)); Severe_lobe_c3 three_merged 2.9x (sensitive (2-3x)); LeftOnly_test_c3 binary 0.7x (not determined (< 2x)); LeftOnly_test_c3 three 1.9x (not determined (< 2x)); LeftOnly_test_c3 three_merged 0.7x (not determined (< 2x)) | results/05_lobe/review/A1_one_bar.csv |
| A2 test designed to fail? | CHANGED (design flaw stated) | 'could not succeed' -> under-powered by design and knowable before cf56de8: P(pred. 1 passes | model right) = 0.58; predicted cross-ratios <= 2.7x the lobe_v1-era floor (0.43 dB) | results/05_lobe/review/A2_power.csv |
| A3 mirror test | CONFIRMED for the power indices; CHANGED overall | 'no left-right difference beyond the rulers' -> band power: 2/33 statistics >= 3x clean (T2 refl. vs T6 refl., T3 refl. vs T5 refl.; measured <= 1.8x); phase pairs 0/8; but 16/22 phase cross-ratios >= 3x the clean ruler (16 beyond every symmetric design; 2 still >= 3x with ±2 dB/±10° errors) | results/05_lobe/review/A3_mirror_test.csv |
| A4 imaging gets the sign | CHANGED: my indices discard the information | 'no left-right difference' -> the inversion's LR is 4.9x the mirror null rms (1.9x its max) and 85% phase; with measurement errors 0.4x (±0.5 dB), 0.4x (±2 dB ±10°) for the primary method | results/05_lobe/review/A4_imaging_operator.csv |
| A5 locality loses? | CHANGED | miss -> Healthy_sliced: +0.031 dB [-0.029, +0.087], P(locality wins) 0.19: no preference (interval contains 0); Healthy_sliced_new: +0.045 dB [-0.017, +0.095], P(locality wins) 0.09: no preference (interval contains 0) | results/05_lobe/review/A5_locality_vs_baseline.csv |
| A6 mechanism | CHANGED (claim withdrawn; mechanism measured) | 'weaker copy of the symmetric Mild change; long paths wrap round' -> holds for band power only. Neighbour paths change in phase, not power: |dS|/|S| -14.9 dB with a 0.40 dB magnitude and 7.6 deg phase change (Mild); LeftOnly phase change left -6.0 to -3.7 deg vs right -1.8 to -1.6 deg (Mild -9.5 to -6.0 deg on both sides). Left larger than right, but per path or pair only 2-3x the rulers (mirror-test neighbour phase index 2.4x clean, 3.4x null rms); the decisive left-right evidence is the phase cross-ratios (A3). Wrap-round vs a global CSF_Mild component is not separable in power | results/05_lobe/review/A6_*.csv |
| A7 MCI 4x = mesh? | CONFIRMED (now with evidence) | asserted -> the 7 cross-ratios >= 3x noise SD are 95% non-circulant (mean |residual part| / |total|); the same-design mesh-only difference reaches 3.1x noise SD (2 cross-ratios >= 3x) | results/05_lobe/review/A7_mci_circulant.csv |
| A8 lobe-Mild three-stage | CHANGED (reverted) | lobe_B 'weakened' -> retracted (not determined): Mild_lobe +0.007 dB = 0.06x; Mild_lobe_new -0.028 dB = 0.26x | results/05_lobe/review/A1_one_bar.csv |

One solve per design: within-simulation noise robustness, not generalisation.