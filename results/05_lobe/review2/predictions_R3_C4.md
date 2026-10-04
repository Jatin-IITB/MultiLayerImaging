# Predictions written before the round-2 computations (R3 detuning, C4 phase sign and size, C4 band dependence)

Written on 2026-10-04, before `scripts/11_review2.py` and `scripts/12_review2_fields.py` were run. Committed with the
code. Status of the phase finding: **post hoc** (round 1, after unblinding).

## C4. Sign and size of the phase change from CSF replacing gray matter (first principles)
- HFSS uses e^{+jωt}, so a transmitted wave carries e^{−jkL}. A higher refractive index along the path makes the phase
  of S **more negative**.
- LeftOnly replaces healthy gray matter (εr 47.7, n = 6.907) by CSF_Mild (εr 55.25, n = 7.433) over e = 7.5 mm in
  S2 and 11.5 mm in S3: Δn = **+0.526**. At f = 3.475 GHz (k0 = 72.8 rad/m), a wave crossing the whole gap once would
  change phase by −k0·Δn·d = **−16.5° (S2), −25.2° (S3)**.
- The remaining S2/S3 gray and white matter become Mild materials, with lower index (gray Δn = −0.559 over 7 mm, white
  Δn = −0.305). That pushes the other way (more positive phase), with a smaller sensitivity share because it is
  deeper.
- **Prediction:** left-side paths (both ends on T1–T4, at least one end on T2/T3) get a **negative** phase change of
  size ≈ share × 16–25°. "Share" is the fraction of that path's Born sensitivity |E_a·E_b| lying in the changed gap
  volume, computed from the healthy volume field exports (not from any LeftOnly data). Reaching the observed −4 to −6°
  would need a share of roughly 0.2–0.35. If the share is ≲ 0.05, the CSF-gap propagation mechanism cannot produce
  the observed size, and something else (antenna loading/detuning) must.
- Right-side paths: CSF_Mild also replaces CSF_Healthy (εr 65 → 55.25, Δn = −0.63) in the 0.5 mm layer everywhere.
  That gives a small **positive** phase change everywhere (share × −k0·Δn·0.5 mm = share × +1.3°).

## C4. Band dependence
- Pure propagation: Δφ ∝ f, so the left asymmetry should be about 27% larger at 4.2 GHz than at 3.3 GHz, and should
  not vanish anywhere in the band.
- If the asymmetry vanishes or changes sign near the antenna resonance (≈ 3.62–3.66 GHz) or near transmission
  notches, that points to a resonance/notch artefact or antenna detuning, not propagation.

## R3. Detuning hypothesis
- **Near-field loading:** under T2/T3 the medium 5–16.5 mm below the skin gets a higher permittivity (55.25 vs 47.7),
  so the left antennas' effective loading permittivity rises.
- **Prediction 1:** the reflection resonance of T2 and T3 shifts **down** relative to T5 and T6, by ≲ 5 MHz (the
  patch near field decays within a few mm and the change starts ≥ 5 mm below the skin). The depth of the |Sii|
  minimum changes by ≲ 1 dB.
- **Prediction 2:** a purely per-antenna (separable) effect, S_ab → S_ab·t_a·t_b, cancels exactly in complex
  cross-ratios. Round 1 found the left-right asymmetry in exactly those cross-ratios (16/22 combinations). So, if that
  finding is real, the separable (per-antenna) part should explain **less than half** of LeftOnly's left-right
  transmission phase asymmetry. The per-antenna terms of T2/T3 should track their reflection changes.
- **Decision:** if the separable part explains ≥ 80% of the left-right phase asymmetry, and the cross-ratio asymmetry
  does not survive the round-2 floor rule (R1c), then "localisation" here means "which antenna sits over a change",
  with depth ≈ the antenna near field, and that will be said plainly.
