import pytrnsys.psim.conditions as _conds


class Comparison:
    @staticmethod
    def createPlot(plotVariables, pathFolder, typeOfProcess, logger, latexNames, configPath,
                   stylesheet, plotStyle, comparePlotUserName, setPrintDataForGle):
        if len(plotVariables) < 2:
            raise ValueError(
                'You did not specify variable names and labels for the x and the y Axis in a compare Plot line')
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

        plotXDict = {}
        plotYDict = {}

        seriesColors = {}
        colorsCounter = 0
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        if typeOfProcess == "json":
            resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)
        else:
            resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"))

        if not resultFiles:
            logger.error('No results.json-files found.')
            logger.error(
                'Unable to generate "comparePlot %s %s %s"' % (xAxisVariable, yAxisVariable, seriesVariable))
            return

        conditionNeverMet = True

        for file in resultFiles:
            with open(file) as f_in:
                resultsDict = json.load(f_in)
                resultsDict[''] = None

            conditionsFulfilled = conditions.doResultsSatisfyConditions(resultsDict)

            if conditionsFulfilled:

                conditionNeverMet = False

                if resultsDict[seriesVariable] not in seriesColors.keys():
                    seriesColors[resultsDict[seriesVariable]] = colors[colorsCounter]
                    colorsCounter += 1
                    colorsCounter = colorsCounter % len(colors)

                if '[' not in xAxisVariable:
                    xAxis = resultsDict[xAxisVariable]
                else:
                    name, index = str(xAxisVariable).split('[')
                    index = int(index.replace(']', ''))
                    xAxis = resultsDict[name][index]
                if '[' not in yAxisVariable:
                    yAxis = resultsDict[yAxisVariable]
                else:
                    name, index = str(yAxisVariable).split('[')
                    index = int(index.replace(']', ''))
                    yAxis = resultsDict[name][index]
                if resultsDict[chunkVariable] not in plotXDict.keys():
                    plotXDict[resultsDict[chunkVariable]] = {}
                    plotYDict[resultsDict[chunkVariable]] = {}
                    plotXDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [xAxis]
                    plotYDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [yAxis]
                elif resultsDict[seriesVariable] not in plotXDict[resultsDict[chunkVariable]].keys():
                    plotXDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [xAxis]
                    plotYDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [yAxis]
                else:
                    plotXDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]].append(xAxis)
                    plotYDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]].append(yAxis)

        if conditionNeverMet:
            logger.warning(
                'The following conditions from "comparePlotConditional" were never met all at once:')
            for condition in conditions.conditions:
                logger.warning(condition)
            logger.warning('The respective plot cannot be generated')
            return

        doc = latex.LatexReport('', '')
        if latexNames:
            if ':' in latexNames:
                latexNameFullPath = latexNames
            else:
                latexNameFullPath = os.path.join(configPath, latexNames)
            doc.getLatexNamesDict(file=latexNameFullPath)
        else:
            doc.getLatexNamesDict()

        if not stylesheet:
            stylesheet = 'word.mplstyle'
        if stylesheet not in plt.style.available:
            root = os.path.dirname(os.path.abspath(__file__))
            stylesheet = os.path.join(root, r"..\\plot\\stylesheets", stylesheet)

        plt.style.use(stylesheet)

        fig1, ax1 = plt.subplots(constrained_layout=True)
        if plotStyle == "line":
            styles = ['x-', 'x--', 'x-.', 'x:', 'o-', 'o--', 'o-.', 'o:']
        elif plotStyle == "dot":
            styles = ['x', 'o', '+', 'd', 's', 'v', '^', 'h']
        else:
            logger.error("Invalid 'plotStyle' argument")

        dummy_lines = []
        chunkLabels = []
        labelSet = set()
        lines = ""
        for chunk, style in zip(plotXDict.keys(), styles):
            dummy_lines.append(ax1.plot([], [], style, c='black'))
            if chunk is not None:
                if not isinstance(chunk, str):
                    chunkLabel = round(float(chunk), 2)
                    chunkLabels.append("{:.2f}".format(chunkLabel))
                else:
                    chunkLabels.append(chunk)

            for key in plotXDict[chunk].keys():
                index = num.argsort(plotXDict[chunk][key])
                myX = num.array(plotXDict[chunk][key])[index]
                myY = num.array(plotYDict[chunk][key])[index]

                mySize = len(myX)

                if key is not None and not isinstance(key, str):
                    labelValue = round(float(key), 2)
                elif key is not None:
                    labelValue = key
                if key is not None and labelValue not in labelSet:
                    if not isinstance(labelValue, str):
                        label = "{0:.1f}".format(labelValue)
                    else:
                        label = labelValue
                        label = doc.getNiceLatexNames(label)

                    labelSet.add(labelValue)
                    ax1.plot(myX, myY,
                             style, color=seriesColors[key], label=label)
                else:
                    ax1.plot(myX, myY,
                             style, color=seriesColors[key])

        lines = "!%s\t" % seriesVariable
        for chunk, style in zip(plotXDict.keys(), styles):
            for key in plotXDict[chunk].keys():  # the varables that appear in the legend
                line = "%s\t" % key;
                lines = lines + line
            line = "\n";
            lines = lines + line

        for i in range(mySize):
            for chunk, style in zip(plotXDict.keys(), styles):

                for key in plotXDict[chunk].keys():  # the varables that appear in the legend
                    index = num.argsort(plotXDict[chunk][key])
                    myX = num.array(plotXDict[chunk][key])[index]
                    myY = num.array(plotYDict[chunk][key])[index]

                    if (len(myY) > i):
                        if type(myX[i]) == num.str_ and type(myY[i]) == num.str_:
                            line = myX[i] + "\t" + myY[i] + "\t"
                        elif type(myX[i]) == num.str_:
                            line = myX[i] + "\t" + "%8.4f\t" % myY[i]
                        elif type(myY[i]) == num.str_:
                            line = "%8.4f\t" % myX[i] + myX[i] + "\t"
                        else:
                            line = "%8.4f\t%8.4f\t" % (myX[i], myY[i]);
                        lines = lines + line
                    else:
                        pass

            line = "\n";
            lines = lines + line

        if chunkVariable !='':
            legend2 = fig1.legend([dummy_line[0] for dummy_line in dummy_lines], chunkLabels,
                                  title=doc.getNiceLatexNames(chunkVariable), bbox_to_anchor=(1.31, 1.0),
                                  bbox_transform=ax1.transAxes)

        else:
            legend2 = None
        if seriesVariable !='':
            legend1 = fig1.legend(title=doc.getNiceLatexNames(seriesVariable), bbox_to_anchor=(1.15, 1.0),
                                  # change legend position!
                                  bbox_transform=ax1.transAxes)

        else:
            legend1 = None
        ax1.set_xlabel(doc.getNiceLatexNames(xAxisVariable))
        ax1.set_ylabel(doc.getNiceLatexNames(yAxisVariable))

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

        if conditionsTitle:
            ax1.set_title(conditionsTitle)

        if legend2 is not None:
            fig1.add_artist(legend2)

        fileName = xAxisVariable + '_' + yAxisVariable + '_' + seriesVariable

        if chunkVariable:
             fileName += '_' + chunkVariable

        if conditionsFileName:
            fileName += '_' + conditionsFileName

        if comparePlotUserName:
            fileName += '_' + comparePlotUserName

        fig1.savefig(os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
        plt.close()

        if setPrintDataForGle:
            outfile = open(os.path.join(pathFolder, fileName + '.dat'), 'w')
            outfile.writelines(lines)
            outfile.close()
