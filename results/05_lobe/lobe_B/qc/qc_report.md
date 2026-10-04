# QC report - track A (A-sphere7-ring6-hfss), code 08a9a53

## Parsed files (native grids)
| class | file | N | F_native | f_min_GHz | f_max_GHz | step_MHz | uniform | option_line | values_per_f |
|---|---|---|---|---|---|---|---|---|---|
| Normal | new_with_slices_Healthy_sliced.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Mild | new_with_slices_Mild_lobe_new.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Moderate | new_with_slices_Moderate_lobe_c3.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Severe | new_with_slices_Severe_lobe_c3.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |

Common grid: 3.200-4.200 GHz, 201 points, step 5.0 MHz. S tensor shape (4, 201, 6, 6) (sims, F, N, N).

## Integrity (native grids)
recip_rel_band_* = |Sij - Sji| / band-rms|Sij| over off-diagonal entries (dB). n_glitch_pts = (f, pair) points with local |Sij - Sji|/|Sij| > -20 dB. Passive = column power sum and largest singular value <= 1 + tol. interp_* = leave-every-other-out spline error / band-rms level (dB).
| class | recip_abs_max | recip_rel_band_max_db | recip_rel_band_p99_db | recip_rel_band_median_db | n_glitch_pts | n_pts | col_power_max | sigma_max | passive | resampled |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 0.000185 | -23.3 | -61.2 | -96 | 0 | 6030 | 0.904 | 0.951 | True | False |
| Mild | 0.00891 | 11.4 | -52.8 | -90.2 | 4 | 6030 | 0.904 | 0.951 | True | False |
| Moderate | 0.000102 | -29.2 | -54.6 | -89.4 | 0 | 6030 | 0.902 | 0.95 | True | False |
| Severe | 0.00115 | -5.59 | -34.7 | -90.8 | 3 | 6030 | 0.901 | 0.95 | True | False |

Glitch frequencies (GHz):

- Normal: []
- Mild: [3.85, 3.855]
- Moderate: []
- Severe: [3.83, 3.835]

## Circulant symmetry spread per ring distance k (common grid)
mag_spread = max-min of |S(t,t+k)| across t in dB; cplx_rel = rms complex deviation from the ring mean relative to its magnitude (dB, noise-to-signal).
| class | k | n_pairs | mag_spread_db_median | mag_spread_db_p95 | mag_spread_db_max | mag_std_db_median | cplx_rel_db_median | level_db_median |
|---|---|---|---|---|---|---|---|---|
| Normal | 0 | 6 | 0.0661 | 0.479 | 0.807 | 0.0221 | -48.9 | -4.61 |
| Normal | 1 | 12 | 0.158 | 0.299 | 0.546 | 0.0557 | -39.5 | -42 |
| Normal | 2 | 12 | 0.282 | 2.26 | 3.47 | 0.0976 | -33 | -60.4 |
| Normal | 3 | 6 | 0.138 | 1.21 | 6.6 | 0.0602 | -40.4 | -55.7 |
| Mild | 0 | 6 | 0.166 | 0.963 | 1.25 | 0.0631 | -39.2 | -4.79 |
| Mild | 1 | 12 | 0.285 | 0.614 | 0.692 | 0.108 | -31.8 | -41.6 |
| Mild | 2 | 12 | 1.12 | 4.72 | 11.4 | 0.42 | -22.6 | -59.4 |
| Mild | 3 | 6 | 0.645 | 1.87 | 21.6 | 0.282 | -25 | -56.1 |
| Moderate | 0 | 6 | 0.193 | 1.03 | 1.22 | 0.0683 | -39.9 | -4.93 |
| Moderate | 1 | 12 | 0.346 | 0.532 | 0.561 | 0.128 | -30 | -41.7 |
| Moderate | 2 | 12 | 0.908 | 2.92 | 3.61 | 0.309 | -23.7 | -59.4 |
| Moderate | 3 | 6 | 0.38 | 1.59 | 7.52 | 0.162 | -29.3 | -56.4 |
| Severe | 0 | 6 | 0.112 | 0.571 | 1.03 | 0.0407 | -42.9 | -4.96 |
| Severe | 1 | 12 | 0.25 | 0.672 | 0.766 | 0.0862 | -35.9 | -41.9 |
| Severe | 2 | 12 | 0.66 | 1.52 | 2.98 | 0.222 | -25.7 | -58.7 |
| Severe | 3 | 6 | 0.174 | 1.36 | 7.9 | 0.0782 | -35.6 | -57.1 |

## Port-to-antenna mapping check
All 60 distinct ring orderings (720 permutations mod rotation/reflection) scored by circulant error = mean over f and k>=1 of std_t |S(t,t+k)| (dB). Config mapping port_to_ant = [4, 3, 2, 1, 6, 5] (equivalent under reflection/rotation to 1-2-3-4-5-6, i.e. ports in file order are consecutive around the ring).
| class | config_mapping_error_db | config_rank_of_60 | best_mapping | best_error_db | 2nd_best_error_db | worst_error_db |
|---|---|---|---|---|---|---|
| Normal | 0.15 | 1 | 1-2-3-4-5-6 | 0.15 | 1.79 | 7.25 |
| Mild | 0.359 | 1 | 1-2-3-4-5-6 | 0.359 | 2.09 | 7.25 |
| Moderate | 0.273 | 1 | 1-2-3-4-5-6 | 0.273 | 2.05 | 7.18 |
| Severe | 0.174 | 1 | 1-2-3-4-5-6 | 0.174 | 1.93 | 6.94 |

## Orientation re-derivation (native grids, per-port min |Sii|, parabolic refine)
Shoulder = power average of |Sii|^2 over 3.38-3.52 GHz.
| class | f_res_mean_MHz | f_res_min | f_res_max | notch_min_dB | notch_max_dB | shoulder_mean_dB | shoulder_spread_dB |
|---|---|---|---|---|---|---|---|
| Normal | 3659.2 | 3658.5 | 3660.4 | -21.236 | -20.862 | -11.138 | 0.11433 |
| Mild | 3656.3 | 3655.3 | 3657.6 | -21.071 | -20.234 | -10.737 | 0.39272 |
| Moderate | 3657.8 | 3655.3 | 3658.5 | -20.953 | -20.441 | -10.521 | 0.39346 |
| Severe | 3657.5 | 3656.6 | 3659.2 | -20.959 | -20.309 | -10.042 | 0.172 |

## Confound assessment (common grid)
Ring-mode c_k(f) = mean_t S(t,t+k). diff/noise = rms_f|c_k^a - c_k^b| divided by the pooled rms port-to-port deviation (complex). rms_dB_diff = rms_f of dB difference of |c_k|. Project membership is from the model card (sims.csv), not from file headers.
| pair | same_project | k0_diff/noise | k0_rms_dB_diff | k1_diff/noise | k1_rms_dB_diff | k2_diff/noise | k2_rms_dB_diff | k3_diff/noise | k3_rms_dB_diff | k0_shoulder_dB_diff |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal-Mild | True | 4.25 | 0.509 | 6.74 | 0.469 | 2.94 | 1.39 | 1.44 | 1.34 | 0.393 |
| Normal-Moderate | True | 5.26 | 0.52 | 6.36 | 0.475 | 3.98 | 1.55 | 4.16 | 1.43 | 0.614 |
| Normal-Severe | True | 12.4 | 0.737 | 13.4 | 0.778 | 7.01 | 2.42 | 7.03 | 1.78 | 1.1 |
| Mild-Moderate | True | 1.25 | 0.181 | 1.24 | 0.205 | 1.02 | 0.459 | 1.14 | 0.902 | 0.221 |
| Mild-Severe | True | 3.67 | 0.404 | 4.98 | 0.708 | 3.1 | 1.74 | 2.15 | 1.38 | 0.703 |
| Moderate-Severe | True | 2.79 | 0.26 | 3.84 | 0.519 | 2.43 | 1.35 | 5.34 | 0.73 | 0.482 |

Within-file port-to-port noise (rms over f of std_t in dB):
| class | k0_port_noise_rms_dB | k1_port_noise_rms_dB | k2_port_noise_rms_dB | k3_port_noise_rms_dB |
|---|---|---|---|---|
| Normal | 0.0612 | 0.0629 | 0.333 | 0.355 |
| Mild | 0.159 | 0.128 | 0.814 | 0.849 |
| Moderate | 0.138 | 0.137 | 0.523 | 0.392 |
| Severe | 0.082 | 0.115 | 0.307 | 0.322 |
