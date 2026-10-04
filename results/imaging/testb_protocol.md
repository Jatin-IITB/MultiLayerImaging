# Blind protocol for Test_B (imaging session)

Committed **before Test_B is loaded**. Implementation: `imaging/score_testb.py`, committed in the code commit
immediately preceding this file. Neither file is edited after Test_B is loaded. Predictions and frozen files
(`lobe_predictions.md`, `lobe_frozen.json`, `round2_predictions.md`) are unchanged.

## 0. Blind handling

- Test_B is read only through `study_lobe.load_design("Test_B")`: its S-parameters, glitch-masked with the −30 dB
  rule, in antenna order T1..T6 (port map as for every lobe file).
- Nothing else about it is used: no header fields, file metadata, HFSS project, or other sessions' files.
- The material table, healthy anatomy and the other solved designs are used exactly as before.

## 1. What is reported (estimates only; the user holds the truth)

For each **reference** — H7 = Healthy_sliced (7 passes; the reference of the frozen pre-registration) and H6 =
Healthy_sliced_new (6 passes, stop rule 1, the same stop rule as Test_B):
- for each **method**, the sector map dε'' S1..S6 (and dεr), LR = mean(S2, S3) − mean(S5, S6), FB = S1 − S4;
- frozen calls R1 (sector affected if dε'' > T_abs), R2 (side) and R3 (front/back), with the thresholds in
  `lobe_frozen.json`.

Methods: the four frozen methods (tikhonov dS = **primary**, bounded dS, frozen log, frozen bounded log), plus the
**whitened log, labelled POST-HOC** (no frozen thresholds, no calls, not used by the reading).

Also reported:
- the reference-free LR_anti(X) = ½[LR(X) − LR(mirror X)], with its rank p against the nine mirror-symmetric
  solves;
- the whitened relative fit residual ρ;
- the data-level size (whitened dS norm against the largest one-pass mesh difference). This is context only, not
  a gate. Dry runs showed LeftOnly at only 1.25–1.59× it, so a data-level gate would reject real two-sector
  changes.

## 2. Rulers (R1c, fixed in round 2)

Clean ruler = max(one-pass yardstick, largest |value| over the null designs, none excluded). The one-pass
yardstick is the largest |change| from Healthy 7−6, Mild 6−5, Moderate 6−5 and Severe 6−5, each added to the
reference with both signs.

| quantity | null designs for the floor |
|---|---|
| LR (stage − ref) | the nine mirror-symmetric solves (minus the reference itself) |
| LR_anti (reference-free) | the nine mirror-symmetric solves |
| FB (stage − ref) | designs whose true S1 and S4 changes are equal: Healthy_sliced, Healthy_sliced_new, MCI_lobe_c3, Mild_lobe, Mild_lobe_new, Severe_lobe, Severe_lobe_c3 |
| each sector dε'' | designs with no cortical change: Healthy_sliced, Healthy_sliced_new, MCI_lobe_c3 |

Bar: ≥ 3× established, 2–3× sensitive, < 2× not separable. The measurement-level spread (Prompt 07 model,
±0.5 dB, 200 draws) is reported as context only.

## 3. Fit-rejection rule

For each reference and method, Test_B's fit is **rejected** if ρ > 1.5 × the largest ρ of the known cortical
designs. The known cortical designs are Mild_lobe, Moderate_lobe, Severe_lobe, Mild_lobe_new, Moderate_lobe_c3,
Severe_lobe_c3, LeftOnly_test_c3 and RightOnly_test, with the same reference and method. Rejected
reference/method combinations are reported but not used by the reading. If the primary method is rejected in
both references, no lobe reading is stated.

QC (points, band, passivity, reciprocity, mask log) is reported. If a masked point falls on a fit frequency
(3.4/3.6/3.8 GHz), that is flagged.

## 4. Reading rule (the stated estimate; primary method, accepted references only)

- **Affected** = dε'' > frozen T_abs (13.81) in **every** accepted reference.
- **Possible** = above T_abs in one accepted reference only.
- **Not affected** = otherwise.
- If no sector is above T_abs in any accepted reference: "no lobe read as affected".
- **Side** (from LR_anti against its R1c ruler, same sign in both references, smallest ratio decides): ≥ 3×
  "left/right (established)", 2–3× "left/right (tentative)", else none.
- **Front/back** (FB against its R1c ruler in every accepted reference, same sign, smallest ratio decides): ≥ 3×
  established, 2–3× tentative, else none.
- **Ranking** of the six sectors by mean dε'' over the accepted references. Round 1 found the ranking to be the
  robust part of the sector map.

Not estimated: the stage or severity, the hippocampus or core (not determined, §2 of the report), and dεr signs
(unreliable, §3).

**Behaviour of this rule on known designs** (dry runs before Test_B was loaded; truth in brackets):

| design | truth | reading |
|---|---|---|
| RightOnly_test | S5, S6 | affected S5, S6; side right (tentative) |
| Moderate_lobe | S1, S2, S3, S5, S6 | affected S1, S3, S5, S6; possible S2; front (tentative) |
| Mild_lobe_new | S2, S3, S5, S6 | affected S2; possible S3, S6 |
| LeftOnly_test_c3 | S2, S3 | possible S3 |
| MCI_lobe_c3 | none | nothing |

The rule is conservative. It made no wrong "affected" call on these designs, but it misses affected sectors
(sensitivity rather than specificity limited), and side and front/back reach at most "tentative".

## 5. Suggested scoring (the user decides; stated so that the protocol is complete)

- Primary: per sector, the "affected" set against the truth (e_k > 0 or changed materials), correct out of 6.
- Secondary: "affected ∪ possible" against the truth.
- Side and front/back are scored only when stated (established or tentative); an unstated side is
  "no call", not a hit.

## 6. Outputs

`results/imaging/testb_report.md`, `results/imaging/testb.json`, and section 11 of `lobe_report.md`. Nothing
else changes.
