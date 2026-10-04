"""imaging2 data layer: S-parameter files, glitch masking, antenna order, ground-truth registry.

Read-only use of ``src/adstage`` (Touchstone reader, glitch masking). Nothing here writes
outside ``results/imaging2``.

Conventions (MODEL_CARD Part 5, HFSS geometry audit):
  * antennas T1..T6 at azimuth -90 + 60 (t-1) deg, ring at +z (feed polar 60.5 deg);
  * Touchstone port order Port 1..6 = T4, T3, T2, T1, T6, T5;
  * sector S_k is the 60 deg full-height wedge centred on T_k (S1 frontal, nose at -Y);
  * +X = subject's left, so S2/S3 are left, S5/S6 right.
All S tensors returned here are in ANTENNA order (index 0 = T1).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from adstage.io.masking import mask_glitches       # noqa: E402
from adstage.io.touchstone import read_touchstone  # noqa: E402

RAW = ROOT / "data" / "raw"
OUT = ROOT / "results" / "imaging2"
FIG = OUT / "figures"
CACHE = OUT / "cache"

PORT_TO_ANT = np.array([4, 3, 2, 1, 6, 5])          # Port p+1 carries antenna PORT_TO_ANT[p]
ANT_TO_PORT = np.argsort(PORT_TO_ANT)                # antenna a (0-based) -> port index
N = 6
F_LO, F_HI = 3.2e9, 4.2e9                            # common band of every file used here
GLITCH_THR_DB = -30.0                                # same rule as the main session

SECTOR_NAMES = ["Frontal", "Temporal L", "Parietal L", "Occipital", "Parietal R", "Temporal R"]
SECTOR_SHORT = ["S1 Fr", "S2 TL", "S3 PL", "S4 Oc", "S5 PR", "S6 TR"]
ANT_AZ_DEG = -90.0 + 60.0 * np.arange(N)

# ----------------------------------------------------------------------------------------------
# Paths (reciprocal antenna pairs) and the ring symmetry group D6
# ----------------------------------------------------------------------------------------------
PATHS = [(i, j) for i in range(N) for j in range(i, N)]          # 21, antenna indices
PI = np.array([p[0] for p in PATHS])
PJ = np.array([p[1] for p in PATHS])


def ring_dist(i, j):
    d = abs(i - j) % N
    return min(d, N - d)


PATH_TYPE = np.array([ring_dist(i, j) for i, j in PATHS])        # 0 refl, 1 nb, 2 2nd, 3 opp
TYPE_NAMES = ["reflection", "neighbour", "second-neighbour", "opposite"]


def path_name(p):
    i, j = PATHS[p]
    return f"T{i + 1} refl." if i == j else f"T{i + 1}-T{j + 1}"


def group_maps():
    """The 12 elements of D6 acting on antenna (= sector) indices: 6 rotations x {id, mirror}.
    Mirror x -> -x maps azimuth phi -> 180 - phi, i.e. T_a -> T_(6-a) (0-based a -> -a mod 6):
    T1, T4 fixed, T2<->T6, T3<->T5."""
    maps = []
    for m in (False, True):
        for r in range(N):
            maps.append(np.array([((-a if m else a) + r) % N for a in range(N)]))
    return maps


G = group_maps()
MIRROR = G[N]                                                    # pure mirror (r = 0)


def path_index(i, j):
    i, j = min(i, j), max(i, j)
    return PATHS.index((i, j))


def permute_paths(g):
    """Index array q such that data'[q[p]] = data[p] when antennas are relabelled by g."""
    return np.array([path_index(g[i], g[j]) for i, j in PATHS])


def apply_group(L, g):
    """L (21, ...) path data of a design -> path data of the design transformed by g."""
    out = np.empty_like(L)
    out[permute_paths(g)] = L
    return out


def orbit_ids():
    """(21, 6) orbit index of every (path, sector) pair under D6 (13 orbits)."""
    keys = {}
    out = np.zeros((len(PATHS), N), int)
    for p, (i, j) in enumerate(PATHS):
        for k in range(N):
            cands = []
            for g in G:
                a, b = sorted((g[i], g[j]))
                cands.append((a, b, g[k]))
            key = min(cands)
            out[p, k] = keys.setdefault(key, len(keys))
    return out


ORBIT = orbit_ids()
N_ORBIT = int(ORBIT.max()) + 1

# ----------------------------------------------------------------------------------------------
# Ground truth registry (MODEL_CARD Part 5.1, sims_lobe.csv, Touchstone headers checked by hand)
# ----------------------------------------------------------------------------------------------


@dataclass
class Truth:
    """Geometry/material state of one design. Lobe designs: per-sector CSF expansion e_k (gray
    76-e..83-e, white 25..76-e); uniform designs: explicit radii (gray thickness differs)."""
    kind: str                       # 'lobe' or 'uniform'
    e: np.ndarray                   # (6,) mm (lobe) ; uniform: 83 - r_gray at every sector
    affected: np.ndarray            # (6,) bool: diseased gray/white material in that sector
    tissue_stage: str               # material table for affected gray/white ('Healthy' if none)
    csf_stage: str                  # CSF material (one object -> everywhere)
    hip_stage: str                  # hippocampus material
    r_hip: float
    r_gray: float | None = None     # uniform designs only
    r_white: float | None = None


def lobe(e, stage, r_hip, csf=None, hip=None, affected=None):
    e = np.asarray(e, float)
    aff = (e > 0) if affected is None else np.asarray(affected, bool)
    return Truth("lobe", e, aff, stage if aff.any() else "Healthy", csf or stage, hip or stage, r_hip)


def uniform(stage, r_gray, r_white, r_hip, csf=None, hip=None):
    aff = np.full(N, stage not in ("Healthy", "MCI"))
    return Truth("uniform", np.full(N, 83.0 - r_gray), aff, stage if aff.any() else "Healthy",
                 csf or ("Healthy" if stage == "MCI" else stage), hip or stage, r_hip, r_gray, r_white)


@dataclass
class Design:
    name: str                       # design (geometry) name; meshes of one design share it
    file: str
    mesh: str                       # e.g. 'p6'
    ref: str                        # file of the matched healthy reference
    truth: Truth
    project: str
    group: str                      # leave-one-design-out group
    role: str = "target"            # 'target' (imaged), 'train_only', 'reference'
    S: np.ndarray | None = field(default=None, repr=False)


H6 = "new_with_slices_Healthy_sliced_new.s6p"   # 6 passes, stop rule 1
H7 = "new_with_slices_Healthy_sliced.s6p"       # 7 passes, stop rule 2
V2H = "new_Healthy.s6p"

HEALTHY_LOBE = lobe(np.zeros(N), "Healthy", 25.0)
E_MILD = [0, 7.5, 11.5, 0, 11.5, 7.5]
E_MOD = [11.5, 12.5, 15.5, 0, 15.5, 12.5]
E_SEV = [15.5, 17.5, 18, 11.5, 18, 17.5]
E_LEFT = [0, 7.5, 11.5, 0, 0, 0]

DESIGNS = [
    # healthy meshes: each is the other's 'target' in the healthy control
    Design("Healthy", H7, "p7", H6, HEALTHY_LOBE, "new_with_slices", "Healthy", "target"),
    Design("Healthy", H6, "p6", H7, HEALTHY_LOBE, "new_with_slices", "Healthy", "reference"),
    Design("Mild_lobe", "new_with_slices_Mild_lobe.s6p", "p5", H6,
           lobe(E_MILD, "Mild", 17.5), "new_with_slices", "Mild_lobe"),
    Design("Mild_lobe", "new_with_slices_Mild_lobe_new.s6p", "p6", H7,
           lobe(E_MILD, "Mild", 17.5), "new_with_slices", "Mild_lobe"),
    Design("Moderate_lobe", "new_with_slices_Moderate_lobe.s6p", "p5", H6,
           lobe(E_MOD, "Moderate", 12.5), "new_with_slices", "Moderate_lobe"),
    Design("Moderate_lobe", "new_with_slices_Moderate_lobe_c3.s6p", "p6", H7,
           lobe(E_MOD, "Moderate", 12.5), "new_with_slices", "Moderate_lobe"),
    Design("Severe_lobe", "new_with_slices_Severe_lobe.s6p", "p5", H6,
           lobe(E_SEV, "Severe", 7.5), "new_with_slices", "Severe_lobe"),
    Design("Severe_lobe", "new_with_slices_Severe_lobe_c3.s6p", "p6", H7,
           lobe(E_SEV, "Severe", 7.5), "new_with_slices", "Severe_lobe"),
    Design("LeftOnly", "new_with_slices_LeftOnly_test_c3.s6p", "p6", H6,
           lobe(E_LEFT, "Mild", 17.5), "new_with_slices", "LeftOnly"),
    # MCI: hippocampus material only, CSF healthy (sims_lobe.csv); e = 0
    Design("MCI_lobe", "new_with_slices_MCI_lobe_c3.s6p", "p6", H6,
           lobe(np.zeros(N), "Healthy", 21.25, csf="Healthy", hip="MCI"), "new_with_slices", "MCI_lobe"),
    # uniform v2 project 'new' (MODEL_CARD Part 1 radii); reference = its own healthy head
    Design("Uniform_MCI", "new_MCI.s6p", "v2", V2H, uniform("MCI", 83.0, 76.0, 21.25),
           "new", "Uniform_MCI", "train_only"),
    Design("Uniform_Mild", "new_MildAD.s6p", "v2", V2H, uniform("Mild", 70.55, 64.6, 17.5),
           "new", "Uniform_Mild", "train_only"),
    Design("Uniform_Moderate", "new_ModerateAD.s6p", "v2", V2H, uniform("Moderate", 66.05, 60.8, 12.5),
           "new", "Uniform_Moderate", "train_only"),
    Design("Uniform_Severe", "new_SevereAD.s6p", "v2", V2H, uniform("Severe", 62.25, 57.0, 7.5),
           "new", "Uniform_Severe", "train_only"),
]
REFERENCE_FILES = [H6, H7, V2H]
TARGET_GROUPS = ["Healthy", "Mild_lobe", "Moderate_lobe", "Severe_lobe", "LeftOnly", "MCI_lobe"]
STAGE_OF_GROUP = {"Mild_lobe": "Mild", "Moderate_lobe": "Moderate", "Severe_lobe": "Severe",
                  "LeftOnly": "Mild", "Uniform_Mild": "Mild", "Uniform_Moderate": "Moderate",
                  "Uniform_Severe": "Severe", "Healthy": "Healthy", "MCI_lobe": "Healthy",
                  "Uniform_MCI": "Healthy"}

# ----------------------------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------------------------
_CACHE: dict = {}


def load_file(fname: str):
    """-> (f_hz (201,), S (201, 6, 6) complex, antenna order, glitch-masked, reciprocal-symmetrised
    off the diagonal), plus the mask log."""
    if fname in _CACHE:
        return _CACHE[fname]
    ts = read_touchstone(RAW / fname)
    f = ts.f_hz
    sel = (f >= F_LO - 1) & (f <= F_HI + 1)
    f, s = f[sel], ts.s[sel]
    if len(f) != 201 or abs(np.median(np.diff(f)) - 5e6) > 1:
        raise ValueError(f"{fname}: unexpected grid {len(f)} pts")
    s, log = mask_glitches(f, s, GLITCH_THR_DB)
    s = s[:, ANT_TO_PORT][:, :, ANT_TO_PORT]             # -> antenna order
    s = 0.5 * (s + s.transpose(0, 2, 1))
    _CACHE[fname] = (f, s, log)
    return _CACHE[fname]


def paths_of(S):
    """(F, 6, 6) -> (21, F) reciprocal path data."""
    return S[:, PI, PJ].T


def log_ratio(S, Sref):
    """Complex log-ratio ln(S / S_ref) per path: real = amplitude change (Np), imag = phase (rad)."""
    return np.log(paths_of(S) / paths_of(Sref))


def all_designs():
    for d in DESIGNS:
        if d.S is None:
            d.S = load_file(d.file)[1]
    return DESIGNS


def freq():
    return load_file(H6)[0]


def git_rev():
    import subprocess
    try:
        h = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                           text=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "imaging2"], capture_output=True,
                               text=True).stdout.strip()
        return h + ("+imaging2-uncommitted" if dirty else "")
    except Exception:
        return "unknown"


def mask_table():
    rows = []
    for fn in sorted({d.file for d in DESIGNS} | set(REFERENCE_FILES)):
        f, _, log = load_file(fn)
        for r in log:
            rows.append(dict(file=fn, f_GHz=round(r["f_GHz"], 4), port_i=r["port_i"], port_j=r["port_j"],
                             ant_i=int(PORT_TO_ANT[r["port_i"] - 1]), ant_j=int(PORT_TO_ANT[r["port_j"] - 1]),
                             recip_err_db=round(float(r["recip_err_db"]), 2)))
    return rows
