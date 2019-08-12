#!/usr/bin/python
"""
Main class to process all TRNSYS results.
We need to include in this class any processing Class
customized for new projects
Author : Daniel Carbonell
Date   : 01-10-2018
ToDo : Copy config file to results folder automatically, remove processDataGshp and make it generic
       getBaseClass should be defined outside this function so that this class is not changet at all
"""

import os
import PyTrnsys.processingSimulations.debugProcess as debugProcess
import multiprocessing as mp
import runParallel as run
import PyTriHpTrnsys as ice
import PyTrnsys.utilities.utilsSpf as utils
import PyTrnsys.Trnsys.readConfigTrnsys as readConfig
import PyTriHpTrnsys.ProcessingSimulations.GshpTrnsysBaseClass as gshp
import PySpfTrnsys.ProcessingSimulations.AlStoreTrnsysBaseClass as alu
import PySpfTrnsys.ProcessingSimulations.p2GErlackerTrnsysClass as erlacker
import warnings
#we would need to pass the Class as inputs


def processDataGeneral(casesInputs):

    (baseClass,locationPath, fileName, avoidUser, maxMinAvoided, yearReadedInMonthlyFile, cleanModeLatex, firstMonthUsed,\
      processQvsT,firstMonthUsed,buildingArea,dllTrnsysPath,setPrintDataForGle,firstConsideredTime) = casesInputs

    print "starting processing of: " + fileName
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

    splitMonths = False

    if (splitMonths == True):
        # monthsSplit = [1,2,3,4,5,6,7,8,9,10,11,12]  #[5,10,11,12]
        monthsSplit = [3, 4, 5, 6]  # [5,10,11,12]

    else:
        monthsSplit = []

    if (processQvsT == True):
        test.loadQvsT("QVsT.Plt", monthsSplit=monthsSplit, addDhwCirc=False, normalized=True,cut=True)

    doProcess = True

    if (doProcess):
        test.loadAndProcess()

    # rename files if multiple years are available:
    if yearReadedInMonthlyFile != -1:
        renameFile = os.path.join(locationPath, fileName, fileName)

        fileEndingsDefault = ["-results.dat", "-report.pdf"]

        for ending in fileEndingsDefault:
            newEnding = "-Year%i" % yearReadedInMonthlyFile + ending
            try:
                os.rename(renameFile + ending, renameFile + newEnding)
            except:
                warnings.warn(
                    "File %s already exists, and thus was not saved again, needs to be improved (either not processed, or actually replaced)" % (
                                renameFile + newEnding))

        # rename files if multiple years are available:
    if yearReadedInMonthlyFile != -1:
        renameFile = os.path.join(locationPath, fileName, fileName)

        fileEndingsDefault = ["-results.dat", "-report.pdf"]

        for ending in fileEndingsDefault:
            newEnding = "-Year%i" % yearReadedInMonthlyFile + ending
            try:
                os.rename(renameFile + ending, renameFile + newEnding)
            except:
                warnings.warn(
                    "File %s already exists, and thus was not saved again, needs to be improved (either not processed, or actually replaced)" % (
                                renameFile + newEnding))

    del test  # time.sleep(5)

    return " Finished: " + fileName


def processDataGshp(casesInputs):
#Include this in the generic function

    (locationPath, fileName, avoidUser, maxMinAvoided, yearReadedInMonthlyFile, cleanModeLatex, firstMonthUsed,\
      processQvsT,firstMonthUsed,buildingArea,dllTrnsysPath,setPrintDataForGle,firstConsideredTime) = casesInputs

    print "starting processing of: " + fileName

    test = gshp.GshpTrnsysBaseClass(locationPath, fileName)

    test.setBuildingArea(buildingArea)
    test.setTrnsysDllPath(dllTrnsysPath)

    test.setPrintDataForGle(setPrintDataForGle)

    test.avoidUserDefinedCalculation = avoidUser
    test.maxMinAvoided = maxMinAvoided
    test.yearReadedInMonthylFile = yearReadedInMonthlyFile
    test.cleanModeLatex = cleanModeLatex
    test.firstConsideredTime = firstConsideredTime

    myFirstMonthLong = utils.getMonthLongName(firstMonthUsed + 1)  # starts at 1
    test.firstMonth = myFirstMonthLong
    test.firstMonthIndex = 0  # firstMonthUsed

    splitMonths = False

    if (splitMonths == True):
        monthsSplit = [3, 4, 5, 6]  # [5,10,11,12]
    else:
        monthsSplit = []

    if (processQvsT == True):
        test.loadQvsT("QVsT.Plt", monthsSplit=monthsSplit, addDhwCirc=True, normalized=True)

    doProcess = True

    if (doProcess):
        test.loadAndProcess()

    del test

    return " Finished: " + fileName



class ProcessParallelTrnsys():

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
        self.inputs["processQvsT"] = True
        self.inputs["dllTrnsysPath"] = False
        self.inputs["classProcessing"] = False

    def setFilteredFolders(self,foldersNotUsed):
        self.filteredfolder = foldersNotUsed

    def readConfig(self,path,name,parseFileCreated=False):

        tool = readConfig.ReadConfigTrnsys()
        tool.readFile(path,name,self.inputs,parseFileCreated=parseFileCreated)

    def getBaseClass(self,classProcessing,pathFolder,fileName):



        if (classProcessing == "Erlacker"):
            baseClass = erlacker.P2GErlackerTrnsysClass(pathFolder,fileName)
        elif (classProcessing == "AlStore"):
            baseClass = alu.AlStoreTrnsysBaseClass(pathFolder,fileName)
        elif (classProcessing == "BigIce"):
            baseClass = ice.BigIceTrnsysClass(pathFolder,fileName)
        else:
            baseClass = None
            raise ValueError("This function needs to be defined for each processing case")

        return baseClass

    def process(self):

        casesInputs = []
        fileName = []
        classList = []

        if (self.inputs["typeOfProcess"] == "completeFolder"):

            pathFolder = self.inputs["pathBase"]
            fileName = [name for name in os.listdir(pathFolder) if os.path.isdir(pathFolder + "\\" + name)]

            for name in fileName:

                folderUsed = True
                for i in range(len(self.filteredfolder)):
                    if (name == self.filteredfolder[i]):
                        folderUsed=False
                if(folderUsed):
                    nameWithPath = os.path.join(pathFolder, "%s\\%s-results.dat" % (name, name))

                    if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                        print "file :%s already processed" % name

                    elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.dat" % (name, name))) and  self.inputs["forceProcess"] == False:
                        print "file :%s already processed" % name

                    else:
                        baseClass = self.getBaseClass(self.inputs["classProcessing"],pathFolder,name)



                        print "file :%s will be processed" % name
                        casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"],self.inputs["maxMinAvoided"],self.inputs["yearReadedInMonthlyFile"],\
                                            self.inputs["cleanModeLatex"],self.inputs["firstMonthUsed"],self.inputs["processQvsT"],self.inputs["firstMonthUsed"],self.inputs["buildingArea"],\
                                            self.inputs["dllTrnsysPath"],self.inputs["setPrintDataForGle"],self.inputs["firstConsideredTime"]))

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
                nameWithPath = os.path.join(pathFolder, "%s\\%s-results.dat" % (name, name))

                if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                    print "file :%s already processed" % name
                else:
                    print "file :%s will be processed" % name
                    

                    baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder,self.inputs["fileName"])


                    casesInputs.append((baseClass,pathFolder, name, self.inputs["avoidUser"], self.inputs["maxMinAvoided"],
                                    self.inputs["yearReadedInMonthlyFile"], \
                                    self.inputs["cleanModeLatex"], self.inputs["firstMonthUsed"],
                                    self.inputs["processQvsT"], self.inputs["firstMonthUsed"],
                                    self.inputs["buildingArea"], \
                                    self.inputs["dllTrnsysPath"], self.inputs["setPrintDataForGle"],
                                    self.inputs["firstConsideredTime"]))

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
                        nameWithPath = os.path.join(pathFolder, "%s\\%s-results.dat" % (name, name))

                        if (os.path.isfile(nameWithPath) and self.inputs["forceProcess"] == False):
                            print "file :%s already processed" % name

                        elif os.path.isfile(os.path.join(pathFolder, "%s\\%s-Year1-results.dat" % (name, name))) and self.inputs["forceProcess"] == False:
                            print "file :%s already processed" % name

                        else:
                            baseClass = self.getBaseClass(self.inputs["classProcessing"], pathFolder, name)

                            print "file :%s will be processed" % name


                            if "hourly" in name and not "Mean" in name:
                                for i in range(self.inputs["numberOfYearsInHourlyFile"]):
                                    casesInputs.append((baseClass, pathFolder, name, self.inputs["avoidUser"], self.inputs["maxMinAvoided"],
                                                i+1, self.inputs["cleanModeLatex"], self.inputs["firstMonthUsed"],
                                                self.inputs["processQvsT"], self.inputs["firstMonthUsed"],
                                                self.inputs["buildingArea"], \
                                                self.inputs["dllTrnsysPath"], self.inputs["setPrintDataForGle"],
                                                self.inputs["firstConsideredTime"]))
                            else:
                                casesInputs.append((baseClass, pathFolder, name, self.inputs["avoidUser"],
                                                    self.inputs["maxMinAvoided"],
                                                    self.inputs["yearReadedInMonthlyFile"], \
                                                    self.inputs["cleanModeLatex"], self.inputs["firstMonthUsed"],
                                                    self.inputs["processQvsT"], self.inputs["firstMonthUsed"],
                                                    self.inputs["buildingArea"], \
                                                    self.inputs["dllTrnsysPath"], self.inputs["setPrintDataForGle"],
                                                    self.inputs["firstConsideredTime"]))

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
            if(self.inputs["classProcessing"]=="GSHP"):
                results = pool.map(processDataGshp,casesInputs)
            else:
                results = pool.map(processDataGeneral, casesInputs)

            pool.close()

            debug.addLines(results)
            debug.finish()
        else:
            for i in range(len(casesInputs)):
                if (self.inputs["classProcessing"] == "GSHP"):
                    processDataGshp(casesInputs[i])
                else:
                    # test = erlacker.P2GErlackerTrnsysClass(pathFolder,fileName[i])
                    processDataGeneral(casesInputs[i])

    def changeFile(self,source,end):

        # todo: this function is currently not working

        found=False
        for i in range(len(self.lines)):
            # self.lines[i].replace(source,end)
            if(self.lines[i]==source):
                self.lines[i] = end
                found=True

        if(found==False):
            print Warning("changeFile was not able to change %s by %s"%(source,end))