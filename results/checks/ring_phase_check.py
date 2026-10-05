"""Independent re-computation of the 'raw phase' ring numbers (deck slide raw_pattern). Viewing only.
Run: python results/checks/ring_phase_check.py   (reads data/raw/*.s6p; numpy only)
Per antenna T_k: phase delay = -(1/2)[mean_f angle(S_k,k+1 / Sref_k,k+1) + mean_f angle(S_k,k-1 / Sref_k,k-1)],
f in 3.30-3.65 GHz, degrees. Own Touchstone reader; no repo code."""
import numpy as np, glob, os
RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "raw") + os.sep
ATT = RAW
def read_s6p(path):
    fmt = None; nums = []
    for line in open(path):
        line = line.split("!")[0].strip()
        if not line: continue
        if line.startswith("#"): fmt = line.upper().split(); continue
        nums += [float(v) for v in line.split()]
    a = np.array(nums).reshape(-1, 1 + 72)
    unit = {"HZ": 1, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9}[fmt[1]]
    f = a[:, 0] * unit; p = a[:, 1:].reshape(-1, 6, 6, 2)
    if "MA" in fmt: S = p[..., 0] * np.exp(1j * np.deg2rad(p[..., 1]))
    elif "DB" in fmt: S = 10 ** (p[..., 0] / 20) * np.exp(1j * np.deg2rad(p[..., 1]))
    else: S = p[..., 0] + 1j * p[..., 1]
    # Touchstone v1 6-port: row-major (S11 S12 ... S16, S21 ...)
    PORT_OF_ANT = [3, 2, 1, 0, 5, 4]          # T1..T6 -> port index (Port1..6 = T4,T3,T2,T1,T6,T5)
    S = S[:, PORT_OF_ANT][:, :, PORT_OF_ANT]
    S = 0.5 * (S + S.transpose(0, 2, 1))
    return f, S
def ring(path, ref, band=(3.30e9, 3.65e9)):
    f, S = read_s6p(path); f2, R = read_s6p(ref); assert np.allclose(f, f2)
    m = (f >= band[0] - 1) & (f <= band[1] + 1)
    out = []
    for k in range(6):
        ph = [np.degrees(np.angle(S[m, k, j] / R[m, k, j])).mean() for j in ((k + 1) % 6, (k - 1) % 6)]
        out.append(-0.5 * sum(ph))
    return np.array(out), m.sum()
H6 = RAW + "new_with_slices_Healthy_sliced_new.s6p"; H7 = RAW + "new_with_slices_Healthy_sliced.s6p"
designs = {"Healthy H7": H7, "Mild p5": RAW + "new_with_slices_Mild_lobe.s6p", "Mild p6": RAW + "new_with_slices_Mild_lobe_new.s6p",
           "Moderate p5": RAW + "new_with_slices_Moderate_lobe.s6p", "Moderate c3": RAW + "new_with_slices_Moderate_lobe_c3.s6p",
           "Severe p5": RAW + "new_with_slices_Severe_lobe.s6p", "Severe c3": RAW + "new_with_slices_Severe_lobe_c3.s6p",
           "LeftOnly c3": RAW + "new_with_slices_LeftOnly_test_c3.s6p", "MCI c3": RAW + "new_with_slices_MCI_lobe_c3.s6p",
           "RightOnly": ATT + "new_with_slices_RightOnly_test.s6p", "Test_B": ATT + "new_with_slices_Test_B.s6p"}
for r in (7, 19, 31, 43): designs[f"Null rot{r:02d}"] = ATT + f"new_with_slices_Null_rot{r:02d}.s6p"
hdr = "design".ljust(14) + "".join(f"{'T'+str(k+1):>7s}" for k in range(6)) + "   ring-mean  pattern(max-min)  left(T2,T3)-right(T5,T6)"
for refname, ref in (("H6", H6), ("H7", H7)):
    print(f"\n=== reference {refname} ===\n" + hdr)
    for name, p in designs.items():
        if name == "Healthy H7" and refname == "H7": name, p = "Healthy H6", H6
        v, n = ring(p, ref)
        lr = (v[1] + v[2]) / 2 - (v[4] + v[5]) / 2
        print(name.ljust(14) + "".join(f"{x:7.1f}" for x in v) + f"   {v.mean():8.1f}  {v.max()-v.min():10.1f}  {lr:12.1f}")
print("points in band:", n)
