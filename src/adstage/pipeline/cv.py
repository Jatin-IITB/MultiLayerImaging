"""Leakage-aware cross-validation folds over (simulation, antenna view) blocks.

Rules
-----
* Noisy copies of one simulation are drawn separately for training and testing (different
  seeds), so a test draw never appears in training.
* Every class with >= 2 simulations: whole simulations are held out (LOSO); a held-out
  simulation contributes nothing to training.
* A class with exactly 1 simulation: leave-one-DIAMETER-out. The held-out views are an
  opposite antenna pair {t, t+N/2}, not a single antenna. By reciprocity the view of t
  contains the path S(t+N/2, t), and that is the same path as the t+N/2 view's
  S(t, t+N/2), so the whole pair has to leave together. Neighbour paths (k = 1, 2) are
  still shared with training views; with one simulation per class the result is
  noise-robustness only.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Fold:
    train: list[tuple[int, list[int]]]      # (sim index, antenna views)
    test: list[tuple[int, list[int]]]


def diameters(n_ant: int) -> list[list[int]]:
    if n_ant % 2:
        return [[t] for t in range(n_ant)]
    return [[t, t + n_ant // 2] for t in range(n_ant // 2)]


def make_folds(groups: dict[str, list[int]], n_ant: int) -> tuple[str, list[Fold]]:
    """groups: class -> simulation indices. Returns (cv_scheme name, folds)."""
    views = list(range(n_ant))
    sizes = [len(v) for v in groups.values()]
    if min(sizes) >= 2:
        folds = []
        for sims in groups.values():
            for s_out in sims:
                train = [(s, views) for g in groups.values() for s in g if s != s_out]
                folds.append(Fold(train, [(s_out, views)]))
        return "LOSO", folds
    n_rot = max(sizes)
    folds = []
    for j in range(n_rot):
        for d in diameters(n_ant):
            train, test = [], []
            for sims in groups.values():
                if len(sims) == 1:
                    s = sims[0]
                    test.append((s, d))
                    train.append((s, [t for t in views if t not in d]))
                else:
                    s_out = sims[j % len(sims)]
                    test.append((s_out, d))
                    train += [(s, views) for s in sims if s != s_out]
            folds.append(Fold(train, test))
    return ("LODO" if n_rot == 1 else "LODO+LOSO-within-class"), folds


def validity_label(groups: dict[str, list[int]], head_ids: list[str]) -> str:
    """generalisation-across-heads: every class has >= 2 distinct heads.
    cross-solve-same-head: every class has >= 2 solves (e.g. repeats), but of one head.
    noise-robustness-only: some class has a single simulation."""
    if all(len({head_ids[s] for s in sims}) >= 2 for sims in groups.values()):
        return "generalisation-across-heads"
    if all(len(sims) >= 2 for sims in groups.values()):
        return "cross-solve-same-head"
    return "noise-robustness-only"
