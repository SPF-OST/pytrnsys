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
import typing as _tp
import matplotlib as mpl
from matplotlib import pyplot as plt

import pytrnsys.psim.resultsProcessedFile as results
from pytrnsys.cost_calculation import _economicFunctions as _ef
from pytrnsys.report import latexReport as latex

from ._models import input as _input
from ._models import output as _output
from ._models import common as _common
from . import _costTable as _ct

logger = logging.getLogger('root')


class costConfig:
    _USE_kCHF_FOR_TOTAL_COSTS = False

    # public: used
    def __init__(self):
        self.method = "VDI"
        self.cleanModeLatex = True

        self._input: _tp.Optional[_input.Input] = None
        self._output: _tp.Optional[_output.Output] = None
        self._valuesByVariable: _tp.Dict[_input.Variable, float] = {}

        self.rate = 0.
        self.analysPeriod = 0.
        self.costElecFix = 0.
        self.costEleckWh = 0.
        self.lifeTime = 0.
        self.increaseElecCost = 0.
        self.elDemand = 0.
        self.totalInvestCost = _common.UncertainFloat.zero()

        self.qDemand = 0.
        self.elDemandTotal = 0.
        self.MaintenanceRate = 0.
        self.costResidual = 0.
        self.lifeTimeResVal = 0.
        self.readCompleteFolder = True
        self.fileNameList = None

    def setFileNameList(self, fileNameList):
        self.fileNameList = fileNameList
        self.readCompleteFolder = False

    def setDefaultData(self, dictCost):
        self.rate = dictCost["parameters"]["rate"]
        self.analysPeriod = dictCost["parameters"]["analysisPeriod"]
        self.costElecFix = dictCost["parameters"]["costElecFix"]
        self.costEleckWh = dictCost["parameters"]["costElecKWh"]
        self.increaseElecCost = dictCost["parameters"]["increaseElecCost"]
        self.MaintenanceRate = dictCost["parameters"]["maintenanceRate"]
        self.costResidual = dictCost["parameters"]["costResidual"]
        self.cleanModeLatex = dictCost["parameters"]["cleanModeLatex"]
        self.lifeTimeResVal = dictCost["parameters"]["lifetimeResVal"]

    def readResults(self, dataPath):
        self.resClass = results.ResultsProcessedFile(dataPath)
        self.resClass.readResultsData(resultType='json', completeFolder=self.readCompleteFolder,
                                      fileNameList=self.fileNameList)

    @staticmethod
    def readCostJson(path):

        with open(path) as json_file:
            dictCost = json.load(json_file)

        return dictCost

    def process(self, dictCost):
        self._input = _input.Input.from_dict(dictCost)

        self.investVec = []
        self.annuityVec = []

        for i in range(len(self.resClass.results)):
            self._processResult(dictCost, i, self._input.componentGroups, self._input.yearlyCosts)

        self._clean()

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
    def _processResult(self, dictCost, i,
                       componentGroups: _tp.Sequence[_input.ComponentGroup],
                       yearlyCosts: _tp.Sequence[_input.YearlyCost]):
        fileName = self.resClass.fileName[i]
        outputPath = os.path.join(self.resClass.path, fileName)

        self._setOutputPathAndFileName(outputPath, fileName)

        self._addComponentSizes(i, componentGroups)

        self.qDemand = self.resClass.results[i].get(dictCost['parameters']['qDemandVariable'])
        self.elFromGrid = self.resClass.results[i].get(dictCost['parameters']['elFromGridVariable'])
        self.elDemandTotal = self.elFromGrid

        self._addYearlySizes(i, yearlyCosts)

        componentGroups = _output.ComponentGroups.createFromValues(self._input.componentGroups,
                                                                   self._valuesByVariable,
                                                                   self._input.parameters.rate)
        yearlyCosts = _output.CostFactors.createForYearlyCosts(self._input.yearlyCosts,
                                                               self._valuesByVariable,
                                                               self._input.parameters.rate,
                                                               self._input.parameters.analysisPeriod)
        self._output = _output.Output(componentGroups, yearlyCosts)

        self._calculate()
        self.investVec.append(self.totalInvestCost.mean)
        self.annuityVec.append(self.heatGenCost)

        self._generateOutputs(i, outputPath, componentGroups, yearlyCosts)

        self._clean()

    def _calculate(self):
        self.totalInvestCost = _common.UncertainFloat.zero()
        size: float
        for i, component in enumerate(c for cg in self._output.componentGroups.groups for c in cg.components.factors):
            logger.debug("ncomp:%d rate:%f lifeTime%f" % (i, self.rate, component.period))
            self.totalInvestCost = self.totalInvestCost + component.cost

        # ===================================================
        # electricity
        # ===================================================

        self.costElecTotalY = self.costElecFix + self.costEleckWh * self.elDemandTotal

        if self.rate == self.increaseElecCost:
            self.npvFacElec = self.analysPeriod / (
                    1. + self.rate)  # DC It was lifeTime but now its different from each other
        else:
            self.npvFacElec = _ef.getNPVIncreaseCost(self.rate, self.analysPeriod, self.increaseElecCost)

        self.npvElec = self.costElecTotalY * self.npvFacElec

        # ===================================================
        # Maintenance cost
        # ===================================================
        self.npvMaintenance = self.MaintenanceRate * self.totalInvestCost.mean \
                              * _ef.getNPV(self.rate, self.analysPeriod)

        # ===================================================
        # Residual Value. Do for all that have a longer life time. What happens with replacement 5 y before
        # analysis period? Should we also add this?
        # ===================================================

        self.discountFromEnd = (1 + self.rate) ** (-1. * self.analysPeriod)
        self.resValFactor = (self.lifeTimeResVal - self.analysPeriod) / self.lifeTimeResVal
        self.residualValue = self.costResidual * self.resValFactor
        self.npvResVal = self.residualValue * self.discountFromEnd

        # ===================================================
        # NET PRESENT VALUE
        # ===================================================

        self.npvSystem = self.totalInvestCost.mean + self._output.yearlyCosts.npvCost.mean \
                         + self.npvElec + self.npvMaintenance - self.npvResVal

        logger.debug("npvSystem:%f totalInvestCost :%f AlMatcost:%f npvElec :%f npvMaintenance:%f npvResVal:%f" % (
            self.npvSystem, self.totalInvestCost.mean, self._output.yearlyCosts.npvCost.mean,
            self.npvElec, self.npvMaintenance, self.npvResVal))

        # ===================================================
        # ANNUITY
        # ===================================================

        self.annuityFac = _ef.getAnnuity(self.rate, self.analysPeriod)

        self.anElec = self.annuityFac * self.npvElec
        self.anMaint = self.MaintenanceRate * self.totalInvestCost.mean  # to use DP method

        self.anResVal = (-1.) * self.annuityFac * self.npvResVal

        self.annuity = self._output.componentGroups.annualizedCost.mean + self.anElec + self.anMaint + self.anResVal \
                       + self._output.yearlyCosts.cost.mean

        logger.info(" AnElectricity:%f npvElec:%f npvFacElec:%f annnuityFac:%f   " % (
            self.anElec, self.npvElec, self.npvFacElec, self.annuityFac))

        self.heatGenCost = self.annuity / self.qDemand  # Fr./kWh

        logger.info("AnnuityFac:%f  " % self.annuityFac)
        logger.info("Heat Generation Cost Annuity:%f " % self.heatGenCost)

    def _generateOutputs(self, i, outputPath,
                         componentGroups: _output.ComponentGroups,
                         yearlyCosts: _output.CostFactors):
        self._doPlots(componentGroups)
        self._doPlotsAnnuity(componentGroups, yearlyCosts)
        self._createLatex()

        self._addCostsToResultJson(componentGroups, i, outputPath)

    def _addCostsToResultJson(self, componentGroups: _output.ComponentGroups, i, outputPath):
        costDict = self._createCostDict(componentGroups)
        resultJsonPath = os.path.join(outputPath, self.fileName + '-results.json')
        self._addCostToJson(costDict, self.resClass.results[i], resultJsonPath)

    def _createCostDict(self, componentGroups: _output.ComponentGroups):
        collectorComponents = [c for g in componentGroups.groups
                               for c in g.components.factors if c.name == "Collector"]
        if not collectorComponents:
            raise RuntimeError("No `Collector' component found.")

        if len(collectorComponents) > 1:
            raise RuntimeError("More than one `Collector' component found.")

        collectorComponent = collectorComponents[0]
        size = collectorComponent.value

        totalCost = self.totalInvestCost.mean

        return {
            "investment": totalCost,
            "energyCost": self.heatGenCost,
            "investmentPerM2": totalCost / size.value,
            "investmentPerMWh": totalCost * 1000 / self.qDemand
        }

    def _addYearlySizes(self, i, yearlyCosts: _tp.Sequence[_input.YearlyCost]):
        for yearlyCost in yearlyCosts:
            variable = yearlyCost.variable
            size = self.resClass.results[i].get(variable.name)
            self._valuesByVariable[variable] = size

    def _addComponentSizes(self, i, componentGroups: _tp.Sequence[_input.ComponentGroup]):
        for group in componentGroups:
            for component in group.components:
                variable = component.variable
                size = self.resClass.results[i].get(variable.name)
                self._valuesByVariable[variable] = size

    def _clean(self):
        self._valuesByVariable = {}

    # plots

    def _doPlots(self, componentGroups: _output.ComponentGroups) -> None:
        groupNamesWithCost = [(g.name, g.components.cost.mean) for g in componentGroups.groups]

        groupNames, groupCosts = zip(*groupNamesWithCost)
        self.nameCostPdf = self._plotCostShare(groupCosts, groupNames, "costShare" + "-" + self.fileName,
                                               sizeFont=30, plotJpg=False, writeFile=False)

    def _doPlotsAnnuity(self, componentGroups: _output.ComponentGroups, yearlyCosts: _output.CostFactors):
        legends = []
        inVar = []

        inVar.append(componentGroups.annualizedCost.mean)
        legends.append("Capital cost")

        inVar.append(self.anMaint)
        legends.append("Maintenance")

        inVar.append(self.anElec)
        legends.append("El. purchased \n from the grid")

        for yearlyCost in yearlyCosts.factors:
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

    def _createLatex(self):
        fileName = self.fileName + "-cost"
        self.doc.resetTexName(fileName)

        self.doc.setSubTitle("Energy generation costs")

        self.doc.setTitle(self.fileName)

        self.doc.setCleanMode(self.cleanModeLatex)
        self.doc.addBeginDocument()
        self._addTableEconomicAssumptions()
        self._addTableCosts(self.doc)

        try:
            self.doc.addPlot(self.nameCostPdf, "System cost", "systemCost", 13)
            self.doc.addPlot(self.nameCostAnnuityPdf, "System cost annuity share", "systemCostannuity", 13)
        except:
            pass

        self.doc.addEndDocumentAndCreateTexFile()
        self.doc.executeLatexFile()

    def _addTableEconomicAssumptions(self):
        caption = "Assumptions for calculation of heat generation costs"
        names = ["", "", "", ""]
        units = None

        perc = "\\%"

        lines = ""
        line = "Rate & %2.1f %s $per$ $annum$\\\\ \n" % (self.rate * 100., perc)
        lines = lines + line
        line = "Analysis period & %2.0f $years$\\\\ \n" % self.analysPeriod
        lines = lines + line
        line = "Maintenance & %2.1f %s $of$ $Investment$ $costs$ $per$ $year$ \\\\ \n" % (
            self.MaintenanceRate * 100., perc)
        lines = lines + line
        line = "\\hline \\\\ \n"
        lines = lines + line
        line = "Electricity & Fix costs: %2.0f  $Fr.$ $per$ $year$ \\\\ \n" % self.costElecFix
        lines = lines + line
        line = " & Variable costs:  %2.2f $Fr.$ $per$ $kWh$ \\\\ \n" % self.costEleckWh
        lines = lines + line
        line = "Increase of electricity costs & %2.1f %s $per$ $year$ \\\\ \n" % (self.increaseElecCost * 100., perc)
        lines = lines + line
        line = "Electricity costs year 1 & %2.0f Fr. in year 1 \\\\ \n" % self.costElecTotalY
        lines = lines + line

        label = "definitionTable"

        self.doc.addTable(caption, names, units, label, lines, useFormula=True)

    def _addTableCosts(self, doc):
        totalCostScaleFactor = 1e-3 if self._USE_kCHF_FOR_TOTAL_COSTS else 1
        caption = r"System and Heat generation costs (all values incl. 8$\%$ VAT) "

        names = ["Group", "Component", "Costs", "Size", "LifeTime", "Total Costs"]
        if self._USE_kCHF_FOR_TOTAL_COSTS:
            units = ["", "", "[CHF]", "", "", "[kCHF]"]
        else:
            units = ["", "", "[CHF]", "", "Years", "[CHF]"]

        label = "CostsTable"
        lines = r"\\" + "\n"

        writer = _ct.ComponentGroupsRowsLinesWriter(self.totalInvestCost, totalCostScaleFactor)
        componentRowsLines = writer.createLines(self._output.componentGroups)

        lines += componentRowsLines

        symbol = "\\%"

        line = "\\hline \\\\ \n"
        lines = lines + line
        line = "\\hline \\\\ \n"
        lines = lines + line

        costUnit = " $CHF/a$"

        line = "Annuity & Annuity (yearly costs over lifetime)  &&& & %2.0f% s  \\\\ \n" % (self.annuity, costUnit)
        lines = lines + line
        line = " & Share of Investment & &&& %2.0f%s (%2.0f%s) \\\\ \n" % (
            self._output.componentGroups.annualizedCost.mean, costUnit,
            self._output.componentGroups.annualizedCost.mean * 100. / self.annuity, symbol)
        lines = lines + line
        line = " & Share of Electricity  & %.0f+%.2f/kWh & %2.0f kWh&  & %2.0f%s (%2.0f%s)\\\\ \n" % (
            self.costElecFix, self.costEleckWh, self.elDemandTotal, self.anElec, costUnit,
            self.anElec * 100. / self.annuity, symbol)
        lines = lines + line
        line = " & Share of Maintenance & &&& %2.0f%s (%2.0f%s)\\\\ \n" % (
            self.anMaint, costUnit, self.anMaint * 100. / self.annuity, symbol)
        lines = lines + line
        for yc in self._output.yearlyCosts.factors:
            line = " & Share of %s & %.0f+%.2f/%s & %.0f  %s & & %2.0f%s (%2.0f%s)\\\\ \n" % (
                yc.name,
                yc.coeffs.offset.mean,
                yc.coeffs.slope.mean,
                yc.value.unit,
                yc.value.value, yc.value.unit, yc.cost.mean, costUnit,
                yc.cost.mean * 100. / self.annuity, symbol)
            lines = lines + line

        line = " & Share of Residual Value &&& & %2.0f%s (%2.0f%s)\\\\ \n" % (
            self.anResVal, costUnit, self.anResVal * 100. / self.annuity, symbol)
        lines = lines + line

        line = "Present Value  & Present Value of all costs  & &&& %2.2f% s  \\\\ \n" % (self.npvSystem, " CHF")
        lines = lines + line
        line = "\\hline \\\\ \n"
        lines = lines + line

        hgcUnit = "$Rp./kWh$"

        line = " Energy Generation Costs & Using annuity: &&& %2.2f & %s \\\\ \n" % (self.heatGenCost * 100., hgcUnit)
        lines = lines + line

        doc.addTable(caption, names, units, label, lines, useFormula=False)

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
