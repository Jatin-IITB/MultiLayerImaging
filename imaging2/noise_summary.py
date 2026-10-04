"""Summary table of results/imaging2/noise_study.json -> noise_summary.csv (+ markdown on stdout).

Per target and condition over the K draws: stage correct, exact lobe pattern (all 6 calls right),
mean lobe calls correct /6, and for LeftOnly the fraction with the left side ahead
(mean e of S2,S3 minus mean e of S5,S6 > 2 mm) and with any right-side call.
"""
from __future__ import annotations

import collections
import json

import numpy as np
import pandas as pd

from .data import DESIGNS, OUT

TRUTH = {"Healthy_p7": "new_with_slices_Healthy_sliced.s6p", "Mild_p5": "new_with_slices_Mild_lobe.s6p",
         "Moderate_p5": "new_with_slices_Moderate_lobe.s6p", "Severe_p5": "new_with_slices_Severe_lobe.s6p",
         "LeftOnly_p6": "new_with_slices_LeftOnly_test_c3.s6p", "MCI_p6": "new_with_slices_MCI_lobe_c3.s6p"}


def main():
    nj = json.loads((OUT / "noise_study.json").read_text())
    groups = collections.defaultdict(list)
    for r in nj["rows"]:
        groups[(r["target"], r["condition"])].append(r)
    rows = []
    for (t, c), rs in groups.items():
        tr = next(d.truth for d in DESIGNS if d.file == TRUTH[t])
        calls_t = tr.affected.astype(int)
        stage_t = tr.tissue_stage if tr.affected.any() else "Healthy"
        calls = np.array([r["calls"] for r in rs])
        em = np.array([r["e_med"] for r in rs])
        lr = em[:, [1, 2]].mean(1) - em[:, [4, 5]].mean(1)
        rows.append(dict(target=t, condition=c, K=len(rs),
                         stage_correct=np.mean([r["stage"] == stage_t for r in rs]),
                         exact_pattern=np.mean((calls == calls_t).all(1)),
                         calls_correct_mean=float((calls == calls_t).sum(1).mean()),
                         left_ahead=float(np.mean(lr > 2.0)) if t == "LeftOnly_p6" else np.nan,
                         any_right_call=float(np.mean(calls[:, [4, 5]].any(1))) if t == "LeftOnly_p6" else np.nan))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "noise_summary.csv", index=False)
    conds = nj["conditions"]
    lines = ["| design | " + " | ".join(conds) + " |", "|---|" + "---|" * len(conds)]
    for t in TRUTH:
        cells = []
        for c in conds:
            r = df[(df.target == t) & (df.condition == c)].iloc[0]
            cell = f"stage {r.stage_correct:.0%}, exact lobes {r.exact_pattern:.0%}"
            if t == "LeftOnly_p6":
                cell += f", left ahead {r.left_ahead:.0%}"
            cells.append(cell)
        lines.append(f"| {t} | " + " | ".join(cells) + " |")
    md = "\n".join(lines)
    print(md)
    return md


if __name__ == "__main__":
    main()
