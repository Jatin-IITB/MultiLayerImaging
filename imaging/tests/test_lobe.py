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
