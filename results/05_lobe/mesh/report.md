# Lobe convergence study: stop-rule matched sets and one-extra-pass mesh yardstick (code e1b3629)

HFSS Setup1 (user, from the convergence tables): adaptive at 3.4 GHz, Max Delta S 0.02, 30% refinement per pass, first-order basis, iterative solver; interpolating sweep 3.2-4.2 GHz, 201 points. Meshing is deterministic. Stop rule 1 = first pass with Delta S < 0.02; stop rule 2 = two consecutive passes.
Sets: **lobe_A** (stop rule 1; primary): Healthy_sliced_new, Mild_lobe, Moderate_lobe, Severe_lobe (+ the test designs LeftOnly_test_c3, MCI_lobe_c3, scored in `results/05_lobe/tests/`). **lobe_B** (stop rule 2): Healthy_sliced, Mild_lobe_new, Moderate_lobe_c3, Severe_lobe_c3. **lobe_v1** (Prompt 07, unmatched): Healthy_sliced (rule 2) with the rule-1 stages. lobe_A/lobe_B are *stop-rule matched*, not mesh-matched (element counts below). One solve per design and stop rule: within-simulation noise robustness, not generalisation.

| design | class | kind | set | stop_rule | passes | final_dS | elements |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | Normal | stage | lobe_v1 lobe_B | 2 | 7 | 0.0092 | 1349491 |
| Healthy_sliced_new | Normal | stage | lobe_A lobe_tests | 1 | 6 | 0.0155 | 1081728 |
| MCI_lobe_c3 | MCI | test | lobe_A lobe_tests | 1 | 6 | 0.01395 | 981160 |
| LeftOnly_test_c3 | Mild | test | lobe_A lobe_tests | 1 | 6 | 0.01469 | 941358 |
| Mild_lobe | Mild | stage | lobe_v1 lobe_A | 1 | 5 | 0.0186 | 739774 |
| Mild_lobe_new | Mild | stage | lobe_B | 2 | 6 | 0.015 | 878656 |
| Moderate_lobe | Moderate | stage | lobe_v1 lobe_A | 1 | 5 | 0.0194 | 796281 |
| Moderate_lobe_c3 | Moderate | stage | lobe_B | 2 | 6 | 0.01459 | 949865 |
| Severe_lobe | Severe | stage | lobe_v1 lobe_A | 1 | 5 | 0.02 | 690077 |
| Severe_lobe_c3 | Severe | stage | lobe_B | 2 | 6 | 0.01157 | 819294 |

## 0. Duplicates, glitch log, largest non-reciprocity per file
Re-solves with an unchanged stop rule reproduce the file (deterministic meshing); only one of each is in the manifest:
| file | same as | max |S_new - S| (linear) |
|---|---|---|
| new_with_slices_Moderate_lobe_new.s6p | new_with_slices_Moderate_lobe.s6p | 9.14e-09 |
| new_with_slices_Severe_lobe_new.s6p | new_with_slices_Severe_lobe.s6p | 1.65e-08 |

Points masked by the analysis (|Sij - Sji| > -30 dB of the pair's band level; Sij and Sji replaced by linear interpolation), all lobe files including duplicates. Log: `results/05_lobe/qc/masked_points.csv`. (The QC reports' own glitch count uses a different, local detector, |Sij - Sji|/|Sij| > -20 dB.)
| file | f_GHz | ports | path | type | |Sij| dB | |Sji| dB | reciprocity error dB (re band level) | masked |
|---|---|---|---|---|---|---|---|---|
| new_with_slices_Healthy_sliced.s6p | 3.52 | 1-4 | T1-T4 | opposite | -42.42 | -42.49 | -23.35 | True |
| new_with_slices_LeftOnly_test_c3.s6p | 3.85 | 2-5 | T3-T6 | opposite | -54.36 | -54.41 | -25.85 | True |
| new_with_slices_Mild_lobe_new.s6p | 3.85 | 3-6 | T2-T5 | opposite | -34.03 | -38.87 | 10.93 | True |
| new_with_slices_Moderate_lobe_c3.s6p | 3.85 | 1-4 | T1-T4 | opposite | -55.91 | -56.23 | -29.23 | True |
| new_with_slices_Severe_lobe.s6p | 3.85 | 2-5 | T3-T6 | opposite | -53.37 | -53.19 | -25.69 | True |
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
| new_with_slices_Severe_lobe_new.s6p | 3.85 | 2-5 | T3-T6 | opposite | -53.37 | -53.19 | -25.69 | True |

Largest magnitude non-reciprocity of each file and whether the frozen mask caught it (the mask threshold is part of the frozen recipe and is not changed):
| file | f_GHz | ports | path | |Sij| dB | |Sji| dB | max |Sij|/|Sji| dB | reciprocity error dB (re band level) | mask threshold dB | masked |
|---|---|---|---|---|---|---|---|---|---|
| new_with_slices_Healthy_sliced.s6p | 3.85 | 1-4 | T1-T4 | -59.87 | -59.55 | 0.32 | -35.34 | -30.00 | False |
| new_with_slices_Healthy_sliced_new.s6p | 3.85 | 1-4 | T1-T4 | -56.79 | -56.67 | 0.12 | -42.29 | -30.00 | False |
| new_with_slices_LeftOnly_test_c3.s6p | 3.85 | 2-5 | T3-T6 | -65.10 | -64.95 | 0.15 | -44.07 | -30.00 | False |
| new_with_slices_MCI_lobe_c3.s6p | 3.85 | 1-4 | T1-T4 | -55.57 | -55.62 | 0.05 | -47.74 | -30.00 | False |
| new_with_slices_Mild_lobe.s6p | 3.85 | 2-4 | T1-T3 | -64.36 | -63.98 | 0.38 | -32.56 | -30.00 | False |
| new_with_slices_Mild_lobe_new.s6p | 3.85 | 3-6 | T2-T5 | -34.03 | -38.87 | 4.84 | 10.93 | -30.00 | True |
| new_with_slices_Moderate_lobe.s6p | 3.85 | 2-5 | T3-T6 | -55.85 | -55.49 | 0.36 | -30.09 | -30.00 | False |
| new_with_slices_Moderate_lobe_c3.s6p | 3.85 | 1-4 | T1-T4 | -55.91 | -56.23 | 0.32 | -29.23 | -30.00 | True |
| new_with_slices_Moderate_lobe_new.s6p | 3.85 | 2-5 | T3-T6 | -55.85 | -55.49 | 0.36 | -30.09 | -30.00 | False |
| new_with_slices_Severe_lobe.s6p | 3.84 | 2-5 | T3-T6 | -63.82 | -64.21 | 0.39 | -36.86 | -30.00 | False |
| new_with_slices_Severe_lobe_c3.s6p | 3.83 | 3-6 | T2-T5 | -52.25 | -54.68 | 2.43 | -5.60 | -30.00 | True |
| new_with_slices_Severe_lobe_new.s6p | 3.84 | 2-5 | T3-T6 | -63.82 | -64.21 | 0.39 | -36.86 | -30.00 | False |

Effect of the mask on the frozen-recipe features (masked minus unmasked), files with masked points:
| file | masked points | C1 neighbour masked - unmasked dB | C2 second-neighbour masked - unmasked dB | C3 opposite masked - unmasked dB | R31 masked - unmasked dB | R21 masked - unmasked dB | R32 masked - unmasked dB |
|---|---|---|---|---|---|---|---|
| new_with_slices_Healthy_sliced.s6p | 1 | 0.000 | 0.000 | -0.039 | -0.038 | 0.000 | -0.038 |
| new_with_slices_LeftOnly_test_c3.s6p | 1 | -0.000 | -0.000 | -0.002 | -0.002 | -0.000 | -0.002 |
| new_with_slices_Mild_lobe_new.s6p | 1 | -0.000 | -0.000 | -0.335 | -0.319 | -0.000 | -0.319 |
| new_with_slices_Moderate_lobe_c3.s6p | 1 | 0.000 | 0.000 | -0.001 | -0.001 | 0.000 | -0.001 |
| new_with_slices_Severe_lobe.s6p | 1 | -0.000 | -0.000 | -0.005 | -0.005 | -0.000 | -0.005 |
| new_with_slices_Severe_lobe_c3.s6p | 16 | 0.000 | -0.008 | -0.006 | -0.005 | -0.009 | 0.003 |
| new_with_slices_Severe_lobe_new.s6p | 1 | -0.000 | -0.000 | -0.005 | -0.005 | -0.000 | -0.005 |

## 1. Reproduction of the user's tables
Plain mean (no masking; |S|^2 averaged over 201 points and the 12/12/6 equivalent pairs; kept for traceability only). The user's plain-mean R31 values (incl. Severe_lobe_c3 -15.57, Moderate_lobe_c3 -16.01) match to 0.005 dB:
| file | passes | C1 | C2 | C3 (opposite) | R31 | R21 | R32 |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | 7 | -36.87 | -57.37 | -51.44 | -14.57 | -20.50 | 5.93 |
| Healthy_sliced_new | 6 | -36.86 | -57.42 | -51.60 | -14.74 | -20.56 | 5.82 |
| MCI_lobe_c3 | 6 | -36.84 | -57.39 | -51.61 | -14.77 | -20.55 | 5.78 |
| LeftOnly_test_c3 | 6 | -36.87 | -57.06 | -52.31 | -15.44 | -20.19 | 4.76 |
| Mild_lobe | 5 | -36.82 | -56.78 | -52.63 | -15.81 | -19.96 | 4.15 |
| Mild_lobe_new | 6 | -36.82 | -56.75 | -52.33 | -15.51 | -19.93 | 4.43 |
| Moderate_lobe | 5 | -37.06 | -56.51 | -53.07 | -16.00 | -19.44 | 3.44 |
| Moderate_lobe_c3 | 6 | -37.07 | -56.51 | -53.08 | -16.01 | -19.44 | 3.43 |
| Severe_lobe | 5 | -37.70 | -55.70 | -53.23 | -15.52 | -18.00 | 2.47 |
| Severe_lobe_c3 | 6 | -37.70 | -55.58 | -53.28 | -15.57 | -17.88 | 2.31 |

Frozen-rule recipe (glitch masking, trapezoid band integration, geometric-mean ratios), used for every number below:
| file | passes | C1 neighbour | C2 second-neighbour | C3 opposite | R31 | R21 | R32 |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | 7 | -36.849 | -57.355 | -51.458 | -14.609 | -20.507 | 5.898 |
| Healthy_sliced_new | 6 | -36.837 | -57.404 | -51.581 | -14.744 | -20.567 | 5.823 |
| MCI_lobe_c3 | 6 | -36.817 | -57.370 | -51.590 | -14.773 | -20.555 | 5.783 |
| LeftOnly_test_c3 | 6 | -36.849 | -57.045 | -52.289 | -15.445 | -20.200 | 4.755 |
| Mild_lobe | 5 | -36.799 | -56.765 | -52.615 | -15.822 | -19.974 | 4.152 |
| Mild_lobe_new | 6 | -36.799 | -56.737 | -52.645 | -15.856 | -19.940 | 4.084 |
| Moderate_lobe | 5 | -37.042 | -56.488 | -53.051 | -16.008 | -19.451 | 3.443 |
| Moderate_lobe_c3 | 6 | -37.051 | -56.496 | -53.063 | -16.012 | -19.451 | 3.440 |
| Severe_lobe | 5 | -37.681 | -55.684 | -53.216 | -15.533 | -18.002 | 2.469 |
| Severe_lobe_c3 | 6 | -37.681 | -55.575 | -53.266 | -15.584 | -17.892 | 2.308 |

One extra adaptive pass (stop rule 1 -> 2), all four stages:
| quantity | Healthy 6->7 dB | Mild 5->6 dB | Moderate 5->6 dB | Severe 5->6 dB | yardstick dB |
|---|---|---|---|---|---|
| R31 | 0.135 | -0.034 | -0.004 | -0.051 | 0.135 |
| R21 | 0.060 | 0.034 | -0.000 | 0.110 | 0.110 |
| R32 | 0.075 | -0.068 | -0.004 | -0.161 | 0.161 |
| C1 neighbour | -0.012 | -0.001 | -0.009 | 0.000 | 0.012 |
| C2 second-neighbour | 0.049 | 0.028 | -0.009 | 0.109 | 0.109 |
| C3 opposite | 0.124 | -0.030 | -0.012 | -0.050 | 0.124 |

Normal - Mild R31: lobe_A 1.08 dB, lobe_B 1.25 dB, lobe_v1 (unmatched) 1.21 dB. Frozen detection threshold tau = -15.27 dB. Margins to tau:
| set | design | R31 dB | margin to tau dB | margin / R31 yardstick |
|---|---|---|---|---|
| lobe_A | Healthy_sliced_new | -14.744 | 0.529 | 3.913 |
| lobe_A | Mild_lobe | -15.822 | -0.549 | 4.064 |
| lobe_A | Moderate_lobe | -16.008 | -0.735 | 5.439 |
| lobe_A | Severe_lobe | -15.533 | -0.261 | 1.928 |
| lobe_B | Healthy_sliced | -14.609 | 0.664 | 4.913 |
| lobe_B | Mild_lobe_new | -15.856 | -0.583 | 4.317 |
| lobe_B | Moderate_lobe_c3 | -16.012 | -0.739 | 5.468 |
| lobe_B | Severe_lobe_c3 | -15.584 | -0.312 | 2.306 |

The plain-mean Mild 5->6 change of C3 (+0.30 dB) is the Mild_lobe_new 3.855 GHz glitch on T2-T5 (section 0); with masking it is -0.03 dB.

## 2. Mesh yardstick against every stage effect
Yardstick = the largest change of the four one-extra-pass pairs (Healthy 6->7, Mild 5->6, Moderate 5->6, Severe 5->6); for per-path values and cross-ratios at least the rms one-pass change of that family (asymmetry cross-ratio 0.127 dB, cross-ratio 0.162 dB, path (neighbour) 0.041 dB, path (opposite) 0.090 dB, path (reflection) 0.026 dB, path (second-neighbour) 0.108 dB). Symmetry floor = numerical asymmetry of the six mirror-symmetric stage designs (lobe_A and lobe_B), for a difference of two designs (x sqrt 2): asymmetry cross-ratio 0.291 dB, cross-ratio 0.287 dB, index 0.178 dB, path (neighbour) 0.111 dB, path (opposite) 0.117 dB, path (reflection) 0.008 dB, path (second-neighbour) 0.217 dB. Noise SD = typical noise and setup perturbation without per-port calibration error; spreads add ±0.5 dB, or ±2 dB and ±10°, per-port gain/phase (gain cancels in ratios and cross-ratios, not in paths or indices); all for a difference of two measurements. **Clean ruler** = max(yardstick, symmetry floor); **measured ruler** = max(yardstick, floor (+) ±0.5 dB spread). Stage effects are stage minus the healthy head of the same set; 'Moderate - Mild' adds the frontal lobe (and deepens the other lobes).
### Ring averages, ratios and front-back / left-right indices
| quantity | one pass Healthy 6->7 dB | one pass Mild 5->6 dB | one pass Moderate 5->6 dB | one pass Severe 5->6 dB | yardstick dB | symmetry floor of a difference dB | noise SD of a difference dB | spread ±0.5 dB of a difference dB | spread ±2 dB ±10° of a difference dB |
|---|---|---|---|---|---|---|---|---|---|
| C1 neighbour | -0.012 | -0.001 | -0.009 | 0.000 | 0.012 | 0.000 | 0.137 | 0.349 | 1.292 |
| C2 second-neighbour | 0.049 | 0.028 | -0.009 | 0.109 | 0.109 | 0.000 | 0.143 | 0.358 | 1.300 |
| C3 opposite | 0.124 | -0.030 | -0.012 | -0.050 | 0.124 | 0.000 | 0.139 | 0.352 | 1.302 |
| R31 | 0.135 | -0.034 | -0.004 | -0.051 | 0.135 | 0.000 | 0.036 | 0.039 | 0.039 |
| R21 | 0.060 | 0.034 | -0.000 | 0.110 | 0.110 | 0.000 | 0.059 | 0.067 | 0.070 |
| R32 | 0.075 | -0.068 | -0.004 | -0.161 | 0.161 | 0.000 | 0.064 | 0.077 | 0.078 |
| index: front-back, all paths | 0.070 | -0.034 | -0.018 | -0.057 | 0.070 | 0.122 | 0.276 | 0.626 | 2.362 |
| index: left-right, all paths | -0.052 | -0.004 | -0.037 | 0.064 | 0.064 | 0.102 | 0.237 | 0.510 | 1.986 |
| index: front-back, neighbour paths | 0.068 | -0.003 | -0.013 | -0.068 | 0.068 | 0.111 | 0.314 | 0.798 | 2.878 |
| index: left-right, neighbour paths | 0.040 | 0.063 | -0.017 | 0.048 | 0.063 | 0.091 | 0.259 | 0.562 | 2.202 |
| index: front-back, second-neighbour paths | 0.071 | -0.066 | -0.023 | -0.046 | 0.071 | 0.217 | 0.357 | 0.741 | 2.974 |
| index: left-right, second-neighbour paths | -0.191 | -0.106 | -0.066 | 0.087 | 0.191 | 0.217 | 0.223 | 0.441 | 1.664 |

**Mild (A)**:
| quantity | Mild (A) dB | Mild (A) / noise SD | Mild (A) / yardstick | Mild (A) / clean ruler | Mild (A) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | 0.04 | 0.28 | 3.29 | 3.29 | 0.11 |
| C2 second-neighbour | 0.64 | 4.46 | 5.87 | 5.87 | 1.79 |
| C3 opposite | -1.03 | 7.45 | 8.36 | 8.36 | 2.93 |
| R31 | -1.08 | 30.09 | 7.98 | 7.98 | 7.98 |
| R21 | 0.59 | 10.03 | 5.40 | 5.40 | 5.40 |
| R32 | -1.67 | 26.29 | 10.39 | 10.39 | 10.39 |
| index: front-back, all paths | 0.21 | 0.77 | 3.03 | 1.73 | 0.33 |
| index: left-right, all paths | 0.03 | 0.13 | 0.50 | 0.31 | 0.06 |
| index: front-back, neighbour paths | 0.11 | 0.37 | 1.69 | 1.03 | 0.14 |
| index: left-right, neighbour paths | 0.01 | 0.05 | 0.19 | 0.13 | 0.02 |
| index: front-back, second-neighbour paths | 0.31 | 0.86 | 4.32 | 1.41 | 0.40 |
| index: left-right, second-neighbour paths | 0.06 | 0.28 | 0.32 | 0.28 | 0.13 |

**Moderate (A)**:
| quantity | Moderate (A) dB | Moderate (A) / noise SD | Moderate (A) / yardstick | Moderate (A) / clean ruler | Moderate (A) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.21 | 1.50 | 17.55 | 17.55 | 0.59 |
| C2 second-neighbour | 0.92 | 6.39 | 8.42 | 8.42 | 2.56 |
| C3 opposite | -1.47 | 10.59 | 11.89 | 11.89 | 4.17 |
| R31 | -1.26 | 35.27 | 9.35 | 9.35 | 9.35 |
| R21 | 1.12 | 18.87 | 10.17 | 10.17 | 10.17 |
| R32 | -2.38 | 37.45 | 14.79 | 14.79 | 14.79 |
| index: front-back, all paths | 0.14 | 0.50 | 2.00 | 1.14 | 0.22 |
| index: left-right, all paths | -0.08 | 0.33 | 1.22 | 0.76 | 0.15 |
| index: front-back, neighbour paths | -0.14 | 0.46 | 2.10 | 1.29 | 0.18 |
| index: left-right, neighbour paths | 0.03 | 0.12 | 0.48 | 0.34 | 0.05 |
| index: front-back, second-neighbour paths | 0.42 | 1.18 | 5.93 | 1.94 | 0.55 |
| index: left-right, second-neighbour paths | -0.24 | 1.07 | 1.25 | 1.10 | 0.49 |

**Severe (A)**:
| quantity | Severe (A) dB | Severe (A) / noise SD | Severe (A) / yardstick | Severe (A) / clean ruler | Severe (A) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.84 | 6.15 | 72.19 | 72.19 | 2.42 |
| C2 second-neighbour | 1.72 | 12.00 | 15.81 | 15.81 | 4.81 |
| C3 opposite | -1.63 | 11.77 | 13.22 | 13.22 | 4.64 |
| R31 | -0.79 | 22.03 | 5.84 | 5.84 | 5.84 |
| R21 | 2.57 | 43.38 | 23.37 | 23.37 | 23.37 |
| R32 | -3.35 | 52.79 | 20.85 | 20.85 | 20.85 |
| index: front-back, all paths | 0.14 | 0.52 | 2.06 | 1.18 | 0.22 |
| index: left-right, all paths | -0.09 | 0.37 | 1.36 | 0.84 | 0.17 |
| index: front-back, neighbour paths | 0.12 | 0.39 | 1.81 | 1.11 | 0.15 |
| index: left-right, neighbour paths | -0.06 | 0.25 | 1.00 | 0.70 | 0.11 |
| index: front-back, second-neighbour paths | 0.16 | 0.46 | 2.31 | 0.76 | 0.21 |
| index: left-right, second-neighbour paths | -0.12 | 0.54 | 0.63 | 0.56 | 0.25 |

**Moderate - Mild (A, front lobe added)**:
| quantity | Moderate - Mild (A, front lobe added) dB | Moderate - Mild (A, front lobe added) / noise SD | Moderate - Mild (A, front lobe added) / yardstick | Moderate - Mild (A, front lobe added) / clean ruler | Moderate - Mild (A, front lobe added) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.24 | 1.78 | 20.84 | 20.84 | 0.70 |
| C2 second-neighbour | 0.28 | 1.93 | 2.54 | 2.54 | 0.77 |
| C3 opposite | -0.44 | 3.14 | 3.53 | 3.53 | 1.24 |
| R31 | -0.19 | 5.18 | 1.37 | 1.37 | 1.37 |
| R21 | 0.52 | 8.85 | 4.77 | 4.77 | 4.77 |
| R32 | -0.71 | 11.15 | 4.41 | 4.41 | 4.41 |
| index: front-back, all paths | -0.07 | 0.26 | 1.04 | 0.59 | 0.11 |
| index: left-right, all paths | -0.11 | 0.46 | 1.72 | 1.07 | 0.21 |
| index: front-back, neighbour paths | -0.26 | 0.82 | 3.79 | 2.32 | 0.32 |
| index: left-right, neighbour paths | 0.02 | 0.07 | 0.29 | 0.20 | 0.03 |
| index: front-back, second-neighbour paths | 0.11 | 0.32 | 1.61 | 0.53 | 0.15 |
| index: left-right, second-neighbour paths | -0.30 | 1.35 | 1.57 | 1.39 | 0.61 |

**Mild (B)**:
| quantity | Mild (B) dB | Mild (B) / noise SD | Mild (B) / yardstick | Mild (B) / clean ruler | Mild (B) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | 0.05 | 0.36 | 4.24 | 4.24 | 0.14 |
| C2 second-neighbour | 0.62 | 4.31 | 5.68 | 5.68 | 1.73 |
| C3 opposite | -1.19 | 8.55 | 9.60 | 9.60 | 3.37 |
| R31 | -1.25 | 34.81 | 9.23 | 9.23 | 9.23 |
| R21 | 0.57 | 9.58 | 5.16 | 5.16 | 5.16 |
| R32 | -1.81 | 28.54 | 11.28 | 11.28 | 11.28 |
| index: front-back, all paths | 0.11 | 0.39 | 1.54 | 0.88 | 0.17 |
| index: left-right, all paths | 0.08 | 0.34 | 1.26 | 0.78 | 0.15 |
| index: front-back, neighbour paths | 0.04 | 0.14 | 0.65 | 0.40 | 0.05 |
| index: left-right, neighbour paths | 0.04 | 0.14 | 0.56 | 0.39 | 0.06 |
| index: front-back, second-neighbour paths | 0.17 | 0.47 | 2.39 | 0.78 | 0.22 |
| index: left-right, second-neighbour paths | 0.15 | 0.66 | 0.77 | 0.68 | 0.30 |

**Moderate (B)**:
| quantity | Moderate (B) dB | Moderate (B) / noise SD | Moderate (B) / yardstick | Moderate (B) / clean ruler | Moderate (B) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.20 | 1.47 | 17.30 | 17.30 | 0.58 |
| C2 second-neighbour | 0.86 | 5.99 | 7.89 | 7.89 | 2.40 |
| C3 opposite | -1.61 | 11.56 | 12.99 | 12.99 | 4.56 |
| R31 | -1.40 | 39.15 | 10.38 | 10.38 | 10.38 |
| R21 | 1.06 | 17.85 | 9.62 | 9.62 | 9.62 |
| R32 | -2.46 | 38.69 | 15.28 | 15.28 | 15.28 |
| index: front-back, all paths | 0.05 | 0.19 | 0.74 | 0.42 | 0.08 |
| index: left-right, all paths | -0.06 | 0.26 | 0.97 | 0.60 | 0.12 |
| index: front-back, neighbour paths | -0.22 | 0.71 | 3.29 | 2.01 | 0.28 |
| index: left-right, neighbour paths | -0.03 | 0.10 | 0.41 | 0.29 | 0.05 |
| index: front-back, second-neighbour paths | 0.33 | 0.91 | 4.60 | 1.51 | 0.42 |
| index: left-right, second-neighbour paths | -0.11 | 0.51 | 0.60 | 0.53 | 0.23 |

**Severe (B)**:
| quantity | Severe (B) dB | Severe (B) / noise SD | Severe (B) / yardstick | Severe (B) / clean ruler | Severe (B) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.83 | 6.07 | 71.17 | 71.17 | 2.38 |
| C2 second-neighbour | 1.78 | 12.42 | 16.36 | 16.36 | 4.98 |
| C3 opposite | -1.81 | 13.03 | 14.63 | 14.63 | 5.13 |
| R31 | -0.98 | 27.23 | 7.22 | 7.22 | 7.22 |
| R21 | 2.61 | 44.22 | 23.83 | 23.83 | 23.83 |
| R32 | -3.59 | 56.50 | 22.32 | 22.32 | 22.32 |
| index: front-back, all paths | 0.02 | 0.06 | 0.24 | 0.14 | 0.03 |
| index: left-right, all paths | 0.03 | 0.12 | 0.46 | 0.29 | 0.06 |
| index: front-back, neighbour paths | -0.01 | 0.04 | 0.19 | 0.12 | 0.02 |
| index: left-right, neighbour paths | -0.06 | 0.21 | 0.87 | 0.61 | 0.10 |
| index: front-back, second-neighbour paths | 0.05 | 0.13 | 0.66 | 0.22 | 0.06 |
| index: left-right, second-neighbour paths | 0.16 | 0.70 | 0.82 | 0.72 | 0.32 |

**Moderate - Mild (B, front lobe added)**:
| quantity | Moderate - Mild (B, front lobe added) dB | Moderate - Mild (B, front lobe added) / noise SD | Moderate - Mild (B, front lobe added) / yardstick | Moderate - Mild (B, front lobe added) / clean ruler | Moderate - Mild (B, front lobe added) / measured ruler |
|---|---|---|---|---|---|
| C1 neighbour | -0.25 | 1.84 | 21.54 | 21.54 | 0.72 |
| C2 second-neighbour | 0.24 | 1.68 | 2.21 | 2.21 | 0.67 |
| C3 opposite | -0.42 | 3.01 | 3.38 | 3.38 | 1.19 |
| R31 | -0.16 | 4.34 | 1.15 | 1.15 | 1.15 |
| R21 | 0.49 | 8.27 | 4.46 | 4.46 | 4.46 |
| R32 | -0.64 | 10.15 | 4.01 | 4.01 | 4.01 |
| index: front-back, all paths | -0.06 | 0.20 | 0.80 | 0.46 | 0.09 |
| index: left-right, all paths | -0.14 | 0.60 | 2.22 | 1.38 | 0.27 |
| index: front-back, neighbour paths | -0.27 | 0.85 | 3.94 | 2.41 | 0.33 |
| index: left-right, neighbour paths | -0.06 | 0.24 | 0.97 | 0.68 | 0.11 |
| index: front-back, second-neighbour paths | 0.16 | 0.44 | 2.21 | 0.72 | 0.20 |
| index: left-right, second-neighbour paths | -0.26 | 1.17 | 1.37 | 1.21 | 0.53 |

### Per-path values, cross-ratios and indices: how many exceed 3x the clean / measured ruler
| family | effect | n | n >= 3x clean ruler | n >= 3x measured ruler | best (clean) | best dB | best / clean ruler | best / measured ruler |
|---|---|---|---|---|---|---|---|---|
| path (reflection) | Mild (A) | 6 | 0 | 0 | path T5 refl. | -0.06 | 1.77 | 0.07 |
| path (reflection) | Moderate (A) | 6 | 0 | 0 | path T1 refl. | -0.07 | 2.74 | 0.08 |
| path (reflection) | Severe (A) | 6 | 2 | 0 | path T1 refl. | -0.09 | 3.59 | 0.10 |
| path (reflection) | Moderate - Mild (A, front lobe added) | 6 | 1 | 0 | path T1 refl. | -0.08 | 3.06 | 0.09 |
| path (reflection) | Mild (B) | 6 | 0 | 0 | path T5 refl. | -0.07 | 2.06 | 0.08 |
| path (reflection) | Moderate (B) | 6 | 0 | 0 | path T1 refl. | -0.08 | 2.99 | 0.09 |
| path (reflection) | Severe (B) | 6 | 3 | 0 | path T1 refl. | -0.10 | 3.98 | 0.12 |
| path (reflection) | Moderate - Mild (B, front lobe added) | 6 | 0 | 0 | path T1 refl. | -0.08 | 2.92 | 0.08 |
| path (neighbour) | Mild (A) | 6 | 0 | 0 | path T1-T6 | 0.11 | 0.95 | 0.16 |
| path (neighbour) | Moderate (A) | 6 | 0 | 0 | path T1-T6 | -0.28 | 2.51 | 0.43 |
| path (neighbour) | Severe (A) | 6 | 6 | 0 | path T2-T3 | -0.99 | 8.91 | 1.60 |
| path (neighbour) | Moderate - Mild (A, front lobe added) | 6 | 1 | 0 | path T1-T6 | -0.39 | 3.47 | 0.59 |
| path (neighbour) | Mild (B) | 6 | 0 | 0 | path T2-T3 | 0.11 | 0.95 | 0.17 |
| path (neighbour) | Moderate (B) | 6 | 1 | 0 | path T1-T6 | -0.35 | 3.11 | 0.53 |
| path (neighbour) | Severe (B) | 6 | 6 | 0 | path T2-T3 | -0.91 | 8.21 | 1.48 |
| path (neighbour) | Moderate - Mild (B, front lobe added) | 6 | 3 | 0 | path T2-T3 | -0.40 | 3.59 | 0.65 |
| path (second-neighbour) | Mild (A) | 6 | 2 | 0 | path T2-T6 | 1.09 | 5.04 | 1.57 |
| path (second-neighbour) | Moderate (A) | 6 | 4 | 0 | path T1-T5 | 1.23 | 5.67 | 1.90 |
| path (second-neighbour) | Severe (A) | 6 | 6 | 0 | path T1-T3 | 1.83 | 8.45 | 2.70 |
| path (second-neighbour) | Moderate - Mild (A, front lobe added) | 6 | 0 | 0 | path T1-T5 | 0.61 | 2.83 | 0.95 |
| path (second-neighbour) | Mild (B) | 6 | 3 | 0 | path T2-T6 | 0.96 | 4.44 | 1.38 |
| path (second-neighbour) | Moderate (B) | 6 | 5 | 0 | path T1-T5 | 1.11 | 5.12 | 1.72 |
| path (second-neighbour) | Severe (B) | 6 | 6 | 0 | path T2-T6 | 2.02 | 9.29 | 2.88 |
| path (second-neighbour) | Moderate - Mild (B, front lobe added) | 6 | 0 | 0 | path T1-T5 | 0.62 | 2.86 | 0.96 |
| path (opposite) | Mild (A) | 3 | 3 | 0 | path T3-T6 | -1.21 | 9.99 | 1.74 |
| path (opposite) | Moderate (A) | 3 | 3 | 0 | path T3-T6 | -1.52 | 12.52 | 2.17 |
| path (opposite) | Severe (A) | 3 | 3 | 0 | path T3-T6 | -1.64 | 13.54 | 2.35 |
| path (opposite) | Moderate - Mild (A, front lobe added) | 3 | 1 | 0 | path T1-T4 | -0.67 | 5.28 | 1.05 |
| path (opposite) | Mild (B) | 3 | 3 | 0 | path T3-T6 | -1.37 | 11.29 | 1.96 |
| path (opposite) | Moderate (B) | 3 | 3 | 0 | path T3-T6 | -1.72 | 14.22 | 2.47 |
| path (opposite) | Severe (B) | 3 | 3 | 1 | path T1-T4 | -1.91 | 15.14 | 3.00 |
| path (opposite) | Moderate - Mild (B, front lobe added) | 3 | 1 | 0 | path T1-T4 | -0.73 | 5.78 | 1.15 |
| cross-ratio | Mild (A) | 45 | 31 | 29 | chi T2T5·T3T6 / T2T6·T3T5 | -4.28 | 12.39 | 12.39 |
| cross-ratio | Moderate (A) | 45 | 36 | 35 | chi T2T5·T3T6 / T2T6·T3T5 | -5.21 | 15.09 | 15.09 |
| cross-ratio | Severe (A) | 45 | 29 | 25 | chi T1T3·T4T6 / T1T4·T3T6 | 6.93 | 22.89 | 20.96 |
| cross-ratio | Moderate - Mild (A, front lobe added) | 45 | 15 | 10 | chi T1T4·T5T6 / T1T5·T4T6 | -1.93 | 6.70 | 5.79 |
| cross-ratio | Mild (B) | 45 | 31 | 30 | chi T2T5·T3T6 / T2T6·T3T5 | -4.45 | 12.90 | 12.90 |
| cross-ratio | Moderate (B) | 45 | 37 | 37 | chi T2T5·T3T6 / T2T6·T3T5 | -5.40 | 15.65 | 15.65 |
| cross-ratio | Severe (B) | 45 | 32 | 30 | chi T1T3·T4T6 / T1T4·T3T6 | 7.31 | 24.14 | 22.11 |
| cross-ratio | Moderate - Mild (B, front lobe added) | 45 | 13 | 10 | chi T1T4·T5T6 / T1T5·T4T6 | -1.65 | 5.74 | 4.96 |
| asymmetry cross-ratio | Mild (A) | 45 | 2 | 0 | asym chi T2T5·T3T6 / T2T6·T3T5 | -0.94 | 3.22 | 2.93 |
| asymmetry cross-ratio | Moderate (A) | 45 | 0 | 0 | asym chi T2T4·T3T6 / T2T6·T3T4 | -0.69 | 2.36 | 2.07 |
| asymmetry cross-ratio | Severe (A) | 45 | 0 | 0 | asym chi T2T4·T3T5 / T2T5·T3T4 | -0.33 | 1.13 | 1.03 |
| asymmetry cross-ratio | Moderate - Mild (A, front lobe added) | 45 | 0 | 0 | asym chi T1T4·T3T5 / T1T5·T3T4 | -0.70 | 2.40 | 2.08 |
| asymmetry cross-ratio | Mild (B) | 45 | 0 | 0 | asym chi T1T4·T2T6 / T1T6·T2T4 | 0.86 | 2.95 | 2.60 |
| asymmetry cross-ratio | Moderate (B) | 45 | 0 | 0 | asym chi T2T4·T3T6 / T2T6·T3T4 | -0.64 | 2.18 | 1.91 |
| asymmetry cross-ratio | Severe (B) | 45 | 0 | 0 | asym chi T1T3·T5T6 / T1T6·T3T5 | 0.59 | 2.02 | 1.60 |
| asymmetry cross-ratio | Moderate - Mild (B, front lobe added) | 45 | 0 | 0 | asym chi T1T4·T3T5 / T1T5·T3T4 | -0.73 | 2.51 | 2.18 |
| index | Mild (A) | 6 | 0 | 0 | index: front-back, all paths | 0.21 | 1.73 | 0.33 |
| index | Moderate (A) | 6 | 0 | 0 | index: front-back, second-neighbour paths | 0.42 | 1.94 | 0.55 |
| index | Severe (A) | 6 | 0 | 0 | index: front-back, all paths | 0.14 | 1.18 | 0.22 |
| index | Moderate - Mild (A, front lobe added) | 6 | 0 | 0 | index: front-back, neighbour paths | -0.26 | 2.32 | 0.32 |
| index | Mild (B) | 6 | 0 | 0 | index: front-back, all paths | 0.11 | 0.88 | 0.17 |
| index | Moderate (B) | 6 | 0 | 0 | index: front-back, neighbour paths | -0.22 | 2.01 | 0.28 |
| index | Severe (B) | 6 | 0 | 0 | index: left-right, second-neighbour paths | 0.16 | 0.72 | 0.32 |
| index | Moderate - Mild (B, front lobe added) | 6 | 0 | 0 | index: front-back, neighbour paths | -0.27 | 2.41 | 0.33 |

Front-lobe statistics, Moderate - Mild (A, front lobe added):
| quantity | yardstick dB | symmetry floor of a difference dB | Moderate - Mild (A, front lobe added) dB | Moderate - Mild (A, front lobe added) / yardstick | Moderate - Mild (A, front lobe added) / clean ruler | Moderate - Mild (A, front lobe added) / measured ruler |
|---|---|---|---|---|---|---|
| index: front-back, all paths | 0.07 | 0.12 | -0.07 | 1.04 | 0.59 | 0.11 |
| index: front-back, neighbour paths | 0.07 | 0.11 | -0.26 | 3.79 | 2.32 | 0.32 |
| path T1-T2 | 0.05 | 0.11 | -0.31 | 6.39 | 2.75 | 0.50 |
| path T1-T6 | 0.09 | 0.11 | -0.39 | 4.11 | 3.47 | 0.59 |

Front-lobe statistics, Moderate - Mild (B, front lobe added):
| quantity | yardstick dB | symmetry floor of a difference dB | Moderate - Mild (B, front lobe added) dB | Moderate - Mild (B, front lobe added) / yardstick | Moderate - Mild (B, front lobe added) / clean ruler | Moderate - Mild (B, front lobe added) / measured ruler |
|---|---|---|---|---|---|---|
| index: front-back, all paths | 0.07 | 0.12 | -0.06 | 0.80 | 0.46 | 0.09 |
| index: front-back, neighbour paths | 0.07 | 0.11 | -0.27 | 3.94 | 2.41 | 0.33 |
| path T1-T2 | 0.05 | 0.11 | -0.35 | 7.24 | 3.12 | 0.57 |
| path T1-T6 | 0.09 | 0.11 | -0.39 | 4.19 | 3.54 | 0.60 |

Figure `figures/yardstick_maps.png`: per-path one-pass changes of all four stages next to the stage effects, same colour scale.

## 3. Frozen rule (unchanged) and localisation in each set
Fraction of noisy measurements given the expected label (typical noise, ±0.5 dB gain); full tables in each set's folder (`results/05_lobe/lobe_A/`, `lobe_B/`):
| rule | expected | design | lobe_A (stop rule 1) | lobe_B (stop rule 2) | lobe_v1 (unmatched) |
|---|---|---|---|---|---|
| binary_R31 | AD | Mild_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Mild_lobe_new | n/a | 1.000 | n/a |
| binary_R31 | AD | Moderate_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Moderate_lobe_c3 | n/a | 1.000 | n/a |
| binary_R31 | AD | Severe_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Severe_lobe_c3 | n/a | 1.000 | n/a |
| binary_R31 | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| binary_R31 | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Mild | Mild_lobe | 0.413 | n/a | 0.413 |
| three | Mild | Mild_lobe_new | n/a | 0.690 | n/a |
| three | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Severe | Severe_lobe | 1.000 | n/a | 1.000 |
| three | Severe | Severe_lobe_c3 | n/a | 1.000 | n/a |
| three_merged | Mild+Moderate | Mild_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Mild_lobe_new | n/a | 1.000 | n/a |
| three_merged | Mild+Moderate | Moderate_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Moderate_lobe_c3 | n/a | 1.000 | n/a |
| three_merged | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three_merged | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three_merged | Severe | Severe_lobe | 1.000 | n/a | 1.000 |
| three_merged | Severe | Severe_lobe_c3 | n/a | 1.000 | n/a |

Same with ±2 dB gain and ±10° phase per port:
| rule | expected | design | lobe_A (stop rule 1) | lobe_B (stop rule 2) | lobe_v1 (unmatched) |
|---|---|---|---|---|---|
| binary_R31 | AD | Mild_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Mild_lobe_new | n/a | 1.000 | n/a |
| binary_R31 | AD | Moderate_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Moderate_lobe_c3 | n/a | 1.000 | n/a |
| binary_R31 | AD | Severe_lobe | 1.000 | n/a | 1.000 |
| binary_R31 | AD | Severe_lobe_c3 | n/a | 1.000 | n/a |
| binary_R31 | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| binary_R31 | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Mild | Mild_lobe | 0.430 | n/a | 0.430 |
| three | Mild | Mild_lobe_new | n/a | 0.717 | n/a |
| three | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three | Severe | Severe_lobe | 1.000 | n/a | 1.000 |
| three | Severe | Severe_lobe_c3 | n/a | 1.000 | n/a |
| three_merged | Mild+Moderate | Mild_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Mild_lobe_new | n/a | 1.000 | n/a |
| three_merged | Mild+Moderate | Moderate_lobe | 1.000 | n/a | 1.000 |
| three_merged | Mild+Moderate | Moderate_lobe_c3 | n/a | 1.000 | n/a |
| three_merged | Normal | Healthy_sliced | n/a | 1.000 | 1.000 |
| three_merged | Normal | Healthy_sliced_new | 1.000 | n/a | n/a |
| three_merged | Severe | Severe_lobe | 1.000 | n/a | 1.000 |
| three_merged | Severe | Severe_lobe_c3 | n/a | 1.000 | n/a |

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
| lobe_B (stop rule 2) | Mild_lobe_new | front-back, all paths | 0.11 | 1.22 | 0.23 |
| lobe_B (stop rule 2) | Mild_lobe_new | front-back, neighbour paths | 0.04 | 0.58 | 0.08 |
| lobe_B (stop rule 2) | Mild_lobe_new | front-back, second-neighbour paths | 0.17 | 1.07 | 0.30 |
| lobe_B (stop rule 2) | Moderate_lobe_c3 | front-back, all paths | 0.05 | 0.58 | 0.11 |
| lobe_B (stop rule 2) | Moderate_lobe_c3 | front-back, neighbour paths | -0.22 | -2.91 | -0.40 |
| lobe_B (stop rule 2) | Moderate_lobe_c3 | front-back, second-neighbour paths | 0.33 | 2.07 | 0.53 |
| lobe_B (stop rule 2) | Severe_lobe_c3 | front-back, all paths | 0.02 | 0.19 | 0.04 |
| lobe_B (stop rule 2) | Severe_lobe_c3 | front-back, neighbour paths | -0.01 | -0.17 | -0.03 |
| lobe_B (stop rule 2) | Severe_lobe_c3 | front-back, second-neighbour paths | 0.05 | 0.30 | 0.08 |
| lobe_B (stop rule 2) | Moderate - Mild | best asymmetry cross-ratio T1T4·T3T5 / T1T5·T3T4 | -0.73 | n/a | 2.34 |

## Claims (stop-rule matched)
| claim | number | baseline | verdict |
|---|---|---|---|
| the user's convergence tables reproduce | frozen recipe R31 to 0.001 dB; plain-mean R31 (all eight solves, incl. the c3 files) to 0.005 dB | user's numbers (2026-10-04) | holds |
| one extra adaptive pass (all four stages) moves the ratios much less than Normal vs Mild | one-pass yardstick: R31 0.135, R21 0.110, R32 0.161 dB; Normal - Mild R31 1.08-1.25 dB = 8-9x the R31 yardstick | one-pass yardstick (4 pairs) | holds |
| frozen detection (R31) labels Healthy_sliced_new correctly in lobe_A | 1.00 correct (±2 dB/±10°: 1.00); margin to tau +0.53 dB = 3.9x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Mild_lobe correctly in lobe_A | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.55 dB = 4.1x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Moderate_lobe correctly in lobe_A | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.73 dB = 5.4x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Severe_lobe correctly in lobe_A | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.26 dB = 1.9x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds on this mesh; margin < 2x yardstick |
| frozen three_merged labels Mild_lobe as Mild+Moderate in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Moderate_lobe as Mild+Moderate in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Severe_lobe as Severe in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Healthy_sliced_new as Normal in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three labels Mild_lobe as Mild in lobe_A | 0.41 correct (±2 dB/±10°: 0.43) | frozen rule unchanged | retracted (reported as-is, no refitting) |
| frozen three labels Severe_lobe as Severe in lobe_A | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen detection (R31) labels Healthy_sliced correctly in lobe_B | 1.00 correct (±2 dB/±10°: 1.00); margin to tau +0.66 dB = 4.9x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Mild_lobe_new correctly in lobe_B | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.58 dB = 4.3x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Moderate_lobe_c3 correctly in lobe_B | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.74 dB = 5.5x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds |
| frozen detection (R31) labels Severe_lobe_c3 correctly in lobe_B | 1.00 correct (±2 dB/±10°: 1.00); margin to tau -0.31 dB = 2.3x yardstick | frozen rule unchanged; R31 one-pass yardstick | holds; margin mesh-sensitive (2-3x) |
| frozen three_merged labels Mild_lobe_new as Mild+Moderate in lobe_B | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Moderate_lobe_c3 as Mild+Moderate in lobe_B | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Severe_lobe_c3 as Severe in lobe_B | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three_merged labels Healthy_sliced as Normal in lobe_B | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| frozen three labels Mild_lobe_new as Mild in lobe_B | 0.69 correct (±2 dB/±10°: 0.72) | frozen rule unchanged | weakened |
| frozen three labels Severe_lobe_c3 as Severe in lobe_B | 1.00 correct (±2 dB/±10°: 1.00) | frozen rule unchanged | holds |
| the frozen three-class result on lobe-Mild is decided by the mesh (one extra pass) | Mild_lobe (pass 5, A) 0.41 vs Mild_lobe_new (pass 6, B) 0.69 correct; R21 +0.006 / +0.040 dB from the Normal|Mild boundary (-19.98) against an R21 yardstick of 0.110 dB | frozen rule unchanged; one-pass yardstick | retracted for lobe-Mild (A 0.41: retracted; B 0.69: weakened; both < 0.95); the difference between the sets is mesh |
| localisation: frontal lobe visible in the front-back, neighbour paths index (Moderate - Mild (A, front lobe added)) | -0.26 dB = 3.8x yardstick, 2.3x clean ruler, 0.3x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: mesh-sensitive (2-3x); measured: not detectable (0.3x) |
| localisation: frontal lobe visible in the front-back, all paths index (Moderate - Mild (A, front lobe added)) | -0.07 dB = 1.0x yardstick, 0.6x clean ruler, 0.1x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: not separable from mesh (< 2x); measured: not detectable (0.1x) |
| front neighbour path T1-T2 changes when the frontal lobe is added (severity + location; not a location test alone) (Moderate - Mild (A, front lobe added)) | -0.31 dB = 6.4x yardstick, 2.8x clean ruler, 0.5x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: mesh-sensitive (2-3x); measured: not detectable (0.5x) |
| front neighbour path T1-T6 changes when the frontal lobe is added (severity + location; not a location test alone) (Moderate - Mild (A, front lobe added)) | -0.39 dB = 4.1x yardstick, 3.5x clean ruler, 0.6x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: exceeds mesh yardstick and symmetry floor (>= 3x); measured: not detectable (0.6x) |
| localisation: gain-invariant asymmetry cross-ratios see the frontal lobe (Moderate - Mild (A, front lobe added)) | 0/45 exceed 3x the clean ruler, 0/45 the measured ruler; best asym chi T1T4·T3T5 / T1T5·T3T4 -0.70 dB (2.4x clean, 2.1x measured) | max(one-pass yardstick (>= family rms), symmetry floor (+) spread) | not separable from mesh |
| raw cross-ratios separate Moderate from Mild (Moderate - Mild (A, front lobe added); overall severity, not location) | 15/45 exceed 3x the clean ruler, 10/45 the measured ruler; best chi T1T4·T5T6 / T1T5·T4T6 -1.93 dB (6.7x clean, 5.8x measured) | max(one-pass yardstick (>= family rms), symmetry floor (+) spread) | exceeds mesh and noise; raw cross-ratios also change with overall severity, not location |
| localisation: frontal lobe visible in the front-back, neighbour paths index (Moderate - Mild (B, front lobe added)) | -0.27 dB = 3.9x yardstick, 2.4x clean ruler, 0.3x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: mesh-sensitive (2-3x); measured: not detectable (0.3x) |
| localisation: frontal lobe visible in the front-back, all paths index (Moderate - Mild (B, front lobe added)) | -0.06 dB = 0.8x yardstick, 0.5x clean ruler, 0.1x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: not separable from mesh (< 2x); measured: not detectable (0.1x) |
| front neighbour path T1-T2 changes when the frontal lobe is added (severity + location; not a location test alone) (Moderate - Mild (B, front lobe added)) | -0.35 dB = 7.2x yardstick, 3.1x clean ruler, 0.6x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: exceeds mesh yardstick and symmetry floor (>= 3x); measured: not detectable (0.6x) |
| front neighbour path T1-T6 changes when the frontal lobe is added (severity + location; not a location test alone) (Moderate - Mild (B, front lobe added)) | -0.39 dB = 4.2x yardstick, 3.5x clean ruler, 0.6x measured ruler (±0.5 dB gain) | one-pass yardstick; symmetry floor; measurement-error spread | clean: exceeds mesh yardstick and symmetry floor (>= 3x); measured: not detectable (0.6x) |
| localisation: gain-invariant asymmetry cross-ratios see the frontal lobe (Moderate - Mild (B, front lobe added)) | 0/45 exceed 3x the clean ruler, 0/45 the measured ruler; best asym chi T1T4·T3T5 / T1T5·T3T4 -0.73 dB (2.5x clean, 2.2x measured) | max(one-pass yardstick (>= family rms), symmetry floor (+) spread) | not separable from mesh |
| raw cross-ratios separate Moderate from Mild (Moderate - Mild (B, front lobe added); overall severity, not location) | 13/45 exceed 3x the clean ruler, 10/45 the measured ruler; best chi T1T4·T5T6 / T1T5·T4T6 -1.65 dB (5.7x clean, 5.0x measured) | max(one-pass yardstick (>= family rms), symmetry floor (+) spread) | exceeds mesh and noise; raw cross-ratios also change with overall severity, not location |

One solve per design and stop rule: within-simulation noise robustness, not generalisation.