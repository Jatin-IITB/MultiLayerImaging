# Lobe-sector phantom (set lobe_v1): sector-level localisation and imaging (code fb5b775, 2026-10-03)

Regenerate: `python imaging/run_lobe.py` (blind stage: `python imaging/run_lobe.py --blind`, only after `lobe_predictions.md` is committed). This section is new; the v1/v2 imaging results in `report.md` are unchanged.

## 0. Data, background, scope

- Designs (project `new_with_slices`, one solve each, 3.2–4.2 GHz, 201 points, glitch masking ON): `Healthy_sliced`, `Mild_lobe`, `Moderate_lobe`, `Severe_lobe`. Every difference is dS = S(stage) − S(Healthy_sliced) (same project and setup; meshes NOT matched, see §5b). LeftOnly_test and MCI_lobe are the blind set (§6).
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

## 5b. Mesh yardstick (added after the freeze; frozen pipeline unchanged)

*Superseded by §5c (4 Oct): this compared two different projects as well as meshes; the mesh-matched set and the one-extra-pass yardstick are in §5c.*

The designs were **not** solved on matched meshes (results/STATUS.md §7 (HFSS solution dialogs): Healthy_sliced 1,349,491 elements, Mild 739,774, Moderate 796,281, Severe 690,077): the healthy reference has ~1.8× the elements of every stage, so each dS = S(stage) − S(Healthy_sliced) also contains a mesh difference. To size it, the difference between two healthy heads solved with different meshes (v2 Normal `new_Healthy.s6p` − Healthy_sliced) and its 12 ring-symmetry images were passed through the frozen inversions and rules as if they were a stage.

Size of the mesh difference at the fit frequencies: 0.511 (Frobenius norm over 21 pairs × 3 frequencies) vs Mild 0.174, Moderate 0.185, Severe 0.243 for the stage differences (293% of Mild).

Recovered values for the unrotated mesh difference:

| method | dε'' S1 Fr | dε'' S2 TL | dε'' S3 PL | dε'' S4 Oc | dε'' S5 PR | dε'' S6 TR | called | LR | side | FB | frontback |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | 25.5 | 28.9 | 24.5 | 24.6 | 20.4 | 35.4 | S1 S2 S3 S4 S5 S6 | -1.2 | none | +0.9 | none |
| bounded dS | 25.5 | 28.9 | 24.5 | 24.6 | 20.4 | 35.4 | S1 S2 S3 S4 S5 S6 | -1.2 | none | +0.9 | none |
| tikhonov log (gain-inv.) | 17.5 | 16.7 | 14.8 | 15.5 | 15.8 | 24.2 | S1 S2 S3 S4 S5 S6 | -4.2 | right | +2.0 | none |
| bounded log (gain-inv.) | 17.5 | 16.7 | 14.8 | 15.5 | 15.8 | 24.2 | S1 S2 S3 S4 S5 S6 | -4.2 | right | +2.0 | none |

Over all 12 symmetry images (largest values, and how many of the 12 trigger a call):

| method | max_sector | T_abs | n_sector_calls | max_abs_LR | T_LR | n_side_calls | max_abs_FB | T_FB | n_fb_calls |
|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | 36.3 | 13.8 | 72 | 6.7 | 4.1 | 4 | 9.4 | 6.4 | 6 |
| bounded dS | 36.3 | 13.8 | 72 | 6.7 | 3.9 | 4 | 9.4 | 3.8 | 6 |
| tikhonov log (gain-inv.) | 24.9 | 13.3 | 64 | 6.7 | 3.9 | 6 | 8.2 | 7.8 | 2 |
| bounded log (gain-inv.) | 24.9 | 13.3 | 64 | 6.7 | 3.9 | 6 | 8.2 | 4.5 | 4 |

- **Absolute level.** The mesh difference alone lifts every sector to dε'' ≈ 15–35, above the frozen T_abs, and its norm is 2.9× Mild's dS. The upward offset of the healthy sectors in §3 (6–11 instead of 0.3) is therefore consistent with a mesh contribution as well as Born error, and absolute 'affected' calls are not mesh-robust.
- **Contrasts.** Unrotated, the mesh difference gives LR -1.2 / FB +0.9 (primary) and LR -4.2 / FB +2.0 (gain-invariant). Under the 12 ring symmetries |LR| reaches 6.7 and |FB| 9.4; a mesh difference alone triggers a side call in 4 and a front/back call in 6 of 12 images (primary).
- Moderate's front/back contrast (primary +10.1) is 1.1× the largest |FB| a mesh difference between two fine healthy meshes produces (9.4); the left/right threshold T_LR = 4.1 compares with a largest mesh |LR| of 6.7. The pre-registered LeftOnly contrast (+14.7) would be 2.2× the largest mesh |LR|; a left call near the threshold would not be distinguishable from mesh.
- Caveat: this yardstick compares two fine meshes; the disease stages are on coarser meshes (~0.7–0.8 M elements), whose error is probably larger. It also includes any other difference between the two projects (e.g. the internal wedge faces of the sliced head). Mesh-matched re-solves are needed before the front/back and left/right results can be called mesh-independent.

## 5c. Mesh-matched set lobe_A (4 Oct): frozen pipeline, one-extra-pass yardstick, opposite paths

**Data.** lobe_A = `Healthy_sliced_new` (6 adaptive passes, same stop rule as the stages; the stages converged in 5 passes, results/STATUS.md §7) as the reference, with `Mild_lobe`, `Moderate_lobe`, `Severe_lobe` (the `_new` Moderate and Severe files are identical to the old ones: max |ΔS| 9e-09, 4e-09). Frozen κ, λ and thresholds from `lobe_frozen.json` (code `fb5b775`) are applied unchanged; only the reference (its noise weights and the log-ratio reference) is now Healthy_sliced_new. The pre-registered predictions are unchanged.

**Mesh yardstick = one extra adaptive pass.** Two pass-to-pass differences, each passed through the pipeline as if it were a stage: Healthy 7 − 6 passes (`Healthy_sliced` − `Healthy_sliced_new`) and Mild 6 − 5 passes (`Mild_lobe_new` − `Mild_lobe`). The sign of a mesh error is not known, so each difference is passed with both signs (+ and −); for the linear Tikhonov fits the two give the same |dε''|, for the bounded fits only one sign survives the bound dε'' ≥ 0.

Amplitude change per path class (dB, largest path of the class, 3.2–4.2 GHz, 201 points, glitch-masked): band = band-mean power ratio; median = median over frequency; worst = worst single frequency (set by spectral notches, where |S| is small):

| difference | statistic | reflection | neighbour | second-neighbour | opposite |
|---|---|---|---|---|---|
| Healthy 7 - 6 passes | band | 0.019 | 0.081 | 0.174 | 0.126 |
| Healthy 7 - 6 passes | median | 0.044 | 0.095 | 0.156 | 0.046 |
| Healthy 7 - 6 passes | worst | 0.961 | 0.422 | 2.484 | 4.548 |
| Mild 6 - 5 passes | band | 0.039 | 0.048 | 0.258 | 0.146 |
| Mild 6 - 5 passes | median | 0.085 | 0.112 | 0.186 | 0.102 |
| Mild 6 - 5 passes | worst | 0.978 | 0.445 | 5.676 | 9.458 |

Which class moves most depends on the statistic: band: second-neighbour; median: second-neighbour; worst: opposite. The opposite paths dominate only at single frequencies (notches). The 0.16–0.30 dB (opposite) / ≤ 0.05 dB (others) quoted for this check is the ring-mean change computed without glitch masking; `docs/01_claims_register.md` §L traces its 0.30 dB end (Mild 5→6) to one non-reciprocal sample on T2–T5 at 3.855 GHz in `Mild_lobe_new` (−34 dB against ≈ −70 dB at the neighbouring samples). Here that sample is glitch-masked (−30 dB rule; it becomes −58 dB) and 3.855 GHz is not one of the fit frequencies, so it does not enter any inversion below. The inversion uses complex S at 3.4, 3.6, 3.8 GHz, so the table above is what it sees. This yardstick replaces §5b (v2 Normal − Healthy_sliced), which compared different projects as well as meshes.

### lobe_A, all 21 paths

Recovered dε'' per sector (* = exceeds the one-extra-pass yardstick of that sector and method, i.e. the larger of the two pass differences' |dε''| in that sector), calls by the frozen rules:

| method | stage | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | called | correct | corr_truth | LR | side | FB | frontback |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | Mild_lobe | 9.2* | 18.2* | 14.9* | 5.4* | 13.8* | 18.6* | S2 S3 S6 | 5 | 0.91 | +0.3 | none | +3.9 | none |
| tikhonov dS | Moderate_lobe | 15.5* | 13.1* | 13.9* | 5.3* | 16.2* | 17.9* | S1 S3 S5 S6 | 5 | 0.92 | -3.5 | none | +10.2 | front |
| tikhonov dS | Severe_lobe | 18.4* | 15.5* | 17.1* | 14.6* | 15.3* | 18.1* | S1 S2 S3 S4 S5 S6 | 6 | 0.55 | -0.4 | none | +3.8 | none |
| bounded dS | Mild_lobe | 9.2* | 18.2* | 14.9* | 5.4* | 13.8* | 18.6* | S2 S3 S6 | 5 | 0.91 | +0.3 | none | +3.9 | front |
| bounded dS | Moderate_lobe | 15.5* | 13.1* | 13.9* | 5.3* | 16.2* | 17.9* | S1 S3 S5 S6 | 5 | 0.92 | -3.5 | none | +10.2 | front |
| bounded dS | Severe_lobe | 18.4* | 15.5* | 17.1* | 14.6* | 15.3* | 18.1* | S1 S2 S3 S4 S5 S6 | 6 | 0.55 | -0.4 | none | +3.8 | front |
| tikhonov log (gain-inv.) | Mild_lobe | 8.6* | 16.1* | 14.3* | 4.7* | 15.1* | 15.8* | S2 S3 S5 S6 | 6 | 0.96 | -0.3 | none | +3.9 | none |
| tikhonov log (gain-inv.) | Moderate_lobe | 15.4* | 14.7* | 13.8* | 5.0* | 15.7* | 19.9* | S1 S2 S3 S5 S6 | 6 | 0.91 | -3.6 | none | +10.4 | front |
| tikhonov log (gain-inv.) | Severe_lobe | 20.6* | 16.7* | 19.7* | 16.4* | 17.8* | 19.6* | S1 S2 S3 S4 S5 S6 | 6 | 0.56 | -0.5 | none | +4.1 | none |
| bounded log (gain-inv.) | Mild_lobe | 8.6* | 16.1* | 14.3* | 4.7* | 15.1* | 15.8* | S2 S3 S5 S6 | 6 | 0.96 | -0.3 | none | +3.9 | none |
| bounded log (gain-inv.) | Moderate_lobe | 15.4* | 14.7* | 13.8* | 5.0* | 15.7* | 19.9* | S1 S2 S3 S5 S6 | 6 | 0.91 | -3.6 | none | +10.4 | front |
| bounded log (gain-inv.) | Severe_lobe | 20.6* | 16.7* | 19.7* | 16.4* | 17.8* | 19.6* | S1 S2 S3 S4 S5 S6 | 6 | 0.56 | -0.5 | none | +4.1 | none |

The yardstick itself (each pass difference, both signs, through the same pipeline):

| method | difference | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | called | LR | FB |
|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | +(Healthy 7 - 6 passes) | -2.2 | -2.0 | -2.7 | -2.2 | -2.4 | -3.0 | none | +0.3 | +0.0 |
| tikhonov dS | -(Healthy 7 - 6 passes) | 2.2 | 2.0 | 2.7 | 2.2 | 2.4 | 3.0 | none | -0.3 | -0.0 |
| tikhonov dS | +(Mild 6 - 5 passes) | -3.1 | -4.2 | -2.4 | -2.4 | -2.5 | -5.2 | none | +0.5 | -0.7 |
| tikhonov dS | -(Mild 6 - 5 passes) | 3.1 | 4.2 | 2.4 | 2.4 | 2.5 | 5.2 | none | -0.5 | +0.7 |
| bounded dS | +(Healthy 7 - 6 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded dS | -(Healthy 7 - 6 passes) | 2.2 | 2.0 | 2.7 | 2.2 | 2.4 | 3.0 | none | -0.3 | -0.0 |
| bounded dS | +(Mild 6 - 5 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded dS | -(Mild 6 - 5 passes) | 3.1 | 4.2 | 2.4 | 2.4 | 2.5 | 5.2 | none | -0.5 | +0.7 |
| tikhonov log (gain-inv.) | +(Healthy 7 - 6 passes) | -1.7 | -1.2 | -2.0 | -1.5 | -1.7 | -2.1 | none | +0.3 | -0.2 |
| tikhonov log (gain-inv.) | -(Healthy 7 - 6 passes) | 1.7 | 1.2 | 1.9 | 1.4 | 1.6 | 2.0 | none | -0.3 | +0.2 |
| tikhonov log (gain-inv.) | +(Mild 6 - 5 passes) | -2.5 | -2.8 | -1.0 | -1.9 | -1.5 | -3.6 | none | +0.7 | -0.6 |
| tikhonov log (gain-inv.) | -(Mild 6 - 5 passes) | 2.4 | 2.9 | 1.1 | 1.6 | 1.6 | 3.4 | none | -0.5 | +0.8 |
| bounded log (gain-inv.) | +(Healthy 7 - 6 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded log (gain-inv.) | -(Healthy 7 - 6 passes) | 1.7 | 1.2 | 1.9 | 1.4 | 1.6 | 2.0 | none | -0.3 | +0.2 |
| bounded log (gain-inv.) | +(Mild 6 - 5 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded log (gain-inv.) | -(Mild 6 - 5 passes) | 2.4 | 2.9 | 1.1 | 1.6 | 1.6 | 3.4 | none | -0.5 | +0.8 |

Against the yardstick (sectors over the larger / over the sum of the two pass differences; contrasts vs the larger pass-difference |LR|, |FB|):

| method | stage | n_sectors_over_yard | n_sectors_over_sum | n_healthy_over_yard | LR | yard_LR | LR_exceeds | FB | yard_FB | FB_exceeds |
|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | Mild_lobe | 6 | 4 | 2 | +0.3 | 0.5 | False | +3.9 | 0.7 | True |
| tikhonov dS | Moderate_lobe | 6 | 5 | 1 | -3.5 | 0.5 | True | +10.2 | 0.7 | True |
| tikhonov dS | Severe_lobe | 6 | 6 | 0 | -0.4 | 0.5 | False | +3.8 | 0.7 | True |
| bounded dS | Mild_lobe | 6 | 6 | 2 | +0.3 | 0.5 | False | +3.9 | 0.7 | True |
| bounded dS | Moderate_lobe | 6 | 6 | 1 | -3.5 | 0.5 | True | +10.2 | 0.7 | True |
| bounded dS | Severe_lobe | 6 | 6 | 0 | -0.4 | 0.5 | False | +3.8 | 0.7 | True |
| tikhonov log (gain-inv.) | Mild_lobe | 6 | 5 | 2 | -0.3 | 0.7 | False | +3.9 | 0.8 | True |
| tikhonov log (gain-inv.) | Moderate_lobe | 6 | 5 | 1 | -3.6 | 0.7 | True | +10.4 | 0.8 | True |
| tikhonov log (gain-inv.) | Severe_lobe | 6 | 6 | 0 | -0.5 | 0.7 | False | +4.1 | 0.8 | True |
| bounded log (gain-inv.) | Mild_lobe | 6 | 6 | 2 | -0.3 | 0.5 | False | +3.9 | 0.8 | True |
| bounded log (gain-inv.) | Moderate_lobe | 6 | 6 | 1 | -3.6 | 0.5 | True | +10.4 | 0.8 | True |
| bounded log (gain-inv.) | Severe_lobe | 6 | 6 | 0 | -0.5 | 0.5 | True | +4.1 | 0.8 | True |

### lobe_A, without opposite paths

Recovered dε'' per sector (* = exceeds the one-extra-pass yardstick of that sector and method, i.e. the larger of the two pass differences' |dε''| in that sector), calls by the frozen rules:

| method | stage | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | called | correct | corr_truth | LR | side | FB | frontback |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | Mild_lobe | 10.5* | 19.9* | 16.7* | 6.8* | 15.5* | 20.6* | S2 S3 S5 S6 | 6 | 0.92 | +0.3 | none | +3.7 | none |
| tikhonov dS | Moderate_lobe | 16.4* | 15.1* | 15.4* | 6.6* | 18.0* | 19.6* | S1 S2 S3 S5 S6 | 6 | 0.93 | -3.5 | none | +9.9 | front |
| tikhonov dS | Severe_lobe | 20.6* | 17.9* | 19.2* | 17.1* | 17.2* | 20.6* | S1 S2 S3 S4 S5 S6 | 6 | 0.49 | -0.4 | none | +3.5 | none |
| bounded dS | Mild_lobe | 10.5* | 19.9* | 16.7* | 6.8* | 15.5* | 20.6* | S2 S3 S5 S6 | 6 | 0.92 | +0.3 | none | +3.7 | none |
| bounded dS | Moderate_lobe | 16.4* | 15.1* | 15.4* | 6.6* | 18.0* | 19.6* | S1 S2 S3 S5 S6 | 6 | 0.93 | -3.5 | none | +9.9 | front |
| bounded dS | Severe_lobe | 20.6* | 17.9* | 19.2* | 17.1* | 17.2* | 20.6* | S1 S2 S3 S4 S5 S6 | 6 | 0.49 | -0.4 | none | +3.5 | none |
| tikhonov log (gain-inv.) | Mild_lobe | 10.5* | 18.6* | 16.5* | 7.2* | 17.1* | 18.7* | S2 S3 S5 S6 | 6 | 0.96 | -0.4 | none | +3.3 | none |
| tikhonov log (gain-inv.) | Moderate_lobe | 16.0* | 17.8* | 15.9* | 6.2* | 18.2* | 22.7* | S1 S2 S3 S5 S6 | 6 | 0.89 | -3.6 | none | +9.8 | front |
| tikhonov log (gain-inv.) | Severe_lobe | 24.2* | 22.1* | 23.9* | 21.0* | 22.5* | 25.2* | S1 S2 S3 S4 S5 S6 | 6 | 0.67 | -0.8 | none | +3.2 | none |
| bounded log (gain-inv.) | Mild_lobe | 10.5* | 18.6* | 16.5* | 7.2* | 17.1* | 18.7* | S2 S3 S5 S6 | 6 | 0.96 | -0.4 | none | +3.3 | none |
| bounded log (gain-inv.) | Moderate_lobe | 16.0* | 17.8* | 15.9* | 6.2* | 18.2* | 22.7* | S1 S2 S3 S5 S6 | 6 | 0.89 | -3.6 | none | +9.8 | front |
| bounded log (gain-inv.) | Severe_lobe | 24.2* | 22.1* | 23.9* | 21.0* | 22.5* | 25.2* | S1 S2 S3 S4 S5 S6 | 6 | 0.67 | -0.8 | none | +3.2 | none |

The yardstick itself (each pass difference, both signs, through the same pipeline):

| method | difference | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR | called | LR | FB |
|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | +(Healthy 7 - 6 passes) | -2.5 | -2.1 | -3.1 | -2.4 | -2.7 | -3.2 | none | +0.4 | -0.1 |
| tikhonov dS | -(Healthy 7 - 6 passes) | 2.5 | 2.1 | 3.1 | 2.4 | 2.7 | 3.2 | none | -0.4 | +0.1 |
| tikhonov dS | +(Mild 6 - 5 passes) | -3.6 | -4.5 | -3.2 | -2.7 | -3.3 | -5.8 | none | +0.6 | -0.9 |
| tikhonov dS | -(Mild 6 - 5 passes) | 3.6 | 4.5 | 3.2 | 2.7 | 3.3 | 5.8 | none | -0.6 | +0.9 |
| bounded dS | +(Healthy 7 - 6 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded dS | -(Healthy 7 - 6 passes) | 2.5 | 2.1 | 3.1 | 2.4 | 2.7 | 3.2 | none | -0.4 | +0.1 |
| bounded dS | +(Mild 6 - 5 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded dS | -(Mild 6 - 5 passes) | 3.6 | 4.5 | 3.2 | 2.7 | 3.3 | 5.8 | none | -0.6 | +0.9 |
| tikhonov log (gain-inv.) | +(Healthy 7 - 6 passes) | -2.1 | -1.6 | -2.6 | -2.0 | -2.1 | -2.7 | none | +0.3 | -0.1 |
| tikhonov log (gain-inv.) | -(Healthy 7 - 6 passes) | 2.1 | 1.5 | 2.5 | 1.9 | 2.0 | 2.7 | none | -0.3 | +0.2 |
| tikhonov log (gain-inv.) | +(Mild 6 - 5 passes) | -3.5 | -3.9 | -2.4 | -3.0 | -2.7 | -5.1 | none | +0.8 | -0.5 |
| tikhonov log (gain-inv.) | -(Mild 6 - 5 passes) | 3.5 | 4.0 | 2.6 | 2.7 | 2.9 | 4.9 | none | -0.6 | +0.8 |
| bounded log (gain-inv.) | +(Healthy 7 - 6 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded log (gain-inv.) | -(Healthy 7 - 6 passes) | 2.1 | 1.5 | 2.5 | 1.9 | 2.0 | 2.7 | none | -0.3 | +0.2 |
| bounded log (gain-inv.) | +(Mild 6 - 5 passes) | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | none | +0.0 | +0.0 |
| bounded log (gain-inv.) | -(Mild 6 - 5 passes) | 3.5 | 4.0 | 2.6 | 2.7 | 2.9 | 4.9 | none | -0.6 | +0.8 |

Against the yardstick (sectors over the larger / over the sum of the two pass differences; contrasts vs the larger pass-difference |LR|, |FB|):

| method | stage | n_sectors_over_yard | n_sectors_over_sum | n_healthy_over_yard | LR | yard_LR | LR_exceeds | FB | yard_FB | FB_exceeds |
|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | Mild_lobe | 6 | 4 | 2 | +0.3 | 0.6 | False | +3.7 | 0.9 | True |
| tikhonov dS | Moderate_lobe | 6 | 5 | 1 | -3.5 | 0.6 | True | +9.9 | 0.9 | True |
| tikhonov dS | Severe_lobe | 6 | 6 | 0 | -0.4 | 0.6 | False | +3.5 | 0.9 | True |
| bounded dS | Mild_lobe | 6 | 6 | 2 | +0.3 | 0.6 | False | +3.7 | 0.9 | True |
| bounded dS | Moderate_lobe | 6 | 6 | 1 | -3.5 | 0.6 | True | +9.9 | 0.9 | True |
| bounded dS | Severe_lobe | 6 | 6 | 0 | -0.4 | 0.6 | False | +3.5 | 0.9 | True |
| tikhonov log (gain-inv.) | Mild_lobe | 6 | 4 | 2 | -0.4 | 0.8 | False | +3.3 | 0.8 | True |
| tikhonov log (gain-inv.) | Moderate_lobe | 6 | 5 | 1 | -3.6 | 0.8 | True | +9.8 | 0.8 | True |
| tikhonov log (gain-inv.) | Severe_lobe | 6 | 6 | 0 | -0.8 | 0.8 | False | +3.2 | 0.8 | True |
| bounded log (gain-inv.) | Mild_lobe | 6 | 6 | 2 | -0.4 | 0.6 | False | +3.3 | 0.8 | True |
| bounded log (gain-inv.) | Moderate_lobe | 6 | 6 | 1 | -3.6 | 0.6 | True | +9.8 | 0.8 | True |
| bounded log (gain-inv.) | Severe_lobe | 6 | 6 | 0 | -0.8 | 0.6 | True | +3.2 | 0.8 | True |

Change of the recovered dε'' when the 7-pass reference (§3) is replaced by the 6-pass reference (lobe_A − §3, all paths). For the linear fits it equals minus the Healthy 7 − 6 yardstick row above:

| method | stage | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR |
|---|---|---|---|---|---|---|---|
| tikhonov dS | Mild_lobe | -2.2 | -2.0 | -2.7 | -2.2 | -2.5 | -3.0 |
| tikhonov dS | Moderate_lobe | -2.2 | -2.0 | -2.7 | -2.2 | -2.4 | -3.0 |
| tikhonov dS | Severe_lobe | -2.2 | -2.0 | -2.7 | -2.2 | -2.5 | -2.9 |
| bounded dS | Mild_lobe | -2.2 | -2.0 | -2.7 | -2.2 | -2.5 | -3.0 |
| bounded dS | Moderate_lobe | -2.2 | -2.0 | -2.7 | -2.2 | -2.4 | -3.0 |
| bounded dS | Severe_lobe | -2.2 | -2.0 | -2.7 | -2.2 | -2.5 | -2.9 |
| tikhonov log (gain-inv.) | Mild_lobe | -1.8 | -0.9 | -1.9 | -1.2 | -1.8 | -1.8 |
| tikhonov log (gain-inv.) | Moderate_lobe | -1.7 | -1.3 | -1.9 | -1.3 | -1.7 | -2.2 |
| tikhonov log (gain-inv.) | Severe_lobe | -2.0 | -1.4 | -2.2 | -1.6 | -1.9 | -2.6 |
| bounded log (gain-inv.) | Mild_lobe | -1.8 | -0.9 | -1.9 | -1.2 | -1.8 | -1.8 |
| bounded log (gain-inv.) | Moderate_lobe | -1.7 | -1.3 | -1.9 | -1.3 | -1.7 | -2.2 |
| bounded log (gain-inv.) | Severe_lobe | -2.0 | -1.4 | -2.2 | -1.6 | -1.9 | -2.6 |

### Does the reconstruction depend on the opposite paths?

Share of the information (whitened Fisher diagonal) on each sector's dε'' that comes from the 3 opposite paths, and share of the whitened data energy in those paths (all-path model):

| model | S1 Fr | S2 TL | S3 PL | S4 Oc | S5 PR | S6 TR |
|---|---|---|---|---|---|---|
| dS | 9.1% | 9.9% | 10.0% | 10.4% | 10.2% | 9.7% |
| log | 12.6% | 12.2% | 12.6% | 14.2% | 14.0% | 13.2% |

| model | Mild_lobe | Moderate_lobe | Severe_lobe | Healthy 7 - 6 passes | Mild 6 - 5 passes |
|---|---|---|---|---|---|
| dS | 4.5% | 9.1% | 12.4% | 12.5% | 8.6% |
| log | 11.9% | 20.8% | 25.2% | 11.8% | 5.1% |

Information share per path class (mean over the six sectors' dε''):

| model | reflection | neighbour | second-neighbour | opposite |
|---|---|---|---|---|
| dS | 19.4% | 56.5% | 14.2% | 9.9% |
| log | 25.3% | 45.9% | 15.6% | 13.1% |

(For the gain-invariant model the rows are taken after the gain projection, which mixes paths, so its shares are approximate; the 'without opposite paths' fits rebuild the projection on the 18 kept paths.)

### Reading

- **Absolute sector levels.** A one-pass mesh change shifts every sector by up to 5.2 (dε''), almost uniformly (same sign in all six sectors; table 'yardstick itself'). Every recovered sector value, healthy ones included, exceeds its own sector's yardstick (3 healthy-sector estimates over the yardstick, primary method, all paths). So the upward offset of the healthy sectors (about 5–10 instead of 0.3) is not explained by a one-pass mesh change; Born model error and leakage from neighbouring affected sectors are the likely cause. Per-sector exceedance is therefore not a test of 'affected'; the contrasts below are.
- **The frozen absolute threshold is sensitive to the reference mesh.** Replacing the 7-pass reference by the 6-pass one lowers every sector by about 2–3 (table above), comparable to the margin of some calls around T_abs = 13.8. Primary method, all paths: Mild S2 S3 S6 (5/6 correct); Moderate S1 S3 S5 S6 (5/6 correct); Severe S1 S2 S3 S4 S5 S6 (6/6 correct). Without the opposite paths: Mild S2 S3 S5 S6 (6/6 correct); Moderate S1 S2 S3 S5 S6 (6/6 correct); Severe S1 S2 S3 S4 S5 S6 (6/6 correct). Gain-invariant, all paths: Mild S2 S3 S5 S6 (6/6 correct); Moderate S1 S2 S3 S5 S6 (6/6 correct); Severe S1 S2 S3 S4 S5 S6 (6/6 correct). Without: Mild S2 S3 S5 S6 (6/6 correct); Moderate S1 S2 S3 S5 S6 (6/6 correct); Severe S1 S2 S3 S4 S5 S6 (6/6 correct).
- **Front/back.** Moderate's FB = S1 − S4 is +10.2 (all paths) and +9.9 (without opposite paths) for the primary method, +10.4 / +9.8 gain-invariant; the one-pass yardstick gives |FB| ≤ 0.9. Front is called for Moderate by every method in both path sets. Mild and Severe (S1 and S4 equal in truth) give FB of about +3 to +4, also well above the yardstick: a systematic front-positive bias of about 4 that is not mesh. The frozen T_FB (Mild's |FB|) absorbs it, except in the bounded-dS fit, whose T_FB = 3.8 lets Mild and Severe through in the all-path version.
- **Left/right.** The one-pass yardstick gives |LR| ≤ 0.8. The mirror-symmetric designs give |LR| up to 3.6 (Moderate): more than the mesh yardstick, but below the frozen T_LR = 4.1. The pre-registered LeftOnly contrast (+14.7 ± 2.2, Born-simulated) is about 20× the one-pass yardstick.
- **Opposite paths.** They carry 9%–14% of the information on each sector and 4%–25% of the stage data energy; in the whitened complex data they carry 5%–13% of the pass-difference energy, i.e. not more than their information share, so the pass difference is not concentrated on them as seen by the inversion. Removing them moves the sector estimates by +0.5 to +5.5, raises the yardstick slightly, and changes calls only where a sector sits near T_abs. Pattern, front/back and left/right conclusions are the same with and without them. Both versions are tabulated above and neither is preferred.

## 5d. Front/back and left/right against all three error rulers (lobe_A, 4 Oct)

The main session (`results/05_lobe/mesh/report.md`, commits aff9d56–bf5af59) found localisation not separable from error once the numerical symmetry floor and antenna gain/phase errors are included. The same rulers are applied here to the contrasts of the recovered conductivity map, each propagated through the frozen inversions (κ, λ unchanged):

1. **Mesh yardstick**: one extra adaptive pass (Healthy 7 − 6, Mild 6 − 5), both signs, largest |contrast|.
2. **Numerical symmetry floor**: as in Prompt 07, per-design numerical SD = √2 × the mirror-antisymmetric part of the design's S-matrix. That pattern is placed in the 6 rotations × 2 reflections of the ring (both signs) and passed through the pipeline; the rms contrast is the design's floor; a difference of two designs adds both floors in quadrature. All four lobe_A designs are mirror-symmetric, Healthy_sliced_new included.
3. **Gain/phase errors**: 200 Monte Carlo draws per design with the Prompt 07 measurement model (`adstage.pipeline.augment.draws`: typical noise profile, setup perturbation amp_sd 0.015, phase_sd 10.0° per port, jitter 1.0 MHz, plus per-port gain uniform ±0.5 dB, or ±2 dB with ±10° phase), independent draws for the two designs of each comparison. Spread = SD of the contrast over the draws; the 95 % interval is also given. Note that this model contains more than gain errors.

Ruler = max(yardstick, symmetry floor, measurement-error SD of the Prompt 07 model; column gain_sd, dominant = measurement). |clean contrast| / ruler ≥ 3: exceeds; 2–3: sensitive; < 2: not separable (the main session's categories). 'clean_ratio' = |clean contrast| / max(yardstick, symmetry floor): the simulation-level ruler without measurement errors (the main session's 'clean ruler'). Truth = sensitivity-weighted true dε'' contrast. **Moderate − Mild is not a pure frontal contrast**: besides adding the frontal lobe (S1 +14.8) it changes every affected lobe (S2, S3, S5, S6: +1.8, +2.1, +2.1, +1.8) and the CSF material everywhere (S4 +0.2).

**Erratum: the frozen 'gain-invariant' log method is not gain-invariant.** `study_lobe.RegionModel` (kind 'log') removes the per-port gain subspace with P = I − A A⁺ but applies it to the noise-whitened log-ratios W_f y. A per-port gain g adds W_f A g, and P W_f A g ≠ 0 because the per-path weights W_f differ (weak paths are weighted up), so gains leak into the fit (component table below). The frozen pipeline and the pre-registered predictions keep this method unchanged; its name is a misnomer, and the 'log, gain-invariant' CRLB columns in §2 are CRLBs for that projected data, not for gain-free data. For comparison only, **'tikhonov log, whitened projection (post-hoc)'** projects after whitening, per frequency (P_f = I − W_f A (W_f A)⁺), with the frozen κ and λ_log; it has no frozen thresholds and makes no calls.

Which part of the Prompt 07 measurement model drives the spread (Moderate − Healthy, all paths; SD of the contrast over 100 draws per component, every other component switched off):

| component | FB sd, tikhonov dS | LR sd, tikhonov dS | FB sd, tikhonov log (gain-inv.) | LR sd, tikhonov log (gain-inv.) | FB sd, tikhonov log, whitened projection (post-hoc) | LR sd, tikhonov log, whitened projection (post-hoc) |
|---|---|---|---|---|---|---|
| typical noise profile only | 3.94 | 2.01 | 4.32 | 2.43 | 4.50 | 2.50 |
| frequency jitter 1 MHz only | 0.22 | 0.06 | 0.15 | 0.16 | 0.20 | 0.05 |
| per-port amplitude 1.5 % + phase 10° (07 setup) only | 32.51 | 25.79 | 12.45 | 10.91 | 0.00 | 0.00 |
| per-port gain ±0.5 dB only | 3.65 | 3.04 | 0.72 | 0.19 | 0.00 | 0.00 |
| per-port gain ±2 dB, phase ±10° only | 24.58 | 21.71 | 7.59 | 6.29 | 0.00 | 0.00 |

### Gain/phase condition: ±0.5 dB gain

Front/back (FB = S1 − S4):

| variant | method | comparison | contrast | clean | truth | yardstick | floor | gain_sd | gain_95 | ruler | dominant | ratio | verdict | clean_ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all 21 paths | tikhonov dS | Mild − Healthy | FB | +3.9 | -0.0 | 0.71 | 1.27 | 31.71 | [-60.4, +58.0] | 31.71 | measurement | 0.12 | not separable (< 2×) | 3.04 |
| all 21 paths | tikhonov dS | Moderate − Healthy | FB | +10.2 | +14.6 | 0.71 | 4.58 | 34.67 | [-55.5, +70.5] | 34.67 | measurement | 0.29 | not separable (< 2×) | 2.22 |
| all 21 paths | tikhonov dS | Severe − Healthy | FB | +3.8 | +0.1 | 0.71 | 1.66 | 31.70 | [-60.8, +63.3] | 31.70 | measurement | 0.12 | not separable (< 2×) | 2.31 |
| all 21 paths | tikhonov dS | Moderate − Mild | FB | +6.2 | +14.6 | 0.71 | 4.41 | 32.64 | [-52.4, +73.1] | 32.64 | measurement | 0.19 | not separable (< 2×) | 1.41 |
| all 21 paths | bounded dS | Mild − Healthy | FB | +3.9 | -0.0 | 0.71 | 0.57 | 21.32 | [-42.8, +37.7] | 21.32 | measurement | 0.18 | not separable (< 2×) | 5.43 |
| all 21 paths | bounded dS | Moderate − Healthy | FB | +10.2 | +14.6 | 0.71 | 1.95 | 24.40 | [-39.1, +49.2] | 24.40 | measurement | 0.42 | not separable (< 2×) | 5.20 |
| all 21 paths | bounded dS | Severe − Healthy | FB | +3.8 | +0.1 | 0.71 | 0.76 | 26.63 | [-46.8, +51.3] | 26.63 | measurement | 0.14 | not separable (< 2×) | 5.05 |
| all 21 paths | bounded dS | Moderate − Mild | FB | +4.4 | +14.6 | 0.71 | 1.89 | 16.11 | [-30.9, +38.8] | 16.11 | measurement | 0.27 | not separable (< 2×) | 2.31 |
| all 21 paths | tikhonov log (gain-inv.) | Mild − Healthy | FB | +3.9 | -0.0 | 0.83 | 1.27 | 13.51 | [-21.9, +30.5] | 13.51 | measurement | 0.29 | not separable (< 2×) | 3.09 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Healthy | FB | +10.4 | +14.6 | 0.83 | 4.07 | 14.10 | [-13.7, +40.1] | 14.10 | measurement | 0.74 | not separable (< 2×) | 2.57 |
| all 21 paths | tikhonov log (gain-inv.) | Severe − Healthy | FB | +4.1 | +0.1 | 0.83 | 1.46 | 13.29 | [-22.9, +27.7] | 13.29 | measurement | 0.31 | not separable (< 2×) | 2.84 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Mild | FB | +6.4 | +14.6 | 0.83 | 3.89 | 15.65 | [-23.0, +33.9] | 15.65 | measurement | 0.41 | not separable (< 2×) | 1.65 |
| all 21 paths | bounded log (gain-inv.) | Mild − Healthy | FB | +3.9 | -0.0 | 0.83 | 0.55 | 10.70 | [-17.3, +23.9] | 10.70 | measurement | 0.37 | not separable (< 2×) | 4.71 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Healthy | FB | +10.4 | +14.6 | 0.83 | 1.66 | 12.00 | [-12.9, +33.8] | 12.00 | measurement | 0.87 | not separable (< 2×) | 6.29 |
| all 21 paths | bounded log (gain-inv.) | Severe − Healthy | FB | +4.1 | +0.1 | 0.83 | 0.61 | 13.09 | [-21.9, +27.7] | 13.09 | measurement | 0.32 | not separable (< 2×) | 4.97 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Mild | FB | +5.7 | +14.6 | 0.83 | 1.61 | 9.38 | [-13.2, +24.6] | 9.38 | measurement | 0.61 | not separable (< 2×) | 3.53 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | FB | +2.3 | -0.0 | 0.27 | 0.97 | 4.07 | [-5.2, +11.0] | 4.07 | measurement | 0.56 | not separable (< 2×) | 2.37 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | FB | +10.3 | +14.6 | 0.27 | 3.34 | 4.17 | [+3.0, +19.0] | 4.17 | measurement | 2.47 | sensitive (2–3×) | 3.09 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | FB | +4.9 | +0.1 | 0.27 | 1.12 | 4.50 | [-1.9, +15.1] | 4.50 | measurement | 1.08 | not separable (< 2×) | 4.34 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | FB | +8.5 | +14.6 | 0.27 | 3.22 | 4.72 | [-0.5, +18.2] | 4.72 | measurement | 1.80 | not separable (< 2×) | 2.65 |
| without opposite paths | tikhonov dS | Mild − Healthy | FB | +3.7 | -0.0 | 0.92 | 1.27 | 31.74 | [-59.9, +57.8] | 31.74 | measurement | 0.12 | not separable (< 2×) | 2.95 |
| without opposite paths | tikhonov dS | Moderate − Healthy | FB | +9.9 | +14.6 | 0.92 | 4.58 | 34.66 | [-55.7, +71.5] | 34.66 | measurement | 0.29 | not separable (< 2×) | 2.16 |
| without opposite paths | tikhonov dS | Severe − Healthy | FB | +3.5 | +0.1 | 0.92 | 1.66 | 31.75 | [-62.4, +62.8] | 31.75 | measurement | 0.11 | not separable (< 2×) | 2.12 |
| without opposite paths | tikhonov dS | Moderate − Mild | FB | +6.1 | +14.6 | 0.92 | 4.42 | 32.77 | [-52.9, +72.3] | 32.77 | measurement | 0.18 | not separable (< 2×) | 1.37 |
| without opposite paths | bounded dS | Mild − Healthy | FB | +3.7 | -0.0 | 0.92 | 0.63 | 22.69 | [-42.6, +41.0] | 22.69 | measurement | 0.16 | not separable (< 2×) | 4.04 |
| without opposite paths | bounded dS | Moderate − Healthy | FB | +9.9 | +14.6 | 0.92 | 2.19 | 25.58 | [-41.9, +50.8] | 25.58 | measurement | 0.39 | not separable (< 2×) | 4.51 |
| without opposite paths | bounded dS | Severe − Healthy | FB | +3.5 | +0.1 | 0.92 | 0.85 | 27.91 | [-50.0, +54.5] | 27.91 | measurement | 0.13 | not separable (< 2×) | 3.81 |
| without opposite paths | bounded dS | Moderate − Mild | FB | +4.3 | +14.6 | 0.92 | 2.12 | 17.34 | [-30.4, +41.5] | 17.34 | measurement | 0.25 | not separable (< 2×) | 2.02 |
| without opposite paths | tikhonov log (gain-inv.) | Mild − Healthy | FB | +3.3 | -0.0 | 0.79 | 1.28 | 13.48 | [-22.9, +28.8] | 13.48 | measurement | 0.24 | not separable (< 2×) | 2.58 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Healthy | FB | +9.8 | +14.6 | 0.79 | 4.08 | 14.06 | [-14.8, +39.2] | 14.06 | measurement | 0.69 | not separable (< 2×) | 2.39 |
| without opposite paths | tikhonov log (gain-inv.) | Severe − Healthy | FB | +3.2 | +0.1 | 0.79 | 1.47 | 13.13 | [-23.6, +26.4] | 13.13 | measurement | 0.24 | not separable (< 2×) | 2.17 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Mild | FB | +6.5 | +14.6 | 0.79 | 3.90 | 15.52 | [-23.0, +34.1] | 15.52 | measurement | 0.42 | not separable (< 2×) | 1.66 |
| without opposite paths | bounded log (gain-inv.) | Mild − Healthy | FB | +3.3 | -0.0 | 0.79 | 0.67 | 11.16 | [-21.0, +24.8] | 11.16 | measurement | 0.30 | not separable (< 2×) | 4.17 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Healthy | FB | +9.8 | +14.6 | 0.79 | 2.00 | 12.25 | [-12.6, +35.0] | 12.25 | measurement | 0.80 | not separable (< 2×) | 4.90 |
| without opposite paths | bounded log (gain-inv.) | Severe − Healthy | FB | +3.2 | +0.1 | 0.79 | 0.79 | 12.90 | [-23.5, +26.4] | 12.90 | measurement | 0.25 | not separable (< 2×) | 4.03 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Mild | FB | +4.9 | +14.6 | 0.79 | 1.91 | 9.72 | [-15.1, +26.0] | 9.72 | measurement | 0.50 | not separable (< 2×) | 2.54 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | FB | +1.6 | -0.0 | 0.43 | 0.98 | 4.08 | [-6.1, +10.4] | 4.08 | measurement | 0.39 | not separable (< 2×) | 1.63 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | FB | +9.4 | +14.6 | 0.43 | 3.35 | 4.15 | [+2.5, +17.6] | 4.15 | measurement | 2.26 | sensitive (2–3×) | 2.80 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | FB | +3.3 | +0.1 | 0.43 | 1.13 | 4.48 | [-3.5, +13.7] | 4.48 | measurement | 0.74 | not separable (< 2×) | 2.96 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | FB | +8.4 | +14.6 | 0.43 | 3.23 | 4.70 | [-0.7, +18.1] | 4.70 | measurement | 1.78 | not separable (< 2×) | 2.60 |

Left/right (LR = mean(S2, S3) − mean(S5, S6); all designs are mirror-symmetric, true LR = 0):

| variant | method | comparison | contrast | clean | truth | yardstick | floor | gain_sd | gain_95 | ruler | dominant | ratio | verdict | clean_ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all 21 paths | tikhonov dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.52 | 1.20 | 26.54 | [-47.9, +47.7] | 26.54 | measurement | 0.01 | not separable (< 2×) | 0.29 |
| all 21 paths | tikhonov dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.52 | 4.21 | 25.93 | [-57.9, +42.4] | 25.93 | measurement | 0.14 | not separable (< 2×) | 0.84 |
| all 21 paths | tikhonov dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.52 | 1.51 | 23.21 | [-48.4, +46.9] | 23.21 | measurement | 0.02 | not separable (< 2×) | 0.28 |
| all 21 paths | tikhonov dS | Moderate − Mild | LR | -3.9 | +0.0 | 0.52 | 4.05 | 23.67 | [-50.7, +36.3] | 23.67 | measurement | 0.17 | not separable (< 2×) | 0.96 |
| all 21 paths | bounded dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.52 | 0.53 | 21.02 | [-39.0, +37.0] | 21.02 | measurement | 0.02 | not separable (< 2×) | 0.65 |
| all 21 paths | bounded dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.52 | 1.79 | 20.83 | [-44.1, +33.0] | 20.83 | measurement | 0.17 | not separable (< 2×) | 1.97 |
| all 21 paths | bounded dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.52 | 0.65 | 19.79 | [-43.2, +39.0] | 19.79 | measurement | 0.02 | not separable (< 2×) | 0.65 |
| all 21 paths | bounded dS | Moderate − Mild | LR | -0.9 | +0.0 | 0.52 | 1.73 | 11.29 | [-22.8, +22.4] | 11.29 | measurement | 0.08 | not separable (< 2×) | 0.54 |
| all 21 paths | tikhonov log (gain-inv.) | Mild − Healthy | LR | -0.3 | -0.0 | 0.68 | 1.17 | 11.14 | [-21.8, +18.7] | 11.14 | measurement | 0.03 | not separable (< 2×) | 0.24 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.68 | 3.76 | 10.82 | [-25.0, +14.5] | 10.82 | measurement | 0.33 | not separable (< 2×) | 0.95 |
| all 21 paths | tikhonov log (gain-inv.) | Severe − Healthy | LR | -0.5 | -0.0 | 0.68 | 1.28 | 11.38 | [-24.1, +20.2] | 11.38 | measurement | 0.05 | not separable (< 2×) | 0.41 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Mild | LR | -3.8 | +0.0 | 0.68 | 3.60 | 11.05 | [-24.8, +16.7] | 11.05 | measurement | 0.34 | not separable (< 2×) | 1.05 |
| all 21 paths | bounded log (gain-inv.) | Mild − Healthy | LR | -0.3 | -0.0 | 0.48 | 0.51 | 10.65 | [-20.5, +18.0] | 10.65 | measurement | 0.03 | not separable (< 2×) | 0.55 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.48 | 1.55 | 10.44 | [-23.7, +13.4] | 10.44 | measurement | 0.34 | not separable (< 2×) | 2.29 |
| all 21 paths | bounded log (gain-inv.) | Severe − Healthy | LR | -0.5 | -0.0 | 0.48 | 0.53 | 11.23 | [-24.1, +20.0] | 11.23 | measurement | 0.05 | not separable (< 2×) | 0.99 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Mild | LR | -1.8 | +0.0 | 0.48 | 1.51 | 5.55 | [-13.3, +9.2] | 5.55 | measurement | 0.33 | not separable (< 2×) | 1.22 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | LR | +0.0 | -0.0 | 0.19 | 0.86 | 2.62 | [-4.9, +4.4] | 2.62 | measurement | 0.02 | not separable (< 2×) | 0.06 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | LR | -3.0 | -0.0 | 0.19 | 3.14 | 2.76 | [-8.1, +3.2] | 3.14 | symmetry | 0.95 | not separable (< 2×) | 0.95 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | LR | -0.5 | -0.0 | 0.19 | 0.96 | 2.58 | [-5.3, +4.2] | 2.58 | measurement | 0.19 | not separable (< 2×) | 0.50 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | LR | -3.6 | +0.0 | 0.19 | 3.03 | 2.93 | [-8.1, +2.1] | 3.03 | symmetry | 1.18 | not separable (< 2×) | 1.18 |
| without opposite paths | tikhonov dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.65 | 1.20 | 26.61 | [-47.9, +47.8] | 26.61 | measurement | 0.01 | not separable (< 2×) | 0.25 |
| without opposite paths | tikhonov dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.65 | 4.21 | 26.00 | [-58.3, +43.2] | 26.00 | measurement | 0.14 | not separable (< 2×) | 0.84 |
| without opposite paths | tikhonov dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.65 | 1.51 | 23.29 | [-48.7, +45.3] | 23.29 | measurement | 0.02 | not separable (< 2×) | 0.27 |
| without opposite paths | tikhonov dS | Moderate − Mild | LR | -3.9 | +0.0 | 0.65 | 4.06 | 23.73 | [-50.9, +36.4] | 23.73 | measurement | 0.16 | not separable (< 2×) | 0.95 |
| without opposite paths | bounded dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.65 | 0.59 | 21.85 | [-40.2, +37.9] | 21.85 | measurement | 0.01 | not separable (< 2×) | 0.46 |
| without opposite paths | bounded dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.65 | 2.00 | 21.64 | [-45.5, +34.2] | 21.64 | measurement | 0.16 | not separable (< 2×) | 1.77 |
| without opposite paths | bounded dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.65 | 0.73 | 20.48 | [-44.9, +39.5] | 20.48 | measurement | 0.02 | not separable (< 2×) | 0.56 |
| without opposite paths | bounded dS | Moderate − Mild | LR | -1.1 | +0.0 | 0.65 | 1.94 | 12.21 | [-25.9, +24.7] | 12.21 | measurement | 0.09 | not separable (< 2×) | 0.58 |
| without opposite paths | tikhonov log (gain-inv.) | Mild − Healthy | LR | -0.4 | -0.0 | 0.80 | 1.17 | 11.15 | [-22.1, +18.4] | 11.15 | measurement | 0.04 | not separable (< 2×) | 0.33 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.80 | 3.77 | 10.85 | [-24.9, +14.5] | 10.85 | measurement | 0.33 | not separable (< 2×) | 0.96 |
| without opposite paths | tikhonov log (gain-inv.) | Severe − Healthy | LR | -0.8 | -0.0 | 0.80 | 1.28 | 11.46 | [-24.6, +20.3] | 11.46 | measurement | 0.07 | not separable (< 2×) | 0.62 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Mild | LR | -3.7 | +0.0 | 0.80 | 3.61 | 11.06 | [-24.8, +16.5] | 11.06 | measurement | 0.34 | not separable (< 2×) | 1.04 |
| without opposite paths | bounded log (gain-inv.) | Mild − Healthy | LR | -0.4 | -0.0 | 0.61 | 0.60 | 10.62 | [-20.6, +18.4] | 10.62 | measurement | 0.04 | not separable (< 2×) | 0.64 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.61 | 1.85 | 10.40 | [-23.7, +13.4] | 10.40 | measurement | 0.35 | not separable (< 2×) | 1.95 |
| without opposite paths | bounded log (gain-inv.) | Severe − Healthy | LR | -0.8 | -0.0 | 0.61 | 0.66 | 11.32 | [-24.6, +18.7] | 11.32 | measurement | 0.07 | not separable (< 2×) | 1.20 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Mild | LR | -2.3 | +0.0 | 0.61 | 1.78 | 6.59 | [-16.6, +12.2] | 6.59 | measurement | 0.35 | not separable (< 2×) | 1.30 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | LR | +0.0 | -0.0 | 0.30 | 0.86 | 2.60 | [-5.1, +4.3] | 2.60 | measurement | 0.01 | not separable (< 2×) | 0.02 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | LR | -2.9 | -0.0 | 0.30 | 3.15 | 2.75 | [-8.1, +3.2] | 3.15 | symmetry | 0.93 | not separable (< 2×) | 0.93 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | LR | -0.5 | -0.0 | 0.30 | 0.97 | 2.60 | [-5.4, +4.3] | 2.60 | measurement | 0.19 | not separable (< 2×) | 0.52 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | LR | -3.5 | +0.0 | 0.30 | 3.04 | 2.93 | [-8.0, +2.1] | 3.04 | symmetry | 1.16 | not separable (< 2×) | 1.16 |

### Gain/phase condition: ±2 dB gain, ±10° phase

Front/back (FB = S1 − S4):

| variant | method | comparison | contrast | clean | truth | yardstick | floor | gain_sd | gain_95 | ruler | dominant | ratio | verdict | clean_ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all 21 paths | tikhonov dS | Mild − Healthy | FB | +3.9 | -0.0 | 0.71 | 1.27 | 43.36 | [-72.2, +83.1] | 43.36 | measurement | 0.09 | not separable (< 2×) | 3.04 |
| all 21 paths | tikhonov dS | Moderate − Healthy | FB | +10.2 | +14.6 | 0.71 | 4.58 | 41.44 | [-78.4, +84.8] | 41.44 | measurement | 0.25 | not separable (< 2×) | 2.22 |
| all 21 paths | tikhonov dS | Severe − Healthy | FB | +3.8 | +0.1 | 0.71 | 1.66 | 44.30 | [-86.9, +87.4] | 44.30 | measurement | 0.09 | not separable (< 2×) | 2.31 |
| all 21 paths | tikhonov dS | Moderate − Mild | FB | +6.2 | +14.6 | 0.71 | 4.41 | 41.20 | [-71.7, +93.5] | 41.20 | measurement | 0.15 | not separable (< 2×) | 1.41 |
| all 21 paths | bounded dS | Mild − Healthy | FB | +3.9 | -0.0 | 0.71 | 0.57 | 26.41 | [-48.6, +56.2] | 26.41 | measurement | 0.15 | not separable (< 2×) | 5.43 |
| all 21 paths | bounded dS | Moderate − Healthy | FB | +10.2 | +14.6 | 0.71 | 1.95 | 27.99 | [-55.5, +52.5] | 27.99 | measurement | 0.36 | not separable (< 2×) | 5.20 |
| all 21 paths | bounded dS | Severe − Healthy | FB | +3.8 | +0.1 | 0.71 | 0.76 | 31.55 | [-53.3, +62.8] | 31.55 | measurement | 0.12 | not separable (< 2×) | 5.05 |
| all 21 paths | bounded dS | Moderate − Mild | FB | +4.4 | +14.6 | 0.71 | 1.89 | 21.66 | [-41.2, +49.0] | 21.66 | measurement | 0.20 | not separable (< 2×) | 2.31 |
| all 21 paths | tikhonov log (gain-inv.) | Mild − Healthy | FB | +3.9 | -0.0 | 0.83 | 1.27 | 15.20 | [-24.9, +36.7] | 15.20 | measurement | 0.26 | not separable (< 2×) | 3.09 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Healthy | FB | +10.4 | +14.6 | 0.83 | 4.07 | 16.27 | [-22.4, +41.1] | 16.27 | measurement | 0.64 | not separable (< 2×) | 2.57 |
| all 21 paths | tikhonov log (gain-inv.) | Severe − Healthy | FB | +4.1 | +0.1 | 0.83 | 1.46 | 15.67 | [-32.1, +29.3] | 15.67 | measurement | 0.26 | not separable (< 2×) | 2.84 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Mild | FB | +6.4 | +14.6 | 0.83 | 3.89 | 17.69 | [-27.9, +37.8] | 17.69 | measurement | 0.36 | not separable (< 2×) | 1.65 |
| all 21 paths | bounded log (gain-inv.) | Mild − Healthy | FB | +3.9 | -0.0 | 0.83 | 0.55 | 11.33 | [-19.1, +25.8] | 11.33 | measurement | 0.35 | not separable (< 2×) | 4.71 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Healthy | FB | +10.4 | +14.6 | 0.83 | 1.66 | 13.59 | [-17.4, +36.3] | 13.59 | measurement | 0.77 | not separable (< 2×) | 6.29 |
| all 21 paths | bounded log (gain-inv.) | Severe − Healthy | FB | +4.1 | +0.1 | 0.83 | 0.61 | 14.74 | [-29.1, +29.3] | 14.74 | measurement | 0.28 | not separable (< 2×) | 4.97 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Mild | FB | +5.7 | +14.6 | 0.83 | 1.61 | 11.46 | [-17.6, +28.5] | 11.46 | measurement | 0.50 | not separable (< 2×) | 3.53 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | FB | +2.3 | -0.0 | 0.27 | 0.97 | 4.22 | [-5.6, +12.0] | 4.22 | measurement | 0.54 | not separable (< 2×) | 2.37 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | FB | +10.3 | +14.6 | 0.27 | 3.34 | 4.33 | [+3.2, +18.7] | 4.33 | measurement | 2.38 | sensitive (2–3×) | 3.09 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | FB | +4.9 | +0.1 | 0.27 | 1.12 | 4.74 | [-4.4, +14.8] | 4.74 | measurement | 1.03 | not separable (< 2×) | 4.34 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | FB | +8.5 | +14.6 | 0.27 | 3.22 | 4.73 | [-0.4, +18.8] | 4.73 | measurement | 1.80 | not separable (< 2×) | 2.65 |
| without opposite paths | tikhonov dS | Mild − Healthy | FB | +3.7 | -0.0 | 0.92 | 1.27 | 43.31 | [-73.3, +83.6] | 43.31 | measurement | 0.09 | not separable (< 2×) | 2.95 |
| without opposite paths | tikhonov dS | Moderate − Healthy | FB | +9.9 | +14.6 | 0.92 | 4.58 | 41.40 | [-80.0, +84.2] | 41.40 | measurement | 0.24 | not separable (< 2×) | 2.16 |
| without opposite paths | tikhonov dS | Severe − Healthy | FB | +3.5 | +0.1 | 0.92 | 1.66 | 44.43 | [-85.7, +87.4] | 44.43 | measurement | 0.08 | not separable (< 2×) | 2.12 |
| without opposite paths | tikhonov dS | Moderate − Mild | FB | +6.1 | +14.6 | 0.92 | 4.42 | 41.28 | [-72.2, +94.6] | 41.28 | measurement | 0.15 | not separable (< 2×) | 1.37 |
| without opposite paths | bounded dS | Mild − Healthy | FB | +3.7 | -0.0 | 0.92 | 0.63 | 28.08 | [-49.0, +64.1] | 28.08 | measurement | 0.13 | not separable (< 2×) | 4.04 |
| without opposite paths | bounded dS | Moderate − Healthy | FB | +9.9 | +14.6 | 0.92 | 2.19 | 29.46 | [-59.2, +60.2] | 29.46 | measurement | 0.34 | not separable (< 2×) | 4.51 |
| without opposite paths | bounded dS | Severe − Healthy | FB | +3.5 | +0.1 | 0.92 | 0.85 | 33.13 | [-59.8, +66.3] | 33.13 | measurement | 0.11 | not separable (< 2×) | 3.81 |
| without opposite paths | bounded dS | Moderate − Mild | FB | +4.3 | +14.6 | 0.92 | 2.12 | 23.39 | [-43.6, +54.4] | 23.39 | measurement | 0.18 | not separable (< 2×) | 2.02 |
| without opposite paths | tikhonov log (gain-inv.) | Mild − Healthy | FB | +3.3 | -0.0 | 0.79 | 1.28 | 15.21 | [-24.8, +35.8] | 15.21 | measurement | 0.22 | not separable (< 2×) | 2.58 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Healthy | FB | +9.8 | +14.6 | 0.79 | 4.08 | 16.30 | [-21.7, +41.8] | 16.30 | measurement | 0.60 | not separable (< 2×) | 2.39 |
| without opposite paths | tikhonov log (gain-inv.) | Severe − Healthy | FB | +3.2 | +0.1 | 0.79 | 1.47 | 15.52 | [-33.3, +29.7] | 15.52 | measurement | 0.21 | not separable (< 2×) | 2.17 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Mild | FB | +6.5 | +14.6 | 0.79 | 3.90 | 17.61 | [-28.6, +38.5] | 17.61 | measurement | 0.37 | not separable (< 2×) | 1.66 |
| without opposite paths | bounded log (gain-inv.) | Mild − Healthy | FB | +3.3 | -0.0 | 0.79 | 0.67 | 12.05 | [-20.8, +27.0] | 12.05 | measurement | 0.27 | not separable (< 2×) | 4.17 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Healthy | FB | +9.8 | +14.6 | 0.79 | 2.00 | 13.92 | [-19.3, +37.4] | 13.92 | measurement | 0.70 | not separable (< 2×) | 4.90 |
| without opposite paths | bounded log (gain-inv.) | Severe − Healthy | FB | +3.2 | +0.1 | 0.79 | 0.79 | 14.66 | [-29.6, +28.5] | 14.66 | measurement | 0.22 | not separable (< 2×) | 4.03 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Mild | FB | +4.9 | +14.6 | 0.79 | 1.91 | 12.16 | [-19.8, +32.0] | 12.16 | measurement | 0.40 | not separable (< 2×) | 2.54 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | FB | +1.6 | -0.0 | 0.43 | 0.98 | 4.28 | [-6.1, +11.1] | 4.28 | measurement | 0.37 | not separable (< 2×) | 1.63 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | FB | +9.4 | +14.6 | 0.43 | 3.35 | 4.35 | [+2.2, +18.0] | 4.35 | measurement | 2.16 | sensitive (2–3×) | 2.80 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | FB | +3.3 | +0.1 | 0.43 | 1.13 | 4.77 | [-5.8, +13.2] | 4.77 | measurement | 0.70 | not separable (< 2×) | 2.96 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | FB | +8.4 | +14.6 | 0.43 | 3.23 | 4.76 | [-0.8, +18.7] | 4.76 | measurement | 1.76 | not separable (< 2×) | 2.60 |

Left/right (LR = mean(S2, S3) − mean(S5, S6); all designs are mirror-symmetric, true LR = 0):

| variant | method | comparison | contrast | clean | truth | yardstick | floor | gain_sd | gain_95 | ruler | dominant | ratio | verdict | clean_ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all 21 paths | tikhonov dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.52 | 1.20 | 32.40 | [-56.1, +77.8] | 32.40 | measurement | 0.01 | not separable (< 2×) | 0.29 |
| all 21 paths | tikhonov dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.52 | 4.21 | 31.98 | [-62.5, +66.2] | 31.98 | measurement | 0.11 | not separable (< 2×) | 0.84 |
| all 21 paths | tikhonov dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.52 | 1.51 | 29.81 | [-44.3, +69.4] | 29.81 | measurement | 0.01 | not separable (< 2×) | 0.28 |
| all 21 paths | tikhonov dS | Moderate − Mild | LR | -3.9 | +0.0 | 0.52 | 4.05 | 27.75 | [-54.9, +47.8] | 27.75 | measurement | 0.14 | not separable (< 2×) | 0.96 |
| all 21 paths | bounded dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.52 | 0.53 | 24.22 | [-43.9, +57.2] | 24.22 | measurement | 0.01 | not separable (< 2×) | 0.65 |
| all 21 paths | bounded dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.52 | 1.79 | 24.34 | [-47.2, +45.3] | 24.34 | measurement | 0.15 | not separable (< 2×) | 1.97 |
| all 21 paths | bounded dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.52 | 0.65 | 22.42 | [-34.6, +50.7] | 22.42 | measurement | 0.02 | not separable (< 2×) | 0.65 |
| all 21 paths | bounded dS | Moderate − Mild | LR | -0.9 | +0.0 | 0.52 | 1.73 | 13.25 | [-29.0, +24.5] | 13.25 | measurement | 0.07 | not separable (< 2×) | 0.54 |
| all 21 paths | tikhonov log (gain-inv.) | Mild − Healthy | LR | -0.3 | -0.0 | 0.68 | 1.17 | 11.81 | [-21.5, +25.1] | 11.81 | measurement | 0.02 | not separable (< 2×) | 0.24 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.68 | 3.76 | 12.16 | [-26.2, +23.9] | 12.16 | measurement | 0.29 | not separable (< 2×) | 0.95 |
| all 21 paths | tikhonov log (gain-inv.) | Severe − Healthy | LR | -0.5 | -0.0 | 0.68 | 1.28 | 12.55 | [-21.7, +25.7] | 12.55 | measurement | 0.04 | not separable (< 2×) | 0.41 |
| all 21 paths | tikhonov log (gain-inv.) | Moderate − Mild | LR | -3.8 | +0.0 | 0.68 | 3.60 | 12.10 | [-28.7, +17.5] | 12.10 | measurement | 0.31 | not separable (< 2×) | 1.05 |
| all 21 paths | bounded log (gain-inv.) | Mild − Healthy | LR | -0.3 | -0.0 | 0.48 | 0.51 | 11.07 | [-21.2, +22.0] | 11.07 | measurement | 0.03 | not separable (< 2×) | 0.55 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.48 | 1.55 | 11.43 | [-22.2, +21.8] | 11.43 | measurement | 0.31 | not separable (< 2×) | 2.29 |
| all 21 paths | bounded log (gain-inv.) | Severe − Healthy | LR | -0.5 | -0.0 | 0.48 | 0.53 | 12.27 | [-21.5, +24.7] | 12.27 | measurement | 0.04 | not separable (< 2×) | 0.99 |
| all 21 paths | bounded log (gain-inv.) | Moderate − Mild | LR | -1.8 | +0.0 | 0.48 | 1.51 | 6.61 | [-16.3, +9.7] | 6.61 | measurement | 0.28 | not separable (< 2×) | 1.22 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | LR | +0.0 | -0.0 | 0.19 | 0.86 | 2.62 | [-4.4, +5.1] | 2.62 | measurement | 0.02 | not separable (< 2×) | 0.06 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | LR | -3.0 | -0.0 | 0.19 | 3.14 | 2.52 | [-7.7, +2.2] | 3.14 | symmetry | 0.95 | not separable (< 2×) | 0.95 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | LR | -0.5 | -0.0 | 0.19 | 0.96 | 2.70 | [-5.2, +4.8] | 2.70 | measurement | 0.18 | not separable (< 2×) | 0.50 |
| all 21 paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | LR | -3.6 | +0.0 | 0.19 | 3.03 | 2.54 | [-8.7, +0.7] | 3.03 | symmetry | 1.18 | not separable (< 2×) | 1.18 |
| without opposite paths | tikhonov dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.65 | 1.20 | 32.45 | [-55.7, +77.2] | 32.45 | measurement | 0.01 | not separable (< 2×) | 0.25 |
| without opposite paths | tikhonov dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.65 | 4.21 | 31.98 | [-61.6, +66.7] | 31.98 | measurement | 0.11 | not separable (< 2×) | 0.84 |
| without opposite paths | tikhonov dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.65 | 1.51 | 29.80 | [-45.0, +70.3] | 29.80 | measurement | 0.01 | not separable (< 2×) | 0.27 |
| without opposite paths | tikhonov dS | Moderate − Mild | LR | -3.9 | +0.0 | 0.65 | 4.06 | 27.82 | [-54.5, +48.1] | 27.82 | measurement | 0.14 | not separable (< 2×) | 0.95 |
| without opposite paths | bounded dS | Mild − Healthy | LR | +0.3 | -0.0 | 0.65 | 0.59 | 25.35 | [-45.2, +60.4] | 25.35 | measurement | 0.01 | not separable (< 2×) | 0.46 |
| without opposite paths | bounded dS | Moderate − Healthy | LR | -3.5 | -0.0 | 0.65 | 2.00 | 25.28 | [-50.1, +48.9] | 25.28 | measurement | 0.14 | not separable (< 2×) | 1.77 |
| without opposite paths | bounded dS | Severe − Healthy | LR | -0.4 | -0.0 | 0.65 | 0.73 | 23.36 | [-36.1, +50.9] | 23.36 | measurement | 0.02 | not separable (< 2×) | 0.56 |
| without opposite paths | bounded dS | Moderate − Mild | LR | -1.1 | +0.0 | 0.65 | 1.94 | 14.52 | [-30.3, +26.6] | 14.52 | measurement | 0.08 | not separable (< 2×) | 0.58 |
| without opposite paths | tikhonov log (gain-inv.) | Mild − Healthy | LR | -0.4 | -0.0 | 0.80 | 1.17 | 11.83 | [-21.4, +24.5] | 11.83 | measurement | 0.03 | not separable (< 2×) | 0.33 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.80 | 3.77 | 12.15 | [-26.6, +23.7] | 12.15 | measurement | 0.30 | not separable (< 2×) | 0.96 |
| without opposite paths | tikhonov log (gain-inv.) | Severe − Healthy | LR | -0.8 | -0.0 | 0.80 | 1.28 | 12.57 | [-22.5, +25.1] | 12.57 | measurement | 0.06 | not separable (< 2×) | 0.62 |
| without opposite paths | tikhonov log (gain-inv.) | Moderate − Mild | LR | -3.7 | +0.0 | 0.80 | 3.61 | 12.09 | [-28.6, +18.0] | 12.09 | measurement | 0.31 | not separable (< 2×) | 1.04 |
| without opposite paths | bounded log (gain-inv.) | Mild − Healthy | LR | -0.4 | -0.0 | 0.61 | 0.60 | 11.04 | [-21.3, +23.3] | 11.04 | measurement | 0.04 | not separable (< 2×) | 0.64 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Healthy | LR | -3.6 | -0.0 | 0.61 | 1.85 | 11.39 | [-24.2, +21.8] | 11.39 | measurement | 0.32 | not separable (< 2×) | 1.95 |
| without opposite paths | bounded log (gain-inv.) | Severe − Healthy | LR | -0.8 | -0.0 | 0.61 | 0.66 | 12.37 | [-22.1, +24.8] | 12.37 | measurement | 0.06 | not separable (< 2×) | 1.20 |
| without opposite paths | bounded log (gain-inv.) | Moderate − Mild | LR | -2.3 | +0.0 | 0.61 | 1.78 | 7.89 | [-19.0, +12.3] | 7.89 | measurement | 0.29 | not separable (< 2×) | 1.30 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Mild − Healthy | LR | +0.0 | -0.0 | 0.30 | 0.86 | 2.61 | [-4.3, +5.0] | 2.61 | measurement | 0.01 | not separable (< 2×) | 0.02 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Healthy | LR | -2.9 | -0.0 | 0.30 | 3.15 | 2.53 | [-7.7, +2.1] | 3.15 | symmetry | 0.93 | not separable (< 2×) | 0.93 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Severe − Healthy | LR | -0.5 | -0.0 | 0.30 | 0.97 | 2.69 | [-5.3, +5.0] | 2.69 | measurement | 0.19 | not separable (< 2×) | 0.52 |
| without opposite paths | tikhonov log, whitened projection (post-hoc) | Moderate − Mild | LR | -3.5 | +0.0 | 0.30 | 3.04 | 2.55 | [-8.7, +0.7] | 3.04 | symmetry | 1.16 | not separable (< 2×) | 1.16 |

### Reading

- **Moderate − Healthy, FB, Tikhonov dS:** clean +10.2 (truth +14.6). ±0.5 dB: ruler 34.7 (measurement), 0.3× → not separable (< 2×); ±2 dB/±10°: ruler 41.4 (measurement), 0.2× → not separable (< 2×). Without opposite paths: 0.3× / 0.2×. Clean ruler (mesh, symmetry only): 2.2× (sensitive (2–3×)); without opposite paths 2.2×.
- **Moderate − Mild, FB, Tikhonov dS:** clean +6.2 (truth +14.6). ±0.5 dB: ruler 32.6 (measurement), 0.2× → not separable (< 2×); ±2 dB/±10°: ruler 41.2 (measurement), 0.2× → not separable (< 2×). Without opposite paths: 0.2× / 0.1×. Clean ruler (mesh, symmetry only): 1.4× (not separable (< 2×)); without opposite paths 1.4×.
- **Moderate − Healthy, FB, frozen log:** clean +10.4 (truth +14.6). ±0.5 dB: ruler 14.1 (measurement), 0.7× → not separable (< 2×); ±2 dB/±10°: ruler 16.3 (measurement), 0.6× → not separable (< 2×). Without opposite paths: 0.7× / 0.6×. Clean ruler (mesh, symmetry only): 2.6× (sensitive (2–3×)); without opposite paths 2.4×.
- **Moderate − Mild, FB, frozen log:** clean +6.4 (truth +14.6). ±0.5 dB: ruler 15.6 (measurement), 0.4× → not separable (< 2×); ±2 dB/±10°: ruler 17.7 (measurement), 0.4× → not separable (< 2×). Without opposite paths: 0.4× / 0.4×. Clean ruler (mesh, symmetry only): 1.7× (not separable (< 2×)); without opposite paths 1.7×.
- **Moderate − Healthy, FB, whitened log:** clean +10.3 (truth +14.6). ±0.5 dB: ruler 4.2 (measurement), 2.5× → sensitive (2–3×); ±2 dB/±10°: ruler 4.3 (measurement), 2.4× → sensitive (2–3×). Without opposite paths: 2.3× / 2.2×. Clean ruler (mesh, symmetry only): 3.1× (exceeds (≥ 3×)); without opposite paths 2.8×.
- **Moderate − Mild, FB, whitened log:** clean +8.5 (truth +14.6). ±0.5 dB: ruler 4.7 (measurement), 1.8× → not separable (< 2×); ±2 dB/±10°: ruler 4.7 (measurement), 1.8× → not separable (< 2×). Without opposite paths: 1.8× / 1.8×. Clean ruler (mesh, symmetry only): 2.6× (sensitive (2–3×)); without opposite paths 2.6×.
- **The front-positive bias** (Mild, Severe: true FB ≈ 0). Clean FB: Tikhonov dS Mild +3.9, Tikhonov dS Severe +3.8, frozen log Mild +3.9, frozen log Severe +4.1, whitened log Mild +2.3, whitened log Severe +4.9. Ratio to the full ruler (±0.5 dB / ±2 dB): Tikhonov dS Mild 0.1× / 0.1×; Tikhonov dS Severe 0.1× / 0.1×; frozen log Mild 0.3× / 0.3×; frozen log Severe 0.3× / 0.3×; whitened log Mild 0.6× / 0.5×; whitened log Severe 1.1× / 1.0×. Ratio to the clean ruler (mesh, symmetry): Tikhonov dS Mild 3.0×; Tikhonov dS Severe 2.3×; frozen log Mild 3.1×; frozen log Severe 2.8×; whitened log Mild 2.4×; whitened log Severe 4.3×. Against the clean ruler the bias is about as large, relative to error, as Moderate's FB itself; Moderate − Healthy FB contains it, and Moderate − Mild (which removes most of it) is the smaller contrast.
- **Left/right on the mirror-symmetric designs** (true LR = 0): |LR| / full ruler ≤ 1.2×; |LR| / clean ruler ≤ 2.3× (worst: frozen bounded log, Moderate − Healthy, all 21 paths, LR -3.6). Exactly mirror-symmetrised data give |LR| ≤ 1.3 (kernel mirror asymmetry of the HFSS field exports); the rest of the symmetric designs' LR is their own numerical mirror residual, i.e. the symmetry floor in its actual orientation.
- **LeftOnly prediction vs the LR rulers (Tikhonov dS):** predicted LR +14.7 (Born-simulated) against the Mild − Healthy LR ruler 26.5 (±0.5 dB) / 32.4 (±2 dB/±10°) → 0.6× / 0.5×; clean ruler 1.2 → 12.2×.
- **LeftOnly prediction vs the LR rulers (frozen log):** predicted LR +14.9 (Born-simulated) against the Mild − Healthy LR ruler 11.1 (±0.5 dB) / 11.8 (±2 dB/±10°) → 1.3× / 1.3×; clean ruler 1.2 → 12.7×.

## 6. Blind test (pre-registered, §4 of the brief)

Pipeline frozen in `results/imaging/lobe_frozen.json` and predictions written to `results/imaging/lobe_predictions.md` before LeftOnly_test or MCI_lobe were opened. Outcome: **pending** (the two designs are still solving). Run `python imaging/run_lobe.py --blind` when they arrive; this section will then be replaced by the scored outcome.

## 7. Verdict — can this 6-antenna ring localise lobe-level AD?

Within these simulations (one head, one solve per design, typical noise, Born kernels on the v2 Normal fields):

- **Which lobes (pattern):** yes, as a ranking. On the mesh-matched set lobe_A (§5c) the recovered sector conductivity correlates 0.89–0.96 with the truth for Mild and Moderate (all four methods, with and without the opposite paths) and the affected lobes are the most changed. Absolute 'affected' calls depend on a threshold calibrated on Mild and are fragile: a one-pass change of the reference mesh shifts every sector by about 2–3, enough to move sectors near T_abs = 13.8 across it (primary, all paths: 5/6, 5/6, 6/6 correct for Mild/Moderate/Severe; without opposite paths: 6/6, 6/6, 6/6). Healthy lobes are biased upward by about 5–10, more than a one-pass mesh change; Born model error and leakage are the likely cause.
- **Front/back: not established.** Moderate − Healthy FB on lobe_A = +10.2 (primary; truth +14.6). Against the simulation-level ruler max(one-pass mesh, symmetry floor): Tikhonov dS 2.2×, frozen log 2.6×, whitened log 3.1× (≥ 3× exceeds, 2–3× sensitive). With the Prompt 07 measurement errors: Tikhonov dS 0.3×, frozen log 0.7×, whitened log 2.5× (±0.5 dB) and Tikhonov dS 0.2×, frozen log 0.6×, whitened log 2.4× (±2 dB/±10°). Mild and Severe carry a front-positive bias of about +4 that is itself 2.3–4.3× the clean ruler, and Moderate − Mild (not a pure frontal contrast) is Tikhonov dS 1.4×, frozen log 1.7×, whitened log 2.6× the clean ruler. This agrees with the main session: localisation is not separable from error once symmetry floor and gain/phase errors are included (§5d).
- **Left/right:** not testable on the available designs (all mirror-symmetric). The frozen pipeline predicts LR = +14.7 ± 2.2 for LeftOnly_test (left in 100% of noisy draws); the blind test decides. Rulers (§5d): the predicted LeftOnly contrast is 12× the clean LR ruler, so the clean simulation can test left/right; with the Prompt 07 measurement errors it would be only 0.6× (Tikhonov dS) / 1.3× (frozen log) the ruler at ±0.5 dB: not separable in a measurement with the frozen pipeline. The mirror-symmetric designs themselves (true LR = 0) reach up to 2.3× the clean LR ruler, so that ruler underestimates left/right error by up to that factor; the LeftOnly margin would survive it.
- **Depth:** no, beyond the outermost cortex. The under-skull gap (76–83.5 mm) is determined where it changes; the deeper cortex (60–76 mm) has a 2–3× larger CRLB and is not determined in any sector at any stage (§2); the core (hippocampus) is not determined at all.
- **Radar imaging:** no — it still peaks at the centre and its energy direction does not track the lobes.
- **Opposite paths:** they carry 9%–14% of the information per sector; removing them shifts sector values by +0.5 to +5.5 and flips only near-threshold calls. No conclusion depends on them (both versions in §5c).
- **Caveats:** the Born model explains only about a quarter to a third of the dS size (κ ≈ 3 absorbs it) and the background fields come from the unsliced design; the lobe placement is schematic (azimuthal wedges at the ring height); everything is within one simulated head; lobe_A matches the stop rule, not the pass count (reference 6 passes, stages 5), and the yardstick is a single extra pass, so mesh error relative to a converged solution is not bounded by it (§5c). **Erratum (§5d):** the frozen 'gain-invariant' log method projects out the port gains before noise whitening, so it is not gain-invariant (the Prompt 07 per-port amplitude/phase perturbation alone moves its FB by SD 12); a post-hoc whitened projection is exactly gain-invariant (SD 0.00) and is limited by the measurement noise instead.

