import pytrnsys.rsim.runParallelTrnsys as runTrnsys
import os

pathConfig  = "pathToTheConfigFile"
configFile = "DualRun.config"
runTool = runTrnsys.RunParallelTrnsys(pathConfig,configFile=configFile)