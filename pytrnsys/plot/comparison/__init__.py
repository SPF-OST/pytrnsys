import collections.abc as _cabc
import json as _json
import logging as _log
import os as _os
import pathlib as _pl
import typing as _tp

import matplotlib.pyplot as _plt

import pytrnsys.plot.comparison.common as _common
import pytrnsys.psim.conditions as _conds
import pytrnsys.report.latexReport as _latex
from . import _gle


def createPlot(  # pylint: disable=too-many-arguments,too-many-locals
    plotVariablesAndConditions: _cabc.Sequence[str],
    resultsDirPath: str,
    logger: _log.Logger,
    *,
    imageFileExtension: str = ".png",
    typeOfProcess: _tp.Literal["json"] | None = None,
    relativeLatexNamesFilePath: str | None = None,
    configPath: str | None = None,
    stylesheetNameOrPath: str | None = None,
    plotStyle: _tp.Literal["dot"] | None = None,
    comparePlotUserName: str | None = None,
    shallPrintDataForGle: bool = False,
    shallPlotUncertainties: bool = False,
):
    xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions = _separatePlotVariables(
        plotVariablesAndConditions
    )

    assert seriesVariable != "" and chunkVariable != ""

    resultFilePaths = _getResultsFilePaths(resultsDirPath, typeOfProcess, logger)
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

    _configurePypltStyle(stylesheetNameOrPath)

    createAndSavePlotAndData(
        manySeriesOrChunks,
        resultsDirPath,
        imageFileExtension,
        conditions,
        relativeLatexNamesFilePath,
        configPath,
        plotStyle,
        comparePlotUserName,
        shallPrintDataForGle,
        shallPlotUncertainties,
    )


def createAndSavePlotAndData(  # pylint: disable=too-many-arguments,too-many-locals
    manySeriesOrChunks: _common.ManySeries | _common.ManyChunks,
    resultsFolderPath: str,
    extensionFig,
    conditions: _conds.Conditions = _conds.ALL,
    latexNamesFilePath: str | None = None,
    configFileDirPath: str | None = None,
    plotStyle: _tp.Literal["dot"] | None = None,
    comparePlotUserName: str | None = None,
    shallPrintDataForGle: bool = False,
    shallPlotUncertainties: bool = False,
):
    styles = ["x-", "x--", "x-.", "x:", "o-", "o--", "o-.", "o:"]
    if plotStyle == "dot":
        styles = ["x", "o", "+", "d", "s", "v", "^", "h"]

    if isinstance(manySeriesOrChunks, _common.ManyChunks) and len(manySeriesOrChunks.chunks) > len(styles):
        raise AssertionError("Too many chunks")

    fig, ax = _plt.subplots(constrained_layout=True)

    chunkLabels, dummyLines = _plotValues(ax, manySeriesOrChunks, styles)

    doc = _createLatexDoc(configFileDirPath, latexNamesFilePath)

    seriesGroupingValueName = (
        manySeriesOrChunks.seriesGroupingValueName
        if isinstance(manySeriesOrChunks, _common.ManyChunks)
        else manySeriesOrChunks.groupingValueName
    )
    chunkGroupingValueName = (
        manySeriesOrChunks.groupingValueName if isinstance(manySeriesOrChunks, _common.ManyChunks) else None
    )
    _setLegendsAndLabels(
        fig,
        ax,
        manySeriesOrChunks.abscissaName,
        manySeriesOrChunks.ordinateName,
        seriesGroupingValueName,
        chunkGroupingValueName,
        chunkLabels,
        dummyLines,
        doc,
    )

    conditionsFileNamePart, conditionsTitle = _getConditionsFileNameAndTitle(conditions)
    if conditionsTitle:
        ax.set_title(conditionsTitle)

    allSeries = (
        manySeriesOrChunks.allSeries
        if isinstance(manySeriesOrChunks, _common.ManySeries)
        else [s for c in manySeriesOrChunks.chunks for s in c.manySeries.allSeries]
    )

    _savePlotAndData(
        fig,
        manySeriesOrChunks.abscissaName,
        manySeriesOrChunks.ordinateName,
        seriesGroupingValueName,
        chunkGroupingValueName,
        resultsFolderPath,
        comparePlotUserName,
        conditionsFileNamePart,
        allSeries,
        shallPrintDataForGle,
        shallPlotUncertainties,
        extensionFig,
    )


def _separatePlotVariables(plotVariables):
    if len(plotVariables) < 2:
        raise ValueError(
            "You did not specify variable names and labels for the x and the y Axis in a `comparePlot` line"
        )
    xAxisVariable = plotVariables[0]
    yAxisVariable = plotVariables[1]

    seriesVariable = None
    chunkVariable = None

    serializedConditions = plotVariables[2:]
    if len(plotVariables) >= 3 and not _conds.mayBeSerializedCondition(plotVariables[2]):
        seriesVariable = plotVariables[2]
        serializedConditions = plotVariables[3:]

    if len(plotVariables) >= 4 and not _conds.mayBeSerializedCondition(plotVariables[3]):
        chunkVariable = plotVariables[3]
        serializedConditions = plotVariables[4:]

    conditions = _conds.createConditions(serializedConditions)

    return xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions


def _getResultsFilePaths(
    pathFolderAsString: str, typeOfProcess: _tp.Literal["json"] | None, logger: _log.Logger
) -> _tp.Sequence[_pl.Path]:
    pathFolder = _pl.Path(pathFolderAsString)

    if not pathFolder.is_dir():
        raise ValueError("`pathFolder` needs to point to a directory.")

    if typeOfProcess == "json":
        return list(pathFolder.rglob("*-results.json"))

    return _getExistingResultsFilePaths(pathFolder, logger)


def _getExistingResultsFilePaths(pathFolder: _pl.Path, logger: _log.Logger) -> _tp.Sequence[_pl.Path]:
    resultFilePaths = sorted(d / f"{d.name}-results.json" for d in pathFolder.iterdir() if d.is_dir())
    existingResultsFilePaths = [p for p in resultFilePaths if p.is_file()]
    missingResultsFilePaths = sorted(set(resultFilePaths) - set(existingResultsFilePaths))

    if missingResultsFilePaths:
        formattedMissingResultsFilePaths = "\n\t".join(str(p) for p in missingResultsFilePaths)
        logger.warning(
            "The following expected result files could not be found:\n\t%s", formattedMissingResultsFilePaths
        )

    return existingResultsFilePaths


def _loadValues(
    resultsFilePaths: _tp.Sequence[_pl.Path],
    xAxisVariable: str,
    yAxisVariable: str,
    seriesVariable: str | None,
    chunkVariable: str | None,
    conditions: _conds.Conditions,
    shallPlotUncertainties: bool,
) -> _tp.Union[_common.ManySeries, _common.ManyChunks, None]:
    allResults = [
        results
        for p in resultsFilePaths
        if (results := _loadResults(p)) and conditions.doResultsSatisfyConditions(results)
    ]

    return _common.createManySeriesOrManyChunksFromResults(
        allResults,
        xAxisVariable,
        yAxisVariable,
        seriesVariable,
        chunkVariable,
        shallPlotUncertainties,
    )


def _loadResults(resultsFilePath) -> _tp.Mapping[str, _tp.Any]:
    serializedResults = resultsFilePath.read_text()
    resultsDict = _json.loads(serializedResults)
    return resultsDict


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
    styles: _cabc.Sequence[str],
) -> tuple[_cabc.Sequence[str], _cabc.Sequence[_tp.Any]]:
    if isinstance(manySeriesOrChunks, _common.ManySeries):
        allSeries = manySeriesOrChunks.allSeries
        chunkStyle = styles[0]

        colors = _getSeriesColors(len(allSeries))

        for series, seriesColor in zip(allSeries, colors):
            _plotSeries(ax, series, chunkStyle, seriesColor)

        return [], []

    if isinstance(manySeriesOrChunks, _common.ManyChunks):
        colors = _getSeriesColors(manySeriesOrChunks.chunkLength)

        dummyLines = []
        chunkLabels = []
        for chunk, chunkStyle in zip(manySeriesOrChunks.chunks, styles):
            dummyLines.append(ax.plot([], [], chunkStyle, c="black"))
            chunkLabel = chunk.groupingValue.label

            if chunkLabel:
                chunkLabels.append(chunkLabel)

            allSeries = chunk.manySeries.allSeries
            for series, seriesColor in zip(allSeries, colors):
                _plotSeries(ax, series, chunkStyle, seriesColor)

        return chunkLabels, dummyLines

    raise AssertionError("Can't get here.")


def _plotSeries(ax, series, style, color):
    label = series.groupingValue.label if series.groupingValue else None

    abscissa = series.abscissa
    ordinate = series.ordinate

    if series.shallPrintUncertainties:
        ax.errorbar(
            x=abscissa.means,
            y=ordinate.means,
            yerr=ordinate.errors,
            xerr=abscissa.errors,
            fmt=style,
            ecolor=color,
            label=label,
        )
    else:
        ax.plot(abscissa.means, ordinate.means, style, color=color, label=label)


def _createLatexDoc(configPath, latexNames) -> _latex.LatexReport:  # type: ignore[name-defined]
    doc = _latex.LatexReport("", "")  # type: ignore[attr-defined]
    if latexNames:
        if ":" in latexNames:
            latexNameFullPath = latexNames
        else:
            latexNameFullPath = _os.path.join(configPath, latexNames)
        doc.getLatexNamesDict(file=latexNameFullPath)
    else:
        doc.getLatexNamesDict()
    return doc


def _getSeriesColors(numberOfSeries: int) -> _tp.Sequence[_tp.Any]:
    colors = _plt.rcParams["axes.prop_cycle"].by_key()["color"]
    nColors = len(colors)

    seriesColors = [colors[i % nColors] for i in range(numberOfSeries)]

    return seriesColors


def _setLegendsAndLabels(
    fig, ax, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, chunkLabels, dummyLines, doc
):  # pylint: disable=too-many-arguments
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
    shallPrintDataForGle,
    shallPlotUncertainties,
    extensionFig,
):  # pylint: disable=too-many-arguments
    fileName = _getFileName(
        xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditionsFileNamePart, comparePlotUserName
    )

    fig.savefig(_os.path.join(pathFolder, fileName + extensionFig), bbox_inches="tight")
    _plt.close()

    if shallPrintDataForGle:
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
