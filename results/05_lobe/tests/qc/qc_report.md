# QC report - track A (A-sphere7-ring6-hfss), code 08a9a53

## Parsed files (native grids)
| class | file | N | F_native | f_min_GHz | f_max_GHz | step_MHz | uniform | option_line | values_per_f |
|---|---|---|---|---|---|---|---|---|---|
| Normal | new_with_slices_Healthy_sliced_new.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| MCI | new_with_slices_MCI_lobe_c3.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |
| Mild | new_with_slices_LeftOnly_test_c3.s6p | 6 | 201 | 3.2 | 4.2 | 5 | True | # GHz S MA R 50.000000 | 72 |

Common grid: 3.200-4.200 GHz, 201 points, step 5.0 MHz. S tensor shape (3, 201, 6, 6) (sims, F, N, N).

## Integrity (native grids)
recip_rel_band_* = |Sij - Sji| / band-rms|Sij| over off-diagonal entries (dB). n_glitch_pts = (f, pair) points with local |Sij - Sji|/|Sij| > -20 dB. Passive = column power sum and largest singular value <= 1 + tol. interp_* = leave-every-other-out spline error / band-rms level (dB).
| class | recip_abs_max | recip_rel_band_max_db | recip_rel_band_p99_db | recip_rel_band_median_db | n_glitch_pts | n_pts | col_power_max | sigma_max | passive | resampled |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal | 3.84e-05 | -41.1 | -55.5 | -91.3 | 0 | 6030 | 0.905 | 0.952 | True | False |
| MCI | 1.97e-05 | -42.5 | -58.7 | -92.2 | 0 | 6030 | 0.905 | 0.952 | True | False |
| Mild | 0.000121 | -25.8 | -55.8 | -91.5 | 0 | 6030 | 0.904 | 0.951 | True | False |

Glitch frequencies (GHz):

- Normal: []
- MCI: []
- Mild: []

## Circulant symmetry spread per ring distance k (common grid)
mag_spread = max-min of |S(t,t+k)| across t in dB; cplx_rel = rms complex deviation from the ring mean relative to its magnitude (dB, noise-to-signal).
| class | k | n_pairs | mag_spread_db_median | mag_spread_db_p95 | mag_spread_db_max | mag_std_db_median | cplx_rel_db_median | level_db_median |
|---|---|---|---|---|---|---|---|---|
| Normal | 0 | 6 | 0.116 | 0.645 | 1.09 | 0.0417 | -44.6 | -4.63 |
| Normal | 1 | 12 | 0.225 | 0.307 | 0.648 | 0.0804 | -36.7 | -41.9 |
| Normal | 2 | 12 | 0.337 | 1.59 | 3.95 | 0.111 | -32.9 | -60.4 |
| Normal | 3 | 6 | 0.122 | 1.44 | 6.98 | 0.0516 | -39.7 | -55.6 |
| MCI | 0 | 6 | 0.0776 | 0.546 | 1.14 | 0.025 | -43.5 | -4.65 |
| MCI | 1 | 12 | 0.183 | 0.397 | 0.486 | 0.0643 | -39.7 | -41.8 |
| MCI | 2 | 12 | 0.511 | 3.01 | 3.45 | 0.161 | -30.3 | -60.2 |
| MCI | 3 | 6 | 0.191 | 0.994 | 2.31 | 0.0791 | -39 | -55.7 |
| Mild | 0 | 6 | 0.201 | 1.08 | 1.32 | 0.0731 | -39.1 | -4.76 |
| Mild | 1 | 12 | 0.335 | 0.934 | 1.01 | 0.11 | -30.2 | -41.7 |
| Mild | 2 | 12 | 0.972 | 3.71 | 5.2 | 0.355 | -24.7 | -59.8 |
| Mild | 3 | 6 | 0.447 | 1.87 | 6.36 | 0.193 | -29.7 | -55.8 |

## Port-to-antenna mapping check
All 60 distinct ring orderings (720 permutations mod rotation/reflection) scored by circulant error = mean over f and k>=1 of std_t |S(t,t+k)| (dB). Config mapping port_to_ant = [4, 3, 2, 1, 6, 5] (equivalent under reflection/rotation to 1-2-3-4-5-6, i.e. ports in file order are consecutive around the ring).
| class | config_mapping_error_db | config_rank_of_60 | best_mapping | best_error_db | 2nd_best_error_db | worst_error_db |
|---|---|---|---|---|---|---|
| Normal | 0.146 | 1 | 1-2-3-4-5-6 | 0.146 | 1.8 | 7.26 |
| MCI | 0.17 | 1 | 1-2-3-4-5-6 | 0.17 | 1.84 | 7.26 |
| Mild | 0.302 | 1 | 1-2-3-4-5-6 | 0.302 | 2 | 7.25 |

## Orientation re-derivation (native grids, per-port min |Sii|, parabolic refine)
Shoulder = power average of |Sii|^2 over 3.38-3.52 GHz.
| class | f_res_mean_MHz | f_res_min | f_res_max | notch_min_dB | notch_max_dB | shoulder_mean_dB | shoulder_spread_dB |
|---|---|---|---|---|---|---|---|
| Normal | 3657.7 | 3656.7 | 3659.4 | -21.206 | -20.755 | -11.038 | 0.16249 |
| MCI | 3657 | 3655.5 | 3658 | -21.343 | -20.638 | -11.029 | 0.16665 |
| Mild | 3657 | 3655.6 | 3658.8 | -21.022 | -20.166 | -10.853 | 0.33785 |

## Confound assessment (common grid)
Ring-mode c_k(f) = mean_t S(t,t+k). diff/noise = rms_f|c_k^a - c_k^b| divided by the pooled rms port-to-port deviation (complex). rms_dB_diff = rms_f of dB difference of |c_k|. Project membership is from the model card (sims.csv), not from file headers.
| pair | same_project | k0_diff/noise | k0_rms_dB_diff | k1_diff/noise | k1_rms_dB_diff | k2_diff/noise | k2_rms_dB_diff | k3_diff/noise | k3_rms_dB_diff | k0_shoulder_dB_diff |
|---|---|---|---|---|---|---|---|---|---|---|
| Normal-MCI | True | 0.805 | 0.064 | 0.796 | 0.111 | 0.584 | 0.186 | 0.631 | 0.131 | 0.00954 |
| Normal-Mild | True | 1.81 | 0.223 | 2.81 | 0.253 | 1.94 | 0.801 | 2.47 | 0.637 | 0.177 |
| MCI-Mild | True | 1.51 | 0.191 | 2.3 | 0.242 | 1.64 | 0.728 | 2.85 | 0.641 | 0.167 |

Within-file port-to-port noise (rms over f of std_t in dB):
| class | k0_port_noise_rms_dB | k1_port_noise_rms_dB | k2_port_noise_rms_dB | k3_port_noise_rms_dB |
|---|---|---|---|---|
| Normal | 0.0867 | 0.081 | 0.287 | 0.32 |
| MCI | 0.0879 | 0.0821 | 0.403 | 0.179 |
| Mild | 0.17 | 0.162 | 0.612 | 0.421 |
