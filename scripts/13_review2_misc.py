"""Adversarial review, round 2 (main session): G7 material dispersion and C6 replication design + predictions.

    python scripts/13_review2_misc.py

G7: Gabriel et al. (1996) 4-Cole-Cole parameters (as tabulated on the IFAC/webnir reference page) evaluated at
3.2 / 3.241 / 3.7 / 4.2 GHz against the model's constant healthy values.
C6: proposed blind design RightOnly_test = exact mirror image of LeftOnly_test, and the main session's predictions,
derived only from LeftOnly_test_c3, the nine mirror-symmetric designs and the round-2 floor rule (R1c). Written to
results/05_lobe/rightonly_predictions.{md,csv}; committed before the design exists; never edited afterwards.
"""
from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adstage.config import load_config  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
R10 = _load("rev10", "10_lobe_review.py")
R11 = _load("rev11", "11_review2.py")
OUT = ROOT / "results" / "05_lobe"
md = L7.md
E0 = 8.854187817e-12
GABRIEL = {  # einf, sigma_ionic, [(delta_eps, tau, alpha) x 4]
    "gray matter": (4, 0.02, [(45, 7.958e-12, .1), (400, 15.915e-9, .15), (2e5, 106.1e-6, .22), (4.5e7, 5.305e-3, 0)]),
    "white matter": (4, 0.02, [(32, 7.958e-12, .1), (100, 7.958e-9, .1), (4e4, 53.052e-6, .3), (3.5e7, 7.958e-3, .02)]),
    "CSF": (4, 2.0, [(65, 7.958e-12, .1), (40, 1.592e-9, 0), (0, 159.16e-6, 0), (0, 15.915e-3, 0)]),
    "bone cortical (skull)": (2.5, 0.02, [(10, 13.263e-12, .2), (180, 79.577e-9, .2), (5000, 159.16e-6, .2), (1e5, 15.915e-3, 0)]),
    "fat": (2.5, 0.01, [(3, 7.958e-12, .2), (15, 15.915e-9, .1), (33000, 159.16e-6, .05), (1e7, 7.958e-3, .01)]),
    "skin (dry)": (4, 0.0002, [(32, 7.234e-12, 0), (1100, 32.481e-9, .2), (0, 159.16e-6, .2), (0, 15.915e-3, .2)])}
MODEL = {"gray matter": (47.7, 2.42), "white matter": (35.3, 1.65), "CSF": (65.0, 4.27)}


def gabriel(t, f):
    einf, sig, terms = GABRIEL[t]
    w = 2 * np.pi * f
    e = einf + sum(de / (1 + (1j * w * tau) ** (1 - a)) for de, tau, a in terms) + sig / (1j * w * E0)
    return float(e.real), float(-e.imag * w * E0)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    gh = git_hash(ROOT)
    rows = []
    for t in GABRIEL:
        for f in (3.2e9, 3.241e9, 3.7e9, 4.2e9):
            eps, sg = gabriel(t, f)
            row = {"tissue": t, "f (GHz)": f / 1e9, "Gabriel eps_r": eps, "Gabriel sigma (S/m)": sg}
            if t in MODEL:
                row["model eps_r"], row["model sigma"] = MODEL[t]
                row["model - Gabriel eps (%)"] = 100 * (MODEL[t][0] - eps) / eps
                row["model - Gabriel sigma (%)"] = 100 * (MODEL[t][1] - sg) / sg
            rows.append(row)
    g7 = pd.DataFrame(rows)
    (OUT / "review2").mkdir(exist_ok=True)
    g7.to_csv(OUT / "review2" / "G7_dispersion.csv", index=False)

    # ------------------------------------------------------------------ C6 predictions for RightOnly_test
    f, Sd, man, _ = L8.load_all(load_config(ROOT, "config_lobe.yaml"))
    LO, SYM = R11.LO, R11.SYM
    cp = {d: R11.lr_cr_phase(Sd[d]) for d in SYM + [LO]}
    MS = {d: R10.mirror_stats(f, Sd[d]) for d in SYM + [LO]}
    msk = R11.fmask(f, R11.LRBAND)
    pred = []
    for k in cp[LO]:
        for bn, m_ in (("band mean 3.2-4.2", np.ones(len(f), bool)), ("3.30-3.65 GHz", msk)):
            v = lambda d: float(cp[d][k][m_].mean())          # noqa: E731
            yd = max(abs(v(b) - v(a)) for a, b in L8.PAIRS.values())
            fr = R11.floor_rule(v(LO), [v(d) for d in SYM], yd)
            pred.append({"statistic": f"phase cross-ratio {k}", "frequencies": bn, "LeftOnly": v(LO),
                         "predicted RightOnly": -v(LO), "tolerance (clean ruler)": fr["clean ruler"],
                         "LeftOnly / ruler": fr["ratio"], "sign test informative": fr["ratio"] >= 2})
    for k in MS[LO]:
        if k.startswith("phase cross-ratio"):
            continue
        yd = max(abs(float(MS[b][k][0] - MS[a][k][0])) for a, b in L8.PAIRS.values())
        fr = R11.floor_rule(float(MS[LO][k][0]), [float(MS[d][k][0]) for d in SYM], yd)
        pred.append({"statistic": k, "frequencies": "band mean 3.2-4.2", "LeftOnly": float(MS[LO][k][0]),
                     "predicted RightOnly": -float(MS[LO][k][0]), "tolerance (clean ruler)": fr["clean ruler"],
                     "LeftOnly / ruler": fr["ratio"], "sign test informative": fr["ratio"] >= 2})
    X, nm, _, _ = __import__("adstage.features.ring_features", fromlist=["features"]).features(f, Sd[LO][None])
    R = L8.rulers(f, Sd, load_config(ROOT, "config_lobe.yaml"), 60)
    for ft in ("R31", "R21", "R32"):
        pred.append({"statistic": f"{ft} (mirror-invariant)", "frequencies": "band mean 3.2-4.2",
                     "LeftOnly": float(X[0][nm.index(ft)]), "predicted RightOnly": float(X[0][nm.index(ft)]),
                     "tolerance (clean ruler)": R["yard"][ft], "LeftOnly / ruler": np.nan, "sign test informative": False})
    pt = pd.DataFrame(pred)
    pt.to_csv(OUT / "rightonly_predictions.csv", index=False)
    inf = pt[pt["sign test informative"]]
    n_est = {bn: int(((pt.frequencies == bn) & pt.statistic.str.startswith("phase cross-ratio") & (pt["LeftOnly / ruler"] >= 3)).sum())
             for bn in ("band mean 3.2-4.2", "3.30-3.65 GHz")}
    L = ["# Main-session predictions for the blind design RightOnly_test (written before the design exists)", "",
         f"Code {gh}. Derived only from LeftOnly_test_c3, the nine mirror-symmetric lobe designs and the round-2 floor rule "
         "(scripts/11_review2.py docstring). Status of the phase finding being tested: **post hoc**. Do not edit after "
         "RightOnly_test exists.", "",
         "## Design to build (HFSS project new_with_slices, copy of LeftOnly_test)",
         "- e_S1..e_S6 = 0 / 0 / 0 / 0 / 11.5 / 7.5 mm (S5 parietal R 11.5, S6 temporal R 7.5; the exact mirror of "
         "LeftOnly_test's 0 / 7.5 / 11.5 / 0 / 0 / 0), r_hip 17.5 mm.",
         "- Materials: GM/WM_Mild in S5 and S6 only; HIP_Mild; CSF_Mild (one object, so also the 0.5 mm layer on the left).",
         "- Setup1 identical to LeftOnly_test_c3 (adaptive at 3.4 GHz, Max Delta S 0.02, stop rule 1 = first converged pass, "
         "30% refinement, first order, iterative; interpolating sweep 3.2-4.2 GHz, 201 points). Report passes, final "
         "Delta S and elements. File: data/raw/new_with_slices_RightOnly_test.s6p.",
         "- Why this design: the left-right phase finding claims a real asymmetry. A mirrored design with its own mesh must "
         "reproduce it with the opposite sign; a numerical artefact of LeftOnly's mesh would not.", "",
         "## Predictions (reference-free mirror statistics T: RightOnly against its own port mirror)",
         "1. Every left-right statistic flips sign: T(RightOnly) = -T(LeftOnly), within one clean ruler (max(largest "
         "symmetric design, one-pass yardstick)). Informative only where |T(LeftOnly)| >= 2x its ruler "
         f"({len(inf)} statistics, listed below with 'sign test informative').",
         f"2. Phase cross-ratios >= 3x the clean ruler: {n_est['band mean 3.2-4.2']} (band mean) and "
         f"{n_est['3.30-3.65 GHz']} (3.30-3.65 GHz) for LeftOnly; RightOnly within +-2 of each count, all with the "
         "opposite sign.",
         "3. Power: no power LR index beyond 2x its ruler; the reflection pairs flip sign (T2 vs T6, T3 vs T5 about +0.06 / "
         "+0.07 dB).",
         "4. Mirror-invariant ratios equal LeftOnly's within one one-pass yardstick (R31, R21, R32 rows below). The frozen "
         "detection label is therefore not determined (LeftOnly: 0.09 dB inside the AD zone).",
         "5. Imaging-session mirror-test LR: about -7.9 (LeftOnly +7.9), i.e. the sign flips; its size stays below 2x the "
         "max floor (LeftOnly 1.94x), as for LeftOnly.", "",
         "## Scoring (fixed now)",
         "- Prediction 1 holds if the sign flips and |T(RO) + T(LO)| <= the stated tolerance for >= 80% of the "
         "informative statistics.",
         "- Prediction 2 holds if both counts are within +-2 with the opposite sign.",
         "- The phase finding is **replicated** only if 1 and 2 both hold. If the signs do not flip, it is retracted as "
         "numerical.", "",
         "## Table", md(pt, ".3f"), ""]
    (OUT / "rightonly_predictions.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:30]))
    print(md(g7, ".3f"))


if __name__ == "__main__":
    main()
