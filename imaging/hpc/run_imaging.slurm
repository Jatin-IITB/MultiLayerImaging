#!/bin/bash
# Full Track A imaging study on one compute node. Submit from the repo root:
#   sbatch imaging/hpc/run_imaging.slurm
# The code is CPU-bound NumPy (no GPU use). Cores matter: the I3 fits run in parallel with
# --jobs $SLURM_CPUS_PER_TASK. I1/I2 use one process (NumPy BLAS threads).
#SBATCH --job-name=mli-imaging
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=imaging_%j.log
#SBATCH --partition=CHANGE_ME           # <-- a CPU partition name from the Praganak manual
set -euo pipefail

PY_MODULE="${PY_MODULE:-python}"        # <-- same module as in setup_env.sh
VENV="${VENV:-$HOME/venvs/mli}"

module load "$PY_MODULE"
source "$VENV/bin/activate"
cd "$SLURM_SUBMIT_DIR"

# main process may use all cores for BLAS; joblib limits BLAS threads inside its workers
export OMP_NUM_THREADS="$SLURM_CPUS_PER_TASK"
export MPLBACKEND=Agg

echo "node $(hostname), $SLURM_CPUS_PER_TASK cores, start $(date)"
# --no-csv: metrics rows are appended on the laptop copy (see imaging/hpc/README.md)
python -u imaging/run_imaging.py --jobs "$SLURM_CPUS_PER_TASK" --no-csv "$@"
echo "done $(date)"
