"""PRE-REGISTERED evaluation of the null rulers (committed 2026-10-04 before Null_rot31 / Null_rot43 exist).
Everything it produces is POST HOC with respect to Test_B and RightOnly. Frozen files, protocols, predictions,
submitted estimates and committed verdicts are never changed.

    python scripts/18_null_rulers.py [--n 300]

The rotated nulls are read from data/sims_lobe.csv (every row whose set lists `lobe_nulls`), so the script runs
unchanged when Null_rot31 / Null_rot43 are added. Writes results/05_lobe/null_rulers/{report.md, *.csv}; the
pre-registration text is results/05_lobe/null_rulers/preregistration.md.

Rulers (pre-registered; bars are the existing ones: >= 3x established / survives, 2-3x sensitive, < 2x not):
  NULLS   = the 9 mirror-symmetric designs + every rotated null. No null is dropped (rot19 included) unless the user
            documents a build defect in HFSS.
  Variants reported side by side:
    "all nulls"            floors over the 9 + all rotated nulls; re-mesh yardstick over all rotated nulls;
    "all nulls w/o rot19"  the same with Null_rot19 removed;
    "rot19 alone"          the ruler Null_rot19 sets by itself: floor = |value(rot19)|; re-mesh yardstick =
                           max(one-pass yardstick, |Q(rot19) - Q(H6)|); pattern-fit null contrast = r0(rot19) and
                           healthy-twin ring mean = |g(rot19)|.
    Only "all nulls" is the ruler; the other two show the dependence on one sample and are never adopted.
  R1c clean ruler of a mirror statistic = max(floor, one-pass yardstick); floor = max |T| over the variant's nulls
  (leave-one-out when a null is the target).
  Re-mesh yardstick of R31 / R21 / R32 / front-back indices = max(one-pass yardstick, max |Q(rotated) - Q(H6)|).
  Label margin ratio A1 = |margin to the label edge| / max(yardstick, boundary SD); quadrature adds the ±0.5 dB spread.
  Pattern fit (protocol d3a4bbf rule, w = 0.4): null contrast = max(protocol 0.212 deg, r0 of the variant's rotated
  nulls against Healthy_sliced_new); healthy-twin ring mean = max(1.111 deg, |g| of the variant's rotated nulls).
Path classes (descriptive): for every pair, the per-path band-power difference (dB) of each class k = 1, 2, 3 at
  3.30-3.65 GHz and 3.2-4.2 GHz. A class difference is called "common-mode" if every path has the sign of the class
  mean and |mean| >= 2 x the SD of the paths about that mean; otherwise "scattered".
  Pairs: each rotated null - Healthy_sliced_new; every rotated null against every other; the four refinement twins
  (Healthy 6->7, Mild 5->6, Moderate 5->6, Severe 5->6) and LeftOnly - mirrored RightOnly (pass 6 vs 5).
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adstage.config import load_config  # noqa: E402
from adstage.features.metrics import to_ring_order  # noqa: E402
from adstage.features.ring_features import features  # noqa: E402
from adstage.io.dataset import load_dataset  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
L9 = _load("lobe09", "09_lobe_tests.py")
R10 = _load("rev10", "10_lobe_review.py")
R11 = _load("rev11", "11_review2.py")
T15 = _load("tb15", "15_test_b.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "null_rulers"
H6, H7, LO, RO, TB, MCI = R11.H6, R11.H7, R11.LO, "RightOnly_test", "Test_B", R11.MCI
N19 = "Null_rot19"
SYM9 = list(R11.SYM)
RATIOS = ("R31", "R21", "R32")
FBK = ("index: front-back, all paths", "index: front-back, neighbour paths")
W = 0.4
BANDS = {"3.30-3.65 GHz": (3.30e9, 3.65e9), "3.2-4.2 GHz": (3.2e9, 4.2e9)}
md = L7.md
tier = R10.tier


def class_paths(k):
    return [(i, j) for i in range(6) for j in range(i + 1, 6) if L7.DIST[i, j] == k]


def path_db(f, S, band):
    m = R11.fmask(f, band)
    Sb = R11.sbar(S)[m]
    return 10 * np.log10(np.mean(np.abs(Sb) ** 2, 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)
    cfg = load_config(ROOT, "config_lobe.yaml")
    rule = json.loads((ROOT / "results/04/frozen_rule.json").read_text())
    f, Sd, man, ds = L8.load_all(cfg)
    ROT = sorted(d for d, s_ in zip(man.design, man.set.astype(str)) if "lobe_nulls" in s_.split())
    if N19 not in ROT:
        raise SystemExit("Null_rot19 missing from the manifest")
    ROT_W = [r for r in ROT if r != N19]
    VAR = {"all nulls": (SYM9 + ROT, ROT, False), "all nulls w/o rot19": (SYM9 + ROT_W, ROT_W, False),
           "rot19 alone": ([N19], [N19], True)}
    L = [f"# Null rulers, pre-registered evaluation (code {gh}; POST HOC with respect to Test_B and RightOnly)", "",
         f"Rotated nulls in the manifest: {', '.join(ROT)}. Only 'all nulls' is the ruler; the other two variants show the "
         "dependence on Null_rot19 and are not adopted.", ""]

    # ================================================================== P: path classes
    pairs = [(f"{r} - {H6}", Sd[r], Sd[H6]) for r in ROT]
    pairs += [(f"{a} - {b}", Sd[a], Sd[b]) for a, b in itertools.combinations(ROT, 2)]
    pairs += [(f"twin {n} (b - a)", Sd[b], Sd[a]) for n, (a, b) in L8.PAIRS.items()]
    pairs += [(f"{LO} - mirrored {RO} (pass 6 vs 5)", Sd[LO], R10.mirror(Sd[RO]))]
    prow, crow = [], []
    for bn, band in BANDS.items():
        lev = path_db(f, Sd[H6], band)
        for pn, A, B in pairs:
            dA = path_db(f, A, band) - path_db(f, B, band)
            for k in (1, 2, 3):
                ps = class_paths(k)
                v = np.array([dA[i, j] for i, j in ps])
                mu, sd = float(v.mean()), float(v.std())
                same = int(np.sum(np.sign(v) == np.sign(mu)))
                cm = same == len(v) and abs(mu) >= 2 * sd
                crow.append({"band": bn, "pair": pn, "class": f"k={k} ({L7.PATH[k]})", "n paths": len(v),
                             "H6 level (dB)": float(np.mean([lev[i, j] for i, j in ps])), "mean (dB)": mu,
                             "SD about mean (dB)": sd, "min": float(v.min()), "max": float(v.max()),
                             "same sign as mean": f"{same}/{len(v)}", "verdict": "common-mode" if cm else "scattered"})
                for (i, j), x in zip(ps, v):
                    prow.append({"band": bn, "pair": pn, "class": k, "path": f"T{i + 1}-T{j + 1}", "diff dB": float(x),
                                 "H6 level dB": float(lev[i, j])})
    ct = pd.DataFrame(crow)
    ct.to_csv(OUT / "P_path_classes.csv", index=False)
    pd.DataFrame(prow).to_csv(OUT / "P_paths.csv", index=False)
    piv = ct.pivot_table(index=["band", "pair"], columns="class", values="verdict", aggfunc="first").reset_index()
    L += ["## P. Path classes: common-mode or scattered (descriptive; criterion in the script docstring)",
          md(piv), "", md(ct, ".3f"), ""]

    # ================================================================== shared quantities
    MI = T15.Mirror(f, Sd)
    keys = [(r.statistic, r.frequencies) for _, r in MI.table.iterrows()]
    inf_keys = [(r.statistic, r.frequencies) for _, r in MI.inf.iterrows()]
    cache = {}

    def v(d, k):
        if d not in cache:
            cache[d] = MI.values(d)
        return cache[d][k]

    def yard_of(k):
        if k[0].startswith("phase cross-ratio "):
            c = k[0][len("phase cross-ratio "):]
            m_ = np.ones(len(f), bool) if k[1].startswith("band mean") else MI.msk
            return max(abs(float(MI.cp(b)[c][m_].mean() - MI.cp(a)[c][m_].mean())) for a, b in L8.PAIRS.values())
        return max(abs(v(b, k) - v(a, k)) for a, b in L8.PAIRS.values())

    yards = {k: yard_of(k) for k in keys}
    R = L8.rulers(f, Sd, cfg, args.n, qfn=L9.ext_quantities)
    Q = R["Q"]
    IM = R10.Imaging(f)
    Simg = {d: IM.SL.load_design(d, f)[0] for d in SYM9 + ROT + [LO, RO, TB]}
    T_im = {}
    for mth in IM.methods:
        for rn, ref in (("Healthy_sliced", H7), ("Healthy_sliced_new", H6)):
            Sr = Simg[ref]
            T_im[(mth, rn)] = ({d: IM.T(Simg[d], Sr, mth) for d in Simg},
                               max(abs(IM.T(Simg[b], Sr, mth) - IM.T(Simg[a], Sr, mth)) for a, b in L8.PAIRS.values()))
    pp = {d: R11.pair_phase(Sd[d]) for d in SYM9 + ROT + [LO]}
    res = {d: R11.resonance(f, Sd[d]) for d in SYM9 + ROT + [LO]}
    lrres = {d: (res[d][1][0] + res[d][2][0]) / 2 - (res[d][5][0] + res[d][4][0]) / 2 for d in res}
    Xr = {}
    for d in [LO, RO]:
        x, nm_, _, _ = features(f, Sd[d][None])
        Xr[d] = {r: float(x[0][nm_.index(r)]) for r in RATIOS}
    Yh = {d: T15.nb_phase(f, Sd[d], Sd[H6]) for d in ROT + [TB]}
    nc_prot = max(float(np.std(T15.nb_phase(f, Sd[a], Sd[b]))) for a, b in T15.UNIFORM)
    hg_prot = abs(float(np.mean(T15.nb_phase(f, Sd[H7], Sd[H6]))))
    # boundary SDs (as in 11_review2 / 15_test_b)
    r6 = pd.read_csv(LOBE / "review2" / "R6_A28_rulers.csv")
    tb_sd = float(r6[r6.rule == "binary"]["boundary SD"].iloc[0])
    cfg_u = load_config(ROOT, "config_repeats.yaml")
    du = load_dataset(cfg_u, ROOT)
    Xu, nu, _, _ = features(du.f_hz, to_ring_order(du.S, du.port_to_ant))
    ucls = list(du.classes)
    rng = np.random.default_rng([cfg["seed"], 111])
    fro = {k: sorted(float(p.split(" at ")[1]) for p in v_.split(", ")) for k, v_ in L7.boundaries(rule).items()}
    bfro = {"three": fro["three (R21)"], "three_merged": fro["three_merged (R32)"]}
    bsd = {}
    for sch, (ft, cls) in {"three": ("R21", [["Normal"], ["Mild"], ["Severe"]]),
                           "three_merged": ("R32", [["Normal"], ["Mild", "Moderate"], ["Severe"]])}.items():
        sols = [[s for s, c in enumerate(ucls) if c in mem] for mem in cls]
        bb = [sorted(0.5 * (mu[i] + mu[i + 1]) for i in range(2)) for mu in
              ([np.mean([float(Xu[s][nu.index(ft)]) for s in rng.choice(ss, len(ss))]) for ss in sols] for _ in range(3000))]
        bsd[sch] = np.array(bb).std(0, ddof=1)
    lab_designs = list(R11.STAGES["lobe_A"]) + list(R11.STAGES["lobe_B"]) + [LO, MCI]

    # ================================================================== rulers and survival per variant
    surv, rul = [], []
    for vn, (fnulls, rnulls, alone) in VAR.items():
        def floor(k, exclude=None):
            vals = [abs(v(d, k)) for d in fnulls if d != exclude]
            return float(max(vals)) if vals else 0.0

        def ruler(k, exclude=None):
            return max(floor(k, exclude), yards[k])

        def ymesh(k):
            return max(R["yard"][k], max(abs(float(Q[r][k][0] - Q[H6][k][0])) for r in rnulls))
        if alone:
            nc, hg = float(np.std(Yh[N19])), abs(float(np.mean(Yh[N19])))
        else:
            nc = max(nc_prot, *(float(np.std(Yh[r])) for r in rnulls)) if rnulls else nc_prot
            hg = max(hg_prot, *(abs(float(np.mean(Yh[r]))) for r in rnulls)) if rnulls else hg_prot
        for k in RATIOS + FBK:
            rul.append({"variant": vn, "ruler": f"yardstick {k}", "value": ymesh(k)})
        rul += [{"variant": vn, "ruler": "pattern-fit null contrast (deg)", "value": nc},
                {"variant": vn, "ruler": "healthy-twin ring mean (deg)", "value": hg}]
        for k in keys:
            rul.append({"variant": vn, "ruler": f"clean ruler {k[0]} [{k[1]}]", "value": ruler(k)})

        def add(item, bar, value, verdict):
            surv.append({"item": item, "bar": bar, "variant": vn, "value": value, "verdict": verdict})

        # label margins
        mrows = []
        for d in lab_designs + [RO, TB]:
            for sch, ft in (("binary", "R31"), ("three", "R21"), ("three_merged", "R32")):
                x = float(Q[d][ft][0])
                lab, mg = R10.edge_margin(rule, sch, x)
                sb = tb_sd if sch == "binary" else float(bsd[sch][int(np.argmin([abs(x - b) for b in bfro[sch]]))])
                yd = ymesh(ft)
                s05 = R["sd"]["spread ±0.5 dB"][ft] / np.sqrt(2)
                mrows.append({"design": d, "rule": sch, "label": lab, "A1": abs(mg) / max(yd, sb),
                              "quadrature": abs(mg) / np.sqrt(yd ** 2 + sb ** 2 + s05 ** 2)})
        mt = pd.DataFrame(mrows)
        mt.assign(variant=vn).to_csv(OUT / f"label_margins_{vn.replace(' ', '_').replace('/', '')}.csv", index=False)
        lob = mt[mt.design.isin(lab_designs)]
        add("frozen labels >= 3x (A1), 30 lobe labels", ">= 3x", int((lob.A1 >= 3).sum()), f"{int((lob.A1 >= 3).sum())}/30")
        st_ = lob[lob.rule != "binary"]
        add("staging labels (20): >= 3x / 2-3x / < 2x", "tiers",
            f"{int((st_.A1 >= 3).sum())} / {int(((st_.A1 >= 2) & (st_.A1 < 3)).sum())} / {int((st_.A1 < 2).sum())}",
            "sensitive: " + ", ".join(f"{r.design} {r.rule} {r.A1:.2f}x" for r in st_[(st_.A1 >= 2) & (st_.A1 < 3)].itertuples()))
        for d in lab_designs + [RO, TB]:
            for sch in ("binary", "three", "three_merged"):
                r_ = mt[(mt.design == d) & (mt.rule == sch)].iloc[0]
                add(f"label {d} {sch} ({r_['label']})", "A1 >= 3x", float(r_.A1), tier(float(r_.A1)))
        add("claim 6: mask shift 0.319 dB / R31 yardstick", ">= 2x", 0.319 / ymesh("R31"), tier(0.319 / ymesh("R31")))
        g10 = 0.489 / (2 * ymesh("R21"))
        add("claim 10: smallest lobe R21 stage gap / (2 x R21 yardstick)", ">= 1", g10, "separates" if g10 >= 1 else "does not separate")
        for nm_, d in (("claim 32: R21 rise of LeftOnly / R21 yardstick", LO), ("claim 32: R21 rise of Test_B / R21 yardstick", TB),
                       ("claim 32: R21 rise of RightOnly / R21 yardstick", RO)):
            x = (float(Q[d]["R21"][0]) - float(Q[H6]["R21"][0])) / ymesh("R21")
            add(nm_, "tiers", x, tier(x))
        x29 = 0.133 / ymesh("R21")
        add("claim 29: R21 mirror-twin difference 0.133 dB / R21 yardstick", "> 1 = exceeds", x29, "exceeds" if x29 > 1 else "within")
        for (mth, rn), (T, yd) in T_im.items():
            fl = max([abs(T[d]) for d in fnulls if d in T] or [0.0])
            for d in (LO, RO, TB):
                x = abs(T[d]) / max(fl, yd)
                add(f"claim 15 imaging LR {d} [{mth}, {rn}]", "tiers", x, tier(x))
        for band in ("band mean 3.2-4.2", "3.30-3.65 GHz"):
            sub = [k for k in keys if k[0].startswith("phase cross-ratio") and k[1] == band]
            for d, nm_ in ((LO, "claim 16 LeftOnly"), (RO, "C6 P2 RightOnly"), (TB, "Test_B")):
                c = sum(abs(v(d, k)) / ruler(k) >= 3 for k in sub)
                add(f"{nm_} phase cross-ratios >= 3x [{band}]", "count", c, str(c))
        nmax = max([abs(lrres[d]) for d in fnulls if d in lrres] or [0.0])
        add("claim 17: LeftOnly LR resonance shift vs null max (MHz)", "beyond null?", lrres[LO],
            f"{lrres[LO]:+.2f} vs {nmax:.2f}: " + ("beyond" if abs(lrres[LO]) > nmax else "not beyond"))
        for st in ("power pair T2 refl. vs T6 refl.", "power pair T3 refl. vs T5 refl."):
            k = (st, "band mean 3.2-4.2")
            for d in (LO, RO, TB):
                x = abs(v(d, k)) / ruler(k)
                add(f"claim 18/33 {st[11:]} {d}", "tiers", x, tier(x))
        kk = [("power pair T2 refl. vs T6 refl.", "band mean 3.2-4.2"), ("power pair T3 refl. vs T5 refl.", "band mean 3.2-4.2")]
        okb = all(abs(v(TB, k)) / ruler(k) >= 3 for k in kk) and np.sign(v(TB, kk[0])) == np.sign(v(LO, kk[0])) \
            and np.sign(v(TB, kk[1])) == -np.sign(v(LO, kk[1]))
        add("claim 33: Test_B per-pair reading S2 left and S5 right, both >= 3x", "both >= 3x, signs as stated", float(okb),
            "holds" if okb else "does not hold")
        for st in ("T2-T3 vs T5-T6", "T3-T4 vs T4-T5", "T1-T2 vs T1-T6"):
            lo_v = float(pp[LO][st][MI.msk].mean())
            m_ = max([abs(float(pp[d][st][MI.msk].mean())) for d in fnulls if d in pp] or [1e-9])
            add(f"claim 19 LeftOnly phase pair {st} (3.30-3.65) / null max", "tiers", abs(lo_v) / m_, tier(abs(lo_v) / m_))
        n1 = sum((np.sign(v(RO, k)) == -np.sign(v(LO, k))) and abs(v(RO, k) + v(LO, k)) <= ruler(k) for k in inf_keys)
        add("claim 28 / C6 P1 within tolerance (post hoc only)", "count of 26", n1, f"{n1}/26")
        p4 = ", ".join(f"{r} {abs(Xr[RO][r] - Xr[LO][r]) <= ymesh(r)}" for r in RATIOS)
        add("C6 P4 within yardstick (post hoc only)", "all True", np.nan, p4)
        raised = {}
        for k in keys:
            if ruler(k) > max(max(abs(v(d, k)) for d in SYM9), yards[k]) * 1.0001:
                fam_ = R10.fam_of(k[0])
                raised[fam_] = raised.get(fam_, 0) + 1
        add("claim 35: mirror rulers raised above the 9-null rulers, by family", "count", sum(raised.values()), str(raised))
        for d in (TB,):
            for k in FBK:
                x = abs(float(Q[d][k][0] - Q[H6][k][0])) / max(ymesh(k), R["fdiff"][k])
                add(f"Test_B {k.replace('index: ', '')}", "tiers", x, tier(x))
        votes = []
        for k in inf_keys:
            x = abs(v(TB, k)) / ruler(k)
            if x >= 2:
                votes.append("left" if np.sign(v(TB, k)) == np.sign(v(LO, k)) else "right")
        side = "none" if len(votes) < 3 else ("left" if votes.count("left") / len(votes) >= 0.8 else
                                              ("right" if votes.count("right") / len(votes) >= 0.8 else "mixed"))
        add("Test_B mirror side (protocol rule)", "as protocol", len(votes), f"{side} ({votes.count('left')} left, {votes.count('right')} right)")
        loc = T15.localise(Yh[TB], W, nc, hg)
        add("claim 34: Test_B pattern fit (contrast / call)", ">= 2x and residual <= 0.5 r0", loc["contrast / null"],
            f"{'accepted' if loc['accepted'] else 'rejected'}; call {loc['pattern call']}; sectors "
            + ", ".join(f"S{i + 1} {c[0]}{q:.1f}" for i, (c, q) in enumerate(zip(loc["sector calls"], loc["sector confidence"]))))
        for r in ROT:
            if alone and r == N19:
                continue
            o = [x for x in rnulls if x != r]
            nc_r = max(nc_prot, *(float(np.std(Yh[x])) for x in o)) if (o and not alone) else (nc if alone else nc_prot)
            hg_r = max(hg_prot, *(abs(float(np.mean(Yh[x]))) for x in o)) if (o and not alone) else (hg if alone else hg_prot)
            lr_ = T15.localise(Yh[r], W, nc_r, hg_r)
            add(f"claim 34: {r} as target (leave-one-out rulers) must give 'none'", "call = none", lr_["contrast / null"],
                f"{lr_['pattern call']} (contrast {lr_['contrast / null']:.2f}x)")
    sv = pd.DataFrame(surv)
    sv.to_csv(OUT / "survival_long.csv", index=False)
    wide = sv.pivot_table(index="item", columns="variant", values="verdict", aggfunc="first", sort=False).reset_index()
    order = list(dict.fromkeys(sv["item"]))
    wide = wide.set_index("item").loc[order].reset_index()[["item"] + list(VAR)]
    wide.to_csv(OUT / "survival_wide.csv", index=False)
    rt = pd.DataFrame(rul)
    rw = rt.pivot_table(index="ruler", columns="variant", values="value", aggfunc="first", sort=False).reset_index()
    rw.to_csv(OUT / "rulers_three_ways.csv", index=False)
    head = rw[~rw.ruler.str.startswith("clean ruler")]
    L += ["## Rulers three ways", md(head, ".3f"), "", "(clean rulers of the 88 mirror statistics: rulers_three_ways.csv)", "",
          "## Survival of the pre-registered items (verdict per variant; only 'all nulls' is the ruler)", md(wide), ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:4]))
    print(md(piv))
    print(md(head, ".3f"))
    print(md(wide))


if __name__ == "__main__":
    main()
