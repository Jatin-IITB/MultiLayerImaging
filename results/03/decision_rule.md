# Decision rule (binary Normal | AD, code f142bf6) - noise-robustness only

Input: one complete 6-port measurement.

0. **Floor.** Estimate the instrument floor P_f from reciprocal-pair differences on the weakest paths (or from a dedicated terminated-port measurement). For each driven antenna t, x_t = 10·log10(<|S(t+3,t)|²>_band − P_f), the floor-subtracted band power of the opposite path.
1. **INVALID** (with the reason) if the gate fails:
   - any antenna with <|S_ii|²> > 0.8 or std_f|S_ii| < 0.1 (open / short / no contact);
   - 50 MHz column power > 1 + 0.2; neighbour reciprocity error > 1.0;
   - symmetry spread > [1.25, 5.0] dB (k = 0, 1); accepted-power centroid outside the Normal window (at least ±50 MHz);
   - **instrument floor too high**: 10·log10 P_f > τ − 8.0 dB (= -62.0 dB here).
2. Per view: **AD** if x_t < τ − m, **Normal** if x_t > τ + m, else **UNCERTAIN**; τ = -54.00 dB (95 % CI -54.04 to -53.82), m = 0.12 dB (`typical` profile; σ_ref = 0.23 dB, noise reference = port, between-mesh not yet measured). Screening prior P(Normal) = 0.8: τ_screen = -54.00 dB.
3. Majority vote of the non-UNCERTAIN views; a tie or no decided view gives **UNCERTAIN**.

**Calibration-free alternative (M5.R31)**, recommended when per-port gains are not calibrated to better than ±0.5 dB: R31 = 10·log10( GM_t(<|S(t+3,t)|²> − P_f) / GM_t(<|S(t+1,t)|²> − P_f) ), one value per measurement (GM = geometric mean over the six antennas; per-port gains cancel). Use it with the gain-invariant gate (relative |S_ii| flatness for open/short, reciprocity, floor). **AD** if R31 < τ − m, **Normal** if R31 > τ + m, else UNCERTAIN; τ = -15.14 dB (95 % CI -15.32 to -15.14), m = 0.05 dB. Same gate.

Performance of the complete rule per measurement (CV; gate = full or gain-invariant):

| rule | gate_mode | profile | sensitivity | specificity | uncertain_rate | invalid_rate |
|---|---|---|---|---|---|---|
| M5.C3 ring-mean | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 ring-mean | full | typical | 1.000 | 1.000 | 0.000 | 0.003 |
| M5.C3 ring-mean | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.353 |
| M5.C3 ring-mean | full | typical+gain1.0dB | 1.000 | 0.625 | 0.109 | 0.847 |
| M5.C3 ring-mean | full | typical+gain2.0dB | 1.000 | 0.000 | 0.133 | 0.958 |
| M5.C3 ring-mean | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 ring-mean | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain1.0dB | 0.817 | 0.833 | 0.144 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain2.0dB | 0.689 | 0.500 | 0.292 | 0.000 |
| M5.C3 vote(6 views) | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 vote(6 views) | full | typical | 1.000 | 1.000 | 0.000 | 0.003 |
| M5.C3 vote(6 views) | full | typical+gain0.5dB | 1.000 | 0.985 | 0.007 | 0.353 |
| M5.C3 vote(6 views) | full | typical+gain1.0dB | 0.989 | 0.708 | 0.048 | 0.847 |
| M5.C3 vote(6 views) | full | typical+gain2.0dB | 1.000 | 0.000 | 0.578 | 0.958 |
| M5.C3 vote(6 views) | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 vote(6 views) | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain0.5dB | 0.993 | 0.991 | 0.008 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain1.0dB | 0.826 | 0.883 | 0.088 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain2.0dB | 0.485 | 0.691 | 0.251 | 0.000 |
| M5.R31 | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.R31 | full | typical | 1.000 | 1.000 | 0.000 | 0.003 |
| M5.R31 | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.353 |
| M5.R31 | full | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.847 |
| M5.R31 | full | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.958 |
| M5.R31 | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.R31 | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.000 |

τ and m per profile:

| feature | profile | tau_dB | tau_CI_lo | tau_CI_hi | tau_screen_dB | margin_dB | sd_ref_dB |
|---|---|---|---|---|---|---|---|
| M5.C3 | good | -53.969 | -54.102 | -53.861 | -53.969 | 0.122 | 0.232 |
| M5.C3 | ideal | -53.901 | -54.228 | -53.899 | -53.901 | 0.119 | 0.228 |
| M5.C3 | noisy | -53.724 | -53.843 | -53.658 | -53.764 | 0.156 | 0.297 |
| M5.C3 | typical | -54.003 | -54.037 | -53.819 | -54.003 | 0.123 | 0.234 |
| M5.C3 | typical+gain0.5dB | -53.773 | -54.049 | -53.723 | -54.096 | 0.249 | 0.476 |
| M5.C3 | typical+gain1.0dB | -53.733 | -54.052 | -53.694 | -54.693 | 0.451 | 0.861 |
| M5.C3 | typical+gain2.0dB | -54.521 | -54.711 | -53.561 | -56.089 | 1.562 | 1.645 |
| M5.C3 | typical_jitter | -53.883 | -54.151 | -53.853 | -53.883 | 0.120 | 0.228 |
| M5.C3 | very_noisy | -51.293 | -51.359 | -51.171 | -51.510 | 0.261 | 0.497 |
| M5.R31 | good | -15.147 | -15.319 | -15.145 | -15.410 | 0.053 | 0.010 |
| M5.R31 | ideal | -15.150 | -15.322 | -15.148 | -15.420 | 0.053 | 0.004 |
| M5.R31 | noisy | -15.061 | -15.276 | -15.019 | -15.212 | 0.044 | 0.084 |
| M5.R31 | typical | -15.139 | -15.319 | -15.136 | -15.376 | 0.053 | 0.029 |
| M5.R31 | typical+gain0.5dB | -15.160 | -15.327 | -15.147 | -15.394 | 0.053 | 0.030 |
| M5.R31 | typical+gain1.0dB | -15.136 | -15.310 | -15.130 | -15.372 | 0.053 | 0.029 |
| M5.R31 | typical+gain2.0dB | -15.148 | -15.319 | -15.132 | -15.381 | 0.053 | 0.029 |
| M5.R31 | typical_jitter | -15.139 | -15.316 | -15.134 | -15.375 | 0.049 | 0.029 |
| M5.R31 | very_noisy | -12.841 | -13.021 | -12.729 | -13.022 | 0.109 | 0.209 |

No thresholds are given for 3-class schemes: they are unverified against mesh noise.