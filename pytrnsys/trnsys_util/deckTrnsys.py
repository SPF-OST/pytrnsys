# pylint: skip-file
# type: ignore
import io
import logging
import os
import re
import shutil
import typing as tp

import pytrnsys.trnsys_util.deckUtils as deckUtils
import pytrnsys.trnsys_util.replaceAssignStatements as _ras

logger = logging.getLogger("root")
# stop propagting to root logger
logger.propagate = False


class DeckTrnsys:
    """
    This class gives the functionality to dck files:
    -to set a new path for the deck
    -to comment all online plotters
    -change the name of the deck
    -change the assign path
    """

    def __init__(self, _path, _name):
        self.extensionDeck = "dck"

        self.setPathAndNames(_path, _name)

        self.linesDeck = []
        self.cleanMode = False
        self.useAbsoluteTempPath = False  # actually False does not work since trnsys does not work with  ./temp/whatever. Corrected False works since temp/whatever works !!

        # True is not working becasue it looks for files in the D:\MyPrograms\Trnsys17 as local path
        self.eliminateComments = False
        try:
            self.myCommonTrnsysFolder = os.getenv("TRNSYS_DATA_FOLDER") + "\\"
        except:
            self.myCommonTrnsysFolder = None

            logger.debug("TRNSYS_DATA_FOLDER not defined as an enviromental variable.")

        self.packageNameTrnsysFiles = "None"

    def setPackageNameTrnsysFiles(self, name):
        self.packageNameTrnsysFiles = name

    def setPathAndNames(self, _path, _name):
        self.fileName = _name  # _name.split('.')[0]
        self.path = _path
        self.nameDck = self.path + r"\%s.%s" % (_name, self.extensionDeck)
        self.pathOutput = self.path + r"\%s" % self.fileName
        self.titleOfLatex = "%s" % self.fileName
        self.useRelativePath = False

        if self.useRelativePath == False:
            self.filesOutputPath = self.pathOutput

        self.nameDckPathOutput = self.pathOutput + r"\%s.%s" % (_name, self.extensionDeck)

    def setEliminateComments(self, comment):
        self.eliminateComments = comment

    def changeNameOfDeck(self, newName):
        self.nameDck = self.path + r"\%s.%s" % (newName, self.extensionDeck)
        self.pathOutput = self.path + r"\%s" % newName
        self.titleOfLatex = "%s" % newName
        self.tempFolderEnd = "%s\\temp" % self.pathOutput

        if self.useRelativePath == False:
            self.filesOutputPath = self.pathOutput

    def createDeckBackUp(self):
        nameDeckBck = "%s-bck" % self.nameDck
        shutil.copy(self.nameDck, nameDeckBck)

    def loadDeck(self, useDeckName=False, eraseBeginComment=True, eliminateComments=True, useDeckOutputPath=False):
        r"""
        It reads the deck  removing files starting with \*\*\*.

        Return
        ----------
        linesDeck : list of str
            list containing the lines of the deck from the read deck.
        """

        if useDeckName == False:
            if useDeckOutputPath == True:
                nameDck = self.nameDckPathOutput
            else:
                nameDck = self.nameDck

            logger.debug("DECK TRNSYS::LOAD DECK nameDeck:%s" % (self.nameDck))

        else:
            logger.debug("DECK TRNSYS::LOAD DECK nameDeck:%s USEDECKNAME:%s" % (self.nameDck, useDeckName))

            # self.nameDck = useDeckName
            # self.nameDckPathOutput = useDeckName
            nameDck = useDeckName
        lines = deckUtils.loadDeck(nameDck, eraseBeginComment=eraseBeginComment, eliminateComments=eliminateComments)

        self.linesDeck = lines

        return lines

    def writeDeck(self):
        tempName = "%s" % self.nameDck
        print("tempName:%s" % tempName)
        tempFile = open(tempName, "w")
        tempFile.writelines(self.linesDeck)
        tempFile.close()

    def changeAssignPath(self, inputsDict=False):
        """
        This file only changes the assign path of those that start with HOME$, so we use for those the absolute path
        It assumess that self.linesDeck is loaded.
        """
        for i in range(len(self.linesDeck)):
            splitBlank = self.linesDeck[i].split()

            try:
                if splitBlank[0] == "ASSIGN":
                    splitPath = splitBlank[1].split("\\")
                    lineChanged = False
                    for j in range(len(splitPath)):
                        if splitPath[j] in inputsDict.keys():
                            name = os.path.join(
                                *splitPath[j + 1 :]
                            )  # * sot joining the vector, j+1 becasue we dont need spfTrnsysFiles,already in the path my commonTrnsysFolder
                            if inputsDict:
                                logger.warning(
                                    "Using "
                                    + str(splitPath[j])
                                    + "specified in the config file (deprecated). Root of the ddck library should be indicated as PATH$"
                                )

                                if len(splitBlank) > 2:
                                    lineChanged = 'ASSIGN "%s" %s \n' % (
                                        os.path.join(inputsDict[splitPath[j]], name),
                                        splitBlank[2],
                                    )
                                else:
                                    lineChanged = 'ASSIGN "%s" \n' % (os.path.join(inputsDict[splitPath[j]], name))
                            else:
                                logger.warning(
                                    "Common Trnsys Folder from config file not used. Use TRNSYS_DATA_FOLDER enviroment variable instead (deprecated)"
                                )
                                if len(splitBlank) > 2:
                                    lineChanged = 'ASSIGN "%s" %s \n' % (
                                        os.path.join(inputsDict[splitPath[j]], name),
                                        splitBlank[2],
                                    )
                                else:
                                    lineChanged = 'ASSIGN "%s" \n' % (os.path.join(inputsDict[splitPath[j]], name))
                    if lineChanged != False:
                        self.linesDeck[i] = lineChanged
            except:
                pass

    def ignoreOnlinePlotter(self):
        jBegin = 0
        found = False

        plotterFound = 0

        for i in range(len(self.linesDeck)):
            splitBlank = self.linesDeck[i].split()

            if found == True:
                try:
                    if splitBlank[0].replace(" ", "").lower() == "LABELS".lower():
                        nLabelString = splitBlank[1].replace(" ", "")
                        nLabel = int(nLabelString)

                        jEnd = i + nLabel

                        for j in range(jBegin, jEnd + 1, 1):
                            self.linesDeck[j] = "**IGNORE ONLINE PLOTTER - 1" + self.linesDeck[j]

                        found = False
                        i = jEnd

                except:
                    self.linesDeck[i] = "**IGNORE ONLINE PLOTTER 3 - \n" + self.linesDeck[i]

            else:  # First it looks for the unit number corresponding to the TYPE and comments util it enters into the LABEL (try section above)
                found = False
                try:
                    unit = splitBlank[0].replace(" ", "")
                    types = splitBlank[2].replace(" ", "")
                    ntype = splitBlank[3].replace(" ", "")

                    if unit.lower() == "unit".lower() and types.lower() == "Type".lower() and ntype == "65":
                        jBegin = i
                        found = True
                        self.linesDeck[i] = "** IGNORE ONLINE PLOTTER - " + self.linesDeck[i]
                        plotterFound = plotterFound + 1

                except:
                    pass

        return

    def getVariables(self):
        self.eliminateComments = (
            True  # BE CAREFUL, THIS CAN CHANGE  [30,1] by [301] so it does not WORK !!!! DC: Is this updated?
        )
        self.loadDeck(self.nameDck)

        self.variablesNames = []
        self.variablesResults = []

        for i in range(len(self.linesDeck)):
            splitEquality = self.linesDeck[i].split("=")
            try:
                myName = splitEquality[0].replace(" ", "")
                myValue = splitEquality[1].replace(" ", "")

                self.variablesNames.append("%s" % myName)
                self.variablesResults.append("%s" % myValue)

            except:
                pass

        nameFile = self.pathOutput + "\\namesVariables.info"

        lines = ""
        for name in self.variablesNames:
            count = 0
            resFound = ""
            for res in self.variablesResults:
                n = res.count(name)
                count = count + n
                if n >= 1:
                    resFound = resFound + "\t%s" % res
            #           print "name:%s count:%d" % (name,count)

            line = name + " count=%d\n" % count
            lines = lines + line
            if count >= 1:
                line = "%s" % resFound
                lines = lines + line

        outfile = open(nameFile, "w")
        outfile.writelines(lines)
        outfile.close()

    def changeParameter(self, _parameters):
        logger.debug("Change Parameters deckTrnsys Class")

        if _parameters != None:
            self.parameters = _parameters

            for i in range(len(self.linesDeck)):
                splitEquality = self.linesDeck[i].split("=")
                splitBlank = self.linesDeck[i].split()

                try:
                    if splitBlank[0] == "ASSIGN":
                        fileNameWithoutCommas = splitBlank[1].replace('"', "")

                        compressorDataSplit = fileNameWithoutCommas.split("Compressor\\")

                        if len(compressorDataSplit) > 1:
                            myFileInNewPath = self.HOMEPath + "Compressor\\" + "%s" % compressorDataSplit[1]
                            self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])

                            print("Compressor data changed :%s " % self.linesDeck[i])

                        nameSplited = fileNameWithoutCommas.split("temp\\")

                        try:
                            if self.useAbsoluteTempPath:
                                myFileInNewPath = self.filesOutputPath + "\\temp\\" + nameSplited[1]
                                self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])
                            else:
                                myFileInNewPath = "temp\\" + nameSplited[1]
                                self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])

                        except:
                            if nameSplited[0] == "Temp_zone.BAL" or nameSplited[0] == "Energy_zone.BAL":
                                myFileInNewPath = self.filesOutputPath + "\\" + nameSplited[0]
                                self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])

                except:
                    pass

                try:
                    myName = splitEquality[0].replace(" ", "")

                    for key in self.parameters.keys():
                        if key.lower() == myName.lower():  # avoid case-sensitive
                            #
                            myNewLine = "%s=%s ! value changed from original by executeTrnsys.py\n" % (
                                key,
                                self.parameters[key],
                            )
                            logger.debug("NEW LINE %s" % myNewLine)

                            self.linesDeck[i] = myNewLine

                except:
                    pass

            logger.debug("variation deck file at %s" % self.nameDck)

    def changeAssignStatementsBasedOnUnitVariables(
        self, newAssignStatements: tp.Sequence[_ras.AssignStatement]
    ) -> None:
        originalDeckContent = "".join(self.linesDeck)
        updatedDeckContent = _ras.replaceAssignStatementsBasedOnUnitVariables(
            originalDeckContent, newAssignStatements, logger
        )

        newLines = self._readlines(updatedDeckContent)
        self.linesDeck = newLines

    @staticmethod
    def _readlines(string: str) -> tp.Sequence[str]:
        """Like `io.IOBase.readlines` but for strings."""
        stringIO = io.StringIO(string)
        lines = stringIO.readlines()
        return lines

    def getTypeFromUnit(self, myUnit):
        return deckUtils.getTypeFromUnit(myUnit, self.linesDeck)

    def getDataFromDeck(self, myName, typeValue="double"):
        return deckUtils.getDataFromDeck(self.linesDeck, myName, typeValue=typeValue)

    def getAllDataFromDeck(self):
        linesDeck = self.linesDeck

        self.deckVariables = {}
        for line in linesDeck:
            if "=" in line:
                line = line.strip("\n")
                splitEquality = line.split("=")
                name = splitEquality[0].replace(" ", "")
                value = splitEquality[1].replace(" ", "").replace("^", "**")
                try:
                    if "[" not in value:
                        self.deckVariables[name] = eval(value, self.deckVariables)
                        parts = re.split(r"[*/+-]", value.replace(r"(", "").replace(r")", ""))
                        if len(parts) == 2 and len(re.split(r"[*]", value)) == 2:
                            self.deckVariables[name + "_factor"] = float(parts[0])
                    else:
                        float(value)
                except:
                    if "[" not in line:
                        parts = re.split(r"[*/+-]", value.replace(r"(", "").replace(r")", ""))
                        for part1 in parts:
                            reValue = self.getDataFromDeckRecursively(part1, linesDeck)
                            if reValue is not None:
                                self.deckVariables[part1] = reValue
                        try:
                            finalValue = eval(value, self.deckVariables)
                            self.deckVariables[name] = float(finalValue)
                        except:
                            pass
        return self.deckVariables

    def getDataFromDeckRecursively(self, part, linesDeck):
        for line in linesDeck:
            if "=" in line:
                line = line.strip("\n")
                splitEquality = line.split("=")
                name = splitEquality[0].replace(" ", "")
                value = splitEquality[1].replace(" ", "")
                if name.lower() == part.lower():
                    try:
                        if "[" not in value:
                            self.deckVariables[name] = eval(value, self.deckVariables)
                        else:
                            float(value)
                    except:
                        if "[" not in line:
                            parts = re.split(r"[*/+-]", value.replace(r"(", "").replace(r")", ""))
                            for part1 in parts:
                                reValue = self.getDataFromDeckRecursively(part1, linesDeck)
                                if reValue is not None:
                                    self.deckVariables[part1] = reValue
                            try:
                                finalValue = eval(value, self.deckVariables)
                                dict = {}
                                dict[name] = float(finalValue)
                                return dict[name]
                            except:
                                return None
                                pass
                        else:
                            return None
