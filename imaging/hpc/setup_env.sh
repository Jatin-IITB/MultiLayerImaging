#!/bin/bash
# One-time environment setup on Praganak (run on the LOGIN node; it only installs packages).
#   bash imaging/hpc/setup_env.sh
# Needs Python >= 3.11. Check the module name with `module avail python` / `module avail anaconda`
# (see https://hpcverse.iitb.ac.in/praganak-manuals) and edit PY_MODULE below if it differs.
set -euo pipefail

PY_MODULE="${PY_MODULE:-python}"          # <-- CHECK against `module avail`
VENV="${VENV:-$HOME/venvs/mli}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"

module load "$PY_MODULE"
python3 --version
python3 -m venv "$VENV"
source "$VENV/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r "$REPO/imaging/hpc/requirements.txt"
# If the login node has no internet, use `pip download` on the laptop and copy the wheels over,
# or use the cluster's anaconda module instead of a venv.

cd "$REPO"
python -m pytest imaging/tests -q -p no:cacheprovider    # ~30 s sanity check (19 tests)
echo "Environment ready: source $VENV/bin/activate"
