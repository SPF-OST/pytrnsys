# pylint: skip-file
# type: ignore

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Child class from ProcessMonthlyDataBase used for processing all TRNSYS simulations.

Author : Dani Carbonell
Date   : 2018
ToDo :
"""

import os, subprocess
import re
import string, shutil
import pytrnsys.pdata.processFiles as spfUtils
import pytrnsys.psim.processMonthlyDataBase as monthlyData  # changed in order to clean the processing of files
import pytrnsys.utils.utilsSpf as utils
import time
import numpy as num
import matplotlib.pyplot as plt
import pytrnsys.trnsys_util.readTrnsysFiles as readTrnsysFiles
import pytrnsys.utils.unitConverter as unit
import pytrnsys.trnsys_util.LogTrnsys as LogTrnsys
from pytrnsys.psim.simulationLoader import SimulationLoader
import pandas as pd
import logging

logger = logging.getLogger("root")


class ProcessTrnsys(monthlyData.ProcessMonthlyDataBase):
    def __init__(self, _path, _name, language="en"):

        monthlyData.ProcessMonthlyDataBase.__init__(self, _path, _name, language=language)
        #
        #        self.fileName = _name.split('.')[0]
        #        self.outputPath = _path + "\%s" % self.fileName

        self.cleanModeLatex = False

        self.tempFolder = "%s\\temp" % self.outputPath
        self.tempFolderEnd = "%s\\temp" % self.outputPath

        self.trnsysVersion = "standard"
        self.yearReadedInMonthylFile = -1  # -1 means the last
        self.firstMonth = "January"

        self.yearlyFactor = 10.0  # value to divide yerarly values when plotted along with monthly data
        self.units = unit.UnitConverter()

        # self.qWcpHPPlusAux = num.zeros(12)
        # self.qHpAux = num.zeros(12)

        self.loadPCM = False
        self.solarFileLoaded = False  # To erase or to fill up depending on document class

        self.multiPort = False  # HighIce use Multiport and some symbols are changed. QLoss

        self.readTrnsysFiles = readTrnsysFiles.ReadTrnsysFiles(self.tempFolderEnd)

        # self.tInEvapHpMonthlyMax = num.zeros(12,float)
        # self.tInEvapHpMonthlyMin = num.zeros(12,float)
        # self.tInEvapHpMonthlyAv  = num.zeros(12,float)

        self.nameClass = "ProcessTrnsys"
        self.unit = unit.UnitConverter()
        self.trnsysDllPath = False
        self.summaryFile = os.path.join(self.executingPath, "Summary.dat")

    def plot_as_emf(self, figure, **kwargs):
        inkscape_path = kwargs.get("inkscape", "C://Program Files//Inkscape//inkscape.exe")
        filepath = kwargs.get("filename", None)

        if filepath is not None:
            path, filename = os.path.split(filepath)
            filename, extension = os.path.splitext(filename)

            svg_filepath = os.path.join(path, filename + ".svg")
            emf_filepath = os.path.join(path, filename + ".emf")

            figure.savefig(svg_filepath, format="svg")

            subprocess.call([inkscape_path, svg_filepath, "--export-emf", emf_filepath])
            os.remove(svg_filepath)

    def writeToSummaryFile(self, resultsDict):
        self.resultsDict = {}
        variations = self.fileName.split("-")[1:]
        names = [re.sub(r"[\d\.]", "", variation) for variation in variations]
        values = [re.sub(r"[^\d\.]", "", variation) for variation in variations]
        values = [value if len(value) > 0 else name for value, name in zip(values, names)]
        self.resultsDict = dict(zip(names, values))
        self.resultsDict = {**self.resultsDict, **resultsDict}
        if os.path.exists(self.summaryFile):
            written = False
            while not written:
                try:
                    file = open(self.summaryFile, "a")
                    file.write("\t".join(map(str, list(self.resultsDict.values()))) + "\n")
                    written = True
                except:
                    time.sleep(0.1)
                    logger.warning("Summary File Used By Other Process! Wait...")
        else:
            file = open(self.summaryFile, "w")
            file.write("\t".join(map(str, list(self.resultsDict.keys()))) + "\n")
            file.write("\t".join(map(str, list(self.resultsDict.values()))) + "\n")
        file.close()

    #    def readTrnsysDeck(self):

    # the idea is to read the deck and get important information fro processing.
    # area collector, volume ice storage, volume Tes, Area uncovered, nH1, nominal power heat pump, etc...
    def setBuildingArea(self, area):
        self.buildingArea = area

    def setTrnsysDllPath(self, path):

        self.trnsysDllPath = path

    def setBuildingArea(self, area):
        self.buildingArea = area

    def getNameCity(self, nCity):

        utils.getNameCity(nCity)

    def setTrnsysVersion(self, version):
        self.trnsysVersion = version

    def setPrintDataForGle(self, printData):

        self.printDataForGle = printData

    def loadAndProcess(self):

        self.loadFiles()
        self.process()
        self.doLatexPdf()

    def setLoaderParameters(self):

        self.monthlyUsed = True
        self.hourlyUsed = True
        self.timeStepUsed = True

        self.fileNameListToRead = False
        self.loadMode = "complete"

    def loadFiles(self):

        self.setLoaderParameters()
        self.loader = SimulationLoader(
            self.outputPath + "//temp",
            fileNameList=self.fileNameListToRead,
            mode=self.loadMode,
            monthlyUsed=self.monthlyUsed,
            hourlyUsed=self.hourlyUsed,
            timeStepUsed=self.timeStepUsed,
        )
        # self.monData = self.loader.monData
        self.monDataDf = self.loader.monDataDf
        self.houDataDf = self.loader.houDataDf

        self.myShortMonths = utils.getShortMonthyNameArray(self.monDataDf["Month"].values)

        logger.info("loadFiles completed using SimulationLoader")

    def process(self):

        pass

    def doLatexPdf(self, documentClass="SPFShortReportIndex"):

        self.createLatex(documentClass=documentClass)

        self.executeLatexFile()

    def addLatexContent(self):

        raise ValueError("process needs to be defined in each particuar child class")

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

            if len(name) > 9 and name[0:9] == "elSysOut_":

                if name[-6:] == "Demand":
                    self.elDemandVector.append(self.monDataDf[name])
                    self.legendEl.append(self.getNiceLatexNames(name))

            elif len(name) > 8 and name[0:8] == "qSysOut_":

                if name[-6:] == "Demand":
                    self.qDemandVector.append(self.monDataDf[name].values)
                    self.qDemandDf = self.qDemandDf + self.monDataDf[name]
                    self.legendQ.append(self.getNiceLatexNames(name))

        self.qDemand = num.zeros(12)

        for i in range(len(self.qDemandVector)):
            self.qDemand = self.qDemand + self.qDemandVector[i]

    def addDemands(self):

        legend = ["Month"] + self.legendQ + ["Total"]

        caption = "Heat Demand"
        nameFile = "HeatDemand"
        addLines = False

        var = self.qDemandVector
        var.append(self.qDemand)

        self.doc.addTableMonthlyDf(
            var, legend, "kWh", caption, nameFile, self.myShortMonths, sizeBox=15, addLines=addLines
        )

    def calculateSPFSystem(self):

        self.SpfShpDis = num.zeros(13)

        for i in range(len(self.qDemand)):
            if self.elHeatSysTotal[i] == 0:
                self.SpfShpDis[i] = 0.0
            else:
                self.SpfShpDis = [i] = self.qDemand[i] / self.elHeatSysTotal[i]

        self.yearSpfShpDis = sum(self.qDemand) / sum(self.elHeatSysTotal)
        self.SpfShpDis[12] = self.yearSpfShpDis

    def addSPFSystem(self, printData=False):

        var = []

        qD = self.qDemand
        qD = num.append(qD, sum(self.qDemand))

        var.append(qD)

        el = self.elHeatSysTotal
        el = num.append(el, sum(self.elHeatSysTotal))

        var.append(el)

        var.append(self.SPFSHP)

        nameFile = "SPF_SHP"
        legend = ["Month", "$Q_{demand}$", "$El_{Heat,Sys}$", "$SPF_{SHP}$"]
        caption = "Seasonal performance factor of the complete system"
        self.doc.addTableMonthlyDf(
            var, legend, ["", "kWh", "kWh", "-"], caption, nameFile, self.myShortMonths, sizeBox=15
        )

        yearlyFactor = 10.0

        namePdf = self.plot.plotMonthlyDf(
            self.SPFSHP, "$SPF_{SHP}$", nameFile, yearlyFactor, self.myShortMonths, myTitle=None, printData=printData
        )

        self.doc.addPlot(namePdf, caption, nameFile, 12)

    def addHeatBalance(self, printData=False):

        inVar = []
        outVar = []
        legendsIn = []
        legendsOut = []

        # for name in self.monData.keys():
        for name in self.monDataDf.columns:

            found = False

            try:
                if name[0:7] == "qSysIn_" or name[0:10] == "elSysIn_Q_":
                    # inVar.append(self.monData[name])
                    inVar.append(self.monDataDf[name].values)
                    legendsIn.append(self.getNiceLatexNames(name))

                elif name[0:8] == "qSysOut_":
                    # outVar.append(self.monData[name])
                    outVar.append(self.monDataDf[name].values)

                    legendsOut.append(self.getNiceLatexNames(name))
            except:
                pass

        nameFile = "HeatMonthly"

        niceLegend = legendsIn + legendsOut

        # firstMonthId = self.monDataDf["Month"].index[0]

        # firstMonthId = utils.getMonthNameIndex(self.monDataDf["Month"].index)
        # startMonth = firstMonthId

        namePdf = self.plot.plotMonthlyBalanceDf(
            inVar,
            outVar,
            niceLegend,
            "Energy Flows",
            nameFile,
            "kWh",
            self.myShortMonths,
            yearlyFactor=10,
            useYear=False,
            printData=printData,
        )

        for i in range(len(outVar)):
            outVar[i] = -outVar[i]

        var = inVar + outVar
        var.append(sum(inVar) + sum(outVar))

        names = ["Month"] + niceLegend + ["Imb"]

        caption = "System Heat Balance"

        totalDemand = sum(self.monData["qSysOut_DhwDemand"]) + sum(self.monData["qSysOut_BuiDemand"])

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
            var, names, "kWh", caption, nameFile, self.myShortMonths, sizeBox=15, addLines=addLines
        )
        self.doc.addPlot(namePdf, caption, nameFile, 12)

    def calculateElConsumption(self, printData=False):

        inVar = []
        outVar = []
        legends = []
        self.elHeatSysTotal = []  # vector of a sum of all electricity consumption used for the heating system
        self.elHeatSysMatrix = []  # matrix with all vectors included in the el consumption. For table printing and plot

        for name in self.monDataDf.columns:

            found = False

            try:
                if name[0:9] == "elSysOut_" or name[0:10] == "elSysIn_Q_":
                    el = self.monDataDf[name].values
                    self.elHeatSysMatrix.append(el)
                    # self.elHeatSysTotal = self.elHeatSysTotal + el
                    legends.append(self.getNiceLatexNames(name))
            except:
                pass

        self.elHeatSysTotal = sum(self.elHeatSysMatrix)

    def addElConsumption(self, printData=False):

        nameFile = "elHeatSysMonthly"

        niceLegend = legends

        inVar = self.elHeatSysMatrix

        namePdf = self.plot.plotMonthlyBalanceDf(
            inVar,
            outVar,
            niceLegend,
            "El heat system",
            nameFile,
            "kWh",
            self.myShortMonths,
            yearlyFactor=10,
            useYear=False,
            printImb=False,
            printData=printData,
        )

        var = inVar
        self.elHeatSysTotal = sum(inVar)
        var.append(self.elHeatSysTotal)

        names = ["Month"] + niceLegend + ["Total"]

        caption = "System El Heat Balance"

        self.doc.addTableMonthlyDf(var, names, "kWh", caption, nameFile, self.myShortMonths, sizeBox=15)
        self.doc.addPlot(namePdf, caption, nameFile, 12)

    def getListOfNiceLatexNames(self, legends):

        legendOut = []
        for name in legends:
            legendOut.append(self.getNiceLatexNames(name))

        return legendOut

    def getNiceLatexNames(self, name):

        name = name.lower()
        if name == "qSysOut_DhwDemand".lower():  # DHW demand
            niceName = "$Q_{DHW}$"

        elif name == "qSysOut_BuiDemand".lower():  # SH demand
            niceName = "$Q_{SH}$"

        elif name == "qSysIn_BuiDemand".lower():  # SC demand
            niceName = "$Q_{SC}$"

        elif name == "qSysIn_Collector".lower():  # Q solar
            niceName = "$Q_{col}$"

        elif name == "elSysIn_Q_HpComp".lower():  # Heat pump compressor
            niceName = "$El_{Hp,comp}$"

        elif name == "elSysOut_PuCond".lower():  # pump condenser
            niceName = "$El_{pu}^{cond}$"

        elif name == "elSysOut_PuEvap".lower():  # pump evaporator
            niceName = "$El_{pu}^{evap}$"

        elif name == "elSysOut_PuSH".lower():  # pump evaporator
            niceName = "$El_{pu}^{SH}$"

        elif name == "qSysOut_TesLoss".lower():  # losses TES
            niceName = "$Q^{Tes}_{loss}$"

        elif name == "qSysOut_TesDhwLoss".lower():  # losses TES DHW
            niceName = "$Q^{TesDhw}_{loss}$"

        elif name == "qSysOut_TesShLoss".lower():  # losses TES SH
            niceName = "$Q^{TesSh}_{loss}$"

        elif name == "qSysOut_PipeLoss".lower():  # losses pipes
            niceName = "$Q^{pipe}_{loss}$"

        elif name == "elSysOut_HHDemand".lower():  # Household Electricity demand
            niceName = "$El_{HH}$"

        elif name == "elSysIn_PV".lower():  # PV to the system
            niceName = "$El_{PV}$"

        elif name == "elSysOut_InvLoss".lower():  # Inverter losses
            niceName = "$El^{inv}_{loss}$"

        elif name == "elSysOut_BatLoss".lower():  # Batrtery losses
            niceName = "$El^{bat}_{loss}$"

        elif name == "elSysIn_Grid".lower():  # GRID to the system
            niceName = "$El_{grid}$"

        elif name == "elSysOut_PvToGrid".lower():  # Pv to GRID
            niceName = "$El_{Pv2Grid}$"

        elif name == "elSysIn_Q_TesShAux".lower():  # Auxiliar back up in Tes SH
            niceName = "$El_{Aux}^{TesSh}$"

        elif name == "elSysIn_Q_TesAux".lower():  # Auxiliar back up in Tes SH
            niceName = "$El_{Aux}^{Tes}$"

        elif name == "elSysIn_Q_TesDhwAux".lower():  # Auxiliar back up in Tes DHW
            niceName = "$El_{Aux}^{TesDhw}$"

        elif name == "qSysIn_Ghx".lower():  # Heat inputs grom GHX
            niceName = "$Q_{GHX}$"
        else:
            niceName = "$%s$" % name

        return niceName

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

    #############################################
    # Section for loading files
    #############################################

    def loadSolar(self, _name):

        self.readTrnsysFiles.readMonthlyFiles(_name, firstMonth=self.firstMonth, myYear=self.yearReadedInMonthylFile)

        self.numberOfMonthsSimulated = self.readTrnsysFiles.numberOfMonthsSimulated

        self.existSolarLoop = True
        self.solarFileLoaded = True

        self.qSolarToSystem = self.readTrnsysFiles.get("Pcoll_KW")
        self.qSunToCol = self.readTrnsysFiles.get("P_IRRAD_kW")
        self.qLossPipeSolarLoop = self.readTrnsysFiles.get("PPiCLoss_kW")

        #         print self.qSolarToSystem
        #         print self.qLossPipeSolarLoop

        if self.parallelSystem:
            for i in range(self.numberOfMonthsSimulated):
                self.qSolarToTes[i] = self.qSolarToSystem[i] - self.qLossPipeSolarLoop[i]
        else:
            logger.warning("Serial system and qSolartoTes must be readed from Storage data")

    def loadWeatherData(self, _name):

        self.readTrnsysFiles.readMonthlyFiles(_name, firstMonth=self.firstMonth, myYear=self.yearReadedInMonthylFile)
        self.numberOfMonthsSimulated = self.readTrnsysFiles.numberOfMonthsSimulated

        self.iTHorizontalkWPerM2 = self.readTrnsysFiles.get("IT_H_KW")
        self.iTColkWPerM2 = self.readTrnsysFiles.get(
            "IT_Coll_kW"
        )  # depracated, this should now be defined in SOLAR_MO.Prt
        self.tAmb = self.readTrnsysFiles.get("tAmb")

        if self.iTColkWPerM2 == None:
            self.iTColkWPerM2 = self.qIrradTilt

    def loadStorage(self, _name):

        self.readTrnsysFiles.readMonthlyFiles(_name, firstMonth=self.firstMonth, myYear=self.yearReadedInMonthylFile)
        self.numberOfMonthsSimulated = self.readTrnsysFiles.numberOfMonthsSimulated

        self.qTesFromSolar = abs(self.readTrnsysFiles.get("PSC_kW", ifNotFoundEqualToZero=True))
        self.qOutFromTesToSH = abs(self.readTrnsysFiles.get("PSB_kW", ifNotFoundEqualToZero=True))
        self.qOutFromTesToDHW = abs(self.readTrnsysFiles.get("PSD_kW", ifNotFoundEqualToZero=True))
        self.qLossTes = self.readTrnsysFiles.get("PSt_loss_kW", ifNotFoundEqualToZero=True)

        self.qTesDhwFromHp = self.readTrnsysFiles.get("PSA1_kW", ifNotFoundEqualToZero=True)
        self.qTesShFromHp = self.readTrnsysFiles.get("PSA2_kW", ifNotFoundEqualToZero=True)

        self.qTesFromHp = self.qTesShFromHp + self.qTesDhwFromHp

        if abs(sum(self.qTesFromHp) - (sum(self.qTesDhwFromHp) + sum(self.qTesShFromHp)) > 1):

            logger.warning(
                "Something goes wrong QTesFromHp:%f QTesFromHPDhwSh:%f "
                % (sum(self.qTesFromHp), sum(self.qTesDhwFromHp) + sum(self.qTesShFromHp))
            )

        self.qOutFromTes = num.zeros(12)

        for i in range(12):
            if self.multiPort:
                self.qLossTes[i] = -self.qLossTes[i]
            self.qOutFromTes[i] = self.qOutFromTesToSH[i] + self.qOutFromTesToDHW[i]

        #            print "qOutTnk:%f qOutTnkSH:%f qOutTnkDHW:%f" % (self.qOutFromTes[i],self.qOutFromTesToSH[i],self.qOutFromTesToDHW[i])

        self.qOutFromTesFound = True

    def loadBuilding(self, _name):

        self.readTrnsysFiles.readMonthlyFiles(_name, myYear=self.yearReadedInMonthylFile, firstMonth=self.firstMonth)
        # self.numberOfMonthsSimulated = self.readTrnsysFiles.numberOfMonthsSimulated

        self.qSHDemand = self.readTrnsysFiles.get("PheatBui_kW")

        self.qSC = self.readTrnsysFiles.get("PcoolBui_kW", ifNotFoundEqualToZero=True)

        self.qSHSCDemand = self.readTrnsysFiles.get("PtotBui_kW", ifNotFoundEqualToZero=True)

        self.qRadiator = self.readTrnsysFiles.get("PRdIn_kW", ifNotFoundEqualToZero=True)

        self.qSH = self.qSHDemand  # Changed !!

        self.qBuiGroundLosses = self.readTrnsysFiles.get("PBuiGrd_kW", ifNotFoundEqualToZero=True)

        self.qBuiIntGainPeople = self.readTrnsysFiles.get("PBuiGainPers_KW", ifNotFoundEqualToZero=True)
        self.qBuiIntGainEq = self.readTrnsysFiles.get("PBuiGainEq_KW", ifNotFoundEqualToZero=True)
        self.qBuiIntGainLight = self.readTrnsysFiles.get("PBuiLight_kW", ifNotFoundEqualToZero=True)

        self.qBuiSolarGains = self.readTrnsysFiles.get("PBuiSol_kW", ifNotFoundEqualToZero=True)
        self.qBuiRadiatorGains = self.readTrnsysFiles.get("PBuiGains_KW", ifNotFoundEqualToZero=True)

        self.qBuiTransLosses = self.readTrnsysFiles.get("PBuiUAstatic_kW")  #

        self.qBuiInfLosses = self.readTrnsysFiles.get("PbuiInf_kW", ifNotFoundEqualToZero=True)
        self.qBuiVentLosses = self.readTrnsysFiles.get("PbuiVent_kW", ifNotFoundEqualToZero=True)

        self.qShFromHp = self.readTrnsysFiles.get("QShFromHp", ifNotFoundEqualToZero=True)
        self.qShFromTes = self.readTrnsysFiles.get("QShFromTes", ifNotFoundEqualToZero=True)

        self.qAcumRadiator = self.readTrnsysFiles.get("QAcumRadiator", ifNotFoundEqualToZero=True)

        self.qBuiAcum = self.readTrnsysFiles.get("PAcumBui_kW", ifNotFoundEqualToZero=True)

        self.pElShPenalty = self.readTrnsysFiles.get("PpenSH_kW", ifNotFoundEqualToZero=True)

        self.pElCoolPenalty = self.readTrnsysFiles.get("PpenSC_kW", ifNotFoundEqualToZero=True)

        self.qBuiHeat = num.zeros(12)
        self.qBuiCool = num.zeros(12)

        for i in range(12):
            self.qBuiHeat[i] = max(self.qSH[i], 0.0)
            self.qBuiCool[i] = -min(self.qSH[i], 0.0)

        self.buildingDataLoaded = True
        self.existUserCircuitSH = True

    def readBuildingHourlyDataType56(self, _name):

        self.readTrnsysFiles.readHourlyBuildingFile(_name)
        self.buildingDataLoaded = True

        logger.info("READING HOURLY DATA FROM BUILDING TYPE 56")

        # ['TIME', 'REL_BAL_ENERGY', '1_B4_QBAL=-', '1_B4_DQAIRdT+', '1_B4_QHEAT-', '1_B4_QCOOL+', '1_B4_QINF+', '1_B4_QVENT+', '1B4_QCOUP+', '1_B4_QTRANS+', '1_B4_QGINT+', '1_B4_QWGAIN+', '1_B4_QSOL+', '1_B4_QSOLAIR+']

        self.qBuiHeatHour = self.readTrnsysFiles.get("1_B4_QHEAT-")
        self.qBuiCoolHour = self.readTrnsysFiles.get("1_B4_QCOOL+")

        self.qBuiSolarGainsHour = self.readTrnsysFiles.get("1_B4_QSOL+")
        self.qBuiIntGainsHour = self.readTrnsysFiles.get("1_B4_QGINT+")
        self.qBuiTransLossesHour = self.readTrnsysFiles.get("1_B4_QTRANS+")
        self.qBuiInfLossesHour = self.readTrnsysFiles.get("1_B4_QINF+")
        self.qBuiVentLossesHour = self.readTrnsysFiles.get("1_B4_QVENT+")

        # The heat of the buiding readed is zero, so I recalculated it.

        #        for i in range(len(self.qBuiSolarGainsHour)):
        #        for i in range(2):

        #            gain   = self.qBuiSolarGainsHour[i]+self.qBuiIntGainsHour[i]
        #            loss = self.qBuiTransLossesHour[i]+self.qBuiInfLossesHour[i]+self.qBuiVentLossesHour[i]
        #            self.qBuiHeatHour[i]=-(gain+loss) #kJ/h
        #            print "hour%d gain:%f loss:%f"%(i,gain,loss)

        self.qBuiHeat = utils.calculateMonthlyValues(self.qBuiHeatHour)
        self.qBuiCool = utils.calculateMonthlyValues(self.qBuiCoolHour)
        self.qBuiSolarGains = utils.calculateMonthlyValues(self.qBuiSolarGainsHour) * self.unit.getJTokWh() * 1000.0

        # Probably this is the sum of radiator and internal gains
        self.qBuiGains = utils.calculateMonthlyValues(self.qBuiIntGainsHour) * self.unit.getJTokWh() * 1000.0

        self.qBuiTransLosses = utils.calculateMonthlyValues(self.qBuiTransLossesHour) * self.unit.getJTokWh() * 1000.0
        self.qBuiInfLosses = utils.calculateMonthlyValues(self.qBuiInfLossesHour) * self.unit.getJTokWh() * 1000.0

        #        print self.qBuiInfLosses
        #        raise ValueError("")

        self.qBuiVentLosses = utils.calculateMonthlyValues(self.qBuiVentLossesHour) * self.unit.getJTokWh() * 1000.0

        yearlyHeatDemand = (
            sum(self.qBuiSolarGains)
            + sum(self.qBuiGains)
            + sum(self.qBuiTransLosses)
            + sum(self.qBuiInfLosses)
            + sum(self.qBuiVentLosses)
        )

        logger.info("YEARLY DEMAND IN BUILDING :%f kWh" % yearlyHeatDemand)

        for i in range(12):
            logger.info(
                "month:%d GAIN solar:%f int(rad+conv):%f LOSS Inf:%f Trns:%f Vent:%f"
                % (
                    i + 1,
                    self.qBuiSolarGains[i],
                    self.qBuiGains[i],
                    self.qBuiInfLosses[i],
                    self.qBuiTransLosses[i],
                    self.qBuiVentLosses[i],
                )
            )

    def loadDHW(self, _name):

        self.existUserCircuitDHW = True

        self.readTrnsysFiles.readMonthlyFiles(_name, firstMonth=self.firstMonth, myYear=self.yearReadedInMonthylFile)
        self.numberOfMonthsSimulated = self.readTrnsysFiles.numberOfMonthsSimulated

        self.qDHW = self.readTrnsysFiles.get("Pdhw_kW")
        self.qHxLossDHW = self.readTrnsysFiles.get("PhxDloss_kW")
        # self.qPipeLossDHW = self.readTrnsysFiles.get("PPiDHWLoss_kW") I centralize pipe losses in one file loadPipeLosses (not done at this level yet)
        self.pElDhwPenalty = self.readTrnsysFiles.get("PpenDHW_kW", ifNotFoundEqualToZero=True)

    def loadElectric(self, _name):

        self.readTrnsysFiles.readMonthlyFiles(_name, firstMonth=self.firstMonth, myYear=self.yearReadedInMonthylFile)
        self.numberOfMonthsSimulated = self.readTrnsysFiles.numberOfMonthsSimulated

        self.pumpSH = self.readTrnsysFiles.get("PelPuSh_kW")
        self.qWcpHPPlusAux = self.readTrnsysFiles.get("PelAuxTot_kW")
        self.qWcpHP = self.readTrnsysFiles.get("PelAuxComp_kW")

        # self.pumpHPsink = self.readTrnsysFiles.get("PelPuAuxTot_kW",ifNotFoundEqualToZero=True) # JS: update for value that is actually calculated
        self.pumpHPsink = self.readTrnsysFiles.get("PelPuAuxSH_kW", ifNotFoundEqualToZero=True)

        # self.pumpHPsource = self.readTrnsysFiles.get("PelPuBri_kW")  # JS: update for value that is actually calculated
        self.pumpHPsource = self.readTrnsysFiles.get("PelPuAuxBri_kW")

        if self.pumpHPsource.any() == None:
            self.pumpHPsource = self.readTrnsysFiles.get("PelPuGHX_kW", ifNotFoundEqualToZero=True)

        # if(sum(self.qAuxHeaterSh)==0.0):
        # self.qAuxHeaterSh = self.readTrnsysFiles.get("PelHeater_kW",ifNotFoundEqualToZero=True)

        self.pumpSolar = self.readTrnsysFiles.get("PelPuC_kW", ifNotFoundEqualToZero=True)
        self.pumpDHW = self.readTrnsysFiles.get("PelPuDHW_kW", ifNotFoundEqualToZero=True)
        self.pElControllerSolar = self.readTrnsysFiles.get("PelContr_kW", ifNotFoundEqualToZero=True)
        self.pElControllerHp = self.readTrnsysFiles.get("PelContr_kW", ifNotFoundEqualToZero=True)

        # This control is done because in some decks these values are readed from another source.

        try:
            if sum(self.pElDhwPenalty) > 0:
                pass
            else:
                self.pElDhwPenalty = self.readTrnsysFiles.get("PpenDHW_kW", ifNotFoundEqualToZero=True)
        except:
            self.pElDhwPenalty = self.readTrnsysFiles.get("PpenDHW_kW", ifNotFoundEqualToZero=True)

        try:
            if sum(self.pElShPenalty) > 0:
                pass
            else:
                self.pElShPenalty = self.readTrnsysFiles.get("PpenSH_kW", ifNotFoundEqualToZero=True)
        except:
            self.pElShPenalty = self.readTrnsysFiles.get("PpenSH_kW", ifNotFoundEqualToZero=True)

        self.pElPenalty = num.zeros(12)
        self.pElController = num.zeros(12)

        for i in range(self.numberOfMonthsSimulated):
            self.pElPenalty[i] = self.pElShPenalty[i] + self.pElDhwPenalty[i] + self.pElCoolPenalty[i]

            # In the results we get the sum of both values so:It may be the case that there is only one pump to Sh so the pumpHpsink=0
            self.pumpHPsink[i] = max(self.pumpHPsink[i] - self.pumpHPsource[i], 0.0)
            self.pElController[i] = self.pElControllerSolar[i] + self.pElControllerHp[i]

    def loadWorkingHoursFromMonthy(self, _name):

        self.readTrnsysFiles.readMonthlyFiles(_name, firstMonth=self.firstMonth, myYear=self.yearReadedInMonthylFile)

        # self.onOffPumpCol   = self.readTrnsysFiles.get("BoCnoOn",ifNotFoundEqualToZero=True)    JS: depracated BoCnoOn
        self.onOffPumpCol = self.readTrnsysFiles.get(
            "pumpColOn", ifNotFoundEqualToZero=True
        )  # JS: pumpColOn instead of BoCnoOn
        self.onOffPumpHpDhw = self.readTrnsysFiles.get("BoAuxWWon", ifNotFoundEqualToZero=True)
        self.onOffPumpHpSh = self.readTrnsysFiles.get("BoAuxSHOn", ifNotFoundEqualToZero=True)
        self.onOffPumpSh = self.readTrnsysFiles.get("BoPumpShOn", ifNotFoundEqualToZero=True)

        self.onOffPumpHp = num.zeros(12)

        for i in range(12):
            self.onOffPumpHp[i] = self.onOffPumpHpDhw[i] + self.onOffPumpHpSh[i]

    def loadWorkingHours(self, _name):

        self.readTrnsysFiles.readUserDefinedFiles(_name)

        self.onOffPumpColUserDefined = self.readTrnsysFiles.get("BoCnoOn")
        self.onOffPumpHpDhwUserDefined = self.readTrnsysFiles.get("BoAuxWWon")
        self.onOffPumpHpShUserDefined = self.readTrnsysFiles.get("BoAuxSHOn")

        #        BoPumpShOn

        for i in range(len(self.onOffPumpColUserDefined)):
            # Domestic hot water priority
            if self.onOffPumpHpDhwUserDefined[i] == 1:
                self.onOffPumpHpShUserDefined[i] = 0.0

        self.onOffPumpCol = utils.calculateMonthlyValuesFromUserDefinedTimeStep(self.onOffPumpColUserDefined, 120)
        self.onOffPumpHpDhw = utils.calculateMonthlyValuesFromUserDefinedTimeStep(self.onOffPumpHpDhwUserDefined, 120)
        self.onOffPumpHpSh = utils.calculateMonthlyValuesFromUserDefinedTimeStep(self.onOffPumpHpShUserDefined, 120)

        for i in range(12):
            self.onOffPumpCol[i] = self.onOffPumpCol[i] * (120.0 / 3600.0)
            self.onOffPumpHpDhw[i] = self.onOffPumpHpDhw[i] * (120.0 / 3600.0)
            self.onOffPumpHpSh[i] = self.onOffPumpHpSh[i] * (120.0 / 3600.0)
            self.onOffPumpHp[i] = self.onOffPumpHpDhw[i] + self.onOffPumpHpSh[i]

    def loadHP(self, _name):

        self.readTrnsysFiles.readMonthlyFiles(_name, firstMonth=self.firstMonth, myYear=self.yearReadedInMonthylFile)
        self.numberOfMonthsSimulated = self.readTrnsysFiles.numberOfMonthsSimulated

        self.existHeatGeneratorLoop = True
        # self.qPipeLossHPSink = self.readTrnsysFiles.get("PPiAuxLossTot_kW",ifNotFoundEqualToZero=True) #DCAR centralized in loadPipeLosses

        self.qAuxHeaterHp = num.zeros(12)

        self.qHpToSh = self.readTrnsysFiles.get("PAuxSH_kW", ifNotFoundEqualToZero=True)
        self.qAirEvapHp = self.readTrnsysFiles.get("PauxEvapAir_kW", ifNotFoundEqualToZero=True)
        self.qBrineEvapHp = self.readTrnsysFiles.get("PauxEvapBrine_kW", ifNotFoundEqualToZero=True)
        self.qEvapHP = self.readTrnsysFiles.get("PauxEvap_kW", ifNotFoundEqualToZero=True)
        self.lossDefrostingHp = self.readTrnsysFiles.get("PauxDefrost_kW", ifNotFoundEqualToZero=True)
        self.lossCyclingHp = self.readTrnsysFiles.get("PauxLossStart_kW", ifNotFoundEqualToZero=True)
        self.lossThermalHp = self.readTrnsysFiles.get("PAuxLossAmb_kW", ifNotFoundEqualToZero=True)

        self.pElVentilatorHP = self.readTrnsysFiles.get("PelAuxVent_kW", ifNotFoundEqualToZero=True)
        self.qCondHP = self.readTrnsysFiles.get("PauxCond_kW")
        self.qDesuperHeaterHP = self.readTrnsysFiles.get("PauxDesup_kW", ifNotFoundEqualToZero=True)

        self.qHpInShMode = self.readTrnsysFiles.get("PauxCondSh_kW")
        self.qHpInDhwMode = self.readTrnsysFiles.get("PauxCondDHW_kW")

        # This value does not include the PiAuxRt !!neither the term QHpToSh
        self.qHpToTesSh = None  # self.readTrnsysFiles.get("PAuxTES_kW")

        if self.qHpToTesSh == None:
            # This includes then the PiAuxRt pipe losses
            self.qHpToTesSh = self.qHpInShMode - self.qHpToSh

            logger.info(
                "QHpInSHMode:%f QHpToTesSH:%f QHpToSHLoop:%f"
                % (sum(self.qHpInShMode), sum(self.qHpToTesSh), sum(self.qHpToSh))
            )

        self.qHpToTesDhw = self.qHpInDhwMode
        self.qHpToTes = self.qHpToTesSh + self.qHpToTesDhw

        self.qLossHp = num.zeros(12)

        for i in range(self.numberOfMonthsSimulated):

            self.qLossHp[i] = self.lossDefrostingHp[i] + self.lossCyclingHp[i] + self.lossThermalHp[i]
            self.qCondHP[i] = self.qCondHP[i] + self.qDesuperHeaterHP[i]
            # imbSH = self.qHpInShMode[i]-self.qHpToSh[i]-self.qTesShFromHp[i]
            # imbDHW = self.qHpInDhwMode[i]-self.qTesDhwFromHp[i]
            # print "HP SH(mode):%f DHW(mode):%f TO-SH:%f TO-DHWTES:%f TO-SHTES:%f imbSH:%f imbDHW:%f"%(self.qHpInShMode[i],self.qHpInDhwMode[i],self.qHpToSh[i],self.qTesDhwFromHp[i],self.qTesShFromHp[i],imbSH,imbDHW)

    def calculateDemand(self):

        self.qUseFound = True
        self.qDemandFound = True

        self.pElPenalty = self.pElShPenalty + self.pElDhwPenalty
        self.qUse = self.qDHW + self.qSH + self.qSC
        self.qDemand = self.qUse + self.pElShPenalty + self.pElDhwPenalty
        self.qDemandDhw = self.qDHW + self.pElDhwPenalty
        self.qDemandSh = self.qSH + self.pElShPenalty
        self.qUseDhw = self.qDHW
        self.qUseSh = self.qSH

        # for i in range(self.firstMonthIndex,self.firstMonthIndex+self.numberOfMonthsSimulated):
        #     self.pElPenalty[i] = self.pElShPenalty[i]+self.pElDhwPenalty[i]
        #     self.qUse[i] = self.qDHW[i] + self.qSH[i]
        #     self.qDemand[i] = self.qUse[i]+self.pElShPenalty[i]+self.pElDhwPenalty[i]
        #     self.qDemandDhw[i] =  self.qDHW[i] + self.pElDhwPenalty[i]
        #     self.qDemandSh[i] =  self.qSH[i] + self.pElShPenalty[i]
        #     self.qUseDhw[i] = self.qDHW[i]
        #     self.qUseSh[i] = self.qSH[i]
