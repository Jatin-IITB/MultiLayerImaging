"""C6 replication: score RightOnly_test against the predictions committed at 0f97bb2, exactly as written.

    python scripts/14_rightonly.py

Reads (never writes) results/05_lobe/rightonly_predictions.{md,csv} and checks their git blobs first. Writes
results/05_lobe/rightonly/{report.md, scored.csv, summary.csv}.

Scoring, copied from rightonly_predictions.md (0f97bb2):
  P1  every informative left-right statistic flips sign: holds if the sign flips and |T(RO) + T(LO)| <= the stated
      tolerance (clean ruler) for >= 80% of the informative statistics (column 'sign test informative', 26 rows).
  P2  phase cross-ratios >= 3x the clean ruler: LeftOnly 4 (band mean) and 9 (3.30-3.65 GHz); RightOnly within +-2 of
      each count, all with the opposite sign.
  P3  power: no power LR index beyond 2x its ruler; the reflection pairs flip sign.
  P4  R31, R21, R32 equal LeftOnly's within one one-pass yardstick.
  P5  imaging-session mirror-test LR: sign flips (LeftOnly +7.9); size below 2x the max floor.
  Replicated only if P1 and P2 both hold. If the signs do not flip, the phase finding is retracted as numerical.
RightOnly is scored with the same code paths that produced the predictions (scripts/13_review2_misc.py): the
left-right phase of the complex cross-ratios (11_review2.lr_cr_phase), the reference-free mirror statistics
(10_lobe_review.mirror_stats) and the ring features. One solve per design: within-simulation noise robustness.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adstage.config import load_config  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
R10 = _load("rev10", "10_lobe_review.py")
R11 = _load("rev11", "11_review2.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "rightonly"
RO, LO, H6, H7 = "RightOnly_test", R11.LO, R11.H6, R11.H7
BLOBS = {"rightonly_predictions.md": "a0150e76aadafc1170f666b982d03d626f37277f",
         "rightonly_predictions.csv": "c03834e756300d21ad378acbae24ba0f915b901b"}
md = L7.md


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)
    for fn, blob in BLOBS.items():
        h = subprocess.run(["git", "hash-object", str(LOBE / fn)], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        if h != blob:
            raise SystemExit(f"{fn}: blob {h} differs from the committed {blob} (0f97bb2); refusing to score")
    pred = pd.read_csv(LOBE / "rightonly_predictions.csv")

    cfg = load_config(ROOT, "config_lobe.yaml")
    f, Sd, man, ds = L8.load_all(cfg)
    if RO not in Sd:
        raise SystemExit("RightOnly_test is not in data/sims_lobe.csv")
    mlog = ds.masked_log
    n_mask = int((mlog["file"].str.contains(RO)).sum()) if len(mlog) else 0
    msk = R11.fmask(f, R11.LRBAND)
    cp = {d: R11.lr_cr_phase(Sd[d]) for d in (LO, RO)}
    ms = {d: R10.mirror_stats(f, Sd[d]) for d in (LO, RO)}
    X = {}
    for d in (LO, RO):
        x, nm, _, _ = features(f, Sd[d][None])
        X[d] = {ft: float(x[0][nm.index(ft)]) for ft in ("R31", "R21", "R32")}

    def value(d, stat, band):
        if stat.startswith("phase cross-ratio "):
            k = stat[len("phase cross-ratio "):]
            m_ = np.ones(len(f), bool) if band.startswith("band mean") else msk
            return float(cp[d][k][m_].mean())
        if stat.endswith("(mirror-invariant)"):
            return X[d][stat.split()[0]]
        return float(ms[d][stat][0])

    rows = []
    for _, r in pred.iterrows():
        lo_now, ro = value(LO, r.statistic, r.frequencies), value(RO, r.statistic, r.frequencies)
        tol = float(r["tolerance (clean ruler)"])
        mi = r.statistic.endswith("(mirror-invariant)")
        rows.append({"statistic": r.statistic, "frequencies": r.frequencies, "LeftOnly (committed)": r.LeftOnly,
                     "LeftOnly recomputed - committed": lo_now - r.LeftOnly,
                     "predicted RightOnly": r["predicted RightOnly"], "RightOnly observed": ro,
                     "tolerance (clean ruler)": tol, "RightOnly / ruler": np.nan if mi else abs(ro) / tol,
                     "|RO + LO|": np.nan if mi else abs(ro + r.LeftOnly),
                     "|RO - LO| (mirror-invariant)": abs(ro - r.LeftOnly) if mi else np.nan,
                     "sign flipped": np.nan if mi else bool(np.sign(ro) == -np.sign(r.LeftOnly)),
                     "within tolerance": bool((abs(ro - r.LeftOnly) if mi else abs(ro + r.LeftOnly)) <= tol),
                     "sign test informative": bool(r["sign test informative"])})
    sc = pd.DataFrame(rows)
    if sc["LeftOnly recomputed - committed"].abs().max() > 1e-9:
        raise SystemExit("LeftOnly no longer reproduces the committed values; scoring stopped")

    inf = sc[sc["sign test informative"]]
    p1_ok = inf["sign flipped"].astype(bool) & inf["within tolerance"]
    p1_frac = float(p1_ok.mean())
    p1 = p1_frac >= 0.8
    p2rows, p2 = [], True
    for bn, lo_count in (("band mean 3.2-4.2", 4), ("3.30-3.65 GHz", 9)):
        sub = sc[(sc.frequencies == bn) & sc.statistic.str.startswith("phase cross-ratio")]
        lo_n = int((sub["LeftOnly (committed)"].abs() / sub["tolerance (clean ruler)"] >= 3).sum())
        cnt = sub[sub["RightOnly / ruler"] >= 3]
        opp = bool(cnt["sign flipped"].astype(bool).all()) if len(cnt) else True
        ok = abs(len(cnt) - lo_count) <= 2 and opp
        p2 &= ok
        p2rows.append({"frequencies": bn, "LeftOnly count (committed)": lo_count, "LeftOnly count (recomputed)": lo_n,
                       "RightOnly count": len(cnt), "all counted with opposite sign": opp, "holds": ok,
                       "RightOnly statistics >= 3x": "; ".join(f"{s.replace('phase cross-ratio ', '')} "
                                                              f"({v:+.2f}, {q:.2f}x)" for s, v, q in
                                                              zip(cnt.statistic, cnt["RightOnly observed"],
                                                                  cnt["RightOnly / ruler"]))})
    p2t = pd.DataFrame(p2rows)
    pli = sc[sc.statistic.str.startswith("power LR index")]
    refl = sc[sc.statistic.isin(["power pair T2 refl. vs T6 refl.", "power pair T3 refl. vs T5 refl."])]
    p3 = bool((pli["RightOnly / ruler"] < 2).all() and refl["sign flipped"].astype(bool).all())
    mi = sc[sc.statistic.str.endswith("(mirror-invariant)")]
    p4 = bool(mi["within tolerance"].all())

    # P5: imaging-session mirror-test LR (operator rebuilt read-only, as in 11_review2 R1a)
    IM = R10.Imaging(f)
    Simg = {d: IM.SL.load_design(d, f)[0] for d in R11.SYM + [LO, RO]}
    p5rows = []
    for mth in IM.methods:
        for rn, ref in (("Healthy_sliced (7 passes)", H7), ("Healthy_sliced_new (6 passes)", H6)):
            Sr = Simg[ref]
            Tn = [IM.T(Simg[d], Sr, mth) for d in R11.SYM]
            yd = max(abs(IM.T(Simg[b], Sr, mth) - IM.T(Simg[a], Sr, mth)) for a, b in L8.PAIRS.values())
            tlo, tro = IM.T(Simg[LO], Sr, mth), IM.T(Simg[RO], Sr, mth)
            fr = R11.floor_rule(tro, Tn, yd)
            p5rows.append({"method": mth, "reference": rn, "T(LeftOnly)": tlo, "T(RightOnly)": tro,
                           "T(RO) + T(LO)": tro + tlo, "clean ruler": fr["clean ruler"],
                           "RightOnly / ruler": fr["ratio"], "sign flipped": bool(np.sign(tro) == -np.sign(tlo)),
                           "below 2x": fr["ratio"] < 2})
    p5t = pd.DataFrame(p5rows)
    prim = p5t[p5t.method.str.startswith("Tikhonov dS")]
    p5 = bool(prim["sign flipped"].all() and prim["below 2x"].all())

    # frozen rule (descriptive; committed expectation: not determined)
    rule = json.loads((ROOT / "results/04/frozen_rule.json").read_text())
    det = rule["detection_binary_R31"]
    edge = det["tau_dB"] - det["margin_dB"]
    R31y = float(pred.loc[pred.statistic == "R31 (mirror-invariant)", "tolerance (clean ruler)"].iloc[0])
    lab = {d: str(R10.rule_label(rule, "binary", X[d]["R31"])[0]) for d in (LO, RO)}
    st3 = {d: str(R10.rule_label(rule, "three", X[d]["R21"])[0]) for d in (LO, RO)}
    stm = {d: str(R10.rule_label(rule, "three_merged", X[d]["R32"])[0]) for d in (LO, RO)}
    frz = pd.DataFrame([{"design": d, "R31": X[d]["R31"], "binary label": lab[d],
                         "margin to AD edge (dB)": edge - X[d]["R31"],
                         "margin / R31 yardstick": (edge - X[d]["R31"]) / R31y,
                         "three (R21)": st3[d], "three_merged (R32)": stm[d]} for d in (LO, RO)])

    replicated = p1 and p2
    verdict = "REPLICATED" if replicated else "NOT REPLICATED"
    fam = sc.assign(family=sc.statistic.map(lambda s: R10.fam_of(s) if not s.endswith("(mirror-invariant)")
                                           else "mirror-invariant ratio"))
    asym = fam[~fam.statistic.str.endswith("(mirror-invariant)")].groupby("family").apply(
        lambda g: pd.Series({"n": len(g), "sign flipped": int(g["sign flipped"].astype(bool).sum()),
                             "within tolerance": int(g["within tolerance"].sum()),
                             "rms |RO + LO|": float(np.sqrt(np.mean(g["|RO + LO|"] ** 2))),
                             "rms |LO|": float(np.sqrt(np.mean(g["LeftOnly (committed)"] ** 2)))})).reset_index()

    summ = pd.DataFrame([
        {"prediction": "P1 sign flips within the clean ruler (>= 80% of informative)",
         "observed": f"{int(p1_ok.sum())}/{len(inf)} = {100 * p1_frac:.0f}% "
                     f"(sign flipped {int(inf['sign flipped'].astype(bool).sum())}/{len(inf)}; within tolerance "
                     f"{int(inf['within tolerance'].sum())}/{len(inf)})", "holds": p1},
        {"prediction": "P2 cross-ratio counts within +-2, opposite sign",
         "observed": "; ".join(f"{r_['frequencies']}: RO {r_['RightOnly count']} vs LO {r_['LeftOnly count (committed)']}, "
                               f"opposite sign {r_['all counted with opposite sign']}" for _, r_ in p2t.iterrows()),
         "holds": p2},
        {"prediction": "P3 power LR indices < 2x; reflection pairs flip",
         "observed": "LR index / ruler " + ", ".join(f"{v:.2f}" for v in pli["RightOnly / ruler"]) + "; reflection pairs "
                     + ", ".join(f"{v:+.3f} dB" for v in refl["RightOnly observed"]), "holds": p3},
        {"prediction": "P4 R31/R21/R32 = LeftOnly within the yardstick",
         "observed": ", ".join(f"{s.split()[0]} {v:.3f} (|diff| {dd:.3f} vs {t:.3f})" for s, v, dd, t in
                               zip(mi.statistic, mi["RightOnly observed"], mi["|RO - LO| (mirror-invariant)"],
                                   mi["tolerance (clean ruler)"])), "holds": p4},
        {"prediction": "P5 imaging LR sign flips, < 2x the max floor (Tikhonov dS)",
         "observed": "; ".join(f"{r_['reference']}: T {r_['T(RightOnly)']:+.2f} ({r_['RightOnly / ruler']:.2f}x)"
                               for _, r_ in prim.iterrows()), "holds": p5},
        {"prediction": "VERDICT (replicated iff P1 and P2)", "observed": verdict, "holds": replicated}])
    sc.to_csv(OUT / "scored.csv", index=False)
    summ.to_csv(OUT / "summary.csv", index=False)
    p5t.to_csv(OUT / "imaging_lr.csv", index=False)

    L = [f"# RightOnly_test: scoring of the C6 predictions committed at 0f97bb2 (code {gh})", "",
         "Predictions read unchanged (git blobs checked: " + ", ".join(f"{k} {v[:7]}" for k, v in BLOBS.items()) + "). "
         "Status of the phase finding under test: **post hoc**. Scored exactly as written in rightonly_predictions.md. "
         f"RightOnly_test: stop rule 1 (user); passes / final dS / elements not supplied; glitch mask (-30 dB) masked "
         f"{n_mask} point(s). LeftOnly values recomputed from the raw file match the committed ones "
         f"(max |difference| {sc['LeftOnly recomputed - committed'].abs().max():.1e}).", "",
         f"## Verdict: **{verdict}** (replicated only if P1 and P2 both hold)", "", md(summ), "",
         "## P2 detail", md(p2t, ".2f"), "", "## P5 detail (imaging operator rebuilt read-only)", md(p5t, ".2f"), "",
         "## By family (all left-right statistics; |RO + LO| is the residual asymmetry the mirror image does not cancel)",
         md(asym, ".3f"), "",
         "## Frozen rule (descriptive; the committed expectation was 'not determined')", md(frz, ".3f"), "",
         "## Every statistic", md(sc, ".3f"), ""]
    if not replicated:
        failed = ", ".join(n for n, ok in (("P1", p1), ("P2", p2)) if not ok)
        L += [f"Not replicated ({failed} failed). As committed at 0f97bb2 and confirmed by the user, the post-hoc "
              "left-right phase finding is therefore retracted as numerical.", ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12]))
    print(md(p2t, ".2f"))
    print(md(asym, ".3f"))
    print(md(frz, ".3f"))


if __name__ == "__main__":
    main()
