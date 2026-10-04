"""Unit tests for the lobe-sector study: sector geometry, mirror map, region masks, calling rules.

Run:  python -m pytest imaging/tests -q
"""
import numpy as np

from imaging import study_lobe as SL
from imaging.run_lobe import apply_rules, contrasts


def test_sector_of_centres_and_edges():
    # sector k is centred on antenna T(k+1): T1 -90, T2 -30, T3 30, T4 90, T5 150, T6 -150
    assert SL.sector_of([-90, -30, 30, 90, 150, -150]).tolist() == [0, 1, 2, 3, 4, 5]
    assert SL.sector_of([-120, -60, 0, 60, 120, 180]).tolist() == [0, 1, 2, 3, 4, 5]


def test_mirror_perm_maps_sectors_to_mirror_images():
    mp = SL.mirror_perm()
    az = np.array([-90, -30, 30, 90, 150, -150])
    mirrored = (180 - az + 180) % 360 - 180
    assert np.allclose(SL.sector_of(mirrored), mp)
    assert np.array_equal(mp[mp], np.arange(6))


def test_region_masks_disjoint_and_split_consistent():
    m = SL.region_masks()
    stack = np.array([v for k, v in m.items()])
    assert stack.sum(0).max() <= 1
    ms = SL.region_masks(split=True)
    for k, name in enumerate(SL.LOBES):
        both = ms[f"{name} gap"] | ms[f"{name} deep"]
        assert not np.any(ms[f"{name} gap"] & ms[f"{name} deep"])
        assert np.all(both[SL.R_MID >= 76.0] == m[name][SL.R_MID >= 76.0])


def test_rules_left_right_front_back():
    rule = dict(T_abs=10.0, T_LR=4.0, T_FB=5.0)
    x = np.zeros(12)
    x[6:12] = [2, 15, 16, 1, 3, 2]                      # left lobes high
    c = apply_rules(x, rule)
    assert c["side"] == "left" and c["frontback"] == "none"
    assert c["affected"] == [False, True, True, False, False, False]
    x[6:12] = [12, 3, 3, 1, 3, 3]
    c = apply_rules(x, rule)
    assert c["side"] == "none" and c["frontback"] == "front"
    assert contrasts(x)["FB"] == 11


def test_whitened_log_projection_removes_port_gains_and_frozen_one_does_not():
    from imaging.lobe_A import KEEP_ALL
    from imaging.lobe_rulers import WhitenedLog
    rng = np.random.default_rng(0)
    F, n = 3, SL.N_ANT
    fh = np.array([3.4e9, 3.6e9, 3.8e9])
    S = rng.normal(size=(F, n, n)) + 1j * rng.normal(size=(F, n, n))
    S = 0.5 * (S + S.transpose(0, 2, 1))
    K = rng.normal(size=(21, F, 6)) + 1j * rng.normal(size=(21, F, 6))
    sig = np.abs(SL.recip(S)) * rng.uniform(0.01, 0.2, (21, F))         # unequal per-path weights
    g = 10 ** (rng.uniform(-2, 2, n) / 20) * np.exp(1j * np.deg2rad(rng.uniform(-10, 10, n)))
    Sg = S * g[None, :, None] * g[None, None, :]
    kappa = np.ones(F, complex)
    w = WhitenedLog(K, fh, kappa, sig, KEEP_ALL, S)
    assert np.max(np.abs(w.data(S_stage=Sg, S_ref=S))) < 1e-9
    frozen = SL.RegionModel(K, fh, kappa, sig, S_ref=S, kind="log")
    assert np.max(np.abs(frozen.data(S_stage=Sg, S_ref=S))) > 1e-3        # documents the erratum


def test_one_bar_verdict():
    from imaging.lobe_c3 import verdict
    assert verdict("left", "left", 2.04, 0.0) == "sensitive"
    assert verdict("left", "left", 3.2, 0.0) == "hit"
    assert verdict("left", "left", 1.5, 0.0) == "not separable"
    assert verdict(True, False, 5.0, 0.4) == "not separable"      # missed by 0.4 ruler: not a miss
    assert verdict(True, False, 5.0, 3.5) == "miss"
    assert verdict(False, False, 9.0, 0.0) == "hit"               # null prediction holds
    assert verdict("none", "left", 4.0, 3.1) == "miss"


def test_mirror_permutation_of_pairs_is_an_involution():
    from imaging.lobe_review import PM, MS
    assert np.array_equal(PM[PM], np.arange(len(PM)))
    assert np.array_equal(MS[MS], np.arange(6))
