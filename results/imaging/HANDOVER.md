# HANDOVER — imaging session (Track A imaging / lobe localisation)

Written 2026-10-04. Last imaging code commit before this file: `226f9b1`. A fresh session should be able to
continue from this file alone. Everything below was checked against the repository on 2026-10-04: commit
hashes, sha256 prefixes, and a full re-run of the lobe chain (§5.3), which reproduced every committed result
apart from the embedded code-hash strings.

---------------------------------------------------------------------------------------------------------------

## 1. Role and ground rules (from the user, still in force)

**Role.** Imaging and localisation analysis of HFSS S-parameter simulations of a 7-layer sphere head with a
ring of 6 patch antennas. Two parts:
- **Track A (v1/v2 uniform-atrophy data).** Radar beamforming I1, HFSS-field Born inversion I2,
  model-based inversion I3, the ratio-lead physical test. Report: `results/imaging/report.md`.
- **Lobe-sector phantom (Prompts 08 onwards).** Sector kernels, CRLB, frozen sector inversion, a pre-registered
  blind test (LeftOnly_test, MCI_lobe), mesh/symmetry/measurement rulers, and two adversarial review rounds.
  Report: `results/imaging/lobe_report.md`; reviews `lobe_review.md` (round 1), `lobe_round2.md` (round 2).

A second session (the **main session**) owns the classifier / frozen-rule analysis (`scripts/`, `src/adstage/`,
`results/0x_*`, `MODEL_CARD.md`, `results/STATUS.md`, `data/sims*.csv`, `config*.yaml`). It commits concurrently.
A third directory, `imaging2/` + `results/imaging2/` (untracked), belongs to another session: **do not touch it**.

Rules, verbatim where quoted:
- "Your space: put all your code in `imaging/` and all outputs in `results/imaging/`. … Do not edit, move,
  reformat or delete anything outside these two folders."
- "Shared code is read-only for you. You may *import* the existing package (`src/adstage/…`) … If you need a
  change, copy the function into `imaging/` and modify the copy."
- "Do not append to `results/metrics.csv`." (Imaging metrics go to `results/imaging/metrics_imaging.csv`.)
- Git: "never `git add -A`, `git add .`, `git stash`, `git checkout <branch>`, `git reset`, or anything that
  touches the working tree globally. Stage only your paths: `git add imaging results/imaging`, then commit with
  a message prefixed `[imaging]`. If the index has other staged files, leave them alone and ask the user."
  Check `git diff --cached --name-only` before every commit. **Commit code first, then results.**
- Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Do not log in to the HPC cluster or handle passwords or credentials (the user does that).
- Do not open blind files before the predictions for them are committed.
- Predictions and frozen files (§3) are never edited.
- Review discipline the user requires: re-derive every number from code and data (command, number, file,
  commit). Give each item a verdict of CONFIRMED / CHANGED / CANNOT TELL. Never concede or defend without
  numbers. Answer every "why" with a mechanism or a measurement. Label phase-based claims **POST-HOC**.

---------------------------------------------------------------------------------------------------------------

## 2. Where things stand (one paragraph)

The pre-registered blind test gave **PARTIAL** with the frozen 7-pass reference (side left, S3 called, S2
missed) and **FAIL** with the stop-rule-matched reference. Neither reference is more credible. **MCI_lobe:
SUCCESS** (nothing called, nothing beyond any ruler). After two review rounds, sector-level values and calls
are **not results**: they flip with λ, reference and calibration, Born error is about the size of the signal,
and each sector is ≈ 80 % its own antenna. What remains is **[POST-HOC]**: the LeftOnly left/right sign is in
the data (mirror test passes) and is carried ≈ 85 % by phase. Its size is 1.93× (Tikhonov dS) to 2.77×
(whitened log) the clean ruler under the agreed floor rule. That is not established, and the rank p is 0.1
with nine null solves. Bias-corrected front/back is established only on the better-converged set (lobe_B).
A replication design (RightOnly_test) was proposed and its prediction committed.

**Update, 2026-10-04 (later):**
- **RightOnly_test was scored by the committed scorer: REPLICATED** (`rightonly_score.md`; `lobe_report.md` §10).
  LR −9.44 vs H6 and −9.83 vs H7 (predicted −6.9 ± 3.9, bar |LR| ≥ 7.8). The phase sign check is negative at 3.4
  and 3.6 GHz, and 83 % of LR comes from phase.
- [POST-HOC] Each mirror design alone is 2–3.4× the R1c ruler. Both lie beyond all nine nulls with the predicted
  opposite signs, so if the two meshes' asymmetries are independent the pair's rank p is about 0.01.
- **Test_B (blind) estimates were submitted** under protocol `24aa0c4`: affected none; possible S2; side none;
  front/back none; ranking S2 > S5 ≫ S3, S6, S1, S4 (`testb_report.md`; `lobe_report.md` §11). The user holds the
  truth and will score it. **Next action: record the user's score of Test_B (§5.6).**

---------------------------------------------------------------------------------------------------------------

## 3. Committed predictions and frozen files (never edit)

| file | role | committed in | content frozen at code | sha256 (first 16) |
|---|---|---|---|---|
| `results/imaging/lobe_predictions.md` | pre-registered blind predictions (LeftOnly_test, MCI_lobe) | `62709e0` (2026-10-03 22:37) | `fb5b775` (2026-10-03 22:36) | `f11ba5a50264b07e` |
| `results/imaging/lobe_frozen.json` | frozen pipeline: κ(f) at 3.4/3.6/3.8 GHz, λ_dS 0.1585, λ_log 0.1259, calling rules T_abs / T_LR / T_FB per method | `62709e0` | `fb5b775` | `9f3e9bb147f9a188` |
| `results/imaging/round2_predictions.md` | round-2 predictions: R3 detuning, C4 phase sign, **C6 RightOnly_test design + decision rule** | `0ceb626` (2026-10-04 11:52) | — | `8d7487e0e2277855` |
| `results/imaging/testb_protocol.md` | **blind protocol for Test_B** (references, methods, R1c rulers, fit rejection, reading rule, suggested scoring) | `24aa0c4` (2026-10-04 16:42), before Test_B was loaded | scorer `imaging/score_testb.py` at `b2f1472` | `b8922f0c0c7aedc2` |

Results scored against these (not to be edited either): `rightonly_score.md` (`6aed0b5aa9c55a4a`, written by the
unchanged `score_rightonly.py` of `226f9b1`), and `testb_report.md` / `testb.json` (commit `5818235`).

Known defect, recorded rather than fixed (the protocol forbids editing the scorer after loading): the reading
line in `testb_report.md` says "every reference that passed the gate". There is no gate in the committed
protocol (data-level size is context only). The references listed are simply the non-rejected ones, which here
are both.

Main-session frozen files I read but do not own: `results/05_lobe/predictions.md` (`cf56de8`, sha256
`e3e4cb45f95567f4`) and `results/04/frozen_rule.json` (`5192287`, `886911157b424a1b`; read via
`adstage.frozen.apply_rule` in round-2 R4 only).

Verify integrity: `sha256sum results/imaging/lobe_frozen.json results/imaging/lobe_predictions.md results/imaging/round2_predictions.md`

Frozen numbers, for reference (in `lobe_frozen.json`):
- κ ≈ 3.218−0.694j, 3.563+0.503j, 3.104+5.578j.
- T_abs 13.81 (dS methods) / 13.32 (log methods). T_LR 4.06 / 3.92 / 3.93 / 3.93. T_FB 6.45 / 3.78 / 7.83 / 4.53.
  Method order: tikhonov dS, bounded dS, tikhonov log (gain-inv.), bounded log (gain-inv.).
- The method named "gain-invariant" **is not gain-invariant** (erratum, `lobe_report.md` §5d). The frozen
  method is kept as is; the corrected post-hoc version is `lobe_rulers.WhitenedLog` ("whitened log").

---------------------------------------------------------------------------------------------------------------

## 4. Current claims table (rebuilt from scratch in round 2; source `results/imaging/lobe_claims.csv`)

Only CONFIRMED / CHANGED items. [POST-HOC] = built after unblinding.

| claim | verdict | items |
|---|---|---|
| Kernels come from 3-D volume field exports (±90 mm, 3 mm, 3.4/3.6/3.8 GHz, six excitations) of the v2 Normal head; no cut-plane was used | CONFIRMED | R7/G8 |
| Each field export peaks at its antenna's azimuth; the Port 1..6 = T4,T3,T2,T1,T6,T5 order and +X = subject's left hold for all ports | CONFIRMED | G4 |
| The array's sensitivity lies 54–70 % above z = 40 mm and ≤ 4 % below z = 0; 'lobes' are azimuthal wedges of the upper head | CHANGED | G5 |
| The antenna near field in front of each antenna is meridionally polarised | CHANGED | G3 |
| HFSS tissue values equal Gabriel 1996 at 3.25 GHz, held constant; true σ rises 29–38 % over 3.2–4.2 GHz | CHANGED | G7 |
| Born linearisation error: 50–58 % on the symmetric and 92–96 % on the antisymmetric part of LeftOnly; kernels move 24 % with the export grid | CHANGED | B14 |
| Sector values and per-sector calls are not results: they flip with λ, reference and calibration, depend on depth profile, and are ≈ 80 % their own antenna | CHANGED | R5, B16, B17, B21, B25 |
| Pre-registered blind test: PARTIAL with the frozen 7-pass reference, FAIL with the matched reference; neither reference is more credible | CONFIRMED | B23 |
| [POST-HOC] LeftOnly left/right sign is in the data (mirror test) and stable over λ, references and kernel symmetrisation; size 1.93× (Tikhonov dS) to 2.77× (whitened log) the clean ruler under the fixed max-floor rule: not established; rank p = 0.1 with nine nulls | CHANGED | R1, B22 |
| [POST-HOC] 85–88 % of the LeftOnly LR comes from phase; it is not per-antenna detuning (per-port factors explain ≤ 20 %) | CHANGED | R3, C2 |
| [POST-HOC] Cross-ratio phases: 12/18 distinct statistics ≥ 3× under the rms rule, 3/18 under the max rule; no symmetric file exceeds 1/18; with measurement errors (±0.5 dB) 0/18 (rms) and 0/18 (max) | CHANGED | R2, C3, C5 |
| Moderate_lobe's large mirror residual is mesh asymmetry of that pass-5 file (halved one pass later) | CHANGED | R1 |
| Left antennas' reflection depth changes by 0.9–1.0 dB (3–6× one-pass); resonance frequencies do not move | CHANGED | R3 |
| Phase change of the left neighbour path is negative (delay), −7 to −9° at 3.30–3.60 GHz, as the CSF-gap physics predicts | CONFIRMED | C4 |
| Bias-corrected Moderate front/back is 6.3–7.4 (truth 14.6): established in lobe_B (3.2–4.0×), not in lobe_A (1.4–1.9×); mesh-sensitive | CHANGED | B24 |
| MCI_lobe shows nothing beyond the rulers in any variant (never flips with λ, reference or calibration) | CONFIRMED | B17, round 1 |
| R31 detection is defensible on the uniform training data and fragile on lobe Severe/LeftOnly; no single feature determines every lobe design | CONFIRMED | R4 |
| Thresholds were frozen before LeftOnly/MCI existed but tuned on Mild of the same head; Mild calls are in-sample | CHANGED | B19 |
| **Added after round 2:** RightOnly_test (mirror of LeftOnly, independent mesh) is REPLICATED under the committed C6 rule: LR −9.44 (H6) / −9.83 (H7), phase sign at 3.4 and 3.6 GHz, 83 % phase. [POST-HOC] LR_anti −10.15 = 2.5× (Tikhonov dS) to 3.4× (whitened log) the R1c ruler; both mirror designs beyond all nine nulls with opposite signs | CONFIRMED (prediction held) | C6, `rightonly_score.md`, report §10 |

**Agreement with the main session (round 2).** Both sessions independently fixed the same floor rule R1c:
clean ruler = max(one-pass yardstick, largest |value| over the nine mirror-symmetric solves, none excluded).
Both get imaging LR_anti 1.93× (main 1.94×; the yardstick is computed slightly differently, 2.14 vs 2.12) and
3/18 distinct phase cross-ratios. Main's "4/22" is the same set counted with its 4 algebraic duplicates.

**Not re-reviewed in round 2.** `results/imaging/report.md` (Track A v1/v2: I1, I2, I3, ratio lead, §6
verdict) has not been re-derived under the round-2 standard. Treat its claims as **unverified**. Known
impacts:
- The I3 forward model assumes point dipoles with a θ/φ mix, but G3 measured meridional polarisation.
- Materials are 3.25 GHz constants (G7).
- There is one HFSS solve per stage, and the mesh error on v2 is unmeasured.
- §4.3's "99 % of the k = 3 sensitivity in air" used the `_wide` volume export (±120 mm, 4 mm), so it is
  **not** affected by the cut-plane worry (G8).

---------------------------------------------------------------------------------------------------------------

## 5. How to rerun

### 5.0 Environment and data

- Run from the repository root. Python 3.12.6, numpy 2.3.5, scipy 1.18.0, pandas 3.0.5, matplotlib 3.11.0
  (laptop). The HPC requirements are in `imaging/hpc/requirements.txt`.
- On the Windows console, set `PYTHONIOENCODING=utf-8`, or printing Greek or unicode characters crashes
  (cp1252).
- Tests: `python -m pytest imaging/tests -q` → 27 passed (≈ 1 min).
- **Data are not all in git.** The lobe `.s6p` files are untracked, and `data/fields/` is in `.gitignore`. They
  must exist on disk. Verify with `sha256sum` (first 16 hex shown):

| file | sha256 (16) | in git |
|---|---|---|
| data/raw/new_with_slices_Healthy_sliced.s6p | b4dcc70fbddb3641 | no |
| data/raw/new_with_slices_Healthy_sliced_new.s6p | 46bf335a1455bb20 | no |
| data/raw/new_with_slices_Mild_lobe.s6p | 506d565062eed1c7 | no |
| data/raw/new_with_slices_Mild_lobe_new.s6p | 390dbacdfacceb03 | no |
| data/raw/new_with_slices_Moderate_lobe.s6p | 5d8fb53a6b52ffc2 | no |
| data/raw/new_with_slices_Moderate_lobe_new.s6p | 64095b253010aa7a | no (≡ Moderate_lobe to 1e-8) |
| data/raw/new_with_slices_Moderate_lobe_c3.s6p | e640e23a7cf835cb | no |
| data/raw/new_with_slices_Severe_lobe.s6p | d1f2c504904a71b3 | no |
| data/raw/new_with_slices_Severe_lobe_new.s6p | 9bd72760e5f58212 | no (≡ Severe_lobe to 1e-8) |
| data/raw/new_with_slices_Severe_lobe_c3.s6p | d922adc08cb78515 | no |
| data/raw/new_with_slices_LeftOnly_test_c3.s6p | 28d350d6dcaa9ac3 | no (blind, scored) |
| data/raw/new_with_slices_MCI_lobe_c3.s6p | 98940e10a50c7944 | no (blind, scored) |
| data/raw/new_{Healthy,MCI,MildAD,ModerateAD,SevereAD}.s6p | e10dece5…, 74754835…, 8fe68dc8…, 405d362b…, 7ef7cb8b… | yes (v2) |
| data/fields/E_Normal_T{1..6}_{3p4,3p6,3p8}GHz.fld (18 files, ≈ 48 MB each) | T1_3p4 bd96f0c01161e60a, T1_3p6 3b0273f41837b613, T1_3p8 985f0edc7d66e838 (others: `sha256sum data/fields/*.fld`) | no (ignored) |
| data/fields/E_Normal_T1_3p6GHz_wide.fld | 55369dac226a0f00 | no |
| data/hfss_geometry_audit_Healthy_sliced.txt | (main session's file) | yes |

The lobe imaging-side registry (stop rule, passes, final ΔS, elements, sets) is
`results/imaging/lobe_sets.csv`. Sets:
- **lobe_v1** (unmatched): Healthy_sliced p7 + Mild/Moderate/Severe_lobe p5. The frozen pipeline was fitted
  on this set.
- **lobe_A** (stop rule 1): Healthy_sliced_new p6 + Mild/Moderate/Severe_lobe p5 + LeftOnly_test_c3 p6 +
  MCI_lobe_c3 p6.
- **lobe_B** (stop rule 2): Healthy_sliced p7 + Mild_lobe_new / Moderate_lobe_c3 / Severe_lobe_c3 p6.

Glitch masking: `adstage.io.masking.mask_glitches`, −30 dB rule (`config.yaml` `qc.glitch_thr_db`), applied in
`study_lobe.load_design`. None of the masked points is at a fit frequency (`lobe_mask_log.csv`).

### 5.1 NEVER run `python imaging/run_lobe.py` without `--blind`

Stage 1 of `run_lobe.py` rewrites `lobe_frozen.json` **and** `lobe_predictions.md` with a new date and code
hash. That would corrupt the pre-registration. Use the safe rebuild instead.

### 5.2 Caches (gitignored, `results/imaging/cache/`)

- `lobe_v1-masked/born_table.pkl` (24 MB, the Born table from the field exports). Rebuilt automatically when
  missing (`RL.build`).
- `lobe_v1-masked/stage1.pkl`: read by `lobe_A`, `lobe_rulers`, `mesh_lobe`, `lobe_c3` and
  `report_lobe.run_blind`. **It went missing on 2026-10-04 (directory modified 11:57, cause unknown).** Rebuild
  it with:

```bash
python imaging/rebuild_stage1_cache.py
```

  This recomputes stage 1 and checks all 36 frozen values (κ, λ, every threshold) against `lobe_frozen.json`
  (rtol 1e-9). It writes only the cache, and refuses to write if anything differs. Verified 2026-10-04:
  reproduced exactly, frozen files byte-identical before and after.
- `hfss-v1-masked/`, `hfss-v2-sameproject-masked/`: Track A caches (i1, i2, i3, val, ratios, snr). Present
  locally.

### 5.3 Regenerate every lobe result (tested 2026-10-04, ≈ 5 min, deterministic seeds)

`lobe_report.md` is assembled **in place** by several scripts, each owning its sections. Run them in this
order. `lobe_c3` truncates everything after §6 and rebuilds §6–§7, so it must be followed by `lobe_review` and
then `lobe_round2`.

```bash
python imaging/rebuild_stage1_cache.py
```
```bash
python imaging/mesh_lobe.py
```
```bash
python imaging/lobe_A.py
```
```bash
python imaging/lobe_rulers.py --n 200
```
```bash
python imaging/lobe_c3.py --n 200
```
```bash
python imaging/lobe_review.py --n 200
```
```bash
python imaging/lobe_round2.py --n 200
```
```bash
python imaging/score_rightonly.py
```
```bash
python imaging/report_rightonly.py
```
```bash
python imaging/score_testb.py --n 200
```

What each writes:
1. `rebuild_stage1_cache.py` (17 s): cache only.
2. `mesh_lobe.py` (16 s): §5b, the superseded v2-vs-sliced yardstick; `lobe_mesh_yardstick.json`.
3. `lobe_A.py` (41 s): §5c, the mesh-matched set and one-pass yardstick; `lobe_A.json`.
4. `lobe_rulers.py` (47 s): §5d, the symmetry floor, measurement Monte Carlo and erratum; `lobe_rulers.json`.
5. `lobe_c3.py` (67 s): §6 (pre-registered scoring, via `report_lobe.run_blind`) and §6a–§6d (registry/QC,
   rulers, MCI, lobe_B); §7. Also `lobe_sets.csv`, `lobe_qc_c3.csv`, `lobe_mask_log.csv`,
   `lobe_blind_outcome.json`, `lobe_blind_rulers.csv`, `lobe_c3.json`.
6. `lobe_review.py` (51 s): round 1 (B1–B9) in `lobe_review.md` / `lobe_review.json`; §8; amends the §7
   left/right bullet.
7. `lobe_round2.py` (61 s): round 2 in `lobe_round2.md` / `lobe_round2.json`, `lobe_claims.csv`, §9.
8. `score_rightonly.py` (≈ 30 s): `rightonly_score.md`, the committed C6 verdict.
9. `report_rightonly.py` (≈ 40 s): §10 (QC, verdict, post-hoc mirror-pair table).
10. `score_testb.py` (≈ 40 s): `testb_report.md`, `testb.json`, §11. It refuses to run if the protocol is not
    committed.

The §8 and §9 writers keep later sections. `lobe_c3` (step 5) still truncates everything after §6, which is why
steps 6–10 must follow it.

§0–§5 and the figures `figures/lobe_*.png` were written by stage 1 (`report_lobe.write_stage1`) at `62709e0`.
**Do not regenerate them**, because that function also rewrites the predictions file. They are final in git.

Expected result of a rerun: `git diff -- results/imaging` shows only the embedded code-hash strings.
`common.git_hash` records the repository HEAD at run time, which may be a main-session commit. After checking,
restore with `git restore -- results/imaging`, which is scoped to this folder.

### 5.4 Track A (v1/v2 uniform data, `report.md`)

```bash
python imaging/run_imaging.py --reuse
```

- Default config `config.yaml` → `data/sims.csv`, sim_set `hfss-v2-sameproject-masked`.
- v1 archive: set `MLI_CONFIG=imaging/configs/v1_archive.yaml` (bash: `MLI_CONFIG=... python ...`).
- `--only paths,snr,i1,val,i2,ratios,i3`, `--jobs N` (parallel I1/I3), `--quick` (smoke test).
- Without `--reuse` the full run takes about 6–7 h on the laptop (I3 ≈ 5 h). Use `--jobs` or the HPC scripts in
  `imaging/hpc/` (README there; the user handles login).
- I3 checkpoints in the cache resume after interruption. Laptop sleep stops runs; ask the user to keep it awake
  and plugged in.

### 5.6 NEXT: Test_B score from the user

The user holds Test_B's truth and scores it against `testb_protocol.md` (`24aa0c4`).
- **Blind rules (still in force until the user releases the truth):**
  - Test_B's geometry may be learned only from its S-parameters: no HFSS project, no other session's files about
    it (for example `results/imaging2/`, or main-session Test_B outputs such as commit `d3a4bbf`), no file
    metadata, and no asking the user.
- **When the truth arrives:**
  1. Write `results/imaging/testb_score.md`: the user's truth, and the per-sector "affected" and
     "affected ∪ possible" agreement as in the protocol's §5.
  2. Do not re-run with changed rules. Any post-hoc analysis goes in a separate, labelled section.
  3. Add a claims row.
- Do not touch `share_lobe_phantom_data/` (an external share copy; never commit, move or edit it).
- Data checksums: `new_with_slices_RightOnly_test.s6p` `bc26c50a0b57af5e`, `new_with_slices_Test_B.s6p`
  `0e0e83feaa12e041` (untracked). Their passes, ΔS and elements were not supplied by the user (blanks in the
  delivery message).

### 5.5 DONE: RightOnly_test (scored 2026-10-04: REPLICATED)

```bash
python imaging/score_rightonly.py
```

- Looks for `data/raw/new_with_slices_RightOnly_test*.s6p`, scores it with the frozen pipeline, and writes
  `results/imaging/rightonly_score.md`.
- The rule is exactly the one committed in `0ceb626`: LR vs Healthy_sliced_new, frozen Tikhonov dS, predicted
  −6.9 ± 3.9.
  - **REPLICATED** if LR < 0, |LR| ≥ 7.8, and the T5–T6 minus T2–T3 phase change is negative at both 3.4 and
    3.6 GHz.
  - **FAILED** if LR ≥ 0 or |LR| < 3.9.
  - Otherwise **INCONCLUSIVE**.
- **Known flaw, recorded before the data exist:** the predicted |LR| (6.9) is below the 7.8 bar. The dry run on
  mirror(LeftOnly) (`python imaging/score_rightonly.py --dry-run-mirror`, prints only) gives LR −6.90 →
  INCONCLUSIVE. Do not change the rule. Report the outcome as is, plus the post-hoc mirror-pair average.
- Do not open the RightOnly file before running the scorer.
- Afterwards:
  1. Add the file to `REGISTRY` in `imaging/lobe_c3.py` (QC row).
  2. Add a §10 to `lobe_report.md` (new script, own section).
  3. Update `lobe_claims.csv`.
  4. Commit code, then results.

### 5.6 Quick reference: conventions

- **Antennas** T1..T6 at azimuth −90 + 60(t−1)° (the array is rotated −0.4°), ring at z ≈ 48 mm (port sheets),
  feeds at r = 97.15 mm. **Touchstone Port 1..6 = T4, T3, T2, T1, T6, T5** (`config.yaml` `ring.port_to_ant`;
  `study_ratios.ant_matrix` returns antenna order).
- **Sectors** S_k = 60° wedge centred on T_k, full height: S1 frontal (nose at −Y), S2 temporal L, S3 parietal
  L, S4 occipital, S5 parietal R, S6 temporal R. +X = subject's left.
- **Unknowns** dεr and dε'' (= dσ/(ωε0) at 3.6 GHz) of each sector shell r 70–83.5 mm. The core is excluded
  from the inversions.
- **LR** = mean(S2, S3) − mean(S5, S6) of the recovered dε'' (> 0 = left). **FB** = S1 − S4 (> 0 = front).
  **LR_anti**(X) = ½[LR(X) − LR(mirror X)] (reference-free).
- **References:** H7 = Healthy_sliced (7 passes, frozen, primary); H6 = Healthy_sliced_new (6 passes, matched).
- **Rulers:**
  - one-pass yardstick = max over Healthy 7−6, Mild 6−5, Moderate 6−5, Severe 6−5, both signs;
  - symmetry floor (R1c) = largest |value| over the nine mirror-symmetric solves;
  - clean ruler = max(yardstick, floor); measured ruler = max(yardstick, floor ⊕ ±0.5 dB Prompt 07 spread).
- **Bar:** ≥ 3× established, 2–3× sensitive, < 2× not separable.
- **Labels:** hit / sensitive / miss / not separable (`lobe_c3.verdict`).

---------------------------------------------------------------------------------------------------------------

## 6. Open items

1. **Test_B**: the user's score is pending (§5.6). RightOnly_test is done: REPLICATED.
2. **Floor significance**: nine symmetric solves cap the rank p at 0.1. Needs ≥ 19 independent mirror-symmetric
   solves, for example Healthy_sliced re-solved with head and array rotated k × 7°, k = 1…10 (R1, C3).
3. **Fit frequencies**: field exports exist only at 3.4/3.6/3.8 GHz. Kernel interpolation is invalid (≈ 62°
   phase rotation per 200 MHz). Needs `E_Normal_T{1..6}_{3p3,3p5,3p7,3p9}GHz.fld` (24 files, same ±90 mm
   volume, ideally 1 mm in r 60–88 mm), better of Healthy_sliced_new (B18).
4. **Measurement level**: antenna position error and frequency-dependent cable flex are not modelled. Needs
   HFSS re-solves with each antenna displaced ±1 mm (C5).
5. **Realistic layers**: CSF 0.5 mm, skull 3 mm, skin 0.5 mm in the model. Shehab 2025 Table 6 is not in the
   repo (UNVERIFIED). Effect of 2 mm CSF / 6 mm skull unknown without re-simulation (G1).
6. **Unverified geometry**: v1/v2 radius variables and the v2 skull hole (kernels come from the v2 Normal head);
   MCI_lobe Ventricle_CSF sphere; meaning of `z_ebg` (G2, G3, G6).
7. **AD material provenance and uncertainty** (G7).
8. **Sector model vs depth on real data**: needs an HFSS design with S3 materials changed and no CSF expansion
   (B16).
9. **Track A `report.md`** has not been re-reviewed under the round-2 standard (§4).
10. Items A14–A28 (data handling, statistics, staging of the frozen rule) belong to the main session.
11. Ranked improvement list (R5): rotated-mesh null solves → more frequencies/finer exports → data-driven
    sector kernels (single-sector HFSS designs) → RightOnly → second, lower ring → iterative DBIM → wider band.

---------------------------------------------------------------------------------------------------------------

## 7. Code map (`imaging/`)

| module | purpose |
|---|---|
| `common.py` | paths (ROOT, OUT, FIG), config loader, phantom radii and materials, noise profiles, `git_hash` (repo HEAD) |
| `fields.py` | reads HFSS `.fld` exports (`load_hfss_fields`, `Grid.sample`) |
| `study_lobe.py` | lobe designs and truth maps, Born table, region kernels, `RegionModel` (frozen; contains the 'gain-invariant' erratum), nulls, radar |
| `run_lobe.py` | frozen stage 1 (**do not run without `--blind`**), `invert`, `contrasts`, `apply_rules` |
| `report_lobe.py` | stage-1 report and predictions writer, `run_blind` (both references), `_verdict` (§7) |
| `rebuild_stage1_cache.py` | safe cache rebuild (§5.2) |
| `mesh_lobe.py`, `lobe_A.py`, `lobe_rulers.py`, `lobe_c3.py` | §5b, §5c, §5d, §6a–§6d (see §5.3) |
| `lobe_review.py` + `lobe_review_md.py` | round 1 (B1–B9) |
| `lobe_round2.py` + `lobe_round2_md.py` | round 2 (R, B14–B25, G, C), claims |
| `score_rightonly.py` | C6 replication scorer (§5.5) |
| `report_rightonly.py` | §10: RightOnly QC, verdict, post-hoc mirror-pair table |
| `score_testb.py` | Test_B blind scorer implementing `testb_protocol.md` (`--dry-run STEM` on known designs only) |
| `run_imaging.py`, `study_i1/i2/i2_hfss/i3/ratios.py`, `beamform.py`, `forward.py`, `mie.py`, `linear.py`, `timedomain.py`, `paths.py`, `stage_snr.py`, `report*.py` | Track A |
| `tests/` | `test_imaging.py` (Track A), `test_lobe.py` (geometry, rules, one bar, whitened projection) |
| `hpc/` | SLURM / env scripts for the Praganak cluster |

Key commits:
- `da22b5d` Track A start; `7dca095` Track A v2 results.
- `fb5b775` lobe code frozen; `62709e0` stage 1 + predictions.
- `2df90a8` / `bf83290` lobe_A; `9182afd` / `2ce6d97` rulers + erratum; `92a8998` / `7944508` blind scoring (c3).
- `237ad47` / `b543b33` round 1; `0ceb626` round-2 predictions; `66c04db` / `e4c33d3` round 2.
- `226f9b1` safe rebuild + RightOnly scorer; `2a75644` this handover.
- `b2f1472` / `24aa0c4` Test_B scorer and protocol (before loading); RightOnly REPLICATED.
- `6efd1db` / `5818235` §10 writer and Test_B estimates.

## 8. Pitfalls seen in this project

- The main session commits concurrently. Always stage only `imaging` / `results/imaging`, and check
  `git diff --cached --name-only`.
- Bash heredocs containing quotes, backticks or `\\` failed several times in the tool shell. Write patch scripts
  with a file tool and run them instead.
- OneDrive or Windows file locks broke pickle writes once (the I3 checkpoint now retries). Laptop sleep kills
  long runs.
- Hand-typed numbers in report text went stale twice. Compute every number in text from the results objects.
- "Two analyses agreeing" is not replication; a new blind design is (C6).
