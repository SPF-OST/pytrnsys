# pylint: skip-file
# type: ignore

#!/usr/bin/python
"""
Author : Dani Carbonell
Date   : 30.09.2016
ToDo
"""

import os
import string, shutil
import pytrnsys.pdata.processFiles as spfUtils
import pytrnsys.trnsys_util.deckTrnsys as deckTrnsys
import pytrnsys.trnsys_util.deckUtils as deckUtils
import logging

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

    def loadDeck(self, useDeckName=False, check=False, eliminateComments=False, useDeckOutputPath=False):

        if useDeckName == False:
            nameDck = self.fileName  # self.nameDckPathOutput
        else:
            nameDck = useDeckName

        self.deckTrnsys = deckTrnsys.DeckTrnsys(self.path, nameDck)

        lines = self.deckTrnsys.loadDeck(
            eraseBeginComment=False, eliminateComments=False, useDeckOutputPath=useDeckOutputPath
        )

        if check == True:
            deckUtils.checkEquationsAndConstants(lines)

    def changeParameter(self, _parameters):

        self.deckTrnsys.changeParameter(_parameters)

        # with this function we obtain some data from the deck file.

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

        logger.debug("Path %s" % self.path)
        logger.debug("PathOutput %s" % self.pathOutput)

        if len(fileSource) >= 260:
            raise Exception("fileSource has a length of %d >= 260 exceeding Windows path length limit." % len(fileSource))
        if len(fileEnd) >= 260:
            raise Exception("fileEnd has a length of %d >= 260 exceeding Windows path length limit." % len(fileEnd))

        try:
            shutil.move(fileSource, fileEnd)
            logger.debug("move file %s to %s" % (name, fileEnd))
        except:
            logger.warning("FAIL to move the file %s to %s" % (name, fileEnd))

    def copyFileFromSource(self, name):

        fileSource = os.path.join(self.path, name)
        fileEnd = os.path.join(self.pathOutput, name)

        try:
            shutil.copy(fileSource, fileEnd)
            logger.debug("copy file %s to %s" % (name, fileEnd))
        except:
            logger.warning("FAIL to copy the file %s to %s" % (name, fileEnd))

    def copyFolderFrom(self, sourcePath, name):

        folderSource = os.path.join(sourcePath, name)
        folderEnd = os.path.join(self.pathOutput, name)

        try:
            shutil.copytree(folderSource, folderEnd)
            logger.debug("copy folder %s to %s" % (name, folderEnd))
        except:
            logger.warning("FAIL to copy the folder %s from %s to %s" % (name, folderSource, folderEnd))

    def setTrnsysVersion(self, version):
        self.trnsysVersion = version

    def getExecuteTrnsys(self, inputDict, useDeckName=False):

        if inputDict["ignoreOnlinePlotter"] == True:
            if self.removePopUpWindow == True:
                ext = " /H"
            else:
                ext = " /N"
            if useDeckName == False:
                cmd = self.trnsysExePath + " " + self.nameDckPathOutput + ext
            else:
                cmd = self.trnsysExePath + " " + useDeckName + ext
        else:
            if useDeckName == False:
                cmd = self.trnsysExePath + " " + self.nameDckPathOutput + " /N"
            else:
                cmd = self.trnsysExePath + " " + useDeckName + " /N"

        #        myCmd ='"%s"'%cmd #for blank spaces in paths

        logger.debug("getExecuteTrnsys cmd:%s" % cmd)

        #        os.system(myCmd)

        return cmd

    def executeTrnsys(self, useDeckName=False):

        # use this '"%s"' to handle blank spaces in executable name like Program Files/
        myCmd = '"%s"' % self.getExecuteTrnsys(useDeckName)

        # print myCmd

        os.system(myCmd)

        if self.cleanMode:
            self.cleanFilesForRunning()

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
