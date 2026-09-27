# QC report - track A (A-sphere7-ring6-hfss), code 89db27a

## Parsed files (native grids)
| class | file | N | F_native | f_min_GHz | f_max_GHz | step_MHz | uniform | option_line | values_per_f |
|---|---|---|---|---|---|---|---|---|---|
| Normal | brain_sevem_layer_Healthy.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Mild | Brain_sevem_layer_MildAD.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Moderate | Brain_sevem_layer_ModerateAD.s6p | 6 | 281 | 2.8 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Severe | brain_sevem_layer_SevereAD.s6p | 6 | 501 | 3.2 | 4.2 | 2 | True | # GHz S MA R 50.000000 | 72 |

Common grid: 3.200-4.200 GHz, 201 points, step 5.0 MHz. S tensor shape (4, 201, 6, 6) (sims, F, N, N).

## Integrity (native grids)
recip_rel_band_* = |Sij - Sji| / band-rms|Sij| over off-diagonal entries (dB). n_glitch_pts = (f, pair) points with local |Sij - Sji|/|Sij| > -20 dB. Passive = column power sum and largest singular value <= 1 + tol. interp_* = leave-every-other-out spline error / band-rms level (dB).
| class | recip_abs_max | recip_rel_band_max_db | recip_rel_band_p99_db | recip_rel_band_median_db | n_glitch_pts | n_pts | col_power_max | sigma_max | passive | resampled | interp_rel_diag_max_db | interp_rel_diag_median_db | interp_rel_off_max_db | interp_rel_off_median_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 0.000691 | -3.58 | -39.6 | -77.2 | 12 | 8430 | 0.962 | 0.982 | True | False | nan | nan | nan | nan |
| Mild | 0.00117 | -15.8 | -40.3 | -76 | 32 | 8430 | 0.961 | 0.981 | True | False | nan | nan | nan | nan |
| Moderate | 2.59e-05 | -33.9 | -48 | -81.7 | 2 | 8430 | 0.961 | 0.981 | True | False | nan | nan | nan | nan |
| Severe | 0.000661 | -8.02 | -41.7 | -79.1 | 18 | 15030 | 0.902 | 0.95 | True | True | -99.7 | -155 | -8.61 | -134 |

Glitch frequencies (GHz):

- Normal: [3.565, 4.135, 4.14, 4.145, 4.15, 4.155]
- Mild: [2.875, 2.88, 2.885, 2.89, 2.895, 2.9, 2.905, 2.91, 2.915, 2.92, 2.925, 2.93, 2.935, 2.94, 2.945, 2.95, 2.955]
- Moderate: [3.81]
- Severe: [3.28, 3.282, 3.714, 3.716, 3.814, 3.904, 3.906, 3.908, 3.91]

## Circulant symmetry spread per ring distance k (common grid)
mag_spread = max-min of |S(t,t+k)| across t in dB; cplx_rel = rms complex deviation from the ring mean relative to its magnitude (dB, noise-to-signal).
| class | k | n_pairs | mag_spread_db_median | mag_spread_db_p95 | mag_spread_db_max | mag_std_db_median | cplx_rel_db_median | level_db_median |
|---|---|---|---|---|---|---|---|---|
| Normal | 0 | 6 | 0.237 | 1.74 | 5.03 | 0.0856 | -37.6 | -4.08 |
| Normal | 1 | 12 | 0.605 | 1.8 | 2.42 | 0.223 | -25.9 | -43 |
| Normal | 2 | 12 | 1.13 | 10.5 | 20 | 0.367 | -21.3 | -61.4 |
| Normal | 3 | 6 | 0.607 | 2.34 | 2.92 | 0.252 | -28.8 | -55.3 |
| Mild | 0 | 6 | 0.319 | 4.93 | 17.3 | 0.106 | -36 | -4.26 |
| Mild | 1 | 12 | 1.13 | 1.74 | 1.86 | 0.366 | -24.3 | -42.8 |
| Mild | 2 | 12 | 1.63 | 6.24 | 14.3 | 0.567 | -21.8 | -59.2 |
| Mild | 3 | 6 | 1.02 | 4.18 | 5.35 | 0.434 | -24.7 | -56.2 |
| Moderate | 0 | 6 | 0.233 | 2.03 | 14.5 | 0.088 | -36.8 | -4.37 |
| Moderate | 1 | 12 | 0.596 | 2.46 | 2.81 | 0.196 | -29.4 | -42.6 |
| Moderate | 2 | 12 | 1.11 | 5.86 | 19.1 | 0.425 | -23.4 | -59.5 |
| Moderate | 3 | 6 | 0.409 | 2.39 | 3.19 | 0.167 | -31.3 | -56.4 |
| Severe | 0 | 6 | 0.134 | 2.53 | 23.6 | 0.0521 | -35.4 | -4.26 |
| Severe | 1 | 12 | 0.796 | 1.87 | 2.09 | 0.281 | -27 | -43 |
| Severe | 2 | 12 | 1.39 | 11 | 25.2 | 0.47 | -21 | -58.7 |
| Severe | 3 | 6 | 0.839 | 4.31 | 4.61 | 0.361 | -25.9 | -56.1 |

## Port-to-antenna mapping check
All 60 distinct ring orderings (720 permutations mod rotation/reflection) scored by circulant error = mean over f and k>=1 of std_t |S(t,t+k)| (dB). Config mapping port_to_ant = [4, 3, 2, 1, 6, 5] (equivalent under reflection/rotation to 1-2-3-4-5-6, i.e. ports in file order are consecutive around the ring).
| class | config_mapping_error_db | config_rank_of_60 | best_mapping | best_error_db | 2nd_best_error_db | worst_error_db |
|---|---|---|---|---|---|---|
| Normal | 0.46 | 1 | 1-2-3-4-5-6 | 0.46 | 1.71 | 5.97 |
| Mild | 0.47 | 1 | 1-2-3-4-5-6 | 0.47 | 1.84 | 6 |
| Moderate | 0.358 | 1 | 1-2-3-4-5-6 | 0.358 | 1.81 | 6.11 |
| Severe | 0.638 | 1 | 1-2-3-4-5-6 | 0.638 | 2.18 | 6.82 |

## Orientation re-derivation (native grids, per-port min |Sii|, parabolic refine)
Shoulder = power average of |Sii|^2 over 3.38-3.52 GHz.
| class | f_res_mean_MHz | f_res_min | f_res_max | notch_min_dB | notch_max_dB | shoulder_mean_dB | shoulder_spread_dB |
|---|---|---|---|---|---|---|---|
| Normal | 3623.9 | 3622.2 | 3625.3 | -31.107 | -27.454 | -8.9589 | 0.37878 |
| Mild | 3626.7 | 3618.1 | 3633.7 | -38.298 | -34.369 | -8.1868 | 0.38541 |
| Moderate | 3627.7 | 3624.5 | 3630 | -40.72 | -34.908 | -8.2514 | 0.54021 |
| Severe | 3628.8 | 3625.9 | 3634 | -49.163 | -40.37 | -7.8566 | 0.39683 |

## Confound assessment (common grid)
Ring-mode c_k(f) = mean_t S(t,t+k). diff/noise = rms_f|c_k^a - c_k^b| divided by the pooled rms port-to-port deviation (complex). rms_dB_diff = rms_f of dB difference of |c_k|. Project membership is from the model card (sims.csv), not from file headers.
| pair | same_project | k0_diff/noise | k0_rms_dB_diff | k1_diff/noise | k1_rms_dB_diff | k2_diff/noise | k2_rms_dB_diff | k3_diff/noise | k3_rms_dB_diff | k0_shoulder_dB_diff |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal-Mild | False | 1.73 | 0.876 | 1.44 | 0.496 | 1.51 | 3.06 | 3.49 | 1.62 | 0.771 |
| Normal-Moderate | False | 2.58 | 0.968 | 1.05 | 0.554 | 1.39 | 2.91 | 5.08 | 1.8 | 0.709 |
| Normal-Severe | True | 2.85 | 1.42 | 2.45 | 0.77 | 2 | 3.79 | 4.78 | 1.74 | 1.12 |
| Mild-Moderate | True | 0.459 | 0.451 | 0.532 | 0.206 | 0.687 | 0.738 | 0.704 | 0.416 | -0.062 |
| Mild-Severe | False | 0.78 | 0.938 | 0.521 | 0.433 | 0.792 | 1.11 | 1.88 | 0.584 | 0.345 |
| Moderate-Severe | False | 1.22 | 0.562 | 1.04 | 0.399 | 1.04 | 1.31 | 1.96 | 0.313 | 0.407 |

Within-file port-to-port noise (rms over f of std_t in dB):
| class | k0_port_noise_rms_dB | k1_port_noise_rms_dB | k2_port_noise_rms_dB | k3_port_noise_rms_dB |
|---|---|---|---|---|
| Normal | 0.275 | 0.321 | 1.75 | 0.466 |
| Mild | 1.06 | 0.402 | 1.11 | 0.846 |
| Moderate | 0.659 | 0.394 | 1.14 | 0.451 |
| Severe | 0.827 | 0.358 | 1.58 | 0.758 |
