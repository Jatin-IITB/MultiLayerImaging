# Test_B: blind estimates (main session; code d3a4bbf-dirty; protocol committed at d3a4bbf)

Test_B was loaded only after the protocol was committed. Its geometry was not read from anything but its S-parameters; header comments were not read. One solve: within-simulation statements only. Reference: Healthy_sliced_new (stop rule 1).

## QC
| points | band GHz | max singular value^2 | max |Sij - Sji| / |Sij| (dB) | glitch-masked points (-30 dB rule) |
|---|---|---|---|---|
| 201 | 3.200-4.200 | 0.905 | -26.162 | 3 |

## Estimates
| item | estimate | margin / confidence |
|---|---|---|
| detection (frozen R31) | AD | +0.094 dB; A1 0.70x; not determined (< 2x) |
| staging three (R21) | Normal | +0.122 dB; A1 1.11x; not determined (< 2x) |
| staging three_merged (R32) | Normal | -0.025 dB; A1 0.16x; not determined (< 2x) |
| side | left | sensitive (mirror test only); fit side symmetric, mirror side left (7 votes >= 2x, 4 >= 3x) |
| sector pattern | 25 | fit accepted (accepted); contrast 3.2x null; ring mean -3.88 deg (3.5x healthy twin) |
| S1 frontal | uncertain | 1.5x |
| S2 temporal L | uncertain | 1.9x |
| S3 parietal L | uncertain | 1.0x |
| S4 occipital | uncertain | 1.8x |
| S5 parietal R | uncertain | 1.1x |
| S6 temporal R | uncertain | 1.6x |
| secondary reference Healthy_sliced (7 passes) | 25 | accepted True; contrast 3.3x |
| most similar known designs (rms of y) | LeftOnly_test_c3, RightOnly_test, Mild_lobe_new | 1.60 deg, 2.64 deg, 3.37 deg |

## Frozen rule
| rule | feature | value dB | label | signed margin to label edge (dB) | yardstick | boundary SD | meas SD ±0.5 dB | A1 ratio | quadrature ±0.5 dB | verdict (A1) | noisy draws (typical + ±0.5 dB), label fractions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| binary | R31 | -15.445 | AD | 0.094 | 0.135 | 0.054 | 0.027 | 0.696 | 0.635 | not determined (< 2x) | {'AD': 1.0} |
| three | R21 | -20.109 | Normal | 0.122 | 0.110 | 0.065 | 0.047 | 1.107 | 0.894 | not determined (< 2x) | {'Normal': 1.0} |
| three_merged | R32 | 4.665 | Normal | -0.025 | 0.161 | 0.038 | 0.054 | 0.159 | 0.147 | not determined (< 2x) | {'Normal': 0.687, 'Mild+Moderate': 0.26, 'UNCERTAIN': 0.053} |

## Power indices
Front-back (Test_B minus reference):
| index | reference | value dB | clean ruler | ratio | tier |
|---|---|---|---|---|---|
| front-back, all paths (power) | Healthy_sliced_new | -0.003 | 0.122 | 0.022 | not determined (< 2x) |
| front-back, all paths (power) | Healthy_sliced | -0.072 | 0.122 | 0.592 | not determined (< 2x) |
| front-back, neighbour paths (power) | Healthy_sliced_new | -0.053 | 0.111 | 0.478 | not determined (< 2x) |
| front-back, neighbour paths (power) | Healthy_sliced | -0.121 | 0.111 | 1.090 | not determined (< 2x) |

Left-right (reference-free) and reflection mirror pairs against the R1c ruler:
| statistic | value | R1c clean ruler | ratio | LeftOnly |
|---|---|---|---|---|
| power LR index, all paths | 0.018 | 0.099 | 0.176 | -0.015 |
| power LR index, neighbour paths | -0.025 | 0.122 | 0.205 | 0.004 |
| power LR index, second-neighbour paths | 0.081 | 0.191 | 0.425 | -0.042 |
| power pair T2 refl. vs T6 refl. | -0.066 | 0.017 | 3.839 | -0.060 |
| power pair T3 refl. vs T5 refl. | 0.068 | 0.014 | 4.971 | -0.068 |
| phase pair T2 refl. vs T6 refl. | -0.133 | 0.385 | 0.345 | -0.002 |
| phase pair T3 refl. vs T5 refl. | 0.001 | 0.131 | 0.011 | -0.034 |

## [POST HOC] Phase cross-ratio counts >= 3x the R1c clean ruler
band mean 3.2-4.2: 0 (); 3.30-3.65 GHz: 4 (T1T2·T3T6 / T1T6·T2T3 -9.47, T1T2·T4T5 / T1T4·T2T5 -7.58, T2T3·T4T5 / T2T4·T3T5 -6.89, T2T3·T4T6 / T2T6·T3T4 -6.89)

## Localisation
y_k (deg, 3.2-3.5 GHz) against Healthy_sliced_new: T1 -3.34, T2 -5.07, T3 -3.85, T4 -3.08, T5 -4.46, T6 -3.49; against Healthy_sliced: T1 -4.41, T2 -6.19, T3 -4.97, T4 -4.12, T5 -5.60, T6 -4.66
Fit (w = 0.4): r0 (relative-pattern rms, deg): 0.6890014698934241, contrast / null: 3.2426733688649074, ring mean g (deg): -3.8819126140057176, |g| / healthy-twin |g|: 3.494547187313225, best pattern: 25, best residual (deg): 0.28639810638137303, a (deg): -2.2155675068040206, c (deg): -2.5525721099233047, second pattern: 235, second residual (deg): 0.494992542186557, accepted: True, reason: accepted, pattern call: 25

Mirror test (26 statistics informative for LeftOnly):
| statistic | frequencies | value | ruler | ratio | LeftOnly | left-like |
|---|---|---|---|---|---|---|
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | -0.711 | 2.931 | 0.243 | -10.266 | True |
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | 3.30-3.65 GHz | -4.208 | 4.148 | 1.015 | -15.720 | True |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | 0.589 | 2.510 | 0.235 | 10.115 | True |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | 3.30-3.65 GHz | 2.311 | 3.737 | 0.618 | 15.127 | True |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | -1.642 | 2.051 | 0.801 | -5.109 | True |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | 3.30-3.65 GHz | -6.473 | 3.438 | 1.883 | 8.501 | False |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | 1.327 | 3.884 | 0.342 | 9.930 | True |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | 3.30-3.65 GHz | -3.472 | 6.189 | 0.561 | 15.713 | False |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | -1.642 | 2.051 | 0.801 | -5.109 | True |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | 3.30-3.65 GHz | -8.784 | 3.291 | 2.669 | -6.626 | True |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | 3.30-3.65 GHz | -17.568 | 6.581 | 2.669 | -13.252 | True |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | 3.30-3.65 GHz | -6.473 | 3.438 | 1.883 | 8.501 | False |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | -0.193 | 2.179 | 0.089 | 4.972 | False |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | 3.30-3.65 GHz | -4.576 | 2.446 | 1.871 | 9.094 | False |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | -0.386 | 4.358 | 0.089 | 9.943 | False |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | 3.30-3.65 GHz | -9.151 | 4.892 | 1.871 | 18.187 | False |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | -0.782 | 1.281 | 0.610 | -5.143 | True |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | 3.30-3.65 GHz | -6.887 | 1.751 | 3.932 | -6.033 | True |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | 3.30-3.65 GHz | 1.208 | 2.159 | 0.559 | 8.508 | True |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | 0.149 | 4.351 | 0.034 | -10.300 | False |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | 3.30-3.65 GHz | -8.095 | 3.671 | 2.205 | -14.541 | True |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | -0.782 | 1.281 | 0.610 | -5.143 | True |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | 3.30-3.65 GHz | -6.887 | 1.751 | 3.932 | -6.033 | True |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | 3.30-3.65 GHz | 1.208 | 2.159 | 0.559 | 8.508 | True |
| power pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | -0.066 | 0.017 | 3.839 | -0.060 | True |
| power pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | 0.068 | 0.014 | 4.971 | -0.068 | False |
