"""HFSS complex E-field exports: reader, completeness checks, interpolation; model substitute.

Files (data/fields/): E_Normal_T{t}_{3p4,3p6,3p8}GHz.fld, one per antenna excitation, plus
E_Normal_T1_3p6GHz_wide.fld. As supplied (2026-10-02): HFSS 2024.2 calculator export of complex
vector E, project `new`, design `Healthy`; source = terminal T_t at 1 V incident voltage, 0 deg,
all other terminals 0 V (matched 50 ohm), port post-processing off. Cartesian grid, z varies
fastest; coordinates in metres. A few NaN points lie inside antenna metal (r ~ 97-115 mm).

Two header layouts are understood:
  * HFSS:  'X, Y, Z, Complex Vector data "<Ex,Ey,Ez>"'  -> x y z, then (re, im) per component in
           the listed component order;
  * named columns (X Y Z ExRe ExIm ...), any order.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .common import N_ANT, ROOT

FIELD_DIR = ROOT / "data" / "fields"
FREQ_TAGS = {"3p4": 3.4e9, "3p6": 3.6e9, "3p8": 3.8e9}
WIDE_FILE = "E_Normal_T1_3p6GHz_wide.fld"
V_INC = 1.0          # incident voltage of the driven terminal [V]
Z0 = 50.0            # reference impedance [ohm]


def expected_files(stage="Normal"):
    return [FIELD_DIR / f"E_{stage}_T{t}_{tag}GHz.fld" for tag in FREQ_TAGS for t in range(1, N_ANT + 1)]


def fields_available(stage="Normal") -> bool:
    return all(p.exists() for p in expected_files(stage))


def _is_number(tok: str) -> bool:
    try:
        float(tok)
        return True
    except ValueError:
        return False


def _col_index(names: list[str]) -> dict:
    """Map X, Y, Z, ExRe, ExIm, ... to column numbers from header names (case-insensitive)."""
    norm = [re.sub(r"[^a-z0-9]", "", n.lower()) for n in names]
    out = {}
    for ax in "xyz":
        for i, n in enumerate(norm):
            if n in (ax, f"{ax}mm", f"{ax}m", f"{ax}meter", f"{ax}coord", f"{ax}coordinate"):
                out[ax.upper()] = i
    for ax in "xyz":
        for part, keys in (("Re", ("re", "real")), ("Im", ("im", "imag"))):
            for i, n in enumerate(norm):
                if n.startswith(f"e{ax}") and any(k in n[2:] for k in keys):
                    out[f"E{ax}{part}"] = i
    need = {"X", "Y", "Z", "ExRe", "ExIm", "EyRe", "EyIm", "EzRe", "EzIm"}
    if missing := need - set(out):
        raise ValueError(f"field header lacks columns {sorted(missing)}: {names}")
    return out


def _header(path: Path):
    lines = []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            toks = [t for t in re.split(r"[\s,;]+", line.strip()) if t]
            if toks and all(_is_number(t) for t in toks):
                break
            lines.append(line.rstrip("\n"))
    return lines


def read_fld(path: str | Path, pairing: str = "interleaved"):
    """-> (pts_mm (P, 3), E (P, 3) complex), rows in file order. NaN rows are kept (NaN).

    pairing (HFSS layout only): 'interleaved' = Ex_re Ex_im Ey_re Ey_im Ez_re Ez_im (as supplied);
    'blocked' = Ex_re Ey_re Ez_re Ex_im Ey_im Ez_im (used only to test the pairing)."""
    path = Path(path)
    hdr = _header(path)
    A = pd.read_csv(path, sep=r"\s+", skiprows=len(hdr), header=None, engine="c",
                    na_values=["Nan", "NaN", "nan", "-Nan", "-nan"], dtype=float).to_numpy()
    hv = " ".join(hdr)
    m = re.search(r"Complex\s+Vector\s+data\s*\"?<\s*([^>]+)>", hv, flags=re.IGNORECASE)
    if m:
        comps = [c.strip().lower() for c in m.group(1).split(",")]
        order = {c[-1]: i for i, c in enumerate(comps)}          # 'ex' -> 'x'
        if sorted(order) != ["x", "y", "z"] or A.shape[1] != 9:
            raise ValueError(f"{path.name}: unexpected vector header {m.group(0)!r} / {A.shape[1]} cols")
        pts = A[:, :3]
        if pairing == "interleaved":
            E = np.stack([A[:, 3 + 2 * order[a]] + 1j * A[:, 4 + 2 * order[a]] for a in "xyz"], -1)
        else:
            E = np.stack([A[:, 3 + order[a]] + 1j * A[:, 6 + order[a]] for a in "xyz"], -1)
    else:
        names = next((re.split(r"[\s,;]+", h.strip()) for h in reversed(hdr)
                      if len(re.split(r"[\s,;]+", h.strip())) >= 9), None)
        if names is None:
            raise ValueError(f"{path}: no recognised column header")
        ci = _col_index(names)
        pts = A[:, [ci["X"], ci["Y"], ci["Z"]]]
        E = np.stack([A[:, ci[f"E{a}Re"]] + 1j * A[:, ci[f"E{a}Im"]] for a in "xyz"], -1)
    if np.nanmax(np.abs(pts)) < 1.0:                    # metres -> mm
        pts = pts * 1e3
    return pts, E


class Grid:
    """A regular Cartesian field grid (z fastest), E on (nx, ny, nz, 3)."""

    def __init__(self, pts_mm, E):
        ax = [np.unique(np.round(pts_mm[:, i], 6)) for i in range(3)]
        n = [len(a) for a in ax]
        self.full = len(pts_mm) == n[0] * n[1] * n[2]
        if not self.full:
            raise ValueError(f"not a full grid: {len(pts_mm)} rows for {n}")
        Pg = np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
        self.z_fastest = bool(np.allclose(np.round(pts_mm, 6), Pg))
        if not self.z_fastest:                           # reorder if the file was not z-fastest
            idx = np.lexsort((pts_mm[:, 2], pts_mm[:, 1], pts_mm[:, 0]))
            E = E[idx]
        self.axes = ax
        self.step = float(np.median(np.diff(ax[0])))
        self.E = E.reshape(n[0], n[1], n[2], 3)

    def points(self):
        return np.stack(np.meshgrid(*self.axes, indexing="ij"), -1)

    def sample(self, pts_mm):
        """Trilinear interpolation of E at pts (P, 3) mm -> (P, 3); NaN outside the grid or next
        to a NaN node."""
        from scipy.interpolate import RegularGridInterpolator
        out = np.empty((len(pts_mm), 3), complex)
        for c in range(3):
            f = RegularGridInterpolator(self.axes, self.E[..., c], bounds_error=False,
                                        fill_value=np.nan)
            out[:, c] = f(pts_mm)
        return out


def divergence_ratio(path, r_ranges=((90.0, 94.0), (125.0, 200.0))):
    """Median |div E| h / |E| over air points (r in r_ranges, all 6 neighbours in air) for the
    interleaved and the blocked (re/im) pairing. Correct pairing -> clearly smaller."""
    out = {}
    for pairing in ("interleaved", "blocked"):
        g = Grid(*read_fld(path, pairing))
        P = g.points()
        r = np.linalg.norm(P, axis=-1)
        air = np.zeros(r.shape, bool)
        for lo, hi in r_ranges:
            air |= (r >= lo) & (r <= hi)
        E = g.E
        d = np.full(r.shape, np.nan, complex)
        inner = (slice(1, -1),) * 3
        dx = (E[2:, 1:-1, 1:-1, 0] - E[:-2, 1:-1, 1:-1, 0])
        dy = (E[1:-1, 2:, 1:-1, 1] - E[1:-1, :-2, 1:-1, 1])
        dz = (E[1:-1, 1:-1, 2:, 2] - E[1:-1, 1:-1, :-2, 2])
        d[inner] = (dx + dy + dz) / 2.0                     # x h (h = grid step)
        ok = air.copy()
        for ax in range(3):                                 # neighbours must be air as well
            for s in (1, -1):
                ok &= np.roll(air, s, axis=ax)
        ok &= np.isfinite(d) & np.all(np.isfinite(E), -1)
        mag = np.linalg.norm(E, axis=-1)
        out[pairing] = float(np.median(np.abs(d[ok]) / mag[ok])) if ok.any() else float("nan")
        out["n_points"] = int(ok.sum())
    return out


def check_files(stage="Normal"):
    """Completeness table for the 18 field files + the wide file."""
    rows = []
    for p in expected_files(stage) + [FIELD_DIR / WIDE_FILE]:
        row = {"file": p.name, "present": p.exists()}
        if p.exists():
            pts, E = read_fld(p)
            row["rows"] = len(pts)
            try:
                g = Grid(pts, E)
                row.update(full_grid=g.full, z_fastest=g.z_fastest,
                           shape="x".join(str(len(a)) for a in g.axes), step_mm=g.step,
                           range_mm=f"{g.axes[0][0]:.0f}..{g.axes[0][-1]:.0f}")
            except ValueError as e:
                row["full_grid"] = f"NO ({e})"
            r = np.linalg.norm(pts, axis=1)
            bad = ~np.all(np.isfinite(E), axis=1)
            row["n_nan"] = int(bad.sum())
            row["nan_r_mm"] = f"{r[bad].min():.0f}-{r[bad].max():.0f}" if bad.any() else "-"
            row["finite_inside_r88"] = bool(np.all(np.isfinite(E[r < 88.0])))
            row["n_inside_r88"] = int((r < 88.0).sum())
        rows.append(row)
    return rows


def load_hfss_fields(stage="Normal"):
    """-> f (3,), Grid list [antenna][freq] for antennas T1..T6 (file index = T#)."""
    out = [[None] * len(FREQ_TAGS) for _ in range(N_ANT)]
    axes0 = None
    for fi, tag in enumerate(FREQ_TAGS):
        for t in range(1, N_ANT + 1):
            g = Grid(*read_fld(FIELD_DIR / f"E_{stage}_T{t}_{tag}GHz.fld"))
            if axes0 is None:
                axes0 = g.axes
            elif not all(np.allclose(a, b) for a, b in zip(axes0, g.axes)):
                raise ValueError("field files are on different grids")
            out[t - 1][fi] = g
    return np.array(list(FREQ_TAGS.values())), out


def hfss_fields_at(grids, pts_mm):
    """(6, F, P, 3) fields of every antenna at pts by trilinear interpolation (exact on nodes)."""
    return np.stack([np.stack([g.sample(pts_mm) for g in row]) for row in grids])


def locate_antennas(grids, f_index=1, r_shell=(89.0, 93.0)):
    """Feed direction of each antenna from its own field: |E|-weighted centroid of the strongest
    1 % of air points in the gap between skin and antenna. Returns (6, 3) unit vectors and the
    dominant tangential polarisation ('theta' or 'phi') fraction."""
    dirs, pol = [], []
    for row in grids:
        g = row[f_index]
        P = g.points().reshape(-1, 3)
        E = g.E.reshape(-1, 3)
        r = np.linalg.norm(P, axis=1)
        sel = (r >= r_shell[0]) & (r <= r_shell[1]) & np.all(np.isfinite(E), 1)
        mag = np.linalg.norm(E[sel], axis=1)
        top = mag >= np.quantile(mag, 0.99)
        Pt, w = P[sel][top], mag[top]
        c = (Pt * w[:, None]).sum(0) / w.sum()
        u = c / np.linalg.norm(c)
        dirs.append(u)
        # polarisation at the strongest points: |E.theta^| vs |E.phi^|
        th = np.arccos(np.clip(u[2], -1, 1))
        ph = np.arctan2(u[1], u[0])
        e_th = np.array([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)])
        e_ph = np.array([-np.sin(ph), np.cos(ph), 0.0])
        Et = E[sel][top]
        a_th = np.sqrt(np.mean(np.abs(Et @ e_th) ** 2))
        a_ph = np.sqrt(np.mean(np.abs(Et @ e_ph) ** 2))
        pol.append(a_th / (a_th + a_ph))
    return np.array(dirs), np.array(pol)


def model_fields(model, p, f_hz, pts_mm, chunk=6000):
    """Forward-model substitute: (6, F, P, 3) total E of each antenna (T1..T6) at pts."""
    out = np.zeros((N_ANT, len(f_hz), len(pts_mm), 3), complex)
    for a in range(N_ANT):
        for s in range(0, len(pts_mm), chunk):
            out[a, :, s:s + chunk] = model.fields(p, f_hz, pts_mm[s:s + chunk], a)
    return out
