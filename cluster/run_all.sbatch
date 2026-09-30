#!/bin/bash
# Full Track A pipeline (QC -> 02 metrics -> 03 classifiers/thresholds) on one compute node.
#
#   sbatch cluster/run_all.sbatch                 # logs rows to results/metrics.csv
#   sbatch cluster/run_all.sbatch --no-csv        # regenerate outputs only
#   sbatch cluster/run_all.sbatch --skip-qc --skip-02
#
# Arguments after the script name are passed to scripts/run_all.py.
# Partition: none is set, so the cluster default is used. Add
#   #SBATCH --partition=<name>
# below once the Praganak manual confirms the CPU partition name.
#SBATCH --job-name=mli-trackA
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=cluster/logs/run_all_%j.log

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")/..}"
mkdir -p cluster/logs
[ -n "${PY_MODULE:-}" ] && module load "$PY_MODULE"
source "${VENV:-$HOME/venvs/mli}/bin/activate"

# One BLAS thread per worker: parallelism comes from joblib (one worker per noise profile, 9 max).
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

echo "node $(hostname), ${SLURM_CPUS_PER_TASK:-?} cpus, commit $(git rev-parse --short HEAD 2>/dev/null || echo no-git)"
python -m pytest -q tests
python scripts/run_all.py "$@"
