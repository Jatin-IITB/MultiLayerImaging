"""Readers for HFSS complex E-field exports and a model-based substitute.

Expected HFSS files (not yet delivered): data/fields/E_Normal_T{t}_{3p4,3p6,3p8}GHz.fld, one per
antenna excitation (terminal t at 1 W / 0 deg, others matched), Cartesian grid -90..90 mm, 3 mm.
The column order is read from each file's header; nothing is assumed about it beyond the
presence of X, Y, Z and the real/imaginary parts of Ex, Ey, Ez.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from .common import ROOT, N_ANT

FIELD_DIR = ROOT / "data" / "fields"
FREQ_TAGS = {"3p4": 3.4e9, "3p6": 3.6e9, "3p8": 3.8e9}


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


def read_fld(path: str | Path):
    """-> (pts_mm (P, 3), E (P, 3) complex). Coordinates in m are converted to mm."""
    path = Path(path)
    header, rows = [], []
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            toks = [t for t in re.split(r"[\s,;]+", line.strip()) if t]
            if not toks:
                continue
            if all(_is_number(t) for t in toks):
                rows.append([float(t) for t in toks])
            elif not rows:
                header.append(toks)
    names = next((h for h in reversed(header) if len(h) >= 9), None)
    if names is None:
        raise ValueError(f"{path}: no column header with >= 9 names")
    ci = _col_index(names)
    A = np.array(rows)
    pts = A[:, [ci["X"], ci["Y"], ci["Z"]]]
    if np.abs(pts).max() < 1.0:                      # metres -> mm
        pts = pts * 1e3
    E = np.stack([A[:, ci[f"E{a}Re"]] + 1j * A[:, ci[f"E{a}Im"]] for a in "xyz"], -1)
    return pts, E


def load_hfss_fields(stage="Normal"):
    """-> f (3,), pts_mm (P, 3), E (6 antennas, 3 freqs, P, 3)."""
    Es, pts0 = [], None
    for tag in FREQ_TAGS:
        row = []
        for t in range(1, N_ANT + 1):
            pts, E = read_fld(FIELD_DIR / f"E_{stage}_T{t}_{tag}GHz.fld")
            if pts0 is None:
                pts0 = pts
            elif not np.allclose(pts, pts0):
                raise ValueError("field files are on different grids")
            row.append(E)
        Es.append(row)
    E = np.transpose(np.array(Es), (1, 0, 2, 3))
    return np.array(list(FREQ_TAGS.values())), pts0, E


def model_fields(model, p, f_hz, pts_mm, chunk=6000):
    """Forward-model substitute: (6, F, P, 3) total E of each antenna (T1..T6) at pts."""
    out = np.zeros((N_ANT, len(f_hz), len(pts_mm), 3), complex)
    for a in range(N_ANT):
        for s in range(0, len(pts_mm), chunk):
            out[a, :, s:s + chunk] = model.fields(p, f_hz, pts_mm[s:s + chunk], a)
    return out
