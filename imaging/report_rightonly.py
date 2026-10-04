"""Section 10 of lobe_report.md: RightOnly_test (replication, C6). QC from the S-parameters, the committed
scorer's verdict (imaging/score_rightonly.py, 226f9b1; rule 0ceb626) and the POST-HOC mirror-pair context.

    python imaging/report_rightonly.py      (after imaging/score_rightonly.py has written rightonly_score.md)
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_round2 as R2  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import score_rightonly as SR  # noqa: E402
from imaging import score_testb as TB  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT  # noqa: E402
from imaging.report_lobe import _t  # noqa: E402


def main():
    fz = json.loads((OUT / "lobe_frozen.json").read_text(encoding="utf-8"))
    ctx = C3.Ctx(20)
    ctx.S["RightOnly_test"], _ = SL.load_design("RightOnly_test", ctx.f)
    q = TB.qc("RightOnly_test", ctx.f)
    verdict, _ = SR.score(ctx.S["RightOnly_test"], "RightOnly_test", ctx.f, ctx.fh, ctx.fi, ctx.P, fz)
    rows = []
    for ref in ("Healthy_sliced", "Healthy_sliced_new"):
        for m in (RL.METHODS[0], RL.METHODS[2], R2.LR.WNAME):
            T = R2.anti_lr(ctx, m, ref)
            ro, lo = T(ctx.S["RightOnly_test"]), T(ctx.S["LeftOnly_test_c3"])
            nulls = [abs(T(ctx.S[d])) for d in C3.SYMMETRIC]
            yard = max(abs(T(ctx.S[a]) - T(ctx.S[b])) for a, b in C3.ONE_PASS.values())
            ruler = max(yard, max(nulls))
            rows.append(dict(reference=ref, method=R2.SH[m], LR_anti_Right=ro, LR_anti_Left=lo,
                             ratio_Right=abs(ro) / ruler, ratio_Left=abs(lo) / ruler,
                             mirror_pair_average=(lo - ro) / 2, average_over_ruler=abs(lo - ro) / 2 / ruler,
                             right_beyond_all_nulls=abs(ro) > max(nulls), left_beyond_all_nulls=abs(lo) > max(nulls)))
    L = ["## 10. RightOnly_test: replication of the left/right sign (C6)", "",
         f"Scored by the committed scorer (`imaging/score_rightonly.py`, `226f9b1`; rule `0ceb626`) before any other use "
         f"of the file: **{verdict}**. Full output: `results/imaging/rightonly_score.md`.", "",
         "QC (S-parameters only): " + ", ".join(f"{k} {v}" for k, v in q.items() if k != "masked") + ".", "",
         "**POST-HOC context** (not part of the committed rule): LR_anti of RightOnly and LeftOnly against the R1c ruler "
         "(max(one-pass yardstick, largest |null| of the nine symmetric solves)):", "",
         _t(rows, list(rows[0]), {"LR_anti_Right": "+.2f", "LR_anti_Left": "+.2f", "ratio_Right": ".2f", "ratio_Left": ".2f",
                                   "mirror_pair_average": "+.2f", "average_over_ruler": ".2f"}), "",
         "Each design alone is 'sensitive' (2–3×) under R1c. Both lie beyond all nine nulls with the predicted opposite "
         "signs, on independently meshed files. If the two meshes' asymmetries are independent, the one-sided rank p "
         "of the pair is about 0.1 × 0.1 = 0.01. That assumes what the rotated-mesh null solves (open item) would test.", ""]
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    sec = "\n".join(L)
    if "## 10." in rep:
        i0 = rep.index("## 10.")
        j = rep.find("\n## ", i0 + 5)
        rep = rep[:i0] + sec + ("\n" + rep[j + 1:] if j >= 0 else "\n")
    elif "## 11." in rep:
        i = rep.index("## 11.")
        rep = rep[:i] + sec + "\n" + rep[i:]
    else:
        rep = rep.rstrip("\n") + "\n\n" + sec + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
    print(verdict)
    for r in rows:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
