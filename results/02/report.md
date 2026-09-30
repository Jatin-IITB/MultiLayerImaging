# Prompt 02 - metric separability (track A, code f142bf6, sim_set hfss-v2-sameproject-masked)

J_meas = min pairwise Fisher ratio from noisy realisations (ranking key). J_eff adds the port-to-port asymmetry as extra variance. gap/port = class gap / port-to-port std. gap/mesh = pending (mesh-repeat not yet available). shift_move = largest change under ±2/5/10 MHz resonance shifts / smallest class gap. band_gap_retention = worst (gap after ±10 % band change) / (original gap); < 0 means the class order flips. freq_robust (brief's literal criterion) = shift AND band value changes < 0.25 × smallest gap. AD-vs-AD pairs unverified against mesh noise.

Glitch masking ON: 7 in-band (f, pair) points masked in 2 runs (results/qc/masked_points.csv).

## Ranking - scheme `binary` (binary:Normal|AD(Mild+Moderate+Severe)), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C3[k3] | 419 | Normal|AD | 32.5 | 8.39 | 3.22e-54 | 0.03 | 0.9 | True |
| 2 | M5.C3_dBavg[k3] | 264 | Normal|AD | 40.7 | 9.81 | 2.82e-40 | 0.0498 | 0.876 | True |
| 3 | M5.C3 | 158 | Normal|AD | 18 | 6.38 | 1.53e-26 | 0.000548 | 1.11 | False |
| 4 | M6.N[3.65] | 75.1 | Normal|AD | 11.4 | 5.19 | 1.38e-13 | 1.32 | 0.856 | False |
| 5 | M6.A[3.65] | 73.2 | Normal|AD | 11.3 | 5.18 | 2.42e-13 | 1.33 | 0.855 | False |
| 6 | M6.N[3.85] | 45.3 | Normal|AD | 13.9 | 6.32 | 6.14e-07 | 1.17 | 0.93 | False |
| 7 | M6.A[3.85] | 45.3 | Normal|AD | 13.9 | 6.32 | 6.14e-07 | 1.17 | 0.93 | False |
| 8 | M0.old_score | 41.5 | Normal|AD | 38.4 | 31.9 | 5.54e-07 | 0.0317 | 1.07 | False |
| 9 | M7.D2 | 29.2 | Normal|AD | 19.8 | 11.1 | 5.89e-08 | 1.27 | 1.11 | False |
| 10 | M6.A[3.25] | 21.6 | Normal|AD | 13.4 | 8.36 | 0.000491 | 1.04 | 0.983 | False |
| 11 | M6.N[3.25] | 21.6 | Normal|AD | 13.3 | 8.36 | 0.000493 | 1.04 | 0.983 | False |
| 12 | M6.N[3.30] | 14.6 | Normal|AD | 5.4 | 4.14 | 0.00312 | 2.1 | 0.895 | False |
| 13 | M6.A[3.30] | 14.6 | Normal|AD | 5.4 | 4.14 | 0.00312 | 2.1 | 0.895 | False |
| 14 | M6.A[3.80] | 14.5 | Normal|AD | 4.46 | 3.59 | 0.000555 | 1.78 | 0.672 | False |
| 15 | M6.N[3.80] | 14.4 | Normal|AD | 4.44 | 3.59 | 0.000576 | 1.78 | 0.672 | False |
| 42 | M2.R | 5.61 | Normal|AD | 5.32 | 14.4 | 0.0209 | 0.0491 | 1.05 | False |
| 77 | M1.Sii_dBavg | 1.02 | Normal|AD | 0.975 | 6.66 | 0.0438 | 0.0432 | 1.13 | False |

Top 10 by J_eff (port asymmetry included), scheme `binary`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 2 | M5.C3_dBavg[k3] | 264 | Normal|AD | 40.7 | 9.81 | 2.82e-40 | 0.0498 | 0.876 | True |
| 8 | M0.old_score | 41.5 | Normal|AD | 38.4 | 31.9 | 5.54e-07 | 0.0317 | 1.07 | False |
| 1 | M5.C3[k3] | 419 | Normal|AD | 32.5 | 8.39 | 3.22e-54 | 0.03 | 0.9 | True |
| 9 | M7.D2 | 29.2 | Normal|AD | 19.8 | 11.1 | 5.89e-08 | 1.27 | 1.11 | False |
| 3 | M5.C3 | 158 | Normal|AD | 18 | 6.38 | 1.53e-26 | 0.000548 | 1.11 | False |
| 7 | M6.A[3.85] | 45.3 | Normal|AD | 13.9 | 6.32 | 6.14e-07 | 1.17 | 0.93 | False |
| 6 | M6.N[3.85] | 45.3 | Normal|AD | 13.9 | 6.32 | 6.14e-07 | 1.17 | 0.93 | False |
| 16 | M7.D3 | 13.6 | Normal|AD | 13.4 | 45.2 | 3.13e-05 | 1.34 | 1.11 | False |
| 10 | M6.A[3.25] | 21.6 | Normal|AD | 13.4 | 8.36 | 0.000491 | 1.04 | 0.983 | False |
| 11 | M6.N[3.25] | 21.6 | Normal|AD | 13.3 | 8.36 | 0.000493 | 1.04 | 0.983 | False |

## Ranking - scheme `three_merged` (three_merged:Normal|Mild+Moderate(Mild+Moderate)|Severe), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C2 | 283 | Mild+Moderate|Severe | 14.4 | 5.52 | 9.59e-35 | 0.000943 | 1.11 | False |
| 2 | M7.D3[k3] | 64.5 | Mild+Moderate|Severe | 46.7 | 18.4 | 1.27e-11 | 1.74 | 0.806 | False |
| 3 | M5.C2[k3] | 61.7 | Normal|Mild+Moderate | 15.8 | 6.52 | 6.28e-11 | 0.106 | 0.867 | False |
| 4 | M6.A[3.40] | 47.6 | Normal|Mild+Moderate | 5.36 | 3.48 | 3.08e-08 | 1.66 | 0.959 | False |
| 5 | M6.N[3.40] | 47.3 | Normal|Mild+Moderate | 5.34 | 3.47 | 3.31e-08 | 1.66 | 0.959 | False |
| 6 | M6.A[3.45] | 42.2 | Normal|Mild+Moderate | 3.1 | 2.58 | 1.25e-06 | 1.35 | 0.772 | False |
| 7 | M6.N[3.45] | 42.1 | Normal|Mild+Moderate | 3.06 | 2.56 | 1.28e-06 | 1.36 | 0.77 | False |
| 8 | M5.C | 20.5 | Normal|Mild+Moderate | 0.834 | 1.32 | 0.000185 | 0.000587 | 1.11 | False |
| 9 | M5.C1 | 18.6 | Normal|Mild+Moderate | 0.718 | 1.22 | 0.000376 | 0.000441 | 1.11 | False |
| 10 | M7.D3 | 13.6 | Mild+Moderate|Severe | 12.5 | 17.4 | 0.000299 | 2.57 | 1.11 | False |
| 11 | M5.C1[k3] | 12.7 | Mild+Moderate|Severe | 3.84 | 3.24 | 0.00028 | 0.962 | 0.617 | False |
| 12 | M5.C[k3] | 12.4 | Mild+Moderate|Severe | 4.42 | 3.45 | 0.000339 | 1 | 0.636 | False |
| 13 | M5.C3 | 10.7 | Mild+Moderate|Severe | 5.13 | 4.45 | 0.00403 | 0.00372 | 1.11 | False |
| 14 | M6.A[3.70] | 7.93 | Normal|Mild+Moderate | 0.744 | 1.28 | 0.0211 | 4.54 | 0.165 | False |
| 15 | M6.N[3.70] | 7.64 | Normal|Mild+Moderate | 0.731 | 1.27 | 0.023 | 4.56 | 0.159 | False |
| 22 | M2.R | 4.89 | Mild+Moderate|Severe | 4.21 | 7.76 | 0.0345 | 0.0708 | 1.03 | False |
| 36 | M0.old_score | 3.73 | Mild+Moderate|Severe | 3.35 | 8.13 | 0.0761 | 0.135 | 0.957 | False |
| 40 | M5.C3[k3] | 2.96 | Mild+Moderate|Severe | 1.04 | 1.79 | 0.0868 | 0.442 | 0.786 | False |
| 62 | M1.Sii_dBavg | 1.17 | Mild+Moderate|Severe | 1.1 | 2.75 | 0.0376 | 0.167 | 1.09 | False |

Top 10 by J_eff (port asymmetry included), scheme `three_merged`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 2 | M7.D3[k3] | 64.5 | Mild+Moderate|Severe | 46.7 | 18.4 | 1.27e-11 | 1.74 | 0.806 | False |
| 3 | M5.C2[k3] | 61.7 | Normal|Mild+Moderate | 15.8 | 6.52 | 6.28e-11 | 0.106 | 0.867 | False |
| 1 | M5.C2 | 283 | Mild+Moderate|Severe | 14.4 | 5.52 | 9.59e-35 | 0.000943 | 1.11 | False |
| 10 | M7.D3 | 13.6 | Mild+Moderate|Severe | 12.5 | 17.4 | 0.000299 | 2.57 | 1.11 | False |
| 4 | M6.A[3.40] | 47.6 | Normal|Mild+Moderate | 5.36 | 3.48 | 3.08e-08 | 1.66 | 0.959 | False |
| 5 | M6.N[3.40] | 47.3 | Normal|Mild+Moderate | 5.34 | 3.47 | 3.31e-08 | 1.66 | 0.959 | False |
| 13 | M5.C3 | 10.7 | Mild+Moderate|Severe | 5.13 | 4.45 | 0.00403 | 0.00372 | 1.11 | False |
| 19 | M8.lam3^2 | 5.64 | Mild+Moderate|Severe | 4.83 | 8.17 | 0.0264 | 0.0692 | 1.03 | False |
| 20 | M8.lam2^2 | 5.15 | Mild+Moderate|Severe | 4.44 | 8.05 | 0.0312 | 0.0669 | 1.03 | False |
| 12 | M5.C[k3] | 12.4 | Mild+Moderate|Severe | 4.42 | 3.45 | 0.000339 | 1 | 0.636 | False |

## Ranking - scheme `three` (three:Normal|Mild|Severe), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M7.D1 | 2.88e+03 | Mild|Severe | 81.8 | 13 | 0 | 11.9 | 1.11 | False |
| 2 | M6.A[3.60] | 975 | Normal|Severe | 13.7 | 5.27 | 1.43e-110 | 1.79 | 0.804 | False |
| 3 | M6.N[3.60] | 902 | Normal|Severe | 13 | 5.13 | 1.77e-102 | 1.85 | 0.797 | False |
| 4 | M7.D3[k3] | 578 | Mild|Severe | 122 | 17.6 | 1.14e-66 | 1.98 | 0.791 | False |
| 5 | M5.C2 | 520 | Mild|Severe | 20 | 6.45 | 6.65e-59 | 0.000985 | 1.11 | False |
| 6 | M5.C1[k3] | 463 | Mild|Severe | 8.9 | 4.23 | 1.12e-52 | 1.33 | 0.645 | False |
| 7 | M7.D | 449 | Normal|Severe | 29 | 7.78 | 2.16e-51 | 2.47 | 1.04 | False |
| 8 | M7.D0 | 444 | Normal|Severe | 28.6 | 7.73 | 9.16e-51 | 2.42 | 1.03 | False |
| 9 | M5.C[k3] | 418 | Mild|Severe | 9.7 | 4.42 | 8.56e-48 | 1.4 | 0.656 | False |
| 10 | M5.C2[k3] | 368 | Mild|Severe | 34.2 | 8.69 | 2.36e-42 | 0.0965 | 0.903 | True |
| 11 | M7.D3 | 326 | Mild|Severe | 101 | 17.1 | 4.99e-38 | 3.51 | 1.11 | False |
| 12 | M6.A[3.75] | 177 | Normal|Severe | 8.29 | 4.17 | 2.3e-21 | 0.799 | 0.942 | False |
| 13 | M6.N[3.75] | 176 | Normal|Severe | 8.23 | 4.16 | 2.83e-21 | 0.802 | 0.941 | False |
| 14 | M6.A[3.40] | 144 | Normal|Mild | 2.56 | 2.28 | 9.19e-18 | 1.9 | 0.958 | False |
| 15 | M6.N[3.40] | 144 | Normal|Mild | 2.55 | 2.28 | 1.05e-17 | 1.9 | 0.958 | False |
| 29 | M5.C3[k3] | 20.3 | Mild|Severe | 3.29 | 2.8 | 0.000718 | 0.3 | 0.868 | False |
| 36 | M2.R | 11.7 | Normal|Mild | 6.08 | 5.02 | 0.00763 | 0.1 | 1.02 | False |
| 42 | M1.Sii_dBavg | 9.07 | Normal|Severe | 2.67 | 2.75 | 0.0166 | 0.167 | 1.09 | False |
| 60 | M0.old_score | 2.99 | Mild|Severe | 2.33 | 4.6 | 0.111 | 0.207 | 0.753 | False |

Top 10 by J_eff (port asymmetry included), scheme `three`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 4 | M7.D3[k3] | 578 | Mild|Severe | 122 | 17.6 | 1.14e-66 | 1.98 | 0.791 | False |
| 11 | M7.D3 | 326 | Mild|Severe | 101 | 17.1 | 4.99e-38 | 3.51 | 1.11 | False |
| 1 | M7.D1 | 2.88e+03 | Mild|Severe | 81.8 | 13 | 0 | 11.9 | 1.11 | False |
| 10 | M5.C2[k3] | 368 | Mild|Severe | 34.2 | 8.69 | 2.36e-42 | 0.0965 | 0.903 | True |
| 7 | M7.D | 449 | Normal|Severe | 29 | 7.78 | 2.16e-51 | 2.47 | 1.04 | False |
| 8 | M7.D0 | 444 | Normal|Severe | 28.6 | 7.73 | 9.16e-51 | 2.42 | 1.03 | False |
| 5 | M5.C2 | 520 | Mild|Severe | 20 | 6.45 | 6.65e-59 | 0.000985 | 1.11 | False |
| 16 | M5.C3 | 87.1 | Mild|Severe | 15 | 5.84 | 2e-11 | 0.00293 | 1.11 | False |
| 2 | M6.A[3.60] | 975 | Normal|Severe | 13.7 | 5.27 | 1.43e-110 | 1.79 | 0.804 | False |
| 3 | M6.N[3.60] | 902 | Normal|Severe | 13 | 5.13 | 1.77e-102 | 1.85 | 0.797 | False |

## Ranking - scheme `binary_early` (binary_early:Normal|MCI), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M7.D1 | 2.45e+04 | Normal|MCI | 139 | 16.7 | 0 | 1.53 | 1.11 | False |
| 2 | M6.A[3.60] | 4.5e+03 | Normal|MCI | 125 | 16.1 | 0 | 0.602 | 0.878 | False |
| 3 | M6.N[3.60] | 4.46e+03 | Normal|MCI | 128 | 16.2 | 0 | 0.599 | 0.878 | False |
| 4 | M7.D3 | 3.08e+03 | Normal|MCI | 79.2 | 12.7 | 0 | 1.92 | 1.11 | False |
| 5 | M7.D | 2.71e+03 | Normal|MCI | 330 | 27.4 | 5.02e-305 | 0.92 | 1.1 | False |
| 6 | M7.D0 | 2.63e+03 | Normal|MCI | 327 | 27.3 | 2.36e-296 | 0.91 | 1.1 | False |
| 7 | M7.D2 | 2.54e+03 | Normal|MCI | 172 | 19.2 | 4.84e-308 | 1.43 | 1.11 | False |
| 8 | M6.A[3.65] | 1.99e+03 | Normal|MCI | 27.3 | 7.44 | 3.18e-229 | 1.02 | 0.836 | False |
| 9 | M6.N[3.65] | 1.95e+03 | Normal|MCI | 27 | 7.39 | 6.77e-225 | 1.02 | 0.835 | False |
| 10 | M6.N[3.45] | 1.45e+03 | Normal|MCI | 231 | 23.4 | 1.57e-162 | 0.339 | 0.969 | False |
| 11 | M6.A[3.45] | 1.45e+03 | Normal|MCI | 230 | 23.4 | 3.24e-162 | 0.338 | 0.969 | False |
| 12 | M6.N[3.75] | 1.37e+03 | Normal|MCI | 137 | 17.5 | 2.13e-157 | 0.238 | 0.939 | True |
| 13 | M6.A[3.75] | 1.37e+03 | Normal|MCI | 137 | 17.5 | 2.65e-157 | 0.237 | 0.939 | True |
| 14 | M7.D3[k3] | 1.2e+03 | Normal|MCI | 78.8 | 13 | 7.14e-178 | 3.15 | 0.723 | False |
| 15 | M5.C1[k3] | 779 | Normal|MCI | 5.49 | 3.33 | 2.75e-87 | 0.905 | 0.679 | False |
| 18 | M1.Sii_dBavg | 213 | Normal|MCI | 59.7 | 12.9 | 2.85e-25 | 0.0348 | 1.1 | False |
| 43 | M5.C3[k3] | 16.4 | Normal|MCI | 0.484 | 0.999 | 0.00209 | 0.254 | 0.893 | False |
| 56 | M0.old_score | 1.14 | Normal|MCI | 0.963 | 3.51 | 0.224 | 0.352 | 1.17 | False |
| 62 | M2.R | 0.641 | Normal|MCI | 0.53 | 2.47 | 0.285 | 0.426 | 0.827 | False |

Top 10 by J_eff (port asymmetry included), scheme `binary_early`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 5 | M7.D | 2.71e+03 | Normal|MCI | 330 | 27.4 | 5.02e-305 | 0.92 | 1.1 | False |
| 6 | M7.D0 | 2.63e+03 | Normal|MCI | 327 | 27.3 | 2.36e-296 | 0.91 | 1.1 | False |
| 10 | M6.N[3.45] | 1.45e+03 | Normal|MCI | 231 | 23.4 | 1.57e-162 | 0.339 | 0.969 | False |
| 11 | M6.A[3.45] | 1.45e+03 | Normal|MCI | 230 | 23.4 | 3.24e-162 | 0.338 | 0.969 | False |
| 7 | M7.D2 | 2.54e+03 | Normal|MCI | 172 | 19.2 | 4.84e-308 | 1.43 | 1.11 | False |
| 1 | M7.D1 | 2.45e+04 | Normal|MCI | 139 | 16.7 | 0 | 1.53 | 1.11 | False |
| 13 | M6.A[3.75] | 1.37e+03 | Normal|MCI | 137 | 17.5 | 2.65e-157 | 0.237 | 0.939 | True |
| 12 | M6.N[3.75] | 1.37e+03 | Normal|MCI | 137 | 17.5 | 2.13e-157 | 0.238 | 0.939 | True |
| 3 | M6.N[3.60] | 4.46e+03 | Normal|MCI | 128 | 16.2 | 0 | 0.599 | 0.878 | False |
| 2 | M6.A[3.60] | 4.5e+03 | Normal|MCI | 125 | 16.1 | 0 | 0.602 | 0.878 | False |

## Power averaging vs dB averaging (min pairwise J_meas)
| scheme | pair | profile | J_dB | J_pow | ratio_pow/dB | shift_move_dB | shift_move_pow |
|---|---|---|---|---|---|---|---|
| binary | M1.Sii_dBavg vs M2.R | good | 1.03 | 6.12 | 5.94 | 0.0432 | 0.0491 |
| binary | M1.Sii_dBavg vs M2.R | typical | 1.02 | 5.61 | 5.5 | 0.0432 | 0.0491 |
| binary | M1.Sii_dBavg vs M2.R | very_noisy | 0.915 | 1.99 | 2.18 | 0.0432 | 0.0491 |
| binary | M1.Sii_dBavg vs M2.R | typical_jitter | 0.989 | 5.45 | 5.51 | 0.0432 | 0.0491 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | good | 2.52 | 6.22 | 2.47 | 0.134 | 0.0486 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | typical | 1.34 | 5.69 | 4.25 | 0.134 | 0.0486 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.785 | 2 | 2.54 | 0.134 | 0.0486 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 1.09 | 5.52 | 5.04 | 0.134 | 0.0486 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 312 | 555 | 1.78 | 0.0498 | 0.03 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 264 | 419 | 1.59 | 0.0498 | 0.03 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 12.5 | 14.8 | 1.19 | 0.0498 | 0.03 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 271 | 429 | 1.58 | 0.0498 | 0.03 |
| three_merged | M1.Sii_dBavg vs M2.R | good | 1.18 | 5.87 | 4.98 | 0.167 | 0.0708 |
| three_merged | M1.Sii_dBavg vs M2.R | typical | 1.17 | 4.89 | 4.17 | 0.167 | 0.0708 |
| three_merged | M1.Sii_dBavg vs M2.R | very_noisy | 0.574 | 1.19 | 2.07 | 0.167 | 0.0708 |
| three_merged | M1.Sii_dBavg vs M2.R | typical_jitter | 1.18 | 4.74 | 4.02 | 0.167 | 0.0708 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | good | 1.93 | 5.8 | 3.01 | 0.196 | 0.0709 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.871 | 4.85 | 5.56 | 0.196 | 0.0709 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.341 | 1.19 | 3.49 | 0.196 | 0.0709 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.69 | 4.69 | 6.8 | 0.196 | 0.0709 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 7.49 | 4.31 | 0.576 | 0.495 | 0.442 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 4.83 | 2.96 | 0.613 | 0.495 | 0.442 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.0451 | 0.0392 | 0.869 | 0.495 | 0.442 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 4.4 | 2.74 | 0.623 | 0.495 | 0.442 |
| three | M1.Sii_dBavg vs M2.R | good | 57.8 | 71.9 | 1.24 | 0.167 | 0.1 |
| three | M1.Sii_dBavg vs M2.R | typical | 9.07 | 11.7 | 1.3 | 0.167 | 0.1 |
| three | M1.Sii_dBavg vs M2.R | very_noisy | 0.574 | 0.67 | 1.17 | 0.167 | 0.1 |
| three | M1.Sii_dBavg vs M2.R | typical_jitter | 7.19 | 9.66 | 1.34 | 0.167 | 0.1 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | good | 1.41 | 71.9 | 51 | 0.218 | 0.0989 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.601 | 11.7 | 19.5 | 0.218 | 0.0989 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.325 | 0.671 | 2.06 | 0.218 | 0.0989 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.45 | 9.65 | 21.4 | 0.218 | 0.0989 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 238 | 190 | 0.8 | 0.365 | 0.3 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 24.7 | 20.3 | 0.824 | 0.365 | 0.3 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.0932 | 0.0885 | 0.95 | 0.365 | 0.3 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 18.6 | 16.3 | 0.876 | 0.365 | 0.3 |
| binary_early | M1.Sii_dBavg vs M2.R | good | 1.35e+03 | 4.24 | 0.00314 | 0.0348 | 0.426 |
| binary_early | M1.Sii_dBavg vs M2.R | typical | 213 | 0.641 | 0.00301 | 0.0348 | 0.426 |
| binary_early | M1.Sii_dBavg vs M2.R | very_noisy | 13.2 | 0.0603 | 0.00457 | 0.0348 | 0.426 |
| binary_early | M1.Sii_dBavg vs M2.R | typical_jitter | 181 | 0.657 | 0.00362 | 0.0348 | 0.426 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | good | 0.0654 | 4.24 | 64.8 | 1 | 0.417 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.0602 | 0.641 | 10.6 | 1 | 0.417 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.0167 | 0.0603 | 3.62 | 1 | 0.417 |
| binary_early | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.102 | 0.657 | 6.42 | 1 | 0.417 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 177 | 158 | 0.89 | 0.509 | 0.254 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 18.2 | 16.4 | 0.901 | 0.509 | 0.254 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.136 | 0.178 | 1.31 | 0.509 | 0.254 |
| binary_early | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 17.2 | 15.5 | 0.903 | 0.509 | 0.254 |

## Robustness: |Δ metric| / |Normal - Mild gap| (selected)
| metric | shift-2 | shift+10 | shift-20 | band_shrink10 | band_lo10 | band_3.4-3.9 | band_3.2-3.5_nodip | flatten_notch | detune+200 | one_open |
|---|---|---|---|---|---|---|---|---|---|---|
| M0.old_score | 0.0066 | 0.032 | 0.061 | 2.2 | 1.9 | 18 | 14 | 1.1 | 0.95 | 4.1 |
| M1.Sii_dBavg | 0.018 | 0.0086 | 0.017 | 1.8 | 1.7 | 22 | 9.8 | 4.4 | 0.27 | 2.9 |
| M2.R | 0.02 | 0.1 | 0.19 | 9.2 | 8.1 | 89 | 53 | 10 | 3 | 17 |
| M3.ML_of_powavg | 0.019 | 0.099 | 0.19 | 8.7 | 7.7 | 64 | 42 | 11 | 3 | 1.7e+02 |
| M4.N | 0.02 | 0.1 | 0.19 | 9.1 | 8.1 | 88 | 52 | 10 | 3 | 17 |
| M5.C | 0.00021 | 0.00073 | 0.0014 | 5.2 | 5.2 | 78 | 15 | 2.1e-13 | 0.032 | 15 |
| M5.C3 | 0.00011 | 0.0006 | 0.0011 | 0.41 | 0.4 | 3.9 | 5.3 | 0 | 0.028 | 1.3 |
| M5.C3[k3] | 0.0054 | 0.026 | 0.076 | 0.073 | 0.08 | n/a | n/a | 0 | 2 | 1.1 |
| M6.fc_A | 0.73 | 3.7 | 7.3 | 1.6 | 6.8 | 28 | 81 | 0.38 | 71 | 3.9e+03 |
| M6.spread_A | 0.023 | 0.11 | 0.24 | 3.3 | 3.9 | 31 | 45 | 1.3 | 0.84 | 42 |
| M7.D | 0.12 | 0.98 | 1.5 | 0.11 | 0.11 | 1.8 | 0.79 | 1.6 | 48 | 1.5e+02 |
| M7.D_pow | 0.21 | 1.7 | 2.5 | 0.13 | 0.13 | 1.9 | 0.86 | 5.4 | 1.3e+02 | 62 |
| M7.D3[k3] | 0.23 | 1.4 | 1.9 | 0.042 | 0.25 | n/a | n/a | 0 | 11 | 2.2 |
| M8.s1^2 | 0.035 | 0.18 | 0.34 | 16 | 14 | 1.5e+02 | 92 | 19 | 5.4 | 1.7e+02 |
| M8.lam0^2 | 0.02 | 0.1 | 0.2 | 9.3 | 8.2 | 90 | 51 | 11 | 3.1 | 17 |
| M8.lam0^2[k3] | 0.25 | 1.3 | 2.3 | 1.1 | 3.5 | n/a | n/a | 5.9 | 51 | 17 |
| M8.lam3^2[k3] | 0.17 | 0.9 | 1.6 | 1 | 2.4 | n/a | n/a | 5.2 | 45 | 16 |

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
| M6.spread_A | True | True | False | True | False |
| M7.D | True | True | False | False | False |
| M7.D_pow | True | True | False | False | False |
| M7.D3[k3] | True | True | True | False | False |
| M8.s1^2 | True | True | False | False | False |
| M8.lam0^2 | True | True | False | False | False |
| M8.lam0^2[k3] | True | True | False | False | False |
| M8.lam3^2[k3] | True | True | False | False | False |

## Ordinality: stage-to-stage steps in port-noise units (noise-free, all 4 stages)
4 of 99 metrics are monotone over Normal < Mild < Moderate < Severe. Normal->Mild and Moderate->Severe cross HFSS projects; Mild->Moderate does not (see summary caveat).
| metric | monotone | Normal->MCI / port | MCI->Mild / port | Mild->Moderate / port | Moderate->Severe / port |
|---|---|---|---|---|---|
| M0.old_score | False | 3.4 | 34 | -6.2 | 12 |
| M2.R | False | 1.5 | -7.8 | -7.3 | -5.4 |
| M5.C | False | 2.6 | -4 | -0.68 | -7 |
| M5.C3 | False | 1.7 | -10 | -0.76 | -1 |
| M5.C3[k3] | False | 1.5 | -13 | -0.8 | -0.45 |
| M6.A[3.40] | False | 2.2 | -5.5 | -0.94 | -5.6 |
| M6.A[3.45] | False | 11 | -14 | 0.52 | -3.3 |
| M7.D3 | False | 17 | 6.4 | -6.6 | 16 |
| M7.D3[k3] | False | 12 | 14 | -5.2 | 24 |
| M8.lam0^2[k3] | False | -1.3 | 4.5 | -1.7 | 3.1 |
| M8.lam3^2[k3] | False | -1.9 | 5.5 | -2.1 | 2.6 |

## M0 decomposition (couplings zeroed)
M0 = mean_B Σ_(j≠i)|S_ii + S_ij| / VSWR_i. With every S_ij set to 0 the score is almost unchanged, i.e. M0 is in practice (N-1)·<|Γ|/VSWR>: a reflection-only quantity with an arbitrary weighting.
| stage | M0 | M0_couplings_zeroed |
|---|---|---|
| Normal | 0.42664 | 0.42762 |
| MCI | 0.42822 | 0.42855 |
| Mild | 0.44429 | 0.44462 |
| Moderate | 0.44139 | 0.44213 |
| Severe | 0.44698 | 0.44776 |
