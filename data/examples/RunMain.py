# pylint: skip-file
# type: ignore

import pytrnsys.rsim.runParallelTrnsys as runTrnsys

pathConfig = "solar_dhw"
configFile = "run_solar_dhw.config"
runTool = runTrnsys.RunParallelTrnsys(pathConfig, configFile=configFile)
