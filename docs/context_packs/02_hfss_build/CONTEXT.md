# Context pack 02 — HFSS build history of the lobe-sector phantom, settings, convergence, verification

Source: the working sessions between Jatin and Claude (chat), 2–4 Oct 2026, plus HFSS outputs Jatin
pasted (Message Manager logs, convergence tables, material dialogs, geometry dump). Facts marked
**[HFSS]** were read from HFSS output; **[FILE]** from Touchstone headers or repo files; **[CHAT]** are
statements from the working sessions that are not otherwise recorded (treat as REPORTED).

## 1. Why this phantom exists
- **[CHAT]** After the review meeting, Prof. Sarkar asked for both radial (layer) and lateral (sector)
  variation in one geometry: the earlier single-layer *sectored* phantom (Pack 01) and the *layered*
  multilayer sphere (v1/v2) combined into a "hybrid" phantom.
- Design idea: keep the v2 Normal head and the 6-antenna ring unchanged; cut gray and white matter into six
  60° sectors, one per antenna; apply AD only to the lobes affected at each stage (Shehab et al. 2025
  Tables 5–7 for materials, radii and per-lobe CSF expansion; Saied et al. 2022 Table II for which lobes are
  affected at which stage).

## 2. Geometry as built [HFSS geometry dump: data/hfss_geometry_audit_Healthy_sliced.txt]
- Project `new_with_slices` (D:/Jatin/new_with_slices.aedt), HFSS 2024.2, Terminal Network, model units mm.
- Layers: Skin r_skin 88, Fat r_fat 87.5, Skull r_skull 86.5, CSF_outer r_csf_outer 83.5 (solid sphere),
  gray `GM_Sk` radius `83mm − e_Sk`, white `WM_Sk` radius `76mm − e_Sk`, HippocampusAD radius r_hip.
- Sectors (objects GM_S1_Frontal … WM_S6_TemporalR): Sk spans azimuth [−120° + 60°(k−1), −60° + 60°(k−1)],
  full height. S1 Frontal, S2 Temporal L, S3 Parietal L, S4 Occipital, S5 Parietal R, S6 Temporal R.
  +Z superior, nose at −Y, +X = subject's left.
- White matter has a fixed 25 mm central hole ("VentHole", subtracted during the build); gray = sphere(83 − e)
  ∩ wedge minus a solid sphere(76 − e); CSF_outer is a solid sphere and the brain parts inside take
  priority, so CSF fills the 0.5 mm layer, the e_k gap and the ventricle gap r_hip…25 mm.
- Skull inner surface set explicitly to r_csf_outer (SkullHole subtract) in this project; the v2 skull hole
  radius (hidden tool `Brain_sphere_1`) was never determined.
- Antennas: six DGS patches on Rogers RT/duroid 6010 (H = 1.575 mm), patch toward the head, copper ground
  outward, 3 × 3 FR4 AMC tiles behind (AMC ground ≈ 107 mm from origin). Lumped-port sheets at 97.70 mm,
  z = 48.06 mm (polar 60.5°), azimuths −90.4 (T1), −30.4 (T2), +29.6 (T3), +89.6 (T4), +149.6 (T5),
  −150.4 (T6). Antenna + AMC span z ≈ 44–78 mm. Nearest AMC tiles of neighbours ≈ 64 mm apart.
- Ports: excitations FEED_3_T4, T3, T2, T1, T6, T5 = Touchstone Port 1..6. **[HFSS + GUI]** Port 1 lights
  the +Y antenna and Port 4 the −Y antenna (field exports); selecting excitation 2 highlights the sheet at
  +29.6° (+X side). So Port 1..6 = T4, T3, T2, T1, T6, T5 with T2/T3 on the subject's left.
- Leftover variables present but used by no visible object: r_brain 95, r_csf 95.5, r_gray 70.55,
  r_white 17.5, r_brain_ad 61.68, r_csf_inner 61.68, r_csf_expanded 64.6, ant_dist 115 mm.
- A sheet `field_cutplane` exists at z = −9.09 mm (purpose and use in field exports: to be established).

## 3. Build procedure and scripts [CHAT; final versions in `scripts/` of this pack]
1. `build_lobe_phantom.py` (run on a copy of the v2 Normal design, renamed Healthy_sliced): pre-flight
   report; adds variables e_S1..e_S6, r_hip; adds the SkullHole subtract; removes leftovers; deletes
   Gray_Matter / White_MatterAD; sets the hippocampus radius to r_hip; builds 12 sector pieces (wedge = a
   rectangle in the XZ plane swept 60° about Z, then rotated); assigns healthy materials; validates.
2. `make_stage_designs.py`: from Healthy_sliced, copies Mild_lobe, Moderate_lobe, Severe_lobe, MCI_lobe;
   sets e_Sk and r_hip; assigns stage materials to GM/WM of affected sectors, HIP and CSF (MCI: HIP only);
   ensures 13 materials exist; validates each.
3. `make_leftonly_test.py`: copies Mild_lobe → LeftOnly_test, sets e_S5 = e_S6 = 0 and restores healthy
   GM/WM in S5, S6 (CSF stays CSF_Mild everywhere because CSF is one object).
4. `fix_mci_mesh.py`: adds Ventricle_CSF (sphere r 25 mm, CSF_Healthy) to MCI_lobe after mesh failures.
5. Read-only helpers: `diagnose_phantom.py`, `report_setup_and_materials.py`, `geometry_audit.py`.

Stage table [FILE headers]:

| Design | e_S1 | e_S2 | e_S3 | e_S4 | e_S5 | e_S6 | r_hip |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | 0 | 0 | 0 | 0 | 0 | 0 | 25 |
| MCI_lobe | 0 | 0 | 0 | 0 | 0 | 0 | 21.25 |
| Mild_lobe | 0 | 7.5 | 11.5 | 0 | 11.5 | 7.5 | 17.5 |
| Moderate_lobe | 11.5 | 12.5 | 15.5 | 0 | 15.5 | 12.5 | 12.5 |
| Severe_lobe | 15.5 | 17.5 | 18 | 11.5 | 18 | 17.5 | 7.5 |
| LeftOnly_test | 0 | 7.5 | 11.5 | 0 | 0 | 0 | 17.5 |

## 4. Problems met during the build and how they were fixed [CHAT]
- Scripts first referenced material names instead of object names → rewritten for CSF_outer, Gray_Matter,
  White_MatterAD, HippocampusAD.
- Validation errors: gray wedges intersected the hippocampus (gray had subtracted the holed white) → gray now
  minus a solid core sphere(76 − e). Pieces intersected the skull (skull hole smaller than 83.5) → SkullHole
  subtract at r_csf_outer. Leftover clones from a deleted Subtract → cleanup step.
- "CSF_outer minus 13 parts" failed to regenerate when lobes shrink → CSF_outer made a solid sphere;
  inner objects take priority.
- Design copy/rename failures (deleted names reserved; paste only works with the base design active) →
  save after delete, `_v2` fallback, set base active and retry.
- MCI_lobe failed to mesh (TAU and classic) → Ventricle_CSF object (fix_mci_mesh.py).
- Mild solve crashed / took ≈ 7 h with FieldSweep enabled → FieldSweep disabled, sweep restricted to
  3.2–4.2 GHz; licence errors (elec_solve_hfss unavailable) from stray processes → runs queued one at a time.

## 5. Materials — verified [HFSS material dialogs, screenshots 3 Oct 2026]
CSF_Healthy 65 / 4.27, Gray_Matter_healthy 47.7 / 2.42, Hippocampus_healthy 47.7 / 2.42,
WhiteMatterHealthy 35.3 / 1.65 (εr / bulk conductivity S/m); μr 1; dielectric and magnetic loss tangent 0;
no frequency dependency set ("Measured Frequency 9.4e9 Hz" is a default label, unused).
Per-object assignments for all six designs read by `report_setup_and_materials.py` match the stage table
(LeftOnly: GM/WM_Mild in S2, S3 only; HIP_Mild; CSF_Mild. MCI: HIP_MCI; CSF_outer and Ventricle_CSF healthy).
Stage material values (Shehab Table 5) are listed in MODEL_CARD Part 5; the reference frequency of those
values is not established.

## 6. Solver settings and convergence [HFSS]
Setup1 (all designs): adaptive solution at 3.4 GHz (single), Max ΔS 0.02, 30 % refinement per pass,
first-order basis, iterative solver, no ABC on ports. Sweep: interpolating, 3.2–4.2 GHz, 201 points (5 MHz),
"Converged". FieldSweep disabled. Export `GHz S MA R 50`.

Convergence tables (pass: elements / max |ΔS|):

| Design | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| Healthy_sliced | 416,751 / – | 531,074 / 0.376 | 618,703 / 0.133 | 727,565 / 0.0520 | 863,780 / 0.0210 | 1,081,728 / 0.0155 | 1,349,491 / 0.0092 |
| Mild_lobe | 408,913 / – | 521,032 / 0.374 | 604,558 / 0.101 | 673,289 / 0.0358 | 739,774 / 0.0186 | 878,656 / 0.0150 | |
| Moderate_lobe | 394,150 / – | 502,189 / 0.329 | 610,999 / 0.137 | 711,104 / 0.0431 | 796,281 / 0.0194 | 949,865 / 0.0146 | |
| Severe_lobe | 324,117 / – | 413,177 / 0.331 | 530,043 / 0.121 | 600,579 / 0.0422 | 690,077 / 0.019999 | 819,294 / 0.0116 | |
| LeftOnly_test | 407,030 / – | 518,859 / 0.395 | 596,082 / 0.119 | 695,577 / 0.0485 | 793,144 / 0.0220 | 941,358 / 0.0147 | |
| MCI_lobe | 418,663 / – | 533,581 / 0.439 | 614,780 / 0.150 | 751,208 / 0.0552 | 850,720 / 0.0222 | 981,160 / 0.0139 | |

Exported files (data/raw/new_with_slices_…), with the stop rule that produced them:

| File | Stop rule | Final pass |
|---|---|---|
| Healthy_sliced.s6p | ΔS < 0.02 on 2 consecutive passes | 7 |
| Healthy_sliced_new.s6p | ΔS < 0.02, 1 pass | 6 |
| Mild_lobe.s6p | 1 pass | 5 |
| Mild_lobe_new.s6p | 2 consecutive | 6 |
| Moderate_lobe.s6p (= Moderate_lobe_new.s6p to 1e-8) | 1 pass | 5 |
| Moderate_lobe_c3.s6p | 2 consecutive | 6 |
| Severe_lobe.s6p (= Severe_lobe_new.s6p to 1e-8) | 1 pass | 5 |
| Severe_lobe_c3.s6p | 2 consecutive | 6 |
| LeftOnly_test_c3.s6p | 1 pass | 6 |
| MCI_lobe_c3.s6p | 1 pass | 6 |

("_new" and "_c3" are file-name labels only.)

## 7. How the convergence question was handled (chronology) [CHAT + HFSS]
1. 3 Oct: first four lobe files analysed; the analysis session assumed identical settings. The convergence
   tables showed Healthy_sliced had required 2 consecutive converged passes (7 passes, 1.35 M elements) while
   the stages stopped at the first pass below 0.02 (5 passes, ~0.7–0.8 M): a healthy-vs-disease mesh
   imbalance, the same kind flagged in the v2 audit.
2. Re-solves were started. Two HFSS behaviours were learned: changing convergence settings does not
   invalidate an existing solution (Analyze only re-runs the sweep instantly; "Results → Clean Up
   Solutions" is needed), and the "2" was first typed into *Minimum Number of Passes* instead of
   *Minimum Converged Passes* in three designs.
3. Adaptive meshing proved **deterministic**: re-solves reproduced every pass (elements and ΔS) exactly, so
   the solution at a given pass is reproducible and old and new files form a pass-by-pass convergence study.
4. A quick plain-mean check suggested one extra pass moves the opposite path by +0.30 dB. The documentation
   session found that this came from a single-sample, non-reciprocal sweep glitch in Mild_lobe_new (T2–T5,
   3.855 GHz). With the frozen-rule recipe (glitch masking, trapezoid, geometric means), one extra pass moves
   R31 by ≤ 0.135 dB, R21 by ≤ 0.110 dB, R32 by ≤ 0.161 dB (four-stage yardstick, main session).
5. Two stop-rule-matched sets were defined: **lobe_A** (1 converged pass: Healthy_sliced_new, Mild_lobe,
   Moderate_lobe, Severe_lobe, LeftOnly_test_c3, MCI_lobe_c3) and **lobe_B** (2 consecutive: Healthy_sliced,
   Mild_lobe_new, Moderate_lobe_c3, Severe_lobe_c3). LeftOnly and MCI also match Healthy_sliced_new in pass
   count (6; in all three, pass 5 missed 0.02 by ≈ 0.002).
6. Decision recorded: no further re-solves; the matched sets plus the measured one-pass yardstick are the
   standard. "Stop-rule matched", not "mesh-matched" (element counts still differ).

## 8. Process notes worth reporting
- Pre-registration: LeftOnly predictions were committed (main `cf56de8`, imaging `lobe_predictions.md`)
  before the LeftOnly file existed; LeftOnly and MCI were opened only for QC before scoring.
- Adversarial review rounds (Prompts 11, 12) were run on both analysis sessions; their results are in
  `results/05_lobe/review/` and `results/imaging/lobe_review.md` and will arrive as their own pack.

## 9. Open items for the documentation
- v2 uniform designs: build history and skull hole radius (not in this pack).
- Purpose of `field_cutplane` (z = −9 mm) and the geometry of `data/fields` exports.
- Reference frequency of Shehab Table 5 values; realism of layer thicknesses (skin 0.5, fat 1, skull 3,
  CSF 0.5 mm).
- Scripts in `scripts/` are the final versions as delivered; whether every run used exactly these versions is REPORTED, not verified.
