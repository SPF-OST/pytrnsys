#!/usr/bin/python

import os
import glob
import json
import pytrnsys.psim.debugProcess as debugProcess
import multiprocessing as mp
import pytrnsys.rsim.runParallel as run
import pytrnsys.utils.utilsSpf as utils
import pytrnsys.trnsys_util.readConfigTrnsys as readConfig
import pytrnsys.psim.processTrnsysDf as processTrnsys
import warnings
import copy
import pytrnsys.report.latexReport as latex
import matplotlib.pyplot as plt
import numpy as num
import pandas as pd
#import seaborn as sns
import pytrnsys.utils.costConfig as costConfig
from pathlib import Path
import pytrnsys.plot.plotMatplotlib as plot
import sys
import re
import pkg_resources
import logging
try:
    import pytrnsys_examples
except ImportError:
    pass
#we would need to pass the Class as inputs
import pytrnsys.utils.log as log

def processDataGeneral(casesInputs,withIndividualFiles = False):
    """
    processes all the specified cases

    Parameters
    ----------
    casesInputs: list of str
        list of strings with all cases to run

    Returns
    -------

    """
    if withIndividualFiles:
        (baseClass,locationPath, fileName, inputs, individualFiles) = casesInputs
    else:
        (baseClass,locationPath, fileName, inputs) = casesInputs

    #    locationPath = inputs.pop(0)
    #    fileName,avoidUser,maxMinAvoided,yearReadedInMonthlyFile,cleanModeLatex,firstMonthUsed,processQvsT

    test = baseClass

    # casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"],self.inputs["maxMinAvoided"],self.inputs["yearReadedInMonthlyFile"],\
    #                     self.inputs["cleanModeLatex"],self.inputs["firstMonthUsed"],self.inputs["processQvsT"],self.inputs["firstMonthUsed"],self.inputs["buildingArea"],\
    #                     self.inputs["dllTrnsysPath"],self.inputs["setPrintDataForGle"],self.inputs["firstConsideredTime"]))


    test.setInputs(inputs)
    if inputs['typeOfProcess'] == 'individual':
        test.setIndividualFiles(individualFiles)
    if 'latexNames' in inputs.keys():
        test.setLatexNamesFile(inputs['latexNames'])
    else:
        test.setLatexNamesFile(None)

    if "matplotlibStyle" in inputs:
        test.setMatplotlibStyle(inputs["matplotlibStyle"])

    if "setFontsize" in inputs:
        test.setFontsize(inputs["setFontsize"])

    test.setBuildingArea(inputs["buildingArea"])
    test.setTrnsysDllPath(inputs["dllTrnsysPath"])

    # test.setTrnsysVersion("TRNSYS17_EXE")

    test.setPrintDataForGle(inputs["setPrintDataForGle"])

    # test.avoidUserDefinedCalculation = inputs["avoidUser"]
    # test.maxMinAvoided = inputs["maxMinAvoided"]
    test.yearReadedInMonthylFile = inputs["yearReadedInMonthlyFile"]

    test.cleanModeLatex = inputs["cleanModeLatex"]
    # test.firstConsideredTime = firstConsideredTime

    # myFirstMonthLong = utils.getMonthLongName(firstMonthUsed + 1)  # starts at 1
    # test.firstMonth = myFirstMonthLong
    # test.firstMonthIndex = 0  # firstMonthUsed

    doProcess = True

    if(inputs['isTrnsys']):
        test.loadAndProcessTrnsys()
    else:
        test.loadAndProcessGeneric()

    # rename files if multiple years are available:
    if inputs["yearReadedInMonthlyFile"] != -1 and inputs["typeOfProcess"] != 'json':
        renameFile = os.path.join(locationPath, fileName, fileName)

        fileEndingsDefault = ["-results.json", "-report.pdf","-plots.html"]

        for ending in fileEndingsDefault:
            newEnding = "-Year%i" % inputs["yearReadedInMonthlyFile"] + ending
            try:
                if os.path.isfile(renameFile + newEnding):
                    os.remove(renameFile + newEnding)
                os.rename(renameFile + ending, renameFile + newEnding)
                os.remove(renameFile + ending)
            except:
                print(
                    "File %s already exists, and thus was not saved again, needs to be improved (either not processed, or actually replaced)" % (
                                renameFile + newEnding))

    del test  # time.sleep(5)

    return " Finished: " + fileName




class ProcessParallelTrnsys():
    """
    Main class to process all TRNSYS results.
    We need to include in this class any processing Class
    customized for new projects
    Author : Daniel Carbonell
    Date   : 01-10-2018
    ToDo : remove processDataGshp and make it generic
    getBaseClass should be defined outside this function so that this class is not changet at all
    """

    def __init__(self):

        self.defaultInputs()
        self.filteredfolder = [".gle"]
        try:
            self.logger = logging.getself.logger('root')
        except:
            self.logger = log.setup_custom_logger('root', self.inputs['outputLevel'])

    def defaultInputs(self):

        self.inputs = {}
        self.inputs["plotStyle"] = "line"
        self.inputs["isTrnsys"] = True
        self.inputs["processParallel"] = True
        self.inputs["avoidUser"]    = False
        self.inputs["processQvsT"]  = True
        self.inputs["cleanModeLatex"] = False
        self.inputs["maxMinAvoided"] = False
        self.inputs["yearReadedInMonthlyFile"] = -1
        self.inputs["process"] = True
        self.inputs["firstMonth"] = "January"     # 0=January 1=February 7=August
        self.inputs["reduceCpu"] = 2
        self.inputs["typeOfProcess"] = "completeFolder" # "casesDefined"
        self.inputs["forceProcess"]  =  True #even if results file exist it proceess the results, otherwise it checks if it exists
        self.inputs["pathBase"] = os.getcwd()
        self.inputs["setPrintDataForGle"] = True
        self.inputs['firstConsideredTime'] = None #Be carefull here. Thsi will not be proprly filtered
        self.inputs["buildingArea"] = 1072.
        self.inputs["parseFileCreated"] = False
        self.inputs["dllTrnsysPath"] = False
        self.inputs["classProcessing"] = False
        self.inputs["latexExePath"] = "Unknown"
        self.inputs["figureFormat"] = 'pdf'
        self.inputs["plotEmf"] = False
        self.inputs["outputLevel"] = "INFO"
        self.inputs['createLatexPdf'] = True
        self.inputs['calculateCost'] = False

        self.inputs['calculateHeatDemand']=True
        self.inputs['calculateSPF']=True
        self.inputs['calculateElectricDemand']=True

        self.inputs["comparePlotUserName"] = "" #don't change this default value

        self.individualFile = False

    def setFilteredFolders(self,foldersNotUsed):
        self.filteredfolder = foldersNotUsed

    def readConfig(self,path,name,parseFileCreated=False):
        self.configPath = path
        tool = readConfig.ReadConfigTrnsys()
        tool.readFile(path,name,self.inputs,parseFileCreated=parseFileCreated)
        if 'latexNames' in self.inputs.keys():
            if ':' not in self.inputs['latexNames']:
                self.inputs['latexNames'] = os.path.join(self.configPath, self.inputs['latexNames'])
        if 'fileToLoad' in self.inputs.keys():
            self.individualFile = True


    def getBaseClass(self, classProcessing, pathFolder, fileName):

       return processTrnsys.ProcessTrnsysDf(pathFolder, fileName,individualFile=self.individualFile)

    def isStringNumber(self,sample):
        """
        Does a given string consist of a number only?

        Parameters
        ---------
        sample : str
            String to be checked

        Returns
        -------
        bool
            Indicates whether sample consists only of a number

        """
        try:
            float(sample)
            return True
        except ValueError:
            return False

    def loadPlotJson(self, filePath):

        with open(filePath, 'r') as file:
            plotParDict = json.load(file)

        returnDict = {}

        pyplotKwargs = ''
        for entry in plotParDict:
            try:
                if isinstance(plotParDict[entry],str):
                    plotParDict[entry] = '\'' + plotParDict[entry] + '\''
                plotStatement = 'plt.plot(1.,1.,' + entry + '=%s)' %plotParDict[entry]
                plt.figure()
                exec(plotStatement)
                plt.close()
                pyplotKwargs = pyplotKwargs + ',' + entry + '=' + str(plotParDict[entry])
            except:
                pass
        return pyplotKwargs


    def process(self):
        casesInputs = []
        fileName = []
        classList = []

        if os.path.exists(os.path.join(self.inputs['pathBase'],'Summary.dat')):
            os.remove(os.path.join(self.inputs['pathBase'],'Summary.dat'))

        if (self.inputs["typeOfProcess"] == "completeFolder") or (self.inputs["typeOfProcess"] == "json"):

            pathFolder = self.inputs["pathBase"]

            if (self.inputs["typeOfProcess"] == "completeFolder"):
                files = glob.glob(os.path.join(pathFolder, "**/*.lst"), recursive=True)
                fileName = [Path(name).parts[-2] for name in files]
                relPaths = [os.path.relpath(os.path.dirname(file), pathFolder) for file in files]

            elif (self.inputs["typeOfProcess"] == "json"):
                files = glob.glob(os.path.join(pathFolder, "**/*.json"), recursive=True)
                fileName = [Path(name).parts[-2] for name in files]
                relPaths = [os.path.relpath(os.path.dirname(file), pathFolder) for file in files]
                relPaths = list(dict.fromkeys(relPaths))  # remove duplicates due to folders containing more than one json files

            for relPath in relPaths:
                if relPath == '.':
                    continue
                name = Path(relPath).parts[-1]
                folderUsed = True
                for i in range(len(self.filteredfolder)):
                    if (name == self.filteredfolder[i]):
                        folderUsed=False
                if(folderUsed):
                    nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (relPath, name))

                    if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                        self.logger.info("%s already processed" % name)

                    elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (relPath, name))) and  self.inputs["forceProcess"] == False:
                        self.logger.info("%s already processed" % name)

                    else:
                        if len(Path(relPath).parts)>1:
                            newPath = os.path.join(pathFolder,os.path.join(*list(Path(relPath).parts[:-1])))
                        else:
                            newPath = pathFolder
                        baseClass = self.getBaseClass(self.inputs["classProcessing"],newPath,name)

                        self.logger.info("%s will be processed" % name)
                        # casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"],self.inputs["maxMinAvoided"],self.inputs["yearReadedInMonthlyFile"],\
                        #                     self.inputs["cleanModeLatex"],self.inputs["firstMonthUsed"],self.inputs["processQvsT"],self.inputs["firstMonthUsed"],self.inputs["buildingArea"],\
                        #                     self.inputs["dllTrnsysPath"],self.inputs["setPrintDataForGle"],self.inputs["firstConsideredTime"]))

                        casesInputs.append((baseClass,pathFolder, name, self.inputs))

        elif self.inputs["typeOfProcess"] == "individual":
            self.individualFiles = []
            for file in self.inputs['fileToLoad']:
                fileDict = {}
                fileDict['timeStep'] = file[0]
                fileDict['path'] = self.inputs[file[1]]
                fileDict['name'] = file[2]
                self.individualFiles += [fileDict]

            for fileDict in self.individualFiles:
                baseClass = self.getBaseClass(self.inputs["classProcessing"], fileDict['path'], fileDict['name'])
                self.logger.info("%s will be processed" % fileDict['name'])
                casesInputs.append((baseClass, fileDict['path'], fileDict['name'], self.inputs, self.individualFiles))

        elif self.inputs["typeOfProcess"] == "casesDefined":

            #for city in self.inputs["cities"]:
            #    for fileType in self.inputs["fileTypes"]:

            #        name = self.inputs["fileName"]+"-%s_%s"%(city,fileType)
            #        pathFolder = os.path.join(self.inputs["pathBase"],city)
            name = self.inputs["fileName"]
            pathFolder = self.inputs["pathBase"]
            baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name) #DC This was missing
            casesInputs.append((baseClass, pathFolder, name, self.inputs)) #DC This was missing

            # fileName.append(name)

            # folderUsed = True #DC Why this is here ? casesDefined are the ones defined in the config.
            # for i in range(len(self.filteredfolder)):
            #     if (name == self.filteredfolder[i]):
            #         folderUsed = False
            # if (folderUsed):
            #     nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (name, name))
            #
            #     if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
            #         print ("file :%s already processed" % name)
            #     else:
            #         print ("%s will be processed" % name)
            #
            #
            #         baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder,self.inputs["fileName"])
            #
            #         casesInputs.append((baseClass,pathFolder, name, self.inputs))

        elif self.inputs["typeOfProcess"] == "citiesFolder":

            for city in self.inputs["cities"]:
                pathFolder = os.path.join(self.inputs["pathBase"],city)
                fileName = [name for name in os.listdir(pathFolder) if os.path.isdir(pathFolder + "\\" + name)]

                for name in fileName:

                    folderUsed = True
                    for i in range(len(self.filteredfolder)):
                        if (name == self.filteredfolder[i]):
                            folderUsed = False
                    if (folderUsed):
                        nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (name, name))

                        if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                            self.logger.info("%s already processed" % name)

                        elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (name, name))) and self.inputs["forceProcess"] == False:
                            self.logger.info("%s already processed" % name)

                        else:
                            baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name)

                            self.logger.info("%s will be processed" % name)


                            if ("hourly" in name or "hourlyOld" in name) and not "Mean" in name:
                                inputs = []
                                if self.inputs["yearReadedInMonthlyFile"] == -1:
                                    for i in range(self.inputs["numberOfYearsInHourlyFile"]):
                                        inputs.append(copy.deepcopy(self.inputs))
                                        inputs[i]['yearReadedInMonthlyFile'] = i
                                        casesInputs.append((baseClass, pathFolder, name, inputs[i]))
                                else:
                                    for i in range(self.inputs["numberOfYearsInHourlyFile"]):
                                        inputs.append(copy.deepcopy(self.inputs))
                                        inputs[i]['yearReadedInMonthlyFile'] = self.inputs["yearReadedInMonthlyFile"] + i
                                        casesInputs.append((baseClass, pathFolder, name, inputs[i]))
                            else:
                                casesInputs.append((baseClass, pathFolder, name, self.inputs))

        elif self.inputs["typeOfProcess"] == "config":
            """
            Processes the files that are specified in the process.config file
            
            This option is to be used with the following arguments in the process.config file:
            
            stringArray cities 
            stringArray fileTypes 
            
            examples for cities:
            
            "GVE" "BER" "BAS" "SMA" "DAV" "OTL"
            
            examples for fileTypes:
            
            "sia" "hourly" "monthlyMean"
            """

            for city in self.inputs["cities"][0]:
                pathFolder = os.path.join(self.inputs["pathBase"], city)
                fileName = [name for name in os.listdir(pathFolder) if os.path.isdir(pathFolder + "\\" + name)]

                for name in fileName:

                    for type in self.inputs['fileTypes'][0]:
                        if type in name:

                            folderUsed = True
                            for i in range(len(self.filteredfolder)):
                                if (name == self.filteredfolder[i]):
                                    folderUsed = False
                            if (folderUsed):
                                nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (name, name))

                                if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                                    self.logger.info("file :%s already processed" % name)

                                elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (name, name))) and \
                                        self.inputs["forceProcess"] == False:
                                    self.logger.info("file :%s already processed" % name)

                                else:
                                    baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name)

                                    self.logger.info("%s will be processed" % name)

                                    if ("hourly" in name or "hourlyOld" in name) and not "Mean" in name:
                                        if self.inputs["forceHourlyYear"]:
                                            casesInputs.append((baseClass, pathFolder, name, self.inputs))
                                        else:
                                            inputs = []
                                            if self.inputs["yearReadedInMonthlyFile"] == -1:
                                                for i in range(self.inputs["numberOfYearsInHourlyFile"]):
                                                    inputs.append(copy.deepcopy(self.inputs))
                                                    inputs[i]['yearReadedInMonthlyFile'] = i
                                                    casesInputs.append((baseClass, pathFolder, name, inputs[i]))
                                            else:
                                                for i in range(self.inputs["numberOfYearsInHourlyFile"]):
                                                    inputs.append(copy.deepcopy(self.inputs))
                                                    inputs[i]['yearReadedInMonthlyFile'] = self.inputs[
                                                                                               "yearReadedInMonthlyFile"] + i
                                                    casesInputs.append((baseClass, pathFolder, name, inputs[i]))
                                    elif "hourlyMean" in name and type=='hourlyMean':
                                        casesInputs.append((baseClass, pathFolder, name, self.inputs))
                                    elif "hourlyMean" in name and type !='hourlyMean':
                                        pass
                                    else:
                                        casesInputs.append((baseClass, pathFolder, name, self.inputs))
                        else:
                            pass

            #sort to process 10 year files first and all 10 years:

        else:
            raise ValueError("Not Implemented yet")

        if(self.inputs["processParallel"]==True):

            debug = debugProcess.DebugProcess(pathFolder, "FileProcessed.dat", fileName)
            debug.start()

            # maximum number of processes at once:
            maxNumberOfCPU = min(run.getNumberOfCPU() - self.inputs["reduceCpu"], len(fileName))

            pool = mp.Pool(processes=maxNumberOfCPU)

            results = pool.map(processDataGeneral,casesInputs)

            # if(self.inputs["classProcessing"]=="BigIce"):
            #     results = pool.map(processDataGeneral,casesInputs)
            #if(self.inputs["classProcessing"]=="GSHP"):
            #    results = pool.map(processDataGshp,casesInputs)
            #else:
            #    results = pool.map(processDataGeneral, casesInputs)

            pool.close()

            debug.addLines(results)
            debug.finish()
        else:
            for i in range(len(casesInputs)):
                if self.inputs['typeOfProcess'] == 'individual':
                    processDataGeneral(casesInputs[i],True)
                else:
                    processDataGeneral(casesInputs[i])
                # try:
                #     processDataGeneral(casesInputs[i])
                # except:
                #     print('WARNING: the following case failed: ' + casesInputs[i][2])
        if  self.inputs['calculateCost']==True and 'cost' in self.inputs.keys(): #
            if(self.inputs['typeOfProcess']== "casesDefined"):
                fileNameList=[]
                fileNameList.append(self.inputs["fileName"])
            else:
                fileNameList =None

            self.calcCost(fileNameList=fileNameList)

        if 'acrossSetsCalc' in self.inputs.keys():
            self.logger.info('Calculating across sets')
            self.calculationsAcrossSets()

        if 'comparePlot' in self.inputs.keys():
            self.plotComparison()

        if 'comparePlotConditional' in self.inputs.keys():
            self.logger.info('Generating conditional comparison plot')
            self.plotComparisonConditional()

        if 'acrossSetsCalculationsPlot' in self.inputs.keys():
            self.logger.info('Generating plot of calculations across sets')
            self.plotCalculationsAcrossSets()

        if 'scatterPlot' in self.inputs.keys():
            self.scatterPlot()

        if 'pathInfoToJson' in self.inputs.keys():
            self.transferPathInfoToJson()

        if 'jsonCalc' in self.inputs.keys():
            self.calculateInJson()

        if 'jsonInsert' in self.inputs.keys():
            self.insertIntoJson()

        if 'calcClimateCorrections' in self.inputs.keys():
            self.calculateClimateCorrections()
            
        if 'compareMonthlyBarsPlot' in self.inputs.keys():
            self.plotMonthlyBarComparison()

        if 'printBoxPlotGLEData' in self.inputs.keys():
            self.printBoxPlotGLEData()

    def calculationsAcrossSets(self):
        pathFolder = self.inputs["pathBase"]
        for plotVariables in self.inputs['acrossSetsCalc']:
            if len(plotVariables) < 4:
                raise ValueError(
                    'You did not specify variable names and labels for the x and the y Axis in a compare Plot line')
            xAxisVariable = plotVariables[0]
            yAxisVariable = plotVariables[1]
            calculationVariable = plotVariables[2]


            conditionDict = {}
            equationDict = {}
            calcVariableDict = {}
            for plotVariable in plotVariables:
                if ':' in plotVariable:
                    conditionEntry, conditionValue = plotVariable.split(':')
                    conditionDict[conditionEntry] = conditionValue
                elif "=" in plotVariable:
                    equationVariable,equationExpression = plotVariable.split('=')
                    equationDict[equationVariable] = equationExpression
                    for variable in re.split('\W',equationExpression):
                        if variable != '' and not(self.isStringNumber(variable)):
                            calcVariableDict[variable] = ''

            plotXDict = {}
            plotYDict = {}

            if self.inputs["typeOfProcess"] == "json":
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)
            else:
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"))

            xVariable = []

            for file in resultFiles:
                with open(file) as f_in:
                    resultsDict = json.load(f_in)
                    resultsDict[''] = None

                conditionList = []
                for conditionEntry in conditionDict:
                    entryClass = type(resultsDict[conditionEntry])
                    conditionDict[conditionEntry] = entryClass(conditionDict[conditionEntry])
                    conditionList.append(conditionDict[conditionEntry]==resultsDict[conditionEntry])

                if all(conditionList):

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

                    xVariable.append(xAxis)

                    chunkVariable = ''

                    if resultsDict[chunkVariable] not in plotXDict.keys():
                        plotXDict[resultsDict[chunkVariable]] = {}
                        plotYDict[resultsDict[chunkVariable]] = {}
                        plotXDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [xAxis]
                        plotYDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [yAxis]
                    elif resultsDict[calculationVariable] not in plotXDict[resultsDict[chunkVariable]].keys():
                        plotXDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [xAxis]
                        plotYDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [yAxis]
                    else:
                        plotXDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]].append(xAxis)
                        plotYDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]].append(yAxis)

                else:
                    pass

            for variable in calcVariableDict:
                calcVariableDict[variable] = num.array(plotYDict[None][variable])

            calcVariableDict['equationDict'] = equationDict
            for equation in equationDict:
                calcVariableDict['equation'] = equation
                exec('equationDict[equation]='+equationDict[equation],calcVariableDict)

            xVariable = list(dict.fromkeys(xVariable))

            dataFrameDict = {}
            dataFrameDict[xAxisVariable] = xVariable
            dataFrameDict.update(equationDict)

            saveDf = pd.DataFrame(data=dataFrameDict)

            conditionsFileName = ''
            for conditionEntry in conditionDict:
                conditionsFileName += '_' + conditionEntry + '=' + str(conditionDict[conditionEntry])


            fileName = xAxisVariable + '_' + yAxisVariable + '_' + calculationVariable
            for equation in equationDict:
                fileName += '_' + equation
            fileName += conditionsFileName

            fullCsvPath = os.path.join(pathFolder, fileName + '.csv')
            saveDf.to_csv(fullCsvPath, index=False, sep=';')

    def plotComparison(self):
        pathFolder = self.inputs["pathBase"]
        for plotVariables in self.inputs['comparePlot']:
            if len(plotVariables) < 2:
                raise ValueError(
                    'You did not specify variable names and labels for the x and the y Axis in a compare Plot line')
            xAxisVariable = plotVariables[0]
            yAxisVariable = plotVariables[1]
            chunkVariable = ''
            seriesVariable = ''
            if len(plotVariables) >= 3:
                seriesVariable = plotVariables[2]
                chunkVariable = ''
            if len(plotVariables) == 4:
                chunkVariable = plotVariables[3]

            self.logger.info('Generating "comparePlot %s %s %s"' % (xAxisVariable, yAxisVariable, seriesVariable))

            plotXDict = {}
            plotYDict = {}
    
            seriesColors = {}
            colorsCounter = 0
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

            if self.inputs["typeOfProcess"] == "json":
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)
            else:
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"))

            if not(resultFiles):
                self.logger.error('No results.json-files found.')
                self.logger.error(
                    'Unable to generate "comparePlot %s %s %s"' % (xAxisVariable, yAxisVariable, seriesVariable))
                return

            for file in resultFiles:
                with open(file) as f_in:
                    resultsDict = json.load(f_in)
                    resultsDict['']=None

                if resultsDict[seriesVariable] not in seriesColors.keys():
                    seriesColors[resultsDict[seriesVariable]]=colors[colorsCounter]
                    colorsCounter+=1

                if '[' not in xAxisVariable:
                    xAxis = resultsDict[xAxisVariable]
                else:
                    name,index = str(xAxisVariable).split('[')
                    index = int(index.replace(']',''))
                    xAxis = resultsDict[name][index]
                if '[' not in yAxisVariable:
                    yAxis = resultsDict[yAxisVariable]
                else:
                    name,index = str(yAxisVariable).split('[')
                    index = int(index.replace(']',''))
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

            self.doc = latex.LatexReport('', '')
            if 'latexNames' in self.inputs.keys():
                if ':' in self.inputs['latexNames']:
                    latexNameFullPath = self.inputs['latexNames']
                else:
                    latexNameFullPath = os.path.join(self.configPath,self.inputs['latexNames'])
                self.doc.getLatexNamesDict(file=latexNameFullPath)
            else:
                self.doc.getLatexNamesDict()
            if 'matplotlibStyle' in self.inputs.keys():
                stylesheet = self.inputs['matplotlibStyle']
            else:
                stylesheet = 'word.mplstyle'
            if stylesheet in plt.style.available:
                self.stylesheet = stylesheet
            else:
                root = os.path.dirname(os.path.abspath(__file__))
                self.stylesheet = os.path.join(root, r"..\\plot\\stylesheets", stylesheet)
            plt.style.use(self.stylesheet)

            fig1,ax1 = plt.subplots(constrained_layout=True)
            if self.inputs["plotStyle"] == "line":
                styles = ['x-','x--','x-.','x:','o-','o--','o-.','o:']
            elif self.inputs["plotStyle"] == "dot":
                styles = ['x', 'o', '+', 'd', 's', 'v', '^', 'h']
            else:
                self.logger.error("Invalid 'plotStyle' argument")

            dummy_lines = []
            chunkLabels = []
            labelSet = set()
            lines = ""
            for chunk,style in zip(plotXDict.keys(),styles):
                dummy_lines.append(ax1.plot([],[],style,c='black'))
                if chunk is not None:
                    if not isinstance(chunk,str):
                        chunkLabel = round(float(chunk), 2)
                        chunkLabels.append("{:.2f}".format(chunkLabel))
                    else:
                        chunkLabels.append(chunk)

                for key in plotXDict[chunk].keys():
                    index = num.argsort(plotXDict[chunk][key])
                    myX = num.array(plotXDict[chunk][key])[index]
                    myY = num.array(plotYDict[chunk][key])[index]

                    mySize = len(myX)

                    if key is not None and not isinstance(key,str):
                        labelValue=round(float(key),2)
                    elif key is not None:
                        labelValue = key
                    if key is not None and labelValue not in labelSet:
                        if not isinstance(labelValue,str):
                            label = "{:.2f}".format(labelValue)
                        else:
                            label = labelValue
                        label = self.doc.getNiceLatexNames(label)
                        labelSet.add(labelValue)
                        ax1.plot(myX, myY,
                                 style, color=seriesColors[key], label=label)
                    else:
                        ax1.plot(myX, myY,
                                 style, color=seriesColors[key])

                    # for i in range(len(myX)):
                    #     line="%8.4f\t%8.4f\n"%(myX[i],myY[i]);lines=lines+line
            lines="!%s\t"%seriesVariable
            for chunk, style in zip(plotXDict.keys(), styles):
                for key in plotXDict[chunk].keys():  # the varables that appear in the legend
                    line="%s\t"%key;lines=lines+line
                line = "\n";lines = lines + line

            if(0):
                for X,Y in zip(myX,myY):
                    for chunk, style in zip(plotXDict.keys(), styles):

                        for key in plotXDict[chunk].keys(): #the varables that appear in the legend
                            index = num.argsort(plotXDict[chunk][key])
                            myX = num.array(plotXDict[chunk][key])[index]
                            myY = num.array(plotYDict[chunk][key])[index]
                            line = "%8.4f\t%8.4f\t" % (X, Y); lines = lines + line

                    line = "\n"; lines = lines + line
            else:
                for i in range(mySize):
                    for chunk, style in zip(plotXDict.keys(), styles):

                        for key in plotXDict[chunk].keys():  # the varables that appear in the legend
                            index = num.argsort(plotXDict[chunk][key])
                            myX = num.array(plotXDict[chunk][key])[index]
                            myY = num.array(plotYDict[chunk][key])[index]

                            try:
                                line = "%8.4f\t%8.4f\t" % (myX[i],myY[i]);
                                lines = lines + line
                            except:
                                pass

                    line = "\n"; lines = lines + line

            # box = ax1.get_position()
            #ax1.set_position([box.x0, box.y0, box.width, box.height])

            if chunkVariable != '':
                legend2=fig1.legend([dummy_line[0] for dummy_line in dummy_lines],chunkLabels,title=self.doc.getNiceLatexNames(chunkVariable), bbox_to_anchor=(1.5, 1.0), bbox_transform=ax1.transAxes)

            else:
                legend2 = None
            if seriesVariable != '':
                legend1 = fig1.legend(title=self.doc.getNiceLatexNames(seriesVariable), bbox_to_anchor=(1.2, 1.0), bbox_transform=ax1.transAxes)

            else:
                legend1 = None
            ax1.set_xlabel(self.doc.getNiceLatexNames(xAxisVariable))
            ax1.set_ylabel(self.doc.getNiceLatexNames(yAxisVariable))
            #if chunkVariable is not '':
            #
            if legend2 is not None:
                fig1.add_artist(legend2)
            #fig1.canvas.draw()
            #if legend2 is not None:
            #    ax1.add_artist(legend2)
            #    legend2.set_in_layout(True)
            #if legend1 is not None:
            #    legend1.set_in_layout(True)

            fileName = xAxisVariable + '_' + yAxisVariable + '_' + seriesVariable

            if chunkVariable != '':
                 fileName = fileName + '_' + chunkVariable

            if (self.inputs["comparePlotUserName"] != ""):
                fileName = fileName + '_' + self.inputs["comparePlotUserName"]


            fig1.savefig(os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
            plt.close()

            if(self.inputs["setPrintDataForGle"]):
                outfile = open(os.path.join(pathFolder, fileName + '.dat'), 'w')
                outfile.writelines(lines)
                outfile.close()
                # self.plot.gle.getEasyPlot(self, nameGleFile, fileNameData, legends, useSameStyle=True):

    def plotComparisonConditional(self):
        pathFolder = self.inputs["pathBase"]
        for plotVariables in self.inputs['comparePlotConditional']:
            if len(plotVariables) < 2:
                raise ValueError(
                    'You did not specify variable names and labels for the x and the y Axis in a compare Plot line')
            xAxisVariable = plotVariables[0]
            yAxisVariable = plotVariables[1]
            chunkVariable = ''
            seriesVariable = ''
            if len(plotVariables) >= 3 and not(':' in plotVariables[2]):
                seriesVariable = plotVariables[2]
                chunkVariable = ''
            if len(plotVariables) >= 4 and not(':' in plotVariables[3]):
                chunkVariable = plotVariables[3]

            conditionDict = {}
            for plotVariable in plotVariables:
                if ':' in plotVariable:
                    conditionEntry, conditionValue = plotVariable.split(':')
                    conditionDict[conditionEntry] = conditionValue

            plotXDict = {}
            plotYDict = {}

            seriesColors = {}
            colorsCounter = 0
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

            if self.inputs["typeOfProcess"] == "json":
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)
            else:
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"))

            conditionNeverMet = True

            for file in resultFiles:
                with open(file) as f_in:
                    resultsDict = json.load(f_in)
                    resultsDict[''] = None

                conditionList = []
                for conditionEntry in conditionDict:
                    entryClass = type(resultsDict[conditionEntry])
                    conditionDict[conditionEntry] = entryClass(conditionDict[conditionEntry])
                    conditionList.append(conditionDict[conditionEntry]==resultsDict[conditionEntry])

                if all(conditionList):

                    conditionNeverMet = False

                    if resultsDict[seriesVariable] not in seriesColors.keys():
                        seriesColors[resultsDict[seriesVariable]] = colors[colorsCounter]
                        colorsCounter += 1

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

                else:
                    pass

            if conditionNeverMet:
                self.logger.warning('The following conditions from "comparePlotConditional" were never met all at once:')
                for entry in conditionDict:
                    self.logger.warning('%s = %s' %(entry, str(conditionDict[entry])))
                self.logger.warning('The respective plot cannot be generated')
                return 

            self.doc = latex.LatexReport('', '')
            if 'latexNames' in self.inputs.keys():
                if ':' in self.inputs['latexNames']:
                    latexNameFullPath = self.inputs['latexNames']
                else:
                    latexNameFullPath = os.path.join(self.configPath, self.inputs['latexNames'])
                self.doc.getLatexNamesDict(file=latexNameFullPath)
            else:
                self.doc.getLatexNamesDict()
            if 'matplotlibStyle' in self.inputs.keys():
                stylesheet = self.inputs['matplotlibStyle']
            else:
                stylesheet = 'word.mplstyle'
            if stylesheet in plt.style.available:
                self.stylesheet = stylesheet
            else:
                root = os.path.dirname(os.path.abspath(__file__))
                self.stylesheet = os.path.join(root, r"..\\plot\\stylesheets", stylesheet)
            plt.style.use(self.stylesheet)

            fig1, ax1 = plt.subplots(constrained_layout=True)
            if self.inputs["plotStyle"] == "line":
                styles = ['x-', 'x--', 'x-.', 'x:', 'o-', 'o--', 'o-.', 'o:']
            elif self.inputs["plotStyle"] == "dot":
                styles = ['x', 'o', '+', 'd', 's', 'v', '^', 'h']
            else:
                print("Invalid 'plotStyle' argument")

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
                            label = "{:.2f}".format(labelValue)
                        else:
                            label = labelValue
                        label = self.doc.getNiceLatexNames(label)
                        labelSet.add(labelValue)
                        ax1.plot(myX, myY,
                                 style, color=seriesColors[key], label=label)
                    else:
                        ax1.plot(myX, myY,
                                 style, color=seriesColors[key])

                    # for i in range(len(myX)):
                    #     line="%8.4f\t%8.4f\n"%(myX[i],myY[i]);lines=lines+line
            lines = "!%s\t" % seriesVariable
            for chunk, style in zip(plotXDict.keys(), styles):
                for key in plotXDict[chunk].keys():  # the varables that appear in the legend
                    line = "%s\t" % key;
                    lines = lines + line
                line = "\n";
                lines = lines + line

            if (0):
                for X, Y in zip(myX, myY):
                    for chunk, style in zip(plotXDict.keys(), styles):

                        for key in plotXDict[chunk].keys():  # the varables that appear in the legend
                            index = num.argsort(plotXDict[chunk][key])
                            myX = num.array(plotXDict[chunk][key])[index]
                            myY = num.array(plotYDict[chunk][key])[index]
                            line = "%8.4f\t%8.4f\t" % (X, Y);
                            lines = lines + line

                    line = "\n";
                    lines = lines + line
            else:
                for i in range(mySize):
                    for chunk, style in zip(plotXDict.keys(), styles):

                        for key in plotXDict[chunk].keys():  # the varables that appear in the legend
                            index = num.argsort(plotXDict[chunk][key])
                            myX = num.array(plotXDict[chunk][key])[index]
                            myY = num.array(plotYDict[chunk][key])[index]

                            if type(myX[i]) == num.str_ and type(myY[i]) == num.str_:
                                line = myX[i] + "\t" + myY[i] + "\t"
                            elif type(myX[i]) == num.str_:
                                line = myX[i] + "\t" + "%8.4f\t" % myY[i]
                            elif type(myY[i]) == num.str_:
                                line = "%8.4f\t" % myX[i] + myX[i] + "\t"
                            else:
                                line = "%8.4f\t%8.4f\t" % (myX[i], myY[i]);
                            lines = lines + line

                    line = "\n";
                    lines = lines + line

            # box = ax1.get_position()
            # ax1.set_position([box.x0, box.y0, box.width, box.height])

            if chunkVariable !='':
                legend2 = fig1.legend([dummy_line[0] for dummy_line in dummy_lines], chunkLabels,
                                      title=self.doc.getNiceLatexNames(chunkVariable), bbox_to_anchor=(1.5, 1.0),
                                      bbox_transform=ax1.transAxes)

            else:
                legend2 = None
            if seriesVariable !='':
                legend1 = fig1.legend(title=self.doc.getNiceLatexNames(seriesVariable), bbox_to_anchor=(1.2, 1.0),
                                      bbox_transform=ax1.transAxes)

            else:
                legend1 = None
            ax1.set_xlabel(self.doc.getNiceLatexNames(xAxisVariable))
            ax1.set_ylabel(self.doc.getNiceLatexNames(yAxisVariable))

            conditionsFileName = ''
            if len(conditionDict) == 1:
                conditionName = self.doc.getNiceLatexNames(sorted(conditionDict)[0])
                ax1.set_title(conditionName + ' = ' + str(conditionDict[sorted(conditionDict)[0]]))
                conditionsFileName = sorted(conditionDict)[0] + '=' + str(conditionDict[sorted(conditionDict)[0]])
            else:
                conditionsTitle = ''
                for conditionEntry in conditionDict:
                    conditionName = self.doc.getNiceLatexNames(conditionEntry)
                    conditionsTitle += conditionName + ' = ' + str(conditionDict[conditionEntry]) + ', '
                    conditionsFileName += conditionEntry + '=' + str(conditionDict[conditionEntry]) + '_'
                conditionsTitle = conditionsTitle[:-2]
                ax1.set_title(conditionsTitle)
                conditionsFileName = conditionsFileName[:-1]
            # if chunkVariable is not '':
            #
            if legend2 is not None:
                fig1.add_artist(legend2)
            # fig1.canvas.draw()
            # if legend2 is not None:
            #    ax1.add_artist(legend2)
            #    legend2.set_in_layout(True)
            # if legend1 is not None:
            #    legend1.set_in_layout(True)
            if chunkVariable == '':
                fileName = xAxisVariable + '_' + yAxisVariable + '_' + seriesVariable + '_' + conditionsFileName
            else:
                fileName = xAxisVariable + '_' + yAxisVariable + '_' + seriesVariable + '_' + chunkVariable + '_' + conditionsFileName
            fig1.savefig(os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
            plt.close()

            if (self.inputs["setPrintDataForGle"]):
                outfile = open(os.path.join(pathFolder, fileName + '.dat'), 'w')
                outfile.writelines(lines)
                outfile.close()

    def plotCalculationsAcrossSets(self):
        pathFolder = self.inputs["pathBase"]
        for plotVariables in self.inputs['acrossSetsCalculationsPlot']:
            if len(plotVariables) < 4:
                raise ValueError(
                    'You did not specify variable names and labels for the x and the y Axis in a compare Plot line')
            xAxisVariable = plotVariables[0]
            yAxisVariable = plotVariables[1]
            calculationVariable = plotVariables[2]


            conditionDict = {}
            equationDict = {}
            calcVariableDict = {}
            for plotVariable in plotVariables:
                if ':' in plotVariable:
                    conditionEntry, conditionValue = plotVariable.split(':')
                    conditionDict[conditionEntry] = conditionValue
                elif "=" in plotVariable:
                    equationVariable,equationExpression = plotVariable.split('=')
                    equationDict[equationVariable] = equationExpression
                    for variable in re.split('\W',equationExpression):
                        if variable != '' and not(self.isStringNumber(variable)):
                            calcVariableDict[variable] = ''

            plotXDict = {}
            plotYDict = {}

            seriesColors = {}
            colorsCounter = 0
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

            if self.inputs["typeOfProcess"] == "json":
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)
            else:
                resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"))

            for file in resultFiles:
                with open(file) as f_in:
                    resultsDict = json.load(f_in)
                    resultsDict[''] = None

                conditionList = []
                for conditionEntry in conditionDict:
                    entryClass = type(resultsDict[conditionEntry])
                    conditionDict[conditionEntry] = entryClass(conditionDict[conditionEntry])
                    conditionList.append(conditionDict[conditionEntry]==resultsDict[conditionEntry])

                if all(conditionList):

                    #if equationVariable not in seriesColors.keys():
                    #    seriesColors[equationVariable] = colors[colorsCounter]
                    #    colorsCounter += 1

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

                    chunkVariable = ''

                    if resultsDict[chunkVariable] not in plotXDict.keys():
                        plotXDict[resultsDict[chunkVariable]] = {}
                        plotYDict[resultsDict[chunkVariable]] = {}
                        plotXDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [xAxis]
                        plotYDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [yAxis]
                    elif resultsDict[calculationVariable] not in plotXDict[resultsDict[chunkVariable]].keys():
                        plotXDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [xAxis]
                        plotYDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]] = [yAxis]
                    else:
                        plotXDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]].append(xAxis)
                        plotYDict[resultsDict[chunkVariable]][resultsDict[calculationVariable]].append(yAxis)

                else:
                    pass

            for variable in calcVariableDict:
                calcVariableDict[variable] = num.array(plotYDict[None][variable])

            calcVariableDict['equationDict'] = equationDict
            for equation in equationDict:
                calcVariableDict['equation'] = equation
                exec('equationDict[equation]='+equationDict[equation],calcVariableDict)
                seriesColors[equation] = colors[colorsCounter]
                colorsCounter += 1

            self.doc = latex.LatexReport('', '')
            if 'latexNames' in self.inputs.keys():
                if ':' in self.inputs['latexNames']:
                    latexNameFullPath = self.inputs['latexNames']
                else:
                    latexNameFullPath = os.path.join(self.configPath, self.inputs['latexNames'])
                self.doc.getLatexNamesDict(file=latexNameFullPath)
            else:
                self.doc.getLatexNamesDict()
            if 'matplotlibStyle' in self.inputs.keys():
                stylesheet = self.inputs['matplotlibStyle']
            else:
                stylesheet = 'word.mplstyle'
            if stylesheet in plt.style.available:
                self.stylesheet = stylesheet
            else:
                root = os.path.dirname(os.path.abspath(__file__))
                self.stylesheet = os.path.join(root, r"..\\plot\\stylesheets", stylesheet)
            plt.style.use(self.stylesheet)

            fig1, ax1 = plt.subplots(constrained_layout=True)
            if self.inputs["plotStyle"] == "line":
                styles = ['x-', 'x--', 'x-.', 'x:', 'o-', 'o--', 'o-.', 'o:']
            elif self.inputs["plotStyle"] == "dot":
                styles = ['x', 'o', '+', 'd', 's', 'v', '^', 'h']
            else:
                print("Invalid 'plotStyle' argument")

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

                globalXAxisVariable = list(plotXDict[chunk].keys())[0]
                index = num.argsort(plotXDict[chunk][globalXAxisVariable])
                myX = num.array(plotXDict[chunk][globalXAxisVariable])[index]
                mySize = len(myX)

                for key in equationDict.keys():
                    myY = equationDict[key]

                    if key is not None and not isinstance(key, str):
                        labelValue = round(float(key), 2)
                    elif key is not None:
                        labelValue = key
                    if key is not None and labelValue not in labelSet:
                        if not isinstance(labelValue, str):
                            label = "{:.2f}".format(labelValue)
                        else:
                            label = labelValue
                        label = self.doc.getNiceLatexNames(label)
                        labelSet.add(labelValue)

                        if 'plotStyleJson' in self.inputs:
                            plotKwargs = self.loadPlotJson(self.inputs['plotStyleJson'])
                            plotStatement = 'ax1.plot(myX, myY,style, color=seriesColors[key], label=label' + plotKwargs + ')'
                            exec(plotStatement)
                        else:
                            ax1.plot(myX, myY,style, color=seriesColors[key], label=label)
                    else:
                        ax1.plot(myX, myY,
                                 style, color=seriesColors[key])

                    # for i in range(len(myX)):
                    #     line="%8.4f\t%8.4f\n"%(myX[i],myY[i]);lines=lines+line
            lines = "!%s\t" % calculationVariable
            for chunk, style in zip(plotXDict.keys(), styles):
                for key in equationDict.keys():  # the varables that appear in the legend
                    line = "%s\t" % key;
                    lines = lines + line
                line = "\n";
                lines = lines + line

            for i in range(mySize):
                for chunk, style in zip(plotXDict.keys(), styles):

                    index = num.argsort(plotXDict[chunk][globalXAxisVariable])
                    myX = num.array(plotXDict[chunk][globalXAxisVariable])[index]
                    for key in equationDict.keys():  # the varables that appear in the legend
                        myY = equationDict[key][index]

                        if type(myX[i]) == num.str_ and type(myY[i]) == num.str_:
                            line = myX[i] + "\t" + myY[i] + "\t"
                        elif type(myX[i]) == num.str_:
                            line = myX[i] + "\t" + "%8.4f\t" %myY[i]
                        elif type(myY[i]) == num.str_:
                            line = "%8.4f\t" %myX[i] + myX[i] + "\t"
                        else:
                            line = "%8.4f\t%8.4f\t" % (myX[i], myY[i]);
                        lines = lines + line

                line = "\n";
                lines = lines + line

            if chunkVariable !='':
                legend2 = fig1.legend([dummy_line[0] for dummy_line in dummy_lines], chunkLabels,
                                      title=self.doc.getNiceLatexNames(chunkVariable), bbox_to_anchor=(1.5, 1.0),
                                      bbox_transform=ax1.transAxes)

            else:
                legend2 = None
            if calculationVariable !='':
                legend1 = fig1.legend(title=self.doc.getNiceLatexNames(calculationVariable), bbox_to_anchor=(1.2, 1.0),
                                      bbox_transform=ax1.transAxes)

            else:
                legend1 = None
            ax1.set_xlabel(self.doc.getNiceLatexNames(xAxisVariable))
            ax1.set_ylabel(self.doc.getNiceLatexNames(yAxisVariable))

            conditionsFileName = ''
            if len(conditionDict) == 1:
                conditionName = self.doc.getNiceLatexNames(sorted(conditionDict)[0])
                ax1.set_title(conditionName + ' = ' + str(conditionDict[sorted(conditionDict)[0]]))
                conditionsFileName = sorted(conditionDict)[0] + '=' + str(conditionDict[sorted(conditionDict)[0]])
            else:
                conditionsTitle = ''
                for conditionEntry in conditionDict:
                    conditionName = self.doc.getNiceLatexNames(conditionEntry)
                    conditionsTitle += conditionName + ' = ' + str(conditionDict[conditionEntry]) + ', '
                    conditionsFileName += conditionEntry + '=' + str(conditionDict[conditionEntry]) + '_'
                conditionsTitle = conditionsTitle[:-2]
                ax1.set_title(conditionsTitle)
                conditionsFileName = conditionsFileName[:-1]
            # if chunkVariable is not '':
            #
            if legend2 is not None:
                fig1.add_artist(legend2)
            # fig1.canvas.draw()
            # if legend2 is not None:
            #    ax1.add_artist(legend2)
            #    legend2.set_in_layout(True)
            # if legend1 is not None:
            #    legend1.set_in_layout(True)
            fileName = xAxisVariable + '_' + yAxisVariable + '_' + calculationVariable
            for equation in equationDict:
                fileName += '_' + equation
            fileName += '_' + conditionsFileName

            fig1.savefig(os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
            plt.close()

            if (self.inputs["setPrintDataForGle"]):
                outfile = open(os.path.join(pathFolder, fileName + '.dat'), 'w')
                outfile.writelines(lines)
                outfile.close()

    def scatterPlot(self):
        pathFolder = self.inputs["pathBase"]
        plotVariables = self.inputs['scatterPlot'][0]
        differencePlot = False
        xVariable = plotVariables[0]
        yVariables = [plotVariables[1]]
        if '-' in plotVariables[1]:
            differencePlot = True
            yVariables = plotVariables[1].split('-')
        if len(plotVariables) > 2:
            seriesVariable = plotVariables[2]
        seriesVariable = ''

        if self.inputs["typeOfProcess"] == "json":
            resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)
        else:
            resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"))

        xDict = {}
        yDict = {}
        diffDict = {}

        for file in resultFiles:
            with open(file) as f_in:
                resultsDict = json.load(f_in)
                resultsDict[''] = None

            if xVariable not in resultsDict:
                continue
            for variable in yVariables:
                if variable not in resultsDict:
                    continue

            if str(resultsDict[seriesVariable]) in xDict:
                xDict[str(resultsDict[seriesVariable])].append(resultsDict[xVariable])
                yDict[str(resultsDict[seriesVariable])].append(resultsDict[yVariables[0]])
                if differencePlot:
                    diffDict[str(resultsDict[seriesVariable])].append(resultsDict[yVariables[1]])
            else:
                xDict[str(resultsDict[seriesVariable])] = [resultsDict[xVariable]]
                yDict[str(resultsDict[seriesVariable])] = [resultsDict[yVariables[0]]]
                if differencePlot:
                    diffDict[str(resultsDict[seriesVariable])] = [resultsDict[yVariables[1]]]

        self.doc = latex.LatexReport('', '')
        if 'latexNames' in self.inputs.keys():
            if ':' in self.inputs['latexNames']:
                latexNameFullPath = self.inputs['latexNames']
            else:
                latexNameFullPath = os.path.join(self.configPath, self.inputs['latexNames'])
            self.doc.getLatexNamesDict(file=latexNameFullPath)
        else:
            self.doc.getLatexNamesDict()

        fig1, ax1 = plt.subplots(constrained_layout=True)
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colorsCounter = 0

        for entry in xDict:
            if differencePlot:
                for i in range(len(xDict[entry])):
                    ax1.plot([xDict[entry][i],xDict[entry][i]],[diffDict[entry][i],yDict[entry][i]],'-',color='grey')
                ax1.plot(xDict[entry], diffDict[entry], 'd', markeredgecolor=colors[colorsCounter], markerfacecolor='w',
                         label=self.doc.getNiceLatexNames(entry) + ', ' + self.doc.getNiceLatexNames(yVariables[1]))
                ax1.plot(xDict[entry], yDict[entry], 'd', color=colors[colorsCounter],
                         label=self.doc.getNiceLatexNames(entry) + ', ' + self.doc.getNiceLatexNames(yVariables[0]))
            else:
                ax1.plot(xDict[entry], yDict[entry], 'd', color=colors[colorsCounter],
                         label=self.doc.getNiceLatexNames(entry))
            colorsCounter += 1
        if seriesVariable != '':
            ax1.legend(loc='best')
        ax1.set_xlabel(self.doc.getNiceLatexNames(xVariable))
        if differencePlot:
            ax1.set_ylabel(self.doc.getNiceLatexNames(yVariables[0]) + ' / ' + self.doc.getNiceLatexNames(yVariables[1]))
        else:
            ax1.set_ylabel(self.doc.getNiceLatexNames(yVariables[0]))

        fileName = 'scatter_*' + xVariable
        for name in yVariables:
            fileName += '_' + name
        fileName += '_' + seriesVariable
        fileName = re.sub(r'[^\w\-_\. ]', '', fileName)

        line = seriesVariable + '\t' +  xVariable
        for name in yVariables:
            line += '\t' + name
        lines = line + '\n'
        for key in xDict:
            for i in range(len(xDict[key])):
                line = key + '\t' + str(xDict[key][i]) + '\t' + str(yDict[key][i])
                if differencePlot:
                    line += '\t' + str(diffDict[key][i])
                lines += line + '\n'

        outfile = open(os.path.join(pathFolder, fileName + '.dat'), 'w')
        outfile.writelines(lines)
        outfile.close()

        fig1.savefig(os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
        plt.close()

    def transferPathInfoToJson(self):
        parDict = {}
        for parList in self.inputs['pathInfoToJson']:
            parDict[parList[0]] = parList[1:]

        pathFolder = self.inputs["pathBase"]
        resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)

        for file in resultFiles:
            with open(file) as f_in:
                resultsDict = json.load(f_in)

            for parName in parDict:
                keyNotFound = True
                for key in parDict[parName]:
                    if key in file:
                        resultsDict[parName] = key
                        keyNotFound = False
                if keyNotFound:
                    resultsDict[parName] = ''

            self.logger.info("Adding path info to " + os.path.split(file)[-1])

            with open(file, 'w') as f_out:
                json.dump(resultsDict, f_out, indent=2, separators=(',', ': '))

    def calculateInJson(self):
        pathFolder = self.inputs["pathBase"]
        resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)

        for file in resultFiles:
            with open(file) as f_in:
                resultsDict = json.load(f_in)

            for equation in self.inputs['jsonCalc'][0]:
                if '=' not in equation:
                    info.error('Invalid equation statement in `jsonCalc`')
                    return -1
                else:
                    for variable in re.split('\W', equation):
                        if variable != '' and not (self.isStringNumber(variable)):
                            equation = equation.replace(variable,'resultsDict[\"%s\"]' %variable)
                    exec(equation)

            self.logger.info("Adding equation result to "  + os.path.split(file)[-1])

            with open(file, 'w') as f_out:
                json.dump(resultsDict, f_out, indent=2, separators=(',', ': '))

    def insertIntoJson(self):
        pathFolder = self.inputs["pathBase"]
        resultFiles = glob.glob(os.path.join(pathFolder, "**/*-results.json"), recursive=True)

        for file in resultFiles:
            with open(file) as f_in:
                resultsDict = json.load(f_in)

            for item in self.inputs['jsonInsert']:
                resultsDict[item[0]] = item[1]

            self.logger.info("Inserting additional items to " + os.path.split(file)[-1])

            with open(file, 'w') as f_out:
                json.dump(resultsDict, f_out, indent=2, separators=(',', ': '))

    def printBoxPlotGLEData(self):
        pathFolder = self.inputs["pathBase"]
        for SPFload in self.inputs['printBoxPlotGLEData']:
            SPF = SPFload[0]

        #SPF = plotVariables[0]
            #SPFload = []
            SPFValues = []

            for file in glob.glob(os.path.join(pathFolder, "**/*-results.json")):
                with open(file) as f_in:
                    resultsDict = json.load(f_in)
                #resultsDict[''] = None
                     #name, index = str(SPF).split('[')
                    #index = int(index.replace(']', ''))

                    SPFValue=resultsDict[SPF]
                    SPFValues.append(SPFValue)


        SPFV = num.array(SPFValues)

        SPFQ25 = num.quantile(SPFV, 0.25)
        SPFQ50 = num.quantile(SPFV, 0.5)
        SPFQ75 = num.quantile(SPFV, 0.75)
        SPFAv = num.average(SPFV)
        SPFMin = num.min(SPFV)
        SPFMax = num.max(SPFV)






       # line = "\n";
        #lines = lines + line

        lines = "%8.4f\t%8.4f\t%8.4f\t%8.4f\t%8.4f\t%8.4f\t" % (SPFAv, SPFMin, SPFQ25, SPFQ50, SPFQ75, SPFMax)
        outfileName = "yearSpfShpDisgle"

        outfile = open(os.path.join(pathFolder, outfileName + '.dat'), 'w')
        outfile.writelines(lines)
        outfile.close()




    def plotMonthlyBarComparison(self):
        pathFolder = self.inputs["pathBase"]
        for plotVariables in self.inputs['compareMonthlyBarsPlot']:
            seriesVariable = plotVariables[1]
            valueVariable = plotVariables[0]
            legend = []
            inVar = []
            for file in glob.glob(os.path.join(pathFolder, "**/*-results.json")):
                with open(file) as f_in:
                    resultsDict = json.load(f_in)
                    resultsDict['']=None
                legend.append(resultsDict[seriesVariable])
                inVar.append(num.array(resultsDict[valueVariable]))
            nameFile = '_'.join(plotVariables)
            titlePlot = 'Balance'
            self.plot = plot.PlotMatplotlib(language='en')
            self.plot.setPath(pathFolder)
            self.myShortMonths = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            self.doc = latex.LatexReport('', '')
            if 'latexNames' in self.inputs.keys():
                if ':' in self.inputs['latexNames']:
                    latexNameFullPath = self.inputs['latexNames']
                else:
                    latexNameFullPath = os.path.join(self.configPath,self.inputs['latexNames'])
                self.doc.getLatexNamesDict(file=latexNameFullPath)
            else:
                self.doc.getLatexNamesDict()
            if 'matplotlibStyle' in self.inputs.keys():
                stylesheet = self.inputs['matplotlibStyle']
            else:
                stylesheet = 'word.mplstyle'
            if stylesheet in plt.style.available:
                self.stylesheet = stylesheet
            else:
                root = os.path.dirname(os.path.abspath(__file__))
                self.stylesheet = os.path.join(root, r"..\\plot\\stylesheets", stylesheet)
            plt.style.use(self.stylesheet)
            niceLegend = []
            for entry in legend:
                niceLegend.append(self.doc.getNiceLatexNames(entry))
            namePdf = self.plot.plotMonthlyNBar(inVar, niceLegend, self.doc.getNiceLatexNames(valueVariable), nameFile, 10, self.myShortMonths,useYear=True)
            


    def plotComparisonSeaborn(self):
        pathFolder = self.inputs["pathBase"]
        plotVariables = self.inputs['comparePlot']
        if len(plotVariables) < 2:
            raise ValueError(
                'You did not specify variable names and labels for the x and the y Axis in a compare Plot line')
        elif len(plotVariables) == 2:
            plotVariables.extend([None,None])
        elif len(plotVariables) == 3:
            plotVariables.append([None])
        
        df = pd.DataFrame(columns=plotVariables)
        for file in glob.glob(os.path.join(pathFolder, "**/*-results.json")):
            with open(file) as f_in:
                resultsDict = json.load(f_in)
            plotDict = {k: [float("{:.2f}".format(resultsDict[k]))] for k in plotVariables}
            df = df.append(pd.DataFrame.from_dict(plotDict))
        snsPlot = sns.lineplot(x=plotVariables[0],y=plotVariables[1],hue=plotVariables[2],style=plotVariables[3],palette=None,markers=True,data=df)
        fig = snsPlot.get_figure()
        name = '_'.join(plotVariables)
        fig.savefig(os.path.join(pathFolder, name+'.png'), dpi=500)

    def changeFile(self,source,end):

        # todo: this function is currently not working

        found=False
        for i in range(len(self.lines)):
            # self.lines[i].replace(source,end)
            if(self.lines[i]==source):
                self.lines[i] = end
                found=True

        if(found==False):
            self.logger.warning("changeFile was not able to change %s by %s"%(source,end))

    def calcCost(self,fileNameList=None):

        path = self.inputs['pathBase']

        costPath = self.inputs['cost']

        cost = costConfig.costConfig()
        dictCost = cost.readCostJson(costPath)

        # for name in names:
        # path = os.path.join(pathBase, name)

        small = 15


        if(fileNameList!=None):
            cost.setFileNameList(fileNameList)

        cost.setFontsizes(small)

        cost.setDefaultData(dictCost)
        cost.readResults(path)

        cost.process(dictCost)


        # cost.plotLines(cost.pvAreaVec,"PvPeak [kW]",cost.annuityVec,"Annuity [Euro/kWh]",cost.batSizeVec,"Bat-Size [kWh]", "Annuity_vs_PvPeak", extension="pdf")
        # cost.plotLines(cost.batSizeVec,"Bat-Size [kWh]",cost.annuityVec,"Annuity [Euro/kWh]",cost.pvAreaVec,"PvPeak [kW]","Annuity_vs_Bat", extension="pdf")
        # cost.plotLines(cost.batSizeVec,"Bat-Size [kWh]",cost.RselfSuffVec,"$R_{self,suff}$",cost.pvAreaVec,"PvPeak [kW]","RselfSuff_vs_Bat", extension="pdf")
        # cost.plotLines(cost.batSizeVec,"Bat-Size [kWh]",cost.RpvGenVec,"$R_{pv,gen}$",cost.pvAreaVec,"PvPeak [kW]","RpvGen_vs_Bat", extension="pdf")

        # cost.printDataFile()

def process():
   pathBase = ''
   template = pkg_resources.resource_filename('pytrnsys_examples', 'solar_dhw/process_solar_dhw.config')
   if len(sys.argv)>1:
       pathBase,configFile = os.path.split(sys.argv[1])
   else:
       pathBase,configFile = os.path.split(template)

   if ':' not in pathBase:
       pathBase = os.path.join(os.getcwd(),pathBase)
   tool = ProcessParallelTrnsys()
   tool.readConfig(pathBase, configFile)
   tool.process()

if __name__ == '__main__':
    process()