"""Additions after the Test_B reconstruction was committed (c0fafd6). New file only; no module used by
`imaging2.blind` is modified (see results/imaging2/blind/DEVIATIONS.md, item 2).

    python -m imaging2.extras rightonly   # RightOnly_test: mirror / mesh-independence check of LeftOnly
    python -m imaging2.extras testb       # Test_B z = 50 overview in the standard style (no truth row)
    python -m imaging2.extras pres        # *_pres.png copies ("other mesh" -> "repeat simulation")

RightOnly is reconstructed with EXACTLY the LeftOnly fold (training = every lobe design except LeftOnly):
with LeftOnly in training its D6-mirrored copy would be RightOnly's own truth (a look-up).
"""
from __future__ import annotations

import argparse
import copy
import json

import numpy as np

from . import figures as FG
from . import invert as IV
from . import lodo as LO
from . import render as RE
from .data import (CACHE, DESIGNS, FIG, H6, H7, MIRROR, N, OUT, PATH_TYPE, SECTOR_SHORT, TYPE_NAMES, Design,
                   apply_group, git_rev, load_external, load_file, lobe, log_ratio)

RO_FILE = "new_with_slices_RightOnly_test.s6p"
LO_FILE = "new_with_slices_LeftOnly_test_c3.s6p"
OUT_RO = OUT / "rightonly"
SWEEPS, BURN, SEED = 600, 150, 0
NULL_TAGS = ["Healthy_p7", "Healthy_p6_vsH7", "MCI_p6", "Mild_p5", "Mild_p6", "Moderate_p5", "Moderate_p6",
             "Severe_p5", "Severe_p6"]          # the nine mirror-symmetric designs (R1c null)


def register_rightonly():
    if not any(d.file == RO_FILE for d in DESIGNS):
        DESIGNS.append(Design("RightOnly", RO_FILE, "p6", H6, lobe([0, 0, 0, 0, 11.5, 7.5], "Mild", 17.5),
                              "new_with_slices_rep", "RightOnly", "target"))   # project tag keeps it out of training


def _summ(post, L, tag):
    res = post.run(L, n_sweep=SWEEPS, burn=BURN, seed=SEED)
    Ps, marg = IV.sector_marginals(res)
    np.save(CACHE / f"marg_{tag}.npy", marg)
    sm = IV.summarize(Ps=Ps, marg=marg)
    g = float(res["_gof_raw"])
    sm.update(gof=dict(chi2_per_dof=g, tau=float(res["_tau"])), calls=[int(s["P_affected"] > 0.5) for s in sm["sectors"]],
              stage_MAP=max(sm["P_stage"], key=sm["P_stage"].get))
    return sm


def lr_stats(sm):
    e = np.array([s["e_median"] for s in sm["sectors"]])
    p = np.array([s["P_affected"] for s in sm["sectors"]])
    return dict(LR_e=float(e[[1, 2]].mean() - e[[4, 5]].mean()), LR_p=float(p[[1, 2]].mean() - p[[4, 5]].mean()))


def rightonly():
    OUT_RO.mkdir(parents=True, exist_ok=True)
    fold = LO.fit_fold("LeftOnly", verbose=True)                      # identical to the main LeftOnly fold
    register_rightonly()
    S_ro = load_external(RO_FILE)[1]
    S_lo = load_file(LO_FILE)[1]
    std = IV.Posterior(fold["sur"], fold["s_re"], fold["s_im"], fold["ell"], fold["f"], fold["cfg"][0])
    gfr = IV.Posterior(fold["sur"], fold["s_re"], fold["s_im"], fold["ell"], fold["f"], fold["cfg"][0], gain_free=True)
    L_ro6, L_ro7 = log_ratio(S_ro, load_file(H6)[1]), log_ratio(S_ro, load_file(H7)[1])
    L_lo6 = log_ratio(S_lo, load_file(H6)[1])
    runs = {"RightOnly_p6": _summ(std, L_ro6, "RightOnly_p6"),
            "RightOnly_gainfree": _summ(gfr, L_ro6, "RightOnly_gainfree"),
            "RightOnly_vsH7": _summ(std, L_ro7, "RightOnly_vsH7"),
            "LeftOnly_p6_rerun": _summ(std, L_lo6, "LeftOnly_p6_rerun"),
            "LeftOnly_gainfree": _summ(gfr, L_lo6, "LeftOnly_gainfree")}
    # the ninth null design: H6 against H7 (the main run has H7 against H6), with the Healthy fold
    hf = LO.fit_fold("Healthy")
    hpost = IV.Posterior(hf["sur"], hf["s_re"], hf["s_im"], hf["ell"], hf["f"], hf["cfg"][0])
    runs["Healthy_p6_vsH7"] = _summ(hpost, log_ratio(load_file(H6)[1], load_file(H7)[1]), "Healthy_p6_vsH7")
    for k, v in runs.items():
        v.update(lr_stats(v))
        print(f"{k:20s} stage {v['stage_MAP']} ({v['P_stage'][v['stage_MAP']]:.2f}) calls {v['calls']} "
              f"e_med {[s['e_median'] for s in v['sectors']]} fit {v['gof']['chi2_per_dof']:.2f} "
              f"LR_e {v['LR_e']:+.2f} LR_p {v['LR_p']:+.2f}", flush=True)
    # mirror comparison of the reconstructions (LeftOnly mirrored: S2<->S6, S3<->S5)
    post_main = json.loads((OUT / "posteriors.json").read_text())["targets"]
    lo = post_main["LeftOnly_p6"]
    mir = MIRROR
    comp = []
    for k in range(N):
        km = int(np.flatnonzero(mir == k)[0])                          # sector of LeftOnly that maps onto k
        r, l = runs["RightOnly_p6"]["sectors"][k], lo["sectors"][km]
        comp.append(dict(sector=SECTOR_SHORT[k], mirror_of=SECTOR_SHORT[km], P_RO=r["P_affected"], P_LO_mirror=l["P_affected"],
                         e_RO=r["e_median"], e_LO_mirror=l["e_median"], e_RO_int=[r["e_q05"], r["e_q95"]],
                         e_LO_int=[l["e_q05"], l["e_q95"]], e_true=float([0, 0, 0, 0, 11.5, 7.5][k])))
    # data level: RightOnly vs mirrored LeftOnly, against the mesh-pair double-difference ruler
    from .noise import noise_samples
    D = L_ro6 - apply_group(L_lo6, mir)
    ns = noise_samples(())
    data_rows = []
    for t in range(4):
        sel = PATH_TYPE == t
        rms = lambda X, part: float(np.sqrt(np.mean((X[sel].real * 8.686) ** 2)) if part == "amp"  # noqa: E731
                                    else np.sqrt(np.mean(np.degrees(X[sel].imag) ** 2)))
        ruler_amp = float(np.sqrt(np.mean([rms(s, "amp") ** 2 for s in ns]))) * np.sqrt(2)
        ruler_ph = float(np.sqrt(np.mean([rms(s, "ph") ** 2 for s in ns]))) * np.sqrt(2)
        data_rows.append(dict(path_type=TYPE_NAMES[t], RO_minus_mirrorLO_dB=rms(D, "amp"), RO_minus_mirrorLO_deg=rms(D, "ph"),
                              mesh_ruler_dB=ruler_amp, mesh_ruler_deg=ruler_ph,
                              LO_signal_dB=rms(L_lo6, "amp"), LO_signal_deg=rms(L_lo6, "ph")))
    from .data import freq
    fq = freq()
    Llm = apply_group(L_lo6, mir)
    for t, row in enumerate(data_rows):
        sel = PATH_TYPE == t
        row["RO_signal_dB"] = float(np.sqrt(np.mean((L_ro6[sel].real * 8.686) ** 2)))
        row["RO_signal_deg"] = float(np.sqrt(np.mean(np.degrees(L_ro6[sel].imag) ** 2)))
        row["corr_RO_mirrorLO"] = float(np.real(np.vdot(L_ro6[sel].ravel(), Llm[sel].ravel()))
                                        / np.linalg.norm(L_ro6[sel]) / np.linalg.norm(Llm[sel]))
        row["mean_diff_deg"] = float(np.degrees((L_ro6 - Llm)[sel].imag.mean()))
    rings = {"RightOnly_vsH6": (-FG.detuning_values(L_ro6, fq)).tolist(),
             "LeftOnly_mirrored_vsH6": (-FG.detuning_values(Llm, fq)).tolist(),
             "RightOnly_vsH7": (-FG.detuning_values(L_ro7, fq)).tolist()}
    # R1c on the side statistics: null = nine mirror-symmetric designs
    null = {}
    for t in NULL_TAGS:
        null[t] = runs[t] if t in runs else lr_stats(post_main[t])
        if t in runs:
            null[t] = dict(LR_e=runs[t]["LR_e"], LR_p=runs[t]["LR_p"])
    r1c = {}
    for stat in ("LR_e", "LR_p"):
        floor = max(abs(v[stat]) for v in null.values())
        vals = {"LeftOnly_p6": lr_stats(lo)[stat], "RightOnly_p6": runs["RightOnly_p6"][stat],
                "RightOnly_vsH7": runs["RightOnly_vsH7"][stat], "RightOnly_gainfree": runs["RightOnly_gainfree"][stat]}
        r1c[stat] = dict(null={k: v[stat] for k, v in null.items()}, floor=floor,
                         ratios={k: (abs(v) / floor if floor > 0 else float("inf")) for k, v in vals.items()},
                         values=vals,
                         rank_p={k: (1 + sum(abs(n[stat]) >= abs(v) for n in null.values())) / (1 + len(null))
                                 for k, v in vals.items()})
    out = dict(code=git_rev(), fold=dict(cfg=list(fold["cfg"]), train=fold["train_files"]), runs=runs, mirror_comparison=comp,
               data_level=data_rows, detuning_rings=rings, R1c=r1c)
    (OUT_RO / "rightonly.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    (OUT_RO / "rightonly.md").write_text(rightonly_md(out, lo), encoding="utf-8")
    rightonly_figures(runs)
    return out


def bar(x):
    return "established (≥ 3x)" if x >= 3 else "sensitive (2–3x)" if x >= 2 else "not separable (< 2x)"


def rightonly_md(o, lo):
    r = o["runs"]
    L = ["# RightOnly_test: mirror / mesh-independence check of the LeftOnly result", "",
         f"Code {o['code']}. RightOnly reconstructed with the LeftOnly fold (training = {len(o['fold']['train'])} files, "
         f"every lobe design except LeftOnly; RightOnly itself never in training; surrogate {o['fold']['cfg'][0]} / "
         f"λ {o['fold']['cfg'][1]:g}). Reference H6 (same stop rule as LeftOnly) primary; H7 and gain-free alongside. "
         "Truth (supplied, header checked): e = 0/0/0/0/11.5/7.5 mm, Mild in S5, S6.", "",
         "## Reconstructions", "", "| run | stage (P) | lobes called | ê S1…S6 (mm) | fit χ²/dof |", "|---|---|---|---|---|"]
    for k in ["RightOnly_p6", "RightOnly_vsH7", "RightOnly_gainfree", "LeftOnly_p6_rerun", "LeftOnly_gainfree"]:
        v = r[k]
        L.append(f"| {k} | {v['stage_MAP']} ({v['P_stage'][v['stage_MAP']]:.2f}) | "
                 f"{', '.join(SECTOR_SHORT[i] for i in range(N) if v['calls'][i]) or 'none'} | "
                 f"{' / '.join(f'{s['e_median']:.1f}' for s in v['sectors'])} | {v['gof']['chi2_per_dof']:.2f} |")
    L += ["", "## RightOnly against mirrored LeftOnly, sector by sector (primary runs, reference H6)", "",
          "| sector | ← LeftOnly sector | P(aff) RightOnly | P(aff) LeftOnly mirrored | ê RightOnly [90%] | ê LeftOnly mirrored [90%] | e true |",
          "|---|---|---|---|---|---|---|"]
    for c in o["mirror_comparison"]:
        L.append(f"| {c['sector']} | {c['mirror_of']} | {c['P_RO']:.2f} | {c['P_LO_mirror']:.2f} | {c['e_RO']:.1f} "
                 f"[{c['e_RO_int'][0]:.1f}–{c['e_RO_int'][1]:.1f}] | {c['e_LO_mirror']:.1f} [{c['e_LO_int'][0]:.1f}–"
                 f"{c['e_LO_int'][1]:.1f}] | {c['e_true']:.1f} |")
    L += ["", "## Data level: RightOnly − mirror(LeftOnly), rms over paths and 201 frequencies", "",
          "Ruler = rms of the mesh-pair double differences (both meshes of Mild, Moderate, Severe and H7 − H6), √2 × the "
          "one-observation sd, i.e. the expected difference between two independent meshes.", "",
          "| path type | RO − mirror(LO) dB | ruler dB | RO − mirror(LO) ° | ruler ° | band-mean phase RO − mirror(LO) ° | "
          "RightOnly signal dB / ° | LeftOnly signal dB / ° | corr(RO, mirror LO) |", "|---|---|---|---|---|---|---|---|---|"]
    for d in o["data_level"]:
        L.append(f"| {d['path_type']} | {d['RO_minus_mirrorLO_dB']:.3f} | {d['mesh_ruler_dB']:.3f} | "
                 f"{d['RO_minus_mirrorLO_deg']:.2f} | {d['mesh_ruler_deg']:.2f} | {d['mean_diff_deg']:+.2f} | "
                 f"{d['RO_signal_dB']:.2f} / {d['RO_signal_deg']:.1f} | {d['LO_signal_dB']:.2f} / {d['LO_signal_deg']:.1f} | "
                 f"{d['corr_RO_mirrorLO']:.2f} |")
    L += ["", "Model-free ring (neighbour-path phase delay per antenna T1…T6, mean 3.30–3.65 GHz, °; the window is post hoc, "
          "README §6b):", ""]
    for k, v in o["detuning_rings"].items():
        L.append(f"- {k}: " + " / ".join(f"{x:.1f}" for x in v) + f"  (right T5,T6 − left T2,T3: {np.mean(v[4:6]) - np.mean(v[1:3]):+.2f}°)")
    L += ["", "## Side statistics under R1c (null = the nine mirror-symmetric designs; floor = largest |null|)", "",
          "LR_e = mean ê(S2, S3) − mean ê(S5, S6) (mm); LR_p = mean P(affected)(S2, S3) − mean P(affected)(S5, S6).", ""]
    v = o["R1c"]["LR_e"]
    L.append("**LR_e** null: " + ", ".join(f"{k} {x:+.2f}" for k, x in v["null"].items()) + f"; floor {v['floor']:.2f} "
             "(set by Severe_p6, whose depth is undetermined).")
    L += ["", "| design | LR_e (mm) | / floor | bar | rank p |", "|---|---|---|---|---|"]
    for k, x in v["values"].items():
        L.append(f"| {k} | {x:+.2f} | {v['ratios'][k]:.2f} | {bar(v['ratios'][k])} | {v['rank_p'][k]:.2f} |")
    v = o["R1c"]["LR_p"]
    L += ["", f"**LR_p / one-sided calls.** All nine null designs give mirror-symmetric calls: largest |LR_p| = "
          f"{v['floor']:.1e}, i.e. the floor is zero and the R1c ratio is NOT APPLICABLE. Reported instead: is the call "
          "pattern one-sided (affected lobes on one side only)? Null: 0 of 9.", "",
          "| design | lobes called | one-sided | LR_p |", "|---|---|---|---|"]
    runs_ = o["runs"]
    for k, src in [("LeftOnly_p6", runs_["LeftOnly_p6_rerun"]), ("RightOnly_p6", runs_["RightOnly_p6"]),
                   ("RightOnly_vsH7", runs_["RightOnly_vsH7"]), ("RightOnly_gainfree", runs_["RightOnly_gainfree"])]:
        c = src["calls"]
        left, right = bool(c[1] or c[2]), bool(c[4] or c[5])
        L.append(f"| {k} | {', '.join(SECTOR_SHORT[i] for i in range(N) if c[i]) or 'none'} | "
                 f"{'yes (' + ('left' if left else 'right') + ')' if left != right else 'no'} | {v['values'][k]:+.2f} |")
    L.append("")
    return "\n".join(L)


def _post_with(extra):
    post = FG.load_post()
    post["targets"].update(extra)
    return post


def _as_target(v, file, transform=None):
    return dict(v, file=file, transform=transform)


def rightonly_figures(runs):
    nr = RE.noise_rel_at_field_freqs()
    register_rightonly()
    extra = {"RightOnly_p6": _as_target(runs["RightOnly_p6"], RO_FILE),
             "RightOnly_vsH7": _as_target(runs["RightOnly_vsH7"], RO_FILE),
             "RightOnly_gainfree": _as_target(runs["RightOnly_gainfree"], RO_FILE),
             "LeftOnly_gainfree": _as_target(runs["LeftOnly_gainfree"], LO_FILE)}
    titles = {"RightOnly_p6": "RightOnly (replication)", "RightOnly_vsH7": "RightOnly, other healthy ref.",
              "RightOnly_gainfree": "RightOnly, gain-removing", "LeftOnly_gainfree": "LeftOnly, gain-removing",
              "LeftOnly_p6": "LeftOnly (test)"}
    saved = dict(FG.TITLES)
    FG.TITLES.update(titles)
    post = _post_with(extra)
    FG.fig_overview(["LeftOnly_p6", "RightOnly_p6", "LeftOnly_gainfree", "RightOnly_gainfree", "RightOnly_vsH7"], post, nr,
                    "sig", 50.0, fn=OUT_RO / "rightonly_vs_leftonly_sig_z50.png",
                    suptitle="Mirror check: LeftOnly and its replication RightOnly (separate solve), same model, z = 50 mm")
    FG.fig_slices("RightOnly_p6", post, nr, "sig")
    FG.fig_stack(["LeftOnly_p6", "RightOnly_p6"], post, nr, "sig")
    import shutil
    for src, dst in [(FIG / "slices_sig_RightOnly_p6.png", OUT_RO / "slices_sig_RightOnly_p6.png"),
                     (FIG / "stack_sig.png", OUT_RO / "stack_sig_LeftOnly_RightOnly.png")]:
        shutil.move(src, dst)
    (FIG / "slices_sig_RightOnly_p6.npz").unlink(missing_ok=True)
    FG.TITLES.clear()
    FG.TITLES.update(saved)
    # restore the committed main stack figure (it was overwritten by the call above)
    main_post = FG.load_post()
    FG.fig_stack(["Mild_p5", "Moderate_p5", "Severe_p5", "LeftOnly_p6"], main_post, nr, "sig")


# ----------------------------------------------------------------------------------------------
def testb():
    """Test_B in the standard overview style: reconstructed change at z = 50 mm and the lobe bars, no truth row."""
    import matplotlib.pyplot as plt
    from .blind import _bars
    out = OUT / "blind" / "Test_B"
    rep = json.loads((out / "report.json").read_text(encoding="utf-8"))
    nr = RE.noise_rel_at_field_freqs()
    names = list(rep["variants"])
    fig, axs = plt.subplots(2, len(names), figsize=(3.0 * len(names) + 1.0, 6.6), gridspec_kw=dict(height_ratios=[1, 0.75]))
    X, Y, Z, ext = FG.display_grid("axial", 50.0)
    alpha = RE.fade_alpha(RE.snr_at(X, Y, Z, nr) * RE.BAND_FACTOR)
    alpha[np.sqrt(X ** 2 + Y ** 2 + Z ** 2) > 83.5] = 1.0
    for j, n in enumerate(names):
        v = rep["variants"][n]
        M = RE.posterior_maps(np.load(out / f"marg_{n}.npy"), X, Y, Z)
        FG.show_change(axs[0, j], M["sig"] - M["sig0"], ext, "sig", alpha)
        FG.decorate(axs[0, j], "axial", 50.0, labels=(j == 0))
        label = {"standard_H6": "standard (PRIMARY)", "gainfree_H6": "gain-removing", "standard_H7": "standard, other healthy ref."}[n]
        axs[0, j].set_title(f"{label}\nest. {v['stage_MAP']} ({v['P_stage'][v['stage_MAP']]:.2f}) · fit χ²/dof "
                            f"{v['chi2_per_dof']:.2f}", fontsize=9)
        _bars(axs[1, j], v)
    axs[0, 0].set_ylabel("RECONSTRUCTED\nchange", fontsize=10)
    axs[1, 0].set_ylabel("cortex retreat ê (mm)\nP(affected) above", fontsize=8.5)
    cax = fig.add_axes([0.93, 0.45, 0.012, 0.4])
    fig.colorbar(plt.cm.ScalarMappable(cmap=FG.DIV, norm=plt.Normalize(-FG.LIM["sig"], FG.LIM["sig"])), cax=cax,
                 label="change in conductivity σ (S/m)")
    fig.suptitle("BLIND Test_B, z = 50 mm (antenna ring): conductivity change from healthy. Truth withheld; "
                 "same colour scale as all stages", fontsize=10.5)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.86, bottom=0.07, wspace=0.08, hspace=0.18)
    fn = out / "overview_sig_z50_Test_B.png"
    fig.savefig(fn, dpi=120)
    plt.close(fig)
    return fn


# ----------------------------------------------------------------------------------------------
PRES_TITLES = {"Healthy_p7": "Healthy (control:\nrepeat simulation)", "LeftOnly_vsH7": "LeftOnly vs repeat\nhealthy simulation",
               "Mild_p6_shuffled": "Control: Mild data,\npaths shuffled", "LeftOnly_mirrored": "Control: LeftOnly\ndata mirrored",
               "MCI_p6": "MCI\n(hippocampus only)", "LeftOnly_p6": "Left lobes only\n(test)",
               "Mild_p6": "Mild (lobes), repeat simulation", "Moderate_p6": "Moderate (lobes), repeat simulation",
               "Severe_p6": "Severe (lobes), repeat simulation"}


def pres():
    from .make_figures import CONTROLS, PRIMARY
    nr = RE.noise_rel_at_field_freqs()
    saved = copy.deepcopy(FG.TITLES)
    FG.TITLES.update(PRES_TITLES)
    post = FG.load_post()
    made = [FG.fig_overview(PRIMARY, post, nr, "sig", 50.0, fn=FIG / "overview_sig_z50_pres.png"),
            FG.fig_overview(PRIMARY, post, nr, "eps", 50.0, fn=FIG / "overview_eps_z50_pres.png"),
            FG.fig_overview([t for t in CONTROLS if t in post["targets"]], post, nr, "sig", 50.0,
                            fn=FIG / "controls_sig_z50_pres.png",
                            suptitle="Controls: no change (repeat healthy simulation, MCI), mirrored / shuffled data, "
                                     "repeat-simulation reference: conductivity change at z = 50 mm"),
            detuning_pres(PRIMARY, post)]
    FG.TITLES.clear()
    FG.TITLES.update(saved)
    return made


def detuning_pres(tags, post):
    """fig_detuning with the ruler sentence in presentation wording."""
    import matplotlib.pyplot as plt
    from .data import freq
    f = freq()
    fig, axs = plt.subplots(2, len(tags), figsize=(2.7 * len(tags) + 1.0, 6.2))
    for j, tag in enumerate(tags):
        t = post["targets"][tag]
        d = next(x for x in LO.lobe_designs() if x.file == t["file"])
        tr, _ = FG.truth_of(tag, post)
        v = -FG.detuning_values(LO.observation(d), f)
        FG.ring_wedges(axs[0, j], tr.e, FG.SEQ_BLUE, 0, 18, "{:.1f}")
        FG.ring_wedges(axs[1, j], v, FG.SEQ_ORANGE, 0, 18, "{:.1f}°")
        axs[0, j].set_title(FG.TITLES.get(tag, tag), fontsize=10)
    axs[0, 0].text(-150, 0, "TRUE cortex\nretreat e_k (mm)", ha="center", va="center", fontsize=10, rotation=90)
    axs[1, 0].text(-150, 0, "RAW DATA:\nphase delay of the\nneighbour paths (°)", ha="center", va="center",
                   fontsize=10, rotation=90)
    fig.suptitle("Model-free check: per-antenna phase shift of its two neighbour paths, mean over 3.30–3.65 GHz, "
                 "against the healthy scan (front at top, subject's left on the right).\nNo inversion, no training. "
                 "Ruler: two repeat simulations of the healthy head differ by 1.3–1.6° (uniform); MCI by ≤ 0.5°.",
                 fontsize=10.5)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.02, wspace=0.05, hspace=0.12)
    fn = FIG / "detuning_ring_raw_data_pres.png"
    fig.savefig(fn, dpi=130)
    plt.close(fig)
    return fn


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["rightonly", "rightonly-figs", "testb", "pres"])
    a = ap.parse_args()
    if a.cmd == "rightonly-figs":                       # re-render from rightonly.json without re-inverting
        rightonly_figures(json.loads((OUT_RO / "rightonly.json").read_text(encoding="utf-8"))["runs"])
    else:
        print({"rightonly": rightonly, "testb": testb, "pres": pres}[a.cmd]())
