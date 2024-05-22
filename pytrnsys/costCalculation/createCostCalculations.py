# pylint: skip-file

import collections.abc as _cabc
import dataclasses as _dc
import json as _json
import pathlib as _pl

from . import processType as _pt
from .models import input as _input
from .models import output as _output


@_dc.dataclass()
class CostCalculation:
    resultsJsonFilePath: _pl.Path
    output: _output.Output


_Result = _cabc.Mapping[str, float]


@_dc.dataclass()
class _PathAndResult:
    resultsJsonFilePath: _pl.Path
    result: _Result


def createCostCalculations(
    config: _input.Input, resultsDirPath: _pl.Path, processType: _pt.ProcessType
) -> _cabc.Sequence["CostCalculation"]:
    pathAndResults = loadResults(resultsDirPath, processType)

    costCalculations = [createCostCalculation(config, par) for par in pathAndResults]

    return costCalculations


def createCostCalculation(config: _input.Input, pathAndResult: _PathAndResult) -> CostCalculation:
    values = _getValues(config, pathAndResult.result)
    output = _output.Output.createOutput(config, values)
    costCalculation = CostCalculation(pathAndResult.resultsJsonFilePath, output)
    return costCalculation


def loadResults(resultsDirPath: _pl.Path, processType: _pt.ProcessType) -> _cabc.Iterable[_PathAndResult]:
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
