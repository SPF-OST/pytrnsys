# pylint: skip-file
# type: ignore

import json
import os
import pathlib as _pl
import shutil
from copy import deepcopy

import pandas as pd

import pytrnsys.rsim.executeTrnsys as exeTrnsys
import pytrnsys.rsim.getConfigMixin as _gcm
import pytrnsys.rsim.runParallel as runPar
import pytrnsys.trnsys_util.buildTrnsysDeck as _btd
import pytrnsys.trnsys_util.createTrnsysDeck as createDeck
import pytrnsys.trnsys_util.readConfigTrnsys as readConfig
import pytrnsys.trnsys_util.replaceAssignStatements as _ras
import pytrnsys.utils.log as log
import pytrnsys.utils.result as _res


class RunParallelTrnsys(_gcm.GetConfigMixin):
    """
    Main class that represents a simulation job of pytrnsys. The standardized way of initiating it is by providing a
    config-file, in which case the run defined in the config case is started automatically.

    Args
    ----------
    path : str
        Path to the config file.
    name : str
        Main name of the Deck file, optional, default: "TrnsysRun". (Deprecated - should be defined in the config file.)
    configFile : str, None
        Name of the config file. If no argument is passed, the run has to be started by executing the methods externally
        , optional, default: None.

    Attributes
    ----------
    inputs : dict
        Dictionary containing the entries of the config file

    """

    def __init__(self, pathConfig, name="pytrnsysRun", configFile=None, runPath=None):
        super().__init__()

        self.pathConfig = pathConfig

        self.ddckPlaceHolderValuesJsonPath = None

        self.defaultInputs()
        self.cmds = []
        if runPath == None:
            self.path = os.getcwd()
        else:
            self.path = runPath

        if configFile is not None:
            self.readConfig(self.pathConfig, configFile)

            if "nameRef" in self.inputs:
                self.nameBase = self.inputs["nameRef"]
            else:
                if name == "pytrnsysRun":
                    self.nameBase = self.inputs["addResultsFolder"]

            if "projectPath" in self.inputs:
                self.path = self.inputs["projectPath"]
            elif runPath == None:
                self.path = os.getcwd()

            self.outputFileDebugRun = os.path.join(self.path, "debugParallelRun.dat")
            self.getConfig()

            result = self.runConfig()
            if _res.isError(result):
                _res.error(result).throw()

            self.runParallel()
        else:
            self.outputFileDebugRun = os.path.join(self.path, "debugParallelRun.dat")
            self.nameBase = name
            self.path = os.getcwd()

        self._assignStatements: list[_ras.AssignStatement] = []
        self._ddckFilePathWithComponentNames: list[_btd.DdckFilePathWithComponentName] = []

    def setDeckName(self, _name):
        self.nameBase = _name

    def setPath(self, path):
        self.path = path

    def defaultInputs(self):
        self.inputs = {}
        self.inputs["ignoreOnlinePlotter"] = False
        self.inputs["removePopUpWindow"] = False

        self.inputs["checkDeck"] = True
        self.inputs["reduceCpu"] = 0
        self.inputs["combineAllCases"] = True
        self.inputs["parseFileCreated"] = True
        self.inputs["HOME$"] = None
        self.inputs["trnsysVersion"] = "TRNSYS_EXE"
        self.inputs["trnsysExePath"] = "enviromentalVariable"
        self.inputs["copyBuildingData"] = False  # activate when Type 55 is used or change the path to the source
        self.inputs["addResultsFolder"] = False
        self.inputs["rerunFailedCases"] = False
        self.inputs["scaling"] = False
        self.inputs["doAutoUnitNumbering"] = True
        self.inputs["addAutomaticEnergyBalance"] = True
        self.inputs["generateUnitTypesUsed"] = True
        self.inputs["runCases"] = True
        self.inputs["runType"] = "runFromConfig"
        self.inputs["outputLevel"] = "INFO"

        self.overwriteForcedByUser = False

        self.variablesOutput = []

    def readFromFolder(self, pathRun):
        fileNames = [name for name in os.listdir(pathRun) if os.path.isdir(pathRun + "\\" + name)]

        returnNames = []
        for n in fileNames:
            if n[0] == ".":  # filfer folders such as ".gle" and so on
                pass
            else:
                returnNames.append(n)

        return returnNames

    def readCasesToRun(self, pathRun, nameFileWithCasesToRun):
        fileToRunWithPath = os.path.join(pathRun, nameFileWithCasesToRun)
        file = open(fileToRunWithPath, "r")
        lines = file.readlines()
        cases = []

        for line in lines:
            if line == "\n" or line[0] == "#":  # ignoring blank lines and lines starting with #
                pass
            else:
                cases.append(line[:-1])  # remove \n

        return cases

    def runFromNames(self, path, fileNames):
        tests = []
        self.cmds = []
        for i in range(len(fileNames)):
            tests.append(exeTrnsys.ExecuteTrnsys(path, fileNames[i]))
            tests[i].setTrnsysExePath(self.inputs["trnsysExePath"])
            tests[i].loadDeck(check=self.inputs["checkDeck"])

            tests[i].changeParameter(self.parameters)

            if self.inputs["ignoreOnlinePlotter"] == True:
                tests[i].ignoreOnlinePlotter()

            tests[i].deckTrnsys.writeDeck()

            tests[i].setRemovePopUpWindow(self.inputs["removePopUpWindow"])

            self.cmds.append(tests[i].getExecuteTrnsys(self.inputs, useDeckName=tests[i].nameDck))

        self.runParallel()

    def runConfig(self) -> _res.Result[None]:
        """
        Runs the cases defined in the config file

        Returns
        -------

        """

        if self.inputs["runType"] == "runFromCases":
            cases = self.readCasesToRun(self.inputs["pathWithCasesToRun"], self.inputs["fileWithCasesToRun"])
            self.runFromNames(self.inputs["pathWithCasesToRun"], cases)
        elif self.inputs["runType"] == "runFromFolder":
            cases = self.readFromFolder(self.inputs["pathFolderToRun"])
            self.runFromNames(self.inputs["pathFolderToRun"], cases)
        elif self.inputs["runType"] == "runFromConfig":
            if self.changeDDckFilesUsed == True:
                # It actually loops around the changed files and then execute the parameters variations for each
                # so the definitons of two weathers will run all variations in two cities
                nameBase = self.nameBase
                self.unscaledVariables = deepcopy(self.variablesOutput)
                for i in range(len(self.sourceFilesToChange)):
                    originalSourceFile = self.sourceFilesToChange[i]
                    sourceFile = self.sourceFilesToChange[i]
                    for j in range(len(self.sinkFilesToChange[i])):
                        sinkFile = self.sinkFilesToChange[i][j]
                        self.changeDDckFile(sourceFile, sinkFile)
                        if "scalingVariable" in self.inputs.keys() and "scalingReference" in self.inputs.keys():
                            if "changeScalingFile" in self.inputs.keys():
                                self.scaleVariables(
                                    self.inputs["scalingReference"],
                                    self.inputs["changeScalingFile"][0],
                                    self.inputs["changeScalingFile"][j + 1],
                                )
                            else:
                                self.scaleVariables(self.inputs["scalingReference"], originalSourceFile, sinkFile)

                        sourceFile = sinkFile  # for each case the listddck will be changed to the new one, so we need to compare with the updated string

                        if self.foldersForDDckVariationUsed == True:
                            addFolder = self.foldersForDDckVariation[j]
                            originalPath = self.path
                            self.path = os.path.join(self.path, addFolder)
                            if not os.path.isdir(self.path):
                                os.mkdir(self.path)
                        else:
                            self.nameBase = nameBase + "-" + os.path.split(sinkFile)[-1]

                        result = self.buildTrnsysDeck()

                        if _res.isError(result):
                            error = _res.error(result)
                            self.logger.error(error.message)
                            return error

                        self.createDecksFromVariant()

                        if self.foldersForDDckVariationUsed == True:
                            self.path = originalPath  # recall the original path, otherwise the next folder will be cerated inside the first
            else:
                result = self.buildTrnsysDeck()

                if _res.isError(result):
                    error = _res.error(result)
                    self.logger.error(error.message)
                    return error

                self.createDecksFromVariant()

    def createDecksFromVariant(self, fitParameters={}):
        variations = self.variablesOutput
        parameters = self.parameters
        parameters.update(fitParameters)

        myDeckGenerator = createDeck.CreateTrnsysDeck(self.path, self.nameBase, variations)

        myDeckGenerator.combineAllCases = self.inputs["combineAllCases"]

        successfulCases = []

        if "masterFile" in self.inputs:
            if os.path.isfile(self.inputs["masterFile"]):
                try:
                    masterDf = pd.read_csv(self.inputs["masterFile"], sep=";", index_col=0)
                except:
                    self.logger.error("Unable to read " + self.inputs["masterFile"])
                    self.logger.error("Variation dck files of %s won't be created" % self.nameBase)
                    return

                self.logger.info("Checking for successful runs in " + self.inputs["masterFile"])
                for index, row in masterDf.iterrows():
                    if row["outcome"] == "success":
                        successfulCases.append(index)
            else:
                self.logger.info("Master file does not exist, no runs will be excluded")

        # creates a list of decks with the appropriate name but nothing changed inside!!
        if self.variationsUsed or (self.changeDDckFilesUsed == True and self.foldersForDDckVariationUsed == False):
            if successfulCases:
                fileName = myDeckGenerator.generateDecks(successfulCases=successfulCases)
            else:
                fileName = myDeckGenerator.generateDecks()
        else:
            fileName = []
            fileName.append(self.nameBase)

        if myDeckGenerator.noVariationCreated and self.variation:
            self.logger.warning("No variation dck files created from " + self.nameBase)
            return

        tests = []

        variablePath = self.path

        for i in range(len(fileName)):
            self.logger.debug("name to run :%s" % fileName[i])

            # if useLocationStructure:
            # variablePath = os.path.join(path,location) #assign subfolder for path

            # Parameters changed by variation
            localCopyPar = dict.copy(parameters)  #

            if self.variationsUsed:
                myParameters = myDeckGenerator.getParameters(i)
                localCopyPar.update(myParameters)

            # We add to the global parameters that also need to be modified
            # If we assign like localCopyPar = parameters, then the parameters will change with localCopyPar !!
            # Otherwise we change the global parameter and some values of last variation will remain.

            tests.append(exeTrnsys.ExecuteTrnsys(variablePath, fileName[i]))

            tests[i].setTrnsysExePath(self.inputs["trnsysExePath"])

            tests[i].setRemovePopUpWindow(self.inputs["removePopUpWindow"])

            tests[i].moveFileFromSource()

            tests[i].loadDeck(useDeckOutputPath=True)

            tests[i].changeParameter(localCopyPar)

            tests[i].changeAssignStatementsBasedOnUnitVariables(self._assignStatements)

            if self.inputs["ignoreOnlinePlotter"] == True:
                tests[i].ignoreOnlinePlotter()

            tests[i].deckTrnsys.writeDeck()

            tests[i].cleanAndCreateResultsTempFolder()
            tests[i].moveFileFromSource()

            if self.inputs["runCases"] == True:
                self.cmds.append(tests[i].getExecuteTrnsys(self.inputs))

    def createLocationFolders(path, locations):
        for location in locations:
            if not os.path.exists(location):
                os.makedirs(location)
                print("created directory '") + path + location + "'"

    def moveResultsFolder(path, resultsFolder, destinationFolder):
        root_src_dir = os.path.join(path, resultsFolder)
        root_target_dir = os.path.join(path, destinationFolder)

        shutil.move(root_src_dir, root_target_dir)

    def buildTrnsysDeck(self) -> _res.Result[str]:
        """
        It builds a TRNSYS Deck from a listDdck with pathDdck using the BuildingTrnsysDeck Class.
        it reads the Deck list and writes a deck file. Afterwards it checks that the deck looks fine

        """
        #  I can create folders in another path to move them in the running folder and run them one by one
        #  path = "C:\Daten\OngoingProject\Ice-Ex\systemSimulations\\check\\"

        deckExplanation = []
        deckExplanation.append("! ** New deck built from list of ddcks. **\n")
        deck = _btd.BuildTrnsysDeck(
            self.path, self.nameBase, self._ddckFilePathWithComponentNames, self.ddckPlaceHolderValuesJsonPath
        )
        result = deck.readDeckList(
            self.pathConfig,
            doAutoUnitNumbering=self.inputs["doAutoUnitNumbering"],
            dictPaths=self.dictDdckPaths,
            replaceLineList=self.replaceLines,
        )

        if _res.isError(result):
            return _res.error(result)

        deck.overwriteForcedByUser = self.overwriteForcedByUser
        deck.writeDeck(addedLines=deckExplanation)
        self.overwriteForcedByUser = deck.overwriteForcedByUser

        result = deck.checkTrnsysDeck(deck.nameDeck, check=self.inputs["checkDeck"])
        if _res.isError(result):
            return _res.error(result)

        if self.inputs["generateUnitTypesUsed"] == True:
            deck.saveUnitTypeFile()

        if self.inputs["addAutomaticEnergyBalance"] == True:
            deck.addAutomaticEnergyBalancePrinters()
            deck.writeDeck()  # Deck rewritten with added printer

        deck.analyseDck()

        return deck.nameDeck

    def runParallel(self, writeLogFile=True):
        if writeLogFile:
            self.writeRunLogFile()

        if "masterFile" in self.inputs:
            runPar.runParallel(
                self.cmds,
                reduceCpu=int(self.inputs["reduceCpu"]),
                trackingFile=self.inputs["trackingFile"],
                masterFile=self.inputs["masterFile"],
            )
        elif "trackingFile" in self.inputs:
            runPar.runParallel(
                self.cmds, reduceCpu=int(self.inputs["reduceCpu"]), trackingFile=self.inputs["trackingFile"]
            )
        else:
            runPar.runParallel(self.cmds, reduceCpu=int(self.inputs["reduceCpu"]), outputFile=self.outputFileDebugRun)

    def writeRunLogFile(self):
        logfile = open(os.path.join(self.path, "runLogFile.config"), "w")
        username = os.getenv("username")
        logfile.write("# Run created by " + username + "\n")
        logfile.write("# Ddck repositories used:\n")
        try:
            import git

            found = True
        except ModuleNotFoundError:
            found = False

        for path in self.listDdckPaths:
            logfile.write("# " + path + "\n")
            logfile.write("# Revision Hash number: ")
            if found:
                try:
                    repo = git.Repo(path, search_parent_directories=True)
                    logfile.write(str(repo.head.object.hexsha) + "\n")
                except git.exc.InvalidGitRepositoryError:
                    logfile.write("None - Not in a Git repository \n")
            else:
                logfile.write("not found \n")
        logfile.write("\n# Config file used: \n\n")
        for line in self.lines:
            logfile.write(line + "\n")
        logfile.close()

    def readConfig(self, path, name, parseFileCreated=False):
        """
        It reads the config file used for running TRNSYS and loads the self.inputs dictionary.
        It also loads the readed lines into self.lines
        """
        tool = readConfig.ReadConfigTrnsys()

        self.lines = tool.readFile(path, name, self.inputs, parseFileCreated=parseFileCreated, controlDataType=False)
        try:
            self.logger = logging.getLogger("root")
        except:
            self.logger = log.getOrCreateCustomLogger("root", self.inputs["outputLevel"])
        if "pathBaseSimulations" in self.inputs:
            self.path = self.inputs["pathBaseSimulations"]
        if "pathToConnectionInfo" in self.inputs:
            self.ddckPlaceHolderValuesJsonPath = self.inputs["pathToConnectionInfo"]
        if self.inputs["addResultsFolder"] == False:
            pass
        else:
            self.path = os.path.join(self.path, self.inputs["addResultsFolder"])

            if not os.path.isdir(self.path):
                os.mkdir(self.path)

    def changeFile(self, source, end):
        """
        It uses the self-lines readed by readConfig and change the lines from source to end.
        This is used to change a ddck file readed for another. A typical example is the weather data file
        Parameters
        ----------
        source : str
            string to be replaced in the config file in the self.lines field
        end : str
            str to replace the source in the config file in the self.lines field

        Returns
        -------

        """

        found = False
        for i in range(len(self.lines)):
            lineFilter = self.lines[i]

            if lineFilter == source:
                self.lines[i] = end
                found = True

        if found == False:
            self.logger.warning("change File was not able to change %s by %s" % (source, end))

    def changeDDckFile(self, source, end):
        """
        It uses the  self.listDdck readed by readConfig and change the lines from source to end.
        This is used to change a ddck file readed for another. A typical example is the weather data file
        """
        found = False
        nCharacters = len(source)

        for i in range(len(self._ddckFilePathWithComponentNames)):
            ddckFilePathWithComponentName = self._ddckFilePathWithComponentNames[i]

            ddckFilePath = str(ddckFilePathWithComponentName.path)

            mySource = ddckFilePath[-nCharacters:]  # I read only the last characters with the same size as the end file
            if mySource == source:
                newDdckFilePath = ddckFilePath[0:-nCharacters] + end
                self.dictDdckPaths[newDdckFilePath] = self.dictDdckPaths[ddckFilePath]
                newDdckFilePathWithComponentName = _btd.DdckFilePathWithComponentName(
                    _pl.Path(newDdckFilePath), ddckFilePathWithComponentName.componentName
                )
                self._ddckFilePathWithComponentNames[i] = newDdckFilePathWithComponentName

                found = True

        if not found:
            self.logger.warning("change File was not able to change %s by %s" % (source, end))

    def copyConfigFile(self, configPath, configName):
        configFile = os.path.join(configPath, configName)
        dstPath = os.path.join(configPath, self.inputs["addResultsFolder"], configName)
        shutil.copyfile(configFile, dstPath)
        self.logger.debug("copied config file to: %s" % dstPath)

    def scaleVariables(self, reference, source, sink):
        """

        Parameters
        ----------
        reference : str
            File path of the reference results file. Has to point to a json-File with the pytrnsys resuls file format
        source : str
            Substring to be replaced in reference
        sink : str
            String to replace the substrings in the reference

        Returns
        -------

        """
        resultFile = reference.replace(source, sink)
        with open(resultFile) as f_in:
            resultsDict = json.load(f_in)

        exec("scalingVariable=" + self.inputs["scalingVariable"], globals(), resultsDict)
        loadDemand = resultsDict["scalingVariable"]

        try:
            exec("scalingElDemandVariable=" + self.inputs["scalingElDemandVariable"], globals(), resultsDict)
            loadElDemand = resultsDict["scalingElDemandVariable"]
        except:
            pass

        try:
            exec("scaleHP=" + self.inputs["scaleHP"], globals(), resultsDict)
            loadHPsize = resultsDict["scaleHP"]
        except:
            pass

        for j in range(len(self.variablesOutput)):
            for i in range(2, len(self.variablesOutput[j]), 1):
                if self.variablesOutput[j][1] == "sizeHpUsed":
                    self.variablesOutput[j][i] = (
                        str(round(self.unscaledVariables[j][i], 3)) + "*" + str(round(loadHPsize, 3))
                    )
                elif self.variablesOutput[j][1] == "AreaPvRoof":
                    self.variablesOutput[j][i] = (
                        str(round(self.unscaledVariables[j][i], 3)) + "*" + str(round(loadElDemand, 3))
                    )
                else:
                    self.variablesOutput[j][i] = (
                        str(round(self.unscaledVariables[j][i], 3)) + "*" + str(round(loadDemand, 3))
                    )
