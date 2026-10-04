# RightOnly_test: scoring of the C6 predictions committed at 0f97bb2 (code d83d1d5-dirty)

Predictions read unchanged (git blobs checked: rightonly_predictions.md a0150e7, rightonly_predictions.csv c03834e). Status of the phase finding under test: **post hoc**. Scored exactly as written in rightonly_predictions.md. RightOnly_test: stop rule 1 (user); passes / final dS / elements not supplied; glitch mask (-30 dB) masked 0 point(s). LeftOnly values recomputed from the raw file match the committed ones (max |difference| 1.8e-15).

## Verdict: **NOT REPLICATED** (replicated only if P1 and P2 both hold)

| prediction | observed | holds |
|---|---|---|
| P1 sign flips within the clean ruler (>= 80% of informative) | 12/26 = 46% (sign flipped 26/26; within tolerance 12/26) | False |
| P2 cross-ratio counts within +-2, opposite sign | band mean 3.2-4.2: RO 4 vs LO 4, opposite sign True; 3.30-3.65 GHz: RO 9 vs LO 9, opposite sign True | True |
| P3 power LR indices < 2x; reflection pairs flip | LR index / ruler 0.70, 0.25, 0.66; reflection pairs +0.070 dB, +0.073 dB | True |
| P4 R31/R21/R32 = LeftOnly within the yardstick | R31 -15.458 (|diff| 0.013 vs 0.135), R21 -20.067 (|diff| 0.133 vs 0.110), R32 4.609 (|diff| 0.146 vs 0.161) | False |
| P5 imaging LR sign flips, < 2x the max floor (Tikhonov dS) | Healthy_sliced (7 passes): T -10.17 (2.50x); Healthy_sliced_new (6 passes): T -10.15 (2.51x) | False |
| VERDICT (replicated iff P1 and P2) | NOT REPLICATED | False |

## P2 detail
| frequencies | LeftOnly count (committed) | LeftOnly count (recomputed) | RightOnly count | all counted with opposite sign | holds | RightOnly statistics >= 3x |
|---|---|---|---|---|---|---|
| band mean 3.2-4.2 | 4 | 4 | 4 | True | True | T1T2·T3T4 / T1T3·T2T4 (+8.89, 3.03x); T1T3·T2T4 / T1T4·T2T3 (-7.79, 3.10x); T2T3·T4T5 / T2T4·T3T5 (+4.36, 3.40x); T2T3·T4T6 / T2T6·T3T4 (+4.36, 3.40x) |
| 3.30-3.65 GHz | 9 | 9 | 9 | True | True | T1T2·T3T4 / T1T3·T2T4 (+16.62, 4.01x); T1T3·T2T4 / T1T4·T2T3 (-15.31, 4.10x); T1T2·T4T6 / T1T4·T2T6 (+10.60, 3.22x); T1T2·T4T6 / T1T6·T2T4 (+21.19, 3.22x); T2T3·T4T5 / T2T4·T3T5 (+9.28, 5.30x); T2T4·T3T5 / T2T5·T3T4 (-11.19, 5.18x); T2T3·T4T6 / T2T4·T3T6 (+20.47, 5.58x); T2T3·T4T6 / T2T6·T3T4 (+9.28, 5.30x); T2T4·T3T6 / T2T6·T3T4 (-11.19, 5.18x) |

## P5 detail (imaging operator rebuilt read-only)
| method | reference | T(LeftOnly) | T(RightOnly) | T(RO) + T(LO) | clean ruler | RightOnly / ruler | sign flipped | below 2x |
|---|---|---|---|---|---|---|---|---|
| Tikhonov dS (primary) | Healthy_sliced (7 passes) | 7.86 | -10.17 | -2.31 | 4.07 | 2.50 | True | False |
| Tikhonov dS (primary) | Healthy_sliced_new (6 passes) | 7.86 | -10.15 | -2.29 | 4.04 | 2.51 | True | False |
| Tikhonov log (gain-inv.) | Healthy_sliced (7 passes) | 8.75 | -11.09 | -2.34 | 3.72 | 2.98 | True | False |
| Tikhonov log (gain-inv.) | Healthy_sliced_new (6 passes) | 8.82 | -11.20 | -2.38 | 3.76 | 2.98 | True | False |
| whitened log (post-hoc) | Healthy_sliced (7 passes) | 8.69 | -10.58 | -1.89 | 3.14 | 3.37 | True | False |
| whitened log (post-hoc) | Healthy_sliced_new (6 passes) | 8.77 | -10.71 | -1.94 | 3.17 | 3.38 | True | False |

## By family (all left-right statistics; |RO + LO| is the residual asymmetry the mirror image does not cancel)
| family | n | sign flipped | within tolerance | rms |RO + LO| | rms |LO| |
|---|---|---|---|---|---|
| phase LR index | 3.000 | 3.000 | 3.000 | 1.289 | 2.356 |
| phase cross-ratio | 44.000 | 40.000 | 28.000 | 3.130 | 8.164 |
| phase pair | 8.000 | 7.000 | 8.000 | 1.142 | 2.252 |
| power LR index | 3.000 | 1.000 | 3.000 | 0.110 | 0.026 |
| power cross-ratio | 22.000 | 4.000 | 10.000 | 0.647 | 0.340 |
| power pair | 8.000 | 4.000 | 4.000 | 0.254 | 0.126 |

## Frozen rule (descriptive; the committed expectation was 'not determined')
| design | R31 | binary label | margin to AD edge (dB) | margin / R31 yardstick | three (R21) | three_merged (R32) |
|---|---|---|---|---|---|---|
| LeftOnly_test_c3 | -15.445 | AD | 0.094 | 0.693 | Normal | Normal |
| RightOnly_test | -15.458 | AD | 0.107 | 0.788 | Normal | Mild+Moderate |

## Every statistic
| statistic | frequencies | LeftOnly (committed) | LeftOnly recomputed - committed | predicted RightOnly | RightOnly observed | tolerance (clean ruler) | RightOnly / ruler | |RO + LO| | |RO - LO| (mirror-invariant) | sign flipped | within tolerance | sign test informative |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | -10.266 | 0.000 | 10.266 | 8.885 | 2.931 | 3.032 | 1.381 | n/a | True | True | True |
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | 3.30-3.65 GHz | -15.720 | 0.000 | 15.720 | 16.622 | 4.148 | 4.007 | 0.902 | n/a | True | True | True |
| phase cross-ratio T1T2·T3T4 / T1T4·T2T3 | band mean 3.2-4.2 | -0.151 | -0.000 | 0.151 | 1.096 | 1.592 | 0.688 | 0.945 | n/a | True | True | False |
| phase cross-ratio T1T2·T3T4 / T1T4·T2T3 | 3.30-3.65 GHz | -0.593 | 0.000 | 0.593 | 1.312 | 1.779 | 0.738 | 0.720 | n/a | True | True | False |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | 10.115 | 0.000 | -10.115 | -7.789 | 2.510 | 3.103 | 2.326 | n/a | True | True | True |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | 3.30-3.65 GHz | 15.127 | 0.000 | -15.127 | -15.309 | 3.737 | 4.096 | 0.182 | n/a | True | True | True |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | -5.109 | 0.000 | 5.109 | 2.907 | 2.051 | 1.417 | 2.202 | n/a | True | False | True |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | 3.30-3.65 GHz | -7.212 | 0.000 | 7.212 | 5.432 | 3.667 | 1.481 | 1.780 | n/a | True | True | False |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | band mean 3.2-4.2 | 4.821 | 0.000 | -4.821 | -2.335 | 2.768 | 0.844 | 2.485 | n/a | True | True | False |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | 3.30-3.65 GHz | 8.501 | 0.000 | -8.501 | -4.713 | 3.438 | 1.371 | 3.788 | n/a | True | False | True |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | 9.930 | 0.000 | -9.930 | -5.242 | 3.884 | 1.350 | 4.687 | n/a | True | False | True |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | 3.30-3.65 GHz | 15.713 | 0.000 | -15.713 | -10.145 | 6.189 | 1.639 | 5.568 | n/a | True | True | True |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | -5.109 | 0.000 | 5.109 | 2.907 | 2.051 | 1.417 | 2.202 | n/a | True | False | True |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | 3.30-3.65 GHz | -7.212 | 0.000 | 7.212 | 5.432 | 3.667 | 1.481 | 1.780 | n/a | True | True | False |
| phase cross-ratio T1T2·T3T6 / T1T6·T2T3 | band mean 3.2-4.2 | -0.288 | 0.000 | 0.288 | 0.572 | 2.095 | 0.273 | 0.283 | n/a | True | True | False |
| phase cross-ratio T1T2·T3T6 / T1T6·T2T3 | 3.30-3.65 GHz | 1.289 | 0.000 | -1.289 | 0.720 | 2.911 | 0.247 | 2.009 | n/a | False | True | False |
| phase cross-ratio T1T2·T4T5 / T1T4·T2T5 | band mean 3.2-4.2 | -0.137 | -0.000 | 0.137 | -0.524 | 1.767 | 0.297 | 0.661 | n/a | False | True | False |
| phase cross-ratio T1T2·T4T5 / T1T4·T2T5 | 3.30-3.65 GHz | 1.882 | -0.000 | -1.882 | -0.593 | 1.354 | 0.438 | 1.289 | n/a | True | True | False |
| phase cross-ratio T1T2·T4T5 / T1T5·T2T4 | band mean 3.2-4.2 | -0.323 | 0.000 | 0.323 | 2.023 | 3.240 | 0.624 | 1.700 | n/a | True | True | False |
| phase cross-ratio T1T2·T4T5 / T1T5·T2T4 | 3.30-3.65 GHz | 2.467 | 0.000 | -2.467 | 4.571 | 4.950 | 0.924 | 7.039 | n/a | False | False | False |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | band mean 3.2-4.2 | -5.294 | 0.000 | 5.294 | 5.454 | 2.747 | 1.986 | 0.160 | n/a | True | True | False |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | 3.30-3.65 GHz | -6.626 | 0.000 | 6.626 | 10.597 | 3.291 | 3.220 | 3.970 | n/a | True | False | True |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | band mean 3.2-4.2 | -10.588 | 0.000 | 10.588 | 10.908 | 5.493 | 1.986 | 0.319 | n/a | True | True | False |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | 3.30-3.65 GHz | -13.252 | 0.000 | 13.252 | 21.193 | 6.581 | 3.220 | 7.941 | n/a | True | False | True |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | band mean 3.2-4.2 | 4.821 | 0.000 | -4.821 | -2.335 | 2.768 | 0.844 | 2.485 | n/a | True | True | False |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | 3.30-3.65 GHz | 8.501 | 0.000 | -8.501 | -4.713 | 3.438 | 1.371 | 3.788 | n/a | True | False | True |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | 4.972 | 0.000 | -4.972 | -3.431 | 2.179 | 1.575 | 1.541 | n/a | True | True | True |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | 3.30-3.65 GHz | 9.094 | 0.000 | -9.094 | -6.025 | 2.446 | 2.463 | 3.069 | n/a | True | False | True |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | 9.943 | 0.000 | -9.943 | -6.862 | 4.358 | 1.575 | 3.081 | n/a | True | True | True |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | 3.30-3.65 GHz | 18.187 | 0.000 | -18.187 | -12.050 | 4.892 | 2.463 | 6.137 | n/a | True | False | True |
| phase cross-ratio T1T3·T4T6 / T1T4·T3T6 | band mean 3.2-4.2 | -0.185 | -0.000 | 0.185 | 2.547 | 3.335 | 0.764 | 2.362 | n/a | True | True | False |
| phase cross-ratio T1T3·T4T6 / T1T4·T3T6 | 3.30-3.65 GHz | 0.586 | 0.000 | -0.586 | 5.164 | 3.818 | 1.353 | 5.750 | n/a | False | False | False |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | -5.143 | 0.000 | 5.143 | 4.358 | 1.281 | 3.403 | 0.785 | n/a | True | True | True |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | 3.30-3.65 GHz | -6.033 | 0.000 | 6.033 | 9.284 | 1.751 | 5.301 | 3.251 | n/a | True | False | True |
| phase cross-ratio T2T3·T4T5 / T2T5·T3T4 | band mean 3.2-4.2 | 0.014 | 0.000 | -0.014 | -1.620 | 2.007 | 0.807 | 1.606 | n/a | True | True | False |
| phase cross-ratio T2T3·T4T5 / T2T5·T3T4 | 3.30-3.65 GHz | 2.474 | 0.000 | -2.474 | -1.905 | 2.142 | 0.889 | 0.569 | n/a | True | True | False |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | band mean 3.2-4.2 | 5.157 | 0.000 | -5.157 | -5.978 | 3.107 | 1.924 | 0.821 | n/a | True | True | False |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | 3.30-3.65 GHz | 8.508 | 0.000 | -8.508 | -11.189 | 2.159 | 5.183 | 2.681 | n/a | True | False | True |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | -10.300 | 0.000 | 10.300 | 10.336 | 4.351 | 2.376 | 0.036 | n/a | True | True | True |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | 3.30-3.65 GHz | -14.541 | 0.000 | 14.541 | 20.473 | 3.671 | 5.578 | 5.932 | n/a | True | False | True |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | -5.143 | 0.000 | 5.143 | 4.358 | 1.281 | 3.403 | 0.785 | n/a | True | True | True |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | 3.30-3.65 GHz | -6.033 | 0.000 | 6.033 | 9.284 | 1.751 | 5.301 | 3.251 | n/a | True | False | True |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | band mean 3.2-4.2 | 5.157 | 0.000 | -5.157 | -5.978 | 3.107 | 1.924 | 0.821 | n/a | True | True | False |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | 3.30-3.65 GHz | 8.508 | 0.000 | -8.508 | -11.189 | 2.159 | 5.183 | 2.681 | n/a | True | False | True |
| power LR index, all paths | band mean 3.2-4.2 | -0.015 | -0.000 | 0.015 | -0.069 | 0.099 | 0.696 | 0.084 | n/a | False | True | False |
| power LR index, neighbour paths | band mean 3.2-4.2 | 0.004 | 0.000 | -0.004 | -0.031 | 0.122 | 0.252 | 0.027 | n/a | True | True | False |
| power LR index, second-neighbour paths | band mean 3.2-4.2 | -0.042 | -0.000 | 0.042 | -0.127 | 0.191 | 0.665 | 0.169 | n/a | False | True | False |
| power pair T1-T2 vs T1-T6 | band mean 3.2-4.2 | 0.082 | 0.000 | -0.082 | 0.049 | 0.127 | 0.383 | 0.131 | n/a | False | False | False |
| power pair T1-T3 vs T1-T5 | band mean 3.2-4.2 | 0.108 | 0.000 | -0.108 | -0.009 | 0.495 | 0.019 | 0.099 | n/a | True | True | False |
| power pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | -0.060 | -0.000 | 0.060 | 0.070 | 0.017 | 4.092 | 0.010 | n/a | True | True | True |
| power pair T2-T3 vs T5-T6 | band mean 3.2-4.2 | 0.103 | 0.000 | -0.103 | -0.066 | 0.295 | 0.222 | 0.038 | n/a | True | True | False |
| power pair T2-T4 vs T4-T6 | band mean 3.2-4.2 | -0.193 | 0.000 | 0.193 | -0.245 | 0.301 | 0.812 | 0.438 | n/a | False | False | False |
| power pair T2-T5 vs T3-T6 | band mean 3.2-4.2 | 0.151 | 0.000 | -0.151 | 0.334 | 0.209 | 1.600 | 0.485 | n/a | False | False | False |
| power pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | -0.068 | 0.000 | 0.068 | 0.073 | 0.014 | 5.318 | 0.004 | n/a | True | True | True |
| power pair T3-T4 vs T4-T5 | band mean 3.2-4.2 | -0.175 | -0.000 | 0.175 | -0.075 | 0.092 | 0.816 | 0.250 | n/a | False | False | False |
| power cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | -0.008 | -0.000 | 0.008 | 0.228 | 0.486 | 0.469 | 0.220 | n/a | True | True | False |
| power cross-ratio T1T2·T3T4 / T1T4·T2T3 | band mean 3.2-4.2 | -0.195 | -0.000 | 0.195 | 0.039 | 0.270 | 0.144 | 0.156 | n/a | True | True | False |
| power cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | -0.188 | -0.000 | 0.188 | -0.189 | 0.407 | 0.464 | 0.376 | n/a | False | True | False |
| power cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | -0.177 | -0.000 | 0.177 | -0.276 | 0.305 | 0.904 | 0.453 | n/a | False | False | False |
| power cross-ratio T1T2·T3T5 / T1T5·T2T3 | band mean 3.2-4.2 | 0.088 | 0.000 | -0.088 | 0.105 | 0.439 | 0.239 | 0.192 | n/a | False | True | False |
| power cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | 0.264 | 0.000 | -0.264 | 0.381 | 0.643 | 0.592 | 0.645 | n/a | False | False | False |
| power cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | -0.177 | 0.000 | 0.177 | -0.276 | 0.305 | 0.904 | 0.453 | n/a | False | False | False |
| power cross-ratio T1T2·T3T6 / T1T6·T2T3 | band mean 3.2-4.2 | -0.089 | -0.000 | 0.089 | -0.171 | 0.365 | 0.469 | 0.260 | n/a | False | True | False |
| power cross-ratio T1T2·T4T5 / T1T4·T2T5 | band mean 3.2-4.2 | 0.106 | 0.000 | -0.106 | -0.210 | 0.242 | 0.869 | 0.104 | n/a | True | True | False |
| power cross-ratio T1T2·T4T5 / T1T5·T2T4 | band mean 3.2-4.2 | 0.558 | 0.000 | -0.558 | 0.359 | 0.657 | 0.546 | 0.917 | n/a | False | False | False |
| power cross-ratio T1T2·T4T6 / T1T4·T2T6 | band mean 3.2-4.2 | 0.275 | 0.000 | -0.275 | 0.293 | 0.428 | 0.685 | 0.569 | n/a | False | False | False |
| power cross-ratio T1T2·T4T6 / T1T6·T2T4 | band mean 3.2-4.2 | 0.551 | 0.000 | -0.551 | 0.587 | 0.857 | 0.685 | 1.137 | n/a | False | False | False |
| power cross-ratio T1T2·T5T6 / T1T5·T2T6 | band mean 3.2-4.2 | 0.088 | 0.000 | -0.088 | 0.105 | 0.439 | 0.239 | 0.192 | n/a | False | True | False |
| power cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | 0.283 | 0.000 | -0.283 | 0.066 | 0.545 | 0.121 | 0.349 | n/a | False | True | False |
| power cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | 0.566 | 0.000 | -0.566 | 0.131 | 1.090 | 0.121 | 0.697 | n/a | False | True | False |
| power cross-ratio T1T3·T4T6 / T1T4·T3T6 | band mean 3.2-4.2 | 0.452 | 0.000 | -0.452 | 0.569 | 0.417 | 1.364 | 1.021 | n/a | False | False | False |
| power cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | 0.471 | 0.000 | -0.471 | 0.254 | 0.382 | 0.666 | 0.725 | n/a | False | False | False |
| power cross-ratio T2T3·T4T5 / T2T5·T3T4 | band mean 3.2-4.2 | 0.301 | 0.000 | -0.301 | -0.249 | 0.510 | 0.489 | 0.052 | n/a | True | True | False |
| power cross-ratio T2T4·T3T5 / T2T5·T3T4 | band mean 3.2-4.2 | -0.169 | -0.000 | 0.169 | -0.503 | 0.322 | 1.564 | 0.673 | n/a | False | False | False |
| power cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | 0.640 | 0.000 | -0.640 | 0.758 | 0.533 | 1.423 | 1.398 | n/a | False | False | False |
| power cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | 0.471 | 0.000 | -0.471 | 0.254 | 0.382 | 0.666 | 0.725 | n/a | False | False | False |
| power cross-ratio T2T4·T3T6 / T2T6·T3T4 | band mean 3.2-4.2 | -0.169 | -0.000 | 0.169 | -0.503 | 0.322 | 1.564 | 0.673 | n/a | False | False | False |
| phase pair T1-T2 vs T1-T6 | band mean 3.2-4.2 | -1.996 | 0.000 | 1.996 | 3.235 | 1.738 | 1.861 | 1.239 | n/a | True | True | False |
| phase pair T1-T3 vs T1-T5 | band mean 3.2-4.2 | 3.435 | 0.000 | -3.435 | -1.261 | 3.256 | 0.387 | 2.174 | n/a | True | True | False |
| phase pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | -0.002 | -0.000 | 0.002 | -0.368 | 0.385 | 0.956 | 0.370 | n/a | False | True | False |
| phase pair T2-T3 vs T5-T6 | band mean 3.2-4.2 | -3.381 | 0.000 | 3.381 | 4.309 | 2.226 | 1.936 | 0.928 | n/a | True | True | False |
| phase pair T2-T4 vs T4-T6 | band mean 3.2-4.2 | 3.299 | 0.000 | -3.299 | -2.219 | 2.889 | 0.768 | 1.080 | n/a | True | True | False |
| phase pair T2-T5 vs T3-T6 | band mean 3.2-4.2 | -0.322 | 0.000 | 0.322 | 1.589 | 1.866 | 0.851 | 1.267 | n/a | True | True | False |
| phase pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | -0.034 | -0.000 | 0.034 | 0.042 | 0.131 | 0.320 | 0.008 | n/a | True | True | False |
| phase pair T3-T4 vs T4-T5 | band mean 3.2-4.2 | -1.537 | 0.000 | 1.537 | 2.170 | 1.078 | 2.014 | 0.634 | n/a | True | True | False |
| phase LR index, all paths | band mean 3.2-4.2 | -0.036 | -0.000 | 0.036 | 1.247 | 1.916 | 0.651 | 1.211 | n/a | True | True | False |
| phase LR index, neighbour paths | band mean 3.2-4.2 | -2.305 | 0.000 | 2.305 | 3.238 | 1.681 | 1.927 | 0.934 | n/a | True | True | False |
| phase LR index, second-neighbour paths | band mean 3.2-4.2 | 3.367 | 0.000 | -3.367 | -1.740 | 2.269 | 0.767 | 1.627 | n/a | True | True | False |
| R31 (mirror-invariant) | band mean 3.2-4.2 | -15.445 | 0.000 | -15.445 | -15.458 | 0.135 | n/a | n/a | 0.013 | n/a | True | False |
| R21 (mirror-invariant) | band mean 3.2-4.2 | -20.200 | 0.000 | -20.200 | -20.067 | 0.110 | n/a | n/a | 0.133 | n/a | False | False |
| R32 (mirror-invariant) | band mean 3.2-4.2 | 4.755 | 0.000 | 4.755 | 4.609 | 0.161 | n/a | n/a | 0.146 | n/a | True | False |

Not replicated (P1 failed). As committed at 0f97bb2 and confirmed by the user, the post-hoc left-right phase finding is therefore retracted as numerical.
