"""Touchstone v1 (.sNp) reader.

Only the option line (``# <unit> <param> <fmt> R <z0>``) and the port count (from the
``.sNp`` extension, or passed explicitly) are used to decode the data. All ``!`` comment
lines -- design/project names, variables, ``Port[k]`` labels, port impedances -- are kept
verbatim in ``comments`` but are NOT interpreted: exporter headers are unreliable. Labels,
port-to-antenna mapping and geometry come from ``data/sims.csv`` and ``config.yaml``.

Because the option line is itself trusted only as far as the data agree with it,
``plausibility()`` checks the decoded values (|S| <= ~1, angles in [-180, 360], band in
the expected range).

Data are consumed as a token stream: one record = 1 + 2*N^2 numbers, and every record must
start on a fresh line (checked, so a misaligned file fails loudly instead of silently
shifting S-parameters). Matrix order: row-major for N != 2; for N == 2 the Touchstone v1
order S11 S21 S12 S22 is transposed back.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

_FREQ_SCALE = {"HZ": 1.0, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9}
_FORMATS = {"MA", "DB", "RI"}


@dataclass
class Touchstone:
    path: str
    f_hz: np.ndarray                  # (F,)
    s: np.ndarray                     # (F, N, N) complex; s[:, i, j] = S_{i+1, j+1}
    z0: float
    fmt: str
    option_line: str
    raw_pairs: np.ndarray = field(repr=False)   # (F, N*N, 2) numbers as written
    comments: list[str] = field(default_factory=list, repr=False)  # untrusted, not parsed

    @property
    def n_ports(self) -> int:
        return self.s.shape[1]


def _n_ports_from_name(path: Path) -> int | None:
    m = re.search(r"\.s(\d+)p$", path.name, flags=re.IGNORECASE)
    return int(m.group(1)) if m else None


def _parse_option_line(line: str) -> tuple[float, str, float]:
    unit, param, fmt, z0 = "GHZ", "S", "MA", 50.0      # Touchstone defaults
    toks = line[1:].split("!")[0].upper().split()
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in _FREQ_SCALE:
            unit = t
        elif t in _FORMATS:
            fmt = t
        elif t in {"S", "Y", "Z", "H", "G"}:
            param = t
        elif t == "R":
            z0 = float(toks[i + 1])
            i += 1
        else:
            raise ValueError(f"Unknown token {t!r} in option line {line!r}")
        i += 1
    if param != "S":
        raise NotImplementedError(f"Only S-parameters are supported, option line says {param}")
    return _FREQ_SCALE[unit], fmt, z0


def _to_complex(a: np.ndarray, b: np.ndarray, fmt: str) -> np.ndarray:
    if fmt == "RI":
        return a + 1j * b
    mag = a if fmt == "MA" else 10.0 ** (a / 20.0)
    return mag * np.exp(1j * np.deg2rad(b))


def read_touchstone(path: str | Path, n_ports: int | None = None) -> Touchstone:
    path = Path(path)
    n = n_ports or _n_ports_from_name(path)
    if n is None:
        raise ValueError(f"Cannot infer port count from {path.name}; pass n_ports")

    option_line = None
    scale = fmt = z0 = None
    comments: list[str] = []
    tokens: list[float] = []
    line_start: list[bool] = []       # token is the first number on its line

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("["):
            raise NotImplementedError("Touchstone v2 keyword files are not supported")
        if line.startswith("!"):
            comments.append(line)
            continue
        if line.startswith("#"):
            if option_line is None:       # spec: only the first option line counts
                option_line = line
                scale, fmt, z0 = _parse_option_line(line)
            continue
        vals = line.split("!")[0].split()
        for k, v in enumerate(vals):
            tokens.append(float(v))
            line_start.append(k == 0)

    if option_line is None:
        raise ValueError(f"{path.name}: no option line")

    rec = 1 + 2 * n * n
    tok = np.asarray(tokens)
    starts = np.asarray(line_start)
    if tok.size % rec:
        raise ValueError(f"{path.name}: {tok.size} numbers is not a multiple of record size "
                         f"{rec} (N={n})")
    n_f = tok.size // rec
    if not starts[::rec].all():
        bad = int(np.flatnonzero(~starts[::rec])[0])
        raise ValueError(f"{path.name}: record {bad} does not start on a new line (misaligned)")

    tok = tok.reshape(n_f, rec)
    f_hz = tok[:, 0] * scale
    if np.any(np.diff(f_hz) <= 0):
        raise ValueError(f"{path.name}: frequencies not strictly increasing")
    pairs = tok[:, 1:].reshape(n_f, n * n, 2)
    s = _to_complex(pairs[..., 0], pairs[..., 1], fmt).reshape(n_f, n, n)
    if n == 2:
        s = s.transpose(0, 2, 1)
    return Touchstone(str(path), f_hz, s, z0, fmt, option_line, pairs, comments)


def plausibility(ts: Touchstone, band_hz: tuple[float, float] = (1e8, 1e11)) -> list[str]:
    """Data-based checks that the option line decodes the numbers sensibly.

    Returns a list of problems (empty = plausible)."""
    problems = []
    a, b = ts.raw_pairs[..., 0], ts.raw_pairs[..., 1]
    if ts.fmt == "MA" and (a.min() < 0 or a.max() > 1.05):
        problems.append(f"MA magnitudes outside [0, 1.05]: [{a.min():.3g}, {a.max():.3g}]")
    if ts.fmt == "DB" and a.max() > 0.5:
        problems.append(f"DB magnitudes > 0.5 dB (max {a.max():.3g}) - maybe not dB?")
    if ts.fmt in {"MA", "DB"} and (b.min() < -180.5 or b.max() > 360.5):
        problems.append(f"angles outside [-180, 360] deg: [{b.min():.3g}, {b.max():.3g}] "
                        "- maybe radians or RI?")
    if ts.fmt == "RI" and np.abs(ts.s).max() > 1.05:
        problems.append(f"|S| up to {np.abs(ts.s).max():.3g} in RI data")
    if ts.f_hz.min() < band_hz[0] or ts.f_hz.max() > band_hz[1]:
        problems.append(f"band {ts.f_hz.min():.4g}-{ts.f_hz.max():.4g} Hz outside expected "
                        f"{band_hz[0]:.3g}-{band_hz[1]:.3g} Hz - wrong frequency unit?")
    return problems
