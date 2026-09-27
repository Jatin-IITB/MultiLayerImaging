"""Features per antenna view, fold-local feature construction, models, calibration.

Sample = (simulation, noise draw, driven antenna t). Features of view t use only column t
of S (waves received when antenna t is driven).

Feature sets (anything chosen from data is chosen on the training fold only):
  M0, M1, M2          old score, dB-avg reflection, power-avg reflection. M3 and M4 are left
                      out: M3 is affine in M2, and M4 = M2 up to ~4e-4 coupling (absorbed
                      power reduces to reflection in this geometry).
  M5                  C, C1, C2, C3 (full band)
  M5.C3               full-band opposite-antenna power (headline primary feature)
  M5.C3[k3]           3.35-3.60 GHz window. Window chosen post hoc on all data in prompt 02,
                      so it is optimistic.
  M5.C3[nested]       window chosen inside each training fold (max training Fisher)
  M6                  accepted-power centroid, spread and 20 sub-band energies
  M7                  differential energy vs a Normal reference built from training views
  M8                  circulant modal powers |λ_m|^2, m = 0..3 (full band)
  COMB                <= 3 scalars greedily chosen on the training fold (Fisher,
                      |corr| < 0.9) from M2/M5/M6/M7/M8
  M9                  full spectrum of view t: 20log10|S(t+k,t)|, cos/sin of phase, k = 0..N-1
"""
from __future__ import annotations

import itertools

import numpy as np
from scipy.optimize import minimize
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC, LinearSVC

from ..features.floor import CLIP, floor_power, r31
from ..features.metrics import band_avg, compute

FAMILIES = {
    "M0": ["M0.old_score"], "M1": ["M1.Sii_dBavg"], "M2": ["M2.R"],
    "M5": ["M5.C", "M5.C1", "M5.C2", "M5.C3"], "M5.C3": ["M5.C3"], "M5.C3[k3]": ["M5.C3[k3]"],
    "M8": ["M8.lam0^2", "M8.lam1^2", "M8.lam2^2", "M8.lam3^2"],
}
FS_METHOD = {"M5.C3": "M5", "M5.C3[k3]": "M5", "M5.C3[nested]": "M5", "COMB": "COMB"}


# ============================================================ feature extraction
def extract(f, D, metrics, bands, subbands, floor_subtract=True):
    """D: (n, F, N, N) ring-order draws -> dict of per-view arrays (views on axis 1) plus
    per-measurement values (floor estimate, R31).

    With floor_subtract, every band-averaged transmission power (M5.C*, sub-band C3) is
    debiased by the measurement's own floor estimate before any dB conversion. The raw
    full-band C3 is kept as 'M5.C3_raw' for comparison."""
    per_ant = [m for m in metrics if m.level == "per_ant" and m.method_id != "M7"]
    scal = compute(per_ant, bands, f, D, None)                       # name -> (n, N)
    N = D.shape[-1]
    idx = np.arange(N)
    pf = floor_power(D)                                              # (n,)
    scal["M5.C3_raw"] = scal["M5.C3"].copy()
    if floor_subtract:
        n_paths = {"M5.C": N - 1, "M5.C1": 1, "M5.C2": 1, "M5.C3": 1}
        for base, k in n_paths.items():
            for name in (base, base + "[k3]"):
                if name in scal:
                    scal[name] = np.maximum(scal[name] - k * pf[:, None], CLIP)
    cols = np.stack([D[..., (idx + k) % N, idx] for k in range(N)], -1)   # (n, F, N_view, K)
    cols = np.moveaxis(cols, 1, -1)                                  # (n, N_view, K, F)
    k3 = N // 2
    p3 = np.abs(cols[:, :, k3, :]) ** 2                              # (n, N, F)
    c3sb = np.stack([band_avg(f, p3, b) for b in subbands], -1)      # (n, N, n_sb)
    if floor_subtract:
        c3sb = np.maximum(c3sb - pf[:, None, None], CLIP)
    A = 1 - np.abs(cols[:, :, 0, :]) ** 2
    m6 = np.stack([band_avg(f, A, b) for b in subbands], -1)
    band = (float(f[0]), float(f[-1]))
    meas = {"floor": pf, "M5.R31": r31(f, D, pf if floor_subtract else 0 * pf, band)}
    return {"scal": scal, "c3sb": c3sb, "m6sb": m6, "cols": cols.astype(np.complex64),
            "meas": meas}


# ============================================================ fold-local features
def _take(feats, blocks, split, getter):
    parts = []
    for s, views in blocks:
        a = getter(feats[s][split])                                  # (n, N, ...)
        parts.append(np.concatenate([a[:, t] for t in views], 0))
    return np.concatenate(parts, 0)


def _fisher_multi(x, y):
    """min over class pairs of (Δμ)^2 / (σa^2 + σb^2) for 1-D x."""
    cls = np.unique(y)
    st = [(x[y == c].mean(), x[y == c].var()) for c in cls]
    return min((a[0] - b[0]) ** 2 / (a[1] + b[1] + 1e-300) for a, b in itertools.combinations(st, 2))


def build_features(fs, feats, train_blocks, test_blocks, y_tr, ctx):
    """-> (X_train, X_test, info dict). y_tr: training labels (for nested choices)."""
    f = ctx["f"]
    info = {}
    if fs in FAMILIES:
        names = FAMILIES[fs]
        g = lambda d: np.stack([d["scal"][n] for n in names], -1)            # noqa: E731
        return _take(feats, train_blocks, "train", g), _take(feats, test_blocks, "test", g), info
    if fs == "M6":
        g = lambda d: np.concatenate([np.stack([d["scal"]["M6.fc_A"], d["scal"]["M6.spread_A"]], -1),
                                      d["m6sb"]], -1)                         # noqa: E731
        return _take(feats, train_blocks, "train", g), _take(feats, test_blocks, "test", g), info
    if fs == "M5.C3[nested]":
        tr = _take(feats, train_blocks, "train", lambda d: d["c3sb"])
        best = None
        for w in ctx["window_lengths"]:
            for lo in range(tr.shape[1] - w + 1):
                j = _fisher_multi(tr[:, lo:lo + w].mean(1), y_tr)
                if best is None or j > best[0]:
                    best = (j, lo, w)
        _, lo, w = best
        sb = ctx["subbands"]
        info["window_GHz"] = (sb[lo][0] / 1e9, sb[lo + w - 1][1] / 1e9)
        te = _take(feats, test_blocks, "test", lambda d: d["c3sb"])
        return tr[:, lo:lo + w].mean(1, keepdims=True), te[:, lo:lo + w].mean(1, keepdims=True), info
    if fs in ("M7", "COMB"):
        m7_tr, m7_te = _m7(feats, train_blocks, test_blocks, ctx)
    if fs == "M7":
        return m7_tr, m7_te, info
    if fs == "COMB":
        pool = ["M2.R", "M5.C", "M5.C1", "M5.C2", "M5.C3", "M6.fc_A", "M6.spread_A",
                "M8.lam0^2", "M8.lam1^2", "M8.lam2^2", "M8.lam3^2"]
        g = lambda d: np.stack([d["scal"][n] for n in pool], -1)              # noqa: E731
        sbn = [f"M6.A[{b[0] / 1e9:.2f}]" for b in ctx["subbands"]]
        names = pool + sbn + ["M7.D", "M7.D_pow", "M7.D0", "M7.D1", "M7.D2", "M7.D3"]
        tr = np.concatenate([_take(feats, train_blocks, "train", g),
                             _take(feats, train_blocks, "train", lambda d: d["m6sb"]), m7_tr], 1)
        te = np.concatenate([_take(feats, test_blocks, "test", g),
                             _take(feats, test_blocks, "test", lambda d: d["m6sb"]), m7_te], 1)
        score = np.array([_fisher_multi(tr[:, j], y_tr) for j in range(tr.shape[1])])
        chosen = []
        for j in np.argsort(-score):
            if len(chosen) == ctx["comb_max"]:
                break
            if all(abs(np.corrcoef(tr[:, j], tr[:, c])[0, 1]) < ctx["comb_corr"] for c in chosen):
                chosen.append(j)
        info["chosen"] = [names[j] for j in chosen]
        return tr[:, chosen], te[:, chosen], info
    if fs == "M9":
        def g(d):
            c = d["cols"]                                                     # (n, N, K, F)
            mag = 20 * np.log10(np.maximum(np.abs(c), 1e-12))
            ph = np.angle(c)
            return np.concatenate([mag, np.cos(ph), np.sin(ph)], -1).reshape(*c.shape[:2], -1)
        return (_take(feats, train_blocks, "train", g).astype(np.float32),
                _take(feats, test_blocks, "test", g).astype(np.float32), info)
    raise KeyError(fs)


def _m7(feats, train_blocks, test_blocks, ctx):
    """Differential energy vs a Normal reference averaged over TRAINING Normal views/draws."""
    f, ref_sims = ctx["f"], ctx["ref_sims"]
    acc, cnt = 0, 0
    for s, views in train_blocks:
        if s in ref_sims:
            c = feats[s]["train"]["cols"][:, views]                          # (n, v, K, F)
            acc = acc + c.sum((0, 1))
            cnt += c.shape[0] * c.shape[1]
    ref = acc / cnt                                                          # (K, F)
    K = ref.shape[0]
    band = (float(f[0]), float(f[-1]))

    def g(d):
        c = d["cols"]
        diff = np.abs(c - ref) ** 2                                          # (n, N, K, F)
        dpow = (np.abs(c) ** 2 - np.abs(ref) ** 2) ** 2
        out = [band_avg(f, diff.sum(2), band), band_avg(f, dpow.sum(2), band)]
        for k in range(K // 2 + 1):
            x = diff[:, :, k] if k in (0, K // 2) else 0.5 * (diff[:, :, k] + diff[:, :, K - k])
            out.append(band_avg(f, x, band))
        return np.stack(out, -1)
    return _take(feats, train_blocks, "train", g), _take(feats, test_blocks, "test", g)


# ============================================================ models
class OrdinalLogit(BaseEstimator, ClassifierMixin):
    """Proportional-odds (cumulative logit): P(y <= k | x) = σ(θ_k - w·x), class-balanced
    weights, L2 penalty. decision_function = w·x is the severity index."""

    def __init__(self, alpha=1e-2):
        self.alpha = alpha

    def fit(self, X, y):
        self.classes_ = np.unique(y)
        yi = np.searchsorted(self.classes_, y)
        K, d = len(self.classes_), X.shape[1]
        cw = len(y) / (K * np.bincount(yi, minlength=K))
        sw = cw[yi]

        def unpack(p):
            w, t0, dt = p[:d], p[d], p[d + 1:]
            return w, np.concatenate([[t0], t0 + np.cumsum(np.exp(dt))])

        def nll(p):
            w, th = unpack(p)
            z = X @ w
            cdf = lambda k: 1 / (1 + np.exp(-(th[k] - z))) if k < K - 1 else np.ones_like(z)  # noqa: E731
            upper = np.stack([cdf(k) for k in range(K)], 1)
            lower = np.concatenate([np.zeros((len(z), 1)), upper[:, :-1]], 1)
            pr = np.clip(upper - lower, 1e-12, 1)[np.arange(len(z)), yi]
            return -(sw * np.log(pr)).sum() / len(z) + self.alpha * w @ w

        p0 = np.zeros(d + K - 1)
        res = minimize(nll, p0, method="L-BFGS-B")
        self.coef_, self.thresholds_ = unpack(res.x)
        return self

    def decision_function(self, X):
        return X @ self.coef_

    def predict_proba(self, X):
        z = self.decision_function(X)
        K = len(self.classes_)
        up = np.stack([1 / (1 + np.exp(-(self.thresholds_[k] - z))) for k in range(K - 1)]
                      + [np.ones_like(z)], 1)
        lo = np.concatenate([np.zeros((len(z), 1)), up[:, :-1]], 1)
        return np.clip(up - lo, 0, 1)

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(1)]


class Threshold1D(BaseEstimator, ClassifierMixin):
    """Explicit binary boundary on a single feature: τ minimises the class-balanced error on
    the training data, with orientation chosen automatically."""

    def fit(self, X, y):
        x = X[:, 0]
        self.classes_ = np.unique(y)
        if len(self.classes_) != 2:
            raise ValueError("Threshold1D is binary only")
        pos = y == self.classes_[1]
        xs = np.unique(x)
        cand = np.concatenate([[xs[0] - 1e-12], 0.5 * (xs[1:] + xs[:-1]), [xs[-1] + 1e-12]])
        if cand.size > 1000:
            cand = np.quantile(x, np.linspace(0, 1, 1001))
        best = None
        for sgn in (1, -1):
            pred = (sgn * x[:, None] > sgn * cand[None, :])
            err = 0.5 * ((~pred[pos]).mean(0) + pred[~pos].mean(0))
            j = int(np.argmin(err))
            if best is None or err[j] < best[0]:
                best = (err[j], cand[j], sgn)
        _, self.tau_, self.sign_ = best
        return self

    def decision_function(self, X):
        return self.sign_ * (X[:, 0] - self.tau_)

    def predict(self, X):
        return np.where(self.decision_function(X) > 0, self.classes_[1], self.classes_[0])


class BalancedKNN(BaseEstimator, ClassifierMixin):
    """kNN on a class-balanced random undersample of the training set."""

    def __init__(self, n_neighbors=15, random_state=0):
        self.n_neighbors, self.random_state = n_neighbors, random_state

    def fit(self, X, y):
        rng = np.random.default_rng(self.random_state)
        cls, cnt = np.unique(y, return_counts=True)
        keep = np.concatenate([rng.choice(np.flatnonzero(y == c), cnt.min(), replace=False)
                               for c in cls])
        self.knn_ = KNeighborsClassifier(self.n_neighbors).fit(X[keep], y[keep])
        self.classes_ = self.knn_.classes_
        return self

    def predict_proba(self, X):
        return self.knn_.predict_proba(X)

    def predict(self, X):
        return self.knn_.predict(X)


def make_model(name, dim, n_classes, Cs, seed):
    pre = [StandardScaler()]
    if dim > 20:
        pre.append(PCA(n_components=20, random_state=seed))
    if name == "LDA":
        est = LinearDiscriminantAnalysis(priors=np.full(n_classes, 1 / n_classes))
    elif name == "LR":
        est = GridSearchCV(LogisticRegression(class_weight="balanced", max_iter=3000),
                           {"C": Cs}, cv=GroupKFold(3), scoring="balanced_accuracy")
    elif name == "LSVM":
        est = LinearSVC(class_weight="balanced", max_iter=20000)
    elif name == "RBF":
        est = SVC(kernel="rbf", class_weight="balanced", gamma="scale")
    elif name == "kNN":
        est = BalancedKNN(15, seed)
    elif name == "ORD":
        est = OrdinalLogit()
    elif name == "THR":
        return make_pipeline(Threshold1D())
    else:
        raise KeyError(name)
    return make_pipeline(*pre, est)


def fit_model(model, X, y, groups):
    last = model.steps[-1][0]
    if isinstance(model.steps[-1][1], GridSearchCV):
        return model.fit(X, y, **{f"{last}__groups": groups})
    return model.fit(X, y)


def scores(model, X):
    """Continuous scores for calibration: decision_function or log-probabilities."""
    try:
        s = model.decision_function(X)
    except AttributeError:
        s = np.log(np.clip(model.predict_proba(X), 1e-6, 1))
    return s[:, None] if s.ndim == 1 else s


def freeze_hyper(model):
    """Clone with the grid-searched C fixed (so inner calibration folds do not re-search)."""
    last = model.steps[-1][1]
    m = clone(model)
    if isinstance(last, GridSearchCV):
        m.steps[-1] = (m.steps[-1][0], clone(last.estimator).set_params(**last.best_params_))
    return m


def calibrate(model, X, y, groups, seed):
    """Cross-fitted Platt/multinomial calibration: out-of-fold scores from inner GroupKFold(3)
    (hyper-parameters frozen), then a class-balanced logistic map scores -> posteriors."""
    base = freeze_hyper(model)
    oof = None
    for tr, va in GroupKFold(3).split(X, y, groups):
        if len(np.unique(y[tr])) < len(np.unique(y)):
            continue
        m = clone(base).fit(X[tr], y[tr])
        s = scores(m, X[va])
        if oof is None:
            oof = np.full((len(y), s.shape[1]), np.nan)
        oof[va] = s
    ok = ~np.isnan(oof).any(1)
    cal = make_pipeline(StandardScaler(),
                        LogisticRegression(class_weight="balanced", C=1e4, max_iter=3000))
    return cal.fit(oof[ok], y[ok])
