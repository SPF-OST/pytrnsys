#!/usr/bin/python
"""
Author : Dani Carbonell
Date   : 30.09.2016
ToDo :  the double comment.
Now Only one comment is erased, so that if we hve ! comment1 ! comment2 only the commen2 will be erased
"""

import os
import string,shutil
import processFiles as spfUtils

class DeckTrnsys():
    """
    This class gives the functionality to dck files:
    -to set a new path for the deck
    -to comment all online plotters
    -change the name of the deck
    -change the assign path
    """

    def __init__(self,_path,_name):        
        
        
        self.extensionDeck = "dck"

        self.setPathAndNames(_path,_name)
        
        self.linesChanged = ""
        self.cleanMode = False
        self.useAbsoluteTempPath = True #actually False does not work since trnsys does not work with  ./temp/whatever
                     
        #True is not working becasue it looks for files in the D:\MyPrograms\Trnsys17 as local path           
        self.eliminateComments = False
        try:
            self.myCommonTrnsysFolder = os.getenv("TRNSYS_DATA_FOLDER")+"\\"
        except:
            self.myCommonTrnsysFolder=None
                 
            print "Warning. TRNSYS_DATA_FOLDER not defined as a enviromental variable."

        self.packageNameTrnsysFiles="None"

    def setPackageNameTrnsysFiles(self,name):

        self.packageNameTrnsysFiles=name

    def setPathAndNames(self,_path,_name):
        
        self.fileName = _name #_name.split('.')[0]                
        self.path = _path
        self.nameDck = self.path + "\%s.%s" % (_name,self.extensionDeck)
        self.pathOutput = self.path + "\%s" % self.fileName        
        self.titleOfLatex = "%s" % self.fileName
        self.useRelativePath = False 
   
        if(self.useRelativePath==False):         
            self.filesOutputPath = self.pathOutput
       
        self.nameDckPathOutput = self.pathOutput + "\%s.%s" % (_name,self.extensionDeck)
        
    def setEliminateComments(self,comment):
        self.eliminateComments = comment
        
    def changeNameOfDeck(self,newName):
        
        self.nameDck = self.path + "\%s.%s" % (newName,self.extensionDeck)
        self.pathOutput = self.path + "\%s" % newName
        self.titleOfLatex = "%s" % newName
        self.tempFolderEnd = "%s\\temp" % self.pathOutput   
        self.nameDckPathOutput = self.pathOutput + "\%s.%s" % (newName,self.extensionDeck)

        if(self.useRelativePath==False):         
            self.filesOutputPath = self.pathOutput

    def createDeckBackUp(self):

        nameDeckBck = "%s-bck" % self.nameDck        
        shutil.copy(self.nameDck,nameDeckBck)
      

    def loadDeckWithoutComments(self):        
                    
        infile=open(self.nameDck,'r')
        lines=infile.readlines()        
        
#        skypChar = None    #['*'] #This will eliminate the lines starting with skypChar
        skypChar = ['*','!','      \n']    #['*'] #This will eliminate the lines starting with skypChar

        replaceChar = None #[',','\''] #This characters will be eliminated, so replaced by nothing 

        self.linesReadedNoComments = spfUtils.purgueLines(lines,skypChar,replaceChar,removeBlankLines=False)   

        #Only one comment is erased, so that if we hve ! comment1 ! comment2 only the commen2 will be erased
        self.linesReadedNoComments = spfUtils.purgueComments(self.linesReadedNoComments,['!'])
        
#        print self.linesChanged
        infile.close()
        
    def loadDeck(self,useDeckName=False,eraseBeginComment=True):        

        if(useDeckName==False):
            pass
            print "DECK TRNSYS::LOAD DECK nameDeck:%s eliminateCmments=%s" % (self.nameDck,self.eliminateComments)

        else:
            print "DECK TRNSYS::LOAD DECK nameDeck:%s eliminateCmments=%s USEDECKNAME:%s" % (self.nameDck,self.eliminateComments,useDeckName)
            self.nameDck = useDeckName    
            self.nameDckPathOutput = useDeckName 
            
#        infile=open(self.nameDck,'r')            
        infile=open(self.nameDckPathOutput,'r')
        
        lines=infile.readlines()        
        
#        skypChar = None    #['*'] #This will eliminate the lines starting with skypChar
        if(eraseBeginComment==True):
            skypChar = ['*','!','      \n']    #['*'] #This will eliminate the lines starting with skypChar
        else:
            skypChar = ['!','      \n']    #['*'] #This will eliminate the lines starting with skypChar
            
        replaceChar = None #[',','\''] #This characters will be eliminated, so replaced by nothing 

        self.linesChanged = spfUtils.purgueLines(lines,skypChar,replaceChar,removeBlankLines=True)   

        #Only one comment is erased, so that if we hve ! comment1 ! comment2 only the commen2 will be erased
        if(self.eliminateComments==True):
            self.linesChanged = spfUtils.purgueComments(self.linesChanged,['!'])
        
        infile.close()

    def loadDeckAndEraseWhiteSpaces(self):        

        print "nameDeck:%s" % self.nameDck 
 
        infile=open(self.nameDck,'r')
        lines=infile.readlines()        
        
       
#        skypChar = None    #['*'] #This will eliminate the lines starting with skypChar
        skypChar = ['*','      \n']    #['*'] #This will eliminate the lines starting with skypChar

        replaceChar = None #[',','\''] #This characters will be eliminated, so replaced by nothing 

        self.linesChanged = spfUtils.purgueLines(lines,skypChar,replaceChar,removeBlankLines=True)   

        #Only one comment is erased, so that if we hve ! comment1 ! comment2 only the commen2 will be erased
        if(self.eliminateComments==True):
            self.linesChanged = spfUtils.purgueComments(self.linesChanged,['!'])
        
#        print self.linesChanged
        infile.close()

        
        #Create temporary file
        
#        tempName = "%s.temp" % self.nameDck
#        print "tempName:%s" % tempName
#        tempFile=open(tempName,'w')
#
#        tempFile.writelines(self.linesChanged)
#        tempFile.close()

    def writeDeck(self):

        tempName = "%s" % self.nameDck
        print "tempName:%s" % tempName
        tempFile=open(tempName,'w')
        tempFile.writelines(self.linesChanged)
        tempFile.close()

    def changeAssignPath(self,HOMEPath=False):
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
                        if(splitPath[j]=="HOME$"):
                            name = os.path.join(*splitPath[j+1:]) #* sot joining the vector, j+1 becasue we dont need spfTrnsysFiles,already in the path my commonTrnsysFolder
                            if HOMEPath:
                                if len(splitBlank)>2:
                                    lineChanged ="ASSIGN \"%s\" %s \n" % (os.path.join(HOMEPath,name),splitBlank[2])
                                else:
                                    lineChanged = "ASSIGN \"%s\" \n" % (os.path.join(HOMEPath, name))
                            else:
                                print("Warning: Common Trnsys Folder from config file not used. Use TRNSYS_DATA_FOLDER enviroment variable instead (deprecated)")
                                if len(splitBlank)>2:
                                    lineChanged = "ASSIGN \"%s\" %s \n" % (os.path.join(self.HOMEPath, name), splitBlank[2])
                                else:
                                    lineChanged = "ASSIGN \"%s\" \n" % (os.path.join(self.HOMEPath, name))
                    if(lineChanged!=False):
                        self.linesChanged[i] = lineChanged
            except:
                pass



    def ignoreOnlinePlotter(self):
          
        jBegin = 0
        jEnd   = 0
        found=False
        
        plotterFound = 0
        
        for i in range(len(self.linesChanged)):
                 
            splitBlank =  self.linesChanged[i].split() 
                   
#            if(jBegin>0 and i>jBegin+30):
#                raise ValueError("jBegin found and not finishd yet")

#            print "check line i:%d"%i
            
                
            if(found==True):
              try:                  
                  
#                  print splitBlank[0].replace(" ","").lower()
                  
                  if(splitBlank[0].replace(" ","").lower()=="LABELS".lower()):
                      
            
                      nLabelString = splitBlank[1].replace(" ","")
                      nLabel  = string.atoi(nLabelString)
                      
                      jEnd = i+nLabel
                      
#                      print "jBegin:%d jEnd:%d nLabel:%d"%(jBegin,jEnd,nLabel)
                      
#                      raise ValueError()
                      
                      for j in range(jBegin,jEnd+1,1):
#                          print "COMMENT (1) FROM j:%d"%(j)
                          self.linesChanged[j]="**IGNORE ONLINE PLOTTER - 1"+self.linesChanged[j]
                      
                      found=False
                      i=jEnd #it does nothing !!!
                      
                      
              except:
#                print "COMMENT (3) FROM i:%d"%(i)
                self.linesChanged[i]="**IGNORE ONLINE PLOTTER 3 - \n"+self.linesChanged[i]
                
            else: #First it looks for the unit number corresponding to the TYPE and comments util it enters into the LABEL (try section above)
                found=False
                try:    
                    unit  = splitBlank[0].replace(" ","")
                    nUnit = splitBlank[1].replace(" ","")                                      
                    types = splitBlank[2].replace(" ","")     
                    ntype = splitBlank[3].replace(" ","")                     
                    
                    
                    if(unit.lower()=="unit".lower() and types.lower()=="Type".lower() and ntype=="65"):
                        jBegin=i                                      
                        found=True    
                        self.linesChanged[i]="** IGNORE ONLINE PLOTTER - "+self.linesChanged[i]
#                        print "FOUND CASE i:%d %s"%(i,ntype) 
                        plotterFound = plotterFound+1
                        
    #                    print "FOUND CASE j:%d TYPE:%s UNIT:%s "%(j,ntype,nUnit)
                    
                    
                except:                
                    pass

        outfile=open(self.nameDck,'w')


        outfile.writelines(self.linesChanged)
        outfile.close() 
             
        return None
        
    # used to change the path os files when we move the deck. It is assumed that common folders are the same       
    def updatePath(self):
                
        for i in range(len(self.linesChanged)):
                 
            splitBlank = self.linesChanged[i].split()

            try:       
                if(splitBlank[0]=="ASSIGN"):                    
                         
                    fileNameWithoutCommas = string.replace(splitBlank[1],"\"","")
                    buildingSplit = fileNameWithoutCommas.split("building\\")                         
                             
                                                    
    #==============================================================================
    #                              BUILDING DATA 
    #==============================================================================                             
                         
                    if(len(buildingSplit)>1):     
                         #Not used from the common folder becasue if some executable try to read the same file it fails.                                                                                                 
                         try: #It changes the buildign anme if set in parameters
                             myFileInNewPath = self.pathOutput +"\\building\\"+ self.parameters["buildingName"]
                             self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                         except: #change the path to the common Trnsys folder 
                             myFileInNewPath = self.pathOutput +"\\building\\"+ buildingSplit[1]
                             self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                             
#                                 try: #It changes the buildign anme if set in parameters
#                                     myFileInNewPath = self.myCommonTrnsysFolder +"\\building\\"+ self.parameters["buildingName"]
#                                     self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
#                                 except: #change the path to the common Trnsys folder 
#                                     myFileInNewPath = self.myCommonTrnsysFolder +"\\building\\"+ buildingSplit[1]
#                                     self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                             
                         print "Building changed :%s " % self.linesChanged[i]

#==============================================================================
#                               TEMP FOLDER
#==============================================================================
                             
                    nameSplited = fileNameWithoutCommas.split("temp\\")
                     
                    try:
                         myFileInNewPath = self.filesOutputPath +"\\temp\\"+ nameSplited[1]
                         self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
    
                    except:
                         
                         if(nameSplited[0]=="Temp_zone.BAL" or nameSplited[0]=="Energy_zone.BAL"):                              
                             myFileInNewPath = self.filesOutputPath +"\\"+ nameSplited[0]
                             self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])      
            except:
                pass

    def getVariables(self):
        
        self.eliminateComments = True  #BE CAREFUL, THIS CAN CHANGE  [30,1] by [301] so it does not WORK !!!! DC: Is this updated?
        self.loadDeck(self.nameDckPathOutput)
        
        self.variablesNames   = []
        self.variablesResults = []
        
        for i in range(len(self.linesChanged)):
                 
             splitEquality = self.linesChanged[i].split('=')
             try:                
                 myName = splitEquality[0].replace(" ","")
                 myValue = splitEquality[1].replace(" ","")
                 
                 self.variablesNames.append("%s"%myName)
                 self.variablesResults.append("%s"%myValue)
                 
             except:
                pass
            
        nameFile = self.pathOutput+"\\namesVariables.info"
           
        lines = ""   
        for name in  self.variablesNames:
          
           count = 0
           resFound = ""
           for res in self.variablesResults:
               n = res.count(name)
               count = count + n
               if(n>=1):
                   resFound = resFound + "\t%s"%res
#           print "name:%s count:%d" % (name,count)
           
           line = name+" count=%d\n" % count; lines = lines + line
           if(count>=1):
               line = "%s"%resFound; lines = lines + line
               
        outfile=open(nameFile,'w')
        outfile.writelines(lines)
        outfile.close() 
                          
    def changeParameter(self,_parameters): #Is this used??

                 
#         print "linesChanged"
#         print self.linesChanged
         print "Change Parameters deckTrnsys Class"
#         print _parameters
         
         if(_parameters != None):
             
             self.parameters = _parameters

#             print "execute TRNSYS. Parameters"                       
#             print self.parameters
#             for key in self.parameters.iterkeys():                                                         
#                 print "key:%s"%key
             
             for i in range(len(self.linesChanged)):
                 
                 splitEquality = self.linesChanged[i].split('=')
                 splitBlank = self.linesChanged[i].split()
                 
#                 print splitEquality
                 #print splitBlank
                 
#                 Im IN ASSIGN building\T44A38sfh100.bui 56 
#                 fileNameWithoutCommas:building\T44A38sfh100.bui
#                 ['building\\T44A38sfh100.bui']


                 try:       
                     if(splitBlank[0]=="ASSIGN"):                    
                         
#                         print "Im IN %s %s %s " % (splitBlank[0],splitBlank[1],splitBlank[2])
                         
                         fileNameWithoutCommas = string.replace(splitBlank[1],"\"","")
                         
#                         print "fileNameWithoutCommas:%s" % fileNameWithoutCommas
                         

                       
                             
    #==============================================================================
    #                              BUILDING DATA 
    #==============================================================================

# buildingSplit = fileNameWithoutCommas.split("building\\")

#                          if(len(buildingSplit)>1):
#                              #Not used from the common folder becasue if some executable try to read the same file it fails.
#                              try: #It changes the buildign anme if set in parameters
#                                  myFileInNewPath = self.pathOutput +"\\building\\"+ self.parameters["buildingName"]
#                                  self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
#                              except: #change the path to the common Trnsys folder
#                                  myFileInNewPath = self.pathOutput +"\\building\\"+ buildingSplit[1]
#                                  self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
#
# #                                 try: #It changes the buildign anme if set in parameters
# #                                     myFileInNewPath = self.myCommonTrnsysFolder +"\\building\\"+ self.parameters["buildingName"]
# #                                     self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
# #                                 except: #change the path to the common Trnsys folder
# #                                     myFileInNewPath = self.myCommonTrnsysFolder +"\\building\\"+ buildingSplit[1]
# #                                     self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
#
#                              print "Building changed :%s " % self.linesChanged[i]

#==============================================================================
#                              ADD DATA 
#==============================================================================
                        
                         # addDataSplit = fileNameWithoutCommas.split("add_dat\\")
                         #
                         #
                         # if(len(addDataSplit)>1):
                         #     myFileInNewPath = self.myCommonTrnsysFolder + "add_dat\\" + "%s" % addDataSplit[1]
                         #
                         #     self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                         #
                         #     print "Add_dat changed :%s " % self.linesChanged[i]
 
#==============================================================================
#                               COMPRESSOR
#==============================================================================
                                        
                         compressorDataSplit = fileNameWithoutCommas.split("Compressor\\")                         
                                 
                         if(len(compressorDataSplit)>1):     
                             myFileInNewPath = self.HOMEPath + "Compressor\\" + "%s" % compressorDataSplit[1]
                             self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                             
                             print "Compressor data changed :%s " % self.linesChanged[i]

#==============================================================================
#                               CLIMATE
#==============================================================================
                                        
                         # climateDataSplit = fileNameWithoutCommas.split("climate\\")
                         #
                         # if(len(climateDataSplit)>1):
                         #     myFileInNewPath = self.myCommonTrnsysFolder + "climate\\" + "%s" % climateDataSplit[1]
                         #     self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                         #
                         #     print "Climate data changed :%s " % self.linesChanged[i]

                        
#==============================================================================
#                               TEMP FOLDER
#==============================================================================
                             
                         nameSplited = fileNameWithoutCommas.split("temp\\")
                         
#                         print nameSplited
                         
                         try:
#                             print "split[0]:%f splt[1]:%s" % (fileNameWithoutCommas[0],fileNameWithoutCommas[1])
                             if(self.useAbsoluteTempPath):
                                 myFileInNewPath = self.filesOutputPath +"\\temp\\"+ nameSplited[1]
                                 self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])
                             else:
                                myFileInNewPath =  "\\temp\\" + nameSplited[1]
                                self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath, splitBlank[2])

    #                             print "lineChanged-0 : %s pathOut:%s nameSplied:%s" % (self.linesChanged[i],self.pathOutput,nameSplited[1])

                         except:
                             
                             if(nameSplited[0]=="Temp_zone.BAL" or nameSplited[0]=="Energy_zone.BAL"):
                                  
                                 myFileInNewPath = self.filesOutputPath +"\\"+ nameSplited[0]
                                 self.linesChanged[i] = "ASSIGN %s %s \n" % (myFileInNewPath,splitBlank[2])      
#                                 print "lineChanged-1 : %s pathOut:%s nameSplited:%s" % (self.linesChanged[i],self.pathOutput,nameSplited[0])
                                           
                 except: 
                    pass
                                        
                 try:                
                     myName = splitEquality[0].replace(" ","")
                     value = splitEquality[1].replace(" ","")                                      
                     
#                     print splitEquality,myName
                     
#                     print self.parameters
#                     print "myName:%s- oldValue:%s\n" % (myName,value)
                     
#                     print myName,value
                     
                     for key in self.parameters.iterkeys():                                                         
                         
#                         print "IN TRY key:%s"%key

#                         myName = string.replace(name," ","")
                                              
                         if(key.lower()==myName.lower()): #avoid case sensitive
#                                                     
                             myNewLine = "%s=%s ! value changed from original by executeTrnsys.py\n" % (key,self.parameters[key])
                             print "NEW LINE %s" % myNewLine  
#                             
                             self.linesChanged[i] = myNewLine
                                                                            
                 except:
#                    print "Not an equality name:%s\n" % name
                    pass
                
                
                             
             print 'OUPUT AT %s' % self.nameDck
                 
             outfile=open(self.nameDck,'w') 
            
             outfile.writelines(self.linesChanged)
             outfile.close() 
             
    #with this function we obtain some data from the deck file.
             
#    def getDataFromDeck(self,myName):
#        
#        for i in range(len(self.linesChanged)):
#            
#            splitEquality = self.linesChanged[i].split('=')
#        
#            try:    
#                name = splitEquality[0].replace(" ","")
#                value = splitEquality[1].replace(" ","")                                      
#
#                if(name.lower()==myName.lower()):  
#                    return value
#                
#            except:
#                pass
#                 
#        return None
        

    def readAllTypes(self):

        self.TrnsysTypes = []
        self.TrnsysUnits = []
        
        for i in range(len(self.linesReadedNoComments)):
            
            splitEquality =  self.linesReadedNoComments[i].split()
        
            try:    
                unit  = splitEquality[0].replace(" ","")
                nUnit = splitEquality[1].replace(" ","")                                      
                types =  splitEquality[2].replace(" ","")     
                ntype =  splitEquality[3].replace(" ","")     
                
                
                if(unit.lower()=="unit".lower() and types.lower()=="Type".lower()):
#                    print "unit:%s nUnit:%s types:%s ntype:%s"%(unit,nUnit,types,ntype)
                    self.TrnsysTypes.append(int(ntype))
                    self.TrnsysUnits.append(int(nUnit))
                
            except:
                pass
                 
        return None

   
    def getTypeFromUnit(self,myUnit):

        for i in range(len(self.linesReadedNoComments)):
            
            splitEquality =  self.linesReadedNoComments[i].split()
        
            try:    
                unit  = splitEquality[0].replace(" ","")
                nUnit = splitEquality[1].replace(" ","")                                      
                types =  splitEquality[2].replace(" ","")     
                ntype =  splitEquality[3].replace(" ","")     
                
                
                if(unit.lower()=="unit".lower() and types.lower()=="Type".lower()):
#                    print "unit:%s nUnit:%s types:%s ntype:%s"%(unit,nUnit,types,ntype)

                    if(nUnit.lower()==myUnit.lower()):
                        print "UNIT FOUND myUnit:%s type:%s"%(myUnit,ntype)
                        return ntype
                
            except:
                pass
                 
        return None
       
       
    def getMyDataFromDeck(self,myName):
        
        for i in range(len(self.linesReadedNoComments)):
            
            splitEquality =  self.linesReadedNoComments[i].split('=')
        
            try:    
                name = splitEquality[0].replace(" ","")
                value = splitEquality[1].replace(" ","")                                      

                if(name.lower()==myName.lower()):  
                    return value
                
            except:
                pass
                 
        return None

    def getDataFromDeck(self,myName,typeValue="string"):
    
        value = self.getMyDataFromDeck(myName)               
        
        if(value==None):
            return None
            
        if(typeValue=="double"):
            return string.atof(value)
        elif(typeValue=="int"):
            return string.atoi(value)
        elif(typeValue=="string"):
            return value
        else:
            raise ValueError("typeValue must be double,int or string")
        
    # it does not work if 
        # ______ ! dlskdkd
        #  EQUATIONS ! sdsds
    def checkEquationsAndConstants(self):
              
        for i in range(len(self.linesChanged)):
           
            splitBlank = self.linesChanged[i].split()
           
            
            if(splitBlank[0].lower()=="EQUATIONS".lower() or splitBlank[0].lower()=="CONSTANTS".lower()):               
                
                lineError = i+1
                try:
                    numberOfValues = string.atoi(splitBlank[1])
                except:
                    raise ValueError("checkEquationsAndConstants %s can't be split in line i:%d (missing number?)"%(splitBlank,i))
                    
                countedValues = 0 # start counting                
                error = 0                         
                while(error==0):
                    i = i+1
                    
                    splitEquality = self.linesChanged[i].split('=')
                    error = 1
#                    print "count=%d"%countedValues
#                    print splitEquality
                    
                    if(len(splitEquality)>=2):
#                        print "counting at %s"%(self.linesChanged[i])
                        error=0                                  
                        countedValues = countedValues+1
                                                
                if(countedValues != numberOfValues):
                    parsedFile = "%s.parse" % self.nameDck
                    outfile=open(parsedFile,'w')
                    outfile.writelines(self.linesChanged)                
                    outfile.close()
                        
                    raise ValueError("FATAL Error in : ",splitBlank[0]," at line ",lineError," of parsed file =",\
                    parsedFile,". Number set is ",numberOfValues," and there are ",countedValues)

    def getPipeData(self,massFlow):

#Calc with tube calc , we need 100 kPa pressure loss, 200-300 is accpeted too. Velocity should be 0.6 < v < 1.5 m/s
#Flow above or equal	kg/h	0	90	 140  235	405	 565 880 1445 1590	2557 4209  5943
#inner diam.	mm	            8	10	 13	  16	20	 25	 32	 39	  41.8	53	 68	   80.8
#U-value	kJ/hK	           20.2	17.7 15.3 13.7	12.3 9.3 8.3 6.6  6.1	4.8	 3.7   3.2

        if(massFlow<90.):
            dIn   = 8./1000. # m
            UPipe = 20.2 # kJ/hm2K
        elif(massFlow<140.):
            dIn   = 10./1000. # m
            UPipe = 17.7 # kJ/hm2K
        elif(massFlow<235.):
            dIn   = 13./1000. # m
            UPipe = 15.3 # kJ/hm2K
        elif(massFlow<405.):
            dIn   = 16./1000. # m
            UPipe = 13.7 # kJ/hm2K
        elif(massFlow<565.):
            dIn   = 20./1000. # m
            UPipe = 12.3 # kJ/hm2K
        elif(massFlow<880.):
            dIn   = 25./1000. # m
            UPipe = 9.3 # kJ/hm2K
        elif(massFlow<1445.):
            dIn   = 32./1000. # m
            UPipe = 8.3 # kJ/hm2K
        elif(massFlow<1590.):
            dIn   = 39./1000. # m
            UPipe = 6.6 # kJ/hm2K
        elif(massFlow<2557.):
            dIn   = 41.8/1000. # m
            UPipe = 6.1 # kJ/hm2K
        elif(massFlow<4209.):
            dIn   = 53./1000. # m
            UPipe = 4.8 # kJ/hm2K
        elif(massFlow<5943.):
            dIn   = 68/1000. # m
            UPipe = 3.7 # kJ/hm2K
        elif(massFlow<7000.):
            dIn   = 80.8/1000. # m
            UPipe = 3.2 # kJ/hm2K
        elif(massFlow>=7000.):
            dIn   = 100.8/1000. # m
            UPipe = 3. # kJ/hm2K
        
        return dIn,UPipe




    def resizeParameters(self,read=True):
        
        if(read):
            self.loadDeckWithoutComments()

        massFlowHpEvapNom = self.getDataFromDeck("MfrHpEvapRef",typeValue="double")
        massFlowHpCondNom = self.getDataFromDeck("MfrHpCondRef",typeValue="double")

        sizeHpUsed = self.getDataFromDeck("sizeHpUsed",typeValue="double")
        sizeHpNom = self.getDataFromDeck("sizeHpNom",typeValue="double")
        
        massFlowHpEvap = massFlowHpEvapNom*sizeHpUsed/sizeHpNom
        massFlowHpCond = massFlowHpCondNom*sizeHpUsed/sizeHpNom

        diPiPcm,UPipePcm = self.getPipeData(massFlowHpEvap)
        diPiSh,UPipeSh   = self.getPipeData(massFlowHpCond)

        areaCov = self.getDataFromDeck("AcollAp",typeValue="double")        
        useCov  = self.getDataFromDeck("useCovered",typeValue="int")        

        areaUnc = self.getDataFromDeck("AreaUnc",typeValue="double")        
        useUnc  = self.getDataFromDeck("useUncovered",typeValue="int")        
        
        areaCol = useCov*areaCov+useUnc*areaUnc

        versionDeck = self.getDataFromDeck("versionDeck",typeValue="int")
        
        if(versionDeck>=62):
            priorRoof = self.getDataFromDeck("PriorRoof",typeValue="int")
            if(priorRoof==1):
                massFlowCol = massFlowHpEvap
            else:
                massFlowColPerArea = self.getDataFromDeck("MfrCPriSpec",typeValue="double") # kg/h m2            
                massFlowCol = massFlowColPerArea*areaCol
        else:                
            massFlowColPerArea = self.getDataFromDeck("MfrCPriSpec",typeValue="double") # kg/h m2            
            massFlowCol = massFlowColPerArea*areaCol

        #PIPE COLLECTOR        
        dInCol,UPipeCol = self.getPipeData(massFlowCol)
        #PIPE HP EVAPORATOR
                
        print "RESIZE PARAMETERS"
        print "massFlow:%f [kg/h] areaCov:%f useCov:%d areaUnc:%f useUInc:%d"%(massFlowCol,areaCov,useCov,areaUnc,useUnc)
        print "sizeHpUsed:%f sizeHpNom:%f nominalFlowEvap:%d realFlowEvap:%f nominalFlowCond:%d realFlowCond:%f"%(sizeHpUsed,sizeHpNom,massFlowHpEvapNom,massFlowHpEvap,massFlowHpCondNom,massFlowHpCond)
        
        
        myParameters = { 
        "diPiCPri" : dInCol,
        "UPiCPri0" : UPipeCol,
        "diPiPCM"  : diPiPcm,
        "UPiPCM0"  : UPipePcm,
        "diPiAux"  : diPiSh,
        "UPiHydUncorr" : UPipeSh
        }

        print myParameters
        
        self.changeParameter(myParameters)

    def getTypeName(self, typeNum):

        if (typeNum == 888):
            return "General Controller (SPF)"
        elif (typeNum == 816):
            return "Averaging"
        elif (typeNum == 862):
            return "TColl control expected for switch (SPF)"
        elif (typeNum == 817):
            return "Time delay"
        elif (typeNum == 863):
            return "Ice controller (SPF)"
        elif (typeNum == 993):
            return "Recall"
        elif (typeNum == 46):
            return "Monthly integrator"
        elif (typeNum == 9):
            return "Data reader"
        elif (typeNum == 109):
            return "Weather data processor"
        elif (typeNum == 33):
            return "Psychrometrics"
        elif (typeNum == 69):
            return "Sky temperature"
        elif (typeNum == 861):
            return "Ice Storage non-deiceable (SPF)"
        elif (typeNum == 25):
            return "User defined printer"
        elif (typeNum == 889):
            return "Adapted PD-controller"
        elif (typeNum == 833):
            return "Collector with condensation (SPF)"
        elif (typeNum == 977):
            return "Parameter fit heat pump (SPF)"
        elif (typeNum == 1925 or typeNum == 1924):
            return "Plug-flow TES (SPF)"
        elif (typeNum == 811):
            return "Tempering valve"
        elif (typeNum == 929):
            return "TeePiece (SPF)"
        elif (typeNum == 931):
            return "Pipe (reverted option) (SPF)"
        elif (typeNum == 1792):
            return "Radiant floor (SPF)"
        elif (typeNum == 5998):
            return "Building ISO (SPF)"
        elif (typeNum == 2):
            return "Collector controller"
        elif (typeNum == 935):
            return "Flow solver (SPF)"

        else:
            return "Unknown"

