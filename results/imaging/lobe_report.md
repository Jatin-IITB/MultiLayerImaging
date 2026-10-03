# Lobe-sector phantom (set lobe_v1): sector-level localisation and imaging (code fb5b775, 2026-10-03)

Regenerate: `python imaging/run_lobe.py` (blind stage: `python imaging/run_lobe.py --blind`, only after `lobe_predictions.md` is committed). This section is new; the v1/v2 imaging results in `report.md` are unchanged.

## 0. Data, background, scope

- Designs (project `new_with_slices`, one solve each, 3.2–4.2 GHz, 201 points, glitch masking ON): `Healthy_sliced`, `Mild_lobe`, `Moderate_lobe`, `Severe_lobe`. Every difference is dS = S(stage) − S(Healthy_sliced) (same project, setup and mesh recipe). LeftOnly_test and MCI_lobe are the blind set (§6).
- **Background fields.** The Born kernels use the HFSS field exports of the *unsliced* v2 Normal design (`data/fields`, 3.4/3.6/3.8 GHz). At e = 0 the sliced head is the same head geometrically, except that its skull inner surface was set explicitly to 83.5 mm and its mesh differs; the kernels are therefore an approximation of the sliced background.
- **One simulation per design and one head.** Everything below is within-simulation capability under the stated noise, not generalisation to other heads or setups.
- **Calibration.** κ(f) is fitted on Mild only and frozen: |κ| = 3.29, 3.60, 6.38 at 3.4/3.6/3.8 GHz. With κ the linear model reproduces Mild 0.81, Moderate 0.86, Severe 0.93 (shape correlation with HFSS dS) but with relative errors 0.59, 0.56, 0.61; the absolute Born prediction is 0.23, 0.29, 0.35 of the HFSS dS size. The AD changes are far from Born-small.
- **Which quantity marks an affected lobe.** The brief assumed AD only lowers ε. That is true for conductivity-weighted loss but **not for εr at Mild and Moderate**: their CSF permittivity (55.25, 48.75) is higher than or equal to healthy gray matter (47.7), so the true sensitivity-weighted dεr of an affected sector is Mild +7.4, Moderate +3.1, Severe -13.0. What rises in every affected sector is the conductivity: dε'' = dσ/(ωε0) = Mild +13.0, Moderate +15.0, Severe +20.2 in affected sectors vs ≤ 0.4 in healthy ones. The sector calls therefore use dε''; the bounded fit constrains dε'' ≥ 0 only.

## 1. Sector sensitivity kernels (3.1)

Born sensitivity of each reciprocal antenna pair to a unit complex dε uniform in each region: the six outer-cortex sector shells (r 70–83.5 mm inside each 60° wedge, full height) and the core (r < 25 mm). |K| at 3.6 GHz, normalised to the largest entry:

| pair | S1 | S2 | S3 | S4 | S5 | S6 | core |
|---|---|---|---|---|---|---|---|
| T1 refl. (reflection) | 0.98 | 0.066 | 0.0053 | 0.0019 | 0.004 | 0.13 | 0.00081 |
| T1–T2 (neighbour) | 0.23 | 0.23 | 0.0065 | 0.001 | 0.00023 | 0.0083 | 0.0023 |
| T1–T3 (second-neighbour) | 0.057 | 0.03 | 0.059 | 0.012 | 0.0012 | 0.013 | 0.0012 |
| T1–T4 (opposite) | 0.061 | 0.019 | 0.02 | 0.067 | 0.018 | 0.023 | 0.0013 |
| T1–T5 (second-neighbour) | 0.064 | 0.012 | 0.0016 | 0.011 | 0.062 | 0.029 | 0.0012 |
| T1–T6 (neighbour) | 0.32 | 0.0049 | 0.00089 | 0.0009 | 0.0091 | 0.3 | 0.0012 |
| T2 refl. (reflection) | 0.063 | 1 | 0.13 | 0.0058 | 0.0015 | 0.0076 | 0.0017 |
| T2–T3 (neighbour) | 0.0034 | 0.36 | 0.34 | 0.0065 | 0.0018 | 0.0018 | 0.0016 |
| T2–T4 (second-neighbour) | 0.01 | 0.06 | 0.036 | 0.064 | 0.011 | 0.0018 | 0.00084 |
| T2–T5 (opposite) | 0.026 | 0.069 | 0.022 | 0.025 | 0.073 | 0.025 | 0.00089 |
| T2–T6 (second-neighbour) | 0.031 | 0.066 | 0.0099 | 0.0014 | 0.0098 | 0.064 | 0.0014 |
| T3 refl. (reflection) | 0.0044 | 0.14 | 0.84 | 0.13 | 0.006 | 0.0017 | 0.0019 |
| T3–T4 (neighbour) | 0.00081 | 0.0093 | 0.25 | 0.27 | 0.008 | 0.0011 | 0.0011 |
| T3–T5 (second-neighbour) | 0.0011 | 0.01 | 0.056 | 0.033 | 0.063 | 0.011 | 0.001 |
| T3–T6 (opposite) | 0.023 | 0.024 | 0.068 | 0.021 | 0.022 | 0.067 | 0.00063 |
| T4 refl. (reflection) | 0.0032 | 0.0044 | 0.13 | 0.9 | 0.18 | 0.005 | 0.003 |
| T4–T5 (neighbour) | 0.00061 | 0.0012 | 0.0064 | 0.31 | 0.36 | 0.0082 | 0.0013 |
| T4–T6 (second-neighbour) | 0.0098 | 0.0021 | 0.01 | 0.064 | 0.04 | 0.057 | 0.0011 |
| T5 refl. (reflection) | 0.0069 | 0.0012 | 0.0062 | 0.12 | 0.88 | 0.13 | 0.0022 |
| T5–T6 (neighbour) | 0.0071 | 0.0012 | 0.0014 | 0.0067 | 0.24 | 0.34 | 0.0033 |
| T6 refl. (reflection) | 0.12 | 0.005 | 0.00098 | 0.0048 | 0.13 | 0.83 | 0.001 |

Singular values of the noise-whitened kernel matrix (21 pairs × 3 frequencies × Re/Im; unknowns dεr and dε'' per region), relative to the largest:

- 6 sectors + core: 1.000, 0.987, 0.748, 0.730, 0.722, 0.704, 0.533, 0.526, 0.509, 0.504, 0.399, 0.390, 0.014, 0.013 → condition number 75. The two smallest belong to the core.
- 6 sectors only: condition number 2.6 (gain-invariant log data 3.3); 12 regions with the gap/deep split: 14.

Similarity of the region kernels (cosine between whitened dεr columns; 1 = indistinguishable):

| region | S1 | S2 | S3 | S4 | S5 | S6 | core |
|---|---|---|---|---|---|---|---|
| S1 frontal | 1.00 | 0.38 | 0.12 | 0.11 | 0.13 | 0.38 | 0.16 |
| S2 temporal L | 0.38 | 1.00 | 0.44 | 0.13 | 0.12 | 0.14 | 0.20 |
| S3 parietal L | 0.12 | 0.44 | 1.00 | 0.38 | 0.12 | 0.12 | 0.14 |
| S4 occipital | 0.11 | 0.13 | 0.38 | 1.00 | 0.44 | 0.13 | 0.10 |
| S5 parietal R | 0.13 | 0.12 | 0.12 | 0.44 | 1.00 | 0.38 | 0.13 |
| S6 temporal R | 0.38 | 0.14 | 0.12 | 0.13 | 0.38 | 1.00 | 0.15 |
| core | 0.16 | 0.20 | 0.14 | 0.10 | 0.13 | 0.15 | 1.00 |

- **All six sectors are distinguishable** with 6 antennas on one ring: no two sector kernels are collinear (largest cosine 0.44, between neighbouring sectors). The mirror pairs S2/S6 (0.14) and S3/S5 (0.12) are nearly orthogonal in pair space: each is seen by a different set of antenna pairs (its own ring position), which is what allows a left/right call.
- **The core is not**: its kernel is tiny (singular values 0.014, 0.013 of the largest) — the hippocampus is invisible, as in v2.

Figure: `figures/lobe_kernels.png`.

## 2. Identifiability before any fit (CRLB, 3.2)

Typical noise on both measurements (0.25 dB, 2°, −70 dB floor), κ frozen. Three variants: no gain error; ±0.5 dB per-port amplitude gain (6 nuisance parameters, constant over frequency, 0.5 dB prior); and gain-invariant data (complex log-ratios projected onto the complement of all per-port, per-frequency complex gains = cross-ratios). Columns 'true': sensitivity-weighted mean true change of the region.

| quantity | region | dS (no gain error) | dS + 0.5 dB port gains | log, gain-invariant | true Mild | true Moderate | true Severe |
|---|---|---|---|---|---|---|---|
| dεr | S1 frontal | 3.4 | 3.6 | 4.1 | -0.8 | +2.7 | -13.0 |
| dεr | S2 temporal L | 3.3 | 3.5 | 4 | +5.8 | +3.1 | -13.0 |
| dεr | S3 parietal L | 3.4 | 3.6 | 4.1 | +8.9 | +3.2 | -13.0 |
| dεr | S4 occipital | 3.4 | 3.5 | 4.1 | -0.8 | -1.3 | -12.7 |
| dεr | S5 parietal R | 3.3 | 3.5 | 4.1 | +8.9 | +3.3 | -13.0 |
| dεr | S6 temporal R | 3.3 | 3.5 | 4 | +5.8 | +3.1 | -13.0 |
| dεr | core | 1.4e+02 | 1.4e+02 | 1.6e+02 | +2.7 | -0.1 | -15.1 |
| dε'' | S1 frontal | 3.3 | 3.4 | 4 | +0.3 | +15.0 | +20.3 |
| dε'' | S2 temporal L | 3.3 | 3.3 | 4 | +13.2 | +15.0 | +20.3 |
| dε'' | S3 parietal L | 3.3 | 3.3 | 4 | +12.9 | +14.9 | +20.3 |
| dε'' | S4 occipital | 3.3 | 3.3 | 4 | +0.3 | +0.4 | +20.1 |
| dε'' | S5 parietal R | 3.3 | 3.3 | 4 | +12.9 | +14.9 | +20.3 |
| dε'' | S6 temporal R | 3.2 | 3.3 | 3.9 | +13.2 | +15.0 | +20.3 |
| dε'' | core | 1.4e+02 | 1.4e+02 | 1.5e+02 | +13.6 | +14.9 | +19.9 |

Affected sectors determined (CRLB of dε'' < half the true change), 6-sector model:

| stage | affected | determined_dS | determined_gain_inv | core_crlb_over_change |
|---|---|---|---|---|
| Mild_lobe | S2 S3 S5 S6 | S2 S3 S5 S6 | S2 S3 S5 S6 | 10.1 |
| Moderate_lobe | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | 9.2 |
| Severe_lobe | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | 6.9 |

- Sector conductivity is determined in every affected sector, with or without per-port gain errors (the ±0.5 dB gain prior raises the CRLB by 7% at most; the fully gain-invariant data by 22%).
- The core is not determined: its CRLB is many times its change.

**Depth.** Each sector split into an under-skull gap (76–83.5 mm) and a deeper part (60–76 mm), dε'':

| region | crlb_dS | crlb_gain_inv | true Mild | true Moderate | true Severe |
|---|---|---|---|---|---|
| S1 frontal gap | 4.9 | 5.6 | +0.4 | +13.5 | +18.8 |
| S1 frontal deep | 12.6 | 14.5 | +0.0 | +17.4 | +22.9 |
| S2 temporal L gap | 4.9 | 5.6 | +11.4 | +13.5 | +18.8 |
| S2 temporal L deep | 13.4 | 16.0 | +13.1 | +17.7 | +23.3 |
| S3 parietal L gap | 5.7 | 6.6 | +11.4 | +13.5 | +18.8 |
| S3 parietal L deep | 15.7 | 18.4 | +15.2 | +18.7 | +23.4 |
| S4 occipital gap | 5.4 | 6.3 | +0.4 | +0.6 | +18.8 |
| S4 occipital deep | 14.9 | 18.2 | +0.0 | +0.0 | +20.4 |
| S5 parietal R gap | 5.4 | 6.4 | +11.4 | +13.5 | +18.8 |
| S5 parietal R deep | 14.3 | 17.1 | +15.2 | +18.7 | +23.4 |
| S6 temporal R gap | 5.6 | 6.5 | +11.4 | +13.5 | +18.8 |
| S6 temporal R deep | 15.0 | 17.4 | +13.1 | +17.8 | +23.3 |

Determined (CRLB < half the true change) in the 12-region model:

| stage | gap determined (dS) | deep determined (dS) | gap determined (gain-inv) | deep determined (gain-inv) |
|---|---|---|---|---|
| Mild_lobe | S2 S5 S6 | none | S2 | none |
| Moderate_lobe | S1 S2 S3 S5 S6 | none | S1 S2 S3 S5 S6 | none |
| Severe_lobe | S1 S2 S3 S4 S5 S6 | none | S1 S2 S3 S4 S5 S6 | none |

- Gap and deep kernels of one sector are not collinear (cosine -0.18…-0.01), but the deep CRLB (13–16) is 2–3× the gap CRLB (4.9–5.7). By the brief's criterion the deeper cortex (60–76 mm) is not determined in any sector at any stage; the under-skull gap is determined only where listed. The ring sees the outermost ~8 mm of cortex; depth beyond that is not resolved.

## 3. Sector inversion (3.3)

Unknowns: dεr and dε'' of the six sector shells (core excluded: §1–2). λ chosen by GCV on Mild only and frozen: dS fits 0.158, gain-invariant fits 0.126. Methods: (a) Tikhonov on dS; (b) bounded (dε'' ≥ 0) on dS; (c) Tikhonov and bounded on gain-invariant log-ratio data (no per-port calibration needed). Recovered conductivity change per sector:

| method | stage | dε'' S1 Fr | dε'' S2 TL | dε'' S3 PL | dε'' S4 Oc | dε'' S5 PR | dε'' S6 TR |
|---|---|---|---|---|---|---|---|
| tikhonov dS | Mild_lobe | 11.4 | 20.2 | 17.6 | 7.6 | 16.2 | 21.7 |
| tikhonov dS | Moderate_lobe | 17.7 | 15.1 | 16.6 | 7.5 | 18.6 | 20.9 |
| tikhonov dS | Severe_lobe | 20.6 | 17.4 | 19.8 | 16.7 | 17.7 | 21.1 |
| bounded dS | Mild_lobe | 11.4 | 20.2 | 17.6 | 7.6 | 16.2 | 21.7 |
| bounded dS | Moderate_lobe | 17.7 | 15.1 | 16.6 | 7.5 | 18.6 | 20.9 |
| bounded dS | Severe_lobe | 20.6 | 17.4 | 19.8 | 16.7 | 17.7 | 21.1 |
| tikhonov log (gain-inv.) | Mild_lobe | 10.4 | 17.1 | 16.2 | 5.9 | 16.9 | 17.6 |
| tikhonov log (gain-inv.) | Moderate_lobe | 17.1 | 15.9 | 15.7 | 6.3 | 17.4 | 22.1 |
| tikhonov log (gain-inv.) | Severe_lobe | 22.6 | 18.1 | 21.9 | 18.1 | 19.7 | 22.3 |
| bounded log (gain-inv.) | Mild_lobe | 10.4 | 17.1 | 16.2 | 5.9 | 16.9 | 17.6 |
| bounded log (gain-inv.) | Moderate_lobe | 17.1 | 15.9 | 15.7 | 6.3 | 17.4 | 22.1 |
| bounded log (gain-inv.) | Severe_lobe | 22.6 | 18.1 | 21.9 | 18.1 | 19.7 | 22.3 |
| TRUTH (sens.-weighted) | Mild_lobe | 0.3 | 13.2 | 12.9 | 0.3 | 12.9 | 13.2 |
| TRUTH (sens.-weighted) | Moderate_lobe | 15.0 | 15.0 | 14.9 | 0.4 | 14.9 | 15.0 |
| TRUTH (sens.-weighted) | Severe_lobe | 20.3 | 20.3 | 20.3 | 20.1 | 20.3 | 20.3 |

Scores. corr_e = Pearson correlation of recovered dε'' with the true CSF expansion e_k; corr_truth = with the true dε''; top-k = fraction of the k truly affected sectors among the k largest recovered values (undefined for Severe, where all are affected). Calls use the frozen rule R1 (§5); 'null only' uses the noise-null threshold alone.

| method | stage | corr_e | corr_truth | topk | called | called_null_only | true_set | correct_calls | LR | side | FB | frontback |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | Mild_lobe | 0.74 | 0.91 | 1.00 | S2 S3 S5 S6 | S1 S2 S3 S4 S5 S6 | S2 S3 S5 S6 | 6 | -0.0 | none | +3.8 | none |
| tikhonov dS | Moderate_lobe | 0.86 | 0.91 | 1.00 | S1 S2 S3 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S5 S6 | 6 | -3.9 | none | +10.1 | front |
| tikhonov dS | Severe_lobe | 0.40 | 0.56 | n/a | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | 6 | -0.8 | none | +3.9 | none |
| bounded dS | Mild_lobe | 0.74 | 0.91 | 1.00 | S2 S3 S5 S6 | S1 S2 S3 S4 S5 S6 | S2 S3 S5 S6 | 6 | -0.0 | none | +3.8 | none |
| bounded dS | Moderate_lobe | 0.86 | 0.91 | 1.00 | S1 S2 S3 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S5 S6 | 6 | -3.9 | none | +10.1 | front |
| bounded dS | Severe_lobe | 0.40 | 0.56 | n/a | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | 6 | -0.8 | none | +3.9 | front |
| tikhonov log (gain-inv.) | Mild_lobe | 0.87 | 0.95 | 1.00 | S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S2 S3 S5 S6 | 6 | -0.7 | none | +4.5 | none |
| tikhonov log (gain-inv.) | Moderate_lobe | 0.82 | 0.90 | 1.00 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | S1 S2 S3 S5 S6 | 6 | -3.9 | none | +10.8 | front |
| tikhonov log (gain-inv.) | Severe_lobe | 0.39 | 0.55 | n/a | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | 6 | -1.0 | none | +4.5 | none |
| bounded log (gain-inv.) | Mild_lobe | 0.87 | 0.95 | 1.00 | S2 S3 S5 S6 | S1 S2 S3 S4 S5 S6 | S2 S3 S5 S6 | 6 | -0.7 | none | +4.5 | none |
| bounded log (gain-inv.) | Moderate_lobe | 0.82 | 0.90 | 1.00 | S1 S2 S3 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S5 S6 | 6 | -3.9 | none | +10.8 | front |
| bounded log (gain-inv.) | Severe_lobe | 0.39 | 0.55 | n/a | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | S1 S2 S3 S4 S5 S6 | 6 | -1.0 | none | +4.5 | none |

**Front/back (Moderate: frontal S1 affected, occipital S4 healthy):**

| method | S1 | S4 | crlb_S1 | crlb_S4 | FB | T_FB | verdict | S1_called | S4_called |
|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | 17.7 | 7.5 | 3.3 | 3.3 | +10.1 | 6.4 | front | True | False |
| bounded dS | 17.7 | 7.5 | 3.3 | 3.3 | +10.1 | 3.8 | front | True | False |
| tikhonov log (gain-inv.) | 17.1 | 6.3 | 4.0 | 4.0 | +10.8 | 7.8 | front | True | False |
| bounded log (gain-inv.) | 17.1 | 6.3 | 4.0 | 4.0 | +10.8 | 4.5 | front | True | False |

Reading:
- The bounded fits equal the Tikhonov fits on the real designs: the bound dε'' ≥ 0 is never active (all recovered dε'' are positive). The bound matters only for the null inputs (different T_null, T_FB).
- Severe: every sector is affected with nearly equal true dε'' (20.1–20.3), so corr_truth there (≈ 0.55) measures noise in a flat map, not localisation.
- The **pattern** is recovered: corr_truth 0.90–0.95 for Mild/Moderate and top-k = 1.00 in every method: the affected lobes are always the most changed ones.
- The **absolute level** is not: healthy sectors come out at dε'' ≈ 6–11 instead of ≈ 0.3 (Born model error and leakage from the neighbouring affected sectors, kernel cosine ≈ 0.4). A threshold from noise-only inputs therefore calls every sector affected ('called_null_only'); the frozen rule R1 adds a threshold tuned on Mild, and with it every call on Mild, Moderate and Severe is correct.
- **Front/back:** Moderate's frontal lobe is recovered at 17.7 and the occipital at 7.5 (CRLB 3.3); the contrast +10.1 exceeds its frozen threshold in every method → **front**. On Mild (S1, S4 both healthy) and Severe (both affected, frontal expansion 15.5 mm vs occipital 11.5 mm, nearly equal conductivity) the call should be none: bounded dS Severe front (FB +3.9 vs T_FB 3.8). These are marginal false/ambiguous calls; the threshold was not changed after seeing them.
- dεr is recovered with the wrong sign at Mild/Moderate (corr with the true dεr -0.86, -0.85, +0.09 for Mild/Moderate/Severe, primary method): the permittivity part is not usable here.

Figure: `figures/lobe_maps.png` (truth beside the recovered maps).

## 4. Radar imaging of the asymmetric change (3.4)

DAS and DMAS of dS (whitened 21 reciprocal pairs, layered straight-ray delays, t_ant = 0.5 ns as tuned on v2 Mild) on the ring plane. Peak = maximum outside r = 40 mm; mean direction / resultant = circular mean of the image energy in the annulus 40–80 mm (resultant 0 = isotropic, 1 = all energy at one azimuth). True centroid = e-weighted mean direction of the affected sectors (S1 front = −90°, S4 back = +90°).

| stage | method | global_peak_r_mm | peak_az_deg | peak_r_mm | mean_dir_deg | resultant | true_dir_deg | true_resultant |
|---|---|---|---|---|---|---|---|---|
| Mild_lobe | DAS | 9 | 90 | 42 | 102 | 0.022 | 90 | 0.11 |
| Mild_lobe | DMAS | 69 | 120 | 69 | 108 | 0.038 | 90 | 0.11 |
| Moderate_lobe | DAS | 9 | -55 | 49 | -66 | 0.028 | -90 | 0.13 |
| Moderate_lobe | DMAS | 9 | 72 | 63 | -52 | 0.037 | -90 | 0.13 |
| Severe_lobe | DAS | 9 | 90 | 42 | -6 | 0.002 | -90 | 0.04 |
| Severe_lobe | DMAS | 9 | -55 | 49 | 41 | 0.005 | -90 | 0.04 |

- The global maximum stays at the centre (r ≈ 9 mm) in 5 of 6 images: the symmetric-ring artefact of v2 persists, because most of each stage's change is still shared by all sectors (every sector's thin CSF layer and the core change with the stage).
- The image energy is nearly isotropic (resultant ≤ 0.038); its direction does not follow the true centroid consistently (table). The images are speckle-dominated, as the v2 ring-plane images were (`figures/i1_ring_plane.png`). **Radar imaging does not localise the lobes**; the regional inversion does.

Figure: `figures/lobe_radar.png`.

## 5. Noise floors, null distributions and the frozen calling rules (3.5)

Null inputs (dS that contain no lobe change), each passed through the frozen inversion: circulant (12); mirror Mild_lobe (12); mirror Moderate_lobe (12); mirror Severe_lobe (12); measurement (40). 'circulant' = the Healthy_sliced deviation from its own rotational symmetry, mapped through the 6 rotations × 2 reflections of the ring; 'mirror <stage>' = the part of each mirror-symmetric stage that is antisymmetric under x → −x (numerical noise), under the same 12 maps; 'measurement' = typical-noise draws of Healthy_sliced minus Healthy_sliced.

Frozen rules (per method):

- **R1 sector affected** if dε''_k > T_abs = max(T_null, T_mild). T_null = 95th percentile of the largest sector value over all null inputs (family-wise 5 %). T_mild = midway between the largest healthy and the smallest affected sector of Mild (tuned on Mild only).
- **R2 side** = left if LR = mean(S2, S3) − mean(S5, S6) > T_LR, right if LR < −T_LR. T_LR = max(95th percentile of |LR| over the null inputs, largest |LR| of the three mirror-symmetric designs).
- **R3 front/back** = front if FB = S1 − S4 > T_FB, back if < −T_FB. T_FB = max(95th percentile of |FB| over the nulls, |FB| of Mild, whose S1 and S4 are both healthy).

| method | T_null | T_mild | T_abs | T_LR_null | LR_sym_max | T_LR | T_FB_null | T_FB |
|---|---|---|---|---|---|---|---|---|
| tikhonov dS | 4.93 | 13.81 | 13.81 | 4.06 | 3.92 | 4.06 | 6.45 | 6.45 |
| bounded dS | 4.16 | 13.81 | 13.81 | 2.42 | 3.92 | 3.92 | 2.52 | 3.78 |
| tikhonov log (gain-inv.) | 6.44 | 13.32 | 13.32 | 3.61 | 3.93 | 3.93 | 7.83 | 7.83 |
| bounded log (gain-inv.) | 5.04 | 13.32 | 13.32 | 2.28 | 3.93 | 3.93 | 3.00 | 4.53 |

Figure: `figures/lobe_null_lr.png` (null distribution of the left−right contrast, the mirror-symmetric designs, the threshold and the pre-registered LeftOnly prediction).

## 6. Blind test (pre-registered, §4 of the brief)

Pipeline frozen in `results/imaging/lobe_frozen.json` and predictions written to `results/imaging/lobe_predictions.md` before LeftOnly_test or MCI_lobe were opened. Outcome: **pending** (the two designs are still solving). Run `python imaging/run_lobe.py --blind` when they arrive; this section will then be replaced by the scored outcome.

## 7. Verdict — can this 6-antenna ring localise lobe-level AD?

Within these simulations (one head, one solve per design, typical noise, Born kernels on the v2 Normal fields):

- **Which lobes (pattern):** yes, as a ranking. The recovered sector conductivity correlates 0.90–0.95 with the truth and the affected lobes are always the most changed. Absolute 'affected' calls need a threshold calibrated on a known stage (Mild), because healthy lobes are biased upward by model error and leakage.
- **Front/back:** yes for Moderate (frontal 17.7 vs occipital 7.5, contrast +10.1 > 6.4).
- **Left/right:** not testable on the available designs (all mirror-symmetric; they give |LR| ≤ 3.9). The frozen pipeline predicts LR = +14.7 ± 2.2 for LeftOnly_test (left in 100% of noisy draws); the blind test decides.
- **Depth:** only coarsely. Under-skull gap and deeper cortex are separable in principle, but the deeper region's CRLB is 2–3× larger; the core (hippocampus) is not determined at all.
- **Radar imaging:** no — it still peaks at the centre and its energy direction does not track the lobes.
- **Caveats:** the Born model explains only about a quarter to a third of the dS size (κ ≈ 3 absorbs it) and the background fields come from the unsliced design; the lobe placement is schematic (azimuthal wedges at the ring height); everything is within one simulated head.

