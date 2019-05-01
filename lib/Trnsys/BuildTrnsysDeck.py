# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 10:02:57 2016

@author: dcarbone
"""

import processFiles as spfUtils
import deckTrnsys as deck
import os
import Tkinter as tk
import tkMessageBox

class BuildTrnsysDeck():

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
        
        return lines[0:3]

    def readDeckListConfig(self):

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

    def readDeckList(self):
                
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

            elif(split[0].lower() == "local"): #We use a local path
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
            
            addedLines = firstThreeLines+self.linesChanged
            
            caption = " **********************************************************************\n ** %s.ddck from %s \n **********************************************************************\n"%(nameList,pathList)
            
            
            self.deckText.append(caption)
            
            self.deckText =  self.deckText + addedLines
        
    def writeDeck(self,addedLines=None):

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
        
        
    def checkTrnsysDeck(self):
        
        nameDeck = self.nameDeck.split(".")[0]
        nameDeck = nameDeck.split("\\")[-1]
        myDeck = deck.DeckTrnsys(self.pathDeck,nameDeck)

        myDeck.eliminateComments=False
        myDeck.loadDeckAndEraseWhiteSpaces()
        myDeck.checkEquationsAndConstants()
        
        