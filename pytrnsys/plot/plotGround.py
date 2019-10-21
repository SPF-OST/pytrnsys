#!/usr/bin/env python

"""
Plotting functionality customized for data printed by TYPE ?? developed by SPF.
This type solves the ground in 2D and is used to couple ice storages with the ground
for undergound storages.
Author : Dani Carbonell
Date   : 20.02.2014
"""

import numpy as num
import matplotlib.pyplot as plt
import matplotlib
import interpolation
import string
import pytrnsys.utils.utilsSpf as utils
import math
import os


class PlotGround():

    def __init__(self, _path, _name):

        self.outputPath = _path
        self.nameWithExtension = _name
        self.name = _name.split('.')[0]
        self.revertPlotT = False
        self.revertPlotGrid = False

        self.addSizeInNames = False

    def readTemperatureField(self, name):

        self.T = num.arange(len(self.xPoints) * len(self.yPoints), dtype=float).reshape(len(self.xPoints),
                                                                                        len(self.yPoints))

        nameWithPath = "%s\%s" % (self.outputPath, name)

        print(nameWithPath)

        infile = open(nameWithPath, 'r')

        lines = infile.readlines()

        j = len(self.yPoints) - 1
        for line in lines:

            splittedLines = line.split()
            splittedLines = [float(list_item) for list_item in splittedLines]

            for i in range(len(splittedLines)):
                self.T[i][j] = splittedLines[i]

            j = j - 1

        TX = len(self.xPoints)
        TY = len(self.yPoints)

        self.T[0][0] = self.T[0][1]
        self.T[0][TY - 1] = self.T[0][TY - 2]
        self.T[TX - 1][0] = self.T[TX - 1][1]
        self.T[TX - 1][TY - 1] = self.T[TX - 1][TY - 2]

    def plotLines(self, name, x, y):

        #        print "sizeX%d sizeY:%d"% (len(self.xPoints),len(self.yPoints))

        self.yLine = interpolation.getVectorIn2DMatrix(self.xPoints, self.yPoints, self.T, "x", x)
        self.xLine = interpolation.getVectorIn2DMatrix(self.xPoints, self.yPoints, self.T, "y", y)

        if (self.addSizeInNames):
            nameX = "%s\lineX-TX%dTY%d.dat" % (self.outputPath, len(self.xPoints), len(self.yPoints))
        else:
            nameX = "%s\lineX.dat" % (self.outputPath)

        lines = ""
        line = "!X\tTLine at Y=%f\n" % y;
        lines = lines + line
        for i in range(len(self.xPoints)):
            if (y == 0 and (i == 0 or i == len(self.xPoints) - 1)):
                pass
            else:
                line = "%8.4f\t%8.4f\n" % (self.xPoints[i], self.xLine[i])
                lines = lines + line

        outfile = open(nameX, 'w')
        outfile.writelines(lines)
        outfile.close()

        if (self.addSizeInNames):
            nameY = "%s\lineY-TX%dTY%d.dat" % (self.outputPath, len(self.xPoints), len(self.yPoints))
        else:
            nameY = "%s\lineY.dat" % (self.outputPath)

        lines = ""
        line = "!Y\tTLine at X=%f\n" % x;
        lines = lines + line
        for i in range(len(self.yPoints)):
            if (x == 0 and (i == 0 or i == len(self.xPoints) - 1)):
                pass
            else:
                line = "%8.4f\t%8.4f\n" % (self.yPoints[i], self.yLine[i])
                lines = lines + line

        outfile = open(nameY, 'w')
        outfile.writelines(lines)
        outfile.close()

    def loadGroundField(self):

        nameGroundWithPath = "%s\%s" % (self.outputPath, self.nameWithExtension)

        print(nameGroundWithPath)

        infile = open(nameGroundWithPath, 'r')

        lines = infile.readlines()

        k = 0

        self.xPoints = []
        self.yPoints = []

        for line in lines:

            splittedLines = line.split()
            splittedLines = [float(list_item) for list_item in splittedLines]

            if (k == 0):
                xPoints = splittedLines  # The first value is 0 and not used.
            elif (k == 1):
                yPoints = splittedLines
            else:
                pass

            k = k + 1

        self.xPoints = num.array(xPoints)
        self.yPoints = num.array(yPoints)

    def plotGroundMesh(self):

        fig = plt.figure(1, figsize=(12, 8))

        axes = fig.add_subplot(111)

        matplotlib.rcParams.update({'font.size': 17})

        beginX = self.xPoints[0]
        endX = self.xPoints[len(self.xPoints) - 1]

        if (self.revertPlotGrid):
            beginY = self.yPoints[len(self.yPoints) - 1]
            endY = self.yPoints[0]
        else:
            beginY = self.yPoints[0]
            endY = self.yPoints[len(self.yPoints) - 1]

        axes.set_xticks(self.xPoints)
        axes.set_yticks(self.yPoints)

        sizeX = len(self.xPoints)
        sizeY = len(self.yPoints)

        xLabel = []
        for i in range(sizeX):
            xLabel.append("")

        xLabel[0] = repr(beginX)
        xLabel[sizeX - 1] = "%.2f" % endX

        yLabel = []
        for i in range(sizeY):
            yLabel.append("")

        #        yLabel[0] = repr(beginY)
        yLabel[sizeY - 1] = "%.2f" % endY

        axes.set_xticklabels(xLabel, fontsize=14)
        axes.set_yticklabels(yLabel, fontsize=14)

        axes.set_xlabel("r [m]", visible=True)
        axes.set_ylabel("y [m]", visible=True)

        plt.xlim([beginX, endX])
        plt.ylim([beginY, endY])

        plt.grid(color='black', linestyle='-', linewidth=1)

        if (self.addSizeInNames):
            myName = "%s/%s-TX%dTY%d.pdf" % (self.outputPath, self.name, len(self.xPoints), len(self.yPoints))
        else:
            myName = "%s/%s.pdf" % (self.outputPath, self.name)

        fig.savefig(myName)

        fig.clear()

    def plotTwelveGround(self, name, hour):

        size = 50

        # be carefull. This is wrong we must use nodx and not vclx
        if (self.revertPlotT):
            self.xDataMesh, self.yDataMesh = num.meshgrid(self.xPoints, -self.yPoints)
        else:
            self.xDataMesh, self.yDataMesh = num.meshgrid(self.xPoints, self.yPoints)

        fig = plt.figure(figsize=(12, 12))

        #        levels = [0,5,10,15,20,25,30,35,40,45,50,55,60]

        for i in range(12):
            plot = fig.add_subplot(4, 3, i + 1)

            self.readTemperatureField(name[i])

            axes = plot.contourf(self.xDataMesh, self.yDataMesh, self.T.T, vmin=0, vmax=60, size=500)

            plot.tick_params(axis='both', which='major', labelsize=6)
            plot.tick_params(axis='both', which='minor', labelsize=6)

            (month, day, year) = utils.getMonthIndexByHourOfYear(hour[i] + 24)
            year = 2012 + year
            plot.set_title("%d-%d-%d" % (day, month, year), fontsize=6)

            cbar = fig.colorbar(axes)  # draw colorbar
            cbar.ax.tick_params(labelsize=6)
            cbar.update_ticks()

        self.nameGroundWithPath1 = "%s/groundPlot1.pdf" % (self.outputPath)

        fig.savefig(self.nameGroundWithPath1)

        fig.clear()

    def plotTGround(self, name, hour):

        fig = plt.figure()
        plot = fig.add_subplot(1, 1, 1)

        size = 1000

        (month, day, year) = utils.getMonthIndexByHourOfYear(hour + 24)
        year = 2012 + year
        plot.set_title("%d-%d-%d" % (day, month, year), fontsize=8)

        # be carefull. This is wrong we must use nodx and not vclx
        if (self.revertPlotT):
            self.xDataMesh, self.yDataMesh = num.meshgrid(self.xPoints, -self.yPoints)
        else:
            self.xDataMesh, self.yDataMesh = num.meshgrid(self.xPoints, self.yPoints)

        axes = plot.contourf(self.xDataMesh, self.yDataMesh, self.T.T, size)

        plot.tick_params(axis='both', which='major', labelsize=8)
        plot.tick_params(axis='both', which='minor', labelsize=8)

        #        plot.grid(True)

        cbar = fig.colorbar(axes)  # draw colorbar
        cbar.update_ticks()

        if (self.addSizeInNames):
            myName = "%s/%s-T-TX%dTY%d.pdf" % (
            self.outputPath, name.split('.')[0], len(self.xPoints), len(self.yPoints))
        else:
            myName = "%s/%s-T.pdf" % (self.outputPath, name.split('.')[0])

        fig.savefig(myName)

        fig.clear()

        return os.path.basename(myName)
#        myX = "%s/%s-NODX.dat" % (self.outputPath,name.split('.')[0])
#        num.savetxt(myX,self.xDataMesh)

#        myX = "%s/%s-NODY.dat" % (self.outputPath,name.split('.')[0])
#        num.savetxt(myX,self.yDataMesh)
#
#        myX = "%s/%s-T.dat" % (self.outputPath,name.split('.')[0])
#        num.savetxt(myX,self.T.T)

#