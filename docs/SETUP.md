# Setup on Purdue AF: from checkout to a first data read

This guide assumes a **Purdue Analysis Facility** session (JupyterHub, `/work` and `/eos/purdue` mounted). On another
machine the paths, interpreter and mounts below do not apply: identify your own environment first.

If your coding agent does not read `AGENTS.md` by itself, paste the starter request from [`AGENTS.md`](../AGENTS.md).

## 1. Prerequisites

- **A Purdue AF session.** Find your username with `whoami`; it is also `$NB_USER`.
- **A CERN account in the CMS VO with a grid certificate in `~/.globus/`.** Your CERN username
  is usually different from your Purdue one.
- **A GitHub account,** only if you will push. Reading the repository needs none.

## 2. Get the code

Keep code and outputs on `/work`, not `/home`: `/home` is small and invisible to workers.

```bash
mkdir -p /work/users/$(whoami) && cd /work/users/$(whoami)
git clone -b fullRun3 https://github.com/JanFSchulte/Tau3MuAnalysisStudies.git
cd Tau3MuAnalysisStudies
git status -sb          # expect: ## fullRun3...origin/fullRun3
```

## 3. Python

- **Interpreter:** use the AF's shared environment. There is nothing to install for this guide.
  ```bash
  PY=/work/pixi/global/.pixi/envs/default/bin/python
  $PY -c "import uproot, awkward, numpy, pandas, xgboost; print(uproot.__version__, awkward.__version__, xgboost.__version__)"
  ```
  - Expected output: three version numbers. Tested: `5.7.4 2.9.1 3.2.0`.
  - Bare `python` / `python3` in a terminal is the image's base environment, which is not meant
    for analysis.
- **Jupyter kernel:** in a notebook, choose **"Python (pixi global)"**.
- **Do not install into `/work/pixi/global`;** it is shared. If you need extra packages, make your
  own pixi project under `/work/users/$(whoami)/` (`pixi init`, `pixi add ...`) and run with
  `pixi run python` from that directory.

## 4. Where data lives (read shared, write your own)

The existing ntuples were produced by CERN user `skuang`. Read them from that namespace, exactly as written.

| Action | Where |
|---|---|
| Browse in a notebook or terminal (read-only) | `/eos/purdue/store/user/skuang/` |
| Read in code, notebooks and jobs | `root://eos.cms.rcac.purdue.edu//store/user/skuang/...` |
| Write analysis outputs | `/work/users/$(whoami)/...` |
| Write grid/CRAB outputs | `/store/user/<your-cern-username>/` on `T2_US_Purdue`, never `skuang`'s |

The list of samples, their production tags and their status is kept in one place: the data-access table in
[`README.md`](../README.md#data-access-at-purdue).

Jobs on Dask or Slurm workers must read over XRootD (`root://...`), not through `/eos`, which they cannot see reliably.

## 5. CMS proxy

Authentication requirements vary by endpoint: use your own valid CMS proxy for protected reads (for example the
global redirector `root://cms-xrd-global.cern.ch/`) and for anything CRAB-related, and test access with the read
check below. Make the proxy from **your own** certificate:

```bash
voms-proxy-info -timeleft        # seconds left; 0 or an error means none
voms-proxy-init -voms cms -rfc   # asks for your certificate pass phrase
```

Run `voms-proxy-init` yourself in an interactive terminal; it needs your pass phrase. For Dask workers, create it
where they can read it and pass `X509_USER_PROXY` to them; the default `/tmp` location is invisible to workers.

## 6. Small read check

```bash
$PY - <<'EOF'
import uproot
url = ("root://eos.cms.rcac.purdue.edu//store/user/skuang/DstoPhiPi-Phito2Mu_Fil-Mu_TuneCP5_13p6TeV_pythia8-evtgen/"
       "SkimDsPhiPi_2024_MC_DsPhiPi_Mini_v4/260903_165448/0000/dsphipi_output_MC_1.root")
with uproot.open(url) as f:
    t = f["Events"]
    print("entries", t.num_entries, "branches", len(t.keys()))
    print("candidates per event:", t["nCand2MuTrk"].array(entry_stop=5).tolist())
EOF
```

Expected output, tested on 2026-11-04 from `skuang`'s account:

```text
entries 2345 branches 201
candidates per event: [2, 1, 3, 2, 3]
```

This is a Ds→φπ control-channel MC file, so nothing blinded is involved. A successful read from one account does not
prove another account can read `/store/user/skuang/`. **Your own run of this check is the access test.**

## 7. If something fails

| Symptom | Likely cause and fix |
|---|---|
| `[FATAL] Auth failed`, `no valid proxy`, `Permission denied` on a `root://` URL | No or expired proxy: run step 5. If it persists with a valid proxy, you may lack read access to that path. Report the exact URL and error rather than trying other paths. |
| `ModuleNotFoundError: uproot` (or similar) | Wrong interpreter or kernel: use `$PY` from step 3, or the "Python (pixi global)" kernel. |
| `File did not open properly`, `Operation expired`, `No such file` | The file or server is unavailable, or the path is mistyped. Check the path with `ls /eos/purdue/store/user/skuang/...`. If it exists, retry later; transient XRootD errors do happen. |
| `pixi` refuses to run in your directory | Pixi projects are not allowed under `/home`; move the project to `/work/users/$(whoami)/`. |

## 8. What is ready, and what is pending

- **Ready:**
  - reading the existing ntuples
  - the dataset table in the README
  - CMSSW production code and a local test (optional, see [`PRODUCTION.md`](PRODUCTION.md))
- **Pending:**
  - a setup script for the CMSSW part
  - the downstream analysis package (selections, Ds fit, trigger studies)
  - the classifier training pipeline
  - verified cross-account access
