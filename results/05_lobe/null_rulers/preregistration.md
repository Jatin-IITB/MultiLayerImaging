# Pre-registration (main session): null rulers when Null_rot31 and Null_rot43 arrive

This file was written and committed on 2026-10-04, before Null_rot31 and Null_rot43 exist. The evaluation code is
`scripts/18_null_rulers.py`, committed together with this file. When the files arrive, nothing new is written:
1. add their manifest rows;
2. run the script unchanged;
3. commit the output;
4. report.

Status: everything it produces is POST HOC with respect to Test_B and RightOnly. Frozen rules, thresholds, protocols
(d3a4bbf), predictions (cf56de8, 0f97bb2), submitted estimates (0f49389) and committed verdicts stay unchanged. No
re-solves.

## 1. Which nulls
- **Every ruler is the maximum over all nulls:** the 9 mirror-symmetric designs plus every rotated null in
  `data/sims_lobe.csv` (set `lobe_nulls`).
  - The 9: Healthy_sliced, Healthy_sliced_new, Mild_lobe, Mild_lobe_new, Moderate_lobe, Moderate_lobe_c3,
    Severe_lobe, Severe_lobe_c3, MCI_lobe_c3.
  - The rotated nulls: Null_rot07 and Null_rot19 now; Null_rot31 and Null_rot43 when they arrive.
- **No null is dropped, Null_rot19 included,** unless the user and the imaging sessions find and document a build
  defect in the HFSS model.
  - Even then, the dropped file is still reported.
  - Its exclusion must cite the written defect record.

## 2. Every ruler three ways
Only the first variant is the ruler; the other two show how much rests on one sample and are never adopted.

| variant | floors (mirror statistics, imaging LR, resonance and phase-pair nulls) | re-mesh yardstick (R31, R21, R32, front-back indices) | pattern fit (null contrast; healthy-twin ring mean) |
|---|---|---|---|
| **all nulls** | max over the 9 + all rotated nulls | max(one-pass yardstick, max over all rotated nulls \|Q(rot) − Q(Healthy_sliced_new)\|) | max(protocol value, rotated nulls' r0 / \|g\|) |
| **all nulls without rot19** | as above without Null_rot19 | as above without Null_rot19 | as above without Null_rot19 |
| **rot19 alone** | \|value(Null_rot19)\| | max(one-pass yardstick, \|Q(rot19) − Q(H6)\|) | r0(rot19); \|g(rot19)\| |

Fixed definitions:
- **Clean ruler of a mirror statistic:** max(floor, one-pass yardstick). The floor is leave-one-out when a null is
  the target.
- **Label margin:** A1 = |margin| / max(yardstick, boundary SD). The quadrature version adds the ±0.5 dB spread.
- **Pattern fit:** the protocol rule of d3a4bbf, w = 0.4: contrast ≥ 2x, residual ≤ 0.5 r0, a < 0.

## 3. Items re-evaluated, with their bars
All bars are the existing ones: ≥ 3x established / survives; 2–3x sensitive; < 2x not determined.

| # | item (MODEL_CARD 6.2 claim) | statistic | bar |
|---|---|---|---|
| 1 | Frozen labels, 30 lobe labels (claims 2, 3, 11) | A1 per label; count ≥ 3x; staging labels split into ≥ 3x / 2–3x / < 2x | ≥ 3x |
| 2 | Frozen labels of RightOnly and Test_B | A1 | ≥ 3x |
| 3 | Mask dependency (claim 6) | 0.319 dB / R31 yardstick | ≥ 2x |
| 4 | Lobe stage ordering on R21 (claim 10) | smallest lobe stage gap 0.489 dB / (2 × R21 yardstick) | ≥ 1 |
| 5 | Staging grades total retreat (claim 32) | R21 rise of LeftOnly, RightOnly, Test_B over Healthy_sliced_new / R21 yardstick | tiers |
| 6 | Mirror-twin R21 difference (claim 29) | 0.133 dB / R21 yardstick | > 1 = exceeds |
| 7 | Imaging mirror-test LR (claim 15; C6 P5) | \|T\| / clean ruler, 3 methods × 2 references, for LeftOnly, RightOnly, Test_B | tiers |
| 8 | Phase cross-ratio counts (claim 16; C6 P2; Test_B) | number ≥ 3x the clean ruler, band mean and 3.30–3.65 GHz | count |
| 9 | Resonance shift (claim 17) | LeftOnly left−right shift vs null max | beyond / not beyond |
| 10 | Reflection pairs (claims 18, 33) | T2 vs T6 and T3 vs T5 / clean ruler for LeftOnly, RightOnly, Test_B; Test_B reading "S2 left and S5 right" | both ≥ 3x with the stated signs |
| 11 | Neighbour phase pairs (claim 19) | LeftOnly T2-T3/T5-T6, T3-T4/T4-T5, T1-T2/T1-T6 at 3.30–3.65 GHz / null max | tiers |
| 12 | C6 P1 and P4 (claim 28; post hoc only, the verdict stands) | count within tolerance of 26; P4 within yardstick | count |
| 13 | Raised rulers (claim 35) | number of mirror rulers above the 9-null ruler, by family | count |
| 14 | Test_B front-back indices | / max(yardstick, √2 × floor) | tiers |
| 15 | Test_B mirror side | protocol vote rule | as protocol |
| 16 | Pattern fit (claim 34) | Test_B contrast, acceptance, sector confidences | protocol rule |
| 17 | Pattern fit on every rotated null as a target, leave-one-out rulers (claim 34) | pattern call | must be "none" |
| 18 | Path classes | per pair and class k = 1, 2, 3: common-mode or scattered (criterion in the script docstring) | descriptive |

Not evaluated: **uniform staging**. No rotated null exists for the uniform (unsectored) head, and the uniform v1/v2
solves are not a clean re-mesh pair (MODEL_CARD 6.8). So uniform staging is "not tested against re-meshing".
