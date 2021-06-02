# pylint: skip-file
# type: ignore

__all__ = ["createPlot"]

import json as _json
import os as _os
import pathlib as _pl
import typing as _tp

import matplotlib.pyplot as _plt

import pytrnsys.psim.conditions as _conds
import pytrnsys.report.latexReport as _latex

from . import _gle
from . import _common


def createPlot(
    plotVariables,
    pathFolder,
    typeOfProcess,
    logger,
    latexNames,
    configPath,
    stylesheet,
    plotStyle,
    comparePlotUserName,
    setPrintDataForGle,
    shallPlotUncertainties,
    extensionFig
):
    xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions = _separatePlotVariables(plotVariables)

    resultFilePaths = _getResultsFilePaths(pathFolder, typeOfProcess)
    if not resultFilePaths:
        logger.error("No results.json-files found.")
        logger.error('Unable to generate "comparePlot %s %s %s"', xAxisVariable, yAxisVariable, seriesVariable)
        return

    manySeriesOrChunks = _loadValues(
        resultFilePaths, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions, shallPlotUncertainties
    )
    if not manySeriesOrChunks:
        logger.warning('The following conditions from "comparePlotConditional" were never met all at once:')
        for condition in conditions.conditions:
            logger.warning(condition)
        logger.warning("The respective plot cannot be generated.")
        return

    _configurePypltStyle(stylesheet)

    styles = ["x-", "x--", "x-.", "x:", "o-", "o--", "o-.", "o:"]
    if plotStyle == "dot":
        styles = ["x", "o", "+", "d", "s", "v", "^", "h"]

    if isinstance(manySeriesOrChunks, _common.ManyChunks) and len(manySeriesOrChunks.chunks) > len(styles):
        raise AssertionError("Too many chunks")

    allSeries = (
        manySeriesOrChunks.allSeries
        if isinstance(manySeriesOrChunks, _common.ManySeries)
        else [s for c in manySeriesOrChunks.chunks for s in c.allSeries]
    )
    seriesColors = _getSeriesColors(allSeries)

    doc = _createLatexDoc(configPath, latexNames)

    fig, ax = _plt.subplots(constrained_layout=True)

    chunkLabels, dummyLines = _plotValues(ax, manySeriesOrChunks, shallPlotUncertainties, seriesColors, styles, doc)

    _setLegendsAndLabels(
        fig, ax, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, chunkLabels, dummyLines, doc
    )

    conditionsFileNamePart, conditionsTitle = _getConditionsFileNameAndTitle(conditions)

    if conditionsTitle:
        ax.set_title(conditionsTitle)

    _savePlotAndData(
        fig,
        xAxisVariable,
        yAxisVariable,
        seriesVariable,
        chunkVariable,
        pathFolder,
        comparePlotUserName,
        conditionsFileNamePart,
        allSeries,
        setPrintDataForGle,
        shallPlotUncertainties,
        extensionFig,
    )


def _separatePlotVariables(plotVariables):
    if len(plotVariables) < 2:
        raise ValueError(
            "You did not specify variable names and labels " "for the x and the y Axis in a compare Plot line"
        )
    xAxisVariable = plotVariables[0]
    yAxisVariable = plotVariables[1]

    seriesVariable = ""
    chunkVariable = ""

    serializedConditions = plotVariables[2:]
    if len(plotVariables) >= 3 and not _conds.mayBeSerializedCondition(plotVariables[2]):
        seriesVariable = plotVariables[2]
        serializedConditions = plotVariables[3:]

    if len(plotVariables) >= 4 and not _conds.mayBeSerializedCondition(plotVariables[3]):
        chunkVariable = plotVariables[3]
        serializedConditions = plotVariables[4:]

    conditions = _conds.createConditions(serializedConditions)

    return xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions


def _getResultsFilePaths(pathFolder, typeOfProcess) -> _tp.Sequence[_pl.Path]:
    pathFolder = _pl.Path(pathFolder)

    if not pathFolder.is_dir():
        raise ValueError("`pathFolder` needs to point to a directory.")

    if typeOfProcess == "json":
        return list(pathFolder.rglob("*-results.json"))

    resultFilePaths = [d / f"{d.name}-results.json" for d in pathFolder.iterdir() if d.is_dir()]

    return resultFilePaths


def _loadValues(
    resultFilePaths, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions, shallPlotUncertainties
) -> _tp.Union[_common.ManySeries, _common.ManyChunks, None]:
    values = {}
    for resultFilePath in resultFilePaths:
        results = _loadResults(resultFilePath)

        conditionsFulfilled = conditions.doResultsSatisfyConditions(results)
        if not conditionsFulfilled:
            continue

        xAxis = _getValue(results, xAxisVariable)
        yAxis = _getValue(results, yAxisVariable)

        chunkVariableValue = results[chunkVariable] if chunkVariable else None
        if chunkVariableValue not in values:
            values[chunkVariableValue] = {}
        chunk = values[chunkVariableValue]

        seriesVariableValue = results[seriesVariable] if seriesVariable else None
        if seriesVariableValue not in chunk:
            chunk[seriesVariableValue] = []
        seriesValues = chunk[seriesVariableValue]

        seriesValues.append((xAxis, yAxis))

    manySeriesOrChunks = _common.createManySeriesOrManyChunksFromValues(
        xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, values, shallPlotUncertainties
    )

    return manySeriesOrChunks


def _loadResults(resultFilePath) -> _tp.Dict[str, _tp.Any]:
    serializedResults = resultFilePath.read_text()
    resultsDict = _json.loads(serializedResults)
    return resultsDict


def _getValue(resultsDict, variable):
    if "[" not in variable:
        yAxis = resultsDict[variable]
    else:
        name, index = str(variable).split("[")
        index = int(index.replace("]", ""))
        yAxis = resultsDict[name][index]
    return yAxis


def _configurePypltStyle(stylesheet):
    if not stylesheet:
        stylesheet = "word.mplstyle"
    if stylesheet not in _plt.style.available:
        root = _os.path.dirname(_os.path.abspath(__file__))
        stylesheet = _os.path.join(root, r"../stylesheets", stylesheet)
    _plt.style.use(stylesheet)


def _plotValues(
    ax: _plt.Axes,
    manySeriesOrChunks: _tp.Union[_common.ManySeries, _common.ManyChunks],
    shallPlotUncertainties,
    seriesColors,
    styles,
    doc,
):
    if isinstance(manySeriesOrChunks, _common.ManySeries):
        styles = styles[0]

        seriesLabels = set()
        for series in manySeriesOrChunks.allSeries:
            _plotSeries(ax, series, styles, seriesColors, seriesLabels, doc, shallPlotUncertainties)

        return [], []
    else:
        dummyLines = []
        chunkLabels = []
        seriesLabels = set()
        for chunk, style in zip(manySeriesOrChunks.chunks, styles):
            dummyLines.append(ax.plot([], [], style, c="black"))
            chunkLabel = _getChunkLabel(chunk.groupingValue.value)

            if chunkLabel:
                chunkLabels.append(chunkLabel)

            for series in chunk.allSeries:
                _plotSeries(ax, series, style, seriesColors, seriesLabels, doc, shallPlotUncertainties)

        return chunkLabels, dummyLines


def _plotSeries(ax, series, style, seriesColors, seriesLabels, doc, shallPlotUncertainties):
    seriesVariableValue = series.groupingValue.value if series.groupingValue else None

    label = _getSeriesLabelOrNone(seriesVariableValue, seriesLabels, doc)

    abscissa = series.abscissa
    ordinate = series.ordinate

    if shallPlotUncertainties:
        ax.errorbar(
            abscissa.means,
            ordinate.means,
            ordinate.errors,
            abscissa.errors,
            style,
            color=seriesColors[series],
            label=label,
        )
    else:
        ax.plot(abscissa.means, ordinate.means, style, color=seriesColors[series], label=label)


def _createLatexDoc(configPath, latexNames):
    doc = _latex.LatexReport("", "")
    if latexNames:
        if ":" in latexNames:
            latexNameFullPath = latexNames
        else:
            latexNameFullPath = _os.path.join(configPath, latexNames)
        doc.getLatexNamesDict(file=latexNameFullPath)
    else:
        doc.getLatexNamesDict()
    return doc


def _getSeriesColors(allSeries):
    colors = _plt.rcParams["axes.prop_cycle"].by_key()["color"]
    seriesColors = {s: colors[i % len(colors)] for i, s in enumerate(allSeries)}
    return seriesColors


def _getChunkLabel(chunkVariableValue):
    if chunkVariableValue is None:
        return None

    if isinstance(chunkVariableValue, str):
        return chunkVariableValue

    roundedValue = round(float(chunkVariableValue), 2)
    return "{:.2f}".format(roundedValue)


def _getSeriesLabelOrNone(seriesVariableValue, labelSet, doc):
    if seriesVariableValue is None:
        return None

    labelValue = seriesVariableValue if isinstance(seriesVariableValue, str) else round(float(seriesVariableValue), 2)

    if labelValue in labelSet:
        return None

    labelSet.add(labelValue)

    if not isinstance(labelValue, str):
        label = "{0:.1f}".format(labelValue)
    else:
        label = doc.getNiceLatexNames(labelValue)

    return label


def _setLegendsAndLabels(
    fig, ax, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, chunkLabels, dummyLines, doc
):
    if chunkVariable:
        legend = fig.legend(
            [dummy_line[0] for dummy_line in dummyLines],
            chunkLabels,
            title=doc.getNiceLatexNames(chunkVariable),
            bbox_to_anchor=(1.31, 1.0),
            bbox_transform=ax.transAxes,
        )
        fig.add_artist(legend)
    if seriesVariable:
        legend = fig.legend(
            title=doc.getNiceLatexNames(seriesVariable), bbox_to_anchor=(1.15, 1.0), bbox_transform=ax.transAxes
        )
        fig.add_artist(legend)
    ax.set_xlabel(doc.getNiceLatexNames(xAxisVariable))
    ax.set_ylabel(doc.getNiceLatexNames(yAxisVariable))


def _savePlotAndData(
    fig,
    xAxisVariable,
    yAxisVariable,
    seriesVariable,
    chunkVariable,
    pathFolder,
    comparePlotUserName,
    conditionsFileNamePart,
    allSeries,
    setPrintDataForGle,
    shallPlotUncertainties,
    extensionFig,
):
    fileName = _getFileName(
        xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditionsFileNamePart, comparePlotUserName
    )

    fig.savefig(_os.path.join(pathFolder, fileName + extensionFig), bbox_inches="tight")
    _plt.close()

    if setPrintDataForGle:
        _gle.writeFiles(
            pathFolder,
            fileName,
            allSeries,
            shallPlotUncertainties,
        )


def _getFileName(xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditionsFileName, comparePlotUserName):
    possibleParts = [
        xAxisVariable,
        yAxisVariable,
        seriesVariable,
        chunkVariable,
        conditionsFileName,
        comparePlotUserName,
    ]

    parts = [part for part in possibleParts if part]

    return "_".join(parts)


def _getConditionsFileNameAndTitle(conditions):
    conditionsFileName = ""
    conditionsTitle = ""
    for condition in conditions.conditions:
        conditionsFileName += condition.serializedCondition
        if conditionsTitle != "":
            conditionsTitle += ", " + condition.serializedCondition
        else:
            conditionsTitle += condition.serializedCondition
    conditionsTitle = conditionsTitle.replace("RANGE", "")
    conditionsTitle = conditionsTitle.replace("LIST", "")
    conditionsFileName = conditionsFileName.replace("==", "=")
    conditionsFileName = conditionsFileName.replace(">", "_g_")
    conditionsFileName = conditionsFileName.replace("<", "_l_")
    conditionsFileName = conditionsFileName.replace(">=", "_ge_")
    conditionsFileName = conditionsFileName.replace("<=", "_le_")
    conditionsFileName = conditionsFileName.replace("|", "_o_")
    conditionsFileName = conditionsFileName.replace("RANGE:", "")
    conditionsFileName = conditionsFileName.replace("LIST:", "")
    return conditionsFileName, conditionsTitle
