# POST HOC: rotated healthy nulls, Test_B truth, pass gap (code 29fef32-dirty)

Everything below was computed after the Test_B truth and the rotated nulls arrived. Frozen rules, thresholds, protocols, predictions, submitted estimates and committed verdicts are unchanged and stand as scored.

## QC of the new files (raw, before masking)
| design | points | band GHz | max singular value^2 | worst ||Sij|-|Sji|| (dB) | at | worst |Sij-Sji|/|Sij| (dB) | masked points (-30 dB rule) | masked at |
|---|---|---|---|---|---|---|---|---|
| Null_rot07 | 201 | 3.20-4.20 | 0.906 | 0.492 | 3.860 GHz, ports 1-4 | -21.402 | 2 | 3.860 GHz ports 1-4; 3.565 GHz ports 3-4 |
| Null_rot19 | 201 | 3.20-4.20 | 0.909 | 0.143 | 3.870 GHz, ports 1-4 | -27.203 | 1 | 3.870 GHz ports 1-4 |
| RightOnly_test | 201 | 3.20-4.20 | 0.906 | 0.259 | 3.850 GHz, ports 4-6 | -29.373 | 0 |  |
| Test_B | 201 | 3.20-4.20 | 0.905 | 0.386 | 3.545 GHz, ports 2-5 | -26.162 | 3 | 3.840 GHz ports 4-6; 3.845 GHz ports 4-6; 3.850 GHz ports 4-6 |

## V. The user's quoted numbers, re-derived
| quantity | Null_rot07 | Null_rot19 | max |.| over the 9 symmetric | LeftOnly_test_c3 | Test_B | Healthy_sliced_new (alone) | values T1..T6 | range max-min | rms about the ring mean (= contrast r0) |
|---|---|---|---|---|---|---|---|---|---|
| power pair T1-T3 vs T1-T5 (band mean, dB) | 0.156 | -0.444 | 0.495 | 0.108 | -0.372 | n/a | n/a | n/a | n/a |
| power pair T2-T4 vs T4-T6 (band mean, dB) | 0.270 | 0.743 | 0.301 | -0.193 | 0.535 | n/a | n/a | n/a | n/a |
| power pair T2 refl. vs T6 refl. (band mean, dB) | -0.011 | -0.005 | 0.017 | -0.060 | -0.066 | n/a | n/a | n/a | n/a |
| power pair T3 refl. vs T5 refl. (band mean, dB) | -0.004 | 0.012 | 0.014 | -0.068 | 0.068 | n/a | n/a | n/a | n/a |
| phase pair T1-T2 vs T1-T6 at 3.4 GHz (deg) | 1.666 | 0.976 | 1.363 | -2.897 | -2.558 | 0.715 | n/a | n/a | n/a |
| phase pair T2-T5 vs T3-T6 at 3.4 GHz (deg) | 1.778 | 1.713 | 1.017 | -0.377 | 1.013 | 0.040 | n/a | n/a | n/a |
| per-antenna neighbour phase vs Healthy_sliced_new: Null_rot07 (deg) | n/a | n/a | n/a | n/a | n/a | n/a | -0.56, -0.23, -0.42, +0.31, +0.50, -0.57 | 1.066 | 0.419 |
| per-antenna neighbour phase vs Healthy_sliced_new: Null_rot19 (deg) | n/a | n/a | n/a | n/a | n/a | n/a | -0.25, -0.04, -0.74, -0.41, +0.08, -0.45 | 0.819 | 0.272 |
| per-antenna neighbour phase vs Healthy_sliced_new: Test_B (deg) | n/a | n/a | n/a | n/a | n/a | n/a | -3.34, -5.07, -3.85, -3.08, -4.46, -3.49 | 1.990 | 0.689 |

Test_B T2 / T5 delay beyond the mean of the other four antennas: T2 1.63 deg, T5 1.02 deg; range max-min 1.99 deg.

## A. 0.3(a) Pass gap: LeftOnly minus mirrored RightOnly against the three pass-5 vs pass-6 twins
RightOnly stopped at pass 5 (dS 0.0197, 789k elements), LeftOnly at pass 6 (dS 0.0147, 941k). The twins are the same design refined by one pass (same initial mesh); LeftOnly and RightOnly are independent meshes with a pass gap, so the twin differences are a lower bound on what a pass gap plus a re-mesh can do.
| summary | count |
|---|---|
| 26 informative: within the largest pass-5/6 twin difference | 7/26 |
| the 14 that failed the C6 tolerance: within the largest twin difference | 0/14 |
| all 88 antisymmetric statistics: within the largest twin difference | 27/88 |
| R31 / R21 / R32: within the largest twin difference | R31 0.013 vs 0.051, R21 0.133 vs 0.110, R32 0.146 vs 0.161 |

26 informative statistics:
| statistic | frequencies | |T(LO) + T(RO)| | twin Mild 5->6 | twin Moderate 5->6 | twin Severe 5->6 | max twin | ratio to max twin | within max twin | C6 tolerance (9-null ruler) | within C6 tolerance |
|---|---|---|---|---|---|---|---|---|---|---|
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | 1.381 | 0.509 | 1.498 | 0.144 | 1.498 | 0.922 | True | 2.931 | True |
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | 3.30-3.65 GHz | 0.902 | 1.782 | 1.584 | 1.326 | 1.782 | 0.506 | True | 4.148 | True |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | 2.326 | 0.157 | 1.464 | 0.234 | 1.464 | 1.589 | False | 2.510 | True |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | 3.30-3.65 GHz | 0.182 | 1.702 | 1.207 | 0.987 | 1.702 | 0.107 | True | 3.737 | True |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | 2.202 | 1.511 | 0.855 | 0.968 | 1.511 | 1.457 | False | 2.051 | False |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | 3.30-3.65 GHz | 3.788 | 0.315 | 0.107 | 1.104 | 1.104 | 3.432 | False | 3.438 | False |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | 4.687 | 1.099 | 1.268 | 1.765 | 1.765 | 2.655 | False | 3.884 | False |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | 3.30-3.65 GHz | 5.568 | 1.478 | 1.066 | 0.768 | 1.478 | 3.766 | False | 6.189 | True |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | 2.202 | 1.511 | 0.855 | 0.968 | 1.511 | 1.457 | False | 2.051 | False |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | 3.30-3.65 GHz | 3.970 | 1.387 | 1.100 | 2.091 | 2.091 | 1.899 | False | 3.291 | False |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | 3.30-3.65 GHz | 7.941 | 2.773 | 2.200 | 4.181 | 4.181 | 1.899 | False | 6.581 | False |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | 3.30-3.65 GHz | 3.788 | 0.315 | 0.107 | 1.104 | 1.104 | 3.432 | False | 3.438 | False |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | 1.541 | 0.060 | 0.447 | 0.886 | 0.886 | 1.739 | False | 2.179 | True |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | 3.30-3.65 GHz | 3.069 | 0.395 | 0.484 | 0.765 | 0.765 | 4.013 | False | 2.446 | False |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | 3.081 | 0.120 | 0.894 | 1.772 | 1.772 | 1.739 | False | 4.358 | True |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | 3.30-3.65 GHz | 6.137 | 0.790 | 0.968 | 1.529 | 1.529 | 4.013 | False | 4.892 | False |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | 0.785 | 0.217 | 1.017 | 1.120 | 1.120 | 0.701 | True | 1.281 | True |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | 3.30-3.65 GHz | 3.251 | 1.307 | 0.723 | 1.751 | 1.751 | 1.856 | False | 1.751 | False |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | 3.30-3.65 GHz | 2.681 | 0.618 | 0.625 | 0.990 | 0.990 | 2.708 | False | 2.159 | False |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | 0.036 | 0.785 | 1.660 | 2.233 | 2.233 | 0.016 | True | 4.351 | True |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | 3.30-3.65 GHz | 5.932 | 1.925 | 1.347 | 2.742 | 2.742 | 2.164 | False | 3.671 | False |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | 0.785 | 0.217 | 1.017 | 1.120 | 1.120 | 0.701 | True | 1.281 | True |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | 3.30-3.65 GHz | 3.251 | 1.307 | 0.723 | 1.751 | 1.751 | 1.856 | False | 1.751 | False |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | 3.30-3.65 GHz | 2.681 | 0.618 | 0.625 | 0.990 | 0.990 | 2.708 | False | 2.159 | False |
| power pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | 0.010 | 0.004 | 0.003 | 0.009 | 0.009 | 1.105 | False | 0.017 | True |
| power pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | 0.004 | 0.005 | 0.009 | 0.012 | 0.012 | 0.367 | True | 0.014 | True |

R31 / R21 / R32:
| statistic | frequencies | |T(LO) + T(RO)| | twin Mild 5->6 | twin Moderate 5->6 | twin Severe 5->6 | max twin | ratio to max twin | within max twin |
|---|---|---|---|---|---|---|---|---|
| R31 (mirror-invariant) | band mean 3.2-4.2 | 0.013 | 0.034 | 0.004 | 0.051 | 0.051 | 0.251 | True |
| R21 (mirror-invariant) | band mean 3.2-4.2 | 0.133 | 0.034 | 0.000 | 0.110 | 0.110 | 1.213 | False |
| R32 (mirror-invariant) | band mean 3.2-4.2 | 0.146 | 0.068 | 0.004 | 0.161 | 0.161 | 0.907 | True |

## B. 0.3(b) Rulers rebuilt with the rotated nulls (NULL11 = 9 symmetric + Null_rot07 + Null_rot19)
Mirror statistics (88): how many rulers the rotated nulls raise, by family:
| family | n | raised | max_raise |
|---|---|---|---|
| phase LR index | 3 | 0 | 1.00 |
| phase cross-ratio | 44 | 23 | 2.51 |
| phase pair | 8 | 1 | 1.19 |
| power LR index | 3 | 2 | 1.17 |
| power cross-ratio | 22 | 14 | 3.34 |
| power pair | 8 | 2 | 2.47 |

Imaging mirror-test LR (operator rebuilt read-only):
| method | reference | T Null_rot07 | T Null_rot19 | floor 9 | floor 11 | yardstick | LeftOnly_test_c3 / ruler 9 | LeftOnly_test_c3 / ruler 11 | T LeftOnly_test_c3 | RightOnly_test / ruler 9 | RightOnly_test / ruler 11 | T RightOnly_test | Test_B / ruler 9 | Test_B / ruler 11 | T Test_B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tikhonov dS (primary) | Healthy_sliced | 1.41 | -0.96 | 4.07 | 4.07 | 2.14 | 1.93 | 1.93 | 7.86 | 2.50 | 2.50 | -10.17 | 0.04 | 0.04 | 0.18 |
| Tikhonov dS (primary) | Healthy_sliced_new | 1.39 | -0.93 | 4.04 | 4.04 | 2.12 | 1.94 | 1.94 | 7.86 | 2.51 | 2.51 | -10.15 | 0.05 | 0.05 | 0.20 |
| Tikhonov log (gain-inv.) | Healthy_sliced | 0.87 | -0.87 | 3.72 | 3.72 | 2.38 | 2.35 | 2.35 | 8.75 | 2.98 | 2.98 | -11.09 | 0.12 | 0.12 | -0.43 |
| Tikhonov log (gain-inv.) | Healthy_sliced_new | 0.88 | -0.88 | 3.76 | 3.76 | 2.38 | 2.35 | 2.35 | 8.82 | 2.98 | 2.98 | -11.20 | 0.11 | 0.11 | -0.40 |
| whitened log (post-hoc) | Healthy_sliced | 0.58 | -0.68 | 3.14 | 3.14 | 1.98 | 2.76 | 2.76 | 8.69 | 3.37 | 3.37 | -10.58 | 0.04 | 0.04 | -0.14 |
| whitened log (post-hoc) | Healthy_sliced_new | 0.59 | -0.68 | 3.17 | 3.17 | 1.97 | 2.77 | 2.77 | 8.77 | 3.38 | 3.38 | -10.71 | 0.03 | 0.03 | -0.09 |

Re-mesh yardstick (same physics, rotated mesh, same pass count as Healthy_sliced_new):
| quantity | one-pass yardstick | Null_rot07 - Healthy_sliced_new | Null_rot19 - Healthy_sliced_new | re-mesh max | new yardstick | new / old |
|---|---|---|---|---|---|---|
| R31 | 0.135 | 0.030 | 0.105 | 0.105 | 0.135 | 1.000 |
| R21 | 0.110 | 0.070 | -0.364 | 0.364 | 0.364 | 3.314 |
| R32 | 0.161 | -0.040 | 0.469 | 0.469 | 0.469 | 2.913 |
| index: front-back, all paths | 0.070 | 0.106 | 0.170 | 0.170 | 0.170 | 2.441 |
| index: front-back, neighbour paths | 0.068 | 0.165 | 0.040 | 0.165 | 0.165 | 2.426 |

Pattern-fit rulers: null contrast 0.212 deg (protocol) -> 0.419 deg; healthy-twin |ring mean| 1.111 -> 1.111 deg.

## Q4. Pattern fit: best vs runner-up, and the rotated healthy heads as targets
w = 0.4 (89af4b3); protocol rulers null contrast 0.212 deg, healthy twin 1.111 deg.
| design | truth | best | best residual | runner-up | runner-up residual | gap (deg) | gap / null contrast | runner-up / best | best = truth | all sectors certain (>= 2x) | contrast / null |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mild_lobe | 2356 | 2356 | 0.239 | 23456 | 0.395 | 0.156 | 0.735 | 1.654 | True | False | 2.641 |
| Mild_lobe_new | 2356 | 2356 | 0.214 | 36 | 0.513 | 0.300 | 1.410 | 2.400 | True | False | 3.149 |
| Moderate_lobe | 12356 | 12356 | 0.318 | 26 | 0.397 | 0.078 | 0.369 | 1.246 | True | False | 7.208 |
| Moderate_lobe_c3 | 12356 | 12356 | 0.206 | 26 | 0.304 | 0.098 | 0.462 | 1.477 | True | True | 6.724 |
| LeftOnly_test_c3 | 23 | 23 | 0.243 | 1234 | 0.702 | 0.459 | 2.160 | 2.891 | True | True | 7.998 |
| RightOnly_test | 56 | 56 | 0.232 | 1456 | 0.677 | 0.444 | 2.091 | 2.911 | True | True | 8.184 |
| Test_B | 25 | 25 | 0.286 | 235 | 0.495 | 0.209 | 0.982 | 1.728 | True | False | 3.243 |

Rotated healthy heads (and the old nulls) as targets against Healthy_sliced_new:
| target (vs Healthy_sliced_new) | rulers | best pattern | best residual | r0 | contrast / null | accepted | pattern call | ring mean g | |g| / healthy twin |
|---|---|---|---|---|---|---|---|---|---|
| Null_rot07 | protocol rulers | 136 | 0.127 | 0.419 | 1.971 | False | none | -0.163 | 0.147 |
| Null_rot07 | rulers incl. rotated nulls (leave-one-out) | 136 | 0.127 | 0.419 | 1.541 | False | none | -0.163 | 0.147 |
| Null_rot19 | protocol rulers | 1346 | 0.146 | 0.272 | 1.279 | False | none | -0.302 | 0.272 |
| Null_rot19 | rulers incl. rotated nulls (leave-one-out) | 1346 | 0.146 | 0.272 | 0.649 | False | none | -0.302 | 0.272 |
| Healthy_sliced | protocol rulers | 14 | 0.020 | 0.046 | 0.214 | False | none | 1.111 | 1.000 |
| Healthy_sliced | rulers incl. rotated nulls (leave-one-out) | 14 | 0.020 | 0.046 | 0.109 | False | none | 1.111 | 1.000 |
| MCI_lobe_c3 | protocol rulers | 1 | 0.029 | 0.116 | 0.544 | False | none | -0.185 | 0.167 |
| MCI_lobe_c3 | rulers incl. rotated nulls (leave-one-out) | 1 | 0.029 | 0.116 | 0.276 | False | none | -0.185 | 0.167 |

Test_B with the rulers incl. the rotated nulls: contrast 1.64x, accepted False, call 123456 (diffuse), sector confidences S1 affected 3.5, S2 affected 3.5, S3 affected 3.5, S4 affected 3.5, S5 affected 3.5, S6 affected 3.5

## Q3. Mirror-test votes: Test_B (diagonal S2 + S5) vs LeftOnly / RightOnly (one-sided)
Votes (|T| >= 2x ruler) with the 9-null rulers: {'': 19, 'left': 6, 'right': 1}; with the 11-null rulers: {'': 22, 'left': 3, 'right': 1}.
| statistic | frequencies | antennas | LeftOnly_test_c3 | LeftOnly_test_c3 / r9 | LeftOnly_test_c3 / r11 | RightOnly_test | RightOnly_test / r9 | RightOnly_test / r11 | Test_B | Test_B / r9 | Test_B / r11 | Test_B vote (r9 >= 2) | Test_B vote (r11 >= 2) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | T1T2T3T4 | -10.27 | 3.50 | 3.50 | 8.89 | 3.03 | 3.03 | -0.71 | 0.24 | 0.24 |  |  |
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | 3.30-3.65 GHz | T1T2T3T4 | -15.72 | 3.79 | 3.79 | 16.62 | 4.01 | 4.01 | -4.21 | 1.01 | 1.01 |  |  |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | T1T2T3T4 | 10.11 | 4.03 | 4.03 | -7.79 | 3.10 | 3.10 | 0.59 | 0.23 | 0.23 |  |  |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | 3.30-3.65 GHz | T1T2T3T4 | 15.13 | 4.05 | 4.05 | -15.31 | 4.10 | 4.10 | 2.31 | 0.62 | 0.62 |  |  |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | T1T2T3T5 | -5.11 | 2.49 | 2.49 | 2.91 | 1.42 | 1.42 | -1.64 | 0.80 | 0.80 |  |  |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | 3.30-3.65 GHz | T1T2T3T5 | 8.50 | 2.47 | 1.88 | -4.71 | 1.37 | 1.04 | -6.47 | 1.88 | 1.43 |  |  |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | T1T2T3T5 | 9.93 | 2.56 | 2.22 | -5.24 | 1.35 | 1.17 | 1.33 | 0.34 | 0.30 |  |  |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | 3.30-3.65 GHz | T1T2T3T5 | 15.71 | 2.54 | 1.71 | -10.14 | 1.64 | 1.10 | -3.47 | 0.56 | 0.38 |  |  |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | T1T2T3T6 | -5.11 | 2.49 | 2.49 | 2.91 | 1.42 | 1.42 | -1.64 | 0.80 | 0.80 |  |  |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | 3.30-3.65 GHz | T1T2T4T6 | -6.63 | 2.01 | 1.68 | 10.60 | 3.22 | 2.68 | -8.78 | 2.67 | 2.22 | left | left |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | 3.30-3.65 GHz | T1T2T4T6 | -13.25 | 2.01 | 1.68 | 21.19 | 3.22 | 2.68 | -17.57 | 2.67 | 2.22 | left | left |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | 3.30-3.65 GHz | T1T2T5T6 | 8.50 | 2.47 | 1.88 | -4.71 | 1.37 | 1.04 | -6.47 | 1.88 | 1.43 |  |  |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | T1T3T4T5 | 4.97 | 2.28 | 2.10 | -3.43 | 1.57 | 1.45 | -0.19 | 0.09 | 0.08 |  |  |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | 3.30-3.65 GHz | T1T3T4T5 | 9.09 | 3.72 | 1.78 | -6.03 | 2.46 | 1.18 | -4.58 | 1.87 | 0.90 |  |  |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | T1T3T4T5 | 9.94 | 2.28 | 2.10 | -6.86 | 1.57 | 1.45 | -0.39 | 0.09 | 0.08 |  |  |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | 3.30-3.65 GHz | T1T3T4T5 | 18.19 | 3.72 | 1.78 | -12.05 | 2.46 | 1.18 | -9.15 | 1.87 | 0.90 |  |  |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | T2T3T4T5 | -5.14 | 4.02 | 3.01 | 4.36 | 3.40 | 2.55 | -0.78 | 0.61 | 0.46 |  |  |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | 3.30-3.65 GHz | T2T3T4T5 | -6.03 | 3.44 | 1.37 | 9.28 | 5.30 | 2.11 | -6.89 | 3.93 | 1.57 | left |  |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | 3.30-3.65 GHz | T2T3T4T5 | 8.51 | 3.94 | 3.09 | -11.19 | 5.18 | 4.06 | 1.21 | 0.56 | 0.44 |  |  |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | T2T3T4T6 | -10.30 | 2.37 | 2.37 | 10.34 | 2.38 | 2.38 | 0.15 | 0.03 | 0.03 |  |  |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | 3.30-3.65 GHz | T2T3T4T6 | -14.54 | 3.96 | 2.03 | 20.47 | 5.58 | 2.86 | -8.09 | 2.21 | 1.13 | left |  |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | T2T3T4T6 | -5.14 | 4.02 | 3.01 | 4.36 | 3.40 | 2.55 | -0.78 | 0.61 | 0.46 |  |  |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | 3.30-3.65 GHz | T2T3T4T6 | -6.03 | 3.44 | 1.37 | 9.28 | 5.30 | 2.11 | -6.89 | 3.93 | 1.57 | left |  |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | 3.30-3.65 GHz | T2T3T4T6 | 8.51 | 3.94 | 3.09 | -11.19 | 5.18 | 4.06 | 1.21 | 0.56 | 0.44 |  |  |
| power pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | T2T6 | -0.06 | 3.53 | 3.53 | 0.07 | 4.09 | 4.09 | -0.07 | 3.84 | 3.84 | left | left |
| power pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | T3T5 | -0.07 | 5.00 | 5.00 | 0.07 | 5.32 | 5.32 | 0.07 | 4.97 | 4.97 | right | right |

## Q2. Staging: R21 and R32 against the frozen stage edges
Frozen edges: three (R21) Normal|Mild -19.98, Mild|Severe -18.75 dB; merged (R32) Mild+Moderate|Normal 4.64, Severe|Mild+Moderate 2.77 dB.
| design | total cortical retreat (mm, sum of e) | materials | R21 | R21 - matched healthy | three label | R21 - Normal|Mild edge | R32 | merged label | R32 - Mild+Moderate|Normal edge |
|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced_new | 0.000 | healthy | -20.567 | 0.000 | Normal | -0.587 | 5.823 | Normal | 1.183 |
| Healthy_sliced | 0.000 | healthy | -20.507 | 0.000 | Normal | -0.527 | 5.898 | Normal | 1.258 |
| LeftOnly_test_c3 | 19.000 | Mild | -20.200 | 0.367 | Normal | -0.220 | 4.755 | Normal | 0.115 |
| RightOnly_test | 19.000 | Mild | -20.067 | 0.500 | Normal | -0.087 | 4.609 | Mild+Moderate | -0.031 |
| Test_B | 19.000 | Mild | -20.109 | 0.458 | Normal | -0.129 | 4.665 | Normal | 0.025 |
| Mild_lobe | 38.000 | Mild | -19.974 | 0.593 | UNCERTAIN | 0.006 | 4.152 | Mild+Moderate | -0.488 |
| Mild_lobe_new | 38.000 | Mild | -19.940 | 0.566 | Mild | 0.040 | 4.084 | Mild+Moderate | -0.556 |
| Moderate_lobe | 67.500 | Moderate | -19.451 | 1.116 | Mild | 0.529 | 3.443 | Mild+Moderate | -1.197 |
| uniform new_Healthy.s6p | 0.000 | healthy | -20.722 | 0.000 | Normal | -0.742 | 6.048 | Normal | 1.408 |
| uniform new_MildAD.s6p | 74.700 | Mild | -19.479 | 1.243 | Mild | 0.501 | 3.421 | Mild+Moderate | -1.219 |
| uniform brain_sevem_layer_Healthy.s6p | 0.000 | healthy | -20.395 | 0.000 | Normal | -0.415 | 5.916 | Normal | 1.276 |
| uniform Brain_sevem_layer_MildAD.s6p | 74.700 | Mild | -19.308 | 1.086 | Mild | 0.672 | 3.113 | Mild+Moderate | -1.527 |

Mild-material designs: R21 rise vs total cortical retreat, linear fit slope 0.131 dB per 10 mm, intercept +0.159 dB. The Normal|Mild edge corresponds to about 33 mm of total retreat relative to Healthy_sliced_new.

## C. Survival of every ruler-dependent claim and reading (old rulers vs rulers with the rotated nulls)
Claim numbers refer to MODEL_CARD 6.2. Claims 1, 4, 5, 7, 8, 12-14 and 21-27 do not use a null floor or the mesh yardstick as their ruler (or use sub-band yardsticks not rebuilt here) and are not listed.
| claim / reading | old rulers (9 nulls, one-pass yardstick) | new rulers (11 nulls, re-mesh yardstick) | survives | note |
|---|---|---|---|---|
| 2/11 lobe labels >= 3x (A1), all 30 | 20/30 | 7/30 | weakened |  |
| 2 detection Healthy_sliced_new (quadrature +-0.5 dB) | 3.04x | 3.04x | yes |  |
| 2 detection Healthy_sliced (quadrature +-0.5 dB) | 3.96x | 3.96x | yes |  |
| 2 detection Mild_lobe (quadrature +-0.5 dB) | 3.18x | 3.18x | yes |  |
| 2 detection Mild_lobe_new (quadrature +-0.5 dB) | 3.42x | 3.42x | yes |  |
| 2 detection Moderate_lobe (quadrature +-0.5 dB) | 4.44x | 4.44x | yes |  |
| 2 detection Moderate_lobe_c3 (quadrature +-0.5 dB) | 4.46x | 4.46x | yes |  |
| 3 detection Severe_lobe (quadrature) | 1.23x | 1.23x | unchanged verdict |  |
| 3 detection Severe_lobe_c3 (quadrature) | 1.58x | 1.58x | unchanged verdict |  |
| 3 detection LeftOnly_test_c3 (quadrature) | 0.64x | 0.64x | unchanged verdict |  |
| 3 detection MCI_lobe_c3 (quadrature) | 2.85x | 2.85x | unchanged verdict |  |
| 6 mask dependency: Mild_lobe_new R31 shift 0.319 dB / yardstick | 2.36x | 2.36x | yes |  |
| 10 R21 lobe stage gaps (smallest 0.489 dB, lobe_B Mild|Moderate) / 2 x yardstick | 2.23x | 0.67x | no |  |
| 15 [POST HOC] imaging LR LeftOnly (Tikhonov dS, H6) | 1.94x | 1.94x | not determined (< 2x) |  |
| RightOnly imaging LR (P5) | 2.51x | 2.51x | sensitive (2-3x) |  |
| Test_B imaging LR | 0.05x | 0.05x | not determined (< 2x) |  |
| 16 [POST HOC] LeftOnly phase cross-ratios >= 3x (band mean 3.2-4.2) | 4 | 4 | yes |  |
| Test_B phase cross-ratios >= 3x (band mean 3.2-4.2) | 0 | 0 | - |  |
| RightOnly phase cross-ratios >= 3x (band mean 3.2-4.2) (P2) | 4 | 2 | - |  |
| 16 [POST HOC] LeftOnly phase cross-ratios >= 3x (3.30-3.65 GHz) | 9 | 4 | yes |  |
| Test_B phase cross-ratios >= 3x (3.30-3.65 GHz) | 4 | 2 | - |  |
| RightOnly phase cross-ratios >= 3x (3.30-3.65 GHz) (P2) | 9 | 4 | - |  |
| 17 [POST HOC] LeftOnly left-right resonance shift vs null max (MHz) | +1.91 vs 2.86 | +1.91 vs 2.86 | yes (still no shift beyond the null) |  |
| 18 reflection pair T2 refl. vs T6 refl.: LeftOnly_test_c3 | 3.53x | 3.53x | robust (>= 3x) |  |
| 18 reflection pair T2 refl. vs T6 refl.: RightOnly_test | 4.09x | 4.09x | robust (>= 3x) |  |
| 18 reflection pair T2 refl. vs T6 refl.: Test_B | 3.84x | 3.84x | robust (>= 3x) |  |
| 18 reflection pair T3 refl. vs T5 refl.: LeftOnly_test_c3 | 5.00x | 5.00x | robust (>= 3x) |  |
| 18 reflection pair T3 refl. vs T5 refl.: RightOnly_test | 5.32x | 5.32x | robust (>= 3x) |  |
| 18 reflection pair T3 refl. vs T5 refl.: Test_B | 4.97x | 4.97x | robust (>= 3x) |  |
| 19 [POST HOC] LeftOnly neighbour phase pair T2-T3 vs T5-T6 (3.30-3.65 GHz) vs null max | -5.07 vs 1.79 (2.8x) | -5.07 vs 1.79 (2.8x) | sensitive (2-3x) |  |
| 19 [POST HOC] LeftOnly neighbour phase pair T3-T4 vs T4-T5 (3.30-3.65 GHz) vs null max | -3.40 vs 0.63 (5.4x) | -3.40 vs 1.28 (2.7x) | sensitive (2-3x) |  |
| 19 [POST HOC] LeftOnly neighbour phase pair T1-T2 vs T1-T6 (3.30-3.65 GHz) vs null max | -2.26 vs 1.40 (1.6x) | -2.26 vs 1.40 (1.6x) | not determined (< 2x) |  |
| 20 Moderate_lobe imaging T (-4.04) vs the rotated nulls (Tikhonov dS, H6) | largest of the 9 | rot07 +1.39, rot19 -0.93 | context |  |
| 28 C6 P1: within tolerance (26 informative) | 12/26 | 21/26 | post hoc only; verdict stands |  |
| 29 R21 mirror-twin difference 0.133 dB / yardstick | 1.21x | 0.37x | no (within the re-mesh yardstick) |  |
| C6 P4: RightOnly - LeftOnly within yardstick (R31, R21, R32) | R31 True, R21 False, R32 True | R31 True, R21 True, R32 True | post hoc only; verdict stands |  |
| Test_B binary label margin (A1) | 0.70x | 0.70x | not determined (< 2x) |  |
| Test_B three label margin (A1) | 1.11x | 0.33x | not determined (< 2x) |  |
| Test_B three_merged label margin (A1) | 0.16x | 0.05x | not determined (< 2x) |  |
| Test_B index: front-back, all paths | 0.02x | 0.02x | not determined (< 2x) |  |
| Test_B index: front-back, neighbour paths | 0.48x | 0.32x | not determined (< 2x) |  |
| Test_B mirror side (votes >= 2x) | left (7 votes, 4 >= 3x) | mixed (4 votes) | no |  |
| Test_B pattern fit 25: contrast / accepted | 3.24x / accepted | 1.64x / rejected | no |  |

Front-back indices (vs Healthy_sliced_new):
| design | index | value dB (vs H6) | ratio old | ratio new |
|---|---|---|---|---|
| Test_B | index: front-back, all paths | -0.003 | 0.022 | 0.015 |
| Test_B | index: front-back, neighbour paths | -0.053 | 0.478 | 0.322 |
| LeftOnly_test_c3 | index: front-back, all paths | 0.137 | 1.127 | 0.810 |
| LeftOnly_test_c3 | index: front-back, neighbour paths | 0.074 | 0.669 | 0.451 |
| RightOnly_test | index: front-back, all paths | 0.168 | 1.375 | 0.988 |
| RightOnly_test | index: front-back, neighbour paths | 0.163 | 1.469 | 0.989 |

Label margins (all designs):
| design | rule | label | margin dB | A1 old | A1 new | quadrature old | quadrature new |
|---|---|---|---|---|---|---|---|
| Healthy_sliced_new | binary | Normal | -0.45 | 3.33 | 3.33 | 3.04 | 3.04 |
| Healthy_sliced_new | three | Normal | 0.58 | 5.28 | 1.59 | 4.27 | 1.56 |
| Healthy_sliced_new | three_merged | Normal | -1.18 | 7.36 | 2.53 | 6.80 | 2.50 |
| Mild_lobe | binary | AD | 0.47 | 3.49 | 3.49 | 3.18 | 3.18 |
| Mild_lobe | three | UNCERTAIN | 0.01 | 0.06 | 0.02 | 0.05 | 0.02 |
| Mild_lobe | three_merged | Mild+Moderate | 0.48 | 2.99 | 1.03 | 2.76 | 1.02 |
| Moderate_lobe | binary | AD | 0.66 | 4.86 | 4.86 | 4.44 | 4.44 |
| Moderate_lobe | three | Mild | -0.52 | 4.71 | 1.42 | 3.81 | 1.39 |
| Moderate_lobe | three_merged | Mild+Moderate | -0.66 | 4.10 | 1.41 | 3.81 | 1.40 |
| Severe_lobe | binary | AD | 0.18 | 1.35 | 1.35 | 1.23 | 1.23 |
| Severe_lobe | three | Severe | -0.74 | 6.77 | 2.04 | 5.98 | 2.02 |
| Severe_lobe | three_merged | Severe | 0.30 | 1.85 | 0.64 | 1.72 | 0.63 |
| Healthy_sliced | binary | Normal | -0.59 | 4.34 | 4.34 | 3.96 | 3.96 |
| Healthy_sliced | three | Normal | 0.52 | 4.73 | 1.43 | 3.82 | 1.40 |
| Healthy_sliced | three_merged | Normal | -1.26 | 7.83 | 2.69 | 7.23 | 2.66 |
| Mild_lobe_new | binary | AD | 0.51 | 3.74 | 3.74 | 3.42 | 3.42 |
| Mild_lobe_new | three | Mild | -0.03 | 0.26 | 0.08 | 0.21 | 0.08 |
| Mild_lobe_new | three_merged | Mild+Moderate | 0.55 | 3.41 | 1.17 | 3.15 | 1.16 |
| Moderate_lobe_c3 | binary | AD | 0.66 | 4.89 | 4.89 | 4.46 | 4.46 |
| Moderate_lobe_c3 | three | Mild | -0.52 | 4.71 | 1.42 | 3.81 | 1.39 |
| Moderate_lobe_c3 | three_merged | Mild+Moderate | -0.66 | 4.08 | 1.40 | 3.78 | 1.39 |
| Severe_lobe_c3 | binary | AD | 0.23 | 1.73 | 1.73 | 1.58 | 1.58 |
| Severe_lobe_c3 | three | Severe | -0.85 | 7.77 | 2.34 | 6.86 | 2.31 |
| Severe_lobe_c3 | three_merged | Severe | 0.46 | 2.85 | 0.98 | 2.65 | 0.97 |
| LeftOnly_test_c3 | binary | AD | 0.09 | 0.70 | 0.70 | 0.64 | 0.64 |
| LeftOnly_test_c3 | three | Normal | 0.21 | 1.93 | 0.58 | 1.56 | 0.57 |
| LeftOnly_test_c3 | three_merged | Normal | -0.12 | 0.72 | 0.25 | 0.67 | 0.25 |
| MCI_lobe_c3 | binary | Normal | -0.42 | 3.12 | 3.12 | 2.85 | 2.85 |
| MCI_lobe_c3 | three | Normal | 0.57 | 5.18 | 1.56 | 4.18 | 1.53 |
| MCI_lobe_c3 | three_merged | Normal | -1.14 | 7.11 | 2.44 | 6.57 | 2.42 |
| RightOnly_test | binary | AD | 0.11 | 0.79 | 0.79 | 0.72 | 0.72 |
| RightOnly_test | three | Normal | 0.08 | 0.72 | 0.22 | 0.58 | 0.21 |
| RightOnly_test | three_merged | Mild+Moderate | 0.02 | 0.15 | 0.05 | 0.14 | 0.05 |
| Test_B | binary | AD | 0.09 | 0.70 | 0.70 | 0.64 | 0.64 |
| Test_B | three | Normal | 0.12 | 1.11 | 0.33 | 0.89 | 0.33 |
| Test_B | three_merged | Normal | -0.03 | 0.16 | 0.05 | 0.15 | 0.05 |

Every mirror-statistic ruler:
| statistic | frequencies | informative (C6) | yardstick | floor 9 | floor 11 | set by | ruler 9 | ruler 11 | ruler 11 / ruler 9 | LeftOnly_test_c3 / ruler 9 | RightOnly_test / ruler 9 | Test_B / ruler 9 | LeftOnly_test_c3 / ruler 11 | RightOnly_test / ruler 11 | Test_B / ruler 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | True | 1.498 | 2.931 | 2.931 | Healthy_sliced | 2.931 | 2.931 | 1.000 | 3.503 | 3.032 | 0.243 | 3.503 | 3.032 | 0.243 |
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | 3.30-3.65 GHz | True | 1.812 | 4.148 | 4.148 | Healthy_sliced | 4.148 | 4.148 | 1.000 | 3.790 | 4.007 | 1.015 | 3.790 | 4.007 | 1.015 |
| phase cross-ratio T1T2·T3T4 / T1T4·T2T3 | band mean 3.2-4.2 | False | 0.724 | 1.592 | 1.592 | Severe_lobe | 1.592 | 1.592 | 1.000 | 0.095 | 0.688 | 0.077 | 0.095 | 0.688 | 0.077 |
| phase cross-ratio T1T2·T3T4 / T1T4·T2T3 | 3.30-3.65 GHz | False | 0.377 | 1.779 | 1.779 | Severe_lobe_c3 | 1.779 | 1.779 | 1.000 | 0.333 | 0.738 | 1.067 | 0.333 | 0.738 | 1.067 |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | True | 1.464 | 2.510 | 2.510 | Healthy_sliced | 2.510 | 2.510 | 1.000 | 4.029 | 3.103 | 0.235 | 4.029 | 3.103 | 0.235 |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | 3.30-3.65 GHz | True | 1.702 | 3.737 | 3.737 | Mild_lobe | 3.737 | 3.737 | 1.000 | 4.048 | 4.096 | 0.618 | 4.048 | 4.096 | 0.618 |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | True | 1.511 | 2.051 | 2.051 | Mild_lobe | 2.051 | 2.051 | 1.000 | 2.491 | 1.417 | 0.801 | 2.491 | 1.417 | 0.801 |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | 3.30-3.65 GHz | False | 1.163 | 3.667 | 5.705 | Null_rot19 | 3.667 | 5.705 | 1.556 | 1.967 | 1.481 | 0.818 | 1.264 | 0.952 | 0.526 |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | band mean 3.2-4.2 | False | 0.797 | 2.768 | 2.768 | Moderate_lobe | 2.768 | 2.768 | 1.000 | 1.742 | 0.844 | 0.114 | 1.742 | 0.844 | 0.114 |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | 3.30-3.65 GHz | True | 1.104 | 3.438 | 4.521 | Null_rot07 | 3.438 | 4.521 | 1.315 | 2.473 | 1.371 | 1.883 | 1.880 | 1.042 | 1.432 |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | True | 1.765 | 3.884 | 4.480 | Null_rot07 | 3.884 | 4.480 | 1.153 | 2.556 | 1.350 | 0.342 | 2.216 | 1.170 | 0.296 |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | 3.30-3.65 GHz | True | 1.674 | 6.189 | 9.184 | Null_rot19 | 6.189 | 9.184 | 1.484 | 2.539 | 1.639 | 0.561 | 1.711 | 1.105 | 0.378 |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | True | 1.511 | 2.051 | 2.051 | Mild_lobe | 2.051 | 2.051 | 1.000 | 2.491 | 1.417 | 0.801 | 2.491 | 1.417 | 0.801 |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | 3.30-3.65 GHz | False | 1.163 | 3.667 | 5.705 | Null_rot19 | 3.667 | 5.705 | 1.556 | 1.967 | 1.481 | 0.818 | 1.264 | 0.952 | 0.526 |
| phase cross-ratio T1T2·T3T6 / T1T6·T2T3 | band mean 3.2-4.2 | False | 1.924 | 2.095 | 2.095 | Moderate_lobe_c3 | 2.095 | 2.095 | 1.000 | 0.138 | 0.273 | 0.935 | 0.138 | 0.273 | 0.935 |
| phase cross-ratio T1T2·T3T6 / T1T6·T2T3 | 3.30-3.65 GHz | False | 1.439 | 2.911 | 2.911 | Severe_lobe_c3 | 2.911 | 2.911 | 1.000 | 0.443 | 0.247 | 3.255 | 0.443 | 0.247 | 3.255 |
| phase cross-ratio T1T2·T4T5 / T1T4·T2T5 | band mean 3.2-4.2 | False | 1.572 | 1.767 | 1.767 | Mild_lobe | 1.767 | 1.767 | 1.000 | 0.078 | 0.297 | 1.038 | 0.078 | 0.297 | 1.038 |
| phase cross-ratio T1T2·T4T5 / T1T4·T2T5 | 3.30-3.65 GHz | False | 1.100 | 1.354 | 1.354 | Moderate_lobe_c3 | 1.354 | 1.354 | 1.000 | 1.390 | 0.438 | 5.597 | 1.390 | 0.438 | 5.597 |
| phase cross-ratio T1T2·T4T5 / T1T5·T2T4 | band mean 3.2-4.2 | False | 1.917 | 3.240 | 4.305 | Null_rot07 | 3.240 | 4.305 | 1.329 | 0.100 | 0.624 | 0.339 | 0.075 | 0.470 | 0.255 |
| phase cross-ratio T1T2·T4T5 / T1T5·T2T4 | 3.30-3.65 GHz | False | 2.855 | 4.950 | 8.916 | Null_rot07 | 4.950 | 8.916 | 1.801 | 0.499 | 0.924 | 2.699 | 0.277 | 0.513 | 1.498 |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | band mean 3.2-4.2 | False | 1.052 | 2.747 | 2.747 | Severe_lobe_c3 | 2.747 | 2.747 | 1.000 | 1.928 | 1.986 | 0.329 | 1.928 | 1.986 | 0.329 |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | 3.30-3.65 GHz | True | 2.091 | 3.291 | 3.951 | Null_rot07 | 3.291 | 3.951 | 1.201 | 2.014 | 3.220 | 2.669 | 1.677 | 2.682 | 2.223 |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | band mean 3.2-4.2 | False | 2.103 | 5.493 | 5.493 | Severe_lobe_c3 | 5.493 | 5.493 | 1.000 | 1.928 | 1.986 | 0.329 | 1.928 | 1.986 | 0.329 |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | 3.30-3.65 GHz | True | 4.181 | 6.581 | 7.903 | Null_rot07 | 6.581 | 7.903 | 1.201 | 2.014 | 3.220 | 2.669 | 1.677 | 2.682 | 2.223 |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | band mean 3.2-4.2 | False | 0.797 | 2.768 | 2.768 | Moderate_lobe | 2.768 | 2.768 | 1.000 | 1.742 | 0.844 | 0.114 | 1.742 | 0.844 | 0.114 |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | 3.30-3.65 GHz | True | 1.104 | 3.438 | 4.521 | Null_rot07 | 3.438 | 4.521 | 1.315 | 2.473 | 1.371 | 1.883 | 1.880 | 1.042 | 1.432 |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | True | 0.953 | 2.179 | 2.366 | Null_rot07 | 2.179 | 2.366 | 1.086 | 2.282 | 1.575 | 0.089 | 2.102 | 1.450 | 0.082 |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | 3.30-3.65 GHz | True | 1.232 | 2.446 | 5.107 | Null_rot19 | 2.446 | 5.107 | 2.088 | 3.718 | 2.463 | 1.871 | 1.781 | 1.180 | 0.896 |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | True | 1.905 | 4.358 | 4.732 | Null_rot07 | 4.358 | 4.732 | 1.086 | 2.282 | 1.575 | 0.089 | 2.102 | 1.450 | 0.082 |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | 3.30-3.65 GHz | True | 2.464 | 4.892 | 10.214 | Null_rot19 | 4.892 | 10.214 | 2.088 | 3.718 | 2.463 | 1.871 | 1.781 | 1.180 | 0.896 |
| phase cross-ratio T1T3·T4T6 / T1T4·T3T6 | band mean 3.2-4.2 | False | 1.999 | 3.335 | 3.825 | Null_rot07 | 3.335 | 3.825 | 1.147 | 0.056 | 0.764 | 0.221 | 0.048 | 0.666 | 0.193 |
| phase cross-ratio T1T3·T4T6 / T1T4·T3T6 | 3.30-3.65 GHz | False | 1.755 | 3.818 | 7.720 | Null_rot07 | 3.818 | 7.720 | 2.022 | 0.153 | 1.353 | 1.515 | 0.076 | 0.669 | 0.749 |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | True | 1.120 | 1.281 | 1.711 | Null_rot07 | 1.281 | 1.711 | 1.336 | 4.016 | 3.403 | 0.610 | 3.006 | 2.547 | 0.457 |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | 3.30-3.65 GHz | True | 1.751 | 1.512 | 4.396 | Null_rot07 | 1.751 | 4.396 | 2.510 | 3.445 | 5.301 | 3.932 | 1.373 | 2.112 | 1.567 |
| phase cross-ratio T2T3·T4T5 / T2T5·T3T4 | band mean 3.2-4.2 | False | 1.219 | 2.007 | 2.007 | MCI_lobe_c3 | 2.007 | 2.007 | 1.000 | 0.007 | 0.807 | 0.853 | 0.007 | 0.807 | 0.853 |
| phase cross-ratio T2T3·T4T5 / T2T5·T3T4 | 3.30-3.65 GHz | False | 0.790 | 2.142 | 2.142 | MCI_lobe_c3 | 2.142 | 2.142 | 1.000 | 1.155 | 0.889 | 2.651 | 1.155 | 0.889 | 2.651 |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | band mean 3.2-4.2 | False | 1.113 | 3.107 | 3.107 | Severe_lobe_c3 | 3.107 | 3.107 | 1.000 | 1.660 | 1.924 | 0.300 | 1.660 | 1.924 | 0.300 |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | 3.30-3.65 GHz | True | 1.002 | 2.159 | 2.755 | Null_rot07 | 2.159 | 2.755 | 1.276 | 3.941 | 5.183 | 0.559 | 3.088 | 4.061 | 0.438 |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | True | 2.233 | 4.351 | 4.351 | Severe_lobe_c3 | 4.351 | 4.351 | 1.000 | 2.368 | 2.376 | 0.034 | 2.368 | 2.376 | 0.034 |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | 3.30-3.65 GHz | True | 2.742 | 3.671 | 7.151 | Null_rot07 | 3.671 | 7.151 | 1.948 | 3.962 | 5.578 | 2.205 | 2.034 | 2.863 | 1.132 |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | True | 1.120 | 1.281 | 1.711 | Null_rot07 | 1.281 | 1.711 | 1.336 | 4.016 | 3.403 | 0.610 | 3.006 | 2.547 | 0.457 |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | 3.30-3.65 GHz | True | 1.751 | 1.512 | 4.396 | Null_rot07 | 1.751 | 4.396 | 2.510 | 3.445 | 5.301 | 3.932 | 1.373 | 2.112 | 1.567 |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | band mean 3.2-4.2 | False | 1.113 | 3.107 | 3.107 | Severe_lobe_c3 | 3.107 | 3.107 | 1.000 | 1.660 | 1.924 | 0.300 | 1.660 | 1.924 | 0.300 |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | 3.30-3.65 GHz | True | 1.002 | 2.159 | 2.755 | Null_rot07 | 2.159 | 2.755 | 1.276 | 3.941 | 5.183 | 0.559 | 3.088 | 4.061 | 0.438 |
| power LR index, all paths | band mean 3.2-4.2 | False | 0.064 | 0.099 | 0.116 | Null_rot07 | 0.099 | 0.116 | 1.170 | 0.149 | 0.696 | 0.176 | 0.127 | 0.595 | 0.151 |
| power LR index, neighbour paths | band mean 3.2-4.2 | False | 0.063 | 0.122 | 0.122 | Severe_lobe | 0.122 | 0.122 | 1.000 | 0.030 | 0.252 | 0.205 | 0.030 | 0.252 | 0.205 |
| power LR index, second-neighbour paths | band mean 3.2-4.2 | False | 0.191 | 0.185 | 0.213 | Null_rot07 | 0.191 | 0.213 | 1.113 | 0.222 | 0.665 | 0.425 | 0.199 | 0.597 | 0.382 |
| power pair T1-T2 vs T1-T6 | band mean 3.2-4.2 | False | 0.092 | 0.127 | 0.127 | MCI_lobe_c3 | 0.127 | 0.127 | 1.000 | 0.647 | 0.383 | 0.245 | 0.647 | 0.383 | 0.245 |
| power pair T1-T3 vs T1-T5 | band mean 3.2-4.2 | False | 0.157 | 0.495 | 0.495 | Moderate_lobe_c3 | 0.495 | 0.495 | 1.000 | 0.219 | 0.019 | 0.751 | 0.219 | 0.019 | 0.751 |
| power pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | True | 0.009 | 0.017 | 0.017 | Severe_lobe | 0.017 | 0.017 | 1.000 | 3.528 | 4.092 | 3.839 | 3.528 | 4.092 | 3.839 |
| power pair T2-T3 vs T5-T6 | band mean 3.2-4.2 | False | 0.115 | 0.295 | 0.295 | Severe_lobe | 0.295 | 0.295 | 1.000 | 0.350 | 0.222 | 0.528 | 0.350 | 0.222 | 0.528 |
| power pair T2-T4 vs T4-T6 | band mean 3.2-4.2 | False | 0.248 | 0.301 | 0.743 | Null_rot19 | 0.301 | 0.743 | 2.467 | 0.641 | 0.812 | 1.774 | 0.260 | 0.329 | 0.719 |
| power pair T2-T5 vs T3-T6 | band mean 3.2-4.2 | False | 0.117 | 0.209 | 0.209 | Moderate_lobe_c3 | 0.209 | 0.209 | 1.000 | 0.723 | 1.600 | 2.059 | 0.723 | 1.600 | 2.059 |
| power pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | True | 0.012 | 0.014 | 0.014 | Moderate_lobe | 0.014 | 0.014 | 1.000 | 5.000 | 5.318 | 4.971 | 5.000 | 5.318 | 4.971 |
| power pair T3-T4 vs T4-T5 | band mean 3.2-4.2 | False | 0.081 | 0.092 | 0.129 | Null_rot19 | 0.092 | 0.129 | 1.394 | 1.893 | 0.816 | 2.161 | 1.358 | 0.585 | 1.551 |
| power cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | False | 0.486 | 0.472 | 0.499 | Null_rot19 | 0.486 | 0.499 | 1.027 | 0.015 | 0.469 | 0.809 | 0.015 | 0.456 | 0.788 |
| power cross-ratio T1T2·T3T4 / T1T4·T2T3 | band mean 3.2-4.2 | False | 0.180 | 0.270 | 0.270 | Moderate_lobe_c3 | 0.270 | 0.270 | 1.000 | 0.724 | 0.144 | 1.430 | 0.724 | 0.144 | 1.430 |
| power cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | False | 0.399 | 0.407 | 0.450 | Null_rot19 | 0.407 | 0.450 | 1.106 | 0.462 | 0.464 | 0.017 | 0.417 | 0.419 | 0.015 |
| power cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | False | 0.177 | 0.305 | 0.517 | Null_rot19 | 0.305 | 0.517 | 1.695 | 0.580 | 0.904 | 2.527 | 0.342 | 0.534 | 1.491 |
| power cross-ratio T1T2·T3T5 / T1T5·T2T3 | band mean 3.2-4.2 | False | 0.151 | 0.439 | 0.439 | Severe_lobe_c3 | 0.439 | 0.439 | 1.000 | 0.200 | 0.239 | 1.274 | 0.200 | 0.239 | 1.274 |
| power cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | False | 0.328 | 0.643 | 0.881 | Null_rot19 | 0.643 | 0.881 | 1.370 | 0.411 | 0.592 | 2.067 | 0.300 | 0.432 | 1.509 |
| power cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | False | 0.177 | 0.305 | 0.517 | Null_rot19 | 0.305 | 0.517 | 1.695 | 0.580 | 0.904 | 2.527 | 0.342 | 0.534 | 1.491 |
| power cross-ratio T1T2·T3T6 / T1T6·T2T3 | band mean 3.2-4.2 | False | 0.237 | 0.365 | 0.365 | MCI_lobe_c3 | 0.365 | 0.365 | 1.000 | 0.245 | 0.469 | 0.581 | 0.245 | 0.469 | 0.581 |
| power cross-ratio T1T2·T4T5 / T1T4·T2T5 | band mean 3.2-4.2 | False | 0.158 | 0.242 | 0.242 | Mild_lobe | 0.242 | 0.242 | 1.000 | 0.438 | 0.869 | 2.472 | 0.438 | 0.869 | 2.472 |
| power cross-ratio T1T2·T4T5 / T1T5·T2T4 | band mean 3.2-4.2 | False | 0.333 | 0.657 | 1.130 | Null_rot19 | 0.657 | 1.130 | 1.719 | 0.850 | 0.546 | 1.124 | 0.494 | 0.318 | 0.654 |
| power cross-ratio T1T2·T4T6 / T1T4·T2T6 | band mean 3.2-4.2 | False | 0.340 | 0.428 | 0.814 | Null_rot19 | 0.428 | 0.814 | 1.900 | 0.643 | 0.685 | 1.320 | 0.338 | 0.360 | 0.695 |
| power cross-ratio T1T2·T4T6 / T1T6·T2T4 | band mean 3.2-4.2 | False | 0.679 | 0.857 | 1.628 | Null_rot19 | 0.857 | 1.628 | 1.900 | 0.643 | 0.685 | 1.320 | 0.338 | 0.360 | 0.695 |
| power cross-ratio T1T2·T5T6 / T1T5·T2T6 | band mean 3.2-4.2 | False | 0.151 | 0.439 | 0.439 | Severe_lobe_c3 | 0.439 | 0.439 | 1.000 | 0.200 | 0.239 | 1.274 | 0.200 | 0.239 | 1.274 |
| power cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | False | 0.237 | 0.545 | 0.545 | Moderate_lobe_c3 | 0.545 | 0.545 | 1.000 | 0.519 | 0.121 | 0.317 | 0.519 | 0.121 | 0.317 |
| power cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | False | 0.475 | 1.090 | 1.090 | Moderate_lobe_c3 | 1.090 | 1.090 | 1.000 | 0.519 | 0.121 | 0.317 | 0.519 | 0.121 | 0.317 |
| power cross-ratio T1T3·T4T6 / T1T4·T3T6 | band mean 3.2-4.2 | False | 0.175 | 0.417 | 1.331 | Null_rot19 | 0.417 | 1.331 | 3.190 | 1.084 | 1.364 | 3.203 | 0.340 | 0.428 | 1.004 |
| power cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | False | 0.261 | 0.382 | 0.765 | Null_rot19 | 0.382 | 0.765 | 2.003 | 1.232 | 0.666 | 0.470 | 0.615 | 0.332 | 0.235 |
| power cross-ratio T2T3·T4T5 / T2T5·T3T4 | band mean 3.2-4.2 | False | 0.245 | 0.510 | 0.510 | Moderate_lobe_c3 | 0.510 | 0.510 | 1.000 | 0.591 | 0.489 | 1.931 | 0.591 | 0.489 | 1.931 |
| power cross-ratio T2T4·T3T5 / T2T5·T3T4 | band mean 3.2-4.2 | False | 0.309 | 0.322 | 1.016 | Null_rot19 | 0.322 | 1.016 | 3.156 | 0.526 | 1.564 | 3.616 | 0.167 | 0.496 | 1.146 |
| power cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | False | 0.470 | 0.533 | 1.781 | Null_rot19 | 0.533 | 1.781 | 3.345 | 1.202 | 1.423 | 2.523 | 0.359 | 0.425 | 0.754 |
| power cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | False | 0.261 | 0.382 | 0.765 | Null_rot19 | 0.382 | 0.765 | 2.003 | 1.232 | 0.666 | 0.470 | 0.615 | 0.332 | 0.235 |
| power cross-ratio T2T4·T3T6 / T2T6·T3T4 | band mean 3.2-4.2 | False | 0.309 | 0.322 | 1.016 | Null_rot19 | 0.322 | 1.016 | 3.156 | 0.526 | 1.564 | 3.616 | 0.167 | 0.496 | 1.146 |
| phase pair T1-T2 vs T1-T6 | band mean 3.2-4.2 | False | 0.607 | 1.738 | 1.738 | Moderate_lobe | 1.738 | 1.738 | 1.000 | 1.148 | 1.861 | 1.295 | 1.148 | 1.861 | 1.295 |
| phase pair T1-T3 vs T1-T5 | band mean 3.2-4.2 | False | 1.270 | 3.256 | 3.256 | Moderate_lobe | 3.256 | 3.256 | 1.000 | 1.055 | 0.387 | 0.468 | 1.055 | 0.387 | 0.468 |
| phase pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | False | 0.169 | 0.385 | 0.385 | Moderate_lobe | 0.385 | 0.385 | 1.000 | 0.005 | 0.956 | 0.345 | 0.005 | 0.956 | 0.345 |
| phase pair T2-T3 vs T5-T6 | band mean 3.2-4.2 | False | 1.464 | 2.226 | 2.226 | Moderate_lobe | 2.226 | 2.226 | 1.000 | 1.519 | 1.936 | 0.185 | 1.519 | 1.936 | 0.185 |
| phase pair T2-T4 vs T4-T6 | band mean 3.2-4.2 | False | 1.658 | 2.889 | 2.889 | Severe_lobe_c3 | 2.889 | 2.889 | 1.000 | 1.142 | 0.768 | 0.466 | 1.142 | 0.768 | 0.466 |
| phase pair T2-T5 vs T3-T6 | band mean 3.2-4.2 | False | 1.055 | 1.866 | 1.866 | Mild_lobe | 1.866 | 1.866 | 1.000 | 0.172 | 0.851 | 1.143 | 0.172 | 0.851 | 1.143 |
| phase pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | False | 0.116 | 0.131 | 0.156 | Null_rot19 | 0.131 | 0.156 | 1.193 | 0.256 | 0.320 | 0.011 | 0.215 | 0.268 | 0.009 |
| phase pair T3-T4 vs T4-T5 | band mean 3.2-4.2 | False | 0.823 | 1.078 | 1.078 | Moderate_lobe | 1.078 | 1.078 | 1.000 | 1.426 | 2.014 | 1.593 | 1.426 | 2.014 | 1.593 |
| phase LR index, all paths | band mean 3.2-4.2 | False | 1.164 | 1.916 | 1.916 | Moderate_lobe | 1.916 | 1.916 | 1.000 | 0.019 | 0.651 | 0.080 | 0.019 | 0.651 | 0.080 |
| phase LR index, neighbour paths | band mean 3.2-4.2 | False | 0.964 | 1.681 | 1.681 | Moderate_lobe | 1.681 | 1.681 | 1.000 | 1.371 | 1.927 | 0.188 | 1.371 | 1.927 | 0.188 |
| phase LR index, second-neighbour paths | band mean 3.2-4.2 | False | 1.464 | 2.269 | 2.269 | Moderate_lobe | 2.269 | 2.269 | 1.000 | 1.484 | 0.767 | 0.039 | 1.484 | 0.767 | 0.039 |
