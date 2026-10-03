# Lobe-sector phantom (set lobe_B): analysis (code 7f5b39b)

Designs: Healthy_sliced, Mild_lobe_new (3.2-4.2 GHz, 201 points). One solve per design: within-simulation noise robustness, not generalisation. Noise unless stated: typical profile + setup perturbation + per-port gain ±0.5 dB. Antennas in ring order T1..T6 = Frontal, Temporal L, Parietal L, Occipital, Parietal R, Temporal R.

## 3.1 QC and symmetry floors
Parsing, passivity, reciprocity and the port-map search: `results/05_lobe/lobe_B/qc/qc_report.md` (its glitch count uses a local detector, |Sij - Sji|/|Sij| > -20 dB). Points masked by the analysis (|Sij - Sji| > -30 dB of the pair's band level; log of all lobe files: `results/05_lobe/qc/masked_points.csv`): Healthy_sliced 3.525 GHz ports 1-4; Mild_lobe_new 3.855 GHz ports 3-6.
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
| Mild_lobe_new | reflection | 2 | 0.003 | 0.030 |
| Mild_lobe_new | neighbour | 3 | 0.040 | 0.103 |
| Mild_lobe_new | second-neighbour | 2 | 0.084 | 0.249 |
| Mild_lobe_new | opposite | 1 | 0.004 | 0.049 |

Pooled mirror floor over Mild/Moderate/Severe band powers: **0.046 dB** (rms). Per-path numerical SD of the staged designs (mirror rms / sqrt 2), used as the noise ruler for every asymmetry claim: reflection 0.002 dB, neighbour 0.028 dB, second-neighbour 0.059 dB, opposite 0.003 dB. The staged designs are 2-5x less symmetric than Healthy_sliced, so the healthy floor alone would overstate asymmetry significance.

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
| typical, ±0.5 dB gain | binary_R31 | Mild_lobe_new | AD | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | binary_R31 | Mild_lobe_new | AD | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three | Mild_lobe_new | Mild | 0.690 | 0.120 | 0.000 |
| ±2 dB gain + ±10° phase | three | Mild_lobe_new | Mild | 0.717 | 0.130 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Healthy_sliced | Normal | 1.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | three_merged | Mild_lobe_new | Mild+Moderate | 1.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | three_merged | Mild_lobe_new | Mild+Moderate | 1.000 | 0.000 | 0.000 |

All labels:
| condition | design | rule | Normal | AD | Mild | Mild+Moderate | UNCERTAIN |
|---|---|---|---|---|---|---|---|
| typical, ±0.5 dB gain | Healthy_sliced | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Healthy_sliced | three | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Healthy_sliced | three_merged | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Mild_lobe_new | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| typical, ±0.5 dB gain | Mild_lobe_new | three | 0.190 | 0.000 | 0.690 | 0.000 | 0.120 |
| typical, ±0.5 dB gain | Mild_lobe_new | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced | binary_R31 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced | three | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Healthy_sliced | three_merged | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Mild_lobe_new | binary_R31 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| ±2 dB gain + ±10° phase | Mild_lobe_new | three | 0.153 | 0.000 | 0.717 | 0.000 | 0.130 |
| ±2 dB gain + ±10° phase | Mild_lobe_new | three_merged | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |

Ratio values of the lobe designs next to the uniform solves (dB, clean data):
| set | stage | solve | R31 | R21 | R32 |
|---|---|---|---|---|---|
| lobe | Normal | Healthy_sliced | -14.61 | -20.51 | 5.90 |
| lobe | Mild | Mild_lobe_new | -15.86 | -19.94 | 4.08 |
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
| Mild_lobe_new | T2-T5 | opposite | Temporal L / Parietal R | -1.390 |
| Mild_lobe_new | T3-T6 | opposite | Parietal L / Temporal R | -1.369 |
| Mild_lobe_new | T2-T6 | second-neighbour | Temporal L / Temporal R | 0.963 |
| Mild_lobe_new | T1-T4 | opposite | Frontal / Occipital | -0.835 |

Neighbour-path changes (both directions averaged):
| path | Mild_lobe_new |
|---|---|
| T1-T2 | 0.067 |
| T1-T6 | 0.047 |
| T2-T3 | 0.105 |
| T3-T4 | 0.030 |
| T4-T5 | -0.005 |
| T5-T6 | 0.054 |

### (b) Front-back and left-right indices
front-back = mean change of transmission paths touching T1 (front, not T4) minus those touching T4 (back, not T1); left-right = paths touching T2/T3 (left, not T5/T6) minus those touching T5/T6. Healthy floor = rms of the same index over the 12 symmetry relabelings of the healthy circulant residual; staged mirror floor = the index's SD from the per-path numerical SD of the staged designs; verdicts use the larger. Measurement SD includes ±0.5 dB per-port gain errors, which these indices do NOT cancel.
| design | index | value dB | healthy floor dB | staged mirror floor dB | / floor (larger) | measurement SD dB (±0.5 dB gain) | / sqrt(floor^2+meas^2) |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | front-back, all paths | 0.000 | 0.066 | 0.033 | 0.000 | 0.438 | 0.000 |
| Healthy_sliced | left-right, all paths | 0.000 | 0.062 | 0.027 | 0.000 | 0.400 | 0.000 |
| Healthy_sliced | front-back, neighbour paths | 0.000 | 0.022 | 0.028 | 0.000 | 0.556 | 0.000 |
| Healthy_sliced | left-right, neighbour paths | 0.000 | 0.017 | 0.023 | 0.000 | 0.443 | 0.000 |
| Healthy_sliced | front-back, second-neighbour paths | 0.000 | 0.119 | 0.059 | 0.000 | 0.523 | 0.000 |
| Healthy_sliced | left-right, second-neighbour paths | 0.000 | 0.132 | 0.059 | 0.000 | 0.342 | 0.000 |
| Mild_lobe_new | front-back, all paths | 0.107 | 0.066 | 0.033 | 1.620 | 0.448 | 0.236 |
| Mild_lobe_new | left-right, all paths | 0.080 | 0.062 | 0.027 | 1.298 | 0.381 | 0.207 |
| Mild_lobe_new | front-back, neighbour paths | 0.044 | 0.022 | 0.028 | 1.581 | 0.541 | 0.082 |
| Mild_lobe_new | left-right, neighbour paths | 0.035 | 0.017 | 0.023 | 1.542 | 0.423 | 0.083 |
| Mild_lobe_new | front-back, second-neighbour paths | 0.169 | 0.119 | 0.059 | 1.426 | 0.542 | 0.305 |
| Mild_lobe_new | left-right, second-neighbour paths | 0.147 | 0.132 | 0.059 | 1.113 | 0.323 | 0.421 |

### (c) Gain-invariant cross-ratios
45 cross-ratios (15 sets of 4 antennas x 3 pairings). SD = symmetry floor (12 relabelings of the healthy head) and measurement noise in quadrature. 0 of 45 separate front-affected Moderate from front-healthy Mild by >= 3 SD; the top 8:
| cross-ratio | Δ Mild_lobe_new dB | symmetry floor dB | measurement SD dB | Moderate-Mild (front affected vs not) dB | |Moderate-Mild| / SD |
|---|---|---|---|---|---|
| T1T2·T3T4 / T1T3·T2T4 | -1.053 | 0.129 | 0.108 | n/a | n/a |
| T1T2·T3T4 / T1T4·T2T3 | 0.826 | 0.041 | 0.057 | n/a | n/a |
| T1T3·T2T4 / T1T4·T2T3 | 1.878 | 0.129 | 0.115 | n/a | n/a |
| T1T2·T3T5 / T1T3·T2T5 | 1.505 | 0.129 | 0.109 | n/a | n/a |
| T1T2·T3T5 / T1T5·T2T3 | 0.199 | 0.133 | 0.112 | n/a | n/a |
| T1T3·T2T5 / T1T5·T2T3 | -1.306 | 0.129 | 0.113 | n/a | n/a |
| T1T2·T3T6 / T1T3·T2T6 | -2.945 | 0.129 | 0.119 | n/a | n/a |
| T1T2·T3T6 / T1T6·T2T3 | -1.454 | 0.041 | 0.055 | n/a | n/a |

These raw cross-ratios mix path distances (e.g. T1T4·T2T5 / T1T5·T2T4 = (opposite / second-neighbour)^2 for a symmetric head), so they also change for a uniformly diseased head: they measure overall severity, not location. Moderate is also more severe than Mild everywhere, so the table above does NOT show front-lobe localisation.

**Asymmetry cross-ratios** (each minus the mean of its symmetry-equivalent copies; zero for any rotationally symmetric head, still gain-invariant). Numerical floor per design: healthy residual rms 0.114 dB, staged mirror residual 0.065 dB (larger used); SD of a Moderate-Mild difference = sqrt2 x (floor (+) measurement). 0 of 45 separate Moderate from Mild by >= 3 SD (0 of them involve T1). Top 8:
| asymmetry cross-ratio | Healthy_sliced dB | Mild_lobe_new dB | SD dB (floor+meas) | Moderate-Mild dB | |Moderate-Mild| / SD | involves T1 (front) |
|---|---|---|---|---|---|---|
| T1T2·T3T4 / T1T3·T2T4 | 0.055 | 0.135 | 0.202 | n/a | n/a | True |
| T1T2·T3T4 / T1T4·T2T3 | -0.013 | -0.435 | 0.176 | n/a | n/a | True |
| T1T3·T2T4 / T1T4·T2T3 | -0.068 | -0.570 | 0.210 | n/a | n/a | True |
| T1T2·T3T5 / T1T3·T2T5 | 0.157 | 0.415 | 0.222 | n/a | n/a | True |
| T1T2·T3T5 / T1T5·T2T3 | 0.155 | 0.339 | 0.252 | n/a | n/a | True |
| T1T3·T2T5 / T1T5·T2T3 | -0.067 | -0.126 | 0.228 | n/a | n/a | True |
| T1T2·T3T6 / T1T3·T2T6 | 0.142 | -0.423 | 0.209 | n/a | n/a | True |
| T1T2·T3T6 / T1T6·T2T3 | -0.049 | -0.256 | 0.176 | n/a | n/a | True |

## Claims
| claim | number | baseline | verdict |
|---|---|---|---|
| Healthy_sliced reproduces the v2 healthy head on the classifier features | R31 +0.06 dB (+0.4 SD); R21 +0.21 dB (+1.3 SD); R32 -0.15 dB (-1.2 SD) | v2 solve-to-solve SD (4 pairs) | holds |
| frozen binary_R31 rule labels Mild_lobe_new as AD (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen binary_R31 rule labels Healthy_sliced as Normal (no refitting) | 1.00 correct, 0.00 uncertain (±2 dB/±10°: 1.00) | trained on uniform-atrophy solves only | holds |
| frozen three rule labels Mild_lobe_new as Mild (no refitting) | 0.69 correct, 0.12 uncertain (±2 dB/±10°: 0.72) | trained on uniform-atrophy solves only | weakened |
| left-right index of Mild_lobe_new is ~0 (mirror-symmetric by construction; a check) | +0.080 dB = +1.3x floor | larger of healthy / staged-mirror floor | check passes |

One solve per design: within-simulation noise robustness, not generalisation.