# QC report - track A (A-sphere7-ring6-hfss), code 3f993a4

## Parsed files (native grids)
| class | file | N | F_native | f_min_GHz | f_max_GHz | step_MHz | uniform | option_line | values_per_f |
|---|---|---|---|---|---|---|---|---|---|
| Normal | new_with_slices_Healthy_sliced.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Mild | new_with_slices_Mild_lobe.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Moderate | new_with_slices_Moderate_lobe.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Severe | new_with_slices_Severe_lobe.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |

Common grid: 3.200-4.200 GHz, 201 points, step 5.0 MHz. S tensor shape (4, 201, 6, 6) (sims, F, N, N).

## Integrity (native grids)
recip_rel_band_* = |Sij - Sji| / band-rms|Sij| over off-diagonal entries (dB). n_glitch_pts = (f, pair) points with local |Sij - Sji|/|Sij| > -20 dB. Passive = column power sum and largest singular value <= 1 + tol. interp_* = leave-every-other-out spline error / band-rms level (dB).
| class | recip_abs_max | recip_rel_band_max_db | recip_rel_band_p99_db | recip_rel_band_median_db | n_glitch_pts | n_pts | col_power_max | sigma_max | passive | resampled |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 0.000185 | -23.3 | -61.2 | -96 | 0 | 6030 | 0.904 | 0.951 | True | False |
| Mild | 4.2e-05 | -30.7 | -42.5 | -86 | 0 | 6030 | 0.905 | 0.952 | True | False |
| Moderate | 6.88e-05 | -30.1 | -53.2 | -89.7 | 0 | 6030 | 0.902 | 0.951 | True | False |
| Severe | 0.000113 | -25.7 | -52.6 | -87.3 | 0 | 6030 | 0.902 | 0.95 | True | False |

Glitch frequencies (GHz):

- Normal: []
- Mild: []
- Moderate: []
- Severe: []

## Circulant symmetry spread per ring distance k (common grid)
mag_spread = max-min of |S(t,t+k)| across t in dB; cplx_rel = rms complex deviation from the ring mean relative to its magnitude (dB, noise-to-signal).
| class | k | n_pairs | mag_spread_db_median | mag_spread_db_p95 | mag_spread_db_max | mag_std_db_median | cplx_rel_db_median | level_db_median |
|---|---|---|---|---|---|---|---|---|
| Normal | 0 | 6 | 0.0661 | 0.479 | 0.807 | 0.0221 | -48.9 | -4.61 |
| Normal | 1 | 12 | 0.158 | 0.299 | 0.546 | 0.0557 | -39.5 | -42 |
| Normal | 2 | 12 | 0.282 | 2.26 | 3.47 | 0.0976 | -33 | -60.4 |
| Normal | 3 | 6 | 0.138 | 1.21 | 6.6 | 0.0602 | -40.4 | -55.7 |
| Mild | 0 | 6 | 0.261 | 1.13 | 1.54 | 0.0881 | -37.6 | -4.8 |
| Mild | 1 | 12 | 0.313 | 0.694 | 0.752 | 0.116 | -30.6 | -41.4 |
| Mild | 2 | 12 | 1.26 | 7.06 | 15.4 | 0.488 | -21.7 | -59.4 |
| Mild | 3 | 6 | 0.634 | 1.94 | 3.91 | 0.294 | -25 | -56.1 |
| Moderate | 0 | 6 | 0.277 | 1.15 | 2.36 | 0.091 | -36.7 | -4.9 |
| Moderate | 1 | 12 | 0.428 | 0.641 | 0.685 | 0.15 | -28.1 | -41.6 |
| Moderate | 2 | 12 | 0.877 | 3.65 | 6.6 | 0.31 | -23.7 | -59.3 |
| Moderate | 3 | 6 | 0.361 | 1.39 | 5.42 | 0.156 | -28.6 | -56.2 |
| Severe | 0 | 6 | 0.146 | 0.795 | 1.35 | 0.0493 | -40.5 | -4.99 |
| Severe | 1 | 12 | 0.287 | 0.685 | 0.747 | 0.103 | -33.6 | -42 |
| Severe | 2 | 12 | 0.462 | 2.32 | 5.68 | 0.146 | -31.5 | -58.9 |
| Severe | 3 | 6 | 0.233 | 0.888 | 6.2 | 0.101 | -35.5 | -57.1 |

## Port-to-antenna mapping check
All 60 distinct ring orderings (720 permutations mod rotation/reflection) scored by circulant error = mean over f and k>=1 of std_t |S(t,t+k)| (dB). Config mapping port_to_ant = [4, 3, 2, 1, 6, 5] (equivalent under reflection/rotation to 1-2-3-4-5-6, i.e. ports in file order are consecutive around the ring).
| class | config_mapping_error_db | config_rank_of_60 | best_mapping | best_error_db | 2nd_best_error_db | worst_error_db |
|---|---|---|---|---|---|---|
| Normal | 0.15 | 1 | 1-2-3-4-5-6 | 0.15 | 1.79 | 7.25 |
| Mild | 0.383 | 1 | 1-2-3-4-5-6 | 0.383 | 2.12 | 7.26 |
| Moderate | 0.294 | 1 | 1-2-3-4-5-6 | 0.294 | 2.07 | 7.17 |
| Severe | 0.183 | 1 | 1-2-3-4-5-6 | 0.183 | 1.93 | 6.91 |

## Orientation re-derivation (native grids, per-port min |Sii|, parabolic refine)
Shoulder = power average of |Sii|^2 over 3.38-3.52 GHz.
| class | f_res_mean_MHz | f_res_min | f_res_max | notch_min_dB | notch_max_dB | shoulder_mean_dB | shoulder_spread_dB |
|---|---|---|---|---|---|---|---|
| Normal | 3659.2 | 3658.5 | 3660.4 | -21.236 | -20.862 | -11.138 | 0.11433 |
| Mild | 3654.9 | 3653.4 | 3656.9 | -20.991 | -19.914 | -10.554 | 0.45998 |
| Moderate | 3656.5 | 3652.9 | 3658.2 | -21.161 | -20.011 | -10.333 | 0.48246 |
| Severe | 3655.9 | 3654.7 | 3658.3 | -20.921 | -20.189 | -9.8719 | 0.23545 |

## Confound assessment (common grid)
Ring-mode c_k(f) = mean_t S(t,t+k). diff/noise = rms_f|c_k^a - c_k^b| divided by the pooled rms port-to-port deviation (complex). rms_dB_diff = rms_f of dB difference of |c_k|. Project membership is from the model card (sims.csv), not from file headers.
| pair | same_project | k0_diff/noise | k0_rms_dB_diff | k1_diff/noise | k1_rms_dB_diff | k2_diff/noise | k2_rms_dB_diff | k3_diff/noise | k3_rms_dB_diff | k0_shoulder_dB_diff |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal-Mild | True | 5.71 | 0.717 | 8.31 | 0.552 | 2.72 | 1.35 | 2.88 | 1.03 | 0.577 |
| Normal-Moderate | True | 5.84 | 0.686 | 6.83 | 0.555 | 3.75 | 1.5 | 3.96 | 1.41 | 0.802 |
| Normal-Severe | True | 11 | 0.866 | 14.3 | 0.878 | 8.75 | 2.26 | 6.52 | 1.82 | 1.27 |
| Mild-Moderate | True | 1.21 | 0.201 | 1.03 | 0.21 | 0.994 | 0.458 | 2.4 | 0.444 | 0.225 |
| Mild-Severe | True | 3.14 | 0.398 | 4.31 | 0.735 | 2.92 | 1.58 | 6.51 | 0.917 | 0.689 |
| Moderate-Severe | True | 2.07 | 0.248 | 3.18 | 0.542 | 2.47 | 1.14 | 5.88 | 0.667 | 0.464 |

Within-file port-to-port noise (rms over f of std_t in dB):
| class | k0_port_noise_rms_dB | k1_port_noise_rms_dB | k2_port_noise_rms_dB | k3_port_noise_rms_dB |
|---|---|---|---|---|
| Normal | 0.0612 | 0.0629 | 0.333 | 0.355 |
| Mild | 0.177 | 0.136 | 0.994 | 0.404 |
| Moderate | 0.183 | 0.16 | 0.646 | 0.332 |
| Severe | 0.113 | 0.139 | 0.397 | 0.317 |
