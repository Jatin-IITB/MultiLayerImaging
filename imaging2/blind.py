"""Pre-registered blind reconstruction and scoring (results/imaging2/BLIND_PROTOCOL.md).

Reconstruct (no truth anywhere):
    python -m imaging2.blind run --file new_with_slices_Test_B.s6p --tag Test_B
Score, only after the truth is supplied as results/imaging2/blind/<tag>/truth.json:
    python -m imaging2.blind score --tag Test_B

Everything that decides the outcome is a constant below or in the committed modules; nothing is
tuned on the blind file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from . import invert as IV
from . import lodo as LO
from . import render as RE
from .data import H6, H7, N, OUT, SECTOR_SHORT, git_rev, load_external, load_file, log_ratio

# ---------------------------------------------------------------- pre-registered constants
X_REJECT = 3.0          # chi2/dof above this: reconstruction REJECTED
X_POOR = 1.5            # 1.5 < chi2/dof <= 3: reported, flagged "poor fit: depth not trusted"
SWEEPS, BURN, SEED = 600, 150, 0
FOLD_NAME = "__blind__"  # not a design group -> training = every lobe design, both meshes
VARIANTS = [  # (name, reference file, gain_free, role)
    ("standard_H6", H6, False, "PRIMARY"),
    ("gainfree_H6", H6, True, "secondary"),
    ("standard_H7", H7, False, "secondary"),
]
CALL_P = 0.5
COVER_MIN = 4            # truth inside the 90% interval in >= 4 of 6 sectors
OUT_BLIND = OUT / "blind"


def fit_status(g):
    return "REJECTED" if g > X_REJECT else ("POOR FIT (depth not trusted)" if g > X_POOR else "OK")


def side_text(calls):
    left, right = calls[1] or calls[2], calls[4] or calls[5]
    lr = "left and right" if left and right else "left only" if left else "right only" if right else "neither side"
    fb = ("front and back" if calls[0] and calls[3] else "front (not back)" if calls[0]
          else "back (not front)" if calls[3] else "neither front nor back")
    return lr, fb


# ---------------------------------------------------------------- reconstruction
def run(fname, tag, out=None):
    out = Path(out) if out else OUT_BLIND / tag
    out.mkdir(parents=True, exist_ok=True)
    f, S, mlog, note = load_external(fname)
    fold = LO.fit_fold(FOLD_NAME, verbose=True)
    rep = dict(protocol="results/imaging2/BLIND_PROTOCOL.md", code=git_rev(), file=fname, tag=tag, grid_note=note,
               masked_points=len(mlog), training=fold["train_files"], model=list(fold["cfg"]), ell=fold["ell"],
               X_REJECT=X_REJECT, X_POOR=X_POOR, variants={})
    for name, ref, gf, role in VARIANTS:
        post = IV.Posterior(fold["sur"], fold["s_re"], fold["s_im"], fold["ell"], fold["f"], fold["cfg"][0], gain_free=gf)
        L = log_ratio(S, load_file(ref)[1])
        res = post.run(L, n_sweep=SWEEPS, burn=BURN, seed=SEED)
        Ps, marg = IV.sector_marginals(res)
        np.save(out / f"marg_{name}.npy", marg)
        sm = IV.summarize(Ps=Ps, marg=marg)
        g = float(res["_gof_raw"])
        calls = [s["P_affected"] > CALL_P for s in sm["sectors"]]
        lr, fb = side_text(calls)
        sm.update(role=role, reference=ref, gain_free=gf, chi2_per_dof=g, tau=float(res["_tau"]), fit=fit_status(g),
                  stage_MAP=max(sm["P_stage"], key=sm["P_stage"].get), calls=[int(c) for c in calls],
                  left_right=lr, front_back=fb)
        rep["variants"][name] = sm
        print(f"{name:12s} [{role}] stage {sm['stage_MAP']} ({sm['P_stage'][sm['stage_MAP']]:.2f}) calls {sm['calls']} "
              f"e_med {[s['e_median'] for s in sm['sectors']]} fit {g:.2f} -> {sm['fit']}", flush=True)
    (out / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    (out / "report.md").write_text(report_md(rep), encoding="utf-8")
    figs = blind_figures(tag, rep, S, out)
    print("figures:", *[p.name for p in figs])
    return rep


def report_md(rep):
    L = [f"# Blind reconstruction: {rep['tag']} (`{rep['file']}`)", "",
         f"Protocol `{rep['protocol']}`; code {rep['code']}; training = all {len(rep['training'])} lobe files; "
         f"surrogate {rep['model'][0]} / lambda {rep['model'][1]:g}; ell {rep['ell']}; grid: {rep['grid_note']}; "
         f"glitch-masked points {rep['masked_points']}. **No truth used.**", ""]
    for name, v in rep["variants"].items():
        L += [f"## {name} ({v['role']}; reference {v['reference']}; gain-free {v['gain_free']})", "",
              f"- stage (MAP): **{v['stage_MAP']}**, P = {v['P_stage'][v['stage_MAP']]:.3f} "
              f"(all: {', '.join(f'{k} {p:.3f}' for k, p in v['P_stage'].items())})",
              f"- fit χ²/dof = {v['chi2_per_dof']:.2f} → **{v['fit']}** (likelihood tempered ×{v['tau']:.2f})",
              f"- affected lobes: {', '.join(SECTOR_SHORT[k] for k in range(N) if v['calls'][k]) or 'none'}; "
              f"side: {v['left_right']}; {v['front_back']}", "",
              "| sector | P(affected) | ê median (mm) | 90% interval (mm) |", "|---|---|---|---|"]
        for k, s in enumerate(v["sectors"]):
            L.append(f"| {SECTOR_SHORT[k]} | {s['P_affected']:.2f} | {s['e_median']:.1f} | {s['e_q05']:.1f}–{s['e_q95']:.1f} |")
        L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- figures (blind: no truth)
def _maps(marg, view, pos, q, nr, step=RE.STEP):
    from .figures import display_grid
    from .phantom import R_CSF
    X, Y, Z, ext = display_grid(view, pos, step)
    est = RE.posterior_maps(marg, X, Y, Z)
    alpha = RE.fade_alpha(RE.snr_at(X, Y, Z, nr) * RE.BAND_FACTOR)
    alpha[np.sqrt(X ** 2 + Y ** 2 + Z ** 2) > R_CSF] = 1.0
    return dict(ext=ext, base=est[q + "0"], d=est[q] - est[q + "0"], sd=est[q + "_sd"], alpha=alpha, X=X, Y=Y, Z=Z)


def _bars(a, v, title=None):
    from .figures import BLUE, INK2
    xs = np.arange(N)
    med = np.array([s["e_median"] for s in v["sectors"]])
    lo = np.array([s["e_q05"] for s in v["sectors"]])
    hi = np.array([s["e_q95"] for s in v["sectors"]])
    a.errorbar(xs, med, yerr=[med - lo, hi - med], fmt="o", ms=6, color=BLUE, elinewidth=1.6, capsize=3)
    for k in range(N):
        a.text(k, 23.5, f"{v['sectors'][k]['P_affected']:.2f}", ha="center", fontsize=7.5, color=INK2)
    a.set_xticks(xs)
    a.set_xticklabels([s.replace(" ", "\n") for s in SECTOR_SHORT], fontsize=8)
    a.set_ylim(0, 25.5)
    a.grid(axis="y", color="#e6e5e1", lw=0.6)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    if title:
        a.set_title(title, fontsize=9)


def blind_figures(tag, rep, S, out):
    import matplotlib.pyplot as plt
    from . import figures as FG
    nr = RE.noise_rel_at_field_freqs()
    made = []
    names = list(rep["variants"])
    margs = {n: np.load(out / f"marg_{n}.npy") for n in names}
    prim = names[0]
    # 1. overview: 3 variants x (z 60, 50, 40) + bars
    zs = [60.0, 50.0, 40.0]
    fig, axs = plt.subplots(len(zs) + 1, len(names), figsize=(3.0 * len(names) + 1.2, 3.0 * len(zs) + 2.8),
                            gridspec_kw=dict(height_ratios=[1] * len(zs) + [0.8]))
    for j, n in enumerate(names):
        v = rep["variants"][n]
        for i, z in enumerate(zs):
            M = _maps(margs[n], "axial", z, "sig", nr)
            FG.show_change(axs[i, j], M["d"], M["ext"], "sig", M["alpha"])
            FG.decorate(axs[i, j], "axial", z, labels=(j == 0))
            if j == 0:
                axs[i, j].set_ylabel(f"z = {z:.0f} mm", fontsize=10)
        axs[0, j].set_title(f"{n} [{v['role']}]\nstage {v['stage_MAP']} ({v['P_stage'][v['stage_MAP']]:.2f}) · "
                            f"fit {v['chi2_per_dof']:.2f}: {v['fit'].split(' (')[0]}", fontsize=9)
        _bars(axs[-1, j], v)
    axs[-1, 0].set_ylabel("cortex retreat ê (mm)\nP(affected) above", fontsize=8.5)
    cax = fig.add_axes([0.93, 0.4, 0.012, 0.35])
    fig.colorbar(plt.cm.ScalarMappable(cmap=FG.DIV, norm=plt.Normalize(-FG.LIM["sig"], FG.LIM["sig"])), cax=cax,
                 label="change in conductivity σ (S/m)")
    fig.suptitle(f"BLIND {tag}: reconstructed conductivity change (no truth used).\nFront at top, subject's left on "
                 f"the right; hatched = not measured", fontsize=10.5)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.9, bottom=0.05, wspace=0.08, hspace=0.18)
    made.append(out / f"blind_overview_{tag}.png")
    fig.savefig(made[-1], dpi=120)
    plt.close(fig)
    # 2. slices of the primary variant: baseline | change | head | posterior SD of the change
    for q in ("sig", "eps"):
        zs = RE.Z_SLICES
        fig, axs = plt.subplots(len(zs), 4, figsize=(11.2, 2.75 * len(zs) + 1.0))
        for i, z in enumerate(zs):
            M = _maps(margs[prim], "axial", z, q, nr)
            FG.show_head(axs[i, 0], M["base"], M["ext"], q)
            FG.show_change(axs[i, 1], M["d"], M["ext"], q, M["alpha"])
            FG.show_head(axs[i, 2], M["base"] + M["d"] * M["alpha"], M["ext"], q)
            FG.show_change(axs[i, 3], M["sd"], M["ext"], q, M["alpha"])
            for j in range(4):
                FG.decorate(axs[i, j], "axial", z, labels=(j == 0))
            axs[i, 0].set_ylabel(f"z = {z:.0f} mm", fontsize=11)
        for j, c in enumerate(["Baseline (healthy scan)", "Estimated change", "Estimated head",
                               "Uncertainty (posterior SD)"]):
            axs[0, j].set_title(c, fontsize=11)
        v = rep["variants"][prim]
        fig.suptitle(f"BLIND {tag} ({prim}): {FG.QNAME[q]}; stage {v['stage_MAP']} ({v['P_stage'][v['stage_MAP']]:.2f}), "
                     f"fit {v['chi2_per_dof']:.2f} {v['fit']}; hatched = not measured", fontsize=11, y=0.995)
        cax = fig.add_axes([0.92, 0.35, 0.012, 0.3])
        fig.colorbar(plt.cm.ScalarMappable(cmap=FG.DIV, norm=plt.Normalize(-FG.LIM[q], FG.LIM[q])), cax=cax,
                     label=f"change / SD in {FG.QNAME[q]} {FG.UNIT[q]}".strip())
        fig.subplots_adjust(left=0.05, right=0.905, top=0.95, bottom=0.01, wspace=0.03, hspace=0.06)
        made.append(out / f"blind_slices_{q}_{tag}.png")
        fig.savefig(made[-1], dpi=110)
        plt.close(fig)
    # 3. stack: three variants at seven heights
    zs = RE.Z_SLICES
    fig, axs = plt.subplots(len(names), len(zs), figsize=(1.95 * len(zs) + 1.6, 2.0 * len(names) + 1.0))
    for i, n in enumerate(names):
        for j, z in enumerate(zs):
            M = _maps(margs[n], "axial", z, "sig", nr, step=0.75)
            FG.show_change(axs[i, j], M["d"], M["ext"], "sig", M["alpha"])
            FG.decorate(axs[i, j], "axial", z, labels=False)
            if i == 0:
                axs[i, j].set_title(f"z = {z:.0f} mm", fontsize=10)
        axs[i, 0].set_ylabel(n, fontsize=9)
    fig.suptitle(f"BLIND {tag}: reconstructed conductivity change slice by slice (same colour scale as all stages)",
                 fontsize=10.5)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.88, bottom=0.01, wspace=0.03, hspace=0.05)
    made.append(out / f"blind_stack_{tag}.png")
    fig.savefig(made[-1], dpi=110)
    plt.close(fig)
    # 4. coronal / sagittal of the primary variant
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 4.2))
    for a, (view, nm) in zip(axs, [("coronal", "Coronal (y = 0)"), ("sagittal", "Sagittal (x = 0)")]):
        M = _maps(margs[prim], view, 0.0, "sig", nr)
        FG.show_change(a, M["d"], M["ext"], "sig", M["alpha"])
        FG.decorate(a, view, 0.0, labels=True)
        a.set_title(nm)
    fig.suptitle(f"BLIND {tag} ({prim}): vertical slices of the reconstructed conductivity change", fontsize=10.5)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.85, bottom=0.02, wspace=0.05)
    made.append(out / f"blind_views_{tag}.png")
    fig.savefig(made[-1], dpi=120)
    plt.close(fig)
    # 5. model-free detuning ring (data only), against both healthy meshes
    from .data import freq
    fig, axs = plt.subplots(1, 2, figsize=(6.4, 3.6))
    for a, ref in zip(axs, (H6, H7)):
        vals = -FG.detuning_values(log_ratio(S, load_file(ref)[1]), freq())
        FG.ring_wedges(a, vals, FG.SEQ_ORANGE, 0, 18, "{:.1f}°")
        a.set_title(f"vs {'H6 (6 passes)' if ref == H6 else 'H7 (7 passes)'}", fontsize=9)
    fig.suptitle(f"BLIND {tag}, model-free: neighbour-path phase delay per antenna, 3.30–3.65 GHz\n(ruler: healthy "
                 f"mesh vs mesh 1.3–1.6°, MCI ≤ 0.5°)", fontsize=9.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.78, bottom=0.01)
    made.append(out / f"blind_detuning_{tag}.png")
    fig.savefig(made[-1], dpi=130)
    plt.close(fig)
    return made


# ---------------------------------------------------------------- scoring (after the truth is supplied)
def truth_from_json(tj):
    """truth.json: {"e": [6 mm], "tissue_stage": "Mild" | ..., optional "sector_stage": [6], "affected": [6],
    "csf_stage", "hip_stage", "r_hip"}. affected defaults to e > 0, or to a non-Healthy sector_stage."""
    from .data import lobe
    e = np.asarray(tj["e"], float)
    per = tj.get("sector_stage")
    aff = np.asarray(tj["affected"], bool) if "affected" in tj else (
        (e > 0) | (np.array([s not in (None, "Healthy") for s in per]) if per else False))
    stages = sorted({per[k] for k in range(N) if aff[k]}) if per else ([tj.get("tissue_stage", "Healthy")] if aff.any() else [])
    t = lobe(e, stages[0] if len(stages) == 1 else (tj.get("tissue_stage") or "Healthy"), float(tj.get("r_hip", 25.0)),
             csf=tj.get("csf_stage"), hip=tj.get("hip_stage"), affected=aff)
    if per:
        t.sector_stage = list(per)
    true_stage = "Healthy" if not aff.any() else (stages[0] if len(stages) == 1 else None)   # None = mixed: N/A
    return t, true_stage


def criteria(v, t, true_stage):
    calls = np.array(v["calls"], bool)
    n_calls = int((calls == t.affected).sum())
    c1 = "PASS" if n_calls == 6 else "PARTIAL" if n_calls == 5 else "FAIL"
    c2 = None if true_stage is None else (v["stage_MAP"] == true_stage)
    cov = [s["e_q05"] <= float(t.e[k]) <= s["e_q95"] for k, s in enumerate(v["sectors"])]
    c3 = sum(cov) >= COVER_MIN
    if v["chi2_per_dof"] > X_REJECT:
        overall = "REJECTED"
    elif c1 == "PASS" and c2 in (True, None) and c3:
        overall = "PASS"
    elif c1 in ("PASS", "PARTIAL") and c2 in (True, None):
        overall = "PARTIAL"
    else:
        overall = "FAIL"
    med = np.array([s["e_median"] for s in v["sectors"]])
    aff = t.affected
    return dict(lobe_calls_correct=n_calls, C1_lobes=c1, C2_stage=("N/A (mixed stages)" if c2 is None else c2),
                stage_true=true_stage, C3_coverage=int(sum(cov)), C3_met=c3, fit=v["fit"], overall=overall,
                mae_affected_mm=float(np.mean(np.abs(med[aff] - t.e[aff]))) if aff.any() else 0.0,
                per_sector=[dict(sector=SECTOR_SHORT[k], e_true=float(t.e[k]), affected_true=bool(aff[k]),
                                 P_affected=v["sectors"][k]["P_affected"], call=bool(calls[k]),
                                 e_median=float(med[k]), interval=[v["sectors"][k]["e_q05"], v["sectors"][k]["e_q95"]],
                                 covered=bool(cov[k])) for k in range(N)])


def score(tag, out=None):
    out = Path(out) if out else OUT_BLIND / tag
    rep = json.loads((out / "report.json").read_text(encoding="utf-8"))
    tj = json.loads((out / "truth.json").read_text(encoding="utf-8"))
    t, true_stage = truth_from_json(tj)
    sc = dict(tag=tag, code=git_rev(), truth=tj, primary=VARIANTS[0][0], variants={})
    for name, v in rep["variants"].items():
        sc["variants"][name] = criteria(v, t, true_stage)
    sc["verdict"] = sc["variants"][VARIANTS[0][0]]["overall"]
    (out / "score.json").write_text(json.dumps(sc, indent=1), encoding="utf-8")
    L = [f"# Blind score: {tag} — PRIMARY verdict **{sc['verdict']}**", "",
         f"Truth (supplied after the reconstruction): `{json.dumps(tj)}`", "",
         "| variant | role | stage est / true | lobe calls /6 (C1) | stage (C2) | truth in 90% /6 (C3) | fit | overall |",
         "|---|---|---|---|---|---|---|---|"]
    for name, c in sc["variants"].items():
        v = rep["variants"][name]
        L.append(f"| {name} | {v['role']} | {v['stage_MAP']} / {c['stage_true']} | {c['lobe_calls_correct']} ({c['C1_lobes']}) | "
                 f"{c['C2_stage']} | {c['C3_coverage']} ({'met' if c['C3_met'] else 'not met'}) | "
                 f"{v['chi2_per_dof']:.2f} {c['fit']} | **{c['overall']}** |")
    (out / "score.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    score_figures(tag, rep, t, out)
    return sc


def score_figures(tag, rep, t, out):
    """Truth | reconstruction | error for every variant at z = 60/50/40, after scoring."""
    import matplotlib.pyplot as plt
    from . import figures as FG
    nr = RE.noise_rel_at_field_freqs()
    names = list(rep["variants"])
    zs = [60.0, 50.0, 40.0]
    fig, axs = plt.subplots(len(zs), 1 + 2 * len(names), figsize=(2.6 * (1 + 2 * len(names)) + 1.0, 2.7 * len(zs) + 1.0))
    for i, z in enumerate(zs):
        M0 = _maps(np.load(out / f"marg_{names[0]}.npy"), "axial", z, "sig", nr)
        tru = RE.truth_maps(t, M0["X"], M0["Y"], M0["Z"])
        dt = tru["sig"] - tru["sig0"]
        FG.show_change(axs[i, 0], dt, M0["ext"], "sig")
        FG.decorate(axs[i, 0], "axial", z, labels=True)
        axs[i, 0].set_ylabel(f"z = {z:.0f} mm")
        for j, n in enumerate(names):
            M = _maps(np.load(out / f"marg_{n}.npy"), "axial", z, "sig", nr)
            FG.show_change(axs[i, 1 + 2 * j], M["d"], M["ext"], "sig", M["alpha"])
            FG.show_change(axs[i, 2 + 2 * j], M["d"] - dt, M["ext"], "sig")
            FG.decorate(axs[i, 1 + 2 * j], "axial", z, labels=False)
            FG.decorate(axs[i, 2 + 2 * j], "axial", z, labels=False)
            if i == 0:
                axs[0, 1 + 2 * j].set_title(f"{n}\nreconstructed", fontsize=9)
                axs[0, 2 + 2 * j].set_title(f"{n}\nerror", fontsize=9)
    axs[0, 0].set_title("TRUE (revealed after)", fontsize=9)
    fig.suptitle(f"BLIND {tag} scored: conductivity change, truth vs reconstruction", fontsize=10.5)
    fig.subplots_adjust(left=0.04, right=0.99, top=0.88, bottom=0.01, wspace=0.04, hspace=0.06)
    fn = out / f"blind_scored_{tag}.png"
    fig.savefig(fn, dpi=110)
    plt.close(fig)
    return fn


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "score"])
    ap.add_argument("--file")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.file, a.tag, a.out)
    else:
        score(a.tag, a.out)
