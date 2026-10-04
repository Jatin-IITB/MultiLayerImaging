"""POST HOC (written 2026-10-04 after the Test_B truth and the rotated healthy nulls Null_rot07 / Null_rot19 arrived).

    python scripts/17_posthoc_nulls.py [--n 300]

Writes results/05_lobe/posthoc_nulls/{report.md, *.csv}. Nothing committed earlier is changed: frozen rules,
thresholds, protocols, predictions, submitted estimates and committed verdicts stand as scored. Everything here is
post hoc.

Sections
  QC   new files (Null_rot07, Null_rot19, RightOnly_test, Test_B): passivity, worst |Sij|/|Sji| magnitude difference and
       worst relative non-reciprocity with location, points masked by the frozen -30 dB glitch rule.
  V    the user's quoted null numbers, re-derived (second-neighbour power pairs, reflection pairs, 3.4 GHz phase pairs,
       per-antenna neighbour-phase spread).
  A    0.3(a) pass gap: |T(LO) + T(RO)| (antisymmetric statistics; = LeftOnly minus mirrored RightOnly) and |Q(RO) - Q(LO)|
       (R31, R21, R32) against the three pass-5 vs pass-6 twin differences |T(a) - T(b)| of Mild, Moderate, Severe,
       same statistics, same frequencies. Consistent with the pass gap if within the largest twin difference.
  B    0.3(b) rulers rebuilt with the rotated nulls: NULL11 = the 9 symmetric designs + Null_rot07 + Null_rot19.
       R1c floor = max |T| over NULL11 (leave-one-out for a null scored as a target); imaging mirror-test LR floor;
       re-mesh yardstick for R31 / R21 / R32 / front-back indices = max(one-pass yardstick, |Q(rot) - Q(H6)|);
       pattern-fit null contrast and healthy-twin ring mean with the rotated nulls against Healthy_sliced_new.
  C    survival of every ruler-dependent claim (MODEL_CARD 6.2) and every Test_B and RightOnly reading, old vs new rulers.
  Q2   R21 and R32 of Test_B, LeftOnly, RightOnly and the two Mild lobe designs against the frozen stage edges, with the
       total cortical retreat (sum of e over the six sectors).
  Q3   mirror-test votes of Test_B (diagonal pair) vs LeftOnly / RightOnly (one-sided), with the per-sector-pair
       reflection statistics.
  Q4   pattern fit: best vs runner-up residual in the validation designs and Test_B; the rotated nulls as targets.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adstage.config import load_config  # noqa: E402
from adstage.features.metrics import to_ring_order  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.io.touchstone import read_touchstone  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
L9 = _load("lobe09", "09_lobe_tests.py")
R10 = _load("rev10", "10_lobe_review.py")
R11 = _load("rev11", "11_review2.py")
T15 = _load("tb15", "15_test_b.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "posthoc_nulls"
H6, H7, LO, RO, TB, MCI = R11.H6, R11.H7, R11.LO, "RightOnly_test", "Test_B", R11.MCI
N7, N19 = "Null_rot07", "Null_rot19"
ROT = [N7, N19]
SYM9 = list(R11.SYM)
NULL11 = SYM9 + ROT
TWINS = {"Mild 5->6": ("Mild_lobe", "Mild_lobe_new"), "Moderate 5->6": ("Moderate_lobe", "Moderate_lobe_c3"),
         "Severe 5->6": ("Severe_lobe", "Severe_lobe_c3")}
RATIOS = ("R31", "R21", "R32")
FBK = ("index: front-back, all paths", "index: front-back, neighbour paths")
W = 0.4                                   # smearing chosen at 89af4b3 (protocol d3a4bbf)
NC_OLD, HG_OLD = 0.21167, 1.11103         # protocol rulers (validation.md at 89af4b3), recomputed below as a check
md = L7.md
tier = R10.tier


def retreat(notes):
    m = re.search(r"e = ([\d./]+) mm", str(notes))
    return float(sum(float(v) for v in m.group(1).split("/"))) if m else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)
    cfg = load_config(ROOT, "config_lobe.yaml")
    rule = json.loads((ROOT / "results/04/frozen_rule.json").read_text())
    f, Sd, man, ds = L8.load_all(cfg)
    for d in ROT + [RO, TB]:
        if d not in Sd:
            raise SystemExit(f"{d} missing from data/sims_lobe.csv")
    L = [f"# POST HOC: rotated healthy nulls, Test_B truth, pass gap (code {gh})", "",
         "Everything below was computed after the Test_B truth and the rotated nulls arrived. Frozen rules, thresholds, "
         "protocols, predictions, submitted estimates and committed verdicts are unchanged and stand as scored.", ""]
    summ = []

    # ================================================================== QC
    qc = []
    for d in ROT + [RO, TB]:
        t = read_touchstone(ROOT / cfg["data"]["raw_dir"] / f"new_with_slices_{d}.s6p")
        s = t.s
        sv = np.linalg.svd(s, compute_uv=False)
        off = ~np.eye(6, dtype=bool)
        mag = np.abs(20 * np.log10(np.abs(s)) - 20 * np.log10(np.abs(np.swapaxes(s, -1, -2))))
        mag[:, ~off] = 0
        fi, i, j = np.unravel_index(np.argmax(mag), mag.shape)
        rel = np.abs(s - np.swapaxes(s, -1, -2)) / np.maximum(np.abs(s), 1e-30)
        rel[:, ~off] = 0
        nm = int(ds.masked_log["file"].str.contains(d).sum()) if len(ds.masked_log) else 0
        where = ds.masked_log[ds.masked_log["file"].str.contains(d)] if nm else pd.DataFrame()
        qc.append({"design": d, "points": len(t.f_hz), "band GHz": f"{t.f_hz[0] / 1e9:.2f}-{t.f_hz[-1] / 1e9:.2f}",
                   "max singular value^2": float((sv ** 2).max()),
                   "worst ||Sij|-|Sji|| (dB)": float(mag.max()),
                   "at": f"{t.f_hz[fi] / 1e9:.3f} GHz, ports {i + 1}-{j + 1}",
                   "worst |Sij-Sji|/|Sij| (dB)": float(20 * np.log10(rel.max())),
                   "masked points (-30 dB rule)": nm,
                   "masked at": "; ".join(f"{r.f_GHz:.3f} GHz ports {int(r.port_i)}-{int(r.port_j)}" for _, r in where.iterrows())
                   if nm else ""})
    qct = pd.DataFrame(qc)
    qct.to_csv(OUT / "QC_new_files.csv", index=False)
    L += ["## QC of the new files (raw, before masking)", md(qct, ".3f"), ""]

    # ================================================================== mirror statistics on every design
    MI = T15.Mirror(f, Sd)
    tab = MI.table                                            # the 88 antisymmetric rows of the C6 table
    keys = [(r.statistic, r.frequencies) for _, r in tab.iterrows()]
    inf_keys = [(r.statistic, r.frequencies) for _, r in MI.inf.iterrows()]
    allv = {d: MI.values(d) for d in NULL11 + [LO, RO, TB]}

    def yard_of(k):
        if k[0].startswith("phase cross-ratio "):
            c = k[0][len("phase cross-ratio "):]
            m_ = np.ones(len(f), bool) if k[1].startswith("band mean") else MI.msk
            return max(abs(float(MI.cp(b)[c][m_].mean() - MI.cp(a)[c][m_].mean())) for a, b in L8.PAIRS.values())
        return max(abs(allv_get(b, k) - allv_get(a, k)) for a, b in L8.PAIRS.values())

    def allv_get(d, k):
        if d not in allv:
            allv[d] = MI.values(d)
        return allv[d][k]

    yards = {k: yard_of(k) for k in keys}

    def floor(k, nulls, exclude=None):
        v = [abs(allv_get(d, k)) for d in nulls if d != exclude]
        i = int(np.argmax(v))
        return float(v[i]), [d for d in nulls if d != exclude][i]

    def ruler(k, nulls, exclude=None):
        return max(floor(k, nulls, exclude)[0], yards[k])

    # ================================================================== V: the user's quoted numbers
    pp = {d: R11.pair_phase(Sd[d]) for d in NULL11 + [LO, TB, RO]}
    i34 = int(np.argmin(np.abs(f - 3.4e9)))
    vrows = []
    for st in ("power pair T1-T3 vs T1-T5", "power pair T2-T4 vs T4-T6", "power pair T2 refl. vs T6 refl.",
               "power pair T3 refl. vs T5 refl."):
        k = (st, "band mean 3.2-4.2")
        vrows.append({"quantity": f"{st} (band mean, dB)", **{d: allv_get(d, k) for d in ROT},
                      "max |.| over the 9 symmetric": floor(k, SYM9)[0], LO: allv_get(LO, k), TB: allv_get(TB, k)})
    for st in ("T1-T2 vs T1-T6", "T2-T5 vs T3-T6"):
        vrows.append({"quantity": f"phase pair {st} at 3.4 GHz (deg)", **{d: float(pp[d][st][i34]) for d in ROT},
                      "max |.| over the 9 symmetric": max(abs(float(pp[d][st][i34])) for d in SYM9),
                      H6 + " (alone)": float(pp[H6][st][i34]), LO: float(pp[LO][st][i34]), TB: float(pp[TB][st][i34])})
    Yh = {d: T15.nb_phase(f, Sd[d], Sd[H6]) for d in ROT + [TB, H7, MCI, LO, RO]}
    for d in ROT + [TB]:
        y = Yh[d]
        vrows.append({"quantity": f"per-antenna neighbour phase vs {H6}: {d} (deg)",
                      "values T1..T6": ", ".join(f"{v:+.2f}" for v in y), "range max-min": float(y.max() - y.min()),
                      "rms about the ring mean (= contrast r0)": float(np.std(y))})
    vt = pd.DataFrame(vrows)
    vt.to_csv(OUT / "V_user_numbers.csv", index=False)
    yb = Yh[TB]
    others = [k for k in range(6) if k not in (1, 4)]
    elev = {f"T{k + 1}": float(np.mean(yb[others]) - yb[k]) for k in (1, 4)}
    L += ["## V. The user's quoted numbers, re-derived", md(vt, ".3f"), "",
          f"Test_B T2 / T5 delay beyond the mean of the other four antennas: T2 {elev['T2']:.2f} deg, T5 {elev['T5']:.2f} deg; "
          f"range max-min {float(yb.max() - yb.min()):.2f} deg.", ""]

    # ================================================================== A: pass gap (0.3a)
    Xr = {}
    for d in [LO, RO] + [x for p in TWINS.values() for x in p] + [H6] + ROT:
        x, nm_, _, _ = features(f, Sd[d][None])
        Xr[d] = {r: float(x[0][nm_.index(r)]) for r in RATIOS}
    arows = []
    for k in keys:
        dlr = abs(allv_get(LO, k) + allv_get(RO, k))
        tw = {n: abs(allv_get(a, k) - allv_get(b, k)) for n, (a, b) in TWINS.items()}
        arows.append({"statistic": k[0], "frequencies": k[1], "informative (C6)": k in inf_keys,
                      "|T(LO) + T(RO)|": dlr, **{f"twin {n}": v for n, v in tw.items()}, "max twin": max(tw.values()),
                      "ratio to max twin": dlr / max(tw.values()), "within max twin": dlr <= max(tw.values()),
                      "C6 tolerance (9-null ruler)": ruler(k, SYM9), "within C6 tolerance": dlr <= ruler(k, SYM9)})
    for r in RATIOS:
        dlr = abs(Xr[RO][r] - Xr[LO][r])
        tw = {n: abs(Xr[a][r] - Xr[b][r]) for n, (a, b) in TWINS.items()}
        arows.append({"statistic": f"{r} (mirror-invariant)", "frequencies": "band mean 3.2-4.2", "informative (C6)": False,
                      "|T(LO) + T(RO)|": dlr, **{f"twin {n}": v for n, v in tw.items()}, "max twin": max(tw.values()),
                      "ratio to max twin": dlr / max(tw.values()), "within max twin": dlr <= max(tw.values()),
                      "C6 tolerance (9-null ruler)": np.nan, "within C6 tolerance": np.nan})
    at = pd.DataFrame(arows)
    at.to_csv(OUT / "A_pass_gap.csv", index=False)
    ai = at[at["informative (C6)"]]
    fail = ai[~ai["within C6 tolerance"].astype(bool)]
    a_sum = {"26 informative: within the largest pass-5/6 twin difference": f"{int(ai['within max twin'].sum())}/26",
             "the 14 that failed the C6 tolerance: within the largest twin difference": f"{int(fail['within max twin'].sum())}/{len(fail)}",
             "all 88 antisymmetric statistics: within the largest twin difference": f"{int(at[~at.statistic.str.endswith('invariant)')]['within max twin'].sum())}/88",
             "R31 / R21 / R32: within the largest twin difference": ", ".join(
                 f"{r} {v:.3f} vs {m:.3f}" for r, v, m in zip(RATIOS, at.tail(3)["|T(LO) + T(RO)|"], at.tail(3)["max twin"]))}
    L += ["## A. 0.3(a) Pass gap: LeftOnly minus mirrored RightOnly against the three pass-5 vs pass-6 twins",
          "RightOnly stopped at pass 5 (dS 0.0197, 789k elements), LeftOnly at pass 6 (dS 0.0147, 941k). The twins are the "
          "same design refined by one pass (same initial mesh); LeftOnly and RightOnly are independent meshes with a pass gap, "
          "so the twin differences are a lower bound on what a pass gap plus a re-mesh can do.",
          md(pd.DataFrame([a_sum]).T.reset_index().rename(columns={"index": "summary", 0: "count"})), "",
          "26 informative statistics:", md(ai.drop(columns=["informative (C6)"]), ".3f"), "",
          "R31 / R21 / R32:", md(at.tail(3).drop(columns=["informative (C6)", "C6 tolerance (9-null ruler)",
                                                          "within C6 tolerance"]), ".3f"), ""]

    # ================================================================== B: rulers with the rotated nulls (0.3b)
    brows = []
    for k in keys:
        f9, w9 = floor(k, SYM9)
        f11, w11 = floor(k, NULL11)
        brows.append({"statistic": k[0], "frequencies": k[1], "informative (C6)": k in inf_keys, "yardstick": yards[k],
                      "floor 9": f9, "floor 11": f11, "set by": w11, "ruler 9": max(f9, yards[k]),
                      "ruler 11": max(f11, yards[k]), "ruler 11 / ruler 9": max(f11, yards[k]) / max(f9, yards[k]),
                      **{f"{d} / ruler 9": abs(allv_get(d, k)) / max(f9, yards[k]) for d in (LO, RO, TB)},
                      **{f"{d} / ruler 11": abs(allv_get(d, k)) / max(f11, yards[k]) for d in (LO, RO, TB)}})
    bt = pd.DataFrame(brows)
    bt.to_csv(OUT / "B_mirror_rulers.csv", index=False)
    fam = bt.assign(family=bt.statistic.map(R10.fam_of)).groupby("family").agg(
        n=("statistic", "count"), raised=("ruler 11 / ruler 9", lambda v: int((v > 1.0001).sum())),
        max_raise=("ruler 11 / ruler 9", "max")).reset_index()

    # imaging LR
    IM = R10.Imaging(f)
    Simg = {d: IM.SL.load_design(d, f)[0] for d in NULL11 + [LO, RO, TB]}
    irows = []
    for mth in IM.methods:
        for rn, ref in (("Healthy_sliced", H7), ("Healthy_sliced_new", H6)):
            Sr = Simg[ref]
            T = {d: IM.T(Simg[d], Sr, mth) for d in NULL11 + [LO, RO, TB]}
            yd = max(abs(IM.T(Simg[b], Sr, mth) - IM.T(Simg[a], Sr, mth)) for a, b in L8.PAIRS.values())
            f9 = max(abs(T[d]) for d in SYM9)
            f11 = max(abs(T[d]) for d in NULL11)
            row = {"method": mth, "reference": rn, **{f"T {d}": T[d] for d in ROT}, "floor 9": f9, "floor 11": f11,
                   "yardstick": yd}
            for d in (LO, RO, TB):
                row[f"{d} / ruler 9"] = abs(T[d]) / max(f9, yd)
                row[f"{d} / ruler 11"] = abs(T[d]) / max(f11, yd)
                row[f"T {d}"] = T[d]
            irows.append(row)
    it = pd.DataFrame(irows)
    it.to_csv(OUT / "B_imaging_LR_rulers.csv", index=False)

    # re-mesh yardstick for ratios and FB indices; label margins
    R = L8.rulers(f, Sd, cfg, args.n, qfn=L9.ext_quantities)
    Q = R["Q"]
    rm = []
    for k in RATIOS + FBK:
        diffs = {d: float(Q[d][k][0] - Q[H6][k][0]) for d in ROT}
        y_old = R["yard"][k]
        rm.append({"quantity": k, "one-pass yardstick": y_old, **{f"{d} - {H6}": v for d, v in diffs.items()},
                   "re-mesh max": max(abs(v) for v in diffs.values()),
                   "new yardstick": max(y_old, max(abs(v) for v in diffs.values())),
                   "new / old": max(y_old, max(abs(v) for v in diffs.values())) / y_old})
    rmt = pd.DataFrame(rm).set_index("quantity")
    rmt.reset_index().to_csv(OUT / "B_remesh_yardstick.csv", index=False)
    r6 = pd.read_csv(LOBE / "review2" / "R6_A28_rulers.csv")
    tb_sd = float(r6[r6.rule == "binary"]["boundary SD"].iloc[0])
    cfg_u = load_config(ROOT, "config_repeats.yaml")
    du = load_dataset(cfg_u, ROOT)
    Xu, nu, _, _ = features(du.f_hz, to_ring_order(du.S, du.port_to_ant))
    ucls = list(du.classes)
    rng = np.random.default_rng([cfg["seed"], 111])
    fro = {k: sorted(float(p.split(" at ")[1]) for p in v.split(", ")) for k, v in L7.boundaries(rule).items()}
    bfro = {"three": fro["three (R21)"], "three_merged": fro["three_merged (R32)"]}
    bsd = {}
    for sch, (ft, cls) in {"three": ("R21", [["Normal"], ["Mild"], ["Severe"]]),
                           "three_merged": ("R32", [["Normal"], ["Mild", "Moderate"], ["Severe"]])}.items():
        sols = [[s for s, c in enumerate(ucls) if c in mem] for mem in cls]
        bb = [sorted(0.5 * (mu[i] + mu[i + 1]) for i in range(2)) for mu in
              ([np.mean([float(Xu[s][nu.index(ft)]) for s in rng.choice(ss, len(ss))]) for ss in sols] for _ in range(3000))]
        bsd[sch] = np.array(bb).std(0, ddof=1)
    lab_designs = list(R11.STAGES["lobe_A"]) + list(R11.STAGES["lobe_B"]) + [LO, MCI, RO, TB]
    mrows = []
    for d in lab_designs:
        for sch, ft in (("binary", "R31"), ("three", "R21"), ("three_merged", "R32")):
            x = float(Q[d][ft][0])
            lab, mg = R10.edge_margin(rule, sch, x)
            sb = tb_sd if sch == "binary" else float(bsd[sch][int(np.argmin([abs(x - b) for b in bfro[sch]]))])
            s05 = R["sd"]["spread ±0.5 dB"][ft] / np.sqrt(2)
            yo, yn = rmt.loc[ft, "one-pass yardstick"], rmt.loc[ft, "new yardstick"]
            mrows.append({"design": d, "rule": sch, "label": lab, "margin dB": mg,
                          "A1 old": abs(mg) / max(yo, sb), "A1 new": abs(mg) / max(yn, sb),
                          "quadrature old": abs(mg) / np.sqrt(yo ** 2 + sb ** 2 + s05 ** 2),
                          "quadrature new": abs(mg) / np.sqrt(yn ** 2 + sb ** 2 + s05 ** 2)})
    mt = pd.DataFrame(mrows)
    mt.to_csv(OUT / "B_label_margins.csv", index=False)
    fbrows = []
    for d in (TB, LO, RO):
        for k in FBK:
            v = float(Q[d][k][0] - Q[H6][k][0])
            ro_, rn_ = max(R["yard"][k], R["fdiff"][k]), max(rmt.loc[k, "new yardstick"], R["fdiff"][k])
            fbrows.append({"design": d, "index": k, "value dB (vs H6)": v, "ratio old": abs(v) / ro_, "ratio new": abs(v) / rn_})
    fbt = pd.DataFrame(fbrows)

    # pattern-fit rulers with the rotated nulls
    nc_chk = max(float(np.std(T15.nb_phase(f, Sd[a], Sd[b]))) for a, b in T15.UNIFORM)
    hg_chk = abs(float(np.mean(T15.nb_phase(f, Sd[H7], Sd[H6]))))
    nc_new = max(nc_chk, *(float(np.std(Yh[d])) for d in ROT))
    hg_new = max(hg_chk, *(abs(float(np.mean(Yh[d]))) for d in ROT))
    L += ["## B. 0.3(b) Rulers rebuilt with the rotated nulls (NULL11 = 9 symmetric + Null_rot07 + Null_rot19)",
          "Mirror statistics (88): how many rulers the rotated nulls raise, by family:", md(fam, ".2f"), "",
          "Imaging mirror-test LR (operator rebuilt read-only):", md(it, ".2f"), "",
          "Re-mesh yardstick (same physics, rotated mesh, same pass count as Healthy_sliced_new):",
          md(rmt.reset_index(), ".3f"), "",
          f"Pattern-fit rulers: null contrast {nc_chk:.3f} deg (protocol) -> {nc_new:.3f} deg; healthy-twin |ring mean| "
          f"{hg_chk:.3f} -> {hg_new:.3f} deg.", ""]

    # ================================================================== Q4: pattern fit
    def fits_of(y):
        out = []
        for x in T15.PATS:
            r, coef = T15.fit_pattern(y, x, W)
            if coef[1] < 0:
                out.append((r, "".join(str(i + 1) for i in range(6) if x[i])))
        return sorted(out)

    truth = T15.truth_of(man)
    refd = T15.ref_of(man)
    vdes = ["Mild_lobe", "Mild_lobe_new", "Moderate_lobe", "Moderate_lobe_c3", LO, RO]
    grows = []
    for d in vdes + [TB]:
        y = T15.nb_phase(f, Sd[d], Sd[refd[d]] if d != TB else Sd[H6])
        fs = fits_of(y)
        loc = T15.localise(y, W, nc_chk, hg_chk)
        grows.append({"design": d, "truth": truth.get(d, ""), "best": fs[0][1], "best residual": fs[0][0],
                      "runner-up": fs[1][1], "runner-up residual": fs[1][0], "gap (deg)": fs[1][0] - fs[0][0],
                      "gap / null contrast": (fs[1][0] - fs[0][0]) / nc_chk, "runner-up / best": fs[1][0] / fs[0][0],
                      "best = truth": fs[0][1] == truth.get(d, ""),
                      "all sectors certain (>= 2x)": all(c != "uncertain" for c in loc["sector calls"]),
                      "contrast / null": loc["contrast / null"]})
    gt = pd.DataFrame(grows)
    gt.to_csv(OUT / "Q4_best_vs_runnerup.csv", index=False)
    nrows = []
    for d in ROT + [H7, MCI]:
        y = Yh[d]
        for lab_, nc, hg in (("protocol rulers", nc_chk, hg_chk), ("rulers incl. rotated nulls (leave-one-out)",
                                                                   max(nc_chk, *(float(np.std(Yh[o])) for o in ROT if o != d)),
                                                                   max(hg_chk, *(abs(float(np.mean(Yh[o]))) for o in ROT if o != d)))):
            loc = T15.localise(y, W, nc, hg)
            fs = fits_of(y)
            nrows.append({"target (vs Healthy_sliced_new)": d, "rulers": lab_, "best pattern": fs[0][1],
                          "best residual": fs[0][0], "r0": loc["r0 (relative-pattern rms, deg)"],
                          "contrast / null": loc["contrast / null"], "accepted": loc["accepted"],
                          "pattern call": loc["pattern call"], "ring mean g": loc["ring mean g (deg)"],
                          "|g| / healthy twin": loc["|g| / healthy-twin |g|"]})
    nt = pd.DataFrame(nrows)
    nt.to_csv(OUT / "Q4_rotated_nulls_as_targets.csv", index=False)
    loc_tb_new = T15.localise(yb, W, nc_new, hg_new)
    L += ["## Q4. Pattern fit: best vs runner-up, and the rotated healthy heads as targets",
          f"w = {W} (89af4b3); protocol rulers null contrast {nc_chk:.3f} deg, healthy twin {hg_chk:.3f} deg.",
          md(gt, ".3f"), "", "Rotated healthy heads (and the old nulls) as targets against Healthy_sliced_new:",
          md(nt, ".3f"), "",
          f"Test_B with the rulers incl. the rotated nulls: contrast {loc_tb_new['contrast / null']:.2f}x, accepted "
          f"{loc_tb_new['accepted']}, call {loc_tb_new['pattern call']}, sector confidences "
          + ", ".join(f"S{k + 1} {c} {q:.1f}" for k, (c, q) in enumerate(zip(loc_tb_new['sector calls'],
                                                                              loc_tb_new['sector confidence']))), ""]

    # ================================================================== Q3: mirror votes
    q3 = []
    for k in inf_keys:
        ants = sorted(set(re.findall(r"T\d", k[0])))
        row = {"statistic": k[0], "frequencies": k[1], "antennas": "".join(ants)}
        for d in (LO, RO, TB):
            v = allv_get(d, k)
            r9, r11 = abs(v) / ruler(k, SYM9), abs(v) / ruler(k, NULL11)
            row[f"{d}"] = v
            row[f"{d} / r9"] = r9
            row[f"{d} / r11"] = r11
        row["Test_B vote (r9 >= 2)"] = ("left" if np.sign(row[TB]) == np.sign(row[LO]) else "right") if row[f"{TB} / r9"] >= 2 else ""
        row["Test_B vote (r11 >= 2)"] = ("left" if np.sign(row[TB]) == np.sign(row[LO]) else "right") if row[f"{TB} / r11"] >= 2 else ""
        q3.append(row)
    q3t = pd.DataFrame(q3)
    q3t.to_csv(OUT / "Q3_mirror_votes.csv", index=False)
    v9 = q3t["Test_B vote (r9 >= 2)"].value_counts().to_dict()
    v11 = q3t["Test_B vote (r11 >= 2)"].value_counts().to_dict()
    L += ["## Q3. Mirror-test votes: Test_B (diagonal S2 + S5) vs LeftOnly / RightOnly (one-sided)",
          f"Votes (|T| >= 2x ruler) with the 9-null rulers: {v9}; with the 11-null rulers: {v11}.",
          md(q3t, ".2f"), ""]

    # ================================================================== Q2: staging
    man_i = man.set_index("design")
    srows = []
    for d in [H6, H7, LO, RO, TB, "Mild_lobe", "Mild_lobe_new", "Moderate_lobe"]:
        r21, r32 = float(Q[d]["R21"][0]), float(Q[d]["R32"][0])
        ref = H7 if d in ("Mild_lobe_new", H7) else H6
        srows.append({"design": d, "total cortical retreat (mm, sum of e)": retreat(man_i.loc[d, "notes"]),
                      "materials": "Mild" if d in (LO, RO, TB, "Mild_lobe", "Mild_lobe_new") else
                      ("Moderate" if d == "Moderate_lobe" else "healthy"),
                      "R21": r21, "R21 - matched healthy": r21 - float(Q[ref]["R21"][0]),
                      "three label": str(R10.rule_label(rule, "three", r21)[0]),
                      "R21 - Normal|Mild edge": r21 - bfro["three"][0],
                      "R32": r32, "merged label": str(R10.rule_label(rule, "three_merged", r32)[0]),
                      "R32 - Mild+Moderate|Normal edge": r32 - bfro["three_merged"][1]})
    iu = {Path(str(x)).name: s for s, x in enumerate(du.files)}
    for fn in ("new_Healthy.s6p", "new_MildAD.s6p", "brain_sevem_layer_Healthy.s6p", "Brain_sevem_layer_MildAD.s6p"):
        s = iu[fn]
        r21, r32 = float(Xu[s][nu.index("R21")]), float(Xu[s][nu.index("R32")])
        href = "new_Healthy.s6p" if fn.startswith("new") else "brain_sevem_layer_Healthy.s6p"
        srows.append({"design": f"uniform {fn}", "total cortical retreat (mm, sum of e)": 0.0 if "Healthy" in fn else 6 * (83 - 70.55),
                      "materials": "healthy" if "Healthy" in fn else "Mild", "R21": r21,
                      "R21 - matched healthy": r21 - float(Xu[iu[href]][nu.index("R21")]),
                      "three label": str(R10.rule_label(rule, "three", r21)[0]), "R21 - Normal|Mild edge": r21 - bfro["three"][0],
                      "R32": r32, "merged label": str(R10.rule_label(rule, "three_merged", r32)[0]),
                      "R32 - Mild+Moderate|Normal edge": r32 - bfro["three_merged"][1]})
    st = pd.DataFrame(srows)
    st.to_csv(OUT / "Q2_staging.csv", index=False)
    mild = st[st.materials == "Mild"]
    slope = np.polyfit(mild["total cortical retreat (mm, sum of e)"], mild["R21 - matched healthy"], 1)
    edge_mm = (bfro["three"][0] - float(Q[H6]["R21"][0]) - slope[1]) / slope[0]
    L += ["## Q2. Staging: R21 and R32 against the frozen stage edges",
          f"Frozen edges: three (R21) Normal|Mild {bfro['three'][0]:.2f}, Mild|Severe {bfro['three'][1]:.2f} dB; merged (R32) "
          f"Mild+Moderate|Normal {bfro['three_merged'][1]:.2f}, Severe|Mild+Moderate {bfro['three_merged'][0]:.2f} dB.",
          md(st, ".3f"), "",
          f"Mild-material designs: R21 rise vs total cortical retreat, linear fit slope {slope[0] * 10:.3f} dB per 10 mm, "
          f"intercept {slope[1]:+.3f} dB. The Normal|Mild edge corresponds to about {edge_mm:.0f} mm of total retreat "
          "relative to Healthy_sliced_new.", ""]

    # ================================================================== C: survival of claims and readings
    def cnt(d, nulls, band, thr=3):
        sub = [k for k in keys if k[0].startswith("phase cross-ratio") and k[1] == band]
        return sum(abs(allv_get(d, k)) / ruler(k, nulls, d if d in nulls else None) >= thr for k in sub)

    def p1(nulls):
        return sum((np.sign(allv_get(RO, k)) == -np.sign(allv_get(LO, k)))
                   and abs(allv_get(RO, k) + allv_get(LO, k)) <= ruler(k, nulls) for k in inf_keys)

    def mlab(d, sch, col):
        r_ = mt[(mt.design == d) & (mt.rule == sch)].iloc[0]
        return float(r_[col])

    def n3(col):
        return int((mt[mt.design.isin(R11.LOBE_ALL)][col] >= 3).sum())

    def ratio_of(d, st_):
        k = (st_, "band mean 3.2-4.2")
        return abs(allv_get(d, k)) / ruler(k, SYM9), abs(allv_get(d, k)) / ruler(k, NULL11)

    imp = it[(it.method.str.startswith("Tikhonov dS")) & (it.reference == "Healthy_sliced_new")].iloc[0]
    res = {d: R11.resonance(f, Sd[d]) for d in NULL11 + [LO]}
    lrres = {d: (res[d][1][0] + res[d][2][0]) / 2 - (res[d][5][0] + res[d][4][0]) / 2 for d in res}
    nbp = {}
    for st_ in ("T2-T3 vs T5-T6", "T3-T4 vs T4-T5", "T1-T2 vs T1-T6"):
        v = {d: float(pp[d][st_][MI.msk].mean()) for d in NULL11 + [LO, TB, RO]}
        nbp[st_] = (v[LO], max(abs(v[d]) for d in SYM9), max(abs(v[d]) for d in NULL11))
    ms = MI.side(TB)
    votes11 = q3t[q3t["Test_B vote (r11 >= 2)"] != ""]
    side11 = ("none" if len(votes11) < 3 else ("left" if (votes11["Test_B vote (r11 >= 2)"] == "left").mean() >= 0.8
                                               else ("right" if (votes11["Test_B vote (r11 >= 2)"] == "right").mean() >= 0.8 else "mixed")))
    rows = []

    def add(item, old, new, survives, note=""):
        rows.append({"claim / reading": item, "old rulers (9 nulls, one-pass yardstick)": old,
                     "new rulers (11 nulls, re-mesh yardstick)": new, "survives": survives, "note": note})
    a1o, a1n = n3("A1 old"), n3("A1 new")
    add("2/11 lobe labels >= 3x (A1), all 30", f"{a1o}/30", f"{a1n}/30", "yes" if a1n == a1o else "weakened")
    for d in ("Healthy_sliced_new", "Healthy_sliced", "Mild_lobe", "Mild_lobe_new", "Moderate_lobe", "Moderate_lobe_c3"):
        o, n_ = mlab(d, "binary", "quadrature old"), mlab(d, "binary", "quadrature new")
        add(f"2 detection {d} (quadrature +-0.5 dB)", f"{o:.2f}x", f"{n_:.2f}x", "yes" if n_ >= 3 else ("sensitive" if n_ >= 2 else "no"))
    for d in ("Severe_lobe", "Severe_lobe_c3", LO, MCI):
        o, n_ = mlab(d, "binary", "quadrature old"), mlab(d, "binary", "quadrature new")
        add(f"3 detection {d} (quadrature)", f"{o:.2f}x", f"{n_:.2f}x", "unchanged verdict" if (o >= 3) == (n_ >= 3) and (o >= 2) == (n_ >= 2) else "verdict changes")
    add("6 mask dependency: Mild_lobe_new R31 shift 0.319 dB / yardstick", f"{0.319 / rmt.loc['R31', 'one-pass yardstick']:.2f}x",
        f"{0.319 / rmt.loc['R31', 'new yardstick']:.2f}x", "yes" if 0.319 / rmt.loc['R31', 'new yardstick'] >= 2 else "weakened")
    add("10 R21 lobe stage gaps (smallest 0.489 dB, lobe_B Mild|Moderate) / 2 x yardstick",
        f"{0.489 / (2 * rmt.loc['R21', 'one-pass yardstick']):.2f}x", f"{0.489 / (2 * rmt.loc['R21', 'new yardstick']):.2f}x",
        "yes" if 0.489 / (2 * rmt.loc['R21', 'new yardstick']) >= 1 else "no")
    for nm_, col in (("15 [POST HOC] imaging LR LeftOnly (Tikhonov dS, H6)", LO), ("RightOnly imaging LR (P5)", RO),
                     ("Test_B imaging LR", TB)):
        o, n_ = imp[f"{col} / ruler 9"], imp[f"{col} / ruler 11"]
        add(nm_, f"{o:.2f}x", f"{n_:.2f}x", tier(n_))
    for band in ("band mean 3.2-4.2", "3.30-3.65 GHz"):
        add(f"16 [POST HOC] LeftOnly phase cross-ratios >= 3x ({band})", cnt(LO, SYM9, band), cnt(LO, NULL11, band),
            "yes" if cnt(LO, NULL11, band) > 0 else "no")
        add(f"Test_B phase cross-ratios >= 3x ({band})", cnt(TB, SYM9, band), cnt(TB, NULL11, band), "-")
        add(f"RightOnly phase cross-ratios >= 3x ({band}) (P2)", cnt(RO, SYM9, band), cnt(RO, NULL11, band), "-")
    add("17 [POST HOC] LeftOnly left-right resonance shift vs null max (MHz)",
        f"{lrres[LO]:+.2f} vs {max(abs(lrres[d]) for d in SYM9):.2f}", f"{lrres[LO]:+.2f} vs {max(abs(lrres[d]) for d in NULL11):.2f}",
        "yes (still no shift beyond the null)" if abs(lrres[LO]) <= max(abs(lrres[d]) for d in NULL11) else "changes")
    for st_ in ("power pair T2 refl. vs T6 refl.", "power pair T3 refl. vs T5 refl."):
        for d in (LO, RO, TB):
            o, n_ = ratio_of(d, st_)
            add(f"18 reflection pair {st_[11:]}: {d}", f"{o:.2f}x", f"{n_:.2f}x", tier(n_))
    for st_, (lo_v, m9, m11) in nbp.items():
        add(f"19 [POST HOC] LeftOnly neighbour phase pair {st_} (3.30-3.65 GHz) vs null max", f"{lo_v:+.2f} vs {m9:.2f} ({abs(lo_v) / m9:.1f}x)",
            f"{lo_v:+.2f} vs {m11:.2f} ({abs(lo_v) / m11:.1f}x)", tier(abs(lo_v) / m11))
    add("20 Moderate_lobe imaging T (-4.04) vs the rotated nulls (Tikhonov dS, H6)", "largest of the 9",
        f"rot07 {imp[f'T {N7}']:+.2f}, rot19 {imp[f'T {N19}']:+.2f}", "context")
    add("28 C6 P1: within tolerance (26 informative)", f"{p1(SYM9)}/26", f"{p1(NULL11)}/26", "post hoc only; verdict stands")
    add("29 R21 mirror-twin difference 0.133 dB / yardstick", f"{0.133 / rmt.loc['R21', 'one-pass yardstick']:.2f}x",
        f"{0.133 / rmt.loc['R21', 'new yardstick']:.2f}x", "yes" if 0.133 > rmt.loc['R21', 'new yardstick'] else "no (within the re-mesh yardstick)")
    add("C6 P4: RightOnly - LeftOnly within yardstick (R31, R21, R32)",
        ", ".join(f"{r} {abs(Xr[RO][r] - Xr[LO][r]) <= rmt.loc[r, 'one-pass yardstick']}" for r in RATIOS),
        ", ".join(f"{r} {abs(Xr[RO][r] - Xr[LO][r]) <= rmt.loc[r, 'new yardstick']}" for r in RATIOS), "post hoc only; verdict stands")
    for d in (TB,):
        for sch in ("binary", "three", "three_merged"):
            o, n_ = mlab(d, sch, "A1 old"), mlab(d, sch, "A1 new")
            add(f"Test_B {sch} label margin (A1)", f"{o:.2f}x", f"{n_:.2f}x", tier(n_))
    for _, r_ in fbt[fbt.design == TB].iterrows():
        add(f"Test_B {r_['index']}", f"{r_['ratio old']:.2f}x", f"{r_['ratio new']:.2f}x", tier(r_["ratio new"]))
    add("Test_B mirror side (votes >= 2x)", f"{ms[0]} ({ms[1]} votes, {ms[2]} >= 3x)", f"{side11} ({len(votes11)} votes)",
        "yes" if side11 == ms[0] else "no")
    add("Test_B pattern fit 25: contrast / accepted", f"{T15.localise(yb, W, nc_chk, hg_chk)['contrast / null']:.2f}x / accepted",
        f"{loc_tb_new['contrast / null']:.2f}x / {'accepted' if loc_tb_new['accepted'] else 'rejected'}",
        "yes" if loc_tb_new["accepted"] else "no")
    ct = pd.DataFrame(rows)
    ct.to_csv(OUT / "C_survival.csv", index=False)
    L += ["## C. Survival of every ruler-dependent claim and reading (old rulers vs rulers with the rotated nulls)",
          "Claim numbers refer to MODEL_CARD 6.2. Claims 1, 4, 5, 7, 8, 12-14 and 21-27 do not use a null floor or the "
          "mesh yardstick as their ruler (or use sub-band yardsticks not rebuilt here) and are not listed.",
          md(ct), "", "Front-back indices (vs Healthy_sliced_new):", md(fbt, ".3f"), "",
          "Label margins (all designs):", md(mt, ".2f"), "",
          "Every mirror-statistic ruler:", md(bt, ".3f"), ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:6]))
    print(md(qct, ".3f"))
    print(md(vt, ".3f"))
    print(a_sum)
    print(md(fam, ".2f"))
    print(md(rmt.reset_index(), ".3f"))
    print(md(gt, ".3f"))
    print(md(nt, ".3f"))
    print(md(st, ".3f"))
    print(md(ct))


if __name__ == "__main__":
    main()
