# HANDOVER — main analysis session, Track A (written 2026-10-04)

A fresh session should be able to continue from this file alone. It was written at code commit **e7794fd**, and the
commit that adds it is 4aabb1d (its parent, 6db98f6, is an `[imaging2]` commit). Uncommitted edits to
`results/imaging*` in the working tree belong to the imaging sessions: never stage them. Repository: this folder, branch `master`. **There is no git remote**: the
only copy is this OneDrive folder.

**Updated 2026-10-04 (later):** RightOnly_test scored (C6: NOT REPLICATED, 546d804). The Test_B blind protocol was
committed (d3a4bbf) and the blind estimates were committed (0f49389). The truth is pending: see §7.1(a).

Read in this order: this file → `MODEL_CARD.md` Part 6 (authoritative claims) → `results/05_lobe/review2/report_stats.md`
and `report_fields.md` (round-2 numbers) → `results/STATUS.md` (plain-language status for the user).

---

## 1. Role and boundaries

**Project.** Non-invasive Alzheimer's (AD) staging from 6-port HFSS S-parameters.
- Phantom: a 7-layer concentric-sphere head with a ring of 6 patch antennas (T1..T6) at z ≈ 50 mm.
- Uniform phantom: the stages Normal / MCI / Mild / Moderate / Severe change radially.
- Lobe phantom (project `new_with_slices`): the same head with gray/white matter cut into six 60° sectors
  S1..S6, one under each antenna, and disease applied per sector.

**This session (main analysis) owns:**
- `scripts/` (00–15, `run_all.py`);
- `src/adstage/`, `tests/`;
- `config*.yaml`;
- `data/sims*.csv`, `data/sim_plan.csv`;
- `MODEL_CARD.md`;
- `results/` except `results/imaging*`.

Its jobs:
- QC of every delivered Touchstone file.
- The frozen detection/staging rule and its application to new designs.
- Mesh and numerical rulers.
- Blind scoring of pre-registered predictions.
- The adversarial reviews, which the user poses as numbered items (A…, R…, G…, C…).

**The imaging session** is a separate Claude session in the same repo; its commits are prefixed `[imaging]`.
- It owns `imaging/` and `results/imaging/`.
- A third line of work commits `imaging2/` and `results/imaging2/` with the prefix `[imaging2]` (first commit
  6db98f6, 2026-10-04 13:10: slice images of the lobe phantom). Treat it like the imaging session: read only.
- It also owns the B-items of the reviews.
- You may **read** its files and import its code read-only (scripts 10–12 do).
- **Never modify them.** Never coordinate predictions with it: both sessions write their own, separately.

**Not ours / leave alone:**
- `prompts/` and `docs/context_packs/` (untracked; the user's).
- `blind_validation_presentation.pptx` (untracked; the deck is on hold).
- `references/`, `cluster/` (incl. the untracked `cluster/hfss.pbs`).
- `share_lobe_phantom_data/` and `share_lobe_phantom_data.zip`: an external share copy. Never commit, move or edit
  them (user, 2026-10-04).
- `Microwave AD Detection — Progress Review.pptx` (untracked).
- The uncommitted `.gitattributes` line `*.pbs text eol=lf` is not ours. It makes `git_hash()` report `-dirty`;
  that is the only reason the runs since c100803 carry the `-dirty` suffix.

## 2. Standing user instructions (binding)
- **Touchstone headers are unreliable.** "please don't rely on touchstone headers for information, that's completly
  unreliable". Labels, passes, ΔS and element counts come from the user and live in `data/sims*.csv`.
- **The frozen rule is never changed.** `results/04/frozen_rule.json` "must not be changed when new simulations
  arrive; it gets tested as-is".
- **Predictions and frozen files are never edited.** Committed predictions are scored as written.
- **Commit code before every logged run.** Report headers record the git hash; `-dirty` means the run was not clean.
  Results are committed after the code.
- **Never commit raw data or the CRLF-only diffs, and never "fix" raw data.** "Do not commit them; do not 'fix' raw
  data." The lobe `.s6p` files are untracked on purpose. `git config core.autocrlf` is `true`.
- **Never enter passwords** or log in on the user's behalf.
- **The report and the deck are on hold** until the user says otherwise.
- **Reviews:** re-derive every item from code and data (command, number, file, commit); quoting earlier text is not
  evidence. Verdict CONFIRMED / CHANGED (old → new, cause) / CANNOT TELL (what would settle it). Never concede or
  defend without numbers. Every "why" gets a mechanism or a measurement.
- **Style.** The user wants blunt, honest, accurate answers, verdict first, no sugar-coating, numbers exact.
  Also stored in auto-memory: `blunt-honest-assessments.md`, `ad-staging-priorities.md`.
- **The user's priority view** (memory): anatomy variation is untested and decisive; the disease model is
  exaggerated; more mesh or lobe work is low value.

## 3. Data inventory

**Manifests (authoritative labels):**
- `data/sims.csv`: uniform v2, 5 solves.
- `data/sims_with_repeats.csv`: v2 plus the 4 archived v1 solves as repeats.
- `data/sims_lobe.csv`: lobe phantom, with columns `set`, `kind`, `stop_rule`, `passes`, `final_dS`, `elements`.
- `data/archive/v1_mixed_projects/sims.csv`.
- `data/sim_plan.csv`: planned solves, not read by the pipeline.

**Lobe sets** (`data.set` in the configs):
- `lobe_v1`: the Prompt 07 files, stop rules not matched; kept as-is.
- `lobe_A`: stop rule 1, primary. Contains Healthy_sliced_new (6 passes), Mild_lobe (5), Moderate_lobe (5),
  Severe_lobe (5), and the test designs LeftOnly_test_c3 and MCI_lobe_c3 (6 each, `kind=test`).
- `lobe_B`: stop rule 2. Contains Healthy_sliced (7), Mild_lobe_new (6), Moderate_lobe_c3 (6), Severe_lobe_c3 (6).
- `lobe_tests`: Healthy_sliced_new plus the two test designs, for QC.
- Not in the manifest: `*_Moderate_lobe_new.s6p` and `*_Severe_lobe_new.s6p` duplicate Moderate_lobe /
  Severe_lobe to ~1e-8.

**Files.** Checksums are the first 16 hex characters of the SHA-256 of the file as it sits on disk.

| file | tracked | sha256[:16] |
|---|---|---|
| data/raw/new_Healthy.s6p | yes | e10dece5d3bf5d53 |
| data/raw/new_MCI.s6p | yes | 74754835ef2e24e1 |
| data/raw/new_MildAD.s6p | yes | 8fe68dc8df9a51d5 |
| data/raw/new_ModerateAD.s6p | yes | 405d362b87761555 |
| data/raw/new_SevereAD.s6p | yes | 7ef7cb8b16377491 |
| data/archive/v1_mixed_projects/raw/brain_sevem_layer_Healthy.s6p | yes | 03e82af8de0fd08e |
| data/archive/v1_mixed_projects/raw/Brain_sevem_layer_MildAD.s6p | yes | 3eb0d655f940008f |
| data/archive/v1_mixed_projects/raw/Brain_sevem_layer_ModerateAD.s6p | yes | 72a71c990ebdf141 |
| data/archive/v1_mixed_projects/raw/brain_sevem_layer_SevereAD.s6p | yes | 3598bf7043f5cbdf |
| data/raw/new_with_slices_Healthy_sliced.s6p | **no** | b4dcc70fbddb3641 |
| data/raw/new_with_slices_Healthy_sliced_new.s6p | **no** | 46bf335a1455bb20 |
| data/raw/new_with_slices_Mild_lobe.s6p | **no** | 506d565062eed1c7 |
| data/raw/new_with_slices_Mild_lobe_new.s6p | **no** | 390dbacdfacceb03 |
| data/raw/new_with_slices_Moderate_lobe.s6p | **no** | 5d8fb53a6b52ffc2 |
| data/raw/new_with_slices_Moderate_lobe_c3.s6p | **no** | e640e23a7cf835cb |
| data/raw/new_with_slices_Severe_lobe.s6p | **no** | d1f2c504904a71b3 |
| data/raw/new_with_slices_Severe_lobe_c3.s6p | **no** | d922adc08cb78515 |
| data/raw/new_with_slices_LeftOnly_test_c3.s6p | **no** | 28d350d6dcaa9ac3 |
| data/raw/new_with_slices_MCI_lobe_c3.s6p | **no** | 98940e10a50c7944 |
| data/raw/new_with_slices_Moderate_lobe_new.s6p (duplicate) | **no** | 64095b253010aa7a |
| data/raw/new_with_slices_Severe_lobe_new.s6p (duplicate) | **no** | 9bd72760e5f58212 |
| data/raw/new_with_slices_RightOnly_test.s6p (C6 replication; in the manifest) | **no** | bc26c50a0b57af5e |
| data/raw/new_with_slices_Test_B.s6p (**blind**; not in the manifest; loaded only by `15_test_b.py --blind`) | **no** | 0e0e83feaa12e041 |
| results/imaging/cache/lobe_v1-masked/born_table.pkl (imaging cache; read by 10, 11, 14) | **no** | 998ff933b8869718 |

- **HFSS field exports** (`data/fields/`, git-ignored, 920.6 MB). The v2 Normal design, one export per
  excitation:
  - 18 volume exports `E_Normal_T{1..6}_{3p4,3p6,3p8}GHz.fld`, (−90..90 mm)³ on a 3 mm grid;
  - one `E_Normal_T1_3p6GHz_wide.fld`, (−120..120 mm)³ on a 4 mm grid.
  - Checksums: `cd data/fields && sha256sum *.fld` gives, for example, T1 3p6 `3b0273f41837b613` and
    T6 3p8 `8f12d84f1cd8ddbd`.
  - Needed only by `12_review2_fields.py`.
- **Geometry audit:** `data/hfss_geometry_audit_Healthy_sliced.txt` (tracked; the user's HFSS script output).
  - Excitation order Port1..6 = FEED_3_T4, T3, T2, T1, T6, T5.
  - Port sheets at azimuths +89.6, +29.6, −30.4, −90.4, −150.4, +149.6°.
  - So T1 is at −90° and +x is the subject's left; T2/T3 are left, T5/T6 right.
- **Integrity check:** `sha256sum data/raw/new_with_slices_*.s6p | cut -c1-16`. If an untracked file is missing or
  differs, ask the user for it. Do not regenerate it and do not edit it.

## 4. Committed predictions and frozen files

Check that each file is unchanged:
- `git log --oneline -- <path>` lists only the commit shown;
- `git hash-object <path>` equals the blob hash.

Both checks passed at e7794fd.

| path | owner | content | committed (date) | git blob | status |
|---|---|---|---|---|---|
| `results/04/frozen_rule.json` | main | **Frozen rule.** Detection: AD if R31 < τ − m, with τ = −15.2727958516 dB and m = 0.0783244599 dB. Staging: `three` = LDA on R21 (Normal / Mild / Severe); `three_merged` = LDA on R32 (Normal / Mild+Moderate / Severe); p* 0.7. Band 3.2–4.2 GHz, floor subtracted, glitch mask −30 dB. Trained on the 9 uniform v1/v2 solves | 5192287 (2026-10-02 10:59), code 2baddee | 0856a0f67075cbceb77a48cb001a309d536a3e54 | frozen; applied as-is to every new design |
| `src/adstage/frozen.py` | main | `apply_rule()`: evaluates the rule; must never change it | 2baddee (2026-10-02) | db80c52d821bda6458aab1461244f36f8757f107 | frozen |
| `config.yaml` → `qc.glitch_thr_db: -30.0` | main | Glitch mask: masks a point where \|Sij − Sji\| > −30 dB of the pair's band-rms level | value set 89d4f23 (2026-09-27); unchanged through every later config.yaml commit | file blob 530ebd7c6e40ce5f8cf675ab377d997868b05c58 | frozen parameter |
| `results/v2_with_v1_repeats/03/thresholds.csv` | main | Source table of τ (profile `typical`). The JSON is authoritative | 9741265 (2026-10-01 11:09), code c95604c | 59f95fb48ae3cd405d935838255d9d31aef22671 | do not commit a rerun's version |
| `MODEL_CARD.md` Part 4, "Pre-registered test for the equal-settings re-solves" | main | Retraction criteria for detection, staging and Normal≈MCI when the uniform equal-settings re-solves arrive | 28c7707 (2026-10-02 16:08) | (section of MODEL_CARD) | **pending**: files not delivered |
| `results/05_lobe/predictions.md` | main | **Pre-registered** LeftOnly_test predictions (power LR index, front/back, per-path changes, R31/R21/R32 levels, frozen label), derived from lobe_v1 | cf56de8 (2026-10-03 21:25), code 7ccec7f | 3b6304b630212741adfecc3da7ed1ca46d3c2da4 | scored (09 at e1b3629; reviews 10, 11): power predictions fail or are not separable; registration under-powered |
| `results/05_lobe/predictions.csv` | main | same, as a table | cf56de8 | 2682ac4a801706f3b51a49aa74563754701f1f0e | scored |
| `scripts/09_lobe_tests.py` (added 08a9a53, 2026-10-04 09:40) | main | Gain-invariant left-right cross-ratio test, with predictions derived from cf56de8 and a decision rule fixed in the code before the first run | 08a9a53 | (code) | scored at 522e579: 0/22 beyond 3× the measured ruler (fails) |
| `results/05_lobe/review2/predictions_R3_C4.md` | main | Round-2 predictions: R3 detuning, C4 phase sign/size/band | 2a222ff (2026-10-04 12:10), with the code, before any run | 6d619b95d65cbedaec6308f6dac29e307d1db6f3 | scored: R3 rejected (wrong sign; separable share 0.11); C4 sign right, neighbour sizes right, long paths and the ∝ f band prediction wrong |
| `scripts/11_review2.py` docstring, "FLOOR RULE (R1c)" | main | Floor rule for left-right statistics (§5) | 2a222ff | (code) | fixed; used by both sessions |
| `results/05_lobe/rightonly_predictions.md` | main | **C6:** RightOnly_test design, predictions 1–5, scoring rule | 0f97bb2 (2026-10-04 12:16), code b61c5d8 | a0150e76aadafc1170f666b982d03d626f37277f | **scored** by 14_rightonly (c100803 → 546d804): NOT REPLICATED (P1 12/26 within tolerance, signs 26/26; P2 holds) |
| `results/05_lobe/rightonly_predictions.csv` | main | the 91-row prediction table (statistic, LeftOnly value, predicted value, tolerance, informative flag) | 0f97bb2 | c03834e756300d21ad378acbae24ba0f915b901b | scored (546d804) |
| `results/05_lobe/test_b/protocol.md` | main | **Test_B blind protocol.** Reported items, decision rules (sector-pattern fit with fit-rejection rule, mirror side test), references (Healthy_sliced_new), scoring against the truth, validation on the known designs. Code `scripts/15_test_b.py` 89af4b3 | d3a4bbf (2026-10-04), before Test_B was loaded | 37a5bc4ebced50a223e9c6b179a4f9f9632d3af1 | **frozen; truth pending** |
| `results/05_lobe/test_b/estimates.csv` (+ report.md, statistics.csv) | main | Blind estimates under d3a4bbf | 0f49389 (2026-10-04) | fa4a6bcf80a5ac52261d54f3e811476d5e911958 | **truth pending; never edit; keep out of MODEL_CARD/STATUS until the truth is returned** |
| `results/imaging/lobe_frozen.json` | imaging (read-only) | Frozen imaging inversion (κ, λ, thresholds); used read-only by 10 and 11 to rebuild the imaging LR | 62709e0 (2026-10-03 22:37), code fb5b775 | 0b42ece21b4990ac99271e3cf5c9cb7f5df0c1cd | frozen |
| `results/imaging/lobe_predictions.md` | imaging | Imaging blind predictions for LeftOnly / MCI | 62709e0 | b13103691aad1b2d2142020c98d295841105e314 | scored by imaging: LeftOnly PARTIAL (7-pass reference) / FAIL (matched), MCI success |
| `results/imaging/round2_predictions.md` | imaging | Imaging R3, C4 and C6 predictions (RightOnly LR −6.9 ± 3.9) | 0ceb626 (2026-10-04 11:52) | 1b941d759d7f35e585c94df8dc06a3627e333e95 | scored by the imaging session with its own rule (its commit 24aa0c4); not used by the main session |

**Overwrite guards** (e7794fd):
- `05_audit.py` refuses to freeze when `frozen_rule.json` exists (run it with `--no-freeze`).
- `07_lobe.py --write-predictions` refuses when `predictions.md` exists.
- `13_review2_misc.py` writes the C6 files only with `--write-predictions` and only if they are absent. By default it
  checks that the committed CSV reproduces (max diff 1.8e-15 at e7794fd).
- `14_rightonly.py` checks the git blobs of the C6 predictions before scoring and never writes them.
- `15_test_b.py --blind` refuses to run unless `protocol.md` is committed unchanged. Test_B is not in the manifest,
  so no other script loads it.

## 5. Rulers and definitions used by every claim

- **Noise model.** All of it was chosen, not measured.
  - Per-entry profile `typical`: 0.25 dB / 2° / −70 dB floor.
  - Setup perturbation: 1.5% amplitude, 10° per port, 1 MHz jitter.
  - Default calibration error: ±0.5 dB per-port gain.
  - Stress settings: ±2 dB / ±10°.
  - Sources: Prompt 02 (89d4f23) and Prompt 03 follow-ups (6eca5d7).
- **One-pass mesh yardstick.** The largest change of a quantity over Healthy 6→7, Mild 5→6, Moderate 5→6 and
  Severe 5→6 (stop rule 1 → 2).
  - R31 0.135 dB, R21 0.110 dB, R32 0.161 dB.
  - Four samples: a rough ruler, not an SD.
- **Label margin.** The distance to the label edge, divided by max(yardstick, boundary bootstrap SD). Round 2 adds
  the measurement spread in quadrature.
  - Label edge for detection: τ ± m. For staging: the LDA boundary.
- **Bar:** ≥ 3× established; 2–3× sensitive; < 2× not separable / not determined.
- **Mirror test.** T(S) is any statistic that flips sign under the port mirror T2↔T6, T3↔T5 (index arrays must be
  applied as `S[..., MIR, :][..., MIR]`). T is evaluated on one design alone, with no reference.
  - The null is the nine mirror-symmetric designs: Healthy_sliced, Healthy_sliced_new, Mild_lobe, Mild_lobe_new,
    Moderate_lobe, Moderate_lobe_c3, Severe_lobe, Severe_lobe_c3, MCI_lobe_c3.
- **Floor rule R1c.**
  - Floor = max |T| over the nine (leave-one-out when a null file is scored).
  - Clean ruler = max(floor, one-pass yardstick).
  - The rank p is reported; nine nulls cannot give p < 0.1.
- **Complex cross-ratios.** S_ab·S_cd / (S_ac·S_bd) cancel any per-port complex gain. Their left-right
  antisymmetric phase gives 22 combinations, of which 18 are distinct.
- **Effective sample size.** The two uniform solves of a stage differ only in sweep settings, so N = 1 design per
  stage. Every lobe number is one solve per design: within-simulation noise robustness, not generalisation.

## 6. Current claims table (copy of MODEL_CARD 6.2; also `results/05_lobe/review2/claims_round2.csv`)

All claims concern one idealised spherical head, with one solve per design. The noise model was chosen, not measured.
Anything in MODEL_CARD Parts 1–5 or STATUS that is not listed here is **unconfirmed**. This includes STATUS §2's
delay numbers, §3 (MCI, reflection metrics, spectral-shape, imaging), §4 (the M5.C2 staging lead) and the M5.C3
detection row of §1.

| # | claim | verdict | items |
|---|---|---|---|
| 1 | The frozen τ = −15.2728 dB re-derives exactly (95% −15.368 to −15.165). It and the staging boundaries were fitted on uniform solves before any lobe file existed | CONFIRMED | A18, A28 |
| 2 | Frozen detection labels ≥ 3x every ruler, incl. the ±0.5 dB spread: healthy (3.0x / 4.0x), lobe-Mild (3.2x / 3.4x), lobe-Moderate (4.4x / 4.5x) in both matched sets | CHANGED | R6 |
| 3 | Severe (1.2x / 1.6x) and LeftOnly (0.6x) are labelled AD but are not determined. MCI_lobe Normal is sensitive (2.85x) | CHANGED | R6, A23 |
| 4 | R31 is non-monotonic because the neighbour coupling falls at Severe while the opposite coupling saturates | CHANGED | A23 |
| 5 | Detection depends on 3.2–3.8 GHz; in 3.8–4.2 GHz the uniform Normal and AD solves overlap | CHANGED | A16 |
| 6 | Without the frozen glitch mask, Mild_lobe_new's detection is not determined (1.4x); a 2x stricter mask changes nothing (≤ 0.29x) | CHANGED | A15 |
| 7 | At 2x the chosen noise and ±4 dB / ±20° calibration errors, detection fractions stay 1.00 (LeftOnly 0.94) | CHANGED | A19 |
| 8 | Leave-one-solve-out passes on all 22 folds, but it tests sweep-setting robustness: effective N = 1 design per stage | CHANGED | A17, A21 |
| 9 | R31 was a defensible choice on the training solves. On the lobe set R31, R21 and the pair each leave designs undetermined (7/10, 7/10, 9/10 ≥ 3x). None is adopted | CONFIRMED | R4 |
| 10 | R21 orders the four lobe stages (6–15x the summed yardsticks); uniform Mild and Moderate are not ordered on R21 | CHANGED | A24 |
| 11 | Lobe-Mild's three-class label is not determined (0.06x / 0.26x). 10 of 30 lobe labels are below 3x | CHANGED | A28, R6 |
| 12 | Best single features: R32 for Normal vs AD/Mild; R21 for Mild vs Severe. Mild vs Moderate is not separable on any feature | CHANGED | A22 |
| 13 | Divergence values move 6–74x with the between-solve covariance scaling; only rankings are reportable | CHANGED | A20 |
| 14 | Not-returned ("absorbed") power does not separate Normal from AD (0.92x) | CHANGED | A26 |
| 15 | [POST HOC] [WITHDRAWN 2026-10-04 (C6 not replicated)] The imaging mirror-test LR for LeftOnly is 1.94x (Tikhonov dS) to 2.77x (whitened log) the R1c ruler: not established. Rank p 0.1 | WITHDRAWN | R1, C6 |
| 16 | [POST HOC] [WITHDRAWN 2026-10-04 (C6 not replicated)] LeftOnly phase cross-ratios beyond R1c: 4/22 (3 distinct) at band mean. 16/22 in 3.2–3.5 GHz, 0 above 3.5 GHz. No symmetric file has any. At measurement level 0–2/22 | WITHDRAWN | R2, A16, C3, C5, C6 |
| 17 | [POST HOC] [WITHDRAWN 2026-10-04 (C6 not replicated)] The LeftOnly transmission phase asymmetry is not per-antenna detuning (separable share 0.11; no resonance shift beyond the null) | WITHDRAWN | R3, C6 |
| 18 | [POST HOC] LeftOnly's left reflections differ from their mirrors by −0.06 / −0.07 dB (3.5x / 5.0x); per-port gain errors swamp this in measurement. Replicated in the mirror: RightOnly +0.070 / +0.073 dB, within one clean ruler (C6 P3) | CHANGED | R3, C6 |
| 19 | [POST HOC] [WITHDRAWN 2026-10-04 (C6 not replicated)] The left neighbour-path phase is delayed, as CSF-gap propagation predicts; the field-share model gives the neighbour sizes, but not the long paths or the band dependence | WITHDRAWN | C4, C6 |
| 20 | Moderate_lobe's large mirror residual is mesh asymmetry of that 5-pass file | CHANGED | R1b |
| 21 | Port map Port1..6 = T4, T3, T2, T1, T6, T5 (T1 at −90°, +x = subject's left) is fixed by the HFSS geometry and the fields; the symmetry search cannot fix it | CONFIRMED | A14, G4 |
| 22 | Field exports are 3-D volumes; no claim used the cut plane | CONFIRMED | R7, G8 |
| 23 | Inside the head, in front of each antenna, the field is meridional (θ 0.95, φ 0.08) | CHANGED | G3 |
| 24 | 98.7–99.4% of path sensitivity is in air; ≤ 4% of the in-brain part lies below z = 0. Lobe statements refer to wedges of the upper cap | CHANGED | G5 |
| 25 | Healthy_sliced layer radii and inner structure match Part 1; leftover variables are unused | CONFIRMED | G1, G2, G6 |
| 26 | Healthy tissue values are Gabriel 1996 at 3.241 GHz held constant; real σ is 28–38% higher at 4.2 GHz | CHANGED | G7 |
| 27 | Sector-level imaging values are not results | CHANGED | R5 |
| 28 | Mirror replication (C6, RightOnly_test vs LeftOnly_test): all 26 informative left-right statistics flip sign and the phase cross-ratio counts match (4/4 band mean, 9/9 at 3.30–3.65 GHz, all with opposite sign), but only 12/26 sizes agree within one clean ruler (median \|RO + LO\| 1.07x the ruler, max 1.86x). Verdict under the committed rule: NOT REPLICATED | CHANGED | C6 |
| 29 | Solves of two mirror-equivalent designs (stop rule 1) differ by 0.133 dB in R21 (1.2x the one-pass yardstick) and 0.146 dB in R32 (0.9x): the one-pass yardstick does not bound design-to-design mesh variation | CHANGED | C6 P4 |
| 30 | The merged staging label differs between the mirror twins (LeftOnly Normal, RightOnly Mild+Moderate); both lie within 1x of the R32 boundary | CHANGED | C6 |

**The pre-registered answer stays primary:** the cf56de8 power predictions for LeftOnly fail or are not separable.
The phase finding (rows 15, 16, 17, 19) was post hoc. It was **withdrawn** after C6 was not replicated, on the user's
instruction. Note that the committed retraction clause was conditional on the signs *not* flipping; they flipped
26/26, and it was the sizes that failed (MODEL_CARD 6.6).

## 7. Open items

### 7.1 Waiting on the user (do nothing until the files arrive)

**(a) Test_B truth (blind design; protocol d3a4bbf, estimates 0f49389).** Done so far:
- RightOnly_test was scored (546d804): NOT REPLICATED.
- The Test_B protocol was committed before Test_B was loaded, and the estimates were committed.

Until the user returns the truth:
- Do not read other sessions' Test_B files.
- Do not put Test_B estimates into MODEL_CARD or STATUS.
- Do not edit `results/05_lobe/test_b/`.

When the truth arrives:
1. Record it: add a `data/sims_lobe.csv` row for Test_B with its sectors_affected, e values and r_hip in notes, and the
   passes / ΔS / elements if the user gives them. Commit.
2. Write `scripts/16_test_b_score.py`. It reads `estimates.csv` and `protocol.md` (check their blobs as `14_rightonly.py`
   does) and **never writes them**. It scores exactly per protocol §3:
   - detection label;
   - staging, only if Test_B uses one stage's materials;
   - side, by the sign of (e_S2 + e_S3) − (e_S5 + e_S6);
   - per sector: hits, misses, false alarms, correct rejections, uncertain;
   - confidence calibration.
3. Commit the code, run it, commit the results.
4. Update MODEL_CARD Part 6, STATUS §7 and this file.

**(b) Uniform equal-settings re-solves** (`data/sim_plan.csv`): `new_Healthy_meshrep`, `new_MCI_rep`,
`new_MildAD_eq`, `new_ModerateAD_eq`, `new_SevereAD_eq`. Status: running or planned since 2026-10-02, not
delivered.

When they arrive:
1. Add the rows to `data/sims.csv` and `data/sims_with_repeats.csv` (role `mesh_repeat`, see README).
2. Apply `results/04/frozen_rule.json` unchanged via `adstage.frozen.apply_rule` to noisy draws (typical + ±0.5 dB).
3. Score against the retraction criteria in MODEL_CARD Part 4 (28c7707). No script exists yet; write one and commit
   it before running.

### 7.2 Open limitations (CANNOT TELL / UNVERIFIED)
- **Generalisation.** One head, one stand-off, one mesh per design. **First experiment:** Normal plus lobe-Mild at
  ≥ 3 head radii, skull/scalp thicknesses and antenna stand-offs, scored with the frozen rule as-is. This is the
  decisive missing test, and it needs the user to build the designs.
- **Floor significance.** Getting below rank p 0.1 needs ≥ 19 independent mirror-symmetric solves (re-meshed or
  rotated healthy design).
- **Effective N.** Whether v1/v2 share a mesh: needs their HFSS mesh statistics.
- **Noise model.** It was chosen; real VNA and antenna data are needed.
- **Antenna position error and frequency-dependent cable flex.** These need ±1 mm displaced-antenna re-solves.
- **Layers.** The Shehab Table 6 source is not in the repo. Realistic 2 mm CSF / 6 mm skull is not simulated.
- **Other geometry.** The v1/v2 geometry variables, the v2 skull hole and the MCI_lobe ventricle are unaudited.
- **Materials.** Skin/fat/skull values in HFSS are unknown; the AD material provenance is unverified.
- **Post-hoc frequency choices.** The 3.30–3.65 GHz window and the sub-band split.
- **Frontal lobe.** The frontal-lobe (Moderate − Mild) result is power-only; it was never checked in phase.
- **Imaging-side items** (B14–B25, R5 evidence): `results/imaging/lobe_round2.md`.

### 7.3 On hold
- The report and the deck (`blind_validation_presentation.pptx`, untracked): do not touch until the user asks.

## 8. Exactly how to rerun the pipeline

**Environment.**
- Windows 11 with Git Bash. Python 3.12.6 (≥ 3.11 required). Versions pinned in `requirements.txt`: numpy 2.3.5,
  scipy 1.18.0, scikit-learn 1.9.0, pandas 3.0.5, matplotlib 3.11.0, PyYAML 6.0.2, joblib 1.5.3, pytest 9.1.1.
- The path contains spaces, so always quote it.
- Bash heredocs containing `'''` fail in this shell; put patch scripts in files instead.

```bash
cd "C:/Users/Asus/OneDrive - Indian Institute of Technology Bombay/Desktop/MultiLayerImaging_v1"
python -m pip install -r requirements.txt
export PYTHONIOENCODING=utf-8
python -m pytest -q
```
Expected result: `17 passed`.

**Config selection.**
- Scripts 00/02/03 read the `MLI_CONFIG` environment variable (default `config.yaml`). `run_all.py --config`,
  `04 --config` and `07 --config` set it.
- `results.out_root` in each config chooses the output folder.
- `--no-csv` stops 02/03/04 appending rows to the append-only `results/metrics.csv`. Use it for pure reproduction.

**Determinism.**
- Every random draw is seeded from `config.yaml` `seed`, so reruns should reproduce the committed numbers. Verified so
  far only for 13 (C6, max diff 1.8e-15).
- Report headers carry the current git hash, so a rerun at a new HEAD changes those header lines.
- After any rerun, inspect `git diff --stat results/`. Commit nothing that only differs in the hash header or in CRLF.
- If a rerun changes `results/v2_with_v1_repeats/03/thresholds.csv`, do not commit it; the frozen JSON is
  authoritative.

**Uniform set (Prompts 01–05).** Committed runs and their code commits:

```bash
python scripts/run_all.py --no-csv
```
Runs 00_qc, 02_metrics and 03_classify on `config.yaml` (v2, 5 solves). Writes `results/qc`, `results/02`,
`results/03`, `results/figures`. Committed at f142bf6 (qc at 5968676); log in `results/run_v2.log`.

```bash
python scripts/run_all.py --config config_repeats.yaml --no-csv
```
Same, on v2 plus the v1 repeats. Writes `results/v2_with_v1_repeats/`, the source of τ. Committed at c95604c.

```bash
python scripts/01_compare_solves.py
```
Writes `results/qc/solve_comparison.md`.

```bash
python scripts/04_likelihood.py --config config_repeats.yaml --no-csv
```
Writes `results/04/`. Committed at 5c060e3.

```bash
python scripts/05_audit.py --no-freeze
```
Writes `results/04/audit/`. Committed at 2baddee. Without `--no-freeze` it now refuses to run.

**Lobe phantom (Prompt 07 and the reviews).** Run in this order; later scripts read earlier outputs.

```bash
MLI_CONFIG=config_lobe.yaml python scripts/00_qc.py --include-moderate
```
Writes `results/05_lobe/qc/`. Committed at 3f993a4.

```bash
MLI_CONFIG=config_lobe_tests.yaml python scripts/00_qc.py --include-moderate
```
Writes `results/05_lobe/tests/qc/`. Committed at 08a9a53.

```bash
python scripts/07_lobe.py --config config_lobe.yaml --n 300
```
Writes `results/05_lobe/` (lobe_v1). Committed at 08a9a53. **Never pass --write-predictions.**

```bash
python scripts/07_lobe.py --config config_lobe_A.yaml --n 300
```
Writes `results/05_lobe/lobe_A/`. Committed at 08a9a53.

```bash
python scripts/07_lobe.py --config config_lobe_B.yaml --n 300
```
Writes `results/05_lobe/lobe_B/`. Committed at 08a9a53.

```bash
python scripts/08_lobe_mesh.py --n 300
```
Writes `results/05_lobe/mesh/` and `qc/masked_points.csv`. Committed at e1b3629.

```bash
python scripts/09_lobe_tests.py --n 300
```
Writes `results/05_lobe/tests/` (blind scoring vs cf56de8). Committed at e1b3629.

```bash
python scripts/10_lobe_review.py --n 300
```
Writes `results/05_lobe/review/` (round 1). Committed at 2f143e4. Needs the imaging Born cache.

```bash
python scripts/11_review2.py --n 300
```
Writes `results/05_lobe/review2/report_stats.md` and the R*/A*/C* CSVs. Committed at 2a222ff.

```bash
python scripts/12_review2_fields.py
```
Writes `review2/report_fields.md` and the F_* CSVs. Committed at d03c077. Needs `data/fields/`.

```bash
python scripts/13_review2_misc.py
```
Writes `review2/G7_dispersion.csv` and checks that the C6 predictions reproduce. G7 committed at b61c5d8.

```bash
python scripts/14_rightonly.py
```
Writes `results/05_lobe/rightonly/` (C6 scoring). Committed at 546d804 (code c100803). Needs the imaging Born cache.

```bash
python scripts/15_test_b.py --validate
```
Writes `results/05_lobe/test_b/validation*` (known designs only). Committed at d3a4bbf (code 89af4b3).

```bash
python scripts/15_test_b.py --blind
```
Writes `results/05_lobe/test_b/{report.md, estimates.csv, statistics.csv}`. Committed at 0f49389. **Do not rerun and
commit over these files**: they are the blind record. A rerun is only a reproducibility check (`git diff`).

- **Imports.** Scripts 10–12 import `imaging/` read-only (`imaging.fields.read_fld`, the Born table
  `results/imaging/cache/lobe_v1-masked/born_table.pkl`, `results/imaging/lobe_frozen.json`). Script 10 checks that the
  rebuilt operator reproduces. If the cache is missing, ask the imaging session or the user; do not rebuild it inside
  `results/imaging/` yourself.
- **Shared helpers.** Scripts 09–13 import 07/08/10/11 through `importlib`. The shared helpers are:
  - 08: `load_all`, `rulers`, `PAIRS`;
  - 10: `mirror`, `mirror_stats`, `complex_cr`, `Imaging`;
  - 11: `floor_rule`, `lr_cr_phase`, `fmask`, `LRBAND`, `SYM`, `LO`.

## 9. Working conventions
- **Workflow per task:**
  1. write or modify the code;
  2. commit;
  3. run;
  4. commit the results with the producing hash in the message;
  5. update MODEL_CARD/STATUS;
  6. commit the docs.
- Write predictions **before** computing, and commit them with the code.
- **Commit messages** end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Never stage** `data/raw/new_with_slices_*`, `prompts/`, `docs/context_packs/`, `imaging*/`, `results/imaging*/`
  or the `.pptx`. Use `git add <explicit paths>`, never `git add -A`.
- **Verdict text** in reports is computed from the data, never typed in advance (round 2 caught hard-coded verdicts).
- **Lessons from the reviews:**
  - the mirror needs both index operations;
  - neighbour paths change in phase, not power;
  - a symmetry search cannot fix left from right;
  - quote "post hoc" first on every phase statement.

## 10. Timeline of key commits
| commit | date | what |
|---|---|---|
| 89d4f23 | 09-27 | Prompt 02: glitch mask −30 dB, noise model |
| 6eca5d7 | 09-28 | R31 (calibration-free), gain errors |
| c95604c / 9741265 | 10-01 | v2 + v1 repeats run, τ table |
| 2baddee / 5192287 | 10-02 | audit and **frozen rule** |
| 28c7707 | 10-02 | Part 4 pre-registered test for the equal-settings re-solves |
| 7ccec7f / cf56de8 | 10-03 | lobe_v1 analysis, **LeftOnly predictions** |
| aff9d56 / bf5af59 | 10-04 | convergence study, lobe_A / lobe_B |
| 08a9a53 / 522e579 | 10-04 | c3 files, blind scoring |
| 2f143e4 / 65bd292 | 10-04 | review round 1 (A1–A9) |
| 2a222ff | 10-04 | round-2 code and R3/C4 predictions |
| b61c5d8 / 0f97bb2 | 10-04 | G7 + **RightOnly predictions** |
| d03c077 / ae2a7cb / 5b7909d | 10-04 | G3 fix, round-2 results, docs (MODEL_CARD Part 6) |
| e7794fd | 10-04 | overwrite guards |
| c100803 / 546d804 | 10-04 | C6 scoring: RightOnly NOT REPLICATED |
| 89af4b3 / d3a4bbf | 10-04 | **Test_B blind protocol** (code, validation) |
| 0f49389 | 10-04 | Test_B blind estimates (truth pending) |
