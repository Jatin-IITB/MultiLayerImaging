# E-field plots (viewing only)

Plots of the HFSS field exports for the **healthy uniform head (v2), 3.6 GHz**. They are not used by any
analysis and are not in the presentation.

| File | What it shows |
|---|---|
| `efield_overview.png` | (a, b) field of T1 when it transmits, in the ring plane (z = 48 mm) and a vertical cut (x = 0); (c, d) where the T1→T4 (opposite) signal is sensitive, \|E₁·E₄\|, in the same two cuts |
| `efield_paths_profile.png` | (e) sensitivity of the T1→T2 (neighbour) signal; (f) T1's field along its axis going into the head |
| `efield_routes_explained.png` | where the x = 0 slice is and where you stand; T1's field along the two routes to T4 (over the top in air vs straight through the head); the T1→T4 sensitivity, all on one dB reference |
| `efield_plots.py` | regenerates the first two PNGs: `python results/efield/efield_plots.py` |
| `efield_numbers.py` | prints every number below step by step and writes `efield_routes_explained.png`: `python results/efield/efield_numbers.py` |

"Sensitivity" is the first-order (Born) measure \|E_a·E_b\|: how much a small tissue change at a point would alter
the a→b signal. A point counts only if both antennas' fields reach it; in dB it is roughly dB(E_a) + dB(E_b).

dB references differ between the files, so compare only differences across them:
- `efield_overview.png`, `efield_paths_profile.png`: 0 dB = the strongest value in each panel.
- `efield_routes_explained.png`: 0 dB = T1's field just in front of T1 (point R); for sensitivity, R².

Readings:
- T1 and T4 are 180° apart around the ring but 121° apart seen from the head centre (both sit 48 mm above it).
  The straight line between them crosses 135 mm of brain, its middle 48 mm from the centre; the route over the
  top, just outside the skin (r = 91 mm), is 192 mm long.
- Half-way to T4, T1's field is −33 dB over the top (in air) against −57 dB on the straight line through the
  head (23 dB weaker), relative to R. The 4 mm grid makes these ±3 dB.
- Tissue loss from the material values (plane wave, 3.6 GHz): gray 5.7, white 4.5, CSF 8.6 dB/cm.
  Quick rule: 16.4 × σ / √εr dB/cm.
- Along T1's axis, between r = 80 and 55 mm, the field falls 5.3–5.6 dB/cm (depends on how the grid is
  interpolated). Absorption alone predicts 4.7 dB/cm for that stretch (4 mm gray + 21 mm white); the remaining
  0.6–0.9 dB/cm is the beam spreading out.
- The ~15 dB drop between the skin (r 88) and the brain surface (r 83) is mostly the boundary, not absorption:
  the part of the field pointing into the head is divided by |ε| ≈ 38 on entering the skin.
- T1→T4 sensitivity: 0.31% in the brain, 0.75% in CSF/skull/fat/skin, 99% in air (same as
  `results/imaging/report.md` §4.3). Half-way: −68 dB over the top, −98 dB at the sides in the ring plane,
  −116 dB on the straight line (relative to R²).

Input: `data/fields/E_Normal_T{1,2,4}_3p6GHz*.fld` (exports of the healthy uniform head; git-ignored, ≈ 47 MB each).
The lobe-sector head has no field exports.
