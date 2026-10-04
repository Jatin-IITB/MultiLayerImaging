"""Adversarial review of the lobe results (questions A1-A9 of 2026-10-04), re-derived from the raw files.

    python scripts/10_lobe_review.py [--n 300]

Writes results/05_lobe/review/{report.md, A*.csv}. Reads (never writes) the committed predictions
(results/05_lobe/predictions.*), the frozen rule (results/04/frozen_rule.json) and the imaging session's frozen
inversion (results/imaging/lobe_frozen.json + its cached Born table); the imaging code is imported read-only to
evaluate its left-right operator.

Mirror test (A3/A4): a statistic T(S) that changes sign under the port mirror x -> -x (T2<->T6, T3<->T5) is
evaluated on each design alone (no reference file). True value 0 for every mirror-symmetric design, so the nine
mirror-symmetric designs (two healthy heads, six stages, MCI) give the empirical null of T (numerical asymmetry).
Rulers of T: null rms and max, one-pass yardstick (largest |T(pass n+1) - T(pass n)| over the four stages),
measurement-error spread (noisy draws of LeftOnly: noise only, ±0.5 dB gain, ±2 dB gain + ±10° phase).
One verdict bar everywhere: >= 3x the ruler.
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import itertools
import json
import pickle
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
from adstage.features.floor import floor_power, r31  # noqa: E402
from adstage.features.metrics import to_ring_order  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.noise.model import PROFILES  # noqa: E402
from adstage.noise.reference import mesh_pairs, mesh_sd  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.pipeline.classify import Threshold1D  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
L9 = _load("lobe09", "09_lobe_tests.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "review"
ANT, MIR, DIST = L7.ANT, L7.MIRROR, L7.DIST
LO, MCI = "LeftOnly_test_c3", "MCI_lobe_c3"
H7, H6 = L8.H7, L8.H6
SYM = [H7, H6, "Mild_lobe", "Mild_lobe_new", "Moderate_lobe", "Moderate_lobe_c3", "Severe_lobe", "Severe_lobe_c3", MCI]
CONDS = {"noise + setup, no calibration error": {}, "±0.5 dB gain": {"gain_err_db": 0.5},
         "±2 dB gain ±10° phase": {"gain_err_db": 2.0, "phase_err_deg": 10.0}}
MM = L7.mirror_map()
md = L7.md


def tier(x):
    return "robust (>= 3x)" if x >= 3 else ("sensitive (2-3x)" if x >= 2 else "not determined (< 2x)")


# ======================================================================== mirror-test statistics
def mirror(S):
    return S[..., MIR, :][..., MIR]


def sbar(S):
    return 0.5 * (S + np.swapaxes(S, -1, -2))


PAIR_LIST = [(i, j) for i in range(6) for j in range(i, 6)
             if (min(MIR[i], MIR[j]), max(MIR[i], MIR[j])) != (i, j) and (i, j) < (min(MIR[i], MIR[j]), max(MIR[i], MIR[j]))]


def pair_name(i, j):
    a = f"{ANT[i]}-{ANT[j]}" if i != j else f"{ANT[i]} refl."
    mi, mj = sorted((MIR[i], MIR[j]))
    b = f"{ANT[mi]}-{ANT[mj]}" if mi != mj else f"{ANT[mi]} refl."
    return f"{a} vs {b}"


IDX = {"all paths": L7.LR_PATHS, "neighbour paths": L7.restrict(L7.LR_PATHS, 1),
       "second-neighbour paths": L7.restrict(L7.LR_PATHS, 2)}


def complex_cr(Sb):
    """Complex cross-ratios S_ab S_cd / (S_ac S_bd) per frequency, same names and pairings as L7.cross_ratios."""
    out = {}
    for a, b, c, d in itertools.combinations(range(6), 4):
        prs = {f"{ANT[a]}{ANT[b]}·{ANT[c]}{ANT[d]}": Sb[..., a, b] * Sb[..., c, d],
               f"{ANT[a]}{ANT[c]}·{ANT[b]}{ANT[d]}": Sb[..., a, c] * Sb[..., b, d],
               f"{ANT[a]}{ANT[d]}·{ANT[b]}{ANT[c]}": Sb[..., a, d] * Sb[..., b, c]}
        ks = list(prs)
        for i, j in itertools.combinations(range(3), 2):
            out[f"{ks[i]} / {ks[j]}"] = prs[ks[i]] / prs[ks[j]]
    return out


def mirror_stats(f, S, noisy=False):
    """Reference-free left-right statistics of one design (S (F,6,6)) or of noisy draws (D (n,F,6,6)).
    Power: LR indices of the band powers (= half the index of S - mirror(S)), mirror path-pair differences,
    left-right power cross-ratios. Phase: LR index of mirror path-pair phase differences, left-right phase of
    the complex cross-ratios (invariant to per-port complex gains). dB / degrees."""
    D = S if noisy else S[None]
    bp = L7.band_power_noisy(f, D) if noisy else L7.band_power(f, D)
    bdb = L7.db(bp)
    q = {}
    for nm, paths in IDX.items():
        q[f"power LR index, {nm}"] = L7.index(bdb, paths)
    for i, j in PAIR_LIST:
        q[f"power pair {pair_name(i, j)}"] = bdb[:, i, j] - bdb[:, MIR[i], MIR[j]]
    for n, v in L9.lr_chi(L7.cross_ratios(bp)).items():
        q[f"power cross-ratio {n}"] = v
    Sb = sbar(D)
    for i, j in PAIR_LIST:
        q[f"phase pair {pair_name(i, j)}"] = np.degrees(np.angle(Sb[:, :, i, j]
                                                               * np.conj(Sb[:, :, MIR[i], MIR[j]]))).mean(1)
    for nm, (pa, _) in IDX.items():
        d = [np.degrees(np.angle(Sb[:, :, i, j] * np.conj(Sb[:, :, MIR[i], MIR[j]]))).mean(1) for i, j in pa]
        q[f"phase LR index, {nm}"] = np.mean(d, 0)
    cr = complex_cr(Sb)
    for n, (m, s) in MM.items():
        if (m == n and s == 1) or (m != n and m < n):
            continue
        z = cr[n] * (np.conj(cr[m]) if s == 1 else cr[m])
        q[f"phase cross-ratio {n}"] = np.degrees(np.angle(z)).mean(1)
    return q


def fam_of(k):
    for p in ("power LR index", "power pair", "power cross-ratio", "phase LR index", "phase pair", "phase cross-ratio"):
        if k.startswith(p):
            return p
    return k


# ======================================================================== imaging operator (read-only)
class Imaging:
    def __init__(self, f):
        from imaging import lobe_A as ILA
        from imaging import lobe_c3 as IC
        from imaging import lobe_rulers as ILR
        from imaging import run_lobe as IRL
        from imaging import study_lobe as SL
        from imaging.fields import FREQ_TAGS
        self.IC, self.SL = IC, SL
        P = pickle.loads((ROOT / "results/imaging/cache/lobe_v1-masked/born_table.pkl").read_bytes())
        fz = json.loads((ROOT / "results/imaging/lobe_frozen.json").read_text(encoding="utf-8"))
        self.kappa = np.array(fz["kappa_re"]) + 1j * np.array(fz["kappa_im"])
        self.lam = {"dS": fz["lambda_dS"], "log": fz["lambda_log"]}
        self.fh = np.array(list(FREQ_TAGS.values()), float)
        self.fi = np.array([int(np.argmin(np.abs(f - q))) for q in self.fh])
        self.K6 = SL.region_kernels(P, SL.region_masks())[..., :6]
        self.methods = {"Tikhonov dS (primary)": IRL.METHODS[0], "Tikhonov log (gain-inv.)": IRL.METHODS[2],
                        "whitened log (post-hoc)": ILR.WNAME}
        self._ILR, self._ILA = ILR, ILA
        self._M = {}

    def fx(self, Sref, method):
        key = (id(Sref), method)
        if key not in self._M:
            M = self._ILR.build_models(self.K6, self.fh, self.fi, self.kappa, Sref, self._ILA.KEEP_ALL)
            self._M[key] = self.IC.make_x(M, self.methods[method], self.lam)
        return self._M[key]

    def lr(self, S, Sref, method):
        return float(self.IC.qvec(self.fx(Sref, method)(S[self.fi], Sref[self.fi]))[6])

    def T(self, S, Sref, method):
        return 0.5 * (self.lr(S, Sref, method) - self.lr(mirror(S), Sref, method))


# ======================================================================== frozen-rule helpers
def rule_label(rule, scheme, x):
    """Frozen label of feature value(s) x for 'binary' (R31) or a staging scheme (1-D LDA + p*)."""
    x = np.atleast_1d(np.asarray(x, float))
    if scheme == "binary":
        d = rule["detection_binary_R31"]
        return np.where(x < d["tau_dB"] - d["margin_dB"], "AD", np.where(x > d["tau_dB"] + d["margin_dB"], "Normal",
                                                                         "UNCERTAIN"))
    st = rule["staging"][scheme]
    w = np.ravel(st["coef"]) if np.ndim(st["coef"]) == 1 else np.asarray(st["coef"])[:, 0]
    z = np.outer(x / float(np.ravel(st["scale"])[0]), w) + np.asarray(st["intercept"])
    p = np.exp(z - z.max(1, keepdims=True))
    p /= p.sum(1, keepdims=True)
    lab = np.array(st["classes"], dtype=object)[p.argmax(1)]
    return np.where(p.max(1) < float(rule["p_star_reject"]), "UNCERTAIN", lab)


def edge_margin(rule, scheme, x0, span=3.0, step=5e-4):
    """Signed distance from x0 to the nearest feature value where the frozen label changes."""
    lab0 = rule_label(rule, scheme, x0)[0]
    g = x0 + np.arange(-span, span + step / 2, step)
    lab = rule_label(rule, scheme, g)
    ch = np.flatnonzero(lab != lab0)
    if not ch.size:
        return lab0, np.inf
    j = ch[np.argmin(np.abs(g[ch] - x0))]
    return lab0, float(g[j] - x0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    cfg = load_config(ROOT, "config_lobe.yaml")
    gh = git_hash(ROOT)
    f, Sd, man, _ = L8.load_all(cfg)
    rule = json.loads((ROOT / "results/04/frozen_rule.json").read_text())
    tau, m_det = rule["detection_binary_R31"]["tau_dB"], rule["detection_binary_R31"]["margin_dB"]
    R = L8.rulers(f, Sd, cfg, args.n, qfn=L9.ext_quantities)
    Q = R["Q"]
    g = lambda d, k: float(Q[d][k][0])                       # noqa: E731
    pred = pd.read_csv(LOBE / "predictions.csv")
    L = [f"# Adversarial review of the lobe results, A1-A9 (code {gh})", "",
         "Every number below is recomputed from the raw files by `scripts/10_lobe_review.py`; nothing is copied from "
         "earlier reports. One verdict bar everywhere: >= 3x the stated ruler. One solve per design: "
         "within-simulation noise robustness, not generalisation.", ""]
    summary = []

    # ------------------------------------------------------------------ A9 first (A1, A8 need the boundary SDs)
    cfg_u = load_config(ROOT, "config_repeats.yaml")
    du = load_dataset(cfg_u, ROOT)
    fu = du.f_hz
    Su = to_ring_order(du.S, du.port_to_ant)
    ccfg = cfg_u["classify"]
    pi = list(PROFILES).index("typical")
    hv = {}
    for s in range(len(du.classes)):
        vals = []
        for split, off in (("train", 0), ("test", 1)):
            rng = np.random.default_rng([cfg_u["seed"], 3, pi, s, off])
            D = draws(fu, Su[s], PROFILES["typical"], int(ccfg[f"n_{split}_draws"]), rng, dict(cfg_u.get("augment", {})))
            vals.append(r31(fu, D, floor_power(D), (float(fu[0]), float(fu[-1]))))
        hv[s] = np.concatenate(vals)
    groups = {"Normal": [s for s, c in enumerate(du.classes) if c == "Normal"],
              "AD": [s for s, c in enumerate(du.classes) if c in ("Mild", "Moderate", "Severe")]}
    T03 = _load("cls03", "03_classify.py")
    pairs = mesh_pairs(du.files, du.manifest)
    vals_db = np.array([10 * np.log10(np.mean(hv[s])) for s in range(len(du.classes))])
    t03 = T03.thresholds(hv, groups, float(ccfg["p_star"]), float(ccfg["screening_prior_normal"]), int(ccfg["n_boot"]),
                         cfg_u["seed"], mesh_sd(vals_db, pairs))
    db = {s: 10 * np.log10(v) for s, v in hv.items()}

    def tau_of(nsel, asel):
        xn = np.concatenate([db[s] for s in nsel])
        xa = np.concatenate([db[s] for s in asel])
        t = Threshold1D().fit(np.r_[xn, xa][:, None], np.r_[np.zeros(len(xn)), np.ones(len(xa))])
        return float(t.tau_)
    rng = np.random.default_rng([cfg_u["seed"], 99])
    tb = np.array([tau_of(rng.choice(groups["Normal"], len(groups["Normal"])), rng.choice(groups["AD"], len(groups["AD"])))
                   for _ in range(4000)])
    loo = [{"left out": Path(str(du.files[s])).name, "class": du.classes[s],
            "tau dB": tau_of([x for x in groups["Normal"] if x != s] or groups["Normal"],
                             [x for x in groups["AD"] if x != s] or groups["AD"])} for s in groups["Normal"] + groups["AD"]]
    sd_tau = float(tb.std(ddof=1))
    # staging boundaries: 1-D LDA with equal priors = midpoint of the class means; bootstrap over solves
    Xu, nmu, _, _ = features(fu, Su)
    val = lambda s, k: float(Xu[s][nmu.index(k)])            # noqa: E731
    bdefs = {"three (R21)": ("R21", [("Normal", ["Normal"]), ("Mild", ["Mild"]), ("Severe", ["Severe"])]),
             "three_merged (R32)": ("R32", [("Normal", ["Normal"]), ("Mild+Moderate", ["Mild", "Moderate"]),
                                            ("Severe", ["Severe"])])}
    frozen_b = {k: [float(p.split(" at ")[1]) for p in v.split(", ")] for k, v in L7.boundaries(rule).items()}
    brow, bsd = [], {}
    for key, (feat, cls) in bdefs.items():
        sols = [[s for s, c in enumerate(du.classes) if c in members] for _, members in cls]
        mu = [np.mean([val(s, feat) for s in ss]) for ss in sols]
        mids = sorted(0.5 * (mu[i] + mu[i + 1]) for i in range(len(mu) - 1))
        bs = []
        for _ in range(4000):
            mub = [np.mean([val(s, feat) for s in rng.choice(ss, len(ss))]) for ss in sols]
            bs.append(sorted(0.5 * (mub[i] + mub[i + 1]) for i in range(len(mub) - 1)))
        bs = np.array(bs)
        for i, (fb, mb) in enumerate(zip(sorted(frozen_b[key]), mids)):
            bsd[(key, i)] = float(bs[:, i].std(ddof=1))
            brow.append({"rule": key, "boundary": i + 1, "frozen dB": fb, "re-derived midpoint dB": mb,
                         "bootstrap SD dB": bsd[(key, i)], "2.5% dB": float(np.quantile(bs[:, i], 0.025)),
                         "97.5% dB": float(np.quantile(bs[:, i], 0.975))})
    bt = pd.DataFrame(brow)
    tauq = pd.DataFrame([{"quantity": "tau (frozen)", "dB": tau},
                         {"quantity": "tau re-derived (03 code, same seeds)", "dB": t03["tau_dB"]},
                         {"quantity": "03 bootstrap CI (solves + draws), 2.5%", "dB": t03["tau_CI_lo"]},
                         {"quantity": "03 bootstrap CI (solves + draws), 97.5%", "dB": t03["tau_CI_hi"]},
                         {"quantity": "solve-only bootstrap SD", "dB": sd_tau},
                         {"quantity": "solve-only bootstrap 2.5%", "dB": float(np.quantile(tb, 0.025))},
                         {"quantity": "solve-only bootstrap 97.5%", "dB": float(np.quantile(tb, 0.975))}])
    flips = []
    for d in (LO, "Severe_lobe", "Severe_lobe_c3", "Mild_lobe", "Mild_lobe_new", "Moderate_lobe", "Moderate_lobe_c3",
              H6, H7, MCI):
        x = g(d, "R31")
        lab0 = rule_label(rule, "binary", x)[0]
        labs = np.where(x < tb - m_det, "AD", np.where(x > tb + m_det, "Normal", "UNCERTAIN"))
        flips.append({"design": d, "R31 dB": x, "frozen label": lab0, "distance to tau dB": x - tau,
                      "distance to label edge dB": edge_margin(rule, "binary", x)[1],
                      "P(label differs | solve bootstrap of tau)": float((labs != lab0).mean())})
    ft = pd.DataFrame(flips)
    pd.concat([tauq, bt, ft], axis=0).to_csv(OUT / "A9_boundaries.csv", index=False)
    pd.DataFrame(loo).to_csv(OUT / "A9_tau_leave_one_solve_out.csv", index=False)
    L += ["## A9. Uncertainty of the frozen boundaries",
          f"tau is re-derived with the 03 code and the same seeds (config_repeats.yaml, typical profile, 2 Normal + 6 AD "
          f"solves): **{t03['tau_dB']:.4f} dB** vs frozen {tau:.4f} dB. 03's own CI (bootstrap over solves within class, "
          f"then draws): {t03['tau_CI_lo']:.3f} to {t03['tau_CI_hi']:.3f} dB. Solve-only bootstrap (4000x): SD "
          f"**{sd_tau:.3f} dB**, 95% {np.quantile(tb, 0.025):.3f} to {np.quantile(tb, 0.975):.3f} dB. tau is the "
          "midpoint between the closest draws of the two classes, so it is set by v2 Normal and the two Severe solves:",
          md(pd.DataFrame(loo), ".3f"), "",
          "Staging boundaries (1-D LDA with equal priors = midpoint of class means; re-derived from the solves and "
          "bootstrapped over solves within class):", md(bt, ".3f"), "",
          "Labels against the tau bootstrap (frozen margin m kept):", md(ft, ".3f"), ""]
    lo_flip = float(ft.set_index("design").loc[LO, "P(label differs | solve bootstrap of tau)"])
    sv_flip = ft.set_index("design").loc[["Severe_lobe", "Severe_lobe_c3"], "P(label differs | solve bootstrap of tau)"]
    summary.append({"question": "A9 tau uncertainty", "verdict": "CHANGED (new number)",
                    "old -> new": f"not reported -> tau SD {sd_tau:.3f} dB (solve bootstrap), 95% CI width "
                                  f"{np.quantile(tb, 0.975) - np.quantile(tb, 0.025):.2f} dB; P(label changes): LeftOnly "
                                  f"{lo_flip:.2f}, Severe_lobe {sv_flip.iloc[0]:.2f}, Severe_lobe_c3 {sv_flip.iloc[1]:.2f}",
                    "evidence": "results/05_lobe/review/A9_boundaries.csv"})

    # ------------------------------------------------------------------ A1 one bar for every frozen-rule label
    yard = {"binary": R["yard"]["R31"], "three": R["yard"]["R21"], "three_merged": R["yard"]["R32"]}
    feat = {"binary": "R31", "three": "R21", "three_merged": "R32"}
    a1 = []
    sets = {"lobe_A": [H6, "Mild_lobe", "Moderate_lobe", "Severe_lobe"],
            "lobe_B": [H7, "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3"], "tests": [LO, MCI]}
    for sname, ds_ in sets.items():
        for d in ds_:
            for sch in ("binary", "three", "three_merged"):
                x = g(d, feat[sch])
                lab, mg = edge_margin(rule, sch, x)
                if sch == "binary":
                    sb = sd_tau
                else:
                    key = "three (R21)" if sch == "three" else "three_merged (R32)"
                    nb = sorted(frozen_b[key])
                    sb = bsd[(key, int(np.argmin([abs(x - b) for b in nb])))]
                ruler = max(yard[sch], sb)
                a1.append({"set": sname, "design": d, "rule": sch, "feature dB": x, "frozen label": lab,
                           "distance to label edge dB": mg, "feature yardstick dB": yard[sch],
                           "boundary bootstrap SD dB": sb, "/ yardstick": abs(mg) / yard[sch],
                           "/ boundary SD": abs(mg) / sb, "/ max(yardstick, boundary SD)": abs(mg) / ruler,
                           "verdict (one bar)": tier(abs(mg) / ruler)})
    a1t = pd.DataFrame(a1)
    a1t.to_csv(OUT / "A1_one_bar.csv", index=False)
    old = subprocess.run(["git", "show", "aff9d56:scripts/08_lobe_mesh.py"], cwd=ROOT, capture_output=True,
                         text=True).stdout
    bars = [ln.strip() for ln in old.splitlines() if ("c >= 3" in ln or "mv >= 3" in ln or "mv >= 2" in ln
                                                         or "c >= 2" in ln)]
    L += ["## A1. One bar for every label",
          "The detection and localisation tiers come from the same commit, aff9d56 (before the c3 files existed); "
          "they are numerically the same (>= 3x unqualified, 2-3x 'mesh-sensitive', < 2x 'not separable'):",
          "```", *bars, "```",
          "The inconsistency was the word 'holds' put in front of a sub-3x detection margin, and margins measured to "
          "tau instead of to the label edge (tau - m for AD). Below, every frozen-rule label of every lobe design, "
          "with the margin to the nearest point where the label changes, against max(feature yardstick, bootstrap SD "
          "of that boundary):", md(a1t, ".3f"), ""]
    nd = a1t[a1t["/ max(yardstick, boundary SD)"] < 3]
    summary.append({"question": "A1 one bar", "verdict": "CHANGED (labels); the bar itself was one bar (aff9d56)",
                    "old -> new": "'holds' for sub-3x detection margins -> " + "; ".join(
                        f"{r.design} {r.rule} {r['/ max(yardstick, boundary SD)']:.1f}x ({r['verdict (one bar)']})"
                        for _, r in nd.iterrows()),
                    "evidence": "results/05_lobe/review/A1_one_bar.csv"})

    # ------------------------------------------------------------------ A2 power of the registered tests
    log = lambda c: subprocess.run(["git", "log", "-1", "--format=%h %ad", "--date=iso", c], cwd=ROOT,   # noqa: E731
                                   capture_output=True, text=True).stdout.strip()
    old_ix = pd.read_csv(io.StringIO(subprocess.run(
        ["git", "show", "cf56de8:results/05_lobe/4b_indices.csv"], cwd=ROOT, capture_output=True, text=True).stdout))
    hrow = old_ix[(old_ix.design == "Healthy_sliced") & (old_ix["index"] == "left-right, all paths")].iloc[0]
    sig1 = float(np.hypot(hrow["staged mirror floor dB"], hrow["healthy floor dB"]))
    from scipy.stats import norm
    p_lr = 0.232
    power1 = float(norm.sf((3 * 0.071 - p_lr) / sig1))
    A_loc = L9.lr_chi(L7.cross_ratios(10 ** (L9.mat_from(pred, "predicted LeftOnly change dB (locality)") / 10)))
    v1st = ["Mild_lobe", "Moderate_lobe", "Severe_lobe"]
    lrk = [k for k in Q[H6] if k.startswith("lr chi ")]
    fl_v1 = float(np.sqrt(2) * np.sqrt(np.mean([g(d, k) ** 2 for d in v1st for k in lrk])))
    fl_now = float(R["fam_floor"]["left-right cross-ratio"] * np.sqrt(2))
    a2 = pd.DataFrame([
        {"item": "cf56de8 committed (predictions)", "value": log("cf56de8")},
        {"item": "08a9a53 committed (left-right cross-ratio test and its floor)", "value": log("08a9a53")},
        {"item": "LR-index floor of a difference known at cf56de8 (staged 0.071 (+) healthy, dB)", "value": f"{sig1:.3f}"},
        {"item": "prediction 1: P(rule passes | locality model exactly right)", "value": f"{power1:.2f}"},
        {"item": "left-right cross-ratio floor of a difference from the lobe_v1 stages only (dB)", "value": f"{fl_v1:.3f}"},
        {"item": "same floor as used at scoring (six stages incl. c3, dB)", "value": f"{fl_now:.3f}"},
        {"item": "largest predicted left-right cross-ratio (from cf56de8 paths, dB)",
         "value": f"{max(abs(v) for v in A_loc.values()):.3f}"},
        {"item": "largest predicted / lobe_v1-era floor", "value": f"{max(abs(v) for v in A_loc.values()) / fl_v1:.2f}"}])
    a2.to_csv(OUT / "A2_power.csv", index=False)
    L += ["## A2. Could the registered tests pass?",
          "The ~0.43 dB clean ruler of the left-right cross-ratios is max(one-pass yardstick, symmetry floor); its "
          "floor part is sqrt2 x the rms of the left-right cross-ratios of the mirror-symmetric stages (a per-band, "
          "band-averaged 3.2-4.2 GHz power quantity). The test and its floor were added in 08a9a53, after cf56de8, "
          "but the same floor can be computed from the lobe_v1 stages that existed before cf56de8:", md(a2), "",
          "So both registered left-right tests were under-powered by design: prediction 1's pass threshold (3 x 0.071 "
          "= 0.213 dB) sat 8% below its own predicted value (0.232 dB), and no predicted power cross-ratio reached 3x "
          "a floor computable before registration. That is a design flaw of the registration (mine), knowable at "
          "cf56de8; no power check was run.", ""]
    summary.append({"question": "A2 test designed to fail?", "verdict": "CHANGED (design flaw stated)",
                    "old -> new": f"'could not succeed' -> under-powered by design and knowable before cf56de8: "
                                  f"P(pred. 1 passes | model right) = {power1:.2f}; predicted cross-ratios <= "
                                  f"{max(abs(v) for v in A_loc.values()) / fl_v1:.1f}x the lobe_v1-era floor "
                                  f"({fl_v1:.2f} dB)",
                    "evidence": "results/05_lobe/review/A2_power.csv"})

    # ------------------------------------------------------------------ A3 mirror test
    MS = {d: mirror_stats(f, Sd[d]) for d in SYM + [LO]}
    keys = list(MS[LO])
    rowsA3 = []
    spreads = {}
    for ci, (cname, extra) in enumerate(CONDS.items()):
        D = draws(f, Sd[LO], PROFILES["typical"], args.n, np.random.default_rng([cfg["seed"], 101, ci]),
                  {**cfg.get("augment", {}), **extra})
        qn = mirror_stats(f, D, noisy=True)
        spreads[cname] = {k: float(np.std(qn[k], ddof=1)) for k in keys}
    for k in keys:
        null = np.array([float(MS[d][k][0]) for d in SYM])
        yd = max(abs(float(MS[b][k][0] - MS[a][k][0])) for a, b in L8.PAIRS.values())
        lo = float(MS[LO][k][0])
        rms = float(np.sqrt(np.mean(null ** 2)))
        clean = max(rms, yd)
        meas = max(clean, spreads["±0.5 dB gain"][k])
        rowsA3.append({"statistic": k, "family": fam_of(k), "LeftOnly": lo, "null mean": float(null.mean()),
                       "null rms": rms, "null max |.|": float(np.abs(null).max()), "one-pass yardstick": yd,
                       **{f"spread {c}": spreads[c][k] for c in CONDS},
                       "/ null rms": abs(lo) / rms, "/ null max": abs(lo) / float(np.abs(null).max()),
                       "/ clean ruler": abs(lo) / clean, "/ measured ruler (±0.5 dB)": abs(lo) / meas,
                       "/ measured ruler (±2 dB ±10°)": abs(lo) / max(clean, spreads["±2 dB gain ±10° phase"][k])})
    a3 = pd.DataFrame(rowsA3)
    a3.to_csv(OUT / "A3_mirror_test.csv", index=False)
    fam3 = a3.groupby("family").agg(n=("statistic", "size"),
                                    clean=("/ clean ruler", lambda v: int((v >= 3).sum())),
                                    meas=("/ measured ruler (±0.5 dB)", lambda v: int((v >= 3).sum())),
                                    meas2=("/ measured ruler (±2 dB ±10°)", lambda v: int((v >= 3).sum())),
                                    beyond_max=("/ null max", lambda v: int((v > 1).sum())),
                                    best=("/ clean ruler", "max")).reset_index()
    fam3.columns = ["family", "n", ">= 3x clean ruler", ">= 3x measured (±0.5 dB)", ">= 3x measured (±2 dB ±10°)",
                    "beyond null max", "best / clean ruler"]
    ident = pd.DataFrame([{"reference": r, "index(LO) - index(ref)": g(LO, "index: left-right, all paths")
                           - g(r, "index: left-right, all paths"),
                           "index(LO - mirror LO) / 2": float(MS[LO]["power LR index, all paths"][0]),
                           "index(ref - mirror ref) / 2": float(MS[r]["power LR index, all paths"][0])} for r in (H7, H6)])
    top3 = a3.sort_values("/ clean ruler", ascending=False).head(12)
    L += ["## A3. Mirror test (reference-free)",
          "For the band-power LR index the mirror test is algebraically the earlier index: index(S - mirror(S)) = "
          "2 index(S), and index(LO) - index(ref) is what was reported. Numerically:", md(ident, ".4f"), "",
          f"Null = the nine mirror-symmetric designs ({', '.join(SYM)}). Per family, how many LeftOnly statistics exceed "
          "3x the clean ruler (max(null rms, one-pass yardstick)), 3x the measured rulers, and the largest null value:",
          md(fam3, ".2f"), "", "Largest (by clean ruler):",
          md(top3[["statistic", "LeftOnly", "null rms", "null max |.|", "one-pass yardstick", "spread ±0.5 dB gain",
                   "spread ±2 dB gain ±10° phase", "/ clean ruler", "/ measured ruler (±0.5 dB)",
                   "/ measured ruler (±2 dB ±10°)"]], ".2f"), ""]
    pw = fam3[fam3.family.str.startswith("power")]
    ph = fam3[fam3.family == "phase cross-ratio"].iloc[0]
    pp = fam3[fam3.family == "phase pair"].iloc[0]
    pwr = a3[a3.family.str.startswith("power") & (a3["/ clean ruler"] >= 3)]
    summary.append({"question": "A3 mirror test", "verdict": "CONFIRMED for the power indices; CHANGED overall",
                    "old -> new": f"'no left-right difference beyond the rulers' -> band power: "
                                  f"{len(pwr)}/{int(pw.n.sum())} statistics >= 3x clean ({', '.join(pwr.statistic.str.replace('power pair ', ''))}; "
                                  f"measured <= {a3[a3.family.str.startswith('power')]['/ measured ruler (±0.5 dB)'].max():.1f}x); phase pairs "
                                  f"{int(pp['>= 3x clean ruler'])}/{int(pp.n)}; but "
                                  f"{int(ph['>= 3x clean ruler'])}/{int(ph.n)} phase cross-ratios >= 3x the clean ruler "
                                  f"({int(ph['beyond null max'])} beyond every symmetric design; "
                                  f"{int(ph['>= 3x measured (±2 dB ±10°)'])} still >= 3x with ±2 dB/±10° errors)",
                    "evidence": "results/05_lobe/review/A3_mirror_test.csv"})

    # ------------------------------------------------------------------ A4 the imaging operator, read-only
    IM = Imaging(f)
    Simg = {}
    for d in SYM + [LO]:
        Simg[d], _ = IM.SL.load_design(d, f)
    same = max(float(np.max(np.abs(Simg[d] - Sd[d]))) for d in SYM + [LO])
    rowsA4 = []
    for mth in IM.methods:
        for rn, ref in (("Healthy_sliced (7 passes)", H7), ("Healthy_sliced_new (6 passes)", H6)):
            Sr = Simg[ref]
            lr_lo = IM.lr(Simg[LO], Sr, mth)
            mag = IM.lr(np.abs(Simg[LO]) * np.exp(1j * np.angle(Sr)), Sr, mth)
            pha = IM.lr(np.abs(Sr) * np.exp(1j * np.angle(Simg[LO])), Sr, mth)
            Tn = np.array([IM.T(Simg[d], Sr, mth) for d in SYM])
            Tlo = IM.T(Simg[LO], Sr, mth)
            yd = max(abs(IM.T(Simg[b], Sr, mth) - IM.T(Simg[a], Sr, mth)) for a, b in L8.PAIRS.values())
            sp = {}
            for ci, (cname, extra) in enumerate(CONDS.items()):
                D = draws(f, Sd[LO], PROFILES["typical"], max(args.n // 3, 60),
                          np.random.default_rng([cfg["seed"], 102, ci]), {**cfg.get("augment", {}), **extra})
                sp[cname] = float(np.std([IM.T(Dk, Sr, mth) for Dk in D], ddof=1))
            rms = float(np.sqrt(np.mean(Tn ** 2)))
            clean = max(rms, yd)
            rowsA4.append({"method": mth, "reference": rn, "LR (stage - ref)": lr_lo, "LR magnitude part": mag,
                           "LR phase part": pha, "mirror-test T(LeftOnly)": Tlo, "null T mean": float(Tn.mean()),
                           "null T rms": rms, "null T max |.|": float(np.abs(Tn).max()), "one-pass yardstick": yd,
                           **{f"spread {c}": v for c, v in sp.items()}, "T / null rms": abs(Tlo) / rms,
                           "T / null max": abs(Tlo) / float(np.abs(Tn).max()), "T / clean ruler": abs(Tlo) / clean,
                           "T / measured ruler (±0.5 dB)": abs(Tlo) / max(clean, sp["±0.5 dB gain"]),
                           "T / measured ruler (±2 dB ±10°)": abs(Tlo) / max(clean, sp["±2 dB gain ±10° phase"])})
    a4 = pd.DataFrame(rowsA4)
    a4.to_csv(OUT / "A4_imaging_operator.csv", index=False)
    split = []
    S6r = Simg[H6]
    for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe", MCI, LO):
        X = Simg[d]
        split.append({"design (vs Healthy_sliced_new)": d, "LR full": IM.lr(X, S6r, "Tikhonov dS (primary)"),
                      "magnitude part": IM.lr(np.abs(X) * np.exp(1j * np.angle(S6r)), S6r, "Tikhonov dS (primary)"),
                      "phase part": IM.lr(np.abs(S6r) * np.exp(1j * np.angle(X)), S6r, "Tikhonov dS (primary)")})
    st4 = pd.DataFrame(split)
    st4.to_csv(OUT / "A4_magnitude_phase_split.csv", index=False)
    prim = a4[(a4.method == "Tikhonov dS (primary)") & (a4.reference.str.startswith("Healthy_sliced_new"))].iloc[0]
    L += ["## A4. The imaging left-right estimate, evaluated with these rulers",
          f"The imaging operator is rebuilt read-only (cached Born table, frozen kappa and lambda; max |S| difference "
          f"between its loader and this pipeline {same:.1e}). LR = mean(S2, S3) - mean(S5, S6) of the recovered "
          "sector d eps''; it is linear in the complex dS at 3.4/3.6/3.8 GHz. T = (LR(S) - LR(mirror S))/2 is its "
          "mirror test.", md(a4, ".2f"), "", "Where the LR comes from (Tikhonov dS; stage minus Healthy_sliced_new):",
          md(st4, ".2f"), "",
          "The band-power indices (A3) are blind to it because the left-right signal is mostly in phase: LeftOnly's "
          f"LR {prim['LR (stage - ref)']:+.2f} = magnitude {prim['LR magnitude part']:+.2f} + phase "
          f"{prim['LR phase part']:+.2f} (first order). The inversion does not manufacture it: the mirror test puts "
          f"LeftOnly at {prim['T / null rms']:.1f}x the null rms and {prim['T / null max']:.1f}x the largest symmetric "
          "design, consistent with the independent phase cross-ratios of A3.", ""]
    summary.append({"question": "A4 imaging gets the sign", "verdict": "CHANGED: my indices discard the information",
                    "old -> new": f"'no left-right difference' -> the inversion's LR is {prim['T / null rms']:.1f}x the "
                                  f"mirror null rms ({prim['T / null max']:.1f}x its max) and "
                                  f"{100 * prim['LR phase part'] / prim['LR (stage - ref)']:.0f}% phase; with measurement "
                                  f"errors {prim['T / measured ruler (±0.5 dB)']:.1f}x (±0.5 dB), "
                                  f"{prim['T / measured ruler (±2 dB ±10°)']:.1f}x (±2 dB ±10°) for the primary method",
                    "evidence": "results/05_lobe/review/A4_imaging_operator.csv"})

    # ------------------------------------------------------------------ A5 rms comparison with uncertainty
    frac = np.where(np.abs(pred["Mild change dB"]) > 1e-12,
                    pred["predicted LeftOnly change dB (locality)"] / pred["Mild change dB"].where(
                        np.abs(pred["Mild change dB"]) > 1e-12, 1.0), 0.0)
    keysP = ["path " + p for p in pred.path]
    sig = np.array([max(R["yard"][k], R["fdiff"][k]) for k in keysP])
    mild = pred["Mild change dB"].to_numpy()
    a5 = []
    rng5 = np.random.default_rng([cfg["seed"], 105])
    for rn, ref in (("Healthy_sliced (7 passes, primary)", H7), ("Healthy_sliced_new (6 passes, matched)", H6)):
        obs = np.array([g(LO, k) - g(ref, k) for k in keysP])

        def drms(o, mc):
            loc, base = frac * mc, 0.5 * mc
            return float(np.sqrt(np.mean((o - loc) ** 2)) - np.sqrt(np.mean((o - base) ** 2)))
        d0 = drms(obs, mild)
        dist = np.array([drms(obs + rng5.normal(0, sig), mild + rng5.normal(0, sig)) for _ in range(20000)])
        boot = []
        for _ in range(20000):
            ii = rng5.integers(0, len(obs), len(obs))
            boot.append(np.sqrt(np.mean((obs[ii] - (frac * mild)[ii]) ** 2)) - np.sqrt(np.mean((obs[ii] - 0.5 * mild[ii]) ** 2)))
        boot = np.array(boot)
        a5.append({"reference": rn, "rms(locality) - rms(baseline) dB": d0,
                   "ruler perturbation 2.5%": float(np.quantile(dist, 0.025)),
                   "ruler perturbation 97.5%": float(np.quantile(dist, 0.975)),
                   "P(locality wins) under rulers": float((dist < 0).mean()),
                   "path bootstrap 2.5%": float(np.quantile(boot, 0.025)),
                   "path bootstrap 97.5%": float(np.quantile(boot, 0.975)),
                   "verdict": ("baseline preferred beyond the rulers" if np.quantile(dist, 0.025) > 0 else
                               "locality preferred beyond the rulers" if np.quantile(dist, 0.975) < 0 else
                               "no preference (interval contains 0)")})
    a5t = pd.DataFrame(a5)
    a5t.to_csv(OUT / "A5_locality_vs_baseline.csv", index=False)
    L += ["## A5. Locality vs no-locality, with uncertainty",
          "Both the observed LeftOnly changes and the Mild changes the predictions were built from carry numerical "
          "error; each path is perturbed by N(0, clean ruler) (max(one-pass yardstick, symmetry floor) of that path), "
          "both models are rebuilt from the perturbed Mild change with the committed rules, and the rms difference is "
          "recomputed (20000x). A bootstrap over the 21 paths is shown alongside.", md(a5t, ".3f"), ""]
    summary.append({"question": "A5 locality loses?", "verdict": "CHANGED",
                    "old -> new": "miss -> " + "; ".join(
                        f"{r.reference.split(' (')[0]}: {r['rms(locality) - rms(baseline) dB']:+.3f} dB "
                        f"[{r['ruler perturbation 2.5%']:+.3f}, {r['ruler perturbation 97.5%']:+.3f}], P(locality wins) "
                        f"{r['P(locality wins) under rulers']:.2f}: {r.verdict}" for _, r in a5t.iterrows()),
                    "evidence": "results/05_lobe/review/A5_locality_vs_baseline.csv"})

    # ------------------------------------------------------------------ A6 mechanism: per path class and side
    side = {}
    for p in pred.path:
        side[p] = ("left" if p in L9.LEFT else "right" if p in L9.RIGHT else
                   "cross (left-right)" if p in ("T2-T5", "T2-T6", "T3-T5", "T3-T6") else "self-mirror")
    a6 = []
    for rn, ref, mref in (("rule 1 (LeftOnly, Mild_lobe vs Healthy_sliced_new)", H6, "Mild_lobe"),
                          ("as predicted (vs Healthy_sliced)", H7, "Mild_lobe")):
        for p, k in zip(pred.path, keysP):
            dlo, dmi = g(LO, k) - g(ref, k), g(mref, k) - g(ref, k)
            s_ = max(R["yard"][k], R["fdiff"][k])
            pi_, pj_ = pth(p)

            def ph(d, pi_=pi_, pj_=pj_, ref=ref):
                return float(np.degrees(np.angle(sbar(Sd[d])[:, pi_, pj_] * np.conj(sbar(Sd[ref])[:, pi_, pj_]))).mean())
            a6.append({"comparison": rn, "path": p, "type": L7.PATH[int(DIST[pth(p)])], "side": side[p],
                       "LeftOnly change dB": dlo, "Mild change dB": dmi, "clean ruler dB": s_,
                       "Mild change / ruler": abs(dmi) / s_,
                       "ratio LeftOnly / Mild": dlo / dmi if abs(dmi) >= 2 * s_ else np.nan,
                       "ratio SD": np.hypot(s_ / dmi, (dlo / dmi) * s_ / dmi) if abs(dmi) >= 2 * s_ else np.nan,
                       "LeftOnly phase change deg": ph(LO), "Mild phase change deg": ph(mref)})
    a6t = pd.DataFrame(a6)

    def ph_change(a, b, i, j):
        return float(np.degrees(np.angle(sbar(Sd[b])[:, i, j] * np.conj(sbar(Sd[a])[:, i, j]))).mean())
    staged = ["Mild_lobe", "Moderate_lobe", "Severe_lobe", "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3"]
    pyard, pfloor = {}, {}
    for p in pred.path:
        i, j = pth(p)
        pyard[p] = max(abs(ph_change(a, b, i, j)) for a, b in L8.PAIRS.values())
        if (MIR[i], MIR[j]) != (i, j) and (MIR[j], MIR[i]) != (i, j):
            pfloor[p] = float(np.sqrt(np.mean([float(np.degrees(np.angle(sbar(Sd[d])[:, i, j] * np.conj(
                sbar(Sd[d])[:, MIR[i], MIR[j]]))).mean()) ** 2 for d in staged])))
    fam_pf = {t: float(np.sqrt(np.mean([v ** 2 for q_, v in pfloor.items() if DIST[pth(q_)] == t] or [0.0])))
              for t in range(4)}
    a6t["phase clean ruler deg"] = [max(pyard[p], pfloor.get(p, fam_pf[int(DIST[pth(p)])])) for p in a6t.path]
    a6t["LeftOnly phase / ruler"] = np.abs(a6t["LeftOnly phase change deg"]) / a6t["phase clean ruler deg"]
    a6t.to_csv(OUT / "A6_paths.csv", index=False)
    grp = []
    for (cmpn, ty, sd_), sub in a6t.groupby(["comparison", "type", "side"]):
        ok = sub.dropna(subset=["ratio LeftOnly / Mild"])
        if len(ok):
            w = 1 / ok["ratio SD"] ** 2
            mu = float(np.sum(w * ok["ratio LeftOnly / Mild"]) / w.sum())
            se = float(np.sqrt(1 / w.sum()))
        else:
            mu = se = np.nan
        grp.append({"comparison": cmpn, "type": ty, "side": sd_, "paths": len(sub), "usable (Mild >= 2x ruler)": len(ok),
                    "weighted ratio LeftOnly/Mild": mu, "SE": se,
                    "locality predicts": {"left": 1.0, "right": 0.0}.get(sd_, 0.5), "no-locality predicts": 0.5})
    gt = pd.DataFrame(grp)
    gt.to_csv(OUT / "A6_ratios_by_class_side.csv", index=False)
    # neighbour paths: dose-response (change vs CSF widening of the two lobes it faces) and |dS| / |S|
    E = {"Mild_lobe": (0, 7.5, 11.5, 0, 11.5, 7.5), "Mild_lobe_new": (0, 7.5, 11.5, 0, 11.5, 7.5),
         "Moderate_lobe": (11.5, 12.5, 15.5, 0, 15.5, 12.5), "Moderate_lobe_c3": (11.5, 12.5, 15.5, 0, 15.5, 12.5),
         "Severe_lobe": (15.5, 17.5, 18, 11.5, 18, 17.5), "Severe_lobe_c3": (15.5, 17.5, 18, 11.5, 18, 17.5),
         LO: (0, 7.5, 11.5, 0, 0, 0)}
    refs = {"Mild_lobe": H6, "Moderate_lobe": H6, "Severe_lobe": H6, LO: H6, "Mild_lobe_new": H7,
            "Moderate_lobe_c3": H7, "Severe_lobe_c3": H7}
    dr = []
    for d, e in E.items():
        for i in range(6):
            j = (i + 1) % 6
            k = L8.path_key(min(i, j), max(i, j))
            dr.append({"design": d, "neighbour path": k[5:], "mean CSF widening of its two lobes mm": 0.5 * (e[i] + e[j]),
                       "change dB": g(d, k) - g(refs[d], k), "clean ruler dB": max(R["yard"][k], R["fdiff"][k])})
    drt = pd.DataFrame(dr)
    drt.to_csv(OUT / "A6_neighbour_dose_response.csv", index=False)
    dosebin = drt.assign(bin=pd.cut(drt["mean CSF widening of its two lobes mm"], [-0.1, 0.1, 6, 10, 13, 16, 19])).groupby(
        "bin", observed=True).agg(paths=("change dB", "size"), mean_change=("change dB", "mean"),
                                  max_abs=("change dB", lambda v: float(np.abs(v).max()))).reset_index()
    dosebin["bin"] = dosebin["bin"].astype(str)
    rel = []
    for k_ in range(4):
        ii = [(i, j) for i in range(6) for j in range(i, 6) if DIST[i, j] == k_]
        a = np.array([np.sqrt(np.mean(np.abs(sbar(Sd["Mild_lobe"])[:, i, j] - sbar(Sd[H6])[:, i, j]) ** 2)) for i, j in ii])
        b = np.array([np.sqrt(np.mean(np.abs(sbar(Sd[H6])[:, i, j]) ** 2)) for i, j in ii])
        mag = np.array([np.mean(np.abs(20 * np.log10(np.abs(sbar(Sd["Mild_lobe"])[:, i, j]) / np.abs(sbar(Sd[H6])[:, i, j]))))
                        for i, j in ii])
        phs = np.array([np.mean(np.abs(np.degrees(np.angle(sbar(Sd["Mild_lobe"])[:, i, j] * np.conj(sbar(Sd[H6])[:, i, j])))))
                        for i, j in ii])
        rel.append({"path type": L7.PATH[k_], "|S| band-rms dB": float(20 * np.log10(np.median(b))),
                    "|dS| band-rms (Mild - healthy) dB": float(20 * np.log10(np.median(a))),
                    "|dS| / |S| dB": float(20 * np.log10(np.median(a / b))),
                    "mean |magnitude change| dB": float(np.median(mag)), "mean |phase change| deg": float(np.median(phs))})
    relt = pd.DataFrame(rel)
    relt.to_csv(OUT / "A6_relative_change.csv", index=False)
    L += ["## A6. Mechanism: LeftOnly against Mild, per path class and side",
          "Ratio = LeftOnly change / Mild change of the same path against the same healthy head; only paths whose Mild "
          "change is >= 2x the path's clean ruler give a usable ratio (inverse-variance weighted per class and side). "
          "Locality predicts 1 on the left, 0 on the right, 0.5 across; no locality predicts 0.5 everywhere.",
          md(gt, ".2f"), "", "Per path, with the phase changes (degrees, band-mean of the wrapped difference):",
          md(a6t[a6t.comparison.str.startswith("rule 1")].drop(columns=["comparison"]), ".2f"), "",
          "Neighbour paths, dose-response over every stage design (change against the CSF widening of the two lobes "
          "the path faces):", md(dosebin, ".3f"), "",
          "What kind of change each path type sees (Mild - Healthy_sliced_new, median over the paths of each type; "
          "magnitude and phase changes are band-means of the absolute per-frequency change):", md(relt, ".2f"), ""]
    r1 = a6t[a6t.comparison.str.startswith("rule 1") & (a6t.type == "neighbour")]
    nbl, nbr = r1[r1.side == "left"], r1[r1.side == "right"]
    nrel = relt.set_index("path type").loc["neighbour"]
    nbi = a3.set_index("statistic").loc["phase LR index, neighbour paths"]
    L += ["Neighbour paths, power against phase (LeftOnly and Mild minus Healthy_sliced_new):",
          md(r1[["path", "side", "LeftOnly change dB", "Mild change dB", "clean ruler dB", "LeftOnly phase change deg",
                 "Mild phase change deg", "phase clean ruler deg", "LeftOnly phase / ruler"]], ".2f"), ""]
    summary.append({"question": "A6 mechanism", "verdict": "CHANGED (claim withdrawn; mechanism measured)",
                    "old -> new": "'weaker copy of the symmetric Mild change; long paths wrap round' -> holds for band "
                                  "power only. Neighbour paths change in phase, not power: |dS|/|S| "
                                  f"{nrel['|dS| / |S| dB']:.1f} dB with a {nrel['mean |magnitude change| dB']:.2f} dB magnitude "
                                  f"and {nrel['mean |phase change| deg']:.1f} deg phase change (Mild); LeftOnly phase change "
                                  f"left {nbl['LeftOnly phase change deg'].min():.1f} to {nbl['LeftOnly phase change deg'].max():.1f} deg "
                                  f"vs right {nbr['LeftOnly phase change deg'].min():.1f} to {nbr['LeftOnly phase change deg'].max():.1f} deg "
                                  f"(Mild {r1['Mild phase change deg'].min():.1f} to {r1['Mild phase change deg'].max():.1f} deg on both "
                                  "sides). Left larger than right, but per path or pair only 2-3x the rulers (mirror-test "
                                  f"neighbour phase index {nbi['/ clean ruler']:.1f}x clean, {nbi['/ null rms']:.1f}x null rms); the "
                                  "decisive left-right evidence is the phase cross-ratios (A3). Wrap-round vs a global CSF_Mild "
                                  "component is not separable in power",
                    "evidence": "results/05_lobe/review/A6_*.csv"})

    # ------------------------------------------------------------------ A7 MCI: circulant decomposition
    def bpdb(d):
        return L7.db(L7.band_power(f, Sd[d][None]))[0]

    def circ(P):
        C = P.copy()
        for k_ in range(4):
            mm = DIST == k_
            C[mm] = P[mm].mean()
        return C
    chi_db = lambda P: L7.cross_ratios(10 ** (P / 10))        # noqa: E731
    PM, P6, P7 = bpdb(MCI), bpdb(H6), bpdb(H7)
    resid = []
    for d, P in ((MCI, PM), (H6, P6), (H7, P7)):
        Rr = P - circ(P)
        for k_ in range(4):
            resid.append({"file": d, "path type": L7.PATH[k_], "circulant residual rms dB": float(np.sqrt(np.mean(Rr[DIST == k_] ** 2)))})
    rt = pd.DataFrame(resid)
    c_full = {n: chi_db(PM)[n] - chi_db(P6)[n] for n in chi_db(PM)}
    c_circ = {n: chi_db(circ(PM))[n] - chi_db(circ(P6))[n] for n in c_full}
    c_mesh = {n: chi_db(P7)[n] - chi_db(P6)[n] for n in c_full}
    sdn = R["sd"]["noise SD"]
    a7 = pd.DataFrame([{"cross-ratio": n, "MCI - Healthy_new dB": c_full[n], "circulant part dB": c_circ[n],
                        "non-circulant (residual) part dB": c_full[n] - c_circ[n],
                        "/ noise SD": abs(c_full[n]) / sdn[f"chi {n}"],
                        "Healthy_sliced - Healthy_new (same design, mesh only) dB": c_mesh[n],
                        "mesh-only / noise SD": abs(c_mesh[n]) / sdn[f"chi {n}"]} for n in c_full])
    a7 = a7.sort_values("/ noise SD", ascending=False)
    a7.to_csv(OUT / "A7_mci_circulant.csv", index=False)
    flag = a7[a7["/ noise SD"] >= 3]
    L += ["## A7. MCI cross-ratios against the circulant symmetry of each file",
          "Both MCI_lobe and the healthy heads are rotationally symmetric by construction, so any non-circulant part of "
          "their band powers is numerical. Circulant residual of each file:", md(rt, ".3f"), "",
          "Each cross-ratio of MCI - Healthy_sliced_new split into the change of the circulant projection (physics a "
          "symmetric head can produce) and the change of the residual (numerical), with the same-design mesh-only "
          "difference Healthy_sliced - Healthy_sliced_new alongside:", md(a7.head(12), ".3f"), ""]
    summary.append({"question": "A7 MCI 4x = mesh?", "verdict": "CONFIRMED (now with evidence)",
                    "old -> new": f"asserted -> the {len(flag)} cross-ratios >= 3x noise SD are "
                                  f"{100 * float(np.mean(np.abs(flag['non-circulant (residual) part dB']) / np.abs(flag['MCI - Healthy_new dB']))):.0f}% "
                                  "non-circulant (mean |residual part| / |total|); the same-design mesh-only difference "
                                  f"reaches {a7['mesh-only / noise SD'].max():.1f}x noise SD "
                                  f"({int((a7['mesh-only / noise SD'] >= 3).sum())} cross-ratios >= 3x)",
                    "evidence": "results/05_lobe/review/A7_mci_circulant.csv"})

    # ------------------------------------------------------------------ A8 lobe-Mild three-stage
    a8 = a1t[(a1t.rule == "three") & a1t.design.isin(["Mild_lobe", "Mild_lobe_new"])]
    L += ["## A8. Lobe-Mild under the three-stage rule",
          "Distance of R21 to the nearest point where the frozen three-stage label changes, against the R21 yardstick and "
          "the bootstrap SD of that boundary (A9):", md(a8, ".3f"), "",
          "Neither set clears 2x: the 0.41 vs 0.69 difference between the sets is what an undetermined label looks like. "
          "'weakened' for lobe_B came from the fraction-correct tier (>= 0.5), which ignores mesh and boundary "
          "uncertainty; under the one bar it is 'not determined', i.e. retracted in both sets.", ""]
    summary.append({"question": "A8 lobe-Mild three-stage", "verdict": "CHANGED (reverted)",
                    "old -> new": "lobe_B 'weakened' -> retracted (not determined): " + "; ".join(
                        f"{r.design} {r['distance to label edge dB']:+.3f} dB = {r['/ max(yardstick, boundary SD)']:.2f}x"
                        for _, r in a8.iterrows()),
                    "evidence": "results/05_lobe/review/A1_one_bar.csv"})

    st = pd.DataFrame(summary)
    st.to_csv(OUT / "summary.csv", index=False)
    L += ["## Summary", md(st), "",
          "One solve per design: within-simulation noise robustness, not generalisation."]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print((OUT / "report.md").read_text(encoding="utf-8"))


def pth(p):
    a = p.replace(" refl.", "")
    if "-" not in a:
        i = ANT.index(a)
        return i, i
    i, j = (ANT.index(x) for x in a.split("-"))
    return i, j


if __name__ == "__main__":
    main()
