# pylint: skip-file
# type: ignore

#!/usr/bin/env python

"""
Read the -results file from each simulation and allows to process them
Author : Dani Carbonell
Date   : 09.05.2018
ToDo   :
"""

import json
import os
import pathlib as pl

import matplotlib.pyplot as plt

import pytrnsys.report.latexReport as latex


class ResultsProcessedFile:
    """
    class for analysis of simulation data to facilitate debugging
    """

    def __init__(self, _path):

        self.path = _path
        self.cases = []
        self.filteredfolder = [".gle"]

    def get(self, name, resultList):
        for lines in resultList:
            if lines.split("\t")[0] == name:
                return float(lines.split("\t")[1])

    def readResultsData(self, resultType="dat", completeFolder=True, fileNameList=None):

        pathFolder = self.path

        if completeFolder:
            self.fileName = [
                p.relative_to(pathFolder)
                for p in pl.Path(pathFolder).iterdir()
                if p.is_dir() and p.name[0] != "." and p.name not in self.filteredfolder
            ]
        else:
            self.fileName = fileNameList

        self.results = []

        for name in self.fileName:

            dictRes = {}

            if resultType == "dat":
                nameWithPath = os.path.join(pathFolder, "%s\\%s-results.dat" % (name, name))

                resultFile = open(nameWithPath, "r")
                resultList = resultFile.readlines()
                for lines in resultList:
                    split = lines.split("\t")
                    if len(split) == 2:
                        try:
                            dictRes[split[0]] = float(split[1][:-1])
                        except:
                            dictRes[split[0]] = split[1][:-1]

                    elif len(split) > 12:
                        monthVal = split[1:12]
                        dictRes[split[0]] = monthVal
                    else:
                        try:
                            dictRes[split[0]] = float(split[1])
                        except:
                            dictRes[split[0]] = split[1]

                resultFile.close()

            elif resultType == "json":
                nameWithPath = os.path.join(pathFolder, "%s\\%s-results.json" % (name, name))

                with open(nameWithPath) as json_file:
                    dictRes = json.load(json_file)

            self.results.append(dictRes)

    # to be moved to a child class since it is case dependent.
    def plotSPfVsAcolViceDeprecated(self):

        spf = []
        aCol = []
        vIce = []

        for i in range(len(self.results)):
            spf.append(self.results[i]["SPFdis"])
            aCol.append(self.results[i]["Aunc"])
            vIce.append(self.results[i]["VIce"])

        spfSorted = [x for y, x in sorted(zip(aCol, spf))]
        aColSorted = sorted(aCol)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax1 = plt.subplot()
        ax1.plot(aColSorted, spfSorted)
        ax1.set(ylabel="$SPF_{SHP+}$", xlabel="$A_{col}$")
        ax1.grid()

        extension = "pdf"
        figureName = "spfVsAcol"

        self.spfVsAcolPdf = self.path + "\\" + figureName + ".%s" % extension

        fig.savefig(self.spfVsAcolPdf)

    def createLatexSimulationReport(self):

        self.plotT = False

        self.plots()

        nameLatex = "ResultsFile"

        doc = latex.LatexReport(self.path, nameLatex)
        doc.setCleanMode(True)

        doc.setTitle("Processed results")
        doc.setSubTitle("%s" % self.path.split("\\")[-1])

        doc.addBeginDocument()

        doc.lines = doc.lines + self.tableLines

        # doc.addPlot(self.imbSpfPdf,"","",12)
        # doc.addPlot(self.imbItPdf,"","",12)

        doc.addEndDocumentAndCreateTexFile()
        doc.executeLatexFile()
