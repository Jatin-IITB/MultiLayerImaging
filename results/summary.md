# Track A — running summary

## Prompt 01A — data loading and QC

Details: `MODEL_CARD.md` Part 2, `results/qc/qc_report.md`. No classification run yet, so
`metrics.csv` has no rows.

- **Parsing.** All 4 files parse as 6-port `GHz S MA R 50`. They are reciprocal to −76…−82 dB
  (median, relative to band-RMS) and passive (σ_max ≤ 0.982).
- **Common grid.** 3.2–4.2 GHz, 201 points at 5 MHz. The 2.8–3.2 GHz range is lost because
  Severe starts at 3.2 GHz.
- **Glitches.** Isolated frequency glitches (non-reciprocal single points) sit inside the
  band at 3.565 and 4.135–4.155 GHz (Normal), 3.81 (Moderate), and 3.28, 3.71, 3.81 and
  3.90–3.91 GHz (Severe). They look like sweep artefacts.
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
  Mild vs Severe cannot be trusted until the mesh noise between projects is measured.
- **Best path.** The through-head path k=3 carries the clearest Normal-vs-AD signal:
  about 2 dB over 3.35–3.6 GHz.
