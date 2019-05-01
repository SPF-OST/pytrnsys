#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string,shutil
import processFiles as spfUtils
import deckTrnsys 

# 
#
#

class ExecuteTrnsys():

    def __init__(self,_path,_name):        
                
        self.fileName = _name #_name.split('.')[0]                
        self.path = _path
        self.nameDck = os.path.join(self.path, _name + '.dck')               
        self.linesChanged = ""
        self.titleOfLatex = "%s" % self.fileName

        self.addGround=False #Added Ground file for ground calculations
        self.addWWProfile=False
        self.addBuildingData=True #if ISo model set to FALSE
        self.addSimData=False #MB you have to activate this in your case.

        self.trnsysVersion="TRNSYS_EXE"
        self.trnsysExePath="enviromentalVariable"
        self.myCommonTrnsysFolder= None

        self.pathOutput = os.path.join(self.path, self.fileName)
        
        if not os.path.exists(self.pathOutput):
            print self.pathOutput
            os.makedirs(self.pathOutput)
        
        self.tempFolder = os.path.join(self.path, 'temp')
        self.tempFolderEnd = os.path.join(self.pathOutput, 'temp')   
       
        self.nameDckPathOutput = os.path.join(self.pathOutput, _name + '.dck')

        self.cleanMode = True
        
        self.foldersForRunning = []
        self.filesForRunning = []
        self.foldersForRunningFromSource = []
   
        self.filesOutputPath = "."
        #True is not working becasue it looks for files in the D:\MyPrograms\Trnsys17 as local path 
        self.useRelativePath = False 
   
        if(self.useRelativePath==False):         
            self.filesOutputPath = self.pathOutput

        
        # if True it reads files from common folder defined by TRNSYS_DATA_FOLDER
        # the problem is that some files like building fail if tried to open by several trnsys executables
        
#        self.useSameCommonFolder=True
        
#        print "file:%s path:%s pathOutput:%s filesOutputPath:%s\n" % (self.fileName,self.path,self.pathOutput,self.filesOutputPath)

        # self.copyFilesForRunning() #I move this in order to be able to set the path self.myCommonTrnsysFolder manually.

    def setAddBuildingData(self,add):
        self.addBuildingData=add

    def setCommonTrnsysFolderPath(self,path):
        self.myCommonTrnsysFolder = path

    def setTrnsysExePath(self,path):
        self.trnsysExePath = path

    def redefinePath(self,path,_name):

        self.pathOutput = self.path
        
        if not os.path.exists(self.pathOutput):
            print self.pathOutput
            os.makedirs(self.pathOutput)
        
        self.tempFolder = os.path.join(self.path, 'temp')
        self.tempFolderEnd = os.path.join(self.pathOutput, 'temp')          
        self.nameDckPathOutput = os.path.join(self.pathOutput, _name + '.dck')

    def ignoreOnlinePlotter(self,useOutputDeck=False):

        nameDck = self.deckTrnsys.nameDck
        nameDckPathOutput = self.deckTrnsys.nameDckPathOutput

        if(useOutputDeck==True):
            self.deckTrnsys.nameDck = nameDckPathOutput

        self.deckTrnsys.ignoreOnlinePlotter()

        self.deckTrnsys.nameDck = nameDck

    def changeNameOfDeck(self,newName):
        
        self.nameDck = os.path.join(self.path, newName + ".dck")
        self.pathOutput = os.path.join(self.path,newName)
        self.titleOfLatex = "%s" % newName
        self.tempFolderEnd = os.path.join(self.pathOutput, 'temp')   
        self.nameDckPathOutput = os.path.join(self.pathOutput, newName  + ".dck")

        self.deckTrnsys.nameDck = self.nameDck
        self.deckTrnsys.pathOutput = self.pathOutput
        self.deckTrnsys.tempFolderEnd = self.tempFolderEnd
        self.deckTrnsys.nameDckPathOutput = self.nameDckPathOutput
        

        if(self.useRelativePath==False):         
            self.filesOutputPath = self.pathOutput
                
#        print self.path        
#        print self.nameDck 
#        print self.pathOutput
        
#        print self.tempFolderEnd
#        print self.nameDckPathOutput
#        
        
    def createDeckBackUp(self):

        nameDeckBck = "%s-bck" % self.nameDck        
        shutil.copy(self.nameDck,nameDeckBck)
        
    def resizeParameters(self):
        
        self.deckTrnsys.resizeParameters(read=True)
        
    def loadDeck(self,useDeckName=False,check=False,eliminateComments=False):        
                    
              
        print self.path
        print self.fileName
                
        self.deckTrnsys = deckTrnsys.DeckTrnsys(self.path,self.fileName)

        if(eliminateComments==False):
            self.deckTrnsys.eliminateComments =False   
            
        self.deckTrnsys.loadDeck(useDeckName,eraseBeginComment=False) #neglectBeginComment=True in order to let information about each file in the deck
        
        if(check==True):
            self.deckTrnsys.checkEquationsAndConstants()
        
    def changeParameter(self,_parameters):

        self.deckTrnsys.changeParameter(_parameters)
      
        #with this function we obtain some data from the deck file.


    def changeAssignPath(self,commonTrnsysFolder=False):


        # self.deckTrnsys.changeAssign(_nameActual,_nameChanged)

        self.deckTrnsys.changeAssignPath(commonTrnsysFolder=commonTrnsysFolder)

    def getDataFromDeck(self,myName):
        
        return self.deckTrnsys.getDataFromDeck(myName)            
        
    def addFilesForRunning(self,nameFiles):
        
        self.filesForRunning.append(nameFiles)
        
    def addFoldersForRunning(self,nameFolder):
        
        self.foldersForRunning.append(nameFolder)
     
    def addFoldersForRunningFromSource(self,nameFolder):
 
        self.foldersForRunningFromSource.append(nameFolder)
 
    def addAllFilesAndFoldersForRunning(self):
        
#        self.addFilesForRunning("fort.93" )
#        self.addFilesForRunning("Temp_zone.BAL" )
#        self.addFilesForRunning("Energy_zone.BAL")
#        self.addFilesForRunning("temp\Month_sum_zone.BAL")
        
        if(self.addGround==True):         self.addFilesForRunning("TGroundIni.dat")
        if(self.addWWProfile==True):      self.addFoldersForRunning("Wastewaterprofil")        
        
        if(self.addBuildingData==True):
            self.addFoldersForRunning("building")
        if(self.addSimData==True):      self.addFoldersForRunning("SimData")

#        I use them from a common folder 
        
#        self.addFoldersForRunning("Climate")
#        self.addFoldersForRunning("Compressor")
#        self.addFoldersForRunning("add_dat")

        
    def copyFilesForRunning(self):

        if(self.myCommonTrnsysFolder==None):

            self.myCommonTrnsysFolder = os.getenv("TRNSYS_DATA_FOLDER") + "\\"

            if (self.myCommonTrnsysFolder == None):
                raise ValueError("FATAL. The user must define TRNSYS_DATA_FOLDER as a enviromental variable. \
                     In this folder you must place the folders needed for calculation, for example add_data, climate, etc. My TrnsysFolder:%s" % self.myCommonTrnsysFolder)
        else:
            self.myCommonTrnsysFolder=self.myCommonTrnsysFolder+ "\\"

         # File used for Ground calculation of Type 708        

        self.cleanAndCreateResultsTempFolder()

        #This function should be called by the class of specific case Solar and Heat Pump or Ice ...

        self.addAllFilesAndFoldersForRunning()
              
        for nameFile in self.filesForRunning:
            self.copyFileFromSource(nameFile)

        nameFile = "%s.dck" % self.fileName
        print nameFile            
        
        self.moveFileFromSource(nameFile)
        
        for nameFolder in self.foldersForRunning:     
            print "executeTrnsys.py Folder for running from common folder :%s" % nameFolder            
            self.copyFolderFromCommonFolder(nameFolder)        

        for nameFolder in self.foldersForRunningFromSource:
            print "folder for running from source folder :%s" % nameFolder                        
            self.copyFolderFromSource(nameFolder)

    def cleanFilesForRunning(self):

        for folder in self.foldersForRunning:
            folderWithPath = os.path.join(self.pathOutput,folder)
            shutil.rmtree(folderWithPath)

        for files in self.filesForRunning:
            fileWithPath = os.path.join(self.pathOutput,files)
            shutil.rmtree(fileWithPath)
        
    def moveFileFromSource(self,name):
        
        fileSource = os.path.join(self.path,name)
        fileEnd    = os.path.join(self.pathOutput,name)

        print 'Path', self.path
        print 'PathOutput', self.pathOutput

        try:
            shutil.move(fileSource,fileEnd)      
            print "\nmove file %s to %s\n" % (name,fileEnd)
        except:
            print "\nFAIL to move the file %s to %s" % (name,fileEnd)

    def copyFileFromSource(self,name):
        
        fileSource = os.path.join(self.path,name)
        fileEnd    = os.path.join(self.pathOutput,name)

        try:
            shutil.copy(fileSource,fileEnd)      
            print "\ncopy file %s to %s\n" % (name,fileEnd)
        except:
            print "\nFAIL to copy the file %s to %s\n" % (name,fileEnd)
        
    def copyFolderFrom(self,sourcePath,name):
        
        folderSource = os.path.join(sourcePath,name)
        folderEnd    = os.path.join(self.pathOutput,name)
                
        try:
            shutil.copytree(folderSource,folderEnd)      
            print "copy folder %s to %s" % (name,folderEnd)
        except:
            print "FAIL to copy the folder %s from %s to %s" % (name,folderSource,folderEnd)
            
    def copyFolderFromSource(self,name):

        self.copyFolderFrom(self.path,name)
        
    def copyFolderFromCommonFolder(self,name):
            
        self.copyFolderFrom(self.myCommonTrnsysFolder,name)
            
    def setTrnsysVersion(self,version):
        self.trnsysVersion = version
        
    def getExecuteTrnsys(self,useDeckName=False):

        if(self.trnsysExePath=="enviromentalVariable"):

            self.trnsysExe = os.getenv(self.trnsysVersion)

            if(self.trnsysExe==None):

                raise ValueError("FATAL. The user must define TRNSYS_EXE as a enviromental variable.")
        else:
            self.trnsysExe = self.trnsysExePath

        if(useDeckName==False):
            cmd = self.trnsysExe +" "+ self.nameDckPathOutput + " /N"              
        else:
            cmd = self.trnsysExe +" "+ useDeckName + " /N"
        
        
#        myCmd ='"%s"'%cmd #for blank spaces in paths
        
        print "getExecuteTrnsys cmd:%s"%cmd
        
#        os.system(myCmd)         
        
        return cmd        
        
    def executeTrnsys(self,useDeckName=False):
                      
        #use this '"%s"' to handle blank spaces in executable name like Program Files/
        myCmd ='"%s"'%self.getExecuteTrnsys(useDeckName)            
        
        print myCmd 
        
        os.system(myCmd)

        if(self.cleanMode):
            self.cleanFilesForRunning()
        
    def copyReadFiles(self):
        
       nameFile =  "\\temp\\DhwOut.plt" 
       nameSource  = self.path + nameFile
       nameOut     = self.pathOutput + nameFile
       
       print nameSource
       print nameOut
       
       shutil.copy(nameSource,nameOut)
           
    def cleanAndCreateResultsTempFolder(self):
      
       try:
           print "removing temp : %s " % self.tempFolderEnd
           shutil.rmtree(self.tempFolderEnd)   
           os.makedirs(self.tempFolderEnd)
           
       except:
           print "creating temp : %s " % self.tempFolderEnd
           os.makedirs(self.tempFolderEnd)
           pass

    def movingAuxFiles(self):
        
       nameSource  = self.path + "\\%s.log" % self.fileName
       nameOut     = self.pathOutput + "\\%s.log" % self.fileName
       
       shutil.move(nameSource,nameOut)
               
       nameSource  = self.path + "\\%s.lst" % self.fileName
       nameOut     = self.pathOutput + "\\%s.lst" % self.fileName
       
       shutil.move(nameSource,nameOut)
        
       nameSource  = self.path + "\\%s.dck" % self.fileName
       nameOut     = self.pathOutput + "\\%s.dck" % self.fileName
       
       shutil.copy(nameSource,nameOut)
       


