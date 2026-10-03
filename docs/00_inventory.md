# 00 — Repository inventory (Phase 0)

Written 2026-10-03 at HEAD `ecacd35` (branch `master`). Read-only survey; nothing outside `docs/`
was changed. Notation: `docs/notation.md`. Tags: **VERIFIED** (I saw it in code, data or the file
system), **REPORTED** (stated in a project document, not re-checked), **UNKNOWN**.

Project stages used throughout (my labels, to be confirmed by you):

| Stage | Name | Where it lives |
|---|---|---|
| S0 | Single-layer sector / cross-section phantom (8 antennas, R = 58 mm sphere) | **Not in this repo.** Only `blind_validation_presentation.pptx` (untracked) and `references/imaging_code.m`. Pack 01 expected |
| S1 | 7-layer sphere, dataset **v1** (mixed HFSS projects), QC + metrics + classifiers | `data/archive/v1_mixed_projects/`, git history up to `e9bced0` |
| S2 | Imaging / localisation study on the sphere (I1 radar, I2 Born, I3 nonlinear) | `imaging/`, `results/imaging/report.md` |
| S3 | Dataset **v2** (one project, + MCI), cross-solve tests with v1 as repeats | `data/raw/new_*.s6p`, `results/02`, `03`, `v2_with_v1_repeats/` |
| S4 | Likelihood/divergence analysis, ratio lead, audit, frozen rule | `results/04/` |
| S5 | HFSS field exports, Born physics of the ratios | `data/fields/` (not in git), `results/imaging/report.md` §4 |
| S6 | Mesh-settings problem found; equal-settings re-solves planned | `MODEL_CARD.md` Part 2/4, `data/sim_plan.csv` |
| S7 | Lobe-sector layered phantom (lobe_v1): analysis + imaging, pre-registered blind tests | `data/raw/new_with_slices_*`, `results/05_lobe/`, `results/imaging/lobe_*` |
| S8 | CST voxel-head track | **Not in this repo.** Only `results/imaging/report.md` §7 ("for the CST voxel model"). Pack 03 expected |

---

## 1. Folder tree (important files only; 308 files on disk, 260 tracked by git)

Dates are file-modification dates (VERIFIED, `find -printf`). "untracked" = present on disk but not in git (VERIFIED, `git status`, `git ls-files`).

```
MultiLayerImaging_v1/
├── MODEL_CARD.md                 S1–S7  phantom facts, verification status, Parts 1–5 (2026-10-03 22:31)
├── README.md                     S1     how to regenerate (run_all.py); short
├── blind_validation_presentation.pptx  S0  UNTRACKED. 14 slides, single-layer 8-antenna study (2026-09-20)
├── config.yaml                   S1–S4  every tunable: grid, classes, ring map, QC, gate, augment, classify
├── config_repeats.yaml           S3–S4  overlay: v2 + v1-as-repeats manifest → results/v2_with_v1_repeats/
├── config_lobe.yaml              S7     overlay: lobe manifest → results/05_lobe/
├── requirements.txt              —      pinned versions (Python 3.12.6, numpy 2.3.5, scipy 1.18.0, sklearn 1.9.0 …)
├── cluster/                      —      Praganak SLURM scripts + README (CPU-only)
├── data/
│   ├── sims.csv                  S3     manifest of v2 (5 solves): authoritative labels
│   ├── sims_with_repeats.csv     S3–S4  v2 + 4 v1 solves as repeats (9 solves)
│   ├── sims_lobe.csv             S7     manifest of lobe_v1 (4 solves)
│   ├── sim_plan.csv              S6–S7  planned/running HFSS solves (not read by code)
│   ├── mesh_lobe.csv             S7     HFSS Setup1 convergence table for lobe_v1 (from user)
│   ├── raw/new_*.s6p             S3     v2 Touchstone files (5) — tracked
│   ├── raw/new_with_slices_*.s6p S7     lobe_v1 Touchstone files (4) — UNTRACKED
│   ├── archive/v1_mixed_projects/ S1    v1 Touchstone files (4), sims.csv, README.md
│   ├── fields/E_Normal_T*_*.fld  S5     19 HFSS E-field exports, ~48 MB each (~880 MB) — git-ignored
│   └── processed/common_grid.npz —      cache, git-ignored
├── src/adstage/                  S1–S4  shared analysis package (parser, masking, features, noise, gate, CV, frozen rule)
├── scripts/                      S1–S7  00_qc, 01_compare_solves, 02_metrics, 03_classify, 04_likelihood, 05_audit, 07_lobe, run_all
├── imaging/                      S2,S5,S7  imaging/localisation code (Mie, Born, beamforming, I1–I3, ratios, lobe)
├── tests/, imaging/tests/        —      unit tests (parser, masking, folds, gate, R31 and χ gain cancellation, Mie, Born, DMAS …)
├── prompts/                      S7     UNTRACKED. Only 07 and 08 present (01A–06 missing)
├── references/                   —      Shehab 2025 PDF, Saied 2022 PDF, imaging_code.m (2-D DBIM script)
└── results/
    ├── STATUS.md                 S3–S7  professor-facing status (3 Oct)
    ├── summary.md                S1–S4  running summary per prompt
    ├── metrics.csv               S1–S4  append-only log of every metric/classifier row (6.5 MB)
    ├── qc/                       S3     QC of v2 (+ solve_comparison.md v1 vs v2)
    ├── 02/, 03/, figures/        S3     prompt 02/03 on v2 only ("run 1", code f142bf6)
    ├── v2_with_v1_repeats/       S3     prompt 02/03 on 9 solves ("run 2", code c95604c) — basis of STATUS §1
    ├── 04/                       S4     likelihood report, frozen_rule.json, audit/
    ├── 05_lobe/                  S7     lobe analysis (Prompt 07)
    └── imaging/                  S2,S5,S7  report.md, lobe_report.md, frozen pipeline, figures, caches (caches git-ignored)
```

**Important:** the prompt-02/03 numbers for the **v1** set quoted in `results/summary.md` (e.g. τ = −52.69 dB, M5.C3 CV 0.977) are no longer in the working tree: `results/02` and `results/03` were overwritten by the v2 run on 2026-10-01. They exist only in git history (`8105ac1`, `047c2e1`). VERIFIED (`git show 8105ac1:results/03/report.md` lists the four v1 files).

### 1.1 Key documents

| Path | What it is | Stage | Notes |
|---|---|---|---|
| `MODEL_CARD.md` | Supplied facts (Part 1), v1 verification (2), v2 verification (3), field-export facts + pre-registered re-solve test (4), lobe set (5) | S1–S7 | The central fact sheet. Part 1 numbers are user-supplied |
| `results/STATUS.md` | Plain-language status for the professor; §1–5 as of 2 Oct, §6–7 3 Oct | S3–S7 | Quotes stale v1 k=3 delays (notation §9.6) |
| `results/summary.md` | Running summary, newest first: prompt 04, v2 cross-solve, prompt 03 follow-ups, 03, 02, 01A | S1–S4 | Prompt 02/03 sections describe v1 numbers |
| `results/04/audit/report.md` | Audit of the ratio staging lead (6 sections + claims + falsification criteria) | S4 | Code 2baddee |
| `results/05_lobe/report.md` | Lobe analysis: floors, sliced vs v2 healthy, frozen rule, asymmetry, mesh scale, claims | S7 | Code bac41d4 |
| `results/imaging/report.md` | Imaging study on v2: paths, I1, Mie validation, I2 (HFSS fields), ratios §4.7, I3, verdict, array requirements §7 | S2,S5 | Code d9ddc7e |
| `results/imaging/lobe_report.md` | Lobe imaging: kernels, CRLB, sector inversion, radar, nulls, mesh yardstick, blind-test (pending), verdict | S7 | Code fb5b775 + §5b added later |
| `results/05_lobe/predictions.md` | PRE-REGISTERED LeftOnly_test path predictions | S7 | Committed `cf56de8` |
| `results/imaging/lobe_predictions.md`, `lobe_frozen.json` | PRE-REGISTERED blind predictions (LeftOnly_test, MCI_lobe) + frozen κ, λ, thresholds | S7 | Committed `62709e0` |
| `results/04/frozen_rule.json` | Frozen detection (R31 τ, m) and staging (LDA on R21; LDA on R32) rule | S4 | "Do not edit" |
| `prompts/07_lobe_analysis_prompt.md`, `08_lobe_imaging_prompt.md` | Briefs given to the analysis and imaging sessions for the lobe phantom | S7 | Untracked |
| `references/Alzehimer_stages_human_head_phantom.pdf` | J. N. Shehab, M. J. Farhan, S. Al-Azawi, *Results in Engineering* 27 (2025) 106350, doi:10.1016/j.rineng.2025.106350 — source of stage radii (Table 6), materials (Table 5), lobe stages (Table 7) | — | VERIFIED (PDF metadata) |
| `references/Classification_of_Alzheimers_Disease_Using_RF_Signals_and_Machine_Learning.pdf` | I. M. Saied, T. Arslan, S. Chandran, *IEEE J-ERM* 6(1), Mar 2022, pp. 77–85 — 6 antennas, 9 head models; lobe order Table II; "98.97 %" benchmark | — | VERIFIED (page 1) |
| `references/imaging_code.m` | MATLAB 2-D DBIM script: incident/total CSV fields, XY plane at z = 94.5 mm, 2-D Green's function, ε_obj = 18 test rectangle | S0? | Belongs to pre-repo work; which stage is UNKNOWN |
| `blind_validation_presentation.pptx` | 14-slide deck: "8-Antenna DGS Array, Spherical Phantom", sphere R = 58 mm, 6 × 60° sectors, 8 antennas (6 equatorial + 2 top), 2.7–4.1 GHz 71 pts, Port 2 excluded (VSWR > 4), 5 blind cases, 4/5 "correct or partial", SVD clutter attempts | S0 | Untracked; python-pptx generated; numbers REPORTED only |

## 2. Datasets

All Touchstone facts in the first table were **VERIFIED** by parsing each file with the project's own parser (`src/adstage/io/touchstone.py`, read-only) on 2026-10-03: 6 ports, option line `# GHz S MA R 50.000000`, uniform step. Design/project names are from the file headers, which the pipeline deliberately does not trust; they agree with the manifests.

| File | Set | Stage label (manifest) | Phantom | HFSS project / design (header) | Band (GHz) | Points / step | Ports (Port 1…6) |
|---|---|---|---|---|---|---|---|
| `data/archive/v1_mixed_projects/raw/brain_sevem_layer_Healthy.s6p` | v1 | Normal | 7-layer sphere, uniform | new / Healthy | 2.8–4.2 | 281 / 5 MHz | T4,T3,T2,T1,T6,T5 |
| `…/Brain_sevem_layer_MildAD.s6p` | v1 | Mild | same | Brain_sevem_layer / MildAD | 2.8–4.2 | 281 / 5 MHz | same |
| `…/Brain_sevem_layer_ModerateAD.s6p` | v1 | Moderate | same | Brain_sevem_layer / ModerateAD | 2.8–4.2 | 281 / 5 MHz | same |
| `…/brain_sevem_layer_SevereAD.s6p` | v1 | Severe | same | new / SevereAD | **3.2–4.2** | **501 / 2 MHz** | same |
| `data/raw/new_Healthy.s6p` | v2 | Normal | same | new / Healthy | 2.8–4.2 | 281 / 5 MHz | same |
| `data/raw/new_MCI.s6p` | v2 | MCI | same, r_hip 21.25 | new / MCI | 2.8–4.2 | 281 / 5 MHz | same |
| `data/raw/new_MildAD.s6p` | v2 | Mild | same | new / MildAD | 2.8–4.2 | 281 / 5 MHz | same |
| `data/raw/new_ModerateAD.s6p` | v2 | Moderate | same | new / ModerateAD | 2.8–4.2 | 281 / 5 MHz | same |
| `data/raw/new_SevereAD.s6p` | v2 | Severe | same | new / SevereAD | 2.8–4.2 | 281 / 5 MHz | same |
| `data/raw/new_with_slices_Healthy_sliced.s6p` | lobe_v1 | Normal | lobe-sector layered sphere | new_with_slices / Healthy_sliced | 3.2–4.2 | 201 / 5 MHz | same |
| `data/raw/new_with_slices_Mild_lobe.s6p` | lobe_v1 | Mild | same, e = 0/7.5/11.5/0/11.5/7.5 (header VERIFIED) | new_with_slices / Mild_lobe | 3.2–4.2 | 201 / 5 MHz | same |
| `data/raw/new_with_slices_Moderate_lobe.s6p` | lobe_v1 | Moderate | same, e = 11.5/12.5/15.5/0/15.5/12.5 | new_with_slices / Moderate_lobe | 3.2–4.2 | 201 / 5 MHz | same |
| `data/raw/new_with_slices_Severe_lobe.s6p` | lobe_v1 | Severe | same, e = 15.5/17.5/18/11.5/18/17.5 | new_with_slices / Severe_lobe | 3.2–4.2 | 201 / 5 MHz | same |
| `data/fields/E_Normal_T{1..6}_{3p4,3p6,3p8}GHz.fld` + `E_Normal_T1_3p6GHz_wide.fld` | fields | Normal (v2) | complex E, 61³ nodes, 3 mm grid ±90 mm (wide: ±120 mm / 4 mm) | new / Healthy, HFSS 2024.2 | 3.4, 3.6, 3.8 | — | one file per driven antenna, 1 V incident, others matched |

Field-file facts: 19 files present, ~48.4 MB each (VERIFIED, file system); grid and source description REPORTED (`imaging/fields.py` docstring, `results/imaging/report.md` §4.0).

**Solver settings per dataset (all REPORTED, user-supplied from HFSS dialogs).**

| Set | Adaptive settings | Per-design convergence | Sweep | Source |
|---|---|---|---|---|
| v1 | UNKNOWN (mesh stats not in files; user said only sweep settings differ from v2) | UNKNOWN | UNKNOWN type; Severe exported 3.2–4.2 GHz / 2 MHz | `MODEL_CARD.md` Part 2; `data/sims_with_repeats.csv` header |
| v2 | max 6 passes, 30 % refinement; Max ΔS **0.02** (Normal, MCI) vs **0.05** (Mild, Moderate, Severe) | Normal: 6 passes, NOT converged. MCI: 5 passes, ΔS 0.0200, 910,960 tets. Mild: 4, 0.0410, 672,508. Moderate: 6, 0.0261, 569,697. Severe: 6, 0.0288, 606,640 | interpolating, 281 points; field exports: 3-point discrete | `MODEL_CARD.md` Part 2 (VERIFY table) |
| lobe_v1 | adaptive at 3.4 GHz, Max ΔS 0.02, max 8 passes, 30 %, first-order basis, iterative solver | Healthy_sliced 7 passes, 0.0092, 1,349,491 elements, min converged passes 2. Mild_lobe 5, 0.0186, 739,774, 1. Moderate_lobe 5, 0.0194, 796,281, 1. Severe_lobe 5, 0.019999, 690,077, 1 (marginal) | interpolating 3.2–4.2 GHz, 201 points; FieldSweep disabled | `data/mesh_lobe.csv`; `MODEL_CARD.md` 5.2; `prompts/07…` §1.5 |
| Normal mesh repeat (attempt 2026-10-02) | ΔS 0.01 but still 6 passes | "bit-identical to new_Healthy.s6p and is not a repeat" | — | `data/sim_plan.csv` |

**Phantom geometry and materials** (REPORTED from `MODEL_CARD.md` Part 1 and 5.1; sphere radii also hard-coded in `imaging/common.py`, VERIFIED).

Uniform sphere, outer radius in mm (skin 88, fat 87.5, skull 86.5, CSF outer 83.5 fixed):

| Layer | Normal | MCI | Mild | Moderate | Severe |
|---|---|---|---|---|---|
| Gray matter | 83 | 83 | 70.55 | 66.05 | 62.25 |
| White matter | 76 | 76 | 64.6 | 60.8 | 57 |
| Hippocampus (central sphere) | 25 | 21.25 | 17.5 | 12.5 | 7.5 |

Materials (ε_r / σ S/m, static, Shehab 2025 Table 5 at 3.241 GHz; Normal back-calculated):

| Tissue | Normal | Mild | Moderate | Severe |
|---|---|---|---|---|
| Hippocampus | 47.7 / 2.42 | 39.11 / 5.687 | 38.39 / 5.92 | 37.2 / 6.413 |
| White matter | 35.3 / 1.65 | 31.77 / 2.39 | 31.064 / 2.722 | 30.35 / 2.88 |
| Gray matter | 47.7 / 2.42 | 40.3 / 5.203 | 39.11 / 5.687 | 38.39 / 5.92 |
| CSF | 65 / 4.27 | 55.25 / 4.91 | 48.75 / 5.337 | 32.5 / 6.405 |

Skin, fat, skull materials: **UNKNOWN** (OPEN-GUI in MODEL_CARD). The imaging code **assumed** skin 37/2.0, fat 10.5/0.42, skull 10.8/0.61 (`imaging/common.py`, flagged there). MCI hippocampus material: UNKNOWN for v2 (imaging code uses Normal material); 40.3/5.203 for MCI_lobe (MODEL_CARD 5.1).

Lobe phantom: skull 83.5–86.5, fat 86.5–87.5, skin 87.5–88 mm; skull inner radius set explicitly to 83.5 mm (v2: hidden tool `Brain_sphere_1`, radius UNKNOWN). Healthy materials checked in the HFSS material table by the user (MODEL_CARD 5.2, REPORTED).

**Header variables (untrusted, listed for completeness).** Every v1/v2/lobe header lists project variables including `L = 42mm, W = 35mm, $L = 85mm, $W = 35mm, H = 1.575mm, slot_distance = 15mm, ant_dist = 115mm, z_ebg = -94.575mm, r_brain = 95mm, r_csf = 95.5mm, r_gray = 70.55mm, r_white = 17.5mm, r_csf_outer = 83.5mm …` (VERIFIED by reading the headers). Several of these (e.g. `r_gray = 70.55mm`, `r_white = 17.5mm` in the **Healthy** file) are project-wide variables whose use per design is UNKNOWN; they are not evidence of the geometry.

**Pending / planned files (none present).** `new_Healthy_meshrep`, `new_MCI_rep`, `new_SevereAD_eq`, `new_ModerateAD_eq` (running from 2026-10-02), `new_MildAD_eq` (planned), `new_with_slices_{Mild,Moderate,Severe}_lobe_m2`, `…_LeftOnly_test_m2`, `…_MCI_lobe_m2` (running from 2026-10-03). Source `data/sim_plan.csv` (REPORTED status).

## 3. Analysis scripts

Run commands are from each file's docstring (VERIFIED). "Result" = where its output is committed.

| Script | Inputs | Method (one line) | Outputs / result files |
|---|---|---|---|
| `scripts/00_qc.py` (Prompt 01A) | manifest in config, raw `.s6p` | Parse, integrity (passivity, reciprocity, glitches), circulant symmetry floor, 60-ordering port-map search, confound table | `results/qc/*.csv`, `qc_report.md`, `results/figures/qc_ring_modes.png`, `data/processed/common_grid.npz` |
| `scripts/01_compare_solves.py` | v1 archive vs v2 | Whole-spectrum ring-mode dB differences and C3/R31 shifts between two solves of the same stage | `results/qc/solve_comparison.md` |
| `scripts/02_metrics.py` (Prompt 02) | config manifest | Glitch masking, M0–M8 metrics under 6 noise profiles, Fisher/Bhattacharyya separability, frequency-robustness and fault tests, ordinality | `results/02/*.csv`, `report.md`, `results/figures/02_*.png`, rows in `results/metrics.csv` |
| `scripts/03_classify.py` (Prompt 03 + follow-ups) | config manifest | Quality gate, setup perturbation, leakage-aware CV (LOSO / LODO), 7 models × 12 feature sets, thresholds τ ± m, floor subtraction, R31, gain profiles, per-measurement rule | `results/03/*` (`decision_rule.md`, `thresholds.csv`, `cv_*`), `results/figures/03_*.png`, `metrics.csv` |
| `scripts/run_all.py` | `--config` | Runs 00 → 02 → 03 | as above (run 1: `results/`, run 2: `results/v2_with_v1_repeats/`) |
| `scripts/04_likelihood.py` (Prompt 04) | `config_repeats.yaml` (9 solves) | Gaussian class models with shrunk between-solve covariance; symmetric KL and Bhattacharyya with/without between-solve term; LOSO QDA/LDA; MI ranking | `results/04/{report.md, divergences.csv, loso.csv, confusion.json, mi.csv, shrinkage.csv, per_solve_values.csv, figures/}` |
| `scripts/05_audit.py` | 9 solves | Repeat independence, nested feature selection inside LOSO, exact permutation test, per-solve values, band robustness, hardware/floor sweep; writes the frozen rule | `results/04/audit/*`, `results/04/frozen_rule.json` |
| `scripts/07_lobe.py` (Prompt 07) | `data/sims_lobe.csv` | Symmetry floors, Healthy_sliced vs v2 Normal, frozen rule unchanged on lobe designs, ΔP maps, I_FB/I_LR, χ and χ̃, mesh scale, pre-registered LeftOnly predictions | `results/05_lobe/*` |
| `imaging/run_imaging.py` → `paths`, `stage_snr`, `study_i1`, `forward`/`mie` (val), `study_i2` / `study_i2_hfss`, `study_ratios`, `study_i3`, `report*.py` | current config (v2) + `data/fields/` | Group-delay path test; raw-data SNR; DAS/DMAS/MVDR; layered-sphere Mie + point-dipole validation; Born sensitivity, radial/voxel inversions; Born test of R21/R31/R32; 9-parameter LM inversion | `results/imaging/{report.md, metrics_imaging.csv, summary.json, figures/i1_*, i2h_*, i3_*, k3_*, ratios_*}` |
| `imaging/run_lobe.py` → `study_lobe.py`, `report_lobe.py` | lobe_v1 files + `data/fields/` | Sector Born kernels, CRLB, Tikhonov / bounded / gain-invariant sector inversion (κ, λ on Mild), radar, null distributions, frozen rules R1–R3; `--blind` scores LeftOnly/MCI later | `results/imaging/{lobe_report.md, lobe_predictions.md, lobe_frozen.json, figures/lobe_*}` |
| `imaging/mesh_lobe.py` | v2 Normal + Healthy_sliced | Passes the healthy-vs-healthy (mesh) difference through the frozen lobe inversion | `results/imaging/lobe_mesh_yardstick.json`, `lobe_report.md` §5b |

Core library (`src/adstage/`): `io/touchstone.py` (parser), `io/masking.py` (glitches), `io/dataset.py` (loader, common grid), `features/metrics.py` (M0–M8), `features/floor.py` (P_f, R31), `features/ring_features.py` (89 features, ratios), `noise/model.py` (profiles), `noise/reference.py` (solve SD), `pipeline/{augment, cv, classify, quality, rule}.py`, `frozen.py` (applies the frozen rule), `separability.py`, `robustness.py`. All VERIFIED by reading.

Tests: `tests/test_touchstone.py` (16 tests incl. gate, folds, R31 and χ gain cancellation), `imaging/tests/test_imaging.py` (18 incl. Mie, reciprocity, Born vs exact), `imaging/tests/test_lobe.py` (4). Test results were **not re-run** by me.

## 4. Existing figures

"Inspected" = I opened the image. "Usable as-is" is my judgement against the report rules (plain-language labels, readable, correct).

| Path | What it shows | Inspected | Usable as-is? |
|---|---|---|---|
| `results/imaging/figures/i2h_k3_path.png` | |E_T1| and |E_T1·E_T4| maps (x = 0 and ring plane, 3.6 GHz) + field along the arc vs the chord T1→T4 | yes | **Yes** (STATUS slide fig. 1). Could add "around the head / through the head" labels |
| `results/v2_with_v1_repeats/figures/03_severity_index.png` | Histograms of full-band opposite-path power per view, 6 noise profiles, τ and margin | yes | **Partly**: axis says "M5.C3" (internal code); five stage colours are near-identical blues, MCI vs Normal hard to tell apart. Regenerate with plain labels |
| `results/v2_with_v1_repeats/figures/03_gain_errors.png` | Balanced accuracy and no-decision rate vs per-port gain error, C3 vote / ring mean vs R31 | yes | **Yes** with a caption translating "M5.C3"/"M5.R31" |
| `results/imaging/figures/i2h_detectability_radial.png` | SNR of a 1 cm³ blob vs radius, per path type, absolute and κ-calibrated | yes | **Yes**; legend uses "k=0..3" → rename to path names |
| `results/imaging/figures/k3_path_time.png` | Time-domain ring modes (Normal) and Mild − Normal, with creeping vs straight predictions | yes | **No**: right panel title truncated; legend "k=0…3"; title says 3.2–4.2 GHz while the v2 report uses 2.8–4.2 GHz (check which data produced it) |
| `results/05_lobe/figures/3_ratios_lobe_vs_uniform.png` | R31/R21/R32 for lobe and uniform solves with frozen boundaries | yes | **Yes** |
| `results/05_lobe/figures/4a_path_change_maps.png` | 6×6 ΔP maps (stage − Healthy_sliced), per lobe stage | yes | **No**: x-axis tick labels overlap ("Temporal L" / "Parietal L" collide). Regenerate |
| `results/imaging/figures/lobe_maps.png` | Polar lobe maps: true vs recovered dε″ for 3 methods × 3 stages | yes | **Yes** (dense; fine for report, crop for slides) |
| `results/imaging/figures/lobe_kernels.png` | Pair × region Born kernel heatmap (3.6 GHz, plain path names) + singular values | yes (D0b) | **Yes** |
| `results/imaging/figures/lobe_radar.png` | DAS/DMAS images of lobe dS, ring plane | yes (D0b) | **No**: panel titles overlap each other |
| `results/imaging/figures/lobe_null_lr.png` | Null distribution of LR_inv with ±T_LR, mirror-symmetric designs and the pre-registered LeftOnly band | yes (D0b) | **Yes** |
| `results/imaging/figures/i1_ring_plane.png` | DAS/DMAS/MVDR ring-plane images, noise-only + 4 stages (v2) | yes (D0b) | **Yes** |
| `results/imaging/figures/i1_vertical_plane.png`, `i1_radial_profiles.png` | I1 vertical images and radial profiles (v2) | no | UNKNOWN |
| `results/imaging/figures/i2h_sensitivity_maps.png` | Σ\|J\| per ring distance (ring plane, x = 0) + log SNR maps | yes (D0b) | **Partly**: "k=0…3" labels, last title truncated |
| `results/imaging/figures/i2h_inversions.png` | Radial inversion (synthetic, HFSS, noise-only), resolution diagonal, voxel PSF offset | yes (D0b) | **Yes** for the report (dense); not for slides |
| `results/imaging/figures/i2h_voxel.png` | Voxel inversion | no | UNKNOWN |
| `results/imaging/figures/i3_csf_thickness.png` | CSF thickness estimate vs k3 metric | no | UNKNOWN |
| `results/imaging/figures/ratios_kernels.png` | Radial kernels of C1, C2, R21 (left); shell-integrated path sensitivity incl. air (right) | yes (D0b) | **Yes** |
| `results/04/figures/04_divergence.png`, `04_mi_map.png` | Divergences with/without between-solve term; MI map | no | UNKNOWN |
| `results/04/audit/4_per_solve.png`, `6_floor_sweep.png` | Per-solve R31/R21/R32; R21 rule vs instrument floor | no | UNKNOWN |
| `results/figures/02_*.png` (5), `03_*.png` (5), `qc_ring_modes.png` | Prompt 02/03 run 1 on v2 only (5 solves) | no | UNKNOWN; superseded by run 2 for most claims |
| `results/v2_with_v1_repeats/figures/02_*.png` (5), `03_accuracy_vs_noise.png`, `03_confusion.png`, `03_coverage_accuracy.png`, `qc_ring_modes.png` | Run 2 versions | no | UNKNOWN |
| `results/05_lobe/figures/qc_ring_modes.png` | Lobe QC ring modes | no | UNKNOWN |
| `blind_validation_presentation.pptx` media (7 PNGs) | S0 single-layer results | no | UNKNOWN; Pack 01 decides |

No figure exists for: the phantom geometry (layered sphere, lobe sectors, antenna ring), the mesh-convergence tables, or a project timeline. These will need new figures in `docs/figures/`.

## 5. Timeline

Pre-repo items are dated by file-modification time only; repo items by commit date (+05:30). VERIFIED unless marked.

| Date | What | Evidence |
|---|---|---|
| ≤ 2026-09-20 | **S0** single-layer sector phantom, 8-antenna DGS array, blind validation (5 cases) and SVD clutter attempts; conclusion "next: multi-layer phantom" | `blind_validation_presentation.pptx` (mtime 2026-09-20), content REPORTED |
| 2026-09-23 | 2-D DBIM MATLAB script (incident/total fields, 6 antenna configurations) | `references/imaging_code.m` mtime |
| 2026-09-27 22:39–22:43 | v1 Touchstone files written (4 stages, two HFSS projects) | archive file mtimes |
| 2026-09-27 22:56 | Repo created: parser, loader, QC, model card (`89db27a`); QC run (`ea8be31`) — Prompt 01A | git |
| 2026-09-27 23:17–23:23 | Prompt 02: masking, metrics M0–M8, separability, robustness (`89d4f23` … `2e60be5`) | git |
| 2026-09-28 00:08–02:28 | Prompt 03: gate, augmentation, CV classifiers, thresholds; floor subtraction, R31, gain-invariant gate (`3ad19cb` … `047c2e1`) | git |
| 2026-09-28 → 09-29 02:36 | **S2** imaging study on v1: path test, I1, layered-sphere model, I2 (surrogate fields), I3 (`da22b5d` … `935f26d`) | git |
| 2026-09-30 | Shehab 2025 paper added; cluster scripts; parallel I3 (`e9bced0`, `5968676`) | git |
| 2026-10-01 00:32–00:41 | **S3** v2 files written; switch to v2 (+ MCI), v1 archived; v1-vs-v2 solve comparison (`4495539`) | git, file mtimes |
| 2026-10-01 01:25–11:09 | Run 1 on v2 (`8523dac`); config overlays; Run 2 with v1 as repeats, cross-solve LOSO (`9741265`) | git |
| 2026-10-02 01:36 | **S5** HFSS field exports written | `data/fields` mtimes |
| 2026-10-02 02:00–02:59 | I2 with HFSS fields; MODEL_CARD Part 4 (ring +z, T1 at −90°, polarisation); STATUS.md created; sim_plan.csv (`18b1573` … `41b66bc`) | git |
| 2026-10-02 03:06–03:08 | **S4** Prompt 04 likelihood/divergence (`5c060e3`, `2304dc3`) | git |
| 2026-10-02 03:29 | Imaging ratio study: Born test of R21/R31/R32 (`a0cfb85`) | git |
| 2026-10-02 03:39–10:59 | Audit of the ratio lead; **frozen rule** written (`2baddee`, `5192287`) | git |
| 2026-10-02 11:56–13:08 | Imaging report §4.7; all v2 imaging results recomputed (`1728899`, `d9ddc7e`, `7dca095`) | git |
| 2026-10-02 16:00–16:13 | **S6** HFSS convergence tables: v2 settings differ by class (ΔS 0.02 vs 0.05; Normal not converged); pre-registered re-solve test; re-solves started (`c66f473` … `3f993a4`) | git |
| 2026-10-03 21:06–21:07 | **S7** lobe_v1 Touchstone files written | file mtimes |
| 2026-10-03 21:11 | Prompts 07 and 08 written | file mtimes |
| 2026-10-03 21:24–21:25 | Prompt 07 analysis; LeftOnly predictions **pre-registered** (`7ccec7f`, `cf56de8`) | git |
| 2026-10-03 22:30–22:32 | Lobe mesh table from user: lobe_v1 mesh-unmatched; identical-mesh claim retracted; mesh-scale section; MODEL_CARD Part 5; STATUS §7 (`cd4a7cc` … `4073d25`) | git |
| 2026-10-03 22:36–22:43 | Prompt 08 lobe imaging; blind predictions **pre-registered** (`fb5b775`, `62709e0`); mesh yardstick §5b (`6db4c39`, `ecacd35`) | git |
| after 2026-10-03 | **S8** CST voxel head | UNKNOWN (no files) |

Order of the work (one line): single-layer 8-antenna sector phantom (S0) → 7-layer sphere v1, metrics and classifiers (S1) → imaging/localisation on the sphere (S2) → re-solved v2 + MCI and cross-solve tests (S3) → field exports, likelihood, audit, frozen rule (S4–S5) → mesh-settings confound found (S6) → lobe-sector phantom, frozen-rule transfer, pre-registered localisation tests (S7) → CST voxel model (S8, outside this repo).
