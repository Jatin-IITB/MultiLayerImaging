# Model card — Track A: 7-layer concentric sphere + 6-antenna ring (HFSS)

Part 1 records the facts as supplied by the user (prompt 01A). Part 2 records what was
checked against the data, by `scripts/00_qc.py` (full tables in `results/qc/qc_report.md`).

**Header policy.** Touchstone comment headers (design and project names, variables,
`Port[k]` labels, port impedances) are **not trusted** and are not parsed. The user
instructed this on 2026-09-27. The parser uses only two things to decode the numbers: the
option line and the port count from the extension. Both are then checked for plausibility
against the data.

- Labels come from `data/sims.csv`.
- The port→antenna mapping comes from `config.yaml`.
- Geometry and materials come from this card.

---

## Part 1 — Supplied facts

### Phantom geometry (concentric spheres centred at the origin; outer radius, mm)

| Layer (outer → inner) | Normal | MCI | Mild | Moderate | Severe | Notes |
|---|---|---|---|---|---|---|
| Skin | 88 | 88 | 88 | 88 | 88 | fixed |
| Fat | 87.5 | 87.5 | 87.5 | 87.5 | 87.5 | fixed |
| Skull | 86.5 | 86.5 | 86.5 | 86.5 | 86.5 | fixed |
| CSF (outer boundary) | 83.5 | 83.5 | 83.5 | 83.5 | 83.5 | fixed outer boundary |
| Gray matter | 83 | 83 | 70.55 | 66.05 | 62.25 | shrinks (Shehab Table 6) |
| White matter | 76 | 76 | 64.6 | 60.8 | 57 | shrinks |
| Hippocampus (central sphere) | 25 | 21.25 | 17.5 | 12.5 | 7.5 | shrinks 15/30/50/70 % |

- **CSF grows as gray matter shrinks.** The CSF outer boundary is fixed, so CSF thickness
  goes from 0.5 mm (Normal) to 21.25 mm (Severe). This is ex-vacuo expansion; there is no
  separate variable for it.
- **The hippocampus is a central sphere.** This is a deliberate simplification.
- **Every disease change is radially uniform.** The whole phantom is spherically symmetric.

### Materials (static εr / σ [S/m], frequency-independent in HFSS)

Stage values are from Shehab et al. 2025, Table 5 (3.241 GHz). Skin, fat and skull are
fixed across stages, but their values are not given here (see Part 2).

| Tissue | Normal* | Mild | Moderate | Severe |
|---|---|---|---|---|
| Hippocampus | 47.7 / 2.42 | 39.11 / 5.687 | 38.39 / 5.92 | 37.2 / 6.413 |
| White matter | 35.3 / 1.65 | 31.77 / 2.39 | 31.064 / 2.722 | 30.35 / 2.88 |
| Gray matter | 47.7 / 2.42 | 40.3 / 5.203 | 39.11 / 5.687 | 38.39 / 5.92 |
| CSF | 65 / 4.27 | 55.25 / 4.91 | 48.75 / 5.337 | 32.5 / 6.405 |

\*Normal values are back-calculated from the paper's % change columns.

Several values coincide on purpose:

- Hippocampus_Mild ≡ GrayMatter_Moderate
- Hippocampus_Moderate ≡ GrayMatter_Severe
- Hippocampus ≡ Gray matter at Normal

**Modelling caveat:** the materials are static, so tissue dispersion is not simulated.
Anything F1 assumes about frequency dependence must match the simulation (constant εr and
σ), not real tissue.

### Antennas and ring

- **Antennas:** six identical DGS patch antennas with an AMC reflector. In-situ resonance is
  about 3.62 GHz.
- **Design variables** (card): L = 42 mm, W = 35 mm, $L = 85 mm, $W = 35 mm, H = 1.575 mm,
  slot_distance = 15 mm, ant_dist = 115 mm, z_ebg = −94.575 mm.
- **Ring:** uniform, 60° azimuthal spacing. The feed points sit 97.55 mm from the origin at
  a polar angle of 60.5°.
- **Settled by the HFSS field exports** (Part 4; imaging report §4):
  - The ring is at **+z** (upper hemisphere), at a polar angle of 60.5°.
  - **T1 is at azimuth −90°.** T1…T6 are consecutive in steps of **+60°**, so T4 is at +90°
    and the T1–T4 plane is x = 0.
  - The antenna near field is mixed, about **65% θ / 35% φ** polarised.
  - The antennas' fields match each other's rotated copies to **11–16% rms**. **T1 and T4
    are about 4% stronger** than the other four.
- **Excitation:** HFSS Driven Terminal, lumped 50 Ω ports, radiation boundary box.

### Port mapping (card)

`Port[1..6] = T4, T3, T2, T1, T6, T5` → `config.yaml: ring.port_to_ant = [4, 3, 2, 1, 6, 5]`.

### Data files — current set v2 (added 2026-10-01)

All five stages re-solved in **one** HFSS project (user-stated: "corrected, same project"),
including a new MCI case. Parsed and checked in Part 3.

| File | Class | HFSS project | Native band | Points |
|---|---|---|---|---|
| `new_Healthy.s6p` | Normal | `new` | 2.8–4.2 GHz | 281 (5 MHz) |
| `new_MCI.s6p` | MCI | `new` | 2.8–4.2 GHz | 281 (5 MHz) |
| `new_MildAD.s6p` | Mild | `new` | 2.8–4.2 GHz | 281 (5 MHz) |
| `new_ModerateAD.s6p` | Moderate | `new` | 2.8–4.2 GHz | 281 (5 MHz) |
| `new_SevereAD.s6p` | Severe | `new` | 2.8–4.2 GHz | 281 (5 MHz) |

**Archived set v1** (`data/archive/v1_mixed_projects/`, used for all results up to commit
e9bced0): the four files below. Normal and Severe came from project `new`, Mild and Moderate
from `Brain_sevem_layer`, and Severe covered only 3.2–4.2 GHz.

| File | Class | HFSS project (card) | Native band | Points |
|---|---|---|---|---|
| `brain_sevem_layer_Healthy.s6p` | Normal | `new` | 2.8–4.2 GHz | 281 (5 MHz) |
| `Brain_sevem_layer_MildAD.s6p` | Mild | `Brain_sevem_layer` | 2.8–4.2 GHz | 281 (5 MHz) |
| `Brain_sevem_layer_ModerateAD.s6p` | Moderate | `Brain_sevem_layer` | 2.8–4.2 GHz | 281 (5 MHz) |
| `brain_sevem_layer_SevereAD.s6p` | Severe | `new` | 3.2–4.2 GHz | 501 (2 MHz) |

### Standing caveats (carry into every report)

1. **Symmetry.** S should be circulant. Port-to-port differences within a file are numerical
   noise: use them as a noise estimate, never as a signal. Spatial localisation is
   impossible in this track.
2. **Project confound.** Resolved in v2 (all stages in one project). It applied to v1.
3. **One simulation per class.** All classification results are *noise robustness only, not
   generalisation to new heads*.
4. **Notch depth and resonance frequency are solve-sensitive** and are never used as features.
   The resonance moved 16 MHz between the v1 and v2 solves of Normal.
5. **The k = 3 (opposite-antenna) signal travels around the head surface, not through its
   centre.** Imaging study §1: measured group delay 3.61 ns, surface path 3.69 ns, straight
   path 6.03 ns. Its disease sensitivity comes from the CSF/cortex just under the skull.

---

## Part 2 — Verification results for the ARCHIVED v1 set (reproduce from `data/archive/v1_mixed_projects/`)

### Parsing

| Class | N | Values / freq | Native F | Band (GHz) | Step | Option line | Plausibility |
|---|---|---|---|---|---|---|---|
| Normal | 6 | 72 | 281 | 2.8–4.2 | 5 MHz uniform | `# GHz S MA R 50` | pass |
| Mild | 6 | 72 | 281 | 2.8–4.2 | 5 MHz uniform | `# GHz S MA R 50` | pass |
| Moderate | 6 | 72 | 281 | 2.8–4.2 | 5 MHz uniform | `# GHz S MA R 50` | pass |
| Severe | 6 | 72 | 501 | 3.2–4.2 | 2 MHz uniform | `# GHz S MA R 50` | pass |

- **Record alignment.** Records are multi-line: each matrix row is wrapped over two lines,
  with `!` comment lines interleaved. Every record starts on a new line; this was verified.
- **Plausibility checks.** Magnitudes are in [0, 1.05] and angles in [−180, 180]. The band
  matches GHz units.
- **Common grid:** 3.200–4.200 GHz, 201 points at 5 MHz, giving an S tensor of shape
  (4, 201, 6, 6).
  - Normal, Mild and Moderate need no interpolation: every grid point is a native node.
  - Severe is interpolated with a cubic spline on Re and Im. The leave-every-other-out
    spline error is −134 dB median relative to band-RMS. It reaches −8.6 dB at most, and
    only at glitch points (below).
- **Lost band.** The 2.8–3.2 GHz part is lost for all classes, because Severe was exported
  only from 3.2 GHz.

### Integrity

| Class | max\|S−Sᵀ\| | Reciprocity rel. to band-RMS: median / p99 / max (dB) | Glitch points | Max column power | σ_max | Passive |
|---|---|---|---|---|---|---|
| Normal | 6.9e-4 | −77 / −40 / −3.6 | 12 / 8430 | 0.962 | 0.982 | yes |
| Mild | 1.2e-3 | −76 / −40 / −16 | 32 / 8430 | 0.961 | 0.981 | yes |
| Moderate | 2.6e-5 | −82 / −48 / −34 | 2 / 8430 | 0.961 | 0.981 | yes |
| Severe | 6.6e-4 | −79 / −42 / −8.0 | 18 / 15030 | 0.902 | 0.950 | yes |

**Frequency glitches.** A glitch is a point where |Sij − Sji| > 0.1·|Sij|. At these points
a transmission entry jumps up to 5× and its phase swings by up to 180° between adjacent
samples. The pattern suggests sweep artefacts (e.g. an interpolating sweep), not physics.

| Class | Glitch frequencies (GHz) | Inside the common band? |
|---|---|---|
| Normal | 3.565; 4.135–4.155 | yes |
| Mild | 2.875–2.955 | no |
| Moderate | 3.81 | yes |
| Severe | 3.28, 3.714, 3.814, 3.904–3.91 | yes |

Band power averages dilute these points, but per-frequency features see them. Should they
be despiked, or the sweeps re-run as discrete sweeps? See "open decisions" below.

### Circulant-symmetry noise floor (common grid)

Numbers are across the t equivalent pairs at each ring distance k:

- median over frequency of max − min of |S| (dB);
- median over frequency of the std (dB), in parentheses;
- the median signal level.

| Class | k=0 (6 pairs) | k=1 (12) | k=2 (12) | k=3 (6) |
|---|---|---|---|---|
| Normal | 0.24 (0.09) | 0.61 (0.22) | 1.13 (0.37) | 0.61 (0.25) |
| Mild | 0.32 (0.11) | 1.13 (0.37) | 1.63 (0.57) | 1.02 (0.43) |
| Moderate | 0.23 (0.09) | 0.60 (0.20) | 1.11 (0.43) | 0.41 (0.17) |
| Severe | 0.13 (0.05) | 0.80 (0.28) | 1.39 (0.47) | 0.84 (0.36) |
| Level (median dB) | ≈ −4.2 | ≈ −43 | ≈ −60 | ≈ −56 |

- **Complex deviation from the ring mean**, relative to its magnitude (median):
  - k=0: −35 to −38 dB
  - k=1: −24 to −29 dB
  - k=2: −21 to −23 dB
  - k=3: −25 to −31 dB
- **Tails.** Near the Sii notch and the k=2 nulls (≈3.8 GHz), the 95th-percentile spread
  reaches 2–11 dB. Relative quantities are unreliable there.
- **Card vs data.** The card's figure of "0.1–0.2 dB" holds for |Sii| away from the notch.
  For transmission it is 0.4–1.6 dB (max − min).

### VERIFY items

| Item | Status | Evidence |
|---|---|---|
| Port→antenna order (T1…T6 consecutive, `[4,3,2,1,6,5]`) | **Supported by data** | Tested against all 60 distinct ring orderings. The card's mapping gives the lowest circulant error in every file, and by a wide margin: 0.36–0.64 dB vs 1.71–2.18 dB for the next best. It is equivalent to "file ports 1–6 are consecutive around the ring". The S-parameters cannot tell a ring direction or rotation from its mirror. **Now confirmed directly by the HFSS fields** (Part 4): T1…T6 consecutive at +60°, starting from T1 at −90°. |
| Ring geometry arithmetic | **Consistent** | 97.55·cos 60.5° = 48.04 mm (\|z\|); 97.55·sin 60.5° = 84.90 mm (ring radius); stand-off 97.55 − 88 = 9.55 mm. |
| Resonance ≈ 3.62 GHz; 3624 → 3626 → 3628 → 3630 MHz | **Reproduced; the spread across ports is larger than the card says** | Mean of per-port min \|Sii\| (native grid, parabolic refinement): 3623.9 / 3626.7 / 3627.7 / 3628.8 MHz (Normal / Mild / Moderate / Severe). Port ranges: Normal 3622–3625, Mild 3618–3634, Moderate 3624–3630, Severe 3626–3634 MHz. The trend is monotonic but inside the port scatter; it is not usable as a single-shot feature. |
| Shoulder 3.38–3.52 GHz: Normal −10 dB vs AD −8.3 to −8.9 dB | **Reproduced (definitions differ)** | The ring-mean point minimum for Normal is ≈ −10 dB. The power average over the band is Normal −8.96, Mild −8.19, Moderate −8.25, Severe −7.86 dB, with a port spread (max − min) of 0.38–0.54 dB. Normal vs AD differs by 0.6–1.1 dB, which is about 2× the port spread. Mild ≈ Moderate. |
| Notch depth mesh-sensitive | **Consistent** | Notch minima range from −27…−31 dB (Normal) to −40…−49 dB (Severe). The depth varies across ports of one file by 4–9 dB, so it is excluded as a feature. |
| Healthy file actually uses Normal geometry (not Mild) | **OPEN — GUI** | Headers are untrusted, so this cannot be settled from the files. Weak data hint: Normal differs from all AD stages by 2–5× the port noise in the opposite-antenna (k=3) coupling, and the AD stages cluster together. That fits a genuinely different Normal geometry and material set, but does not prove it. |
| Skin / fat / skull εr, σ | **OPEN — GUI** | Not in the data. |
| Normal-stage εr, σ as assigned in HFSS | **OPEN — GUI** | Not in the data. |
| Sign of ring z | **SETTLED: +z** (HFSS fields, Part 4) | Every antenna's field centroid lies in the upper hemisphere, at polar ≈ 55° (the feed is at 60.5°). |
| Antenna azimuths | **SETTLED: T1 at −90°, +60° steps** (HFSS fields, Part 4) | Field centroids at −90.5, −31.0, 29.6, 89.4, 148.9, −150.4°. The imaging I1/I3 geometry had assumed T1 at 0°. That has no effect on S for a symmetric head, and none on the classifier, which uses only the ring order. |
| Antenna polarisation | **SETTLED: ≈ 65% θ / 35% φ** (HFSS fields, Part 4) | θ-fraction 0.65 for all six antennas. The point-dipole forward model (pure φ) is therefore wrong in kind; this is part of its validation failure. |
| Field-level ring symmetry | **SETTLED: 11–16% rms; T1, T4 ≈ 4% stronger** (HFSS fields, Part 4) | The field-level counterpart of the S-parameter port asymmetry. |
| Meaning of `ant_dist`, `z_ebg` | **OPEN — GUI** | Not in the data. |
| Sweep type, convergence, mesh settings | **SETTLED from HFSS convergence tables (user, 2026-10-02) — settings DIFFER between designs** | v2 adaptive meshing, max 6 passes, 30% refinement. Healthy: ΔS target 0.02, 6 passes, NOT converged. MCI: target 0.02, 5 passes, final ΔS 0.0200, 910,960 tets (pass 1: 450,277). MildAD: target **0.05**, 4 passes, ΔS 0.0410, 672,508 tets (383,901). ModerateAD: target **0.05**, 6 passes, ΔS 0.0261, 569,697 tets (212,567; ΔS N/A at pass 4). SevereAD: target **0.05**, 6 passes, ΔS 0.0288, 606,640 tets (200,893; ΔS N/A at pass 4). The mesh settings split along Normal/MCI (0.02) vs AD (0.05), the same split as the main findings: a mesh contribution to Normal-vs-AD cannot be excluded. v2 S-parameters: interpolating sweep, 281 points; field exports: 3-point discrete sweep. v1/v2 repeat pairs very likely share meshes (deterministic meshing), so the solve-to-solve SD is a sweep spread and mesh error is unmeasured. |

### Project-confound assessment (common grid)

Method: build the ring-mode curve c_k(f) = mean over t of S(t, t+k). For each pair of
files, divide rms_f |c_k^a − c_k^b| by the pooled port-to-port RMS deviation. Values
≲ 1 mean "indistinguishable from within-file numerical noise".

| Pair | Same project? | k0 | k1 | k2 | k3 | k3 rms dB diff |
|---|---|---|---|---|---|---|
| Normal–Mild | no | 1.7 | 1.4 | 1.5 | 3.5 | 1.6 |
| Normal–Moderate | no | 2.6 | 1.1 | 1.4 | 5.1 | 1.8 |
| Normal–Severe | **yes** | 2.9 | 2.5 | 2.0 | 4.8 | 1.7 |
| Mild–Moderate | **yes** | 0.5 | 0.5 | 0.7 | 0.7 | 0.4 |
| Mild–Severe | no | 0.8 | 0.5 | 0.8 | 1.9 | 0.6 |
| Moderate–Severe | no | 1.2 | 1.0 | 1.0 | 2.0 | 0.3 |

Reading:

1. **Normal is the outlier.** It is equally far from the same-project file (Severe) and the
   other-project files (Mild, Moderate). The cross-project pair Mild–Severe is closer than
   the same-project pair Normal–Severe. If the project/mesh effect dominated, the reverse
   would hold. So there is **no evidence that the project effect dominates**. The pattern
   matches the physics: Normal→Mild is by far the largest change in geometry and materials.
2. **The AD stages are hard to tell apart.** Mild, Moderate and Severe differ from each other
   by only about 0.5–2× the within-file port noise, and their only visible signal is in k=3.
   At that size, an unmeasured mesh or project effect could produce or cancel the whole
   difference. **Mild vs Severe separation is not trustworthy until the mesh noise is
   measured.**
3. **Port-to-port spread is only a lower bound on cross-file noise.** It measures asymmetry
   inside one mesh; differences between two meshes are likely larger. The confound cannot
   be identified from these four files.
   - **Recommended fix:** re-solve one design, e.g. Normal, in the other project, or
     re-solve it with a different mesh seed or convergence setting.
   - The difference between the two runs is the true between-mesh noise floor.
4. **The most informative path is k=3** (opposite antennas; the wave travels around the head
   surface, see caveat 5). Normal sits about 2 dB above every AD stage over 3.35–3.6 GHz,
   clear of the port-noise band. Reflection (k=0) separates Normal only in the shoulder.

---

## Part 3 — Verification results for the CURRENT v2 set (2026-10-01)

Reproduce with `python scripts/00_qc.py --include-moderate` → `results/qc/qc_report.md`, and
`python scripts/01_compare_solves.py` → `results/qc/solve_comparison.md`.

**Parsing and integrity.**

- All 5 files are 6-port `GHz S MA R 50`, 2.8–4.2 GHz, 281 points. The common grid is now the full
  2.8–4.2 GHz band, with no resampling.
- Passive (σ_max ≤ 0.982). Reciprocal to −88…−98 dB (median, relative to band level).
- **Nearly glitch-free.** The QC count (local reciprocity error > −20 dB) finds none. The more
  sensitive masking rule (> −30 dB of the band level) masks 1 point in Normal (pair 4–5,
  3.43 GHz) and 6 in Severe (pair 2–5, 3.505 GHz). v1 had 26.
- **Port map `[4,3,2,1,6,5]`** ranks 1st of the 60 ring orderings in every file.

**Symmetry noise floor** (rms of the across-antenna SD, dB) is 2–3× lower than v1:

| Class | k0 | k1 | k2 | k3 |
|---|---|---|---|---|
| Normal | 0.36 | 0.26 | 0.70 | 0.32 |
| MCI | 0.07 | 0.11 | 0.39 | 0.15 |
| Mild | 0.15 | 0.12 | 0.61 | 0.21 |
| Moderate | 0.09 | 0.11 | 0.56 | 0.16 |
| Severe | 0.12 | 0.13 | 0.66 | 0.15 |

**Resonance (mean of per-port minimum |S_ii|):** Normal 3640.3, MCI 3655.5, Mild 3654.2,
Moderate 3647.3, Severe 3648.2 MHz. Not monotone in stage. The v1 Normal solve resonated at
3623.9 MHz, so the re-solve alone moved it by 16 MHz.

**v1 vs v2 solve of the same stage.** What the "correction" changed is not recorded here. If
only mesh/sweep settings changed, this is an estimate of solve-to-solve noise.

- Whole-spectrum differences (rms over 3.2–4.2 GHz of the ring-mode dB) between two solves of
  the *same* stage are 0.9–1.5 dB on k3 and 2.6–3.2 dB on k0. That is **as large as the
  Normal-vs-AD differences** (k3 1.5–2.1 dB).
- The band-averaged scalars move much less. C3 moves 0.14–0.61 dB and R31 0.00–0.34 dB,
  against Normal-vs-AD gaps of 1.5–1.9 dB (C3) and 1.2–1.5 dB (R31).
- **MCI ≈ Normal** on the scalars: C3 +0.23 dB, R31 +0.06 dB. That is expected, since MCI
  changes only the central hippocampus, where the array has no sensitivity (imaging study). Its
  whole-spectrum difference from Normal (≈1 dB on k3) is the same size as solve-to-solve
  variation.

---

## Part 4 — Facts settled by the HFSS field exports (2026-10-02)

**Source:** imaging report §4.0 and §4.3 (`results/imaging/report.md`, imaging-agent commits
18b1573–8fcae28).

**Data:** HFSS calculator exports of the complex E field for the **Normal** v2 design. There is
one file per driven antenna (1 V incident, other ports matched), at 3.4 / 3.6 / 3.8 GHz, on a
3 mm grid from −90 to 90 mm, plus a ±120 mm / 4 mm export of T1 at 3.6 GHz. They are stored in
`data/fields/` (19 files, about 880 MB, kept out of git).

**Antennas located from their own fields.** Each centroid is the |E|-weighted centre of the
strongest air nodes at r = 89–93 mm.

| Antenna | Azimuth (°) | Field-centroid polar angle (°) | θ fraction |
|---|---|---|---|
| T1 | −90.5 | 55.1 | 0.65 |
| T2 | −31.0 | 54.9 | 0.65 |
| T3 | 29.6 | 55.0 | 0.65 |
| T4 | 89.4 | 55.1 | 0.65 |
| T5 | 148.9 | 55.1 | 0.65 |
| T6 | −150.4 | 55.0 | 0.65 |

- **Ring at +z, T1 at −90°, T1…T6 consecutive at +60°.** The feed polar angle of 60.5° stays the
  geometric value; the field centroid sits slightly above it.
- **Mixed polarisation,** ≈ 65% θ / 35% φ in amplitude.
- **Ring symmetry at field level.** Inside r < 88 mm, each antenna's field differs from its
  opposite antenna's field (rotated 180°) by 11.4–15.8% rms across 3.4–3.8 GHz. At 3.6 GHz the
  rms amplitudes relative to the six-antenna mean are T1 1.044, T2 0.974, T3 0.981, T4 1.046,
  T5 0.973 and T6 0.979.
- **The k = 3 path (§4.3)** confirms the earlier delay test with the real antennas.
  - 99% of the T1–T4 Born sensitivity lies in air; only 0.3% is in the brain.
  - Half-way between T1 and T4, the field is −33 dB on the arc around the head against −57 dB
    on the straight chord through it.
  - Of the small in-brain part, 73% lies within 13.5 mm of the brain surface.
- **Effect on results: none.** The classification pipeline uses only the ring order, which is
  unchanged; no rerun is needed. The imaging forward model (point dipole, φ-polarised, T1 at 0°)
  disagrees with these facts. That is consistent with its documented validation failure.

### Pre-registered test for the equal-settings re-solves (written 2026-10-02, before any re-solve exists)

All five designs (Normal, MCI, Mild, Moderate, Severe) are to be re-solved with identical settings: Max ΔS 0.01, max passes
10-12, minimum converged passes 2, 30% refinement, all ending CONVERGED, same 281-point interpolating sweep. The frozen rule
`results/04/frozen_rule.json` (commit 2baddee) is applied unchanged to noisy draws of the re-solves (typical + ±0.5 dB gain):

- **Detection (R31 rule) is retracted** if any re-solved AD stage is labelled Normal, or the re-solved Normal labelled AD,
  in > 5% of measurements; or if the re-solved Normal-vs-AD R31 gap falls below 0.75 dB (half of the current 1.53 dB).
- **Staging (R21 / R32 rules) is retracted** under the conditions in `results/04/audit/report.md` §7 (items 1-2), and also
  if the re-solved Mild-Severe gap in R21 or R32 falls below 0.5 dB.
- **"Normal ≈ MCI"** stays as stated only if the re-solved MCI-Normal R31/R21/R32 differences stay below 2x the solve SD.


## Part 5 — Lobe-sector phantom (2026-10-03, convergence study 2026-10-04)

**Sources.**
- Prompt 07 (`prompts/07_lobe_analysis_prompt.md`) and the user's HFSS checks of 2026-10-03/04.
- Manifest `data/sims_lobe.csv` (with stop rule, passes, final ΔS and elements, and set membership).
- Analysis: `scripts/07_lobe.py --config config_lobe{,_A,_B}.yaml` writes `results/05_lobe/`, `results/05_lobe/lobe_A/` and
  `results/05_lobe/lobe_B/`; `scripts/08_lobe_mesh.py` writes `results/05_lobe/mesh/` (reproduction, one-pass yardstick,
  set comparison, claims); `scripts/09_lobe_tests.py` writes `results/05_lobe/tests/` (LeftOnly_test scoring, MCI_lobe).
  Results: 07 at code 08a9a53, 08 and 09 at e1b3629 (2026-10-04).
- The v1/v2 results are untouched; this is a separate dataset.

### 5.1 Supplied facts (from the user; not read from Touchstone headers)
- HFSS project `new_with_slices`: copies of the v2 Normal design (same 7-layer sphere, same ring, same port map
  Port 1..6 = T4, T3, T2, T1, T6, T5). Gray and white matter are cut into six 60° azimuthal sectors S1..S6, each
  centred on antenna T1..T6: Frontal, Temporal L, Parietal L, Occipital, Parietal R, Temporal R. The subject faces −Y
  (nose at T1); +X is the subject's left. The lobe placement is schematic: real temporal lobes lie below the ring.
- Inside sector k: gray 76 − e_k … 83 − e_k mm, white 25 … 76 − e_k mm, hippocampus sphere r_hip at the centre.
  CSF is one solid sphere r = 83.5 mm that fills every gap, so its material is the stage material everywhere.
  Skull 83.5–86.5, fat 86.5–87.5, skin 87.5–88 mm. The skull inner radius is set explicitly to 83.5 mm; in v2 it came
  from a hidden tool (`Brain_sphere_1`) of unknown radius.
- Stages (CSF expansion e_k in mm, sectors S1..S6; r_hip): Healthy_sliced 0 everywhere, 25; Mild_lobe 0/7.5/11.5/0/11.5/7.5,
  17.5; Moderate_lobe 11.5/12.5/15.5/0/15.5/12.5, 12.5; Severe_lobe 15.5/17.5/18/11.5/18/17.5, 7.5. Pending:
  MCI_lobe (no CSF expansion, r_hip 21.25, hippocampus material only; extra `Ventricle_CSF` sphere added to fix a
  meshing failure) and LeftOnly_test (= Mild with S5, S6 reset to healthy).
- Moderate − Mild is not a pure "frontal lobe added" contrast. Moderate also deepens the temporal and parietal
  atrophy, and it changes the CSF and hippocampus materials everywhere.
- Materials (εr / σ S/m, Shehab 2025 Table 5): healthy gray 47.7/2.42, white 35.3/1.65, hippocampus 47.7/2.42,
  CSF 65/4.27; Mild 40.3/5.203, 31.77/2.39, 39.11/5.687, 55.25/4.91; Moderate 39.11/5.687, 31.064/2.722,
  38.39/5.92, 48.75/5.337; Severe 38.39/5.92, 30.35/2.88, 37.2/6.413, 32.5/6.405 (gray, white, hippocampus,
  CSF); MCI hippocampus 40.3/5.203. Unaffected sectors keep healthy materials.
- Symmetry by construction: Healthy_sliced and MCI_lobe are rotationally symmetric; Mild/Moderate/Severe are mirror-
  symmetric about the Y axis (T2↔T6, T3↔T5); LeftOnly_test breaks left-right symmetry.
- Sweep: 3.2–4.2 GHz, 5 MHz, 201 points, interpolating, "Converged". One solve per design and stop rule.

### 5.2 VERIFIED items (user, in HFSS, 2026-10-03/04)
**Materials, VERIFIED in the HFSS material editor.**
- Gray_Matter_healthy 47.7/2.42, WhiteMatterHealthy 35.3/1.65, Hippocampus_healthy 47.7/2.42, CSF_Healthy 65/4.27.
- μr 1, dielectric loss tangent 0, no frequency dependence.
- Per-object assignments, read by script for all six designs, match the stage table:
  - LeftOnly_test: GM/WM_Mild in S2, S3 only; HIP_Mild; CSF_Mild.
  - MCI_lobe: HIP_MCI only; CSF_outer and Ventricle_CSF = CSF_Healthy.

**Setup1 and convergence, VERIFIED from the HFSS convergence tables.** Common to all designs:
- adaptive solution at 3.4 GHz (single frequency), Max ΔS 0.02, 30% refinement per pass;
- first-order basis, iterative solver, no ABC on ports.

Adaptive meshing is deterministic: re-solving with the same stop rule reproduces every pass exactly.

| File (`data/raw/new_with_slices_…`) | Stop rule | Passes | Final ΔS | Elements | Set |
|---|---|---|---|---|---|
| Healthy_sliced.s6p | ΔS < 0.02, 2 consecutive | 7 | 0.0092 | 1,349,491 | lobe_v1, lobe_B |
| Healthy_sliced_new.s6p | ΔS < 0.02, 1 | 6 | 0.0155 | 1,081,728 | lobe_A |
| Mild_lobe.s6p | ΔS < 0.02, 1 | 5 | 0.0186 | 739,774 | lobe_v1, lobe_A |
| Mild_lobe_new.s6p | ΔS < 0.02, 2 consecutive | 6 | 0.0150 | 878,656 | lobe_B |
| Moderate_lobe.s6p (= Moderate_lobe_new.s6p) | ΔS < 0.02, 1 | 5 | 0.0194 | 796,281 | lobe_v1, lobe_A |
| Severe_lobe.s6p (= Severe_lobe_new.s6p) | ΔS < 0.02, 1 | 5 | 0.019999 | 690,077 | lobe_v1, lobe_A |
| Moderate_lobe_c3.s6p | ΔS < 0.02, 2 consecutive | 6 | 0.014593 | 949,865 | lobe_B |
| Severe_lobe_c3.s6p | ΔS < 0.02, 2 consecutive | 6 | 0.011567 | 819,294 | lobe_B |
| LeftOnly_test_c3.s6p | ΔS < 0.02, 1 | 6 | 0.014686 | 941,358 | lobe_A (test design) |
| MCI_lobe_c3.s6p | ΔS < 0.02, 1 | 6 | 0.013948 | 981,160 | lobe_A (test design) |

The `_c3` suffix is only the user's label, not a stop rule. In LeftOnly_test, MCI_lobe and Healthy_sliced_new, pass 5
missed ΔS 0.02 by ≈ 0.002, so all three have 6 passes. Header variables were checked by the user: LeftOnly
e = 0/7.5/11.5/0/0/0 mm, r_hip 17.5; MCI e = 0, r_hip 21.25.

The `_new` files of Moderate and Severe equal the originals to ≤ 1.7e-8 (`results/05_lobe/mesh/0_duplicates.csv`).
Only one of each is in the manifest.

**Correction of the record.**
- The Prompt 07 files (lobe_v1) were **not** solved under one stopping rule: Healthy_sliced needed 2 consecutive
  converged passes, the stages 1.
- "Identical mesh settings" is **retracted** wherever it was written, and so is the inference that 100% detection in
  lobe_v1 is independent of mesh.
- My Part 5 of 2026-10-03 listed "max 8 passes / min converged passes 2 vs 1". The table above supersedes it.

**Sets.**
- **lobe_v1** (unmatched): the Prompt 07 results, kept as-is.
- **lobe_A** (stop rule 1, *stop-rule matched*): the primary set from 2026-10-04.
- **lobe_B** (stop rule 2): Healthy_sliced (7 passes), Mild_lobe_new, Moderate_lobe_c3, Severe_lobe_c3 (6 passes).
  Complete for the four stages since 2026-10-04.
- The test designs LeftOnly_test_c3 and MCI_lobe_c3 belong to lobe_A (manifest `kind = test`). The staging analysis
  (`kind = stage`) excludes them, and `scripts/09_lobe_tests.py` scores them.

lobe_A and lobe_B are stop-rule matched, not mesh-matched: the healthy head still has 1.46x (A) / 1.54x (B) the
elements of Mild.

**Still open.** The v2 skull inner radius (`Brain_sphere_1`) against 83.5 mm here is unknown, so a small
Normal-geometry difference cannot be excluded.

**Two caveats for scoring LeftOnly_test** (both reported with the score; cf56de8 is not edited):
- **Right-side CSF.** CSF is one object, so LeftOnly_test carries CSF_Mild on the right too, but only as the 0.5 mm
  layer (e_S5 = e_S6 = 0). The pre-registered predictions did **not** model this: they treat the right lobes as fully
  healthy, so right-side paths are predicted to change by ~0.
- **Unmatched derivation.** The predictions were derived from the lobe_v1 pair (Healthy_sliced, stop rule 2, against
  Mild_lobe, stop rule 1), so mesh is part of their per-path "Mild change".
- LeftOnly is scored against the Healthy file with its own stop rule.

### 5.3 Prompt 07 results on lobe_v1 (unmatched; one solve per design: within-simulation noise robustness, not generalisation)
- **QC.** All four files parse and pass passivity/reciprocity; the port map T4,T3,T2,T1,T6,T5 ranks 1st of 60 in every file.
  - **Correction:** the QC report's "no glitches" used a local detector (|Sij − Sji|/|Sij| > −20 dB).
  - The analysis mask (band-relative, −30 dB) did mask one weak point each: Healthy_sliced T1–T4 at 3.525 GHz and
    Severe_lobe T3–T6 at 3.845 GHz. Masking was on for every lobe_v1 number.
  - Glitch log: `results/05_lobe/qc/masked_points.csv`. It also holds the Mild_lobe_new T2–T5 glitch at 3.855 GHz,
    a single sample at −34/−38 dB on a ≈ −70 dB path, non-reciprocal by ≈ 5 dB.
- **Numerical symmetry floors.**
  - In Healthy_sliced, paths that should be identical by symmetry differ by band-power SD 0.003 (reflection), 0.028
    (neighbour), 0.095 (second-neighbour) and 0.054 dB (opposite).
  - In the mirror-symmetric stages, mirror-image paths differ by 0.007 / 0.080 / 0.149 / 0.063 dB.
- **Healthy_sliced ≈ v2 Normal.** R31 +0.06 dB (0.4 v2 solve SD), R21 +0.21 (1.3 SD), R32 −0.15 (1.2 SD).
  - Healthy_sliced_new ≈ v2 Normal too: R31 −0.07 (0.5 SD), R21 +0.16 (1.0 SD), R32 −0.23 dB (1.7 SD).
- **Frozen rule (commit 2baddee), applied unchanged.**
  - Detection: 100% on all four designs.
  - Merged staging (three_merged): 100%.
  - Three-class: Mild_lobe 41–43%, Severe_lobe 100%.
- **Localisation.**
  - Front-back neighbour index, Moderate: −0.21 dB = 2.6x the floor.
  - Asymmetry cross-ratios: best 2.3 SD.
- **Pre-registered LeftOnly_test predictions** (cf56de8): left-right index +0.23 dB; R31 −15.22 dB, so mostly UNCERTAIN.
- **Superseded:** the 2026-10-03 "mesh scale" (Healthy_sliced against the v2 healthy head). It is replaced by the
  one-pass yardstick in 5.4.

### 5.4 Convergence study (lobe_A primary, lobe_B; frozen-rule recipe throughout)
**Reproduction.** The user's table (`results/05_lobe/mesh/report.md` §1) reproduces exactly:
- the plain-mean table to 0.01 dB;
- the frozen-rule recipe values (glitch masking, trapezoid integration, geometric-mean ratios) to 0.001 dB.

The plain-mean "+0.30 dB through C3" for Mild 5 → 6 is the 3.855 GHz glitch. With masking it is −0.03 dB.

**One extra adaptive pass** (stop rule 1 → 2), all four stages since 2026-10-04:

| Ratio | Healthy 6 → 7 | Mild 5 → 6 | Moderate 5 → 6 | Severe 5 → 6 | Yardstick (largest) |
|---|---|---|---|---|---|
| R31 | +0.135 dB | −0.034 dB | −0.004 dB | −0.051 dB | 0.135 dB |
| R21 | +0.060 dB | +0.034 dB | −0.000 dB | +0.110 dB | 0.110 dB |
| R32 | +0.075 dB | −0.068 dB | −0.004 dB | −0.161 dB | 0.161 dB |

There is no consistent sign. The Severe 5 → 6 change is real, not a masking effect: the frozen mask removes 16 points
from Severe_lobe_c3 but moves its ratios by ≤ 0.009 dB (`results/05_lobe/mesh/0_mask_effect.csv`). Against this:
- **Normal − Mild R31:** 1.08 (A) / 1.25 (B) / 1.21 dB (v1), i.e. 8–9x the R31 yardstick.
- **R31 margins to τ (−15.27 dB) in lobe_A:**

  | Design | Margin to τ | × yardstick |
  |---|---|---|
  | Healthy_sliced_new | +0.53 dB | 3.9 |
  | Mild_lobe | −0.55 dB | 4.1 |
  | Moderate_lobe | −0.74 dB | 5.4 |
  | Severe_lobe | −0.26 dB | 1.9 |

- **R31 margins in lobe_B:**

  | Design | Margin to τ | × yardstick |
  |---|---|---|
  | Healthy_sliced | +0.66 dB | 4.9 |
  | Mild_lobe_new | −0.58 dB | 4.3 |
  | Moderate_lobe_c3 | −0.74 dB | 5.5 |
  | Severe_lobe_c3 | −0.31 dB | 2.3 |

  **Severe stays on the AD side of τ in both matched sets** (100% AD, also with ±2 dB / ±10°). It remains the design
  closest to the threshold.

**Yardstick against every statistic** (`results/05_lobe/mesh/2_yardstick_all.csv`).
- *Yardstick:* per statistic, the largest of the four one-pass changes. For per-path values and cross-ratios it is at
  least the rms one-pass change of that family: neighbour paths 0.041, second-neighbour 0.108, opposite 0.090,
  cross-ratios 0.162, asymmetry cross-ratios 0.127 dB.
- *Symmetry floor:* the mirror residual of the six mirror-symmetric stage designs (lobe_A and lobe_B), ×√2 for a
  difference of two designs: neighbour paths 0.111, second-neighbour 0.217, opposite 0.117, indices 0.178, asymmetry
  cross-ratios 0.291 dB.
- *Noise SD:* typical noise and setup perturbation, without per-port calibration error.
- *Measurement-error spread:* the same plus ±0.5 dB per-port gain, or ±2 dB gain + ±10° phase.
- *Rulers:* clean ruler = max(yardstick, floor); measured ruler = max(yardstick, floor ⊕ ±0.5 dB spread).

Findings:
- **Ring ratios** (detection/staging), Mild − healthy:
  - lobe_A: R31 −1.08 dB = 8.0x yardstick; R21 +0.59 = 5.4x; R32 −1.67 = 10.4x.
  - lobe_B: R31 −1.25 = 9.2x; R21 +0.57 = 5.2x; R32 −1.81 = 11.3x.
  - Severe − healthy: R21 23x (A) / 24x (B); R32 21x / 22x.
- **Frontal lobe (Moderate − Mild).** Moderate − Mild is independent of the healthy file; A and B agree.
  - Front-back neighbour index: −0.26 / −0.27 dB = 3.8x / 3.9x yardstick, but only 2.3x / 2.4x the clean ruler (the
    floor dominates) and 0.3x the measured ruler.
  - Front neighbour path T1–T6: 3.5x clean ruler, 0.6x measured. A single path mixes severity and location.
  - Asymmetry cross-ratios: 0 of 45 reach 3x the clean ruler (best 2.4x / 2.5x).
  - Raw cross-ratios separate Moderate from Mild (15/45 and 13/45 at 3x clean) through overall severity, not location.
- **Three-class rule on lobe-Mild is decided by the mesh.**
  - Mild_lobe (pass 5, lobe_A) is 0.41 correct; Mild_lobe_new (pass 6, lobe_B) is 0.69 (0.72 with ±2 dB / ±10°).
  - R21 sits 0.006 / 0.040 dB inside the Normal|Mild boundary (−19.98 dB). Mild's own one-pass R21 change is 0.034 dB
    (the four-stage R21 yardstick is 0.110 dB).
- **Exploratory, no refitting: lobe-Mild against uniform Mild.** Lobe-Mild (4 of 6 sectors affected) lies between
  healthy and uniform Mild on both staging ratios:
  - R21: −19.97 (A) / −19.94 (B), against −19.48 (uniform v2) / −19.31 (uniform v1) dB;
  - R32: 4.15 / 4.08, against 3.42 / 3.11 dB.
- **Changes against lobe_v1.**
  - Detection and merged staging: unchanged (100%).
  - Healthy margin to τ: +0.66 → +0.53 dB.
  - Front-back neighbour index of Moderate against the healthy head: −0.21 dB (2.6x floor) → −0.14 dB (1.8x).
  - Asymmetry cross-ratios: unchanged (same stage files).

**Feature roles (user note, 2026-10-04).**
- **R31 is a detection feature only.** It separates Normal from AD but is not monotonic across the AD stages:
  - lobe_A: Moderate −16.01 dB, Severe −15.53 dB;
  - uniform v2: Moderate −16.17 dB, Severe −15.85 dB.

  In both uniform solves Severe also lies above Mild.
- **R21 is the staging feature** (the three-class rule). It is monotonic across the four lobe stages in lobe_A:
  −20.57, −19.97, −19.45, −18.00 dB.
- **R32** is used by the merged rule (Normal / Mild+Moderate / Severe) and is also monotonic in the lobe set.
- **Mild and Moderate overlap** on both R21 and R32 in the uniform solves (audit: not separable). That is why the frozen
  staging rules leave Moderate out or merge it with Mild.

### 5.5 Claims (lobe_A primary; full table `results/05_lobe/mesh/claims.csv`)
| claim | verdict |
|---|---|
| The user's convergence table reproduces (frozen recipe) | holds |
| One extra pass (four stages) moves R31 / R21 / R32 by ≤ 0.135 / 0.110 / 0.161 dB, against Normal − Mild R31 1.08–1.25 dB | holds |
| Frozen detection (R31), stop-rule matched: healthy, Mild and Moderate correct in lobe_A and lobe_B, margins 3.9–5.5x yardstick | holds |
| Frozen detection on Severe, both matched sets | holds: 100% AD; Severe stays on the AD side of τ in lobe_B. Margins −0.26 / −0.31 dB = 1.9x / 2.3x the yardstick, the closest to τ (mesh-sensitive) |
| Frozen merged staging (three_merged, R32) labels all designs of lobe_A and lobe_B correctly | holds |
| R31 orders the AD stages | retracted: R31 is a detection feature only (Severe above Moderate in the lobe and uniform sets); staging uses R21 (and R32 for the merged rule) |
| Frozen three-class (R21) labels lobe-Mild as Mild | retracted (lobe_A 0.41; lobe_B 0.69, weakened); which value you get is decided by the mesh |
| Frontal lobe visible front-to-back (neighbour index), Moderate − Mild | clean: mesh-sensitive (2.3x A, 2.4x B); measured with ±0.5 dB gain: not detectable (0.3x) |
| Frontal lobe visible in gain-invariant asymmetry cross-ratios | not separable from mesh (best 2.4x / 2.5x the clean ruler) |
| Raw cross-ratios separate Moderate from Mild | holds as severity; not a location claim |
| Healthy_sliced(_new) reproduces the v2 healthy head | holds (both files within 1.7 v2 solve SD on R31/R21/R32) |
| Left-right checks on the mirror-symmetric designs (A, B) | pass (≤ 1.3x floor) |
| Lobe set had identical mesh settings, so detection is independent of mesh | **retracted** |
| Left-right asymmetry detectable (LeftOnly_test; scored blind against cf56de8) | **retracted**: no left-right difference beyond the rulers in the index or the gain-invariant cross-ratios; the locality predictions fail (5.7) |
| MCI_lobe ≈ healthy (Prompt 07 §3.5) | holds: 0 of 228 features beyond 3x the clean ruler; all frozen rules 100% Normal |

### 5.6 Data status
- Every lobe design listed in Prompt 07 is now solved, as are both stop-rule matched sets (lobe_A, lobe_B).
- Nothing in the lobe set is pending.
- **Not tested at all:** variation of anatomy between people (head size, skull/scalp thickness, antenna stand-off).

### 5.7 Pre-registered test designs (2026-10-04; `results/05_lobe/tests/`; one solve per design: within-simulation noise robustness, not generalisation)
**LeftOnly_test_c3 (left temporal + left parietal lobes).**
- **Scoring.** Scored blind against the predictions committed at cf56de8; git confirms they are unchanged.
  - References: Healthy_sliced (7 passes; primary, as pre-registered) and Healthy_sliced_new (6 passes; stop-rule and
    pass matched).
  - Caveats stated with the score: the predictions were derived from the unmatched lobe_v1 pair; LeftOnly carries
    CSF_Mild everywhere (a 0.5 mm layer on the right).
  - Labels: hit = committed rule holds and the effect is separable (≥ 3x the clean ruler); miss = rule fails by
    ≥ 3x the clean ruler; not separable = otherwise.

| Prediction (cf56de8) | Observed (primary / matched) | Committed rule | Label |
|---|---|---|---|
| 1. Left-right index +0.232 dB | +0.023 / −0.029 dB (0.1x noise SD) | fails (needs ≥ +0.213) | not separable: even the predicted value is only 2.3x the clean ruler (0.10 dB); the index is ≈ 0 |
| 2. Front-back index ≈ 0 (floor 0.084) | +0.068 / +0.137 dB | holds / fails | hit / not separable |
| 3. Right-side paths ≈ 0 | 7/7 / 4/7 within tolerance | — | 7 hit / 4 hit, 3 not separable |
| 4. Left-side paths ≈ full Mild change | 4/7 / 4/7 within tolerance | — | 1 hit, 6 not separable (both) |
| Locality model beats the no-locality baseline | rms 0.166 vs 0.135 / 0.189 vs 0.144 dB | fails | miss (both) |
| 5. R31 / R21 / R32 levels −15.22 / −20.24 / 5.03 dB | −15.445 / −20.200 / 4.755 dB | holds (all within 0.3 dB) | hit |
| 6. Frozen detection mostly UNCERTAIN | 0% UNCERTAIN, 100% AD | fails | miss |
| Gain-invariant left-right cross-ratios (primary test as agreed; predictions derived from cf56de8; decision rule fixed before the first run) | 0 of 22 beyond 3x the measured ruler (best 1.5x / 2.0x); locality rms 0.68 vs 0.47 / 0.93 vs 0.62 dB | fails | — |

- **What LeftOnly shows.** No left-right difference survives the rulers.
  - The numerical left-right asymmetry of the mirror-symmetric designs (clean ruler ≈ 0.43 dB for these
    cross-ratios) exceeds every predicted value.
  - The observed path changes look like a weaker, mirror-symmetric Mild change: the no-locality baseline wins.
  - The likely reason: the long paths (second-neighbour, opposite) wrap around the head and average both sides, while
    the short neighbour paths barely change even in Mild (≤ 0.1 dB).
  - A global contribution from CSF_Mild, present everywhere, cannot be separated with this design.
- **Frozen rules (unchanged) on LeftOnly.**
  - Detection: 100% AD. The R31 margin is −0.17 dB = 1.3x the R31 yardstick, so it is not mesh-robust.
  - Both staging rules say Normal: three 100%, three_merged 99%. That is inconsistent with detection.
- **Post hoc, not pre-registered.** The halfway model re-derived from the matched pair gives R31 −15.28, R21 −20.27,
  R32 4.99 dB.

**MCI_lobe_c3 (hippocampus only; Prompt 07 §3.5).**
- MCI − Healthy_sliced_new exceeds 3x the clean ruler on 0 of 228 quantities (largest 2.0x), and 3x the measured ruler
  on 0. The quantities are ring averages, ratios, indices, 21 paths, cross-ratios and their asymmetry parts, and the
  sub-band ring features.
- All frozen rules label it 100% Normal.
- Expected "no": confirmed.
- A methods note: several MCI cross-ratios reach 4x the noise SD. MCI is rotationally symmetric, so that is mesh
  asymmetry. Judged by noise alone, it would have looked like a finding; the mesh yardstick and symmetry floor are
  required rulers.
