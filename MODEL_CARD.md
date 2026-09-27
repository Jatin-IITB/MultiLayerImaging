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
- **Excitation:** HFSS Driven Terminal, lumped 50 Ω ports, radiation boundary box.

### Port mapping (card)

`Port[1..6] = T4, T3, T2, T1, T6, T5` → `config.yaml: ring.port_to_ant = [4, 3, 2, 1, 6, 5]`.

### Data files

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
2. **Project confound.** Normal and Severe come from one HFSS project; Mild and Moderate
   come from another.
3. **One simulation per class.** All classification results are *noise robustness only, not
   generalisation to new heads*.
4. **Notch depth is mesh-sensitive** and is never used as a feature.

---

## Part 2 — Verification results (code: see hash in `results/qc/qc_report.md`)

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
| Port→antenna order (T1…T6 consecutive, `[4,3,2,1,6,5]`) | **Supported by data** | Tested against all 60 distinct ring orderings. The card's mapping gives the lowest circulant error in every file, and by a wide margin: 0.36–0.64 dB vs 1.71–2.18 dB for the next best. It is equivalent to "file ports 1–6 are consecutive around the ring". The data cannot tell a ring direction or rotation from its mirror, so this is irrelevant for a symmetric head. |
| Ring geometry arithmetic | **Consistent** | 97.55·cos 60.5° = 48.04 mm (\|z\|); 97.55·sin 60.5° = 84.90 mm (ring radius); stand-off 97.55 − 88 = 9.55 mm. |
| Resonance ≈ 3.62 GHz; 3624 → 3626 → 3628 → 3630 MHz | **Reproduced; the spread across ports is larger than the card says** | Mean of per-port min \|Sii\| (native grid, parabolic refinement): 3623.9 / 3626.7 / 3627.7 / 3628.8 MHz (Normal / Mild / Moderate / Severe). Port ranges: Normal 3622–3625, Mild 3618–3634, Moderate 3624–3630, Severe 3626–3634 MHz. The trend is monotonic but inside the port scatter; it is not usable as a single-shot feature. |
| Shoulder 3.38–3.52 GHz: Normal −10 dB vs AD −8.3 to −8.9 dB | **Reproduced (definitions differ)** | The ring-mean point minimum for Normal is ≈ −10 dB. The power average over the band is Normal −8.96, Mild −8.19, Moderate −8.25, Severe −7.86 dB, with a port spread (max − min) of 0.38–0.54 dB. Normal vs AD differs by 0.6–1.1 dB, which is about 2× the port spread. Mild ≈ Moderate. |
| Notch depth mesh-sensitive | **Consistent** | Notch minima range from −27…−31 dB (Normal) to −40…−49 dB (Severe). The depth varies across ports of one file by 4–9 dB, so it is excluded as a feature. |
| Healthy file actually uses Normal geometry (not Mild) | **OPEN — GUI** | Headers are untrusted, so this cannot be settled from the files. Weak data hint: Normal differs from all AD stages by 2–5× the port noise in the through-head k=3 path, and the AD stages cluster together. That fits a genuinely different Normal geometry and material set, but does not prove it. |
| Skin / fat / skull εr, σ | **OPEN — GUI** | Not in the data. |
| Normal-stage εr, σ as assigned in HFSS | **OPEN — GUI** | Not in the data. |
| Meaning of `ant_dist`, `z_ebg`; sign of ring z | **OPEN — GUI** | Not in the data. A symmetric head makes the S-parameters insensitive to the sign of z (mirror symmetry), but F1 needs it. |
| Sweep type (interpolating vs discrete), convergence ΔS, mesh settings per project | **OPEN — GUI** | Needed to explain the glitches and to size the mesh noise. |

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
4. **The most informative path is k=3** (opposite antennas, the path through the centre).
   Normal sits about 2 dB above every AD stage over 3.35–3.6 GHz, clear of the port-noise
   band (`results/figures/qc_ring_modes.png`). Reflection (k=0) separates Normal only in
   the shoulder.
