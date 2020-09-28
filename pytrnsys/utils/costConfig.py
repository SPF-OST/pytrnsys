#!/usr/bin/env python

"""
Child class from costClass customized for general calculation with config file

Author : Dani Carbonell
Last Change: Jeremias Schmidli
Date : 07.04.2020
"""

import pytrnsys.utils.costCalculationVar as costClass
import pytrnsys.psim.resultsProcessedFile as results
import matplotlib.pyplot as plt
import os
import json
import logging
logger = logging.getLogger('root')

class costConfig(costClass.CostCalculationVar):

    def __init__(self):

        costClass.CostCalculationVar.__init__(self)

        self.readCompleteFolder=True
        self.fileNameList = None

    def setDataPath(self ,dataPath):

        self.dataPath = dataPath

    def setFileNameList(self,fileNameList):
        self.fileNameList=fileNameList
        self.readCompleteFolder=False

    def setDefaultData(self,dictCost):

        self.rate               = dictCost["DefaultData"]["rate"]
        self.analysPeriod       = dictCost["DefaultData"]["analysPeriod"]
        self.costElecFix        = dictCost["DefaultData"]["costElecFix"]
        self.costEleckWh        = dictCost["DefaultData"]["costEleckWh"]
        self.increaseElecCost   = dictCost["DefaultData"]["increaseElecCost"]
        self.MaintenanceRate    = dictCost["DefaultData"]["MaintenanceRate"]
        self.costResidual       = dictCost["DefaultData"]["costResidual"]
        self.cleanModeLatex     = dictCost["DefaultData"]["cleanModeLatex"]
        self.lifeTimeResVal     = dictCost["DefaultData"]["lifeTimeResVal"]

    # This will read all results from the folder dataPath
    # To access to the information you should use self.results[i]["nameOfVariable"]

    def readResults(self ,dataPath):

        self.resClass = results.ResultsProcessedFile(dataPath)
        self.resClass.readResultsData(resultType='json',completeFolder=self.readCompleteFolder,fileNameList=self.fileNameList)

    @staticmethod
    def readCostJson(path):

        with open(path) as json_file:
            dictCost = json.load(json_file)

        return dictCost

    def process(self, dictCost):

        # lifeTime = 25
        # self.lifeTimeResVal =lifeTime
        # lifeTimeBat = 15
        # lifeTimeFC = 20
        # lifeTimeTes = 40

        # self.pvAreaVec = []
        # self.batSizeVec = []
        self.investVec = []
        self.annuityVec = []
        # self.RselfSuffVec = []
        # self.RpvGenVec = []

        self.resultsVecDict = []
        # batList = []

        for i in range(len(self.resClass.results)):
            caseDict = {}

            fileName = self.resClass.fileName[i]
            outputPath = os.path.join(self.resClass.path, fileName)

            self.setOutputhPathAndFileName(outputPath, fileName)

            for component in dictCost['Components']:
                comp = dictCost['Components'][component]
                size = self.resClass.results[i].get(comp['size'])
                self.addComponent(component, size, comp["baseCost"], comp["varCost"], comp["varUnit"], comp["group"], comp["lifeTime"])


            # self.vTes = self.resClass.results[i].get("Vol_Tes1") / 1000.
            # self.hpSize = self.resClass.results[i].get("sizeHpUsed")
            #
            # self.addComponent("Combi-Storage", self.vTes, 700., 700., "m$^3$", "TES", lifeTimeTes)
            # self.addComponent("Heat pump", self.hpSize, 6000., 450, "kW", "Heat pump", lifeTime)

            # self.kgAlUsed = self.resClass.results[i].get("kgAlUsed")
            # qDemand = self.resClass.results[i].get("Q_yearly")
            qDemand = self.resClass.results[i].get(dictCost['DefaultData']['qDemand'])
            # elDemand = self.resClass.results[i].get("ElDemand")

            # self.qDemand = qDemand + elDemand
            self.qDemand = qDemand

            # self.elFromGrid = self.resClass.results[i].get("E_yearly")
            self.elFromGrid = self.resClass.results[i].get(dictCost['DefaultData']['elFromGrid'])
            # self.AlToGrid = 0.  # self.resClass.results[i].get("AlToGrid")
            # self.PvToSmelter = self.resClass.results[i].get("PVToSmelter")
            self.elDemandTotal = self.elFromGrid

            for yearlyCost in dictCost['YearlyCosts']:
                cost = dictCost['YearlyCosts'][yearlyCost]
                size = self.resClass.results[i].get(cost['size'])
                self.addYearlyComponentCost(yearlyCost, size, cost['baseCost'], cost['varCost'], cost['varUnit'])

            # self.addYearlyComponentCost("Aluminium fuel", self.kgAlUsed, 0., 1.2, "kg")
            # self.addYearlyComponentCost("Transmission grid", self.elFromGrid, 0., 0.05, "kWh")
            # self.addYearlyComponentCost("Feed in from Al", self.AlToGrid, 0., -0.2, "kWh")

            # self.pvAreaVec.append(self.pvPeak)
            # self.batSizeVec.append(self.batkWh)

            self.calculate()

            self.investVec.append(self.totalInvestCost)
            self.annuityVec.append(self.heatGenCost)
            # self.RselfSuffVec.append(self.RselfSuff)
            # self.RpvGenVec.append(self.RpvGen)

            self.doPlots()
            self.doPlotsAnnuity()

            fileName = self.fileName + "-cost"

            self.doc.resetTexName(fileName)
            self.unit = 1

            self.createLatex()
            self.clean()

            # if (scenario == "today"):
            #     if (efficiency == "low"):
            #         xPosition = 0.25
            #     elif (efficiency == "mid"):
            #         xPosition = 2.25
            #     elif (efficiency == "high"):
            #         xPosition = 4.25
            # elif (scenario == "future"):
            #     if (efficiency == "low"):
            #         xPosition = 0.75
            #     elif (efficiency == "mid"):
            #         xPosition = 2.75
            #     elif (efficiency == "high"):
            #         xPosition = 4.75
            #
            # caseDict["PvPeak"] = self.pvPeak
            # caseDict["batkWh"] = self.batkWh
            caseDict["investment"] = self.totalInvestCost
            caseDict["energyCost"] = self.heatGenCost

            for component in dictCost['Components']:
                if(component=="Collector"):
                    comp = dictCost['Components'][component]
                    size = self.resClass.results[i].get(comp['size'])

                    caseDict["investmentPerM2"] = self.totalInvestCost/size
                    caseDict["investmentPerMWh"] = self.totalInvestCost*1000/(self.qDemand)

            # caseDict["pvGen"] = self.RpvGen

            # batList.append(self.batkWh)
            self.resultsVecDict.append(caseDict)
            # else:
            resultJsonPath = os.path.join(outputPath,self.fileName + '-results.json')
            self.addCostToJson(resultJsonPath, self.resClass.results[i], caseDict)
        # self.batList = list(batList)

        self.clean()

    def printDataFile(self):

        for bat in self.batList:

            lines = ""
            line = "!pvPeak\tBatsize\t investment\tAnnuity\tPvGen\n";
            lines = lines + line
            line = "!kW\t \tkWh \t kFr\t CHF/kWh\t-\n";
            lines = lines + line

            for i in range(len(self.pvAreaVec)):
                if (self.batSizeVec[i] == bat):
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

        figureData = []
        legendList = []

        xList = sorted(list(set(varXAxis)))
        lineList = sorted(list(set(varDiffLines)))

        for i in range(len(lineList)):

            varVec = []
            xVec = []

            legendList.append("%s=%s" % (nameLines, lineList[i]))

            for j in range(len(xList)):

                for k in range(len(self.annuityVec)):
                    if (varXAxis[k] == xList[j] and varDiffLines[k] == lineList[i]):
                        xVec.append(xList[j])
                        varVec.append(varYAxis[k])

            # ax1 = plt.subplot(1, 3, i + 1)
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

        figureData = []
        legendList = []

        pvList = sorted(list(set(self.pvAreaVec)))
        batList = sorted(list(set(self.batSizeVec)))

        for i in range(len(batList)):

            varVec = []
            areaVec = []

            legendList.append("Bat-Size=%s kWh" % batList[i])

            for j in range(len(pvList)):

                for k in range(len(self.annuityVec)):
                    if (self.pvAreaVec[k] == pvList[j] and self.batSizeVec[k] == batList[i]):
                        areaVec.append(pvList[j])
                        varVec.append(self.annuityVec[k])

            # varSorted = [x for y, x in sorted(zip(pvList, varVec))]
            # areaSorted = sorted(pvList)

            varSorted = varVec
            areaSorted = areaVec

            # ax1 = plt.subplot(1, 3, i + 1)
            ax.plot(areaSorted, varSorted)

        ax.legend(legendList)
        ax.set(xlabel='PV [kWp]', ylabel='Energy cost [\Euro/kWh]')

        ax.grid()
        # ax.set_ylim([1.5, 9.5])

        fig.show()
        ax.grid()

        figureName = "Annuity_vs_PvPeak.%s" % (extension)

        plotName = os.path.join(self.resClass.path, figureName)

        fig.savefig(plotName)

    def plotVsBat(self, extension="pdf"):

        fig, ax = plt.subplots(figsize=(16, 8))

        figureData = []
        legendList = []

        pvList = sorted(list(set(self.pvAreaVec)))
        batList = sorted(list(set(self.batSizeVec)))

        for i in range(len(pvList)):

            varVec = []
            batVec = []

            legendList.append("Pv_p=%s kWh" % pvList[i])

            for j in range(len(batList)):

                for k in range(len(self.annuityVec)):
                    if (self.pvAreaVec[k] == pvList[i] and self.batSizeVec[k] == batList[j]):
                        batVec.append(batList[j])
                        varVec.append(self.annuityVec[k])

            # varSorted = [x for y, x in sorted(zip(pvList, varVec))]
            # areaSorted = sorted(pvList)

            varSorted = varVec
            batSorted = batVec

            # ax1 = plt.subplot(1, 3, i + 1)
            ax.plot(batSorted, varSorted, marker='o')

        ax.legend(legendList)

        ax.set(xlabel='Battery [kWh]', ylabel='Energy cost [Euro/kWh]')

        ax.grid()
        # ax.set_ylim([1.5, 9.5])

        fig.show()
        ax.grid()

        figureName = "Annuity_vs_Bat.%s" % (extension)

        plotName = os.path.join(self.resClass.path, figureName)

        fig.savefig(plotName)

        # self.plotNamesGenerated.append(figureName)

    @staticmethod
    def addCostToJson(jsonPath, resultsDict, costResultsDict):

        logger.debug("updating results.json file")

        newResultsDict = {**resultsDict, **costResultsDict}

        with open(jsonPath, 'w') as fp:
            json.dump(newResultsDict, fp, indent = 2, separators=(',', ': '),sort_keys=True)

        logger.info("results.json file was updated with cost data")