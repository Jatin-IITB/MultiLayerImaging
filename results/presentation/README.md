# Presentation figures (5 Oct 2026 progress review)

Figures made for the review deck. Viewing only: no new analysis, every number comes from the files named below.

| File | What it shows | Source |
|---|---|---|
| `overlay_stages_z50.png` | Ring height z = 50 mm, for Healthy, Mild, Moderate, Severe, left lobes only and MCI: true change, estimated change and error, drawn on the healthy head | `results/imaging2/posteriors.json` |
| `overlay_slices_a.png` | Mild and Moderate at z = 80 … 0 mm: true, estimated, error | same |
| `overlay_slices_b.png` | Severe and left lobes only at z = 80 … 0 mm | same |
| `overlay_blind_slices.png` | Blind design Test_B at z = 80 … 0 mm: truth (revealed after scoring), blind estimate, error | `results/imaging2/blind/Test_B/report.json`, `truth.json` |
| `overlay_figures.py` | Regenerates the four figures above: `python results/presentation/overlay_figures.py` (numpy, matplotlib) | |
| `per_lobe_results.png` | Per-lobe estimate vs truth (P(affected), median retreat, 90% interval), estimated stage and fit, six designs | bottom row of `results/imaging2/figures/overview_sig_z50.png` with a header from `scores_designs.csv` |
| `blind_lobes.png` | Blind test: true design and per-lobe blind estimate vs truth, estimated stage and fit | `results/imaging2/blind/Test_B/` |

How to read the overlay figures:
- **Red:** brain tissue that the cortex retreat turns into CSF. **Arc outside the head:** lobe called affected
  (P(affected) > 0.5). **Error row:** blue = true change the estimate missed, amber = estimated change not in the truth.
- Each estimated lobe is drawn at its **posterior median** retreat; the 90% intervals are wide (see `per_lobe_results.png`).
- **No tissue values are drawn.** The inversion estimates only the stage and one retreat per lobe; permittivity and
  conductivity are not estimated.
- **Height is not measured.** All antennas sit at z ≈ 48 mm and the lobes are full-height 60° wedges in the model,
  so every slice repeats the same seven numbers. Slices at z ≤ 20 mm are hatched: below the array's view, model only.
  The hippocampus is not estimated and stays healthy in the estimate.
- **Severe:** stage and lobes right, depth not recoverable (Severe CSF absorbs within about 5 mm, and no Severe design
  is in the training set when Severe is imaged); its fit value (2.59) flags it as "depth not trusted".

Explanations of the method and of every number on the slides: [`docs/presentation_qa.md`](../../docs/presentation_qa.md).
