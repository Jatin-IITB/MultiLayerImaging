# Adversarial review round 2, main session: field exports (code d03c077)

## R7 / G8. Geometry of every field export
Read from each file's header and, for the 18 per-excitation exports, from the data rows:
| file | min (mm) | max (mm) | grid (mm) | nodes | z planes | kind | z range read (mm) | distinct z read | NaN nodes |
|---|---|---|---|---|---|---|---|---|---|
| E_Normal_T1_3p4GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T1_3p6GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T1_3p6GHz_wide.fld | [-120.0, -120.0, -120.0] | [120.0, 120.0, 120.0] | [4.0, 4.0, 4.0] | 226981 | 61 | volume | n/a | n/a | n/a |
| E_Normal_T1_3p8GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T2_3p4GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T2_3p6GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T2_3p8GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T3_3p4GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T3_3p6GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T3_3p8GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T4_3p4GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T4_3p6GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T4_3p8GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T5_3p4GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T5_3p6GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T5_3p8GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T6_3p4GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T6_3p6GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |
| E_Normal_T6_3p8GHz.fld | [-90.0, -90.0, -90.0] | [90.0, 90.0, 90.0] | [3.0, 3.0, 3.0] | 226981 | 61 | volume | -90 to 90 | 61 | 22 |

Every export is a 3-D volume (61 z planes, -90 to +90 mm, 3 mm grid; the 'wide' T1 export 61 planes, -120 to +120 mm, 4 mm). None is the `field_cutplane` sheet (z = -9.09 mm). The antennas (feed z = 48 mm, patch to AMC z = 44-78 mm, radius 97-111 mm) lie inside the exported cube.

## A14 / G3. Antennas located from their own fields (3.6 GHz; |E|-weighted centroid of the strongest 1% of nodes at r = 89-93 mm)
| field file | centroid azimuth (deg) | centroid z (mm) | expected azimuth (T# convention) |
|---|---|---|---|
| E_Normal_T1_3p6GHz | -90.5 | 51.8 | -90 |
| E_Normal_T2_3p6GHz | -31.0 | 51.8 | -30 |
| E_Normal_T3_3p6GHz | 29.6 | 51.7 | 30 |
| E_Normal_T4_3p6GHz | 89.4 | 51.7 | 90 |
| E_Normal_T5_3p6GHz | 148.9 | 51.8 | 150 |
| E_Normal_T6_3p6GHz | -150.4 | 51.8 | -150 |

Polarisation near each antenna (field components in the local spherical frame, amplitude shares; the air gap lies between skin (r 88) and antenna ground (r 97.65); 'in head' is skin to outer gray matter):
| region | nodes | |E_r| share | |E_theta| share | |E_phi| share | theta / (theta+phi) amplitude |
|---|---|---|---|---|---|
| air gap r 89-93, +-15 deg, 40 < z < 80 | 272.00 | 0.85 | 0.45 | 0.28 | 0.61 |
| air gap r 89-93, boresight +-5 deg, 45 < z < 58 | 38.33 | 0.90 | 0.40 | 0.16 | 0.71 |
| in head r 80-87, boresight +-5 deg, 45 < z < 58 | 56.00 | 0.30 | 0.95 | 0.08 | 0.92 |
| in head r 80-87, +-15 deg, 40 < z < 80 | 425.17 | 0.32 | 0.93 | 0.16 | 0.85 |
(mean over the six antennas; per antenna in F_G3_polarisation.csv)

## G5 and the depth claims. Share of each path's sensitivity |E_a.E_b| (3.6 GHz) by region and by height, mean per path type:
| type | share air (r > 88, inside the cube) | share skin+fat+skull (83.5-88) | share CSF layer (83-83.5) | share gray (76-83) | share white (25-76) | share hippocampus (<= 25) | brain share at z > 40 | head share at z > 40 | brain share at 0 < z <= 40 | head share at 0 < z <= 40 | brain share at z <= 0 | head share at z <= 0 | in-brain share within 13.5 mm of the brain surface |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| neighbour | 0.990 | 0.006 | 0.000 | 0.002 | 0.002 | 0.000 | 0.574 | 0.688 | 0.396 | 0.278 | 0.030 | 0.034 | 0.699 |
| opposite | 0.987 | 0.009 | 0.000 | 0.002 | 0.002 | 0.000 | 0.692 | 0.781 | 0.271 | 0.178 | 0.037 | 0.041 | 0.731 |
| reflection | 0.994 | 0.004 | 0.000 | 0.001 | 0.001 | 0.000 | 0.558 | 0.714 | 0.428 | 0.270 | 0.014 | 0.016 | 0.764 |
| second-neighbour | 0.988 | 0.008 | 0.000 | 0.002 | 0.002 | 0.000 | 0.615 | 0.740 | 0.344 | 0.220 | 0.041 | 0.041 | 0.715 |

## C4. Physical sign and size (prediction committed in predictions_R3_C4.md before this ran)
Head share of each path's sensitivity in the LeftOnly change volumes and the phase change predicted by share x (-k0 dn d) at 3.6 GHz, against the observed LeftOnly - Healthy_sliced_new phase change:
| path | type | head share: gap S2 (gray -> CSF_Mild) | head share: gray band S2 (white -> Mild gray) | head share: gap S3 (gray -> CSF_Mild) | head share: gray band S3 (white -> Mild gray) | head share: CSF layer, all (CSF -> CSF_Mild) | predicted phase change (deg), share x -k0 dn d | observed at 3.6 GHz (deg) | observed mean 3.30-3.65 GHz (deg) |
|---|---|---|---|---|---|---|---|---|---|
| T1-T2 | neighbour | 0.083 | 0.041 | 0.004 | 0.001 | 0.026 | -2.012 | -4.453 | -4.902 |
| T1-T3 | second-neighbour | 0.023 | 0.011 | 0.059 | 0.014 | 0.020 | -2.228 | 0.752 | 6.242 |
| T1-T4 | opposite | 0.010 | 0.005 | 0.014 | 0.004 | 0.019 | -0.622 | 2.666 | 1.324 |
| T1-T5 | second-neighbour | 0.011 | 0.005 | 0.005 | 0.001 | 0.020 | -0.364 | -7.945 | -0.236 |
| T1-T6 | neighbour | 0.003 | 0.001 | 0.001 | 0.000 | 0.026 | -0.056 | -1.857 | -2.099 |
| T2-T3 | neighbour | 0.078 | 0.038 | 0.118 | 0.031 | 0.027 | -5.219 | -7.595 | -7.883 |
| T2-T4 | second-neighbour | 0.042 | 0.019 | 0.031 | 0.008 | 0.020 | -1.850 | -2.418 | 6.658 |
| T2-T5 | opposite | 0.059 | 0.027 | 0.017 | 0.004 | 0.021 | -1.795 | 3.099 | 2.040 |
| T2-T6 | second-neighbour | 0.048 | 0.022 | 0.015 | 0.004 | 0.021 | -1.507 | 1.587 | 7.019 |
| T3-T4 | neighbour | 0.002 | 0.001 | 0.104 | 0.028 | 0.026 | -3.069 | -4.985 | -5.759 |
| T3-T5 | second-neighbour | 0.010 | 0.005 | 0.062 | 0.015 | 0.020 | -2.005 | -8.146 | 3.719 |
| T3-T6 | opposite | 0.011 | 0.005 | 0.078 | 0.019 | 0.021 | -2.503 | 5.245 | 2.925 |
| T4-T5 | neighbour | 0.001 | 0.000 | 0.003 | 0.001 | 0.027 | -0.071 | -1.700 | -1.946 |
| T4-T6 | second-neighbour | 0.003 | 0.002 | 0.014 | 0.004 | 0.020 | -0.464 | -1.457 | 1.697 |
| T5-T6 | neighbour | 0.001 | 0.000 | 0.001 | 0.000 | 0.027 | -0.008 | -1.749 | -2.321 |

Neighbour paths: predicted -5.22 to -0.01 deg, observed (3.30-3.65 GHz) -7.88 to -1.95 deg. Correlation of predicted and observed over the 15 paths: r = 0.25 (p = 0.37).
Band dependence (figure `figures/F_C4_band_dependence.png`): healthy-head |Sii| resonances at 3.658, 3.658, 3.659, 3.657, 3.658, 3.657 GHz; transmission notches in `F_C4_notches.csv` (6 found).

Neighbour mirror pairs, left minus right:
| mirror pair | predicted left - right (deg) | observed left - right, 3.30-3.65 GHz (deg) |
|---|---|---|
| T2-T3 vs T5-T6 | -5.21 | -5.56 |
| T3-T4 vs T4-T5 | -3.00 | -3.81 |
| T1-T2 vs T1-T6 | -1.96 | -2.80 |

Long paths: predicted and observed signs agree on 1 of 9. The right-side neighbour paths all move by about -2.1 deg although the share model predicts ~0.

Band dependence of the largest cross-ratio asymmetries (mean |value| per sub-band against the largest symmetric design):
| statistic | band | |LeftOnly| mean (deg) | largest symmetric design, mean |.| (deg) | ratio |
|---|---|---|---|---|
| T1T3·T4T5 / T1T5·T3T4 | 3.20-3.50 | 12.41 | 3.94 | 3.15 |
| T1T3·T4T5 / T1T5·T3T4 | 3.50-3.65 | 23.65 | 9.33 | 2.53 |
| T1T3·T4T5 / T1T5·T3T4 | 3.65-3.80 | 9.24 | 18.25 | 0.51 |
| T1T3·T4T5 / T1T5·T3T4 | 3.80-4.20 | 4.13 | 7.63 | 0.54 |
| T1T2·T3T4 / T1T3·T2T4 | 3.20-3.50 | 13.49 | 2.39 | 5.65 |
| T1T2·T3T4 / T1T3·T2T4 | 3.50-3.65 | 17.54 | 7.78 | 2.26 |
| T1T2·T3T4 / T1T3·T2T4 | 3.65-3.80 | 9.90 | 10.57 | 0.94 |
| T1T2·T3T4 / T1T3·T2T4 | 3.80-4.20 | 5.18 | 4.87 | 1.06 |
| T1T3·T2T5 / T1T5·T2T3 | 3.20-3.50 | 11.16 | 2.40 | 4.65 |
| T1T3·T2T5 / T1T5·T2T3 | 3.50-3.65 | 19.74 | 10.66 | 1.85 |
| T1T3·T2T5 / T1T5·T2T3 | 3.65-3.80 | 7.01 | 20.99 | 0.33 |
| T1T3·T2T5 / T1T5·T2T3 | 3.80-4.20 | 6.34 | 9.96 | 0.64 |

## Summary (fields part)
| item | verdict | old -> new | evidence |
|---|---|---|---|
| R7/G8 field-export geometry | CONFIRMED (volume, not the cut plane) | unstated -> all 19 exports are volumes: 18 x (-90..90 mm)^3 at 3 mm, 1 x (-120..120 mm)^3 at 4 mm; no field claim used the z = -9 mm plane | review2/F_R7_exports.csv |
| A14 field evidence | CONFIRMED | T# positions from fields: T1 -91, T2 -31, T3 +30, T4 +89, T5 +149, T6 -150 deg | review2/F_A14_antenna_positions.csv |
| G3 polarisation | CHANGED (inside the head the field is meridional; the 65/35 figure is an air-gap window average) | 65% theta / 35% phi -> in head at boresight: |E_theta| 0.95, |E_phi| 0.08, |E_r| 0.30 (theta/(theta+phi) 0.92); air gap +-15 deg window: |E_r| 0.85, theta/(theta+phi) 0.61 | review2/F_G3_polarisation.csv |
| G5 sensitivity by height; depth claims | CHANGED (quantified) | '99% in air' (opposite) -> air 0.987, brain 0.0045; in-brain share at z > 40 / 0-40 / <= 0: neighbour: 0.57/0.40/0.03; opposite: 0.69/0.27/0.04; reflection: 0.56/0.43/0.01; second-neighbour: 0.61/0.34/0.04 | review2/F_G5_sensitivity_regions.csv |
| C4 physical sign and size | CHANGED (neighbour asymmetry explained; long paths not) | none -> neighbour left-right, predicted vs observed: T2-T3 vs T5-T6 -5.2 vs -5.6; T3-T4 vs T4-T5 -3.0 vs -3.8; T1-T2 vs T1-T6 -2.0 vs -2.8 deg; long-path signs agree 1/9; common right-side -2.1 deg unexplained; band: cross-ratio asymmetry / largest symmetric design 3.20-3.50 3.2x, 3.50-3.65 2.5x, 3.65-3.80 0.5x, 3.80-4.20 0.5x | review2/F_C4_*.csv, figures/F_C4_band_dependence.png |
