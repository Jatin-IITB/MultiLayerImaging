# Microwave AD staging, Track A: status (4 Oct 2026; §7 updated 4 Oct, §6 3 Oct, §1–5 as of 2 Oct)

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

## 7. Lobe phantom: disease in selected lobes only (3–4 Oct)

As the professor suggested, the layered head and the sectored head are now one geometry. The
healthy head was cut into six 60° lobe wedges, one facing each antenna: frontal, left temporal,
left parietal, occipital, right parietal and right temporal. Atrophy (CSF widening under the
skull, and diseased tissue properties) is applied only in the lobes affected at each stage:
- Mild: temporal and parietal lobes on both sides;
- Moderate: Mild plus frontal, with deeper atrophy elsewhere;
- Severe: all six lobes.

There is one simulation per design and mesh setting, so these are noise-robustness results
within a simulation, not generalisation. The tissue values were checked in HFSS.

**Mesh: the first comparison was not like-for-like.** HFSS refines its mesh in passes until the
answer stops changing. In the first set, the healthy head was refined until two passes in a row
had converged (7 passes, 1.35 M elements), but each disease stage stopped at the first converged
pass (5 passes, 0.69–0.80 M elements). So the earlier statement "same mesh settings for all
stages" was wrong and is withdrawn. The healthy head and Mild were therefore re-solved:

| Design | Stopping rule | Passes | Mesh elements |
|---|---|---|---|
| Healthy (sliced) | first converged pass | 6 | 1,081,728 |
| Healthy (sliced) | two converged passes | 7 | 1,349,491 |
| Mild (lobes) | first converged pass | 5 | 739,774 |
| Mild (lobes) | two converged passes | 6 | 878,656 |
| Moderate (lobes) | first converged pass | 5 | 796,281 |
| Severe (lobes) | first converged pass | 5 | 690,077 |

The main comparison now uses the same stopping rule for every design (first converged pass).
It is a matched stopping rule, not a matched mesh: the healthy head still has ~1.5× the
elements of Mild.

**How much does one more refinement pass move the numbers?** That serves as the yardstick for
mesh error.
- **Detection ratio:** one extra pass moves it by at most 0.14 dB, the other two ratios by at
  most 0.08 dB, in no consistent direction. The healthy-vs-Mild difference is 1.1–1.25 dB,
  8–9× larger.
- **Detection holds under the matched rule:** the unchanged rule labels every design correctly
  in 100% of noisy measurements, including with ±2 dB / ±10° antenna errors.
- **Distance from the threshold:**
  - Healthy (sliced): 0.53 dB, 4× the yardstick;
  - Mild (lobes): 0.55 dB, 4×;
  - Moderate (lobes): 0.74 dB, 5×;
  - Severe (lobes): only 0.26 dB, 1.9×, so one more pass could push it to the threshold.
- **Merged staging** (Normal / Mild+Moderate / Severe) labels every lobe design correctly.
- **The finer three-stage rule fails on lobe-Mild, and the mesh decides by how much:** 41%
  correct at 5 passes, 69% at 6. Lobe-Mild sits right on the Normal|Mild boundary, closer to it
  than one pass moves the feature.
- **Where the disease is still cannot be told.**
  - When the frontal lobe is added (Mild → Moderate), the front-to-back difference is −0.26 dB.
    That is 3.8× the one-pass change, but only 2.3× the numerical symmetry error of these
    simulations. It is invisible with ±0.5 dB antenna gain errors (0.3×).
  - Gain-proof combinations of the antenna paths stay below 3× (best 2.3×).
  - These effects are **not separable from mesh and numerical error**.
- **Pending:** a left-lobes-only design (left-right asymmetry) and an MCI design. The
  predictions for the left-only design were written and committed before the file existed
  (`results/05_lobe/predictions.md`). It will be scored against them unchanged, using the
  healthy head solved with the same stopping rule. Two caveats go with the score: the
  predictions came from the first, unmatched pair; and the left-only design keeps a thin layer
  of diseased CSF on the right.
- **Suggested simulations:** Moderate and Severe (lobes) with the two-pass stopping rule. This
  completes the second matched set, and shows whether Severe stays on the AD side of the
  threshold.

Details: `results/05_lobe/mesh/report.md` (convergence study), `results/05_lobe/lobe_A/` (main
set), `MODEL_CARD.md` Part 5.

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
6. `results/05_lobe/lobe_A/figures/3_ratios_lobe_vs_uniform.png`: lobe-phantom stages (matched stopping
   rule) next to the uniform ones on the frozen decision boundaries.
7. `results/05_lobe/lobe_A/figures/4a_path_change_maps.png`: which antenna paths change per lobe stage.
8. `results/05_lobe/mesh/figures/yardstick_maps.png`: one extra mesh pass against the disease
   effects, on the same colour scale.

Source tables: `results/v2_with_v1_repeats/03/` (rules, thresholds, CV results),
`results/v2_with_v1_repeats/02/` (gaps vs noise), `results/qc/solve_comparison.md`,
`results/imaging/report.md` §1 and §4.
