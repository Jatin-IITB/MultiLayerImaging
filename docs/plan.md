# Plan — technical report, presentation and study notes

Phase 0 proposal (2026-10-03, HEAD `ecacd35`). Not started: chapters are written only on your
go-ahead, one at a time, after the relevant context packs have been merged.

Inputs: **INV** = `docs/00_inventory.md` (section), **CR** = `docs/01_claims_register.md` (claim IDs),
**OQ** = `docs/open_questions.md`, **P01–P04** = context packs.

## Deliverables and how they are built

| Deliverable | Location | Built from |
|---|---|---|
| Technical report | `docs/report/NN_<chapter>.md` (one file per chapter), later assembled | chapters below |
| Presentation | built from the finished report; one slide group per chapter | report + figures |
| Study notes | `docs/notes/NN_<chapter>_notes.md`, one per chapter, written together with the chapter | for every step: what / why / how (settings, equations, file) / result / meaning / limits / 2–3 likely professor questions with answers |
| Figures | reused from `results/…` (path recorded) or regenerated: script `docs/figures/src/`, image `docs/figures/` | INV §4 |

Each chapter ends with a **claims box**: every claim, its status (holds / weakened / retracted / not testable / pending) and its validity class (NR / XS / PHY / GEO), copied from CR. Never "generalisation".

## Chapter outline

| # | Chapter | Content | Feeds from | Figures (existing → new) |
|---|---|---|---|---|
| 1 | Introduction and aim | AD staging problem; why microwaves; dielectric changes with AD (Shehab 2025); prior work (Saied 2022: 6 antennas, 9 heads, 98.97 %); project aim and the question of "detection vs staging vs localisation"; honest scope statement (simulation only, one head) | INV §1.1 (references); P04 | new: concept sketch (head, ring, paths) |
| 2 | Measurement principle and notation | S-parameters, path power, ring distance and path names, reciprocity, circulant symmetry, why per-port gain matters; noise model | `docs/notation.md`; `src/adstage/noise/model.py`, `pipeline/augment.py` | new: ring diagram with T1–T6, ports, path types |
| 3 | Stage S0: single-layer sector / cross-section phantom | geometry, antennas, materials, S-parameter results, sector-scoring method, blind validation (5 cases), SVD gain problem, **why we moved to a layered model** | **P01**; `blind_validation_presentation.pptx`; `references/imaging_code.m`; CR §J; OQ A1–A3, A6 | from P01 / pptx media |
| 4 | Layered spherical phantom and antenna ring (HFSS build) | 7-layer geometry and stage table (Shehab Tables 5–6), materials, DGS-patch + AMC antenna, ring geometry and how it was settled (field exports), excitation, boundary, mesh/convergence settings, v1 → v2 history | **P02**; MODEL_CARD Parts 1, 2 (VERIFY), 3, 4; INV §2; CR §A; OQ B1–B13 | new: layered-sphere cross-section with radii per stage; convergence table |
| 5 | Data handling and quality control | Touchstone parsing and header policy, glitch masking, common grid, passivity/reciprocity, symmetry noise floor, port-map search, project confound (v1) | `scripts/00_qc.py`, `src/adstage/io/*`; `results/qc/qc_report.md`; MODEL_CARD Part 2–3; CR A1, A5, A14–A17 | `results/figures/qc_ring_modes.png` (inspect) |
| 6 | Features and separability (Prompt 02) | M0–M9 definitions; power vs dB averaging; Fisher ratio, Bhattacharyya; frequency robustness and faults; ordinality; why reflection metrics and M0 fail | `scripts/02_metrics.py`, `features/metrics.py`; `results/02/`, `results/v2_with_v1_repeats/02/`; summary §Prompt 02 (v1 numbers from git `2e60be5`) | `02_spectra.png`, `02_subbands.png`, `02_fisher_heatmap.png` (inspect) |
| 7 | Detection rule: Normal vs AD (Prompt 03 + follow-ups) | quality gate; setup perturbation; leakage-aware CV (LODO → LOSO); thresholds τ ± m; floor estimate and subtraction; **R31 and its gain invariance (proof)**; gain-invariant gate; per-measurement rule; cross-solve result | `scripts/03_classify.py`, `pipeline/*`, `features/floor.py`; `results/v2_with_v1_repeats/03/`; CR §C; STATUS §1 | `03_severity_index.png` (regenerate labels), `03_gain_errors.png` |
| 8 | Why detection works: the opposite path goes around the head | group-delay test, HFSS field exports, sensitivity depth, what the array can and cannot see | `imaging/paths.py`, `study_i2_hfss.py`; imaging report §1, §4.2–4.3; CR §B | `i2h_k3_path.png`, `i2h_detectability_radial.png`, `k3_path_time.png` (regenerate) |
| 9 | Staging: likelihood analysis, ratio lead and audit | between-solve covariance, symmetric KL, Bhattacharyya kept %, LOSO QDA/LDA, MI; R21/R32; nested selection; exact permutation test; band robustness; hardware; frozen rule; physics of R21 (Born, CSF permittivity) and its fragility; M5.C2 vs ratios (OQ D1) | `scripts/04_likelihood.py`, `05_audit.py`; `results/04/`; imaging §4.7; CR §D, §E | `04_divergence.png`, `audit/4_per_solve.png`, `ratios_kernels.png` (inspect) |
| 10 | Imaging and localisation on the symmetric phantom | I1 radar (DAS/DMAS/MVDR), Mie/point-dipole validation failure, I2 Born inversions (radial, voxel), I3 nonlinear inversion and identifiability; MCI detectability vs solve-to-solve floor | `imaging/*`; imaging report §2–6; CR §F, E3 | `i1_ring_plane.png`, `i2h_inversions.png`, `i2h_voxel.png`, `i3_csf_thickness.png` (inspect) |
| 11 | The mesh-settings problem | v2 convergence tables; class-correlated settings; what the solve-to-solve SD does and does not measure; pre-registered re-solve test; lobe Setup1 table; mesh yardstick | MODEL_CARD Part 2, 4, 5.2; `data/sim_plan.csv`, `data/mesh_lobe.csv`; CR A7–A10, G13–G18, H8, §I; OQ B4, C1–C3 | new: convergence/elements bar chart per design |
| 12 | Lobe-sector layered phantom: build and frozen-rule transfer | professor's request; sector geometry, stages (Shehab Table 7, Saied lobe order), materials, symmetry by construction; sliced vs v2 healthy; frozen rule applied unchanged; why Mild_lobe fails `three` | **P02**, **P04**; prompts 07; `results/05_lobe/`; MODEL_CARD Part 5; CR §G1–G5; OQ D6, D7 | `3_ratios_lobe_vs_uniform.png`; new: top-view sector diagram with e_k per stage |
| 13 | Lobe-sector phantom: asymmetry and localisation | per-path change maps; I_FB/I_LR; cross-ratios χ and χ̃ (gain invariance); sector Born kernels, CRLB, sector inversion; radar; null distributions; mesh yardstick; pre-registered blind tests (status) | `scripts/07_lobe.py`, `imaging/study_lobe.py`, `mesh_lobe.py`; `results/05_lobe/`, `results/imaging/lobe_*`; CR §G6–G18, §H | `4a_path_change_maps.png` (regenerate: tick overlap), `lobe_maps.png`, `lobe_kernels.png`, `lobe_null_lr.png` |
| 14 | CST voxel-head track | model, antennas, band, settings, results, how it answers the array-requirements analysis | **P03**; imaging report §7; OQ E1–E2 | from P03 |
| 15 | Professor's review asks and answers | each ask → what was done → where it is answered | **P04**; all chapters | table |
| 16 | Discussion, limitations, conclusions | detection vs staging vs localisation verdict; within-simulation vs generalisation; mesh confound; air-path dependence (coupling medium would suppress it); required next simulations (heads, stand-off, re-solves) | STATUS §5–6; audit §7; imaging §6–7; CR all | new: summary "can / cannot" table figure |
| A | Appendices | full notation and glossary; claims register; reproducibility (commands, commit hashes, requirements); data manifest | `docs/notation.md`, `docs/01_claims_register.md`, INV §2–3 | — |

## Order of work (proposed)

1. Merge Packs 01–04 as they arrive (update INV, CR, notation, OQ; list contradictions). **No chapters yet.**
2. On your go-ahead: chapters 2 and 4–5 first (foundations), then 3 (S0, after Pack 01), then 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 1 → 16 (introduction and conclusions last).
3. Study notes for each chapter written together with that chapter.
4. Figures regenerated only where INV §4 says "No"/"Partly" or a new figure is listed.
5. Presentation after the report is complete.

## Rules carried into every chapter

- Every number has a path (file or pack §) and a VERIFIED/REPORTED tag in the notes.
- Status labels from the analysis sessions are kept; superseded statements (e.g. stale k = 3 delays, M5.C2 headline) are explained, not silently replaced.
- Within-simulation noise robustness (NR), cross-solve same head (XS) and generalisation are never mixed. Nothing here is generalisation.
- One notation (`docs/notation.md`); plain-language path and lobe names in figures.
