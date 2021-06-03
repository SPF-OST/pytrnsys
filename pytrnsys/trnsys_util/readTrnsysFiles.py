# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
Class to read all kind of TRNSYS output files, monthly, hourly and with any timeStep data
Author : Daniel Carbonell
Date   : 26-07-2013
ToDo :   Copy config file to results folder automatically
"""


import pytrnsys.pdata.loadBaseNumpy as load
import numpy as num
import pytrnsys.utils.utilsSpf as utils
import pytrnsys.trnsys_util.deckTrnsys as deckTrnsys
import pytrnsys.trnsys_util.deckUtils as deckUtils

import string

import os


class ReadTrnsysFiles:
    def __init__(self, _path):

        self.path = _path

        self.clean()

        self.pathWithoutTemp = self.path[:-5]

    def setPath(self, _path):

        self.path = _path

    def clean(self):

        self.userDefinedFileIsReaded = False
        self.monthlyFileIsReaded = False
        self.hourlyFileIsReaded = False

        self.name = []
        self.variables = []
        self.numberOfMonthsSimulated = 0

    def readUserDefinedFiles(self, _nameFile, skypedLines=0, firstConsideredTime=8760, useOnlyOneYear=False):

        self.clean()

        self.userDefinedFileIsReaded = True

        nameUserDefinedFile = os.path.join(self.path, _nameFile)

        self.load = load.loadBaseNumpy(nameUserDefinedFile)
        self.load.loadFile(skypedLines=skypedLines, readLabels=True, verbose=True)

        self.name = self.load.namesVariables

        time = self.get("TIME")

        self.initialTime = time[0]
        self.timeStepUsed = (time[2] - time[1]) * 3600  # In seconds

        if firstConsideredTime == None:
            yearsSimulated = time[len(time) - 1] / 8760
            if utils.isWhole(yearsSimulated):
                firstConsideredTime = time[len(time) - 1] - 8760.0
                print(
                    "Number of years simulated : %d. First time considered is:%f. Last Time is :%f"
                    % (yearsSimulated, firstConsideredTime, time[len(time) - 1])
                )
                self.initialTime = firstConsideredTime
            else:
                firstConsideredTime = self.initialTime
                print("readUserDefinedFiles. First considered Time is initialTime:%f" % firstConsideredTime)

        k = 0
        for i in range(len(time)):
            if time[i] >= firstConsideredTime:
                #                raise ValueError("i:",i," time: ",time[i]," fistConsideredTime:",firstConsideredTime)
                k = i
                break

        print("time[i-1]:%f time[i]:%f k:%d" % (time[k - 1], time[k], k))

        if useOnlyOneYear == True:

            last = 0
            for i in range(k, len(time)):
                if time[i] >= (firstConsideredTime + 8760):
                    last = i
                    break

            print("INDEX FOR ONE YEAR begin:%d last:%d" % (k, last))

            self.timeInHours = time[k:last]
            myVar = self.load.variables.T
            myVarWithoutFirstTimes = myVar[k:last][:]
        else:
            self.timeInHours = time[k:]
            myVar = self.load.variables.T
            myVarWithoutFirstTimes = myVar[k:][:]

        self.variables = myVarWithoutFirstTimes.T
        self.load.variables = myVarWithoutFirstTimes.T

    # The difference with the readUserDEfined with firstConsideredTime=hours selectd is that loadFileNumpyis not
    # saving the whole memory in python which sometimes is out of space

    def readUserDefinedFilesYear(self, _nameFile, year, skypedLines=0):

        self.clean()

        self.userDefinedFileIsReaded = True

        nameUserDefinedFile = "%s\%s" % (self.path, _nameFile)

        self.load = load.loadBaseNumpy(nameUserDefinedFile)
        self.load.loadFileYear(year, splitArgument=None, verbose=True)

        self.name = self.load.namesVariables

        time = self.get("TIME")
        self.initialTime = time[0]
        self.timeStepUsed = (time[2] - time[1]) * 3600  # In seconds

        k = 0

        self.timeInHours = time[k:]
        myVar = self.load.variables.T
        myVarWithoutFirstTimes = myVar[k:][:]

        self.variables = myVarWithoutFirstTimes.T
        self.load.variables = myVarWithoutFirstTimes.T

    def readHourlyFiles(self, _nameFile, skypedLines=1, firstConsideredTime=8760):

        self.clean()

        self.hourlyFileIsReaded = True

        nameUserDefinedFile = os.path.join(self.path, _nameFile)

        print(nameUserDefinedFile)

        infile = open(nameUserDefinedFile, "r")

        lines = infile.readlines()[skypedLines:]

        k = 0
        for line in lines:
            # if the line is blank it breaks, so the maximum, minimum,etc are not readed.
            if not line.strip():
                #                print "readHourlyfiles BREAK at line:%s after line:%s" %(line,lines[k-1])
                break

            linesWithSign = line.split()

            if k == 0:
                for i in range(len(linesWithSign)):

                    self.name.append(linesWithSign[i])
            else:

                if len(linesWithSign) > 0:

                    if k == 1:
                        initialTime = linesWithSign[0]
                        if firstConsideredTime == None:
                            firstConsideredTime = initialTime
                        print("firstConsideredTime:%f" % firstConsideredTime)

                    if float(linesWithSign[0]) >= firstConsideredTime:  # if Time>firstConsideredTime
                        linesWithSign = [float(list_item) for list_item in linesWithSign]
                        self.variables.append(linesWithSign)
            k = k + 1

        infile.close()

    def readHourlyBuildingFile(self, _nameFile):

        self.clean()

        self.hourlyFileIsReaded = True

        nameUserDefinedFile = "%s\%s" % (self.pathWithoutTemp, _nameFile)

        infile = open(nameUserDefinedFile, "r")

        lines = infile.readlines()

        if len(lines) > (8760 * 2):
            firstConsideredTime = 8760
        else:
            firstConsideredTime = 0

        k = 0
        indexTime = 2  # two lines are used for name and unit

        for line in lines:
            # if the line is blank it breaks, so the maximum, minimum,etc are not readed.
            if not line.strip():
                #                print "readHourlyfiles BREAK at line:%s after line:%s" %(line,lines[k-1])
                break

            linesWithSign = line.split()

            if k == 0:
                for i in range(len(linesWithSign)):
                    if linesWithSign[i] != "|":
                        self.name.append(linesWithSign[i])
            #                       print linesWithSign[i]
            # to avoid reading units
            elif k >= indexTime:

                if len(linesWithSign) > 0:

                    time = float(linesWithSign[0])

                    if k == indexTime and time == 8016:
                        firstConsideredTime = 8760

                    if time >= firstConsideredTime:
                        var = []
                        for i in range(len(linesWithSign)):
                            if linesWithSign[i] != "|":
                                var.append(float(linesWithSign[i]))
                        self.variables.append(var)
            k = k + 1

        print("HOURLY DATA FROM BUILDING firstConsideredTime=%f" % firstConsideredTime)

        print(self.name)

        infile.close()

    def getIndexAndTagNames(self, lines, name, myYear, firstMonth):

        indexToStart = 0
        year = 0

        #         print "name:%s year:%d firstMonth:%s" % (name,myYear,firstMonth)
        #         print lines

        for k in range(len(lines)):

            splitLine = lines[k].split()

            #            print splitLine[0]

            try:
                # I read the labels
                if splitLine[0] == "Month":
                    #                    print "Reading Labels in monthly file"
                    for m in range(len(splitLine)):
                        name.append(splitLine[m])
            except:
                pass

            try:
                if splitLine[0] == firstMonth:
                    indexToStart = k
                    year = year + 1
            #                    print "First month found :%s indextoStart:%d year:%d" % (firstMonth,indexToStart,year)

            except:
                pass

            # I stop reading when the year of reading is the one defined.
            # -1 means last year so it reads until the end
            if year == myYear:
                #                print "year=myYear :%d k:%d"%(year,k)
                return indexToStart

        return indexToStart

    def readMonthlyFiles(self, _nameFile, firstMonth="January", myYear=-1):

        print("namefile %s" % _nameFile)

        self.clean()

        self.monthlyFileIsReaded = True

        # nameMonthlyFile = "%s\%s" % (self.path,_nameFile)
        nameMonthlyFile = os.path.join(self.path, _nameFile)

        infile = open(nameMonthlyFile, "r")
        lines = infile.readlines()

        # We take the index of the line for the last year of study

        self.name = []
        self.indexToStart = 0
        self.indexToStart = self.getIndexAndTagNames(lines, self.name, myYear, firstMonth)

        self.name = self.name[1:]  # I do not want the name Month

        self.numberOfVariables = len(self.name)
        self.variables = num.zeros(12 * self.numberOfVariables, dtype=float).reshape(self.numberOfVariables, 12)

        m = utils.getMonthNameIndex(firstMonth) - 1

        print("firstMonth=%s month:%d indexToStart:%d" % (firstMonth, m + 1, self.indexToStart))
        #        raise ValueError("")

        nMonth = 0
        for k in range(self.indexToStart, self.indexToStart + 12):
            m = m + 1

            if m > 11:
                m = 0

            try:
                splitLine = lines[k].split()

                #                print splitLine

                if utils.isMonthName(splitLine[0]) == False:
                    pass
                else:

                    # I think this is not necessary anymore !!!!!!!!!!!!!
                    if k == self.indexToStart and splitLine[0] == "December":  # Neglect the first December month
                        pass
                    else:

                        nMonth = nMonth + 1

                        #                        print "MONTH index :%d nMonth: %d" %(m,nMonth)

                        for i in range(len(self.name)):

                            self.variables[i][m] = splitLine[i + 1]
            #
            except:

                pass

        infile.close()

        if self.indexToStart == 0:
            print("Tag month not found in file:%s" % nameMonthlyFile)

        self.numberOfMonthsSimulated = nMonth

        print("Number of simulated months:%d yearConsidered:%d" % (self.numberOfMonthsSimulated, myYear))

    #        print self.variables

    #        raise ValueError("")

    #

    def readDeck(self, path, name):

        self.deck = deckTrnsys.DeckTrnsys(path, name)
        #        self.deck.setEliminateComments(True)
        #         self.deck.loadDeckWithNotes()
        self.deck.loadDeck()
        self.deckVariables = self.deck.getAllDataFromDeck()
        return self.deckVariables

    # def readAllTypes(self): #It should be deprecated. Done at building Deck level

    # TrnsysUnitsSorted, TrnsysTypesSorted, filesUsedInDdck, filesUnitUsedInDdck

    # deckUtils.readAllTypes(self.deck.linesDeck)
    # self.TrnsysTypes = self.deck.TrnsysTypes
    # self.TrnsysUnits = self.deck.TrnsysUnits
    # print ("types loaded")
    #
    #
    # def writeTrnsysTypesUsed(self,name,doSort=False): #It should be deprecated. Done at building deck level
    #
    #     if(doSort):
    #         iSort = num.argsort(self.TrnsysUnits)
    #
    #     lines = "UNIT\tTYPE\tName\n"
    #
    #     for i in range(len(self.TrnsysTypes)):
    #         if(doSort):
    #             k = iSort[i]
    #         else:
    #             k=i
    #         line="%4d\t%4d\t%s\n"%(self.TrnsysUnits[k],self.TrnsysTypes[k],self.deck.getTypeName(self.TrnsysTypes[k]))
    #         lines=lines+line
    #
    #     nameFile = os.path.join(self.path,name)
    #
    #     print ("Type file :%s created"%nameFile)
    #     outfile=open(nameFile,'w')
    #     outfile.writelines(lines)

    def getDataFromDeck(self, myName, typeValue="double", ifNotFoundEqualToZero=False):

        try:
            value = self.deck.getDataFromDeck(myName, typeValue)
            if value == None and ifNotFoundEqualToZero == True:
                return 0.0
            else:
                return value
        except:
            if ifNotFoundEqualToZero == True:
                return 0.0
            else:
                return None

        print(value)

    def getTypeFromUnit(self, myUnit):

        return self.deck.getTypeFromUnit(myUnit)

    #   Return the array with the seleted name

    def getFromVariables(self, name):

        for j in range(len(self.name)):

            if self.name[j].lower() == name.lower():
                #                 print "Im in j:%d nameVar:%s name:%s" % (j,self.namesVariables[j],name)
                return self.variables[j][:]
        return None

    def get(self, name, ifNotFoundEqualToZero=False):

        if self.userDefinedFileIsReaded:
            #            value =  self.getFromVariables(name)
            value = self.load.get(name)

        else:
            value = self.getFromList(name)

        try:
            if value == None and ifNotFoundEqualToZero == True and self.monthlyFileIsReaded == True:
                #                print name
                return num.zeros(12)

        except:
            return value

    def getFromList(self, name):

        for j in range(len(self.name)):

            #             print "name:%s name%s" % (self.name[j].lower(),name.lower())

            if self.name[j].lower() == name.lower():
                if self.monthlyFileIsReaded == True:
                    #                     print self.variables
                    return self.variables[j][:]
                else:
                    b = num.transpose(self.variables)
                    return b[j][:]

        return None

    def cleanMemory(self):

        self.load.cleanMemory()
