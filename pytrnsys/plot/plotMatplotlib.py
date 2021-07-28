# pylint: skip-file
# type: ignore

# -*- coding: utf-8 -*-
#!/usr/bin/python

"""
Class to plot using matplotlib

Author : Daniel Carbonell
Date   : 05-05-2018
ToDo :
"""

import matplotlib.pyplot as plt
import numpy as num
import matplotlib
import pytrnsys.utils.utilsSpf as utils
import time
import pytrnsys.plot.plotGle as gle
import os, subprocess
import logging
import pandas as pd
from scipy.optimize import curve_fit

logger = logging.getLogger("root")


class PlotMatplotlib:
    """Plot TRNSYS Results with Matplotlib"""

    def __init__(self, language="en", stylesheet="word.mplstyle", extensionPlot="pdf"):
        self.language = language
        self.root = os.path.dirname(os.path.abspath(__file__))
        if stylesheet in plt.style.available:
            self.stylesheet = stylesheet
        else:
            self.stylesheet = os.path.join(self.root, r".\\stylesheets", stylesheet)
        plt.style.use(self.stylesheet)
        self.extensionPlot = extensionPlot
        self.yearlyFactor = 10
        self.setDefaultColors()

    def setExtensionPlot(self, extension):
        self.extensionPlot = extension

    def setDefaultColors(self):

        myColorsIn = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        self.myColorsIn = myColorsIn + myColorsIn + myColorsIn + myColorsIn
        self.myColorsOut = self.myColorsIn[::-1]

        self.myColorsImb = "k"

        self.colorGLE = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
            "lightblue",
            "slateblue",
            "khaki",
            "darkorange",
            "firebrick",
            "deepskyblue",
            "gray50",
        ]

        # "#1f77b4" #blue
        # "#ff7f0e" #orange
        # "#2ca02c" #green
        # "#d62728" #red
        # "#9467bd" #violet
        # "#8c564b" #brown
        # "#e377c2" #pink
        # "#7f7f7f" #grey
        # "#bcbd22" #yellow
        # "#17becf" #cyan

        #        self.myColorsIn  = ['y','0.75','r','#FF9933','#CCFF33','#CCFFFF','g']

    #        self.myColorsOut = ['b','m','#FF9933','g','c','#CCFF33','#CCFFFF''r']

    def setPath(self, _path):

        self.path = _path
        self.gle = gle.PlotGle(_path)

    #    var = [1,....,12]
    def plotMonthly(
        self,
        var,
        myLabel,
        nameFile,
        yearlyFactor,
        useYearlyFactorAsValue=False,
        startMonth=1,
        myTitle=None,
        plotEmf=False,
        printData=False,
    ):
        """
        Plot Monthly Values

        Parameters
        ---------
        var : ndarray
            1D array of length 12 (not containing a yearly value) or 13 (containing a yearly value)
        myLabel : str
            Label of the y-Axis
        nameFile : str
            Name of the plot file to be saved
        yearlyFactor : float
            Value of the yearly Factor
        startMonth : obj:'int', optional
            Starting month of the Plot (1= January, 12=December), Default is 1
        myTitle : str, optional
            Title of the Plot
        plotEmf : bool, optional
            Plot as Enhanced Meta File
        printData : bool, optional
            Additionaly print data in a .dat-File

        Returns
        -------
        str
            Path of Pdf created.

        """
        move = 0
        N = 13
        width = 0.35  # the width of the bars
        ind = num.arange(N)  # the x locations for the groups
        with plt.style.context(self.stylesheet):
            fig = plt.figure()

            plot = fig.add_subplot(111)

            # More processing is necessary if we want to have the yearly value at the 13 position as in Task44A38

            if startMonth != 1:
                if len(var) == 13:
                    yearly = var[12]

                var = utils.reorganizeMonthlyFile(var, startMonth)

                if len(var) == 13:
                    var[12] = yearly

            if len(var) == 12:
                var13 = utils.addYearlyValue(var, yearlyFactor=yearlyFactor)
            elif len(var) == 13:
                var13 = var

            if useYearlyFactorAsValue:
                var13[12] = yearlyFactor

            plot.bar(ind - move * width, var13, width)

            plot.set_ylabel(myLabel)

            box = plot.get_position()
            plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

            if myTitle != None:
                plot.set_title(myTitle, size=20)

            plot.set_xticks(ind)

            if self.language == "en":
                if yearlyFactor == 1:
                    yearTag = "Year"
                else:
                    yearTag = "Year/%d" % yearlyFactor
            if self.language == "de":
                if yearlyFactor == 1:
                    yearTag = "Jahr"
                else:
                    yearTag = "Jahr/%d" % yearlyFactor

            monthSequence = utils.getMonthNameSequence(startMonth, language=self.language)
            monthSequence.append(yearTag)

            plot.set_xticklabels(monthSequence, rotation="45")

            plot.axes.grid(which="major", axis="y")

            namePdf = "%s.pdf" % nameFile
            nameWithPath = "%s\%s" % (self.path, namePdf)

            logger.debug("plotMonthly name:%s" % nameWithPath)

            plt.xlim([-0.5, 12.5])

            plt.savefig(nameWithPath)

            if plotEmf:
                nameEmf = "%s.emf" % nameFile
                nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

                self._plot_as_emf(plt, filename=nameEmfWithPath)

            plt.close()

            if printData == True:

                lines = ""
                line = "!nMonth %s\n" % (myLabel)
                lines = lines + line

                for i in range(N):
                    line = "%d\t%f\n" % (i + 1, var13[i])
                    lines = lines + line

                nameWithPath = "%s\%s.dat" % (self.path, nameFile)
                outfile = open(nameWithPath, "w")
                outfile.writelines(lines)
                outfile.close()

                legends = []
                legends.append(myLabel)

        #            self.gle.getBarPlot(nameFile,nameWithPath,myLabel,xnames=monthSequence)
        #            self.gle.getBarBalancePlot(nameFile,nameWithPath,myLabel,1,0,xnames=monthSequence)

        return namePdf

    def plotMonthlyDf(
        self,
        var,
        myLabel,
        nameFile,
        yearlyFactor,
        defMonths,
        useYearlyFactorAsValue=False,
        myTitle=None,
        plotEmf=False,
        printData=False,
    ):
        """
        Plot Monthly Values

        Parameters
        ---------
        var : ndarray
            1D array of length 12 (not containing a yearly value) or 13 (containing a yearly value)
        myLabel : str
            Label of the y-Axis
        nameFile : str
            Name of the plot file to be saved
        yearlyFactor : float
            Value of the yearly Factor
        defMonth : obj:'int', optional
            Starting month of the Plot (1= January, 12=December), Default is 1
        myTitle : str, optional
            Title of the Plot
        plotEmf : bool, optional
            Plot as Enhanced Meta File
        printData : bool, optional
            Additionaly print data in a .dat-File

        Returns
        -------
        str
            Path of Pdf created.

        """
        move = 0
        N = 13
        width = 0.35  # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        with plt.style.context(self.stylesheet):
            fig = plt.figure()

            plot = fig.add_subplot(111)

            if len(var) == 12:
                var13 = utils.addYearlyValue(var, yearlyFactor=yearlyFactor)
            elif len(var) == 13:
                var13 = var

            if useYearlyFactorAsValue:
                var13[12] = yearlyFactor

            plot.bar(ind - move * width, var13, width)

            plot.set_ylabel(myLabel)

            box = plot.get_position()
            plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

            if myTitle != None:
                plot.set_title(myTitle, size=20)

            plot.set_xticks(ind)

            if yearlyFactor == 1 or useYearlyFactorAsValue == True or len(var) == 13:
                yearTag = "Year"
            else:
                yearTag = "Year/%d" % yearlyFactor

            monthSequence = defMonths.copy()
            monthSequence.append(yearTag)

            plot.set_xticklabels(monthSequence, rotation="45")

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            logger.debug("plotMonthlyDf name:%s" % nameWithPath)

            plt.xlim([-0.5, 12.5])

            plt.savefig(nameWithPath)

            if plotEmf:
                nameEmf = "%s.emf" % nameFile
                nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

                self._plot_as_emf(plt, filename=nameEmfWithPath)

            plt.close()

            if printData == True:

                lines = ""
                line = "!nMonth %s\n" % (myLabel)
                lines = lines + line

                for i in range(N):
                    line = "%d\t%f\n" % (i + 1, var13[i])
                    lines = lines + line

                nameWithPath = "%s\%s.dat" % (self.path, nameFile)
                outfile = open(nameWithPath, "w")
                outfile.writelines(lines)
                outfile.close()

                legends = []
                # legends.append("$%s$"%myLabel)
                legends.append("%s" % myLabel)

                self.gle.getBarPlot(nameFile, nameWithPath, legends, xnames=monthSequence)

            #            self.gle.getBarBalancePlot(nameFile,nameWithPath,myLabel,1,0,xnames=monthSequence)

        return namePdf

    # If the yearly value needs to be set from outside, use avector with 13 positions as input and the yearly value will be unchanged.

    def plotMonthly2Bar(
        self,
        var1,
        var2,
        legends,
        myLabel,
        nameFile,
        yearlyFactor,
        startMonth=1,
        myTitle=None,
        plotEmf=False,
        showMonths=False,
        ylim=False,
    ):

        move = 0.5
        if showMonths == False:
            N = 13
            showMonths = [i for i in range(13)]
        else:
            N = len(showMonths)
        width = 0.35  # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        with plt.style.context(self.stylesheet):
            fig = plt.figure()

            plot = fig.add_subplot(111)

            # More processing is necessary if we want to have the yearly value at the 13 position as in Task44A38
            if startMonth != 1:
                if len(var1) == 13:
                    yearly = var1[12]

                var1 = utils.reorganizeMonthlyFile(var1, startMonth)

                if len(var1) == 13:
                    var1[12] = yearly

                if len(var2) == 13:
                    yearly = var2[12]

                var2 = utils.reorganizeMonthlyFile(var2, startMonth)

                if len(var2) == 13:
                    var2[12] = yearly

            if len(var1) == 12:
                var13_1 = utils.addYearlyValue(var1, yearlyFactor=yearlyFactor)
            else:
                var13_1 = var1

            if len(var2) == 12:
                var13_2 = utils.addYearlyValue(var2, yearlyFactor=yearlyFactor)
            else:
                var13_2 = var2

            bar1 = plot.bar(ind - move * width, var13_1[showMonths], width)
            bar2 = plot.bar(ind + move * width, var13_2[showMonths], width)

            plot.set_ylabel(myLabel)

            box = plot.get_position()
            plot.set_position([box.x0, box.y0, box.width * 0.8 / 12 * N, box.height])

            plot.legend([bar1, bar2], legends, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
            if ylim:
                plot.set_ylim(ylim)
            if myTitle != None:
                plot.set_title(myTitle)

            plot.set_xticks(ind)

            plot.axes.grid(which="major", axis="y")

            if self.language == "en":
                if yearlyFactor == 1:
                    yearTag = "Year"
                else:
                    yearTag = "Year/%d" % yearlyFactor
            if self.language == "de":
                if yearlyFactor == 1:
                    yearTag = "Jahr"
                else:
                    yearTag = "Jahr/%d" % yearlyFactor

            monthSequence = utils.getMonthNameSequence(startMonth, language=self.language)
            monthSequence.append(yearTag)

            plot.set_xticklabels([monthSequence[i] for i in showMonths], rotation="45")

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            logger.debug("plotMonthly name:%s" % nameWithPath)

            plt.xlim([-0.5, N + 1.5])

            plt.savefig(nameWithPath)

            if plotEmf:
                nameEmf = "%s.emf" % nameFile
                nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

                self._plot_as_emf(plt, filename=nameEmfWithPath)

            plt.close()

        return namePdf

    def plotMonthlyNBar(
        self,
        inVar,
        legends,
        myLabel,
        nameFile,
        yearlyFactor,
        defMonths,
        useYear=False,
        myTitle=None,
        plotEmf=False,
        showMonths=False,
        ylim=False,
    ):
        """
        Plot Monthly Values of N different data series

        Parameters
        ---------
        legends : list of str
            list of strings containing N entries for the legend
        var1 : ndarray
            2D array of length Nx12 (not containing a yearly value) or Nx13 (containing a yearly value)
            or list of 1D-arrays
        myLabel : str
            Label of the y-Axis
        nameFile : str
            Name of the plot file to be saved
        yearlyFactor : float
            Value of the yearly Factor
        startMonth : obj:'int', optional
            Starting month of the Plot (1= January, 12=December), Default is 1
        myTitle : str, optional
            Title of the Plot
        plotEmf : bool, optional
            Plot as Enhanced Meta File
        showMonths : list of int, optional
            list with numbers of which months to plot (0=january), Default is False (shows all files)
        ylims : [lower,upper], optional
            lower and upper limit for y axi, Default is False (automatic limits by matplotlib)

        Returns
        -------
        str
            Path of Pdf created.

        """

        move = 0
        if yearlyFactor == 1:
            yearTag = "Year"
        else:
            yearTag = "Year/%d" % yearlyFactor

        monthSequence = defMonths.copy()
        variables = inVar.copy()

        if useYear == True:

            nMonth = 13
            var13 = []
            monthSequence.append(yearTag)

            for i in range(len(variables)):
                var13.append(utils.addYearlyValue(variables[i], yearlyFactor=yearlyFactor))

            if showMonths == False:
                showMonths = [i for i in range(13)]
                nMonth = 13
            else:
                nMonth = len(showMonths)
        else:
            nMonth = 12
            var13 = variables
            if showMonths == False:
                showMonths = [i for i in range(12)]
            else:
                nMonth = len(showMonths)

        bars = []
        fig = plt.figure()
        plot = fig.add_subplot(111)
        ind = num.arange(len(showMonths))  # the x locations for the groups
        if showMonths:
            numberOfMonths = len(showMonths)
        else:
            showMonths = 12
        width = 0.5 / (len(inVar))  # the width of the bars
        for i, values in enumerate(inVar):

            bar = plot.bar(ind - 0.25 + i * width + width / 2, [var13[i][j] for j in showMonths], width)
            bars.append(bar)

        plot.set_ylabel(myLabel)

        box = plot.get_position()
        plot.set_position([box.x0, box.y0 + box.height * 0.05, box.width * 0.8 / 12 * numberOfMonths, box.height])

        plot.legend(bars, legends, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)
        plot.tick_params(axis="y")

        if myTitle != None:
            plot.set_title(myTitle)

        plot.set_xticks(ind)

        if self.language == "en":
            if yearlyFactor == 1:
                yearTag = "Year"
            else:
                yearTag = "Year/%d" % yearlyFactor
        if self.language == "de":
            if yearlyFactor == 1:
                yearTag = "Jahr"
            else:
                yearTag = "Jahr/%d" % yearlyFactor

        plot.set_xticklabels([monthSequence[i] for i in showMonths], rotation="45")

        namePdf = "%s.%s" % (nameFile, self.extensionPlot)
        nameWithPath = "%s\%s" % (self.path, namePdf)

        logger.debug("plotMonthly name:%s" % nameWithPath)

        plt.xlim([-0.5, numberOfMonths + 1.5])

        plt.savefig(nameWithPath)

        if plotEmf:
            nameEmf = "%s.emf" % nameFile
            nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

            self._plot_as_emf(plt, filename=nameEmfWithPath)

        plt.close()

        return namePdf

    def _plot_as_emf(self, figure, **kwargs):

        try:
            inkscape_path = kwargs.get("inkscape", "C://Program Files//Inkscape//inkscape.exe")
            filepath = kwargs.get("filename", None)

            if filepath is not None:
                path, filename = os.path.split(filepath)
                filename, extension = os.path.splitext(filename)

                svg_filepath = os.path.join(path, filename + ".svg")
                emf_filepath = os.path.join(path, filename + ".emf")

                figure.savefig(svg_filepath, format="svg")

                subprocess.call([inkscape_path, svg_filepath, "--export-emf", emf_filepath])
                os.remove(svg_filepath)
        except:
            logger.warning("EMF not created, please install inkscape")

    def plotMonthlyBalance(
        self,
        inVar,
        outVar,
        legends,
        myLabel,
        nameFile,
        unit=False,
        startMonth=1,
        printImb=True,
        yearlyFactor=1,
        useYear=False,
        plotEmf=False,
        printData=False,
        showMonths=False,
        ylims=False,
    ):
        """

        Parameters
        ----------
        inVar : ndarray
            1D array of length 12 (not containing a yearly value) or 13 (containing a yearly value)
        outVar : ndarray
            1D array of length 12 (not containing a yearly value) or 13 (containing a yearly value)
        legends : list of str
                    list of strings containing N entries for the legend
        myLabel : str
                    Label of the y-Axis
        nameFile : str
                    Name of the plot file to be saved
        unit : str
            unit for the y-axis (deprecated)
        startMonth : int, optional
            Starting month of the Plot (1= January, 12=December), Default is 1
        printImb : bool, optional
            Print the monthly imbalance between in and out variables, Default is True
        yearlyFactor : float, optional
            Value for the reduction of the yearly sum to make it fit in the y-axis, Default is 1
        useYear : bool, optional
            Show the yearly sum, Default is false
        plotEmf : bool, optional
            Print the plot as an emf (requres an installation of inkscape), Default is False
        printData : bool, optional
            Print the data to a .dat file, Default is false
        showMonths : list of int, optional
            list with numbers of which months to plot (0=january), Default is False (shows all files)
        ylims : [lower,upper], optional
            lower and upper limit for y axi, Default is False (automatic limits by matplotlib)

        Returns
        -------
        str
            Path of Pdf created.
        """
        move = 0

        if startMonth != 1:
            if months != False:
                months[i] = utils.reorganizeMonthlyFile(months, startMonth)

            for i in range(len(inVar)):
                inVar[i] = utils.reorganizeMonthlyFile(inVar[i], startMonth)

            for i in range(len(outVar)):
                outVar[i] = utils.reorganizeMonthlyFile(outVar[i], startMonth)

        if useYear == True:

            nMonth = 13
            inVar13 = []
            outVar13 = []

            for i in range(len(inVar)):
                #                print "useYear i:%d (inVar below)"%i
                #                print inVar[i]

                inVar13.append(utils.addYearlyValue(inVar[i], yearlyFactor=yearlyFactor))

            #                print "useYear i:%d (inVar13 below)"%i
            #                print inVar13[i]

            for i in range(len(outVar)):
                outVar13.append(utils.addYearlyValue(outVar[i], yearlyFactor=yearlyFactor))
            if showMonths == False:
                showMonths = [i for i in range(13)]
                nMonth = 13
            else:
                nMonth = len(showMonths)
        else:
            nMonth = 12
            inVar13 = inVar
            outVar13 = outVar
            if showMonths == False:
                showMonths = [i for i in range(12)]
            else:
                nMonth = len(showMonths)

        width = 0.35  # the width of the bars
        ind = num.arange(len(showMonths))  # the x locations for the groups
        imbPlus = num.zeros(nMonth)
        imbNeg = num.zeros(nMonth)
        imb = num.zeros(nMonth)

        with plt.style.context(self.stylesheet, after_reset=True):
            fig = plt.figure()
            plot = fig.add_subplot(111)

            for j, m in enumerate(showMonths):
                sumIn = 0.0
                for i in range(len(inVar13)):
                    sumIn = sumIn + inVar13[i][m]
                #                if(m==3):
                #                print "month:%d i:%d sumIn:%f inVar:%f"%(m,i,sumIn,inVar13[i][m])

                sumOut = 0.0
                for i in range(len(outVar13)):
                    sumOut = sumOut + outVar13[i][m]

                #                print "month:%d i:%d sumOut:%f outVar:%f"%(m,i,sumOut,outVar13[i][m])

                imbNeg[j] = max(sumIn - sumOut, 0)
                imbPlus[j] = max(sumOut - sumIn, 0)
                imb[j] = imbNeg[j] + imbPlus[j]
            #            if(m==3):
            #                print "month:%d imbNeg:%f imbPos:%f imb:%f"%(m,imbNeg[m],imbPlus[m],imb[m])

            bar = []

            addVar = [0 for i in range(len(showMonths))]
            for i in range(len(inVar13)):
                #            print "i:%d colorsIn:%s"%(i,self.myColorsIn[i])
                bar.append(
                    plot.bar(ind - move * width, inVar13[i][showMonths], width, color=self.myColorsIn[i], bottom=addVar)
                )
                addVar = addVar + inVar13[i][showMonths]
            #            if(i==0):
            #                bar.append(plot.bar(ind-0.5*width, inVar13[i], width, color=self.myColorsIn[i]))
            #                addVar = inVar13[i]
            #            else:
            #                bar.append(plot.bar(ind-0.5*width, inVar13[i], width, color=self.myColorsIn[i],bottom=addVar))
            #                addVar = addVar+inVar13[i]

            if printImb == True:
                plot.bar(ind - move * width, imbPlus, width, color=self.myColorsImb, bottom=addVar)

            for i in range(len(outVar13)):
                if i == 0:
                    bar.append(plot.bar(ind - move * width, -outVar13[i][showMonths], width, color=self.myColorsOut[i]))
                    addVar = -outVar13[i][showMonths]
                else:
                    bar.append(
                        plot.bar(
                            ind - move * width, -outVar13[i][showMonths], width, color=self.myColorsOut[i], bottom=addVar
                        )
                    )
                    addVar = addVar - outVar13[i][showMonths]

            if printImb == True:
                bar.append(plot.bar(ind - move * width, -imbNeg, width, color=self.myColorsImb, bottom=addVar))
            if unit:
                myLabel = myLabel + "[%s]" % unit
            plot.set_ylabel(myLabel)

            box = plot.get_position()
            plot.set_position([box.x0, box.y0 + 0.05 * box.height, box.width * 0.7 / 12 * nMonth, box.height])

            #        plot.set_title('Title',size=20)
            plot.set_xticks(ind)
            if self.language == "en":
                if yearlyFactor == 1:
                    yearTag = "Year"
                else:
                    yearTag = "Year/%d" % yearlyFactor
            if self.language == "de":
                if yearlyFactor == 1:
                    yearTag = "Jahr"
                else:
                    yearTag = "Jahr/%d" % yearlyFactor

            monthSequence = utils.getMonthNameSequence(1, language=self.language)
            monthSequence.append(yearTag)

            plot.set_xticklabels([monthSequence[i] for i in showMonths], rotation="45")

            plot.axes.grid(which="major", axis="y")

            allbar = []
            for b in bar:
                allbar.append(b[0])

            plot.legend(allbar, legends, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            logger.debug("PlotMonthlyBalance name:%s" % nameWithPath)

            if useYear == True:
                plot.set_xlim([-0.5, 13.5])
            else:
                plot.set_xlim([-0.5, len(showMonths) + 1.5])
            if ylims:
                plot.set_ylim(ylims)
            fig.savefig(nameWithPath)

            if plotEmf:

                nameEmf = "%s.emf" % nameFile
                nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

                self._plot_as_emf(fig, filename=nameEmfWithPath)

            plt.close()

            if printData == True:

                lines = ""
                line = "!nMonth\t"
                lines = lines + line

                for label in legends:
                    line = "%s\t" % label
                    lines = lines + line
                line = "\n"
                lines = lines + line

                # inVar(nVar,nMonth)

                for j in range(nMonth):
                    line = "%d\t" % (j + 1)
                    lines = lines + line

                    sumVar = 0.0
                    for i in range(len(inVar13)):

                        sumVar = sumVar + inVar13[i][j]
                        line = "%.2f\t" % sumVar
                        lines = lines + line

                    sumVar = 0
                    for i in range(len(outVar13)):

                        sumVar = sumVar - outVar13[i][j]
                        line = "%.2f\t" % sumVar
                        lines = lines + line

                    line = "\n"
                    lines = lines + line

                nameWithPath = "%s\%s.dat" % (self.path, nameFile)
                outfile = open(nameWithPath, "w")
                outfile.writelines(lines)
                outfile.close()

                self.gle.getBarBalancePlot(
                    nameFile, nameWithPath, legends, len(inVar13), len(outVar13), xnames=monthSequence
                )

        return namePdf

    def plotMonthlyBalanceDf(
        self,
        inVar,
        outVar,
        legends,
        myLabel,
        nameFile,
        unit,
        defMonths,
        printImb=True,
        yearlyFactor=1,
        useYear=False,
        plotEmf=False,
        printData=False,
        showMonths=False,
        ylims=None,
        title="",
        style="",
    ):
        """
        Plots monthly energy balance of system input variables and system output variables.

        Parameters
        ----------
        inVar : ndarray
            1D array of length 12 containing monthly values of system input variables
        outVar : ndarray
            1D array of length 12 containing monthly values of system output variables
        legends : list of str
            list of strings containing N entries for the legend. Input variables go first Output vairables go second)
        myLabel : str
            Label of the y-Axis
        nameFile : str
            Name of the plot file to be saved
        defMonths : list of str
            list of strings with the month names
        printImb : bool, optional
            Print the monthly imbalance between in and out variables, Default is True
        yearlyFactor : float, optional
            Value for the reduction of the yearly sum to make it fit in the y-axis, Default is 1
        useYear : bool, optional
            Show the yearly sum, Default is false
        plotEmf : bool, optional
            Print the plot as an emf (requres an installation of inkscape), Default is False
        printData : bool, optional
            Print the data to a .dat file, Default is false
        showMonths : list of int, optional
            list with numbers of which months to plot (0=january), Default is False (shows all files)
        ylims : [lower,upper], optional
            lower and upper limit for y axi, Default is False (automatic limits by matplotlib)

        Returns
        -------
        str
            Path of Pdf created.
        """

        move = 0
        if yearlyFactor == 1:
            yearTag = "Year"
        else:
            yearTag = "Year/%d" % yearlyFactor

        monthSequence = defMonths.copy()
        variables = inVar.copy()
        for var in outVar:
            variables.append(-var)
        if useYear == True:

            nMonth = 13
            variables13 = []
            monthSequence.append(yearTag)

            for i in range(len(variables)):

                variables13.append(utils.addYearlyValue(variables[i], yearlyFactor=yearlyFactor))

            if showMonths == False:
                showMonths = [i for i in range(13)]
                nMonth = 13
            else:
                nMonth = len(showMonths)
        else:
            nMonth = 12
            variables13 = variables
            if showMonths == False:
                showMonths = [i for i in range(12)]
            else:
                nMonth = len(showMonths)

        data = num.array(variables13)
        if printImb:
            data = num.append(data, [-num.sum(data[:, showMonths], axis=0)], axis=0)

        cumulated_data = self._get_cumulated_array(data, min=0)
        cumulated_data_neg = self._get_cumulated_array(data, max=0)

        row_mask = data < 0
        cumulated_data[row_mask] = cumulated_data_neg[row_mask]
        data_stack = cumulated_data

        width = 0.35  # the width of the bars
        ind = num.arange(len(showMonths))  # the x locations for the groups

        if style == "relative":
            positiveSum = num.zeros(nMonth)
            for variable in variables13:
                positiveSum += num.where(variable > 0.0, variable, 0.0)

        with plt.style.context(self.stylesheet):
            fig = plt.figure()
            plot = fig.add_subplot(111)
            bar = []

            # tempColors = ['r','orange','yellow','brown','c','b','g','grey']

            for i in range(len(variables13)):
                if style == "relative":
                    test = variables13[i][showMonths] / positiveSum
                    bar.append(
                        plot.bar(
                            ind - move * width,
                            variables13[i][showMonths] / positiveSum * 100.0,
                            width,
                            color=self.myColorsIn[i],  # color=tempColors[i],
                            bottom=data_stack[i] / positiveSum * 100.0,
                        )
                    )
                else:
                    try:
                        bar.append(
                            plot.bar(
                                ind - move * width,
                                variables13[i][showMonths],
                                width,
                                color=self.myColorsIn[i],
                                bottom=data_stack[i],
                            )
                        )
                    except:
                        bar.append(plot.bar(ind - move * width, variables13[i][showMonths], width, bottom=data_stack[i]))

            if printImb:
                if style == "relative":
                    bar.append(
                        plot.bar(
                            ind - move * width,
                            data[-1][showMonths] / positiveSum * 100.0,
                            width,
                            color="k",
                            bottom=data_stack[-1] / positiveSum * 100.0,
                        )
                    )
                else:
                    bar.append(
                        plot.bar(ind - move * width, data[-1][showMonths], width, color="k", bottom=data_stack[-1])
                    )

            if style == "relative":
                myLabel = myLabel + " [%]"
            else:
                myLabel = myLabel + " [%s]" % unit

            plot.set_ylabel(myLabel)
            box = plot.get_position()
            plot.set_position([box.x0, box.y0, box.width * 0.8 / 12 * nMonth, box.height])
            plot.set_xticks(ind)
            plot.set_xticklabels([monthSequence[i] for i in showMonths], rotation="45")

            allbar = []
            for b in bar:
                allbar.append(b[0])

            lgd = plot.legend(allbar, legends, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

            if title != "":
                plot.set_title(title)

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            logger.debug("PlotMonthlyBalance name:%s" % nameWithPath)

            if useYear == True:
                plt.xlim([-0.5, 13.5])
            else:
                plt.xlim([-0.5, len(showMonths) + 1.5])

            if ylims is not None:
                plt.ylim(ylims)

            plt.savefig(nameWithPath, bbox_extra_artists=(lgd,), bbox_inches="tight")

            if plotEmf:
                nameEmf = "%s.png" % nameFile
                nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

                self._plot_as_emf(fig, filename=nameEmfWithPath)

            plt.close()

            if style == "relative":
                printData = False

            if printData == True:

                lines = ""
                line = "!nMonth\t"
                lines = lines + line

                for label in legends:
                    line = "%s\t" % label
                    lines = lines + line
                line = "\n"
                lines = lines + line

                # variables(nVar,nMonth)

                for j in range(nMonth):
                    line = "%d\t" % (j + 1)
                    lines = lines + line
                    sumVar = 0.0
                    sumVarNeg = 0.0
                    for i in range(len(variables13)):
                        if variables13[i][j] >= 0:
                            sumVar = sumVar + variables13[i][j]
                            line = "%.2f\t" % sumVar

                        else:
                            sumVarNeg += variables[i][j]
                            line = "%.2f\t" % sumVarNeg

                        lines = lines + line

                    line = "\n"
                    lines = lines + line

                nameWithPath = "%s\%s.dat" % (self.path, nameFile)
                outfile = open(nameWithPath, "w")
                outfile.writelines(lines)
                outfile.close()

                self.gle.getBarBalancePlot(nameFile, nameWithPath, legends, len(variables13), 0, xnames=monthSequence)

        return namePdf

    def plotDailyBalanceDf(
        self,
        inVar,
        outVar,
        dayLabel,
        legends,
        myLabel,
        myXLabel,
        nameFile,
        unit,
        printImb=True,
        useYear=False,
        plotEmf=False,
        printData=False,
        showMonths=False,
        ylims=None,
        title="",
        style="",
    ):
        """
        Plots daily energy balance for selected days of system input variables and system output variables.

        Parameters
        ----------
        inVar : ndarray
            1D array of length 12 containing monthly values of system input variables
        outVar : ndarray
            1D array of length 12 containing monthly values of system output variables
        legends : list of str
            list of strings containing N entries for the legend. Input variables go first Output vairables go second)
        myLabel : str
            Label of the y-Axis
        nameFile : str
            Name of the plot file to be saved
        defMonths : list of str
            list of strings with the month names
        printImb : bool, optional
            Print the monthly imbalance between in and out variables, Default is True
        yearlyFactor : float, optional
            Value for the reduction of the yearly sum to make it fit in the y-axis, Default is 1
        useYear : bool, optional
            Show the yearly sum, Default is false
        plotEmf : bool, optional
            Print the plot as an emf (requres an installation of inkscape), Default is False
        printData : bool, optional
            Print the data to a .dat file, Default is false
        showMonths : list of int, optional
            list with numbers of which months to plot (0=january), Default is False (shows all files)
        ylims : [lower,upper], optional
            lower and upper limit for y axi, Default is False (automatic limits by matplotlib)

        Returns
        -------
        str
            Path of Pdf created.
        """

        move = 0

        variables = inVar.copy()
        for var in outVar:
            variables.append(-var)

        nDays = len(dayLabel)
        showDays = [i for i in range(nDays)]

        data = num.array(variables)
        if printImb:
            data = num.append(data, [-num.sum(data[:, showDays], axis=0)], axis=0)

        cumulated_data = self._get_cumulated_array(data, min=0)
        cumulated_data_neg = self._get_cumulated_array(data, max=0)

        row_mask = data < 0
        cumulated_data[row_mask] = cumulated_data_neg[row_mask]
        data_stack = cumulated_data

        width = 0.35  # the width of the bars
        ind = num.arange(len(showDays))  # the x locations for the groups

        if style == "relative":
            positiveSum = num.zeros(nDays)
            for variable in variables:
                positiveSum += num.where(variable > 0.0, variable, 0.0)

        with plt.style.context(self.stylesheet):
            fig = plt.figure()
            plot = fig.add_subplot(111)
            bar = []

            # tempColors = ['r','orange','yellow','brown','c','b','g','grey']

            for i in range(len(variables)):
                if style == "relative":
                    test = variables[i][showDays] / positiveSum
                    bar.append(
                        plot.bar(
                            ind - move * width,
                            variables[i][showDays] / positiveSum * 100.0,
                            width,
                            color=self.myColorsIn[i],  # color=tempColors[i],
                            bottom=data_stack[i] / positiveSum * 100.0,
                        )
                    )
                else:
                    try:
                        bar.append(
                            plot.bar(
                                ind - move * width,
                                variables[i][showDays],
                                width,
                                color=self.myColorsIn[i],
                                bottom=data_stack[i],
                            )
                        )
                    except:
                        bar.append(plot.bar(ind - move * width, variables[i][showDays], width, bottom=data_stack[i]))

            if printImb:
                if style == "relative":
                    bar.append(
                        plot.bar(
                            ind - move * width,
                            data[-1][showDays] / positiveSum * 100.0,
                            width,
                            color="k",
                            bottom=data_stack[-1] / positiveSum * 100.0,
                        )
                    )
                else:
                    bar.append(plot.bar(ind - move * width, data[-1][showDays], width, color="k", bottom=data_stack[-1]))

            if style == "relative":
                myLabel = myLabel + " [%]"
            else:
                myLabel = myLabel + " [%s]" % unit

            plot.set_ylabel(myLabel)
            plot.set_xlabel(myXLabel)
            box = plot.get_position()
            plot.set_position([box.x0, box.y0, box.width * 0.8 / (nDays - 1) * nDays, box.height])
            plot.set_xticks(ind)
            plot.set_xticklabels(dayLabel, rotation="45")

            allbar = []
            for b in bar:
                allbar.append(b[0])

            lgd = plot.legend(allbar, legends, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

            if title != "":
                plot.set_title(title)

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            logger.debug("PlotMonthlyBalance name:%s" % nameWithPath)

            if useYear == True:
                plt.xlim([-0.5, 13.5])
            else:
                plt.xlim([-0.5, len(showDays)])

            if ylims is not None:
                plt.ylim(ylims)

            plt.savefig(nameWithPath, bbox_extra_artists=(lgd,), bbox_inches="tight")

            if plotEmf:
                nameEmf = "%s.png" % nameFile
                nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

                self._plot_as_emf(fig, filename=nameEmfWithPath)

            plt.close()

            if style == "relative":
                printData = False

            if printData == True:

                lines = ""
                line = "!nMonth\t"
                lines = lines + line

                for label in legends:
                    line = "%s\t" % label
                    lines = lines + line
                line = "\n"
                lines = lines + line

                # variables(nVar,nMonth)

                for j in range(nDays):
                    line = "%d\t" % (j + 1)
                    lines = lines + line
                    sumVar = 0.0
                    sumVarNeg = 0.0
                    for i in range(len(variables)):

                        sumVarNeg += variables[i][j]
                        line = "%.2f\t" % sumVarNeg

                        lines = lines + line

                    line = "\n"
                    lines = lines + line

                nameWithPath = "%s\%s.dat" % (self.path, nameFile)
                outfile = open(nameWithPath, "w")
                outfile.writelines(lines)
                outfile.close()

            # self.gle.getBarBalancePlot(nameFile, nameWithPath, legends, len(variables), 0,
        #                                           xnames=dayLabel)

        return namePdf

    def plotHeatingLimitFit(self, dailyTemperature, heatingPower, fileName, timeStep, title="", yLabel="",doPlot=True):
        """
        Generate a plot of heating power values in dependence of average daily temperature. If timeStep == 'daily' a
        linear fit over these data will be done to obtain values for H and HG (heating limit). Only heating power values
        > fitHeatingPowerLowerLimit will be used for the fit.

        Parameters
        ---------
        dailyTemperature : pandas.Series
            Series of average daily temperature featuring time stamps
        heatingPower : pandas.Series
            Series of heating power values featuring time stamps
        fileName : str
            Name of the file to be generated
        timeStep : str
            Time step of the heating power data. It can either be 'daily' or 'hourly'.
        title : str, optional
            Title of the plot to be generated

        Returns
        -------
        namePdf : str
            Name of pdf created
        float, optional
            Fitted value of H
        float, optional
            Fitted value of HG (heating limit)
        float, optional
            R^2 as obtained from the fit

        """

        def _heatingLimitFittingFunction_(temperature, H, HG):
            return H * (temperature - HG)

        with plt.style.context(self.stylesheet):
            fig = plt.figure()
            plot = fig.add_subplot(111)

            fitHeatingPowerLowerLimit = 500.0
            fitHeatingPower = heatingPower[heatingPower > fitHeatingPowerLowerLimit]

            if timeStep == "hourly":

                temperatureHourFromDay = []
                days = heatingPower.index.dayofyear
                for day in days:
                    temperatureHourFromDay.append(dailyTemperature.iloc[day - 1])
                plot.plot(temperatureHourFromDay, heatingPower, "bo", Markersize=3)
                timeStepTitle = "Stundenwerte"

                if title == "":
                    plot.set_title(timeStepTitle)
                else:
                    plot.set_title(title + " [" + timeStepTitle + "]")

                plot.set_ylabel(yLabel)
                plot.set_xlabel("Tagesdurchschnittstemperatur [$^\circ$C]")

                plt.gcf().subplots_adjust(bottom=0.15)

                namePdf = "%s.%s" % (fileName, self.extensionPlot)
                nameWithPath = "%s\%s" % (self.path, namePdf)

                logger.debug("PlotMonthlyBalance name:%s" % nameWithPath)

                plt.savefig(nameWithPath)  # , bbox_extra_artists=(lgd,), bbox_inches='tight')

                plt.close()

                return namePdf

            elif timeStep == "daily":

                plot.plot(dailyTemperature, heatingPower, "bo", Markersize=3)
                timeStepTitle = "Tageswerte"

                dayFilterMask = []
                for day in dailyTemperature.index.dayofyear:
                    dayFilterMask.append(day in fitHeatingPower.index.dayofyear)

                fitDailyTemperature = dailyTemperature[dayFilterMask]

                fitParametersStartValues = [-1000.0, 15.0]
                fittedParameters, covarianceParameters = curve_fit(
                    _heatingLimitFittingFunction_, fitDailyTemperature, fitHeatingPower, p0=fitParametersStartValues
                )

                RSquared = 1.0 - sum(
                    (
                        fitHeatingPower
                        - _heatingLimitFittingFunction_(fitDailyTemperature, fittedParameters[0], fittedParameters[1])
                    )
                    ** 2
                ) / sum((fitHeatingPower - num.mean(fitHeatingPower)) ** 2)

                plot.plot(
                    [min(fitDailyTemperature), fittedParameters[1]],
                    [
                        _heatingLimitFittingFunction_(
                            min(fitDailyTemperature), fittedParameters[0], fittedParameters[1]
                        ),
                        _heatingLimitFittingFunction_(fittedParameters[1], fittedParameters[0], fittedParameters[1]),
                    ],
                    "r-",
                    linewidth=2,
                )

                plot.set_ylabel(yLabel)
                plot.set_xlabel("Tagesdurchschnittstemperatur [$^\circ$C]")

                textBox = "\n".join(
                    (
                        r"$\mathrm{H}=%.0f$ W/K" % fittedParameters[0],
                        r"$\mathrm{HG}=%.1f ^\circ$C" % fittedParameters[1],
                        r"$R^2=%.2f$" % RSquared,
                    )
                )

                textBoxX = max(dailyTemperature - 10.0)
                textBoxY = max(heatingPower)
                plot.text(
                    textBoxX, textBoxY, textBox, fontsize=8, verticalalignment="top", backgroundcolor="w"
                )  # , transform=ax.transAxes, bbox=props

                if title == "":
                    plot.set_title(timeStepTitle)
                else:
                    plot.set_title(title + " [" + timeStepTitle + "]")

                plt.gcf().subplots_adjust(bottom=0.15)

                namePdf = "%s.%s" % (fileName, self.extensionPlot)
                nameWithPath = "%s\%s" % (self.path, namePdf)

                logger.debug("PlotMonthlyBalance name:%s" % nameWithPath)

                if doPlot:
                    plt.savefig(nameWithPath)  # , bbox_extra_artists=(lgd,), bbox_inches='tight')

                plt.close()

                return namePdf, round(fittedParameters[0], 0), round(fittedParameters[1], 1), round(RSquared, 2)

    def _get_cumulated_array(self, data, **kwargs):
        cum = data.clip(**kwargs)
        cum = num.cumsum(cum, axis=0)
        d = num.zeros(num.shape(data))
        d[1:] = cum[:-1]
        return d

    def plotDaily(self, var, myLabel, nameFile, plotJpg=False):

        N = 365
        width = 0.1  # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        fig = plt.figure(1, figsize=(50, 8))

        plot = fig.add_subplot(111)

        plot.bar(ind - 0.5 * width, var, width)

        plot.set_ylabel(myLabel)

        box = plot.get_position()
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        plot.axes.grid(which="major", axis="y")

        #        plot.set_title('Title',size=20)
        #        plot.set_xticks(ind)
        #        plot.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Oct', 'Nov', 'Dec','Year/10'),fontsize=20)

        namePdf = "%s.%s" % (nameFile, self.extensionPlot)
        nameWithPath = "%s\%s" % (self.path, namePdf)

        plt.xlim([-0.5, 365])

        plt.savefig(nameWithPath)

        if plotJpg:

            nameJpg = "%s.jpg" % myLabel
            nameJpgWithPath = "%s\%s" % (self.path, nameJpg)

            plt.savefig(nameJpgWithPath)

        plt.close()
        return namePdf

    # xvar 1d yVar 2D, so several lines
    def plotDynamic(
        self,
        xVar,
        yVar,
        legends,
        nameFile=None,
        xLabel="Days",
        yLabel=None,
        plotJpg=False,
        printData=False,
        printEvery=1,
        xlim=False,
        ylim=False,
    ):

        try:
            size = len(xVar)
        except:
            xVar = num.arange(len(yVar[0]))

        fig = plt.figure()

        axes = fig.add_subplot(111)

        matplotlib.rcParams.update({"font.size": 17})

        for i in range(len(yVar)):
            axes.plot(xVar, yVar[i], "-", color=self.myColorsIn[i])

        axes.legend(legends, loc="upper left", borderaxespad=0.0)

        axes.set_xlabel("%s" % xLabel, fontsize=20)

        if yLabel != None:
            axes.set_ylabel("%s" % yLabel, fontsize=20)

        if xlim:
            plt.xlim(xlim)

        if ylim:
            plt.ylim(ylim)

        if nameFile == None:
            plt.show()
            namePdf = None

        else:

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            plt.savefig(nameWithPath)

            if plotJpg:

                nameJpg = "%s.jpg" % nameFile
                nameJpgWithPath = "%s\%s" % (self.path, nameJpg)

                plt.savefig(nameJpgWithPath)

        plt.close()

        if printData == True and nameFile != None:
            lines = ""
            line = "!x\t"
            lines = lines + line

            for label in legends:
                line = "%s\t" % label
                lines = lines + line
            line = "\n"
            lines = lines + line

            for j in range(len(yVar[0])):
                if j % printEvery == 0:
                    line = "%f\t" % xVar[j]
                    lines = lines + line
                    for i in range(len(yVar)):
                        line = "%f\t" % yVar[i][j]
                        lines = lines + line

                    line = "\n"
                    lines = lines + line

            nameWithPath = "%s\%s.dat" % (self.path, nameFile)
            outfile = open(nameWithPath, "w")
            outfile.writelines(lines)
            outfile.close()

            markers = self.gle.useMarkers
            self.gle.useMarkers = False
            self.gle.getEasyPlot(nameFile, nameWithPath, legends)
            self.gle.useMarkers = markers

        return namePdf

    def plotDynamicBalance(
        self,
        xVar,
        yVarPos,
        yVarNeg,
        legends,
        nameFile=None,
        xLabel="Days",
        plotJpg=False,
        printData=False,
        printEvery=1,
        xlim=False,
        ylim=False,
    ):

        try:
            size = len(xVar)
        except:
            xVar = num.arange(len(yVarPos[0]))

        fig = plt.figure()

        axes = fig.add_subplot(111)

        matplotlib.rcParams.update({"font.size": 17})

        for i in range(len(yVarPos)):
            axes.plot(xVar, yVarPos[i], "-", color=self.myColorsIn[i])

        k = len(yVarPos)
        for i in range(len(yVarNeg)):
            axes.plot(xVar, -yVarNeg[i], "-", color=self.myColorsIn[k])

        axes.legend(legends, loc="upper left", borderaxespad=0.0)

        axes.set_xlabel("%s" % xLabel, fontsize=20)
        #        axes.set_ylabel('%s'%myLabel,fontsize=20)

        if xlim:
            plt.xlim(xlim)

        if ylim:
            plt.ylim(ylim)

        if nameFile == None:
            plt.show()
            namePdf = None

        else:

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            plt.savefig(nameWithPath)

            if plotJpg:
                nameJpg = "%s.jpg" % nameFile
                nameJpgWithPath = "%s\%s" % (self.path, nameJpg)

                plt.savefig(nameJpgWithPath)

        plt.close()

        if printData == True and nameFile != None:
            lines = ""
            line = "!x\t"
            lines = lines + line

            for label in legends:
                line = "%s\t" % label
                lines = lines + line
            line = "\n"
            lines = lines + line

            for j in range(len(yVarPos[0])):
                if j % printEvery == 0:
                    line = "%f\t" % xVar[j]
                    lines = lines + line
                    for i in range(len(yVarPos)):
                        line = "%f\t" % yVarPos[i][j]
                        lines = lines + line

                    for i in range(len(yVarNeg)):
                        line = "%f\t" % yVarNeg[i][j]
                        lines = lines + line

                    line = "\n"
                    lines = lines + line

            nameWithPath = "%s\%s.dat" % (self.path, nameFile)
            outfile = open(nameWithPath, "w")
            outfile.writelines(lines)
            outfile.close()

            markers = self.gle.useMarkers
            self.gle.useMarkers = False
            self.gle.getEasyPlot(nameFile, nameWithPath, legends)
            self.gle.useMarkers = markers

        return namePdf

    def plotDynamicOneVar(self, xVar, yVar, myLegend, nameFile, plotJpg=False):

        try:
            size = len(xVar)
        except:
            xVar = num.arange(len(yVar))

        fig = plt.figure()

        axes = fig.add_subplot(111)

        matplotlib.rcParams.update({"font.size": 17})

        axes.plot(xVar, yVar, "-")

        axes.legend(myLegend, loc="upper left", borderaxespad=0.0)

        axes.set_xlabel("$Time$ $ [day]$", fontsize=20)
        axes.set_ylabel("$%s$" % myLegend, fontsize=20)

        if nameFile == None:
            plt.show()
            namePdf = None

        else:

            namePdf = "%s.%s" % (nameFile, self.extensionPlot)
            nameWithPath = "%s\%s" % (self.path, namePdf)

            logger.debug("plotDynamic: Save plot name:%s" % nameWithPath)

            plt.savefig(nameWithPath)

            if plotJpg:

                nameJpg = "%s.jpg" % nameFile
                nameJpgWithPath = "%s\%s" % (self.path, nameJpg)

                plt.savefig(nameJpgWithPath)

        plt.close()

        return namePdf

    def calcAndPrintQVersusT(self, fileName, tFlow, eFlow, legends, printEvery=1, normalized=False, cut=False):
        return namePdf

    def calcAndPrintQVersusT(self, fileName, tFlow, eFlow, legends, printEvery=1, normalized=False, cut=False):

        nVar = len(legends)

        if nVar > 0:
            nTimeStep = len(tFlow[0])
        else:
            nTimeStep = len(tFlow)

        tSortVec = []
        cumEnerVec = []

        for i in range(nVar):
            logger.debug("calcAndPrintQVersusT var:%s " % legends[i])
            tSort, cumE = utils.calcQvsT(tFlow[i], eFlow[i])
            tSortVec.append(tSort)
            cumEnerVec.append(cumE)

        lines = ""
        line = "!Postprocessed file of ice storage.\n"
        lines = lines + line
        line = "!File processed with plotMatplotlib.py at %s\n" % (time.strftime("%c"))
        lines = lines + line

        line = "! "
        lines = lines + line
        i = 2
        for j in range(nVar):
            line = "(%d) T-%s-sort (%d) cum-%s " % (i, legends[j], i + 1, legends[j])
            lines = lines + line
            i = i + 2
        line = "\n"
        lines = lines + line

        for i in range(nTimeStep):
            if i != 0 and i != nTimeStep - 1 and i % printEvery == 0:
                line = "%d " % (i)
                lines = lines + line
                for j in range(nVar):
                    if cumEnerVec[j][i] <= 0.99 * cumEnerVec[j][nTimeStep - 1] or cut == False:  # cut at 99%
                        line = "%f %f " % (tSortVec[j][i], cumEnerVec[j][i])
                        lines = lines + line
                    else:
                        line = "- - "
                        lines = lines + line

                line = "\n"
                lines = lines + line
            elif i == nTimeStep - 1:
                line = "%d " % (i)
                lines = lines + line
                for j in range(nVar):
                    if cumEnerVec[j][i] <= 0.99 * cumEnerVec[j][nTimeStep - 1] or cut == False:  # cut at 99%
                        line = "%f %f " % (tSortVec[j][i], cumEnerVec[j][i])
                        lines = lines + line
                    else:
                        line = "- - "
                        lines = lines + line

        myFileName = os.path.join(self.path, fileName + ".dat")
        myFileName = os.path.join(self.path, fileName + ".dat")

        logger.debug("File created :%s" % myFileName)

        outfile = open(myFileName, "w")
        outfile.writelines(lines)
        outfile.close()

        self.gle.createGleQvsT(
            fileName, legends, normalized=normalized
        )  # path not nedded becasue it is in the same folder
        self.gle.executeGLE(fileName)

    # var[nvariables,nMonth] or var[nVariables], labels[nvariables]

    def plotPie(self, var, labels, myTitle, nameFile, printData=False, extension="pdf", sort=True, fontSize=10):

        fig = plt.figure()

        fig.add_subplot(111)

        #        figure(1, figsize=(6,6))
        #        ax = axes([0.1, 0.1, 0.8, 0.8])

        # The slices will be ordered and plotted counter-clockwise.

        varYear = []
        nVar = len(var)
        #        print "nVar:%d"%nVar

        try:
            for i in range(nVar):
                # sum for all months
                varYear.append(sum(var[i]))
        except:
            for i in range(nVar):
                # yearly value already given
                varYear.append(var[i])

        total = sum(varYear)

        fracs = []
        colors = []

        for i in range(nVar):
            fracs.append(varYear[i] / total)
            colors.append(self.myColorsIn[i])

        if sort == True:
            # sort fracs by magnitude and joint those which are very small

            sortIndex = num.argsort(fracs)

            #        print fracs
            #        print sortIndex

            fracsSorted = []
            labelsSorted = []

            sumOthers = 0.0
            for i in range(nVar):
                if fracs[sortIndex[i]] > 0.02:
                    fracsSorted.append(fracs[sortIndex[i]])
                    labelsSorted.append(labels[sortIndex[i]])
                else:
                    sumOthers = sumOthers + fracs[sortIndex[i]]

            if sumOthers > 0.0:
                fracsSorted.append(sumOthers)
                labelsSorted.append("Others")
        else:
            fracsSorted = fracs
            labelsSorted = labels

        #            explode=(0,1, 0.1, 0.1, 0.1, 0.1,0.1, 0.1)
        patches, texts, autotexts = plt.pie(
            fracsSorted, labels=labelsSorted, colors=colors, autopct="%1.0f%%", shadow=False, startangle=0
        )

        # patches, texts, autotexts = plt.pie(fracsSorted, colors=colors,autopct='%1.0f%%', shadow=False, startangle=0)

        # plt.legend(patches, labelsSorted, bbox_to_anchor=(2, 0.5), loc="upper right", fontsize=fontSize,
        #            bbox_transform=plt.gcf().transFigure)

        for i in range(len(texts)):
            texts[i].set_fontsize(fontSize)

        # The default startangle is 0, which would start
        # the Frogs slice on the x-axis.  With startangle=90,
        # everything is rotated counter-clockwise by 90 degrees,
        # so the plotting starts on the positive y-axis.

        matplotlib.rcParams.update({"font.size": fontSize})

        plt.title(myTitle, bbox={"facecolor": "0.9", "pad": 10}, fontsize=fontSize)

        # pie = plt.pie(fracsSorted, startangle=0)
        #
        # plt.legend(pie[0], labels, bbox_to_anchor=(1, 0.5), loc="center right", fontsize=10,
        #            bbox_transform=plt.gcf().transFigure)
        # plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)

        # This is working , just erase the labels section
        #         plt.legend(bbox_to_anchor=(0.15,0.9),loc='upper right', borderaxespad=0.,fontsize=fontSize)

        namePdf = "%s.%s" % (nameFile, extension)
        nameWithPath = "%s\%s" % (self.path, namePdf)

        plt.savefig(nameWithPath)

        plt.close()

        if printData == True:

            lines = ""

            for label in labelsSorted:
                line = "%s\t" % label
                lines = lines + line
            line = "\n"
            lines = lines + line

            for i in range(len(fracsSorted)):
                line = "%f\t" % fracsSorted[i]
                lines = lines + line

            line = "\n"
            lines = lines + line

            nameWithPath = "%s\%s.dat" % (self.path, nameFile)
            outfile = open(nameWithPath, "w")
            outfile.writelines(lines)
            outfile.close()

        return namePdf

    def plotYearlyEnergyBalance(
        self,
        inVar,
        outVar,
        legends,
        myLabel,
        nameFile,
        unit,
        useShares=False,
        colors=False,
        printImb=True,
        plotEmf=False,
        printData=False,
        useTwoColumns=False,
    ):

        try:
            if len(inVar[0]) > 2:
                monthlyDataUsed = True
        except:
            monthlyDataUsed = False

        N = 2
        width = 0.65  # the width of the bars

        ind = num.arange(N)  # the x locations for the groups
        move = 0

        fig = plt.figure()
        plot = fig.add_subplot(111)

        imbPlus = num.zeros(N)
        imbNeg = num.zeros(N)

        inVarYear = num.arange(len(inVar) * N, dtype=float).reshape(len(inVar), N)
        outVarYear = num.arange(len(outVar) * N, dtype=float).reshape(len(outVar), N)

        for i in range(len(inVar)):
            if monthlyDataUsed:
                inVarYear[i][0] = sum(inVar[i])
                inVarYear[i][1] = 0.0
            else:
                inVarYear[i][0] = inVar[i]
                inVarYear[i][1] = 0.0

        positive = 0.0
        for i in range(len(inVar)):
            positive = positive + inVarYear[i][0]

        if useShares:
            for i in range(len(inVar)):
                inVarYear[i][0] = inVarYear[i][0] * 100.0 / positive

        for i in range(len(outVar)):
            if monthlyDataUsed:
                outVarYear[i][1] = sum(outVar[i])
                outVarYear[i][0] = 0.0

            else:
                outVarYear[i][1] = outVar[i]
                outVarYear[i][0] = 0.0

        negative = 0.0
        for i in range(len(outVar)):
            negative = negative + outVarYear[i][1]

        if useShares:
            for i in range(len(outVar)):
                outVarYear[i][1] = outVarYear[i][1] * 100.0 / negative

        myImb = positive - negative

        #        print inVarYear
        #        print outVarYear

        if myImb > 0.0:
            imbNeg[1] = positive - negative
        else:
            imbPlus[0] = abs(positive - negative)

        addVar = 0
        barIn = []
        for i in range(len(inVarYear)):
            barIn.append(plot.bar(ind - move * width, inVarYear[i], width, color=self.myColorsIn[i], bottom=addVar))
            addVar = addVar + inVarYear[i]
        #            print "plotYearEnergyBalance colorIn:%s"%self.myColorsIn[i]

        if printImb == True and useShares == False:
            plot.bar(ind - move * width, imbPlus, width, color=self.myColorsImb, bottom=addVar)

        addVar = 0
        barOut = []
        for i in range(len(outVarYear)):
            #            print "plotYearEnergyBalance colorOut:%s"%self.myColorsOut[i]

            barOut.append(plot.bar(ind - move * width, outVarYear[i], width, color=self.myColorsOut[i], bottom=addVar))
            addVar = addVar + outVarYear[i]

        if printImb == True:
            plot.bar(ind - move * width, imbNeg, width, color=self.myColorsImb, bottom=addVar)

        myLabel = myLabel + " [%s]" % unit
        plot.set_ylabel(myLabel)

        box = plot.get_position()
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        #        plot.set_title('Title',size=20)
        plot.set_xticks(ind)
        plot.set_xticklabels(("In", "Out"), rotation="45")

        allbar = []
        for i in range(len(barIn)):
            #            print "plotYearlyEnergyBalance size BarIn:%d i:%d"%(len(barIn),i)
            if printImb == True and i == len(barIn) - 1:
                #                print "plotYearlyEnergyBalance IGNORED i:%d"%(i)
                pass
            # Otherwise the legend should include the imbalabce between in and out variables
            else:
                allbar.append(barIn[i][0])

        for b in barOut:
            allbar.append(b[1])

        plot.legend(allbar, legends, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

        plot.axes.grid(which="major", axis="y")

        namePdf = "%s.%s" % (nameFile, self.extensionPlot)
        nameWithPath = "%s\%s" % (self.path, namePdf)

        logger.debug("PlotMonthlyBalance name:%s" % nameWithPath)

        plt.xlim([-0.5, 1.5])

        plt.savefig(nameWithPath)

        if plotEmf:
            nameEmf = "%s.emf" % nameFile
            nameEmfWithPath = "%s\%s" % (self.path, nameEmf)

            self._plot_as_emf(plt, filename=nameEmfWithPath)

        plt.close()

        if printData == True:

            lines = ""
            line = "!nMonth\t"
            lines = lines + line

            for label in legends:
                line = "%s\t" % label
                lines = lines + line
            line = "\n"
            lines = lines + line

            # inVar(nVar,nMonth)

            if useTwoColumns:  # Uses two columns
                for j in range(2):
                    line = "%d\t" % (j + 1)
                    lines = lines + line

                    sumVar = 0.0
                    for i in range(len(inVarYear)):

                        sumVar = sumVar + inVarYear[i][j]
                        line = "%f\t" % sumVar
                        lines = lines + line

                    sumVar = 0
                    for i in range(len(outVarYear)):

                        sumVar = sumVar - outVarYear[i][j]
                        line = "%f\t" % sumVar
                        lines = lines + line

                    line = "\n"
                    lines = lines + line
            else:  # Use one column
                j = 0
                linesOne = ""
                linesEmpty = ""
                line = "%d\t" % (j + 1)
                linesOne = linesOne + line
                lineEmpty = "%d\t" % (j + 2)
                linesEmpty = linesEmpty + lineEmpty
                sumVar = 0.0
                for i in range(len(inVarYear)):

                    sumVar = sumVar + inVarYear[i][j]
                    line = "%f\t" % sumVar
                    linesOne = linesOne + line
                    lineEmpty = "0.0\t"
                    linesEmpty = linesEmpty + lineEmpty

                j = 1
                sumVar = 0
                for i in range(len(outVarYear)):

                    sumVar = sumVar - outVarYear[i][j]
                    line = "%f\t" % sumVar
                    linesOne = linesOne + line
                    lineEmpty = "0.0\t"
                    linesEmpty = linesEmpty + lineEmpty

                line = "\n"
                linesOne = linesOne + line
                lineEmpty = "\n"
                linesEmpty = linesEmpty + lineEmpty

                # I copy the same think twice
                lines = lines + linesOne
                lines = lines + linesEmpty
            #                 lines = lines + linesOne

            nameWithPath = "%s\%s.dat" % (self.path, nameFile)
            outfile = open(nameWithPath, "w")
            outfile.writelines(lines)
            outfile.close()

            self.gle.getBarPlot(nameFile, nameWithPath, legends, xmin=0.5, xmax=1.5, xnames=["In", "Out"])

        return namePdf

        ##########################################HERE

    def plotTemperatureFrequency(
        self, path, nameFile, name, temperature, printData=False, extension="pdf", sort=True, fontSize=10
    ):

        fig, ax = plt.subplots(1, 1)

        ax.set_title(name)
        ax.hist(temperature, bins=100)
        # plt.xlabel('Temperature [deg C]')
        plt.ylabel("Frequency [-]")

        namePdf = "%s.%s" % (nameFile, extension)
        nameWithPath = os.path.join(path, namePdf)

        plt.savefig(nameWithPath)
        plt.close()
        return namePdf
