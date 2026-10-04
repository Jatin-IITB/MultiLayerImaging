"""Text of round 5 (results/imaging/lobe_round5.md) and section 14 of lobe_report.md. POST-HOC throughout; every
number is read from lobe_round5.json (and, for the regression check, the committed lobe_round4.json)."""
from __future__ import annotations

import json
import subprocess

import numpy as np

from imaging.common import OUT, ROOT
from imaging.report_lobe import SHORT, _t


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT).stdout.strip()


def _g(rows, **kw):
    for r in rows:
        if all(r.get(k) == v for k, v in kw.items()):
            return r
    raise KeyError(kw)


def _na(rows):
    return [{k: ("n/a" if v is None else v) for k, v in r.items()} for r in rows]


def _f(x, f=".2f"):
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else format(x, f)


def tier(x):
    if x is None or not np.isfinite(x):
        return "n/a"
    return "established" if x >= 3 else ("sensitive" if x >= 2 else "not determined")


def write_md(res):
    VN = [v[0] for v in res["variants"]]
    rot = res["rot"]
    new = [r for r in rot if r not in ("Null_rot07", "Null_rot19")]
    N = len(res["nulls"])
    c_code = _git("log", "--diff-filter=A", "--format=%h", "--", "imaging/lobe_round5.py").splitlines()
    c_reg = _git("log", "--reverse", "--format=%h", "-S", "Null_rot31", "--", "imaging/lobe_c3.py").splitlines()
    T = []
    L = ["# Round 5 (imaging session, POST-HOC): every rotated null, rulers three ways, pair p, reference typicality", "",
         f"Computed by `python imaging/lobe_round5.py --n {res['n_draws']}` at code `{res['code']}`; numbers in "
         "`results/imaging/lobe_round5.json`. Everything here is post hoc. Frozen files, protocols, predictions and "
         "committed verdicts are unchanged.", "",
         "## 0. What ran", "",
         f"- The procedure pre-registered in `HANDOVER.md` §2 (round 4): the round-3 and round-4 computations with every "
         f"registered rotated null. Null set: the 9 mirror-symmetric designs + {len(rot)} rotated "
         f"({', '.join(rot)}): **N = {N}**. Round 3 and round 4 keep their own files as the 11-null record. The "
         "'11 nulls (round 3)' column below repeats the same computations restricted to rot07/rot19, as a regression check.",
         f"- This code was committed **before** the new files were loaded (code commit `{c_code[0] if c_code else 'uncommitted'}`; "
         f"registry commit adding the new files `{c_reg[0] if c_reg else 'not yet'}`). The generalisations made then: the "
         "rank-p denominator of round 3 was hard-coded as 12 (11 nulls), and the bias-corrected FB floor named rot07/rot19; "
         "both now use every rotated null.",
         "- Rulers three ways, as in the pre-registration `5966ee4`: **all** (the ruler) = max(one-pass yardstick, largest "
         "|value| over the 9 symmetric designs + every rotated null); **without rot19**; **rot19 alone** = max(one-pass "
         "yardstick, |rot19|). Only 'all' is the ruler. Bar: ≥ 3× established, 2–3× sensitive, < 2× not determined.", ""]

    # ------------------------------------------------------------------ 1 files
    fl = res["files"]
    nf = [r for r in fl if r["stem"] in new]
    L += ["## 1. New files: registry and QC", "",
          _t(_na(fl), ["stem", "sha256_16", "matches_user", "passes", "final_dS", "elements", "sets", "points", "max_sv_squared",
                       "passive", "worst_amp_nonrecip_dB", "at_GHz", "ports", "path", "worst_point_masked", "n_masked"],
             {"final_dS": ".6f", "max_sv_squared": ".3f", "worst_amp_nonrecip_dB": ".2f", "at_GHz": ".3f"}), "",
          "Points masked by the −30 dB reciprocity rule in the rotated nulls:", "",
          _t(res["masks"], list(res["masks"][0]) if res["masks"] else ["file"],
             {"f_GHz": ".3f", "Sij_dB": ".1f", "Sji_dB": ".1f", "recip_err_dB": ".1f"}), ""]
    ok = all(r["matches_user"] is True for r in nf) and all(r["passive"] for r in nf)
    L += [f"**Result.** sha256 prefixes match the delivery: {', '.join(f'{r['stem']} {r['matches_user']}' for r in nf) or 'n/a'}. "
          f"Passive: {', '.join(f'{r['stem']} (max σ² {r['max_sv_squared']:.3f})' for r in nf)}. Worst amplitude "
          "non-reciprocity: " + "; ".join(f"{r['stem']} {r['worst_amp_nonrecip_dB']:.2f} dB at {r['at_GHz']:.3f} GHz, ports "
                                            f"{r['ports']} ({r['path']}), masked: {r['worst_point_masked']}" for r in nf)
          + ". Registered as kind = null, set lobe_nulls; in no training, frozen or stage set.", ""]
    T.append(("New files (QC)", "CONFIRMED" if ok else "CHANGED", "sha256 = delivery; passive; worst non-reciprocal point "
              + ", ".join(f"{r['stem']} masked {r['worst_point_masked']}" for r in nf), "lobe_round5.json: files, masks"))

    # ------------------------------------------------------------------ 2 nulls as targets
    nr = res["nulls_rows"]
    mx = max(max(r[s] for s in SHORT) for r in nr)
    mlr, mfb = max(r["LR_ratio"] for r in nr), max(r["FB_ratio"] for r in nr)
    calls = [r for r in nr if r["called"] not in ("none", "n/a (no frozen thresholds)") or r["side"] not in ("none", "n/a")
             or r["frontback"] not in ("none", "n/a")]
    L += ["## 2. Every rotated null as a target (frozen pipeline, both references)", "",
          _t([r for r in nr if r["null"] in new] or nr, ["null", "reference", "method"] + SHORT + ["LR", "LR_ratio", "FB", "FB_ratio",
                                                                                                  "called", "side", "frontback", "residual"],
             {**{s: "+.2f" for s in SHORT}, "LR": "+.2f", "FB": "+.2f", "LR_ratio": ".2f", "FB_ratio": ".2f", "residual": ".2f"}), "",
          "Reading rule of the Test_B protocol applied to each null:", "",
          _t([dict(null=r["null"], affected=", ".join(r["affected"]) or "none", possible=", ".join(r["possible"]) or "none",
                   side=r["side"], frontback=r["frontback"], statement=r["statement"] or "") for r in res["nulls_read"]],
             ["null", "affected", "possible", "side", "frontback", "statement"]), "",
          f"**Result (all {len(rot)} rotated nulls).** Largest sector value {mx:.2f} (frozen T_abs 13.81). LR and FB at most "
          f"{mlr:.2f}× and {mfb:.2f}× the protocol rulers. Frozen calls in any method and reference: {len(calls)}.", ""]
    T.append(("Rotated nulls as targets", "CONFIRMED" if not calls and mx < 13.81 else "CHANGED",
              f"no frozen call (max sector {mx:.2f} < 13.81); LR ≤ {mlr:.2f}×, FB ≤ {mfb:.2f}× the protocol rulers",
              "lobe_round5.json: nulls_rows, nulls_read"))

    # ------------------------------------------------------------------ 3 beyond all nulls, pair p
    an = res["anti"]
    a3 = res["anti3"]
    pp = res["pairs"]
    a0 = _g(an, reference="H7", method="Tikhonov dS")
    p0 = _g(pp, reference="H7", method="Tikhonov dS", nulls="all")
    p11 = _g(pp, reference="H7", method="Tikhonov dS", nulls=VN[0])
    beyond = all(r[f"both mirror designs beyond all {N}"] for r in an)
    lo = [r["LeftOnly (all)"] for r in a3]
    ro = [r["RightOnly (all)"] for r in a3]
    L += [f"## 3. 'LeftOnly and RightOnly beyond all nulls' with N = {N}", "",
          "LR_anti = ½[LR(X) − LR(mirror X)] for every null and both mirror designs:", "",
          _t(an, list(an[0]), {k: ".2f" for k in an[0] if isinstance(an[0][k], float)}), "",
          "Ratios to the LR_anti ruler, three ways (plus the round-3 11-null ruler):", "",
          _t(a3, list(a3[0]), {k: ".2f" for k in a3[0] if isinstance(a3[0][k], float)}), "",
          "Rank p of each mirror design and of the pair:", "",
          _t(pp, list(pp[0]), {"p_Left": ".4f", "p_Right": ".4f", "product": ".4f", "exact_exchangeable": ".4f"}), "",
          f"**Result.** Both mirror designs beyond all {N} nulls in every method × reference: **{beyond}**. Each rank p = "
          f"1/{N + 1} = {p0['p_Left']:.4f}. LR_anti ratio to the all-null ruler: LeftOnly {min(lo):.2f}–{max(lo):.2f}×, "
          f"RightOnly {min(ro):.2f}–{max(ro):.2f}× over methods and references.",
          f"**Pair p, corrected.** Rounds 2–3 multiplied the two rank p's ('if independent'): with 11 nulls "
          f"{p11['product']:.4f}, now {p0['product']:.4f}. That is the wrong formula even for independent meshes: both "
          "values are compared with the same null maximum, so the two events are positively dependent. For two values "
          f"that both exceed the same N nulls, with all N + 2 exchangeable, p = 2/((N + 1)(N + 2)): with 11 nulls "
          f"{p11['exact_exchangeable']:.4f}, with {N} {p0['exact_exchangeable']:.4f} (two-sided in |LR_anti|; the predicted "
          f"opposite signs hold: {p0['predicted_signs']}). Round 3's 'pair p ≈ 0.007' understated p by "
          f"{p11['exact_exchangeable'] / p11['product']:.2f}×.", ""]
    T.append((f"Both mirror designs beyond all {N} nulls", "CONFIRMED" if beyond else "CHANGED",
              f"rank p 1/{N + 1} each; LR_anti ratio LeftOnly {min(lo):.2f}–{max(lo):.2f}×, RightOnly {min(ro):.2f}–{max(ro):.2f}× "
              f"(all-null ruler)", "lobe_round5.json: anti, anti3"))
    T.append(("Pair p", "CHANGED (formula)", f"product {p11['product']:.4f} (11 nulls) → exact {p0['exact_exchangeable']:.4f} "
              f"(N = {N}, 2/((N+1)(N+2))); round 3 understated p by {p11['exact_exchangeable'] / p11['product']:.2f}×",
              "lobe_round5.json: pairs"))

    # ------------------------------------------------------------------ 4 independence
    ind = res["independence"]
    sup = sum(r["independence"] == "supported" for r in ind)
    L += ["## 4. Do the meshes' asymmetries behave as independent draws? (four rotated samples)", "",
          "LR_anti of the healthy meshes (one geometry, meshed several times), with the criterion fixed before the new "
          "files were loaded: supported if the values take both signs with |mean| < SD and q = rms(rot − H6) / (√2 × SD of "
          "all nulls) ≥ 0.5; contradicted if all share a sign with |mean| > SD, or q < 0.5.", "",
          _t(ind, list(ind[0]), {k: "+.2f" for k in ind[0] if isinstance(ind[0][k], float)}
             | {"q_rot_vs_H6": ".2f", "H7_vs_H6": ".2f", "healthy_SD": ".2f", "SD_all_nulls": ".2f"}), "",
          f"**Result.** Independence supported in {sup} of {len(ind)} method × reference cases. q (rotated vs H6) "
          f"{min(r['q_rot_vs_H6'] for r in ind):.2f}–{max(r['q_rot_vs_H6'] for r in ind):.2f}; the same-lineage pair H7 vs H6 "
          f"{min(r['H7_vs_H6'] for r in ind):.2f}–{max(r['H7_vs_H6'] for r in ind):.2f} in the same units. This tests "
          "rotation, not mirroring: a mesher that reproduced a mirrored mesh would still pass it.", ""]
    T.append(("Independence of mesh asymmetries", f"{'supported' if sup == len(ind) else ('mixed' if sup else 'contradicted')} "
              f"({sup}/{len(ind)})", f"q {min(r['q_rot_vs_H6'] for r in ind):.2f}–{max(r['q_rot_vs_H6'] for r in ind):.2f}; "
              "rotation only, mirroring untested", "lobe_round5.json: independence"))

    # ------------------------------------------------------------------ 5 rulers
    rl = res["rulers"]
    cr = res["cr"]
    b24 = res["b24"]
    rcols = ["reference", "rulers"] + [f"ruler {s}" for s in SHORT] + ["ruler_LR", "ruler_FB"] + [c for c in rl[0] if c.endswith("max sector")]
    L += ["## 5. Rulers three ways", "",
          "Sector, LR and FB rulers (primary method), as in round 3, for each null set:", "",
          _t(rl, rcols, {k: ".2f" for k in rcols if k not in ("reference", "rulers")}), "",
          "Ratios of the mirror and blind designs to those rulers:", "",
          _t(rl, ["reference", "rulers"] + [c for c in rl[0] if c.endswith("ratio")], {c: ".2f" for c in rl[0] if c.endswith("ratio")}), "",
          "Cross-ratio phase counts (18 distinct statistics, LeftOnly ≥ 3× the floor; null files ≥ 3× leave-one-out):", "",
          _t(_na(cr), list(cr[0])), "",
          "Bias-corrected Moderate front/back (round-2 B24):", "",
          _t(b24, list(b24[0]), {k: ("+.2f" if k.startswith("FB_") or k == "corrected" else ".2f") for k in b24[0] if isinstance(b24[0][k], float)}), ""]

    # ------------------------------------------------------------------ 6 detection
    det = res["detection"]
    mci = res["mci"]
    fs = res["fit_summary"]
    fit = res["fit"]

    def dmin(v, key):
        rows = [r for r in det if r["variant"] == v]
        w = min(rows, key=lambda r: r[key])
        return w[key], w["design"], w["reference"]
    L += ["## 6. Detection re-graded (0.3b)", "",
          "Per design: best and worst affected sector over the sector ruler, and the largest sector value over the "
          "max-sector ruler (max(largest one-pass yardstick of a sector, largest |sector| of a no-change null)):", "",
          _t([r for r in det if r["variant"] in ("all", "without rot19")], list(det[0]),
             {"best_affected": ".2f", "worst_affected": ".2f", "max_sector": ".2f", "max_sector_ruler": ".2f", "max_sector_ratio": ".2f"}), "",
          "Tier counts (design × reference):", ""]
    cnt = []
    for v in VN:
        rows = [r for r in det if r["variant"] == v]
        cnt.append(dict(variant=v, **{f"best affected {t}": sum(tier(r["best_affected"]) == t for r in rows)
                                      for t in ("established", "sensitive", "not determined")},
                        **{f"max sector {t}": sum(tier(r["max_sector_ratio"]) == t for r in rows)
                           for t in ("established", "sensitive", "not determined")},
                        weakest_best=f"{dmin(v, 'best_affected')[0]:.2f} ({dmin(v, 'best_affected')[1]}, {dmin(v, 'best_affected')[2]})",
                        weakest_max_sector=f"{dmin(v, 'max_sector_ratio')[0]:.2f} ({dmin(v, 'max_sector_ratio')[1]}, {dmin(v, 'max_sector_ratio')[2]})"))
    L += [_t(cnt, list(cnt[0])), "", "MCI against rulers built without MCI (< 1 = nothing beyond):", "",
          _t(mci, list(mci[0]), {k: ".2f" for k in ("max_sector_ratio", "LR_ratio", "FB_ratio")}), ""]
    sep = []
    for ref in ("H7", "H6"):
        rows = [r for r in fit if r["reference"] == ref]
        tmin = min(r["explained_norm"] for r in rows if r["kind"] != "null")
        for v, sel in (("all", lambda d: True), ("without rot19", lambda d: d != "Null_rot19"), ("rot19 alone", lambda d: d == "Null_rot19")):
            nmax = max(r["explained_norm"] for r in rows if r["kind"] == "null" and sel(r["design"]))
            sep.append(dict(reference=ref, nulls=v, largest_null_explained=nmax, smallest_target_explained=tmin, ratio=tmin / nmax))
    L += ["Sector-shaped part of the data (explained norm of the primary fit, round 4 §1), smallest target over largest null:", "",
          _t(sep, list(sep[0]), {"largest_null_explained": ".2f", "smallest_target_explained": ".2f", "ratio": ".2f"}), ""]
    b_all, d_all, r_all = dmin("all", "best_affected")
    m_all, md_all, mr_all = dmin("all", "max_sector_ratio")
    s_all = min(r["ratio"] for r in sep if r["nulls"] == "all")
    s_wo = min(r["ratio"] for r in sep if r["nulls"] == "without rot19")
    sentence = (f"Against both references, every lobe design's largest sector value is at least {m_all:.1f}× the largest "
                f"no-change null's (weakest {md_all}, {mr_all}; {tier(m_all)}), and the sector-shaped part of every target is "
                f"at least {s_all:.1f}× that of every null ({tier(s_all)}).")
    L += [f"**Surviving detection claim (one sentence).** {sentence}",
          f"Per affected sector the picture is weaker: the weakest design's best affected sector is {b_all:.2f}× its "
          f"sector ruler ({d_all}, {r_all}; {tier(b_all)}). Without rot19: explained-norm separation {s_wo:.2f}×.", ""]
    T.append(("Detection (0.3b)", "re-graded", sentence, "lobe_round5.json: detection, mci, fit"))

    # ------------------------------------------------------------------ 7 staging
    lb = [r for r in b24 if r["set"] == "lobe_B"]
    la = [r for r in b24 if r["set"] == "lobe_A"]

    def rr(rows, v):
        x = [r[f"ratio ({v})"] for r in rows]
        return f"{min(x):.2f}–{max(x):.2f}×"
    L += ["## 7. Staging claims with and without rot19 (0.3a)", "",
          "The imaging claims table has one staging-type claim: the bias-corrected Moderate front/back magnitude (B24). "
          "Three ways: " + "; ".join(f"{v}: lobe_B {rr(lb, v)}, lobe_A {rr(la, v)}" for v in VN) + ". "
          "The R21/R32 staging verdict is the main session's; nothing in this folder computes it.", ""]
    T.append(("Staging (B24 bias-corrected FB)", tier(min(r["ratio (all)"] for r in lb)),
              f"lobe_B {rr(lb, VN[0])} (11 nulls) → {rr(lb, 'all')} (all), {rr(lb, 'without rot19')} (without rot19)",
              "lobe_round5.json: b24"))

    # ------------------------------------------------------------------ 8 round 3/4 computations
    r4 = res["r4"]
    try:
        committed = json.loads((OUT / "lobe_round4.json").read_text(encoding="utf-8"))
        same = (committed["fair"]["fair"] == r4[VN[0]]["fair"]["fair"]
                and [(x["hits"], x["false_alarms"], x["exact"]) for x in committed["loo"]]
                == [(x["hits"], x["false_alarms"], x["exact"]) for x in r4[VN[0]]["loo"]])
    except Exception:  # noqa: BLE001
        same = "not checked"
    rdt = []
    for v, d in r4.items():
        for s in d["readings"]:
            rdt.append(dict(nulls=v, **s))
    frt = []
    for v, d in r4.items():
        for s in d["fair"]["fair"]:
            frt.append(dict(nulls=v, **{k: s[k] for k in ("statistic", "calibration", "rule", "threshold", "hits",
                                                           "false_alarms", "exact", "n", "false_alarms_on_nulls")}))
    lot = []
    for v, d in r4.items():
        for s in d["loo"]:
            lot.append(dict(nulls=v, **{k: s[k] for k in ("held_out", "statistic", "kinds", "hits", "false_alarms", "exact", "n",
                                                           "exact_without_TestB", "TestB_read")}))
    L += ["## 8. Round-3 and round-4 computations with every null (points 1 and 3 of round 4, and the rank rules)", "",
          f"Regression: the '11 nulls (round 3)' column reproduces the committed `lobe_round4.json`: **{same}**.", "",
          "**Fit statistic (point 1).** Every design against both references (ρ and explained norm do not depend on the "
          "null set; the limit does not either):", "",
          _t(fs, list(fs[0]), {k: ".3f" for k in ("limit", "rho_rot19", "max_target_rho", "min_null_rho")}
             | {"rot19_data_norm": ".1f", "smallest_target_data_norm": ".1f", "spearman_rho_vs_data_norm": ".2f"}), "",
          _t([r for r in fit if r["kind"] == "null"], ["reference", "design", "rho", "data_norm", "explained_norm", "limit", "rejected"],
             {"rho": ".3f", "data_norm": ".1f", "explained_norm": ".1f", "limit": ".3f"}), "",
          "**Rank readings (round 3 §7).**", "", _t(rdt, list(rdt[0])), "",
          "**Born vs raw delay, identically calibrated (point 3).** Thresholds from the null rows only:", "",
          _t(frt, list(frt[0]), {"threshold": ".2f"}), "",
          "**Rank rules out of sample (round 4 §4).**", "", _t(lot, list(lot[0])), ""]
    tg = {v: _g(r4[v]["fair"]["fair"], statistic="Born", calibration="T_null_set", rule="gap") for v in r4}
    tt = {v: _g(r4[v]["fair"]["fair"], statistic="Born", calibration="T_null_set", rule="threshold") for v in r4}
    rawbest = {v: max((x for x in r4[v]["fair"]["fair"] if x["statistic"] != "Born" and x["calibration"] == "T_null_set"),
                      key=lambda x: (x["exact"], -x["false_alarms"])) for v in r4}
    born_loo = {v: _g(r4[v]["loo"], held_out="family", statistic="Born", kinds="gap/mid") for v in r4}
    L += [f"**Result.** Born, null-only threshold: {tt['all']['hits']}/{tt['all']['false_alarms']}/{tt['all']['exact']} "
          f"(hits/FA/exact) with all nulls vs {tt[VN[0]]['hits']}/{tt[VN[0]]['false_alarms']}/{tt[VN[0]]['exact']} with 11; "
          f"Born gap: {tg['all']['hits']}/{tg['all']['false_alarms']}/{tg['all']['exact']} vs "
          f"{tg[VN[0]]['hits']}/{tg[VN[0]]['false_alarms']}/{tg[VN[0]]['exact']}; best raw rule (same calibration): "
          f"{rawbest['all']['statistic']} {rawbest['all']['rule']} {rawbest['all']['hits']}/{rawbest['all']['false_alarms']}/"
          f"{rawbest['all']['exact']}. Born rank rule leave-one-family-out: {born_loo['all']['hits']}/"
          f"{born_loo['all']['false_alarms']}/{born_loo['all']['exact']} of {born_loo['all']['n']} (11 nulls: "
          f"{born_loo[VN[0]]['hits']}/{born_loo[VN[0]]['false_alarms']}/{born_loo[VN[0]]['exact']} of {born_loo[VN[0]]['n']}); "
          f"Test_B read {born_loo['all']['TestB_read']}.", ""]
    T.append(("Round 4 points 1, 3, 4 with every null", "re-run", f"Born gap {tg['all']['exact']}/{tg['all']['n']} exact, "
              f"{tg['all']['false_alarms']} FA; Born rank LOFO {born_loo['all']['hits']}/{born_loo['all']['false_alarms']}/"
              f"{born_loo['all']['exact']}; nulls rejected by the fit rule: "
              + "; ".join(f"{s['reference']} {s['nulls_rejected']}" for s in fs), "lobe_round5.json: r4, fit"))

    # ------------------------------------------------------------------ 9 0.3(c)
    tr, ring, ext, one = res["typ_rows"], res["typ_ring"], res["typ_extreme"], res["one_sided"]
    nmesh = len({r["mesh"] for r in tr})
    h6x = [r for r in ext if r["most_extreme"] == "H6"]
    L += [f"## 9. Is the primary reference typical? (0.3c, POST-HOC, not adopted)", "",
          f"Each of the {nmesh} healthy meshes against the complex mean of the other {nmesh - 1} (frozen inversion; primary "
          "method shown, all three in the JSON):", "",
          _t([r for r in tr if r["method"] == "Tikhonov dS"], ["mesh", "method"] + SHORT + ["LR", "FB", "max_abs_sector"],
             {**{s: "+.2f" for s in SHORT}, "LR": "+.2f", "FB": "+.2f", "max_abs_sector": ".2f"}), "",
          "Raw neighbour-path delay against the mean of the others (deg; + = more delay):", "",
          _t(ring, list(ring[0]), {k: "+.2f" for k in ("ring_mean_delay", "ring_range", "left_minus_right")}), "",
          "Criterion (fixed before loading): H6 is atypical if it is the most extreme in at least twice the chance number "
          "of rows, or if all other meshes lie on one side of it for at least max(2, 3 × the chance expectation) statistics.", "",
          f"Most extreme mesh per statistic ({len(ext)} statistic × method rows; H6 is most extreme in {len(h6x)}; "
          f"chance alone ≈ {len(ext) / nmesh:.1f}):", "",
          _t(ext, list(ext[0]), {"H6": "+.2f", "largest_other": ".2f"}), "",
          "Against H6 as the reference, the other healthy meshes per statistic (primary method; one side = all on one side):", "",
          _t(one, list(one[0])), ""]
    calls = res["alt_calls"]
    ch = []
    for d in sorted({r["design"] for r in calls}):
        h6r = _g(calls, design=d, reference="H6")
        mr = _g(calls, design=d, reference="mean of healthy meshes")
        h7r = _g(calls, design=d, reference="H7")
        ch.append(dict(design=d, truth=h6r["truth"], called_H7=h7r["called"], called_H6=h6r["called"], called_mean=mr["called"],
                       side_H6=h6r["side"], side_mean=mr["side"], rank_H6=h6r["rank_set"], rank_mean=mr["rank_set"],
                       LR_H6=h6r["LR"], LR_mean=mr["LR"]))
    changed = [r for r in ch if (r["called_H6"], r["side_H6"], r["rank_H6"]) != (r["called_mean"], r["side_mean"], r["rank_mean"])]

    def toset(x):
        return set() if x == "none" else set(x.split())
    tally = []
    for rn in ("H7", "H6", "mean of healthy meshes"):
        for kind, col in (("frozen T_abs calls", "called"), ("rank set (largest gap, gate T_null; not adopted)", "rank_set")):
            h = m_ = fa = ex = 0
            for r in [x for x in calls if x["reference"] == rn]:
                t, c = toset(r["truth"]), toset(r[col])
                h, m_, fa, ex = h + len(t & c), m_ + len(t - c), fa + len(c - t), ex + (t == c)
            tally.append(dict(reference=rn, reading=kind, hits=h, misses=m_, false_alarms=fa, exact=f"{ex}/{len(ch)}"))
    L += ["Claims that use H6 as their reference: the RightOnly C6 verdict (committed rule: LR vs H6); the blind test's "
          "'FAIL with the matched reference'; the lobe_A set (one-pass yardstick, bias-corrected FB in lobe_A); the H6 rows of "
          "the Test_B readings, rulers and LR_anti; the raw per-antenna delays of round 3 (§5) and the user's 0.3(b) numbers.", "",
          "Frozen calls (primary method, frozen thresholds) against H7, H6 and the mean of all healthy meshes:", "",
          _t(ch, list(ch[0]), {"LR_H6": "+.2f", "LR_mean": "+.2f"}), "",
          "Scored against the truth (sectors, summed over the designs above):", "",
          _t(tally, list(tally[0])), "",
          "The committed C6 rule applied to each reference:", "",
          _t(res["alt_c6"], list(res["alt_c6"][0]), {"LR": "+.2f", "phase_3p4": "+.2f", "phase_3p6": "+.2f"}), ""]
    c6m = _g(res["alt_c6"], reference="mean of healthy meshes")["verdict"]
    one_side = [r["statistic"] for r in one if r["one_side"]]
    p_one = 2 * 0.5 ** (nmesh - 1)                                    # all others on either side of H6
    exp_one = len(one) * p_one
    tH6 = _g(tally, reference="H6", reading="frozen T_abs calls")
    tM = _g(tally, reference="mean of healthy meshes", reading="frozen T_abs calls")
    tH7 = _g(tally, reference="H7", reading="frozen T_abs calls")
    outlier = len(h6x) >= 2 * len(ext) / nmesh or len(one_side) >= max(2, 3 * exp_one)
    L += [f"**Result.** H6 is the most extreme of {nmesh} meshes in {len(h6x)} of {len(ext)} statistic rows (≈ "
          f"{len(ext) / nmesh:.1f} expected if the meshes are exchangeable): " + (", ".join(f"{r['method']} {r['statistic']}" for r in h6x) or "none")
          + f". Statistics on which all {nmesh - 1} other healthy meshes lie on one side of H6: {', '.join(one_side) or 'none'} "
          f"({len(one_side)} of {len(one)}; chance {p_one:.3f} each, ≈ {exp_one:.1f} expected, the statistics are correlated). "
          f"With the mean of the healthy meshes as reference, frozen calls score {tM['hits']} hits / {tM['false_alarms']} FA / "
          f"{tM['exact']} exact, against {tH6['hits']} / {tH6['false_alarms']} / {tH6['exact']} with H6 and {tH7['hits']} / "
          f"{tH7['false_alarms']} / {tH7['exact']} with H7; calls, side or rank set change for {len(changed)} of {len(ch)} designs"
          + (f" ({', '.join(r['design'] for r in changed)})" if changed else "")
          + f". The C6 rule gives {c6m} (committed, vs H6: {_g(res['alt_c6'], reference='H6')['verdict']}).", ""]
    T.append(("Reference typicality (0.3c)", "H6 " + ("atypical on some statistics" if outlier else "not shown to be an outlier"),
              f"H6 most extreme in {len(h6x)}/{len(ext)} rows (chance ≈ {len(ext) / nmesh:.1f}); all others on one side for "
              f"{len(one_side)}/{len(one)} statistics (≈ {exp_one:.1f} by chance); mean reference: frozen calls {tM['hits']}/{tM['false_alarms']}/"
              f"{tM['exact']} vs H6 {tH6['hits']}/{tH6['false_alarms']}/{tH6['exact']}; C6 {c6m}", "lobe_round5.json: typ_*, one_sided, alt_*"))

    # ------------------------------------------------------------------ 10 user's at-a-glance
    gl = res["glance"]
    gb = [r for r in gl if r["view"] == "band 3.2-4.2"]
    agree = sum((r["ring_mean_delay"] > 0) == (r["user_ring_mean"] > 0) for r in gb if r["user_ring_mean"] is not None)
    L += ["## 10. The user's at-a-glance phase columns, recomputed (verify, do not adopt)", "",
          "Mine: per neighbour path, minus the mean phase change against H6 over the window (delay positive); ring mean "
          "over the six neighbour paths; spread = SD and range over them; left − right = mean(T1-T2, T2-T3, T3-T4) − "
          "mean(T4-T5, T5-T6, T6-T1). These definitions do not reproduce the user's numbers exactly on rot07/rot19 "
          "(checked before loading the new files), so only signs and ordering are compared.", "",
          _t(_na(gl), list(gl[0]), {k: "+.2f" for k in ("ring_mean_delay", "path_SD", "path_range", "left_minus_right")}), "",
          f"**Result.** Ring-mean delay has the user's sign (more delay than H6) for {agree} of {len(gb)} rotated nulls (band "
          f"3.2–4.2 GHz). Rank agreement of the spread (Spearman, n = {len(gb)}): {_f(res['glance_spearman_spread'])}.", ""]
    T.append(("User's at-a-glance phase columns", "signs verified" if agree == len(gb) else "partly verified",
              f"ring-mean delay sign {agree}/{len(gb)}; definitions differ, magnitudes not compared", "lobe_round5.json: glance"))

    # ------------------------------------------------------------------ 11 survival
    sv = res["survival"]

    def cell(x, unit):
        if x is None or (isinstance(x, float) and not np.isfinite(x)):
            return "n/a"
        if unit == "p":
            return f"{x:.4f}"
        if unit == "count":
            return str(x)
        return f"{x:.2f}"
    st = [dict(claim=r["claim"], **{v: cell(r[v], r["unit"]) for v in VN}, tier_all=r["tier_all"],
               tier_without_rot19=r["tier_without_rot19"]) for r in sv]
    moved = [r for r in sv if r["unit"] == "ratio" and tier(r[VN[0]]) != tier(r["all"])]
    L += ["## 11. Survival table (11 nulls → all nulls, three ways)", "", _t(st, list(st[0])), "",
          f"**Tier changes from 11 nulls to all nulls:** " + ("; ".join(f"{r['claim']}: {tier(r[VN[0]])} → {tier(r['all'])}"
                                                                       for r in moved) or "none") + ".", ""]
    T.append(("Survival (11 → all nulls)", f"{len(moved)} tier change(s)", "; ".join(f"{r['claim']}: {tier(r[VN[0]])} → {tier(r['all'])}"
                                                                                      for r in moved) or "none", "lobe_round5.json: survival"))

    L += ["## Final table", "", _t([dict(item=a, verdict=b, change=c, evidence=d) for a, b, c, d in T],
                                   ["item", "verdict", "change", "evidence"]), ""]
    (OUT / "lobe_round5.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    sec = [f"## 14. Round 5 (POST-HOC): every rotated null (N = {N}), rulers three ways, pair p, reference typicality", "",
           "Full text: `results/imaging/lobe_round5.md`.", "",
           _t([dict(item=a, verdict=b, change=c) for a, b, c, d in T], ["item", "verdict", "change"]), ""]
    if "## 14." in rep:
        i0 = rep.index("## 14.")
        j = rep.find("\n## ", i0 + 5)
        rep = rep[:i0] + "\n".join(sec) + ("\n" + rep[j + 1:] if j >= 0 else "\n")
    else:
        rep = rep.rstrip("\n") + "\n\n" + "\n".join(sec) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
