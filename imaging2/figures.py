"""Deck-ready figures (PNG + the arrays behind them, .npz) in results/imaging2/figures/.

View convention (radiological): axial slices seen from below, FRONT (nose, T1) at the TOP,
subject's LEFT on the image RIGHT. Coronal: seen from the front, subject's left on the right.
Sagittal: front on the left.
"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

from . import render as RE  # noqa: E402
from .data import CACHE, FIG, OUT, SECTOR_SHORT, N, git_rev  # noqa: E402
from .invert import E_GRID, STAGES  # noqa: E402
from .phantom import R_CSF, R_SKIN  # noqa: E402

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
SURF = "#fcfcfb"
BLUE, ORANGE = "#2a78d6", "#eb6834"
DIV = LinearSegmentedColormap.from_list("div", ["#104281", "#3987e5", "#9ec5f4", "#f0efec", "#f3b0a6", "#e34948", "#8f1d1c"])
DIV.set_bad(SURF)
LIM = {"sig": 4.0, "eps": 20.0}
UNIT = {"sig": "S/m", "eps": ""}
QNAME = {"sig": "conductivity σ", "eps": "permittivity εr"}
plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.edgecolor": MUTED, "text.color": INK,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "figure.facecolor": SURF,
                     "axes.facecolor": SURF, "savefig.facecolor": SURF})

TITLES = {"Healthy_p7": "Healthy (control: other mesh)", "Mild_p5": "Mild (lobes)", "Mild_p6": "Mild (lobes), 2nd mesh",
          "Moderate_p5": "Moderate (lobes)", "Moderate_p6": "Moderate (lobes), 2nd mesh",
          "Severe_p5": "Severe (lobes)", "Severe_p6": "Severe (lobes), 2nd mesh",
          "LeftOnly_p6": "Left lobes only (test)", "MCI_p6": "MCI (hippocampus only)",
          "LeftOnly_mirrored": "Control: LeftOnly data mirrored", "LeftOnly_rot180": "Control: LeftOnly rotated 180°",
          "Mild_p6_shuffled": "Control: Mild data, paths shuffled", "LeftOnly_vsH7": "LeftOnly vs other healthy mesh",
          "Prior_only": "Prior alone (no data)",
          "LOSO_Mild_p5": "Mild, no Mild-material design in training", "LOSO_Mild_p6": "Mild (2nd mesh), no Mild in training",
          "LOSO_LeftOnly_p6": "LeftOnly, no Mild-material design in training"}


def load_post():
    post = json.loads((OUT / "posteriors.json").read_text())
    fn = OUT / "posteriors_loso.json"
    if fn.exists():
        post["targets"].update(json.loads(fn.read_text())["targets"])
    return post


def truth_of(tag, post):
    from .data import DESIGNS, MIRROR, G
    t = post["targets"][tag]
    d = next(x for x in DESIGNS if x.file == t["file"])
    tr = d.truth
    how = t.get("transform")
    if how in ("mirror", "rot3"):
        import copy
        g = MIRROR if how == "mirror" else G[3]
        tr = copy.deepcopy(tr)
        e, a = np.zeros(N), np.zeros(N, bool)
        e[g], a[g] = d.truth.e, d.truth.affected
        tr.e, tr.affected = e, a
    return tr, how


# ----------------------------------------------------------------------------------------------
def display_grid(view, pos, step=RE.STEP):
    """(X, Y, Z) of a display grid with u right, v up, plus extent."""
    ax = np.arange(-RE.HALF, RE.HALF + 1e-9, step)
    U, V = np.meshgrid(ax, ax, indexing="xy")
    if view == "axial":            # u = x, v = -y (front up)
        X, Y, Z = U, -V, np.full_like(U, pos)
    elif view == "coronal":        # u = x, v = z
        X, Y, Z = U, np.full_like(U, pos), V
    else:                          # sagittal: u = y (front left), v = z
        X, Y, Z = np.full_like(U, pos), U, V
    return X, Y, Z, [ax[0], ax[-1], ax[0], ax[-1]]


def decorate(a, view, pos, labels=True):
    if view == "axial":
        rs = np.sqrt(max(R_SKIN ** 2 - pos ** 2, 0))
        if rs > 0:
            a.add_patch(Circle((0, 0), rs, fill=False, lw=0.6, ec=INK2))
        rb = np.sqrt(max(R_CSF ** 2 - pos ** 2, 0))
        for k in range(N):
            ang = np.radians(-120 + 60 * k)          # sector edges (azimuth); display v = -y
            a.plot([0, rb * np.cos(ang)], [0, -rb * np.sin(ang)], lw=0.5, color=INK2, ls=(0, (2, 2)))
        for k in range(N):
            az = np.radians(-90 + 60 * k)
            u, v = 91 * np.cos(az), -91 * np.sin(az)
            a.plot(u, v, marker="s", ms=4.5, color=ORANGE if k == 0 else INK2, mec=SURF, mew=0.6)
            if labels:
                a.text(u * 1.0, v * 1.0 + (6 if v > 0 else -6), f"T{k + 1}", ha="center", va="center", fontsize=7,
                       color=INK2)
        if labels:
            a.text(-88, -88, "R", fontsize=8, color=INK2, ha="left", va="bottom")
            a.text(88, -88, "L", fontsize=8, color=INK2, ha="right", va="bottom")
    else:
        a.add_patch(Circle((0, 0), R_SKIN, fill=False, lw=0.6, ec=INK2))
        a.axhspan(44, 78, color=ORANGE, alpha=0.08, lw=0)
        a.axhline(48, color=ORANGE, lw=0.6, ls=(0, (3, 2)))
        if labels:
            a.text(-92, 50, "antenna ring", fontsize=7, color=ORANGE, va="bottom")
            if view == "coronal":
                a.text(-88, -88, "R", fontsize=8, color=INK2)
                a.text(84, -88, "L", fontsize=8, color=INK2)
            else:
                a.text(-88, -88, "front", fontsize=8, color=INK2)
                a.text(70, -88, "back", fontsize=8, color=INK2)
    a.add_patch(Circle((0, 0), RE.R_CORE_HATCH if view != "axial" else np.sqrt(max(RE.R_CORE_HATCH ** 2 - pos ** 2, 0)),
                       fill=False, hatch="xxx", ec=MUTED, lw=0.0, alpha=0.5))
    a.set_xlim(-RE.HALF, RE.HALF)
    a.set_ylim(-RE.HALF, RE.HALF)
    a.set_xticks([])
    a.set_yticks([])
    a.set_aspect("equal")


def show_change(a, D, ext, q, alpha=None):
    """Diverging change map; where alpha < 1 the map fades onto a hatched 'not measured' ground."""
    a.add_patch(Rectangle((ext[0], ext[2]), ext[1] - ext[0], ext[3] - ext[2], facecolor=SURF, hatch="////",
                          edgecolor="#d9d8d3", lw=0, zorder=0))
    rgba = DIV((np.clip(D, -LIM[q], LIM[q]) + LIM[q]) / (2 * LIM[q]))
    if alpha is not None:
        rgba[..., 3] = alpha
    return a.imshow(rgba, origin="lower", extent=ext, interpolation="nearest", zorder=1)


def show_head(a, V, ext, q):
    vmax = 70 if q == "eps" else 7
    return a.imshow(V, origin="lower", extent=ext, cmap="gray", vmin=0, vmax=vmax, interpolation="nearest")


def maps_for(tag, post, view, pos, q, noise_rel, step=RE.STEP):
    X, Y, Z, ext = display_grid(view, pos, step)
    marg = np.load(CACHE / f"marg_{tag}.npy")
    est = RE.posterior_maps(marg, X, Y, Z)
    tr, _ = truth_of(tag, post)
    tru = RE.truth_maps(tr, X, Y, Z)
    snr = RE.snr_at(X, Y, Z, noise_rel) * RE.BAND_FACTOR
    alpha = RE.fade_alpha(snr)
    r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
    alpha[r > R_CSF] = 1.0                          # outside the brain the change is exactly 0
    d_est = est[q] - est[q + "0"]
    d_tru = tru[q] - tru[q + "0"]
    return dict(ext=ext, base=est[q + "0"], est_head=est[q], true_head=tru[q], d_est=d_est, d_true=d_tru,
                err=d_est - d_tru, sd=est[q + "_sd"], alpha=alpha, snr=snr)


def fig_slices(tag, post, noise_rel, q="sig", zs=RE.Z_SLICES):
    cols = ["Baseline (healthy scan)", "Estimated change", "Estimated head", "True head (not used)", "Error (est. − true change)"]
    fig, axs = plt.subplots(len(zs), 5, figsize=(13.5, 2.75 * len(zs) + 1.0))
    store = {}
    for i, z in enumerate(zs):
        M = maps_for(tag, post, "axial", z, q, noise_rel)
        store[f"z{int(z)}"] = M
        ext = M["ext"]
        show_head(axs[i, 0], M["base"], ext, q)
        show_change(axs[i, 1], M["d_est"], ext, q, M["alpha"])
        show_head(axs[i, 2], M["base"] + M["d_est"] * M["alpha"], ext, q)
        show_head(axs[i, 3], M["true_head"], ext, q)
        im = show_change(axs[i, 4], M["err"], ext, q)
        axs[i, 4].contour(*np.meshgrid(np.linspace(ext[0], ext[1], M["snr"].shape[1]),
                                       np.linspace(ext[2], ext[3], M["snr"].shape[0])), M["snr"], levels=[1.0],
                          colors=[INK2], linewidths=0.6, linestyles="dashed")
        for j in range(5):
            decorate(axs[i, j], "axial", z, labels=(j == 0))
        axs[i, 0].set_ylabel(f"z = {z:.0f} mm", fontsize=11, color=INK)
    for j, c in enumerate(cols):
        axs[0, j].set_title(c, fontsize=11)
    t = post["targets"][tag]
    ps = t["P_stage"]
    stage = max(ps, key=ps.get)
    fig.suptitle(f"{TITLES.get(tag, tag)}: {QNAME[q]} change reconstructed from the antenna S-parameters\n"
                 f"estimated stage {stage} (P = {ps[stage]:.2f}); leave-one-design-out surrogate inversion; "
                 f"hatched = array has no sensitivity there, x-hatched core = hippocampus not estimable",
                 fontsize=11.5, y=0.995)
    cax = fig.add_axes([0.92, 0.35, 0.012, 0.3])
    sm = plt.cm.ScalarMappable(cmap=DIV, norm=plt.Normalize(-LIM[q], LIM[q]))
    cb = fig.colorbar(sm, cax=cax)
    cb.set_label(f"change in {QNAME[q]} {UNIT[q]}".strip())
    cax2 = fig.add_axes([0.92, 0.70, 0.012, 0.2])
    cb2 = fig.colorbar(plt.cm.ScalarMappable(cmap="gray", norm=plt.Normalize(0, 70 if q == "eps" else 7)), cax=cax2)
    cb2.set_label(f"{QNAME[q]} {UNIT[q]}".strip())
    fig.subplots_adjust(left=0.04, right=0.905, top=0.94, bottom=0.01, wspace=0.03, hspace=0.06)
    fn = FIG / f"slices_{q}_{tag}.png"
    fig.savefig(fn, dpi=110)
    plt.close(fig)
    np.savez_compressed(FIG / f"slices_{q}_{tag}.npz", **{f"{k}_{kk}": v for k, M in store.items()
                                                           for kk, v in M.items() if kk != "ext"})
    return fn


def sector_panel(a, t, tr, title=None):
    xs = np.arange(N)
    a.bar(xs, tr.e, width=0.62, color="none", edgecolor=INK2, lw=1.2, label="true CSF expansion e_k")
    med = np.array([s["e_median"] for s in t["sectors"]])
    lo = np.array([s["e_q05"] for s in t["sectors"]])
    hi = np.array([s["e_q95"] for s in t["sectors"]])
    a.errorbar(xs, med, yerr=[med - lo, hi - med], fmt="o", ms=6, color=BLUE, ecolor=BLUE, elinewidth=1.6,
               capsize=3, label="estimate (median, 90% interval)")
    for k in range(N):
        a.text(k, 23.5, f"{t['sectors'][k]['P_affected']:.2f}", ha="center", fontsize=7.5, color=INK2)
    a.set_xticks(xs)
    a.set_xticklabels([s.replace(" ", "\n") for s in SECTOR_SHORT], fontsize=8)
    a.set_ylim(0, 25.5)
    a.set_ylabel("cortex retreat e (mm)")
    a.grid(axis="y", color="#e6e5e1", lw=0.6)
    a.set_axisbelow(True)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    if title:
        a.set_title(title, fontsize=10)


def fig_overview(tags, post, noise_rel, q="sig", z=50.0, fn=None, suptitle=None):
    fig, axs = plt.subplots(4, len(tags), figsize=(2.75 * len(tags) + 0.9, 11.6),
                            gridspec_kw=dict(height_ratios=[1, 1, 1, 0.8]))
    for j, tag in enumerate(tags):
        M = maps_for(tag, post, "axial", z, q, noise_rel)
        ext = M["ext"]
        show_change(axs[0, j], M["d_true"], ext, q)
        show_change(axs[1, j], M["d_est"], ext, q, M["alpha"])
        show_change(axs[2, j], M["err"], ext, q)
        for i in range(3):
            decorate(axs[i, j], "axial", z, labels=(j == 0))
        t = post["targets"][tag]
        tr, _ = truth_of(tag, post)
        ps = t["P_stage"]
        stage = max(ps, key=ps.get)
        axs[0, j].set_title(f"{TITLES.get(tag, tag)}", fontsize=10.5)
        g = t.get("gof", {}).get("chi2_per_dof", float("nan"))
        if tag == "Prior_only":
            sub = "prior: P(stage) = 0.25 each"
        else:
            flag = "  FIT REJECTED" if g > 3 else ("  (fit poor)" if g > 1.5 else "")
            sub = f"est. {stage} ({ps[stage]:.2f}) · fit χ²/dof {g:.2f}{flag}"
        axs[1, j].set_title(sub, fontsize=8.5, color="#b8461c" if g > 1.5 else INK2)
        sector_panel(axs[3, j], t, tr)
        if j:
            axs[3, j].set_ylabel("")
    for i, lab in enumerate(["TRUE change\n(design, not used)", "RECONSTRUCTED\nchange", "ERROR\n(est. − true)"]):
        axs[i, 0].set_ylabel(lab, fontsize=11, color=INK)
    h, l = axs[3, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.005, 0.215, "P(affected)\nabove bars", fontsize=7.5, color=INK2)
    cax = fig.add_axes([0.935, 0.42, 0.01, 0.4])
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=DIV, norm=plt.Normalize(-LIM[q], LIM[q])), cax=cax)
    cb.set_label(f"change in {QNAME[q]} {UNIT[q]}".strip())
    fig.suptitle(suptitle or f"Axial slice z = {z:.0f} mm (antenna ring): {QNAME[q]} change from healthy, "
                 f"same colour scale for all stages", fontsize=12, y=0.995)
    fig.subplots_adjust(left=0.06, right=0.925, top=0.95, bottom=0.07, wspace=0.08, hspace=0.12)
    fn = fn or FIG / f"overview_{q}_z{int(z)}.png"
    fig.savefig(fn, dpi=120)
    plt.close(fig)
    return fn


def fig_views(tag, post, noise_rel, q="sig"):
    """Coronal (y = 0) and sagittal (x = 0) of truth / estimate / error."""
    fig, axs = plt.subplots(2, 3, figsize=(10.5, 7.4))
    for i, (view, pos, nm) in enumerate([("coronal", 0.0, "Coronal (y = 0)"), ("sagittal", 0.0, "Sagittal (x = 0)")]):
        M = maps_for(tag, post, view, pos, q, noise_rel)
        show_change(axs[i, 0], M["d_true"], M["ext"], q)
        show_change(axs[i, 1], M["d_est"], M["ext"], q, M["alpha"])
        show_change(axs[i, 2], M["err"], M["ext"], q)
        for j in range(3):
            decorate(axs[i, j], view, pos, labels=(j == 0))
        axs[i, 0].set_ylabel(nm, fontsize=11)
    for j, c in enumerate(["True change (not used)", "Reconstructed change", "Error"]):
        axs[0, j].set_title(c)
    fig.suptitle(f"{TITLES.get(tag, tag)}: vertical slices of the {QNAME[q]} change; shaded band = antenna ring "
                 f"height (z 44–78 mm)", fontsize=11)
    cax = fig.add_axes([0.93, 0.25, 0.012, 0.5])
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=DIV, norm=plt.Normalize(-LIM[q], LIM[q])), cax=cax)
    cb.set_label(f"change in {QNAME[q]} {UNIT[q]}".strip())
    fig.subplots_adjust(left=0.05, right=0.92, top=0.9, bottom=0.02, wspace=0.04, hspace=0.06)
    fn = FIG / f"views_{q}_{tag}.png"
    fig.savefig(fn, dpi=120)
    plt.close(fig)
    return fn


def fig_noise(tags, noise_json, noise_rel, q="sig", z=50.0):
    """Rows = conditions (clean + 4 measurement conditions), columns = targets. Each image is the
    posterior-mean change averaged over the K noisy realisations (the expected image); the text
    gives how often the exact affected-lobe pattern and the stage were recovered."""
    import collections
    post = load_post()
    conds = noise_json["conditions"]
    stats = collections.defaultdict(list)
    for r in noise_json["rows"]:
        stats[(r["target"], r["condition"])].append(r)
    fig, axs = plt.subplots(len(conds) + 1, len(tags), figsize=(2.75 * len(tags) + 1.2, 2.75 * (len(conds) + 1) + 0.8))
    X, Y, Z, ext = display_grid("axial", z)
    alpha = RE.fade_alpha(RE.snr_at(X, Y, Z, noise_rel) * RE.BAND_FACTOR)
    alpha[np.sqrt(X ** 2 + Y ** 2 + Z ** 2) > R_CSF] = 1.0
    for j, tag in enumerate(tags):
        tr, _ = truth_of(tag, post)
        true_calls = tr.affected.astype(int).tolist()
        true_stage = tr.tissue_stage if tr.affected.any() else "Healthy"
        for i in range(len(conds) + 1):
            fn = CACHE / (f"marg_{tag}.npy" if i == 0 else f"marg_noisemean_{tag}_{i - 1}.npy")
            M = RE.posterior_maps(np.load(fn), X, Y, Z)
            show_change(axs[i, j], M[q] - M[q + "0"], ext, q, alpha)
            decorate(axs[i, j], "axial", z, labels=False)
            if i > 0:
                rs = stats[(tag, conds[i - 1])]
                ex = np.mean([r["calls"] == true_calls for r in rs])
                st = np.mean([r["stage"] == true_stage for r in rs])
                axs[i, j].text(0, -93, f"exact lobes {ex:.0%} · stage {st:.0%}", ha="center", va="bottom",
                               fontsize=8, color=INK)
        axs[0, j].set_title(TITLES.get(tag, tag), fontsize=10)
    labels = ["no measurement noise"] + [c.replace("noisy+drift gain-free", "noisy + drift,\ngain-free inversion")
                                         .replace("noisy+drift", "noisy + port drift\n(not modelled)")
                                         .replace("typical", "typical noise\n0.25 dB, 2°")
                                         .replace("noisy", "noisy\n0.5 dB, 5°") for c in conds]
    for i, lab in enumerate(labels):
        axs[i, 0].set_ylabel(lab, fontsize=10)
    cax = fig.add_axes([0.93, 0.35, 0.01, 0.3])
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=DIV, norm=plt.Normalize(-LIM[q], LIM[q])), cax=cax)
    cb.set_label(f"change in {QNAME[q]} {UNIT[q]}".strip())
    fig.suptitle(f"Measurement noise on both scans (baseline and follow-up): expected reconstruction over "
                 f"{noise_json['K']} draws, z = {z:.0f} mm.\nPort drift = per-antenna gain/phase change ±0.5 dB, ±5° "
                 f"between the two scans", fontsize=11, y=0.995)
    fig.subplots_adjust(left=0.08, right=0.92, top=0.93, bottom=0.01, wspace=0.05, hspace=0.08)
    fn = FIG / f"noise_{q}_z{int(z)}.png"
    fig.savefig(fn, dpi=115)
    plt.close(fig)
    return fn


SEQ_BLUE = LinearSegmentedColormap.from_list("sb", ["#f0efec", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
SEQ_ORANGE = LinearSegmentedColormap.from_list("so", ["#f0efec", "#fbd3bf", "#f4a07a", "#eb6834", "#b8461c", "#7a2a0c"])


def detuning_values(L, f, band=(3.30e9, 3.65e9)):
    """Model-free per-antenna value: mean phase change (deg) of the antenna's two neighbour paths
    over the band where the left/right phase signal lives (lobe review B7)."""
    from .data import path_index
    sel = (f >= band[0]) & (f <= band[1])
    return np.array([np.degrees(0.5 * (L[path_index(k, (k + 1) % N)].imag[sel].mean()
                                       + L[path_index(k, (k - 1) % N)].imag[sel].mean())) for k in range(N)])


def ring_wedges(a, vals, cmap, vmin, vmax, fmt, r_in=55, r_out=88):
    from matplotlib.patches import Wedge
    for k in range(N):
        az = -90 + 60 * k                                  # data azimuth; display angle = -az (v = -y)
        c = cmap((np.clip(vals[k], vmin, vmax) - vmin) / (vmax - vmin))
        a.add_patch(Wedge((0, 0), r_out, -az - 30, -az + 30, width=r_out - r_in, facecolor=c, edgecolor=SURF, lw=2))
        rm = 0.5 * (r_in + r_out)
        lum = np.dot(c[:3], [0.299, 0.587, 0.114])
        a.text(rm * np.cos(np.radians(-az)), rm * np.sin(np.radians(-az)), fmt.format(vals[k]), ha="center",
               va="center", fontsize=8.5, color=INK if lum > 0.55 else SURF)
    for k in range(N):
        az = np.radians(-90 + 60 * k)
        a.text(99 * np.cos(-az), 99 * np.sin(-az), f"T{k + 1}", ha="center", va="center", fontsize=7.5, color=INK2)
    a.set_xlim(-108, 108)
    a.set_ylim(-108, 108)
    a.set_aspect("equal")
    a.axis("off")


def fig_detuning(tags, post):
    from . import lodo as LO
    from .data import freq
    f = freq()
    fig, axs = plt.subplots(2, len(tags), figsize=(2.7 * len(tags) + 1.0, 6.2))
    for j, tag in enumerate(tags):
        t = post["targets"][tag]
        d = next(x for x in LO.lobe_designs() if x.file == t["file"])
        tr, _ = truth_of(tag, post)
        v = -detuning_values(LO.observation(d), f)
        ring_wedges(axs[0, j], tr.e, SEQ_BLUE, 0, 18, "{:.1f}")
        ring_wedges(axs[1, j], v, SEQ_ORANGE, 0, 18, "{:.1f}°")
        axs[0, j].set_title(TITLES.get(tag, tag), fontsize=10)
    axs[0, 0].text(-150, 0, "TRUE cortex\nretreat e_k (mm)", ha="center", va="center", fontsize=10, rotation=90)
    axs[1, 0].text(-150, 0, "RAW DATA:\nphase delay of the\nneighbour paths (°)", ha="center", va="center",
                   fontsize=10, rotation=90)
    fig.suptitle("Model-free check: per-antenna phase shift of its two neighbour paths, mean over 3.30–3.65 GHz, "
                 "against the healthy scan (front at top, subject's left on the right).\nNo inversion, no training. "
                 "Ruler: the two healthy meshes differ by 1.3–1.6° (uniform); MCI by ≤ 0.5°.", fontsize=10.5)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.84, bottom=0.02, wspace=0.05, hspace=0.12)
    fn = FIG / "detuning_ring_raw_data.png"
    fig.savefig(fn, dpi=130)
    plt.close(fig)
    return fn


def fig_stack(tags, post, noise_rel, q="sig", zs=(80.0, 70.0, 60.0, 50.0, 40.0, 20.0, 0.0)):
    """Rows: for each design, TRUE then RECONSTRUCTED change; columns: axial heights. Same colour scale."""
    nr = len(tags) * 2
    fig, axs = plt.subplots(nr, len(zs), figsize=(1.95 * len(zs) + 1.6, 1.95 * nr + 0.9))
    for j, z in enumerate(zs):
        for i, tag in enumerate(tags):
            M = maps_for(tag, post, "axial", z, q, noise_rel, step=0.75)
            show_change(axs[2 * i, j], M["d_true"], M["ext"], q)
            show_change(axs[2 * i + 1, j], M["d_est"], M["ext"], q, M["alpha"])
            decorate(axs[2 * i, j], "axial", z, labels=False)
            decorate(axs[2 * i + 1, j], "axial", z, labels=False)
        axs[0, j].set_title(f"z = {z:.0f} mm" + (" (ring)" if z == 50 else ""), fontsize=10)
    for i, tag in enumerate(tags):
        t = post["targets"][tag]
        ps = t["P_stage"]
        st = max(ps, key=ps.get)
        axs[2 * i, 0].set_ylabel(f"{TITLES.get(tag, tag)}\nTRUE", fontsize=8.5)
        axs[2 * i + 1, 0].set_ylabel(f"RECONSTRUCTED\nest. {st}, fit {t['gof']['chi2_per_dof']:.2f}", fontsize=8.5,
                                     color=BLUE)
    cax = fig.add_axes([0.93, 0.3, 0.01, 0.4])
    cb = fig.colorbar(plt.cm.ScalarMappable(cmap=DIV, norm=plt.Normalize(-LIM[q], LIM[q])), cax=cax)
    cb.set_label(f"change in {QNAME[q]} {UNIT[q]}".strip())
    fig.suptitle(f"Change in {QNAME[q]} from the healthy baseline, slice by slice (front at top, subject's left on the "
                 f"right; T1 marked orange).\nHatched = the array has no sensitivity there; the reconstruction fades out "
                 f"below the antenna ring.", fontsize=10.5, y=0.997)
    fig.subplots_adjust(left=0.09, right=0.92, top=0.95, bottom=0.005, wspace=0.03, hspace=0.04)
    fn = FIG / f"stack_{q}.png"
    fig.savefig(fn, dpi=110)
    plt.close(fig)
    return fn
