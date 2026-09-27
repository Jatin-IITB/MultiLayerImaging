# AD staging from microwave S-parameters — Track A (7-layer sphere, 6-antenna ring, HFSS)

- `MODEL_CARD.md` — phantom facts + verification status (read first).
- `config.yaml` — every tunable; `data/sims.csv` — authoritative labels (file headers are not trusted).
- `src/adstage/io/` — Touchstone parser, glitch masking, dataset loader / common grid.
- `src/adstage/features/metrics.py` — M0–M8; `noise/` — noise model, mesh/port noise reference.
- `src/adstage/pipeline/` — quality gate, augmentation, CV folds, classifiers.
- `scripts/00_qc.py`, `02_metrics.py`, `03_classify.py`; `scripts/run_all.py` runs all three.
- `results/metrics.csv` (append-only, fixed schema), `results/summary.md`, `results/*/report.md`.

## Regenerating after new simulations arrive

1. Copy the `.sNp` files to `data/raw/` and add one row each to `data/sims.csv`:
   `class` (Normal / MCI / Mild / Moderate / Severe), `head_id` (same id = same head geometry),
   `role` (`primary`, or `mesh_repeat` with `repeat_of` = the file it re-solves).
2. If the files replace the old set, change `metrics.sim_set` in `config.yaml`.
3. Commit, then run everything with one command:

```bash
python scripts/run_all.py
```

What adapts automatically:
- **Class schemes.** Schemes with an empty class are skipped; `binary_early` starts when an MCI row exists.
- **Cross-validation.** It switches to leave-one-simulation-out once every class has ≥ 2
  simulations. Results count as generalisation only when every class has ≥ 2 distinct `head_id`s.
- **Noise reference.** It switches from port-to-port to between-mesh when `mesh_repeat` rows exist.

Tests:

```bash
python -m pytest -q
```
