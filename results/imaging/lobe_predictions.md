# Pre-registered predictions for the blind lobe designs (imaging session)

Written 2026-10-03 by `imaging/run_lobe.py` at code `fb5b775`, **before LeftOnly_test or MCI_lobe were opened**. The pipeline state is frozen in `results/imaging/lobe_frozen.json` (κ, λ, thresholds). Do not edit after the blind files arrive.

## Frozen pipeline

- κ(f) (fitted on Mild only): 3.218-0.694j, 3.563+0.503j, 3.104+5.578j at [3.4, 3.6, 3.8] GHz. λ (GCV on Mild): dS 0.1585, gain-invariant 0.1259.
- Primary method: **tikhonov dS**; secondary (no per-port calibration): **tikhonov log (gain-inv.)**. Rules R1–R3 as in `lobe_report.md` §5:

| method | T_abs | T_LR | T_FB |
|---|---|---|---|
| tikhonov dS | 13.81 | 4.06 | 6.45 |
| bounded dS | 13.81 | 3.92 | 3.78 |
| tikhonov log (gain-inv.) | 13.32 | 3.93 | 7.83 |
| bounded log (gain-inv.) | 13.32 | 3.93 | 4.53 |

## Expected outcomes

**LeftOnly_test** (truth: S2 left temporal and S3 left parietal affected, S1, S4, S5, S6 healthy; core as Mild).
Success criterion (from the brief, fixed now): with the primary method, R2 side = **left**, and R1 calls S2 and S3 affected and S5 and S6 healthy. Partial success: side = left with S3 affected and S5, S6 healthy.

What the frozen pipeline returns on Born-simulated LeftOnly data (true dε map, frozen κ) plus 40 typical-noise draws:

| method | P(called) S1 Fr | P(called) S2 TL | P(called) S3 PL | P(called) S4 Oc | P(called) S5 PR | P(called) S6 TR | LR | p_left | p_right | p_front_or_back |
|---|---|---|---|---|---|---|---|---|---|---|
| tikhonov dS | 0.00 | 0.62 | 1.00 | 0.00 | 0.00 | 0.00 | +14.7 ± 2.2 | 1.00 | 0.00 | 0.05 |
| bounded dS | 0.00 | 0.62 | 1.00 | 0.00 | 0.00 | 0.00 | +14.6 ± 2.2 | 1.00 | 0.00 | 0.25 |
| tikhonov log (gain-inv.) | 0.00 | 0.75 | 1.00 | 0.00 | 0.00 | 0.00 | +14.9 ± 2.3 | 1.00 | 0.00 | 0.07 |
| bounded log (gain-inv.) | 0.00 | 0.75 | 1.00 | 0.00 | 0.00 | 0.00 | +14.8 ± 2.2 | 1.00 | 0.00 | 0.20 |

Predicted: side = **left**; S3 affected; S2 affected in most draws (it is the weaker of the two: e = 7.5 mm vs 11.5 mm); S1, S4, S5, S6 healthy; front/back none (spurious front/back in 5–25 % of noisy draws, highest for the bounded fits). Caveat: the simulated data follow the linear model, while the HFSS changes are only partly linear (§0 of the report), so the real values will scatter more than these draws.

**MCI_lobe** (truth: only the hippocampus, 25 → 21.25 mm; CSF healthy).

Success criterion (fixed now): with the primary method, no sector called, side none, front/back none.

| method | p_any_called | p_left | p_right | p_front_or_back | LR |
|---|---|---|---|---|---|
| tikhonov dS | 0.00 | 0.03 | 0.03 | 0.15 | -0.4 ± 2.2 |
| bounded dS | 0.00 | 0.00 | 0.03 | 0.12 | -0.2 ± 1.4 |
| tikhonov log (gain-inv.) | 0.00 | 0.03 | 0.05 | 0.05 | -0.4 ± 2.8 |
| bounded log (gain-inv.) | 0.00 | 0.00 | 0.03 | 0.07 | -0.2 ± 1.7 |

Predicted: **no sector called, side none, front/back none** (nothing beyond the noise floor; under noise a spurious front/back call is expected in 5%–15% of draws, a spurious side call in ≤ 8 %). The hippocampal change is invisible to the array (CRLB of the core ≫ its change).

