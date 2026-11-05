# Working in this repository (for coding agents and the people using them)

## Start here

1. Read [`README.md`](README.md) (layout, datasets) and [`docs/SETUP.md`](docs/SETUP.md) (environment, first read).
2. Read [`docs/PRODUCTION.md`](docs/PRODUCTION.md) only if ntuples have to be produced from MiniAOD.
3. Before editing, check where you are:
   ```bash
   git status -sb && git log --oneline -3
   ```
   - Work on `fullRun3`, or on a branch made from it.
   - Do not overwrite uncommitted changes you did not make.

## Two separate parts

- **Production** (`production/`) is CMSSW C++ and Python configs. It turns MiniAOD into the custom
  ntuples and needs a CMSSW area.
- **Downstream analysis** is plain Python, reading the existing ntuples over XRootD. It needs no
  CMSSW.

Most work uses the existing ntuples. Setting up does **not** require CRAB, ntuple production or a
full dataset scan.

## Working rules

- **Use the real configuration and commands** in this repository. If a step fails or something
  is missing, report the exact error. Do not invent setup steps, paths or workarounds.
- **Keep the blinding.** Exclude data with a 3µ mass in the τ signal window from downstream
  analysis, training tables and plots.
  - The current window is 1.752–1.802 GeV.
  - Leave the production configuration as it is: raw ntuples store all candidates, and blinding
    is applied downstream. Do not add a mass filter to production.
  - For classifier training, also exclude the AN Table 9 window of each η category.
  - Do not narrow or remove these windows. Monte Carlo is not blinded.
- **Read shared, write your own.** Existing ntuples are read from `/store/user/skuang/`.
  - New outputs go to your own space: `/work/users/<you>/` or `/store/user/<your-cern-username>/`.
  - Use your own CMS proxy and CRAB credentials. Never use or copy someone else's.
- **Never submit CRAB jobs** unless the person you are working for asks for that submission
  explicitly. Generating configs is fine.
- **Keep generated data out of Git:** ROOT files, caches, logs, CRAB task directories and models.
  `.gitignore` covers the common cases.
- **Provisional numbers are provisional.** Do not hardcode a study result as a correction or a
  systematic.
- **On Purdue AF:**
  - no Python environments under `/home`
  - never install into `/work/pixi/global`
  - workers read data over XRootD, not from `/eos`

## Starter request

Paste this into your agent if it does not read `AGENTS.md` automatically:

> Read AGENTS.md and docs/SETUP.md. Help me set up this checkout on Purdue AF and complete the small read check. Check what already exists before installing anything. Report what passed and any missing access or software; use docs/PRODUCTION.md only if I need ntuple production.
