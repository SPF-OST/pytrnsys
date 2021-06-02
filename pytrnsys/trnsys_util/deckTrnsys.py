# pylint: skip-file
# type: ignore

#!/usr/bin/python
"""
Author : Dani Carbonell
Date   : 30.09.2016
ToDo :  the double comment.
Now Only one comment is erased, so that if we hve ! comment1 ! comment2 only the commen2 will be erased
"""

import os
import string, shutil
import pytrnsys.trnsys_util.deckUtils as deckUtils
import re
import logging

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

        self.linesDeck = ""
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
        self.nameDck = self.path + "\%s.%s" % (_name, self.extensionDeck)
        self.pathOutput = self.path + "\%s" % self.fileName
        self.titleOfLatex = "%s" % self.fileName
        self.useRelativePath = False

        if self.useRelativePath == False:
            self.filesOutputPath = self.pathOutput

        self.nameDckPathOutput = self.pathOutput + "\%s.%s" % (_name, self.extensionDeck)

    def setEliminateComments(self, comment):
        self.eliminateComments = comment

    def changeNameOfDeck(self, newName):

        self.nameDck = self.path + "\%s.%s" % (newName, self.extensionDeck)
        self.pathOutput = self.path + "\%s" % newName
        self.titleOfLatex = "%s" % newName
        self.tempFolderEnd = "%s\\temp" % self.pathOutput
        # self.nameDckPathOutput = self.pathOutput + "\%s.%s" % (newName,self.extensionDeck)

        if self.useRelativePath == False:
            self.filesOutputPath = self.pathOutput

    def createDeckBackUp(self):

        nameDeckBck = "%s-bck" % self.nameDck
        shutil.copy(self.nameDck, nameDeckBck)

    def loadDeck(self, useDeckName=False, eraseBeginComment=True, eliminateComments=True, useDeckOutputPath=False):
        """
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
        jEnd = 0
        found = False

        plotterFound = 0

        for i in range(len(self.linesDeck)):

            splitBlank = self.linesDeck[i].split()

            #            if(jBegin>0 and i>jBegin+30):
            #                raise ValueError("jBegin found and not finishd yet")

            #            print "check line i:%d"%i

            if found == True:
                try:

                    #                  print splitBlank[0].replace(" ","").lower()

                    if splitBlank[0].replace(" ", "").lower() == "LABELS".lower():

                        nLabelString = splitBlank[1].replace(" ", "")
                        nLabel = int(nLabelString)

                        jEnd = i + nLabel

                        #                      print "jBegin:%d jEnd:%d nLabel:%d"%(jBegin,jEnd,nLabel)

                        #                      raise ValueError()

                        for j in range(jBegin, jEnd + 1, 1):
                            #                          print "COMMENT (1) FROM j:%d"%(j)
                            self.linesDeck[j] = "**IGNORE ONLINE PLOTTER - 1" + self.linesDeck[j]

                        found = False
                        i = jEnd  # it does nothing !!!

                except:
                    #                print "COMMENT (3) FROM i:%d"%(i)
                    self.linesDeck[i] = "**IGNORE ONLINE PLOTTER 3 - \n" + self.linesDeck[i]

            else:  # First it looks for the unit number corresponding to the TYPE and comments util it enters into the LABEL (try section above)
                found = False
                try:
                    unit = splitBlank[0].replace(" ", "")
                    nUnit = splitBlank[1].replace(" ", "")
                    types = splitBlank[2].replace(" ", "")
                    ntype = splitBlank[3].replace(" ", "")

                    if unit.lower() == "unit".lower() and types.lower() == "Type".lower() and ntype == "65":
                        jBegin = i
                        found = True
                        self.linesDeck[i] = "** IGNORE ONLINE PLOTTER - " + self.linesDeck[i]
                        #                        print "FOUND CASE i:%d %s"%(i,ntype)
                        plotterFound = plotterFound + 1

                #                    print "FOUND CASE j:%d TYPE:%s UNIT:%s "%(j,ntype,nUnit)

                except:
                    pass

        outfile = open(self.nameDck, "w")

        outfile.writelines(self.linesDeck)
        outfile.close()

        return None

    def getVariables(self):

        self.eliminateComments = (
            True  # BE CAREFUL, THIS CAN CHANGE  [30,1] by [301] so it does not WORK !!!! DC: Is this updated?
        )
        # self.loadDeck(self.nameDckPathOutput)
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

        lines = self.linesDeck

        #         print "linesDeck"
        #         print self.linesDeck
        logger.debug("Change Parameters deckTrnsys Class")
        #         print _parameters

        if _parameters != None:

            self.parameters = _parameters

            for i in range(len(lines)):

                splitEquality = lines[i].split("=")
                splitBlank = lines[i].split()

                #                 print splitEquality
                # print splitBlank

                #                 Im IN ASSIGN building\T44A38sfh100.bui 56
                #                 fileNameWithoutCommas:building\T44A38sfh100.bui
                #                 ['building\\T44A38sfh100.bui']

                try:
                    if splitBlank[0] == "ASSIGN":

                        #                         print "Im IN %s %s %s " % (splitBlank[0],splitBlank[1],splitBlank[2])

                        fileNameWithoutCommas = splitBlank[1].replace('"', "")

                        #                         print "fileNameWithoutCommas:%s" % fileNameWithoutCommas

                        # ==============================================================================
                        #                              BUILDING DATA
                        # ==============================================================================

                        # buildingSplit = fileNameWithoutCommas.split("building\\")

                        #                          if(len(buildingSplit)>1):
                        #                              #Not used from the common folder becasue if some executable try to read the same file it fails.
                        #                              try: #It changes the buildign anme if set in parameters
                        #                                  myFileInNewPath = self.pathOutput +"\\building\\"+ self.parameters["buildingName"]
                        #                                  self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                        #                              except: #change the path to the common Trnsys folder
                        #                                  myFileInNewPath = self.pathOutput +"\\building\\"+ buildingSplit[1]
                        #                                  self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                        #
                        # #                                 try: #It changes the buildign anme if set in parameters
                        # #                                     myFileInNewPath = self.myCommonTrnsysFolder +"\\building\\"+ self.parameters["buildingName"]
                        # #                                     self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                        # #                                 except: #change the path to the common Trnsys folder
                        # #                                     myFileInNewPath = self.myCommonTrnsysFolder +"\\building\\"+ buildingSplit[1]
                        # #                                     self.linesDeck[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                        #
                        #                              print "Building changed :%s " % self.linesDeck[i]

                        # ==============================================================================
                        #                               COMPRESSOR
                        # ==============================================================================

                        compressorDataSplit = fileNameWithoutCommas.split("Compressor\\")

                        if len(compressorDataSplit) > 1:
                            myFileInNewPath = self.HOMEPath + "Compressor\\" + "%s" % compressorDataSplit[1]
                            lines[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])

                            print("Compressor data changed :%s " % lines[i])

                        # ==============================================================================
                        #                               TEMP FOLDER
                        # ==============================================================================

                        nameSplited = fileNameWithoutCommas.split("temp\\")

                        #                         print nameSplited

                        try:
                            #                             print "split[0]:%f splt[1]:%s" % (fileNameWithoutCommas[0],fileNameWithoutCommas[1])
                            if self.useAbsoluteTempPath:
                                myFileInNewPath = self.filesOutputPath + "\\temp\\" + nameSplited[1]
                                lines[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])
                            else:
                                myFileInNewPath = "temp\\" + nameSplited[1]
                                lines[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])

                        #                             print "lineChanged-0 : %s pathOut:%s nameSplied:%s" % (self.linesDeck[i],self.pathOutput,nameSplited[1])

                        except:

                            if nameSplited[0] == "Temp_zone.BAL" or nameSplited[0] == "Energy_zone.BAL":

                                myFileInNewPath = self.filesOutputPath + "\\" + nameSplited[0]
                                lines[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])
                #                                 print "lineChanged-1 : %s pathOut:%s nameSplited:%s" % (self.linesDeck[i],self.pathOutput,nameSplited[0])

                except:
                    pass

                try:
                    myName = splitEquality[0].replace(" ", "")
                    value = splitEquality[1].replace(" ", "")

                    #                     print splitEquality,myName

                    #                     print self.parameters
                    #                     print "myName:%s- oldValue:%s\n" % (myName,value)

                    #                     print myName,value

                    for key in self.parameters.keys():

                        # print ("IN TRY key:%s"%key)

                        #                         myName = string.replace(name," ","")

                        if key.lower() == myName.lower():  # avoid case sensitive
                            #
                            myNewLine = "%s=%s ! value changed from original by executeTrnsys.py\n" % (
                                key,
                                self.parameters[key],
                            )
                            logger.debug("NEW LINE %s" % myNewLine)
                            #
                            lines[i] = myNewLine

                except:
                    #                    print "Not an equality name:%s\n" % name
                    pass

            logger.debug("variation deck file at %s" % self.nameDck)

            outfile = open(self.nameDck, "w")

            outfile.writelines(lines)
            outfile.close()

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
