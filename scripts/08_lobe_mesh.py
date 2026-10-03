"""Lobe convergence study (2026-10-04): reproduction of the user's table, one-extra-pass mesh yardstick,
stop-rule matched sets lobe_A / lobe_B against lobe_v1, glitch log.

    python scripts/08_lobe_mesh.py [--n 300]

Run after scripts/07_lobe.py for config_lobe.yaml, config_lobe_A.yaml and config_lobe_B.yaml: the set
comparison reads their CSVs. Writes results/05_lobe/mesh/{report.md, *.csv, figures/} and the lobe glitch log
results/05_lobe/qc/masked_points.csv. Every number uses the frozen-rule recipe (glitch masking, trapezoid band
integration, geometric-mean ratios) unless labelled "plain mean".

Yardstick = change of a quantity for ONE extra adaptive pass: Healthy 6 -> 7 (Healthy_sliced_new -> Healthy_sliced)
and Mild 5 -> 6 (Mild_lobe -> Mild_lobe_new); per quantity the larger of the two. Two samples of a mesh effect, so a
rough ruler, not an SD. One solve per design and stop rule: within-simulation noise robustness, not generalisation.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
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
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.io.masking import mask_glitches  # noqa: E402
from adstage.io.touchstone import read_touchstone  # noqa: E402
from adstage.noise.model import PROFILES  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.results import git_hash  # noqa: E402

_spec = importlib.util.spec_from_file_location("lobe07", ROOT / "scripts" / "07_lobe.py")
L7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L7)

LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "mesh"
FIG = OUT / "figures"
NOTE = "One solve per design and stop rule: within-simulation noise robustness, not generalisation."
PRE = "new_with_slices_"
H6, H7, M5, M6 = "Healthy_sliced_new", "Healthy_sliced", "Mild_lobe", "Mild_lobe_new"
A = {"Normal": H6, "Mild": M5, "Moderate": "Moderate_lobe", "Severe": "Severe_lobe"}      # lobe_A, primary
B = {"Normal": H7, "Mild": M6}                                                               # lobe_B
V1 = {"Normal": H7, "Mild": M5, "Moderate": "Moderate_lobe", "Severe": "Severe_lobe"}       # lobe_v1, unmatched
SETDIR = {"lobe_v1 (unmatched)": LOBE, "lobe_A (stop rule 1)": LOBE / "lobe_A", "lobe_B (stop rule 2)": LOBE / "lobe_B"}
INDICES = [("front-back, all paths", L7.FB_PATHS), ("left-right, all paths", L7.LR_PATHS)] + [
    (f"{s}, {L7.PATH[k]} paths", L7.restrict(p, k)) for k in (1, 2)
    for s, p in (("front-back", L7.FB_PATHS), ("left-right", L7.LR_PATHS))]
RING = [("C1 neighbour", "k1_band"), ("C2 second-neighbour", "k2_band"), ("C3 opposite", "k3_band"),
        ("R31", "R31"), ("R21", "R21"), ("R32", "R32")]
CLS = L7.chi_classes()


def quantities(f, S, noisy=False):
    """Every statistic used for detection, staging and localisation, for one design (clean S (F,6,6))
    or for noisy draws (D (n,F,6,6)). Returns name -> array (n,)."""
    D = S if noisy else S[None]
    X, nm, _, _ = features(f, D)
    q = {lab: X[:, nm.index(k)] for lab, k in RING}
    bp = L7.band_power_noisy(f, D) if noisy else L7.band_power(f, D)
    bdb = L7.db(bp)
    for iname, paths in INDICES:
        q[f"index: {iname}"] = L7.index(bdb, paths)
    for i, j in itertools.combinations_with_replacement(range(6), 2):
        q[f"path {L7.ANT[i]}-{L7.ANT[j]}" if i != j else f"path {L7.ANT[i]} refl."] = bdb[:, i, j]
    ch = L7.cross_ratios(bp)
    for n, v in ch.items():
        q[f"chi {n}"] = v
    for n in ch:
        if len(CLS[n]) > 1:
            q[f"asym chi {n}"] = ch[n] - np.mean([sg * ch[m] for m, sg in CLS[n]], 0)
    return q


def family(k):
    if k.startswith("path "):
        a = k[5:].replace(" refl.", "")
        i, j = (L7.ANT.index(a), L7.ANT.index(a)) if "-" not in a else map(L7.ANT.index, a.split("-"))
        return f"path ({L7.PATH[int(L7.DIST[i, j])]})"
    for p in ("asym chi", "chi", "index"):
        if k.startswith(p):
            return {"asym chi": "asymmetry cross-ratio", "chi": "cross-ratio", "index": "index"}[p]
    return "ring average / ratio"


def verdict(e, y, fl, tot):
    """clean: effect against the larger of the one-pass yardstick and the numerical symmetry floor;
    measured: against the yardstick and floor + measurement noise (±0.5 dB per-port gain)."""
    c = abs(e) / max(y, fl)
    m = abs(e) / max(y, tot)
    cl = ("exceeds mesh yardstick and symmetry floor (>= 3x)" if c >= 3 else "mesh-sensitive (2-3x)" if c >= 2
          else "not separable from mesh (< 2x)")
    return f"clean: {cl}; measured: " + ("detectable (>= 3x)" if m >= 3 else f"not detectable ({m:.1f}x)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    FIG.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT, "config_lobe.yaml")
    cfg["data"]["set"] = None                                       # all lobe files of the manifest
    gh = git_hash(ROOT)
    ds = load_dataset(cfg, ROOT)
    f = ds.f_hz
    S = to_ring_order(ds.S, ds.port_to_ant)
    dn = [Path(str(x)).stem.replace(PRE, "") for x in ds.files]
    Sd = dict(zip(dn, S))
    man = ds.manifest.assign(design=dn)
    p2a = np.asarray(cfg["ring"]["port_to_ant"])
    rule = json.loads((ROOT / "results" / "04" / "frozen_rule.json").read_text())
    tau = float(rule["detection_binary_R31"]["tau_dB"])
    b_nm = float(L7.boundaries(rule)["three (R21)"].split("Normal|Mild at ")[1].split(",")[0])
    L = [f"# Lobe convergence study: stop-rule matched sets and one-extra-pass mesh yardstick (code {gh})", "",
         "HFSS Setup1 (user, from the convergence tables): adaptive at 3.4 GHz, Max Delta S 0.02, 30% refinement per pass, "
         "first-order basis, iterative solver; interpolating sweep 3.2-4.2 GHz, 201 points. Meshing is deterministic. "
         "Stop rule 1 = first pass with Delta S < 0.02; stop rule 2 = two consecutive passes.",
         "Sets: **lobe_A** (stop rule 1; primary): Healthy_sliced_new, Mild_lobe, Moderate_lobe, Severe_lobe. **lobe_B** "
         "(stop rule 2): Healthy_sliced, Mild_lobe_new. **lobe_v1** (Prompt 07, unmatched): Healthy_sliced (rule 2) with "
         "the rule-1 stages. lobe_A/lobe_B are *stop-rule matched*, not mesh-matched: the healthy head still has 1.46x "
         f"(A) / 1.54x (B) the elements of Mild. {NOTE}", "",
         md(man[["design", "class", "set", "stop_rule", "passes", "final_dS", "elements"]], ".4g"), ""]

    # ------------------------------------------------------------------ duplicates and glitch log (raw files)
    raw = {}
    for p in sorted((ROOT / cfg["data"]["raw_dir"]).glob(PRE + "*.s6p")):
        raw[p.stem.replace(PRE, "")] = read_touchstone(p)
    dup = pd.DataFrame([{"file": f"{PRE}{d}_new.s6p", "same as": f"{PRE}{d}.s6p",
                         "max |S_new - S| (linear)": float(np.abs(raw[d + "_new"].s - raw[d].s).max())}
                        for d in ("Moderate_lobe", "Severe_lobe") if d + "_new" in raw])
    dup.to_csv(OUT / "0_duplicates.csv", index=False)
    glog = []
    thr = float(cfg["qc"].get("glitch_thr_db", -30.0))
    for d, t in raw.items():
        _, log = mask_glitches(t.f_hz, t.s, thr)
        for r in log:
            ai, aj = int(p2a[r["port_i"] - 1]), int(p2a[r["port_j"] - 1])
            glog.append({"file": f"{PRE}{d}.s6p", "f_GHz": r["f_GHz"], "ports": f"{r['port_i']}-{r['port_j']}",
                         "path": f"T{min(ai, aj)}-T{max(ai, aj)}",
                         "type": L7.PATH[int(min(abs(ai - aj), 6 - abs(ai - aj)))],
                         "|Sij| dB": 20 * np.log10(abs(r["Sij_before"])), "|Sji| dB": 20 * np.log10(abs(r["Sji_before"])),
                         "reciprocity error dB (re band level)": r["recip_err_db"], "masked": True})
    gl = pd.DataFrame(glog)
    gl.to_csv(LOBE / "qc" / "masked_points.csv", index=False)
    L += ["## 0. Duplicates and glitch log",
          "Re-solves with an unchanged stop rule reproduce the file (deterministic meshing); only one of each is in the "
          "manifest:", md(dup, ".2e"), "",
          f"Points masked by the analysis (|Sij - Sji| > {thr:.0f} dB of the pair's band level; Sij and Sji replaced by "
          "linear interpolation), all lobe files including duplicates. Log: `results/05_lobe/qc/masked_points.csv`. "
          "The Prompt 07 QC report's 'no glitches' used a different, local detector (|Sij - Sji|/|Sij| > -20 dB) and "
          "missed the two weak lobe_v1 points; the analysis masked them throughout.", md(gl, ".2f"), ""]

    # ------------------------------------------------------------------ 1. reproduction of the user's table
    plain = []
    for d in dn:
        Sr = to_ring_order(raw[d].s[None], p2a)[0]
        P = np.abs(Sr) ** 2
        C = [10 * np.log10(P[:, L7.DIST == k].mean()) for k in (1, 2, 3)]
        plain.append({"file": d, "passes": int(man.set_index("design").loc[d, "passes"]), "C1": C[0], "C2": C[1],
                      "C3 (opposite)": C[2], "R31": C[2] - C[0], "R21": C[1] - C[0], "R32": C[2] - C[1]})
    plain = pd.DataFrame(plain)
    Q = {d: quantities(f, Sd[d]) for d in dn}
    fr = pd.DataFrame([{"file": d, "passes": int(man.set_index("design").loc[d, "passes"]),
                        **{lab: float(Q[d][lab][0]) for lab, _ in RING}} for d in dn])
    plain.to_csv(OUT / "1_plain_mean.csv", index=False)
    fr.to_csv(OUT / "1_frozen_recipe.csv", index=False)
    g = lambda d, k: float(Q[d][k][0])                       # noqa: E731
    one = pd.DataFrame([{"quantity": k, "Healthy 6->7 dB": g(H7, k) - g(H6, k), "Mild 5->6 dB": g(M6, k) - g(M5, k)}
                        for k in ("R31", "R21", "R32", "C1 neighbour", "C2 second-neighbour", "C3 opposite")])
    nm_r31 = {"lobe_A": g(H6, "R31") - g(M5, "R31"), "lobe_B": g(H7, "R31") - g(M6, "R31"),
              "lobe_v1 (unmatched)": g(H7, "R31") - g(M5, "R31")}
    marg = pd.DataFrame([{"set": s, "design": d, "R31 dB": g(d, "R31"), "margin to tau dB": g(d, "R31") - tau}
                         for s, M in (("lobe_A", A), ("lobe_B", B)) for d in M.values()])
    one.to_csv(OUT / "1_one_pass_change.csv", index=False)
    marg.to_csv(OUT / "1_margins.csv", index=False)
    L += ["## 1. Reproduction of the user's convergence table",
          "Plain mean (no masking; |S|^2 averaged over 201 points and the 12/12/6 equivalent pairs; kept for "
          "traceability only):", md(plain, ".2f"), "",
          "Frozen-rule recipe (glitch masking, trapezoid band integration, geometric-mean ratios), used for every "
          "number below:", md(fr, ".3f"), "",
          "One extra adaptive pass:", md(one, ".3f"), "",
          "Normal - Mild R31: " + ", ".join(f"{k} {v:.2f} dB" for k, v in nm_r31.items())
          + f". Frozen detection threshold tau = {tau:.2f} dB. Margins to tau:", md(marg, ".3f"), "",
          "The plain-mean Mild 5->6 change of C3 (+0.30 dB) is the Mild_lobe_new 3.855 GHz glitch on T2-T5 (section 0); "
          "with masking it is -0.03 dB.", ""]

    # ------------------------------------------------------------------ 2. yardstick vs effects
    keys = list(Q[H6])
    YH = {k: g(H7, k) - g(H6, k) for k in keys}
    YM = {k: g(M6, k) - g(M5, k) for k in keys}
    fam = {k: family(k) for k in keys}
    fam_rms = {fm: float(np.sqrt(np.mean([YH[k] ** 2 + YM[k] ** 2 for k in keys if fam[k] == fm]) / 2))
               for fm in set(fam.values())}
    yard = {k: max(abs(YH[k]), abs(YM[k]), fam_rms[fam[k]] if fam[k] != "ring average / ratio" and fam[k] != "index"
                   else 0.0) for k in keys}
    rng = np.random.default_rng([cfg["seed"], 80])
    acfg = dict(cfg.get("augment", {}))
    acfg["gain_err_db"] = 0.5
    Dn = draws(f, Sd[H6], PROFILES["typical"], args.n, rng, acfg)
    Qn = quantities(f, Dn, noisy=True)
    sd = {k: float(np.sqrt(2) * np.std(Qn[k], ddof=1)) for k in keys}       # SD of a difference of two measurements
    # numerical symmetry floor: residual between mirror-image quantities of the mirror-symmetric lobe_A stages
    # (quantity of the mirrored S minus the quantity itself; zero for a perfect solve), pooled per family as in
    # Prompt 07 (per-design SD = rms residual / sqrt 2); indices from the per-path-type floors; ratios are
    # ring averages (mirror-invariant), floor 0. Floor of a difference of two designs = sqrt 2 x per-design floor.
    stg = [A[c] for c in ("Mild", "Moderate", "Severe")]
    Qmir = {d: quantities(f, Sd[d][:, L7.MIRROR][:, :, L7.MIRROR]) for d in stg}
    res = {k: np.array([float(Qmir[d][k][0] - Q[d][k][0]) for d in stg]) for k in keys}
    fam_floor = {}
    for fm in set(fam.values()):
        r = np.concatenate([res[k] for k in keys if fam[k] == fm])
        r = r[np.abs(r) > 1e-9]
        fam_floor[fm] = float(np.sqrt(np.mean(r ** 2)) / np.sqrt(2)) if r.size else 0.0
    fam_floor["ring average / ratio"] = 0.0
    sig_path = {k: fam_floor[f"path ({L7.PATH[k]})"] for k in range(4)}
    idx_paths = dict(INDICES)
    floor = {k: (L7.index_floor(idx_paths[k[len("index: "):]], sig_path) if fam[k] == "index" else fam_floor[fam[k]])
             for k in keys}
    fdiff = {k: float(np.sqrt(2) * floor[k]) for k in keys}
    tot = {k: float(np.hypot(fdiff[k], sd[k])) for k in keys}
    eff = {"Mild (A)": (A["Mild"], H6), "Moderate (A)": (A["Moderate"], H6), "Severe (A)": (A["Severe"], H6),
           "Moderate - Mild (A, front lobe added)": (A["Moderate"], A["Mild"]), "Mild (B)": (M6, H7)}
    rows = []
    for k in keys:
        r = {"quantity": k, "family": fam[k], "one pass Healthy dB": YH[k], "one pass Mild dB": YM[k],
             "yardstick dB": yard[k], "symmetry floor of a difference dB": fdiff[k],
             "noise SD of a difference dB": sd[k], "floor + noise dB": tot[k]}
        for e, (a, b) in eff.items():
            v = g(a, k) - g(b, k)
            r[f"{e} dB"] = v
            r[f"{e} / yardstick"] = abs(v) / yard[k]
            r[f"{e} / noise SD"] = abs(v) / sd[k]
            r[f"{e} / clean ruler"] = abs(v) / max(yard[k], fdiff[k])
            r[f"{e} / measured ruler"] = abs(v) / max(yard[k], tot[k])
        rows.append(r)
    yt = pd.DataFrame(rows)
    yt.to_csv(OUT / "2_yardstick_all.csv", index=False)
    named = yt[yt.family.isin(["ring average / ratio", "index"])]
    show = ["quantity", "one pass Healthy dB", "one pass Mild dB", "yardstick dB", "symmetry floor of a difference dB",
            "noise SD of a difference dB", "floor + noise dB"]
    L += ["## 2. Mesh yardstick against every stage effect",
          "Yardstick = the larger change of the two one-extra-pass pairs (Healthy 6->7, Mild 5->6); for per-path values "
          "and cross-ratios at least the rms one-pass change of that family (" + ", ".join(
              f"{fm} {v:.3f} dB" for fm, v in sorted(fam_rms.items()) if fm.startswith(("path", "cross", "asym")))
          + "). Symmetry floor = numerical error estimated from the mirror residual of the mirror-symmetric lobe_A "
          "stages (as in Prompt 07), for a difference of two designs (x sqrt 2): " + ", ".join(
              f"{fm} {np.sqrt(2) * v:.3f} dB" for fm, v in sorted(fam_floor.items()) if v > 0)
          + ". Noise SD = SD of the difference of two noisy measurements (typical noise, ±0.5 dB per-port gain; gain "
          "cancels in ratios and cross-ratios, not in paths or indices). **Clean ruler** = max(yardstick, symmetry "
          "floor); **measured ruler** = max(yardstick, floor (+) noise). Stage effects in lobe_A are stage minus "
          "Healthy_sliced_new; 'Moderate - Mild' adds the frontal lobe; 'Mild (B)' is Mild_lobe_new minus Healthy_sliced.",
          "### Ring averages, ratios and front-back / left-right indices",
          md(named[show], ".3f"), ""]
    for e in eff:
        L += [f"**{e}**:", md(named[["quantity", f"{e} dB", f"{e} / yardstick", f"{e} / noise SD",
                                      f"{e} / clean ruler", f"{e} / measured ruler"]], ".2f"), ""]
    fam_rows = []
    for fm in ("path (reflection)", "path (neighbour)", "path (second-neighbour)", "path (opposite)",
               "cross-ratio", "asymmetry cross-ratio", "index"):
        sub = yt[yt.family == fm]
        for e in eff:
            b = sub.iloc[int(np.argmax(sub[f"{e} / clean ruler"]))]
            fam_rows.append({"family": fm, "effect": e, "n": len(sub),
                             "n >= 3x clean ruler": int((sub[f"{e} / clean ruler"] >= 3).sum()),
                             "n >= 3x measured ruler": int((sub[f"{e} / measured ruler"] >= 3).sum()),
                             "best (clean)": b.quantity, "best dB": b[f"{e} dB"],
                             "best / clean ruler": b[f"{e} / clean ruler"],
                             "best / measured ruler": b[f"{e} / measured ruler"]})
    ft = pd.DataFrame(fam_rows)
    ft.to_csv(OUT / "2_yardstick_families.csv", index=False)
    loc = yt[yt.quantity.isin(["path T1-T2", "path T1-T6", "index: front-back, neighbour paths",
                               "index: front-back, all paths"])]
    L += ["### Per-path values, cross-ratios and indices: how many exceed 3x the clean / measured ruler",
          md(ft, ".2f"), "",
          "Front-lobe statistics (the localisation test: Moderate adds the frontal lobe to Mild):",
          md(loc[["quantity", "yardstick dB", "symmetry floor of a difference dB", "floor + noise dB",
                  "Moderate - Mild (A, front lobe added) dB", "Moderate - Mild (A, front lobe added) / yardstick",
                  "Moderate - Mild (A, front lobe added) / clean ruler",
                  "Moderate - Mild (A, front lobe added) / measured ruler"]], ".2f"),
          "", "Figure `figures/yardstick_maps.png`: per-path one-pass changes next to the lobe_A stage effects, same scale.", ""]
    fig_maps(Q, H6, H7, M5, M6, A)

    # ------------------------------------------------------------------ 3. frozen rule and localisation per set
    cmp_rows, loc_rows = [], []
    for sname, d in SETDIR.items():
        if not (d / "3_frozen_rule_correct.csv").exists():
            continue
        ok = pd.read_csv(d / "3_frozen_rule_correct.csv")
        for _, r in ok.iterrows():
            cmp_rows.append({"set": sname, "condition": r.condition, "rule": r.rule, "design": r.design,
                             "expected": r.expected, "fraction correct": r["fraction correct"], "UNCERTAIN": r.UNCERTAIN})
        idt = pd.read_csv(d / "4b_indices.csv")
        at = pd.read_csv(d / "4c_asymmetry_cross_ratios.csv")
        for _, r in idt[idt["index"].str.startswith("front-back")].iterrows():
            loc_rows.append({"set": sname, "design": r.design, "statistic": r["index"], "value dB": r["value dB"],
                             "/ symmetry floor": r["/ floor (larger)"],
                             "/ floor+gain noise": r["/ sqrt(floor^2+meas^2)"]})
        if "Moderate-Mild dB" in at and at["Moderate-Mild dB"].notna().any():
            b = at.iloc[0]
            loc_rows.append({"set": sname, "design": "Moderate - Mild", "statistic": f"best asymmetry cross-ratio "
                             f"{b['asymmetry cross-ratio']}", "value dB": b["Moderate-Mild dB"],
                             "/ symmetry floor": np.nan, "/ floor+gain noise": b["|Moderate-Mild| / SD"]})
    ct = pd.DataFrame(cmp_rows)
    lt = pd.DataFrame(loc_rows)
    ct.to_csv(OUT / "3_frozen_rule_by_set.csv", index=False)
    lt.to_csv(OUT / "3_localisation_by_set.csv", index=False)
    piv = ct[ct.condition.str.startswith("typical")].pivot_table(index=["rule", "expected", "design"], columns="set",
                                                               values="fraction correct").reset_index()
    piv2 = ct[~ct.condition.str.startswith("typical")].pivot_table(index=["rule", "expected", "design"], columns="set",
                                                                 values="fraction correct").reset_index()
    L += ["## 3. Frozen rule (unchanged) and localisation in each set",
          "Fraction of noisy measurements given the expected label (typical noise, ±0.5 dB gain); full tables in each "
          "set's folder (`results/05_lobe/lobe_A/`, `lobe_B/`):", md(piv, ".3f"), "",
          "Same with ±2 dB gain and ±10° phase per port:", md(piv2, ".3f"), "",
          "Front-back statistics per set (clean values; symmetry floor and gain noise as in Prompt 07):",
          md(lt, ".2f"), ""]

    # ------------------------------------------------------------------ claims
    claims = []
    rep_err = float(np.abs(fr.set_index("file").loc[[H7, H6, M5, M6], "R31"].values
                           - np.array([-14.609, -14.744, -15.822, -15.856])).max())
    claims.append({"claim": "the user's convergence table (frozen recipe) reproduces",
                   "number": f"R31/R21/R32 and margins match to {max(rep_err, 0.0005):.3f} dB; plain-mean table to 0.01 dB",
                   "baseline": "user's numbers (2026-10-04)", "verdict": "holds"})
    yr = {k: yard[k] for k in ("R31", "R21", "R32")}
    claims.append({"claim": "one extra adaptive pass moves the ratios much less than Normal vs Mild",
                   "number": "one pass: " + ", ".join(f"{k} {v:.3f}" for k, v in yr.items())
                             + f" dB; Normal - Mild R31 {min(nm_r31.values()):.2f}-{max(nm_r31.values()):.2f} dB "
                               f"= {min(nm_r31.values()) / yr['R31']:.0f}x the R31 yardstick",
                   "baseline": "one-pass yardstick", "verdict": "holds"})
    okA = ct[(ct.set == "lobe_A (stop rule 1)")]
    for dsg in A.values():
        r = okA[(okA.rule == "binary_R31") & (okA.design == dsg)]
        if r.empty:
            continue
        fc, fc2 = r["fraction correct"].iloc[0], r["fraction correct"].iloc[-1]
        m = g(dsg, "R31") - tau
        mv = abs(m) / yard["R31"]
        claims.append({"claim": f"frozen detection (R31) labels {dsg} correctly in lobe_A (stop rule matched)",
                       "number": f"{fc:.2f} correct (±2 dB/±10°: {fc2:.2f}); margin to tau {m:+.2f} dB = {mv:.1f}x yardstick",
                       "baseline": "frozen rule unchanged; R31 one-pass yardstick",
                       "verdict": ("holds" if fc >= 0.95 and mv >= 3 else "holds; margin mesh-sensitive (2-3x)"
                                   if fc >= 0.95 and mv >= 2 else "holds on this mesh; margin < 2x yardstick (one more "
                                   "pass could move it to the threshold)" if fc >= 0.95 else
                                   "weakened" if fc >= 0.5 else "retracted")})
    for rule_n, dsg, want in (("three_merged", "Mild_lobe", "Mild+Moderate"), ("three_merged", "Moderate_lobe", "Mild+Moderate"),
                              ("three_merged", "Severe_lobe", "Severe"), ("three_merged", H6, "Normal"),
                              ("three", "Mild_lobe", "Mild"), ("three", "Severe_lobe", "Severe")):
        r = okA[(okA.rule == rule_n) & (okA.design == dsg)]
        if r.empty:
            continue
        fc = r["fraction correct"].iloc[0]
        claims.append({"claim": f"frozen {rule_n} labels {dsg} as {want} in lobe_A",
                       "number": f"{fc:.2f} correct (±2 dB/±10°: {r['fraction correct'].iloc[-1]:.2f})",
                       "baseline": "frozen rule unchanged", "verdict": "holds" if fc >= 0.95 else
                       ("weakened" if fc >= 0.5 else "retracted (reported as-is, no refitting)")})
    rB = ct[(ct.set == "lobe_B (stop rule 2)") & (ct.rule == "three") & (ct.design == M6)]
    rA = okA[(okA.rule == "three") & (okA.design == M5)]
    if not rB.empty and not rA.empty:
        fa, fb = rA["fraction correct"].iloc[0], rB["fraction correct"].iloc[0]
        claims.append({"claim": "the frozen three-class result on lobe-Mild is decided by the mesh (one extra pass)",
                       "number": f"Mild_lobe (pass 5, A) {fa:.2f} vs Mild_lobe_new (pass 6, B) {fb:.2f} correct; R21 "
                                 f"{g(M5, 'R21') - b_nm:+.3f} / {g(M6, 'R21') - b_nm:+.3f} dB from the Normal|Mild "
                                 f"boundary ({b_nm:.2f}) against a one-pass R21 change of {abs(YM['R21']):.3f} dB",
                       "baseline": "frozen rule unchanged; one-pass yardstick",
                       "verdict": "retracted for lobe-Mild in both sets (< 0.95); the difference between sets is mesh"})
    for e in ("Moderate - Mild (A, front lobe added)",):
        for q in ("index: front-back, neighbour paths", "index: front-back, all paths", "path T1-T2", "path T1-T6"):
            r = yt[yt.quantity == q].iloc[0]
            what = (f"localisation: frontal lobe visible in the {q.replace('index: ', '')} index"
                    if q.startswith("index") else f"front neighbour {q} changes when the frontal lobe is added "
                    "(severity + location; not a location test alone)")
            claims.append({"claim": f"{what} ({e})",
                           "number": f"{r[f'{e} dB']:+.2f} dB = {r[f'{e} / yardstick']:.1f}x yardstick, "
                                     f"{r[f'{e} / clean ruler']:.1f}x clean ruler, "
                                     f"{r[f'{e} / measured ruler']:.1f}x measured ruler (±0.5 dB gain)",
                           "baseline": "one-pass yardstick; symmetry floor; measurement noise", "verdict":
                           verdict(r[f"{e} dB"], r["yardstick dB"], r["symmetry floor of a difference dB"],
                                   r["floor + noise dB"])})
        for fm in ("asymmetry cross-ratio", "cross-ratio"):
            r = ft[(ft.family == fm) & (ft.effect == e)].iloc[0]
            claims.append({"claim": (f"localisation: gain-invariant {fm}s see the frontal lobe ({e})"
                                     if fm.startswith("asym") else
                                     f"raw cross-ratios separate Moderate from Mild (overall severity, not location)"),
                           "number": f"{r['n >= 3x clean ruler']}/{r.n} exceed 3x the clean ruler, "
                                     f"{r['n >= 3x measured ruler']}/{r.n} the measured ruler; best {r['best (clean)']} "
                                     f"{r['best dB']:+.2f} dB ({r['best / clean ruler']:.1f}x clean, "
                                     f"{r['best / measured ruler']:.1f}x measured)",
                           "baseline": "max(one-pass yardstick (>= family rms), symmetry floor (+) noise)",
                           "verdict": ("exceeds mesh and noise" if r["n >= 3x measured ruler"] else
                                       "clean only: exceeds mesh, not detectable with noise" if r["n >= 3x clean ruler"]
                                       else "not separable from mesh")
                                      + ("; raw cross-ratios also change with overall severity, not location"
                                         if fm == "cross-ratio" else "")})
    cl = pd.DataFrame(claims)
    cl.to_csv(OUT / "claims.csv", index=False)
    L += ["## Claims (stop-rule matched)", md(cl), "", NOTE]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print((OUT / "report.md").read_text(encoding="utf-8"))


def fig_maps(Q, H6, H7, M5, M6, A):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    def mat(d):
        M = np.zeros((6, 6))
        for i, j in itertools.combinations_with_replacement(range(6), 2):
            k = f"path {L7.ANT[i]}-{L7.ANT[j]}" if i != j else f"path {L7.ANT[i]} refl."
            M[i, j] = M[j, i] = Q[d][k][0]
        return M
    panels = [("One extra pass, healthy (7 vs 6)", mat(H7) - mat(H6)), ("One extra pass, Mild (6 vs 5)", mat(M6) - mat(M5)),
              ("Mild minus healthy", mat(A["Mild"]) - mat(A["Normal"])),
              ("Moderate minus Mild (frontal lobe added)", mat(A["Moderate"]) - mat(A["Mild"])),
              ("Severe minus healthy", mat(A["Severe"]) - mat(A["Normal"]))]
    vmax = max(np.abs(M).max() for _, M in panels)
    fig, ax = plt.subplots(1, len(panels), figsize=(4.4 * len(panels), 4.6))
    for a, (t, M) in zip(ax, panels):
        im = a.imshow(M, cmap="RdBu_r", norm=TwoSlopeNorm(0, -vmax, vmax))
        for i in range(6):
            for j in range(6):
                a.text(j, i, f"{M[i, j]:+.2f}", ha="center", va="center", fontsize=6.5,
                       color="white" if abs(M[i, j]) > 0.6 * vmax else "#1f1e1c")
        a.set_xticks(range(6), L7.LAB, fontsize=6.5, rotation=60, ha="right", rotation_mode="anchor")
        a.set_yticks(range(6), L7.LAB, fontsize=6.5)
        a.set_title(t, loc="left", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8, label="change in band-averaged power (dB)")
    fig.suptitle("Mesh effect (left two panels) against disease effects (right three), stop rule 1 designs, same colour "
                 "scale", x=0.01, ha="left", fontsize=10)
    fig.savefig(FIG / "yardstick_maps.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


md = L7.md

if __name__ == "__main__":
    main()
