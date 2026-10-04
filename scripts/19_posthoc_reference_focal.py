"""POST HOC (2026-10-04, after Null_rot31 / Null_rot43): is the primary reference typical, and a focal-disease table.

    python scripts/19_posthoc_reference_focal.py

Writes results/05_lobe/reference_focal/{report.md, *.csv}. Nothing committed earlier is changed; the alternative
reference computed here is NOT adopted.

C  Typicality of Healthy_sliced_new (H6). The six healthy meshes H6, Healthy_sliced (H7), Null_rot07/19/31/43, each
   against the mean of the other five: R31, R21, R32 (clean ring features), and the per-antenna neighbour-path phase
   (mean of the two neighbour paths at each antenna, band-mean phase of S relative to H6, then minus the other five's
   mean): ring mean, ring spread (max - min) and left - right (mean T2, T3 minus mean T5, T6), at 3.2-3.5 GHz (the
   protocol band) and 3.30-3.65 GHz. Phase sign: negative = more delay. A mesh is called 'extreme' if it ranks first
   or last of the six and 'outlier' if, in addition, |deviation| >= 2 x the SD of the other five (criterion stated here).
D  What changes if the reference is the mean of the healthy meshes (post hoc, not adopted): the re-mesh yardstick
   (max |Q - mean of the five 6-pass healthy meshes|), the frozen-label margins with it, the Test_B pattern fit, the
   R21 rise of the 19 mm designs and the front-back index.
F  Focal-disease table: per-antenna R31 change (opposite / mean of the two neighbours, dB, against H6), half-ring R21
   left - right (left half T1-T4, right half T4-T1), neighbour-phase left - right, for LeftOnly, RightOnly, Test_B,
   Mild_lobe, Mild_lobe_new and the four rotated nulls; and the SD of each statistic under +-0.5 dB per-port gain error
   (uniform, as adstage.pipeline.augment) and under +-10 deg per-port phase error, 2000 draws on LeftOnly.
"""
from __future__ import annotations

import importlib.util
import json
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
T15 = _load("tb15", "15_test_b.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "reference_focal"
H6, H7, LO, RO, TB = R11.H6, R11.H7, R11.LO, "RightOnly_test", "Test_B"
ROT = ["Null_rot07", "Null_rot19", "Null_rot31", "Null_rot43"]
HEALTHY = [H6, H7] + ROT
SIX = [H6] + ROT                                       # the five 6-pass healthy meshes (H7 has 7 passes)
RATIOS = ("R31", "R21", "R32")
BANDS = {"3.2-3.5 GHz": (3.2e9, 3.5e9), "3.30-3.65 GHz": (3.30e9, 3.65e9)}
FOCAL = [LO, RO, TB, "Mild_lobe", "Mild_lobe_new"] + ROT
md = L7.md


def nb_phase_band(f, S, Sref, band):
    m = R11.fmask(f, band)
    ph = np.degrees(np.angle(R11.sbar(S)[m] / R11.sbar(Sref)[m])).mean(0)
    return np.array([0.5 * (ph[k, (k - 1) % 6] + ph[k, (k + 1) % 6]) for k in range(6)])


def lr(y):
    return float(np.mean(y[[1, 2]]) - np.mean(y[[4, 5]]))


def bdb(f, S):
    return 10 * np.log10(L7.band_power(f, S[None])[0])


def per_antenna_r31(P):
    return np.array([P[k, (k + 3) % 6] - 0.5 * (P[k, (k - 1) % 6] + P[k, (k + 1) % 6]) for k in range(6)])


def half_r21(P):
    left = np.mean([P[0, 2], P[1, 3]]) - np.mean([P[0, 1], P[1, 2], P[2, 3]])
    right = np.mean([P[3, 5], P[4, 0]]) - np.mean([P[3, 4], P[4, 5], P[5, 0]])
    return float(left - right)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)
    cfg = load_config(ROOT, "config_lobe.yaml")
    rule = json.loads((ROOT / "results/04/frozen_rule.json").read_text())
    f, Sd, man, ds = L8.load_all(cfg)
    for d in HEALTHY + FOCAL:
        if d not in Sd:
            raise SystemExit(f"{d} missing")
    X = {}
    for d in set(HEALTHY + FOCAL + [H7, "Moderate_lobe", "Severe_lobe", "Mild_lobe", "MCI_lobe_c3"] + list(R11.LOBE_ALL)):
        x, nm, _, _ = features(f, Sd[d][None])
        X[d] = {r: float(x[0][nm.index(r)]) for r in RATIOS}
    L = [f"# POST HOC: typicality of the primary reference and a focal-disease table (code {gh})", "",
         "Computed after Null_rot31 / Null_rot43 arrived. Nothing committed is changed; the alternative reference is not "
         "adopted.", ""]

    # ================================================================== C: typicality
    crows = []
    Y = {bn: {d: nb_phase_band(f, Sd[d], Sd[H6], b) for d in HEALTHY} for bn, b in BANDS.items()}
    for d in HEALTHY:
        others = [o for o in HEALTHY if o != d]
        row = {"mesh": d}
        for r in RATIOS:
            vo = np.array([X[o][r] for o in others])
            dev = X[d][r] - vo.mean()
            allv = np.array([X[o][r] for o in HEALTHY])
            rank = int((allv < X[d][r]).sum()) + 1
            row[f"{r} - mean(others)"] = dev
            row[f"{r} / SD(others)"] = dev / vo.std(ddof=1)
            row[f"{r} rank (1 = lowest)"] = rank
        for bn in BANDS:
            yo = np.mean([Y[bn][o] for o in others], 0)
            y = Y[bn][d] - yo
            row[f"ring mean {bn}"] = float(y.mean())
            row[f"ring spread {bn}"] = float(y.max() - y.min())
            row[f"left-right {bn}"] = lr(y)
        crows.append(row)
    ct = pd.DataFrame(crows)
    flags = []
    for r in RATIOS + tuple(f"ring mean {bn}" for bn in BANDS):
        col = f"{r} - mean(others)" if r in RATIOS else r
        v = ct.set_index("mesh")[col]
        for d in HEALTHY:
            others = v.drop(d)
            dev = v[d]
            ext = v[d] == v.max() or v[d] == v.min()
            if r in RATIOS:
                sd = np.std([X[o][r] for o in HEALTHY if o != d], ddof=1)
                dev_ = X[d][r] - np.mean([X[o][r] for o in HEALTHY if o != d])
            else:
                sd, dev_ = others.std(ddof=1), dev
            flags.append({"quantity": r, "mesh": d, "deviation": dev_, "SD of the other five": sd,
                          "extreme (rank 1 or 6)": bool(ext), "outlier (extreme and >= 2 SD)": bool(ext and abs(dev_) >= 2 * sd)})
    ft = pd.DataFrame(flags)
    ct.to_csv(OUT / "C_healthy_meshes.csv", index=False)
    ft.to_csv(OUT / "C_outlier_flags.csv", index=False)
    vsh6 = pd.DataFrame([{"mesh": d, **{f"d{r} vs H6": X[d][r] - X[H6][r] for r in RATIOS},
                          **{f"{q} vs H6 {bn}": fn(Y[bn][d]) for bn in BANDS for q, fn in
                             (("ring mean", lambda y: float(y.mean())), ("ring spread", lambda y: float(y.max() - y.min())),
                              ("left-right", lr))}} for d in HEALTHY if d != H6])
    vsh6.to_csv(OUT / "C_against_H6.csv", index=False)
    h6f = ft[ft.mesh == H6]
    L += ["## C. Each healthy mesh against the mean of the other five",
          "Against Healthy_sliced_new (as quoted by the user; phase negative = more delay):", md(vsh6, ".3f"), "",
          "Each mesh minus the mean of the other five:", md(ct, ".3f"), "",
          "Healthy_sliced_new flags:", md(h6f, ".3f"), ""]

    # ================================================================== D: mean-of-healthy reference (not adopted)
    mean6 = {r: float(np.mean([X[d][r] for d in SIX])) for r in RATIOS}
    yard_mean = {r: max(abs(X[d][r] - mean6[r]) for d in SIX) for r in RATIOS}
    yard_h6 = {r: max(abs(X[d][r] - X[H6][r]) for d in ROT) for r in RATIOS}
    one_pass = {"R31": 0.135125, "R21": 0.109744, "R32": 0.160848}
    r6 = pd.read_csv(LOBE / "review2" / "R6_A28_rulers.csv")
    tb_sd = float(r6[r6.rule == "binary"]["boundary SD"].iloc[0])
    drows = []
    for r in RATIOS:
        drows.append({"quantity": r, "one-pass yardstick": one_pass[r], "re-mesh vs H6 (pre-registered)": yard_h6[r],
                      "re-mesh vs mean of the five 6-pass meshes (post hoc)": yard_mean[r],
                      "pre-registered ruler": max(one_pass[r], yard_h6[r]),
                      "alternative ruler": max(one_pass[r], yard_mean[r])})
    dt = pd.DataFrame(drows)
    mrows = []
    for d in list(R11.LOBE_ALL) + [RO, TB]:
        x = X[d]["R31"]
        lab, mg = R10.edge_margin(rule, "binary", x)
        mrows.append({"design": d, "label": lab, "margin dB": mg,
                      "A1 pre-registered (vs H6)": abs(mg) / max(max(one_pass["R31"], yard_h6["R31"]), tb_sd),
                      "A1 alternative (vs mean)": abs(mg) / max(max(one_pass["R31"], yard_mean["R31"]), tb_sd)})
    mt = pd.DataFrame(mrows)
    # Test_B pattern fit with the mean of the five 6-pass meshes as reference (complex mean of S)
    Smean = np.mean([Sd[d] for d in SIX], 0)
    yb_h6 = T15.nb_phase(f, Sd[TB], Sd[H6])
    yb_mean = T15.nb_phase(f, Sd[TB], Smean)
    nc_mean = max(float(np.std(T15.nb_phase(f, Sd[d], np.mean([Sd[o] for o in SIX if o != d], 0)))) for d in SIX)
    g_mean = max(abs(float(np.mean(T15.nb_phase(f, Sd[d], np.mean([Sd[o] for o in SIX if o != d], 0))))) for d in SIX)
    nc_h6 = max(0.21167, *(float(np.std(T15.nb_phase(f, Sd[d], Sd[H6]))) for d in ROT))
    g_h6 = max(1.11103, *(abs(float(np.mean(T15.nb_phase(f, Sd[d], Sd[H6])))) for d in ROT))
    loc_h6 = T15.localise(yb_h6, 0.4, nc_h6, g_h6)
    loc_mean = T15.localise(yb_mean, 0.4, nc_mean, max(1.11103, g_mean))
    rise = pd.DataFrame([{"design": d, "R21 rise vs H6": X[d]["R21"] - X[H6]["R21"],
                          "R21 rise vs mean of 5": X[d]["R21"] - mean6["R21"],
                          "/ pre-registered R21 ruler": (X[d]["R21"] - X[H6]["R21"]) / max(one_pass["R21"], yard_h6["R21"]),
                          "/ alternative R21 ruler": (X[d]["R21"] - mean6["R21"]) / max(one_pass["R21"], yard_mean["R21"])}
                         for d in (LO, RO, TB)])
    dt.to_csv(OUT / "D_rulers_reference.csv", index=False)
    mt.to_csv(OUT / "D_detection_margins_reference.csv", index=False)
    rise.to_csv(OUT / "D_R21_rise_reference.csv", index=False)
    L += ["## D. If the reference were the mean of the healthy meshes (post hoc, not adopted)",
          "Claims that use H6 as their reference: the re-mesh yardstick (|Q(rotated) - Q(H6)|), the Test_B pattern fit "
          "(y against H6), the R21 rise of the 19 mm designs (claim 32), the front-back index. The frozen labels themselves "
          "(R31 vs tau, R21 / R32 vs the LDA edges) and the mirror statistics are reference-free.", md(dt, ".3f"), "",
          "Detection margins:", md(mt, ".2f"), "", "R21 rise of the 19 mm designs:", md(rise, ".3f"), "",
          f"Test_B pattern fit, reference H6 (all-null rulers): contrast {loc_h6['contrast / null']:.2f}x, "
          f"{'accepted' if loc_h6['accepted'] else 'rejected'}, call {loc_h6['pattern call']}. Reference = mean of the five 6-pass "
          f"meshes (null contrast {nc_mean:.3f} deg from leave-one-out healthy meshes): contrast {loc_mean['contrast / null']:.2f}x, "
          f"{'accepted' if loc_mean['accepted'] else 'rejected'}, call {loc_mean['pattern call']}, best pattern "
          f"{loc_mean.get('best pattern', '-')}.", ""]

    # ================================================================== F: focal-disease table
    P = {d: bdb(f, Sd[d]) for d in FOCAL + [H6]}
    ra_h6 = per_antenna_r31(P[H6])
    frows = []
    for d in FOCAL:
        ra = per_antenna_r31(P[d]) - ra_h6
        y = {bn: nb_phase_band(f, Sd[d], Sd[H6], b) for bn, b in BANDS.items()}
        frows.append({"design": d, **{f"R31 T{k + 1} change dB": ra[k] for k in range(6)},
                      "per-antenna R31 left-right dB": lr(ra),
                      "half-ring R21 left-right dB (design)": half_r21(P[d]),
                      "half-ring R21 left-right dB (minus H6)": half_r21(P[d]) - half_r21(P[H6]),
                      **{f"neighbour-phase left-right deg {bn}": lr(y[bn]) for bn in BANDS}})
    fct = pd.DataFrame(frows)
    rng = np.random.default_rng([cfg["seed"], 191])
    S0 = Sd[LO]
    gstats, pstats = [], []
    for kind, n in (("gain", 2000), ("phase", 2000)):
        for _ in range(n):
            if kind == "gain":
                g = 10 ** (rng.uniform(-0.5, 0.5, 6) / 20)
            else:
                g = np.exp(1j * np.deg2rad(rng.uniform(-10, 10, 6)))
            Sg = S0 * g[None, :, None] * g[None, None, :]
            Pg = bdb(f, Sg)
            yg = {bn: nb_phase_band(f, Sg, Sd[H6], b) for bn, b in BANDS.items()}
            rec = {"per-antenna R31 left-right dB": lr(per_antenna_r31(Pg) - ra_h6),
                   "half-ring R21 left-right dB (design)": half_r21(Pg),
                   **{f"neighbour-phase left-right deg {bn}": lr(yg[bn]) for bn in BANDS},
                   "per-antenna R31 T2 change dB": float((per_antenna_r31(Pg) - ra_h6)[1])}
            (gstats if kind == "gain" else pstats).append(rec)
    sdt = pd.DataFrame([{"statistic": k, "SD under +-0.5 dB per-port gain error": float(pd.DataFrame(gstats)[k].std()),
                         "SD under +-10 deg per-port phase error": float(pd.DataFrame(pstats)[k].std())}
                        for k in gstats[0]])
    opp = pd.DataFrame([{"opposite path": f"T{k + 1}-T{(k + 3) % 6 + 1}",
                         "sides": {0: "front (T1, midline) - back (T4, midline)", 1: "left (T2) - right (T5)",
                                   2: "left (T3) - right (T6)"}[k]} for k in range(3)])
    fct.to_csv(OUT / "F_focal_table.csv", index=False)
    sdt.to_csv(OUT / "F_error_sd.csv", index=False)
    L += ["## F. Focal-disease table (post hoc; against Healthy_sliced_new; phase negative = more delay)",
          "The three opposite paths and the sides they join (a half-ring R31 would need an opposite path inside one half; "
          "there is none):", md(opp), "", md(fct, ".3f"), "",
          "Spread of each statistic on LeftOnly under per-port calibration errors (2000 draws each):", md(sdt, ".3f"), ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
