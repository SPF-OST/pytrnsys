__all__ = ['ResultOutput', 'createOutputs']

import pathlib as _pl
import typing as _tp
import dataclasses as _dc

from ._models import input as _input
from ._models import output as _output

import pytrnsys.psim.resultsProcessedFile as _results

_Result = _tp.Dict[str, float]


@_dc.dataclass(frozen=True)
class ResultOutput:
    resultsDir: _pl.Path
    output: _output.Output


def createOutputs(config: _input.Input, resultsDirPath: _pl.Path,
                  shallReadCompleteFolder: bool, fileNamesToRead: _tp.Sequence[str])\
        -> _tp.Sequence["ResultOutput"]:
    results = _results.ResultsProcessedFile(str(resultsDirPath))
    results.readResultsData(resultType='json',
                            completeFolder=shallReadCompleteFolder,
                            fileNameList=fileNamesToRead)

    resultOutputs = []
    for i, result in enumerate(results.results):
        values = _getValues(config, result)
        output = _output.Output.createOutput(config, values)
        resultsDir = _pl.Path(results.fileName[i])
        resultOutput = ResultOutput(resultsDir, output)
        resultOutputs.append(resultOutput)

    return resultOutputs


def _getValues(config: _input.Input, result: _Result) -> _output.Values:
    return {v: _getValue(v, result) for v in config.variables}


def _getValue(variable: _input.Variable, result: _Result) -> float:
    return result[variable.name]

