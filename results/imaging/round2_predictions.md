# Round-2 predictions (imaging session), written before the round-2 computations

Committed before `imaging/lobe_round2.py` computes R3, C4 or the C6 design. Not edited afterwards.

**Honesty note.** R3 and C4 concern the LeftOnly phase asymmetry, and its measured value is already known from
round 1: T2–T3 minus T5–T6 phase is about −5° to −6° at 3.30–3.65 GHz and about 0 at 3.70–3.85 GHz; the
whitened (gain-invariant) log LR is +9.27 against +8.48 for Tikhonov dS. Those predictions are therefore
consistency checks, not blind tests. Only C6 is blind.

## C4. Physical sign and size of the phase change (ray-share estimate)

Complex refractive index n = sqrt(εr − jσ/(ωε0)) at 3.6 GHz (Shehab Table 5 values as in `imaging/common.py`):
gray 6.96 − 0.87j, CSF_Mild 7.61 − 1.61j, gray_Mild 6.64 − 1.96j, white 5.98 − 0.69j, white_Mild 5.73 − 1.04j.
Double radial pass, HFSS e^{jωt} convention, Δφ = −2 k0 Re(Δn) d:
- gray → CSF_Mild over e = 7.5 mm (S2): −42°; over e = 11.5 mm (S3): −64° (phase delay).
- gray → gray_Mild over 7 mm: +19°; white → white_Mild per 10 mm: +22° (phase advance).

Sensitivity shares of path T2–T3 at 3.6 GHz, from the healthy-head kernels (fraction of Σ|kernel| in the head):
S2 gap 0.24, S2 gray 0.11, S2 white 0.12; S3 gap 0.32, S3 gray 0.08, S3 white 0.09. Mirror path T5–T6: ≤ 0.001
in S2/S3. Share-weighted estimate: 0.24·(−42) + 0.32·(−64) + 0.19·(+19) + 0.21·(+22) ≈ −22°.

**Prediction C4:** the T2–T3 phase change is negative (delay), because the CSF gap under the left antennas
dominates the sensitivity. Its size is −5° to −25°; the ray-share estimate overestimates, because it treats the
gap as traversed radially twice. The antisymmetric part (T2–T3 minus T5–T6) has the same sign. A positive sign
would contradict the propagation picture.

## R3. Detuning hypothesis

Hypothesis H_det: CSF under the left antennas detunes them, and the transmission phase asymmetry is mostly that
detuning (a per-antenna factor), not propagation through the lobe.

Predictions written now (the whitened log result above already argues against H_det):
1. **Resonance.** Of the four lateral antennas, only T2 and T3 shift their reflection resonance (min |S_ii|) by
   more than the one-pass mesh change of that resonance. T5 and T6 do not.
2. **Per-port model.** The fit Δln S_ab ≈ g_a + g_b (one complex factor per antenna per frequency) explains less
   than 30 % of the energy of the mirror-antisymmetric part of the transmission log-changes at 3.4 and 3.6 GHz.
   If it explains more than 70 %, H_det is supported.
3. **Reflection product.** ½(Δln S_aa + Δln S_bb) predicts the T2–T3 minus T5–T6 phase difference with the
   right sign but less than half its size.

If 2 and 3 hold, the asymmetry is not per-antenna detuning. "Localisation" would then still be limited to the
sensitivity volume of the left paths, which is mostly the outer 8–10 mm (gap share ≈ 0.56 for T2–T3).

## C6. Proposed blind design: RightOnly_test (mirror of LeftOnly_test)

- e = 0 / 0 / 0 / 0 / 11.5 / 7.5 mm (S5 parietal R 11.5, S6 temporal R 7.5), r_hip 17.5 mm, Mild materials in
  S5, S6 and hippocampus, CSF_Mild (one object, everywhere), Healthy_sliced geometry otherwise.
- Stop rule 1 (first pass with ΔS < 0.02, 1 converged pass), the same as LeftOnly_test_c3 and
  Healthy_sliced_new.
- Why this design: the leading alternative explanation of the LeftOnly asymmetry is numerical (mesh) asymmetry
  of that one file. A mirrored design gets an independent mesh. A true lobe signal must flip sign. Mesh
  asymmetry has no reason to flip with the design.

**Imaging predictions** (frozen pipeline, `lobe_frozen.json`; derived from round-1 LeftOnly numbers:
LR_anti = +7.86, LR_sum/2 = +0.62 with H7 and +0.96 with H6):
1. LR(RightOnly − Healthy_sliced_new), Tikhonov dS = −6.9 ± 3.9 (envelope = largest |null| LR of the
   symmetric designs). Sign negative.
2. Asymmetry-free LR_anti(RightOnly) = −7.9 ± 3.9. The mirror-pair average (LR_anti(Left) − LR_anti(Right))/2
   = +7.9; its error is reduced only if the two meshes' asymmetries are independent.
3. More than 70 % of LR comes from phase (round 1: 85 %); amplitude contributes less than 2 in absolute value.
4. The phase difference T5–T6 minus T2–T3 at 3.4–3.6 GHz is about −5° (mirror of LeftOnly) and ≈ 0 at
   3.70–3.85 GHz.
5. Sector calls (frozen T_abs) are not predicted beyond "S5 and/or S6 highest": round 1 showed the calls depend
   on reference and calibration.

**Decision rule, fixed now:** the phase finding is replicated if prediction 1 has the right sign and
|LR| ≥ 2 × (largest |null| LR of the symmetric designs), and prediction 4 has the right sign at both 3.4 and
3.6 GHz. It fails if LR has the wrong sign, or |LR| < largest |null|.
