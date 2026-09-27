# Decision rule (binary headline, code 3ad19cb) - noise-robustness only

Input: one full 6-port measurement. For each driven antenna t, x_t = band power-average over the whole common band of |S(t+3, t)|^2 (opposite antenna), in dB.

1. **INVALID** if the quality gate fails: any antenna with <|S_ii|^2> > 0.8 or std_f|S_ii| < 0.1 (open / short / no contact); 50 MHz column power > 1 + 0.2; neighbour reciprocity error > 1.0; symmetry spread > [1.25, 5.0] dB (k = 0, 1); accepted-power centroid outside the Normal window (at least ±50 MHz). Report the reason.
2. Otherwise, per antenna view: **AD** if x_t < τ − m, **Normal** if x_t > τ + m, else **UNCERTAIN**; τ = -52.69 dB (95 % CI -52.92 to -52.64), m = 0.23 dB at the `typical` noise profile (σ_ref = 0.44 dB, noise reference = port, between-mesh not yet measured).
3. Screening variant (P(Normal) = 0.8): τ_screen = -52.76 dB.
4. Combine the six views by majority vote of the non-UNCERTAIN views; a tie or no non-UNCERTAIN view gives UNCERTAIN.

τ and m per noise profile:

| profile | tau_dB | tau_CI_lo | tau_CI_hi | tau_screen_dB | margin_dB | sd_ref_dB | uncertain_fraction |
|---|---|---|---|---|---|---|---|
| ideal | -52.769 | -53.035 | -52.762 | -52.769 | 0.239 | 0.455 | 0.012 |
| good | -52.848 | -53.000 | -52.673 | -52.848 | 0.236 | 0.450 | 0.033 |
| typical | -52.687 | -52.922 | -52.636 | -52.759 | 0.231 | 0.441 | 0.023 |
| noisy | -51.897 | -52.068 | -51.865 | -51.996 | 0.218 | 0.415 | 0.043 |
| very_noisy | -48.099 | -48.119 | -47.992 | -48.300 | 0.167 | 0.319 | 0.231 |
| typical_jitter | -52.693 | -52.777 | -52.564 | -52.693 | 0.231 | 0.440 | 0.018 |

No thresholds are given for 3-class schemes: they are unverified against mesh noise.