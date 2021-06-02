# pylint: skip-file
# type: ignore

__all__ = ["writeFiles"]

import pathlib as _pl
import typing as _tp
import dataclasses as _dc

import pytrnsys.plot.plotGle as _pgle

from . import _common


def writeFiles(
    outputFolder: str,
    outputFileStem: str,
    allSeries: _tp.Sequence[_common.Series],
    shallPlotUncertainties: bool,
) -> None:
    if not allSeries:
        return

    _writeDataFile(
        outputFolder,
        outputFileStem,
        allSeries,
        shallPlotUncertainties,
    )

    _writeScriptFile(outputFolder, outputFileStem, allSeries, shallPlotUncertainties)


@_dc.dataclass
class _VariableNames:
    abscissa: str
    ordinate: str
    series: _tp.Optional[str]
    chunk: _tp.Optional[str]


def _writeDataFile(
    outputFolder: str,
    outputFileStem: str,
    allSeries: _tp.Sequence[_common.Series],
    shallPlotUncertainties: bool,
) -> None:
    allSeriesSorted = list(sorted(allSeries, key=lambda s: s.index))

    columnHeadersLegend = _getColumnHeadersLegend(allSeriesSorted)
    columnHeaders = _getColumnHeaders(allSeriesSorted, shallPlotUncertainties)
    joinedColumnHeaders = "\t".join(columnHeaders)

    lines = f"! {columnHeadersLegend}\n! {joinedColumnHeaders}\n"
    maxSeriesLength = max(s.length for s in allSeriesSorted)
    for rowIndex in range(maxSeriesLength):
        for series in allSeriesSorted:
            if series.length <= rowIndex:
                missingValue = _formatMissingValue(shallPlotUncertainties)
                line = f"{missingValue}\t{missingValue}\t"
                lines += line
                continue

            x, xMax, xMin = _getMinMeanMaxAt(series.abscissa, rowIndex)
            formattedX = _formatUncertainValue(xMin, x, xMax, shallPlotUncertainties)

            yMin, y, yMax = _getMinMeanMaxAt(series.ordinate, rowIndex)
            formattedY = _formatUncertainValue(yMin, y, yMax, shallPlotUncertainties)

            lines += f"{formattedX}\t{formattedY}\t"

        lines += "\n"

        datFilePath = _pl.Path(outputFolder) / f"{outputFileStem}.dat"
        datFilePath.write_text(lines)


def _getColumnHeaders(allSeries: _tp.Sequence[_common.Series], shallPlotUncertainties: bool) -> _tp.Iterable[str]:
    for series in allSeries:
        yield series.getAbscissaHeader(shallPlotUncertainties)
        yield series.getOrdinateHeader(shallPlotUncertainties)


def _getColumnHeadersLegend(allSeries: _tp.Sequence[_common.Series]) -> str:
    variableNames = _getUniqueVariableNames(allSeries)

    abscissaVariable = variableNames.abscissa
    ordinateVariable = variableNames.ordinate
    seriesVariable = variableNames.series
    chunkVariable = variableNames.chunk

    if not seriesVariable:
        return f"{ordinateVariable}={ordinateVariable}({abscissaVariable})"

    if not chunkVariable:
        return f"{ordinateVariable}={ordinateVariable}({abscissaVariable}_j, {seriesVariable})"

    return f"{ordinateVariable}={ordinateVariable}({abscissaVariable}_j, {seriesVariable}, {chunkVariable})"


def _getUniqueVariableNames(allSeries: _tp.Sequence[_common.Series]) -> _VariableNames:
    abscissas = {s.abscissa.name for s in allSeries}
    if len(abscissas) > 1:
        raise ValueError("All series must have same abscissa")
    abscissa = list(abscissas)[0]

    ordinates = {s.ordinate.name for s in allSeries}
    if len(ordinates) > 1:
        raise ValueError("All series must have same ordinates")
    ordinate = list(ordinates)[0]

    seriesNames = {s.groupingValue.name if s.groupingValue else None for s in allSeries}
    if len(seriesNames) > 1:
        raise ValueError("All series must have same series variable (or none at all)")
    seriesName = list(seriesNames)[0]

    chunks = {s.chunk.groupingValue.name if s.chunk else None for s in allSeries}
    if len(chunks) > 1:
        raise ValueError("All series must have same chunk (or none at all)")
    chunk = list(chunks)[0]

    return _VariableNames(abscissa, ordinate, seriesName, chunk)


def _formatMissingValue(shallPlotUncertainties: bool) -> str:
    if not shallPlotUncertainties:
        return "-"

    return "-\t-\t-"


def _getMinMeanMaxAt(axisValues, rowIndex) -> _tp.Tuple[float, float, float]:
    uMin, u, uMax = (
        axisValues.mins[rowIndex],
        axisValues.means[rowIndex],
        axisValues.maxs[rowIndex],
    )
    return uMin, u, uMax


def _formatUncertainValue(uMin, u, uMax, shallPlotUncertainties) -> str:
    if not shallPlotUncertainties:
        return _formatValue(u)

    formattedValues = [_formatValue(v) for v in [uMin, u, uMax]]

    return "\t".join(formattedValues)


def _formatValue(u) -> str:
    if isinstance(u, str):
        return u

    return f"{u:8.4f}"


def _writeScriptFile(
    outputFolder: str,
    outputFileStem: str,
    allSeries: _tp.Sequence[_common.Series],
    shallPlotUncertainties: bool,
) -> None:
    columnHeaders = list(_getColumnHeaders(allSeries, shallPlotUncertainties))

    plot = _pgle.PlotGle(outputFolder)

    if shallPlotUncertainties:
        plot.getEasyErrorPlot(outputFileStem, f"{outputFileStem}.dat", columnHeaders)
    else:
        plot.getEasyPlot(
            outputFileStem, f"{outputFileStem}.dat", columnHeaders, inputsAsPairs=True
        )
