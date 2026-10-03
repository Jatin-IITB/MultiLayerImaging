# Lobe-sector phantom (set lobe_v1): analysis (code bac41d4)

Designs: Healthy_sliced, Mild_lobe, Moderate_lobe, Severe_lobe (3.2-4.2 GHz, 201 points). One solve per design: within-simulation noise robustness, not generalisation. Noise unless stated: typical profile + setup perturbation + per-port gain ±0.5 dB. Antennas in ring order T1..T6 = Frontal, Temporal L, Parietal L, Occipital, Parietal R, Temporal R.

## 3.1 QC and symmetry floors
Parsing, passivity, reciprocity, glitches and the port-map search: `results/05_lobe/qc/qc_report.md` (all four files pass; the port map T4,T3,T2,T1,T6,T5 ranks 1st of 60 in every file; no glitches).
Circulant floor = spread of equivalent paths in Healthy_sliced (should be identical by symmetry):
| floor | path | band-power SD dB | band-power max-min dB | median over f of per-frequency SD dB |
|---|---|---|---|---|
| circulant (Healthy_sliced) | reflection | 0.003 | 0.009 | 0.024 |
| circulant (Healthy_sliced) | neighbour | 0.028 | 0.076 | 0.058 |
| circulant (Healthy_sliced) | second-neighbour | 0.095 | 0.292 | 0.102 |
| circulant (Healthy_sliced) | opposite | 0.054 | 0.112 | 0.066 |

Mirror floor = difference between mirror-image paths (T2<->T6, T3<->T5) in the mirror-symmetric designs:
| design | path | mirror pairs | band-power rms diff dB | median over f of rms diff dB |
|---|---|---|---|---|
| Healthy_sliced | reflection | 2 | 0.003 | 0.028 |
| Healthy_sliced | neighbour | 3 | 0.036 | 0.094 |
| Healthy_sliced | second-neighbour | 2 | 0.069 | 0.139 |
| Healthy_sliced | opposite | 1 | 0.017 | 0.046 |
| Mild_lobe | reflection | 2 | 0.004 | 0.062 |
| Mild_lobe | neighbour | 3 | 0.073 | 0.113 |
| Mild_lobe | second-neighbour | 2 | 0.218 | 0.367 |
| Mild_lobe | opposite | 1 | 0.106 | 0.101 |
| Moderate_lobe | reflection | 2 | 0.011 | 0.081 |
| Moderate_lobe | neighbour | 3 | 0.061 | 0.172 |
| Moderate_lobe | second-neighbour | 2 | 0.271 | 0.201 |
| Moderate_lobe | opposite | 1 | 0.091 | 0.070 |
| Severe_lobe | reflection | 2 | 0.013 | 0.050 |
| Severe_lobe | neighbour | 3 | 0.173 | 0.075 |
| Severe_lobe | second-neighbour | 2 | 0.106 | 0.123 |
| Severe_lobe | opposite | 1 | 0.067 | 0.051 |

Pooled mirror floor over Mild/Moderate/Severe band powers: **0.128 dB** (rms). Per-path numerical SD of the staged designs (mirror rms / sqrt 2), used as the noise ruler for every asymmetry claim: reflection 0.007 dB, neighbour 0.080 dB, second-neighbour 0.149 dB, opposite 0.063 dB. The staged designs are 2-5x less symmetric than Healthy_sliced, so the healthy floor alone would overstate asymmetry significance.

## 3.2 Is Healthy_sliced the same head as the v2 Normal?
| feature | Healthy_sliced | new_Healthy (v2) | difference dB | / v2 solve SD | sliced antenna-spread SE dB | / sliced antenna-spread SE |
|---|---|---|---|---|---|---|
| R31 | -14.609 | -14.674 | 0.065 | 0.442 | 0.028 | 2.328 |
| R21 | -20.507 | -20.722 | 0.215 | 1.338 | 0.042 | 5.087 |
| R32 | 5.898 | 6.048 | -0.150 | -1.164 | 0.045 | -3.344 |
| k0_band | -3.647 | -3.613 | -0.033 | -0.462 | 0.001 | -26.720 |
| k1_band | -36.849 | -36.990 | 0.141 | 0.581 | 0.007 | 19.657 |
| k2_band | -57.355 | -57.710 | 0.355 | 1.544 | 0.027 | 13.236 |
| k3_band | -51.458 | -51.658 | 0.200 | 0.636 | 0.022 | 9.062 |
| logN | -2.459 | -2.484 | 0.025 | 0.464 | 0.001 | 26.788 |

Across all 89 ring-symmetrised features: 48% within 1x, 78% within 2x, 93% within 3x the v2 solve-to-solve SD; largest: k3_sb4.05, k1_sb3.60, k3_sb4.10, k0_sb3.35, k3_sb4.00. The resonance moved by +18.9 MHz (3640 -> 3659 MHz) and the notch is shallower (-21 vs -34…-39 dB). Verdict on the classifier features above: **equivalent**. Caveat: the v2 skull inner radius (hidden tool Brain_sphere_1) is unknown, so a small geometry difference cannot be excluded.

## 3.3 Frozen rule applied unchanged to the lobe designs
`results/04/frozen_rule.json` (commit 2baddee) and the gain-invariant gate (Normal window fitted on the v2 Normal, floor limit from the v2 thresholds) are applied without refitting to 300 noisy measurements per design and condition. This is the first test on a different disease geometry (regional instead of uniform atrophy) in the same head. One solve per design: within-simulation noise robustness, not generalisation.
Fraction of measurements given the expected label:
| condition | rule | design | expected | fraction correct | UNCERTAIN | INVALID |
|---|---|---|---|---|---|---|
| typical, ±0.5 dB gain | binary_R31 | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | binary_R31 | Mild_lobe | AD | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Mild_lobe | AD | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | binary_R31 | Moderate_lobe | AD | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Moderate_lobe | AD | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | binary_R31 | Severe_lobe | AD | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Severe_lobe | AD | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three | Mild_lobe | Mild | 0.413 | 0.160 | 0.000 |
| ±2 dB gain + ±10° phase | three | Mild_lobe | Mild | 0.430 | 0.187 | 0.000 |
| typical, ±0.5 dB gain | three | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Mild_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Mild_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Moderate_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Moderate_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |

All labels:
| condition | design | rule | Normal | AD | Mild | Mild+Moderate | Severe | UNCERTAIN |
|---|---|---|---|---|---|---|---|---|
| typical, ±0.5 dB gain | Healthy_sliced | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Healthy_sliced | three | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Healthy_sliced | three_merged | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Mild_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Mild_lobe | three | 0.427 | 0.000 | 0.413 | 0.000 | 0.000 | 0.160 |
| typical, ±0.5 dB gain | Mild_lobe | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Moderate_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Moderate_lobe | three | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Moderate_lobe | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Severe_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Severe_lobe | three | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| typical, ±0.5 dB gain | Severe_lobe | three_merged | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced | three | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced | three_merged | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Mild_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Mild_lobe | three | 0.383 | 0.000 | 0.430 | 0.000 | 0.000 | 0.187 |
| ±2 dB gain + ±10° phase | Mild_lobe | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Moderate_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Moderate_lobe | three | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Moderate_lobe | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Severe_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Severe_lobe | three | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| ±2 dB gain + ±10° phase | Severe_lobe | three_merged | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |

Ratio values of the lobe designs next to the uniform solves (dB, clean data):
| set | stage | solve | R31 | R21 | R32 |
|---|---|---|---|---|---|
| lobe | Normal | Healthy_sliced | -14.61 | -20.51 | 5.90 |
| lobe | Mild | Mild_lobe | -15.82 | -19.97 | 4.15 |
| lobe | Moderate | Moderate_lobe | -16.01 | -19.45 | 3.44 |
| lobe | Severe | Severe_lobe | -15.53 | -18.00 | 2.47 |
| uniform v1 | Normal | brain_sevem_layer_Healthy.s6p | -14.48 | -20.39 | 5.92 |
| uniform v2 | Normal | new_Healthy.s6p | -14.67 | -20.72 | 6.05 |
| uniform v2 | MCI | new_MCI.s6p | -14.61 | -20.68 | 6.07 |
| uniform v1 | Mild | Brain_sevem_layer_MildAD.s6p | -16.20 | -19.31 | 3.11 |
| uniform v2 | Mild | new_MildAD.s6p | -16.06 | -19.48 | 3.42 |
| uniform v1 | Moderate | Brain_sevem_layer_ModerateAD.s6p | -16.51 | -19.77 | 3.26 |
| uniform v2 | Moderate | new_ModerateAD.s6p | -16.17 | -19.53 | 3.36 |
| uniform v1 | Severe | brain_sevem_layer_SevereAD.s6p | -15.85 | -18.16 | 2.31 |
| uniform v2 | Severe | new_SevereAD.s6p | -15.85 | -18.06 | 2.21 |

Frozen decision boundaries: R31 tau = -15.27 dB (margin 0.08); three (R21): Normal|Mild at -19.98, Mild|Severe at -18.75; three_merged (R32): Severe|Mild+Moderate at 2.77, Mild+Moderate|Normal at 4.64.
Lobe ordering Normal -> Mild -> Moderate -> Severe monotone: R21 True, R32 True (R31 is not monotone in the uniform set either).

## 3.4 Asymmetry and localisation
### (a) Per-path change maps (stage minus Healthy_sliced, band power, clean data)
Figure `figures/4a_path_change_maps.png`. Largest changes per design:
| design | path | type | lobes | change dB |
|---|---|---|---|---|
| Severe_lobe | T2-T6 | second-neighbour | Temporal L / Temporal R | 1.842 |
| Severe_lobe | T1-T3 | second-neighbour | Frontal / Parietal L | 1.814 |
| Severe_lobe | T1-T4 | opposite | Frontal / Occipital | -1.799 |
| Severe_lobe | T3-T6 | opposite | Parietal L / Temporal R | -1.762 |
| Moderate_lobe | T3-T6 | opposite | Parietal L / Temporal R | -1.639 |
| Moderate_lobe | T1-T4 | opposite | Frontal / Occipital | -1.577 |
| Moderate_lobe | T2-T5 | opposite | Temporal L / Parietal R | -1.564 |
| Mild_lobe | T3-T6 | opposite | Parietal L / Temporal R | -1.333 |
| Mild_lobe | T2-T5 | opposite | Temporal L / Parietal R | -1.244 |
| Mild_lobe | T2-T6 | second-neighbour | Temporal L / Temporal R | 1.144 |
| Moderate_lobe | T2-T6 | second-neighbour | Temporal L / Temporal R | 1.125 |
| Mild_lobe | T1-T4 | opposite | Frontal / Occipital | -0.912 |

Neighbour-path changes (both directions averaged):
| path | Mild_lobe | Moderate_lobe | Severe_lobe |
|---|---|---|---|
| T1-T2 | 0.019 | -0.287 | -0.787 |
| T1-T6 | 0.090 | -0.295 | -0.810 |
| T2-T3 | 0.086 | -0.240 | -0.979 |
| T3-T4 | 0.003 | -0.071 | -0.889 |
| T4-T5 | 0.012 | -0.089 | -0.818 |
| T5-T6 | 0.090 | -0.185 | -0.716 |

### (b) Front-back and left-right indices
front-back = mean change of transmission paths touching T1 (front, not T4) minus those touching T4 (back, not T1); left-right = paths touching T2/T3 (left, not T5/T6) minus those touching T5/T6. Healthy floor = rms of the same index over the 12 symmetry relabelings of the healthy circulant residual; staged mirror floor = the index's SD from the per-path numerical SD of the staged designs; verdicts use the larger. Measurement SD includes ±0.5 dB per-port gain errors, which these indices do NOT cancel.
| design | index | value dB | healthy floor dB | staged mirror floor dB | / floor (larger) | measurement SD dB (±0.5 dB gain) | / sqrt(floor^2+meas^2) |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | front-back, all paths | 0.000 | 0.066 | 0.084 | 0.000 | 0.438 | 0.000 |
| Healthy_sliced | left-right, all paths | 0.000 | 0.062 | 0.071 | 0.000 | 0.400 | 0.000 |
| Healthy_sliced | front-back, neighbour paths | 0.000 | 0.022 | 0.080 | 0.000 | 0.556 | 0.000 |
| Healthy_sliced | left-right, neighbour paths | 0.000 | 0.017 | 0.066 | 0.000 | 0.443 | 0.000 |
| Healthy_sliced | front-back, second-neighbour paths | 0.000 | 0.119 | 0.149 | 0.000 | 0.523 | 0.000 |
| Healthy_sliced | left-right, second-neighbour paths | 0.000 | 0.132 | 0.149 | 0.000 | 0.342 | 0.000 |
| Mild_lobe | front-back, all paths | 0.141 | 0.066 | 0.084 | 1.672 | 0.448 | 0.310 |
| Mild_lobe | left-right, all paths | 0.084 | 0.062 | 0.071 | 1.181 | 0.381 | 0.217 |
| Mild_lobe | front-back, neighbour paths | 0.047 | 0.022 | 0.080 | 0.584 | 0.541 | 0.086 |
| Mild_lobe | left-right, neighbour paths | -0.028 | 0.017 | 0.066 | -0.427 | 0.423 | -0.066 |
| Mild_lobe | front-back, second-neighbour paths | 0.236 | 0.119 | 0.149 | 1.586 | 0.542 | 0.419 |
| Mild_lobe | left-right, second-neighbour paths | 0.253 | 0.132 | 0.149 | 1.700 | 0.323 | 0.710 |
| Moderate_lobe | front-back, all paths | 0.069 | 0.066 | 0.084 | 0.821 | 0.467 | 0.146 |
| Moderate_lobe | left-right, all paths | -0.025 | 0.062 | 0.071 | -0.350 | 0.392 | -0.063 |
| Moderate_lobe | front-back, neighbour paths | -0.211 | 0.022 | 0.080 | -2.626 | 0.555 | -0.376 |
| Moderate_lobe | left-right, neighbour paths | -0.010 | 0.017 | 0.066 | -0.146 | 0.434 | -0.022 |
| Moderate_lobe | front-back, second-neighbour paths | 0.350 | 0.119 | 0.149 | 2.353 | 0.594 | 0.571 |
| Moderate_lobe | left-right, second-neighbour paths | -0.048 | 0.132 | 0.149 | -0.324 | 0.334 | -0.132 |
| Severe_lobe | front-back, all paths | 0.074 | 0.066 | 0.084 | 0.875 | 0.421 | 0.172 |
| Severe_lobe | left-right, all paths | -0.034 | 0.062 | 0.071 | -0.479 | 0.369 | -0.091 |
| Severe_lobe | front-back, neighbour paths | 0.055 | 0.022 | 0.080 | 0.683 | 0.506 | 0.107 |
| Severe_lobe | left-right, neighbour paths | -0.103 | 0.017 | 0.066 | -1.577 | 0.407 | -0.251 |
| Severe_lobe | front-back, second-neighbour paths | 0.093 | 0.119 | 0.149 | 0.625 | 0.542 | 0.165 |
| Severe_lobe | left-right, second-neighbour paths | 0.070 | 0.132 | 0.149 | 0.470 | 0.316 | 0.200 |

### (c) Gain-invariant cross-ratios
45 cross-ratios (15 sets of 4 antennas x 3 pairings). SD = symmetry floor (12 relabelings of the healthy head) and measurement noise in quadrature. 24 of 45 separate front-affected Moderate from front-healthy Mild by >= 3 SD; the top 8:
| cross-ratio | Δ Mild_lobe dB | Δ Moderate_lobe dB | Δ Severe_lobe dB | symmetry floor dB | measurement SD dB | Moderate-Mild (front affected vs not) dB | |Moderate-Mild| / SD |
|---|---|---|---|---|---|---|---|
| T1T4·T2T5 / T1T5·T2T4 | -3.057 | -4.856 | -6.734 | 0.013 | 0.112 | -1.799 | 15.935 |
| T1T3·T4T6 / T1T4·T3T6 | 2.944 | 4.470 | 7.026 | 0.013 | 0.130 | 1.525 | 11.702 |
| T1T4·T5T6 / T1T5·T4T6 | -1.369 | -3.294 | -5.789 | 0.129 | 0.113 | -1.926 | 11.260 |
| T1T2·T4T5 / T1T5·T2T4 | -0.870 | -2.091 | -4.828 | 0.044 | 0.110 | -1.221 | 10.316 |
| T1T2·T3T4 / T1T4·T2T3 | 0.848 | 1.458 | 1.101 | 0.041 | 0.057 | 0.610 | 8.693 |
| T1T5·T4T6 / T1T6·T4T5 | 0.446 | 1.917 | 4.903 | 0.129 | 0.112 | 1.471 | 8.610 |
| T1T3·T4T6 / T1T6·T3T4 | 0.606 | 1.620 | 5.165 | 0.044 | 0.112 | 1.014 | 8.406 |
| T1T3·T2T4 / T1T4·T2T3 | 1.879 | 3.253 | 6.191 | 0.129 | 0.115 | 1.374 | 7.979 |

These raw cross-ratios mix path distances (e.g. T1T4·T2T5 / T1T5·T2T4 = (opposite / second-neighbour)^2 for a symmetric head), so they also change for a uniformly diseased head: they measure overall severity, not location. Moderate is also more severe than Mild everywhere, so the table above does NOT show front-lobe localisation.

**Asymmetry cross-ratios** (each minus the mean of its symmetry-equivalent copies; zero for any rotationally symmetric head, still gain-invariant). Numerical floor per design: healthy residual rms 0.114 dB, staged mirror residual 0.196 dB (larger used); SD of a Moderate-Mild difference = sqrt2 x (floor (+) measurement). 0 of 45 separate Moderate from Mild by >= 3 SD (0 of them involve T1). Top 8:
| asymmetry cross-ratio | Healthy_sliced dB | Mild_lobe dB | Moderate_lobe dB | Severe_lobe dB | SD dB (floor+meas) | Moderate-Mild dB | |Moderate-Mild| / SD | involves T1 (front) |
|---|---|---|---|---|---|---|---|---|
| T1T4·T5T6 / T1T5·T4T6 | -0.035 | 0.874 | 0.181 | 0.110 | 0.307 | -0.693 | 2.257 | True |
| T1T4·T3T5 / T1T5·T3T4 | 0.103 | 0.712 | 0.014 | -0.003 | 0.321 | -0.698 | 2.170 | True |
| T1T3·T5T6 / T1T5·T3T6 | -0.049 | 0.313 | -0.273 | 0.263 | 0.319 | -0.586 | 1.838 | True |
| T1T2·T4T6 / T1T4·T2T6 | 0.128 | -1.192 | -0.630 | 0.025 | 0.323 | 0.562 | 1.740 | True |
| T1T5·T3T6 / T1T6·T3T5 | -0.139 | -0.660 | -0.102 | -0.045 | 0.323 | 0.558 | 1.727 | True |
| T2T5·T3T6 / T2T6·T3T5 | -0.015 | -0.997 | -0.508 | 0.027 | 0.308 | 0.489 | 1.588 | False |
| T1T2·T3T4 / T1T4·T2T3 | -0.013 | -0.378 | 0.046 | 0.164 | 0.286 | 0.424 | 1.482 | True |
| T1T2·T3T6 / T1T3·T2T6 | 0.142 | -0.631 | -0.176 | -0.128 | 0.307 | 0.455 | 1.481 | True |

## Mesh scale (lobe_v1 is mesh-unmatched)
HFSS Setup1 per design (from the HFSS solution dialogs, user 2026-10-03; `data/mesh_lobe.csv`). Common: adaptive at 3.4 GHz, Max Delta S 0.02, max 8 passes, 30% refinement, first-order basis, iterative solver. **The settings are not matched:** the healthy reference has ~1.8x the elements and ~2x tighter final Delta S than every AD stage (minimum converged passes 2 vs 1), the same healthy-vs-AD mesh imbalance as in v2.
| file | set | passes | final_dS | elements | min_converged_passes | status |
|---|---|---|---|---|---|---|
| new_with_slices_Healthy_sliced.s6p | lobe_v1 | 7 | 0.0092 | 1349491 | 2 | CONVERGED |
| new_with_slices_Mild_lobe.s6p | lobe_v1 | 5 | 0.0186 | 739774 | 1 | CONVERGED |
| new_with_slices_Moderate_lobe.s6p | lobe_v1 | 5 | 0.0194 | 796281 | 1 | CONVERGED |
| new_with_slices_Severe_lobe.s6p | lobe_v1 | 5 | 0.02 | 690077 | 1 | CONVERGED (marginal) |

Rough mesh scale = Healthy_sliced vs v2 new_Healthy (two healthy heads, different meshes; one pair, so not an SD; may include a small geometry difference): R31 0.065 dB, R21 0.215 dB, R32 0.150 dB; neighbour paths 0.234 dB rms per path; front-back neighbour index 0.173 dB; asymmetry cross-ratios 0.365 dB rms. Each lobe-set effect as a multiple of it:
| effect | dB | mesh scale dB | x own-feature mesh scale | x largest ratio mesh scale | verdict (own-feature scale) |
|---|---|---|---|---|---|
| detection: R31 Healthy_sliced -> Mild_lobe | -1.213 | 0.065 | 18.773 | 5.651 | exceeds the mesh scale (>= 5x) |
| detection: R31 Healthy_sliced -> Moderate_lobe | -1.399 | 0.065 | 21.647 | 6.516 | exceeds the mesh scale (>= 5x) |
| detection: R31 Healthy_sliced -> Severe_lobe | -0.924 | 0.065 | 14.305 | 4.306 | exceeds the mesh scale (>= 5x) |
| detection: distance of Healthy_sliced R31 from tau | 0.664 | 0.065 | 10.274 | 3.092 | exceeds the mesh scale (>= 5x) |
| detection: distance of Mild_lobe R31 from tau | -0.549 | 0.065 | 8.499 | 2.558 | exceeds the mesh scale (>= 5x) |
| detection: distance of Moderate_lobe R31 from tau | -0.735 | 0.065 | 11.374 | 3.424 | exceeds the mesh scale (>= 5x) |
| detection: distance of Severe_lobe R31 from tau | -0.261 | 0.065 | 4.032 | 1.214 | mesh-sensitive (2-5x) |
| staging: R21 Healthy_sliced -> Mild_lobe | 0.533 | 0.215 | 2.482 | 2.482 | mesh-sensitive (2-5x) |
| staging: R21 Healthy_sliced -> Severe_lobe | 2.505 | 0.215 | 11.670 | 11.670 | exceeds the mesh scale (>= 5x) |
| staging: R32 Healthy_sliced -> Mild_lobe | -1.746 | 0.150 | 11.635 | 8.133 | exceeds the mesh scale (>= 5x) |
| staging: R32 Healthy_sliced -> Severe_lobe | -3.429 | 0.150 | 22.856 | 15.976 | exceeds the mesh scale (>= 5x) |
| localisation: front-back index, neighbour paths, Moderate_lobe | -0.211 | 0.173 | 1.221 | 0.983 | not separable from mesh (< 2x) |
| localisation: frontal neighbour path T1-T2, Moderate_lobe | -0.287 | 0.234 | 1.228 | 1.339 | not separable from mesh (< 2x) |
| localisation: frontal neighbour path T1-T6, Moderate_lobe | -0.295 | 0.234 | 1.261 | 1.375 | not separable from mesh (< 2x) |
| localisation: best asymmetry cross-ratio, Moderate-Mild (T1T4·T5T6 / T1T5·T4T6) | -0.693 | 0.365 | 1.901 | 3.230 | not separable from mesh (< 2x) |

Localisation effects are within a few mesh scales, so they are **not separable from mesh** until the mesh-matched re-solves (set lobe_v1m) exist. The v1 vs v1m difference of Mild/Moderate/Severe will measure the mesh effect on the AD stages directly.

### (d) LeftOnly_test predictions
Written to `results/05_lobe/predictions.md` (pre-registered; scored only after LeftOnly_test arrives).

## Claims
| claim | number | baseline | verdict |
|---|---|---|---|
| Healthy_sliced reproduces the v2 healthy head on the classifier features | R31 +0.06 dB (+0.4 SD); R21 +0.21 dB (+1.3 SD); R32 -0.15 dB (-1.2 SD) | v2 solve-to-solve SD (4 pairs) | holds |
| frozen binary_R31 rule labels Mild_lobe as AD (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen binary_R31 rule labels Moderate_lobe as AD (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen binary_R31 rule labels Severe_lobe as AD (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen binary_R31 rule labels Healthy_sliced as Normal (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen three rule labels Mild_lobe as Mild (no refitting) | 0.41 correct, 0.16 uncertain (±2 dB/±10°: 0.43) | trained on uniform-atrophy solves only | retracted |
| frozen three rule labels Severe_lobe as Severe (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen three_merged rule labels Moderate_lobe as Mild+Moderate (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| front-affected Moderate differs front-to-back (front-back, neighbour paths) | Moderate -0.21 dB = -2.6x floor (Mild +0.05); with ±0.5 dB gain errors -0.4x | symmetry floor of the healthy sliced head; and measurement noise incl. per-port gain | clean: weakened; with gain errors: retracted; not separable from mesh (lobe_v1 mesh-unmatched) |
| front-affected Moderate differs front-to-back (front-back, all paths) | Moderate +0.07 dB = +0.8x floor (Mild +0.14); with ±0.5 dB gain errors +0.1x | symmetry floor of the healthy sliced head; and measurement noise incl. per-port gain | clean: retracted; with gain errors: retracted; not separable from mesh (lobe_v1 mesh-unmatched) |
| raw cross-ratios separate Moderate from Mild (severity, not location) | 24/45 >= 3 SD; best T1T4·T2T5 / T1T5·T2T4 -1.80 dB (15.9 SD) | symmetry floor + measurement noise | holds as severity; not a location claim |
| gain-invariant ASYMMETRY cross-ratios see the front-lobe involvement of Moderate | 0/45 >= 3 SD (0 involve T1); best T1T4·T5T6 / T1T5·T4T6 -0.69 dB (2.3 SD) | larger of healthy / staged-mirror asymmetry floor, x sqrt2 (two designs), + measurement noise | not significant (best 2.3 SD; 7 of the top 8 involve T1); not separable from mesh (lobe_v1 mesh-unmatched) |
| left-right index of Mild_lobe is ~0 (mirror-symmetric by construction; a check) | +0.084 dB = +1.2x floor | larger of healthy / staged-mirror floor | check passes |
| left-right index of Moderate_lobe is ~0 (mirror-symmetric by construction; a check) | -0.025 dB = -0.4x floor | larger of healthy / staged-mirror floor | check passes |
| left-right index of Severe_lobe is ~0 (mirror-symmetric by construction; a check) | -0.034 dB = -0.5x floor | larger of healthy / staged-mirror floor | check passes |
| mesh scale: how far mesh alone moves the features (Healthy_sliced vs v2 new_Healthy) | R31 0.06, R21 0.21, R32 0.15 dB; neighbour path 0.23 dB; front-back neighbour index 0.17 dB | one pair of healthy heads with different meshes (rough; may include geometry) | ruler for the rows below |
| detection: R31 Healthy_sliced -> Mild_lobe exceeds the mesh scale | -1.21 dB = 18.8x own-feature mesh scale (5.7x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| detection: R31 Healthy_sliced -> Moderate_lobe exceeds the mesh scale | -1.40 dB = 21.6x own-feature mesh scale (6.5x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| detection: R31 Healthy_sliced -> Severe_lobe exceeds the mesh scale | -0.92 dB = 14.3x own-feature mesh scale (4.3x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| detection: distance of Healthy_sliced R31 from tau exceeds the mesh scale | +0.66 dB = 10.3x own-feature mesh scale (3.1x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| detection: distance of Mild_lobe R31 from tau exceeds the mesh scale | -0.55 dB = 8.5x own-feature mesh scale (2.6x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| detection: distance of Moderate_lobe R31 from tau exceeds the mesh scale | -0.73 dB = 11.4x own-feature mesh scale (3.4x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| detection: distance of Severe_lobe R31 from tau exceeds the mesh scale | -0.26 dB = 4.0x own-feature mesh scale (1.2x the largest ratio scale) | mesh scale above | mesh-sensitive (2-5x) |
| staging: R21 Healthy_sliced -> Mild_lobe exceeds the mesh scale | +0.53 dB = 2.5x own-feature mesh scale (2.5x the largest ratio scale) | mesh scale above | mesh-sensitive (2-5x) |
| staging: R21 Healthy_sliced -> Severe_lobe exceeds the mesh scale | +2.51 dB = 11.7x own-feature mesh scale (11.7x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| staging: R32 Healthy_sliced -> Mild_lobe exceeds the mesh scale | -1.75 dB = 11.6x own-feature mesh scale (8.1x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| staging: R32 Healthy_sliced -> Severe_lobe exceeds the mesh scale | -3.43 dB = 22.9x own-feature mesh scale (16.0x the largest ratio scale) | mesh scale above | exceeds the mesh scale (>= 5x) |
| localisation: front-back index, neighbour paths, Moderate_lobe exceeds the mesh scale | -0.21 dB = 1.2x own-feature mesh scale (1.0x the largest ratio scale) | mesh scale above | not separable from mesh (< 2x); not separable from mesh until lobe_v1m |
| localisation: frontal neighbour path T1-T2, Moderate_lobe exceeds the mesh scale | -0.29 dB = 1.2x own-feature mesh scale (1.3x the largest ratio scale) | mesh scale above | not separable from mesh (< 2x); not separable from mesh until lobe_v1m |
| localisation: frontal neighbour path T1-T6, Moderate_lobe exceeds the mesh scale | -0.30 dB = 1.3x own-feature mesh scale (1.4x the largest ratio scale) | mesh scale above | not separable from mesh (< 2x); not separable from mesh until lobe_v1m |
| localisation: best asymmetry cross-ratio, Moderate-Mild (T1T4·T5T6 / T1T5·T4T6) exceeds the mesh scale | -0.69 dB = 1.9x own-feature mesh scale (3.2x the largest ratio scale) | mesh scale above | not separable from mesh (< 2x); not separable from mesh until lobe_v1m |

One solve per design: within-simulation noise robustness, not generalisation.