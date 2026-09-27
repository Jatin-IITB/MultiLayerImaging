# Prompt 02 - metric separability (track A, code 4962836, sim_set hfss-v1-masked)

J_meas = min pairwise Fisher ratio from noisy realisations (ranking key). J_eff adds the port-to-port asymmetry as extra variance. gap/port = class gap / port-to-port std. gap/mesh = pending (mesh-repeat not yet available). shift_move = largest change under ±2/5/10 MHz resonance shifts / smallest class gap. band_gap_retention = worst (gap after ±10 % band change) / (original gap); < 0 means the class order flips. freq_robust (brief's literal criterion) = shift AND band value changes < 0.25 × smallest gap. AD-vs-AD pairs unverified against mesh noise.

Glitch masking ON: 26 in-band (f, pair) points masked in 7 runs (results/qc/masked_points.csv).

## Ranking - scheme `binary` (binary:Normal|AD(Mild+Moderate+Severe)), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C3[k3] | 775 | Normal|AD | 17.9 | 6.05 | 2.03e-96 | 0.0337 | 0.944 | True |
| 2 | M5.C3 | 548 | Normal|AD | 13 | 5.15 | 9.3e-75 | 0.00901 | 1.11 | False |
| 3 | M5.C3_dBavg[k3] | 472 | Normal|AD | 12.1 | 4.98 | 2.92e-71 | 0.0593 | 0.912 | True |
| 4 | M6.N[3.55] | 55.3 | Normal|AD | 1.31 | 1.64 | 5.18e-09 | 1.68 | 0.96 | False |
| 5 | M6.A[3.55] | 53.9 | Normal|AD | 1.33 | 1.65 | 6.99e-09 | 1.67 | 0.96 | False |
| 6 | M0.old_score | 45.3 | Normal|AD | 16.9 | 7.33 | 7.1e-07 | 0.215 | 0.76 | False |
| 7 | M6.N[3.50] | 39.8 | Normal|AD | 3.53 | 2.78 | 9.27e-07 | 0.424 | 0.965 | False |
| 8 | M6.A[3.50] | 39.3 | Normal|AD | 3.54 | 2.79 | 1.04e-06 | 0.426 | 0.965 | False |
| 9 | M6.N[3.45] | 31.6 | Normal|AD | 7.06 | 4.26 | 6.56e-07 | 0.297 | 0.948 | False |
| 10 | M6.A[3.45] | 31.3 | Normal|AD | 7.06 | 4.27 | 7.11e-07 | 0.295 | 0.948 | False |
| 11 | M6.A[3.25] | 31.2 | Normal|AD | 12.5 | 6.45 | 3.93e-05 | 1.05 | 0.975 | False |
| 12 | M6.N[3.25] | 31.2 | Normal|AD | 12.5 | 6.45 | 3.96e-05 | 1.05 | 0.975 | False |
| 13 | M8.lam3^2[k3] | 20.3 | Normal|AD | 8.43 | 5.37 | 1.04e-05 | 0.363 | 0.907 | False |
| 14 | M7.D1 | 19.4 | Normal|AD | 1.87 | 2.03 | 4.54e-06 | 4.95 | 1.09 | False |
| 15 | M8.lam2^2[k3] | 18.5 | Normal|AD | 7.68 | 5.12 | 2.38e-05 | 0.435 | 0.897 | False |
| 35 | M2.R | 12.4 | Normal|AD | 4.17 | 3.54 | 0.00614 | 0.441 | 0.357 | False |
| 77 | M1.Sii_dBavg | 0.273 | Normal|AD | 0.0166 | 0.188 | 0.347 | 3.53 | 1.54 | False |

Top 10 by J_eff (port asymmetry included), scheme `binary`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M5.C3[k3] | 775 | Normal|AD | 17.9 | 6.05 | 2.03e-96 | 0.0337 | 0.944 | True |
| 6 | M0.old_score | 45.3 | Normal|AD | 16.9 | 7.33 | 7.1e-07 | 0.215 | 0.76 | False |
| 2 | M5.C3 | 548 | Normal|AD | 13 | 5.15 | 9.3e-75 | 0.00901 | 1.11 | False |
| 11 | M6.A[3.25] | 31.2 | Normal|AD | 12.5 | 6.45 | 3.93e-05 | 1.05 | 0.975 | False |
| 12 | M6.N[3.25] | 31.2 | Normal|AD | 12.5 | 6.45 | 3.96e-05 | 1.05 | 0.975 | False |
| 3 | M5.C3_dBavg[k3] | 472 | Normal|AD | 12.1 | 4.98 | 2.92e-71 | 0.0593 | 0.912 | True |
| 23 | M6.A[3.20] | 15.5 | Normal|AD | 11.5 | 9.5 | 0.00253 | 0.744 | 0.996 | False |
| 24 | M6.N[3.20] | 15.5 | Normal|AD | 11.5 | 9.5 | 0.00253 | 0.744 | 0.996 | False |
| 30 | M6.spread_A | 12.8 | Normal|AD | 10.5 | 10.9 | 0.00561 | 0.0579 | 0.617 | False |
| 31 | M6.spread_N | 12.8 | Normal|AD | 10.5 | 10.9 | 0.00563 | 0.0579 | 0.617 | False |

## Ranking - scheme `three_merged` (three_merged:Normal|Mild+Moderate(Mild+Moderate)|Severe), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M7.D3 | 175 | Mild+Moderate|Severe | 2.89 | 2.42 | 3.04e-23 | 2.36 | 1.1 | False |
| 2 | M7.D3[k3] | 165 | Mild+Moderate|Severe | 4.22 | 2.94 | 6.69e-22 | 2.33 | 0.882 | False |
| 3 | M7.D2 | 154 | Mild+Moderate|Severe | 2.13 | 2.08 | 3.09e-20 | 1.36 | 1.05 | False |
| 4 | M8.lam0^2[k3] | 146 | Mild+Moderate|Severe | 2.31 | 2.16 | 2.71e-18 | 1.06 | 0.854 | False |
| 5 | M8.lam1^2[k3] | 133 | Mild+Moderate|Severe | 2.22 | 2.12 | 4.54e-17 | 0.979 | 0.859 | False |
| 6 | M2.R[k3] | 126 | Mild+Moderate|Severe | 2.08 | 2.06 | 2.95e-16 | 0.934 | 0.855 | False |
| 7 | M4.N[k3] | 125 | Mild+Moderate|Severe | 2.07 | 2.05 | 3.51e-16 | 0.935 | 0.853 | False |
| 8 | M8.lam3^2[k3] | 120 | Mild+Moderate|Severe | 1.89 | 1.96 | 1.12e-15 | 0.785 | 0.852 | False |
| 9 | M8.lam2^2[k3] | 109 | Mild+Moderate|Severe | 1.88 | 1.95 | 1.56e-14 | 0.898 | 0.847 | False |
| 10 | M6.A[3.40] | 95.1 | Mild+Moderate|Severe | 4.04 | 2.91 | 1.37e-12 | 0.36 | 0.961 | False |
| 11 | M6.N[3.40] | 95.1 | Mild+Moderate|Severe | 4.02 | 2.9 | 1.39e-12 | 0.359 | 0.961 | False |
| 12 | M6.N[3.65] | 43.2 | Normal|Mild+Moderate | 0.314 | 0.796 | 1.53e-06 | 3.35 | 0.908 | False |
| 13 | M6.A[3.65] | 41.7 | Normal|Mild+Moderate | 0.312 | 0.793 | 2.18e-06 | 3.37 | 0.907 | False |
| 14 | M5.C[k3] | 27.1 | Normal|Mild+Moderate | 0.317 | 0.8 | 1.98e-05 | 1.88 | 0.655 | False |
| 15 | M6.A[3.45] | 26.4 | Mild+Moderate|Severe | 0.807 | 1.29 | 0.00012 | 0.843 | 0.915 | False |
| 43 | M0.old_score | 1.18 | Mild+Moderate|Severe | 0.42 | 1.14 | 0.22 | 1.42 | 0.645 | False |
| 44 | M5.C3[k3] | 1.03 | Mild+Moderate|Severe | 0.0187 | 0.195 | 0.171 | 0.989 | 0.427 | False |
| 54 | M2.R | 0.444 | Mild+Moderate|Severe | 0.0802 | 0.443 | 0.317 | 2.29 | 0.343 | False |
| 73 | M1.Sii_dBavg | 0.0918 | Normal|Severe | 0.00234 | 0.0694 | 0.415 | 7.39 | 0.138 | False |

Top 10 by J_eff (port asymmetry included), scheme `three_merged`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 2 | M7.D3[k3] | 165 | Mild+Moderate|Severe | 4.22 | 2.94 | 6.69e-22 | 2.33 | 0.882 | False |
| 10 | M6.A[3.40] | 95.1 | Mild+Moderate|Severe | 4.04 | 2.91 | 1.37e-12 | 0.36 | 0.961 | False |
| 11 | M6.N[3.40] | 95.1 | Mild+Moderate|Severe | 4.02 | 2.9 | 1.39e-12 | 0.359 | 0.961 | False |
| 24 | M7.D_pow | 8.22 | Mild+Moderate|Severe | 3.03 | 3.1 | 0.0212 | 3.47 | 0.79 | False |
| 1 | M7.D3 | 175 | Mild+Moderate|Severe | 2.89 | 2.42 | 3.04e-23 | 2.36 | 1.1 | False |
| 4 | M8.lam0^2[k3] | 146 | Mild+Moderate|Severe | 2.31 | 2.16 | 2.71e-18 | 1.06 | 0.854 | False |
| 5 | M8.lam1^2[k3] | 133 | Mild+Moderate|Severe | 2.22 | 2.12 | 4.54e-17 | 0.979 | 0.859 | False |
| 3 | M7.D2 | 154 | Mild+Moderate|Severe | 2.13 | 2.08 | 3.09e-20 | 1.36 | 1.05 | False |
| 6 | M2.R[k3] | 126 | Mild+Moderate|Severe | 2.08 | 2.06 | 2.95e-16 | 0.934 | 0.855 | False |
| 7 | M4.N[k3] | 125 | Mild+Moderate|Severe | 2.07 | 2.05 | 3.51e-16 | 0.935 | 0.853 | False |

## Ranking - scheme `three` (three:Normal|Mild|Severe), profile `typical`
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 1 | M7.D3 | 638 | Mild|Severe | 3.27 | 2.56 | 3.88e-73 | 2.29 | 1.1 | False |
| 2 | M7.D3[k3] | 588 | Mild|Severe | 5 | 3.18 | 1.15e-67 | 2.3 | 0.874 | False |
| 3 | M7.D2 | 460 | Mild|Severe | 3.19 | 2.53 | 6.17e-53 | 1.41 | 1.05 | False |
| 4 | M5.C | 410 | Normal|Mild | 2.69 | 2.33 | 7.05e-47 | 0.0116 | 1.11 | False |
| 5 | M5.C2 | 404 | Normal|Mild | 2.32 | 2.16 | 2.48e-46 | 0.0323 | 0.979 | False |
| 6 | M5.C1 | 347 | Normal|Mild | 2.2 | 2.11 | 5.07e-40 | 0.0102 | 1.11 | False |
| 7 | M8.lam0^2[k3] | 204 | Mild|Severe | 2.57 | 2.28 | 2.84e-24 | 1.12 | 0.856 | False |
| 8 | M8.lam1^2[k3] | 203 | Mild|Severe | 2.39 | 2.2 | 3.59e-24 | 1.04 | 0.861 | False |
| 9 | M2.R[k3] | 196 | Mild|Severe | 2.21 | 2.11 | 1.87e-23 | 0.993 | 0.86 | False |
| 10 | M4.N[k3] | 194 | Mild|Severe | 2.2 | 2.11 | 3.18e-23 | 0.994 | 0.858 | False |
| 11 | M8.lam3^2[k3] | 188 | Mild|Severe | 2.01 | 2.02 | 1.4e-22 | 0.836 | 0.864 | False |
| 12 | M5.C[k3] | 185 | Normal|Mild | 0.424 | 0.922 | 2.91e-22 | 1.61 | 0.671 | False |
| 13 | M5.C2[k3] | 183 | Normal|Mild | 3.63 | 2.72 | 3.96e-22 | 0.0961 | 0.748 | False |
| 14 | M8.lam2^2[k3] | 180 | Mild|Severe | 1.92 | 1.97 | 9.93e-22 | 0.962 | 0.854 | False |
| 15 | M6.A[3.40] | 133 | Mild|Severe | 4.13 | 2.92 | 1.65e-16 | 0.384 | 0.959 | False |
| 46 | M0.old_score | 2.63 | Mild|Severe | 0.725 | 1.42 | 0.126 | 1.06 | 0.742 | False |
| 51 | M2.R | 1.18 | Mild|Severe | 0.19 | 0.673 | 0.221 | 1.56 | 0.289 | False |
| 73 | M1.Sii_dBavg | 0.0918 | Normal|Severe | 0.00234 | 0.0694 | 0.415 | 7.39 | 0.672 | False |
| 77 | M5.C3[k3] | 0.0791 | Mild|Severe | 0.000329 | 0.0257 | 0.421 | 9.38 | -6.41 | False |

Top 10 by J_eff (port asymmetry included), scheme `three`:
| rank | metric | min_J_meas | weakest_pair | min_J_eff | min_gap_over_port | max_bayes_err | shift_move_over_min_gap | band_gap_retention | freq_robust |
|---|---|---|---|---|---|---|---|---|---|
| 2 | M7.D3[k3] | 588 | Mild|Severe | 5 | 3.18 | 1.15e-67 | 2.3 | 0.874 | False |
| 15 | M6.A[3.40] | 133 | Mild|Severe | 4.13 | 2.92 | 1.65e-16 | 0.384 | 0.959 | False |
| 16 | M6.N[3.40] | 133 | Mild|Severe | 4.11 | 2.91 | 1.85e-16 | 0.383 | 0.959 | False |
| 13 | M5.C2[k3] | 183 | Normal|Mild | 3.63 | 2.72 | 3.96e-22 | 0.0961 | 0.748 | False |
| 1 | M7.D3 | 638 | Mild|Severe | 3.27 | 2.56 | 3.88e-73 | 2.29 | 1.1 | False |
| 3 | M7.D2 | 460 | Mild|Severe | 3.19 | 2.53 | 6.17e-53 | 1.41 | 1.05 | False |
| 4 | M5.C | 410 | Normal|Mild | 2.69 | 2.33 | 7.05e-47 | 0.0116 | 1.11 | False |
| 7 | M8.lam0^2[k3] | 204 | Mild|Severe | 2.57 | 2.28 | 2.84e-24 | 1.12 | 0.856 | False |
| 32 | M7.D_pow | 7.45 | Mild|Severe | 2.49 | 2.73 | 0.0265 | 3.72 | 0.815 | False |
| 8 | M8.lam1^2[k3] | 203 | Mild|Severe | 2.39 | 2.2 | 3.59e-24 | 1.04 | 0.861 | False |

## Power averaging vs dB averaging (min pairwise J_meas)
| scheme | pair | profile | J_dB | J_pow | ratio_pow/dB | shift_move_dB | shift_move_pow |
|---|---|---|---|---|---|---|---|
| binary | M1.Sii_dBavg vs M2.R | good | 0.768 | 38.1 | 49.6 | 3.53 | 0.441 |
| binary | M1.Sii_dBavg vs M2.R | typical | 0.273 | 12.4 | 45.6 | 3.53 | 0.441 |
| binary | M1.Sii_dBavg vs M2.R | very_noisy | 0.0254 | 0.775 | 30.6 | 3.53 | 0.441 |
| binary | M1.Sii_dBavg vs M2.R | typical_jitter | 0.0389 | 8.62 | 222 | 3.53 | 0.441 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | good | 30.7 | 38.4 | 1.25 | 0.416 | 0.44 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.749 | 12.5 | 16.7 | 0.416 | 0.44 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.447 | 0.774 | 1.73 | 0.416 | 0.44 |
| binary | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.787 | 8.64 | 11 | 0.416 | 0.44 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 566 | 1.1e+03 | 1.94 | 0.0593 | 0.0337 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 472 | 775 | 1.64 | 0.0593 | 0.0337 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 20.2 | 22.2 | 1.1 | 0.0593 | 0.0337 |
| binary | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 441 | 736 | 1.67 | 0.0593 | 0.0337 |
| three_merged | M1.Sii_dBavg vs M2.R | good | 0.396 | 1.92 | 4.86 | 7.39 | 2.29 |
| three_merged | M1.Sii_dBavg vs M2.R | typical | 0.0918 | 0.444 | 4.84 | 7.39 | 2.29 |
| three_merged | M1.Sii_dBavg vs M2.R | very_noisy | 0.00236 | 0.0595 | 25.2 | 7.39 | 2.29 |
| three_merged | M1.Sii_dBavg vs M2.R | typical_jitter | 0.00931 | 0.346 | 37.2 | 7.39 | 2.29 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | good | 5.07 | 1.9 | 0.375 | 1.51 | 2.31 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.038 | 0.439 | 11.6 | 1.51 | 2.31 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.0724 | 0.0588 | 0.812 | 1.51 | 2.31 |
| three_merged | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.0562 | 0.343 | 6.1 | 1.51 | 2.31 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 0.113 | 1.22 | 10.8 | 3.55 | 0.989 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 0.0746 | 1.03 | 13.8 | 3.55 | 0.989 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.0106 | 0.0406 | 3.82 | 3.55 | 0.989 |
| three_merged | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 0.0745 | 0.917 | 12.3 | 3.55 | 0.989 |
| three | M1.Sii_dBavg vs M2.R | good | 0.535 | 7.09 | 13.3 | 7.39 | 1.56 |
| three | M1.Sii_dBavg vs M2.R | typical | 0.0918 | 1.18 | 12.8 | 7.39 | 1.56 |
| three | M1.Sii_dBavg vs M2.R | very_noisy | 0.00236 | 0.148 | 62.8 | 7.39 | 1.56 |
| three | M1.Sii_dBavg vs M2.R | typical_jitter | 0.00931 | 0.734 | 78.8 | 7.39 | 1.56 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | good | 6.7 | 7.04 | 1.05 | 1.36 | 1.56 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | typical | 0.0388 | 1.17 | 30.2 | 1.36 | 1.56 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | very_noisy | 0.0905 | 0.147 | 1.63 | 1.36 | 1.56 |
| three | M3.ML_dBavg vs M3.ML_of_powavg | typical_jitter | 0.0499 | 0.729 | 14.6 | 1.36 | 1.56 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | good | 92.4 | 0.484 | 0.00524 | 0.886 | 9.38 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | typical | 8.8 | 0.0791 | 0.00899 | 0.886 | 9.38 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | very_noisy | 0.00456 | 0.000723 | 0.158 | 0.886 | 9.38 |
| three | M5.C3_dBavg[k3] vs M5.C3[k3] | typical_jitter | 5.7 | 0.0478 | 0.00838 | 0.886 | 9.38 |

## Robustness: |Δ metric| / |Normal - Mild gap| (selected)
| metric | shift-2 | shift+10 | shift-20 | band_shrink10 | band_lo10 | band_3.4-3.9 | band_3.2-3.5_nodip | flatten_notch | detune+200 | one_open |
|---|---|---|---|---|---|---|---|---|---|---|
| M0.old_score | 0.046 | 0.23 | 0.5 | 3 | 4.4 | 17 | 15 | 1 | 3.8 | 8.6 |
| M1.Sii_dBavg | 0.73 | 0.72 | 1.6 | 34 | 38 | 2.4e+02 | 16 | 94 | 12 | 63 |
| M2.R | 0.1 | 0.49 | 1.1 | 9.8 | 13 | 62 | 26 | 14 | 8.3 | 24 |
| M3.ML_of_powavg | 0.1 | 0.49 | 1.1 | 9.5 | 12 | 51 | 24 | 15 | 8 | n/a |
| M4.N | 0.1 | 0.49 | 1.1 | 9.8 | 13 | 61 | 26 | 14 | 8.2 | 24 |
| M5.C | 0.0022 | 0.011 | 0.025 | 2 | 2 | 16 | 6.3 | 5.3e-14 | 0.21 | 6.3 |
| M5.C3 | 0.0017 | 0.0085 | 0.019 | 0.25 | 0.3 | 1.1 | 2.5 | 0 | 0.16 | 0.84 |
| M5.C3[k3] | 0.0063 | 0.028 | 0.076 | 0.053 | 0.06 | n/a | n/a | 0 | 1.4 | 0.7 |
| M6.fc_A | 0.89 | 4.4 | 8.8 | 4.2 | 7 | 18 | 1.4e+02 | 2.2 | 84 | 2e+02 |
| M6.spread_A | 0.0099 | 0.063 | 0.097 | 4.7 | 4.2 | 27 | 45 | 1.3 | 5.4 | 12 |
| M7.D | 0.06 | 1.9 | 5.8 | 0.11 | 0.15 | 0.42 | 1.6 | 6 | 1.6e+02 | 3.4e+02 |
| M7.D_pow | 0.11 | 2.9 | 8.1 | 0.038 | 0.2 | 0.45 | 1.7 | 18 | 3.9e+02 | 2.1e+02 |
| M7.D3[k3] | 0.31 | 2.3 | 4.1 | 0.094 | 0.21 | n/a | n/a | 0 | 17 | 4.2 |
| M8.s1^2 | 0.3 | 1.5 | 3.3 | 29 | 37 | 1.8e+02 | 79 | 44 | 25 | 4.2e+02 |
| M8.lam0^2 | 0.095 | 0.47 | 1 | 9.3 | 12 | 59 | 22 | 13 | 7.8 | 23 |
| M8.lam0^2[k3] | 0.13 | 0.69 | 1.3 | 0.15 | 1.8 | n/a | n/a | 2.5 | 23 | 8.7 |
| M8.lam3^2[k3] | 0.08 | 0.42 | 0.79 | 0.056 | 1.1 | n/a | n/a | 2.1 | 18 | 7 |

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
| M6.spread_A | True | True | False | False | False |
| M7.D | True | True | False | False | False |
| M7.D_pow | True | True | False | False | False |
| M7.D3[k3] | True | True | False | False | False |
| M8.s1^2 | True | True | False | False | False |
| M8.lam0^2 | True | True | False | False | False |
| M8.lam0^2[k3] | True | True | False | False | False |
| M8.lam3^2[k3] | True | True | False | False | False |

## Ordinality: stage-to-stage steps in port-noise units (noise-free, all 4 stages)
31 of 83 metrics are monotone over Normal < Mild < Moderate < Severe. Normal->Mild and Moderate->Severe cross HFSS projects; Mild->Moderate does not (see summary caveat).
| metric | monotone | Normal->Mild / port | Mild->Moderate / port | Moderate->Severe / port |
|---|---|---|---|---|
| M0.old_score | True | 7 | 0.81 | 0.77 |
| M2.R | True | -2.6 | -0.57 | -0.32 |
| M5.C | False | -1.9 | 1.3 | -3.4 |
| M5.C3 | False | -5.2 | -0.32 | 0.47 |
| M5.C3[k3] | False | -6.1 | -0.38 | 0.4 |
| M6.A[3.40] | False | -5 | 0.38 | -3.2 |
| M6.A[3.45] | False | -3.7 | 0.31 | -1.6 |
| M7.D3 | True | 3.3 | 0.4 | 3 |
| M7.D3[k3] | True | 4 | 0.51 | 3.7 |
| M8.lam0^2[k3] | False | 3.6 | -0.23 | 2.5 |
| M8.lam3^2[k3] | False | 4.1 | -0.26 | 2.3 |

## M0 decomposition (couplings zeroed)
M0 = mean_B Σ_(j≠i)|S_ii + S_ij| / VSWR_i. With every S_ij set to 0 the score is almost unchanged, i.e. M0 is in practice (N-1)·<|Γ|/VSWR>: a reflection-only quantity with an arbitrary weighting.
| stage | M0 | M0_couplings_zeroed |
|---|---|---|
| Normal | 0.54891 | 0.55155 |
| Mild | 0.5596 | 0.5618 |
| Moderate | 0.56083 | 0.56292 |
| Severe | 0.56201 | 0.56423 |
