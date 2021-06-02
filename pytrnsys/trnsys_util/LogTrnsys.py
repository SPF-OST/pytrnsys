# pylint: skip-file
# type: ignore

#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob
import string, shutil
import pytrnsys.pdata.processFiles as spfUtils
import pytrnsys.utils.utilsSpf as utils
import numpy as num
import logging

logger = logging.getLogger("root")
# stop propagting to root logger
logger.propagate = False


class LogTrnsys:
    def __init__(self, _path, _name):

        self.fileName = _name  # _name.split('.')[0]
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

        # True is not working becasue it looks for files in the D:\MyPrograms\Trnsys17 as local path
        self.useRelativePath = False

        if self.useRelativePath == False:
            self.filesOutputPath = self.pathOutput

        self.eliminateComments = False
        self.numberOfFailedIt = 0
        self.loadLog()

    def loadLog(self):

        logger.debug("nameLog:%s" % self.nameLog)

        try:
            infile = open(self.nameLog, "r")
            lines = infile.readlines()

            skypChar = None  # ['*'] #This will eliminate the lines starting with skypChar
            replaceChar = None  # [',','\''] #This characters will be eliminated, so replaced by nothing

            self.lines = spfUtils.purgueLines(
                lines, skypChar, replaceChar, removeBlankLines=True, removeBlankSpaces=False
            )

            infile.close()

        except:
            self.lines = None
            self.numberOfFailedIt = 0

    def getCalculationTime(self):

        sentence = "Total TRNSYS Calculation Time"

        # I increase the number of back lines to read becasue if we add the time for each type it is writen after the calculation time
        for i in range(len(self.lines)):

            split = self.lines[i].split(":")

            try:
                if split[0].strip() == sentence:
                    ntime = split[1].strip()
                    time = float(ntime.split()[0]) / 60.0
                    return time
            except:
                pass

        return -99

    def checkFatalErrors(self):

        sentence = "Total Fatal Errors"

        for i in range(len(self.lines)):

            split = self.lines[i].split(":")

            try:
                if split[0].strip() == sentence:
                    nNumberOfFatalErrors = split[1].strip()
                    numberOfFatalErrors = int(nNumberOfFatalErrors.split()[0])
                    return numberOfFatalErrors
            except:
                pass

        return -99

    def logFatalErrors(self):

        sentence = "*** Fatal Error at time"

        for i in range(len(self.lines)):

            split = self.lines[i].split(":")

            try:
                if split[0].strip() == sentence:
                    return self.lines[i : i + 5]

                    # nNumberOfFatalErrors = split[1].strip()
                    # numberOfFatalErrors = int(nNumberOfFatalErrors.split()[0])
                    # return numberOfFatalErrors
            except:
                pass

        return False

    def checkWarnings(self):

        sentence = "Total Warnings"

        for i in range(len(self.lines) - 1, len(self.lines) - 500, -1):

            split = self.lines[i].split(":")

            try:
                if split[0].strip() == sentence:
                    nNumberOfWarnings = split[1].strip()
                    numberOfWarnings = int(nNumberOfWarnings.split()[0])
                    return numberOfWarnings
            except:
                pass

        return -99

    def getMyDataFromLog(self):

        sentence = "The simulation failed to converge during"

        try:
            for i in range(len(self.lines)):

                split = self.lines[i].split(sentence)

                try:

                    self.numberOfFailedIt = split[1].replace("%", "\%")
                    logger.debug(self.numberOfFailedIt)

                except:
                    pass

        except:
            self.numberOfFailedIt = -99
            logger.warning("LOG FILE NOT FOUND")

        return None

    def getIteProblemsForEachMonth(self):

        sentence = "TRNSYS Message    441"
        sentenceUnit = "Reported information  : UNITS:"

        iteMonth = num.zeros(12)

        self.hourWhereItProblems = []
        self.unitsInvolvedItProlems = []

        try:
            for i in range(len(self.lines)):

                mysplit = self.lines[i].split(sentence)

                try:
                    if mysplit[1] != None:

                        hourOfYear = float(self.lines[i - 3].split(":")[1])
                        self.hourWhereItProblems.append(hourOfYear)

                        units = self.lines[i + 1].split(sentenceUnit)[1]
                        self.unitsInvolvedItProlems.append(list(units.split()))

                        #                       print "hourOfYear:%f " % (hourOfYear)
                        (n, d, h) = utils.getMonthIndexByHourOfYear(hourOfYear)
                        n = n - 1
                        iteMonth[n] = iteMonth[n] + 1
                #                       print "ite in month:%d = %d"% (n,iteMonth[n])

                except:
                    pass

        except:
            logger.warning("LOG FILE NOT FOUND")

        return iteMonth

    def writeFileWithItErrors(self, nameFile="ItProblems.dat"):

        # if(self.printItProblemsFile==True):

        lines = ""
        line = "!This file shows the time where it problems occur\n"
        lines += line
        line = "!time [h] day itProblem\n"
        lines += line

        for i in range(len(self.hourWhereItProblems)):
            line = "%f\t%f\t%d\n" % (self.hourWhereItProblems[i], self.hourWhereItProblems[i] / 24.0, 1)
            lines += line

        nameItProblem = self.path + nameFile

        logger.warning("It problems printed in %s" % nameItProblem)

        infile = open(nameItProblem, "w")
        lines = infile.writelines(lines)
        infile.close()

    def checkSimulatedHours(self):
        hourInterval = []

        prtFiles = glob.glob(os.path.join(self.path, "**/*.Prt"), recursive=True)
        for prtFile in prtFiles:
            if "HR" in os.path.split(prtFile)[-1]:
                with open(prtFile) as f_in:
                    hourlyFile = f_in.readlines()
                break

        indexFirstHour = -1
        firstFound = False
        lastHour = -1
        for i in range(0, len(hourlyFile)):
            lineBeginning = hourlyFile[i].split("\t")[0]
            if "Period" in lineBeginning:
                indexFirstHour = i + 1
            if i == indexFirstHour:
                firstFound = True
                try:
                    hourInterval.append(int(lineBeginning))
                except:
                    hourInterval.append(None)
            elif firstFound:
                try:
                    lastHour = int(lineBeginning)
                except:
                    hourInterval.append(lastHour)
                    break

        return hourInterval
