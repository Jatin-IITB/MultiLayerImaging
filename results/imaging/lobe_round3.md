# Round 3 (imaging session): rotated nulls, Test_B truth, rank readings, raw delay, pass gap

**POST-HOC throughout.** Everything here was computed after the Test_B truth and the rotated nulls were released, by `python imaging/lobe_round3.py --n 100` at code `97efdd4-dirty` (numbers in `results/imaging/lobe_round3.json`). Frozen rules, thresholds, protocols, predictions and submitted estimates are unchanged. Committed verdicts stand as scored.

## 1. Test_B: the user's score against my committed protocol (24aa0c4)

Truth (released by the user): e = 0 / 11.5 / 0 / 0 / 7.5 / 0 mm, r_hip 17.5, Mild materials in S2 and S5, CSF_Mild everywhere. Affected: S2 (left temporal, deeper) and S5 (right parietal, shallower), a diagonal pair 180° apart.

| item | estimate | truth | score |
|---|---|---|---|
| lobes (committed reading rule) | affected none; possible S2 | S2, S5 | MISS |
| ranking (reported under the protocol) | S2 > S5 ≫ S3, S6, S1, S4 | S2 > S5 (deeper first) | correct pair in the correct order |
| side | none | both sides (left larger) | MISS (user's score) |
| front/back | none | S1, S4 unaffected | consistent; not scored by the user |

Recorded as scored. The committed rule was conservative: the frozen T_abs (13.81) was exceeded only by S2, and only against the 7-pass reference. The ranking, which the protocol reported but did not use for the reading, had the right pair in the right order.

## 2. New files: registry and QC

Registered in `imaging/lobe_c3.py` REGISTRY → `results/imaging/lobe_sets.csv` (passes, final ΔS and elements as supplied by the user). The nulls are marked kind = null and are in no frozen, training or stage set.

| file | points | max_singular_value | passive | max_recip_err_dB_re_band | worst_amp_nonrecip_dB | at_GHz | path | worst_point_masked | n_masked |
|---|---|---|---|---|---|---|---|---|---|
| new_with_slices_RightOnly_test.s6p | 201 | 0.9519 | True | -34.8 | 0.26 | 3.850 | T1–T5 | False | 0 |
| new_with_slices_Test_B.s6p | 201 | 0.9512 | True | -25.9 | 0.39 | 3.545 | T3–T6 | False | 3 |
| new_with_slices_Null_rot07.s6p | 201 | 0.9519 | True | -12.6 | 0.49 | 3.860 | T1–T4 | True | 2 |
| new_with_slices_Null_rot19.s6p | 201 | 0.9534 | True | -26.3 | 0.14 | 3.870 | T1–T4 | True | 1 |

Masked points (−30 dB rule):

| file | f_GHz | ports | path | type | Sij_dB | Sji_dB | recip_err_dB | at_fit_freq |
|---|---|---|---|---|---|---|---|---|
| new_with_slices_Test_B.s6p | 3.840 | 4-6 | T1–T5 | second-neighbour | -57.5 | -57.6 | -28.5 | False |
| new_with_slices_Test_B.s6p | 3.845 | 4-6 | T1–T5 | second-neighbour | -56.5 | -56.6 | -25.9 | False |
| new_with_slices_Test_B.s6p | 3.850 | 4-6 | T1–T5 | second-neighbour | -57.3 | -57.4 | -27.3 | False |
| new_with_slices_Null_rot07.s6p | 3.860 | 1-4 | T1–T4 | opposite | -42.5 | -42.0 | -12.6 | False |
| new_with_slices_Null_rot07.s6p | 3.565 | 3-4 | T1–T2 | neighbour | -35.1 | -35.0 | -20.6 | False |
| new_with_slices_Null_rot19.s6p | 3.870 | 1-4 | T1–T4 | opposite | -50.4 | -50.3 | -26.3 | False |

The 0.49 dB point of Null_rot07 (3.86 GHz, T1–T4) is masked; so is a second point (3.56 GHz, T1–T2). Neither is at a fit frequency.

## 3. Rotated nulls as targets (frozen pipeline, both references)

| null | reference | method | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | LR | LR_ratio | FB | FB_ratio | called | side | frontback | residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Null_rot07 | H7 (Healthy_sliced, 7 passes) | Tikhonov dS | +3.59 | +3.62 | +4.75 | +0.75 | +0.20 | +3.65 | +2.26 | 0.58 | +2.83 | 0.73 | none | none | none | 0.79 |
| Null_rot07 | H7 (Healthy_sliced, 7 passes) | bounded dS | +3.59 | +3.62 | +4.75 | +0.75 | +0.20 | +3.65 | +2.26 | 0.58 | +2.83 | 0.73 | none | none | none | 0.79 |
| Null_rot07 | H7 (Healthy_sliced, 7 passes) | frozen log | +2.91 | +2.11 | +4.47 | -0.30 | -0.04 | +3.19 | +1.71 | 0.44 | +3.21 | 0.71 | none | none | none | 0.79 |
| Null_rot07 | H7 (Healthy_sliced, 7 passes) | frozen bounded log | +2.86 | +2.14 | +4.35 | +0.00 | +0.00 | +3.18 | +1.66 | 0.42 | +2.86 | 0.63 | none | none | none | 0.79 |
| Null_rot07 | H7 (Healthy_sliced, 7 passes) | whitened log (POST-HOC) | +2.22 | +1.69 | +3.80 | -0.17 | -0.17 | +2.62 | +1.52 | 0.49 | +2.39 | 0.48 | n/a (no frozen thresholds) | n/a | n/a | 0.84 |
| Null_rot07 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | +1.43 | +1.64 | +2.02 | -1.38 | -2.17 | +0.66 | +2.58 | 0.73 | +2.81 | 0.73 | none | none | none | 0.89 |
| Null_rot07 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | +1.35 | +1.58 | +1.47 | +0.00 | +0.00 | +0.00 | +1.52 | 0.43 | +1.35 | 0.35 | none | none | none | 0.93 |
| Null_rot07 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | +1.29 | +0.99 | +2.51 | -1.73 | -1.76 | +1.17 | +2.04 | 0.58 | +3.01 | 0.73 | none | none | none | 0.87 |
| Null_rot07 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | +1.12 | +0.93 | +1.89 | +0.00 | +0.00 | +0.55 | +1.13 | 0.32 | +1.12 | 0.27 | none | none | none | 0.92 |
| Null_rot07 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log (POST-HOC) | +0.96 | +0.59 | +1.99 | -1.34 | -1.52 | +1.08 | +1.51 | 0.51 | +2.30 | 0.47 | n/a (no frozen thresholds) | n/a | n/a | 0.91 |
| Null_rot19 | H7 (Healthy_sliced, 7 passes) | Tikhonov dS | +1.73 | +1.37 | +2.98 | +1.22 | +1.02 | +3.45 | -0.06 | 0.01 | +0.51 | 0.13 | none | none | none | 0.92 |
| Null_rot19 | H7 (Healthy_sliced, 7 passes) | bounded dS | +1.73 | +1.37 | +2.98 | +1.22 | +1.02 | +3.45 | -0.06 | 0.01 | +0.51 | 0.13 | none | none | none | 0.92 |
| Null_rot19 | H7 (Healthy_sliced, 7 passes) | frozen log | +0.12 | -0.53 | +0.79 | -0.06 | -0.63 | +0.87 | +0.01 | 0.00 | +0.18 | 0.04 | none | none | none | 0.84 |
| Null_rot19 | H7 (Healthy_sliced, 7 passes) | frozen bounded log | +0.00 | +0.00 | +0.56 | +0.00 | +0.00 | +0.66 | -0.05 | 0.01 | +0.00 | 0.00 | none | none | none | 0.84 |
| Null_rot19 | H7 (Healthy_sliced, 7 passes) | whitened log (POST-HOC) | -0.45 | -1.08 | +0.50 | -0.58 | -1.03 | -0.32 | +0.38 | 0.12 | +0.14 | 0.03 | n/a (no frozen thresholds) | n/a | n/a | 0.91 |
| Null_rot19 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | Tikhonov dS | -0.41 | -0.61 | +0.24 | -1.00 | -1.44 | +0.40 | +0.33 | 0.09 | +0.59 | 0.15 | none | none | none | 0.94 |
| Null_rot19 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | bounded dS | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.00 | +0.00 | 0.00 | none | none | none | 0.95 |
| Null_rot19 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen log | -1.54 | -1.63 | -1.16 | -1.48 | -2.38 | -0.95 | +0.27 | 0.08 | -0.06 | 0.01 | none | none | none | 0.84 |
| Null_rot19 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | frozen bounded log | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.00 | +0.00 | 0.00 | none | none | none | 0.88 |
| Null_rot19 | H6 (Healthy_sliced_new, 6 passes, stop rule 1) | whitened log (POST-HOC) | -1.74 | -2.22 | -1.31 | -1.80 | -2.42 | -1.71 | +0.30 | 0.10 | +0.06 | 0.01 | n/a (no frozen thresholds) | n/a | n/a | 0.87 |

**Result.** No sector reaches T_abs (largest 4.75). LR and FB are at most 0.73× and 0.73× their rulers. Frozen calls in any method: 0. Applied to the nulls, the protocol's reading rule gives 'no lobe' for rot07. For rot19 it gives 'fit rejected'. *Revised in round 4:* that rejection is **not** a validation of the rule. The rule fires on the relative misfit of a mesh-only difference, so it acts as a signal-size gate (`lobe_round4.md` §1). **Verdict: CONFIRMED** that both nulls show no sector, LR or FB beyond the rulers.

## 4. 'Beyond all nulls' re-tested with the rotated nulls (the independence assumption)

Asymmetry-free LR_anti = ½[LR(X) − LR(mirror X)] for every null; R1c ruler = max(one-pass yardstick, largest |null|):

| reference | method | yardstick | null9_max | null9_rms | rot07 | rot19 | null11_max | null11_rms | LeftOnly ratio (9) | LeftOnly ratio (11) | LeftOnly rank p (11) | RightOnly ratio (9) | RightOnly ratio (11) | RightOnly rank p (11) | Test ratio (9) | Test ratio (11) | Test rank p (11) | both mirror designs beyond all 11 | rotated nulls within old 9-null envelope |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | Tikhonov dS | 2.14 | 4.07 | 1.62 | 1.41 | -0.96 | 4.07 | 1.55 | 1.93 | 1.93 | 0.08 | 2.50 | 2.50 | 0.08 | 0.04 | 0.04 | 0.92 | True | True |
| H7 | frozen log | 2.38 | 3.72 | 1.43 | 0.87 | -0.87 | 3.72 | 1.35 | 2.35 | 2.35 | 0.08 | 2.98 | 2.98 | 0.08 | 0.12 | 0.12 | 0.83 | True | True |
| H7 | whitened log | 1.98 | 3.14 | 1.21 | 0.58 | -0.68 | 3.14 | 1.12 | 2.76 | 2.76 | 0.08 | 3.37 | 3.37 | 0.08 | 0.04 | 0.04 | 1.00 | True | True |
| H6 | Tikhonov dS | 2.12 | 4.04 | 1.60 | 1.39 | -0.93 | 4.04 | 1.54 | 1.94 | 1.94 | 0.08 | 2.51 | 2.51 | 0.08 | 0.05 | 0.05 | 0.92 | True | True |
| H6 | frozen log | 2.38 | 3.76 | 1.45 | 0.88 | -0.88 | 3.76 | 1.37 | 2.35 | 2.35 | 0.08 | 2.98 | 2.98 | 0.08 | 0.11 | 0.11 | 0.83 | True | True |
| H6 | whitened log | 1.97 | 3.17 | 1.22 | 0.59 | -0.68 | 3.17 | 1.13 | 2.77 | 2.77 | 0.08 | 3.38 | 3.38 | 0.08 | 0.03 | 0.03 | 1.00 | True | True |

**Result.** The rotated nulls give LR_anti +1.41 (rot07) and -0.96 (rot19), inside the old nine-null envelope (4.07). The 11-null maximum is unchanged, so every ratio is unchanged: LeftOnly 1.93× and RightOnly 2.50× (Tikhonov dS). Both still lie beyond all 11 nulls; each has rank p = 1/12 = 0.083. If the two meshes' asymmetries are independent, the pair's rank p is ≈ 0.007 (was ≈ 0.01 with nine). **Verdict: CONFIRMED for this statistic**, with two rotated samples only. Meshes in other orientations did not produce a larger asymmetry-free LR. They do on other statistics (§5, §6), so 'the nulls share mesh structure' is real for some quantities.

## 5. The user's 0.3(b) numbers, verified

Band-mean (3.2–4.2 GHz) power difference of each mirror path pair (dB):

| pair | type | power Healthy_sliced_new dB | power Healthy_sliced dB | power Null_rot07 dB | power Null_rot19 dB | power LeftOnly_test_c3 dB | power Test_B dB | power max |old 9 nulls| dB |
|---|---|---|---|---|---|---|---|---|
| T1-T2 vs T1-T6 | neighbour | -0.070 | -0.048 | +0.126 | -0.071 | +0.082 | -0.031 | +0.127 |
| T1-T3 vs T1-T5 | second-neighbour | +0.074 | -0.083 | +0.156 | -0.444 | +0.108 | -0.372 | +0.495 |
| T2 refl. vs T6 refl. | reflection | -0.005 | -0.002 | -0.011 | -0.005 | -0.060 | -0.066 | +0.017 |
| T2-T3 vs T5-T6 | neighbour | -0.049 | -0.032 | +0.133 | -0.151 | +0.103 | +0.156 | +0.294 |
| T2-T4 vs T4-T6 | second-neighbour | +0.173 | -0.052 | +0.269 | +0.742 | -0.193 | +0.535 | +0.301 |
| T2-T5 vs T3-T6 | opposite | +0.015 | +0.017 | +0.081 | -0.144 | +0.151 | -0.429 | +0.208 |
| T3 refl. vs T5 refl. | reflection | -0.007 | -0.005 | -0.004 | +0.011 | -0.068 | +0.068 | +0.013 |
| T3-T4 vs T4-T5 | neighbour | -0.056 | +0.025 | -0.103 | -0.128 | -0.175 | -0.199 | +0.092 |

Single-path mirror phase difference at 3.4 GHz (deg):

| pair | phase@3.4 Healthy_sliced_new deg | phase@3.4 Healthy_sliced deg | phase@3.4 Null_rot07 deg | phase@3.4 Null_rot19 deg | phase@3.4 LeftOnly_test_c3 deg | phase@3.4 Test_B deg | phase@3.4 max |old 9 nulls| deg |
|---|---|---|---|---|---|---|---|
| T1-T2 vs T1-T6 | +0.71 | +0.67 | +1.67 | +0.98 | -2.90 | -2.56 | +1.36 |
| T1-T3 vs T1-T5 | -0.74 | -0.92 | +1.45 | -0.20 | +2.87 | -4.25 | +2.31 |
| T2 refl. vs T6 refl. | +0.55 | +0.50 | -0.47 | +0.58 | +4.84 | +5.64 | +0.57 |
| T2-T3 vs T5-T6 | +0.20 | +0.04 | +0.04 | +0.27 | -5.58 | +0.09 | +2.05 |
| T2-T4 vs T4-T6 | +0.25 | -0.75 | -0.12 | +0.45 | +4.34 | +5.85 | +3.22 |
| T2-T5 vs T3-T6 | +0.04 | +0.22 | +1.78 | +1.71 | -0.38 | +1.01 | +1.02 |
| T3 refl. vs T5 refl. | -0.34 | -0.20 | +0.12 | +0.62 | +4.94 | -4.82 | +0.35 |
| T3-T4 vs T4-T5 | +0.42 | +0.63 | -1.19 | -1.33 | -3.32 | +2.51 | +0.63 |

Per-antenna neighbour-path delay against Healthy_sliced_new (deg, + = more delay than the reference; mean of the antenna's two neighbour paths), with its range across the ring:

| design | view | T1 delay deg | T2 delay deg | T3 delay deg | T4 delay deg | T5 delay deg | T6 delay deg | ring_range |
|---|---|---|---|---|---|---|---|---|
| Null_rot07 | band 3.2-4.2 | +0.85 | +0.86 | +0.45 | -0.61 | -0.86 | +0.20 | +1.72 |
| Null_rot07 | fit 3.4/3.6/3.8 | +1.04 | +1.40 | +0.76 | -0.80 | -0.96 | +0.25 | +2.36 |
| Null_rot19 | band 3.2-4.2 | +0.58 | +0.33 | +0.51 | +0.03 | -0.46 | +0.27 | +1.04 |
| Null_rot19 | fit 3.4/3.6/3.8 | +0.77 | +0.45 | +0.69 | +0.18 | +0.01 | +0.83 | +0.82 |
| Healthy_sliced | band 3.2-4.2 | -1.22 | -1.14 | -1.29 | -1.32 | -1.44 | -1.50 | +0.36 |
| Healthy_sliced | fit 3.4/3.6/3.8 | -1.74 | -1.56 | -1.63 | -1.53 | -1.79 | -2.07 | +0.54 |
| LeftOnly_test_c3 | band 3.2-4.2 | +2.76 | +4.99 | +4.87 | +2.73 | +1.66 | +1.57 | +3.41 |
| LeftOnly_test_c3 | fit 3.4/3.6/3.8 | +2.33 | +4.77 | +4.90 | +2.58 | +1.60 | +1.48 | +3.42 |
| RightOnly_test | band 3.2-4.2 | +6.83 | +5.08 | +4.56 | +5.22 | +7.05 | +8.13 | +3.57 |
| RightOnly_test | fit 3.4/3.6/3.8 | +7.72 | +5.74 | +5.54 | +6.42 | +8.56 | +9.65 | +4.12 |
| Test_B | band 3.2-4.2 | +2.72 | +4.48 | +3.33 | +2.39 | +3.23 | +2.42 | +2.09 |
| Test_B | fit 3.4/3.6/3.8 | +2.21 | +4.25 | +2.98 | +2.33 | +3.68 | +2.28 | +2.05 |
| MCI_lobe_c3 | band 3.2-4.2 | +0.49 | +0.49 | +0.20 | +0.12 | -0.34 | -0.25 | +0.83 |
| MCI_lobe_c3 | fit 3.4/3.6/3.8 | +0.20 | +0.36 | +0.08 | +0.26 | -0.34 | -0.68 | +1.05 |

**Verified.**
- Second-neighbour band power reaches −0.44 dB (T1-T3 vs T1-T5, rot19) and +0.74 dB (T2-T4 vs T4-T6, rot19), above LeftOnly's 0.11 / 0.19 dB. The old nine nulls already reached 0.50 dB on the first pair; the 0.74 dB is new.
- Reflection power pairs stay ≤ 0.011 dB in the rotated nulls (old ≤ 0.017), against 0.060–0.068 dB for LeftOnly and Test_B.
- Single-path phase at 3.4 GHz reaches 1.67° (T1-T2 vs T1-T6, rot07) and 1.78° / 1.71° (T2-T5 vs T3-T6, rot07 / rot19). Both pairs exceed the old nulls (1.36°, 1.02°). Healthy_sliced_new stays ≤ 0.74°.
- The per-antenna ring range is 1.72° / 2.36° for rot07 and 1.04° / 0.82° for rot19 (band / fit frequencies); the user's measure gave 1.42° / 0.68°. Test_B's pattern on the same measure is 2.05–2.09°: not larger than rot07's.
**Consequence:** for single-path phase, second-neighbour power and the raw per-antenna delay, the old nine nulls understated the floor. For the reflection pairs and LR_anti they did not.

## 6. Rulers rebuilt with the rotated nulls (max over 9 + 2 nulls): what survives

Sector, LR and FB rulers of the Test_B protocol, primary method, with the rotated nulls added to the floors:

| reference | rulers | ruler S1 Fr | ruler S2 TL | ruler S3 PL | ruler S4 Oc | ruler S5 PR | ruler S6 TR | ruler_LR | ruler_FB | Test S2 TL ratio | Test S5 PR ratio | Test LR ratio | RightOnly S5 PR ratio | RightOnly S6 TR ratio | RightOnly LR ratio | LeftOnly S2 TL ratio | LeftOnly S3 PL ratio | LeftOnly LR ratio | rot07 max sector | rot19 max sector |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | old | 3.14 | 4.19 | 2.93 | 3.39 | 5.15 | 5.15 | 3.92 | 3.88 | 3.50 | 2.55 | 0.19 | 3.18 | 4.34 | 2.50 | 3.13 | 5.12 | 2.16 | 4.75 | 3.45 |
| H7 | with rotated nulls | 3.59 | 4.19 | 4.75 | 3.39 | 5.15 | 5.15 | 3.92 | 3.88 | 3.50 | 2.55 | 0.19 | 3.18 | 4.34 | 2.50 | 3.13 | 3.16 | 2.16 | 4.75 | 3.45 |
| H6 | old | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 3.54 | 3.85 | 3.03 | 2.10 | 0.32 | 2.74 | 3.75 | 2.67 | 2.65 | 4.55 | 2.49 | 2.02 | 0.40 |
| H6 | with rotated nulls | 3.14 | 4.20 | 2.70 | 2.43 | 5.09 | 5.15 | 3.54 | 3.85 | 3.03 | 2.10 | 0.32 | 2.74 | 3.75 | 2.67 | 2.65 | 4.55 | 2.49 | 2.02 | 0.40 |

Cross-ratio phase counts (18 distinct statistics) with 9 and 11 nulls:

| view | nulls | LeftOnly ≥3× rms | LeftOnly ≥3× max | RightOnly ≥3× rms | RightOnly ≥3× max | Test ≥3× rms | Test ≥3× max | null files ≥3× rms (leave-one-out), max over files | per null file |
|---|---|---|---|---|---|---|---|---|---|
| band mean 3.2-4.2 GHz | 9 nulls | 12 | 3 | 7 | 3 | 0 | 0 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0 |
| band mean 3.2-4.2 GHz | 11 nulls | 12 | 3 | 7 | 2 | 0 | 0 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0 |
| 3.4 GHz | 9 nulls | 9 | 4 | 8 | 4 | 10 | 5 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0 |
| 3.4 GHz | 11 nulls | 9 | 3 | 8 | 2 | 10 | 4 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0 |
| band mean 3.30-3.65 GHz | 9 nulls | 12 | 7 | 9 | 7 | 7 | 3 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0 |
| band mean 3.30-3.65 GHz | 11 nulls | 11 | 3 | 7 | 3 | 7 | 2 | 0 | H 0, H_new 0, Mild 0, Mild_new 0, Moderate 0, Moderate_c3 0, Severe 0, Severe_c3 0, MCI_c3 0, Null_rot07 0, Null_rot19 0 |

Bias-corrected Moderate FB (round-2 B24) with the rotated nulls' FB added to the floor:

| set | method | FB_rot07 | FB_rot19 | corrected | ratio_old | ratio_new |
|---|---|---|---|---|---|---|
| lobe_A | Tikhonov dS | +2.81 | +0.59 | +6.31 | 1.38 | 1.38 |
| lobe_A | frozen log | +3.01 | -0.06 | +6.41 | 1.58 | 1.58 |
| lobe_A | whitened log | +2.30 | +0.06 | +6.72 | 1.88 | 1.88 |
| lobe_B | Tikhonov dS | +2.83 | +0.51 | +7.42 | 3.21 | 2.61 |
| lobe_B | frozen log | +3.21 | +0.18 | +7.16 | 3.98 | 2.23 |
| lobe_B | whitened log | +2.39 | +0.14 | +6.93 | 3.97 | 2.80 |

**Survival table:**

| claim | old | new | survives |
|---|---|---|---|
| LeftOnly LR_anti vs R1c ruler (Tikhonov dS / whitened log) | 1.93× / 2.76× | 1.93× / 2.76× | yes (unchanged; still 'sensitive at best') |
| RightOnly LR_anti vs R1c ruler | 2.50×–3.37× | 2.50×–3.37× | yes (unchanged) |
| Cross-ratio phases, LeftOnly, band mean (≥3×, rms / max rule) | 12 / 3 of 18 | 12 / 3 of 18 | yes |
| Cross-ratio phases, LeftOnly, 3.30–3.65 GHz | 12 / 7 | 11 / 3 | weakened (max rule 7 → 3) |
| Cross-ratio phases, LeftOnly, 3.4 GHz | 9 / 4 | 9 / 3 | slightly weakened |
| Null files ≥3× (leave-one-out, rms rule), any view | 0 of 18 | 0 of 18 (rotated nulls included) | yes |
| Test_B S2 / S5 vs sector ruler (H7) | 3.50× / 2.55× | 3.50× / 2.55× | yes (unchanged) |
| RightOnly S5 / S6 vs sector ruler (H7) | 3.18× / 4.34× | 3.18× / 4.34× | yes (unchanged) |
| LeftOnly S3 vs sector ruler (H7) | 5.12× | 3.16× | weakened (rot07 S3 = 4.75 raises the ruler), still ≥ 3× |
| Bias-corrected Moderate FB, lobe_B (established 3.2–4.0×) | 3.21×, 3.98×, 3.97× | 2.61×, 2.23×, 2.80× | NO: rot07 FB (+2.3 to +3.2) enters the floor; 'established in lobe_B' → sensitive |
| Left/right reflection asymmetry of LeftOnly (power) | 0.060–0.068 dB vs old nulls ≤ 0.017 | vs all nulls ≤ 0.017 (rotated ≤ 0.011) | yes |
| MCI: nothing beyond the rulers | — | nulls behave like MCI | yes |

Claims that do not use a null floor (field geometry, Born error, λ, references, per-port shares, depth) are not affected. When Null_rot31 and Null_rot43 arrive: add them to `REGISTRY` and to `ROT` in `imaging/lobe_round3.py`, and re-run.

## 7. Rank readings vs the frozen threshold (POST-HOC; not adopted)

Designs: every known lobe design, RightOnly, Test_B, MCI, both rotated nulls and the other healthy file, each against both references (26 cases, 72 truly affected sectors). Primary method. Rules (stated before computing):
- frozen: dε'' > T_abs = 13.81;
- rank (largest gap): sort the six values; k = position of the largest drop; k = 0 if the top value ≤ the frozen T_null = 4.93;
- rank (above midpoint): sectors above ½(max + min), same gate.
The raw-delay row is §8's comparison.

| reading | hits | misses | false_alarms | exact_sets |
|---|---|---|---|---|
| frozen T_abs | 51 | 21 | 0 | 15/26 |
| rank (largest gap, gate T_null) | 58 | 14 | 0 | 20/26 |
| rank (above midpoint, gate T_null) | 60 | 12 | 0 | 22/26 |
| raw delay (centred, largest gap, gate null max) | 43 | 29 | 6 | 14/26 |

| reference | design | truth | frozen T_abs set | rank (largest gap, gate T_null) set | rank (above midpoint, gate T_null) set | raw delay (centred, largest gap, gate null max) set |
|---|---|---|---|---|---|---|
| H7 | Mild_lobe | S2 S3 S5 S6 | S2 S3 S5 S6 | S2 S3 S5 S6 | S2 S3 S5 S6 | S1 S2 S3 S5 S6 |
| H7 | Mild_lobe_new | S2 S3 S5 S6 | S2 S3 S6 | S2 S3 S5 S6 | S2 S3 S5 S6 | S1 S2 S3 S5 S6 |
| H7 | Moderate_lobe | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S6 |
| H7 | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | S1 S3 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 |
| H7 | Severe_lobe | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S3 S6 | S1 S3 S6 | none |
| H7 | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S3 S6 | S1 S3 S6 | none |
| H7 | LeftOnly_test_c3 | S2 S3 | S3 | S2 S3 | S2 S3 | S2 S3 |
| H7 | RightOnly_test | S5 S6 | S5 S6 | S6 | S5 S6 | S1 S5 S6 |
| H7 | Test_B | S2 S5 | S2 | S2 S5 | S2 S5 | S2 S5 |
| H7 | MCI_lobe_c3 | none | none | none | none | none |
| H7 | Null_rot07 | none | none | none | none | none |
| H7 | Null_rot19 | none | none | none | none | none |
| H7 | Healthy_sliced_new | none | none | none | none | none |
| H6 | Mild_lobe | S2 S3 S5 S6 | S2 S3 S6 | S2 S3 S5 S6 | S2 S3 S5 S6 | S1 S2 S3 S5 S6 |
| H6 | Mild_lobe_new | S2 S3 S5 S6 | S2 | S2 S3 S5 S6 | S2 S3 S5 S6 | S1 S2 S3 S5 S6 |
| H6 | Moderate_lobe | S1 S2 S3 S5 S6 | S1 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S5 S6 |
| H6 | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | S1 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 |
| H6 | Severe_lobe | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S3 S6 | S1 S3 S6 | none |
| H6 | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | S1 S3 S6 | S1 S3 S6 | S1 S3 S6 | none |
| H6 | LeftOnly_test_c3 | S2 S3 | none | S2 S3 | S2 S3 | S2 S3 |
| H6 | RightOnly_test | S5 S6 | S5 S6 | S6 | S5 S6 | S1 S5 S6 |
| H6 | Test_B | S2 S5 | none | S2 S5 | S2 S5 | S2 S5 |
| H6 | MCI_lobe_c3 | none | none | none | none | none |
| H6 | Null_rot07 | none | none | none | none | none |
| H6 | Null_rot19 | none | none | none | none | none |
| H6 | Healthy_sliced | none | none | none | none | none |

**Result.** Neither rank rule makes a false alarm. The largest-gap rank reading finds 58 of 72 affected sectors against 51 for the frozen threshold, with 20/26 exact sets against 15/26. Its misses are mainly Severe (all six affected; a gap rule cannot return 'all') and RightOnly (it stops after S6). It would have read Test_B as S2 + S5 against both references. **Not adopted:** the rule was formulated after the Test_B truth was known.

## 8. Is the ranking evidence for the Born pipeline, or only for 'the delay is largest at the antennas over the change'?

Raw statistic per antenna (sector k ↔ antenna Tk): minus the mean phase change, against the reference, of the antenna's two neighbour paths at 3.4 / 3.6 / 3.8 GHz (the same frequencies as the Born fit), with the ring median removed (common CSF_Mild delay). Its gate is the largest centred value of the designs with no cortical change (H7 0.74°, H6 0.89°).

| measure | Born | raw |
|---|---|---|
| top-k with the true k (designs with 1–5 affected sectors) | 1.000 (14/14 perfect) | 0.964 (12/14 perfect) |
| Spearman with the true sector map (designs with a non-flat truth) | 0.71 | 0.79 |
| stated-k reading (largest gap, own null gate): hits / misses / false alarms / exact | 58 / 14 / 0 / 20/26 | 43 / 29 / 6 / 14/26 |

Per design (raw delays as values):

| reference | design | truth | raw delay deg | Born values | Born top-k oracle | raw top-k oracle | Born spearman | raw spearman |
|---|---|---|---|---|---|---|---|---|
| H7 | Mild_lobe | S2 S3 S5 S6 | +0.01, +0.99, -0.07, -2.10, -0.01, +1.05 | +11.4, +20.2, +17.6, +7.6, +16.2, +21.7 | 1.00 | 0.75 | 0.89 | 0.66 |
| H7 | Mild_lobe_new | S2 S3 S5 S6 | -0.48, +0.75, +0.17, -1.71, -0.17, +0.48 | +8.2, +16.0, +15.2, +5.1, +13.7, +16.5 | 1.00 | 1.00 | 0.89 | 0.83 |
| H7 | Moderate_lobe | S1 S2 S3 S5 S6 | +0.42, -0.18, -1.58, -2.93, +0.18, +2.12 | +17.7, +15.1, +16.6, +7.5, +18.6, +20.9 | 1.00 | 1.00 | 0.60 | 0.89 |
| H7 | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | +1.21, +0.61, -0.69, -2.42, -0.61, +1.72 | +16.1, +12.1, +14.3, +5.3, +13.5, +16.4 | 1.00 | 1.00 | 0.71 | 0.94 |
| H7 | Severe_lobe | S1 S2 S3 S4 S5 S6 | -0.37, +0.41, +0.09, -0.69, +0.00, -0.00 | +20.6, +17.4, +19.8, +16.7, +17.7, +21.1 |  |  |  |  |
| H7 | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | +0.11, +0.60, +0.12, -0.43, -0.18, -0.11 | +18.5, +15.5, +18.3, +14.9, +14.8, +18.2 |  |  |  |  |
| H7 | LeftOnly_test_c3 | S2 S3 | -0.02, +2.23, +2.43, +0.02, -0.71, -0.55 | +5.2, +13.1, +15.0, +5.6, +5.0, +6.2 | 1.00 | 1.00 | 0.77 | 0.94 |
| H7 | RightOnly_test | S5 S6 | +0.75, -1.41, -1.54, -0.75, +1.65, +3.02 | +10.7, +9.0, +10.1, +9.2, +16.4, +22.3 | 1.00 | 1.00 | 0.71 | 0.94 |
| H7 | Test_B | S2 S5 | -0.53, +1.33, +0.13, -0.62, +0.99, -0.13 | +4.9, +14.7, +6.5, +4.2, +13.1, +6.5 | 1.00 | 1.00 | 0.43 | 0.37 |
| H7 | MCI_lobe_c3 | none | +0.20, +0.17, -0.04, +0.04, -0.30, -0.36 | +2.5, +3.4, +2.9, +3.4, +2.1, +2.1 |  |  |  |  |
| H7 | Null_rot07 | none | +0.43, +0.60, +0.04, -1.62, -1.53, -0.04 | +3.6, +3.6, +4.7, +0.8, +0.2, +3.7 |  |  |  |  |
| H7 | Null_rot19 | none | +0.34, -0.15, +0.15, -0.45, -0.36, +0.74 | +1.7, +1.4, +3.0, +1.2, +1.0, +3.5 |  |  |  |  |
| H7 | Healthy_sliced_new | none | +0.06, -0.13, -0.06, -0.15, +0.10, +0.39 | +2.2, +2.0, +2.7, +2.2, +2.4, +3.0 |  |  |  |  |
| H6 | Mild_lobe | S2 S3 S5 S6 | -0.01, +1.15, +0.01, -1.92, -0.09, +0.69 | +9.2, +18.2, +14.9, +5.4, +13.8, +18.6 | 1.00 | 0.75 | 0.89 | 0.66 |
| H6 | Mild_lobe_new | S2 S3 S5 S6 | -0.45, +0.97, +0.31, -1.47, -0.18, +0.18 | +6.1, +14.0, +12.4, +2.9, +11.3, +13.5 | 1.00 | 1.00 | 0.83 | 0.66 |
| H6 | Moderate_lobe | S1 S2 S3 S5 S6 | +0.35, -0.06, -1.54, -2.80, +0.06, +1.73 | +15.5, +13.1, +13.9, +5.3, +16.2, +17.9 | 1.00 | 1.00 | 0.60 | 0.89 |
| H6 | Moderate_lobe_c3 | S1 S2 S3 S5 S6 | +1.10, +0.68, -0.68, -2.32, -0.77, +1.28 | +13.9, +10.1, +11.6, +3.1, +11.1, +13.4 | 1.00 | 1.00 | 0.77 | 0.89 |
| H6 | Severe_lobe | S1 S2 S3 S4 S5 S6 | -0.18, +0.78, +0.39, -0.29, +0.14, -0.14 | +18.4, +15.5, +17.1, +14.6, +15.3, +18.1 |  |  |  |  |
| H6 | Severe_lobe_c3 | S1 S2 S3 S4 S5 S6 | +0.17, +0.84, +0.29, -0.17, -0.18, -0.39 | +16.3, +13.6, +15.6, +12.7, +12.4, +15.2 |  |  |  |  |
| H6 | LeftOnly_test_c3 | S2 S3 | -0.13, +2.31, +2.44, +0.13, -0.86, -0.98 | +3.0, +11.1, +12.3, +3.4, +2.6, +3.2 | 1.00 | 1.00 | 0.89 | 0.89 |
| H6 | RightOnly_test | S5 S6 | +0.65, -1.32, -1.53, -0.65, +1.49, +2.59 | +8.5, +7.0, +7.4, +7.0, +13.9, +19.3 | 1.00 | 1.00 | 0.60 | 0.94 |
| H6 | Test_B | S2 S5 | -0.45, +1.60, +0.32, -0.32, +1.03, -0.37 | +2.8, +12.7, +3.8, +2.0, +10.7, +3.5 | 1.00 | 1.00 | 0.37 | 0.54 |
| H6 | MCI_lobe_c3 | none | +0.06, +0.22, -0.06, +0.12, -0.48, -0.82 | +0.4, +1.4, +0.2, +1.2, -0.3, -0.8 |  |  |  |  |
| H6 | Null_rot07 | none | +0.54, +0.89, +0.26, -1.31, -1.47, -0.26 | +1.4, +1.6, +2.0, -1.4, -2.2, +0.7 |  |  |  |  |
| H6 | Null_rot19 | none | +0.20, -0.12, +0.12, -0.39, -0.56, +0.26 | -0.4, -0.6, +0.2, -1.0, -1.4, +0.4 |  |  |  |  |
| H6 | Healthy_sliced | none | -0.06, +0.13, +0.06, +0.15, -0.10, -0.39 | -2.2, -2.0, -2.7, -2.2, -2.4, -3.0 |  |  |  |  |

**Verdict: CHANGED (the ranking is not evidence for the Born pipeline).** With the number of affected sectors given, the raw neighbour-path delay ranks them almost as well (0.96 vs 1.00). It correlates with the true map as well or better (0.79 vs 0.71); its only misses are Mild_lobe (4 affected; raw ranks the unaffected S1 above an affected sector). So the ranking mostly re-expresses 'the phase delay is largest at the antennas over the change'.
Where the Born map does add something is a calibrated level. With stated rules it gives fewer false alarms (0 vs 6) and more exact sets (20/26 vs 14/26), because the centred raw delay of the healthy-like designs reaches 0.89°, comparable to Test_B's S5 (≈ 1.0°).

## 9. Pass gap (0.3a): LeftOnly (pass 6) vs mirrored RightOnly (pass 5), against the three pass-5/pass-6 twins

Same statistics and frequencies (3.4/3.6/3.8 GHz) for Left − mirror(Right) and for each twin (p6 − p5): LR, LR_anti, its amplitude and phase parts, phase share, the mean of the two affected sectors, and the common-mode neighbour-path delay.

| reference | method | Left−mirRight LR | twins max abs Δ LR | Left−mirRight LR_anti | twins max abs Δ LR_anti | Left−mirRight LR_amp | twins max abs Δ LR_amp | Left−mirRight LR_phase | twins max abs Δ LR_phase | common-mode delay Left / mirRight deg | Left−mirRight common-mode delay deg | twins max abs Δ common-mode delay deg | phase share Left | phase share mirRight | affected-sector mean Left / mirRight | relative Δ affected sectors (Left−mirRight) | twins relative Δ affected sectors (p6 − p5) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | Tikhonov dS | -2.04 | +2.18 | -2.31 | +2.14 | -0.33 | +0.69 | -1.67 | +2.04 | 4.66 / 8.99 | -4.33 | +3.30 | +0.82 | +0.82 | 14.06 / 19.37 | -0.38 | -0.19, -0.19, -0.12 |
| H7 | frozen log | -1.92 | +2.42 | -2.34 | +2.38 | -0.58 | +0.61 | -1.34 | +2.06 | 4.66 / 8.99 | -4.33 | +3.30 | +0.88 | +0.85 | 14.04 / 18.00 | -0.28 | -0.13, -0.14, -0.08 |
| H7 | whitened log | -1.70 | +1.85 | -1.89 | +1.98 | -0.60 | +0.61 | -1.10 | +1.53 | 4.66 / 8.99 | -4.33 | +3.30 | +0.86 | +0.82 | 13.58 / 16.65 | -0.23 | -0.11, -0.12, -0.06 |
| H6 | Tikhonov dS | -2.05 | +2.14 | -2.29 | +2.12 | -0.30 | +0.68 | -1.68 | +2.04 | 2.94 / 7.27 | -4.33 | +3.30 | +0.85 | +0.85 | 11.71 / 17.03 | -0.45 | -0.22, -0.22, -0.13 |
| H6 | frozen log | -1.94 | +2.44 | -2.38 | +2.38 | -0.59 | +0.63 | -1.36 | +2.08 | 2.94 / 7.27 | -4.33 | +3.30 | +0.88 | +0.85 | 12.57 / 16.63 | -0.32 | -0.15, -0.16, -0.09 |
| H6 | whitened log | -1.75 | +1.86 | -1.94 | +1.97 | -0.61 | +0.64 | -1.14 | +1.52 | 2.94 / 7.27 | -4.33 | +3.30 | +0.87 | +0.83 | 12.22 / 15.41 | -0.26 | -0.12, -0.14, -0.07 |

**Result.** LR, LR_anti, amplitude and phase parts: |Left − mirRight| is at most 1.08× the largest twin difference. Primary method, H7: LR -2.04 vs ≤ 2.18; LR_anti -2.31 vs ≤ 2.14. The phase share is the same (0.82 vs 0.82).
Two size measures are outside the twins. The common-mode delay is 4.66 / 8.99° (difference -4.33° vs twins ≤ 3.30°). The affected-sector level differs by -38% vs twins -0.19, -0.19, -0.12.
**Verdict (revised in round 4, ruler language).** Ratio to the largest of the n = 3 twin differences: common-mode delay 1.31×; affected-sector level 1.86–2.06× over methods and references; LR, LR_anti and their parts ≤ 1.08×. Even a value beyond all three twins has a rank p of 1/4. On the bar used everywhere else (≥ 3× established, 2–3× sensitive, < 2× not separable): LR and phase share are **not separable from the pass gap**. The common-mode delay (1.31×) is **undetermined**. The sector level reaches the 2× bar in 3 of 6 method × reference cases (frozen log H7 2.01×, Tikhonov dS H6 2.06×, frozen log H6 2.02×), and only at the threshold of 'sensitive', so it is **undetermined**. Round 3's 'not explained by the pass gap' was stronger than three twins can support.

## Final table

| item | verdict | change | evidence |
|---|---|---|---|
| Test_B (committed reading) | MISS (as scored) | affected none / possible S2 vs truth S2+S5; ranking S2 > S5 correct | testb_report.md; this file §1 |
| Nulls as targets | CONFIRMED | no sector ≥ T_abs (max 4.75); LR ≤ 0.73×, FB ≤ 0.73× rulers | lobe_round3.json: nulls_rows |
| 'Beyond all nulls, p ≈ 0.01' | CONFIRMED (this statistic) | rotated nulls +1.41/-0.96 inside the old envelope 4.07; pair p ≈ 0.007 (11 nulls) | lobe_round3.json: anti |
| User's 0.3(b) numbers | CONFIRMED (verified) | rotated nulls exceed the old floor on 2nd-neighbour power and single-path phase; not on reflections or LR_anti | lobe_round3.json: pairs, ring |
| Rulers rebuilt (11 nulls) | CHANGED (one claim falls) | bias-corrected FB in lobe_B 3.2–4.0× → 2.61×, 2.23×, 2.80×; others survive; phase counts at 3.30–3.65 weakened | lobe_round3.json: rulers, cr, b24 |
| Rank reading vs threshold | reported, not adopted | frozen 51 hits / 0 FA / 15/26 exact; largest-gap 58 / 0 / 20/26 | lobe_round3.json: readings |
| Born ranking vs raw delay | CHANGED | ranking credited to the Born map → raw delay ranks as well (oracle 0.96 vs 1.00; Spearman 0.79 vs 0.71); Born adds only the gated level | lobe_round3.json: readings |
| Pass gap, LR and phase share | not separable from the pass gap | abs Δ ≤ 1.08× the twins; phase share equal | lobe_round3.json: pass_gap |
| Pass gap, absolute level | undetermined (revised in round 4) | common-mode delay 1.31× the largest of 3 twins; sector level 1.86–2.06×; round 3 said 'not explained' | lobe_round3.json: pass_gap |

