#!/usr/bin/env python
"""
Purdue copy of submit_CRAB.py -- GENERATES CRAB configs, never submits.

Differences from Felice's submit_CRAB.py (which is left untouched):
  1. It does NOT call `crab submit`. It only writes the config files and a
     submit.sh you can run by hand, one stream at a time.
  2. Era is a real parameter and you can pass several at once:
        --era C-v1 C-v2          (this is what "era C" means -- C has two
                                  PromptReco versions and each is its own dataset)
  3. Splitting is 'Automatic' with a target job runtime, instead of
     LumiBased/unitsPerJob=50.
  4. It prints a resolved summary table so you can eyeball GT / lumi mask /
     dataset / output path before anything goes to the grid.

Run it from the CMSSW area so the pset path CRAB records is the CMSSW one:
    cd $CMSSW_BASE/src/PhysicsTools/Tau3muNANO/crab_submission
    python submit_CRAB_purdue.py --year 2025 --era C-v1 C-v2 --channel control
"""

import argparse
import json
import os
import shutil
import subprocess

# CRABClient limits for Automatic splitting (Commands/submit.py:229-230).
AUTO_MIN_MIN = 180
AUTO_MAX_MIN = 2700

# The MC-side global tag hardcoded in Felice's test cfgs (the isMC=True branch).
MC_GT_PLACEHOLDER = "140X_mcRun3_2024_realistic_v26"

# Which Runs.json to read. Felice's original is git-tracked, so the Purdue
# MC entries live in Runs_purdue.json (ground rule 1). Overridable with --runs-json.
RUNS_JSON = "Runs.json"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--year", required=True)
    p.add_argument("--era", required=True, nargs="+",
                   help="One or more era keys exactly as they appear in Runs.json, "
                        "e.g. --era C-v1 C-v2")
    p.add_argument("--channel", required=True, choices=["signal", "control"])
    p.add_argument("--splitting", choices=["LumiBased", "Automatic"], default="LumiBased",
                   help="LumiBased (default): you choose lumis/job and can also set "
                        "maxJobRuntimeMin, so job count and output file size are "
                        "predictable before you submit. Automatic: CRAB picks the "
                        "splitting from probe jobs and maxJobRuntimeMin is forbidden.")
    p.add_argument("--units-per-job", type=int, default=400,
                   help="LumiBased: lumisections per job (era B used 50 -> 7:44 jobs; "
                        "400 -> roughly 60 min jobs). Automatic: TARGET JOB RUNTIME IN "
                        f"MINUTES, must be in [{AUTO_MIN_MIN}, {AUTO_MAX_MIN}].")
    p.add_argument("--max-job-runtime-min", type=int, default=300,
                   help="LumiBased only. Ignored (and omitted from the config) for "
                        "Automatic, which rejects it.")
    p.add_argument("--runs-json", default=None,
                   help="Path to the Runs.json to read. Defaults to Runs_purdue.json when "
                        "it exists (Purdue MC entries), else Felice's Runs.json.")
    p.add_argument("--isMC", action="store_true",
                   help="Treat --era values as MC_era keys from Runs.json instead of "
                        "data Eras. MC has no lumi mask and no 8-stream split, so this "
                        "writes exactly ONE CRAB config per sample.")
    return p.parse_args()


def build_one_era(year, era, channel, splitting, units_per_job, max_runtime):
    """Write <year>_era<era>_<channel>/ with a PatAndTree_cfg.py and 8 CRAB configs."""

    with open(RUNS_JSON) as f:
        data = json.load(f)[year]

    if era not in data["Eras"]:
        raise SystemExit(f"ERROR: era '{era}' not in Runs.json {year} eras {data['Eras']}")
    i_era = data["Eras"].index(era)

    globaltag = data["GTs"][i_era]
    golden_json = data["golden_json"][i_era]

    dataset_file = f"datasets/datasets_{year}_{era}.txt"
    if not os.path.exists(dataset_file):
        raise SystemExit(f"ERROR: missing {dataset_file} (regenerate with getDatset.py)")
    with open(dataset_file) as f:
        datasets = [line.strip() for line in f if line.strip()]
    if len(datasets) != 8:
        print(f"  WARNING: {dataset_file} has {len(datasets)} datasets, expected 8")

    channel_name = "Tau3mu" if channel == "signal" else "DsPhiPi"
    cfg_src = "test_Tau3Mu_cfg.py" if channel == "signal" else "test_DsPhiPi_cfg.py"
    dir_name = f"{year}_era{era}_{channel}"

    os.makedirs(dir_name, exist_ok=True)

    # --- the CMSSW pset: copy Felice's test cfg and stamp the global tag in ---
    pset = os.path.join(dir_name, "PatAndTree_cfg.py")
    shutil.copyfile(os.path.join("..", "test", cfg_src), pset)
    with open(pset) as f:
        text = f.read()
    # '140X_dataRun3_v4' is the data-GT placeholder in Felice's test cfg.
    if "140X_dataRun3_v4" not in text:
        raise SystemExit(f"ERROR: GT placeholder '140X_dataRun3_v4' not found in {cfg_src}; "
                         "the sed in the original submit_CRAB.py would have silently done nothing.")
    text = text.replace("140X_dataRun3_v4", globaltag)
    text = text.replace("options.register('isMC', True", "options.register('isMC', False")
    with open(pset, "w") as f:
        f.write(text)

    # Use the logical $PWD (not os.getcwd(), which resolves the CMSSW symlink to the
    # Tau3MuRun3_NANO path). Era B recorded the CMSSW_15_1_1 path; keep that convention.
    pset_abspath = os.path.join(os.environ.get("PWD", os.getcwd()), pset)

    # --- helper shell scripts (status/report/resubmit/submit) ---
    for script in ("report.sh", "status.sh", "resubmit.sh", "submit.sh"):
        dst = os.path.join(dir_name, script)
        shutil.copyfile(os.path.join("templates", script), dst)
        with open(dst) as f:
            s = f.read()
        s = s.replace("YEAR", year).replace("ERANAME", era).replace("CHANNELNAME", channel_name)
        with open(dst, "w") as f:
            f.write(s)

    # --- the 8 per-stream CRAB configs ---
    with open("templates/CRAB_template_purdue.py") as f:
        template = f.read()

    # maxJobRuntimeMin is only legal for non-Automatic splitting
    # (CRABClient Commands/submit.py:231-234 rejects the combination).
    if splitting == "Automatic":
        maxruntime_line = ("# maxJobRuntimeMin deliberately omitted: CRAB rejects it with "
                           "Automatic splitting.")
    else:
        maxruntime_line = f"config.JobType.maxJobRuntimeMin = {max_runtime}"

    rows = []
    for i, dataset in enumerate(datasets):
        cfg = (template
               .replace("CHANNELNAME", channel_name)
               .replace("YEAR", year)
               .replace("ERANAME", era)
               .replace("NUMBER", str(i))
               .replace("DATASET_NAME", dataset)
               .replace("FILE_TO_SUBMIT_PATH", pset_abspath)
               .replace("GOLDEN_JSON_PATH", golden_json)
               .replace("SPLITTING_MODE", splitting)
               .replace("UNITS_PER_JOB", str(units_per_job))
               .replace("MAXRUNTIME_LINE", maxruntime_line))
        out = os.path.join(dir_name, f"CRAB_stream_{i}.py")
        with open(out, "w") as f:
            f.write(cfg)
        rows.append((i, dataset, out))

    return dict(dir_name=dir_name, globaltag=globaltag, golden_json=golden_json,
                pset=pset_abspath, channel_name=channel_name, rows=rows,
                tag=f"Skim{channel_name}_{year}era{era}_stream<N>_Mini_v4",
                splitting=splitting, units_per_job=units_per_job,
                max_runtime=(None if splitting == "Automatic" else max_runtime))


def build_one_mc_era(year, mcera, channel, splitting, units_per_job, max_runtime):
    """Write <year>_era<mcera>_<channel>/ with a PatAndTree_cfg.py and ONE CRAB config.

    Differences from the data path (build_one_era):
      * dataset comes from Runs.json MC_datasets, not datasets/datasets_*.txt
      * no lumi mask -- MC has no golden JSON
      * one config per sample, not 8 -- MC is not split across parking streams
      * isMC stays True, and the *MC* global tag placeholder is the one stamped
    """

    with open(RUNS_JSON) as f:
        data = json.load(f)[year]

    if mcera not in data["MC_era"]:
        raise SystemExit(f"ERROR: MC era '{mcera}' not in Runs.json {year} "
                         f"MC_era {data['MC_era']}")
    i_era = data["MC_era"].index(mcera)

    for key in ("MC_GTs", "MC_datasets", "MC_input_type"):
        if i_era >= len(data.get(key, [])):
            raise SystemExit(
                f"ERROR: Runs.json {year} '{key}' has {len(data.get(key, []))} entries "
                f"but MC era '{mcera}' is at index {i_era}. Fill {key} in before submitting.")

    globaltag = data["MC_GTs"][i_era]
    dataset = data["MC_datasets"][i_era]
    input_dbs = data["MC_input_type"][i_era]

    channel_name = "Tau3mu" if channel == "signal" else "DsPhiPi"
    # 2026-11-02: signal MC uses the Purdue cfg, which stores bits for the full
    # 2025 L1 menu OR (13 seeds) and runs on all events; Felice's
    # test_Tau3Mu_cfg.py misses 2 TripleMu seeds and stops at 1000 events.
    cfg_src = "test_Tau3Mu_signal_crab_purdue_cfg.py" if channel == "signal" else "test_DsPhiPi_cfg.py"
    dir_name = f"{year}_era{mcera}_{channel}"

    os.makedirs(dir_name, exist_ok=True)

    # --- the CMSSW pset: stamp the MC global tag, leave isMC=True alone ---
    pset = os.path.join(dir_name, "PatAndTree_cfg.py")
    shutil.copyfile(os.path.join("..", "test", cfg_src), pset)
    with open(pset) as f:
        text = f.read()
    if MC_GT_PLACEHOLDER not in text:
        raise SystemExit(f"ERROR: MC GT placeholder '{MC_GT_PLACEHOLDER}' not found in "
                         f"{cfg_src}; refusing to write a pset with the wrong conditions.")
    text = text.replace(MC_GT_PLACEHOLDER, globaltag)
    with open(pset, "w") as f:
        f.write(text)

    pset_abspath = os.path.join(os.environ.get("PWD", os.getcwd()), pset)

    # --- the single CRAB config ---
    with open("templates/CRAB_template_MC_purdue.py") as f:
        template = f.read()

    if splitting == "Automatic":
        maxruntime_line = ("# maxJobRuntimeMin deliberately omitted: CRAB rejects it with "
                           "Automatic splitting.")
    else:
        maxruntime_line = f"config.JobType.maxJobRuntimeMin = {max_runtime}"

    cfg = (template
           .replace("CHANNELNAME", channel_name)
           .replace("YEAR", year)
           .replace("ERANAME", mcera)
           .replace("DATASET_NAME", dataset)
           .replace("INPUT_TYPE", input_dbs)
           .replace("FILE_TO_SUBMIT_PATH", pset_abspath)
           .replace("SPLITTING_MODE", splitting)
           .replace("UNITS_PER_JOB", str(units_per_job))
           .replace("MAXRUNTIME_LINE", maxruntime_line))
    out = os.path.join(dir_name, "CRAB_MC.py")
    with open(out, "w") as f:
        f.write(cfg)

    # --- helper scripts: one line each, not the 8-stream templates ---
    req = f"crab_Skim{channel_name}_{year}_{mcera}_Mini_v4"
    for script, verb in (("status.sh", "status"), ("resubmit.sh", "resubmit"),
                         ("report.sh", "report")):
        with open(os.path.join(dir_name, script), "w") as f:
            f.write(f"crab {verb} -d crab_projects/{req}\n")
    with open(os.path.join(dir_name, "submit.sh"), "w") as f:
        f.write("crab submit -c CRAB_MC.py\n")

    return dict(dir_name=dir_name, globaltag=globaltag, golden_json=None,
                pset=pset_abspath, channel_name=channel_name,
                rows=[(0, dataset, out)],
                tag=f"Skim{channel_name}_{year}_{mcera}_Mini_v4",
                splitting=splitting, units_per_job=units_per_job,
                max_runtime=(None if splitting == "Automatic" else max_runtime))


def main():
    global RUNS_JSON
    args = parse_args()

    if args.runs_json:
        RUNS_JSON = args.runs_json
    elif os.path.exists("Runs_purdue.json"):
        RUNS_JSON = "Runs_purdue.json"
    print(f"reading era/dataset config from: {RUNS_JSON}")

    if args.splitting == "Automatic" and not (AUTO_MIN_MIN <= args.units_per_job <= AUTO_MAX_MIN):
        raise SystemExit(f"ERROR: with Automatic splitting --units-per-job is a runtime in "
                         f"minutes and must be in [{AUTO_MIN_MIN}, {AUTO_MAX_MIN}].")

    for era in args.era:
        print(f"\n{'='*78}\n{args.year} era {era} -- channel {args.channel}\n{'='*78}")
        builder = build_one_mc_era if args.isMC else build_one_era
        info = builder(args.year, era, args.channel, args.splitting,
                       args.units_per_job, args.max_job_runtime_min)
        print(f"  output dir   : {info['dir_name']}/")
        print(f"  global tag   : {info['globaltag']}")
        print(f"  lumi mask    : {info['golden_json'] or '(none - MC)'}")
        print(f"  pset         : {info['pset']}")
        if info["splitting"] == "Automatic":
            print(f"  splitting    : Automatic, target {info['units_per_job']} min/job "
                  f"(job count decided by CRAB probe jobs)")
        else:
            print(f"  splitting    : LumiBased, {info['units_per_job']} lumis/job, "
                  f"maxJobRuntimeMin={info['max_runtime']}")
        print(f"  EOS output   : /eos/purdue/store/user/<your-cern-username>/<dataset>/{info['tag']}/")
        print("  streams:")
        for i, dataset, out in info["rows"]:
            print(f"    [{i}] {dataset}")
        print(f"\n  Wrote {len(info['rows'])} configs. NOTHING SUBMITTED.")
        one = os.path.basename(info["rows"][0][2])
        print(f"  To submit by hand:  cd {info['dir_name']} && crab submit -c {one}")

    print("\nNo `crab submit` was run by this script, by design.\n")


if __name__ == "__main__":
    main()
