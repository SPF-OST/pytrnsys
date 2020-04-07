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
import seaborn as sns
import pytrnsys_spf.psim.costConfig as costConfig
#we would need to pass the Class as inputs


def processDataGeneralDeprecated(casesInputs):
    """
    processes all the specified cases

    Parameters
    ----------
    casesInputs: list of str
        list of strings with all cases to run

    Returns
    -------

    """

    (baseClass,locationPath, fileName, avoidUser, maxMinAvoided, yearReadedInMonthlyFile, cleanModeLatex, firstMonthUsed,\
      processQvsT,firstMonthUsed,buildingArea,dllTrnsysPath,setPrintDataForGle,firstConsideredTime) = casesInputs

    print ("starting processing of: %s"% fileName)
    #    locationPath = inputs.pop(0)
    #    fileName,avoidUser,maxMinAvoided,yearReadedInMonthlyFile,cleanModeLatex,firstMonthUsed,processQvsT

    test = baseClass

    test.setBuildingArea(buildingArea)
    test.setTrnsysDllPath(dllTrnsysPath)

    # test.setTrnsysVersion("TRNSYS17_EXE")

    test.setPrintDataForGle(setPrintDataForGle)

    test.avoidUserDefinedCalculation = avoidUser
    test.maxMinAvoided = maxMinAvoided
    test.yearReadedInMonthylFile = yearReadedInMonthlyFile
    test.cleanModeLatex = cleanModeLatex
    test.firstConsideredTime = firstConsideredTime

    myFirstMonthLong = utils.getMonthLongName(firstMonthUsed + 1)  # starts at 1
    test.firstMonth = myFirstMonthLong
    test.firstMonthIndex = 0  # firstMonthUsed

    doProcess = True

    if (doProcess):
        test.loadAndProcess()

    # rename files if multiple years are available:
    if yearReadedInMonthlyFile != -1:
        renameFile = os.path.join(locationPath, fileName, fileName)

        fileEndingsDefault = ["-results.json", "-report.pdf"]

        for ending in fileEndingsDefault:
            newEnding = "-Year%i" % yearReadedInMonthlyFile + ending
            try:
                os.rename(renameFile + ending, renameFile + newEnding)
                print("renamed %s"%newEnding)
            except:
                warnings.warn(
                    "File %s already exists, and thus was not saved again, needs to be improved (either not processed, or actually replaced)" % (
                                renameFile + newEnding))


    del test  # time.sleep(5)

    return " Finished: " + fileName

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

    print ("starting processing of: %s"% fileName)
    #    locationPath = inputs.pop(0)
    #    fileName,avoidUser,maxMinAvoided,yearReadedInMonthlyFile,cleanModeLatex,firstMonthUsed,processQvsT

    test = baseClass

    # casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"],self.inputs["maxMinAvoided"],self.inputs["yearReadedInMonthlyFile"],\
    #                     self.inputs["cleanModeLatex"],self.inputs["firstMonthUsed"],self.inputs["processQvsT"],self.inputs["firstMonthUsed"],self.inputs["buildingArea"],\
    #                     self.inputs["dllTrnsysPath"],self.inputs["setPrintDataForGle"],self.inputs["firstConsideredTime"]))


    test.setInputs(inputs)
    if "latexNames" in inputs:
        test.setLatexNamesFile(inputs["latexNames"])
    else:
        test.setLatexNamesFile(None)
    if "matplotlibStyle" in inputs:
        test.setMatplotlibStyle(inputs["matplotlibStyle"])
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

    if (doProcess):
        test.loadAndProcess()

    # rename files if multiple years are available:
    if inputs["yearReadedInMonthlyFile"] != -1:
        renameFile = os.path.join(locationPath, fileName, fileName)

        fileEndingsDefault = ["-results.json", "-report.pdf","-plots.html"]

        for ending in fileEndingsDefault:
            newEnding = "-Year%i" % inputs["yearReadedInMonthlyFile"] + ending
            try:
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
        self.inputs["processParallel"] = True
        self.inputs["avoidUser"]    = False
        self.inputs["processQvsT"]  = True
        self.inputs["cleanModeLatex"] = False
        self.inputs["maxMinAvoided"] = False
        self.inputs["yearReadedInMonthlyFile"] = -1
        self.inputs["process"] = True
        self.inputs["firstMonthUsed"] = 6     # 0=January 1=February 7=August
        self.inputs["reduceCpu"] = 0
        self.inputs["typeOfProcess"] = "completeFolder" # "casesDefined"
        self.inputs["forceProcess"]  =  True #even if results file exist it proceess the results, otherwise it checks if it exists
        self.inputs["pathBase"] = False
        self.inputs["setPrintDataForGle"] = True
        self.inputs['firstConsideredTime'] = None #Be carefull here. Thsi will not be proprly filtered
        self.inputs["buildingArea"] = 1072.
        self.inputs["parseFileCreated"] = False
        self.inputs["dllTrnsysPath"] = False
        self.inputs["classProcessing"] = False
        self.inputs["latexExePath"] = "Unknown"

    def setFilteredFolders(self,foldersNotUsed):
        self.filteredfolder = foldersNotUsed

    def readConfig(self,path,name,parseFileCreated=False):

        tool = readConfig.ReadConfigTrnsys()
        tool.readFile(path,name,self.inputs,parseFileCreated=parseFileCreated)

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
            fileName = [name for name in os.listdir(pathFolder) if os.path.isdir(pathFolder + "\\" + name)]

            for name in fileName:

                folderUsed = True
                for i in range(len(self.filteredfolder)):
                    if (name == self.filteredfolder[i]):
                        folderUsed=False
                if(folderUsed):
                    nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (name, name))

                    if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                        print ("file :%s already processed" % name)

                    elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (name, name))) and  self.inputs["forceProcess"] == False:
                        print ("file :%s already processed" % name)

                    else:
                        baseClass = self.getBaseClass(self.inputs["classProcessing"],pathFolder,name)

                        print ("file :%s will be processed" % name)
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

            fileName.append(name)

            folderUsed = True
            for i in range(len(self.filteredfolder)):
                if (name == self.filteredfolder[i]):
                    folderUsed = False
            if (folderUsed):
                nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (name, name))

                if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                    print ("file :%s already processed" % name)
                else:
                    print ("file :%s will be processed" % name)
                    

                    baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder,self.inputs["fileName"])


                    # casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"], self.inputs["maxMinAvoided"],
                    #                 self.inputs["yearReadedInMonthlyFile"], \
                    #                 self.inputs["cleanModeLatex"], self.inputs["firstMonthUsed"],
                    #                 self.inputs["processQvsT"], self.inputs["firstMonthUsed"],
                    #                 self.inputs["buildingArea"], \
                    #                 self.inputs["dllTrnsysPath"], self.inputs["setPrintDataForGle"],
                    #                 self.inputs["firstConsideredTime"]))

                    casesInputs.append((baseClass,pathFolder, name, self.inputs))

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
                            print ("file :%s already processed" % name)

                        elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (name, name))) and self.inputs["forceProcess"] == False:
                            print ("file :%s already processed" % name)

                        else:
                            baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name)

                            print ("file :%s will be processed" % name)


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

            for city in self.inputs["cities"]:
                pathFolder = os.path.join(self.inputs["pathBase"], city)
                fileName = [name for name in os.listdir(pathFolder) if os.path.isdir(pathFolder + "\\" + name)]

                for name in fileName:

                    for type in self.inputs['fileTypes']:
                        if type in name:

                            folderUsed = True
                            for i in range(len(self.filteredfolder)):
                                if (name == self.filteredfolder[i]):
                                    folderUsed = False
                            if (folderUsed):
                                nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (name, name))

                                if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                                    print("file :%s already processed" % name)

                                elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.json" % (name, name))) and \
                                        self.inputs["forceProcess"] == False:
                                    print("file :%s already processed" % name)

                                else:
                                    baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name)

                                    print("file :%s will be processed" % name)

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
                                                inputs[i]['yearReadedInMonthlyFile'] = self.inputs[
                                                                                           "yearReadedInMonthlyFile"] + i
                                                casesInputs.append((baseClass, pathFolder, name, inputs[i]))
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
                processDataGeneral(casesInputs[i])
                
        if 'cost' in self.inputs.keys():
            self.calcCost()

        if 'comparePlot' in self.inputs.keys():
            self.plotComparison()

    def plotComparison(self):
        pathFolder = self.inputs["pathBase"]
        plotVariables = self.inputs['comparePlot']
        if len(plotVariables) < 2:
            raise ValueError(
                'You did not specify variable names and labels for the x and the y Axis in a compare Plot line')
        xAxisVariable = plotVariables[0]
        yAxisVariable = plotVariables[1]
        seriesVariable = ''
        if len(plotVariables) >= 3:
            seriesVariable = plotVariables[2]
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
            if resultsDict[seriesVariable] not in seriesColors.keys():
                seriesColors[resultsDict[seriesVariable]]=colors[colorsCounter]
                colorsCounter+=1
            if resultsDict[chunkVariable] not in plotXDict.keys():
                plotXDict[resultsDict[chunkVariable]] = {}
                plotYDict[resultsDict[chunkVariable]] = {}
                plotXDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [resultsDict[xAxisVariable]]
                plotYDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [resultsDict[yAxisVariable]]
            elif resultsDict[seriesVariable] not in plotXDict[resultsDict[chunkVariable]].keys():
                plotXDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [resultsDict[xAxisVariable]]
                plotYDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]] = [resultsDict[yAxisVariable]]
            else:
                plotXDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]].append(resultsDict[xAxisVariable])
                plotYDict[resultsDict[chunkVariable]][resultsDict[seriesVariable]].append(resultsDict[yAxisVariable])

        self.doc = latex.LatexReport('', '')
        if 'latexNames' in self.inputs.keys():
            self.doc.getLatexNamesDict(file=self.inputs['latexNames'])
        else:
            self.doc.getLatexNamesDict()

        fig1 = plt.figure(1)
        ax1 = fig1.add_subplot(111)
        styles = ['x-','x--','x-.','x:','o-','o--','o-.','o:']

        dummy_lines = []
        chunkLabels = []
        labelSet = set()
        for chunk,style in zip(plotXDict.keys(),styles):
            dummy_lines.append(ax1.plot([],[],style,c='black'))
            chunkLabel = round(float(chunk), 2)
            chunkLabels.append("{:.2f}".format(chunkLabel))
            for key in plotXDict[chunk].keys():
                index = num.argsort(plotXDict[chunk][key])

                labelValue=round(float(key),2)
                if labelValue not in labelSet:
                    label = f'{labelValue:.2f}'
                    labelSet.add(labelValue)
                else:
                    label = ''
                ax1.plot(num.array(plotXDict[chunk][key])[index], num.array(plotYDict[chunk][key])[index], style,color=seriesColors[key], label=label)

        legend2=plt.legend([dummy_line[0] for dummy_line in dummy_lines],chunkLabels,title=self.doc.getNiceLatexNames(chunkVariable),loc=4)
        ax1.legend(title=self.doc.getNiceLatexNames(seriesVariable), loc=1)
        ax1.set_xlabel(self.doc.getNiceLatexNames(xAxisVariable))
        ax1.set_ylabel(self.doc.getNiceLatexNames(yAxisVariable))
        ax1.add_artist(legend2)
        plt.tight_layout()
        fig1.savefig(os.path.join(pathFolder, xAxisVariable + '_' + yAxisVariable + '_' + seriesVariable + '_' + chunkVariable+'.png'))
        plt.close()

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
            plotDict = {k: ["{:.2f}".format(resultsDict[k])] for k in plotVariables}
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
            print ("changeFile was not able to change %s by %s"%(source,end))

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
