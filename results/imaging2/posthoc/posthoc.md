# POST HOC analyses after the Test_B truth (imaging2)

Code cc46f76+imaging2-uncommitted. **Everything in this file is post hoc.** Committed estimates, the blind protocol (595e9cb), its verdict (PASS, f88236c), thresholds and predictions are unchanged.

## 0. New files (imaging2 set file: `results/imaging2/sets.csv`)

| design | file | role | passes | final ΔS | elements | glitch-masked points |
|---|---|---|---|---|---|---|
| RightOnly | `new_with_slices_RightOnly_test.s6p` | replication | 5 | 0.019742 | 789,241 | 0 |
| Test_B | `new_with_slices_Test_B.s6p` | blind (scored) | 6 | 0.012597 | 903,758 | 3 |
| rot07 | `new_with_slices_Null_rot07.s6p` | null (healthy rotated 7 deg) | 6 | 0.01465 | 1,045,101 | 2 |
| rot19 | `new_with_slices_Null_rot19.s6p` | null (healthy rotated 19 deg) | 6 | 0.014495 | 939,082 | 1 |

## A. Rotated nulls as targets (training = every lobe design; nulls never in training)

| run | stage (P) | lobes called | P(affected) S1…S6 | fit |
|---|---|---|---|---|
| rot07 vs H6 [standard] | Healthy (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.30 |
| rot07 vs H6 [gainfree] | Healthy (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.34 |
| rot07 vs H7 [standard] | Healthy (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.59 |
| rot07 vs H7 [gainfree] | Mild (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 0.70 |
| rot19 vs H6 [standard] | Healthy (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 1.39 |
| rot19 vs H6 [gainfree] | Healthy (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 1.55 |
| rot19 vs H7 [standard] | Healthy (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 1.89 |
| rot19 vs H7 [gainfree] | Healthy (1.00) | none | 0.00 / 0.00 / 0.00 / 0.00 / 0.00 / 0.00 | 2.01 |

## B. Each rotated null as the healthy reference

| run | stage (P) | lobes called | ê S1…S6 (mm) | fit |
|---|---|---|---|---|
| Test_B vs rot07 [standard] | Mild (1.00) | S2 TL, S5 PR | 0.0 / 16.0 / 0.0 / 0.0 / 12.0 / 0.0 | 0.66 |
| Test_B vs rot07 [gainfree] | Mild (1.00) | S2 TL, S5 PR | 0.0 / 12.0 / 0.0 / 0.0 / 6.0 / 0.0 | 1.05 |
| Test_B vs rot19 [standard] | Moderate (1.00) | S2 TL, S5 PR | 0.0 / 7.5 / 0.0 / 0.0 / 7.5 / 0.0 | 1.63 |
| Test_B vs rot19 [gainfree] | Mild (1.00) | S2 TL, S5 PR | 0.0 / 11.0 / 0.0 / 0.0 / 12.0 / 0.0 | 1.73 |
| LeftOnly vs rot07 [standard] | Mild (1.00) | S2 TL, S3 PL | 0.0 / 9.0 / 6.5 / 0.0 / 0.0 / 0.0 | 0.51 |
| LeftOnly vs rot07 [gainfree] | Mild (1.00) | S2 TL, S3 PL | 0.0 / 1.0 / 1.0 / 0.0 / 0.0 / 0.0 | 1.07 |
| LeftOnly vs rot19 [standard] | Moderate (1.00) | S2 TL, S3 PL | 0.0 / 0.5 / 6.5 / 0.0 / 0.0 / 0.0 | 1.40 |
| LeftOnly vs rot19 [gainfree] | Moderate (1.00) | S2 TL, S3 PL | 0.0 / 0.5 / 1.0 / 0.0 / 0.0 / 0.0 | 1.41 |
| RightOnly vs rot07 [standard] | Mild (1.00) | S5 PR, S6 TR | 0.0 / 0.0 / 0.0 / 0.0 / 3.0 / 3.5 | 0.64 |
| RightOnly vs rot07 [gainfree] | Mild (1.00) | S2 TL, S5 PR, S6 TR | 0.0 / 1.5 / 0.0 / 0.0 / 3.0 / 3.0 | 0.86 |
| RightOnly vs rot19 [standard] | Moderate (1.00) | S5 PR, S6 TR | 0.0 / 0.0 / 0.0 / 0.0 / 9.0 / 4.0 | 1.19 |
| RightOnly vs rot19 [gainfree] | Severe (1.00) | S6 TR | 0.0 / 0.0 / 0.0 / 0.0 / 0.0 / 0.5 | 1.88 |

## C. Pass gap: RightOnly vs mirror(LeftOnly) against the three pass-5 vs pass-6 twins

Same statistics, same frequencies: per path class, rms and band mean of the complex log-ratio between the two solves (amplitude dB, phase °). 'within' = |RightOnly − mirror(LeftOnly)| ≤ the largest of the three 5-vs-6 twins.

**3.2-4.2 GHz**

| statistic | RO − mirror(LO) | twins 5 vs 6 (min–max) | / twin max | within |
|---|---|---|---|---|
| reflection rms_dB | 0.286 | 0.208–0.231 | 1.24 | **no** |
| reflection rms_deg | 1.871 | 1.359–1.499 | 1.25 | **no** |
| reflection mean_dB | 0.104 | 0.089–0.099 | 1.05 | **no** |
| reflection mean_deg | 0.452 | 0.388–0.399 | 1.13 | **no** |
| neighbour rms_dB | 0.227 | 0.121–0.199 | 1.14 | **no** |
| neighbour rms_deg | 3.757 | 2.765–2.979 | 1.26 | **no** |
| neighbour mean_dB | 0.063 | 0.013–0.048 | 1.31 | **no** |
| neighbour mean_deg | 3.049 | 2.368–2.525 | 1.21 | **no** |
| second-neighbour rms_dB | 0.716 | 0.352–0.562 | 1.27 | **no** |
| second-neighbour rms_deg | 6.240 | 4.282–4.881 | 1.28 | **no** |
| second-neighbour mean_dB | 0.024 | 0.019–0.047 | 0.51 | yes |
| second-neighbour mean_deg | 3.874 | 3.094–3.442 | 1.13 | **no** |
| opposite rms_dB | 0.474 | 0.246–0.449 | 1.06 | **no** |
| opposite rms_deg | 4.255 | 3.529–4.397 | 0.97 | yes |
| opposite mean_dB | 0.026 | 0.011–0.038 | 0.67 | yes |
| opposite mean_deg | 3.248 | 2.661–2.749 | 1.18 | **no** |

**3.30-3.65 GHz**

| statistic | RO − mirror(LO) | twins 5 vs 6 (min–max) | / twin max | within |
|---|---|---|---|---|
| reflection rms_dB | 0.394 | 0.262–0.308 | 1.28 | **no** |
| reflection rms_deg | 2.264 | 1.476–1.823 | 1.24 | **no** |
| reflection mean_dB | 0.178 | 0.131–0.149 | 1.20 | **no** |
| reflection mean_deg | 0.212 | 0.261–0.490 | 0.43 | yes |
| neighbour rms_dB | 0.161 | 0.102–0.120 | 1.35 | **no** |
| neighbour rms_deg | 3.127 | 2.295–2.411 | 1.30 | **no** |
| neighbour mean_dB | 0.100 | 0.061–0.083 | 1.21 | **no** |
| neighbour mean_deg | 2.812 | 2.152–2.334 | 1.20 | **no** |
| second-neighbour rms_dB | 0.431 | 0.155–0.311 | 1.39 | **no** |
| second-neighbour rms_deg | 4.088 | 3.057–3.884 | 1.05 | **no** |
| second-neighbour mean_dB | 0.057 | 0.010–0.104 | 0.55 | yes |
| second-neighbour mean_deg | 3.114 | 2.810–3.597 | 0.87 | yes |
| opposite rms_dB | 0.288 | 0.151–0.252 | 1.14 | **no** |
| opposite rms_deg | 4.768 | 3.726–4.118 | 1.16 | **no** |
| opposite mean_dB | 0.031 | 0.023–0.071 | 0.44 | yes |
| opposite mean_deg | 4.391 | 2.914–3.803 | 1.15 | **no** |

Model-free ring of each pair (per-antenna neighbour-path phase difference, 3.30–3.65 GHz): mean and spread (°)

| pair | T1…T6 | mean | spread |
|---|---|---|---|
| RightOnly vs mirror(LeftOnly) (5 vs 6) | 3.46 / 2.11 / 2.27 / 2.38 / 2.70 / 3.95 | +2.81 | 1.84 |
| Mild 5 vs 6 | 2.43 / 2.22 / 2.07 / 2.39 / 2.50 / 2.39 | +2.33 | 0.43 |
| Moderate 5 vs 6 | 1.99 / 1.83 / 1.70 / 1.91 / 2.83 / 2.79 | +2.17 | 1.13 |
| Severe 5 vs 6 | 2.08 / 2.27 / 2.08 / 2.13 / 2.30 / 2.06 | +2.15 | 0.24 |
| Healthy 6 vs 7 (context) | 1.39 / 1.25 / 1.40 / 1.43 / 1.53 / 1.64 | +1.44 | 0.39 |
| rot07 vs H6 (context, 6 vs 6) | 0.80 / 0.74 / 0.54 / -0.52 / -0.62 / 0.50 | +0.24 | 1.42 |
| rot19 vs H6 (context, 6 vs 6) | 0.80 / 0.87 / 1.21 / 0.68 / 0.53 / 1.00 | +0.85 | 0.68 |

Signal size: rms of the change against H6, second solve / first solve (RightOnly / mirrored LeftOnly; pass-5 / pass-6 for the twins). 1.00 = same size.

| pair | reflection amp / phase | neighbour amp / phase | second-neighbour amp / phase | opposite amp / phase |
|---|---|---|---|---|
| RightOnly / LeftOnly (5 / 6) | 1.76 / 1.75 | 1.33 / 1.74 | 1.21 / 1.03 | 1.04 / 1.29 |
| Mild 5 / 6 | 1.50 / 1.49 | 1.17 / 1.43 | 1.01 / 1.00 | 0.85 / 1.18 |
| Moderate 5 / 6 | 1.33 / 1.33 | 1.17 / 1.31 | 0.99 / 0.95 | 0.97 / 0.78 |
| Severe 5 / 6 | 1.15 / 1.15 | 1.12 / 1.15 | 0.93 / 1.04 | 1.01 / 0.87 |

Reconstruction: |ê(second solve) − ê(first solve)| per sector (mm; committed primary runs).

| pair | S1…S6 | max |
|---|---|---|
| RightOnly vs mirror(LeftOnly) | 0.0 / 0.0 / 0.0 / 0.0 / 8.5 / 8.0 | 8.5 |
| Mild 5 vs 6 | 1.0 / 0.0 / 1.5 / 0.0 / 2.5 / 5.5 | 5.5 |
| Moderate 5 vs 6 | 6.5 / 1.0 / 1.5 / 0.0 / 2.0 / 1.0 | 6.5 |
| Severe 5 vs 6 | 0.0 / 0.0 / 0.0 / 0.0 / 2.0 / 8.5 | 8.5 |

## D. Rulers rebuilt with the rotated nulls (R1c: floor = largest |null|; ≥ 3x established, 2–3x sensitive, < 2x not separable)

**Reconstruction statistics.**

- LR_e (ê left − right): floor old 9.25 → new 9.25 mm (rotated nulls: rot07 +0.00, rot19 +0.00).
  - LeftOnly_p6: +11.50 mm → 1.24x old, 1.24x new
  - RightOnly (primary): -3.25 mm → 0.35x old, 0.35x new
  - Test_B (primary): +3.00 mm → 0.32x old, 0.32x new
- One-sided call patterns among nulls: old 0/9; rotated nulls one-sided: {'rot07': False, 'rot19': False}; lobes called in the rotated nulls: {'rot07': 0, 'rot19': 0}.

**Model-free ring statistics** (vs the matched healthy reference; 3.30–3.65 GHz window is itself post hoc).

- ring LR contrast (left T2,T3 - right T5,T6), deg: floor old 0.91 → new 0.91; nulls H7 vs H6 +0.26, H6 vs H7 -0.26, MCI vs H6 +0.34, Mild5 vs H6 +0.06, Mild6 vs H7 +0.11, Mod5 vs H6 -0.91, Mod6 vs H7 -0.12, Sev5 vs H6 +0.70, Sev6 vs H7 +0.45, rot07 vs H6 +0.69, rot19 vs H6 +0.28
  - LeftOnly vs H6: +4.44 → 4.87x old, **4.87x new**
  - RightOnly vs H6: -4.60 → 5.05x old, **5.05x new**
  - Test_B vs H6: +0.43 → 0.47x old, **0.47x new**
- ring spread (max - min), deg: floor old 0.41 → new 1.42; nulls H7 vs H6 +0.39, H6 vs H7 +0.39, MCI vs H6 +0.41, rot07 vs H6 +1.42, rot19 vs H6 +0.68
  - Test_B vs H6: +2.11 → 5.12x old, **1.49x new**
- ring diagonal-pair elevation (largest of 3 pairs), deg: floor old 0.12 → new 0.42; nulls H7 vs H6 +0.08, H6 vs H7 +0.12, MCI vs H6 +0.12, rot07 vs H6 +0.42, rot19 vs H6 +0.39
  - Test_B vs H6: +1.57 → 12.76x old, **3.73x new**
- ring T2,T5 elevation (Test_B's pair, chosen after seeing it), deg: floor old 0.08 → new 0.27; nulls H7 vs H6 +0.08, H6 vs H7 -0.08, MCI vs H6 -0.00, rot07 vs H6 -0.27, rot19 vs H6 -0.22
  - Test_B vs H6: +1.57 → 20.89x old, **5.79x new**

## E. Noise model with every solve-to-solve offset, coverage before / after

Twin samples (each taken as one sample of an observation's solve-to-solve error; the target's own twin excluded): rms per path class:

| twin | refl dB / ° | neighbour dB / ° | 2nd-nb dB / ° | opposite dB / ° |
|---|---|---|---|---|
| H7/H6 (7 vs 6 passes) | 0.19 / 1.2 | 0.09 / 1.6 | 0.40 / 3.2 | 0.35 / 3.0 |
| rot07/H6 (6 vs 6, rotated mesh) | 0.15 / 1.0 | 0.15 / 1.1 | 0.54 / 3.3 | 0.50 / 2.2 |
| rot19/H6 (6 vs 6, rotated mesh) | 0.29 / 1.9 | 0.22 / 1.5 | 0.96 / 6.0 | 0.82 / 8.0 |
| Mild 5/6 | 0.23 / 1.5 | 0.12 / 2.9 | 0.50 / 4.8 | 0.45 / 4.4 |
| Moderate 5/6 | 0.22 / 1.4 | 0.14 / 2.8 | 0.35 / 4.3 | 0.25 / 3.5 |
| Severe 5/6 | 0.21 / 1.4 | 0.20 / 3.0 | 0.56 / 4.9 | 0.43 / 4.3 |
| RightOnly/mirror(LeftOnly) (5 vs 6) | 0.29 / 1.9 | 0.23 / 3.8 | 0.72 / 6.2 | 0.47 / 4.3 |

| | sectors | 90% coverage, all sectors | affected sectors | 90% coverage, affected | lobe calls correct |
|---|---|---|---|---|---|
| before (committed noise model) | 66 | 83% | 36 | 69% | 98% |
| after (+ solve-to-solve offsets) | 66 | 88% | 36 | 78% | 100% |

Targets: 9 leave-one-out designs + RightOnly + Test_B (primary variant).

| target (after) | stage | lobes called | ê S1…S6 [90%] | fit |
|---|---|---|---|---|
| Healthy_p7 | Healthy (1.00) | none | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.16 |
| Mild_p5 | Mild (1.00) | S2 TL, S3 PL, S5 PR, S6 TR | 0.0 [0.0–1.0] / 8.5 [3.5–16.5] / 15.0 [8.5–21.5] / 0.0 [0.0–0.0] / 12.5 [3.5–21.5] / 12.5 [8.0–21.0] | 0.56 |
| Mild_p6 | Mild (1.00) | S2 TL, S3 PL, S5 PR, S6 TR | 0.0 [0.0–0.0] / 9.0 [8.0–20.0] / 15.0 [8.0–21.5] / 0.0 [0.0–0.0] / 14.0 [8.0–21.5] / 14.0 [8.0–21.5] | 0.31 |
| Moderate_p5 | Moderate (1.00) | S1 Fr, S2 TL, S3 PL, S5 PR, S6 TR | 12.5 [5.0–21.0] / 13.0 [4.5–21.5] / 13.0 [5.0–21.0] / 0.0 [0.0–0.0] / 13.0 [5.5–21.5] / 13.0 [5.0–21.0] | 0.20 |
| Moderate_p6 | Moderate (1.00) | S1 Fr, S2 TL, S3 PL, S5 PR, S6 TR | 7.0 [0.5–20.5] / 13.0 [5.0–21.5] / 12.0 [2.0–21.0] / 0.0 [0.0–0.0] / 11.5 [1.5–21.0] / 12.5 [5.0–21.0] | 0.19 |
| Severe_p5 | Severe (1.00) | S1 Fr, S2 TL, S3 PL, S4 Oc, S5 PR, S6 TR | 1.0 [1.0–1.5] / 2.0 [1.5–2.5] / 2.0 [1.5–19.5] / 1.0 [0.5–11.5] / 2.5 [1.5–19.0] / 1.5 [1.0–18.5] | 1.28 |
| Severe_p6 | Severe (1.00) | S1 Fr, S2 TL, S3 PL, S4 Oc, S5 PR, S6 TR | 1.5 [1.0–2.5] / 2.0 [1.0–9.0] / 2.0 [1.0–19.0] / 1.0 [0.5–19.0] / 10.0 [1.5–21.0] / 8.5 [1.0–21.0] | 1.16 |
| LeftOnly_p6 | Mild (1.00) | S2 TL, S3 PL | 0.0 [0.0–0.0] / 13.5 [5.5–21.0] / 12.5 [5.5–21.5] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.26 |
| MCI_p6 | Healthy (1.00) | none | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.21 |
| RightOnly | Mild (0.99) | S5 PR, S6 TR | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 3.0 [2.5–17.0] / 3.5 [3.0–4.0] | 0.35 |
| Test_B | Mild (1.00) | S2 TL, S5 PR | 0.0 [0.0–0.0] / 13.5 [7.0–21.5] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 7.5 [6.5–20.5] / 0.0 [0.0–0.0] | 0.26 |

**Challenge: P(affected) with the augmented noise model**

| run | P(affected) S1…S6 | lobes called |
|---|---|---|
| RightOnly standard vs H6 | 0.00 / 0.01 / 0.00 / 0.00 / 1.00 / 1.00 | S5 PR, S6 TR |
| RightOnly gainfree vs H6 | 0.12 / 1.00 / 0.67 / 0.05 / 1.00 / 1.00 | S2 TL, S3 PL, S5 PR, S6 TR |
| RightOnly standard vs H7 | 0.69 / 0.14 / 0.24 / 0.07 / 1.00 / 1.00 | S1 Fr, S5 PR, S6 TR |
| Test_B standard vs H6 | 0.00 / 1.00 / 0.00 / 0.00 / 1.00 / 0.00 | S2 TL, S5 PR |
| Test_B gainfree vs H6 | 0.00 / 1.00 / 0.00 / 0.00 / 1.00 / 0.00 | S2 TL, S5 PR |
| Test_B standard vs H7 | 0.00 / 1.00 / 0.00 / 0.00 / 1.00 / 0.00 | S2 TL, S5 PR |

Calibration of confident calls (P ≥ 0.99 or ≤ 0.01): before 1 wrong of 84 (all calls: 5 wrong of 90); after 1 of 82 (all: 3 of 90).

## F. Ring-mean-phase variant (phase ring mean of every path class removed at every frequency)

| target | noise | stage (P) | P(stage) Healthy/Mild/Moderate/Severe | lobes called | ê S1…S6 [90%] | fit |
|---|---|---|---|---|---|---|
| Test_B | ringphase (fold noise) | Mild (1.00) | 0.00 / 1.00 / 0.00 / 0.00 | S2 TL, S5 PR | 0.0 [0.0–0.0] / 8.0 [7.5–20.5] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 7.0 [7.0–16.5] / 0.0 [0.0–0.0] | 0.37 |
| Test_B | ringphase (augmented noise) | Mild (1.00) | 0.00 / 1.00 / 0.00 / 0.00 | S2 TL, S5 PR | 0.0 [0.0–0.0] / 12.5 [7.0–21.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 8.0 [7.0–20.5] / 0.0 [0.0–0.0] | 0.22 |
| RightOnly | ringphase (fold noise) | Mild (1.00) | 0.00 / 1.00 / 0.00 / 0.00 | S5 PR, S6 TR | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 13.5 [4.5–21.0] / 3.5 [3.5–4.0] | 0.43 |
| RightOnly | ringphase (augmented noise) | Mild (1.00) | 0.00 / 1.00 / 0.00 / 0.00 | S5 PR, S6 TR | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 13.5 [3.5–21.5] / 4.0 [3.5–10.0] | 0.28 |
| LeftOnly_p6 | ringphase (fold noise) | Mild (1.00) | 0.00 / 1.00 / 0.00 / 0.00 | S2 TL, S3 PL | 0.0 [0.0–0.0] / 15.0 [6.0–21.5] / 15.0 [7.5–21.5] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.32 |
| Healthy_p7 | ringphase (fold noise) | Healthy (1.00) | 1.00 / 0.00 / 0.00 / 0.00 | none | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.13 |
| MCI_p6 | ringphase (fold noise) | Healthy (1.00) | 1.00 / 0.00 / 0.00 / 0.00 | none | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.30 |
| rot07 | ringphase (fold noise) | Healthy (1.00) | 1.00 / 0.00 / 0.00 / 0.00 | none | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.29 |
| rot19 | ringphase (fold noise) | Healthy (1.00) | 1.00 / 0.00 / 0.00 / 0.00 | none | 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] / 0.0 [0.0–0.0] | 0.89 |
| Mild_p5 | ringphase (fold noise) | Mild (1.00) | 0.00 / 1.00 / 0.00 / 0.00 | S2 TL, S3 PL, S5 PR, S6 TR | 0.0 [0.0–0.0] / 9.0 [8.5–14.5] / 16.0 [10.0–22.0] / 0.0 [0.0–0.0] / 16.5 [9.0–21.5] / 14.5 [8.5–21.5] | 0.68 |
| Moderate_p5 | ringphase (fold noise) | Moderate (1.00) | 0.00 / 0.00 / 1.00 / 0.00 | S1 Fr, S2 TL, S3 PL, S5 PR, S6 TR | 13.0 [5.0–21.5] / 13.0 [4.0–21.5] / 13.5 [5.0–21.5] / 0.0 [0.0–0.0] / 13.0 [4.5–21.5] / 12.5 [4.5–21.0] | 0.29 |
| Severe_p5 | ringphase (fold noise) | Severe (1.00) | 0.00 / 0.00 / 0.00 / 1.00 | S1 Fr, S2 TL, S3 PL, S4 Oc, S5 PR, S6 TR | 0.5 [0.5–7.5] / 13.5 [2.5–21.5] / 13.0 [4.0–21.5] / 0.5 [0.5–20.0] / 13.5 [4.5–21.0] / 8.5 [0.5–20.5] | 1.87 |
