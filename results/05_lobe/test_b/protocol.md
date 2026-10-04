# Test_B blind protocol (main session), committed before Test_B is loaded

**Code.** `scripts/15_test_b.py` at **89af4b3**.
- Validation run: `python scripts/15_test_b.py --validate` at 89af4b3. The report header reads 89af4b3-dirty; the
  only dirty file is an uncommitted `.gitattributes` line (`*.pbs eol`) that is not ours.
- Blind run: `python scripts/15_test_b.py --blind`. It refuses to start unless this file is committed unchanged.

**Blind rules followed.**
- Test_B's geometry is learned from its S-parameters only. The parser reads the option line and the data lines; the
  header comments are never read or printed.
- Not used: the HFSS project, file metadata, and other sessions' files about Test_B. Commit subjects of the imaging
  sessions are visible in `git log` and say they committed their own Test_B protocols and estimates; none of their
  files was opened.
- Allowed and used: the material table, the healthy anatomy, and all other solved designs.
- Predictions, frozen rules and earlier protocols are unchanged.

## 1. What is reported for Test_B
1. **Frozen rule** (`results/04/frozen_rule.json`, 5192287, unchanged).
   - Labels, from the clean file: detection (R31 vs τ ± m), three-stage (R21) and merged staging (R32).
   - For each label:
     - the signed margin to the label edge (dB);
     - that margin over the A1 ruler, max(one-pass yardstick, boundary bootstrap SD), and with the ±0.5 dB
       measurement spread in quadrature;
     - a verdict: ≥ 3x determined, 2–3x sensitive, < 2x not determined;
     - label fractions of 300 noisy draws (typical profile + setup perturbation + ±0.5 dB per-port gain).
2. **Power-based indices.**
   - Left-right, reference-free: the power LR indices (all / neighbour / second-neighbour paths) and the reflection
     mirror pairs (T2 vs T6, T3 vs T5), against the R1c clean ruler.
   - Front-back power index (all / neighbour paths), Test_B minus Healthy_sliced_new (Healthy_sliced as a check),
     against max(one-pass yardstick, √2 × symmetry floor).
3. **[POST HOC] phase cross-ratio counts.** The number of left-right phase cross-ratios ≥ 3x the R1c clean ruler,
   at band mean and at 3.30–3.65 GHz, with signs.
   - Status: post hoc.
   - C6 on RightOnly: the signs replicated 26/26, the sizes did not (12/26 within tolerance), so the C6 verdict
     was NOT REPLICATED.
4. **Localisation:** side, plus a call per sector S1..S6 (affected / not affected / uncertain) with a confidence
   number. Defined in §2.
5. **Extent:** the ring-mean neighbour phase change g, and the most similar known designs (rms over y).

## 2. Decision rules (exactly as coded)

**(a) Sector-pattern fit** (reference-based; primary for sectors and side).
- **Statistic.** y_k = mean phase change (deg, 3.2–3.5 GHz) of the two neighbour paths at antenna Tk, Test_B against
  Healthy_sliced_new. The 3.2–3.5 GHz sub-band is the pre-defined A16 sub-band, chosen on the known designs.
- **Model.** y = c + a·K(w)·x, where:
  - x ∈ {0, 1}⁶ marks the affected sectors (not all equal);
  - K(w) is circulant (w, 1, w), because antenna k's two neighbour paths also see sectors k−1 and k+1;
  - c is free;
  - a < 0, because disease delays the neighbour paths (C4).
- **Fitting.** All 62 patterns are fitted by least squares; the smallest rms residual wins.
- **w = 0.4.** Chosen on the known designs from the grid 0.2 / 0.3 / 0.4 / 0.5, maximising first the exact patterns,
  then the correct sectors, then a small residual.
- **Fit-rejection rule.** The pattern is accepted only if all three hold:
  1. contrast r0 = rms(y − mean y) is ≥ 2x the null contrast. The null contrast is 0.212°: the largest r0 among
     Healthy_sliced vs Healthy_sliced_new, MCI_lobe_c3, Severe_lobe and Severe_lobe_c3.
  2. best residual ≤ 0.5·r0;
  3. a < 0.
- **Sector confidence.** (residual with that sector flipped − best residual) / null contrast.
  - ≥ 2 gives the sector's call (affected / not affected); ≥ 3 is established.
  - < 2 gives "uncertain".
  - 99 means no physical fit (a < 0) exists with that sector flipped.
- **If the fit is rejected,** there is no sector pattern. Then:
  - if |g| ≥ 2x the healthy-twin |g| (1.111°), all six sectors are "affected" (diffuse);
  - otherwise no sector is affected.

**(b) Mirror test** (reference-free; confirms the side).
- Uses the 26 statistics that were informative for LeftOnly in the C6 table (0f97bb2).
- Votes are the statistics with |T| ≥ 2x their R1c clean ruler. A vote is "left" if its sign equals LeftOnly's.
- Outcome:
  - left / right if there are ≥ 3 votes and ≥ 80% agree;
  - mixed if there are ≥ 3 votes and they do not agree that strongly;
  - none if there are fewer than 3 votes.

**(c) Final side.** The fit side is left if more of S2/S3 than of S5/S6 are in the pattern, right if the reverse,
otherwise symmetric.

| fit side | mirror side | final side | confidence |
|---|---|---|---|
| left / right | same | that side | established if ≥ 3 mirror statistics are ≥ 3x, else sensitive |
| left / right | none or mixed | the fit side | sensitive (reference-based fit only) |
| left / right | the opposite side | undetermined | — |
| symmetric | left / right | the mirror side | sensitive (mirror test only) |
| symmetric | mixed | undetermined | — |
| symmetric | none | no left-right asymmetry | — |

**(d) Not assessable.** Hippocampus/core changes: MCI_lobe gave 0 of 228 features beyond the rulers. No core call is
made.

**References.**
- Healthy_sliced_new (stop rule 1, 6 passes, matched to Test_B's stop rule 1) is used for every reference-based number.
- Healthy_sliced (7 passes) is reported as a secondary check and never used for a call.
- Reference-free statistics need no reference.

**QC** (reported, never used to drop the file): number of points and band, max singular value², worst relative
reciprocity, and glitch-masked points under the frozen −30 dB rule.

## 3. How to score these estimates against the truth
- **Detection.** The label is correct if it is AD and Test_B contains any disease change, or Normal if it contains
  none. The margin tier is my confidence.
- **Staging.** Score only if Test_B uses one stage's materials:
  - three-stage: Normal / Mild / Severe;
  - merged: Normal / Mild+Moderate / Severe;
  - UNCERTAIN counts as an abstention.
- **Side.** True side = sign of (e_S2 + e_S3) − (e_S5 + e_S6); zero means no left-right asymmetry. My call is left,
  right, no left-right asymmetry, or undetermined (= abstention).
- **Sectors.** Sector k is truly affected if e_Sk > 0 or Sk carries diseased GM/WM material.
  - Count hits, misses, false alarms, correct rejections, and uncertain (= abstentions).
  - The pattern is exact only if it has no uncertain and no errors.
- **Confidence calibration.** Check whether errors fall on calls marked established (≥ 3) or only on sensitive and
  uncertain ones.

## 4. Validation on the known designs (Test_B not opened; `validation.md`, `validation_*.csv`)

| mode | designs | exact | hits | false alarms | misses | correct rejections | uncertain | side correct |
|---|---|---|---|---|---|---|---|---|
| in-sample (w on all designs) | 10 | 7 | 26 | 0 | 0 | 24 | 10 | 10 |
| leave design group out | 10 | 7 | 24 | 0 | 2 | 24 | 10 | 10 |

Pattern calls:
- **Exact patterns:** LeftOnly → 23, RightOnly → 56, Moderate_lobe_c3 → 12356.
- **Uniform designs (handled by the rejection rule):** healthy twin → none, MCI → none, Severe ×2 → all six, diffuse.
- **Right pattern, some sectors uncertain:** Mild ×2 → 2356; Moderate_lobe → 12356, with S3 uncertain.
- **Leaving the Moderate pair out:** w becomes 0.5 and Moderate_lobe is called 26 (two misses).

## 5. Known limits (stated before seeing Test_B)
- **Mild-level bilateral patterns** have low contrast (2.6–3.1x null), so most of their sectors come out uncertain.
- **Graded involvement.** The binary model cannot represent graded involvement. A sector called "not affected" may be
  less affected, not untouched. Deep atrophy can read as less change than shallow atrophy (Moderate: S3/S5 at
  15.5 mm show less neighbour delay than S1/S2/S6).
- **Alternating patterns** (S1, S3, S5 vs S2, S4, S6) are nearly indistinguishable from uniform involvement at w ≈ 0.5.
- **Calibration.** The phase statistics are simulation-only. Per-port phase errors in a real measurement would enter
  y directly.
- **Generality.** One solve per design and one head. This is a within-simulation estimate, not a generalisation claim.
