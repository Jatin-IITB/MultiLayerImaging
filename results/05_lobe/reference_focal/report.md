# POST HOC: typicality of the primary reference and a focal-disease table (code f5c8143)

Computed after Null_rot31 / Null_rot43 arrived. Nothing committed is changed; the alternative reference is not adopted.

## C. Each healthy mesh against the mean of the other five
Against Healthy_sliced_new (as quoted by the user; phase negative = more delay):
| mesh | dR31 vs H6 | dR21 vs H6 | dR32 vs H6 | ring mean vs H6 3.2-3.5 GHz | ring spread vs H6 3.2-3.5 GHz | left-right vs H6 3.2-3.5 GHz | ring mean vs H6 3.30-3.65 GHz | ring spread vs H6 3.30-3.65 GHz | left-right vs H6 3.30-3.65 GHz |
|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | 0.135 | 0.060 | 0.075 | 1.111 | 0.139 | -0.036 | 1.441 | 0.389 | -0.257 |
| Null_rot07 | 0.030 | 0.070 | -0.040 | -0.163 | 1.066 | -0.289 | -0.240 | 1.418 | -0.692 |
| Null_rot19 | 0.105 | -0.364 | 0.469 | -0.302 | 0.819 | -0.202 | -0.848 | 0.682 | -0.276 |
| Null_rot31 | 0.119 | 0.054 | 0.065 | -0.455 | 1.228 | -0.692 | -0.630 | 1.686 | -1.167 |
| Null_rot43 | 0.204 | -0.172 | 0.376 | -0.181 | 1.056 | -0.484 | -0.549 | 0.912 | -0.840 |

Each mesh minus the mean of the other five:
| mesh | R31 - mean(others) | R31 / SD(others) | R31 rank (1 = lowest) | R21 - mean(others) | R21 / SD(others) | R21 rank (1 = lowest) | R32 - mean(others) | R32 / SD(others) | R32 rank (1 = lowest) | ring mean 3.2-3.5 GHz | ring spread 3.2-3.5 GHz | left-right 3.2-3.5 GHz | ring mean 3.30-3.65 GHz | ring spread 3.30-3.65 GHz | left-right 3.30-3.65 GHz |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced_new | -0.119 | -1.898 | 1 | 0.070 | 0.364 | 3 | -0.189 | -0.857 | 2 | -0.002 | 0.750 | 0.341 | 0.165 | 0.907 | 0.647 |
| Healthy_sliced | 0.044 | 0.544 | 5 | 0.142 | 0.772 | 5 | -0.099 | -0.425 | 4 | 1.331 | 0.666 | 0.297 | 1.894 | 0.637 | 0.338 |
| Null_rot07 | -0.083 | -1.122 | 2 | 0.155 | 0.849 | 6 | -0.237 | -1.128 | 1 | -0.198 | 1.137 | -0.006 | -0.122 | 1.121 | -0.184 |
| Null_rot19 | 0.007 | 0.089 | 3 | -0.366 | -3.621 | 1 | 0.374 | 2.279 | 6 | -0.365 | 0.754 | 0.098 | -0.853 | 0.671 | 0.315 |
| Null_rot31 | 0.024 | 0.291 | 4 | 0.135 | 0.727 | 4 | -0.111 | -0.481 | 3 | -0.547 | 0.801 | -0.490 | -0.591 | 1.116 | -0.754 |
| Null_rot43 | 0.126 | 2.133 | 6 | -0.136 | -0.733 | 2 | 0.262 | 1.285 | 5 | -0.219 | 1.177 | -0.241 | -0.494 | 1.058 | -0.362 |

Healthy_sliced_new flags:
| quantity | mesh | deviation | SD of the other five | extreme (rank 1 or 6) | outlier (extreme and >= 2 SD) |
|---|---|---|---|---|---|
| R31 | Healthy_sliced_new | -0.119 | 0.062 | True | False |
| R21 | Healthy_sliced_new | 0.070 | 0.193 | False | False |
| R32 | Healthy_sliced_new | -0.189 | 0.220 | False | False |
| ring mean 3.2-3.5 GHz | Healthy_sliced_new | -0.002 | 0.757 | False | False |
| ring mean 3.30-3.65 GHz | Healthy_sliced_new | 0.165 | 1.109 | False | False |

## D. If the reference were the mean of the healthy meshes (post hoc, not adopted)
Claims that use H6 as their reference: the re-mesh yardstick (|Q(rotated) - Q(H6)|), the Test_B pattern fit (y against H6), the R21 rise of the 19 mm designs (claim 32), the front-back index. The frozen labels themselves (R31 vs tau, R21 / R32 vs the LDA edges) and the mirror statistics are reference-free.
| quantity | one-pass yardstick | re-mesh vs H6 (pre-registered) | re-mesh vs mean of the five 6-pass meshes (post hoc) | pre-registered ruler | alternative ruler |
|---|---|---|---|---|---|
| R31 | 0.135 | 0.204 | 0.113 | 0.204 | 0.135 |
| R21 | 0.110 | 0.364 | 0.281 | 0.364 | 0.281 |
| R32 | 0.161 | 0.469 | 0.295 | 0.469 | 0.295 |

Detection margins:
| design | label | margin dB | A1 pre-registered (vs H6) | A1 alternative (vs mean) |
|---|---|---|---|---|
| Healthy_sliced_new | Normal | -0.45 | 2.21 | 3.33 |
| Mild_lobe | AD | 0.47 | 2.31 | 3.49 |
| Moderate_lobe | AD | 0.66 | 3.22 | 4.86 |
| Severe_lobe | AD | 0.18 | 0.89 | 1.35 |
| Healthy_sliced | Normal | -0.59 | 2.87 | 4.34 |
| Mild_lobe_new | AD | 0.51 | 2.48 | 3.74 |
| Moderate_lobe_c3 | AD | 0.66 | 3.24 | 4.89 |
| Severe_lobe_c3 | AD | 0.23 | 1.14 | 1.73 |
| LeftOnly_test_c3 | AD | 0.09 | 0.46 | 0.70 |
| MCI_lobe_c3 | Normal | -0.42 | 2.07 | 3.12 |
| RightOnly_test | AD | 0.11 | 0.52 | 0.79 |
| Test_B | AD | 0.09 | 0.46 | 0.70 |

R21 rise of the 19 mm designs:
| design | R21 rise vs H6 | R21 rise vs mean of 5 | / pre-registered R21 ruler | / alternative R21 ruler |
|---|---|---|---|---|
| LeftOnly_test_c3 | 0.367 | 0.449 | 1.010 | 1.597 |
| RightOnly_test | 0.500 | 0.583 | 1.376 | 2.070 |
| Test_B | 0.458 | 0.540 | 1.259 | 1.919 |

Test_B pattern fit, reference H6 (all-null rulers): contrast 1.60x, rejected, call 123456 (diffuse). Reference = mean of the five 6-pass meshes (null contrast 0.393 deg from leave-one-out healthy meshes): contrast 2.04x, accepted, call 25, best pattern 25.

## F. Focal-disease table (post hoc; against Healthy_sliced_new; phase negative = more delay)
The three opposite paths and the sides they join (a half-ring R31 would need an opposite path inside one half; there is none):
| opposite path | sides |
|---|---|
| T1-T4 | front (T1, midline) - back (T4, midline) |
| T2-T5 | left (T2) - right (T5) |
| T3-T6 | left (T3) - right (T6) |

| design | R31 T1 change dB | R31 T2 change dB | R31 T3 change dB | R31 T4 change dB | R31 T5 change dB | R31 T6 change dB | per-antenna R31 left-right dB | half-ring R21 left-right dB (design) | half-ring R21 left-right dB (minus H6) | neighbour-phase left-right deg 3.2-3.5 GHz | neighbour-phase left-right deg 3.30-3.65 GHz |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LeftOnly_test_c3 | -0.516 | -0.838 | -0.869 | -0.442 | -0.717 | -0.822 | -0.084 | -0.046 | -0.228 | -4.075 | -4.435 |
| RightOnly_test | -0.621 | -0.707 | -0.910 | -0.458 | -0.609 | -0.975 | -0.017 | -0.096 | -0.278 | 4.196 | 4.597 |
| Test_B | -0.471 | -1.072 | -0.608 | -0.525 | -1.022 | -0.505 | -0.076 | 0.106 | -0.076 | -0.485 | -0.432 |
| Mild_lobe | -0.868 | -1.186 | -1.250 | -0.753 | -1.116 | -1.295 | -0.012 | 0.231 | 0.049 | 0.021 | -0.064 |
| Mild_lobe_new | -0.792 | -1.365 | -1.308 | -0.680 | -1.235 | -1.291 | -0.074 | 0.062 | -0.120 | -0.332 | -0.367 |
| Null_rot07 | 0.012 | -0.105 | -0.027 | 0.177 | 0.106 | 0.018 | -0.128 | 0.161 | -0.021 | -0.289 | -0.692 |
| Null_rot19 | -0.024 | 0.095 | 0.292 | 0.017 | 0.046 | 0.203 | 0.069 | 0.266 | 0.084 | -0.202 | -0.276 |
| Null_rot31 | -0.065 | 0.113 | 0.169 | -0.002 | 0.253 | 0.245 | -0.108 | -0.077 | -0.259 | -0.692 | -1.167 |
| Null_rot43 | 0.088 | 0.091 | 0.325 | 0.311 | 0.198 | 0.210 | 0.004 | 0.256 | 0.074 | -0.484 | -0.840 |

Spread of each statistic on LeftOnly under per-port calibration errors (2000 draws each):
| statistic | SD under +-0.5 dB per-port gain error | SD under +-10 deg per-port phase error |
|---|---|---|
| per-antenna R31 left-right dB | 0.436 | 0.000 |
| half-ring R21 left-right dB (design) | 0.097 | 0.000 |
| neighbour-phase left-right deg 3.2-3.5 GHz | 0.000 | 8.632 |
| neighbour-phase left-right deg 3.30-3.65 GHz | 0.000 | 8.632 |
| per-antenna R31 T2 change dB | 0.352 | 0.000 |
