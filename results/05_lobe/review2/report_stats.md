# Adversarial review round 2, main session: statistics (code 2a222ff)

Every number is recomputed from the raw files by `scripts/11_review2.py`. Floor rule (R1c) and verdict bar are in the script docstring and were fixed before any round-2 number existed. One solve per design: within-simulation noise robustness, not generalisation.

## R1. The floor dispute
**(a) Empirical null of the imaging mirror-test LR (T = (LR(S) - LR(mirror S))/2) over the nine mirror-symmetric designs**, normality and rank p:
| method | reference | T(LeftOnly) | floor (max |null|) | yardstick | clean ruler | ratio | verdict | rank p | ratio to null rms | null mean | Shapiro-Wilk W | Shapiro-Wilk p | SW p without Moderate_lobe | one-sided rank p (T_LO > all null) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tikhonov dS (primary) | Healthy_sliced (7 passes) | 7.860 | 4.071 | 2.143 | 4.071 | 1.930 | not separable (< 2x) | 0.100 | 4.859 | -0.985 | 0.837 | 0.054 | 0.457 | 0.100 |
| Tikhonov dS (primary) | Healthy_sliced_new (6 passes) | 7.857 | 4.042 | 2.123 | 4.042 | 1.944 | not separable (< 2x) | 0.100 | 4.897 | -0.970 | 0.838 | 0.055 | 0.458 | 0.100 |
| Tikhonov log (gain-inv.) | Healthy_sliced (7 passes) | 8.754 | 3.723 | 2.376 | 3.723 | 2.351 | sensitive (2-3x) | 0.100 | 6.102 | -0.910 | 0.816 | 0.031 | 0.965 | 0.100 |
| Tikhonov log (gain-inv.) | Healthy_sliced_new (6 passes) | 8.822 | 3.757 | 2.375 | 3.757 | 2.348 | sensitive (2-3x) | 0.100 | 6.075 | -0.923 | 0.822 | 0.036 | 0.977 | 0.100 |
| whitened log (post-hoc) | Healthy_sliced (7 passes) | 8.690 | 3.143 | 1.978 | 3.143 | 2.765 | sensitive (2-3x) | 0.100 | 7.209 | -0.751 | 0.806 | 0.024 | 0.856 | 0.100 |
| whitened log (post-hoc) | Healthy_sliced_new (6 passes) | 8.773 | 3.168 | 1.974 | 3.168 | 2.769 | sensitive (2-3x) | 0.100 | 7.202 | -0.756 | 0.811 | 0.027 | 0.833 | 0.100 |

Null values (Healthy_sliced_new reference):
| design | Tikhonov dS (primary) | Tikhonov log (gain-inv.) | whitened log (post-hoc) |
|---|---|---|---|
| Healthy_sliced | -0.85 | -0.90 | -0.87 |
| Healthy_sliced_new | -1.14 | -1.09 | -0.81 |
| MCI_lobe_c3 | 0.22 | -0.21 | -0.20 |
| Mild_lobe | -0.36 | -0.64 | -0.38 |
| Mild_lobe_new | 0.05 | -0.29 | -0.19 |
| Moderate_lobe | -4.04 | -3.76 | -3.17 |
| Moderate_lobe_c3 | -1.92 | -1.38 | -1.19 |
| Severe_lobe | -0.95 | -0.47 | -0.37 |
| Severe_lobe_c3 | 0.25 | 0.43 | 0.36 |

**(b) Why Moderate_lobe.** Its T is decomposed exactly into path contributions (Tikhonov dS is linear in dS). Largest Moderate_lobe contributions: T2-T3 -1.31, T5-T6 -1.28, T1-T6 -0.45, T4-T5 -0.38. Path contributions of every design:
| path | Healthy_sliced | Healthy_sliced_new | LeftOnly_test_c3 | MCI_lobe_c3 | Mild_lobe | Mild_lobe_new | Moderate_lobe | Moderate_lobe_c3 | Severe_lobe | Severe_lobe_c3 |
|---|---|---|---|---|---|---|---|---|---|---|
| SUM (= T) | -0.85 | -1.14 | 7.86 | 0.22 | -0.36 | 0.05 | -4.04 | -1.92 | -0.95 | 0.25 |
| T1 refl. | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| T1-T2 | -0.09 | -0.16 | 0.45 | 0.10 | -0.14 | -0.06 | -0.37 | -0.26 | -0.06 | -0.07 |
| T1-T3 | -0.06 | -0.01 | 0.22 | 0.13 | 0.17 | 0.09 | -0.06 | -0.08 | 0.06 | 0.18 |
| T1-T4 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| T1-T5 | -0.07 | -0.02 | 0.24 | 0.15 | 0.14 | 0.05 | -0.06 | -0.07 | 0.08 | 0.21 |
| T1-T6 | -0.09 | -0.18 | 0.48 | 0.16 | -0.13 | -0.02 | -0.45 | -0.32 | -0.07 | -0.04 |
| T2 refl. | 0.03 | 0.03 | 0.39 | 0.04 | -0.01 | 0.01 | 0.05 | 0.04 | 0.02 | 0.02 |
| T2-T3 | -0.14 | -0.44 | 1.75 | 0.00 | -0.27 | -0.04 | -1.31 | -0.67 | -0.15 | 0.20 |
| T2-T4 | -0.04 | 0.06 | 0.19 | -0.03 | 0.21 | 0.06 | 0.05 | 0.01 | -0.06 | -0.03 |
| T2-T5 | 0.00 | 0.00 | 0.03 | -0.01 | -0.01 | -0.02 | 0.01 | 0.02 | 0.01 | 0.02 |
| T2-T6 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| T3 refl. | -0.02 | -0.02 | 0.38 | -0.01 | 0.05 | 0.03 | -0.01 | 0.00 | 0.01 | 0.00 |
| T3-T4 | -0.16 | -0.06 | 0.52 | -0.17 | -0.17 | -0.04 | -0.34 | -0.03 | -0.33 | -0.25 |
| T3-T5 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| T3-T6 | 0.01 | 0.01 | 0.01 | -0.00 | 0.00 | -0.00 | 0.00 | 0.00 | 0.00 | 0.01 |
| T4 refl. | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| T4-T5 | -0.14 | -0.06 | 0.45 | -0.18 | -0.18 | -0.05 | -0.38 | -0.02 | -0.39 | -0.28 |
| T4-T6 | -0.04 | 0.07 | 0.17 | -0.03 | 0.18 | 0.03 | 0.03 | 0.01 | -0.07 | -0.03 |
| T5 refl. | -0.02 | -0.02 | 0.41 | -0.01 | 0.06 | 0.04 | -0.01 | 0.00 | 0.02 | -0.00 |
| T5-T6 | -0.08 | -0.36 | 1.74 | 0.03 | -0.26 | -0.05 | -1.28 | -0.60 | -0.04 | 0.27 |
| T6 refl. | 0.04 | 0.04 | 0.43 | 0.05 | 0.01 | 0.02 | 0.09 | 0.06 | 0.03 | 0.02 |

Per-pair mirror residuals (power dB, band mean; phase deg at 3.4 GHz) with mesh data:
| design | passes | elements | final_dS | power T1-T2 vs T1-T6 dB | phase T1-T2 vs T1-T6 deg (3.4 GHz) | power T1-T3 vs T1-T5 dB | phase T1-T3 vs T1-T5 deg (3.4 GHz) | power T2 refl. vs T6 refl. dB | phase T2 refl. vs T6 refl. deg (3.4 GHz) | power T2-T3 vs T5-T6 dB | phase T2-T3 vs T5-T6 deg (3.4 GHz) | power T2-T4 vs T4-T6 dB | phase T2-T4 vs T4-T6 deg (3.4 GHz) | power T2-T5 vs T3-T6 dB | phase T2-T5 vs T3-T6 deg (3.4 GHz) | power T3 refl. vs T5 refl. dB | phase T3 refl. vs T5 refl. deg (3.4 GHz) | power T3-T4 vs T4-T5 dB | phase T3-T4 vs T4-T5 deg (3.4 GHz) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | 7 | 1349491 | 0.009 | -0.048 | 0.667 | -0.083 | -0.923 | -0.002 | 0.495 | -0.032 | 0.041 | -0.052 | -0.752 | 0.017 | 0.218 | -0.005 | -0.204 | 0.025 | 0.631 |
| Healthy_sliced_new | 6 | 1081728 | 0.015 | -0.070 | 0.715 | 0.074 | -0.737 | -0.005 | 0.547 | -0.049 | 0.201 | 0.173 | 0.249 | 0.015 | 0.040 | -0.007 | -0.339 | -0.056 | 0.418 |
| Mild_lobe | 5 | 739774 | 0.019 | -0.119 | 1.363 | 0.069 | 0.794 | -0.005 | 0.208 | -0.037 | 0.254 | 0.301 | 1.646 | 0.106 | 0.916 | -0.001 | 0.354 | 0.017 | 0.252 |
| Mild_lobe_new | 6 | 878656 | 0.015 | -0.028 | 1.162 | 0.106 | 0.457 | -0.001 | 0.220 | 0.019 | -0.370 | 0.053 | -0.218 | -0.004 | 1.017 | 0.004 | 0.299 | 0.060 | -0.165 |
| Moderate_lobe | 5 | 796281 | 0.019 | -0.040 | 1.051 | -0.361 | 2.308 | 0.008 | 0.572 | -0.087 | 2.053 | 0.130 | 0.042 | 0.091 | 0.879 | -0.014 | -0.294 | 0.043 | -0.117 |
| Moderate_lobe_c3 | 6 | 949865 | 0.015 | 0.019 | 0.486 | -0.495 | 0.471 | 0.011 | 0.548 | -0.201 | 0.573 | 0.131 | -0.165 | 0.209 | 0.739 | -0.004 | -0.029 | 0.050 | -0.262 |
| Severe_lobe | 5 | 690077 | 0.020 | -0.024 | -0.199 | 0.108 | 1.107 | 0.017 | 0.444 | -0.295 | -0.062 | -0.103 | -0.738 | 0.067 | -0.496 | 0.007 | 0.118 | -0.046 | 0.005 |
| Severe_lobe_c3 | 6 | 819294 | 0.012 | 0.067 | 0.167 | 0.149 | 0.468 | 0.008 | 0.422 | -0.222 | -0.177 | 0.029 | -3.219 | 0.123 | -0.835 | -0.005 | -0.141 | -0.066 | -0.058 |
| MCI_lobe_c3 | 6 | 981160 | 0.014 | 0.127 | 0.727 | 0.171 | -1.150 | 0.004 | 0.538 | -0.039 | 0.278 | -0.301 | 0.897 | -0.072 | -0.089 | -0.006 | -0.089 | 0.092 | 0.532 |
| LeftOnly_test_c3 | 6 | 941358 | 0.015 | 0.082 | -2.897 | 0.108 | 2.868 | -0.060 | 4.838 | 0.103 | -5.579 | -0.193 | 4.341 | 0.151 | -0.377 | -0.068 | 4.943 | -0.175 | -3.320 |

**(c) One floor rule** (script docstring): floor = max |value| over the nine mirror-symmetric designs; clean ruler = max(floor, one-pass yardstick); >= 3x established, 2-3x sensitive, < 2x not separable. Applied to the main session's reference-free statistics:
| family | n | >= 3x (established) | 2-3x (sensitive) | best ratio | beyond all 9 (rank p 0.1) |
|---|---|---|---|---|---|
| phase LR index | 3 | 0 | 0 | 1.48 | 2 |
| phase cross-ratio | 22 | 4 | 6 | 4.03 | 16 |
| phase pair | 8 | 0 | 0 | 1.52 | 5 |
| power LR index | 3 | 0 | 0 | 0.22 | 0 |
| power cross-ratio | 22 | 0 | 0 | 1.23 | 4 |
| power pair | 8 | 2 | 0 | 5.00 | 3 |

## R2. Main 16/22 against imaging b9_anti: one quantity, one ruler
Both families evaluated reference-free (design against its own port mirror) at the band mean, at 3.30-3.65 GHz and at the three imaging fit frequencies, with the R1c floor rule:
| quantity | frequencies | n | >= 3x | 2-3x | best ratio |
|---|---|---|---|---|---|
| cross-ratio phase | 3.30-3.65 GHz | 22 | 9 | 5 | 4.05 |
| cross-ratio phase | 3.4 GHz | 22 | 5 | 11 | 4.26 |
| cross-ratio phase | 3.6 GHz | 22 | 0 | 0 | 1.77 |
| cross-ratio phase | 3.8 GHz | 22 | 0 | 0 | 1.23 |
| cross-ratio phase | band mean 3.2-4.2 | 22 | 4 | 6 | 4.03 |
| pair phase (left minus mirror path) | 3.30-3.65 GHz | 8 | 1 | 1 | 4.58 |
| pair phase (left minus mirror path) | 3.4 GHz | 8 | 3 | 2 | 13.97 |
| pair phase (left minus mirror path) | 3.6 GHz | 8 | 0 | 0 | 1.91 |
| pair phase (left minus mirror path) | 3.8 GHz | 8 | 0 | 0 | 0.73 |
| pair phase (left minus mirror path) | band mean 3.2-4.2 | 8 | 0 | 0 | 1.52 |

Why the two families disagree: share of the reference-free left-right phase asymmetry (3.30-3.65 GHz) explained by per-antenna (separable) terms, which cancel in cross-ratios but not in single path pairs:
| design | rms LR phase asymmetry, all (deg) | rms per-antenna (separable) part (deg) | rms non-separable part (deg) | separable share of power |
|---|---|---|---|---|
| Healthy_sliced | 1.50 | 0.70 | 1.32 | 0.22 |
| Healthy_sliced_new | 1.01 | 0.52 | 0.86 | 0.27 |
| Mild_lobe | 2.02 | 1.18 | 1.63 | 0.34 |
| Mild_lobe_new | 1.40 | 0.75 | 1.18 | 0.29 |
| Moderate_lobe | 2.03 | 1.71 | 1.09 | 0.71 |
| Moderate_lobe_c3 | 1.37 | 0.87 | 1.06 | 0.40 |
| Severe_lobe | 1.32 | 0.89 | 0.98 | 0.46 |
| Severe_lobe_c3 | 2.18 | 1.24 | 1.79 | 0.33 |
| MCI_lobe_c3 | 1.72 | 0.74 | 1.55 | 0.18 |
| LeftOnly_test_c3 | 4.61 | 1.39 | 4.40 | 0.09 |

## R3. Detuning hypothesis (predictions committed in predictions_R3_C4.md before this ran)
Reflection resonance (min |Sii|) and depth per antenna; left - right = mean(T2, T3) - mean(T6, T5):
| design | T1 f_res MHz | T1 depth dB | T2 f_res MHz | T2 depth dB | T3 f_res MHz | T3 depth dB | T4 f_res MHz | T4 depth dB | T5 f_res MHz | T5 depth dB | T6 f_res MHz | T6 depth dB | left-right f_res MHz | left-right depth dB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | 3658.96 | -20.97 | 3659.03 | -21.26 | 3660.42 | -20.98 | 3658.46 | -21.15 | 3659.21 | -21.04 | 3659.16 | -20.88 | 0.54 | -0.16 |
| Healthy_sliced_new | 3657.70 | -21.25 | 3658.16 | -21.31 | 3659.44 | -21.03 | 3656.69 | -21.18 | 3657.63 | -21.06 | 3656.74 | -20.83 | 1.61 | -0.23 |
| Mild_lobe | 3654.20 | -20.49 | 3656.88 | -20.53 | 3655.11 | -20.99 | 3654.70 | -20.20 | 3654.82 | -20.15 | 3653.44 | -19.97 | 1.86 | -0.70 |
| Mild_lobe_new | 3655.85 | -20.87 | 3657.63 | -20.64 | 3656.70 | -21.15 | 3655.34 | -20.45 | 3656.65 | -20.56 | 3655.35 | -20.24 | 1.17 | -0.50 |
| Moderate_lobe | 3658.15 | -20.96 | 3657.44 | -20.28 | 3657.29 | -20.60 | 3656.95 | -21.27 | 3656.10 | -20.70 | 3652.90 | -20.11 | 2.86 | -0.03 |
| Moderate_lobe_c3 | 3658.33 | -20.92 | 3658.51 | -20.50 | 3658.20 | -20.72 | 3658.20 | -21.05 | 3658.28 | -20.87 | 3655.30 | -20.59 | 1.57 | 0.13 |
| Severe_lobe | 3658.33 | -20.86 | 3655.63 | -20.20 | 3655.97 | -20.61 | 3655.16 | -20.92 | 3654.67 | -20.80 | 3655.79 | -20.29 | 0.57 | 0.14 |
| Severe_lobe_c3 | 3659.18 | -20.88 | 3657.07 | -20.53 | 3656.57 | -20.70 | 3657.03 | -21.06 | 3657.30 | -20.89 | 3657.70 | -20.43 | -0.68 | 0.05 |
| MCI_lobe_c3 | 3655.53 | -21.07 | 3658.00 | -21.47 | 3657.97 | -21.17 | 3657.02 | -20.74 | 3657.15 | -20.76 | 3656.60 | -20.89 | 1.11 | -0.49 |
| LeftOnly_test_c3 | 3657.86 | -20.71 | 3656.93 | -20.26 | 3658.77 | -20.20 | 3656.26 | -21.07 | 3656.32 | -20.82 | 3655.56 | -20.80 | 1.91 | 0.58 |

LeftOnly left-right resonance shift +1.91 MHz against the largest of the symmetric designs 2.86 MHz.
Per-antenna (separable) model of the LeftOnly transmission change, ln S_ab(LO)/S_ab(ref) = g_a + g_b + r_ab:
| reference | band | rms LR phase asymmetry of transmissions (deg) | separable (per-antenna) share | per-antenna phase terms T1..T6 (deg) | reflection phase change T1..T6 (deg) | corr(per-antenna term, reflection phase change) |
|---|---|---|---|---|---|---|
| Healthy_sliced | 3.2-4.2 | 4.57 | 0.19 | -0.36, -1.39, -2.02, -0.27, -1.75, -0.78 | -0.36, -0.31, -0.41, -0.26, -0.33, -0.43 | 0.30 |
| Healthy_sliced | 3.30-3.65 | 5.78 | 0.09 | -0.61, -0.48, -1.13, -0.58, -0.92, +0.15 | +0.46, +1.44, +1.16, +0.22, +0.59, +0.19 | -0.45 |
| Healthy_sliced_new | 3.2-4.2 | 4.29 | 0.20 | +0.05, -0.60, -1.23, +0.46, -0.74, +0.28 | -0.09, -0.03, -0.13, -0.05, -0.03, -0.23 | -0.23 |
| Healthy_sliced_new | 3.30-3.65 | 5.17 | 0.11 | -0.24, +0.41, -0.51, +0.17, -0.01, +1.48 | +0.60, +1.37, +1.06, +0.08, +0.47, -0.06 | -0.51 |

## R4. Detection feature choice (shown, not adopted; any new rule needs pre-registration and a new blind design)
R21 alone, fitted exactly like tau (03 code, same training draws): tau21 = -20.071 dB, margin 0.087 dB. (R31, R21) pair: LDA (lsqr, Ledoit-Wolf, equal priors) on the same draws; distance to its boundary in dB along the normal; projected one-pass yardstick 0.110 dB. Uniform designs are training data (in-sample).
| set | design | R31 | R21 | R31 frozen: label | R31: / yardstick | R21 alone: label | R21: / yardstick | (R31, R21) LDA: label | pair: distance dB | pair: / projected yardstick |
|---|---|---|---|---|---|---|---|---|---|---|
| lobe_A | Healthy_sliced_new | -14.744 | -20.567 | Normal | 3.334 | Normal | 3.721 | Normal | -0.805 | 7.350 |
| lobe_A | Mild_lobe | -15.822 | -19.974 | AD | 3.486 | AD | 0.094 | AD | 0.404 | 3.686 |
| lobe_A | Moderate_lobe | -16.008 | -19.451 | AD | 4.862 | AD | 4.860 | AD | 0.744 | 6.789 |
| lobe_A | Severe_lobe | -15.533 | -18.002 | AD | 1.351 | AD | 18.065 | AD | 0.746 | 6.812 |
| lobe_B | Healthy_sliced | -14.609 | -20.507 | Normal | 4.337 | Normal | 3.174 | Normal | -0.915 | 8.350 |
| lobe_B | Mild_lobe_new | -15.856 | -19.940 | AD | 3.741 | AD | 0.401 | AD | 0.447 | 4.078 |
| lobe_B | Moderate_lobe_c3 | -16.012 | -19.451 | AD | 4.888 | AD | 4.859 | AD | 0.747 | 6.822 |
| lobe_B | Severe_lobe_c3 | -15.584 | -17.892 | AD | 1.728 | AD | 19.065 | AD | 0.829 | 7.568 |
| tests | LeftOnly_test_c3 | -15.445 | -20.200 | AD | 0.696 | Normal | 0.375 | Normal | -0.025 | 0.228 |
| tests | MCI_lobe_c3 | -14.773 | -20.555 | Normal | 3.123 | Normal | 3.617 | Normal | -0.775 | 7.071 |
| uniform (training) | brain_sevem_layer_Healthy.s6p | -14.479 | -20.395 | Normal | 5.299 | Normal | 2.151 | Normal | -1.004 | 9.159 |
| uniform (training) | new_Healthy.s6p | -14.674 | -20.722 | Normal | 3.856 | Normal | 5.130 | Normal | -0.921 | 8.403 |
| uniform (training) | new_MCI.s6p | -14.614 | -20.685 | Normal | 4.300 | Normal | 4.795 | Normal | -0.966 | 8.816 |
| uniform (training) | Brain_sevem_layer_MildAD.s6p | -16.195 | -19.308 | AD | 6.250 | AD | 6.161 | AD | 0.967 | 8.822 |
| uniform (training) | new_MildAD.s6p | -16.058 | -19.479 | AD | 5.228 | AD | 4.606 | AD | 0.782 | 7.141 |
| uniform (training) | Brain_sevem_layer_ModerateAD.s6p | -16.505 | -19.768 | AD | 8.540 | AD | 1.972 | AD | 1.117 | 10.196 |
| uniform (training) | new_ModerateAD.s6p | -16.168 | -19.526 | AD | 6.046 | AD | 4.180 | AD | 0.872 | 7.963 |
| uniform (training) | brain_sevem_layer_SevereAD.s6p | -15.850 | -18.164 | AD | 3.693 | AD | 16.584 | AD | 0.996 | 9.093 |
| uniform (training) | new_SevereAD.s6p | -15.851 | -18.058 | AD | 3.700 | AD | 17.551 | AD | 1.030 | 9.402 |

Why R31 was frozen: on the training solves it had the widest Normal-AD gap of the calibration-free ratios (closest solves: v2 Normal and the Severe solves). That choice was made on 2026-09-28 (6eca5d7), before any lobe file existed.

## R6 / A28. Label margins with every ruler
Margins to the label edge against (A1) max(yardstick, boundary bootstrap SD), and with the single-measurement spread added in quadrature. Effective sample size: the boundary SD resamples the training solves, but the v1/v2 solves of a stage differ only in sweep settings and very likely share a mesh, so there is effectively one healthy design behind tau; its head-to-head uncertainty is not estimable from these data (the SD is a lower bound).
| set | design | rule | label | edge margin dB | yardstick | boundary SD | meas SD ±0.5 dB | meas SD ±2 dB ±10° | A1 ratio max(yard, bSD) | quadrature ±0.5 dB | quadrature ±2 dB ±10° | P(label differs | boundary bootstrap) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lobe_A | Healthy_sliced_new | binary | Normal | -0.450 | 0.135 | 0.054 | 0.027 | 0.027 | 3.334 | 3.045 | 3.046 | 0.000 |
| lobe_A | Healthy_sliced_new | three | Normal | 0.580 | 0.110 | 0.066 | 0.047 | 0.049 | 5.280 | 4.249 | 4.224 | 0.000 |
| lobe_A | Healthy_sliced_new | three_merged | Normal | -1.184 | 0.161 | 0.038 | 0.054 | 0.055 | 7.361 | 6.807 | 6.798 | 0.000 |
| lobe_A | Mild_lobe | binary | AD | 0.471 | 0.135 | 0.054 | 0.027 | 0.027 | 3.486 | 3.183 | 3.184 | 0.000 |
| lobe_A | Mild_lobe | three | UNCERTAIN | 0.007 | 0.110 | 0.066 | 0.047 | 0.049 | 0.059 | 0.048 | 0.047 | 0.756 |
| lobe_A | Mild_lobe | three_merged | Mild+Moderate | 0.481 | 0.161 | 0.038 | 0.054 | 0.055 | 2.987 | 2.762 | 2.759 | 0.000 |
| lobe_A | Moderate_lobe | binary | AD | 0.657 | 0.135 | 0.054 | 0.027 | 0.027 | 4.862 | 4.440 | 4.442 | 0.000 |
| lobe_A | Moderate_lobe | three | Mild | -0.517 | 0.110 | 0.066 | 0.047 | 0.049 | 4.711 | 3.791 | 3.768 | 0.000 |
| lobe_A | Moderate_lobe | three_merged | Mild+Moderate | -0.660 | 0.161 | 0.035 | 0.054 | 0.055 | 4.103 | 3.807 | 3.802 | 0.000 |
| lobe_A | Severe_lobe | binary | AD | 0.183 | 0.135 | 0.054 | 0.027 | 0.027 | 1.351 | 1.233 | 1.234 | 0.000 |
| lobe_A | Severe_lobe | three | Severe | -0.743 | 0.110 | 0.035 | 0.047 | 0.049 | 6.770 | 5.964 | 5.922 | 0.000 |
| lobe_A | Severe_lobe | three_merged | Severe | 0.298 | 0.161 | 0.035 | 0.054 | 0.055 | 1.853 | 1.719 | 1.717 | 0.000 |
| lobe_B | Healthy_sliced | binary | Normal | -0.586 | 0.135 | 0.054 | 0.027 | 0.027 | 4.337 | 3.960 | 3.962 | 0.000 |
| lobe_B | Healthy_sliced | three | Normal | 0.520 | 0.110 | 0.066 | 0.047 | 0.049 | 4.734 | 3.809 | 3.787 | 0.000 |
| lobe_B | Healthy_sliced | three_merged | Normal | -1.259 | 0.161 | 0.038 | 0.054 | 0.055 | 7.827 | 7.238 | 7.228 | 0.000 |
| lobe_B | Mild_lobe_new | binary | AD | 0.506 | 0.135 | 0.054 | 0.027 | 0.027 | 3.741 | 3.416 | 3.417 | 0.000 |
| lobe_B | Mild_lobe_new | three | Mild | -0.028 | 0.110 | 0.066 | 0.047 | 0.049 | 0.255 | 0.205 | 0.204 | 0.381 |
| lobe_B | Mild_lobe_new | three_merged | Mild+Moderate | 0.549 | 0.161 | 0.038 | 0.054 | 0.055 | 3.410 | 3.153 | 3.149 | 0.000 |
| lobe_B | Moderate_lobe_c3 | binary | AD | 0.661 | 0.135 | 0.054 | 0.027 | 0.027 | 4.888 | 4.464 | 4.465 | 0.000 |
| lobe_B | Moderate_lobe_c3 | three | Mild | -0.517 | 0.110 | 0.066 | 0.047 | 0.049 | 4.711 | 3.791 | 3.768 | 0.000 |
| lobe_B | Moderate_lobe_c3 | three_merged | Mild+Moderate | -0.656 | 0.161 | 0.035 | 0.054 | 0.055 | 4.078 | 3.784 | 3.779 | 0.000 |
| lobe_B | Severe_lobe_c3 | binary | AD | 0.234 | 0.135 | 0.054 | 0.027 | 0.027 | 1.728 | 1.578 | 1.579 | 0.000 |
| lobe_B | Severe_lobe_c3 | three | Severe | -0.852 | 0.110 | 0.035 | 0.047 | 0.049 | 7.768 | 6.843 | 6.795 | 0.000 |
| lobe_B | Severe_lobe_c3 | three_merged | Severe | 0.459 | 0.161 | 0.035 | 0.054 | 0.055 | 2.854 | 2.648 | 2.644 | 0.000 |
| tests | LeftOnly_test_c3 | binary | AD | 0.094 | 0.135 | 0.054 | 0.027 | 0.027 | 0.696 | 0.635 | 0.635 | 0.063 |
| tests | LeftOnly_test_c3 | three | Normal | 0.212 | 0.110 | 0.066 | 0.047 | 0.049 | 1.932 | 1.554 | 1.545 | 0.000 |
| tests | LeftOnly_test_c3 | three_merged | Normal | -0.116 | 0.161 | 0.038 | 0.054 | 0.055 | 0.721 | 0.667 | 0.666 | 0.000 |
| tests | MCI_lobe_c3 | binary | Normal | -0.422 | 0.135 | 0.054 | 0.027 | 0.027 | 3.123 | 2.852 | 2.853 | 0.000 |
| tests | MCI_lobe_c3 | three | Normal | 0.568 | 0.110 | 0.066 | 0.047 | 0.049 | 5.176 | 4.165 | 4.140 | 0.000 |
| tests | MCI_lobe_c3 | three_merged | Normal | -1.144 | 0.161 | 0.038 | 0.054 | 0.055 | 7.112 | 6.577 | 6.568 | 0.000 |

Labels >= 3x: A1 20/30, quadrature ±0.5 dB 19, quadrature ±2 dB ±10° 19. Labels that change somewhere inside the boundary's bootstrap distribution (P > 0.025): 3 of 30: Mild_lobe three, Mild_lobe_new three, LeftOnly_test_c3 binary.

## A14. Port map
The symmetry search scores every ring ordering by how circulant |S| becomes. A mirrored assignment gives exactly the same score (Healthy_sliced):
| assignment | circulant score dB |
|---|---|
| config: Port1..6 = T4,T3,T2,T1,T6,T5 | 0.149969 |
| mirror image (T2<->T6, T3<->T5) | 0.149969 |

So the search cannot decide left from right. The assignment is fixed by geometry: (1) HFSS audit (data/hfss_geometry_audit_Healthy_sliced.txt): excitations in order FEED_3_T4, T3, T2, T1, T6, T5 and lumped-port sheets Rectangle1..6 at azimuth +89.6, +29.6, -30.4, -90.4, -150.4, +149.6 deg; the user's GUI check ties excitation 2 (FEED_3_T3) to Rectangle2 (+29.6 deg); (2) the field exports E_Normal_T#, located from their own fields (scripts/12_review2_fields.py). A mirrored map would flip the sign of every left-right statistic; it does not change whether an asymmetry exists.

## A15. Glitch masking
Threshold: |Sij - Sji| > -30 dB of the pair's band-rms level (config.yaml qc.glitch_thr_db, commit 89d4f23, 2026-09-27, six days before the first lobe file, 7ccec7f 2026-10-03). Masked points per file:
| threshold | file | masked points | per port pair |
|---|---|---|---|
| mask -30 dB (frozen) | Healthy_sliced_new | 0 |  |
| mask -30 dB (frozen) | Mild_lobe | 0 |  |
| mask -30 dB (frozen) | Moderate_lobe | 0 |  |
| mask -30 dB (frozen) | Severe_lobe | 1 | 2-5: 1 |
| mask -30 dB (frozen) | Healthy_sliced | 1 | 1-4: 1 |
| mask -30 dB (frozen) | Mild_lobe_new | 1 | 3-6: 1 |
| mask -30 dB (frozen) | Moderate_lobe_c3 | 1 | 1-4: 1 |
| mask -30 dB (frozen) | Severe_lobe_c3 | 16 | 2-6: 13, 3-6: 3 |
| mask -30 dB (frozen) | LeftOnly_test_c3 | 1 | 2-5: 1 |
| mask -30 dB (frozen) | MCI_lobe_c3 | 0 |  |
| mask -36 dB (2x stricter) | Healthy_sliced_new | 0 |  |
| mask -36 dB (2x stricter) | Mild_lobe | 4 | 2-4: 4 |
| mask -36 dB (2x stricter) | Moderate_lobe | 1 | 2-5: 1 |
| mask -36 dB (2x stricter) | Severe_lobe | 1 | 2-5: 1 |
| mask -36 dB (2x stricter) | Healthy_sliced | 2 | 1-4: 2 |
| mask -36 dB (2x stricter) | Mild_lobe_new | 2 | 3-6: 2 |
| mask -36 dB (2x stricter) | Moderate_lobe_c3 | 3 | 1-4: 1, 2-5: 1, 3-6: 1 |
| mask -36 dB (2x stricter) | Severe_lobe_c3 | 35 | 2-6: 29, 3-6: 6 |
| mask -36 dB (2x stricter) | LeftOnly_test_c3 | 1 | 2-5: 1 |
| mask -36 dB (2x stricter) | MCI_lobe_c3 | 0 |  |

Headline numbers with masking off and with a 2x stricter threshold (-36 dB):
| ('design', '') | ('R21', 'mask -30 dB (frozen)') | ('R21', 'mask -36 dB (2x stricter)') | ('R21', 'mask off') | ('R31', 'mask -30 dB (frozen)') | ('R31', 'mask -36 dB (2x stricter)') | ('R31', 'mask off') | ('R32', 'mask -30 dB (frozen)') | ('R32', 'mask -36 dB (2x stricter)') | ('R32', 'mask off') |
|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | -20.507 | -20.507 | -20.507 | -14.609 | -14.607 | -14.571 | 5.898 | 5.900 | 5.936 |
| Healthy_sliced_new | -20.567 | -20.567 | -20.567 | -14.744 | -14.744 | -14.744 | 5.823 | 5.823 | 5.823 |
| LeftOnly phase cross-ratios >= 3x (R1c) | n/a | n/a | n/a | 4.000 | 4.000 | 4.000 | n/a | n/a | n/a |
| LeftOnly_test_c3 | -20.200 | -20.200 | -20.200 | -15.445 | -15.445 | -15.443 | 4.755 | 4.755 | 4.757 |
| MCI_lobe_c3 | -20.555 | -20.555 | -20.555 | -14.773 | -14.773 | -14.773 | 5.783 | 5.783 | 5.783 |
| Mild_lobe | -19.974 | -19.977 | -19.974 | -15.822 | -15.822 | -15.822 | 4.152 | 4.155 | 4.152 |
| Mild_lobe_new | -19.940 | -19.940 | -19.940 | -15.856 | -15.852 | -15.537 | 4.084 | 4.088 | 4.403 |
| Moderate_lobe | -19.451 | -19.451 | -19.451 | -16.008 | -16.009 | -16.008 | 3.443 | 3.442 | 3.443 |
| Moderate_lobe_c3 | -19.451 | -19.451 | -19.451 | -16.012 | -16.017 | -16.011 | 3.440 | 3.434 | 3.441 |
| Severe_lobe | -18.002 | -18.002 | -18.002 | -15.533 | -15.533 | -15.528 | 2.469 | 2.469 | 2.474 |
| Severe_lobe_c3 | -17.892 | -17.924 | -17.883 | -15.584 | -15.586 | -15.579 | 2.308 | 2.338 | 2.304 |

Largest change of any ratio, in units of its one-pass yardstick: mask off: Mild_lobe_new R31 2.36x; mask -36 dB (2x stricter): Severe_lobe_c3 R21 0.29x.

## A16. Disjoint sub-bands (no refitting; effect sizes against the sub-band's own one-pass yardstick)
| band | uniform: min Normal R31 - max AD R31 (dB) | R31 one-pass yardstick | uniform gap / yardstick | lobe_A: min(Normal - stage) R31 / yardstick | lobe_A: R21 monotone | lobe_A: R32 monotone | lobe_A: Mild-Severe R21 gap / yardstick | lobe_B: min(Normal - stage) R31 / yardstick | lobe_B: R21 monotone | lobe_B: R32 monotone | lobe_B: Mild-Severe R21 gap / yardstick | LeftOnly - Healthy_new R31 / yardstick | LeftOnly phase cross-ratios >= 3x (R1c) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.2-3.5 | 0.25 | 0.07 | 3.42 | 10.67 | False | True | 16.10 | 12.44 | False | True | 16.88 | 9.76 | 16 |
| 3.5-3.8 | 1.55 | 0.27 | 5.71 | 5.00 | True | True | 11.49 | 6.23 | True | True | 11.57 | 3.59 | 0 |
| 3.8-4.2 | -3.46 | 0.48 | -7.25 | 0.13 | False | False | 0.12 | 0.43 | False | False | -0.61 | 0.30 | 0 |

## A19. Noise model at 2x
Provenance: the noise profiles (per-entry 0.25 dB / 2 deg / -70 dB floor for 'typical') and the setup perturbation (1.5% amplitude, 10 deg per port, 1 MHz jitter) were chosen in Prompt 02 (89d4f23, 2026-09-27); the ±0.5 / ±2 dB and ±10 deg calibration errors were chosen in the Prompt 03 follow-ups (6eca5d7). None comes from a measured VNA/antenna dataset. Every claim is conditional on them. At 2x (per-entry 0.5 dB / 4 deg / -64 dB, setup 3% / 20 deg / 2 MHz, calibration ±1 dB or ±4 dB ±20 deg):
| design | 1x: typical, ±0.5 dB | 2x: noise, ±1 dB | 2x: noise, ±4 dB ±20° |
|---|---|---|---|
| Healthy_sliced | 1.000 | 1.000 | 1.000 |
| Healthy_sliced_new | 1.000 | 1.000 | 1.000 |
| LeftOnly phase cross-ratios >= 3x measured (R1c) | 2.000 | 0.000 | 0.000 |
| LeftOnly_test_c3 | 1.000 | 0.953 | 0.940 |
| MCI_lobe_c3 | 1.000 | 1.000 | 1.000 |
| Mild_lobe | 1.000 | 1.000 | 1.000 |
| Mild_lobe_new | 1.000 | 1.000 | 1.000 |
| Moderate_lobe | 1.000 | 1.000 | 1.000 |
| Moderate_lobe_c3 | 1.000 | 1.000 | 1.000 |
| Severe_lobe | 1.000 | 1.000 | 1.000 |
| Severe_lobe_c3 | 1.000 | 1.000 | 1.000 |

| condition | design | UNCERTAIN | INVALID |
|---|---|---|---|
| 2x: noise, ±1 dB | Healthy_sliced_new | 0.000 | 0.000 |
| 2x: noise, ±1 dB | Mild_lobe | 0.000 | 0.000 |
| 2x: noise, ±1 dB | Moderate_lobe | 0.000 | 0.000 |
| 2x: noise, ±1 dB | Severe_lobe | 0.000 | 0.000 |
| 2x: noise, ±1 dB | Healthy_sliced | 0.000 | 0.000 |
| 2x: noise, ±1 dB | Mild_lobe_new | 0.000 | 0.000 |
| 2x: noise, ±1 dB | Moderate_lobe_c3 | 0.000 | 0.000 |
| 2x: noise, ±1 dB | Severe_lobe_c3 | 0.000 | 0.000 |
| 2x: noise, ±1 dB | LeftOnly_test_c3 | 0.047 | 0.000 |
| 2x: noise, ±1 dB | MCI_lobe_c3 | 0.000 | 0.000 |
| 2x: noise, ±1 dB | LeftOnly phase cross-ratios >= 3x measured (R1c) | n/a | n/a |
| 2x: noise, ±4 dB ±20° | Healthy_sliced_new | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | Mild_lobe | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | Moderate_lobe | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | Severe_lobe | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | Healthy_sliced | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | Mild_lobe_new | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | Moderate_lobe_c3 | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | Severe_lobe_c3 | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | LeftOnly_test_c3 | 0.057 | 0.000 |
| 2x: noise, ±4 dB ±20° | MCI_lobe_c3 | 0.000 | 0.000 |
| 2x: noise, ±4 dB ±20° | LeftOnly phase cross-ratios >= 3x measured (R1c) | n/a | n/a |

## A20. Between-solve covariance (Prompt 04 model)
Sigma_b is estimated from the 4 v1/v2 repeat pairs (d/sqrt2), i.e. at most rank 4, shrunk toward median variances (Opgen-Rhein & Strimmer) and zero correlations (Schafer & Strimmer). Symmetric KL J with Sigma_b scaled x0.1 / x1 / x10:
| features | pair | 0.1 | 1.0 | 10.0 |
|---|---|---|---|---|
| C2 | MCI|Normal | 0.607 | 0.327 | 0.0586 |
| C2 | Mild|Severe | 9.04 | 5.35 | 1.06 |
| C2 | Normal|AD | 12.3 | 7.92 | 1.93 |
| C2 | Normal|Mild | 11.6 | 7.03 | 1.43 |
| C3 | MCI|Normal | 1.23 | 0.518 | 0.0767 |
| C3 | Mild|Severe | 0.26 | 0.119 | 0.0185 |
| C3 | Normal|AD | 39.8 | 18.6 | 2.93 |
| C3 | Normal|Mild | 35.4 | 16.6 | 2.62 |
| G_coup | MCI|Normal | 381 | 92.3 | 12.3 |
| G_coup | Mild|Severe | 641 | 143 | 20 |
| G_coup | Normal|AD | 2.42e+03 | 492 | 62.7 |
| G_coup | Normal|Mild | 2.45e+03 | 501 | 61.3 |
| G_ratio | MCI|Normal | 3.88 | 0.747 | 0.0827 |
| G_ratio | Mild|Severe | 485 | 85.5 | 9.29 |
| G_ratio | Normal|AD | 1.65e+03 | 399 | 50 |
| G_ratio | Normal|Mild | 2.09e+03 | 414 | 46.1 |
| R31 | MCI|Normal | 0.466 | 0.0609 | 0.00629 |
| R31 | Mild|Severe | 24 | 3.36 | 0.35 |
| R31 | Normal|AD | 435 | 72.4 | 10.1 |
| R31 | Normal|Mild | 791 | 108 | 11.2 |

## A21. Leave-one-solve-out, every fold (training: uniform v1/v2 solves; held-out solve's 120 noisy draws)
| rule | held out | class | training solves | Normal solves in training | boundary dB | fraction correct | UNCERTAIN |
|---|---|---|---|---|---|---|---|
| detection (R31) | brain_sevem_layer_Healthy.s6p | Normal | 7 | 1.000 | -15.273 | 1.000 | 0.000 |
| detection (R31) | new_Healthy.s6p | Normal | 7 | 1.000 | -15.165 | 1.000 | 0.000 |
| detection (R31) | Brain_sevem_layer_MildAD.s6p | Mild | 7 | 2.000 | -15.273 | 1.000 | 0.000 |
| detection (R31) | new_MildAD.s6p | Mild | 7 | 2.000 | -15.273 | 1.000 | 0.000 |
| detection (R31) | Brain_sevem_layer_ModerateAD.s6p | Moderate | 7 | 2.000 | -15.273 | 1.000 | 0.000 |
| detection (R31) | new_ModerateAD.s6p | Moderate | 7 | 2.000 | -15.273 | 1.000 | 0.000 |
| detection (R31) | brain_sevem_layer_SevereAD.s6p | Severe | 7 | 2.000 | -15.281 | 1.000 | 0.000 |
| detection (R31) | new_SevereAD.s6p | Severe | 7 | 2.000 | -15.273 | 1.000 | 0.000 |
| three | brain_sevem_layer_Healthy.s6p | Normal | 5 | n/a | -20.06, -18.75 | 1.000 | n/a |
| three | new_Healthy.s6p | Normal | 5 | n/a | -19.89, -18.75 | 1.000 | n/a |
| three | Brain_sevem_layer_MildAD.s6p | Mild | 5 | n/a | -20.02, -18.80 | 1.000 | n/a |
| three | new_MildAD.s6p | Mild | 5 | n/a | -19.93, -18.71 | 1.000 | n/a |
| three | brain_sevem_layer_SevereAD.s6p | Severe | 5 | n/a | -19.98, -18.73 | 1.000 | n/a |
| three | new_SevereAD.s6p | Severe | 5 | n/a | -19.98, -18.78 | 1.000 | n/a |
| three_merged | brain_sevem_layer_Healthy.s6p | Normal | 7 | n/a | 4.67, 2.77 | 1.000 | n/a |
| three_merged | new_Healthy.s6p | Normal | 7 | n/a | 4.60, 2.77 | 1.000 | n/a |
| three_merged | Brain_sevem_layer_MildAD.s6p | Mild | 7 | n/a | 4.66, 2.80 | 1.000 | n/a |
| three_merged | new_MildAD.s6p | Mild | 7 | n/a | 4.61, 2.75 | 1.000 | n/a |
| three_merged | Brain_sevem_layer_ModerateAD.s6p | Moderate | 7 | n/a | 4.64, 2.78 | 1.000 | n/a |
| three_merged | new_ModerateAD.s6p | Moderate | 7 | n/a | 4.62, 2.76 | 1.000 | n/a |
| three_merged | brain_sevem_layer_SevereAD.s6p | Severe | 7 | n/a | 4.64, 2.75 | 1.000 | n/a |
| three_merged | new_SevereAD.s6p | Severe | 7 | n/a | 4.64, 2.80 | 1.000 | n/a |

## A22. Separability metrics (univariate; class = mean of solve means; variance = within-solve noise + between-solve variance from the repeat pairs + stage scatter of merged classes; 95% bootstrap over solves)
Fisher = dmu^2/(v1+v2); Bhattacharyya = dmu^2/(4(v1+v2)) + 0.5 ln((v1+v2)/(2 sqrt(v1 v2))); symmetric KL = 0.5(v1/v2 + v2/v1 - 2) + 0.5 dmu^2 (1/v1 + 1/v2).
| pair | feature | Fisher | Fisher 2.5% | Fisher 97.5% | Bhattacharyya | Bhattacharyya 2.5% | Bhattacharyya 97.5% | sym. KL | sym. KL 2.5% | sym. KL 97.5% |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal|AD | R31 | 27.8 | 18 | 54.7 | 7.02 | 4.62 | 13.7 | 72 | 59.6 | 110 |
| Normal|AD | R21 | 4.44 | 2.98 | 19.2 | 1.51 | 1.17 | 4.81 | 51.1 | 29.2 | 77.8 |
| Normal|AD | R32 | 33.6 | 26.2 | 193 | 8.75 | 6.93 | 48.4 | 274 | 252 | 388 |
| Normal|AD | k1_band | 0.452 | 0.00154 | 1.97 | 0.132 | 0.0163 | 0.5 | 1.13 | 0.134 | 4.32 |
| Normal|AD | k2_band | 4.5 | 2.64 | 8.29 | 1.24 | 0.844 | 2.1 | 15.4 | 10.4 | 22.2 |
| Normal|AD | k3_band | 14.9 | 9.57 | 18.7 | 3.73 | 2.42 | 4.69 | 29.9 | 20.6 | 37.5 |
| Normal|AD | logN | 0.155 | 0.00422 | 0.516 | 0.0387 | 0.00112 | 0.131 | 0.31 | 0.00894 | 1.05 |
| Normal|Mild | R31 | 53.8 | 42.9 | 66 | 13.5 | 10.7 | 16.5 | 108 | 85.8 | 132 |
| Normal|Mild | R21 | 24.5 | 15.1 | 36.1 | 6.12 | 3.78 | 9.01 | 48.9 | 30.2 | 72.1 |
| Normal|Mild | R32 | 200 | 169 | 233 | 49.9 | 42.3 | 58.2 | 400 | 339 | 465 |
| Normal|Mild | k1_band | 0.21 | 0.00176 | 2.55 | 0.0525 | 0.00044 | 0.638 | 0.42 | 0.00352 | 5.11 |
| Normal|Mild | k2_band | 7.72 | 5.6 | 10.2 | 1.93 | 1.4 | 2.54 | 15.4 | 11.2 | 20.4 |
| Normal|Mild | k3_band | 13.6 | 8.17 | 20.5 | 3.41 | 2.04 | 5.12 | 27.3 | 16.3 | 41 |
| Normal|Mild | logN | 0.07 | 0.00371 | 0.348 | 0.0175 | 0.000928 | 0.0871 | 0.14 | 0.00742 | 0.696 |
| Mild|Severe | R31 | 1.66 | 0.947 | 2.57 | 0.415 | 0.237 | 0.642 | 3.32 | 1.89 | 5.14 |
| Mild|Severe | R21 | 29.9 | 23.9 | 36.6 | 7.48 | 5.97 | 9.16 | 59.8 | 47.7 | 73.3 |
| Mild|Severe | R32 | 27.8 | 17.7 | 40.1 | 6.94 | 4.43 | 10 | 55.5 | 35.4 | 80.1 |
| Mild|Severe | k1_band | 1.39 | 0.0867 | 4.25 | 0.347 | 0.0217 | 1.06 | 2.78 | 0.173 | 8.5 |
| Mild|Severe | k2_band | 5.38 | 2.36 | 9.65 | 1.35 | 0.589 | 2.41 | 10.8 | 4.71 | 19.3 |
| Mild|Severe | k3_band | 0.116 | 0.0217 | 1.31 | 0.0289 | 0.00542 | 0.327 | 0.232 | 0.0434 | 2.61 |
| Mild|Severe | logN | 0.0614 | 0.00333 | 0.65 | 0.0153 | 0.000833 | 0.162 | 0.123 | 0.00666 | 1.3 |
| Mild|Moderate | R31 | 1.02 | 0.0105 | 4.51 | 0.255 | 0.00262 | 1.13 | 2.04 | 0.021 | 9.02 |
| Mild|Moderate | R21 | 1.19 | 0.0464 | 3.87 | 0.298 | 0.0116 | 0.967 | 2.38 | 0.0928 | 7.74 |
| Mild|Moderate | R32 | 0.049 | 0.00076 | 1.58 | 0.0123 | 0.00019 | 0.395 | 0.098 | 0.00152 | 3.16 |
| Mild|Moderate | k1_band | 0.0376 | 0.00899 | 1.4 | 0.0094 | 0.00225 | 0.351 | 0.0752 | 0.018 | 2.81 |
| Mild|Moderate | k2_band | 0.281 | 0.0194 | 2.64 | 0.0703 | 0.00485 | 0.66 | 0.562 | 0.0388 | 5.28 |
| Mild|Moderate | k3_band | 0.0987 | 0.0974 | 2.57 | 0.0247 | 0.0244 | 0.642 | 0.197 | 0.195 | 5.14 |
| Mild|Moderate | logN | 0.0211 | 0.000191 | 0.468 | 0.00528 | 4.79e-05 | 0.117 | 0.0422 | 0.000383 | 0.937 |

Ranking agreement:
| pair | rho(Fisher, Bhattacharyya) | rho(Fisher, sym. KL) | top feature (Fisher / B / KL) |
|---|---|---|---|
| Normal|AD | 0.96 | 0.89 | R32 / R32 / R32 |
| Normal|Mild | 1.00 | 1.00 | R32 / R32 / R32 |
| Mild|Severe | 1.00 | 1.00 | R21 / R21 / R21 |
| Mild|Moderate | 1.00 | 1.00 | R21 / R21 / R21 |

## A23. Why R31 turns back at Severe
R31 = C3 - C1 (dB). Components against the healthy head of the same set:
| set | design | C1 neighbour | C3 opposite | R31 | dC1 vs healthy | dC3 vs healthy |
|---|---|---|---|---|---|---|
| lobe_A | Healthy_sliced_new | -36.837 | -51.581 | -14.744 | 0.000 | 0.000 |
| lobe_A | Mild_lobe | -36.799 | -52.615 | -15.822 | 0.038 | -1.033 |
| lobe_A | Moderate_lobe | -37.042 | -53.051 | -16.008 | -0.205 | -1.470 |
| lobe_A | Severe_lobe | -37.681 | -53.216 | -15.533 | -0.844 | -1.634 |
| lobe_B | Healthy_sliced | -36.849 | -51.458 | -14.609 | 0.000 | 0.000 |
| lobe_B | Mild_lobe_new | -36.799 | -52.645 | -15.856 | 0.050 | -1.187 |
| lobe_B | Moderate_lobe_c3 | -37.051 | -53.063 | -16.012 | -0.202 | -1.605 |
| lobe_B | Severe_lobe_c3 | -37.681 | -53.266 | -15.584 | -0.832 | -1.808 |
| uniform | brain_sevem_layer_Healthy.s6p | -37.344 | -51.817 | -14.479 | n/a | n/a |
| uniform | new_Healthy.s6p | -36.990 | -51.658 | -14.674 | n/a | n/a |
| uniform | new_MCI.s6p | -36.813 | -51.426 | -14.614 | n/a | n/a |
| uniform | Brain_sevem_layer_MildAD.s6p | -37.573 | -53.754 | -16.195 | n/a | n/a |
| uniform | new_MildAD.s6p | -37.083 | -53.141 | -16.058 | n/a | n/a |
| uniform | Brain_sevem_layer_ModerateAD.s6p | -37.403 | -53.908 | -16.505 | n/a | n/a |
| uniform | new_ModerateAD.s6p | -37.130 | -53.298 | -16.168 | n/a | n/a |
| uniform | brain_sevem_layer_SevereAD.s6p | -37.869 | -53.682 | -15.850 | n/a | n/a |
| uniform | new_SevereAD.s6p | -37.688 | -53.540 | -15.851 | n/a | n/a |

From Moderate to Severe the opposite path C3 barely moves while the neighbour path C1 drops (CSF gaps of 15.5-18 mm under every antenna reach the neighbour paths, which are flat below ~10 mm; round-1 dose-response, review/A6_neighbour_dose_response.csv). Severe would reach the edge of the AD zone (tau - m) after a further R31 rise of Severe_lobe +0.18 dB, Severe_lobe_c3 +0.23 dB, i.e. a further C1 drop of that size with C3 fixed. With the measured neighbour slope beyond 10 mm that corresponds to roughly one more Moderate-to-Severe step of atrophy. This is an extrapolation, not a measurement.

## A24. R21 on one axis
Figure `figures/A24_R21_axis.png`.
| set | design | stage | R21 |
|---|---|---|---|
| uniform v1 | brain_sevem_layer_Healthy.s6p | Normal | -20.395 |
| uniform v2 | new_Healthy.s6p | Normal | -20.722 |
| uniform v2 | new_MCI.s6p | MCI | -20.685 |
| uniform v1 | Brain_sevem_layer_MildAD.s6p | Mild | -19.308 |
| uniform v2 | new_MildAD.s6p | Mild | -19.479 |
| uniform v1 | Brain_sevem_layer_ModerateAD.s6p | Moderate | -19.768 |
| uniform v2 | new_ModerateAD.s6p | Moderate | -19.526 |
| uniform v1 | brain_sevem_layer_SevereAD.s6p | Severe | -18.164 |
| uniform v2 | new_SevereAD.s6p | Severe | -18.058 |
| lobe_v1 | Healthy_sliced | Normal | -20.507 |
| lobe_v1 | Mild_lobe | Mild | -19.974 |
| lobe_v1 | Moderate_lobe | Moderate | -19.451 |
| lobe_v1 | Severe_lobe | Severe | -18.002 |
| lobe_A | Healthy_sliced_new | Normal | -20.567 |
| lobe_A | Mild_lobe | Mild | -19.974 |
| lobe_A | Moderate_lobe | Moderate | -19.451 |
| lobe_A | Severe_lobe | Severe | -18.002 |
| lobe_B | Healthy_sliced | Normal | -20.507 |
| lobe_B | Mild_lobe_new | Mild | -19.940 |
| lobe_B | Moderate_lobe_c3 | Moderate | -19.451 |
| lobe_B | Severe_lobe_c3 | Severe | -17.892 |
| tests | LeftOnly_test_c3 | LeftOnly | -20.200 |
| tests | MCI_lobe_c3 | MCI | -20.555 |

Stage pairs against the sum of their yardsticks (lobe: one-pass change per stage; uniform: v1-v2 sweep difference):
| set | pair | R21 gap dB | sum of the two yardsticks | gap / sum | yardstick used |
|---|---|---|---|---|---|
| uniform v1 | Normal|Mild | 1.086 | 0.498 | 2.183 | v1-v2 sweep difference |
| uniform v1 | Mild|Moderate | -0.460 | 0.413 | 1.113 | v1-v2 sweep difference |
| uniform v1 | Moderate|Severe | 1.604 | 0.348 | 4.603 | v1-v2 sweep difference |
| uniform v1 | Mild|Severe | 1.144 | 0.277 | 4.133 | v1-v2 sweep difference |
| uniform v2 | Normal|Mild | 1.243 | 0.498 | 2.497 | v1-v2 sweep difference |
| uniform v2 | Mild|Moderate | -0.047 | 0.413 | 0.113 | v1-v2 sweep difference |
| uniform v2 | Moderate|Severe | 1.467 | 0.348 | 4.212 | v1-v2 sweep difference |
| uniform v2 | Mild|Severe | 1.421 | 0.277 | 5.133 | v1-v2 sweep difference |
| lobe_v1 | Normal|Mild | 0.533 | 0.094 | 5.684 | one-pass change |
| lobe_v1 | Mild|Moderate | 0.523 | 0.034 | 15.446 | one-pass change |
| lobe_v1 | Moderate|Severe | 1.449 | 0.110 | 13.183 | one-pass change |
| lobe_v1 | Mild|Severe | 1.972 | 0.143 | 13.751 | one-pass change |
| lobe_A | Normal|Mild | 0.593 | 0.094 | 6.325 | one-pass change |
| lobe_A | Mild|Moderate | 0.523 | 0.034 | 15.446 | one-pass change |
| lobe_A | Moderate|Severe | 1.449 | 0.110 | 13.183 | one-pass change |
| lobe_A | Mild|Severe | 1.972 | 0.143 | 13.751 | one-pass change |
| lobe_B | Normal|Mild | 0.566 | 0.094 | 6.043 | one-pass change |
| lobe_B | Mild|Moderate | 0.489 | 0.034 | 14.446 | one-pass change |
| lobe_B | Moderate|Severe | 1.559 | 0.110 | 14.183 | one-pass change |
| lobe_B | Mild|Severe | 2.048 | 0.143 | 14.281 | one-pass change |

The frozen boundaries were fitted on the uniform solves on 2026-10-02 (2baddee/5192287), before the lobe files existed (2026-10-03); they were not placed after seeing the lobe designs. They were placed after seeing the uniform designs, which are their training data.

## A26. 'Absorbed' power (power not returned to any port)
N_t = 1 - sum_u |S_ut|^2 (driven port t; ring and band mean; it includes radiation to the HFSS boundary and antenna loss, not head absorption alone):
| solve | class | N (not returned) dB | 1 - reflection dB | coupled power returned to other ports |
|---|---|---|---|---|
| brain_sevem_layer_Healthy.s6p | Normal | -2.553 | -2.55 | 0.0003768 |
| new_Healthy.s6p | Normal | -2.499 | -2.496 | 0.0004082 |
| new_MCI.s6p | MCI | -2.503 | -2.5 | 0.0004253 |
| Brain_sevem_layer_MildAD.s6p | Mild | -2.521 | -2.518 | 0.0003564 |
| new_MildAD.s6p | Mild | -2.475 | -2.472 | 0.0003988 |
| Brain_sevem_layer_ModerateAD.s6p | Moderate | -2.515 | -2.512 | 0.0003698 |
| new_ModerateAD.s6p | Moderate | -2.426 | -2.423 | 0.0003944 |
| brain_sevem_layer_SevereAD.s6p | Severe | -2.511 | -2.508 | 0.0003344 |
| new_SevereAD.s6p | Severe | -2.407 | -2.404 | 0.0003486 |

AD - Normal gap +0.050 dB against the solve-to-solve SD 0.054 dB (repeat pairs): 0.92x (bootstrap 95% 0.07-2.12x). The coupled power is ~3.8e-04 of the incident power, so N = 1 - reflection to within that; the weak (opposite, second-neighbour) entries cannot move N. The '0.89x' figure was not found anywhere in the repository.

## C. Phase finding (post hoc: found after unblinding with a statistic built after unblinding)
**C2. Convergence per combination and frequency** (figure `figures/C2_phase_ratio_heatmap.png`):
| combination | median one-pass yardstick (deg) | median |LeftOnly| (deg) | frequencies >= 3x max(yard, null max) | of which in 3.30-3.65 GHz | median yardstick 3.30-3.65 (deg) | median |LO| 3.30-3.65 (deg) |
|---|---|---|---|---|---|---|
| T1T2·T3T4 / T1T3·T2T4 | 2.21 | 10.30 | 63 | 43 | 3.24 | 14.65 |
| T1T2·T3T4 / T1T4·T2T3 | 1.36 | 0.64 | 0 | 0 | 1.07 | 0.64 |
| T1T3·T2T4 / T1T4·T2T3 | 1.95 | 9.19 | 68 | 48 | 3.16 | 14.13 |
| T1T2·T3T5 / T1T3·T2T5 | 1.32 | 3.56 | 38 | 20 | 1.89 | 6.17 |
| T1T2·T3T5 / T1T5·T2T3 | 1.47 | 3.76 | 23 | 18 | 1.08 | 7.20 |
| T1T3·T2T5 / T1T5·T2T3 | 2.13 | 7.26 | 41 | 32 | 2.50 | 13.29 |
| T1T2·T3T6 / T1T3·T2T6 | 1.32 | 3.56 | 38 | 20 | 1.89 | 6.17 |
| T1T2·T3T6 / T1T6·T2T3 | 1.45 | 1.53 | 0 | 0 | 2.09 | 1.22 |
| T1T2·T4T5 / T1T4·T2T5 | 0.89 | 1.85 | 0 | 0 | 1.23 | 1.97 |
| T1T2·T4T5 / T1T5·T2T4 | 1.94 | 1.90 | 0 | 0 | 2.20 | 1.26 |
| T1T2·T4T6 / T1T4·T2T6 | 1.53 | 4.94 | 37 | 17 | 2.85 | 7.34 |
| T1T2·T4T6 / T1T6·T2T4 | 3.05 | 9.88 | 37 | 17 | 5.69 | 14.68 |
| T1T2·T5T6 / T1T5·T2T6 | 1.47 | 3.76 | 23 | 18 | 1.08 | 7.20 |
| T1T3·T4T5 / T1T4·T3T5 | 1.63 | 4.50 | 43 | 23 | 1.79 | 7.92 |
| T1T3·T4T5 / T1T5·T3T4 | 3.26 | 9.00 | 43 | 23 | 3.58 | 15.85 |
| T1T3·T4T6 / T1T4·T3T6 | 1.56 | 1.56 | 0 | 0 | 1.78 | 1.93 |
| T2T3·T4T5 / T2T4·T3T5 | 1.82 | 5.25 | 46 | 26 | 2.43 | 6.83 |
| T2T3·T4T5 / T2T5·T3T4 | 1.92 | 1.76 | 0 | 0 | 1.94 | 1.78 |
| T2T4·T3T5 / T2T5·T3T4 | 1.36 | 5.50 | 54 | 34 | 1.82 | 8.35 |
| T2T3·T4T6 / T2T4·T3T6 | 2.65 | 10.63 | 50 | 30 | 4.52 | 14.97 |
| T2T3·T4T6 / T2T6·T3T4 | 1.82 | 5.25 | 46 | 26 | 2.43 | 6.83 |
| T2T4·T3T6 / T2T6·T3T4 | 1.36 | 5.50 | 54 | 34 | 1.82 | 8.35 |

**C3. The identical statistic on every file** (each file judged against the other eight; 22 correlated combinations):
| file | >= 3x (round-1 rule: max(null rms, yard)) | >= 3x (R1c: max(null max, yard)) |
|---|---|---|
| Healthy_sliced | 0 | 0 |
| Healthy_sliced_new | 0 | 0 |
| Mild_lobe | 0 | 0 |
| Mild_lobe_new | 0 | 0 |
| Moderate_lobe | 0 | 0 |
| Moderate_lobe_c3 | 0 | 0 |
| Severe_lobe | 0 | 0 |
| Severe_lobe_c3 | 0 | 0 |
| MCI_lobe_c3 | 0 | 0 |
| LeftOnly_test_c3 | 16 | 4 |

## Summary (statistics part)
| item | verdict | old -> new | evidence |
|---|---|---|---|
| R1 floor dispute | CHANGED (main label) | imaging LR 3.7x (null rms) -> 1.94x under the max-floor rule (not separable (< 2x)); Shapiro-Wilk p = 0.055 (0.46 without Moderate_lobe); rank p 0.10; Moderate's T driven by T2-T3, T5-T6 | review2/R1a_imaging_null.csv, R1b_*.csv, R1c_*.csv |
| R2 16/22 vs b9_anti | CHANGED (one answer) | 16/22 (rms ruler) vs 0.9x (max floor, one pair) -> same max-floor rule: cross-ratio phase 4/22 >= 3x at band mean, 9/22 at 3.30-3.65 GHz; pair phase 0/8 (band), 3/8 (3.4 GHz); separable (per-antenna) share of the reference-free LR phase asymmetry: null median 0.33, LeftOnly 0.09 | review2/R2_*.csv |
| R3 detuning | CHANGED (tested; first-order detuning does not explain the asymmetry) | untested -> left-right resonance shift +1.91 MHz (symmetric designs <= 2.86); separable share of the LR transmission phase asymmetry 0.11 (3.30-3.65 GHz, matched reference); corr(per-antenna term, reflection change) -0.51 | review2/R3_*.csv |
| R4 detection feature | CONFIRMED (defensible on training data; fragile) | not compared -> lobe designs with >= 3x margin: R31 7/10, R21 alone 7/10, (R31, R21) pair 9/10; R21 alone puts LeftOnly Normal and lobe-Mild near its threshold | review2/R4_feature_choice.csv |
| R6 robust detection | CHANGED | 3.3-4.9x with max(yard, bSD) -> quadrature with ±0.5 dB measurement spread: Healthy_sliced_new 3.04x, Mild_lobe 3.18x, Moderate_lobe 4.44x, Severe_lobe 1.23x, Healthy_sliced 3.96x, Mild_lobe_new 3.42x, Moderate_lobe_c3 4.46x, Severe_lobe_c3 1.58x | review2/R6_A28_rulers.csv |
| A28 tau and boundary intervals | CHANGED (count) | -> tau 95% -15.368 to -15.165 dB; 3 of 30 lobe labels change inside a boundary's bootstrap distribution | review2/R6_A28_rulers.csv |
| A14 port map | CONFIRMED (by geometry, not by the search) | symmetry search -> the search is mirror-blind (scores 0.149969 = 0.149969); audit excitation order + port-sheet azimuths + field centroids fix it | review2/A14_symmetry_search.csv; data/hfss_geometry_audit_Healthy_sliced.txt |
| A15 masking | CHANGED (one dependency found) | mask off: largest move Mild_lobe_new R31 = 2.36x yardstick; mask -36 dB (2x stricter): largest move Severe_lobe_c3 R21 = 0.29x yardstick; threshold fixed 2026-09-27, before the lobe files | review2/A15_*.csv |
| A16 sub-bands | CHANGED (frequency dependence stated) | 3.2-4.2 only -> 3.2-3.5: uniform gap 3.4x, lobe_A min 10.7x, lobe_B min 12.4x, phase CR 16/22; 3.5-3.8: uniform gap 5.7x, lobe_A min 5.0x, lobe_B min 6.2x, phase CR 0/22; 3.8-4.2: uniform gap -7.3x, lobe_A min 0.1x, lobe_B min 0.4x, phase CR 0/22 | review2/A16_subbands.csv |
| A19 noise model | CHANGED (conditional claims stated) | unstated -> chosen, not measured; at 2x noise and ±4 dB/±20°: detection fraction expected Healthy_sliced_new 1.00, Mild_lobe 1.00, Moderate_lobe 1.00, Severe_lobe 1.00, Healthy_sliced 1.00, Mild_lobe_new 1.00, Moderate_lobe_c3 1.00, Severe_lobe_c3 1.00, LeftOnly_test_c3 0.94, MCI_lobe_c3 1.00 | review2/A19_noise_2x.csv |
| A20 between-solve covariance | CHANGED (sensitivity stated) | single shrunk estimate from 4 pairs -> J changes by a factor 6.3-74 between x0.1 and x10; Normal|AD for R31: x0.1: 435, x1.0: 72, x10.0: 10 | review2/A20_between_cov.csv |
| A21 LOSO per fold | CONFIRMED | averages -> 0 of 22 folds below 0.95:  | review2/A21_loso_folds.csv |
| A22 separability | CHANGED (intervals added) | point values -> Normal|AD: top R32 / R32 / R32, rho 0.89; Normal|Mild: top R32 / R32 / R32, rho 1.00; Mild|Severe: top R21 / R21 / R21, rho 1.00; Mild|Moderate: top R21 / R21 / R21, rho 1.00 | review2/A22_separability.csv |
| A23 R31 non-monotonic | CHANGED (mechanism measured; claim narrowed) | 'detection' -> robust detection is Mild/Moderate in the lobe set (Severe 1.4-1.7x); mechanism: C1 drop at Severe (lobe_A -0.84 dB) with C3 nearly flat; crossing needs a further 0.18-0.23 dB | review2/A23_R31_components.csv |
| A24 R21 staging | CHANGED (pairs inside yardsticks listed) | 1 stage pairs separated by less than the sum of their yardsticks: uniform v2 Mild|Moderate | review2/A24_*.csv, figures/A24_R21_axis.png |
| A26 absorbed power | CHANGED (re-derived; 0.89x not found) | '0.89x' -> 0.92x (95% 0.07-2.12x); N = 1 - reflection within ~1e-3, so weak-entry convergence cannot be the cause; N's solve-to-solve SD (0.054 dB) is the reflection's | review2/A26_absorbed.csv |
| C2 phase convergence | CHANGED (per frequency) | band-mean yardstick -> per frequency: median one-pass yardstick 1.60 deg vs median |LO| 4.72 deg; cells >= 3x: 704 of 4422 | review2/C2_phase_convergence.csv, figures/C2_phase_ratio_heatmap.png |
| C3 null distribution | CHANGED (count recomputed per file) | 16/22 -> LeftOnly 16/22 (round-1 rule) and 4/22 (R1c); symmetric files max 0 and 0 | review2/C3_null_counts.csv |
