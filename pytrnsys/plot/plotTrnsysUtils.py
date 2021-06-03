# pylint: skip-file
# type: ignore

#!/usr/bin/env python

"""
Class to plot hourly or time step data from TRNSYS
Author : Dani Carbonell
Date   : 2018
ToDo   :
"""

import pytrnsys.trnsys_util.readTrnsysFiles as readTrnsysFiles
import matplotlib.pyplot as plt
import matplotlib
import os
import pytrnsys.plot.plotMatplotlib as plotMatplotlib
import numpy as num


class PlotTrnsysUtils:
    def __init__(self, _path):
        self.path = _path
        self.readTrnsysFiles = readTrnsysFiles.ReadTrnsysFiles(_path)
        self.myPlot = plotMatplotlib.PlotMatplotlib()
        self.myPlot.setPath(_path)
        self.sizeFigX = 12
        self.sizeFigY = 6

        self.color = ["k", "b", "g", "r", "c", "m", "y"]
        self.i = 0
        self.yLabel = False
        self.clean()

        self.printData = True
        self.printEvery = 100

    #        b: blue
    #        g: green
    #        r: red
    #        c: cyan
    #        m: magenta
    #        y: yellow
    #        k: black
    #        w: white

    def clean(self):

        self.x = []
        self.y = []
        self.nameX = []
        self.nameY = []

    def changePath(self, _path):
        self.readTrnsysFiles.path = _path

    def load(self, _name):
        self.readTrnsysFiles.readUserDefinedFiles(_name)

    def loadHourly(self, _name, firstConsideredTime=8760):
        self.readTrnsysFiles.readHourlyFiles(_name, firstConsideredTime=firstConsideredTime)

    def setYLabel(self, ylabel):
        self.yLabel = ylabel

    def add(self, nameX, nameY, scale=1.0):
        self.i = self.i + 1

        self.nameY.append(nameY)
        self.nameX.append(nameX)

        self.x.append(self.readTrnsysFiles.get(nameX))
        self.y.append(self.readTrnsysFiles.get(nameY) * scale)

    def scaleX(self, scale):
        self.x[self.i - 1] = self.x[self.i - 1] * scale

    def moveX(self, move):
        self.x[self.i - 1] = self.x[self.i - 1] + move

    def scaleY(self, scale):
        self.y[self.i - 1] = self.y[self.i - 1] * scale

    def scaleAllX(self, scale):
        for i in range(len(self.x)):
            self.x[i] = self.x[i] * scale

    def scaleAllY(self, scale):
        for i in range(len(self.y)):
            self.y[i] = self.y[i] * scale

    def moveAllX(self, move):
        for i in range(len(self.x)):
            self.x[i] = self.x[i] + move

    def integrateCumulative(self):
        dTime = (self.x[self.i - 1][2] - self.x[self.i - 1][1]) / 3600.0  # Assume constant time step in hours
        y = num.cumsum(self.y[self.i - 1]) * dTime
        self.y[self.i - 1] = y

    def plot(self, name=None):

        myLegend = []

        for i in range(len(self.x)):
            myLegend.append(self.nameY[i])

        self.myPlot.plotDynamic(
            self.x[0],
            self.y,
            myLegend,
            nameFile=name,
            xLabel=self.nameX[0],
            printData=self.printData,
            printEvery=self.printEvery,
        )
        # self.myPlot.plotDynamicOneVar(self.x[0],self.y[0],myLegend,name)

    def show(self, name=False):
        fig = plt.figure(1, figsize=(self.sizeFigX, self.sizeFigY))

        axes = fig.add_subplot(111)

        myLegend = []
        matplotlib.rcParams.update({"font.size": 15})

        myLegend = []
        for i in range(len(self.x)):
            axes.plot(self.x[i], self.y[i], "-", color=self.color[i])
            myLegend.append(self.nameY[i])

        #            axes.set_ylabel(self.nameY[i],fontsize=20)

        axes.legend(myLegend, loc="upper right", borderaxespad=0.0)

        #        plt.legend( myLegend,bbox_to_anchor=(1.1,1),loc=2, borderaxespad=0.,fontsize=8)

        axes.set_xlabel(self.nameX[0], fontsize=10)
        if self.yLabel != False:
            axes.set_ylabel(self.yLabel, fontsize=10)

        if name == False:
            plt.show()
        else:
            nameWithPath = os.path.join(self.path, name)
            plt.savefig(nameWithPath)
