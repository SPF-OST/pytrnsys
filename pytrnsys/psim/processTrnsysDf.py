# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
Child class from ProcessMonthlyDataBase used for processing all TRNSYS simulations.

Author : Dani Carbonell
Date   : 2018
ToDo :
"""

import os, subprocess
import string, shutil
import pytrnsys.pdata.processFiles as spfUtils

# import pytrnsys.psim.processMonthlyDataBase as  monthlyData  # changed in order to clean the processing of files
import pytrnsys.utils.utilsSpf as utils
import time
import numpy as num
import matplotlib.pyplot as plt
import pytrnsys.trnsys_util.readTrnsysFiles as readTrnsysFiles
import pytrnsys.utils.unitConverter as unit
import pytrnsys.trnsys_util.LogTrnsys as LogTrnsys
import pytrnsys.trnsys_util.deckTrnsys as deckTrnsys
from pytrnsys.psim.simulationLoader import SimulationLoader
import pandas as pd
import pytrnsys.report.latexReport as latex
import pytrnsys.plot.plotMatplotlib as plot
import json
import pytrnsys.plot.plotBokeh as pltB
from string import ascii_letters, digits, whitespace
import locale
import re
import logging
from calendar import monthrange
from datetime import datetime, timedelta

logger = logging.getLogger("root")
# stop propagting to root logger
logger.propagate = False

# import pytrnsys_spf.psim.costConfig as costConfig


# from collections import OrderedDict


class ProcessTrnsysDf:
    """"""

    def __init__(self, _path, _name, language="en", individualFile=False):

        self.fileName = _name
        if individualFile:
            self.outputPath = _path
        else:
            self.outputPath = os.path.join(_path, self.fileName)
        self.executingPath = _path

        # Internal data

        self.fileNameWithExtension = _name
        self.titleOfLatex = "$%s$" % self.fileName
        self.folderName = self.fileName

        self.rootPath = os.getcwd()

        self.doc = latex.LatexReport(self.outputPath, self.fileName)
        self.plot = plot.PlotMatplotlib(language=language)

        self.plot.setPath(self.outputPath)

        self.pltB = pltB.PlotBokeh()

        self.cleanModeLatex = False

        self.tempFolder = "%s\\temp" % self.outputPath
        self.tempFolderEnd = "%s\\temp" % self.outputPath

        self.trnsysVersion = "standard"
        self.yearReadedInMonthlyFile = -1  # -1 means the last
        self.firstMonth = "January"

        self.yearlyFactor = 10.0  # value to divide yerarly values when plotted along with monthly data
        self.units = unit.UnitConverter()

        self.addPlotToLaTeX = {}
        self.readTrnsysFiles = readTrnsysFiles.ReadTrnsysFiles(self.tempFolderEnd)

        # self.tInEvapHpMonthlyMax = num.zeros(12,float)
        # self.tInEvapHpMonthlyMin = num.zeros(12,float)
        # self.tInEvapHpMonthlyAv  = num.zeros(12,float)

        self.nameClass = "ProcessTrnsys"
        self.unit = unit.UnitConverter()
        self.trnsysDllPath = False

        self.deckData = {}
        self.yearlySums = {}
        self.yearlyMin = {}
        self.yearlyMax = {}
        self.cumSumEnd = {}

    def setInputs(self, inputs):
        self.inputs = inputs
        self.plot.setExtensionPlot(self.inputs["figureFormat"])

    def setIndividualFiles(self, individualFiles):
        self.individualFiles = individualFiles

    def setLatexNamesFile(self, file):
        if file is not None:
            self.doc.getLatexNamesDict(file=file)
        else:
            self.doc.getLatexNamesDict()

    def setMatplotlibStyle(self, stylesheet):
        self.plot = plot.PlotMatplotlib(language=self.plot.language, stylesheet=stylesheet)
        self.plot.setPath(self.outputPath)

    def setFontsize(self, stylesheet):
        self.plot = plot.PlotMatplotlib(language=self.plot.language, stylesheet=stylesheet)
        # self.plot.ytick.labelsize: 8
        self.plot.setPath(self.outputPath)

    # the idea is to read the deck and get important information fro processing.
    # area collector, volume ice storage, volume Tes, Area uncovered, nH1, nominal power heat pump, etc...
    def setBuildingArea(self, area):
        self.buildingArea = area

    def setTrnsysDllPath(self, path):

        self.trnsysDllPath = path

    def setBuildingArea(self, area):
        self.buildingArea = area

    def setTrnsysVersion(self, version):
        self.trnsysVersion = version

    def setPrintDataForGle(self, printData):

        self.printDataForGle = printData

    def process(self):
        pass

    def loadAndProcessGeneric(self):
        self.houDataDf = pd.DataFrame()
        self.monDataDf = pd.DataFrame()
        self.dayDataDf = pd.DataFrame()

        for fileName in os.listdir(self.outputPath):
            path = os.path.join(self.outputPath, fileName)
            if "_Monats" in fileName:
                self.loadMonthlyFile(path)
            elif "_Stunden" in fileName:
                self.loadHourlyFile(path)
            elif "_Tage" in fileName:
                self.loadDailyFile(path)
            elif ".json" in fileName and "results" not in fileName:
                self.loadJson(path)

        if "loadClimateData" in self.inputs.keys():
            self.loadClimateDataFile()

        self.yearlyMin = {value + "_Min": self.houDataDf[value].min() for value in self.houDataDf.columns}
        self.yearlyMax = {value + "_Max": self.houDataDf[value].max() for value in self.houDataDf.columns}
        self.cumSumEnd = {}

        self.yearlyAvg = {value + "_Avg": self.houDataDf[value].mean() for value in self.houDataDf.columns}

        self.calcConfigEquations()

        self.addBokehPlot()
        self.addCustomBalance()
        self.addHeatingLimitFit()
        self.addCustomStackedBar()
        self.addCustomNBar()
        self.addTemperatureFreq()

        self.saveHourlyToCsv()
        self.addResultsFile()

    def loadHourlyFile(self, pathFile):

        file = pd.read_csv(pathFile, header=0, delimiter=";").rename(columns=lambda x: x.strip())

        file.set_index("Time", inplace=True, drop=False)
        period = pd.to_datetime(file["Time"], format="%d.%m.%Y %H:%M")

        file["Time"] = period
        file.set_index("Time", inplace=True)
        cols_to_use = [item for item in file.columns if item not in set(self.houDataDf.columns)]
        self.houDataDf = pd.merge(self.houDataDf, file[cols_to_use], left_index=True, right_index=True, how="outer")

    def loadDailyFile(self, pathFile):

        file = pd.read_csv(pathFile, header=0, delimiter=";").rename(columns=lambda x: x.strip())

        file.set_index("Time", inplace=True, drop=False)
        period = pd.to_datetime(file["Time"], format="%d.%m.%Y")
        file["Time"] = period
        file.set_index("Time", inplace=True)
        cols_to_use = [item for item in file.columns if item not in set(self.dayDataDf.columns)]
        self.dayDataDf = pd.merge(self.dayDataDf, file[cols_to_use], left_index=True, right_index=True, how="outer")

    def loadMonthlyFile(self, pathFile):

        file = pd.read_csv(pathFile, header=0, delimiter=";")  # .rename(columns=lambda x: x.strip())

        file["Number"] = file.index + pd.to_datetime(file["Time"][0].strip(), format="%B").month
        file.set_index("Number", inplace=True)
        # file['Datetime'] = pd.to_datetime(file['Month'].str.strip(), format='%B')

        # file['Time'] = file.index + pd.to_datetime(file['Time'][0].strip(), format='%B').month
        # file["Time"] = period
        # file.set_index('Time', inplace=True)
        cols_to_use = [item for item in file.columns if item not in set(self.monDataDf.columns)]
        self.monDataDf = pd.merge(self.monDataDf, file[cols_to_use], left_index=True, right_index=True, how="outer")

        self.myShortMonths = utils.getShortMonthyNameArray(self.monDataDf["Time"].values)

    def loadClimateDataFile(self, filePath=""):
        """
        Load Climate Data File (csv)

        Parameters
        ---------
        filePath : str, optional
            Full path of csv containing climate data to be loaded; if not specified it needs to be given by the input

        Returns
        -------

        """
        if "loadClimateData" in self.inputs.keys():
            filePathFull = self.inputs["loadClimateData"]
        else:
            filePathFull = filePath
        file = pd.read_csv(filePathFull, header=0, delimiter=";")

        file.set_index("Time", inplace=True, drop=False)
        period = pd.to_datetime(file["Time"], format="%d.%m.%Y %H:%M")
        file["Time"] = period
        file.set_index("Time", inplace=True)

        self.climateDf = file

    def loadJson(self, filePath):
        """
        Load the json containing the parameters of the data set

        Parameters
        ---------
        filePath : str
            Full path of json containing the data set parameters to be loaded

        Returns
        -------

        """
        with open(filePath, "r") as file:
            parameterDictionary = json.load(file)
            self.deckData.update(parameterDictionary)

    def loadAndProcessTrnsys(self):

        # self.inputs['fileOutputPath'] = "C:\Daten\OngoingProject\BigIce\PassiveCoolingFlatPlate\BigIce-MFH-TestPassiveCoolTest\temp"
        # self.inputs['listOfFiles'] = ["PCMOut.Plt"]
        # self.definedResultsFileToRead(self.inputs['fileOutputPath'],self.inputs['listOfFiles'])

        self.loadFiles()
        if self.inputs["typeOfProcess"] != "individual":
            self.loadDll()
        self.process()
        self.addBokehPlot()
        self.addQvsTPlot()

        if self.inputs["createLatexPdf"] == True and self.inputs["typeOfProcess"] != "individual":
            self.doLatexPdf()

        self.saveHourlyToCsv()
        self.addResultsFile()
        # if "cost" in self.inputs.keys():
        #     self.calcCost()

    def setLoaderParameters(self):

        self.monthlyUsed = True
        self.hourlyUsed = True
        self.timeStepUsed = True
        self.fullYear = False
        self.fileNameListToRead = None
        self.loadMode = "complete"

        if "firstMonth" in self.inputs.keys():
            self.firstMonth = self.inputs["firstMonth"]
        else:
            self.firstMonth = "January"
        if "yearReadedInMonthlyFile" in self.inputs.keys():
            self.yearReadedInMonthlyFile = self.inputs["yearReadedInMonthlyFile"]
        else:
            self.yearReadedInMonthlyFile = -1

        self.resultsPath = self.outputPath + "//temp"

    def definedResultsFileToRead(self, _outputPath, _fileNameListToRead):
        self.resultsPath = _outputPath
        self.fileNameListToRead = _fileNameListToRead

    def loadFiles(self):

        self.setLoaderParameters()
        locale.setlocale(locale.LC_ALL, "enn")

        if self.inputs["typeOfProcess"] == "individual":
            self.fileNameListToRead = []
            for file in self.individualFiles:
                self.fileNameListToRead += [os.path.join(file["path"], file["name"])]
            self.loader = SimulationLoader(
                self.resultsPath,
                fileNameList=self.fileNameListToRead,
                sortMonths=True,
                mode=self.loadMode,
                monthlyUsed=self.monthlyUsed,
                hourlyUsed=self.hourlyUsed,
                timeStepUsed=self.timeStepUsed,
                firstMonth=self.firstMonth,
                year=self.yearReadedInMonthlyFile,
                individualFiles=True,
            )

        else:
            if "footerPresent" in self.inputs.keys():
                self.loader = SimulationLoader(
                    self.resultsPath,
                    fileNameList=self.fileNameListToRead,
                    sortMonths=True,
                    mode=self.loadMode,
                    monthlyUsed=self.monthlyUsed,
                    hourlyUsed=self.hourlyUsed,
                    timeStepUsed=self.timeStepUsed,
                    firstMonth=self.firstMonth,
                    year=self.yearReadedInMonthlyFile,
                    footerPresent=self.inputs["footerPresent"],
                )
            else:
                self.loader = SimulationLoader(
                    self.resultsPath,
                    fileNameList=self.fileNameListToRead,
                    sortMonths=True,
                    mode=self.loadMode,
                    monthlyUsed=self.monthlyUsed,
                    hourlyUsed=self.hourlyUsed,
                    timeStepUsed=self.timeStepUsed,
                    firstMonth=self.firstMonth,
                    fullYear=self.fullYear,
                    year=self.yearReadedInMonthlyFile,
                )
        self.monDataDf = self.loader.monDataDf
        self.houDataDf = self.loader.houDataDf
        self.steDataDf = self.loader.steDataDf
        self.myShortMonths = self.loader.myShortMonths

        self.deck = deckTrnsys.DeckTrnsys(self.outputPath, self.fileName)
        if self.inputs["typeOfProcess"] != "individual":
            self.deck.loadDeck()
            self.deckData = self.deck.getAllDataFromDeck()
        try:
            self.nYearsSimulated = (self.deckData["STOP"] - self.deckData["START"]) / 8760
        except:
            logger.warning(
                "START or STOP variable called differentely. Number of simulated years not calculated and printed. Mabe check for upper lower case issues."
            )

        if "loadExternalData" in self.inputs.keys() and "loadExternalDataMask" in self.inputs.keys():
            m = re.search(self.inputs["loadExternalDataMask"], self.fileName)
            fileToLoad = self.inputs["loadExternalData"]
            try:
                stringToBeInserted = m.group(1)
                fileToLoad = fileToLoad.replace("*", stringToBeInserted)
            except:
                pass
            with open(fileToLoad) as f_in:
                resultsDict = json.load(f_in)
            for key, value in resultsDict.items():
                if isinstance(value, list):
                    self.monDataDf[key + "_Ext"] = pd.Series(num.array(value), index=range(1, 13, 1))
                else:
                    self.deckData[key + "_Ext"] = value

        self.yearlySums = {value + "_Tot": self.monDataDf[value].sum() for value in self.monDataDf.columns}
        self.yearlyMin = {value + "_Min": self.houDataDf[value].min() for value in self.houDataDf.columns}
        self.yearlyMax = {value + "_Max": self.houDataDf[value].max() for value in self.houDataDf.columns}
        self.yearlyAvg = {value + "_Avg": self.houDataDf[value].mean() for value in self.houDataDf.columns}

        for column in self.monDataDf.columns:
            self.monDataDf["Cum_" + column] = self.monDataDf[column].cumsum()
        self.calcConfigEquations()

        # We recalculate all to capture also variables that were calculated from equations, while at the same time
        # having all read-in variables feature _Tot, _Min, _Max and _Avg; should be improved

        self.yearlySums = {value + "_Tot": self.monDataDf[value].sum() for value in self.monDataDf.columns}
        self.yearlyMin = {value + "_Min": self.houDataDf[value].min() for value in self.houDataDf.columns}
        self.yearlyMax = {value + "_Max": self.houDataDf[value].max() for value in self.houDataDf.columns}
        self.yearlyAvg = {value + "_Avg": self.houDataDf[value].mean() for value in self.houDataDf.columns}

        try:
            self.myShortMonths = utils.getShortMonthyNameArray(self.monDataDf["Month"].values)
        except:
            pass

        logger.info("Completed loading files of " + self.fileName)

    def addBokehPlot(self):

        if "plotHourly" in self.inputs.keys():
            for varToPlot in self.inputs["plotHourly"]:
                self.pltB.createBokehPlot(self.houDataDf, self.outputPath, self.fileName + "hourly", varToPlot)

        if "plotDaily" in self.inputs.keys():
            for varToPlot in self.inputs["plotDaily"]:
                self.pltB.createBokehPlot(
                    self.dayDataDf, self.outputPath, self.fileName + "daily", self.inputs["plotDaily"][0]
                )

        if "plotTimeStep" in self.inputs.keys():
            for varToPlot in self.inputs["plotTimeStep"]:
                self.pltB.createBokehPlot(
                    self.steDataDf, self.outputPath, self.fileName + "timeStep", self.inputs["plotTimeStep"][0]
                )

    def addMonthlyPlots(self):

        if "plotMonthly" in self.inputs.keys():
            #
            for i in range(len(self.inputs["plotMonthly"])):
                key = self.inputs["plotMonthly"][i]
                nameFile = key[0]
                # namePdf=self.plot.plotMonthlyDf(self.monDataDf[key].values, key[0], nameFile,1,self.myShortMonths,myTitle=None, printData=True)
                namePdf = self.plot.plotMonthlyDf(
                    self.monDataDf[key].values,
                    key[0],
                    nameFile,
                    10.0,
                    self.myShortMonths,
                    myTitle=None,
                    printData=self.printDataForGle,
                )

                # self.doc.addTableMonthlyDf(self.monDataDf[key].values, key[0], unit, caption, nameFile, self.myShortMonths, sizeBox=15,
                #                            addLines=addLines)
                self.doc.addPlotShort(namePdf, label=nameFile)

                # self.addPlotToLaTeX = {namePdf: "Monthly plot. Yearly value divided by 10."}
                logger.debug("%s monthly plot" % namePdf)

    def addHourlyPlots(self):

        if "plotHourly" in self.inputs.keys():
            self.pltB.createBokehPlot(self.houDataDf, self.outputPath, self.fileName, self.inputs["plotHourly"][0])

    def addQvsTPlot(self):
        # define QvsTDf here!
        monthsSplit = []
        if "plotHourlyQvsT" in self.inputs.keys():
            InputListQvsT = self.inputs["plotHourlyQvsT"][0]
            QvsTDf = self.houDataDf
            logger.debug("hourlyUsed")
            self.loadQvsTConfig(
                QvsTDf, InputListQvsT, "plotQvsTconfigured", monthsSplit=monthsSplit, normalized=True, cut=False
            )
        if "plotTimestepQvsT" in self.inputs.keys():
            InputListQvsT = self.inputs["plotTimestepQvsT"][0]
            QvsTDf = self.steDataDf
            if "Time" in QvsTDf:
                timestep = (QvsTDf[2] - QvsTDf[1]).seconds
            else:
                timestep = (QvsTDf.index[2] - QvsTDf.index[1]).seconds
            factorForHour = timestep / 3600
            logger.debug("stepDfUsed")
            self.loadQvsTConfig(
                QvsTDf,
                InputListQvsT,
                "plotQvsTconfigured",
                monthsSplit=monthsSplit,
                normalized=True,
                cut=False,
                factor=factorForHour,
            )
        else:
            pass

    def executeLatexFile(self):

        self.doc.executeLatexFile(moveToTrnsysLogFile=True, runTwice=False)

    def doLatexPdf(self, documentClass="SPFShortReportIndex"):

        self.createLatex(documentClass=documentClass)

        self.executeLatexFile()

    def addLatexContent(self):
        self.addImages()
        self.addCaseDefinition()
        self.calculateDemands()

        if self.inputs["calculateHeatDemand"] == True:
            self.addHeatBalance()
            self.calculateElHeatConsumption()
            self.addDemands()
        if self.inputs["calculateSPF"] == True:
            self.addSPFSystem()

        if self.inputs["dailyBalance"] == True:
            daysSelected = self.inputs["daysSelected"]
            self.addHeatBalanceDaily(daysSelected)
        if self.inputs["hourlyBalance"] == True:
            daySelected = self.inputs["daySelected"]
            self.addHeatBalanceHourly(daySelected)

        if self.inputs["calculateElectricDemand"] == True:
            self.addElBalance()
            self.addElConsumption()

        if "calculateEPF" in self.inputs:
            if self.inputs["calculateEPF"]:
                self.addEPFSystem()

        self.addCustomBalance()
        self.addCustomStackedBar()
        self.addCustomNBar()
        self.addTemperatureFreq()

        self.addMonthlyPlots()
        self.addHourlyPlots()
        self.addQvsTPlot()

        for key in self.addPlotToLaTeX:
            self.doc.addPlotShort(key, caption=self.addPlotToLaTeX[key], label=key)

        # self.addQvsTPlot()
        self.saveHourlyToCsv()

    def createLatex(self, documentClass="SPFShortReportIndex"):

        self.doc.documentClass = documentClass

        self.doc.setTitle(self.titleOfLatex)
        self.doc.setSubTitle("TRNSYS results")
        self.doc.setCleanMode(self.cleanModeLatex)
        self.doc.addBeginDocument()

        self.addLatexContent()

        self.doc.addEndDocumentAndCreateTexFile()

    def calculateDemands(self):

        self.qDemandVector = []
        self.elDemandVector = []
        self.qDemandDf = pd.DataFrame()
        self.legendEl = []
        self.legendQ = []
        # self.elDemandDf = pd.DataFrame()

        for name in self.monDataDf.columns:

            if len(name) > 9 and ((name[0:9] == "elSysOut_") or (name[0:9] == "elSysIn_Q")):

                if (name[-6:] == "Demand") or (name[-1] == "D"):
                    self.elDemandVector.append(self.monDataDf[name])  # Why not .values ??
                    self.legendEl.append(self.getNiceLatexNames(name))

            elif len(name) > 8 and name[0:8] == "qSysOut_":

                if (name[-6:] == "Demand") or (name[-1] == "D"):
                    self.qDemandVector.append(self.monDataDf[name].values)
                    self.qDemandDf = self.qDemandDf + self.monDataDf[name]
                    self.legendQ.append(self.getNiceLatexNames(name))

        self.qDemand = num.zeros(12)

        for i in range(len(self.qDemandVector)):
            self.qDemand[: len(self.qDemandVector[i])] = (
                self.qDemand[: len(self.qDemandVector[i])] + self.qDemandVector[i]
            )

        self.monDataDf["qDemand"] = self.qDemand[:12].tolist()
        self.elDemand = num.zeros(12)

        for i in range(len(self.elDemandVector)):
            self.elDemand[: len(self.elDemandVector[i])] = (
                self.elDemand[: len(self.elDemandVector[i])] + self.elDemandVector[i]
            )

        # self.monDataDf["qDemand"]=self.qDemandDf
        # self.deckData["qDemand_Tot"]=sum(self.qDemandDf)
        #
        # pass

    def addDemands(self, unit="kWh"):

        if unit == "kWh":
            myUnit = 1.0
        elif unit == "MWh":
            myUnit = 1000.0
        elif unit == "GWh":
            myUnit = 1e6
        else:
            raise ValueError("unit %s not considered" % unit)

        legend = ["Month"] + self.legendQ + ["Total"]

        caption = "Heat Demand"
        nameFile = "HeatDemand"
        addLines = False

        var = self.qDemandVector
        for i in range(len(var)):
            var[i] = var[i] / myUnit

        var.append(self.qDemand / myUnit)

        units = []
        units.append(unit)

        self.doc.addTableMonthlyDf(
            var, legend, units, caption, nameFile, self.myShortMonths, sizeBox=15, addLines=addLines
        )

    def addSPFSystem(self, printData=True):
        if max(self.qDemand) > 0 and not isinstance(self.elHeatSysTotal, int):

            self.SpfShpDis = num.zeros(13)  # SPF_shp including el. demand of cond., evap., and solar loop pumps
            self.SpfShpDisPen = num.zeros(13)  # SPF_shp with penalties for low room or DHW temperature
            self.SpfShpDisPlus = num.zeros(13)  # SPF_shp with all pumps (including SH and DHW circulation pump)

            for i in range(len(self.elHeatSysTotalPumps)):
                if self.elHeatSysTotalPumps[i] == 0:
                    self.SpfShpDis[i] = 0.0
                else:
                    self.SpfShpDis[i] = self.qDemand[i] / self.elHeatSysTotalPumps[i]

            for i in range(len(self.elHeatSysTotalPen)):
                if self.elHeatSysTotalPen[i] == 0:
                    self.SpfShpDisPen[i] = 0.0
                else:
                    self.SpfShpDisPen[i] = self.qDemand[i] / self.elHeatSysTotalPen[i]

            for i in range(len(self.elHeatSysTotalPlus)):
                if self.elHeatSysTotalPlus[i] == 0:
                    self.SpfShpDisPlus[i] = 0.0
                else:
                    self.SpfShpDisPlus[i] = self.qDemand[i] / self.elHeatSysTotalPlus[i]

            self.monDataDf["SpfShpDis"] = self.SpfShpDis[:12].tolist()
            self.monDataDf["SpfShpDisPen"] = self.SpfShpDisPen[:12].tolist()
            self.monDataDf["SpfShpDisPlus"] = self.SpfShpDisPlus[:12].tolist()

            self.yearQDemand = sum(self.qDemand)
            self.yearElHeatSysTotalPen = sum(self.elHeatSysTotalPen)
            self.yearElHeatSysTotalPlus = sum(self.elHeatSysTotalPlus)
            self.yearElHeatSysTotalPumps = sum(self.elHeatSysTotalPumps)

            self.yearSpfShpDis = self.yearQDemand / self.yearElHeatSysTotalPumps  ## including Cond/Evap/Solar pumps
            self.yearSpfShpDisPen = self.yearQDemand / self.yearElHeatSysTotalPen  ## including Penalties
            self.yearSpfShpDisPlus = (
                self.yearQDemand / self.yearElHeatSysTotalPlus
            )  ## including SH und DHW circulation pumps

            self.SpfShpDis[12] = self.yearSpfShpDis
            self.SpfShpDisPen[12] = self.yearSpfShpDisPen
            self.SpfShpDisPlus[12] = self.yearSpfShpDisPlus

            var = []

            qD = self.qDemand
            qD = num.append(qD, sum(self.qDemand))

            var.append(qD)

            el = self.elHeatSysTotal
            el = num.append(el, sum(self.elHeatSysTotalPumps))

            var.append(el)
            var.append(self.SpfShpDis)
            var.append(self.SpfShpDisPlus)
            var.append(self.SpfShpDisPen)

            nameFile = "SPF_SHP"
            legend = ["Month", "$Q_{demand}$", "$El_{Heat,Sys}$", "$SPF_{SHP}$", "$SPF_{SHP}+$", "$SPF_{SHP,Pen}$"]
            caption = "Seasonal performance factor of the complete system"
            self.doc.addTableMonthlyDf(
                var, legend, ["", "kWh", "kWh", "-", "-"], caption, nameFile, self.myShortMonths, sizeBox=15
            )

            yearlyFactor = 10.0

            namePdf = self.plot.plotMonthlyDf(
                self.SpfShpDis,
                "$SPF_{SHP}$",
                nameFile,
                yearlyFactor,
                self.myShortMonths,
                myTitle=None,
                printData=self.printDataForGle,
            )

            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

            if self.inputs["addWeightedSPF"] == True:
                self.SPFShpWeighted = num.zeros(13)

                self.SPFShpWeighted[12] = self.yearSpfShpDis

                for i in range(len(self.qDemand)):
                    self.SPFShpWeighted[i] = self.SpfShpDis[i] * self.qDemand[i] / sum(self.qDemand)

                nameFile = "SPF_SHP_weighted"

                namePdf = self.plot.plotMonthlyDf(
                    self.SPFShpWeighted,
                    "$\widetilde{SPF_{SHP}}$",
                    nameFile,
                    yearlyFactor,
                    self.myShortMonths,
                    myTitle=None,
                    printData=self.printDataForGle,
                )

                self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addEPFSystem(self, printData=True):

        self.elSys = num.zeros(12)
        self.elH = num.zeros(12)
        self.elPv = num.zeros(12)
        self.elGrid = num.zeros(12)
        self.elExp = num.zeros(12)
        self.elNetE = num.zeros(12)
        self.EPF = num.zeros(12)

        for c, value in enumerate(self.elDemandVector):
            if value.name in [
                "elSysOut_PuShDemand",
                "elSysOut_CtrlDemand",
                "elSysIn_Q_TesDhwAuxD",
                "elSysIn_Q_TesShAuxD",
                "elSysIn_Q_HpCompD",
            ]:
                self.elSys += value.values
            elif value.name == "elSysOut_HHDemand":
                self.elH = value.values

        self.elPv = self.monDataDf["elSysIn_PV"]
        self.elGrid = self.monDataDf["elSysIn_Grid"]
        self.elExp = self.monDataDf["elSysOut_PvToGrid"]
        self.elNetE = self.elGrid - self.elExp

        self.EPF = (self.elSys + self.elH) / (self.elPv + self.elGrid - self.elExp)

        self.EPF_yearly = (self.elSys.sum() + self.elH.sum()) / (self.elPv.sum() + self.elGrid.sum() - self.elExp.sum())

        nameFile = "Electrical_Performance_Factor"
        legend = ["Month", "$Q_{demand}$", "$El_{Heat,Sys}$", "$SPF_{SHP}$"]
        caption = "Electrical Performance Factor"
        # self.doc.addTableMonthlyDf(var, legend, ["", "kWh", "kWh", "-"], caption, nameFile, self.myShortMonths,
        #                            sizeBox=15)
        yearlyFactor = 1
        epfToPlot = num.append(self.EPF.values, self.EPF_yearly)

        namePdf = self.plot.plotMonthlyDf(
            epfToPlot,
            "electrical performance factor $\eta_{El}$ $[-]$",
            nameFile,
            yearlyFactor,
            self.myShortMonths,
            myTitle=None,
            printData=self.printDataForGle,
        )

        self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def calcConfigEquations(self):
        for equation in self.inputs["calcMonthlyTest"]:
            kwargs = {
                "local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax, **self.yearlyAvg}
            }
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.monDataDf.eval(equation, inplace=True, **kwargs)
            value = splitEquation[0].strip()
            self.monDataDf["Cum_" + value] = self.monDataDf[value].cumsum()
            self.yearlySums = {value + "_Tot": self.monDataDf[value].sum() for value in self.monDataDf.columns}

        for equation in self.inputs["calcMonthlyMin"]:
            splitEquation = equation.split("=")
            elem1 = splitEquation[1].split(",")[0][5:]  # removing max(
            elem2 = splitEquation[1].split(",")[1][:-1]

            value = splitEquation[0].strip()

            self.monDataDf[value] = self.monDataDf[elem1]
            for i in range(len(self.monDataDf[elem1])):
                self.monDataDf[value].values[i] = min(self.monDataDf[elem1].values[i], self.monDataDf[elem2].values[i])

            self.monDataDf["Cum_" + value] = self.monDataDf[value].cumsum()
            self.yearlySums = {value + "_Tot": self.monDataDf[value].sum() for value in self.monDataDf.columns}

        for equation in self.inputs["calc"]:
            namespace = {
                **self.deckData,
                **self.__dict__,
                **self.yearlySums,
                **self.yearlyMin,
                **self.yearlyMax,
                **self.yearlyAvg,
            }
            expression = equation.replace(" ", "")
            exec(expression, globals(), namespace)
            self.deckData = namespace
            logger.debug(expression)

        for equation in self.inputs["calcMonthly"]:
            kwargs = {
                "local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax, **self.yearlyAvg}
            }
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.monDataDf.eval(equation, inplace=True, **kwargs)
            value = splitEquation[0].strip()
            self.monDataDf["Cum_" + value] = self.monDataDf[value].cumsum()
            self.yearlySums = {value + "_Tot": self.monDataDf[value].sum() for value in self.monDataDf.columns}
        for equation in self.inputs["calcDaily"]:
            kwargs = {"local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax}}
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.dayDataDf.eval(equation, inplace=True, **kwargs)
            self.yearlyMin = {value + "_Min": self.dayDataDf[value].min() for value in self.dayDataDf.columns}
            self.yearlyMax = {value + "_Max": self.dayDataDf[value].max() for value in self.dayDataDf.columns}
            self.cumSumEnd = {value + "_End": self.dayDataDf[value][-1] for value in self.dayDataDf.columns}
            self.yearlyAvg = {value + "_Avg": self.dayDataDf[value].mean() for value in self.houDataDf.columns}

        for equation in self.inputs["calcHourly"]:
            kwargs = {
                "local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax, **self.yearlyAvg}
            }
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.houDataDf.eval(equation, inplace=True, **kwargs)
            self.yearlyMin = {value + "_Min": self.houDataDf[value].min() for value in self.houDataDf.columns}
            self.yearlyMax = {value + "_Max": self.houDataDf[value].max() for value in self.houDataDf.columns}
            self.cumSumEnd = {value + "_End": self.houDataDf[value][-1] for value in self.houDataDf.columns}
            self.yearlyAvg = {value + "_Avg": self.houDataDf[value].mean() for value in self.houDataDf.columns}

        for equation in self.inputs["calcMonthlyFromHourly"]:
            kwargs = {"local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax}}
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.houDataDf.eval(equation, inplace=True, **kwargs)
            calculatedVariableName = splitEquation[0].strip()
            calculatedVariableDf = self.houDataDf[calculatedVariableName]
            calculatedVariableMonth = num.array(calculatedVariableDf.index.month)
            calculatedVariable = calculatedVariableDf.to_numpy()
            calculatedVariablePerMonth = []
            for month in num.arange(1, 13, 1):
                support = num.where(calculatedVariableMonth == month, 1, 0)
                calculatedVariablePerMonth.append(num.dot(support, calculatedVariable))
            self.monDataDf[calculatedVariableName] = calculatedVariablePerMonth
            self.yearlyMin = {value + "_Min": self.houDataDf[value].min() for value in self.houDataDf.columns}
            self.yearlyMax = {value + "_Max": self.houDataDf[value].max() for value in self.houDataDf.columns}
            self.cumSumEnd = {value + "_End": self.houDataDf[value][-1] for value in self.houDataDf.columns}
            self.yearlyAvg = {value + "_Avg": self.houDataDf[value].mean() for value in self.houDataDf.columns}

        for equation in self.inputs["calcCumSumHourly"]:
            for value in equation:
                for key in self.houDataDf.columns:
                    if key == value:
                        self.houDataDf["cumsum_" + value] = self.houDataDf[value].cumsum()
                        myValue = "cumsum_" + value
                        self.cumSumEnd = {myValue + "_End": self.houDataDf[myValue][-1]}
        for equation in self.inputs["calcHourlyTest"]:
            kwargs = {"local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax}}
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.houDataDf.eval(equation, inplace=True, **kwargs)
            value = splitEquation[0]
            # self.yearlyMax = {value + '_Ma': self.houDataDf[value].max()}
            self.yearlyMin = {value + "_Min": self.houDataDf[value].min() for value in self.houDataDf.columns}
            self.yearlyMax = {value + "_Max": self.houDataDf[value].max() for value in self.houDataDf.columns}
            self.cumSumEnd = {value + "_End": self.houDataDf[value][-1] for value in self.houDataDf.columns}
            self.yearlyAvg = {value + "_Avg": self.houDataDf[value].mean() for value in self.houDataDf.columns}

        for equation in self.inputs["calcTimeStep"]:
            kwargs = {"local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax}}
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.steDataDf.eval(
                equation, inplace=True, **kwargs
            )  # by doing so we add also the key into the dictionary steDataDf
            self.yearlyMin = {value + "_Min": self.steDataDf[value].min() for value in self.steDataDf.columns}
            self.yearlyMax = {value + "_Max": self.steDataDf[value].max() for value in self.steDataDf.columns}

        for equation in self.inputs["calcCumSumTimeStep"]:
            for value in equation:
                for key in self.steDataDf.columns:
                    if key == value:
                        self.steDataDf["cumsum_" + value] = self.steDataDf[value].cumsum()

        for equation in self.inputs[
            "calcTimeStepTest"
        ]:  # dirty trick to be able to use it also after calcCumSumTimeStep DC
            kwargs = {"local_dict": {**self.deckData, **self.yearlySums, **self.yearlyMin, **self.yearlyMax}}
            scalars = kwargs["local_dict"].keys()
            splitEquation = equation.split("=")
            parsedEquation = splitEquation[1].replace(" ", "").replace("^", "**")
            parts = re.split(r"[*/+-]", parsedEquation.replace(r"(", "").replace(r")", ""))
            for scalar in scalars:
                if scalar in parts:
                    equation = equation.replace(scalar, "@" + scalar)
            self.steDataDf.eval(equation, inplace=True, **kwargs)
            self.yearlyMin = {value + "_Min": self.steDataDf[value].min() for value in self.steDataDf.columns}
            self.yearlyMax = {value + "_Max": self.steDataDf[value].max() for value in self.steDataDf.columns}

        for equation in self.inputs["calcTest"]:
            namespace = {
                **self.deckData,
                **self.__dict__,
                **self.yearlySums,
                **self.yearlyMin,
                **self.yearlyMax,
                **self.yearlyAvg,
            }
            expression = equation.replace(" ", "")
            exec(expression, globals(), namespace)
            self.deckData = namespace
            logger.debug(expression)

    def addPlotConfigEquation(self):
        for equation in self.inputs["calcMonthly"]:

            parameters = re.findall(r"[\w']+", equation)

            # monplot = sns.barplot(x=self.monDataDf['Month'], y=self.monDataDf[parameters[0]], color="blue")
            #
            # fig = monplot.get_figure()
            # fig.savefig(os.path.join(self.outputPath,('monthlyFigure' + parameters[0] + '.pdf')))
            #
            # for i in range(12):
            #     # We only consider if the qSol is lower than the demand, the rest will be lost in the storage
            #     qSolar = min(qCol[i], qDhw[i])
            #     fSolar[i] = qSolar / qDhw[i]
            #     sumCol = sumCol + qSolar
            #
            # self.monDataDf["fSolar"] = fSolar
            #
            # self.yearlyFsol = sumCol / sum(qDhw)
            #
            # yearlyFactor = self.yearlyFsol

            nameFile = "Fsolar"
            values = self.monDataDf[parameters[0]].values
            averageValue = values.mean()

            namePdf = self.plot.plotMonthlyDf(
                values,
                parameters[0],
                parameters[0],
                averageValue,
                self.myShortMonths,
                useYearlyFactorAsValue=True,
                myTitle=None,
                printData=self.printDataForGle,
                plotEmf=self.inputs["plotEmf"],
            )

            caption = parameters[0]

            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

            nameFile = parameters[0]
            legend = ["Month", parameters[0]]

            # var = []
            # var.append(fSolar)

            # self.doc.addTableMonthlyDf(values, legend, ["", "-"], caption, nameFile, self.myShortMonths,
            #                            sizeBox=15)

    def loadQvsTConfig(
        self, df, inputs, year=False, useOnlyOneYear=False, monthsSplit=[], normalized=False, cut=False, factor=1
    ):

        self.QvsTInput = inputs

        tFlow = []
        eCum = []
        legend = []
        factor = factor / 1000.0  # from kWh to MWh

        if "QvsTnormalized" in self.inputs.keys():
            self.QvsTNorm = self.inputs["QvsTnormalized"]
            norm = 0.0
            normalized = True
            for i in range(0, len(self.QvsTNorm)):
                norm = norm + max(num.cumsum(df[self.QvsTNorm[i]].values * factor))
        else:
            norm = 1.0
            normalized = False

        for i in range(0, len(self.QvsTInput)):

            # legend.append(jsonDict["legend"])
            if i % 2 == 0:
                eCum.append(abs(df[self.QvsTInput[i]].values) * factor / norm)
                name = self.QvsTInput[i]
                legend.append(self.getNiceLatexNames(name))
            else:
                tFlow.append(df[self.QvsTInput[i]])

        # df.columns = df.columns.str.lower()
        # SPACE HEATING DEMAND

        # self.readTrnsysFiles.timeStepUsed * self.unit.getkJToMWh()  # from kW to MWh
        # nameLatex = self.inputs["nameLatex"]
        # test = self.doc.getLatexNamesDict(nameLatex)

        fileName = "QvsT"

        self.plot.calcAndPrintQVersusT(fileName, tFlow, eCum, legend, printEvery=100, normalized=normalized, cut=cut)

        namePdf = self.plot.gle.executeGLE(fileName + ".gle")

        self.addPlotToLaTeX = {namePdf: "Cumulative energy flow as function of reference temperature"}
        # self.doc.addPlot(namePdf, "Cumulative energy flow as function of reference temperature", fileName, 12)

        for mIndex in range(len(monthsSplit)):
            timeStepInSeconds = self.readTrnsysFiles.timeStepUsed
            month = monthsSplit[mIndex]
            # Energy values in W*second
            iBegin, iEnd = utils.getMonthlySliceFromUserDefinedTimeStep(
                tShFl, timeStepInSeconds, month, firstHourInYear=self.firstConsideredTime
            )

            fileName = "QvsT-month-%d" % month

            tFlow = []
            eCum = []
            legend = []

            for i in range(0, len(self.test)):

                if i % 2 == 0:
                    eCum.append(abs(df[self.QvsTInput[i]]) * factor / norm)
                    name = self.QvsTInput[i]
                    legend.append(self.getNiceLatexNames(name))
                else:
                    tFlow.append(df[self.QvsTInput[i]])

            self.plot.calcAndPrintQVersusT(fileName, tFlow, eCum, legend, printEvery=100)

    def addElBalance(self, unit="kWh"):
        if unit == "kWh":
            myUnit = 1.0
        elif unit == "MWh":
            myUnit = 1000.0
        elif unit == "GWh":
            myUnit = 1e6
        else:
            raise ValueError("unit %s not considered" % unit)
        inVar = []
        outVar = []
        legendsIn = []
        legendsOut = []

        for name in self.monDataDf.columns:

            found = False

            try:
                if name[0:9] == "elSysOut_" or name[0:10] == "elSysIn_Q_":
                    # outVar.append(self.monData[name])
                    outVar.append(self.monDataDf[name].values / myUnit)

                    legendsOut.append(self.getNiceLatexNames(name))
                elif name[0:8] == "elSysIn_":
                    # inVar.append(self.monData[name])
                    inVar.append(self.monDataDf[name].values / myUnit)
                    legendsIn.append(self.getNiceLatexNames(name))

            except:
                pass

        nameFile = "ElMonthly"

        niceLegend = legendsIn + legendsOut

        if len(inVar) > 0 or len(outVar) > 0:
            namePdf = self.plot.plotMonthlyBalanceDf(
                inVar,
                outVar,
                niceLegend,
                "Energy Flows",
                nameFile,
                unit,
                self.myShortMonths,
                yearlyFactor=10,
                useYear=False,
                printData=self.printDataForGle,
                plotEmf=self.inputs["plotEmf"],
            )

            for i in range(len(outVar)):
                outVar[i] = -outVar[i]

            var = inVar + outVar
            var.append(sum(inVar) + sum(outVar))

            names = ["Month"] + niceLegend + ["Imb"]

            caption = "System Electricity Balance"

            totalDemand = sum(self.elDemand) / myUnit

            imb = sum(var[len(var) - 1])

            addLines = ""
            symbol = "\%"
            line = "\\hline \\\\ \n"
            addLines = addLines + line
            line = "$El_D$ & %.2f & MWh \\\\ \n" % (totalDemand / 1000.0)
            addLines = addLines + line
            line = "Imb & %.1f & %s \\\\ \n" % (100 * imb / totalDemand, symbol)
            addLines = addLines + line

            self.doc.addTableMonthlyDf(
                var, names, unit, caption, nameFile, self.myShortMonths, sizeBox=15, addLines=addLines
            )
            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addHeatBalance(self, printData=False, unit="kWh"):

        if unit == "kWh":
            myUnit = 1.0
        elif unit == "MWh":
            myUnit = 1000.0
        elif unit == "GWh":
            myUnit = 1e6
        else:
            raise ValueError("unit %s not considered" % unit)

        inVar = []
        outVar = []
        legendsIn = []
        legendsOut = []

        # for name in self.monData.keys():
        for name in self.monDataDf.columns:

            found = False

            try:
                if name[0:7] == "qSysIn_" or name[0:10] == "elSysOut_Q_" or name[0:10] == "elSysIn_Q_":
                    # inVar.append(self.monData[name])
                    inVar.append(self.monDataDf[name].values / myUnit)
                    legendsIn.append(self.getNiceLatexNames(name))

                elif name[0:8] == "qSysOut_":
                    # outVar.append(self.monData[name])
                    outVar.append(self.monDataDf[name].values / myUnit)

                    legendsOut.append(self.getNiceLatexNames(name))
            except:
                pass

        nameFile = "HeatMonthly"

        niceLegend = legendsIn + legendsOut

        if len(inVar) > 0 or len(outVar) > 0:
            namePdf = self.plot.plotMonthlyBalanceDf(
                inVar,
                outVar,
                niceLegend,
                "Energy Flows",
                nameFile,
                unit,
                self.myShortMonths,
                yearlyFactor=10,
                useYear=False,
                printData=self.printDataForGle,
                plotEmf=self.inputs["plotEmf"],
            )

            for i in range(len(outVar)):
                outVar[i] = -outVar[i]

            var = inVar + outVar
            var.append(sum(inVar) + sum(outVar))

            names = ["Month"] + niceLegend + ["Imb"]

            caption = "System Heat Balance"

            totalDemand = sum(self.qDemand) / myUnit

            imb = sum(var[len(var) - 1])

            addLines = ""
            symbol = "\%"
            line = "\\hline \\\\ \n"
            addLines = addLines + line
            line = "$Q_D$ & %.2f & MWh \\\\ \n" % (totalDemand / 1000.0)
            addLines = addLines + line
            line = "Imb & %.1f & %s \\\\ \n" % (100 * imb / totalDemand, symbol)
            addLines = addLines + line

            self.doc.addTableMonthlyDf(
                var, names, unit, caption, nameFile, self.myShortMonths, sizeBox=15, addLines=addLines
            )
            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addHeatBalanceDaily(self, month, printData=False, unit="kWh"):

        if unit == "kWh":
            myUnit = 1.0
        elif unit == "MWh":
            myUnit = 1000.0
        elif unit == "GWh":
            myUnit = 1e6
        else:
            raise ValueError("unit %s not considered" % unit)

        inVar = []
        outVar = []
        legendsIn = []
        legendsOut = []

        # selectedDays_list = daysSelected.split(" ")   #eval(daysSelected.split()[0])
        monthDate = datetime.strptime(month, "%B")
        monthNr = datetime.strftime(monthDate, "%m")
        monthNr = int(monthNr)
        if monthNr > 10:
            getDate = datetime(year=2018, month=monthNr, day=1)
            endDate = datetime(year=2018, month=monthNr + 1, day=1)
        else:
            getDate = datetime(year=2019, month=monthNr, day=1)
            endDate = datetime(year=2019, month=monthNr + 1, day=1)
        difference = endDate - getDate
        diffSeconds = difference.total_seconds()
        NrDays = int(diffSeconds / (60 * 60 * 24))
        Days = num.arange(NrDays)
        selectedDays_list = getDate + pd.to_timedelta(Days, unit="d")

        nr = len(selectedDays_list)

        selectedDays = []
        count = num.arange(nr)
        for i in count:
            help = selectedDays_list[i]
            selectedDays.append(help)

        # period = selectedDays[0]#+pd.to_timedelta('1 day')
        # month = datetime.strptime(self.firstMonth, '%B').month,
        Date = datetime(year=2018, month=1, day=1) + pd.to_timedelta(self.houDataDf["Time"], unit="h")
        df_selectedDay = self.houDataDf
        df_selectedDay["Date"] = Date
        #  df_selectedDay["Date"] = df_selectedDay["DateTime"].date()
        #  Test = df_selectedDay.groupby("Date").cumsum()

        numDays = len(selectedDays)
        Days = num.arange(numDays)

        # Test = pd.DataFrame()
        DaysSelected = pd.DataFrame()
        for i in Days:

            min_time = selectedDays[i]
            max_time = selectedDays[i] + pd.to_timedelta(23, unit="h")

            df_DataSelected = df_selectedDay[(df_selectedDay["Date"] <= max_time) & (df_selectedDay["Date"] >= min_time)]
            Test = pd.DataFrame(df_DataSelected.sum(), df_DataSelected.columns)
            Test2 = Test.T
            Test2["Date"] = min_time.date()

            DaysSelected = DaysSelected.append(Test2)

        for name in DaysSelected.columns:

            found = False

            try:
                if name[0:7] == "qSysIn_" or name[0:10] == "elSysOut_Q_" or name[0:10] == "elSysIn_Q_":
                    # inVar.append(self.monData[name])
                    inVar.append(DaysSelected[name].values / myUnit)
                    legendsIn.append(self.getNiceLatexNames(name))

                elif name[0:8] == "qSysOut_":
                    # outVar.append(self.monData[name])
                    outVar.append(DaysSelected[name].values / myUnit)

                    legendsOut.append(self.getNiceLatexNames(name))
            except:
                pass

        nameFile = "HeatDaily_" + month

        niceLegend = legendsIn + legendsOut
        nrOfDays = len(DaysSelected)

        legendDates = num.arange(nrOfDays) + 1

        xLegend = "Month " + month

        if len(inVar) > 0 or len(outVar) > 0:

            namePdf = self.plot.plotDailyBalanceDf(
                inVar,
                outVar,
                legendDates,
                niceLegend,
                "Energy Flows Daily",
                xLegend,
                nameFile,
                unit,
                self.myShortMonths,
                useYear=False,
                printData=self.printDataForGle,
                plotEmf=self.inputs["plotEmf"],
            )

            for i in range(len(outVar)):
                outVar[i] = -outVar[i]

            var = inVar + outVar
            var.append(sum(inVar) + sum(outVar))

            names = ["Month"] + niceLegend + ["Imb"]

            caption = "System Heat Balance"

            totalDemand = sum(self.qDemand) / myUnit

            imb = sum(var[len(var) - 1])

            addLines = ""
            symbol = "\%"
            line = "\\hline \\\\ \n"
            addLines = addLines + line
            line = "$Q_D$ & %.2f & MWh \\\\ \n" % (totalDemand / 1000.0)
            addLines = addLines + line
            line = "Imb & %.1f & %s \\\\ \n" % (100 * imb / totalDemand, symbol)
            addLines = addLines + line

            # self.doc.addTableMonthlyDf(var, names, unit, caption, nameFile, self.myShortMonths, sizeBox=15,
            #                                       addLines=addLines)
            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addHeatBalanceHourly(self, daySelected, printData=False, unit="kWh"):

        if unit == "kWh":
            myUnit = 1.0
        elif unit == "MWh":
            myUnit = 1000.0
        elif unit == "GWh":
            myUnit = 1e6
        else:
            raise ValueError("unit %s not considered" % unit)

        inVar = []
        outVar = []
        legendsIn = []
        legendsOut = []

        selectedDays_list = daySelected  # eval(daysSelected.split()[0])

        nr = len(selectedDays_list)

        selectedDays = datetime.strptime(selectedDays_list, "%Y,%m,%d")

        # period = selectedDays  # +pd.to_timedelta('1 day')
        # month = datetime.strptime(self.firstMonth, '%B').month,
        getDate = datetime(year=2018, month=1, day=1) + pd.to_timedelta(self.houDataDf["Time"], unit="h")
        df_selectedDay = self.houDataDf
        df_selectedDay["Date"] = getDate
        #  df_selectedDay["Date"] = df_selectedDay["DateTime"].date()
        #  Test = df_selectedDay.groupby("Date").cumsum()

        # Test = pd.DataFrame()
        DaysSelected = pd.DataFrame()

        min_time = selectedDays
        max_time = selectedDays + pd.to_timedelta(23, unit="h")

        df_DataSelected = df_selectedDay[(df_selectedDay["Date"] <= max_time) & (df_selectedDay["Date"] >= min_time)]

        DaysSelected = df_DataSelected

        for name in DaysSelected.columns:

            found = False

            try:
                if name[0:7] == "qSysIn_" or name[0:10] == "elSysOut_Q_" or name[0:10] == "elSysIn_Q_":
                    # inVar.append(self.monData[name])
                    inVar.append(DaysSelected[name].values / myUnit)
                    legendsIn.append(self.getNiceLatexNames(name))

                elif name[0:8] == "qSysOut_":
                    # outVar.append(self.monData[name])
                    outVar.append(DaysSelected[name].values / myUnit)

                    legendsOut.append(self.getNiceLatexNames(name))
            except:
                pass

        niceLegend = legendsIn + legendsOut

        legendDates = num.arange(24)
        help = DaysSelected["Date"]
        XLabel = str(help[5].date())

        nameFile = "HeatHourly_" + XLabel
        if len(inVar) > 0 or len(outVar) > 0:

            namePdf = self.plot.plotDailyBalanceDf(
                inVar,
                outVar,
                legendDates,
                niceLegend,
                "Energy Flows Hourly",
                XLabel,
                nameFile,
                unit,
                useYear=False,
                printData=self.printDataForGle,
                plotEmf=self.inputs["plotEmf"],
            )

            for i in range(len(outVar)):
                outVar[i] = -outVar[i]

            var = inVar + outVar
            var.append(sum(inVar) + sum(outVar))

            names = ["Month"] + niceLegend + ["Imb"]

            caption = "System Heat Balance"

            totalDemand = sum(self.qDemand) / myUnit

            imb = sum(var[len(var) - 1])

            addLines = ""
            symbol = "\%"
            line = "\\hline \\\\ \n"
            addLines = addLines + line
            line = "$Q_D$ & %.2f & MWh \\\\ \n" % (totalDemand / 1000.0)
            addLines = addLines + line
            line = "Imb & %.1f & %s \\\\ \n" % (100 * imb / totalDemand, symbol)
            addLines = addLines + line

            # self.doc.addTableMonthlyDf(var, names, unit, caption, nameFile, self.myShortMonths, sizeBox=15,
            #                                       addLines=addLines)
            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def calculateElHeatConsumption(self):

        inVar = []
        outVar = []
        self.legendsElHeatConsumption = []
        self.legendsElHeatConsumptionPen = []
        self.legendsElHeatConsumptionPlus = []
        self.elHeatSysTotal = []  # vector of a sum of all electricity consumption used for the heating system
        self.elHeatSysMatrix = []  # matrix with all vectors included in the el consumption. For table printing and plot
        self.elHeatSysTotalPumps = []
        self.elHeatSysTotalPen = []
        self.elHeatSysTotalPlus = []
        self.elHeatSysMatrixPumps = []
        self.elHeatSysMatrixPen = []
        self.elHeatSysMatrixPlus = []
        # self.elHeatSysMatrix_allPumps = []

        for name in self.monDataDf.columns:

            found = False

            try:
                if name[0:10] == "elSysIn_Q_":
                    el = self.monDataDf[name].values
                    self.elHeatSysMatrix.append(el)
                    self.elHeatSysMatrixPumps.append(el)
                    self.elHeatSysMatrixPen.append(el)
                    self.elHeatSysMatrixPlus.append(el)
                    # self.elHeatSysMatrix_allPumps.append(el)
                    # self.elHeatSysTotal = self.elHeatSysTotal + el
                    self.legendsElHeatConsumption.append(self.getNiceLatexNames(name))

                if name[0:8] == "PelPuAux":  ## add el. demand pump
                    el = self.monDataDf[name].values
                    self.elHeatSysMatrixPumps.append(el)
                    self.elHeatSysMatrixPlus.append(el)
                    self.elHeatSysMatrixPen.append(el)
                    # self.elHeatSysTotal = self.elHeatSysTotal + el
                    self.legendsElHeatConsumption.append(self.getNiceLatexNames(name))

                if name[0:9] == "PelPuC_kW":  ## add el. demand pump
                    el = self.monDataDf[name].values * 2
                    self.elHeatSysMatrixPumps.append(el)
                    self.elHeatSysMatrixPlus.append(el)
                    self.elHeatSysMatrixPen.append(el)
                    # self.elHeatSysTotal = self.elHeatSysTotal + el
                    self.legendsElHeatConsumption.append(self.getNiceLatexNames(name))

                if name[0:4] == "Ppen":  ## add el. demand pump
                    el = self.monDataDf[name].values
                    self.elHeatSysMatrixPen.append(el)
                    # self.elHeatSysTotal = self.elHeatSysTotal + el
                    self.legendsElHeatConsumptionPen.append(self.getNiceLatexNames(name))

                if name[0:8] == "BoPuSHon":  ## add el. demand pump
                    PSHPump = (
                        (8600 / 3600) / self.deckData["RHOWAT"] * 0.25 * 100
                    )  # calculated via MfrBuiNom according to other el. pump power! results in about 60W-Pump
                    PCircPump = (150 / 3600) / self.deckData["RHOWAT"] * 0.25 * 100
                    el = self.monDataDf[name].values * PSHPump / 0.35
                    self.elHeatSysMatrixPlus.append(el)
                    self.legendsElHeatConsumptionPlus.append(self.getNiceLatexNames(name))
                    monthlyHours = [730 for i in range(12)]
                    monthlyHours = num.array(monthlyHours)
                    el2 = monthlyHours * PCircPump / 0.35
                    self.elHeatSysMatrixPlus.append(el2)

                    # self.elHeatSysTotal = self.elHeatSysTotal + el

            except:
                pass

        self.elHeatSysTotal = sum(self.elHeatSysMatrix)
        self.elHeatSysTotalPumps = sum(self.elHeatSysMatrixPumps)
        self.elHeatSysTotalPen = sum(self.elHeatSysMatrixPen)
        self.elHeatSysTotalPlus = sum(self.elHeatSysMatrixPlus)

    def addElConsumption(self):

        nameFile = "elHeatSysMonthly"

        legend = self.legendsElHeatConsumption
        inVar = self.elHeatSysMatrix
        outVar = []

        if len(inVar) > 0:
            namePdf = self.plot.plotMonthlyBalanceDf(
                inVar,
                outVar,
                legend,
                "El heat system",
                nameFile,
                "MWh",
                self.myShortMonths,
                yearlyFactor=10,
                useYear=False,
                printImb=False,
                printData=self.printDataForGle,
                plotEmf=self.inputs["plotEmf"],
            )

            var = inVar
            self.elHeatSysTotal = sum(inVar)
            var.append(self.elHeatSysTotal)

            names = ["Month"] + legend + ["Total"]

            caption = "System El Heat Balance"

            self.doc.addTableMonthlyDf(var, names, "kWh", caption, nameFile, self.myShortMonths, sizeBox=15)
            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addCustomMonthlyBars(self):
        if "monthlyBar" in self.inputs.keys():
            for name in self.inputs["monthlyBar"]:
                values = self.monDataDf[name].values
                averageValue = values.mean()

                namePdf = self.plot.plotMonthlyDf(
                    values,
                    name,
                    name,
                    averageValue,
                    self.myShortMonths,
                    useYearlyFactorAsValue=True,
                    myTitle=None,
                    printData=self.printDataForGle,
                    plotEmf=self.inputs["plotEmf"],
                )

                caption = name
                self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

                nameFile = name
                legend = ["Month", name]

    def addCustomBalance(self):
        if "monthlyBalance" in self.inputs.keys():
            for i in range(len(self.inputs["monthlyBalance"])):
                namePlot = self.inputs["monthlyBalance"][i][0]
                plotStyle = ""

                legend = []
                inVar = []
                for variable in self.inputs["monthlyBalance"][i]:
                    # legend = [self.getNiceLatexNames(name) if name[0]!='-' else self.getNiceLatexNames(name[1:]) for name in variables ]
                    # inVar = [self.monDataDf[name].values if name[0]!='-' else -self.monDataDf[name[1:]].values for name in variables]
                    # First name is now the name of the plot
                    # legend = [self.getNiceLatexNames(name) if name[0]!='-' else self.getNiceLatexNames(name[1:]) for name in variables[1:] ]
                    # inVar = [self.monDataDf[name].values if name[0]!='-' else -self.monDataDf[name[1:]].values for name in variables[1:]]
                    if ":" in variable:
                        plotStyle = variable.split(":")[-1]
                    elif variable != namePlot:
                        legend.append(
                            self.getNiceLatexNames(variable)
                        )  # if name[0]!='-' else self.getNiceLatexNames(name[1:]) for name in variables[1:] ]
                        inVar.append(
                            self.monDataDf[variable].values
                        )  # if name[0]!='-' else -self.monDataDf[name[1:]].values for name in variables[1:]]

                if plotStyle == "relative":
                    nameFile = namePlot + "_relative"
                else:
                    nameFile = namePlot  #'Balance'+'_'.join(variables)
                titlePlot = "Balance"
                titleOfPlot = (
                    titlePlot  # self.deckData['Simulation_MFH'] + ' (' + self.deckData['Umgebungstemperatur'] + ')'
                )
                namePdf = self.plot.plotMonthlyBalanceDf(
                    inVar,
                    [],
                    legend,
                    "Energy",
                    nameFile,
                    "MWh",
                    self.myShortMonths,
                    yearlyFactor=10,
                    useYear=False,
                    printData=self.printDataForGle,
                    plotEmf=self.inputs["plotEmf"],
                    style=plotStyle,
                    title=titleOfPlot,
                )  #
                caption = titlePlot
                tableNames = ["Month"] + legend + ["Total"]
                var = inVar
                var.append(sum(inVar))
                self.doc.addTableMonthlyDf(var, tableNames, "MWh", caption, nameFile, self.myShortMonths, sizeBox=15)

                self.addPlotToLaTeX = {namePdf: caption}

                # self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addHeatingLimitFit(self):
        """
        Prepare input for and call pytrnsys.plot.plotMatplotlib.plotHeatingLimitFit. The fitting parameters from calling
        this function are then saved into the respective results.json.

        author: mneugeba
        last changes: jschmidl june 2021

        This Function is KliKo specific and should not be included in the general pytrnsys package

        Parameters
        ---------

        Returns
        -------

        """
        if "fitHeatingLimit" in self.inputs.keys():

            inputs = self.inputs["fitHeatingLimit"][0]

            yAxisVariableName = inputs[0]
            timeStep = inputs[1]

            doPlot = True

            if 'noPlot' in inputs:
                doPLot = False

            if self.inputs["isTrnsys"]:
                climate = os.path.split(self.executingPath)[-1].split('_')[-1]
            else:
                climate = self.deckData["Umgebungstemperatur"]
            climateDataPath = (
                "R:\\Projekte\\BFE_KliKo\\02_AP2_Simulationen\\IDA_ICE_HSLU\\Simulation_MFH_Resultate\\KlimaDaten\\Luzern_"
                + climate
                + "_daily.csv"
            )
            self.loadClimateDataFile(climateDataPath)
            averageDailyTemperature = self.climateDf["TAIR_Deg-C"][0:365]

            if timeStep == "daily":
                yAxisVariable = self.dayDataDf[yAxisVariableName][0:365]
                fileName = "HeatingLimitFit_daily"
            elif timeStep == "hourly":
                yAxisVariable = self.houDataDf[yAxisVariableName][0:8760]
                fileName = "HeatingLimit_hourly"


            if self.inputs["isTrnsys"]:
                titleOfPlot = self.fileName + " (" + climate + ")"
            else:
                titleOfPlot = self.deckData["Simulation_MFH"] + " (" + climate + ")"

            if yAxisVariableName == 'qSysIn_Heat':
                yAxisVariableName = '$P_H$ [W]'

            if timeStep == "hourly":
                namePdf = self.plot.plotHeatingLimitFit(
                    averageDailyTemperature,
                    yAxisVariable,
                    fileName,
                    timeStep,
                    title=titleOfPlot,
                    yLabel=yAxisVariableName,
                    doPlot=doPlot
                )
            elif timeStep == "daily":
                namePdf, fitted_H, fitted_HG, RSquared = self.plot.plotHeatingLimitFit(
                    averageDailyTemperature,
                    yAxisVariable,
                    fileName,
                    timeStep,
                    title=titleOfPlot,
                    yLabel=yAxisVariableName,
                    doPlot=doPlot
                    )

                pathResultsJson = os.path.join(self.outputPath, self.fileName + "-results.json")
                if os.path.isfile(pathResultsJson):

                    with open(pathResultsJson, "r") as file:
                        resultsDict = json.load(file)

                    resultsDict["fit_HG_[deg-C]"] = fitted_HG
                    resultsDict["fit_H_[W/K]"] = fitted_H
                    resultsDict["fit_R2"] = RSquared

                    with open(pathResultsJson, "w") as file:
                        json.dump(resultsDict, file, indent=2, separators=(",", ": "), sort_keys=True)

    def addCustomStackedBar(self):
        if "monthlyStackedBar" in self.inputs.keys():
            for variables in self.inputs["monthlyStackedBar"]:
                legend = [
                    self.getNiceLatexNames(name) if name[0] != "-" else self.getNiceLatexNames(name[1:])
                    for name in variables
                ]
                inVar = [
                    self.monDataDf[name].values if name[0] != "-" else -self.monDataDf[name[1:]].values
                    for name in variables
                ]
                nameFile = "StackedBar" + "_".join(variables)
                titlePlot = "Balance"
                namePdf = self.plot.plotMonthlyBalanceDf(
                    inVar,
                    [],
                    legend,
                    "Energy",
                    nameFile,
                    "MWh",
                    self.myShortMonths,
                    yearlyFactor=10,
                    useYear=False,
                    printData=self.printDataForGle,
                    printImb=False,
                    plotEmf=self.inputs["plotEmf"],
                )
                caption = titlePlot
                tableNames = ["Month"] + legend
                var = inVar
                var.append(sum(inVar))
                self.doc.addTableMonthlyDf(var, tableNames, "kWh", caption, nameFile, self.myShortMonths, sizeBox=15)

                self.addPlotToLaTeX = {namePdf: caption}

                # self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addCustomNBar(self):
        if "monthlyBars" in self.inputs.keys():
            for variables in self.inputs["monthlyBars"]:
                legend = [
                    self.getNiceLatexNames(name) if name[0] != "-" else self.getNiceLatexNames(name[1:])
                    for name in variables
                ]
                inVar = [
                    self.monDataDf[name].values if name[0] != "-" else -self.monDataDf[name[1:]].values
                    for name in variables
                ]
                nameFile = "NBar" + "_".join(variables)
                titlePlot = "Balance"
                namePdf = self.plot.plotMonthlyNBar(
                    inVar, legend, "", nameFile, 10, self.myShortMonths, plotEmf=self.inputs["plotEmf"]
                )
                caption = titlePlot
                tableNames = ["Month"] + legend
                var = inVar
                var.append(sum(inVar))
                self.doc.addTableMonthlyDf(var, tableNames, "kWh", caption, nameFile, self.myShortMonths, sizeBox=15)

                self.addPlotToLaTeX = {namePdf: caption}

                # self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addCaseDefinition(
        self,
    ):

        caption = "General data"
        names = ["", "", "", ""]
        units = None
        symbol = "\%"

        lines = ""
        jointDicts = {
            **self.deckData,
            **self.__dict__,
            **self.yearlySums,
            **self.yearlyMin,
            **self.yearlyMax,
            **self.yearlyAvg,
            **self.cumSumEnd,
        }
        if "caseDefinition" in self.inputs.keys():
            for variable in self.inputs["caseDefinition"][0]:
                line = self.getNiceLatexNames(variable) + " & %2.1f& &  \\\\ \n" % (jointDicts[variable])
                lines = lines + line

        if "PpenDHW_kW_Tot" in self.yearlySums:
            line = self.getNiceLatexNames("PpenDHW_kW") + " & %2.1f& &  \\\\ \n" % (self.yearlySums["PpenDHW_kW_Tot"])
            lines = lines + line

        if "PpenSH_kW_Tot" in self.yearlySums:
            line = self.getNiceLatexNames("PpenSH_kW") + " & %2.1f& &  \\\\ \n" % (self.yearlySums["PpenSH_kW_Tot"])
            lines = lines + line

        line = "Simulation Time & %.1f (min/year) & \\\\ \n" % (self.calcTime / self.nYearsSimulated)
        lines = lines + line
        if self.nItProblems == 0:
            line = "$nIte_{erro}$ & %s & (%s) \\\\ \n" % (0, 0)
            lines = lines + line
        else:
            ite = self.nItProblems.split("(")
            line = "$nIte_{erro}$ & %s & (%s) \\\\ \n" % (ite[0], ite[1].split(")")[0])
            lines = lines + line

        line = "\\hline \\\\ \n"
        lines = lines + line

        label = "definitionTable"
        sizeBox = 14
        self.doc.addTable(caption, names, units, label, lines, useFormula=True)

    def addTemperatureFreq(self, printData=False):

        if "plotT" in self.inputs.keys():
            if len(self.inputs["plotT"]) > 0:
                for name in self.inputs["plotT"][0]:
                    nameFile = "tempFreqDis" + name
                    # name = self.inputs['plotT'][0]
                    outVar = []
                    temperature = self.houDataDf[name].values
                    namePdf = self.plot.plotTemperatureFrequency(self.outputPath, nameFile, name, temperature)

                    caption = "Temperature Frequency Distribution"

                    self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def getNiceLatexNames(self, name):
        if name in self.doc.latexNames:
            niceName = self.doc.latexNames[name]
        else:
            niceName = self.getCustomeNiceLatexNames(name)
            if niceName == None:
                niceName = "$%s$" % "".join([c for c in name if c in ascii_letters + digits])

        return niceName

    def getCustomeNiceLatexNames(self, name):
        return None

    def loadDll(self):

        self.log = LogTrnsys.LogTrnsys(self.outputPath, self.fileName)
        self.log.loadLog()
        self.log.getMyDataFromLog()
        self.calcTime = self.log.getCalculationTime()

        self.iteErrorMonth = self.log.getIteProblemsForEachMonth

        self.nItProblems = self.log.numberOfFailedIt

    def getVersionsDll(self):

        if 0:
            raise ValueError("Deprecated. File created in simulaiton folder. To be improved")
            #
            #        namesDll= ["type860","type1924","type709","type878","type859","Type832","Type833"]

            namesDll = []
            myset = set(self.readTrnsysFiles.TrnsysTypes)  # get the unique names (all repeated ones are excluded)
            logger.info(myset)

            for number in myset:
                nameType = "type%s" % number
                namesDll.append(nameType)

            self.dllVersions = self.getDllVersionFromType(namesDll)

            self.buildingModel = None
            for dll in self.dllVersions:
                logger.debug(dll)
                if dll[0:6] == "type56":
                    self.buildingModel = "Type56"
                elif dll[0:8] == "type5998":
                    self.buildingModel = "ISO"

    def getDllVersionFromType(self, typeNumber):

        if self.trnsysDllPath == False:

            if self.trnsysVersion == "standard":
                trnsysExe = os.getenv("TRNSYS_EXE")

            else:
                trnsysExe = os.getenv(self.trnsysVersion)

            logger.debug(trnsysExe)

            mySplit = trnsysExe.split("Exe")
            self.trnsysDllPath = mySplit[0] + "\\UserLib\\ReleaseDLLs"
        else:
            pass

        logger.debug("Dll path:%s" % self.trnsysDllPath)

        listDll = os.listdir(self.trnsysDllPath)

        dllVersion = []
        for name in typeNumber:
            nameFound = False
            for dll in listDll:
                if dll[-3:] == "dll":
                    #                    print "%s %s" % (dll,name)
                    if dll.count(name) == 1 and nameFound == False:
                        nameFound = True
                        dllVersion.append(dll)
                        logger.debug("FOUND %s %s" % (dll, name))
                        break

        logger.debug(dllVersion)
        #        raise ValueError()

        return dllVersion

    def getTagLabel(self, label):

        return "#=======================================\n#%s :%s\n#=======================================\n" % (
            self.nameClass,
            label,
        )

    def setPathReadTrnsysFile(self, _path):

        self.readTrnsysFiles.setPath(_path)

    def addResultsFile(self):
        """
        Save results to a results.json file.

        Function uses results stringArray from config file to provide keys that will be saved
        :return:
        """
        if "results" in self.inputs:
            logger.info("creating results.json file at " + self.outputPath)
            if "-" in self.fileName:
                self.resultsDict = {"Name": self.fileName.split("-")[1]}
            else:
                self.resultsDict = {}
            jointDicts = {
                **self.deckData,
                **self.monDataDf.to_dict(orient="list"),
                **self.__dict__,
                **self.yearlySums,
                **self.yearlyMin,
                **self.yearlyMax,
                **self.yearlyAvg,
                **self.cumSumEnd,
            }  # ,**self.maximumMonth,**self.minimumMonth}
            for key in self.inputs["results"][0]:
                if ":month" in key:
                    valueName = key.split(":")[0]
                    for monthNumber in range(0, 12):
                        self.resultsDict[valueName + "_" + self.myShortMonths[monthNumber]] = self.monDataDf[
                            valueName
                        ].iloc[monthNumber]
                elif type(jointDicts[key]) == num.ndarray:
                    value = list(jointDicts[key])
                elif isinstance(jointDicts[key], pd.Series):
                    value = list(jointDicts[key].values)
                else:
                    if type(jointDicts[key]) == num.ndarray:
                        value = list(jointDicts[key])
                    else:
                        value = jointDicts[key]
                    self.resultsDict[key] = value

            pathParameterJson = os.path.join(self.outputPath, self.fileName + ".json")
            if os.path.isfile(pathParameterJson):
                with open(pathParameterJson, "r") as file:
                    parameterDictionary = json.load(file)
                    self.resultsDict.update(parameterDictionary)

            fileName = self.fileName + "-results.json"
            fileNamePath = os.path.join(self.outputPath, fileName)

            if os.path.isfile(fileNamePath):

                tempDict = self.resultsDict

                with open(fileNamePath, "r") as file:
                    self.resultsDict = json.load(file)

                self.resultsDict.update(tempDict)

            with open(fileNamePath, "w") as fp:
                json.dump(self.resultsDict, fp, indent=2, separators=(",", ": "), sort_keys=True)

    def saveHourlyToCsv(self):
        """
        Saves hourly printer values to csv files. config file key is stringArray "hourlyToCsv" nameOfFile [variables,...]
        Returns
        -------
        """
        if "hourlyToCsv" in self.inputs:
            for stringArray in self.inputs["hourlyToCsv"]:
                pathFile = os.path.join(self.outputPath, stringArray[0] + ".csv")
                self.houDataDf[stringArray[1:]].to_csv(pathFile, sep=";")

    def plot_as_emf(self, figure, **kwargs):
        if "inkscape" in self.inputs:
            try:
                inkscape_path = kwargs.get("inkscape", self.inputs["inkscape"])
                filepath = kwargs.get("filename", None)

                if filepath is not None:
                    path, filename = os.path.split(filepath)
                    filename, extension = os.path.splitext(filename)

                    svg_filepath = os.path.join(path, filename + ".svg")
                    emf_filepath = os.path.join(path, filename + ".emf")
                    figure.savefig(svg_filepath, format="svg")
                    subprocess.call([inkscape_path, svg_filepath, "--export-emf", emf_filepath])
                    os.remove(svg_filepath)
            except:
                raise ValueError("Inkscape path is not set correctly.")

    def addImages(self):
        if "addImage" in self.inputs.keys():
            for image in self.inputs["addImage"][0]:
                if os.path.exists(image):
                    name = os.path.basename(image)
                    image = image.replace(os.path.sep, "//")
                    caption = self.getNiceLatexNames(name)
                    label = "scheme"
                    line = "\\begin{figure}[!ht]\n"
                    self.doc.lines = self.doc.lines + line
                    line = "\\begin{center}\n"
                    self.doc.lines = self.doc.lines + line
                    line = "\\includegraphics[width=1\\textwidth]{%s}\n" % (image.replace(r"\\", r"\\\\"))
                    self.doc.lines = self.doc.lines + line
                    line = "\\caption{%s}\n" % caption
                    self.doc.lines = self.doc.lines + line
                    line = "\\label{%s}\n" % label
                    self.doc.lines = self.doc.lines + line
                    line = "\\end{center}\n"
                    self.doc.lines = self.doc.lines + line
                    line = "\\end{figure}\n"
                    self.doc.lines = self.doc.lines + line
