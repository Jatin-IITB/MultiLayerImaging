"""Blind design Test_B (main session): protocol, validation on the known lobe designs, blind estimates.

    python scripts/15_test_b.py --validate   # known designs only; never opens Test_B
    python scripts/15_test_b.py --blind      # Test_B; refuses unless results/05_lobe/test_b/protocol.md is committed

Writes results/05_lobe/test_b/{validation.md, validation_*.csv} (--validate) and {report.md, estimates.csv,
statistics.csv} (--blind). Reads, never writes, the frozen rule, the committed predictions and the C6 table.
Blind rules (user, 2026-10-04): Test_B's geometry is learned from its S-parameters only; its header comments are
never read or printed (only the frequency/S data lines are parsed by adstage.io.touchstone).

What is reported (fixed in protocol.md before Test_B is loaded):
 1. Frozen rule (results/04/frozen_rule.json, unchanged): detection label (R31) and staging labels (three: R21;
    three_merged: R32) of the clean file, each with its signed margin to the label edge and that margin over the
    round-2 rulers (A1 = max(one-pass yardstick, boundary SD); quadrature with the ±0.5 dB measurement spread); label
    fractions of 300 noisy draws (typical profile + setup perturbation + ±0.5 dB per-port gain).
 2. Power-based indices: the reference-free left-right power indices (all / neighbour / second-neighbour paths) and the
    reflection mirror pairs against the R1c ruler; the front-back power index (all / neighbour paths) of Test_B minus
    Healthy_sliced_new against max(one-pass yardstick, sqrt2 x symmetry floor).
 3. [POST HOC] Phase cross-ratio counts >= 3x the R1c clean ruler (band mean and 3.30-3.65 GHz), with signs.
 4. Localisation estimate (side and sectors S1..S6), from two statistics fixed below and validated here.
    (a) Sector pattern fit [reference-based, primary]: y_k = mean phase change (deg, 3.2-3.5 GHz) of the two
        neighbour paths at antenna Tk, Test_B against Healthy_sliced_new. Model y = c + a K(w) x with x in {0,1}^6 the
        affected sectors (not all equal), K(w) circulant (w, 1, w), c free, a < 0 (disease delays the neighbour paths:
        C4). All 62 patterns are fitted; the best (least rms residual) is taken.
        Fit-rejection rule: the pattern is accepted only if (i) the relative-pattern contrast r0 = rms(y - mean y) is
        >= 2x the null contrast (largest r0 of the uniform-involvement designs: Healthy_sliced vs Healthy_sliced_new,
        MCI_lobe_c3, Severe_lobe, Severe_lobe_c3), (ii) the best residual is <= 0.5 r0 (>= 75% of the relative variance
        explained) and (iii) a < 0. Per-sector confidence: (residual with that sector flipped - best residual) / null
        contrast; >= 3 established, 2-3 sensitive, < 2 uncertain. If rejected: no sector pattern; extent from the ring
        mean g = mean(y): |g| >= 2x the healthy-twin |g| -> "diffuse: all six sectors", else "no sector involvement".
        w is chosen on the known designs (grid 0.2/0.3/0.4/0.5; most exact patterns, then most correct sectors, then
        smallest residual) and checked leaving one design group out.
    (b) Mirror test [reference-free, confirmation]: the 26 statistics that were informative for LeftOnly in the C6
        table (0f97bb2). Votes = those with |T| >= 2x their R1c clean ruler; 'left' if the sign equals LeftOnly's.
        Side = left / right if >= 3 votes and >= 80% agree; 'mixed' if >= 3 votes otherwise; 'none' if < 3 votes.
        Signs of these statistics replicated 26/26 on RightOnly (C6); their sizes did not (12/26 within tolerance).
    Final side: both agree -> that side ('established' if >= 3 mirror votes are >= 3x, else 'sensitive'); fit only ->
    that side, 'sensitive'; conflict -> 'undetermined'; fit symmetric (left = right sectors) and mirror 'none' ->
    'no left-right asymmetry'. Hippocampus/core changes are not assessable (MCI_lobe: 0 of 228 features) and are
    not called.
References: Healthy_sliced_new (stop rule 1, 6 passes; matches Test_B's stop rule 1) for every reference-based number;
Healthy_sliced (7 passes) reported as a secondary check only. One solve per design: within-simulation statements.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from adstage.config import load_config  # noqa: E402
from adstage.features.metrics import to_ring_order  # noqa: E402
from adstage.frozen import apply_rule  # noqa: E402
from adstage.noise.model import PROFILES  # noqa: E402
from adstage.pipeline.augment import draws  # noqa: E402
from adstage.results import git_hash  # noqa: E402


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L7 = _load("lobe07", "07_lobe.py")
L8 = _load("lobe08", "08_lobe_mesh.py")
L9 = _load("lobe09", "09_lobe_tests.py")
R10 = _load("rev10", "10_lobe_review.py")
R11 = _load("rev11", "11_review2.py")
LOBE = ROOT / "results" / "05_lobe"
OUT = LOBE / "test_b"
PROTOCOL = OUT / "protocol.md"
TESTB_FILE = "new_with_slices_Test_B.s6p"
TB = "Test_B"
H6, H7, LO, RO, MCI = R11.H6, R11.H7, R11.LO, "RightOnly_test", R11.MCI
SYM = R11.SYM
BAND = (3.2e9, 3.5e9)
W_GRID = (0.2, 0.3, 0.4, 0.5)
UNIFORM = [(H7, H6), (MCI, H6), ("Severe_lobe", H6), ("Severe_lobe_c3", H7)]   # null contrast designs (design, ref)
GROUPS = [[H6, H7], ["Mild_lobe", "Mild_lobe_new"], ["Moderate_lobe", "Moderate_lobe_c3"],
          ["Severe_lobe", "Severe_lobe_c3"], [LO], [RO], [MCI]]
SECT = ["S1 frontal", "S2 temporal L", "S3 parietal L", "S4 occipital", "S5 parietal R", "S6 temporal R"]
C6_BLOBS = {"rightonly_predictions.csv": "c03834e756300d21ad378acbae24ba0f915b901b"}
md = L7.md
tier = R10.tier


# ======================================================================== statistics
def nb_phase(f, S, Sref):
    """y_k: mean phase change (deg) over BAND of the two neighbour paths at antenna k, S against Sref (reciprocal mean)."""
    m = R11.fmask(f, BAND)
    Sb, Rb = R11.sbar(S), R11.sbar(Sref)
    ph = np.degrees(np.angle(Sb[m] / Rb[m])).mean(0)          # (6, 6)
    return np.array([0.5 * (ph[k, (k - 1) % 6] + ph[k, (k + 1) % 6]) for k in range(6)])


PATS = [np.array(x) for x in itertools.product([0, 1], repeat=6) if 0 < sum(x) < 6]


def kmat(w):
    M = np.eye(6)
    for k in range(6):
        M[k, (k - 1) % 6] = M[k, (k + 1) % 6] = w
    return M


def fit_pattern(y, x, w):
    A = np.c_[np.ones(6), kmat(w) @ x]
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(np.sqrt(np.mean((y - A @ coef) ** 2))), coef


def localise(y, w, null_contrast, healthy_g):
    """Sector-pattern fit with the fit-rejection rule. Returns a dict (see module docstring)."""
    r0 = float(np.std(y))
    fits = []
    for x in PATS:
        r, coef = fit_pattern(y, x, w)
        if coef[1] < 0:
            fits.append((r, x, coef))
    fits.sort(key=lambda t: t[0])
    g = float(np.mean(y))
    out = {"r0 (relative-pattern rms, deg)": r0, "contrast / null": r0 / null_contrast, "ring mean g (deg)": g,
           "|g| / healthy-twin |g|": abs(g) / healthy_g}
    if not fits:
        out.update(accepted=False, reason="no pattern with a < 0")
    else:
        r1, x1, c1 = fits[0]
        out.update({"best pattern": "".join(str(i + 1) for i in range(6) if x1[i]), "best residual (deg)": r1,
                    "a (deg)": float(c1[1]), "c (deg)": float(c1[0]),
                    "second pattern": "".join(str(i + 1) for i in range(6) if fits[1][1][i]) if len(fits) > 1 else "",
                    "second residual (deg)": fits[1][0] if len(fits) > 1 else np.nan})
        ok = (r0 >= 2 * null_contrast) and (r1 <= 0.5 * r0)
        out["accepted"] = bool(ok)
        out["reason"] = ("accepted" if ok else "; ".join(
            s for s, bad in (("contrast < 2x null", r0 < 2 * null_contrast), ("residual > 0.5 r0", r1 > 0.5 * r0)) if bad))
    calls, conf = [], []
    if out["accepted"]:
        for k in range(6):
            x2 = x1.copy()
            x2[k] = 1 - x2[k]
            if 0 < x2.sum() < 6:
                r2, cf2 = fit_pattern(y, x2, w)
                r2 = r2 if cf2[1] < 0 else np.inf
            else:                                              # flipping makes the pattern uniform: c absorbs it
                r2 = r0
            q = min((r2 - r1) / null_contrast, 99.0)            # 99 = no physical (a < 0) fit with that sector flipped
            conf.append(q)
            calls.append(("affected" if x1[k] else "not affected") if q >= 2 else "uncertain")
        out["pattern call"] = out["best pattern"]
    else:
        diffuse = abs(g) >= 2 * healthy_g
        q = abs(g) / healthy_g
        for k in range(6):
            conf.append(q if diffuse else np.nan)
            calls.append("affected" if diffuse else "not affected")
        out["pattern call"] = "123456 (diffuse)" if diffuse else "none"
    out["sector calls"] = calls
    out["sector confidence"] = conf
    return out


def fit_side(loc):
    if not loc["accepted"]:
        return "symmetric"
    p = loc["best pattern"]
    left, right = sum(c in p for c in "23"), sum(c in p for c in "56")
    return "left" if left > right else ("right" if right > left else "symmetric")


class Mirror:
    """Reference-free mirror statistics and their R1c rulers (as in scripts/13_review2_misc.py)."""

    def __init__(self, f, Sd):
        self.f = f
        self.msk = R11.fmask(f, R11.LRBAND)
        self.Sd = Sd
        self._c, self._cp, self._r = {}, {}, {}
        c6 = pd.read_csv(LOBE / "rightonly_predictions.csv")
        self.table = c6[~c6.statistic.str.endswith("(mirror-invariant)")].reset_index(drop=True)
        self.inf = self.table[self.table["sign test informative"]].reset_index(drop=True)

    def cp(self, d):
        if d not in self._cp:
            self._cp[d] = R11.lr_cr_phase(self.Sd[d])
        return self._cp[d]

    def values(self, d):
        if d not in self._c:
            cp = self.cp(d)
            ms = R10.mirror_stats(self.f, self.Sd[d])
            v = {}
            for _, r in self.table.iterrows():
                if r.statistic.startswith("phase cross-ratio "):
                    k = r.statistic[len("phase cross-ratio "):]
                    m_ = np.ones(len(self.f), bool) if r.frequencies.startswith("band mean") else self.msk
                    v[(r.statistic, r.frequencies)] = float(cp[k][m_].mean())
                else:
                    v[(r.statistic, r.frequencies)] = float(ms[r.statistic][0])
            self._c[d] = v
        return self._c[d]

    def ruler(self, key, exclude=None):
        if (key, exclude) in self._r:
            return self._r[(key, exclude)]
        null = [self.values(d)[key] for d in SYM if d != exclude]
        if key[0].startswith("phase cross-ratio "):
            k = key[0][len("phase cross-ratio "):]
            m_ = np.ones(len(self.f), bool) if key[1].startswith("band mean") else self.msk
            yd = max(abs(float(self.cp(b)[k][m_].mean() - self.cp(a)[k][m_].mean()))
                     for a, b in L8.PAIRS.values())
        else:
            yd = max(abs(self.values(b)[key] - self.values(a)[key]) for a, b in L8.PAIRS.values())
        self._r[(key, exclude)] = max(float(np.max(np.abs(null))), yd)
        return self._r[(key, exclude)]

    def side(self, d):
        rows = []
        for _, r in self.inf.iterrows():
            key = (r.statistic, r.frequencies)
            v, ru = self.values(d)[key], self.ruler(key, exclude=d if d in SYM else None)
            rows.append({"statistic": r.statistic, "frequencies": r.frequencies, "value": v, "ruler": ru,
                         "ratio": abs(v) / ru, "LeftOnly": r.LeftOnly, "left-like": bool(np.sign(v) == np.sign(r.LeftOnly))})
        t = pd.DataFrame(rows)
        votes = t[t.ratio >= 2]
        n3 = int((t.ratio >= 3).sum())
        if len(votes) < 3:
            s = "none"
        else:
            fl = float(votes["left-like"].mean())
            s = "left" if fl >= 0.8 else ("right" if fl <= 0.2 else "mixed")
        return s, len(votes), n3, t

    def counts(self, d):
        out = {}
        for bn in ("band mean 3.2-4.2", "3.30-3.65 GHz"):
            sub = self.table[(self.table.frequencies == bn) & self.table.statistic.str.startswith("phase cross-ratio")]
            vals = [(r.statistic, self.values(d)[(r.statistic, bn)], self.ruler((r.statistic, bn), d if d in SYM else None))
                    for _, r in sub.iterrows()]
            out[bn] = [(s, v, v / ru) for s, v, ru in vals if abs(v) / ru >= 3]
        return out


def final_side(fs, ms, n3):
    if fs in ("left", "right") and ms == fs:
        return fs, "established" if n3 >= 3 else "sensitive"
    if fs in ("left", "right") and ms in ("none", "mixed"):
        return fs, "sensitive (reference-based fit only)"
    if fs in ("left", "right") and ms in ("left", "right"):
        return "undetermined", "fit and mirror test disagree"
    if fs == "symmetric" and ms in ("left", "right"):
        return ms, "sensitive (mirror test only)"
    if ms == "mixed":
        return "undetermined", "mirror test mixed, fit symmetric"
    return "no left-right asymmetry", "-"


def truth_of(man):
    t = {}
    for _, r in man.iterrows():
        s = str(r.get("sectors_affected", ""))
        t[r.design] = "".join(c for c in "123456" if f"S{c}" in s)
    return t


def ref_of(man):
    return {r.design: (H7 if (r.stop_rule == 2 and r.design != H7) or r.design == H6 else H6) for _, r in man.iterrows()}


def score_pattern(call_calls, truth):
    tr = [str(k + 1) in truth for k in range(6)]
    hit = sum(c == "affected" and t for c, t in zip(call_calls, tr))
    fa = sum(c == "affected" and not t for c, t in zip(call_calls, tr))
    miss = sum(c == "not affected" and t for c, t in zip(call_calls, tr))
    cr = sum(c == "not affected" and not t for c, t in zip(call_calls, tr))
    unc = sum(c == "uncertain" for c in call_calls)
    exact = unc == 0 and fa == 0 and miss == 0
    return {"hits": hit, "false alarms": fa, "misses": miss, "correct rejections": cr, "uncertain": unc, "exact": exact}


def truth_side(t):
    left, right = sum(c in t for c in "23"), sum(c in t for c in "56")
    return "left" if left > right else ("right" if right > left else "no left-right asymmetry")


def choose_w(Y, truth, refd, designs, null_contrast, healthy_g):
    best = None
    for w in W_GRID:
        sc = [score_pattern(localise(Y[d], w, null_contrast, healthy_g)["sector calls"], truth[d]) for d in designs]
        key = (sum(s["exact"] for s in sc), sum(s["hits"] + s["correct rejections"] for s in sc))
        res = sum(localise(Y[d], w, null_contrast, healthy_g).get("best residual (deg)", 0) for d in designs)
        cand = (key[0], key[1], -res, w)
        if best is None or cand > best:
            best = cand
    return best[3]


# ======================================================================== frozen rule and indices
def frozen_block(f, Sd, d, R, rule, cfg, n, seed_tag):
    """Clean labels with margins (round-2 rulers) and noisy-draw fractions for design d."""
    r6 = pd.read_csv(LOBE / "review2" / "R6_A28_rulers.csv")
    tb_sd = float(r6[r6.rule == "binary"]["boundary SD"].iloc[0])
    cfg_u = load_config(ROOT, "config_repeats.yaml")
    from adstage.features.ring_features import features
    from adstage.io.dataset import load_dataset
    du = load_dataset(cfg_u, ROOT)
    Xu, nu, _, _ = features(du.f_hz, to_ring_order(du.S, du.port_to_ant))
    ucls = list(du.classes)
    rng = np.random.default_rng([cfg["seed"], 111])
    fro = {k: sorted(float(p.split(" at ")[1]) for p in v.split(", ")) for k, v in L7.boundaries(rule).items()}
    bfro = {"three": fro["three (R21)"], "three_merged": fro["three_merged (R32)"]}
    bdefs = {"three": ("R21", [["Normal"], ["Mild"], ["Severe"]]),
             "three_merged": ("R32", [["Normal"], ["Mild", "Moderate"], ["Severe"]])}
    bsd = {}
    for sch, (ft, cls) in bdefs.items():
        sols = [[s for s, c in enumerate(ucls) if c in mem] for mem in cls]
        bb = []
        for _ in range(3000):
            mu = [np.mean([float(Xu[s][nu.index(ft)]) for s in rng.choice(ss, len(ss))]) for ss in sols]
            bb.append(sorted(0.5 * (mu[i] + mu[i + 1]) for i in range(2)))
        bsd[sch] = np.array(bb).std(0, ddof=1)
    rows = []
    for sch, ft in (("binary", "R31"), ("three", "R21"), ("three_merged", "R32")):
        x = float(R["Q"][d][ft][0])
        lab, mg = R10.edge_margin(rule, sch, x)
        sb = tb_sd if sch == "binary" else float(bsd[sch][int(np.argmin([abs(x - b) for b in bfro[sch]]))])
        yd = R["yard"][ft]
        s05 = R["sd"]["spread ±0.5 dB"][ft] / np.sqrt(2)
        a1 = abs(mg) / max(yd, sb)
        rows.append({"rule": sch, "feature": ft, "value dB": x, "label": lab, "signed margin to label edge (dB)": mg,
                     "yardstick": yd, "boundary SD": sb, "meas SD ±0.5 dB": s05, "A1 ratio": a1,
                     "quadrature ±0.5 dB": abs(mg) / np.sqrt(yd ** 2 + sb ** 2 + s05 ** 2),
                     "verdict (A1)": "determined (>= 3x)" if a1 >= 3 else ("sensitive (2-3x)" if a1 >= 2 else "not determined (< 2x)")})
    ft = pd.DataFrame(rows)
    aug = dict(cfg.get("augment", {}))
    D = draws(f, Sd[d], PROFILES["typical"], n, np.random.default_rng([cfg["seed"], 151, seed_tag]),
              {**aug, "gain_err_db": 0.5})
    lab = apply_rule(ROOT / "results/04/frozen_rule.json", f, D)
    frac = {k: pd.Series(v).value_counts(normalize=True).round(3).to_dict() for k, v in lab.items()}
    ft["noisy draws (typical + ±0.5 dB), label fractions"] = [str(frac["binary_R31"]), str(frac["three"]),
                                                              str(frac["three_merged"])]
    return ft


def index_block(R, d, refs=(H6, H7)):
    rows = []
    for k in ("index: front-back, all paths", "index: front-back, neighbour paths"):
        for ref in refs:
            v = float(R["Q"][d][k][0] - R["Q"][ref][k][0])
            ru = max(R["yard"][k], R["fdiff"][k])
            rows.append({"index": k.replace("index: ", "") + " (power)", "reference": ref, "value dB": v,
                         "clean ruler": ru, "ratio": abs(v) / ru, "tier": tier(abs(v) / ru)})
    return pd.DataFrame(rows)


# ======================================================================== loading Test_B (blind mode only)
def load_test_b(cfg, f_ref):
    from adstage.io.masking import mask_glitches
    from adstage.io.touchstone import plausibility, read_touchstone
    t = read_touchstone(ROOT / cfg["data"]["raw_dir"] / TESTB_FILE)
    probs = plausibility(t, tuple(float(v) for v in cfg["qc"]["expected_band_hz"]))
    if probs:
        raise SystemExit(f"Test_B: implausible decode: {probs}")
    if len(t.f_hz) != len(f_ref) or np.max(np.abs(t.f_hz - f_ref)) > 1:
        raise SystemExit("Test_B: frequency grid differs from the lobe grid")
    s, log = mask_glitches(t.f_hz, t.s, float(cfg["qc"]["glitch_thr_db"]))
    S = to_ring_order(s[None], np.asarray(cfg["ring"]["port_to_ant"]))[0]
    sv = np.linalg.svd(t.s, compute_uv=False)
    off = ~np.eye(6, dtype=bool)
    rec = np.abs(t.s - np.swapaxes(t.s, -1, -2))[:, off] / np.maximum(np.abs(t.s)[:, off], 1e-30)
    qc = {"points": len(t.f_hz), "band GHz": f"{t.f_hz[0] / 1e9:.3f}-{t.f_hz[-1] / 1e9:.3f}",
          "max singular value^2": float((sv ** 2).max()), "max |Sij - Sji| / |Sij| (dB)": float(20 * np.log10(rec.max())),
          "glitch-masked points (-30 dB rule)": len(log)}
    return S, qc


def committed(path):
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    blob = subprocess.run(["git", "hash-object", str(path)], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    head = subprocess.run(["git", "rev-parse", f"HEAD:{rel}"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    log = subprocess.run(["git", "log", "--format=%h", "--", rel], capture_output=True, text=True, cwd=ROOT).stdout.split()
    return blob == head and bool(log), (log[-1] if log else None)


# ======================================================================== main
def main():
    ap = argparse.ArgumentParser()
    g_ = ap.add_mutually_exclusive_group(required=True)
    g_.add_argument("--validate", action="store_true")
    g_.add_argument("--blind", action="store_true")
    ap.add_argument("--n", type=int, default=300)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    gh = git_hash(ROOT)
    for fn, blob in C6_BLOBS.items():
        h = subprocess.run(["git", "hash-object", str(LOBE / fn)], capture_output=True, text=True, cwd=ROOT).stdout.strip()
        if h != blob:
            raise SystemExit(f"{fn} differs from the committed blob")
    if args.blind:
        ok, first = committed(PROTOCOL) if PROTOCOL.exists() else (False, None)
        if not ok:
            raise SystemExit("protocol.md is not committed unchanged; commit the protocol before loading Test_B")
    cfg = load_config(ROOT, "config_lobe.yaml")
    rule = json.loads((ROOT / "results/04/frozen_rule.json").read_text())
    f, Sd, man, _ = L8.load_all(cfg)
    if TB in Sd:
        raise SystemExit("Test_B must not be in the manifest before the blind run")
    truth, refd = truth_of(man), ref_of(man)
    known = [d for d in Sd]
    Y = {d: nb_phase(f, Sd[d], Sd[refd[d]]) for d in known}
    null_contrast = max(float(np.std(nb_phase(f, Sd[a], Sd[b]))) for a, b in UNIFORM)
    healthy_g = abs(float(np.mean(nb_phase(f, Sd[H7], Sd[H6]))))
    MI = Mirror(f, Sd)

    if args.validate:
        loc_designs = [d for d in known if d != H6]               # H6 is the reference of the stop-rule-1 designs
        w_all = choose_w(Y, truth, refd, loc_designs, null_contrast, healthy_g)
        rows, srows = [], []
        for grp in GROUPS:
            held = [d for d in grp if d in loc_designs]
            if not held:
                continue
            w_lodo = choose_w(Y, truth, refd, [d for d in loc_designs if d not in grp], null_contrast, healthy_g)
            for d in held:
                for mode, w in (("in-sample (w on all designs)", w_all), ("leave group out", w_lodo)):
                    loc = localise(Y[d], w, null_contrast, healthy_g)
                    sc = score_pattern(loc["sector calls"], truth[d])
                    ms, nv, n3, _ = MI.side(d)
                    fsd = fit_side(loc)
                    side, conf = final_side(fsd, ms, n3)
                    rows.append({"design": d, "reference": refd[d], "truth sectors": truth[d] or "none", "mode": mode,
                                 "w": w, "accepted": loc["accepted"], "reason": loc["reason"],
                                 "pattern call": loc["pattern call"],
                                 "contrast / null": loc["contrast / null"], "ring mean g (deg)": loc["ring mean g (deg)"],
                                 **sc, "fit side": fsd, "mirror side": ms, "mirror votes (>=2x)": nv, "mirror >=3x": n3,
                                 "final side": side, "side confidence": conf, "truth side": truth_side(truth[d]),
                                 "side correct": side == truth_side(truth[d]),
                                 "sector calls": ", ".join(f"S{k + 1} {c} ({q:.1f})" for k, (c, q) in
                                                           enumerate(zip(loc["sector calls"], loc["sector confidence"])))})
                srows.append({"design": d, **{f"y T{k + 1} (deg)": v for k, v in enumerate(Y[d])}})
        vt, yt = pd.DataFrame(rows), pd.DataFrame(srows)
        vt.to_csv(OUT / "validation_designs.csv", index=False)
        yt.to_csv(OUT / "validation_y.csv", index=False)
        summ = vt.groupby("mode").agg(designs=("design", "count"), exact=("exact", "sum"), hits=("hits", "sum"),
                                      false_alarms=("false alarms", "sum"), misses=("misses", "sum"),
                                      correct_rejections=("correct rejections", "sum"), uncertain=("uncertain", "sum"),
                                      side_correct=("side correct", "sum")).reset_index()
        summ.to_csv(OUT / "validation_summary.csv", index=False)
        L = [f"# Test_B protocol validation on the known lobe designs (code {gh})", "",
             "Test_B was not opened. Every known design is treated as if blind (its own matched healthy reference; "
             "Test_B will use Healthy_sliced_new). Truth = sectors_affected in data/sims_lobe.csv (core not scored).",
             f"Rulers: null contrast {null_contrast:.3f} deg (largest relative-pattern rms of "
             + ", ".join(f"{a} vs {b}" for a, b in UNIFORM) + f"); healthy-twin |ring mean| {healthy_g:.3f} deg "
             f"(Healthy_sliced vs Healthy_sliced_new). Smearing w on all known designs: {w_all}.", "",
             "## Summary", md(summ), "", "## Per design", md(vt, ".2f"), "",
             "## y_k (deg, 3.2-3.5 GHz neighbour-path phase change at antenna k, against the matched reference)",
             md(yt, ".2f"), ""]
        (OUT / "validation.md").write_text("\n".join(L), encoding="utf-8")
        print("\n".join(L[:8]))
        print(md(vt[["design", "mode", "w", "truth sectors", "pattern call", "accepted", "exact", "final side",
                     "side confidence", "truth side"]], ".2f"))
        return

    # ------------------------------------------------------------------ blind run
    S_b, qc = load_test_b(cfg, f)
    Sd = {**Sd, TB: S_b}
    MI = Mirror(f, Sd)
    loc_designs = [d for d in known if d != H6]
    w_all = choose_w(Y, truth, refd, loc_designs, null_contrast, healthy_g)
    yb = nb_phase(f, S_b, Sd[H6])
    yb7 = nb_phase(f, S_b, Sd[H7])
    loc = localise(yb, w_all, null_contrast, healthy_g)
    loc7 = localise(yb7, w_all, null_contrast, healthy_g)
    ms, nv, n3, mt = MI.side(TB)
    fsd = fit_side(loc)
    side, conf = final_side(fsd, ms, n3)
    cnt = MI.counts(TB)
    lr = MI.table[MI.table.statistic.str.startswith("power LR index") | MI.table.statistic.str.contains("refl. vs")]
    lrt = pd.DataFrame([{"statistic": r.statistic, "value": MI.values(TB)[(r.statistic, r.frequencies)],
                         "R1c clean ruler": MI.ruler((r.statistic, r.frequencies)),
                         "ratio": abs(MI.values(TB)[(r.statistic, r.frequencies)]) / MI.ruler((r.statistic, r.frequencies)),
                         "LeftOnly": r.LeftOnly} for _, r in lr.iterrows()])
    R = L8.rulers(f, Sd, cfg, args.n, qfn=L9.ext_quantities)
    frz = frozen_block(f, Sd, TB, R, rule, cfg, args.n, 1)
    idx = index_block(R, TB)
    near = sorted(((float(np.sqrt(np.mean((yb - Y[d]) ** 2))), d) for d in known if d != H6))[:3]
    est = pd.DataFrame([
        {"item": "detection (frozen R31)", "estimate": frz.loc[0, "label"],
         "margin / confidence": f"{frz.loc[0, 'signed margin to label edge (dB)']:+.3f} dB; A1 {frz.loc[0, 'A1 ratio']:.2f}x; "
                                f"{frz.loc[0, 'verdict (A1)']}"},
        {"item": "staging three (R21)", "estimate": frz.loc[1, "label"],
         "margin / confidence": f"{frz.loc[1, 'signed margin to label edge (dB)']:+.3f} dB; A1 {frz.loc[1, 'A1 ratio']:.2f}x; "
                                f"{frz.loc[1, 'verdict (A1)']}"},
        {"item": "staging three_merged (R32)", "estimate": frz.loc[2, "label"],
         "margin / confidence": f"{frz.loc[2, 'signed margin to label edge (dB)']:+.3f} dB; A1 {frz.loc[2, 'A1 ratio']:.2f}x; "
                                f"{frz.loc[2, 'verdict (A1)']}"},
        {"item": "side", "estimate": side, "margin / confidence": f"{conf}; fit side {fsd}, mirror side {ms} "
                                                                  f"({nv} votes >= 2x, {n3} >= 3x)"},
        {"item": "sector pattern", "estimate": loc["pattern call"],
         "margin / confidence": f"fit {'accepted' if loc['accepted'] else 'rejected'} ({loc['reason']}); contrast "
                                f"{loc['contrast / null']:.1f}x null; ring mean {loc['ring mean g (deg)']:+.2f} deg "
                                f"({loc['|g| / healthy-twin |g|']:.1f}x healthy twin)"}] +
        [{"item": SECT[k], "estimate": c, "margin / confidence": f"{q:.1f}x" if np.isfinite(q) else "-"}
         for k, (c, q) in enumerate(zip(loc["sector calls"], loc["sector confidence"]))] +
        [{"item": "secondary reference Healthy_sliced (7 passes)", "estimate": loc7["pattern call"],
          "margin / confidence": f"accepted {loc7['accepted']}; contrast {loc7['contrast / null']:.1f}x"},
         {"item": "most similar known designs (rms of y)", "estimate": ", ".join(d for _, d in near),
          "margin / confidence": ", ".join(f"{r:.2f} deg" for r, _ in near)}])
    est.to_csv(OUT / "estimates.csv", index=False)
    stats = pd.concat([frz.assign(block="frozen rule"), idx.assign(block="front-back index"),
                       lrt.assign(block="left-right power / reflection pairs"), mt.assign(block="mirror test (26)")],
                      ignore_index=True)
    stats.to_csv(OUT / "statistics.csv", index=False)
    ok, first = committed(PROTOCOL)
    L = [f"# Test_B: blind estimates (main session; code {gh}; protocol committed at {first})", "",
         "Test_B was loaded only after the protocol was committed. Its geometry was not read from anything but its "
         "S-parameters; header comments were not read. One solve: within-simulation statements only. "
         "Reference: Healthy_sliced_new (stop rule 1).", "",
         "## QC", md(pd.DataFrame([qc]), ".3f"), "", "## Estimates", md(est), "",
         "## Frozen rule", md(frz, ".3f"), "", "## Power indices",
         "Front-back (Test_B minus reference):", md(idx, ".3f"), "",
         "Left-right (reference-free) and reflection mirror pairs against the R1c ruler:", md(lrt, ".3f"), "",
         "## [POST HOC] Phase cross-ratio counts >= 3x the R1c clean ruler",
         "; ".join(f"{bn}: {len(v)} (" + ", ".join(f"{s.replace('phase cross-ratio ', '')} {x:+.2f}" for s, x, _ in v) + ")"
                   for bn, v in cnt.items()), "",
         "## Localisation", f"y_k (deg, 3.2-3.5 GHz) against Healthy_sliced_new: " +
         ", ".join(f"T{k + 1} {v:+.2f}" for k, v in enumerate(yb)) + f"; against Healthy_sliced: " +
         ", ".join(f"T{k + 1} {v:+.2f}" for k, v in enumerate(yb7)),
         f"Fit (w = {w_all}): " + ", ".join(f"{k}: {v}" for k, v in loc.items() if k not in ("sector calls", "sector confidence")),
         "", "Mirror test (26 statistics informative for LeftOnly):", md(mt, ".3f"), ""]
    (OUT / "report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
