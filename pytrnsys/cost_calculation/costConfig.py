#!/usr/bin/env python

"""
Child class from costClass customized for general calculation with config file

Author : Dani Carbonell
Last Change: Jeremias Schmidli
Date : 07.04.2020
"""

import json
import logging
import os
import pathlib as _pl

import matplotlib as mpl
from matplotlib import pyplot as plt

from pytrnsys.report import latexReport as latex
from . import _cost_table as _ct
from . import createOutput as _co
from ._models import input as _input
from ._models import output as _output

logger = logging.getLogger('root')


class costConfig:
    _SHALL_USE_kCHF_FOR_TOTAL_COSTS = False

    # public: used
    def __init__(self):
        self.method = "VDI"
        self.cleanModeLatex = None

        self.readCompleteFolder = True
        self.fileNameList = None

    def setFileNameList(self, fileNameList):
        self.fileNameList = fileNameList
        self.readCompleteFolder = False

    @staticmethod
    def readCostJson(path):

        with open(path) as json_file:
            dictCost = json.load(json_file)

        return dictCost

    def process(self, configFilePath: _pl.Path, resultsDirPath: _pl.Path):
        config = _input.Input.from_dict(self.readCostJson(configFilePath))
        resultOutputs = _co.createOutputs(config, resultsDirPath, self.readCompleteFolder, self.fileNameList)

        self.investVec = []
        self.annuityVec = []

        for resultOutput in resultOutputs:
            self._processResult(config.parameters, resultOutput, resultsDirPath)

    @staticmethod
    def setFontSizes(small):
        SMALL_SIZE = small
        MEDIUM_SIZE = SMALL_SIZE + 2
        BIGGER_SIZE = MEDIUM_SIZE + 2

        plt.rc('font', size=SMALL_SIZE)  # controls default text sizes
        plt.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
        plt.rc('axes', labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

    # public: unused (?)
    def printDataFile(self):
        for bat in self.batList:

            lines = ""
            line = "!pvPeak\tBatsize\t investment\tAnnuity\tPvGen\n"
            lines = lines + line
            line = "!kW\t \tkWh \t kFr\t CHF/kWh\t-\n"
            lines = lines + line

            for i in range(len(self.pvAreaVec)):
                if self.batSizeVec[i] == bat:
                    line = "%f\t%f\t%f\t%f\t%f\n" % (self.pvAreaVec[i], self.batSizeVec[i],
                                                     self.investVec[i], self.annuityVec[i], self.RpvGenVec[i])
                    lines = lines + line
            fileName = "cost-batkWh%.0f" % bat
            myFileName = self.resClass.path + "\\%s.dat" % fileName

            logger.debug("%s file created" % myFileName)

            outfile = open(myFileName, 'w')
            outfile.writelines(lines)
            outfile.close()

    def plotLines(self, varXAxis, nameXAxis, varYAxis, nameYAxis, varDiffLines, nameLines, nameFig, extension="pdf"):
        fig, ax = plt.subplots(figsize=(16, 8))

        legendList = []

        xList = sorted(list(set(varXAxis)))
        lineList = sorted(list(set(varDiffLines)))

        for i in range(len(lineList)):

            varVec = []
            xVec = []

            legendList.append("%s=%s" % (nameLines, lineList[i]))

            for j in range(len(xList)):

                for k in range(len(self.annuityVec)):
                    if varXAxis[k] == xList[j] and varDiffLines[k] == lineList[i]:
                        xVec.append(xList[j])
                        varVec.append(varYAxis[k])

            ax.plot(xVec, varVec, marker='o')

        ax.legend(legendList)
        ax.set(xlabel=nameXAxis, ylabel=nameYAxis)

        ax.grid()

        fig.show()

        figureName = "%s.%s" % (nameFig, extension)

        plotName = os.path.join(self.resClass.path, figureName)

        fig.savefig(plotName)

    def plotVsPv(self, extension="pdf"):
        fig, ax = plt.subplots(figsize=(16, 8))

        legendList = []

        pvList = sorted(list(set(self.pvAreaVec)))
        batList = sorted(list(set(self.batSizeVec)))

        for i in range(len(batList)):

            varVec = []
            areaVec = []

            legendList.append("Bat-Size=%s kWh" % batList[i])

            for j in range(len(pvList)):

                for k in range(len(self.annuityVec)):
                    if self.pvAreaVec[k] == pvList[j] and self.batSizeVec[k] == batList[i]:
                        areaVec.append(pvList[j])
                        varVec.append(self.annuityVec[k])

            varSorted = varVec
            areaSorted = areaVec

            ax.plot(areaSorted, varSorted)

        ax.legend(legendList)
        ax.set(xlabel='PV [kWp]', ylabel=r'Energy cost [\Euro/kWh]')

        ax.grid()

        fig.show()
        ax.grid()

        figureName = "Annuity_vs_PvPeak.%s" % extension

        plotName = os.path.join(self.resClass.path, figureName)

        fig.savefig(plotName)

    def plotVsBat(self, extension="pdf"):
        fig, ax = plt.subplots(figsize=(16, 8))

        legendList = []

        pvList = sorted(list(set(self.pvAreaVec)))
        batList = sorted(list(set(self.batSizeVec)))

        for i in range(len(pvList)):

            varVec = []
            batVec = []

            legendList.append("Pv_p=%s kWh" % pvList[i])

            for j in range(len(batList)):

                for k in range(len(self.annuityVec)):
                    if self.pvAreaVec[k] == pvList[i] and self.batSizeVec[k] == batList[j]:
                        batVec.append(batList[j])
                        varVec.append(self.annuityVec[k])

            varSorted = varVec
            batSorted = batVec

            ax.plot(batSorted, varSorted, marker='o')

        ax.legend(legendList)

        ax.set(xlabel='Battery [kWh]', ylabel='Energy cost [Euro/kWh]')

        ax.grid()

        fig.show()
        ax.grid()

        figureName = "Annuity_vs_Bat.%s" % extension

        plotName = os.path.join(self.resClass.path, figureName)

        fig.savefig(plotName)

    # private
    def _processResult(self, parameters: _input.Parameters, resultOutput: _co.ResultOutput, resultsDirPath: _pl.Path):
        fileName = str(resultOutput.resultsDir)
        outputPath = os.path.join(str(resultsDirPath), fileName)

        self._setOutputPathAndFileName(outputPath, fileName)

        self.investVec.append(resultOutput.output.componentGroups.cost.mean)
        self.annuityVec.append(resultOutput.output.heatGenerationCost)

        self._generateOutputs(parameters, outputPath, resultOutput.output)

    def _generateOutputs(self, parameters: _input.Parameters, outputPath, output: _output.Output):
        self._doPlots(output.componentGroups)
        self._doPlotsAnnuity(output)
        self._createLatex(parameters, output)

        self._addCostsToResultJson(output, outputPath)

    def _addCostsToResultJson(self, output: _output.Output, outputPath):
        costDict = self._createCostDict(output)
        resultJsonPath = os.path.join(outputPath, self.fileName + '-results.json')
        with open(resultJsonPath, 'r') as resultsJson:
            oldResults = json.load(resultsJson)
        self._addCostToJson(costDict, oldResults, resultJsonPath)

    def _createCostDict(self, output: _output.Output):
        collectorComponents = [c for g in output.componentGroups.groups
                               for c in g.components.factors if c.name == "Collector"]
        if not collectorComponents:
            raise RuntimeError("No `Collector' component found.")

        if len(collectorComponents) > 1:
            raise RuntimeError("More than one `Collector' component found.")

        collectorComponent = collectorComponents[0]
        size = collectorComponent.value

        totalCost = output.componentGroups.cost.mean

        return {
            "investment": totalCost,
            "energyCost": output.heatGenerationCost.mean,
            "investmentPerM2": totalCost / size.value,
            "investmentPerMWh": totalCost * 1000 / output.heatingDemand
        }

    # plots

    def _doPlots(self, componentGroups: _output.ComponentGroups) -> None:
        groupNamesWithCost = [(g.name, g.components.cost.mean) for g in componentGroups.groups]

        groupNames, groupCosts = zip(*groupNamesWithCost)
        self.nameCostPdf = self._plotCostShare(groupCosts, groupNames, "costShare" + "-" + self.fileName,
                                               sizeFont=30, plotJpg=False, writeFile=False)

    def _doPlotsAnnuity(self, output: _output.Output):
        legends = []
        inVar = []

        inVar.append(output.componentGroups.annuity.mean)
        legends.append("Capital cost")

        inVar.append(output.componentGroups.maintenanceCost.mean)
        legends.append("Maintenance")

        inVar.append(output.electricity.annuity)
        legends.append("El. purchased \n from the grid")

        for yearlyCost in output.yearlyCosts.factors:
            name = yearlyCost.name
            cost = yearlyCost.cost.mean

            logger.debug("cost:%f name:%s", cost, name)

            if cost > 0:
                inVar.append(cost)
                if name == "Transmission grid":
                    legends.append("El. transmitted \n through the \n grid")
                elif name == "Aluminium fuel":
                    legends.append("Fuel cost \n (Al regeneration)")
                else:
                    legends.append(name)

        self.nameCostAnnuityPdf = self._plotCostShare(inVar, legends, "costShareAnnuity" + "-" + self.fileName,
                                                      plotSize=17, sizeFont=30, plotJpg=False, writeFile=False)

    def _plotCostShare(self, inVar, legends, nameFile, plotSize=15, sizeFont=15, plotJpg=False, writeFile=False):
        mpl.rcParams['font.size'] = sizeFont

        fig = plt.figure(1, figsize=(plotSize, plotSize))

        fig.add_subplot(111)

        total = sum(inVar)

        myColors = ['#66CCFF', '#336699', '#FFCC00', '#3366CC', '#66FF66', '#FF9966', '#FF9933', '#CCFF33', '#CCFFFF',
                    '#FF9933']

        fracs = []
        colors = []
        explode = []
        for i in range(len(inVar)):
            fracs.append(inVar[i] / total)
            colors.append(myColors[i])
            explode.append(0.)  # (0.05)

        patches, texts, autotexts = plt.pie(fracs, labels=legends, explode=explode, colors=colors, autopct='%1.1f%%',
                                            shadow=False, startangle=0)

        for i in range(len(texts)):
            texts[i].set_fontsize(sizeFont)

        plt.title("", bbox={'facecolor': '0.9', 'pad': 10}, fontsize=sizeFont)

        namePdf = '%s.pdf' % nameFile
        nameWithPath = '%s\\%s' % (self.outputPath, namePdf)

        plt.savefig(nameWithPath)

        if plotJpg:
            nameJpg = '%s.jpg' % nameFile

            nameJpgWithPath = '%s\\%s' % (self.outputPath, nameJpg)
            logger.info("Plot printed as %s" % nameJpgWithPath)

            plt.savefig(nameJpgWithPath)

        plt.close()

        if writeFile:
            lines = ""
            line = "!Units kFr.\n"
            lines = lines + line
            line = "!"
            lines = lines + line
            for i in range(len(legends)):
                line = "%s\t" % legends[i]
                lines = lines + line
            line = "\n"
            lines = lines + line

            for i in range(len(legends)):
                sumVar = inVar[i] / 1000.  # I assume Fr. and change to kFr. !!!!

                line = "%f\t" % sumVar
                lines = lines + line
            line = "\n"
            lines = lines + line
            nameDat = '%s.dat' % nameFile
            nameDatWithPath = '%s\\%s' % (self.outputPath, nameDat)

            logger.info("PRINT FILE COST SHARE : %s" % nameDatWithPath)
            outfile = open(nameDatWithPath, 'w')
            outfile.writelines(lines)
            outfile.close()

        return namePdf

    # latex

    def _createLatex(self, parameters: _input.Parameters, output: _output.Output):
        fileName = self.fileName + "-cost"
        self.doc.resetTexName(fileName)

        self.doc.setSubTitle("Energy generation costs")

        self.doc.setTitle(self.fileName)

        self.doc.setCleanMode(self._getIsLatexCleanMode(parameters))
        self.doc.addBeginDocument()
        self._addTableEconomicAssumptions(parameters, output)
        self._addTableCosts(self.doc, output)

        try:
            self.doc.addPlot(self.nameCostPdf, "System cost", "systemCost", 13)
            self.doc.addPlot(self.nameCostAnnuityPdf, "System cost annuity share", "systemCostannuity", 13)
        except:
            pass

        self.doc.addEndDocumentAndCreateTexFile()
        self.doc.executeLatexFile()

    def _getIsLatexCleanMode(self, parameters):
        return parameters.cleanModeLatex if self.cleanModeLatex is None else self.cleanModeLatex

    def _addTableEconomicAssumptions(self, parameters: _input.Parameters, output: _output.Output):
        caption = "Assumptions for calculation of heat generation costs"
        names = ["", "", "", ""]
        units = None

        perc = "\\%"

        lines = ""
        line = "Rate & %2.1f %s $per$ $annum$\\\\ \n" % (parameters.rate * 100., perc)
        lines = lines + line
        line = "Analysis period & %2.0f $years$\\\\ \n" % parameters.analysisPeriod
        lines = lines + line
        line = "Maintenance & %2.1f %s $of$ $Investment$ $costs$ $per$ $year$ \\\\ \n" % (
            parameters.maintenanceRate * 100., perc)
        lines = lines + line
        line = "\\hline \\\\ \n"
        lines = lines + line
        line = "Electricity & Fix costs: %2.0f  $Fr.$ $per$ $year$ \\\\ \n" % parameters.costElecFix
        lines = lines + line
        line = " & Variable costs:  %2.2f $Fr.$ $per$ $kWh$ \\\\ \n" % parameters.costElecKWh
        lines = lines + line
        line = "Increase of electricity costs & %2.1f %s $per$ $year$ \\\\ \n" % (parameters.increaseElecCost * 100., perc)
        lines = lines + line
        line = "Electricity costs year 1 & %2.0f Fr. in year 1 \\\\ \n" % output.electricity.cost
        lines = lines + line

        label = "definitionTable"

        self.doc.addTable(caption, names, units, label, lines, useFormula=True)

    def _addTableCosts(self, doc, output: _output.Output):
        lines = _ct.createLines(output, self._SHALL_USE_kCHF_FOR_TOTAL_COSTS)

        caption = r"System and Heat generation costs (all values incl. 8$\%$ VAT) "
        names = ["Group", "Component", "Costs", "Size", "LifeTime", "Total Costs"]
        units = self._getUnitsForAnnuityPlot()
        label = "CostsTable"

        doc.addTable(caption, names, units, label, lines, useFormula=False)

    def _getUnitsForAnnuityPlot(self):
        if self._SHALL_USE_kCHF_FOR_TOTAL_COSTS:
            units = ["", "", "[CHF]", "", "", "[kCHF]"]
        else:
            units = ["", "", "[CHF]", "", "Years", "[CHF]"]
        return units

    # misc

    def _setOutputPathAndFileName(self, path, fileName):
        self.outputPath = path
        self.fileName = fileName

        logger.debug("path:%s name:%s" % (self.outputPath, self.fileName))
        self.doc = latex.LatexReport(self.outputPath, self.fileName)

    @staticmethod
    def _addCostToJson(costResultsDict, resultsDict, jsonPath):

        logger.debug("updating results.json file")

        newResultsDict = {**resultsDict, **costResultsDict}

        with open(jsonPath, 'w') as fp:
            json.dump(newResultsDict, fp, indent=2, separators=(',', ': '), sort_keys=True)

        logger.info("results.json file was updated with cost data")
