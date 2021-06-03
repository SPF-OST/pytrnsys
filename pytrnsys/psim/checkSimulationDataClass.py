# pylint: skip-file
# type: ignore

#!/usr/bin/env python

"""
Class for analysis of simulation data to facilitate debugging.
A child class of this should be defined to print a table with custom data.
Iteration problems and heat imbalances should be included and others can be custom

Author : Dani Carbonell
Date   : 2018
ToDo :
"""

import os
import shutil
import pytrnsys.report.latexReport as latex
import matplotlib.pyplot as plt
import pytrnsys.psim.resultsProcessedFile as results
import logging

logger = logging.getLogger("root")


class checkSimulationDataClass(results.ResultsProcessedFile):
    def __init__(self, _path):

        results.ResultsProcessedFile.__init__(self, _path)
        self.version = "checkSimulationData v1 2019-01-22"

        self.path = _path

        self.cases = []

        self.dataPath = self.path

        self.filteredfolder = [".gle"]

    def findFailedSimulations(self):
        """find simulations that failed based on the log file"""
        path = self.path
        cases = [name for name in os.listdir(path) if os.path.isdir(path + "\\" + name)]
        word = "Fatal"
        failedCases = []
        successfulCases = []
        for case in cases:
            # resultFile = open(path + "\\" + case + "\\temp\\BUILDING_MO.Prt", "r")
            try:
                resultFile = open(path + "\\" + case + "\\" + case + ".log", "r")
                resultList = resultFile.readlines()
                resultFile.close()
                k = 0

                for line in resultList:
                    words = line.split()
                    for i in words:
                        if i == word:
                            k += 1
                if k != 1:
                    failedCases.append(case + "\n")
                    logger.warning(case + " failed, number of Fatal errors = " + str(k - 1))

                else:
                    successfulCases.append(case + "\n")

            except:
                failedCases.append(case + "\n")

        outfile = open(path + "\\FailedCases.txt", "w")
        outfile.writelines(failedCases)
        outfile.close

        outfile = open(path + "\\SuccessfulCases.txt", "w")
        outfile.writelines(successfulCases)
        outfile.close

        self.failedCases = failedCases
        return failedCases

    def moveFailedCases(self):

        """
        first folder is not transfered as a whole folder, but only the files... -> seems to work now?
        """

        dstFolder = self.path + "-failed"

        if not os.path.isdir(dstFolder):
            os.mkdir(dstFolder)

        for case in self.failedCases:
            src = self.path + "\\" + case[:-1]
            dst = dstFolder
            shutil.move(src, dst)

            logger.debug("moved failed cases from " + self.path + " to " + dstFolder)

    def checkNumberOfMonthsSimulated(self):

        dataPath = self.path

        cases = [name for name in os.listdir(dataPath) if os.path.isdir(dataPath + "\\" + name)]
        numberOfMonths = []
        for case in cases:
            resultFile = open(dataPath + "\\" + case + "\\" + case + "-results.dat", "r")
            resultList = resultFile.readlines()
            resultFile.close
            for line in resultList:
                if line.split("\t")[0] == "numberOfMonthSimulated":
                    numberOfMonths.append(line.split("\t")[1])
        return numberOfMonths

    def doTableErrors(self, doc, sortBy="spf", useLineForGroups=False):
        pass

    def plots(self):

        spfSorted = [x for y, x in sorted(zip(self.imb, self.spf))]
        imbSorted = sorted(self.imb)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax1 = plt.subplot()
        ax1.plot(spfSorted, imbSorted)
        ax1.set(ylabel="$Q_{imb}$ [\%]", xlabel="$SPF_{SHP+}$")
        ax1.grid()

        extension = "pdf"
        figureName = "Imb_vs_spf"

        imbSpfPdf = self.path + "\\" + figureName + ".%s" % extension

        fig.savefig(imbSpfPdf)

        self.imbSpfPdf = figureName + ".%s" % extension

        itSorted = [x for y, x in sorted(zip(self.imb, self.itProblems))]
        imbSorted = sorted(self.imb)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax1 = plt.subplot()
        ax1.plot(imbSorted, itSorted)
        ax1.set(xlabel="$Q_{imb}$ [\%]", ylabel="$It_{prob}$")
        ax1.grid()

        extension = "pdf"
        figureName = "Imb_vs_it"

        imbItPdf = self.path + "\\" + figureName + ".%s" % extension
        fig.savefig(imbItPdf)

        self.imbItPdf = figureName + ".%s" % extension

    def createLatexSimulationReport(self, sortBy="it"):

        self.plotT = False

        self.plots()

        nameLatex = "SimulationsErrorCheck"

        doc = latex.LatexReport(self.path, nameLatex)
        doc.setCleanMode(True)

        doc.setTitle("Errors in simulations")
        doc.setSubTitle("%s" % self.path.split("\\")[-1])

        doc.addBeginDocument()

        self.doTableErrors(doc, sortBy=sortBy)
        self.doTableErrors(doc, sortBy="imb")

        doc.addPlot(self.imbSpfPdf, "", "", 12)
        doc.addPlot(self.imbItPdf, "", "", 12)

        doc.addEndDocumentAndCreateTexFile()
        doc.executeLatexFile()
