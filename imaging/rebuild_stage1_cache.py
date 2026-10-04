"""Rebuild results/imaging/cache/lobe_v1-masked/stage1.pkl WITHOUT touching the frozen files.

    python imaging/rebuild_stage1_cache.py

`python imaging/run_lobe.py` (stage 1) would also rewrite lobe_frozen.json and lobe_predictions.md with a new
code hash, which must never happen after the freeze (fb5b775 / 62709e0). This script runs the same stage-1
computation, checks that kappa, the lambdas and every calling threshold equal the committed lobe_frozen.json
(relative tolerance 1e-9), and only then writes the cache file that lobe_A / lobe_rulers / mesh_lobe /
lobe_c3 / report_lobe.run_blind read. It never writes lobe_frozen.json or lobe_predictions.md.
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from imaging import run_lobe as RL  # noqa: E402


def main():
    fz = json.loads(RL.FROZEN.read_text(encoding="utf-8"))
    res, _ = RL.run_stage1(reuse=True)
    new = res["frozen"]
    checks = {"kappa_re": (new["kappa_re"], fz["kappa_re"]), "kappa_im": (new["kappa_im"], fz["kappa_im"]),
              "lambda_dS": (new["lambda_dS"], fz["lambda_dS"]), "lambda_log": (new["lambda_log"], fz["lambda_log"])}
    for m, r in fz["rules"].items():
        for k, v in r.items():
            checks[f"{m}/{k}"] = (new["rules"][m][k], v)
    bad = {k: (a, b) for k, (a, b) in checks.items() if not np.allclose(a, b, rtol=1e-9, atol=1e-12)}
    if bad:
        print("REFUSED: the recomputed stage 1 differs from lobe_frozen.json; nothing written.")
        for k, (a, b) in bad.items():
            print(f"  {k}: recomputed {a} vs frozen {b}")
        sys.exit(1)
    RL.CACHE.mkdir(parents=True, exist_ok=True)
    (RL.CACHE / "stage1.pkl").write_bytes(pickle.dumps(res))
    bp = res["blind_pred"]["LeftOnly_test"][RL.METHODS[0]]
    print(f"OK: {len(checks)} frozen values reproduced exactly; wrote {RL.CACHE / 'stage1.pkl'} "
          f"(stage-1 code hash in the pickle: {res['code']}; LeftOnly predicted LR {bp['LR_mean']:+.2f} ± {bp['LR_sd']:.2f})")


if __name__ == "__main__":
    main()
