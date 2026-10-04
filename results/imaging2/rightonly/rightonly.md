# RightOnly_test: mirror / mesh-independence check of the LeftOnly result

Code 24aa0c4+imaging2-uncommitted. RightOnly reconstructed with the LeftOnly fold (training = 8 files, every lobe design except LeftOnly; RightOnly itself never in training; surrogate tm0 / λ 0.01). Reference H6 (same stop rule as LeftOnly) primary; H7 and gain-free alongside. Truth (supplied, header checked): e = 0/0/0/0/11.5/7.5 mm, Mild in S5, S6.

## Reconstructions

| run | stage (P) | lobes called | ê S1…S6 (mm) | fit χ²/dof |
|---|---|---|---|---|
| RightOnly_p6 | Mild (1.00) | S5 PR, S6 TR | 0.0 / 0.0 / 0.0 / 0.0 / 3.0 / 3.5 | 0.57 |
| RightOnly_vsH7 | Mild (1.00) | S1 Fr, S2 TL, S5 PR, S6 TR | 1.5 / 1.5 / 0.0 / 0.0 / 3.0 / 3.5 | 0.98 |
| RightOnly_gainfree | Mild (1.00) | S2 TL, S3 PL, S5 PR, S6 TR | 0.0 / 1.5 / 1.0 / 0.0 / 3.0 / 3.0 | 0.78 |
| LeftOnly_p6_rerun | Mild (1.00) | S2 TL, S3 PL | 0.0 / 11.5 / 11.5 / 0.0 / 0.0 / 0.0 | 0.41 |
| LeftOnly_gainfree | Mild (1.00) | S2 TL, S3 PL | 0.0 / 1.0 / 1.5 / 0.0 / 0.0 / 0.0 | 0.79 |

## RightOnly against mirrored LeftOnly, sector by sector (primary runs, reference H6)

| sector | ← LeftOnly sector | P(aff) RightOnly | P(aff) LeftOnly mirrored | ê RightOnly [90%] | ê LeftOnly mirrored [90%] | e true |
|---|---|---|---|---|---|---|
| S1 Fr | S1 Fr | 0.00 | 0.00 | 0.0 [0.0–0.0] | 0.0 [0.0–0.0] | 0.0 |
| S2 TL | S6 TR | 0.01 | 0.00 | 0.0 [0.0–0.0] | 0.0 [0.0–0.0] | 0.0 |
| S3 PL | S5 PR | 0.00 | 0.00 | 0.0 [0.0–0.0] | 0.0 [0.0–0.0] | 0.0 |
| S4 Oc | S4 Oc | 0.00 | 0.00 | 0.0 [0.0–0.0] | 0.0 [0.0–0.0] | 0.0 |
| S5 PR | S3 PL | 1.00 | 1.00 | 3.0 [2.5–3.5] | 11.5 [5.5–21.5] | 11.5 |
| S6 TR | S2 TL | 1.00 | 1.00 | 3.5 [3.5–3.5] | 11.5 [5.0–21.0] | 7.5 |

## Data level: RightOnly − mirror(LeftOnly), rms over paths and 201 frequencies

Ruler = rms of the mesh-pair double differences (both meshes of Mild, Moderate, Severe and H7 − H6), √2 × the one-observation sd, i.e. the expected difference between two independent meshes.

| path type | RO − mirror(LO) dB | ruler dB | RO − mirror(LO) ° | ruler ° | band-mean phase RO − mirror(LO) ° | RightOnly signal dB / ° | LeftOnly signal dB / ° | corr(RO, mirror LO) |
|---|---|---|---|---|---|---|---|---|
| reflection | 0.272 | 0.157 | 1.78 | 1.03 | -0.45 | 0.48 / 3.1 | 0.27 / 1.8 | 0.88 |
| neighbour | 0.262 | 0.129 | 3.81 | 1.74 | -3.05 | 0.41 / 6.6 | 0.31 / 3.8 | 0.85 |
| second-neighbour | 0.811 | 0.534 | 6.39 | 3.86 | -3.87 | 1.16 / 6.7 | 0.96 / 6.5 | 0.63 |
| opposite | 0.523 | 0.446 | 4.51 | 3.93 | -3.25 | 0.75 / 4.2 | 0.73 / 3.3 | 0.58 |

Model-free ring (neighbour-path phase delay per antenna T1…T6, mean 3.30–3.65 GHz, °; the window is post hoc, README §6b):

- RightOnly_vsH6: 7.0 / 4.8 / 4.9 / 6.2 / 9.1 / 9.8  (right T5,T6 − left T2,T3: +4.60°)
- LeftOnly_mirrored_vsH6: 3.5 / 2.2 / 2.1 / 3.9 / 6.8 / 6.4  (right T5,T6 − left T2,T3: +4.44°)
- RightOnly_vsH7: 8.4 / 6.1 / 6.3 / 7.7 / 10.6 / 11.5  (right T5,T6 − left T2,T3: +4.85°)

## Side statistics under R1c (null = the nine mirror-symmetric designs; floor = largest |null|)

LR_e = mean ê(S2, S3) − mean ê(S5, S6) (mm); LR_p = mean P(affected)(S2, S3) − mean P(affected)(S5, S6).

**LR_e** null: Healthy_p7 +0.00, Healthy_p6_vsH7 +0.00, MCI_p6 +0.00, Mild_p5 +0.25, Mild_p6 -2.00, Moderate_p5 +0.50, Moderate_p6 +0.75, Severe_p5 -4.00, Severe_p6 -9.25; floor 9.25 (set by Severe_p6, whose depth is undetermined).

| design | LR_e (mm) | / floor | bar | rank p |
|---|---|---|---|---|
| LeftOnly_p6 | +11.50 | 1.24 | not separable (< 2x) | 0.10 |
| RightOnly_p6 | -3.25 | 0.35 | not separable (< 2x) | 0.30 |
| RightOnly_vsH7 | -2.50 | 0.27 | not separable (< 2x) | 0.30 |
| RightOnly_gainfree | -1.75 | 0.19 | not separable (< 2x) | 0.40 |

**LR_p / one-sided calls.** All nine null designs give mirror-symmetric calls: largest |LR_p| = 1.1e-16, i.e. the floor is zero and the R1c ratio is NOT APPLICABLE. Reported instead: is the call pattern one-sided (affected lobes on one side only)? Null: 0 of 9.

| design | lobes called | one-sided | LR_p |
|---|---|---|---|
| LeftOnly_p6 | S2 TL, S3 PL | yes (left) | +1.00 |
| RightOnly_p6 | S5 PR, S6 TR | yes (right) | -1.00 |
| RightOnly_vsH7 | S1 Fr, S2 TL, S5 PR, S6 TR | no | -0.69 |
| RightOnly_gainfree | S2 TL, S3 PL, S5 PR, S6 TR | no | -0.01 |
