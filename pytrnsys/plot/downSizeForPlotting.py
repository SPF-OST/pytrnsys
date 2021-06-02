# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
Class to down resize time step data in order to plot faster with less data points
It does not interpolate, it just eliminates points depending on the new time step chosen.
Author : Dani Carbonell
Date   : 14.12.2012
"""

import sys, time
import getopt
import numpy as num
import pytrnsys.pdata.loadBaseNumpy as load
import logging

logger = logging.getLogger("root")


class DownSizeForPlotting:
    def __init__(self, _path, _name):

        self.name = _name.split(".")[0]
        self.path = _path
        self.fileNameWithPath = "%s\\%s" % (_path, _name)

        self.load = load.loadBaseNumpy(self.fileNameWithPath)

        self.modifyFirstColumTime = False

        self.doubleLine = "==========DownSizeExp======================="

    def downSize(self, timeStepOld, timeStepNew, skypedLines=0):

        self.timeStepOld = timeStepOld
        self.timeStepNew = timeStepNew
        self.skypLine = int(self.timeStepNew / self.timeStepOld)

        self.load.loadFile(skypChar=["#", "!"], readLabels=False, skypedLines=skypedLines)
        #        self.load.loadFile(skypChar=None,readLabels=False,skypedLines=1)

        self.variablesDownSized = []

        if self.modifyFirstColumTime:
            self.timeOld = self.load.variables[:][0] * 3600

            tBegin = self.timeOld[0]

            self.timeOld = self.timeOld - tBegin

        count = 0
        for i in range(self.load.numberOfDataPoints):

            count = count + 1
            if count == self.skypLine or i == 1:
                count = 0
                allLine = self.load.variables.T[i][:]

                if self.modifyFirstColumTime:

                    allLine[0] = (self.timeOld[i] + tBegin) / 3600.0

                self.variablesDownSized.append(allLine)

    #                print  self.doubleLine
    #                print "TIME:%f is whole. Used for new time step data" % (self.timeOld[i])

    def cut(self, _timeBegin, _timeEnd, timeStepOld, timeStepNew, skypedLines=0):

        self.timeStepOld = timeStepOld
        self.timeStepNew = timeStepNew
        self.skypLine = int(self.timeStepNew / self.timeStepOld)

        logger.debug("timeBegin:%f timeEnd:%f" % (_timeBegin, _timeEnd))

        self.load.loadFileAndCut(_timeBegin, _timeEnd, skypedLines)

        self.variablesDownSized = []

        count = 0
        for i in range(self.load.numberOfDataPoints):

            count = count + 1
            if count == self.skypLine or i == 1:
                count = 0
                allLine = self.load.variables.T[i][:]

                self.variablesDownSized.append(allLine)

    def recalculateColumn(self, column, factor):

        for k in range(len(column)):
            for j in range(len(self.variablesDownSized[0])):
                if j + 1 == column[k]:
                    logger.info("RECALCULATE COLUMN :%d with factor :%f" % (column[k], factor[k]))
                    for i in range(len(self.variablesDownSized)):
                        self.variablesDownSized[i][j] = self.variablesDownSized[i][j] * factor[k]

    def createDataFile(self):
        # I include here TinIce and tOutIce because the test switch from ice mode to deice and therefore tIn and tOut are exchanged

        header = ""
        myName = "%s/%s-DownSized.dat" % (self.path, self.name)

        line = "Down sized tool for printing purposes\n"
        header = header + line
        line = "File processed with DownSizeExp.py at %s\n" % (time.strftime("%c"))
        header = header + line
        line = "Author:DCarbonell. Version v1 \n"
        header = header + line

        header = header + line
        formatPrint = "%-10.5f"

        num.savetxt(myName, self.variablesDownSized, fmt=formatPrint, header=header, comments="! ")
