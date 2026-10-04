# imaging2: slice images of where the brain changed, from the simulated antenna data

**Verdict, Healthy → Mild → Moderate:** the images get *which lobes* changed right on every lobe design.
This holds in clean simulation, on both meshes and against both healthy references:
- **LeftOnly:** left temporal + left parietal, nothing on the right, ✔.
- **Moderate:** frontal + temporal + parietal, occipital spared, ✔.
- **Mild:** temporal + parietal both sides ✔; one mesh adds a small false frontal call.
- **Healthy-vs-healthy and MCI:** empty, ✔.

It holds leave-one-design-out (nothing from the imaged design enters the model). LeftOnly is still exact when *no
Mild-material design at all* is in training.

**How deep the cortex retreated** is recovered to about ±1–3 mm only for Mild/Moderate, and only as a wide posterior.

**Severe fails on depth.** The stage and "all six lobes" are right, but the retreat comes out as 1–12 mm against
a true 11.5–18 mm. The fit test flags it (χ²/dof 2.1–2.6). It extrapolates beyond every training material, and the
very lossy Severe CSF screens tissue more than about 5 mm below the skull.

**Replication (RightOnly_test, a separate solve of LeftOnly's mirror image; §9):**
- The lobe calls replicate exactly as the mirror (S5 + S6 only).
- Depth does **not** replicate: ê 3.0 / 3.5 mm against 11.5 / 7.5 true, with 90% intervals that exclude the truth.
- The secondary variants are not one-sided. Against the other healthy mesh S1/S2 are added; the gain-removing
  inversion calls both sides.
- So the side call is solid only in the primary configuration, and the depth uncertainty is under-stated.

**Blind Test_B (§8): PASS under the protocol committed before the file existed.**
- **Estimate committed before the truth:** Mild; temporal L (S2) and parietal R (S5) affected, all other lobes not; fit 0.46.
- **Truth:** S2 11.5 mm, S5 7.5 mm, Mild.
- **Primary result:** lobes exact, stage correct, both depths inside their intervals in the right order: a blind hit.
- **Secondary variants:** each misses one interval. Gain-removing: S5 interval 6.0–6.5 excludes 7.5. Against H7: S2
  interval 3.0–9.0 excludes 11.5, and the depth order is reversed.

**Post hoc, after the truth (§11):**
- Rotated-mesh nulls come out empty.
- The lobe calls survive every null reference and an inflated noise model.
- Interval coverage on affected lobes is 69% → 78% with every solve-to-solve offset added. Coverage of 78% on
  affected lobes is accepted with the warning (nominal 90%).
- P = 1.00 means the data strongly prefer the lobe under this model.
- One model-free reading (Test_B's ring spread) does not survive the rotated nulls.

Everything below z ≈ 30 mm and deeper than ≈ 1.5–2 cm is not measured by this array. The images fade/hatch it.

**Scope.** One idealised head, simulations only, 5–6 solved designs per fold. This is noise robustness inside one
phantom family, not generalisation to people.

## 1. What exists and what was verified first (§1 of the brief)
- **Field exports (`data/fields`)** are full 3-D volumes, not the z = −9 mm cut plane:
  - grid: 61³ nodes, 3 mm, x, y, z ∈ [−90, 90] mm; all six antennas; 3.4 / 3.6 / 3.8 GHz; plus a ±120 mm T1 export;
  - they cover the array region (z 44–78) and the whole head;
  - they belong to the *healthy v2 head only*. There is no field of any diseased design, so an iterative DBIM
    update of the background is not possible without new HFSS solves. They are used here for the sensitivity fade.
- **Geometry and port order** re-checked against `hfss_geometry_audit_Healthy_sliced.txt`:
  - sector wedges are GM `83 − e_k` / WM `76 − e_k`; CSF_outer is one sphere r 83.5;
  - port sheets at azimuth −90.4 … +149.6°, z = 48.06 mm;
  - Port 1..6 = T4, T3, T2, T1, T6, T5.
- **Duplicates:** `Moderate_lobe_new` and `Severe_lobe_new` duplicate `Moderate_lobe` / `Severe_lobe` (MODEL_CARD 5.2).
  The real mesh pairs are therefore Healthy p6/p7, Mild p5/p6, Moderate p5/p6, Severe p5/p6.
- **Glitch masking** (−30 dB band-relative reciprocity rule, the main session's) reproduces
  `results/05_lobe/qc/masked_points.csv` exactly.
- **The uniform v2 designs (`new_*.s6p`) were not used.** Their own-project mesh noise is larger than the lobe
  signal: Uniform_MCI − v2 Healthy, a change the array cannot see, is 2.3 dB / 15–40° rms, more than the entire
  lobe-Mild signal (0.5 dB / 8° on neighbour paths).

## 2. Method that produced the images (one-page note: `METHOD_surrogate_inversion.md`)
**Image model:** healthy baseline + estimated change.

**Unknowns:**
- one stage per head (sets the diseased gray/white and CSF material);
- per 60° lobe sector, either unaffected or affected with cortex retreat e_k (0.5–22 mm).

**Forward model:** a surrogate trained leave-one-design-out.
- It predicts the complex log-ratio ln(S/S_healthy) (amplitude **and phase**) of all 21 paths at 201 frequencies.
- Physics features: the exact multilayer reflection change ΔΓ_k(f) of each sector's tissue column
  (skin/fat/skull/CSF/GM/WM, transmission-line model).
- Coefficients are shared across the ring's 12 symmetries (rotation + mirror = symmetry augmentation) and fitted by
  ridge regression.

**Solver:** exact Gibbs sampling over sector states, with stage evidence by Chib's method.

**Likelihood noise:** mesh-pair numerical noise + nested leave-one-out model error.
- Corrected for frequency correlation (ℓ ≈ 15 samples).
- Tempered by the fit's own χ²/dof when it exceeds 1 (Birge rule).

**Images:** posterior-mean ε_r and σ (uncertain boundaries come out blurred). Faded/hatched where the HFSS-field Born
SNR of a 1 cm³ change is low; the hippocampus is never estimated (x-hatched).

**Tried and rejected:**
- *Linear depth-moment features* (∫e^{−d/δ}Δε_r, Δσ). They predicted held-out Mild/Moderate/LeftOnly as well, but
  failed on Severe: held-out misfit 94 vs 15 with ΔΓ, against a signal of 170.
- *Evanescent / TE stack features:* never chosen by the inner model selection.
- *v2 uniform designs:* noise, see above.

**Not repeated, on purpose (results/imaging/lobe_report.md §3–§8, lobe_review.md):**
- *Radar / DAS / DMAS:* peaked at the head centre and did not track the lobes.
- *Linear Born with healthy fields:* missed 56–67% of ΔS. Its sector calls depended on a threshold tuned on Mild,
  on the reference mesh and on κ.
- *DBIM:* needs fields of a perturbed head, which do not exist here.

The surrogate above replaces the Born forward model with one trained on the solved designs. Its calls need no tuned
threshold: they are posterior probabilities.

**Model-free check:** `detuning_ring_raw_data.png` shows the per-antenna phase delay of the neighbour paths straight
from the data. The lobe pattern is visible before any model is applied.

## 3. Scores (truth used only here; `scores_designs.csv`, `scores_sectors.csv`)
- Leave-one-design-out, clean simulation, matched-stop-rule healthy reference.
- `e` = cortex retreat (mm). Calls are P(affected) > 0.5.
- Image corr / rel. err = σ-change map against the truth over the sensed brain (3-D grid, fade opacity ≥ 0.5).
- Fit = χ²/dof at the best state; ≈ ≤ 1 is consistent with the noise model.

| design (mesh) | stage est. (P) | lobe calls correct /6 | MAE e (affected) mm | e pattern corr | truth in 90% interval /6 | image corr | image rel. err | fit χ²/dof |
|---|---|---|---|---|---|---|---|---|
| Healthy, other mesh | Healthy (1.00) | 6 | 0.0 | – | 6 | – | – | 0.36 |
| Mild p5 | Mild (1.00) | 5 (S1 called at ê = 1 mm) | 2.6 | 0.99 | 4 | 0.82 | 0.40 | 1.01 |
| Mild p6 | Mild (1.00) | 6 | 3.0 | 0.95 | 4 | 0.94 | 0.22 | 0.56 |
| Moderate p5 | Moderate (1.00) | 6 | 1.4 | 0.96 | 6 | 0.94 | 0.16 | 0.32 |
| Moderate p6 | Moderate (1.00) | 6 | 3.0 | 0.91 | 6 | 0.91 | 0.21 | 0.30 |
| Severe p5 | Severe (1.00) | 6 | **13.5** | 0.40 | 3 | **0.09** | 0.42 | **2.59** |
| Severe p6 | Severe (1.00) | 6 | **11.8** | 0.49 | 4 | **0.17** | 0.38 | **2.12** |
| LeftOnly p6 | Mild (1.00) | 6 | 2.0 | 0.97 | 6 | 0.97 | 0.22 | 0.41 |
| MCI p6 | Healthy (1.00) | 6 | 0.0 | – | 6 | – | – | 0.37 |

**Left/right (LeftOnly):**
- ê_left − ê_right = **+11.5 mm** (truth +9.5).
- Mirrored data give −11.5. LeftOnly against the other healthy mesh gives +8.75.
- **Strict leave-one-stage-out** (no Mild-material design in training): still exactly S2 + S3, ê = 11.5 / 6 mm
  (truth 7.5 / 11.5; `posteriors_loso.json`).

**Left/right null (the mirror-symmetric files):** every one of the nine mirror-symmetric files gives mirror-symmetric
lobe calls (Healthy p7, MCI, Mild p5/p6, Moderate p5/p6, Severe p5/p6). That includes Moderate_lobe p5, whose 2° mesh
mirror asymmetry the round-2 review measured (MODEL_CARD 6.1 R1b). LeftOnly is the only file with one-sided calls.

On *depth*, the left − right difference of ê in the symmetric files is ≤ 2 mm, except Severe p5 (−4.0 mm) and
Severe p6 (−9.25 mm), whose depth is undetermined. So **the side call is established by the lobe calls, not by the ê
difference.**

**Front/back (Moderate):** frontal ê = 12.5 (p5) / 6.0 (p6) mm against occipital 0 (truth 11.5 / 0).

**Mesh:** the second mesh of each design gives the same lobe pattern. One exception: Mild p5's S1 call.

## 4. Controls (`controls_sig_z50.png`)
- **Prior alone (no data):** a faint uniform ring (P(affected) 0.38 everywhere). It is not a lobe pattern, so the
  patterns above come from the data.
- **Healthy vs other healthy mesh; MCI:** P(Healthy) = 1.00, change map empty.
- **Mirrored LeftOnly data → right lobes (S5, S6); rotated 180° → S5, S6.** Equivariant, as it must be.
- **Paths shuffled (Mild data with the 21 path labels permuted):**
  - The image is NOT empty: S6, and S3 at P 0.45.
  - The fit test rejects it: χ²/dof = 23, against 0.3–1.0 for every real design.
  - So images must always be read with their fit value, which is printed on every panel.

## 5. Noise (`noise_sig_z50.png`, `noise_study.json`; K = 12 draws per condition, both scans noisy)
Columns are the four conditions (instrument noise on both scans):
- **typical:** 0.25 dB / 2° / −70 dB floor;
- **noisy:** 0.5 dB / 5° / −60 dB floor;
- **+ drift:** a per-port ±0.5 dB / ±5° gain/phase change between baseline and follow-up;
- **gain-free:** the inversion that projects out per-port gains.

Cells give the stage correct, all six lobe calls exactly right, and for LeftOnly the left side ahead by > 2 mm.
Leave-one-design-out, same rules as the clean run (`noise_summary.csv`).

| design | typical | noisy | noisy + drift (not modelled) | noisy + drift, gain-free |
|---|---|---|---|---|
| Healthy, other mesh | 100% / 100% | 100% / 100% | 100% / 100% | 100% / 100% |
| MCI | 100% / 100% | 100% / 100% | 100% / 100% | 100% / 100% |
| Mild p5 | 100% / 0%* | 100% / 0%* | 83% / 0%* | 100% / 33% |
| Moderate p5 | 100% / 100% | 100% / 100% | 42% / 33% | 100% / 83% |
| Severe p5 | 100% / 100% | 100% / 100% | 100% / 50% | 100% / 75% |
| LeftOnly p6 | 100% / 100% / left 100% | 100% / 75% / left 100% | 58% / 17% / left 58% | 100% / 92% / left 100% |

\* Mild p5 has 5/6 calls right in every draw: its clean result already calls S1 at ê ≈ 1 mm (§3). That is a
property of that mesh's data, not of the noise.

- **LeftOnly under 0.5 dB / 5° noise:** the failures are missed left lobes (S2 or S3 not called), never a right-side
  call: right-side calls 0/12 in every condition except unmodelled drift (2/12).
- **Healthy and MCI** stay empty in all 48 noisy reconstructions each.

Per-port drift between baseline and follow-up must be modelled. The gain-free inversion (per-port log-gain
projected out) restores the lobe pattern.
- **Depth under noise:** with the instrument noise in the likelihood, the gain-free inversion recovers the same depths
  as the standard one. LeftOnly median ê is 4.5 / 7 mm (gain-free) against 4 / 7 mm (noisy, no drift).
  - Only in the clean, mesh-noise-only test did gain-free depths collapse, to 1–1.5 mm.
- **Noise biases depth low across the board** (median over draws, truth in brackets):
  - LeftOnly S2/S3: 6.75 / 10.25 typical, 4 / 7 noisy (7.5 / 11.5);
  - Moderate: 11.5–12.5 typical, 5.5–9.75 noisy (11.5–15.5).
- **Mild p5's false frontal call grows** under noisy data, to a median ê of 8 mm in S1.

## 6. Failures and limits, stated plainly
- **Severe depth.**
  - Not recovered (ê 1–12 mm vs 11.5–18). The posterior intervals are wide after Birge tempering, but the medians
    are wrong.
  - Physics: χ² against a uniform retreat is flat from 6 to 20 mm for Severe. A Severe CSF layer (σ 6.4 S/m,
    loss tangent ≈ 1) attenuates the field within ≈ 5 mm, so the array cannot see deeper.
  - Model: Severe materials lie outside every training design.
- **Depth beyond ≈ 10 mm** is weakly determined even for Mild/Moderate (90% intervals 5–21 mm).
- **Vertical extent is not observed.** The full-height wedge is imposed by the model; below z ≈ 30 mm the
  images are faded because the array has no sensitivity there (Born SNR of a 1 cm³ change ≤ 0.6 at z = 20, ≤ 0.26
  at z = 0).
- **Hippocampus (MCI, r_hip):** not estimable at all.
- **Scope.** One phantom family, 6 distinct lobe designs. Every number is within-simulation, and the stage structure
  (one stage per head, 60° wedges) is a prior taken from how the phantoms were built.

## 6b. Decisions made after looking at held-out results (disclosed; nothing here was pre-registered)
1. **Feature family.**
   - The first surrogate used linear depth-moment features. Its leave-one-design-out errors on *all* designs,
     Severe included, were seen before switching to the layered-stack ΔΓ feature.
   - That choice is therefore informed by the test designs, even though truth never entered a fit.
   - Within the ΔΓ family, the variant and λ are chosen by nested leave-one-out on training designs only (all folds
     picked the simplest one).
2. **Birge tempering** was added after seeing Severe's over-confident posterior. It is applied by one rule to every
   target, uses only the target's own data, and can only widen a posterior. It changed only Severe (×2.6 / ×2.1) and
   the shuffled control (×23).
3. **The 3.30–3.65 GHz window of the model-free detuning figure** comes from the earlier LeftOnly review (B7), so it is
   post hoc (MODEL_CARD 6.1 A18). The inversion itself uses the whole 3.2–4.2 GHz band.
4. **Fade thresholds** (SNR 0.5 → 4) were set from the field-based SNR values, not from any reconstruction.
5. **Not changed after seeing results:** prior (stage 1/4, P(unaffected) 1/2, flat e), e grid, frequency band
   3.2–4.2 GHz, reference pairing (matched stop rule), noise ruler.

## 7. Figure index (`figures/`, each PNG has a `.npz` with the arrays where applicable)
**Best for slides (in this order):**

1. `stack_sig.png`: **the main image.**
   - Truth vs reconstruction of the conductivity change for Mild, Moderate, Severe and LeftOnly at z = 80, 70, 60,
     50, 40, 20, 0 mm, same scale.
   - Trust: lobe pattern high at z 40–70 (clean simulation, leave-one-design-out); depth moderate (Mild/Moderate,
     ±1–3 mm, wide intervals); Severe depth not trustworthy; z ≤ 20 is faded because it is not measured.
2. `overview_sig_z50.png`: one slice at the ring for all six designs incl. Healthy and MCI, with truth, error and the
   per-lobe retreat bars (median + 90% interval, P(affected)). The quantitative summary slide.
3. `detuning_ring_raw_data.png`: **model-free.**
   - The per-antenna neighbour-path phase delay (3.30–3.65 GHz) straight from the S-parameters.
   - LeftOnly 6.4/6.8° on the left vs 2.1/2.2° on the right; Moderate frontal 11.9° vs occipital 7.6°.
   - Shows the pattern is in the data, not drawn by the model. Spatially blurred (each antenna also sees its
     neighbours' lobes), so it is not a lobe map by itself.
4. `controls_sig_z50.png`: prior alone, healthy-vs-healthy, MCI, mirrored data, shuffled data, other reference.
   Shows the method draws nothing without data, follows a mirror, and that shuffled data are caught only by the fit test.
5. `noise_sig_z50.png`: expected image under typical and 0.5 dB / 5° instrument noise on both scans, with and without
   per-port drift, and the gain-free remedy. Success rates printed per panel.
6. `loso_sig_z50.png`: Mild and LeftOnly imaged with no Mild-material design in training. The strongest evidence that
   the left-only image is not a look-up.
7. `views_sig_Moderate_p5.png` (and `views_sig_LeftOnly_p6.png`): coronal and sagittal slices. The reconstruction
   lives in the cap around the antenna ring; everything below is hatched as unmeasured.
8. `mesh_pairs_sig_z50.png`: each stage on its two meshes, i.e. the numerical-noise ruler as an image.

**Complete sets:**
- `slices_{sig,eps}_<target>.png`: baseline | estimated change | estimated head | true head | error at all seven
  heights, for every target and control (σ and ε_r). The data behind them is in `slices_*.npz` (local; regenerate with
  `make_figures`).
- `overview_eps_z50.png`, `stack_eps.png`: the same in permittivity.
  - ε_r rises at Mild (CSF 55 replaces gray 47.7) and falls at Severe (CSF 32.5), so its sign changes with stage.
  - σ rises in every affected lobe, so σ is the clearer quantity to show.
- `views_sig_<target>.png`: coronal/sagittal for Mild, Moderate, Severe, LeftOnly.

**Data files:**
- `posteriors.json`: posterior summaries, stage evidence, fit and tempering per target; selected model per fold.
- `posteriors_loso.json`: the leave-one-stage-out variant.
- `cache/marg_<target>.npy`: joint posterior P(stage, sector state) behind every image.
- `scores_designs.csv`, `scores_sectors.csv`: the scores.
- `noise_study.json`, `noise_summary.csv`: the noise study.

## 8. Blind design Test_B (estimates committed before the truth; scored after)
- **Commits:**
  - protocol `595e9cb` (`BLIND_PROTOCOL.md`, before the file existed);
  - fix of a syntax error in a figure title, found before Test_B was read: `d83d1d5` (`blind/DEVIATIONS.md` item 1);
  - reconstruction `c0fafd6`.
- **Inputs:** training = all nine lobe observations; the Test_B header was not read.
- Full report: `blind/Test_B/report.md`.

| variant | stage (P) | lobes called (P > 0.5) | ê S2 TL [90%] | ê S5 PR [90%] | other lobes | fit χ²/dof → rule |
|---|---|---|---|---|---|---|
| standard vs H6 (**PRIMARY**) | Mild (1.00) | S2, S5 | 13.0 [7.0–21.5] | 7.0 [6.5–12.5] | P(aff) 0.00 | 0.46 → OK, not rejected |
| gain-removing vs H6 | Mild (1.00) | S2, S5 | 6.5 [6.0–11.5] | 6.0 [6.0–6.5] | P(aff) 0.00 | 0.77 → OK |
| standard vs H7 | Mild (1.00) | S2, S5 | 3.5 [3.0–9.0] | 7.5 [7.0–17.5] | P(aff) 0.00 | 0.42 → OK |

- **Model-free ring** (neighbour-path phase delay, 3.30–3.65 GHz, T1…T6):
  - vs H6: 3.5 / 5.6 / 4.3 / 3.5 / 5.2 / 3.9°, largest at T2 and T5;
  - vs H7: 4.9 / 6.9 / 5.7 / 4.9 / 6.7 / 5.6°.
- **How much to trust it** (from §3, §5 and §9):
  - the lobe calls are the robust part;
  - the stage was right on every Mild-material design;
  - the ê values differ across variants by up to 9.5 mm (S2), and RightOnly showed that the 90% intervals can
    exclude the truth.
- **Figures** (`blind/Test_B/`): `overview_sig_z50_Test_B.png` (standard style, no truth row), `blind_stack_Test_B.png`,
  `blind_overview_Test_B.png` (z 60/50/40), `blind_slices_{sig,eps}_Test_B.png` (baseline | change | head | posterior
  SD), `blind_views_Test_B.png`, `blind_detuning_Test_B.png`.

**Score (truth revealed after all three sessions had committed; scored with the committed scorer, `f88236c`):**
- **Truth:** e = 0 / 11.5 / 0 / 0 / 7.5 / 0 mm; Mild gray/white in S2 and S5; HIP_Mild; CSF_Mild; r_hip 17.5.
- **Files:** `blind/Test_B/truth.json` (the user's values in the protocol's format), `score.md`, `score.json`,
  `blind_scored_Test_B.png`.

| variant | stage | lobe calls (C1) | stage (C2) | truth inside 90% (C3) | fit | protocol verdict |
|---|---|---|---|---|---|---|
| standard vs H6 (**PRIMARY**) | Mild | 6/6 PASS | correct | 6/6 | 0.46 OK | **PASS** |
| gain-removing vs H6 | Mild | 6/6 PASS | correct | 5/6 (S5 6.0–6.5 excludes 7.5) | 0.77 OK | PASS (C3 needs ≥ 4/6) |
| standard vs H7 | Mild | 6/6 PASS | correct | 5/6 (S2 3.0–9.0 excludes 11.5; order reversed) | 0.42 OK | PASS (C3 needs ≥ 4/6) |

- **User's scoring:** a blind hit (lobes exact, stage correct, primary depths inside their intervals in the right
  order).
- **Across sessions:** imaging2 is the only one with stage Mild correct and "both sides". Main staged it Normal and
  read the side as left; the Born imaging read "none".
- **Open problem:** together with RightOnly, interval coverage. The secondary variants' intervals miss.
- **Presentation figures:** `figures/TestB_vs_truth_pres.png` (z = 50 overview with truth, estimate and error rows),
  `figures/TestB_stack_truth_pres.png` (slice stack, true affected region outlined at Δσ = 1 S/m).

## 9. RightOnly_test: replication of the left/right result (geometry known; `rightonly/rightonly.md`)
- **Setup:**
  - RightOnly = LeftOnly mirrored (e = 0/0/0/0/11.5/7.5 mm; header checked), a separate solve with 1 converged pass.
  - Reconstructed with **exactly the LeftOnly fold** (training = every lobe design except LeftOnly). With LeftOnly in
    training, its mirrored copy would be RightOnly's truth.
  - LeftOnly's rerun with that fold reproduces the committed marginals bit for bit.
- **Lobe calls (primary, vs H6):** S5 + S6 only, P(affected) 1.00 / 1.00, all others ≤ 0.01, stage Mild, fit 0.57.
  This is the exact mirror of LeftOnly (S2 + S3) and the exact truth.
- **Depth does not replicate.**
  - RightOnly: ê 3.0 [2.5–3.5] / 3.5 [3.5–3.5] mm. Mirrored LeftOnly: 11.5 [5.5–21.5] / 11.5 [5.0–21.0]. Truth 11.5 / 7.5.
  - RightOnly's intervals exclude the truth: the posterior is over-confident for this solve.
- **Secondary variants are not one-sided:**
  - vs H7 it calls S1, S2, S5, S6 (ê 1.5 mm in S1/S2);
  - gain-removing it calls S2, S3, S5, S6 (ê 1–1.5 mm on the left).
  - LeftOnly's secondaries were one-sided.
- **Data level.** RightOnly − mirror(LeftOnly) is 1.7–2.2× the mesh-pair ruler on reflection and neighbour paths.
  - Mostly a near-uniform extra phase delay: band-mean −3.1° neighbour, −3.9° second-neighbour, −3.3° opposite.
    That is about twice the healthy mesh-to-mesh offset.
  - RightOnly's change is 1.5–1.7× LeftOnly's on these paths; correlation with mirrored LeftOnly 0.85–0.88.
  - The **right − left contrast replicates within 0.2°** in the model-free ring: +4.60° vs +4.44° (mirrored LeftOnly),
    +4.85° vs H7.
- **R1c (null = the nine mirror-symmetric designs):**
  - On LR_e (ê left − right) the floor is 9.25 mm, set by Severe_p6, whose depth is undetermined. LeftOnly 1.24×
    and RightOnly 0.35× → **not separable**.
  - On the calls the floor is exactly zero (all nine nulls give mirror-symmetric calls), so the ratio is **not
    applicable**. One-sided call patterns: 0/9 nulls, LeftOnly yes, RightOnly primary yes, its two secondaries no.
- **Reading:**
  - The side information in the data replicates.
  - The inversion's lobe calls replicate in the primary configuration only.
  - Its depth and its uncertainty do not replicate. The noise model (mesh pairs + model error) under-states
    solve-to-solve variation of the kind RightOnly shows (a uniform ~3° offset).

## 10. Presentation copies
`figures/{overview_sig_z50,overview_eps_z50,controls_sig_z50,detuning_ring_raw_data}_pres.png`: same content, "other
mesh" wording replaced by "repeat simulation".

## 11. POST HOC, after the Test_B truth (`posthoc/posthoc.md`, `imaging2/posthoc.py`; everything here is post hoc)
- **Unchanged:** committed estimates, the protocol, verdicts, thresholds.
- **New files:** recorded in imaging2's own set file `sets.csv`; never in any training set.
  - Null_rot07 (6 passes, ΔS 0.01465, 1,045,101 elements) and Null_rot19 (6, 0.014495, 939,082);
  - RightOnly (5, 0.019742, 789,241) and Test_B (6, 0.012597, 903,758).
- **Masking:** the −30 dB rule masks the reported rot07 point (3.86 GHz, T4–T1). It also masks 3.565 GHz T2–T1 in
  rot07, 3.87 GHz T4–T1 in rot19, and 3.84–3.85 GHz T1–T5 in Test_B.

**A. Rotated nulls as targets** (training = every lobe design; nulls never trained on): **empty**.
- 0 lobes called in all 8 runs (rot07, rot19 × H6, H7 reference × standard, gain-removing).
- Stage Healthy in 7/8. rot07 vs H7, gain-removing, says Mild with no lobe: a whole-head CSF reading from a mesh offset.
- Fits 0.30–2.01; rot19 vs H7 reaches the "poor fit" band.

**B. Each rotated null as the healthy reference.**
- **Standard variant, lobe calls hold in 6/6 runs:** Test_B S2 + S5; LeftOnly S2 + S3; RightOnly S5 + S6.
- **Gain-removing variant:** Test_B 2/2 and LeftOnly 2/2 hold; RightOnly fails 2/2 (adds S2 against rot07; only S6
  against rot19).
- **Stage is reference-sensitive:** with rot19 as reference the standard variant says Moderate for Test_B, LeftOnly
  and RightOnly.

**C. Pass gap (5 vs 6 passes).** RightOnly − mirror(LeftOnly), against the three pass-5 vs pass-6 twins (Mild, Moderate,
Severe), same statistics and frequencies:
- **Same signature:** a uniform phase lag. Band-mean neighbour phase is 3.05° against 2.37–2.53°; the model-free ring
  mean is +2.81° against +2.15 to +2.33°.
- **Larger than all three twins** on 12/16 statistics over 3.2–4.2 GHz and 11/16 over 3.30–3.65 GHz, by 5–39%.
- **Signal-size ratio** RightOnly / mirrored LeftOnly: 1.76 (reflection amplitude) and 1.74 (neighbour phase), against
  1.15–1.50 and 1.15–1.43 for the twins.
- **At reconstruction level** the change of ê (max 8.5 mm) equals the Severe twin's (8.5) and exceeds Mild's (5.5) and
  Moderate's (6.5).
- **Verdict by the stated rule:** the difference is larger than the pass-5/6 twins, so **the pass gap does not explain
  it fully**. It has the pass gap's form, a uniform lag, but is 1.05–1.39× its size. The mirrored mesh orientation is a
  candidate for the rest: the rotated null rot19 vs H6 is as large on second-neighbour and opposite paths (0.96 dB,
  8.0°). That is an interpretation, not a test.

**D. Rulers rebuilt with the rotated nulls** (R1c: floor = max |null| over the 9 old + 2 rotated; 3x bar). Each current
claim and reading:

| claim / reading | old | with rotated nulls | survives? |
|---|---|---|---|
| Healthy, MCI and both rotated nulls reconstruct empty | 0 lobes | 0 lobes (8/8 runs) | yes |
| LeftOnly / RightOnly one-sided lobe calls | 0/9 nulls one-sided | 0/11 | yes (the ratio is not applicable: floor 0; rank p 1/12) |
| ê left − right (LR_e) | 1.24x (not separable) | 1.24x | not separable (unchanged) |
| model-free ring left − right contrast, LeftOnly / RightOnly | 4.87x / 5.05x | 4.87x / 5.05x (rotated 0.69, 0.28 < floor 0.91) | yes |
| model-free ring front − back, Moderate (`posthoc/ring_front_back_check.txt`) | 8.0x / 7.8x | **3.2x / 3.1x** (rot07 1.32°) | yes, barely |
| Test_B ring spread | 5.12x | **1.49x** (rot07 1.42°) | **no** (not separable) |
| Test_B diagonal-pair elevation (largest of 3 pairs; defined after seeing Test_B) | 12.8x | 3.73x | yes, but post hoc statistic |
| Test_B T2/T5 elevation (Test_B's own pair) | 20.9x | 5.79x | post hoc pair, not a test |
| "healthy meshes differ by 1.3–1.6° uniform" (detuning figure ruler) | — | non-uniform spread up to 1.42°, front − back up to 1.32° | ruler text was optimistic |

Your listed null numbers reproduce: rot19 second-neighbour power pairs 0.44 / 0.74 dB; reflection pairs ≤ 0.011 dB;
rot07 phase pairs at 3.4 GHz 1.67 / 1.78°; ring spread 1.42° / 0.68°.

**E. Noise model with every solve-to-solve offset.**
- **Samples added in quadrature** to the fold noise; each twin is taken as one observation's error, and the target's
  own twin is excluded:
  - H7/H6;
  - rot07/H6 and rot19/H6;
  - Mild/Moderate/Severe 5/6;
  - RightOnly/mirror(LeftOnly).
- **Empirical 90% coverage of ê** over the 9 leave-one-out targets + RightOnly + Test_B (primary):

| | all 66 sectors | 36 affected sectors | lobe calls correct |
|---|---|---|---|
| before (committed noise model) | 83% | **69%** | 98% |
| after | 88% | **78%** | 100% (Mild p5's false S1 call disappears) |

- Coverage of 78% on affected lobes is accepted with the warning: it is above the 70% threshold but below the nominal
  90%.
- **The 8 remaining misses:**
  - 3 near-misses on Mild's 7.5 mm lobes (intervals start at 8.0);
  - Severe S1/S2 on both meshes (depth undetermined);
  - RightOnly S6 (3.0–4.0 vs 7.5).

**Challenge: is P = 1.00 believable?** Not as a calibrated probability.
- **With the augmented noise:**
  - Test_B P(S2) = P(S5) = 1.00 and P = 0.00 elsewhere, in all three variants.
  - RightOnly's wrong lobes stay: gain-removing P(S2) = **1.00**, P(S3) = 0.67; against H7, P(S1) = 0.69.
- **Calibration:** confident calls (P ≥ 0.99 or ≤ 0.01) were wrong 1 of 84 times before and 1 of 82 after. It is the
  same call each time, RightOnly gain-removing S2.
- **Reading:** P = 1.00 means the data strongly prefer the lobe under this model. The model does not represent
  solve-to-solve offsets well enough for the number to be a probability.

**F. Ring-mean-phase variant** (the phase ring mean of every path class removed at every frequency):
- **RightOnly:** S5 + S6, ê 13.5 [4.5–21.0] (truth 11.5, now covered) and 3.5 [3.5–4.0] (7.5, still missed).
- **Test_B:** S2 + S5, ê 8.0 [7.5–20.5] and 7.0 [7.0–16.5], both covered.
- **Controls:** Healthy, MCI and both rotated nulls are empty.
- **Stage did not weaken:** Mild 1.00 for RightOnly and Test_B; Mild, Moderate and Severe correct on the leave-one-out
  designs. The amplitude ring mean and the frequency shape of the phase pattern still carry it.
- **Severe p5:** S2/S3/S5 depths become 13–13.5 mm (truth 17.5–18) instead of 2 mm, but S1/S4 stay at 0.5; fit 1.87.

## 11b. POST HOC round 2: the rot19 question, stage vs reference, variant choice (`nullrulers/report.md`)
- **Pre-registration:** committed before Null_rot31 / Null_rot43 exist as `a295006` (`ROTATED_NULLS_PROTOCOL.md`).
  - Every ruler = max over all nulls (old 9 + every rotated null), none dropped.
  - Reported three ways: all; without rot19; rot19 alone.
  - Readings R1–R12 with their existing bars.
  - `python -m imaging2.nullrulers all` runs unchanged when the files arrive.
- **Evaluation:** the numbers below come from that code with the nulls present now (rot07, rot19), commit `d939eec`.

**Section 0, common-mode vs scattered** (reported as found; no conclusion beyond it).
- **Definitions:** your numbers reproduce with the mean of the dB difference (rot19 second-neighbour, 3.30–3.65 GHz:
  −0.64 / +0.02 / −0.23 / −0.85 / −0.70 / −0.90 dB). Band power (dB of mean |S|²) gives the same pattern, smaller:
  −0.47 / +0.12 / −0.16 / −0.42 / −0.38 / −0.54.

| pair | k = 1 power | k = 2 power | k = 3 power | phase |
|---|---|---|---|---|
| rot07 vs H6 | scattered | scattered | scattered | scattered in every class, both bands |
| rot19 vs H6, 3.30–3.65 GHz | mixed (+0.22 ± 0.12 dB) | mixed (−0.31 ± 0.23) | **common-mode (+0.31 ± 0.06, all six +0.26 to +0.40)** | k3 common-mode (−3.1°) |
| rot19 vs H6, full band | **common-mode (+0.15 ± 0.04)** | scattered | **common-mode (+0.25 ± 0.10)** | mixed / scattered |
| rot07 vs rot19, 3.30–3.65 GHz | mixed | **common-mode (+0.36)** | **common-mode (−0.28)** | k3 common-mode |
| Mild, Moderate, Severe 5 vs 6; H6 vs H7; RightOnly vs mirror(LeftOnly) | mostly scattered or mixed; Mild k1 common (+0.07); H6/H7 k3 common (−0.13) | scattered or mixed | scattered or mixed, except H6/H7 | **common-mode in every class, both bands** (the uniform pass-gap lag) |

- Among the twin pairs, a class-wide *power* shift of the opposite class shows only in H6 vs H7 (−0.13 dB, opposite
  sign). The twins share a class-wide *phase* lag that rot07 does not show and rot19 shows only in k = 3.

**Stage and lobe calls vs every reference** (13 targets × H6, H7, rot07, rot19 × 3 variants; full table in
`nullrulers/report.md` §1).
- **Is it only rot19 that moves the stage? Yes.**
  - Standard variant: 8 of its 9 wrong stages use rot19 as reference. All Mild-material targets become Moderate,
    Moderate_p5 becomes Severe (with S1/S3/S5 lost), and MCI becomes Mild (no lobes). The ninth is MCI vs H7 (Mild, no
    lobes).
  - **rot07 behaves like H6:** 0 wrong stages and 0 wrong lobes in 12 standard runs.
  - Ring-phase: all 7 wrong stages are rot19.
  - So the stage fragility is the same rot19 question as Section 0.
- **Lobe calls with rot19 as reference:** wrong only for Moderate_p5 (3 lobes lost, all variants) and Moderate_p6
  (ring-phase). Test_B, LeftOnly and RightOnly keep exact lobes with rot19 in the standard and ring-phase variants.

**Rulers three ways (R1c):**
- **Binding null:** for the model-free ring rulers it is **rot07**, not rot19: front − back floor 1.32°, Test_B spread
  floor 1.42°. "Without rot19" therefore equals "all".
- **rot19 alone** would give LR contrast 16x, front − back 33x, Test_B spread 3.1x.
- **LR_e:** stays not separable (floor 9.25 mm from Severe_p6).
- **Coverage on affected lobes:** 78% with all nulls; **83% without rot19**; 78% with rot19 alone.

**Variant choice for real hardware: recommendation.**

| variant | clean, every target × reference (49 runs): wrong lobe calls (runs) / wrong stages | noisy 0.5 dB, 5° + per-port drift ±0.5 dB, ±5° (96 draws, identical draws for all variants, `posthoc/variants_drift.md`): exact lobes / stage correct / wrong lobes per draw |
|---|---|---|
| standard | 7 (4) / 9 | 47% / 82% / 0.73 |
| **gain-removing** | 19 (11) / 8 | **90% / 99% / 0.10** |
| ring-mean-phase | **6 (2), all vs rot19** / 7 | 44% / 76% / 0.80 |
| gain-removing + ring-mean-phase (post hoc) | 25 (12) / 9 | 84% / 94% / 0.18 |

- **No variant is robust to both error types.**
  - Per-port drift breaks the variants that keep the per-port gains (standard, ring-phase: 0.73–0.80 wrong lobes per
    draw).
  - Non-gain differences between baseline and follow-up (the mesh offsets) break the gain-removing ones most (19–25
    wrong lobes in 49 runs; P = 1.00 on RightOnly's wrong S2).
- Requiring two variants to agree did not help on the drift draws. The best rule, gain-removing AND gain + ring, gives
  83% exact against 90% for gain-removing alone.
- **Recommendation: gain-removing for real hardware unless per-port drift is calibrated out.**
  - Drift is certain on hardware and was the larger error: 0.10 against 0.73 wrong lobes per draw.
  - Its weakness should be stated with every result: it is the least stable to non-gain baseline differences.
  - Show the standard and ring-phase results alongside it.
  - If calibration brings drift well below ±0.5 dB / ±5°, ring-phase is the more stable choice across references. The
    drift level at which that switch pays off has not been tested.

## 12. What I would do next
1. **Solve 2–3 designs that turn Severe into interpolation:** e.g. Severe materials in the left lobes only, and Mild
   materials at e = 3 mm and e = 20 mm. Today every Severe-material state is outside the training set.
2. **Export fields of one diseased design** (Moderate_lobe, same 3-D grid). That enables a distorted-Born / DBIM
   correction of the surrogate and a field-based depth-sensitivity check for lossy CSF.
3. **Vertical information:** a second, lower ring (z ≈ 0–20 mm) or tilted antennas. The vertical extent of the
   lobes is imposed by the model at present, and nothing below z ≈ 30 mm is measured.
4. **Real-measurement mode** (updated post hoc, §11b):
   - Use the gain-removing inversion by default, unless per-port drift is calibrated out. It is the only tested
     variant that survives ±0.5 dB / ±5° drift.
   - It is also the most sensitive to non-gain differences between baseline and follow-up.
   - Show the standard and ring-phase results alongside, and expect depth to be biased low under realistic noise.
5. **Anatomy variation** (head size, skull/scalp thickness, stand-off) is still untested and decisive. Every result
   here is one idealised head.

## 13. Reproduce
```
python -m imaging2.run_lobe2 --sweeps 600     # all leave-one-design-out inversions + controls (≈ 3 min)
python -m imaging2.run_loso                   # leave-one-stage-out variant (≈ 1 min)
python -m imaging2.noise_study --k 12         # measurement-noise study (≈ 20 min, 6 processes)
python -m imaging2.make_figures               # figures + scores (≈ 15 min)
python -m imaging2.blind run --file new_with_slices_Test_B.s6p --tag Test_B   # blind protocol (595e9cb / d83d1d5)
python -m imaging2.extras rightonly           # RightOnly replication check (≈ 3 min)
python -m imaging2.extras testb               # Test_B z = 50 overview (standard style)
python -m imaging2.extras pres                # *_pres.png copies
python -m imaging2.posthoc all                # POST HOC analyses after the Test_B truth (≈ 12 min)
python -m imaging2.posthoc figs               # TestB_vs_truth_pres.png, TestB_stack_truth_pres.png
```
Code hash in `posteriors.json` (`code`). The field cache `cache/fields_head.npz` is rebuilt from `data/fields` on
first use (≈ 30 s). Nothing outside `imaging2/` and `results/imaging2/` is written.
