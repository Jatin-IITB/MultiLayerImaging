"""Bayesian sector-state inversion with the layered-stack surrogate.

Unknowns: stage s in {Healthy, Mild, Moderate, Severe} (sets the material table of the affected
gray/white matter and of the CSF everywhere; structural prior shared by every lobe design) and, for
each sector k, its state x_k in {unaffected} U {affected with CSF expansion e_k in 0.5 .. 22 mm}.
Prior: P(s) = 1/4; P(unaffected) = 1/2; e | affected uniform on the grid. Healthy => all
unaffected, no change at all. r_hip is not estimated (no sensitivity, see README); it is drawn from
the prior for rendering only and drawn hatched.

Likelihood: Gaussian on the complex log-ratio data (real = amplitude, imag = phase), per path and
frequency, variance = numerical noise (mesh pairs) + surrogate model error (nested
leave-one-design-out residuals) [+ measurement noise], divided by the frequency correlation
length so that 201 correlated frequencies are not counted as 201 independent ones.

Sampler: Gibbs over sectors with exact discrete conditionals (the model is additive over sectors).
Stage evidence: Chib (1995) from the Gibbs output with reduced runs.
"""
from __future__ import annotations

import numpy as np

from .data import N, HEALTHY_LOBE, lobe
from .surrogate import STACK_SETS, stack_features

STAGES = ["Healthy", "Mild", "Moderate", "Severe"]
E_GRID = np.arange(0.5, 22.01, 0.5)
N_CAND = 1 + len(E_GRID)                       # 0 = unaffected


def candidate_features(stage, f, sset):
    """(N_CAND, M, F) features of one sector in each candidate state for a stage (all sectors
    share the depth profile in the lobe geometry, so sector 0 is used)."""
    out = []
    t0 = lobe(np.zeros(N), stage, 25.0, affected=np.zeros(N, bool))
    t0.tissue_stage = stage
    out.append(stack_features(t0, f, sset)[0])
    for e in E_GRID:
        ev = np.zeros(N)
        ev[0] = e
        out.append(stack_features(lobe(ev, stage, 25.0), f, sset)[0])
    return np.stack(out)


class Posterior:
    def __init__(self, sur, s_re, s_im, ell, f, sset, gain_free=False):
        self.sur, self.f, self.sset, self.ell = sur, f, sset, ell
        self.w_re = 1.0 / (s_re ** 2 * ell)
        self.w_im = 1.0 / (s_im ** 2 * ell)
        self.gain_free = gain_free
        self.tau = 1.0                         # likelihood temperature (Birge ratio, see run)
        self.contrib = {}                      # stage -> (6, N_CAND, 21, F) complex
        for s in STAGES[1:]:
            cf = candidate_features(s, f, sset)                     # (C, M, F)
            arr = []
            for k in range(N):
                G = sur.sector_gain(k)                              # (21, M, F)
                arr.append(np.einsum("pmf,cmf->cpf", G, cf))
            self.contrib[s] = np.stack(arr)
            if gain_free:
                self.contrib[s] = self.project(self.contrib[s])
        self.lp_prior = np.log(np.r_[0.5, np.full(len(E_GRID), 0.5 / len(E_GRID))])
        # constant pieces of the sector conditionals (weighted design rows and quadratic terms)
        self._A, self._Q = {}, {}
        for s, Cs in self.contrib.items():
            nc = Cs.shape[1]
            self._A[s] = [np.concatenate([(Cs[k].real * self.w_re).reshape(nc, -1),
                                          (Cs[k].imag * self.w_im).reshape(nc, -1)], 1) for k in range(N)]
            self._Q[s] = [((Cs[k].real ** 2) * self.w_re).sum((1, 2)) + ((Cs[k].imag ** 2) * self.w_im).sum((1, 2))
                          for k in range(N)]

    # -- per-port gain nuisance --------------------------------------------------------------------
    def project(self, R):
        """Remove the best-fitting per-port complex log-gain (constant over frequency) from path data
        R (..., 21, F): R_ij -> R_ij - (g_i + g_j), g by weighted least squares on the frequency
        means. Linear, so applied identically to data and to every model contribution."""
        from .data import PI, PJ
        A = np.zeros((len(PI), N))
        A[np.arange(len(PI)), PI] += 1
        A[np.arange(len(PI)), PJ] += 1
        out = np.array(R, copy=True)
        for part, w in ((0, self.w_re.mean(1)), (1, self.w_im.mean(1))):
            W = np.diag(w)
            H = A @ np.linalg.solve(A.T @ W @ A, A.T @ W)                 # (21, 21) hat matrix
            X = out.real if part == 0 else out.imag
            m = X.mean(-1, keepdims=True)                                  # (..., 21, 1)
            corr = np.einsum("pq,...qf->...pf", H, m)
            if part == 0:
                out = out - corr
            else:
                out = out - 1j * corr
        return out

    # -- likelihood pieces ---------------------------------------------------------------------
    def chi2(self, R):
        return float((self.w_re * R.real ** 2).sum() + (self.w_im * R.imag ** 2).sum())

    def _cond(self, s, k, R_wo_k):
        """log p(x_k = c | rest, y) up to a constant, for every candidate c. R_wo_k: data minus
        prediction of all sectors except k."""
        r = np.concatenate([R_wo_k.real.ravel(), R_wo_k.imag.ravel()])
        lin = self._A[s][k] @ r
        return -0.5 * (self._Q[s][k] - 2 * lin) / self.tau + self.lp_prior

    def predict(self, s, x):
        if s == "Healthy":
            return 0.0
        return sum(self.contrib[s][k, x[k]] for k in range(N))

    def gibbs(self, L, s, n_sweep=600, burn=150, seed=0, fixed=None, x0=None):
        """Samples of x (n, 6) for stage s; `fixed` = {k: c} holds sectors fixed (Chib runs).
        Also returns the averaged conditional probability of each sector's candidates."""
        rng = np.random.default_rng(seed)
        fixed = fixed or {}
        x = np.zeros(N, int) if x0 is None else x0.copy()
        for k, c in fixed.items():
            x[k] = c
        P = self.predict(s, x)
        out = []
        cond_avg = np.zeros((N, N_CAND))
        for it in range(n_sweep):
            for k in range(N):
                if k in fixed:
                    continue
                Rk = L - (P - self.contrib[s][k, x[k]])
                lp = self._cond(s, k, Rk)
                p = np.exp(lp - lp.max())
                p /= p.sum()
                c = rng.choice(N_CAND, p=p)
                P = P - self.contrib[s][k, x[k]] + self.contrib[s][k, c]
                x[k] = c
                if it >= burn:
                    cond_avg[k] += p
            if it >= burn:
                out.append(x.copy())
        return np.array(out), cond_avg / max(n_sweep - burn, 1)

    def map_search(self, L, s, n_restart=4, seed=0):
        """Iterated conditional modes from several starts -> best x."""
        rng = np.random.default_rng(seed)
        best, best_lp = None, -np.inf
        starts = [np.zeros(N, int), np.full(N, N_CAND // 2)] + [rng.integers(0, N_CAND, N) for _ in range(n_restart)]
        for x in starts:
            x = x.copy()
            for _ in range(20):
                old = x.copy()
                P = self.predict(s, x)
                for k in range(N):
                    Rk = L - (P - self.contrib[s][k, x[k]])
                    c = int(np.argmax(self._cond(s, k, Rk)))
                    P = P - self.contrib[s][k, x[k]] + self.contrib[s][k, c]
                    x[k] = c
                if (x == old).all():
                    break
            lp = self.log_post(L, s, x)
            if lp > best_lp:
                best, best_lp = x.copy(), lp
        return best, best_lp

    def log_post(self, L, s, x):
        if s == "Healthy":
            return -0.5 * self.chi2(L) / self.tau
        return -0.5 * self.chi2(L - self.predict(s, x)) / self.tau + float(self.lp_prior[x].sum())

    def evidence(self, L, s, n_sweep=600, burn=150, seed=0):
        """Chib's estimate of log p(y | s) and the posterior samples of the full run."""
        if s == "Healthy":
            return -0.5 * self.chi2(L) / self.tau, np.zeros((1, N), int), np.zeros(N, int)
        xs, _ = self.map_search(L, s, seed=seed)
        samples, cond = self.gibbs(L, s, n_sweep, burn, seed, x0=xs)
        logp_star = np.log(max(cond[0, xs[0]], 1e-300))
        for k in range(1, N):
            fixed = {j: xs[j] for j in range(k)}
            if k < N - 1:
                _, ck = self.gibbs(L, s, n_sweep // 2, burn // 2, seed + 101 * k, fixed=fixed, x0=xs)
                logp_star += np.log(max(ck[k, xs[k]], 1e-300))
            else:
                P = self.predict(s, xs)
                Rk = L - (P - self.contrib[s][k, xs[k]])
                lp = self._cond(s, k, Rk)
                logp_star += lp[xs[k]] - (lp.max() + np.log(np.exp(lp - lp.max()).sum()))
        logZ = self.log_post(L, s, xs) - logp_star
        return logZ, samples, xs

    def run(self, L, n_sweep=600, burn=150, seed=0, stages=STAGES, birge=True):
        """Posterior over stages and sector states. birge=True: if the best fit is worse than the
        noise model allows (chi2 per effective dof > 1), rerun with the likelihood tempered by that
        ratio (Birge scaling: the noise model is taken to be too optimistic by this factor). Uses
        only the target's own data. The raw (untempered) result is kept in res['_raw']."""
        if self.gain_free:
            L = self.project(L)
        self.tau = 1.0
        res = self._run_once(L, n_sweep, burn, seed, stages)
        g = self.gof(L, res)
        res["_gof_raw"] = g
        res["_tau"] = 1.0
        if birge and g > 1.0:
            raw = res
            self.tau = g
            res = self._run_once(L, n_sweep, burn, seed, stages)
            self.tau = 1.0
            res["_gof_raw"] = g
            res["_tau"] = g
            res["_raw"] = {s: dict(P=raw[s]["P"], logZ=raw[s]["logZ"], samples=raw[s]["samples"]) for s in stages}
        return res

    def gof(self, L, res):
        """chi2 per effective dof at the MAP state of the most probable stage."""
        best = max(STAGES, key=lambda s: res[s]["P"] if s in res else -1)
        P = self.predict(best, res[best]["map"]) if best != "Healthy" else 0.0
        return self.chi2(L - P) / (L.size * 2 / self.ell)

    def _run_once(self, L, n_sweep, burn, seed, stages):
        res = {}
        for i, s in enumerate(stages):
            logZ, smp, xs = self.evidence(L, s, n_sweep, burn, seed + 1000 * i)
            res[s] = dict(logZ=logZ, samples=smp, map=xs)
        lz = np.array([res[s]["logZ"] for s in stages]) + np.log(1.0 / len(stages))
        p = np.exp(lz - lz.max())
        p /= p.sum()
        for s, ps in zip(stages, p):
            res[s]["P"] = float(ps)
        return res


def sector_marginals(res):
    """-> P_stage (4,), marg (4 stages, 6 sectors, N_CAND): joint posterior P(s, x_k = c)."""
    Ps = np.array([res[s]["P"] for s in STAGES])
    marg = np.zeros((len(STAGES), N, N_CAND))
    for i, s in enumerate(STAGES):
        smp = res[s]["samples"]
        for k in range(N):
            cnt = np.bincount(smp[:, k], minlength=N_CAND).astype(float)
            marg[i, k] = Ps[i] * cnt / cnt.sum()
    return Ps, marg


def e_of(c):
    return np.where(np.asarray(c) == 0, 0.0, E_GRID[np.maximum(np.asarray(c) - 1, 0)])


def prior_marginals():
    """The prior alone (no data): P(s) = 1/4, P(unaffected | s != Healthy) = 1/2, e uniform."""
    Ps = np.full(len(STAGES), 1.0 / len(STAGES))
    marg = np.zeros((len(STAGES), N, N_CAND))
    marg[0, :, 0] = Ps[0]
    for i in range(1, len(STAGES)):
        marg[i, :, 0] = Ps[i] * 0.5
        marg[i, :, 1:] = Ps[i] * 0.5 / len(E_GRID)
    return Ps, marg


def summarize(res=None, Ps=None, marg=None):
    """Posterior summaries per sector: P(affected), mean / median / 5-95% of e (unaffected = 0),
    and the stage probabilities. Pass a run() result, or (Ps, marg) directly."""
    if res is not None:
        Ps, marg = sector_marginals(res)
    e_vals = e_of(np.arange(N_CAND))
    out = dict(P_stage={s: float(p) for s, p in zip(STAGES, Ps)}, sectors=[])
    for k in range(N):
        pk = marg[:, k].sum(0)                                      # over stages
        p_aff = float(marg[1:, k, 1:].sum())
        order = np.argsort(e_vals)
        cdf = np.cumsum(pk[order])
        q = lambda a: float(e_vals[order][np.searchsorted(cdf, a * cdf[-1])])  # noqa: E731
        out["sectors"].append(dict(P_affected=p_aff, e_mean=float((pk * e_vals).sum()), e_median=q(0.5),
                                   e_q05=q(0.05), e_q95=q(0.95)))
    return out
