"""Score the blind replication design RightOnly_test against the committed round-2 prediction (C6).

    python imaging/score_rightonly.py                  # once data/raw/new_with_slices_RightOnly_test*.s6p exists
    python imaging/score_rightonly.py --dry-run-mirror # pipeline check: mirror(LeftOnly_test_c3) as stand-in, prints only

Committed rule (results/imaging/round2_predictions.md, commit 0ceb626, written before this file):
  prediction 1: LR(RightOnly - Healthy_sliced_new), frozen Tikhonov dS = -6.9 +- 3.9, where 3.9 is the stated
                envelope (largest |null| LR of the symmetric designs);
  prediction 4: phase(T5-T6) - phase(T2-T3) change vs Healthy_sliced_new ~ -5 deg at 3.4-3.6 GHz, ~0 at 3.70-3.85;
  REPLICATED   if LR < 0, |LR| >= 2 x 3.9 = 7.8, and prediction 4 has the right sign (negative) at 3.4 AND 3.6 GHz;
  FAILED       if LR >= 0 (wrong sign) or |LR| < 3.9;
  otherwise    INCONCLUSIVE (the rule names no third outcome; this label is the only addition).
Note recorded before the data exist: the predicted |LR| (6.9) is below the 7.8 replication bar, so the expected
outcome under the prediction itself is INCONCLUSIVE. The rule is not changed.
Frozen pipeline: lobe_frozen.json (kappa, lambdas); nothing is re-fitted. Writes results/imaging/rightonly_score.md.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402

from imaging import lobe_A as LA  # noqa: E402
from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_rulers as LR  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, ROOT, git_hash  # noqa: E402
from imaging.report_lobe import _t  # noqa: E402

ENVELOPE = 3.9                      # committed in 0ceb626 (prediction 1)
PRED_LR = -6.9
MP = SL.mirror_perm()


def mir(S):
    return S[..., MP[:, None], MP[None, :]]


def find_file():
    c = sorted((ROOT / "data" / "raw").glob("new_with_slices_RightOnly_test*.s6p"))
    return c[0] if c else None


def score(S_ro, label, f, fh, fi, P, fz):
    kappa = np.array(fz["kappa_re"]) + 1j * np.array(fz["kappa_im"])
    lam = {"dS": fz["lambda_dS"], "log": fz["lambda_log"]}
    K6 = SL.region_kernels(P, SL.region_masks())[..., :6]
    out = []
    for ref in ("Healthy_sliced_new", "Healthy_sliced"):
        R, _ = SL.load_design(ref, f)
        M = LR.build_models(K6, fh, fi, kappa, R, LA.KEEP_ALL)
        for m in (RL.METHODS[0], RL.METHODS[2], LR.WNAME):
            fx = C3.make_x(M, m, lam)
            x = fx(S_ro[fi], R[fi])
            xm = fx(mir(S_ro)[fi], R[fi])
            amp = np.abs(S_ro) * np.exp(1j * np.angle(R))
            pha = np.abs(R) * np.exp(1j * np.angle(S_ro))
            lr = RL.contrasts(x)["LR"]
            out.append(dict(reference=ref, method=LR.SHORTM[m], LR=lr, LR_anti=(lr - RL.contrasts(xm)["LR"]) / 2,
                            LR_amp_part=RL.contrasts(fx(amp[fi], R[fi]))["LR"],
                            LR_phase_part=RL.contrasts(fx(pha[fi], R[fi]))["LR"],
                            **{f"S{k + 1}": float(x[6 + k]) for k in range(6)}))
    R6, _ = SL.load_design("Healthy_sliced_new", f)
    rho = SL.recip(S_ro) / SL.recip(R6)
    i23, i56 = SL.PAIRS.index((1, 2)), SL.PAIRS.index((4, 5))
    ph = {}
    for fq in (3.4, 3.5, 3.6, 3.7, 3.75, 3.8, 3.85):
        k = int(np.argmin(np.abs(f - fq * 1e9)))
        ph[fq] = float(np.degrees(np.angle(rho[i56, k])) - np.degrees(np.angle(rho[i23, k])))
    prim = out[0]
    lr = prim["LR"]
    p4 = ph[3.4] < 0 and ph[3.6] < 0
    if lr < 0 and abs(lr) >= 2 * ENVELOPE and p4:
        verdict = "REPLICATED"
    elif lr >= 0 or abs(lr) < ENVELOPE:
        verdict = "FAILED"
    else:
        verdict = "INCONCLUSIVE"
    L = [f"# RightOnly_test scored against the committed prediction (0ceb626) — {label}", "",
         f"Scored at code `{git_hash(ROOT)}` with the frozen pipeline (`lobe_frozen.json`, frozen at `{fz['code']}`).", "",
         f"**Verdict (committed rule): {verdict}.** Primary: LR = {lr:+.2f} (predicted {PRED_LR:+.1f} ± {ENVELOPE}); "
         f"replication bar |LR| ≥ {2 * ENVELOPE:.1f} with negative sign; fail if positive or |LR| < {ENVELOPE}. "
         f"Prediction 4 (T5–T6 minus T2–T3 phase change, deg): 3.4 GHz {ph[3.4]:+.1f}, 3.6 GHz {ph[3.6]:+.1f} "
         f"→ {'negative at both' if p4 else 'NOT negative at both'}; 3.70–3.85 GHz "
         + ", ".join(f"{v:+.1f}" for q, v in ph.items() if q >= 3.7) + ".",
         f"Prediction 3 (> 70 % of LR from phase; amplitude part below 2 in absolute value): phase part "
         f"{prim['LR_phase_part']:+.2f} of {lr:+.2f}, amplitude part {prim['LR_amp_part']:+.2f}.", "",
         _t(out, ["reference", "method", "LR", "LR_anti", "LR_amp_part", "LR_phase_part", "S1", "S2", "S3", "S4", "S5", "S6"],
            {c: "+.2f" for c in ["LR", "LR_anti", "LR_amp_part", "LR_phase_part", "S1", "S2", "S3", "S4", "S5", "S6"]}), "",
         "POST-HOC context, not part of the rule: LeftOnly_test_c3 gave LR +8.82 (vs Healthy_sliced_new), LR_anti +7.86, "
         "85 % phase. The mirror-pair average (LR_anti(Left) − LR_anti(Right)) / 2 is worth reporting, but it reduces "
         "mesh error only if the two meshes' asymmetries are independent."]
    return verdict, "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run-mirror", action="store_true")
    a = ap.parse_args()
    fz = json.loads((OUT / "lobe_frozen.json").read_text(encoding="utf-8"))
    S, f, fh, fi, P = RL.build(reuse=True)
    if a.dry_run_mirror:
        L_, _ = SL.load_design("LeftOnly_test_c3", f)
        verdict, txt = score(mir(L_), "DRY RUN: mirror(LeftOnly_test_c3), not a blind result", f, fh, fi, P, fz)
        print(txt.encode("ascii", "replace").decode())
        return
    fp = find_file()
    if fp is None:
        print("RightOnly_test not delivered yet (expected data/raw/new_with_slices_RightOnly_test*.s6p); nothing written.")
        return
    S_ro, _ = SL.load_design(fp.stem.replace("new_with_slices_", ""), f)
    verdict, txt = score(S_ro, fp.name, f, fh, fi, P, fz)
    (OUT / "rightonly_score.md").write_text(txt, encoding="utf-8")
    print(verdict, "->", OUT / "rightonly_score.md")


if __name__ == "__main__":
    main()
