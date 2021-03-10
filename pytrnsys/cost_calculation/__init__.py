__all__ = ['calculateCostsAndWriteReports']

import pathlib as _pl
import json as _json
import typing as _tp

from ._models import input as _input
from . import _createCostCalculations as _co
from . import _resultsWriter
from .processType import ProcessType


def calculateCostsAndWriteReports(configFilePath: _pl.Path, resultsDirPath: _pl.Path,
                                  typeOfProcess: ProcessType,
                                  fileNamesToRead: _tp.Sequence[str] = ()) -> None:
    config = _createConfig(configFilePath)
    costCalculations = _co.createCostCalculations(config, resultsDirPath, typeOfProcess, fileNamesToRead)

    reportWriter = _resultsWriter.ResultsWriter()
    for costCalculation in costCalculations:
        reportWriter.writeReportAndResults(config.parameters, costCalculation)


def _createConfig(configFilePath):
    with configFilePath.open('r') as configFile:
        serializedConfig = _json.load(configFile)

    config = _input.Input.from_dict(serializedConfig)
    return config
