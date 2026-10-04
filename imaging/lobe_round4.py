"""Round 4 (POST-HOC throughout): what the fit-rejection rule separates, a fair Born-vs-raw comparison, and
leave-one-design-out / leave-one-family-out scoring of the rank rules.

    python imaging/lobe_round4.py

Writes results/imaging/lobe_round4.{md,json} and section 13 of lobe_report.md. Frozen files, protocols,
predictions and the committed scorers are unchanged (score_testb.py is imported read-only).
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_round3 as R3  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import score_testb as TB  # noqa: E402
from imaging.common import OUT, ROOT, git_hash  # noqa: E402
from imaging.report_lobe import SHORT, _t  # noqa: E402

REFS = R3.REFS
PRIMARY = RL.METHODS[0]
NULLSET = ("Healthy_sliced", "Healthy_sliced_new", "MCI_lobe_c3") + R3.ROT   # no cortical change
GATES = np.round(np.arange(0.0, 20.0001, 0.25), 2)
FAMILY = {"Mild_lobe": "Mild", "Mild_lobe_new": "Mild", "Moderate_lobe": "Moderate", "Moderate_lobe_c3": "Moderate",
          "Severe_lobe": "Severe", "Severe_lobe_c3": "Severe",
          "Healthy_sliced": "healthy cross-reference", "Healthy_sliced_new": "healthy cross-reference",
          **{r: "rotated nulls" for r in R3.ROT}}


def kind_of(d):
    if not R3.affected(d):
        return "null"
    return {"Test_B": "blind test", "RightOnly_test": "replication", "LeftOnly_test_c3": "blind test"}.get(d, "stage")


def rng(rows, key, sel):
    v = [r[key] for r in rows if sel(r)]
    return f"{min(v):.1f}–{max(v):.1f}"


# ----------------------------------------------------------------------------------------------- 1. fit statistic
def fit_stats(ctx):
    out, lim = [], {}
    for rlab, ref in REFS.items():
        M, R = ctx.model(ref), ctx.S[ref]
        known = {d: TB.residual(M, PRIMARY, ctx.lam, ctx.S[d], R, ctx.fi)[0] for d in TB.CORTICAL}
        lim[rlab] = TB.REJECT_FACTOR * max(known.values())
        for d in R3.TRUTH:
            if d == ref:
                continue
            rho, dn = TB.residual(M, PRIMARY, ctx.lam, ctx.S[d], R, ctx.fi)
            out.append(dict(reference=rlab, design=d, kind=kind_of(d), rho=rho, data_norm=dn, abs_residual=rho * dn,
                            explained_norm=float(np.sqrt(max(dn ** 2 - (rho * dn) ** 2, 0.0))), limit=lim[rlab],
                            rejected=bool(rho > lim[rlab])))
    out.sort(key=lambda r: (r["reference"], -r["rho"]))
    summ = []
    for rlab in REFS:
        rows = [r for r in out if r["reference"] == rlab]
        isn = lambda r: r["kind"] == "null"  # noqa: E731
        ist = lambda r: r["kind"] != "null"  # noqa: E731
        summ.append(dict(reference=rlab, limit=lim[rlab], rho_rot19=next(r["rho"] for r in rows if r["design"] == "Null_rot19"),
                         accepted_targets_above_rot19=sum(r["rho"] > next(x["rho"] for x in rows if x["design"] == "Null_rot19")
                                                          for r in rows if ist(r) and not r["rejected"]),
                         max_target_rho=max(r["rho"] for r in rows if ist(r)), min_null_rho=min(r["rho"] for r in rows if isn(r)),
                         nulls_accepted=", ".join(r["design"] for r in rows if isn(r) and not r["rejected"]) or "none",
                         nulls_rejected=", ".join(r["design"] for r in rows if isn(r) and r["rejected"]) or "none",
                         targets_rejected=", ".join(r["design"] for r in rows if ist(r) and r["rejected"]) or "none",
                         null_abs_residual=rng(rows, "abs_residual", isn), target_abs_residual=rng(rows, "abs_residual", ist),
                         null_explained=rng(rows, "explained_norm", isn), target_explained=rng(rows, "explained_norm", ist),
                         rot19_data_norm=next(r["data_norm"] for r in rows if r["design"] == "Null_rot19"),
                         smallest_target_data_norm=min(r["data_norm"] for r in rows if ist(r)),
                         spearman_rho_vs_data_norm=float(spearmanr([r["rho"] for r in rows], [r["data_norm"] for r in rows]).statistic)))
    return out, summ


# ----------------------------------------------------------------------------------------------- per-row values
def row_values(ctx):
    rows = []
    for rlab, ref in REFS.items():
        fx = C3.make_x(ctx.model(ref), PRIMARY, ctx.lam)
        R = ctx.S[ref]
        for d in R3.TRUTH:
            if d == ref:
                continue
            raw = R3.per_antenna_delay(ctx.S[d], R, ctx.fi)
            rows.append(dict(reference=rlab, ref=ref, design=d, truth=R3.affected(d), is_null=d in NULLSET,
                             vals={"Born": fx(ctx.S[d][ctx.fi], R[ctx.fi])[6:12], "raw uncentred": raw,
                                   "raw centred": R3.centred(raw)}))
    return rows


def tally(rows, sets):
    h = m = fa = ex = 0
    for r, s in zip(rows, sets):
        t = r["truth"]
        h += len(s & t)
        m += len(t - s)
        fa += len(s - t)
        ex += s == t
    return dict(hits=h, misses=m, false_alarms=fa, exact=ex, n=len(rows))


def read_rule(kind, G, v):
    if v.max() <= G:
        return set()
    if kind == "threshold":
        return set(np.flatnonzero(v > G))
    if kind == "gap":
        return set(np.argsort(-v)[:R3.largest_gap_k(v, G)])
    return set(np.flatnonzero(v > 0.5 * (v.max() + v.min())))          # "mid"


# ----------------------------------------------------------------------------------------------- 3. fair comparison
def fair(ctx, rows):
    out = {}
    before_gate, after_gate = {}, {}
    for rlab, ref in REFS.items():
        before_gate[rlab] = max(R3.per_antenna_delay(ctx.S[d], ctx.S[ref], ctx.fi).max() for d in R3.NULL9 if d != ref)
        after_gate[rlab] = max(R3.centred(R3.per_antenna_delay(ctx.S[d], ctx.S[ref], ctx.fi)).max()
                               for d in ("Healthy_sliced", "Healthy_sliced_new", "MCI_lobe_c3") + R3.ROT if d != ref)
    out["round3_raw_before"] = tally(rows, [read_rule("gap", before_gate[r["reference"]], r["vals"]["raw uncentred"]) for r in rows])
    out["round3_raw_after"] = tally(rows, [read_rule("gap", after_gate[r["reference"]], r["vals"]["raw centred"]) for r in rows])
    out["round3_born_gap"] = tally(rows, [read_rule("gap", ctx.fz["rules"][PRIMARY]["T_null"], r["vals"]["Born"]) for r in rows])
    out["gates_round3"] = dict(before=before_gate, after=after_gate)
    # thresholds from the null rows ONLY, fixed before any hit is counted
    null_rows = [r for r in rows if r["is_null"]]
    thr = {}
    for stat in ("Born", "raw uncentred", "raw centred"):
        t_null = max(r["vals"][stat].max() for r in null_rows)
        mild = next(r for r in rows if r["design"] == "Mild_lobe" and r["ref"] == "Healthy_sliced")["vals"][stat]
        aff = np.array([k in R3.affected("Mild_lobe") for k in range(6)])
        lo, hi = mild[~aff].max(), mild[aff].min()
        t_mild = 0.5 * (lo + hi) if hi > lo else np.nan
        thr[stat] = dict(T_null_set=float(t_null), T_mild=float(t_mild), T_recipe=float(np.nanmax([t_null, t_mild])))
    out["thresholds"] = thr
    tabs = []
    for stat in ("Born", "raw uncentred", "raw centred"):
        for cal in ("T_null_set", "T_recipe"):
            for kind in ("threshold", "gap"):
                G = thr[stat][cal]
                t = tally(rows, [read_rule(kind, G, r["vals"][stat]) for r in rows])
                tn = tally(null_rows, [read_rule(kind, G, r["vals"][stat]) for r in null_rows])
                tabs.append(dict(statistic=stat, calibration=cal, rule=kind, threshold=G, **t, false_alarms_on_nulls=tn["false_alarms"]))
    out["fair"] = tabs
    return out


# ----------------------------------------------------------------------------------------------- 4. leave-one-out
def loo(rows, stat, kinds, by_family=False):
    key = (lambda d: FAMILY.get(d, d)) if by_family else (lambda d: d)
    groups = sorted({key(r["design"]) for r in rows})
    chosen, sets_by_row = [], {}
    for h in groups:
        train = [r for r in rows if key(r["design"]) != h and r["design"] != "Test_B"]
        best, cands = None, []
        for kind in kinds:
            for G in GATES:
                t = tally(train, [read_rule(kind, G, r["vals"][stat]) for r in train])
                k_ = (t["exact"], -t["false_alarms"], t["hits"])
                if best is None or k_ > best:
                    best, cands = k_, [(kind, G)]
                elif k_ == best:
                    cands.append((kind, G))
        k0 = next(k for k in kinds if any(c[0] == k for c in cands))          # stated tie-break: kind order
        gs = sorted(G for k, G in cands if k == k0)
        G0 = gs[len(gs) // 2]                                                  # middle of the tied gate interval
        chosen.append(dict(held_out=h, rule=k0, gate=float(G0), train_exact=best[0], train_false=-best[1]))
        for r in rows:
            if key(r["design"]) == h:
                sets_by_row[id(r)] = read_rule(k0, G0, r["vals"][stat])
    tot = tally(rows, [sets_by_row[id(r)] for r in rows])
    noTB = [r for r in rows if r["design"] != "Test_B"]
    tnb = tally(noTB, [sets_by_row[id(r)] for r in noTB])
    tb = [(r["reference"], " ".join(SHORT[k].split()[0] for k in sorted(sets_by_row[id(r)])) or "none")
          for r in rows if r["design"] == "Test_B"]
    return dict(held_out="family" if by_family else "design", statistic=stat, kinds="/".join(kinds), **tot,
                exact_without_TestB=f"{tnb['exact']}/{tnb['n']}", false_without_TestB=tnb["false_alarms"],
                TestB_read="; ".join(f"{a}: {b}" for a, b in tb)), chosen


def main():
    ctx = C3.Ctx(20)
    res = dict(code=git_hash(ROOT))
    res["fit"], res["fit_summary"] = fit_stats(ctx)
    rows = row_values(ctx)
    res["fair"] = fair(ctx, rows)
    res["loo"], res["loo_chosen"] = [], {}
    for fam in (False, True):
        for stat, kinds in (("Born", ("gap", "mid")), ("Born", ("threshold",)), ("raw centred", ("gap", "mid")),
                            ("raw centred", ("threshold",)), ("raw uncentred", ("gap", "mid")), ("raw uncentred", ("threshold",))):
            s, ch = loo(rows, stat, kinds, by_family=fam)
            res["loo"].append(s)
            res["loo_chosen"][f"{stat} | {'/'.join(kinds)} | {'family' if fam else 'design'}"] = ch
    (OUT / "lobe_round4.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item")
                                                     else (o.tolist() if hasattr(o, "tolist") else (sorted(o) if isinstance(o, set) else str(o)))),
                                          encoding="utf-8")
    write_md(res)
    print("done")


# ----------------------------------------------------------------------------------------------- text
def write_md(res):
    fs, fit, fr = res["fit_summary"], res["fit"], res["fair"]
    T = []
    L = ["# Round 4 (imaging session, POST-HOC): fit rejection, fair Born-vs-raw comparison, leave-one-out", "",
         f"Computed by `python imaging/lobe_round4.py` at code `{res['code']}`; numbers in `results/imaging/lobe_round4.json`. "
         "Everything here is post hoc. Frozen files, protocols, predictions and the committed scorers are unchanged.", ""]
    # 1
    L += ["## 1. What the fit-rejection rule separates", "",
          "Fit statistic = relative whitened misfit ρ = ‖d − Jx̂‖ / ‖d‖ of the primary (Tikhonov dS) fit, the quantity in "
          "the Test_B protocol. Rejected if ρ > 1.5 × the largest ρ of the known cortical designs. Explained norm = "
          "√(‖d‖² − ‖d − Jx̂‖²), the sector-shaped part of the data. Every design against both references, sorted by ρ:", "",
          _t(fit, ["reference", "design", "kind", "rho", "data_norm", "abs_residual", "explained_norm", "limit", "rejected"],
             {"rho": ".3f", "data_norm": ".1f", "abs_residual": ".1f", "explained_norm": ".1f", "limit": ".3f"}), "",
          _t(fs, list(fs[0]), {"limit": ".3f", "rho_rot19": ".3f", "max_target_rho": ".3f", "min_null_rho": ".3f",
                               "rot19_data_norm": ".1f", "smallest_target_data_norm": ".1f", "spearman_rho_vs_data_norm": ".2f"}), ""]
    a_tgt = sum(s["accepted_targets_above_rot19"] for s in fs)
    L += [f"**Answer.** Accepted real targets above rot19's ρ: {a_tgt} (H7 and H6 together). There can be none: rot19 sits "
          "above the rejection limit, so every accepted design sits below it. What the numbers show:",
          "- **In this sample ρ separates nulls from targets completely, with a gap.** Targets have ρ ≤ "
          + ", ".join(f"{s['reference']} {s['max_target_rho']:.3f}" for s in fs) + "; nulls have ρ ≥ "
          + ", ".join(f"{s['reference']} {s['min_null_rho']:.3f}" for s in fs) + ". The committed limit ("
          + ", ".join(f"{s['reference']} {s['limit']:.3f}" for s in fs) + ") sits **above** the gap, so it rejects some "
          "nulls and accepts others. Accepted nulls: " + "; ".join(f"{s['reference']} {s['nulls_accepted']}" for s in fs)
          + ". Rejected: " + "; ".join(f"{s['reference']} {s['nulls_rejected']}" for s in fs) + ".",
          "- **It is not the total data size.** rot19's data norm ("
          + ", ".join(f"{s['reference']} {s['rot19_data_norm']:.1f}" for s in fs) + ") is comparable to the smallest targets' ("
          + ", ".join(f"{s['reference']} {s['smallest_target_data_norm']:.1f}" for s in fs) + "). The absolute misfits overlap: "
          "nulls " + ", ".join(f"{s['reference']} {s['null_abs_residual']}" for s in fs) + ", targets "
          + ", ".join(f"{s['reference']} {s['target_abs_residual']}" for s in fs) + ", and rot19's exceeds LeftOnly's and "
          "Test_B's. ρ correlates with the data norm (Spearman " + ", ".join(f"{s['reference']} {s['spearman_rho_vs_data_norm']:+.2f}" for s in fs)
          + "), but rot19 is the counterexample.",
          "- **The separating quantity is the sector-shaped part of the data**: explained norm nulls "
          + ", ".join(f"{s['reference']} {s['null_explained']}" for s in fs) + ", targets "
          + ", ".join(f"{s['reference']} {s['target_explained']}" for s in fs) + ". A mesh-only difference is mostly not "
          "sector-shaped; a lobe change mostly is.",
          "**What the rule separates:** data whose sector-shaped part is large relative to the remaining (mesh) "
          "structure from data whose sector-shaped part is not. So it does fire on mesh noise alone, as the objection "
          "says. It would equally reject a real change whose sector-shaped part were as small as a null's (explained norm "
          "about 3–4, roughly a third of LeftOnly's). For real targets it is a detection gate on sector-shaped signal "
          "against mesh structure, not a check that the sector model is right. 'Correctly flagged' (round 3) is "
          "withdrawn. A limit inside the observed gap would have rejected every null and accepted every target here, "
          "but choosing it now would be post hoc. **Verdict: CHANGED.**", ""]
    T.append(("1 fit rejection", "CHANGED", "'rot19 correctly rejected' → a gate on the sector-shaped part of the data vs mesh "
              f"structure (explained norm: nulls {', '.join(s['null_explained'] for s in fs)}, targets {', '.join(s['target_explained'] for s in fs)}); "
              "fires on mesh noise alone; the limit sits above the null/target gap, so nulls are both accepted and rejected; "
              "it would reject a real change with a null-sized sector component", "lobe_round4.json: fit"))
    # 2
    L += ["## 2. Pass gap in ruler language", "",
          "Re-stated in `lobe_round3.md` §9 and its final table (round-3 text revised). Ratio to the largest of n = 3 "
          "twin differences: the common-mode delay excess is 1.31×, and the affected-sector level 1.9–2.1× depending on "
          "method and reference. A value beyond all three twins has a rank p of 1/4. LR and phase share: **not "
          "separable from the pass gap**. Common-mode level: **undetermined**. Sector level: **undetermined**, at the "
          "2× edge in some cases only. Round 3's 'not explained by the pass gap' is withdrawn.", ""]
    T.append(("2 pass gap", "CHANGED", "'not explained' → undetermined (1.31× and 1.9–2.1× the largest of n = 3)", "lobe_round3.md §9"))
    # 3
    b, a, bg, th = fr["round3_raw_before"], fr["round3_raw_after"], fr["round3_born_gap"], fr["thresholds"]
    L += ["## 3. Born vs raw delay, calibrated identically", "",
          "**Before and after the mid-run redefinition** (round 3, largest-gap reading):", "",
          _t([dict(version="round-3 raw, first run: uncentred, gate = max over the nine 'symmetric' designs incl. stages "
                           f"({', '.join(f'{k} {v:.2f}°' for k, v in fr['gates_round3']['before'].items())})", **b),
              dict(version="round-3 raw, as reported: centred, gate = max over no-cortical-change designs "
                           f"({', '.join(f'{k} {v:.2f}°' for k, v in fr['gates_round3']['after'].items())})", **a),
              dict(version="round-3 Born (gate = frozen T_null 4.93)", **bg)],
             ["version", "hits", "misses", "false_alarms", "exact", "n"]), "",
          "The first version was wrong: its 'null' set contained diseased stages, which set the gate at 14–16°. The "
          "second fixed that and also removed the common mode, while the results were visible. Below, both raw variants "
          "and the Born values are calibrated **the same way**. Thresholds are computed from the null rows only ("
          f"{', '.join(NULLSET)}, each against each reference, rotated nulls included) **before any hit is counted**. "
          "'T_null_set' gives zero false alarms on the nulls by construction. 'T_recipe' = max(T_null_set, T_mild) adds "
          "the frozen recipe's Mild-tuned midpoint (Mild_lobe against Healthy_sliced; n/a where Mild's affected and "
          "healthy sectors overlap):", "",
          _t([dict(statistic=k, **v) for k, v in th.items()], ["statistic", "T_null_set", "T_mild", "T_recipe"],
             {"T_null_set": ".2f", "T_mild": ".2f", "T_recipe": ".2f"}), "",
          _t(fr["fair"], ["statistic", "calibration", "rule", "threshold", "hits", "misses", "false_alarms", "exact", "n",
                          "false_alarms_on_nulls"], {"threshold": ".2f"}), ""]
    fair_ = {(r["statistic"], r["calibration"], r["rule"]): r for r in fr["fair"]}
    comp = []
    for cal in ("T_null_set", "T_recipe"):
        for rule in ("threshold", "gap"):
            bo, rc, ru = fair_[("Born", cal, rule)], fair_[("raw centred", cal, rule)], fair_[("raw uncentred", cal, rule)]
            comp.append(dict(calibration=cal, rule=rule, Born=f"{bo['hits']} hits / {bo['false_alarms']} FA / {bo['exact']} exact",
                             raw_centred=f"{rc['hits']} / {rc['false_alarms']} / {rc['exact']}",
                             raw_uncentred=f"{ru['hits']} / {ru['false_alarms']} / {ru['exact']}",
                             exact_gap_vs_best_raw=bo["exact"] - max(rc["exact"], ru["exact"])))
    thr_g = [c["exact_gap_vs_best_raw"] for c in comp if c["rule"] == "threshold"]
    gap_g = [c["exact_gap_vs_best_raw"] for c in comp if c["rule"] == "gap"]
    span = lambda g: f"{min(g):+d}" if min(g) == max(g) else f"{min(g):+d}…{max(g):+d}"  # noqa: E731
    lo_ = res["loo"]
    bfam = next(x for x in lo_ if x["statistic"] == "Born" and x["kinds"] == "threshold" and x["held_out"] == "family")
    rfam = max((x for x in lo_ if x["statistic"].startswith("raw") and x["held_out"] == "family"),
               key=lambda x: (x["exact"], -x["false_alarms"]))
    verdict3 = (f"with threshold readings calibrated on the nulls only, the Born map adds nothing measurable ({span(thr_g)} exact "
                f"set of 26); with the rank (largest-gap) reading it keeps {span(gap_g)} exact sets and makes 0 false alarms "
                "against the raw delay's 5–6. With thresholds tuned out of sample on labelled designs (§4, leave-one-family-out), "
                f"the Born threshold reaches {bfam['exact']}/26 exact with {bfam['false_alarms']} false alarms, the best raw rule "
                f"{rfam['exact']}/26 with {rfam['false_alarms']}. So the Born advantage depends on the calibration: absent under "
                "null-only thresholds, a few exact sets and many fewer false alarms otherwise")
    L += ["Side by side:", "", _t(comp, list(comp[0])), "",
          f"**Verdict: CHANGED.** Round 3's 'Born adds a calibrated level' compared a Born reading calibrated on frozen "
          f"nulls with a raw reading calibrated differently. Under identical calibration, {verdict3}. The raw delay has "
          "no Mild-tuned level at all: Mild's affected and healthy antennas overlap in raw delay against the 7-pass "
          "reference.", ""]
    T.append(("3 Born vs raw (fair)", "CHANGED", f"round-3 gap 20 vs 14 exact, 0 vs 6 FA → identical calibration: {verdict3}",
              "lobe_round4.json: fair"))
    # 4
    lo = res["loo"]
    pick = lambda st, kd, ho: next(x for x in lo if x["statistic"] == st and x["kinds"] == kd and x["held_out"] == ho)  # noqa: E731
    br, bt, bf = pick("Born", "gap/mid", "design"), pick("Born", "threshold", "design"), pick("Born", "gap/mid", "family")
    rf = max((x for x in lo if x["statistic"].startswith("raw") and x["held_out"] == "family"), key=lambda x: (x["exact"], -x["false_alarms"]))
    L += ["## 4. Rank rules scored out of sample", "",
          "For each held-out design (or family), the free choices are selected on everything else **except Test_B**, which "
          "is never in any selection. The choices are the rule (largest gap or above-midpoint) and the gate on the top "
          "value (0 to 20 in steps of 0.25). Selection maximises exact sets, then fewer false alarms, then more hits; ties "
          "go to the first rule listed and the middle of the tied gate interval. The rule is then applied to the "
          "held-out rows (both references). Families: a stage's pass-5/pass-6 twins, both rotated nulls, and both "
          "healthy cross-references are each held out together. Threshold-only rules and the raw delay are scored the "
          "same way as comparators.", "",
          _t(lo, ["held_out", "statistic", "kinds", "hits", "misses", "false_alarms", "exact", "n", "exact_without_TestB",
                  "false_without_TestB", "TestB_read"]), "",
          "Rules chosen per held-out family, Born rank rules:", "",
          _t(res["loo_chosen"]["Born | gap/mid | family"], ["held_out", "rule", "gate", "train_exact", "train_false"], {"gate": ".2f"}), "",
          f"**Result.** Born rank rule, leave-one-design-out: {br['hits']} hits, {br['false_alarms']} false alarms, "
          f"{br['exact']}/{br['n']} exact ({br['exact_without_TestB']} without Test_B). Leave-one-family-out: {bf['hits']} / "
          f"{bf['false_alarms']} / {bf['exact']}/{bf['n']} ({bf['exact_without_TestB']} without Test_B). Test_B, never "
          f"selected on, is read as {bf['TestB_read']}. LOO-calibrated Born threshold: {bt['hits']} / {bt['false_alarms']} / "
          f"{bt['exact']}/{bt['n']}. Best raw-delay rule, leave-one-family-out: {rf['statistic']} {rf['kinds']} "
          f"{rf['hits']} / {rf['false_alarms']} / {rf['exact']}/{rf['n']}.",
          "Caveat: there are 10 families, all from one head, mesh family and material table. 'Out of sample' here means "
          "out-of-design, not out-of-head.", ""]
    T.append(("4 rank rules out of sample", "CHANGED (scored out of sample)", f"in-sample 58/0/20 → leave-one-design-out "
              f"{br['hits']}/{br['false_alarms']}/{br['exact']}, leave-one-family-out {bf['hits']}/{bf['false_alarms']}/{bf['exact']}; "
              f"Test_B (never selected on): {bf['TestB_read']}", "lobe_round4.json: loo"))
    L += ["## Final table", "", _t([dict(item=a, verdict=b, change=c, evidence=d) for a, b, c, d in T],
                                   ["item", "verdict", "change", "evidence"]), ""]
    (OUT / "lobe_round4.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    sec = ["## 13. Round 4 (POST-HOC): fit rejection, fair Born-vs-raw, out-of-sample rank rules", "",
           "Full text: `results/imaging/lobe_round4.md`.", "",
           _t([dict(item=a, verdict=b, change=c) for a, b, c, d in T], ["item", "verdict", "change"]), ""]
    if "## 13." in rep:
        i0 = rep.index("## 13.")
        j = rep.find("\n## ", i0 + 5)
        rep = rep[:i0] + "\n".join(sec) + ("\n" + rep[j + 1:] if j >= 0 else "\n")
    else:
        rep = rep.rstrip("\n") + "\n\n" + "\n".join(sec) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")


if __name__ == "__main__":
    main()
