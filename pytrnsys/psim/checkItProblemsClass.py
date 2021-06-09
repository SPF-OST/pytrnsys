# pylint: skip-file
# type: ignore

#!/usr/bin/env python

"""
Class for analysis of simulation data to facilitate debugging

Author : Dani Carbonell
Date : xx.xx.2018
ToDo :
"""


import os
import pytrnsys.psim.processTrnsysBase as processTrnsys
import pytrnsys.pdata.loadBaseNumpy as load
import pytrnsys.trnsys_util.LogTrnsys as LogTrnsys
import pytrnsys.trnsys_util.deckTrnsys as deckTrnsys


class checkIterationProblemsClass(processTrnsys.ProcessTrnsysBase):
    def __init__(self, _path, _name):

        processTrnsys.ProcessTrnsysBase.__init__(self, _path, _name)

    def loadStatus(self, _name):

        useOnlyOneYear = False
        firstConsideredTime = None
        year = False

        if year == False:
            self.readTrnsysFiles.readUserDefinedFiles(
                _name, firstConsideredTime=firstConsideredTime, useOnlyOneYear=useOnlyOneYear
            )
        else:
            self.readTrnsysFiles.readUserDefinedFilesYear(_name, year)

        if firstConsideredTime == None:
            self.firstConsideredTime = self.readTrnsysFiles.initialTime
        else:
            self.firstConsideredTime = firstConsideredTime

        self.nameVariables = self.readTrnsysFiles.name
        self.variables = self.readTrnsysFiles.load.variables
        self.nData = self.readTrnsysFiles.load.numberOfDataPoints

        if self.nameVariables[0] != "TIME":
            raise ValueError("File %s must have TIME as first variable" % _name)
        else:
            self.error = (self.variables[0][2] - self.variables[0][1]) * 0.1

    # This is for cases where the file has been generated with the standard process
    def readItProblemsFile(self, name):

        nameWithPath = os.path.join(self.outputPath, name)

        itFile = load.loadBaseNumpy(nameWithPath)
        itFile.loadFile(skypChar="!", splitArgument="\t")
        self.hourWhereItProblems = itFile.getByIndex(1)

    # Here we read the log file as done in the process class without having to print the file and to actually process
    # the whole case only for the it Problems
    def readItProblemsFromLog(self):

        log = LogTrnsys.LogTrnsys(self.outputPath, self.fileName)
        log.loadLog()
        log.getMyDataFromLog()
        log.getIteProblemsForEachMonth()

        self.hourWhereItProblems = log.hourWhereItProblems
        self.unitsItProblems = log.unitsInvolvedItProlems

        deck = deckTrnsys.DeckTrnsys(self.outputPath, self.fileName)
        deck.loadDeckWithNotes()
        deck.readAllTypes()

        self.namesUnitsItProblems = []
        for i in range(len(self.unitsItProblems)):
            listNames = []
            for j in range(len(self.unitsItProblems[i])):
                unit = int(self.unitsItProblems[i][j])
                for k in range(len(deck.TrnsysUnits)):
                    if deck.TrnsysUnits[k] == unit:
                        name = deck.getTypeName(deck.TrnsysTypes[k])
                        listNames.append(name)
            self.namesUnitsItProblems.append(listNames)

    def writeItFileWithSatus(self, name, limit=100):

        lines = ""
        line = "Number of iteration problems %f\n " % len(self.hourWhereItProblems)
        lines = lines + line

        if limit == None:
            limit = len(self.hourWhereItProblems)

        count = 0
        for t in range(len(self.hourWhereItProblems)):
            if count > limit:
                pass
            else:
                time = self.hourWhereItProblems[t]
                for i in range(self.nData):
                    # I assume fist variable is TIME

                    if abs(self.variables[0][i] - time) < self.error:  # error is the time step /10.
                        count = count + 1
                        line = "========================================\n"
                        lines = lines + line
                        line = "Iteration problem at :%f\nInvolved Types :" % time
                        lines = lines + line
                        for m in range(len(self.namesUnitsItProblems[t])):
                            line = "%s:%s\t" % (self.unitsItProblems[t][m], self.namesUnitsItProblems[t][m])
                            lines = lines + line
                        line = "\n"
                        lines = lines + line
                        line = "========================================\n"
                        lines = lines + line

                        for j in range(i - 1, i + 1, 1):
                            for k in range(len(self.variables)):
                                line = "%s=%8.3f\t" % (self.nameVariables[k], self.variables[k][j])
                                lines = lines + line
                            line = "\n"
                            lines = lines + line

        nameWithPath = os.path.join(self.outputPath, name)

        print("file Printed :%s" % nameWithPath)

        outfile = open(nameWithPath, "w")
        outfile.writelines(lines)
        outfile.close()

        print("End of printing errors in file:%s" % nameWithPath)
