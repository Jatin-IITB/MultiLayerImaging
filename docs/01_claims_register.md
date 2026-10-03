# 01 — Claims register (Phase 0)

Written 2026-10-03 at HEAD `ecacd35`. Every claim found in `MODEL_CARD.md`, `results/STATUS.md`,
`results/04/audit/report.md`, `results/05_lobe/` and (because they belong to the same stages)
`results/04/report.md`, `results/imaging/report.md` §6 and `results/imaging/lobe_report.md` §7.

**Columns.**
- *Status* = the label the analysis sessions gave the claim: **holds / weakened / retracted / not testable / requirement / pending / fact**. I keep their label unchanged. Where I think a label is out of date, I add it in *Caveats*, not in *Status*.
- *Evidence* = VERIFIED (I recomputed or saw it in data/code), REPORTED (stated in the file, not re-checked).
- *Validity class* = what kind of evidence it is: **NR** = within-simulation noise robustness (one solve per class); **XS** = cross-solve, same head (train on one HFSS solve, test on another; v1↔v2 differ in sweep settings only); **PHY** = physics/forward-model argument; **GEO** = geometry/settings fact. **No claim in this repo is generalisation to other heads.**

**My own check (2026-10-03).** Clean-data R31/R21/R32 recomputed from the raw `.s6p` files with `src/adstage/features/ring_features.ratios` (3.2–4.2 GHz, glitch masking −30 dB). They match `results/04/audit/report.md` §4 and `results/05_lobe/report.md` §3.3 to ≤ 0.01 dB:

| solve | R31 | R21 | R32 |
|---|---|---|---|
| v1 Normal / v2 Normal / v2 MCI | −14.479 / −14.674 / −14.614 | −20.395 / −20.722 / −20.685 | 5.916 / 6.048 / 6.071 |
| v1 / v2 Mild | −16.195 / −16.058 | −19.308 / −19.479 | 3.113 / 3.421 |
| v1 / v2 Moderate | −16.505 / −16.168 | −19.768 / −19.526 | 3.263 / 3.358 |
| v1 / v2 Severe | −15.850 / −15.851 | −18.165 / −18.058 | 2.315 / 2.208 |
| Healthy_sliced / Mild_lobe / Moderate_lobe / Severe_lobe | −14.609 / −15.822 / −16.008 / −15.533 | −20.507 / −19.974 / −19.451 / −18.002 | 5.898 / 4.152 / 3.443 / 2.469 |

From these: Normal-vs-AD R31 gap = −14.577 − (−16.105) = **1.53 dB**; R31 solve SD from the 4 pairs = **0.146 dB** (audit: 0.148 with noisy means). Claims that rest only on these numbers are marked VERIFIED below.

---

## A. Data, geometry and settings (facts)

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| A1 | Port order is Port 1…6 = T4, T3, T2, T1, T6, T5; ports in file order are consecutive around the ring | rank 1 of 60 orderings in every v1, v2, lobe file; v1 error 0.36–0.64 vs next 1.71–2.18 dB | `MODEL_CARD.md` Part 2 VERIFY; `results/qc/qc_report.md`; `results/05_lobe/qc/qc_report.md` | fact (supported by data) | REPORTED (headers also say `Port[1] = FEED_3_T4 …`, VERIFIED) | S-parameters cannot distinguish a ring from its mirror; direction fixed by field exports |
| A2 | Ring at +z, T1 at azimuth −90°, T1…T6 at +60° steps | centroids −90.5, −31.0, 29.6, 89.4, 148.9, −150.4°; polar ≈ 55° | `MODEL_CARD.md` Part 4; `results/imaging/report.md` §4.0 | fact (settled) | REPORTED | Based on Normal v2 fields only |
| A3 | Antenna near field is mixed polarised | ≈ 65 % θ / 35 % φ | same | fact | REPORTED | Invalidates the pure-φ point-dipole model |
| A4 | Field-level ring symmetry | 11.4–15.8 % rms; T1 1.044, T4 1.046 vs 0.97–0.98 others at 3.6 GHz | same | fact | REPORTED | Why are T1/T4 stronger? UNKNOWN |
| A5 | v1 was solved in two HFSS projects (Normal, Severe in `new`; Mild, Moderate in `Brain_sevem_layer`); v1 Severe covers 3.2–4.2 GHz at 2 MHz | — | `MODEL_CARD.md` Part 1; headers | fact | VERIFIED (headers + parse) | Common band for any v1 use = 3.2–4.2 GHz |
| A6 | v2: all five stages in one project `new`, 2.8–4.2 GHz, 281 pts | — | `data/sims.csv`; headers | fact | VERIFIED | — |
| A7 | v1 and v2 solves of a stage differ only in sweep settings | — | `data/sims_with_repeats.csv` header (user, 2026-10-01) | fact (user-stated) | REPORTED | Contradicted in part by A5: v1 Mild/Moderate came from a **different project**. What else differed is UNKNOWN |
| A8 | v1/v2 repeat pairs very likely share meshes, so the solve-to-solve SD is a sweep spread and mesh error is unmeasured | — | `MODEL_CARD.md` Part 2 | fact (inference) | REPORTED | Hard to reconcile with A7/A5 for Mild/Moderate (different project) |
| A9 | **v2 mesh settings differ by class**: Max ΔS 0.02 for Normal/MCI vs 0.05 for Mild/Moderate/Severe; Normal did not converge | see `00_inventory.md` §2 | `MODEL_CARD.md` Part 2 | fact (user, HFSS dialogs) | REPORTED | Aligns with the Normal-vs-AD split → mesh confound cannot be excluded for every v2 result |
| A10 | lobe_v1 mesh settings NOT matched: Healthy_sliced 1,349,491 elements, ΔS 0.0092, min converged passes 2; AD stages 0.69–0.80 M, ΔS ≈ 0.019–0.020, min passes 1 | ~1.8× elements, ~2× tighter ΔS | `data/mesh_lobe.csv`; `MODEL_CARD.md` 5.2 | fact | REPORTED | Prompt 07's "identical mesh settings" is retracted (see E9) |
| A11 | Healthy material values in the HFSS material table equal the stated values; static, tan δ 0 | 47.7/2.42, 35.3/1.65, 47.7/2.42, 65/4.27 | `MODEL_CARD.md` 5.2 | fact (VERIFIED in HFSS by user) | REPORTED | Lobe project only; v2 Normal materials remain OPEN-GUI |
| A12 | Materials are static (no dispersion) | — | `MODEL_CARD.md` Part 1 | fact | REPORTED | Any frequency-dependence claim concerns the simulation, not tissue |
| A13 | Normal-stage materials are back-calculated from Shehab's % change columns | — | `MODEL_CARD.md` Part 1 | fact | REPORTED | Not re-checked against the PDF |
| A14 | v2 resonances (mean of per-port min \|S_ii\|) | Normal 3640.3, MCI 3655.5, Mild 3654.2, Moderate 3647.3, Severe 3648.2 MHz; not monotone | `MODEL_CARD.md` Part 3; `results/qc/qc_report.md` | fact | REPORTED | — |
| A15 | Re-solve alone moved Normal's resonance | 16 MHz (3623.9 → 3640.3) | `MODEL_CARD.md` caveat 4, Part 3 | fact | REPORTED | Hence notch depth and resonance are never used as features |
| A16 | v2 data nearly glitch-free; v1 had 26 masked points | v2: 1 (Normal) + 6 (Severe) masked | `MODEL_CARD.md` Part 3; `results/summary.md` | fact | REPORTED | — |
| A17 | v2 symmetry floor is 2–3× lower than v1 | rms across-antenna SD: e.g. k3 0.15–0.32 dB v2 | `MODEL_CARD.md` Part 3 | fact | REPORTED | — |
| A18 | Healthy_sliced is more symmetric than v2 Normal | circulant floor 0.003 / 0.028 / 0.095 / 0.054 dB | `results/05_lobe/report.md` §3.1 | fact | REPORTED | Staged lobe designs are 2–5× less symmetric (mirror floor 0.007/0.080/0.149/0.063) |

## B. Signal path physics

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| B1 | The opposite-path (k = 3) signal travels **around** the head in air, not through it (delay test) | v2: measured 3.11 ns, creeping 2.97 ns, straight 5.31 ns | `results/imaging/report.md` §1 | holds (PHY) | REPORTED | **MODEL_CARD caveat 5 and STATUS §2 quote 3.61 / 3.69 / 6.03 ns = the v1 numbers** (`git show 935f26d`). Same conclusion, stale numbers |
| B2 | Same, from HFSS fields | 99 % of T1–T4 Born sensitivity in air, 0.3 % in brain; half-way −33 dB (arc) vs −57 dB (chord); 73 % of the in-brain part within 13.5 mm of the brain surface | `MODEL_CARD.md` Part 4; imaging §4.3 | holds (PHY) | REPORTED | Field-sampling limits (3–4 mm grid) |
| B3 | The array senses only the outer ~1–1.5 cm of brain, only near an antenna | SNR ≥ 1 for a 1 cm³, \|dε\| = 10 blob down to r ≈ 83 mm (absolute) / 69 mm (κ-calibrated); median direction ≤ 0.21 / 0.89 | STATUS §2; imaging §4.2 | holds (PHY) | REPORTED | κ-calibrated values are an upper bound (include 3.8 GHz where Born fails) |
| B4 | Hippocampus (central) is invisible | MCI Born dS = 1.0·10⁻⁴ of the solve-to-solve difference; core CRLB ≫ change | imaging §4.7(5), lobe §2 | holds (PHY) | REPORTED | — |
| B5 | R21 is not specifically a CSF probe: in-head kernel 77 % skin/fat + first 1.75 mm of air | — | imaging §4.7(3) | holds (PHY) | REPORTED | Implies sensitivity to stand-off and head size (B6) |
| B6 | Setup changes move R21 as much as disease, or more | first-order ΔR21 up to 11.4 dB for ±1 mm stand-off / ±2 % scale (9.3× the Severe−Mild gap) | imaging §4.7(4) | holds as order of magnitude only (PHY) | REPORTED | Born slopes at skin↔air contrast; **needs HFSS re-solve** to be a number |
| B7 | CSF permittivity drop at Severe drives Severe's R21 separation (linear level) | 94 % of predicted Severe−Mild gap removed with Mild CSF material | imaging §4.7(2) | holds at linear level only | REPORTED | Decisive test (HFSS re-solve of Severe with Mild CSF) not done |
| B8 | Point-dipole layered-sphere forward model fails validation beyond the neighbour path | calB beats the trivial predictor in 0 of 8 cases; k3 amplitude error 1.4× | imaging §3 | holds (negative result) | REPORTED | Mismatch is in the antenna model, not the head |

## C. Detection: Normal vs AD (uniform sphere)

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| C1 | R31 separates Normal from AD on the unseen solve | τ = −15.27 dB (95 % CI −15.37 to −15.17), m = 0.08 dB; sens 1.00, spec 1.00, 0 % UNCERTAIN | STATUS §1; `results/v2_with_v1_repeats/03/decision_rule.md`; `frozen_rule.json` | holds (XS) | τ, m VERIFIED in `frozen_rule.json`; scores REPORTED | One head; Normal test draws are noise copies; v2 mesh confound (A9) |
| C2 | R31 gap ≈ 10× solve-to-solve noise | gap 1.53 dB, solve SD 0.15 dB; t = −12.7 (4 pairs, p = 2.3·10⁻⁴), t = −10.2 (2 pairs, p = 0.0095) | STATUS §1; audit §1, claims | holds (XS) | gap and SD VERIFIED (my recompute 1.53, 0.146) | SD from 4 pairs: 95 % CI 0.089–0.425 dB → gap/SD 3.6–17; "solve" = sweep repeat, not mesh |
| C3 | Full-band opposite-path power M5.C3 separates Normal vs AD | τ = −52.72 dB (CI −52.83 to −52.51), m = 0.24 dB; gap 1.83 dB ≈ 7× SD 0.31 dB; sens/spec 1.00 (6-view vote) | STATUS §1; decision_rule.md | holds (XS) | REPORTED | Requires per-port calibration (C4) |
| C4 | R31 needs no per-antenna calibration; M5.C3 does | ±2 dB gain: R31 1.00/1.00; M5.C3 vote 0.60/0.77 (gain-invariant gate) | STATUS §1; decision_rule.md table | holds (XS) | REPORTED (table seen); cancellation VERIFIED in code + unit test | Phase errors irrelevant to \|S\|²-only features |
| C5 | R31 threshold stable across solve sets | −15.17, −15.14, −15.27 dB (within 0.13 dB) | STATUS §1; summary | holds | REPORTED | — |
| C6 | Instrument floor must be ≥ 8 dB below τ (≈ −61 dB) or INVALID | floor gate | STATUS §1; `pipeline/quality.py` | requirement | VERIFIED (code) | Margin 8 dB is a design choice |
| C7 | Gate catches 100 % of single open/short antennas and ±200 MHz detuning, 0 % false rejects (gain-invariant mode) | — | summary (Prompt 03 follow-ups) | holds (NR) | REPORTED | Thresholds were set by looking at these same simulations |
| C8 | Reflection metrics (\|S11\|-type) fail on the unseen solve | balanced accuracy 0.45–0.56; Normal–AD change ~1–2 % | STATUS §3 | holds (negative) | REPORTED | — |
| C9 | Old score Σ\|Sii+Sij\|/VSWR is a reflection measure; 0.62 on unseen solve | — | STATUS §3; `metrics.py` M0 note | holds (negative) | REPORTED; M0 definition VERIFIED | — |
| C10 | Spectral-shape features partly learn the solve | 2 solves of a design differ 0.9–1.5 dB (k3) in shape; staging accuracy 0.93 ↔ 0.37 depending on classifier | STATUS §3; `results/qc/solve_comparison.md` | holds (negative) | REPORTED | — |
| C11 | Most apparent information in high-dimensional groups is solve-specific | G_all keeps 9 % of Bhattacharyya distance (1280 → 119) once the between-solve term is added; G_all QDA meas-only collapses to 0.57 (binary), 0.24 (three) | `results/04/report.md`; summary | holds | REPORTED | — |
| C12 | Detection does not gain from using all features | R31 alone 1.00 LOSO; C3 0.99 | `results/04/report.md` | holds (XS) | REPORTED | — |

## D. Staging (uniform sphere)

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| D1 | R21 separates Mild vs Severe beyond solve noise | gap +1.28 dB; t = 8.1 (4 pairs, p = 0.0013); t = 8.7 (2 pairs, p = 0.013) | audit claims | holds (XS) | gap VERIFIED (−19.394 vs −18.112 → 1.28) | 4 repeat pairs; one head; v2 mesh confound (A9); falsification tests §7 pending |
| D2 | R32 separates Mild vs Severe beyond solve noise | gap −1.00 dB; t = −7.8 (p = 0.0014); t = −6.2 (p = 0.025) | audit claims | holds (XS) | gap VERIFIED | same |
| D3 | R21 Normal vs AD beyond solve noise | +1.51 dB; t = 12.6, p = 0.0062 (2-pair SD) | audit claims | holds (XS) | REPORTED | — |
| D4 | Mild vs Moderate separable | R32 gap +0.04 dB, t = 0.26 | audit claims | not supported (no claim made) | VERIFIED (3.267 vs 3.311) | — |
| D5 | 3-class staging survives feature selection inside the folds | nested LOSO bal. acc 1.000; ratios-only chosen in 6/6 folds | audit §2 | holds (XS) | REPORTED | — |
| D6 | `three` result not achievable by arbitrary solve groupings | exact p = 0.133 (2/15); smallest attainable 0.0667 | audit §3 | cannot reach p < 0.05 with these solves | REPORTED | Important limit to state to the professor |
| D7 | `three_merged` not achievable by arbitrary groupings | p = 0.005 (1/210) | audit §3 | holds | REPORTED | — |
| D8 | Band robustness of R21/R32 (Mild vs Severe) | 3.2–4.2 holds; R21 3.2–3.6 and 3.6–4.2 **retracted**; R32 3.6–4.2 **weakened**; R21 2.8–3.2 **weakened**; R32 3.2–3.6, minus-nulls, 2.8–3.2 hold; R21 minus-nulls holds | audit §5, claims | mixed as listed | REPORTED | R21 depends on the full band |
| D9 | Staging survives ±2 dB gain + ±10° phase per port, and a −60 dB floor | 3-class bal. acc 1.000; R21 gap/noise 29.8 and 8.9 | audit §6 | holds (NR) | REPORTED | — |
| D10 | Minimum instrument floor for the R21 rule | ≤ −55.0 dB (C2 level −56.8 dB) | audit §6 | requirement | REPORTED | — |
| D11 | Ratios are not monotone over the stages | R31: Normal→Mild −1.55, Mild→Mod −0.21, Mod→Sev +0.49 dB; R21 not monotone; R32 monotone only ignoring steps < 1 SD | audit §4 | fact | VERIFIED (from my table) | R31 is a binary feature only |
| D12 | **Staging lead M5.C2** separates Mild from Severe by 3.6–3.9× the solve noise; opposite path 0.55×; four coupled-power features 0.96 bal. acc (Normal/Mild/Severe) | — | STATUS §4; summary (v2 cross-solve) | "preliminary" | REPORTED | **Superseded in the analysis chain by the R21/R32 ratio lead (audit, frozen rule) but STATUS §4 still presents M5.C2.** Needs your decision which is the headline |
| D13 | Moderate not separable from Mild | 0.9× (M5.C2), 0.5× (M5.C3) | STATUS §4 | holds | REPORTED | — |
| D14 | Linear theory reproduces "Severe separates, Mild ≈ Moderate" for R21 qualitatively | predicted Sev−Mild +0.57 dB vs HFSS +1.22 (47 %) | imaging §4.7(1) | holds qualitatively (PHY) | REPORTED | R31, R32 (contain C3) not reproduced |
| D15 | Full-spectrum (imaging) stage separation is not supported | whitened AD-vs-AD 70–246 vs 517 between two solves of Normal | imaging §6 Cannot-6 | holds (negative) | REPORTED | — |

## E. MCI

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| E1 | MCI ≈ Normal on the robust features | R31 +0.06 dB vs solve SD 0.15 dB (gap/SD 0.22–0.27); C3 +0.23 dB | STATUS §3; MODEL_CARD Part 3; audit §1 | holds (no detection claim) | R31 diff VERIFIED (0.060) | Only one MCI solve |
| E2 | Spectral-shape classifiers score 100 % for MCI but likely fingerprint the file | M6 around 3.40–3.60 GHz; resonance moves ±16 MHz between solves | STATUS §3; summary | not testable yet (needs second MCI solve) | REPORTED | — |
| E3 | MCI differs from Normal far above measurement noise, but by the size of solve-to-solve variation | matched-filter SNR 480 vs 517 (two Normal solves); Born prediction of true change SNR 0.015 | imaging §6.1 | holds: "undetectable against the relevant floor" | REPORTED | v2 MCI hippocampus material UNKNOWN (open question) |

## F. Imaging and localisation (uniform sphere)

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| F1 | Radar focusing (DAS/DMAS/MVDR) puts every change at the head centre | peak r = 1–11 mm | STATUS §3; imaging §2 | holds (negative) | REPORTED | Symmetric-ring artefact; depth also set by unknown t_ant |
| F2 | DAS/DMAS detect "a change" 22–29 dB above noise, not disease-specifically | MCI 26–29 dB as well | imaging §6 Can-1 | holds | REPORTED | — |
| F3 | Linear inversion with HFSS fields predicts only part of the signal and resolves depth only in the outer ~1 cm | Born/HFSS 0.11–0.44; resolution diagonal ≥ 0.5 only at r ≥ 75 mm | STATUS §3 ("11–44 %"); imaging §4.1, §4.4 | holds (negative) | REPORTED | — |
| F4 | Voxel inversion fails; deep voxels imaged toward the surface | r = 20 → peak 64 mm away … r = 80 → 6 mm | imaging §4.5 | holds (negative) | REPORTED | — |
| F5 | CSF thickness, gray/white radii, hippocampus size not identifiable (I3) | CRLB > prior range; only ε_CSF, σ_CSF determined; HFSS fits χ²/dof 10–25 | imaging §5 | holds (negative) | REPORTED | — |
| F6 | No imaging method beat the k = 3 band-averaged power for Normal vs AD | — | imaging §6 | holds | REPORTED | — |

## G. Lobe-sector phantom: analysis session (`results/05_lobe/`)

All NR (one solve per design) and **mesh-unmatched** (A10).

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| G1 | Healthy_sliced reproduces the v2 healthy head on classifier features | R31 +0.065 (0.4 SD), R21 +0.215 (1.3 SD), R32 −0.150 (1.2 SD); 93 % of 89 features within 3 SD; resonance +19 MHz, notch shallower | `results/05_lobe/report.md` §3.2, claims | holds | ratio diffs VERIFIED | Two different meshes and possibly skull radius; this pair is also the "mesh yardstick" |
| G2 | Frozen R31 rule labels Healthy_sliced Normal and all three lobe stages AD, 300 draws, typical ±0.5 dB and ±2 dB/±10° | 1.00 correct, 0 UNCERTAIN, 0 INVALID | §3.3, claims | holds | margins from τ VERIFIED (+0.66, −0.55, −0.74, −0.26 dB) | Not evidence of mesh independence (E9); Severe_lobe only 0.26 dB past τ |
| G3 | Frozen `three` (R21) labels Mild_lobe as Mild | 0.41 (typical), 0.43 (±2 dB) correct; 0.43 / 0.38 Normal; 16–19 % UNCERTAIN | §3.3 | **retracted** | REPORTED; R21 −19.974 vs boundary −19.98 VERIFIED | Regional Mild gives about half the uniform Mild R21 change |
| G4 | Frozen `three` labels Severe_lobe Severe; `three_merged` (R32) labels all lobe stages correctly | 1.00 | §3.3 | holds | REPORTED | — |
| G5 | R21 and R32 order the lobe stages monotonically | — | §3.3 | holds | VERIFIED (my table) | R31 not monotone |
| G6 | Front-lobe involvement visible front-to-back on neighbour paths (Moderate) | I_FB = −0.21 dB = 2.6× floor clean; 0.4× with ±0.5 dB gains; 1.2× the mesh scale | §3.4(b), mesh scale | clean: **weakened**; with gain errors: **retracted**; not separable from mesh | REPORTED | — |
| G7 | Front-back on all paths | +0.07 dB = 0.8× floor | §3.4(b) | **retracted** | REPORTED | — |
| G8 | Raw cross-ratios separate Moderate from Mild | 24/45 ≥ 3 SD; best −1.80 dB (15.9 SD) | §3.4(c) | holds **as severity, not location** | REPORTED | Raw χ mix path distances |
| G9 | Gain-invariant asymmetry cross-ratios see front-lobe involvement | 0/45 ≥ 3 SD; best −0.69 dB (2.3 SD); 7 of top 8 involve T1 | §3.4(c) | **not significant**; not separable from mesh (1.9× mesh scale) | REPORTED | — |
| G10 | Left-right index ≈ 0 for mirror-symmetric designs (check) | +0.084, −0.025, −0.034 dB (≤ 1.2× floor) | claims | check passes | REPORTED | — |
| G11 | Left-right asymmetry detectable | prediction I_LR = +0.232 dB (3.3× floor) | `predictions.md` | **not testable yet** (LeftOnly_test pending; pre-registered `cf56de8`) | REPORTED | Predictions ignore CSF_Mild on the right side (MODEL_CARD 5.2); only measurable on clean data |
| G12 | MCI_lobe indistinguishable from Healthy_sliced | — | MODEL_CARD 5.4 | **not testable yet** | — | — |
| G13 | "Identical mesh settings across lobe stages, hence 100 % detection is mesh-independent" | — | MODEL_CARD 5.4 | **retracted** | REPORTED | — |
| G14 | Mesh scale (Healthy_sliced vs v2 Normal) | R31 0.065, R21 0.215, R32 0.150 dB; neighbour path 0.234 dB rms; I_FB 0.173 dB; χ̃ 0.365 dB rms | §mesh scale | ruler (one pair; rough) | REPORTED | Two fine meshes; AD meshes coarser → multiples optimistic |
| G15 | Detection effects exceed the mesh scale | R31 healthy→Mild/Mod/Sev −1.21/−1.40/−0.92 dB = 19/22/14× | §mesh scale | holds (exceeds ≥ 5×) | REPORTED | 4–7× the largest ratio scale |
| G16 | Detection margin of Severe_lobe | −0.26 dB from τ = 4.0× own scale, 1.2× largest | §mesh scale | **mesh-sensitive** | VERIFIED (−0.26) | Re-solve `Severe_lobe_m2` running |
| G17 | Staging effects vs mesh | R21 healthy→Mild_lobe +0.53 dB = 2.5× (mesh-sensitive); R32 −1.75 dB = 11.6× (exceeds); Severe 11.7× / 22.9× | §mesh scale | as listed | REPORTED | — |
| G18 | Localisation effects vs mesh | 1.2–1.9× | §mesh scale | **not separable from mesh** until lobe_v1m | REPORTED | — |

## H. Lobe-sector phantom: imaging session (`results/imaging/lobe_report.md`)

| # | Claim | Number(s) | Evidence path | Status | Evidence | Caveats |
|---|---|---|---|---|---|---|
| H1 | All six sectors are distinguishable in pair space; core is not | largest kernel cosine 0.44; condition number 2.6 (6 sectors), 75 (with core); core singular values 0.014, 0.013 | §1 | holds (PHY) | REPORTED | Born kernels from **unsliced** v2 fields |
| H2 | Affected-sector conductivity is determined (CRLB < ½ change) in every affected sector, with and without gain errors | — | §2 | holds (PHY) | REPORTED | — |
| H3 | Deeper cortex (60–76 mm) not determined in any sector; under-skull gap only where listed | deep CRLB 2–3× gap CRLB | §2 | holds (negative) | REPORTED | "Ring sees outermost ~8 mm" |
| H4 | Pattern of affected lobes recovered as a ranking | corr with truth 0.90–0.95 (Mild/Moderate), top-k 1.00 all methods | §3 | holds (NR) | REPORTED | Absolute level biased (healthy sectors 6–11 vs 0.3); thresholds tuned on Mild |
| H5 | AD does not only lower ε_r; conductivity (ε″) rises in every affected sector, so calls use dε″ | Mild dε_r +7.4 (CSF ε 55.25 > gray 47.7) | §0 | fact (PHY) | REPORTED | dε_r recovered with the wrong sign for Mild/Moderate |
| H6 | Front/back for Moderate: frontal above occipital | FB_inv +10.1 > T_FB 6.45 (primary); all 4 methods "front" | §3 | holds on clean data, but **not separable from mesh** (mesh alone \|FB\| up to 9.4) | REPORTED | §5b |
| H7 | Radar imaging does not localise lobes | global max at centre in 5/6 images; resultant ≤ 0.038 | §4 | holds (negative) | REPORTED | — |
| H8 | Mesh difference alone lifts every sector above T_abs | dε″ 15–35; norm 2.9× Mild's dS | §5b | holds | REPORTED | Absolute 'affected' calls not mesh-robust |
| H9 | LeftOnly_test: side = left, S3 affected, S2 mostly, others healthy | LR_inv +14.7 ± 2.2 (primary); mesh alone \|LR\| up to 6.7 | `lobe_predictions.md` | **pending** (pre-registered `62709e0`) | REPORTED | Must also be > 6.7 to beat mesh |
| H10 | MCI_lobe: nothing called | p(any called) 0.00 | `lobe_predictions.md` | **pending** | REPORTED | — |
| H11 | Linear model explains only a quarter to a third of dS size | Born/HFSS 0.23–0.35; κ ≈ 3 | §0, §7 | fact | REPORTED | — |

## I. Pre-registered tests that are fixed but not yet run

| # | Test | Retraction criteria | Source |
|---|---|---|---|
| I1 | Equal-settings re-solves of all five v2 designs (ΔS 0.01, 10–12 passes, converged) | Detection retracted if any re-solved AD → Normal or Normal → AD in > 5 % of measurements, or R31 gap < 0.75 dB. Staging retracted per audit §7 items 1–2 or Mild–Severe gap < 0.5 dB in R21 or R32. "Normal ≈ MCI" kept only if differences < 2× solve SD | `MODEL_CARD.md` Part 4 |
| I2 | Audit falsification criteria 1–5 (Normal mesh repeat; Mild/Severe finer mesh; second head geometry; stand-off ±2 mm; second MCI solve) | see audit §7 | `results/04/audit/report.md` §7 |
| I3 | LeftOnly_test and MCI_lobe (analysis + imaging predictions) | scoring rules fixed in the two predictions files | `results/05_lobe/predictions.md`, `results/imaging/lobe_predictions.md` |
| I4 | lobe_v1m mesh-matched re-solves | v1 vs v1m difference measures the mesh effect | `MODEL_CARD.md` 5.5 |

## J. Claims from the pre-repo presentation (S0) — REPORTED only, outside the repo's evidence

| # | Claim | Number(s) | Evidence path | Status | Caveats |
|---|---|---|---|---|---|
| J1 | Single-material sphere, 8 antennas: 4 of 5 blind cases correctly localised (correct or partial) | 4/5; baseline method 3/5 | `blind_validation_presentation.pptx` slides 6, 9, 11 | UNKNOWN (no data in repo) | Slide 6 says 4/5, slide 11 baseline 3/5: which method gave 4/5? |
| J2 | "8 antennas with ~16 mm range resolution can stage AD severity at the sector level" | ~16 mm | slide 9 | UNKNOWN | Conflicts in spirit with later findings (no depth/lobe localisation in the layered phantom); needs Pack 01 |
| J3 | Dominant error is a multiplicative per-port gain (~10× on Port 5), not additive clutter | 2.76× estimated vs ~10× "ground truth" | slides 12–13 | UNKNOWN | Motivates the later gain-invariant features (R31, χ) — worth stating in the report if Pack 01 confirms |

## K. Contradictions and stale statements found (Phase 0)

1. **k = 3 delays** (B1): MODEL_CARD caveat 5 and STATUS §2 use v1 numbers (3.61/3.69/6.03 ns); current v2 report 3.11/2.97/5.31 ns.
2. **Staging headline** (D12): STATUS §4 names M5.C2; the audit and frozen rule use R21/R32. STATUS §4 was written before the audit.
3. **"Sweep only" vs different project** (A7, A8): v1 Mild/Moderate came from project `Brain_sevem_layer`, yet the repeats are described as differing only in sweep settings and "very likely sharing meshes".
4. **Repeat role label**: v1 solves are `mesh_repeat` in `data/sims_with_repeats.csv`; decision_rule.md prints "noise reference = mesh". They are sweep repeats (notation §9.1).
5. **Prompt 07 vs data**: Prompt 07 §1.5 says one Setup1 gives identical mesh settings; `data/mesh_lobe.csv` shows they differ (retracted, G13). Prompt 07 §1.1 says the port order was "confirmed in every new file header", while the pipeline policy is not to trust headers (harmless: QC confirms the order from data).
6. **MCI hippocampus material**: imaging code models v2 MCI with Normal materials (`imaging/common.py`), while MCI_lobe uses HIP_MCI 40.3/5.203 (MODEL_CARD 5.1). v2 MCI material is not documented.
7. **Lobe geometry ≠ uniform geometry**: in the lobe phantom gray matter is always 7 mm thick (76 − e … 83 − e); in the uniform phantom gray thickness changes with stage (e.g. Mild 64.6–70.55 mm). So "Mild_lobe" is not "uniform Mild restricted to some lobes". Not stated anywhere explicitly.
8. **v1 prompt-02/03 numbers in `results/summary.md`** no longer match the files in `results/02`, `results/03` (overwritten by v2 run 1).
