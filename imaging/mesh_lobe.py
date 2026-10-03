"""Mesh yardstick for the lobe study (added after the freeze at fb5b775; does not change the frozen
pipeline, kappa, lambdas, thresholds or predictions):

    python imaging/mesh_lobe.py

Two healthy heads solved with different meshes - the v2 Normal design (`new_Healthy.s6p`) and
Healthy_sliced - differ only by mesh (and the explicit 83.5 mm skull surface of the sliced head).
Their difference, and its 12 ring-symmetry images, are passed through the frozen inversions and
rules exactly as a stage would be. The result is inserted into lobe_report.md as section 5b.
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np  # noqa: E402

from imaging import study_lobe as SL  # noqa: E402
from imaging import run_lobe as RL  # noqa: E402
from imaging.common import OUT, PROFILES, ROOT, load_config, git_hash  # noqa: E402
from imaging.report_lobe import SHORT, _t  # noqa: E402

MESH_TABLE = "results/STATUS.md §7 (HFSS solution dialogs): Healthy_sliced 1,349,491 elements, " \
             "Mild 739,774, Moderate 796,281, Severe 690,077"


def load_v2_normal(f_ref):
    from adstage.io.masking import mask_glitches
    from adstage.io.touchstone import read_touchstone
    cfg = load_config()
    t = read_touchstone(ROOT / "data" / "raw" / "new_Healthy.s6p")
    k = np.array([int(np.argmin(np.abs(t.f_hz - q))) for q in f_ref])     # v2 band 2.8-4.2 GHz, same 5 MHz step
    if np.max(np.abs(t.f_hz[k] - f_ref)) > 1:
        raise ValueError("new_Healthy: frequency grid does not contain the sliced grid")
    s = mask_glitches(t.f_hz[k], t.s[k], float(cfg["qc"].get("glitch_thr_db", -30.0)))[0]
    return SL.ant_matrix(s, cfg["ring"]["port_to_ant"])


def main():
    fz = json.loads((OUT / "lobe_frozen.json").read_text(encoding="utf-8"))
    S, f, fh, fi, P = RL.build(reuse=True)
    kappa = np.array(fz["kappa_re"]) + 1j * np.array(fz["kappa_im"])
    M = RL.models(S, fh, fi, P, kappa, PROFILES["typical"])
    H = S["Healthy_sliced"]
    N2 = load_v2_normal(f)
    dmesh = N2 - H
    n = SL.N_ANT
    idx = np.arange(n)
    maps = [np.roll(idx, r) for r in range(n)] + [np.roll(idx[::-1], r) for r in range(n)]
    lam = {"dS": fz["lambda_dS"], "log": fz["lambda_log"]}
    rows, summ = [], []
    sizes = {d: float(np.linalg.norm(SL.recip(S[d] - H)[:, fi])) for d in ("Mild_lobe", "Moderate_lobe", "Severe_lobe")}
    size_mesh = float(np.linalg.norm(SL.recip(dmesh)[:, fi]))
    for m in RL.METHODS:
        lm = lam["dS"] if m.endswith("dS") else lam["log"]
        xs, cs = [], []
        for j, mp in enumerate(maps):
            dn = SL.permute(dmesh, mp)
            x = RL.invert(M, m, lm, S_stage_fi=(H + dn)[fi], S_ref_fi=H[fi], dS_fi=SL.recip(dn[fi]))
            c = RL.apply_rules(x, fz["rules"][m])
            xs.append(x)
            cs.append(c)
            if j == 0:
                rows.append(dict(method=m, **{f"dε'' {s}": x[6 + k] for k, s in enumerate(SHORT)},
                                 called=" ".join(f"S{k + 1}" for k in range(6) if c["affected"][k]) or "none",
                                 LR=c["LR"], side=c["side"], FB=c["FB"], frontback=c["frontback"]))
        xs = np.array(xs)
        r = fz["rules"][m]
        summ.append(dict(method=m, max_sector=float(xs[:, 6:12].max()), T_abs=r["T_abs"],
                         max_abs_LR=float(max(abs(c["LR"]) for c in cs)), T_LR=r["T_LR"],
                         max_abs_FB=float(max(abs(c["FB"]) for c in cs)), T_FB=r["T_FB"],
                         n_side_calls=sum(c["side"] != "none" for c in cs),
                         n_fb_calls=sum(c["frontback"] != "none" for c in cs),
                         n_sector_calls=int(sum(sum(c["affected"]) for c in cs))))
    res1 = __import__("pickle").loads((RL.CACHE / "stage1.pkl").read_bytes())
    fbm = {r_["method"]: r_["FB"] for r_ in res1["front_back"]}
    prim = summ[0]
    L = ["## 5b. Mesh yardstick (added after the freeze; frozen pipeline unchanged)", "",
         f"The designs were **not** solved on matched meshes ({MESH_TABLE}): the healthy reference has ~1.8× "
         "the elements of every stage, so each dS = S(stage) − S(Healthy_sliced) also contains a mesh "
         "difference. To size it, the difference between two healthy heads solved with different meshes "
         "(v2 Normal `new_Healthy.s6p` − Healthy_sliced) and its 12 ring-symmetry images were passed through "
         "the frozen inversions and rules as if they were a stage.", "",
         f"Size of the mesh difference at the fit frequencies: {size_mesh:.3g} (Frobenius norm over 21 pairs × 3 "
         "frequencies) vs " + ", ".join(f"{d.split('_')[0]} {v:.3g}" for d, v in sizes.items())
         + f" for the stage differences ({size_mesh / sizes['Mild_lobe']:.0%} of Mild).", "",
         "Recovered values for the unrotated mesh difference:", "",
         _t(rows, ["method"] + [f"dε'' {s}" for s in SHORT] + ["called", "LR", "side", "FB", "frontback"],
            {**{f"dε'' {s}": ".1f" for s in SHORT}, "LR": "+.1f", "FB": "+.1f"}), "",
         "Over all 12 symmetry images (largest values, and how many of the 12 trigger a call):", "",
         _t(summ, ["method", "max_sector", "T_abs", "n_sector_calls", "max_abs_LR", "T_LR", "n_side_calls",
                   "max_abs_FB", "T_FB", "n_fb_calls"],
            {c: ".1f" for c in ["max_sector", "T_abs", "max_abs_LR", "T_LR", "max_abs_FB", "T_FB"]}), "",
         f"- **Absolute level.** The mesh difference alone lifts every sector to dε'' ≈ "
         f"{min(min(r_[f'dε{chr(39) * 2} {x}'] for x in SHORT) for r_ in rows):.0f}–"
         f"{max(max(r_[f'dε{chr(39) * 2} {x}'] for x in SHORT) for r_ in rows):.0f}, above the frozen T_abs, and its "
         f"norm is {size_mesh / sizes['Mild_lobe']:.1f}× Mild's dS. The upward offset of the healthy sectors in §3 "
         "(6–11 instead of 0.3) is therefore consistent with a mesh contribution as well as Born error, and "
         "absolute 'affected' calls are not mesh-robust.",
         f"- **Contrasts.** Unrotated, the mesh difference gives LR {rows[0]['LR']:+.1f} / FB {rows[0]['FB']:+.1f} "
         f"(primary) and LR {rows[2]['LR']:+.1f} / FB {rows[2]['FB']:+.1f} (gain-invariant). Under the 12 ring "
         f"symmetries |LR| reaches {prim['max_abs_LR']:.1f} and |FB| {prim['max_abs_FB']:.1f}; a mesh difference "
         f"alone triggers a side call in {prim['n_side_calls']} and a front/back call in {prim['n_fb_calls']} of "
         "12 images (primary).",
         f"- Moderate's front/back contrast (primary {fbm[RL.METHODS[0]]:+.1f}) is "
         f"{abs(fbm[RL.METHODS[0]]) / max(prim['max_abs_FB'], 1e-9):.1f}× the largest |FB| a mesh difference "
         f"between two fine healthy meshes produces ({prim['max_abs_FB']:.1f}); the left/right threshold "
         f"T_LR = {prim['T_LR']:.1f} compares with a largest mesh |LR| of {prim['max_abs_LR']:.1f}. The "
         f"pre-registered LeftOnly contrast (+{res1['blind_pred']['LeftOnly_test'][RL.METHODS[0]]['LR_mean']:.1f}) "
         f"would be {res1['blind_pred']['LeftOnly_test'][RL.METHODS[0]]['LR_mean'] / prim['max_abs_LR']:.1f}× the "
         "largest mesh |LR|; a left call near the threshold would not be distinguishable from mesh.",
         "- Caveat: this yardstick compares two fine meshes; the disease stages are on coarser meshes "
         "(~0.7–0.8 M elements), whose error is probably larger. It also includes any other difference between "
         "the two projects (e.g. the internal wedge faces of the sliced head). Mesh-matched re-solves are needed "
         "before the front/back and left/right results can be called mesh-independent.", ""]
    rep = (OUT / "lobe_report.md").read_text(encoding="utf-8")
    rep = rep.replace("(same project, setup and mesh recipe)",
                      "(same project and setup; meshes NOT matched, see §5b)")
    if "## 5b." in rep:
        i0, i1 = rep.index("## 5b."), rep.index("## 6.")
        rep = rep[:i0] + rep[i1:]
    i = rep.index("## 6.")
    rep = rep[:i] + "\n".join(L) + "\n" + rep[i:]
    (OUT / "lobe_mesh_yardstick.json").write_text(json.dumps(dict(code=git_hash(ROOT), rows=rows, summary=summ,
                                                                  size_mesh=size_mesh, sizes=sizes),
                                                             indent=1, default=float), encoding="utf-8")
    if "## 6. Blind test outcome" not in rep:                      # before the blind stage: refresh the verdict
        from imaging.report_lobe import _verdict
        rep = rep[:rep.index("## 7. Verdict")] + "\n".join(_verdict(res1)) + "\n"
    (OUT / "lobe_report.md").write_text(rep, encoding="utf-8")
    for s in summ:
        print(s)
    for r_ in rows:
        print({k: v for k, v in r_.items() if k.isascii()})


if __name__ == "__main__":
    main()
