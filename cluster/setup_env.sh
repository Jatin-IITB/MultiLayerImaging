#!/bin/bash
# One-time environment setup on the Praganak LOGIN node (light work only: creating a venv is fine).
#
#   bash cluster/setup_env.sh [module-name]
#
# module-name: the Python/Anaconda module to load, as listed by `module avail` (e.g. python/3.12).
# Without it, the python3 already on PATH is used. Python >= 3.11 is required (numpy 2.3, pandas 3).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ $# -ge 1 ]; then
    module load "$1"
fi

PY=${PYTHON:-python3}
if ! "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "ERROR: $("$PY" --version 2>&1) is too old; need Python >= 3.11." >&2
    echo "Run 'module avail' and pass a newer python/anaconda module, or install Miniforge in \$HOME." >&2
    exit 1
fi

VENV=${VENV:-$HOME/venvs/mli}
"$PY" -m venv "$VENV"
source "$VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Environment ready: $VENV ($(python --version))"
echo "Quick check (login node, ~1 min):"
python -m pytest -q tests
