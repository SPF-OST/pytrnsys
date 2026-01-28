import pathlib as _pl
import os as _os

from pytrnsys.rsim import runParallelTrnsys as runTrnsys
from pytrnsys.utils import log as log

def run_pytrnsys(config_file_path: _pl.Path):
    logger = log.getOrCreateCustomLogger("root", "INFO")

    logger.info("Running config file %s...", "run")

    nameDeck = "run"
    pathBase = _os.getcwd()

    runTool = runTrnsys.RunParallelTrnsys(pathBase, nameDeck)

    runTool.readConfig(pathBase, str(config_file_path))
    runTool.getConfig()
    runTool.runConfig()
    runTool.runParallel()

    logger.info("...DONE (%s).", "run")