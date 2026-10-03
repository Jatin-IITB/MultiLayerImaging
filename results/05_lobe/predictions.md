# Pre-registered predictions for LeftOnly_test (written before the file exists)

Code 7ccec7f. Derived only from Healthy_sliced and Mild_lobe. LeftOnly_test = Mild_lobe with the right temporal (S6) and right parietal (S5) lobes reset to healthy; left temporal (S2), left parietal (S3) and the hippocampus as in Mild. Do not edit after LeftOnly_test arrives.

## Model
Linear superposition + locality: the Mild change of each path is split between the left lobes (facing T2, T3) and the right lobes (facing T5, T6) in proportion to how many of the path's end antennas face an affected lobe on each side. Paths whose ends face only unaffected lobes (T1, T4), and every path that maps to itself under the left-right mirror, get exactly half of the Mild change (mirror symmetry + linearity). Nonlinearity is ignored (the changes are not small), so sizes are rough. Baseline for scoring: every path changes by half of Mild (no locality).

## Predictions
1. **Left-right index** (paths touching T2/T3 minus paths touching T5/T6): **+0.232 dB**, sign positive, |value| = 3.3x the noise floor (0.071 dB, larger of healthy / staged-mirror floors). The no-locality baseline predicts 0. Both are clean-data statements: with ±0.5 dB per-port gain errors this index is not measurable (its gain-induced SD is ~0.4 dB).
2. **Front-back index**: +0.038 dB (floor 0.084 dB), i.e. no front-back asymmetry beyond the floor.
3. **Paths with both ends on the right** (T5-T6, T5 and T6 reflections) and paths from an unaffected antenna to a right antenna (T1-T6, T4-T5, T1-T5, T4-T6): change ~0 (within 2x the numerical noise of their path type: reflection 0.01 dB, neighbour 0.16 dB, second-neighbour 0.30 dB, opposite 0.13 dB).
4. **Paths with both ends on the left** (T2-T3, T2 and T3 reflections) and from an unaffected antenna to a left antenna (T1-T2, T3-T4, T1-T3, T2-T4): change ~ the full Mild change of that path (sign as in Mild).
5. **Ring-averaged ratios** ~ halfway between Healthy_sliced and Mild_lobe: R31 -15.22, R21 -20.24, R32 5.03 dB.
6. **Frozen detection rule** (R31, tau -15.27 ± 0.08 dB): predicted R31 -15.22 dB -> mostly **UNCERTAIN**. Frozen staging boundaries: three (R21): Normal|Mild at -19.98, Mild|Severe at -18.75; three_merged (R32): Severe|Mild+Moderate at 2.77, Mild+Moderate|Normal at 4.64.

## Scoring (fixed now)
- Each path prediction (table below) is correct if the observed change has the predicted sign and |observed - predicted| <= max(0.5 |predicted|, 2x the numerical noise of that path type, column below); predictions of ~0 are correct if |observed| <= that 2x noise.
- The locality model wins over the no-locality baseline if its rms error over all 21 paths is lower.
- Prediction 1 holds if the left-right index has the predicted sign and |index| >= 3x the symmetry floor.
- Predictions 5-6 hold if R31/R21/R32 lie within 0.3 dB of the predicted values and the frozen-rule label matches for >= 80% of noisy measurements.

## Per-path predictions
| path | type | Mild change dB | predicted LeftOnly change dB (locality) | no-locality baseline dB | 2x numerical noise of path type dB |
|---|---|---|---|---|---|
| T1 refl. | reflection | 0.020 | 0.010 | 0.010 | 0.014 |
| T1-T2 | neighbour | 0.019 | 0.019 | 0.009 | 0.161 |
| T1-T3 | second-neighbour | 0.594 | 0.594 | 0.297 | 0.297 |
| T1-T4 | opposite | -0.912 | -0.456 | -0.456 | 0.127 |
| T1-T5 | second-neighbour | 0.442 | 0.000 | 0.221 | 0.297 |
| T1-T6 | neighbour | 0.090 | 0.000 | 0.045 | 0.161 |
| T2 refl. | reflection | -0.026 | -0.026 | -0.013 | 0.014 |
| T2-T3 | neighbour | 0.086 | 0.086 | 0.043 | 0.161 |
| T2-T4 | second-neighbour | 0.459 | 0.459 | 0.229 | 0.297 |
| T2-T5 | opposite | -1.244 | -0.622 | -0.622 | 0.127 |
| T2-T6 | second-neighbour | 1.144 | 0.572 | 0.572 | 0.297 |
| T3 refl. | reflection | -0.037 | -0.037 | -0.018 | 0.014 |
| T3-T4 | neighbour | 0.003 | 0.003 | 0.002 | 0.161 |
| T3-T5 | second-neighbour | 0.753 | 0.376 | 0.376 | 0.297 |
| T3-T6 | opposite | -1.333 | -0.666 | -0.666 | 0.127 |
| T4 refl. | reflection | 0.033 | 0.017 | 0.017 | 0.014 |
| T4-T5 | neighbour | 0.012 | 0.000 | 0.006 | 0.161 |
| T4-T6 | second-neighbour | 0.106 | 0.000 | 0.053 | 0.297 |
| T5 refl. | reflection | -0.040 | -0.000 | -0.020 | 0.014 |
| T5-T6 | neighbour | 0.090 | 0.000 | 0.045 | 0.161 |
| T6 refl. | reflection | -0.022 | -0.000 | -0.011 | 0.014 |
