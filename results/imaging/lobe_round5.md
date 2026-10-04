# Round 5 (imaging session, POST-HOC): every rotated null, rulers three ways, pair p, reference typicality

Computed by `python imaging/lobe_round5.py --n 100` at code `472b3dd-dirty`; numbers in `results/imaging/lobe_round5.json`. Everything here is post hoc. Frozen files, protocols, predictions and committed verdicts are unchanged.

## 0. What ran

- The procedure pre-registered in `HANDOVER.md` §2 (round 4): the round-3 and round-4 computations with every registered rotated null. Null set: the 9 mirror-symmetric designs + 4 rotated (Null_rot07, Null_rot19, Null_rot31, Null_rot43): **N = 13**. Round 3 and round 4 keep their own files as the 11-null record. The '11 nulls (round 3)' column below repeats the same computations restricted to rot07/rot19, as a regression check.
- This code was committed **before** the new files were loaded (code commit `ef73da6`; registry commit adding the new files `472b3dd`). The generalisations made then: the rank-p denominator of round 3 was hard-coded as 12 (11 nulls), and the bias-corrected FB floor named rot07/rot19; both now use every rotated null.
- Rulers three ways, as in the pre-registration `5966ee4`: **all** (the ruler) = max(one-pass yardstick, largest |value| over the 9 symmetric designs + every rotated null); **without rot19**; **rot19 alone** = max(one-pass yardstick, |rot19|). Only 'all' is the ruler. Bar: ≥ 3× established, 2–3× sensitive, < 2× not determined.

## 1. New files: registry and QC

| stem | sha256_16 | matches_user | passes | final_dS | elements | sets | points | max_sv_squared | passive | worst_amp_nonrecip_dB | at_GHz | ports | path | Sij_dB_there | path_band_level_dB | recip_err_re_band_dB | worst_point_masked | n_masked |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Null_rot07 | cb1176fda2b1e7db | n/a (round 3) | 6 | 0.014650 | 1045101 | lobe_nulls: healthy, whole model rotated 7 deg (kind = null) | 201 | 0.906 | True | 0.49 | 3.860 | 1-4 | T1–T4 | -42.5 | -51.3 | -12.6 | True | 2 |
| Null_rot19 | b79f3a884d1dc926 | n/a (round 3) | 6 | 0.014495 | 939082 | lobe_nulls: healthy, whole model rotated 19 deg (kind = null) | 201 | 0.909 | True | 0.14 | 3.870 | 1-4 | T1–T4 | -50.4 | -51.4 | -26.3 | True | 1 |
| Null_rot31 | 7a7a6697c6c389d2 | True | 6 | 0.016155 | 1078590 | lobe_nulls: healthy, whole model rotated 31 deg (kind = null) | 201 | 0.906 | True | 0.47 | 3.850 | 1-5 | T4–T6 | -88.2 | -57.5 | -55.4 | False | 0 |
| Null_rot43 | 551a05d494d6668c | True | 6 | 0.014859 | 976618 | lobe_nulls: healthy, whole model rotated 43 deg (kind = null) | 201 | 0.909 | True | 0.11 | 3.850 | 3-5 | T2–T6 | -70.0 | -57.1 | -48.8 | False | 0 |

Points masked by the −30 dB reciprocity rule in the rotated nulls:

| file | f_GHz | ports | path | type | Sij_dB | Sji_dB | recip_err_dB | at_fit_freq |
|---|---|---|---|---|---|---|---|---|
| new_with_slices_Null_rot07.s6p | 3.860 | 1-4 | T1–T4 | opposite | -42.5 | -42.0 | -12.6 | False |
| new_with_slices_Null_rot07.s6p | 3.565 | 3-4 | T1–T2 | neighbour | -35.1 | -35.0 | -20.6 | False |
| new_with_slices_Null_rot19.s6p | 3.870 | 1-4 | T1–T4 | opposite | -50.4 | -50.3 | -26.3 | False |

**Result.** sha256 prefixes match the delivery: Null_rot31 True, Null_rot43 True. Passive: Null_rot31 (max σ² 0.906), Null_rot43 (max σ² 0.909). Worst amplitude non-reciprocity: Null_rot31 0.47 dB at 3.850 GHz, ports 1-5 (T4–T6), masked: False; Null_rot43 0.11 dB at 3.850 GHz, ports 3-5 (T2–T6), masked: False. Registered as kind = null, set lobe_nulls; in no training, frozen or stage set.
- Null_rot31's 0.47 dB point is **not** masked. The −30 dB rule tests the absolute error |Sij − Sji| against the path's band level; here it is -55.4 dB. The point sits in a notch: |S| = -88.2 dB against a band level of -57.5 dB, so a 0.47 dB ratio is a tiny absolute difference. It is not at a fit frequency, so the frozen inversion does not see it; band-mean statistics use the reciprocal average of the two values.

## 2. Every rotated null as a target (frozen pipeline, both references)

| null | reference | method | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | LR | LR_ratio | FB | FB_ratio | called | side | frontback | residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Null_rot31 | H7 (Healthy_sliced, 7 passes) | Tikhonov dS | +4.67 | +4.71 | +3.94 | +3.63 | +0.28 | +3.81 | +2.28 | 0.58 | +1.04 | 0.27 | none | none | none | 0.84 |
| Null_rot31 | H7 (Healthy_sliced, 7 passes) | bounded dS | +4.67 | +4.71 | +3.94 | +3.63 | +0.28 | +3.81 | +2.28 | 0.58 | +1.04 | 0.27 | none | none | none | 0.84 |
| Null_rot31 | H7 (Healthy_sliced, 7 passes) | frozen log | +3.80 | +2.83 | +3.12 | +1.72 | -0.01 | +2.01 | +1.98 | 0.50 | +2.08 | 0.46 | none | none | none | 0.84 |
| Null_rot31 | H7 (Healthy_sliced, 7 passes) | frozen bounded log | +3.80 | +2.82 | +3.13 | +1.72 | +0.00 | +2.01 | +1.97 | 0.50 | +2.08 | 0.46 | none | none | none | 0.84 |
| Null_rot31 | H7 (Healthy_sliced, 7 passes) | whitened log (POST-HOC) | +2.42 | +2.91 | +2.01 | +1.77 | -0.85 | +1.80 | +1.98 | 0.64 | +0.65 | 0.13 | n/a (no frozen thresholds) | n/a | n/a | 0.89 |
| Null_rot31 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | +2.52 | +2.71 | +1.23 | +1.48 | -2.12 | +0.82 | +2.62 | 0.74 | +1.04 | 0.27 | none | none | none | 0.93 |
| Null_rot31 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | +2.58 | +2.58 | +1.36 | +0.75 | +0.00 | +0.20 | +1.87 | 0.53 | +1.83 | 0.47 | none | none | none | 0.94 |
| Null_rot31 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | +2.23 | +1.64 | +1.15 | +0.34 | -1.72 | -0.08 | +2.29 | 0.65 | +1.89 | 0.46 | none | none | none | 0.93 |
| Null_rot31 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | +2.16 | +1.41 | +1.22 | +0.00 | +0.00 | +0.00 | +1.31 | 0.37 | +2.16 | 0.52 | none | none | none | 0.94 |
| Null_rot31 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log (POST-HOC) | +1.22 | +1.69 | +0.21 | +0.58 | -2.15 | +0.15 | +1.95 | 0.65 | +0.65 | 0.13 | n/a (no frozen thresholds) | n/a | n/a | 0.95 |
| Null_rot43 | H7 (Healthy_sliced, 7 passes) | Tikhonov dS | +3.53 | +4.08 | +2.93 | +2.74 | +1.02 | +3.98 | +1.01 | 0.26 | +0.78 | 0.20 | none | none | none | 0.83 |
| Null_rot43 | H7 (Healthy_sliced, 7 passes) | bounded dS | +3.53 | +4.08 | +2.93 | +2.74 | +1.02 | +3.98 | +1.01 | 0.26 | +0.78 | 0.20 | none | none | none | 0.83 |
| Null_rot43 | H7 (Healthy_sliced, 7 passes) | frozen log | +2.24 | +1.71 | +2.01 | +1.16 | +0.47 | +1.40 | +0.92 | 0.23 | +1.08 | 0.24 | none | none | none | 0.78 |
| Null_rot43 | H7 (Healthy_sliced, 7 passes) | frozen bounded log | +2.24 | +1.71 | +2.01 | +1.16 | +0.47 | +1.40 | +0.92 | 0.23 | +1.08 | 0.24 | none | none | none | 0.78 |
| Null_rot43 | H7 (Healthy_sliced, 7 passes) | whitened log (POST-HOC) | +1.20 | +2.04 | +0.61 | +1.75 | -0.63 | +1.25 | +1.01 | 0.33 | -0.55 | 0.11 | n/a (no frozen thresholds) | n/a | n/a | 0.85 |
| Null_rot43 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | +1.36 | +2.10 | +0.21 | +0.52 | -1.40 | +0.99 | +1.36 | 0.38 | +0.84 | 0.22 | none | none | none | 0.89 |
| Null_rot43 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | +1.40 | +2.02 | +0.29 | +0.04 | +0.00 | +0.58 | +0.87 | 0.25 | +1.36 | 0.35 | none | none | none | 0.89 |
| Null_rot43 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | +0.80 | +0.54 | +0.05 | -0.21 | -1.18 | -0.61 | +1.19 | 0.34 | +1.01 | 0.24 | none | none | none | 0.84 |
| Null_rot43 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | +0.49 | +0.41 | +0.00 | +0.00 | +0.00 | +0.00 | +0.21 | 0.06 | +0.49 | 0.12 | none | none | none | 0.85 |
| Null_rot43 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log (POST-HOC) | +0.12 | +0.83 | -1.20 | +0.61 | -1.92 | -0.30 | +0.93 | 0.31 | -0.49 | 0.10 | n/a (no frozen thresholds) | n/a | n/a | 0.87 |

Reading rule of the Test_B protocol applied to each null:

| null | affected | possible | side | frontback | statement |
|---|---|---|---|---|---|
| Null_rot07 | none | none | none | none | No sector above the frozen T_abs (13.81) in any accepted reference: no lobe is read as affected. Data-level size vs the largest one-pass mesh difference: H7 0.77× (not separable), H6 0.46× (not separable). |
| Null_rot19 | none | none | none | none | Fit rejected in both references (residual > 1.5× the largest residual of the known cortical designs): the sector model does not explain Null_rot19, so no lobe reading is stated. Data-level size vs the largest one-pass mesh difference: H7 1.20× (not separable), H6 0.89× (not separable). |
| Null_rot31 | none | none | none | none | No sector above the frozen T_abs (13.81) in any accepted reference: no lobe is read as affected. Data-level size vs the largest one-pass mesh difference: H7 1.05× (not separable), H6 0.71× (not separable). |
| Null_rot43 | none | none | none | none | No sector above the frozen T_abs (13.81) in any accepted reference: no lobe is read as affected. Data-level size vs the largest one-pass mesh difference: H7 1.10× (not separable), H6 0.78× (not separable). |

**Result (all 4 rotated nulls).** Largest sector value 4.75 (frozen T_abs 13.81). LR and FB at most 0.74× and 0.73× the protocol rulers. Frozen calls in any method and reference: 0.

## 3. 'LeftOnly and RightOnly beyond all nulls' with N = 13

LR_anti = ½[LR(X) − LR(mirror X)] for every null and both mirror designs:

| reference | method | yardstick | null9_max | null9_rms | rot07 | rot19 | rot31 | rot43 | null13_max | null13_rms | LeftOnly ratio (9) | LeftOnly ratio (13) | LeftOnly rank p (13) | RightOnly ratio (9) | RightOnly ratio (13) | RightOnly rank p (13) | Test ratio (9) | Test ratio (13) | Test rank p (13) | both mirror designs beyond all 13 | rotated nulls within old 9-null envelope |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | Tikhonov dS | 2.14 | 4.07 | 1.62 | 1.41 | -0.96 | 1.40 | -0.01 | 4.07 | 1.48 | 1.93 | 1.93 | 0.07 | 2.50 | 2.50 | 0.07 | 0.04 | 0.04 | 0.86 | True | True |
| H7 | frozen log | 2.38 | 3.72 | 1.43 | 0.87 | -0.87 | 1.18 | -0.05 | 3.72 | 1.28 | 2.35 | 2.35 | 0.07 | 2.98 | 2.98 | 0.07 | 0.12 | 0.12 | 0.79 | True | True |
| H7 | whitened log | 1.98 | 3.14 | 1.21 | 0.58 | -0.68 | 1.01 | -0.13 | 3.14 | 1.07 | 2.76 | 2.76 | 0.07 | 3.37 | 3.37 | 0.07 | 0.04 | 0.04 | 0.93 | True | True |
| H6 | Tikhonov dS | 2.12 | 4.04 | 1.60 | 1.39 | -0.93 | 1.38 | -0.01 | 4.04 | 1.47 | 1.94 | 1.94 | 0.07 | 2.51 | 2.51 | 0.07 | 0.05 | 0.05 | 0.86 | True | True |
| H6 | frozen log | 2.38 | 3.76 | 1.45 | 0.88 | -0.88 | 1.18 | -0.08 | 3.76 | 1.30 | 2.35 | 2.35 | 0.07 | 2.98 | 2.98 | 0.07 | 0.11 | 0.11 | 0.79 | True | True |
| H6 | whitened log | 1.97 | 3.17 | 1.22 | 0.59 | -0.68 | 1.00 | -0.16 | 3.17 | 1.08 | 2.77 | 2.77 | 0.07 | 3.38 | 3.38 | 0.07 | 0.03 | 0.03 | 1.00 | True | True |

Ratios to the LR_anti ruler, three ways (plus the round-3 11-null ruler):

| reference | method | yardstick | ruler (11 nulls (round 3)) | LeftOnly (11 nulls (round 3)) | RightOnly (11 nulls (round 3)) | Test (11 nulls (round 3)) | ruler (all) | LeftOnly (all) | RightOnly (all) | Test (all) | ruler (without rot19) | LeftOnly (without rot19) | RightOnly (without rot19) | Test (without rot19) | ruler (rot19 alone) | LeftOnly (rot19 alone) | RightOnly (rot19 alone) | Test (rot19 alone) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | Tikhonov dS | 2.14 | 4.07 | 1.93 | 2.50 | 0.04 | 4.07 | 1.93 | 2.50 | 0.04 | 4.07 | 1.93 | 2.50 | 0.04 | 2.14 | 3.67 | 4.75 | 0.08 |
| H7 | frozen log | 2.38 | 3.72 | 2.35 | 2.98 | 0.12 | 3.72 | 2.35 | 2.98 | 0.12 | 3.72 | 2.35 | 2.98 | 0.12 | 2.38 | 3.68 | 4.67 | 0.18 |
| H7 | whitened log | 1.98 | 3.14 | 2.76 | 3.37 | 0.04 | 3.14 | 2.76 | 3.37 | 0.04 | 3.14 | 2.76 | 3.37 | 0.04 | 1.98 | 4.39 | 5.35 | 0.07 |
| H6 | Tikhonov dS | 2.12 | 4.04 | 1.94 | 2.51 | 0.05 | 4.04 | 1.94 | 2.51 | 0.05 | 4.04 | 1.94 | 2.51 | 0.05 | 2.12 | 3.70 | 4.78 | 0.09 |
| H6 | frozen log | 2.38 | 3.76 | 2.35 | 2.98 | 0.11 | 3.76 | 2.35 | 2.98 | 0.11 | 3.76 | 2.35 | 2.98 | 0.11 | 2.38 | 3.71 | 4.72 | 0.17 |
| H6 | whitened log | 1.97 | 3.17 | 2.77 | 3.38 | 0.03 | 3.17 | 2.77 | 3.38 | 0.03 | 3.17 | 2.77 | 3.38 | 0.03 | 1.97 | 4.44 | 5.43 | 0.05 |

Rank p of each mirror design and of the pair:

| reference | method | nulls | N | p_Left | p_Right | product | exact_exchangeable | both_beyond | predicted_signs |
|---|---|---|---|---|---|---|---|---|---|
| H7 | Tikhonov dS | 11 nulls (round 3) | 11 | 0.0833 | 0.0833 | 0.0069 | 0.0128 | True | True |
| H7 | Tikhonov dS | all | 13 | 0.0714 | 0.0714 | 0.0051 | 0.0095 | True | True |
| H7 | Tikhonov dS | without rot19 | 12 | 0.0769 | 0.0769 | 0.0059 | 0.0110 | True | True |
| H7 | frozen log | 11 nulls (round 3) | 11 | 0.0833 | 0.0833 | 0.0069 | 0.0128 | True | True |
| H7 | frozen log | all | 13 | 0.0714 | 0.0714 | 0.0051 | 0.0095 | True | True |
| H7 | frozen log | without rot19 | 12 | 0.0769 | 0.0769 | 0.0059 | 0.0110 | True | True |
| H7 | whitened log | 11 nulls (round 3) | 11 | 0.0833 | 0.0833 | 0.0069 | 0.0128 | True | True |
| H7 | whitened log | all | 13 | 0.0714 | 0.0714 | 0.0051 | 0.0095 | True | True |
| H7 | whitened log | without rot19 | 12 | 0.0769 | 0.0769 | 0.0059 | 0.0110 | True | True |
| H6 | Tikhonov dS | 11 nulls (round 3) | 11 | 0.0833 | 0.0833 | 0.0069 | 0.0128 | True | True |
| H6 | Tikhonov dS | all | 13 | 0.0714 | 0.0714 | 0.0051 | 0.0095 | True | True |
| H6 | Tikhonov dS | without rot19 | 12 | 0.0769 | 0.0769 | 0.0059 | 0.0110 | True | True |
| H6 | frozen log | 11 nulls (round 3) | 11 | 0.0833 | 0.0833 | 0.0069 | 0.0128 | True | True |
| H6 | frozen log | all | 13 | 0.0714 | 0.0714 | 0.0051 | 0.0095 | True | True |
| H6 | frozen log | without rot19 | 12 | 0.0769 | 0.0769 | 0.0059 | 0.0110 | True | True |
| H6 | whitened log | 11 nulls (round 3) | 11 | 0.0833 | 0.0833 | 0.0069 | 0.0128 | True | True |
| H6 | whitened log | all | 13 | 0.0714 | 0.0714 | 0.0051 | 0.0095 | True | True |
| H6 | whitened log | without rot19 | 12 | 0.0769 | 0.0769 | 0.0059 | 0.0110 | True | True |

**Result.** Both mirror designs beyond all 13 nulls in every method × reference: **True**. Each rank p = 1/14 = 0.0714. LR_anti ratio to the all-null ruler: LeftOnly 1.93–2.77×, RightOnly 2.50–3.38× over methods and references.
**Pair p, corrected.** Rounds 2–3 multiplied the two rank p's ('if independent'): with 11 nulls 0.0069, now 0.0051. That is the wrong formula even for independent meshes: both values are compared with the same null maximum, so the two events are positively dependent. For two values that both exceed the same N nulls, with all N + 2 exchangeable, p = 2/((N + 1)(N + 2)): with 11 nulls 0.0128, with 13 0.0095 (two-sided in |LR_anti|; the predicted opposite signs hold: True). Round 3's 'pair p ≈ 0.007' understated p by 1.85×.

## 4. Do the meshes' asymmetries behave as independent draws? (four rotated samples)

LR_anti of the healthy meshes (one geometry, meshed several times), with the criterion fixed before the new files were loaded: supported if the values take both signs with |mean| < SD and q = rms(rot − H6) / (√2 × SD of all nulls) ≥ 0.5; contradicted if all share a sign with |mean| > SD, or q < 0.5.

| reference | method | H6 | H7 | rot07 | rot19 | rot31 | rot43 | healthy_mean | healthy_SD | n_positive | SD_all_nulls | q_rot_vs_H6 | H7_vs_H6 | independence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | Tikhonov dS | -1.15 | -0.86 | +1.41 | -0.96 | +1.40 | -0.01 | -0.03 | 1.18 | 2/6 | 1.43 | 0.94 | 0.14 | supported |
| H7 | frozen log | -1.06 | -0.88 | +0.87 | -0.87 | +1.18 | -0.05 | -0.13 | 0.97 | 2/6 | 1.21 | 0.91 | 0.11 | supported |
| H7 | whitened log | -0.79 | -0.84 | +0.58 | -0.68 | +1.01 | -0.13 | -0.14 | 0.78 | 2/6 | 1.01 | 0.83 | 0.03 | supported |
| H6 | Tikhonov dS | -1.14 | -0.85 | +1.39 | -0.93 | +1.38 | -0.01 | -0.03 | 1.16 | 2/6 | 1.42 | 0.93 | 0.14 | supported |
| H6 | frozen log | -1.09 | -0.90 | +0.88 | -0.88 | +1.18 | -0.08 | -0.15 | 0.98 | 2/6 | 1.22 | 0.92 | 0.11 | supported |
| H6 | whitened log | -0.81 | -0.87 | +0.59 | -0.68 | +1.00 | -0.16 | -0.15 | 0.79 | 2/6 | 1.02 | 0.83 | 0.04 | supported |

**Result.** Independence supported in 6 of 6 method × reference cases. q (rotated vs H6) 0.83–0.94; the same-lineage pair H7 vs H6 0.03–0.14 in the same units. This tests rotation, not mirroring: a mesher that reproduced a mirrored mesh would still pass it.

## 5. Rulers three ways

Sector, LR and FB rulers (primary method), as in round 3, for each null set:

| reference | rulers | ruler S1 Fr | ruler S2 TL | ruler S3 PL | ruler S4 Oc | ruler S5 PR | ruler S6 TR | ruler_LR | ruler_FB | rot07 max sector | rot19 max sector | rot31 max sector | rot43 max sector |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | 11 nulls (round 3) | 3.59 | 4.19 | 4.75 | 3.39 | 5.15 | 5.15 | 3.92 | 3.88 | 4.75 | 3.45 | 4.71 | 4.08 |
| H7 | all | 4.67 | 4.71 | 4.75 | 3.63 | 5.15 | 5.15 | 3.92 | 3.88 | 4.75 | 3.45 | 4.71 | 4.08 |
| H7 | without rot19 | 4.67 | 4.71 | 4.75 | 3.63 | 5.15 | 5.15 | 3.92 | 3.88 | 4.75 | 3.45 | 4.71 | 4.08 |
| H7 | rot19 alone | 3.14 | 4.19 | 2.98 | 2.47 | 5.15 | 5.15 | 2.18 | 0.67 | 4.75 | 3.45 | 4.71 | 4.08 |
| H6 | 11 nulls (round 3) | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 3.54 | 3.85 | 2.02 | 0.40 | 2.71 | 2.10 |
| H6 | all | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 3.54 | 3.85 | 2.02 | 0.40 | 2.71 | 2.10 |
| H6 | without rot19 | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 3.54 | 3.85 | 2.02 | 0.40 | 2.71 | 2.10 |
| H6 | rot19 alone | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 2.14 | 0.71 | 2.02 | 0.40 | 2.71 | 2.10 |

Ratios of the mirror and blind designs to those rulers:

| reference | rulers | Test S2 TL ratio | Test S5 PR ratio | Test LR ratio | RightOnly S5 PR ratio | RightOnly S6 TR ratio | RightOnly LR ratio | LeftOnly S2 TL ratio | LeftOnly S3 PL ratio | LeftOnly LR ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| H7 | 11 nulls (round 3) | 3.50 | 2.55 | 0.19 | 3.18 | 4.34 | 2.50 | 3.13 | 3.16 | 2.16 |
| H7 | all | 3.11 | 2.55 | 0.19 | 3.18 | 4.34 | 2.50 | 2.78 | 3.16 | 2.16 |
| H7 | without rot19 | 3.11 | 2.55 | 0.19 | 3.18 | 4.34 | 2.50 | 2.78 | 3.16 | 2.16 |
| H7 | rot19 alone | 3.50 | 2.55 | 0.35 | 3.18 | 4.34 | 4.50 | 3.13 | 5.03 | 3.88 |
| H6 | 11 nulls (round 3) | 3.03 | 2.10 | 0.32 | 2.74 | 3.75 | 2.67 | 2.65 | 4.55 | 2.49 |
| H6 | all | 3.03 | 2.10 | 0.32 | 2.74 | 3.75 | 2.67 | 2.65 | 4.55 | 2.49 |
| H6 | without rot19 | 3.03 | 2.10 | 0.32 | 2.74 | 3.75 | 2.67 | 2.65 | 4.55 | 2.49 |
| H6 | rot19 alone | 3.03 | 2.10 | 0.53 | 2.74 | 3.75 | 4.41 | 2.65 | 4.55 | 4.12 |

Cross-ratio phase counts (18 distinct statistics, LeftOnly ≥ 3× the floor; null files ≥ 3× leave-one-out):

| view | nulls | LeftOnly ≥3× rms | LeftOnly ≥3× max | RightOnly ≥3× rms | RightOnly ≥3× max | Test ≥3× rms | Test ≥3× max | null files ≥3× rms (leave-one-out), max over files | per null file |
|---|---|---|---|---|---|---|---|---|---|
| band mean 3.2-4.2 GHz | 9 nulls | 12 | 3 | 7 | 3 | 0 | 0 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0 |
| band mean 3.2-4.2 GHz | 11 nulls (round 3) | 12 | 3 | 7 | 2 | 0 | 0 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0 |
| band mean 3.2-4.2 GHz | all | 12 | 2 | 7 | 2 | 0 | 0 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0, Null_rot31 0, Null_rot43 0 |
| band mean 3.2-4.2 GHz | without rot19 | 12 | 2 | 7 | 2 | 0 | 0 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot31 0, Null_rot43 0 |
| band mean 3.2-4.2 GHz | rot19 alone | 12 | 12 | 9 | 9 | 0 | 0 | n/a |  |
| 3.4 GHz | 9 nulls | 9 | 4 | 8 | 4 | 10 | 5 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0 |
| 3.4 GHz | 11 nulls (round 3) | 9 | 3 | 8 | 2 | 10 | 4 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0 |
| 3.4 GHz | all | 9 | 2 | 8 | 2 | 9 | 4 | 1 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0, Null_rot31 1, Null_rot43 0 |
| 3.4 GHz | without rot19 | 9 | 2 | 8 | 2 | 9 | 4 | 1 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot31 1, Null_rot43 0 |
| 3.4 GHz | rot19 alone | 9 | 9 | 8 | 8 | 10 | 10 | n/a |  |
| band mean 3.30-3.65 GHz | 9 nulls | 12 | 7 | 9 | 7 | 7 | 3 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0 |
| band mean 3.30-3.65 GHz | 11 nulls (round 3) | 11 | 3 | 7 | 3 | 7 | 2 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0 |
| band mean 3.30-3.65 GHz | all | 10 | 2 | 7 | 3 | 7 | 2 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0, Null_rot31 0, Null_rot43 0 |
| band mean 3.30-3.65 GHz | without rot19 | 11 | 2 | 7 | 3 | 7 | 2 | 1 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot31 1, Null_rot43 0 |
| band mean 3.30-3.65 GHz | rot19 alone | 5 | 5 | 6 | 6 | 5 | 5 | n/a |  |

Bias-corrected Moderate front/back (round-2 B24):

| set | method | FB_rot07 | FB_rot19 | FB_rot31 | FB_rot43 | corrected | ratio_old | ratio_new | ratio (11 nulls (round 3)) | ratio (all) | ratio (without rot19) | ratio (rot19 alone) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lobe_A | Tikhonov dS | +2.81 | +0.59 | +1.04 | +0.84 | +6.31 | 1.38 | 1.38 | 1.38 | 1.38 | 1.38 | 8.90 |
| lobe_A | frozen log | +3.01 | -0.06 | +1.89 | +1.01 | +6.41 | 1.58 | 1.58 | 1.58 | 1.58 | 1.58 | 7.00 |
| lobe_A | whitened log | +2.30 | +0.06 | +0.65 | -0.49 | +6.72 | 1.88 | 1.88 | 1.88 | 1.88 | 1.88 | 3.89 |
| lobe_B | Tikhonov dS | +2.83 | +0.51 | +1.04 | +0.78 | +7.42 | 3.21 | 2.61 | 2.61 | 2.61 | 2.61 | 10.29 |
| lobe_B | frozen log | +3.21 | +0.18 | +2.08 | +1.08 | +7.16 | 3.98 | 2.23 | 2.23 | 2.23 | 2.23 | 7.13 |
| lobe_B | whitened log | +2.39 | +0.14 | +0.65 | -0.55 | +6.93 | 3.97 | 2.80 | 2.80 | 2.80 | 2.80 | 5.04 |

## 6. Detection re-graded (0.3b)

Per design: best and worst affected sector over the sector ruler, and the largest sector value over the max-sector ruler (max(largest one-pass yardstick of a sector, largest |sector| of a no-change null)):

| reference | variant | design | affected | best_affected | worst_affected | max_sector | max_sector_ruler | max_sector_ratio |
|---|---|---|---|---|---|---|---|---|
| H7 | all | Mild_lobe | S2 S3 S5 S6 | 4.29 | 3.15 | 21.66 | 5.15 | 4.20 |
| H7 | all | Mild_lobe_new | S2 S3 S5 S6 | 3.40 | 2.66 | 16.50 | 5.15 | 3.20 |
| H7 | all | Moderate_lobe | S1 S2 S3 S5 S6 | 4.06 | 3.20 | 20.92 | 5.15 | 4.06 |
| H7 | all | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | 3.44 | 2.57 | 16.40 | 5.15 | 3.18 |
| H7 | all | Severe_lobe | S1 S2 S3 S4 S5 S6 | 4.62 | 3.44 | 21.06 | 5.15 | 4.09 |
| H7 | all | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | 4.11 | 2.88 | 18.53 | 5.15 | 3.60 |
| H7 | all | LeftOnly_test_c3 | S2 S3 | 3.16 | 2.78 | 15.02 | 5.15 | 2.92 |
| H7 | all | RightOnly_test | S5 S6 | 4.34 | 3.18 | 22.34 | 5.15 | 4.34 |
| H7 | all | Test_B | S2 S5 | 3.11 | 2.55 | 14.67 | 5.15 | 2.85 |
| H7 | without rot19 | Mild_lobe | S2 S3 S5 S6 | 4.29 | 3.15 | 21.66 | 5.15 | 4.20 |
| H7 | without rot19 | Mild_lobe_new | S2 S3 S5 S6 | 3.40 | 2.66 | 16.50 | 5.15 | 3.20 |
| H7 | without rot19 | Moderate_lobe | S1 S2 S3 S5 S6 | 4.06 | 3.20 | 20.92 | 5.15 | 4.06 |
| H7 | without rot19 | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | 3.44 | 2.57 | 16.40 | 5.15 | 3.18 |
| H7 | without rot19 | Severe_lobe | S1 S2 S3 S4 S5 S6 | 4.62 | 3.44 | 21.06 | 5.15 | 4.09 |
| H7 | without rot19 | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | 4.11 | 2.88 | 18.53 | 5.15 | 3.60 |
| H7 | without rot19 | LeftOnly_test_c3 | S2 S3 | 3.16 | 2.78 | 15.02 | 5.15 | 2.92 |
| H7 | without rot19 | RightOnly_test | S5 S6 | 4.34 | 3.18 | 22.34 | 5.15 | 4.34 |
| H7 | without rot19 | Test_B | S2 S5 | 3.11 | 2.55 | 14.67 | 5.15 | 2.85 |
| H6 | all | Mild_lobe | S2 S3 S5 S6 | 5.50 | 2.71 | 18.64 | 5.15 | 3.62 |
| H6 | all | Mild_lobe_new | S2 S3 S5 S6 | 4.60 | 2.21 | 14.04 | 5.15 | 2.72 |
| H6 | all | Moderate_lobe | S1 S2 S3 S5 S6 | 5.16 | 3.12 | 17.91 | 5.15 | 3.48 |
| H6 | all | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | 4.41 | 2.18 | 13.87 | 5.15 | 2.69 |
| H6 | all | Severe_lobe | S1 S2 S3 S4 S5 S6 | 6.32 | 3.00 | 18.42 | 5.15 | 3.57 |
| H6 | all | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | 5.76 | 2.44 | 16.34 | 5.15 | 3.17 |
| H6 | all | LeftOnly_test_c3 | S2 S3 | 4.55 | 2.65 | 12.28 | 5.15 | 2.38 |
| H6 | all | RightOnly_test | S5 S6 | 3.75 | 2.74 | 19.35 | 5.15 | 3.75 |
| H6 | all | Test_B | S2 S5 | 3.03 | 2.10 | 12.71 | 5.15 | 2.47 |
| H6 | without rot19 | Mild_lobe | S2 S3 S5 S6 | 5.50 | 2.71 | 18.64 | 5.15 | 3.62 |
| H6 | without rot19 | Mild_lobe_new | S2 S3 S5 S6 | 4.60 | 2.21 | 14.04 | 5.15 | 2.72 |
| H6 | without rot19 | Moderate_lobe | S1 S2 S3 S5 S6 | 5.16 | 3.12 | 17.91 | 5.15 | 3.48 |
| H6 | without rot19 | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | 4.41 | 2.18 | 13.87 | 5.15 | 2.69 |
| H6 | without rot19 | Severe_lobe | S1 S2 S3 S4 S5 S6 | 6.32 | 3.00 | 18.42 | 5.15 | 3.57 |
| H6 | without rot19 | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | 5.76 | 2.44 | 16.34 | 5.15 | 3.17 |
| H6 | without rot19 | LeftOnly_test_c3 | S2 S3 | 4.55 | 2.65 | 12.28 | 5.15 | 2.38 |
| H6 | without rot19 | RightOnly_test | S5 S6 | 3.75 | 2.74 | 19.35 | 5.15 | 3.75 |
| H6 | without rot19 | Test_B | S2 S5 | 3.03 | 2.10 | 12.71 | 5.15 | 2.47 |

Tier counts (design × reference):

| variant | best affected established | best affected sensitive | best affected not determined | max sector established | max sector sensitive | max sector not determined | weakest_best | weakest_max_sector |
|---|---|---|---|---|---|---|---|---|
| 11 nulls (round 3) | 18 | 0 | 0 | 12 | 6 | 0 | 3.03 (Test_B, H6) | 2.38 (LeftOnly_test_c3, H6) |
| all | 18 | 0 | 0 | 12 | 6 | 0 | 3.03 (Test_B, H6) | 2.38 (LeftOnly_test_c3, H6) |
| without rot19 | 18 | 0 | 0 | 12 | 6 | 0 | 3.03 (Test_B, H6) | 2.38 (LeftOnly_test_c3, H6) |
| rot19 alone | 18 | 0 | 0 | 12 | 6 | 0 | 3.03 (Test_B, H6) | 2.38 (LeftOnly_test_c3, H6) |

MCI against rulers built without MCI (claim: < 2× = nothing separable; < 1 = nothing beyond):

| reference | variant | max_sector_ratio | LR_ratio | FB_ratio |
|---|---|---|---|---|
| H7 | 11 nulls (round 3) | 1.37 | 0.26 | 0.22 |
| H7 | all | 0.93 | 0.26 | 0.22 |
| H7 | without rot19 | 0.93 | 0.26 | 0.22 |
| H7 | rot19 alone | 1.37 | 0.47 | 1.28 |
| H6 | 11 nulls (round 3) | 0.50 | 0.39 | 0.22 |
| H6 | all | 0.50 | 0.39 | 0.22 |
| H6 | without rot19 | 0.50 | 0.39 | 0.22 |
| H6 | rot19 alone | 0.50 | 0.64 | 1.18 |

Sector-shaped part of the data (explained norm of the primary fit, round 4 §1), smallest target over largest null:

| reference | nulls | largest_null_explained | smallest_target_explained | ratio |
|---|---|---|---|---|
| H7 | all | 5.59 | 12.76 | 2.28 |
| H7 | without rot19 | 5.59 | 12.76 | 2.28 |
| H7 | rot19 alone | 4.34 | 12.76 | 2.94 |
| H6 | all | 3.47 | 9.84 | 2.84 |
| H6 | without rot19 | 3.47 | 9.84 | 2.84 |
| H6 | rot19 alone | 2.82 | 9.84 | 3.49 |

**Surviving detection claim (one sentence).** Against both references, every lobe design has an affected sector at least 3.0× its all-null sector ruler (18/18 design × reference established), but as one whole-map number the margin is only 2.4× (largest sector over the largest no-change null; weakest LeftOnly_test_c3, H6; sensitive) and the sector-shaped part of the data separates every target from every null by 2.3× (sensitive).
Weakest per-sector case: Test_B (H6) at 3.03×. Without rot19 the explained-norm separation is 2.28×, so rot19 does not set it.

## 7. Staging claims with and without rot19 (0.3a)

The imaging claims table has one staging-type claim: the bias-corrected Moderate front/back magnitude (B24). Three ways: 11 nulls (round 3): lobe_B 2.23–2.80×, lobe_A 1.38–1.88×; all: lobe_B 2.23–2.80×, lobe_A 1.38–1.88×; without rot19: lobe_B 2.23–2.80×, lobe_A 1.38–1.88×; rot19 alone: lobe_B 5.04–10.29×, lobe_A 3.89–8.90×. The R21/R32 staging verdict is the main session's; nothing in this folder computes it.

## 8. Round-3 and round-4 computations with every null (points 1 and 3 of round 4, and the rank rules)

Regression: the '11 nulls (round 3)' column reproduces the committed `lobe_round4.json`: **True**.

**Fit statistic (point 1).** Every design against both references (ρ and explained norm do not depend on the null set; the limit does not either):

| reference | limit | rho_rot19 | accepted_targets_above_rot19 | max_target_rho | min_null_rho | nulls_accepted | nulls_rejected | targets_rejected | null_abs_residual | target_abs_residual | null_explained | target_explained | rot19_data_norm | smallest_target_data_norm | spearman_rho_vs_data_norm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | 0.867 | 0.920 | 0 | 0.578 | 0.756 | Null_rot31, Null_rot43, MCI_lobe_c3, Null_rot07, Healthy_sliced_new | Null_rot19 | none | 4.0–10.2 | 6.8–18.6 | 3.5–5.6 | 12.8–35.7 | 11.1 | 14.7 | -0.69 |
| H6 | 0.824 | 0.940 | 0 | 0.549 | 0.758 | Healthy_sliced | MCI_lobe_c3, Null_rot19, Null_rot31, Null_rot43, Null_rot07 | none | 3.7–7.7 | 5.5–17.1 | 1.3–3.5 | 9.8–33.4 | 8.2 | 11.5 | -0.86 |

| reference | design | rho | data_norm | explained_norm | limit | rejected |
|---|---|---|---|---|---|---|
| H6 | MCI_lobe_c3 | 0.944 | 3.9 | 1.3 | 0.824 | True |
| H6 | Null_rot19 | 0.940 | 8.2 | 2.8 | 0.824 | True |
| H6 | Null_rot31 | 0.929 | 6.5 | 2.4 | 0.824 | True |
| H6 | Null_rot43 | 0.889 | 7.2 | 3.3 | 0.824 | True |
| H6 | Null_rot07 | 0.889 | 4.3 | 2.0 | 0.824 | True |
| H6 | Healthy_sliced | 0.758 | 5.3 | 3.5 | 0.824 | False |
| H7 | Null_rot19 | 0.920 | 11.1 | 4.3 | 0.867 | True |
| H7 | Null_rot31 | 0.836 | 9.7 | 5.3 | 0.867 | False |
| H7 | Null_rot43 | 0.834 | 10.1 | 5.6 | 0.867 | False |
| H7 | MCI_lobe_c3 | 0.794 | 6.6 | 4.0 | 0.867 | False |
| H7 | Null_rot07 | 0.794 | 7.1 | 4.3 | 0.867 | False |
| H7 | Healthy_sliced_new | 0.756 | 5.3 | 3.5 | 0.867 | False |

**Rank readings (round 3 §7).**

| nulls | reading | hits | misses | false_alarms | exact | n |
|---|---|---|---|---|---|---|
| 11 nulls (round 3) | frozen T_abs | 51 | 21 | 0 | 15 | 26 |
| 11 nulls (round 3) | rank (largest gap, gate T_null) | 58 | 14 | 0 | 20 | 26 |
| 11 nulls (round 3) | rank (above midpoint, gate T_null) | 60 | 12 | 0 | 22 | 26 |
| 11 nulls (round 3) | raw delay (centred, largest gap, gate null max) | 43 | 29 | 6 | 14 | 26 |
| all | frozen T_abs | 51 | 21 | 0 | 19 | 30 |
| all | rank (largest gap, gate T_null) | 58 | 14 | 0 | 24 | 30 |
| all | rank (above midpoint, gate T_null) | 60 | 12 | 0 | 26 | 30 |
| all | raw delay (centred, largest gap, gate null max) | 31 | 41 | 3 | 18 | 30 |
| without rot19 | frozen T_abs | 51 | 21 | 0 | 17 | 28 |
| without rot19 | rank (largest gap, gate T_null) | 58 | 14 | 0 | 22 | 28 |
| without rot19 | rank (above midpoint, gate T_null) | 60 | 12 | 0 | 24 | 28 |
| without rot19 | raw delay (centred, largest gap, gate null max) | 31 | 41 | 3 | 16 | 28 |

**Born vs raw delay, identically calibrated (point 3).** Thresholds from the null rows only:

| nulls | statistic | calibration | rule | threshold | hits | false_alarms | exact | n | false_alarms_on_nulls |
|---|---|---|---|---|---|---|---|---|---|
| 11 nulls (round 3) | Born | T_null_set | threshold | 4.75 | 72 | 25 | 15 | 26 | 0 |
| 11 nulls (round 3) | Born | T_null_set | gap | 4.75 | 58 | 0 | 20 | 26 | 0 |
| 11 nulls (round 3) | Born | T_recipe | threshold | 13.81 | 51 | 0 | 15 | 26 | 0 |
| 11 nulls (round 3) | Born | T_recipe | gap | 13.81 | 54 | 0 | 18 | 26 | 0 |
| 11 nulls (round 3) | raw uncentred | T_null_set | threshold | 2.95 | 72 | 29 | 13 | 26 | 0 |
| 11 nulls (round 3) | raw uncentred | T_null_set | gap | 2.95 | 50 | 6 | 14 | 26 | 0 |
| 11 nulls (round 3) | raw uncentred | T_recipe | threshold | 2.95 | 72 | 29 | 13 | 26 | 0 |
| 11 nulls (round 3) | raw uncentred | T_recipe | gap | 2.95 | 50 | 6 | 14 | 26 | 0 |
| 11 nulls (round 3) | raw centred | T_null_set | threshold | 0.89 | 22 | 0 | 14 | 26 | 0 |
| 11 nulls (round 3) | raw centred | T_null_set | gap | 0.89 | 39 | 5 | 14 | 26 | 0 |
| 11 nulls (round 3) | raw centred | T_recipe | threshold | 0.89 | 22 | 0 | 14 | 26 | 0 |
| 11 nulls (round 3) | raw centred | T_recipe | gap | 0.89 | 39 | 5 | 14 | 26 | 0 |
| all | Born | T_null_set | threshold | 4.75 | 72 | 25 | 19 | 30 | 0 |
| all | Born | T_null_set | gap | 4.75 | 58 | 0 | 24 | 30 | 0 |
| all | Born | T_recipe | threshold | 13.81 | 51 | 0 | 19 | 30 | 0 |
| all | Born | T_recipe | gap | 13.81 | 54 | 0 | 22 | 30 | 0 |
| all | raw uncentred | T_null_set | threshold | 4.02 | 71 | 23 | 18 | 30 | 0 |
| all | raw uncentred | T_null_set | gap | 4.02 | 50 | 6 | 18 | 30 | 0 |
| all | raw uncentred | T_recipe | threshold | 4.02 | 71 | 23 | 18 | 30 | 0 |
| all | raw uncentred | T_recipe | gap | 4.02 | 50 | 6 | 18 | 30 | 0 |
| all | raw centred | T_null_set | threshold | 1.17 | 15 | 0 | 16 | 30 | 0 |
| all | raw centred | T_null_set | gap | 1.17 | 27 | 2 | 18 | 30 | 0 |
| all | raw centred | T_recipe | threshold | 1.17 | 15 | 0 | 16 | 30 | 0 |
| all | raw centred | T_recipe | gap | 1.17 | 27 | 2 | 18 | 30 | 0 |
| without rot19 | Born | T_null_set | threshold | 4.75 | 72 | 25 | 17 | 28 | 0 |
| without rot19 | Born | T_null_set | gap | 4.75 | 58 | 0 | 22 | 28 | 0 |
| without rot19 | Born | T_recipe | threshold | 13.81 | 51 | 0 | 17 | 28 | 0 |
| without rot19 | Born | T_recipe | gap | 13.81 | 54 | 0 | 20 | 28 | 0 |
| without rot19 | raw uncentred | T_null_set | threshold | 4.02 | 71 | 23 | 16 | 28 | 0 |
| without rot19 | raw uncentred | T_null_set | gap | 4.02 | 50 | 6 | 16 | 28 | 0 |
| without rot19 | raw uncentred | T_recipe | threshold | 4.02 | 71 | 23 | 16 | 28 | 0 |
| without rot19 | raw uncentred | T_recipe | gap | 4.02 | 50 | 6 | 16 | 28 | 0 |
| without rot19 | raw centred | T_null_set | threshold | 1.17 | 15 | 0 | 14 | 28 | 0 |
| without rot19 | raw centred | T_null_set | gap | 1.17 | 27 | 2 | 16 | 28 | 0 |
| without rot19 | raw centred | T_recipe | threshold | 1.17 | 15 | 0 | 14 | 28 | 0 |
| without rot19 | raw centred | T_recipe | gap | 1.17 | 27 | 2 | 16 | 28 | 0 |

**Rank rules out of sample (round 4 §4).**

| nulls | held_out | statistic | kinds | hits | false_alarms | exact | n | exact_without_TestB | TestB_read |
|---|---|---|---|---|---|---|---|---|---|
| 11 nulls (round 3) | design | Born | gap/mid | 58 | 0 | 20 | 26 | 18/24 | H7: S2 S5; H6: S2 S5 |
| 11 nulls (round 3) | design | Born | threshold | 68 | 3 | 20 | 26 | 19/24 | H7: S2 S5; H6: S2 |
| 11 nulls (round 3) | design | raw centred | gap/mid | 20 | 2 | 12 | 26 | 10/24 | H7: S2 S5; H6: S2 S5 |
| 11 nulls (round 3) | design | raw centred | threshold | 19 | 0 | 13 | 26 | 12/24 | H7: S2; H6: S2 S5 |
| 11 nulls (round 3) | design | raw uncentred | gap/mid | 42 | 6 | 10 | 26 | 8/24 | H7: S2 S5; H6: S2 S5 |
| 11 nulls (round 3) | design | raw uncentred | threshold | 60 | 16 | 15 | 26 | 14/24 | H7: S2 S5; H6: none |
| 11 nulls (round 3) | family | Born | gap/mid | 58 | 0 | 20 | 26 | 18/24 | H7: S2 S5; H6: S2 S5 |
| 11 nulls (round 3) | family | Born | threshold | 69 | 3 | 21 | 26 | 20/24 | H7: S2 S5; H6: S2 |
| 11 nulls (round 3) | family | raw centred | gap/mid | 13 | 2 | 12 | 26 | 10/24 | H7: S2 S5; H6: S2 S5 |
| 11 nulls (round 3) | family | raw centred | threshold | 19 | 0 | 13 | 26 | 12/24 | H7: S2; H6: S2 S5 |
| 11 nulls (round 3) | family | raw uncentred | gap/mid | 45 | 6 | 10 | 26 | 8/24 | H7: S2 S5; H6: S2 S5 |
| 11 nulls (round 3) | family | raw uncentred | threshold | 68 | 16 | 17 | 26 | 16/24 | H7: S2 S5; H6: none |
| all | design | Born | gap/mid | 58 | 0 | 24 | 30 | 22/28 | H7: S2 S5; H6: S2 S5 |
| all | design | Born | threshold | 68 | 3 | 24 | 30 | 23/28 | H7: S2 S5; H6: S2 |
| all | design | raw centred | gap/mid | 20 | 2 | 16 | 30 | 14/28 | H7: S2 S5; H6: S2 S5 |
| all | design | raw centred | threshold | 14 | 1 | 15 | 30 | 15/28 | H7: S2; H6: S2 |
| all | design | raw uncentred | gap/mid | 40 | 9 | 12 | 30 | 11/28 | H7: S2 S5; H6: none |
| all | design | raw uncentred | threshold | 60 | 16 | 19 | 30 | 18/28 | H7: S2 S5; H6: none |
| all | family | Born | gap/mid | 58 | 0 | 24 | 30 | 22/28 | H7: S2 S5; H6: S2 S5 |
| all | family | Born | threshold | 69 | 3 | 25 | 30 | 24/28 | H7: S2 S5; H6: S2 |
| all | family | raw centred | gap/mid | 13 | 2 | 16 | 30 | 14/28 | H7: S2 S5; H6: S2 S5 |
| all | family | raw centred | threshold | 14 | 1 | 15 | 30 | 15/28 | H7: S2; H6: S2 |
| all | family | raw uncentred | gap/mid | 43 | 9 | 12 | 30 | 11/28 | H7: S2 S5; H6: none |
| all | family | raw uncentred | threshold | 68 | 16 | 21 | 30 | 20/28 | H7: S2 S5; H6: none |
| without rot19 | design | Born | gap/mid | 58 | 0 | 22 | 28 | 20/26 | H7: S2 S5; H6: S2 S5 |
| without rot19 | design | Born | threshold | 68 | 3 | 22 | 28 | 21/26 | H7: S2 S5; H6: S2 |
| without rot19 | design | raw centred | gap/mid | 20 | 2 | 14 | 28 | 12/26 | H7: S2 S5; H6: S2 S5 |
| without rot19 | design | raw centred | threshold | 14 | 1 | 13 | 28 | 13/26 | H7: S2; H6: S2 |
| without rot19 | design | raw uncentred | gap/mid | 40 | 9 | 10 | 28 | 9/26 | H7: S2 S5; H6: none |
| without rot19 | design | raw uncentred | threshold | 60 | 16 | 17 | 28 | 16/26 | H7: S2 S5; H6: none |
| without rot19 | family | Born | gap/mid | 58 | 0 | 22 | 28 | 20/26 | H7: S2 S5; H6: S2 S5 |
| without rot19 | family | Born | threshold | 69 | 3 | 23 | 28 | 22/26 | H7: S2 S5; H6: S2 |
| without rot19 | family | raw centred | gap/mid | 13 | 2 | 14 | 28 | 12/26 | H7: S2 S5; H6: S2 S5 |
| without rot19 | family | raw centred | threshold | 14 | 1 | 13 | 28 | 13/26 | H7: S2; H6: S2 |
| without rot19 | family | raw uncentred | gap/mid | 43 | 9 | 10 | 28 | 9/26 | H7: S2 S5; H6: none |
| without rot19 | family | raw uncentred | threshold | 68 | 16 | 19 | 28 | 18/26 | H7: S2 S5; H6: none |

**Result.** Born, null-only threshold: 72/25/19 (hits/FA/exact) with all nulls vs 72/25/15 with 11; Born gap: 58/0/24 vs 58/0/20; best raw rule (same calibration): raw centred gap 27/2/18. Born rank rule leave-one-family-out: 58/0/24 of 30 (11 nulls: 58/0/20 of 26); Test_B read H7: S2 S5; H6: S2 S5.

## 9. Is the primary reference typical? (0.3c, POST-HOC, not adopted)

Each of the 6 healthy meshes against the complex mean of the other 5 (frozen inversion; primary method shown, all three in the JSON):

| mesh | method | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | LR | FB | max_abs_sector |
|---|---|---|---|---|---|---|---|---|---|---|
| H6 | Tikhonov dS | -0.51 | -0.70 | -0.21 | +0.50 | +1.91 | +0.02 | -1.42 | -1.01 | 1.91 |
| H7 | Tikhonov dS | -3.10 | -3.07 | -3.44 | -2.09 | -0.98 | -3.52 | -1.00 | -1.02 | 3.52 |
| rot07 | Tikhonov dS | +1.19 | +1.17 | +2.23 | -1.13 | -0.69 | +0.81 | +1.64 | +2.32 | 2.23 |
| rot19 | Tikhonov dS | -1.09 | -1.52 | +0.10 | -0.67 | +0.19 | +0.51 | -1.06 | -0.42 | 1.52 |
| rot31 | Tikhonov dS | +2.47 | +2.45 | +1.28 | +2.30 | -0.63 | +1.02 | +1.67 | +0.17 | 2.47 |
| rot43 | Tikhonov dS | +1.07 | +1.72 | +0.04 | +1.14 | +0.24 | +1.21 | +0.16 | -0.07 | 1.72 |

Raw neighbour-path delay against the mean of the others (deg; + = more delay):

| mesh | view | ring_mean_delay | ring_range | left_minus_right |
|---|---|---|---|---|
| H6 | fit 3.4/3.6/3.8 | -0.22 | +1.28 | -0.87 |
| H6 | band 3.2-4.2 | +0.00 | +1.21 | -0.72 |
| H7 | fit 3.4/3.6/3.8 | -2.28 | +1.08 | -0.46 |
| H7 | band 3.2-4.2 | -1.58 | +0.93 | -0.41 |
| rot07 | fit 3.4/3.6/3.8 | +0.11 | +1.67 | +0.85 |
| rot07 | band 3.2-4.2 | +0.18 | +1.06 | +0.46 |
| rot19 | fit 3.4/3.6/3.8 | +0.37 | +1.24 | -0.70 |
| rot19 | band 3.2-4.2 | +0.26 | +0.50 | -0.11 |
| rot31 | fit 3.4/3.6/3.8 | +1.41 | +1.35 | +0.94 |
| rot31 | band 3.2-4.2 | +0.77 | +0.97 | +0.76 |
| rot43 | fit 3.4/3.6/3.8 | +0.55 | +0.40 | +0.22 |
| rot43 | band 3.2-4.2 | +0.34 | +0.70 | +0.02 |

Criterion (fixed before loading): H6 is atypical if it is the most extreme in at least twice the chance number of rows, or if all other meshes lie on one side of it for at least max(2, 3 × the chance expectation) statistics.

Most extreme mesh per statistic (33 statistic × method rows; H6 is most extreme in 4; chance alone ≈ 5.5):

| method | statistic | most_extreme | H6_rank | H6 | largest_other |
|---|---|---|---|---|---|
| Tikhonov dS | S1 Fr | H7 | 6 | -0.51 | 3.10 |
| Tikhonov dS | S2 TL | H7 | 6 | -0.70 | 3.07 |
| Tikhonov dS | S3 PL | H7 | 4 | -0.21 | 3.44 |
| Tikhonov dS | S4 Oc | rot31 | 6 | +0.50 | 2.30 |
| Tikhonov dS | S5 PR | H6 | 1 | +1.91 | 0.98 |
| Tikhonov dS | S6 TR | H7 | 6 | +0.02 | 3.52 |
| Tikhonov dS | LR | rot31 | 3 | -1.42 | 1.67 |
| Tikhonov dS | FB | rot07 | 3 | -1.01 | 2.32 |
| Tikhonov dS | max_abs_sector | H7 | 4 | +1.91 | 3.52 |
| frozen log | S1 Fr | rot31 | 6 | -0.24 | 2.43 |
| frozen log | S2 TL | rot19 | 6 | -0.12 | 2.04 |
| frozen log | S3 PL | rot07 | 5 | -0.11 | 2.89 |
| frozen log | S4 Oc | rot07 | 5 | +0.84 | 1.27 |
| frozen log | S5 PR | H6 | 1 | +1.75 | 1.09 |
| frozen log | S6 TR | H7 | 4 | +0.47 | 1.99 |
| frozen log | LR | rot31 | 2 | -1.23 | 1.56 |
| frozen log | FB | rot07 | 5 | -1.08 | 2.52 |
| frozen log | max_abs_sector | rot07 | 5 | +1.75 | 2.89 |
| whitened log | S1 Fr | rot19 | 6 | +0.12 | 1.86 |
| whitened log | S2 TL | rot19 | 6 | +0.01 | 2.64 |
| whitened log | S3 PL | rot07 | 6 | +0.46 | 2.82 |
| whitened log | S4 Oc | rot19 | 6 | +0.57 | 1.52 |
| whitened log | S5 PR | H6 | 1 | +1.90 | 1.02 |
| whitened log | S6 TR | rot07 | 5 | +0.45 | 1.73 |
| whitened log | LR | rot31 | 3 | -0.94 | 1.44 |
| whitened log | FB | rot07 | 4 | -0.45 | 2.30 |
| whitened log | max_abs_sector | rot07 | 4 | +1.90 | 2.82 |
| raw (fit 3.4/3.6/3.8) | ring_mean_delay | H7 | 5 | -0.22 | 2.28 |
| raw (fit 3.4/3.6/3.8) | ring_range | rot07 | 3 | +1.28 | 1.67 |
| raw (fit 3.4/3.6/3.8) | left_minus_right | rot31 | 2 | -0.87 | 0.94 |
| raw (band 3.2-4.2) | ring_mean_delay | H7 | 6 | +0.00 | 1.58 |
| raw (band 3.2-4.2) | ring_range | H6 | 1 | +1.21 | 1.06 |
| raw (band 3.2-4.2) | left_minus_right | rot31 | 2 | -0.72 | 0.76 |

Against H6 as the reference, the other healthy meshes per statistic (primary method; one side = all on one side):

| statistic | values | n_positive | one_side |
|---|---|---|---|
| S1 Fr | H7 -2.16, rot07 +1.43, rot19 -0.41, rot31 +2.52, rot43 +1.36 | 3/5 | False |
| S2 TL | H7 -1.98, rot07 +1.64, rot19 -0.61, rot31 +2.71, rot43 +2.10 | 3/5 | False |
| S3 PL | H7 -2.70, rot07 +2.02, rot19 +0.24, rot31 +1.23, rot43 +0.21 | 4/5 | False |
| S4 Oc | H7 -2.16, rot07 -1.38, rot19 -1.00, rot31 +1.48, rot43 +0.52 | 2/5 | False |
| S5 PR | H7 -2.39, rot07 -2.17, rot19 -1.44, rot31 -2.12, rot43 -1.40 | 0/5 | True |
| S6 TR | H7 -2.97, rot07 +0.66, rot19 +0.40, rot31 +0.82, rot43 +0.99 | 4/5 | False |
| LR | H7 +0.34, rot07 +2.58, rot19 +0.33, rot31 +2.62, rot43 +1.36 | 5/5 | True |
| FB | H7 +0.00, rot07 +2.81, rot19 +0.59, rot31 +1.04, rot43 +0.84 | 5/5 | True |
| ring-mean neighbour delay (fit 3.4/3.6/3.8), deg | H7 -1.72, rot07 +0.28, rot19 +0.49, rot31 +1.36, rot43 +0.64 | 4/5 | False |
| ring-mean neighbour delay (band 3.2-4.2), deg | H7 -1.32, rot07 +0.15, rot19 +0.21, rot31 +0.64, rot43 +0.28 | 4/5 | False |

Claims that use H6 as their reference: the RightOnly C6 verdict (committed rule: LR vs H6); the blind test's 'FAIL with the matched reference'; the lobe_A set (one-pass yardstick, bias-corrected FB in lobe_A); the H6 rows of the Test_B readings, rulers and LR_anti; the raw per-antenna delays of round 3 (§5) and the user's 0.3(b) numbers.

Frozen calls (primary method, frozen thresholds) against H7, H6 and the mean of all healthy meshes:

| design | truth | called_H7 | called_H6 | called_mean | side_H6 | side_mean | rank_H6 | rank_mean | LR_H6 | LR_mean |
|---|---|---|---|---|---|---|---|---|---|---|
| LeftOnly_test_c3 | S2 S3 | S3 | none | none | left | left | S2 S3 | S2 S3 | +8.82 | +7.63 |
| MCI_lobe_c3 | none | none | none | none | none | none | none | none | +1.37 | +0.19 |
| Mild_lobe | S2 S3 S5 S6 | S2 S3 S5 S6 | S2 S3 S6 | S2 S3 S5 S6 | none | none | S2 S3 S5 S6 | S2 S3 S5 S6 | +0.35 | -0.88 |
| Mild_lobe_new | S2 S3 S5 S6 | S2 S3 S6 | S2 | none | none | none | S2 S3 S5 S6 | S2 S3 S5 S6 | +0.87 | -0.33 |
| Moderate_lobe | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S3 S5 S6 | S1 S3 S5 S6 | none | right | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | -3.54 | -4.74 |
| Moderate_lobe_c3 | S1 S2 S3 S5 S6 | S1 S3 S6 | S1 | none | none | none | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | -1.40 | -2.57 |
| RightOnly_test | S5 S6 | S5 S6 | S5 S6 | S5 S6 | right | right | S6 | S5 S6 | -9.44 | -10.66 |
| Severe_lobe | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | none | none | S1 S3 S6 | S1 S3 S5 S6 | -0.43 | -1.64 |
| Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S3 S6 | S1 S3 S5 S6 | none | none | S1 S3 S6 | S1 S3 S6 | +0.74 | -0.43 |
| Test_B | S2 S5 | S2 | none | none | none | none | S2 S5 | S2 S5 | +1.13 | -0.05 |

Scored against the truth (sectors, summed over the designs above):

| reference | reading | hits | misses | false_alarms | exact |
|---|---|---|---|---|---|
| H7 | frozen T_abs calls | 31 | 5 | 0 | 6/10 |
| H7 | rank set (largest gap, gate T_null; not adopted) | 29 | 7 | 0 | 7/10 |
| H6 | frozen T_abs calls | 20 | 16 | 0 | 3/10 |
| H6 | rank set (largest gap, gate T_null; not adopted) | 29 | 7 | 0 | 7/10 |
| mean of healthy meshes | frozen T_abs calls | 20 | 16 | 0 | 4/10 |
| mean of healthy meshes | rank set (largest gap, gate T_null; not adopted) | 31 | 5 | 0 | 8/10 |

The committed C6 rule applied to each reference:

| reference | LR | phase_3p4 | phase_3p6 | verdict |
|---|---|---|---|---|
| H7 | -9.83 | -7.44 | -4.95 | REPLICATED |
| H6 | -9.44 | -7.28 | -3.91 | REPLICATED |
| mean of healthy meshes | -10.66 | -7.45 | -4.84 | REPLICATED |

**Result.** H6 is the most extreme of 6 meshes in 4 of 33 statistic rows (≈ 5.5 expected if the meshes are exchangeable): Tikhonov dS S5 PR, frozen log S5 PR, whitened log S5 PR, raw (band 3.2-4.2) ring_range. Statistics on which all 5 other healthy meshes lie on one side of H6: S5 PR, LR, FB (3 of 10; chance 0.062 each, ≈ 0.6 expected, the statistics are correlated). With the mean of the healthy meshes as reference, frozen calls score 20 hits / 0 FA / 4/10 exact, against 20 / 0 / 3/10 with H6 and 31 / 0 / 6/10 with H7; calls, side or rank set change for 7 of 10 designs (Mild_lobe, Mild_lobe_new, Moderate_lobe, Moderate_lobe_c3, RightOnly_test, Severe_lobe, Severe_lobe_c3). The C6 rule gives REPLICATED (committed, vs H6: REPLICATED).

## 10. The user's at-a-glance phase columns, recomputed (verify, do not adopt)

Mine: per neighbour path, minus the mean phase change against H6 over the window (delay positive); ring mean over the six neighbour paths; spread = SD and range over them; left − right = mean(T1-T2, T2-T3, T3-T4) − mean(T4-T5, T5-T6, T6-T1). These definitions do not reproduce the user's numbers exactly on rot07/rot19 (checked before loading the new files), so only signs and ordering are compared.

| null | view | ring_mean_delay | user_ring_mean | path_SD | path_range | user_spread | left_minus_right | user_left_right |
|---|---|---|---|---|---|---|---|---|
| rot07 | band 3.2-4.2 | +0.15 | 0.24 | +0.88 | +2.12 | 1.45 | +0.82 | 0.69 |
| rot19 | band 3.2-4.2 | +0.21 | 0.85 | +0.57 | +1.47 | 0.68 | +0.53 | 0.28 |
| rot31 | band 3.2-4.2 | +0.64 | 0.63 | +0.80 | +2.27 | 1.69 | +1.17 | 1.17 |
| rot43 | band 3.2-4.2 | +0.28 | 0.55 | +0.73 | +1.85 | 0.91 | +0.58 | 0.84 |
| rot07 | 3.30-3.65 | +0.24 | 0.24 | +0.84 | +2.24 | 1.45 | +0.72 | 0.69 |
| rot19 | 3.30-3.65 | +0.85 | 0.85 | +0.57 | +1.69 | 0.68 | +0.48 | 0.28 |
| rot31 | 3.30-3.65 | +0.63 | 0.63 | +0.85 | +2.49 | 1.69 | +1.26 | 1.17 |
| rot43 | 3.30-3.65 | +0.55 | 0.55 | +0.65 | +1.74 | 0.91 | +0.85 | 0.84 |
| rot07 | fit 3.4/3.6/3.8 | +0.28 | 0.24 | +1.17 | +3.13 | 1.45 | +1.33 | 0.69 |
| rot19 | fit 3.4/3.6/3.8 | +0.49 | 0.85 | +0.71 | +1.97 | 0.68 | +0.40 | 0.28 |
| rot31 | fit 3.4/3.6/3.8 | +1.36 | 0.63 | +1.11 | +3.10 | 1.69 | +1.68 | 1.17 |
| rot43 | fit 3.4/3.6/3.8 | +0.64 | 0.55 | +0.63 | +1.61 | 0.91 | +0.77 | 0.84 |

**Result.** Ring-mean delay has the user's sign (more delay than H6) for 4 of 4 rotated nulls (band 3.2–4.2 GHz). Rank agreement of the spread (Spearman, n = 4): 0.80.

## 11. Survival table (11 nulls → all nulls, three ways)

| claim | 11 nulls (round 3) | all | without rot19 | rot19 alone | tier_all | tier_without_rot19 |
|---|---|---|---|---|---|---|
| LeftOnly LR_anti / R1c ruler (H7, Tikhonov dS) | 1.93 | 1.93 | 1.93 | 3.67 | not determined | not determined |
| LeftOnly LR_anti / R1c ruler (H7, whitened log) | 2.76 | 2.76 | 2.76 | 4.39 | sensitive | sensitive |
| LeftOnly LR_anti / R1c ruler (H6, Tikhonov dS) | 1.94 | 1.94 | 1.94 | 3.70 | not determined | not determined |
| LeftOnly LR_anti / R1c ruler (H6, whitened log) | 2.77 | 2.77 | 2.77 | 4.44 | sensitive | sensitive |
| RightOnly LR_anti / R1c ruler (H7, Tikhonov dS) | 2.50 | 2.50 | 2.50 | 4.75 | sensitive | sensitive |
| RightOnly LR_anti / R1c ruler (H7, whitened log) | 3.37 | 3.37 | 3.37 | 5.35 | established | established |
| RightOnly LR_anti / R1c ruler (H6, Tikhonov dS) | 2.51 | 2.51 | 2.51 | 4.78 | sensitive | sensitive |
| RightOnly LR_anti / R1c ruler (H6, whitened log) | 3.38 | 3.38 | 3.38 | 5.43 | established | established |
| pair rank p, product of the two rank p's (H7, Tikhonov dS) | 0.0069 | 0.0051 | 0.0059 | n/a |  |  |
| pair rank p, both beyond the same nulls (exact) (H7, Tikhonov dS) | 0.0128 | 0.0095 | 0.0110 | n/a |  |  |
| pair rank p, product of the two rank p's (H6, Tikhonov dS) | 0.0069 | 0.0051 | 0.0059 | n/a |  |  |
| pair rank p, both beyond the same nulls (exact) (H6, Tikhonov dS) | 0.0128 | 0.0095 | 0.0110 | n/a |  |  |
| LeftOnly cross-ratio phases >= 3x (rms rule), band mean 3.2-4.2 GHz, of 18 | 12 | 12 | 12 | 12 |  |  |
| LeftOnly cross-ratio phases >= 3x (max rule), band mean 3.2-4.2 GHz, of 18 | 3 | 2 | 2 | 12 |  |  |
| null files >= 3x (leave-one-out, rms rule), band mean 3.2-4.2 GHz, max over files, of 18 | 0 | 0 | 0 | n/a |  |  |
| LeftOnly cross-ratio phases >= 3x (rms rule), band mean 3.30-3.65 GHz, of 18 | 11 | 10 | 11 | 5 |  |  |
| LeftOnly cross-ratio phases >= 3x (max rule), band mean 3.30-3.65 GHz, of 18 | 3 | 2 | 2 | 5 |  |  |
| null files >= 3x (leave-one-out, rms rule), band mean 3.30-3.65 GHz, max over files, of 18 | 0 | 0 | 1 | n/a |  |  |
| LeftOnly cross-ratio phases >= 3x (rms rule), 3.4 GHz, of 18 | 9 | 9 | 9 | 9 |  |  |
| LeftOnly cross-ratio phases >= 3x (max rule), 3.4 GHz, of 18 | 3 | 2 | 2 | 9 |  |  |
| null files >= 3x (leave-one-out, rms rule), 3.4 GHz, max over files, of 18 | 0 | 1 | 1 | n/a |  |  |
| Test_B S2 TL / sector ruler (H7) | 3.50 | 3.11 | 3.11 | 3.50 | established | established |
| Test_B S5 PR / sector ruler (H7) | 2.55 | 2.55 | 2.55 | 2.55 | sensitive | sensitive |
| RightOnly S5 PR / sector ruler (H7) | 3.18 | 3.18 | 3.18 | 3.18 | established | established |
| RightOnly S6 TR / sector ruler (H7) | 4.34 | 4.34 | 4.34 | 4.34 | established | established |
| LeftOnly S2 TL / sector ruler (H7) | 3.13 | 2.78 | 2.78 | 3.13 | sensitive | sensitive |
| LeftOnly S3 PL / sector ruler (H7) | 3.16 | 3.16 | 3.16 | 5.03 | established | established |
| Test_B S2 TL / sector ruler (H6) | 3.03 | 3.03 | 3.03 | 3.03 | established | established |
| Test_B S5 PR / sector ruler (H6) | 2.10 | 2.10 | 2.10 | 2.10 | sensitive | sensitive |
| RightOnly S5 PR / sector ruler (H6) | 2.74 | 2.74 | 2.74 | 2.74 | sensitive | sensitive |
| RightOnly S6 TR / sector ruler (H6) | 3.75 | 3.75 | 3.75 | 3.75 | established | established |
| LeftOnly S2 TL / sector ruler (H6) | 2.65 | 2.65 | 2.65 | 2.65 | sensitive | sensitive |
| LeftOnly S3 PL / sector ruler (H6) | 4.55 | 4.55 | 4.55 | 4.55 | established | established |
| bias-corrected Moderate FB / ruler (lobe_A, Tikhonov dS) | 1.38 | 1.38 | 1.38 | 8.90 | not determined | not determined |
| bias-corrected Moderate FB / ruler (lobe_A, frozen log) | 1.58 | 1.58 | 1.58 | 7.00 | not determined | not determined |
| bias-corrected Moderate FB / ruler (lobe_A, whitened log) | 1.88 | 1.88 | 1.88 | 3.89 | not determined | not determined |
| bias-corrected Moderate FB / ruler (lobe_B, Tikhonov dS) | 2.61 | 2.61 | 2.61 | 10.29 | sensitive | sensitive |
| bias-corrected Moderate FB / ruler (lobe_B, frozen log) | 2.23 | 2.23 | 2.23 | 7.13 | sensitive | sensitive |
| bias-corrected Moderate FB / ruler (lobe_B, whitened log) | 2.80 | 2.80 | 2.80 | 5.04 | sensitive | sensitive |
| MCI largest of sector, LR, FB / its ruler without MCI (H7); claim: < 2x (nothing separable) | 1.37 | 0.93 | 0.93 | 1.37 | nothing separable (< 2x) | nothing separable (< 2x) |
| weakest design's best affected sector / sector ruler (H7), over 9 designs | 3.16 | 3.11 | 3.11 | 3.50 | established | established |
| weakest design's largest sector / max-sector ruler (H7) | 2.85 | 2.85 | 2.85 | 2.85 | sensitive | sensitive |
| MCI largest of sector, LR, FB / its ruler without MCI (H6); claim: < 2x (nothing separable) | 0.50 | 0.50 | 0.50 | 1.18 | nothing separable (< 2x) | nothing separable (< 2x) |
| weakest design's best affected sector / sector ruler (H6), over 9 designs | 3.03 | 3.03 | 3.03 | 3.03 | established | established |
| weakest design's largest sector / max-sector ruler (H6) | 2.38 | 2.38 | 2.38 | 2.38 | sensitive | sensitive |

**Tier changes from 11 nulls to all nulls:** LeftOnly S2 TL / sector ruler (H7): established → sensitive.

## Final table

| item | verdict | change | evidence |
|---|---|---|---|
| New files (QC) | CONFIRMED | sha256 = delivery; passive; worst non-reciprocal point Null_rot31 masked False, Null_rot43 masked False | lobe_round5.json: files, masks |
| Rotated nulls as targets | CONFIRMED | no frozen call (max sector 4.75 < 13.81); LR ≤ 0.74×, FB ≤ 0.73× the protocol rulers | lobe_round5.json: nulls_rows, nulls_read |
| Both mirror designs beyond all 13 nulls | CONFIRMED | rank p 1/14 each; LR_anti ratio LeftOnly 1.93–2.77×, RightOnly 2.50–3.38× (all-null ruler) | lobe_round5.json: anti, anti3 |
| Pair p | CHANGED (formula) | product 0.0069 (11 nulls) → exact 0.0095 (N = 13, 2/((N+1)(N+2))); round 3 understated p by 1.85× | lobe_round5.json: pairs |
| Independence of mesh asymmetries | supported (6/6) | q 0.83–0.94; rotation only, mirroring untested | lobe_round5.json: independence |
| Detection (0.3b) | re-graded | Against both references, every lobe design has an affected sector at least 3.0× its all-null sector ruler (18/18 design × reference established), but as one whole-map number the margin is only 2.4× (largest sector over the largest no-change null; weakest LeftOnly_test_c3, H6; sensitive) and the sector-shaped part of the data separates every target from every null by 2.3× (sensitive). | lobe_round5.json: detection, mci, fit |
| Staging (B24 bias-corrected FB) | sensitive | lobe_B 2.23–2.80× (11 nulls) → 2.23–2.80× (all), 2.23–2.80× (without rot19) | lobe_round5.json: b24 |
| Round 4 points 1, 3, 4 with every null | re-run | Born gap 24/30 exact, 0 FA; Born rank LOFO 58/0/24; nulls rejected by the fit rule: H7 Null_rot19; H6 MCI_lobe_c3, Null_rot19, Null_rot31, Null_rot43, Null_rot07 | lobe_round5.json: r4, fit |
| Reference typicality (0.3c) | H6 atypical on some statistics | H6 most extreme in 4/33 rows (chance ≈ 5.5); all others on one side for 3/10 statistics (≈ 0.6 by chance); mean reference: frozen calls 20/0/4/10 vs H6 20/0/3/10; C6 REPLICATED | lobe_round5.json: typ_*, one_sided, alt_* |
| User's at-a-glance phase columns | signs verified | ring-mean delay sign 4/4; definitions differ, magnitudes not compared | lobe_round5.json: glance |
| Survival (11 → all nulls) | 1 tier change(s) | LeftOnly S2 TL / sector ruler (H7): established → sensitive | lobe_round5.json: survival |

