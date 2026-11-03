import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
import FWCore.ParameterSet.VarParsing as VarParsing
from PhysicsTools.Tau3muNANO.Tau3mu_builder_cff import setupTau3Mu

options = VarParsing.VarParsing('analysis')
options.register('isMC', True, 
                 VarParsing.VarParsing.multiplicity.singleton, 
                 VarParsing.VarParsing.varType.bool, 
                 "True if MC, False if Data")
options.parseArguments()

isMC = options.isMC
process = cms.Process('NANO', eras.Run3)

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("PhysicsTools.NanoAOD.nano_cff")
process.load("TrackingTools.TransientTrack.TransientTrackBuilder_cfi")

from Configuration.AlCa.GlobalTag import GlobalTag
if isMC:
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_mcRun3_2024_realistic_v26', '')  # placeholder, stamped by submit_CRAB_purdue.py
else:
    process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_v4', '')

output_name = "tau3mu_output_MC.root" if isMC else "tau3mu_output_Data.root"

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))

process.source = cms.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'root://cms-xrd-global.cern.ch//store/mc/RunIII2024Summer24MiniAODv6/DstoTau-Tauto3Mu_Fil-3Mu_TuneCP5_13p6TeV_pythia8-evtgen/MINIAODSIM/150X_mcRun3_2024_realistic_v2-v4/2550000/eab164c0-efde-46fc-b6ba-6ed2865e82dc.root')
)

process.load("PhysicsTools.Tau3muNANO.Tau3mu_builder_cff")
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi") ##if isMC

setupTau3Mu(process, isMC)

# Purdue: store bits for the full 2025 menu OR (13 seeds, verified 2026-10-27,
# notebooks/L1_seeds_2025_MENU.txt) plus Felice's original list, without editing
# Tau3mu_builder_cff.py. A seed absent from the event's L1 menu is stored as 0.
from PhysicsTools.Tau3muNANO.Tau3mu_builder_cff import L1_path_list
MENU_2025 = [
    "L1_TripleMu_3SQ_2p5SQ_0_OS_Mass_Max12", "L1_TripleMu_4SQ_2p5SQ_0_OS_Mass_Max12",
    "L1_TripleMu_5SQ_3SQ_0_DoubleMu_5_3_SQ_OS_Mass_Max9", "L1_TripleMu_5SQ_3SQ_0OQ_DoubleMu_5_3_SQ_OS_Mass_Max9",
    "L1_DoubleMu0er1p5_SQ_OS_dR_Max1p4", "L1_DoubleMu0er1p4_SQ_OS_dR_Max1p4",
    "L1_DoubleMu4_SQ_OS_dR_Max1p2", "L1_DoubleMu4p5_SQ_OS_dR_Max1p2",
    "L1_DoubleMu0er1p4_SQ_OS_dEta_Max1p2", "L1_DoubleMu4er2p0_SQ_OS_dR_Max1p6",
    "L1_DoubleMu5_SQ_OS_dR_Max1p6", "L1_DoubleMu3er2p0_SQ_OS_dR_Max1p6",
    "L1_DoubleMu0er1p5_SQ_OS_dEta_Max1p2",
]
process.triggerTableTau3Mu.l1Seeds = cms.vstring(list(dict.fromkeys(MENU_2025 + list(L1_path_list))))

process.out = cms.OutputModule("NanoAODOutputModule",
    fileName = cms.untracked.string(output_name),
    SelectEvents = cms.untracked.PSet(
        SelectEvents = cms.vstring('p')
    ),
    outputCommands = cms.untracked.vstring(
        "drop *",
        "keep nanoaodFlatTable_*_*_*",
    ),
    compressionLevel = cms.untracked.int32(9),
    compressionAlgorithm = cms.untracked.string("ZLIB"),
)

process.p = cms.Path(process.tau3muSequence)
process.endp = cms.EndPath(process.out)

process.MessageLogger.cerr.FwkReport.reportEvery = 100