# Main-session predictions for the blind design RightOnly_test (written before the design exists)

Code b61c5d8. Derived only from LeftOnly_test_c3, the nine mirror-symmetric lobe designs and the round-2 floor rule (scripts/11_review2.py docstring). Status of the phase finding being tested: **post hoc**. Do not edit after RightOnly_test exists.

## Design to build (HFSS project new_with_slices, copy of LeftOnly_test)
- e_S1..e_S6 = 0 / 0 / 0 / 0 / 11.5 / 7.5 mm (S5 parietal R 11.5, S6 temporal R 7.5; the exact mirror of LeftOnly_test's 0 / 7.5 / 11.5 / 0 / 0 / 0), r_hip 17.5 mm.
- Materials: GM/WM_Mild in S5 and S6 only; HIP_Mild; CSF_Mild (one object, so also the 0.5 mm layer on the left).
- Setup1 identical to LeftOnly_test_c3 (adaptive at 3.4 GHz, Max Delta S 0.02, stop rule 1 = first converged pass, 30% refinement, first order, iterative; interpolating sweep 3.2-4.2 GHz, 201 points). Report passes, final Delta S and elements. File: data/raw/new_with_slices_RightOnly_test.s6p.
- Why this design: the left-right phase finding claims a real asymmetry. A mirrored design with its own mesh must reproduce it with the opposite sign; a numerical artefact of LeftOnly's mesh would not.

## Predictions (reference-free mirror statistics T: RightOnly against its own port mirror)
1. Every left-right statistic flips sign: T(RightOnly) = -T(LeftOnly), within one clean ruler (max(largest symmetric design, one-pass yardstick)). Informative only where |T(LeftOnly)| >= 2x its ruler (26 statistics, listed below with 'sign test informative').
2. Phase cross-ratios >= 3x the clean ruler: 4 (band mean) and 9 (3.30-3.65 GHz) for LeftOnly; RightOnly within +-2 of each count, all with the opposite sign.
3. Power: no power LR index beyond 2x its ruler; the reflection pairs flip sign (T2 vs T6, T3 vs T5 about +0.06 / +0.07 dB).
4. Mirror-invariant ratios equal LeftOnly's within one one-pass yardstick (R31, R21, R32 rows below). The frozen detection label is therefore not determined (LeftOnly: 0.09 dB inside the AD zone).
5. Imaging-session mirror-test LR: about -7.9 (LeftOnly +7.9), i.e. the sign flips; its size stays below 2x the max floor (LeftOnly 1.94x), as for LeftOnly.

## Scoring (fixed now)
- Prediction 1 holds if the sign flips and |T(RO) + T(LO)| <= the stated tolerance for >= 80% of the informative statistics.
- Prediction 2 holds if both counts are within +-2 with the opposite sign.
- The phase finding is **replicated** only if 1 and 2 both hold. If the signs do not flip, it is retracted as numerical.

## Table
| statistic | frequencies | LeftOnly | predicted RightOnly | tolerance (clean ruler) | LeftOnly / ruler | sign test informative |
|---|---|---|---|---|---|---|
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | -10.266 | 10.266 | 2.931 | 3.503 | True |
| phase cross-ratio T1T2·T3T4 / T1T3·T2T4 | 3.30-3.65 GHz | -15.720 | 15.720 | 4.148 | 3.790 | True |
| phase cross-ratio T1T2·T3T4 / T1T4·T2T3 | band mean 3.2-4.2 | -0.151 | 0.151 | 1.592 | 0.095 | False |
| phase cross-ratio T1T2·T3T4 / T1T4·T2T3 | 3.30-3.65 GHz | -0.593 | 0.593 | 1.779 | 0.333 | False |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | 10.115 | -10.115 | 2.510 | 4.029 | True |
| phase cross-ratio T1T3·T2T4 / T1T4·T2T3 | 3.30-3.65 GHz | 15.127 | -15.127 | 3.737 | 4.048 | True |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | -5.109 | 5.109 | 2.051 | 2.491 | True |
| phase cross-ratio T1T2·T3T5 / T1T3·T2T5 | 3.30-3.65 GHz | -7.212 | 7.212 | 3.667 | 1.967 | False |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | band mean 3.2-4.2 | 4.821 | -4.821 | 2.768 | 1.742 | False |
| phase cross-ratio T1T2·T3T5 / T1T5·T2T3 | 3.30-3.65 GHz | 8.501 | -8.501 | 3.438 | 2.473 | True |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | 9.930 | -9.930 | 3.884 | 2.556 | True |
| phase cross-ratio T1T3·T2T5 / T1T5·T2T3 | 3.30-3.65 GHz | 15.713 | -15.713 | 6.189 | 2.539 | True |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | -5.109 | 5.109 | 2.051 | 2.491 | True |
| phase cross-ratio T1T2·T3T6 / T1T3·T2T6 | 3.30-3.65 GHz | -7.212 | 7.212 | 3.667 | 1.967 | False |
| phase cross-ratio T1T2·T3T6 / T1T6·T2T3 | band mean 3.2-4.2 | -0.288 | 0.288 | 2.095 | 0.138 | False |
| phase cross-ratio T1T2·T3T6 / T1T6·T2T3 | 3.30-3.65 GHz | 1.289 | -1.289 | 2.911 | 0.443 | False |
| phase cross-ratio T1T2·T4T5 / T1T4·T2T5 | band mean 3.2-4.2 | -0.137 | 0.137 | 1.767 | 0.078 | False |
| phase cross-ratio T1T2·T4T5 / T1T4·T2T5 | 3.30-3.65 GHz | 1.882 | -1.882 | 1.354 | 1.390 | False |
| phase cross-ratio T1T2·T4T5 / T1T5·T2T4 | band mean 3.2-4.2 | -0.323 | 0.323 | 3.240 | 0.100 | False |
| phase cross-ratio T1T2·T4T5 / T1T5·T2T4 | 3.30-3.65 GHz | 2.467 | -2.467 | 4.950 | 0.499 | False |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | band mean 3.2-4.2 | -5.294 | 5.294 | 2.747 | 1.928 | False |
| phase cross-ratio T1T2·T4T6 / T1T4·T2T6 | 3.30-3.65 GHz | -6.626 | 6.626 | 3.291 | 2.014 | True |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | band mean 3.2-4.2 | -10.588 | 10.588 | 5.493 | 1.928 | False |
| phase cross-ratio T1T2·T4T6 / T1T6·T2T4 | 3.30-3.65 GHz | -13.252 | 13.252 | 6.581 | 2.014 | True |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | band mean 3.2-4.2 | 4.821 | -4.821 | 2.768 | 1.742 | False |
| phase cross-ratio T1T2·T5T6 / T1T5·T2T6 | 3.30-3.65 GHz | 8.501 | -8.501 | 3.438 | 2.473 | True |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | 4.972 | -4.972 | 2.179 | 2.282 | True |
| phase cross-ratio T1T3·T4T5 / T1T4·T3T5 | 3.30-3.65 GHz | 9.094 | -9.094 | 2.446 | 3.718 | True |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | 9.943 | -9.943 | 4.358 | 2.282 | True |
| phase cross-ratio T1T3·T4T5 / T1T5·T3T4 | 3.30-3.65 GHz | 18.187 | -18.187 | 4.892 | 3.718 | True |
| phase cross-ratio T1T3·T4T6 / T1T4·T3T6 | band mean 3.2-4.2 | -0.185 | 0.185 | 3.335 | 0.056 | False |
| phase cross-ratio T1T3·T4T6 / T1T4·T3T6 | 3.30-3.65 GHz | 0.586 | -0.586 | 3.818 | 0.153 | False |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | -5.143 | 5.143 | 1.281 | 4.016 | True |
| phase cross-ratio T2T3·T4T5 / T2T4·T3T5 | 3.30-3.65 GHz | -6.033 | 6.033 | 1.751 | 3.445 | True |
| phase cross-ratio T2T3·T4T5 / T2T5·T3T4 | band mean 3.2-4.2 | 0.014 | -0.014 | 2.007 | 0.007 | False |
| phase cross-ratio T2T3·T4T5 / T2T5·T3T4 | 3.30-3.65 GHz | 2.474 | -2.474 | 2.142 | 1.155 | False |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | band mean 3.2-4.2 | 5.157 | -5.157 | 3.107 | 1.660 | False |
| phase cross-ratio T2T4·T3T5 / T2T5·T3T4 | 3.30-3.65 GHz | 8.508 | -8.508 | 2.159 | 3.941 | True |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | -10.300 | 10.300 | 4.351 | 2.368 | True |
| phase cross-ratio T2T3·T4T6 / T2T4·T3T6 | 3.30-3.65 GHz | -14.541 | 14.541 | 3.671 | 3.962 | True |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | -5.143 | 5.143 | 1.281 | 4.016 | True |
| phase cross-ratio T2T3·T4T6 / T2T6·T3T4 | 3.30-3.65 GHz | -6.033 | 6.033 | 1.751 | 3.445 | True |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | band mean 3.2-4.2 | 5.157 | -5.157 | 3.107 | 1.660 | False |
| phase cross-ratio T2T4·T3T6 / T2T6·T3T4 | 3.30-3.65 GHz | 8.508 | -8.508 | 2.159 | 3.941 | True |
| power LR index, all paths | band mean 3.2-4.2 | -0.015 | 0.015 | 0.099 | 0.149 | False |
| power LR index, neighbour paths | band mean 3.2-4.2 | 0.004 | -0.004 | 0.122 | 0.030 | False |
| power LR index, second-neighbour paths | band mean 3.2-4.2 | -0.042 | 0.042 | 0.191 | 0.222 | False |
| power pair T1-T2 vs T1-T6 | band mean 3.2-4.2 | 0.082 | -0.082 | 0.127 | 0.647 | False |
| power pair T1-T3 vs T1-T5 | band mean 3.2-4.2 | 0.108 | -0.108 | 0.495 | 0.219 | False |
| power pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | -0.060 | 0.060 | 0.017 | 3.528 | True |
| power pair T2-T3 vs T5-T6 | band mean 3.2-4.2 | 0.103 | -0.103 | 0.295 | 0.350 | False |
| power pair T2-T4 vs T4-T6 | band mean 3.2-4.2 | -0.193 | 0.193 | 0.301 | 0.641 | False |
| power pair T2-T5 vs T3-T6 | band mean 3.2-4.2 | 0.151 | -0.151 | 0.209 | 0.723 | False |
| power pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | -0.068 | 0.068 | 0.014 | 5.000 | True |
| power pair T3-T4 vs T4-T5 | band mean 3.2-4.2 | -0.175 | 0.175 | 0.092 | 1.893 | False |
| power cross-ratio T1T2·T3T4 / T1T3·T2T4 | band mean 3.2-4.2 | -0.008 | 0.008 | 0.486 | 0.015 | False |
| power cross-ratio T1T2·T3T4 / T1T4·T2T3 | band mean 3.2-4.2 | -0.195 | 0.195 | 0.270 | 0.724 | False |
| power cross-ratio T1T3·T2T4 / T1T4·T2T3 | band mean 3.2-4.2 | -0.188 | 0.188 | 0.407 | 0.462 | False |
| power cross-ratio T1T2·T3T5 / T1T3·T2T5 | band mean 3.2-4.2 | -0.177 | 0.177 | 0.305 | 0.580 | False |
| power cross-ratio T1T2·T3T5 / T1T5·T2T3 | band mean 3.2-4.2 | 0.088 | -0.088 | 0.439 | 0.200 | False |
| power cross-ratio T1T3·T2T5 / T1T5·T2T3 | band mean 3.2-4.2 | 0.264 | -0.264 | 0.643 | 0.411 | False |
| power cross-ratio T1T2·T3T6 / T1T3·T2T6 | band mean 3.2-4.2 | -0.177 | 0.177 | 0.305 | 0.580 | False |
| power cross-ratio T1T2·T3T6 / T1T6·T2T3 | band mean 3.2-4.2 | -0.089 | 0.089 | 0.365 | 0.245 | False |
| power cross-ratio T1T2·T4T5 / T1T4·T2T5 | band mean 3.2-4.2 | 0.106 | -0.106 | 0.242 | 0.438 | False |
| power cross-ratio T1T2·T4T5 / T1T5·T2T4 | band mean 3.2-4.2 | 0.558 | -0.558 | 0.657 | 0.850 | False |
| power cross-ratio T1T2·T4T6 / T1T4·T2T6 | band mean 3.2-4.2 | 0.275 | -0.275 | 0.428 | 0.643 | False |
| power cross-ratio T1T2·T4T6 / T1T6·T2T4 | band mean 3.2-4.2 | 0.551 | -0.551 | 0.857 | 0.643 | False |
| power cross-ratio T1T2·T5T6 / T1T5·T2T6 | band mean 3.2-4.2 | 0.088 | -0.088 | 0.439 | 0.200 | False |
| power cross-ratio T1T3·T4T5 / T1T4·T3T5 | band mean 3.2-4.2 | 0.283 | -0.283 | 0.545 | 0.519 | False |
| power cross-ratio T1T3·T4T5 / T1T5·T3T4 | band mean 3.2-4.2 | 0.566 | -0.566 | 1.090 | 0.519 | False |
| power cross-ratio T1T3·T4T6 / T1T4·T3T6 | band mean 3.2-4.2 | 0.452 | -0.452 | 0.417 | 1.084 | False |
| power cross-ratio T2T3·T4T5 / T2T4·T3T5 | band mean 3.2-4.2 | 0.471 | -0.471 | 0.382 | 1.232 | False |
| power cross-ratio T2T3·T4T5 / T2T5·T3T4 | band mean 3.2-4.2 | 0.301 | -0.301 | 0.510 | 0.591 | False |
| power cross-ratio T2T4·T3T5 / T2T5·T3T4 | band mean 3.2-4.2 | -0.169 | 0.169 | 0.322 | 0.526 | False |
| power cross-ratio T2T3·T4T6 / T2T4·T3T6 | band mean 3.2-4.2 | 0.640 | -0.640 | 0.533 | 1.202 | False |
| power cross-ratio T2T3·T4T6 / T2T6·T3T4 | band mean 3.2-4.2 | 0.471 | -0.471 | 0.382 | 1.232 | False |
| power cross-ratio T2T4·T3T6 / T2T6·T3T4 | band mean 3.2-4.2 | -0.169 | 0.169 | 0.322 | 0.526 | False |
| phase pair T1-T2 vs T1-T6 | band mean 3.2-4.2 | -1.996 | 1.996 | 1.738 | 1.148 | False |
| phase pair T1-T3 vs T1-T5 | band mean 3.2-4.2 | 3.435 | -3.435 | 3.256 | 1.055 | False |
| phase pair T2 refl. vs T6 refl. | band mean 3.2-4.2 | -0.002 | 0.002 | 0.385 | 0.005 | False |
| phase pair T2-T3 vs T5-T6 | band mean 3.2-4.2 | -3.381 | 3.381 | 2.226 | 1.519 | False |
| phase pair T2-T4 vs T4-T6 | band mean 3.2-4.2 | 3.299 | -3.299 | 2.889 | 1.142 | False |
| phase pair T2-T5 vs T3-T6 | band mean 3.2-4.2 | -0.322 | 0.322 | 1.866 | 0.172 | False |
| phase pair T3 refl. vs T5 refl. | band mean 3.2-4.2 | -0.034 | 0.034 | 0.131 | 0.256 | False |
| phase pair T3-T4 vs T4-T5 | band mean 3.2-4.2 | -1.537 | 1.537 | 1.078 | 1.426 | False |
| phase LR index, all paths | band mean 3.2-4.2 | -0.036 | 0.036 | 1.916 | 0.019 | False |
| phase LR index, neighbour paths | band mean 3.2-4.2 | -2.305 | 2.305 | 1.681 | 1.371 | False |
| phase LR index, second-neighbour paths | band mean 3.2-4.2 | 3.367 | -3.367 | 2.269 | 1.484 | False |
| R31 (mirror-invariant) | band mean 3.2-4.2 | -15.445 | -15.445 | 0.135 | n/a | False |
| R21 (mirror-invariant) | band mean 3.2-4.2 | -20.200 | -20.200 | 0.110 | n/a | False |
| R32 (mirror-invariant) | band mean 3.2-4.2 | 4.755 | 4.755 | 0.161 | n/a | False |
