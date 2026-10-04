# Test_B protocol validation on the known lobe designs (code 89af4b3-dirty)

Test_B was not opened. Every known design is treated as if blind (its own matched healthy reference; Test_B will use Healthy_sliced_new). Truth = sectors_affected in data/sims_lobe.csv (core not scored).
Rulers: null contrast 0.212 deg (largest relative-pattern rms of Healthy_sliced vs Healthy_sliced_new, MCI_lobe_c3 vs Healthy_sliced_new, Severe_lobe vs Healthy_sliced_new, Severe_lobe_c3 vs Healthy_sliced); healthy-twin |ring mean| 1.111 deg (Healthy_sliced vs Healthy_sliced_new). Smearing w on all known designs: 0.4.

## Summary
| mode | designs | exact | hits | false_alarms | misses | correct_rejections | uncertain | side_correct |
|---|---|---|---|---|---|---|---|---|
| in-sample (w on all designs) | 10 | 7 | 26 | 0 | 0 | 24 | 10 | 10 |
| leave group out | 10 | 7 | 24 | 0 | 2 | 24 | 10 | 10 |

## Per design
| design | reference | truth sectors | mode | w | accepted | reason | pattern call | contrast / null | ring mean g (deg) | hits | false alarms | misses | correct rejections | uncertain | exact | fit side | mirror side | mirror votes (>=2x) | mirror >=3x | final side | side confidence | truth side | side correct | sector calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced | Healthy_sliced_new | none | in-sample (w on all designs) | 0.40 | False | contrast < 2x null | none | 0.21 | 1.11 | 0 | 0 | 0 | 6 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (nan), S2 not affected (nan), S3 not affected (nan), S4 not affected (nan), S5 not affected (nan), S6 not affected (nan) |
| Healthy_sliced | Healthy_sliced_new | none | leave group out | 0.40 | False | contrast < 2x null | none | 0.21 | 1.11 | 0 | 0 | 0 | 6 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (nan), S2 not affected (nan), S3 not affected (nan), S4 not affected (nan), S5 not affected (nan), S6 not affected (nan) |
| Mild_lobe | Healthy_sliced_new | 2356 | in-sample (w on all designs) | 0.40 | True | accepted | 2356 | 2.64 | -7.82 | 0 | 0 | 0 | 1 | 5 | False | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (99.0), S2 uncertain (0.8), S3 uncertain (1.4), S4 uncertain (0.7), S5 uncertain (1.3), S6 uncertain (1.1) |
| Mild_lobe | Healthy_sliced_new | 2356 | leave group out | 0.40 | True | accepted | 2356 | 2.64 | -7.82 | 0 | 0 | 0 | 1 | 5 | False | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (99.0), S2 uncertain (0.8), S3 uncertain (1.4), S4 uncertain (0.7), S5 uncertain (1.3), S6 uncertain (1.1) |
| Mild_lobe_new | Healthy_sliced | 2356 | in-sample (w on all designs) | 0.40 | True | accepted | 2356 | 3.15 | -7.19 | 1 | 0 | 0 | 1 | 4 | False | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (2.1), S2 uncertain (1.7), S3 affected (2.1), S4 uncertain (1.7), S5 uncertain (1.5), S6 uncertain (1.4) |
| Mild_lobe_new | Healthy_sliced | 2356 | leave group out | 0.40 | True | accepted | 2356 | 3.15 | -7.19 | 1 | 0 | 0 | 1 | 4 | False | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (2.1), S2 uncertain (1.7), S3 affected (2.1), S4 uncertain (1.7), S5 uncertain (1.5), S6 uncertain (1.4) |
| Moderate_lobe | Healthy_sliced_new | 12356 | in-sample (w on all designs) | 0.40 | True | accepted | 12356 | 7.21 | -9.84 | 4 | 0 | 0 | 1 | 1 | False | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 affected (5.3), S2 affected (4.1), S3 uncertain (1.9), S4 not affected (5.7), S5 affected (3.2), S6 affected (5.3) |
| Moderate_lobe | Healthy_sliced_new | 12356 | leave group out | 0.50 | True | accepted | 26 | 7.21 | -9.84 | 2 | 0 | 2 | 1 | 1 | False | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 uncertain (1.4), S2 affected (4.2), S3 not affected (5.2), S4 not affected (5.9), S5 not affected (4.2), S6 affected (5.5) |
| Moderate_lobe_c3 | Healthy_sliced | 12356 | in-sample (w on all designs) | 0.40 | True | accepted | 12356 | 6.72 | -9.30 | 5 | 0 | 0 | 1 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 affected (5.4), S2 affected (4.9), S3 affected (2.9), S4 not affected (5.8), S5 affected (2.5), S6 affected (4.9) |
| Moderate_lobe_c3 | Healthy_sliced | 12356 | leave group out | 0.50 | True | accepted | 12356 | 6.72 | -9.30 | 5 | 0 | 0 | 1 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 affected (6.0), S2 affected (5.5), S3 affected (3.5), S4 not affected (6.4), S5 affected (3.1), S6 affected (5.4) |
| Severe_lobe | Healthy_sliced_new | 123456 | in-sample (w on all designs) | 0.40 | False | contrast < 2x null | 123456 (diffuse) | 1.00 | -16.89 | 6 | 0 | 0 | 0 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 affected (15.2), S2 affected (15.2), S3 affected (15.2), S4 affected (15.2), S5 affected (15.2), S6 affected (15.2) |
| Severe_lobe | Healthy_sliced_new | 123456 | leave group out | 0.40 | False | contrast < 2x null | 123456 (diffuse) | 1.00 | -16.89 | 6 | 0 | 0 | 0 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 affected (15.2), S2 affected (15.2), S3 affected (15.2), S4 affected (15.2), S5 affected (15.2), S6 affected (15.2) |
| Severe_lobe_c3 | Healthy_sliced | 123456 | in-sample (w on all designs) | 0.40 | False | contrast < 2x null | 123456 (diffuse) | 0.90 | -16.57 | 6 | 0 | 0 | 0 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 affected (14.9), S2 affected (14.9), S3 affected (14.9), S4 affected (14.9), S5 affected (14.9), S6 affected (14.9) |
| Severe_lobe_c3 | Healthy_sliced | 123456 | leave group out | 0.40 | False | contrast < 2x null | 123456 (diffuse) | 0.90 | -16.57 | 6 | 0 | 0 | 0 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 affected (14.9), S2 affected (14.9), S3 affected (14.9), S4 affected (14.9), S5 affected (14.9), S6 affected (14.9) |
| LeftOnly_test_c3 | Healthy_sliced_new | 23 | in-sample (w on all designs) | 0.40 | True | accepted | 23 | 8.00 | -3.73 | 2 | 0 | 0 | 4 | 0 | True | left | left | 26 | 15 | left | established | left | True | S1 not affected (3.8), S2 affected (2.8), S3 affected (4.2), S4 not affected (2.3), S5 not affected (3.7), S6 not affected (4.4) |
| LeftOnly_test_c3 | Healthy_sliced_new | 23 | leave group out | 0.40 | True | accepted | 23 | 8.00 | -3.73 | 2 | 0 | 0 | 4 | 0 | True | left | left | 26 | 15 | left | established | left | True | S1 not affected (3.8), S2 affected (2.8), S3 affected (4.2), S4 not affected (2.3), S5 not affected (3.7), S6 not affected (4.4) |
| RightOnly_test | Healthy_sliced_new | 56 | in-sample (w on all designs) | 0.40 | True | accepted | 56 | 8.18 | -5.61 | 2 | 0 | 0 | 4 | 0 | True | right | right | 18 | 15 | right | established | right | True | S1 not affected (2.6), S2 not affected (4.0), S3 not affected (4.4), S4 not affected (3.7), S5 affected (3.1), S6 affected (4.3) |
| RightOnly_test | Healthy_sliced_new | 56 | leave group out | 0.40 | True | accepted | 56 | 8.18 | -5.61 | 2 | 0 | 0 | 4 | 0 | True | right | right | 18 | 15 | right | established | right | True | S1 not affected (2.6), S2 not affected (4.0), S3 not affected (4.4), S4 not affected (3.7), S5 affected (3.1), S6 affected (4.3) |
| MCI_lobe_c3 | Healthy_sliced_new | none | in-sample (w on all designs) | 0.40 | False | contrast < 2x null | none | 0.54 | -0.19 | 0 | 0 | 0 | 6 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (nan), S2 not affected (nan), S3 not affected (nan), S4 not affected (nan), S5 not affected (nan), S6 not affected (nan) |
| MCI_lobe_c3 | Healthy_sliced_new | none | leave group out | 0.40 | False | contrast < 2x null | none | 0.54 | -0.19 | 0 | 0 | 0 | 6 | 0 | True | symmetric | none | 0 | 0 | no left-right asymmetry | - | no left-right asymmetry | True | S1 not affected (nan), S2 not affected (nan), S3 not affected (nan), S4 not affected (nan), S5 not affected (nan), S6 not affected (nan) |

## y_k (deg, 3.2-3.5 GHz neighbour-path phase change at antenna k, against the matched reference)
| design | y T1 (deg) | y T2 (deg) | y T3 (deg) | y T4 (deg) | y T5 (deg) | y T6 (deg) |
|---|---|---|---|---|---|---|
| Healthy_sliced | 1.07 | 1.12 | 1.12 | 1.04 | 1.14 | 1.18 |
| Mild_lobe | -6.79 | -7.89 | -8.44 | -7.41 | -8.22 | -8.15 |
| Mild_lobe_new | -6.13 | -7.55 | -8.03 | -6.47 | -7.42 | -7.57 |
| Moderate_lobe | -11.14 | -10.76 | -9.05 | -7.12 | -9.34 | -11.65 |
| Moderate_lobe_c3 | -10.61 | -10.52 | -8.76 | -6.76 | -8.52 | -10.61 |
| Severe_lobe | -16.83 | -17.21 | -17.14 | -16.78 | -16.69 | -16.67 |
| Severe_lobe_c3 | -16.51 | -16.82 | -16.83 | -16.36 | -16.37 | -16.53 |
| LeftOnly_test_c3 | -3.05 | -5.75 | -6.17 | -3.61 | -1.96 | -1.82 |
| RightOnly_test | -5.45 | -3.70 | -3.67 | -5.04 | -7.69 | -8.07 |
| MCI_lobe_c3 | -0.39 | -0.20 | -0.12 | -0.10 | -0.04 | -0.25 |
