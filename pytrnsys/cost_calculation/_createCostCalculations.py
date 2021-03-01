__all__ = ['CostCalculation', 'createCostCalculations']

import pathlib as _pl
import typing as _tp
import dataclasses as _dc

from ._models import input as _input
from ._models import output as _output

import pytrnsys.psim.resultsProcessedFile as _results

_Result = _tp.Dict[str, float]


@_dc.dataclass(frozen=True)
class CostCalculation:
    resultsDir: _pl.Path
    output: _output.Output


def createCostCalculations(config: _input.Input, resultsDirPath: _pl.Path,
                           fileNamesToRead: _tp.Sequence[str])\
        -> _tp.Iterable["CostCalculation"]:
    results = _results.ResultsProcessedFile(str(resultsDirPath))

    shallReadCompleteFolder = not fileNamesToRead
    results.readResultsData(resultType='json',
                            completeFolder=shallReadCompleteFolder,
                            fileNameList=fileNamesToRead)

    for i, result in enumerate(results.results):
        values = _getValues(config, result)
        output = _output.Output.createOutput(config, values)
        resultsDir = _pl.Path(results.fileName[i])
        resultOutput = CostCalculation(resultsDir, output)
        yield resultOutput


def _getValues(config: _input.Input, result: _Result) -> _output.Values:
    return {v: _getValue(v, result) for v in config.variables}


def _getValue(variable: _input.Variable, result: _Result) -> float:
    return result[variable.name]
