# pylint: skip-file
# type: ignore

import io as _io
import json as _json
import logging
import os
import pathlib as _pl
import re as _re
import tkinter as tk
import typing as _tp
from tkinter import messagebox as tkMessageBox

import pytrnsys.ddck.replaceVariables as _replace
import pytrnsys.pdata.processFiles as spfUtils
import pytrnsys.trnsys_util.deckTrnsys as deck
import pytrnsys.trnsys_util.deckUtils as deckUtils
import pytrnsys.trnsys_util.trnsysComponent as trnsysComponent
import pytrnsys.utils.result as _res

logger = logging.getLogger("root")
# stop propagting to root logger
logger.propagate = False
"""
This class uses a list of ddck files to built a complete TRNSYS deck file
"""


class BuildTrnsysDeck:
    def __init__(self, _pathDeck, _nameDeck, _nameList, ddckPlaceHolderValuesJsonPath):

        self.pathDeck = _pathDeck
        self.nameDeck = self.pathDeck + "\%s.dck" % _nameDeck

        self._ddckPlaceHolderValuesJsonPath = _pl.Path(
            ddckPlaceHolderValuesJsonPath) if ddckPlaceHolderValuesJsonPath else None

        self.oneSheetList = []
        self.nameList = _nameList
        self.deckText = []

        self.overwriteForcedByUser = False
        self.abortedByUser = False
        self.extOneSheetDeck = "ddck"

        self.skypChar = ["*", "!", "      \n"]  # ['*'] #This will eliminate the lines starting with skypChar
        self.eliminateComments = False

        self.replaceAutomaticUnits = False

        self.existingDckUnchecked = True
        self.dckAlreadyExists = True

    def loadDeck(self, _path, _name) -> _res.Result[_tp.Tuple[str, str, str]]:
        ddckFilePath = _pl.Path(_path) / f"{_name}.{self.extOneSheetDeck}"

        result = self._replacePlaceholdersAndGetContent(ddckFilePath)
        if _res.isError(result):
            return _res.error(result)
        ddckContent = _res.value(result)

        # Historically, the lines we're read in from a file directly using `readlines`. To reproduce the same behaviour
        # regarding new line characters, we use `StringIO.readlines` here.
        stream = _io.StringIO(ddckContent)
        lines = stream.readlines()

        replaceChar = None

        self.linesChanged = spfUtils.purgueLines(lines, self.skypChar, replaceChar, removeBlankLines=True)

        if self.eliminateComments:
            self.linesChanged = spfUtils.purgueComments(self.linesChanged, ["!"])

        return lines[0:3]  # only returns the caption with the info of the file

    def _replacePlaceholdersAndGetContent(self, ddckFilePath: _pl.Path) -> _res.Result[str]:
        componentName = ddckFilePath.parent.name

        if self._ddckPlaceHolderValuesJsonPath:

            if not self._ddckPlaceHolderValuesJsonPath.is_file():
                return _res.Error(
                    f"The ddck placeholder values file at {self._ddckPlaceHolderValuesJsonPath} does not exist.")

            placeholderValues = _json.loads(self._ddckPlaceHolderValuesJsonPath.read_text())

            if componentName in placeholderValues:
                namesByPort = placeholderValues[componentName]
                result = _replace.replaceComputedVariablesWithNames(ddckFilePath, namesByPort)

                if _res.isError(result):
                    return _res.error(result)

                return _res.value(result)

        return _replace.replaceComputedVariablesWithDefaults(ddckFilePath)

    def readDeckList(
            self, pathConfig, doAutoUnitNumbering=False, dictPaths=False, replaceLineList=[]
    ) -> _res.Result[None]:
        """

        Parameters
        ----------
        doAutoUnitNumbering : bool
            use the automatic renumbering of trnsys units, optional, default: False
        dictPaths: dict
            dictionary with keys equal to the old ddck path and values equal to the ones that should replace it


        Returns
        -------

        """

        self.unitId = 9  # I start at 10 becasue it seems that UNIT 4 and 6 can't be used?

        self.dependencies = {}
        self.definitions = {}
        for i in range(len(self.nameList)):

            split = self.nameList[i].split("\\")

            if self.nameList[i][1] == ":":  # absolute path

                nameList = split[-1]
                pathVec = split[:-1]
                pathList = ""
                for j in range(len(pathVec)):
                    if j == 0:
                        pathList = pathVec[j]
                    else:
                        pathList = pathList + "\\" + pathVec[j]
            else:

                nameList = split[-1]
                pathVec = split[:-1]
                pathList = pathConfig
                for j in range(len(pathVec)):
                    pathList = pathList + "\\" + pathVec[j]
                dictPaths[self.nameList[i]] = os.path.join(pathConfig, dictPaths[self.nameList[i]])

            result = self.loadDeck(pathList, nameList)

            if _res.isError(result):
                return _res.error(result)

            firstThreeLines = _res.value(result)

            ddck = trnsysComponent.TrnsysComponent(pathList, nameList)
            definedVariables, requiredVariables = ddck.getVariables()
            if (
                    "printer" not in nameList
                    and "Printer" not in nameList
                    and "Control" not in nameList
                    and "control" not in nameList
                    and "BigIceCoolingTwoStorages" not in nameList
            ):
                self.dependencies[nameList] = requiredVariables - definedVariables
                self.definitions[nameList] = definedVariables

            self.replaceLines(replaceLineList)
            self.linesChanged = deckUtils.changeAssignPath(
                self.linesChanged, "path$", dictPaths[os.path.join(self.nameList[i])]
            )
            addedLines = firstThreeLines + self.linesChanged

            caption = (
                    "**********************************************************************\n** %s.ddck from %s \n**********************************************************************\n"
                    % (nameList, pathList)
            )

            if doAutoUnitNumbering:
                (unit, types, fileAssign, fileAssignUnit) = deckUtils.readAllTypes(addedLines)
                logger.debug("Replacemenet of Units of file:%s" % nameList)
                self.unitId = deckUtils.replaceAllUnits(addedLines, self.unitId, unit, fileAssignUnit, fileAssign)

                unitModifiedLines = [line.replace("£", "") for line in addedLines]
                addedLines = unitModifiedLines

            stream = _io.StringIO(caption)
            lines = stream.readlines()
            self.deckText.extend(lines)
            self.deckText = self.deckText + addedLines

        self.logger = logging.getLogger("root")
        # stop propagting to root logger
        self.logger.propagate = False
        self.logger.debug("Replacemenet of Units done")

    def createDependencyGraph(self):
        e = Graph("ER", filename="er.gv", node_attr={"color": "lightblue2", "style": "filled"})
        e.attr("node", shape="box")
        variables_global = ["cpwat", "rhowat", "nix", "tamb", "dtsim", "cpbri", "rhobri", "pi", "stop", "start", "zero"]
        for (key, value) in self.dependencies.items():
            e.node(key)

        for (key, value) in self.dependencies.items():
            for (keyDef, valueDef) in self.definitions.items():
                edgelLabel = ""
                for dependency in value:
                    if dependency in valueDef and dependency not in variables_global:
                        edgelLabel += dependency + "\n"
                if edgelLabel != "":
                    e.edge(key, keyDef, label=edgelLabel, style="bold")

        e.attr(label=r"\n\nEntity Relation Diagram\ndrawn by NEATO")
        e.attr(fontsize="1")

        e.render("er.gv", view=False)

    def writeDeck(self, addedLines=None):
        """
        Writes the deck stored in self.deckText in the file self.nameDeck

        Parameters
        ----------
        addedLines : str
            lines to be added at the beginning of the file

        Returns
        -------

        """
        tempName = "%s" % self.nameDeck

        if self.existingDckUnchecked:
            self.dckAlreadyExists = os.path.isfile(tempName)
            self.existingDckUnchecked = False

        ok = True

        if self.dckAlreadyExists and self.overwriteForcedByUser is False:

            window = tk.Tk()
            window.geometry("2x2+" + str(window.winfo_screenwidth()) + "+" + str(window.winfo_screenheight()))
            ok = tkMessageBox.askokcancel(
                title="Processing Trnsys",
                message="Do you want override %s ?\n If parallel simulations most likely accepting this will ovrewrite all the rest too. Think of it twice !! "
                        % tempName,
            )
            window.destroy()

            if ok:
                self.overwriteForcedByUser = True

        if ok:
            tempFile = open(tempName, "w", encoding='windows-1252')
            if addedLines != None:
                text = addedLines + self.deckText
            else:
                text = self.deckText
            tempFile.writelines(text)
            tempFile.close()
        else:
            logger.warning("dck export cancelled by user")
            self.abortedByUser = True

    def readTrnsyDeck(self, useDeckName=False):
        """
        It reads the deck generated using the DeckTrnsys Class and saves it into self.myDeck class DeckTrnsys.
        """
        nameDeck = self.nameDeck.split(".")[0]
        nameDeck = nameDeck.split("\\")[-1]
        self.myDeck = deck.DeckTrnsys(self.pathDeck, nameDeck)

        self.linesDeckReaded = self.myDeck.loadDeck(
            useDeckName=useDeckName, eraseBeginComment=False, eliminateComments=False
        )

    def checkTrnsysDeck(self, nameDck, check=True) -> _res.Result[None]:
        lines = deckUtils.loadDeck(nameDck, eraseBeginComment=True, eliminateComments=True)
        if check:
            result = deckUtils.checkEquationsAndConstants(lines, self.nameDeck)
            if _res.isError(result):
                return _res.error(result)

        self.linesDeckReaded = lines

    def saveUnitTypeFile(self):

        (self.TrnsysUnits, self.TrnsysTypes, self.filesUsedInDdck, self.filesUnitUsedInDdck) = deckUtils.readAllTypes(
            self.deckText, sort=False
        )

        self.writeTrnsysTypesUsed("UnitsType.info")

    def writeTrnsysTypesUsed(self, name):

        lines = "UNIT\tTYPE\tName\n"

        for i in range(len(self.TrnsysTypes)):
            line = "%4d\t%4d\t%s\n" % (
                self.TrnsysUnits[i],
                self.TrnsysTypes[i],
                deckUtils.getTypeName(self.TrnsysTypes[i]),
            )
            lines = lines + line

        for i in range(len(self.filesUsedInDdck)):
            nameUnitFile = deckUtils.getDataFromDeck(self.linesDeckReaded, self.filesUnitUsedInDdck[i])

            if nameUnitFile == None:
                line = "%s\tNone\t%s\n" % (self.filesUnitUsedInDdck[i], self.filesUsedInDdck[i])
            else:
                line = "%s\t%s\t%s\n" % (self.filesUnitUsedInDdck[i], nameUnitFile, self.filesUsedInDdck[i])

            lines = lines + line

        nameFile = os.path.join(self.pathDeck, name)

        logger.debug("Type file %s created" % nameFile)
        outfile = open(nameFile, "w")
        outfile.writelines(lines)

    def automaticEnegyBalanceStaff(self):
        """
        It reads and generates a onthly printer for energy system calculations in an automatic way
        It needs the data read by checkTrnsysDeck
        """
        eBalance = deckUtils.readEnergyBalanceVariablesFromDeck(self.deckText)
        unitId = self.unitId + 1

        lines = deckUtils.addEnergyBalanceMonthlyPrinter(unitId, eBalance)
        self.deckText = self.deckText[:-4] + lines + self.deckText[-4:]

        unitId = self.unitId + 2
        lines = deckUtils.addEnergyBalanceHourlyPrinter(unitId, eBalance)
        self.deckText = self.deckText[:-4] + lines + self.deckText[-4:]

    def replaceLines(self, replaceList):
        """
        Replaces a deck lines with different lines
        Parameters
        ----------
        replaceList: list of tuples with two strings (oldLine, newLine)

        Returns
        -------

        """
        for tuple in replaceList:
            oldLine = tuple[0]
            newLine = tuple[1]
            for index, line in enumerate(self.linesChanged):
                if oldLine in line:
                    self.linesChanged[index] = newLine + "\n"

    def analyseDck(self):
        maxLineWidth = 0
        maxNumberOfConstantsInABlock = 0

        constantsToCheck = ["UNIT", "EQUATIONS", "CONSTANTS", "PARAMETERS", "INPUTS"]
        numOfTrnsysConstants = {}

        for index, line in enumerate(self.deckText):
            maxLineWidth = max(maxLineWidth, len(line))
            if maxLineWidth > 1000:
                self.logger.warning(f"Line {index + 1} has {maxLineWidth} characters which exceeds the limit.")
                maxLineWidth = 0

            for constant in constantsToCheck:
                match = _re.search(fr"^\b{constant}\s*\d+\b", line, _re.MULTILINE)
                if match:
                    if constant == "UNIT":
                        numOfTrnsysConstants[constant] = numOfTrnsysConstants.get(constant, 0) + 1
                    elif constant in ("CONSTANTS", "EQUATIONS"):
                        split = match.group().split()
                        numOfTrnsysConstants["EQUATIONS"] = numOfTrnsysConstants.get("EQUATIONS", 0) + int(split[1])
                        maxNumberOfConstantsInABlock = max(maxNumberOfConstantsInABlock, int(split[1]))
                    else:
                        split = match.group().split()
                        numOfTrnsysConstants[constant] = numOfTrnsysConstants.get(constant, 0) + int(split[1])
                        maxNumberOfConstantsInABlock = max(maxNumberOfConstantsInABlock, int(split[1]))
                    break

        for constant, number in numOfTrnsysConstants.items():
            if (constant == "UNIT" and number > 1000) or (constant == "EQUATIONS" and number > 500) or (
                    constant == "PARAMETERS" and number > 2000) or (constant == "INPUTS" and number > 750):
                self.logger.warning(f"There are {number} of {constant} which exceeds the limit")

        if maxNumberOfConstantsInABlock > 250:
            self.logger.warning(
                f"There are {maxNumberOfConstantsInABlock} of components in one block which exceeds the limit")
