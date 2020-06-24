import pytrnsys.rsim.runParallelTrnsys as runTrnsys

pathConfig  = "pathToTheConfigFile"
configFile = "DualRun.config"
runTool = runTrnsys.RunParallelTrnsys(pathConfig,configFile=configFile)