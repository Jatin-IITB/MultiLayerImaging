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


def test_masking_replaces_nonreciprocal_bump():
    from adstage.io.masking import mask_glitches
    f = np.arange(50) * 5e6 + 3e9
    s = np.zeros((50, 3, 3), complex)
    base = 0.01 * np.exp(1j * f / 1e8)
    s[:, 0, 1] = s[:, 1, 0] = base
    s[:, 0, 0] = 0.5
    s[20:23, 0, 1] += 0.02                      # 3-point glitch on one direction only
    out, log = mask_glitches(f, s, -30)
    assert len(log) == 3 and {r["f_GHz"] for r in log} == set(f[20:23] / 1e9)
    lin = base[19] + (f[20:23] - f[19]) / (f[23] - f[19]) * (base[23] - base[19])
    np.testing.assert_allclose(out[20:23, 0, 1], lin)
    np.testing.assert_allclose(out[20:23, 1, 0], lin)
    np.testing.assert_allclose(out[:, 0, 0], 0.5)


def test_grid_never_upsamples():
    fa = np.linspace(2.8e9, 4.2e9, 281)
    fb = np.linspace(3.2e9, 4.2e9, 501)
    g = common_grid([fa, fb])
    assert np.isclose(np.median(np.diff(g)), 5e6) and g[0] == 3.2e9
    with pytest.raises(ValueError):
        common_grid([fa, fb], step_hz=2e6)


def test_modal_parseval_and_affine_metrics():
    from adstage.features.metrics import modal_reflections, circulant_projection, band_avg
    rng = np.random.default_rng(0)
    S = 0.1 * (rng.standard_normal((5, 6, 6)) + 1j * rng.standard_normal((5, 6, 6)))
    lam = modal_reflections(S)
    np.testing.assert_allclose((np.abs(lam) ** 2).sum(-2), 6 * (np.abs(S) ** 2).sum(-2))
    C = circulant_projection(S)
    np.testing.assert_allclose(C[:, 0, 1], C[:, 2, 3])
    f = np.linspace(1, 2, 11)
    P = rng.random(11)
    assert np.isclose(band_avg(f, 1 - P, (1.0, 2.0)), 1 - band_avg(f, P, (1.0, 2.0)))


def test_folds_never_share_test_views_or_heldout_sims():
    from adstage.pipeline.cv import make_folds
    name, folds = make_folds({"Normal": [0], "AD": [1, 2, 3]}, 6)
    assert name == "LODO+LOSO-within-class" and len(folds) == 9
    seen = set()
    for fd in folds:
        tr = {(s, t) for s, v in fd.train for t in v}
        te = {(s, t) for s, v in fd.test for t in v}
        assert not tr & te
        for s, v in fd.test:                      # opposite antennas leave together
            assert sorted(v) in ([0, 3], [1, 4], [2, 5])
            if s != 0:                            # held-out AD simulation absent from training
                assert all(ss != s for ss, _ in fd.train)
        seen |= te
    assert seen == {(s, t) for s in range(4) for t in range(6)}
    name, folds = make_folds({"A": [0, 1], "B": [2, 3]}, 6)
    assert name == "LOSO" and len(folds) == 4


def test_gate_catches_single_open_antenna():
    from adstage.pipeline.quality import QualityGate
    rng = np.random.default_rng(0)
    f = np.linspace(3.2e9, 4.2e9, 201)
    n = 6
    S = np.zeros((201, n, n), complex)
    for t in range(n):
        S[:, t, t] = 0.85 * np.exp(1j * f / 3e8) * (1 - 0.95 * np.exp(-((f - 3.6e9) / 2e8) ** 2))
        for k in (1, 2, 3):
            S[:, (t + k) % n, t] = S[:, t, (t + k) % n] = 0.01 / k * np.exp(1j * f / 2e8)
    cfg = {"open_short_R": 0.8, "flat_sd": 0.1, "passivity_tol": 0.2, "recip_rel_max": 1.0,
           "sym_db": [1.25, 5.0], "detune_k_sigma": 5.0, "detune_min_window_hz": 5e7}
    g = QualityGate(cfg, f).fit_detune(S[None] + 1e-4 * rng.standard_normal((5, 201, n, n)))
    assert not g.check(S[None])["invalid"][0]
    bad = S.copy()
    bad[:, 2, 2] = 1.0
    bad[:, 2, [0, 1, 3, 4, 5]] = 1e-5
    bad[:, [0, 1, 3, 4, 5], 2] = 1e-5
    out = g.check(bad[None])
    assert out["invalid"][0] and out["open_short"][0] and out["bad_antenna"][0, 2]


def test_ordinal_logit_orders_classes():
    from adstage.pipeline.classify import OrdinalLogit
    rng = np.random.default_rng(1)
    x = np.concatenate([rng.normal(m, 0.3, 200) for m in (0, 1, 2)])[:, None]
    y = np.repeat([0, 1, 2], 200)
    m = OrdinalLogit().fit(x, y)
    assert m.coef_[0] > 0 and np.all(np.diff(m.thresholds_) > 0)
    assert (m.predict(x) == y).mean() > 0.85


def test_r31_cancels_per_port_gains_and_floor_estimate():
    from adstage.features.floor import floor_power, r31
    rng = np.random.default_rng(3)
    f = np.linspace(3.2e9, 4.2e9, 101)
    n = 6
    S = np.zeros((101, n, n), complex)
    for t in range(n):
        S[:, t, t] = 0.5
        for k, a in ((1, 3e-3), (2, 1e-3), (3, 2e-3)):
            S[:, (t + k) % n, t] = S[:, t, (t + k) % n] = a * (1 + 0.1 * t) * np.exp(1j * f / 1e8)
    g = 10 ** (rng.uniform(-2, 2, n) / 20) * np.exp(1j * rng.uniform(0, 6, n))
    Sg = S * g[None, :, None] * g[None, None, :]
    band = (f[0], f[-1])
    zero = np.zeros(1)
    np.testing.assert_allclose(r31(f, Sg[None], zero, band), r31(f, S[None], zero, band), rtol=1e-10)
    floor = 1e-7                                          # -70 dB per entry
    noisy = S[None] + np.sqrt(floor / 2) * (rng.standard_normal((20, 101, n, n))
                                            + 1j * rng.standard_normal((20, 101, n, n)))
    est = 10 * np.log10(floor_power(noisy))
    assert np.all(np.abs(est + 70) < 0.5)


def test_cross_ratios_cancel_per_port_gains_and_vanish_when_symmetric():
    import importlib.util
    import pathlib
    p = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "07_lobe.py"
    spec = importlib.util.spec_from_file_location("lobe07", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rng = np.random.default_rng(5)
    bp = np.exp(rng.normal(size=(6, 6)))
    bp = bp + bp.T                                         # reciprocal band powers
    g = 10 ** (rng.uniform(-2, 2, 6) / 10)                 # per-port power gains, ±2 dB
    bpg = bp * g[:, None] * g[None, :]
    a, b = mod.cross_ratios(bp), mod.cross_ratios(bpg)
    assert len(a) == 45
    np.testing.assert_allclose([a[k] for k in a], [b[k] for k in a], atol=1e-10)
    # a rotationally symmetric (circulant) head has zero asymmetry cross-ratios
    d = mod.DIST
    circ = np.array([[1.0, 0.3, 0.05, 0.1][d[i, j]] for i in range(6) for j in range(6)]).reshape(6, 6)
    cls = mod.chi_classes()
    chi = mod.cross_ratios(circ)
    asym = [chi[n] - np.mean([s * chi[m] for m, s in cls[n]]) for n in chi]
    np.testing.assert_allclose(asym, 0, atol=1e-10)


def test_manifest_set_filter_selects_rows_listing_the_set():
    import pathlib
    from adstage.config import load_config
    from adstage.io.dataset import load_dataset
    root = pathlib.Path(__file__).resolve().parents[1]
    sets = {}
    n = {}
    for name in ("config_lobe.yaml", "config_lobe_A.yaml", "config_lobe_B.yaml", "config_lobe_tests.yaml"):
        ds = load_dataset(load_config(root, name), root)
        sets[name] = dict(zip(ds.classes, ds.files))
        n[name] = len(ds.files)
    assert sets["config_lobe.yaml"]["Normal"].endswith("Healthy_sliced.s6p") and n["config_lobe.yaml"] == 4
    assert sets["config_lobe_A.yaml"]["Normal"].endswith("Healthy_sliced_new.s6p")
    # kind: stage keeps the test designs (LeftOnly_test_c3 is class Mild) out of the staging set
    assert sets["config_lobe_A.yaml"]["Mild"].endswith("Mild_lobe.s6p") and n["config_lobe_A.yaml"] == 4
    assert n["config_lobe_B.yaml"] == 4 and sets["config_lobe_B.yaml"]["Mild"].endswith("Mild_lobe_new.s6p")
    assert sets["config_lobe_B.yaml"]["Severe"].endswith("Severe_lobe_c3.s6p")
    assert set(sets["config_lobe_tests.yaml"]) == {"Normal", "Mild", "MCI"} and n["config_lobe_tests.yaml"] == 3
    assert sets["config_lobe_tests.yaml"]["Mild"].endswith("LeftOnly_test_c3.s6p")
