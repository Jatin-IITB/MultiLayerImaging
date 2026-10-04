# imaging2 ledger

**Scope.** Every claim is about one idealised simulated head, a single lobe-phantom family solved in HFSS. These are
noise- and mesh-robustness results within that family, not generalisation to people.

**Tiers.** A tier is the ratio to the R1c ruler over all 13 nulls: the 9 mirror-symmetric designs plus rot07, rot19,
rot31 and rot43.
- **established** ≥ 3×; **sensitive** 2–3×; **not determined** < 2×.
- **"count"** marks a claim whose null floor is exactly zero (no null ever produces the event). There the ratio is not
  defined, and the tier rests on the count of null runs.
- **"n/a"** marks a performance number that has no null ruler.

**Commits.** The evidence for the 13-null rulers is in `2f7f482` (pre-registered code `a295006`, run unchanged).

## 1. Claims still standing
| id | claim | tier | ratio (13 nulls) | ratio without rot19 | origin | evidence | commit | depends on |
|---|---|---|---|---|---|---|---|---|
| C1 | At least one lobe is called in every diseased design and in no healthy, MCI or rotated-null head, against all six healthy reference meshes and in all three inversion variants (162 of 162 diseased runs, 0 of 93 healthy runs). | established (count) | n/a: floor 0 (0 of 93 null runs) | n/a: floor 0 | post hoc wording; R1 and R12 pre-registered at a295006 | results/imaging2/nullrulers/report.json (stage_table) | 2f7f482 | lobe-phantom family; wedge + one-stage model; amplitude and phase; any of six references |
| C2 | Held out of training and measured against the matching healthy mesh, the reconstruction names exactly the affected lobes for every lobe design, except one small extra frontal lobe on one Mild mesh (65 of 66 lobe calls). | established (count) | n/a: no null calls a lobe | n/a | analysis plan (leave-one-design-out), not pre-registered | results/imaging2/scores_sectors.csv; rightonly/rightonly.md; blind/Test_B/report.md | 6db98f6, 5a24a0f, c0fafd6 | matched reference H6/H7; standard variant; model family |
| C3 | Under the protocol committed before the file existed, the blind design was reconstructed with exactly the right lobes (left temporal, right parietal), the right stage (Mild), and both true depths inside their 90% intervals. | pre-registered hit (one design) | n/a | n/a | pre-registered (595e9cb) | results/imaging2/blind/Test_B/score.md | f88236c | reference H6; standard variant; one design |
| C4 | Disease on one side gives lobe calls on that side only, and none of the 13 nulls ever gives a one-sided pattern. | established (count) | n/a: floor 0 (0 of 13 nulls one-sided) | n/a: floor 0 | rotated nulls pre-registered (R2, a295006); old nulls post hoc | results/imaging2/nullrulers/report.md §4; rightonly/rightonly.md | 2f7f482, 5a24a0f | standard and ring-phase variants (gain-removing calls both sides on RightOnly); reference H6 |
| C5 | In the raw data, without any model, the phase delay on the affected side exceeds the other side by 4.4–4.6°. | established | 3.80 (LeftOnly) / 3.94 (RightOnly); floor rot31 1.17° | 3.80 / 3.94 | pre-registered (R4, a295006); the 3.30–3.65 GHz window is post hoc | results/imaging2/nullrulers/report.md §3 | 2f7f482 | phase only; reference H6; post-hoc band |
| C6 | In the raw data, with the frontal lobe affected and the occipital not, the frontal antenna's phase delay exceeds the occipital's by 4.1–4.2°. | established (barely) | 3.21 / 3.12; floor rot07 1.32° | 3.21 / 3.12 | pre-registered (R5, a295006); window post hoc | results/imaging2/nullrulers/report.md §3 | 2f7f482 | phase only; references H6/H7; post-hoc band |
| C7 | In the raw data of the blind design, its two diagonal antennas show 1.57° more phase delay than the other four. | established, post hoc statistic | 3.64; floor rot43 0.43° | 3.64 | post hoc (statistic defined after seeing Test_B) | results/imaging2/nullrulers/report.md §3 | 2f7f482 | phase only; reference H6; post-hoc statistic and band |
| C8 | The disease stage is named correctly for every diseased design against four of the six healthy meshes (H6, H7, rot07, rot31), but wrongly for 5–6 of 9 designs against rot19 or rot43. | not determined (reference-dependent) | n/a | n/a: rot43 alone still breaks it | R10 pre-registered (a295006); summary post hoc | results/imaging2/nullrulers/report.json | 2f7f482 | the healthy reference mesh; standard variant |
| C9 | With every diseased design held out, Mild and Moderate cortex retreat is estimated with a mean error of 1.4–3.0 mm against the matching healthy mesh; Severe retreat is not recovered. | not determined | ≈ 1.2–2.4: the retreat changes by up to 6.5 mm between two meshes of one design, against 7.5–15.5 mm true | same | analysis plan (leave-one-design-out) | results/imaging2/scores_designs.csv; posthoc/posthoc.md §C | 6db98f6, b8eb7fa | matched reference; model family; point estimates only (intervals fail, W1) |
| C10 | With no Mild-material design in training at all, the left-only design is still named exactly (left temporal and left parietal only). | established (count) | n/a | n/a | post hoc stress test (before the blind round) | results/imaging2/posteriors_loso.json | ed7f2e3 | reference H6; standard variant |
| C11 | With realistic instrument noise and ±0.5 dB / ±5° antenna drift between scans, the gain-removing inversion names exactly the right lobes in 90% of draws, against 47% (standard), 44% (ring-phase) and 84% (gain + ring). | n/a (performance; 96 draws per variant) | n/a | n/a | post hoc | results/imaging2/posthoc/variants_drift.md | 52c8149 | noise and drift model (chosen, not measured); reference H6 |
| C12 | Across all six healthy references in clean simulation, the standard inversion makes the fewest wrong lobe calls (11 in 85 runs), then ring-phase (15), gain-removing (34) and gain + ring (39). | n/a (performance) | n/a | n/a | post hoc (counts; pre-registered table R12) | results/imaging2/nullrulers/report.md §2; posthoc/xref_gainring.json | 2f7f482 | the six healthy meshes as references; no instrument noise |

## 2. Failed or withdrawn
- **W1.** "Depth intervals are reportable (78% coverage accepted with the warning)." Killed: with all 13 nulls in the
  noise model, coverage on affected lobes is 67% < 70% (pre-registered R11). 8 of the 12 misses are Severe.
  `2f7f482`.
- **W2.** "The stage does not depend on the healthy reference." Killed by rot19 (8 of 14 standard runs wrong) and
  rot43 (8 of 14). `d939eec`, `2f7f482`.
- **W3.** "Test_B's model-free ring spread is beyond the nulls (5.1×)." Killed by the rotated nulls: 1.49× and then
  1.25× (floor rot31). `b8eb7fa`, `2f7f482`.
- **W4.** "Severe retreat is recovered." Killed by leave-one-design-out: ê 1–12 mm against 11.5–18 mm; fit χ²/dof
  2.1–2.6. `6db98f6`.
- **W5.** "The right-only replication reproduces LeftOnly's depth." Killed: ê 3.0 / 3.5 mm against 11.5 / 7.5 mm, and
  the intervals exclude the truth. `5a24a0f`.
- **W6.** "The 5-vs-6-pass gap fully explains RightOnly's offset." Killed: 1.05–1.39× the largest of three 5-vs-6
  twins on 12 of 16 statistics. `b8eb7fa`.
- **W7.** "The estimated left − right retreat (LR_e) separates the sides." Never established: 1.24× a floor of 9.25 mm
  set by Severe_p6. `5a24a0f`, `2f7f482`.
- **W8.** "Two healthy repeats differ by 1.3–1.6°, uniformly" (detuning-figure ruler). Killed by the rotated nulls,
  whose ring spread reaches 1.69°. `b8eb7fa`, `2f7f482`.
- **W9.** "P(affected) = 1.00 is a calibrated probability." Killed: on RightOnly the gain-removing variant put
  P = 1.00 on the wrong lobe S2. `b8eb7fa`.
- **W10.** "Use the gain-removing inversion by default, unconditionally." Revised: it has the most wrong lobes across
  references (34 in 85 runs). It is now recommended only when drift is not calibrated out. `52c8149`, `2f7f482`.
- **W11.** "The secondary variants' depth intervals on Test_B cover the truth." Killed: each misses one (scored).
  `f88236c`.
- **W12.** "A linear depth-moment surrogate is good enough." Rejected: held-out Severe misfit 94, against 15 with
  layered-stack features. `6db98f6`.
- **W13.** "The uniform v2 designs can train the surrogate." Rejected: their own mesh noise (2.3 dB, 15–40°) exceeds
  the lobe signal. `6db98f6`.
- **W14.** "Mild_p5's lobe pattern is exact." Killed: one extra frontal lobe at ê ≈ 1 mm (disappears with the
  mean-of-six reference, post hoc). `6db98f6`, `2f7f482`.

## 3. Open limitations (CANNOT TELL / UNVERIFIED)
- **L1.** Variation between heads (size, skull and scalp thickness, antenna stand-off): untested. CANNOT TELL.
- **L2.** Is rot19's (and rot43's) class-wide shift a build difference or real mesh noise? CANNOT TELL until the HFSS
  model is checked.
- **L3.** Is H6 typical? It has the lowest R31 of the six healthy meshes (−0.12 dB, z −1.9) and is central in R21, R32
  and phase. CANNOT TELL with six meshes.
- **L4.** The vertical extent of the lobes is imposed by the model. Nothing below z ≈ 30 mm is measured. UNVERIFIED.
- **L5.** Hippocampus / MCI changes are not estimable by this array.
- **L6.** Skin, fat and skull materials are assumed values (OPEN-GUI). UNVERIFIED.
- **L7.** There are no field exports of a diseased head, so a field-based (distorted-Born / DBIM) correction is
  untested.
- **L8.** The mirrored-mesh contribution to the RightOnly difference is untested.
- **L9.** The drift level below which ring-phase beats gain-removing is untested.
- **L10.** The 3.30–3.65 GHz window of every model-free reading was chosen post hoc.
- **L11.** The surrogate is trained on 5–6 designs of one family; Severe materials are extrapolation.
- **L12.** P(affected) is not calibrated. P = 1.00 means the data strongly prefer the lobe under this model.
- **L13.** Whether instrument noise removes gain-removing's clean cross-reference errors is untested on references
  other than H6.

## 4. Numbers for the report
| # | number | source | commit |
|---|---|---|---|
| N1 | Blind Test_B (pre-registered): lobes S2 + S5 exact, stage Mild, ê 13.0 [7.0–21.5] mm vs 11.5 and 7.0 [6.5–12.5] mm vs 7.5, fit χ²/dof 0.46; protocol verdict PASS | results/imaging2/blind/Test_B/score.md | f88236c |
| N2 | Lobe calls against the matching healthy mesh: 65 of 66 correct (9 held-out designs + RightOnly + Test_B) | results/imaging2/scores_sectors.csv; rightonly/rightonly.md; blind/Test_B/report.md | 6db98f6, 5a24a0f, c0fafd6 |
| N3 | Detection by lobes: 162 of 162 diseased runs call ≥ 1 lobe; 0 of 93 healthy, MCI or null runs call any | results/imaging2/nullrulers/report.json | 2f7f482 |
| N4 | Four rotated healthy heads as targets: 0 lobes called in every one of their 60 runs | results/imaging2/nullrulers/report.md §4 | 2f7f482 |
| N5 | Model-free side contrast +4.44° (LeftOnly) / −4.60° (RightOnly) against a 13-null floor of 1.17°: 3.80× / 3.94× | results/imaging2/nullrulers/report.md §3 | 2f7f482 |
| N6 | Wrong stages per healthy reference (standard, of 14–15 runs): H6 0, H7 1, rot07 0, rot31 0, rot19 8, rot43 8 | results/imaging2/nullrulers/report.md §2 | 2f7f482 |
| N7 | Coverage of the 90% depth intervals on affected lobes: 67% with all 13 nulls, 78% without rot19, 83% without Severe | results/imaging2/nullrulers/report.md §5; posthoc3/coverage_detail.json | 2f7f482 |
| N8 | Drift test, exact lobe patterns: gain-removing 90%, gain + ring 84%, standard 47%, ring-phase 44% | results/imaging2/posthoc/variants_drift.md | 52c8149 |
| N9 | Wrong lobe calls across six references (85 runs each): standard 11, ring-phase 15, gain-removing 34, gain + ring 39 | results/imaging2/nullrulers/report.md §2; posthoc/xref_gainring.json | 2f7f482 |
| N10 | Severe: stage and all six lobes correct, retreat ê 1–12 mm vs true 11.5–18 mm, fit χ²/dof 2.1–2.6 | results/imaging2/scores_designs.csv | 6db98f6 |
| N11 | RightOnly replication: lobes S5 + S6 exact; ê 3.0 / 3.5 mm vs true 11.5 / 7.5 mm | results/imaging2/rightonly/rightonly.md | 5a24a0f |
| N12 | Array sensitivity (SNR of a 1 cm³ change of \|Δε*\| = 20): up to ≈ 8 at the ring height, ≤ 0.6 at z = 20 mm, ≤ 0.26 at z = 0 | results/imaging2/README.md §6; imaging2/render.py | 6db98f6 |
| N13 | Held-out surrogate misfit for Severe: 94 with linear depth features, 15 with layered-stack features (signal 170) | results/imaging2/README.md §2 | 6db98f6 |
| N14 | H6 against the other five healthy meshes: lowest R31 (−0.12 dB, z −1.9); central in R21, R32 and phase | results/imaging2/posthoc3/verify.md | 2f7f482 |
