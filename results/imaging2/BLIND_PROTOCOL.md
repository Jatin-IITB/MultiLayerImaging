# Blind protocol for `data/raw/new_with_slices_Test_B.s6p` (imaging2)

**Committed before the file exists.** At commit time `data/raw` holds no `Test_B` file. Neither this file nor
`imaging2/` will be changed after this commit until the score is committed. Any deviation will be reported as a
deviation, never folded in silently.

**Blindness:**
- The Touchstone header of the blind file is never read or printed (the parser uses the option line only).
- No truth is requested before the reconstruction is committed.
- The main session's RightOnly / C6 replication documents (`results/05_lobe/review2/predictions_R3_C4.md`,
  MODEL_CARD §6.5, the RightOnly parts of `results/HANDOVER.md`) have not been read and will not be read before
  the score is committed.

## 1. Commands (fixed)
```
python -m imaging2.blind run   --file new_with_slices_Test_B.s6p --tag Test_B   # reconstruction + blind figures
git commit (results/imaging2/blind/Test_B/)                                      # BEFORE any truth is known
# truth supplied by the user -> results/imaging2/blind/Test_B/truth.json, written verbatim
python -m imaging2.blind score --tag Test_B                                      # criteria below + scored figure
```
Outputs go to `results/imaging2/blind/Test_B/`:
- `report.json`, `report.md`;
- `marg_<variant>.npy`;
- `blind_overview`, `blind_slices_{sig,eps}`, `blind_stack`, `blind_views`, `blind_detuning` PNGs;
- after the truth arrives: `score.json`, `score.md`, `blind_scored` PNG.

## 2. Data handling (fixed)
- **Loader:** `imaging2.data.load_external`.
  - Glitch masking with the main session's −30 dB reciprocity rule, on the native grid.
  - The common 3.2–4.2 GHz / 5 MHz / 201-point grid is taken exactly if the file's nodes contain it, otherwise cubic
    spline on Re/Im. If the file does not cover 3.2–4.2 GHz the run stops (reported, not patched).
  - Port order Port 1..6 = T4, T3, T2, T1, T6, T5.
- **Data:** complex log-ratio ln(S_TestB / S_ref) of the 21 reciprocal paths, amplitude and phase, all 201 frequencies.

## 3. Training set (fixed): every lobe design, both meshes
| observation | reference |
|---|---|
| Healthy_sliced (p7), zero-change example | Healthy_sliced_new (H6) |
| Mild_lobe (p5) / Mild_lobe_new (p6) | H6 / H7 |
| Moderate_lobe (p5) / Moderate_lobe_c3 (p6) | H6 / H7 |
| Severe_lobe (p5) / Severe_lobe_c3 (p6) | H6 / H7 |
| LeftOnly_test_c3 (p6) | H6 |
| MCI_lobe_c3 (p6) | H6 |

- **Same surrogate and selection as the main run** (`METHOD_surrogate_inversion.md`): layered-stack ΔΓ features,
  D6-shared coefficients, ridge.
- **Feature variant and λ:** chosen by nested leave-one-design-out over these six designs, from the same 9 candidates.
- **Noise ruler:** all four mesh pairs (Mild, Moderate, Severe double differences; H7 − H6) plus the nested
  model-error residuals.
- **Not used:** uniform v2 designs.

## 4. Inversion (fixed)
- **Prior:** P(stage) = 1/4 over Healthy / Mild / Moderate / Severe; P(unaffected) = 1/2 per sector; e uniform on
  0.5–22 mm.
- **Sampler:** Gibbs with 600 sweeps (150 burn-in), seed 0; Chib evidence; Birge tempering if χ²/dof > 1.
- **Variants, all reported:**

| variant | reference | gain handling | role |
|---|---|---|---|
| `standard_H6` | Healthy_sliced_new (H6) | none | **PRIMARY**: decides the verdict |
| `gainfree_H6` | H6 | per-port log-gain projected out | secondary |
| `standard_H7` | Healthy_sliced (H7) | none | secondary (reference dependence) |

- **Why H6 is primary:** the stop rule of Test_B is unknown. H6 (stop rule 1, 6 passes) is the reference of
  lobe_A, the primary set, and its pass count matches the earlier test designs (LeftOnly, MCI: 6 passes).

## 5. Fit-rejection rule (fixed)
- **χ²/dof definition:** χ² per effective degree of freedom at the MAP state of the most probable stage, before any
  tempering (2·21·201/ℓ effective dof, with ℓ the fold's frequency correlation length). It is `chi2_per_dof` in the
  report.
- **REJECTED if χ²/dof > X = 3.0.**
- **POOR FIT (depth not trusted)** if 1.5 < χ²/dof ≤ 3.0. This is descriptive only; it changes no criterion.

**Why X = 3.0** (the distribution available at commit, `posteriors.json`, `posteriors_loso.json`):

| reconstructions | χ²/dof |
|---|---|
| real designs inside the training range (12: LODO Mild/Moderate/LeftOnly/Healthy/MCI on both meshes and references, LOSO ×3, mirrored, rotated) | 0.30 – 1.02 |
| real design outside the training range (Severe p5 / p6: stage and lobes right, depth wrong) | 2.12, 2.59 |
| corrupted data (Mild p6 with the 21 paths shuffled) | 22.9 |

- X = 3.0 lies above every real head reconstructed so far, 16% above the worst, which is the extrapolated Severe.
  It lies 7.6× below the corrupted control.
- Rejection is meant for data the model cannot represent at all. A real head that is merely outside the training
  range should not be rejected if its lobes are still right.
- The 1.5 flag sits in the gap between 1.02 and 2.12, where depth was already shown to be wrong.

## 6. What is reported for every variant (no truth needed)
- Stage: MAP stage and all four stage probabilities.
- Per sector: P(affected), the call (affected iff P > 0.5), median ê, and the 90% interval.
- Side statements derived from the calls: left/right, front/back.
- χ²/dof, the fit status, and the tempering factor.

## 7. Truth definitions used by the scorer (fixed)
- **Truth format:** the user's file, written verbatim to `truth.json`: `{"e": [6 values in mm], "tissue_stage": ...}`,
  optionally `"sector_stage": [6]`, `"affected": [6]`, `"csf_stage"`, `"hip_stage"`, `"r_hip"`.
- **Affected sector:** a sector is truly affected if e_k > 0 or its gray/white material is not healthy.
- **True stage:**
  - the material table of the affected gray/white matter;
  - **Healthy** if no sector is affected (a hippocampus-only / MCI-type design counts as Healthy, because the
    hippocampus is not estimated);
  - if affected sectors carry different stages, the stage criterion is **N/A** and reported as such.
- **Coverage:** a sector's truth is covered if q05 ≤ e_true ≤ q95. An unaffected truth (e = 0) is covered when the
  interval reaches 0. True e > 22 mm cannot be covered (grid limit, stated in advance).

## 8. Pass criteria (fixed; the PRIMARY variant decides, the secondaries are scored the same way and reported)
| criterion | rule |
|---|---|
| C1 lobe pattern | 6/6 sector calls correct = PASS; 5/6 = PARTIAL; ≤ 4/6 = FAIL |
| C2 stage | MAP stage = true stage (or N/A, see §7) |
| C3 depth | truth inside the 90% interval in ≥ 4 of 6 sectors |
| fit | χ²/dof > 3.0 = REJECTED |

**Overall:**
- **REJECTED** if the fit is rejected.
- else **PASS** if C1 = PASS, C2 correct or N/A, and C3 met.
- else **PARTIAL** if C1 ∈ {PASS, PARTIAL} and C2 correct or N/A.
- else **FAIL**.

A wrong stage is therefore a FAIL even when the lobes are right.

## 9. Expectations stated in advance (not criteria)
- **Depth beyond ≈ 10 mm** is weakly determined. Severe-material depth is unreliable (§6 of the README).
- **On clean simulated data the gain-free variant's depths may collapse** towards 1–1.5 mm (seen on LeftOnly, README
  §5). Its C3 may fail for that reason.
- **If Test_B differs in kind** from the training family, the model has no representation for it. Examples:
  different stages in different sectors, non-wedge geometry, changed skull/skin, a different antenna setup. The fit
  rule is the safeguard; a POOR or REJECTED fit is the expected sign.

## 10. Code test before commit (not evidence)
- **Scope:** the whole run → figures → score chain was executed in-sample on LeftOnly_test_c3 (it is in the
  training set) into a scratch folder. Nothing was kept in the repo.
- **Bug found and fixed:** a UTF-8 file-writing error on Windows. A figure title was also wrapped.
- **Result:** all three variants PASS. That is expected in-sample and says nothing about the blind test.
