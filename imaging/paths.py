"""Data-driven propagation-path test on the HFSS ring couplings (no forward model).

Measured: group delay (linear phase fit over the band) and envelope peak time of each ring mode
c_k(f) and of dS_k (stage - Normal). The unknown antenna/feed delay is removed with the k = 1
path, whose straight line between neighbours only grazes the skin (closest approach 87.8 mm),
i.e. travels in air: 2 t_ant = gd_1 - chord_1 / c.
Candidate k = 3 paths: straight chord through the head (layered optical path), and the
shortest air path around the sphere (tangent + great-circle arc + tangent, 'creeping').
"""
from __future__ import annotations

import numpy as np

from .common import HeadParams, R_SKIN, antenna_positions_mm, ring_modes
from .timedomain import C0, TimeResponse, delay_layered


def group_delay(f, x):
    return float(-np.polyfit(2 * np.pi * f, np.unwrap(np.angle(x)), 1)[0])


def peak_time(f, x, tmax=12e-9):
    t = np.arange(0, tmax, 5e-12)
    tr = TimeResponse(f, x[None])
    return float(t[np.argmax(np.abs(tr(t[None]))[0])])


def creeping_length_mm(a, b, R=R_SKIN):
    d = np.linalg.norm(a)
    gamma = np.arccos(np.clip(a @ b / (d * np.linalg.norm(b)), -1, 1))
    alpha = np.arccos(R / d)
    arc = max(gamma - 2 * alpha, 0.0) * R
    return float(2 * np.sqrt(d * d - R * R) + arc), float(np.degrees(gamma))


def run(sd):
    f = sd.f_hz
    c = {s: ring_modes(sd.S[s], sd.port_to_ant) for s in sd.S}
    pos = antenna_positions_mm()
    lay = [(r, e) for (r, e, s) in HeadParams.stage("Normal").layers()]
    rows = []
    for k in range(1, 4):
        a, b = pos[0], pos[k]
        chord = float(np.linalg.norm(b - a))
        closest = float(np.linalg.norm(a + ((b - a) @ -a) / chord ** 2 * (b - a)))
        straight = float(delay_layered(a, b[None], lay)[0])
        creep, gamma = creeping_length_mm(a, b)
        rows.append(dict(k=k, sep_deg=gamma, chord_mm=chord, chord_closest_to_centre_mm=closest,
                         t_straight_ns=straight * 1e9, t_air_creep_ns=creep * 1e-3 / C0 * 1e9,
                         creep_len_mm=creep))
    meas = {}
    for s in c:
        meas[s] = {f"gd_k{k}_ns": group_delay(f, c[s][:, k]) * 1e9 for k in range(4)}
        meas[s].update({f"peak_k{k}_ns": peak_time(f, c[s][:, k]) * 1e9 for k in range(4)})
        if s != "Normal":
            d = c[s] - c["Normal"]
            meas[s].update({f"gd_dS_k{k}_ns": group_delay(f, d[:, k]) * 1e9 for k in range(4)})
    two_tant = meas["Normal"]["gd_k1_ns"] - rows[0]["chord_mm"] * 1e-3 / C0 * 1e9
    for r in rows:
        r["pred_straight_ns"] = two_tant + r["t_straight_ns"]
        r["pred_creep_ns"] = two_tant + r["t_air_creep_ns"]
        r["measured_gd_Normal_ns"] = meas["Normal"][f"gd_k{r['k']}_ns"]
    return dict(paths=rows, measured=meas, two_t_ant_ns=two_tant)
