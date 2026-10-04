"""Pre-registered test designs of the lobe phantom: blind scoring of LeftOnly_test against the predictions committed
at cf56de8 (read, never written), Prompt 07 §3.5 (MCI_lobe), and the frozen rule on both.

    python scripts/09_lobe_tests.py [--n 300]

Test designs: LeftOnly_test_c3 and MCI_lobe_c3 (stop rule 1, 6 passes, as Healthy_sliced_new). LeftOnly is scored
against two references: Healthy_sliced (7 passes, stop rule 2; primary, as pre-registered) and Healthy_sliced_new
(6 passes, stop rule 1; stop-rule and pass matched). Writes results/05_lobe/tests/{report.md, *.csv, figures/}.

Scoring of each prediction:
1. the committed rule of cf56de8, applied as written ("committed verdict");
2. the rulers of scripts/08_lobe_mesh.py (noise SD, one-pass mesh yardstick, symmetry floor, measurement-error
   spread at ±0.5 dB and at ±2 dB/±10°) give the label: **hit** = the committed rule holds and the effect is
   separable from the clean ruler (3x max(yardstick, symmetry floor)), or a predicted null/level is confirmed;
   **miss** = the committed rule fails by more than 3x the clean ruler; **not separable** = otherwise. The same label
   with the measured ruler (max(yardstick, floor (+) ±0.5 dB spread)) says whether a real measurement could tell.

Gain-invariant left-right cross-ratios (the primary test agreed on 2026-10-03, after cf56de8): for every mirror pair
of cross-ratios, A = chi_n - s chi_mirror(n), zero for any mirror-symmetric head and free of per-port gain. The
predicted A follow from the committed per-path predictions with no new parameter. Decision rule, fixed in this
code before the first run: the test holds if (a) at least one A exceeds 3x the measured ruler, (b) the locality
model's rms error over all A is below the no-locality baseline's, and (c) the observed sign agrees with the locality
prediction for >= 80% of the A whose predicted value exceeds 3x the clean ruler.
One solve per design: within-simulation noise robustness, not generalisation.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adstage.config import load_config  # noqa: E402
from adstage.features.metrics import to_ring_order  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.frozen import apply_rule  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.noise.model import PROFILES  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.pipeline.quality import QualityGate  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "tests"
FIG = OUT / "figures"
NOTE = L8.NOTE
LO, MCI = "LeftOnly_test_c3", "MCI_lobe_c3"
H7, H6, M5 = L8.H7, L8.H6, L8.M5
REFS = {"Healthy_sliced (7 passes, primary)": H7, "Healthy_sliced_new (6 passes, matched)": H6}
RIGHT = ["T5-T6", "T5 refl.", "T6 refl.", "T1-T6", "T4-T5", "T1-T5", "T4-T6"]        # prediction 3
LEFT = ["T2-T3", "T2 refl.", "T3 refl.", "T1-T2", "T3-T4", "T1-T3", "T2-T4"]         # prediction 4
MM = L7.mirror_map()
NULL_TOL = 0.005                                     # a committed per-path prediction of |x| < 0.005 dB is "~0"
CAVEATS = [
    "The predictions were derived from the lobe_v1 pair (Healthy_sliced, stop rule 2, 7 passes, against Mild_lobe, "
    "stop rule 1, 5 passes), so mesh is part of their per-path 'Mild change'.",
    "LeftOnly_test carries CSF_Mild everywhere (CSF is one object): on the right it is only the 0.5 mm layer "
    "(e_S5 = e_S6 = 0). The prediction model treats the right lobes as fully healthy.",
    "The gain-invariant cross-ratio test was agreed after cf56de8 (2026-10-03); its predicted values are derived from "
    "the committed per-path predictions without new parameters, and its decision rule is fixed in this script "
    "before the first run.",
    "Prediction 2 says 'no front-back asymmetry beyond the floor' without a numeric rule; it is scored as "
    "|index| <= the stated floor (strict), with |index| < 3x floor reported alongside.",
    "LeftOnly_test_c3 has 6 passes (stop rule 1; pass 5 missed 0.02 by ~0.002); the matched reference is "
    "Healthy_sliced_new (6 passes, stop rule 1).",
    "One solve per design: within-simulation noise robustness, not generalisation. Lobe placement is schematic.",
]


def lr_chi(ch):
    """Left-right antisymmetric cross-ratios A = chi_n - s chi_mirror(n), one per mirror pair (dict or arrays)."""
    out = {}
    for n, (m, s) in MM.items():
        if m == n and s == 1:
            continue                                  # its own mirror image: A is identically zero
        if m != n and m < n:
            continue                                  # one per pair (A_m = -s A_n)
        out[n] = ch[n] - s * ch[m]
    return out


def ext_quantities(f, S, noisy=False):
    """scripts/08 quantities + left-right cross-ratios + every ring feature not already included."""
    q = L8.quantities(f, S, noisy)
    D = S if noisy else S[None]
    bp = L7.band_power_noisy(f, D) if noisy else L7.band_power(f, D)
    for n, v in lr_chi(L7.cross_ratios(bp)).items():
        q[f"lr chi {n}"] = v
    X, nm, _, _ = features(f, D)
    have = {k for _, k in L8.RING}
    for i, k in enumerate(nm):
        if k not in have:
            q[f"ring feature {k}"] = X[:, i]
    return q


def ruler(R, k):
    y, fl = R["yard"][k], R["fdiff"][k]
    s0, s05, s2 = (R["sd"][n][k] for n in L8.NOISE)
    return {"yard": y, "floor": fl, "sd0": s0, "sd05": s05, "sd2": s2, "clean": max(y, fl),
            "meas": max(y, float(np.hypot(fl, s05))), "meas2": max(y, float(np.hypot(fl, s2)))}


def label(correct, obs, pred, C, kind):
    """kind: 'change' (non-zero predicted change), 'null' (predicted ~0) or 'value' (predicted level)."""
    if correct:
        return "hit" if kind != "change" or abs(obs) >= 3 * C else "not separable"
    return "miss" if abs(obs - pred) >= 3 * C else "not separable"


def ratios(obs, rr):
    return {"/ noise SD": abs(obs) / rr["sd0"], "/ yardstick": abs(obs) / rr["yard"],
            "/ symmetry floor": abs(obs) / rr["floor"] if rr["floor"] > 0 else np.inf,
            "/ spread ±0.5 dB": abs(obs) / rr["sd05"], "/ spread ±2 dB": abs(obs) / rr["sd2"]}


def mat_from(pred, col):
    M = np.zeros((6, 6))
    for _, r in pred.iterrows():
        a = r.path.replace(" refl.", "")
        i, j = (L7.ANT.index(a),) * 2 if "-" not in a else map(L7.ANT.index, a.split("-"))
        M[i, j] = M[j, i] = r[col]
    return M


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    FIG.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT, "config_lobe.yaml")
    gh = git_hash(ROOT)
    f, Sd, man, ds = L8.load_all(cfg)
    rule_path = ROOT / "results" / "04" / "frozen_rule.json"
    rule = json.loads(rule_path.read_text())
    tau = float(rule["detection_binary_R31"]["tau_dB"])

    # ------------------------------------------------------------------ committed predictions (read only)
    files = ["results/05_lobe/predictions.md", "results/05_lobe/predictions.csv"]
    unchanged = subprocess.run(["git", "diff", "--quiet", "cf56de8", "--", *files], cwd=ROOT).returncode == 0
    clean_wt = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *files], cwd=ROOT).returncode == 0
    pred = pd.read_csv(LOBE / "predictions.csv")
    txt = (LOBE / "predictions.md").read_text(encoding="utf-8")
    p_lr = float(re.search(r"\*\*Left-right index\*\*[^*]*\*\*([+-][0-9.]+) dB\*\*", txt).group(1))
    fl_lr = float(re.search(r"the noise floor \(([0-9.]+) dB", txt).group(1))
    m2 = re.search(r"\*\*Front-back index\*\*: ([+-][0-9.]+) dB \(floor ([0-9.]+) dB\)", txt)
    p_fb, fl_fb = float(m2.group(1)), float(m2.group(2))
    m5 = re.search(r"R31 (-?[0-9.]+), R21 (-?[0-9.]+), R32 (-?[0-9.]+) dB", txt)
    p_rat = {"R31": float(m5.group(1)), "R21": float(m5.group(2)), "R32": float(m5.group(3))}
    p_lab = re.search(r"mostly \*\*([A-Z]+)\*\*", txt).group(1)

    R = L8.rulers(f, Sd, cfg, args.n, qfn=ext_quantities)
    Q = R["Q"]
    g = lambda d, k: float(Q[d][k][0])                       # noqa: E731
    L = [f"# Pre-registered test designs of the lobe phantom: LeftOnly_test and MCI_lobe (code {gh})", "",
         "Designs (HFSS convergence tables, user 2026-10-04; header variables checked by the user):",
         md(man[man.design.isin([LO, MCI, H6, H7])][["design", "kind", "stop_rule", "passes", "final_dS", "elements",
                                                    "notes"]], ".5g"), "",
         f"Predictions: `results/05_lobe/predictions.md` / `.csv`, committed at cf56de8 before LeftOnly_test existed. "
         f"Unchanged since cf56de8: **{unchanged and clean_wt}** (git). LeftOnly is scored against Healthy_sliced "
         "(primary, as pre-registered) and Healthy_sliced_new (stop-rule and pass matched) alongside.", "",
         "**Caveats (recorded before scoring):**"] + [f"- {c}" for c in CAVEATS] + [
         "", "**Rulers** (for a difference of two designs; `scripts/08_lobe_mesh.py`): noise SD (typical noise and setup "
         "perturbation, no per-port calibration error), one-pass mesh yardstick (largest of Healthy 6->7, Mild 5->6, "
         "Moderate 5->6, Severe 5->6; families floored at their rms), symmetry floor (mirror residual of the six "
         "mirror-symmetric stage designs), measurement-error spread (±0.5 dB per-port gain; ±2 dB gain + ±10° phase). "
         "**Label**: hit = committed rule holds and the effect is separable (>= 3x clean ruler = max(yardstick, floor)), "
         "or a predicted null/level is confirmed; miss = committed rule fails by >= 3x the clean ruler; not separable = "
         "otherwise. 'measured' = the same with max(yardstick, floor (+) ±0.5 dB spread).", ""]

    # ------------------------------------------------------------------ 0. QC
    qc = OUT / "qc"
    gl = pd.read_csv(LOBE / "qc" / "masked_points.csv")
    gl = gl[gl.file.str.contains("|".join([LO, MCI, "Severe_lobe_c3", "Moderate_lobe_c3"]))]
    L += ["## 0. QC",
          "Parsing, passivity, reciprocity and port-map search for Healthy_sliced_new + the two test designs: "
          "`results/05_lobe/tests/qc/qc_report.md` (rows labelled by manifest class: Mild = LeftOnly_test_c3, "
          "MCI = MCI_lobe_c3); the c3 stage designs: `results/05_lobe/lobe_B/qc/qc_report.md`. Points masked by the "
          "frozen recipe in the four new files (`results/05_lobe/qc/masked_points.csv`):",
          md(gl, ".2f") if len(gl) else "none", ""]
    if (qc / "integrity.csv").exists():
        it = pd.read_csv(qc / "integrity.csv")
        cols = [c for c in ("class", "recip_rel_band_max_db", "n_glitch_pts", "col_power_max", "sigma_max", "passive")
                if c in it]
        L += ["Integrity (tests set):", md(it[cols], ".3g"), ""]

    # ------------------------------------------------------------------ 1. per-path predictions
    rows = []
    for rname, ref in REFS.items():
        for _, p in pred.iterrows():
            k = "path " + p.path
            obs = g(LO, k) - g(ref, k)
            pl, pb = p["predicted LeftOnly change dB (locality)"], p["no-locality baseline dB"]
            tol = p["2x numerical noise of path type dB"]
            null = abs(pl) < NULL_TOL
            correct = bool(abs(obs) <= tol) if null else bool(np.sign(obs) == np.sign(pl)
                                                               and abs(obs - pl) <= max(0.5 * abs(pl), tol))
            rr = ruler(R, k)
            grp = ("3: right (~0)" if p.path in RIGHT else "4: left (~ full Mild)" if p.path in LEFT
                   else "half of Mild (both models)")
            rows.append({"reference": rname, "path": p.path, "type": p.type, "prediction": grp,
                         "Mild change dB (cf56de8)": p["Mild change dB"], "predicted (locality) dB": pl,
                         "baseline (no locality) dB": pb, "observed dB": obs, "committed tolerance dB": tol,
                         "committed verdict": "correct" if correct else "incorrect",
                         "label": label(correct, obs, pl, rr["clean"], "null" if null else "change"),
                         "label (measured)": label(correct, obs, pl, rr["meas"], "null" if null else "change"),
                         **ratios(obs, rr), "|obs - pred| / clean ruler": abs(obs - pl) / rr["clean"]})
    pt = pd.DataFrame(rows)
    pt.to_csv(OUT / "1_leftonly_paths.csv", index=False)

    # ------------------------------------------------------------------ 2. predictions 1-6
    prow = []
    lb = {}
    for rname, ref in REFS.items():
        for pid, key, pv, fl in (("1 left-right index", "index: left-right, all paths", p_lr, fl_lr),
                                 ("2 front-back index", "index: front-back, all paths", p_fb, fl_fb)):
            obs = g(LO, key) - g(ref, key)
            rr = ruler(R, key)
            if pid.startswith("1"):
                correct = bool(np.sign(obs) == np.sign(pv) and abs(obs) >= 3 * fl)
                rule_txt = f"sign {'+' if pv > 0 else '-'} and |index| >= 3 x {fl:.3f} dB"
                kind = "change"
            else:
                correct = bool(abs(obs) <= fl)
                rule_txt = f"|index| <= floor {fl:.3f} dB (strict; < 3x floor: {abs(obs) < 3 * fl})"
                kind = "null"
            prow.append({"reference": rname, "prediction": pid, "predicted dB": pv, "committed rule": rule_txt,
                         "observed dB": obs, "committed verdict": "correct" if correct else "incorrect",
                         "label": label(correct, obs, pv, rr["clean"], kind),
                         "label (measured)": label(correct, obs, pv, rr["meas"], kind),
                         "label (±2 dB)": label(correct, obs, pv, rr["meas2"], kind), **ratios(obs, rr)})
        sub = pt[pt.reference == rname]
        for pid, grp in (("3 right paths ~0", "3: right (~0)"), ("4 left paths ~ full Mild", "4: left (~ full Mild)")):
            s = sub[sub.prediction == grp]
            nh, nm_, ns = ((s.label == v).sum() for v in ("hit", "miss", "not separable"))
            prow.append({"reference": rname, "prediction": pid, "predicted dB": np.nan,
                         "committed rule": "per path (see section 1)", "observed dB": np.nan,
                         "committed verdict": f"{int((s['committed verdict'] == 'correct').sum())}/{len(s)} correct",
                         "label": f"{nh} hit, {nm_} miss, {ns} not separable",
                         "label (measured)": ", ".join(f"{int((s['label (measured)'] == v).sum())} {v}"
                                                       for v in ("hit", "miss", "not separable")),
                         "label (±2 dB)": ""})
        rms_l = float(np.sqrt(np.mean((sub["observed dB"] - sub["predicted (locality) dB"]) ** 2)))
        rms_b = float(np.sqrt(np.mean((sub["observed dB"] - sub["baseline (no locality) dB"]) ** 2)))
        dif = sub[np.abs(sub["predicted (locality) dB"] - sub["baseline (no locality) dB"]) > 1e-9]
        rms_ld = float(np.sqrt(np.mean((dif["observed dB"] - dif["predicted (locality) dB"]) ** 2)))
        rms_bd = float(np.sqrt(np.mean((dif["observed dB"] - dif["baseline (no locality) dB"]) ** 2)))
        lb[rname] = (rms_l, rms_b, rms_ld, rms_bd, len(dif))
        prow.append({"reference": rname, "prediction": "locality model vs no-locality baseline",
                     "predicted dB": np.nan, "committed rule": "locality wins if its rms error over all 21 paths is lower",
                     "observed dB": np.nan, "committed verdict": f"locality {'wins' if rms_l < rms_b else 'loses'} "
                     f"(rms {rms_l:.3f} vs {rms_b:.3f} dB)",
                     "label": "hit" if rms_l < rms_b else "miss",
                     "label (measured)": f"on the {len(dif)} paths where the models differ: {rms_ld:.3f} vs {rms_bd:.3f} dB",
                     "label (±2 dB)": ""})
    for r, pv in p_rat.items():
        obs = g(LO, r)
        rr = ruler(R, r)
        correct = bool(abs(obs - pv) <= 0.3)
        prow.append({"reference": "(absolute value)", "prediction": f"5 {r} level", "predicted dB": pv,
                     "committed rule": "within 0.3 dB", "observed dB": obs,
                     "committed verdict": "correct" if correct else "incorrect",
                     "label": label(correct, obs, pv, rr["clean"], "value"),
                     "label (measured)": label(correct, obs, pv, rr["meas"], "value"),
                     "label (±2 dB)": label(correct, obs, pv, rr["meas2"], "value"),
                     **{c: abs(obs - pv) / rr[x] for c, x in (("/ noise SD", "sd0"), ("/ yardstick", "yard"),
                                                              ("/ spread ±0.5 dB", "sd05"), ("/ spread ±2 dB", "sd2"))}})
    post = {r: 0.5 * (g(H6, r) + g(M5, r)) for r in p_rat}

    # ------------------------------------------------------------------ 3. frozen rule on the test designs
    cfg_u = load_config(ROOT, "config_repeats.yaml")
    du = load_dataset(cfg_u, ROOT)
    assert np.allclose(du.f_hz, f), "uniform and lobe grids differ"
    Su = to_ring_order(du.S, du.port_to_ant)
    iH = du.files.index("new_Healthy.s6p")
    prof = PROFILES["typical"]
    acfg = {**cfg.get("augment", {}), "gain_err_db": 0.5}
    gate = QualityGate(cfg["gate"], f, mode="gain_invariant")      # exactly as scripts/07_lobe.py
    gate.fit_detune(draws(f, Su[iH], prof, 200, np.random.default_rng([cfg["seed"], 70]), acfg))
    thr = pd.read_csv(ROOT / "results" / "v2_with_v1_repeats" / "03" / "thresholds.csv")
    gate.set_floor_limit(float(thr[(thr.feature == "M5.C3") & (thr.profile == "typical")].tau_dB.iloc[0]))
    conds = {"typical, ±0.5 dB gain": acfg,
             "±2 dB gain + ±10° phase": {**cfg.get("augment", {}), "gain_err_db": 2.0, "phase_err_deg": 10.0}}
    dec = []
    for ci, (cname, ac) in enumerate(conds.items()):
        for di, d in enumerate((LO, MCI)):
            D = draws(f, Sd[d], prof, args.n, np.random.default_rng([cfg["seed"], 91, ci, di]), ac)
            inv = gate.check(D)["invalid"]
            for rname, labs in apply_rule(rule_path, f, D).items():
                vc = pd.Series(np.where(inv, "INVALID", labs)).value_counts(normalize=True)
                dec.append({"condition": cname, "design": d, "rule": rname,
                            **{k: float(vc.get(k, 0)) for k in
                               ("Normal", "AD", "Mild", "Mild+Moderate", "Severe", "UNCERTAIN", "INVALID")}})
    dt = pd.DataFrame(dec)
    dt.to_csv(OUT / "3_frozen_rule_test_designs.csv", index=False)
    lo_det = dt[(dt.design == LO) & (dt.rule == "binary_R31")]
    f6 = float(lo_det[p_lab].iloc[0])
    f6b = float(lo_det[p_lab].iloc[-1])
    correct6 = f6 >= 0.8
    prow.append({"reference": "(noisy measurements)", "prediction": f"6 frozen detection label {p_lab}",
                 "predicted dB": np.nan, "committed rule": f">= 80% of noisy measurements labelled {p_lab}",
                 "observed dB": np.nan, "committed verdict": f"{f6:.2f} {p_lab} (±2 dB/±10°: {f6b:.2f}); "
                 f"R31 {g(LO, 'R31'):.2f} dB vs tau {tau:.2f} ± {rule['detection_binary_R31']['margin_dB']:.2f}",
                 "label": "hit" if correct6 else "miss", "label (measured)": "", "label (±2 dB)": ""})
    pr = pd.DataFrame(prow)
    pr.to_csv(OUT / "2_leftonly_predictions.csv", index=False)
    ok5 = all(abs(g(LO, r) - v) <= 0.3 for r, v in p_rat.items())

    L += ["## 1. LeftOnly_test: committed predictions 1-6 (scored blind, cf56de8 unchanged)",
          md(pr, ".3f"), "",
          "Joint rule as committed ('Predictions 5-6 hold if R31/R21/R32 lie within 0.3 dB ... and the frozen-rule label "
          f"matches for >= 80%'): **{'holds' if ok5 and correct6 else 'fails'}** (5: {ok5}, 6: {correct6}).",
          "Post hoc, not pre-registered: the same halfway model re-derived from the matched pair (Healthy_sliced_new, "
          "Mild_lobe) gives " + ", ".join(f"{r} {v:.2f}" for r, v in post.items()) + " dB; observed "
          + ", ".join(f"{r} {g(LO, r):.2f}" for r in post) + " dB.", "",
          "## 2. Per-path predictions (both references)", md(pt, ".3f"), ""]

    # ------------------------------------------------------------------ 4. gain-invariant left-right cross-ratios
    def chg_chi(M):
        return lr_chi(L7.cross_ratios(10 ** (M / 10)))       # predicted per-path dB changes -> predicted A changes
    A_loc = chg_chi(mat_from(pred, "predicted LeftOnly change dB (locality)"))
    A_base = chg_chi(mat_from(pred, "no-locality baseline dB"))
    crows, chi_res = [], {}
    for rname, ref in REFS.items():
        for n in A_loc:
            k = f"lr chi {n}"
            obs = g(LO, k) - g(ref, k)
            rr = ruler(R, k)
            crows.append({"reference": rname, "left-right cross-ratio": n, "predicted (locality) dB": A_loc[n],
                          "baseline (no locality) dB": A_base[n], "observed dB": obs,
                          "clean ruler dB": rr["clean"], "measured ruler dB": rr["meas"],
                          "measured ruler (±2 dB) dB": rr["meas2"], **ratios(obs, rr),
                          "/ clean ruler": abs(obs) / rr["clean"], "/ measured ruler": abs(obs) / rr["meas"],
                          "/ measured ruler (±2 dB)": abs(obs) / rr["meas2"],
                          "predicted / clean ruler": abs(A_loc[n]) / rr["clean"]})
        c = pd.DataFrame([r for r in crows if r["reference"] == rname])
        na = int((c["/ measured ruler"] >= 3).sum())
        na2 = int((c["/ measured ruler (±2 dB)"] >= 3).sum())
        nc = int((c["/ clean ruler"] >= 3).sum())
        rl = float(np.sqrt(np.mean((c["observed dB"] - c["predicted (locality) dB"]) ** 2)))
        rb = float(np.sqrt(np.mean((c["observed dB"] - c["baseline (no locality) dB"]) ** 2)))
        big = c[c["predicted / clean ruler"] >= 3]
        agree = int((np.sign(big["observed dB"]) == np.sign(big["predicted (locality) dB"])).sum())
        frac = agree / len(big) if len(big) else np.nan
        holds = na >= 1 and rl < rb and len(big) > 0 and frac >= 0.8
        chi_res[rname] = {"n": len(c), "n_clean": nc, "n_meas": na, "n_meas2": na2, "rms_loc": rl, "rms_base": rb,
                          "n_big": len(big), "agree": agree, "frac": frac, "holds": holds,
                          "best": c.iloc[int(np.argmax(c["/ measured ruler"]))]}
    cx = pd.DataFrame(crows)
    cx.to_csv(OUT / "4_leftonly_lr_cross_ratios.csv", index=False)
    cs = pd.DataFrame([{"reference": k, "left-right cross-ratios": v["n"], ">= 3x clean ruler": v["n_clean"],
                        ">= 3x measured ruler (±0.5 dB)": v["n_meas"], ">= 3x measured ruler (±2 dB)": v["n_meas2"],
                        "rms error locality dB": v["rms_loc"], "rms error baseline dB": v["rms_base"],
                        "predicted >= 3x clean ruler": v["n_big"], "sign agrees": f"{v['agree']}/{v['n_big']}",
                        "best": v["best"]["left-right cross-ratio"], "best observed dB": v["best"]["observed dB"],
                        "best / measured ruler": v["best"]["/ measured ruler"],
                        "primary test": "holds" if v["holds"] else "fails"} for k, v in chi_res.items()])
    L += ["## 3. Gain-invariant left-right cross-ratios (primary test, as agreed; derived from cf56de8)",
          "A = chi_n - s chi_mirror(n) for each mirror pair of the 45 cross-ratios: zero for any mirror-symmetric head, "
          "independent of per-port gain. Predicted A from the committed per-path predictions (locality model) and from "
          "the no-locality baseline. Decision rule (fixed in the script before the first run): (a) >= 1 A beyond 3x the "
          "measured ruler, (b) locality rms error < baseline rms error, (c) sign agreement >= 80% where the predicted A "
          "exceeds 3x the clean ruler.", md(cs, ".3f"), "",
          "All left-right cross-ratios (largest observed first):",
          md(cx.sort_values(["reference", "/ measured ruler"], ascending=[True, False])
             [["reference", "left-right cross-ratio", "predicted (locality) dB", "baseline (no locality) dB",
               "observed dB", "/ noise SD", "/ yardstick", "/ symmetry floor", "/ spread ±0.5 dB", "/ spread ±2 dB",
               "/ clean ruler", "/ measured ruler"]], ".2f"), ""]

    # ------------------------------------------------------------------ 5. MCI_lobe (§3.5)
    mrows = []
    for k in R["keys"]:
        e = g(MCI, k) - g(H6, k)
        rr = ruler(R, k)
        mrows.append({"quantity": k, "family": R["fam"][k], "MCI - Healthy_sliced_new dB": e, **ratios(e, rr),
                      "/ clean ruler": abs(e) / rr["clean"], "/ measured ruler": abs(e) / rr["meas"],
                      "MCI - Healthy_sliced (7 passes) dB": g(MCI, k) - g(H7, k)})
    mt = pd.DataFrame(mrows)
    mt.to_csv(OUT / "5_mci_all_features.csv", index=False)
    mf = mt.groupby("family").agg(n=("quantity", "size"),
                                  n_clean=("/ clean ruler", lambda v: int((v >= 3).sum())),
                                  n_meas=("/ measured ruler", lambda v: int((v >= 3).sum())),
                                  max_clean=("/ clean ruler", "max"), max_meas=("/ measured ruler", "max")).reset_index()
    mf.columns = ["family", "n", ">= 3x clean ruler", ">= 3x measured ruler", "max / clean ruler", "max / measured ruler"]
    top = mt.sort_values("/ clean ruler", ascending=False).head(12)
    mci_dec = dt[dt.design == MCI]
    n_c, n_m = int((mt["/ clean ruler"] >= 3).sum()), int((mt["/ measured ruler"] >= 3).sum())
    L += ["## 4. MCI_lobe (Prompt 07 §3.5): is MCI - Healthy_sliced_new larger than the rulers on any feature?",
          f"Expectation: no (the hippocampus lies deeper than the array's sensing depth). {len(mt)} quantities: ring "
          "averages and ratios, front-back / left-right indices, 21 paths, 45 cross-ratios and their (rotational and "
          f"left-right) asymmetry parts, and the remaining ring features (sub-band spectra). **{n_c}** exceed 3x the clean "
          f"ruler, **{n_m}** 3x the measured ruler (many comparisons: with a yardstick from four one-pass pairs, a few "
          "chance exceedances are possible).", md(mf, ".2f"), "",
          "Largest (by clean ruler):", md(top[["quantity", "family", "MCI - Healthy_sliced_new dB", "/ noise SD",
                                                "/ yardstick", "/ symmetry floor", "/ spread ±0.5 dB",
                                                "/ clean ruler", "/ measured ruler",
                                                "MCI - Healthy_sliced (7 passes) dB"]], ".3f"), ""]

    show = dt.loc[:, (dt != 0).any(axis=0)]
    L += ["## 5. Frozen rule (unchanged) on the test designs", f"{args.n} noisy measurements per condition; gate as in "
          "Prompt 07 (gain-invariant mode, Normal window from the v2 Normal).", md(show, ".3f"), ""]

    # ------------------------------------------------------------------ figure
    P = {d: L8.path_matrix(Q[d]) for d in (LO, MCI, H6, H7)}
    L8.draw_maps([("LeftOnly minus Healthy_sliced (7 passes)", P[LO] - P[H7]),
                  ("LeftOnly minus Healthy_sliced_new (6 passes)", P[LO] - P[H6]),
                  ("Predicted, locality model (cf56de8)", mat_from(pred, "predicted LeftOnly change dB (locality)")),
                  ("Predicted, no-locality baseline (cf56de8)", mat_from(pred, "no-locality baseline dB")),
                  ("MCI minus Healthy_sliced_new", P[MCI] - P[H6])],
                 "LeftOnly_test (left temporal + parietal lobes) and MCI_lobe: observed against predicted path changes",
                 FIG / "leftonly_mci_maps.png", 5)

    # ------------------------------------------------------------------ claims
    claims = [{"claim": "the LeftOnly predictions were scored unchanged (cf56de8)",
               "number": f"predictions.md / .csv identical to cf56de8: {unchanged and clean_wt}",
               "baseline": "git", "verdict": "holds" if unchanged and clean_wt else "VIOLATED"}]
    for _, r in pr.iterrows():
        claims.append({"claim": f"LeftOnly prediction {r.prediction} ({r.reference})",
                       "number": (f"observed {r['observed dB']:+.3f} dB vs predicted {r['predicted dB']:+.3f}; "
                                  if np.isfinite(r["observed dB"]) else "") + str(r["committed verdict"]),
                       "baseline": str(r["committed rule"]),
                       "verdict": f"{r.label}" + (f" (measured: {r['label (measured)']})" if r["label (measured)"]
                                                  and not str(r["label (measured)"]).startswith("on the") else "")})
    for k, v in chi_res.items():
        claims.append({"claim": f"gain-invariant left-right cross-ratios: LeftOnly asymmetry detected and in the predicted "
                                f"direction ({k})",
                       "number": f"{v['n_meas']}/{v['n']} beyond 3x measured ruler (±2 dB: {v['n_meas2']}); rms error "
                                 f"locality {v['rms_loc']:.3f} vs baseline {v['rms_base']:.3f} dB; sign agrees "
                                 f"{v['agree']}/{v['n_big']}",
                       "baseline": "decision rule fixed before the first run; derived from cf56de8",
                       "verdict": "holds" if v["holds"] else "fails"})
    claims.append({"claim": "MCI_lobe - Healthy_sliced_new exceeds the rulers on any feature (expected: no)",
                   "number": f"{n_c}/{len(mt)} beyond 3x clean ruler, {n_m}/{len(mt)} beyond 3x measured ruler; largest "
                             f"{top.iloc[0].quantity} {top.iloc[0]['MCI - Healthy_sliced_new dB']:+.3f} dB "
                             f"({top.iloc[0]['/ clean ruler']:.1f}x clean)",
                   "baseline": "clean / measured ruler", "verdict": "no (as expected)" if n_c == 0 else
                   ("only on the clean ruler" if n_m == 0 else "yes: see section 4")})
    for rname in ("binary_R31", "three", "three_merged"):
        r = mci_dec[(mci_dec.rule == rname) & mci_dec.condition.str.startswith("typical")].iloc[0]
        claims.append({"claim": f"frozen {rname} labels MCI_lobe as Normal",
                       "number": f"{r.Normal:.2f} Normal, {r.UNCERTAIN:.2f} UNCERTAIN, {r.INVALID:.2f} INVALID",
                       "baseline": "frozen rule unchanged (typical, ±0.5 dB gain)",
                       "verdict": "holds" if r.Normal >= 0.95 else "weakened" if r.Normal >= 0.5 else "fails"})
    cl = pd.DataFrame(claims)
    cl.to_csv(OUT / "claims.csv", index=False)
    L += ["Figure `figures/leftonly_mci_maps.png`.", "", "## Claims", md(cl), "", NOTE]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print((OUT / "report.md").read_text(encoding="utf-8"))


md = L7.md

if __name__ == "__main__":
    main()
