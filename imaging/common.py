"""Shared helpers for the imaging study: data, phantom truth, antenna geometry, noise, CSV.

Read-only use of the shared package ``src/adstage`` (loader, glitch masking, ring helpers,
noise model, metrics schema). Nothing here writes outside ``results/imaging``.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from adstage.io.dataset import load_dataset          # noqa: E402
from adstage.noise.model import PROFILES, realise     # noqa: E402
from adstage.results import SCHEMA, append_row, git_hash  # noqa: E402
from adstage.ring import pairs_at_distance, ring_average, ring_distance  # noqa: E402

OUT = ROOT / "results" / "imaging"
FIG = OUT / "figures"
METRICS_CSV = OUT / "metrics_imaging.csv"
TRACK = "A-img"

# ----------------------------------------------------------------------------------------------
# Phantom (MODEL_CARD.md Part 1; Shehab et al. 2025 Tables 5-6)
# ----------------------------------------------------------------------------------------------
R_SKIN, R_FAT, R_SKULL, R_CSF = 88.0, 87.5, 86.5, 83.5          # mm, fixed
RADII = {  # gray, white, hippocampus outer radii (mm)
    "Normal": (83.0, 76.0, 25.0), "MCI": (83.0, 76.0, 21.25), "Mild": (70.55, 64.6, 17.5),
    "Moderate": (66.05, 60.8, 12.5), "Severe": (62.25, 57.0, 7.5)}
MATS = {  # (eps_r, sigma S/m) per stage: hippocampus, white, gray, CSF
    "Normal": {"hip": (47.7, 2.42), "white": (35.3, 1.65), "gray": (47.7, 2.42), "csf": (65.0, 4.27)},
    "Mild": {"hip": (39.11, 5.687), "white": (31.77, 2.39), "gray": (40.3, 5.203), "csf": (55.25, 4.91)},
    "Moderate": {"hip": (38.39, 5.92), "white": (31.064, 2.722), "gray": (39.11, 5.687),
                 "csf": (48.75, 5.337)},
    "Severe": {"hip": (37.2, 6.413), "white": (30.35, 2.88), "gray": (38.39, 5.92), "csf": (32.5, 6.405)},
}
# ASSUMED (not recorded in MODEL_CARD.md; literature values near 3.5 GHz): flagged in the report.
FIXED = {"skull": (10.8, 0.61), "fat": (10.5, 0.42), "skin": (37.0, 2.0)}
ASSUMPTIONS = [
    "Skin/fat/skull materials are not in MODEL_CARD.md (OPEN-GUI): assumed skin 37/2.0, "
    "fat 10.5/0.42, skull 10.8/0.61 (eps_r / S/m).",
    "Ring z-sign and antenna orientation are OPEN in MODEL_CARD.md: ring assumed at +z "
    "(polar angle 60.5 deg), broadside facing the origin; S is mirror-symmetric in z so the sign "
    "does not affect S, only image coordinates.",
    "Antenna = point electric dipole at the feed point, tangential to the sphere; the "
    "polarisation (theta^ vs phi^) is chosen by the fit to the HFSS Normal ring couplings.",
    "Normal-stage materials are back-calculated values (MODEL_CARD caveat).",
    "The HFSS materials are static (no dispersion); the model uses the same constant eps_r, sigma.",
]


@dataclass
class HeadParams:
    """The ~10 numbers that describe the phantom (radii mm; eps_r, sigma S/m)."""
    r_gray: float
    r_white: float
    r_hip: float
    gray: tuple
    white: tuple
    csf: tuple
    hip: tuple

    @classmethod
    def stage(cls, s: str) -> "HeadParams":
        rg, rw, rh = RADII[s]
        m = MATS["Normal" if s == "MCI" else s]
        return cls(rg, rw, rh, m["gray"], m["white"], m["csf"], m["hip"])

    def layers(self):
        """[(outer radius mm, eps_r, sigma)] core first."""
        return [(self.r_hip, *self.hip), (self.r_white, *self.white), (self.r_gray, *self.gray),
                (R_CSF, *self.csf), (R_SKULL, *FIXED["skull"]), (R_FAT, *FIXED["fat"]),
                (R_SKIN, *FIXED["skin"])]


def eps_profile(p: HeadParams, r_mm: np.ndarray, f_hz: float = 3.6e9):
    """(eps_r(r), sigma(r)) of the phantom on radii r_mm (outside the skin: vacuum)."""
    r_mm = np.asarray(r_mm, float)
    er = np.ones_like(r_mm)
    sg = np.zeros_like(r_mm)
    inner = 0.0
    for (ro, e, s) in p.layers():
        sel = (r_mm >= inner) & (r_mm < ro)
        er[sel], sg[sel] = e, s
        inner = ro
    return er, sg


def true_delta(stage: str, r_mm: np.ndarray):
    """True (d eps_r, d sigma) of a stage relative to Normal on radii r_mm."""
    e1, s1 = eps_profile(HeadParams.stage(stage), r_mm)
    e0, s0 = eps_profile(HeadParams.stage("Normal"), r_mm)
    return e1 - e0, s1 - s0


# ----------------------------------------------------------------------------------------------
# Antennas
# ----------------------------------------------------------------------------------------------
R_FEED_MM = 97.55
THETA0_DEG = 60.5
N_ANT = 6


def antenna_positions_mm(z_sign: int = +1) -> np.ndarray:
    """(6, 3) feed positions of antennas T1..T6 (azimuth (t-1)*60 deg)."""
    th = np.deg2rad(THETA0_DEG)
    ph = np.deg2rad(60.0 * np.arange(N_ANT))
    return R_FEED_MM * np.stack([np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph),
                                 z_sign * np.cos(th) * np.ones(N_ANT)], -1)


def dipole_dirs(pol: str, pos: np.ndarray) -> np.ndarray:
    """Unit tangential dipole directions: 'theta' (meridian) or 'phi' (along the ring)."""
    r = np.linalg.norm(pos, axis=-1)
    th = np.arccos(pos[:, 2] / r)
    ph = np.arctan2(pos[:, 1], pos[:, 0])
    if pol == "theta":
        return np.stack([np.cos(th) * np.cos(ph), np.cos(th) * np.sin(ph), -np.sin(th)], -1)
    if pol == "phi":
        return np.stack([-np.sin(ph), np.cos(ph), np.zeros_like(ph)], -1)
    raise ValueError(pol)


def port_positions_mm(port_to_ant) -> np.ndarray:
    """Feed position of the antenna on each Touchstone port (port order)."""
    return antenna_positions_mm()[np.asarray(port_to_ant) - 1]


# ----------------------------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------------------------
def load_config():
    with open(ROOT / "config.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@dataclass
class StageData:
    f_hz: np.ndarray
    S: dict            # stage -> (F, 6, 6) (first simulation of that stage)
    port_to_ant: np.ndarray
    files: dict
    ds: object = field(repr=False, default=None)

    def dS(self, stage: str, ref: str = "Normal") -> np.ndarray:
        return self.S[stage] - self.S[ref]

    @property
    def kmat(self):
        return ring_distance(self.port_to_ant)


def load_stages(cfg=None) -> StageData:
    """Glitch-masked S tensors on the common grid, one (primary) simulation per stage."""
    cfg = cfg or load_config()
    ds = load_dataset(cfg, ROOT, mask=True)
    S, files = {}, {}
    roles = ds.manifest["role"].tolist() if "role" in ds.manifest else ["primary"] * len(ds.files)
    for i, (c, f, role) in enumerate(zip(ds.classes, ds.files, roles)):
        if role == "primary" and c not in S:
            S[c], files[c] = ds.S[i], f
    return StageData(ds.f_hz, S, ds.port_to_ant, files, ds)


def ring_modes(S: np.ndarray, port_to_ant) -> np.ndarray:
    """(..., F, 4) ring-mode curves c_k(f) = mean_t S(t, t+k)."""
    return ring_average(S, port_to_ant)


def noisy(f, S, profile: str, n: int, seed: int) -> np.ndarray:
    """n noisy realisations of S (F, N, N) with the shared noise model."""
    return realise(f, S, PROFILES[profile], n, np.random.default_rng(seed))


# ----------------------------------------------------------------------------------------------
# Metrics CSV (own file; same schema as results/metrics.csv)
# ----------------------------------------------------------------------------------------------
def write_metric(row: dict, cfg=None) -> None:
    cfg = cfg or load_config()
    base = {"git_hash": git_hash(ROOT), "track": TRACK, "model_id": cfg["model_id"],
            "sim_set": cfg["metrics"]["sim_set"]}
    OUT.mkdir(parents=True, exist_ok=True)
    append_row(METRICS_CSV, {**base, **row})
