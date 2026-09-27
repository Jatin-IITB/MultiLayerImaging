# Track A — running summary

**Standing caveats**

- One simulation per stage, so results show noise robustness only, not generalisation to
  new heads.
- The between-mesh noise floor has not been measured yet. All AD-vs-AD comparisons are
  **unverified against mesh noise**.
- Headline scheme: `binary` (Normal vs AD).

## Prompt 02 — power-based metrics, frequency robustness, separability (code `7ca77f1`; report regenerated at `4962836`)

Details are in `results/02/report.md`, the tables in `results/02/*.csv`, and the figures in
`results/figures/02_*.png`. `metrics.csv` gained 1494 rows: 83 scalar metrics × 6 noise
profiles × 3 schemes, classifier `none-fisher`, 500 noisy realisations per simulation.

**Data handling changes**

- **Glitch masking is on** (`qc.mask_glitches`). 26 in-band (f, pair) points in 7 runs
  were replaced by linear interpolation, and each is logged in
  `results/qc/masked_points.csv`. Detection rule: |Sij − Sji| > −30 dB relative to the
  pair's band-RMS. Moderate has none.
- **Grid rule.** The grid is set to the coarsest step among the files, currently 5 MHz. Finer
  files are downsampled onto it; upsampling raises an error.

**Definitions used in the tables**

- J_meas: Fisher ratio under measurement noise. This is the ranking key the brief asked for.
- J_eff: Fisher ratio that also counts the port-to-port asymmetry as noise.
- gap/port: class gap divided by the port-to-port spread.
- gap/mesh: pending until the mesh-repeat runs arrive.

**Ranking at `typical` noise**

| Scheme | Best metric | J_meas | J_eff | gap/port | Weakest pair | Frequency-robust |
|---|---|---|---|---|---|---|
| binary | M5.C3[k3], opposite-antenna power in 3.35–3.60 GHz | 775 | 17.9 | 6.1 | Normal\|AD | **yes** (shift 0.03, keeps 94% of the class gap under band change) |
| binary | M5.C3, same, full band | 548 | 13.0 | 5.2 | Normal\|AD | shift yes (0.009); band value no (0.25–0.3) |
| binary | M0, old score | 45 | 16.9 | 7.3 | Normal\|AD | no (band change moves it 3–4× the gap; keeps 76% of the gap) |
| binary | M2.R, power-averaged reflection | 12 | 4.2 | 3.5 | Normal\|AD | no (keeps 36% of the gap under band change) |
| binary | M1, dB-averaged Sii | 0.27 | 0.02 | 0.19 | Normal\|AD | no |
| three_merged | M7.D3[k3], differential energy on opposite path | 165 | 4.2 | 2.9 | Mild+Mod\|Severe | no (shift 2.3) |
| three | M7.D3[k3] | 588 | 5.0 | 3.2 | Mild\|Severe | no (shift 2.3) |
| three | M6.A[3.40], accepted power in the 3.40–3.45 GHz sub-band | 133 | 4.1 | 2.9 | Mild\|Severe | no (shift 0.38) |

**Findings**

1. **Binary staging is robust.** M5.C3[k3] keeps J_eff ≥ 17 from `ideal` through `noisy`
   noise, and J_eff = 10 at `very_noisy`.
2. **No 3-class metric meets the brief's frequency-robust criterion.** All the 3-class winners
   move by more than 0.25 of the smallest class gap under a ±10 MHz resonance shift. Their
   weakest pair (AD vs AD) is only 2–3× the port noise and has not been checked against
   mesh noise.
3. **Ordinality is weak.** Only 31 of 83 metrics are monotone over Normal < Mild <
   Moderate < Severe.
   - Every metric has a large Normal → Mild step, 2–7× the port noise.
   - Mild → Moderate is within ±1.3× the port noise.
   - Moderate → Severe is 0.2–3.7×.
   - The two large steps are the ones that cross HFSS projects. The one same-project step is
     tiny. Physics can explain this, since CSF permittivity drops from 48.75 to 32.5 at
     Severe, but a mesh confound would produce the same pattern. The mesh-repeat runs are
     needed.
4. **M0 is in practice a reflection-only score.** Zeroing every Sij changes it by less than
   0.5%. It separates Normal from AD at a fixed band, but it depends heavily on the chosen
   band and on a single failed antenna (one open port moves it 8.6× the Normal–Mild gap),
   and it gives no usable AD-vs-AD separation (J_eff ≤ 0.7).

**Power vs dB averaging**

- Mean |Sii| in dB (M1) against power-averaged |Sii|² (M2): at `typical` noise, J is 46×
  higher with power averaging (binary), 5× (`three_merged`) and 13× (`three`). With
  frequency jitter the factor is 37–220×. A resonance shift moves the dB average 8× more.
  - Why: the dB average is dominated by the notch (−30 to −49 dB), which is
    mesh-sensitive.
- Mismatch loss, computed as the dB of the power average versus the band average of dB
  values: power is 17× better at `typical`.
- For the k=3 coupling the two are similar in binary (1.6×).

**The "which frequency?" answer**

- **The resonance itself carries no information.** The 3.60–3.65 GHz sub-band has
  J ≤ 0.07 in every scheme (`02_subbands.png`). The information sits in the 3.40–3.60 GHz
  shoulder and in opposite-antenna transmission.
- **Band-averaged power avoids picking a frequency.** Metrics that don't use Sii (M5) are
  unaffected when the notch is flattened.
- **Shifts.** Metrics that do not track the resonance survive ±10 MHz shifts: M5.C3 moves
  under 0.03 of the gap. Resonance-tracking metrics fail: M6.fc moves 0.9 of the Normal–Mild
  gap per 2 MHz.
- **Faults.** Open or short on all antennas pushes every metric out of the class range, or
  makes it undefined (mismatch loss), so the gate can catch it. **A single open antenna
  is the risk:** it shifts the C3 ring mean by 0.7–0.84 of the gap and stays inside the class
  range. The per-antenna reflection gate in prompt 03 must catch this.

**Caveats**

- The k3 window (3.35–3.60 GHz) was chosen by looking at these same four simulations, so it
  is optimistic. Full-band M5.C3 gives similar numbers (J_eff 13).
- In a symmetric ring, SVD features (M8.s_k) duplicate the modal features, and they have
  no per-antenna port-noise estimate.
- M3's accepted power ⟨A⟩ is an exact affine copy of M2.

## Prompt 01A — data loading and QC

Details: `MODEL_CARD.md` Part 2, `results/qc/qc_report.md`.

- **Parsing.** All 4 files parse as 6-port `GHz S MA R 50`. They are reciprocal to −76…−82 dB
  (median, relative to band-RMS) and passive (σ_max ≤ 0.982).
- **Common grid.** 3.2–4.2 GHz, 201 points at 5 MHz. The 2.8–3.2 GHz range is lost because
  Severe starts at 3.2 GHz.
- **Glitches.** Non-reciprocal frequency bumps on single antenna pairs look like sweep
  artefacts. They are now masked (see Prompt 02).
- **Port mapping.** The data support the card's port→antenna mapping: it ranks 1 of 60
  ring orderings in every file.
- **Symmetry noise floor.** Measured as |S| spread across equivalent pairs, max − min,
  median over frequency:
  - k=0: 0.13–0.32 dB
  - k=1: 0.6–1.1 dB
  - k=2: 1.1–1.6 dB
  - k=3: 0.4–1.0 dB
- **Confound.** Normal is the outlier, 1.4–5× the port noise, whether the comparison file
  comes from the same project or the other one. This is no evidence that the project
  effect dominates. The AD stages differ from each other by only 0.5–2× the port noise.
