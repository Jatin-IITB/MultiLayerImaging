# Track A — imaging / localisation study (`imaging/`, code b051f2b, 2026-09-29)

Regenerate: `python imaging/run_imaging.py` (tests: `python -m pytest imaging/tests -q`).
Everything here comes from **one HFSS simulation per stage**: it shows what is recoverable from these simulations under the stated noise, **not** generalisation to new heads. Between-mesh noise is unmeasured, so every AD-vs-AD statement is **unverified against mesh noise**.
**Tuning protocol:** every free choice (antenna delay, effective permittivity, regularisation weights, calibration scale kappa(f), thresholds) is set on **Mild**; results are reported on **Moderate and Severe**. Noise floor = 'typical' profile (0.25 dB, 2 deg, -70 dB floor) on both the stage and the Normal measurement.

## 0. Data, assumptions, blocked items

- Files: Normal: `brain_sevem_layer_Healthy.s6p`, Mild: `Brain_sevem_layer_MildAD.s6p`, Moderate: `Brain_sevem_layer_ModerateAD.s6p`, Severe: `brain_sevem_layer_SevereAD.s6p`. Common grid 3.2-4.2 GHz, 201 points, glitch masking ON (shared loader).
- Assumption: Skin/fat/skull materials are not in MODEL_CARD.md (OPEN-GUI): assumed skin 37/2.0, fat 10.5/0.42, skull 10.8/0.61 (eps_r / S/m).
- Assumption: Ring z-sign and antenna orientation are OPEN in MODEL_CARD.md: ring assumed at +z (polar angle 60.5 deg), broadside facing the origin; S is mirror-symmetric in z so the sign does not affect S, only image coordinates.
- Assumption: Antenna = point electric dipole at the feed point, tangential to the sphere; the polarisation (theta^ vs phi^) is chosen by the fit to the HFSS Normal ring couplings.
- Assumption: Normal-stage materials are back-calculated values (MODEL_CARD caveat).
- Assumption: The HFSS materials are static (no dispersion); the model uses the same constant eps_r, sigma.
- The brief names `reference/dbim_reference.m`; the repository holds `references/imaging_code.m` (a 2-D incident/total-field script). Not used beyond inspiration.
- **`data/fields/` HFSS field exports: ABSENT.** Blocked: I2 with the numerical (HFSS) Green's function, i.e. HFSS sensitivity maps, HFSS-field Jacobians and their inversions. The field reader (`imaging/fields.py`, header-driven column order) is implemented and unit-tested on a synthetic file. Everything in I2 below uses the **forward-model fields as a SURROGATE** Green's function, labelled as such.

## 1. The k = 3 path question — direct evidence from the HFSS couplings

Group delay = slope of the unwrapped phase over 3.2–4.2 GHz. The unknown antenna/feed delay is removed with the neighbour path (k = 1). Its straight line only grazes the skin (closest approach 87.8 mm), so it travels in air: 2 t_ant = gd(k1) − chord/c = **3.05 ns**.

| k | sep_deg | chord_mm | chord_closest_to_centre_mm | creep_len_mm | pred_straight_ns | pred_creep_ns | measured_gd_Normal_ns |
|---|---|---|---|---|---|---|---|
| 1 | 51.59 | 84.90 | 87.83 | 84.90 | 3.52 | 3.34 | 3.34 |
| 2 | 97.83 | 147.06 | 64.11 | 155.92 | 5.51 | 3.57 | 4.87 |
| 3 | 121.00 | 169.81 | 48.04 | 191.51 | 6.03 | 3.69 | 3.61 |

| stage | gd_k0_ns | gd_k1_ns | gd_k2_ns | gd_k3_ns | gd_dS_k0_ns | gd_dS_k1_ns | gd_dS_k2_ns | gd_dS_k3_ns |
|---|---|---|---|---|---|---|---|---|
| Normal | 1.20 | 3.34 | 4.87 | 3.61 |  |  |  |  |
| Mild | 1.21 | 3.32 | 4.91 | 3.64 | 0.51 | 3.45 | 4.24 | 3.28 |
| Moderate | 1.21 | 3.33 | 4.93 | 3.65 | 0.53 | 3.55 | 4.35 | 3.25 |
| Severe | 1.21 | 3.34 | 4.96 | 3.70 | 0.52 | 3.44 | 4.16 | 3.07 |

**Verdict (k = 3).** Measured group delay 3.61 ns. The air/creeping path predicts 3.69 ns (Δ = 0.08 ns). The straight path through the head predicts 6.03 ns (Δ = 2.4 ns). The same holds for Mild/Moderate/Severe (table). So the opposite-antenna signal **travels around the head** (air side of the skin: creeping, or guided along the nearly closed ring of AMC reflectors), not through the brain. dS_k3 has about the same delay as the k3 wave itself. So the stage information on k = 3 is a modification of that surface-guided wave by the near-surface layers (CSF/cortex below the skull), not an echo from depth. Figure: `figures/k3_path_time.png`.
- Caveats: (i) with a resonant patch/AMC antenna the group delay is frequency-dependent. The single slope is a band average, uncertain by a few tenths of a ns. The 2.4 ns margin is well outside that. (ii) k = 2 does not fit either prediction cleanly (4.87 ns): its coupling has deep nulls near 3.8 GHz (two unequal paths around the ring interfere), so its slope is unreliable.

## 2. I1 — radar beamforming of dS (DAS, DMAS, MVDR)

- Signals: the 21 reciprocal pairs, each whitened by its noise std (else S_ii, 40–60 dB above the transmissions, is the whole image). Hann window, zero-padded IFFT (8192), -6 dB pulse width 1.98 ns; DAS/DMAS energy over a 0.49 ns window at the focal delay.
- Delays: (a) one effective eps inside the skin; (b) straight rays through the Normal layers. Pair delay tau_i + tau_j + 2 t_ant.
- MVDR: see `imaging/beamform.py`. With **one** measurement per pair, the 21×21 covariance of a single snapshot is rank 1 and not invertible. The F = 201 focused frequency bins are used as snapshots (rank ≤ 21, assumes a frequency-flat focused response), with diagonal loading 0.1·tr(R)/21. With loading → ∞ it reduces to DAS.
- Tuned on Mild: t_ant ∈ {0, 0.5, 1, 1.5, 2} ns and eps_eff ∈ {20, 30, 40, 50}, chosen by the largest signal-to-clutter ratio (SCR = Mild image peak / mean noise-only peak). SCR does not use the true change location.

| setting | eps_eff | t_ant_ns | scr_db | peak_r_mm |
|---|---|---|---|---|
| eff|DAS | 20 | 1.5 | 23.8 | 1 |
| eff|DMAS | 20 | 1.5 | 24.2 | 1 |
| eff|MVDR | 20 | 0 | 4.0 | 15 |
| layered|DAS | None | 0 | 23.8 | 1 |
| layered|DMAS | None | 1 | 23.5 | 1 |
| layered|MVDR | None | 1.5 | 2.2 | 9 |

**Point-target test (ideal flat-spectrum scatterer, homogeneous eps = 40, ring plane).** This is the array's intrinsic resolution: −3 dB widths along x (radial), y (azimuthal) and z (elevation), and the peak offset.

| r_mm | method | x_peak_offset_mm | x_width_3dB_mm | y_peak_offset_mm | y_width_3dB_mm | z_peak_offset_mm | z_width_3dB_mm |
|---|---|---|---|---|---|---|---|
| 10 | DAS | 0 | 28 | 0 | 30 | 0 | 82 |
| 10 | DMAS | 0 | 28 | 0 | 2 | 0 | 66 |
| 10 | MVDR | 0 | 2 | 0 | 2 | 0 | 26 |
| 30 | DAS | 0 | 2 | 0 | 2 | 0 | 56 |
| 30 | DMAS | 0 | 2 | 0 | 2 | 0 | 50 |
| 30 | MVDR | 0 | 2 | 0 | 2 | 0 | 6 |
| 50 | DAS | 0 | 2 | 0 | 2 | 0 | 32 |
| 50 | DMAS | 0 | 2 | 0 | 2 | 0 | 16 |
| 50 | MVDR | 0 | 2 | 0 | 2 | 0 | 2 |
| 65 | DAS | 0 | 2 | 0 | 2 | 0 | 16 |
| 65 | DMAS | 0 | 2 | 0 | 2 | 0 | 10 |
| 65 | MVDR | 0 | 2 | 0 | 2 | 0 | 2 |

An ideal point scatterer is focused at the right place in-plane by all three methods; widths of 2 mm are the grid-sampling limit. This test is noise-free, so the MVDR widths are optimistic. Elevation is the weak axis (DAS/DMAS 16–82 mm), as expected for one ring. So the failure on the real dS below is not a beamformer bug. A spherically symmetric change gives the same signal on every pair at a given k, and those add coherently at the equidistant centre. The echo delays also contain the unknown antenna response.

**Results.** The true change of every AD stage is a set of shells: the outermost starts at the brain surface (83 mm, gray → CSF; 83–83.5 mm CSF material). The changed band spans 57–83.5 mm (Severe), plus the hippocampus. peak_r = radius of the maximum of the azimuthally averaged profile. SCR = clean stage image peak / mean noise-only peak. scr_noisy = the same with noise on both measurements.

| delays | method | stage | peak_r_mm | scr_db | scr_noisy_db | frac_draws_above_noise_p95 |
|---|---|---|---|---|---|---|
| eff | DAS | Mild | 1 | 23.7 | 23.7 | 1.00 |
| eff | DAS | Moderate | 1 | 22.2 | 22.2 | 1.00 |
| eff | DAS | Severe | 1 | 25.3 | 25.3 | 1.00 |
| eff | DMAS | Mild | 1 | 23.9 | 23.9 | 1.00 |
| eff | DMAS | Moderate | 1 | 19.4 | 19.5 | 1.00 |
| eff | DMAS | Severe | 1 | 28.7 | 28.6 | 1.00 |
| eff | MVDR | Mild | 15 | 4.3 | 8.0 | 1.00 |
| eff | MVDR | Moderate | 15 | 3.7 | 7.7 | 1.00 |
| eff | MVDR | Severe | 1 | 7.4 | 8.7 | 1.00 |
| layered | DAS | Mild | 1 | 23.8 | 23.9 | 1.00 |
| layered | DAS | Moderate | 11 | 22.5 | 22.5 | 1.00 |
| layered | DAS | Severe | 1 | 25.3 | 25.2 | 1.00 |
| layered | DMAS | Mild | 1 | 23.1 | 23.3 | 1.00 |
| layered | DMAS | Moderate | 1 | 19.9 | 19.8 | 1.00 |
| layered | DMAS | Severe | 1 | 28.5 | 28.4 | 1.00 |
| layered | MVDR | Mild | 9 | 2.5 | 5.2 | 1.00 |
| layered | MVDR | Moderate | 1 | 2.3 | 5.2 | 1.00 |
| layered | MVDR | Severe | 1 | 0.5 | 4.4 | 1.00 |

Peak radius vs assumed antenna delay (DAS, layered rays). The depth the image assigns is set by t_ant, which the data cannot fix (§1: transmission carries ~3 ns of antenna delay that reflection does not show):

| t_ant_ns | Mild | Moderate | Severe |
|---|---|---|---|
| 0.00 | 1 | 11 | 1 |
| 0.25 | 1 | 5 | 1 |
| 0.50 | 1 | 5 | 1 |
| 0.75 | 1 | 5 | 1 |
| 1.00 | 1 | 1 | 1 |
| 1.25 | 1 | 1 | 1 |
| 1.50 | 1 | 1 | 1 |
| 1.75 | 1 | 3 | 1 |
| 2.00 | 1 | 5 | 1 |
| 2.25 | 87 | 5 | 1 |
| 2.50 | 87 | 5 | 5 |
| 2.75 | 87 | 5 | 5 |
| 3.00 | 43 | 5 | 5 |

Figures: `figures/i1_ring_plane.png`, `figures/i1_vertical_plane.png`, `figures/i1_radial_profiles.png`.

## 3. Forward model (a): layered-sphere Mie solution + point dipoles — validation

Exact vector-spherical-wave solution for the 7-layer sphere. Each antenna is a tangential electric point dipole at its feed (97.55 mm, polar 60.5°). The dyadic Green's function expansion, the Mie coefficients, field continuity, reciprocity and Born-vs-exact are unit-tested: free-space limit 1e-10, Mie vs direct 1e-12, reciprocity 1e-15, Born = exact thin-shell derivative to 3e-5.

- Polarisation chosen on **Normal only**: misfit of one common complex antenna factor a²(f) to the HFSS k = 1..3 couplings — theta 0.71, phi 0.63 → **phi**.
- Convergence in the number of harmonics (relative change of dV_Mild vs n = 150):

| nmax | k0 | k1 | k2 | k3 |
|---|---|---|---|---|
| 30 | 1.5e-04 | 6.8e-04 | 1.8e-03 | 3.1e-03 |
| 50 | 9.1e-07 | 1.5e-06 | 2.8e-06 | 1.5e-07 |
| 70 | 1.4e-09 | 3.7e-11 | 3.3e-09 | 5.8e-10 |
| 90 | 3.1e-12 | 3.9e-12 | 4.0e-12 | 3.4e-13 |
| 110 | 7.5e-15 | 1.3e-14 | 3.2e-14 | 2.7e-14 |
| 130 | 9.6e-16 | 2.4e-15 | 1.7e-14 | 2.4e-14 |

- dS prediction. calA = the brief's per-ring-distance correction c_k(f) = S_k/V_k fitted on the Normal total coupling (c_0 := c_1). calB = one complex a²(f) per frequency, fitted to dS_Mild over all k (tuned on Mild). trivial = predicting dS_stage by dS_Mild. rel_err = |pred − HFSS| / |HFSS|, so 1.0 is as bad as predicting zero. shape_corr = |<pred, HFSS>| over frequency. growth = |dS_stage| / |dS_Mild|.

| stage | k | calA_rel_err | calB_rel_err | shape_corr | trivial_rel_err | model_growth_vs_mild | hfss_growth_vs_mild |
|---|---|---|---|---|---|---|---|
| Mild | 0 | 3.04 | 0.67 | 0.14 | n/a | 1.00 | 1.00 |
| Mild | 1 | 0.85 | 0.88 | 0.89 | n/a | 1.00 | 1.00 |
| Mild | 2 | 1.36 | 0.98 | 0.34 | n/a | 1.00 | 1.00 |
| Mild | 3 | 1.63 | 1.04 | 0.86 | n/a | 1.00 | 1.00 |
| Moderate | 0 | 3.48 | 0.79 | 0.08 | 0.26 | 1.21 | 1.04 |
| Moderate | 1 | 2.02 | 0.91 | 0.67 | 0.61 | 1.25 | 0.72 |
| Moderate | 2 | 1.65 | 1.08 | 0.43 | 0.48 | 1.23 | 0.99 |
| Moderate | 3 | 1.62 | 1.05 | 0.83 | 0.17 | 1.21 | 1.09 |
| Severe | 0 | 4.38 | 0.80 | 0.10 | 0.37 | 1.99 | 1.33 |
| Severe | 1 | 1.64 | 0.87 | 0.90 | 0.29 | 2.20 | 1.29 |
| Severe | 2 | 1.82 | 1.12 | 0.48 | 0.38 | 2.12 | 1.41 |
| Severe | 3 | 1.80 | 1.08 | 0.78 | 0.44 | 1.97 | 1.43 |

**Verdict: the validation FAILS beyond the neighbour path.** Findings:

- With the brief's Normal calibration, the model predicts Mild dS only on k = 1 (shape correlation ≈ 0.9). k = 0 and k = 2 are wrong in shape (corr 0.1–0.5), and k = 3 is off in amplitude.
- The model's k = 3 total coupling is a deep shadow (−83…−99 dB). HFSS has −55 dB. HFSS carries an opposite-antenna path the point-dipole model lacks, consistent with §1 (around-the-head air path; the six AMC reflectors nearly close a ring).
- The model predicts Severe dS ≈ 2× Mild on every path. HFSS shows ≈ 1.3–1.4×. Even the most flexible calibration fitted on Mild does not beat the trivial predictor on Moderate/Severe.
- A patch-sized aperture (5×5 dipoles, cos taper) and phase-centre radii 92–105 mm were also tried. None fixes this (rel. err ≈ 0.8–1.2). The mismatch is in the antenna/array structure, not the head model.
- Consequence: every inversion that needs a forward model (I2 with surrogate fields, I3) is reported twice: on HFSS data (model-mismatch limited) and on model-generated synthetic data with the same noise (the array's intrinsic capability if the antenna were modelled correctly).

## 4. I2 — sensitivity maps and linearised inversion

**Field source: SURROGATE (forward-model fields; data/fields absent).** J_ij(r) = −j k0³ E_i·E_j (no conjugate, e^{+jωt}). With HFSS exports this becomes −(jωε0/4a_ia_j)E_i·E_j; a complex scale kappa(f) per frequency is calibrated on Mild in both cases.

### 4.1 Where can this array see?

Shell-averaged sensitivity (sum over pairs at distance k and 3.4/3.6/3.8 GHz). r_peak = radius of maximum sensitivity; r_XdB = the largest radius below r_peak where it is X dB under that maximum.

| k | r_peak | r_10dB | r_20dB | r_40dB |
|---|---|---|---|---|
| k0 | 87 | 67 | 33 | n/a |
| k1 | 87 | 67 | n/a | n/a |
| k2 | 87 | 65 | n/a | n/a |
| k3 | 87 | 65 | n/a | n/a |

**Detectability (absolute).** A relative profile only shows shape. What matters is the SNR a localised change would produce. Here: a 1 cm³ blob with |d eps| = 10 (about the gray→CSF contrast) at radius r, on the Normal background, typical noise on both measurements, scale kappa(f) from Mild, 3 frequencies. r_min_snrX = the smallest radius down to which SNR ≥ X holds continuously from the surface. Figure: `figures/i2_detectability_radial.png`.

| path | over | snr_at_83 | snr_at_70 | snr_at_50 | snr_at_20 | r_min_snr1 | r_min_snr3 |
|---|---|---|---|---|---|---|---|
| k=0 | median dir. | 0.0029 | 0.0012 | 0.00048 | 0.00095 | n/a | n/a |
| k=0 | best dir. | 3.3 | 0.68 | 0.061 | 0.0015 | 75 | 83 |
| k=1 | median dir. | 0.025 | 0.01 | 0.0032 | 0.01 | n/a | n/a |
| k=1 | best dir. | 1 | 0.27 | 0.064 | 0.015 | 83 | 87 |
| k=2 | median dir. | 0.016 | 0.0063 | 0.0025 | 0.0079 | n/a | n/a |
| k=2 | best dir. | 0.4 | 0.11 | 0.022 | 0.026 | 87 | n/a |
| k=3 | median dir. | 0.0027 | 0.0011 | 0.00061 | 0.0072 | n/a | n/a |
| k=3 | best dir. | 0.093 | 0.031 | 0.01 | 0.033 | n/a | n/a |
| all 21 pairs | median dir. | 0.04 | 0.016 | 0.0062 | 0.015 | n/a | n/a |
| all 21 pairs | best dir. | 3.5 | 0.74 | 0.075 | 0.043 | 73 | 83 |

Relative (shape) profile: k = 3 is the flattest in depth, because both opposite fields are weak everywhere. In absolute terms every path has the same tiny sensitivity at the centre (all six fields are equal there). k = 3 simply has far less surface sensitivity and far lower noise than k = 0.

Volume-weighted fraction of the sensitivity inside r < 60 mm: k0 4.0e-02, k1 6.2e-02, k2 8.3e-02, k3 1.2e-01.

Block-the-core test (model): everything inside r_b is replaced by a strong absorber (eps 40, 40 S/m). Entries are the relative change of the TOTAL coupling of each path:

| r_block_mm | k0 | k1 | k2 | k3 |
|---|---|---|---|---|
| 20 | 7.6e-05 | 2.1e-03 | 4.3e-03 | 1.1e-02 |
| 40 | 1.7e-03 | 1.2e-02 | 2.0e-02 | 1.7e-02 |
| 55 | 1.2e-02 | 3.5e-02 | 6.1e-02 | 5.1e-02 |
| 65 | 4.4e-02 | 1.0e-01 | 1.4e-01 | 1.2e-01 |
| 75 | 1.6e-01 | 3.1e-01 | 3.7e-01 | 2.6e-01 |
| 80 | 2.6e-01 | 3.9e-01 | 4.0e-01 | 3.2e-01 |
| 82 | 4.3e-01 | 9.3e-01 | 1.1e+00 | 6.5e-01 |

- In the model, every path is dominated by the outer ~1 cm. Replacing everything inside r < 55 mm by an absorber changes the total couplings by only 1%–6%. The same test inside r < 75 mm changes them by 16%–37%. k = 3 is not special in depth once measured in absolute terms. Together with §1 (measured delay = air path), **k = 3 is a surface/air path, not a through-centre path**. Its stage sensitivity comes from the near-surface layers (CSF/cortex below the skull).
- Relative-profile table: n/a = the profile never falls that far below its own maximum (the product of two weak fields is weak everywhere); use the absolute detectability table instead.
- Figures: `figures/i2_sensitivity_maps.png` (ring + vertical planes, per k), `figures/i2_sensitivity_radial.png`.

### 4.2 Linearisation error

Model-internal: |Born(true d eps) − exact dV| / |exact dV|. HFSS: |kappa·Born(true d eps) − dS_HFSS| / |dS_HFSS|, with kappa(f) fitted on Mild.

| stage | model_k0 | model_k1 | model_k2 | model_k3 | hfss_k0 | hfss_k1 | hfss_k2 | hfss_k3 |
|---|---|---|---|---|---|---|---|---|
| Mild | 0.32 | 0.42 | 0.33 | 0.35 | 0.91 | 0.83 | 1.10 | 1.12 |
| Moderate | 0.31 | 0.34 | 0.30 | 0.33 | 0.93 | 0.79 | 1.15 | 1.09 |
| Severe | 0.47 | 0.49 | 0.38 | 0.32 | 0.89 | 0.83 | 1.20 | 1.13 |

- The Normal→AD change replaces 12–21 mm of gray/white matter by CSF (|d eps| up to 20). That is far outside the Born regime, so the linear model is not a quantitative description of any stage.

### 4.3 Radial (spherically symmetric) inversion — 2 mm shells, d eps_r and d eps''

Tikhonov with GCV and L-curve lambda, and 1-D TV (lambda tuned on Mild synthetic = 0.1). Errors are relative L2 against the true shell-averaged profile. corr = Pearson correlation with the truth.

| data | stage | method | rel_err_eps_r | rel_err_eps_pp | corr_eps_r | corr_eps_pp |
|---|---|---|---|---|---|---|
| synthetic-linear | Mild | tikhonov-gcv | 0.99 | 0.99 | 0.15 | 0.06 |
| synthetic-linear | Mild | tikhonov-lcurve | 0.99 | 0.99 | 0.15 | 0.06 |
| synthetic-linear | Mild | tv | 0.81 | 0.54 | 0.82 | 0.46 |
| synthetic-nonlinear | Mild | tikhonov-gcv | 1.07 | 1.00 | 0.01 | 0.00 |
| synthetic-nonlinear | Mild | tikhonov-lcurve | 0.99 | 0.99 | 0.15 | 0.04 |
| synthetic-nonlinear | Mild | tv | 0.93 | 0.61 | 0.54 | 0.24 |
| HFSS | Mild | tikhonov-gcv | 1986.97 | 1939.19 | -0.14 | -0.10 |
| HFSS | Mild | tikhonov-lcurve | 0.99 | 0.99 | 0.15 | 0.06 |
| HFSS | Mild | tv | 13.29 | 27.13 | 0.64 | 0.15 |
| synthetic-linear | Moderate | tikhonov-gcv | 0.99 | 0.99 | 0.10 | 0.08 |
| synthetic-linear | Moderate | tikhonov-lcurve | 0.99 | 0.99 | 0.11 | 0.08 |
| synthetic-linear | Moderate | tv | 0.90 | 0.52 | 0.25 | 0.47 |
| synthetic-nonlinear | Moderate | tikhonov-gcv | 1.13 | 0.99 | 0.02 | 0.08 |
| synthetic-nonlinear | Moderate | tikhonov-lcurve | 0.99 | 0.99 | 0.12 | 0.06 |
| synthetic-nonlinear | Moderate | tv | 0.92 | 0.53 | 0.30 | 0.28 |
| HFSS | Moderate | tikhonov-gcv | 1908.39 | 1602.60 | -0.10 | 0.08 |
| HFSS | Moderate | tikhonov-lcurve | 0.99 | 0.99 | 0.13 | 0.07 |
| HFSS | Moderate | tv | 13.73 | 19.88 | 0.63 | -0.34 |
| synthetic-linear | Severe | tikhonov-gcv | 0.94 | 0.94 | 0.02 | 0.05 |
| synthetic-linear | Severe | tikhonov-lcurve | 0.98 | 0.98 | 0.24 | 0.13 |
| synthetic-linear | Severe | tv | 0.67 | 0.60 | 0.44 | 0.44 |
| synthetic-nonlinear | Severe | tikhonov-gcv | 2.61 | 1.77 | -0.12 | 0.21 |
| synthetic-nonlinear | Severe | tikhonov-lcurve | 0.99 | 0.98 | 0.18 | 0.13 |
| synthetic-nonlinear | Severe | tv | 1.39 | 0.78 | 0.01 | 0.79 |
| HFSS | Severe | tikhonov-gcv | 2270.65 | 2096.02 | -0.03 | 0.06 |
| HFSS | Severe | tikhonov-lcurve | 0.99 | 0.99 | 0.22 | 0.11 |
| HFSS | Severe | tv | 57.37 | 21.02 | 0.52 | -0.46 |

Model-resolution matrix (whitened, GCV lambda on Mild): diag ≥ 0.5 for d eps_r at r ∈ 83–83 mm and for d eps'' at r ∈ 83–83 mm. Largest diag: 0.69 / 0.72. Number of singular values within 1e-3 of the largest: 20 of 84. Only the outermost shell (82–83.5 mm) is resolved; below it the radial inversion returns a smeared, strongly damped copy. 1-D TV (a piecewise-constant prior that matches the true layered profile) is the only method that recovers a correlated shape on synthetic data. Figure: `figures/i2_resolution.png`, `figures/i2_radial_inversion.png`.

### 4.4 Voxel inversion — 3 mm voxels in r < 83.5 mm

90447 voxels × (d eps_r, d eps''), 21 pairs × 6 frequencies (3.2–4.2 GHz). Tikhonov-GCV and L1 sparsity (FISTA, lambda tuned on Mild synthetic).

| data | stage | method | rel_err_eps_r | rel_err_eps_pp | corr_eps_r | corr_eps_pp |
|---|---|---|---|---|---|---|
| synthetic-linear | Mild | tikhonov-gcv | 1.00 | 1.00 | 0.08 | 0.02 |
| synthetic-linear | Mild | l1 | 1.00 | 1.00 | n/a | n/a |
| HFSS | Mild | tikhonov-gcv | 23.70 | 21.03 | 0.01 | 0.00 |
| HFSS | Mild | l1 | 1.00 | 1.00 | 0.00 | n/a |
| synthetic-linear | Moderate | tikhonov-gcv | 1.00 | 1.00 | 0.07 | 0.02 |
| synthetic-linear | Moderate | l1 | 1.00 | 1.00 | 0.01 | n/a |
| HFSS | Moderate | tikhonov-gcv | 1.00 | 1.00 | 0.04 | 0.01 |
| HFSS | Moderate | l1 | 1.00 | 1.00 | 0.01 | n/a |
| synthetic-linear | Severe | tikhonov-gcv | 0.99 | 1.00 | 0.12 | 0.04 |
| synthetic-linear | Severe | l1 | 1.00 | 1.00 | 0.01 | 0.00 |
| HFSS | Severe | tikhonov-gcv | 22.10 | 12.06 | 0.03 | -0.01 |
| HFSS | Severe | l1 | 1.00 | 1.00 | 0.02 | n/a |

- Tikhonov-GCV on the HFSS data (radial and voxel): the HFSS data are inconsistent with the surrogate Jacobian (§3, §4.2). GCV then picks a tiny lambda and the solution blows up (errors of 10–2000×). The L-curve lambda returns an almost-zero image instead. Neither is an image of the change.
- L1 (sparsity) with lambda tuned on Mild: the lambda with the lowest error on Mild gave the all-zero image. No sparse voxel pattern recovered the true change better than zero, so L1 reports nothing (rel. err 1.00, corr undefined).

Point-spread functions (columns of the resolution matrix, lambda = GCV on Mild synthetic) for voxels on the x-axis (z = 0, azimuth of T1) at radius r_mm. diag = the fraction of a unit change recovered in place. peak_at = where its image actually peaks:

| r_mm | diag | peak_at_mm | n_vox_above_half | extent_mm |
|---|---|---|---|---|
| 20 | 4.81e-06 | [66.0, 0.0, 51.0] | 39 | 8.28 |
| 40 | 1.92e-06 | [72.0, 0.0, 42.0] | 32 | 21.7 |
| 60 | 2.08e-06 | [57.0, 0.0, 36.0] | 172 | 26.8 |
| 70 | 5.16e-06 | [72.0, 0.0, 42.0] | 67 | 20.3 |
| 80 | 1.62e-05 | [66.0, 0.0, 48.0] | 117 | 11 |

Figure: `figures/i2_voxel.png`.

## 5. I3 — targeted model-based nonlinear inversion (9 parameters)

Unknowns: r_gray, r_white, r_hip, eps/sigma of gray, white and CSF (hippocampus material tied to gray). Bounded by a sigmoid map; MINPACK Levenberg–Marquardt; 6 starts (the Normal truth + 5 random). Data: ring-mode dS_k, k = 0..3, 51 frequencies, whitened by the typical-noise std. Uncertainty = CRLB from the whitened Jacobian at the solution.

### 5.1 Identifiability at the truth (synthetic, calB scale, typical noise)

**Moderate** (Fisher condition number 4.4e+11)

| param | truth | change | crlb_sd | verdict |
|---|---|---|---|---|
| r_gray [mm] | 66 | -17 | 3.4e+02 | not determined (CRLB > half the prior range) |
| r_white [mm] | 60.8 | -15.2 | 1.6e+03 | not determined (CRLB > half the prior range) |
| r_hip [mm] | 12.5 | -12.5 | 7.1e+04 | not determined (CRLB > half the prior range) |
| eps_gray | 39.1 | -8.59 | 2.6e+03 | not determined (CRLB > half the prior range) |
| sig_gray [S/m] | 5.69 | 3.27 | 9.1e+02 | not determined (CRLB > half the prior range) |
| eps_white | 31.1 | -4.24 | 1.7e+04 | not determined (CRLB > half the prior range) |
| sig_white [S/m] | 2.72 | 1.07 | 1.9e+03 | not determined (CRLB > half the prior range) |
| eps_csf | 48.8 | -16.2 | 0.85 | determined |
| sig_csf [S/m] | 5.34 | 1.07 | 0.2 | determined |

Weakest Fisher direction (smallest eigenvalue 2.0e-10): r_hip -1.00; strongest: sig_csf -1.00

**Severe** (Fisher condition number 5.1e+15)

| param | truth | change | crlb_sd | verdict |
|---|---|---|---|---|
| r_gray [mm] | 62.2 | -20.8 | 1.9e+04 | not determined (CRLB > half the prior range) |
| r_white [mm] | 57 | -19 | 6.3e+04 | not determined (CRLB > half the prior range) |
| r_hip [mm] | 7.5 | -17.5 | 5.9e+06 | not determined (CRLB > half the prior range) |
| eps_gray | 38.4 | -9.31 | 6.8e+04 | not determined (CRLB > half the prior range) |
| sig_gray [S/m] | 5.92 | 3.5 | 3.4e+04 | not determined (CRLB > half the prior range) |
| eps_white | 30.4 | -4.95 | 6.6e+05 | not determined (CRLB > half the prior range) |
| sig_white [S/m] | 2.88 | 1.23 | 7.6e+04 | not determined (CRLB > half the prior range) |
| eps_csf | 32.5 | -32.5 | 0.77 | determined |
| sig_csf [S/m] | 6.41 | 2.14 | 0.16 | determined |

Weakest Fisher direction (smallest eigenvalue 3.2e-14): r_hip -1.00; strongest: sig_csf +1.00

### 5.2 Fits

t_csf = 83.5 − r_gray (true: Normal 0.5, Mild 12.95, Moderate 17.45, Severe 21.25 mm). chi2/dof ≈ 1 means the model explains the data to within the noise.

| dataset | stage | chi2_dof | t_csf | t_csf_true | r_white | r_hip | eps_gray | sig_gray | eps_white | sig_white | eps_csf | sig_csf |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HFSS calA (Normal cal.) | Mild | 13.9 | 1.7 ± 0.6 | 12.95 | 79.3 (64.6) | 16.7 (17.5) | 53.2 (40.3) | 7.13 (5.2) | 30.5 (31.8) | 0.808 (2.39) | 80 (55.2) | 2.94 (4.91) |
| HFSS calB (Mild-tuned a2) | Mild | 13.9 | 19.5 ± 0.2 | 12.95 | 59.3 (64.6) | 16.7 (17.5) | 80 (40.3) | 4.47 (5.2) | 46 (31.8) | 0.841 (2.39) | 80 (55.2) | 0.2 (4.91) |
| HFSS calA (Normal cal.) | Moderate | 11.9 | 1.4 ± 0.2 | 17.45 | 80 (60.8) | 21.7 (12.5) | 10 (39.1) | 1.87 (5.69) | 33 (31.1) | 1.06 (2.72) | 59 (48.8) | 8 (5.34) |
| HFSS calB (Mild-tuned a2) | Moderate | 13.7 | 1.9 ± 0.3 | 17.45 | 77 (60.8) | 40.7 (12.5) | 52.1 (39.1) | 1.17 (5.69) | 64.5 (31.1) | 0.2 (2.72) | 67.5 (48.8) | 0.203 (5.34) |
| HFSS calA (Normal cal.) | Severe | 24.2 | 11.8 ± 0.1 | 21.25 | 62.2 (57) | 5.81 (7.5) | 80 (38.4) | 4.12 (5.92) | 10.9 (30.4) | 0.616 (2.88) | 65.4 (32.5) | 0.202 (6.41) |
| HFSS calB (Mild-tuned a2) | Severe | 27.5 | 1.9 ± 0.2 | 21.25 | 80.6 (57) | 4.34 (7.5) | 10 (38.4) | 4.12 (5.92) | 80 (30.4) | 0.622 (2.88) | 80 (32.5) | 8 (6.41) |
| HFSS calA (Normal cal.) | noise-only | 0.974 | 14.2 ± 0.3 | 0.50 | 52.2 (76) | 20.8 (25) | 62.4 (47.7) | 1.68 (2.42) | 58 (35.3) | 1.96 (1.65) | 57.5 (65) | 0.608 (4.27) |
| synthetic (same model) | Mild | 1.05 | 2.7 ± 1.2 | 12.95 | 69.7 (64.6) | 3.48 (17.5) | 70.5 (40.3) | 0.618 (5.2) | 80 (31.8) | 1.72 (2.39) | 61.3 (55.2) | 3.95 (4.91) |
| synthetic (patch antenna) | Mild | 3.07 | 24.3 ± 1.4 | 12.95 | 56.5 (64.6) | 37.8 (17.5) | 79 (40.3) | 0.832 (5.2) | 10 (31.8) | 0.601 (2.39) | 58.8 (55.2) | 1.96 (4.91) |
| synthetic (same model) | Moderate | 1.05 | 2.4 ± 2.5 | 17.45 | 65.1 (60.8) | 61.9 (12.5) | 68.4 (39.1) | 2.49 (5.69) | 80 (31.1) | 8 (2.72) | 54.2 (48.8) | 4.36 (5.34) |
| synthetic (patch antenna) | Moderate | 3.57 | 1.1 ± 0.4 | 17.45 | 59.7 (60.8) | 41.8 (12.5) | 80 (39.1) | 1.91 (5.69) | 10 (31.1) | 0.542 (2.72) | 59.8 (48.8) | 0.2 (5.34) |
| synthetic (same model) | Severe | 1.07 | 19.4 ± 123.1 | 21.25 | 47.9 (57) | 22 (7.5) | 76.2 (38.4) | 5.06 (5.92) | 28.9 (30.4) | 1.46 (2.88) | 32.1 (32.5) | 6.53 (6.41) |
| synthetic (patch antenna) | Severe | 8.24 | 1.1 ± 0.3 | 21.25 | 63.3 (57) | 60.2 (7.5) | 80 (38.4) | 1.81 (5.92) | 10 (30.4) | 8 (2.88) | 46.6 (32.5) | 0.2 (6.41) |
| synthetic (same model) | noise-only | 0.983 | 9.2 ± 1.8 | 0.50 | 65.4 (76) | 3.59 (25) | 69 (47.7) | 2.88 (2.42) | 80 (35.3) | 1.18 (1.65) | 57.6 (65) | 1.23 (4.27) |

(parameter: estimate (truth))

Reading the fits:
- **Synthetic, same model (inverse crime, noise only):** every fit reaches chi2/dof ≈ 1, yet CSF thickness and the deeper parameters land far from the truth. Many different layered heads explain the same data: the degeneracy seen in §5.1. eps_csf, the parameter §5.1 calls determined, deviates from its truth by Mild 0.8σ, Moderate 0.4σ, Severe 0.7σ, noise-only 5.2σ (|est − truth| / CRLB at the fit). It is recovered within its uncertainty for the AD stages. On noise-only data, however, the fit settles in a different minimum, because the misfit surface is multimodal. Only the effective material of the outermost layer is measured; its geometry is not.
- **HFSS:** chi2/dof 12–27. The model cannot reproduce the HFSS dS (antenna-model mismatch, §3). Parameters sit on bounds and change with the calibration choice (calA vs calB), so they carry no physical meaning.
- **Antenna-mismatch test:** data made with the patch-aperture antenna and inverted with the point-dipole model give chi2/dof 3–8 and wrong CSF thickness. A modest antenna-model error alone is enough to break I3.

### 5.3 CSF thickness as a feature vs the k = 3 scalar metric

One LM fit per noisy draw, started at the Normal truth. Threshold tuned on Mild vs Normal draws; tested on Moderate + Severe vs fresh Normal draws. k3 metric = full-band mean opposite-antenna power in dB (M5.C3; lower → AD). For k3, tau is printed sign-flipped: the threshold is −tau dB.

| data | feature | tau | sens | spec | bal_acc | macro_f1 |
|---|---|---|---|---|---|---|
| HFSS | t_csf | 1.076 | 0.400 | 0.650 | 0.525 | 0.482 |
| HFSS | k3 | 51.797 | 1.000 | 1.000 | 1.000 | 1.000 |
| synthetic | t_csf | 3.533 | 0.000 | 1.000 | 0.500 | 0.250 |
| synthetic | k3 | 51.797 | 0.275 | 1.000 | 0.637 | 0.506 |

Figure: `figures/i3_csf_thickness.png`.

## 6. Verdict — what 6 antennas on one ring at 3.2–4.2 GHz can and cannot localise

**Can (in these simulations, under typical noise):**

1. **Detect that something changed** relative to a Normal baseline of the same head. DAS/DMAS image energy sits 19–29 dB above the noise-only image for Moderate/Severe, in every noisy draw (§2, §8). This is detection, not localisation.
2. **See the outer ~10 mm of brain, and only near the antennas.** A 1 cm³ change of |d eps| = 10 reaches SNR ≥ 1 down to r ≈ 73 mm in the best direction. In the median direction the SNR is ≤ 0.13 at every depth (§4.1, surrogate fields, Mild-calibrated scale).
3. **Estimate the effective material of the layer right under the skull.** Of the 9 phantom parameters, only eps_csf, sig_csf are identifiable (CRLB at the truth, synthetic data, typical noise). The array measures one surface impedance, not a layered structure.

**Cannot:**

1. **Place the change with radar imaging (I1).** Every method and delay model puts the radial peak at r = 1, 11, 15 mm. That is the centre, where all 21 pair delays coincide for a ring of equidistant antennas: a symmetric-array artefact. The true change lies at 57–83.5 mm. The depth scale also hinges on an antenna delay the data cannot fix (§1: ~3 ns in transmission, ~0 in reflection). The ideal point target has an elevation width of several cm (§2 table).
2. **See deep structures.** The hippocampus (r < 25 mm) and white matter beyond ~10 mm under the cortex are invisible: SNR ≈ 0.04 at r = 20 mm even in the best direction. The hippocampal shrinkage cannot be recovered by any method here.
3. **Resolve depth structure (I2).** In the radial inversion only the outermost shell (82–83.5 mm) has resolution-matrix diagonal ≥ 0.5 (max 0.72). Voxel point-spread functions have diagonals ~1e-5 and peak tens of mm from the true voxel. Voxel images on HFSS data are noise or zero.
4. **Recover CSF thickness (atrophy), gray/white radii or deeper materials (I3).** They are not identifiable even with a perfect forward model (CRLB > prior range). On HFSS data the model cannot fit the data (chi2/dof 12–27; §3). The recovered CSF thickness does not separate the classes; the k = 3 scalar metric does (§5.3).
5. **Lateral / lobe localisation.** Impossible in this phantom by construction: the head and every change are spherically symmetric, so any azimuthal structure in an image is an array artefact. With six antennas on one ring it would also be impossible in an anatomical head (§7).
6. **Separate AD stages.** The model predicts Severe dS ≈ 2× Mild; HFSS shows ≈ 1.3–1.4×. AD-vs-AD differences are 0.5–3× the port asymmetry, and the mesh noise is unmeasured: **unverified against mesh noise**.

**Imaging vs the scalar metric.** No imaging or inversion method recovered the known changes better than the k = 3 band-averaged power. That scalar remains the best Normal-vs-AD discriminator. Section 1 explains why it works: the opposite-antenna wave skims the head surface, and the near-surface CSF/cortex change is exactly what it samples.

## 7. What array would lobe-level localisation need? (for the CST voxel model)

Target: tell apart changes of order 2–3 cm in extent located in different lobes, at cortical depths 1–4 cm under the skull, in a head that is **not** spherically symmetric. That needs three things this array lacks: lateral (angular) sampling, elevation sampling, and depth (range) information that is not killed by loss.

**Loss and wavelength in gray matter** (3.5 GHz: this project's value; 1–2 GHz: approximate IT'IS/Gabriel values, flagged):

| f_GHz | eps_r | sigma | lambda_mm | att_dB_cm | two_way_loss_3cm_dB | xrange_res_mm |
|---|---|---|---|---|---|---|
| 1.0 | 52.3 | 0.99 | 40.9 | 2.2 | 13 | 20 |
| 1.5 | 51.1 | 1.21 | 27.7 | 2.7 | 16 | 14 |
| 2.0 | 50.1 | 1.43 | 21.0 | 3.3 | 20 | 11 |
| 3.5 | 47.7 | 2.42 | 12.3 | 5.7 | 34 | 6 |

**Range resolution** c/(2B·sqrt(eps)), eps ≈ 45:

| band | B_GHz | range_res_mm |
|---|---|---|
| 3.2-4.2 GHz (this array) | 1 | 22 |
| 2.8-4.2 GHz (re-run) | 1.4 | 16 |
| 0.7-2.2 GHz | 1.5 | 15 |
| 0.5-2.5 GHz | 2 | 11 |

Reasoning and minimum requirements:
1. **Frequency.** At 3.5 GHz, two-way loss to 3 cm of cortex is ~35 dB on top of the skin/skull mismatch. That is why every path here sees only the outer ~1–2 cm (§4.1). A band of about 0.7–2.2 GHz (2–3 dB/cm, λ ≈ 3–4 cm in tissue) roughly halves the loss per cm and keeps a half-wavelength lateral resolution of ~1.5–2 cm. Imaging systems for stroke use this band for the same reason.
2. **Bandwidth.** ≥ 1.5 GHz (fractional bandwidth ≳ 100 %) for ~1.5 cm range resolution. This needs genuinely wideband antennas (not a resonant patch whose ~3 ns transmission group delay (§1) blurs range), plus per-antenna de-embedding measured on a phantom.
3. **Angular sampling.** Around a ~55 cm head circumference, lobe-scale lateral resolution (~2 cm) needs element spacing ≲ λ_medium/2. With a coupling medium (eps ≈ 20–40) at ≤ 2 GHz that is 16–24 antennas per ring. Six antennas give only 4 independent ring modes for a symmetric target, and 21 pairs at most otherwise.
4. **Elevation.** A single ring cannot place anything in z. §2's point-target test gives an elevation width of several cm even for an ideal scatterer. At least 2–3 rings (or a helmet), with ~2–3 cm vertical spacing over the fronto-parietal-temporal region: **≈ 32–64 antennas** in total, multistatic, all pairs measured.
5. **Coupling medium / matching.** An immersion or matching layer (eps ≈ 20–40, low loss) between antennas and skin suppresses the skin reflection (the dominant |S_ii|) and the around-the-head air path, which here carries the k = 3 signal (§1). This forces energy through the skull.
6. **Forward model.** Model-based inversion needs each antenna's own incident field in the head (HFSS/CST field exports per port, as planned for I2), not a point-dipole idealisation. §3 shows that the idealisation fails even on this simple phantom. Then use a DBIM/Gauss–Newton loop with an anatomical (MRI-template) prior. Microwave data alone will not give voxel-level lobe maps; a regional parameterisation (per-lobe d eps, like I3 here) is realistic.
7. **Calibration against mesh noise.** Lobe-level differences are small. Between-mesh and repeat-measurement noise must be measured first (Normal mesh-repeat), because the port-asymmetry floor here is already 0.5–3× the AD-vs-AD differences.

