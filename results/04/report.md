# Prompt 04 - likelihood / divergence analysis (code 5c060e3)

Solves: {'../archive/v1_mixed_projects/raw/brain_sevem_layer_Healthy.s6p': 'Normal', 'new_Healthy.s6p': 'Normal', 'new_MCI.s6p': 'MCI', '../archive/v1_mixed_projects/raw/Brain_sevem_layer_MildAD.s6p': 'Mild', 'new_MildAD.s6p': 'Mild', '../archive/v1_mixed_projects/raw/Brain_sevem_layer_ModerateAD.s6p': 'Moderate', 'new_ModerateAD.s6p': 'Moderate', '../archive/v1_mixed_projects/raw/brain_sevem_layer_SevereAD.s6p': 'Severe', 'new_SevereAD.s6p': 'Severe'}. Band 3.20-4.20 GHz. Noise: typical + setup perturbation + per-port gain ±0.5 dB; 150 draws per solve per split (train/test seeds differ). One head geometry throughout. Every 3-class number is **preliminary: one head, two solves, 4 repeat pairs**. MCI has one solve: no classification claim.

Feature groups: G_refl (23), G_coup (63), G_ratio (3), G_all (89), R31 (1), C3 (1), C2 (1). Units: each feature divided by its pooled within-solve (measurement-noise) SD.

## Shrinkage
Measurement covariance: Ledoit-Wolf toward scaled identity (lw_meas_*). Between-solve covariance from the repeat pairs (d/sqrt2): variances toward their median (lambda_var), correlations toward 0 (lambda_corr); 1 = fully shrunk.
| group | dim | n_pairs | lambda_var | lambda_corr | lw_meas_Normal | lw_meas_MCI | lw_meas_Mild | lw_meas_Moderate | lw_meas_Severe | fit | lambda_var_min | lambda_var_max | lambda_corr_min | lambda_corr_max | n_pairs_min | n_pairs_max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G_refl | 23.000 | 4.000 | 0.085 | 0.134 | 0.006 | 0.018 | 0.006 | 0.006 | 0.006 | all data | n/a | n/a | n/a | n/a | n/a | n/a |
| G_coup | 63.000 | 4.000 | 0.060 | 0.404 | 0.008 | 0.026 | 0.009 | 0.010 | 0.010 | all data | n/a | n/a | n/a | n/a | n/a | n/a |
| G_ratio | 3.000 | 4.000 | 1.000 | 0.812 | 0.021 | 0.050 | 0.028 | 0.024 | 0.025 | all data | n/a | n/a | n/a | n/a | n/a | n/a |
| G_all | 89.000 | 4.000 | 0.073 | 0.339 | 0.008 | 0.024 | 0.008 | 0.009 | 0.009 | all data | n/a | n/a | n/a | n/a | n/a | n/a |
| R31 | 1.000 | 4.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | all data | n/a | n/a | n/a | n/a | n/a | n/a |
| C3 | 1.000 | 4.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | all data | n/a | n/a | n/a | n/a | n/a | n/a |
| C2 | 1.000 | 4.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | all data | n/a | n/a | n/a | n/a | n/a | n/a |
| G_all | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | LOSO folds (min/max) | 0.050 | 0.366 | 0.338 | 0.669 | 2.000 | 3.000 |
| G_coup | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | LOSO folds (min/max) | 0.036 | 0.303 | 0.341 | 0.755 | 2.000 | 3.000 |
| G_ratio | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | LOSO folds (min/max) | 1.000 | 1.000 | 0.720 | 1.000 | 2.000 | 3.000 |
| G_refl | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | LOSO folds (min/max) | 0.055 | 0.461 | 0.166 | 0.381 | 2.000 | 3.000 |

## Divergences: symmetric KL (J) and Bhattacharyya (B), without and with the between-solve term
meas_only = measurement noise only (the apparent information); with_between = plus solve-to-solve covariance. B_kept_% = share of the apparent Bhattacharyya distance that survives. 'repeat:X' = the two solves of the same stage X, i.e. pure solve-to-solve difference (a class pair should beat it). Bhattacharyya B -> Bayes error bound 0.5·exp(-B).
| group | pair | J_meas_only | J_with_between | B_meas_only | B_with_between | B_kept_% |
|---|---|---|---|---|---|---|
| C2 | Normal|AD | 13.1 | 7.92 | 1.14 | 0.822 | 72.3 |
| C2 | Normal|Mild | 12.5 | 7.03 | 1.56 | 0.879 | 56.3 |
| C2 | Normal|Moderate | 8.93 | 4.85 | 1.11 | 0.606 | 54.5 |
| C2 | Normal|Severe | 46.6 | 25.3 | 5.8 | 3.16 | 54.5 |
| C2 | Mild|Moderate | 0.474 | 0.257 | 0.059 | 0.032 | 54.3 |
| C2 | Mild|Severe | 9.79 | 5.35 | 1.22 | 0.668 | 54.9 |
| C2 | Moderate|Severe | 15.6 | 8.26 | 1.95 | 1.03 | 53 |
| C2 | MCI|Normal | 0.671 | 0.327 | 0.0816 | 0.0406 | 49.7 |
| C2 | repeat:Normal | 0.0556 | 0.0235 | 0.00691 | 0.00293 | 42.4 |
| C2 | repeat:Mild | 1.02 | 0.551 | 0.127 | 0.0688 | 54.1 |
| C2 | repeat:Moderate | 4.23 | 2.86 | 0.528 | 0.357 | 67.5 |
| C2 | repeat:Severe | 1.69 | 0.874 | 0.209 | 0.109 | 52.1 |
| C3 | Normal|AD | 45.7 | 18.6 | 5.71 | 2.32 | 40.7 |
| C3 | Normal|Mild | 40.6 | 16.6 | 5.07 | 2.07 | 40.9 |
| C3 | Normal|Moderate | 51.7 | 20.1 | 6.44 | 2.51 | 39.1 |
| C3 | Normal|Severe | 50.2 | 19.9 | 6.26 | 2.49 | 39.7 |
| C3 | Mild|Moderate | 0.322 | 0.124 | 0.04 | 0.0154 | 38.6 |
| C3 | Mild|Severe | 0.3 | 0.119 | 0.0374 | 0.0148 | 39.7 |
| C3 | Moderate|Severe | 0.0015 | 0.000228 | 0.000188 | 2.85e-05 | 15.2 |
| C3 | MCI|Normal | 1.46 | 0.518 | 0.178 | 0.0646 | 36.2 |
| C3 | repeat:Normal | 0.671 | 0.233 | 0.0836 | 0.0291 | 34.8 |
| C3 | repeat:Mild | 5.01 | 2.43 | 0.625 | 0.303 | 48.5 |
| C3 | repeat:Moderate | 6.17 | 2.81 | 0.769 | 0.351 | 45.7 |
| C3 | repeat:Severe | 0.521 | 0.171 | 0.0649 | 0.0213 | 32.9 |
| G_all | Normal|AD | 1.36e+04 | 1.39e+03 | 1.28e+03 | 119 | 9.23 |
| G_all | Normal|Mild | 1.29e+04 | 1.48e+03 | 1.36e+03 | 183 | 13.5 |
| G_all | Normal|Moderate | 1.42e+04 | 1.43e+03 | 1.49e+03 | 177 | 11.9 |
| G_all | Normal|Severe | 2.23e+04 | 2.7e+03 | 2.28e+03 | 334 | 14.7 |
| G_all | Mild|Moderate | 955 | 34.5 | 104 | 4.27 | 4.11 |
| G_all | Mild|Severe | 4.69e+03 | 331 | 502 | 41 | 8.18 |
| G_all | Moderate|Severe | 4.52e+03 | 422 | 477 | 52.3 | 11 |
| G_all | MCI|Normal | 1.72e+04 | 127 | 1.65e+03 | 15.6 | 0.947 |
| G_all | repeat:Normal | 1.47e+04 | 194 | 1.2e+03 | 22.7 | 1.88 |
| G_all | repeat:Mild | 3.46e+04 | 259 | 3.18e+03 | 31.3 | 0.987 |
| G_all | repeat:Moderate | 1.85e+04 | 83.5 | 1.78e+03 | 10.3 | 0.578 |
| G_all | repeat:Severe | 2.05e+04 | 90.2 | 1.97e+03 | 11.1 | 0.562 |
| G_coup | Normal|AD | 8.12e+03 | 492 | 790 | 45.8 | 5.8 |
| G_coup | Normal|Mild | 8.02e+03 | 501 | 883 | 62.4 | 7.07 |
| G_coup | Normal|Moderate | 9.03e+03 | 476 | 967 | 59.4 | 6.14 |
| G_coup | Normal|Severe | 1.43e+04 | 916 | 1.42e+03 | 114 | 8.02 |
| G_coup | Mild|Moderate | 349 | 21.7 | 39.7 | 2.69 | 6.78 |
| G_coup | Mild|Severe | 2.43e+03 | 143 | 279 | 17.8 | 6.38 |
| G_coup | Moderate|Severe | 2.85e+03 | 177 | 317 | 22 | 6.94 |
| G_coup | MCI|Normal | 4.37e+03 | 92.3 | 419 | 11.4 | 2.71 |
| G_coup | repeat:Normal | 2.79e+03 | 141 | 229 | 16.8 | 7.33 |
| G_coup | repeat:Mild | 8.17e+03 | 187 | 703 | 22.6 | 3.22 |
| G_coup | repeat:Moderate | 4.67e+03 | 27.9 | 369 | 3.45 | 0.934 |
| G_coup | repeat:Severe | 5.09e+03 | 50.1 | 438 | 6.16 | 1.41 |
| G_ratio | Normal|AD | 2.91e+03 | 399 | 183 | 42.2 | 23.1 |
| G_ratio | Normal|Mild | 3.94e+03 | 414 | 484 | 51.8 | 10.7 |
| G_ratio | Normal|Moderate | 4.41e+03 | 443 | 543 | 55.3 | 10.2 |
| G_ratio | Normal|Severe | 6.1e+03 | 680 | 734 | 85 | 11.6 |
| G_ratio | Mild|Moderate | 66.4 | 5.23 | 8.3 | 0.654 | 7.88 |
| G_ratio | Mild|Severe | 1.05e+03 | 85.5 | 129 | 10.7 | 8.31 |
| G_ratio | Moderate|Severe | 1.54e+03 | 121 | 186 | 15.2 | 8.15 |
| G_ratio | MCI|Normal | 7.99 | 0.747 | 0.991 | 0.0933 | 9.42 |
| G_ratio | repeat:Normal | 77.5 | 10.2 | 9.61 | 1.27 | 13.3 |
| G_ratio | repeat:Mild | 41.7 | 4.44 | 5.13 | 0.555 | 10.8 |
| G_ratio | repeat:Moderate | 134 | 14.1 | 16.1 | 1.76 | 11 |
| G_ratio | repeat:Severe | 7.61 | 0.552 | 0.946 | 0.069 | 7.3 |
| G_refl | Normal|AD | 1.15e+03 | 41.3 | 84.7 | 4.33 | 5.12 |
| G_refl | Normal|Mild | 1.76e+03 | 42.3 | 186 | 5.27 | 2.84 |
| G_refl | Normal|Moderate | 961 | 33.6 | 115 | 4.19 | 3.63 |
| G_refl | Normal|Severe | 2.2e+03 | 88.4 | 257 | 11 | 4.27 |
| G_refl | Mild|Moderate | 483 | 2.6 | 53.7 | 0.324 | 0.604 |
| G_refl | Mild|Severe | 1.38e+03 | 20.4 | 150 | 2.52 | 1.68 |
| G_refl | Moderate|Severe | 480 | 21.5 | 58.1 | 2.66 | 4.59 |
| G_refl | MCI|Normal | 1.23e+04 | 23.1 | 1.19e+03 | 2.84 | 0.238 |
| G_refl | repeat:Normal | 8.63e+03 | 17 | 849 | 2.1 | 0.247 |
| G_refl | repeat:Mild | 2.01e+04 | 44.5 | 2.08e+03 | 5.52 | 0.265 |
| G_refl | repeat:Moderate | 1.2e+04 | 13.1 | 1.2e+03 | 1.63 | 0.136 |
| G_refl | repeat:Severe | 1.52e+04 | 12 | 1.51e+03 | 1.5 | 0.0992 |
| R31 | Normal|AD | 1.54e+03 | 72.4 | 14.8 | 7.02 | 47.6 |
| R31 | Normal|Mild | 2.69e+03 | 108 | 330 | 13.5 | 4.09 |
| R31 | Normal|Moderate | 3.5e+03 | 140 | 431 | 17.5 | 4.06 |
| R31 | Normal|Severe | 1.88e+03 | 73.4 | 232 | 9.17 | 3.95 |
| R31 | Mild|Moderate | 44.1 | 2.02 | 5.51 | 0.253 | 4.59 |
| R31 | Mild|Severe | 75.1 | 3.36 | 9.38 | 0.42 | 4.48 |
| R31 | Moderate|Severe | 239 | 10.6 | 29.8 | 1.33 | 4.45 |
| R31 | MCI|Normal | 1.78 | 0.0609 | 0.223 | 0.00762 | 3.42 |
| R31 | repeat:Normal | 46.4 | 1.58 | 5.8 | 0.197 | 3.4 |
| R31 | repeat:Mild | 19.1 | 0.717 | 2.29 | 0.0896 | 3.91 |
| R31 | repeat:Moderate | 114 | 11.2 | 14.2 | 1.4 | 9.91 |
| R31 | repeat:Severe | 0.0869 | 0.00267 | 0.0108 | 0.000334 | 3.08 |

## Leave-one-solve-out classification
Each fold holds out one solve (all its test draws); the model is fitted on the other solves only (means, covariances, between-solve pairs not involving the held-out solve, standardisation, temperature by inner leave-one-solve-out). Reject = max posterior < 0.7. ECE = expected calibration error of the max posterior.

### `binary`
| features | dim | classifier | balanced_accuracy | reject_rate | bal_acc_on_accepted | ece | n_folds |
|---|---|---|---|---|---|---|---|
| G_coup | 63 | QDA meas-only | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_coup | 63 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_ratio | 3 | QDA meas-only | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_ratio | 3 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_coup | 63 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_all | 89 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_all | 89 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| R31 | 1 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_ratio | 3 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| R31 | 1 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| C3 | 1 | QDA meas-only | 0.994 | 0.008 | 0.997 | 0.003 | 8 |
| C3 | 1 | LDA | 0.993 | 0.009 | 0.998 | 0.003 | 8 |
| C3 | 1 | QDA+between | 0.993 | 0.010 | 0.998 | 0.004 | 8 |
| G_refl | 23 | QDA+between | 0.983 | 0.002 | 0.985 | 0.008 | 8 |
| G_refl | 23 | LDA | 0.955 | 0.004 | 0.959 | 0.020 | 8 |
| C2 | 1 | QDA+between | 0.939 | 0.096 | 0.954 | 0.048 | 8 |
| C2 | 1 | QDA meas-only | 0.937 | 0.078 | 0.958 | 0.051 | 8 |
| C2 | 1 | LDA | 0.912 | 0.133 | 0.943 | 0.036 | 8 |
| R31 | 1 | QDA meas-only | 0.907 | 0.000 | 0.907 | 0.046 | 8 |
| G_all | 89 | QDA meas-only | 0.568 | 0.000 | 0.568 | 0.216 | 8 |
| G_refl | 23 | QDA meas-only | 0.500 | 0.000 | 0.500 | 0.248 | 8 |

Confusion matrix, best row (G_coup, QDA meas-only); rows = true ['Normal', 'AD']: `[[300, 0], [0, 900]]`

### `three_merged` (preliminary: one head, two solves, 4 repeat pairs)
| features | dim | classifier | balanced_accuracy | reject_rate | bal_acc_on_accepted | ece | n_folds |
|---|---|---|---|---|---|---|---|
| G_coup | 63 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_ratio | 3 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_ratio | 3 | QDA meas-only | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_ratio | 3 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_coup | 63 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_all | 89 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| G_all | 89 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 8 |
| R31 | 1 | QDA meas-only | 0.999 | 0.000 | 0.999 | 0.004 | 8 |
| R31 | 1 | QDA+between | 0.965 | 0.010 | 0.967 | 0.037 | 8 |
| G_refl | 23 | QDA+between | 0.948 | 0.108 | 0.955 | 0.080 | 8 |
| R31 | 1 | LDA | 0.944 | 0.077 | 0.971 | 0.042 | 8 |
| C2 | 1 | QDA+between | 0.880 | 0.191 | 0.917 | 0.045 | 8 |
| C2 | 1 | LDA | 0.878 | 0.126 | 0.910 | 0.034 | 8 |
| C2 | 1 | QDA meas-only | 0.878 | 0.172 | 0.913 | 0.041 | 8 |
| G_refl | 23 | LDA | 0.854 | 0.008 | 0.855 | 0.102 | 8 |
| G_coup | 63 | QDA meas-only | 0.667 | 0.000 | 0.667 | 0.249 | 8 |
| C3 | 1 | QDA meas-only | 0.494 | 0.758 | n/a | 0.254 | 8 |
| C3 | 1 | QDA+between | 0.476 | 0.761 | n/a | 0.283 | 8 |
| G_all | 89 | QDA meas-only | 0.474 | 0.041 | 0.470 | 0.361 | 8 |
| C3 | 1 | LDA | 0.467 | 0.687 | n/a | 0.301 | 8 |
| G_refl | 23 | QDA meas-only | 0.308 | 0.313 | 0.333 | 0.417 | 8 |

Confusion matrix, best row (G_coup, QDA+between); rows = true ['Normal', 'Mild+Moderate', 'Severe']: `[[300, 0, 0], [0, 600, 0], [0, 0, 300]]`

### `three` (preliminary: one head, two solves, 4 repeat pairs)
| features | dim | classifier | balanced_accuracy | reject_rate | bal_acc_on_accepted | ece | n_folds |
|---|---|---|---|---|---|---|---|
| G_coup | 63 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 6 |
| G_ratio | 3 | LDA | 1.000 | 0.000 | 1.000 | 0.000 | 6 |
| G_ratio | 3 | QDA meas-only | 1.000 | 0.000 | 1.000 | 0.000 | 6 |
| G_ratio | 3 | QDA+between | 1.000 | 0.000 | 1.000 | 0.000 | 6 |
| G_all | 89 | LDA | 0.998 | 0.000 | 0.998 | 0.002 | 6 |
| G_all | 89 | QDA+between | 0.988 | 0.667 | n/a | 0.264 | 6 |
| R31 | 1 | QDA meas-only | 0.987 | 0.000 | 0.987 | 0.013 | 6 |
| R31 | 1 | LDA | 0.980 | 0.016 | 0.987 | 0.005 | 6 |
| R31 | 1 | QDA+between | 0.980 | 0.002 | 0.982 | 0.018 | 6 |
| C2 | 1 | QDA meas-only | 0.886 | 0.129 | 0.925 | 0.023 | 6 |
| C2 | 1 | QDA+between | 0.883 | 0.143 | 0.928 | 0.020 | 6 |
| C2 | 1 | LDA | 0.882 | 0.108 | 0.917 | 0.032 | 6 |
| G_coup | 63 | QDA+between | 0.831 | 0.667 | n/a | 0.362 | 6 |
| G_refl | 23 | LDA | 0.662 | 0.004 | 0.661 | 0.337 | 6 |
| C3 | 1 | QDA meas-only | 0.564 | 0.572 | n/a | 0.128 | 6 |
| C3 | 1 | QDA+between | 0.564 | 0.613 | n/a | 0.118 | 6 |
| C3 | 1 | LDA | 0.559 | 0.414 | 0.490 | 0.276 | 6 |
| G_refl | 23 | QDA+between | 0.498 | 1.000 | n/a | 0.144 | 6 |
| G_coup | 63 | QDA meas-only | 0.341 | 0.096 | 0.333 | 0.605 | 6 |
| G_all | 89 | QDA meas-only | 0.237 | 0.074 | 0.252 | 0.713 | 6 |
| G_refl | 23 | QDA meas-only | 0.000 | 0.146 | 0.000 | 0.928 | 6 |

Confusion matrix, best row (G_coup, LDA); rows = true ['Normal', 'Mild', 'Severe']: `[[300, 0, 0], [0, 300, 0], [0, 0, 300]]`

## Per-solve values of the ratio and band-power features (dB, mean over noisy draws)
R32 = R31 - R21 exactly (same geometric means), so G_ratio has rank 2. Solve-to-solve SD per feature = rms over the repeat pairs of (difference / sqrt 2).
| solve | stage | set | R31 | R21 | R32 | k1_band | k2_band | k3_band | logN |
|---|---|---|---|---|---|---|---|---|---|
| brain_sevem_layer_Healthy.s6p | Normal | v1 | -14.48 | -20.41 | 5.93 | -37.33 | -57.70 | -51.81 | -2.58 |
| new_Healthy.s6p | Normal | v2 | -14.67 | -20.73 | 6.05 | -36.95 | -57.67 | -51.62 | -2.54 |
| new_MCI.s6p | MCI | v2 | -14.62 | -20.69 | 6.08 | -36.79 | -57.48 | -51.40 | -2.54 |
| Brain_sevem_layer_MildAD.s6p | Mild | v1 | -16.20 | -19.31 | 3.11 | -37.56 | -56.84 | -53.75 | -2.54 |
| new_MildAD.s6p | Mild | v2 | -16.06 | -19.49 | 3.43 | -37.07 | -56.55 | -53.13 | -2.50 |
| Brain_sevem_layer_ModerateAD.s6p | Moderate | v1 | -16.51 | -19.77 | 3.27 | -37.38 | -57.14 | -53.89 | -2.55 |
| new_ModerateAD.s6p | Moderate | v2 | -16.17 | -19.53 | 3.36 | -37.10 | -56.62 | -53.27 | -2.46 |
| brain_sevem_layer_SevereAD.s6p | Severe | v1 | -15.85 | -18.17 | 2.32 | -37.87 | -56.03 | -53.68 | -2.53 |
| new_SevereAD.s6p | Severe | v2 | -15.86 | -18.06 | 2.21 | -37.65 | -55.71 | -53.50 | -2.45 |

Stage gaps in units of the solve-to-solve SD (stage means over solves):
| feature | solve_SD_dB | Normal|Mild gap/SD | Mild|Moderate gap/SD | Mild|Severe gap/SD | Moderate|Severe gap/SD | Normal|MCI gap/SD |
|---|---|---|---|---|---|---|
| R31 | 0.15 | 10.64 | 1.43 | 1.89 | 3.32 | 0.27 |
| R21 | 0.16 | 7.34 | 1.58 | 8.06 | 9.64 | 0.79 |
| R32 | 0.13 | 20.92 | 0.33 | 7.74 | 8.07 | 0.67 |
| k2_band | 0.24 | 4.16 | 0.76 | 3.48 | 4.24 | 0.88 |
| k3_band | 0.32 | 5.35 | 0.44 | 0.48 | 0.04 | 0.97 |

## Mutual information with the stage (Normal / Mild / Moderate / Severe), bits (max 2)
**MI_stage_gauss_between** (ranking key): 1-D Gaussian class model whose spread includes the between-solve variance, i.e. the information a new solve would still carry. MI_stage_pooled (kNN, both solves pooled) is NOT a cross-solve measure: it is high whenever the 8 solve clusters are separable by class, even if a new solve would land elsewhere. v2only / v1only = one solve per stage (kNN).
| feature | group | MI_stage_gauss_between_bits | MI_stage_pooled_bits | MI_stage_v2only_bits | MI_stage_v1only_bits | MI_binary_pooled_bits |
|---|---|---|---|---|---|---|
| R21 | G_ratio | 1.659 | 1.793 | 1.586 | 2.004 | 0.812 |
| R32 | G_ratio | 1.507 | 1.737 | 1.650 | 1.847 | 0.812 |
| R31 | G_ratio | 1.346 | 1.736 | 1.956 | 2.004 | 0.812 |
| k2_band | G_coup | 1.000 | 1.162 | 1.360 | 1.242 | 0.614 |
| k2_sb3.50 | G_coup | 0.889 | 1.436 | 1.541 | 1.727 | 0.762 |
| k2_sb3.60 | G_coup | 0.839 | 1.012 | 1.492 | 1.022 | 0.740 |
| k2_sb3.20 | G_coup | 0.812 | 0.909 | 1.080 | 0.957 | 0.386 |
| k2_sb3.55 | G_coup | 0.784 | 1.167 | 1.600 | 1.252 | 0.811 |
| k3_sb3.55 | G_coup | 0.774 | 0.965 | 0.981 | 1.239 | 0.812 |
| k3_band | G_coup | 0.774 | 0.875 | 0.921 | 0.873 | 0.802 |
| k3_sb3.45 | G_coup | 0.747 | 0.897 | 0.869 | 0.975 | 0.812 |
| k3_sb3.50 | G_coup | 0.734 | 0.960 | 0.933 | 1.044 | 0.812 |
| k2_sb3.25 | G_coup | 0.721 | 0.835 | 0.981 | 0.879 | 0.331 |
| k3_sb3.35 | G_coup | 0.714 | 0.779 | 0.809 | 0.873 | 0.746 |
| k2_sb3.30 | G_coup | 0.705 | 0.718 | 0.864 | 0.715 | 0.225 |

By group (mean over features):
| group | MI_stage_gauss_between_bits | MI_stage_pooled_bits | MI_stage_v2only_bits | MI_stage_v1only_bits | MI_binary_pooled_bits |
|---|---|---|---|---|---|
| G_coup | 0.343 | 0.615 | 0.839 | 0.705 | 0.364 |
| G_ratio | 1.504 | 1.755 | 1.731 | 1.951 | 0.812 |
| G_refl | 0.046 | 0.230 | 0.351 | 0.200 | 0.137 |

By ring distance (sub-band features, mean MI):
| k | MI_stage_gauss_between_bits | MI_stage_pooled_bits | MI_stage_v2only_bits |
|---|---|---|---|
| 0 | 0.051 | 0.265 | 0.396 |
| 1 | 0.157 | 0.424 | 0.681 |
| 2 | 0.424 | 0.753 | 0.952 |
| 3 | 0.399 | 0.642 | 0.870 |
