__all__ = ["writeData"]

import pathlib as _pl
import typing as _tp

from . import _common


def writeData(
    pathFolder,
    fileName,
    allSeries: _tp.Sequence[_common.Series],
    abscissaVariable,
    ordinateVariable,
    seriesVariable,
    chunkVariable,
    shallPlotUncertainties,
):
    allSeriesSorted = list(sorted(allSeries, key=lambda s: s.index))

    columnHeadersLegend = _getColumnHeadersLegend(abscissaVariable, ordinateVariable, seriesVariable, chunkVariable)
    columnHeaders = "\t".join(f"{s.getAbscissaHeader()}\t{s.getOrdinateHeader()}" for s in allSeriesSorted)

    lines = f"! {columnHeadersLegend}\n! {columnHeaders}\n"
    maxSeriesLength = max(s.length for s in allSeriesSorted)
    for rowIndex in range(maxSeriesLength):
        for series in allSeriesSorted:
            if series.length <= rowIndex:
                lines += "-\t"
                continue

            x, xMax, xMin = _getMinMeanMaxAt(series.abscissa, rowIndex)
            formattedX = _formatUncertainValue(xMin, x, xMax, shallPlotUncertainties)

            yMin, y, yMax = _getMinMeanMaxAt(series.ordinate, rowIndex)
            formattedY = _formatUncertainValue(yMin, y, yMax, shallPlotUncertainties)

            lines += f"{formattedX}\t{formattedY}\t"

        lines += "\n"

        datFilePath = _pl.Path(pathFolder) / f"{fileName}.dat"
        datFilePath.write_text(lines)


def _getMinMeanMaxAt(axisValues, rowIndex):
    uMin, u, uMax = axisValues.mins[rowIndex], axisValues.means[rowIndex], axisValues.maxs[rowIndex]
    return uMin, u, uMax


def _getColumnHeadersLegend(abscissaVariable, ordinateVariable, seriesVariable, chunkVariable):
    if not seriesVariable:
        return f"{ordinateVariable}={ordinateVariable}({abscissaVariable})"

    if not chunkVariable:
        return f"{ordinateVariable}={ordinateVariable}({abscissaVariable}_j, {seriesVariable})"

    return f"{ordinateVariable}={ordinateVariable}({abscissaVariable}_j, {seriesVariable}, {chunkVariable})"


def _formatUncertainValue(uMin, u, uMax, shallPlotUncertainties):
    if not shallPlotUncertainties:
        return _formatValue(u)

    formattedValues = [_formatValue(v) for v in [uMin, u, uMax]]

    return "\t".join(formattedValues)


def _formatValue(u):
    if isinstance(u, str):
        return u

    return f"{u:8.4f}"
