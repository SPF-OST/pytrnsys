# pylint: disable=invalid-name

import pathlib as _pl
import os as _os

from pytrnsys.rsim import runParallelTrnsys as runTrnsys
from pytrnsys.utils import log


def run_pytrnsys(configFilePath: _pl.Path) -> Exception | None:
    logger = log.getOrCreateCustomLogger("root", "INFO")

    logger.info("Running config file %s...", "run")

    nameDeck = "run"
    pathBase = _os.getcwd()
    print("")
    print(f"pathBase {pathBase}")
    print("")

    runTool = runTrnsys.RunParallelTrnsys(pathBase, nameDeck)  # type: ignore[attr-defined]
    error = None
    try:
        runTool.readConfig(pathBase, str(configFilePath))
        runTool.getConfig()
        runTool.runConfig()
        runTool.runParallel()

        logger.info("...DONE (%s).", "run")
    except Exception as e:
        error = e

    return error
