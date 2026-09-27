# Decision rule (binary Normal | AD, code 45e16c6) - noise-robustness only

Input: one complete 6-port measurement.

0. **Floor.** Estimate the instrument floor P_f from reciprocal-pair differences on the weakest paths (or from a dedicated terminated-port measurement). For each driven antenna t, x_t = 10·log10(<|S(t+3,t)|²>_band − P_f), the floor-subtracted band power of the opposite path.
1. **INVALID** (with the reason) if the gate fails:
   - any antenna with <|S_ii|²> > 0.8 or std_f|S_ii| < 0.1 (open / short / no contact);
   - 50 MHz column power > 1 + 0.2; neighbour reciprocity error > 1.0;
   - symmetry spread > [1.25, 5.0] dB (k = 0, 1); accepted-power centroid outside the Normal window (at least ±50 MHz);
   - **instrument floor too high**: 10·log10 P_f > τ − 8.0 dB (= -60.8 dB here).
2. Per view: **AD** if x_t < τ − m, **Normal** if x_t > τ + m, else **UNCERTAIN**; τ = -52.79 dB (95 % CI -53.01 to -52.73), m = 0.24 dB (`typical` profile; σ_ref = 0.45 dB, noise reference = port, between-mesh not yet measured). Screening prior P(Normal) = 0.8: τ_screen = -52.79 dB.
3. Majority vote of the non-UNCERTAIN views; a tie or no decided view gives **UNCERTAIN**.

**Calibration-free alternative (M5.R31)**, recommended when per-port gains are not calibrated to better than ±0.5 dB: R31 = 10·log10( GM_t(<|S(t+3,t)|²> − P_f) / GM_t(<|S(t+1,t)|²> − P_f) ), one value per measurement (GM = geometric mean over the six antennas; per-port gains cancel). Use it with the gain-invariant gate (relative |S_ii| flatness for open/short, reciprocity, floor). **AD** if R31 < τ − m, **Normal** if R31 > τ + m, else UNCERTAIN; τ = -15.17 dB (95 % CI -15.48 to -15.16), m = 0.05 dB. Same gate.

Performance of the complete rule per measurement (CV; gate = full or gain-invariant):

| rule | gate_mode | profile | sensitivity | specificity | uncertain_rate | invalid_rate |
|---|---|---|---|---|---|---|
| M5.C3 ring-mean | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 ring-mean | full | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 ring-mean | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.069 |
| M5.C3 ring-mean | full | typical+gain1.0dB | 1.000 | 0.767 | 0.106 | 0.686 |
| M5.C3 ring-mean | full | typical+gain2.0dB | 1.000 | 0.000 | 0.500 | 0.956 |
| M5.C3 ring-mean | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 ring-mean | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain1.0dB | 0.933 | 0.867 | 0.092 | 0.000 |
| M5.C3 ring-mean | gain_invariant | typical+gain2.0dB | 0.533 | 0.728 | 0.278 | 0.000 |
| M5.C3 vote(6 views) | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 vote(6 views) | full | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 vote(6 views) | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.069 |
| M5.C3 vote(6 views) | full | typical+gain1.0dB | 0.981 | 0.722 | 0.106 | 0.686 |
| M5.C3 vote(6 views) | full | typical+gain2.0dB | 1.000 | 0.222 | 0.458 | 0.956 |
| M5.C3 vote(6 views) | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.C3 vote(6 views) | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain1.0dB | 0.909 | 0.874 | 0.081 | 0.000 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain2.0dB | 0.470 | 0.837 | 0.192 | 0.000 |
| M5.R31 | full | noisy | n/a | n/a | n/a | 1.000 |
| M5.R31 | full | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.069 |
| M5.R31 | full | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.686 |
| M5.R31 | full | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.956 |
| M5.R31 | gain_invariant | noisy | n/a | n/a | n/a | 1.000 |
| M5.R31 | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.000 |
| M5.R31 | gain_invariant | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.000 |

τ and m per profile:

| feature | profile | tau_dB | tau_CI_lo | tau_CI_hi | tau_screen_dB | margin_dB | sd_ref_dB |
|---|---|---|---|---|---|---|---|
| M5.C3 | good | -52.857 | -53.009 | -52.681 | -52.857 | 0.237 | 0.451 |
| M5.C3 | ideal | -52.770 | -53.036 | -52.763 | -52.770 | 0.239 | 0.455 |
| M5.C3 | noisy | -52.662 | -52.865 | -52.555 | -52.734 | 0.267 | 0.509 |
| M5.C3 | typical | -52.785 | -53.012 | -52.727 | -52.785 | 0.237 | 0.451 |
| M5.C3 | typical+gain0.5dB | -52.695 | -52.909 | -52.652 | -52.980 | 0.322 | 0.614 |
| M5.C3 | typical+gain1.0dB | -52.735 | -52.822 | -52.589 | -53.659 | 0.496 | 0.946 |
| M5.C3 | typical+gain2.0dB | -53.287 | -53.512 | -52.416 | -55.096 | 1.313 | 1.683 |
| M5.C3 | typical_jitter | -52.778 | -52.861 | -52.635 | -52.778 | 0.236 | 0.450 |
| M5.C3 | very_noisy | -50.894 | -50.955 | -50.780 | -51.216 | 0.340 | 0.649 |
| M5.R31 | good | -15.159 | -15.485 | -15.158 | -15.488 | 0.055 | 0.011 |
| M5.R31 | ideal | -15.163 | -15.492 | -15.163 | -15.502 | 0.058 | 0.004 |
| M5.R31 | noisy | -15.094 | -15.445 | -15.088 | -15.313 | 0.051 | 0.097 |
| M5.R31 | typical | -15.171 | -15.483 | -15.159 | -15.482 | 0.055 | 0.032 |
| M5.R31 | typical+gain0.5dB | -15.164 | -15.485 | -15.155 | -15.473 | 0.058 | 0.030 |
| M5.R31 | typical+gain1.0dB | -15.153 | -15.488 | -15.143 | -15.453 | 0.057 | 0.030 |
| M5.R31 | typical+gain2.0dB | -15.158 | -15.490 | -15.152 | -15.458 | 0.057 | 0.033 |
| M5.R31 | typical_jitter | -15.164 | -15.485 | -15.157 | -15.471 | 0.054 | 0.032 |
| M5.R31 | very_noisy | -13.634 | -13.775 | -13.547 | -13.639 | 0.136 | 0.259 |

No thresholds are given for 3-class schemes: they are unverified against mesh noise.