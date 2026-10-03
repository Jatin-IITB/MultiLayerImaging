# Notation and glossary (single source of truth)

Phase 0, written 2026-10-03 at repo HEAD `ecacd35`. Every later document in `docs/` uses
these symbols. When the code and a report disagree, the **code** definition is recorded and the
disagreement is listed in §9.

Status tags: **VERIFIED** = seen in code or data by me; **REPORTED** = stated in a project
document, not re-checked; **UNKNOWN** = not established (see `open_questions.md`).

---

## 1. Geometry, antennas, ports

| Symbol / name | Meaning | Value / formula | Source | Status |
|---|---|---|---|---|
| T1 … T6 | The six DGS-patch + AMC antennas, numbered consecutively around the ring | — | `config.yaml` `ring`, `src/adstage/features/metrics.py::to_ring_order` | VERIFIED |
| ring order | Index order T1, T2, …, T6 used by **all** analysis code after re-ordering the file ports | `to_ring_order(S, port_to_ant)` | `src/adstage/features/metrics.py:40` | VERIFIED |
| port order (file) | Touchstone Port 1 … 6 = **T4, T3, T2, T1, T6, T5** | `ring.port_to_ant: [4, 3, 2, 1, 6, 5]` | `config.yaml`; Touchstone headers `Port[1] = FEED_3_T4 …` | VERIFIED (config and header text both say this; headers are not trusted by the pipeline, see §8) |
| port-map check | Of the 60 distinct ring orderings, the config map has the lowest circulant error in every file | rank 1 of 60 | `results/qc/qc_report.md`, `results/05_lobe/qc/qc_report.md` | REPORTED |
| φ_t | Azimuth of antenna T_t | φ_t = −90° + 60°(t − 1): T1 −90° (−Y), T2 −30°, T3 +30°, T4 +90° (+Y), T5 150°, T6 −150° | `MODEL_CARD.md` Part 4; `imaging/study_lobe.py` docstring | REPORTED (from field-export centroids −90.5, −31.0, 29.6, 89.4, 148.9, −150.4°) |
| feed point | Antenna feed position | r = 97.55 mm from the origin, polar angle 60.5° → ring plane z ≈ +48.04 mm, ring radius 84.90 mm, stand-off 97.55 − 88 = 9.55 mm from the skin | `MODEL_CARD.md` Part 1–2 | REPORTED (arithmetic VERIFIED: 97.55·cos60.5° = 48.04, 97.55·sin60.5° = 84.90) |
| +X, −Y | Subject's left is +X; the subject faces −Y (nose at T1) | — | `prompts/07_lobe_analysis_prompt.md` §1.2 | REPORTED |
| S1 … S6 | Lobe sectors (lobe phantom only). Sk spans azimuth [−120° + 60°(k−1), −60° + 60°(k−1)], centred on Tk | S1 Frontal, S2 Temporal L, S3 Parietal L, S4 Occipital, S5 Parietal R, S6 Temporal R; "core" = hippocampus sphere | `prompts/07…` §1.2; `imaging/study_lobe.py`; `scripts/07_lobe.py:41` | VERIFIED (code labels) / REPORTED (geometry) |
| e_k | CSF expansion in sector k (mm). Inside sector k: gray 76 − e_k … 83 − e_k mm; white 25 … 76 − e_k mm | per design, see `00_inventory.md` §2 | `MODEL_CARD.md` 5.1; header variables `e_S1 … e_S6` | REPORTED; header values VERIFIED for Mild_lobe |
| r_hip | Hippocampus sphere radius (mm) | Normal 25, MCI 21.25, Mild 17.5, Moderate 12.5, Severe 7.5 | `MODEL_CARD.md` Part 1, 5.1 | REPORTED |
| t_CSF | CSF thickness of the uniform (v1/v2) phantom | t_CSF = 83.5 − r_gray (mm): Normal 0.5, Mild 12.95, Moderate 17.45, Severe 21.25 | `imaging/study_i3.py`; `results/imaging/report.md` §5.2 | VERIFIED (code) |
| mirror map | x → −x: T1, T4 fixed; T2↔T6, T3↔T5 | `MIRROR = [0,5,4,3,2,1]` | `scripts/07_lobe.py:44` | VERIFIED |
| 12 relabelings | The symmetry group of a 6-ring: 6 rotations × 2 reflections | `symmetry_transforms()` | `scripts/07_lobe.py:106` | VERIFIED |

**Plain-language path names (use these in every figure).**

| Ring distance k | Plain name | Example pairs | Number of ordered pairs |
|---|---|---|---|
| 0 | reflection (self-coupling, S_tt) | T1–T1 | 6 |
| 1 | neighbour path | T1–T2, T6–T1 | 12 |
| 2 | second-neighbour path | T1–T3, T2–T6 | 12 |
| 3 | opposite path | T1–T4, T2–T5, T3–T6 | 6 |

k(u, t) = min(|u − t| mod 6, 6 − |u − t| mod 6). Code: `src/adstage/ring.py:7`,
`src/adstage/features/metrics.py:68`. VERIFIED.

## 2. S-parameters and powers

| Symbol | Meaning | Formula | Source | Status |
|---|---|---|---|---|
| f | Frequency (Hz in code, GHz in text) | — | — | — |
| S_ut(f) | Complex scattering parameter: wave leaving antenna u when antenna t is driven (column t = driven antenna), ring order | `S[..., u, t]` | `metrics.py` docstring | VERIFIED |
| P_ut(f) | Path power (the "|S21|² path power") | P_ut = \|S_ut\|² | `metrics.py::power_spectra` | VERIFIED |
| R_t(f) | Reflected power of antenna t | R_t = \|S_tt\|² | same | VERIFIED |
| A_t(f) | Accepted power | A_t = 1 − \|S_tt\|² | same | VERIFIED |
| N_t(f) | Power **not returned to any port** ("absorbed power" in the reports) | N_t = 1 − Σ_u \|S_ut\|² = head absorption + radiation to the HFSS boundary + antenna/substrate loss. **Not head absorption alone.** | `metrics.py` docstring, M4 | VERIFIED |
| C_t(f) | Total coupled power out of antenna t | C_t = Σ_{u≠t} \|S_ut\|² | `power_spectra` key `C` | VERIFIED |
| ⟨X⟩_B | Band average over band B = [f_lo, f_hi] | ⟨X⟩_B = (1/(f_hi − f_lo)) ∫_B X df, trapezoid rule, X linearly interpolated at the band edges | `metrics.py::band_avg` | VERIFIED |
| P_f | Instrument noise-floor power per entry, estimated from the measurement itself | P_f = ½ · mean of \|S_ij − S_ji\|² over the weakest 50 % of (f, pair) points ranked by \|S_ij\|\|S_ji\| | `src/adstage/features/floor.py::floor_power` | VERIFIED |
| P̄_t^k | Floor-subtracted band power of the path from t to t+k | P̄_t^k = max(⟨\|S_{t+k,t}\|²⟩_B − P_f, 10⁻¹⁰) | `ring_features.py::path`, `floor.py::r31` | VERIFIED |
| c_k(f) | Ring mode (complex): mean of S over all pairs at ring distance k | c_k(f) = mean_t S(t, t+k) | `src/adstage/ring.py::ring_average`; `qc_report.md` | VERIFIED |
| dS | Difference spectrum of a stage from its reference | dS = S_stage − S_ref; reference = v2 Normal (`new_Healthy.s6p`) in the imaging study, Healthy_sliced in the lobe study | `results/imaging/report.md`; `lobe_report.md` §0 | REPORTED |
| ΔP_ij | Per-path change map (lobe study) | ΔP_ij = 10log10 BP_ij(stage) − 10log10 BP_ij(Healthy_sliced), BP = band power symmetrised over i↔j | `scripts/07_lobe.py::band_power` | VERIFIED |

## 3. The coupled-power features C1–C3 and the ratios R31, R21, R32

The code has **three** related definitions. They must not be mixed.

| Symbol (docs) | Code name | Definition | Used by | Status |
|---|---|---|---|---|
| C_k^view(t) | `M5.Ck` (per antenna view) | ½(⟨\|S_{t+k,t}\|²⟩_B + ⟨\|S_{t−k,t}\|²⟩_B) − P_f (floor-subtracted when `floor_subtract: true`), in dB per view; "ring mean" = arithmetic mean over t | `scripts/03_classify.py`, `classify.py::extract` | VERIFIED |
| C_k^ring | `k{K}_band` | 10log10 ⟨ mean over all pairs at distance k of \|S\|² − P_f ⟩_B (arithmetic mean over pairs, then band average) | `scripts/04_likelihood.py`, `ring_features.py::features` | VERIFIED |
| C_k^GM | inside `R31/R21/R32` | (Π_t P̄_t^k)^{1/6}, geometric mean over the six antennas of the floor-subtracted band powers | `ring_features.py`, `floor.py::r31`, `imaging/study_ratios.py` | VERIFIED |

**Ratios (dB, one value per complete 6-port measurement):**

R_ab = 10 log10( C_a^GM / C_b^GM ) = (10 / ln 10) · (1/6) Σ_t [ln P̄_t^a − ln P̄_t^b]

- **R31** = opposite ÷ neighbour; **R21** = second-neighbour ÷ neighbour; **R32** = opposite ÷ second-neighbour.
- R32 = R31 − R21 exactly, so {R31, R21, R32} has rank 2 (`scripts/04_likelihood.py` docstring; `results/04/report.md`). VERIFIED in code.
- **Gain invariance.** A per-port complex gain g_i multiplies S_ij by g_i g_j, so \|S_ij\|² by \|g_i\|²\|g_j\|². Each port occurs exactly twice in Π_t P̄_t^k for every k, so all \|g_i\| cancel in R_ab. Phase errors do not enter at all (only \|S\|² is used). Code argument: `floor.py` docstring; unit test `tests/test_touchstone.py::test_r31_cancels_per_port_gains_and_floor_estimate`. VERIFIED (the cancellation is exact only before floor subtraction; with P_f subtracted it is exact to the extent P_f ≪ path power).
- "M5.R31" (03 scripts) and "R31" (04, frozen rule) are the same quantity. The frozen rule computes it on 3.2–4.2 GHz with floor subtraction and glitch masking (`results/04/frozen_rule.json` `feature_spec`). VERIFIED.

## 4. Metric families M0–M9 (prompts 02–03)

All from `src/adstage/features/metrics.py::build_catalogue` and `src/adstage/pipeline/classify.py` docstring. VERIFIED.

| ID | Definition | Note recorded in the code |
|---|---|---|
| M0 | "old score": ⟨ Σ_{j≠i} \|S_ii + S_ij\| / VSWR_i ⟩_B, VSWR_i = (1+\|S_ii\|)/(1−\|S_ii\|) | not a physical quantity; in practice a reflection-only score |
| M1 | ⟨20 log10 \|S_ii\|⟩_B (dB averaging) | fragile, dominated by the notch |
| M2 | ⟨\|S_ii\|²⟩_B (power averaging) | — |
| M3 | ⟨1 − \|S_ii\|²⟩_B and mismatch loss −10log10⟨A⟩_B | affine copy of M2 |
| M4 | ⟨N_t⟩_B | ≈ 1 − M2 because coupled power is only ~4·10⁻⁴ of incident |
| M5 | C, C1, C2, C3 (coupled powers, see §3); `M5.C3` = headline opposite-path power; `[k3]` = 3.35–3.60 GHz window (chosen post hoc); `[nested]` = window chosen inside each training fold | — |
| M6 | power-weighted centroid f_c and spread of A(f), N(f); 50 MHz sub-band energies | resonance-tracking, solve-sensitive |
| M7 | differential energy ⟨Σ_j \|S_jt − S_ref,jt\|²⟩_B against a circulant Normal reference | reference is solve-specific |
| M8 | singular values s_k² of S; circulant modal powers \|λ_m\|², λ_m^(t) = Σ_k S(t+k,t) e^{−j2πmk/6} | duplicate the ring modes for a symmetric ring |
| M9 | full spectrum of one view: 20log10\|S(t+k,t)\| and cos/sin of the phase, k = 0…5 | upper bound; solve-specific |
| COMB | ≤ 3 scalars greedily chosen in the training fold (Fisher, \|corr\| < 0.9) | — |

Feature groups of prompt 04 (`scripts/04_likelihood.py`): **G_refl** (k = 0 sub-bands + band, N, logN; 23 features), **G_coup** (k = 1–3; 63), **G_ratio** (R31, R21, R32; 3), **G_all** (89). VERIFIED (counts from `results/04/report.md`, REPORTED).

## 5. Lobe-study asymmetry features

| Symbol (docs) | Code name | Definition | Source | Status |
|---|---|---|---|---|
| χ_{(ab·cd)/(ac·bd)} | `cross_ratios` | For antennas a<b<c<d the three pairings Π₁ = BP_ab BP_cd, Π₂ = BP_ac BP_bd, Π₃ = BP_ad BP_bc; χ = 10log10(Π_i/Π_j). 15 quadruples × 3 = 45 cross-ratios. Every antenna occurs once in every pairing, so per-port gains cancel exactly | `scripts/07_lobe.py:69`; test `tests/test_touchstone.py:193` | VERIFIED |
| χ̃ ("asymmetry cross-ratio") | `asym` | χ minus the (sign-adjusted) mean of its symmetry-equivalent copies; zero for any rotationally symmetric head; still gain-invariant | `scripts/07_lobe.py:373–379` | VERIFIED |
| I_FB, I_LR (path indices, dB) | `index` | I_FB = mean ΔP over transmission paths touching T1 but not T4 − mean over paths touching T4 but not T1. I_LR = paths touching {T2, T3} but not {T5, T6} minus the reverse. **Not** gain-invariant | `scripts/07_lobe.py:85–103` | VERIFIED |
| FB_inv, LR_inv (inversion contrasts, units of dε″) | `contrasts` | FB_inv = dε″(S1) − dε″(S4); LR_inv = mean(dε″(S2), dε″(S3)) − mean(dε″(S5), dε″(S6)) | `results/imaging/lobe_report.md` §5 | REPORTED |

**Notation collision to avoid:** the analysis session calls I_FB "front-back index" (dB of path power); the imaging session calls FB_inv "FB" (sector conductivity units). They are different quantities with different thresholds.

## 6. Noise model and perturbations

**Measurement noise** (`src/adstage/noise/model.py`, VERIFIED), applied per entry (f, i, j) independently:

S′ = S(f − δ) · 10^{g/20} · e^{jφ} + a,  g ~ N(0, σ_dB), φ ~ N(0, σ_deg), a ~ CN(0, 10^{L/10}), δ ~ N(0, σ_MHz) (one shift per realisation)

| Profile | σ_dB | σ_deg | floor L (dB) | jitter (MHz) |
|---|---|---|---|---|
| ideal | 0.05 | 0.5 | −90 | 0 |
| good | 0.1 | 1 | −80 | 0 |
| typical | 0.25 | 2 | −70 | 0 |
| noisy | 0.5 | 5 | −60 | 0 |
| very_noisy | 1.0 | 10 | −50 | 0 |
| typical_jitter | 0.25 | 2 | −70 | 3 |

**Setup perturbation** (`src/adstage/pipeline/augment.py`, VERIFIED), applied before the profile noise:
S_ij′ = g_i g_j S_ij(f − δ), g_i = (1 + ε_i) e^{jφ_i}, ε_i ~ N(0, 0.015), φ_i ~ N(0, 10°), δ ~ N(0, 1 MHz); optional per-port gain error G_i ~ U(−X, X) dB ("±X dB gain") and optional extra phase error U(−Y°, Y°) ("±10° phase").
Reciprocity is preserved by the setup perturbation, not by the profile noise.

**"Typical + ±0.5 dB gain"** = the standard noise condition of prompts 04, 05 (audit) and 07 (`results/04/report.md` header). VERIFIED in code paths, REPORTED as the condition used.

## 7. Statistics and methods

| Term | Definition as used here | Source | Status |
|---|---|---|---|
| Fisher ratio J (prompt 02) | J = (μ_a − μ_b)² / (σ_a² + σ_b²); **J_meas** uses measurement noise; **J_eff** adds the port-to-port SDs to the denominator | `src/adstage/separability.py` | VERIFIED |
| gap/port | \|Δμ\| / √(½(port_sd_a² + port_sd_b²)), port_sd = across-antenna SD (numerical asymmetry) | same | VERIFIED |
| Bhattacharyya distance B | 1-D: B = ⅛ Δμ²/v + ½ ln(v / √(v_a v_b)), v = ½(v_a + v_b). Multivariate (prompt 04): B = ⅛ Δμᵀ C̄⁻¹ Δμ + ½[ln\|C̄\| − ½ln\|C₁\| − ½ln\|C₂\|], C̄ = ½(C₁+C₂). Bayes error ≤ ½e^{−B} | `separability.py`; `scripts/04_likelihood.py:149` | VERIFIED |
| Symmetric KL divergence (prompt 04, called "J" there) | J_KL = ½[tr(C₂⁻¹C₁) + tr(C₁⁻¹C₂) − 2d] + ½ Δμᵀ(C₁⁻¹ + C₂⁻¹)Δμ | `scripts/04_likelihood.py:154` | VERIFIED |
| between-solve covariance Σ_b | From repeat pairs d/√2, variances shrunk toward their median, correlations toward 0 | `scripts/04_likelihood.py` docstring | VERIFIED (docstring) |
| solve-to-solve SD | σ_solve = √(mean over repeat pairs of d²/2), d = value(v1 solve) − value(v2 solve) | `src/adstage/noise/reference.py::mesh_sd`; audit §1 | VERIFIED |
| LDA / QDA | Linear / quadratic discriminant analysis (Gaussian class models; shared vs per-class covariance). Frozen staging rule: LDA, lsqr solver, Ledoit–Wolf shrinkage, equal priors | `results/04/frozen_rule.json` | VERIFIED |
| LOSO | Leave-one-solve-out: hold out every draw of one HFSS solve; fit on the others | `src/adstage/pipeline/cv.py` | VERIFIED |
| LODO | Leave-one-diameter-out: for a class with one simulation, hold out the antenna pair {t, t+3} together (reciprocity would otherwise leak the opposite path) | same | VERIFIED |
| validity labels | `noise-robustness-only` (some class has one solve) / `cross-solve-same-head` (≥ 2 solves per class, one head) / `generalisation-across-heads` (≥ 2 heads per class) | `cv.py::validity_label` | VERIFIED |
| balanced accuracy | mean of per-class recalls; in rule scoring UNCERTAIN counts as not correct | `src/adstage/pipeline/rule.py::score` | VERIFIED |
| τ, m | Decision threshold (class-balanced error minimiser) and UNCERTAIN margin m = max(m_post, Φ⁻¹(p*)·σ_ref), p* = 0.7 | `rule.py::fit_rule` | VERIFIED |
| p* | Reject threshold: UNCERTAIN if max posterior < 0.7 | `config.yaml` `classify.p_star` | VERIFIED |
| ECE | Expected calibration error of the max posterior (10 bins) | `scripts/04_likelihood.py::ece` | VERIFIED |
| MI | Mutual information between a feature and the stage, bits (max 2 for 4 stages); ranking key = 1-D Gaussian model including between-solve variance | `results/04/report.md` | REPORTED |
| permutation test | Exact enumeration of distinct partitions of stage labels over solves; p = fraction with balanced accuracy ≥ observed | audit §3 | REPORTED |
| CRLB | Cramér–Rao lower bound: SD bound from the inverse Fisher information of the whitened Jacobian | imaging report §5, lobe report §2 | REPORTED |
| Tikhonov / GCV / L-curve / TV / L1 | Regularised least squares; λ chosen by generalised cross-validation or L-curve; total-variation and sparsity variants | `imaging/linear.py` | VERIFIED (names) |
| κ(f) | Complex calibration factor that maps the Born prediction onto HFSS dS, fitted on Mild only, then frozen | `imaging/study_i2_hfss.py` docstring | VERIFIED |
| DAS / DMAS / MVDR | Delay-and-sum / delay-multiply-and-sum / minimum-variance distortionless-response beamformers | `imaging/beamform.py` docstring | VERIFIED |
| SCR | Signal-to-clutter ratio = stage image peak ÷ mean noise-only image peak (dB) | `imaging/study_i1.py` | VERIFIED |

## 8. EM and simulation terms

| Term | Meaning | Source | Status |
|---|---|---|---|
| ε_r, σ | Relative permittivity and conductivity (S/m); static (frequency-independent) in HFSS | `MODEL_CARD.md` Part 1 | REPORTED |
| ε″ | Imaginary part of the complex relative permittivity, ε″ = σ/(ωε₀); dε = dε_r − j dε″ (HFSS e^{+jωt} convention) | `imaging/linear.py`, `study_i2_hfss.py` | VERIFIED |
| Born sensitivity | dS_ij(f) = −(jωε₀Z₀ / 4V²) ∫ dε(r) E_i(r)·E_j(r) dV, all ports 1 V incident, 50 Ω | `imaging/study_i2_hfss.py` docstring | VERIFIED |
| ΔS adaptive convergence ("Max Delta S") | HFSS adaptive meshing stops when the max change of any S-parameter magnitude between successive passes is below the target | `MODEL_CARD.md` Part 2, 5.2 | REPORTED (standard HFSS meaning) |
| passes, tets/elements | Adaptive passes; tetrahedral mesh elements | same | REPORTED |
| interpolating vs discrete sweep | HFSS frequency-sweep types; S-parameter files used interpolating sweeps; field exports used a 3-point discrete sweep | `MODEL_CARD.md` Part 2 | REPORTED |
| solve / repeat | One HFSS solution of a design. v1 and v2 solves of the same design are treated as repeats (role `mesh_repeat` in `data/sims_with_repeats.csv`), although they differ in **sweep** settings only (see §9) | `data/sims_with_repeats.csv` | VERIFIED |
| glitch | (f, i, j) point with \|S_ij − S_ji\| > 10^{−30/20} × band-rms level of the pair; masked by complex linear interpolation | `src/adstage/io/masking.py` | VERIFIED |
| header policy | Touchstone `!` comment lines are kept but never interpreted; labels from `data/sims*.csv`, ports from `config.yaml` | `src/adstage/io/touchstone.py` docstring | VERIFIED |
| INVALID / UNCERTAIN | Gate failure (with reason) / decision within margin of τ or posterior < p* | `rule.py`, `quality.py` | VERIFIED |

## 9. Inconsistencies in terms found in the repo (do not propagate)

1. **"mesh repeat" vs "sweep repeat".** `data/sims_with_repeats.csv` marks the v1 solves `role = mesh_repeat`, and `results/v2_with_v1_repeats/03/decision_rule.md` prints "noise reference = mesh". The user stated (2026-10-01) that only the **sweep** settings changed, and `MODEL_CARD.md` Part 2 says the pairs "very likely share meshes". In the docs I call this the **solve-to-solve SD (sweep repeats)**, never "mesh noise".
2. **C_k** has three definitions (§3). Write C_k^view, C_k^ring, C_k^GM.
3. **"J"** = Fisher ratio in prompt 02, but symmetric KL divergence in prompt 04. In the docs: J_F (Fisher) and J_KL.
4. **"front-back index"** = path-power index I_FB (dB) in `results/05_lobe/`, but sector contrast FB_inv (dε″) in `results/imaging/lobe_report.md` (§5 above).
5. **"absorbed power"** (N) is not head absorption (§2).
6. **k = 3 group delay numbers**: `MODEL_CARD.md` caveat 5 and `results/STATUS.md` §2 quote 3.61 ns measured / 3.69 ns creeping / 6.03 ns straight. These are the **v1-data** values (`git show 935f26d:results/imaging/report.md` §1). The current v2 report gives 3.11 / 2.97 / 5.31 ns (`results/imaging/report.md` §1). The conclusion is the same; the numbers in MODEL_CARD and STATUS are stale.

## 10. Running glossary (plain words)

- **Phantom**: a simulated head model with assigned tissue properties.
- **Stage**: Normal (healthy), MCI (mild cognitive impairment), Mild, Moderate, Severe AD.
- **Uniform (spherical) atrophy**: every disease change is the same in all directions (v1/v2 sphere).
- **Regional (lobe) atrophy**: disease applied only in selected 60° sectors (lobe phantom).
- **Within-simulation noise robustness**: the classifier is tested on new noisy copies of the *same* simulated file(s). It says nothing about other heads.
- **Cross-solve (same head)**: trained on one HFSS solve, tested on another solve of the same design. Still one head geometry.
- **Generalisation**: tested on heads (geometries) not used in training. **Never achieved in this repo.**
- **Frozen rule**: a decision rule saved to a file with its commit hash and applied unchanged to new data (`results/04/frozen_rule.json`, `results/imaging/lobe_frozen.json`).
- **Pre-registration**: predictions written and committed before the test data exist (`results/05_lobe/predictions.md` at `cf56de8`; `results/imaging/lobe_predictions.md` at `62709e0`).
- **Mesh yardstick / mesh scale**: the difference between two healthy heads solved on different meshes (v2 Normal vs Healthy_sliced), used as a rough ruler for "could the mesh alone do this?".
