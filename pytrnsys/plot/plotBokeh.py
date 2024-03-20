# pylint: skip-file
# type: ignore

# -*- coding: utf-8 -*-
# !/usr/bin/python

"""
Class to plot using bokeh

Based on plotMatplotlib.py and ProcessHourly.py

Author : Jeremias Schmidli
Date   : 2019/12/10
ToDo : get class to work, automatically load and plot hourly files based on names of variables
"""
import itertools
import os

from bokeh.layouts import gridplot
from bokeh.models import HoverTool, DatetimeTickFormatter
from bokeh.palettes import Dark2_8 as palette
from bokeh.plotting import figure, output_file, show, save


class PlotBokeh:
    """
    Class to plot TRNSYS results using Bokeh
    """

    def __init__(self):
        self.counter = 0
        self.fileNameUsed = []

        self.plotWidth = 1000  # 800
        self.plotHeight = 600  # 250

    def createBokehPlot(self, df, path, fileName, inputKeys, showPlot=False, sortPlots=True):
        if fileName in self.fileNameUsed:
            self.counter += 1
            useCounter = True
        else:
            self.fileNameUsed.append(fileName)
            useCounter = False

        try:
            timeArray = df["TIME"] * 3600 * 1000
        except:
            timeArray = df.index.values

        # prepare sort indices:
        temperatures = []
        energyflows = []
        massflows = []
        iceFraction = []
        various = []

        plotsDict = {}

        if sortPlots:
            # sort indices:
            for key in inputKeys:
                if key[0].lower() == "t":
                    temperatures.append(key)
                    plotsDict["temperatures"] = {"ylabel": "Temperature [deg C]", "columns": temperatures}
                elif key[0].lower() in ["q", "p"]:
                    energyflows.append(key)
                    plotsDict["energyflows"] = {"ylabel": "Energyflow [kW]", "columns": energyflows}
                elif key[0].lower() in ["m"]:
                    massflows.append(key)
                    plotsDict["massflows"] = {"ylabel": "Massflow [kg/h]", "columns": massflows}
                elif key[0].lower() in ["v"]:
                    iceFraction.append(key)
                    plotsDict["iceFraction"] = {"ylabel": "Ice Fraction [%]", "columns": iceFraction}
                else:
                    various.append(key)
                    plotsDict["various"] = {"ylabel": "various", "columns": various}
        else:
            for key in inputKeys:
                various.append(key)
                plotsDict["various"] = {"ylabel": "various", "columns": various}

        # count how many plots to make:
        plotCount = len(plotsDict)

        # plotting:
        hover = HoverTool(tooltips=[("date", "@timeArray{%F}")], formatters={"DateTime": "datetime"})
        if useCounter:
            output_file(os.path.join(path, fileName + "-plots-id%d.html" % self.counter))
        else:
            output_file(os.path.join(path, fileName + "-plots.html"))

        # TOOLS = ['box_select,box_zoom,reset,xpan,xwheel_zoom','hover','save']
        TOOLS = ["box_zoom", "reset", "pan", "wheel_zoom", "hover", "save"]

        # create a color iterator
        colors = itertools.cycle(palette)

        plots = []
        keysList = []
        for key in plotsDict:
            keysList.append(key)
        for i in range(plotCount):
            key = keysList[i]

            if i == 0:
                plotsDict[key]["fig"] = figure(
                    width=self.plotWidth, height=self.plotHeight, x_axis_type="datetime", tools=TOOLS
                )
            else:
                plotsDict[key]["fig"] = figure(
                    width=self.plotWidth,
                    x_range=plotsDict[keysList[0]]["fig"].x_range,
                    height=self.plotHeight,
                    x_axis_type="datetime",
                    tools=TOOLS,
                )
            for column in plotsDict[key]["columns"]:
                plotsDict[key]["fig"].line(timeArray, df[column], color=next(colors), alpha=0.5, legend_label=column)

            plotsDict[key]["fig"].xaxis.formatter = DatetimeTickFormatter(months=["%b"])

            plotsDict[key]["fig"].yaxis.axis_label = plotsDict[key]["ylabel"]

            plotsDict[key]["fig"].add_layout(plotsDict[key]["fig"].legend[0], "right")

            plotsDict[key]["fig"].legend.click_policy = "hide"
            plotsDict[key]["fig"].legend.label_text_font_size = "10pt"
            plots.append([plotsDict[key]["fig"]])

        p = gridplot(plots)

        if showPlot:
            show(p)
        else:
            save(p)
