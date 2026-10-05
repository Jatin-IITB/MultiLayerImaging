# Microwave sensing of Alzheimer's-related brain change: simulated S-parameters, detection, staging and imaging

Dual Degree Project, IIT Bombay. Student: Jatin Gupta. Supervisor: Prof. Anirban Sarkar.

Six patch antennas sit on one ring around a layered spherical head phantom, simulated in Ansys HFSS. The
question is how much the antenna-to-antenna signals (6-port S-parameters) reveal about Alzheimer's-type
change in the brain:
- **detection:** healthy vs AD;
- **staging:** Mild / Moderate / Severe;
- **localisation:** which lobes changed.

This repository holds the simulated Touchstone files, every analysis script, the committed results and the
review history.

> Everything here is **simulation of one idealised head**. Results show what the data can carry in a
> controlled setting, not performance on people.

---

## Status at a glance (4 Oct 2026)

The live versions are [`results/STATUS.md`](results/STATUS.md) and [`MODEL_CARD.md`](MODEL_CARD.md) Part 6.
Claims are graded against a noise floor (§ How results are judged).

| Question | Answer so far |
|---|---|
| **Detection** (healthy vs AD) | A calibration-free ratio of ring-averaged path powers (R31, threshold fitted on the uniform heads) separates healthy from AD. It holds for the healthy, Mild and Moderate lobe designs. Severe and one-sided disease sit near the threshold. Antenna gain cancels exactly. |
| **Staging** | The stage order is visible, but the labels have small margins. The staging ratio (R21) rests on the weakest paths (≈ −55 dB). Disease confined to a few lobes reads as Normal. Mild vs Moderate is not separable. |
| **Which lobes changed** | `imaging2` estimates the stage and one cortex-retreat value per lobe from the S-parameters, then draws the change on the known healthy anatomy. In leave-one-design-out tests the lobe calls are correct for Mild (5–6 of 6), Moderate and the one-sided design (6 of 6). Healthy, MCI and rotated healthy heads come out empty. **Blind test (Test_B):** the two affected lobes and the stage were named correctly under a protocol committed before the file existed. |
| **Depth / height** | Depth is rough: 90% intervals cover the truth for 69% of affected lobes, or 78% after widening the noise model (post hoc). Height is **not observable** with one antenna ring: the vertical shape of every image comes from the lobe model. |
| **MCI** (hippocampus only) | Not detectable. The hippocampus is far below the sensing depth (≤ 4% of in-brain sensitivity lies below z = 0). |
| **Other approaches tried** | With this six-antenna ring and a 1 GHz band (21 paths, about 22 mm range resolution in tissue), radar focusing (DAS / DMAS / MVDR) did not resolve the lobes in our runs, and a linear Born sector inversion was outside its small-change validity (model error 56–67% of the change). Details in `results/imaging/`. |

---

## Where to start

| Read | For |
|---|---|
| [`results/STATUS.md`](results/STATUS.md) | Current state, newest first |
| [`MODEL_CARD.md`](MODEL_CARD.md) | Phantom geometry, materials, antennas, port mapping, data sets, and every claim with its status (Parts 5–6: lobe phantom, reviews, blind test, post-hoc checks) |
| [`results/HANDOVER.md`](results/HANDOVER.md) | Main analysis track: data inventory with checksums, frozen files, rulers, claims, exact rerun commands (§8) |
| [`results/imaging/HANDOVER.md`](results/imaging/HANDOVER.md) | First imaging track (radar, Born, sector maps): claims, rerun (§5), code map (§7) |
| [`results/imaging2/README.md`](results/imaging2/README.md) | Slice-image track: method, scores, controls, noise, blind test, post-hoc checks, reproduce (§13). One-page method note: [`METHOD_surrogate_inversion.md`](results/imaging2/METHOD_surrogate_inversion.md) |
| [`docs/notation.md`](docs/notation.md) | Symbols and definitions used everywhere |
| [`share_lobe_phantom_data/README.md`](share_lobe_phantom_data/README.md) | Self-contained description of the lobe-phantom data, for someone who only wants the files |
| [`docs/presentation_qa.md`](docs/presentation_qa.md) | Step-by-step explanations used for the 5 Oct review: forward model, inversion, why the ratios cannot locate lobes, how Fisher/KL get a spread, Severe depth, raw-phase ring, E-field numbers |
| [`results/presentation/`](results/presentation/README.md) | Review figures: the estimate drawn on the healthy head (true / estimated / error, slices), per-lobe charts |
| [`results/checks/`](results/checks/) | Independent recomputations (raw-phase ring numbers) |
| [`results/efield/`](results/efield/README.md) | E-field plots and worked numbers of the field exports (viewing only) |
| `*.pptx` (repo root) | Presentation decks |

---

## The simulated heads

**Coordinates:**
- The origin is the head centre, in mm. +z is up, the nose points toward −y, and **+x is the subject's left**.
- Antennas T1…T6 sit at azimuth −90° (T1, front), −30°, +30°, +90° (T4, back), +150° and −150°. T2 and T3 are on the left; T5 and T6 on the right.
- The feeds lie on one ring at z ≈ 48 mm (polar angle 60.5°, 97.7 mm from the origin), about 9 mm from the skin.
- Each antenna is an imported printed antenna (V-shaped copper radiator with a partial ground on a 20 × 20 mm Rogers RT/duroid 6010 board) with a 3 × 3 FR4 AMC reflector behind it. The antenna variables in the file headers (L, W, H and similar) belong to an earlier, deleted antenna: ignore them.

**Port order in every Touchstone file: Port 1..6 = T4, T3, T2, T1, T6, T5** (not T1..T6). This is verified
from the HFSS port positions and stated in each file header (`Port[1] = FEED_3_T4`, …).

**Layers** (outer radius, mm): skin 88, fat 87.5, skull 86.5, CSF 83.5, gray matter 83, white matter 76,
hippocampus 25. Tissue values follow Shehab et al. 2025 (healthy = Gabriel at ≈ 3.24 GHz) and are held constant
over frequency. Full tables are in `MODEL_CARD.md` Part 1 and `share_lobe_phantom_data/README.md`.

| Model | Files | What changes with stage |
|---|---|---|
| **Uniform layered head** | `data/raw/new_*.s6p` (set v2); the older v1 set is in `data/archive/v1_mixed_projects/` | Every layer shrinks uniformly (CSF widens) and tissue values change. Normal, MCI, Mild, Moderate, Severe. |
| **Lobe-sector head** | `data/raw/new_with_slices_*.s6p`, 3.2–4.2 GHz, 201 points | Gray/white matter are cut into six 60° sectors, one under each antenna (S1 frontal, S2 temporal L, S3 parietal L, S4 occipital, S5 parietal R, S6 temporal R). In sector k the cortex retreats by eₖ, and diseased sectors get the stage's tissue values. |

Lobe-sector designs (eₖ for S1…S6 in mm; hippocampus radius):

| Design | e (S1…S6) | r_hip | Role |
|---|---|---|---|
| Healthy_sliced, Healthy_sliced_new | 0 0 0 0 0 0 | 25 | reference (two solves) |
| MCI_lobe_c3 | 0 0 0 0 0 0 | 21.25 | hippocampus only |
| Mild_lobe, Mild_lobe_new | 0 7.5 11.5 0 11.5 7.5 | 17.5 | stage |
| Moderate_lobe, Moderate_lobe_c3 | 11.5 12.5 15.5 0 15.5 12.5 | 12.5 | stage |
| Severe_lobe, Severe_lobe_c3 | 15.5 17.5 18 11.5 18 17.5 | 7.5 | stage |
| LeftOnly_test_c3 | 0 7.5 11.5 0 0 0 | 17.5 | one-sided test |
| RightOnly_test | 0 0 0 0 11.5 7.5 | 17.5 | mirror of LeftOnly (replication) |
| Test_B | 0 11.5 0 0 7.5 0 | 17.5 | **blind test**; geometry withheld until all analyses had committed estimates |
| Null_rot07, Null_rot19 | 0 0 0 0 0 0 | 25 | healthy head with the whole model rotated 7° / 19° about z: same physics, different mesh |

The suffixes `_new` and `_c3` mark repeat solves of the same design with a different adaptive-mesh stop rule;
the sets are defined in the `config_lobe_*.yaml` files. `Moderate_lobe_new` and `Severe_lobe_new` duplicate
`Moderate_lobe` and `Severe_lobe` (to ~1e-8) and are not used.

**Labels are taken from the manifests, never from file headers:**
- `data/sims.csv` (uniform), `data/sims_lobe.csv` (lobe, with passes / ΔS / elements per solve);
- `data/sim_plan.csv` (what is solved or pending).

---

## Repository layout

| Path | Contents |
|---|---|
| `src/adstage/` | Library. `io/` (Touchstone parser, glitch masking, loader), `features/` (ring metrics), `noise/`, `pipeline/` (QC gate, augmentation, CV, classifiers), `inversion/`, `ring.py`, `separability.py`, `robustness.py`, `frozen.py` |
| `scripts/` | Main analysis track, numbered in run order. `00`–`05`: uniform heads (QC, metrics, classification, likelihood, audit and frozen rule). `07`–`13`: lobe phantom and adversarial reviews. `14`: RightOnly replication. `15`–`16`: Test_B blind protocol and scoring. `17`–`18`: post-hoc rotated-null rulers. `run_all.py` runs 00 → 02 → 03. |
| `imaging/` | First imaging track: beamforming (`beamform.py`), linear/Born inversion (`linear.py`, `forward.py`), field handling, lobe sector maps and reviews (`lobe_*.py`), blind/replication scorers |
| `imaging2/` | Slice-image track: surrogate model (`surrogate.py`), Bayesian inversion (`invert.py`), leave-one-design-out runs (`lodo.py`, `run_lobe2.py`), noise study, rendering and figures, blind protocol (`blind.py`), post-hoc checks (`posthoc.py`) |
| `results/` | Committed outputs. `02/` `03/` `04/` and `v2_with_v1_repeats/`: uniform heads. `05_lobe/`: lobe phantom, reviews, tests, Test_B score, post-hoc nulls. `imaging/` and `imaging2/`: imaging tracks. `qc/`, `figures/`. `metrics.csv` is append-only. |
| `data/` | `raw/` (Touchstone files), `archive/` (v1 set), manifests (`sims*.csv`, `sim_plan.csv`), `hfss_geometry_audit_Healthy_sliced.txt` |
| `docs/` | Inventory, claims register, notation, report plan, open questions. `context_packs/02_hfss_build/` holds the HFSS build scripts (lobe phantom, stage designs, test designs, geometry audit). |
| `config*.yaml` | One config per data set (uniform, uniform + repeats, lobe sets A / B / tests) |
| `tests/`, `imaging/tests/` | Unit and regression tests |
| `cluster/` | Job scripts for the IIT Bombay HPC (PBS for HFSS, SLURM for analysis) |
| `prompts/` | Briefs given to the analysis sessions (history) |
| `references/` | Source papers and the reference MATLAB imaging code |
| `share_lobe_phantom_data/` (+ `.zip`) | Self-contained subset of the lobe-phantom data for external users |

---

## Setup and tests

Python ≥ 3.11; the committed results were produced with 3.12.6 and the versions pinned in `requirements.txt`.

```bash
python -m pip install -r requirements.txt
python -m pytest -q                  # main library and scripts
python -m pytest imaging/tests -q    # imaging tracks
```

On Windows, run `export PYTHONIOENCODING=utf-8` (Git Bash) first. The repository path contains spaces, so quote it.

## Reproducing results

Every random draw is seeded, and report headers carry the git hash they were produced at. Exact, ordered
commands are in each track's handover:

- **Uniform heads:** `python scripts/run_all.py --no-csv`, then `scripts/04_likelihood.py` and `05_audit.py`.
  See `results/HANDOVER.md` §8.
- **Lobe phantom, reviews, replication, blind scoring:** `scripts/07_lobe.py` … `18_null_rulers.py`, in the
  order given in `results/HANDOVER.md` §8.
- **Imaging, first track:** `results/imaging/HANDOVER.md` §5.3. Never run `imaging/run_lobe.py` without `--blind`.
- **Slice images:** `results/imaging2/README.md` §13, starting with `python -m imaging2.run_lobe2 --sweeps 600`.

**Not in git:**
- `data/fields/` (≈ 880 MB of HFSS field exports, needed by the sensitivity maps in `imaging2` and by
  `scripts/12_review2_fields.py`);
- the HFSS project files (`.aedt`);
- local caches.

Ask for them if you need to rerun those parts.

---

## How results are judged

- **Pre-registration.** Predictions, blind protocols and frozen decision rules are committed *before* the data
  they apply to exist. Frozen files are never edited. Anything decided after seeing a result is labelled
  **post hoc**. The blind design's geometry was stripped from its file header and held back until every
  analysis had committed its estimates.
- **Rulers.** Each statistic is compared with a floor: the largest value seen in designs where the effect cannot
  exist. These are the symmetric designs and the rotated healthy heads (same physics, different mesh). The tiers
  are **≥ 3× established**, **2–3× sensitive**, **< 2× not determined**.
- **Sample size.** One simulated head per stage. Repeat solves test numerical robustness, not generalisation
  across people.

## Main limitations

- One idealised spherical head, with thin layers (skin 0.5, skull 3, CSF 0.5 mm) compared with real anatomy.
- Tissue values are held at their ≈ 3.24 GHz level; real conductivity is 28–38% higher at 4.2 GHz.
- Lobes are 60° full-height wedges aligned with the antennas, a favourable geometry.
- One antenna ring:
  - no height information;
  - about 99% of path sensitivity lies in the air around the head;
  - of the in-brain part, 56–69% lies above z = 40 mm.
- The weakest paths (second-neighbour, ≈ −55 dB) shift between equivalent simulations, which limits staging.
  Two more rotated healthy heads (31°, 43°) are pending. How they will be evaluated is pre-registered.

## Related work not in this repository

- An earlier single-layer sectored-sphere phantom (first cross-section study): a separate project folder.
- A CST voxel head model used to show the CSF compartment.

## Contact and reuse

Jatin Gupta, IIT Bombay (22b3967@iitb.ac.in). No licence has been chosen yet: please ask before reusing
code or data. The two PDFs in `references/` are published papers included for internal reference only.
