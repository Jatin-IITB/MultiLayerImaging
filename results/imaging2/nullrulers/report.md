# Rotated-null rulers (POST HOC; protocol `ROTATED_NULLS_PROTOCOL.md`)

Code 79ed048. Rotated nulls present: rot07, rot19.

## 0. Common-mode vs scattered differences per path class

Per path: band-power difference (dB) and band-mean phase difference (°) between the two files. Per class: mean, SD and range over its 6 paths; common-mode fraction cm = mean² / (mean² + SD²). Classification (fixed in the protocol): common-mode if cm ≥ 0.8, scattered if cm < 0.5, mixed otherwise, negligible if every path is within ±0.05 dB (±0.5°).

### 3.30-3.65 GHz

| pair | class | band power: mean ± SD [min, max] dB | cm | class. | mean of dB: mean ± SD [min, max] | cm | class. | phase: mean ± SD [min, max] ° | cm | class. |
|---|---|---|---|---|---|---|---|---|---|---|
| rot07 vs H6 | neighbour (k=1) | -0.01 ± 0.14 [-0.19, +0.21] | 0.01 | scattered | -0.00 ± 0.12 [-0.17, +0.19] | 0.00 | scattered | -0.24 ± 0.76 [-0.88, +1.36] | 0.09 | scattered |
| rot07 vs H6 | second-neighbour (k=2) | +0.05 ± 0.12 [-0.10, +0.20] | 0.17 | scattered | +0.05 ± 0.19 [-0.21, +0.31] | 0.06 | scattered | +0.27 ± 1.84 [-1.69, +2.85] | 0.02 | scattered |
| rot07 vs H6 | opposite (k=3) | +0.03 ± 0.05 [-0.04, +0.08] | 0.26 | scattered | +0.02 ± 0.05 [-0.04, +0.06] | 0.20 | scattered | -0.25 ± 0.34 [-0.58, +0.22] | 0.35 | scattered |
| rot19 vs H6 | neighbour (k=1) | +0.22 ± 0.12 [+0.08, +0.38] | 0.77 | mixed | +0.20 ± 0.09 [+0.09, +0.33] | 0.82 | common-mode | -0.85 ± 0.52 [-1.52, +0.17] | 0.72 | mixed |
| rot19 vs H6 | second-neighbour (k=2) | -0.31 ± 0.23 [-0.54, +0.12] | 0.65 | mixed | -0.55 ± 0.33 [-0.90, +0.02] | 0.73 | mixed | -2.28 ± 2.28 [-5.28, +2.04] | 0.50 | scattered |
| rot19 vs H6 | opposite (k=3) | +0.31 ± 0.06 [+0.26, +0.40] | 0.96 | common-mode | +0.32 ± 0.06 [+0.27, +0.41] | 0.96 | common-mode | -3.07 ± 1.11 [-3.97, -1.51] | 0.89 | common-mode |
| rot07 vs rot19 | neighbour (k=1) | -0.23 ± 0.16 [-0.44, +0.04] | 0.69 | mixed | -0.20 ± 0.11 [-0.34, -0.04] | 0.78 | mixed | +0.61 ± 0.56 [-0.11, +1.20] | 0.54 | mixed |
| rot07 vs rot19 | second-neighbour (k=2) | +0.36 ± 0.17 [+0.06, +0.59] | 0.83 | common-mode | +0.60 ± 0.21 [+0.20, +0.84] | 0.89 | common-mode | +2.11 ± 1.50 [-0.03, +3.91] | 0.66 | mixed |
| rot07 vs rot19 | opposite (k=3) | -0.28 ± 0.12 [-0.45, -0.20] | 0.86 | common-mode | -0.30 ± 0.11 [-0.46, -0.22] | 0.88 | common-mode | +2.84 ± 0.77 [+1.75, +3.44] | 0.93 | common-mode |
| Mild 5 vs 6 | neighbour (k=1) | +0.07 ± 0.03 [+0.03, +0.11] | 0.87 | common-mode | +0.08 ± 0.02 [+0.04, +0.10] | 0.93 | common-mode | -2.33 ± 0.21 [-2.60, -1.97] | 0.99 | common-mode |
| Mild 5 vs 6 | second-neighbour (k=2) | -0.00 ± 0.13 [-0.19, +0.21] | 0.00 | scattered | -0.04 ± 0.17 [-0.32, +0.22] | 0.05 | scattered | -3.60 ± 0.69 [-4.64, -2.72] | 0.96 | common-mode |
| Mild 5 vs 6 | opposite (k=3) | +0.04 ± 0.09 [-0.07, +0.14] | 0.17 | scattered | +0.06 ± 0.09 [-0.06, +0.16] | 0.28 | scattered | -3.81 ± 0.37 [-4.19, -3.31] | 0.99 | common-mode |
| Moderate 5 vs 6 | neighbour (k=1) | +0.08 ± 0.04 [+0.02, +0.14] | 0.79 | mixed | +0.08 ± 0.03 [+0.02, +0.12] | 0.85 | common-mode | -2.17 ± 0.60 [-3.38, -1.54] | 0.93 | common-mode |
| Moderate 5 vs 6 | second-neighbour (k=2) | +0.03 ± 0.04 [-0.02, +0.07] | 0.35 | scattered | +0.01 ± 0.05 [-0.07, +0.07] | 0.04 | scattered | -2.81 ± 0.59 [-3.71, -1.92] | 0.96 | common-mode |
| Moderate 5 vs 6 | opposite (k=3) | +0.01 ± 0.05 [-0.03, +0.08] | 0.02 | scattered | +0.02 ± 0.05 [-0.02, +0.10] | 0.16 | scattered | -3.34 ± 0.61 [-3.84, -2.48] | 0.97 | common-mode |
| Severe 5 vs 6 | neighbour (k=1) | +0.08 ± 0.07 [-0.02, +0.19] | 0.55 | mixed | +0.06 ± 0.05 [-0.01, +0.11] | 0.64 | mixed | -2.15 ± 0.20 [-2.35, -1.81] | 0.99 | common-mode |
| Severe 5 vs 6 | second-neighbour (k=2) | -0.12 ± 0.07 [-0.24, -0.04] | 0.77 | mixed | -0.10 ± 0.07 [-0.24, -0.04] | 0.70 | mixed | -3.07 ± 0.83 [-4.04, -1.63] | 0.93 | common-mode |
| Severe 5 vs 6 | opposite (k=3) | +0.08 ± 0.05 [+0.02, +0.15] | 0.70 | mixed | +0.07 ± 0.06 [+0.02, +0.15] | 0.62 | mixed | -2.91 ± 0.13 [-3.08, -2.78] | 1.00 | common-mode |
| Healthy 6 vs 7 (H6 vs H7) | neighbour (k=1) | +0.08 ± 0.05 [-0.00, +0.14] | 0.77 | mixed | +0.08 ± 0.03 [+0.02, +0.12] | 0.84 | common-mode | -1.44 ± 0.18 [-1.74, -1.23] | 0.98 | common-mode |
| Healthy 6 vs 7 (H6 vs H7) | second-neighbour (k=2) | -0.05 ± 0.08 [-0.18, +0.06] | 0.26 | scattered | -0.06 ± 0.10 [-0.21, +0.12] | 0.27 | scattered | -1.50 ± 0.54 [-2.20, -0.54] | 0.88 | common-mode |
| Healthy 6 vs 7 (H6 vs H7) | opposite (k=3) | -0.13 ± 0.01 [-0.14, -0.11] | 0.99 | common-mode | -0.12 ± 0.01 [-0.13, -0.10] | 0.99 | common-mode | -2.24 ± 0.52 [-2.66, -1.51] | 0.95 | common-mode |
| RightOnly 5 vs mirror(LeftOnly) 6 | neighbour (k=1) | +0.08 ± 0.10 [-0.08, +0.19] | 0.41 | scattered | +0.10 ± 0.07 [+0.00, +0.24] | 0.64 | mixed | -2.81 ± 0.92 [-4.65, -1.95] | 0.90 | common-mode |
| RightOnly 5 vs mirror(LeftOnly) 6 | second-neighbour (k=2) | +0.08 ± 0.11 [-0.13, +0.22] | 0.33 | scattered | +0.06 ± 0.15 [-0.24, +0.25] | 0.12 | scattered | -3.11 ± 1.03 [-4.49, -1.88] | 0.90 | common-mode |
| RightOnly 5 vs mirror(LeftOnly) 6 | opposite (k=3) | -0.04 ± 0.20 [-0.28, +0.21] | 0.04 | scattered | -0.03 ± 0.21 [-0.28, +0.23] | 0.02 | scattered | -4.39 ± 0.59 [-5.11, -3.67] | 0.98 | common-mode |

### 3.2-4.2 GHz

| pair | class | band power: mean ± SD [min, max] dB | cm | class. | mean of dB: mean ± SD [min, max] | cm | class. | phase: mean ± SD [min, max] ° | cm | class. |
|---|---|---|---|---|---|---|---|---|---|---|
| rot07 vs H6 | neighbour (k=1) | -0.02 ± 0.11 [-0.15, +0.14] | 0.02 | scattered | +0.01 ± 0.09 [-0.15, +0.12] | 0.00 | scattered | -0.15 ± 0.80 [-0.95, +1.16] | 0.03 | scattered |
| rot07 vs H6 | second-neighbour (k=2) | +0.06 ± 0.14 [-0.19, +0.21] | 0.14 | scattered | +0.01 ± 0.09 [-0.15, +0.09] | 0.00 | scattered | +0.08 ± 0.98 [-0.91, +1.42] | 0.01 | scattered |
| rot07 vs H6 | opposite (k=3) | +0.01 ± 0.04 [-0.04, +0.05] | 0.13 | scattered | -0.01 ± 0.04 [-0.06, +0.02] | 0.03 | scattered | +0.09 ± 0.63 [-0.77, +0.74] | 0.02 | scattered |
| rot19 vs H6 | neighbour (k=1) | +0.15 ± 0.04 [+0.09, +0.20] | 0.93 | common-mode | +0.06 ± 0.04 [+0.01, +0.12] | 0.69 | mixed | -0.22 ± 0.52 [-0.78, +0.70] | 0.16 | scattered |
| rot19 vs H6 | second-neighbour (k=2) | -0.22 ± 0.26 [-0.63, +0.21] | 0.42 | scattered | -0.18 ± 0.23 [-0.62, +0.08] | 0.37 | scattered | -0.16 ± 1.00 [-1.55, +1.26] | 0.03 | scattered |
| rot19 vs H6 | opposite (k=3) | +0.25 ± 0.10 [+0.14, +0.38] | 0.86 | common-mode | +0.05 ± 0.13 [-0.12, +0.21] | 0.13 | scattered | -1.48 ± 1.11 [-2.82, -0.09] | 0.64 | mixed |
| rot07 vs rot19 | neighbour (k=1) | -0.16 ± 0.12 [-0.26, +0.03] | 0.65 | mixed | -0.06 ± 0.05 [-0.16, -0.00] | 0.54 | mixed | +0.04 ± 0.51 [-0.70, +0.80] | 0.01 | scattered |
| rot07 vs rot19 | second-neighbour (k=2) | +0.27 ± 0.26 [-0.09, +0.70] | 0.52 | mixed | +0.18 ± 0.25 [-0.04, +0.70] | 0.34 | scattered | +0.49 ± 1.26 [-1.34, +2.69] | 0.13 | scattered |
| rot07 vs rot19 | opposite (k=3) | -0.24 ± 0.14 [-0.42, -0.09] | 0.74 | mixed | -0.06 ± 0.14 [-0.19, +0.14] | 0.14 | scattered | +1.46 ± 0.43 [+0.92, +1.96] | 0.92 | common-mode |
| Mild 5 vs 6 | neighbour (k=1) | +0.00 ± 0.03 [-0.05, +0.04] | 0.00 | negligible | -0.01 ± 0.03 [-0.05, +0.04] | 0.16 | scattered | -2.48 ± 0.28 [-2.81, -2.01] | 0.99 | common-mode |
| Mild 5 vs 6 | second-neighbour (k=2) | -0.03 ± 0.13 [-0.26, +0.18] | 0.06 | scattered | -0.05 ± 0.06 [-0.18, +0.01] | 0.35 | scattered | -3.44 ± 0.24 [-3.84, -3.19] | 1.00 | common-mode |
| Mild 5 vs 6 | opposite (k=3) | +0.03 ± 0.09 [-0.08, +0.15] | 0.13 | scattered | +0.04 ± 0.10 [-0.04, +0.18] | 0.10 | scattered | -2.71 ± 0.61 [-3.56, -2.18] | 0.95 | common-mode |
| Moderate 5 vs 6 | neighbour (k=1) | +0.01 ± 0.04 [-0.06, +0.05] | 0.05 | scattered | -0.02 ± 0.03 [-0.05, +0.03] | 0.34 | scattered | -2.36 ± 0.61 [-3.54, -1.74] | 0.94 | common-mode |
| Moderate 5 vs 6 | second-neighbour (k=2) | +0.01 ± 0.05 [-0.05, +0.08] | 0.04 | scattered | -0.02 ± 0.07 [-0.13, +0.11] | 0.06 | scattered | -3.07 ± 0.59 [-3.93, -2.25] | 0.96 | common-mode |
| Moderate 5 vs 6 | opposite (k=3) | +0.01 ± 0.05 [-0.03, +0.09] | 0.06 | scattered | +0.04 ± 0.04 [-0.01, +0.08] | 0.51 | mixed | -2.66 ± 0.67 [-3.23, -1.71] | 0.94 | common-mode |
| Severe 5 vs 6 | neighbour (k=1) | -0.00 ± 0.05 [-0.07, +0.09] | 0.00 | scattered | -0.05 ± 0.03 [-0.10, -0.00] | 0.71 | mixed | -2.51 ± 0.17 [-2.72, -2.29] | 1.00 | common-mode |
| Severe 5 vs 6 | second-neighbour (k=2) | -0.11 ± 0.05 [-0.18, -0.04] | 0.80 | mixed | +0.02 ± 0.07 [-0.08, +0.09] | 0.11 | scattered | -3.33 ± 0.41 [-3.75, -2.53] | 0.98 | common-mode |
| Severe 5 vs 6 | opposite (k=3) | +0.05 ± 0.05 [-0.01, +0.11] | 0.53 | mixed | -0.01 ± 0.04 [-0.05, +0.04] | 0.08 | scattered | -2.72 ± 0.54 [-3.26, -1.98] | 0.96 | common-mode |
| Healthy 6 vs 7 (H6 vs H7) | neighbour (k=1) | +0.01 ± 0.04 [-0.04, +0.08] | 0.09 | scattered | +0.01 ± 0.02 [-0.02, +0.05] | 0.17 | negligible | -1.32 ± 0.21 [-1.70, -1.12] | 0.98 | common-mode |
| Healthy 6 vs 7 (H6 vs H7) | second-neighbour (k=2) | -0.05 ± 0.10 [-0.17, +0.09] | 0.20 | scattered | -0.01 ± 0.09 [-0.11, +0.10] | 0.00 | scattered | -1.83 ± 0.36 [-2.21, -1.09] | 0.96 | common-mode |
| Healthy 6 vs 7 (H6 vs H7) | opposite (k=3) | -0.12 ± 0.00 [-0.13, -0.12] | 1.00 | common-mode | -0.05 ± 0.02 [-0.08, -0.03] | 0.85 | common-mode | -1.66 ± 0.39 [-1.97, -1.10] | 0.95 | common-mode |
| RightOnly 5 vs mirror(LeftOnly) 6 | neighbour (k=1) | -0.03 ± 0.09 [-0.18, +0.10] | 0.08 | scattered | -0.06 ± 0.05 [-0.17, +0.00] | 0.60 | mixed | -3.03 ± 0.85 [-4.64, -2.12] | 0.93 | common-mode |
| RightOnly 5 vs mirror(LeftOnly) 6 | second-neighbour (k=2) | +0.11 ± 0.14 [-0.13, +0.31] | 0.36 | scattered | +0.02 ± 0.17 [-0.25, +0.32] | 0.02 | scattered | -3.89 ± 1.21 [-5.62, -2.14] | 0.91 | common-mode |
| RightOnly 5 vs mirror(LeftOnly) 6 | opposite (k=3) | -0.04 ± 0.20 [-0.27, +0.22] | 0.04 | scattered | -0.03 ± 0.20 [-0.24, +0.24] | 0.02 | scattered | -3.27 ± 0.45 [-3.83, -2.72] | 0.98 | common-mode |

Per-path values, second-neighbour class, 3.30–3.65 GHz (power_dB):

- rot07 vs H6: TT1-T3 +0.12, TT1-T5 +0.18, TT2-T4 +0.20, TT2-T6 -0.10, TT3-T5 -0.05, TT4-T6 -0.03
- rot19 vs H6: TT1-T3 -0.47, TT1-T5 +0.12, TT2-T4 -0.16, TT2-T6 -0.42, TT3-T5 -0.38, TT4-T6 -0.54
- rot07 vs rot19: TT1-T3 +0.59, TT1-T5 +0.06, TT2-T4 +0.36, TT2-T6 +0.32, TT3-T5 +0.33, TT4-T6 +0.51
- Mild 5 vs 6: TT1-T3 -0.06, TT1-T5 -0.07, TT2-T4 -0.01, TT2-T6 +0.21, TT3-T5 +0.11, TT4-T6 -0.19
- Moderate 5 vs 6: TT1-T3 +0.06, TT1-T5 -0.02, TT2-T4 -0.02, TT2-T6 +0.07, TT3-T5 +0.04, TT4-T6 +0.03
- Severe 5 vs 6: TT1-T3 -0.04, TT1-T5 -0.09, TT2-T4 -0.24, TT2-T6 -0.17, TT3-T5 -0.09, TT4-T6 -0.08
- Healthy 6 vs 7 (H6 vs H7): TT1-T3 -0.07, TT1-T5 -0.18, TT2-T4 +0.06, TT2-T6 +0.02, TT3-T5 -0.04, TT4-T6 -0.07
- RightOnly 5 vs mirror(LeftOnly) 6: TT1-T3 +0.14, TT1-T5 +0.22, TT2-T4 -0.13, TT2-T6 +0.16, TT3-T5 +0.03, TT4-T6 +0.06

Per-path values, second-neighbour class, 3.30–3.65 GHz (mean_of_dB):

- rot07 vs H6: TT1-T3 +0.17, TT1-T5 +0.21, TT2-T4 +0.31, TT2-T6 -0.21, TT3-T5 -0.12, TT4-T6 -0.06
- rot19 vs H6: TT1-T3 -0.64, TT1-T5 +0.02, TT2-T4 -0.23, TT2-T6 -0.85, TT3-T5 -0.70, TT4-T6 -0.90
- rot07 vs rot19: TT1-T3 +0.81, TT1-T5 +0.20, TT2-T4 +0.53, TT2-T6 +0.63, TT3-T5 +0.58, TT4-T6 +0.84
- Mild 5 vs 6: TT1-T3 -0.06, TT1-T5 -0.11, TT2-T4 -0.03, TT2-T6 +0.22, TT3-T5 +0.08, TT4-T6 -0.32
- Moderate 5 vs 6: TT1-T3 +0.06, TT1-T5 -0.04, TT2-T4 -0.07, TT2-T6 +0.07, TT3-T5 +0.04, TT4-T6 +0.01
- Severe 5 vs 6: TT1-T3 -0.06, TT1-T5 -0.04, TT2-T4 -0.24, TT2-T6 -0.13, TT3-T5 -0.09, TT4-T6 -0.06
- Healthy 6 vs 7 (H6 vs H7): TT1-T3 -0.07, TT1-T5 -0.21, TT2-T4 +0.12, TT2-T6 -0.02, TT3-T5 -0.09, TT4-T6 -0.12
- RightOnly 5 vs mirror(LeftOnly) 6: TT1-T3 +0.12, TT1-T5 +0.25, TT2-T4 -0.24, TT2-T6 +0.15, TT3-T5 +0.07, TT4-T6 -0.01

## 1. Stage and lobe calls for every target, reference and variant

| target | reference | variant | stage (P) | stage ok | lobes called | wrong lobes | fit |
|---|---|---|---|---|---|---|---|
| Healthy_p7 | H6 | standard | Healthy (1.00) | yes | none | 0 | 0.36 |
| Healthy_p7 | H6 | gainfree | Healthy (1.00) | yes | none | 0 | 1.18 |
| Healthy_p7 | H6 | ringphase | Healthy (1.00) | yes | none | 0 | 0.13 |
| Healthy_p7 | rot07 | standard | Healthy (1.00) | yes | none | 0 | 0.66 |
| Healthy_p7 | rot07 | gainfree | Healthy (1.00) | yes | none | 0 | 1.59 |
| Healthy_p7 | rot07 | ringphase | Healthy (1.00) | yes | none | 0 | 0.37 |
| Healthy_p7 | rot19 | standard | Healthy (1.00) | yes | none | 0 | 2.08 |
| Healthy_p7 | rot19 | gainfree | Healthy (1.00) | yes | none | 0 | 2.14 |
| Healthy_p7 | rot19 | ringphase | Healthy (1.00) | yes | none | 0 | 1.23 |
| Mild_p5 | H6 | standard | Mild (1.00) | yes | S1, S2, S3, S5, S6 | 1 | 1.01 |
| Mild_p5 | H6 | gainfree | Mild (1.00) | yes | S1, S2, S3, S4, S5, S6 | 2 | 1.40 |
| Mild_p5 | H6 | ringphase | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.68 |
| Mild_p5 | H7 | standard | Mild (1.00) | yes | S1, S2, S3, S5, S6 | 1 | 1.66 |
| Mild_p5 | H7 | gainfree | Mild (1.00) | yes | S1, S2, S3, S4, S5, S6 | 2 | 2.97 |
| Mild_p5 | H7 | ringphase | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.86 |
| Mild_p5 | rot07 | standard | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 1.25 |
| Mild_p5 | rot07 | gainfree | Mild (1.00) | yes | S2, S3, S4, S5, S6 | 1 | 1.69 |
| Mild_p5 | rot07 | ringphase | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.93 |
| Mild_p5 | rot19 | standard | Moderate (1.00) | **no** | S2, S3, S5, S6 | 0 | 1.25 |
| Mild_p5 | rot19 | gainfree | Mild (0.99) | yes | S1, S2, S3, S4, S5, S6 | 2 | 2.42 |
| Mild_p5 | rot19 | ringphase | Moderate (1.00) | **no** | S2, S3, S5, S6 | 0 | 0.89 |
| Mild_p6 | H6 | standard | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.49 |
| Mild_p6 | H6 | gainfree | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.75 |
| Mild_p6 | H6 | ringphase | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.44 |
| Mild_p6 | H7 | standard | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.56 |
| Mild_p6 | H7 | gainfree | Mild (1.00) | yes | S1, S2, S3, S5, S6 | 1 | 0.67 |
| Mild_p6 | H7 | ringphase | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.45 |
| Mild_p6 | rot07 | standard | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.72 |
| Mild_p6 | rot07 | gainfree | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 1.01 |
| Mild_p6 | rot07 | ringphase | Mild (1.00) | yes | S2, S3, S5, S6 | 0 | 0.65 |
| Mild_p6 | rot19 | standard | Moderate (1.00) | **no** | S2, S3, S5, S6 | 0 | 1.54 |
| Mild_p6 | rot19 | gainfree | Moderate (1.00) | **no** | S2, S3, S5, S6 | 0 | 1.54 |
| Mild_p6 | rot19 | ringphase | Moderate (1.00) | **no** | S2, S3, S5, S6 | 0 | 1.04 |
| Moderate_p5 | H6 | standard | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.32 |
| Moderate_p5 | H6 | gainfree | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.33 |
| Moderate_p5 | H6 | ringphase | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.29 |
| Moderate_p5 | H7 | standard | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.36 |
| Moderate_p5 | H7 | gainfree | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.50 |
| Moderate_p5 | H7 | ringphase | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.33 |
| Moderate_p5 | rot07 | standard | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.38 |
| Moderate_p5 | rot07 | gainfree | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.41 |
| Moderate_p5 | rot07 | ringphase | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.35 |
| Moderate_p5 | rot19 | standard | Severe (1.00) | **no** | S2, S6 | 3 | 1.14 |
| Moderate_p5 | rot19 | gainfree | Severe (1.00) | **no** | S2, S6 | 3 | 1.16 |
| Moderate_p5 | rot19 | ringphase | Severe (0.89) | **no** | S2, S6 | 3 | 0.77 |
| Moderate_p6 | H6 | standard | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.47 |
| Moderate_p6 | H6 | gainfree | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.54 |
| Moderate_p6 | H6 | ringphase | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.30 |
| Moderate_p6 | H7 | standard | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.30 |
| Moderate_p6 | H7 | gainfree | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.30 |
| Moderate_p6 | H7 | ringphase | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.24 |
| Moderate_p6 | rot07 | standard | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.54 |
| Moderate_p6 | rot07 | gainfree | Moderate (1.00) | yes | S2, S3, S5, S6 | 1 | 0.63 |
| Moderate_p6 | rot07 | ringphase | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 0.36 |
| Moderate_p6 | rot19 | standard | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 1.50 |
| Moderate_p6 | rot19 | gainfree | Moderate (1.00) | yes | S1, S2, S3, S5, S6 | 0 | 1.45 |
| Moderate_p6 | rot19 | ringphase | Severe (1.00) | **no** | S2, S6 | 3 | 0.87 |
| Severe_p5 | H6 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.59 |
| Severe_p5 | H6 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.47 |
| Severe_p5 | H6 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 1.87 |
| Severe_p5 | H7 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 3.14 |
| Severe_p5 | H7 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 3.05 |
| Severe_p5 | H7 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.10 |
| Severe_p5 | rot07 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.84 |
| Severe_p5 | rot07 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.80 |
| Severe_p5 | rot07 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.13 |
| Severe_p5 | rot19 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.84 |
| Severe_p5 | rot19 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.93 |
| Severe_p5 | rot19 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 1.80 |
| Severe_p6 | H6 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.05 |
| Severe_p6 | H6 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.98 |
| Severe_p6 | H6 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 1.56 |
| Severe_p6 | H7 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.12 |
| Severe_p6 | H7 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.23 |
| Severe_p6 | H7 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 1.60 |
| Severe_p6 | rot07 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.29 |
| Severe_p6 | rot07 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 3.31 |
| Severe_p6 | rot07 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 1.78 |
| Severe_p6 | rot19 | standard | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 2.78 |
| Severe_p6 | rot19 | gainfree | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 3.30 |
| Severe_p6 | rot19 | ringphase | Severe (1.00) | yes | S1, S2, S3, S4, S5, S6 | 0 | 1.95 |
| LeftOnly_p6 | H6 | standard | Mild (1.00) | yes | S2, S3 | 0 | 0.41 |
| LeftOnly_p6 | H6 | gainfree | Mild (1.00) | yes | S2, S3 | 0 | 0.79 |
| LeftOnly_p6 | H6 | ringphase | Mild (1.00) | yes | S2, S3 | 0 | 0.32 |
| LeftOnly_p6 | H7 | standard | Mild (1.00) | yes | S2, S3 | 0 | 0.35 |
| LeftOnly_p6 | H7 | gainfree | Mild (1.00) | yes | S2, S3 | 0 | 0.68 |
| LeftOnly_p6 | H7 | ringphase | Mild (1.00) | yes | S2, S3 | 0 | 0.31 |
| LeftOnly_p6 | rot07 | standard | Mild (1.00) | yes | S2, S3 | 0 | 0.51 |
| LeftOnly_p6 | rot07 | gainfree | Mild (1.00) | yes | S2, S3 | 0 | 1.07 |
| LeftOnly_p6 | rot07 | ringphase | Mild (1.00) | yes | S2, S3 | 0 | 0.41 |
| LeftOnly_p6 | rot19 | standard | Moderate (1.00) | **no** | S2, S3 | 0 | 1.40 |
| LeftOnly_p6 | rot19 | gainfree | Moderate (1.00) | **no** | S2, S3 | 0 | 1.41 |
| LeftOnly_p6 | rot19 | ringphase | Moderate (1.00) | **no** | S2, S3 | 0 | 0.97 |
| MCI_p6 | H6 | standard | Healthy (1.00) | yes | none | 0 | 0.37 |
| MCI_p6 | H6 | gainfree | Healthy (1.00) | yes | none | 0 | 0.57 |
| MCI_p6 | H6 | ringphase | Healthy (1.00) | yes | none | 0 | 0.30 |
| MCI_p6 | H7 | standard | Mild (1.00) | **no** | none | 0 | 0.59 |
| MCI_p6 | H7 | gainfree | Mild (1.00) | **no** | none | 0 | 0.92 |
| MCI_p6 | H7 | ringphase | Healthy (1.00) | yes | none | 0 | 0.34 |
| MCI_p6 | rot07 | standard | Healthy (1.00) | yes | none | 0 | 0.45 |
| MCI_p6 | rot07 | gainfree | Healthy (1.00) | yes | none | 0 | 0.73 |
| MCI_p6 | rot07 | ringphase | Healthy (1.00) | yes | none | 0 | 0.40 |
| MCI_p6 | rot19 | standard | Mild (1.00) | **no** | none | 0 | 1.42 |
| MCI_p6 | rot19 | gainfree | Mild (1.00) | **no** | none | 0 | 1.64 |
| MCI_p6 | rot19 | ringphase | Healthy (1.00) | yes | none | 0 | 1.01 |
| RightOnly | H6 | standard | Mild (1.00) | yes | S5, S6 | 0 | 0.56 |
| RightOnly | H6 | gainfree | Mild (1.00) | yes | S2, S3, S5, S6 | 2 | 0.78 |
| RightOnly | H6 | ringphase | Mild (1.00) | yes | S5, S6 | 0 | 0.43 |
| RightOnly | H7 | standard | Mild (1.00) | yes | S1, S2, S5, S6 | 2 | 0.98 |
| RightOnly | H7 | gainfree | Mild (1.00) | yes | S1, S2, S3, S5, S6 | 3 | 1.50 |
| RightOnly | H7 | ringphase | Mild (1.00) | yes | S5, S6 | 0 | 0.53 |
| RightOnly | rot07 | standard | Mild (1.00) | yes | S5, S6 | 0 | 0.64 |
| RightOnly | rot07 | gainfree | Mild (1.00) | yes | S2, S5, S6 | 1 | 0.86 |
| RightOnly | rot07 | ringphase | Mild (1.00) | yes | S5, S6 | 0 | 0.52 |
| RightOnly | rot19 | standard | Moderate (1.00) | **no** | S5, S6 | 0 | 1.19 |
| RightOnly | rot19 | gainfree | Severe (1.00) | **no** | S6 | 1 | 1.88 |
| RightOnly | rot19 | ringphase | Moderate (1.00) | **no** | S5, S6 | 0 | 0.79 |
| Test_B | H6 | standard | Mild (1.00) | yes | S2, S5 | 0 | 0.46 |
| Test_B | H6 | gainfree | Mild (1.00) | yes | S2, S5 | 0 | 0.77 |
| Test_B | H6 | ringphase | Mild (1.00) | yes | S2, S5 | 0 | 0.37 |
| Test_B | H7 | standard | Mild (1.00) | yes | S2, S5 | 0 | 0.42 |
| Test_B | H7 | gainfree | Mild (1.00) | yes | S2, S5 | 0 | 0.51 |
| Test_B | H7 | ringphase | Mild (1.00) | yes | S2, S5 | 0 | 0.36 |
| Test_B | rot07 | standard | Mild (1.00) | yes | S2, S5 | 0 | 0.66 |
| Test_B | rot07 | gainfree | Mild (1.00) | yes | S2, S5 | 0 | 1.05 |
| Test_B | rot07 | ringphase | Mild (1.00) | yes | S2, S5 | 0 | 0.55 |
| Test_B | rot19 | standard | Moderate (1.00) | **no** | S2, S5 | 0 | 1.63 |
| Test_B | rot19 | gainfree | Mild (1.00) | yes | S2, S5 | 0 | 1.73 |
| Test_B | rot19 | ringphase | Moderate (1.00) | **no** | S2, S5 | 0 | 1.12 |
| rot07 | H6 | standard | Healthy (1.00) | yes | none | 0 | 0.30 |
| rot07 | H6 | gainfree | Healthy (1.00) | yes | none | 0 | 0.34 |
| rot07 | H6 | ringphase | Healthy (1.00) | yes | none | 0 | 0.29 |
| rot07 | H7 | standard | Healthy (1.00) | yes | none | 0 | 0.59 |
| rot07 | H7 | gainfree | Mild (1.00) | **no** | none | 0 | 0.70 |
| rot07 | H7 | ringphase | Healthy (1.00) | yes | none | 0 | 0.36 |
| rot07 | rot19 | standard | Mild (0.62) | **no** | none | 0 | 1.51 |
| rot07 | rot19 | gainfree | Mild (1.00) | **no** | none | 0 | 1.67 |
| rot07 | rot19 | ringphase | Healthy (1.00) | yes | none | 0 | 1.01 |
| rot19 | H6 | standard | Healthy (1.00) | yes | none | 0 | 1.39 |
| rot19 | H6 | gainfree | Healthy (1.00) | yes | none | 0 | 1.55 |
| rot19 | H6 | ringphase | Healthy (1.00) | yes | none | 0 | 0.89 |
| rot19 | H7 | standard | Healthy (1.00) | yes | none | 0 | 1.89 |
| rot19 | H7 | gainfree | Healthy (1.00) | yes | none | 0 | 2.01 |
| rot19 | H7 | ringphase | Healthy (1.00) | yes | none | 0 | 1.18 |
| rot19 | rot07 | standard | Healthy (1.00) | yes | none | 0 | 1.54 |
| rot19 | rot07 | gainfree | Healthy (1.00) | yes | none | 0 | 1.87 |
| rot19 | rot07 | ringphase | Healthy (1.00) | yes | none | 0 | 1.01 |

## 2. Per variant: wrong lobe calls and wrong stages over all targets × references

| variant | runs | wrong lobe calls | runs with ≥ 1 wrong lobe | wrong stage | by reference (wrong lobes / wrong stage / runs) |
|---|---|---|---|---|---|
| standard | 49 | 7 | 4 | 9 | H6: 1/0/13; H7: 3/1/12; rot07: 0/0/12; rot19: 3/8/12 |
| gainfree | 49 | 19 | 11 | 8 | H6: 4/0/13; H7: 6/2/12; rot07: 3/0/12; rot19: 6/6/12 |
| ringphase | 49 | 6 | 2 | 7 | H6: 0/0/13; H7: 0/0/12; rot07: 0/0/12; rot19: 6/7/12 |

## 3. Rulers, three ways (rule 2)

**R4 ring left-right contrast**: null values H7 vs H6 +0.26, H6 vs H7 -0.26, MCI vs H6 +0.34, Mild5 vs H6 +0.06, Mild6 vs H7 +0.11, Mod5 vs H6 -0.91, Mod6 vs H7 -0.12, Sev5 vs H6 +0.70, Sev6 vs H7 +0.45, rot07 +0.69, rot19 +0.28

| way | floor | reading | value | / floor | bar |
|---|---|---|---|---|---|
| all nulls | 0.91 | LeftOnly vs H6 | +4.44 | 4.87 | established (>= 3x) |
| all nulls | 0.91 | RightOnly vs H6 | -4.60 | 5.05 | established (>= 3x) |
| all without rot19 | 0.91 | LeftOnly vs H6 | +4.44 | 4.87 | established (>= 3x) |
| all without rot19 | 0.91 | RightOnly vs H6 | -4.60 | 5.05 | established (>= 3x) |
| rot19 alone | 0.28 | LeftOnly vs H6 | +4.44 | 16.08 | established (>= 3x) |
| rot19 alone | 0.28 | RightOnly vs H6 | -4.60 | 16.66 | established (>= 3x) |

**R5 ring front-back contrast**: null values H7 vs H6 +0.04, H6 vs H7 -0.04, MCI vs H6 +0.02, Mild5 vs H6 +0.53, Mild6 vs H7 +0.45, rot07 +1.32, rot19 +0.13

| way | floor | reading | value | / floor | bar |
|---|---|---|---|---|---|
| all nulls | 1.32 | Mod5 vs H6 | +4.24 | 3.21 | established (>= 3x) |
| all nulls | 1.32 | Mod6 vs H7 | +4.13 | 3.12 | established (>= 3x) |
| all without rot19 | 1.32 | Mod5 vs H6 | +4.24 | 3.21 | established (>= 3x) |
| all without rot19 | 1.32 | Mod6 vs H7 | +4.13 | 3.12 | established (>= 3x) |
| rot19 alone | 0.13 | Mod5 vs H6 | +4.24 | 33.62 | established (>= 3x) |
| rot19 alone | 0.13 | Mod6 vs H7 | +4.13 | 32.68 | established (>= 3x) |

**R6 ring spread**: null values H7 vs H6 +0.39, H6 vs H7 +0.39, MCI vs H6 +0.41, rot07 +1.42, rot19 +0.68

| way | floor | reading | value | / floor | bar |
|---|---|---|---|---|---|
| all nulls | 1.42 | Test_B vs H6 | +2.11 | 1.49 | not separable (< 2x) |
| all without rot19 | 1.42 | Test_B vs H6 | +2.11 | 1.49 | not separable (< 2x) |
| rot19 alone | 0.68 | Test_B vs H6 | +2.11 | 3.09 | established (>= 3x) |

**R7 ring diagonal-pair elevation (post hoc statistic)**: null values H7 vs H6 +0.08, H6 vs H7 +0.12, MCI vs H6 +0.12, rot07 +0.42, rot19 +0.39

| way | floor | reading | value | / floor | bar |
|---|---|---|---|---|---|
| all nulls | 0.42 | Test_B vs H6 | +1.57 | 3.73 | established (>= 3x) |
| all without rot19 | 0.42 | Test_B vs H6 | +1.57 | 3.73 | established (>= 3x) |
| rot19 alone | 0.39 | Test_B vs H6 | +1.57 | 4.06 | established (>= 3x) |

**R8 ring T2,T5 elevation (post hoc pair)**: null values H7 vs H6 +0.08, H6 vs H7 -0.08, MCI vs H6 -0.00, rot07 -0.27, rot19 -0.22

| way | floor | reading | value | / floor | bar |
|---|---|---|---|---|---|
| all nulls | 0.27 | Test_B vs H6 | +1.57 | 5.79 | established (>= 3x) |
| all without rot19 | 0.27 | Test_B vs H6 | +1.57 | 5.79 | established (>= 3x) |
| rot19 alone | 0.22 | Test_B vs H6 | +1.57 | 7.03 | established (>= 3x) |

**R3 LR_e (e left - right), reconstruction**: null values Healthy_p7 +0.00, MCI_p6 +0.00, Mild_p5 +0.25, Mild_p6 -2.00, Moderate_p5 +0.50, Moderate_p6 +0.75, Severe_p5 -4.00, Severe_p6 -9.25, Healthy_p6_vsH7 +0.00, rot07 +0.00, rot19 +0.00

| way | floor | reading | value | / floor | bar |
|---|---|---|---|---|---|
| all nulls | 9.25 | LeftOnly_p6 | +11.50 | 1.24 | not separable (< 2x) |
| all nulls | 9.25 | RightOnly | -3.25 | 0.35 | not separable (< 2x) |
| all nulls | 9.25 | Test_B | +3.00 | 0.32 | not separable (< 2x) |
| all without rot19 | 9.25 | LeftOnly_p6 | +11.50 | 1.24 | not separable (< 2x) |
| all without rot19 | 9.25 | RightOnly | -3.25 | 0.35 | not separable (< 2x) |
| all without rot19 | 9.25 | Test_B | +3.00 | 0.32 | not separable (< 2x) |
| rot19 alone | 0.00 | LeftOnly_p6 | +11.50 | – | floor 0: not applicable |
| rot19 alone | 0.00 | RightOnly | -3.25 | – | floor 0: not applicable |
| rot19 alone | 0.00 | Test_B | +3.00 | – | floor 0: not applicable |

## 4. Readings R1, R2, R9, R10

R1 (rotated nulls as targets; lobes called per run):

- rot07: vs H6 standard: 0 lobes, Healthy; vs H6 gainfree: 0 lobes, Healthy; vs H6 ringphase: 0 lobes, Healthy; vs H7 standard: 0 lobes, Healthy; vs H7 gainfree: 0 lobes, Mild; vs H7 ringphase: 0 lobes, Healthy; vs rot19 standard: 0 lobes, Mild; vs rot19 gainfree: 0 lobes, Mild; vs rot19 ringphase: 0 lobes, Healthy
- rot19: vs H6 standard: 0 lobes, Healthy; vs H6 gainfree: 0 lobes, Healthy; vs H6 ringphase: 0 lobes, Healthy; vs H7 standard: 0 lobes, Healthy; vs H7 gainfree: 0 lobes, Healthy; vs H7 ringphase: 0 lobes, Healthy; vs rot07 standard: 0 lobes, Healthy; vs rot07 gainfree: 0 lobes, Healthy; vs rot07 ringphase: 0 lobes, Healthy

R2 (one-sided call pattern in a rotated null): {'rot07': False, 'rot19': False}

R9/R10 (rotated null as reference): exact calls / stage correct:

- LeftOnly_p6 vs rot07 standard: calls exact, stage Mild (ok)
- LeftOnly_p6 vs rot07 gainfree: calls exact, stage Mild (ok)
- LeftOnly_p6 vs rot07 ringphase: calls exact, stage Mild (ok)
- LeftOnly_p6 vs rot19 standard: calls exact, stage Moderate (wrong)
- LeftOnly_p6 vs rot19 gainfree: calls exact, stage Moderate (wrong)
- LeftOnly_p6 vs rot19 ringphase: calls exact, stage Moderate (wrong)
- RightOnly vs rot07 standard: calls exact, stage Mild (ok)
- RightOnly vs rot07 gainfree: calls WRONG, stage Mild (ok)
- RightOnly vs rot07 ringphase: calls exact, stage Mild (ok)
- RightOnly vs rot19 standard: calls exact, stage Moderate (wrong)
- RightOnly vs rot19 gainfree: calls WRONG, stage Severe (wrong)
- RightOnly vs rot19 ringphase: calls exact, stage Moderate (wrong)
- Test_B vs rot07 standard: calls exact, stage Mild (ok)
- Test_B vs rot07 gainfree: calls exact, stage Mild (ok)
- Test_B vs rot07 ringphase: calls exact, stage Mild (ok)
- Test_B vs rot19 standard: calls exact, stage Moderate (wrong)
- Test_B vs rot19 gainfree: calls exact, stage Mild (ok)
- Test_B vs rot19 ringphase: calls exact, stage Moderate (wrong)

## 5. R11 coverage of e (90% intervals, augmented noise), three ways

| way | sectors | coverage all | affected | coverage affected | calls correct |
|---|---|---|---|---|---|
| all nulls | 66 | 88% | 36 | 78% | 100% |
| all without rot19 | 66 | 91% | 36 | 83% | 100% |
| rot19 alone | 66 | 88% | 36 | 78% | 100% |
