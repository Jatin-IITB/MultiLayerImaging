"""Documentation ledger (POST-HOC): standing claims with their tier and ratio to the all-13-null ruler, failed or
withdrawn claims, open limitations, and the numbers a report must show.

    python imaging/lobe_ledger.py

Reads committed results (lobe_round5.json, earlier files for scored outcomes); writes results/imaging/LEDGER.md,
LEDGER.csv and lobe_ledger.json. Two standing claims never had a null ruler; they are re-graded here with the R1c
rule (ruler = max(one-pass yardstick, largest |no-change null|), the same three null sets as round 5): the left
neighbour-path phase delay (C4) and the left antennas' reflection-depth change (R3). Nothing else is recomputed.
Bar: >= 3x established, 2-3x sensitive, < 2x not determined. Claims with no ruler say so ('n/a').
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402

from imaging import lobe_c3 as C3  # noqa: E402
from imaging import lobe_round2 as R2  # noqa: E402
from imaging import lobe_round5 as R5  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, ROOT, git_hash  # noqa: E402
from imaging.report_lobe import _t  # noqa: E402

H6, H7, LEFT = R5.H6, R5.H7, "LeftOnly_test_c3"
RES = "results/imaging/"


def last(path):
    return subprocess.run(["git", "log", "-1", "--format=%h", "--", path], capture_output=True, text=True,
                          cwd=ROOT).stdout.strip() or "uncommitted"


def tier(x):
    if x is None or not np.isfinite(x):
        return "n/a"
    return "established" if x >= 3 else ("sensitive" if x >= 2 else "not determined")


def g(rows, **kw):
    return next(r for r in rows if all(r.get(k) == v for k, v in kw.items()))


def rng(xs, f=".2f"):
    return f"{min(xs):{f}}–{max(xs):{f}}"


# ----------------------------------------------------------------------------------------------- re-grades
def names_of(base, extra, ref):
    return [d for d in (R5.SECT0 if base else ()) + tuple(extra) if d != ref]


def c4_regrade(ctx):
    i23 = SL.PAIRS.index((1, 2))
    sel = [int(np.argmin(np.abs(ctx.f - fq * 1e9))) for fq in np.arange(3.30, 3.601, 0.05)]
    out = []
    for rlab, ref in (("H6", H6), ("H7", H7)):
        R = SL.recip(ctx.S[ref])

        def dphi(X):
            return np.degrees(np.angle(SL.recip(X)[i23, sel] / R[i23, sel]))
        left = dphi(ctx.S[LEFT])
        yard = np.max([np.abs(np.degrees(np.angle(SL.recip(ctx.S[a])[i23, sel] / SL.recip(ctx.S[b])[i23, sel])))
                       for a, b in C3.ONE_PASS.values()], 0)
        for vn, base, extra in R5.VARIANTS:
            nul = [np.abs(dphi(ctx.S[d])) for d in names_of(base, extra, ref)]
            rul = np.maximum(yard, np.max(nul, 0))
            out.append(dict(reference=rlab, nulls=vn, LeftOnly_dphi_deg=rng(left, "+.1f"), ruler_deg=rng(rul, ".2f"),
                            ratio_worst_frequency=float(np.min(np.abs(left) / rul))))
    return out


def r3_regrade(ctx):
    out = []
    for rlab, ref in (("H6", H6), ("H7", H7)):
        def rs(d, a):
            return R2.resonance(ctx.f, ctx.S[d][:, a, a])
        for a in (1, 2):
            dd = rs(LEFT, a)[1] - rs(ref, a)[1]
            df = (rs(LEFT, a)[0] - rs(ref, a)[0]) * 1e3
            yd = max(abs(rs(p, a)[1] - rs(q, a)[1]) for p, q in C3.ONE_PASS.values())
            yf = max(abs(rs(p, a)[0] - rs(q, a)[0]) for p, q in C3.ONE_PASS.values()) * 1e3
            for vn, base, extra in R5.VARIANTS:
                nm = names_of(base, extra, ref)
                rd = max([yd] + [abs(rs(d, a)[1] - rs(ref, a)[1]) for d in nm])
                rf = max([yf] + [abs(rs(d, a)[0] - rs(ref, a)[0]) * 1e3 for d in nm])
                out.append(dict(reference=rlab, antenna=f"T{a + 1}", nulls=vn, depth_change_dB=float(dd), depth_ruler_dB=float(rd),
                                depth_ratio=float(abs(dd) / rd), fres_change_MHz=float(df), fres_ruler_MHz=float(rf),
                                fres_ratio=float(abs(df) / rf)))
    return out


# ----------------------------------------------------------------------------------------------- ledger
def build(r5, c4, r3):
    E5 = RES + "lobe_round5.json"
    c5 = last(E5)
    L5 = "this ledger: " + RES + "lobe_ledger.json"
    an = r5["anti3"]
    pp = r5["pairs"]
    ind = r5["independence"]
    b24 = r5["b24"]
    det = r5["detection"]
    mci = r5["mci"]
    r4 = r5["r4"]["all"]
    r4w = r5["r4"]["without rot19"]

    def anti(who, v, ref="H7", m="Tikhonov dS"):
        return g(an, reference=ref, method=m)[f"{who} ({v})"]
    lo_all = [r["LeftOnly (all)"] for r in an]
    ro_all = [r["RightOnly (all)"] for r in an]
    pe = {v: g(pp, reference="H7", method="Tikhonov dS", nulls=v)["exact_exchangeable"] for v in ("all", "without rot19")}

    def mci_r(ref, v):
        r = g(mci, reference=ref, variant=v)
        return max(r["max_sector_ratio"], r["LR_ratio"], r["FB_ratio"])

    def dmin(v, key):
        return min(r[key] for r in det if r["variant"] == v)

    def sep(v):
        out = []
        for ref in ("H7", "H6"):
            rows = [r for r in r5["fit"] if r["reference"] == ref]
            t = min(r["explained_norm"] for r in rows if r["kind"] != "null")
            n = max(r["explained_norm"] for r in rows if r["kind"] == "null" and (v == "all" or r["design"] != "Null_rot19"))
            out.append(t / n)
        return min(out)
    lb = [r for r in b24 if r["set"] == "lobe_B"]
    la = [r for r in b24 if r["set"] == "lobe_A"]
    c4h6 = {v: g(c4, reference="H6", nulls=v)["ratio_worst_frequency"] for v in ("all", "without rot19")}
    c4h7 = {v: g(c4, reference="H7", nulls=v)["ratio_worst_frequency"] for v in ("all", "without rot19")}
    r3d = {v: min(r["depth_ratio"] for r in r3 if r["nulls"] == v) for v in ("all", "without rot19")}
    r3f = {v: max(r["fres_ratio"] for r in r3 if r["nulls"] == v) for v in ("all", "without rot19")}
    fair = {(x["statistic"], x["rule"]): x for x in r4["fair"]["fair"] if x["calibration"] == "T_null_set"}
    best_raw = {k: max((x for (s, rr), x in fair.items() if s != "Born" and rr == k), key=lambda x: (x["exact"], -x["false_alarms"]))
                for k in ("threshold", "gap")}
    loo_b = g(r4["loo"], held_out="family", statistic="Born", kinds="gap/mid")
    loo_bw = g(r4w["loo"], held_out="family", statistic="Born", kinds="gap/mid")
    c6 = {r["reference"]: r for r in r5["alt_c6"]}
    one = {r["statistic"]: r for r in r5["one_sided"]}
    cr = {(r["view"], r["nulls"]): r for r in r5["cr"]}
    rl = {(r["reference"], r["rulers"]): r for r in r5["rulers"]}
    nr_max = max(max(r[s] for s in ("S1 Fr", "S2 TL", "S3 PL", "S4 Oc", "S5 PR", "S6 TR")) for r in r5["nulls_rows"])
    fit_rej = {s["reference"]: s["nulls_rejected"] for s in r5["fit_summary"]}
    nn = {s["reference"]: len([r for r in r5["fit"] if r["reference"] == s["reference"] and r["kind"] == "null"]) for s in r5["fit_summary"]}

    C = []

    def claim(cid, text, ratio, ratio_wo, origin, evidence, commit, depends, tier_text=None):
        C.append(dict(id=cid, claim=text, tier=tier_text or tier(ratio), ratio=ratio, ratio_without_rot19=ratio_wo,
                      origin=origin, evidence=evidence, commit=commit, depends_on=depends))

    E2, c2 = RES + "lobe_round2.md", last(RES + "lobe_round2.md")
    # ---- what the simulation and the model are (measurements; no null ruler)
    claim("F1", "The sensitivity maps come from full 3-D field exports of the healthy head at 3.4, 3.6 and 3.8 GHz; no "
          "cut plane was used.", None, None, "post hoc (review)", E2 + " (R7/G8)", c2, "v2 Normal head geometry", "n/a (measurement)")
    claim("F2", "Each antenna's field peaks at its own position; the port order T4, T3, T2, T1, T6, T5 and 'left = +X' "
          "hold for all six ports.", None, None, "post hoc (review)", E2 + " (G4)", c2, "field exports", "n/a (measurement)")
    claim("F3", "The ring mostly senses the top of the head: 54–70 % of its sensitivity lies above z = 40 mm and at most "
          "4 % below z = 0, so 'lobes' here are vertical wedges of the upper head.", None, None, "post hoc (review)",
          E2 + " (G5)", c2, "field exports; Born sensitivity", "n/a (measurement)")
    claim("F4", "In front of each antenna the field points up–down (along the meridian), not around the ring.", None, None,
          "post hoc (review)", E2 + " (G3)", c2, "field exports", "n/a (measurement)")
    claim("F5", "Tissue properties are fixed at their 3.25 GHz values; real conductivity rises 29–38 % across 3.2–4.2 GHz, "
          "so realism above about 3.3 GHz is limited.", None, None, "post hoc (review)", E2 + " (G7)", c2,
          "HFSS material table (model family)", "n/a (measurement)")
    claim("F6", "The linear (Born) model is poor here: its error is 50–58 % of the symmetric and 92–96 % of the left/right "
          "part of the LeftOnly signal, and the sensitivity maps move 24 % with the export grid.", None, None,
          "post hoc (review)", E2 + " (B14)", c2, "Born kernels (model family)", "n/a (model error)")
    claim("F7", "The Born sector map is not reportable as a localisation method. Values and calls for single sectors change "
          "with the regularisation, the reference and the calibration, depend on depth, and each sector mostly (≈ 80 %) "
          "reflects its own antenna.", None, None, "post hoc (review)", E2 + " (R5, B16, B17, B21, B25)", c2,
          "Born kernels, λ, reference, calibration", "n/a (negative result)")
    # ---- scored pre-registered outcomes
    claim("P1", "Pre-registered blind test (LeftOnly): partly right with the frozen 7-pass reference (left side found, S3 "
          "called, S2 missed) and wrong with the matched 6-pass reference (nothing called); neither reference is more "
          "credible.", None, None, "pre-registered (62709e0), scored", RES + "lobe_blind_outcome.json",
          last(RES + "lobe_blind_outcome.json"), "reference (H7 vs H6); frozen thresholds", "scored: PARTIAL / FAIL")
    claim("P2", "Pre-registered blind test (MCI): nothing called, as predicted.", None, None, "pre-registered (62709e0), scored",
          RES + "lobe_blind_outcome.json", last(RES + "lobe_blind_outcome.json"), "frozen thresholds", "scored: SUCCESS")
    rH6 = rl[("H6", "all")]["RightOnly LR ratio"]
    claim("P3", f"Pre-registered replication: the mirror design (RightOnly, its own mesh) reads right-higher as predicted "
          f"under the rule committed before the file existed (left/right {c6['H6']['LR']:+.2f} against the bar −7.8, phase "
          f"delay on the right path {c6['H6']['phase_3p4']:+.1f}° / {c6['H6']['phase_3p6']:+.1f}° at 3.4 / 3.6 GHz). It "
          f"still replicates with H7 and with the mean healthy mesh as reference.", rH6, rl[("H6", "without rot19")]["RightOnly LR ratio"],
          "pre-registered (0ceb626), scored; ratio post hoc", RES + "rightonly_score.md; " + E5 + " (alt_c6, rulers)",
          last(RES + "rightonly_score.md"), "phase (83 % of the reading); reference H6; Born left/right contrast")
    claim("P4", "Pre-registered blind Test_B reading missed: it called no lobe (truth S2 and S5) and side 'none' (both "
          "sides affected); the ranking it reported put the right pair first, in the right order.", None, None,
          "pre-registered (24aa0c4), scored by the user", RES + "testb_report.md; " + RES + "lobe_round3.md §1",
          last(RES + "testb_report.md"), "frozen threshold 13.81; Born sector values", "scored: MISS")
    claim("P5", f"Pre-registered sign: the left neighbour path (T2–T3) of LeftOnly is delayed, "
          f"{g(c4, reference='H6', nulls='all')['LeftOnly_dphi_deg']}° against H6 at 3.30–3.60 GHz, as the CSF-gap physics "
          f"predicts. Against the 13 nulls the delay is {c4h6['all']:.1f}× the ruler at its worst frequency (H7: {c4h7['all']:.1f}×).",
          c4h6["all"], c4h6["without rot19"], "pre-registered sign (0ceb626); ratio post hoc (this ledger)",
          RES + "lobe_round2.json (c4); " + L5, "documentation baseline (HANDOVER)", "phase; reference H6; no model")
    # ---- post-hoc findings
    claim("H1", f"LeftOnly reads left-higher than right after its own mesh asymmetry is removed; the size is "
          f"{rng(lo_all)}× the largest of the 13 healthy or symmetric re-meshes ({anti('LeftOnly', 'all'):.2f}× with the "
          "frozen method, up to 2.8× with the whitened log).", anti("LeftOnly", "all"), anti("LeftOnly", "without rot19"),
          "post hoc", E5 + " (anti3)", c5, "phase (85–88 %); Born left/right contrast; both references")
    claim("H2", f"RightOnly reads right-higher by {rng(ro_all)}× the same ruler.", anti("RightOnly", "all"),
          anti("RightOnly", "without rot19"), "post hoc", E5 + " (anti3)", c5, "phase; Born left/right contrast; both references")
    claim("H3", f"Both mirror designs lie beyond all 13 nulls, with the predicted opposite signs. If they were just two "
          f"more nulls this would happen with probability {pe['all']:.4f} ({pe['without rot19']:.4f} without rot19).",
          None, None, "post hoc", E5 + " (pairs)", c5, "exchangeability of the 13 nulls; H4", f"rank p {pe['all']:.4f}")
    claim("H4", f"Re-meshing the same healthy head in other orientations does not reproduce its left/right asymmetry: "
          f"rotated meshes differ from H6 about as much as independent draws (q {rng([r['q_rot_vs_H6'] for r in ind])}, "
          f"both signs present). Tested for rotation only, not for mirroring.", None, None, "post hoc (criterion fixed before "
          "rot31/rot43 were loaded)", E5 + " (independence)", c5, "four rotated meshes", "n/a (check)")
    claim("H5", "85–88 % of LeftOnly's left/right reading comes from phase; per-antenna detuning explains at most 20 % of it.",
          None, None, "post hoc", E2 + " (R3, C2)", c2, "phase; reference H6", "n/a (decomposition)")
    claim("H6", f"LeftOnly's left reflection notches get {rng([r['depth_change_dB'] for r in r3 if r['nulls'] == 'all' and r['reference'] == 'H6'], '+.2f')} dB "
          f"shallower (T2, T3, against H6), but healthy re-meshes alone move these notches by up to "
          f"{max(r['depth_ruler_dB'] for r in r3 if r['nulls'] == 'all' and r['reference'] == 'H6'):.2f} dB, so the change is "
          f"{r3d['all']:.1f}× the 13-null ruler at the weaker antenna. The resonance frequency does not move "
          f"(≤ {r3f['all']:.2f}× its ruler).", r3d["all"], r3d["without rot19"],
          "post hoc; ratio this ledger", RES + "lobe_round2.json (r3); " + L5, "documentation baseline (HANDOVER)", "power (reflection); reference")
    v_b = "band mean 3.2-4.2 GHz"
    claim("H7", f"Calibration-free phase ratios of LeftOnly: {cr[(v_b, 'all')]['LeftOnly ≥3× rms']} of 18 exceed 3× the "
          f"null spread, {cr[(v_b, 'all')]['LeftOnly ≥3× max']} of 18 exceed 3× the largest of 13 nulls; with ±0.5 dB "
          "measurement errors none do.", None, None, "post hoc", E5 + " (cr); " + E2 + " (C5)", c5, "phase; measurement model",
          f"n/a (counts: {cr[(v_b, 'all')]['LeftOnly ≥3× rms']}/18 rms rule, {cr[(v_b, 'all')]['LeftOnly ≥3× max']}/18 max rule)")
    claim("H8", "Moderate_lobe's large left/right residual is mesh asymmetry of that file: it halves one pass later.",
          None, None, "post hoc", E2 + " (R1)", c2, "mesh pass", "n/a")
    claim("H9", f"After correcting the front/back bias seen in Mild and Severe, Moderate reads front-heavy (6.3–7.4; truth "
          f"14.6): {rng([r['ratio (all)'] for r in lb])}× the ruler in the better-converged set, "
          f"{rng([r['ratio (all)'] for r in la])}× in the other.", g(lb, method="Tikhonov dS")["ratio (all)"],
          g(lb, method="Tikhonov dS")["ratio (without rot19)"], "post hoc", E5 + " (b24)", c5,
          "Born front/back contrast; set (lobe_B vs lobe_A); rot07 sets the ruler")
    claim("H10", f"MCI shows no sector, left/right or front/back change separable from the healthy re-meshes "
          f"({mci_r('H7', 'all'):.2f}× against H7, {mci_r('H6', 'all'):.2f}× against H6).", mci_r("H7", "all"),
          mci_r("H7", "without rot19"), "post hoc (wording); blind outcome pre-registered", E5 + " (mci)", c5,
          "rulers built without MCI; Born map", "< 2× (nothing separable: the claim)")
    claim("H11", f"Detection without being told where: every lobe design's largest sector value is at least "
          f"{dmin('all', 'max_sector_ratio'):.1f}× the largest healthy re-mesh's, and the part of the data the sector model "
          f"explains is at least {sep('all'):.1f}× larger than any null's. (Told the true sectors, each design has one at "
          f"≥ {dmin('all', 'best_affected'):.1f}× its sector ruler.)", dmin("all", "max_sector_ratio"),
          dmin("without rot19", "max_sector_ratio"), "post hoc", E5 + " (detection, fit)", c5,
          "Born kernels (model family); reference; the parenthesis uses the truth")
    claim("H12", f"The protocol's fit-rejection rule does not test the model; it rejects healthy re-meshes whose "
          f"sector-shaped part is small (against H6: {len(fit_rej['H6'].split(', '))} of {nn['H6']} nulls rejected; against "
          f"H7: {len(fit_rej['H7'].split(', '))} of {nn['H7']}; no lobe design rejected).", None, None, "post hoc",
          E5 + " (fit)", c5, "Born fit", "n/a (characterisation)")
    claim("H13", f"Under identical null-only calibration the Born map beats raw per-antenna phase delay only with a rank "
          f"reading ({fair[('Born', 'gap')]['exact']} vs {best_raw['gap']['exact']} exact sets of {fair[('Born', 'gap')]['n']}, "
          f"{fair[('Born', 'gap')]['false_alarms']} vs {best_raw['gap']['false_alarms']} false alarms); with thresholds "
          f"{fair[('Born', 'threshold')]['exact']} vs {best_raw['threshold']['exact']}.", None, None, "post hoc", E5 + " (r4.fair)",
          c5, "Born kernels; raw phase; calibration choice", "n/a (comparison)")
    claim("H14", f"A rank reading chosen on other designs (never on Test_B) finds {loo_b['hits']} of "
          f"{loo_b['hits'] + loo_b['misses']} affected sectors with {loo_b['false_alarms']} false "
          f"alarms and {loo_b['exact']} of {loo_b['n']} exact sets, and reads Test_B as S2 + S5. Not adopted; not a method "
          "claim (F7).", None, None, "post hoc", E5 + " (r4.loo)", c5, "Born sector values; one head", "n/a (not adopted)")
    claim("H15", "LeftOnly and mirrored RightOnly agree in left/right reading and phase share within the pass-5/pass-6 "
          "twins (≤ 1.08×); whether RightOnly's larger overall level is a mesh-pass effect is undetermined (1.31–2.06× "
          "the largest of 3 twins).", None, None, "post hoc", RES + "lobe_round3.md §9", last(RES + "lobe_round3.md"),
          "three twins only", "undetermined (< 2×)")
    claim("H16", "R31 detection (main session's feature) is defensible on the uniform training designs and fragile on "
          "the lobe Severe and LeftOnly designs.", None, None, "post hoc (check of main's frozen rule)", E2 + " (R4)", c2,
          "main's frozen rule (results/04/frozen_rule.json)", "n/a (main's ruler)")
    claim("H17", "The frozen thresholds were fixed before LeftOnly and MCI existed but tuned on Mild of the same head, so "
          "Mild calls are in-sample.", None, None, "post hoc", E2 + " (B19)", c2, "frozen thresholds", "n/a (provenance)")
    claim("H18", f"The four rotated healthy re-meshes give no frozen call in any method or reference (largest sector "
          f"{nr_max:.2f} against the threshold 13.81).", nr_max / 13.81, None, "post hoc", E5 + " (nulls_rows)", c5,
          "frozen thresholds", f"{nr_max / 13.81:.2f}× the threshold (null behaves as null)")
    claim("H19", f"The matched reference H6 sits apart from the other five healthy meshes on the right-parietal sector, "
          f"left/right and front/back (all five on one side; chance 1/16 each). With the mean healthy mesh as reference "
          f"RightOnly still replicates ({c6['mean of healthy meshes']['verdict']}).", None, None,
          "post hoc (criterion fixed before rot31/rot43 were loaded); not adopted", E5 + " (one_sided, alt_*)", c5,
          "reference H6", "n/a (reference check)")

    W = [("LeftOnly blind prediction (S2 and S3 affected, side left)", "PARTIAL with H7 (S2 missed), FAIL with H6 (nothing called)", "7944508"),
         ("Test_B blind reading (affected none, possible S2; side none)", "user's score: MISS; truth S2 + S5", "ad1bacb"),
         ("Single-sector values and calls are results; the Born map localises lobes", "round 2: they flip with λ, reference and calibration; Born error ≈ signal; ≈ 80 % own antenna", "e4c33d3"),
         ("The frozen 'gain-invariant' log method is gain-invariant", "erratum: it is not; corrected post hoc as 'whitened log'", "2ce6d97"),
         ("LeftOnly left/right is 3.7× the floor (established)", "one fixed max-floor rule (R1c): 1.93× (not determined) to 2.77×", "e4c33d3"),
         ("Cross-ratio phases: 16/22 ≥ 3×", "12/18 distinct (rms), 3/18 (max); with 13 nulls the max rule gives 2/18", "e4c33d3; " + c5),
         ("CRLB 3.3 says single sectors are resolvable", "model error 6–8 and measured SD 12–26 exceed it", "e4c33d3"),
         ("Antenna near field is a 65/35 θ/φ mix", "measured meridional", "e4c33d3"),
         ("Bias-corrected Moderate front/back established in lobe_B (3.2–4.0×)", "rotated null rot07 enters the floor: 2.2–2.8× (sensitive)", "ad1bacb"),
         ("The sector ranking is evidence for the Born pipeline", "raw per-antenna phase delay ranks as well (oracle 0.96 vs 1.00)", "ad1bacb"),
         ("rot19 correctly rejected by the fit rule", "the rule gates on the size of the sector-shaped part; it fires on mesh noise", "79ed048"),
         ("RightOnly's level is not explained by the pass gap", "1.31× / 1.86–2.06× the largest of 3 twins: undetermined", "79ed048"),
         ("Born adds a calibrated level over raw delay", "under identical calibration the advantage depends on the reading rule", "79ed048"),
         ("Pair p ≈ 0.01 (9 nulls) / ≈ 0.007 (11 nulls)", "the product of two rank p's understates p; exact 0.018 / 0.0128; now 0.0095 (13 nulls)", c5),
         ("LeftOnly S2 vs the H7 sector ruler 3.13× (established)", "rot31 raises the S2 ruler: 2.78× (sensitive)", c5),
         ("MCI shows nothing beyond the rulers in any variant", "reworded: nothing separable (< 2×); against H7 1.37× with 11 nulls, 0.93× with 13", c5),
         ("Round 4: null explained norm ≤ 4.3 vs targets ≥ 12.8", "rot31/rot43 reach 5.6 against H7: separation 2.94× → 2.28×", c5),
         ("Left antennas' reflection notch depth changes 0.9–1.0 dB, 3–6× the one-pass yardstick", f"rotated re-meshes move notch depth by up to {max(r['depth_ruler_dB'] for r in r3 if r['nulls'] == 'all'):.2f} dB: {r3d['all']:.1f}× the 13-null ruler (not determined); round 3 did not re-grade it", "documentation baseline (HANDOVER)"),
         ("HANDOVER: new rotated nulls need only REGISTRY and ROT", "round-3 code hard-coded the null count and rot07/rot19; generalised before loading", "ef73da6")]

    O = ["Floor significance: 13 nulls give a single-design rank p of 1/14 at best; p < 0.05 needs ≥ 19 nulls (R1, C3).",
         "Independence of mesh asymmetry under mirroring (as opposed to rotation) is untested; the pair p assumes it (H3, H4).",
         "RightOnly is a pass-5 file and LeftOnly pass 6; the overall-level difference is undetermined with 3 twins (H15).",
         "Fit frequencies other than 3.4/3.6/3.8 GHz: no field exports; kernel interpolation is invalid (B18, B7).",
         "Measurement level: antenna position error and frequency-dependent cable flex are not modelled (C5).",
         "Realistic layer thicknesses (2 mm CSF, 6 mm skull) and the Shehab 2025 Table 6 source: UNVERIFIED (G1).",
         "v1/v2 radius variables, the v2 skull hole and MCI_lobe's Ventricle_CSF: UNVERIFIED, no geometry audit (G2, G6).",
         "AD material provenance and uncertainty: UNVERIFIED (G7).",
         "Sector model against real depth profiles on HFSS data: needs a materials-only S3 design (B16).",
         "Meaning of z_ebg: UNVERIFIED; no imaging result depends on it (G3).",
         "Track A report (results/imaging/report.md, uniform v1/v2 data) has not been re-reviewed under the round-2 standard: UNVERIFIED.",
         "All results come from one head, one mesh family and one material table; 'out of sample' means out-of-design.",
         "Reference choice: H6 is atypical on S5, left/right and front/back; H7 is a different pass; no reference is shown to be more credible.",
         "The user's at-a-glance phase columns: my definitions reproduce the signs (4/4) and spread order (Spearman 0.8), not the magnitudes.",
         "Staging with R21/R32 (0.3a) and the R31 detection margins (0.3b) are the main session's statistics; not computed here.",
         "rot31's unmasked 0.47 dB point (3.85 GHz, a −88 dB notch) is outside the fit frequencies; its effect on band-mean statistics was not isolated.",
         "Items A14–A28 (data handling, statistics, staging of the frozen rule) belong to the main session."]

    N = [("LeftOnly left/right ratio to the all-13-null ruler", f"{rng(lo_all)}×", E5 + " (anti3)", c5),
         ("RightOnly left/right ratio to the same ruler", f"{rng(ro_all)}×", E5 + " (anti3)", c5),
         ("Pair p, both mirror designs beyond all 13 nulls", f"{pe['all']:.4f}", E5 + " (pairs)", c5),
         ("RightOnly replication (committed rule, vs H6)", f"LR {c6['H6']['LR']:+.2f} (bar −7.8): REPLICATED", RES + "rightonly_score.md", last(RES + "rightonly_score.md")),
         ("Share of LeftOnly's left/right reading carried by phase", "85–88 %", E2 + " (R3, C2)", c2),
         ("Left neighbour-path phase delay, 3.30–3.60 GHz (vs H6) and its ratio", f"{g(c4, reference='H6', nulls='all')['LeftOnly_dphi_deg']}°, {c4h6['all']:.1f}×", L5, "documentation baseline (HANDOVER)"),
         ("Pre-registered blind test LeftOnly / MCI", "PARTIAL (H7) / FAIL (H6); MCI SUCCESS", RES + "lobe_blind_outcome.json", last(RES + "lobe_blind_outcome.json")),
         ("Pre-registered blind Test_B", "MISS (ranking S2 > S5 correct)", RES + "testb_report.md", last(RES + "testb_report.md")),
         ("Born model error on LeftOnly (symmetric / left-right part)", "50–58 % / 92–96 %", E2 + " (B14)", c2),
         ("Share of sensitivity above z = 40 mm", "54–70 %", E2 + " (G5)", c2),
         ("Detection margin, whole map / explained part", f"{dmin('all', 'max_sector_ratio'):.1f}× / {sep('all'):.1f}×", E5 + " (detection, fit)", c5),
         ("Bias-corrected Moderate front/back, better-converged set", f"{rng([r['ratio (all)'] for r in lb])}×", E5 + " (b24)", c5),
         ("Rank reading out of sample (hits / false alarms / exact)", f"{loo_b['hits']} / {loo_b['false_alarms']} / {loo_b['exact']} of {loo_b['n']}", E5 + " (r4.loo)", c5),
         ("Born vs raw delay, identical calibration, rank reading (exact sets)", f"{fair[('Born', 'gap')]['exact']} vs {best_raw['gap']['exact']} of {fair[('Born', 'gap')]['n']}", E5 + " (r4.fair)", c5),
         ("Rotated nulls: largest sector vs the frozen threshold", f"{nr_max:.2f} vs 13.81", E5 + " (nulls_rows)", c5)]
    return C, W, O, N, dict(loo_without_rot19=loo_bw)


def write(C, W, O, N, code):
    def cell(x):
        return "n/a" if x is None else (f"{x:.2f}" if isinstance(x, float) else str(x))
    rows = [{**c, "ratio": cell(c["ratio"]), "ratio_without_rot19": cell(c["ratio_without_rot19"])} for c in C]
    cols = ["id", "claim", "tier", "ratio", "ratio_without_rot19", "origin", "evidence", "commit", "depends_on"]
    L = ["# LEDGER — imaging session (lobe phantom)", "",
         f"Generated by `python imaging/lobe_ledger.py` at code `{code}` from committed results. POST-HOC throughout, "
         "except rows marked pre-registered. 'ratio' = ratio to the ruler built from all 13 nulls (9 mirror-symmetric "
         "designs + 4 rotated re-meshes); 'without rot19' drops one of them. Bar: ≥ 3× established, 2–3× sensitive, "
         "< 2× not determined. 'n/a' = the claim has no null ruler (a measurement, a scored outcome or a negative result).", "",
         "**The Born sector map is not reportable as a method** (round 2): values and calls for single sectors change with "
         "the regularisation, the reference and the calibration, and the linear model's error is about the size of the "
         "signal. What survives is detection and the left/right sign, not a sector map.", "",
         "## 1. Claims still standing", "", _t(rows, cols), "",
         "## 2. Failed or withdrawn", ""]
    L += [f"- **{a}** — {b} (`{c}`)" for a, b, c in W]
    L += ["", "## 3. Open limitations (CANNOT TELL / UNVERIFIED)", ""] + [f"- {o}" for o in O]
    L += ["", "## 4. Numbers for the report", "", _t([dict(number=a, value=b, source=c, commit=d) for a, b, c, d in N],
                                                     ["number", "value", "source", "commit"]), ""]
    (OUT / "LEDGER.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(OUT / "LEDGER.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["section"] + cols)
        for r in rows:
            w.writerow(["claim"] + [r[c] for c in cols])
        for a, b, c in W:
            w.writerow(["withdrawn", "", f"{a} -> {b}", "", "", "", "", "", c, ""])
        for o in O:
            w.writerow(["limitation", "", o, "", "", "", "", "", "", ""])
        for a, b, c, d in N:
            w.writerow(["number", "", f"{a}: {b}", "", "", "", "", c, d, ""])


def main():
    r5 = json.loads((OUT / "lobe_round5.json").read_text(encoding="utf-8"))
    ctx = C3.Ctx(20)
    c4, r3 = c4_regrade(ctx), r3_regrade(ctx)
    C, W, O, N, extra = build(r5, c4, r3)
    code = git_hash(ROOT)
    (OUT / "lobe_ledger.json").write_text(json.dumps(dict(code=code, c4=c4, r3=r3, claims=C, **extra), indent=1,
                                                     default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
    write(C, W, O, N, code)
    print("done")


if __name__ == "__main__":
    main()
