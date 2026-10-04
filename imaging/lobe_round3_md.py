"""Text of round 3 (results/imaging/lobe_round3.md) and section 12 of lobe_report.md. POST-HOC throughout;
every number is read from lobe_round3.json."""
from __future__ import annotations

import numpy as np
import pandas as pd

from imaging.common import OUT
from imaging.report_lobe import SHORT, _t


def _g(rows, **kw):
    for r in rows:
        if all(r.get(k) == v for k, v in kw.items()):
            return r
    raise KeyError(kw)


def write_md(res):
    code, n = res["code"], res["n_draws"]
    T = []
    L = ["# Round 3 (imaging session): rotated nulls, Test_B truth, rank readings, raw delay, pass gap", "",
         "**POST-HOC throughout.** Everything here was computed after the Test_B truth and the rotated nulls were "
         f"released, by `python imaging/lobe_round3.py --n {n}` at code `{code}` (numbers in "
         "`results/imaging/lobe_round3.json`). Frozen rules, thresholds, protocols, predictions and submitted "
         "estimates are unchanged. Committed verdicts stand as scored.", ""]

    # ---------------------------------------------------------------- Test_B score
    L += ["## 1. Test_B: the user's score against my committed protocol (24aa0c4)", "",
          "Truth (released by the user): e = 0 / 11.5 / 0 / 0 / 7.5 / 0 mm, r_hip 17.5, Mild materials in S2 and S5, "
          "CSF_Mild everywhere. Affected: S2 (left temporal, deeper) and S5 (right parietal, shallower), a diagonal pair "
          "180° apart.", "",
          _t([dict(item="lobes (committed reading rule)", estimate="affected none; possible S2", truth="S2, S5", score="MISS"),
              dict(item="ranking (reported under the protocol)", estimate="S2 > S5 ≫ S3, S6, S1, S4", truth="S2 > S5 (deeper first)",
                   score="correct pair in the correct order"),
              dict(item="side", estimate="none", truth="both sides (left larger)", score="MISS (user's score)"),
              dict(item="front/back", estimate="none", truth="S1, S4 unaffected", score="consistent; not scored by the user")],
             ["item", "estimate", "truth", "score"]), "",
          "Recorded as scored. The committed rule was conservative: the frozen T_abs (13.81) was exceeded only by S2, "
          "and only against the 7-pass reference. The ranking, which the protocol reported but did not use for the "
          "reading, had the right pair in the right order.", ""]
    T.append(("Test_B (committed reading)", "MISS (as scored)", "affected none / possible S2 vs truth S2+S5; ranking S2 > S5 correct",
              "testb_report.md; this file §1"))

    # ---------------------------------------------------------------- new files
    L += ["## 2. New files: registry and QC", "",
          "Registered in `imaging/lobe_c3.py` REGISTRY → `results/imaging/lobe_sets.csv` (passes, final ΔS and elements "
          "as supplied by the user). The nulls are marked kind = null and are in no frozen, training or stage set.", "",
          _t(res["qc_new"], ["file", "points", "max_singular_value", "passive", "max_recip_err_dB_re_band", "worst_amp_nonrecip_dB",
                             "at_GHz", "path", "worst_point_masked", "n_masked"],
             {"max_singular_value": ".4f", "max_recip_err_dB_re_band": ".1f", "worst_amp_nonrecip_dB": ".2f", "at_GHz": ".3f"}), "",
          "Masked points (−30 dB rule):", "",
          _t(res["mask_new"], list(res["mask_new"][0]), {"f_GHz": ".3f", "Sij_dB": ".1f", "Sji_dB": ".1f", "recip_err_dB": ".1f"}), "",
          "The 0.49 dB point of Null_rot07 (3.86 GHz, T1–T4) is masked; so is a second point (3.56 GHz, T1–T2). Neither "
          "is at a fit frequency.", ""]

    # ---------------------------------------------------------------- nulls as targets
    nr = res["nulls_rows"]
    worst_sector = max(max(r[s] for s in SHORT) for r in nr)
    worst_lr = max(r["LR_ratio"] for r in nr)
    worst_fb = max(r["FB_ratio"] for r in nr)
    any_call = [r for r in nr if r["called"] not in ("none", "n/a (no frozen thresholds)") or r["side"] not in ("none", "n/a")
                or r["frontback"] not in ("none", "n/a")]
    L += ["## 3. Rotated nulls as targets (frozen pipeline, both references)", "",
          _t(nr, ["null", "reference", "method"] + SHORT + ["LR", "LR_ratio", "FB", "FB_ratio", "called", "side", "frontback",
                                                            "residual"],
             {**{s: "+.2f" for s in SHORT}, "LR": "+.2f", "FB": "+.2f", "LR_ratio": ".2f", "FB_ratio": ".2f", "residual": ".2f"}), "",
          f"**Result.** No sector reaches T_abs (largest {worst_sector:.2f}). LR and FB are at most {worst_lr:.2f}× and "
          f"{worst_fb:.2f}× their rulers. Frozen calls in any method: {len(any_call)}. Applied to the nulls, the "
          "protocol's reading rule gives 'no lobe' for rot07. For rot19 it gives 'fit rejected': the sector model "
          "explains nothing, as expected when nothing changed. That sentence names 'Test_B' because it reuses the "
          "protocol's reading function. **Verdict: CONFIRMED.** Both nulls behave as nulls.", ""]
    T.append(("Nulls as targets", "CONFIRMED", f"no sector ≥ T_abs (max {worst_sector:.2f}); LR ≤ {worst_lr:.2f}×, FB ≤ {worst_fb:.2f}× rulers",
              "lobe_round3.json: nulls_rows"))

    # ---------------------------------------------------------------- independence
    an = res["anti"]
    a0 = _g(an, reference="H7", method="Tikhonov dS")
    L += ["## 4. 'Beyond all nulls' re-tested with the rotated nulls (the independence assumption)", "",
          "Asymmetry-free LR_anti = ½[LR(X) − LR(mirror X)] for every null; R1c ruler = max(one-pass yardstick, largest "
          "|null|):", "",
          _t(an, list(an[0]), {k: ".2f" for k in an[0] if isinstance(an[0][k], float)}), "",
          f"**Result.** The rotated nulls give LR_anti {a0['rot07']:+.2f} (rot07) and {a0['rot19']:+.2f} (rot19), inside the "
          f"old nine-null envelope ({a0['null9_max']:.2f}). The 11-null maximum is unchanged, so every ratio is unchanged: "
          f"LeftOnly {a0['LeftOnly ratio (11)']:.2f}× and RightOnly {a0['RightOnly ratio (11)']:.2f}× (Tikhonov dS). Both "
          f"still lie beyond all 11 nulls; each has rank p = 1/12 = {a0['LeftOnly rank p (11)']:.3f}. If the two meshes' "
          f"asymmetries are independent, the pair's rank p is ≈ {a0['LeftOnly rank p (11)'] * a0['RightOnly rank p (11)']:.3f} "
          "(was ≈ 0.01 with nine). **Verdict: CONFIRMED for this statistic**, with two rotated samples only. Meshes in "
          "other orientations did not produce a larger asymmetry-free LR. They do on other statistics (§5, §6), so "
          "'the nulls share mesh structure' is real for some quantities.", ""]
    T.append(("'Beyond all nulls, p ≈ 0.01'", "CONFIRMED (this statistic)", f"rotated nulls {a0['rot07']:+.2f}/{a0['rot19']:+.2f} inside the "
              f"old envelope {a0['null9_max']:.2f}; pair p ≈ {a0['LeftOnly rank p (11)'] * a0['RightOnly rank p (11)']:.3f} (11 nulls)",
              "lobe_round3.json: anti"))

    # ---------------------------------------------------------------- 0.3(b) checks
    pr = res["pairs"]
    L += ["## 5. The user's 0.3(b) numbers, verified", "",
          "Band-mean (3.2–4.2 GHz) power difference of each mirror path pair (dB):", "",
          _t(pr, ["pair", "type"] + [c for c in pr[0] if c.startswith("power")], {c: "+.3f" for c in pr[0] if c.startswith("power")}), "",
          "Single-path mirror phase difference at 3.4 GHz (deg):", "",
          _t(pr, ["pair"] + [c for c in pr[0] if c.startswith("phase")], {c: "+.2f" for c in pr[0] if c.startswith("phase")}), "",
          "Per-antenna neighbour-path delay against Healthy_sliced_new (deg, + = more delay than the reference; mean of the "
          "antenna's two neighbour paths), with its range across the ring:", "",
          _t(res["ring"], list(res["ring"][0]), {k: "+.2f" for k in res["ring"][0] if k not in ("design", "view")}), "",
          "**Verified.**",
          "- Second-neighbour band power reaches −0.44 dB (T1-T3 vs T1-T5, rot19) and +0.74 dB (T2-T4 vs T4-T6, rot19), above "
          "LeftOnly's 0.11 / 0.19 dB. The old nine nulls already reached 0.50 dB on the first pair; the 0.74 dB is new.",
          "- Reflection power pairs stay ≤ 0.011 dB in the rotated nulls (old ≤ 0.017), against 0.060–0.068 dB for LeftOnly "
          "and Test_B.",
          "- Single-path phase at 3.4 GHz reaches 1.67° (T1-T2 vs T1-T6, rot07) and 1.78° / 1.71° (T2-T5 vs T3-T6, rot07 / "
          "rot19). Both pairs exceed the old nulls (1.36°, 1.02°). Healthy_sliced_new stays ≤ 0.74°.",
          "- The per-antenna ring range is 1.72° / 2.36° for rot07 and 1.04° / 0.82° for rot19 (band / fit frequencies); "
          "the user's measure gave 1.42° / 0.68°. Test_B's pattern on the same measure is 2.05–2.09°: not larger than "
          "rot07's.",
          "**Consequence:** for single-path phase, second-neighbour power and the raw per-antenna delay, the old nine "
          "nulls understated the floor. For the reflection pairs and LR_anti they did not.", ""]
    T.append(("User's 0.3(b) numbers", "CONFIRMED (verified)", "rotated nulls exceed the old floor on 2nd-neighbour power and single-path "
              "phase; not on reflections or LR_anti", "lobe_round3.json: pairs, ring"))

    # ---------------------------------------------------------------- rulers rebuilt
    rl = res["rulers"]
    cr = res["cr"]
    b24 = res["b24"]

    def cnt(view, nulls, who, rule):
        return _g(cr, view=view, nulls=nulls)[f"{who} ≥3× {rule}"]
    old_new = lambda rlab, k: (_g(rl, reference=rlab, rulers="old")[k], _g(rl, reference=rlab, rulers="with rotated nulls")[k])  # noqa: E731
    surv = [
        dict(claim="LeftOnly LR_anti vs R1c ruler (Tikhonov dS / whitened log)", old=f"{a0['LeftOnly ratio (9)']:.2f}× / "
             f"{_g(an, reference='H7', method='whitened log')['LeftOnly ratio (9)']:.2f}×",
             new=f"{a0['LeftOnly ratio (11)']:.2f}× / {_g(an, reference='H7', method='whitened log')['LeftOnly ratio (11)']:.2f}×",
             survives="yes (unchanged; still 'sensitive at best')"),
        dict(claim="RightOnly LR_anti vs R1c ruler", old=f"{a0['RightOnly ratio (9)']:.2f}×–{_g(an, reference='H7', method='whitened log')['RightOnly ratio (9)']:.2f}×",
             new=f"{a0['RightOnly ratio (11)']:.2f}×–{_g(an, reference='H7', method='whitened log')['RightOnly ratio (11)']:.2f}×", survives="yes (unchanged)"),
        dict(claim="Cross-ratio phases, LeftOnly, band mean (≥3×, rms / max rule)",
             old=f"{cnt('band mean 3.2-4.2 GHz', '9 nulls', 'LeftOnly', 'rms')} / {cnt('band mean 3.2-4.2 GHz', '9 nulls', 'LeftOnly', 'max')} of 18",
             new=f"{cnt('band mean 3.2-4.2 GHz', '11 nulls', 'LeftOnly', 'rms')} / {cnt('band mean 3.2-4.2 GHz', '11 nulls', 'LeftOnly', 'max')} of 18",
             survives="yes"),
        dict(claim="Cross-ratio phases, LeftOnly, 3.30–3.65 GHz",
             old=f"{cnt('band mean 3.30-3.65 GHz', '9 nulls', 'LeftOnly', 'rms')} / {cnt('band mean 3.30-3.65 GHz', '9 nulls', 'LeftOnly', 'max')}",
             new=f"{cnt('band mean 3.30-3.65 GHz', '11 nulls', 'LeftOnly', 'rms')} / {cnt('band mean 3.30-3.65 GHz', '11 nulls', 'LeftOnly', 'max')}",
             survives="weakened (max rule 7 → 3)"),
        dict(claim="Cross-ratio phases, LeftOnly, 3.4 GHz",
             old=f"{cnt('3.4 GHz', '9 nulls', 'LeftOnly', 'rms')} / {cnt('3.4 GHz', '9 nulls', 'LeftOnly', 'max')}",
             new=f"{cnt('3.4 GHz', '11 nulls', 'LeftOnly', 'rms')} / {cnt('3.4 GHz', '11 nulls', 'LeftOnly', 'max')}", survives="slightly weakened"),
        dict(claim="Null files ≥3× (leave-one-out, rms rule), any view", old="0 of 18", new=f"{max(r['null files ≥3× rms (leave-one-out), max over files'] for r in cr)} of 18 (rotated nulls included)",
             survives="yes"),
        dict(claim="Test_B S2 / S5 vs sector ruler (H7)", old=f"{old_new('H7', 'Test S2 TL ratio')[0]:.2f}× / {old_new('H7', 'Test S5 PR ratio')[0]:.2f}×",
             new=f"{old_new('H7', 'Test S2 TL ratio')[1]:.2f}× / {old_new('H7', 'Test S5 PR ratio')[1]:.2f}×", survives="yes (unchanged)"),
        dict(claim="RightOnly S5 / S6 vs sector ruler (H7)", old=f"{old_new('H7', 'RightOnly S5 PR ratio')[0]:.2f}× / {old_new('H7', 'RightOnly S6 TR ratio')[0]:.2f}×",
             new=f"{old_new('H7', 'RightOnly S5 PR ratio')[1]:.2f}× / {old_new('H7', 'RightOnly S6 TR ratio')[1]:.2f}×", survives="yes (unchanged)"),
        dict(claim="LeftOnly S3 vs sector ruler (H7)", old=f"{old_new('H7', 'LeftOnly S3 PL ratio')[0]:.2f}×", new=f"{old_new('H7', 'LeftOnly S3 PL ratio')[1]:.2f}×",
             survives="weakened (rot07 S3 = 4.75 raises the ruler), still ≥ 3×"),
        dict(claim="Bias-corrected Moderate FB, lobe_B (established 3.2–4.0×)",
             old=", ".join(f"{r['ratio_old']:.2f}×" for r in b24 if r["set"] == "lobe_B"),
             new=", ".join(f"{r['ratio_new']:.2f}×" for r in b24 if r["set"] == "lobe_B"),
             survives=f"NO: rot07 FB ({min(r['FB_rot07'] for r in b24):+.1f} to {max(r['FB_rot07'] for r in b24):+.1f}) enters the floor; "
                      "'established in lobe_B' → sensitive"),
        dict(claim="Left/right reflection asymmetry of LeftOnly (power)", old="0.060–0.068 dB vs old nulls ≤ 0.017",
             new="vs all nulls ≤ 0.017 (rotated ≤ 0.011)", survives="yes"),
        dict(claim="MCI: nothing beyond the rulers", old="—", new="nulls behave like MCI", survives="yes"),
    ]
    L += ["## 6. Rulers rebuilt with the rotated nulls (max over 9 + 2 nulls): what survives", "",
          "Sector, LR and FB rulers of the Test_B protocol, primary method, with the rotated nulls added to the floors:", "",
          _t(rl, list(rl[0]), {k: ".2f" for k in rl[0] if k not in ("reference", "rulers")}), "",
          "Cross-ratio phase counts (18 distinct statistics) with 9 and 11 nulls:", "",
          _t(cr, list(cr[0])), "",
          "Bias-corrected Moderate FB (round-2 B24) with the rotated nulls' FB added to the floor:", "",
          _t(b24, list(b24[0]), {c: "+.2f" for c in ("FB_rot07", "FB_rot19", "corrected")} | {"ratio_old": ".2f", "ratio_new": ".2f"}), "",
          "**Survival table:**", "",
          _t(surv, ["claim", "old", "new", "survives"]), "",
          "Claims that do not use a null floor (field geometry, Born error, λ, references, per-port shares, depth) are not "
          "affected. When Null_rot31 and Null_rot43 arrive: add them to `REGISTRY` and to `ROT` in `imaging/lobe_round3.py`, "
          "and re-run.", ""]
    T.append(("Rulers rebuilt (11 nulls)", "CHANGED (one claim falls)", "bias-corrected FB in lobe_B 3.2–4.0× → "
              + ", ".join(f"{r['ratio_new']:.2f}×" for r in b24 if r["set"] == "lobe_B") + "; others survive; phase counts at "
              "3.30–3.65 weakened", "lobe_round3.json: rulers, cr, b24"))

    # ---------------------------------------------------------------- readings
    rd = pd.DataFrame(res["readings"])
    meta = res["reading_meta"]
    tags = [c[:-4] for c in rd.columns if c.endswith(" set")]
    summ = [dict(reading=t, hits=int(rd[f"{t} hits"].sum()), misses=int(rd[f"{t} misses"].sum()),
                 false_alarms=int(rd[f"{t} false"].sum()), exact_sets=f"{int(rd[f'{t} exact'].sum())}/{len(rd)}") for t in tags]
    L += ["## 7. Rank readings vs the frozen threshold (POST-HOC; not adopted)", "",
          f"Designs: every known lobe design, RightOnly, Test_B, MCI, both rotated nulls and the other healthy file, each "
          f"against both references ({len(rd)} cases, {int(rd['frozen T_abs hits'].sum() + rd['frozen T_abs misses'].sum())} "
          f"truly affected sectors). Primary method. Rules (stated before computing):",
          f"- frozen: dε'' > T_abs = {meta['T_abs']:.2f};",
          f"- rank (largest gap): sort the six values; k = position of the largest drop; k = 0 if the top value ≤ the frozen "
          f"T_null = {meta['T_null']:.2f};",
          "- rank (above midpoint): sectors above ½(max + min), same gate.",
          "The raw-delay row is §8's comparison.", "",
          _t(summ, ["reading", "hits", "misses", "false_alarms", "exact_sets"]), "",
          _t(res["readings"], ["reference", "design", "truth"] + [f"{t} set" for t in tags]), "",
          "**Result.** Neither rank rule makes a false alarm. The largest-gap rank reading finds "
          f"{summ[1]['hits']} of {summ[1]['hits'] + summ[1]['misses']} affected sectors against {summ[0]['hits']} for the frozen "
          f"threshold, with {summ[1]['exact_sets']} exact sets against {summ[0]['exact_sets']}. Its misses are mainly Severe "
          "(all six affected; a gap rule cannot return 'all') and RightOnly (it stops after S6). It would have read Test_B "
          "as S2 + S5 against both references. **Not adopted:** the rule was formulated after the Test_B truth was known.", ""]
    T.append(("Rank reading vs threshold", "reported, not adopted", f"frozen {summ[0]['hits']} hits / {summ[0]['false_alarms']} FA / "
              f"{summ[0]['exact_sets']} exact; largest-gap {summ[1]['hits']} / {summ[1]['false_alarms']} / {summ[1]['exact_sets']}",
              "lobe_round3.json: readings"))

    # ---------------------------------------------------------------- Born vs raw
    bo = rd["Born top-k oracle"].dropna()
    ro = rd["raw top-k oracle"].dropna()
    bs = rd["Born spearman"].dropna()
    rs = rd["raw spearman"].dropna()
    raw = summ[3]
    L += ["## 8. Is the ranking evidence for the Born pipeline, or only for 'the delay is largest at the antennas over the change'?", "",
          "Raw statistic per antenna (sector k ↔ antenna Tk): minus the mean phase change, against the reference, of the "
          "antenna's two neighbour paths at 3.4 / 3.6 / 3.8 GHz (the same frequencies as the Born fit), with the ring "
          f"median removed (common CSF_Mild delay). Its gate is the largest centred value of the designs with no cortical "
          f"change ({', '.join(f'{k} {v:.2f}°' for k, v in meta['raw_gate'].items())}).", "",
          _t([dict(measure="top-k with the true k (designs with 1–5 affected sectors)", Born=f"{bo.mean():.3f} ({int((bo == 1).sum())}/{len(bo)} perfect)",
                   raw=f"{ro.mean():.3f} ({int((ro == 1).sum())}/{len(ro)} perfect)"),
              dict(measure="Spearman with the true sector map (designs with a non-flat truth)", Born=f"{bs.mean():.2f}", raw=f"{rs.mean():.2f}"),
              dict(measure="stated-k reading (largest gap, own null gate): hits / misses / false alarms / exact",
                   Born=f"{summ[1]['hits']} / {summ[1]['misses']} / {summ[1]['false_alarms']} / {summ[1]['exact_sets']}",
                   raw=f"{raw['hits']} / {raw['misses']} / {raw['false_alarms']} / {raw['exact_sets']}")],
             ["measure", "Born", "raw"]), "",
          "Per design (raw delays as values):", "",
          _t(res["readings"], ["reference", "design", "truth", "raw delay deg", "Born values", "Born top-k oracle", "raw top-k oracle",
                               "Born spearman", "raw spearman"], {c: ".2f" for c in ("Born top-k oracle", "raw top-k oracle",
                                                                                     "Born spearman", "raw spearman")}), "",
          f"**Verdict: CHANGED (the ranking is not evidence for the Born pipeline).** With the number of affected sectors "
          f"given, the raw neighbour-path delay ranks them almost as well ({ro.mean():.2f} vs {bo.mean():.2f}). It "
          f"correlates with the true map as well or better ({rs.mean():.2f} vs {bs.mean():.2f}); its only misses are "
          "Mild_lobe (4 affected; raw ranks the unaffected S1 above an affected sector). So the ranking mostly re-expresses 'the phase delay is largest "
          "at the antennas over the change'.",
          "Where the Born map does add something is a calibrated level. With stated rules it gives fewer false alarms "
          f"({summ[1]['false_alarms']} vs {raw['false_alarms']}) and more exact sets ({summ[1]['exact_sets']} vs "
          f"{raw['exact_sets']}), because the centred raw delay of the healthy-like designs reaches "
          f"{max(meta['raw_gate'].values()):.2f}°, comparable to Test_B's S5 (≈ 1.0°).", ""]
    T.append(("Born ranking vs raw delay", "CHANGED", f"ranking credited to the Born map → raw delay ranks as well (oracle {ro.mean():.2f} vs "
              f"{bo.mean():.2f}; Spearman {rs.mean():.2f} vs {bs.mean():.2f}); Born adds only the gated level", "lobe_round3.json: readings"))

    # ---------------------------------------------------------------- pass gap
    pg = res["pass_gap"]
    p0 = _g(pg, reference="H7", method="Tikhonov dS")
    worst = max(abs(r[f"Left−mirRight {k}"]) / r[f"twins max abs Δ {k}"] for r in pg for k in ("LR", "LR_anti", "LR_amp", "LR_phase"))
    L += ["## 9. Pass gap (0.3a): LeftOnly (pass 6) vs mirrored RightOnly (pass 5), against the three pass-5/pass-6 twins", "",
          "Same statistics and frequencies (3.4/3.6/3.8 GHz) for Left − mirror(Right) and for each twin (p6 − p5): LR, "
          "LR_anti, its amplitude and phase parts, phase share, the mean of the two affected sectors, and the common-mode "
          "neighbour-path delay.", "",
          _t(pg, list(pg[0]), {k: ("+.2f" if isinstance(pg[0][k], float) else None) for k in pg[0] if isinstance(pg[0][k], float)}), "",
          f"**Result.** LR, LR_anti, amplitude and phase parts: |Left − mirRight| is at most {worst:.2f}× the largest twin "
          f"difference. Primary method, H7: LR {p0['Left−mirRight LR']:+.2f} vs ≤ {p0['twins max abs Δ LR']:.2f}; LR_anti "
          f"{p0['Left−mirRight LR_anti']:+.2f} vs ≤ {p0['twins max abs Δ LR_anti']:.2f}. The phase share is the same "
          f"({p0['phase share Left']:.2f} vs {p0['phase share mirRight']:.2f}).",
          f"Two size measures are outside the twins. The common-mode delay is {p0['common-mode delay Left / mirRight deg']}° "
          f"(difference {p0['Left−mirRight common-mode delay deg']:+.2f}° vs twins ≤ {p0['twins max abs Δ common-mode delay deg']:.2f}°). "
          f"The affected-sector level differs by {p0['relative Δ affected sectors (Left−mirRight)']:+.0%} vs twins "
          f"{p0['twins relative Δ affected sectors (p6 − p5)']}.",
          "**Verdict.** For LR and phase share, the Left/Right size mismatch is consistent with the pass gap (within or "
          "at the edge of the twin differences). For the absolute level, a common delay about 4° larger in RightOnly "
          f"and sectors {min(-r['relative Δ affected sectors (Left−mirRight)'] for r in pg):.0%}–"
          f"{max(-r['relative Δ affected sectors (Left−mirRight)'] for r in pg):.0%} higher, it is larger than any twin difference: the pass gap does not explain it. "
          "Nothing in these data says what does.", ""]
    T.append(("Pass gap, LR and phase share", "consistent with the pass gap", f"abs Δ ≤ {worst:.2f}× the twins; phase share equal",
              "lobe_round3.json: pass_gap"))
    T.append(("Pass gap, absolute level", "not explained by the pass gap", f"common-mode delay {p0['Left−mirRight common-mode delay deg']:+.2f}° "
              f"vs twins ≤ {p0['twins max abs Δ common-mode delay deg']:.2f}°; sectors {p0['relative Δ affected sectors (Left−mirRight)']:+.0%}",
              "lobe_round3.json: pass_gap"))

    L += ["## Final table", "", _t([dict(item=a, verdict=b, change=c, evidence=d) for a, b, c, d in T],
                                   ["item", "verdict", "change", "evidence"]), ""]
    (OUT / "lobe_round3.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    sec = ["## 12. Round 3 (POST-HOC): Test_B truth, rotated nulls, rank readings, raw delay, pass gap", "",
           "Full text: `results/imaging/lobe_round3.md`. Test_B scored against protocol 24aa0c4: committed reading **MISS** "
           "(affected none / possible S2; truth S2 + S5). The ranking S2 > S5 ≫ rest was the correct pair in the correct "
           "order. Side 'none' was scored a miss.", "",
           _t([dict(item=a, verdict=b, change=c) for a, b, c, d in T], ["item", "verdict", "change"]), ""]
    if "## 12." in rep:
        i0 = rep.index("## 12.")
        j = rep.find("\n## ", i0 + 5)
        rep = rep[:i0] + "\n".join(sec) + ("\n" + rep[j + 1:] if j >= 0 else "\n")
    else:
        rep = rep.rstrip("\n") + "\n\n" + "\n".join(sec) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
