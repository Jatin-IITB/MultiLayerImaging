# Round 4 (imaging session, POST-HOC): fit rejection, fair Born-vs-raw comparison, leave-one-out

Computed by `python imaging/lobe_round4.py` at code `00be60d`; numbers in `results/imaging/lobe_round4.json`. Everything here is post hoc. Frozen files, protocols, predictions and the committed scorers are unchanged.

## 1. What the fit-rejection rule separates

Fit statistic = relative whitened misfit ρ = ‖d − Jx̂‖ / ‖d‖ of the primary (Tikhonov dS) fit, the quantity in the Test_B protocol. Rejected if ρ > 1.5 × the largest ρ of the known cortical designs. Explained norm = √(‖d‖² − ‖d − Jx̂‖²), the sector-shaped part of the data. Every design against both references, sorted by ρ:

| reference | design | kind | rho | data_norm | abs_residual | explained_norm | limit | rejected |
|---|---|---|---|---|---|---|---|---|
| H6 | MCI_lobe_c3 | null | 0.944 | 3.9 | 3.7 | 1.3 | 0.824 | True |
| H6 | Null_rot19 | null | 0.940 | 8.2 | 7.7 | 2.8 | 0.824 | True |
| H6 | Null_rot07 | null | 0.889 | 4.3 | 3.8 | 2.0 | 0.824 | True |
| H6 | Healthy_sliced | null | 0.758 | 5.3 | 4.0 | 3.5 | 0.824 | False |
| H6 | RightOnly_test | replication | 0.549 | 19.2 | 10.6 | 16.1 | 0.824 | False |
| H6 | Test_B | blind test | 0.546 | 11.7 | 6.4 | 9.8 | 0.824 | False |
| H6 | Mild_lobe | stage | 0.527 | 23.6 | 12.5 | 20.1 | 0.824 | False |
| H6 | LeftOnly_test_c3 | blind test | 0.477 | 11.5 | 5.5 | 10.1 | 0.824 | False |
| H6 | Moderate_lobe_c3 | stage | 0.476 | 20.7 | 9.8 | 18.2 | 0.824 | False |
| H6 | Moderate_lobe | stage | 0.469 | 25.1 | 11.8 | 22.2 | 0.824 | False |
| H6 | Mild_lobe_new | stage | 0.463 | 17.4 | 8.1 | 15.4 | 0.824 | False |
| H6 | Severe_lobe_c3 | stage | 0.455 | 34.5 | 15.7 | 30.7 | 0.824 | False |
| H6 | Severe_lobe | stage | 0.454 | 37.5 | 17.1 | 33.4 | 0.824 | False |
| H7 | Null_rot19 | null | 0.920 | 11.1 | 10.2 | 4.3 | 0.867 | True |
| H7 | MCI_lobe_c3 | null | 0.794 | 6.6 | 5.2 | 4.0 | 0.867 | False |
| H7 | Null_rot07 | null | 0.794 | 7.1 | 5.6 | 4.3 | 0.867 | False |
| H7 | Healthy_sliced_new | null | 0.756 | 5.3 | 4.0 | 3.5 | 0.867 | False |
| H7 | RightOnly_test | replication | 0.578 | 23.6 | 13.7 | 19.3 | 0.867 | False |
| H7 | Mild_lobe | stage | 0.551 | 28.0 | 15.4 | 23.3 | 0.867 | False |
| H7 | Test_B | blind test | 0.513 | 14.9 | 7.6 | 12.8 | 0.867 | False |
| H7 | Moderate_lobe | stage | 0.487 | 28.8 | 14.0 | 25.1 | 0.867 | False |
| H7 | Mild_lobe_new | stage | 0.465 | 21.0 | 9.8 | 18.6 | 0.867 | False |
| H7 | Severe_lobe | stage | 0.463 | 40.3 | 18.6 | 35.7 | 0.867 | False |
| H7 | LeftOnly_test_c3 | blind test | 0.462 | 14.7 | 6.8 | 13.0 | 0.867 | False |
| H7 | Moderate_lobe_c3 | stage | 0.442 | 23.3 | 10.3 | 20.9 | 0.867 | False |
| H7 | Severe_lobe_c3 | stage | 0.437 | 36.5 | 16.0 | 32.9 | 0.867 | False |

| reference | limit | rho_rot19 | accepted_targets_above_rot19 | max_target_rho | min_null_rho | nulls_accepted | nulls_rejected | targets_rejected | null_abs_residual | target_abs_residual | null_explained | target_explained | rot19_data_norm | smallest_target_data_norm | spearman_rho_vs_data_norm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H7 | 0.867 | 0.920 | 0 | 0.578 | 0.756 | MCI_lobe_c3, Null_rot07, Healthy_sliced_new | Null_rot19 | none | 4.0–10.2 | 6.8–18.6 | 3.5–4.3 | 12.8–35.7 | 11.1 | 14.7 | -0.65 |
| H6 | 0.824 | 0.940 | 0 | 0.549 | 0.758 | Healthy_sliced | MCI_lobe_c3, Null_rot19, Null_rot07 | none | 3.7–7.7 | 5.5–17.1 | 1.3–3.5 | 9.8–33.4 | 8.2 | 11.5 | -0.86 |

**Answer.** Accepted real targets above rot19's ρ: 0 (H7 and H6 together). There can be none: rot19 sits above the rejection limit, so every accepted design sits below it. What the numbers show:
- **In this sample ρ separates nulls from targets completely, with a gap.** Targets have ρ ≤ H7 0.578, H6 0.549; nulls have ρ ≥ H7 0.756, H6 0.758. The committed limit (H7 0.867, H6 0.824) sits **above** the gap, so it rejects some nulls and accepts others. Accepted nulls: H7 MCI_lobe_c3, Null_rot07, Healthy_sliced_new; H6 Healthy_sliced. Rejected: H7 Null_rot19; H6 MCI_lobe_c3, Null_rot19, Null_rot07.
- **It is not the total data size.** rot19's data norm (H7 11.1, H6 8.2) is comparable to the smallest targets' (H7 14.7, H6 11.5). The absolute misfits overlap: nulls H7 4.0–10.2, H6 3.7–7.7, targets H7 6.8–18.6, H6 5.5–17.1, and rot19's exceeds LeftOnly's and Test_B's. ρ correlates with the data norm (Spearman H7 -0.65, H6 -0.86), but rot19 is the counterexample.
- **The separating quantity is the sector-shaped part of the data**: explained norm nulls H7 3.5–4.3, H6 1.3–3.5, targets H7 12.8–35.7, H6 9.8–33.4. A mesh-only difference is mostly not sector-shaped; a lobe change mostly is.
**What the rule separates:** data whose sector-shaped part is large relative to the remaining (mesh) structure from data whose sector-shaped part is not. So it does fire on mesh noise alone, as the objection says. It would equally reject a real change whose sector-shaped part were as small as a null's (explained norm about 3–4, roughly a third of LeftOnly's). For real targets it is a detection gate on sector-shaped signal against mesh structure, not a check that the sector model is right. 'Correctly flagged' (round 3) is withdrawn. A limit inside the observed gap would have rejected every null and accepted every target here, but choosing it now would be post hoc. **Verdict: CHANGED.**

## 2. Pass gap in ruler language

Re-stated in `lobe_round3.md` §9 and its final table (round-3 text revised). Ratio to the largest of n = 3 twin differences: the common-mode delay excess is 1.31×, and the affected-sector level 1.9–2.1× depending on method and reference. A value beyond all three twins has a rank p of 1/4. LR and phase share: **not separable from the pass gap**. Common-mode level: **undetermined**. Sector level: **undetermined**, at the 2× edge in some cases only. Round 3's 'not explained by the pass gap' is withdrawn.

## 3. Born vs raw delay, calibrated identically

**Before and after the mid-run redefinition** (round 3, largest-gap reading):

| version | hits | misses | false_alarms | exact | n |
|---|---|---|---|---|---|
| round-3 raw, first run: uncentred, gate = max over the nine 'symmetric' designs incl. stages (H7 15.75°, H6 14.19°) | 0 | 72 | 0 | 8 | 26 |
| round-3 raw, as reported: centred, gate = max over no-cortical-change designs (H7 0.74°, H6 0.89°) | 43 | 29 | 6 | 14 | 26 |
| round-3 Born (gate = frozen T_null 4.93) | 58 | 14 | 0 | 20 | 26 |

The first version was wrong: its 'null' set contained diseased stages, which set the gate at 14–16°. The second fixed that and also removed the common mode, while the results were visible. Below, both raw variants and the Born values are calibrated **the same way**. Thresholds are computed from the null rows only (Healthy_sliced, Healthy_sliced_new, MCI_lobe_c3, Null_rot07, Null_rot19, each against each reference, rotated nulls included) **before any hit is counted**. 'T_null_set' gives zero false alarms on the nulls by construction. 'T_recipe' = max(T_null_set, T_mild) adds the frozen recipe's Mild-tuned midpoint (Mild_lobe against Healthy_sliced; n/a where Mild's affected and healthy sectors overlap):

| statistic | T_null_set | T_mild | T_recipe |
|---|---|---|---|
| Born | 4.75 | 13.81 | 13.81 |
| raw uncentred | 2.95 | n/a | 2.95 |
| raw centred | 0.89 | n/a | 0.89 |

| statistic | calibration | rule | threshold | hits | misses | false_alarms | exact | n | false_alarms_on_nulls |
|---|---|---|---|---|---|---|---|---|---|
| Born | T_null_set | threshold | 4.75 | 72 | 0 | 25 | 15 | 26 | 0 |
| Born | T_null_set | gap | 4.75 | 58 | 14 | 0 | 20 | 26 | 0 |
| Born | T_recipe | threshold | 13.81 | 51 | 21 | 0 | 15 | 26 | 0 |
| Born | T_recipe | gap | 13.81 | 54 | 18 | 0 | 18 | 26 | 0 |
| raw uncentred | T_null_set | threshold | 2.95 | 72 | 0 | 29 | 13 | 26 | 0 |
| raw uncentred | T_null_set | gap | 2.95 | 50 | 22 | 6 | 14 | 26 | 0 |
| raw uncentred | T_recipe | threshold | 2.95 | 72 | 0 | 29 | 13 | 26 | 0 |
| raw uncentred | T_recipe | gap | 2.95 | 50 | 22 | 6 | 14 | 26 | 0 |
| raw centred | T_null_set | threshold | 0.89 | 22 | 50 | 0 | 14 | 26 | 0 |
| raw centred | T_null_set | gap | 0.89 | 39 | 33 | 5 | 14 | 26 | 0 |
| raw centred | T_recipe | threshold | 0.89 | 22 | 50 | 0 | 14 | 26 | 0 |
| raw centred | T_recipe | gap | 0.89 | 39 | 33 | 5 | 14 | 26 | 0 |

Side by side:

| calibration | rule | Born | raw_centred | raw_uncentred | exact_gap_vs_best_raw |
|---|---|---|---|---|---|
| T_null_set | threshold | 72 hits / 25 FA / 15 exact | 22 / 0 / 14 | 72 / 29 / 13 | 1 |
| T_null_set | gap | 58 hits / 0 FA / 20 exact | 39 / 5 / 14 | 50 / 6 / 14 | 6 |
| T_recipe | threshold | 51 hits / 0 FA / 15 exact | 22 / 0 / 14 | 72 / 29 / 13 | 1 |
| T_recipe | gap | 54 hits / 0 FA / 18 exact | 39 / 5 / 14 | 50 / 6 / 14 | 4 |

**Verdict: CHANGED.** Round 3's 'Born adds a calibrated level' compared a Born reading calibrated on frozen nulls with a raw reading calibrated differently. Under identical calibration, with threshold readings calibrated on the nulls only, the Born map adds nothing measurable (+1 exact set of 26); with the rank (largest-gap) reading it keeps +4…+6 exact sets and makes 0 false alarms against the raw delay's 5–6. With thresholds tuned out of sample on labelled designs (§4, leave-one-family-out), the Born threshold reaches 21/26 exact with 3 false alarms, the best raw rule 17/26 with 16. So the Born advantage depends on the calibration: absent under null-only thresholds, a few exact sets and many fewer false alarms otherwise. The raw delay has no Mild-tuned level at all: Mild's affected and healthy antennas overlap in raw delay against the 7-pass reference.

## 4. Rank rules scored out of sample

For each held-out design (or family), the free choices are selected on everything else **except Test_B**, which is never in any selection. The choices are the rule (largest gap or above-midpoint) and the gate on the top value (0 to 20 in steps of 0.25). Selection maximises exact sets, then fewer false alarms, then more hits; ties go to the first rule listed and the middle of the tied gate interval. The rule is then applied to the held-out rows (both references). Families: a stage's pass-5/pass-6 twins, both rotated nulls, and both healthy cross-references are each held out together. Threshold-only rules and the raw delay are scored the same way as comparators.

| held_out | statistic | kinds | hits | misses | false_alarms | exact | n | exact_without_TestB | false_without_TestB | TestB_read |
|---|---|---|---|---|---|---|---|---|---|---|
| design | Born | gap/mid | 58 | 14 | 0 | 20 | 26 | 18/24 | 0 | H7: S2 S5; H6: S2 S5 |
| design | Born | threshold | 68 | 4 | 3 | 20 | 26 | 19/24 | 3 | H7: S2 S5; H6: S2 |
| design | raw centred | gap/mid | 20 | 52 | 2 | 12 | 26 | 10/24 | 2 | H7: S2 S5; H6: S2 S5 |
| design | raw centred | threshold | 19 | 53 | 0 | 13 | 26 | 12/24 | 0 | H7: S2; H6: S2 S5 |
| design | raw uncentred | gap/mid | 42 | 30 | 6 | 10 | 26 | 8/24 | 6 | H7: S2 S5; H6: S2 S5 |
| design | raw uncentred | threshold | 60 | 12 | 16 | 15 | 26 | 14/24 | 16 | H7: S2 S5; H6: none |
| family | Born | gap/mid | 58 | 14 | 0 | 20 | 26 | 18/24 | 0 | H7: S2 S5; H6: S2 S5 |
| family | Born | threshold | 69 | 3 | 3 | 21 | 26 | 20/24 | 3 | H7: S2 S5; H6: S2 |
| family | raw centred | gap/mid | 13 | 59 | 2 | 12 | 26 | 10/24 | 2 | H7: S2 S5; H6: S2 S5 |
| family | raw centred | threshold | 19 | 53 | 0 | 13 | 26 | 12/24 | 0 | H7: S2; H6: S2 S5 |
| family | raw uncentred | gap/mid | 45 | 27 | 6 | 10 | 26 | 8/24 | 6 | H7: S2 S5; H6: S2 S5 |
| family | raw uncentred | threshold | 68 | 4 | 16 | 17 | 26 | 16/24 | 16 | H7: S2 S5; H6: none |

Rules chosen per held-out family, Born rank rules:

| held_out | rule | gate | train_exact | train_false |
|---|---|---|---|---|
| LeftOnly_test_c3 | mid | 9.25 | 18 | 0 |
| MCI_lobe_c3 | mid | 8.50 | 18 | 0 |
| Mild | mid | 8.50 | 16 | 0 |
| Moderate | mid | 8.50 | 16 | 0 |
| RightOnly_test | gap | 8.50 | 18 | 0 |
| Severe | mid | 8.50 | 20 | 0 |
| Test_B | mid | 8.50 | 20 | 0 |
| healthy cross-reference | mid | 8.50 | 18 | 0 |
| rotated nulls | mid | 8.00 | 16 | 0 |

**Result.** Born rank rule, leave-one-design-out: 58 hits, 0 false alarms, 20/26 exact (18/24 without Test_B). Leave-one-family-out: 58 / 0 / 20/26 (18/24 without Test_B). Test_B, never selected on, is read as H7: S2 S5; H6: S2 S5. LOO-calibrated Born threshold: 68 / 3 / 20/26. Best raw-delay rule, leave-one-family-out: raw uncentred threshold 68 / 16 / 17/26.
Caveat: there are 10 families, all from one head, mesh family and material table. 'Out of sample' here means out-of-design, not out-of-head.

## Final table

| item | verdict | change | evidence |
|---|---|---|---|
| 1 fit rejection | CHANGED | 'rot19 correctly rejected' → a gate on the sector-shaped part of the data vs mesh structure (explained norm: nulls 3.5–4.3, 1.3–3.5, targets 12.8–35.7, 9.8–33.4); fires on mesh noise alone; the limit sits above the null/target gap, so nulls are both accepted and rejected; it would reject a real change with a null-sized sector component | lobe_round4.json: fit |
| 2 pass gap | CHANGED | 'not explained' → undetermined (1.31× and 1.9–2.1× the largest of n = 3) | lobe_round3.md §9 |
| 3 Born vs raw (fair) | CHANGED | round-3 gap 20 vs 14 exact, 0 vs 6 FA → identical calibration: with threshold readings calibrated on the nulls only, the Born map adds nothing measurable (+1 exact set of 26); with the rank (largest-gap) reading it keeps +4…+6 exact sets and makes 0 false alarms against the raw delay's 5–6. With thresholds tuned out of sample on labelled designs (§4, leave-one-family-out), the Born threshold reaches 21/26 exact with 3 false alarms, the best raw rule 17/26 with 16. So the Born advantage depends on the calibration: absent under null-only thresholds, a few exact sets and many fewer false alarms otherwise | lobe_round4.json: fair |
| 4 rank rules out of sample | CHANGED (scored out of sample) | in-sample 58/0/20 → leave-one-design-out 58/0/20, leave-one-family-out 58/0/20; Test_B (never selected on): H7: S2 S5; H6: S2 S5 | lobe_round4.json: loo |

