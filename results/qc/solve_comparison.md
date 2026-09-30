# Solve comparison: data/archive/v1_mixed_projects (old) vs data/raw (new)

Common band 3.20-4.20 GHz, 201 points. No glitch masking (raw solver output).

## Whole-spectrum shape (rms over frequency of the ring-mode dB difference)
| comparison | k0 rms dB | k1 rms dB | k2 rms dB | k3 rms dB |
|---|---|---|---|---|
| Normal: old vs new solve | 2.62 | 1.25 | 2.58 | 0.90 |
| Mild: old vs new solve | 3.18 | 2.16 | 3.64 | 1.52 |
| Moderate: old vs new solve | 2.77 | 1.73 | 2.58 | 1.15 |
| Severe: old vs new solve | 2.90 | 1.74 | 3.16 | 1.08 |
| new Normal vs new MCI | 2.31 | 1.00 | 2.21 | 1.12 |
| new Normal vs new Mild | 2.22 | 0.93 | 3.36 | 1.71 |
| new Normal vs new Moderate | 1.48 | 0.54 | 2.53 | 1.55 |
| new Normal vs new Severe | 1.60 | 0.77 | 3.28 | 2.10 |

## Band-averaged scalars (classifier features)
| stage | C3 old dB | C3 new dB | C3 shift dB | R31 old dB | R31 new dB | R31 shift dB |
|---|---|---|---|---|---|---|
| Normal | -51.82 | -51.66 | 0.16 | -14.48 | -14.67 | -0.19 |
| MCI | nan | -51.43 | nan | nan | -14.61 | nan |
| Mild | -53.75 | -53.14 | 0.61 | -16.20 | -16.06 | 0.14 |
| Moderate | -53.91 | -53.30 | 0.61 | -16.51 | -16.17 | 0.34 |
| Severe | -53.68 | -53.54 | 0.14 | -15.85 | -15.85 | 0.00 |

New-set Normal vs AD gap: C3 1.48-1.88 dB, R31 1.18-1.50 dB. Largest old-to-new shift of the same stage: C3 0.61 dB, R31 0.34 dB.