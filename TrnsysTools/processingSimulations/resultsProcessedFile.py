#!/usr/bin/env python

"""
Read the -results file from each simulation and allows to process them
Author : Dani Carbonell
Date   : 09.05.2018
ToDo   :
"""

import os
import shutil
import string
import TrnsysTools.reporting.latexReport as latex
import numpy as num
import bigIceTrnsysClass as ice
import matplotlib.pyplot as plt

class ResultsProcessedFile():
    """
    class for analysis of simulation data to facilitate debugging
    """

    def __init__(self, _path):

        self.path = _path
        self.cases = []

        self.filteredfolder = [".gle"]


    def get(self, name, resultList):
        for lines in resultList:
            if (lines.split("\t")[0] == name):
                return string.atof(lines.split("\t")[1])

    def readResultsData(self):

        fileName = []
        pathFolder = self.path

        self.fileName = [name for name in os.listdir(pathFolder) if os.path.isdir(pathFolder + "\\" + name)]

        for name in self.fileName:
            for i in range(len(self.filteredfolder)):
                if (name == self.filteredfolder[i]):
                    del self.fileName[i]

        self.results = []

        lines = ""

        for name in self.fileName:

            dictRes = {}

            nameWithPath = os.path.join(pathFolder, "%s\\%s-results.dat" % (name, name))
            resultFile = open(nameWithPath, 'r')
            resultList = resultFile.readlines()
            for lines in resultList:
                split = lines.split("\t")
                if(len(split)==2):
                    try:
                        dictRes[split[0]] = string.atof(split[1][:-1])
                    except:
                        dictRes[split[0]] = split[1][:-1]

                elif(len(split)>12):
                    monthVal = split[1:12]
                    dictRes[split[0]] = monthVal
                else:
                    try:
                        dictRes[split[0]] = string.atof(split[1])
                    except:
                        dictRes[split[0]] = split[1]

            resultFile.close()

            self.results.append(dictRes)

    #to be moved to a child class since it is case dependent.
    def plotSPfVsAcolViceDeprecated(self):

        spf  = []
        aCol = []
        vIce = []

        for i in range(len(self.results)):
            spf.append(self.results[i]["SPFdis"])
            aCol.append(self.results[i]["Aunc"])
            vIce.append(self.results[i]["VIce"])

        spfSorted = [x for y, x in sorted(zip(aCol,spf))]
        aColSorted = sorted(aCol)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax1 = plt.subplot()
        ax1.plot(aColSorted,spfSorted)
        ax1.set(ylabel='$SPF_{SHP+}$', xlabel='$A_{col}$')
        ax1.grid()

        extension = "pdf"
        figureName = "spfVsAcol"

        self.spfVsAcolPdf = self.path + "\\" + figureName + ".%s" % extension

        fig.savefig(self.spfVsAcolPdf)


    def createLatexSimulationReport(self):

        self.plotT = False

        self.plots()

        nameLatex = "ResultsFile"

        doc = latex.LatexReport(self.path,nameLatex)
        doc.setCleanMode(True)

        doc.setTitle("Processed results")
        doc.setSubTitle("%s"%self.path.split("\\")[-1])

        doc.addBeginDocument()

        doc.lines = doc.lines + self.tableLines

        # doc.addPlot(self.imbSpfPdf,"","",12)
        # doc.addPlot(self.imbItPdf,"","",12)

        doc.addEndDocumentAndCreateTexFile()
        doc.executeLatexFile()



