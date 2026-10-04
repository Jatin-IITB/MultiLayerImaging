# Prompt 07 — Lobe-sector phantom: QC, frozen-rule test, asymmetry (main analysis session)

Paste into the main Track A analysis session (repo `MultiLayerImaging_v1`). Read `MODEL_CARD.md`,
`results/STATUS.md` and `results/04/audit/report.md` first; everything below adds to them.

## 1. What is new

The professor asked us to combine the earlier **sectored** phantom with the **layered** phantom in one
geometry. We built it in HFSS as a copy of the v2 Normal design (project `new_with_slices`):
the same 7-layer sphere and the same 6-antenna ring, but gray and white matter are cut into **six 60°
lobe sectors**, each centred on one antenna. AD is applied **only to the lobes affected at each stage**
(Shehab et al. 2025, Table 7; lobe order as Saied et al. 2022, Table II). The head is therefore no
longer spherically symmetric, so for the first time the antennas can see **different** tissue.

### 1.1 Coordinates and antennas (unchanged from v2, settled by the field exports)
- Origin = centre of the head. Ring of six DGS-patch + AMC antennas in the **upper** hemisphere:
  feed points 97.55 mm from the origin, polar angle 60.5° (ring plane z ≈ +48 mm), 60° apart.
- **T1 at azimuth −90° (−Y)**, then T2 −30°, T3 +30°, T4 +90° (+Y), T5 150°, T6 −150°.
- Touchstone port order (confirmed in every new file header): **Port 1..6 = T4, T3, T2, T1, T6, T5**.

### 1.2 Sectors (lobes)
Sector Sk spans azimuth [−120° + 60°(k−1), −60° + 60°(k−1)], full height, centred on antenna Tk.
The subject faces −Y (nose at T1); **+X is the subject's left**.

| Sector | Antenna | Lobe |
|---|---|---|
| S1 | T1 (−Y) | Frontal |
| S2 | T2 | Temporal, left |
| S3 | T3 | Parietal, left |
| S4 | T4 (+Y) | Occipital |
| S5 | T5 | Parietal, right |
| S6 | T6 | Temporal, right |
| core | — | medial temporal (hippocampus sphere) |

The lobe placement is schematic: azimuthal wedges, while real temporal lobes lie lower than the ring.

### 1.3 Layers inside sector k (e_k = CSF expansion in that sector, mm)
- gray matter: 76 − e_k … 83 − e_k mm
- white matter: 25 … 76 − e_k mm (fixed 25 mm central hole)
- hippocampus: sphere of radius r_hip at the centre, inside the 25 mm hole
- **CSF = solid sphere r = 83.5 mm**; it fills everything the brain parts do not occupy: the 0.5 mm
  healthy layer, the e_k gap under the skull in affected lobes, and the "lateral ventricle" gap
  r_hip … 25 mm. CSF is one connected compartment, so its material is the stage material everywhere.
- skull 83.5–86.5, fat 86.5–87.5, skin 87.5–88 mm (unchanged). **Change vs v2:** the skull's inner
  surface was explicitly set to 83.5 mm (r_csf_outer). The v2 skull hole radius (hidden tool
  `Brain_sphere_1`) is unknown: treat a possible Normal-geometry difference as a caveat.
- MCI_lobe additionally has an explicit `Ventricle_CSF` sphere (r = 25 mm, healthy CSF material) that was
  added only to fix a meshing failure. Same physics.

### 1.4 Stages (Shehab Tables 5–7)
| Design | e_S1 Fr | e_S2 TL | e_S3 PL | e_S4 Oc | e_S5 PR | e_S6 TR | r_hip | Materials changed |
|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | 0 | 0 | 0 | 0 | 0 | 0 | 25 | none |
| MCI_lobe | 0 | 0 | 0 | 0 | 0 | 0 | 21.25 | hippocampus only (CSF stays healthy) |
| Mild_lobe | 0 | 7.5 | 11.5 | 0 | 11.5 | 7.5 | 17.5 | gray+white in S2,S3,S5,S6; hippocampus; CSF |
| Moderate_lobe | 11.5 | 12.5 | 15.5 | 0 | 15.5 | 12.5 | 12.5 | + S1 |
| Severe_lobe | 15.5 | 17.5 | 18 | 11.5 | 18 | 17.5 | 7.5 | all six sectors |
| LeftOnly_test | 0 | 7.5 | 11.5 | 0 | 0 | 0 | 17.5 | = Mild with S5, S6 reset to healthy |

Materials (εr / σ S/m, static, from Shehab Table 5): healthy gray 47.7/2.42, white 35.3/1.65,
hippocampus 47.7/2.42, CSF 65/4.27; Mild gray 40.3/5.203, white 31.77/2.39, hippocampus 39.11/5.687,
CSF 55.25/4.91; Moderate 39.11/5.687, 31.064/2.722, 38.39/5.92, 48.75/5.337; Severe 38.39/5.92,
30.35/2.88, 37.2/6.413, 32.5/6.405; MCI hippocampus 40.3/5.203. Unaffected sectors keep the healthy
materials. *Verify in the user's material table that the healthy materials have exactly these values.*

**Symmetry:** Healthy_sliced and MCI_lobe are rotationally symmetric (circulant S). Mild, Moderate and
Severe are **mirror-symmetric about the Y axis** (x → −x maps T2↔T6, T3↔T5; T1 and T4 map to
themselves), so they can only show front/back/side differences. **LeftOnly_test breaks left/right symmetry.**

### 1.5 Data
`data/raw/new_with_slices_<Design>.s6p` — present now: Healthy_sliced, Mild_lobe, Moderate_lobe,
Severe_lobe. **LeftOnly_test and MCI_lobe are still solving: do not wait for them, and do not look at
them before the predictions in §3.4 are written.**
- 3.2–4.2 GHz, 5 MHz, 201 points (same grid as v2 on that band), `GHz S MA R 50`; e_k and r_hip are in
  the headers. Interpolating sweep; FieldSweep disabled.
- All designs are copies of one design with one Setup1, so the mesh settings are identical across stages
  (unlike v2, where AD stages used ΔS 0.05). Ask the user for the Setup1 values (Max ΔS, passes) and record them.
- One solve per design. No repeats yet.

Add the set to `data/sims.csv` (or a new `data/sims_lobe.csv`) as `set = lobe_v1`, `head_id = h_lobe`,
with a `sectors_affected` column. Glitch masking on as before.

## 2. Orientation numbers (computed by me on clean data, 3.2–4.2 GHz; recompute and correct)

- **Healthy_sliced vs new_Healthy:** R31 −14.57 vs −14.67, R21 −20.50 vs −20.71, R32 5.93 vs 6.05 dB,
  i.e. within ~1–1.5× the v2 solve-to-solve SD (≈ 0.15 dB). Reflection band power is −0.03 dB per antenna.
  Individual transmission entries differ by up to 0.7 dB. Healthy_sliced is **more** symmetric than
  new_Healthy (antenna spread k1 0.08 vs 0.45 dB, k3 0.23 vs 0.66 dB).
- **Stage ratios (R31 / R21 / R32, dB):** Mild −15.82 / −19.97 / 4.15; Moderate −16.00 / −19.45 / 3.44;
  Severe −15.52 / −18.00 / 2.47.
- **Localisation hint (Moderate − Healthy_sliced, band power, neighbour paths, both directions averaged):**
  T6–T1 −0.30, T1–T2 −0.29 (front, S1 affected) vs T3–T4 −0.07, T4–T5 −0.09 (back, S4 healthy) dB.
  Mild: all neighbour paths ≈ 0 to +0.09; Severe: all ≈ −0.8. Reflection changes ≤ 0.08 dB everywhere.
  The Healthy_sliced antenna spread on neighbour paths is 0.08 dB.

## 3. Tasks (write to `results/05_lobe/`, figures to `results/05_lobe/figures/`)

**3.1 QC.** Repeat `00_qc.py` on the new files: parse, passivity, reciprocity, glitches, port-map search
(must rank T4,T3,T2,T1,T6,T5 first). Symmetry floor:
- **circulant spread** from Healthy_sliced (all six equivalent pairs per k);
- **mirror-pair spread** for Mild/Moderate/Severe (|S(T2,·) − S(T6,mirror ·)| etc.). This is the noise
  ruler for every asymmetry claim below. Report both per path k and per frequency.

**3.2 Healthy_sliced vs new_Healthy.** Is the sliced healthy head the same head?
- Report every ring-symmetrised feature, R31/R21/R32 and C1–C3 differences, divided by the v2 solve SD
  (audit §1) and by the Healthy_sliced symmetry spread.
- Verdict: equivalent / small offset / different, with the skull-hole caveat (§1.3).

**3.3 Frozen-rule generalisation test.** Apply `results/04/frozen_rule.json` and the R31 detection rule
(τ, margin, gain-invariant gate) **unchanged** (no refitting) to noisy draws (typical + ±0.5 dB gain;
also ±2 dB gain + ±10° phase) of Healthy_sliced, Mild_lobe, Moderate_lobe and Severe_lobe.
- This is the first test on a **different disease geometry** (regional instead of uniform atrophy, same head).
- Report the per-class decision table, UNCERTAIN/INVALID rates, and where each lobe stage falls relative
  to the uniform v1/v2 stages on R31, R21 and R32 (plot both sets together).
- Is the ordering Normal → Mild → Moderate → Severe preserved? State honestly where the uniform-trained
  thresholds fail.

**3.4 Asymmetry and localisation (pre-register before LeftOnly arrives).**
- (a) Per-path change maps ΔP_ij = band power(stage) − band power(Healthy_sliced), as 6×6 heatmaps in dB,
  antennas in ring order with lobe labels. Separate reflection, neighbour, second-neighbour and opposite paths.
- (b) A **front–back index** (paths touching T1 vs paths touching T4) and a **left–right index** (paths
  touching T2,T3 vs T6,T5), each divided by the symmetry-floor SD. Expect left–right ≈ 0 for
  Mild/Moderate/Severe by construction: that is a check, not a result.
- (c) **Gain-invariant asymmetry features:** cross-ratios χ = |S_ij|²|S_kl|² / (|S_il|²|S_kj|²) for
  distinct i,j,k,l (every per-port gain cancels exactly; add a unit test like the R31 one), band-averaged
  and in dB, compared with the same quantity for Healthy_sliced. Which χ separate front-affected (Moderate)
  from front-healthy (Mild)?
- (d) **Write down now**, in `results/05_lobe/predictions.md` (commit before LeftOnly_test exists):
  which paths and indices should move for LeftOnly_test (left temporal + left parietal affected, right healthy),
  with sign and rough size, derived only from Mild/Moderate/Severe. Then, when LeftOnly_test arrives,
  score the predictions without changing them.

**3.5 MCI_lobe (when it arrives).** Same question as before: is MCI_lobe − Healthy_sliced larger than the
symmetry floor on any feature? Expect no (hippocampus invisible).

**3.6 Claims table** (holds / weakened / retracted / not testable), as in the audit, and a short
`results/05_lobe/report.md`. Update `MODEL_CARD.md` with a Part 5 for the lobe set and update `STATUS.md`.

## 4. Rules
- One solve per design: every number is **within-simulation noise robustness**, not generalisation.
  Say so in every table.
- Do not tune thresholds, bands or feature choices on LeftOnly_test or MCI_lobe.
- Plain-language names in figures (neighbour / second-neighbour / opposite path, lobe names), with internal
  codes only in the tables.
- Keep the v1/v2 results untouched; the lobe set is a new, separate dataset.
