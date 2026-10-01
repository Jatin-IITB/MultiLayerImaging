# Prompt 02 - metric separability (track A, code c95604c, sim_set hfss-v2+v1repeats-masked)

J_meas = min pairwise Fisher ratio from noisy realisations (ranking key). J_eff adds the port-to-port asymmetry as extra variance. gap/port = class gap / port-to-port std. gap/mesh = pending (mesh-repeat not yet available). shift_move = largest change under ±2/5/10 MHz resonance shifts / smallest class gap. band_gap_retention = worst (gap after ±10 % band change) / (original gap); < 0 means the class order flips. freq_robust (brief's literal criterion) = shift AND band value changes < 0.25 × smallest gap. AD-vs-AD pairs unverified against mesh noise.

Glitch masking ON: 33 in-band (f, pair) points masked in 9 runs (results/qc/masked_points.csv).

## Ranking - scheme `binary` (binary:Normal|AD(Mild+Moderate+Severe)), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C3 | 58 | Normal|AD | 12.5 | 5.64 | 4.5e-09 | 0.00944 | 1.11 | False |
| 2 | M5.C3[k3] | 51.7 | Normal|AD | 15.6 | 6.68 | 4.98e-10 | 0.0374 | 0.924 | True |
| 3 | M5.C3_dBavg[k3] | 27.7 | Normal|AD | 10.3 | 5.71 | 1.08e-06 | 0.0688 | 0.897 | True |
| 4 | M0.old_score | 17.3 | Normal|AD | 13.8 | 11.7 | 0.00048 | 0.165 | 0.847 | False |
| 5 | M6.spread_A | 11.4 | Normal|AD | 10 | 12.6 | 0.00815 | 0.0588 | 0.648 | False |
| 6 | M6.spread_N | 11.4 | Normal|AD | 10 | 12.6 | 0.00818 | 0.0589 | 0.647 | False |
| 7 | M5.C2 | 4.89 | Normal|AD | 3.43 | 4.8 | 0.00603 | 0.0214 | 1.04 | False |
| 8 | M6.A[3.20] | 4.67 | Normal|AD | 4.3 | 10.3 | 0.062 | 0.77 | 0.995 | False |
| 9 | M6.N[3.20] | 4.67 | Normal|AD | 4.3 | 10.3 | 0.062 | 0.77 | 0.995 | False |
| 10 | M7.D2 | 3.04 | Normal|AD | 2.62 | 6.12 | 0.0201 | 1.42 | 1.09 | False |
| 11 | M6.N[3.25] | 2.82 | Normal|AD | 2.54 | 7.15 | 0.117 | 1.07 | 0.979 | False |
| 12 | M6.A[3.25] | 2.82 | Normal|AD | 2.54 | 7.15 | 0.117 | 1.07 | 0.979 | False |
| 13 | M7.D1 | 2.8 | Normal|AD | 1.59 | 2.71 | 0.00756 | 5.14 | 1.1 | False |
| 14 | M5.C2[k3] | 2.71 | Normal|AD | 2.16 | 4.62 | 0.044 | 0.0924 | 0.87 | True |
| 15 | M7.D_pow | 1.93 | Normal|AD | 1.47 | 3.5 | 0.0518 | 2.61 | 0.983 | False |
| 36 | M2.R | 0.856 | Normal|AD | 0.816 | 5.92 | 0.237 | 0.322 | 0.575 | False |
| 71 | M1.Sii_dBavg | 0.26 | Normal|AD | 0.247 | 3.18 | 0.355 | 0.259 | 1.14 | False |

Top 10 by J_eff (port asymmetry included), scheme `binary`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 2 | M5.C3[k3] | 51.7 | Normal|AD | 15.6 | 6.68 | 4.98e-10 | 0.0374 | 0.924 | True |
| 4 | M0.old_score | 17.3 | Normal|AD | 13.8 | 11.7 | 0.00048 | 0.165 | 0.847 | False |
| 1 | M5.C3 | 58 | Normal|AD | 12.5 | 5.64 | 4.5e-09 | 0.00944 | 1.11 | False |
| 3 | M5.C3_dBavg[k3] | 27.7 | Normal|AD | 10.3 | 5.71 | 1.08e-06 | 0.0688 | 0.897 | True |
| 5 | M6.spread_A | 11.4 | Normal|AD | 10 | 12.6 | 0.00815 | 0.0588 | 0.648 | False |
| 6 | M6.spread_N | 11.4 | Normal|AD | 10 | 12.6 | 0.00818 | 0.0589 | 0.647 | False |
| 8 | M6.A[3.20] | 4.67 | Normal|AD | 4.3 | 10.3 | 0.062 | 0.77 | 0.995 | False |
| 9 | M6.N[3.20] | 4.67 | Normal|AD | 4.3 | 10.3 | 0.062 | 0.77 | 0.995 | False |
| 7 | M5.C2 | 4.89 | Normal|AD | 3.43 | 4.8 | 0.00603 | 0.0214 | 1.04 | False |
| 10 | M7.D2 | 3.04 | Normal|AD | 2.62 | 6.12 | 0.0201 | 1.42 | 1.09 | False |

## Ranking - scheme `three_merged` (three_merged:Normal|Mild+Moderate(Mild+Moderate)|Severe), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C2 | 12.6 | Mild+Moderate|Severe | 3.72 | 3.24 | 0.00563 | 0.0303 | 1.01 | False |
| 2 | M5.C2[k3] | 3.41 | Normal|Mild+Moderate | 1.93 | 2.99 | 0.0521 | 0.144 | 0.784 | False |
| 3 | M6.spread_A | 1.04 | Mild+Moderate|Severe | 0.915 | 3.87 | 0.235 | 0.222 | 0.398 | False |
| 4 | M6.spread_N | 1.03 | Mild+Moderate|Severe | 0.904 | 3.85 | 0.236 | 0.223 | 0.394 | False |
| 5 | M6.N[3.20] | 0.505 | Mild+Moderate|Severe | 0.454 | 2.98 | 0.307 | 2.35 | 0.967 | False |
| 6 | M6.A[3.20] | 0.505 | Mild+Moderate|Severe | 0.454 | 2.98 | 0.307 | 2.35 | 0.967 | False |
| 7 | M5.C[k3] | 0.462 | Normal|Mild+Moderate | 0.339 | 1.6 | 0.3 | 1.19 | 0.642 | False |
| 8 | M6.N[4.00] | 0.461 | Mild+Moderate|Severe | 0.434 | 3.85 | 0.316 | 1.27 | 0.969 | False |
| 9 | M6.A[4.00] | 0.461 | Mild+Moderate|Severe | 0.434 | 3.85 | 0.316 | 1.27 | 0.969 | False |
| 10 | M6.N[3.95] | 0.457 | Mild+Moderate|Severe | 0.417 | 3.1 | 0.314 | 1.61 | 0.967 | False |
| 11 | M6.A[3.95] | 0.457 | Mild+Moderate|Severe | 0.417 | 3.1 | 0.314 | 1.61 | 0.967 | False |
| 12 | M6.A[3.40] | 0.371 | Mild+Moderate|Severe | 0.352 | 3.71 | 0.333 | 1.06 | 0.96 | False |
| 13 | M6.N[3.40] | 0.369 | Mild+Moderate|Severe | 0.35 | 3.71 | 0.334 | 1.07 | 0.96 | False |
| 14 | M5.C1[k3] | 0.341 | Normal|Mild+Moderate | 0.254 | 1.41 | 0.32 | 1.35 | 0.598 | False |
| 15 | M6.N[3.35] | 0.315 | Normal|Mild+Moderate | 0.149 | 0.754 | 0.223 | 9.26 | 0.401 | False |
| 32 | M0.old_score | 0.155 | Mild+Moderate|Severe | 0.136 | 1.48 | 0.387 | 1.39 | 0.581 | False |
| 39 | M2.R | 0.149 | Mild+Moderate|Severe | 0.139 | 2.13 | 0.376 | 0.629 | 0.516 | False |
| 64 | M1.Sii_dBavg | 0.0526 | Normal|Severe | 0.0487 | 1.15 | 0.407 | 0.603 | 1.04 | False |
| 78 | M5.C3[k3] | 0.00436 | Mild+Moderate|Severe | 0.00192 | 0.0829 | 0.398 | 3.29 | -0.458 | False |

Top 10 by J_eff (port asymmetry included), scheme `three_merged`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C2 | 12.6 | Mild+Moderate|Severe | 3.72 | 3.24 | 0.00563 | 0.0303 | 1.01 | False |
| 2 | M5.C2[k3] | 3.41 | Normal|Mild+Moderate | 1.93 | 2.99 | 0.0521 | 0.144 | 0.784 | False |
| 3 | M6.spread_A | 1.04 | Mild+Moderate|Severe | 0.915 | 3.87 | 0.235 | 0.222 | 0.398 | False |
| 4 | M6.spread_N | 1.03 | Mild+Moderate|Severe | 0.904 | 3.85 | 0.236 | 0.223 | 0.394 | False |
| 5 | M6.N[3.20] | 0.505 | Mild+Moderate|Severe | 0.454 | 2.98 | 0.307 | 2.35 | 0.967 | False |
| 6 | M6.A[3.20] | 0.505 | Mild+Moderate|Severe | 0.454 | 2.98 | 0.307 | 2.35 | 0.967 | False |
| 8 | M6.N[4.00] | 0.461 | Mild+Moderate|Severe | 0.434 | 3.85 | 0.316 | 1.27 | 0.969 | False |
| 9 | M6.A[4.00] | 0.461 | Mild+Moderate|Severe | 0.434 | 3.85 | 0.316 | 1.27 | 0.969 | False |
| 10 | M6.N[3.95] | 0.457 | Mild+Moderate|Severe | 0.417 | 3.1 | 0.314 | 1.61 | 0.967 | False |
| 11 | M6.A[3.95] | 0.457 | Mild+Moderate|Severe | 0.417 | 3.1 | 0.314 | 1.61 | 0.967 | False |

## Ranking - scheme `three` (three:Normal|Mild|Severe), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C2 | 16.3 | Mild|Severe | 4.2 | 3.36 | 0.00207 | 0.0271 | 0.999 | False |
| 2 | M5.C2[k3] | 4.98 | Mild|Severe | 3.12 | 4.09 | 0.0572 | 0.121 | 0.847 | False |
| 3 | M6.spread_A | 1.4 | Mild|Severe | 1.23 | 4.49 | 0.201 | 0.195 | 0.447 | False |
| 4 | M6.spread_N | 1.39 | Mild|Severe | 1.22 | 4.47 | 0.203 | 0.195 | 0.444 | False |
| 5 | M7.D1 | 1.33 | Mild|Severe | 0.686 | 1.68 | 0.205 | 6.5 | 1.1 | False |
| 6 | M6.N[3.95] | 0.752 | Mild|Severe | 0.671 | 3.55 | 0.261 | 1.35 | 0.963 | False |
| 7 | M6.A[3.95] | 0.752 | Mild|Severe | 0.671 | 3.55 | 0.261 | 1.35 | 0.963 | False |
| 8 | M6.N[4.00] | 0.626 | Normal|Mild | 0.592 | 4.59 | 0.288 | 1.03 | 0.964 | False |
| 9 | M6.A[4.00] | 0.626 | Normal|Mild | 0.592 | 4.58 | 0.288 | 1.03 | 0.964 | False |
| 10 | M6.N[3.20] | 0.568 | Mild|Severe | 0.49 | 2.69 | 0.296 | 2.17 | 0.971 | False |
| 11 | M6.A[3.20] | 0.567 | Mild|Severe | 0.49 | 2.69 | 0.296 | 2.17 | 0.971 | False |
| 12 | M8.lam3^2 | 0.494 | Mild|Severe | 0.454 | 3.38 | 0.295 | 0.571 | 0.219 | False |
| 13 | M6.N[3.55] | 0.486 | Mild|Severe | 0.267 | 1.09 | 0.184 | 2.65 | 0.925 | False |
| 14 | M8.lam2^2 | 0.482 | Mild|Severe | 0.442 | 3.27 | 0.288 | 0.562 | 0.242 | False |
| 15 | M7.D | 0.481 | Mild|Severe | 0.398 | 2.14 | 0.111 | 2.88 | 1.04 | False |
| 20 | M2.R | 0.461 | Mild|Severe | 0.422 | 3.19 | 0.301 | 0.59 | 0.235 | False |
| 59 | M5.C3[k3] | 0.0626 | Mild|Severe | 0.0265 | 0.303 | 0.39 | 0.877 | 0.52 | False |
| 63 | M1.Sii_dBavg | 0.0526 | Normal|Severe | 0.0487 | 1.15 | 0.407 | 0.603 | 1.07 | False |
| 68 | M0.old_score | 0.031 | Mild|Severe | 0.0273 | 0.682 | 0.4 | 2.74 | -0.0669 | False |

Top 10 by J_eff (port asymmetry included), scheme `three`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C2 | 16.3 | Mild|Severe | 4.2 | 3.36 | 0.00207 | 0.0271 | 0.999 | False |
| 2 | M5.C2[k3] | 4.98 | Mild|Severe | 3.12 | 4.09 | 0.0572 | 0.121 | 0.847 | False |
| 3 | M6.spread_A | 1.4 | Mild|Severe | 1.23 | 4.49 | 0.201 | 0.195 | 0.447 | False |
| 4 | M6.spread_N | 1.39 | Mild|Severe | 1.22 | 4.47 | 0.203 | 0.195 | 0.444 | False |
| 5 | M7.D1 | 1.33 | Mild|Severe | 0.686 | 1.68 | 0.205 | 6.5 | 1.1 | False |
| 6 | M6.N[3.95] | 0.752 | Mild|Severe | 0.671 | 3.55 | 0.261 | 1.35 | 0.963 | False |
| 7 | M6.A[3.95] | 0.752 | Mild|Severe | 0.671 | 3.55 | 0.261 | 1.35 | 0.963 | False |
| 8 | M6.N[4.00] | 0.626 | Normal|Mild | 0.592 | 4.59 | 0.288 | 1.03 | 0.964 | False |
| 9 | M6.A[4.00] | 0.626 | Normal|Mild | 0.592 | 4.58 | 0.288 | 1.03 | 0.964 | False |
| 10 | M6.N[3.20] | 0.568 | Mild|Severe | 0.49 | 2.69 | 0.296 | 2.17 | 0.971 | False |

## Ranking - scheme `binary_early` (binary_early:Normal|MCI), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M7.D1 | 3.29e+04 | Normal|MCI | 169 | 18.4 | 0 | 0.941 | 1.11 | False |
| 2 | M7.D | 6.48e+03 | Normal|MCI | 194 | 20 | 0 | 0.606 | 1.11 | False |
| 3 | M7.D0 | 6.28e+03 | Normal|MCI | 190 | 19.8 | 0 | 0.601 | 1.11 | False |
| 4 | M7.D3 | 4.43e+03 | Normal|MCI | 95.2 | 13.9 | 0 | 1.2 | 1.11 | False |
| 5 | M7.D3[k3] | 2.07e+03 | Normal|MCI | 92.4 | 13.9 | 3.31e-236 | 1.35 | 0.796 | False |
| 6 | M7.D2 | 790 | Normal|MCI | 133 | 17.9 | 1.69e-99 | 1.1 | 1.11 | False |
| 7 | M7.D_pow | 468 | Normal|MCI | 56.5 | 11.3 | 1.66e-53 | 0.949 | 1.09 | False |
| 8 | M6.A[3.60] | 126 | Normal|MCI | 81.7 | 21.6 | 1.25e-23 | 0.549 | 0.78 | False |
| 9 | M6.N[3.60] | 121 | Normal|MCI | 80 | 21.8 | 7.89e-23 | 0.546 | 0.781 | False |
| 10 | M5.C2 | 23 | Normal|MCI | 0.683 | 1.19 | 0.000344 | 0.142 | 1.14 | False |
| 11 | M5.C3[k3] | 14.2 | Normal|MCI | 0.514 | 1.03 | 0.00307 | 0.292 | 0.891 | False |
| 12 | M6.A[3.75] | 14 | Normal|MCI | 13.4 | 24.7 | 0.000111 | 0.195 | 0.941 | True |
| 13 | M6.N[3.75] | 14 | Normal|MCI | 13.4 | 24.7 | 0.000113 | 0.194 | 0.941 | True |
| 14 | M5.C3 | 13.9 | Normal|MCI | 0.945 | 1.42 | 0.00125 | 0.0435 | 1.12 | False |
| 15 | M5.C3_dBavg[k3] | 13 | Normal|MCI | 0.521 | 1.04 | 0.00347 | 0.659 | 0.859 | False |
| 39 | M0.old_score | 3.14 | Normal|MCI | 1.67 | 2.67 | 0.103 | 0.938 | 1.22 | False |
| 60 | M2.R | 0.672 | Normal|MCI | 0.626 | 4.25 | 0.149 | 0.696 | 1.19 | False |
| 72 | M1.Sii_dBavg | 0.105 | Normal|MCI | 0.1 | 2.15 | 0.055 | 0.523 | 0.723 | False |

Top 10 by J_eff (port asymmetry included), scheme `binary_early`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 2 | M7.D | 6.48e+03 | Normal|MCI | 194 | 20 | 0 | 0.606 | 1.11 | False |
| 3 | M7.D0 | 6.28e+03 | Normal|MCI | 190 | 19.8 | 0 | 0.601 | 1.11 | False |
| 1 | M7.D1 | 3.29e+04 | Normal|MCI | 169 | 18.4 | 0 | 0.941 | 1.11 | False |
| 6 | M7.D2 | 790 | Normal|MCI | 133 | 17.9 | 1.69e-99 | 1.1 | 1.11 | False |
| 4 | M7.D3 | 4.43e+03 | Normal|MCI | 95.2 | 13.9 | 0 | 1.2 | 1.11 | False |
| 5 | M7.D3[k3] | 2.07e+03 | Normal|MCI | 92.4 | 13.9 | 3.31e-236 | 1.35 | 0.796 | False |
| 8 | M6.A[3.60] | 126 | Normal|MCI | 81.7 | 21.6 | 1.25e-23 | 0.549 | 0.78 | False |
| 9 | M6.N[3.60] | 121 | Normal|MCI | 80 | 21.8 | 7.89e-23 | 0.546 | 0.781 | False |
| 7 | M7.D_pow | 468 | Normal|MCI | 56.5 | 11.3 | 1.66e-53 | 0.949 | 1.09 | False |
| 12 | M6.A[3.75] | 14 | Normal|MCI | 13.4 | 24.7 | 0.000111 | 0.195 | 0.941 | True |

## Power averaging vs dB averaging (min pairwise J_meas)
| scheme | pair | profile | J_dB | J_pow | ratio_pow/dB | shift_move_dB | shift_move_pow |
|---|---|---|---|---|---|---|---|
| binary | M1.Sii_dBavg vs M2.R | good | 0.26 | 0.876 | 3.37 | 0.259 | 0.322 |
| binary | M1.Sii_dBavg vs M2.R | typical | 0.26 | 0.856 | 3.29 | 0.259 | 0.322 |
| binary | M1.Sii_dBavg vs M2.R | very_noisy | 0.245 | 0.622 | 2.54 | 0.259 | 0.322 |
| binary | M1.Sii_dBavg vs M2.R | typical_jitter | 0.243 | 0.844 | 3.47 | 0.259 | 0.322 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | good | 3.12 | 0.878 | 0.282 | 0.382 | 0.324 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.646 | 0.858 | 1.33 | 0.382 | 0.324 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.468 | 0.621 | 1.33 | 0.382 | 0.324 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.66 | 0.846 | 1.28 | 0.382 | 0.324 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 27.8 | 52.5 | 1.89 | 0.0688 | 0.0374 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 27.7 | 51.7 | 1.87 | 0.0688 | 0.0374 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 11.7 | 13.4 | 1.14 | 0.0688 | 0.0374 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 27.5 | 51.4 | 1.87 | 0.0688 | 0.0374 |
| three_merged | M1.Sii_dBavg vs M2.R | good | 0.0525 | 0.15 | 2.85 | 0.603 | 0.629 |
| three_merged | M1.Sii_dBavg vs M2.R | typical | 0.0526 | 0.149 | 2.83 | 0.603 | 0.629 |
| three_merged | M1.Sii_dBavg vs M2.R | very_noisy | 0.0495 | 0.108 | 2.18 | 0.603 | 0.629 |
| three_merged | M1.Sii_dBavg vs M2.R | typical_jitter | 0.0462 | 0.148 | 3.2 | 0.603 | 0.629 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | good | 0.495 | 0.148 | 0.299 | 0.861 | 0.64 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.155 | 0.147 | 0.952 | 0.861 | 0.64 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.0767 | 0.107 | 1.39 | 0.861 | 0.64 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.204 | 0.147 | 0.718 | 0.861 | 0.64 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 0.0414 | 0.00397 | 0.0959 | 1.32 | 3.29 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 0.0426 | 0.00436 | 0.102 | 1.32 | 3.29 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.00342 | 0.000425 | 0.124 | 1.32 | 3.29 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 0.0415 | 0.0042 | 0.101 | 1.32 | 3.29 |
| three | M1.Sii_dBavg vs M2.R | good | 0.0525 | 0.468 | 8.91 | 0.603 | 0.59 |
| three | M1.Sii_dBavg vs M2.R | typical | 0.0526 | 0.461 | 8.76 | 0.603 | 0.59 |
| three | M1.Sii_dBavg vs M2.R | very_noisy | 0.0495 | 0.297 | 6 | 0.603 | 0.59 |
| three | M1.Sii_dBavg vs M2.R | typical_jitter | 0.0462 | 0.447 | 9.66 | 0.603 | 0.59 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | good | 1.19 | 0.464 | 0.391 | 0.644 | 0.591 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.305 | 0.457 | 1.5 | 0.644 | 0.591 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.102 | 0.294 | 2.89 | 0.644 | 0.591 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.333 | 0.443 | 1.33 | 0.644 | 0.591 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 0.16 | 0.0591 | 0.369 | 0.715 | 0.877 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 0.165 | 0.0626 | 0.379 | 0.715 | 0.877 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.0294 | 0.0202 | 0.687 | 0.715 | 0.877 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 0.16 | 0.0597 | 0.374 | 0.715 | 0.877 |
| binary_early | M1.Sii_dBavg vs M2.R | good | 0.108 | 0.705 | 6.51 | 0.523 | 0.696 |
| binary_early | M1.Sii_dBavg vs M2.R | typical | 0.105 | 0.672 | 6.42 | 0.523 | 0.696 |
| binary_early | M1.Sii_dBavg vs M2.R | very_noisy | 0.0913 | 0.295 | 3.23 | 0.523 | 0.696 |
| binary_early | M1.Sii_dBavg vs M2.R | typical_jitter | 0.105 | 0.591 | 5.64 | 0.523 | 0.696 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | good | 0.616 | 0.707 | 1.15 | 1.5 | 0.695 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.000782 | 0.674 | 862 | 1.5 | 0.695 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.0416 | 0.296 | 7.12 | 1.5 | 0.695 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 5.45e-05 | 0.593 | 1.09e+04 | 1.5 | 0.695 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 20.5 | 28.2 | 1.37 | 0.659 | 0.292 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 13 | 14.2 | 1.09 | 0.659 | 0.292 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.255 | 0.309 | 1.21 | 0.659 | 0.292 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 12 | 13.4 | 1.12 | 0.659 | 0.292 |

## Robustness: |Δ metric| / |Normal - Mild gap| (selected)
| metric | shift-2 | shift+10 | shift-20 | band_shrink10 | band_lo10 | band_3.4-3.9 | band_3.2-3.5_nodip | flatten_notch | detune+200 | one_open |
|---|---|---|---|---|---|---|---|---|---|---|
| M0.old_score | 0.032 | 0.15 | 0.34 | 2.2 | 3.1 | 12 | 10 | 1.2 | 2.6 | 5.9 |
| M1.Sii_dBavg | 0.058 | 0.058 | 0.13 | 2.9 | 3.2 | 21 | 4.8 | 7.9 | 0.98 | 5.2 |
| M2.R | 0.11 | 0.56 | 1.2 | 12 | 15 | 74 | 29 | 16 | 9.3 | 27 |
| M3.ML_of_powavg | 0.11 | 0.56 | 1.2 | 11 | 14 | 61 | 27 | 17 | 9.1 | 1.9e+02 |
| M4.N | 0.11 | 0.56 | 1.2 | 12 | 15 | 74 | 29 | 16 | 9.3 | 27 |
| M5.C | 0.003 | 0.015 | 0.034 | 3.1 | 3.2 | 26 | 14 | 1.3e-13 | 0.29 | 9.4 |
| M5.C3 | 0.0019 | 0.0093 | 0.021 | 0.31 | 0.36 | 1.6 | 2.8 | 0 | 0.17 | 1.1 |
| M5.C3[k3] | 0.0072 | 0.032 | 0.085 | 0.064 | 0.07 | n/a | n/a | 0 | 1.7 | 0.94 |
| M6.fc_A | 1.8 | 9.2 | 18 | 8.4 | 14 | 36 | 2.9e+02 | 4.5 | 1.7e+02 | 1.6e+02 |
| M6.spread_A | 0.011 | 0.067 | 0.1 | 5 | 4.5 | 29 | 48 | 1.6 | 5.7 | 13 |
| M7.D | 0.2 | 1.3 | 2.6 | 0.28 | 0.28 | 2.5 | 2 | 2 | 45 | 95 |
| M7.D_pow | 0.31 | 2 | 3.8 | 0.29 | 0.3 | 2.4 | 2 | 6 | 1.2e+02 | 63 |
| M7.D3[k3] | 0.46 | 2.6 | 5.6 | 0.13 | 0.57 | n/a | n/a | 0 | 14 | 2.6 |
| M8.s1^2 | 1.8 | 9 | 20 | 1.9e+02 | 2.3e+02 | 1.2e+03 | 4.8e+02 | 2.8e+02 | 1.5e+02 | 2.6e+03 |
| M8.lam0^2 | 0.11 | 0.56 | 1.2 | 12 | 14 | 74 | 27 | 16 | 9.3 | 27 |
| M8.lam0^2[k3] | 0.17 | 0.91 | 1.7 | 0.73 | 2.4 | n/a | n/a | 4 | 34 | 12 |
| M8.lam3^2[k3] | 0.11 | 0.57 | 1.1 | 0.65 | 1.5 | n/a | n/a | 3.3 | 28 | 9.9 |

## Faults (open / short all antennas, one antenna open)
| metric | open_all: finite | short_all: finite | one_open: in class range | open_all: in class range | short_all: in class range |
|---|---|---|---|---|---|
| M0.old_score | True | True | False | False | False |
| M1.Sii_dBavg | True | True | False | False | False |
| M2.R | True | True | False | False | False |
| M3.ML_of_powavg | False | False | False | False | False |
| M4.N | True | True | False | False | False |
| M5.C | True | True | False | False | False |
| M5.C3 | True | True | True | False | False |
| M5.C3[k3] | True | True | True | False | False |
| M6.fc_A | True | True | False | False | False |
| M6.spread_A | True | True | True | False | False |
| M7.D | True | True | False | False | False |
| M7.D_pow | True | True | False | False | False |
| M7.D3[k3] | True | True | True | False | False |
| M8.s1^2 | True | True | False | False | False |
| M8.lam0^2 | True | True | False | False | False |
| M8.lam0^2[k3] | True | True | False | False | False |
| M8.lam3^2[k3] | True | True | False | False | False |

## Ordinality: stage-to-stage steps in port-noise units (noise-free, all 4 stages)
17 of 83 metrics are monotone over Normal < Mild < Moderate < Severe. Normal->Mild and Moderate->Severe cross HFSS projects; Mild->Moderate does not (see summary caveat).
| metric | monotone | Normal->MCI / port | MCI->Mild / port | Mild->Moderate / port | Moderate->Severe / port |
|---|---|---|---|---|---|
| M0.old_score | False | 2.3 | 11 | -1.5 | 2.3 |
| M2.R | True | -2.5 | -0.45 | -3.1 | -1.2 |
| M5.C | False | 3.8 | -5.6 | 0.53 | -4.7 |
| M5.C3 | False | 1.4 | -7.6 | -0.45 | -0.052 |
| M5.C3[k3] | False | 0.98 | -8.4 | -0.48 | 0.15 |
| M6.A[3.40] | False | 4.4 | -8.7 | -0.073 | -4 |
| M6.A[3.45] | False | 10 | -14 | 0.34 | -1.8 |
| M7.D3 | False | 14 | -8.2 | -1.9 | 3.3 |
| M7.D3[k3] | False | 11 | -5.6 | -1.3 | 4.9 |
| M8.lam0^2[k3] | False | -3 | 6.5 | -0.76 | 2.7 |
| M8.lam3^2[k3] | False | -3.9 | 7.7 | -0.9 | 2.4 |

## M0 decomposition (couplings zeroed)
M0 = mean_B Σ_(j≠i)|S_ii + S_ij| / VSWR_i. With every S_ij set to 0 the score is almost unchanged, i.e. M0 is in practice (N-1)·<|Γ|/VSWR>: a reflection-only quantity with an arbitrary weighting.
| stage | M0 | M0_couplings_zeroed |
|---|---|---|
| Normal | 0.54891 | 0.55155 |
| Normal | 0.54762 | 0.54897 |
| MCI | 0.55099 | 0.55143 |
| Mild | 0.5596 | 0.5618 |
| Mild | 0.56841 | 0.56885 |
| Moderate | 0.56083 | 0.56292 |
| Moderate | 0.56353 | 0.56453 |
| Severe | 0.56201 | 0.56423 |
| Severe | 0.56786 | 0.56893 |
