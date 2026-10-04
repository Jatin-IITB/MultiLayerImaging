"""Figures and scores from results/imaging2/posteriors.json.

    python -m imaging2.make_figures [--quick]
"""
from __future__ import annotations

import argparse
import json

import pandas as pd

from . import figures as FG
from . import render as RE
from . import scores as SC
from .data import FIG, OUT

PRIMARY = ["Healthy_p7", "Mild_p5", "Moderate_p5", "Severe_p5", "LeftOnly_p6", "MCI_p6"]       # stop rule 1 (lobe_A)
SECOND = ["Mild_p6", "Moderate_p6", "Severe_p6"]                                                 # stop rule 2 meshes
CONTROLS = ["Prior_only", "Healthy_p7", "MCI_p6", "LeftOnly_mirrored", "Mild_p6_shuffled", "LeftOnly_vsH7"]


def main(quick=False):
    FIG.mkdir(parents=True, exist_ok=True)
    post = FG.load_post()
    nr = RE.noise_rel_at_field_freqs()
    tags = list(post["targets"])
    made = []
    made.append(FG.fig_overview(PRIMARY, post, nr, "sig", 50.0))
    made.append(FG.fig_overview(PRIMARY, post, nr, "eps", 50.0))
    made.append(FG.fig_overview(["Mild_p5", "Mild_p6", "Moderate_p5", "Moderate_p6", "Severe_p5", "Severe_p6"], post, nr,
                                "sig", 50.0, fn=FIG / "mesh_pairs_sig_z50.png",
                                suptitle="Same design, two meshes (numerical-noise ruler): conductivity change at z = 50 mm"))
    made.append(FG.fig_overview([t for t in CONTROLS if t in tags], post, nr, "sig", 50.0, fn=FIG / "controls_sig_z50.png",
                                suptitle="Controls: no change (other healthy mesh, MCI), mirrored / rotated / shuffled data, "
                                         "other reference: conductivity change at z = 50 mm"))
    loso = [t for t in ("LOSO_Mild_p5", "LOSO_LeftOnly_p6") if t in tags]
    if loso:
        made.append(FG.fig_overview(["Mild_p5", "LOSO_Mild_p5", "LeftOnly_p6", "LOSO_LeftOnly_p6"], post, nr, "sig", 50.0,
                                    fn=FIG / "loso_sig_z50.png",
                                    suptitle="Stricter test: the same designs imaged with NO Mild-material design in "
                                             "training (leave-one-stage-out), z = 50 mm"))
    if (OUT / "noise_study.json").exists():
        nj = json.loads((OUT / "noise_study.json").read_text())
        made.append(FG.fig_noise(["Healthy_p7", "Mild_p5", "Moderate_p5", "Severe_p5", "LeftOnly_p6", "MCI_p6"], nj, nr))
    made.append(FG.fig_detuning(PRIMARY, post))
    made.append(FG.fig_stack(["Mild_p5", "Moderate_p5", "Severe_p5", "LeftOnly_p6"], post, nr, "sig"))
    made.append(FG.fig_stack(["Mild_p5", "Moderate_p5", "Severe_p5", "LeftOnly_p6"], post, nr, "eps"))
    for tag in (PRIMARY if quick else [t for t in tags if not t.startswith("LOSO")]):
        made.append(FG.fig_slices(tag, post, nr, "sig"))
        if not quick or tag in ("LeftOnly_p6", "Moderate_p5"):
            made.append(FG.fig_slices(tag, post, nr, "eps"))
    for tag in ["LeftOnly_p6", "Moderate_p5", "Severe_p5", "Mild_p5"]:
        made.append(FG.fig_views(tag, post, nr, "sig"))
    rows, srows = [], []
    for tag in tags:
        r, s = SC.design_row(tag, post)
        rows.append(r)
        srows += s
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "scores_designs.csv", index=False)
    pd.DataFrame(srows).to_csv(OUT / "scores_sectors.csv", index=False)
    (OUT / "figure_index.json").write_text(json.dumps([str(p.relative_to(OUT)) for p in made], indent=1))
    with pd.option_context("display.width", 250, "display.max_columns", 40):
        print(df[["target", "stage_true", "stage_est", "P_stage_est", "sector_calls_correct", "mae_e_mm",
                  "mae_e_affected_mm", "e_pattern_corr", "covered_90", "gof_chi2_per_dof", "left_minus_right_e",
                  "left_minus_right_true", "sig_sensed_corr", "sig_sensed_relerr", "sig_brain_corr"]].round(2))
    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    main(ap.parse_args().quick)
