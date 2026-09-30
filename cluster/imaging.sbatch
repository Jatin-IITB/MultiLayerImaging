#!/bin/bash
# Imaging / localisation study (imaging/run_imaging.py) on one compute node.
#
#   sbatch cluster/imaging.sbatch
#
# Partition: cluster default unless you add  #SBATCH --partition=<name>  below.
#SBATCH --job-name=mli-imaging
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=cluster/logs/imaging_%j.log

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$(dirname "$0")/..}"
mkdir -p cluster/logs
[ -n "${PY_MODULE:-}" ] && module load "$PY_MODULE"
source "${VENV:-$HOME/venvs/mli}/bin/activate"

# The voxel inversions are dense linear algebra: let BLAS use the allocated cores.
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-16}
export OPENBLAS_NUM_THREADS=$OMP_NUM_THREADS MKL_NUM_THREADS=$OMP_NUM_THREADS

echo "node $(hostname), ${SLURM_CPUS_PER_TASK:-?} cpus, commit $(git rev-parse --short HEAD 2>/dev/null || echo no-git)"
python -m pytest -q imaging/tests
python imaging/run_imaging.py
