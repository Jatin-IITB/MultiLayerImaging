# Running on the Praganak cluster

The analysis code is CPU-only (NumPy / SciPy / scikit-learn). Nothing here uses a GPU, so
request CPU nodes. On a laptop, a full `scripts/run_all.py` takes about 10 minutes and uses at
most 9 parallel workers (one per noise profile).

## Where the cluster actually helps

1. **New EM simulations.** Every current limitation comes from having one head and one
   simulation per stage (no generalisation, no mesh noise, no 3-class claim). More head
   variants, mesh repeats and MCI cases are the highest-value use of the cluster. First check
   whether an ANSYS Electronics (HFSS) or CST module and licence exist: `module avail 2>&1 | grep -i -E "ansys|hfss|cst"`.
2. **Prompt 04 field inversion.** Jacobians built from HFSS field exports (about 90k voxels × 21
   pairs × frequencies) need far more memory than the laptop has. Use `imaging.sbatch`-style
   jobs with more memory.
3. **Bigger statistics.** Raise `classify.n_train_draws` / `n_test_draws`, `metrics.n_realisations`
   and `classify.n_boot` in `config.yaml`. Doing this changes the logged results, so commit the
   config change first.

## First time

```bash
# on your laptop (PowerShell), from the folder that contains MultiLayerImaging_v1
scp -r "MultiLayerImaging_v1" <user>@praganak.iitb.ac.in:~/

# on the cluster login node
cd ~/MultiLayerImaging_v1
module avail 2>&1 | grep -i -E "python|anaconda|conda"   # pick a Python >= 3.11 module
bash cluster/setup_env.sh <python-module>                  # creates ~/venvs/mli, runs the tests
```

If bash complains about `\r` (Windows line endings), run
`sed -i 's/\r$//' cluster/*.sh cluster/*.sbatch` once.

## Running

```bash
export PY_MODULE=<python-module>        # same module as in setup (omit if none was needed)
sbatch cluster/run_all.sbatch           # QC + metrics + classifiers; appends to results/metrics.csv
sbatch cluster/run_all.sbatch --no-csv  # regenerate outputs without logging rows
sbatch cluster/imaging.sbatch           # imaging study
squeue -u $USER                         # status
tail -f cluster/logs/run_all_<jobid>.log
```

No partition is set, so jobs go to the default partition. Add `#SBATCH --partition=...` to the
`.sbatch` files once the manual confirms the name. Never run the pipeline on the login node.

## Keeping results consistent

- Every row in `results/metrics.csv` records the git hash. Commit on the cluster copy before
  a logged run, or the hash is marked `-dirty`.
- Do not run logged jobs on the laptop and the cluster at the same time. Both would append to
  their own `metrics.csv`, and the two files would diverge. Treat one copy as the master.
- To bring results back to the laptop (PowerShell):
  `scp -r <user>@praganak.iitb.ac.in:~/MultiLayerImaging_v1/results .\MultiLayerImaging_v1\`
