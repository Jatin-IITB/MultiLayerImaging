# Audit of the ratio staging lead (code 2baddee-dirty, 2026-10-02)

> Hash note: '-dirty' comes only from an uncommitted 3-line edit to imaging/report.py by the imaging agent; no file used here was modified. All code used is exactly commit 2baddee.

Data: 9 HFSS solves (v2 + v1 repeats of the same designs; only sweep settings differ, user 2026-10-01). Noise unless stated: typical profile + setup perturbation + per-port gain ±0.5 dB; 150 draws per solve per split (train/test seeds differ). Uncertainties: 95% intervals unless stated. One head geometry throughout.

## 1. How independent are the repeats?
Mesh statistics (tetrahedra) and sweep type are **not recoverable from Touchstone files**: please supply them from HFSS (Solution Data / Profile per design). Indirect evidence below: project, native band, glitch count. Differences: v1 - v2 solve, ± 95% from measurement noise of the two solve means.
| stage | v2 solve | v1 solve | v2 project | v1 project | v1 native band | masked glitch pts v2/v1 | mesh tets | sweep type | R31 v1-v2 dB | R21 v1-v2 dB | R32 v1-v2 dB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Normal | new_Healthy.s6p | brain_sevem_layer_Healthy.s6p | new | new | 2.8-4.2 GHz @5 MHz | 1/6 | not in files - ask user | not in files - ask user | +0.199 ± 0.004 | +0.323 ± 0.008 | -0.123 ± 0.008 |
| Mild | new_MildAD.s6p | Brain_sevem_layer_MildAD.s6p | new | Brain_sevem_layer | 2.8-4.2 GHz @5 MHz | 0/13 | not in files - ask user | not in files - ask user | -0.137 ± 0.005 | +0.169 ± 0.007 | -0.306 ± 0.008 |
| Moderate | new_ModerateAD.s6p | Brain_sevem_layer_ModerateAD.s6p | new | Brain_sevem_layer | 2.8-4.2 GHz @5 MHz | 0/0 | not in files - ask user | not in files - ask user | -0.341 ± 0.005 | -0.240 ± 0.007 | -0.102 ± 0.008 |
| Severe | new_SevereAD.s6p | brain_sevem_layer_SevereAD.s6p | new | new | 3.2-4.2 GHz @2 MHz | 6/18 | not in files - ask user | not in files - ask user | +0.000 ± 0.005 | -0.106 ± 0.006 | +0.106 ± 0.007 |

Solve-to-solve SD (rms of difference/sqrt2) with chi2 95% CI:
| feature | pairs | solve_SD_dB | 95% CI | dof |
|---|---|---|---|---|
| R31 | all 4 pairs | 0.148 | 0.089-0.425 | 4 |
| R31 | Mild+Moderate pairs only | 0.184 | 0.096-1.156 | 2 |
| R21 | all 4 pairs | 0.159 | 0.095-0.456 | 4 |
| R21 | Mild+Moderate pairs only | 0.147 | 0.076-0.923 | 2 |
| R32 | all 4 pairs | 0.128 | 0.077-0.367 | 4 |
| R32 | Mild+Moderate pairs only | 0.161 | 0.084-1.014 | 2 |

Stage gaps. SE = solve SD x sqrt(sum 1/n_solves) for each side (stage means are averages of 2 solves or of 3 stage means); p from t with dof = number of pairs used for the SD.
| feature | SD from | pair | gap_dB | t = gap/SE | p (t, dof=P) | gap/SD range over SD 95% CI |
|---|---|---|---|---|---|---|
| R31 | all 4 pairs | Mild | Severe | 0.277 | 1.87 | 0.134 | 0.65-3.13 |
| R31 | all 4 pairs | Normal | Mild+Moderate+Severe | -1.53 | -12.7 | 0.000225 | 3.60-17.24 |
| R31 | all 4 pairs | Mild | Moderate | -0.212 | -1.43 | 0.225 | 0.50-2.39 |
| R31 | all 4 pairs | Moderate | Severe | 0.489 | 3.31 | 0.0297 | 1.15-5.52 |
| R31 | all 4 pairs | Normal | MCI | -0.0347 | -0.192 | 0.857 | 0.08-0.39 |
| R31 | Mild+Moderate pairs only | Mild | Severe | 0.277 | 1.51 | 0.271 | 0.24-2.90 |
| R31 | Mild+Moderate pairs only | Normal | Mild+Moderate+Severe | -1.53 | -10.2 | 0.00952 | 1.32-15.96 |
| R31 | Mild+Moderate pairs only | Mild | Moderate | -0.212 | -1.15 | 0.368 | 0.18-2.21 |
| R31 | Mild+Moderate pairs only | Moderate | Severe | 0.489 | 2.66 | 0.117 | 0.42-5.11 |
| R31 | Mild+Moderate pairs only | Normal | MCI | -0.0347 | -0.154 | 0.892 | 0.03-0.36 |
| R21 | all 4 pairs | Mild | Severe | 1.28 | 8.06 | 0.00129 | 2.80-13.45 |
| R21 | all 4 pairs | Normal | Mild+Moderate+Severe | 1.51 | 11.6 | 0.000311 | 3.31-15.87 |
| R21 | all 4 pairs | Mild | Moderate | -0.253 | -1.59 | 0.186 | 0.55-2.66 |
| R21 | all 4 pairs | Moderate | Severe | 1.53 | 9.65 | 0.000644 | 3.36-16.11 |
| R21 | all 4 pairs | Normal | MCI | -0.123 | -0.633 | 0.561 | 0.27-1.29 |
| R21 | Mild+Moderate pairs only | Mild | Severe | 1.28 | 8.71 | 0.0129 | 1.39-16.74 |
| R21 | Mild+Moderate pairs only | Normal | Mild+Moderate+Severe | 1.51 | 12.6 | 0.00624 | 1.64-19.75 |
| R21 | Mild+Moderate pairs only | Mild | Moderate | -0.253 | -1.72 | 0.227 | 0.27-3.31 |
| R21 | Mild+Moderate pairs only | Moderate | Severe | 1.53 | 10.4 | 0.00905 | 1.66-20.05 |
| R21 | Mild+Moderate pairs only | Normal | MCI | -0.123 | -0.685 | 0.564 | 0.13-1.61 |
| R32 | all 4 pairs | Mild | Severe | -1 | -7.84 | 0.00143 | 2.73-13.09 |
| R32 | all 4 pairs | Normal | Mild+Moderate+Severe | -3.04 | -29.1 | 8.29e-06 | 8.27-39.68 |
| R32 | all 4 pairs | Mild | Moderate | 0.0413 | 0.323 | 0.763 | 0.11-0.54 |
| R32 | all 4 pairs | Moderate | Severe | -1.04 | -8.16 | 0.00123 | 2.84-13.63 |
| R32 | all 4 pairs | Normal | MCI | 0.0885 | 0.565 | 0.602 | 0.24-1.15 |
| R32 | Mild+Moderate pairs only | Mild | Severe | -1 | -6.21 | 0.025 | 0.99-11.93 |
| R32 | Mild+Moderate pairs only | Normal | Mild+Moderate+Severe | -3.04 | -23.1 | 0.00187 | 3.00-36.17 |
| R32 | Mild+Moderate pairs only | Mild | Moderate | 0.0413 | 0.256 | 0.822 | 0.04-0.49 |
| R32 | Mild+Moderate pairs only | Moderate | Severe | -1.04 | -6.47 | 0.0231 | 1.03-12.42 |
| R32 | Mild+Moderate pairs only | Normal | MCI | 0.0885 | 0.448 | 0.698 | 0.09-1.05 |

## 2. Selection bias: feature selection inside each leave-one-solve-out fold
Candidates per training set: the 4 groups (G_refl, G_coup, G_ratio, G_all) and the top-k (k = 1, 2, 3, 5, 10) of all 89 features ranked by min-pairwise gap^2 / (within + between-solve variance) on the training solves. Chosen by inner leave-one-solve-out balanced accuracy (LDA), ties -> fewer features. The chosen set is refitted on the training solves and tested on the held-out solve.
| scheme | outer folds | nested-selection LOSO bal. acc | folds choosing only ratio features | folds choosing >=1 ratio feature | fixed G_ratio LDA LOSO bal. acc (not nested) |
|---|---|---|---|---|---|
| three | 6 | 1.000 | 6/6 | 6/6 | 1.000 |
| three_merged | 8 | 1.000 | 8/8 | 8/8 | 1.000 |
| binary | 8 | 1.000 | 8/8 | 8/8 | 1.000 |

Per fold:
| scheme | held_out | chosen | features | inner_bal_acc | fold_acc |
|---|---|---|---|---|---|
| three | ../archive/v1_mixed_projects/raw/brain_sevem_layer_Healthy.s6p | top1 | R21 | 1.000 | 1.000 |
| three | new_Healthy.s6p | top1 | R21 | 1.000 | 1.000 |
| three | ../archive/v1_mixed_projects/raw/Brain_sevem_layer_MildAD.s6p | top1 | R32 | 1.000 | 1.000 |
| three | new_MildAD.s6p | top1 | R32 | 1.000 | 1.000 |
| three | ../archive/v1_mixed_projects/raw/brain_sevem_layer_SevereAD.s6p | top1 | R21 | 1.000 | 1.000 |
| three | new_SevereAD.s6p | top1 | R21 | 1.000 | 1.000 |
| three_merged | ../archive/v1_mixed_projects/raw/brain_sevem_layer_Healthy.s6p | top1 | R21 | 1.000 | 1.000 |
| three_merged | new_Healthy.s6p | top1 | R32 | 1.000 | 1.000 |
| three_merged | ../archive/v1_mixed_projects/raw/Brain_sevem_layer_MildAD.s6p | top1 | R32 | 1.000 | 1.000 |
| three_merged | new_MildAD.s6p | top1 | R32 | 1.000 | 1.000 |
| three_merged | ../archive/v1_mixed_projects/raw/Brain_sevem_layer_ModerateAD.s6p | top1 | R21 | 1.000 | 1.000 |
| three_merged | new_ModerateAD.s6p | top1 | R32 | 1.000 | 1.000 |
| three_merged | ../archive/v1_mixed_projects/raw/brain_sevem_layer_SevereAD.s6p | top1 | R32 | 1.000 | 1.000 |
| three_merged | new_SevereAD.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | ../archive/v1_mixed_projects/raw/brain_sevem_layer_Healthy.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | new_Healthy.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | ../archive/v1_mixed_projects/raw/Brain_sevem_layer_MildAD.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | new_MildAD.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | ../archive/v1_mixed_projects/raw/Brain_sevem_layer_ModerateAD.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | new_ModerateAD.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | ../archive/v1_mixed_projects/raw/brain_sevem_layer_SevereAD.s6p | top1 | R32 | 1.000 | 1.000 |
| binary | new_SevereAD.s6p | top1 | R32 | 1.000 | 1.000 |

Frozen rule written to `results/04/frozen_rule.json` (selection run on all 9 solves with the same procedure): staging features = ['R21'], merged = ['R32']. It must be applied unchanged to new solves (`adstage.frozen.apply_rule`).

## 3. Permutation test: stage labels shuffled across solves (antennas of a solve stay together)
All distinct assignments enumerated. Assignments that differ only by renaming equally sized classes give the same problem, so the null is over distinct partitions. 60 draws per solve per split. p = fraction of partitions with balanced accuracy >= observed (observed included).
| scheme | pipeline | solves | label assignments | distinct partitions | observed bal. acc | null median | null max (excl. observed) | exact p | smallest attainable p | top null partitions (nested acc) |
|---|---|---|---|---|---|---|---|---|---|---|
| three | nested selection | 6 | 90 | 15 | 1 | 0.333 | 1 | 0.133 | 0.0667 | Normal(v1)+Normal(v2) / Mild(v1)+Severe(v1) / Mild(v2)+Severe(v2): 1.00; Mild(v2)+Normal(v1) / Normal(v2)+Severe(v2) / Mild(v1)+Severe(v1): 0.49; Mild(v2)+Normal(v2) / Mild(v1)+Severe(v1) / Normal(v1)+Severe(v2): 0.48 |
| three | fixed G_ratio | 6 | 90 | 15 | 1 | 0 | 0.667 | 0.0667 | 0.0667 | n/a |
| three_merged | nested selection | 8 | 420 | 210 | 1 | 0.25 | 0.91 | 0.00476 | 0.00476 | Severe(v1)+Severe(v2) / Mild(v1)+Mild(v2)+Moderate(v2)+Normal(v1) / Moderate(v1)+Normal(v2): 0.91; Normal(v1)+Normal(v2) / Mild(v2)+Moderate(v1)+Severe(v1)+Severe(v2) / Mild(v1)+Moderate(v2): 0.71; Normal(v1)+Severe(v1) / Mild(v1)+Moderate(v1)+Normal(v2)+Severe(v2) / Mild(v2)+Moderate(v2): 0.68 |
| three_merged | fixed G_ratio | 8 | 420 | 210 | 1 | 0.25 | 0.993 | 0.00476 | 0.00476 | n/a |
| binary | nested selection | 8 | 28 | 28 | 1 | 0.366 | 1 | 0.0714 | 0.0357 | Severe(v1)+Severe(v2) / Mild(v1)+Mild(v2)+Moderate(v1)+Moderate(v2)+Normal(v1)+Normal(v2): 1.00; Moderate(v1)+Moderate(v2) / Mild(v1)+Mild(v2)+Normal(v1)+Normal(v2)+Severe(v1)+Severe(v2): 0.59; Moderate(v2)+Severe(v2) / Mild(v1)+Mild(v2)+Moderate(v1)+Normal(v1)+Normal(v2)+Severe(v1): 0.58 |
| binary | fixed G_ratio | 8 | 28 | 28 | 1 | 0.333 | 1 | 0.0714 | 0.0357 | n/a |

## 4. Per-solve values (dB; noise SD = spread over noisy draws of one solve)
| solve | stage | set | R31 | R21 | R32 | R31 noise SD | R21 noise SD | R32 noise SD |
|---|---|---|---|---|---|---|---|---|
| brain_sevem_layer_Healthy.s6p | Normal | v1 | -14.478 | -20.403 | 5.925 | 0.028 | 0.047 | 0.050 |
| new_Healthy.s6p | Normal | v2 | -14.677 | -20.726 | 6.048 | 0.028 | 0.050 | 0.055 |
| new_MCI.s6p | MCI | v2 | -14.612 | -20.687 | 6.075 | 0.023 | 0.044 | 0.046 |
| Brain_sevem_layer_MildAD.s6p | Mild | v1 | -16.197 | -19.311 | 3.115 | 0.032 | 0.042 | 0.049 |
| new_MildAD.s6p | Mild | v2 | -16.060 | -19.481 | 3.421 | 0.031 | 0.042 | 0.048 |
| Brain_sevem_layer_ModerateAD.s6p | Moderate | v1 | -16.511 | -19.769 | 3.259 | 0.032 | 0.046 | 0.053 |
| new_ModerateAD.s6p | Moderate | v2 | -16.169 | -19.529 | 3.360 | 0.032 | 0.046 | 0.049 |
| brain_sevem_layer_SevereAD.s6p | Severe | v1 | -15.850 | -18.169 | 2.319 | 0.030 | 0.037 | 0.045 |
| new_SevereAD.s6p | Severe | v2 | -15.851 | -18.063 | 2.213 | 0.032 | 0.039 | 0.046 |

Monotonicity over Normal -> Mild -> Moderate -> Severe (stage means over solves):
| feature | Normal->Mild dB | Mild->Moderate dB | Moderate->Severe dB | monotone | monotone ignoring steps < 1 solve SD | solve SD dB |
|---|---|---|---|---|---|---|
| R31 | -1.550 | -0.212 | 0.489 | False | False | 0.148 |
| R21 | 1.168 | -0.253 | 1.533 | False | False | 0.159 |
| R32 | -2.718 | 0.041 | -1.044 | False | True | 0.128 |

## 5. Band robustness of the ratios (k = 2 path)
Location of the deepest k = 2 null in 3.6-4.0 GHz per solve: brain_sevem_layer_Healthy.s6p: 3.790; new_Healthy.s6p: 3.825; new_MCI.s6p: 3.850; Brain_sevem_layer_MildAD.s6p: 3.810; new_MildAD.s6p: 3.850; Brain_sevem_layer_ModerateAD.s6p: 3.810; new_ModerateAD.s6p: 3.840; brain_sevem_layer_SevereAD.s6p: 3.815; new_SevereAD.s6p: 3.850.
Each band uses only the solves that cover it (the v1 Severe solve starts at 3.2 GHz, so 2.8-3.2 GHz has one Severe solve and 3 repeat pairs).
| band | feature | pair | solves | pairs | solve SD dB | gap dB | t | p |
|---|---|---|---|---|---|---|---|---|
| 3.2-4.2 (reference) | R31 | Mild | Severe | 9 | 4 | 0.147 | 0.276 | 1.88 | 0.133 |
| 3.2-4.2 (reference) | R31 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.147 | -1.53 | -12.8 | 0.000216 |
| 3.2-4.2 (reference) | R21 | Mild | Severe | 9 | 4 | 0.158 | 1.28 | 8.08 | 0.00128 |
| 3.2-4.2 (reference) | R21 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.158 | 1.51 | 11.7 | 0.000306 |
| 3.2-4.2 (reference) | R32 | Mild | Severe | 9 | 4 | 0.127 | -1 | -7.93 | 0.00137 |
| 3.2-4.2 (reference) | R32 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.127 | -3.04 | -29.5 | 7.91e-06 |
| 3.2-3.6 | R31 | Mild | Severe | 9 | 4 | 0.861 | 0.359 | 0.417 | 0.698 |
| 3.2-3.6 | R31 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.861 | -1.37 | -1.95 | 0.123 |
| 3.2-3.6 | R21 | Mild | Severe | 9 | 4 | 0.863 | 1.35 | 1.56 | 0.193 |
| 3.2-3.6 | R21 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.863 | 1.53 | 2.17 | 0.0961 |
| 3.2-3.6 | R32 | Mild | Severe | 9 | 4 | 0.0574 | -0.991 | -17.3 | 6.59e-05 |
| 3.2-3.6 | R32 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.0574 | -2.9 | -61.8 | 4.09e-07 |
| 3.6-4.2 | R31 | Mild | Severe | 9 | 4 | 0.561 | -0.302 | -0.538 | 0.619 |
| 3.6-4.2 | R31 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.561 | -1.74 | -3.8 | 0.0191 |
| 3.6-4.2 | R21 | Mild | Severe | 9 | 4 | 0.72 | 0.833 | 1.16 | 0.312 |
| 3.6-4.2 | R21 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.72 | 1.82 | 3.1 | 0.0363 |
| 3.6-4.2 | R32 | Mild | Severe | 9 | 4 | 0.543 | -1.13 | -2.09 | 0.105 |
| 3.6-4.2 | R32 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.543 | -3.56 | -8.05 | 0.0013 |
| 3.2-4.2 minus 3.72-3.90 (k2 nulls) | R31 | Mild | Severe | 9 | 4 | 0.368 | 0.285 | 0.776 | 0.481 |
| 3.2-4.2 minus 3.72-3.90 (k2 nulls) | R31 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.368 | -1.52 | -5.07 | 0.00712 |
| 3.2-4.2 minus 3.72-3.90 (k2 nulls) | R21 | Mild | Severe | 9 | 4 | 0.271 | 1.32 | 4.87 | 0.0082 |
| 3.2-4.2 minus 3.72-3.90 (k2 nulls) | R21 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.271 | 1.59 | 7.21 | 0.00196 |
| 3.2-4.2 minus 3.72-3.90 (k2 nulls) | R32 | Mild | Severe | 9 | 4 | 0.144 | -1.04 | -7.21 | 0.00197 |
| 3.2-4.2 minus 3.72-3.90 (k2 nulls) | R32 | Normal | Mild+Moderate+Severe | 9 | 4 | 0.144 | -3.12 | -26.6 | 1.19e-05 |
| 2.8-3.2 (no v1 Severe) | R31 | Mild | Severe | 8 | 3 | 0.251 | 0.465 | 1.51 | 0.227 |
| 2.8-3.2 (no v1 Severe) | R31 | Normal | Mild+Moderate+Severe | 8 | 3 | 0.251 | -0.585 | -2.75 | 0.071 |
| 2.8-3.2 (no v1 Severe) | R21 | Mild | Severe | 8 | 3 | 0.259 | 0.83 | 2.62 | 0.0791 |
| 2.8-3.2 (no v1 Severe) | R21 | Normal | Mild+Moderate+Severe | 8 | 3 | 0.259 | -0.301 | -1.37 | 0.264 |
| 2.8-3.2 (no v1 Severe) | R32 | Mild | Severe | 8 | 3 | 0.0629 | -0.365 | -4.73 | 0.0179 |
| 2.8-3.2 (no v1 Severe) | R32 | Normal | Mild+Moderate+Severe | 8 | 3 | 0.0629 | -0.283 | -5.29 | 0.0132 |

## 6. Hardware realism (ratios only; 3-class = Normal / Mild / Severe)
Band powers (ring mean, 3.2-4.2 GHz): C1 -37.3 dB, C2 -56.8 dB, C3 -52.9 dB. Per-port phase errors cannot change the ratios: they multiply S_ij by e^{j(phi_i+phi_j)} and the ratios use |S|^2 only.
| condition | 3-class LOSO bal. acc (ratios, LDA) | R21 noise SD per measurement dB | R21 Mild|Severe gap dB | R21 gap / per-measurement noise SD | t vs solve SD |
|---|---|---|---|---|---|
| reference: typical, ±0.5 dB gain | 1 | 0.0412 | 1.28 | 31.1 | 8.05 |
| ±2 dB gain + ±10° phase per port | 1 | 0.0432 | 1.29 | 29.8 | 8.21 |
| floor -70 dB (typical) | 1 | 0.0436 | 1.28 | 29.4 | 7.89 |
| floor -60 dB | 1 | 0.142 | 1.27 | 8.93 | 7.8 |
| floor sweep -90.0 dB | 1 | 0.0163 | 1.28 | 78.5 | 7.93 |
| floor sweep -87.5 dB | 1 | 0.017 | 1.28 | 75.2 | 8.04 |
| floor sweep -85.0 dB | 1 | 0.0171 | 1.28 | 75.1 | 8.01 |
| floor sweep -82.5 dB | 1 | 0.0186 | 1.28 | 68.8 | 8.01 |
| floor sweep -80.0 dB | 1 | 0.0194 | 1.28 | 66 | 8.01 |
| floor sweep -77.5 dB | 1 | 0.0236 | 1.28 | 54.3 | 7.95 |
| floor sweep -75.0 dB | 1 | 0.0274 | 1.28 | 46.7 | 8.01 |
| floor sweep -72.5 dB | 1 | 0.0339 | 1.28 | 37.8 | 7.99 |
| floor sweep -70.0 dB | 1 | 0.0432 | 1.29 | 29.8 | 8.15 |
| floor sweep -67.5 dB | 1 | 0.0579 | 1.28 | 22.1 | 7.79 |
| floor sweep -65.0 dB | 1 | 0.076 | 1.28 | 16.8 | 7.84 |
| floor sweep -62.5 dB | 1 | 0.0976 | 1.29 | 13.3 | 8.4 |
| floor sweep -60.0 dB | 1 | 0.14 | 1.25 | 8.95 | 7.89 |
| floor sweep -57.5 dB | 1 | 0.196 | 1.21 | 6.16 | 7.51 |
| floor sweep -55.0 dB | 0.978 | 0.248 | 1.14 | 4.58 | 6.12 |
| floor sweep -52.5 dB | 0.931 | 0.321 | 0.953 | 2.97 | 4.82 |
| floor sweep -50.0 dB | 0.883 | 0.372 | 0.811 | 2.18 | 3.57 |

Highest floor at which the R21 rule still gives >= 0.95 LOSO balanced accuracy and a Mild|Severe gap >= 3x the per-measurement noise SD: **-55.0 dB** (sweep step 2.5 dB, 60 draws/solve).

## Claims
| claim | number | baseline | verdict |
|---|---|---|---|
| R21 separates Mild vs Severe beyond solve noise | gap +1.28 dB; t=8.1 (4 pairs, p=0.0013); t=8.7 (Mild+Moderate pairs only, p=0.013) | solve-to-solve SD (4 pairs / 2 pairs that changed project) | holds |
| R32 separates Mild vs Severe beyond solve noise | gap -1.00 dB; t=-7.8 (4 pairs, p=0.0014); t=-6.2 (Mild+Moderate pairs only, p=0.025) | solve-to-solve SD (4 pairs / 2 pairs that changed project) | holds |
| R21 Normal vs AD beyond solve noise | gap +1.51 dB; t=12.6, p=0.0062 (2-pair SD) | solve SD from Mild+Moderate pairs | holds |
| R31 Normal vs AD beyond solve noise | gap -1.53 dB; t=-10.2, p=0.0095 (2-pair SD) | solve SD from Mild+Moderate pairs | holds |
| Mild vs Moderate separable | R32 gap +0.04 dB; t=0.26 | solve SD (2 pairs) | not supported (no claim made) |
| 3-class staging survives selection inside the folds | nested bal. acc 1.000; ratios-only chosen in 6/6 folds | chance 0.333; non-nested G_ratio 1.000 | holds |
| three result is not achievable by arbitrary solve groupings | exact p = 0.133 (2/15); null max 1.000 | smallest attainable p = 0.0667 | cannot reach p<0.05 with these solves |
| three_merged result is not achievable by arbitrary solve groupings | exact p = 0.005 (1/210); null max 0.910 | smallest attainable p = 0.0048 | holds |
| R21: Mild vs Severe in band 3.2-4.2 (reference) | gap +1.28 dB, solve SD 0.16 dB, t=8.1, p=0.0013 | solve SD in that band (4 pairs) | holds |
| R32: Mild vs Severe in band 3.2-4.2 (reference) | gap -1.00 dB, solve SD 0.13 dB, t=-7.9, p=0.0014 | solve SD in that band (4 pairs) | holds |
| R21: Mild vs Severe in band 3.2-3.6 | gap +1.35 dB, solve SD 0.86 dB, t=1.6, p=0.19 | solve SD in that band (4 pairs) | retracted |
| R32: Mild vs Severe in band 3.2-3.6 | gap -0.99 dB, solve SD 0.06 dB, t=-17.3, p=6.6e-05 | solve SD in that band (4 pairs) | holds |
| R21: Mild vs Severe in band 3.6-4.2 | gap +0.83 dB, solve SD 0.72 dB, t=1.2, p=0.31 | solve SD in that band (4 pairs) | retracted |
| R32: Mild vs Severe in band 3.6-4.2 | gap -1.13 dB, solve SD 0.54 dB, t=-2.1, p=0.1 | solve SD in that band (4 pairs) | weakened |
| R21: Mild vs Severe in band 3.2-4.2 minus 3.72-3.90 (k2 nulls) | gap +1.32 dB, solve SD 0.27 dB, t=4.9, p=0.0082 | solve SD in that band (4 pairs) | holds |
| R32: Mild vs Severe in band 3.2-4.2 minus 3.72-3.90 (k2 nulls) | gap -1.04 dB, solve SD 0.14 dB, t=-7.2, p=0.002 | solve SD in that band (4 pairs) | holds |
| R21: Mild vs Severe in band 2.8-3.2 (no v1 Severe) | gap +0.83 dB, solve SD 0.26 dB, t=2.6, p=0.079 | solve SD in that band (3 pairs) | weakened |
| R32: Mild vs Severe in band 2.8-3.2 (no v1 Severe) | gap -0.36 dB, solve SD 0.06 dB, t=-4.7, p=0.018 | solve SD in that band (3 pairs) | holds |
| staging survives ±2 dB gain + ±10° phase per port | 3-class bal. acc 1.000; R21 gap/noise 29.8 | reference condition, chance 0.333 | holds |
| staging survives floor -60 dB | 3-class bal. acc 1.000; R21 gap/noise 8.9 | reference condition, chance 0.333 | holds |
| minimum instrument floor for the R21 staging rule | <= -55.0 dB | C2 level -56.8 dB | requirement |

## 7. Falsification criteria
Fixed before any new data (frozen rule: `results/04/frozen_rule.json`, applied unchanged):

1. **Normal mesh repeat (Max Delta S 0.01).** Retract if the new-mesh Normal differs from the v2 Normal by more than
   0.5 dB in R21 or R32 (that alone would put the solve SD near the Mild-Severe gap / 2). Weakened if > 0.25 dB.
2. **Mild and Severe re-solved with the finer mesh.** Retract if the frozen 3-class rule classifies either one
   wrongly in > 5% of noisy measurements (typical noise, ±0.5 dB gain), or if R21(Severe) - R21(Mild) < 0.5 dB.
3. **A second head geometry, Mild and Severe** (e.g. head scale 0.95, or skull +1 mm). Retract the staging lead if
   the R21 or R32 ordering flips (Severe not beyond Mild in the same direction), or if the Mild-Severe gap is below
   2x the solve-to-solve SD. The frozen rule failing on the new head is reported as "no generalisation".
4. **Antenna stand-off ±2 mm (Normal and Severe).** Weakened if the R21 shift exceeds half the Mild-Severe gap
   (0.6 dB); retract if it exceeds the full gap.
5. **Second MCI solve.** Not about staging, but: retract any MCI statement if the two MCI solves differ by more than
   their distance to Normal in R21/R32 (expected: they will not separate; no MCI claim is made now).
