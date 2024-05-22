# pylint: skip-file
# type: ignore

__all__ = ["calculateCostsAndWriteReports", "CasesDefined", "OTHER"]

import pathlib as _pl
import json as _json

from .models import input as _input
from . import createCostCalculations as _co
from . import resultsWriter
from . import processType as _pt


CasesDefined = _pt.CasesDefined
OTHER = _pt.OTHER


def calculateCostsAndWriteReports(
    configFilePath: _pl.Path, resultsDirPath: _pl.Path, shallWriteReport: bool, processType: _pt.ProcessType
) -> None:
    config = createConfig(configFilePath)
    costCalculations = _co.createCostCalculations(config, resultsDirPath, processType)

    reportWriter = resultsWriter.ResultsWriter()
    for costCalculation in costCalculations:
        reportWriter.writeReportAndResults(config.parameters, costCalculation, shallWriteReport)


def createConfig(configFilePath: _pl.Path) -> _input.Input:
    with configFilePath.open("r") as configFile:
        serializedConfig = _json.load(configFile)

    config = _input.Input.from_dict(serializedConfig)
    return config
