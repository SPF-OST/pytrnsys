# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
Class to load results file storing the names into self.namesVariables
and the results into self.variables. As a difference of the loadBaseNumpy the
results are stored into a normal list instead of numpy arrays.
Author : Dani Carbonell
Date   : 14.12.2012
"""

import string, os
import pytrnsys.pdata.processFiles as spfUtils


class loadBase:
    def __init__(self, _name):

        self.verbose = True

        # internal data

        self.variables = []
        self.namesVariables = []
        self.fileNameWithExtension = _name
        name = _name.split(".")
        self.fileName = name[0]
        self.rootPath = os.getcwd()

        self.numberOfDataPoints = 0
        self.numberOfVariables = 0

        self.skypedLines = 0
        self.readLabels = True

        self.splitArgument = "\t"

    def setSplitArgument(self, _split):
        self.splitArgument = _split

    def setSkypedLines(self, _number):
        self.skypedLines = _number

    def setVerbose(self, _verbose):
        self.verbose = _verbose

    # True of False
    def setReadLabels(self, _labels):
        self.readLabels = _labels

    def loadFile(self, skypChar, replaceChar):

        if self.verbose:
            print("Reading the file: %s " % self.fileNameWithExtension)

        infile = open(self.fileNameWithExtension, "r")
        lines = infile.readlines()

        if skypChar != None or replaceChar != None:
            if self.verbose:
                print("Purgin the input file")
            lines = spfUtils.purgueLines(lines, skypChar, replaceChar, self.skypedLines)

        k = 0
        if self.verbose:
            print("Copying Data from file to variables array")

        for line in lines:
            linesWithSign = line.split(self.splitArgument)

            if k == 0 and self.readLabels == True:
                for i in range(len(linesWithSign)):
                    self.namesVariables.append(linesWithSign[i])

            else:
                if len(linesWithSign) > 0:

                    linesWithSign = [float(list_item) for list_item in linesWithSign]
                    #                    The previous line does the same as is doing the next but faster
                    #                    for i in range(len(linesWithSign)):
                    self.variables.append(linesWithSign)

            #                    print linesWithSign

            k = k + 1

        self.numberOfDataPoints = len(self.variables)
        self.numberOfVariables = len(self.variables[0])

        # Controlling the two last characters of the last name in case \n or \t is found
        if self.readLabels == True:
            endingOfLastName = self.namesVariables[self.numberOfVariables - 1][-1:]
            if endingOfLastName == "\n" or endingOfLastName == "\t":
                # I erase the last two characters
                self.namesVariables[self.numberOfVariables - 1] = self.namesVariables[self.numberOfVariables - 1][:-1]

        if self.verbose:
            print("End of copying Data")
            print("numberOfDataPoints:%d numberOfVariables:%d\n", self.numberOfDataPoints, self.numberOfVariables)
        #        print self.namesVariables

        infile.close()
