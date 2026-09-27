import numpy as np
import pytest

from adstage.io.dataset import class_from_filename, common_grid, resample
from adstage.io.touchstone import plausibility, read_touchstone
from adstage.ring import ring_distance


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text)
    return p


def test_three_port_multiline_ma(tmp_path):
    # Row-major, each matrix row on its own line, freq in MHz, comments interleaved.
    txt = """! header junk: ignored
# MHz S MA R 50
! Port[1] = WRONG_LABEL
100 0.5 0 0.1 90 0.2 180
    0.1 90 0.6 10 0.3 -90
    0.2 180 0.3 -90 0.7 45
! Gamma 0 0 0
200 0.5 1 0.1 91 0.2 181
    0.1 91 0.6 11 0.3 -89
    0.2 181 0.3 -89 0.7 46
"""
    ts = read_touchstone(_write(tmp_path, "x.s3p", txt))
    assert ts.s.shape == (2, 3, 3)
    np.testing.assert_allclose(ts.f_hz, [100e6, 200e6])
    np.testing.assert_allclose(ts.s[0, 0, 2], 0.2 * np.exp(1j * np.pi))
    np.testing.assert_allclose(ts.s[0, 1, 2], 0.3 * np.exp(-1j * np.pi / 2))
    assert len(ts.comments) == 3


def test_two_port_column_order_db(tmp_path):
    # v1 2-port order is S11 S21 S12 S22
    txt = "# GHz S DB R 50\n1.0 -6 0 -20 0 -30 0 -3 0\n"
    ts = read_touchstone(_write(tmp_path, "y.s2p", txt))
    np.testing.assert_allclose(abs(ts.s[0, 1, 0]), 10 ** (-20 / 20))   # S21
    np.testing.assert_allclose(abs(ts.s[0, 0, 1]), 10 ** (-30 / 20))   # S12


def test_ri_and_hz(tmp_path):
    txt = "# Hz S RI R 50\n1e9 0.1 0.2 0 0 0 0 0.3 -0.4\n"
    ts = read_touchstone(_write(tmp_path, "z.s2p", txt))
    assert ts.f_hz[0] == 1e9
    np.testing.assert_allclose(ts.s[0, 1, 1], 0.3 - 0.4j)


def test_misaligned_record_rejected(tmp_path):
    txt = "# GHz S MA R 50\n1.0 0.5 0 0.1 0\n0.1 0 0.5 0 2.0 0.5 0 0.1 0 0.1 0 0.5 0\n"
    with pytest.raises(ValueError):
        read_touchstone(_write(tmp_path, "m.s2p", txt))


def test_plausibility_flags_wrong_unit(tmp_path):
    txt = "# Hz S MA R 50\n3.5 0.5 0 0.1 0 0.1 0 0.5 0\n"     # really GHz
    ts = read_touchstone(_write(tmp_path, "u.s2p", txt))
    assert plausibility(ts, (1e9, 6e9))


def test_resample_exact_on_shared_nodes():
    f = np.arange(0, 11) * 2.0
    s = (np.sin(f) + 1j * np.cos(f))[:, None, None]
    g = np.array([0.0, 4.0, 10.0])
    np.testing.assert_allclose(resample(f, s, g)[:, 0, 0], s[[0, 2, 5], 0, 0], atol=1e-12)


def test_common_grid_intersection():
    g = common_grid([np.linspace(2.8e9, 4.2e9, 281), np.linspace(3.2e9, 4.2e9, 501)], 5e6)
    assert g[0] == 3.2e9 and g[-1] == 4.2e9 and g.size == 201


def test_ring_distance_and_labels():
    d = ring_distance(np.array([4, 3, 2, 1, 6, 5]))
    assert d[0, 1] == 1 and d[0, 3] == 3 and d[0, 5] == 1 and d[0, 4] == 2
    assert class_from_filename("Brain_sevem_layer_MildAD.s6p") == "Mild"
    assert class_from_filename("brain_sevem_layer_Healthy.s6p") == "Normal"
