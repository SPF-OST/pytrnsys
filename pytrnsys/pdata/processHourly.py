# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
Class to process hourly files with names in the fist line and variables split with \t.
It can be changed is necessary.

Author : Dani Carbonell
Date   : 17.11.2017
"""

import pytrnsys.pdata.loadBaseNumpy as load
import pytrnsys.utils.utilsSpf as utils
import matplotlib.pyplot as plt
import numpy as num
import matplotlib
import pytrnsys.report.latexReport as latex


class processHourly:
    def __init__(self, _path, _name):

        self.path = _path
        self.name = _name

        nameWithoutExtension = self.name.split(".")[0]

        self.doc = latex.LatexReport(self.path, nameWithoutExtension)

        self.fileNameRead = self.path + "\\" + self.name

        self.sizeFigX = 10
        self.sizeFigY = 6

        self.sizeLegend = 15
        self.sizeAxis = 15

        self.yearlyFactor = 10

        self.myColorsIn = ["y", "0.75", "0.5", "#FF9933", "#CCFF33" "#CCFFFF" "g"]
        self.myColorsOut = ["b", "r", "m", "#FF9933", "g" "c" "#CCFF33" "#CCFFFF"]
        self.myColorsImb = "k"

        self.addLatexTables = ""

    def setFileNameToRead(self, name):

        self.name = name
        self.fileNameRead = self.path + "\\" + self.name

    def loadHourly(self):

        self.loadFile = load.loadBaseNumpy(self.fileNameRead)

        self.loadFile.loadFile(skypChar="#", skypedLines=0, splitArgument="\t")

    def get(self, name):
        self.loadFile.get(name)

    def calculateMonthly(self, varHourly):

        return utils.calculateMonthlyValues(varHourly)

    def calculateDaily(self, varHourly):

        return utils.calculateDaylyValuesFromHourly(varHourly)

    def plotHourly(self, var, myLabel, nameFile, plotJpg=False):

        N = 8760
        hours = num.arange(N)

        if len(var) != 8760:
            raise ValueError("plotHourly size of hourly is %d and must be 8760" % len(var))

        fig = plt.figure(1, figsize=(self.sizeFigX, self.sizeFigY))

        axes = fig.add_subplot(111)

        #        myLegend = []

        matplotlib.rcParams.update({"font.size": 17})

        axes.plot(hours, var, "-", color="b")

        #        leg = myLabel
        #        myLegend.append(leg)

        #        axes.legend(myLegend,bbox_to_anchor=(1.05,1),loc='lower right', borderaxespad=0.)
        #        axes.legend(myLegend,loc='upper left', borderaxespad=0.)

        axes.set_xlabel("Time [hour]", fontsize=self.sizeAxis)
        axes.set_ylabel(myLabel, fontsize=self.sizeAxis)

        namePdf = "%s.pdf" % nameFile
        nameWithPath = "%s\%s" % (self.path, namePdf)

        plt.savefig(nameWithPath)

        if plotJpg:
            name = "%s.jpg" % nameFile
            nameWithPath = "%s\%s" % (self.path, name)
            plt.savefig(nameWithPath)

        plt.close()

        return namePdf

    def plotMonthly(self, var, myLabel, nameFile, yearlyFactor, plotEmf=False):

        N = 13
        width = 0.35  # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        fig = plt.figure(1, figsize=(12, 8))

        plot = fig.add_subplot(111)

        # More processing is necessary if we want to have the yearly value at the 13 position as in Task44A38

        var13 = utils.addYearlyValue(var, yearlyFactor=yearlyFactor)

        plot.bar(ind - 0.5 * width, var13, width, color="b")

        plot.set_ylabel(myLabel, size=self.sizeAxis)

        box = plot.get_position()
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        #        plot.set_title('Title',size=20)
        plot.set_xticks(ind)
        plot.set_xticklabels(
            ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Year/10"),
            fontsize=10,
            rotation="45",
        )

        namePdf = "%s.pdf" % nameFile
        nameWithPath = "%s\%s" % (self.path, namePdf)

        plt.xlim([-0.5, 12.5])

        plt.savefig(nameWithPath)

        if plotEmf:

            nameEmf = "%s.jpg" % nameFile
            nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

            plt.savefig(nameEmfWithPath)

        plt.close()

        return namePdf

    # inVar(nVar,nMonth)
    def plotMonthlyBalance(
        self, inVar, outVar, legends, myLabel, nameFile, unit, yearlyFactor=0, useYear=False, plotEmf=False
    ):

        if useYear == True:

            nMonth = 13
            inVar13 = []
            outVar13 = []

            for i in range(len(inVar)):
                inVar13.append(utils.addYearlyValue(inVar[i], yearlyFactor=yearlyFactor))

            for i in range(len(outVar)):
                outVar13.append(utils.addYearlyValue(outVar[i], yearlyFactor=yearlyFactor))
        else:
            nMonth = 12
            inVar13 = inVar
            outVar13 = outVar

        width = 0.35  # the width of the bars
        ind = num.arange(nMonth)  # the x locations for the groups
        imbPlus = num.arange(nMonth)
        imbNeg = num.arange(nMonth)
        imb = num.arange(nMonth)

        fig = plt.figure(1, figsize=(12, 8))
        plot = fig.add_subplot(111)

        for m in range(nMonth):
            sumIn = 0.0
            for i in range(len(inVar13)):
                sumIn = sumIn + inVar13[i][m]

            sumOut = 0.0
            for i in range(len(outVar13)):
                sumOut = sumOut + outVar13[i][m]

            imbNeg[m] = max(sumIn - sumOut, 0)
            imbPlus[m] = min(sumIn - sumOut, 0)
            imb[m] = imbNeg[m] + imbPlus[m]

        bar = []
        for i in range(len(inVar13)):
            if i == 0:
                bar.append(plot.bar(ind - 0.5 * width, inVar13[i], width, color=self.myColorsIn[i]))
                addVar = inVar13[i]
            else:
                bar.append(plot.bar(ind - 0.5 * width, inVar13[i], width, color=self.myColorsIn[i], bottom=addVar))
                addVar = addVar + inVar13[i]

        plot.bar(ind - 0.5 * width, imbPlus, width, color=self.myColorsImb, bottom=addVar)

        for i in range(len(outVar13)):
            if i == 0:
                bar.append(plot.bar(ind - 0.5 * width, -outVar13[i], width, color=self.myColorsOut[i]))
                addVar = -outVar13[i]
            else:
                bar.append(plot.bar(ind - 0.5 * width, -outVar13[i], width, color=self.myColorsOut[i], bottom=addVar))
                addVar = addVar - outVar13[i]

        bar.append(plot.bar(ind - 0.5 * width, -imbNeg, width, color=self.myColorsImb, bottom=addVar))

        myLabel = myLabel + " [%s]" % unit
        plot.set_ylabel(myLabel, size=self.sizeAxis)

        box = plot.get_position()
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        #        plot.set_title('Title',size=20)
        plot.set_xticks(ind)
        plot.set_xticklabels(
            ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Year/10"),
            fontsize=self.sizeAxis,
            rotation="45",
        )

        allbar = []
        for b in bar:
            allbar.append(b[0])

        plot.legend(allbar, legends, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0, fontsize=self.sizeLegend)

        namePdf = "%s.pdf" % nameFile
        nameWithPath = "%s\%s" % (self.path, namePdf)

        if useYear == True:
            plt.xlim([-0.5, 13.5])
        else:
            plt.xlim([-0.5, 12.5])

        plt.savefig(nameWithPath)

        if plotEmf:

            nameEmf = "%s.jpg" % nameFile
            nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

            plt.savefig(nameEmfWithPath)

        plt.close()

        self.addLatexMonthlyData("", legends, unit, inVar, outVar, imb)

        return namePdf

    # Assumed that all units are equal
    def addLatexMonthlyData(self, caption, legends, myUnit, inVar, outVar, imb):

        nMonth = 12
        sizeBox = None
        # inVar(nVar,nMonth)
        names = [""]
        units = [""]

        for i in range(len(legends)):
            names.append(legends[i])
            units.append(myUnit)

        label = "any"
        lines = ""

        for i in range(nMonth):

            line = "%s\t" % utils.getMonthKey(i + 1)
            lines = lines + line

            for j in range(len(inVar)):
                line = "& %.1f\t" % (inVar[j][i])
                lines = lines + line

            for j in range(len(outVar)):
                line = "&%.1f\t" % (outVar[j][i])
                lines = lines + line

            line = "&%.1f\n \\\\" % (imb[i])
            lines = lines + line

        line = "\\hline\n"
        lines = lines + line
        lines = lines + line

        # Yearly data

        line = "Year\t"
        lines = lines + line

        for j in range(len(inVar)):
            line = "& %.1f\t" % (sum(inVar[j][:]))
            lines = lines + line

        for j in range(len(outVar)):
            line = "&%.1f\t" % (sum(outVar[j][:]))
            lines = lines + line

        line = "&%.1f\n \\\\" % (sum(imb))
        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=False)

        self.addLatexTables = self.addLatexTables + self.doc.lines
        self.doc.lines = ""

    def plotDaily(self, var, myLabel, nameFile, plotJpg=False):

        N = 365
        width = 0.1  # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        fig = plt.figure(1, figsize=(50, 8))

        plot = fig.add_subplot(111)

        plot.bar(ind - 0.5 * width, var, width, color="b")

        plot.set_ylabel(myLabel, size=25)

        box = plot.get_position()
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        #        plot.set_title('Title',size=20)
        #        plot.set_xticks(ind)
        #        plot.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Oct', 'Nov', 'Dec','Year/10'),fontsize=20)

        namePdf = "%s.pdf" % nameFile
        nameWithPath = "%s\%s" % (self.path, namePdf)

        plt.xlim([-0.5, 365])

        plt.savefig(nameWithPath)

        if plotJpg:

            nameJpg = "%s.jpg" % myLabel
            nameJpgWithPath = "%s\%s" % (self.path, nameJpg)

            plt.savefig(nameJpgWithPath)

        plt.close()

        return namePdf
