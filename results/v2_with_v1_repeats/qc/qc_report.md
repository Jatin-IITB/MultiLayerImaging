# QC report - track A (A-sphere7-ring6-hfss), code c95604c

## Parsed files (native grids)
| class | file | N | F_native | f_min_GHz | f_max_GHz | step_MHz | uniform | option_line | values_per_f |
|---|---|---|---|---|---|---|---|---|---|
| Normal | brain_sevem_layer_Healthy.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Normal | new_Healthy.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| MCI | new_MCI.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Mild | Brain_sevem_layer_MildAD.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Mild | new_MildAD.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Moderate | Brain_sevem_layer_ModerateAD.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Moderate | new_ModerateAD.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Severe | brain_sevem_layer_SevereAD.s6p | 6 | 501 | 3.2 | 4.2 | 2 | True | # GHz S MA R 50.000000 | 72 |
| Severe | new_SevereAD.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |

Common grid: 3.200-4.200 GHz, 201 points, step 5.0 MHz. S tensor shape (9, 201, 6, 6) (sims, F, N, N).

## Integrity (native grids)
recip_rel_band_* = |Sij - Sji| / band-rms|Sij| over off-diagonal entries (dB). n_glitch_pts = (f, pair) points with local |Sij - Sji|/|Sij| > -20 dB. Passive = column power sum and largest singular value <= 1 + tol. interp_* = leave-every-other-out spline error / band-rms level (dB).
| class | recip_abs_max | recip_rel_band_max_db | recip_rel_band_p99_db | recip_rel_band_median_db | n_glitch_pts | n_pts | col_power_max | sigma_max | passive | resampled | interp_rel_diag_max_db | interp_rel_diag_median_db | interp_rel_off_max_db | interp_rel_off_median_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 0.000691 | -3.58 | -39.6 | -77.2 | 12 | 8430 | 0.962 | 0.982 | True | False | nan | nan | nan | nan |
| Normal | 0.000408 | -29.2 | -65 | -96.6 | 0 | 8430 | 0.963 | 0.982 | True | False | nan | nan | nan | nan |
| MCI | 1.61e-05 | -43.1 | -66.9 | -98.2 | 0 | 8430 | 0.963 | 0.982 | True | False | nan | nan | nan | nan |
| Mild | 0.00117 | -15.8 | -40.3 | -76 | 32 | 8430 | 0.961 | 0.981 | True | False | nan | nan | nan | nan |
| Mild | 4.13e-05 | -43.1 | -56.4 | -88 | 0 | 8430 | 0.962 | 0.982 | True | False | nan | nan | nan | nan |
| Moderate | 2.59e-05 | -33.9 | -48 | -81.7 | 2 | 8430 | 0.961 | 0.981 | True | False | nan | nan | nan | nan |
| Moderate | 1.09e-05 | -41 | -64.6 | -93.4 | 0 | 8430 | 0.961 | 0.981 | True | False | nan | nan | nan | nan |
| Severe | 0.000661 | -8.02 | -41.7 | -79.1 | 18 | 15030 | 0.902 | 0.95 | True | True | -99.7 | -155 | -8.61 | -134 |
| Severe | 0.000209 | -18.7 | -42.7 | -93.3 | 0 | 8430 | 0.958 | 0.98 | True | False | nan | nan | nan | nan |

Glitch frequencies (GHz):

- Normal: [3.565, 4.135, 4.14, 4.145, 4.15, 4.155]
- Normal: []
- MCI: []
- Mild: [2.875, 2.88, 2.885, 2.89, 2.895, 2.9, 2.905, 2.91, 2.915, 2.92, 2.925, 2.93, 2.935, 2.94, 2.945, 2.95, 2.955]
- Mild: []
- Moderate: [3.81]
- Moderate: []
- Severe: [3.28, 3.282, 3.714, 3.716, 3.814, 3.904, 3.906, 3.908, 3.91]
- Severe: []

## Circulant symmetry spread per ring distance k (common grid)
mag_spread = max-min of |S(t,t+k)| across t in dB; cplx_rel = rms complex deviation from the ring mean relative to its magnitude (dB, noise-to-signal).
| class | k | n_pairs | mag_spread_db_median | mag_spread_db_p95 | mag_spread_db_max | mag_std_db_median | cplx_rel_db_median | level_db_median |
|---|---|---|---|---|---|---|---|---|
| Normal | 0 | 6 | 0.237 | 1.74 | 5.03 | 0.0856 | -37.6 | -4.08 |
| Normal | 1 | 12 | 0.605 | 1.8 | 2.42 | 0.223 | -25.9 | -43 |
| Normal | 2 | 12 | 1.13 | 10.5 | 20 | 0.367 | -21.3 | -61.4 |
| Normal | 3 | 6 | 0.607 | 2.34 | 2.92 | 0.252 | -28.8 | -55.3 |
| Normal | 0 | 6 | 0.156 | 1.55 | 10.7 | 0.0492 | -43.4 | -4.41 |
| Normal | 1 | 12 | 0.714 | 1.38 | 5.72 | 0.244 | -28.9 | -42.5 |
| Normal | 2 | 12 | 0.864 | 4.53 | 9.92 | 0.287 | -26.2 | -60.9 |
| Normal | 3 | 6 | 0.392 | 1.85 | 1.98 | 0.166 | -33 | -55.2 |
| MCI | 0 | 6 | 0.112 | 0.507 | 0.918 | 0.0402 | -42.8 | -4.71 |
| MCI | 1 | 12 | 0.228 | 0.841 | 0.934 | 0.0769 | -35.7 | -41.8 |
| MCI | 2 | 12 | 0.539 | 2.84 | 5.69 | 0.188 | -31.6 | -60.3 |
| MCI | 3 | 6 | 0.176 | 0.993 | 1.31 | 0.0748 | -38.4 | -56 |
| Mild | 0 | 6 | 0.319 | 4.93 | 17.3 | 0.106 | -36 | -4.26 |
| Mild | 1 | 12 | 1.13 | 1.74 | 1.86 | 0.366 | -24.3 | -42.8 |
| Mild | 2 | 12 | 1.63 | 6.24 | 14.3 | 0.567 | -21.8 | -59.2 |
| Mild | 3 | 6 | 1.02 | 4.18 | 5.35 | 0.434 | -24.7 | -56.2 |
| Mild | 0 | 6 | 0.225 | 1 | 2.07 | 0.0817 | -36.2 | -4.83 |
| Mild | 1 | 12 | 0.308 | 0.702 | 0.78 | 0.107 | -33.4 | -41.6 |
| Mild | 2 | 12 | 0.531 | 3.76 | 17.4 | 0.171 | -29.2 | -59.6 |
| Mild | 3 | 6 | 0.227 | 1.29 | 2.01 | 0.095 | -37.5 | -56.6 |
| Moderate | 0 | 6 | 0.233 | 2.03 | 14.5 | 0.088 | -36.8 | -4.37 |
| Moderate | 1 | 12 | 0.596 | 2.46 | 2.81 | 0.196 | -29.4 | -42.6 |
| Moderate | 2 | 12 | 1.11 | 5.86 | 19.1 | 0.425 | -23.4 | -59.5 |
| Moderate | 3 | 6 | 0.409 | 2.39 | 3.19 | 0.167 | -31.3 | -56.4 |
| Moderate | 0 | 6 | 0.0686 | 0.478 | 1.66 | 0.0239 | -45 | -4.85 |
| Moderate | 1 | 12 | 0.287 | 0.574 | 0.61 | 0.0995 | -33.6 | -41.9 |
| Moderate | 2 | 12 | 0.971 | 4.35 | 8.97 | 0.306 | -26.8 | -59.8 |
| Moderate | 3 | 6 | 0.258 | 0.874 | 1.08 | 0.11 | -36.1 | -56.8 |
| Severe | 0 | 6 | 0.134 | 2.53 | 23.6 | 0.0521 | -35.4 | -4.26 |
| Severe | 1 | 12 | 0.796 | 1.87 | 2.09 | 0.281 | -27 | -43 |
| Severe | 2 | 12 | 1.39 | 11 | 25.2 | 0.47 | -21 | -58.7 |
| Severe | 3 | 6 | 0.839 | 4.31 | 4.61 | 0.361 | -25.9 | -56.1 |
| Severe | 0 | 6 | 0.107 | 0.741 | 2.39 | 0.0351 | -42.1 | -4.77 |
| Severe | 1 | 12 | 0.288 | 0.774 | 0.796 | 0.0966 | -35 | -42.4 |
| Severe | 2 | 12 | 0.723 | 5.21 | 7.76 | 0.266 | -27.4 | -59 |
| Severe | 3 | 6 | 0.224 | 0.853 | 1.32 | 0.1 | -36 | -57.5 |

## Port-to-antenna mapping check
All 60 distinct ring orderings (720 permutations mod rotation/reflection) scored by circulant error = mean over f and k>=1 of std_t |S(t,t+k)| (dB). Config mapping port_to_ant = [4, 3, 2, 1, 6, 5] (equivalent under reflection/rotation to 1-2-3-4-5-6, i.e. ports in file order are consecutive around the ring).
| class | config_mapping_error_db | config_rank_of_60 | best_mapping | best_error_db | 2nd_best_error_db | worst_error_db |
|---|---|---|---|---|---|---|
| Normal | 0.46 | 1 | 1-2-3-4-5-6 | 0.46 | 1.71 | 5.97 |
| Normal | 0.295 | 1 | 1-2-3-4-5-6 | 0.295 | 1.56 | 6.02 |
| MCI | 0.144 | 1 | 1-2-3-4-5-6 | 0.144 | 1.48 | 6.08 |
| Mild | 0.47 | 1 | 1-2-3-4-5-6 | 0.47 | 1.84 | 6 |
| Mild | 0.193 | 1 | 1-2-3-4-5-6 | 0.193 | 1.69 | 6.19 |
| Moderate | 0.358 | 1 | 1-2-3-4-5-6 | 0.358 | 1.81 | 6.11 |
| Moderate | 0.191 | 1 | 1-2-3-4-5-6 | 0.191 | 1.69 | 6.12 |
| Severe | 0.638 | 1 | 1-2-3-4-5-6 | 0.638 | 2.18 | 6.82 |
| Severe | 0.208 | 1 | 1-2-3-4-5-6 | 0.208 | 1.68 | 5.84 |

## Orientation re-derivation (native grids, per-port min |Sii|, parabolic refine)
Shoulder = power average of |Sii|^2 over 3.38-3.52 GHz.
| class | f_res_mean_MHz | f_res_min | f_res_max | notch_min_dB | notch_max_dB | shoulder_mean_dB | shoulder_spread_dB |
|---|---|---|---|---|---|---|---|
| Normal | 3632.1 | 3622.2 | 3644.1 | -39.274 | -27.454 | -9.6333 | 1.6079 |
| MCI | 3655.5 | 3654.5 | 3656.4 | -21.227 | -20.417 | -10.95 | 0.15823 |
| Mild | 3640.4 | 3618.1 | 3656.4 | -38.298 | -19.494 | -9.0934 | 2.328 |
| Moderate | 3637.5 | 3624.5 | 3648.5 | -40.72 | -25.519 | -9.1233 | 2.0378 |
| Severe | 3638.5 | 3625.9 | 3649.7 | -49.163 | -26.036 | -8.6881 | 1.931 |

## Confound assessment (common grid)
Ring-mode c_k(f) = mean_t S(t,t+k). diff/noise = rms_f|c_k^a - c_k^b| divided by the pooled rms port-to-port deviation (complex). rms_dB_diff = rms_f of dB difference of |c_k|. Project membership is from the model card (sims.csv), not from file headers.
| pair | same_project | k0_diff/noise | k0_rms_dB_diff | k1_diff/noise | k1_rms_dB_diff | k2_diff/noise | k2_rms_dB_diff | k3_diff/noise | k3_rms_dB_diff | k0_shoulder_dB_diff |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal-Normal | True | 8.93 | 2.62 | 8.95 | 1.25 | 2.88 | 2.59 | 11.5 | 0.897 | -1.35 |
| Normal-MCI | True | 16.3 | 3.08 | 17.7 | 2.13 | 5.41 | 3.47 | 19 | 1.61 | -1.99 |
| Normal-Mild | False | 1.73 | 0.876 | 1.44 | 0.496 | 1.51 | 3.06 | 3.49 | 1.62 | 0.771 |
| Normal-Mild | True | 12.4 | 2.84 | 14.5 | 1.88 | 5.78 | 4.47 | 18.7 | 1.78 | -1.04 |
| Normal-Moderate | False | 2.58 | 0.968 | 1.05 | 0.554 | 1.39 | 2.91 | 5.08 | 1.8 | 0.709 |
| Normal-Moderate | True | 12.4 | 2.69 | 12.1 | 1.45 | 5.29 | 3.94 | 17.5 | 1.55 | -1.04 |
| Normal-Severe | True | 2.85 | 1.42 | 2.45 | 0.77 | 2 | 3.79 | 4.78 | 1.74 | 1.12 |
| Normal-Severe | True | 11.6 | 2.74 | 11.4 | 1.47 | 5.67 | 4.46 | 19.1 | 1.85 | -0.56 |
| Normal-MCI | True | 11.6 | 2.31 | 8.79 | 1 | 4.47 | 2.21 | 8.94 | 1.12 | -0.642 |
| Normal-Mild | False | 6.04 | 2.74 | 7.42 | 1.65 | 3.6 | 2.38 | 8.29 | 2.06 | 2.12 |
| Normal-Mild | True | 8.08 | 2.22 | 5.21 | 0.93 | 4.66 | 3.36 | 11.1 | 1.71 | 0.309 |
| Normal-Moderate | False | 9.01 | 2.55 | 6.97 | 1.66 | 2.87 | 2.13 | 11.7 | 2.25 | 2.06 |
| Normal-Moderate | True | 5.79 | 1.48 | 2.79 | 0.545 | 3.76 | 2.54 | 9.27 | 1.55 | 0.313 |
| Normal-Severe | True | 8.07 | 2.63 | 10.3 | 1.81 | 3.5 | 2.84 | 6.39 | 2.27 | 2.47 |
| Normal-Severe | True | 6.21 | 1.6 | 3.34 | 0.77 | 4.53 | 3.28 | 12.5 | 2.1 | 0.788 |
| MCI-Mild | False | 9.57 | 3.45 | 12.3 | 2.49 | 6.69 | 3.31 | 13.1 | 2.51 | 2.76 |
| MCI-Mild | True | 5.34 | 0.646 | 7.86 | 0.564 | 4.32 | 1.74 | 9.8 | 1.53 | 0.951 |
| MCI-Moderate | False | 15.7 | 3.32 | 12 | 2.48 | 5.36 | 3.01 | 20.8 | 2.58 | 2.7 |
| MCI-Moderate | True | 13.1 | 1.23 | 11 | 0.859 | 5.42 | 1.66 | 10 | 1.75 | 0.955 |
| MCI-Severe | True | 13 | 3.48 | 18.6 | 2.6 | 6.12 | 3.57 | 10.3 | 2.6 | 3.11 |
| MCI-Severe | True | 11.8 | 1.33 | 12.6 | 1.06 | 6.73 | 2.03 | 13.2 | 2.25 | 1.43 |
| Mild-Mild | False | 7.76 | 3.18 | 10.1 | 2.16 | 6.75 | 3.64 | 11.8 | 1.52 | -1.81 |
| Mild-Moderate | True | 0.459 | 0.451 | 0.532 | 0.206 | 0.687 | 0.738 | 0.704 | 0.416 | -0.062 |
| Mild-Moderate | False | 7.16 | 2.93 | 8.69 | 1.74 | 6.1 | 2.9 | 10.8 | 1.09 | -1.81 |
| Mild-Severe | False | 0.78 | 0.938 | 0.521 | 0.433 | 0.792 | 1.11 | 1.88 | 0.584 | 0.345 |
| Mild-Severe | False | 6.84 | 2.95 | 8.12 | 1.71 | 6.19 | 3.36 | 11.9 | 0.972 | -1.33 |
| Mild-Moderate | False | 11.4 | 3.04 | 9.72 | 2.15 | 5.32 | 3.34 | 19.3 | 1.48 | 1.75 |
| Mild-Moderate | True | 6.07 | 1.04 | 4.45 | 0.536 | 2.26 | 1.38 | 4.43 | 0.744 | 0.00354 |
| Mild-Severe | True | 10 | 3.2 | 15.5 | 2.28 | 6.09 | 3.56 | 9.1 | 1.6 | 2.16 |
| Mild-Severe | True | 6.44 | 1.1 | 6.1 | 0.839 | 3.26 | 0.939 | 6.49 | 1.09 | 0.479 |
| Moderate-Moderate | False | 11.6 | 2.77 | 8.28 | 1.73 | 4.74 | 2.59 | 17.6 | 1.15 | -1.74 |
| Moderate-Severe | False | 1.22 | 0.562 | 1.04 | 0.399 | 1.04 | 1.31 | 1.96 | 0.313 | 0.407 |
| Moderate-Severe | False | 10.6 | 2.8 | 7.73 | 1.7 | 4.86 | 3.12 | 19.1 | 0.918 | -1.27 |
| Moderate-Severe | True | 9.65 | 2.89 | 13.2 | 1.87 | 5.52 | 2.86 | 8.21 | 1.31 | 2.15 |
| Moderate-Severe | True | 3.23 | 0.269 | 2.58 | 0.549 | 2.12 | 1.13 | 6.49 | 0.769 | 0.475 |
| Severe-Severe | True | 8.88 | 2.9 | 12.4 | 1.74 | 5.45 | 3.17 | 9.24 | 1.08 | -1.68 |

Within-file port-to-port noise (rms over f of std_t in dB):
| class | k0_port_noise_rms_dB | k1_port_noise_rms_dB | k2_port_noise_rms_dB | k3_port_noise_rms_dB |
|---|---|---|---|---|
| Normal | 0.275 | 0.321 | 1.75 | 0.466 |
| Normal | 0.421 | 0.304 | 0.827 | 0.378 |
| MCI | 0.0796 | 0.121 | 0.461 | 0.173 |
| Mild | 1.06 | 0.402 | 1.11 | 0.846 |
| Mild | 0.182 | 0.118 | 0.719 | 0.243 |
| Moderate | 0.659 | 0.394 | 1.14 | 0.451 |
| Moderate | 0.101 | 0.122 | 0.662 | 0.183 |
| Severe | 0.827 | 0.358 | 1.58 | 0.758 |
| Severe | 0.145 | 0.154 | 0.785 | 0.17 |
