"""Apply the frozen rule (results/04/frozen_rule.json) to new solves, unchanged.

    from adstage.frozen import apply_rule
    out = apply_rule(rule_json_path, f_hz, S_ring_draws)   # S: (n, F, 6, 6) ring order, noisy draws

The feature definition is fixed by the rule's feature_spec: ring-symmetrised features of
adstage.features.ring_features on 3.2-4.2 GHz with floor subtraction. Nothing in this file may
change the rule; it only evaluates it.
"""
from __future__ import annotations

import json

import numpy as np

from .features.ring_features import features


def _restrict(f, S, band):
    m = (f >= band[0] - 1) & (f <= band[1] + 1)
    return f[m], S[:, m]


def apply_rule(rule_path, f, S):
    rule = json.loads(open(rule_path, encoding="utf-8").read())
    f, S = _restrict(f, S, rule["feature_spec"]["band_hz"])
    X, names, _, _ = features(f, S)
    out = {}
    det = rule["detection_binary_R31"]
    r31 = X[:, names.index("R31")]
    lab = np.full(len(r31), "UNCERTAIN", dtype=object)
    lab[r31 < det["tau_dB"] - det["margin_dB"]] = "AD"
    lab[r31 > det["tau_dB"] + det["margin_dB"]] = "Normal"
    out["binary_R31"] = lab
    for scheme, st in rule["staging"].items():
        idx = [names.index(n) for n in st["features"]]
        Z = X[:, idx] / np.asarray(st["scale"])
        logit = Z @ np.asarray(st["coef"]).T + np.asarray(st["intercept"])
        if logit.ndim == 1 or logit.shape[1] == 1:               # binary LDA returns one column
            logit = np.column_stack([np.zeros(len(Z)), np.ravel(logit)])
        logit -= logit.max(1, keepdims=True)
        P = np.exp(logit) / np.exp(logit).sum(1, keepdims=True)
        lab = np.array(st["classes"], dtype=object)[P.argmax(1)]
        lab[P.max(1) < rule["p_star_reject"]] = "UNCERTAIN"
        out[scheme] = lab
    return out
