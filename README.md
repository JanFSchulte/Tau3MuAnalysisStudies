# Tau3MuAnalysisStudies: CMS τ→3µ (heavy-flavour) Run 3 analysis, Purdue

This repository covers the Purdue workflow for the Run 3 τ→3µ search (AN-2024/058), extended to 2025 data:

- producing ntuples from MiniAOD
- reading them at Purdue
- running the signal (τ→3µ) and control (Ds→φ(µµ)π) selections
- the normalisation and trigger studies
- the background classifier

> **Status (branch `fullRun3`):** being assembled. Sections marked *TODO* are not ready yet. Results from
> this branch are provisional until stated otherwise.

## Repository layout

| Path | Contents |
|---|---|
| `production/PhysicsTools/Tau3muNANO/` | CMSSW ntuplizer (builders, configs) and the Purdue CRAB helpers. Origin: see `upstream_sources.json` |
| `HLT/` | HLT-path efficiency fits (AN §12.4), J. Schulte |
| `Momentum/` | Muon momentum scale/resolution from Ds→φπ (AN §12.1), J. Schulte |
| `sPlot/` | sPlot studies for the classifier data/MC comparison, J. Schulte |
| `upstream_sources.json` | Where copied code came from (repository, revision, files, local changes) |
| `AGENTS.md`, `docs/` | Setup and production guides, for people and coding agents |

*TODO:* `src/tau3mu/` (selections, control fits, systematics, ML), `config/`, `tests/`.

## Quick start

- **New here, or working with a coding agent?** Read [`AGENTS.md`](AGENTS.md) and [`docs/SETUP.md`](docs/SETUP.md):
  checkout, Python environment, proxy, and a first data read on Purdue AF.
- **Producing ntuples** (optional): see [`docs/PRODUCTION.md`](docs/PRODUCTION.md). It covers the CMSSW build, a
  local test, and CRAB config generation and submission.

There are two separate environments:
- **Production** uses a CMSSW release area (`CMSSW_15_1_1`).
- **Analysis** uses plain Python: on the AF, `/work/pixi/global/.pixi/envs/default/bin/python`. It needs no CMSSW.

## Data access at Purdue

The existing ntuples were produced by the CERN/Grid user **`skuang`** (Purdue user `kuang14`). Read them from
that namespace; do **not** replace `skuang` with your own username. Write new outputs only to your own namespace.

| What | Location |
|---|---|
| Site | `T2_US_Purdue` |
| Namespace | `/store/user/skuang/` |
| Browse (AF notebook, read-only) | `/eos/purdue/store/user/skuang/` |
| Read (XRootD) | `root://eos.cms.rcac.purdue.edu//store/user/skuang/...` |

Directory patterns. A wildcard is only a discovery aid: each pattern still has to be resolved into an explicit file
manifest, because several timestamps may exist.

```text
/store/user/skuang/ParkingDoubleMuonLowMass{stream}/SkimTau3mu_2025era{era}_stream{stream}_Mini_v4/{timestamp}/{chunk}/tau3mu_output_Data_*.root
/store/user/skuang/ParkingDoubleMuonLowMass{stream}/SkimDsPhiPi_2025era{era}_stream{stream}_Mini_v4/{timestamp}/{chunk}/dsphipi_output_Data_*.root
/store/user/skuang/DstoPhiPi-Phito2Mu_Fil-Mu_TuneCP5_13p6TeV_pythia8-evtgen/SkimDsPhiPi_2024_MC_DsPhiPi_Mini_v4/{timestamp}/{chunk}/dsphipi_output_MC_*.root
/store/user/skuang/{Ds,Bd,Bu}toTau-Tauto3Mu_Fil-3Mu_TuneCP5_13p6TeV_pythia8-evtgen/SkimTau3mu_2024_MC_{Ds,Bd,Bu}_tau3mu_Mini_v4/{timestamp}/{chunk}/tau3mu_output_MC_*.root
```

| Channel | Data/MC | Year / campaign | Production | Status (2026-11-03) | Blinding |
|---|---|---|---|---|---|
| τ→3µ | data | 2025 ParkingDoubleMuonLowMass, eras B–G, streams 0–7 | `SkimTau3mu_..._Mini_v4` | *TODO: manifest and coverage* | blinded in analysis |
| Ds→φπ | data | 2025, as above | `SkimDsPhiPi_..._Mini_v4` | *TODO* | n/a |
| Ds→φπ | MC | RunIII2024Summer24MiniAODv6 (2024 MC, used for 2025 data) | `SkimDsPhiPi_2024_MC_DsPhiPi_Mini_v4/260903_165448` | 1194 files discovered (not audited) | n/a |
| Ds→τ→3µ | MC | RunIII2024Summer24MiniAODv6 | `SkimTau3mu_2024_MC_Ds_tau3mu_Mini_v4/261102_161951` | 823/823 files, 4.71M events | MC |
| B0→τ→3µ | MC | same | `..._Bd_tau3mu_Mini_v4/261102_162000` | 1506/1506 files, 2.44M events | MC |
| B+→τ→3µ | MC | same | `..._Bu_tau3mu_Mini_v4/261102_162009` | 1269/1269 files, 2.01M events | MC |

2024 MC is used for the 2025 data, on PPD advice. The signal-MC rows count output files against CRAB jobs.
That does not prove every input event or lumisection was processed. **Physical MC normalisation is still
pending:** the private ntuples carry no generator-weight branches, and both the unit-weight assumption and
the processed coverage still have to be checked.

Reading needs a CMS VOMS proxy:

```bash
voms-proxy-info -timeleft
voms-proxy-init -voms cms -rfc          # if needed
xrdfs root://eos.cms.rcac.purdue.edu ls /store/user/skuang/
```

```python
import uproot
f = uproot.open("root://eos.cms.rcac.purdue.edu//store/user/skuang/ParkingDoubleMuonLowMass0/"
                "SkimTau3mu_2025eraC-v1_stream0_Mini_v4/260912_002703/0000/tau3mu_output_Data_1.root")
print(f["Events"].num_entries)
```

Notes:
- Workers (Slurm, Dask) must read over XRootD, not from the `/eos` mount.
- For remote workers, keep the proxy file in worker-visible storage and pass `X509_USER_PROXY`.
- Reading as `skuang` has been verified. Access from other accounts has **not been verified yet**.
- Facility documentation:
  - [Data access](https://analysis-facility.physics.purdue.edu/data-access/)
  - [EOS writes](https://analysis-facility.physics.purdue.edu/guide-eos-write/)
  - [Storage](https://analysis-facility.physics.purdue.edu/storage/)

## Analysis

*TODO:* signal and control selections, cutflows, and blinding (the data τ window stays closed).

## Uncertainty studies

*TODO:*
- momentum scale/resolution (§12.1, `Momentum/`)
- HLT prescale and efficiencies (§12.4, `HLT/`)
- L1 TripleMu-exclusive fraction (§12.4.2)

## Machine learning

*TODO:* training-table extraction, the XGBoost baseline, and evaluation.

## Outputs

Large outputs (ntuples, caches, models, plots) are not tracked in Git. *TODO:* the shared artifact location.

## Known limitations

*TODO.*

## Credits

- **Ntuplizer and analysis framework:** F. Nenna and the Bari group (`production/`; see
  `upstream_sources.json`).
- **HLT/Momentum/sPlot studies:** J. Schulte.
- **Purdue 2025 extensions:** S. Kuang.
