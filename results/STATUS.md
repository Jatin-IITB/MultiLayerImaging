# Microwave AD staging, Track A: status (3 Oct 2026; §7 and §6 updated, §1–5 as of 2 Oct)

**Setup.** A 7-layer spherical head phantom with six patch antennas on one ring, simulated in
HFSS over 2.8–4.2 GHz. The stages simulated are Normal, MCI, Mild, Moderate and Severe.

**Which results count here.** Every stage except MCI has been solved twice; only the HFSS sweep
settings differ between the two solves. Every number below comes from **training on one solve
and testing on the other** (leave-one-solve-out), with realistic measurement noise added.
Results that only held on noisy copies of a single file are not reported here. All of it
concerns **one head geometry**.

## 1. Detection: Normal vs AD works

The rule takes one 6-port measurement. It returns INVALID if a quality check fails (an open or
shorted antenna, detuning, or an instrument noise floor too close to the signal). Otherwise it
compares one number with a threshold τ and answers Normal, AD, or UNCERTAIN when the number is
within a margin m of τ.

| Feature | τ | Margin m | Normal vs AD gap | Gap ÷ solve-to-solve noise | Result on the unseen solve |
|---|---|---|---|---|---|
| **R31** = opposite-antenna power ÷ neighbour power (geometric means, dB) | −15.27 dB (95% CI −15.37 to −15.17) | 0.08 dB | 1.53 dB | ≈ 10× (noise SD 0.15 dB) | sensitivity 1.00, specificity 1.00, 0% UNCERTAIN |
| **M5.C3** = opposite-antenna power, band-averaged (dB) | −52.72 dB (95% CI −52.83 to −52.51) | 0.24 dB | 1.83 dB | ≈ 7× (noise SD 0.31 dB) | sensitivity 1.00, specificity 1.00 (6-antenna vote) |

- **R31 needs no per-antenna calibration.** Antenna gain errors cancel in the ratio. With
  ±2 dB uncalibrated gain per antenna, R31 still scores 1.00 / 1.00, while M5.C3 drops to
  0.60 / 0.77. Its threshold is stable within 0.13 dB across both solve sets.
- **Requirement:** the instrument noise floor must be at least 8 dB below τ (about −61 dB);
  otherwise the measurement is INVALID. These numbers use 3.2–4.2 GHz, the band common to
  both solves.

## 2. Why it works

The opposite-antenna (k = 3) signal **travels around the head, not through it**.

- **Delay.** It arrives after 3.61 ns. A path around the surface predicts 3.69 ns; a straight
  path through the head predicts 6.03 ns.
- **HFSS fields.** 99% of this path's sensitivity is in the air around the head and only 0.3%
  in the brain. Half-way between the antennas, the field around the head is 23 dB stronger
  than the field through the head.

So the feature responds to the **outer layers**: the CSF/cortex just under the skull, where
atrophy replaces gray matter with CSF. In general this array senses only the **outer
~1–1.5 cm of brain**, and only near the antennas. A change deeper than ~1.5 cm is below the
noise everywhere.

## 3. What does not work

- **MCI.** It differs from Normal by 0.06 dB in R31, below the 0.15 dB solve-to-solve noise.
  That is expected: MCI changes only the central hippocampus, which this array cannot see.
  Some spectral-shape classifiers score 100% for MCI, but that cannot be checked yet because
  there is only one MCI solve.
- **Reflection-based metrics (|S11|-type).** Near chance on the unseen solve (balanced
  accuracy 0.45–0.56). Their Normal–AD change is ~1–2%, smaller than ordinary cable or
  calibration variation.
- **The old score Σ|Sii + Sij|/VSWR.** 0.62 on the unseen solve. In practice it is a
  reflection measure with arbitrary weighting.
- **Spectral-shape features** (full spectrum, 50 MHz sub-bands, resonance position). Two
  solves of the same design differ by 0.9–1.5 dB in spectral shape, as much as Normal vs AD.
  The resonance moved 16 MHz between solves. For staging, their accuracy on the unseen solve
  swings from 0.93 to 0.37 depending only on the classifier: they partly learn the solve, not
  the disease.
- **Imaging / localisation.**
  - Radar focusing puts every change at the head centre, an artefact of a symmetric ring.
  - Linear inversion with the real HFSS fields predicts only 11–44% of the actual signal
    change, and resolves depth only in the outer ~1 cm.
  - CSF thickness, hippocampus size and the location of the change cannot be recovered.

## 4. Staging lead (preliminary)

The **second-neighbour coupling M5.C2** separates Mild from Severe by 3.6–3.9× the
solve-to-solve noise. The opposite-antenna feature manages only 0.55×. The four
coupled-power features together reach 0.96 balanced accuracy for Normal / Mild / Severe on
the unseen solve.

This is preliminary: one head, two solves per stage, and a noise estimate from only four
repeat pairs. Moderate is not separable from Mild (0.9× the noise on M5.C2, 0.5× on M5.C3).

## 5. Limitations

- **One head geometry.** Nothing yet shows that the 1.5–1.8 dB gap survives differences
  between people in head size, skull/scalp thickness or antenna placement. Because the signal
  runs along the surface, skull and scalp variation is the main expected confound.
- **The solve-to-solve noise covers sweep settings only.** The mesh has not been varied.
- **All data are simulated,** with a modelled instrument and noise.
- **The signal path depends on air around the head.** A coupling medium or matching layer
  would likely suppress it.

## 6. Next simulations and what they decide

**Update 3 Oct.** The HFSS convergence tables show the v2 designs were meshed with different
settings: convergence target 0.02 for Normal/MCI but 0.05 for Mild/Moderate/Severe, and the Normal
solve did not converge. That split lines up with Normal vs AD, so a mesh contribution to the
main result cannot yet be excluded. Normal, MCI, Moderate and Severe are being re-solved with
identical, tighter settings (Mild still to start). The test applied to them is fixed in advance
in `MODEL_CARD.md` (Part 4), with the frozen rule unchanged. Items 1–2 below are part of that.

Planned in `data/sim_plan.csv`:

1. **Normal re-solved with a finer mesh** (HFSS Max Delta S 0.02 → 0.01). This is the first
   true mesh repeat, and it measures whether the mesh adds noise beyond the sweep settings. It
   firms up the margins m and the gap ÷ noise ratios in §1 (≈ 10× and 7×). It also shows
   whether the M5.C2 staging lead (3.6–3.9×) survives a realistic noise estimate, and how much of
   the spectral-shape difference comes from the mesh.
2. **A second MCI solve.** This allows the leave-one-solve-out test for Normal vs MCI. It
   decides whether the 100% spectral-shape MCI scores are file fingerprints, as physics
   suggests, and so settles the conclusion "MCI is not detectable with this array".

Beyond these two, generalisation needs **several head geometries per stage**: different head
radius, skull/scalp thickness, CSF thickness and antenna stand-off.

## 7. Lobe phantom: disease in selected lobes only (3 Oct)

As the professor suggested, the layered head and the sectored head are now one geometry. The
healthy head was cut into six 60° lobe wedges, one facing each antenna: frontal, left temporal,
left parietal, occipital, right parietal and right temporal. Atrophy (CSF widening under the
skull, and diseased tissue properties) is applied only in the lobes affected at each stage:
- Mild: temporal and parietal lobes on both sides;
- Moderate: Mild plus frontal;
- Severe: all six lobes.

There is one simulation per design, so these are noise-robustness results within a simulation,
not generalisation.

**Mesh settings are not matched.** The table comes from the HFSS solution dialogs. All designs share
a convergence target of ΔS 0.02 and at most 8 passes, but the healthy head required 2 converged
passes and the disease stages only 1.

| Design | Passes | Final ΔS | Mesh elements | Status |
|---|---|---|---|---|
| Healthy (sliced) | 7 | 0.0092 | 1,349,491 | converged |
| Mild (lobes) | 5 | 0.0186 | 739,774 | converged |
| Moderate (lobes) | 5 | 0.0194 | 796,281 | converged |
| Severe (lobes) | 5 | 0.0200 | 690,077 | converged (marginal) |

The healthy reference therefore has ~1.8× the mesh and ~2× tighter convergence than every
disease stage. This is the same imbalance as in the earlier set. To size it roughly, compare
the two healthy heads solved with different meshes, the sliced one and the earlier one. That
mesh change alone moves the classifier ratios by 0.07–0.21 dB. Measured against this yardstick:
- **Detection:** the healthy-to-disease change is 0.9–1.4 dB, 14–22× the yardstick of its own
  feature and 4–7× the largest one. Severe (lobes), however, sits only 0.26 dB past the
  threshold: 4× its own yardstick, 1.2× the largest.
- **Staging:** the second-neighbour ratio moves 0.53 dB from healthy to Mild (lobes), only 2.5×
  the yardstick.
- **Localisation:** the front-lobe effects are 0.2–0.3 dB, only 1–2× the yardstick. They are
  **not separable from mesh** until mesh-matched re-solves exist.

The yardstick comes from two fine meshes; the coarser disease meshes probably err more.

- **The sliced healthy head matches the earlier healthy head.** The opposite/neighbour ratio
  differs by 0.07 dB, which is within the solve-to-solve noise.
- **Detection still works, without retraining.** The frozen Normal-vs-AD rule from §1 was
  trained only on uniform atrophy. It labels the sliced healthy head Normal, and all three
  lobe stages AD, in 100% of noisy measurements, including with ±2 dB / ±10° per-antenna errors.
  - **Correction:** the lobe designs were *not* meshed alike (table above), so this does
    not show that detection is independent of mesh settings. That earlier inference is
    retracted.
- **Staging is partly fragile.**
  - The frozen rule with merged stages (Normal / Mild+Moderate / Severe) labels every lobe stage
    correctly.
  - The finer three-class rule calls lobe-Mild correctly only ~42% of the time. Lobe-Mild
    changes the staging feature half as much as uniform Mild, and lands right on the Normal|Mild
    boundary.
  - Stage order is preserved: both staging ratios move monotonically from Normal to Severe.
- **Where the disease is cannot be told reliably.** When the frontal lobe becomes affected
  (Mild → Moderate), the front-to-back difference in neighbour-antenna coupling is −0.21 dB. That
  is 2.6× the numerical noise on clean data, but it vanishes under ±0.5 dB antenna gain errors.
  Gain-proof combinations of the antenna paths stay below 3× the noise (best 2.3×).
- **Running:** Mild, Moderate and Severe (lobes) are being re-solved with mesh settings matched
  to the healthy head. Their difference from the current files measures the mesh effect
  directly.
- **Pending:** a left-lobes-only design (left-right asymmetry) and an MCI design, both
  mesh-matched. The predictions for the left-only design were written and committed before
  the file existed (`results/05_lobe/predictions.md`). It will be scored against them
  unchanged.

Details: `results/05_lobe/report.md`, `MODEL_CARD.md` Part 5.

## Figures for slides

1. `results/imaging/figures/i2h_k3_path.png`: the opposite-antenna signal going around the
   head (HFSS fields).
2. `results/v2_with_v1_repeats/figures/03_severity_index.png`: Normal vs AD distributions with
   τ and the UNCERTAIN margin. MCI visibly overlaps Normal.
3. `results/v2_with_v1_repeats/figures/03_gain_errors.png`: R31 stays correct with ±2 dB
   antenna gain errors; the plain power feature does not.
4. `results/imaging/figures/i2h_detectability_radial.png`: the array senses only the outer
   ~1–1.5 cm.
5. `results/imaging/figures/k3_path_time.png`: the delay test (around the head, not through it).
6. `results/05_lobe/figures/3_ratios_lobe_vs_uniform.png`: lobe-phantom stages next to the uniform
   ones on the frozen decision boundaries.
7. `results/05_lobe/figures/4a_path_change_maps.png`: which antenna paths change per lobe stage.

Source tables: `results/v2_with_v1_repeats/03/` (rules, thresholds, CV results),
`results/v2_with_v1_repeats/02/` (gaps vs noise), `results/qc/solve_comparison.md`,
`results/imaging/report.md` §1 and §4.
