#!/usr/bin/python
# -*- coding: utf-8 -*-

import createTrnsysDeck as createDeck
import executeTrnsys as exeTrnsys
import BuildTrnsysDeck as build
import numpy as num
import os
import processFiles
import string
import runParallel as runPar
import readConfigTrnsys as readConfig
import shutil

class RunParallelTrnsys():

    def __init__(self,_path,_name,_configFile=False):
        # TODO: (MB) Do we aim towards having a config file for each simulation?
        # In that case I would move the read in of the config file here in the constructor.
        self.path = _path

        self.defaultInputs()
        if _configFile:
            self.readConfig(self.path,_configFile)

            self.nameBase = self.inputs['nameRef']
        else:
            self.nameBase = _name


    def setDeckName(self,_name):
        self.nameBase = _name

    def setPath(self,path):
        self.path = path

    def defaultInputs(self):

        self.inputs = {}
        self.inputs["ignoreOnlinePlotter"] = False
        self.inputs["reduceCpu"] = 0
        self.inputs["combineAllCases"]   = True
        self.inputs["parseFileCreated"]  = True
        self.inputs["commonTrnsyFolder"] = None
        self.inputs["trnsysVersion" ]    = "TRNSYS_EXE"
        self.inputs["trnsysExePath"]     = "enviromentalVariable"
        self.inputs["copyBuildingData"]  = False #activate when Type 55 is used or change the path to the source
        self.inputs["addResultsFolder"]  = False

        self.outputFileDebugRun = os.path.join(self.path,"debugParallelRun.dat")

        self.overwriteForcedByUser = False

        self.variablesOutput = []

    def readFromFolder(self,pathRun):

        fileNames = [name for name in os.listdir(pathRun) if os.path.isdir(pathRun + "\\" + name)]

        return fileNames

        # self.runFromNames(fileNames)

    def readCasesToRun(self,pathRun,nameFileWithCasesToRun):

        fileToRunWithPath = os.path.join(pathRun, nameFileWithCasesToRun)
        file = open(fileToRunWithPath, "r")
        lines = file.readlines()
        cases = []
        for line in lines:
            if(line=="\n"): #ignoring blank lines
                pass
            else:
                cases.append(line[:-1])  # remove \n

        return cases
    def runFromNames(self,fileNames):

        tests = []
        self.cmds = []
        for i in range(len(fileNames)):

            tests.append(exeTrnsys.ExecuteTrnsys(self.path, fileNames[i]))
            tests[i].setCommonTrnsysFolderPath(self.inputs["commonTrnsyFolder"])
            tests[i].setTrnsysExePath(self.inputs["trnsysExePath"])
            tests[i].setAddBuildingData(self.inputs["copyBuildingData"])
            tests[i].loadDeck()
            tests[i].changeParameter(self.parameters)
            if (self.inputs["ignoreOnlinePlotter"] == True):
                tests[i].ignoreOnlinePlotter()

            tests[i].copyFilesForRunning()

            # tests[i].setTrnsysVersion("TRNSYS17_EXE")

            self.cmds.append(tests[i].getExecuteTrnsys())

        self.runParallel()

    def createDecksFromVariant(self,fitParameters={}):

        variations = self.variablesOutput
        parameters = self.parameters
        parameters.update(fitParameters)

        # if (self.inputs["combineAllCases"]):
        #     sizeUsed = len(variations[0])
        #     for var in variations:
        #         if (len(var) != sizeUsed):
        #             print "sizeUsed:%d var:%s size:%d" % (sizeUsed, var, len(var))
        #             raise ValueError("FATAL ERROR. variations must be of the same size if combineAllCases = True")

        myDeckGenerator = createDeck.CreateTrnsysDeck(self.path, self.nameBase, variations)
        myDeckGenerator.combineAllCases = self.inputs["combineAllCases"]

        # creates a list of decks with the appripiate name but nothing changed inside!!
        if(self.variationsUsed):
            fileName = myDeckGenerator.generateDecks()
        else:
            fileName=[]
            fileName.append(self.nameBase)

        tests = []
        cmds  = []

        variablePath = self.path

        for i in range(len(fileName)):

            print "name to run :%s" % fileName[i]
            #        if useLocationStructure:
            #            variablePath = os.path.join(path,location) #assign subfolder for path

            #           # Parameters changed by variation
            localCopyPar = dict.copy(parameters)  #

            if (self.variationsUsed):
                myParameters = myDeckGenerator.getParameters(i)
                localCopyPar.update(myParameters)

            #           # We add to the global parameters that also need to be modified
            #  If we assign like localCopyPar = parameters, then the parameters will change with localCopyPar !!
            # Otherwise we change the global parameter and some values of last variation will remain.
            #            newPath = path + fileName[i]
            #            newFileDck = newPath+"\\"+fileName[i]+".dck"
            #            print "path:%s fileName:%s newPath:%s newFileDeck:%s"%(path,fileName[i],newPath,newFileDck)


            tests.append(exeTrnsys.ExecuteTrnsys(variablePath, fileName[i]))

            tests[i].setTrnsysExePath(self.inputs["trnsysExePath"])
            tests[i].setAddBuildingData(self.inputs["copyBuildingData"])
            tests[i].setCommonTrnsysFolderPath(self.inputs["commonTrnsyFolder"])
            # tests[i].setTrnsysVersion("TRNSYS17_EXE")

            tests[i].moveFileFromSource(fileName[i] + ".dck")

            tests[i].loadDeck()

            tests[i].changeAssignPath(commonTrnsysFolder=self.inputs['commonTrnsyFolder'])

            tests[i].changeParameter(localCopyPar)
            if (self.inputs["ignoreOnlinePlotter"] == True):
                tests[i].ignoreOnlinePlotter()

            # ==============================================================================
            #             RESIZE PARAMETERS PIPE DIAMETER
            # ==============================================================================
            #            tests[i].resizeParameters()
            tests[i].copyFilesForRunning()

            cmds.append(tests[i].getExecuteTrnsys())

        self.cmds = cmds

    def createLocationFolders(path, locations):
        for location in locations:
            if not os.path.exists(location):
                os.makedirs(location)
                print "created directory '" + path + location + "'"

    def moveResultsFolder(path, resultsFolder, destinationFolder):
        root_src_dir = os.path.join(path, resultsFolder)
        root_target_dir = os.path.join(path, destinationFolder)

        shutil.move(root_src_dir, root_target_dir)

    def buildTrnsysDeck(self):

        # ==============================================================================
        # BUILDING OF TRNSYS DECK
        # ==============================================================================


        #  I can create folders in another path to move them in the running folder and run them one by one
        #  path = "C:\Daten\OngoingProject\Ice-Ex\systemSimulations\\check\\"

        deckExplanation = []
        deckExplanation.append("! ** New solar-ice deck. **\n")
        deck = build.BuildTrnsysDeck(self.path, self.nameBase, self.listDdck,self.pathDdck)
        deck.readDeckList()
        deck.overwriteForcedByUser = self.overwriteForcedByUser
        deck.writeDeck(addedLines=deckExplanation)
        self.overwriteForcedByUser=deck.overwriteForcedByUser
        deck.checkTrnsysDeck()

        return deck.nameDeck

    def addParametricVariations(self,variations):

        # nVariables = len(variations)
        # for n in range(nVariables):
        #     names = []
        #     names.append(variations[n][0]) #namesPrinted
        #     names.append(variations[n][1]) #nameDeck
        #
        #     self.variationsOutput.append(names)


        if(self.inputs["combineAllCases"]==True):

            labels = []
            values = []
            for i, row in enumerate(variations):
                labels.append(row[:2])
                values.append(row[2:])

            value_permutations = num.array(num.meshgrid(*values), dtype=object).reshape(len(variations), -1)
            result = num.concatenate((labels, value_permutations), axis=1)
            self.variablesOutput = result.tolist()

        else:
            raise ValueError("Not implemented yet")

            # for n in range(nVariables):
            #     size = 0
            #     for k in range(nVariables):
            #         if(n!=k):
            #             size = size+len(variations[k])-2 #two positions are for names
            #     for m in range(size):
            #         for i in range(2,len(variations[n]),1):
            #             variationsOutput[n].append(variations[n][i])

            # for n in range(nVariables):
            #     for i in range(2, len(variations[n]), 1):
            #         for k in range(nVariables):
            #             self.variationsOutput[n].append(variations[n][i])

    def runParallel(self):

        runPar.runParallel(self.cmds, reduceCpu=int(self.inputs["reduceCpu"]), outputFile=self.outputFileDebugRun)

    def readConfig(self,path,name,parseFileCreated=False):

        tool = readConfig.ReadConfigTrnsys()

        self.lines = tool.readFile(path,name,self.inputs,parseFileCreated=parseFileCreated,controlDataType=False)

        if(self.inputs["addResultsFolder"]=="None"):
            pass
        else:
            self.path = os.path.join(self.path, self.inputs["addResultsFolder"])

            if not os.path.isdir(self.path):
                os.mkdir(self.path)

    def changeFile(self,source,end):

        found=False
        for i in range(len(self.lines)):
            # self.lines[i].replace(source,end)
            if(self.lines[i]==source):
                self.lines[i] = end
                found=True

        if(found==False):
            print Warning("changeFile was not able to change %s by %s"%(source,end))

    def getConfig(self,baseList):

        self.pathDdck = baseList

        # The vector self.inputs used in python has been filled. Now other variables for Trnsys will be filled

        self.variation = [] #parametric studies
        self.parDeck = []  # fixed values changed in all simulations
        self.listDdck = []
        self.parameters = {} #deck parameters fixed for all simulations
        self.listFit = {}
        self.listFitObs = []
        for line in self.lines:

            splitLine = line.split()

            if (splitLine[0] == "variation"):
                variation = []
                for i in range(len(splitLine)):
                    if(i==0):
                        pass
                    elif (i<=2):
                        variation.append(splitLine[i])
                    else:
                        variation.append(string.atof(splitLine[i]))

                self.variation.append(variation)

            elif (splitLine[0] == "deck"):

                self.parameters[splitLine[1]] = string.atof(splitLine[2])

            elif (splitLine[0] == "Base"):

                self.listDdck.append(os.path.join(self.pathDdck,splitLine[1]))

            elif(splitLine[0] == "Relative"):

                self.listDdck.append(os.path.join(self.path, splitLine[1]))

            elif(splitLine[0] == "Absolute"):

                self.listDdck.append(splitLine[1])
            elif(splitLine[0] == "fit"):
                self.listFit[splitLine[1]] = [splitLine[2],splitLine[3],splitLine[4]]
            elif (splitLine[0] == "fitobs"):
                self.listFitObs.append(splitLine[1])
            else:

                pass


        if(len(self.variation)>0):
            self.addParametricVariations(self.variation)
            self.variationsUsed=True
        else:
            self.variationsUsed=False



    def copyConfigFile(self,configPath,configName):

        configFile = os.path.join(configPath,configName)
        dstPath = os.path.join(self.inputs["pathRef"],self.inputs["addResultsFolder"],self.inputs["nameRef"],configName)
        dstPath = os.path.join(self.inputs["pathRef"],self.inputs["addResultsFolder"],configName)
        shutil.copyfile(configFile, dstPath)
        print "print copied config file to: %s" % dstPath

