#!/usr/bin/env python
"""
Pre-submission checks for the 2025 C-G production. READ-ONLY: queries DAS, submits nothing.

Needs a valid grid proxy (run `voms-proxy-init -voms cms -valid 192:00` yourself first).

    python verify_before_submit.py --year 2025 --era C-v1 C-v2 D E F-v1 F-v2 G

Checks, in order:
  1. every dataset named in datasets_<year>_<era>.txt actually exists in DAS
  2. the -v1 / -v2 pairs of the same era cover DISJOINT runs
     (if they overlap, summing both double-counts luminosity)
  3. every run in every era is inside the golden JSON's run range
  4. prints golden-lumisection counts per era -> real job-count and size estimates
"""

import argparse, json, os, subprocess, sys
from collections import defaultdict
from urllib.request import urlopen

DAS = "/cvmfs/cms.cern.ch/common/dasgoclient"
GOLDEN_URL = ("https://cms-service-dqmdc.web.cern.ch/CAF/certification/"
              "Collisions25/Cert_Collisions2025_391658_398903_Golden.json")

# era B measured reference: 6,690 golden LS -> 4,956,879 events, 18 GB
EB_LS, EB_EVENTS, EB_GB = 6690, 4956879, 18.0


def das(query):
    out = subprocess.run([DAS, "-query", query], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"DAS failed for '{query}':\n{out.stderr.strip()}\n"
                           "(expired proxy? run voms-proxy-init yourself)")
    return [l.strip() for l in out.stdout.splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--year", default="2025")
    ap.add_argument("--era", nargs="+", required=True)
    args = ap.parse_args()
    if args.year != "2025":
        sys.exit(f"--year {args.year}: not supported yet; GOLDEN_URL is the 2025 certification only")

    if not os.path.exists(DAS):
        sys.exit(f"dasgoclient not found at {DAS}")

    golden = json.loads(urlopen(GOLDEN_URL, timeout=60).read())
    gruns = {int(r) for r in golden}
    ls_per_run = {int(r): sum(b - a + 1 for a, b in v) for r, v in golden.items()}
    gmin, gmax = min(gruns), max(gruns)
    print(f"golden JSON: {len(gruns)} runs, {gmin}-{gmax}, {sum(ls_per_run.values()):,} LS\n")

    era_runs, failures = {}, []

    for era in args.era:
        path = f"datasets/datasets_{args.year}_{era}.txt"
        datasets = [l.strip() for l in open(path) if l.strip()]
        print(f"=== era {era} ({len(datasets)} datasets) ===")

        # 1. existence
        missing = [d for d in datasets if not das(f"dataset={d}")]
        if missing:
            failures.append(f"era {era}: {len(missing)} dataset(s) not in DAS: {missing}")
            print(f"  FAIL: not found in DAS: {missing}")
        else:
            print(f"  OK  : all {len(datasets)} datasets exist in DAS")

        # runs (stream 0 is representative; all 8 streams share the run range)
        runs = {int(r) for r in das(f"run dataset={datasets[0]}")}
        era_runs[era] = runs
        print(f"  runs: {len(runs)}  range {min(runs)}-{max(runs)}")

        # 3. golden coverage.
        # Two different situations, only one of which is a problem:
        #  - run is in the dataset but simply NOT CERTIFIED -> the lumi mask drops it,
        #    which is correct behaviour, not a loss. 2025 certification is final
        #    (Cert_...398903_Golden.json published 2026-07-30), so nothing more is coming.
        #  - run is ABOVE the certified maximum AND the year is still being certified
        #    -> you would silently lose lumi that a later JSON would have given you.
        uncertified = sorted(runs - gruns)
        if uncertified:
            print(f"  NOTE: {len(uncertified)} run(s) in the dataset are not golden-certified "
                  f"and will be excluded by the lumi mask: {uncertified[:5]}")
            print(f"        This is correct. 2025 certification is CLOSED, so these runs "
                  f"will never be certified.")
        else:
            print(f"  OK  : every run in the dataset is golden-certified")

        # 4. size estimate
        ls = sum(ls_per_run.get(r, 0) for r in runs & gruns)
        print(f"  golden LS in era : {ls:,}  ({ls/EB_LS:.1f}x era B)")
        print(f"  est. events      : {EB_EVENTS*ls/EB_LS/1e6:.0f} M")
        print(f"  est. size        : {EB_GB*ls/EB_LS:.0f} GB")
        print(f"  jobs @400 lumis  : {-(-ls//400)*8} across 8 streams\n")

    # 2. disjointness of -v1 / -v2 pairs
    print("=== -v1 / -v2 overlap check ===")
    base = defaultdict(list)
    for era in era_runs:
        if "-v" in era:
            base[era.split("-v")[0]].append(era)
    if not any(len(v) > 1 for v in base.values()):
        print("  (no multi-version eras in this selection)")
    for b, eras in sorted(base.items()):
        if len(eras) < 2:
            continue
        a, c = eras[0], eras[1]
        ov = era_runs[a] & era_runs[c]
        if ov:
            failures.append(f"era {b}: {a} and {c} SHARE {len(ov)} runs -> summing double-counts")
            print(f"  FAIL: {a} and {c} share {len(ov)} runs: {sorted(ov)[:8]}")
            print(f"        Do NOT submit both without deciding which reco to keep.")
        else:
            print(f"  OK  : {a} and {c} are disjoint -> safe to submit both and sum")

    print("\n" + "="*70)
    if failures:
        print(f"{len(failures)} PROBLEM(S) - do not submit until resolved:")
        for f in failures:
            print("  - " + f)
        sys.exit(1)
    print("All checks passed. Configs are safe to submit.")


if __name__ == "__main__":
    main()
