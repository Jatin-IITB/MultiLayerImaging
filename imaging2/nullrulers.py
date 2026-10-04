"""Rotated-null rulers (POST HOC; pre-registration in results/imaging2/ROTATED_NULLS_PROTOCOL.md).

Committed BEFORE Null_rot31 / Null_rot43 exist; run unchanged when they arrive:
    python -m imaging2.nullrulers all          # -> results/imaging2/nullrulers/report.md, report.json
    python -m imaging2.nullrulers commonmode   # section 0 only (no inversions)
Every rotated null whose file exists in data/raw is used; none is dropped (protocol rule 1). Every ruler is reported
three ways: all nulls; all nulls without rot19; rot19 alone (rule 2).
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool

import numpy as np

from . import posthoc as PH
from .data import CACHE, MIRROR, N, OUT, PATH_TYPE, RAW, SECTOR_SHORT, apply_group, freq, git_rev, paths_of

ROTATED = ["rot07", "rot19", "rot31", "rot43"]
for _k in ROTATED:
    PH.FILES.setdefault(_k, f"new_with_slices_Null_{_k}.s6p")
OUT_NR = OUT / "nullrulers"
BANDS = {"3.30-3.65 GHz": (3.30e9, 3.65e9), "3.2-4.2 GHz": (3.2e9, 4.2e9)}
CLASS = {1: "neighbour (k=1)", 2: "second-neighbour (k=2)", 3: "opposite (k=3)", 0: "reflection (k=0)"}
CM_COMMON, CM_SCATTER = 0.8, 0.5        # common-mode fraction thresholds (fixed here, descriptive)
NEGLIGIBLE_DB, NEGLIGIBLE_DEG = 0.05, 0.5


def available():
    return [k for k in ROTATED if (RAW / PH.FILES[k]).exists()]


def three_ways(nulls):
    """The three null sets of rule 2 for a dict name -> value-providing key."""
    rot = [k for k in nulls if k in ROTATED]
    out = {"all nulls": list(nulls), "all without rot19": [k for k in nulls if k != "rot19"]}
    out["rot19 alone"] = ["rot19"] if "rot19" in nulls else []
    return out, rot


# ---------------------------------------------------------------- section 0: common-mode vs scattered
def _pair_paths(a, b, mirror_b=False):
    pa = paths_of(PH.S(a))
    pb = paths_of(PH.S(b))
    if mirror_b:
        pb = apply_group(pb, MIRROR)
    return pa, pb


def commonmode():
    f = freq()
    rot = available()
    pairs = [(f"{r} vs H6", r, "H6", False) for r in rot]
    pairs += [(f"{a} vs {b}", a, b, False) for i, a in enumerate(rot) for b in rot[i + 1:]]
    pairs += [("Mild 5 vs 6", "Mild5", "Mild6", False), ("Moderate 5 vs 6", "Mod5", "Mod6", False),
              ("Severe 5 vs 6", "Sev5", "Sev6", False), ("Healthy 6 vs 7 (H6 vs H7)", "H6", "H7", False),
              ("RightOnly 5 vs mirror(LeftOnly) 6", "RightOnly", "LeftOnly", True)]
    out = {}
    for name, a, b, mb in pairs:
        pa, pb = _pair_paths(a, b, mb)
        out[name] = {}
        for bn, (lo, hi) in BANDS.items():
            sel = (f >= lo - 1) & (f <= hi + 1)
            dP = 10 * np.log10(np.mean(np.abs(pa[:, sel]) ** 2, 1) / np.mean(np.abs(pb[:, sel]) ** 2, 1))
            dPh = np.degrees(np.angle(np.mean(pa[:, sel] / pb[:, sel], 1)))
            dM = np.mean(20 * np.log10(np.abs(pa[:, sel]) / np.abs(pb[:, sel])), 1)    # mean over f of the dB difference
            out[name][bn] = {}
            for k in (1, 2, 3, 0):
                idx = np.flatnonzero(PATH_TYPE == k)
                row = {}
                for q, x, neg in (("power_dB", dP[idx], NEGLIGIBLE_DB), ("mean_of_dB", dM[idx], NEGLIGIBLE_DB),
                                  ("phase_deg", dPh[idx], NEGLIGIBLE_DEG)):
                    m, sd = float(x.mean()), float(x.std())
                    cm = m * m / (m * m + sd * sd) if (m * m + sd * sd) > 0 else 0.0
                    cls = ("negligible" if max(abs(x.max()), abs(x.min())) < neg else
                           "common-mode" if cm >= CM_COMMON else "scattered" if cm < CM_SCATTER else "mixed")
                    row[q] = dict(per_path={f"T{PH_path(p)}": float(v) for p, v in zip(idx, x)}, mean=m, sd=sd,
                                  min=float(x.min()), max=float(x.max()), cm_fraction=cm, classification=cls)
                out[name][bn][CLASS[k]] = row
    return out


def PH_path(p):
    from .data import PATHS
    i, j = PATHS[p]
    return f"{i + 1}-T{j + 1}" if i != j else f"{i + 1} refl"


# ---------------------------------------------------------------- stage and lobe calls vs every reference
TARGETS = [("Healthy_p7", "Healthy", "H7"), ("Mild_p5", "Mild_lobe", "Mild5"), ("Mild_p6", "Mild_lobe", "Mild6"),
           ("Moderate_p5", "Moderate_lobe", "Mod5"), ("Moderate_p6", "Moderate_lobe", "Mod6"),
           ("Severe_p5", "Severe_lobe", "Sev5"), ("Severe_p6", "Severe_lobe", "Sev6"),
           ("LeftOnly_p6", "LeftOnly", "LeftOnly"), ("MCI_p6", "MCI_lobe", "MCI"),
           ("RightOnly", "LeftOnly", "RightOnly"), ("Test_B", "__blind__", "Test_B")]
VARIANTS = ["standard", "gainfree", "ringphase"]


def truth_calls_stage(key):
    from .data import DESIGNS
    PH.register()
    fn = PH.FILES[key]
    if key in ROTATED or key == "H7":
        return [0] * N, "Healthy"
    d = next(x for x in DESIGNS if x.file == fn)
    t = d.truth
    return t.affected.astype(int).tolist(), (t.tissue_stage if t.affected.any() else "Healthy")


def _stage_job(args):
    tag, fold_name, key, refs = args
    from . import lodo as LO
    PH.register()
    fold = LO.fit_fold(fold_name)
    rows = []
    for ref in refs:
        if ref == key:
            continue
        Ld = PH.L(key, ref)
        for var in VARIANTS:
            sm = PH.short(PH.summarize_run(PH.posterior(fold, variant=var), Ld))
            rows.append(dict(target=tag, reference=ref, variant=var, stage=sm["stage"], P_stage=sm["P_stage"],
                             calls=sm["calls"], fit=sm["fit"], e_med=sm["e_med"]))
    return rows


def stage_table(procs=6):
    refs = ["H6", "H7"] + available()
    jobs = [(t, g, k, refs) for t, g, k in TARGETS]
    jobs += [(r, "__blind__", r, refs) for r in available()]          # the rotated nulls themselves as targets
    with Pool(procs) as pool:
        rows = sum(pool.map(_stage_job, jobs), [])
    for r in rows:
        key = next((k for t, _, k in TARGETS if t == r["target"]), r["target"])
        tc, ts = truth_calls_stage(key)
        r["true_calls"], r["true_stage"] = tc, ts
        r["wrong_lobes"] = int(sum(int(a != b) for a, b in zip(r["calls"], tc)))
        r["stage_ok"] = r["stage"] == ts
    return rows


# ---------------------------------------------------------------- rulers, three ways (rule 2)
def _ring(Ld):
    from .figures import detuning_values
    return -detuning_values(Ld, freq())


def rulers(stage_rows):
    """R1c-type floors over the nulls, three ways; readings and bars as listed in the protocol."""
    rot = available()
    old_null_obs = {"H7 vs H6": ("H7", "H6"), "H6 vs H7": ("H6", "H7"), "MCI vs H6": ("MCI", "H6"),
                    "Mild5 vs H6": ("Mild5", "H6"), "Mild6 vs H7": ("Mild6", "H7"), "Mod5 vs H6": ("Mod5", "H6"),
                    "Mod6 vs H7": ("Mod6", "H7"), "Sev5 vs H6": ("Sev5", "H6"), "Sev6 vs H7": ("Sev6", "H7")}
    rot_obs = {r: (r, "H6") for r in rot}
    ring = {k: _ring(PH.L(*v)) for k, v in {**old_null_obs, **rot_obs}.items()}
    tests = {"LeftOnly vs H6": _ring(PH.L("LeftOnly", "H6")), "RightOnly vs H6": _ring(PH.L("RightOnly", "H6")),
             "Test_B vs H6": _ring(PH.L("Test_B", "H6")), "Mod5 vs H6": ring["Mod5 vs H6"], "Mod6 vs H7": ring["Mod6 vs H7"]}

    def lr(r):
        return float(np.mean(r[[1, 2]]) - np.mean(r[[4, 5]]))

    def fb(r):
        return float(r[0] - r[3])

    def spread(r):
        return float(r.max() - r.min())

    def diag(r):
        return max(float(np.mean(r[[a, a + 3]]) - np.mean(np.delete(r, [a, a + 3]))) for a in range(3))

    def t2t5(r):
        return float(np.mean(r[[1, 4]]) - np.mean(r[[0, 2, 3, 5]]))

    healthy_old = ["H7 vs H6", "H6 vs H7", "MCI vs H6"]
    sym_old = list(old_null_obs)
    fb_old = healthy_old + ["Mild5 vs H6", "Mild6 vs H7"]
    defs = [("R4 ring left-right contrast", lr, sym_old, ["LeftOnly vs H6", "RightOnly vs H6"]),
            ("R5 ring front-back contrast", fb, fb_old, ["Mod5 vs H6", "Mod6 vs H7"]),
            ("R6 ring spread", spread, healthy_old, ["Test_B vs H6"]),
            ("R7 ring diagonal-pair elevation (post hoc statistic)", diag, healthy_old, ["Test_B vs H6"]),
            ("R8 ring T2,T5 elevation (post hoc pair)", t2t5, healthy_old, ["Test_B vs H6"])]
    out = {}
    for name, fn, olds, tnames in defs:
        nulls = {k: fn(ring[k]) for k in olds}
        nulls.update({k: fn(ring[k]) for k in rot})
        sets, _ = three_ways(nulls)
        res = dict(null_values=nulls, ways={})
        for wname, members in sets.items():
            if not members:
                res["ways"][wname] = None
                continue
            floor = max(abs(nulls[m]) for m in members)
            res["ways"][wname] = dict(floor=floor, members=members,
                                      tests={t: dict(value=fn(tests[t]), ratio=abs(fn(tests[t])) / floor if floor > 0 else None,
                                                     bar=_bar(abs(fn(tests[t])) / floor) if floor > 0 else "n/a")
                                             for t in tnames})
        out[name] = res
    # R3: LR_e of the reconstructions (primary variant vs H6); nulls = old nine + rotated nulls reconstructed vs H6
    post = json.loads((OUT / "posteriors.json").read_text())["targets"]
    ro = json.loads((OUT / "rightonly" / "rightonly.json").read_text(encoding="utf-8"))["runs"]
    tb = json.loads((OUT / "blind" / "Test_B" / "report.json").read_text(encoding="utf-8"))["variants"]

    def lre(e):
        return float(np.mean(e[1:3]) - np.mean(e[4:6]))
    nulls = {t: lre([s["e_median"] for s in post[t]["sectors"]]) for t in
             ["Healthy_p7", "MCI_p6", "Mild_p5", "Mild_p6", "Moderate_p5", "Moderate_p6", "Severe_p5", "Severe_p6"]}
    nulls["Healthy_p6_vsH7"] = lre([s["e_median"] for s in ro["Healthy_p6_vsH7"]["sectors"]])
    for r in stage_rows:
        if r["target"] in rot and r["reference"] == "H6" and r["variant"] == "standard":
            nulls[r["target"]] = lre(r["e_med"])
    tv = {"LeftOnly_p6": lre([s["e_median"] for s in post["LeftOnly_p6"]["sectors"]]),
          "RightOnly": lre([s["e_median"] for s in ro["RightOnly_p6"]["sectors"]]),
          "Test_B": lre([s["e_median"] for s in tb["standard_H6"]["sectors"]])}
    sets, _ = three_ways(nulls)
    res = dict(null_values=nulls, ways={})
    for wname, members in sets.items():
        if not members:
            res["ways"][wname] = None
            continue
        floor = max(abs(nulls[m]) for m in members)
        res["ways"][wname] = dict(floor=floor, members=members, tests={
            t: dict(value=v, ratio=(abs(v) / floor if floor > 0 else None),
                    bar=(_bar(abs(v) / floor) if floor > 0 else "floor 0: not applicable")) for t, v in tv.items()})
    out["R3 LR_e (e left - right), reconstruction"] = res
    return out


def _bar(x):
    return "established (>= 3x)" if x >= 3 else "sensitive (2-3x)" if x >= 2 else "not separable (< 2x)"


def readings_from_table(rows):
    """R1, R2, R9, R10 evaluated on the stage table, per rotated null and three ways."""
    rot = available()
    out = {}
    # R1: rotated nulls as targets: no lobe called in any run against H6/H7, both standard and gain-removing
    out["R1 rotated nulls empty"] = {r: [dict(reference=x["reference"], variant=x["variant"], lobes=sum(x["calls"]),
                                               stage=x["stage"]) for x in rows if x["target"] == r] for r in rot}
    # R2: one-sided call patterns among nulls (target null, primary variant vs H6)
    def onesided(c):
        return bool((c[1] or c[2]) != (c[4] or c[5]))
    out["R2 one-sided calls among rotated nulls"] = {r: any(onesided(x["calls"]) for x in rows if x["target"] == r) for r in rot}
    # R9 / R10: lobe calls and stage of Test_B, LeftOnly, RightOnly with each rotated null as reference
    out["R9-R10 null as reference"] = [dict(target=x["target"], reference=x["reference"], variant=x["variant"],
                                            calls_exact=(x["wrong_lobes"] == 0), stage=x["stage"], stage_ok=x["stage_ok"])
                                       for x in rows if x["target"] in ("Test_B", "LeftOnly_p6", "RightOnly")
                                       and x["reference"] in rot]
    return out


def coverage_three_ways():
    """R11: empirical 90% coverage of e (11 targets, primary variant) with the twin samples of the augmented noise
    model built from: non-null twins + {all rotated nulls | all but rot19 | rot19 only}."""
    from . import lodo as LO
    from .data import DESIGNS
    PH.register()
    rot = available()
    base = {"H7/H6 (7 vs 6 passes)": PH.L("H7", "H6"), "Mild 5/6": PH.L("Mild5", "Mild6"),
            "Moderate 5/6": PH.L("Mod5", "Mod6"), "Severe 5/6": PH.L("Sev5", "Sev6"),
            "RightOnly/mirror(LeftOnly) (5 vs 6)": PH.L_mirror("RightOnly", "LeftOnly")}
    rots = {f"{r}/H6": PH.L(r, "H6") for r in rot}
    ways = {"all nulls": list(rots), "all without rot19": [k for k in rots if not k.startswith("rot19")],
            "rot19 alone": [k for k in rots if k.startswith("rot19")]}
    folds = {}
    res = {}
    targets = [(t, g, k) for t, g, k in TARGETS]
    for wname, keys in ways.items():
        if not keys:
            res[wname] = None
            continue
        samples = {**base, **{k: rots[k] for k in keys}}
        rows = []
        for tag, g, key in targets:
            if g not in folds:
                folds[g] = LO.fit_fold(g)
            fold = folds[g]
            excl = PH.EXCLUDE.get(tag, [])
            smp = [v for k, v in samples.items() if k not in excl]
            F = smp[0].shape[1]
            vr, vi = np.zeros((4, F)), np.zeros((4, F))
            for t in range(4):
                sel = PATH_TYPE == t
                vr[t] = np.mean([np.mean(x[sel].real ** 2, 0) for x in smp], 0)
                vi[t] = np.mean([np.mean(x[sel].imag ** 2, 0) for x in smp], 0)
            from .noise import smooth
            s_re = np.sqrt(fold["s_re"] ** 2 + smooth(vr)[PATH_TYPE])
            s_im = np.sqrt(fold["s_im"] ** 2 + smooth(vi)[PATH_TYPE])
            ref = "H6" if key not in ("Mild6", "Mod6", "Sev6") else "H7"
            sm = PH.summarize_run(PH.posterior(fold, s_re, s_im), PH.L(key, ref))
            tc, _ = truth_calls_stage(key)
            e_true = (next(d for d in DESIGNS if d.file == PH.FILES[key]).truth.e if key not in ("H7",) else np.zeros(N))
            rows += PH._cov_rows(tag, sm["sectors"], e_true)
        res[wname] = PH._coverage(rows)
    return res


# ---------------------------------------------------------------- driver and report
def all_():
    OUT_NR.mkdir(parents=True, exist_ok=True)
    out = dict(code=git_rev(), label="POST HOC; pre-registered in ROTATED_NULLS_PROTOCOL.md",
               rotated_nulls_present=available())
    out["commonmode"] = commonmode()
    rows = stage_table()
    out["stage_table"] = rows
    out["readings"] = readings_from_table(rows)
    out["rulers"] = rulers(rows)
    out["coverage_R11"] = coverage_three_ways()
    out["variant_counts"] = variant_counts(rows)
    (OUT_NR / "report.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT_NR / "report.md").write_text(report(out), encoding="utf-8")
    return out


def variant_counts(rows):
    out = {}
    for v in VARIANTS:
        rs = [r for r in rows if r["variant"] == v]
        out[v] = dict(runs=len(rs), wrong_lobe_calls=int(sum(r["wrong_lobes"] for r in rs)),
                      runs_with_any_wrong_lobe=int(sum(r["wrong_lobes"] > 0 for r in rs)),
                      wrong_stage=int(sum(not r["stage_ok"] for r in rs)),
                      by_reference={ref: dict(wrong_lobe_calls=int(sum(r["wrong_lobes"] for r in rs if r["reference"] == ref)),
                                              wrong_stage=int(sum(not r["stage_ok"] for r in rs if r["reference"] == ref)),
                                              runs=int(sum(r["reference"] == ref for r in rs)))
                                    for ref in sorted({r["reference"] for r in rs})})
    return out


def _calls(c):
    return ", ".join(SECTOR_SHORT[k].split()[0] for k in range(N) if c[k]) or "none"


def report(o):
    L = ["# Rotated-null rulers (POST HOC; protocol `ROTATED_NULLS_PROTOCOL.md`)", "",
         f"Code {o['code']}. Rotated nulls present: {', '.join(o['rotated_nulls_present'])}.", "",
         "## 0. Common-mode vs scattered differences per path class", "",
         f"Per path: band-power difference (dB) and band-mean phase difference (°) between the two files. Per class: mean, "
         f"SD and range over its 6 paths; common-mode fraction cm = mean² / (mean² + SD²). Classification (fixed in the "
         f"protocol): common-mode if cm ≥ {CM_COMMON}, scattered if cm < {CM_SCATTER}, mixed otherwise, negligible if every "
         f"path is within ±{NEGLIGIBLE_DB} dB (±{NEGLIGIBLE_DEG}°).", ""]
    for bn in BANDS:
        L += [f"### {bn}", "",
              "| pair | class | band power: mean ± SD [min, max] dB | cm | class. | mean of dB: mean ± SD [min, max] | cm | class. "
              "| phase: mean ± SD [min, max] ° | cm | class. |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for pair, v in o["commonmode"].items():
            for cls in ("neighbour (k=1)", "second-neighbour (k=2)", "opposite (k=3)"):
                cells = []
                for q in ("power_dB", "mean_of_dB", "phase_deg"):
                    p = v[bn][cls][q]
                    cells.append(f"{p['mean']:+.2f} ± {p['sd']:.2f} [{p['min']:+.2f}, {p['max']:+.2f}] | {p['cm_fraction']:.2f} | "
                                 f"{p['classification']}")
                L.append(f"| {pair} | {cls} | " + " | ".join(cells) + " |")
        L.append("")
    for q in ("power_dB", "mean_of_dB"):
        L += [f"Per-path values, second-neighbour class, 3.30–3.65 GHz ({q}):", ""]
        for pair, v in o["commonmode"].items():
            L.append(f"- {pair}: " + ", ".join(f"T{k} {x:+.2f}" for k, x in
                                               v["3.30-3.65 GHz"]["second-neighbour (k=2)"][q]["per_path"].items()))
        L.append("")
    L += ["## 1. Stage and lobe calls for every target, reference and variant", "",
          "| target | reference | variant | stage (P) | stage ok | lobes called | wrong lobes | fit |", "|---|---|---|---|---|---|---|---|"]
    for r in o["stage_table"]:
        L.append(f"| {r['target']} | {r['reference']} | {r['variant']} | {r['stage']} ({r['P_stage']:.2f}) | "
                 f"{'yes' if r['stage_ok'] else '**no**'} | {_calls(r['calls'])} | {r['wrong_lobes']} | {r['fit']:.2f} |")
    L += ["", "## 2. Per variant: wrong lobe calls and wrong stages over all targets × references", "",
          "| variant | runs | wrong lobe calls | runs with ≥ 1 wrong lobe | wrong stage | by reference (wrong lobes / wrong stage / runs) |",
          "|---|---|---|---|---|---|"]
    for v, c in o["variant_counts"].items():
        L.append(f"| {v} | {c['runs']} | {c['wrong_lobe_calls']} | {c['runs_with_any_wrong_lobe']} | {c['wrong_stage']} | "
                 + "; ".join(f"{k}: {x['wrong_lobe_calls']}/{x['wrong_stage']}/{x['runs']}" for k, x in c["by_reference"].items()) + " |")
    L += ["", "## 3. Rulers, three ways (rule 2)", ""]
    for name, res in o["rulers"].items():
        L.append(f"**{name}**: null values " + ", ".join(f"{k} {v:+.2f}" for k, v in res["null_values"].items()))
        L.append("")
        L.append("| way | floor | reading | value | / floor | bar |")
        L.append("|---|---|---|---|---|---|")
        for w, wv in res["ways"].items():
            if wv is None:
                L.append(f"| {w} | – | – | – | – | – |")
                continue
            for t, tv in wv["tests"].items():
                rr = f"{tv['ratio']:.2f}" if tv["ratio"] is not None else "–"
                L.append(f"| {w} | {wv['floor']:.2f} | {t} | {tv['value']:+.2f} | {rr} | {tv['bar']} |")
        L.append("")
    rd = o["readings"]
    L += ["## 4. Readings R1, R2, R9, R10", "", "R1 (rotated nulls as targets; lobes called per run):", ""]
    for r, runs in rd["R1 rotated nulls empty"].items():
        L.append(f"- {r}: " + "; ".join(f"vs {x['reference']} {x['variant']}: {x['lobes']} lobes, {x['stage']}" for x in runs))
    L += ["", f"R2 (one-sided call pattern in a rotated null): {rd['R2 one-sided calls among rotated nulls']}", "",
          "R9/R10 (rotated null as reference): exact calls / stage correct:", ""]
    for x in rd["R9-R10 null as reference"]:
        L.append(f"- {x['target']} vs {x['reference']} {x['variant']}: calls {'exact' if x['calls_exact'] else 'WRONG'}, "
                 f"stage {x['stage']} ({'ok' if x['stage_ok'] else 'wrong'})")
    L += ["", "## 5. R11 coverage of e (90% intervals, augmented noise), three ways", "",
          "| way | sectors | coverage all | affected | coverage affected | calls correct |", "|---|---|---|---|---|---|"]
    for w, c in o["coverage_R11"].items():
        if c is None:
            L.append(f"| {w} | – | – | – | – | – |")
        else:
            L.append(f"| {w} | {c['n']} | {c['coverage_all']:.0%} | {c['n_affected']} | {c['coverage_affected']:.0%} | {c['calls_correct']:.0%} |")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["all", "commonmode"])
    a = ap.parse_args()
    if a.cmd == "all":
        all_()
    else:
        OUT_NR.mkdir(parents=True, exist_ok=True)
        print(json.dumps(commonmode(), indent=1)[:200])
