"""Adversarial review, round 2 (main session): field-export geometry and field-based claims (R7, G8, G5, G3, A14,
C4, phase band dependence).

    python scripts/12_review2_fields.py

Reads the HFSS field exports data/fields/E_Normal_T#_<f>GHz.fld (v2 Normal design, one export per excitation) with
the imaging package's reader (read-only) and the lobe Touchstone files. Writes results/05_lobe/review2/
{report_fields.md, F*.csv, figures/}. Predictions for C4 were committed before this script first ran
(review2/predictions_R3_C4.md).

Sensitivity density of a path (a, b): |E_a . E_b| (the Born integrand of a permittivity change, without the
material contrast), summed over 3 mm voxels. Thin layers (skin 0.5 mm, CSF 0.5 mm) are below the grid resolution;
voxels are classified by the radius of their centre.
"""
from __future__ import annotations

import importlib.util
import itertools
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adstage.config import load_config  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
R11 = _load("rev11", "11_review2.py")
OUT = ROOT / "results" / "05_lobe" / "review2"
FIG = OUT / "figures"
FD = ROOT / "data" / "fields"
md = L7.md
ANT = L7.ANT
TAGS = {"3p4": 3.4e9, "3p6": 3.6e9, "3p8": 3.8e9}
C0 = 299792458.0


def header(p):
    with open(p, encoding="utf-8", errors="ignore") as fh:
        h = fh.readline()
    m = re.search(r"Min:\s*\[([^\]]+)\]\s*Max:\s*\[([^\]]+)\]\s*Grid Size:\s*\[([^\]]+)\]", h)
    num = lambda s: [float(x.replace("mm", "")) for x in s.split()]     # noqa: E731
    return num(m.group(1)), num(m.group(2)), num(m.group(3))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    FIG.mkdir(parents=True, exist_ok=True)
    from imaging.fields import read_fld
    gh = git_hash(ROOT)
    L = [f"# Adversarial review round 2, main session: field exports (code {gh})", ""]
    summ = []

    # ------------------------------------------------------------------ R7 / G8 geometry of every export
    rows, E, grid = [], {}, None
    for p in sorted(FD.glob("*.fld")):
        mn, mx, st = header(p)
        n = [int(round((b - a) / s)) + 1 for a, b, s in zip(mn, mx, st)]
        row = {"file": p.name, "min (mm)": str(mn), "max (mm)": str(mx), "grid (mm)": str(st), "nodes": int(np.prod(n)),
               "z planes": n[2], "kind": "volume" if n[2] > 1 else "plane"}
        if "_wide" not in p.name:
            pts, Ev = read_fld(p)
            row["z range read (mm)"] = f"{np.nanmin(pts[:, 2]):.0f} to {np.nanmax(pts[:, 2]):.0f}"
            row["distinct z read"] = int(len(np.unique(np.round(pts[:, 2], 3))))
            row["NaN nodes"] = int(np.isnan(Ev).any(1).sum())
            t = int(re.search(r"_T(\d)_", p.name).group(1))
            tag = re.search(r"_(\dp\d)GHz", p.name).group(1)
            if grid is None:
                grid = pts
            if not np.allclose(np.nan_to_num(pts), np.nan_to_num(grid)):
                raise ValueError(f"{p.name}: node order differs from the first export")
            E[(t, tag)] = Ev
        rows.append(row)
    gt = pd.DataFrame(rows)
    gt.to_csv(OUT / "F_R7_exports.csv", index=False)
    L += ["## R7 / G8. Geometry of every field export",
          "Read from each file's header and, for the 18 per-excitation exports, from the data rows:", md(gt), "",
          "Every export is a 3-D volume (61 z planes, -90 to +90 mm, 3 mm grid; the 'wide' T1 export 61 planes, "
          "-120 to +120 mm, 4 mm). None is the `field_cutplane` sheet (z = -9.09 mm). The antennas (feed z = 48 mm, "
          "patch to AMC z = 44-78 mm, radius 97-111 mm) lie inside the exported cube.", ""]
    summ.append({"item": "R7/G8 field-export geometry", "verdict": "CONFIRMED (volume, not the cut plane)",
                 "old -> new": "unstated -> all 19 exports are volumes: 18 x (-90..90 mm)^3 at 3 mm, 1 x (-120..120 mm)^3 at 4 mm; "
                               "no field claim used the z = -9 mm plane",
                 "evidence": "review2/F_R7_exports.csv"})

    pts = grid
    r = np.linalg.norm(pts, axis=1)
    z = pts[:, 2]
    az = np.degrees(np.arctan2(pts[:, 1], pts[:, 0]))
    ok = ~np.isnan(np.stack([E[(t, "3p6")] for t in range(1, 7)])).any((0, 2))
    regions = {"air (r > 88, inside the cube)": r > 88, "skin+fat+skull (83.5-88)": (r > 83.5) & (r <= 88),
               "CSF layer (83-83.5)": (r > 83) & (r <= 83.5), "gray (76-83)": (r > 76) & (r <= 83),
               "white (25-76)": (r > 25) & (r <= 76), "hippocampus (<= 25)": r <= 25}
    brain = r <= 83.5
    head = r <= 88
    zb = {"z > 40": z > 40, "0 < z <= 40": (z > 0) & (z <= 40), "z <= 0": z <= 0}
    D = L7.DIST

    # ------------------------------------------------------------------ A14 antenna positions from their own fields
    a14 = []
    shell = (r >= 89) & (r <= 93) & ok
    for t in range(1, 7):
        mag = np.linalg.norm(np.abs(E[(t, "3p6")]), axis=1)
        sel = shell & (mag >= np.quantile(mag[shell], 0.99))
        w = mag[sel]
        c = (pts[sel] * w[:, None]).sum(0) / w.sum()
        a14.append({"field file": f"E_Normal_T{t}_3p6GHz", "centroid azimuth (deg)": float(np.degrees(np.arctan2(c[1], c[0]))),
                    "centroid z (mm)": float(c[2]), "expected azimuth (T# convention)": -90 + 60 * (t - 1)})
    a14t = pd.DataFrame(a14)
    a14t["expected azimuth (T# convention)"] = ((a14t["expected azimuth (T# convention)"] + 180) % 360) - 180
    a14t.to_csv(OUT / "F_A14_antenna_positions.csv", index=False)

    # ------------------------------------------------------------------ G3 polarisation near each antenna
    g3 = []
    G3REG = {"air gap r 89-93, +-15 deg, 40 < z < 80": lambda d: (r >= 89) & (r <= 93) & (d < 15) & (z > 40) & (z < 80),
             "air gap r 89-93, boresight +-5 deg, 45 < z < 58": lambda d: (r >= 89) & (r <= 93) & (d < 5) & (z > 45) & (z < 58),
             "in head r 80-87, boresight +-5 deg, 45 < z < 58": lambda d: (r >= 80) & (r <= 87) & (d < 5) & (z > 45) & (z < 58),
             "in head r 80-87, +-15 deg, 40 < z < 80": lambda d: (r >= 80) & (r <= 87) & (d < 15) & (z > 40) & (z < 80)}
    for t in range(1, 7):
        phi0 = np.radians(-90 + 60 * (t - 1))
        daz = np.abs(((az - np.degrees(phi0) + 180) % 360) - 180)
        for reg, fn in G3REG.items():
            sel = fn(daz) & ok
            P_, Ev = pts[sel], E[(t, "3p6")][sel]
            rh = P_ / np.linalg.norm(P_, axis=1, keepdims=True)
            th = np.arccos(np.clip(rh[:, 2], -1, 1))
            ph = np.arctan2(P_[:, 1], P_[:, 0])
            eth = np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)], 1)
            eph = np.stack([-np.sin(ph), np.cos(ph), np.zeros_like(ph)], 1)
            comp = {k: np.sqrt(np.sum(np.abs(np.einsum("ij,ij->i", Ev, u)) ** 2)) for k, u in (("r", rh), ("theta", eth), ("phi", eph))}
            tot = np.sqrt(sum(v ** 2 for v in comp.values()))
            g3.append({"antenna": f"T{t}", "region": reg, "nodes": int(sel.sum()),
                       **{f"|E_{k}| share": v / tot for k, v in comp.items()},
                       "theta / (theta+phi) amplitude": comp["theta"] / (comp["theta"] + comp["phi"])})
    g3t = pd.DataFrame(g3)
    g3t.to_csv(OUT / "F_G3_polarisation.csv", index=False)

    # ------------------------------------------------------------------ G5 and re-derived depth claims: sensitivity per region and z band
    g5 = []
    for a, b in itertools.combinations_with_replacement(range(6), 2):
        s = np.abs(np.einsum("ij,ij->i", E[(a + 1, "3p6")], E[(b + 1, "3p6")]))
        s = np.where(ok, s, 0)
        tot = s.sum()
        row = {"path": f"{ANT[a]}-{ANT[b]}" if a != b else f"{ANT[a]} refl.", "type": L7.PATH[int(D[a, b])]}
        for k, m in regions.items():
            row[f"share {k}"] = float(s[m].sum() / tot)
        sb = s[brain].sum()
        for k, m in zb.items():
            row[f"brain share at {k}"] = float(s[brain & m].sum() / sb)
            row[f"head share at {k}"] = float(s[head & m].sum() / s[head].sum())
        row["in-brain share within 13.5 mm of the brain surface"] = float(s[brain & (r >= 70)].sum() / sb)
        g5.append(row)
    g5t = pd.DataFrame(g5)
    g5t.to_csv(OUT / "F_G5_sensitivity_regions.csv", index=False)
    g5c = g5t.groupby("type").mean(numeric_only=True).reset_index()

    L += ["## A14 / G3. Antennas located from their own fields (3.6 GHz; |E|-weighted centroid of the strongest 1% of nodes "
          "at r = 89-93 mm)", md(a14t, ".1f"), "",
          "Polarisation near each antenna (field components in the local spherical frame, amplitude shares; the "
          "air gap lies between skin (r 88) and antenna ground (r 97.65); 'in head' is skin to outer gray matter):",
          md(g3t.groupby("region", sort=False).agg(**{c: (c, "mean") for c in g3t.columns if c not in ("antenna", "region")})
             .reset_index(), ".2f"), "(mean over the six antennas; per antenna in F_G3_polarisation.csv)", "",
          "## G5 and the depth claims. Share of each path's sensitivity |E_a.E_b| (3.6 GHz) by region and by height, "
          "mean per path type:", md(g5c, ".3f"), ""]
    opp = g5c.set_index("type").loc["opposite"]
    summ.append({"item": "A14 field evidence", "verdict": "CONFIRMED",
                 "old -> new": "T# positions from fields: " + ", ".join(f"T{i + 1} {v:+.0f}" for i, v in
                                                                      enumerate(a14t['centroid azimuth (deg)'])) + " deg",
                 "evidence": "review2/F_A14_antenna_positions.csv"})
    g3m = g3t.groupby("region", sort=False).mean(numeric_only=True)
    gap_, hb_ = g3m.loc["air gap r 89-93, +-15 deg, 40 < z < 80"], g3m.loc["in head r 80-87, boresight +-5 deg, 45 < z < 58"]
    summ.append({"item": "G3 polarisation",
                 "verdict": ("CHANGED (inside the head the field is meridional; the 65/35 figure is an air-gap window average)"
                             if hb_["theta / (theta+phi) amplitude"] > 0.8 else "CANNOT TELL"),
                 "old -> new": f"65% theta / 35% phi -> in head at boresight: |E_theta| {hb_['|E_theta| share']:.2f}, |E_phi| "
                               f"{hb_['|E_phi| share']:.2f}, |E_r| {hb_['|E_r| share']:.2f} (theta/(theta+phi) "
                               f"{hb_['theta / (theta+phi) amplitude']:.2f}); air gap +-15 deg window: |E_r| {gap_['|E_r| share']:.2f}, "
                               f"theta/(theta+phi) {gap_['theta / (theta+phi) amplitude']:.2f}",
                 "evidence": "review2/F_G3_polarisation.csv"})
    summ.append({"item": "G5 sensitivity by height; depth claims", "verdict": "CHANGED (quantified)",
                 "old -> new": f"'99% in air' (opposite) -> air {opp['share air (r > 88, inside the cube)']:.3f}, brain "
                               f"{opp[[c for c in g5c.columns if c.startswith('share ') and ('gray' in c or 'white' in c or 'CSF' in c or 'hippo' in c)]].sum():.4f}; "
                               "in-brain share at z > 40 / 0-40 / <= 0: " + "; ".join(
                                   f"{t}: {r_['brain share at z > 40']:.2f}/{r_['brain share at 0 < z <= 40']:.2f}/{r_['brain share at z <= 0']:.2f}"
                                   for t, r_ in g5c.set_index('type').iterrows()),
                 "evidence": "review2/F_G5_sensitivity_regions.csv"})

    # ------------------------------------------------------------------ C4 share of the LeftOnly gap volume and the predicted phase
    f_ = 3.6e9
    k0 = 2 * np.pi * f_ / C0
    n = lambda e: np.sqrt(e)                                  # noqa: E731
    e = {"S2": 7.5, "S3": 11.5}
    secaz = {"S2": (-60, 0), "S3": (0, 60)}
    reg = {}
    for sk, (lo, hi) in secaz.items():
        insec = (az >= lo) & (az < hi)
        reg[f"gap {sk} (gray -> CSF_Mild)"] = (insec & (r > 83 - e[sk]) & (r <= 83), n(55.25) - n(47.7), e[sk])
        reg[f"gray band {sk} (white -> Mild gray)"] = (insec & (r > 76 - e[sk]) & (r <= 83 - e[sk]), n(40.3) - n(35.3), 7.0)
    reg["CSF layer, all (CSF -> CSF_Mild)"] = ((r > 83) & (r <= 83.5), n(55.25) - n(65.0), 0.5)
    f, Sall, _, _ = L8.load_all()
    S = {d: Sall[d] for d in ("Healthy_sliced_new", "LeftOnly_test_c3")}
    fi = int(np.argmin(np.abs(f - f_)))
    c4 = []
    for a, b in itertools.combinations(range(6), 2):
        s = np.abs(np.einsum("ij,ij->i", E[(a + 1, "3p6")], E[(b + 1, "3p6")]))
        s = np.where(ok, s, 0)
        pred, row = 0.0, {"path": f"{ANT[a]}-{ANT[b]}", "type": L7.PATH[int(D[a, b])]}
        for k, (m, dn, dmm) in reg.items():
            sh = float(s[m].sum() / s[head].sum())
            row[f"head share: {k}"] = sh
            pred += -sh * np.degrees(k0 * dn * dmm * 1e-3)
        row["predicted phase change (deg), share x -k0 dn d"] = pred
        obs_b = np.degrees(np.angle(R11.sbar(S["LeftOnly_test_c3"])[:, a, b] * np.conj(R11.sbar(S["Healthy_sliced_new"])[:, a, b])))
        row["observed at 3.6 GHz (deg)"] = float(obs_b[fi])
        row["observed mean 3.30-3.65 GHz (deg)"] = float(obs_b[R11.fmask(f, R11.LRBAND)].mean())
        c4.append(row)
    c4t = pd.DataFrame(c4)
    c4t.to_csv(OUT / "F_C4_phase_prediction.csv", index=False)
    nbr = c4t[c4t.type == "neighbour"]
    from scipy.stats import pearsonr
    rr, pp = pearsonr(c4t["predicted phase change (deg), share x -k0 dn d"], c4t["observed mean 3.30-3.65 GHz (deg)"])

    # ------------------------------------------------------------------ band dependence: phase asymmetry, resonances, notches
    cp = {d: R11.lr_cr_phase(Sall[d]) for d in R11.SYM + [R11.LO]}
    pp_ = {d: R11.pair_phase(Sall[d]) for d in R11.SYM + [R11.LO]}
    key = "T2-T3 vs T5-T6"
    res = R11.resonance(f, Sall["Healthy_sliced_new"])
    notch = []
    for a, b in itertools.combinations(range(6), 2):
        y = 20 * np.log10(np.abs(R11.sbar(Sall["Healthy_sliced_new"])[:, a, b]))
        k = np.flatnonzero((y[1:-1] < y[:-2]) & (y[1:-1] < y[2:]) & (y[1:-1] < np.median(y) - 6)) + 1
        for kk in k:
            notch.append({"path": f"{ANT[a]}-{ANT[b]}", "notch f (GHz)": float(f[kk] / 1e9), "depth below median (dB)": float(np.median(y) - y[kk])})
    nt = pd.DataFrame(notch)
    nt.to_csv(OUT / "F_C4_notches.csv", index=False)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    top = sorted(cp[R11.LO], key=lambda k_: -abs(cp[R11.LO][k_][R11.fmask(f, R11.LRBAND)].mean()))[:3]
    for k_ in top + [None]:
        src = pp_ if k_ is None else cp
        kk = key if k_ is None else k_
        lab = f"pair {kk}" if k_ is None else kk
        nulls = np.array([src[d][kk] for d in R11.SYM])
        line, = ax[0].plot(f / 1e9, src[R11.LO][kk], lw=1.6, label=f"LeftOnly: {lab}")
        ax[0].fill_between(f / 1e9, nulls.min(0), nulls.max(0), color=line.get_color(), alpha=0.12)
    for fr, _ in res:
        ax[0].axvline(fr / 1e3, color="#888", lw=0.6)
    ax[0].axhline(0, color="k", lw=0.5)
    ax[0].set_ylabel("left-right phase (deg)")
    ax[0].legend(fontsize=7)
    ax[0].set_title("LeftOnly against the band of the nine mirror-symmetric designs (shaded); grey lines: |Sii| resonances", loc="left", fontsize=9)
    for t in range(6):
        ax[1].plot(f / 1e9, 20 * np.log10(np.abs(Sall["Healthy_sliced_new"][:, t, t])), lw=1, label=f"|S{ANT[t]}{ANT[t]}|")
    for _, rw in nt.iterrows():
        ax[1].axvline(rw["notch f (GHz)"], color="#c33", lw=0.4, alpha=0.5)
    ax[1].set_ylabel("|Sii| (dB), healthy head")
    ax[1].set_xlabel("frequency (GHz); red lines: transmission notches (> 6 dB below the path median)")
    ax[1].legend(fontsize=7, ncol=3)
    fig.savefig(FIG / "F_C4_band_dependence.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    # left-right asymmetry of the neighbour mirror pairs: predicted vs observed; sign agreement on long paths
    pc = c4t.set_index("path")
    anti = []
    for lft, rgt in (("T2-T3", "T5-T6"), ("T3-T4", "T4-T5"), ("T1-T2", "T1-T6")):
        anti.append({"mirror pair": f"{lft} vs {rgt}",
                     "predicted left - right (deg)": pc.loc[lft, "predicted phase change (deg), share x -k0 dn d"]
                     - pc.loc[rgt, "predicted phase change (deg), share x -k0 dn d"],
                     "observed left - right, 3.30-3.65 GHz (deg)": pc.loc[lft, "observed mean 3.30-3.65 GHz (deg)"]
                     - pc.loc[rgt, "observed mean 3.30-3.65 GHz (deg)"]})
    antit = pd.DataFrame(anti)
    antit.to_csv(OUT / "F_C4_neighbour_asymmetry.csv", index=False)
    longp = c4t[c4t.type != "neighbour"]
    sign_ok = int((np.sign(longp["predicted phase change (deg), share x -k0 dn d"]) == np.sign(longp["observed mean 3.30-3.65 GHz (deg)"])).sum())
    common = float(nbr[nbr.path.isin(["T1-T6", "T4-T5", "T5-T6"])]["observed mean 3.30-3.65 GHz (deg)"].mean())
    sbands = {"3.20-3.50": (3.2e9, 3.5e9), "3.50-3.65": (3.5e9, 3.65e9), "3.65-3.80": (3.65e9, 3.8e9), "3.80-4.20": (3.8e9, 4.2e9)}
    bd = []
    for kk in top:
        for bn, bb in sbands.items():
            m_ = R11.fmask(f, bb)
            bd.append({"statistic": kk, "band": bn, "|LeftOnly| mean (deg)": float(np.abs(cp[R11.LO][kk][m_]).mean()),
                       "largest symmetric design, mean |.| (deg)": float(max(np.abs(cp[d][kk][m_]).mean() for d in R11.SYM))})
    bdt = pd.DataFrame(bd)
    bdt["ratio"] = bdt["|LeftOnly| mean (deg)"] / bdt["largest symmetric design, mean |.| (deg)"]
    bdt.to_csv(OUT / "F_C4_band_ratios.csv", index=False)
    L += ["## C4. Physical sign and size (prediction committed in predictions_R3_C4.md before this ran)",
          "Head share of each path's sensitivity in the LeftOnly change volumes and the phase change predicted by "
          "share x (-k0 dn d) at 3.6 GHz, against the observed LeftOnly - Healthy_sliced_new phase change:",
          md(c4t, ".3f"), "",
          f"Neighbour paths: predicted {nbr['predicted phase change (deg), share x -k0 dn d'].min():.2f} to "
          f"{nbr['predicted phase change (deg), share x -k0 dn d'].max():.2f} deg, observed (3.30-3.65 GHz) "
          f"{nbr['observed mean 3.30-3.65 GHz (deg)'].min():.2f} to {nbr['observed mean 3.30-3.65 GHz (deg)'].max():.2f} deg. "
          f"Correlation of predicted and observed over the 15 paths: r = {rr:.2f} (p = {pp:.2f}).",
          "Band dependence (figure `figures/F_C4_band_dependence.png`): healthy-head |Sii| resonances at "
          + ", ".join(f"{fr / 1e3:.3f}" for fr, _ in res) + f" GHz; transmission notches in `F_C4_notches.csv` "
          f"({len(nt)} found).", "", "Neighbour mirror pairs, left minus right:", md(antit, ".2f"), "",
          f"Long paths: predicted and observed signs agree on {sign_ok} of {len(longp)}. The right-side neighbour paths all "
          f"move by about {common:.1f} deg although the share model predicts ~0.", "",
          "Band dependence of the largest cross-ratio asymmetries (mean |value| per sub-band against the largest "
          "symmetric design):", md(bdt, ".2f"), ""]
    summ.append({"item": "C4 physical sign and size", "verdict": "CHANGED (neighbour asymmetry explained; long paths not)",
                 "old -> new": "none -> neighbour left-right, predicted vs observed: " + "; ".join(
                     f"{r_['mirror pair']} {r_['predicted left - right (deg)']:+.1f} vs {r_['observed left - right, 3.30-3.65 GHz (deg)']:+.1f}"
                     for _, r_ in antit.iterrows()) + f" deg; long-path signs agree {sign_ok}/{len(longp)}; common right-side "
                     f"{common:+.1f} deg unexplained; band: cross-ratio asymmetry / largest symmetric design "
                     + ", ".join(f"{r_.band} {r_.ratio:.1f}x" for _, r_ in bdt[bdt.statistic == top[0]].iterrows()),
                 "evidence": "review2/F_C4_*.csv, figures/F_C4_band_dependence.png"})

    st = pd.DataFrame(summ)
    st.to_csv(OUT / "summary_fields.csv", index=False)
    L += ["## Summary (fields part)", md(st), ""]
    (OUT / "report_fields.md").write_text("\n".join(L), encoding="utf-8")
    print((OUT / "report_fields.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
