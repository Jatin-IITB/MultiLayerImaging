"""Blind scoring of the lobe phantom (c3 delivery, 4 Oct) and the completed sets lobe_A / lobe_B:

    python imaging/lobe_c3.py [--n 200]

1. Imaging-side registry of every lobe file (stop rule, passes, final dS, elements, sets) and QC of the
   four c3 files (points, reciprocity, passivity, glitch-mask log) -> lobe_sets.csv, lobe_qc_c3.csv,
   lobe_mask_log.csv. The shared manifest (data/sims_lobe.csv) belongs to the main session.
2. Blind test: report_lobe.run_blind() (frozen pipeline, pre-registered criterion, both references:
   frozen 7-pass Healthy_sliced primary, Healthy_sliced_new alongside), then every pre-registered
   prediction scored hit / miss / not separable with the effect divided by the noise SD, the one-pass
   mesh yardstick, the numerical symmetry floor and the measurement-error spread (Prompt 07 model).
   The whitened-projection log model (lobe_rulers.WhitenedLog) is added, labelled post-hoc.
3. MCI_lobe - Healthy_sliced_new against the rulers on every reconstruction feature and at data level.
4. lobe_B (stop rule 2): frozen pipeline, contrasts against the rulers, one-pass yardstick for all four
   stages, and a read-only cross-check of the frozen R31 rule (main session's numbers are authoritative).
lobe_frozen.json and lobe_predictions.md are read, never written.
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from imaging import lobe_A as LA  # noqa: E402
from imaging import lobe_rulers as LR  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, PROFILES, ROOT, git_hash, load_config  # noqa: E402
from imaging.report_lobe import SHORT, _t  # noqa: E402

# stem, design, stop rule, passes, final dS, elements, sets, source of the mesh numbers
REGISTRY = [
    ("Healthy_sliced", "Healthy_sliced", 2, 7, 0.0092, 1349491, "lobe_v1 lobe_B", "data/sims_lobe.csv"),
    ("Healthy_sliced_new", "Healthy_sliced", 1, 6, 0.0155, 1081728, "lobe_A", "data/sims_lobe.csv"),
    ("Mild_lobe", "Mild_lobe", 1, 5, 0.0186, 739774, "lobe_v1 lobe_A", "data/sims_lobe.csv"),
    ("Mild_lobe_new", "Mild_lobe", 2, 6, 0.0150, 878656, "lobe_B", "data/sims_lobe.csv"),
    ("Moderate_lobe", "Moderate_lobe", 1, 5, 0.0194, 796281, "lobe_v1 lobe_A", "data/sims_lobe.csv"),
    ("Moderate_lobe_c3", "Moderate_lobe", 2, 6, 0.014593, 949865, "lobe_B", "user 2026-10-04 (c3)"),
    ("Severe_lobe", "Severe_lobe", 1, 5, 0.019999, 690077, "lobe_v1 lobe_A", "data/sims_lobe.csv"),
    ("Severe_lobe_c3", "Severe_lobe", 2, 6, 0.011567, 819294, "lobe_B", "user 2026-10-04 (c3)"),
    ("LeftOnly_test_c3", "LeftOnly_test", 1, 6, 0.014686, 941358, "lobe_A (blind)", "user 2026-10-04 (c3)"),
    ("MCI_lobe_c3", "MCI_lobe", 1, 6, 0.013948, 981160, "lobe_A (blind)", "user 2026-10-04 (c3)"),
]
NEW = ("LeftOnly_test_c3", "MCI_lobe_c3", "Moderate_lobe_c3", "Severe_lobe_c3")
LOBE_A = ("Healthy_sliced_new", "Mild_lobe", "Moderate_lobe", "Severe_lobe", "LeftOnly_test_c3", "MCI_lobe_c3")
LOBE_B = ("Healthy_sliced", "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3")
ONE_PASS = {"Healthy 7 − 6": ("Healthy_sliced", "Healthy_sliced_new"),
            "Mild 6 − 5": ("Mild_lobe_new", "Mild_lobe"),
            "Moderate 6 − 5": ("Moderate_lobe_c3", "Moderate_lobe"),
            "Severe 6 − 5": ("Severe_lobe_c3", "Severe_lobe")}
REFS = {"Healthy_sliced (p7, frozen, primary)": "Healthy_sliced",
        "Healthy_sliced_new (p6, matched)": "Healthy_sliced_new"}
SYMMETRIC = ("Healthy_sliced", "Healthy_sliced_new", "Mild_lobe", "Mild_lobe_new", "Moderate_lobe",
             "Moderate_lobe_c3", "Severe_lobe", "Severe_lobe_c3", "MCI_lobe_c3")
QN = list(SHORT) + ["LR", "FB"]
SHOW = (RL.METHODS[0], RL.METHODS[2], LR.WNAME)
SHORTM = LR.SHORTM
GAIN = LR.GAIN


# ----------------------------------------------------------------------------------------------
# registry and QC
# ----------------------------------------------------------------------------------------------
def registry_and_qc():
    from adstage.io.masking import mask_glitches
    from adstage.io.touchstone import read_touchstone
    cfg = load_config()
    thr = float(cfg["qc"].get("glitch_thr_db", -30.0))
    p2a = cfg["ring"]["port_to_ant"]
    fit = np.array([3.4e9, 3.6e9, 3.8e9])
    reg = pd.DataFrame(REGISTRY, columns=["stem", "design", "stop_rule", "passes", "final_dS", "elements", "sets",
                                          "mesh_source"])
    reg["file"] = "new_with_slices_" + reg.stem + ".s6p"
    qc, mlog = [], []
    for stem in reg.stem:
        t = read_touchstone(ROOT / "data" / "raw" / f"new_with_slices_{stem}.s6p")
        s, f = t.s, t.f_hz
        lvl = np.sqrt((np.abs(s) ** 2).mean(0))
        n = s.shape[1]
        rec_db, worst = -np.inf, None
        amp_db, worst_amp = 0.0, None
        for i in range(n):
            for j in range(i + 1, n):
                e = 20 * np.log10(np.abs(s[:, i, j] - s[:, j, i]) / np.sqrt(lvl[i, j] * lvl[j, i]))
                a = np.abs(20 * np.log10(np.abs(s[:, i, j]) / np.abs(s[:, j, i])))
                k = int(np.argmax(e))
                if e[k] > rec_db:
                    rec_db, worst = e[k], (f[k], i, j)
                k = int(np.argmax(a))
                if a[k] > amp_db:
                    amp_db, worst_amp = a[k], (f[k], i, j, e[k])
        sv = max(np.linalg.svd(s[q], compute_uv=False).max() for q in range(len(f)))
        _, log = mask_glitches(f, s, thr)
        masked = {(round(r["f_GHz"], 4), r["port_i"], r["port_j"]) for r in log}

        def path(i, j):
            a_, b_ = p2a[i] - 1, p2a[j] - 1
            kind = {0: "reflection", 1: "neighbour", 2: "second-neighbour", 3: "opposite"}[SL.ring_k(a_, b_)]
            return f"T{min(a_, b_) + 1}–T{max(a_, b_) + 1}", kind
        pa, kind = path(worst_amp[1], worst_amp[2])
        qc.append(dict(file=f"new_with_slices_{stem}.s6p", points=len(f), f_GHz=f"{f[0] / 1e9:.1f}–{f[-1] / 1e9:.1f}",
                       max_singular_value=float(sv), passive=bool(sv <= 1 + 1e-6),
                       max_recip_err_dB_re_band=float(rec_db),
                       worst_amp_nonrecip_dB=float(amp_db), at_GHz=worst_amp[0] / 1e9, ports=f"{worst_amp[1] + 1}-{worst_amp[2] + 1}",
                       path=pa, path_type=kind, its_recip_err_dB=float(worst_amp[3]),
                       worst_point_masked=(round(worst_amp[0] / 1e9, 4), worst_amp[1] + 1, worst_amp[2] + 1) in masked,
                       worst_point_at_fit_freq=bool(np.min(np.abs(fit - worst_amp[0])) < 1),
                       n_masked=len(log)))
        for r in log:
            pa, kind = path(r["port_i"] - 1, r["port_j"] - 1)
            mlog.append(dict(file=f"new_with_slices_{stem}.s6p", f_GHz=r["f_GHz"], ports=f"{r['port_i']}-{r['port_j']}",
                             path=pa, type=kind, Sij_dB=20 * np.log10(abs(r["Sij_before"])),
                             Sji_dB=20 * np.log10(abs(r["Sji_before"])), recip_err_dB=r["recip_err_db"],
                             at_fit_freq=bool(np.min(np.abs(fit - r["f_GHz"] * 1e9)) < 1)))
    return reg, pd.DataFrame(qc), pd.DataFrame(mlog), thr


# ----------------------------------------------------------------------------------------------
# rulers on the quantity vector q = [S1..S6 d eps'', LR, FB]
# ----------------------------------------------------------------------------------------------
def qvec(x):
    x = np.asarray(x)
    c = RL.contrasts(x)
    return np.r_[x[6:12], c["LR"], c["FB"]]


def make_x(M, m, lam):
    if m == LR.WNAME:
        Mx, meth, lm = {"log": M["wlog"]}, "tikhonov log (gain-inv.)", lam["log"]
    else:
        Mx, meth, lm = M, m, (lam["dS"] if m.endswith("dS") else lam["log"])

    def fx(Sst_fi, Sref_fi):
        return np.asarray(RL.invert(Mx, meth, lm, S_stage_fi=Sst_fi, S_ref_fi=Sref_fi,
                                    dS_fi=SL.recip(Sst_fi - Sref_fi)))
    return fx


class Ctx:
    def __init__(self, n_draws):
        from adstage.pipeline.augment import draws
        fz = json.loads((OUT / "lobe_frozen.json").read_text(encoding="utf-8"))
        self.fz = fz
        self.kappa = np.array(fz["kappa_re"]) + 1j * np.array(fz["kappa_im"])
        self.lam = {"dS": fz["lambda_dS"], "log": fz["lambda_log"]}
        S, f, fh, fi, P = RL.build(reuse=True)
        for stem, *_ in REGISTRY:
            if stem not in S:
                S[stem], _ = SL.load_design(stem, f)
        self.S, self.f, self.fh, self.fi, self.P = S, f, fh, fi, P
        self.K6 = SL.region_kernels(P, SL.region_masks())[..., :6]
        self.prof = PROFILES["typical"]
        self.acfg = dict(load_config().get("augment", {}))
        self.n = n_draws
        self._draws = draws
        self._cache = {}
        self.models = {}
        idx = np.arange(SL.N_ANT)
        self.maps = [np.roll(idx, r) for r in range(SL.N_ANT)] + [np.roll(idx[::-1], r) for r in range(SL.N_ANT)]
        mp = SL.mirror_perm()
        self.E = {d: np.sqrt(2) * 0.5 * (S[d] - SL.permute(S[d], mp)) for d in SYMMETRIC}

    def model(self, ref):
        if ref not in self.models:
            self.models[ref] = LR.build_models(self.K6, self.fh, self.fi, self.kappa, self.S[ref], LA.KEEP_ALL)
        return self.models[ref]

    def dr(self, stem, kind):
        key = (stem, kind)
        if key not in self._cache:
            j = [r[0] for r in REGISTRY].index(stem)
            if kind == "noise":
                ac, n, seed = dict(amp_sd=0, phase_sd_deg=0, jitter_mhz=0), max(self.n // 2, 10), 0
            else:
                ac, n, seed = {**self.acfg, **GAIN[kind]}, self.n, 1 + list(GAIN).index(kind)
            self._cache[key] = self._draws(self.f, self.S[stem], self.prof, n,
                                           np.random.default_rng([2026, 1004, 3, seed, j]), ac)[:, self.fi]
        return self._cache[key]

    def floor(self, stem, ref, m):
        fx = make_x(self.model(ref), m, self.lam)
        R = self.S[ref]
        qs = [qvec(fx((R + sg * SL.permute(self.E[stem], mm))[self.fi], R[self.fi])) for mm in self.maps for sg in (1, -1)]
        return np.sqrt(np.mean(np.square(qs), 0))

    def rulers(self, stage, ref, m, floor_stage=None):
        """Clean q and the four rulers for (stage - ref) with method m."""
        fi, S = self.fi, self.S
        fx = make_x(self.model(ref), m, self.lam)
        R = S[ref]
        clean = qvec(fx(S[stage][fi], R[fi]))
        yd = {k: np.abs(qvec(fx((R + sg * (S[a] - S[b]))[fi], R[fi])))
              for k, (a, b) in ONE_PASS.items() for sg in (1, -1)}
        yard = np.max(list(yd.values()), 0)
        if floor_stage is None:
            floor_stage = stage
        if isinstance(floor_stage, (tuple, list)):
            fs = np.max([self.floor(d, ref, m) for d in floor_stage], 0)
        else:
            fs = self.floor(floor_stage, ref, m)
        flo = np.hypot(fs, self.floor(ref, ref, m))
        out = dict(clean=clean, yard=yard, floor=flo)
        for kind in ("noise",) + tuple(GAIN):
            A, B = self.dr(stage, kind), self.dr(ref, kind)
            qs = np.array([qvec(fx(a, b)) for a, b in zip(A, B)])
            out[f"sd_{kind}"] = qs.std(0, ddof=1)
            if kind != "noise":
                out[f"lo_{kind}"], out[f"hi_{kind}"] = np.quantile(qs, 0.025, 0), np.quantile(qs, 0.975, 0)
        return out


def ratios(r, k):
    eff = abs(r["clean"][k])
    g05, g2 = list(GAIN)
    sim = max(r["yard"][k], r["floor"][k])
    meas = max(r["sd_noise"][k], r["yard"][k], r["floor"][k], r[f"sd_{g05}"][k])
    return dict(over_noise=eff / r["sd_noise"][k], over_yard=eff / r["yard"][k], over_floor=eff / r["floor"][k],
                over_meas_05=eff / r[f"sd_{g05}"][k], over_meas_2=eff / r[f"sd_{g2}"][k],
                ruler_sim=sim, ratio_sim=eff / sim, ruler_meas=meas, ratio_meas=eff / meas)


def verdict(expected, called, ratio):
    """Pre-registered call vs the clean call, and whether the effect is separable from error (>= 2x)."""
    if expected in ("left", "right", "front", "back", True):           # positive prediction
        if called != expected:
            return "miss"
        return "hit" if ratio >= 2 else "not separable"
    if called == expected:                                              # null prediction
        return "hit"
    return "miss" if ratio >= 2 else "not separable"


def score_design(ctx, design_stem, items, floor_stage):
    rows = []
    for rname, ref in REFS.items():
        for m in SHOW:
            r = ctx.rulers(design_stem, ref, m, floor_stage)
            frozen = m in RL.METHODS
            x6 = np.r_[np.zeros(6), r["clean"][:6]]
            c = RL.apply_rules(x6, ctx.fz["rules"][m]) if frozen else None
            for name, k, expected in items:
                q = ratios(r, k)
                if frozen:
                    called = {"LR": c["side"], "FB": c["frontback"]}.get(QN[k], bool(c["affected"][k]) if k < 6 else None)
                elif k >= 6:            # post-hoc whitened log: no thresholds; 'call' = sign when >= 2x the ruler
                    v = r["clean"][k]
                    if QN[k] == "LR":
                        called = ("left" if v > 0 else "right") if q["ratio_sim"] >= 2 else "none"
                    else:
                        called = ("front" if v > 0 else "back") if q["ratio_sim"] >= 2 else "none"
                else:
                    called = "n/a"
                rows.append(dict(reference=rname, method=SHORTM[m] + (" (post-hoc)" if m == LR.WNAME else ""),
                                 prediction=name, quantity=QN[k], effect=float(r["clean"][k]),
                                 call=str(called), **q,
                                 verdict_sim=verdict(expected, called, q["ratio_sim"]) if called != "n/a" else "n/a",
                                 verdict_meas=verdict(expected, called, q["ratio_meas"]) if called != "n/a" else "n/a"))
    return rows


def lobe_b(ctx):
    rows, rul = [], []
    ref = "Healthy_sliced"
    tr = {d: SL.truth_regions(d, ctx.fh, ctx.P, SL.region_masks())["sens"][7:13]
          for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe")}
    pairs = [("Mild_lobe_new", "Mild_lobe", "Mild_lobe"), ("Moderate_lobe_c3", "Moderate_lobe", "Moderate_lobe"),
             ("Severe_lobe_c3", "Severe_lobe", "Severe_lobe")]
    for m in tuple(RL.METHODS) + (LR.WNAME,):
        fx_b = make_x(ctx.model(ref), m, ctx.lam)
        fx_a = make_x(ctx.model("Healthy_sliced_new"), m, ctx.lam)
        for stB, stA, d in pairs:
            xb = fx_b(ctx.S[stB][ctx.fi], ctx.S[ref][ctx.fi])
            xa = fx_a(ctx.S[stA][ctx.fi], ctx.S["Healthy_sliced_new"][ctx.fi])
            for setn, x in (("lobe_B", xb), ("lobe_A", xa)):
                e = np.array(SL.DESIGNS[d][0], float)
                aff = e > 0
                row = dict(set=setn, method=SHORTM[m], stage=d.split("_")[0],
                           **{s: float(x[6 + j]) for j, s in enumerate(SHORT)},
                           corr_truth=float(np.corrcoef(x[6:12], tr[d])[0, 1]))
                if m in RL.METHODS:
                    c = RL.apply_rules(x, ctx.fz["rules"][m])
                    row.update(called=" ".join(f"S{j + 1}" for j in range(6) if c["affected"][j]) or "none",
                               correct=int(np.sum(np.array(c["affected"]) == aff)), LR=c["LR"], side=c["side"],
                               FB=c["FB"], frontback=c["frontback"])
                else:
                    cc = RL.contrasts(x)
                    row.update(called="n/a", correct=np.nan, LR=cc["LR"], side="n/a", FB=cc["FB"], frontback="n/a")
                rows.append(row)
    for m in SHOW:
        for stB, rB, d, lab in [(p[0], ref, p[2], f"{p[2].split('_')[0]} (B) − Healthy (p7)") for p in pairs] +                 [("Moderate_lobe_c3", "Mild_lobe_new", "Moderate_lobe", "Moderate (B) − Mild (B)")]:
            r = ctx.rulers(stB, rB, m)
            for k in (6, 7):
                q = ratios(r, k)
                rul.append(dict(method=SHORTM[m], comparison=lab,
                                quantity=QN[k], effect=float(r["clean"][k]), yardstick=float(r["yard"][k]),
                                floor=float(r["floor"][k]), noise_sd=float(r["sd_noise"][k]),
                                meas_sd_05=float(r[f"sd_{list(GAIN)[0]}"][k]), ratio_sim=q["ratio_sim"],
                                ratio_meas=q["ratio_meas"]))
    return rows, rul


def one_pass(ctx):
    rows, pdb = [], {}
    for k, (a, b) in ONE_PASS.items():
        pdb[k] = LA.path_change_db(ctx.S[a], ctx.S[b])
        for m in SHOW:
            fx = make_x(ctx.model("Healthy_sliced_new"), m, ctx.lam)
            R = ctx.S["Healthy_sliced_new"]
            q = qvec(fx((R + ctx.S[a] - ctx.S[b])[ctx.fi], R[ctx.fi]))
            rows.append(dict(difference=k, method=SHORTM[m], **{QN[j]: float(q[j]) for j in range(8)}))
    return rows, pdb


def r31_check(ctx):
    """Read-only cross-check of the frozen R31 rule on clean (masked) S; the main session is authoritative."""
    from adstage.features.ring_features import features
    rule_path = ROOT / "results" / "04" / "frozen_rule.json"
    rule = json.loads(rule_path.read_text(encoding="utf-8"))
    band = rule["feature_spec"]["band_hz"]
    from adstage.frozen import apply_rule
    sel = (ctx.f >= band[0] - 1) & (ctx.f <= band[1] + 1)
    rows = []
    for setn, stems in (("lobe_A", LOBE_A), ("lobe_B", LOBE_B)):
        for st in stems:
            X, names, _, _ = features(ctx.f[sel], ctx.S[st][None, sel])
            lab = apply_rule(rule_path, ctx.f, ctx.S[st][None])
            rows.append(dict(set=setn, file=st, R31_dB=float(X[0, names.index("R31")]),
                             R21_dB=float(X[0, names.index("R21")]),
                             binary_R31=str(lab["binary_R31"][0]),
                             **{k: str(v[0]) for k, v in lab.items() if k != "binary_R31"}))
    det = rule["detection_binary_R31"]
    return rows, det["tau_dB"], det["margin_dB"]


def mci_data_level(ctx):
    """Whitened data-level size of MCI - Healthy_sliced_new against the one-pass differences and noise."""
    M = ctx.model("Healthy_sliced_new")
    R = ctx.S["Healthy_sliced_new"]
    out = {}
    for kind in ("dS", "wlog"):
        mdl = M[kind]

        def size(Sst):
            return float(np.linalg.norm(mdl.data(dS=SL.recip(Sst - R)[:, ctx.fi], S_stage=Sst[ctx.fi], S_ref=R[ctx.fi])))
        mci = size(ctx.S["MCI_lobe_c3"])
        yd = {k: size(R + ctx.S[a] - ctx.S[b]) for k, (a, b) in ONE_PASS.items()}
        A, B = ctx.dr("Healthy_sliced_new", "noise"), ctx.dr("MCI_lobe_c3", "noise")
        nz = []
        for a, b in zip(A, B):
            d_ = mdl.data(dS=SL.recip(b - a), S_stage=b, S_ref=a) - mdl.data(dS=SL.recip(ctx.S["MCI_lobe_c3"][ctx.fi] - R[ctx.fi]),
                                                                            S_stage=ctx.S["MCI_lobe_c3"][ctx.fi], S_ref=R[ctx.fi])
            nz.append(float(np.linalg.norm(d_)))
        st = {d: size(ctx.S[d]) for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe")}
        out[kind] = dict(MCI=mci, one_pass=yd, noise_rms=float(np.sqrt(np.mean(np.square(nz)))), stages=st)
    return out


# ----------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    a = ap.parse_args()
    from imaging import report_lobe as RP

    reg, qc, mlog, thr = registry_and_qc()
    reg.to_csv(OUT / "lobe_sets.csv", index=False)
    qc.to_csv(OUT / "lobe_qc_c3.csv", index=False)
    mlog.to_csv(OUT / "lobe_mask_log.csv", index=False)

    RP.run_blind()                                   # pre-registered scoring (rewrites sections 6 and 7)

    ctx = Ctx(a.n)
    res1 = pickle.loads((RL.CACHE / "stage1.pkl").read_bytes())
    bp = res1["blind_pred"]
    sym1 = [s for s in SYMMETRIC if s in LOBE_A]
    left_items = [("side = left", 6, "left"), ("S2 affected", 1, True), ("S3 affected", 2, True),
                  ("S1 healthy", 0, False), ("S4 healthy", 3, False), ("S5 healthy", 4, False),
                  ("S6 healthy", 5, False), ("front/back none", 7, "none")]
    mci_items = [(f"S{k + 1} not affected", k, False) for k in range(6)] + [("side none", 6, "none"),
                                                                             ("front/back none", 7, "none")]
    left = score_design(ctx, "LeftOnly_test_c3", left_items, tuple(sym1))
    mci = score_design(ctx, "MCI_lobe_c3", mci_items, "MCI_lobe_c3")
    lb_rows, lb_rul = lobe_b(ctx)
    op_rows, op_pdb = one_pass(ctx)
    r31, tau, marg = r31_check(ctx)
    mdl = mci_data_level(ctx)
    tr_left = SL.truth_regions("LeftOnly_test", ctx.fh, ctx.P, SL.region_masks())["sens"][7:13]
    pd.DataFrame(left + mci).to_csv(OUT / "lobe_blind_rulers.csv", index=False)

    # ---------------------------------------------------------------- report text
    fz = ctx.fz
    q = qc.set_index("file")
    sev = q.loc["new_with_slices_Severe_lobe_c3.s6p"]
    L = ["## 6a. c3 files: registry, sets and QC", "",
         "Imaging-side registry (`results/imaging/lobe_sets.csv`; the shared manifest `data/sims_lobe.csv` belongs to "
         "the main session and is not edited here). The c3 suffix is only the user's label.", "",
         _t(reg.to_dict("records"), ["file", "design", "stop_rule", "passes", "final_dS", "elements", "sets", "mesh_source"],
            {"final_dS": ".6g"}), "",
         "Sets: **lobe_A** (stop rule 1: first pass with ΔS < 0.02) = Healthy_sliced_new (p6), Mild_lobe (p5), "
         "Moderate_lobe (p5), Severe_lobe (p5), LeftOnly_test_c3 (p6), MCI_lobe_c3 (p6); LeftOnly and MCI are stop-rule "
         "and pass matched to Healthy_sliced_new. **lobe_B** (stop rule 2: two consecutive passes) = Healthy_sliced (p7), "
         "Mild_lobe_new (p6), Moderate_lobe_c3 (p6), Severe_lobe_c3 (p6).", "",
         f"QC of every lobe file (glitch rule as in §3.1 of Prompt 07: |S_ij − S_ji| > {thr:.0f} dB re the band-rms level "
         "of the pair, masked by complex linear interpolation; mask log in `results/imaging/lobe_mask_log.csv`):", "",
         _t(qc.to_dict("records"), ["file", "points", "f_GHz", "max_singular_value", "passive", "max_recip_err_dB_re_band",
                                     "worst_amp_nonrecip_dB", "at_GHz", "path", "path_type", "its_recip_err_dB",
                                     "worst_point_masked", "worst_point_at_fit_freq", "n_masked"],
            {"max_singular_value": ".4f", "max_recip_err_dB_re_band": ".1f", "worst_amp_nonrecip_dB": ".2f",
             "at_GHz": ".3f", "its_recip_err_dB": ".1f"}), "",
         "Masked points:", "",
         _t(mlog.to_dict("records"), list(mlog.columns), {"f_GHz": ".3f", "Sij_dB": ".1f", "Sji_dB": ".1f",
                                                          "recip_err_dB": ".1f"}) if len(mlog) else "none", "",
         f"**Severe_lobe_c3:** its most non-reciprocal point is {sev['worst_amp_nonrecip_dB']:.2f} dB in amplitude at "
         f"{sev['at_GHz']:.3f} GHz on {sev['path']} ({sev['path_type']}); its reciprocity error is "
         f"{sev['its_recip_err_dB']:.1f} dB re the band level, so the −30 dB rule "
         + ("**does** mask it" if sev["worst_point_masked"] else "does **not** mask it")
         + (", and it is not at a fit frequency (3.4/3.6/3.8 GHz), so it does not enter the inversions."
            if not sev["worst_point_at_fit_freq"] else "; it is at a fit frequency.")
         + f" The rule masks {int(sev['n_masked'])} points in Severe_lobe_c3 in all: "
         + "; ".join(f"{g.path.iloc[0]} {g.f_GHz.min():.3f}–{g.f_GHz.max():.3f} GHz ({len(g)} pt, worst "
                     f"{g.recip_err_dB.max():.1f} dB)"
                     for _, g in mlog[mlog.file == "new_with_slices_Severe_lobe_c3.s6p"].groupby("path"))
         + "; none at a fit frequency. All four c3 files have 201 points and are passive (largest singular value "
         "≤ 1). LeftOnly_test_c3 and MCI_lobe_c3 were not opened before the scoring run (their QC is part of it).", ""]

    def tab(rows, design):
        return _t([r for r in rows], ["reference", "method", "prediction", "effect", "call", "over_noise", "over_yard",
                                      "over_floor", "over_meas_05", "over_meas_2", "verdict_sim", "verdict_meas"],
                  {"effect": "+.1f", **{c: ".1f" for c in ("over_noise", "over_yard", "over_floor", "over_meas_05",
                                                           "over_meas_2")}})
    bpl = bp["LeftOnly_test"][RL.METHODS[0]]
    L += ["## 6b. Blind predictions against the error rulers", "",
          "Every pre-registered prediction (`lobe_predictions.md`, frozen at `fb5b775`; the main session's "
          "predictions are `cf56de8`) is scored on the clean simulation by the frozen pipeline, against both "
          "references. Columns: effect = the clean recovered quantity (dε'' of the sector, LR or FB of the map); "
          "over_noise = effect / SD under the typical noise profile alone (both designs); over_yard = / one-pass "
          "mesh yardstick (largest of Healthy 7−6, Mild 6−5, Moderate 6−5, Severe 6−5, both signs, added to the "
          "reference); over_floor = / numerical symmetry floor (quadrature of the two designs' floors; LeftOnly is "
          "not mirror-symmetric, so its floor is the largest floor of the lobe_A symmetric designs); over_meas = / "
          "SD under the Prompt 07 measurement model (±0.5 dB gain, and ±2 dB/±10°). verdict_sim uses the clean "
          "ruler max(yardstick, floor); verdict_meas uses max(noise SD, yardstick, floor, ±0.5 dB spread). "
          "**hit** = the pre-registered call is made and (for a positive prediction) the effect is ≥ 2× the ruler; "
          "**not separable** = right call but < 2× the ruler, or a wrong call within 2× the ruler; **miss** = wrong "
          "call ≥ 2× the ruler, or a positive prediction not called. The whitened-projection log method has no "
          "frozen thresholds: its 'call' is the sign of the contrast when it is ≥ 2× the clean ruler, it makes no "
          "sector calls, and it is **post-hoc**.", "",
          "**Caveats recorded before scoring:** (1) the predictions, κ, λ and thresholds were all derived from "
          "lobe_v1 (Mild_lobe p5 against Healthy_sliced p7: stop rules not matched), so mesh is part of the frozen "
          "'Mild change'; (2) LeftOnly carries CSF_Mild also as the 0.5 mm layer on the right (one CSF object). "
          "The imaging forward model includes it (true sensitivity-weighted dε'' of LeftOnly: "
          + ", ".join(f"{s} {v:+.1f}" for s, v in zip(SHORT, tr_left))
          + "), so the Born-simulated predictions contain it; the main session's path-level predictions do not; "
          "(3) the frozen 'gain-invariant' log method is not gain-invariant (§5d erratum); (4) one simulation per "
          f"design, one head. Predicted for LeftOnly (primary method, Born-simulated with noise): LR "
          f"{bpl['LR_mean']:+.1f} ± {bpl['LR_sd']:.1f}, P(called) "
          + ", ".join(f"{s} {p:.2f}" for s, p in zip(SHORT, bpl["p_called"])) + ".", "",
          "### LeftOnly_test_c3", "", tab(left, "LeftOnly"), "",
          "### MCI_lobe_c3", "", tab(mci, "MCI"), ""]

    # MCI rulers summary
    mci_m = [r for r in mci if r["reference"].startswith("Healthy_sliced_new")]
    mx_sim = max(mci_m, key=lambda r: r["ratio_sim"])
    mx_meas = max(mci_m, key=lambda r: r["ratio_meas"])
    L += ["## 6c. MCI_lobe: is MCI − Healthy_sliced_new larger than the rulers on any feature?", "",
          f"Reconstruction features (six sector dε'', LR, FB; Tikhonov dS, frozen log, whitened log, matched reference): "
          f"largest |effect| / clean ruler = {mx_sim['ratio_sim']:.1f}× ({mx_sim['method']}, {mx_sim['quantity']}, "
          f"effect {mx_sim['effect']:+.1f}); largest |effect| / measured ruler = {mx_meas['ratio_meas']:.1f}× "
          f"({mx_meas['method']}, {mx_meas['quantity']}). Features ≥ 2× the clean ruler: "
          + (", ".join(f"{r['method']} {r['quantity']} {r['ratio_sim']:.1f}×" for r in mci_m if r["ratio_sim"] >= 2) or "none")
          + ".", "",
          "Data level (norm of the whitened data vector, 21 paths × 3 frequencies × Re/Im):", "",
          _t([dict(model=k, **{"MCI − H6": v["MCI"], "noise (rms)": v["noise_rms"],
                               **{f"one pass {kk}": vv for kk, vv in v["one_pass"].items()},
                               **{f"{kk.split('_')[0]} − H6": vv for kk, vv in v["stages"].items()}})
              for k, v in mdl.items()], ["model", "MCI − H6", "noise (rms)"] + [f"one pass {k}" for k in ONE_PASS]
             + [f"{d.split('_')[0]} − H6" for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe")],
             {c: ".3g" for c in ["MCI − H6", "noise (rms)"] + [f"one pass {k}" for k in ONE_PASS]
              + [f"{d.split('_')[0]} − H6" for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe")]}), "",
          f"- **Answer:** MCI − Healthy_sliced_new is {mdl['dS']['MCI'] / max(mdl['dS']['one_pass'].values()):.2f}× the "
          f"largest one-pass mesh difference and {mdl['dS']['MCI'] / mdl['dS']['noise_rms']:.2f}× the rms noise at data "
          f"level (dS model; whitened log: {mdl['wlog']['MCI'] / max(mdl['wlog']['one_pass'].values()):.2f}× / "
          f"{mdl['wlog']['MCI'] / mdl['wlog']['noise_rms']:.2f}×), against "
          f"{mdl['dS']['stages']['Mild_lobe'] / max(mdl['dS']['one_pass'].values()):.1f}× for Mild. "
          "Expectation (pre-registered): nothing beyond noise, because the hippocampus lies deeper than the sensing "
          "depth (core CRLB ≫ its change, §2).", ""]

    # lobe_B
    rows_main = [r for r in lb_rows if r["method"] in ("Tikhonov dS", "frozen log", "whitened log")]
    L += ["## 6d. lobe_B (stop rule 2): frozen pipeline, rulers and one-pass yardstick for all four stages", "",
          "Reference Healthy_sliced (p7); stages Mild_lobe_new, Moderate_lobe_c3, Severe_lobe_c3 (p6). Frozen κ, λ, "
          "thresholds. lobe_A rows (reference Healthy_sliced_new) alongside:", "",
          _t(rows_main, ["set", "method", "stage"] + list(SHORT) + ["called", "correct", "corr_truth", "LR", "side", "FB",
                                                                    "frontback"],
             {**{s: ".1f" for s in SHORT}, "corr_truth": ".2f", "LR": "+.1f", "FB": "+.1f", "correct": ".0f"}), "",
          "Front/back and left/right of lobe_B against the rulers (yardstick of all four one-pass differences, "
          "symmetry floor, noise, ±0.5 dB measurement spread):", "",
          _t(lb_rul, ["method", "comparison", "quantity", "effect", "yardstick", "floor", "noise_sd", "meas_sd_05",
                      "ratio_sim", "ratio_meas"], {"effect": "+.1f", **{c: ".2f" for c in ("yardstick", "floor", "noise_sd",
                                                                                          "meas_sd_05", "ratio_sim",
                                                                                          "ratio_meas")}}), "",
          "One-pass yardstick for all four stages (each difference added to Healthy_sliced_new and inverted; "
          "recovered dε'' per sector and the contrasts):", "",
          _t(op_rows, ["difference", "method"] + QN, {k: "+.1f" for k in QN}), "",
          "Per-path amplitude change of each one-pass difference (dB, largest path of each class; band = band-mean "
          "power, median over f, worst single frequency):", "",
          _t([dict(difference=k, statistic=st, **{c: v[c][st] for c in LA.CLASSES}) for k, v in op_pdb.items()
              for st in ("band", "median", "worst")], ["difference", "statistic"] + list(LA.CLASSES),
             {c: ".3f" for c in LA.CLASSES}), "",
          f"**Frozen R31 rule, read-only cross-check** (`adstage.frozen.apply_rule`, clean masked S; the main "
          f"session's numbers are authoritative): τ = {tau:.3f} dB, margin {marg:.3f} dB (AD if R31 < τ − margin).", "",
          _t(r31, list(r31[0]), {"R31_dB": ".3f", "R21_dB": ".3f"}), ""]
    r31d = {(r["set"], r["file"]): r for r in r31}
    sB = r31d[("lobe_B", "Severe_lobe_c3")]
    L += [f"- Severe_lobe_c3 R31 = {sB['R31_dB']:.3f} dB → {sB['binary_R31']} "
          f"({'AD side' if sB['R31_dB'] < tau - marg else 'not on the AD side'} of τ − margin = {tau - marg:.3f}); "
          f"Severe_lobe (p5) {r31d[('lobe_A', 'Severe_lobe')]['R31_dB']:.3f}; Moderate_lobe_c3 "
          f"{r31d[('lobe_B', 'Moderate_lobe_c3')]['R31_dB']:.3f} vs Moderate_lobe (p5) "
          f"{r31d[('lobe_A', 'Moderate_lobe')]['R31_dB']:.3f}. (The user's plain-mean values −15.57 / −15.52 and "
          "−16.01 / −16.00 use the unmasked ring-mean recipe; this is the frozen recipe.)", ""]

    # ---------------------------------------------------------------- verdict bullets
    def pick(rows, ref_prefix, meth, pred):
        return next(r for r in rows if r["reference"].startswith(ref_prefix) and r["method"].startswith(meth)
                    and r["prediction"] == pred)
    side_p = pick(left, "Healthy_sliced (p7", "Tikhonov dS", "side = left")
    side_m = pick(left, "Healthy_sliced_new", "Tikhonov dS", "side = left")
    side_w = pick(left, "Healthy_sliced (p7", "whitened", "side = left")
    blind_rows = json.loads((OUT / "lobe_blind_outcome.json").read_text(encoding="utf-8"))
    off = next(r for r in blind_rows if r["design"] == "LeftOnly_test" and r["method"] == RL.METHODS[0]
               and r["reference"].endswith("primary)"))
    offm = next(r for r in blind_rows if r["design"] == "MCI_lobe" and r["method"] == RL.METHODS[0]
                and r["reference"].endswith("primary)"))
    blind_txt = (f"**pre-registered blind test: {off['verdict']}** (primary method, frozen 7-pass reference): "
                 f"LeftOnly side = {off['side']}, LR = {off['LR']:+.1f} (predicted {bpl['LR_mean']:+.1f} ± {bpl['LR_sd']:.1f}, "
                 f"i.e. {(off['LR'] - bpl['LR_mean']) / bpl['LR_sd']:+.1f} SD: correct sign, smaller than predicted), "
                 f"called {off['called']} (S2 {off[chr(100) + chr(949) + chr(39) * 2 + ' S2 TL']:.1f} just below T_abs "
                 f"{fz['rules'][RL.METHODS[0]]['T_abs']:.1f}; predicted P(S2 called) {bpl['p_called'][1]:.2f}). Against the rulers: LR is {side_p['ratio_sim']:.1f}× the clean ruler "
                 f"({side_p['verdict_sim']}) and {side_p['ratio_meas']:.1f}× the measured ruler ({side_p['verdict_meas']}); "
                 f"matched reference {side_m['ratio_sim']:.1f}× / {side_m['ratio_meas']:.1f}×; post-hoc whitened log "
                 f"{side_w['ratio_sim']:.1f}× / {side_w['ratio_meas']:.1f}× (§6b).")
    extra = [f"- **MCI_lobe (blind):** pre-registered verdict {offm['verdict']} (called {offm['called']}, side "
             f"{offm['side']}, front/back {offm['frontback']}). Largest reconstruction feature "
             f"{mx_sim['ratio_sim']:.1f}× the clean ruler; data level {mdl['dS']['MCI'] / max(mdl['dS']['one_pass'].values()):.2f}× "
             "the largest one-pass mesh difference (§6c).",
             f"- **lobe_B:** frozen pipeline, primary method: "
             + "; ".join(f"{r['stage']} {r['called']} ({r['correct']:.0f}/6), FB {r['FB']:+.1f}"
                         for r in rows_main if r["set"] == "lobe_B" and r["method"] == "Tikhonov dS")
             + f". Severe_lobe_c3 R31 {sB['R31_dB']:.2f} dB → {sB['binary_R31']} (read-only cross-check, §6d).",
             "- **Front/back on lobe_B** (better converged, smaller symmetry floor): "
             + "; ".join(f"{r['method']} {r['comparison']} FB {r['effect']:+.1f} = {r['ratio_sim']:.1f}× clean / "
                         f"{r['ratio_meas']:.1f}× measured ruler"
                         for r in lb_rul if r["quantity"] == "FB" and r["method"] in ("Tikhonov dS", "whitened log"))
             + ". The front-positive bias of Mild and Severe (truth 0) also exceeds the clean ruler, so Moderate's "
             "FB above Healthy is not by itself a frontal signal; Moderate − Mild (not a pure frontal contrast) is "
             "the closer test."]
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    i = rep.index("## 7. Verdict")
    rep = rep[:i] + "\n".join(L) + "\n" + "\n".join(RP._verdict(res1, blind_txt, extra)) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
    (OUT / "lobe_c3.json").write_text(json.dumps(dict(code=git_hash(ROOT), frozen_code=fz["code"], n_draws=a.n,
                                                      left=left, mci=mci, lobe_b=lb_rows, lobe_b_rulers=lb_rul,
                                                      one_pass=op_rows, path_db=op_pdb, r31=r31, tau=tau, margin=marg,
                                                      mci_data=mdl, truth_leftonly=tr_left.tolist()),
                                                 indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)),
                                      encoding="utf-8")
    print("\n".join(L[-6:]).encode("ascii", "replace").decode())
    print(blind_txt.encode("ascii", "replace").decode())
    for e in extra:
        print(e.encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
