# AD staging from microwave S-parameters — Track A (7-layer sphere, 6-antenna ring, HFSS)

- `MODEL_CARD.md` — phantom facts + verification status (read first).
- `config.yaml` — every tunable; `data/sims.csv` — authoritative labels (file headers are not trusted).
- `src/adstage/io/` — Touchstone parser, dataset loader / common-grid resampling.
- `src/adstage/qc.py`, `ring.py` — integrity and ring-symmetry checks.
- `scripts/00_qc.py` — QC run -> `results/qc/`, `results/figures/qc_ring_modes.png`.
- `results/metrics.csv` (append-only, fixed schema), `results/summary.md`.

```bash
python -m pytest -q
python scripts/00_qc.py --include-moderate
```
