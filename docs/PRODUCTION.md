# Production: building the ntuplizer and making ntuples (optional)

You only need this if you are producing **new** ntuples from MiniAOD. To analyse the existing ones, [`SETUP.md`](SETUP.md)
is enough.

Tested on Purdue AF (el8 container) on 2026-11-04, from a clean clone of `fullRun3` @ `f04b635`. The tested items are
listed at the end.

## 1. CMSSW area

The code lives in `production/PhysicsTools/Tau3muNANO/`, with its CMSSW-relative path kept. It is copied into a
CMSSW area under `src/PhysicsTools/`. The release used for the 2025 data and 2024 MC ntuples is `CMSSW_15_1_1`.

Each block below runs in a subshell `( ... )` with `set -e`. It **stops at the first failure** without closing your
terminal, and the error stays visible. `REPO` is your clone and `AREA` is where the CMSSW area goes; change them if
yours differ. `NJ` is the number of build jobs: keep it at or below the CPUs your session reserved.

```bash
( set -eo pipefail
  REPO=/work/users/$(whoami)/Tau3MuAnalysisStudies; AREA=/work/users/$(whoami); NJ=4
  source /cvmfs/cms.cern.ch/cmsset_default.sh
  export SCRAM_ARCH=el8_amd64_gcc12
  cd "$AREA"
  [ ! -e CMSSW_15_1_1 ] || { echo "CMSSW_15_1_1 already exists in $AREA: use the refresh block below"; exit 1; }
  scramv1 project CMSSW CMSSW_15_1_1
  cd CMSSW_15_1_1/src
  rt=$(scramv1 runtime -sh)            # this is cmsenv; a failure stops the block here
  eval "$rt"
  [ "$(realpath "$CMSSW_BASE")" = "$(realpath "$AREA/CMSSW_15_1_1")" ] || { echo "wrong CMSSW_BASE: $CMSSW_BASE"; exit 1; }
  mkdir -p PhysicsTools
  cp -r "$REPO/production/PhysicsTools/Tau3muNANO" PhysicsTools/
  scram b -j "$NJ"
  ls -l "$CMSSW_BASE/lib/$SCRAM_ARCH/pluginPhysicsToolsTau3muNANOPlugins.so"
  echo "BUILD OK in $CMSSW_BASE" )
```

The block counts as successful only if it ends with `BUILD OK`. The repeated `***WARNING: Multiple usage of ...` lines
come from the upstream `plugins/BuildFile.xml` and are harmless. `scram b` must run from `$CMSSW_BASE/src`, which the
block does.

**After you pull new code**, refresh into a *fresh* package directory. Copying over the old one would keep files
that were deleted in Git. The old copy is moved out of `src/`, with any local edits, so you can check it before
deleting it:

```bash
( set -eo pipefail
  REPO=/work/users/$(whoami)/Tau3MuAnalysisStudies; CB=/work/users/$(whoami)/CMSSW_15_1_1; NJ=4
  source /cvmfs/cms.cern.ch/cmsset_default.sh; export SCRAM_ARCH=el8_amd64_gcc12
  cd "$CB/src"; rt=$(scramv1 runtime -sh); eval "$rt"
  mv PhysicsTools/Tau3muNANO "$CB/Tau3muNANO.old_$(date +%Y%m%d_%H%M%S)"
  cp -r "$REPO/production/PhysicsTools/Tau3muNANO" PhysicsTools/
  scram b clean && scram b -j "$NJ"
  ls -l "$CMSSW_BASE/lib/$SCRAM_ARCH/pluginPhysicsToolsTau3muNANOPlugins.so"
  echo "REBUILD OK" )
```

For later commands, enter the environment in your own shell with
`cd /work/users/$(whoami)/CMSSW_15_1_1/src && source /cvmfs/cms.cern.ch/cmsset_default.sh && export SCRAM_ARCH=el8_amd64_gcc12 && eval "$(scramv1 runtime -sh)"`
and check `echo $CMSSW_BASE`.

## 2. Local test on 1000 MC events

From `$CMSSW_BASE/src`, with a valid proxy (see [`SETUP.md`](SETUP.md#5-cms-proxy)); the input is read through the
global redirector:

```bash
cmsRun PhysicsTools/Tau3muNANO/test/test_Tau3Mu_signal_purdue_cfg.py isMC=True
```

- **What it runs on:** 1000 Ds→τ→3µ events from `RunIII2024Summer24MiniAODv6` (150X).
- **What it writes:** `tau3mu_output_MC_signal_Ds.root` in the current directory. Only events
  with at least one τ→3µ candidate are kept, so expect far fewer than 1000.
- **Check the output** with the analysis Python:
  ```bash
  /work/pixi/global/.pixi/envs/default/bin/python -c "import uproot; t=uproot.open('tau3mu_output_MC_signal_Ds.root')['Events']; print(t.num_entries, len(t.keys()))"
  ```
  An earlier run of this config wrote 144 events with 221 branches.
- **Startup:** about 15 minutes in one local-input test; timings vary.

`test_Tau3Mu_cfg.py` and `test_DsPhiPi_cfg.py` are the templates CRAB uses for data. Their built-in input file is MC,
so they are not ready-to-run local data tests: a data test needs a data input file **and** the matching GlobalTag set
explicitly.

## 3. CRAB configs (generation is not submission)

Run the generator from the staged package in the CMSSW area. The generated configs record that path as `psetName`:

```bash
cd $CMSSW_BASE/src/PhysicsTools/Tau3muNANO/crab_submission
python3 submit_CRAB_purdue.py --year 2025 --era C-v1 --channel control           # data: 8 stream configs
python3 submit_CRAB_purdue.py --year 2024 --era MC_Ds_tau3mu --channel signal --isMC   # MC: 1 config
```

- **Where the eras and samples come from:** `Runs_purdue.json` (data eras such as `C-v1`; MC
  keys such as `MC_Ds_tau3mu`, `MC_DsPhiPi`).
- **What it writes:** one directory per era and channel (e.g. `2025_eraC-v1_control/`), holding
  `CRAB_stream_{0..7}.py` for data or `CRAB_MC.py` for MC, plus `submit.sh`, `status.sh`,
  `resubmit.sh` and `report.sh`. **Nothing is submitted.**
- **Outputs** go to `T2_US_Purdue` under the submitting user's own `/store/user/<cern-username>/`
  (CRAB's default).
- **Before submitting** data, check the datasets against DAS and the golden JSON (2025 only):
  ```bash
  python3 verify_before_submit.py --year 2025 --era C-v1
  ```

**Submitting** is a separate, deliberate step. It uses grid resources and writes to your EOS namespace:

```bash
cd 2025_eraC-v1_control
crab submit -c CRAB_stream_0.py     # one stream
# source submit.sh                  # for data this submits ALL EIGHT streams
```

- **Delegation:** CRAB needs a VOMS proxy and a myproxy delegation under your own credentials.
  The client creates the delegation during `crab submit` and asks for your pass phrase, so run it
  in an interactive terminal.
- **Not yet validated for other users:** CRAB submission from accounts other than the original
  producer.

## Tested here, and pending

- **Tested (2026-11-04, clean clone @ `f04b635`, account `kuang14`):**
  - `scramv1 project` and the build block (tested with 8 and with 4 jobs): exit 0, plugin library present.
  - Data and MC CRAB config generation: the configs parse, and nothing was submitted.
  - A 1000-event `cmsRun` of `test_Tau3Mu_signal_purdue_cfg.py` on a **local** Bd→τ→3µ MiniAOD
    (`/store/mc/RunIII2024Summer24MiniAOD/...`, 140X), because no proxy was available at the time.
    Result: exit 0, 140 events written with 221 branches.
- **Pending:**
  - a setup script replacing section 1
  - re-running section 2 exactly as written, with the redirector input and a proxy
  - CRAB submission by a second user
