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
import pkg_resources
try:
    import pytrnsys_examples
except ImportError:
    pass
#we would need to pass the Class as inputs
import pytrnsys.utils.log as log


def processDataGeneral(casesInputs):
    """
    processes all the specified cases

    Parameters
    ----------
    casesInputs: list of str
        list of strings with all cases to run

    Returns
    -------

    """

    (baseClass,locationPath, fileName, inputs) = casesInputs

    #    locationPath = inputs.pop(0)
    #    fileName,avoidUser,maxMinAvoided,yearReadedInMonthlyFile,cleanModeLatex,firstMonthUsed,processQvsT

    test = baseClass

    # casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"],self.inputs["maxMinAvoided"],self.inputs["yearReadedInMonthlyFile"],\
    #                     self.inputs["cleanModeLatex"],self.inputs["firstMonthUsed"],self.inputs["processQvsT"],self.inputs["firstMonthUsed"],self.inputs["buildingArea"],\
    #                     self.inputs["dllTrnsysPath"],self.inputs["setPrintDataForGle"],self.inputs["firstConsideredTime"]))


    test.setInputs(inputs)
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
    if inputs["yearReadedInMonthlyFile"] != -1:
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
                warnings.warn(
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

    def defaultInputs(self):

        self.inputs = {}
        self.inputs["isTrnsys"] = True
        self.inputs["processParallel"] = True
        self.inputs["avoidUser"]    = False
        self.inputs["processQvsT"]  = True
        self.inputs["cleanModeLatex"] = False
        self.inputs["maxMinAvoided"] = False
        self.inputs["yearReadedInMonthlyFile"] = -1
        self.inputs["process"] = True
        self.inputs["firstMonthUsed"] = 6     # 0=January 1=February 7=August
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

    def setFilteredFolders(self,foldersNotUsed):
        self.filteredfolder = foldersNotUsed

    def readConfig(self,path,name,parseFileCreated=False):
        self.configPath = path
        tool = readConfig.ReadConfigTrnsys()
        tool.readFile(path,name,self.inputs,parseFileCreated=parseFileCreated)
        self.logger = log.setup_custom_logger('root', self.inputs['outputLevel'])
        if 'latexNames' in self.inputs.keys():
            if ':' not in self.inputs['latexNames']:
                self.inputs['latexNames'] = os.path.join(self.configPath, self.inputs['latexNames'])


    def getBaseClass(self, classProcessing, pathFolder, fileName):

       return processTrnsys.ProcessTrnsysDf(pathFolder, fileName)

    def process(self):

        casesInputs = []
        fileName = []
        classList = []

        if os.path.exists(os.path.join(self.inputs['pathBase'],'Summary.dat')):
            os.remove(os.path.join(self.inputs['pathBase'],'Summary.dat'))

        if (self.inputs["typeOfProcess"] == "completeFolder"):

            pathFolder = self.inputs["pathBase"]
            files =glob.glob(os.path.join(pathFolder, "**/*.lst"), recursive=True)
            fileName = [Path(name).parts[-2] for name in files]
            relPaths = [os.path.relpath(os.path.dirname(file),pathFolder) for file in files]
            for relPath in relPaths:
                name = Path(relPath).parts[-1]
                folderUsed = True
                for i in range(len(self.filteredfolder)):
                    if (name == self.filteredfolder[i]):
                        folderUsed=False
                if(folderUsed):
                    nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (relPath, name))

                    if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                        self.logger.debug("file :%s already processed" % name)

                    elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (relPath, name))) and  self.inputs["forceProcess"] == False:
                        self.logger.debug("file :%s already processed" % name)

                    else:
                        if len(Path(relPath).parts)>1:
                            newPath = os.path.join(pathFolder,os.path.join(*list(Path(relPath).parts[:-1])))
                        else:
                            newPath = pathFolder
                        baseClass = self.getBaseClass(self.inputs["classProcessing"],newPath,name)

                        self.logger.debug("file :%s will be processed" % name)
                        # casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"],self.inputs["maxMinAvoided"],self.inputs["yearReadedInMonthlyFile"],\
                        #                     self.inputs["cleanModeLatex"],self.inputs["firstMonthUsed"],self.inputs["processQvsT"],self.inputs["firstMonthUsed"],self.inputs["buildingArea"],\
                        #                     self.inputs["dllTrnsysPath"],self.inputs["setPrintDataForGle"],self.inputs["firstConsideredTime"]))

                        casesInputs.append((baseClass,pathFolder, name, self.inputs))

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
            #         print ("file :%s will be processed" % name)
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
                            self.logger.debug("file :%s already processed" % name)

                        elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (name, name))) and self.inputs["forceProcess"] == False:
                            self.logger.debug("file :%s already processed" % name)

                        else:
                            baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name)

                            self.logger.debug("file :%s will be processed" % name)


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
                                    self.logger.debug("file :%s already processed" % name)

                                elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (name, name))) and \
                                        self.inputs["forceProcess"] == False:
                                    self.logger.debug("file :%s already processed" % name)

                                else:
                                    baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name)

                                    self.logger.debug("file :%s will be processed" % name)

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
                                    else:
                                        pass
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
                processDataGeneral(casesInputs[i])
                # try:
                #     processDataGeneral(casesInputs[i])
                # except:
                #     print('WARNING: the following case failed: ' + casesInputs[i][2])
        if 'cost' in self.inputs.keys():
            self.calcCost()

        if 'comparePlot' in self.inputs.keys():
            print("yes1")
            self.plotComparison()
            
        if 'compareMonthlyBarsPlot' in self.inputs.keys():
            self.plotMonthlyBarComparison()


        if 'printBoxPlotGLEData' in self.inputs.keys():
            print("yes")
            self.printBoxPlotGLEData()

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
            plotXDict = {}
            plotYDict = {}
    
            seriesColors = {}
            colorsCounter = 0
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
            for file in glob.glob(os.path.join(pathFolder, "**/*-results.json")):
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
            styles = ['x-','x--','x-.','x:','o-','o--','o-.','o:']

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

                            line = "%8.4f\t%8.4f\t" % (myX[i],myY[i]);
                            lines = lines + line

                    line = "\n"; lines = lines + line

            # box = ax1.get_position()
            #ax1.set_position([box.x0, box.y0, box.width, box.height])

            if chunkVariable is not '':
                legend2=fig1.legend([dummy_line[0] for dummy_line in dummy_lines],chunkLabels,title=self.doc.getNiceLatexNames(chunkVariable), bbox_to_anchor=(1.5, 1.0), bbox_transform=ax1.transAxes)

            else:
                legend2 = None
            if seriesVariable is not '':
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
            fileName = xAxisVariable + '_' + yAxisVariable + '_' + seriesVariable + '_' + chunkVariable
            fig1.savefig(os.path.join(pathFolder, fileName + '.png'), bbox_inches='tight')
            plt.close()

            if(self.inputs["setPrintDataForGle"]):
                outfile = open(os.path.join(pathFolder, fileName + '.dat'), 'w')
                outfile.writelines(lines)
                outfile.close()
                # self.plot.gle.getEasyPlot(self, nameGleFile, fileNameData, legends, useSameStyle=True):

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
            namePdf = self.plot.plotMonthlyNBar(inVar, legend, self.doc.getNiceLatexNames(valueVariable), nameFile, 10, self.myShortMonths,useYear=True)
            


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

    def calcCost(self):

        path = self.inputs['pathBase']

        costPath = self.inputs['cost']

        dictCost = costConfig.costConfig.readCostJson(costPath)

        # for name in names:
        # path = os.path.join(pathBase, name)

        small = 15
        cost = costConfig.costConfig()
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