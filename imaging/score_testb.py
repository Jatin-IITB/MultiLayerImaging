"""Blind design Test_B: estimates under the committed protocol (results/imaging/testb_protocol.md).

    python imaging/score_testb.py [--n 200]                 # the blind run (only after the protocol commit)
    python imaging/score_testb.py --dry-run STEM [--n 20]    # pipeline check on a KNOWN design; prints only

Implements the protocol exactly: frozen pipeline (lobe_frozen.json, fb5b775), both references (Healthy_sliced
7 passes = H7, Healthy_sliced_new 6 passes = H6), frozen calls, R1c rulers, data-level gate, fit-rejection rule,
reading rule; whitened log labelled POST-HOC (no calls). Test_B is read only through study_lobe.load_design
(S-parameters, -30 dB glitch mask, antenna order). Writes results/imaging/testb.json, testb_report.md and
section 11 of lobe_report.md.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402

from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_round2 as R2  # noqa: E402
from imaging import lobe_rulers as LR  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, ROOT, git_hash, load_config  # noqa: E402
from imaging.report_lobe import SHORT, _t  # noqa: E402

H7, H6 = "Healthy_sliced", "Healthy_sliced_new"
REFS = {"H7 (Healthy_sliced, 7 passes)": H7, "H6 (Healthy_sliced_new, 6 passes, stop rule 1)": H6}
METHODS = tuple(RL.METHODS) + (LR.WNAME,)
PRIMARY = RL.METHODS[0]
NULL9 = C3.SYMMETRIC
FB_ZERO = ("Healthy_sliced", "Healthy_sliced_new", "MCI_lobe_c3", "Mild_lobe", "Mild_lobe_new", "Severe_lobe",
           "Severe_lobe_c3")                        # true S1 and S4 changes equal
SECT_ZERO = ("Healthy_sliced", "Healthy_sliced_new", "MCI_lobe_c3")   # no cortical change
CORTICAL = ("Mild_lobe", "Moderate_lobe", "Severe_lobe", "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3",
            "LeftOnly_test_c3", "RightOnly_test")
REJECT_FACTOR = 1.5
FIT = np.array([3.4e9, 3.6e9, 3.8e9])


def bar(r):
    return "established" if r >= 3 else ("sensitive" if r >= 2 else "not separable")


def qc(stem, f_ref):
    """QC from the S-parameters only."""
    from adstage.io.masking import mask_glitches
    from adstage.io.touchstone import read_touchstone
    cfg = load_config()
    t = read_touchstone(ROOT / "data" / "raw" / f"new_with_slices_{stem}.s6p")
    s, f = t.s, t.f_hz
    lvl = np.sqrt((np.abs(s) ** 2).mean(0))
    rec = max(float(np.max(20 * np.log10(np.abs(s[:, i, j] - s[:, j, i]) / np.sqrt(lvl[i, j] * lvl[j, i]))))
              for i in range(6) for j in range(i + 1, 6))
    amp = max(float(np.max(np.abs(20 * np.log10(np.abs(s[:, i, j]) / np.abs(s[:, j, i])))))
              for i in range(6) for j in range(i + 1, 6))
    sv = max(float(np.linalg.svd(s[q], compute_uv=False).max()) for q in range(len(f)))
    _, log = mask_glitches(f, s, float(cfg["qc"].get("glitch_thr_db", -30.0)))
    masked = [dict(f_GHz=r["f_GHz"], ports=f"{r['port_i']}-{r['port_j']}", recip_err_dB=r["recip_err_db"],
                   at_fit_freq=bool(np.min(np.abs(FIT - r["f_GHz"] * 1e9)) < 1)) for r in log]
    return dict(points=len(f), f_min_GHz=float(f[0] / 1e9), f_max_GHz=float(f[-1] / 1e9),
                same_grid=bool(len(f) == len(f_ref) and np.max(np.abs(f - f_ref)) < 1),
                max_singular_value=sv, passive=sv <= 1 + 1e-9, max_recip_err_dB_re_band=rec,
                max_amp_nonrecip_dB=amp, n_masked=len(masked), masked=masked,
                masked_at_fit_freq=any(m["at_fit_freq"] for m in masked))


def residual(M, m, lam, X, R, fi):
    key = "wlog" if m == LR.WNAME else ("dS" if m.endswith("dS") else "log")
    mdl = M[key]
    d = mdl.data(dS=SL.recip(X - R)[:, fi], S_stage=X[fi], S_ref=R[fi])
    x = C3.make_x(M, m, lam)(X[fi], R[fi])
    return float(np.linalg.norm(d - mdl.J @ x) / np.linalg.norm(d)), float(np.linalg.norm(d))


def run(ctx, stem, S_B, n_meas):
    fi, S = ctx.fi, ctx.S
    out = {"rows": [], "rulers": [], "anti": [], "gate": [], "known_q": []}
    for rlab, ref in REFS.items():
        R = S[ref]
        M = ctx.model(ref)
        # data-level gate (whitened dS norm vs the largest one-pass difference added to the reference)
        dnorm = residual(M, PRIMARY, ctx.lam, S_B, R, fi)[1]
        op = max(residual(M, PRIMARY, ctx.lam, R + sg * (S[a] - S[b]), R, fi)[1]
                 for a, b in C3.ONE_PASS.values() for sg in (1, -1))
        known_norm = {d: residual(M, PRIMARY, ctx.lam, S[d], R, fi)[1] for d in CORTICAL + ("MCI_lobe_c3",) if d in S}
        out["gate"].append(dict(reference=rlab, data_norm=dnorm, one_pass_max_norm=op, ratio=dnorm / op,
                                label=bar(dnorm / op), **{f"norm {k}": v for k, v in known_norm.items()}))
        for m in METHODS:
            fx = C3.make_x(M, m, ctx.lam)

            def q(X):
                return C3.qvec(fx(X[fi], R[fi]))
            x = fx(S_B[fi], R[fi])
            qb = C3.qvec(x)
            rho, _ = residual(M, m, ctx.lam, S_B, R, fi)
            rho_known = {d: residual(M, m, ctx.lam, S[d], R, fi)[0] for d in CORTICAL if d in S}
            rmax = max(rho_known.values())
            yard = np.max([np.abs(q(R + sg * (S[a] - S[b]))) for a, b in C3.ONE_PASS.values() for sg in (1, -1)], 0)
            lr_floor = max(abs(q(S[d])[6]) for d in NULL9 if d != ref)
            fb_floor = max(abs(q(S[d])[7]) for d in FB_ZERO if d != ref)
            sec_floor = np.max([np.abs(q(S[d])[:6]) for d in SECT_ZERO if d != ref], 0)
            rul = np.r_[np.maximum(yard[:6], sec_floor), max(yard[6], lr_floor), max(yard[7], fb_floor)]
            row = dict(reference=rlab, method=LR.SHORTM[m] + (" (POST-HOC)" if m == LR.WNAME else ""),
                       **{f"eps_r {SHORT[k]}": float(x[k]) for k in range(6)},
                       **{SHORT[k]: float(qb[k]) for k in range(6)}, LR=float(qb[6]), FB=float(qb[7]),
                       LR_ratio=float(abs(qb[6]) / rul[6]), FB_ratio=float(abs(qb[7]) / rul[7]),
                       residual=rho, residual_known_max=rmax, rejected=bool(rho > REJECT_FACTOR * rmax))
            if m in RL.METHODS:
                c = RL.apply_rules(x, ctx.fz["rules"][m])
                row.update(called=" ".join(f"S{k + 1}" for k in range(6) if c["affected"][k]) or "none",
                           side=c["side"], frontback=c["frontback"], T_abs=ctx.fz["rules"][m]["T_abs"])
            else:
                row.update(called="n/a (no frozen thresholds)", side="n/a", frontback="n/a", T_abs=np.nan)
            out["rows"].append(row)
            out["rulers"].append(dict(reference=rlab, method=LR.SHORTM[m], **{f"ruler {SHORT[k]}": float(rul[k]) for k in range(6)},
                                      ruler_LR=float(rul[6]), ruler_FB=float(rul[7]), yard_LR=float(yard[6]),
                                      floor_LR=float(lr_floor), yard_FB=float(yard[7]), floor_FB=float(fb_floor)))
            if m == PRIMARY:
                for d in CORTICAL + ("MCI_lobe_c3",):
                    if d in S:
                        out["known_q"].append(dict(reference=rlab, design=d, **{SHORT[k]: float(v) for k, v in enumerate(q(S[d])[:6])},
                                                   LR=float(q(S[d])[6]), FB=float(q(S[d])[7])))
            # reference-free LR_anti with the R1c ruler
            T = R2.anti_lr(ctx, m, ref)
            tb = T(S_B)
            nulls = [T(S[d]) for d in NULL9]
            ay = max(abs(T(S[a]) - T(S[b])) for a, b in C3.ONE_PASS.values())
            ar = max(ay, max(abs(v) for v in nulls))
            out["anti"].append(dict(reference=rlab, method=LR.SHORTM[m] + (" (POST-HOC)" if m == LR.WNAME else ""),
                                    LR_anti=float(tb), yardstick=float(ay), null_max=float(max(abs(v) for v in nulls)),
                                    ruler=float(ar), ratio=float(abs(tb) / ar), label=bar(abs(tb) / ar),
                                    rank_p=float((1 + sum(abs(v) >= abs(tb) for v in nulls)) / (len(nulls) + 1))))
    # measurement-level context (Prompt 07 model, +-0.5 dB), primary method
    meas = []
    g = list(LR.GAIN)[0]
    D = ctx._draws(ctx.f, S_B, ctx.prof, n_meas, np.random.default_rng([2026, 1006, 11]), {**ctx.acfg, **LR.GAIN[g]})[:, fi]
    for rlab, ref in REFS.items():
        Dr = ctx._draws(ctx.f, S[ref], ctx.prof, n_meas, np.random.default_rng([2026, 1006, 12, len(ref)]),
                        {**ctx.acfg, **LR.GAIN[g]})[:, fi]
        fx = C3.make_x(ctx.model(ref), PRIMARY, ctx.lam)
        qs = np.array([C3.qvec(fx(a, b)) for a, b in zip(D, Dr)])
        meas.append(dict(reference=rlab, **{f"sd {k}": float(v) for k, v in zip(SHORT + ["LR", "FB"], qs.std(0, ddof=1))}))
    out["measured_sd_05dB"] = meas
    return out


def reading(out, rules):
    prim = [r for r in out["rows"] if r["method"] == LR.SHORTM[PRIMARY]]
    size = ", ".join(f"{g['reference'].split(' ')[0]} {g['ratio']:.2f}× ({bar(g['ratio'])})" for g in out["gate"])
    ok = [r for r in prim if not r["rejected"]]
    if not ok:
        return dict(statement="Fit rejected in both references (residual > 1.5× the largest residual of the known "
                              "cortical designs): the sector model does not explain Test_B, so no lobe reading is "
                              f"stated. Data-level size vs the largest one-pass mesh difference: {size}.",
                    affected=[], possible=[], side="none", frontback="none", ranking=[], used_references=[],
                    data_size=size)
    T = rules[PRIMARY]["T_abs"]
    above = [[r[s] > T for s in SHORT] for r in ok]
    n_above = np.sum(above, 0)
    affected = [s for k, s in enumerate(SHORT) if n_above[k] == len(ok)]
    possible = [s for k, s in enumerate(SHORT) if 0 < n_above[k] < len(ok)]
    if not affected and not possible:
        mean = np.mean([[r[s] for s in SHORT] for r in ok], 0)
        return dict(statement=f"No sector above the frozen T_abs ({T:.2f}) in any accepted reference: no lobe is read "
                              f"as affected. Data-level size vs the largest one-pass mesh difference: {size}.",
                    affected=[], possible=[], side="none", frontback="none",
                    ranking=[SHORT[k] for k in np.argsort(-mean)], mean_sector=[float(v) for v in mean],
                    used_references=[r["reference"] for r in ok], data_size=size)
    anti = [a for a in out["anti"] if a["method"] == LR.SHORTM[PRIMARY]]
    ar = min(a["ratio"] for a in anti)
    sgn = {np.sign(a["LR_anti"]) for a in anti}
    side = "none"
    if len(sgn) == 1 and ar >= 2:
        side = ("left" if sgn.pop() > 0 else "right") + (" (established)" if ar >= 3 else " (tentative)")
    fbr = [(r["FB"], r["FB_ratio"]) for r in ok]
    fsg = {np.sign(v) for v, _ in fbr}
    fmin = min(rr for _, rr in fbr)
    frontback = "none"
    if len(fsg) == 1 and fmin >= 2:
        frontback = ("front" if fsg.pop() > 0 else "back") + (" (established)" if fmin >= 3 else " (tentative)")
    mean = np.mean([[r[s] for s in SHORT] for r in ok], 0)
    ranking = [SHORT[k] for k in np.argsort(-mean)]
    return dict(statement=None, affected=affected, possible=possible, side=side, frontback=frontback,
                ranking=ranking, mean_sector=[float(v) for v in mean], used_references=[r["reference"] for r in ok],
                LR_anti_min_ratio=float(ar), FB_min_ratio=float(fmin), data_size=size)


def write(stem, qcres, out, rd, protocol_commit, n):
    rows = out["rows"]
    num = {c: "+.2f" for c in SHORT + ["LR", "FB"] + [f"eps_r {s}" for s in SHORT]}
    num.update(LR_ratio=".2f", FB_ratio=".2f", residual=".3f", residual_known_max=".3f", T_abs=".2f")
    L = [f"# Test_B (blind): estimates under the committed protocol", "",
         f"Protocol `results/imaging/testb_protocol.md`, committed in `{protocol_commit}` before Test_B was loaded. "
         f"Run: `python imaging/score_testb.py --n {n}` at code `{git_hash(ROOT)}`. Frozen pipeline `lobe_frozen.json` "
         f"(fb5b775). Estimates only; the truth is held by the user.", "",
         "## QC (S-parameters only)", "",
         _t([{k: v for k, v in qcres.items() if k != "masked"}], [k for k in qcres if k != "masked"],
            {"max_singular_value": ".4f", "max_recip_err_dB_re_band": ".1f", "max_amp_nonrecip_dB": ".2f",
             "f_min_GHz": ".2f", "f_max_GHz": ".2f"}), ""]
    if qcres["masked"]:
        L += ["Masked points:", "", _t(qcres["masked"], list(qcres["masked"][0]), {"f_GHz": ".3f", "recip_err_dB": ".1f"}), ""]
    L += ["## Data-level size (context, not a gate)", "",
          "Whitened dS norm of Test_B − reference against the largest one-pass mesh difference (bar ≥ 3× established, "
          "2–3× sensitive, < 2× not separable). Known designs' norms are shown alongside; LeftOnly is only 1.25–1.59×:", "",
          _t(out["gate"], list(out["gate"][0]), {k: ".2f" for k in out["gate"][0] if k not in ("reference", "label")}), "",
          "## Sector map, LR, FB, frozen calls, fit residual", "",
          f"dε'' per sector (and dεr). Calls: frozen R1–R3. Residual = whitened relative misfit; rejected if > "
          f"{REJECT_FACTOR}× the largest residual of the known cortical designs ({', '.join(d for d in CORTICAL)}).", "",
          _t(rows, ["reference", "method"] + SHORT + ["LR", "LR_ratio", "FB", "FB_ratio", "called", "side", "frontback",
                                                      "residual", "residual_known_max", "rejected"], num), "",
          "dεr (context):", "",
          _t(rows, ["reference", "method"] + [f"eps_r {s}" for s in SHORT], num), "",
          "Rulers (R1c: max(one-pass yardstick, largest |value| over the null designs)); sector floor from "
          f"{', '.join(SECT_ZERO)}; LR floor from the nine symmetric solves; FB floor from {', '.join(FB_ZERO)}:", "",
          _t(out["rulers"], list(out["rulers"][0]), {k: ".2f" for k in out["rulers"][0] if k not in ("reference", "method")}), "",
          "Reference-free LR_anti (R1c ruler, rank p against the nine symmetric solves):", "",
          _t(out["anti"], list(out["anti"][0]), {"LR_anti": "+.2f", "yardstick": ".2f", "null_max": ".2f", "ruler": ".2f",
                                                 "ratio": ".2f", "rank_p": ".2f"}), "",
          "Measurement-level context (Prompt 07 model, ±0.5 dB, primary method, SD over draws; not part of the reading):", "",
          _t(out["measured_sd_05dB"], list(out["measured_sd_05dB"][0]),
             {k: ".2f" for k in out["measured_sd_05dB"][0] if k != "reference"}), "",
          "Known designs through the same primary pipeline (context for the reader; not used by the reading rule):", "",
          _t(out["known_q"], list(out["known_q"][0]), {k: "+.2f" for k in out["known_q"][0] if k not in ("reference", "design")}), "",
          "## Stated reading (protocol reading rule, primary method)", ""]
    if rd["statement"]:
        L += [f"**{rd['statement']}**", ""]
    else:
        L += [f"- **Affected lobes** (above the frozen T_abs in every reference that passed the gate and was not rejected: "
              f"{', '.join(rd['used_references'])}): **{', '.join(rd['affected']) or 'none'}**.",
              f"- **Possible** (above T_abs in one reference only): {', '.join(rd['possible']) or 'none'}.",
              f"- **Side:** {rd['side']} (smallest LR_anti ratio over the references {rd['LR_anti_min_ratio']:.2f}×).",
              f"- **Front/back:** {rd['frontback']} (smallest FB ratio {rd['FB_min_ratio']:.2f}×).",
              f"- **Ranking** of the six sectors by mean dε'': {' > '.join(rd['ranking'])} "
              f"({', '.join(f'{s} {v:+.1f}' for s, v in zip(SHORT, rd['mean_sector']))}).",
              "- Caveats from round 2 apply: sector values carry Born and reference error of several units; calls near "
              "T_abs are fragile; the reading is a sector-level estimate of where the change sits under the cap of the "
              "array (sensitivity ≥ 54 % above z = 40 mm), not an anatomical lobe diagnosis.", ""]
    L += ["The whitened-log rows are **POST-HOC** (no frozen thresholds, not used by the reading)."]
    txt = "\n".join(L) + "\n"
    (OUT / "testb_report.md").write_text(txt, encoding="utf-8")
    (OUT / "testb.json").write_text(json.dumps(dict(protocol_commit=protocol_commit, code=git_hash(ROOT), qc=qcres, **out,
                                                    reading=rd), indent=1, default=lambda o: o.item() if hasattr(o, "item")
                                               else (o.tolist() if hasattr(o, "tolist") else str(o))), encoding="utf-8")
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    sec = ["## 11. Blind design Test_B (estimates; truth held by the user)", "",
           f"Protocol committed in `{protocol_commit}` before loading. Full output: `results/imaging/testb_report.md`.", ""]
    sec += ([f"**{rd['statement']}**"] if rd["statement"] else
            [f"Reading (primary method): affected **{', '.join(rd['affected']) or 'none'}**; possible "
             f"{', '.join(rd['possible']) or 'none'}; side {rd['side']}; front/back {rd['frontback']}; ranking "
             f"{' > '.join(rd['ranking'])}."]) + [""]
    if "## 11." in rep:
        i0 = rep.index("## 11.")
        j = rep.find("\n## ", i0 + 5)
        rep = rep[:i0] + "\n".join(sec) + ("\n" + rep[j + 1:] if j >= 0 else "\n")
    else:
        rep = rep.rstrip("\n") + "\n\n" + "\n".join(sec) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--dry-run", default=None, help="known design stem used as a stand-in; prints only")
    a = ap.parse_args()
    ctx = C3.Ctx(max(a.n, 20))
    if (ROOT / "data" / "raw" / "new_with_slices_RightOnly_test.s6p").exists():
        ctx.S["RightOnly_test"], _ = SL.load_design("RightOnly_test", ctx.f)
    stem = a.dry_run or "Test_B"
    if a.dry_run:
        S_B = ctx.S[stem] if stem in ctx.S else SL.load_design(stem, ctx.f)[0]
    else:
        S_B, _ = SL.load_design(stem, ctx.f)
    qcres = qc(stem, ctx.f)
    out = run(ctx, stem, S_B, a.n)
    rd = reading(out, ctx.fz["rules"])
    if a.dry_run:
        print("DRY RUN on", stem, "(known design; nothing written)")
        print(json.dumps(rd, indent=1, default=str))
        for r in out["rows"]:
            if r["method"] == LR.SHORTM[PRIMARY]:
                print(r["reference"], {s: round(r[s], 1) for s in SHORT}, "LR", round(r["LR"], 2), "FB", round(r["FB"], 2),
                      "called", r["called"], "resid", round(r["residual"], 3), "/", round(r["residual_known_max"], 3))
        print([(g["reference"][:2], round(g["ratio"], 2), g["label"]) for g in out["gate"]])
        return
    proto = __import__("subprocess").run(["git", "log", "-1", "--format=%h", "--", "results/imaging/testb_protocol.md"],
                                         capture_output=True, text=True, cwd=ROOT).stdout.strip()
    if not proto:
        print("REFUSED: results/imaging/testb_protocol.md is not committed.")
        sys.exit(1)
    write(stem, qcres, out, rd, proto, a.n)
    print("written: testb_report.md, testb.json, lobe_report.md section 11")


if __name__ == "__main__":
    main()
