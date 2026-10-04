# RightOnly_test scored against the committed prediction (0ceb626) — new_with_slices_RightOnly_test.s6p

Scored at code `595e9cb-dirty` with the frozen pipeline (`lobe_frozen.json`, frozen at `fb5b775`).

**Verdict (committed rule): REPLICATED.** Primary: LR = -9.44 (predicted -6.9 ± 3.9); replication bar |LR| ≥ 7.8 with negative sign; fail if positive or |LR| < 3.9. Prediction 4 (T5–T6 minus T2–T3 phase change, deg): 3.4 GHz -7.3, 3.6 GHz -3.9 → negative at both; 3.70–3.85 GHz -2.8, -3.2, -1.4, -1.1.
Prediction 3 (> 70 % of LR from phase; amplitude part below 2 in absolute value): phase part -7.79 of -9.44, amplitude part -1.62.

| reference | method | LR | LR_anti | LR_amp_part | LR_phase_part | S1 | S2 | S3 | S4 | S5 | S6 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Healthy_sliced_new | Tikhonov dS | -9.44 | -10.15 | -1.62 | -7.79 | +8.54 | +7.03 | +7.36 | +7.00 | +13.92 | +19.35 |
| Healthy_sliced_new | frozen log | -10.77 | -11.20 | -1.61 | -9.16 | +7.60 | +4.70 | +6.65 | +6.30 | +14.08 | +18.81 |
| Healthy_sliced_new | whitened log | -10.26 | -10.71 | -1.93 | -8.32 | +6.35 | +3.84 | +5.92 | +5.20 | +13.37 | +16.90 |
| Healthy_sliced | Tikhonov dS | -9.83 | -10.17 | -1.45 | -8.26 | +10.71 | +8.99 | +10.06 | +9.21 | +16.37 | +22.34 |
| Healthy_sliced | frozen log | -11.02 | -11.09 | -1.52 | -9.49 | +9.32 | +5.76 | +8.58 | +7.66 | +15.69 | +20.69 |
| Healthy_sliced | whitened log | -10.18 | -10.58 | -1.69 | -8.49 | +7.70 | +4.92 | +7.65 | +6.36 | +14.62 | +18.32 |

POST-HOC context, not part of the rule: LeftOnly_test_c3 gave LR +8.82 (vs Healthy_sliced_new), LR_anti +7.86, 85 % phase. The mirror-pair average (LR_anti(Left) − LR_anti(Right)) / 2 is worth reporting, but it reduces mesh error only if the two meshes' asymmetries are independent.
