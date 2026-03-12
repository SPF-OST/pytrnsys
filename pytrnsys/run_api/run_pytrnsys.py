# pylint: disable=invalid-name

import pathlib as _pl
import os as _os

from pytrnsys.rsim import runParallelTrnsys as runTrnsys
from pytrnsys.utils import log


def run_pytrnsys(config_file_path: _pl.Path) -> Exception | None:
    """
    Method to run pytrnsys using a .config file.

    Parameters
    __________
    config_file_path: pathlib.Path
        Path to the desired configuration file.


    Returns
    -------
        error: Exception | None
            This error can be used to get information about why pytrnsys failed.
    """
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
        runTool.readConfig(pathBase, str(config_file_path))
        runTool.getConfig()
        runTool.runConfig()
        runTool.runParallel()

        logger.info("...DONE (%s).", "run")
    except Exception as e:
        error = e

    return error
