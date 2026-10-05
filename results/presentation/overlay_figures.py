"""Presentation figures: the imaging2 estimate drawn on the healthy head (viewing only).

    python results/presentation/overlay_figures.py

Reads results/imaging2/posteriors.json (lobe designs) and results/imaging2/blind/Test_B/{report,truth}.json.
Draws no tissue values: red = brain tissue that the (true or estimated) cortex retreat turns into CSF; an arc
outside the head marks a lobe called affected (P(affected) > 0.5); the error row shows true change the estimate
missed (blue) and estimated change that is not in the truth (amber). Each estimated lobe is drawn at its
posterior MEDIAN retreat; the 90% intervals are wide (results/imaging2/README.md). The hippocampus is not
estimated, so the estimate keeps it healthy. Slices at z <= 20 mm are hatched: below the array's view, drawn by
the lobe model only. Geometry rules as imaging2/phantom.py: spheres, six full-height 60-degree wedges, S1 on T1.
Truth per design as in imaging2/data.py (DESIGNS). Writes four PNGs next to this script.
"""
import json, os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Patch
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap

OUT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("REPO_ROOT", os.path.dirname(os.path.dirname(OUT)))
try:
    from matplotlib import font_manager
    for f in font_manager.findSystemFonts():
        if "Inter" in f:
            font_manager.fontManager.addfont(f)
    if any("Inter" in f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = "Inter"
except Exception:
    pass
INK, BLUE_T = "#14213D", "#2A78D6"
TC = {0: "#F7F6F2", 1: "#E3CDB8", 2: "#EEDDB0", 3: "#D6D3CB", 4: "#C9E2F3", 5: "#CDB9C6", 6: "#EFEAE0", 7: "#E2BFA6"}
CMAP = ListedColormap([TC[i] for i in range(8)])
RED, BLUE, AMBER = np.array([0.80, 0.22, 0.14]), np.array([0.16, 0.47, 0.84]), np.array([0.91, 0.64, 0.24])
HALF, STEP = 95.0, 0.5
ax1 = np.arange(-HALF, HALF + 1e-9, STEP)
X, Y = np.meshgrid(ax1, ax1, indexing="xy")          # image rows: y from -95 (front, top) to +95
AZ_T = [-90.4 + 60 * k for k in range(6)]
ZS = [80, 70, 60, 50, 40, 20, 0]


def sector(Xp, Yp):
    return (np.floor(((np.degrees(np.arctan2(Yp, Xp)) + 120.0) % 360.0) / 60.0)).astype(int) % 6


def labels(z, e, r_hip):
    """0 air, 1 skin, 2 fat, 3 skull, 4 CSF, 5 gray, 6 white, 7 hippocampus (imaging2/phantom.py)."""
    r = np.sqrt(X ** 2 + Y ** 2 + z ** 2)
    sec = sector(X, Y)
    lab = np.zeros(r.shape, int)
    for k in range(6):
        s = sec == k
        rr = r[s]
        l = np.zeros(rr.shape, int)
        for lo, hi, v in [(87.5, 88, 1), (86.5, 87.5, 2), (83.5, 86.5, 3), (0, 83.5, 4),
                          (25, 76 - e[k], 6), (76 - e[k], 83 - e[k], 5), (0, r_hip, 7)]:
            l[(rr >= lo) & (rr < hi)] = v
        lab[s] = l
    return lab


def lost(z, e, r_hip, hip_estimated=True):
    base = labels(z, np.zeros(6), 25.0)
    m = (base >= 5) & (labels(z, np.asarray(e, float), r_hip) == 4)
    if not hip_estimated:
        m &= np.sqrt(X ** 2 + Y ** 2 + z ** 2) >= 25
    return base, m


def frame(ax, z, called=None, hatch=False):
    rs = np.sqrt(max(88 ** 2 - z ** 2, 0))
    rb = np.sqrt(max(83.5 ** 2 - z ** 2, 0))
    for k in range(6):
        a = np.deg2rad(-120 + 60 * k)
        ax.plot([0, rb * np.cos(a)], [0, rb * np.sin(a)], color="#8A8880", lw=0.5, ls=":")
        if called is not None and called[k] and rs > 0:
            t1 = -120 + 60 * k
            ax.add_patch(Arc((0, 0), 2 * (rs + 4), 2 * (rs + 4), theta1=t1 + 3, theta2=t1 + 57, color="#9E2A1A", lw=2.6))
    for k, az in enumerate(AZ_T):
        ax.plot(85 * np.cos(np.deg2rad(az)), 85 * np.sin(np.deg2rad(az)), "s", ms=3.2,
                color="#EB6834" if k == 0 else "#3D4451")
    if hatch:
        ax.add_patch(Circle((0, 0), rs + 1, facecolor="#F7F6F2", alpha=0.72, edgecolor="none"))
        ax.add_patch(Circle((0, 0), rs + 1, facecolor="none", edgecolor="#9AA3B2", hatch="////", lw=0))
    ax.set_xlim(-95, 95); ax.set_ylim(95, -95); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_color("#CFCDC6")


def panel(ax, z, e, r_hip, called, hip_estimated=True, hatch=False, title=None):
    base, m = lost(z, e, r_hip, hip_estimated)
    rgb = CMAP(base)[..., :3]
    rgb[m] = 0.15 * rgb[m] + 0.85 * RED
    ax.imshow(rgb, extent=(-HALF, HALF, HALF, -HALF), interpolation="nearest")
    frame(ax, z, called, hatch)
    if title:
        ax.set_title(title, fontsize=11, color=INK)


def err_panel(ax, z, et, rh, ee, hatch=False):
    base, lt = lost(z, et, rh)
    _, le = lost(z, ee, 25.0, hip_estimated=False)
    rgb = CMAP(base)[..., :3]
    miss, extra = lt & ~le, le & ~lt
    rgb[miss] = 0.15 * rgb[miss] + 0.85 * BLUE
    rgb[extra] = 0.15 * rgb[extra] + 0.85 * AMBER
    ax.imshow(rgb, extent=(-HALF, HALF, HALF, -HALF), interpolation="nearest")
    frame(ax, z, None, hatch)


def legend(fig, y, hatch=True):
    h = [Patch(facecolor=RED, label="brain tissue replaced by CSF (cortex retreat)"),
         Line2D([], [], color="#9E2A1A", lw=2.6, label="lobe called affected"),
         Patch(facecolor="#F7F6F2", edgecolor="#9AA3B2", hatch="////", label="below the array's view: drawn by the model only"),
         Patch(facecolor=BLUE, label="error: true change the estimate missed"),
         Patch(facecolor=AMBER, label="error: estimated change not in the truth")]
    if not hatch:
        h.pop(2)
    fig.legend(handles=h, loc="lower center", ncol=3, fontsize=11, frameon=False, bbox_to_anchor=(0.5, y))


# ---- inputs -----------------------------------------------------------------------------------
post = json.load(open(os.path.join(ROOT, "results", "imaging2", "posteriors.json")))["targets"]
TRUTH = {  # imaging2/data.py DESIGNS: (e per lobe S1..S6 in mm, hippocampus radius in mm)
    "Healthy_p7": ([0] * 6, 25.0), "Mild_p5": ([0, 7.5, 11.5, 0, 11.5, 7.5], 17.5),
    "Moderate_p5": ([11.5, 12.5, 15.5, 0, 15.5, 12.5], 12.5), "Severe_p5": ([15.5, 17.5, 18, 11.5, 18, 17.5], 7.5),
    "LeftOnly_p6": ([0, 7.5, 11.5, 0, 0, 0], 17.5), "MCI_p6": ([0] * 6, 21.25)}


def estimate(t):
    stage = max(t["P_stage"], key=t["P_stage"].get)
    called = [s["P_affected"] > 0.5 for s in t["sectors"]]
    e = [s["e_median"] if c else 0.0 for s, c in zip(t["sectors"], called)]
    return e, called, stage, t["P_stage"][stage]


D = {}
for key, name in [("Healthy_p7", "Healthy"), ("Mild_p5", "Mild"), ("Moderate_p5", "Moderate"),
                  ("Severe_p5", "Severe"), ("LeftOnly_p6", "Left lobes only"), ("MCI_p6", "MCI")]:
    D[name] = (TRUTH[key], estimate(post[key]))
rep = json.load(open(os.path.join(ROOT, "results", "imaging2", "blind", "Test_B", "report.json")))
tru = json.load(open(os.path.join(ROOT, "results", "imaging2", "blind", "Test_B", "truth.json")))
D["Blind test"] = ((tru["e"], tru["r_hip"]), estimate(rep["variants"]["standard_H6"]))


def tcalled(e):
    return [v > 0 for v in e]


# ---- figure A: every design at the ring height -------------------------------------------------
names = ["Healthy", "Mild", "Moderate", "Severe", "Left lobes only", "MCI"]
fig, axs = plt.subplots(3, 6, figsize=(18, 10.2))
for j, n in enumerate(names):
    (et, rh), (ee, called, stage, ps) = D[n]
    panel(axs[0, j], 50, et, rh, tcalled(et), title=n)
    panel(axs[1, j], 50, ee, 25.0, called, hip_estimated=False)
    axs[1, j].set_xlabel(f"estimated stage: {stage}", fontsize=11.5, color=INK)
    err_panel(axs[2, j], 50, et, rh, ee)
axs[0, 0].set_ylabel("TRUE\n(design)", fontsize=12, color=INK)
axs[1, 0].set_ylabel("ESTIMATED\n(from the data)", fontsize=12, color=BLUE_T)
axs[2, 0].set_ylabel("ERROR\n(estimate vs true)", fontsize=12, color=INK)
fig.suptitle("Ring height z = 50 mm: the change drawn on the healthy head (front at top, subject's left on the right)",
             fontsize=13.5, color=INK, y=0.995)
legend(fig, -0.035, hatch=False)
fig.subplots_adjust(left=0.05, right=0.99, top=0.93, bottom=0.07, wspace=0.05, hspace=0.16)
fig.savefig(os.path.join(OUT, "overlay_stages_z50.png"), dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)


# ---- figures B, C: slices --------------------------------------------------------------------
def stack(rows, fname):
    fig, axs = plt.subplots(3 * len(rows), 7, figsize=(10.6, 4.65 * len(rows) + 0.9))
    for i, n in enumerate(rows):
        (et, rh), (ee, called, stage, ps) = D[n]
        for j, z in enumerate(ZS):
            panel(axs[3 * i, j], z, et, rh, tcalled(et),
                  title=(f"z = {z} mm" + (" (ring)" if z == 50 else "")) if i == 0 else None)
            panel(axs[3 * i + 1, j], z, ee, 25.0, called, hip_estimated=False, hatch=z <= 20)
            err_panel(axs[3 * i + 2, j], z, et, rh, ee, hatch=z <= 20)
        axs[3 * i, 0].set_ylabel(f"{n}\ntrue", fontsize=10.5, color=INK)
        axs[3 * i + 1, 0].set_ylabel(f"estimated\n(stage {stage})", fontsize=10.5, color=BLUE_T)
        axs[3 * i + 2, 0].set_ylabel("error", fontsize=10.5, color=INK)
    legend(fig, -0.06 if len(rows) == 1 else -0.045)
    fig.subplots_adjust(left=0.1, right=0.995, top=0.95 if len(rows) > 1 else 0.9, bottom=0.04, wspace=0.04, hspace=0.06)
    fig.savefig(os.path.join(OUT, fname), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


stack(["Mild", "Moderate"], "overlay_slices_a.png")
stack(["Severe", "Left lobes only"], "overlay_slices_b.png")
stack(["Blind test"], "overlay_blind_slices.png")
for n in names + ["Blind test"]:
    (et, rh), (ee, called, stage, ps) = D[n]
    print(f"{n:16s} stage {stage} (P {ps:.2f})  est e {ee}  true e {et}")
