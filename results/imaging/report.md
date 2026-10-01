# Track A — imaging / localisation study (`imaging/`, code 22d5b81, 2026-10-02)

Regenerate: `python imaging/run_imaging.py` (tests: `python -m pytest imaging/tests -q`).
Everything here comes from **one HFSS simulation per stage**: it shows what is recoverable from these simulations under the stated noise, **not** generalisation to new heads. Between-mesh noise is unmeasured, so every AD-vs-AD statement is **unverified against mesh noise**.
**Tuning protocol:** every free choice (antenna delay, effective permittivity, regularisation weights, calibration scale kappa(f), thresholds) is set on **Mild**; results are reported on **Moderate and Severe**. Noise floor = 'typical' profile (0.25 dB, 2 deg, -70 dB floor) on both the stage and the Normal measurement.

## 0. Data, assumptions, blocked items

- Sections from **i2** use `hfss-v2-sameproject-masked` (2.8-4.2 GHz): Normal `new_Healthy.s6p`, MCI `new_MCI.s6p`, Mild `new_MildAD.s6p`, Moderate `new_ModerateAD.s6p`, Severe `new_SevereAD.s6p`. Glitch masking ON.
- Sections from **paths, i1, val, i3** use `hfss-v1-masked` (3.2-4.2 GHz): Normal `brain_sevem_layer_Healthy.s6p`, Mild `Brain_sevem_layer_MildAD.s6p`, Moderate `Brain_sevem_layer_ModerateAD.s6p`, Severe `brain_sevem_layer_SevereAD.s6p`. Glitch masking ON.
- **Two simulation sets are mixed in this report**, and each section states its data. The v2 set (all stages re-solved in one HFSS project, 2.8–4.2 GHz) replaced v1 on 2026-10-01. §4 (I2 with the HFSS field exports) uses v2, because the fields come from the v2 Normal design. §1–3 and §5 are still the v1 analysis and have not yet been re-run on v2.
- Assumption: Skin/fat/skull materials are not in MODEL_CARD.md (OPEN-GUI): assumed skin 37/2.0, fat 10.5/0.42, skull 10.8/0.61 (eps_r / S/m).
- Assumption: Ring z-sign and antenna orientation are OPEN in MODEL_CARD.md: ring assumed at +z (polar angle 60.5 deg), broadside facing the origin; S is mirror-symmetric in z so the sign does not affect S, only image coordinates.
- Assumption: Antenna = point electric dipole at the feed point, tangential to the sphere; the polarisation (theta^ vs phi^) is chosen by the fit to the HFSS Normal ring couplings.
- Assumption: Normal-stage materials are back-calculated values (MODEL_CARD caveat).
- Assumption: The HFSS materials are static (no dispersion); the model uses the same constant eps_r, sigma.
- The brief names `reference/dbim_reference.m`; the repository holds `references/imaging_code.m` (a 2-D incident/total-field script). Not used beyond inspiration.
- **`data/fields/` HFSS field exports: present (used in §4).** 

## 1. The k = 3 path question — direct evidence from the HFSS couplings

*Data: `hfss-v1-masked` (3.2-4.2 GHz) — Normal `brain_sevem_layer_Healthy.s6p`, Mild `Brain_sevem_layer_MildAD.s6p`, Moderate `Brain_sevem_layer_ModerateAD.s6p`, Severe `brain_sevem_layer_SevereAD.s6p`.*

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

*Data: `hfss-v1-masked` (3.2-4.2 GHz) — Normal `brain_sevem_layer_Healthy.s6p`, Mild `Brain_sevem_layer_MildAD.s6p`, Moderate `Brain_sevem_layer_ModerateAD.s6p`, Severe `brain_sevem_layer_SevereAD.s6p`.*

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

*Data: `hfss-v1-masked` (3.2-4.2 GHz) — Normal `brain_sevem_layer_Healthy.s6p`, Mild `Brain_sevem_layer_MildAD.s6p`, Moderate `Brain_sevem_layer_ModerateAD.s6p`, Severe `brain_sevem_layer_SevereAD.s6p`.*

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

## 4. I2 — HFSS numerical Green's function: sensitivity maps and linearised inversion

*Data: `hfss-v2-sameproject-masked` (2.8-4.2 GHz) — Normal `new_Healthy.s6p`, MCI `new_MCI.s6p`, Mild `new_MildAD.s6p`, Moderate `new_ModerateAD.s6p`, Severe `new_SevereAD.s6p`.*

**Source.** HFSS 2024.2 calculator exports of complex E for the Normal design (project `new`, design `Healthy`), one file per driven terminal (1 V incident, 0°, others matched 50 Ω, port post-processing off), at 3.4 / 3.6 / 3.8 GHz on a 3 mm grid (−90…90 mm), plus a ±120 mm / 4 mm export of T1 at 3.6 GHz. Background S-parameters: the matching v2 Normal `new_Healthy.s6p`. All Jacobians therefore have 3 frequency rows (the S data have 281).

### 4.0 Field-file checks

- All 19 files present: True. Every file: 61x61x61 nodes (= 61³ rows: True), full regular grid: True, z varies fastest: True.
- NaN nodes per file: 20, 22; radii 108-113, 97-115 mm (antenna metal). Finite everywhere inside r < 88 mm: True.
- Re/Im pairing (median |div E|·h / |E| over air nodes; a wrong pairing is not divergence-free): E_Normal_T1_3p6GHz.fld: interleaved 0.077 vs blocked 0.147; E_Normal_T4_3p4GHz.fld: interleaved 0.062 vs blocked 0.130; E_Normal_T1_3p6GHz_wide.fld: interleaved 0.088 vs blocked 0.169. The stated pairing (x y z, Ex_re Ex_im, Ey_re Ey_im, Ez_re Ez_im) is the one used. The residual is the 3 mm finite-difference error near the antennas.

**Antennas located from their own fields** (|E|-weighted centroid of the strongest air nodes at r = 89–93 mm; θ-fraction = |E·θ̂| / (|E·θ̂| + |E·φ̂|) there):

| T | azimuth_deg | field_centroid_polar_deg | theta_fraction |
|---|---|---|---|
| 1 | -90.5 | 55.1 | 0.65 |
| 2 | -31.0 | 54.9 | 0.65 |
| 3 | 29.6 | 55.0 | 0.65 |
| 4 | 89.4 | 55.1 | 0.65 |
| 5 | 148.9 | 55.1 | 0.65 |
| 6 | -150.4 | 55.0 | 0.65 |

- This settles two OPEN items of the model card. The ring is at **+z**: every centroid is in the upper hemisphere (≈55°; the field centroid sits slightly above the 60.5° feed, which is used for geometry). T1…T6 are consecutive at 60° steps, with **T1 at azimuth ≈ −90°** (not 0° as assumed in the I1/I3 geometry; immaterial for S of a symmetric head, but it means the plane through T1 and T4 is x = 0).
- Near-field polarisation is mixed, ≈ 65 % θ̂ / 35 % φ̂ in amplitude. The point-dipole model in §3/§5 had chosen φ̂ from the Normal couplings. Neither pure orientation is right; this is part of the antenna-model mismatch found in §3.

**Ring symmetry at field level** (inside r < 88 mm). Relative rms difference between an antenna's field and its opposite antenna's field rotated by 180° about z; rms amplitude of each antenna relative to the mean of all six:

| f_GHz | pair | rel_rms_diff |
|---|---|---|
| 3.4 | T4 vs R180(T1) | 0.114 |
| 3.4 | T5 vs R180(T2) | 0.120 |
| 3.4 | T6 vs R180(T3) | 0.120 |
| 3.6 | T4 vs R180(T1) | 0.153 |
| 3.6 | T5 vs R180(T2) | 0.158 |
| 3.6 | T6 vs R180(T3) | 0.158 |
| 3.8 | T4 vs R180(T1) | 0.119 |
| 3.8 | T5 vs R180(T2) | 0.138 |
| 3.8 | T6 vs R180(T3) | 0.138 |

Amplitude ratios at 3.6 GHz: T1 1.044, T2 0.974, T3 0.981, T4 1.046, T5 0.973, T6 0.979. The fields are symmetric to 11–16 % (rms), the field-level counterpart of the S-parameter port asymmetry. Any image feature below that level is not trustworthy.

### 4.1 Absolute scale and linearisation

With 1 V incident on every 50 Ω port the Born sensitivity is absolute: dS_ij = −(jωε0 Z0 / 4V²) ∫ dε E_i·E_j dV. κ(f) is the complex factor that best maps this prediction (true dε of Mild, radial shells or voxels) onto the HFSS dS of Mild. κ = 1 would mean exact Born agreement in absolute units.

| f_GHz | abs_kappa | phase_deg | abs_kappa_voxel |
|---|---|---|---|
| 3.4 | 1.94 | -25 | 1.18 |
| 3.6 | 1.93 | -72 | 1.19 |
| 3.8 | 11.41 | -121 | 7.81 |

| stage | k | born_over_hfss | err_abs_scale | err_kappa_mild |
|---|---|---|---|---|
| Mild | 0 | 0.11 | 0.99 | 1.19 |
| Mild | 1 | 0.12 | 1.04 | 0.74 |
| Mild | 2 | 0.25 | 0.82 | 1.06 |
| Mild | 3 | 0.15 | 0.91 | 0.97 |
| Moderate | 0 | 0.23 | 0.95 | 1.52 |
| Moderate | 1 | 0.26 | 1.05 | 0.41 |
| Moderate | 2 | 0.32 | 0.73 | 1.18 |
| Moderate | 3 | 0.22 | 0.88 | 1.16 |
| Severe | 0 | 0.35 | 0.87 | 1.57 |
| Severe | 1 | 0.37 | 0.92 | 0.52 |
| Severe | 2 | 0.44 | 0.66 | 1.34 |
| Severe | 3 | 0.30 | 0.73 | 1.50 |

Reading:
- At 3.4 and 3.6 GHz |κ| = 1.18 and 1.19 (voxel Jacobian, fields taken at the grid nodes) and 1.94 and 1.93 (radial Jacobian, fields interpolated onto thin shells). So the absolute 1 V Born scale holds to within a factor of ~2. The spread between the two shows how much the result depends on how the 3 mm grid samples the fields at the thin CSF/skull interfaces. At 3.8 GHz |κ| = 8–11: there the Born prediction misses the HFSS dS badly (the k = 2 couplings have deep nulls near 3.8 GHz).
- The phase of κ turns by about -48° per 200 MHz, i.e. a residual delay of ~0.7 ns between the field-export phase reference and the S-parameter reference plane. A feed line in front of each patch would do this, but it was not measured, so treat it as unexplained.
- The Born prediction of the true change is only 0.11–0.44 of the HFSS dS (column born_over_hfss, radial Jacobian, absolute scale). Even with κ fitted on Mild, the errors for Moderate/Severe are 0.4–1.6. The AD change (12–21 mm of gray/white replaced by CSF) is far from a small perturbation, so a linear inversion can at best be qualitative.

### 4.2 Where can this array see? (HFSS fields)

SNR of a 1 cm³ blob with |dε| = 10 (≈ the gray→CSF contrast) at radius r, on the Normal background, under the typical noise on both measurements, summed over the 3 frequencies. best = the direction closest to the antennas, median = over all directions. r_min_snr1 = the smallest radius down to which SNR ≥ 1 holds continuously from the surface (n/a = never reached).

| scale | path | best_at_83 | best_at_75 | best_at_60 | best_at_20 | median_max | r_min_snr1 |
|---|---|---|---|---|---|---|---|
| absolute | k=0 | 1 | 0.34 | 0.058 | 0.00096 | 0.019 | 83 |
| absolute | k=1 | 0.5 | 0.22 | 0.11 | 0.018 | 0.15 | 87 |
| absolute | k=2 | 0.35 | 0.15 | 0.045 | 0.012 | 0.1 | 87 |
| absolute | k=3 | 0.4 | 0.15 | 0.044 | 0.0048 | 0.094 | 87 |
| absolute | all 21 pairs | 1.2 | 0.43 | 0.11 | 0.022 | 0.21 | 83 |
| κ-calibrated | k=0 | 4.3 | 1.5 | 0.25 | 0.0036 | 0.053 | 71 |
| κ-calibrated | k=1 | 3.2 | 1.3 | 0.31 | 0.047 | 0.64 | 73 |
| κ-calibrated | k=2 | 1.1 | 0.46 | 0.15 | 0.034 | 0.47 | 83 |
| κ-calibrated | k=3 | 2.4 | 1 | 0.26 | 0.017 | 0.25 | 75 |
| κ-calibrated | all 21 pairs | 5.9 | 2.3 | 0.44 | 0.058 | 0.89 | 69 |

Volume-weighted fraction of the (relative) sensitivity inside r < 60 mm: k0 3.1%, k1 4.5%, k2 3.7%, k3 3.7%.

- Best direction, all pairs: SNR ≥ 1 down to r ≈ 83 mm on the absolute scale and r ≈ 69 mm κ-calibrated: between the outermost ~1 mm and the outer ~14 mm of brain, and only right under an antenna. The κ-calibrated values are an upper bound: they include 3.8 GHz, where |κ| ≈ 8–11 because Born fails (§4.1).
- In the median direction the SNR never exceeds 0.21 (absolute) / 0.89 (κ). At r = 60 mm even the best direction gives 0.11 / 0.44, and at r = 20 mm 0.022 / 0.058. A localised change deeper than ~1.5 cm is below the noise everywhere.
- Figures: `figures/i2h_sensitivity_maps.png`, `figures/i2h_detectability_radial.png`.

### 4.3 The k = 3 (opposite-antenna) path, from the wide export

The wide file holds only T1. The opposite antenna's field is obtained by the ring symmetry, E_T4 = R180 E_T1, which agrees with the actual T4 export to 13% rms inside the head. |E_T1·E_T4| is the Born sensitivity of the T1–T4 coupling to a permittivity change at each point, including points in air.

| region | share_of_k3_sensitivity |
|---|---|
| brain r<83.5 | 0.31% |
| CSF/skull/fat/skin 83.5-88 | 0.75% |
| air gap 88-97 | 12.92% |
| air r>=97 (incl. antennas) | 86.01% |

Inside the brain, the k = 3 sensitivity by depth: 0-40 mm 2%, 40-60 mm 9%, 60-70 mm 17%, 70-78 mm 31%, 78-83.5 mm 41%.

Field of T1 on the way to T4 (antennas 121° apart): at the half-way point it is -33 dB (arc over the top, in air at r = 91 mm) vs -57 dB (straight chord, deepest point r = 48 mm), relative to the field near T1.

**Verdict (HFSS fields).** 99% of the k = 3 sensitivity is in air and 0.3% is in the brain. Half-way, the through-head route is 23 dB weaker than the around-the-head route. This confirms the delay-based verdict of §1 with the real antennas: **the opposite-antenna signal travels around the head in air**. The small part that touches the brain sits in its outer layer (73% within 13.5 mm of the brain surface). That is why k = 3 reacts to CSF/cortex changes and to nothing deeper. Figure: `figures/i2h_k3_path.png`.

### 4.4 Radial inversion (2 mm shells; d eps_r and d eps'')

24 real data (4 ring modes × 3 frequencies × Re/Im) for 84 unknowns. Fields trilinearly interpolated onto a shell quadrature (the 3 mm grid under-resolves the 0.5 mm Normal CSF layer). Tikhonov (GCV, L-curve) and 1-D TV (λ = 1, tuned on Mild synthetic data). Errors vs the true shell profile:

| data | stage | method | rel_err_eps_r | rel_err_eps_pp | corr_eps_r | corr_eps_pp |
|---|---|---|---|---|---|---|
| synthetic-linear | Mild | tikhonov-gcv | 1.69 | 1.42 | 0.38 | 0.24 |
| synthetic-linear | Mild | tikhonov-lcurve | 0.98 | 0.99 | 0.24 | 0.09 |
| synthetic-linear | Mild | tv | 1.12 | 0.71 | -0.20 | 0.13 |
| HFSS | Mild | tikhonov-gcv | 1.00 | 0.99 | 0.07 | 0.03 |
| HFSS | Mild | tikhonov-lcurve | 1.00 | 0.99 | 0.05 | 0.02 |
| HFSS | Mild | tv | 5.30 | 4.93 | -0.67 | -0.13 |
| synthetic-linear | Moderate | tikhonov-gcv | 1.59 | 1.33 | 0.44 | 0.27 |
| synthetic-linear | Moderate | tikhonov-lcurve | 0.99 | 0.97 | 0.17 | 0.17 |
| synthetic-linear | Moderate | tv | 0.91 | 0.55 | 0.03 | 0.22 |
| HFSS | Moderate | tikhonov-gcv | 31.86 | 26.41 | -0.11 | 0.26 |
| HFSS | Moderate | tikhonov-lcurve | 1.00 | 1.00 | 0.08 | 0.01 |
| HFSS | Moderate | tv | 0.94 | 1.21 | 0.09 | -0.44 |
| synthetic-linear | Severe | tikhonov-gcv | 1.46 | 1.13 | 0.39 | 0.37 |
| synthetic-linear | Severe | tikhonov-lcurve | 0.95 | 0.96 | 0.33 | 0.23 |
| synthetic-linear | Severe | tv | 1.07 | 0.67 | 0.35 | 0.23 |
| HFSS | Severe | tikhonov-gcv | 31.82 | 22.77 | 0.10 | 0.11 |
| HFSS | Severe | tikhonov-lcurve | 1.00 | 0.99 | 0.14 | 0.08 |
| HFSS | Severe | tv | 0.73 | 1.84 | -0.28 | -0.58 |

Resolution-matrix diagonal (GCV λ on Mild synthetic) ≥ 0.5 at r ∈ 75–83 mm (max 0.96). Scanning inward, it falls below 0.3 at r ≈ 67 mm and below 0.1 at r ≈ 49 mm. Only the outer ~1 cm has any depth resolution.
- Even noise-perturbed **Born-consistent** synthetic data are not recovered: rel. errors 0.55–1.69, correlations ≤ 0.44. On HFSS data, GCV is near zero for Mild and blows up for Moderate/Severe (the data are not Born-consistent, §4.1). The L-curve returns ≈ 0, and TV is mostly anti-correlated with the truth. Figure: `figures/i2h_inversions.png`.

### 4.5 Voxel inversion (3 mm grid nodes, r < 83.5 mm)

90447 voxels × (dε_r, dε''), 126 real data (21 pairs × 3 frequencies × Re/Im). Tikhonov-GCV and L1 (λ tuned on Mild synthetic).

| data | stage | method | rel_err_eps_r | rel_err_eps_pp | corr_eps_r | corr_eps_pp |
|---|---|---|---|---|---|---|
| synthetic-linear | Mild | tikhonov-gcv | 1.00 | 1.00 | 0.08 | 0.03 |
| synthetic-linear | Mild | l1 | 1.00 | 1.00 | n/a | n/a |
| HFSS | Mild | tikhonov-gcv | 1.00 | 1.00 | 0.05 | 0.03 |
| HFSS | Mild | l1 | 1.00 | 1.00 | 0.00 | n/a |
| synthetic-linear | Moderate | tikhonov-gcv | 1.00 | 1.00 | 0.08 | 0.01 |
| synthetic-linear | Moderate | l1 | 1.00 | 1.00 | 0.01 | n/a |
| HFSS | Moderate | tikhonov-gcv | 1.00 | 1.00 | 0.06 | 0.01 |
| HFSS | Moderate | l1 | 1.00 | 1.00 | n/a | n/a |
| synthetic-linear | Severe | tikhonov-gcv | 0.99 | 1.00 | 0.17 | 0.03 |
| synthetic-linear | Severe | l1 | 1.01 | 1.00 | 0.01 | n/a |
| HFSS | Severe | tikhonov-gcv | 0.99 | 1.00 | 0.12 | 0.02 |
| HFSS | Severe | l1 | 1.00 | 1.00 | n/a | n/a |

Point-spread functions (resolution-matrix columns) for voxels along T1's feed direction:

| r_mm | voxel_mm | diag | peak_at_mm | peak_offset_mm | n_vox_above_half |
|---|---|---|---|---|---|
| 20 | [0.0, -18.0, 9.0] | 7.2e-06 | [0.0, -66.0, 51.0] | 64 | 40 |
| 40 | [0.0, -36.0, 21.0] | 9.5e-05 | [0.0, -75.0, 36.0] | 42 | 85 |
| 60 | [0.0, -51.0, 30.0] | 5.5e-04 | [-3.0, -66.0, 51.0] | 26 | 38 |
| 70 | [0.0, -60.0, 33.0] | 1.1e-03 | [0.0, -69.0, 42.0] | 13 | 24 |
| 80 | [0.0, -69.0, 39.0] | 7.1e-03 | [0.0, -69.0, 45.0] | 6 | 12 |

- Point images, inward along T1's feed direction: r = 20 mm → peak 64 mm away (diag 7e-06); r = 40 mm → peak 42 mm away (diag 9e-05); r = 60 mm → peak 26 mm away (diag 6e-04); r = 70 mm → peak 13 mm away (diag 1e-03); r = 80 mm → peak 6 mm away (diag 7e-03). Only the voxel just under the brain surface is imaged near its place, and even that recovers well under 1 % of a unit change. Deeper voxels are imaged outward toward the surface: depth is not resolved.
- The L1 solution is the all-zero image (no sparse pattern beats zero on Mild). Tikhonov images of HFSS data are uncorrelated with the truth (corr ≤ 0.12). Figure: `figures/i2h_voxel.png`.

### 4.6 HFSS vs the earlier surrogate (point-dipole fields, v1 data)

| quantity | surrogate_v1 | hfss_abs | hfss_kappa |
|---|---|---|---|
| SNR≥1 (best dir.) down to r, mm | 73 | 83 | 69 |
| radial resolution diag max | 0.718 | n/a | 0.962 |
| k3 sensitivity share r < 60 mm | 0.124 | n/a | 0.0372 |

The surrogate used 51 frequencies (3.2–4.2 GHz). HFSS fields exist at 3 frequencies, which costs √17 ≈ 4× in SNR for broadband sums, but the HFSS fields describe the real antennas. Both say the same thing: only the outer ~1 cm under the antennas is visible, and nothing is localised in depth.

## 5. I3 — targeted model-based nonlinear inversion (9 parameters)

*Data: `hfss-v1-masked` (3.2-4.2 GHz) — Normal `brain_sevem_layer_Healthy.s6p`, Mild `Brain_sevem_layer_MildAD.s6p`, Moderate `Brain_sevem_layer_ModerateAD.s6p`, Severe `brain_sevem_layer_SevereAD.s6p`.*

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

## 6. Verdict — what 6 antennas on one ring in this band can and cannot localise

Each item cites the section it rests on. §4 uses the v2 data with the HFSS fields; the other sections use v1 (see the data line under each heading).

**Can (in these simulations, under typical noise):**

1. **Detect that something changed** relative to a Normal baseline of the same head. DAS/DMAS image energy sits 19–29 dB above the noise-only image for Moderate/Severe, in every noisy draw (§2, §8). This is detection, not localisation.
2. **Sense only the outermost brain, and only right under an antenna.** A 1 cm³ change of |d eps| = 10 reaches SNR ≥ 1 down to r ≈ 83 mm on the absolute 1 V scale and at most r ≈ 69 mm κ-calibrated (the outermost ~1–14 mm of brain) in the best direction. In the median direction the SNR is ≤ 0.89 at every depth (§4.2, HFSS fields of the real antennas, κ-calibrated).
3. **Explain the k = 3 signal.** With the real antennas' fields, 99% of the opposite-antenna sensitivity lies in air around the head and 0.3% in the brain, almost all of it in the outer layer (§4.3). This agrees with the delay test of §1. The k = 3 metric works because the wave skims the head and samples the CSF/cortex just under the skull.
4. **Estimate the effective material of the layer right under the skull.** Of the 9 phantom parameters, only eps_csf, sig_csf are identifiable (CRLB at the truth, synthetic data, typical noise). The array measures one surface impedance, not a layered structure.

**Cannot:**

1. **Place the change with radar imaging (I1).** Every method and delay model puts the radial peak at r = 1, 11, 15 mm. That is the centre, where all 21 pair delays coincide for a ring of equidistant antennas: a symmetric-array artefact. The true change lies at 57–83.5 mm. The depth scale also hinges on an antenna delay the data cannot fix (§1: ~3 ns in transmission, ~0 in reflection). The ideal point target has an elevation width of several cm (§2 table).
2. **See deep structures.** The hippocampus (r < 25 mm) and white matter beyond the outer centimetre are invisible: SNR ≈ 0.06 at r = 20 mm even in the best direction. The hippocampal shrinkage cannot be recovered by any method here.
3. **Resolve depth structure (I2).** Radial-inversion resolution diagonal ≥ 0.5 only at r ≥ 75 mm (max 0.96). Voxel point images are displaced by (depth → offset) 20 mm → 64, 40 mm → 42, 60 mm → 26, 70 mm → 13, 80 mm → 6 mm. Neither the radial nor the voxel inversion recovers the true change, even from noise-only Born-consistent synthetic data. On HFSS data they return noise or zero, and the linear (Born) model explains the HFSS dS poorly (§4.1).
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

