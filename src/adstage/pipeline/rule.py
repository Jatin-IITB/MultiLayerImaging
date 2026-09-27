"""The complete binary decision rule, scored per complete measurement (not per antenna view).

    gate  ->  INVALID (with reason)
    per view (6 views, views feature, e.g. M5.C3 in dB):
        AD if x_t beyond τ - m (orientation learned), Normal if beyond τ + m, else UNCERTAIN
    majority vote of the non-UNCERTAIN views; tie or none -> UNCERTAIN
For a measurement-level feature (e.g. M5.R31, one value per measurement) there is no vote:
the single value is compared with τ ± m.

τ, orientation and m are fit on training data only:
    τ   class-balanced error minimiser (Threshold1D)
    m   max(m_post, Φ^-1(p*)·σ_ref); m_post from a class-balanced logistic fit, σ_ref = pooled
        within-simulation SD of the training values (+ between-mesh SD when measured)
"""
from __future__ import annotations

import numpy as np
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression

from .classify import Threshold1D

NORMAL, AD, UNCERTAIN, INVALID = 0, 1, -1, -2


def fit_rule(x_db, y, sim, p_star=0.7, mesh_sd_db=np.nan):
    """x_db (n,), y in {0 Normal, 1 AD}, sim ids (n,) -> rule dict."""
    t = Threshold1D().fit(x_db[:, None], y)
    lr = LogisticRegression(class_weight="balanced", C=1e4, max_iter=3000).fit(x_db[:, None], y)
    m_post = np.log(p_star / (1 - p_star)) / max(abs(lr.coef_[0, 0]), 1e-12)
    sd = np.sqrt(np.mean([np.var(x_db[sim == s], ddof=1) for s in np.unique(sim)]))
    sd_ref = np.sqrt(sd ** 2 + (mesh_sd_db ** 2 if np.isfinite(mesh_sd_db) else 0.0))
    return {"tau": float(t.tau_), "sign": int(t.sign_), "margin": float(max(m_post, norm.ppf(p_star) * sd_ref)),
            "m_post": float(m_post), "sd_ref": float(sd_ref)}


def classify_values(x_db, rule):
    """Any shape -> same shape of NORMAL / AD / UNCERTAIN."""
    z = rule["sign"] * (x_db - rule["tau"])          # > 0 means AD side
    out = np.full(x_db.shape, UNCERTAIN)
    out[z > rule["margin"]] = AD
    out[z < -rule["margin"]] = NORMAL
    return out


def vote(view_labels):
    """(n, V) view labels -> (n,) majority of non-UNCERTAIN views; tie / none -> UNCERTAIN."""
    n_ad = (view_labels == AD).sum(1)
    n_no = (view_labels == NORMAL).sum(1)
    out = np.full(view_labels.shape[0], UNCERTAIN)
    out[n_ad > n_no] = AD
    out[n_no > n_ad] = NORMAL
    return out


def score(final, y, invalid):
    """Per-measurement scores. final: rule outputs before the gate; invalid: gate flags."""
    out = np.where(invalid, INVALID, final)
    valid = out != INVALID
    dec = valid & (out != UNCERTAIN)
    r = {"n": int(len(y)), "invalid_rate": float(1 - valid.mean()),
         "uncertain_rate": float((out[valid] == UNCERTAIN).mean()) if valid.any() else np.nan}
    for name, c in (("sensitivity", AD), ("specificity", NORMAL)):
        m = valid & (y == c)
        r[name] = float((out[m] == c).mean()) if m.any() else np.nan           # UNCERTAIN = not correct
        md = dec & (y == c)
        r[name + "_decided"] = float((out[md] == c).mean()) if md.any() else np.nan
    r["balanced_accuracy"] = 0.5 * (r["sensitivity"] + r["specificity"])
    r["balanced_accuracy_decided"] = 0.5 * (r["sensitivity_decided"] + r["specificity_decided"])
    return r
