# Blind reconstruction: Test_B (`new_with_slices_Test_B.s6p`)

Protocol `results/imaging2/BLIND_PROTOCOL.md`; code d83d1d5; training = all 9 lobe files; surrogate tm0 / lambda 0.001; ell 15; grid: native grid contains the common grid (no resampling); glitch-masked points 3. **No truth used.**

## standard_H6 (PRIMARY; reference new_with_slices_Healthy_sliced_new.s6p; gain-free False)

- stage (MAP): **Mild**, P = 1.000 (all: Healthy 0.000, Mild 1.000, Moderate 0.000, Severe 0.000)
- fit χ²/dof = 0.46 → **OK** (likelihood tempered ×1.00)
- affected lobes: S2 TL, S5 PR; side: left and right; neither front nor back

| sector | P(affected) | ê median (mm) | 90% interval (mm) |
|---|---|---|---|
| S1 Fr | 0.00 | 0.0 | 0.0–0.0 |
| S2 TL | 1.00 | 13.0 | 7.0–21.5 |
| S3 PL | 0.00 | 0.0 | 0.0–0.0 |
| S4 Oc | 0.00 | 0.0 | 0.0–0.0 |
| S5 PR | 1.00 | 7.0 | 6.5–12.5 |
| S6 TR | 0.00 | 0.0 | 0.0–0.0 |

## gainfree_H6 (secondary; reference new_with_slices_Healthy_sliced_new.s6p; gain-free True)

- stage (MAP): **Mild**, P = 1.000 (all: Healthy 0.000, Mild 1.000, Moderate 0.000, Severe 0.000)
- fit χ²/dof = 0.77 → **OK** (likelihood tempered ×1.00)
- affected lobes: S2 TL, S5 PR; side: left and right; neither front nor back

| sector | P(affected) | ê median (mm) | 90% interval (mm) |
|---|---|---|---|
| S1 Fr | 0.00 | 0.0 | 0.0–0.0 |
| S2 TL | 1.00 | 6.5 | 6.0–11.5 |
| S3 PL | 0.00 | 0.0 | 0.0–0.0 |
| S4 Oc | 0.00 | 0.0 | 0.0–0.0 |
| S5 PR | 1.00 | 6.0 | 6.0–6.5 |
| S6 TR | 0.00 | 0.0 | 0.0–0.0 |

## standard_H7 (secondary; reference new_with_slices_Healthy_sliced.s6p; gain-free False)

- stage (MAP): **Mild**, P = 1.000 (all: Healthy 0.000, Mild 1.000, Moderate 0.000, Severe 0.000)
- fit χ²/dof = 0.42 → **OK** (likelihood tempered ×1.00)
- affected lobes: S2 TL, S5 PR; side: left and right; neither front nor back

| sector | P(affected) | ê median (mm) | 90% interval (mm) |
|---|---|---|---|
| S1 Fr | 0.00 | 0.0 | 0.0–0.0 |
| S2 TL | 1.00 | 3.5 | 3.0–9.0 |
| S3 PL | 0.00 | 0.0 | 0.0–0.0 |
| S4 Oc | 0.00 | 0.0 | 0.0–0.0 |
| S5 PR | 1.00 | 7.5 | 7.0–17.5 |
| S6 TR | 0.00 | 0.0 | 0.0–0.0 |
