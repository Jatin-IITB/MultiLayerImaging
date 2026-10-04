"""Round 5 (POST-HOC): the pre-registered rerun with every rotated null, rulers three ways, the pair p and the
independence check behind it, reference typicality (0.3c), and the survival table.

    python imaging/lobe_round5.py [--n 100]

Written and committed BEFORE Null_rot31 / Null_rot43 were loaded (dry run on the rotated nulls registered at the
time, rot07 and rot19). Fixed here, before the new files exist:

1. What runs is the procedure pre-registered in HANDOVER section 2 (round 4): the round-3 and round-4 computations
   with every registered rotated null (lobe_round3.use_nulls(ROT_ALL)). Round 3 and round 4 keep their own outputs
   as the 11-null record (their text names specific nulls); the same computations restricted to rot07/rot19 are
   repeated here as the 'old' column, which must equal the committed round-3/round-4 numbers.
2. Rulers three ways, with the definitions of the pre-registration 5966ee4: 'all nulls' = max over the 9 symmetric
   designs + every rotated null (THE ruler); 'without rot19'; 'rot19 alone' = floor |rot19| only, ruler =
   max(one-pass yardstick, floor). Only 'all nulls' is the ruler. Bar: >= 3x established, 2-3x sensitive,
   < 2x not determined.
3. Pair p for 'LeftOnly and RightOnly both beyond all N nulls': the product of the two rank p's (what rounds 2-3
   reported 'if independent') and the exact value 2 / ((N + 1)(N + 2)) for two values that both exceed the same N
   nulls when all N + 2 are exchangeable. The product understates p even for independent meshes, because both
   values are compared with the same null maximum.
4. Independence check: LR_anti of the healthy meshes (one geometry meshed several times: H7, H6, rotated nulls).
   Supported if the values take both signs with |mean| < SD, and q = rms(rot - H6) / (sqrt(2) x SD of all nulls)
   >= 0.5 (the rotated meshes differ from H6 about as much as two independent nulls). Contradicted if all share a
   sign with |mean| > SD, or if q < 0.5 (the rotated meshes reproduce H6's asymmetry).
5. Detection re-grade: per design, the affected-sector values over the sector ruler (best and worst affected
   sector), and the largest sector value over the max-sector ruler = max(largest one-pass yardstick of a sector,
   largest |sector| of a no-change null), three ways. MCI against rulers built without MCI.
6. 0.3(c): each healthy mesh against the complex mean of the other healthy meshes (frozen inversion, three
   methods; raw ring delay). H6 is 'most extreme' on a statistic with chance 1/6 if the meshes are exchangeable.
   H6 is called atypical if it is the most extreme in at least twice the chance number of statistic rows, or if all
   other healthy meshes lie on one side of it for at least max(2, 3 x the chance expectation) statistics.
   Alternative reference = mean of all healthy meshes, for target values and frozen calls only; never adopted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_round3 as R3  # noqa: E402
from imaging import lobe_round4 as R4  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import score_testb as TB  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, ROOT, git_hash  # noqa: E402
from imaging.report_lobe import SHORT  # noqa: E402

R3.use_nulls(R3.ROT_ALL)
ROT = R3.ROT
N19 = "Null_rot19"
H7, H6 = R3.H7, R3.H6
REFS = R3.REFS
PRIMARY, METH, SH = R3.PRIMARY, R3.METH, R3.SH
HEALTHY = (H6, H7) + ROT
SECT0 = ("Healthy_sliced", "Healthy_sliced_new", "MCI_lobe_c3")
TARGETS = ("Mild_lobe", "Mild_lobe_new", "Moderate_lobe", "Moderate_lobe_c3", "Severe_lobe", "Severe_lobe_c3",
           "LeftOnly_test_c3", "RightOnly_test", "Test_B")
WO19 = tuple(r for r in ROT if r != N19)
VARIANTS = (("11 nulls (round 3)", True, R3.ROT3), ("all", True, ROT), ("without rot19", True, WO19),
            ("rot19 alone", False, (N19,)))
VN = [v[0] for v in VARIANTS]
# supplied by the user with the delivery (sha256 first 16 hex) and the user's at-a-glance numbers vs H6 (verify only)
USER_SHA = {"Null_rot31": "7a7a6697c6c389d2", "Null_rot43": "551a05d494d6668c"}
USER_GLANCE = {"Null_rot07": dict(spread=1.45, ring_mean=0.24, left_right=0.69),
               "Null_rot19": dict(spread=0.68, ring_mean=0.85, left_right=0.28),
               "Null_rot31": dict(spread=1.69, ring_mean=0.63, left_right=1.17),
               "Null_rot43": dict(spread=0.91, ring_mean=0.55, left_right=0.84)}


def tier(x):
    if x is None or not np.isfinite(x):
        return "n/a"
    return "established" if x >= 3 else ("sensitive" if x >= 2 else "not determined")


def _tier(x, unit):
    if unit == "ratio":
        return tier(x)
    if unit == "mci":
        return "n/a" if x is None else ("nothing separable (< 2x)" if x < 2 else tier(x))
    return ""


def short(d):
    return d.replace("Null_", "").replace("Healthy_sliced_new", "H6").replace("Healthy_sliced", "H7")


def sset(ks):
    return " ".join(SHORT[k].split()[0] for k in sorted(ks)) or "none"


def nulls_of(base, extra, base_set):
    return (tuple(base_set) if base else ()) + tuple(extra)


# ----------------------------------------------------------------------------------------------- 1. files
def registry(qc, mlog):
    rows = []
    for r in ROT:
        p = ROOT / "data" / "raw" / f"new_with_slices_{r}.s6p"
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        reg = next(x for x in C3.REGISTRY if x[0] == r)
        q = next(x for x in qc if x["file"].endswith(f"_{r}.s6p"))
        from adstage.io.touchstone import read_touchstone
        t = read_touchstone(p)
        i, j = (int(x) - 1 for x in q["ports"].split("-"))
        k = int(np.argmin(np.abs(t.f_hz - q["at_GHz"] * 1e9)))
        lvl = np.sqrt(np.mean(np.abs(t.s[:, i, j]) ** 2))
        rows.append(dict(stem=r, sha256_16=h, matches_user=(h == USER_SHA[r]) if r in USER_SHA else "n/a (round 3)",
                         passes=reg[3], final_dS=reg[4], elements=reg[5], sets=reg[6], points=q["points"],
                         max_sv_squared=q["max_singular_value"] ** 2, passive=q["passive"],
                         worst_amp_nonrecip_dB=q["worst_amp_nonrecip_dB"], at_GHz=q["at_GHz"], ports=q["ports"],
                         path=q["path"], Sij_dB_there=float(20 * np.log10(abs(t.s[k, i, j]))),
                         path_band_level_dB=float(20 * np.log10(lvl)), recip_err_re_band_dB=q["its_recip_err_dB"],
                         worst_point_masked=q["worst_point_masked"], n_masked=q["n_masked"]))
    masks = [x for x in mlog if any(x["file"].endswith(f"_{r}.s6p") for r in ROT)]
    return rows, masks


# ----------------------------------------------------------------------------------------------- 3. LR_anti, pair p
def anti_three(ctx):
    rows, per = R3.anti_section(ctx)
    P = {(p["reference"], p["method"], p["design"]): p["LR_anti"] for p in per}
    out = []
    for r in rows:
        key = (r["reference"], r["method"])
        rec = dict(reference=r["reference"], method=r["method"], yardstick=r["yardstick"])
        for vn, base, extra in VARIANTS:
            rul = max(r["yardstick"], max(abs(P[key + (d,)]) for d in nulls_of(base, extra, R3.NULL9)))
            rec[f"ruler ({vn})"] = rul
            for d in ("LeftOnly_test_c3", "RightOnly_test", "Test_B"):
                rec[f"{d.split('_')[0]} ({vn})"] = abs(P[key + (d,)]) / rul
        out.append(rec)
    return rows, per, out


def pair_p(per, names, ref, meth):
    v = {p["design"]: p["LR_anti"] for p in per if p["reference"] == ref and p["method"] == meth}
    nul = np.abs([v[d] for d in names])
    N = len(nul)
    xl, xr = abs(v["LeftOnly_test_c3"]), abs(v["RightOnly_test"])
    pl, pr = (1 + np.sum(nul >= xl)) / (N + 1), (1 + np.sum(nul >= xr)) / (N + 1)
    both = bool(xl > nul.max() and xr > nul.max())
    return dict(N=N, p_Left=float(pl), p_Right=float(pr), product=float(pl * pr),
                exact_exchangeable=float(2 / ((N + 1) * (N + 2))) if both else float("nan"), both_beyond=both,
                predicted_signs=bool(v["LeftOnly_test_c3"] > 0 and v["RightOnly_test"] < 0))


def pairs(per):
    out = []
    for rlab in REFS:
        for m in METH:
            for vn, base, extra in VARIANTS[:3]:
                out.append(dict(reference=rlab, method=SH[m], nulls=vn, **pair_p(per, nulls_of(base, extra, R3.NULL9), rlab, SH[m])))
    return out


def independence(per):
    out = []
    for rlab in REFS:
        for m in METH:
            v = {p["design"]: p["LR_anti"] for p in per if p["reference"] == rlab and p["method"] == SH[m]}
            hv = np.array([v[d] for d in HEALTHY])
            sd_all = float(np.std([v[d] for d in R3.NULL11], ddof=1))
            q = float(np.sqrt(np.mean([(v[x] - v[H6]) ** 2 for x in ROT])) / (np.sqrt(2) * sd_all))
            mh, sh = float(hv.mean()), float(hv.std(ddof=1))
            npos = int((hv > 0).sum())
            shared = npos in (0, len(hv)) and abs(mh) > sh
            out.append(dict(reference=rlab, method=SH[m], **{short(d): float(v[d]) for d in HEALTHY},
                            healthy_mean=mh, healthy_SD=sh, n_positive=f"{npos}/{len(hv)}", SD_all_nulls=sd_all,
                            q_rot_vs_H6=q, H7_vs_H6=float(abs(v[H7] - v[H6]) / (np.sqrt(2) * sd_all)),
                            independence="contradicted" if (shared or q < 0.5) else "supported"))
    return out


# ----------------------------------------------------------------------------------------------- 5. detection
def detection(keep):
    rows, mci = [], []
    for rlab, ref in REFS.items():
        for vn, base, extra in VARIANTS:
            rul, Q, yard = keep[(rlab, vn)]
            nulls = [d for d in nulls_of(base, extra, SECT0) if d != ref]
            ms_rul = max(float(yard[:6].max()), max(float(np.abs(Q[d][:6]).max()) for d in nulls))
            for d in TARGETS:
                aff = sorted(R3.affected(d))
                a = Q[d][aff] / rul[aff]
                rows.append(dict(reference=rlab, variant=vn, design=d, affected=sset(aff), best_affected=float(a.max()),
                                 worst_affected=float(a.min()), max_sector=float(Q[d][:6].max()),
                                 max_sector_ruler=ms_rul, max_sector_ratio=float(Q[d][:6].max() / ms_rul)))
            nm = [d for d in nulls if d != "MCI_lobe_c3"]
            sec = np.maximum(yard[:6], np.max([np.abs(Q[d][:6]) for d in nm], 0)) if nm else yard[:6]
            lrn = [d for d in nulls_of(base, extra, R3.NULL9) if d not in (ref, "MCI_lobe_c3")]
            fbn = [d for d in nulls_of(base, extra, TB.FB_ZERO) if d not in (ref, "MCI_lobe_c3")]
            lr_r = max([float(yard[6])] + [abs(float(Q[d][6])) for d in lrn])
            fb_r = max([float(yard[7])] + [abs(float(Q[d][7])) for d in fbn])
            mq = Q["MCI_lobe_c3"]
            mci.append(dict(reference=rlab, variant=vn, max_sector_ratio=float((np.abs(mq[:6]) / sec).max()),
                            LR_ratio=abs(float(mq[6])) / lr_r, FB_ratio=abs(float(mq[7])) / fb_r))
    return rows, mci


# ----------------------------------------------------------------------------------------------- 8. rounds 3-4 calls
def readings_summary(rd):
    tags = [c[:-4] for c in rd[0] if c.endswith(" set")]
    return [dict(reading=t, hits=sum(r[f"{t} hits"] for r in rd), misses=sum(r[f"{t} misses"] for r in rd),
                 false_alarms=sum(r[f"{t} false"] for r in rd), exact=sum(bool(r[f"{t} exact"]) for r in rd), n=len(rd))
            for t in tags]


def round4(ctx, rot):
    R3.use_nulls(rot)
    rows = R4.row_values(ctx)
    fair = R4.fair(ctx, rows)
    loo = []
    for fam in (False, True):
        for stat, kinds in (("Born", ("gap", "mid")), ("Born", ("threshold",)), ("raw centred", ("gap", "mid")),
                            ("raw centred", ("threshold",)), ("raw uncentred", ("gap", "mid")),
                            ("raw uncentred", ("threshold",))):
            loo.append(R4.loo(rows, stat, kinds, by_family=fam)[0])
    rd, meta = R3.readings(ctx)
    R3.use_nulls(R3.ROT_ALL)
    return dict(fair=fair, loo=loo, readings=readings_summary(rd), reading_meta=meta, readings_rows=rd)


# ----------------------------------------------------------------------------------------------- 9. 0.3(c)
def typicality(ctx):
    band = np.flatnonzero((ctx.f >= 3.2e9 - 1) & (ctx.f <= 4.2e9 + 1))
    rows, ring = [], []
    for i in HEALTHY:
        key = f"__mean_others_{short(i)}"
        ctx.S[key] = np.mean([ctx.S[d] for d in HEALTHY if d != i], 0)
        for m in METH:
            fx = C3.make_x(ctx.model(key), m, ctx.lam)
            q = C3.qvec(fx(ctx.S[i][ctx.fi], ctx.S[key][ctx.fi]))
            rows.append(dict(mesh=short(i), method=SH[m], **{s: float(q[k]) for k, s in enumerate(SHORT)},
                             LR=float(q[6]), FB=float(q[7]), max_abs_sector=float(np.abs(q[:6]).max())))
        for vname, sel in (("fit 3.4/3.6/3.8", ctx.fi), ("band 3.2-4.2", band)):
            pa = R3.per_antenna_delay(ctx.S[i], ctx.S[key], sel)
            ring.append(dict(mesh=short(i), view=vname, ring_mean_delay=float(pa.mean()),
                             ring_range=float(pa.max() - pa.min()),
                             left_minus_right=float(pa[[1, 2]].mean() - pa[[4, 5]].mean())))
    stats = list(SHORT) + ["LR", "FB", "max_abs_sector"]
    ext = []
    for m in METH:
        for s in stats:
            vals = {r["mesh"]: r[s] for r in rows if r["method"] == SH[m]}
            order = sorted(vals, key=lambda k: -abs(vals[k]))
            ext.append(dict(method=SH[m], statistic=s, most_extreme=order[0], H6_rank=order.index("H6") + 1,
                            H6=vals["H6"], largest_other=max(abs(v) for k, v in vals.items() if k != "H6")))
    for vname in ("fit 3.4/3.6/3.8", "band 3.2-4.2"):
        for s in ("ring_mean_delay", "ring_range", "left_minus_right"):
            vals = {r["mesh"]: r[s] for r in ring if r["view"] == vname}
            order = sorted(vals, key=lambda k: -abs(vals[k]))
            ext.append(dict(method=f"raw ({vname})", statistic=s, most_extreme=order[0], H6_rank=order.index("H6") + 1,
                            H6=vals["H6"], largest_other=max(abs(v) for k, v in vals.items() if k != "H6")))
    return rows, ring, ext


def one_sided(ctx, keep):
    """Against H6 as the reference: how many of the other healthy meshes lie on each side, per statistic."""
    _, Q, _ = keep[("H6", "all")]
    others = (H7,) + ROT
    out = []
    for k, s in enumerate(list(SHORT) + ["LR", "FB"]):
        v = [float(Q[d][k]) for d in others]
        npos = sum(x > 0 for x in v)
        out.append(dict(statistic=s, values=", ".join(f"{short(d)} {x:+.2f}" for d, x in zip(others, v)),
                        n_positive=f"{npos}/{len(v)}", one_side=npos in (0, len(v))))
    band = np.flatnonzero((ctx.f >= 3.2e9 - 1) & (ctx.f <= 4.2e9 + 1))
    for vname, sel in (("fit 3.4/3.6/3.8", ctx.fi), ("band 3.2-4.2", band)):
        v = [float(R3.per_antenna_delay(ctx.S[d], ctx.S[H6], sel).mean()) for d in others]
        npos = sum(x > 0 for x in v)
        out.append(dict(statistic=f"ring-mean neighbour delay ({vname}), deg",
                        values=", ".join(f"{short(d)} {x:+.2f}" for d, x in zip(others, v)),
                        n_positive=f"{npos}/{len(v)}", one_side=npos in (0, len(v))))
    return out


def alt_reference(ctx):
    key = "__mean_healthy"
    ctx.S[key] = np.mean([ctx.S[d] for d in HEALTHY], 0)
    rule = ctx.fz["rules"][PRIMARY]
    refs = (("H7", H7), ("H6", H6), ("mean of healthy meshes", key))
    calls, c6 = [], []
    for rn, ref in refs:
        fx = C3.make_x(ctx.model(ref), PRIMARY, ctx.lam)
        R = ctx.S[ref]
        for d in TARGETS + ("MCI_lobe_c3",):
            x = fx(ctx.S[d][ctx.fi], R[ctx.fi])
            a = RL.apply_rules(x, rule)
            v = np.asarray(x)[6:12]
            calls.append(dict(design=d, reference=rn, truth=sset(R3.affected(d)),
                              called=sset([j for j in range(6) if a["affected"][j]]), side=a["side"],
                              frontback=a["frontback"], LR=float(a["LR"]), FB=float(a["FB"]),
                              rank_set=sset(np.argsort(-v)[:R3.largest_gap_k(v, rule["T_null"])]),
                              max_sector=float(v.max())))
        # the committed C6 rule (0ceb626), applied to this reference (post hoc for the non-H6 references)
        Sro = ctx.S["RightOnly_test"]
        lr = float(RL.contrasts(fx(Sro[ctx.fi], R[ctx.fi]))["LR"])
        rho = SL.recip(Sro) / SL.recip(R)
        i23, i56 = SL.PAIRS.index((1, 2)), SL.PAIRS.index((4, 5))
        ph = {}
        for fq in (3.4, 3.6):
            k = int(np.argmin(np.abs(ctx.f - fq * 1e9)))
            ph[fq] = float(np.degrees(np.angle(rho[i56, k])) - np.degrees(np.angle(rho[i23, k])))
        env = 3.9
        verdict = ("REPLICATED" if lr < 0 and abs(lr) >= 2 * env and ph[3.4] < 0 and ph[3.6] < 0
                   else ("FAILED" if lr >= 0 or abs(lr) < env else "INCONCLUSIVE"))
        c6.append(dict(reference=rn, LR=lr, phase_3p4=ph[3.4], phase_3p6=ph[3.6], verdict=verdict))
    return calls, c6


def glance(ctx):
    """The user's at-a-glance phase columns vs H6, recomputed with my definitions (verify, do not adopt)."""
    out = []
    nb = [SL.PAIRS.index(tuple(sorted((t, (t + 1) % 6)))) for t in range(6)]
    for vname, sel in (("band 3.2-4.2", np.flatnonzero((ctx.f >= 3.2e9 - 1) & (ctx.f <= 4.2e9 + 1))),
                       ("3.30-3.65", np.flatnonzero((ctx.f >= 3.3e9 - 1) & (ctx.f <= 3.65e9 + 1))),
                       ("fit 3.4/3.6/3.8", ctx.fi)):
        for d in ROT:
            rho = SL.recip(ctx.S[d]) / SL.recip(ctx.S[H6])
            ph = -np.degrees(np.angle(rho[nb][:, sel])).mean(1)          # delay-positive, per neighbour path
            u = USER_GLANCE.get(d, {})
            out.append(dict(null=short(d), view=vname, ring_mean_delay=float(ph.mean()), user_ring_mean=u.get("ring_mean"),
                            path_SD=float(ph.std(ddof=1)), path_range=float(ph.max() - ph.min()), user_spread=u.get("spread"),
                            left_minus_right=float(ph[[0, 1, 2]].mean() - ph[[3, 4, 5]].mean()),
                            user_left_right=u.get("left_right")))
    return out


# ----------------------------------------------------------------------------------------------- 11. survival
def survival(res):
    an = {(r["reference"], r["method"]): r for r in res["anti3"]}
    pp = {(r["reference"], r["method"], r["nulls"]): r for r in res["pairs"]}
    rl = {(r["reference"], r["rulers"]): r for r in res["rulers"]}
    cr = {(r["view"], r["nulls"]): r for r in res["cr"]}
    b24 = res["b24"]
    det = res["detection"]
    mci = {(r["reference"], r["variant"]): r for r in res["mci"]}
    S = []

    def add(cid, claim, vals, unit="ratio", note=""):
        S.append(dict(id=cid, claim=claim, unit=unit, **{v: vals.get(v) for v in VN},
                      tier_all=_tier(vals.get("all"), unit), tier_without_rot19=_tier(vals.get("without rot19"), unit), note=note))

    for who in ("LeftOnly", "RightOnly"):
        for ref in REFS:
            for m in ("Tikhonov dS", "whitened log"):
                add(f"anti {who} {ref} {m}", f"{who} LR_anti / R1c ruler ({ref}, {m})",
                    {v: an[(ref, m)][f"{who} ({v})"] for v in VN})
    for ref in REFS:
        add(f"pair product {ref}", f"pair rank p, product of the two rank p's ({ref}, Tikhonov dS)",
            {v: pp[(ref, "Tikhonov dS", v)]["product"] for v in VN[:3]}, unit="p")
        add(f"pair exact {ref}", f"pair rank p, both beyond the same nulls (exact) ({ref}, Tikhonov dS)",
            {v: pp[(ref, "Tikhonov dS", v)]["exact_exchangeable"] for v in VN[:3]}, unit="p")
    for view in ("band mean 3.2-4.2 GHz", "band mean 3.30-3.65 GHz", "3.4 GHz"):
        for rule in ("rms", "max"):
            add(f"cr {view} {rule}", f"LeftOnly cross-ratio phases >= 3x ({rule} rule), {view}, of 18",
                {v: cr[(view, v)][f"LeftOnly ≥3× {rule}"] for v in VN}, unit="count")
        add(f"cr {view} null files", f"null files >= 3x (leave-one-out, rms rule), {view}, max over files, of 18",
            {v: cr[(view, v)]["null files ≥3× rms (leave-one-out), max over files"] for v in VN}, unit="count")
    for ref in REFS:
        for d, keys in (("Test", ("S2 TL", "S5 PR")), ("RightOnly", ("S5 PR", "S6 TR")), ("LeftOnly", ("S2 TL", "S3 PL"))):
            for k in keys:
                add(f"sector {d} {k} {ref}", f"{'Test_B' if d == 'Test' else d} {k} / sector ruler ({ref})",
                    {v: rl[(ref, v)].get(f"{d} {k} ratio") for v in VN})
    for r in b24:
        add(f"b24 {r['set']} {r['method']}", f"bias-corrected Moderate FB / ruler ({r['set']}, {r['method']})",
            {v: r[f"ratio ({v})"] for v in VN})
    for ref in REFS:
        add(f"mci {ref}", f"MCI largest of sector, LR, FB / its ruler without MCI ({ref}); claim: < 2x (nothing separable)",
            {v: max(mci[(ref, v)][k] for k in ("max_sector_ratio", "LR_ratio", "FB_ratio")) for v in VN}, unit="mci")
        add(f"det min best {ref}", f"weakest design's best affected sector / sector ruler ({ref}), over {len(TARGETS)} designs",
            {v: min(r["best_affected"] for r in det if r["reference"] == ref and r["variant"] == v) for v in VN})
        add(f"det min maxsector {ref}", f"weakest design's largest sector / max-sector ruler ({ref})",
            {v: min(r["max_sector_ratio"] for r in det if r["reference"] == ref and r["variant"] == v) for v in VN})
    return S


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
    res = dict(code=git_hash(ROOT), n_draws=a.n, rot=list(ROT), nulls=list(R3.NULL11), variants=[list(v[:2]) + [list(v[2])] for v in VARIANTS])
    res["files"], res["masks"] = registry(qc.to_dict("records"), mlog.to_dict("records"))
    res["nulls_rows"], res["nulls_read"] = R3.nulls_as_targets(ctx, a.n)
    res["anti"], per, res["anti3"] = anti_three(ctx)
    res["anti_per"] = per
    res["pairs"] = pairs(per)
    res["independence"] = independence(per)
    res["cr"] = R3.cr_section(ctx, (("9 nulls", R3.NULL9),) + tuple((vn, nulls_of(b, e, R3.NULL9)) for vn, b, e in VARIANTS))
    keep = {}
    res["rulers"] = R3.ruler_rebuild(ctx, VARIANTS, keep)
    res["detection"], res["mci"] = detection(keep)
    res["b24"] = R3.b24_rebuild(ctx, VARIANTS)
    res["fit"], res["fit_summary"] = R4.fit_stats(ctx)
    res["r4"] = {vn: round4(ctx, rot) for vn, rot in (("11 nulls (round 3)", R3.ROT3), ("all", ROT), ("without rot19", WO19))}
    res["typ_rows"], res["typ_ring"], res["typ_extreme"] = typicality(ctx)
    res["one_sided"] = one_sided(ctx, keep)
    res["alt_calls"], res["alt_c6"] = alt_reference(ctx)
    res["glance"] = glance(ctx)
    g = [r for r in res["glance"] if r["view"] == "band 3.2-4.2" and r["user_spread"] is not None]
    res["glance_spearman_spread"] = float(spearmanr([r["path_SD"] for r in g], [r["user_spread"] for r in g]).statistic) if len(g) > 2 else None
    res["survival"] = survival(res)
    (OUT / "lobe_round5.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else (
        o.tolist() if hasattr(o, "tolist") else (sorted(o) if isinstance(o, set) else str(o)))), encoding="utf-8")
    (RL.CACHE / "lobe_round5.pkl").write_bytes(pickle.dumps(res))
    from imaging.lobe_round5_md import write_md
    write_md(res)
    print("done")


if __name__ == "__main__":
    main()
