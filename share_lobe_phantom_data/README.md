# Lobe-sector head phantom: simulated S-parameters (HFSS)

Six simulated microwave measurements of a layered spherical head phantom in which Alzheimer's-type
atrophy is applied lobe by lobe. Six antennas on a ring around the upper head; one Touchstone file per
design. Simulation data only (Ansys HFSS 2024.2), one idealised head.

Contact: Jatin, IIT Bombay (Dual Degree Project, supervisor Prof. Anirban Sarkar).

## Files

| File | Design | What changes vs healthy |
|---|---|---|
| `lobe_Healthy.s6p` | Healthy | reference |
| `lobe_MCI.s6p` | MCI | hippocampus only (radius 25 → 21.25 mm, MCI material) |
| `lobe_Mild.s6p` | Mild AD | temporal + parietal lobes, both sides |
| `lobe_Moderate.s6p` | Moderate AD | frontal + temporal + parietal lobes |
| `lobe_Severe.s6p` | Severe AD | all six lobes |
| `lobe_LeftOnly.s6p` | Test design | left temporal + left parietal only (Mild level) |

`lobe_phantom_geometry.png`: top views of the five designs (not MCI) with the CSF expansion per lobe.

Format: Touchstone v1, 6 ports, `# GHz S MA R 50` (magnitude, phase in degrees, 50 Ω), 3.2–4.2 GHz in
5 MHz steps (201 points). The header lists every geometry variable of the design (e_S1…e_S6, r_hip, layer
radii). Some header variables are unused leftovers (r_brain, r_csf, r_gray, r_white, r_brain_ad,
r_csf_inner, r_csf_expanded, ant_dist): ignore them; the geometry below is what was simulated.

## Coordinates and antennas

- Origin = head centre, units mm. **+z up, nose toward −y, +x = subject's left.**
- Six DGS-patch antennas (42 × 35 mm, Rogers RT/duroid 6010, εr ≈ 10.2, 1.575 mm) with a 3 × 3 FR4 AMC
  reflector behind each; patch side faces the head. Feeds 97.7 mm from the origin at polar angle 60.5°
  (z ≈ 48 mm), 60° apart, about 9 mm from the skin. The antennas cover z ≈ 44–78 mm (upper head).
- Antenna azimuths: T1 −90° (front, nose), T2 −30°, T3 +30°, T4 +90° (back), T5 +150°, T6 −150°.
  T2 and T3 are on the subject's left, T5 and T6 on the right.
- **Port order in the files: Port 1..6 = T4, T3, T2, T1, T6, T5** (not T1..T6). Verified from the HFSS
  port-sheet positions and field exports.

## Head geometry (all designs)

Concentric layers, outer radius in mm: skin 88, fat 87.5, skull 86.5, CSF 83.5 (a solid sphere filling
every gap inside it), gray matter 83 − eₖ, white matter 76 − eₖ, hippocampus r_hip (central sphere).
White matter has a fixed 25 mm central hole; the gap between the hippocampus and 25 mm is CSF.

Gray and white matter are cut into six full-height 60° azimuthal sectors, each centred on one antenna:

| Sector | Azimuth range | Lobe | Antenna |
|---|---|---|---|
| S1 | −120° to −60° | Frontal | T1 |
| S2 | −60° to 0° | Temporal, left | T2 |
| S3 | 0° to 60° | Parietal, left | T3 |
| S4 | 60° to 120° | Occipital | T4 |
| S5 | 120° to 180° | Parietal, right | T5 |
| S6 | 180° to 240° | Temporal, right | T6 |

In sector k the cortex retreats by eₖ (CSF expansion): gray matter spans 76 − eₖ to 83 − eₖ mm, white
matter 25 to 76 − eₖ mm, and CSF fills 83 − eₖ to 83.5 mm.

| Design | e_S1 | e_S2 | e_S3 | e_S4 | e_S5 | e_S6 | r_hip |
|---|---|---|---|---|---|---|---|
| Healthy | 0 | 0 | 0 | 0 | 0 | 0 | 25 |
| MCI | 0 | 0 | 0 | 0 | 0 | 0 | 21.25 |
| Mild | 0 | 7.5 | 11.5 | 0 | 11.5 | 7.5 | 17.5 |
| Moderate | 11.5 | 12.5 | 15.5 | 0 | 15.5 | 12.5 | 12.5 |
| Severe | 15.5 | 17.5 | 18 | 11.5 | 18 | 17.5 | 7.5 |
| LeftOnly | 0 | 7.5 | 11.5 | 0 | 0 | 0 | 17.5 |

Stage values and lobe order follow Shehab et al. 2025 (Tables 5–7) and Saied et al. 2022 (Table II).

## Materials (relative permittivity εr / conductivity σ in S/m, constant over frequency)

| Tissue | Healthy | Mild | Moderate | Severe |
|---|---|---|---|---|
| Gray matter | 47.7 / 2.42 | 40.3 / 5.203 | 39.11 / 5.687 | 38.39 / 5.92 |
| White matter | 35.3 / 1.65 | 31.77 / 2.39 | 31.064 / 2.722 | 30.35 / 2.88 |
| Hippocampus | 47.7 / 2.42 | 39.11 / 5.687 | 38.39 / 5.92 | 37.2 / 6.413 |
| CSF | 65 / 4.27 | 55.25 / 4.91 | 48.75 / 5.337 | 32.5 / 6.405 |

MCI hippocampus: 40.3 / 5.203. Values from Shehab et al. 2025 Table 5 (healthy values match Gabriel
tissue data at about 3.24 GHz), held constant across 3.2–4.2 GHz, loss tangent 0. In a diseased design,
only the affected sectors get the stage's gray/white matter; the hippocampus gets the stage value; CSF
is one connected object, so the stage's CSF material applies everywhere (including the healthy side of
LeftOnly; MCI keeps healthy CSF). Skin, fat and skull are identical in all designs.

## Simulation settings

HFSS driven terminal, lumped 50 Ω ports, radiation boundary. Adaptive meshing at 3.4 GHz until the
maximum |ΔS| between passes is below 0.02 (6 passes for Healthy, MCI and LeftOnly; 5 for Mild, Moderate,
Severe). Interpolating sweep 3.2–4.2 GHz, 201 points, converged.

## Things to know before using the data

- **Symmetry.** Healthy and MCI are rotationally symmetric; Mild, Moderate and Severe are mirror-symmetric
  about the y axis (left = right). Only LeftOnly is asymmetric. Small port-to-port differences within a
  symmetric file are numerical, not signal.
- **Sweep glitches.** Single non-reciprocal points (|Sij| ≠ |Sji|) occur on weak paths; mask or
  interpolate them: LeftOnly, ports 2–5 (T3–T6) at 3.850 GHz; Severe, ports 2–5 (T3–T6) at 3.845 GHz.
- **Weak paths.** Second-neighbour and opposite transmissions are −50 to −75 dB; treat them accordingly.
- **Sensitivity.** Most of each path's sensitivity is in air and in the outer ~1–1.5 cm of the head near
  the ring; the hippocampus (MCI) is essentially invisible to this array.
- **Scope.** One idealised head, one simulation per design: suitable for method development, not for
  claims about real patients.
