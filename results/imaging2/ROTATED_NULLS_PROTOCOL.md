# Pre-registration: rulers with the rotated nulls (imaging2; POST HOC programme)

**Committed before `Null_rot31` and `Null_rot43` exist** in `data/raw/` (at commit time only rot07 and rot19 are present).

**Freeze.** After those files arrive, nothing below and nothing in `imaging2/nullrulers.py` is changed. The evaluation is:

    python -m imaging2.nullrulers all     # -> results/imaging2/nullrulers/report.md, report.json

It is run unchanged. It uses every rotated null whose file exists (`new_with_slices_Null_rot{07,19,31,43}.s6p`). Any
deviation will be logged in `results/imaging2/nullrulers/DEVIATIONS.md`, never folded in.

**Status of everything here: post hoc.** Committed estimates, the Test_B protocol (595e9cb) and verdict (f88236c), the
frozen files and the predictions are untouched. No re-solves are requested.

## Rules
1. **Every null counts.** Every ruler is the maximum |value| over all nulls: the old nine mirror-symmetric designs
   (H7 vs H6, H6 vs H7, MCI, Mild p5/p6, Moderate p5/p6, Severe p5/p6) plus all rotated nulls present (rot07, rot19,
   rot31, rot43).
   - No null is dropped, rot19 included.
   - The only exception is a build defect in the HFSS model found and documented by the user and the main session.
     Even then, both versions are reported.
2. **Three ways.** Every ruler is reported three ways: (a) all nulls; (b) all nulls without rot19; (c) rot19 alone.
   - For readings that are evaluated per null (R1, R2, R9, R10), each rotated null is listed separately, which contains
     (a)–(c).
   - For R11 the three ways apply to the rotated-null twin samples added to the noise model.
3. **Bars are the existing ones.** R1c floor = max |null|; ≥ 3x established, 2–3x sensitive, < 2x not separable. For
   the per-null readings the bar is exact agreement (stated per item). No new claim or bar is written after the files
   arrive.

## Section 0 (descriptive, no bar): common-mode vs scattered
For every path class k = 1, 2, 3 (and k = 0 for reference) and for each pair:
- each rotated null vs H6;
- every pair of rotated nulls;
- Mild 5 vs 6, Moderate 5 vs 6, Severe 5 vs 6, H6 vs H7 (6 vs 7), RightOnly 5 vs mirror(LeftOnly) 6.

Per path, three quantities over 3.30–3.65 GHz and over 3.2–4.2 GHz:
- band-power difference, 10·log10 of the mean |S|² ratio;
- mean over frequency of the dB difference (the main session's definition);
- band-mean phase difference.

Per class: mean, SD and range over its 6 paths, and the common-mode fraction cm = mean² / (mean² + SD²). Labels:
- **common-mode** if cm ≥ 0.8;
- **scattered** if cm < 0.5;
- **mixed** otherwise;
- **negligible** if every path is within ±0.05 dB (±0.5°).

These are reported as found; no conclusion is drawn beyond them.

## Claims and readings re-evaluated, with their bars
| id | claim / reading | statistic | bar |
|---|---|---|---|
| R1 | Rotated nulls reconstruct empty | each rotated null as target, vs H6, H7 and every other rotated null; variants standard, gain-removing, ring-mean-phase | 0 lobes with P(affected) > 0.5 in every run (stage reported) |
| R2 | LeftOnly / RightOnly one-sided calls are beyond all nulls | one-sided call pattern (affected lobes on one side only) in any rotated-null run | no rotated null one-sided in any run |
| R3 | ê left − right (LR_e) of LeftOnly, RightOnly, Test_B | R1c ratio, nulls = old nine + rotated nulls vs H6 (standard) | ≥ 3x established; currently not separable (1.24x) |
| R4 | Model-free ring left − right contrast, LeftOnly and RightOnly vs H6 | R1c ratio; nulls = nine mirror-symmetric designs + rotated nulls | ≥ 3x (now 4.87x / 5.05x) |
| R5 | Model-free ring front − back, Moderate p5 vs H6 and p6 vs H7 | R1c ratio; nulls = healthy-type + Mild (S1 = S4) + rotated | ≥ 3x (now 3.21x / 3.12x) |
| R6 | Test_B ring spread (max − min) | R1c ratio; nulls = healthy-type + rotated | ≥ 3x (now 1.49x: not separable) |
| R7 | Test_B diagonal-pair elevation (largest of 3 pairs; statistic defined after seeing Test_B) | R1c ratio; healthy-type + rotated | ≥ 3x (now 3.73x), labelled post hoc |
| R8 | Test_B T2/T5 elevation (Test_B's own pair) | R1c ratio | reported only; not a test |
| R9 | Lobe calls with each rotated null as the healthy reference: Test_B, LeftOnly, RightOnly | exact lobe calls, per variant | exact |
| R10 | Stage with each rotated null as the reference (same runs) | MAP stage | correct |
| R11 | Coverage of ê with the augmented noise model | empirical 90% coverage over the 11 targets (9 LODO + RightOnly + Test_B; primary variant); twin samples = non-null twins + {all rotated / all but rot19 / rot19 only} | ≥ 70% on affected lobes (accepted with the warning; nominal 90%) |
| R12 | Variant comparison | wrong lobe calls and wrong stages per variant over every target × reference (H6, H7, each rotated null) | descriptive; feeds the variant recommendation |

**Targets of the stage/lobe table** (R1, R9, R10, R12):
- the 9 leave-one-out designs, RightOnly and Test_B, plus each rotated null;
- references H6, H7 and every rotated null present;
- variants standard, gain-removing and ring-mean-phase;
- the committed noise model (fold noise), as before.
