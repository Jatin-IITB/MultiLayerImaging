# imaging2 handover

documentation baseline: 08a5ce3

## Role and boundaries
- **Role:** baseline + estimated-change slice imaging of the lobe phantom from the S-parameters, using a layered-stack
  surrogate and a Bayesian sector-state inversion.
- **Files written:** only `imaging2/` and `results/imaging2/`.
- **Files not touched:** data, frozen files, predictions, other sessions' files and `share_lobe_phantom_data/`.

## Where things are
- `LEDGER.md` / `LEDGER.csv`: every standing claim with its tier, every failed or withdrawn claim, every open
  limitation, and the report numbers with source and commit.
- `README.md`: the full narrative.
  - §8: the Test_B blind result and its score.
  - §9: RightOnly.
  - §11–11c: post hoc rounds.
  - `METHOD_surrogate_inversion.md`: the method.
- `sets.csv`: imaging2's set file. Every file, its role and kind; rotated nulls are kind = null, set lobe_nulls; none
  is in any training set.

## Commits that matter
| what | commit |
|---|---|
| images, leave-one-design-out, controls, noise study | 6db98f6 (re-run stamped ed7f2e3) |
| Test_B blind protocol (before the file existed) | 595e9cb; syntax fix before Test_B was read d83d1d5 |
| Test_B reconstruction (no truth) / score (PASS) | c0fafd6 / f88236c |
| RightOnly replication | 5a24a0f |
| post hoc after the Test_B truth (rot07, rot19) | b8eb7fa |
| rotated-null pre-registration (before rot31/rot43) | a295006 |
| pre-registered evaluation with all four rotated nulls; post hoc round 3 | 2f7f482 |
| variant drift test | 52c8149 |
| ledger (documentation baseline) | 08a5ce3 |

## Rerun
```
python -m imaging2.run_lobe2 --sweeps 600     # leave-one-design-out inversions + controls
python -m imaging2.make_figures               # figures + scores
python -m imaging2.blind run --file new_with_slices_Test_B.s6p --tag Test_B   # committed blind protocol
python -m imaging2.blind score --tag Test_B                                   # committed scorer (truth.json)
python -m imaging2.extras rightonly
python -m imaging2.posthoc all                # post hoc after the Test_B truth
python -m imaging2.nullrulers all             # pre-registered (a295006); uses every rotated null present
python -m imaging2.posthoc3 verify|meanref|coverage
python -m imaging2.variants_drift [xref]
```
Every run is deterministic (fixed seeds). Posterior marginals are committed in `cache/marg_*.npy`; the field cache
and the slice `.npz` files are rebuilt on demand.
