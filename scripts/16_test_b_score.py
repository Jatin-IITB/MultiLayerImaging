"""Score the main session's Test_B blind estimates (0f49389) against the truth, exactly per protocol §3 (d3a4bbf).

    python scripts/16_test_b_score.py

Reads (never writes) results/05_lobe/test_b/{protocol.md, estimates.csv} after checking their git blobs, and the truth
recorded in data/sims_lobe.csv (row new_with_slices_Test_B.s6p; returned by the user after every session had
committed its estimates). Writes results/05_lobe/test_b_score/{score.md, score.csv}.

Protocol §3, verbatim in substance:
  detection: correct if AD and Test_B contains any disease change; margin tier = confidence.
  staging: scored only if Test_B uses one stage's materials (three: Normal/Mild/Severe; merged: Normal/Mild+Moderate/
           Severe); UNCERTAIN = abstention.
  side: true side = sign of (e_S2 + e_S3) - (e_S5 + e_S6); zero = no left-right asymmetry; 'undetermined' = abstention.
  sectors: affected if e_Sk > 0 or Sk carries diseased GM/WM; hits / misses / false alarms / correct rejections /
           uncertain (= abstention); the pattern is exact only if there is no uncertain and no error.
  calibration: do errors fall on established calls or on sensitive / uncertain ones.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from adstage.io.dataset import load_manifest  # noqa: E402
from adstage.results import git_hash  # noqa: E402

TB_DIR = ROOT / "results" / "05_lobe" / "test_b"
OUT = ROOT / "results" / "05_lobe" / "test_b_score"
BLOBS = {"protocol.md": "37a5bc4ebced50a223e9c6b179a4f9f9632d3af1",
         "estimates.csv": "fa4a6bcf80a5ac52261d54f3e811476d5e911958"}
SECT = ["S1 frontal", "S2 temporal L", "S3 parietal L", "S4 occipital", "S5 parietal R", "S6 temporal R"]


def md(df):
    head = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    return "\n".join([head, sep] + ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    for fn, blob in BLOBS.items():
        h = subprocess.run(["git", "hash-object", str(TB_DIR / fn)], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        if h != blob:
            raise SystemExit(f"{fn}: blob {h} differs from the committed {blob}; refusing to score")
    est = pd.read_csv(TB_DIR / "estimates.csv").set_index("item")
    man = load_manifest(ROOT / "data" / "sims_lobe.csv")
    row = man[man.file == "new_with_slices_Test_B.s6p"].iloc[0]
    e = [float(v) for v in re.search(r"e = ([\d./]+) mm", row.notes).group(1).split("/")]
    mat_sect = {int(c) for c in re.findall(r"S(\d)", str(row.sectors_affected))}
    truth_aff = [e[k] > 0 or (k + 1) in mat_sect for k in range(6)]
    stage_mat = "Mild" if "Mild" in row.notes else None
    rows = []
    det = est.loc["detection (frozen R31)"]
    rows.append({"item": "detection", "estimate": det.estimate, "truth": "AD (disease present)",
                 "score": "correct" if det.estimate == "AD" else ("abstention" if det.estimate == "UNCERTAIN" else "wrong"),
                 "confidence as reported": det["margin / confidence"]})
    for it, tr in (("staging three (R21)", stage_mat), ("staging three_merged (R32)",
                                                        "Mild+Moderate" if stage_mat in ("Mild", "Moderate") else stage_mat)):
        x = est.loc[it]
        sc = "not scored" if tr is None else ("abstention" if x.estimate == "UNCERTAIN" else
                                              ("correct" if x.estimate == tr else "wrong"))
        rows.append({"item": it, "estimate": x.estimate, "truth": tr, "score": sc,
                     "confidence as reported": x["margin / confidence"]})
    d = (e[1] + e[2]) - (e[4] + e[5])
    tside = "left" if d > 0 else ("right" if d < 0 else "no left-right asymmetry")
    s = est.loc["side"]
    rows.append({"item": "side", "estimate": s.estimate, "truth": f"{tside} ((e_S2+e_S3)-(e_S5+e_S6) = {d:+.1f} mm)",
                 "score": "abstention" if s.estimate == "undetermined" else ("correct" if s.estimate == tside else "wrong"),
                 "confidence as reported": s["margin / confidence"]})
    cnt = {"hits": 0, "misses": 0, "false alarms": 0, "correct rejections": 0, "uncertain": 0}
    for k in range(6):
        x = est.loc[SECT[k]]
        if x.estimate == "uncertain":
            sc = "uncertain"
        elif x.estimate == "affected":
            sc = "hits" if truth_aff[k] else "false alarms"
        else:
            sc = "misses" if truth_aff[k] else "correct rejections"
        cnt[sc] += 1
        rows.append({"item": SECT[k], "estimate": x.estimate, "truth": "affected" if truth_aff[k] else "not affected",
                     "score": sc.rstrip("s") if sc != "uncertain" else "uncertain (abstention)",
                     "confidence as reported": x["margin / confidence"]})
    exact = cnt["uncertain"] == 0 and cnt["misses"] == 0 and cnt["false alarms"] == 0
    pat = est.loc["sector pattern"]
    tpat = "".join(str(k + 1) for k in range(6) if truth_aff[k])
    rows.append({"item": "sector pattern (best fit, reported)", "estimate": pat.estimate, "truth": tpat,
                 "score": ("equals the truth" if str(pat.estimate) == tpat else "differs from the truth")
                 + f"; exact under §3: {exact} (§3 requires no uncertain sector)",
                 "confidence as reported": pat["margin / confidence"]})
    sc = pd.DataFrame(rows)
    sc.to_csv(OUT / "score.csv", index=False)
    wrong = sc[sc.score == "wrong"]
    calib = ("errors: " + ", ".join(f"{r['item']} ({r['confidence as reported']})" for _, r in wrong.iterrows())
             if len(wrong) else "no errors")
    est_calls = sc[sc["confidence as reported"].astype(str).str.contains("established|determined \\(>= 3x\\)")]
    L = [f"# Test_B: main-session estimates (0f49389) scored against the truth, per protocol §3 (d3a4bbf) (code {git_hash(ROOT)})",
         "", f"Truth (user, returned after all estimates were committed): e = {'/'.join(f'{v:g}' for v in e)} mm, Mild "
         f"materials in S2 and S5, HIP_Mild, CSF_Mild everywhere. Blobs of protocol.md and estimates.csv checked.", "",
         md(sc), "", f"Sector counts: {cnt}; pattern exact under §3: {exact}.",
         f"Calibration: {calib}. Calls marked established among the scored items: {len(est_calls)}; every error sits on a "
         "label whose margin was 'not determined'." if len(wrong) and all("not determined" in str(c) for c in
                                                                           wrong["confidence as reported"]) else
         f"Calibration: {calib}.", ""]
    (OUT / "score.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
