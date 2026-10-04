# Adversarial review of the lobe blind result (imaging session, 5 Oct)

Every number below was recomputed from the raw `.s6p` files and `lobe_frozen.json` (read only) by `python imaging/lobe_review.py --n 200` at code `aad54d8`; numbers in `results/imaging/lobe_review.json` (key named in each section). Predictions (`lobe_predictions.md`, frozen at `fb5b775`) and frozen files are unchanged. Ruler definitions: clean = max(one-pass mesh yardstick of the four stages, numerical symmetry floor); measured = max(yardstick, floor ⊕ ±0.5 dB measurement spread) (quadrature, as the main session). Bar: ≥ 3× established, 2–3× sensitive, < 2× not separable.

## B1. One bar for left/right and front/back

Key `b1` (LR of LeftOnly; FB of Moderate and of the truth-zero Mild/Severe), plus `b1_floors` (LR floor per design). `ratio_meas_max_old` is the measured ruler as previously combined (plain max).

| quantity | comparison | method | floor_from | clean | yard | floor | sd_±0.5 dB gain | ratio_clean | bar_clean | ratio_meas_quad | bar_meas | ratio_meas_max_old |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LR | LeftOnly − H7 (frozen, primary) | Tikhonov dS | max of lobe_A symmetric designs | 8.48 | 2.18 | 4.16 | 26.00 | 2.04 | sensitive (2–3×) | 0.32 | not separable (< 2×) | 0.33 |
| LR | LeftOnly − H7 (frozen, primary) | Tikhonov dS | pass-matched p6 designs (H6, MCI_c3) | 8.48 | 2.18 | 1.46 | 26.00 | 3.88 | established (≥ 3×) | 0.33 | not separable (< 2×) | 0.33 |
| LR | LeftOnly − H7 (frozen, primary) | frozen log | max of lobe_A symmetric designs | 9.25 | 2.25 | 3.69 | 10.45 | 2.50 | sensitive (2–3×) | 0.83 | not separable (< 2×) | 0.89 |
| LR | LeftOnly − H7 (frozen, primary) | frozen log | pass-matched p6 designs (H6, MCI_c3) | 9.25 | 2.25 | 1.43 | 10.45 | 4.10 | established (≥ 3×) | 0.88 | not separable (< 2×) | 0.89 |
| LR | LeftOnly − H7 (frozen, primary) | whitened log | max of lobe_A symmetric designs | 9.27 | 1.68 | 3.14 | 2.69 | 2.95 | sensitive (2–3×) | 2.24 | sensitive (2–3×) | 2.95 |
| LR | LeftOnly − H7 (frozen, primary) | whitened log | pass-matched p6 designs (H6, MCI_c3) | 9.27 | 1.68 | 1.19 | 2.69 | 5.51 | established (≥ 3×) | 3.15 | established (≥ 3×) | 3.44 |
| LR | LeftOnly − H6 (matched) | Tikhonov dS | max of lobe_A symmetric designs | 8.82 | 2.14 | 4.21 | 26.22 | 2.10 | sensitive (2–3×) | 0.33 | not separable (< 2×) | 0.34 |
| LR | LeftOnly − H6 (matched) | Tikhonov dS | pass-matched p6 designs (H6, MCI_c3) | 8.82 | 2.14 | 1.64 | 26.22 | 4.12 | established (≥ 3×) | 0.34 | not separable (< 2×) | 0.34 |
| LR | LeftOnly − H6 (matched) | frozen log | max of lobe_A symmetric designs | 9.70 | 2.23 | 3.76 | 10.82 | 2.58 | sensitive (2–3×) | 0.85 | not separable (< 2×) | 0.90 |
| LR | LeftOnly − H6 (matched) | frozen log | pass-matched p6 designs (H6, MCI_c3) | 9.70 | 2.23 | 1.58 | 10.82 | 4.35 | established (≥ 3×) | 0.89 | not separable (< 2×) | 0.90 |
| LR | LeftOnly − H6 (matched) | whitened log | max of lobe_A symmetric designs | 9.41 | 1.66 | 3.14 | 3.05 | 3.00 | sensitive (2–3×) | 2.15 | sensitive (2–3×) | 3.00 |
| LR | LeftOnly − H6 (matched) | whitened log | pass-matched p6 designs (H6, MCI_c3) | 9.41 | 1.66 | 1.19 | 3.05 | 5.65 | established (≥ 3×) | 2.87 | sensitive (2–3×) | 3.08 |
| FB | Moderate − H6 (lobe_A) | Tikhonov dS | own design | 10.16 | 0.71 | 4.58 | 30.31 | 2.22 | sensitive (2–3×) | 0.33 | not separable (< 2×) | 0.34 |
| FB | Moderate − Mild (lobe_A) | Tikhonov dS | own design | 6.20 | 0.76 | 4.39 | 29.02 | 1.41 | not separable (< 2×) | 0.21 | not separable (< 2×) | 0.21 |
| FB | Moderate − H7 (lobe_B) | Tikhonov dS | own design | 10.80 | 0.67 | 2.30 | 34.38 | 4.70 | established (≥ 3×) | 0.31 | not separable (< 2×) | 0.31 |
| FB | Moderate − Mild (lobe_B) | Tikhonov dS | own design | 7.59 | 0.71 | 2.10 | 31.06 | 3.61 | established (≥ 3×) | 0.24 | not separable (< 2×) | 0.24 |
| FB | Mild − H6 (lobe_A, truth 0) | Tikhonov dS | own design | 3.85 | 0.71 | 1.27 | 32.72 | 3.04 | established (≥ 3×) | 0.12 | not separable (< 2×) | 0.12 |
| FB | Severe − H6 (lobe_A, truth 0) | Tikhonov dS | own design | 3.84 | 0.71 | 1.66 | 31.11 | 2.31 | sensitive (2–3×) | 0.12 | not separable (< 2×) | 0.12 |
| FB | Moderate − H6 (lobe_A) | frozen log | own design | 10.44 | 0.91 | 4.07 | 12.95 | 2.57 | sensitive (2–3×) | 0.77 | not separable (< 2×) | 0.81 |
| FB | Moderate − Mild (lobe_A) | frozen log | own design | 6.43 | 1.27 | 4.07 | 13.75 | 1.58 | not separable (< 2×) | 0.45 | not separable (< 2×) | 0.47 |
| FB | Moderate − H7 (lobe_B) | frozen log | own design | 10.86 | 1.00 | 1.80 | 13.58 | 6.04 | established (≥ 3×) | 0.79 | not separable (< 2×) | 0.80 |
| FB | Moderate − Mild (lobe_B) | frozen log | own design | 7.50 | 1.16 | 1.59 | 13.87 | 4.71 | established (≥ 3×) | 0.54 | not separable (< 2×) | 0.54 |
| FB | Mild − H6 (lobe_A, truth 0) | frozen log | own design | 3.92 | 0.91 | 1.27 | 13.11 | 3.09 | established (≥ 3×) | 0.30 | not separable (< 2×) | 0.30 |
| FB | Severe − H6 (lobe_A, truth 0) | frozen log | own design | 4.14 | 0.91 | 1.46 | 14.17 | 2.84 | sensitive (2–3×) | 0.29 | not separable (< 2×) | 0.29 |
| FB | Moderate − H6 (lobe_A) | whitened log | own design | 10.30 | 1.16 | 3.34 | 4.46 | 3.09 | established (≥ 3×) | 1.85 | not separable (< 2×) | 2.09 |
| FB | Moderate − Mild (lobe_A) | whitened log | own design | 8.51 | 1.27 | 3.41 | 4.55 | 2.50 | sensitive (2–3×) | 1.50 | not separable (< 2×) | 1.72 |
| FB | Moderate − H7 (lobe_B) | whitened log | own design | 10.25 | 1.23 | 1.63 | 4.57 | 6.28 | established (≥ 3×) | 2.11 | sensitive (2–3×) | 2.24 |
| FB | Moderate − Mild (lobe_B) | whitened log | own design | 8.71 | 1.22 | 1.43 | 4.29 | 6.07 | established (≥ 3×) | 1.92 | not separable (< 2×) | 1.96 |
| FB | Mild − H6 (lobe_A, truth 0) | whitened log | own design | 2.30 | 1.16 | 0.97 | 4.21 | 1.98 | not separable (< 2×) | 0.53 | not separable (< 2×) | 0.55 |
| FB | Severe − H6 (lobe_A, truth 0) | whitened log | own design | 4.86 | 1.16 | 1.12 | 4.24 | 4.19 | established (≥ 3×) | 1.11 | not separable (< 2×) | 1.15 |

LR floor (rms over the 12 ring images × ±) per symmetric design, i.e. the candidates for LeftOnly's own unmeasurable floor:

| reference | method | Healthy_sliced_new | MCI_lobe_c3 | Mild_lobe | Moderate_lobe | Severe_lobe |
|---|---|---|---|---|---|---|
| H6 (matched) | Tikhonov dS | 1.16 | 0.40 | 0.31 | 4.04 | 0.96 |
| H6 (matched) | frozen log | 1.12 | 0.20 | 0.34 | 3.59 | 0.62 |
| H6 (matched) | whitened log | 0.84 | 0.20 | 0.15 | 3.02 | 0.47 |
| H7 (frozen, primary) | Tikhonov dS | 1.18 | 0.40 | 0.33 | 4.07 | 0.99 |
| H7 (frozen, primary) | frozen log | 1.12 | 0.20 | 0.36 | 3.59 | 0.63 |
| H7 (frozen, primary) | whitened log | 0.84 | 0.20 | 0.14 | 3.02 | 0.49 |

**Mechanism of the inconsistency.** §6b used a different verdict function (`lobe_c3.verdict`: hit if the call holds and the effect is ≥ 2× the ruler) from §5d (≥ 3× exceeds, 2–3× sensitive). That was an inconsistency, not a physical difference.
**Verdict: CHANGED.** LeftOnly LR, primary reference, conservative floor (largest symmetric-design floor, set by Moderate_lobe): Tikhonov dS 2.04× → sensitive (2–3×); frozen log 2.50× → sensitive (2–3×); whitened log 2.95× → sensitive (2–3×). With measurement errors (quadrature): Tikhonov dS 0.32×; frozen log 0.83×; whitened log 2.24×. The floor choice matters: with the floor of the pass-matched p6 designs (Healthy_sliced_new, MCI_lobe_c3) the clean ratios are Tikhonov dS 3.88× (established (≥ 3×)); frozen log 4.10× (established (≥ 3×)); whitened log 5.51× (established (≥ 3×)). LeftOnly's own floor cannot be measured (it is not mirror-symmetric), so the conservative label stands: **left/right = sensitive at best, not established**; pre-registered verdict PARTIAL kept alongside. Front/back on the same bar: Moderate − H6 (lobe_A) 2.22× (sensitive (2–3×)), Moderate − H7 (lobe_B) 4.70× (established (≥ 3×)), but the truth-zero Mild − H6 FB is 3.04× (established (≥ 3×)): the clean ruler does not bound the systematic front bias, so front/back stays 'not established'.

## B2. Is +8.5 bias plus leakage?

(a) Key `b2a`: LR of every mirror-symmetric design through the identical pipeline (true LR = 0):

| design | H6 (matched) Tikhonov dS | H6 (matched) frozen log | H6 (matched) whitened log | H7 (frozen, primary) Tikhonov dS | H7 (frozen, primary) frozen log | H7 (frozen, primary) whitened log |
|---|---|---|---|---|---|---|
| Healthy_sliced | +0.34 | +0.29 | -0.07 | n/a | n/a | n/a |
| Healthy_sliced_new | n/a | n/a | n/a | -0.36 | -0.29 | +0.05 |
| MCI_lobe_c3 | +1.37 | +0.91 | +0.62 | +1.02 | +0.58 | +0.64 |
| Mild_lobe | +0.35 | -0.28 | +0.05 | -0.04 | -0.67 | -0.08 |
| Mild_lobe_new | +0.87 | +0.32 | +0.27 | +0.52 | -0.10 | +0.13 |
| Moderate_lobe | -3.54 | -3.55 | -2.98 | -3.92 | -3.93 | -3.08 |
| Moderate_lobe_c3 | -1.40 | -1.11 | -1.12 | -1.74 | -1.52 | -1.23 |
| Severe_lobe | -0.43 | -0.53 | -0.49 | -0.80 | -0.97 | -0.68 |
| Severe_lobe_c3 | +0.74 | +0.51 | +0.16 | +0.41 | +0.01 | -0.08 |

Primary method, primary reference: LR ranges -3.92 … +1.02; 3 positive, 5 negative; mean -0.61. No consistent sign; the largest is Moderate_lobe (negative, i.e. towards the right), the largest positive is MCI_lobe_c3 (+1.02).
(b) Key `b2b`: exactly mirror-symmetrised kernels (K → ½[K + mirror(K)]; frozen kernel mirror asymmetry 6.4%) and symmetrised noise weights: LeftOnly LR +8.80 (frozen kernels +8.48); asymmetry-free LR_anti +7.93 (frozen +7.86). With symmetric kernels the doubly mirrored input gives exactly −LR (-8.80), confirming the symmetrised pipeline is mirror-equivariant.

**Mechanism.** Kernel asymmetry contributes -0.32 to LR. The reference's own mirror asymmetry contributes half of LR_sum (+0.62). The rest, +7.86, is the mirror-antisymmetric part of the LeftOnly data. The symmetric designs' LR (a) is negative as often as positive, so a consistent left-leaning bias is not there to explain +8.5.
**Verdict: CONFIRMED** that +8.5 is not kernel bias or a consistent design bias: ≈ 7.9 of it is antisymmetric data. Whether that antisymmetric data part is lobe or numerical asymmetry is B3/B9.

## B3. Mirror test

Key `b3`: mirror(LeftOnly) = LeftOnly with ports T2↔T6, T3↔T5, against the same (unmirrored) reference; 'mirror_both' mirrors the reference too.

| reference | method | LR_left | LR_mirror | LR_sum | LR_anti | LR_mirror_both | S2 | S3 | S5 | S6 | mirror_S2 | mirror_S3 | mirror_S5 | mirror_S6 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 (frozen, primary) | Tikhonov dS | +8.48 | -7.24 | +1.24 | +7.86 | -8.96 | +13.11 | +15.02 | +4.97 | +6.19 | +5.95 | +6.74 | +13.01 | +14.16 |
| H7 (frozen, primary) | frozen log | +9.25 | -8.26 | +0.99 | +8.75 | -10.01 | +12.62 | +15.47 | +4.45 | +5.14 | +4.73 | +6.07 | +13.54 | +13.78 |
| H7 (frozen, primary) | whitened log | +9.27 | -8.11 | +1.16 | +8.69 | -9.79 | +12.20 | +14.95 | +4.19 | +4.43 | +4.39 | +5.56 | +13.26 | +12.92 |
| H6 (matched) | Tikhonov dS | +8.82 | -6.90 | +1.92 | +7.86 | -9.17 | +11.14 | +12.28 | +2.57 | +3.22 | +3.96 | +4.04 | +10.59 | +11.19 |
| H6 (matched) | frozen log | +9.70 | -7.95 | +1.75 | +8.82 | -10.13 | +11.53 | +13.61 | +2.75 | +2.99 | +3.56 | +4.15 | +11.93 | +11.67 |
| H6 (matched) | whitened log | +9.41 | -8.13 | +1.28 | +8.77 | -9.75 | +11.19 | +13.26 | +2.85 | +2.77 | +3.27 | +3.78 | +12.01 | +11.32 |

Key `b3_rulers`: the two estimators through the rulers (each estimator applied to the yardstick, floor and noise inputs):

| reference | method | estimator | floor_from | clean | yard | floor | sd_noise | sd_±0.5 dB gain | ratio_clean | bar_clean | ratio_meas_quad | bar_meas |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 (frozen, primary) | Tikhonov dS | LR_anti = (LR − LR_mirror)/2 | max of lobe_A symmetric designs | 7.86 | 3.00 | 4.34 | 1.69 | 19.08 | 1.81 | not separable (< 2×) | 0.40 | not separable (< 2×) |
| H7 (frozen, primary) | Tikhonov dS | LR_anti = (LR − LR_mirror)/2 | pass-matched p6 designs (H6, MCI_c3) | 7.86 | 3.00 | 1.90 | 1.69 | 19.08 | 2.62 | sensitive (2–3×) | 0.41 | not separable (< 2×) |
| H7 (frozen, primary) | Tikhonov dS | LR_sum = LR + LR_mirror | max of lobe_A symmetric designs | 1.24 | 1.99 | 2.44 | 3.45 | 38.66 | 0.51 | not separable (< 2×) | 0.03 | not separable (< 2×) |
| H7 (frozen, primary) | Tikhonov dS | LR_sum = LR + LR_mirror | pass-matched p6 designs (H6, MCI_c3) | 1.24 | 1.99 | 2.44 | 3.45 | 38.66 | 0.51 | not separable (< 2×) | 0.03 | not separable (< 2×) |
| H7 (frozen, primary) | frozen log | LR_anti = (LR − LR_mirror)/2 | max of lobe_A symmetric designs | 8.75 | 3.07 | 3.90 | 1.77 | 7.54 | 2.25 | sensitive (2–3×) | 1.03 | not separable (< 2×) |
| H7 (frozen, primary) | frozen log | LR_anti = (LR − LR_mirror)/2 | pass-matched p6 designs (H6, MCI_c3) | 8.75 | 3.07 | 1.89 | 1.77 | 7.54 | 2.85 | sensitive (2–3×) | 1.13 | not separable (< 2×) |
| H7 (frozen, primary) | frozen log | LR_sum = LR + LR_mirror | max of lobe_A symmetric designs | 0.99 | 2.26 | 2.49 | 3.82 | 15.45 | 0.40 | not separable (< 2×) | 0.06 | not separable (< 2×) |
| H7 (frozen, primary) | frozen log | LR_sum = LR + LR_mirror | pass-matched p6 designs (H6, MCI_c3) | 0.99 | 2.26 | 2.49 | 3.82 | 15.45 | 0.40 | not separable (< 2×) | 0.06 | not separable (< 2×) |
| H7 (frozen, primary) | whitened log | LR_anti = (LR − LR_mirror)/2 | max of lobe_A symmetric designs | 8.69 | 2.63 | 3.36 | 1.75 | 1.91 | 2.59 | sensitive (2–3×) | 2.25 | sensitive (2–3×) |
| H7 (frozen, primary) | whitened log | LR_anti = (LR − LR_mirror)/2 | pass-matched p6 designs (H6, MCI_c3) | 8.69 | 2.63 | 1.68 | 1.75 | 1.91 | 3.31 | established (≥ 3×) | 3.31 | established (≥ 3×) |
| H7 (frozen, primary) | whitened log | LR_sum = LR + LR_mirror | max of lobe_A symmetric designs | 1.16 | 2.01 | 2.39 | 3.96 | 3.72 | 0.48 | not separable (< 2×) | 0.26 | not separable (< 2×) |
| H7 (frozen, primary) | whitened log | LR_sum = LR + LR_mirror | pass-matched p6 designs (H6, MCI_c3) | 1.16 | 2.01 | 2.39 | 3.96 | 3.72 | 0.48 | not separable (< 2×) | 0.26 | not separable (< 2×) |
| H6 (matched) | Tikhonov dS | LR_anti = (LR − LR_mirror)/2 | max of lobe_A symmetric designs | 7.86 | 3.26 | 4.50 | 1.68 | 18.74 | 1.75 | not separable (< 2×) | 0.41 | not separable (< 2×) |
| H6 (matched) | Tikhonov dS | LR_anti = (LR − LR_mirror)/2 | pass-matched p6 designs (H6, MCI_c3) | 7.86 | 3.26 | 2.30 | 1.68 | 18.74 | 2.41 | sensitive (2–3×) | 0.42 | not separable (< 2×) |
| H6 (matched) | Tikhonov dS | LR_sum = LR + LR_mirror | max of lobe_A symmetric designs | 1.92 | 2.50 | 3.22 | 3.50 | 36.09 | 0.60 | not separable (< 2×) | 0.05 | not separable (< 2×) |
| H6 (matched) | Tikhonov dS | LR_sum = LR + LR_mirror | pass-matched p6 designs (H6, MCI_c3) | 1.92 | 2.50 | 3.22 | 3.50 | 36.09 | 0.60 | not separable (< 2×) | 0.05 | not separable (< 2×) |
| H6 (matched) | frozen log | LR_anti = (LR − LR_mirror)/2 | max of lobe_A symmetric designs | 8.82 | 3.24 | 4.06 | 1.79 | 7.64 | 2.17 | sensitive (2–3×) | 1.02 | not separable (< 2×) |
| H6 (matched) | frozen log | LR_anti = (LR − LR_mirror)/2 | pass-matched p6 designs (H6, MCI_c3) | 8.82 | 3.24 | 2.21 | 1.79 | 7.64 | 2.72 | sensitive (2–3×) | 1.11 | not separable (< 2×) |
| H6 (matched) | frozen log | LR_sum = LR + LR_mirror | max of lobe_A symmetric designs | 1.75 | 2.74 | 3.09 | 4.23 | 14.82 | 0.56 | not separable (< 2×) | 0.12 | not separable (< 2×) |
| H6 (matched) | frozen log | LR_sum = LR + LR_mirror | pass-matched p6 designs (H6, MCI_c3) | 1.75 | 2.74 | 3.09 | 4.23 | 14.82 | 0.56 | not separable (< 2×) | 0.12 | not separable (< 2×) |
| H6 (matched) | whitened log | LR_anti = (LR − LR_mirror)/2 | max of lobe_A symmetric designs | 8.77 | 2.58 | 3.34 | 1.77 | 1.93 | 2.63 | sensitive (2–3×) | 2.27 | sensitive (2–3×) |
| H6 (matched) | whitened log | LR_anti = (LR − LR_mirror)/2 | pass-matched p6 designs (H6, MCI_c3) | 8.77 | 2.58 | 1.65 | 1.77 | 1.93 | 3.40 | established (≥ 3×) | 3.40 | established (≥ 3×) |
| H6 (matched) | whitened log | LR_sum = LR + LR_mirror | max of lobe_A symmetric designs | 1.28 | 1.93 | 2.30 | 4.41 | 4.25 | 0.56 | not separable (< 2×) | 0.26 | not separable (< 2×) |
| H6 (matched) | whitened log | LR_sum = LR + LR_mirror | pass-matched p6 designs (H6, MCI_c3) | 1.28 | 1.93 | 2.30 | 4.41 | 4.25 | 0.56 | not separable (< 2×) | 0.26 | not separable (< 2×) |

**Result.** LR(mirror) = -7.24 against LR(LeftOnly) = +8.48 (primary); S3 15.0 → mirror S5 13.0, S2 13.1 → mirror S6 14.2. LR + LR_mirror = +1.24 = Tikhonov dS 0.51×, frozen log 0.40×, whitened log 0.48× the clean ruler of that estimator (≈ 0 as required). Asymmetry-free LR_anti against the clean ruler: Tikhonov dS 1.81× (max of lobe_A symmetric designs); Tikhonov dS 2.62× (pass-matched p6 designs); frozen log 2.25× (max of lobe_A symmetric designs); frozen log 2.85× (pass-matched p6 designs); whitened log 2.59× (max of lobe_A symmetric designs); whitened log 3.31× (pass-matched p6 designs). With measurement errors: Tikhonov dS 0.40×; frozen log 1.03×; whitened log 2.25×.
**Verdict: CONFIRMED (the sign is in the data), but not established in size.** The mirror test is passed: the sign follows the data, not kernel or mesh asymmetry of the pipeline. The asymmetry-free estimate is 1.8–2.6× the clean ruler with the conservative floor (not separable / sensitive); with the pass-matched floor 2.6–3.3×; with measurement errors ≤ 3.3×.

## B4. The matched reference

Key `b4`: the pre-registered criterion with each reference:

| method | reference | S2 | S3 | T_abs | LR | side | called | preregistered |
|---|---|---|---|---|---|---|---|---|
| tikhonov dS | H7 (frozen, primary) | 13.11 | 15.02 | 13.81 | +8.48 | left | S3 | PARTIAL |
| tikhonov dS | H6 (matched) | 11.14 | 12.28 | 13.81 | +8.82 | left | none | FAIL |
| bounded dS | H7 (frozen, primary) | 13.11 | 15.02 | 13.81 | +8.48 | left | S3 | PARTIAL |
| bounded dS | H6 (matched) | 11.14 | 12.28 | 13.81 | +8.82 | left | none | FAIL |
| tikhonov log (gain-inv.) | H7 (frozen, primary) | 12.62 | 15.47 | 13.32 | +9.25 | left | S3 | PARTIAL |
| tikhonov log (gain-inv.) | H6 (matched) | 11.53 | 13.61 | 13.32 | +9.70 | left | S3 | PARTIAL |
| bounded log (gain-inv.) | H7 (frozen, primary) | 12.62 | 15.47 | 13.32 | +9.25 | left | S3 | PARTIAL |
| bounded log (gain-inv.) | H6 (matched) | 11.53 | 13.61 | 13.32 | +9.70 | left | S3 | PARTIAL |

Key `b4_mech`: per-sector shift H7 → H6 for LeftOnly (primary method) against the inversion of the one-pass difference −(Healthy_sliced − Healthy_sliced_new):

| sector | x_H7 | x_H6 | shift | one_pass |
|---|---|---|---|---|
| S1 | +5.17 | +3.00 | -2.17 | +2.16 |
| S2 | +13.11 | +11.14 | -1.97 | +1.98 |
| S3 | +15.02 | +12.28 | -2.73 | +2.70 |
| S4 | +5.62 | +3.40 | -2.22 | +2.16 |
| S5 | +4.97 | +2.57 | -2.40 | +2.39 |
| S6 | +6.19 | +3.22 | -2.97 | +2.97 |

**Mechanism.** The reconstruction is linear, so changing the reference moves every sector by the inversion of H7 − H6 (≈ −2 to −3, nearly uniform). Its sign is the opposite of the one-pass row because that row inverts +(H6 − H7) as a stage; the magnitudes agree to ≤ 0.05. T_abs was calibrated on Mild against H7, so it sits in the H7 frame. The LR contrast barely moves (+8.48 → +8.82) because the shift is common to all sectors.
**Verdict: CHANGED (stated plainly).** With the matched reference the primary method calls **nothing** (S2 11.1, S3 12.3 < 13.8): pre-registered verdict **FAIL**; the frozen log method gives PARTIAL (S3 13.6). The reader should not trust the primary sector calls more than the matched ones. The 7-pass reference is primary only because it was pre-registered and because T_abs lives in its frame. Neither reference makes the absolute sector calls robust: they move by the size of one mesh pass. Only the side call is reference-invariant.

## B5. Whitened log: '3.0× with and without measurement errors'

Key `b1` (whitened log, primary reference): yardstick 1.68, floor 3.14, noise SD 2.59, ±0.5 dB spread 2.69, ±2 dB spread 2.86.
**Mechanism.** The old measured ruler was max(noise, yardstick, floor, spread). The whitened log removes per-port gains exactly, so its spread is only the typical measurement noise, 2.69. That is just below the floor (3.14). The max therefore picked the floor in both cases, and the ratio did not move. Measurement error did enter, but it was hidden by the max. Floor and measurement error are independent, so they add in quadrature: 2.24× (H7), 2.15× (H6).
**Multiplicity.** On LeftOnly LR, 10 method × reference combinations were scored (4 frozen methods + whitened log, × 2 references). Across §5c–§7 there were 5 methods × 2 path variants (all paths, no opposite paths) × 2 references = 20; the no-opposite variant was not run on LeftOnly. Treating ratio = z (a Gaussian ruler, which the yardstick and floor are not) and correcting with Bonferroni:

| comparison | ruler | ratio | p_one_sided_if_gaussian | p_bonferroni |
|---|---|---|---|---|
| LeftOnly − H7 (frozen, primary) | clean | 2.95 | 0.0016 | 0.016 |
| LeftOnly − H7 (frozen, primary) | meas_quad | 2.24 | 0.0125 | 0.125 |
| LeftOnly − H7 (frozen, primary) | meas_max_old | 2.95 | 0.0016 | 0.016 |
| LeftOnly − H6 (matched) | clean | 3.00 | 0.0014 | 0.014 |
| LeftOnly − H6 (matched) | meas_quad | 2.15 | 0.0158 | 0.158 |
| LeftOnly − H6 (matched) | meas_max_old | 3.00 | 0.0014 | 0.014 |

(× 20 looks doubles p_bonferroni.) The whitened log was added in commit 9182afd (2026-10-04 03:28:59 +0530), before the LeftOnly file existed (file time 2026-10-04 09:27:31). It was introduced because the frozen log method leaks port gains, not because of any LeftOnly result.
**Verdict: CHANGED.** '3.0× with and without' → 2.95× clean / 2.24× measured. After multiplicity correction the measured value is not significant (p_bonf 0.13 / 0.16 for 10 looks).

## B6. Born validity

Key `b6`: κ-scaled Born prediction of ΔS from the true sector maps against the HFSS ΔS, at the fit frequencies; relative error ‖pred − obs‖ / ‖obs‖ per path class. Also the antisymmetric part (path minus its mirror path), and what the frozen inversion makes of the prediction (LR pred) versus the data (LR obs).

| design | reference | reflection | neighbour | second-neighbour | opposite | all | antisym part: |pred − obs| / |obs| | LR pred Tikhonov dS | LR obs Tikhonov dS | LR pred frozen log | LR obs frozen log |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mild_lobe | H7 (frozen, primary) | 0.59 | 0.42 | 0.97 | 1.23 | 0.59 | 1.18 | 0.16 | -0.04 | -0.13 | -0.67 |
| Mild_lobe | H6 (matched) | 0.57 | 0.34 | 0.97 | 1.25 | 0.57 | 1.17 | 0.15 | 0.35 | -0.11 | -0.28 |
| Moderate_lobe | H7 (frozen, primary) | 0.56 | 0.30 | 0.72 | 1.10 | 0.56 | 1.20 | 0.35 | -3.92 | -0.13 | -3.93 |
| Moderate_lobe | H6 (matched) | 0.60 | 0.33 | 0.75 | 0.95 | 0.60 | 1.18 | 0.33 | -3.54 | -0.10 | -3.55 |
| Severe_lobe | H7 (frozen, primary) | 0.61 | 0.39 | 0.87 | 1.08 | 0.61 | 1.29 | 1.14 | -0.80 | 1.35 | -0.97 |
| Severe_lobe | H6 (matched) | 0.66 | 0.42 | 0.94 | 0.95 | 0.65 | 1.08 | 1.11 | -0.43 | 1.37 | -0.53 |
| LeftOnly_test | H7 (frozen, primary) | 0.57 | 0.39 | 0.70 | 0.99 | 0.57 | 0.96 | 15.01 | 8.48 | 15.05 | 9.25 |
| LeftOnly_test | H6 (matched) | 0.67 | 0.60 | 0.65 | 0.85 | 0.67 | 0.92 | 15.00 | 8.82 | 15.01 | 9.70 |
| MCI_lobe | H7 (frozen, primary) | 1.00 | 1.00 | 1.01 | 1.01 | 1.00 | 1.00 | 0.01 | 1.02 | 0.02 | 0.58 |
| MCI_lobe | H6 (matched) | 1.00 | 1.00 | 1.01 | 1.01 | 1.00 | 1.00 | 0.01 | 1.37 | 0.02 | 0.91 |

Whitened norms (primary model, H7): Born error on Mild 16.2 against the entire LeftOnly signal 14.7; antisymmetric parts: Mild model error 3.6 against LeftOnly 5.0.
**Mechanism.** The kernels use the healthy-head fields, but the perturbation replaces 7.5–18 mm of cortex with CSF and changes CSF everywhere. After the best κ the linear model still misses 56%–67% of ΔS; the second-neighbour and opposite paths, whose |S| is small, are missed by 65%–125%. MCI is all error (≈ 1.0) because its true sector change is zero.
**Verdict: CHANGED (new quantification).** The linearisation error is comparable to the LeftOnly signal. The Born prediction gives LR +15.0 against the observed +8.5, a model error of 6.5 (≈ 77% of the signal). The relative error of the antisymmetric part is 0.96. The pre-registered +14.7 ± 2.2 never had a valid model-error term.

## B7. Fit frequencies

**Why 3.4/3.6/3.8 GHz.** The Born kernels need the HFSS field exports, and those exist only at these three frequencies (`data/fields`: E_Normal_T1_3p4GHz.fld, E_Normal_T1_3p6GHz.fld, E_Normal_T1_3p6GHz_wide.fld, E_Normal_T1_3p8GHz.fld; 3-point discrete sweep). Data were never searched over frequency.

Key `b7` (primary reference): every subset of the three field frequencies, plus linearly interpolated kernels at 3.5/3.7 and 3.45–3.75 GHz:

| frequencies | method | S2 | S3 | S5 | S6 | LR | LR_anti | side | S3_called | S2_called |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.4/3.6/3.8 (frozen) | Tikhonov dS | +13.11 | +15.02 | +4.97 | +6.19 | +8.48 | +7.86 | left | True | False |
| 3.4/3.6/3.8 (frozen) | frozen log | +12.62 | +15.47 | +4.45 | +5.14 | +9.25 | +8.75 | left | True | False |
| 3.4/3.6/3.8 (frozen) | whitened log | +12.20 | +14.95 | +4.19 | +4.43 | +9.27 | +8.69 | n/a | n/a | n/a |
| 3.4 | Tikhonov dS | +13.58 | +15.07 | +5.64 | +6.17 | +8.42 | +8.52 | left | True | False |
| 3.4 | frozen log | +14.71 | +17.08 | +6.62 | +6.26 | +9.46 | +9.51 | left | True | True |
| 3.4 | whitened log | +15.00 | +17.00 | +6.56 | +6.49 | +9.48 | +9.50 | n/a | n/a | n/a |
| 3.6 | Tikhonov dS | +10.39 | +12.52 | +3.40 | +5.66 | +6.93 | +5.63 | left | False | False |
| 3.6 | frozen log | +9.24 | +11.57 | +2.34 | +5.59 | +6.44 | +5.37 | left | False | False |
| 3.6 | whitened log | +7.87 | +10.36 | +2.35 | +4.56 | +5.66 | +4.54 | n/a | n/a | n/a |
| 3.8 | Tikhonov dS | +5.13 | +4.85 | +4.24 | +3.53 | +1.11 | +0.57 | none | False | False |
| 3.8 | frozen log | +2.57 | +3.00 | +2.07 | +1.31 | +1.10 | +0.98 | none | False | False |
| 3.8 | whitened log | +1.55 | +2.46 | +1.74 | -0.13 | +1.20 | +0.61 | n/a | n/a | n/a |
| 3.4/3.6 | Tikhonov dS | +13.33 | +15.63 | +4.78 | +6.38 | +8.90 | +8.38 | left | True | False |
| 3.4/3.6 | frozen log | +13.26 | +16.10 | +4.62 | +5.90 | +9.42 | +9.03 | left | True | False |
| 3.4/3.6 | whitened log | +12.94 | +15.58 | +4.45 | +5.41 | +9.33 | +8.90 | n/a | n/a | n/a |
| 3.4/3.8 | Tikhonov dS | +13.04 | +14.16 | +5.59 | +5.79 | +7.91 | +7.75 | left | True | False |
| 3.4/3.8 | frozen log | +13.33 | +15.86 | +5.85 | +4.79 | +9.28 | +9.10 | left | True | True |
| 3.4/3.8 | whitened log | +13.29 | +15.74 | +5.61 | +4.51 | +9.45 | +9.19 | n/a | n/a | n/a |
| 3.6/3.8 | Tikhonov dS | +10.55 | +11.99 | +4.21 | +5.70 | +6.32 | +5.04 | left | False | False |
| 3.6/3.8 | frozen log | +8.79 | +10.91 | +2.56 | +4.78 | +6.18 | +5.13 | left | False | False |
| 3.6/3.8 | whitened log | +7.42 | +9.84 | +2.49 | +3.48 | +5.65 | +4.39 | n/a | n/a | n/a |
| 3.5/3.7 (interp.) | Tikhonov dS | -4.71 | -4.11 | +1.46 | -1.87 | -4.20 | -2.18 | right | False | False |
| 3.5/3.7 (interp.) | frozen log | -3.93 | -4.14 | +1.44 | -0.14 | -4.68 | -2.74 | right | False | False |
| 3.5/3.7 (interp.) | whitened log | -0.87 | +0.00 | +3.16 | +0.97 | -2.50 | -1.01 | n/a | n/a | n/a |
| 3.45/3.55/3.65/3.75 (interp.) | Tikhonov dS | +5.27 | +6.72 | +0.80 | +0.86 | +5.16 | +5.83 | left | False | False |
| 3.45/3.55/3.65/3.75 (interp.) | frozen log | +3.40 | +6.34 | +1.36 | +2.01 | +3.18 | +4.15 | none | False | False |
| 3.45/3.55/3.65/3.75 (interp.) | whitened log | +3.45 | +4.88 | -0.13 | +1.90 | +3.28 | +4.08 | n/a | n/a | n/a |
| 3.4–3.8 step 0.1 (3.5, 3.7 interp.) | Tikhonov dS | +8.45 | +10.73 | +4.21 | +3.18 | +5.90 | +5.83 | left | False | False |
| 3.4–3.8 step 0.1 (3.5, 3.7 interp.) | frozen log | +8.04 | +10.97 | +3.65 | +2.82 | +6.27 | +6.24 | left | False | False |
| 3.4–3.8 step 0.1 (3.5, 3.7 interp.) | whitened log | +8.64 | +11.89 | +4.11 | +2.58 | +6.92 | +6.70 | n/a | n/a | n/a |

**Interpolation is invalid** (key `b7_val`). The kernel phase rotates by a median 62° per 200 MHz; the 3.6 GHz kernel predicted from 3.4/3.8 has 4.8× relative error; LR at 3.6 GHz with the interpolated kernel is +0.23 against +6.93 with the true one. The interpolated rows, including the apparent sign flip at 3.5/3.7, carry no information.

Key `b7_band` (data only, no kernels): left-minus-right phase change of each mirror pair of paths, LeftOnly − H7, across the band:

| f_GHz | T1-T2 − T1-T6 (deg) | T1-T3 − T1-T5 (deg) | T2 refl. − T6 refl. (deg) | T2-T3 − T5-T6 (deg) | T2-T4 − T4-T6 (deg) | T3 refl. − T5 refl. (deg) | T3-T4 − T4-T5 (deg) |
|---|---|---|---|---|---|---|---|
| 3.3 | -3.1 | +2.8 | +0.3 | -5.0 | +5.1 | +0.7 | -3.4 |
| 3.35 | -3.6 | +2.9 | +1.4 | -5.7 | +3.5 | +2.2 | -3.9 |
| 3.4 | -3.6 | +3.8 | +4.3 | -5.6 | +5.1 | +5.1 | -4.0 |
| 3.45 | -3.0 | +5.9 | +5.2 | -5.3 | +7.8 | +4.1 | -3.8 |
| 3.5 | -2.3 | +7.8 | -1.3 | -5.3 | +11.4 | -3.6 | -4.2 |
| 3.55 | +0.3 | +16.1 | -1.2 | -5.0 | +16.6 | -2.6 | -5.3 |
| 3.6 | -1.8 | +11.7 | +0.2 | -4.8 | -2.1 | -0.9 | -4.2 |
| 3.65 | -3.2 | +5.6 | -2.0 | -1.7 | -5.0 | -2.7 | -3.3 |
| 3.7 | -3.1 | +9.2 | -0.9 | +0.1 | +0.7 | -1.8 | -3.1 |
| 3.75 | -1.6 | +8.9 | +0.2 | -1.1 | +7.7 | -0.7 | -0.3 |
| 3.8 | +0.2 | +0.8 | -0.4 | -1.0 | +6.9 | -0.5 | +0.7 |
| 3.85 | +0.2 | +4.5 | -1.1 | -0.9 | +14.4 | -0.1 | +0.9 |
| 3.9 | -1.7 | +0.3 | -0.3 | -3.2 | +2.1 | -0.1 | +0.1 |

**Mechanism.** The dominant pair (T2–T3 against T5–T6) carries a −5 to −6° left/right phase difference from 3.30 to 3.65 GHz that fades to ≈ 0 to −1° from 3.70 to 3.85 GHz; other pairs vary more erratically. So the LeftOnly asymmetry sits in the lower half of the band, and the 3.8 GHz kernel sees almost none of it.
**Verdict: CHANGED (frequency dependent); CANNOT TELL for 3.3/3.5/3.7 GHz.** Over the true-field subsets the side is 'left' whenever 3.4 or 3.6 GHz is included (Tikhonov dS LR 3.4/3.6/3.8 +8.5, 3.4 +8.4, 3.6 +6.9, 3.8 +1.1, 3.4/3.6 +8.9, 3.4/3.8 +7.9, 3.6/3.8 +6.3). It is 'none' at 3.8 GHz alone. S3 is called only when 3.4 GHz is included. Other frequencies can only be tested with field exports at them.

## B8. Calibration re-derived on lobe_A (diagnostic)

Key `b8_meta`: lobe_A recipe (κ on Mild_lobe vs Healthy_sliced_new, GCV λ on Mild, nulls, T_mild) → |κ| 2.91, 3.26, 4.97 (frozen 3.29, 3.60, 6.38); λ dS 0.126 (frozen 0.158), log 0.100 (frozen 0.126); T_abs tikhonov dS 13.52 (frozen 13.81), bounded dS 13.52 (frozen 13.81), tikhonov log 13.31 (frozen 13.32), bounded log 13.31 (frozen 13.32).

Key `b8`: calls (affected sectors | side | front/back) with the frozen and the lobe_A-derived calibration:

| design | reference | method | frozen | lobe_A_rules | flip | S3_frozen | S3_lobeA | LR_frozen | LR_lobeA |
|---|---|---|---|---|---|---|---|---|---|
| LeftOnly | H6 | tikhonov dS | none | left | none | S3 | left | none | True | 12.28 | 14.79 | 8.82 | 10.43 |
| LeftOnly | H6 | bounded dS | none | left | none | S3 | left | none | True | 12.28 | 14.79 | 8.82 | 10.43 |
| LeftOnly | H6 | tikhonov log (gain-inv.) | S3 | left | none | S2 S3 | left | none | True | 13.61 | 16.10 | 9.70 | 11.25 |
| LeftOnly | H6 | bounded log (gain-inv.) | S3 | left | none | S2 S3 | left | none | True | 13.61 | 16.10 | 9.70 | 11.25 |
| LeftOnly | H7 | tikhonov dS | S3 | left | none | S2 S3 | left | none | True | 15.02 | 17.85 | 8.48 | 10.05 |
| LeftOnly | H7 | bounded dS | S3 | left | none | S2 S3 | left | none | True | 15.02 | 17.85 | 8.48 | 10.05 |
| LeftOnly | H7 | tikhonov log (gain-inv.) | S3 | left | none | S2 S3 | left | none | True | 15.47 | 18.09 | 9.25 | 10.78 |
| LeftOnly | H7 | bounded log (gain-inv.) | S3 | left | none | S2 S3 | left | none | True | 15.47 | 18.09 | 9.25 | 10.78 |
| MCI | H6 | tikhonov dS | none | none | none | none | none | none | False | 0.24 | 0.33 | 1.37 | 1.51 |
| MCI | H6 | bounded dS | none | none | none | none | none | none | False | 0.21 | 0.30 | 0.78 | 0.91 |
| MCI | H6 | tikhonov log (gain-inv.) | none | none | none | none | none | none | False | -0.02 | 0.06 | 0.91 | 0.93 |
| MCI | H6 | bounded log (gain-inv.) | none | none | none | none | none | none | False | 0.00 | 0.00 | 0.36 | 0.39 |
| MCI | H7 | tikhonov dS | none | none | none | none | none | none | False | 2.93 | 3.35 | 1.02 | 1.13 |
| MCI | H7 | bounded dS | none | none | none | none | none | none | False | 2.93 | 3.35 | 1.02 | 1.13 |
| MCI | H7 | tikhonov log (gain-inv.) | none | none | none | none | none | none | False | 1.94 | 2.21 | 0.58 | 0.62 |
| MCI | H7 | bounded log (gain-inv.) | none | none | none | none | none | none | False | 1.94 | 2.21 | 0.58 | 0.62 |
| Mild (B) | H7 | tikhonov dS | S2 S3 S6 | none | none | S2 S3 S5 S6 | none | none | True | 15.19 | 18.06 | 0.52 | 0.56 |
| Mild (B) | H7 | bounded dS | S2 S3 S6 | none | none | S2 S3 S5 S6 | none | none | True | 15.19 | 18.06 | 0.52 | 0.56 |
| Mild (B) | H7 | tikhonov log (gain-inv.) | S2 S3 S5 S6 | none | none | S2 S3 S5 S6 | none | none | False | 14.88 | 17.50 | -0.10 | -0.11 |
| Mild (B) | H7 | bounded log (gain-inv.) | S2 S3 S5 S6 | none | none | S2 S3 S5 S6 | none | none | False | 14.88 | 17.50 | -0.10 | -0.11 |
| Moderate (B) | H7 | tikhonov dS | S1 S3 S6 | none | front | S1 S2 S3 S5 S6 | none | front | True | 14.33 | 17.30 | -1.74 | -1.95 |
| Moderate (B) | H7 | bounded dS | S1 S3 S6 | none | front | S1 S2 S3 S5 S6 | none | front | True | 14.33 | 17.30 | -1.74 | -1.95 |
| Moderate (B) | H7 | tikhonov log (gain-inv.) | S1 S2 S3 S6 | none | front | S1 S2 S3 S5 S6 | none | front | True | 14.66 | 17.49 | -1.52 | -1.66 |
| Moderate (B) | H7 | bounded log (gain-inv.) | S1 S2 S3 S6 | none | front | S1 S2 S3 S5 S6 | none | front | True | 14.66 | 17.49 | -1.52 | -1.66 |
| Severe (B) | H7 | tikhonov dS | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | False | 18.30 | 22.45 | 0.41 | 0.47 |
| Severe (B) | H7 | bounded dS | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | False | 18.30 | 22.45 | 0.41 | 0.47 |
| Severe (B) | H7 | tikhonov log (gain-inv.) | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | False | 20.32 | 24.58 | 0.01 | -0.07 |
| Severe (B) | H7 | bounded log (gain-inv.) | S1 S2 S3 S4 S5 S6 | none | none | S1 S2 S3 S4 S5 S6 | none | none | False | 20.32 | 24.58 | 0.01 | -0.07 |

**Mechanism.** κ re-fitted against the 6-pass reference is 9%–22% smaller, so every recovered dε'' grows by the same factor. T_abs hardly changes (it is set by Mild's own gap). Sectors within ~2 of T_abs cross it.
**Verdict: CHANGED.** 14 of 28 design × reference × method calls flip; 0 of them change a side or front/back call, the rest are sector calls. LeftOnly with H7 becomes SUCCESS (S2 and S3) and with H6 goes from nothing to S3. Mild/Moderate (B) gain their missed sectors; MCI never flips. The sector calls are decided by the calibration at the 10–20 % level.

## B9. Where the +8.5 comes from

Key `b9_sum`: exact linear decomposition LR = Σ_paths (weight · data), split into the amplitude part (ln|S_L/S_ref|) and the phase part (arg S_L/S_ref):

| case | LR | sum_paths | amp | phase |
|---|---|---|---|---|
| H7 (frozen, primary)|tikhonov dS | +8.48 | +8.48 | +1.29 | +7.19 |
| H7 (frozen, primary)|tikhonov log (gain-inv.) | +9.25 | +9.25 | +1.11 | +8.13 |
| H7 (frozen, primary)|tikhonov log, whitened projection (post-hoc) | +9.27 | +9.27 | +1.33 | +7.93 |
| H6 (matched)|tikhonov dS | +8.82 | +8.82 | +1.14 | +7.67 |
| H6 (matched)|tikhonov log (gain-inv.) | +9.70 | +9.70 | +1.15 | +8.55 |
| H6 (matched)|tikhonov log, whitened projection (post-hoc) | +9.41 | +9.41 | +1.24 | +8.17 |

Key `b9_top`: five largest path contributions, with the raw changes at the fit frequencies, the largest one-pass change of that path, and the main session's band-power numbers and rulers for the same path (`results/05_lobe/tests/1_leftonly_paths.csv`):

| reference | method | path | mirror | contribution | from_amplitude | from_phase | mirror_contribution | weight | amp_change_dB_fit | phase_change_deg_fit | one_pass_max_amp_dB_fit | one_pass_max_phase_deg_fit | band_power_dB | main_observed_dB | main_over_yardstick | main_over_floor | main_over_spread_05 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 (frozen, primary) | Tikhonov dS | T2-T3 | T5-T6 | +7.37 | +0.69 | +6.68 | -3.54 | 31.54 | +0.50, +0.09, +0.02 | -10.2, -8.4, -4.5 | 0.16 | 5.56 | 0.11 | 0.11 | 1.66 | 0.98 | 0.18 |
| H7 (frozen, primary) | Tikhonov dS | T5-T6 | T2-T3 | -3.54 | -0.33 | -3.21 | +7.37 | 30.18 | +0.10, +0.18, -0.17 | -4.6, -3.6, -3.5 | 0.22 | 6.32 | -0.03 | -0.03 | 0.43 | 0.23 | 0.04 |
| H7 (frozen, primary) | Tikhonov dS | T3-T4 | T4-T5 | +2.92 | +0.35 | +2.57 | -1.56 | 15.23 | +0.43, +0.14, -0.58 | -7.6, -6.8, -1.7 | 0.20 | 4.63 | -0.12 | -0.12 | 3.04 | 1.11 | 0.20 |
| H7 (frozen, primary) | Tikhonov dS | T1-T2 | T1-T6 | +2.40 | +0.24 | +2.16 | -1.47 | 13.88 | +0.40, +0.21, -0.33 | -6.9, -5.7, -2.3 | 0.22 | 5.15 | 0.05 | 0.05 | 0.99 | 0.43 | 0.08 |
| H7 (frozen, primary) | Tikhonov dS | T4-T5 | T3-T4 | -1.56 | -0.35 | -1.21 | +2.92 | 15.52 | +0.18, +0.37, -0.25 | -3.6, -2.6, -2.4 | 0.40 | 5.78 | 0.08 | 0.08 | 0.93 | 0.68 | 0.12 |
| H7 (frozen, primary) | frozen log | T2-T3 | T5-T6 | +7.27 | +0.58 | +6.69 | -3.38 | 29.80 | +0.50, +0.09, +0.02 | -10.2, -8.4, -4.5 | 0.16 | 5.56 | 0.11 | 0.11 | 1.66 | 0.98 | 0.18 |
| H7 (frozen, primary) | frozen log | T5-T6 | T2-T3 | -3.38 | -0.25 | -3.13 | +7.27 | 29.40 | +0.10, +0.18, -0.17 | -4.6, -3.6, -3.5 | 0.22 | 6.32 | -0.03 | -0.03 | 0.43 | 0.23 | 0.04 |
| H7 (frozen, primary) | frozen log | T3-T4 | T4-T5 | +2.88 | +0.30 | +2.58 | -1.43 | 15.33 | +0.43, +0.14, -0.58 | -7.6, -6.8, -1.7 | 0.20 | 4.63 | -0.12 | -0.12 | 3.04 | 1.11 | 0.20 |
| H7 (frozen, primary) | frozen log | T1-T2 | T1-T6 | +2.26 | +0.19 | +2.06 | -1.46 | 14.07 | +0.40, +0.21, -0.33 | -6.9, -5.7, -2.3 | 0.22 | 5.15 | 0.05 | 0.05 | 0.99 | 0.43 | 0.08 |
| H7 (frozen, primary) | frozen log | T2 refl. | T6 refl. | +1.55 | +0.16 | +1.39 | -0.52 | 16.47 | -0.38, +0.02, +0.04 | +7.5, -2.7, -2.7 | 0.24 | 2.46 | -0.06 | -0.06 | 1.68 | 7.31 | 0.07 |
| H7 (frozen, primary) | whitened log | T2-T3 | T5-T6 | +6.36 | +0.55 | +5.81 | -2.89 | 26.78 | +0.50, +0.09, +0.02 | -10.2, -8.4, -4.5 | 0.16 | 5.56 | 0.11 | 0.11 | 1.66 | 0.98 | 0.18 |
| H7 (frozen, primary) | whitened log | T5-T6 | T2-T3 | -2.89 | -0.24 | -2.65 | +6.36 | 26.37 | +0.10, +0.18, -0.17 | -4.6, -3.6, -3.5 | 0.22 | 6.32 | -0.03 | -0.03 | 0.43 | 0.23 | 0.04 |
| H7 (frozen, primary) | whitened log | T3-T4 | T4-T5 | +2.47 | +0.27 | +2.20 | -1.23 | 13.74 | +0.43, +0.14, -0.58 | -7.6, -6.8, -1.7 | 0.20 | 4.63 | -0.12 | -0.12 | 3.04 | 1.11 | 0.20 |
| H7 (frozen, primary) | whitened log | T1-T2 | T1-T6 | +1.99 | +0.16 | +1.82 | -1.23 | 13.21 | +0.40, +0.21, -0.33 | -6.9, -5.7, -2.3 | 0.22 | 5.15 | 0.05 | 0.05 | 0.99 | 0.43 | 0.08 |
| H7 (frozen, primary) | whitened log | T2 refl. | T6 refl. | +1.86 | +0.20 | +1.66 | -0.54 | 19.55 | -0.38, +0.02, +0.04 | +7.5, -2.7, -2.7 | 0.24 | 2.46 | -0.06 | -0.06 | 1.68 | 7.31 | 0.07 |
| H6 (matched) | Tikhonov dS | T2-T3 | T5-T6 | +5.91 | +0.46 | +5.45 | -1.58 | 31.61 | +0.41, -0.04, +0.05 | -8.5, -7.6, -2.4 | 0.16 | 5.56 | 0.10 | 0.10 | 1.47 | 0.87 | 0.16 |
| H6 (matched) | Tikhonov dS | T3-T4 | T4-T5 | +2.03 | +0.21 | +1.82 | -0.82 | 15.26 | +0.31, -0.07, -0.41 | -6.1, -5.0, +0.2 | 0.20 | 4.63 | -0.12 | -0.12 | 3.05 | 1.12 | 0.20 |
| H6 (matched) | Tikhonov dS | T1-T2 | T1-T6 | +1.80 | +0.21 | +1.59 | -0.59 | 13.93 | +0.32, +0.20, -0.30 | -5.5, -4.5, -0.2 | 0.22 | 5.15 | 0.09 | 0.09 | 1.80 | 0.77 | 0.14 |
| H6 (matched) | Tikhonov dS | T5-T6 | T2-T3 | -1.58 | -0.08 | -1.50 | +5.91 | 30.19 | +0.02, +0.01, -0.15 | -2.7, -1.7, -0.5 | 0.22 | 6.32 | -0.06 | -0.06 | 0.91 | 0.50 | 0.09 |
| H6 (matched) | Tikhonov dS | T3 refl. | T5 refl. | +1.11 | +0.00 | +1.11 | -0.32 | 9.20 | -0.22, -0.01, -0.06 | +7.0, -1.9, -0.8 | 0.24 | 1.91 | -0.07 | -0.07 | 2.11 | 8.64 | 0.08 |
| H6 (matched) | frozen log | T2-T3 | T5-T6 | +6.00 | +0.41 | +5.59 | -1.68 | 29.98 | +0.41, -0.04, +0.05 | -8.5, -7.6, -2.4 | 0.16 | 5.56 | 0.10 | 0.10 | 1.47 | 0.87 | 0.16 |
| H6 (matched) | frozen log | T3-T4 | T4-T5 | +2.15 | +0.21 | +1.93 | -0.83 | 15.44 | +0.31, -0.07, -0.41 | -6.1, -5.0, +0.2 | 0.20 | 4.63 | -0.12 | -0.12 | 3.05 | 1.12 | 0.20 |
| H6 (matched) | frozen log | T1-T2 | T1-T6 | +1.75 | +0.17 | +1.58 | -0.67 | 14.19 | +0.32, +0.20, -0.30 | -5.5, -4.5, -0.2 | 0.22 | 5.15 | 0.09 | 0.09 | 1.80 | 0.77 | 0.14 |
| H6 (matched) | frozen log | T5-T6 | T2-T3 | -1.68 | -0.09 | -1.58 | +6.00 | 29.49 | +0.02, +0.01, -0.15 | -2.7, -1.7, -0.5 | 0.22 | 6.32 | -0.06 | -0.06 | 0.91 | 0.50 | 0.09 |
| H6 (matched) | frozen log | T2 refl. | T6 refl. | +1.51 | +0.21 | +1.30 | -0.36 | 16.50 | -0.30, -0.08, +0.08 | +6.4, -1.1, -2.0 | 0.24 | 2.46 | -0.08 | -0.08 | 2.05 | 8.96 | 0.09 |
| H6 (matched) | whitened log | T2-T3 | T5-T6 | +5.23 | +0.37 | +4.86 | -1.48 | 26.91 | +0.41, -0.04, +0.05 | -8.5, -7.6, -2.4 | 0.16 | 5.56 | 0.10 | 0.10 | 1.47 | 0.87 | 0.16 |
| H6 (matched) | whitened log | T3-T4 | T4-T5 | +1.87 | +0.19 | +1.68 | -0.72 | 13.84 | +0.31, -0.07, -0.41 | -6.1, -5.0, +0.2 | 0.20 | 4.63 | -0.12 | -0.12 | 3.05 | 1.12 | 0.20 |
| H6 (matched) | whitened log | T2 refl. | T6 refl. | +1.81 | +0.23 | +1.57 | -0.38 | 19.64 | -0.30, -0.08, +0.08 | +6.4, -1.1, -2.0 | 0.24 | 2.46 | -0.08 | -0.08 | 2.05 | 8.96 | 0.09 |
| H6 (matched) | whitened log | T3 refl. | T5 refl. | +1.79 | +0.12 | +1.67 | -0.47 | 19.29 | -0.22, -0.01, -0.06 | +7.0, -1.9, -0.8 | 0.24 | 1.91 | -0.07 | -0.07 | 2.11 | 8.64 | 0.08 |
| H6 (matched) | whitened log | T1-T2 | T1-T6 | +1.56 | +0.14 | +1.41 | -0.59 | 13.32 | +0.32, +0.20, -0.30 | -5.5, -4.5, -0.2 | 0.22 | 5.15 | 0.09 | 0.09 | 1.80 | 0.77 | 0.14 |

Key `b9_anti`: left/right differences (left path minus its mirror path) of phase and amplitude at the fit frequencies, against the largest one-pass and numerical-floor values of the same difference:

| reference | pair | anti_phase_deg_fit | anti_amp_dB_fit | one_pass_anti_phase_max_deg | floor_anti_phase_max_deg | floor_set_by | floor_p6_deg | ratio_to_max_ruler | ratio_with_p6_floor |
|---|---|---|---|---|---|---|---|---|---|
| H7 (frozen, primary) | T1-T2 vs T1-T6 | -3.6, -1.8, +0.2 | +0.18, +0.33, -0.24 | 1.39 | 4.44 | Moderate_lobe | 2.40 | 0.80 | 1.49 |
| H7 (frozen, primary) | T1-T3 vs T1-T5 | +3.8, +11.7, +0.8 | -0.46, +2.12, -0.53 | 9.15 | 24.91 | Mild_lobe | 3.88 | 0.47 | 1.28 |
| H7 (frozen, primary) | T2 refl. vs T6 refl. | +4.3, +0.2, -0.4 | -0.28, +0.12, +0.16 | 0.62 | 1.96 | Mild_lobe | 1.79 | 2.21 | 2.42 |
| H7 (frozen, primary) | T2-T3 vs T5-T6 | -5.6, -4.8, -1.0 | +0.39, -0.09, +0.18 | 2.07 | 6.32 | Moderate_lobe | 2.35 | 0.89 | 2.40 |
| H7 (frozen, primary) | T2-T4 vs T4-T6 | +5.1, -2.1, +6.9 | -0.86, +1.85, -0.28 | 4.96 | 10.97 | Mild_lobe | 5.53 | 0.63 | 1.25 |
| H7 (frozen, primary) | T3 refl. vs T5 refl. | +5.1, -0.9, -0.5 | -0.07, +0.03, -0.11 | 0.77 | 1.56 | Mild_lobe | 1.48 | 3.31 | 3.48 |
| H7 (frozen, primary) | T3-T4 vs T4-T5 | -4.0, -4.2, +0.7 | +0.25, -0.24, -0.33 | 2.42 | 3.76 | Moderate_lobe | 1.73 | 1.11 | 1.72 |
| H6 (matched) | T1-T2 vs T1-T6 | -3.6, -2.6, +0.0 | +0.17, +0.43, -0.30 | 1.39 | 4.44 | Moderate_lobe | 2.40 | 0.81 | 1.51 |
| H6 (matched) | T1-T3 vs T1-T5 | +3.6, +8.7, +2.1 | -0.53, +1.67, -0.68 | 9.15 | 24.91 | Mild_lobe | 3.88 | 0.35 | 0.95 |
| H6 (matched) | T2 refl. vs T6 refl. | +4.3, +0.2, -0.6 | -0.34, -0.02, +0.18 | 0.62 | 1.96 | Mild_lobe | 1.79 | 2.19 | 2.39 |
| H6 (matched) | T2-T3 vs T5-T6 | -5.8, -5.8, -1.9 | +0.39, -0.06, +0.21 | 2.07 | 6.32 | Moderate_lobe | 2.35 | 0.93 | 2.49 |
| H6 (matched) | T2-T4 vs T4-T6 | +4.1, -1.0, +2.7 | -0.99, +0.78, -0.42 | 4.96 | 10.97 | Mild_lobe | 5.53 | 0.37 | 0.74 |
| H6 (matched) | T3 refl. vs T5 refl. | +5.3, -1.2, -0.4 | -0.08, +0.00, -0.19 | 0.77 | 1.56 | Mild_lobe | 1.48 | 3.39 | 3.57 |
| H6 (matched) | T3-T4 vs T4-T5 | -3.7, -3.3, +0.8 | +0.28, -0.22, -0.08 | 2.42 | 3.76 | Moderate_lobe | 1.73 | 0.99 | 1.55 |

**Mechanism.** 85% of the primary LR (+7.19 of +8.48) comes from **phase** changes, only +1.29 from amplitude. The largest single term is the left neighbour path T2–T3: its phase moves −10.2/−8.4/−4.5° against −4.6/−3.6/−3.5° on its mirror T5–T6, while its amplitude moves ≤ 0.5 dB. The main session's index and its 22 gain-proof cross-ratios use band-averaged amplitudes, so they cannot see this phase asymmetry. Their per-path band-power numbers for the same top paths (|change| ≤ 0.12 dB, ≤ 3.0× yardstick, ≤ 7.3× floor) agree with the small amplitude part here. There is no contradiction in the data, only two different observables.
**Against the rulers.** The T2–T3 vs T5–T6 phase asymmetry (−5.6° at 3.4 GHz) is 2.7× its largest one-pass change (2.1°). But it is only 0.9× the largest numerical mirror residual of the symmetric designs (6.3°, set by Moderate_lobe); with the floor of the pass-matched p6 designs it is 2.4×. The reflection pairs T2/T6 and T3/T5 exceed both (≈ 2.2× and 3.3×) at 3.4 GHz only.
**Verdict: CONFIRMED (the source is identified), the contradiction resolved by mechanism.** +8.5 is a left-side phase asymmetry of the neighbour paths and reflections at 3.4–3.6 GHz. The main session is right that there is no amplitude asymmetry. Neither result establishes a lobe-level left/right signal beyond the conservative symmetry floor.

## Summary

| question | verdict | change | evidence |
|---|---|---|---|
| B1 one bar | CHANGED | LeftOnly LR 'hit' (≥ 2×) → sensitive (2.04×, Tikhonov dS); 2.95× whitened; measured ≤ 2.24× | lobe_review.json: b1, b1_floors |
| B2 bias + leakage | CONFIRMED | kernel asymmetry -0.32; symmetric designs -3.9…+1.0, no consistent sign; LR_anti 7.86 | lobe_review.json: b2a, b2b, b3 |
| B3 mirror test | CONFIRMED (sign); size not established | LR_mirror -7.24; sum +1.24; LR_anti 7.86 = 1.81× clean (conservative floor) | lobe_review.json: b3, b3_rulers |
| B4 matched reference | CHANGED | primary method: PARTIAL (H7) → FAIL (H6); sector calls move by one mesh pass | lobe_review.json: b4, b4_mech |
| B5 whitened log | CHANGED | 3.0× / 3.0× → 2.95× / 2.24× (max → quadrature); 10 looks, measured p_bonf 0.13 | lobe_review.json: b1, b5, b5_meta |
| B6 Born validity | CHANGED | rel. error 0.56–0.67 (all paths); LeftOnly LR pred +15.0 vs obs +8.5: comparable | lobe_review.json: b6, b6_size |
| B7 fit frequencies | CHANGED; CANNOT TELL (3.3/3.5/3.7) | side left for subsets with 3.4 or 3.6, none at 3.8 alone; S3 needs 3.4; interpolation invalid | lobe_review.json: b7, b7_val, b7_band |
| B8 lobe_A calibration | CHANGED | 14/28 calls flip (all sector calls; side and front/back unchanged; MCI unchanged) | lobe_review.json: b8, b8_meta |
| B9 source of +8.5 | CONFIRMED (mechanism) | 85% phase, T2–T3 largest; main's amplitude-only tests cannot see it; phase asymmetry 2.7× one-pass, 0.9× conservative floor | lobe_review.json: b9_sum, b9_top, b9_anti |

**What survives.** The left/right sign of LeftOnly is in the data (mirror test) and is stable over the true-field frequency subsets that include 3.4 or 3.6 GHz and over both references. Its size: LR_anti (the asymmetry-free estimate) is 1.8–2.6× the clean ruler with the conservative floor and 2.6–3.3× with the pass-matched floor; LR itself 2.0–3.0× / 3.9–5.5×. LeftOnly's own floor cannot be measured, so the conservative floor decides: sensitive at best, not established. It is not separable once measurement errors are included, except marginally for the post-hoc whitened log (2.2×, not significant after 10 looks). It is carried by phase, which the amplitude-based analysis of the main session does not use. The sector calls (S2, S3) and the pre-registered PARTIAL depend on the reference (B4) and on the calibration (B8) by one mesh pass or 9%–22% in κ. The Born model error is as large as the signal (B6).

