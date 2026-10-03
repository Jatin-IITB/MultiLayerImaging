# Lobe-sector phantom (set lobe_A): analysis (code 7f5b39b)

Designs: Healthy_sliced_new, Mild_lobe, Moderate_lobe, Severe_lobe (3.2-4.2 GHz, 201 points). One solve per design: within-simulation noise robustness, not generalisation. Noise unless stated: typical profile + setup perturbation + per-port gain ±0.5 dB. Antennas in ring order T1..T6 = Frontal, Temporal L, Parietal L, Occipital, Parietal R, Temporal R.

## 3.1 QC and symmetry floors
Parsing, passivity, reciprocity and the port-map search: `results/05_lobe/lobe_A/qc/qc_report.md` (its glitch count uses a local detector, |Sij - Sji|/|Sij| > -20 dB). Points masked by the analysis (|Sij - Sji| > -30 dB of the pair's band level; log of all lobe files: `results/05_lobe/qc/masked_points.csv`): Severe_lobe 3.845 GHz ports 2-5.
Circulant floor = spread of equivalent paths in Healthy_sliced (should be identical by symmetry):
| floor | path | band-power SD dB | band-power max-min dB | median over f of per-frequency SD dB |
|---|---|---|---|---|
| circulant (Healthy_sliced) | reflection | 0.004 | 0.011 | 0.046 |
| circulant (Healthy_sliced) | neighbour | 0.049 | 0.149 | 0.084 |
| circulant (Healthy_sliced) | second-neighbour | 0.079 | 0.204 | 0.115 |
| circulant (Healthy_sliced) | opposite | 0.052 | 0.108 | 0.057 |

Mirror floor = difference between mirror-image paths (T2<->T6, T3<->T5) in the mirror-symmetric designs:
| design | path | mirror pairs | band-power rms diff dB | median over f of rms diff dB |
|---|---|---|---|---|
| Healthy_sliced_new | reflection | 2 | 0.006 | 0.052 |
| Healthy_sliced_new | neighbour | 3 | 0.059 | 0.136 |
| Healthy_sliced_new | second-neighbour | 2 | 0.133 | 0.178 |
| Healthy_sliced_new | opposite | 1 | 0.015 | 0.029 |
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
| feature | Healthy_sliced_new | new_Healthy (v2) | difference dB | / v2 solve SD | sliced antenna-spread SE dB | / sliced antenna-spread SE |
|---|---|---|---|---|---|---|
| R31 | -14.744 | -14.674 | -0.071 | -0.483 | 0.029 | -2.390 |
| R21 | -20.567 | -20.722 | 0.155 | 0.963 | 0.046 | 3.365 |
| R32 | 5.823 | 6.048 | -0.225 | -1.746 | 0.043 | -5.196 |
| k0_band | -3.632 | -3.613 | -0.018 | -0.252 | 0.002 | -10.370 |
| k1_band | -36.837 | -36.990 | 0.153 | 0.629 | 0.017 | 8.852 |
| k2_band | -57.404 | -57.710 | 0.306 | 1.332 | 0.017 | 17.879 |
| k3_band | -51.581 | -51.658 | 0.077 | 0.244 | 0.021 | 3.603 |
| logN | -2.470 | -2.484 | 0.014 | 0.253 | 0.001 | 10.298 |

Across all 89 ring-symmetrised features: 56% within 1x, 80% within 2x, 93% within 3x the v2 solve-to-solve SD; largest: k3_sb4.05, k3_sb4.10, k3_sb4.00, k1_sb3.60, k0_sb3.35. Verdict on the classifier features above: **equivalent**. Caveat: the v2 skull inner radius (hidden tool Brain_sphere_1) is unknown, so a small geometry difference cannot be excluded.

## 3.3 Frozen rule applied unchanged to the lobe designs
`results/04/frozen_rule.json` (commit 2baddee) and the gain-invariant gate (Normal window fitted on the v2 Normal, floor limit from the v2 thresholds) are applied without refitting to 300 noisy measurements per design and condition. This is the first test on a different disease geometry (regional instead of uniform atrophy) in the same head. One solve per design: within-simulation noise robustness, not generalisation.
Fraction of measurements given the expected label:
| condition | rule | design | expected | fraction correct | UNCERTAIN | INVALID |
|---|---|---|---|---|---|---|
| typical, ±0.5 dB gain | binary_R31 | Healthy_sliced_new | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Healthy_sliced_new | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | binary_R31 | Mild_lobe | AD | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Mild_lobe | AD | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | binary_R31 | Moderate_lobe | AD | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Moderate_lobe | AD | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | binary_R31 | Severe_lobe | AD | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Severe_lobe | AD | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three | Healthy_sliced_new | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three | Healthy_sliced_new | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three | Mild_lobe | Mild | 0.413 | 0.160 | 0.000 |
| ±2 dB gain + ±10° phase | three | Mild_lobe | Mild | 0.430 | 0.187 | 0.000 |
| typical, ±0.5 dB gain | three | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Healthy_sliced_new | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Healthy_sliced_new | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Mild_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Mild_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Moderate_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Moderate_lobe | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Severe_lobe | Severe | 1.000 | 0.000 | 0.000 |

All labels:
| condition | design | rule | Normal | AD | Mild | Mild+Moderate | Severe | UNCERTAIN |
|---|---|---|---|---|---|---|---|---|
| typical, ±0.5 dB gain | Healthy_sliced_new | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Healthy_sliced_new | three | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Healthy_sliced_new | three_merged | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Mild_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Mild_lobe | three | 0.427 | 0.000 | 0.413 | 0.000 | 0.000 | 0.160 |
| typical, ±0.5 dB gain | Mild_lobe | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Moderate_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Moderate_lobe | three | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Moderate_lobe | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Severe_lobe | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Severe_lobe | three | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| typical, ±0.5 dB gain | Severe_lobe | three_merged | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced_new | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced_new | three | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced_new | three_merged | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
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
| lobe | Normal | Healthy_sliced_new | -14.74 | -20.57 | 5.82 |
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
| Severe_lobe | T1-T3 | second-neighbour | Frontal / Parietal L | 1.831 |
| Severe_lobe | T1-T5 | second-neighbour | Frontal / Parietal R | 1.797 |
| Severe_lobe | T2-T6 | second-neighbour | Temporal L / Temporal R | 1.793 |
| Severe_lobe | T4-T6 | second-neighbour | Occipital / Temporal R | 1.789 |
| Moderate_lobe | T3-T6 | opposite | Parietal L / Temporal R | -1.517 |
| Moderate_lobe | T1-T4 | opposite | Frontal / Occipital | -1.451 |
| Moderate_lobe | T2-T5 | opposite | Temporal L / Parietal R | -1.441 |
| Moderate_lobe | T1-T5 | second-neighbour | Frontal / Parietal R | 1.231 |
| Mild_lobe | T3-T6 | opposite | Parietal L / Temporal R | -1.212 |
| Mild_lobe | T2-T5 | opposite | Temporal L / Parietal R | -1.121 |
| Mild_lobe | T2-T6 | second-neighbour | Temporal L / Temporal R | 1.094 |
| Mild_lobe | T3-T5 | second-neighbour | Parietal L / Parietal R | 0.851 |

Neighbour-path changes (both directions averaged):
| path | Mild_lobe | Moderate_lobe | Severe_lobe |
|---|---|---|---|
| T1-T2 | 0.057 | -0.249 | -0.749 |
| T1-T6 | 0.106 | -0.279 | -0.795 |
| T2-T3 | 0.073 | -0.252 | -0.991 |
| T3-T4 | 0.003 | -0.072 | -0.890 |
| T4-T5 | -0.070 | -0.171 | -0.899 |
| T5-T6 | 0.061 | -0.214 | -0.746 |

### (b) Front-back and left-right indices
front-back = mean change of transmission paths touching T1 (front, not T4) minus those touching T4 (back, not T1); left-right = paths touching T2/T3 (left, not T5/T6) minus those touching T5/T6. Healthy floor = rms of the same index over the 12 symmetry relabelings of the healthy circulant residual; staged mirror floor = the index's SD from the per-path numerical SD of the staged designs; verdicts use the larger. Measurement SD includes ±0.5 dB per-port gain errors, which these indices do NOT cancel.
| design | index | value dB | healthy floor dB | staged mirror floor dB | / floor (larger) | measurement SD dB (±0.5 dB gain) | / sqrt(floor^2+meas^2) |
|---|---|---|---|---|---|---|---|
| Healthy_sliced_new | front-back, all paths | 0.000 | 0.057 | 0.084 | 0.000 | 0.439 | 0.000 |
| Healthy_sliced_new | left-right, all paths | 0.000 | 0.066 | 0.071 | 0.000 | 0.400 | 0.000 |
| Healthy_sliced_new | front-back, neighbour paths | 0.000 | 0.076 | 0.080 | 0.000 | 0.556 | 0.000 |
| Healthy_sliced_new | left-right, neighbour paths | 0.000 | 0.059 | 0.066 | 0.000 | 0.443 | 0.000 |
| Healthy_sliced_new | front-back, second-neighbour paths | 0.000 | 0.073 | 0.149 | 0.000 | 0.523 | 0.000 |
| Healthy_sliced_new | left-right, second-neighbour paths | 0.000 | 0.127 | 0.149 | 0.000 | 0.342 | 0.000 |
| Mild_lobe | front-back, all paths | 0.211 | 0.057 | 0.084 | 2.495 | 0.448 | 0.462 |
| Mild_lobe | left-right, all paths | 0.032 | 0.066 | 0.071 | 0.447 | 0.381 | 0.082 |
| Mild_lobe | front-back, neighbour paths | 0.115 | 0.076 | 0.080 | 1.430 | 0.541 | 0.210 |
| Mild_lobe | left-right, neighbour paths | 0.012 | 0.059 | 0.066 | 0.184 | 0.423 | 0.028 |
| Mild_lobe | front-back, second-neighbour paths | 0.307 | 0.073 | 0.149 | 2.063 | 0.542 | 0.546 |
| Mild_lobe | left-right, second-neighbour paths | 0.062 | 0.127 | 0.149 | 0.414 | 0.323 | 0.173 |
| Moderate_lobe | front-back, all paths | 0.139 | 0.057 | 0.084 | 1.643 | 0.467 | 0.292 |
| Moderate_lobe | left-right, all paths | -0.077 | 0.066 | 0.071 | -1.085 | 0.392 | -0.194 |
| Moderate_lobe | front-back, neighbour paths | -0.143 | 0.076 | 0.080 | -1.780 | 0.555 | -0.255 |
| Moderate_lobe | left-right, neighbour paths | 0.031 | 0.059 | 0.066 | 0.465 | 0.434 | 0.070 |
| Moderate_lobe | front-back, second-neighbour paths | 0.421 | 0.073 | 0.149 | 2.831 | 0.594 | 0.687 |
| Moderate_lobe | left-right, second-neighbour paths | -0.239 | 0.127 | 0.149 | -1.610 | 0.334 | -0.654 |
| Severe_lobe | front-back, all paths | 0.143 | 0.057 | 0.084 | 1.698 | 0.421 | 0.334 |
| Severe_lobe | left-right, all paths | -0.087 | 0.066 | 0.071 | -1.214 | 0.369 | -0.230 |
| Severe_lobe | front-back, neighbour paths | 0.123 | 0.076 | 0.080 | 1.529 | 0.506 | 0.240 |
| Severe_lobe | left-right, neighbour paths | -0.063 | 0.059 | 0.066 | -0.966 | 0.407 | -0.154 |
| Severe_lobe | front-back, second-neighbour paths | 0.164 | 0.073 | 0.149 | 1.103 | 0.542 | 0.292 |
| Severe_lobe | left-right, second-neighbour paths | -0.121 | 0.127 | 0.149 | -0.816 | 0.316 | -0.347 |

### (c) Gain-invariant cross-ratios
45 cross-ratios (15 sets of 4 antennas x 3 pairings). SD = symmetry floor (12 relabelings of the healthy head) and measurement noise in quadrature. 24 of 45 separate front-affected Moderate from front-healthy Mild by >= 3 SD; the top 8:
| cross-ratio | Δ Mild_lobe dB | Δ Moderate_lobe dB | Δ Severe_lobe dB | symmetry floor dB | measurement SD dB | Moderate-Mild (front affected vs not) dB | |Moderate-Mild| / SD |
|---|---|---|---|---|---|---|---|
| T1T4·T2T5 / T1T5·T2T4 | -2.894 | -4.693 | -6.571 | 0.058 | 0.113 | -1.799 | 14.158 |
| T1T4·T5T6 / T1T5·T4T6 | -1.584 | -3.510 | -6.005 | 0.138 | 0.114 | -1.926 | 10.723 |
| T1T3·T4T6 / T1T4·T3T6 | 2.852 | 4.378 | 6.934 | 0.058 | 0.132 | 1.525 | 10.609 |
| T1T2·T4T5 / T1T5·T2T4 | -1.000 | -2.220 | -4.957 | 0.052 | 0.111 | -1.221 | 9.985 |
| T1T2·T4T5 / T1T4·T2T5 | 1.894 | 2.473 | 1.614 | 0.028 | 0.061 | 0.578 | 8.645 |
| T1T5·T4T6 / T1T6·T4T5 | 0.823 | 2.294 | 5.280 | 0.138 | 0.114 | 1.471 | 8.226 |
| T1T2·T3T4 / T1T4·T2T3 | 0.773 | 1.383 | 1.026 | 0.049 | 0.057 | 0.610 | 8.087 |
| T1T3·T4T6 / T1T6·T3T4 | 0.746 | 1.760 | 5.305 | 0.052 | 0.114 | 1.014 | 8.071 |

These raw cross-ratios mix path distances (e.g. T1T4·T2T5 / T1T5·T2T4 = (opposite / second-neighbour)^2 for a symmetric head), so they also change for a uniformly diseased head: they measure overall severity, not location. Moderate is also more severe than Mild everywhere, so the table above does NOT show front-lobe localisation.

**Asymmetry cross-ratios** (each minus the mean of its symmetry-equivalent copies; zero for any rotationally symmetric head, still gain-invariant). Numerical floor per design: healthy residual rms 0.112 dB, staged mirror residual 0.196 dB (larger used); SD of a Moderate-Mild difference = sqrt2 x (floor (+) measurement). 0 of 45 separate Moderate from Mild by >= 3 SD (0 of them involve T1). Top 8:
| asymmetry cross-ratio | Healthy_sliced_new dB | Mild_lobe dB | Moderate_lobe dB | Severe_lobe dB | SD dB (floor+meas) | Moderate-Mild dB | |Moderate-Mild| / SD | involves T1 (front) |
|---|---|---|---|---|---|---|---|---|
| T1T4·T5T6 / T1T5·T4T6 | 0.196 | 0.874 | 0.181 | 0.110 | 0.308 | -0.693 | 2.254 | True |
| T1T4·T3T5 / T1T5·T3T4 | 0.188 | 0.712 | 0.014 | -0.003 | 0.322 | -0.698 | 2.165 | True |
| T1T3·T5T6 / T1T5·T3T6 | 0.123 | 0.313 | -0.273 | 0.263 | 0.320 | -0.586 | 1.832 | True |
| T1T2·T4T6 / T1T4·T2T6 | -0.107 | -1.192 | -0.630 | 0.025 | 0.324 | 0.562 | 1.737 | True |
| T1T5·T3T6 / T1T6·T3T5 | -0.186 | -0.660 | -0.102 | -0.045 | 0.324 | 0.558 | 1.722 | True |
| T2T5·T3T6 / T2T6·T3T5 | -0.061 | -0.997 | -0.508 | 0.027 | 0.308 | 0.489 | 1.587 | False |
| T1T2·T3T4 / T1T4·T2T3 | -0.073 | -0.378 | 0.046 | 0.164 | 0.286 | 0.424 | 1.482 | True |
| T1T2·T3T6 / T1T3·T2T6 | -0.034 | -0.631 | -0.176 | -0.128 | 0.307 | 0.455 | 1.481 | True |

## Claims
| claim | number | baseline | verdict |
|---|---|---|---|
| Healthy_sliced reproduces the v2 healthy head on the classifier features | R31 -0.07 dB (-0.5 SD); R21 +0.15 dB (+1.0 SD); R32 -0.23 dB (-1.7 SD) | v2 solve-to-solve SD (4 pairs) | holds |
| frozen binary_R31 rule labels Mild_lobe as AD (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen binary_R31 rule labels Moderate_lobe as AD (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen binary_R31 rule labels Severe_lobe as AD (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen binary_R31 rule labels Healthy_sliced_new as Normal (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen three rule labels Mild_lobe as Mild (no refitting) | 0.41 correct, 0.16 uncertain (±2 dB/±10°: 0.43) | trained on uniform-atrophy solves only | retracted |
| frozen three rule labels Severe_lobe as Severe (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen three_merged rule labels Moderate_lobe as Mild+Moderate (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| front-affected Moderate differs front-to-back (front-back, neighbour paths) | Moderate -0.14 dB = -1.8x floor (Mild +0.11); with ±0.5 dB gain errors -0.3x | symmetry floor of the healthy sliced head; and measurement noise incl. per-port gain | clean: retracted; with gain errors: retracted |
| front-affected Moderate differs front-to-back (front-back, all paths) | Moderate +0.14 dB = +1.6x floor (Mild +0.21); with ±0.5 dB gain errors +0.3x | symmetry floor of the healthy sliced head; and measurement noise incl. per-port gain | clean: retracted; with gain errors: retracted |
| raw cross-ratios separate Moderate from Mild (severity, not location) | 24/45 >= 3 SD; best T1T4·T2T5 / T1T5·T2T4 -1.80 dB (14.2 SD) | symmetry floor + measurement noise | holds as severity; not a location claim |
| gain-invariant ASYMMETRY cross-ratios see the front-lobe involvement of Moderate | 0/45 >= 3 SD (0 involve T1); best T1T4·T5T6 / T1T5·T4T6 -0.69 dB (2.3 SD) | larger of healthy / staged-mirror asymmetry floor, x sqrt2 (two designs), + measurement noise | not significant (best 2.3 SD; 7 of the top 8 involve T1) |
| left-right index of Mild_lobe is ~0 (mirror-symmetric by construction; a check) | +0.032 dB = +0.4x floor | larger of healthy / staged-mirror floor | check passes |
| left-right index of Moderate_lobe is ~0 (mirror-symmetric by construction; a check) | -0.077 dB = -1.1x floor | larger of healthy / staged-mirror floor | check passes |
| left-right index of Severe_lobe is ~0 (mirror-symmetric by construction; a check) | -0.087 dB = -1.2x floor | larger of healthy / staged-mirror floor | check passes |

One solve per design: within-simulation noise robustness, not generalisation.