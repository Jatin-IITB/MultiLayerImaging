"""Round 3 (POST-HOC throughout): rotated nulls, Test_B truth, rank readings, raw-delay ranking, pass gap.

    python imaging/lobe_round3.py [--n 100]

Everything here was computed after the Test_B truth and the rotated nulls were released. Frozen rules,
thresholds, protocols, predictions and submitted estimates are unchanged; committed verdicts stand as scored.
Writes results/imaging/lobe_round3.{md,json}, refreshes the set files (lobe_sets.csv, lobe_qc_c3.csv,
lobe_mask_log.csv) and section 12 of lobe_report.md.
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
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_round2 as R2  # noqa: E402
from imaging import lobe_rulers as LR  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import score_testb as TB  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, ROOT, git_hash  # noqa: E402
from imaging.report_lobe import SHORT, _t  # noqa: E402

H7, H6 = "Healthy_sliced", "Healthy_sliced_new"
REFS = {"H7": H7, "H6": H6}
ROT = ("Null_rot07", "Null_rot19")
NULL9 = tuple(C3.SYMMETRIC)
NULL11 = NULL9 + ROT
PRIMARY = RL.METHODS[0]
METH = (RL.METHODS[0], RL.METHODS[2], LR.WNAME)
SH = LR.SHORTM
MP = SL.mirror_perm()
# truth (released): affected sectors (indices) and the design name used for the true sector map
SL.DESIGNS.setdefault("RightOnly_test", ((0, 0, 0, 0, 11.5, 7.5), 17.5, "Mild"))
SL.DESIGNS.setdefault("Test_B", ((0, 11.5, 0, 0, 7.5, 0), 17.5, "Mild"))
TRUTH = {"Mild_lobe": "Mild_lobe", "Mild_lobe_new": "Mild_lobe", "Moderate_lobe": "Moderate_lobe",
         "Moderate_lobe_c3": "Moderate_lobe", "Severe_lobe": "Severe_lobe", "Severe_lobe_c3": "Severe_lobe",
         "LeftOnly_test_c3": "LeftOnly_test", "RightOnly_test": "RightOnly_test", "Test_B": "Test_B",
         "MCI_lobe_c3": "MCI_lobe", "Null_rot07": "Healthy_sliced", "Null_rot19": "Healthy_sliced",
         "Healthy_sliced": "Healthy_sliced", "Healthy_sliced_new": "Healthy_sliced"}
TRUTH.update({r: "Healthy_sliced" for r in ROT})          # every rotated null (add new ones to ROT and REGISTRY only)


def mir(S):
    return S[..., MP[:, None], MP[None, :]]


def affected(design):
    return {k for k, e in enumerate(SL.DESIGNS[TRUTH[design]][0]) if e > 0}


def designs_vs(ref):
    return [d for d in TRUTH if d != ref]


# ----------------------------------------------------------------------------------------------- 1
def nulls_as_targets(ctx, n):
    rows, reads = [], []
    for st in ROT:
        out = TB.run(ctx, st, ctx.S[st], n)
        rd = TB.reading(out, ctx.fz["rules"])
        for r in out["rows"]:
            rows.append(dict(null=st, **{k: r[k] for k in ("reference", "method")}, **{s: r[s] for s in SHORT},
                             LR=r["LR"], LR_ratio=r["LR_ratio"], FB=r["FB"], FB_ratio=r["FB_ratio"], called=r["called"],
                             side=r["side"], frontback=r["frontback"], residual=r["residual"]))
        stmt = rd.get("statement")
        stmt = stmt.replace("does not explain Test_B", f"does not explain {st}") if stmt else stmt   # reused protocol text
        reads.append(dict(null=st, statement=stmt, affected=rd["affected"], possible=rd["possible"],
                          side=rd["side"], frontback=rd["frontback"],
                          anti=[(a["reference"][:2], a["method"], a["LR_anti"], a["ratio"]) for a in out["anti"]],
                          data_size=rd.get("data_size")))
    return rows, reads


# ----------------------------------------------------------------------------------------------- LR_anti nulls
def anti_section(ctx):
    rows, per = [], []
    for rlab, ref in REFS.items():
        for m in METH:
            T = R2.anti_lr(ctx, m, ref)
            v = {d: float(T(ctx.S[d])) for d in NULL11 + ("LeftOnly_test_c3", "RightOnly_test", "Test_B")}
            yard = max(abs(T(ctx.S[a]) - T(ctx.S[b])) for a, b in C3.ONE_PASS.values())
            n9 = np.array([v[d] for d in NULL9])
            n11 = np.array([v[d] for d in NULL11])
            for d, x in v.items():
                per.append(dict(reference=rlab, method=SH[m], design=d, LR_anti=x))
            r9, r11 = max(yard, np.abs(n9).max()), max(yard, np.abs(n11).max())
            row = dict(reference=rlab, method=SH[m], yardstick=float(yard), null9_max=float(np.abs(n9).max()),
                       null9_rms=float(np.sqrt(np.mean(n9 ** 2))), rot07=v["Null_rot07"], rot19=v["Null_rot19"],
                       null11_max=float(np.abs(n11).max()), null11_rms=float(np.sqrt(np.mean(n11 ** 2))))
            for d in ("LeftOnly_test_c3", "RightOnly_test", "Test_B"):
                x = abs(v[d])
                row[f"{d.split('_')[0]} ratio (9)"] = x / r9
                row[f"{d.split('_')[0]} ratio (11)"] = x / r11
                row[f"{d.split('_')[0]} rank p (11)"] = float((1 + np.sum(np.abs(n11) >= x)) / 12)
            row["both mirror designs beyond all 11"] = bool(abs(v["LeftOnly_test_c3"]) > np.abs(n11).max()
                                                           and abs(v["RightOnly_test"]) > np.abs(n11).max())
            row["rotated nulls within old 9-null envelope"] = bool(max(abs(v["Null_rot07"]), abs(v["Null_rot19"]))
                                                                  <= np.abs(n9).max())
            rows.append(row)
    return rows, per


# ----------------------------------------------------------------------------------------------- cross-ratio phases
def cr_section(ctx):
    keep18, _, _ = R2.independent_cr(ctx)
    band = np.flatnonzero((ctx.f >= 3.2e9 - 1) & (ctx.f <= 4.2e9 + 1))
    out = []
    for vname, fsel in (("band mean 3.2-4.2 GHz", band), ("3.4 GHz", ctx.fi[:1]),
                        ("band mean 3.30-3.65 GHz", np.flatnonzero((ctx.f >= 3.3e9 - 1) & (ctx.f <= 3.65e9 + 1)))):
        def st(X):
            return R2.phase_cr_stats(X, fsel)[0][keep18]
        vals = {d: st(ctx.S[d]) for d in NULL11 + ("LeftOnly_test_c3", "RightOnly_test", "Test_B")}
        yard = np.max([np.abs(st(ctx.S[a]) - st(ctx.S[b])) for a, b in C3.ONE_PASS.values()], 0)
        for nset, names in (("9 nulls", NULL9), ("11 nulls", NULL11)):
            N = np.array([vals[d] for d in names])
            rms, mx = np.sqrt(np.mean(N ** 2, 0)), np.abs(N).max(0)
            row = dict(view=vname, nulls=nset)
            for d in ("LeftOnly_test_c3", "RightOnly_test", "Test_B"):
                x = np.abs(vals[d])
                row[f"{d.split('_')[0]} ≥3× rms"] = int(np.sum(x >= 3 * np.maximum(yard, rms)))
                row[f"{d.split('_')[0]} ≥3× max"] = int(np.sum(x >= 3 * np.maximum(yard, mx)))
            loo = []
            for k, d in enumerate(names):
                oth = np.delete(N, k, 0)
                loo.append(int(np.sum(np.abs(N[k]) >= 3 * np.maximum(yard, np.sqrt(np.mean(oth ** 2, 0))))))
            row["null files ≥3× rms (leave-one-out), max over files"] = int(max(loo))
            row["per null file"] = ", ".join(f"{d.replace('Healthy_sliced', 'H').replace('_lobe', '')} {c}" for d, c in zip(names, loo))
            out.append(row)
    return out


# ----------------------------------------------------------------------------------------------- 0.3(b) checks
def pair_checks(ctx):
    band = (ctx.f >= 3.2e9 - 1) & (ctx.f <= 4.2e9 + 1)
    k34 = ctx.fi[0]
    rows = []
    designs = ("Healthy_sliced_new", "Healthy_sliced", "Null_rot07", "Null_rot19", "LeftOnly_test_c3", "Test_B")
    for i in [i for i in range(len(SL.PAIRS)) if R2.PM[i] > i]:
        j = R2.PM[i]
        row = dict(pair=f"{R2.RV.plabel(*SL.PAIRS[i])} vs {R2.RV.plabel(*SL.PAIRS[j])}",
                   type=["reflection", "neighbour", "second-neighbour", "opposite"][SL.ring_k(*SL.PAIRS[i])])
        for d in designs:
            S = SL.recip(ctx.S[d])
            bp = 10 * np.log10(np.mean(np.abs(S[i, band]) ** 2) / np.mean(np.abs(S[j, band]) ** 2))
            row[f"power {d} dB"] = float(bp)
            row[f"phase@3.4 {d} deg"] = float(np.degrees(np.angle(S[i, k34] / S[j, k34])))
        row["power max |old 9 nulls| dB"] = float(max(abs(10 * np.log10(np.mean(np.abs(SL.recip(ctx.S[d])[i, band]) ** 2)
                                                                        / np.mean(np.abs(SL.recip(ctx.S[d])[j, band]) ** 2)))
                                                        for d in NULL9))
        row["phase@3.4 max |old 9 nulls| deg"] = float(max(abs(np.degrees(np.angle(SL.recip(ctx.S[d])[i, k34]
                                                                                   / SL.recip(ctx.S[d])[j, k34])))
                                                            for d in NULL9))
        rows.append(row)
    ring = []
    for d in ("Null_rot07", "Null_rot19", "Healthy_sliced", "LeftOnly_test_c3", "RightOnly_test", "Test_B", "MCI_lobe_c3"):
        for vname, sel in (("band 3.2-4.2", np.flatnonzero(band)), ("fit 3.4/3.6/3.8", ctx.fi)):
            pa = per_antenna_delay(ctx.S[d], ctx.S[H6], sel)
            ring.append(dict(design=d, view=vname, **{f"T{t + 1} delay deg": float(pa[t]) for t in range(6)},
                             ring_range=float(pa.max() - pa.min())))
    return rows, ring


def centred(v):
    """Remove the common mode (ring median): CSF_Mild everywhere delays every antenna equally."""
    return v - np.median(v)


def per_antenna_delay(X, R, sel):
    """Raw per-antenna delay: minus the mean phase change (deg) of the antenna's two neighbour paths over sel."""
    rho = SL.recip(X) / SL.recip(R)
    ph = np.degrees(np.angle(rho[:, sel])).mean(1)
    out = np.zeros(6)
    for t in range(6):
        a, b = SL.PAIRS.index(tuple(sorted((t, (t + 1) % 6)))), SL.PAIRS.index(tuple(sorted((t, (t - 1) % 6))))
        out[t] = -0.5 * (ph[a] + ph[b])
    return out


# ----------------------------------------------------------------------------------------------- rebuilt rulers
def ruler_rebuild(ctx):
    rows = []
    sect0 = ("Healthy_sliced", "Healthy_sliced_new", "MCI_lobe_c3")
    for rlab, ref in REFS.items():
        R = ctx.S[ref]
        fx = C3.make_x(ctx.model(ref), PRIMARY, ctx.lam)

        def q(X):
            return C3.qvec(fx(X[ctx.fi], R[ctx.fi]))
        yard = np.max([np.abs(q(R + sg * (ctx.S[a] - ctx.S[b]))) for a, b in C3.ONE_PASS.values() for sg in (1, -1)], 0)
        Q = {d: q(ctx.S[d]) for d in set(NULL11) | set(TB.FB_ZERO) | {"LeftOnly_test_c3", "RightOnly_test", "Test_B",
                                                                       "Moderate_lobe", "Moderate_lobe_c3", "Mild_lobe",
                                                                       "Severe_lobe", "Mild_lobe_new", "Severe_lobe_c3"}}
        for nset, extra in (("old", ()), ("with rotated nulls", ROT)):
            sec_fl = np.max([np.abs(Q[d][:6]) for d in sect0 + extra if d != ref], 0)
            lr_fl = max(abs(Q[d][6]) for d in NULL9 + extra if d != ref)
            fb_fl = max(abs(Q[d][7]) for d in tuple(TB.FB_ZERO) + extra if d != ref)
            rul = np.r_[np.maximum(yard[:6], sec_fl), max(yard[6], lr_fl), max(yard[7], fb_fl)]
            row = dict(reference=rlab, rulers=nset, **{f"ruler {s}": float(rul[k]) for k, s in enumerate(SHORT)},
                       ruler_LR=float(rul[6]), ruler_FB=float(rul[7]))
            for d, ks in (("Test_B", (1, 4)), ("RightOnly_test", (4, 5)), ("LeftOnly_test_c3", (1, 2))):
                for k in ks:
                    row[f"{d.split('_')[0]} {SHORT[k]} ratio"] = float(abs(Q[d][k]) / rul[k])
                row[f"{d.split('_')[0]} LR ratio"] = float(abs(Q[d][6]) / rul[6])
            row["rot07 max sector"] = float(Q["Null_rot07"][:6].max())
            row["rot19 max sector"] = float(Q["Null_rot19"][:6].max())
            rows.append(row)
    return rows


def b24_rebuild(ctx):
    rows = []
    for setn, ref, mild, mod, sev in (("lobe_A", H6, "Mild_lobe", "Moderate_lobe", "Severe_lobe"),
                                      ("lobe_B", H7, "Mild_lobe_new", "Moderate_lobe_c3", "Severe_lobe_c3")):
        for m in METH:
            fx = C3.make_x(ctx.model(ref), m, ctx.lam)
            R = ctx.S[ref][ctx.fi]
            fb = {d: RL.contrasts(fx(ctx.S[d][ctx.fi], R))["FB"] for d in (mild, mod, sev) + ROT}
            bias = 0.5 * (fb[mild] + fb[sev])
            bu = 0.5 * abs(fb[mild] - fb[sev])
            r = ctx.rulers(mod, ref, m)
            clean_old = max(r["yard"][7], r["floor"][7])
            clean_new = max(clean_old, abs(fb["Null_rot07"]), abs(fb["Null_rot19"]))
            corr = fb[mod] - bias
            rows.append(dict(set=setn, method=SH[m], FB_rot07=fb["Null_rot07"], FB_rot19=fb["Null_rot19"],
                             corrected=corr, ratio_old=abs(corr) / np.hypot(bu, clean_old),
                             ratio_new=abs(corr) / np.hypot(bu, clean_new)))
    return rows


# ----------------------------------------------------------------------------------------------- readings
def largest_gap_k(v, gate):
    s = np.sort(v)[::-1]
    if s[0] <= gate:
        return 0
    return int(np.argmax(s[:-1] - s[1:]) + 1)


def readings(ctx):
    T_abs, T_null = ctx.fz["rules"][PRIMARY]["T_abs"], ctx.fz["rules"][PRIMARY]["T_null"]
    rows = []
    raw_gate = {}
    zero = ("Healthy_sliced", "Healthy_sliced_new", "MCI_lobe_c3") + ROT       # no cortical change
    for rlab, ref in REFS.items():
        raw_gate[rlab] = max(centred(per_antenna_delay(ctx.S[d], ctx.S[ref], ctx.fi)).max() for d in zero if d != ref)
    for rlab, ref in REFS.items():
        fx = C3.make_x(ctx.model(ref), PRIMARY, ctx.lam)
        R = ctx.S[ref]
        for d in designs_vs(ref):
            v = fx(ctx.S[d][ctx.fi], R[ctx.fi])[6:12]
            raw = centred(per_antenna_delay(ctx.S[d], R, ctx.fi))
            tru = affected(d)
            tr_map = SL.truth_regions(TRUTH[d], ctx.fh, ctx.P, SL.region_masks())["sens"][7:13] if tru else np.zeros(6)
            row = dict(reference=rlab, design=d, truth=" ".join(SHORT[k].split()[0] for k in sorted(tru)) or "none")

            def score(sel, tag):
                sel = set(sel)
                row[f"{tag} set"] = " ".join(SHORT[k].split()[0] for k in sorted(sel)) or "none"
                row[f"{tag} hits"] = len(sel & tru)
                row[f"{tag} misses"] = len(tru - sel)
                row[f"{tag} false"] = len(sel - tru)
                row[f"{tag} exact"] = sel == tru
            score(np.flatnonzero(v > T_abs), "frozen T_abs")
            score(np.argsort(-v)[:largest_gap_k(v, T_null)], "rank (largest gap, gate T_null)")
            mid = 0.5 * (v.max() + v.min())
            score(np.flatnonzero(v > mid) if v.max() > T_null else [], "rank (above midpoint, gate T_null)")
            score(np.argsort(-raw)[:largest_gap_k(raw, raw_gate[rlab])], "raw delay (centred, largest gap, gate null max)")
            k = len(tru)
            if 0 < k < 6:
                row["Born top-k oracle"] = len(set(np.argsort(-v)[:k]) & tru) / k
                row["raw top-k oracle"] = len(set(np.argsort(-raw)[:k]) & tru) / k
            if tru and np.std(tr_map) > 0.5:
                row["Born spearman"] = float(spearmanr(v, tr_map).statistic)
                row["raw spearman"] = float(spearmanr(raw, tr_map).statistic)
            row["Born values"] = ", ".join(f"{x:+.1f}" for x in v)
            row["raw delay deg"] = ", ".join(f"{x:+.2f}" for x in raw)
            rows.append(row)
    return rows, dict(T_abs=T_abs, T_null=T_null, raw_gate=raw_gate)


# ----------------------------------------------------------------------------------------------- 0.3(a) pass gap
def pass_gap(ctx):
    rows = []
    twins = [("Mild 6 − 5", "Mild_lobe_new", "Mild_lobe"), ("Moderate 6 − 5", "Moderate_lobe_c3", "Moderate_lobe"),
             ("Severe 6 − 5", "Severe_lobe_c3", "Severe_lobe")]
    for rlab, ref in REFS.items():
        R = ctx.S[ref]
        for m in METH:
            fx = C3.make_x(ctx.model(ref), m, ctx.lam)

            def stats(X):
                amp = np.abs(X) * np.exp(1j * np.angle(R))
                pha = np.abs(R) * np.exp(1j * np.angle(X))
                lr = RL.contrasts(fx(X[ctx.fi], R[ctx.fi]))["LR"]
                xm = RL.contrasts(fx(mir(X)[ctx.fi], R[ctx.fi]))["LR"]
                x = fx(X[ctx.fi], R[ctx.fi])
                return dict(LR=lr, LR_anti=(lr - xm) / 2, LR_amp=RL.contrasts(fx(amp[ctx.fi], R[ctx.fi]))["LR"],
                            LR_phase=RL.contrasts(fx(pha[ctx.fi], R[ctx.fi]))["LR"], sectors=x[6:12])
            L_, Rm = stats(ctx.S["LeftOnly_test_c3"]), stats(mir(ctx.S["RightOnly_test"]))
            row = dict(reference=rlab, method=SH[m])
            for k in ("LR", "LR_anti", "LR_amp", "LR_phase"):
                row[f"Left−mirRight {k}"] = L_[k] - Rm[k]
                row[f"twins max abs Δ {k}"] = max(abs(stats(ctx.S[a])[k] - stats(ctx.S[b])[k]) for _, a, b in twins)
            cm = lambda X: float(per_antenna_delay(X, R, ctx.fi).mean())  # noqa: E731
            row["common-mode delay Left / mirRight deg"] = f"{cm(ctx.S['LeftOnly_test_c3']):.2f} / {cm(mir(ctx.S['RightOnly_test'])):.2f}"
            row["Left−mirRight common-mode delay deg"] = cm(ctx.S["LeftOnly_test_c3"]) - cm(mir(ctx.S["RightOnly_test"]))
            row["twins max abs Δ common-mode delay deg"] = max(abs(cm(ctx.S[a]) - cm(ctx.S[b])) for _, a, b in twins)
            row["phase share Left"] = L_["LR_phase"] / L_["LR"]
            row["phase share mirRight"] = Rm["LR_phase"] / Rm["LR"]
            aL = L_["sectors"][[1, 2]].mean()
            aR = Rm["sectors"][[1, 2]].mean()
            row["affected-sector mean Left / mirRight"] = f"{aL:.2f} / {aR:.2f}"
            row["relative Δ affected sectors (Left−mirRight)"] = (aL - aR) / aL
            rel = []
            for _, a, b in twins:
                aff = sorted(affected(a))
                sa, sb = stats(ctx.S[a])["sectors"][aff].mean(), stats(ctx.S[b])["sectors"][aff].mean()
                rel.append((sa - sb) / sb)
            row["twins relative Δ affected sectors (p6 − p5)"] = ", ".join(f"{x:+.2f}" for x in rel)
            rows.append(row)
    return rows


# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    a = ap.parse_args()
    reg, qc, mlog, thr = C3.registry_and_qc()
    reg.to_csv(OUT / "lobe_sets.csv", index=False)
    qc.to_csv(OUT / "lobe_qc_c3.csv", index=False)
    mlog.to_csv(OUT / "lobe_mask_log.csv", index=False)
    ctx = C3.Ctx(max(a.n, 20))
    res = dict(code=git_hash(ROOT), n_draws=a.n)
    res["qc_new"] = [r for r in qc.to_dict("records") if any(s in r["file"] for s in ("RightOnly", "Test_B", "Null_rot"))]
    res["mask_new"] = [r for r in mlog.to_dict("records") if any(s in r["file"] for s in ("RightOnly", "Test_B", "Null_rot"))]
    res["nulls_rows"], res["nulls_read"] = nulls_as_targets(ctx, a.n)
    res["anti"], res["anti_per"] = anti_section(ctx)
    res["cr"] = cr_section(ctx)
    res["pairs"], res["ring"] = pair_checks(ctx)
    res["rulers"] = ruler_rebuild(ctx)
    res["b24"] = b24_rebuild(ctx)
    res["readings"], res["reading_meta"] = readings(ctx)
    res["pass_gap"] = pass_gap(ctx)
    (OUT / "lobe_round3.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item")
                                                     else (o.tolist() if hasattr(o, "tolist") else str(o))), encoding="utf-8")
    import pickle
    (RL.CACHE / "lobe_round3.pkl").write_bytes(pickle.dumps(res))
    from imaging.lobe_round3_md import write_md
    write_md(res)
    print("done")


if __name__ == "__main__":
    main()
