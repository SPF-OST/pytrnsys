# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
Class to load results file storing the names into self.namesVariables
and the results into self.variables. Results are stored into numpy arrays.

Author : Dani Carbonell
Date   : 14.12.2012
"""

import string, os
import pytrnsys.pdata.processFiles as spfUtils
import numpy as np
import time
import datetime
import gc


class loadBaseNumpy:
    def __init__(self, _name):

        # internal data

        self.fileNameWithExtension = _name
        name = _name.split(".")
        self.fileName = name[0]

        #        self.rootPath=os.getcwd()
        #        print self.rootPath

        self.numberOfDataPoints = 0
        self.numberOfVariables = 0
        self.parseFileCreated = False
        self.removeBlankLines = False
        self.removeComments = False
        self.doubleLine = "=============loadNumpyBase========================="
        self.printWarning = False

    def changeName(self, _name):

        self.fileNameWithExtension = _name
        name = _name.split(".")
        self.fileName = name[0]

    def loadFile(
        self,
        skypChar=None,
        replaceChar=None,
        skypedLines=0,
        splitArgument=None,
        readLabels=True,
        verbose=True,
        cutBlank=False,
        typeVariables="float",
        fmt="",
        dateExt="",
    ):

        if verbose:
            print("%s" % self.doubleLine)
            print("Reading the file: %s " % self.fileNameWithExtension)

        infile = open(self.fileNameWithExtension, "r")
        lines = infile.readlines()[skypedLines:]

        # remove last line if its only a \n line

        if cutBlank == True:
            # File used to rad until a black line is found.
            # I want to avoid reading the max min etc... from TRNSYS hourly data

            j = len(lines) - 1

            for i in range(len(lines)):
                if verbose:
                    print("lines:%s size:%d" % (lines[i], len(lines[i])))
                try:
                    if lines[i].split("\t")[1] == "Maximum Instantaneous Values":
                        j = i - 2
                        if verbose:
                            print("BREAK j:%d lines:%s\n" % (j, lines[j]))
                        break
                except:
                    if verbose:
                        print("BLANK LINE:%d lines:%s\n" % (i, lines[i]))
                    j = i
                    break

            lines = lines[0:j]

        size = len(lines) - 1

        if len(lines[size]) == 1:
            lines = lines[:-1]
            size = len(lines) - 1

        if skypChar != None or replaceChar != None:
            if verbose:
                print("%s" % self.doubleLine)
                print("Purgin the input file")

            lines = spfUtils.purgueLines(lines, skypChar, replaceChar, removeBlankLines=self.removeBlankLines)

        if skypChar != None and self.removeComments:
            lines = spfUtils.purgueComments(lines, skypChar)

        if self.parseFileCreated:
            parsedFile = "%s.parse.dat" % self.fileName
            outfile = open(parsedFile, "w")
            outfile.writelines(lines)
            outfile.close()

        self.numberOfVariables = len(lines[0].split(splitArgument))
        #        self.numberOfDataPoints = len(lines)-1

        if readLabels == True:
            self.numberOfDataPoints = len(lines) - 1
        else:
            self.numberOfDataPoints = len(lines)

        # NumPy array
        if typeVariables == "float":
            self.variables = np.arange(self.numberOfVariables * self.numberOfDataPoints, dtype=float).reshape(
                self.numberOfVariables, self.numberOfDataPoints
            )
        else:
            self.variables = np.arange(self.numberOfVariables * self.numberOfDataPoints, dtype=object).reshape(
                self.numberOfVariables, self.numberOfDataPoints
            )

        self.namesVariables = np.arange(self.numberOfVariables, dtype=object)

        if verbose:
            print("%s" % self.doubleLine)
            print("numberOfDataPoints:%d numberOfVariables:%d" % (self.numberOfDataPoints, self.numberOfVariables))

        if verbose:
            print("%s" % self.doubleLine)
            print("Copying Data from file to variables array")

        startIndex = 0
        if readLabels == True:
            splittedLine = lines[0].split(splitArgument)
            for i in range(self.numberOfVariables):
                self.namesVariables[i] = splittedLine[i]
            startIndex = 1

            endingOfLastName = self.namesVariables[self.numberOfVariables - 1][-1:]
            if endingOfLastName == "\n" or endingOfLastName == "\t":
                # I erase the last two characters
                self.namesVariables[self.numberOfVariables - 1] = self.namesVariables[self.numberOfVariables - 1][:-1]

        k = 0
        for i in range(len(lines)):
            if i >= startIndex:
                splittedLine = lines[i].split(splitArgument)
                for j in range(self.numberOfVariables):
                    #                    print "j:%d var:%s" % (j,splittedLine[j])

                    try:
                        #                        [self.numberOfVariables][self.numberOfDataPoints]

                        self.variables[j][i - startIndex] = splittedLine[j]
                    except:

                        try:
                            self.variables[j][i - startIndex] = time.mktime(
                                datetime.datetime.strptime(dateExt + splittedLine[j], fmt).timetuple()
                            )

                        except:

                            if self.printWarning == True and j >= 1:
                                #                                print "i:%d j:%d len(lines):%d startIndex:%d"%(i,j,len(lines),startIndex)
                                print(
                                    "LoadBaseNumpy loadFile Not controlled number :",
                                    splittedLine[j],
                                    " for column j: ",
                                    j + 1,
                                    " line: ",
                                    i,
                                )
                                self.variables[j][i - startIndex] = 0.0

                k = k + 1

        if verbose:
            print("%s" % self.doubleLine)
            print("End of copying Data")

        infile.close()

    # It loads a file and saves a new one usig only the desired time.
    # This is usd for plotting easier and quicker parts of large files
    def loadFileAndCut(self, timeBegin, timeEnd, verbose=True, skypedLines=0, format="%Y.%m.%d %H:%M:%S.%f"):

        if verbose:
            print("%s" % self.doubleLine)
            print("Reading the file: %s " % self.fileNameWithExtension)
            print("Use timeBegin:%f timeEnd:%f" % (timeBegin, timeEnd))

        infile = open(self.fileNameWithExtension, "r")
        #        lines = infile.readlines()
        lines = infile.readlines()[skypedLines:]

        numberOfDataPoints = len(lines) - 1  # LABELS AT 1 position
        #

        self.numberOfVariables = len(lines[0].split())

        if verbose:
            print("numberOfVariables:%d nData:%d" % (self.numberOfVariables, numberOfDataPoints))
        #            raise ValueError("")

        self.namesVariables = np.arange(self.numberOfVariables, dtype=object)

        splittedLine = lines[0].split()

        for i in range(self.numberOfVariables):
            self.namesVariables[i] = splittedLine[i]

        endingOfLastName = self.namesVariables[self.numberOfVariables - 1][-1:]

        if endingOfLastName == "\n" or endingOfLastName == "\t":
            # I erase the last two characters
            self.namesVariables[self.numberOfVariables - 1] = self.namesVariables[self.numberOfVariables - 1][:-1]

        linesCut = []
        k = 1
        for i in range(numberOfDataPoints):
            splittedLine = lines[k].split()
            time = float(splittedLine[0])

            if time >= timeBegin and time <= timeEnd:
                linesCut.append(lines[k])
            k = k + 1

        self.numberOfDataPoints = len(linesCut)

        print("numberOfVariables:%d numberOfDataPoints:%d" % (self.numberOfVariables, self.numberOfDataPoints))
        # NumPy array
        self.variables = np.arange(self.numberOfVariables * self.numberOfDataPoints, dtype=float).reshape(
            self.numberOfVariables, self.numberOfDataPoints
        )

        if verbose:
            print("%s" % self.doubleLine)
            print("numberOfDataPoints:%d numberOfVariables:%d" % (self.numberOfDataPoints, self.numberOfVariables))

        if verbose:
            print("%s" % self.doubleLine)
            print("Copying Data from file to variables array")

        for i in range(self.numberOfDataPoints):

            splittedLine = linesCut[i].split()
            for j in range(self.numberOfVariables):
                try:
                    self.variables[j][i] = splittedLine[j]
                except:
                    try:
                        self.variables[j][i] = time.mktime(
                            datetime.datetime.strptime(splittedLine[j], "%Y.%m.%d %H:%M:%S.%f").timetuple()
                        )
                    except:

                        if self.printWarning == True and j >= 1:
                            #                                print "i:%d j:%d len(lines):%d startIndex:%d"%(i,j,len(lines),startIndex)
                            print(
                                "LoadBaseNumpy loadFile Not controlled number :",
                                splittedLine[j],
                                " for column j: ",
                                j + 1,
                                " line: ",
                                i,
                            )
                            self.variables[j][i] = 0.0

        if verbose:
            print("%s" % self.doubleLine)
            print("End of copying Data")

    # it loads a file specifiyng the desired year. TIME must be in the first column !!!!
    def loadFileYear(self, year, splitArgument=None, verbose=True):

        if verbose:
            print(self.doubleLine)
            print("Reading the file: %s " % self.fileNameWithExtension)

        infile = open(self.fileNameWithExtension, "r")
        linesTitle = infile.readlines()[0]
        infile.close()
        gc.collect()

        infile = open(self.fileNameWithExtension, "r")

        oneYearIndex = 262802  # I assume that time step is 2 minutes
        indexBegin = (year - 1) * oneYearIndex
        indexEnd = indexBegin + oneYearIndex

        lines = infile.readlines()[indexBegin:indexEnd]
        infile.close()
        gc.collect()

        # remove last line if its only a \n line
        #        size = len(lines)

        self.numberOfDataPoints = len(lines)

        print("indexBegin:%d indexEnd:%d nData:%d" % (indexBegin, indexEnd, self.numberOfDataPoints))

        #        if(skypChar != None or replaceChar != None):
        #            if(verbose):
        #                print self.doubleLine
        #                print "Purgin the input file"
        #
        #            lines = spfUtils.purgueLines(lines,skypChar,replaceChar,removeBlankLines=self.removeBlankLines)
        #
        #        if(skypChar != None and self.removeComments):
        #            lines  = spfUtils.purgueComments(lines,skypChar)
        #
        #        if(self.parseFileCreated):
        #            parsedFile = "%s.parse.dat" % self.fileName
        #            outfile=open(parsedFile,'w')
        #            outfile.writelines(lines)
        #            outfile.close()
        #
        self.numberOfVariables = len(linesTitle.split(splitArgument))
        self.namesVariables = np.arange(self.numberOfVariables, dtype=object)

        splittedLine = linesTitle.split(splitArgument)

        for i in range(self.numberOfVariables):
            self.namesVariables[i] = splittedLine[i]

        endingOfLastName = self.namesVariables[self.numberOfVariables - 1][-1:]

        if endingOfLastName == "\n" or endingOfLastName == "\t":
            # I erase the last two characters
            self.namesVariables[self.numberOfVariables - 1] = self.namesVariables[self.numberOfVariables - 1][:-1]

        # if(verbose):
        #     print self.namesVariables

        print("numberOfVariables:%d numberOfDataPoints:%d" % (self.numberOfVariables, self.numberOfDataPoints))
        # NumPy array
        self.variables = np.arange(self.numberOfVariables * self.numberOfDataPoints, dtype=float).reshape(
            self.numberOfVariables, self.numberOfDataPoints
        )

        if verbose:
            print("%s" % self.doubleLine)
            print("numberOfDataPoints:%d numberOfVariables:%d" % (self.numberOfDataPoints, self.numberOfVariables))

        if verbose:
            print("%s" % self.doubleLine)
            print("Copying Data from file to variables array")

        #        for i in range(indexBegin,indexEnd):
        for i in range(self.numberOfDataPoints):

            splittedLine = lines[i].split(splitArgument)
            for j in range(self.numberOfVariables):
                try:
                    self.variables[j][i] = splittedLine[j]
                except:
                    try:
                        self.variables[j][i] = time.mktime(
                            datetime.datetime.strptime(splittedLine[j], "%Y.%m.%d %H:%M:%S.%f").timetuple()
                        )
                    except:

                        if self.printWarning == True and j >= 1:
                            #                                print "i:%d j:%d len(lines):%d startIndex:%d"%(i,j,len(lines),startIndex)
                            print(
                                "LoadBaseNumpy loadFile Not controlled number :",
                                splittedLine[j],
                                " for column j: ",
                                j + 1,
                                " line: ",
                                i,
                            )
                            self.variables[j][i] = 0.0

        if verbose:
            print("%s" % self.doubleLine)
            print("End of copying Data")

    #        infile.close()

    def getByLine(self, indexLine):

        if indexLine <= 0:
            raise ValueError("indexLine:%d", indexLine, "should be > 0")

        return self.variables.T[indexLine - 1][:]

    # indexColumn for 1 to end..

    def getByIndex(self, indexColumn):

        if indexColumn <= 0:
            raise ValueError("indexColumn:%d", indexColumn, "should be > 0")

        return self.variables[indexColumn - 1][:]

    def get(self, name, useZero=False, verbose=False):

        verbose = True
        for j in range(self.numberOfVariables):
            #             if(verbose==True):
            #                 print "j:%d name(input):%s name(stored):%s" % (j,name,self.namesVariables[j])

            if self.namesVariables[j].lower() == name.lower():
                if verbose == True:
                    print("FOUND j:%d name(input):%s nameVar(stored):%s" % (j, name, self.namesVariables[j]))
                return self.variables[j][:]

        if verbose == True:
            print("NOT FOUND j:%d name:%s" % (j, name))

        return None

    def writeFile(self, name, verbose=False, printNames=True):

        if verbose:
            print("%s" % self.doubleLine)
            print("Writting output file : %s" % name)

        # for print as the input file readed !!
        X = self.variables.T

        myHeader = ""

        if printNames:
            for i in range(len(self.namesVariables)):

                if i == len(self.namesVariables) - 1:
                    myHeader = myHeader + "%s" % self.namesVariables[i]
                else:
                    myHeader = myHeader + "%s\t" % self.namesVariables[i]

                if verbose:
                    print(self.namesVariables[i])

        footer = ""
        np.savetxt(name, X, fmt="%+.8e", delimiter=" ", newline="\n", header=myHeader, footer=footer, comments="# ")

    def cleanMemory(self):

        del self.variables
        del self.namesVariables


if __name__ == "__main__":

    name = "ValidationIceStorage-TRNSYSInputSmall.dat"
    #

    path = "D:\MyCalculations\Trnsys\IceStorage\PilotPlantKinderGarten"

    myFile = "%s\%s" % (path, name)

    pilot = loadBaseNumpy(myFile)

    pilot.loadFile(skypChar=None, verbose=True, skypedLines=4)

    print(pilot.get("TPcmExp1"))

    #    print pilot.getTranspose("TPcmExp1")

    print("END OF LOADBASENUMPY")

    myFileOut = "%s\%s-End.dat" % (path, name.split(".")[0])

    pilot.writeFile(myFileOut, verbose=True)
