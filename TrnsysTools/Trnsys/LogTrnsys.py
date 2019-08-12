#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import string,shutil
import TrnsysTools.processingData.processFiles as spfUtils
import TrnsysTools.utilities.utilsSpf as utils
import numpy as num

class LogTrnsys():

    def __init__(self,_path,_name):        
                
        self.fileName = _name #_name.split('.')[0]                
        self.path = _path
        # self.nameLog = self.path + "\%s.lst" % _name
        self.nameLog = self.path + "\%s.log" % _name

               
        # self.printItProblemsFile = True
        
        self.pathOutput = self.path + "\%s" % self.fileName
        self.linesChanged = ""
        self.titleOfLatex = "%s" % self.fileName
       
        # self.nameDckPathOutput = self.pathOutput + "\%s.lst" % _name
        self.nameDckPathOutput = self.pathOutput + "\%s.log" % _name

        self.cleanMode = False
        
        #True is not working becasue it looks for files in the D:\MyPrograms\Trnsys17 as local path 
        self.useRelativePath = False 
   
        if(self.useRelativePath==False):         
            self.filesOutputPath = self.pathOutput
  
        self.eliminateComments = False
        self.numberOfFailedIt = 0
        
    def loadLog(self):        

        print "nameLog:%s" % self.nameLog 

        try:
            infile=open(self.nameLog,'r')
            lines=infile.readlines()                    
           
            skypChar = None    #['*'] #This will eliminate the lines starting with skypChar    
            replaceChar = None #[',','\''] #This characters will be eliminated, so replaced by nothing 
    
            self.lines = spfUtils.purgueLines(lines,skypChar,replaceChar,removeBlankLines=True,removeBlankSpaces=False)
    
            infile.close()
            
        except:
            self.lines = None
            self.numberOfFailedIt = 0

    def getCalculationTime(self):
            
            
        sentence="Total TRNSYS Calculation Time"
        
        #I increase the number of back lines to read becasue if we add the time for each type it is writen after the calclation time
        for i in range(len(self.lines)-1,len(self.lines)-500,-1):

            split =  self.lines[i].split(":")

            try:
                if (split[0].strip() == sentence):
                    ntime= split[1].strip()
                    time = string.atof(ntime.split()[0]) / 60.
                    return time
            except:
                pass
            
        return -99
                
    def getMyDataFromLog(self):
        
        sentence="The simulation failed to converge during"
        
        try:
            for i in range(len(self.lines)):
                
                split =  self.lines[i].split(sentence)
            
                try:    
                  
                   self.numberOfFailedIt = split[1].replace("%","\%")               
                   print self.numberOfFailedIt

                except:
                    pass
                                
        except:
            self.numberOfFailedIt = -99
            print "LOG FILE NOT FOUND"
            
        return None


    def getIteProblemsForEachMonth(self):
        
        sentence="TRNSYS Message    441"
        sentenceUnit="Reported information  : UNITS:"

        iteMonth = num.zeros(12)        
        
        self.hourWhereItProblems = []
        self.unitsInvolvedItProlems = []
        
        try:
            for i in range(len(self.lines)):
                
                mysplit =  self.lines[i].split(sentence)
                
                try:  
                    if(mysplit[1] != None):
                      

                        hourOfYear = string.atof(self.lines[i-3].split(":")[1])
                        self.hourWhereItProblems.append(hourOfYear)

                        units = self.lines[i+1].split(sentenceUnit)[1]
                        self.unitsInvolvedItProlems.append(list(units.split()))

#                       print "hourOfYear:%f " % (hourOfYear)
                        (n,d,h) = utils.getMonthIndexByHourOfYear(hourOfYear)
                        n=n-1
                        iteMonth[n] = iteMonth[n]+1
#                       print "ite in month:%d = %d"% (n,iteMonth[n])
                       
                   
                except:
                    pass
                                
        except:
            print "LOG FILE NOT FOUND"

        return iteMonth

    def writeFileWithItErrors(self,nameFile="ItProblems.dat"):

        # if(self.printItProblemsFile==True):

        lines = ""
        line = "!This file shows the time where it problems occur\n";lines+=line
        line = "!time [h] day itProblem\n";lines+=line


        for i in range(len(self.hourWhereItProblems)):
            line="%f\t%f\t%d\n"%(self.hourWhereItProblems[i],self.hourWhereItProblems[i]/24.,1)
            lines+=line

        nameItProblem = self.path + nameFile

        print "It problems printed in %s"%nameItProblem

        infile=open(nameItProblem,'w')
        lines=infile.writelines(lines)
        infile.close()
                

        
    