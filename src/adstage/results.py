"""Append-only writer for results/metrics.csv (schema fixed by the project brief)."""
from __future__ import annotations

import csv
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = ["timestamp", "git_hash", "track", "model_id", "sim_set", "classes", "method_id",
          "feature_desc", "feature_dim", "classifier", "noise_profile", "cv_scheme",
          "n_sims_per_class", "n_test", "accuracy", "balanced_accuracy", "macro_f1",
          "min_pairwise_fisher", "min_pairwise_bhattacharyya", "reject_rate",
          "accuracy_on_accepted", "notes"]


def git_hash(root: str | Path = ".") -> str:
    """Short HEAD hash; '-dirty' suffix if tracked files are modified."""
    h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                       capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "-uno"], cwd=root,
                           capture_output=True, text=True).stdout.strip()
    return h + ("-dirty" if dirty else "")


def append_row(path: str | Path, row: dict) -> None:
    path = Path(path)
    if unknown := set(row) - set(SCHEMA):
        raise KeyError(f"Not in metrics schema: {unknown}")
    row = {"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"), **row}
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SCHEMA)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in SCHEMA})
