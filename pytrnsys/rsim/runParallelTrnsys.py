#!/usr/bin/python
"""
Author : Dani Carbonell
Date   : 30.09.2016
ToDo
"""

import pytrnsys.trnsys_util.createTrnsysDeck as createDeck
import pytrnsys.rsim.executeTrnsys as exeTrnsys
import pytrnsys.trnsys_util.buildTrnsysDeck as build
import numpy as num
import os
import pytrnsys.pdata.processFiles
import string
import pytrnsys.rsim.runParallel as runPar
import pytrnsys.trnsys_util.readConfigTrnsys as readConfig
import shutil
import sys
import imp
import warnings

# from sets import Set

class RunParallelTrnsys():

    def __init__(self,_path,_name,_configFile=False):

        self.path = _path

        self.defaultInputs()
        if _configFile:
            self.readConfig(self.path,_configFile)
            self.nameBase = self.inputs['nameRef']
            self.path = self.inputs['pathBaseSimulations']
            self.getConfig()
        else:
            self.nameBase = _name

        self.addAutomaticEnergyBalance=True

        self.generateUnitTypesUsed=True


    def setDeckName(self,_name):
        self.nameBase = _name

    def setPath(self,path):
        self.path = path

    def defaultInputs(self):

        self.inputs = {}
        self.inputs["ignoreOnlinePlotter"] = False
        self.inputs["removePopUpWindow"] = False

        self.inputs["reduceCpu"] = 0
        self.inputs["combineAllCases"]   = True
        self.inputs["parseFileCreated"]  = True
        self.inputs["HOME$"] = None
        self.inputs["trnsysVersion" ]    = "TRNSYS_EXE"
        self.inputs["trnsysExePath"]     = "enviromentalVariable"
        self.inputs["copyBuildingData"]  = False #activate when Type 55 is used or change the path to the source
        self.inputs["addResultsFolder"]  = False
        self.inputs["rerunFailedCases"]       = False

        self.inputs["doAutoUnitNumbering"] = False

        self.outputFileDebugRun = os.path.join(self.path,"debugParallelRun.dat")

        self.overwriteForcedByUser = False

        self.variablesOutput = []

    def readFromFolder(self,pathRun):

        fileNames = [name for name in os.listdir(pathRun) if os.path.isdir(pathRun + "\\" + name)]

        returnNames= []
        for n in fileNames:
            if(n[0]=="."): #filfer folders such as ".gle" and so on
                pass
            else:
                returnNames.append(n)

        return returnNames

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
    def runFromNames(self,path,fileNames):

        tests = []
        self.cmds = []
        for i in range(len(fileNames)):

            tests.append(exeTrnsys.ExecuteTrnsys(path, fileNames[i]))
            tests[i].setHOMEPath(self.inputs["HOME$"])
            tests[i].setTrnsysExePath(self.inputs["trnsysExePath"])
            # tests[i].setAddBuildingData(self.inputs["copyBuildingData"]) I comment it until we use again a case where we need this functionality. I guess we dont need this anymore.
            tests[i].loadDeck()
            tests[i].changeParameter(self.parameters)
            if (self.inputs["ignoreOnlinePlotter"] == True):
                tests[i].ignoreOnlinePlotter()

            tests[i].setRemovePopUpWindow(self.inputs["removePopUpWindow"])
            tests[i].copyFilesForRunning()

            # tests[i].setTrnsysVersion("TRNSYS17_EXE")

            self.cmds.append(tests[i].getExecuteTrnsys(self.inputs))

        self.runParallel()

    def runConfig(self):


        if(self.inputs['runType']=="runFromCases"):
            cases = self.readCasesToRun(self.inputs['pathWithCasesToRun'],self.inputs['fileWithCasesToRun'])
            self.runFromNames(self.inputs['pathWithCasesToRun'],cases)
        elif(self.inputs['runType']=="runFromFolder"):
            cases = self.readFromFolder(self.inputs['pathFolderToRun'])
            self.runFromNames(self.inputs['pathFolderToRun'],cases)
        elif (self.inputs['runType'] == "runFromConfig"):
            if (self.changeDDckFilesUsed == True):
                #It actually loops around the changed files and then execute the parameters variations for each
                #so the definitons of two weathers will run all variations in two cities

                for i in range(len(self.sourceFilesToChange)):
                    sourceFile = self.sourceFilesToChange[i]
                    for j in range(len(self.sinkFilesToChange[i])):
                        sinkFile = self.sinkFilesToChange[i][j]
                        self.changeDDckFile(sourceFile,sinkFile)
                        sourceFile=sinkFile #for each case the listddck will be changed to the new one, so we need to compare with the updated string

                        if (self.foldersForDDckVariationUsed == True):
                            addFolder = self.foldersForDDckVariation[j]
                            originalPath = self.path
                            self.path = os.path.join(self.path, addFolder)
                            if not os.path.isdir(self.path):
                                os.mkdir(self.path)

                        self.buildTrnsysDeck()
                        self.createDecksFromVariant()

                        if (self.foldersForDDckVariationUsed == True):
                            self.path=originalPath #recall the original path, otherwise the next folder will be cerated inside the first

            else:
                self.buildTrnsysDeck()
                self.createDecksFromVariant()

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

            print ("name to run :%s" % fileName[i])

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
            tests[i].setHOMEPath(self.inputs["HOME$"])
            tests[i].setRemovePopUpWindow(self.inputs["removePopUpWindow"])

            # tests[i].setTrnsysVersion("TRNSYS17_EXE")

            tests[i].moveFileFromSource(fileName[i] + ".dck")

            tests[i].loadDeck()

            tests[i].changeAssignPath(inputsDict=self.inputs)

            tests[i].changeParameter(localCopyPar)

            if (self.inputs["ignoreOnlinePlotter"] == True):
                tests[i].ignoreOnlinePlotter()

            # ==============================================================================
            #             RESIZE PARAMETERS PIPE DIAMETER
            # ==============================================================================
            #            tests[i].resizeParameters()
            tests[i].cleanAndCreateResultsTempFolder()
            tests[i].moveFileFromSource()

            if(self.inputs['runCases']==True):
                cmds.append(tests[i].getExecuteTrnsys(self.inputs))

        self.cmds = cmds

    #def checkTempFolderForFinishedSimulation(self,basePath):
    #    for file in os.listdir(os.path.join(basePath,'temp')):
    #        if file.endswith('.Prt')

    def createLocationFolders(path, locations):
        for location in locations:
            if not os.path.exists(location):
                os.makedirs(location)
                print ("created directory '") + path + location + "'"

    def moveResultsFolder(path, resultsFolder, destinationFolder):
        root_src_dir = os.path.join(path, resultsFolder)
        root_target_dir = os.path.join(path, destinationFolder)

        shutil.move(root_src_dir, root_target_dir)

    def buildTrnsysDeck(self):
        """
            It builds a TRNSYS Deck from a listDdck with pathDdck using the BuildingTrnsysDeck Class.
            it reads the Deck list and writes a deck file. Afterwards it checks that the deck looks fine

        """
        # ==============================================================================
        # BUILDING OF TRNSYS DECK
        # ==============================================================================


        #  I can create folders in another path to move them in the running folder and run them one by one
        #  path = "C:\Daten\OngoingProject\Ice-Ex\systemSimulations\\check\\"

        deckExplanation = []
        deckExplanation.append("! ** New solar-ice deck. **\n")
        deck = build.BuildTrnsysDeck(self.path, self.nameBase, self.listDdck,self.pathDdck)
        deck.readDeckList(doAutoUnitNumbering=self.inputs['doAutoUnitNumbering'])

        deck.overwriteForcedByUser = self.overwriteForcedByUser
        deck.writeDeck(addedLines=deckExplanation)
        self.overwriteForcedByUser=deck.overwriteForcedByUser

        deck.checkTrnsysDeck()

        if(self.generateUnitTypesUsed==True):

            deck.saveUnitTypeFile()

        if (self.addAutomaticEnergyBalance == True):
            deck.automaticEnegyBalanceStaff(unit=600)
            deck.writeDeck()  # Deck rewritten with added printer

        # deck.addEnergyBalance()

        return deck.nameDeck

    def addParametricVariations(self,variations):
        """
            it fills a variableOutput with a list of all variations to run
            format <class 'list'>: [['Ac', 'AcollAp', 1.5, 2.0, 1.5, 2.0], ['Vice', 'VIceS', 0.3, 0.3, 0.4, 0.4]]
        """

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
            nVariations = len(variations)
            sizeOneVariation = len(variations[0])-2
            for n in range(len(variations)):
                sizeCase = len(variations[n])-2
                if(sizeCase != sizeOneVariation):
                    raise ValueError("for combineAllCases=False all variations must have same lenght :%d case n:%d has a lenght of :%d"%(sizeOneVariation,n+1,sizeCase))

            self.variablesOutput = variations

    def runParallel(self,writeLogFile=True):
        if writeLogFile:
            self.writeRunLogFile()
        runPar.runParallel(self.cmds, reduceCpu=int(self.inputs["reduceCpu"]), outputFile=self.outputFileDebugRun)


    def writeRunLogFile(self):
        logfile = open(os.path.join(self.path,'runLogFile.config'),'w')
        username = os.getenv('username')
        logfile.write('# Run created by '+username+'\n')
        logfile.write('# Ddck repositories used:\n')
        try:
            imp.find_module('git')
            found = True
            import git
        except ImportError:
            found = False

        for path in self.listDdckPaths:
            logfile.write('# '+path+'\n')
            logfile.write('# Revision Hash number: ')
            if found:
                try:
                    repo = git.Repo(path,search_parent_directories=True)
                    logfile.write(str(repo.head.object.hexsha)+'\n')
                except git.exc.InvalidGitRepositoryError:
                    logfile.write('None - Not in a Git repository \n')
            else:
                logfile.write('not found \n')
        logfile.write('\n# Config file used: \n\n')
        for line in self.lines:
            logfile.write(line+'\n')
        logfile.close()
        mainFile = sys.argv[0]
        shutil.copy(mainFile,os.path.join(self.path,'runMainFile.py'))


    def readConfig(self,path,name,parseFileCreated=False):

        """
            It reads the config file used for running TRNSYS and loads the self.inputs dictionary.
            It also loads the readed lines into self.lines
        """
        tool = readConfig.ReadConfigTrnsys()

        self.lines = tool.readFile(path,name,self.inputs,parseFileCreated=parseFileCreated,controlDataType=False)

        if(self.inputs["addResultsFolder"]=="None"):
            pass
        else:
            self.path = os.path.join(self.path, self.inputs["addResultsFolder"])

            if not os.path.isdir(self.path):
                os.mkdir(self.path)

    def changeFile(self,source,end):

        """
            It uses the self-lines readed by readConfig and change the lines from source to end.
            This is used to change a ddck file readed for another. A typical example is the weather data file
        """
        found=False
        for i in range(len(self.lines)):
            lineFilter = self.lines[i]

            if(lineFilter==source):
                self.lines[i] = end
                found=True

        if(found==False):
            # print Warning("change File was not able to change %s by %s"%(source,end))
            warnings.warn("change File was not able to change %s by %s"%(source,end))

    def changeDDckFile(self,source,end):

        """
            It uses the  self.listDdck readed by readConfig and change the lines from source to end.
            This is used to change a ddck file readed for another. A typical example is the weather data file
        """
        found=False
        nCharacters=len(source)

        for i in range(len(self.listDdck)):
            # self.lines[i].replace(source,end)
            mySource = self.listDdck[i][-nCharacters:] # I read only the last characters with the same size as the end file
            if(mySource==source):
                newDDck = self.listDdck[i][0:-nCharacters]+end
                self.listDdck[i]=newDDck
                found=True

        if(found==False):
            # print Warning("change File was not able to change %s by %s"%(source,end))
            warnings.warn("change File was not able to change %s by %s"%(source,end))

    def getConfig(self,pathDdck=None,pathDdck2=None):

        self.pathDdck = pathDdck
        self.pathDdck2 = pathDdck2

        # The vector self.inputs used in python has been filled. Now other variables for Trnsys will be filled

        self.variation = [] #parametric studies
        self.parDeck = []  # fixed values changed in all simulations
        self.listDdck = []
        self.parameters = {} #deck parameters fixed for all simulations
        self.listFit = {}
        self.listFitObs = []
        self.listDdckPaths = set() #Set()
        self.caseDict = {}
        self.sourceFilesToChange = []
        self.sinkFilesToChange = []
        self.foldersForDDckVariation = []

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
                        variation.append(float(splitLine[i]))

                self.variation.append(variation)

            elif (splitLine[0] == "deck"):

                if(splitLine[2]=="string"):
                    self.parameters[splitLine[1]]= splitLine[3]
                else:
                    self.parameters[splitLine[1]] =float(splitLine[2])

            elif (splitLine[0] == "changeDDckFile"):
                self.sourceFilesToChange.append(splitLine[1])
                sinkFilesToChange = []
                for i in range(len(splitLine)):
                    if (i<2):
                        pass
                    else:
                        sinkFilesToChange.append(splitLine[i])
                self.sinkFilesToChange.append(sinkFilesToChange)

            elif(splitLine[0] == "addDDckFolder"):
                for i in range(len(splitLine)):
                    if(i>0):
                        self.foldersForDDckVariation.append(splitLine[i])



            # elif (splitLine[0] == "")
            # elif(splitLine[0] == "Relative"):
            #
            #     self.listDdck.append(os.path.join(self.path, splitLine[1]))
            #
            # elif(splitLine[0] == "Absolute"):
            #
            #     self.listDdck.append(splitLine[1])

            elif(splitLine[0] == "fit"):
                self.listFit[splitLine[1]] = [splitLine[2],splitLine[3],splitLine[4]]
            elif (splitLine[0] == "case"):
                self.listFit[splitLine[1]] = splitLine[2:]
            elif (splitLine[0] == "fitobs"):
                self.listFitObs.append(splitLine[1])

            elif (splitLine[0] in self.inputs.keys()):
                self.listDdck.append(os.path.join(self.inputs[splitLine[0]], splitLine[1]))
                self.listDdckPaths.add(self.inputs[splitLine[0]])
            else:

                pass


        if(len(self.variation)>0):
            self.addParametricVariations(self.variation)
            self.variationsUsed=True
        else:
            self.variationsUsed=False

        if(len(self.sourceFilesToChange)>0):
            self.changeDDckFilesUsed=True
        else:
            self.changeDDckFilesUsed=False

        if(len(self.foldersForDDckVariation)>0):
            self.foldersForDDckVariationUsed = True
        else:
            self.foldersForDDckVariationUsed = False

    def copyConfigFile(self,configPath,configName):

        configFile = os.path.join(configPath,configName)
        # dstPath = os.path.join(self.inputs["pathRef"],self.inputs["addResultsFolder"],self.inputs["nameRef"],configName)
        # dstPath = os.path.join(self.inputs["pathRef"],self.inputs["addResultsFolder"],configName)
        dstPath = os.path.join(configPath,self.inputs["addResultsFolder"],configName)
        shutil.copyfile(configFile, dstPath)
        print("copied config file to: %s"% dstPath)

