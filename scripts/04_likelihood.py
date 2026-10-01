"""Prompt 04: likelihood / divergence analysis with solve-to-solve variation.

    python scripts/04_likelihood.py [--config config_repeats.yaml] [--n 150] [--no-csv]

Data: the solves in the config's manifest (default: v2 solves + v1 repeats, 3.2-4.2 GHz).
Noise: 'typical' profile + setup perturbation + per-port gain error uniform ±0.5 dB.

Features (one vector per complete measurement, ring-symmetrised):
  k{K}_sb{f}  band power of ring distance K (mean over all equivalent antenna pairs) in each
              50 MHz sub-band, floor-subtracted for K >= 1, in dB
  k{K}_band   the same over the whole band
  R31, R21, R32  geometric-mean path-power ratios C3/C1, C2/C1, C3/C2 (dB; per-port gains cancel)
  N, logN     absorbed (not returned) power, ring mean, linear and dB
Groups: G_refl (k = 0 and N), G_coup (k = 1..3), G_ratio, G_all; plus single features
R31, C3 (= k3_band), C2 (= k2_band) for comparison.

Class model (in units of each feature's pooled measurement-noise SD):
  mean      = average of the class's solve means
  Sigma_c   = Sigma_meas,c   Ledoit-Wolf of the within-solve noise of the class's draws
            + Sigma_b        between-solve covariance from the repeat pairs, d/sqrt(2),
                             shrunk: variances toward their median (Opgen-Rhein & Strimmer),
                             correlations toward 0 (Schafer & Strimmer); pooled over stages
            + Sigma_stage,c  scatter of stage means inside a merged class (AD, Mild+Moderate)
Outputs: results/04/{report.md, divergences.csv, loso.csv, confusion.json, mi.csv,
         shrinkage.csv}, results/04/figures/*.png, rows in results/metrics.csv.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adstage.classes import scheme_groups, scheme_label  # noqa: E402
from adstage.config import load_config  # noqa: E402
from adstage.features.floor import CLIP, floor_power  # noqa: E402
from adstage.features.metrics import band_avg, ring_distance_matrix, to_ring_order  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.noise.model import PROFILES  # noqa: E402
from adstage.noise.reference import mesh_pairs  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.results import append_row, git_hash  # noqa: E402

OUT = ROOT / "results" / "04"
STAGES4 = ["Normal", "Mild", "Moderate", "Severe"]
PRELIM = "preliminary: one head, two solves, 4 repeat pairs"
P_STAR = 0.7


# ============================================================ features: adstage.features.ring_features


# ============================================================ covariance estimators
def ledoit_wolf(Z):
    """Centered samples (m, p) -> (cov, shrinkage) toward scaled identity."""
    from sklearn.covariance import LedoitWolf
    lw = LedoitWolf(assume_centered=True).fit(Z)
    return lw.covariance_, float(lw.shrinkage_)


def shrink_between(W):
    """Zero-mean samples W (P, p) -> (cov, lambda_var, lambda_corr).
    Variances -> median (Opgen-Rhein & Strimmer 2007); correlations -> 0 (Schafer & Strimmer 2005)."""
    P = W.shape[0]
    v = (W ** 2).mean(0)
    nu = np.median(v)
    var_v = ((W ** 2 - v) ** 2).sum(0) / (P * max(P - 1, 1))
    den = ((v - nu) ** 2).sum()
    lam_v = float(np.clip(var_v.sum() / den, 0, 1)) if den > 0 else 1.0
    vs = lam_v * nu + (1 - lam_v) * v
    Y = W / np.sqrt(np.maximum(v, 1e-300))
    R = (Y.T @ Y) / P
    prod = Y[:, :, None] * Y[:, None, :]
    var_r = ((prod - R) ** 2).sum(0) / (P * max(P - 1, 1))
    off = ~np.eye(W.shape[1], dtype=bool)
    den = (R[off] ** 2).sum()
    lam_r = float(np.clip(var_r[off].sum() / den, 0, 1)) if den > 0 else 1.0
    Rs = (1 - lam_r) * R
    np.fill_diagonal(Rs, 1.0)
    sd = np.sqrt(vs)
    return Rs * sd[:, None] * sd[None, :], lam_v, lam_r


def between_cov(data, pairs):
    """Shrunk between-solve covariance from repeat pairs of solve-level draw sets."""
    W = np.array([(data[b].mean(0) - data[a].mean(0)) / np.sqrt(2) for a, b in pairs])
    return shrink_between(W)[0]


# ============================================================ class model
class GaussModel:
    """Fit class Gaussians from solve-level draw sets.

    data: {solve: X (n, p)} in standardized units; cls: {solve: class}; pairs: [(a, b)] repeats.
    stage_of: {solve: stage} (for the within-class stage scatter of merged classes)."""

    def __init__(self, data, cls, stage_of, pairs, use_between=True):
        self.classes = sorted(set(cls.values()), key=lambda c: list(cls.values()).index(c))
        means = {s: X.mean(0) for s, X in data.items()}
        p = next(iter(data.values())).shape[1]
        self.info = {}
        Sb = np.zeros((p, p))
        if use_between:
            W = np.array([(means[b] - means[a]) / np.sqrt(2) for a, b in pairs if a in means and b in means])
            if len(W):
                Sb, lv, lr = shrink_between(W)
                self.info.update(n_pairs=len(W), lambda_var=lv, lambda_corr=lr)
        self.mu, self.cov = {}, {}
        for c in self.classes:
            sols = [s for s in data if cls[s] == c]
            Zc = np.concatenate([data[s] - means[s] for s in sols])
            Sm, d = ledoit_wolf(Zc)
            self.info[f"lw_meas_{c}"] = d
            stage_means = {}
            for s in sols:
                stage_means.setdefault(stage_of[s], []).append(means[s])
            sm = np.array([np.mean(v, 0) for v in stage_means.values()])
            mu = sm.mean(0)                                       # equal weight per stage
            Sst = ((sm - mu).T @ (sm - mu)) / len(sm) if len(sm) > 1 else 0
            self.mu[c] = mu
            self.cov[c] = Sm + Sb + Sst
        self._prep()

    def _prep(self):
        self._inv, self._logdet = {}, {}
        for c, C in self.cov.items():
            sign, ld = np.linalg.slogdet(C)
            self._inv[c] = np.linalg.inv(C)
            self._logdet[c] = ld

    def loglik(self, X):
        out = []
        for c in self.classes:
            d = X - self.mu[c]
            out.append(-0.5 * np.einsum("ij,jk,ik->i", d, self._inv[c], d) - 0.5 * self._logdet[c])
        return np.stack(out, 1)


def divergences(mu1, C1, mu2, C2):
    """Symmetric KL (J) and Bhattacharyya distance between two Gaussians."""
    d = len(mu1)
    i1, i2 = np.linalg.inv(C1), np.linalg.inv(C2)
    dm = mu1 - mu2
    J = 0.5 * (np.trace(i2 @ C1) + np.trace(i1 @ C2) - 2 * d) + 0.5 * dm @ (i1 + i2) @ dm
    Cb = 0.5 * (C1 + C2)
    B = dm @ np.linalg.solve(Cb, dm) / 8 + 0.5 * (np.linalg.slogdet(Cb)[1]
                                                    - 0.5 * np.linalg.slogdet(C1)[1] - 0.5 * np.linalg.slogdet(C2)[1])
    return float(J), float(B)


def softmax(L, T=1.0):
    z = L / T
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def fit_temperature(L, y):
    """Grid search of T minimising the NLL of the true class."""
    Ts = np.exp(np.linspace(np.log(0.05), np.log(200), 200))
    nll = [-np.log(np.clip(softmax(L, T)[np.arange(len(y)), y], 1e-300, 1)).mean() for T in Ts]
    return float(Ts[int(np.argmin(nll))])


def gauss_mi(Xd, solves, stage_of, pairs, j, classes):
    """1-D Gaussian MI (bits) between feature j and class; class c ~ N(mean of its solve means,
    within-solve var + between-solve var from the repeat pairs). Equal priors."""
    m = {s: Xd[s][:, j].mean() for s in solves}
    w = np.mean([Xd[s][:, j].var(ddof=1) for s in solves])
    b = np.mean([(m[bb] - m[a]) ** 2 / 2 for a, bb in pairs if a in m and bb in m])
    mu = np.array([np.mean([m[s] for s in solves if stage_of[s] == c]) for c in classes])
    sd = np.sqrt(w + b)
    x = np.linspace(mu.min() - 8 * sd, mu.max() + 8 * sd, 4001)
    pdf = np.exp(-0.5 * ((x[:, None] - mu) / sd) ** 2)
    pdf /= pdf.sum(0, keepdims=True)                        # each class density on the grid
    mix = pdf.mean(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        post = pdf / (len(classes) * mix[:, None])
        h = -np.nansum(np.where(post > 0, post * np.log2(post), 0), 1)
    return float(np.log2(len(classes)) - (mix * h).sum())


def ece(P, y, bins=10):
    conf, pred = P.max(1), P.argmax(1)
    e = 0.0
    for lo in np.linspace(0, 1, bins + 1)[:-1]:
        m = (conf > lo) & (conf <= lo + 1 / bins)
        if m.any():
            e += m.mean() * abs((pred[m] == y[m]).mean() - conf[m].mean())
    return float(e)


# ============================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config_repeats.yaml")
    ap.add_argument("--n", type=int, default=150, help="noisy draws per solve per split")
    ap.add_argument("--no-csv", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    os.environ["MLI_CONFIG"] = args.config
    cfg = load_config(ROOT)
    gh = git_hash(ROOT)
    (OUT / "figures").mkdir(parents=True, exist_ok=True)

    ds = load_dataset(cfg, ROOT)
    f = ds.f_hz
    S = to_ring_order(ds.S, ds.port_to_ant)
    n_s = len(ds.files)
    stage_of = dict(enumerate(ds.classes))
    pairs = mesh_pairs(ds.files, ds.manifest)
    solve_set = {i: ("v1" if r == "mesh_repeat" else "v2") for i, r in enumerate(ds.manifest["role"])}
    acfg = dict(cfg.get("augment", {}))
    acfg["gain_err_db"] = 0.5
    prof = PROFILES["typical"]
    print(f"code {gh}; {n_s} solves {ds.classes}; band {f[0] / 1e9:.2f}-{f[-1] / 1e9:.2f} GHz; "
          f"repeat pairs {pairs}; {args.n} draws/solve/split")

    X = {"train": {}, "test": {}}
    for s in range(n_s):
        for split, off in (("train", 0), ("test", 1)):
            rng = np.random.default_rng([cfg["seed"], 40, s, off])
            Xs, names, groups, singles = features(f, draws(f, S[s], prof, args.n, rng, acfg))
            X[split][s] = Xs
    feat_sets = {**groups, **singles}
    p = len(names)
    print(f"{p} features; groups " + ", ".join(f"{g}:{len(v)}" for g, v in feat_sets.items()))

    def standardize(train_solves):
        Z = np.concatenate([X["train"][s] - X["train"][s].mean(0) for s in train_solves])
        return Z.std(0, ddof=1)

    # ---------------------------------------------------------------- divergences (all data)
    sc_all = standardize(range(n_s))
    data_all = {s: X["train"][s] / sc_all for s in range(n_s)}
    div_rows, shrink_rows = [], []
    for gname, idx in feat_sets.items():
        D = {s: data_all[s][:, idx] for s in range(n_s)}
        for use_b in (False, True):
            stage_cls = {s: c for s, c in stage_of.items() if c in STAGES4 + ["MCI"]}
            gm = GaussModel(D, stage_cls, stage_of, pairs, use_between=use_b)
            if use_b:
                shrink_rows.append({"group": gname, "dim": len(idx), **gm.info})
            tag = "with_between" if use_b else "meas_only"
            for a, b in itertools.combinations(STAGES4, 2):
                J, B = divergences(gm.mu[a], gm.cov[a], gm.mu[b], gm.cov[b])
                div_rows.append({"group": gname, "pair": f"{a}|{b}", "cov": tag, "J": J, "B": B})
            # binary Normal | AD as a merged class
            bcls = {s: ("Normal" if c == "Normal" else "AD") for s, c in stage_of.items() if c in STAGES4}
            gb = GaussModel({s: D[s] for s in bcls}, bcls, stage_of, pairs, use_between=use_b)
            J, B = divergences(gb.mu["Normal"], gb.cov["Normal"], gb.mu["AD"], gb.cov["AD"])
            div_rows.append({"group": gname, "pair": "Normal|AD", "cov": tag, "J": J, "B": B})
            # MCI vs Normal, and the two solves of the same stage (solve-to-solve reference)
            J, B = divergences(gm.mu["MCI"], gm.cov["MCI"], gm.mu["Normal"], gm.cov["Normal"])
            div_rows.append({"group": gname, "pair": "MCI|Normal", "cov": tag, "J": J, "B": B})
            for a, b in pairs:                    # between-solve term from the OTHER pairs only
                sb = between_cov(D, [q for q in pairs if q != (a, b)]) if use_b else 0
                Ca = ledoit_wolf(D[a] - D[a].mean(0))[0] + sb
                Cb = ledoit_wolf(D[b] - D[b].mean(0))[0] + sb
                J, B = divergences(D[a].mean(0), Ca, D[b].mean(0), Cb)
                div_rows.append({"group": gname, "pair": f"repeat:{stage_of[a]}", "cov": tag, "J": J, "B": B})
    div = pd.DataFrame(div_rows)
    div.to_csv(OUT / "divergences.csv", index=False)
    shrink = pd.DataFrame(shrink_rows)

    # ---------------------------------------------------------------- leave-one-solve-out
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score
    schemes = ["binary", "three_merged", "three"]
    loso_rows, cms, fold_shrink = [], {}, []
    for scheme in schemes:
        gst = scheme_groups(cfg, scheme)
        gnames = list(gst)
        cls = {s: g for s, c in stage_of.items() for g, st in gst.items() if c in st}
        solves = sorted(cls)
        y_of = {s: gnames.index(cls[s]) for s in solves}
        held = [s for s in solves if sum(cls[t] == cls[s] for t in solves) >= 2]
        for gname, idx in feat_sets.items():
            res = {m: {"y": [], "P": []} for m in ("QDA+between", "QDA meas-only", "LDA")}
            for s_out in held:
                tr = [s for s in solves if s != s_out]
                sc = standardize(tr)[idx]
                Dtr = {s: X["train"][s][:, idx] / sc for s in tr}
                Xte = X["test"][s_out][:, idx] / sc
                yte = np.full(len(Xte), y_of[s_out])
                tr_pairs = [(a, b) for a, b in pairs if s_out not in (a, b)]
                for mname, use_b in (("QDA+between", True), ("QDA meas-only", False)):
                    gm = GaussModel(Dtr, {s: cls[s] for s in tr}, stage_of, tr_pairs, use_between=use_b)
                    if use_b and gname in ("G_all", "G_coup", "G_ratio", "G_refl"):
                        fold_shrink.append({"scheme": scheme, "group": gname, "held_out": ds.files[s_out], **gm.info})
                    # temperature from an inner leave-one-solve-out inside the training solves
                    Lin, yin = [], []
                    for s_in in tr:
                        if sum(cls[t] == cls[s_in] for t in tr) < 2:
                            continue
                        tr2 = [t for t in tr if t != s_in]
                        gi = GaussModel({t: Dtr[t] for t in tr2}, {t: cls[t] for t in tr2}, stage_of,
                                        [(a, b) for a, b in tr_pairs if s_in not in (a, b)], use_between=use_b)
                        Lin.append(gi.loglik(Dtr[s_in]))
                        yin.append(np.full(len(Dtr[s_in]), gnames.index(cls[s_in])))
                    T = fit_temperature(np.concatenate(Lin), np.concatenate(yin)) if Lin else 1.0
                    order = [gnames.index(c) for c in gm.classes]
                    L = np.empty((len(Xte), len(gnames)))
                    L[:, order] = gm.loglik(Xte)
                    res[mname]["y"].append(yte)
                    res[mname]["P"].append(softmax(L, T))
                Ztr = np.concatenate(list(Dtr.values()))
                ytr = np.concatenate([np.full(len(Dtr[s]), y_of[s]) for s in tr])
                solver = "lsqr" if len(idx) > 1 else "svd"
                lda = LinearDiscriminantAnalysis(solver=solver, shrinkage="auto" if solver == "lsqr" else None,
                                                 priors=np.full(len(gnames), 1 / len(gnames))).fit(Ztr, ytr)
                res["LDA"]["y"].append(yte)
                res["LDA"]["P"].append(lda.predict_proba(Xte))
            for mname, r in res.items():
                y = np.concatenate(r["y"])
                P = np.concatenate(r["P"])
                pred = P.argmax(1)
                acc_m = P.max(1) >= P_STAR
                ba_acc = (balanced_accuracy_score(y[acc_m], pred[acc_m])
                          if acc_m.sum() and len(np.unique(y[acc_m])) == len(gnames) else np.nan)
                cm = confusion_matrix(y, pred, labels=range(len(gnames)))
                cms[f"{scheme}|{gname}|{mname}"] = {"classes": gnames, "cm": cm.tolist()}
                loso_rows.append({"scheme": scheme, "features": gname, "dim": len(idx), "classifier": mname,
                                  "n_folds": len(held), "n_test": len(y),
                                  "balanced_accuracy": balanced_accuracy_score(y, pred),
                                  "accuracy": float((pred == y).mean()),
                                  "macro_f1": f1_score(y, pred, average="macro"),
                                  "reject_rate": float(1 - acc_m.mean()), "bal_acc_on_accepted": ba_acc,
                                  "ece": ece(P, y)})
    loso = pd.DataFrame(loso_rows)
    loso.to_csv(OUT / "loso.csv", index=False)
    (OUT / "confusion.json").write_text(json.dumps(cms, indent=1))
    fold_sh = pd.DataFrame(fold_shrink)
    shrink_all = pd.concat([shrink.assign(fit="all data"),
                            fold_sh.groupby(["group"])[["lambda_var", "lambda_corr", "n_pairs"]].agg(["min", "max"])
                            .pipe(lambda d: d.set_axis(["_".join(c) for c in d.columns], axis=1)).reset_index()
                            .assign(fit="LOSO folds (min/max)")], ignore_index=True)
    shrink_all.to_csv(OUT / "shrinkage.csv", index=False)

    # ---------------------------------------------------------------- mutual information
    from sklearn.feature_selection import mutual_info_classif
    st4 = [s for s in range(n_s) if stage_of[s] in STAGES4]

    def mi(solves, classes_map):
        Z = np.concatenate([X["train"][s] for s in solves])
        y = np.concatenate([np.full(args.n, classes_map(stage_of[s])) for s in solves])
        return mutual_info_classif(Z, y, n_neighbors=3, random_state=cfg["seed"]) / np.log(2)

    stage_y = lambda c: STAGES4.index(c)          # noqa: E731
    bin_y = lambda c: int(c != "Normal")          # noqa: E731
    v1 = [s for s in st4 if solve_set[s] == "v1"]
    v2 = [s for s in st4 if solve_set[s] == "v2"]
    mi_df = pd.DataFrame({"feature": names,
                          "MI_stage_pooled_bits": mi(st4, stage_y),
                          "MI_stage_v2only_bits": mi(v2, stage_y),
                          "MI_stage_v1only_bits": mi(v1, stage_y),
                          "MI_binary_pooled_bits": mi(st4, bin_y)})
    one = mi_df[["MI_stage_v2only_bits", "MI_stage_v1only_bits"]].mean(1)
    mi_df["solve_specific_fraction"] = np.clip(1 - mi_df.MI_stage_pooled_bits / one.replace(0, np.nan), 0, 1)
    mi_df["group"] = [next(g for g in ("G_refl", "G_coup", "G_ratio") if i in groups[g]) for i in range(p)]
    # Gaussian MI per feature with class spread = within-solve + between-solve variance (1-D model):
    # information a NEW solve would still carry, unlike the kNN estimate on pooled solve clusters.
    mi_df["MI_stage_gauss_between_bits"] = [gauss_mi(X["train"], st4, stage_of, pairs, j, STAGES4) for j in range(p)]
    mi_df.to_csv(OUT / "mi.csv", index=False)

    # per-solve values of the calibration-free ratios and band powers (dB), for inspection
    show = ["R31", "R21", "R32", "k1_band", "k2_band", "k3_band", "logN"]
    per_solve = pd.DataFrame([{"solve": ds.files[s].split("/")[-1], "stage": stage_of[s], "set": solve_set[s],
                               **{nm: float(np.concatenate([X["train"][s], X["test"][s]])[:, names.index(nm)].mean())
                                  for nm in show}} for s in range(n_s)])
    per_solve.to_csv(OUT / "per_solve_values.csv", index=False)

    report(gh, cfg, ds, names, feat_sets, div, shrink_all, loso, cms, mi_df, args, per_solve, pairs)
    figures(div, mi_df, names)
    if not args.no_csv:
        log_rows(cfg, gh, loso, div, ds, stage_of)
    print((OUT / "report.md").read_text(encoding="utf-8"))


# ============================================================ outputs
def md(df, fmt=".3g"):
    def cell(v):
        if isinstance(v, (float, np.floating)):
            return "n/a" if not np.isfinite(v) else format(v, fmt)
        return str(v)
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    return "\n".join([head, sep] + ["| " + " | ".join(cell(v) for v in r) + " |" for r in df.itertuples(index=False)])


def report(gh, cfg, ds, names, feat_sets, div, shrink, loso, cms, mi_df, args, per_solve, pairs):
    L = [f"# Prompt 04 - likelihood / divergence analysis (code {gh})", "",
         f"Solves: {dict(zip(ds.files, ds.classes))}. Band {ds.f_hz[0] / 1e9:.2f}-{ds.f_hz[-1] / 1e9:.2f} GHz. "
         f"Noise: typical + setup perturbation + per-port gain ±0.5 dB; {args.n} draws per solve per split "
         "(train/test seeds differ). One head geometry throughout. Every 3-class number is "
         f"**{PRELIM}**. MCI has one solve: no classification claim.", "",
         "Feature groups: " + ", ".join(f"{g} ({len(v)})" for g, v in feat_sets.items()) + ". Units: each "
         "feature divided by its pooled within-solve (measurement-noise) SD.", "",
         "## Shrinkage", "Measurement covariance: Ledoit-Wolf toward scaled identity (lw_meas_*). Between-solve "
         "covariance from the repeat pairs (d/sqrt2): variances toward their median (lambda_var), correlations "
         "toward 0 (lambda_corr); 1 = fully shrunk.", md(shrink.fillna(np.nan), ".3f"), ""]
    tab = div.pivot_table(index=["group", "pair"], columns="cov", values=["J", "B"]).reset_index()
    tab.columns = ["group", "pair"] + [f"{a}_{b}" for a, b in tab.columns[2:]]
    tab["B_kept_%"] = 100 * tab["B_with_between"] / tab["B_meas_only"]
    order = ["Normal|AD", "Normal|Mild", "Normal|Moderate", "Normal|Severe", "Mild|Moderate", "Mild|Severe",
             "Moderate|Severe", "MCI|Normal", "repeat:Normal", "repeat:Mild", "repeat:Moderate", "repeat:Severe"]
    tab["o"] = tab.pair.map({p: i for i, p in enumerate(order)})
    tab = tab.sort_values(["group", "o"]).drop(columns="o")
    L += ["## Divergences: symmetric KL (J) and Bhattacharyya (B), without and with the between-solve term",
          "meas_only = measurement noise only (the apparent information); with_between = plus solve-to-solve "
          "covariance. B_kept_% = share of the apparent Bhattacharyya distance that survives. 'repeat:X' = the "
          "two solves of the same stage X, i.e. pure solve-to-solve difference (a class pair should beat it). "
          "Bhattacharyya B -> Bayes error bound 0.5·exp(-B).",
          md(tab[["group", "pair", "J_meas_only", "J_with_between", "B_meas_only", "B_with_between", "B_kept_%"]], ".3g"), ""]
    L += ["## Leave-one-solve-out classification",
          "Each fold holds out one solve (all its test draws); the model is fitted on the other solves only "
          "(means, covariances, between-solve pairs not involving the held-out solve, standardisation, "
          "temperature by inner leave-one-solve-out). Reject = max posterior < 0.7. ECE = expected "
          "calibration error of the max posterior.", ""]
    for scheme in ["binary", "three_merged", "three"]:
        t = loso[loso.scheme == scheme].sort_values("balanced_accuracy", ascending=False)
        lab = "" if scheme == "binary" else f" ({PRELIM})"
        L += [f"### `{scheme}`{lab}",
              md(t[["features", "dim", "classifier", "balanced_accuracy", "reject_rate", "bal_acc_on_accepted",
                    "ece", "n_folds"]], ".3f"), ""]
        best = t.iloc[0]
        c = cms[f"{scheme}|{best.features}|{best.classifier}"]
        L += [f"Confusion matrix, best row ({best.features}, {best.classifier}); rows = true {c['classes']}: "
              f"`{c['cm']}`", ""]
    L += ["## Per-solve values of the ratio and band-power features (dB, mean over noisy draws)",
          "R32 = R31 - R21 exactly (same geometric means), so G_ratio has rank 2. Solve-to-solve SD per "
          "feature = rms over the repeat pairs of (difference / sqrt 2).",
          md(per_solve, ".2f"), ""]
    sd_rows = []
    for nm in ["R31", "R21", "R32", "k2_band", "k3_band"]:
        v = per_solve[nm].values
        sd = float(np.sqrt(np.mean([(v[b] - v[a]) ** 2 / 2 for a, b in pairs])))
        mean = per_solve.groupby("stage")[nm].mean()
        sd_rows.append({"feature": nm, "solve_SD_dB": sd,
                        **{f"{a}|{b} gap/SD": abs(mean[a] - mean[b]) / sd for a, b in
                           [("Normal", "Mild"), ("Mild", "Moderate"), ("Mild", "Severe"), ("Moderate", "Severe"),
                            ("Normal", "MCI")]}})
    L += ["Stage gaps in units of the solve-to-solve SD (stage means over solves):",
          md(pd.DataFrame(sd_rows), ".2f"), ""]
    top = mi_df.sort_values("MI_stage_gauss_between_bits", ascending=False).head(15)
    L += ["## Mutual information with the stage (Normal / Mild / Moderate / Severe), bits (max 2)",
          "**MI_stage_gauss_between** (ranking key): 1-D Gaussian class model whose spread includes the "
          "between-solve variance, i.e. the information a new solve would still carry. "
          "MI_stage_pooled (kNN, both solves pooled) is NOT a cross-solve measure: it is high whenever the "
          "8 solve clusters are separable by class, even if a new solve would land elsewhere. "
          "v2only / v1only = one solve per stage (kNN).",
          md(top[["feature", "group", "MI_stage_gauss_between_bits", "MI_stage_pooled_bits", "MI_stage_v2only_bits",
                   "MI_stage_v1only_bits", "MI_binary_pooled_bits"]], ".3f"), "",
          "By group (mean over features):",
          md(mi_df.groupby("group")[["MI_stage_gauss_between_bits", "MI_stage_pooled_bits", "MI_stage_v2only_bits",
                                     "MI_stage_v1only_bits", "MI_binary_pooled_bits"]].mean().reset_index(), ".3f"), ""]
    kk = mi_df[mi_df.feature.str.contains("_sb")].assign(k=lambda d: d.feature.str[1].astype(int))
    L += ["By ring distance (sub-band features, mean MI):",
          md(kk.groupby("k")[["MI_stage_gauss_between_bits", "MI_stage_pooled_bits", "MI_stage_v2only_bits"]].mean().reset_index(), ".3f"), ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")


def figures(div, mi_df, names):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlelocation": "left", "axes.titlesize": 9})
    groups = ["G_refl", "G_coup", "G_ratio", "G_all", "R31", "C3", "C2"]
    pairs = ["Normal|AD", "Mild|Severe", "Mild|Moderate", "MCI|Normal", "repeat:Normal"]
    fig, ax = plt.subplots(1, len(pairs), figsize=(3.0 * len(pairs), 3.0), sharey=True)
    for a, pr in zip(ax, pairs):
        t = div[div.pair == pr].pivot_table(index="group", columns="cov", values="B").reindex(groups)
        x = np.arange(len(groups))
        a.bar(x - 0.2, t["meas_only"], 0.38, color="#86b6ef", label="measurement noise only")
        a.bar(x + 0.2, t["with_between"], 0.38, color="#1c5cab", label="+ between-solve")
        a.set_yscale("log")
        a.set_xticks(x, groups, rotation=45, ha="right")
        a.set_title(pr)
        a.axhline(np.log(2), color="#8a8981", lw=0.8, ls="--")
    ax[0].set_ylabel("Bhattacharyya distance (log)")
    ax[0].legend(frameon=False, fontsize=7)
    fig.suptitle("How much separation survives solve-to-solve variation (dashed: B = ln 2, Bayes error bound 25%)",
                 x=0.01, ha="left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "04_divergence.png", dpi=150)
    plt.close(fig)

    kk = mi_df[mi_df.feature.str.contains("_sb")].copy()
    kk["k"] = kk.feature.str[1].astype(int)
    kk["sb"] = kk.feature.str.split("_sb").str[1].astype(float)
    fig, ax = plt.subplots(1, 2, figsize=(11, 2.8), sharey=True)
    for a, col, title in ((ax[0], "MI_stage_v2only_bits", "One solve per stage (v2 only, kNN)"),
                          (ax[1], "MI_stage_gauss_between_bits", "With between-solve variance (survives a new solve)")):
        M = kk.pivot_table(index="k", columns="sb", values=col)
        im = a.imshow(M.values, aspect="auto", cmap="Blues", vmin=0, vmax=2, origin="lower")
        a.set_xticks(range(M.shape[1])[::2], [f"{v:.2f}" for v in M.columns][::2], rotation=45)
        a.set_yticks(range(4), ["k0 refl", "k1 neigh", "k2 2nd", "k3 opp"])
        a.set_title(title)
        a.set_xlabel("sub-band start (GHz)")
    fig.colorbar(im, ax=ax, shrink=0.8, label="MI with stage (bits, max 2)")
    fig.savefig(OUT / "figures" / "04_mi_map.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def log_rows(cfg, gh, loso, div, ds, stage_of):
    for r in loso.itertuples(index=False):
        gst = scheme_groups(cfg, r.scheme)
        nspc = "|".join(f"{g}:{sum(c in st for c in stage_of.values())}" for g, st in gst.items())
        notes = ["cross-solve-same-head", f"ECE={r.ece:.3f}", "noise=typical+setup+gain±0.5dB",
                 "Gaussian class model: Sigma_meas(LW)+Sigma_between(shrunk)+stage scatter"]
        if r.scheme != "binary":
            notes.insert(0, PRELIM)
        append_row(ROOT / cfg["results"]["metrics_csv"], {
            "git_hash": gh, "track": cfg["track"], "model_id": cfg["model_id"],
            "sim_set": cfg["metrics"]["sim_set"], "classes": scheme_label(cfg, r.scheme),
            "method_id": f"L:{r.features}", "feature_desc": f"prompt04 {r.features} (ring-symmetrised, 3.2-4.2 GHz)",
            "feature_dim": r.dim, "classifier": r.classifier, "noise_profile": "typical+gain0.5dB",
            "cv_scheme": "LOSO (solve)", "n_sims_per_class": nspc, "n_test": r.n_test,
            "accuracy": r.accuracy, "balanced_accuracy": r.balanced_accuracy, "macro_f1": r.macro_f1,
            "reject_rate": r.reject_rate, "accuracy_on_accepted": r.bal_acc_on_accepted,
            "notes": "; ".join(notes)})


if __name__ == "__main__":
    main()
