#!/usr/bin/python
"""
Author : Dani Carbonell
Date   : 30.09.2016
ToDo :
"""

import pytrnsys.pdata.processFiles as spfUtils
import pytrnsys.trnsys_util.deckTrnsys as deck
import os
import pytrnsys.trnsys_util.deckUtils as deckUtils
import numpy as num
# import Tkinter as tk
import tkinter as tk
# import Tkinter.messagebox as tkMessageBox
from tkinter import messagebox as tkMessageBox

"""
This class uses a list of ddck files to built a complete TRNSYS deck file
"""

class BuildTrnsysDeck():
    """
    Class used to built a deck file out of a list of ddck files
    inputs :
    - pathDeck : outlet path where we want to built the dck file
    - nameDeck : the base name of the deck. This could be modified by the results of each simulation if variants are used in the cofing file
    - nameList : the list of ddck files needed to built a deck
    - pathList : the Base path of the ddck files
    """
    def __init__(self,_pathDeck,_nameDeck,_nameList,_pathList):
      
        self.pathDeck = _pathDeck
        self.nameDeck  = self.pathDeck + "\%s.dck" % _nameDeck
        
        self.oneSheetList = []       
        self.nameList = _nameList
        self.pathList = _pathList        
        self.deckText = []

        self.overwriteForcedByUser=False
        self.extOneSheetDeck = "ddck"

        self.skypChar = ['*','!','      \n']    #['*'] #This will eliminate the lines starting with skypChar
        self.eliminateComments = False

        self.replaceAutomaticUnits=True


    def loadDeck(self,_path,_name):        
            
        nameOneDck = _path + "\%s.%s" % (_name,self.extOneSheetDeck)
         
#        print nameOneDck
        
        infile=open(nameOneDck,'r')            
        lines=infile.readlines()        
       
        
        replaceChar = None #[',','\''] #This characters will be eliminated, so replaced by nothing 

        self.linesChanged = spfUtils.purgueLines(lines,self.skypChar,replaceChar,removeBlankLines=True)   

        if(self.eliminateComments==True):
            self.linesChanged = spfUtils.purgueComments(self.linesChanged,['!'])

        
        infile.close()
        
        return lines[0:3] #only returns the caption with the info of the file

    def changeAssignPath(self,rootPath):
        """
        This file only changes the assign path of those that start with HOME$, so we use for those the absolute path
        """
        for i in range(len(self.linesChanged)):
            splitBlank = self.linesChanged[i].split()

            try:
                if (splitBlank[0] == "ASSIGN"):
                    splitPath = splitBlank[1].split("\\")
                    lineChanged=False
                    for j in range (len(splitPath)):
                        if splitPath[j].lower() == 'path$':
                            name = os.path.join(*splitPath[j + 1:])
                            if len(splitBlank) > 2:
                                lineChanged = "ASSIGN \"%s\" %s \n" % (
                                os.path.join(rootPath, name), splitBlank[2])
                            else:
                                lineChanged = "ASSIGN \"%s\" \n" % (os.path.join(rootPath, name))
                    if(lineChanged!=False):
                        self.linesChanged[i] = lineChanged
            except:
                pass

    #
    def readDeckListConfig(self):
        """
        It uses the list of ddck to built a deck file

        """

        for i in range(len(self.nameList)):

            split = self.nameList[i].split()

            if(self.nameList[i][1]==":"): #absolute path

                nameList = split[-1]
                pathList = split[:-1]

            else:  # we use the generic path from GIT
                pathList = self.pathList
                nameList = self.nameList[i]

            firstThreeLines = self.loadDeck(pathList, nameList)

            addedLines = firstThreeLines + self.linesChanged

            caption = " **********************************************************************\n ** %s.ddck from %s \n **********************************************************************\n" % (
            nameList, pathList)

            self.deckText.append(caption)



            self.deckText = self.deckText + addedLines

    def readDeckList(self,doAutoUnitNumbering=True,dictPaths=False):
        """
         Reads all ddck files form the nameList and creates a single string with all in self.deckText
        :param self: nameList
        :return: self.deckText

        """

        self.unitId=9 #I start at 10 becasue it seems thta UNIT 4 and 6 can't be used?

        for i in range(len(self.nameList)):
            
            split = self.nameList[i].split("\\")

            if(self.nameList[i][1]==":"): #absolute path

                nameList = split[-1]
                pathVec = split[:-1]
                pathList =""
                for i in range(len(pathVec)):
                    if(i==0):
                        pathList =  pathVec[i]
                    else:
                        pathList =  pathList+"\\"+pathVec[i]

            elif(split[0].lower() == "local"): #We use a local path. This needs to be checked !!!
                pathVec = split[:-2] # Assuming last two names are the name group/type.ddck and the others are the path
                pathList=""
                for i in range(len(pathVec)):            
                    if(i==0):
                        pathList =  ".\\"+pathVec[i]
                    else:    
                        pathList =  pathList+"\\"+pathVec[i]
                
                nameVec = split[-2:]
                nameList = nameVec[0]+"\\"+nameVec[1]
                
            else: #we use the generic path from GIT
                pathList = self.pathList
                nameList = self.nameList[i]
                
            firstThreeLines=self.loadDeck(pathList,nameList)
            self.changeAssignPath(dictPaths[os.path.join(pathList,nameList)])
            addedLines = firstThreeLines+self.linesChanged
            
            caption = " **********************************************************************\n ** %s.ddck from %s \n **********************************************************************\n"%(nameList,pathList)

            if(doAutoUnitNumbering):
                (unit,types,fileAssign,fileAssignUnit)=deckUtils.readAllTypes(addedLines)
                print ("Replacemenet of Units of file:%s"%nameList)
                self.unitId = deckUtils.replaceAllUnits(addedLines,self.unitId,unit,fileAssignUnit,fileAssign)


            self.deckText.append(caption)
            
            self.deckText =  self.deckText + addedLines
        
    def writeDeck(self,addedLines=None):

        """
         Created the ddck file out of the self.deckText string
        :param self: deckText, self.nameDeck
        :return: a dcck file created
        """

        tempName = "%s" % self.nameDeck

        ok = True

        if (os.path.isfile(tempName) and self.overwriteForcedByUser==False):

            window = tk.Tk()
            window.geometry("2x2+" + str(window.winfo_screenwidth()) + "+" + str(window.winfo_screenheight()))
            ok = tkMessageBox.askokcancel(title="Processing Trnsys", message="Do you want override %s ?\n If parallel simulations most likely accepting this will ovrewrite all the rest too. Think of it twice !! " % tempName)
            window.destroy()

            if(ok):
                self.overwriteForcedByUser = True

        if(ok):
            tempFile=open(tempName,'w')
            if(addedLines != None):
                text = addedLines+self.deckText
            else:
                text = self.deckText
            tempFile.writelines(text)
            tempFile.close()
        else:
            raise ValueError("Not Accepted by user")
        


    def readTrnsyDeck(self,useDeckName=False):
        """
         It reads the deck generated using the DeckTrnsys Class and saves it into self.myDeck class DeckTrnsys.
        """
        nameDeck = self.nameDeck.split(".")[0]
        nameDeck = nameDeck.split("\\")[-1]
        self.myDeck = deck.DeckTrnsys(self.pathDeck,nameDeck)

        self.linesDeckReaded = self.myDeck.loadDeck(useDeckName=useDeckName,eraseBeginComment=False,eliminateComments=False)

        # self.myDeck.loadDeckWithoutComments()
        # self.linesDeckReaded = self.myDeck.linesReadedNoComments

    def checkTrnsysDeck(self,nameDck):

        # self.readTrnsyDeck()
        # deckUtils.checkEquationsAndConstants(self.linesDeckReaded)

        lines=deckUtils.loadDeck(nameDck,eraseBeginComment=True,eliminateComments=True)
        deckUtils.checkEquationsAndConstants(lines)

        self.linesDeckReaded=lines
        # self.myDeck.checkEquationsAndConstants(self.deckText) #This does not need to read

    def saveUnitTypeFile(self):

        (self.TrnsysUnits, self.TrnsysTypes,self.filesUsedInDdck,self.filesUnitUsedInDdck) = deckUtils.readAllTypes(self.deckText,sort=False)

        self.writeTrnsysTypesUsed("UnitsType.info")

    def writeTrnsysTypesUsed(self, name):

        lines = "UNIT\tTYPE\tName\n"

        for i in range(len(self.TrnsysTypes)):

            line = "%4d\t%4d\t%s\n" % (
            self.TrnsysUnits[i], self.TrnsysTypes[i], deckUtils.getTypeName(self.TrnsysTypes[i]))
            lines = lines + line

        for i in range(len(self.filesUsedInDdck)):
            nameUnitFile=deckUtils.getDataFromDeck(self.linesDeckReaded,self.filesUnitUsedInDdck[i])
            if(nameUnitFile==None):
                line = "%s\tNone\t%s\n" % (self.filesUnitUsedInDdck[i],self.filesUsedInDdck[i])
            else:
                line = "%s\t%s\t%s\n" % (self.filesUnitUsedInDdck[i],nameUnitFile[:-1],self.filesUsedInDdck[i])

            lines = lines + line

        nameFile = os.path.join(self.pathDeck, name)

        print ("Type file :%s created" % nameFile)
        outfile = open(nameFile, 'w')
        outfile.writelines(lines)


    def automaticEnegyBalanceStaff(self):
        """
            It reads and generates a onthly printer for energy system calculations in an automatic way
            It needs the data read by checkTrnsysDeck
        """
        eBalance = deckUtils.readEnergyBalanceVariablesFromDeck(self.deckText)
        unitId=self.unitId+1
        if(self.unitId<=10):
            unitId=600

        lines = deckUtils.addEnergyBalanceMonthlyPrinter(unitId,eBalance)
        self.deckText = self.deckText[:-4] + lines +self.deckText[-4:]
        self.writeDeck() # Deck rewritten with added printer


