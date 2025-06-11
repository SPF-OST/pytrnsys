# pylint: skip-file
# type: ignore

import dataclasses as _dc
import logging
import os
import pathlib as _pl
import shutil
import shutil as _su
import typing as tp

import pytrnsys.rsim.command as _cmd
import pytrnsys.trnsys_util.deckTrnsys as deckTrnsys
import pytrnsys.trnsys_util.deckUtils as deckUtils
import pytrnsys.trnsys_util.replaceAssignStatements as _ras

logger = logging.getLogger("root")
# stop propagting to root logger
logger.propagate = False


class ExecuteTrnsys:
    """
    This class uses DeckTrnsys class to read a dck file.
    It also gives functionality by means of DeckTrnsys
    -to set a new path for the deck
    -to comment all online plotters
    -change the name of the deck
    -change the assign path
    """

    def __init__(self, _path, _name):
        self.fileName = _name  # _name.split('.')[0]
        self.path = _path
        self.nameDck = os.path.join(self.path, _name + ".dck")
        self.linesChanged = ""
        self.titleOfLatex = "%s" % self.fileName

        self.trnsysVersion = "TRNSYS_EXE"
        self.trnsysExePath = "enviromentalVariable"

        self.pathOutput = os.path.join(self.path, self.fileName)

        if not os.path.exists(self.pathOutput):
            # print self.pathOutput
            os.makedirs(self.pathOutput)

        self.tempFolder = os.path.join(self.path, "temp")
        self.tempFolderEnd = os.path.join(self.pathOutput, "temp")

        self.nameDckPathOutput = os.path.join(self.pathOutput, _name + ".dck")

        self.cleanMode = True

        self.foldersForRunning = []
        self.filesForRunning = []

        self.filesOutputPath = "."
        # True is not working becasue it looks for files in the D:\MyPrograms\Trnsys17 as local path
        self.useRelativePath = False

        self.removePopUpWindow = False

        if self.useRelativePath == False:
            self.filesOutputPath = self.pathOutput

    def setRemovePopUpWindow(self, removePopUpWindow):
        self.removePopUpWindow = removePopUpWindow

    def setTrnsysExePath(self, path):
        self.trnsysExePath = path

    def redefinePath(self, path, _name):
        self.pathOutput = self.path

        if not os.path.exists(self.pathOutput):
            # print self.pathOutput
            os.makedirs(self.pathOutput)

        self.tempFolder = os.path.join(self.path, "temp")
        self.tempFolderEnd = os.path.join(self.pathOutput, "temp")
        self.nameDckPathOutput = os.path.join(self.pathOutput, _name + ".dck")

    def setPackageNameTrnsysFiles(self, name):
        self.deckTrnsys.setPackageNameTrnsysFiles(name)

    def ignoreOnlinePlotter(self, useOutputDeck=False):
        nameDck = self.deckTrnsys.nameDck
        nameDckPathOutput = self.deckTrnsys.nameDckPathOutput

        if useOutputDeck == True:
            self.deckTrnsys.nameDck = nameDckPathOutput

        self.deckTrnsys.ignoreOnlinePlotter()

        self.deckTrnsys.nameDck = nameDck

    def changeNameOfDeck(self, newName):
        self.nameDck = os.path.join(self.path, newName + ".dck")
        self.pathOutput = os.path.join(self.path, newName)
        self.titleOfLatex = "%s" % newName
        self.tempFolderEnd = os.path.join(self.pathOutput, "temp")
        self.nameDckPathOutput = os.path.join(self.pathOutput, newName + ".dck")

        self.deckTrnsys.nameDck = self.nameDck
        self.deckTrnsys.pathOutput = self.pathOutput
        self.deckTrnsys.tempFolderEnd = self.tempFolderEnd
        self.deckTrnsys.nameDckPathOutput = self.nameDckPathOutput

        if self.useRelativePath == False:
            self.filesOutputPath = self.pathOutput

    def createDeckBackUp(self):
        nameDeckBck = "%s-bck" % self.nameDck
        shutil.copy(self.nameDck, nameDeckBck)

    def loadDeck(
        self,
        useDeckName=False,
        check=False,
        eliminateComments=False,
        useDeckOutputPath=False,
    ):
        if useDeckName == False:
            nameDck = self.fileName  # self.nameDckPathOutput
        else:
            nameDck = useDeckName

        self.deckTrnsys = deckTrnsys.DeckTrnsys(self.path, nameDck)

        lines = self.deckTrnsys.loadDeck(
            eraseBeginComment=False,
            eliminateComments=False,
            useDeckOutputPath=useDeckOutputPath,
        )

        if check == True:
            deckUtils.checkEquationsAndConstants(lines, nameDck)

    def changeParameter(self, _parameters):
        self.deckTrnsys.changeParameter(_parameters)

        # with this function we obtain some data from the deck file.

    def changeAssignStatementsBasedOnUnitVariables(
        self, newAssignStatements: tp.Sequence[_ras.AssignStatement]
    ) -> None:
        self.deckTrnsys.changeAssignStatementsBasedOnUnitVariables(newAssignStatements)

    def getDataFromDeck(self, myName):
        return self.deckTrnsys.getDataFromDeck(myName)

    def cleanFilesForRunning(self):
        for folder in self.foldersForRunning:
            folderWithPath = os.path.join(self.pathOutput, folder)
            shutil.rmtree(folderWithPath)

        for files in self.filesForRunning:
            fileWithPath = os.path.join(self.pathOutput, files)
            shutil.rmtree(fileWithPath)

    def moveFileFromSource(self):
        name = "%s.dck" % self.fileName

        fileSource = os.path.join(self.path, name)
        fileEnd = os.path.join(self.pathOutput, name)

        shutil.move(fileSource, fileEnd)

    def setTrnsysVersion(self, version):
        self.trnsysVersion = version

    def getExecuteTrnsys(self, inputDict, useDeckName=False) -> _cmd.Command:
        dckFilePath = _pl.Path(useDeckName) if useDeckName else self.nameDckPathOutput

        ignoreOnlinePlotter = inputDict["ignoreOnlinePlotter"]
        autoCloseOnlinePlotter = inputDict["autoCloseOnlinePlotter"]

        trnsysFlags = self._getTrnsysFlags(ignoreOnlinePlotter, self.removePopUpWindow, autoCloseOnlinePlotter)

        command = _cmd.Command(self.trnsysExePath, dckFilePath, trnsysFlags)

        return command

    @classmethod
    def _getTrnsysFlags(
        cls, *, ignoreOnlinePlotter: bool, removePopupWindow: bool, autoCloseOnlinePlotter: bool
    ) -> str:
        if ignoreOnlinePlotter and removePopupWindow:
            return "/H"
        if ignoreOnlinePlotter and not removePopupWindow:
            return "/N"
        if not ignoreOnlinePlotter and autoCloseOnlinePlotter:
            return "/N"

        return ""

    def cleanAndCreateResultsTempFolder(self):
        try:
            logger.debug("removing temp : %s " % self.tempFolderEnd)
            shutil.rmtree(self.tempFolderEnd)
            os.makedirs(self.tempFolderEnd)

        except:
            logger.debug("creating temp : %s " % self.tempFolderEnd)
            os.makedirs(self.tempFolderEnd)
            pass

    def movingAuxFiles(self):
        nameSource = self.path + "\\%s.log" % self.fileName
        nameOut = self.pathOutput + "\\%s.log" % self.fileName

        shutil.move(nameSource, nameOut)

        nameSource = self.path + "\\%s.lst" % self.fileName
        nameOut = self.pathOutput + "\\%s.lst" % self.fileName

        shutil.move(nameSource, nameOut)

        nameSource = self.path + "\\%s.dck" % self.fileName
        nameOut = self.pathOutput + "\\%s.dck" % self.fileName

        shutil.copy(nameSource, nameOut)

    def clearOrCreateVariationDataFolder(self) -> None:
        dataDirPath = self._getDataDirPath()

        assert not dataDirPath.is_file()

        if dataDirPath.is_dir():
            _su.rmtree(dataDirPath)

        dataDirPath.mkdir()

    def copyPathToVariationDataFolder(self, sourcePath: _pl.Path, targetPath: _pl.Path) -> None:
        if targetPath.is_absolute():
            raise ValueError("Target path must be relative.", targetPath)

        self._copySourceToTargetAtDataDirPath(sourcePath, targetPath)

    def _copySourceToTargetAtDataDirPath(self, sourcePath: _pl.Path, targetPath: _pl.Path) -> None:
        if not sourcePath.exists():
            raise ValueError(
                "copyPathsToVariationDataFolder: Source path doesn't exist.",
                sourcePath,
            )

        dataDirPath = self._getDataDirPath()

        absoluteTargetPath = (dataDirPath / targetPath).resolve()

        assert dataDirPath.is_absolute()

        if not absoluteTargetPath.is_relative_to(dataDirPath):
            raise ValueError(
                "copyPathsToVariationDataFolder: target path must not escape variation data directory.",
                targetPath,
            )

        targetParentPath = absoluteTargetPath.parent
        if not targetParentPath.exists():
            targetParentPath.mkdir(parents=True)

        if sourcePath.is_dir():
            _su.copytree(sourcePath, absoluteTargetPath)
        else:
            _su.copy(sourcePath, absoluteTargetPath)

    def _getDataDirPath(self):
        deckContainingDirPath = _pl.Path(self.pathOutput)
        dataDirPath = deckContainingDirPath / "data"
        return dataDirPath
