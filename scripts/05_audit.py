"""Audit of the ratio staging lead (R31 / R21 / R32) before it goes into STATUS.md.

    python scripts/05_audit.py [--n 150] [--n-perm 60] [--jobs 10] [--no-freeze]

Uses the 9 solves of config_repeats.yaml (v2 + v1 repeats). Writes results/04/audit/ and,
unless --no-freeze, results/04/frozen_rule.json (never to be edited afterwards).

 1  independence of the repeats; solve-to-solve SD from all 4 pairs and from Mild+Moderate only
 2  feature selection nested inside leave-one-solve-out, starting from all 89 features
 3  exact permutation test over all distinct assignments of stage labels to solves
 4  per-solve R31 / R21 / R32 with noise bars; monotonicity
 5  band robustness of the k = 2 path (sub-bands, 2.8-3.2 GHz, null region removed)
 6  hardware: ±2 dB / ±10 deg per-port errors, instrument floor sweep
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adstage.classes import scheme_groups  # noqa: E402
from adstage.config import load_config  # noqa: E402
from adstage.features.metrics import to_ring_order  # noqa: E402
from adstage.features.ring_features import features, ratios  # noqa: E402
from adstage.io.dataset import common_grid, load_dataset, resample  # noqa: E402
from adstage.io.masking import mask_glitches  # noqa: E402
from adstage.io.touchstone import read_touchstone  # noqa: E402
from adstage.noise.model import PROFILES, NoiseProfile  # noqa: E402
from adstage.noise.reference import mesh_pairs  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.results import git_hash  # noqa: E402

OUT = ROOT / "results" / "04" / "audit"
RAT = ["R31", "R21", "R32"]
STAGE_ORDER = ["Normal", "MCI", "Mild", "Moderate", "Severe"]
BANDS = {"3.2-4.2 (reference)": [(3.2e9, 4.2e9)], "3.2-3.6": [(3.2e9, 3.6e9)], "3.6-4.2": [(3.6e9, 4.2e9)],
         "3.2-4.2 minus 3.72-3.90 (k2 nulls)": [(3.2e9, 3.72e9), (3.9e9, 4.2e9)],
         "2.8-3.2 (no v1 Severe)": [(2.8e9, 3.2e9)]}


# ============================================================ helpers
def lda():
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    return LinearDiscriminantAnalysis


def fit_lda(Z, y, n_cls):
    LDA = lda()
    if Z.shape[1] > 1:
        return LDA(solver="lsqr", shrinkage="auto", priors=np.full(n_cls, 1 / n_cls)).fit(Z, y)
    return LDA(solver="svd", priors=np.full(n_cls, 1 / n_cls)).fit(Z, y)


def bal_acc(y, p):
    from sklearn.metrics import balanced_accuracy_score
    return float(balanced_accuracy_score(y, p))


def solve_sd(vals, pairs):
    """rms over pairs of (difference / sqrt 2), with 95% CI from chi2(P)."""
    d = np.array([(vals[b] - vals[a]) / np.sqrt(2) for a, b in pairs])
    P = len(d)
    s = float(np.sqrt(np.mean(d ** 2)))
    lo = s * np.sqrt(P / stats.chi2.ppf(0.975, P))
    hi = s * np.sqrt(P / stats.chi2.ppf(0.025, P))
    return s, lo, hi, P


def gap_test(m, cls, a_stages, b_stages, sd, dof):
    """Gap between the equal-weight means of two stage sets; t = gap / SE with SE from the solve SD
    (each solve mean carries solve noise sd), two-sided p from t(dof)."""
    def grp(st):
        sols = [s for s in m if cls[s] in st]
        per_stage = [np.mean([m[s] for s in sols if cls[s] == x]) for x in st]
        n_per = [sum(cls[s] == x for s in sols) for x in st]
        var = sd ** 2 * sum(1 / n for n in n_per) / len(st) ** 2
        return np.mean(per_stage), var
    ma, va = grp(a_stages)
    mb, vb = grp(b_stages)
    gap = mb - ma
    t = gap / np.sqrt(va + vb)
    return float(gap), float(t), float(2 * stats.t.sf(abs(t), dof))


# ============================================================ data
def load_native(cfg, ds):
    """Each solve on its own band at 5 MHz (glitch-masked), ring order: [(f, S)]."""
    raw = ROOT / cfg["data"]["raw_dir"]
    out = []
    for fname in ds.files:
        t = read_touchstone(raw / fname)
        s, _ = mask_glitches(t.f_hz, t.s, float(cfg["qc"]["glitch_thr_db"]))
        f = common_grid([t.f_hz], 5e6)
        out.append((f, to_ring_order(resample(t.f_hz, s, f), ds.port_to_ant)))
    return out


def make_draws(cfg, f, S, prof, n, tag, acfg):
    rng = np.random.default_rng([cfg["seed"], 50, *tag])
    return draws(f, S, prof, n, rng, acfg)


# ============================================================ nested selection
def univariate_scores(Xtr, tr, cls, pairs):
    """min over class pairs of gap^2 / (within var + between var), per feature, training solves only."""
    m = {s: Xtr[s].mean(0) for s in tr}
    within = np.mean([Xtr[s].var(0, ddof=1) for s in tr], 0)
    pr = [(a, b) for a, b in pairs if a in m and b in m]
    between = np.mean([(m[b] - m[a]) ** 2 / 2 for a, b in pr], 0) if pr else 0
    classes = sorted({cls[s] for s in tr})
    mu = {c: np.mean([m[s] for s in tr if cls[s] == c], 0) for c in classes}
    J = [(mu[a] - mu[b]) ** 2 / (within + between + 1e-12) for a, b in itertools.combinations(classes, 2)]
    return np.min(J, 0)


def candidates(Xtr, tr, cls, pairs, groups):
    c = {g: v for g, v in groups.items()}
    sc = univariate_scores(Xtr, tr, cls, pairs)
    order = np.argsort(-sc)
    for k in (1, 2, 3, 5, 10):
        c[f"top{k}"] = list(order[:k])
    return c


def inner_score(Xtr, tr, cls, idx):
    preds, ys = [], []
    for s_in in tr:
        if sum(cls[t] == cls[s_in] for t in tr) < 2:
            continue
        rest = [t for t in tr if t != s_in]
        sc = np.concatenate([Xtr[t][:, idx] - Xtr[t][:, idx].mean(0) for t in rest]).std(0, ddof=1) + 1e-12
        Z = np.concatenate([Xtr[t][:, idx] / sc for t in rest])
        y = np.concatenate([np.full(len(Xtr[t]), cls[t]) for t in rest])
        mdl = fit_lda(Z, y, len(set(y)))
        preds.append(mdl.predict(Xtr[s_in][:, idx] / sc))
        ys.append(np.full(len(Xtr[s_in]), cls[s_in]))
    if not preds:
        return np.nan
    return bal_acc(np.concatenate(ys), np.concatenate(preds))


def select(Xtr, tr, cls, pairs, groups):
    best = None
    for name, idx in candidates(Xtr, tr, cls, pairs, groups).items():
        sc = inner_score(Xtr, tr, cls, idx)
        key = (-(sc if np.isfinite(sc) else -1), len(idx), name)
        if best is None or key < best[0]:
            best = (key, name, list(idx), sc)
    return best[1], best[2], best[3]


def nested_loso(Xtr_all, Xte_all, solves, cls, pairs, groups):
    """Outer leave-one-solve-out with selection inside. Returns balanced acc, per-fold choices."""
    ys, ps, folds = [], [], []
    for s_out in solves:
        if sum(cls[t] == cls[s_out] for t in solves) < 2:
            continue
        tr = [s for s in solves if s != s_out]
        pr = [(a, b) for a, b in pairs if s_out not in (a, b)]
        Xtr = {s: Xtr_all[s] for s in tr}
        name, idx, sc = select(Xtr, tr, cls, pr, groups)
        scale = np.concatenate([Xtr[t][:, idx] - Xtr[t][:, idx].mean(0) for t in tr]).std(0, ddof=1) + 1e-12
        Z = np.concatenate([Xtr[t][:, idx] / scale for t in tr])
        y = np.concatenate([np.full(len(Xtr[t]), cls[t]) for t in tr])
        mdl = fit_lda(Z, y, len(set(y)))
        ps.append(mdl.predict(Xte_all[s_out][:, idx] / scale))
        ys.append(np.full(len(Xte_all[s_out]), cls[s_out]))
        folds.append({"held_out": s_out, "chosen": name, "features": idx, "inner_bal_acc": sc,
                      "fold_acc": float((ps[-1] == ys[-1]).mean())})
    return bal_acc(np.concatenate(ys), np.concatenate(ps)), folds


def fixed_loso(Xtr_all, Xte_all, solves, cls, idx):
    ys, ps = [], []
    for s_out in solves:
        if sum(cls[t] == cls[s_out] for t in solves) < 2:
            continue
        tr = [s for s in solves if s != s_out]
        scale = np.concatenate([Xtr_all[t][:, idx] - Xtr_all[t][:, idx].mean(0) for t in tr]).std(0, ddof=1) + 1e-12
        Z = np.concatenate([Xtr_all[t][:, idx] / scale for t in tr])
        y = np.concatenate([np.full(len(Xtr_all[t]), cls[t]) for t in tr])
        mdl = fit_lda(Z, y, len(set(y)))
        ps.append(mdl.predict(Xte_all[s_out][:, idx] / scale))
        ys.append(np.full(len(Xte_all[s_out]), cls[s_out]))
    return bal_acc(np.concatenate(ys), np.concatenate(ps))


def partitions(solves, labels):
    """Distinct assignments of the label multiset to solves, deduplicated by the induced partition
    (renaming classes of equal size gives the same classifier problem)."""
    seen, out = set(), []
    for perm in set(itertools.permutations(labels)):
        key = frozenset(frozenset(s for s, l in zip(solves, perm) if l == c) for c in set(perm))
        if key not in seen:
            seen.add(key)
            out.append(dict(zip(solves, perm)))
    return out


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--n-perm", type=int, default=60)
    ap.add_argument("--jobs", type=int, default=10)
    ap.add_argument("--no-freeze", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    os.environ["MLI_CONFIG"] = "config_repeats.yaml"
    cfg = load_config(ROOT)
    gh = git_hash(ROOT)
    OUT.mkdir(parents=True, exist_ok=True)
    ds = load_dataset(cfg, ROOT)
    f = ds.f_hz
    S = to_ring_order(ds.S, ds.port_to_ant)
    n_s = len(ds.files)
    stage = dict(enumerate(ds.classes))
    pairs = mesh_pairs(ds.files, ds.manifest)
    man = ds.manifest
    acfg0 = dict(cfg.get("augment", {}))
    acfg0["gain_err_db"] = 0.5
    prof0 = PROFILES["typical"]
    print(f"code {gh}; solves {ds.classes}; pairs {pairs}")
    L = [f"# Audit of the ratio staging lead (code {gh}, {date.today().isoformat()})", "",
         "Data: 9 HFSS solves (v2 + v1 repeats of the same designs; only sweep settings differ, user 2026-10-01). "
         f"Noise unless stated: typical profile + setup perturbation + per-port gain ±0.5 dB; {args.n} draws "
         "per solve per split (train/test seeds differ). Uncertainties: 95% intervals unless stated. "
         "One head geometry throughout.", ""]
    claims = []

    # ---------------- base features (89) and per-solve ratio draws, reference band
    X = {"train": {}, "test": {}}
    for s in range(n_s):
        for sp, off in (("train", 0), ("test", 1)):
            Xs, names, groups, singles = features(f, make_draws(cfg, f, S[s], prof0, args.n, (s, off), acfg0))
            X[sp][s] = Xs
    groups = {g: v for g, v in groups.items()}
    ri = [names.index(r) for r in RAT]
    allX = {s: np.concatenate([X["train"][s], X["test"][s]]) for s in range(n_s)}
    m = {r: {s: float(allX[s][:, names.index(r)].mean()) for s in range(n_s)} for r in RAT}
    nsd = {r: {s: float(allX[s][:, names.index(r)].std(ddof=1)) for s in range(n_s)} for r in RAT}

    # ================================================================== 1. independence
    glitch = ds.masked_log.groupby("file").size() if len(ds.masked_log) else pd.Series(dtype=int)
    rows = []
    for a, b in pairs:
        r = {"stage": stage[a], "v2 solve": ds.files[a], "v1 solve": ds.files[b].split("/")[-1],
             "v2 project": man.loc[a, "project"], "v1 project": man.loc[b, "project"],
             "v1 native band": "3.2-4.2 GHz @2 MHz" if "Severe" in ds.files[b] else "2.8-4.2 GHz @5 MHz",
             "masked glitch pts v2/v1": f"{int(glitch.get(ds.files[a], 0))}/{int(glitch.get(ds.files[b], 0))}",
             "mesh tets": "not in files - ask user", "sweep type": "not in files - ask user"}
        for rr in RAT:
            d = m[rr][b] - m[rr][a]
            se = np.sqrt(nsd[rr][a] ** 2 + nsd[rr][b] ** 2) / np.sqrt(2 * args.n)
            r[f"{rr} v1-v2 dB"] = f"{d:+.3f} ± {1.96 * se:.3f}"
        rows.append(r)
    indep = pd.DataFrame(rows)
    indep.to_csv(OUT / "1_repeats.csv", index=False)
    mm_pairs = [(a, b) for a, b in pairs if stage[a] in ("Mild", "Moderate")]
    sd_rows, gap_rows = [], []
    for rr in RAT:
        for lab, pr in (("all 4 pairs", pairs), ("Mild+Moderate pairs only", mm_pairs)):
            s, lo, hi, P = solve_sd(m[rr], pr)
            sd_rows.append({"feature": rr, "pairs": lab, "solve_SD_dB": s, "95% CI": f"{lo:.3f}-{hi:.3f}", "dof": P})
            for ga, gb in ((["Mild"], ["Severe"]), (["Normal"], ["Mild", "Moderate", "Severe"]),
                           (["Mild"], ["Moderate"]), (["Moderate"], ["Severe"]), (["Normal"], ["MCI"])):
                gap, t, p = gap_test(m[rr], stage, ga, gb, s, P)
                gap_rows.append({"feature": rr, "SD from": lab, "pair": f"{'+'.join(ga)} | {'+'.join(gb)}",
                                 "gap_dB": gap, "t = gap/SE": t, "p (t, dof=P)": p,
                                 "gap/SD range over SD 95% CI": f"{abs(gap) / hi:.2f}-{abs(gap) / lo:.2f}"})
    sdt, gapt = pd.DataFrame(sd_rows), pd.DataFrame(gap_rows)
    sdt.to_csv(OUT / "1_solve_sd.csv", index=False)
    gapt.to_csv(OUT / "1_gaps.csv", index=False)
    L += ["## 1. How independent are the repeats?",
          "Mesh statistics (tetrahedra) and sweep type are **not recoverable from Touchstone files**: please supply "
          "them from HFSS (Solution Data / Profile per design). Indirect evidence below: project, native band, "
          "glitch count. Differences: v1 - v2 solve, ± 95% from measurement noise of the two solve means.",
          md(indep), "", "Solve-to-solve SD (rms of difference/sqrt2) with chi2 95% CI:", md(sdt, ".3f"), "",
          "Stage gaps. SE = solve SD x sqrt(sum 1/n_solves) for each side (stage means are averages of 2 solves "
          "or of 3 stage means); p from t with dof = number of pairs used for the SD.",
          md(gapt, ".3g"), ""]

    def g(rr, lab, pr):
        return gapt[(gapt.feature == rr) & (gapt["SD from"] == lab) & (gapt.pair == pr)].iloc[0]

    for rr in ("R21", "R32"):
        x4, x2 = g(rr, "all 4 pairs", "Mild | Severe"), g(rr, "Mild+Moderate pairs only", "Mild | Severe")
        claims.append({"claim": f"{rr} separates Mild vs Severe beyond solve noise",
                       "number": f"gap {x4['gap_dB']:+.2f} dB; t={x4['t = gap/SE']:.1f} (4 pairs, p={x4['p (t, dof=P)']:.2g}); "
                                 f"t={x2['t = gap/SE']:.1f} (Mild+Moderate pairs only, p={x2['p (t, dof=P)']:.2g})",
                       "baseline": "solve-to-solve SD (4 pairs / 2 pairs that changed project)",
                       "verdict": verdict_t(x2["t = gap/SE"], x2["p (t, dof=P)"])})
    x = g("R21", "Mild+Moderate pairs only", "Normal | Mild+Moderate+Severe")
    claims.append({"claim": "R21 Normal vs AD beyond solve noise", "number":
                   f"gap {x['gap_dB']:+.2f} dB; t={x['t = gap/SE']:.1f}, p={x['p (t, dof=P)']:.2g} (2-pair SD)",
                   "baseline": "solve SD from Mild+Moderate pairs", "verdict": verdict_t(x["t = gap/SE"], x["p (t, dof=P)"])})
    x = g("R31", "Mild+Moderate pairs only", "Normal | Mild+Moderate+Severe")
    claims.append({"claim": "R31 Normal vs AD beyond solve noise", "number":
                   f"gap {x['gap_dB']:+.2f} dB; t={x['t = gap/SE']:.1f}, p={x['p (t, dof=P)']:.2g} (2-pair SD)",
                   "baseline": "solve SD from Mild+Moderate pairs", "verdict": verdict_t(x["t = gap/SE"], x["p (t, dof=P)"])})
    x = g("R32", "Mild+Moderate pairs only", "Mild | Moderate")
    claims.append({"claim": "Mild vs Moderate separable", "number": f"R32 gap {x['gap_dB']:+.2f} dB; t={x['t = gap/SE']:.2f}",
                   "baseline": "solve SD (2 pairs)", "verdict": "not supported (no claim made)"})

    # ================================================================== 2. nested selection + freeze
    sel_rows, fold_rows = [], []
    for scheme in ("three", "three_merged", "binary"):
        gst = scheme_groups(cfg, scheme)
        cls = {s: gi for gi, (gname, st) in enumerate(gst.items()) for s in range(n_s) if stage[s] in st}
        solves = sorted(cls)
        acc, folds = nested_loso(X["train"], X["test"], solves, cls, pairs, groups)
        acc_ratio = fixed_loso(X["train"], X["test"], solves, cls, ri)
        n_ratio = sum(set(fo["features"]) <= set(ri) for fo in folds)
        n_any_ratio = sum(bool(set(fo["features"]) & set(ri)) for fo in folds)
        for fo in folds:
            fold_rows.append({"scheme": scheme, "held_out": ds.files[fo["held_out"]], "chosen": fo["chosen"],
                              "features": ",".join(names[i] for i in fo["features"]) if len(fo["features"]) <= 10
                              else f"{len(fo['features'])} features", "inner_bal_acc": fo["inner_bal_acc"],
                              "fold_acc": fo["fold_acc"]})
        sel_rows.append({"scheme": scheme, "outer folds": len(folds), "nested-selection LOSO bal. acc": acc,
                         "folds choosing only ratio features": f"{n_ratio}/{len(folds)}",
                         "folds choosing >=1 ratio feature": f"{n_any_ratio}/{len(folds)}",
                         "fixed G_ratio LDA LOSO bal. acc (not nested)": acc_ratio})
    selt, foldt = pd.DataFrame(sel_rows), pd.DataFrame(fold_rows)
    selt.to_csv(OUT / "2_nested_selection.csv", index=False)
    foldt.to_csv(OUT / "2_nested_folds.csv", index=False)
    L += ["## 2. Selection bias: feature selection inside each leave-one-solve-out fold",
          "Candidates per training set: the 4 groups (G_refl, G_coup, G_ratio, G_all) and the top-k (k = 1, 2, 3, "
          "5, 10) of all 89 features ranked by min-pairwise gap^2 / (within + between-solve variance) on the training "
          "solves. Chosen by inner leave-one-solve-out balanced accuracy (LDA), ties -> fewer features. The chosen "
          "set is refitted on the training solves and tested on the held-out solve.",
          md(selt, ".3f"), "", "Per fold:", md(foldt, ".3f"), ""]
    t3 = selt[selt.scheme == "three"].iloc[0]
    claims.append({"claim": "3-class staging survives selection inside the folds",
                   "number": f"nested bal. acc {t3['nested-selection LOSO bal. acc']:.3f}; ratios-only chosen in "
                             f"{t3['folds choosing only ratio features']} folds",
                   "baseline": "chance 0.333; non-nested G_ratio 1.000",
                   "verdict": "holds" if t3["nested-selection LOSO bal. acc"] >= 0.9 else
                   ("weakened" if t3["nested-selection LOSO bal. acc"] >= 0.6 else "retracted")})

    frozen = None
    if not args.no_freeze:
        frozen = freeze(cfg, gh, ds, X, names, groups, stage, pairs, n_s)
        L += ["Frozen rule written to `results/04/frozen_rule.json` (selection run on all 9 solves with the same "
              f"procedure): staging features = {frozen['staging']['three']['features']}, merged = "
              f"{frozen['staging']['three_merged']['features']}. It must be applied unchanged to new solves "
              "(`adstage.frozen.apply_rule`).", ""]

    # ================================================================== 3. permutation test
    perm_rows = []
    Xp = {"train": {}, "test": {}}
    for s in range(n_s):
        for sp, off in (("train", 2), ("test", 3)):
            Xp[sp][s] = features(f, make_draws(cfg, f, S[s], prof0, args.n_perm, (s, off), acfg0))[0]
    from joblib import Parallel, delayed
    for scheme in ("three", "three_merged", "binary"):
        gst = scheme_groups(cfg, scheme)
        cls = {s: gi for gi, (gname, st) in enumerate(gst.items()) for s in range(n_s) if stage[s] in st}
        solves = sorted(cls)
        parts = partitions(solves, [cls[s] for s in solves])
        obs_key = frozenset(frozenset(s for s in solves if cls[s] == c) for c in set(cls.values()))

        def run(pc):
            a_n = nested_loso(Xp["train"], Xp["test"], solves, pc, pairs, groups)[0]
            a_r = fixed_loso(Xp["train"], Xp["test"], solves, pc, ri)
            key = frozenset(frozenset(s for s in solves if pc[s] == c) for c in set(pc.values()))
            return a_n, a_r, key == obs_key
        res = Parallel(n_jobs=args.jobs)(delayed(run)(pc) for pc in parts)
        acc_n = np.array([r[0] for r in res])
        acc_r = np.array([r[1] for r in res])
        obs = [i for i, r in enumerate(res) if r[2]][0]
        n_lab = len(set(itertools.permutations([cls[s] for s in solves])))
        for lab, acc in (("nested selection", acc_n), ("fixed G_ratio", acc_r)):
            p = float((acc >= acc[obs] - 1e-12).mean())
            perm_rows.append({"scheme": scheme, "pipeline": lab, "solves": len(solves),
                              "label assignments": n_lab, "distinct partitions": len(parts),
                              "observed bal. acc": acc[obs], "null median": float(np.median(acc)),
                              "null max (excl. observed)": float(np.max(np.delete(acc, obs))),
                              "exact p": p, "smallest attainable p": 1 / len(parts)})
        pd.DataFrame({"partition": [str(sorted(sorted(ds.files[s].split('/')[-1] for s in solves if pc[s] == c)
                                                for c in set(pc.values()))) for pc in parts],
                      "nested_acc": acc_n, "fixed_ratio_acc": acc_r}).to_csv(OUT / f"3_perm_{scheme}.csv", index=False)
        top = np.argsort(-acc_n)[:4]
        perm_rows[-2]["top null partitions (nested acc)"] = "; ".join(
            f"{' / '.join('+'.join(sorted(stage[s] + ('(v1)' if man.loc[s, 'role'] == 'mesh_repeat' else '(v2)') for s in solves if parts[i][s] == c)) for c in sorted(set(parts[i].values())))}: {acc_n[i]:.2f}"
            for i in top if i != obs)
    permt = pd.DataFrame(perm_rows)
    permt.to_csv(OUT / "3_permutation.csv", index=False)
    L += ["## 3. Permutation test: stage labels shuffled across solves (antennas of a solve stay together)",
          f"All distinct assignments enumerated. Assignments that differ only by renaming equally sized classes "
          f"give the same problem, so the null is over distinct partitions. {args.n_perm} draws per solve per split. "
          "p = fraction of partitions with balanced accuracy >= observed (observed included).",
          md(permt, ".3g"), ""]
    for sch in ("three", "three_merged"):
        r = permt[(permt.scheme == sch) & (permt.pipeline == "nested selection")].iloc[0]
        claims.append({"claim": f"{sch} result is not achievable by arbitrary solve groupings",
                       "number": f"exact p = {r['exact p']:.3f} ({int(round(r['exact p'] * r['distinct partitions']))}/"
                                 f"{r['distinct partitions']}); null max {r['null max (excl. observed)']:.3f}",
                       "baseline": f"smallest attainable p = {r['smallest attainable p']:.4f}",
                       "verdict": ("holds" if r["exact p"] <= 0.05 else
                                   "cannot reach p<0.05 with these solves" if r["smallest attainable p"] > 0.05 else "weakened")})

    # ================================================================== 4. per-solve values
    per = pd.DataFrame([{"solve": ds.files[s].split("/")[-1], "stage": stage[s],
                         "set": "v1" if man.loc[s, "role"] == "mesh_repeat" else "v2",
                         **{f"{r}": m[r][s] for r in RAT}, **{f"{r} noise SD": nsd[r][s] for r in RAT}}
                        for s in range(n_s)])
    per["o"] = per.stage.map(STAGE_ORDER.index)
    per = per.sort_values(["o", "set"]).drop(columns="o")
    per.to_csv(OUT / "4_per_solve.csv", index=False)
    mono = []
    seq = ["Normal", "Mild", "Moderate", "Severe"]
    for r in RAT:
        sm = per.groupby("stage")[r].mean().reindex(seq)
        d = np.diff(sm.values)
        sd = solve_sd(m[r], pairs)[0]
        mono.append({"feature": r, **{f"{a}->{b} dB": x for (a, b), x in zip(zip(seq, seq[1:]), d)},
                     "monotone": bool(np.all(d > 0) or np.all(d < 0)),
                     "monotone ignoring steps < 1 solve SD": bool(np.all(d[np.abs(d) >= sd] > 0) or np.all(d[np.abs(d) >= sd] < 0)),
                     "solve SD dB": sd})
    monot = pd.DataFrame(mono)
    L += ["## 4. Per-solve values (dB; noise SD = spread over noisy draws of one solve)", md(per, ".3f"), "",
          "Monotonicity over Normal -> Mild -> Moderate -> Severe (stage means over solves):", md(monot, ".3f"), ""]
    fig_per_solve(per)

    # ================================================================== 5. band robustness
    native = load_native(cfg, ds)
    band_rows = []
    for bname, bands in BANDS.items():
        vals, nsds, avail = {r: {} for r in RAT}, {r: {} for r in RAT}, []
        for s, (fs, Ss) in enumerate(native):
            if fs[0] > bands[0][0] + 1 or fs[-1] < bands[-1][1] - 1:
                continue
            R = ratios(fs, make_draws(cfg, fs, Ss, prof0, args.n, (s, 7, len(bname)), acfg0), bands)
            avail.append(s)
            for r in RAT:
                vals[r][s], nsds[r][s] = float(R[r].mean()), float(R[r].std(ddof=1))
        pr = [(a, b) for a, b in pairs if a in avail and b in avail]
        for r in RAT:
            sd, lo, hi, P = solve_sd(vals[r], pr)
            for ga, gb in ((["Mild"], ["Severe"]), (["Normal"], ["Mild", "Moderate", "Severe"])):
                if not all(any(stage[s] == x for s in avail) for x in ga + gb):
                    continue
                gap, t, p = gap_test(vals[r], stage, ga, gb, sd, P)
                band_rows.append({"band": bname, "feature": r, "pair": f"{'+'.join(ga)} | {'+'.join(gb)}",
                                  "solves": len(avail), "pairs": P, "solve SD dB": sd, "gap dB": gap,
                                  "t": t, "p": p})
    bandt = pd.DataFrame(band_rows)
    bandt.to_csv(OUT / "5_bands.csv", index=False)
    k2null = []
    for s, (fs, Ss) in enumerate(native):
        p2 = (np.abs(Ss[:, [(t + 2) % 6 for t in range(6)], range(6)]) ** 2).mean(1)
        w = (fs >= 3.6e9) & (fs <= 4.0e9)
        k2null.append(f"{ds.files[s].split('/')[-1]}: {fs[w][np.argmin(p2[w])] / 1e9:.3f}")
    L += ["## 5. Band robustness of the ratios (k = 2 path)",
          "Location of the deepest k = 2 null in 3.6-4.0 GHz per solve: " + "; ".join(k2null) + ".",
          "Each band uses only the solves that cover it (the v1 Severe solve starts at 3.2 GHz, so 2.8-3.2 GHz has "
          "one Severe solve and 3 repeat pairs).", md(bandt, ".3g"), ""]
    for bname in BANDS:
        sub = bandt[(bandt.band == bname) & (bandt.pair == "Mild | Severe") & bandt.feature.isin(["R21", "R32"])]
        for _, r in sub.iterrows():
            claims.append({"claim": f"{r.feature}: Mild vs Severe in band {bname}",
                           "number": f"gap {r['gap dB']:+.2f} dB, solve SD {r['solve SD dB']:.2f} dB, t={r.t:.1f}, p={r.p:.2g}",
                           "baseline": f"solve SD in that band ({int(r.pairs)} pairs)",
                           "verdict": verdict_t(r.t, r.p)})

    # ================================================================== 6. hardware
    hw_rows = []
    conds = {"reference: typical, ±0.5 dB gain": (prof0, {"gain_err_db": 0.5}),
             "±2 dB gain + ±10° phase per port": (prof0, {"gain_err_db": 2.0, "phase_err_deg": 10.0}),
             "floor -70 dB (typical)": (prof0, {"gain_err_db": 0.5}),
             "floor -60 dB": (NoiseProfile("f60", 0.25, 2, -60, 0), {"gain_err_db": 0.5})}
    for fl in np.arange(-90, -47.5, 2.5):
        conds[f"floor sweep {fl:.1f} dB"] = (NoiseProfile(f"f{fl}", 0.25, 2, float(fl), 0), {"gain_err_db": 0.5})
    gst3 = scheme_groups(cfg, "three")
    cls3 = {s: gi for gi, (gname, st) in enumerate(gst3.items()) for s in range(n_s) if stage[s] in st}
    for ci, (cname, (prof, extra)) in enumerate(conds.items()):
        ac = dict(cfg.get("augment", {}))
        ac.update(extra)
        Xh = {"train": {}, "test": {}}
        for s in range(n_s):
            for sp, off in (("train", 0), ("test", 1)):
                Dd = make_draws(cfg, f, S[s], prof, args.n_perm, (s, off, 100 + ci), ac)
                Xh[sp][s] = np.stack([ratios(f, Dd, [(f[0], f[-1])])[r] for r in RAT], 1)
        mh = {r: {s: float(np.concatenate([Xh["train"][s], Xh["test"][s]])[:, j].mean()) for s in range(n_s)}
              for j, r in enumerate(RAT)}
        nh = {r: float(np.mean([np.concatenate([Xh["train"][s], Xh["test"][s]])[:, j].std(ddof=1)
                                for s in range(n_s)])) for j, r in enumerate(RAT)}
        sd, lo, hi, P = solve_sd(mh["R21"], pairs)
        gap, t, p = gap_test(mh["R21"], stage, ["Mild"], ["Severe"], np.sqrt(sd ** 2 + nh["R21"] ** 2 / args.n_perm), P)
        hw_rows.append({"condition": cname, "3-class LOSO bal. acc (ratios, LDA)":
                        fixed_loso(Xh["train"], Xh["test"], sorted(cls3), cls3, [0, 1, 2]),
                        "R21 noise SD per measurement dB": nh["R21"], "R21 Mild|Severe gap dB": gap,
                        "R21 gap / per-measurement noise SD": abs(gap) / nh["R21"], "t vs solve SD": t})
    hwt = pd.DataFrame(hw_rows)
    hwt.to_csv(OUT / "6_hardware.csv", index=False)
    sweep = hwt[hwt.condition.str.startswith("floor sweep")].copy()
    sweep["floor"] = sweep.condition.str.extract(r"(-?\d+\.\d)").astype(float)
    ok = sweep[(sweep["3-class LOSO bal. acc (ratios, LDA)"] >= 0.95) & (sweep["R21 gap / per-measurement noise SD"] >= 3)]
    fmin = float(ok.floor.max()) if len(ok) else np.nan
    lvl = {k: float(np.mean([allX[s][:, names.index(k)].mean() for s in range(n_s)])) for k in ("k1_band", "k2_band", "k3_band")}
    L += ["## 6. Hardware realism (ratios only; 3-class = Normal / Mild / Severe)",
          f"Band powers (ring mean, 3.2-4.2 GHz): C1 {lvl['k1_band']:.1f} dB, C2 {lvl['k2_band']:.1f} dB, "
          f"C3 {lvl['k3_band']:.1f} dB. Per-port phase errors cannot change the ratios: they multiply S_ij by "
          "e^{j(phi_i+phi_j)} and the ratios use |S|^2 only.", md(hwt, ".3g"), "",
          f"Highest floor at which the R21 rule still gives >= 0.95 LOSO balanced accuracy and a Mild|Severe gap >= 3x "
          f"the per-measurement noise SD: **{fmin:.1f} dB** (sweep step 2.5 dB, {args.n_perm} draws/solve)."]
    fig_floor(sweep)
    for cname in ("±2 dB gain + ±10° phase per port", "floor -60 dB"):
        r = hwt[hwt.condition == cname].iloc[0]
        claims.append({"claim": f"staging survives {cname}",
                       "number": f"3-class bal. acc {r['3-class LOSO bal. acc (ratios, LDA)']:.3f}; R21 gap/noise "
                                 f"{r['R21 gap / per-measurement noise SD']:.1f}",
                       "baseline": "reference condition, chance 0.333",
                       "verdict": "holds" if r["3-class LOSO bal. acc (ratios, LDA)"] >= 0.95 else
                       ("weakened" if r["3-class LOSO bal. acc (ratios, LDA)"] >= 0.6 else "retracted")})
    claims.append({"claim": "minimum instrument floor for the R21 staging rule", "number": f"<= {fmin:.1f} dB",
                   "baseline": f"C2 level {lvl['k2_band']:.1f} dB", "verdict": "requirement"})

    # ================================================================== claims + falsification
    L += ["", "## Claims", md(pd.DataFrame(claims)), "", "## 7. Falsification criteria", FALSIFICATION, ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    pd.DataFrame(claims).to_csv(OUT / "claims.csv", index=False)
    print((OUT / "report.md").read_text(encoding="utf-8"))


def verdict_t(t, p):
    t = abs(t)
    if t >= 3 and p <= 0.05:
        return "holds"
    if t >= 2:
        return "weakened"
    return "retracted"


FALSIFICATION = """Fixed before any new data (frozen rule: `results/04/frozen_rule.json`, applied unchanged):

1. **Normal mesh repeat (Max Delta S 0.01).** Retract if the new-mesh Normal differs from the v2 Normal by more than
   0.5 dB in R21 or R32 (that alone would put the solve SD near the Mild-Severe gap / 2). Weakened if > 0.25 dB.
2. **Mild and Severe re-solved with the finer mesh.** Retract if the frozen 3-class rule classifies either one
   wrongly in > 5% of noisy measurements (typical noise, ±0.5 dB gain), or if R21(Severe) - R21(Mild) < 0.5 dB.
3. **A second head geometry, Mild and Severe** (e.g. head scale 0.95, or skull +1 mm). Retract the staging lead if
   the R21 or R32 ordering flips (Severe not beyond Mild in the same direction), or if the Mild-Severe gap is below
   2x the solve-to-solve SD. The frozen rule failing on the new head is reported as "no generalisation".
4. **Antenna stand-off ±2 mm (Normal and Severe).** Weakened if the R21 shift exceeds half the Mild-Severe gap
   (0.6 dB); retract if it exceeds the full gap.
5. **Second MCI solve.** Not about staging, but: retract any MCI statement if the two MCI solves differ by more than
   their distance to Normal in R21/R32 (expected: they will not separate; no MCI claim is made now)."""


def md(df, fmt=".3g"):
    def cell(v):
        if isinstance(v, (float, np.floating)):
            return "n/a" if not np.isfinite(v) else format(v, fmt)
        return str(v)
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    return "\n".join([head, sep] + ["| " + " | ".join(cell(v) for v in r) + " |" for r in df.itertuples(index=False)])


def freeze(cfg, gh, ds, X, names, groups, stage, pairs, n_s):
    """Select on all solves with the same procedure, fit LDA, and write the frozen rule."""
    rule = {"frozen_on": date.today().isoformat(), "git_hash": gh,
            "note": "Do not edit. Apply unchanged to new solves with adstage.frozen.apply_rule.",
            "trained_on": [f.split("/")[-1] for f in ds.files], "trained_classes": list(ds.classes),
            "feature_spec": {"band_hz": [3.2e9, 4.2e9], "module": "adstage.features.ring_features.features",
                             "ring_order_port_to_ant": [int(v) for v in ds.port_to_ant],
                             "floor": "subtracted (adstage.features.floor.floor_power)",
                             "glitch_masking": "on, -30 dB"},
            "noise_used_for_training": "typical + setup perturbation + per-port gain ±0.5 dB",
            "p_star_reject": 0.7, "staging": {}}
    thr = pd.read_csv(ROOT / "results" / "v2_with_v1_repeats" / "03" / "thresholds.csv")
    t = thr[(thr.feature == "M5.R31") & (thr.profile == "typical")].iloc[0]
    rule["detection_binary_R31"] = {"feature": "R31", "tau_dB": float(t.tau_dB), "margin_dB": float(t.margin_dB),
                                    "decision": "AD if R31 < tau - margin; Normal if R31 > tau + margin; else UNCERTAIN",
                                    "source": "results/v2_with_v1_repeats/03/thresholds.csv (typical)"}
    for scheme in ("three", "three_merged"):
        gst = scheme_groups(cfg, scheme)
        gn = list(gst)
        cls = {s: gi for gi, (gname, st) in enumerate(gst.items()) for s in range(n_s) if stage[s] in st}
        sol = sorted(cls)
        name, idx, sc = select({s: X["train"][s] for s in sol}, sol, cls, pairs, groups)
        scale = np.concatenate([X["train"][s][:, idx] - X["train"][s][:, idx].mean(0) for s in sol]).std(0, ddof=1) + 1e-12
        Z = np.concatenate([X["train"][s][:, idx] / scale for s in sol])
        y = np.concatenate([np.full(len(X["train"][s]), cls[s]) for s in sol])
        mdl = fit_lda(Z, y, len(gn))
        rule["staging"][scheme] = {"classes": gn, "selected_candidate": name,
                                   "features": [names[i] for i in idx], "inner_loso_bal_acc": sc,
                                   "scale": scale.tolist(), "classifier": "LDA (lsqr, Ledoit-Wolf shrinkage, equal priors)",
                                   "coef": mdl.coef_.tolist(), "intercept": mdl.intercept_.tolist(),
                                   "decision": "softmax(coef @ (x/scale) + intercept); UNCERTAIN if max < p_star"}
    (ROOT / "results" / "04" / "frozen_rule.json").write_text(json.dumps(rule, indent=1))
    return rule


def fig_per_solve(per):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.3))
    for a, r in zip(ax, RAT):
        for st_i, stg in enumerate(STAGE_ORDER):
            for k, (sset, mk, col) in enumerate((("v2", "o", "#1c5cab"), ("v1", "s", "#eb6834"))):
                row = per[(per.stage == stg) & (per.set == sset)]
                if len(row):
                    a.errorbar(st_i + (k - 0.5) * 0.18, row[r].values[0], yerr=row[f"{r} noise SD"].values[0],
                               fmt=mk, color=col, ms=5, capsize=3, label=f"{sset} solve" if st_i == 0 else None)
        a.set_xticks(range(len(STAGE_ORDER)), STAGE_ORDER, rotation=30)
        a.set_title(f"{r} (dB)", loc="left", fontsize=9)
        a.grid(True, color="#e4e3de", lw=0.5)
        a.spines[["top", "right"]].set_visible(False)
    ax[0].legend(frameon=False, fontsize=7)
    fig.suptitle("Ratio features per solve (bars = ±1 SD over noisy measurements: typical noise, ±0.5 dB gain)",
                 x=0.01, ha="left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "4_per_solve.png", dpi=150)
    plt.close(fig)


def fig_floor(sweep):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.0))
    ax[0].plot(sweep.floor, sweep["3-class LOSO bal. acc (ratios, LDA)"], "-o", color="#1c5cab", ms=4)
    ax[0].axhline(0.95, color="#8a8981", ls="--", lw=0.8)
    ax[0].set_ylabel("3-class LOSO balanced accuracy")
    ax[1].semilogy(sweep.floor, sweep["R21 gap / per-measurement noise SD"], "-o", color="#1c5cab", ms=4)
    ax[1].axhline(3, color="#8a8981", ls="--", lw=0.8)
    ax[1].set_ylabel("R21 Mild|Severe gap / noise SD")
    for a in ax:
        a.set_xlabel("instrument floor (dB)")
        a.grid(True, color="#e4e3de", lw=0.5)
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "6_floor_sweep.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
