"""Lobe study on the mesh-matched set lobe_A (4 Oct), frozen pipeline unchanged:

    python imaging/lobe_A.py

lobe_A = Healthy_sliced_new (reference) + Mild_lobe, Moderate_lobe, Severe_lobe. The frozen kappa,
lambdas and calling thresholds (results/imaging/lobe_frozen.json) are applied as they are; only the
reference changes (noise weights and the log-ratio reference are built from Healthy_sliced_new).
Mesh yardstick = one extra adaptive pass: Healthy_sliced (7 passes) - Healthy_sliced_new (6) and
Mild_lobe_new (6) - Mild_lobe (5), each passed through the pipeline as if it were a stage.
Every result is given with all 21 pairs and without the 3 opposite paths (T1-T4, T2-T5, T3-T6).
Writes results/imaging/lobe_A.json and inserts section 5c into lobe_report.md.
"""
from __future__ import annotations

import json
import pickle
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402

from imaging import run_lobe as RL  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, PROFILES, ROOT, git_hash  # noqa: E402
from imaging.report_lobe import SHORT, _t  # noqa: E402

STAGES = ("Mild_lobe", "Moderate_lobe", "Severe_lobe")
OPP = np.array([SL.ring_k(a, b) == 3 for a, b in SL.PAIRS])
KEEP_ALL = np.ones(len(SL.PAIRS), bool)
KEEP_NOOPP = ~OPP
PASSES = {"Healthy_sliced": 7, "Healthy_sliced_new": 6, "Mild_lobe": 5, "Mild_lobe_new": 6}


class SubModel(SL.RegionModel):
    """RegionModel restricted to a subset of pairs. For kind='log' the gain projector is rebuilt on
    the kept pairs, so the dropped paths do not enter through the projection either."""

    def __init__(self, K, fh, kappa, sig, keep, S_ref=None, kind="dS"):
        self.keep = np.asarray(keep, bool)
        self.fh, self.kind = np.asarray(fh), kind
        nreg = K.shape[-1]
        Kc = K * kappa[None, :, None]
        Kc = np.concatenate([Kc, -1j * Kc * (SL.F_C / self.fh)[None, :, None]], -1)[self.keep]
        sig = sig[self.keep]
        self.nreg = nreg
        if kind == "dS":
            self.w = 1 / (sig / np.sqrt(2))
            self.Jc = Kc * self.w[..., None]
        else:
            Sr = SL.recip(S_ref)[self.keep]
            Jl = Kc / Sr[..., None]
            self.w = 1 / (sig / np.abs(Sr) / np.sqrt(2))
            A = np.zeros((int(self.keep.sum()), SL.N_ANT))
            for i, (a, b) in enumerate(np.array(SL.PAIRS)[self.keep]):
                A[i, a] += 1
                A[i, b] += 1
            self.Pg = np.eye(len(A)) - A @ np.linalg.pinv(A)
            self.Jc = np.stack([self.Pg @ (Jl[:, fi] * self.w[:, fi, None]) for fi in range(len(fh))], 1)
        self.J = np.concatenate([self.Jc.real.reshape(-1, 2 * nreg), self.Jc.imag.reshape(-1, 2 * nreg)], 0)

    def data(self, dS=None, S_stage=None, S_ref=None):
        if self.kind == "dS":
            d = dS[self.keep] * self.w
        else:
            y = np.log(SL.recip(S_stage)) - np.log(SL.recip(S_ref))
            y = (y - 2j * np.pi * np.round(np.imag(y) / (2 * np.pi)))[self.keep]
            d = np.stack([self.Pg @ (y[:, fi] * self.w[:, fi]) for fi in range(len(self.fh))], 1)
        return np.r_[d.real.ravel(), d.imag.ravel()]


def models(K6, fh, fi, kappa, Href, keep):
    sig = SL.pair_sigma_f(Href, PROFILES["typical"])[:, fi]
    return {"dS": SubModel(K6, fh, kappa, sig, keep, kind="dS"),
            "log": SubModel(K6, fh, kappa, sig, keep, S_ref=Href[fi], kind="log")}


CLASSES = ("reflection", "neighbour", "second-neighbour", "opposite")


def path_change_db(A, B):
    """Amplitude change per path class (largest over the paths of the class), three statistics:
    band = |10 log10 of the band-mean power ratio|; median = median over f of |20 log10 |A/B||;
    worst = max over f (dominated by spectral notches, where |S| is small)."""
    a, b = np.abs(SL.recip(A)), np.abs(SL.recip(B))
    r = np.abs(20 * np.log10(a / b))
    band = np.abs(10 * np.log10(np.nanmean(a ** 2, 1) / np.nanmean(b ** 2, 1)))
    out = {}
    for k, nm in enumerate(CLASSES):
        sel = np.array([SL.ring_k(x, y) == k for x, y in SL.PAIRS])
        out[nm] = dict(band=float(np.nanmax(band[sel])), median=float(np.nanmax(np.nanmedian(r[sel], 1))),
                       worst=float(np.nanmax(r[sel])))
    return out


def compute():
    fz = json.loads((OUT / "lobe_frozen.json").read_text(encoding="utf-8"))
    kappa = np.array(fz["kappa_re"]) + 1j * np.array(fz["kappa_im"])
    lam = {"dS": fz["lambda_dS"], "log": fz["lambda_log"]}
    S, f, fh, fi, P = RL.build(reuse=True)
    names = ["Healthy_sliced_new", "Mild_lobe_new", "Moderate_lobe_new", "Severe_lobe_new"]
    for nm in names:
        S[nm], _ = SL.load_design(nm, f)
    H6, H7 = S["Healthy_sliced_new"], S["Healthy_sliced"]
    same = {nm: float(np.nanmax(np.abs(S[nm] - S[nm.replace("_new", "")]))) for nm in names[1:]}
    pairs = {"Healthy 7 - 6 passes": ("Healthy_sliced", "Healthy_sliced_new"),
             "Mild 6 - 5 passes": ("Mild_lobe_new", "Mild_lobe")}
    for d in ("Moderate", "Severe"):                    # stop-rule-2 re-solves (c3 delivery, 4 Oct), if present
        if (ROOT / "data" / "raw" / f"new_with_slices_{d}_lobe_c3.s6p").exists():
            S[f"{d}_lobe_c3"], _ = SL.load_design(f"{d}_lobe_c3", f)
            pairs[f"{d} 6 - 5 passes"] = (f"{d}_lobe_c3", f"{d}_lobe")
    yard_in = {k: S[a] - S[b] for k, (a, b) in pairs.items()}
    path_db = {k: path_change_db(S[a], S[b]) for k, (a, b) in pairs.items()}
    masks = SL.region_masks()
    K6 = SL.region_kernels(P, masks)[..., :6]
    truth = {d: SL.truth_regions(d, fh, P, masks) for d in STAGES}
    res = dict(code=git_hash(ROOT), frozen_code=fz["code"], identical_new=same, path_db=path_db, variants={},
               f_GHz=fz["f_GHz"])
    old = pickle.loads((RL.CACHE / "stage1.pkl").read_bytes())
    res["old_fits"] = {m: {d: np.asarray(x).tolist() for d, x in old["fits"][m].items()} for m in RL.METHODS}
    for vname, keep in (("all 21 paths", KEEP_ALL), ("without opposite paths", KEEP_NOOPP)):
        M = models(K6, fh, fi, kappa, H6, keep)
        Mall = models(K6, fh, fi, kappa, H6, KEEP_ALL)
        v = {"fits": {}, "yard": {}, "info_opp": {}, "data_opp": {}}
        for m in RL.METHODS:
            lm = lam["dS"] if m.endswith("dS") else lam["log"]

            def run(Sst, Sref):
                return RL.invert(M, m, lm, S_stage_fi=Sst[fi], S_ref_fi=Sref[fi], dS_fi=SL.recip(Sst - Sref)[:, fi])
            v["fits"][m] = {d: run(S[d], H6) for d in STAGES}
            v["yard"][m] = {f"{sg}({k})": run(H6 + (1 if sg == "+" else -1) * y, H6)
                            for k, y in yard_in.items() for sg in "+-"}
        # dependence on the opposite paths (all-path model): Fisher-information and data-energy shares
        for kind in ("dS", "log"):
            J = Mall[kind].J
            nrow = J.shape[0] // 2
            rows = np.tile(np.repeat(OPP, len(fh)), 2)
            assert rows.size == 2 * nrow
            v["info_opp"][kind] = (np.sum(J[rows] ** 2, 0) / np.sum(J ** 2, 0))[6:12].tolist()
            v.setdefault("info_class", {})[kind] = {}
            for kc, cls in enumerate(CLASSES):
                rc = np.tile(np.repeat(np.array([SL.ring_k(a, b) == kc for a, b in SL.PAIRS]), len(fh)), 2)
                v["info_class"][kind][cls] = float(np.mean((np.sum(J[rc] ** 2, 0) / np.sum(J ** 2, 0))[6:12]))
            share = {}
            for k, Sst in [(d, S[d]) for d in STAGES] + [(k, H6 + y) for k, y in yard_in.items()]:
                dd = Mall[kind].data(dS=SL.recip(Sst - H6)[:, fi], S_stage=Sst[fi], S_ref=H6[fi])
                share[k] = float(np.sum(dd[rows] ** 2) / np.sum(dd ** 2))
            v["data_opp"][kind] = share
        res["variants"][vname] = v
    res["truth"] = {d: truth[d]["sens"][7:13].tolist() for d in STAGES}
    res["rules"] = fz["rules"]
    return res


def score(x, d, rule, truth):
    c = RL.apply_rules(x, rule)
    e = np.array(SL.DESIGNS[d][0], float)
    aff = e > 0
    corr_t = float(np.corrcoef(x[6:12], truth)[0, 1])
    _, topk = SL.pattern_scores(x[6:12], e, aff)
    return dict(c, corr_truth=corr_t, topk=topk,
                called=" ".join(f"S{k + 1}" for k in range(6) if c["affected"][k]) or "none",
                correct=int(np.sum(np.array(c["affected"]) == aff)))


def section(res):
    pdb = res["path_db"]
    L = ["## 5c. Mesh-matched set lobe_A (4 Oct): frozen pipeline, one-extra-pass yardstick, opposite paths", "",
         "**Data.** lobe_A = `Healthy_sliced_new` (6 adaptive passes, same stop rule as the stages; the stages "
         "converged in 5 passes, results/STATUS.md §7) as the reference, with `Mild_lobe`, `Moderate_lobe`, `Severe_lobe` (the `_new` Moderate and Severe files are "
         "identical to the old ones: max |ΔS| " + ", ".join(f"{v:.0e}" for k, v in res["identical_new"].items()
                                                            if not k.startswith("Mild"))
         + "). Frozen κ, λ and thresholds from `lobe_frozen.json` (code "
         f"`{res['frozen_code']}`) are applied unchanged; only the reference (its noise weights and the "
         "log-ratio reference) is now Healthy_sliced_new. The pre-registered predictions are unchanged.", "",
         "**Mesh yardstick = one extra adaptive pass.** Pass-to-pass differences, each passed through the "
         "pipeline as if it were a stage: Healthy 7 − 6 passes (`Healthy_sliced` − `Healthy_sliced_new`), "
         "Mild 6 − 5 passes (`Mild_lobe_new` − `Mild_lobe`) and, from the c3 delivery (4 Oct), Moderate 6 − 5 "
         "(`Moderate_lobe_c3` − `Moderate_lobe`) and Severe 6 − 5 (`Severe_lobe_c3` − `Severe_lobe`). The sign of a mesh error is not known, so each "
         "difference is passed with both signs (+ and −); for the linear Tikhonov fits the two give the same |dε''|, "
         "for the bounded fits only one sign survives the bound dε'' ≥ 0.", "",
         "Amplitude change per path class (dB, largest path of the class, 3.2–4.2 GHz, 201 points, glitch-masked): "
         "band = band-mean power ratio; median = median over frequency; worst = worst single frequency (set by "
         "spectral notches, where |S| is small):", "",
         _t([dict(difference=k, statistic=st, **{c: v[c][st] for c in CLASSES})
             for k, v in pdb.items() for st in ("band", "median", "worst")],
            ["difference", "statistic"] + list(CLASSES), {c: ".3f" for c in CLASSES}), "",
         "Which class moves most depends on the statistic: "
         + "; ".join(f"{st}: {max(CLASSES, key=lambda c: max(v[c][st] for v in pdb.values()))}"
                     for st in ("band", "median", "worst"))
         + ". The opposite paths dominate only at single frequencies (notches). The 0.16–0.30 dB (opposite) / "
         "≤ 0.05 dB (others) quoted for this check is the ring-mean change computed without glitch masking; "
         "`docs/01_claims_register.md` §L traces its 0.30 dB end (Mild 5→6) to one non-reciprocal sample on "
         "T2–T5 at 3.855 GHz in `Mild_lobe_new` (−34 dB against ≈ −70 dB at the neighbouring samples). Here "
         "that sample is glitch-masked (−30 dB rule; it becomes −58 dB) and 3.855 GHz is not one of the fit "
         "frequencies, so it does not enter any inversion below. The inversion uses complex S at "
         + ", ".join(f"{x:g}" for x in res["f_GHz"]) + " GHz, so the table above is what it sees. "
         "This yardstick replaces §5b (v2 Normal − Healthy_sliced), which compared different projects as well "
         "as meshes.", ""]
    out_rows = {}
    for vname, v in res["variants"].items():
        L += [f"### lobe_A, {vname}", ""]
        rows, yrows, crow = [], [], []
        for m in RL.METHODS:
            rule = res["rules"][m]
            yk = np.array([np.abs(np.asarray(y)[6:12]) for y in v["yard"][m].values()])      # (2, 6)
            ymax, ysum = yk.max(0), yk.sum(0)
            ylr = max(abs(RL.contrasts(y)["LR"]) for y in v["yard"][m].values())
            yfb = max(abs(RL.contrasts(y)["FB"]) for y in v["yard"][m].values())
            for k, y in v["yard"][m].items():
                c = RL.apply_rules(np.asarray(y), rule)
                yrows.append(dict(method=m, difference=k, **{s: float(np.asarray(y)[6 + j]) for j, s in enumerate(SHORT)},
                                  called=" ".join(f"S{j + 1}" for j in range(6) if c["affected"][j]) or "none",
                                  LR=c["LR"], FB=c["FB"]))
            for d in STAGES:
                x = np.asarray(v["fits"][m][d])
                sc = score(x, d, rule, res["truth"][d])
                ex = x[6:12] > ymax
                rows.append(dict(method=m, stage=d,
                                 **{s: f"{x[6 + j]:.1f}{'*' if ex[j] else ''}" for j, s in enumerate(SHORT)},
                                 called=sc["called"], correct=sc["correct"], corr_truth=sc["corr_truth"],
                                 LR=sc["LR"], side=sc["side"], FB=sc["FB"], frontback=sc["frontback"]))
                crow.append(dict(method=m, stage=d, LR=sc["LR"], yard_LR=ylr, LR_exceeds=abs(sc["LR"]) > ylr,
                                 FB=sc["FB"], yard_FB=yfb, FB_exceeds=abs(sc["FB"]) > yfb,
                                 n_sectors_over_yard=int(ex.sum()),
                                 n_sectors_over_sum=int(np.sum(x[6:12] > ysum)),
                                 n_healthy_over_yard=int(np.sum(ex & (np.array(SL.DESIGNS[d][0]) == 0))),
                                 corr_truth=sc["corr_truth"], called=sc["called"], correct=sc["correct"],
                                 frontback=sc["frontback"], side=sc["side"]))
        out_rows[vname] = dict(rows=rows, yrows=yrows, crow=crow)
        L += ["Recovered dε'' per sector (* = exceeds the one-extra-pass yardstick of that sector and method, "
              "i.e. the larger of the two pass differences' |dε''| in that sector), calls by the frozen rules:", "",
              _t(rows, ["method", "stage"] + SHORT + ["called", "correct", "corr_truth", "LR", "side", "FB", "frontback"],
                 {"corr_truth": ".2f", "LR": "+.1f", "FB": "+.1f"}), "",
              "The yardstick itself (each pass difference, both signs, through the same pipeline):", "",
              _t(yrows, ["method", "difference"] + SHORT + ["called", "LR", "FB"],
                 {**{s: ".1f" for s in SHORT}, "LR": "+.1f", "FB": "+.1f"}), "",
              "Against the yardstick (sectors over the larger / over the sum of the two pass differences; "
              "contrasts vs the larger pass-difference |LR|, |FB|):", "",
              _t(crow, ["method", "stage", "n_sectors_over_yard", "n_sectors_over_sum", "n_healthy_over_yard",
                        "LR", "yard_LR", "LR_exceeds", "FB", "yard_FB", "FB_exceeds"],
                 {"LR": "+.1f", "yard_LR": ".1f", "FB": "+.1f", "yard_FB": ".1f"}), ""]
    shift = []
    for m in RL.METHODS:
        for d in STAGES:
            dx = np.asarray(res["variants"]["all 21 paths"]["fits"][m][d])[6:12] - np.asarray(res["old_fits"][m][d])[6:12]
            shift.append(dict(method=m, stage=d, **{s: dx[j] for j, s in enumerate(SHORT)}))
    L += ["Change of the recovered dε'' when the 7-pass reference (§3) is replaced by the 6-pass reference "
          "(lobe_A − §3, all paths). For the linear fits it equals minus the Healthy 7 − 6 yardstick row above:", "",
          _t(shift, ["method", "stage"] + SHORT, {s: "+.1f" for s in SHORT}), ""]
    va = res["variants"]["all 21 paths"]
    L += ["### Does the reconstruction depend on the opposite paths?", "",
          "Share of the information (whitened Fisher diagonal) on each sector's dε'' that comes from the 3 "
          "opposite paths, and share of the whitened data energy in those paths (all-path model):", "",
          _t([dict(model=k, **{s: va["info_opp"][k][j] for j, s in enumerate(SHORT)}) for k in ("dS", "log")],
             ["model"] + SHORT, {s: ".1%" for s in SHORT}), "",
          _t([dict(model=k, **va["data_opp"][k]) for k in ("dS", "log")],
             ["model"] + list(va["data_opp"]["dS"]), {k: ".1%" for k in va["data_opp"]["dS"]}), "",
          "Information share per path class (mean over the six sectors' dε''):", "",
          _t([dict(model=k, **va["info_class"][k]) for k in ("dS", "log")], ["model"] + list(CLASSES),
             {c: ".1%" for c in CLASSES}), "",
          "(For the gain-invariant model the rows are taken after the gain projection, which mixes paths, so its "
          "shares are approximate; the 'without opposite paths' fits rebuild the projection on the 18 kept paths.)", ""]
    res["tables"] = out_rows
    return L


def summarise(res):
    """Numbers used by the reading below and by the verdict in report_lobe."""
    t = res["tables"]
    out = {}
    for vname in t:
        cr = t[vname]["crow"]
        out[vname] = dict(
            correct={m: [r["correct"] for r in cr if r["method"] == m] for m in RL.METHODS},
            called={m: [r["called"] for r in cr if r["method"] == m] for m in RL.METHODS},
            corr={m: [r["corr_truth"] for r in cr if r["method"] == m] for m in RL.METHODS},
            FB_mod={m: next(r["FB"] for r in cr if r["method"] == m and r["stage"] == "Moderate_lobe")
                    for m in RL.METHODS},
            fb_calls={m: [r["frontback"] for r in cr if r["method"] == m] for m in RL.METHODS},
            yard_FB=max(r["yard_FB"] for r in cr), yard_LR=max(r["yard_LR"] for r in cr),
            max_sym_LR=max(abs(r["LR"]) for r in cr),
            healthy_over=sum(r["n_healthy_over_yard"] for r in cr if r["method"] == RL.METHODS[0]))
    a, b = (np.array([np.asarray(res["variants"][v]["fits"][m][d])[6:12] for m in RL.METHODS for d in STAGES])
            for v in t)
    out["noopp_minus_all"] = (float((b - a).min()), float((b - a).max()))
    io = res["variants"]["all 21 paths"]["info_opp"]
    out["info_opp"] = (float(min(min(x) for x in io.values())), float(max(max(x) for x in io.values())))
    ds = [x for k in ("dS", "log") for d, x in res["variants"]["all 21 paths"]["data_opp"][k].items() if d in STAGES]
    out["data_opp"] = (float(min(ds)), float(max(ds)))
    dy = [x for k in ("dS", "log") for d, x in res["variants"]["all 21 paths"]["data_opp"][k].items() if d not in STAGES]
    out["data_opp_yard"] = (float(min(dy)), float(max(dy)))
    out["yard_sector_max"] = float(max(np.abs(np.asarray(x)[6:12]).max()
                                       for m in RL.METHODS for x in res["variants"]["all 21 paths"]["yard"][m].values()))
    rule = res["rules"][RL.METHODS[0]]
    out["T_abs"], out["T_FB"], out["T_LR"] = rule["T_abs"], rule["T_FB"], rule["T_LR"]
    return out


def interpret(res):
    sm = summarise(res)
    res["summary"] = sm
    va, vn = sm["all 21 paths"], sm["without opposite paths"]
    P0, P2 = RL.METHODS[0], RL.METHODS[2]

    def calls(v, m):
        return "; ".join(f"{d.split('_')[0]} {c} ({k}/6 correct)"
                         for d, c, k in zip(STAGES, v["called"][m], v["correct"][m]))
    L = ["### Reading", "",
         f"- **Absolute sector levels.** A one-pass mesh change shifts every sector by up to "
         f"{sm['yard_sector_max']:.1f} (dε''), almost uniformly (same sign in all six sectors; table 'yardstick "
         "itself'). Every recovered sector value, healthy ones included, exceeds its own sector's yardstick "
         f"({va['healthy_over']} healthy-sector estimates over the yardstick, primary method, all paths). So the "
         "upward offset of the healthy sectors (about 5–10 instead of 0.3) is not explained by a one-pass mesh "
         "change; Born model error and leakage from neighbouring affected sectors are the likely cause. Per-sector exceedance is therefore not a "
         "test of 'affected'; the contrasts below are.",
         f"- **The frozen absolute threshold is sensitive to the reference mesh.** Replacing the 7-pass reference "
         f"by the 6-pass one lowers every sector by about 2–3 (table above), comparable to the margin of some calls "
         f"around T_abs = {sm['T_abs']:.1f}. Primary method, all paths: {calls(va, P0)}. Without the opposite "
         f"paths: {calls(vn, P0)}. Gain-invariant, all paths: {calls(va, P2)}. Without: {calls(vn, P2)}.",
         f"- **Front/back.** Moderate's FB = S1 − S4 is {va['FB_mod'][P0]:+.1f} (all paths) and "
         f"{vn['FB_mod'][P0]:+.1f} (without opposite paths) for the primary method, {va['FB_mod'][P2]:+.1f} / "
         f"{vn['FB_mod'][P2]:+.1f} gain-invariant; the one-pass yardstick gives |FB| ≤ "
         f"{max(va['yard_FB'], vn['yard_FB']):.1f}. Front is called for Moderate by every method in both path "
         "sets. Mild and Severe (S1 and S4 equal in truth) give FB of about +3 to +4, also well above the "
         "yardstick: a systematic front-positive bias of about 4 that is not mesh. The frozen T_FB (Mild's |FB|) "
         "absorbs it, except in the bounded-dS fit, whose T_FB = 3.8 lets Mild and Severe through in the all-path "
         "version.",
         f"- **Left/right.** The one-pass yardstick gives |LR| ≤ {max(va['yard_LR'], vn['yard_LR']):.1f}. The "
         f"mirror-symmetric designs give |LR| up to {max(va['max_sym_LR'], vn['max_sym_LR']):.1f} (Moderate): more "
         f"than the mesh yardstick, but below the frozen T_LR = {sm['T_LR']:.1f}. The pre-registered LeftOnly "
         "contrast (+14.7 ± 2.2, Born-simulated) is about 20× the one-pass yardstick.",
         f"- **Opposite paths.** They carry {sm['info_opp'][0]:.0%}–{sm['info_opp'][1]:.0%} of the information on "
         f"each sector and {sm['data_opp'][0]:.0%}–{sm['data_opp'][1]:.0%} of the stage data energy; in the whitened "
         f"complex data they carry {sm['data_opp_yard'][0]:.0%}–{sm['data_opp_yard'][1]:.0%} of the pass-difference "
         "energy, i.e. not more than their "
         "information share, so the pass difference is not concentrated on them as seen by the inversion. Removing "
         f"them moves the sector estimates by {sm['noopp_minus_all'][0]:+.1f} to {sm['noopp_minus_all'][1]:+.1f}, "
         "raises the yardstick slightly, and changes calls only where a sector sits near T_abs. Pattern, "
         "front/back and left/right conclusions are the same with and without them. Both versions are tabulated "
         "above and neither is preferred.", ""]
    return L


def main():
    res = compute()
    L = section(res)
    L += interpret(res)
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    if "## 5c." in rep:
        rep = rep[:rep.index("## 5c.")] + rep[rep.index("## 6."):]
    i = rep.index("## 6.")
    rep = rep[:i] + "\n".join(L) + "\n" + rep[i:]
    old_h = "## 5b. Mesh yardstick (added after the freeze; frozen pipeline unchanged)"
    note = ("*Superseded by §5c (4 Oct): this compared two different projects as well as meshes; the "
            "mesh-matched set and the one-extra-pass yardstick are in §5c.*")
    if old_h in rep and note not in rep:
        rep = rep.replace(old_h, old_h + "\n\n" + note)
    (OUT / "lobe_A.json").write_text(json.dumps({"summary": res["summary"]}, default=float), encoding="utf-8")
    if "## 6. Blind test outcome" not in rep:                      # before the blind stage: refresh the verdict
        from imaging.report_lobe import _verdict
        res1 = pickle.loads((RL.CACHE / "stage1.pkl").read_bytes())
        rep = rep[:rep.index("## 7. Verdict")] + "\n".join(_verdict(res1)) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
    js = {k: v for k, v in res.items() if k not in ("variants", "tables")}
    js["variants"] = {vn: {"fits": {m: {d: np.asarray(x).tolist() for d, x in v["fits"][m].items()} for m in v["fits"]},
                           "yard": {m: {k: np.asarray(x).tolist() for k, x in v["yard"][m].items()} for m in v["yard"]},
                           "info_opp": v["info_opp"], "data_opp": v["data_opp"], "info_class": v["info_class"]}
                      for vn, v in res["variants"].items()}
    (OUT / "lobe_A.json").write_text(json.dumps(js, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)),
                                     encoding="utf-8")
    (RL.CACHE / "lobe_A.pkl").write_bytes(pickle.dumps(res))
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
