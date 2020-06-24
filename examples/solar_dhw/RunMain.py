import pytrnsys.rsim.runParallelTrnsys as runTrnsys
import os

pathConfig  = "C:\Daten\OngoingProject\pytrnsysTest2\\testScaling"
configFile = "run_solar_dhw.config"
runTool = runTrnsys.RunParallelTrnsys(pathConfig,configFile=configFile)