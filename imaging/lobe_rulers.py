"""Error rulers for the lobe_A front/back and left/right contrasts (frozen pipeline unchanged):

    python imaging/lobe_rulers.py [--n 200]

Three rulers, each propagated through the frozen inversions (lobe_frozen.json):
  1. one-extra-pass mesh yardstick: Healthy 7-6 and Mild 6-5 passes, both signs (as in section 5c);
  2. numerical symmetry floor: the left-right mirror residual of the mirror-symmetric designs, as in
     Prompt 07 (per-design numerical SD = rms mirror difference / sqrt 2, i.e. sqrt 2 x the
     mirror-antisymmetric part), placed in the 6 rotations x 2 reflections of the ring; a difference
     of two designs adds the two designs' floors in quadrature;
  3. antenna gain / phase errors: Monte Carlo with the Prompt 07 measurement model
     (adstage.pipeline.augment.draws: typical noise profile + setup perturbation, per-port gain
     uniform +-0.5 dB, or +-2 dB with +-10 deg per-port phase), independent draws for both designs.
Contrasts FB = S1 - S4 and LR = mean(S2, S3) - mean(S5, S6) of the recovered d eps'' for
stage - Healthy_sliced_new (lobe_A) and Moderate - Mild; all 21 paths and without opposite paths.
Ruler = max(yardstick, symmetry floor, gain-error SD); ratio >= 3 'exceeds', 2-3 'sensitive',
< 2 'not separable' (the categories of results/05_lobe/mesh/report.md).

Also: a post-hoc 'whitened projection' log model (not frozen, no calls) that removes per-port gains
after noise whitening; the frozen 'gain-invariant' model projects before whitening and leaks gains.
Writes results/imaging/lobe_rulers.json and inserts section 5d into lobe_report.md.
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402

from imaging import lobe_A as LA  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging import study_lobe as SL  # noqa: E402
from imaging.common import OUT, PROFILES, ROOT, git_hash, load_config  # noqa: E402
from imaging.report_lobe import _t  # noqa: E402

COMPARISONS = {"Mild − Healthy": ("Mild_lobe", "Healthy_sliced_new"),
               "Moderate − Healthy": ("Moderate_lobe", "Healthy_sliced_new"),
               "Severe − Healthy": ("Severe_lobe", "Healthy_sliced_new"),
               "Moderate − Mild": ("Moderate_lobe", "Mild_lobe")}
VARIANTS = {"all 21 paths": LA.KEEP_ALL, "without opposite paths": LA.KEEP_NOOPP}
GAIN = {"±0.5 dB gain": dict(gain_err_db=0.5), "±2 dB gain, ±10° phase": dict(gain_err_db=2.0, phase_err_deg=10.0)}
WNAME = "tikhonov log, whitened projection (post-hoc)"
METHODS_ALL = tuple(RL.METHODS) + (WNAME,)


class WhitenedLog(SL.RegionModel):
    """Post-hoc diagnostic, NOT part of the frozen pipeline. Same log-ratio data as the frozen
    'gain-invariant' model, but the per-port gain subspace is projected out AFTER whitening, per
    frequency: P_f = I - (W_f A)(W_f A)^+. The frozen model applies P = I - A A^+ to W_f y, which
    leaves gain leakage P W_f A g != 0 whenever the per-path weights W_f differ."""

    def __init__(self, K, fh, kappa, sig, keep, S_ref):
        self.keep = np.asarray(keep, bool)
        self.fh, self.kind = np.asarray(fh), "log"
        nreg = K.shape[-1]
        Kc = K * kappa[None, :, None]
        Kc = np.concatenate([Kc, -1j * Kc * (SL.F_C / self.fh)[None, :, None]], -1)[self.keep]
        Sr = SL.recip(S_ref)[self.keep]
        Jl = Kc / Sr[..., None]
        self.nreg = nreg
        self.w = 1 / (sig[self.keep] / np.abs(Sr) / np.sqrt(2))
        A = np.zeros((int(self.keep.sum()), SL.N_ANT))
        for i, (a, b) in enumerate(np.array(SL.PAIRS)[self.keep]):
            A[i, a] += 1
            A[i, b] += 1
        self.Pf = []
        for k in range(len(fh)):
            WA = self.w[:, k, None] * A
            self.Pf.append(np.eye(len(A)) - WA @ np.linalg.pinv(WA))
        self.Jc = np.stack([self.Pf[k] @ (Jl[:, k] * self.w[:, k, None]) for k in range(len(fh))], 1)
        self.J = np.concatenate([self.Jc.real.reshape(-1, 2 * nreg), self.Jc.imag.reshape(-1, 2 * nreg)], 0)

    def data(self, dS=None, S_stage=None, S_ref=None):
        y = np.log(SL.recip(S_stage)) - np.log(SL.recip(S_ref))
        y = (y - 2j * np.pi * np.round(np.imag(y) / (2 * np.pi)))[self.keep]
        d = np.stack([self.Pf[k] @ (y[:, k] * self.w[:, k]) for k in range(len(self.fh))], 1)
        return np.r_[d.real.ravel(), d.imag.ravel()]


def build_models(K6, fh, fi, kappa, Sref, keep):
    M = LA.models(K6, fh, fi, kappa, Sref, keep)
    sig = SL.pair_sigma_f(Sref, PROFILES["typical"])[:, fi]
    M["wlog"] = WhitenedLog(K6, fh, kappa, sig, keep, Sref[fi])
    return M


def make_con(M, m, lam):
    """Contrast function of (stage, ref) at the fit frequencies for method m in METHODS_ALL."""
    if m == WNAME:
        Mx, meth, lm = {"log": M["wlog"]}, "tikhonov log (gain-inv.)", lam["log"]
    else:
        Mx, meth, lm = M, m, (lam["dS"] if m.endswith("dS") else lam["log"])

    def con(Sst_fi, Sref_fi):
        x = RL.invert(Mx, meth, lm, S_stage_fi=Sst_fi, S_ref_fi=Sref_fi, dS_fi=SL.recip(Sst_fi - Sref_fi))
        return RL.contrasts(x)
    return con


SHORTM = {RL.METHODS[0]: "Tikhonov dS", RL.METHODS[1]: "bounded dS", RL.METHODS[2]: "frozen log",
          RL.METHODS[3]: "frozen bounded log", WNAME: "whitened log"}


def category(r):
    return "exceeds (≥ 3×)" if r >= 3 else ("sensitive (2–3×)" if r >= 2 else "not separable (< 2×)")


def compute(n_draws=200):
    from adstage.noise.model import NoiseProfile
    from adstage.pipeline.augment import draws
    fz = json.loads((OUT / "lobe_frozen.json").read_text(encoding="utf-8"))
    kappa = np.array(fz["kappa_re"]) + 1j * np.array(fz["kappa_im"])
    lam = {"dS": fz["lambda_dS"], "log": fz["lambda_log"]}
    S, f, fh, fi, P = RL.build(reuse=True)
    for nm in ("Healthy_sliced_new", "Mild_lobe_new"):
        S[nm], _ = SL.load_design(nm, f)
    H6 = S["Healthy_sliced_new"]
    K6 = SL.region_kernels(P, SL.region_masks())[..., :6]
    prof = PROFILES["typical"]
    acfg0 = dict(load_config().get("augment", {}))
    idx = np.arange(SL.N_ANT)
    maps = [np.roll(idx, r) for r in range(SL.N_ANT)] + [np.roll(idx[::-1], r) for r in range(SL.N_ANT)]
    mp = SL.mirror_perm()
    yard = {"Healthy 7 − 6": S["Healthy_sliced"] - H6, "Mild 6 − 5": S["Mild_lobe_new"] - S["Mild_lobe"]}
    designs = ("Healthy_sliced_new", "Mild_lobe", "Moderate_lobe", "Severe_lobe")
    E = {d: np.sqrt(2) * 0.5 * (S[d] - SL.permute(S[d], mp)) for d in designs}   # per-design numerical error pattern

    D = {}                                          # Monte Carlo draws, shared by all methods / variants
    for gi, (gname, gc) in enumerate(GAIN.items()):
        ac = {**acfg0, **gc}
        D[gname] = {d: draws(f, S[d], prof, n_draws, np.random.default_rng([2026, 1004, gi, j]), ac)[:, fi]
                    for j, d in enumerate(designs)}
    out = dict(code=git_hash(ROOT), frozen_code=fz["code"], n_draws=n_draws, gain_model=acfg0, rows=[], dist={})
    for vname, keep in VARIANTS.items():
        Mref = {r: build_models(K6, fh, fi, kappa, S[r], keep) for r in ("Healthy_sliced_new", "Mild_lobe")}
        for m in METHODS_ALL:
            cons = {r: make_con(Mref[r], m, lam) for r in Mref}
            c6 = cons["Healthy_sliced_new"]
            # yardstick and symmetry floor are inputs added to the reference H6, as in section 5c
            yv = [c6((H6 + sg * y)[fi], H6[fi]) for y in yard.values() for sg in (1, -1)]
            y_fb, y_lr = max(abs(c["FB"]) for c in yv), max(abs(c["LR"]) for c in yv)
            fl = {}
            for d in designs:
                cs = [c6((H6 + sg * SL.permute(E[d], mm))[fi], H6[fi]) for mm in maps for sg in (1, -1)]
                fl[d] = (float(np.sqrt(np.mean([c["FB"] ** 2 for c in cs]))),
                         float(np.sqrt(np.mean([c["LR"] ** 2 for c in cs]))))
            for cname, (st, rf) in COMPARISONS.items():
                cf = cons[rf]
                clean = cf(S[st][fi], S[rf][fi])
                f_fb = float(np.hypot(fl[st][0], fl[rf][0]))
                f_lr = float(np.hypot(fl[st][1], fl[rf][1]))
                gstat = {}
                for gname in GAIN:
                    cs = [cf(a, b) for a, b in zip(D[gname][st], D[gname][rf])]
                    fb = np.array([c["FB"] for c in cs])
                    lr = np.array([c["LR"] for c in cs])
                    gstat[gname] = dict(FB_mean=float(fb.mean()), FB_sd=float(fb.std(ddof=1)),
                                        FB_lo=float(np.quantile(fb, 0.025)), FB_hi=float(np.quantile(fb, 0.975)),
                                        LR_mean=float(lr.mean()), LR_sd=float(lr.std(ddof=1)),
                                        LR_lo=float(np.quantile(lr, 0.025)), LR_hi=float(np.quantile(lr, 0.975)))
                    out["dist"][f"{vname}|{m}|{cname}|{gname}"] = dict(FB=fb.tolist(), LR=lr.tolist())
                out["rows"].append(dict(variant=vname, method=m, comparison=cname, FB=clean["FB"], LR=clean["LR"],
                                        yard_FB=y_fb, yard_LR=y_lr, floor_FB=f_fb, floor_LR=f_lr, gain=gstat))

    # which part of the measurement model drives the spread (Moderate - Healthy, all paths)
    zero = NoiseProfile("zero", 0.0, 0.0, -300, 0)
    comp = {"typical noise profile only": (prof, dict(amp_sd=0, phase_sd_deg=0, jitter_mhz=0)),
            "frequency jitter 1 MHz only": (zero, dict(amp_sd=0, phase_sd_deg=0, jitter_mhz=1.0)),
            "per-port amplitude 1.5 % + phase 10° (07 setup) only":
                (zero, dict(amp_sd=0.015, phase_sd_deg=10.0, jitter_mhz=0)),
            "per-port gain ±0.5 dB only": (zero, dict(amp_sd=0, phase_sd_deg=0, jitter_mhz=0, gain_err_db=0.5)),
            "per-port gain ±2 dB, phase ±10° only":
                (zero, dict(amp_sd=0, phase_sd_deg=0, jitter_mhz=0, gain_err_db=2.0, phase_err_deg=10.0))}
    Mc = build_models(K6, fh, fi, kappa, H6, LA.KEEP_ALL)
    out["components"] = []
    nc = max(n_draws // 2, 10)
    for ci, (cn, (pr, ac)) in enumerate(comp.items()):
        A_ = draws(f, S["Moderate_lobe"], pr, nc, np.random.default_rng([2026, 1005, ci, 0]), ac)[:, fi]
        B_ = draws(f, H6, pr, nc, np.random.default_rng([2026, 1005, ci, 1]), ac)[:, fi]
        row = dict(component=cn)
        for m in (RL.METHODS[0], RL.METHODS[2], WNAME):
            cfun = make_con(Mc, m, lam)
            cs = [cfun(a, b) for a, b in zip(A_, B_)]
            row[f"FB sd, {m}"] = float(np.std([c["FB"] for c in cs], ddof=1))
            row[f"LR sd, {m}"] = float(np.std([c["LR"] for c in cs], ddof=1))
        out["components"].append(row)
    out["n_comp"] = nc
    # model (kernel) asymmetry: LR of exactly mirror-symmetrised data
    sym = {d: 0.5 * (S[d] + SL.permute(S[d], mp)) for d in designs}
    Ms = build_models(K6, fh, fi, kappa, sym["Healthy_sliced_new"], LA.KEEP_ALL)
    out["sym_LR"] = {m: {d: make_con(Ms, m, lam)(sym[d][fi], sym["Healthy_sliced_new"][fi])["LR"]
                         for d in designs[1:]} for m in METHODS_ALL}

    # truth of the contrasts (sensitivity-weighted true d eps'')
    masks = SL.region_masks()
    tr = {d: SL.truth_regions(d, fh, P, masks)["sens"][7:13] for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe")}
    tr["Healthy_sliced_new"] = np.zeros(6)
    out["truth"] = {}
    for cname, (st, rf) in COMPARISONS.items():
        x = np.r_[np.zeros(6), tr[st] - tr[rf]]
        out["truth"][cname] = dict(RL.contrasts(x), sectors=(tr[st] - tr[rf]).tolist())
    return out


def ruler_rows(res, gname):
    rows = []
    for r in res["rows"]:
        g = r["gain"][gname]
        for q in ("FB", "LR"):
            parts = [r[f"yard_{q}"], r[f"floor_{q}"], g[f"{q}_sd"]]
            rl = max(parts)
            rows.append(dict(variant=r["variant"], method=r["method"], comparison=r["comparison"], contrast=q,
                             clean=r[q], truth=res["truth"][r["comparison"]][q], yardstick=parts[0],
                             floor=parts[1], gain_sd=parts[2],
                             gain_95=f"[{g[f'{q}_lo']:+.1f}, {g[f'{q}_hi']:+.1f}]", ruler=rl,
                             dominant=["mesh", "symmetry", "measurement"][int(np.argmax(parts))],
                             ratio=abs(r[q]) / rl, verdict=category(abs(r[q]) / rl),
                             clean_ratio=abs(r[q]) / max(parts[0], parts[1])))
    return rows


def section(res):
    tr = res["truth"]
    mm = np.array(tr["Moderate − Mild"]["sectors"])
    L = ["## 5d. Front/back and left/right against all three error rulers (lobe_A, 4 Oct)", "",
         "The main session (`results/05_lobe/mesh/report.md`, commits aff9d56–bf5af59) found localisation not "
         "separable from error once the numerical symmetry floor and antenna gain/phase errors are included. The "
         "same rulers are applied here to the contrasts of the recovered conductivity map, each propagated "
         "through the frozen inversions (κ, λ unchanged):", "",
         "1. **Mesh yardstick**: one extra adaptive pass (Healthy 7 − 6, Mild 6 − 5), both signs, largest |contrast|.",
         "2. **Numerical symmetry floor**: as in Prompt 07, per-design numerical SD = √2 × the mirror-antisymmetric "
         "part of the design's S-matrix. That pattern is placed in the 6 rotations × 2 reflections of the ring "
         "(both signs) and passed through the pipeline; the rms contrast is the design's floor; a difference of two "
         "designs adds both floors in quadrature. All four lobe_A designs are mirror-symmetric, Healthy_sliced_new "
         "included.",
         f"3. **Gain/phase errors**: {res['n_draws']} Monte Carlo draws per design with the Prompt 07 measurement "
         "model (`adstage.pipeline.augment.draws`: typical noise profile, setup perturbation "
         f"amp_sd {res['gain_model'].get('amp_sd')}, phase_sd {res['gain_model'].get('phase_sd_deg')}° per port, "
         f"jitter {res['gain_model'].get('jitter_mhz')} MHz, plus per-port gain uniform ±0.5 dB, or ±2 dB with ±10° "
         "phase), independent draws for the two designs of each comparison. Spread = SD of the contrast over "
         "the draws; the 95 % interval is also given. Note that this model contains more than gain errors.", "",
         "Ruler = max(yardstick, symmetry floor, measurement-error SD of the Prompt 07 model; column gain_sd, dominant = measurement). |clean contrast| / ruler ≥ 3: exceeds; 2–3: "
         "sensitive; < 2: not separable (the main session's categories). 'clean_ratio' = |clean contrast| / "
         "max(yardstick, symmetry floor): the simulation-level ruler without measurement errors (the main "
         "session's 'clean ruler'). Truth = sensitivity-weighted true dε'' contrast. **Moderate − Mild is not a pure "
         f"frontal contrast**: besides adding the frontal lobe (S1 {mm[0]:+.1f}) it changes every affected lobe "
         f"(S2, S3, S5, S6: {', '.join(f'{v:+.1f}' for v in mm[[1, 2, 4, 5]])}) and the CSF material everywhere "
         f"(S4 {mm[3]:+.1f}).", "",
         "**Erratum: the frozen 'gain-invariant' log method is not gain-invariant.** `study_lobe.RegionModel` "
         "(kind 'log') removes the per-port gain subspace with P = I − A A⁺ but applies it to the noise-whitened "
         "log-ratios W_f y. A per-port gain g adds W_f A g, and P W_f A g ≠ 0 because the per-path weights W_f "
         "differ (weak paths are weighted up), so gains leak into the fit (component table below). The frozen "
         "pipeline and the pre-registered predictions keep this method unchanged; its name is a misnomer, and the "
         "'log, gain-invariant' CRLB columns in §2 are CRLBs for that projected data, not for gain-free data. For "
         f"comparison only, **'{WNAME}'** projects after whitening, per frequency (P_f = I − W_f A (W_f A)⁺), with "
         "the frozen κ and λ_log; it has no frozen thresholds and makes no calls.", "",
         "Which part of the Prompt 07 measurement model drives the spread (Moderate − Healthy, all paths; SD of the "
         f"contrast over {res['n_comp']} draws per component, every other component switched off):", "",
         _t(res["components"], list(res["components"][0]),
            {k: ".2f" for k in res["components"][0] if k != "component"}), ""]
    cols = ["variant", "method", "comparison", "contrast", "clean", "truth", "yardstick", "floor", "gain_sd",
            "gain_95", "ruler", "dominant", "ratio", "verdict", "clean_ratio"]
    fmt = {c: ".2f" for c in ("yardstick", "floor", "gain_sd", "ruler", "ratio", "clean_ratio")}
    fmt.update(clean="+.1f", truth="+.1f")
    tabs = {}
    for gname in GAIN:
        rows = ruler_rows(res, gname)
        tabs[gname] = rows
        L += [f"### Gain/phase condition: {gname}", "",
              "Front/back (FB = S1 − S4):", "",
              _t([r for r in rows if r["contrast"] == "FB"], cols, fmt), "",
              "Left/right (LR = mean(S2, S3) − mean(S5, S6); all designs are mirror-symmetric, true LR = 0):", "",
              _t([r for r in rows if r["contrast"] == "LR"], cols, fmt), ""]
    res["tables"] = tabs
    return L


def interpret(res):
    t = res["tables"]
    P0, P2 = RL.METHODS[0], RL.METHODS[2]
    g05, g2 = list(GAIN)
    va, vn = "all 21 paths", "without opposite paths"

    def get(g, v, m, c, q):
        return next(r for r in t[g] if r["variant"] == v and r["method"] == m and r["comparison"] == c
                    and r["contrast"] == q)
    L = ["### Reading", ""]
    for m in (P0, P2, WNAME):
        for c in ("Moderate − Healthy", "Moderate − Mild"):
            a, b = get(g05, va, m, c, "FB"), get(g2, va, m, c, "FB")
            an, bn = get(g05, vn, m, c, "FB"), get(g2, vn, m, c, "FB")
            L.append(f"- **{c}, FB, {SHORTM[m]}:** clean {a['clean']:+.1f} (truth {a['truth']:+.1f}). ±0.5 dB: ruler "
                     f"{a['ruler']:.1f} ({a['dominant']}), {a['ratio']:.1f}× → {a['verdict']}; ±2 dB/±10°: ruler "
                     f"{b['ruler']:.1f} ({b['dominant']}), {b['ratio']:.1f}× → {b['verdict']}. Without opposite "
                     f"paths: {an['ratio']:.1f}× / {bn['ratio']:.1f}×. Clean ruler (mesh, symmetry only): "
                     f"{a['clean_ratio']:.1f}× ({category(a['clean_ratio'])}); without opposite paths "
                     f"{an['clean_ratio']:.1f}×.")
    bias = [(g, get(g, va, m, c, "FB")) for g in GAIN for m in (P0, P2, WNAME)
            for c in ("Mild − Healthy", "Severe − Healthy")]
    def lab(r):
        return f"{SHORTM[r['method']]} {r['comparison'].split(' ')[0]}"
    b05 = [r for g, r in bias if g == g05]
    L.append("- **The front-positive bias** (Mild, Severe: true FB ≈ 0). Clean FB: "
             + ", ".join(f"{lab(r)} {r['clean']:+.1f}" for r in b05)
             + ". Ratio to the full ruler (±0.5 dB / ±2 dB): "
             + "; ".join(f"{lab(r)} {r['ratio']:.1f}× / {get(g2, va, r['method'], r['comparison'], 'FB')['ratio']:.1f}×"
                         for r in b05)
             + ". Ratio to the clean ruler (mesh, symmetry): "
             + "; ".join(f"{lab(r)} {r['clean_ratio']:.1f}×" for r in b05)
             + ". Against the clean ruler the bias is about as large, relative to error, as Moderate's FB itself; "
             "Moderate − Healthy FB contains it, and Moderate − Mild (which removes most of it) is the smaller "
             "contrast.")
    lr = [get(g, v, m, c, "LR") for g in GAIN for v in VARIANTS for m in METHODS_ALL for c in COMPARISONS]
    lrc = [get(g05, v, m, c, "LR") for v in VARIANTS for m in METHODS_ALL for c in COMPARISONS]
    w = max(lrc, key=lambda r: r["clean_ratio"])
    L.append(f"- **Left/right on the mirror-symmetric designs** (true LR = 0): |LR| / full ruler ≤ "
             f"{max(r['ratio'] for r in lr):.1f}×; |LR| / clean ruler ≤ {w['clean_ratio']:.1f}× (worst: "
             f"{SHORTM[w['method']]}, {w['comparison']}, {w['variant']}, LR {w['clean']:+.1f}). Exactly "
             "mirror-symmetrised data give |LR| ≤ "
             f"{max(abs(v) for d in res['sym_LR'].values() for v in d.values()):.1f} (kernel mirror asymmetry of the "
             "HFSS field exports); the rest of the symmetric designs' LR is their own numerical mirror residual, "
             "i.e. the symmetry floor in its actual orientation.")
    bp = pickle.loads((RL.CACHE / "stage1.pkl").read_bytes())["blind_pred"]["LeftOnly_test"]
    for m in (P0, P2):
        r05, r2 = get(g05, va, m, "Mild − Healthy", "LR"), get(g2, va, m, "Mild − Healthy", "LR")
        L.append(f"- **LeftOnly prediction vs the LR rulers ({SHORTM[m]}):** predicted LR {bp[m]['LR_mean']:+.1f} "
                 f"(Born-simulated) against the Mild − Healthy LR ruler {r05['ruler']:.1f} (±0.5 dB) / "
                 f"{r2['ruler']:.1f} (±2 dB/±10°) → {bp[m]['LR_mean'] / r05['ruler']:.1f}× / "
                 f"{bp[m]['LR_mean'] / r2['ruler']:.1f}×; clean ruler "
                 f"{max(r05['yardstick'], r05['floor']):.1f} → {bp[m]['LR_mean'] / max(r05['yardstick'], r05['floor']):.1f}×.")
    L.append("")
    res["summary"] = dict(
        mod_FB={m: {g: get(g, va, m, "Moderate − Healthy", "FB") for g in GAIN} for m in METHODS_ALL},
        mm_FB={m: {g: get(g, va, m, "Moderate − Mild", "FB") for g in GAIN} for m in METHODS_ALL},
        mod_FB_noopp={m: {g: get(g, vn, m, "Moderate − Healthy", "FB") for g in GAIN} for m in METHODS_ALL},
        bias={m: {c: get(g05, va, m, c, "FB") for c in ("Mild − Healthy", "Severe − Healthy")} for m in METHODS_ALL},
        lr_max_ratio=max(r["ratio"] for r in lr), lr_max_clean=max(r["clean_ratio"] for r in lrc),
        leftonly={m: dict(LR=bp[m]["LR_mean"], ruler05=get(g05, va, m, "Mild − Healthy", "LR")["ruler"],
                          ruler2=get(g2, va, m, "Mild − Healthy", "LR")["ruler"],
                          clean=max(get(g05, va, m, "Mild − Healthy", "LR")["yardstick"],
                                    get(g05, va, m, "Mild − Healthy", "LR")["floor"])) for m in (P0, P2)})
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    a = ap.parse_args()
    res = compute(a.n)
    L = section(res) + interpret(res)
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    if "## 5d." in rep:
        rep = rep[:rep.index("## 5d.")] + rep[rep.index("## 6."):]
    i = rep.index("## 6.")
    rep = rep[:i] + "\n".join(L) + "\n" + rep[i:]
    js = {k: v for k, v in res.items() if k not in ("dist", "tables")}
    (OUT / "lobe_rulers.json").write_text(json.dumps(js, indent=1, default=float), encoding="utf-8")
    (RL.CACHE / "lobe_rulers.pkl").write_bytes(pickle.dumps(res))
    if "## 6. Blind test outcome" not in rep:
        from imaging.report_lobe import _verdict
        res1 = pickle.loads((RL.CACHE / "stage1.pkl").read_bytes())
        rep = rep[:rep.index("## 7. Verdict")] + "\n".join(_verdict(res1)) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
    print("\n".join(L[L.index("### Reading"):]).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
