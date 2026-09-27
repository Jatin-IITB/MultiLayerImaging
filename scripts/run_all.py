"""One command to regenerate everything from data/sims.csv:

    python scripts/run_all.py [--skip-qc] [--skip-02] [--no-csv] [--include-moderate]

Runs 00_qc (raw integrity), 02_metrics (separability/robustness) and 03_classify (gate,
classifiers, thresholds) in order, with the same config.yaml. Commit code before running:
metrics.csv rows record the git hash (suffix -dirty if code/config differ from HEAD).
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script, extra):
    print(f"\n=== {script} {' '.join(extra)}", flush=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / script), *extra], check=True, cwd=ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-qc", action="store_true")
    ap.add_argument("--skip-02", action="store_true")
    ap.add_argument("--no-csv", action="store_true")
    ap.add_argument("--include-moderate", action="store_true")
    a = ap.parse_args()
    common = (["--no-csv"] if a.no_csv else []) + (["--include-moderate"] if a.include_moderate else [])
    if not a.skip_qc:
        run("00_qc.py", ["--include-moderate"])
    if not a.skip_02:
        run("02_metrics.py", common)
    run("03_classify.py", common)


if __name__ == "__main__":
    main()
