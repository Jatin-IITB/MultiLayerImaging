# Open questions (Phase 0)

Everything I could not establish from the repository at HEAD `ecacd35`. Each item says why it
matters and which context pack might answer it. Items marked ★ are in my top-10 list for you.
IDs are stable; later packs will close them with a note.

## Q-A. Project history and scope

- **A1 ★** Stage S0 (single-layer work) is not in this repo. The only traces are `blind_validation_presentation.pptx` (untracked, 2026-09-20: R = 58 mm single-material sphere, **8** DGS antennas, 6 equatorial + 2 top, 2.7–4.1 GHz, 71 points, 5 blind cases) and `references/imaging_code.m`. Was there a separate "cross-section" phantom as well as the "sector" phantom? Which folder holds that work? → Pack 01.
- **A2 ★** The single-layer study used 8 antennas; the layered study uses 6 on one ring. Why did the antenna count and layout change, and who decided? → Pack 01/02.
- **A3** `references/imaging_code.m`: which experiment produced the six CSV field pairs ("diagonal", "same side", "opposite gap 12" …)? Which stage, which solver? → Pack 01.
- **A4** Prompts 01A–06 are referenced in commits and `results/summary.md` but only 07 and 08 are in `prompts/`. Do you have the earlier briefs? They define what each analysis was asked to do. (Is there a Prompt 06 at all? No script `06_*` exists.)
- **A5** Who ran which part? (You built the HFSS models; the analysis was done by Claude sessions. Is that the right attribution for the report?) Your supervisor's role and the dates of review meetings → Pack 04.
- **A6** The pptx was generated with python-pptx: was it presented to the professor? Is "4/5 cases" the method of slide 5 (fused channels), and is the 3/5 "baseline" on slide 11 a different method?

## Q-B. HFSS models and settings (sphere)

- **B1 ★** Skin, fat and skull ε_r/σ used in HFSS (OPEN-GUI since day 1). The imaging code *assumed* skin 37/2.0, fat 10.5/0.42, skull 10.8/0.61. → Pack 02.
- **B2** Normal-stage materials in HFSS v2 (the card's values are back-calculated from Shehab's % columns). Were they checked in the v2 material table, as they were for the lobe project? → Pack 02.
- **B3 ★** v2 MCI: hippocampus material (Normal 47.7/2.42, or MCI 40.3/5.203 as in MCI_lobe?). The imaging conclusions on MCI assume Normal material. → Pack 02.
- **B4 ★** What exactly changed between v1 and v2 ("corrected, same project")? The repeats are treated as "sweep settings only", yet v1 Mild/Moderate came from project `Brain_sevem_layer`. Were the v1 Mild/Moderate designs copies of the `new` designs, solved on the same mesh? This decides whether the solve-to-solve SD (0.15 dB) contains any mesh variation. → Pack 02.
- **B5** v1 solver settings (passes, ΔS, sweep type) — not recorded anywhere. → Pack 02.
- **B6** v2: adaptive solution frequency (lobe set used 3.4 GHz; v2 UNKNOWN), basis order, solver type, radiation-boundary size and distance. → Pack 02.
- **B7** Meaning of `ant_dist = 115 mm` and `z_ebg = −94.575 mm`, and how the feed-point radius 97.55 mm and polar angle 60.5° follow from the design variables. → Pack 02.
- **B8** Antenna design: DGS patch + AMC reflector dimensions (L, W, $L, $W, H, slot_distance …), substrate material, isolated resonance vs in-situ 3.62 GHz, S11 of a single antenna in free space. → Pack 02.
- **B9** The headers list project variables that contradict the stated geometry (e.g. `r_gray = 70.55mm`, `r_white = 17.5mm`, `r_brain = 95mm`, `r_csf = 95.5mm` in the **Healthy** file). Which variables drive each design? → Pack 02.
- **B10** v2 skull inner radius (hidden tool `Brain_sphere_1`): needed to know whether Healthy_sliced and v2 Normal are the same geometry. → Pack 02.
- **B11** Is the hippocampus really modelled as a central sphere of hippocampal tissue, with white matter around it (no ventricles) in v1/v2? → Pack 02.
- **B12** Why are T1 and T4 fields ~4 % stronger than the other four (field exports)? A geometric difference in the HFSS model (e.g. alignment with an axis, mesh)? → Pack 02.
- **B13** The field exports are of the **unsliced v2 Normal**. Was a sliced-head field export ever made? → Pack 02.

## Q-C. Re-solves and pending data

- **C1 ★** Status of the running solves (as of today): Normal mesh repeat, MCI repeat, Severe/Moderate equal-settings re-solves, Mild equal-settings (planned), lobe `_m2` re-solves (Mild, Moderate, Severe, LeftOnly_test, MCI_lobe). Has any finished? The report must say whether the pre-registered tests (claims register §I) have been run.
- **C2** The 2026-10-02 Normal "mesh repeat" was bit-identical to v2 Normal. Was the cause understood (same mesh reused)? → Pack 02.
- **C3** Severe_lobe converged "marginally" (ΔS 0.019999 vs target 0.02). Any warnings in the HFSS log? → Pack 02.
- **C4** MCI_lobe needed an extra `Ventricle_CSF` sphere to fix a meshing failure: what was the failure? → Pack 02.

## Q-D. Analysis and interpretation

- **D1 ★** Which staging feature is the headline: **M5.C2** (STATUS §4) or the **R21/R32 ratios** (audit + frozen rule)? STATUS §4 predates the audit. The report needs one story.
- **D2 ★** Do you accept that every v2 result (detection and staging) carries the class-correlated mesh confound (ΔS 0.02 vs 0.05; Normal unconverged) until the equal-settings re-solves are scored? STATUS §1–4 do not repeat this caveat next to the numbers.
- **D3** The stale k = 3 delays in MODEL_CARD caveat 5 and STATUS §2 (v1 numbers). The report will use the v2 numbers (3.11 / 2.97 / 5.31 ns). Should the analysis session be asked to correct MODEL_CARD/STATUS? (I may not edit them.)
- **D4** `results/imaging/figures/k3_path_time.png` is titled "3.2–4.2 GHz" while the v2 report section uses 2.8–4.2 GHz. Which data produced the committed figure?
- **D5** The `03_severity_index.png` and other run-2 figures: were they produced with floor subtraction on (config `floor_subtract: true`)? (Likely yes; not checked.)
- **D6** The lobe phantom keeps gray matter 7 mm thick in every sector (76 − e … 83 − e), unlike the uniform phantom where gray thickness shrinks with stage. Was this intended (Shehab Table 7 geometry), or a simplification? It affects how "Mild_lobe vs uniform Mild" is compared.
- **D7** LeftOnly_test carries CSF_Mild material in the 0.5 mm layer on the right side as well (one CSF object). The analysis predictions ignore this. Is a variant with a split CSF object planned?

## Q-E. CST voxel track (S8)

- **E1 ★** Nothing about the CST voxel head is in this repo (only the "array requirements" in `results/imaging/report.md` §7, written "for the CST voxel model"). Which voxel model (e.g. a CST Voxel Family head), which antennas, band, ports, and status? → Pack 03.
- **E2** Did the CST design follow the §7 recommendations (0.7–2.2 GHz, ≥ 16 antennas, coupling medium, several rings)? → Pack 03.

## Q-F. Professor's review asks

- **F1 ★** The record of what Prof. Sarkar asked and when. The only trace is Prompt 07 §1: "The professor asked us to combine the earlier sectored phantom with the layered phantom." → Pack 04.
- **F2** Was the "6 sectors × 60°" lobe layout taken from the S0 sector phantom (also 6 × 60°)? → Pack 01/04.

## Q-I. From your message of 2026-10-04 (lobe convergence study)

- **I1 ★** That message reads as addressed to the **analysis session** (Prompt 07 answers; edit the lobe manifest, MODEL_CARD Part 5, STATUS §7; rerun §3.3–3.4; commit). My rules for this session are read-only on `data/`, `results/`, `scripts/`, `MODEL_CARD.md` and `STATUS.md`, so I documented it in `docs/` only. Please forward it, together with the glitch finding (I2), to the analysis session.
- **I2 ★** `Mild_lobe_new.s6p` has a non-reciprocal single-sample spike on T2–T5 at 3.855 GHz (~30 dB). It produces the "+0.30 dB C3 per extra pass" and the set-B Normal−Mild R31 of 0.94 dB in your table. Under the frozen rule's recipe (masked) the one-pass R31 change is +0.135 (Healthy) and −0.034 dB (Mild), with opposite signs. Should the convergence conclusion (U4 §3: "R31, R32 carry ±0.15–0.3 dB through C3") be restated with the masked numbers, or should that frequency be re-solved with a discrete sweep?
- **I3** Is lobe_A "matched" enough? The stop rule is matched, but the healthy mesh still has 1.46× Mild's elements and a tighter final ΔS. Should the report call lobe_A "stop-rule matched" rather than "mesh-matched"?
- **I4** `data/sim_plan.csv` planned `*_m2` files with min converged passes 2 and max passes 10 for all lobe stages. Only Mild was re-solved that way. Are 2-consecutive re-solves of Moderate and Severe planned (lobe_B would then cover all stages)?
- **I5** "No ABC on ports": does this mean the HFSS port option "Use ABC / do not use ABC on port" (radiation boundary on the port face)? For the report's setup section.
- **I6** Closes **C2/L3**: deterministic meshing explains why the 2026-10-02 v2 Normal re-solve with the old pass limit was bit-identical. Confirm this applies to the v2 project as well.
- **I7** LeftOnly_test and MCI_lobe will arrive as `new_with_slices_LeftOnly_test.s6p` / `new_with_slices_MCI_lobe.s6p` (not `_m2`). The scoring compares each with "the Healthy file of the same stop rule". Noted for the plan (F7.7, F7.8, F8.13).

## Q-H. From the D0b outline and figure plan (added after D0b)

- **H1** D0b Ch. 3 mentions a sphere-radius correction 58 → ~100 mm, Bruggeman mixing of materials, and F-K migration / MF-Born imaging. None of these is in the repo (the pptx states R = 58 mm and mentions only DAS-type sector scoring + SVD). → P01.
- **H2** D0b Ch. 5 cites `[EXIST field_route]`. No file of that name exists in the repo. The nearest is `results/imaging/figures/i2h_k3_path.png` (opposite path only). Is `field_route` in a pack, or should neighbour / second-neighbour routes be made as [CODE] from `data/fields/`?
- **H3** D0b Ch. 2 gives the operating band as ~3.4–3.6 GHz. The in-situ S_ii notch is at 3.64–3.66 GHz (v2, lobe) and 3.62 GHz (v1); the design centre in the S0 deck is 3.4 GHz; the analyses use 3.2–4.2 GHz. Which band should the report call "operating band", and how was it chosen? → P02.
- **H4** D0b Ch. 7 calls the frozen-rule result a "generalisation result". The repo's label is transfer to regional atrophy in the same head, one solve per design = within-simulation noise robustness. I will use the repo's wording unless you object.
- **H5** D0b 8.2 "6 → 21 independent paths for a symmetric ring": for a symmetric ring/head only 4 entry types are independent; 21 reciprocal pairs only for an asymmetric head. I will write it that way unless you object.
- **H6** D0b has no chapter for the professor's review asks (P04). Appendix table, or woven into each chapter?
- **H7 Missing figure inputs** (plan.md "need" rows):
  - Screenshots: F1.1 `cst_head_skin.png`, F1.2 `cst_csf.png`, F2.1 antenna geometry, F2.4 radiation pattern, F3.1 single-layer geometry, F4.1 layered cross-section, F4.3 array view, F7.1 lobe sectors per stage, F9.1 CST head + antennas; optional F5.1 field plots.
  - Data: antenna parametric S11 sweeps and a single-antenna free-space S11 (F2.2, F2.3); single-layer Touchstone files and imaging outputs (F3.2–F3.5, F8.1); `LeftOnly_test_m2`, `MCI_lobe_m2`, `*_lobe_m2` files (F7.7–F7.9, F8.13); CST Touchstone files + port map (F9.2–F9.3); P05 imaging extraction (F8.13 and any [IMG] replacements).
  - v1 solver settings (for F4.5) — OQ B5.
- **H8** Fields exist only for the **v2 Normal** design at 3.4/3.6/3.8 GHz. Chapter 5 and the lobe kernels therefore use the unsliced healthy fields for every stage. Are stage or lobe field exports available or planned? (relates to B13)

## Q-G. Reproducibility and housekeeping (for you, not the report)

- **G1** The four lobe `.s6p` files, `prompts/` and the pptx are **untracked** in git, although committed results depend on the lobe files. Do you want them committed by the analysis session? (I may only commit `docs/`.)
- **G2** `data/fields/` (~880 MB) is git-ignored. Where is the archival copy?
- **G3** Test suite not re-run in this phase. Should I run `pytest` (read-only) in a later phase to cite "all tests pass at commit X"?
