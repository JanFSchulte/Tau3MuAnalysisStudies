from CRABClient.UserUtilities import config, getUsername
config = config()

config.General.requestName = 'SkimCHANNELNAME_YEAR_ERANAME_Mini_v4'
config.General.workArea = 'crab_projects'
config.General.transferOutputs = True
config.General.transferLogs = False

config.JobType.pluginName = 'Analysis'

config.JobType.psetName = 'FILE_TO_SUBMIT_PATH'
config.JobType.pyCfgParams = ['isMC=True']
MAXRUNTIME_LINE
# 2026-09-04: CRAB's default is 2000 MB, but era C jobs average ~1780 MB and
# peak at ~3570 MB -- the tail was killed with exit 8901 UnexpectedJobTermination.
config.JobType.maxMemoryMB = 3000  # 3000 = CRAB ceiling for 1-core jobs; 4000 is rejected at submit

config.Data.inputDataset = 'DATASET_NAME'
config.Data.allowNonValidInputDataset = True
config.Data.inputDBS = 'INPUT_TYPE'
config.Data.splitting = 'SPLITTING_MODE'
config.Data.unitsPerJob = UNITS_PER_JOB
# NOTE: no lumiMask -- MC has no golden JSON. This is the one structural
# difference from CRAB_template_purdue.py (besides isMC/naming).
#config.Data.publication = True
config.Data.outputDatasetTag = 'SkimCHANNELNAME_YEAR_ERANAME_Mini_v4'
config.JobType.allowUndistributedCMSSW = True
config.Site.storageSite = 'T2_US_Purdue'
config.Site.ignoreGlobalBlacklist  = True
