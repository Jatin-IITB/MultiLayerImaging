# Presentation Q&A: how each result is computed

Written for the 5 Oct 2026 progress review. Each section answers a question that came up while preparing the
talk, with the numbers and the file they come from. Nothing here is a new analysis; it explains existing results.

---

## 1. The imaging forward model (imaging2)

**Question it answers:** if the head were in a given state, how would every antenna path change relative to the
healthy scan?

**Input: seven numbers.**
- The stage (Healthy, Mild, Moderate, Severe), which picks a literature tissue table (Shehab 2025, Table 5).
- For each of the six lobes: unaffected, or a cortex retreat eₖ = 0.5 … 22 mm.

**Step A, physics (not learned).** For each lobe, a straight column of tissue layers: skin 0.5, fat 1, skull 3 mm,
then CSF, gray and white matter with that lobe's retreat and the stage's tissue values. Its plane-wave reflection
coefficient is computed by the transmission-line recursion (normal incidence), and the healthy column's is
subtracted: ΔΓₖ(f), one complex number per lobe per frequency. An unaffected lobe has ΔΓ = 0. This part carries the
non-linear physics: a thicker CSF gap, lossy Severe CSF hiding deeper tissue, thin-layer resonances.

**Step B, learned mixing.**

    L_p(f) = Σ over lobes k of  C_rel(p,k)(f) · ΔΓ_k(f)        (real and imaginary part of ΔΓ each get a coefficient)

- C is complex: how strongly, and with what phase delay, lobe k's change shows up on path p.
- By the ring's symmetry (6 rotations × mirror) C depends only on how the path sits relative to the lobe. The
  21 paths × 6 lobes = 126 pairs reduce to **13 relations**:

| path | lobe relative to the path | kinds |
|---|---|---|
| reflection (antenna to itself) | under the antenna · 1 away · 2 away · opposite | 4 |
| neighbour (T1–T2) | at an end · just outside · far side | 3 |
| second-neighbour (T1–T3) | middle · end · just outside · opposite the middle | 4 |
| opposite (T1–T4) | at an end · one of the four side lobes | 2 |

- Learned: 13 relations × 2 = 26 complex coefficients per frequency (about 10,000 real numbers in all), by ridge
  regression on the HFSS lobe designs, noise-weighted, λ chosen by an inner leave-one-out. Each solved design counts
  12 times (its rotated and mirrored copies).
- **Leave-one-design-out:** the design being imaged (both meshes) is never in the training set.
- **Assumption:** the six lobes add up and do not interact. This is also what makes the sampler exact.

**Output:** predicted ln(S/S_healthy) for 21 paths × 201 frequencies (real part = amplitude change in Np,
imaginary part = phase change in rad).

**Worked example (blind design; only lobes 2 and 5 changed):**
path T2–T3 = C_end·ΔΓ₂ + C_far·ΔΓ₅; path T5–T6 = C_end·ΔΓ₅ + C_far·ΔΓ₂. The path over the larger change shifts more,
which is how the side is found.

**Why the learned part is small:** only 5–6 designs exist. Cost: Severe's materials are outside every training
design, so for Severe the coefficients are extrapolated (section 6).

Source: `results/imaging2/METHOD_surrogate_inversion.md`, `imaging2/surrogate.py`.

## 2. The inversion, step by step

1. **Data:** L = ln(S_measured ÷ S_healthy). Dividing by the healthy scan cancels what both scans share
   (antennas, cables, normal anatomy). 21 paths × 201 frequencies = 4,221 complex = 8,442 real numbers.
2. **Score a guess:** χ² = Σ (measured − predicted)² ÷ (expected error)². The expected error per path type and
   frequency = numerical noise (two meshes of the same design) + the forward model's own held-out error. A 0.5°
   miss on a strong neighbour path known to 0.1° adds 25; on a weak opposite path with 2° noise it adds 0.06.
3. **Correlated frequencies:** the noise drifts smoothly over about 15 neighbouring frequencies (75 MHz), so χ² is
   divided by ℓ ≈ 15: about 560 effective data (2 × 21 × 201 / 15).
4. **Belief:** ∝ e^(−χ²/2) × prior. Prior: each lobe 50% unaffected, otherwise any retreat 0.5–22 mm; each stage ¼.
   With ~560 independent checks, a χ² gap of 640 between two guesses is odds of e^−320; that is why P = 1.00 is
   common. It means "the data strongly prefer this under this model", not certainty about a real head.
5. **Search (Gibbs sampling):** 46⁶ ≈ 9.5 billion lobe combinations per stage is too many. Because the prediction
   is a sum over lobes, five lobes are held fixed, their contributions subtracted, and all 46 options of the sixth
   scored exactly; one option is drawn in proportion to its belief. Six such steps = one sweep; 600 sweeps, the
   first 150 discarded. Drawing at random (not always the best) is what measures uncertainty.
6. **Stage:** for each stage, the evidence = fit averaged over plausible lobe settings (Chib's method from the
   Gibbs runs). P(stage) = evidence × ¼, normalised.
7. **Fit check:** χ²/dof at the best guess. ≈ 1 is consistent with noise. Rule fixed before the blind test
   (`results/imaging2/BLIND_PROTOCOL.md`): 1.5–3.0 = poor fit, depth not trusted; > 3.0 = rejected. If > 1 the
   error bars are inflated by that factor and the run repeated (Birge rule).
   Values: Healthy 0.37, Mild 1.01, Moderate 0.31, left only 0.41, blind 0.46, Severe 2.59, shuffled paths 22.9.
8. **Report:** per lobe P(affected), median retreat and 90% interval; one stage with its probability
   (`results/imaging2/posteriors.json`, `results/imaging2/blind/Test_B/report.json`).
9. **Draw:** the estimated retreat on the healthy head (section 7).

Source: `imaging2/invert.py`, `results/imaging2/METHOD_surrogate_inversion.md`.

## 3. Why R31/R21 are not used to locate lobes

- They **were** used on the lobe heads: the rule frozen on the uniform heads was applied unchanged. Detection
  margins against the 0.204 dB re-meshing ruler: Moderate 3.2×, healthy 2.2–2.9×, Mild 2.3–2.5×, MCI 2.1×,
  Severe 0.9–1.1×, one-sided designs 0.5× (`results/LEDGER_main.md` D1–D6).
- They **cannot** locate: each is one number, a geometric mean over all six antennas. That average cancels each
  antenna's gain and also erases position. Two Mild lobes (19 mm in total) read Normal (`LEDGER_main.md` S4).
- Local versions fail (`LEDGER_main.md` L6; `results/05_lobe/reference_focal/`): half-ring R31 cannot be built
  (every opposite path crosses the midline); half-ring R21 and per-antenna R31 do not separate left-only from
  right-only; ±0.5 dB per-antenna gain error spreads per-antenna statistics by 0.44 dB.
- The side information is in the phase (neighbour-path phase −4.4° vs +4.6° for left-only vs right-only), which
  in turn needs per-antenna phase calibration (±10° per port spreads it by 8.6°).
- The ratio idea survives in the imaging as the gain-removing variant (exact lobe calls under drift 17% → 92%).

## 4. How Fisher ratio and KL are computed for one-number features

Code: `scripts/11_review2.py`, item A22 → `results/05_lobe/review2/A22_separability.csv`.

- Data: the 9 uniform solves (v2 Healthy, MCI, Mild, Moderate, Severe; v1 Healthy, Mild, Moderate, Severe); MCI
  left out of Normal vs AD.
- Each class gets a spread from three terms:
  1. measurement noise: 120 synthetic noisy copies per solve (per S entry 0.25 dB, 2°, −70 dB floor; per antenna
     1.5%, 10°, 1 MHz), the feature computed on each copy;
  2. solve-to-solve: mean(d²/2) over the 4 v1/v2 pairs;
  3. AD only: the spread of the three stage means.
- Worked for R31: μ_H = −14.58 dB, μ_AD = −16.11 dB, Δμ = 1.53 dB; σ²_H = 0.030² + 0.146² = 0.022;
  σ²_AD = 0.022 + 0.199² = 0.062.
  - Fisher F = Δμ² / (σ²_H + σ²_AD) = 27.8 (95% bootstrap 18.0–54.7)
  - Bhattacharyya B = F/4 + ½ ln(mean variance / geometric-mean variance) = 7.0
  - symmetric KL = ½(σ²_H/σ²_AD + σ²_AD/σ²_H − 2) + ½Δμ²(1/σ²_H + 1/σ²_AD) = 72
- Caveats: the noise model was chosen, not measured; healthy has 2 solves; v1/v2 differ in sweep settings, not true
  re-meshes; all three scores assume Gaussian classes and use the same three numbers. R31 was frozen on 28 Sep;
  this chart (4 Oct) is a later check, and R32 scores slightly higher (34 vs 28).

## 5. The 0.437 on the absorbed-power slide

0.437 = |Sᵢᵢ|² of the v2 healthy uniform head, averaged over the 201 frequencies (3.2–4.2 GHz) and the six
antennas (each antenna 0.436–0.438): on average 43.7% of the power fed to an antenna comes straight back.
The average hides a large swing: 0.75 at 3.2 GHz, 0.0003 (−35 dB) at the 3.64 GHz resonance, 0.90 at 4.2 GHz.
Power reaching the other five antennas: 4.1 × 10⁻⁴. Not returned: 1 − 0.437 − 0.0004 = 0.563 = −2.499 dB
(dB of the band-averaged power). Severe: 0.425. A ±0.5 dB error on Sᵢᵢ moves |Sᵢᵢ|² by 0.437 × (10^0.05 − 1) ≈ 0.05,
about 900× the whole Normal-to-Severe transmission change (6 × 10⁻⁵).

## 6. Severe depth

From `results/imaging2/scores_designs.csv` and `posteriors.json`: stage and all six lobes right in both solves;
average depth error 13.5 mm (5-pass) and 11.75 mm (6-pass); truth inside the 90% interval for 3–4 of 6 lobes;
fit 2.59 / 2.12 ("poor fit, depth not trusted"). Reasons:
- Severe CSF (εr 32.5, σ 6.4 S/m) absorbs about 17 dB/cm (field down to 37% in 5 mm), twice healthy CSF; once the
  CSF gap is thicker than about 5 mm, deeper cortex is out of sight.
- No Severe design is in the training set when Severe is imaged: its coefficients are extrapolated.
- In three lobes the 90% interval reaches 19–21 mm (depth undetermined); frontal and left temporal are confidently
  wrong (1–2 mm against 15.5–17.5).
The earlier conductivity maps hid this: the stage's tissue values coloured every affected lobe regardless of depth
(map correlation with the truth only 0.09–0.17).

## 7. The slice pictures: what is estimated and what is drawn

- Estimated: per lobe, whether it changed and how far; one stage. Tissue εr and σ are **not** estimated.
- Drawn: the healthy head model (spheres, six full-height 60° wedges) with the estimated retreat turned into CSF.
  Every slice repeats the same seven numbers; the antennas all sit at z ≈ 48 mm, so height is never measured.
- 56–69% of the in-brain sensitivity is above z = 40 mm and at most 4% below z = 0: slices at z ≤ 20 mm are model
  extrapolation (hatched). The hippocampus is not estimated and stays healthy in the estimate.
- Figures and script: `results/presentation/` (`overlay_figures.py`), drawn at the posterior medians.

## 8. Raw-phase ring

Per antenna: −½ [mean over 3.30–3.65 GHz of phase(S_k,k+1 / S_healthy) + same for k−1], in degrees, against
Healthy_sliced_new. Independent recomputation: `results/checks/ring_phase_check.py` (reproduces the slide exactly).
- Worked (left-only): T2–T3 −7.9°, T2–T1 −4.9° → T2 = 6.4°; T5–T4 −2.0°, T5–T6 −2.3° → T5 = 2.1°. A path reports
  the lobes at its two ends (0, 1, 2 affected ends → 2.1°, 4.9°, 7.9°). 6.4° at 3.5 GHz = 5 ps.
- Beyond the healthy re-meshes (up to 1.7° around the ring, 1.2° left−right): left-only +4.4° and right-only −4.6°
  left−right, Moderate frontal−occipital +4.3°. Not beyond them: Mild (1.9°), blind test (2.1°), Severe (0.9°);
  MCI 0.4° is at the healthy level. The pre-registered statistics are more conservative (`LEDGER_main.md` L3, L4, L8).
- The window was chosen after looking at left-only; over 3.2–4.2 GHz the sign holds (+3.3° / −2.8°). Why the change
  is a delay is not explained (Severe CSF has lower εr than gray matter yet gives the largest delay).

## 9. Where the opposite-antenna signal goes (E-field exports)

From `results/imaging/report.md` §1, §4.3 and `results/efield/efield_numbers.py` (healthy uniform head, 3.6 GHz):
- T1 and T4 are 121° apart seen from the centre (both 48 mm above it). Straight line: 170 mm, 135 mm of it brain,
  ≈ 63 dB of tissue absorption; over the top just outside the skin: 192 mm, no absorption.
- Half-way, T1's field is −33 dB over the top vs −57 dB on the straight line (relative to just in front of T1, ±3 dB).
- Group delay: measured 3.11 ns; predicted 2.97 ns around the head, 5.31 ns straight through.
- Sensitivity |E₁·E₄|: 0.31% in the brain, 99% in air; 73% of the in-brain part within 13.5 mm of the surface.
- Tissue loss at 3.6 GHz: gray 5.7, white 4.5, CSF 8.6 dB/cm (quick rule 16.4·σ/√εr dB/cm).

## 10. Words that get mixed up

| term | meaning here |
|---|---|
| sensitivity (fields) | how much a small tissue change at a point would change one antenna pair's signal, \|E_a·E_b\| |
| specificity | classifier term: share of healthy heads labelled healthy |
| Fisher ratio | (Δμ)² / (σ₁² + σ₂²), one-feature separability |
| Fisher information | curvature of the likelihood; Cramér–Rao bounds in the imaging part |
| Born | first-order: the healthy head's fields used for the change; misses 56–67% of it here |
| re-mesh null / ruler | the healthy head solved on another mesh; the largest change it shows is the yardstick |
| P = 1.00 | the data strongly prefer it under this model; not certainty about a real head |
| inverse crime | testing on data from the same simulator family the method was trained on |
