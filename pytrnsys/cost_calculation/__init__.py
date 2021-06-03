# pylint: skip-file
# type: ignore

__all__ = ["calculateCostsAndWriteReports", "CasesDefined", "OTHER"]

import pathlib as _pl
import json as _json

from ._models import input as _input
from . import _createCostCalculations as _co
from . import _resultsWriter
from . import processType as _pt


CasesDefined = _pt.CasesDefined
OTHER = _pt.OTHER


def calculateCostsAndWriteReports(
    configFilePath: _pl.Path, resultsDirPath: _pl.Path, shallWriteReport: bool, processType: _pt.ProcessType
) -> None:
    config = _createConfig(configFilePath)
    costCalculations = _co.createCostCalculations(config, resultsDirPath, processType)

    reportWriter = _resultsWriter.ResultsWriter()
    for costCalculation in costCalculations:
        reportWriter.writeReportAndResults(config.parameters, costCalculation, shallWriteReport)


def _createConfig(configFilePath):
    with configFilePath.open("r") as configFile:
        serializedConfig = _json.load(configFile)

    config = _input.Input.from_dict(serializedConfig)
    return config
