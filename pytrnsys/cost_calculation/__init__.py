__all__ = ['calculateCostsAndWriteReports']

import pathlib as _pl
import json as _json
import typing as _tp

from ._models import input as _input
from . import _createCostCalculations as _co
from . import _report


def calculateCostsAndWriteReports(configFilePath: _pl.Path, resultsDirPath: _pl.Path,
                                  fileNamesToRead: _tp.Sequence[str] = ()) -> None:
    config = _createConfig(configFilePath)
    costCalculations = _co.createCostCalculations(config, resultsDirPath, fileNamesToRead)

    reportWriter = _report.ReportWriter()
    for costCalculation in costCalculations:
        reportWriter.writeReportAndResults(config.parameters, costCalculation, resultsDirPath)


def _createConfig(configFilePath):
    with configFilePath.open('r') as configFile:
        serializedConfig = _json.load(configFile)

    config = _input.Input.from_dict(serializedConfig)
    return config
