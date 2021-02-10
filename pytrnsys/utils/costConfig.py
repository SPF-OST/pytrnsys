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

import matplotlib as mpl
import numpy as num
from matplotlib import pyplot as plt

import pytrnsys.psim.resultsProcessedFile as results
from pytrnsys.cost_calculation import economicFunctions as ef
from pytrnsys.report import latexReport as latex

logger = logging.getLogger('root')


class costConfig:
    def __init__(self):
        self.method = "VDI"
        self.unit = 1
        self.cleanModeLatex = True

        self.components = []
        self.baseCost = []
        self.varCost = []
        self.group = []
        self.size = []
        self.varUnit = []
        self.lifeTimeComp = []
        self.costComponent = []

        self.yearlyComp = []
        self.yearlyCompSize = []
        self.yearlyCompBaseCost = []
        self.yearlyCompVarCost = []
        self.yearlyCompVarUnit = []
        self.yearlyCompCost = []

        self.rate = 0.
        self.analysPeriod = 0.
        self.costElecFix = 0.
        self.costEleckWh = 0.
        self.lifeTime = 0.
        self.increaseElecCost = 0.
        self.elDemand = 0.
        self.totalInvestCost = 0.

        self.qDemand = 0.
        self.elDemandTotal = 0.
        self.MaintenanceRate = 0.
        self.costResidual = 0.
        self.lifeTimeResVal = 0.
        self.readCompleteFolder = True
        self.fileNameList = None

    def setDataPath(self, dataPath):
        self.dataPath = dataPath

    def setFileNameList(self, fileNameList):
        self.fileNameList = fileNameList
        self.readCompleteFolder = False

    def setDefaultData(self, dictCost):
        self.rate = dictCost["DefaultData"]["rate"]
        self.analysPeriod = dictCost["DefaultData"]["analysPeriod"]
        self.costElecFix = dictCost["DefaultData"]["costElecFix"]
        self.costEleckWh = dictCost["DefaultData"]["costEleckWh"]
        self.increaseElecCost = dictCost["DefaultData"]["increaseElecCost"]
        self.MaintenanceRate = dictCost["DefaultData"]["MaintenanceRate"]
        self.costResidual = dictCost["DefaultData"]["costResidual"]
        self.cleanModeLatex = dictCost["DefaultData"]["cleanModeLatex"]
        self.lifeTimeResVal = dictCost["DefaultData"]["lifeTimeResVal"]

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
        self.investVec = []
        self.annuityVec = []
        self.resultsVecDict = []

        for i in range(len(self.resClass.results)):
            caseDict = {}

            fileName = self.resClass.fileName[i]
            outputPath = os.path.join(self.resClass.path, fileName)

            self.setOutputPathAndFileName(outputPath, fileName)

            for component in dictCost['Components']:
                comp = dictCost['Components'][component]
                size = self.resClass.results[i].get(comp['size'])
                self.addComponent(component, size, comp["baseCost"], comp["varCost"], comp["varUnit"], comp["group"],
                                  comp["lifeTime"])

            self.qDemand = self.resClass.results[i].get(dictCost['DefaultData']['qDemand'])
            self.elFromGrid = self.resClass.results[i].get(dictCost['DefaultData']['elFromGrid'])
            self.elDemandTotal = self.elFromGrid

            for yearlyCost in dictCost['YearlyCosts']:
                cost = dictCost['YearlyCosts'][yearlyCost]
                size = self.resClass.results[i].get(cost['size'])
                self.addYearlyComponentCost(yearlyCost, size, cost['baseCost'], cost['varCost'], cost['varUnit'])

            self.calculate()

            self.investVec.append(self.totalInvestCost)
            self.annuityVec.append(self.heatGenCost)

            self.doPlots()
            self.doPlotsAnnuity()

            fileName = self.fileName + "-cost"

            self.doc.resetTexName(fileName)
            self.unit = 1

            self.createLatex()
            self.clean()

            caseDict["investment"] = self.totalInvestCost
            caseDict["energyCost"] = self.heatGenCost

            for component in dictCost['Components']:
                if component == "Collector":
                    comp = dictCost['Components'][component]
                    size = self.resClass.results[i].get(comp['size'])

                    caseDict["investmentPerM2"] = self.totalInvestCost / size
                    caseDict["investmentPerMWh"] = self.totalInvestCost * 1000 / self.qDemand

            self.resultsVecDict.append(caseDict)
            resultJsonPath = os.path.join(outputPath, self.fileName + '-results.json')
            self.addCostToJson(resultJsonPath, self.resClass.results[i], caseDict)

        self.clean()

    def printDataFile(self):
        for bat in self.batList:

            lines = ""
            line = "!pvPeak\tBatsize\t investment\tAnnuity\tPvGen\n";
            lines = lines + line
            line = "!kW\t \tkWh \t kFr\t CHF/kWh\t-\n";
            lines = lines + line

            for i in range(len(self.pvAreaVec)):
                if self.batSizeVec[i] == bat:
                    line = "%f\t%f\t%f\t%f\t%f\n" % (self.pvAreaVec[i], self.batSizeVec[i], \
                                                     self.investVec[i], self.annuityVec[i], self.RpvGenVec[i])
                    lines = lines + line
            fileName = "cost-batkWh%.0f" % bat
            myFileName = self.resClass.path + "\\%s.dat" % fileName

            logger.debug("%s file created" % myFileName)

            outfile = open(myFileName, 'w')
            outfile.writelines(lines)
            outfile.close()

    def setFontsizes(self, small):
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
        ax.set(xlabel='PV [kWp]', ylabel='Energy cost [\Euro/kWh]')

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

    @staticmethod
    def addCostToJson(jsonPath, resultsDict, costResultsDict):

        logger.debug("updating results.json file")

        newResultsDict = {**resultsDict, **costResultsDict}

        with open(jsonPath, 'w') as fp:
            json.dump(newResultsDict, fp, indent=2, separators=(',', ': '), sort_keys=True)

        logger.info("results.json file was updated with cost data")

    def calculate(self):
        self.nComp = len(self.costComponent)
        self.costAnn = num.zeros(self.nComp)
        self.annFac = num.zeros(self.nComp)

        self.totalInvestCost = 0.
        for i in range(self.nComp):
            logger.debug("ncomp:%d rate:%f lifeTime%f" % (i, self.rate, self.lifeTimeComp[i]))

            period = self.lifeTimeComp[i]
            ann = ef.getAnnuity(self.rate, period)

            self.annFac[i] = ann
            self.costAnn[i] = self.costComponent[i] * ann
            self.totalInvestCost = self.totalInvestCost + self.costComponent[i]

        # ===================================================
        # electricity
        # ===================================================

        self.costElecTotalY = self.costElecFix + self.costEleckWh * self.elDemandTotal

        if self.rate == self.increaseElecCost:
            self.npvFacElec = self.analysPeriod / (
                    1. + self.rate)  # DC It was lifeTime but now its different from each other
        else:
            self.npvFacElec = ef.getNPVIncreaseCost(self.rate, self.analysPeriod, self.increaseElecCost)

        self.npvElec = self.costElecTotalY * self.npvFacElec

        # ===================================================
        # Maintenance cost
        # ===================================================
        self.npvMaintenance = self.MaintenanceRate * self.totalInvestCost * ef.getNPV(self.rate,
                                                                                      self.analysPeriod)
        self.nYearlyComp = len(self.yearlyComp)
        self.costNpvYearlyComp = num.zeros(self.nYearlyComp)

        for i in range(self.nYearlyComp):
            npv = ef.getNPV(self.rate, self.analysPeriod)
            self.costNpvYearlyComp[i] = self.yearlyCompCost[i] * npv

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

        self.npvSystem = self.totalInvestCost + sum(
            self.costNpvYearlyComp) + self.npvElec + self.npvMaintenance - self.npvResVal

        logger.debug("npvSystem:%f totalInvestCost :%f AlMatcost:%f npvElec :%f npvMaintenance:%f npvResVal:%f" % (
            self.npvSystem, self.totalInvestCost, sum(self.costNpvYearlyComp),
            self.npvElec, self.npvMaintenance, self.npvResVal))

        # ===================================================
        # ANNUITY
        # ===================================================

        self.annuityFac = ef.getAnnuity(self.rate, self.analysPeriod)

        self.anToInvCost = sum(self.costAnn)

        self.anElec = self.annuityFac * self.npvElec
        self.anMaint = self.MaintenanceRate * self.totalInvestCost  # to use DP method

        self.anResVal = (-1.) * self.annuityFac * self.npvResVal

        self.anYearlyComp = num.zeros(self.nYearlyComp)

        for i in range(self.nYearlyComp):
            self.anYearlyComp[i] = self.annuityFac * self.costNpvYearlyComp[i]

        self.annuity = self.anToInvCost + self.anElec + self.anMaint + self.anResVal + sum(self.anYearlyComp)

        logger.info(" AnElectricity:%f npvElec:%f npvFacElec:%f annnuityFac:%f   " % (
            self.anElec, self.npvElec, self.npvFacElec, self.annuityFac))

        self.heatGenCost = self.annuity / self.qDemand  # Fr./kWh

        logger.info("AnnuityFac:%f  " % self.annuityFac)
        logger.info("Heat Generation Cost Annuity:%f " % self.heatGenCost)

    def doPlots(self):
        legends = []
        inVar = []

        groupCost = 0.

        for i in range(self.nComp):

            logger.debug("group:%s" % self.group[i])

            if i < (self.nComp - 1) and self.group[i] != self.group[i + 1]:
                groupCost = groupCost + self.costComponent[i]
                inVar.append(groupCost)
                legends.append(self.group[i])
                groupCost = 0.
                logger.debug("Inside group:%s" % self.group[i])
            elif i == (self.nComp - 1):
                groupCost = groupCost + self.costComponent[i]
                inVar.append(groupCost)
                legends.append(self.group[i])
                logger.debug("Last group:%s" % self.group[i])
            else:
                groupCost = groupCost + self.costComponent[i]
                logger.debug("groupCost:%f group:%s" % (groupCost, self.group[i]))

        self.nameCostPdf = self.plotCostShare(inVar, legends, "costShare" + "-" + self.fileName, sizeFont=30,
                                              plotJpg=False, writeFile=False)

    def doPlotsAnnuity(self):
        legends = []
        inVar = []

        inVar.append(self.anToInvCost)
        legends.append("Capital cost")

        inVar.append(self.anMaint)
        legends.append("Maintenance")

        inVar.append(self.anElec)
        legends.append("El. purchased \n from the grid")

        for i in range(len(self.yearlyComp)):

            logger.debug("cost:%f name:%s" % (self.costComponent[i], self.yearlyComp[i]))

            if self.yearlyCompCost[i] > 0.:
                inVar.append(self.anYearlyComp[i])
                if self.yearlyComp[i] == "Transmission grid":
                    legends.append("El. transmitted \n through the \n grid")
                elif self.yearlyComp[i] == "Aluminium fuel":
                    legends.append("Fuel cost \n (Al regeneration)")
                else:
                    legends.append(self.yearlyComp[i])

        self.nameCostAnnuityPdf = self.plotCostShare(inVar, legends, "costShareAnnuity" + "-" + self.fileName,
                                                     plotSize=17, sizeFont=30, plotJpg=False, writeFile=False)

    def clean(self):
        self.components = []
        self.baseCost = []
        self.varCost = []
        self.group = []
        self.size = []
        self.varUnit = []
        self.lifeTimeComp = []
        self.costComponent = []

        # This are variables that add cost every year such as materials consumed, oil, etc..
        self.yearlyComp = []
        self.yearlyCompSize = []
        self.yearlyCompBaseCost = []
        self.yearlyCompVarCost = []
        self.yearlyCompVarUnit = []
        self.yearlyCompCost = []

    def setOutputPathAndFileName(self, path, fileName):
        self.outputPath = path
        self.fileName   = fileName

        logger.debug("path:%s name:%s" %(self.outputPath,self.fileName))
        self.doc = latex.LatexReport(self.outputPath,self.fileName)

    def addComponent(self, name, size, base, var, varUnit, group, lifeTime):
        self.components.append(name)
        self.size.append(size)
        self.baseCost.append(base)
        self.varCost.append(var)
        self.varUnit.append(varUnit)
        self.group.append(group)
        self.lifeTimeComp.append(lifeTime)
        cost = base + var * size
        self.costComponent.append(cost)

        logger.debug("cost:%f name:%s base:%f var:%f" % (cost, name, base, var))

    def addYearlyComponentCost(self, name, size, base, var, varUnit):
        self.yearlyComp.append(name)
        self.yearlyCompSize.append(size)
        self.yearlyCompBaseCost.append(base)
        self.yearlyCompVarCost.append(var)
        self.yearlyCompVarUnit.append(varUnit)
        cost = base + var * size
        self.yearlyCompCost.append(cost)

        logger.debug("cost:%f name:%s base:%f var:%f" % (cost, name, base, var))

    def plotCostShare(self, inVar, legends, nameFile, plotSize=15, sizeFont=15, plotJpg=False, writeFile=False):
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

    def createLatex(self, fileName=False):
        self.doc.setSubTitle("Energy generation costs")

        if not fileName:
            self.doc.setTitle(self.fileName)
        else:
            self.doc.setTitle(fileName)

        self.doc.setCleanMode(self.cleanModeLatex)
        self.doc.addBeginDocument()
        self.addTableEconomicAssumptions()
        self.addTableCosts(self.doc, self.unit)

        try:
            self.doc.addPlot(self.nameCostPdf, "System cost", "systemCost", 13)
            self.doc.addPlot(self.nameCostAnnuityPdf, "System cost annuity share", "systemCostannuity", 13)
        except:
            pass

        self.doc.addEndDocumentAndCreateTexFile()
        self.doc.executeLatexFile()

    def addTableEconomicAssumptions(self):
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

    def addTableCosts(self, doc, unit=1):
        symbol = "$\\%$"
        caption = "System and Heat generation costs (all values incl. 8%s VAT) " % symbol

        names = ["Group", "Component", "Costs", "Size", "LifeTime", "Total Costs"]
        if unit == 1e-3:
            units = ["", "", "[CHF]", "", "", "[kCHF]"]
        elif unit == 1:
            units = ["", "", "[CHF]", "", "Years", "[CHF]"]
        else:
            raise ValueError("unit not found:%f" % unit)

        label = "CostsTable"
        lines = ""
        symbol = "\\%"

        line = "\\\\ \n"
        lines = lines + line
        j = 0
        sumGroup = 0.
        for i in range(self.nComp):
            if i > 0 and self.group[i] != self.group[i - 1]:
                if j > 1:
                    line = "&\\cline{1-5} \n"
                    lines = lines + line
                    line = " &\\textbf{Total %s} &  & & & %.0f (%.1f %s) \\\\ \n" % (
                        self.group[i - 1], sumGroup, 100 * sumGroup / self.totalInvestCost, symbol)
                    lines = lines + line
                line = "\\hline \\\\ \n"
                lines = lines + line
                group = self.group[i]
                j = 0
                sumGroup = 0.
            else:
                group = self.group[i]

            if self.costComponent[i] > 0.:
                if j == 0:
                    line = "\\textbf{%s} & %s & %.0f+%.0f/%s & %.2f %s &%d & %.1f (%.1f %s) \\\\ \n" % (
                        group, self.components[i],
                        self.baseCost[i], self.varCost[i], self.varUnit[i], self.size[i], self.varUnit[i],
                        self.lifeTimeComp[i], self.costComponent[i] * unit,
                        100 * self.costComponent[i] / self.totalInvestCost, symbol)
                else:
                    line = " & %s & %.0f+%.0f/%s & %.2f %s &%d & %.1f (%.1f %s) \\\\ \n" % (self.components[i],
                                                                                            self.baseCost[i],
                                                                                            self.varCost[i],
                                                                                            self.varUnit[i],
                                                                                            self.size[i],
                                                                                            self.varUnit[i],
                                                                                            self.lifeTimeComp[i],
                                                                                            self.costComponent[
                                                                                                i] * unit,
                                                                                            100 * self.costComponent[
                                                                                                i] / self.totalInvestCost,
                                                                                            symbol)

                lines = lines + line
                j = j + 1

            sumGroup = sumGroup + self.costComponent[i] * unit

        if j > 1:  # The last component
            logger.info("===================================j:%d===============================" % j)
            line = "&\cline{1-5} \n"
            lines = lines + line
            line = " &\\textbf{Total %s} &  & & & %.0f (%.0f %s) \\\\ \n" % (
                self.group[self.nComp - 1], sumGroup, 100 * sumGroup / self.totalInvestCost, symbol)
            lines = lines + line

        line = "\\hline \\\\ \n"
        lines = lines + line
        line = " & \\textbf{Total Investment Cost} & && &\\textbf{%2.2f} (100%s) \\\\ \n" % (
            self.totalInvestCost * unit, symbol)
        lines = lines + line

        line = "\\hline \\\\ \n"
        lines = lines + line
        line = "\\hline \\\\ \n"
        lines = lines + line

        costUnit = " $CHF/a$"

        line = "Annuity & Annuity (yearly costs over lifetime)  &&& & %2.0f% s  \\\\ \n" % (self.annuity, costUnit)
        lines = lines + line
        line = " & Share of Investment & &&& %2.0f%s (%2.0f%s) \\\\ \n" % (
            self.anToInvCost, costUnit, self.anToInvCost * 100. / self.annuity, symbol)
        lines = lines + line
        line = " & Share of Electricity  & %.0f+%.2f/kWh & %2.0f kWh&  & %2.0f%s (%2.0f%s)\\\\ \n" % (
            self.costElecFix, self.costEleckWh, self.elDemandTotal, self.anElec, costUnit,
            self.anElec * 100. / self.annuity, symbol)
        lines = lines + line
        line = " & Share of Maintenance & &&& %2.0f%s (%2.0f%s)\\\\ \n" % (
            self.anMaint, costUnit, self.anMaint * 100. / self.annuity, symbol)
        lines = lines + line
        for i in range(len(self.yearlyComp)):
            line = " & Share of %s & %.0f+%.2f/%s & %.0f  %s & & %2.0f%s (%2.0f%s)\\\\ \n" % (
                self.yearlyComp[i], self.yearlyCompBaseCost[i], self.yearlyCompVarCost[i], self.yearlyCompVarUnit[i],
                self.yearlyCompSize[i], self.yearlyCompVarUnit[i], self.anYearlyComp[i], costUnit,
                self.anYearlyComp[i] * 100. / self.annuity, symbol)
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
