import os as _os
import json as _json
import typing as _tp
import pathlib as _pl

import matplotlib.pyplot as _plt
import numpy as _np

import pytrnsys.psim.conditions as _conds
import pytrnsys.report.latexReport as _latex


def createPlot(plotVariables, pathFolder, typeOfProcess, logger, latexNames, configPath,
               stylesheet, plotStyle, comparePlotUserName, setPrintDataForGle):
    xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions = \
        _separatePlotVariables(plotVariables)

    resultFilePaths = _getResultsFilePaths(pathFolder, typeOfProcess)
    if not resultFilePaths:
        logger.error('No results.json-files found.')
        logger.error('Unable to generate "comparePlot %s %s %s"',
                     xAxisVariable, yAxisVariable, seriesVariable)
        return

    values = _loadValues(resultFilePaths, xAxisVariable, yAxisVariable,
                         chunkVariable, seriesVariable, conditions)
    if not values:
        logger.warning('The following conditions from "comparePlotConditional" were never met all at once:')
        for condition in conditions.conditions:
            logger.warning(condition)
        logger.warning('The respective plot cannot be generated.')
        return

    _configurePyplotStyle(stylesheet)

    styles = ['x-', 'x--', 'x-.', 'x:', 'o-', 'o--', 'o-.', 'o:']
    if plotStyle == "dot":
        styles = ['x', 'o', '+', 'd', 's', 'v', '^', 'h']

    if len(values) > len(styles):
        raise AssertionError("Too many chunks")

    seriesColors = _getSeriesColors(values)

    doc = _createLatexDoc(configPath, latexNames)

    fig, ax = _plt.subplots(constrained_layout=True)

    chunkLabels, dummyLines = _plotValues(ax, values, seriesColors, styles, doc)

    _setLegendsAndLabels(fig, ax, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable,
                         chunkLabels, dummyLines, doc)

    conditionsFileNamePart, conditionsTitle = _getConditionsFileNameAndTitle(conditions)

    if conditionsTitle:
        ax.set_title(conditionsTitle)

    _savePlotAndData(fig, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, pathFolder, comparePlotUserName,
                     conditionsFileNamePart, values, setPrintDataForGle, styles)


def _savePlotAndData(fig, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, pathFolder, comparePlotUserName,
                     conditionsFileNamePart, values, setPrintDataForGle, styles):
    fileName = _getFileName(xAxisVariable, yAxisVariable, seriesVariable,
                            chunkVariable, conditionsFileNamePart, comparePlotUserName)
    fig.savefig(_os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
    _plt.close()
    if setPrintDataForGle:
        _doPrintDataForGle(fileName, pathFolder, values, seriesVariable, styles)


def _setLegendsAndLabels(fig, ax, xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, chunkLabels, dummyLines,
                         doc):
    if chunkVariable:
        legend = fig.legend([dummy_line[0] for dummy_line in dummyLines], chunkLabels,
                            title=doc.getNiceLatexNames(chunkVariable), bbox_to_anchor=(1.31, 1.0),
                            bbox_transform=ax.transAxes)
        fig.add_artist(legend)
    if seriesVariable:
        legend = fig.legend(title=doc.getNiceLatexNames(seriesVariable), bbox_to_anchor=(1.15, 1.0),
                            bbox_transform=ax.transAxes)
        fig.add_artist(legend)
    ax.set_xlabel(doc.getNiceLatexNames(xAxisVariable))
    ax.set_ylabel(doc.getNiceLatexNames(yAxisVariable))


def _plotValues(ax, values, seriesColors, styles, doc):
    dummyLines = []
    chunkLabels = []
    seriesLabels = set()
    for chunkVariableValue, style in zip(values, styles):
        dummyLines.append(ax.plot([], [], style, c='black'))
        chunkLabel = _getChunkLabel(chunkVariableValue)

        if chunkLabel:
            chunkLabels.append(chunkLabel)

        chunk = values[chunkVariableValue]
        for seriesVariableValue in chunk:
            series = chunk[seriesVariableValue]

            xs, ys = _getXsAndYsSortedByXs(series)

            label = _getSeriesLabel(seriesVariableValue, seriesLabels, doc)

            if label:
                ax.plot(xs, ys, style, color=seriesColors[seriesVariableValue], label=label)
            else:
                ax.plot(xs, ys, style, color=seriesColors[seriesVariableValue])
    return chunkLabels, dummyLines


def _configurePyplotStyle(stylesheet):
    if not stylesheet:
        stylesheet = 'word.mplstyle'
    if stylesheet not in _plt.style.available:
        root = _os.path.dirname(_os.path.abspath(__file__))
        stylesheet = _os.path.join(root, r"..\\plot\\stylesheets", stylesheet)
    _plt.style.use(stylesheet)


def _createLatexDoc(configPath, latexNames):
    doc = _latex.LatexReport('', '')
    if latexNames:
        if ':' in latexNames:
            latexNameFullPath = latexNames
        else:
            latexNameFullPath = _os.path.join(configPath, latexNames)
        doc.getLatexNamesDict(file=latexNameFullPath)
    else:
        doc.getLatexNamesDict()
    return doc


def _getChunkLabel(chunkVariableValue):
    if chunkVariableValue is None:
        return None

    if isinstance(chunkVariableValue, str):
        return chunkVariableValue

    roundedValue = round(float(chunkVariableValue), 2)
    return "{:.2f}".format(roundedValue)


def _getFileName(xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditionsFileName, comparePlotUserName):
    fileName = xAxisVariable + '_' + yAxisVariable + '_' + seriesVariable
    if chunkVariable:
        fileName += '_' + chunkVariable
    if conditionsFileName:
        fileName += '_' + conditionsFileName
    if comparePlotUserName:
        fileName += '_' + comparePlotUserName
    return fileName


def _getSeriesLabel(seriesVariableValue, labelSet, doc):
    if seriesVariableValue is None:
        return None

    labelValue = seriesVariableValue if isinstance(seriesVariableValue, str) \
        else round(float(seriesVariableValue), 2)

    if labelValue in labelSet:
        return None

    labelSet.add(labelValue)

    if not isinstance(labelValue, str):
        label = "{0:.1f}".format(labelValue)
    else:
        label = doc.getNiceLatexNames(labelValue)

    return label


def _getConditionsFileNameAndTitle(conditions):
    conditionsFileName = ''
    conditionsTitle = ''
    for condition in conditions.conditions:
        conditionsFileName += condition.serializedCondition
        if conditionsTitle != '':
            conditionsTitle += ', ' + condition.serializedCondition
        else:
            conditionsTitle += condition.serializedCondition
    conditionsTitle = conditionsTitle.replace('RANGE', '')
    conditionsTitle = conditionsTitle.replace('LIST', '')
    conditionsFileName = conditionsFileName.replace('==', '=')
    conditionsFileName = conditionsFileName.replace('>', '_g_')
    conditionsFileName = conditionsFileName.replace('<', '_l_')
    conditionsFileName = conditionsFileName.replace('>=', '_ge_')
    conditionsFileName = conditionsFileName.replace('<=', '_le_')
    conditionsFileName = conditionsFileName.replace('|', '_o_')
    conditionsFileName = conditionsFileName.replace('RANGE:', '')
    conditionsFileName = conditionsFileName.replace('LIST:', '')
    return conditionsFileName, conditionsTitle


def _doPrintDataForGle(fileName, pathFolder, values, seriesVariable, styles):
    lines = "!%s\t" % seriesVariable
    for chunkVariableValue, style in zip(values, styles):
        chunk = values[chunkVariableValue]
        for seriesVariableValue in chunk:
            line = "%s\t" % seriesVariableValue
            lines = lines + line
        line = "\n"
        lines = lines + line

    maxSeriesLength = max(len(s) for c in values.values() for s in c.values())
    for i in range(maxSeriesLength):
        for chunk in values.values():
            for series in chunk.values():
                if len(series) <= i:
                    continue

                xs, ys = _getXsAndYsSortedByXs(series)
                x = xs[i]
                y = ys[i]

                formattedX = _format(x)
                formattedY = _format(y)

                line = f"{formattedX}\t{formattedY}\t"

                lines += line

        lines += "\n"

        datFilePath = _pl.Path(pathFolder) / f"{fileName}.dat"
        datFilePath.write_text(lines)


def _format(u):
    if isinstance(u, str):
        return u

    return f"{u:8.4f}"


def _getXsAndYsSortedByXs(series):
    myX, myY = [_np.array(vs) for vs in zip(*series)]
    index = _np.argsort(myX)
    myX = myX[index]
    myY = myY[index]
    return myX, myY


def _getSeriesColors(values):
    colors = _plt.rcParams['axes.prop_cycle'].by_key()['color']
    series = {s for (c, vs) in values.items() for s in vs}
    seriesColors = {s: colors[i % len(colors)] for i, s in enumerate(series)}
    return seriesColors


def _loadValues(resultFilePaths, xAxisVariable, yAxisVariable,
                chunkVariable, seriesVariable, conditions) \
        -> _tp.Dict[str, _tp.Dict[str, _tp.Sequence[float]]]:
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

    return values


def _loadResults(resultFilePath) -> _tp.Dict[str, _tp.Any]:
    serializedResults = resultFilePath.read_text()
    resultsDict = _json.loads(serializedResults)
    return resultsDict


def _getValue(resultsDict, yAxisVariable):
    if '[' not in yAxisVariable:
        yAxis = resultsDict[yAxisVariable]
    else:
        name, index = str(yAxisVariable).split('[')
        index = int(index.replace(']', ''))
        yAxis = resultsDict[name][index]
    return yAxis


def _getResultsFilePaths(pathFolder, typeOfProcess) -> _tp.Sequence[_pl.Path]:
    pathFolder = _pl.Path(pathFolder)
    pattern = "*-results.json"

    if typeOfProcess == "json":
        return list(pathFolder.rglob(pattern))

    return list(pathFolder.glob(pattern))


def _separatePlotVariables(plotVariables):
    if len(plotVariables) < 2:
        raise ValueError('You did not specify variable names and labels '
                         'for the x and the y Axis in a compare Plot line')
    xAxisVariable = plotVariables[0]
    yAxisVariable = plotVariables[1]
    chunkVariable = ''
    seriesVariable = ''
    serializedConditions = plotVariables[2:]
    if len(plotVariables) >= 3 and not _conds.mayBeSerializedCondition(plotVariables[2]):
        seriesVariable = plotVariables[2]
        serializedConditions = plotVariables[3:]
    if len(plotVariables) >= 4 and not _conds.mayBeSerializedCondition(plotVariables[3]):
        chunkVariable = plotVariables[3]
        serializedConditions = plotVariables[4:]
    conditions = _conds.createConditions(serializedConditions)
    return xAxisVariable, yAxisVariable, seriesVariable, chunkVariable, conditions
