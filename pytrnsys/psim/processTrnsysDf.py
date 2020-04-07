#!/usr/bin/python

"""
Child class from ProcessMonthlyDataBase used for processing all TRNSYS simulations.

Author : Dani Carbonell
Date   : 2018
ToDo :
"""

import os , subprocess
import string, shutil
import pytrnsys.pdata.processFiles as spfUtils
#import pytrnsys.psim.processMonthlyDataBase as  monthlyData  # changed in order to clean the processing of files
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

# from collections import OrderedDict


class ProcessTrnsysDf():
    """

    """

    def __init__(self, _path, _name,language='en'):


        self.fileName = _name
        self.outputPath = _path + "\%s" % self.fileName
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

        self.yearlyFactor = 10.  # value to divide yerarly values when plotted along with monthly data
        self.units = unit.UnitConverter()


        self.readTrnsysFiles = readTrnsysFiles.ReadTrnsysFiles(self.tempFolderEnd)

        # self.tInEvapHpMonthlyMax = num.zeros(12,float)
        # self.tInEvapHpMonthlyMin = num.zeros(12,float)
        # self.tInEvapHpMonthlyAv  = num.zeros(12,float)

        self.nameClass = "ProcessTrnsys"
        self.unit = unit.UnitConverter()
        self.trnsysDllPath = False


    def setInputs(self,inputs):
        self.inputs=inputs

    def setLatexNamesFile(self,file):
        if file is not None:
            self.doc.getLatexNamesDict(file=file)
        else:
            self.doc.getLatexNamesDict()
            
    def setMatplotlibStyle(self,stylesheet):
        self.plot = plot.PlotMatplotlib(language=self.plot.language,stylesheet=stylesheet)
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

    def loadAndProcess(self):

        self.loadFiles()
        self.process()
        self.doLatexPdf()
        self.addResultsFile()

    def setLoaderParameters(self):

        self.monthlyUsed = True
        self.hourlyUsed = True
        self.timeStepUsed = True

        self.fileNameListToRead = None
        self.loadMode = "complete"

        if 'firstMonth' in self.inputs.keys():
            self.firstMonth = self.inputs['firstMonth']
        else:
            self.firstMonth = "January"
        if 'yearReadedInMonthlyFile' in self.inputs.keys():
            self.yearReadedInMonthlyFile = self.inputs['yearReadedInMonthlyFile']
        else:
            self.yearReadedInMonthlyFile = -1

    def loadFiles(self):

        self.setLoaderParameters()
        locale.setlocale(locale.LC_ALL,'enn')
        self.loader = SimulationLoader(self.outputPath + '//temp', fileNameList=self.fileNameListToRead,sortMonths=True,
                                       mode=self.loadMode, monthlyUsed=self.monthlyUsed, hourlyUsed=self.hourlyUsed,
                                       timeStepUsed=self.timeStepUsed,firstMonth=self.firstMonth, year = self.yearReadedInMonthlyFile)
        # self.monData = self.loader.monData
        self.monDataDf = self.loader.monDataDf
        self.houDataDf = self.loader.houDataDf
        self.steDataDf = self.loader.steDataDf

        self.deck = deckTrnsys.DeckTrnsys(self.outputPath,self.fileName)
        self.deck.loadDeck()
        self.deckData = self.deck.getAllDataFromDeck()

        self.yearlySums = {value+'_Tot': self.monDataDf[value].sum() for value in self.monDataDf.columns}


        self.calcConfigEquations()

        self.yearlySums = {value + '_Tot': self.monDataDf[value].sum() for value in self.monDataDf.columns}
        self.myShortMonths = utils.getShortMonthyNameArray(self.monDataDf["Month"].values)

        print ("loadFiles completed using SimulationLoader")

    def process(self):

        if "plotHourly" in self.inputs.keys():
            self.pltB.createBokehPlot(self.houDataDf, self.outputPath,self.fileName,self.inputs["plotHourly"])

        if "plotMonthly" in self.inputs.keys():
        #
            for plot in self.inputs["plotMonthly"]:
                print("%s"%plot)

            # namePdf = self.plot.plotMonthlyDf(fSolar, "$F_{solar}$", nameFile, self.yearlyFsol, self.myShortMonths,
            #                                   useYearlyFactorAsValue=True, myTitle=None, printData=True)

        else:
            pass

        if "plotQvsTconfigured" in self.inputs.keys():
            monthsSplit = []
            # plot QvsT with configured inputs...
            InputListQvsT = self.inputs["plotQvsTconfigured"]
            self.loadQvsTConfig(self.steDataDf, "plotQvsTconfigured", monthsSplit=monthsSplit, addDhwCirc=False,
                                normalized=True, cut=False)

        else:
            pass

    def executeLatexFile(self):

        self.doc.executeLatexFile(moveToTrnsysLogFile=True, runTwice=False)

    def doLatexPdf(self, documentClass="SPFShortReportIndex"):

        self.createLatex(documentClass=documentClass)

        self.executeLatexFile()

    def addLatexContent(self):

        self.calculateDemands()
        self.calculateElConsumption()
        self.calculateSPFSystem()
        self.addDemands()
        self.addHeatBalance()
        self.addElConsumption()
        self.addTemperatureFreq()
        # self.addPlotConfigEquation()
        # self.addPlotAndLatexPV()
        self.addSPFSystem()

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

            if (len(name) > 9 and name[0:9] == "elSysOut_"):

                if (name[-6:] == "Demand"):
                    self.elDemandVector.append(self.monDataDf[name])
                    self.legendEl.append(self.getNiceLatexNames(name))

            elif (len(name) > 8 and name[0:8] == "qSysOut_"):

                if (name[-6:] == "Demand"):
                    self.qDemandVector.append(self.monDataDf[name].values)
                    self.qDemandDf = self.qDemandDf + self.monDataDf[name]
                    self.legendQ.append(self.getNiceLatexNames(name))

        self.qDemand = num.zeros(12)

        for i in range(len(self.qDemandVector)):
            self.qDemand[:len(self.qDemandVector[i])] = self.qDemand[:len(self.qDemandVector[i])] + self.qDemandVector[i]

        # self.monDataDf["qDemand"]=self.qDemandDf
        # self.deckData["qDemand_Tot"]=sum(self.qDemandDf)
        #
        # pass

    def addDemands(self,unit="kWh"):

        if(unit=="kWh"):
            myUnit=1.
        elif(unit=="MWh"):
            myUnit = 1000.
        elif(unit=="GWh"):
            myUnit = 1e6
        else:
            raise ValueError("unit %s not considered"%unit)

        legend = ["Month"] + self.legendQ + ["Total"]

        caption = "Heat Demand"
        nameFile = "HeatDemand"
        addLines = False

        var = self.qDemandVector
        for i in range(len(var)):
            var[i]=var[i]/myUnit
            
        var.append(self.qDemand/myUnit)

        units = []
        units.append(unit)

        self.doc.addTableMonthlyDf(var, legend,units, caption, nameFile, self.myShortMonths, sizeBox=15,
                                   addLines=addLines)

    def calculateSPFSystem(self):

        self.SpfShpDis = num.zeros(13)

        for i in range(len(self.elHeatSysTotal)):
            if (self.elHeatSysTotal[i] == 0):
                self.SpfShpDis[i] = 0.
            else:
                self.SpfShpDis[i] = self.qDemand[i] / self.elHeatSysTotal[i]

        self.yearQDemand = sum(self.qDemand)
        self.yearElHeatSysTotal = sum(self.elHeatSysTotal)
        self.yearSpfShpDis = self.yearQDemand / self.yearElHeatSysTotal
        self.SpfShpDis[12] = self.yearSpfShpDis

    def addSPFSystem(self, printData=False):

        var = []

        qD = self.qDemand
        qD = num.append(qD, sum(self.qDemand))

        var.append(qD)

        el = self.elHeatSysTotal
        el = num.append(el, sum(self.elHeatSysTotal))

        var.append(el)

        var.append(self.SpfShpDis)

        nameFile = "SPF_SHP"
        legend = ["Month", "$Q_{demand}$", "$El_{Heat,Sys}$", "$SPF_{SHP}$"]
        caption = "Seasonal performance factor of the complete system"
        self.doc.addTableMonthlyDf(var, legend, ["", "kWh", "kWh", "-"], caption, nameFile, self.myShortMonths,
                                   sizeBox=15)

        yearlyFactor = 10.

        namePdf = self.plot.plotMonthlyDf(self.SpfShpDis, "$SPF_{SHP}$", nameFile, yearlyFactor, self.myShortMonths,
                                          myTitle=None, printData=printData)

        self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

        self.SPFShpWeighted = num.zeros(12)

        for i in range(len(self.qDemand)):
            self.SPFShpWeighted[i]=self.SpfShpDis[i]*self.qDemand[i]/sum(self.qDemand)

        nameFile = "SPF_SHP_weighted"

        namePdf = self.plot.plotMonthlyDf(self.SPFShpWeighted, "$\widetilde{SPF_{SHP}}$", nameFile, yearlyFactor, self.myShortMonths,
                                          myTitle=None, printData=printData)

        self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def calcConfigEquations(self):
        for equation in self.inputs['calc']:
            namespace = {**self.deckData,**self.__dict__,**self.yearlySums}
            expression = equation.replace(' ','')
            exec(expression,globals(),namespace)
            self.deckData = namespace
            print(expression)
        for equation in self.inputs["calcMonthly"]:
            kwargs = {"local_dict": {**self.deckData,**self.yearlySums}}
            self.monDataDf.eval(equation,inplace=True,**kwargs)
        for equation in self.inputs["calcHourly"]:
            kwargs = {"local_dict": {**self.deckData,**self.yearlySums}}
            self.houDataDf.eval(equation, inplace=True, **kwargs)


    def addPlotConfigEquation(self):
        for equation in self.inputs['calcMonthly']:

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

            namePdf = self.plot.plotMonthlyDf(values, parameters[0], parameters[0], averageValue, self.myShortMonths,
                                              useYearlyFactorAsValue=True, myTitle=None, printData=True)

            caption = parameters[0]

            self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

            nameFile = parameters[0]
            legend = ["Month", parameters[0]]

            # var = []
            # var.append(fSolar)

            # self.doc.addTableMonthlyDf(values, legend, ["", "-"], caption, nameFile, self.myShortMonths,
            #                            sizeBox=15)

    def loadQvsTConfig(self, df, year=False, useOnlyOneYear=False, monthsSplit=[], addDhwCirc=False, normalized=False,
                 cut=False):


        self.QvsTInput = self.inputs["plotQvsTconfigured"]


        factor = 1.
        tFlow = []
        eCum = []
        legend = []

        if "QvsTnormalized" in self.inputs.keys():
            self.QvsTNorm = self.inputs["QvsTnormalized"]
            norm = 0.
            for i in range(0, len(self.QvsTNorm)):
                norm = norm + max(num.cumsum(df[self.QvsTNorm[i]] * factor))
        else:
            norm = 1.


        for i in range (0,len(self.QvsTInput)):

            #legend.append(jsonDict["legend"])
            if i % 2 == 0:
                eCum.append(abs(df[self.QvsTInput[i]]) * factor / norm)
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

        self.doc.addPlot(namePdf, "Cumulative energy flow as funciton of reference temperature", fileName, 12)

        for mIndex in range(len(monthsSplit)):
            timeStepInSeconds = self.readTrnsysFiles.timeStepUsed
            month = monthsSplit[mIndex]
            # Energy values in W*second
            iBegin, iEnd = utils.getMonthlySliceFromUserDefinedTimeStep(tShFl, timeStepInSeconds, month,
                                                                        firstHourInYear=self.firstConsideredTime)

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



    def addHeatBalance(self, printData=False,unit="kWh"):

        if(unit=="kWh"):
            myUnit=1.
        elif(unit=="MWh"):
            myUnit = 1000.
        elif(unit=="GWh"):
            myUnit = 1e6
        else:
            raise ValueError("unit %s not considered"%unit)

        inVar = []
        outVar = []
        legendsIn = []
        legendsOut = []



        # for name in self.monData.keys():
        for name in self.monDataDf.columns:

            found = False

            try:
                if (name[0:7] == "qSysIn_" or name[0:10] == "elSysIn_Q_"):
                    # inVar.append(self.monData[name])
                    inVar.append(self.monDataDf[name].values/myUnit)
                    legendsIn.append(self.getNiceLatexNames(name))


                elif (name[0:8] == "qSysOut_"):
                    # outVar.append(self.monData[name])
                    outVar.append(self.monDataDf[name].values/myUnit)

                    legendsOut.append(self.getNiceLatexNames(name))
            except:
                pass

        nameFile = 'HeatMonthly'

        niceLegend = legendsIn + legendsOut

        # firstMonthId = self.monDataDf["Month"].index[0]

        # firstMonthId = utils.getMonthNameIndex(self.monDataDf["Month"].index)
        # startMonth = firstMonthId


        namePdf = self.plot.plotMonthlyBalanceDf(inVar, outVar, niceLegend, "Energy Flows", nameFile, unit,
                                                 self.myShortMonths, yearlyFactor=10,
                                                 useYear=False, printData=printData)

        for i in range(len(outVar)):
            outVar[i] = -outVar[i]

        var = inVar + outVar
        var.append(sum(inVar) + sum(outVar))

        names = ["Month"] + niceLegend + ["Imb"]

        caption = "System Heat Balance"

        totalDemand = sum(self.qDemand)/myUnit

        imb = sum(var[len(var) - 1])

        addLines = ""
        symbol = "\%"
        line = "\\hline \\\\ \n";
        addLines = addLines + line
        line = "$Q_D$ & %.2f & MWh \\\\ \n" % (totalDemand / 1000.);
        addLines = addLines + line
        line = "Imb & %.1f & %s \\\\ \n" % (100 * imb / totalDemand, symbol);
        addLines = addLines + line

        self.doc.addTableMonthlyDf(var, names, unit, caption, nameFile, self.myShortMonths, sizeBox=15,
                                   addLines=addLines)
        self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)
    
    

    def calculateElConsumption(self, printData=False):

        inVar = []
        outVar = []
        self.legendsElConsumption = []
        self.elHeatSysTotal = []  # vector of a sum of all electricity consumption used for the heating system
        self.elHeatSysMatrix = []  # matrix with all vectors included in the el consumption. For table printing and plot

        for name in self.monDataDf.columns:

            found = False

            try:
                #if (name[0:9] == "elSysOut_" or name[0:10] == "elSysIn_Q_"):
                if (name[0:10] == "elSysIn_Q_"):
                    el = self.monDataDf[name].values
                    self.elHeatSysMatrix.append(el)
                    # self.elHeatSysTotal = self.elHeatSysTotal + el
                    self.legendsElConsumption.append(self.getNiceLatexNames(name))
            except:
                pass

        self.elHeatSysTotal = sum(self.elHeatSysMatrix)

    def addElConsumption(self, printData=False):

        nameFile = 'elHeatSysMonthly'

        legend = self.legendsElConsumption
        inVar = self.elHeatSysMatrix
        outVar= []


        namePdf = self.plot.plotMonthlyBalanceDf(inVar, outVar, legend, "El heat system", nameFile, "kWh",
                                                 self.myShortMonths, yearlyFactor=10,
                                                 useYear=False, printImb=False, printData=printData)

        var = inVar
        self.elHeatSysTotal = sum(inVar)
        var.append(self.elHeatSysTotal)

        names = ["Month"] + legend + ["Total"]

        caption = "System El Heat Balance"

        self.doc.addTableMonthlyDf(var, names, "kWh", caption, nameFile, self.myShortMonths, sizeBox=15)
        self.doc.addPlotShort(namePdf, caption=caption, label=nameFile)

    def addTemperatureFreq(self, printData = False):

        if "plotT" in self.inputs.keys():
            if (len(self.inputs['plotT']) > 0):
                for name in self.inputs['plotT']:
                    nameFile = 'tempFreqDis' + name
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
            if(niceName==None):
                niceName = "$%s$" % "".join([c for c in name if c in ascii_letters+digits])

        return niceName

    def getCustomeNiceLatexNames(self,name):
        return None

    def loadDll(self):

        self.log = LogTrnsys.LogTrnsys(self.outputPath, self.fileName)
        self.log.loadLog()
        self.log.getMyDataFromLog()
        self.calcTime = self.log.getCalculationTime()

        self.iteErrorMonth = self.log.getIteProblemsForEachMonth

        self.nItProblems = self.log.numberOfFailedIt

    def getVersionsDll(self):

        if (0):
            raise ValueError("Deprecated. File created in simulaiton folder. To be improved")
            #
            #        namesDll= ["type860","type1924","type709","type878","type859","Type832","Type833"]

            namesDll = []
            myset = set(self.readTrnsysFiles.TrnsysTypes)  # get the unique names (all repeated ones are excluded)
            print (myset)

            for number in myset:
                nameType = "type%s" % number
                namesDll.append(nameType)

            self.dllVersions = self.getDllVersionFromType(namesDll)

            self.buildingModel = None
            for dll in self.dllVersions:
                print (dll)
                if (dll[0:6] == "type56"):
                    self.buildingModel = "Type56"
                elif (dll[0:8] == "type5998"):
                    self.buildingModel = "ISO"

    def getDllVersionFromType(self, typeNumber):

        if (self.trnsysDllPath == False):

            if (self.trnsysVersion == "standard"):
                trnsysExe = os.getenv("TRNSYS_EXE")

            else:
                trnsysExe = os.getenv(self.trnsysVersion)

            print (trnsysExe)

            mySplit = trnsysExe.split("Exe")
            self.trnsysDllPath = mySplit[0] + "\\UserLib\\ReleaseDLLs"
        else:
            pass

        print ("Dll path:%s" % self.trnsysDllPath)

        listDll = os.listdir(self.trnsysDllPath)

        dllVersion = []
        for name in typeNumber:
            nameFound = False
            for dll in listDll:
                if (dll[-3:] == "dll"):
                    #                    print "%s %s" % (dll,name)
                    if (dll.count(name) == 1 and nameFound == False):
                        nameFound = True
                        dllVersion.append(dll)
                        print ("FOUND %s %s" % (dll, name))
                        break

        print (dllVersion)
        #        raise ValueError()

        return dllVersion

    def getTagLabel(self, label):

        return ("#=======================================\n#%s :%s\n#=======================================\n" % (
        self.nameClass, label))

    def setPathReadTrnsysFile(self, _path):

        self.readTrnsysFiles.setPath(_path)

    def addResultsFile(self):
        """
        Save results to a results.json file.

        Function uses results stringArray from config file to provide keys that will be saved
        :return:
        """
        if 'results' in self.inputs:
            print("creating results.json file")

            self.resultsDict = {}
            jointDicts = {**self.deckData,**self.monDataDf.to_dict(orient='list'),**self.__dict__,**self.yearlySums}
            for key in self.inputs['results']:
                if type(jointDicts[key]) == num.ndarray:
                    value = list(jointDicts[key])
                else:
                    value = jointDicts[key]
                self.resultsDict[key] = value

            fileName = self.fileName+'-results.json'
            fileNamePath = os.path.join(self.outputPath, fileName)
            with open(fileNamePath, 'w') as fp:
                json.dump(self.resultsDict, fp, indent = 2, separators=(',', ': '),sort_keys=True)


    def plot_as_emf(self,figure, **kwargs):
        if 'inkscape' in self.inputs:
            try:
                inkscape_path = kwargs.get('inkscape', self.inputs['inkscape'])
                filepath = kwargs.get('filename', None)
        
                if filepath is not None:
                    path, filename = os.path.split(filepath)
                    filename, extension = os.path.splitext(filename)
        
                    svg_filepath = os.path.join(path, filename + '.svg')
                    emf_filepath = os.path.join(path, filename + '.emf')
        
                    figure.savefig(svg_filepath, format='svg')
        
                    subprocess.call([inkscape_path, svg_filepath, '--export-emf', emf_filepath])
                    os.remove(svg_filepath)
            except:
                raise ValueError('Inkscape path is not set correctly.')
                