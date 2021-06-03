# pylint: skip-file
# type: ignore

import pytrnsys.rsim.runParallelTrnsys as runTrnsys
import os

pathConfig = os.getcwd()
configFile = "run_pv_battery.config"
runTool = runTrnsys.RunParallelTrnsys(pathConfig, configFile=configFile)
