# Running the imaging study on Praganak (IIT Bombay HPC)

What the cluster helps with: the code is CPU-bound NumPy/SciPy, so a GPU does not help. Cores do.
The I3 fits (~280 independent Levenberg–Marquardt fits, ~5 h on the laptop) run in parallel
with `--jobs N` (identical results to the serial run, verified). I1 (~50 min) and I2 (~12 min)
run in one process.

Log-in, 2FA and the password change (`passwd`) are yours to do. Check partition names, core
counts and the Python/Anaconda module in the manual: https://hpcverse.iitb.ac.in/praganak-manuals
(it probably needs the IITB network or VPN).

## 1. Copy the repo (from the laptop, PowerShell)

The repo is ~84 MB. A fresh run does not need the local cache:

```bash
scp -r "C:\Users\Asus\OneDrive - Indian Institute of Technology Bombay\Desktop\MultiLayerImaging_v1" 22b3967@praganak.iitb.ac.in:~/
```

(or `git clone` on the cluster if the repo is pushed to a remote).

## 2. One-time environment (on the cluster, login node)

```bash
cd ~/MultiLayerImaging_v1
PY_MODULE=<python-or-anaconda-module> bash imaging/hpc/setup_env.sh
```

It creates `~/venvs/mli`, installs `imaging/hpc/requirements.txt` and runs the 19 unit tests.

## 3. Submit

Edit `--partition=CHANGE_ME` (and `--cpus-per-task` if the nodes are smaller or larger) in
`imaging/hpc/run_imaging.slurm`, then:

```bash
sbatch imaging/hpc/run_imaging.slurm            # full study
sbatch imaging/hpc/run_imaging.slurm --only i3  # just the I3 fits (plus validation)
squeue -u $USER
tail -f imaging_<jobid>.log
```

I3 checkpoints every fit to `results/imaging/cache/`, so if a job hits its time limit,
resubmitting the same command resumes it.

## 4. Bring results back — only `results/imaging/`

Two Claude sessions share the laptop folder. **Never copy the whole repo back**: that would
overwrite the other session's files. Copy only the imaging results, from the laptop:

```bash
scp -r 22b3967@praganak.iitb.ac.in:~/MultiLayerImaging_v1/results/imaging "C:\Users\Asus\OneDrive - Indian Institute of Technology Bombay\Desktop\MultiLayerImaging_v1\results\"
```

Then, on the laptop, write the metrics rows from the cached results and commit:

```bash
python imaging/run_imaging.py --reuse
git add imaging results/imaging
git commit -m "[imaging] ..."
```

The job runs with `--no-csv`, so `metrics_imaging.csv` rows are appended only once, on the
laptop, with the laptop's git hash.
