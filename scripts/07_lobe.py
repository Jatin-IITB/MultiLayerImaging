"""Prompt 07: lobe-sector phantom (set lobe_v1). QC floors, sliced-vs-v2 healthy, frozen-rule test,
asymmetry / localisation, pre-registered LeftOnly predictions.

    python scripts/07_lobe.py [--n 300] [--write-predictions]

Reads only the files listed in data/sims_lobe.csv (LeftOnly_test / MCI_lobe are not read here).
Writes results/05_lobe/{report.md, *.csv, figures/*.png}; with --write-predictions also
results/05_lobe/predictions.md + predictions.csv (commit them before LeftOnly_test exists).
Every number is from one solve per design: within-simulation noise robustness, not generalisation.
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adstage.config import load_config  # noqa: E402
from adstage.features.floor import CLIP, floor_power  # noqa: E402
from adstage.features.metrics import band_avg, ring_distance_matrix, to_ring_order  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.frozen import apply_rule  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.noise.model import PROFILES  # noqa: E402
from adstage.noise.reference import mesh_pairs  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.pipeline.quality import QualityGate  # noqa: E402
from adstage.results import git_hash  # noqa: E402

OUT = ROOT / "results" / "05_lobe"
FIG = OUT / "figures"
ANT = ["T1", "T2", "T3", "T4", "T5", "T6"]
LOBE = ["Frontal", "Temporal L", "Parietal L", "Occipital", "Parietal R", "Temporal R"]
LAB = [f"{a}\n{l}" for a, l in zip(ANT, LOBE)]
PATH = {0: "reflection", 1: "neighbour", 2: "second-neighbour", 3: "opposite"}
MIRROR = np.array([0, 5, 4, 3, 2, 1])            # x -> -x: T1, T4 fixed; T2<->T6, T3<->T5
DIST = ring_distance_matrix(6)
NOTE = "One solve per design: within-simulation noise robustness, not generalisation."


# ============================================================ basic quantities
def band_power(f, S):
    """S (..., F, 6, 6) -> band-averaged |S_ij|^2 (..., 6, 6), symmetrised over i<->j."""
    P = np.abs(S) ** 2
    bp = band_avg(f, np.moveaxis(P, -3, -1), (float(f[0]), float(f[-1])))
    return 0.5 * (bp + np.swapaxes(bp, -1, -2))


def band_power_noisy(f, D):
    bp = band_power(f, D)
    pf = floor_power(D)
    off = ~np.eye(6, dtype=bool)
    bp[:, off] = np.maximum(bp[:, off] - pf[:, None], CLIP)
    return bp


def db(x):
    return 10 * np.log10(x)


def cross_ratios(bp):
    """bp (..., 6, 6) band powers -> dict name -> (...) cross-ratio in dB.
    For 4 distinct antennas a<b<c<d, the three pairings are {ab,cd}, {ac,bd}, {ad,bc};
    chi = 10log10(pairing1 / pairing2). Per-port gains cancel exactly (each antenna appears
    once in every pairing)."""
    out = {}
    for a, b, c, d in itertools.combinations(range(6), 4):
        prs = {f"{ANT[a]}{ANT[b]}·{ANT[c]}{ANT[d]}": bp[..., a, b] * bp[..., c, d],
               f"{ANT[a]}{ANT[c]}·{ANT[b]}{ANT[d]}": bp[..., a, c] * bp[..., b, d],
               f"{ANT[a]}{ANT[d]}·{ANT[b]}{ANT[c]}": bp[..., a, d] * bp[..., b, c]}
        ks = list(prs)
        for i, j in itertools.combinations(range(3), 2):
            out[f"{ks[i]} / {ks[j]}"] = db(prs[ks[i]] / prs[ks[j]])
    return out


def index_paths(touch_a, touch_b):
    """Unordered transmission paths touching set A but not B, and B but not A."""
    pa, pb = [], []
    for i, j in itertools.combinations(range(6), 2):
        s = {i, j}
        if s & touch_a and not s & touch_b:
            pa.append((i, j))
        if s & touch_b and not s & touch_a:
            pb.append((i, j))
    return pa, pb


FB_PATHS = index_paths({0}, {3})                  # touching T1 (front) vs touching T4 (back)
LR_PATHS = index_paths({1, 2}, {4, 5})            # touching T2,T3 (left) vs T5,T6 (right)


def index(dP, paths):
    pa, pb = paths
    return np.mean([dP[..., i, j] for i, j in pa], 0) - np.mean([dP[..., i, j] for i, j in pb], 0)


def symmetry_transforms():
    """The 12 relabelings of a symmetric ring (6 rotations x 2 reflections) as index arrays."""
    out = []
    for r in range(6):
        for s in (1, -1):
            out.append((s * np.arange(6) + r) % 6)
    return out


def circulant_residual(Pdb):
    """dB band powers (6,6) minus the mean over equivalent pairs (same ring distance)."""
    R = Pdb.copy()
    for k in range(4):
        m = DIST == k
        R[m] = Pdb[m] - Pdb[m].mean()
    return R


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--write-predictions", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    FIG.mkdir(parents=True, exist_ok=True)
    os.environ["MLI_CONFIG"] = "config_lobe.yaml"
    cfg = load_config(ROOT)
    gh = git_hash(ROOT)
    ds = load_dataset(cfg, ROOT)
    f = ds.f_hz
    S = to_ring_order(ds.S, ds.port_to_ant)
    des = {c: i for i, c in enumerate(ds.classes)}          # Normal/Mild/Moderate/Severe -> index
    name = {"Normal": "Healthy_sliced", "Mild": "Mild_lobe", "Moderate": "Moderate_lobe", "Severe": "Severe_lobe"}
    cfg_u = load_config(ROOT, "config_repeats.yaml")
    du = load_dataset(cfg_u, ROOT)
    Su = to_ring_order(du.S, du.port_to_ant)
    assert np.allclose(du.f_hz, f), "uniform and lobe grids differ"
    pairs_u = mesh_pairs(du.files, du.manifest)
    acfg = dict(cfg.get("augment", {}))
    acfg["gain_err_db"] = 0.5
    prof = PROFILES["typical"]
    print(f"code {gh}; lobe designs {[name[c] for c in ds.classes]}; band {f[0] / 1e9:.1f}-{f[-1] / 1e9:.1f} GHz")
    L = [f"# Lobe-sector phantom (set lobe_v1): analysis (code {gh})", "",
         f"Designs: {', '.join(name[c] for c in ds.classes)} (3.2-4.2 GHz, 201 points). {NOTE} "
         "Noise unless stated: typical profile + setup perturbation + per-port gain ±0.5 dB. "
         "Antennas in ring order T1..T6 = Frontal, Temporal L, Parietal L, Occipital, Parietal R, Temporal R.", ""]
    claims = []

    # clean band powers (dB) and ring-features
    BP = {c: band_power(f, S[i]) for c, i in des.items()}
    BPdb = {c: db(v) for c, v in BP.items()}

    # ---------------------------------------------------------------- 3.1 symmetry floors
    rows = []
    Hn = BPdb["Normal"]
    for k in range(4):
        m = DIST == k
        per_f = np.abs(S[des["Normal"]][:, m]) ** 2                    # (F, n_pairs)
        rows.append({"floor": "circulant (Healthy_sliced)", "path": PATH[k],
                     "band-power SD dB": float(Hn[m].std(ddof=1)), "band-power max-min dB": float(np.ptp(Hn[m])),
                     "median over f of per-frequency SD dB": float(np.median(db(per_f).std(1, ddof=1)))})
    mirror_rows = []
    for c in ("Normal", "Mild", "Moderate", "Severe"):
        Pd = BPdb[c]
        Sf = np.abs(S[des[c]]) ** 2
        for k in range(4):
            ent = [(i, j) for i in range(6) for j in range(i, 6) if DIST[i, j] == k
                   and (min(MIRROR[i], MIRROR[j]), max(MIRROR[i], MIRROR[j])) != (i, j)
                   and (i, j) < (min(MIRROR[i], MIRROR[j]), max(MIRROR[i], MIRROR[j]))]
            if not ent:
                continue
            d = np.array([Pd[i, j] - Pd[MIRROR[i], MIRROR[j]] for i, j in ent])
            dfreq = np.array([db(Sf[:, i, j]) - db(Sf[:, MIRROR[i], MIRROR[j]]) for i, j in ent])
            mirror_rows.append({"design": name[c], "path": PATH[k], "mirror pairs": len(ent),
                                "band-power rms diff dB": float(np.sqrt(np.mean(d ** 2))),
                                "median over f of rms diff dB": float(np.median(np.sqrt(np.mean(dfreq ** 2, 0))))})
    circ, mir = pd.DataFrame(rows), pd.DataFrame(mirror_rows)
    circ.to_csv(OUT / "1_circulant_floor.csv", index=False)
    mir.to_csv(OUT / "1_mirror_floor.csv", index=False)
    floor_mirror = float(np.sqrt(np.mean(mir[mir.design != "Healthy_sliced"]["band-power rms diff dB"] ** 2)))
    # per-path numerical SD of the staged (mirror-symmetric) designs: mirror-pair rms difference / sqrt 2
    staged = mir[mir.design != "Healthy_sliced"]
    sig_path = {k: float(np.sqrt(np.mean(staged[staged.path == PATH[k]]["band-power rms diff dB"] ** 2)) / np.sqrt(2))
                for k in range(4)}
    L += ["## 3.1 QC and symmetry floors",
          "Parsing, passivity, reciprocity, glitches and the port-map search: `results/05_lobe/qc/qc_report.md` "
          "(all four files pass; the port map T4,T3,T2,T1,T6,T5 ranks 1st of 60 in every file; no glitches).",
          "Circulant floor = spread of equivalent paths in Healthy_sliced (should be identical by symmetry):",
          md(circ, ".3f"), "",
          "Mirror floor = difference between mirror-image paths (T2<->T6, T3<->T5) in the mirror-symmetric designs:",
          md(mir, ".3f"), "",
          f"Pooled mirror floor over Mild/Moderate/Severe band powers: **{floor_mirror:.3f} dB** (rms). Per-path "
          "numerical SD of the staged designs (mirror rms / sqrt 2), used as the noise ruler for every asymmetry claim: "
          + ", ".join(f"{PATH[k]} {v:.3f} dB" for k, v in sig_path.items())
          + ". The staged designs are 2-5x less symmetric than Healthy_sliced, so the healthy floor alone would "
          "overstate asymmetry significance.", ""]

    # ---------------------------------------------------------------- 3.2 sliced vs v2 healthy
    Xl, names, groups, _ = features(f, S)                              # clean, (4, p)
    Xu, _, _, _ = features(f, Su)                                      # clean, (9, p)
    iH = du.files.index("new_Healthy.s6p")
    solve_sd = np.sqrt(np.mean([(Xu[b] - Xu[a]) ** 2 / 2 for a, b in pairs_u], 0))
    # symmetry spread of the ring-averaged features: antenna-to-antenna spread in Healthy_sliced
    # (per-antenna band powers / per-antenna ratios), divided by sqrt(number of antennas averaged)
    sym_sd = per_antenna_spread(f, S[des["Normal"]])
    key = ["R31", "R21", "R32", "k0_band", "k1_band", "k2_band", "k3_band", "logN"]
    d = Xl[des["Normal"]] - Xu[iH]
    cmp = pd.DataFrame([{"feature": nm, "Healthy_sliced": Xl[des["Normal"]][names.index(nm)],
                         "new_Healthy (v2)": Xu[iH][names.index(nm)], "difference dB": d[names.index(nm)],
                         "/ v2 solve SD": d[names.index(nm)] / solve_sd[names.index(nm)],
                         "sliced antenna-spread SE dB": sym_sd.get(nm, np.nan),
                         "/ sliced antenna-spread SE": d[names.index(nm)] / sym_sd.get(nm, np.nan)} for nm in key])
    cmp.to_csv(OUT / "2_sliced_vs_v2_healthy.csv", index=False)
    z = np.abs(d / solve_sd)
    frac = {t: float((z < t).mean()) for t in (1, 2, 3)}
    worst = [names[i] for i in np.argsort(-z)[:5]]
    res_v2 = 3659.2 - 3640.3
    verdict = "equivalent" if np.abs(cmp["/ v2 solve SD"]).max() < 2 else (
        "small offset" if np.abs(cmp["/ v2 solve SD"]).max() < 5 else "different")
    L += ["## 3.2 Is Healthy_sliced the same head as the v2 Normal?",
          md(cmp, ".3f"), "",
          f"Across all 89 ring-symmetrised features: {100 * frac[1]:.0f}% within 1x, {100 * frac[2]:.0f}% within 2x, "
          f"{100 * frac[3]:.0f}% within 3x the v2 solve-to-solve SD; largest: {', '.join(worst)}. "
          f"The resonance moved by {res_v2:+.1f} MHz (3640 -> 3659 MHz) and the notch is shallower (-21 vs -34…-39 dB). "
          f"Verdict on the classifier features above: **{verdict}**. Caveat: the v2 skull inner radius (hidden tool "
          "Brain_sphere_1) is unknown, so a small geometry difference cannot be excluded.", ""]
    claims.append({"claim": "Healthy_sliced reproduces the v2 healthy head on the classifier features",
                   "number": "; ".join(f"{r.feature} {r['difference dB']:+.2f} dB ({r['/ v2 solve SD']:+.1f} SD)"
                                       for _, r in cmp[cmp.feature.isin(['R31', 'R21', 'R32'])].iterrows()),
                   "baseline": "v2 solve-to-solve SD (4 pairs)", "verdict": "holds" if verdict == "equivalent" else "weakened"})

    # ---------------------------------------------------------------- noisy draws for 3.3 / 3.4
    rule_path = ROOT / "results" / "04" / "frozen_rule.json"
    gate = QualityGate(cfg["gate"], f, mode="gain_invariant")
    rng_g = np.random.default_rng([cfg["seed"], 70])
    gate.fit_detune(draws(f, Su[iH], prof, 200, rng_g, acfg))       # Normal window from the v2 Normal (unchanged)
    thr = pd.read_csv(ROOT / "results" / "v2_with_v1_repeats" / "03" / "thresholds.csv")
    gate.set_floor_limit(float(thr[(thr.feature == "M5.C3") & (thr.profile == "typical")].tau_dB.iloc[0]))
    conds = {"typical, ±0.5 dB gain": acfg, "±2 dB gain + ±10° phase": {**cfg.get("augment", {}),
                                                                       "gain_err_db": 2.0, "phase_err_deg": 10.0}}
    dec_rows, noisy_bp = [], {}
    for ci, (cname, ac) in enumerate(conds.items()):
        for c, i in des.items():
            D = draws(f, S[i], prof, args.n, np.random.default_rng([cfg["seed"], 71, ci, i]), ac)
            inv = gate.check(D)["invalid"]
            lab = apply_rule(rule_path, f, D)
            if ci == 0:
                noisy_bp[c] = band_power_noisy(f, D)
            for rule, labels in lab.items():
                labs = np.where(inv, "INVALID", labels)
                vc = pd.Series(labs).value_counts(normalize=True)
                dec_rows.append({"condition": cname, "design": name[c], "rule": rule,
                                 **{k: float(vc.get(k, 0)) for k in
                                    ["Normal", "AD", "Mild", "Mild+Moderate", "Severe", "UNCERTAIN", "INVALID"]}})
    dec = pd.DataFrame(dec_rows)
    dec.to_csv(OUT / "3_frozen_rule_decisions.csv", index=False)
    show = dec.loc[:, (dec != 0).any(axis=0)]
    expect = {("binary_R31", "Healthy_sliced"): "Normal", ("binary_R31", "Mild_lobe"): "AD",
              ("binary_R31", "Moderate_lobe"): "AD", ("binary_R31", "Severe_lobe"): "AD",
              ("three", "Healthy_sliced"): "Normal", ("three", "Mild_lobe"): "Mild", ("three", "Severe_lobe"): "Severe",
              ("three_merged", "Healthy_sliced"): "Normal", ("three_merged", "Mild_lobe"): "Mild+Moderate",
              ("three_merged", "Moderate_lobe"): "Mild+Moderate", ("three_merged", "Severe_lobe"): "Severe"}
    ok_rows = []
    for (rule, dn), want in expect.items():
        for cname in conds:
            r = dec[(dec.condition == cname) & (dec.rule == rule) & (dec.design == dn)].iloc[0]
            ok_rows.append({"condition": cname, "rule": rule, "design": dn, "expected": want,
                            "fraction correct": r[want], "UNCERTAIN": r["UNCERTAIN"], "INVALID": r["INVALID"]})
    okt = pd.DataFrame(ok_rows)
    okt.to_csv(OUT / "3_frozen_rule_correct.csv", index=False)
    # feature values relative to the uniform sets
    import json
    rule = json.loads(rule_path.read_text())
    vals = []
    for src, X, cls, files in (("lobe", Xl, ds.classes, [name[c] for c in ds.classes]),
                               ("uniform", Xu, du.classes, du.files)):
        for i, c in enumerate(cls):
            vals.append({"set": src if src == "lobe" else ("uniform v1" if du.manifest.loc[i, "role"] == "mesh_repeat"
                                                           else "uniform v2"),
                         "stage": c, "solve": str(files[i]).split("/")[-1],
                         **{r: X[i][names.index(r)] for r in ("R31", "R21", "R32")}})
    vt = pd.DataFrame(vals)
    vt.to_csv(OUT / "3_ratios_lobe_vs_uniform.csv", index=False)
    bounds = boundaries(rule)
    mono = {r: bool(np.all(np.diff(vt[vt.set == "lobe"].set_index("stage").reindex(
        ["Normal", "Mild", "Moderate", "Severe"])[r].values) * (1 if r == "R21" else -1) > 0)) for r in ("R21", "R32")}
    L += ["## 3.3 Frozen rule applied unchanged to the lobe designs",
          f"`results/04/frozen_rule.json` (commit 2baddee) and the gain-invariant gate (Normal window fitted on the v2 "
          f"Normal, floor limit from the v2 thresholds) are applied without refitting to {args.n} noisy measurements per "
          "design and condition. This is the first test on a different disease geometry (regional instead of uniform "
          f"atrophy) in the same head. {NOTE}",
          "Fraction of measurements given the expected label:", md(okt, ".3f"), "",
          "All labels:", md(show, ".3f"), "",
          "Ratio values of the lobe designs next to the uniform solves (dB, clean data):", md(vt, ".2f"), "",
          f"Frozen decision boundaries: R31 tau = {rule['detection_binary_R31']['tau_dB']:.2f} dB "
          f"(margin {rule['detection_binary_R31']['margin_dB']:.2f}); "
          + "; ".join(f"{k}: {v}" for k, v in bounds.items()) + ".",
          f"Lobe ordering Normal -> Mild -> Moderate -> Severe monotone: R21 {mono['R21']}, R32 {mono['R32']} "
          "(R31 is not monotone in the uniform set either).", ""]
    for rule_n, dn in (("binary_R31", "Mild_lobe"), ("binary_R31", "Moderate_lobe"), ("binary_R31", "Severe_lobe"),
                       ("binary_R31", "Healthy_sliced"), ("three", "Mild_lobe"), ("three", "Severe_lobe"),
                       ("three_merged", "Moderate_lobe")):
        r = okt[(okt.rule == rule_n) & (okt.design == dn) & (okt.condition == "typical, ±0.5 dB gain")].iloc[0]
        r2 = okt[(okt.rule == rule_n) & (okt.design == dn) & (okt.condition != "typical, ±0.5 dB gain")].iloc[0]
        fc = r["fraction correct"]
        claims.append({"claim": f"frozen {rule_n} rule labels {dn} as {r.expected} (no refitting)",
                       "number": f"{fc:.2f} correct, {r.UNCERTAIN:.2f} uncertain (±2 dB/±10°: {r2['fraction correct']:.2f})",
                       "baseline": "trained on uniform-atrophy solves only",
                       "verdict": "holds" if fc >= 0.95 else ("weakened" if fc >= 0.5 else "retracted")})
    fig_ratios(vt, rule, bounds)

    # ---------------------------------------------------------------- 3.4 asymmetry / localisation
    dP = {c: BPdb[c] - BPdb["Normal"] for c in ("Mild", "Moderate", "Severe")}
    path_rows = []
    for c, M in dP.items():
        for i, j in itertools.combinations_with_replacement(range(6), 2):
            path_rows.append({"design": name[c], "path": f"{ANT[i]}-{ANT[j]}" if i != j else f"{ANT[i]} refl.",
                              "type": PATH[int(DIST[i, j])], "lobes": f"{LOBE[i]} / {LOBE[j]}" if i != j else LOBE[i],
                              "change dB": float(M[i, j])})
    pt = pd.DataFrame(path_rows)
    pt.to_csv(OUT / "4a_path_changes.csv", index=False)
    fig_maps(dP, name)
    # indices: clean values, symmetry floor (12 relabelings of the healthy circulant residual), measurement SD
    Rh = circulant_residual(BPdb["Normal"])
    floor_fb = float(np.sqrt(np.mean([index(Rh[np.ix_(t, t)], FB_PATHS) ** 2 for t in symmetry_transforms()])))
    floor_lr = float(np.sqrt(np.mean([index(Rh[np.ix_(t, t)], LR_PATHS) ** 2 for t in symmetry_transforms()])))
    nb_h = db(noisy_bp["Normal"])
    idx_rows = []
    variants = [("front-back, all paths", FB_PATHS), ("left-right, all paths", LR_PATHS)]
    for k in (1, 2):
        variants.append((f"front-back, {PATH[k]} paths", restrict(FB_PATHS, k)))
        variants.append((f"left-right, {PATH[k]} paths", restrict(LR_PATHS, k)))
    for c in ("Normal", "Mild", "Moderate", "Severe"):
        nb = db(noisy_bp[c]) - nb_h.mean(0)
        for iname, paths in variants:
            flh = float(np.sqrt(np.mean([index(Rh[np.ix_(t, t)], paths) ** 2 for t in symmetry_transforms()])))
            flm = index_floor(paths, sig_path)
            fl = max(flh, flm)
            v = float(index(BPdb[c] - BPdb["Normal"], paths))
            meas = float(index(nb, paths).std(ddof=1))
            idx_rows.append({"design": name[c], "index": iname, "value dB": v, "healthy floor dB": flh,
                             "staged mirror floor dB": flm, "/ floor (larger)": v / fl,
                             "measurement SD dB (±0.5 dB gain)": meas, "/ sqrt(floor^2+meas^2)": v / np.hypot(fl, meas)})
    idt = pd.DataFrame(idx_rows)
    idt.to_csv(OUT / "4b_indices.csv", index=False)
    # cross-ratios
    CH = {c: cross_ratios(BP[c]) for c in BP}
    cnames = list(CH["Normal"])
    # symmetry floor: same cross-ratio evaluated on the 12 relabelings of the healthy head
    floor_chi = np.array([np.std([cross_ratios(BP["Normal"][np.ix_(t, t)])[n] for t in symmetry_transforms()], ddof=1)
                          for n in cnames])
    chin = {c: cross_ratios(noisy_bp[c]) for c in noisy_bp}
    meas_chi = np.array([chin["Normal"][n].std(ddof=1) for n in cnames])
    sd_chi = np.hypot(floor_chi, meas_chi)
    ct = pd.DataFrame({"cross-ratio": cnames,
                       **{f"Δ {name[c]} dB": [CH[c][n] - CH["Normal"][n] for n in cnames] for c in ("Mild", "Moderate", "Severe")},
                       "symmetry floor dB": floor_chi, "measurement SD dB": meas_chi})
    ct["Moderate-Mild (front affected vs not) dB"] = ct["Δ Moderate_lobe dB"] - ct["Δ Mild_lobe dB"]
    ct["|Moderate-Mild| / SD"] = np.abs(ct["Moderate-Mild (front affected vs not) dB"]) / sd_chi
    ct["involves T1 (front)"] = ct["cross-ratio"].str.contains("T1")
    ct = ct.sort_values("|Moderate-Mild| / SD", ascending=False)
    ct.to_csv(OUT / "4c_cross_ratios.csv", index=False)
    top = ct.head(8)
    nsig = int((ct["|Moderate-Mild| / SD"] >= 3).sum())
    # asymmetry cross-ratios: each cross-ratio minus the mean of its symmetry-equivalent copies (zero for ANY
    # rotationally symmetric head, still gain-invariant). Only these can carry location information.
    cls = chi_classes()
    def asym(chis):
        return {n: chis[n] - np.mean([sg * chis[m] for m, sg in cls[n]], 0) for n in cnames}
    AS = {c: asym(CH[c]) for c in CH}
    ASn = {c: asym(chin[c]) for c in chin}
    floor_as = np.array([abs(AS["Normal"][n]) for n in cnames])            # healthy residual = numerical floor
    pooled_floor_as = float(np.sqrt(np.mean(floor_as ** 2)))
    mm = mirror_map()
    dm = [AS[c][n] - sg * AS[c][m] for c in ("Mild", "Moderate", "Severe") for n, (m, sg) in mm.items() if m != n]
    mirror_floor_as = float(np.sqrt(np.mean(np.square(dm))) / np.sqrt(2))   # per-design numerical SD
    fl_as = max(pooled_floor_as, mirror_floor_as)
    meas_as = np.array([ASn["Normal"][n].std(ddof=1) for n in cnames])
    sd_as = np.sqrt(2) * np.hypot(fl_as, meas_as)                          # Moderate - Mild: two designs
    at = pd.DataFrame({"asymmetry cross-ratio": cnames,
                       **{f"{name[c]} dB": [AS[c][n] for n in cnames] for c in ("Normal", "Mild", "Moderate", "Severe")},
                       "SD dB (floor+meas)": sd_as})
    at["Moderate-Mild dB"] = at["Moderate_lobe dB"] - at["Mild_lobe dB"]
    at["|Moderate-Mild| / SD"] = np.abs(at["Moderate-Mild dB"]) / sd_as
    at["involves T1 (front)"] = at["asymmetry cross-ratio"].str.contains("T1")
    at = at[[len(cls[n]) > 1 for n in at["asymmetry cross-ratio"]]].sort_values("|Moderate-Mild| / SD", ascending=False)
    at.to_csv(OUT / "4c_asymmetry_cross_ratios.csv", index=False)
    nsig_as = int((at["|Moderate-Mild| / SD"] >= 3).sum())
    nsig_as_t1 = int(((at["|Moderate-Mild| / SD"] >= 3) & at["involves T1 (front)"]).sum())
    L += ["## 3.4 Asymmetry and localisation",
          "### (a) Per-path change maps (stage minus Healthy_sliced, band power, clean data)",
          "Figure `figures/4a_path_change_maps.png`. Largest changes per design:",
          md(pt.reindex(pt["change dB"].abs().sort_values(ascending=False).index).groupby("design").head(4), ".3f"), "",
          "Neighbour-path changes (both directions averaged):",
          md(pt[pt.type == "neighbour"].pivot(index="path", columns="design", values="change dB").reset_index(), ".3f"), "",
          "### (b) Front-back and left-right indices",
          "front-back = mean change of transmission paths touching T1 (front, not T4) minus those touching T4 (back, "
          "not T1); left-right = paths touching T2/T3 (left, not T5/T6) minus those touching T5/T6. Healthy floor = rms "
          "of the same index over the 12 symmetry relabelings of the healthy circulant residual; staged mirror floor = "
          "the index's SD from the per-path numerical SD of the staged designs; verdicts use the larger. Measurement SD "
          "includes ±0.5 dB per-port gain errors, which these indices do NOT cancel.",
          md(idt, ".3f"), "",
          "### (c) Gain-invariant cross-ratios",
          f"45 cross-ratios (15 sets of 4 antennas x 3 pairings). SD = symmetry floor (12 relabelings of the healthy "
          f"head) and measurement noise in quadrature. {nsig} of 45 separate front-affected Moderate from front-healthy "
          "Mild by >= 3 SD; the top 8:",
          md(top.drop(columns=["involves T1 (front)"]), ".3f"), "",
          "These raw cross-ratios mix path distances (e.g. T1T4·T2T5 / T1T5·T2T4 = (opposite / second-neighbour)^2 for a "
          "symmetric head), so they also change for a uniformly diseased head: they measure overall severity, not "
          "location. Moderate is also more severe than Mild everywhere, so the table above does NOT show front-lobe "
          "localisation.", "",
          f"**Asymmetry cross-ratios** (each minus the mean of its symmetry-equivalent copies; zero for any rotationally "
          f"symmetric head, still gain-invariant). Numerical floor per design: healthy residual rms {pooled_floor_as:.3f} dB, "
          f"staged mirror residual {mirror_floor_as:.3f} dB (larger used); SD of a Moderate-Mild difference = sqrt2 x "
          f"(floor (+) measurement). "
          f"{nsig_as} of {len(at)} separate Moderate from Mild by >= 3 SD ({nsig_as_t1} of them involve T1). Top 8:",
          md(at.head(8), ".3f"), ""]
    for iname in ("front-back, neighbour paths", "front-back, all paths"):
        fb_mod = idt[(idt.design == "Moderate_lobe") & (idt["index"] == iname)].iloc[0]
        fb_mild = idt[(idt.design == "Mild_lobe") & (idt["index"] == iname)].iloc[0]
        claims.append({"claim": f"front-affected Moderate differs front-to-back ({iname})",
                       "number": f"Moderate {fb_mod['value dB']:+.2f} dB = {fb_mod['/ floor (larger)']:+.1f}x floor (Mild "
                                 f"{fb_mild['value dB']:+.2f}); with ±0.5 dB gain errors {fb_mod['/ sqrt(floor^2+meas^2)']:+.1f}x",
                       "baseline": "symmetry floor of the healthy sliced head; and measurement noise incl. per-port gain",
                       "verdict": f"clean: {verdict_ratio(abs(fb_mod['/ floor (larger)']))}; with gain errors: "
                                  f"{verdict_ratio(abs(fb_mod['/ sqrt(floor^2+meas^2)']))}"})
    claims.append({"claim": "raw cross-ratios separate Moderate from Mild (severity, not location)",
                   "number": f"{nsig}/45 >= 3 SD; best {top.iloc[0]['cross-ratio']} "
                             f"{top.iloc[0]['Moderate-Mild (front affected vs not) dB']:+.2f} dB "
                             f"({top.iloc[0]['|Moderate-Mild| / SD']:.1f} SD)",
                   "baseline": "symmetry floor + measurement noise",
                   "verdict": "holds as severity; not a location claim"})
    ba = at.iloc[0]
    claims.append({"claim": "gain-invariant ASYMMETRY cross-ratios see the front-lobe involvement of Moderate",
                   "number": f"{nsig_as}/{len(at)} >= 3 SD ({nsig_as_t1} involve T1); best {ba['asymmetry cross-ratio']} "
                             f"{ba['Moderate-Mild dB']:+.2f} dB ({ba['|Moderate-Mild| / SD']:.1f} SD)",
                   "baseline": "larger of healthy / staged-mirror asymmetry floor, x sqrt2 (two designs), + measurement noise",
                   "verdict": (verdict_ratio(ba["|Moderate-Mild| / SD"]) if nsig_as else
                               f"not significant (best {ba['|Moderate-Mild| / SD']:.1f} SD; "
                               f"{int(at.head(8)['involves T1 (front)'].sum())} of the top 8 involve T1)")})
    for c in ("Mild", "Moderate", "Severe"):
        r = idt[(idt.design == name[c]) & (idt["index"] == "left-right, all paths")].iloc[0]
        claims.append({"claim": f"left-right index of {name[c]} is ~0 (mirror-symmetric by construction; a check)",
                       "number": f"{r['value dB']:+.3f} dB = {r['/ floor (larger)']:+.1f}x floor",
                       "baseline": "larger of healthy / staged-mirror floor",
                       "verdict": "check passes" if abs(r["/ floor (larger)"]) < 2 else "check FAILS"})

    # ---------------------------------------------------------------- 3.4 (d) predictions
    fl_fb = max(floor_fb, index_floor(FB_PATHS, sig_path))
    fl_lr = max(floor_lr, index_floor(LR_PATHS, sig_path))
    pred = predictions(dP["Mild"], BPdb, Xl, names, des, rule, bounds, fl_fb, fl_lr, CH, sd_chi, cnames)
    pred["paths"]["2x numerical noise of path type dB"] = [2 * sig_path[{v: k for k, v in PATH.items()}[t]]
                                                          for t in pred["paths"]["type"]]
    if args.write_predictions:
        write_predictions(pred, gh, fl_fb, fl_lr, sig_path)
    L += ["### (d) LeftOnly_test predictions", "Written to `results/05_lobe/predictions.md` (pre-registered; "
          "scored only after LeftOnly_test arrives).", ""]
    L += ["## Claims", md(pd.DataFrame(claims)), "", NOTE]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    pd.DataFrame(claims).to_csv(OUT / "claims.csv", index=False)
    print((OUT / "report.md").read_text(encoding="utf-8"))


def index_floor(paths, sig_path):
    """SD of an index from independent per-path numerical noise (sigma by path type)."""
    pa, pb = paths
    va = sum(sig_path[int(DIST[p])] ** 2 for p in pa) / len(pa) ** 2
    vb = sum(sig_path[int(DIST[p])] ** 2 for p in pb) / len(pb) ** 2
    return float(np.sqrt(va + vb))


def mirror_map():
    """Cross-ratio name -> (name of its left-right mirror image, sign)."""
    names = list(cross_ratios(np.ones((6, 6))).keys())
    parsed = {n: _parse(n) for n in names}
    lookup = {}
    for n, (a, b) in parsed.items():
        lookup[(a, b)] = (n, 1)
        lookup[(b, a)] = (n, -1)
    m = {ANT[i]: ANT[MIRROR[i]] for i in range(6)}
    out = {}
    for n, (a, b) in parsed.items():
        ra = frozenset(frozenset(m[x] for x in pr) for pr in a)
        rb = frozenset(frozenset(m[x] for x in pr) for pr in b)
        out[n] = lookup[(ra, rb)]
    return out


def restrict(paths, k):
    pa, pb = paths
    return [p for p in pa if DIST[p] == k], [p for p in pb if DIST[p] == k]


def per_antenna_spread(f, S):
    """Antenna-to-antenna SD of per-antenna versions of the ring-averaged features, / sqrt(6)."""
    P = np.abs(S) ** 2
    idx = np.arange(6)
    bp = {k: band_avg(f, (0.5 * (P[:, (idx + k) % 6, idx] + P[:, (idx - k) % 6, idx])).T, (float(f[0]), float(f[-1])))
          for k in range(4)}
    one = {k: band_avg(f, P[:, (idx + k) % 6, idx].T, (float(f[0]), float(f[-1]))) for k in (1, 2, 3)}
    out = {f"k{k}_band": float(db(bp[k]).std(ddof=1) / np.sqrt(6)) for k in range(4)}
    for a, b in ((3, 1), (2, 1), (3, 2)):
        out[f"R{a}{b}"] = float(db(one[a] / one[b]).std(ddof=1) / np.sqrt(6))
    Nabs = 1 - P.sum(1)                                                  # (F, 6) per driven antenna
    out["logN"] = float(db(band_avg(f, Nabs.T, (float(f[0]), float(f[-1])))).std(ddof=1) / np.sqrt(6))
    return out


def _parse(n):
    num, den = n.split(" / ")

    def pr(p):
        a, b = p.split("·")
        return frozenset([frozenset([a[:2], a[2:]]), frozenset([b[:2], b[2:]])])
    return pr(num), pr(den)


def chi_classes():
    """Cross-ratio name -> [(equivalent name, sign)] over the 12 symmetry relabelings of the ring.
    sign = -1 when the relabeled cross-ratio is the reciprocal of the listed one."""
    names = list(cross_ratios(np.ones((6, 6))).keys())
    parsed = {n: _parse(n) for n in names}
    lookup = {}
    for n, (a, b) in parsed.items():
        lookup[(a, b)] = (n, 1)
        lookup[(b, a)] = (n, -1)
    out = {}
    for n, (a, b) in parsed.items():
        mem = {}
        for t in symmetry_transforms():
            m = {ANT[i]: ANT[t[i]] for i in range(6)}
            ra = frozenset(frozenset(m[x] for x in pr) for pr in a)
            rb = frozenset(frozenset(m[x] for x in pr) for pr in b)
            hit = lookup.get((ra, rb))
            if hit:
                mem[hit[0]] = hit[1]
        out[n] = sorted(mem.items())
    return out


def verdict_ratio(x):
    return "holds" if x >= 3 else ("weakened" if x >= 2 else "retracted")


def boundaries(rule):
    """1-D LDA decision points (dB) between adjacent classes of the frozen staging rules."""
    out = {}
    for sch, st in rule["staging"].items():
        if len(st["features"]) != 1:
            continue
        w = np.ravel(st["coef"]) if np.ndim(st["coef"]) == 1 else np.asarray(st["coef"])[:, 0]
        b = np.asarray(st["intercept"])
        sc = float(np.ravel(st["scale"])[0])
        cls = st["classes"]
        x = np.linspace(-40, 40, 400001)
        lab = np.argmax(np.outer(x / sc, w) + b, 1)
        ch = np.flatnonzero(np.diff(lab))
        out[f"{sch} ({st['features'][0]})"] = ", ".join(f"{cls[lab[i]]}|{cls[lab[i + 1]]} at {x[i]:.2f}" for i in ch)
    return out


# ============================================================ predictions for LeftOnly_test
def predictions(dMild, BPdb, Xl, names, des, rule, bounds, floor_fb, floor_lr, CH, sd_chi, cnames):
    """LeftOnly = Mild with the right lobes (S5, S6) healthy. Derived only from Mild/Healthy_sliced.
    Model (linear superposition + locality): the Mild change of path (i, j) is split between the left
    (S2, S3 = T2, T3) and right (S5, S6 = T5, T6) lobes in proportion to how many of the path's two
    end antennas face an affected lobe on each side; paths whose ends face only unaffected lobes
    (T1, T4) and every mirror-self-symmetric path get exactly half (mirror symmetry + linearity).
    Baseline model for scoring: every path changes by half of Mild (no locality)."""
    left, right = {1, 2}, {4, 5}
    Lmap = np.zeros((6, 6))
    for i in range(6):
        for j in range(6):
            ends = [i, j] if i != j else [i]
            aL = sum(e in left for e in ends)
            aR = sum(e in right for e in ends)
            Lmap[i, j] = dMild[i, j] * (aL / (aL + aR) if aL + aR else 0.5)
    rows = []
    for i, j in itertools.combinations_with_replacement(range(6), 2):
        rows.append({"path": f"{ANT[i]}-{ANT[j]}" if i != j else f"{ANT[i]} refl.", "type": PATH[int(DIST[i, j])],
                     "Mild change dB": dMild[i, j], "predicted LeftOnly change dB (locality)": Lmap[i, j],
                     "no-locality baseline dB": dMild[i, j] / 2})
    pt = pd.DataFrame(rows)
    fb = float(index(Lmap, FB_PATHS))
    lr = float(index(Lmap, LR_PATHS))
    xm = Xl[des["Mild"]]
    xh = Xl[des["Normal"]]
    half = {r: xh[names.index(r)] + 0.5 * (xm[names.index(r)] - xh[names.index(r)]) for r in ("R31", "R21", "R32")}
    tau = rule["detection_binary_R31"]["tau_dB"]
    m = rule["detection_binary_R31"]["margin_dB"]
    r31 = half["R31"]
    det = "AD" if r31 < tau - m else ("Normal" if r31 > tau + m else "UNCERTAIN")
    return {"paths": pt, "fb": fb, "lr": lr, "ratios": half, "r31_label": det, "tau": tau, "margin": m,
            "bounds": bounds}


def write_predictions(p, gh, floor_fb, floor_lr, sig_path):
    pt = p["paths"]
    pt.to_csv(OUT / "predictions.csv", index=False)
    lr_sign = "positive" if p["lr"] > 0 else "negative"
    L = ["# Pre-registered predictions for LeftOnly_test (written before the file exists)", "",
         f"Code {gh}. Derived only from Healthy_sliced and Mild_lobe. LeftOnly_test = Mild_lobe with the right "
         "temporal (S6) and right parietal (S5) lobes reset to healthy; left temporal (S2), left parietal (S3) and the "
         "hippocampus as in Mild. Do not edit after LeftOnly_test arrives.", "",
         "## Model",
         "Linear superposition + locality: the Mild change of each path is split between the left lobes (facing T2, T3) "
         "and the right lobes (facing T5, T6) in proportion to how many of the path's end antennas face an affected lobe "
         "on each side. Paths whose ends face only unaffected lobes (T1, T4), and every path that maps to itself under "
         "the left-right mirror, get exactly half of the Mild change (mirror symmetry + linearity). Nonlinearity is "
         "ignored (the changes are not small), so sizes are rough. Baseline for scoring: every path changes by half "
         "of Mild (no locality).", "",
         "## Predictions",
         f"1. **Left-right index** (paths touching T2/T3 minus paths touching T5/T6): **{p['lr']:+.3f} dB**, sign "
         f"{lr_sign}, |value| = {abs(p['lr']) / floor_lr:.1f}x the noise floor ({floor_lr:.3f} dB, larger of healthy / "
         "staged-mirror floors). The no-locality baseline predicts 0. Both are clean-data statements: with ±0.5 dB "
         "per-port gain errors this index is not measurable (its gain-induced SD is ~0.4 dB).",
         f"2. **Front-back index**: {p['fb']:+.3f} dB (floor {floor_fb:.3f} dB), i.e. no front-back asymmetry beyond "
         "the floor.",
         "3. **Paths with both ends on the right** (T5-T6, T5 and T6 reflections) and paths from an unaffected antenna "
         "to a right antenna (T1-T6, T4-T5, T1-T5, T4-T6): change ~0 (within 2x the numerical noise of their path type: "
         + ", ".join(f"{PATH[k]} {2 * v:.2f} dB" for k, v in sig_path.items()) + ").",
         "4. **Paths with both ends on the left** (T2-T3, T2 and T3 reflections) and from an unaffected antenna to a "
         "left antenna (T1-T2, T3-T4, T1-T3, T2-T4): change ~ the full Mild change of that path (sign as in Mild).",
         f"5. **Ring-averaged ratios** ~ halfway between Healthy_sliced and Mild_lobe: R31 {p['ratios']['R31']:.2f}, "
         f"R21 {p['ratios']['R21']:.2f}, R32 {p['ratios']['R32']:.2f} dB.",
         f"6. **Frozen detection rule** (R31, tau {p['tau']:.2f} ± {p['margin']:.2f} dB): predicted R31 "
         f"{p['ratios']['R31']:.2f} dB -> mostly **{p['r31_label']}**. Frozen staging boundaries: "
         + "; ".join(f"{k}: {v}" for k, v in p["bounds"].items()) + ".",
         "",
         "## Scoring (fixed now)",
         "- Each path prediction (table below) is correct if the observed change has the predicted sign and "
         "|observed - predicted| <= max(0.5 |predicted|, 2x the numerical noise of that path type, column below); "
         "predictions of ~0 are correct if |observed| <= that 2x noise.",
         "- The locality model wins over the no-locality baseline if its rms error over all 21 paths is lower.",
         "- Prediction 1 holds if the left-right index has the predicted sign and |index| >= 3x the symmetry floor.",
         "- Predictions 5-6 hold if R31/R21/R32 lie within 0.3 dB of the predicted values and the frozen-rule label "
         "matches for >= 80% of noisy measurements.", "",
         "## Per-path predictions", md(pt, ".3f"), ""]
    (OUT / "predictions.md").write_text("\n".join(L), encoding="utf-8")


# ============================================================ helpers / figures
def md(df, fmt=".3g"):
    def cell(v):
        if isinstance(v, (float, np.floating)):
            return "n/a" if not np.isfinite(v) else format(v, fmt)
        return str(v).replace("\n", " ")
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    return "\n".join([head, sep] + ["| " + " | ".join(cell(v) for v in r) + " |" for r in df.itertuples(index=False)])


def fig_maps(dP, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    vmax = max(np.abs(M).max() for M in dP.values())
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.8))
    for a, (c, M) in zip(ax, dP.items()):
        im = a.imshow(M, cmap="RdBu_r", norm=TwoSlopeNorm(0, -vmax, vmax))
        for i in range(6):
            for j in range(6):
                a.text(j, i, f"{M[i, j]:+.2f}", ha="center", va="center", fontsize=7,
                       color="white" if abs(M[i, j]) > 0.6 * vmax else "#1f1e1c")
        a.set_xticks(range(6), LAB, fontsize=7)
        a.set_yticks(range(6), LAB, fontsize=7)
        a.set_title(f"{name[c]} minus healthy (dB)", loc="left", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.8, label="change in band-averaged power (dB)")
    fig.suptitle("Which antenna pairs change? Diagonal = reflection; one step off = neighbour; "
                 "two = second-neighbour; three = opposite", x=0.01, ha="left", fontsize=10)
    fig.savefig(FIG / "4a_path_change_maps.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_ratios(vt, rule, bounds):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    order = ["Normal", "MCI", "Mild", "Moderate", "Severe"]
    titles = {"R31": "Opposite ÷ neighbour power", "R21": "Second-neighbour ÷ neighbour power",
              "R32": "Opposite ÷ second-neighbour power"}
    sty = {"uniform v2": ("o", "#1c5cab", -0.15), "uniform v1": ("s", "#86b6ef", 0.0), "lobe": ("D", "#eb6834", 0.15)}
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
    for a, r in zip(ax, ("R31", "R21", "R32")):
        for sset, (mk, col, dx) in sty.items():
            sub = vt[vt.set == sset]
            a.plot([order.index(s) + dx for s in sub.stage], sub[r], mk, color=col, ms=7,
                   label={"lobe": "lobe sectors (new)", "uniform v2": "uniform (v2 solve)", "uniform v1": "uniform (v1 solve)"}[sset])
        if r == "R31":
            t = rule["detection_binary_R31"]
            a.axhspan(t["tau_dB"] - t["margin_dB"], t["tau_dB"] + t["margin_dB"], color="#e4e3de", zorder=0)
            a.axhline(t["tau_dB"], color="#5f5e59", lw=1, ls="--")
        for k, v in bounds.items():
            if f"({r})" in k:
                for part in v.split(", "):
                    a.axhline(float(part.split(" at ")[1]), color="#5f5e59", lw=0.8, ls=":")
        a.set_xticks(range(5), order)
        a.set_title(f"{titles[r]} (dB)", loc="left", fontsize=9)
        a.grid(True, color="#e4e3de", lw=0.5)
        a.spines[["top", "right"]].set_visible(False)
    ax[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Lobe-sector stages against the uniform-atrophy solves; dashed/dotted = frozen decision boundaries",
                 x=0.01, ha="left", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "3_ratios_lobe_vs_uniform.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
