"""Unit tests for the imaging study: delays, time transform, forward model, Born, solvers.

Run:  python -m pytest imaging/tests -q
"""
import numpy as np
import pytest
from scipy.special import spherical_jn, spherical_yn

from imaging.beamform import Imager, fibonacci_dirs
from imaging.common import HeadParams, R_CSF
from imaging.fields import read_fld
from imaging.forward import KernelRingModel, RingModel, ring_from_ant
from imaging.linear import TikhonovSVD, born_prefactor
from imaging.mie import (C0, LayeredSolution, Sphere, eps_complex, free_space_field,
                         internal_field, receiver_field_scattered, rotation_to_pole)
from imaging.study_i3 import theta_of, theta_to_u, u_to_theta
from imaging.timedomain import TimeResponse, delay_effective, delay_layered

F2 = np.array([3.3e9, 3.9e9])
HEAD_R = np.array([0.025, 0.076, 0.083, 0.0835, 0.0865, 0.0875, 0.088])


def head_eps(f):
    mats = [(47.7, 2.42), (35.3, 1.65), (47.7, 2.42), (65, 4.27), (10.8, 0.61), (10.5, 0.42),
            (37, 2.0)]
    return np.array([eps_complex(e, s, f) for e, s in mats])


# ---------------------------------------------------------------- delay model
def test_delay_layered_equals_effective_for_homogeneous_head():
    a = np.array([0.0, 0.0, 97.55])
    pts = np.random.default_rng(1).uniform(-60, 60, (50, 3))
    lay = [(25.0, 40.0), (76.0, 40.0), (88.0, 40.0)]
    np.testing.assert_allclose(delay_layered(a, pts, lay), delay_effective(a, pts, 40.0), rtol=1e-12)


def test_delay_layered_radial_ray_by_hand():
    a = np.array([0.0, 0.0, 97.55])
    lay = [(r, e) for (r, e, s) in HeadParams.stage("Normal").layers()]
    t = delay_layered(a, np.zeros((1, 3)), lay)[0]
    radii = [0.0] + [r for r, _ in lay]
    opl = 97.55 - 88.0 + sum((radii[i + 1] - radii[i]) * np.sqrt(lay[i][1]) for i in range(len(lay)))
    assert t == pytest.approx(opl * 1e-3 / C0, rel=1e-12)


def test_delay_outside_head_is_vacuum():
    a = np.array([0.0, 0.0, 97.55])
    p = np.array([[0.0, 95.0, 97.55]])                       # line stays outside r = 88
    assert delay_effective(a, p, 40.0)[0] == pytest.approx(0.095 / C0, rel=1e-12)


# ---------------------------------------------------------------- IFFT / windowing
@pytest.mark.parametrize("kind", ["hann", "kaiser", "rect"])
def test_time_response_peaks_at_delay(kind):
    f = np.arange(3.2e9, 4.2e9 + 1, 5e6)
    tau0 = 2.37e-9
    X = 0.7 * np.exp(-2j * np.pi * f * tau0)                 # e^{+jwt}: delay -> e^{-jw tau}
    tr = TimeResponse(f, X[None], kind)
    t = np.arange(0, 8e-9, 1e-12)
    h = np.abs(tr(t[None]))[0]
    assert t[np.argmax(h)] == pytest.approx(tau0, abs=5e-12)
    assert h.max() == pytest.approx(0.7 * tr.w.sum(), rel=2e-3)   # coherent sum at the peak
    # value and phase at the exact delay: sum_f W X e^{j2pi f tau0} = 0.7 sum W (real)
    v = tr(np.array([[tau0]]))[0, 0]
    assert abs(np.angle(v)) < 2e-2


def test_pulse_width_scales_with_bandwidth():
    f1 = np.arange(3.2e9, 4.2e9 + 1, 5e6)
    f2 = np.arange(2.8e9, 4.2e9 + 1, 5e6)
    w1 = TimeResponse(f1, np.ones((1, f1.size))).pulse_width()
    w2 = TimeResponse(f2, np.ones((1, f2.size))).pulse_width()
    assert w1 / w2 == pytest.approx(1.4, rel=0.05)


def test_dmas_identity_matches_explicit_pairs():
    rng = np.random.default_rng(0)
    s = rng.normal(size=(21, 7))
    g = np.sign(s) * np.sqrt(np.abs(s))
    fast = 0.5 * (g.sum(0) ** 2 - (g ** 2).sum(0))
    slow = sum(np.sign(s[p] * s[q]) * np.sqrt(np.abs(s[p] * s[q]))
               for p in range(21) for q in range(p + 1, 21))
    np.testing.assert_allclose(fast, slow, rtol=1e-12)


def test_das_focuses_point_scatterer():
    """Synthetic point scatterer in a homogeneous medium: DAS peak at the true location."""
    f = np.arange(3.2e9, 4.2e9 + 1, 5e6)
    th = np.deg2rad(60.5)
    ants = np.array([[97.55 * np.sin(th) * np.cos(p), 97.55 * np.sin(th) * np.sin(p),
                      97.55 * np.cos(th)] for p in np.deg2rad(60 * np.arange(6))])
    tgt = np.array([[20.0, -10.0, 44.0]])
    lay = [(88.0, 30.0)]
    tau = np.stack([delay_layered(a, tgt, lay)[0] for a in ants])
    x = np.stack([np.exp(-2j * np.pi * f * (tau[i] + tau[j])) for i in range(6) for j in range(i, 6)])
    g = np.arange(-40, 41, 2.0)
    X, Y = np.meshgrid(g, g, indexing="ij")
    pts = np.stack([X, Y, np.full_like(X, 44.0)], -1).reshape(-1, 3)      # the target's plane
    pk = pts[np.argmax(Imager(f, ants, pts, lay).das(x))]
    assert np.linalg.norm(pk[:2] - tgt[0, :2]) <= 2.9                     # within one pixel


# ---------------------------------------------------------------- forward model
def test_free_space_limit_matches_closed_form_dipole():
    sol = LayeredSolution(Sphere(HEAD_R, np.ones((7, 2), complex), F2), 120)
    assert np.abs(sol.a[1:]).max() == 0 and np.abs(sol.b[1:]).max() == 0
    pts = np.random.default_rng(0).normal(size=(8, 3))
    pts = pts / np.linalg.norm(pts, axis=1)[:, None] * np.linspace(0.005, 0.085, 8)[:, None]
    E = internal_field(sol, 0.09755, pts)
    E0 = free_space_field(sol.sph.k0, np.array([0, 0, 0.09755]), np.array([1.0, 0, 0]), pts)
    assert np.abs(E - E0).max() / np.abs(E0).max() < 1e-5      # series truncation at r = 85 mm


def test_homogeneous_sphere_mie_coefficients():
    eps = eps_complex(47.7, 2.42, F2)
    R = 0.02
    sol = LayeredSolution(Sphere(np.array([R]), eps[None], F2), 30)
    x = 2 * np.pi * F2 / C0 * R
    m = np.sqrt(eps)
    n = np.arange(1, 31)[:, None]
    psi = lambda n, z: z * spherical_jn(n, z)                                   # noqa: E731
    dpsi = lambda n, z: spherical_jn(n, z) + z * spherical_jn(n, z, derivative=True)  # noqa: E731
    h = lambda n, z: spherical_jn(n, z) + 1j * spherical_yn(n, z)               # noqa: E731
    xi = lambda n, z: z * h(n, z)                                              # noqa: E731
    dxi = lambda n, z: h(n, z) + z * (spherical_jn(n, z, derivative=True)       # noqa: E731
                                      + 1j * spherical_yn(n, z, derivative=True))
    mx = m * x
    a = (m * psi(n, mx) * dpsi(n, x) - psi(n, x) * dpsi(n, mx)) / (m * psi(n, mx) * dxi(n, x) - xi(n, x) * dpsi(n, mx))
    b = (psi(n, mx) * dpsi(n, x) - m * psi(n, x) * dpsi(n, mx)) / (psi(n, mx) * dxi(n, x) - m * xi(n, x) * dpsi(n, mx))
    assert np.nanmax(np.abs(sol.a[1:] - a) / np.abs(a)) < 1e-9
    assert np.nanmax(np.abs(sol.b[1:] - b) / np.abs(b)) < 1e-9
    sol3 = LayeredSolution(Sphere(np.array([0.005, 0.012, 0.02]), np.repeat(eps[None], 3, 0), F2), 30)
    np.testing.assert_allclose(sol3.a, sol.a, atol=1e-14)


def test_tangential_E_continuous_across_every_interface():
    sol = LayeredSolution(Sphere(HEAD_R, head_eps(F2), F2), 120)
    d = np.array([0.3, -0.5, 0.8])
    d /= np.linalg.norm(d)
    tang = lambda v: v - np.outer(v @ d, d)                                     # noqa: E731
    for rb in HEAD_R[:-1]:
        Ei = internal_field(sol, 0.09755, np.array([d * (rb - 1e-9)]))[:, 0]
        Eo = internal_field(sol, 0.09755, np.array([d * (rb + 1e-9)]))[:, 0]
        assert np.abs(tang(Ei) - tang(Eo)).max() / np.abs(tang(Eo)).max() < 1e-5


def test_scattered_field_reciprocity():
    sol = LayeredSolution(Sphere(HEAD_R, head_eps(F2), F2), 100)
    rs = 0.09755
    th = np.deg2rad(60.5)
    posB = rs * np.array([np.sin(th) * np.cos(1.0), np.sin(th) * np.sin(1.0), np.cos(th)])
    posA, pA = np.array([0, 0, rs]), np.array([1.0, 0, 0])
    pB = np.array([0.2, 0.9, 0.1])
    pB -= posB * (pB @ posB) / rs ** 2
    pB /= np.linalg.norm(pB)
    eAB = receiver_field_scattered(sol, rs, posB[None])[:, 0] @ pB
    Rm = rotation_to_pole(posB, pB)
    eBA = receiver_field_scattered(sol, rs, (Rm @ posA)[None])[:, 0] @ (Rm @ pA)
    np.testing.assert_allclose(eAB, eBA, rtol=1e-10)


def test_kernel_model_equals_rotation_model():
    p = HeadParams.stage("Mild")
    a = RingModel("theta", nmax=60).V(p, F2, total=True)
    km = KernelRingModel("point", "theta", nmax=60)
    b = ring_from_ant(km.scattered(p, F2) + km.direct(F2))
    np.testing.assert_allclose(b, a, rtol=1e-9, atol=1e-12 * np.abs(a).max())


def test_harmonic_convergence():
    p0, p1 = HeadParams.stage("Normal"), HeadParams.stage("Mild")
    out = []
    for nm in (60, 90):
        km = KernelRingModel("point", "phi", nmax=nm)
        out.append(ring_from_ant(km.scattered(p1, F2) - km.scattered(p0, F2)))
    assert np.abs(out[0] - out[1]).max() / np.abs(out[1]).max() < 1e-6


def test_born_equals_exact_thin_shell_perturbation():
    p = HeadParams.stage("Normal")
    rm = RingModel("theta", nmax=90)
    r1, r2 = 78.0, 80.0
    de = 1e-3
    fd = rm.V(p, F2, extra_layers=[(r1, r2, de * np.ones(2))]) - rm.V(p, F2)
    xg, wg = np.polynomial.legendre.leggauss(6)
    rr = 0.5 * (r2 - r1) * xg + 0.5 * (r1 + r2)
    wr = 0.5 * (r2 - r1) * wg
    d = fibonacci_dirs(3000)
    pts = (rr[:, None, None] * d[None]).reshape(-1, 3)
    w = (wr[:, None] * rr[:, None] ** 2 * np.ones(len(d))[None] * 4 * np.pi / len(d)).ravel() * 1e-9
    E = [rm.fields(p, F2, pts, a) for a in range(4)]
    born = np.stack([born_prefactor(F2) * np.einsum("fpc,fpc,p->f", E[0], E[k], w) for k in range(4)], -1) * de
    assert np.abs(fd - born).max() / np.abs(fd).max() < 1e-3


# ---------------------------------------------------------------- misc
def test_fld_reader_parses_header_order(tmp_path):
    txt = ("Min: -0.09 -0.09 -0.09\nMax: 0.09 0.09 0.09\nGrid Size: 0.003 0.003 0.003\n\n"
           "X Y Z Ey_real Ey_imag Ex_real Ex_imag Ez_real Ez_imag\n"
           "0.001 0.002 0.003 1 2 3 4 5 6\n-0.03 0 0.09 -1 0 0 1 2 -2\n")
    p = tmp_path / "E.fld"
    p.write_text(txt)
    pts, E = read_fld(p)
    np.testing.assert_allclose(pts[0], [1.0, 2.0, 3.0])
    np.testing.assert_allclose(E[0], [3 + 4j, 1 + 2j, 5 + 6j])


def test_fld_reader_hfss_complex_vector_layout(tmp_path):
    from imaging.fields import Grid
    hdr = ('Grid Output Min: [-3mm -3mm -3mm] Max: [3mm 3mm 3mm] Grid Size: [3mm 3mm 3mm] \n'
           'X, Y, Z, Complex Vector data "<Ex,Ey,Ez>"\n')
    lines = []
    for x in (-3, 0, 3):
        for y in (-3, 0, 3):
            for z in (-3, 0, 3):                                   # z fastest
                if (x, y, z) == (3, 3, 3):
                    lines.append(f"{x/1e3:.6e} {y/1e3:.6e} {z/1e3:.6e}  Nan Nan Nan Nan Nan Nan ")
                else:
                    lines.append(f"{x/1e3:.6e} {y/1e3:.6e} {z/1e3:.6e}  {x} {y} {z} 1 2 -2 ")
    p = tmp_path / "E.fld"
    p.write_text(hdr + "\n".join(lines) + "\n")
    pts, E = read_fld(p)
    np.testing.assert_allclose(pts[1], [-3.0, -3.0, 0.0])          # metres -> mm
    np.testing.assert_allclose(E[1], [-3 - 3j, 0 + 1j, 2 - 2j])     # (re, im) per component
    assert np.isnan(E[-1]).all()
    g = Grid(pts, E)
    assert g.full and g.z_fastest and g.E.shape == (3, 3, 3, 3)


def test_parameter_map_roundtrip():
    for s in ("Normal", "Mild", "Severe"):
        th = theta_of(HeadParams.stage(s))
        np.testing.assert_allclose(u_to_theta(theta_to_u(th)), th, rtol=1e-9)
        assert R_CSF - th[0] > 0


def test_tikhonov_svd_matches_normal_equations():
    rng = np.random.default_rng(3)
    J, d = rng.normal(size=(20, 50)), rng.normal(size=20)
    lam = 0.7
    x = TikhonovSVD(J).solve(d, lam)
    x2 = np.linalg.solve(J.T @ J + lam ** 2 * np.eye(50), J.T @ d)
    np.testing.assert_allclose(x, x2, rtol=1e-8, atol=1e-10)
