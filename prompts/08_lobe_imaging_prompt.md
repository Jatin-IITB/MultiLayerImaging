# Prompt 08 — Lobe-sector phantom: sector-level localisation and imaging (imaging session)

Paste into the imaging session (repo `MultiLayerImaging_v1`, code in `imaging/`). Read
`results/imaging/report.md` (your previous study), `MODEL_CARD.md` and `results/05_lobe/` if the analysis
session has already written it. The geometry and data context is the same as in
`prompts/07_lobe_analysis_prompt.md` §1 (copied in short below).

## 1. Why this study

Your previous study ended with: *every change was spherically symmetric, so radar imaging peaked at the
centre (symmetric-ring artefact); the array senses only the outer ~1–1.5 cm under each antenna; voxel
inversion is hopeless; a regional parameterisation (per-lobe Δε) is realistic.* The new phantom is exactly
that test case. AD now affects **only some lobe sectors**, each centred on an antenna, and the change sits
in the outer cortex, where the array can see: 7.5–18 mm of extra CSF under the skull plus changed gray/white
material in that sector.

## 2. Geometry and data (short)
- Ring: T1 at azimuth −90° (−Y), T2 −30°, T3 30°, T4 90°, T5 150°, T6 −150°; feed points r = 97.55 mm,
  polar 60.5° (ring at z ≈ +48 mm). Port 1..6 = T4, T3, T2, T1, T6, T5.
- Sectors Sk = azimuth [−120 + 60(k−1), −60 + 60(k−1)]°, full height. S1 Frontal (T1, nose −Y),
  S2 Temporal L, S3 Parietal L, S4 Occipital (T4), S5 Parietal R, S6 Temporal R; +X = subject's left.
  Core = hippocampus sphere (medial temporal).
- In sector k: gray 76−e_k … 83−e_k mm, white 25 … 76−e_k mm, hippocampus r_hip inside a fixed 25 mm hole,
  CSF = solid 83.5 mm sphere filling every gap; skull 83.5–86.5, fat, skin to 88 mm.
- Stages (e_S1…e_S6 in mm; r_hip): Healthy_sliced 0 everywhere, 25; Mild_lobe 0/7.5/11.5/0/11.5/7.5, 17.5;
  Moderate_lobe 11.5/12.5/15.5/0/15.5/12.5, 12.5; Severe_lobe 15.5/17.5/18/11.5/18/17.5, 7.5;
  **LeftOnly_test** 0/7.5/11.5/0/0/0, 17.5 (left temporal + left parietal only); **MCI_lobe** 0 everywhere, 21.25.
  Affected sectors use Shehab Table 5 stage materials for gray and white; the CSF material is the stage
  material everywhere; unaffected sectors are healthy. Full material table: prompt 07 §1.4.
- Files: `data/raw/new_with_slices_<Design>.s6p`, 3.2–4.2 GHz, 201 points. Available now:
  Healthy_sliced, Mild_lobe, Moderate_lobe, Severe_lobe. **LeftOnly_test and MCI_lobe are still solving
  and are the blind test set: do not open them until §4 says so.**
- Reference for every difference: **dS = S(stage) − S(Healthy_sliced)** (same project, same setup, same
  mesh recipe). Do not use new_Healthy as the reference except in a side check.
- Fields: `data/fields/E_Normal_T{1..6}_{3p4,3p6,3p8}GHz.fld` (+ T1 wide) are from the **unsliced** v2
  Normal design. At e = 0 the sliced head is geometrically the same head (differences: the skull inner
  surface may differ, and the mesh does), so use them as the background fields for the Born kernels. State that.
- Symmetry: Mild/Moderate/Severe are mirror-symmetric about the Y axis (left = right); only LeftOnly_test
  has a left/right difference.

## 3. Tasks on the four available designs

**3.1 Sector sensitivity kernels.** From the HFSS fields build, for every antenna pair (i,j) and frequency
(3.4/3.6/3.8 GHz), the Born sensitivity to a unit Δε (complex) in each of 7 regions:
- 6 **outer-cortex sector shells** (r 70–83.5 mm inside wedge k: where e_k acts);
- the **core** (r < 25 mm);
- also a variant splitting each sector into "under-skull gap" (r 76–83.5) and "deeper" (r 60–76) for a
  depth-identifiability check.

Report the 21-pair × 7-region kernel matrix (normalised), its singular values, and the conditioning.
- Which sectors are distinguishable at all with 6 antennas on one ring?
- Expect the mirror pairs S2/S6 and S3/S5 to be distinguishable only through the ring position (the kernels
  are not mirror-identical in pair space).

**3.2 Identifiability (CRLB) before any fit.** With the typical noise model (and ±0.5 dB per-port gain;
also the gain-invariant version using log-ratios / cross-ratios), compute the CRLB of the 7 regional
parameters. State which sectors are determined (CRLB < half the expected change) and which are not.

**3.3 Sector inversion (the main result).** Fit the 7 regional amplitudes to dS of Mild, Moderate and
Severe (κ(f) calibration as in your §4.1, fitted on **Mild only**, then frozen). Use:
- (a) a linear least-squares/Tikhonov fit;
- (b) a non-negative / bounded fit (AD only lowers ε here);
- (c) a gain-invariant fit on cross-ratio / log-ratio data (no per-port calibration needed).

Score against the truth:
- **pattern correlation** between the recovered 6-sector map and the true e_k (or true Δε) map;
- **top-k accuracy** of the affected-sector set;
- the **front/back verdict** for Moderate (S1 affected, S4 not): is S1 recovered as affected and S4 as
  healthy beyond the CRLB?

Show polar "lobe maps" (6 wedges coloured by recovered change, truth beside them).

**3.4 Radar imaging, now that the change is asymmetric.** Re-run DAS / DMAS on dS for Moderate and Severe.
- Does the image peak move off the centre toward the affected side?
- Report the angular position of the image maximum vs the centroid of the affected sectors.
- Expect Mild ≈ symmetric (left = right, front = back healthy), so its image should stay centred or show
  front/back only.

**3.5 Noise floors.** Healthy_sliced is circulant: use its antenna-to-antenna spread (and the mirror-pair
spread of each stage) as the numerical noise floor for dS. Every recovered sector value must be compared
with what the same inversion returns on a noise-only input (the Healthy_sliced symmetry residual rotated
into each pair) to give a null distribution.

## 4. Blind test (pre-registered)

Before opening LeftOnly_test or MCI_lobe:
1. Freeze the pipeline (code commit hash, κ, regularisation, thresholds for calling a sector "affected").
2. Write `results/imaging/lobe_predictions.md`: what the frozen pipeline should return for
   - LeftOnly_test: S2 and S3 affected, S5 and S6 healthy, S1 and S4 healthy;
   - MCI_lobe: nothing beyond the noise floor.
3. Commit. Only then run on LeftOnly_test and MCI_lobe and score.

**The left–right call on LeftOnly_test is the headline localisation result.** It succeeds only if S2/S3
come out affected and S5/S6 healthy beyond the null distribution.

## 5. Deliverables
- `results/imaging/lobe_report.md`: kernels, CRLB, inversion scores, radar images, blind-test outcome, and a
  verdict "can this 6-antenna ring localise lobe-level AD: front/back? left/right? depth?".
- Figures in `results/imaging/figures/lobe_*.png`: lobe maps vs truth, kernel heatmap, radar images.
- Plain-language labels in figures (lobe names, neighbour / opposite path), units in dB / mm.
- One simulation per design and one head: everything is within-simulation capability, not
  generalisation. Say so.
- Do not modify the v1/v2 imaging results; this is a new section.
