# Lobe convergence study: stop-rule matched sets and one-extra-pass mesh yardstick (code 7f5b39b)

HFSS Setup1 (user, from the convergence tables): adaptive at 3.4 GHz, Max Delta S 0.02, 30% refinement per pass, first-order basis, iterative solver; interpolating sweep 3.2-4.2 GHz, 201 points. Meshing is deterministic. Stop rule 1 = first pass with Delta S < 0.02; stop rule 2 = two consecutive passes.
Sets: **lobe_A** (stop rule 1; primary): Healthy_sliced_new, Mild_lobe, Moderate_lobe, Severe_lobe. **lobe_B** (stop rule 2): Healthy_sliced, Mild_lobe_new. **lobe_v1** (Prompt 07, unmatched): Healthy_sliced (rule 2) with the rule-1 stages. lobe_A/lobe_B are *stop-rule matched*, not mesh-matched: the healthy head still has 1.46x (A) / 1.54x (B) the elements of Mild. One solve per design and stop rule: within-simulation noise robustness, not generalisation.

| design | class | set | stop_rule | passes | final_dS | elements |
|---|---|---|---|---|---|---|
| Healthy_sliced | Normal | lobe_v1 lobe_B | 2 | 7 | 0.0092 | 1349491 |
| Healthy_sliced_new | Normal | lobe_A | 1 | 6 | 0.0155 | 1081728 |
| Mild_lobe | Mild | lobe_v1 lobe_A | 1 | 5 | 0.0186 | 739774 |
| Mild_lobe_new | Mild | lobe_B | 2 | 6 | 0.015 | 878656 |
| Moderate_lobe | Moderate | lobe_v1 lobe_A | 1 | 5 | 0.0194 | 796281 |
| Severe_lobe | Severe | lobe_v1 lobe_A | 1 | 5 | 0.02 | 690077 |

## 0. Duplicates and glitch log
Re-solves with an unchanged stop rule reproduce the file (deterministic meshing); only one of each is in the manifest:
| file | same as | max |S_new - S| (linear) |
|---|---|---|
| new_with_slices_Moderate_lobe_new.s6p | new_with_slices_Moderate_lobe.s6p | 9.14e-09 |
| new_with_slices_Severe_lobe_new.s6p | new_with_slices_Severe_lobe.s6p | 1.65e-08 |

Points masked by the analysis (|Sij - Sji| > -30 dB of the pair's band level; Sij and Sji replaced by linear interpolation), all lobe files including duplicates. Log: `results/05_lobe/qc/masked_points.csv`. The Prompt 07 QC report's 'no glitches' used a different, local detector (|Sij - Sji|/|Sij| > -20 dB) and missed the two weak lobe_v1 points; the analysis masked them throughout.
| file | f_GHz | ports | path | type | |Sij| dB | |Sji| dB | reciprocity error dB (re band level) | masked |
|---|---|---|---|---|---|---|---|---|
| new_with_slices_Healthy_sliced.s6p | 3.52 | 1-4 | T1-T4 | opposite | -42.42 | -42.49 | -23.35 | True |
| new_with_slices_Mild_lobe_new.s6p | 3.85 | 3-6 | T2-T5 | opposite | -34.03 | -38.87 | 10.93 | True |
| new_with_slices_Severe_lobe.s6p | 3.85 | 2-5 | T3-T6 | opposite | -53.37 | -53.19 | -25.69 | True |
| new_with_slices_Severe_lobe_new.s6p | 3.85 | 2-5 | T3-T6 | opposite | -53.37 | -53.19 | -25.69 | True |

## 1. Reproduction of the user's convergence table
Plain mean (no masking; |S|^2 averaged over 201 points and the 12/12/6 equivalent pairs; kept for traceability only):
| file | passes | C1 | C2 | C3 (opposite) | R31 | R21 | R32 |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | 7 | -36.87 | -57.37 | -51.44 | -14.57 | -20.50 | 5.93 |
| Healthy_sliced_new | 6 | -36.86 | -57.42 | -51.60 | -14.74 | -20.56 | 5.82 |
| Mild_lobe | 5 | -36.82 | -56.78 | -52.63 | -15.81 | -19.96 | 4.15 |
| Mild_lobe_new | 6 | -36.82 | -56.75 | -52.33 | -15.51 | -19.93 | 4.43 |
| Moderate_lobe | 5 | -37.06 | -56.51 | -53.07 | -16.00 | -19.44 | 3.44 |
| Severe_lobe | 5 | -37.70 | -55.70 | -53.23 | -15.52 | -18.00 | 2.47 |

Frozen-rule recipe (glitch masking, trapezoid band integration, geometric-mean ratios), used for every number below:
| file | passes | C1 neighbour | C2 second-neighbour | C3 opposite | R31 | R21 | R32 |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | 7 | -36.849 | -57.355 | -51.458 | -14.609 | -20.507 | 5.898 |
| Healthy_sliced_new | 6 | -36.837 | -57.404 | -51.581 | -14.744 | -20.567 | 5.823 |
| Mild_lobe | 5 | -36.799 | -56.765 | -52.615 | -15.822 | -19.974 | 4.152 |
| Mild_lobe_new | 6 | -36.799 | -56.737 | -52.645 | -15.856 | -19.940 | 4.084 |
| Moderate_lobe | 5 | -37.042 | -56.488 | -53.051 | -16.008 | -19.451 | 3.443 |
| Severe_lobe | 5 | -37.681 | -55.684 | -53.216 | -15.533 | -18.002 | 2.469 |

One extra adaptive pass:
| quantity | Healthy 6->7 dB | Mild 5->6 dB |
|---|---|---|
| R31 | 0.135 | -0.034 |
| R21 | 0.060 | 0.034 |
| R32 | 0.075 | -0.068 |
| C1 neighbour | -0.012 | -0.001 |
| C2 second-neighbour | 0.049 | 0.028 |
| C3 opposite | 0.124 | -0.030 |

Normal - Mild R31: lobe_A 1.08 dB, lobe_B 1.25 dB, lobe_v1 (unmatched) 1.21 dB. Frozen detection threshold tau = -15.27 dB. Margins to tau:
| set | design | R31 dB | margin to tau dB |
|---|---|---|---|
| lobe_A | Healthy_sliced_new | -14.744 | 0.529 |
| lobe_A | Mild_lobe | -15.822 | -0.549 |
| lobe_A | Moderate_lobe | -16.008 | -0.735 |
| lobe_A | Severe_lobe | -15.533 | -0.261 |
| lobe_B | Healthy_sliced | -14.609 | 0.664 |
| lobe_B | Mild_lobe_new | -15.856 | -0.583 |

The plain-mean Mild 5->6 change of C3 (+0.30 dB) is the Mild_lobe_new 3.855 GHz glitch on T2-T5 (section 0); with masking it is -0.03 dB.

## 2. Mesh yardstick against every stage effect
Yardstick = the larger change of the two one-extra-pass pairs (Healthy 6->7, Mild 5->6); for per-path values and cross-ratios at least the rms one-pass change of that family (asymmetry cross-ratio 0.169 dB, cross-ratio 0.188 dB, path (neighbour) 0.037 dB, path (opposite) 0.111 dB, path (reflection) 0.023 dB, path (second-neighbour) 0.122 dB). Symmetry floor = numerical error estimated from the mirror residual of the mirror-symmetric lobe_A stages (as in Prompt 07), for a difference of two designs (x sqrt 2): asymmetry cross-ratio 0.298 dB, cross-ratio 0.293 dB, index 0.185 dB, path (neighbour) 0.114 dB, path (opposite) 0.089 dB, path (reflection) 0.010 dB, path (second-neighbour) 0.210 dB. Noise SD = SD of the difference of two noisy measurements (typical noise, ±0.5 dB per-port gain; gain cancels in ratios and cross-ratios, not in paths or indices). **Clean ruler** = max(yardstick, symmetry floor); **measured ruler** = max(yardstick, floor (+) noise). Stage effects in lobe_A are stage minus Healthy_sliced_new; 'Moderate - Mild' adds the frontal lobe; 'Mild (B)' is Mild_lobe_new minus Healthy_sliced.
### Ring averages, ratios and front-back / left-right indices
| quantity | one pass Healthy dB | one pass Mild dB | yardstick dB | symmetry floor of a difference dB | noise SD of a difference dB | floor + noise dB |
|---|---|---|---|---|---|---|
| C1 neighbour | -0.012 | -0.001 | 0.012 | 0.000 | 0.349 | 0.349 |
| C2 second-neighbour | 0.049 | 0.028 | 0.049 | 0.000 | 0.358 | 0.358 |
| C3 opposite | 0.124 | -0.030 | 0.124 | 0.000 | 0.352 | 0.352 |
| R31 | 0.135 | -0.034 | 0.135 | 0.000 | 0.039 | 0.039 |
| R21 | 0.060 | 0.034 | 0.060 | 0.000 | 0.067 | 0.067 |
| R32 | 0.075 | -0.068 | 0.075 | 0.000 | 0.077 | 0.077 |
| index: front-back, all paths | 0.070 | -0.034 | 0.070 | 0.119 | 0.626 | 0.637 |
| index: left-right, all paths | -0.052 | -0.004 | 0.052 | 0.101 | 0.510 | 0.520 |
| index: front-back, neighbour paths | 0.068 | -0.003 | 0.068 | 0.114 | 0.798 | 0.806 |
| index: left-right, neighbour paths | 0.040 | 0.063 | 0.063 | 0.093 | 0.562 | 0.570 |
| index: front-back, second-neighbour paths | 0.071 | -0.066 | 0.071 | 0.210 | 0.741 | 0.770 |
| index: left-right, second-neighbour paths | -0.191 | -0.106 | 0.191 | 0.210 | 0.441 | 0.489 |

**Mild (A)**:
| quantity | Mild (A) dB | Mild (A) / yardstick | Mild (A) / noise SD | Mild (A) / clean ruler | Mild (A) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | 0.04 | 3.29 | 0.11 | 3.29 | 0.11 |
| C2 second-neighbour | 0.64 | 13.12 | 1.79 | 13.12 | 1.79 |
| C3 opposite | -1.03 | 8.36 | 2.93 | 8.36 | 2.93 |
| R31 | -1.08 | 7.98 | 27.77 | 7.98 | 7.98 |
| R21 | 0.59 | 9.87 | 8.91 | 9.87 | 8.91 |
| R32 | -1.67 | 22.26 | 21.73 | 22.26 | 21.73 |
| index: front-back, all paths | 0.21 | 3.03 | 0.34 | 1.76 | 0.33 |
| index: left-right, all paths | 0.03 | 0.61 | 0.06 | 0.32 | 0.06 |
| index: front-back, neighbour paths | 0.11 | 1.69 | 0.14 | 1.01 | 0.14 |
| index: left-right, neighbour paths | 0.01 | 0.19 | 0.02 | 0.13 | 0.02 |
| index: front-back, second-neighbour paths | 0.31 | 4.32 | 0.41 | 1.46 | 0.40 |
| index: left-right, second-neighbour paths | 0.06 | 0.32 | 0.14 | 0.29 | 0.13 |

**Moderate (A)**:
| quantity | Moderate (A) dB | Moderate (A) / yardstick | Moderate (A) / noise SD | Moderate (A) / clean ruler | Moderate (A) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.21 | 17.55 | 0.59 | 17.55 | 0.59 |
| C2 second-neighbour | 0.92 | 18.80 | 2.56 | 18.80 | 2.56 |
| C3 opposite | -1.47 | 11.89 | 4.17 | 11.89 | 4.17 |
| R31 | -1.26 | 9.35 | 32.55 | 9.35 | 9.35 |
| R21 | 1.12 | 18.58 | 16.76 | 18.58 | 16.76 |
| R32 | -2.38 | 31.70 | 30.94 | 31.70 | 30.94 |
| index: front-back, all paths | 0.14 | 2.00 | 0.22 | 1.16 | 0.22 |
| index: left-right, all paths | -0.08 | 1.48 | 0.15 | 0.77 | 0.15 |
| index: front-back, neighbour paths | -0.14 | 2.10 | 0.18 | 1.26 | 0.18 |
| index: left-right, neighbour paths | 0.03 | 0.48 | 0.05 | 0.33 | 0.05 |
| index: front-back, second-neighbour paths | 0.42 | 5.93 | 0.57 | 2.00 | 0.55 |
| index: left-right, second-neighbour paths | -0.24 | 1.25 | 0.54 | 1.14 | 0.49 |

**Severe (A)**:
| quantity | Severe (A) dB | Severe (A) / yardstick | Severe (A) / noise SD | Severe (A) / clean ruler | Severe (A) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.84 | 72.19 | 2.42 | 72.19 | 2.42 |
| C2 second-neighbour | 1.72 | 35.30 | 4.81 | 35.30 | 4.81 |
| C3 opposite | -1.63 | 13.22 | 4.64 | 13.22 | 4.64 |
| R31 | -0.79 | 5.84 | 20.33 | 5.84 | 5.84 |
| R21 | 2.57 | 42.71 | 38.54 | 42.71 | 38.54 |
| R32 | -3.35 | 44.69 | 43.62 | 44.69 | 43.62 |
| index: front-back, all paths | 0.14 | 2.06 | 0.23 | 1.20 | 0.23 |
| index: left-right, all paths | -0.09 | 1.65 | 0.17 | 0.86 | 0.17 |
| index: front-back, neighbour paths | 0.12 | 1.81 | 0.15 | 1.08 | 0.15 |
| index: left-right, neighbour paths | -0.06 | 1.00 | 0.11 | 0.68 | 0.11 |
| index: front-back, second-neighbour paths | 0.16 | 2.31 | 0.22 | 0.78 | 0.21 |
| index: left-right, second-neighbour paths | -0.12 | 0.63 | 0.27 | 0.58 | 0.25 |

**Moderate - Mild (A, front lobe added)**:
| quantity | Moderate - Mild (A, front lobe added) dB | Moderate - Mild (A, front lobe added) / yardstick | Moderate - Mild (A, front lobe added) / noise SD | Moderate - Mild (A, front lobe added) / clean ruler | Moderate - Mild (A, front lobe added) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.24 | 20.84 | 0.70 | 20.84 | 0.70 |
| C2 second-neighbour | 0.28 | 5.68 | 0.77 | 5.68 | 0.77 |
| C3 opposite | -0.44 | 3.53 | 1.24 | 3.53 | 1.24 |
| R31 | -0.19 | 1.37 | 4.78 | 1.37 | 1.37 |
| R21 | 0.52 | 8.71 | 7.86 | 8.71 | 7.86 |
| R32 | -0.71 | 9.44 | 9.22 | 9.44 | 9.22 |
| index: front-back, all paths | -0.07 | 1.04 | 0.11 | 0.60 | 0.11 |
| index: left-right, all paths | -0.11 | 2.08 | 0.21 | 1.08 | 0.21 |
| index: front-back, neighbour paths | -0.26 | 3.79 | 0.32 | 2.27 | 0.32 |
| index: left-right, neighbour paths | 0.02 | 0.29 | 0.03 | 0.20 | 0.03 |
| index: front-back, second-neighbour paths | 0.11 | 1.61 | 0.15 | 0.54 | 0.15 |
| index: left-right, second-neighbour paths | -0.30 | 1.57 | 0.68 | 1.43 | 0.62 |

**Mild (B)**:
| quantity | Mild (B) dB | Mild (B) / yardstick | Mild (B) / noise SD | Mild (B) / clean ruler | Mild (B) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | 0.05 | 4.24 | 0.14 | 4.24 | 0.14 |
| C2 second-neighbour | 0.62 | 12.69 | 1.73 | 12.69 | 1.73 |
| C3 opposite | -1.19 | 9.60 | 3.37 | 9.60 | 3.37 |
| R31 | -1.25 | 9.23 | 32.13 | 9.23 | 9.23 |
| R21 | 0.57 | 9.43 | 8.51 | 9.43 | 8.51 |
| R32 | -1.81 | 24.16 | 23.59 | 24.16 | 23.59 |
| index: front-back, all paths | 0.11 | 1.54 | 0.17 | 0.89 | 0.17 |
| index: left-right, all paths | 0.08 | 1.52 | 0.16 | 0.79 | 0.15 |
| index: front-back, neighbour paths | 0.04 | 0.65 | 0.06 | 0.39 | 0.05 |
| index: left-right, neighbour paths | 0.04 | 0.56 | 0.06 | 0.38 | 0.06 |
| index: front-back, second-neighbour paths | 0.17 | 2.39 | 0.23 | 0.81 | 0.22 |
| index: left-right, second-neighbour paths | 0.15 | 0.77 | 0.33 | 0.70 | 0.30 |

### Per-path values, cross-ratios and indices: how many exceed 3x the clean / measured ruler
| family | effect | n | n >= 3x clean ruler | n >= 3x measured ruler | best (clean) | best dB | best / clean ruler | best / measured ruler |
|---|---|---|---|---|---|---|---|---|
| path (reflection) | Mild (A) | 6 | 0 | 0 | path T3 refl. | -0.05 | 2.24 | 0.06 |
| path (reflection) | Moderate (A) | 6 | 1 | 0 | path T1 refl. | -0.07 | 3.01 | 0.08 |
| path (reflection) | Severe (A) | 6 | 4 | 0 | path T1 refl. | -0.09 | 3.94 | 0.10 |
| path (reflection) | Moderate - Mild (A, front lobe added) | 6 | 1 | 0 | path T1 refl. | -0.08 | 3.36 | 0.09 |
| path (reflection) | Mild (B) | 6 | 0 | 0 | path T3 refl. | -0.06 | 2.52 | 0.07 |
| path (neighbour) | Mild (A) | 6 | 0 | 0 | path T1-T6 | 0.11 | 0.93 | 0.16 |
| path (neighbour) | Moderate (A) | 6 | 0 | 0 | path T1-T6 | -0.28 | 2.46 | 0.43 |
| path (neighbour) | Severe (A) | 6 | 6 | 0 | path T2-T3 | -0.99 | 8.72 | 1.60 |
| path (neighbour) | Moderate - Mild (A, front lobe added) | 6 | 1 | 0 | path T1-T6 | -0.39 | 3.39 | 0.59 |
| path (neighbour) | Mild (B) | 6 | 0 | 0 | path T2-T3 | 0.11 | 0.93 | 0.17 |
| path (second-neighbour) | Mild (A) | 6 | 2 | 0 | path T2-T6 | 1.09 | 5.21 | 1.57 |
| path (second-neighbour) | Moderate (A) | 6 | 4 | 0 | path T1-T5 | 1.23 | 5.85 | 1.91 |
| path (second-neighbour) | Severe (A) | 6 | 6 | 0 | path T1-T3 | 1.83 | 8.71 | 2.71 |
| path (second-neighbour) | Moderate - Mild (A, front lobe added) | 6 | 0 | 0 | path T1-T5 | 0.61 | 2.92 | 0.95 |
| path (second-neighbour) | Mild (B) | 6 | 3 | 0 | path T2-T6 | 0.96 | 4.58 | 1.38 |
| path (opposite) | Mild (A) | 3 | 3 | 0 | path T3-T6 | -1.21 | 9.99 | 1.75 |
| path (opposite) | Moderate (A) | 3 | 3 | 0 | path T3-T6 | -1.52 | 12.52 | 2.19 |
| path (opposite) | Severe (A) | 3 | 3 | 0 | path T3-T6 | -1.64 | 13.54 | 2.36 |
| path (opposite) | Moderate - Mild (A, front lobe added) | 3 | 1 | 0 | path T1-T4 | -0.67 | 5.28 | 1.05 |
| path (opposite) | Mild (B) | 3 | 3 | 0 | path T3-T6 | -1.37 | 11.29 | 1.97 |
| cross-ratio | Mild (A) | 45 | 31 | 29 | chi T2T5·T3T6 / T2T6·T3T5 | -4.28 | 14.58 | 12.31 |
| cross-ratio | Moderate (A) | 45 | 36 | 35 | chi T2T5·T3T6 / T2T6·T3T5 | -5.21 | 17.75 | 14.98 |
| cross-ratio | Severe (A) | 45 | 29 | 23 | chi T1T3·T4T6 / T1T4·T3T6 | 6.93 | 22.89 | 20.63 |
| cross-ratio | Moderate - Mild (A, front lobe added) | 45 | 15 | 10 | chi T1T4·T5T6 / T1T5·T4T6 | -1.93 | 6.56 | 5.70 |
| cross-ratio | Mild (B) | 45 | 31 | 30 | chi T2T5·T3T6 / T2T6·T3T5 | -4.45 | 15.17 | 12.80 |
| asymmetry cross-ratio | Mild (A) | 45 | 2 | 0 | asym chi T2T5·T3T6 / T2T6·T3T5 | -0.94 | 3.14 | 2.87 |
| asymmetry cross-ratio | Moderate (A) | 45 | 0 | 0 | asym chi T2T4·T3T6 / T2T6·T3T4 | -0.69 | 2.31 | 2.03 |
| asymmetry cross-ratio | Severe (A) | 45 | 0 | 0 | asym chi T2T4·T3T5 / T2T5·T3T4 | -0.33 | 1.11 | 1.01 |
| asymmetry cross-ratio | Moderate - Mild (A, front lobe added) | 45 | 0 | 0 | asym chi T1T4·T3T5 / T1T5·T3T4 | -0.70 | 2.34 | 2.05 |
| asymmetry cross-ratio | Mild (B) | 45 | 0 | 0 | asym chi T1T4·T2T6 / T1T6·T2T4 | 0.86 | 2.89 | 2.55 |
| index | Mild (A) | 6 | 0 | 0 | index: front-back, all paths | 0.21 | 1.76 | 0.33 |
| index | Moderate (A) | 6 | 0 | 0 | index: front-back, second-neighbour paths | 0.42 | 2.00 | 0.55 |
| index | Severe (A) | 6 | 0 | 0 | index: front-back, all paths | 0.14 | 1.20 | 0.23 |
| index | Moderate - Mild (A, front lobe added) | 6 | 0 | 0 | index: front-back, neighbour paths | -0.26 | 2.27 | 0.32 |
| index | Mild (B) | 6 | 0 | 0 | index: front-back, all paths | 0.11 | 0.89 | 0.17 |

Front-lobe statistics (the localisation test: Moderate adds the frontal lobe to Mild):
| quantity | yardstick dB | symmetry floor of a difference dB | floor + noise dB | Moderate - Mild (A, front lobe added) dB | Moderate - Mild (A, front lobe added) / yardstick | Moderate - Mild (A, front lobe added) / clean ruler | Moderate - Mild (A, front lobe added) / measured ruler |
|---|---|---|---|---|---|---|---|
| index: front-back, all paths | 0.07 | 0.12 | 0.64 | -0.07 | 1.04 | 0.60 | 0.11 |
| index: front-back, neighbour paths | 0.07 | 0.11 | 0.81 | -0.26 | 3.79 | 2.27 | 0.32 |
| path T1-T2 | 0.05 | 0.11 | 0.61 | -0.31 | 6.39 | 2.69 | 0.50 |
| path T1-T6 | 0.04 | 0.11 | 0.65 | -0.39 | 8.87 | 3.39 | 0.59 |

Figure `figures/yardstick_maps.png`: per-path one-pass changes next to the lobe_A stage effects, same scale.

## 3. Frozen rule (unchanged) and localisation in each set
Fraction of noisy measurements given the expected label (typical noise, ±0.5 dB gain); full tables in each set's folder (`results/05_lobe/lobe_A/`, `lobe_B/`):
| rule | expected | design | lobe_A (stop rule 1) | lobe_B (stop rule 2) | lobe_v1 (unmatched) |
|---|---|---|---|---|---|
| binary_R31 | AD | Mild_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Mild_lobe_new | n/a | 1.000 | n/a |
| binary_R31 | AD | Moderate_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Severe_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| binary_R31 | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Mild | Mild_lobe | 0.413 | n/a | 0.413 |
| three | Mild | Mild_lobe_new | n/a | 0.690 | n/a |
| three | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Severe | Severe_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Mild_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Mild_lobe_new | n/a | 1.000 | n/a |
| three_merged | Mild+Moderate | Moderate_lobe | 1.000 | n/a | 1.000 |
| three_merged | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three_merged | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three_merged | Severe | Severe_lobe | 1.000 | n/a | 1.000 |

Same with ±2 dB gain and ±10° phase per port:
| rule | expected | design | lobe_A (stop rule 1) | lobe_B (stop rule 2) | lobe_v1 (unmatched) |
|---|---|---|---|---|---|
| binary_R31 | AD | Mild_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Mild_lobe_new | n/a | 1.000 | n/a |
| binary_R31 | AD | Moderate_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Severe_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| binary_R31 | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Mild | Mild_lobe | 0.430 | n/a | 0.430 |
| three | Mild | Mild_lobe_new | n/a | 0.717 | n/a |
| three | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Severe | Severe_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Mild_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Mild_lobe_new | n/a | 1.000 | n/a |
| three_merged | Mild+Moderate | Moderate_lobe | 1.000 | n/a | 1.000 |
| three_merged | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three_merged | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three_merged | Severe | Severe_lobe | 1.000 | n/a | 1.000 |

Front-back statistics per set (clean values; symmetry floor and gain noise as in Prompt 07):
| set | design | statistic | value dB | / symmetry floor | / floor+gain noise |
|---|---|---|---|---|---|
| lobe_v1 (unmatched) | Healthy_sliced | front-back, all paths | 0.00 | 0.00 | 0.00 |
| lobe_v1 (unmatched) | Healthy_sliced | front-back, neighbour paths | 0.00 | 0.00 | 0.00 |
| lobe_v1 (unmatched) | Healthy_sliced | front-back, second-neighbour paths | 0.00 | 0.00 | 0.00 |
| lobe_v1 (unmatched) | Mild_lobe | front-back, all paths | 0.14 | 1.67 | 0.31 |
| lobe_v1 (unmatched) | Mild_lobe | front-back, neighbour paths | 0.05 | 0.58 | 0.09 |
| lobe_v1 (unmatched) | Mild_lobe | front-back, second-neighbour paths | 0.24 | 1.59 | 0.42 |
| lobe_v1 (unmatched) | Moderate_lobe | front-back, all paths | 0.07 | 0.82 | 0.15 |
| lobe_v1 (unmatched) | Moderate_lobe | front-back, neighbour paths | -0.21 | -2.63 | -0.38 |
| lobe_v1 (unmatched) | Moderate_lobe | front-back, second-neighbour paths | 0.35 | 2.35 | 0.57 |
| lobe_v1 (unmatched) | Severe_lobe | front-back, all paths | 0.07 | 0.87 | 0.17 |
| lobe_v1 (unmatched) | Severe_lobe | front-back, neighbour paths | 0.05 | 0.68 | 0.11 |
| lobe_v1 (unmatched) | Severe_lobe | front-back, second-neighbour paths | 0.09 | 0.63 | 0.17 |
| lobe_v1 (unmatched) | Moderate - Mild | best asymmetry cross-ratio T1T4·T5T6 / T1T5·T4T6 | -0.69 | n/a | 2.26 |
| lobe_A (stop rule 1) | Healthy_sliced_new | front-back, all paths | 0.00 | 0.00 | 0.00 |
| lobe_A (stop rule 1) | Healthy_sliced_new | front-back, neighbour paths | 0.00 | 0.00 | 0.00 |
| lobe_A (stop rule 1) | Healthy_sliced_new | front-back, second-neighbour paths | 0.00 | 0.00 | 0.00 |
| lobe_A (stop rule 1) | Mild_lobe | front-back, all paths | 0.21 | 2.50 | 0.46 |
| lobe_A (stop rule 1) | Mild_lobe | front-back, neighbour paths | 0.11 | 1.43 | 0.21 |
| lobe_A (stop rule 1) | Mild_lobe | front-back, second-neighbour paths | 0.31 | 2.06 | 0.55 |
| lobe_A (stop rule 1) | Moderate_lobe | front-back, all paths | 0.14 | 1.64 | 0.29 |
| lobe_A (stop rule 1) | Moderate_lobe | front-back, neighbour paths | -0.14 | -1.78 | -0.26 |
| lobe_A (stop rule 1) | Moderate_lobe | front-back, second-neighbour paths | 0.42 | 2.83 | 0.69 |
| lobe_A (stop rule 1) | Severe_lobe | front-back, all paths | 0.14 | 1.70 | 0.33 |
| lobe_A (stop rule 1) | Severe_lobe | front-back, neighbour paths | 0.12 | 1.53 | 0.24 |
| lobe_A (stop rule 1) | Severe_lobe | front-back, second-neighbour paths | 0.16 | 1.10 | 0.29 |
| lobe_A (stop rule 1) | Moderate - Mild | best asymmetry cross-ratio T1T4·T5T6 / T1T5·T4T6 | -0.69 | n/a | 2.25 |
| lobe_B (stop rule 2) | Healthy_sliced | front-back, all paths | 0.00 | 0.00 | 0.00 |
| lobe_B (stop rule 2) | Healthy_sliced | front-back, neighbour paths | 0.00 | 0.00 | 0.00 |
| lobe_B (stop rule 2) | Healthy_sliced | front-back, second-neighbour paths | 0.00 | 0.00 | 0.00 |
| lobe_B (stop rule 2) | Mild_lobe_new | front-back, all paths | 0.11 | 1.62 | 0.24 |
| lobe_B (stop rule 2) | Mild_lobe_new | front-back, neighbour paths | 0.04 | 1.58 | 0.08 |
| lobe_B (stop rule 2) | Mild_lobe_new | front-back, second-neighbour paths | 0.17 | 1.43 | 0.31 |

## Claims (stop-rule matched)
| claim | number | baseline | verdict |
|---|---|---|---|
| the user's convergence table (frozen recipe) reproduces | R31/R21/R32 and margins match to 0.001 dB; plain-mean table to 0.01 dB | user's numbers (2026-10-04) | holds |
| one extra adaptive pass moves the ratios much less than Normal vs Mild | one pass: R31 0.135, R21 0.060, R32 0.075 dB; Normal - Mild R31 1.08-1.25 dB = 8x the R31 yardstick | one-pass yardstick | holds |
| frozen detection (R31) labels Healthy_sliced_new correctly in lobe_A (stop rule matched) | 1.00 correct (±2 dB/±10°: 1.00); margin to tau +0.53 dB = 3.9x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Mild_lobe correctly in lobe_A (stop rule matched) | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.55 dB = 4.1x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Moderate_lobe correctly in lobe_A (stop rule matched) | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.73 dB = 5.4x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Severe_lobe correctly in lobe_A (stop rule matched) | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.26 dB = 1.9x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds on this mesh; margin < 2x yardstick (one more pass could move it to the threshold) |
| frozen three_merged labels Mild_lobe as Mild+Moderate in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Moderate_lobe as Mild+Moderate in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Severe_lobe as Severe in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Healthy_sliced_new as Normal in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three labels Mild_lobe as Mild in lobe_A | 0.41 correct (±2 dB/±10°: 0.43) | frozen rule unchanged | retracted (reported as-is, no refitting) |
| frozen three labels Severe_lobe as Severe in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| the frozen three-class result on lobe-Mild is decided by the mesh (one extra pass) | Mild_lobe (pass 5, A) 0.41 vs Mild_lobe_new (pass 6, B) 0.69 correct; R21 +0.006 / +0.040 dB from the Normal|Mild boundary (-19.98) against a one-pass R21 change of 0.034 dB | frozen rule unchanged; one-pass yardstick | retracted for lobe-Mild in both sets (< 0.95); the difference between sets is mesh |
| localisation: frontal lobe visible in the front-back, neighbour paths index (Moderate - Mild (A, front lobe added)) | -0.26 dB = 3.8x yardstick, 2.3x clean ruler, 0.3x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement noise | clean: mesh-sensitive (2-3x); measured: not detectable (0.3x) |
| localisation: frontal lobe visible in the front-back, all paths index (Moderate - Mild (A, front lobe added)) | -0.07 dB = 1.0x yardstick, 0.6x clean ruler, 0.1x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement noise | clean: not separable from mesh (< 2x); measured: not detectable (0.1x) |
| front neighbour path T1-T2 changes when the frontal lobe is added (severity + location; not a location test alone) (Moderate - Mild (A, front lobe added)) | -0.31 dB = 6.4x yardstick, 2.7x clean ruler, 0.5x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement noise | clean: mesh-sensitive (2-3x); measured: not detectable (0.5x) |
| front neighbour path T1-T6 changes when the frontal lobe is added (severity + location; not a location test alone) (Moderate - Mild (A, front lobe added)) | -0.39 dB = 8.9x yardstick, 3.4x clean ruler, 0.6x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement noise | clean: exceeds mesh yardstick and symmetry floor (>= 3x); measured: not detectable (0.6x) |
| localisation: gain-invariant asymmetry cross-ratios see the frontal lobe (Moderate - Mild (A, front lobe added)) | 0/45 exceed 3x the clean ruler, 0/45 the measured ruler; best asym chi T1T4·T3T5 / T1T5·T3T4 -0.70 dB (2.3x clean, 2.0x measured) | max(one-pass yardstick (>= family rms), symmetry floor (+) noise) | not separable from mesh |
| raw cross-ratios separate Moderate from Mild (overall severity, not location) | 15/45 exceed 3x the clean ruler, 10/45 the measured ruler; best chi T1T4·T5T6 / T1T5·T4T6 -1.93 dB (6.6x clean, 5.7x measured) | max(one-pass yardstick (>= family rms), symmetry floor (+) noise) | exceeds mesh and noise; raw cross-ratios also change with overall severity, not location |

One solve per design and stop rule: within-simulation noise robustness, not generalisation.