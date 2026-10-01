# Decision rule (binary Normal | AD, code c95604c) - noise-robustness only

Input: one complete 6-port measurement.

0. **Floor.** Estimate the instrument floor P_f from reciprocal-pair differences on the weakest paths (or from a dedicated terminated-port measurement). For each driven antenna t, x_t = 10·log10(<|S(t+3,t)|²>_band − P_f), the floor-subtracted band power of the opposite path.
1. **INVALID** (with the reason) if the gate fails:
   - any antenna with <|S_ii|²> > 0.8 or std_f|S_ii| < 0.1 (open / short / no contact);
   - 50 MHz column power > 1 + 0.2; neighbour reciprocity error > 1.0;
   - symmetry spread > [1.25, 5.0] dB (k = 0, 1); accepted-power centroid outside the Normal window (at least ±50 MHz);
   - **instrument floor too high**: 10·log10 P_f > τ − 8.0 dB (= -60.7 dB here).
2. Per view: **AD** if x_t < τ − m, **Normal** if x_t > τ + m, else **UNCERTAIN**; τ = -52.71 dB (95 % CI -52.83 to -52.51), m = 0.24 dB (`typical` profile; σ_ref = 0.47 dB, noise reference = mesh). Screening prior P(Normal) = 0.8: τ_screen = -52.79 dB.
3. Majority vote of the non-UNCERTAIN views; a tie or no decided view gives **UNCERTAIN**.

**Calibration-free alternative (M5.R31)**, recommended when per-port gains are not calibrated to better than ±0.5 dB: R31 = 10·log10( GM_t(<|S(t+3,t)|²> − P_f) / GM_t(<|S(t+1,t)|²> − P_f) ), one value per measurement (GM = geometric mean over the six antennas; per-port gains cancel). Use it with the gain-invariant gate (relative |S_ii| flatness for open/short, reciprocity, floor). **AD** if R31 < τ − m, **Normal** if R31 > τ + m, else UNCERTAIN; τ = -15.27 dB (95 % CI -15.37 to -15.17), m = 0.08 dB. Same gate.

Performance of the complete rule per measurement (CV; gate = full or gain-invariant):

| rule | gate_mode | profile | sensitivity | specificity | uncertain_rate | invalid_rate |
|---|---|---|---|---|---|---|
| M5.C3 ring-mean | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 ring-mean | full | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 ring-mean | full | typical+gain0.5dB | 0.976 | 0.855 | 0.055 | 0.090 |
| M5.C3 ring-mean | full | typical+gain1.0dB | 0.957 | 0.730 | 0.101 | 0.731 |
| M5.C3 ring-mean | full | typical+gain2.0dB | 1.000 | 0.000 | 0.059 | 0.965 |
| M5.C3 ring-mean | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 ring-mean | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain0.5dB | 0.975 | 0.867 | 0.052 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain1.0dB | 0.819 | 0.883 | 0.148 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain2.0dB | 0.669 | 0.525 | 0.298 | 0.000 |
| M5.C3 vote(6 views) | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 vote(6 views) | full | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 vote(6 views) | full | typical+gain0.5dB | 0.988 | 1.000 | 0.009 | 0.090 |
| M5.C3 vote(6 views) | full | typical+gain1.0dB | 0.978 | 0.730 | 0.054 | 0.731 |
| M5.C3 vote(6 views) | full | typical+gain2.0dB | 1.000 | 0.000 | 0.176 | 0.965 |
| M5.C3 vote(6 views) | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 vote(6 views) | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain0.5dB | 0.983 | 1.000 | 0.013 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain1.0dB | 0.861 | 0.892 | 0.083 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain2.0dB | 0.597 | 0.767 | 0.231 | 0.000 |
| M5.R31 | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.R31 | full | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.090 |
| M5.R31 | full | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.731 |
| M5.R31 | full | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.965 |
| M5.R31 | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.R31 | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.000 |

τ and m per profile:

| feature | profile | tau_dB | tau_CI_lo | tau_CI_hi | tau_screen_dB | margin_dB | sd_ref_dB |
|---|---|---|---|---|---|---|---|
| M5.C3 | good | -52.668 | -52.882 | -52.525 | -52.789 | 0.245 | 0.467 |
| M5.C3 | ideal | -52.717 | -52.785 | -52.568 | -52.717 | 0.247 | 0.470 |
| M5.C3 | noisy | -52.574 | -52.722 | -52.467 | -52.662 | 0.263 | 0.501 |
| M5.C3 | typical | -52.715 | -52.833 | -52.506 | -52.791 | 0.244 | 0.466 |
| M5.C3 | typical+gain0.5dB | -52.660 | -52.695 | -52.393 | -52.903 | 0.328 | 0.625 |
| M5.C3 | typical+gain1.0dB | -52.606 | -52.784 | -52.503 | -53.527 | 0.498 | 0.949 |
| M5.C3 | typical+gain2.0dB | -52.864 | -53.289 | -51.994 | -54.784 | 1.378 | 1.745 |
| M5.C3 | typical_jitter | -52.614 | -52.783 | -52.531 | -52.736 | 0.250 | 0.476 |
| M5.C3 | very_noisy | -50.786 | -50.922 | -50.748 | -51.293 | 0.335 | 0.639 |
| M5.R31 | good | -15.257 | -15.362 | -15.159 | -15.538 | 0.076 | 0.145 |
| M5.R31 | ideal | -15.260 | -15.365 | -15.161 | -15.548 | 0.077 | 0.146 |
| M5.R31 | noisy | -15.218 | -15.383 | -15.097 | -15.378 | 0.086 | 0.164 |
| M5.R31 | typical | -15.273 | -15.368 | -15.165 | -15.527 | 0.078 | 0.149 |
| M5.R31 | typical+gain0.5dB | -15.251 | -15.352 | -15.154 | -15.506 | 0.080 | 0.153 |
| M5.R31 | typical+gain1.0dB | -15.261 | -15.363 | -15.161 | -15.517 | 0.078 | 0.148 |
| M5.R31 | typical+gain2.0dB | -15.250 | -15.367 | -15.154 | -15.500 | 0.078 | 0.150 |
| M5.R31 | typical_jitter | -15.260 | -15.360 | -15.161 | -15.515 | 0.078 | 0.149 |
| M5.R31 | very_noisy | -13.674 | -13.871 | -13.571 | -13.825 | 0.143 | 0.272 |

No thresholds are given for 3-class schemes: they are unverified against mesh noise.