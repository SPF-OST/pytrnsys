# pylint: skip-file
# type: ignore

"""
Author : Dani Carbonell
Date   : 14.12.2012
"""

import string, os
import pytrnsys.pdata.processFiles as spfUtils
import numpy as np


class loadInputFile:
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
        self.doubleLine = "=============loadInputFile========================="

    def loadFile(self, skypChar=None, replaceChar=None, skypedLines=0, splitArgument=None, verbose=True, indexToRead=1):

        if verbose:
            print("%s" % self.doubleLine)
            print("Reading the file: %s " % self.fileNameWithExtension)

        infile = open(self.fileNameWithExtension, "r")
        lines = infile.readlines()[skypedLines:]

        if skypChar != None or replaceChar != None:
            if verbose:
                print("%s" % self.doubleLine)
                print("Purgin the input file")

            lines = spfUtils.purgueLines(
                lines, skypChar, replaceChar, removeBlankLines=self.removeBlankLines, removeBlankSpaces=True
            )

        if skypChar != None and self.removeComments:
            lines = spfUtils.purgueComments(lines, skypChar)

        if self.parseFileCreated:
            parsedFile = "%s.parse.dat" % self.fileName
            outfile = open(parsedFile, "w")
            outfile.writelines(lines)
            outfile.close()

        self.numberOfVariables = len(lines)

        self.variables = np.arange(self.numberOfVariables, dtype=float)
        self.namesVariables = np.arange(self.numberOfVariables, dtype=object)

        for i in range(self.numberOfVariables):
            split = lines[i].split(splitArgument)
            self.namesVariables[i] = split[0]
            #            print split[0]
            self.variables[i] = split[indexToRead]

        infile.close()

    def get(self, name, ifNotFoundEqualToZero=False):

        for j in range(self.numberOfVariables):

            #             print "j:%d nameVar:%s name:%s" % (j,self.namesVariables[j],name)

            if self.namesVariables[j].lower() == name.lower():
                #                 print "Im in j:%d nameVar:%s name:%s" % (j,self.namesVariables[j],name)
                return self.variables[j]
        if ifNotFoundEqualToZero:
            return 0.0
        else:
            return None

    def cleanMemory(self):

        del self.variables
        del self.namesVariables
