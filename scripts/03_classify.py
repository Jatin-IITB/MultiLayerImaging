"""Prompt 03: quality gate, augmentation, classifiers, explicit decision boundaries.

Usage:  python scripts/03_classify.py [--profiles typical,good] [--no-csv] [--include-moderate]
Re-runs on whatever data/sims.csv lists: schemes with an empty class are skipped, the CV scheme
(LOSO vs leave-one-diameter-out) is chosen from simulation counts, and the noise reference
switches from port-to-port to between-mesh when mesh_repeat rows exist.
Writes: results/metrics.csv (append), results/03/*.csv|md, results/figures/03_*.png
"""
from __future__ import annotations

import argparse
import os
import sys
import warnings
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adstage.classes import active_schemes, pair_is_ad_only, scheme_groups, scheme_label  # noqa: E402
from adstage.features.metrics import build_catalogue, to_ring_order  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.noise.model import PROFILES  # noqa: E402
from adstage.noise.reference import mesh_pairs, mesh_sd, reference_label  # noqa: E402
from adstage.pipeline import classify as C  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.pipeline.cv import make_folds, validity_label  # noqa: E402
from adstage.pipeline.quality import REASONS, QualityGate  # noqa: E402
from adstage.results import append_row, git_hash  # noqa: E402
from adstage.robustness import _fault  # noqa: E402

OUT = ROOT / "results" / "03"
FIG = ROOT / "results" / "figures"
STAGE_COLOR = {"Normal": "#86b6ef", "MCI": "#5598e7", "Mild": "#2a78d6", "Moderate": "#1c5cab",
               "Severe": "#0d366b"}
HEADLINE_SETS = ("M0", "M5.C3", "M5.C3[k3]", "M5.C3[nested]")


# ============================================================ per-profile worker
def run_profile(pname, cfg, include_moderate, feature_sets, models):
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    ccfg, acfg = cfg["classify"], cfg.get("augment", {})
    pi = list(PROFILES).index(pname)
    prof = PROFILES[pname]
    ds = load_dataset(cfg, ROOT)
    f = ds.f_hz
    S = to_ring_order(ds.S, ds.port_to_ant)
    n_sims, N = S.shape[0], S.shape[-1]
    metrics, bands = build_catalogue(f, tuple(float(v) for v in cfg["metrics"]["k3_band_hz"]),
                                     float(cfg["metrics"]["subband_hz"]))
    subbands = [bands[b] for b in bands if b.startswith("sb")]
    ref_sims = [s for s in range(n_sims) if ds.classes[s] == cfg["classes"]["reference"]]
    gate = QualityGate(cfg["gate"], f)

    # ---- draws and features (train and test draws use different seeds) ----
    feats, gate_inv, gate_train = {}, {}, []
    for s in range(n_sims):
        feats[s] = {}
        for split, off in (("train", 0), ("test", 1)):
            rng = np.random.default_rng([cfg["seed"], 3, pi, s, off])
            n = int(ccfg[f"n_{split}_draws"])
            D = draws(f, S[s], prof, n, rng, acfg)
            feats[s][split] = C.extract(f, D, metrics, bands, subbands)
            if split == "train" and s in ref_sims:
                gate_train.append(D)
            if split == "test":
                feats[s]["test_D"] = D
    gate.fit_detune(np.concatenate(gate_train))
    for s in range(n_sims):
        gate_inv[s] = gate.check(feats[s].pop("test_D"))["invalid"]

    # ---- gate evaluation on prompt-02 perturbations ----
    gate_rows = []
    cases = {"clean": lambda X, r: X}
    for d in (-20, -10, -5, -2, 2, 5, 10, 20):
        cases[f"shift{d:+d}MHz"] = (lambda d: lambda X, r: _shift(f, X, d))(d)
    cases["flatten_notch"] = lambda X, r: _flatten_ring(f, X)
    for d in (-200, 200):
        cases[f"detune{d:+d}MHz"] = (lambda d: lambda X, r: _shift(f, X, d))(d)
    cases["one_open"] = lambda X, r: _fault(X, "open", r, [0])
    cases["one_short"] = lambda X, r: _fault(X, "short", r, [0])
    cases["open_all"] = lambda X, r: _fault(X, "open", r)
    cases["short_all"] = lambda X, r: _fault(X, "short", r)
    for cname, fn in cases.items():
        res = []
        for s in range(n_sims):
            rng = np.random.default_rng([cfg["seed"], 4, pi, s])
            res.append(gate.check(draws(f, fn(S[s], rng), prof, 40, rng, acfg)))
        row = {"profile": pname, "case": cname,
               "invalid_rate": float(np.mean(np.concatenate([r["invalid"] for r in res])))}
        for reason in REASONS:
            row[reason] = float(np.mean(np.concatenate([r[reason] for r in res])))
        gate_rows.append(row)

    # ---- classification ----
    stages = ds.classes
    schemes, _ = active_schemes(cfg, stages, include_moderate)
    head_ids = list(ds.manifest["head_id"])
    ctx = {"f": f, "subbands": subbands, "ref_sims": ref_sims,
           "window_lengths": [int(w // 50) for w in ccfg["nested_window_widths_mhz"]],
           "comb_max": int(ccfg["comb_max_features"]), "comb_corr": float(ccfg["comb_max_corr"])}
    result_rows, head_preds = [], []
    for scheme in schemes:
        gst = scheme_groups(cfg, scheme)
        groups = {g: [s for s in range(n_sims) if stages[s] in st] for g, st in gst.items()}
        gnames = list(groups)
        lab = {s: gnames.index(g) for g, v in groups.items() for s in v}
        cv_name, folds = make_folds(groups, N)
        validity = validity_label(groups, head_ids)
        K = len(gnames)
        for fs in feature_sets:
            per_model = {m: [] for m in models}
            infos = []
            for fi, fold in enumerate(folds):
                ytr = np.concatenate([np.full(len(v) * feats[s]["train"]["c3sb"].shape[0], lab[s])
                                      for s, v in fold.train])
                gtr = np.concatenate([np.repeat([s * N + t for t in v], feats[s]["train"]["c3sb"].shape[0])
                                      for s, v in fold.train])
                Xtr, Xte, info = C.build_features(fs, feats, fold.train, fold.test, ytr, ctx)
                infos.append(info)
                nte = [feats[s]["test"]["c3sb"].shape[0] for s, _ in fold.test]
                yte = np.concatenate([np.full(len(v) * n, lab[s]) for (s, v), n in zip(fold.test, nte)])
                ste = np.concatenate([np.full(len(v) * n, s) for (s, v), n in zip(fold.test, nte)])
                inv = np.concatenate([np.tile(gate_inv[s], len(v)) for s, v in fold.test])
                for mname in models:
                    if mname == "THR" and (Xtr.shape[1] != 1 or K != 2):
                        continue
                    model = C.make_model(mname, Xtr.shape[1], K, list(map(float, ccfg["lr_Cs"])), cfg["seed"])
                    C.fit_model(model, Xtr, ytr, gtr)
                    cal = C.calibrate(model, Xtr, ytr, gtr, cfg["seed"])
                    pred = model.predict(Xte)
                    proba = cal.predict_proba(C.scores(model, Xte))
                    rec = {"y": yte, "pred": pred, "proba": proba, "sim": ste, "invalid": inv,
                           "fold": np.full(len(yte), fi)}
                    if Xte.shape[1] == 1:
                        rec["x"] = Xte[:, 0]
                    if mname == "THR":
                        rec["tau"] = model.steps[-1][1].tau_
                    per_model[mname].append(rec)
            for mname, recs in per_model.items():
                if not recs:
                    continue
                cat = {k: np.concatenate([r[k] for r in recs]) for k in ("y", "pred", "proba", "sim", "invalid", "fold")}
                if "x" in recs[0]:
                    cat["x"] = np.concatenate([r["x"] for r in recs])
                ev = evaluate(cat, K, float(ccfg["p_star"]))
                ad_only = any(pair_is_ad_only(gst, a, b) for i, a in enumerate(gnames) for b in gnames[i + 1:])
                result_rows.append({
                    "profile": pname, "scheme": scheme, "feature_set": fs, "model": mname,
                    "cv_scheme": cv_name, "validity": validity, "n_folds": len(folds),
                    "feature_dim": _dim(fs, infos),
                    "classes": gnames, "n_sims_per_class": "|".join(f"{g}:{len(v)}" for g, v in groups.items()),
                    "ad_only_pairs": ad_only, "info": _info_str(infos), **ev})
                if scheme == cfg["classify"]["headline_scheme"] and fs in HEADLINE_SETS:
                    head_preds.append({"profile": pname, "feature_set": fs, "model": mname,
                                       "taus": [r.get("tau") for r in recs], **cat,
                                       "stage": np.array(stages)[cat["sim"]]})

    # ---- headline feature values (all draws, all views) for thresholds ----
    hv = {}
    for fs in (cfg["classify"]["headline_feature"], cfg["classify"]["secondary_feature"]):
        hv[fs] = {s: np.concatenate([feats[s][sp]["scal"][fs].ravel() for sp in ("train", "test")])
                  for s in range(n_sims)}
    sim_gap = {fs: [float(np.mean(feats[s]["train"]["scal"][fs])) for s in range(n_sims)] for fs in hv}
    return {"profile": pname, "rows": result_rows, "gate": gate_rows, "head_preds": head_preds,
            "hv": hv, "stages": stages, "sim_means": sim_gap}


def _dim(fs, infos):
    if fs in C.FAMILIES:
        return len(C.FAMILIES[fs])
    return {"M5.C3[nested]": 1, "M6": 22, "M7": 6, "COMB": len(infos[0].get("chosen", [])) if infos else 3,
            "M9": 3618}.get(fs, np.nan)


def _info_str(infos):
    if not infos or not infos[0]:
        return ""
    if "window_GHz" in infos[0]:
        w = pd.Series([f"{a:.2f}-{b:.2f}" for a, b in (i["window_GHz"] for i in infos)]).value_counts()
        return "windows " + ", ".join(f"{k}×{v}" for k, v in w.items())
    if "chosen" in infos[0]:
        w = pd.Series(["+".join(i["chosen"]) for i in infos]).value_counts()
        return "chosen " + "; ".join(f"{k}×{v}" for k, v in w.items())
    return ""


def _shift(f, S, d_mhz):
    from adstage.noise.model import shift_spectrum
    return shift_spectrum(f, S, d_mhz * 1e6)


def _flatten_ring(f, S):
    from adstage.robustness import _flatten
    return _flatten(f, S)


def evaluate(cat, K, p_star):
    from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score
    v = ~cat["invalid"]
    y, p, pr = cat["y"][v], cat["pred"][v], cat["proba"][v]
    cm = confusion_matrix(y, p, labels=range(K))
    acc = float((y == p).mean())
    bal = float(balanced_accuracy_score(y, p))
    mf1 = float(f1_score(y, p, average="macro", labels=range(K), zero_division=0))
    conf = pr.max(1)
    pc = pr.argmax(1)
    acc_m = conf >= p_star
    rej = float(1 - acc_m.mean())
    bal_acc_on = (float(balanced_accuracy_score(y[acc_m], pc[acc_m]))
                  if acc_m.sum() and len(np.unique(y[acc_m])) == K else np.nan)
    return {"n_test": int(v.sum()), "gate_invalid_rate": float(cat["invalid"].mean()),
            "accuracy": acc, "balanced_accuracy": bal, "macro_f1": mf1, "reject_rate": rej,
            "bal_acc_on_accepted": bal_acc_on, "cm": cm.tolist()}


# ============================================================ decision boundaries (binary)
def thresholds(hv, groups, p_star, prior_normal, n_boot, seed, mesh_sd_db=np.nan):
    """Binary τ (Normal | AD) on the headline feature in dB, one antenna view per sample.

    tau        class-balanced (equal priors) error minimiser, orientation automatic
    tau_screen minimiser of P(N)·FPR + P(AD)·FNR with P(N) = prior_normal
    CI         bootstrap over simulations (within class), then views/draws
    margin     m = max(m_post, z·σ_ref), z = Φ^-1(p*). m_post: half-width of the zone where the
               class-balanced logistic posterior is below p*. σ_ref: pooled within-simulation
               SD of a single view (measurement noise, setup variation, port asymmetry), plus
               the between-mesh SD in quadrature once it has been measured. A measurement
               within m of τ has more than a 1 - p* chance of being on the wrong side because of
               the noise we know about, so the rule outputs UNCERTAIN.
    """
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(seed)
    gN = groups["Normal"]
    gA = [s for g, v in groups.items() if g != "Normal" for s in v]
    db = {s: 10 * np.log10(v) for s, v in hv.items()}

    def pool(sims, boot):
        xs = []
        for s in (rng.choice(sims, len(sims)) if boot else sims):
            xs.append(rng.choice(db[s], len(db[s])) if boot else db[s])
        return np.concatenate(xs)

    def taus(xn, xa):
        t = C.Threshold1D().fit(np.r_[xn, xa][:, None], np.r_[np.zeros(len(xn)), np.ones(len(xa))])
        cand = np.quantile(np.r_[xn, xa], np.linspace(0, 1, 1001))
        sgn = t.sign_
        fpr = (sgn * xn[:, None] > sgn * cand).mean(0)
        fnr = (sgn * xa[:, None] <= sgn * cand).mean(0)
        return t.tau_, cand[np.argmin(prior_normal * fpr + (1 - prior_normal) * fnr)], sgn

    xn, xa = pool(gN, False), pool(gA, False)
    tau, tau_s, sgn = taus(xn, xa)
    lr = LogisticRegression(class_weight="balanced", C=1e4, max_iter=3000).fit(
        np.r_[xn, xa][:, None], np.r_[np.zeros(len(xn)), np.ones(len(xa))])
    m_post = np.log(p_star / (1 - p_star)) / abs(lr.coef_[0, 0])
    sd_within = float(np.sqrt(np.mean([np.var(db[s], ddof=1) for s in db])))
    sd_ref = float(np.sqrt(sd_within ** 2 + (0 if not np.isfinite(mesh_sd_db) else mesh_sd_db ** 2)))
    from scipy.stats import norm
    margin = max(m_post, norm.ppf(p_star) * sd_ref)
    boots = np.array([taus(pool(gN, True), pool(gA, True))[:2] for _ in range(n_boot)])
    allx = np.r_[xn, xa]
    unc = np.abs(allx - tau) < margin
    acc_n = ~unc[:len(xn)]
    acc_a = ~unc[len(xn):]
    return {"tau_dB": tau, "tau_CI_lo": np.percentile(boots[:, 0], 2.5),
            "tau_CI_hi": np.percentile(boots[:, 0], 97.5), "tau_screen_dB": tau_s,
            "tau_screen_CI_lo": np.percentile(boots[:, 1], 2.5),
            "tau_screen_CI_hi": np.percentile(boots[:, 1], 97.5),
            "margin_dB": margin, "margin_post_dB": m_post, "sd_ref_dB": sd_ref,
            "sd_within_dB": sd_within, "mesh_sd_dB": mesh_sd_db,
            "mu_Normal_dB": float(xn.mean()), "mu_AD_dB": float(xa.mean()),
            "sensitivity": float((sgn * xa > sgn * tau).mean()),
            "specificity": float((sgn * xn <= sgn * tau).mean()),
            "sens_on_accepted": float((sgn * xa[acc_a] > sgn * tau).mean()) if acc_a.any() else np.nan,
            "spec_on_accepted": float((sgn * xn[acc_n] <= sgn * tau).mean()) if acc_n.any() else np.nan,
            "uncertain_fraction": float(unc.mean()),
            "orientation": "AD if x < tau" if sgn < 0 else "AD if x > tau"}


# ============================================================ main
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", default=",".join(PROFILES))
    ap.add_argument("--feature-sets", default=None)
    ap.add_argument("--models", default=None)
    ap.add_argument("--include-moderate", action="store_true")
    ap.add_argument("--no-csv", action="store_true")
    ap.add_argument("--n-jobs", type=int, default=None)
    args = ap.parse_args()
    warnings.filterwarnings("ignore")
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    ccfg = cfg["classify"]
    fsets = args.feature_sets.split(",") if args.feature_sets else list(ccfg["feature_sets"])
    models = args.models.split(",") if args.models else list(ccfg["models"])
    profiles = args.profiles.split(",")
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)
    ds = load_dataset(cfg, ROOT)
    schemes, skipped = active_schemes(cfg, ds.classes, args.include_moderate)
    pairs = mesh_pairs(ds.files, ds.manifest)
    noise_ref = reference_label(pairs)
    print(f"code {gh}; sims {ds.classes}; schemes {schemes}; skipped {skipped}; noise ref {noise_ref}")

    res = Parallel(n_jobs=min(args.n_jobs or int(ccfg["n_jobs"]), len(profiles)), verbose=5)(
        delayed(run_profile)(p, cfg, args.include_moderate, fsets, models) for p in profiles)

    rows = pd.DataFrame([r for x in res for r in x["rows"]])
    gate = pd.DataFrame([r for x in res for r in x["gate"]])
    rows.drop(columns=["cm"]).to_csv(OUT / "cv_results.csv", index=False)
    rows[["profile", "scheme", "feature_set", "model", "cm"]].to_json(OUT / "confusion_matrices.json", orient="records")
    gate.to_csv(OUT / "gate.csv", index=False)

    # ---- thresholds (headline binary) ----
    hs = ccfg["headline_scheme"]
    thr_rows = []
    if hs in schemes:
        gst = scheme_groups(cfg, hs)
        groups = {g: [s for s in range(len(ds.classes)) if ds.classes[s] in st] for g, st in gst.items()}
        for x in res:
            for fs in (ccfg["headline_feature"], ccfg["secondary_feature"]):
                vals_db = 10 * np.log10(np.array(x["sim_means"][fs]))
                t = thresholds(x["hv"][fs], groups, float(ccfg["p_star"]),
                               float(ccfg["screening_prior_normal"]), int(ccfg["n_boot"]),
                               cfg["seed"], mesh_sd(vals_db, pairs))
                t.update(profile=x["profile"], feature=fs, noise_reference=noise_ref)
                thr_rows.append(t)
    thr = pd.DataFrame(thr_rows)
    thr.to_csv(OUT / "thresholds.csv", index=False)

    # ---- CV sensitivity / specificity of THR on the headline feature ----
    hp = [h for x in res for h in x["head_preds"]]
    sens_rows = []
    for h in hp:
        if h["model"] != "THR":
            continue
        v = ~h["invalid"]
        y, p = h["y"][v], h["pred"][v]
        sens_rows.append({"profile": h["profile"], "feature_set": h["feature_set"],
                          "cv_sensitivity": float((p[y == 1] == 1).mean()),
                          "cv_specificity": float((p[y == 0] == 0).mean()),
                          "fold_tau_dB_min": 10 * np.log10(np.nanmin([t for t in h["taus"] if t is not None])),
                          "fold_tau_dB_max": 10 * np.log10(np.nanmax([t for t in h["taus"] if t is not None]))})
    sens = pd.DataFrame(sens_rows)
    sens.to_csv(OUT / "cv_sens_spec.csv", index=False)

    # ---- metrics.csv ----
    if not args.no_csv:
        for r in rows.itertuples(index=False):
            notes = [r.validity, f"noise_ref={noise_ref}", f"gate_invalid={r.gate_invalid_rate:.3g}",
                     f"CM(rows=true {'/'.join(r.classes)})={r.cm}", "views share simulation (not independent)",
                     "acc_on_accepted is class-balanced; UNCERTAIN at calibrated p*<" + str(ccfg["p_star"])]
            if r.ad_only_pairs and noise_ref == "port":
                notes.append("unverified against mesh noise")
            if r.feature_set == "M5.C3[k3]":
                notes.append("k3 window chosen post hoc on all data (optimistic)")
            if r.info:
                notes.append(r.info)
            append_row(ROOT / cfg["results"]["metrics_csv"], {
                "git_hash": gh, "track": cfg["track"], "model_id": cfg["model_id"],
                "sim_set": cfg["metrics"]["sim_set"], "classes": scheme_label(cfg, r.scheme),
                "method_id": C.FS_METHOD.get(r.feature_set, r.feature_set),
                "feature_desc": f"{r.feature_set} (ring view per driven antenna)",
                "feature_dim": r.feature_dim, "classifier": f"{r.model}+platt", "noise_profile": r.profile,
                "cv_scheme": r.cv_scheme, "n_sims_per_class": r.n_sims_per_class, "n_test": r.n_test,
                "accuracy": r.accuracy, "balanced_accuracy": r.balanced_accuracy, "macro_f1": r.macro_f1,
                "reject_rate": r.reject_rate, "accuracy_on_accepted": r.bal_acc_on_accepted,
                "notes": "; ".join(notes)})
    report(cfg, gh, ds, rows, gate, thr, sens, hp, schemes, skipped, noise_ref)
    decision_rule(cfg, gh, thr, noise_ref)
    figures(cfg, ds, rows, thr, hp, res, schemes)
    print((OUT / "report.md").read_text(encoding="utf-8"))


# ============================================================ report
def md(df, floatfmt=".3g"):
    def cell(v):
        if isinstance(v, (float, np.floating)):
            return "n/a" if not np.isfinite(v) else format(v, floatfmt)
        return str(v)
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    return "\n".join([head, sep] + ["| " + " | ".join(cell(v) for v in r) + " |" for r in df.itertuples(index=False)])


def report(cfg, gh, ds, rows, gate, thr, sens, hp, schemes, skipped, noise_ref):
    ccfg = cfg["classify"]
    L = [f"# Prompt 03 - gate, classifiers, decision boundaries (track A, code {gh})", "",
         f"Simulations: {dict(zip(ds.files, ds.classes))}. Schemes run: {schemes}. Skipped: {skipped}. "
         f"Noise reference: {noise_ref}{' (between-mesh not measured: AD-vs-AD results unverified against mesh noise)' if noise_ref == 'port' else ''}.",
         "Validity: " + ", ".join(sorted(rows.validity.unique())) + ". Samples are antenna views of "
         "one simulation per stage; views are not independent.", ""]
    g = gate.pivot(index="case", columns="profile", values="invalid_rate")
    order = ["clean", "shift-2MHz", "shift+2MHz", "shift-5MHz", "shift+5MHz", "shift-10MHz", "shift+10MHz",
             "shift-20MHz", "shift+20MHz", "flatten_notch", "detune-200MHz", "detune+200MHz",
             "one_open", "one_short", "open_all", "short_all"]
    g = g.reindex([o for o in order if o in g.index])[[p for p in PROFILES if p in g.columns]]
    L += ["## Quality gate: INVALID rate (expected ~0 for clean/shift/flatten, ~1 for detune/open/short)",
          md(g.reset_index(), ".3f"), "",
          "Reasons for the single-antenna faults (typical):",
          md(gate[(gate.profile == "typical") & gate.case.isin(["one_open", "one_short", "detune+200MHz"])]
             [["case", "invalid_rate"] + REASONS], ".3f"), ""]
    for scheme in schemes:
        t = rows[(rows.scheme == scheme) & (rows.profile == "typical")].sort_values("balanced_accuracy", ascending=False)
        lab = " - UNVERIFIED AGAINST MESH NOISE" if t.ad_only_pairs.any() and noise_ref == "port" else ""
        L += [f"## `{scheme}` at `typical` (top 12 by balanced accuracy + M0){lab}",
              f"CV: {t.cv_scheme.iloc[0]} ({t.n_folds.iloc[0]} folds), {t.validity.iloc[0]}.",
              md(pd.concat([t.head(12), t[(t.feature_set == 'M0') & ~t.index.isin(t.head(12).index)]])
                 [["feature_set", "model", "balanced_accuracy", "accuracy", "macro_f1", "reject_rate",
                   "bal_acc_on_accepted", "gate_invalid_rate", "info"]]), ""]
    if len(thr):
        L += ["## Binary thresholds (Normal | AD) on opposite-antenna power, dB",
              "τ = class-balanced (equal priors) error minimiser; τ_screen uses P(Normal) = "
              f"{ccfg['screening_prior_normal']}; CI = bootstrap over simulations (within class), views "
              f"and draws ({ccfg['n_boot']}×). Margin m = max(posterior margin at p* = {ccfg['p_star']}, "
              "Φ⁻¹(p*)·σ_ref); σ_ref = within-simulation SD of one antenna view"
              + (" + between-mesh SD" if noise_ref == "mesh" else " (between-mesh SD not yet measured)")
              + ". Sensitivity/specificity here are on all draws (resubstitution); CV values below.",
              md(thr[["feature", "profile", "tau_dB", "tau_CI_lo", "tau_CI_hi", "tau_screen_dB",
                      "margin_dB", "margin_post_dB", "sd_ref_dB", "mu_Normal_dB", "mu_AD_dB",
                      "sensitivity", "specificity", "uncertain_fraction", "sens_on_accepted",
                      "spec_on_accepted"]], ".4g"), "",
              "### CV sensitivity / specificity of the fold-fitted threshold (THR)", md(sens, ".4g"), ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")


def decision_rule(cfg, gh, thr, noise_ref):
    """Plain-words rule from the current thresholds (regenerated on every run)."""
    ccfg = cfg["classify"]
    hf = ccfg["headline_feature"]
    L = [f"# Decision rule (binary headline, code {gh}) - noise-robustness only", ""]
    t = thr[(thr.feature == hf)] if len(thr) else thr
    if not len(t):
        L.append("Headline scheme not available with the current sims.csv.")
    else:
        ty = t[t.profile == "typical"].iloc[0] if (t.profile == "typical").any() else t.iloc[0]
        g = cfg["gate"]
        mesh_txt = ", between-mesh not yet measured" if noise_ref == "port" else ""
        L += [
            "Input: one full 6-port measurement. For each driven antenna t, x_t = band power-average "
            "over the whole common band of |S(t+3, t)|^2 (opposite antenna), in dB.",
            "",
            f"1. **INVALID** if the quality gate fails: any antenna with <|S_ii|^2> > {g['open_short_R']} "
            f"or std_f|S_ii| < {g['flat_sd']} (open / short / no contact); 50 MHz column power > "
            f"1 + {g['passivity_tol']}; neighbour reciprocity error > {g['recip_rel_max']}; symmetry "
            f"spread > {g['sym_db']} dB (k = 0, 1); accepted-power centroid outside the Normal window "
            f"(at least ±{float(g['detune_min_window_hz']) / 1e6:.0f} MHz). Report the reason.",
            f"2. Otherwise, per antenna view: **AD** if x_t < τ − m, **Normal** if x_t > τ + m, else "
            f"**UNCERTAIN**; τ = {ty.tau_dB:.2f} dB (95 % CI {ty.tau_CI_lo:.2f} to {ty.tau_CI_hi:.2f}), "
            f"m = {ty.margin_dB:.2f} dB at the `{ty.profile}` noise profile "
            f"(σ_ref = {ty.sd_ref_dB:.2f} dB, noise reference = {noise_ref}{mesh_txt}).",
            f"3. Screening variant (P(Normal) = {ccfg['screening_prior_normal']}): "
            f"τ_screen = {ty.tau_screen_dB:.2f} dB.",
            "4. Combine the six views by majority vote of the non-UNCERTAIN views; a tie or no "
            "non-UNCERTAIN view gives UNCERTAIN.",
            "",
            "τ and m per noise profile:", "",
            md(t[["profile", "tau_dB", "tau_CI_lo", "tau_CI_hi", "tau_screen_dB", "margin_dB",
                  "sd_ref_dB", "uncertain_fraction"]], ".3f"), "",
            "No thresholds are given for 3-class schemes: they are unverified against mesh noise."]
    (OUT / "decision_rule.md").write_text("\n".join(L), encoding="utf-8")


# ============================================================ figures
def figures(cfg, ds, rows, thr, hp, res, schemes):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.color": "#e4e3de", "grid.linewidth": 0.5,
                         "axes.edgecolor": "#8a8981", "axes.titlelocation": "left", "axes.titlesize": 9})
    profs = [p for p in PROFILES if p in rows.profile.unique()]
    series = [("M0", "LR", "#8a8981", "M0 old score (LR)"), ("M5.C3", "LR", "#2a78d6", "M5.C3 full band (LR)"),
              ("M5.C3", "THR", "#0d366b", "M5.C3 threshold τ"), ("COMB", "LR", "#eb6834", "COMB nested (LR)"),
              ("M9", "LR", "#1baf7a", "M9 full spectrum (LR)")]
    # 1. headline: balanced accuracy vs noise profile per scheme
    fig, ax = plt.subplots(1, len(schemes), figsize=(4.2 * len(schemes), 3.4), sharey=True)
    ax = np.atleast_1d(ax)
    for a, sc in zip(ax, schemes):
        for fs, m, col, lab in series:
            t = rows[(rows.scheme == sc) & (rows.feature_set == fs) & (rows.model == m)].set_index("profile")
            if len(t):
                a.plot(range(len(profs)), t.reindex(profs).balanced_accuracy, "-o", color=col, lw=1.8, ms=4, label=lab)
        K = len(rows[rows.scheme == sc].classes.iloc[0])
        a.axhline(1 / K, color="#c3c2b7", lw=0.8, ls="--")
        unv = rows[rows.scheme == sc].ad_only_pairs.any()
        a.set_title(sc + ("  (unverified vs mesh noise)" if unv else "  (headline)" if sc == "binary" else ""))
        a.set_xticks(range(len(profs)), profs, rotation=35, ha="right")
        a.set_ylim(0, 1.02)
    ax[0].set_ylabel("balanced accuracy (CV, noise-robustness only)")
    ax[0].legend(frameon=False, fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "03_accuracy_vs_noise.png", dpi=150)
    plt.close(fig)

    # 2. severity index (headline feature, dB) per stage and profile with τ and margin
    hf = cfg["classify"]["headline_feature"]
    fig, ax = plt.subplots(2, 3, figsize=(12, 5.5), sharex=True)
    order = [c for c in ["Normal", "MCI", "Mild", "Moderate", "Severe"] if c in ds.classes]
    for a, x in zip(ax.flat, res):
        vals = x["hv"][hf]
        bins = np.linspace(min(10 * np.log10(v).min() for v in vals.values()),
                           max(10 * np.log10(v).max() for v in vals.values()), 60)
        for c in order:
            v = np.concatenate([10 * np.log10(vals[s]) for s in range(len(ds.classes)) if ds.classes[s] == c])
            a.hist(v, bins, color=STAGE_COLOR[c], alpha=0.65, label=c, density=True)
        t = thr[(thr.profile == x["profile"]) & (thr.feature == hf)]
        if len(t):
            t = t.iloc[0]
            a.axvspan(t.tau_dB - t.margin_dB, t.tau_dB + t.margin_dB, color="#f0efec", zorder=0)
            a.axvline(t.tau_dB, color="#1f1e1c", lw=1)
        a.set_title(x["profile"])
    ax[0, 0].legend(frameon=False, fontsize=7)
    for a in ax[1]:
        a.set_xlabel(f"{hf}: band-avg opposite-antenna power (dB)")
    fig.suptitle("Severity index = full-band opposite-antenna power per antenna view; line = τ (Normal|AD), "
                 "grey = UNCERTAIN margin", x=0.01, ha="left", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "03_severity_index.png", dpi=150)
    plt.close(fig)

    # 3. coverage vs accuracy on accepted (headline LR, calibrated)
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    ps = np.linspace(0.5, 0.995, 60)
    for a, fs in zip(ax, (hf, "M0")):
        for h in hp:
            if h["feature_set"] != fs or h["model"] != "LR":
                continue
            v = ~h["invalid"]
            y, pr = h["y"][v], h["proba"][v]
            cov, acc = [], []
            for p in ps:
                m = pr.max(1) >= p
                if m.sum() and len(np.unique(y[m])) == 2:
                    pc = pr.argmax(1)[m]
                    acc.append(0.5 * sum((pc[y[m] == k] == k).mean() for k in (0, 1)))
                    cov.append(m.mean())
            col = plt.cm.Blues(0.35 + 0.1 * profs.index(h["profile"]))
            a.plot(cov, acc, color=col, lw=1.6, label=h["profile"])
        a.set_title(f"{fs} (LR + Platt), binary")
        a.set_xlabel("coverage (fraction not UNCERTAIN)")
        a.invert_xaxis()
    ax[0].set_ylabel("balanced accuracy on accepted")
    ax[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "03_coverage_accuracy.png", dpi=150)
    plt.close(fig)

    # 4. confusion matrices (typical)
    picks = [("binary", hf, "THR"), ("binary", "M0", "LR"), ("three_merged", "COMB", "ORD"), ("three", "COMB", "ORD")]
    picks = [p for p in picks if p[0] in schemes]
    fig, ax = plt.subplots(1, len(picks), figsize=(3.3 * len(picks), 3.1))
    for a, (sc, fs, m) in zip(np.atleast_1d(ax), picks):
        t = rows[(rows.scheme == sc) & (rows.feature_set == fs) & (rows.model == m) & (rows.profile == "typical")]
        if not len(t):
            continue
        t = t.iloc[0]
        cm = np.array(t.cm, float)
        cmn = cm / cm.sum(1, keepdims=True)
        a.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                a.text(j, i, f"{cmn[i, j]:.2f}", ha="center", va="center", fontsize=8,
                       color="white" if cmn[i, j] > 0.6 else "#1f1e1c")
        a.set_xticks(range(len(t.classes)), t.classes, rotation=30, ha="right", fontsize=7)
        a.set_yticks(range(len(t.classes)), t.classes, fontsize=7)
        a.set_title(f"{sc}: {fs} {m}\nbal.acc {t.balanced_accuracy:.2f}" + (" (unverified)" if t.ad_only_pairs else ""), fontsize=8)
        a.grid(False)
    fig.suptitle("Confusion matrices at typical noise (rows = true class, row-normalised)", x=0.01, ha="left", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "03_confusion.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
