# Method note: baseline + estimated change by Bayesian sector-state inversion (imaging2)

Code: `imaging2/` (entry points `python -m imaging2.run_lobe2`, `python -m imaging2.make_figures`,
`python -m imaging2.noise_study`). Commit hash stored in `results/imaging2/posteriors.json` (`code`).

## Image model (what is drawn)
Image = **healthy baseline** (Healthy_sliced geometry and Shehab materials, the "patient's earlier scan")
**+ estimated change**. The change is parameterised by the phantom family's own physics:

| unknown | values | prior |
|---|---|---|
| stage s (material table of the affected gray/white matter and of the CSF everywhere) | Healthy, Mild, Moderate, Severe | 1/4 each |
| per sector k = 1..6 (60° full-height wedges centred on T1..T6): unaffected, or affected with cortex retreat e_k | {unaffected} ∪ {0.5, 1.0, …, 22 mm} | P(unaffected) = 1/2, e uniform |
| r_hip (hippocampus) | not estimated | the array has no sensitivity there (core x-hatched in every figure) |

Affected sector k: gray matter moved from 76–83 mm to 76−e_k … 83−e_k, the gap filled with CSF of stage s,
diseased gray/white materials. Every sector carries the stage's CSF material in its 0.5 mm layer.
Structural assumptions (from the phantom design, stated, not estimated): six 60° full-height wedges, one stage per head.

## Forward model (surrogate), fitted leave-one-design-out
Data: complex log-ratio L_p(f) = ln(S_p,design / S_p,healthy) for the 21 reciprocal paths, 201 frequencies
3.2–4.2 GHz, **amplitude and phase**, glitch-masked (same −30 dB rule as the main session), stage file
against the healthy mesh with the same stop rule (lobe_A: H6; lobe_B: H7).

L_p(f) = Σ_k Σ_m C_{o(p,k),m}(f) · φ_{k,m}(f)

* φ_k(f): **layered-stack feature** = Re and Im of ΔΓ_k(f), the change of the exact plane-wave reflection
  coefficient of sector k's tissue column (skin 0.5 / fat 1 / skull 3 / CSF / gray / white mm, transmission-line
  recursion, normal incidence, TM) against the healthy column. ΔΓ is non-linear in e and in the materials
  (screening by lossy CSF, thin-layer resonance), which is what lets the surrogate extrapolate across stages.
  The skin/fat/skull values are assumptions (not recorded in the repo); they are common to all designs.
* o(p,k): orbit of the (path, sector) pair under the ring's D6 symmetry (13 orbits). Sharing C across an orbit
  is the symmetry augmentation: each solved design is used in all 12 rotated/mirrored copies at once.
* C: complex, per frequency, ridge regression (real and imaginary parts separately, weighted by the noise).

Feature set and ridge λ are chosen by an **inner leave-one-design-out on the training designs only**
(candidates: ΔΓ_TM at normal incidence; + evanescent TM k_t = 2k0; + TE k_t = 2k0; λ ∈ {1e−3, 1e−2, 1e−1}).
All folds selected the single normal-incidence feature. Earlier candidates that were rejected:
linear depth-moment features (∫ e^{−d/δ} Δε_r, Δσ) predicted held-out Mild/Moderate/LeftOnly as well but
failed on Severe (held-out χ² ≈ 94 vs 15 with ΔΓ; signal 170); the v2 uniform designs were excluded because
their own-project mesh noise (Uniform_MCI − v2 Healthy: 2.3 dB, 15–40°) exceeds the whole lobe-Mild signal.

**Leave-one-design-out:** to image design X, both meshes of X are removed from the surrogate fit, the noise
ruler and the model-error estimate; the Healthy pair (H7 vs H6, zero change) and MCI stay in training as
"no change" examples except when they are the target.

## Noise model and likelihood
Gaussian on Re/Im of L. Variance per path type and frequency = numerical noise (mesh pairs: the two meshes of
each design against their own matched healthy mesh, double difference / √2, plus H7 − H6) + surrogate
model error (inner leave-one-out residuals) [+ instrument noise in the noise study]. The 201 frequencies are
correlated (whitened-noise correlation length ℓ = 14–16 samples); the log-likelihood is divided by ℓ.
**Birge rule:** if the best fit has χ² per effective dof > 1, the likelihood is tempered by that ratio and the
posterior recomputed (uses only the target's own data). It fired for Severe (2.6 / 2.1) and the shuffled control (23).

## Solver
Exact Gibbs sampling over the 6 sector states (the model is additive over sectors, so each conditional is a
46-point discrete distribution, evaluated exactly), 600 sweeps (150 burn-in), started from iterated conditional
modes. Stage evidence by Chib's method (reduced Gibbs runs). Output: joint posterior P(s, x_k) per sector.

## Rendering, uncertainty, sensitivity fade
Posterior-mean ε_r and σ per voxel (mixture over stage and e_k), so an uncertain boundary is drawn blurred;
posterior SD is saved with the arrays. Fade: from the HFSS E-field exports of the healthy head (3-D, 3 mm grid,
3.4/3.6/3.8 GHz), the Born SNR of a 1 cm³ change |Δε*| = 20 summed over the 21 paths with the mesh-noise ruler,
scaled to the band (√(13/3)); opacity 0 at SNR ≤ 0.5, 1 at SNR ≥ 4, log-linear between; faded areas are hatched.
The full-height wedge assumption means the estimate below the ring (z ≤ 20 mm) is model extrapolation, and it is
faded accordingly.

## Data used
All 21 paths (reflection, neighbour, second-neighbour, opposite), amplitude and phase, 3.2–4.2 GHz.
Lobe designs only (10 files of 6 designs + 2 healthy meshes). Field exports only for the sensitivity fade.

## Runtime (laptop, 12 threads)
Surrogate fit with nested selection ≈ 10 s per fold; posterior ≈ 5–8 s per target (≈ 15 s with Birge rerun);
all 14 targets and controls ≈ 3 min; full figure set ≈ 15 min; noise study (6 targets × 4 conditions × 12 draws) ≈ 20 min.

## Limits (read before trusting an image)
* One idealised head; the surrogate is trained on 5–6 designs of the same phantom family. Not generalisation.
* The wedge geometry and one-stage-per-head are imposed, not measured; vertical extent is not observed.
* Depth: retreat beyond ≈ 8–12 mm (Mild/Moderate) and ≈ 3–5 mm (Severe, whose CSF screens deeper tissue) is
  weakly or not determined; the posterior intervals show it.
* Severe is an extrapolation (its materials are outside every training design): stage and "all lobes affected"
  are recovered, depth is not.
