# Track A — running summary

**Standing caveats**

- One simulation per stage, so results show noise robustness only, not generalisation to
  new heads.
- The between-mesh noise floor has not been measured yet. All AD-vs-AD comparisons are
  **unverified against mesh noise**.
- Headline scheme: `binary` (Normal vs AD).

## Prompt 03 — quality gate, classifiers, decision boundaries (code `3ad19cb`)

Details are in `results/03/report.md`, `results/03/decision_rule.md`, `results/03/*.csv` and
`results/figures/03_*.png`. `metrics.csv` gained 1332 rows (12 feature sets × 6–7 models × 6
profiles × 3 schemes). `binary_early` is skipped because there is no MCI simulation yet. To
regenerate from a new `sims.csv`, run `python scripts/run_all.py`.

**Validity.** Every result is **noise-robustness only**: one simulation per stage, one head
geometry. The 3-class schemes are also **unverified against mesh noise**.

**Samples and CV**

- A sample is one antenna view (a driven antenna and its received column) of one noisy draw.
  Views of one simulation are not independent.
- Each draw applies:
  - the prompt-02 measurement noise;
  - ±1.5% cable/connector amplitude variation per antenna;
  - a 10° reference-plane phase offset per port;
  - 1 MHz frequency jitter.
- Train and test draws use different seeds.
- CV:
  - A class with one simulation holds out a **diameter**: antennas t and t+3 leave together.
    Otherwise the held-out opposite path would still be in training via reciprocity.
  - A class with ≥ 2 simulations holds out whole simulations. So in `binary`, each fold
    tests an AD stage the model has never seen.
  - Sub-band windows, COMB features, the M7 reference, the regularisation C and the Platt
    calibration are all fit inside the training folds.

**Feature sets.** M3 and M4 are dropped: in this geometry absorbed power reduces to
reflection. Coupled power is only ~4e-4 of the incident power, so N = 1 − R − C ≈ 1 − R and
M4 ≈ M3 = 1 − M2.

**Quality gate: INVALID rate**

| Case | ideal … noisy | very_noisy |
|---|---|---|
| Clean draws | 0% | 3.1% (passivity: noise pushes the column power past 1.2) |
| ±2–20 MHz resonance shift | 0% | 2.5–3.7% |
| Notch flattened | 0% | 3.7% |
| **One antenna open** | **100%** (open/short 100%, symmetry 100%) | 100% |
| **One antenna short** | **100%** | 100% |
| All open / all short | 100% | 100% |
| Detuned ±200 MHz | 100% (detune check) | 100% |

**Binary (headline) at `typical`, balanced accuracy, CV**

| Feature set | Best model | typical | noisy | very_noisy |
|---|---|---|---|---|
| M9 full spectrum (upper bound) | LDA | 1.000 | 1.000 | 0.998 |
| COMB (nested: M5.C3 + A[3.40] + C2) | LDA | 1.000 | 0.999 | 0.960 |
| M5.C3[nested] (window 3.40–3.50 GHz in 6 of 9 folds) | LDA | 1.000 | 0.990 | 0.893 |
| **M5.C3 full band (primary)** | **THR (τ)** | **0.977** | 0.969 | 0.825 |
| M5.C3[k3] (secondary, post-hoc window) | LDA | 0.996 | 0.993 | 0.889 |
| M0 old score | any | 0.585 | 0.60 | 0.57 |
| M2 power reflection | any | ≤ 0.54 | | |
| M1 dB reflection | any | ≤ 0.51 | | |

**Reflection-based metrics fail once setup variability is included.** M0's Normal–AD gap
is ~2% of its value and M2's ~1%. A ±1.5% per-antenna amplitude variation is enough to hide
both. The opposite-antenna gap is ~1.9 dB (≈ 55% in power) and survives. So the prompt-02
advantage of M0 in `binary` disappears under realistic cable/connector variation.

**Threshold τ (Normal | AD) on full-band M5.C3, `typical` noise**

- τ = −52.69 dB, 95% bootstrap CI −52.92 to −52.64. The CI resamples simulations within
  class, then views and draws.
- Screening prior P(Normal) = 0.8: τ = −52.76 dB.
- Class means: Normal −51.77 dB, AD −53.70 dB.
- CV (τ refit in every fold, fold τ from −52.71 to −52.47 dB): sensitivity 0.996,
  specificity 0.958.
- UNCERTAIN margin m = 0.23 dB = max(posterior margin 0.03, Φ⁻¹(0.7) × σ_ref 0.44). σ_ref is
  the within-simulation SD of one view, mostly the antenna-to-antenna asymmetry (the
  Normal histogram is bimodal).
- 2.3% of views fall inside the margin. Sensitivity and specificity on the accepted views
  are 1.00 / 1.00.

**τ depends on the instrument noise floor.** τ moves from −52.7 dB (`typical`, floor
−70 dB) to −51.9 (`noisy`, −60 dB) and −48.1 (`very_noisy`, −50 dB). Additive floor power
adds to a signal near −52 dB. At a −50 dB floor the classes collapse (CV 0.83). So the
threshold is valid only for the calibrated floor it was derived with, and the floor must
be ≤ −60 dB, i.e. at least 8 dB below the signal. Prompt 04/05 should add an explicit
floor-power subtraction and a gate check on the measured floor.

**Coverage vs accuracy** (M5.C3, LR + Platt, p* = 0.7):

| Profile | Reject rate | Balanced accuracy on accepted |
|---|---|---|
| typical | 1.4% | 0.980 |
| typical_jitter | 0.9% | 0.998 |
| very_noisy | 14.7% | 0.891 |

M0 at the same p* rejects 85% and reaches only 0.67 on what it accepts
(`03_coverage_accuracy.png`).

**3-class schemes (UNVERIFIED AGAINST MESH NOISE, no thresholds reported)**

- `three`: M9 1.000, M6 0.991 (ordinal), M5 0.965, COMB 0.940. M5.C3 alone gets 0.58: it
  separates Normal from AD but not Mild from Severe.
- `three_merged`: M9 0.998, M6 0.982, M5 0.947, COMB (ordinal) 0.888.
- Confusions concentrate on Mild. For COMB-ORD in `three`, 27/360 Mild views go to Normal and
  53/360 to Severe.
- These scores come from one simulation per stage. The classifier may be learning mesh or
  project differences (the steps crossing HFSS projects are the large ones, prompt 02), so
  they are not evidence of staging ability yet.

**Decision rule** (`results/03/decision_rule.md`, regenerated on every run):

1. INVALID if the gate fails (with the reason).
2. Otherwise, per antenna view with x = full-band opposite-antenna power in dB:
   - AD if x < τ − m;
   - Normal if x > τ + m;
   - otherwise UNCERTAIN.
   - τ = −52.69 dB, m = 0.23 dB at the `typical` floor.
3. The proposed combination of the six views (majority of non-UNCERTAIN views) is **not yet
   evaluated**; CV scored single views.

**What the current data can and cannot claim**

*Can claim:*

- In this phantom, the full-band opposite-antenna power separates Normal from AD with a
  simple, explicit threshold.
- This holds under realistic measurement noise, cable/connector variation, reference-plane
  phase and ±20 MHz resonance shifts, provided the noise floor is ≤ −60 dB.
- A per-antenna gate reliably blocks open, short and detuned measurements.

*Cannot claim:*

- **Generalisation to other heads.** There is one head geometry and one simulation per
  stage, so every accuracy above is repeatability under noise.
- **Any 3-class staging ability.** AD-vs-AD gaps are only 2–3× the port asymmetry, and the
  between-mesh noise is unmeasured.
- **That τ transfers to a real instrument or another phantom** without re-deriving it.
- **Reaching or beating Saied's 98.97% benchmark.** That result used 9 different heads.

## Prompt 02 — power-based metrics, frequency robustness, separability (code `7ca77f1`; report regenerated at `4962836`)

Details are in `results/02/report.md`, the tables in `results/02/*.csv`, and the figures in
`results/figures/02_*.png`. `metrics.csv` gained 1494 rows: 83 scalar metrics × 6 noise
profiles × 3 schemes, classifier `none-fisher`, 500 noisy realisations per simulation.

**Data handling changes**

- **Glitch masking is on** (`qc.mask_glitches`). 26 in-band (f, pair) points in 7 runs
  were replaced by linear interpolation, and each is logged in
  `results/qc/masked_points.csv`. Detection rule: |Sij − Sji| > −30 dB relative to the
  pair's band-RMS. Moderate has none.
- **Grid rule.** The grid is set to the coarsest step among the files, currently 5 MHz. Finer
  files are downsampled onto it; upsampling raises an error.

**Definitions used in the tables**

- J_meas: Fisher ratio under measurement noise. This is the ranking key the brief asked for.
- J_eff: Fisher ratio that also counts the port-to-port asymmetry as noise.
- gap/port: class gap divided by the port-to-port spread.
- gap/mesh: pending until the mesh-repeat runs arrive.

**Ranking at `typical` noise**

| Scheme | Best metric | J_meas | J_eff | gap/port | Weakest pair | Frequency-robust |
|---|---|---|---|---|---|---|
| binary | M5.C3[k3], opposite-antenna power in 3.35–3.60 GHz | 775 | 17.9 | 6.1 | Normal\|AD | **yes** (shift 0.03, keeps 94% of the class gap under band change) |
| binary | M5.C3, same, full band | 548 | 13.0 | 5.2 | Normal\|AD | shift yes (0.009); band value no (0.25–0.3) |
| binary | M0, old score | 45 | 16.9 | 7.3 | Normal\|AD | no (band change moves it 3–4× the gap; keeps 76% of the gap) |
| binary | M2.R, power-averaged reflection | 12 | 4.2 | 3.5 | Normal\|AD | no (keeps 36% of the gap under band change) |
| binary | M1, dB-averaged Sii | 0.27 | 0.02 | 0.19 | Normal\|AD | no |
| three_merged | M7.D3[k3], differential energy on opposite path | 165 | 4.2 | 2.9 | Mild+Mod\|Severe | no (shift 2.3) |
| three | M7.D3[k3] | 588 | 5.0 | 3.2 | Mild\|Severe | no (shift 2.3) |
| three | M6.A[3.40], accepted power in the 3.40–3.45 GHz sub-band | 133 | 4.1 | 2.9 | Mild\|Severe | no (shift 0.38) |

**Findings**

1. **Binary staging is robust.** M5.C3[k3] keeps J_eff ≥ 17 from `ideal` through `noisy`
   noise, and J_eff = 10 at `very_noisy`.
2. **No 3-class metric meets the brief's frequency-robust criterion.** All the 3-class winners
   move by more than 0.25 of the smallest class gap under a ±10 MHz resonance shift. Their
   weakest pair (AD vs AD) is only 2–3× the port noise and has not been checked against
   mesh noise.
3. **Ordinality is weak.** Only 31 of 83 metrics are monotone over Normal < Mild <
   Moderate < Severe.
   - Every metric has a large Normal → Mild step, 2–7× the port noise.
   - Mild → Moderate is within ±1.3× the port noise.
   - Moderate → Severe is 0.2–3.7×.
   - The two large steps are the ones that cross HFSS projects. The one same-project step is
     tiny. Physics can explain this, since CSF permittivity drops from 48.75 to 32.5 at
     Severe, but a mesh confound would produce the same pattern. The mesh-repeat runs are
     needed.
4. **M0 is in practice a reflection-only score.** Zeroing every Sij changes it by less than
   0.5%. It separates Normal from AD at a fixed band, but it depends heavily on the chosen
   band and on a single failed antenna (one open port moves it 8.6× the Normal–Mild gap),
   and it gives no usable AD-vs-AD separation (J_eff ≤ 0.7).

**Power vs dB averaging**

- Mean |Sii| in dB (M1) against power-averaged |Sii|² (M2): at `typical` noise, J is 46×
  higher with power averaging (binary), 5× (`three_merged`) and 13× (`three`). With
  frequency jitter the factor is 37–220×. A resonance shift moves the dB average 8× more.
  - Why: the dB average is dominated by the notch (−30 to −49 dB), which is
    mesh-sensitive.
- Mismatch loss, computed as the dB of the power average versus the band average of dB
  values: power is 17× better at `typical`.
- For the k=3 coupling the two are similar in binary (1.6×).

**The "which frequency?" answer**

- **The resonance itself carries no information.** The 3.60–3.65 GHz sub-band has
  J ≤ 0.07 in every scheme (`02_subbands.png`). The information sits in the 3.40–3.60 GHz
  shoulder and in opposite-antenna transmission.
- **Band-averaged power avoids picking a frequency.** Metrics that don't use Sii (M5) are
  unaffected when the notch is flattened.
- **Shifts.** Metrics that do not track the resonance survive ±10 MHz shifts: M5.C3 moves
  under 0.03 of the gap. Resonance-tracking metrics fail: M6.fc moves 0.9 of the Normal–Mild
  gap per 2 MHz.
- **Faults.** Open or short on all antennas pushes every metric out of the class range, or
  makes it undefined (mismatch loss), so the gate can catch it. **A single open antenna
  is the risk:** it shifts the C3 ring mean by 0.7–0.84 of the gap and stays inside the class
  range. The per-antenna reflection gate in prompt 03 must catch this.

**Caveats**

- The k3 window (3.35–3.60 GHz) was chosen by looking at these same four simulations, so it
  is optimistic. Full-band M5.C3 gives similar numbers (J_eff 13).
- In a symmetric ring, SVD features (M8.s_k) duplicate the modal features, and they have
  no per-antenna port-noise estimate.
- M3's accepted power ⟨A⟩ is an exact affine copy of M2.

## Prompt 01A — data loading and QC

Details: `MODEL_CARD.md` Part 2, `results/qc/qc_report.md`.

- **Parsing.** All 4 files parse as 6-port `GHz S MA R 50`. They are reciprocal to −76…−82 dB
  (median, relative to band-RMS) and passive (σ_max ≤ 0.982).
- **Common grid.** 3.2–4.2 GHz, 201 points at 5 MHz. The 2.8–3.2 GHz range is lost because
  Severe starts at 3.2 GHz.
- **Glitches.** Non-reciprocal frequency bumps on single antenna pairs look like sweep
  artefacts. They are now masked (see Prompt 02).
- **Port mapping.** The data support the card's port→antenna mapping: it ranks 1 of 60
  ring orderings in every file.
- **Symmetry noise floor.** Measured as |S| spread across equivalent pairs, max − min,
  median over frequency:
  - k=0: 0.13–0.32 dB
  - k=1: 0.6–1.1 dB
  - k=2: 1.1–1.6 dB
  - k=3: 0.4–1.0 dB
- **Confound.** Normal is the outlier, 1.4–5× the port noise, whether the comparison file
  comes from the same project or the other one. This is no evidence that the project
  effect dominates. The AD stages differ from each other by only 0.5–2× the port noise.
