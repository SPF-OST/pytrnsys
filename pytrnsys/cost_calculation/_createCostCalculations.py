# pylint: skip-file
# type: ignore

__all__ = ["CostCalculation", "createCostCalculations"]

import pathlib as _pl
import typing as _tp
import dataclasses as _dc
import json as _json

from ._models import input as _input
from ._models import output as _output
from . import processType as _pt

import pytrnsys.psim.resultsProcessedFile as _results


@_dc.dataclass()
class CostCalculation:
    resultsJsonFilePath: _pl.Path
    output: _output.Output


_Result = _tp.Dict[str, float]


@_dc.dataclass()
class _PathAndResult:
    resultsJsonFilePath: _pl.Path
    result: _Result


def createCostCalculations(
    config: _input.Input, resultsDirPath: _pl.Path, processType: _pt.ProcessType
) -> _tp.Iterable["CostCalculation"]:
    pathAndResults = _loadResults(resultsDirPath, processType)

    for pathAndResult in pathAndResults:
        values = _getValues(config, pathAndResult.result)
        output = _output.Output.createOutput(config, values)
        costCalculation = CostCalculation(pathAndResult.resultsJsonFilePath, output)
        yield costCalculation


def _loadResults(resultsDirPath: _pl.Path, processType: _pt.ProcessType) -> _tp.Iterable[_PathAndResult]:
    resultJsonFilePaths = _getResultJsonFilePaths(resultsDirPath, processType)

    for resultsJsonFilePath in resultJsonFilePaths:
        serializedResults = resultsJsonFilePath.read_text()
        results = _json.loads(serializedResults)
        yield _PathAndResult(resultsJsonFilePath, results)


def _getResultJsonFilePaths(resultsDirPath: _pl.Path, processType: _pt.ProcessType):
    if isinstance(processType, _pt.CasesDefined):
        return [resultsDirPath / case / f"{case}-results.json" for case in processType.cases]
    elif processType == _pt.OTHER:
        return resultsDirPath.rglob("*-results.json")
    else:
        raise AssertionError(f"Unknown processType: {processType}")


def _getValues(config: _input.Input, result: _Result) -> _output.Values:
    return {v: _getValue(v, result) for v in config.variables}


def _getValue(variable: _input.Variable, result: _Result) -> float:
    return result[variable.name]
