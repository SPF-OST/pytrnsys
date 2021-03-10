__all__ = ['CostCalculation', 'createCostCalculations']

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


def createCostCalculations(config: _input.Input, resultsDirPath: _pl.Path,
                           typeOfProcess: _pt.ProcessType,
                           fileNamesToRead: _tp.Sequence[str])\
        -> _tp.Iterable["CostCalculation"]:
    pathAndResults = _loadResults(resultsDirPath, typeOfProcess, fileNamesToRead)

    for pathAndResult in pathAndResults:
        values = _getValues(config, pathAndResult.result)
        output = _output.Output.createOutput(config, values)
        costCalculation = CostCalculation(pathAndResult.resultsJsonFilePath, output)
        yield costCalculation


def _loadResults(resultsDirPath: _pl.Path,
                 processType: _pt.ProcessType,
                 fileNamesToRead: _tp.Sequence[str]) -> _tp.Iterable[_PathAndResult]:
    if processType == _pt.ProcessType.OTHER:
        return _loadResultsForProcessTypeOther(resultsDirPath, fileNamesToRead)
    elif processType == _pt.ProcessType.JSON:
        return _loadResultsForProcessTypeJson(resultsDirPath, fileNamesToRead)
    else:
        raise AssertionError(f"Unknown process type {processType}")


def _loadResultsForProcessTypeJson(resultsDirPath: _pl.Path, fileNamesToRead: _tp.Sequence[str]) \
        -> _tp.Iterable[_PathAndResult]:
    resultJsonFilePaths = [resultsDirPath / name for name in fileNamesToRead] if fileNamesToRead \
        else resultsDirPath.rglob('*-results.json')

    for resultsJsonFilePath in resultJsonFilePaths:
        serializedResults = resultsJsonFilePath.read_text()
        results = _json.loads(serializedResults)
        yield _PathAndResult(resultsJsonFilePath, results)


def _loadResultsForProcessTypeOther(resultsDirPath: _pl.Path, fileNamesToRead: _tp.Sequence[str]) \
        -> _tp.Iterable[_PathAndResult]:
    results = _results.ResultsProcessedFile(str(resultsDirPath))
    shallReadCompleteFolder = not fileNamesToRead
    results.readResultsData(resultType='json',
                            completeFolder=shallReadCompleteFolder,
                            fileNameList=fileNamesToRead)
    for containingDirPath, result in [(_pl.Path(p), r) for p, r in zip(results.fileName, results.results)]:
        resultsJsonFilePath = resultsDirPath / containingDirPath / f"{containingDirPath.name}-results.json"
        yield _PathAndResult(_pl.Path(resultsJsonFilePath), result)


def _getValues(config: _input.Input, result: _Result) -> _output.Values:
    return {v: _getValue(v, result) for v in config.variables}


def _getValue(variable: _input.Variable, result: _Result) -> float:
    return result[variable.name]
