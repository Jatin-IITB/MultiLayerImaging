# POST HOC: rotated nulls vs H6, and is H6 typical?

Ratios: band power per path (trapezoid over 3.2–4.2 GHz, glitch-masked), geometric mean over each ring class; R31 = opposite / neighbour, R21 = second-neighbour / neighbour, R32 = opposite / second-neighbour (dB). Ring: per-antenna neighbour-path phase delay, 3.30–3.65 GHz.

| rotated null vs H6 | ΔR31 dB | ΔR21 dB | ΔR32 dB | ring spread ° | ring mean ° | left − right ° |
|---|---|---|---|---|---|---|
| rot07 | +0.030 | +0.070 | -0.040 | 1.42 | +0.24 | +0.69 |
| rot19 | +0.105 | -0.363 | +0.468 | 0.68 | +0.85 | +0.28 |
| rot31 | +0.119 | +0.054 | +0.065 | 1.69 | +0.63 | +1.17 |
| rot43 | +0.204 | -0.172 | +0.376 | 0.91 | +0.55 | +0.84 |

Each healthy mesh against the mean of the other five (z = difference / SD of the other five; rank 1 = lowest):

| mesh | R31: Δ (z, rank) | R21: Δ (z, rank) | R32: Δ (z, rank) | ring-mean phase vs mean of others ° | ring spread ° |
|---|---|---|---|---|---|
| H6 | -0.119 (-1.9, 1) | +0.070 (+0.4, 3) | -0.189 (-0.9, 2) | -0.18 | 0.91 |
| H7 | +0.044 (+0.5, 5) | +0.142 (+0.8, 5) | -0.099 (-0.4, 4) | -1.90 | 0.63 |
| rot07 | -0.082 (-1.1, 2) | +0.155 (+0.8, 6) | -0.237 (-1.1, 1) | +0.11 | 1.12 |
| rot19 | +0.007 (+0.1, 3) | -0.366 (-3.6, 1) | +0.373 (+2.3, 6) | +0.85 | 0.68 |
| rot31 | +0.024 (+0.3, 4) | +0.135 (+0.7, 4) | -0.111 (-0.5, 3) | +0.58 | 1.12 |
| rot43 | +0.126 (+2.1, 6) | -0.136 (-0.7, 2) | +0.262 (+1.3, 5) | +0.48 | 1.06 |
