"""Worked numbers behind the E-field plots (healthy uniform head, 3.6 GHz). Viewing only.

    python results/efield/efield_numbers.py

Prints every number step by step (geometry, tissue loss, the 5.6 dB/cm slope, the -33/-57 dB half-way
values, the path sensitivity) and writes efield_routes_explained.png next to this script.
Needs data/fields/E_Normal_T1_3p6GHz_wide.fld (git-ignored). Nothing here feeds any analysis.
"""
import os, re
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from scipy.ndimage import map_coordinates

OUT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(OUT))


def load(path):
    hdr = open(path).readline()
    mn = [float(v) for v in re.findall(r"Min: \[(-?\d+)mm (-?\d+)mm (-?\d+)mm\]", hdr)[0]]
    st = float(re.findall(r"Grid Size: \[(\d+)mm", hdr)[0])
    d = pd.read_csv(path, sep=r"\s+", skiprows=2, header=None, engine="c", na_values=["Nan"], dtype=float).to_numpy()
    n = round(len(d) ** (1 / 3)); assert n ** 3 == len(d)
    return (d[:, 3::2] + 1j * d[:, 4::2]).reshape(n, n, n, 3), mn[0] + st * np.arange(n)


NPZ = os.environ.get("EFIELD_NPZ")          # optional cache: arrays T1_3p6GHz_wide_E / _g
if NPZ:
    Z = np.load(NPZ); E1, g = Z["T1_3p6GHz_wide_E"], Z["T1_3p6GHz_wide_g"]
else:
    E1, g = load(os.path.join(ROOT, "data", "fields", "E_Normal_T1_3p6GHz_wide.fld"))
h = g[1] - g[0]


def say(s=""): print(s)
def db(x): return 20 * np.log10(x)


def sample(E, P):
    """Trilinear interpolation of the complex field at points P (n x 3, mm)."""
    P = np.atleast_2d(P); c = ((P - g[0]) / h).T; out = np.zeros((len(P), 3), complex)
    for k in range(3):
        out[:, k] = map_coordinates(np.nan_to_num(E[..., k].real), c, order=1) \
            + 1j * map_coordinates(np.nan_to_num(E[..., k].imag), c, order=1)
    return out


def rot180(E):
    """Field of T4 from T1's by the ring symmetry: rotate 180 deg about z (T4 sits 180 deg from T1)."""
    F = E[::-1, ::-1].copy(); F[..., 0] *= -1; F[..., 1] *= -1; return F


E4 = rot180(E1)

# =====================================================================================================
say("STEP 1. Where things are")
th = np.deg2rad(60.5); az = np.deg2rad([-90.4, -30.4, 29.6, 89.6, 149.6, -150.4])
u = np.array([[np.sin(th) * np.cos(a), np.sin(th) * np.sin(a), np.cos(th)] for a in az])
u1, u4 = u[0], u[3]
a1, a4 = 97.55 * u1, 97.55 * u4
say(f"  T1 = {np.round(a1, 1)} mm, T4 = {np.round(a4, 1)} mm (front is -y, so T1 is at the front, T4 at the back)")
ang = np.arccos(u1 @ u4)
say(f"  T1 and T4 are 180 deg apart around the ring, but seen from the head centre they are {np.degrees(ang):.0f} deg"
    " apart, because both sit 48 mm above the centre")
say(f"  straight line T1->T4: length {np.linalg.norm(a4 - a1):.0f} mm, stays at z = 48, so its middle (0, 0, 48)"
    " is 48 mm from the centre")
ys, yw = np.sqrt(83 ** 2 - 48.04 ** 2), np.sqrt(76 ** 2 - 48.04 ** 2)
say(f"  it is inside the brain (r < 83) for |y| < {ys:.1f} mm: {2 * ys:.0f} mm of brain;"
    f" gray matter for {ys - yw:.1f} mm each side, white matter for {2 * yw:.0f} mm")
say(f"  the route over the top just outside the skin (r = 91): {91 * ang:.0f} mm, middle at (0, 0, 91)")
say()

# =====================================================================================================
say("STEP 2. How much tissue absorbs, from the material values alone (plane wave, 3.6 GHz)")
f = 3.6e9; w = 2 * np.pi * f; e0 = 8.854e-12; c0 = 2.998e8
tis = {"gray matter": (47.7, 2.42), "white matter": (35.3, 1.65), "CSF": (65.0, 4.27),
       "skull (assumed)": (10.8, 0.61), "skin (assumed)": (37.0, 2.0)}
loss = {}
for name, (er, sg) in tis.items():
    tand = sg / (w * er * e0)                                  # loss tangent
    alpha = w / c0 * np.sqrt(er / 2) * np.sqrt(np.sqrt(1 + tand ** 2) - 1)      # Np/m
    loss[name] = 8.686 * alpha / 100                            # dB/cm
    say(f"  {name:16s} eps_r {er:5.1f}  sigma {sg:4.2f} S/m  tan d {tand:.3f}  alpha {alpha:5.1f} Np/m"
        f" = {loss[name]:.2f} dB/cm  (quick rule 16.4*sigma/sqrt(eps_r) = {16.37 * sg / np.sqrt(er):.2f})")
say("  (8.686 converts Np to dB; the same dB number holds for field and for power)")
say(f"  straight through the brain: {2 * (ys - yw):.0f} mm gray + {2 * yw:.0f} mm white ="
    f" {2 * (ys - yw) / 10 * loss['gray matter'] + 2 * yw / 10 * loss['white matter']:.0f} dB of absorption alone")
say()

# =====================================================================================================
say("STEP 3. The 5.6 dB/cm slope: |E| of T1 sampled along T1's own axis, going into the head")
r = np.linspace(110, 0, 441); P = r[:, None] * u1[None, :]
A = np.linalg.norm(E1, axis=-1); A = np.where(np.isnan(A), np.nanmean(A), A)
prof = map_coordinates(A, ((P - g[0]) / h).T, order=1)          # magnitude first, as in figure (f)
pdb = db(prof / prof.max())
prof2 = np.linalg.norm(sample(E1, P), axis=1); pdb2 = db(prof2 / prof2.max())   # components first
for rr in (88, 83, 80, 76, 70, 65, 60, 55):
    i = np.argmin(abs(r - rr)); say(f"  r = {rr:3d} mm   {pdb[i]:6.1f} dB   (other interpolation {pdb2[i]:6.1f})")
m = (r >= 55) & (r <= 80)
k1, k2 = np.polyfit(r[m], pdb[m], 1)[0] * 10, np.polyfit(r[m], pdb2[m], 1)[0] * 10
mat = (4 * loss["gray matter"] + 21 * loss["white matter"]) / 25
say(f"  straight-line fit, r = 80 -> 55 mm: {k1:.2f} dB/cm (other interpolation {k2:.2f})")
say(f"  that stretch is 4 mm gray + 21 mm white: absorption alone predicts {mat:.2f} dB/cm")
say(f"  left over: {k2 - mat:.1f} to {k1 - mat:.1f} dB/cm = the beam spreading out (not absorbed, just diluted)")
say("  the drop from the skin (r 88) to the brain surface (r 83) is not absorption: see STEP 5")
say()

# =====================================================================================================
say("STEP 4. The -33 / -57 dB numbers: T1's field half-way to T4, on two routes")
t = np.linspace(0, 1, 61)
chord = a1 + t[:, None] * (a4 - a1)
nrm = np.cross(u1, u4); nrm /= np.linalg.norm(nrm)
arc = np.array([91 * (np.cos(s) * u1 + np.sin(s) * np.cross(nrm, u1)) for s in t * ang])
mc = np.linalg.norm(sample(E1, chord), axis=1); ma = np.linalg.norm(sample(E1, arc), axis=1)
ref = ma[:5].max(); iref = int(ma[:5].argmax())
say(f"  0 dB = the strongest |E| on the first 5 arc points, i.e. just in front of T1: {np.round(arc[iref], 0)} mm")
say(f"  over the top, half-way (0, 0, 91):   {db(ma[30] / ref):6.1f} dB")
say(f"  straight line, half-way (0, 0, 48):  {db(mc[30] / ref):6.1f} dB")
say(f"  gap: {db(ma[30] / mc[30]):.1f} dB = {ma[30] / mc[30]:.0f}x in field, {(ma[30] / mc[30]) ** 2:.0f}x in power")
eb, ew = [np.linalg.norm(sample(E1, [[0, -y, 48.04]])[0]) for y in (ys, yw)]
say(f"  hand check along the straight line: enters the brain at {db(eb / ref):.1f} dB, enters white matter at"
    f" {db(ew / ref):.1f} dB;")
say(f"    {yw:.0f} mm of white matter x {loss['white matter']:.2f} dB/cm = {yw / 10 * loss['white matter']:.0f} dB"
    f" -> predicts {db(ew / ref) - yw / 10 * loss['white matter']:.0f} dB at the middle; HFSS gives {db(mc[30] / ref):.0f}")
for R in (90, 93, 95):
    aR = np.array([R * (np.cos(s) * u1 + np.sin(s) * np.cross(nrm, u1)) for s in t * ang])
    mR = np.linalg.norm(sample(E1, aR), axis=1)
    say(f"  robustness: arc at r = {R} mm gives {db(mR[30] / ref):.1f} dB half-way (4 mm grid: read +-3 dB)")
say()

# =====================================================================================================
say("STEP 5. Why the field drops ~15 dB across 5 mm of skin/skull: the boundary, not absorption")
for rr in (92, 88, 83, 80):
    e = sample(E1, [rr * u1])[0]; rad = abs(e @ u1); tan = np.linalg.norm(e - (e @ u1) * u1)
    say(f"  r = {rr} mm: part pointing into the head {db(rad / prof2.max()):6.1f} dB, part along the surface"
        f" {db(tan / prof2.max()):6.1f} dB")
ec = 37 - 1j * 2.0 / (w * e0)
say(f"  entering skin, the part pointing into the head is divided by |eps| = {abs(ec):.0f}"
    f" ({db(abs(ec)):.0f} dB); the part along the surface passes unchanged")
say()

# =====================================================================================================
say("STEP 6. Sensitivity of the T1->T4 signal = |E1 . E4| (E4 from T1 by the 180 deg ring symmetry)")
say("  in dB this is roughly dB(E1) + dB(E4): a point counts only if BOTH antennas reach it")
S = np.abs(np.einsum("xyzc,xyzc->xyz", np.nan_to_num(E1), np.nan_to_num(E4)))
for name, p in [("over the top, half-way (0,0,91)", [0, 0, 91]), ("side, in air (+80,0,48)", [80, 0, 48]),
                ("side, in air (-80,0,48)", [-80, 0, 48]), ("straight line, half-way (0,0,48)", [0, 0, 48.04])]:
    e1, e4 = sample(E1, [p])[0], sample(E4, [p])[0]
    say(f"  {name:33s} |E1| {db(np.linalg.norm(e1) / ref):6.1f}  |E4| {db(np.linalg.norm(e4) / ref):6.1f}"
        f"  |E1.E4| {db(abs(np.sum(e1 * e4)) / ref ** 2):7.1f} dB")
X, Y, Zg = np.meshgrid(g, g, g, indexing="ij"); R = np.sqrt(X ** 2 + Y ** 2 + Zg ** 2)
tot = S.sum()
for name, mk in [("brain r < 83.5", R < 83.5), ("CSF/skull/fat/skin 83.5-88", (R >= 83.5) & (R < 88)),
                 ("air 88-97", (R >= 88) & (R < 97)), ("air >= 97 (incl. antennas)", R >= 97)]:
    say(f"  share of all T1->T4 sensitivity in {name:28s} {S[mk].sum() / tot:7.2%}")

# =====================================================================================================
# Figure
plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.titleweight": "semibold"})
CM = plt.get_cmap("Blues").copy()
fig = plt.figure(figsize=(17, 15))
RH, ZF = 97.7 * np.sin(th), 97.7 * np.cos(th)

# (1) orientation: the head seen from above (this IS the view of panels (a), (c))
ax = fig.add_subplot(2, 2, 1)
ax.add_patch(Circle((0, 0), 88, fill=True, fc="#f3eee4", ec="#2b2b2a", lw=1.2))
ax.add_patch(plt.Polygon([[-9, -86], [9, -86], [0, -104]], fc="#e9dfd6", ec="#2b2b2a"))        # nose = front (-y)
for s_, lab in [(1, "left ear\n(+x)"), (-1, "right ear\n(-x)")]:
    ax.add_patch(plt.matplotlib.patches.Ellipse((s_ * 90, 0), 8, 22, fc="#e9dfd6", ec="#2b2b2a"))
    ax.text(s_ * 112, -26, lab, ha="center", fontsize=9.5, color="#52514e")
tt = np.linspace(0, 2 * np.pi, 100); ax.plot(RH * np.cos(tt), RH * np.sin(tt), color="#eb6834", lw=0.8, ls="--")
for i, a in enumerate(az):
    ax.plot(RH * np.cos(a), RH * np.sin(a), "s", ms=9, mfc="#eb6834", mec="white", mew=1.3)
    lx, ly = (-20, -93) if i == 0 else (1.17 * RH * np.cos(a), 1.17 * RH * np.sin(a))
    ax.text(lx, ly, f"T{i + 1}", ha="center", va="center", fontsize=11, color="#7a2d0a", weight="bold")
ax.plot([0, 0], [-108, 122], color="#1c5cab", lw=3, alpha=0.8)
ax.text(4, 112, "the knife: vertical slice x = 0\n(through T1 and T4) → panels (b), (d)", color="#1c5cab",
        fontsize=10.5, weight="bold")
ax.annotate("", xy=(100, 0), xytext=(150, 0), arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#14213d"))
ax.text(152, 0, "you stand here\nand look at the\ncut face", va="center", fontsize=10.5, color="#14213d")
ax.text(14, -100, "face / front (-y)", ha="left", va="center", fontsize=10)
ax.text(-125, -150, "Seen from above. The ring sits 48 mm above the ear line, where the head is narrower,\n"
        "so from above the antennas appear inside the head outline. Panels (a), (c) use this same view.",
        fontsize=9.5, color="#3d4451", va="bottom")
ax.set_xlim(-128, 210); ax.set_ylim(-152, 135); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("(1) Looking down on the head: where the slice is and where you stand", loc="left")

xi = int(np.argmin(abs(g)))


def heads(ax):
    for rr, ls in [(88, "-"), (83, "--"), (76, (0, (1, 2))), (25, ":")]:
        ax.add_patch(Circle((0, 0), rr, fill=False, ec="#2b2b2a", lw=1.0, ls=ls))
    for s, lab in [(-1, "T1 (front)"), (1, "T4 (back)")]:
        ax.plot(s * RH, ZF, "s", ms=9, mfc="#eb6834", mec="white", mew=1.3)
        ax.text(s * RH, ZF - 14, lab, ha="center", fontsize=10.5, color="#7a2d0a", weight="bold")


def routes(ax):
    ax.plot(chord[:, 1], chord[:, 2], color="#e34948", lw=1.6, ls="--")
    ax.plot(arc[:, 1], arc[:, 2], color="#14213d", lw=1.6, ls=":")


# (2) field of T1 on x = 0, 0 dB = the reference just in front of T1
ax = fig.add_subplot(2, 2, 2)
img = db(np.linalg.norm(np.nan_to_num(E1[xi]), axis=-1) / ref)
mp = ax.imshow(img.T, origin="lower", extent=[g[0], g[-1], g[0], g[-1]], cmap=CM, vmin=-70, vmax=0)
heads(ax); routes(ax)
for p, lab, dx, dy in [(arc[iref], "R  0 dB (reference)", -48, 22), (arc[30], f"A  {db(ma[30] / ref):.0f} dB", 6, 8),
                       (chord[30], f"B  {db(mc[30] / ref):.0f} dB", 6, 8)]:
    ax.plot(p[1], p[2], "o", ms=8, mfc="white", mec="#b3261e", mew=2)
    ax.text(p[1] + dx, p[2] + dy, lab, color="#b3261e", fontsize=11.5, weight="bold")
ax.text(-116, -116, "skin r 88 (solid), brain surface r 83 (dashed),\nwhite matter r 76 (dotted), hippocampus r 25", fontsize=9.5,
        color="#3d4451", va="bottom", bbox=dict(fc="white", ec="none", alpha=0.8))
ax.set_xlim(-120, 120); ax.set_ylim(-120, 120); ax.set_aspect("equal")
ax.set_xlabel("y (mm)   front ←   → back"); ax.set_ylabel("z (mm)   up")
ax.set_title("(2) = panel (b): T1's field, slice x = 0", loc="left")
fig.colorbar(mp, ax=ax, shrink=0.8, extend="max", label="|E| of T1, dB relative to R")

# (3) field along both routes
ax = fig.add_subplot(2, 2, 3)
sc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(chord, axis=0), axis=1))]
sa = np.r_[0, np.cumsum(np.linalg.norm(np.diff(arc, axis=0), axis=1))]
inb = np.linalg.norm(chord, axis=1) < 83
ax.axvspan(sc[inb].min(), sc[inb].max(), color="#efe6f0", zorder=0)
ax.text(sc[inb].mean(), 4, "straight line is inside the brain here", ha="center", fontsize=10, color="#6b4a74")
ax.plot(sa, db(ma / ref), color="#14213d", lw=2.2, ls=":", label=f"over the top in air ({sa[-1]:.0f} mm)")
ax.plot(sc, db(mc / ref), color="#e34948", lw=2.2, ls="--", label=f"straight line through the head ({sc[-1]:.0f} mm)")
s0 = sc[np.argmin(abs(chord[:, 1] + yw))]
ss = np.linspace(s0, sc[30], 20)
ax.plot(ss, db(ew / ref) - (ss - s0) / 10 * loss["white matter"], color="#7a2d0a", lw=1.2,
        label=f"absorption alone in white matter ({loss['white matter']:.1f} dB/cm)")
ax.plot(sa[30], db(ma[30] / ref), "o", ms=8, mfc="white", mec="#14213d", mew=2)
ax.plot(sc[30], db(mc[30] / ref), "o", ms=8, mfc="white", mec="#b3261e", mew=2)
ax.text(sa[30] + 4, db(ma[30] / ref) + 3, "A", fontsize=12, weight="bold")
ax.text(sc[30] + 4, db(mc[30] / ref) - 6, "B", fontsize=12, weight="bold", color="#b3261e")
ax.set_xlabel("distance travelled from T1 (mm)"); ax.set_ylabel("|E| of T1 (dB relative to R)")
ax.set_ylim(-75, 12); ax.grid(alpha=0.3); ax.legend(loc="lower left", fontsize=10)
ax.set_title("(3) T1's field along the two routes to T4", loc="left")

# (4) sensitivity on x = 0, 0 dB = R squared
ax = fig.add_subplot(2, 2, 4)
img = db(np.maximum(S[xi], 1e-40) / ref ** 2)
mp = ax.imshow(img.T, origin="lower", extent=[g[0], g[-1], g[0], g[-1]], cmap=CM, vmin=-130, vmax=-30)
heads(ax); routes(ax)
for p in ([0, 0, 91], [0, 0, 48.04]):
    e1, e4 = sample(E1, [p])[0], sample(E4, [p])[0]
    v = db(abs(np.sum(e1 * e4)) / ref ** 2)
    ax.plot(p[1], p[2], "o", ms=8, mfc="white", mec="#b3261e", mew=2)
    ax.text(p[1] + 6, p[2] + 8, f"{'A' if p[2] > 60 else 'B'}  {v:.0f} dB", color="#b3261e", fontsize=11.5,
            weight="bold")
ax.set_xlim(-120, 120); ax.set_ylim(-120, 120); ax.set_aspect("equal")
ax.set_xlabel("y (mm)   front ←   → back"); ax.set_ylabel("z (mm)   up")
ax.set_title("(4) = panel (d): T1→T4 sensitivity |E₁·E₄|, slice x = 0", loc="left")
fig.colorbar(mp, ax=ax, shrink=0.8, extend="both", label="dB relative to R²  (≈ dB of E₁ + dB of E₄)")
fig.suptitle("Where the T1→T4 signal goes (healthy uniform head, 3.6 GHz, wide export, 4 mm grid; viewing only)",
             fontsize=15, weight="bold", y=0.995)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "efield_routes_explained.png"), dpi=130, bbox_inches="tight")
say("\nwrote efield_routes_explained.png")
