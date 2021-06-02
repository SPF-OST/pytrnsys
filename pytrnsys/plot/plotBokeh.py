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
import numpy as np
import pandas as pd
from bokeh.plotting import figure, output_file, show, save
from bokeh.layouts import gridplot
from bokeh.models import HoverTool, BoxSelectTool, DatetimeTickFormatter

# select a palette
# from bokeh.palettes import Category10_10 as palette
from bokeh.palettes import Dark2_8 as palette

import itertools

import os

import datetime as dt


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
                    plot_width=self.plotWidth, plot_height=self.plotHeight, x_axis_type="datetime", tools=TOOLS
                )
            else:
                plotsDict[key]["fig"] = figure(
                    plot_width=self.plotWidth,
                    x_range=plotsDict[keysList[0]]["fig"].x_range,
                    plot_height=self.plotHeight,
                    x_axis_type="datetime",
                    tools=TOOLS,
                )
            for column in plotsDict[key]["columns"]:
                plotsDict[key]["fig"].line(timeArray, df[column], color=next(colors), alpha=0.5, legend_label=column)
                # plotsDict[key]['fig'].line(timeArray, df[column], color=next(colors), alpha = 0.5)

            plotsDict[key]["fig"].xaxis.formatter = DatetimeTickFormatter(months=["%b"])

            # plotsDict[key]['fig'].xaxis.formatter = DatetimeTickFormatter(hours = ['%Hh', '%H:%M'])
            # plotsDict[key]['fig'].xaxis.formatter = DatetimeTickFormatter(hours = ['%Hh'])

            plotsDict[key]["fig"].yaxis.axis_label = plotsDict[key]["ylabel"]

            plotsDict[key]["fig"].add_layout(plotsDict[key]["fig"].legend[0], "right")
            # plotsDict[key]['fig'].legend.location = 'top_left'

            plotsDict[key]["fig"].legend.click_policy = "hide"
            plotsDict[key]["fig"].legend.label_text_font_size = "10pt"
            plots.append([plotsDict[key]["fig"]])

        p = gridplot(plots)

        if showPlot:
            show(p)
        else:
            save(p)
        #
        #
        # # temperature plot:
        # s1 = figure(plot_width=800, plot_height=250, x_axis_type="datetime", tools=TOOLS)
        # # s1.add_tools(hover)
        # s1.line(timeArray, df['Troom'], color='navy', alpha=0.5, legend='Troom')
        # s1.line(timeArray, df['Tamb'], color=next(colors), alpha=0.5, legend='Tamb')
        # # s1.line(timeArray, df["TSourceIn"], color='olive', alpha=0.5, legend='THXCoolWatIn')
        # # s1.line(timeArray, df["TLoadIn"], color='firebrick', alpha=0.5, legend='THXCoolBriIn')
        # s1.line(timeArray, df["TsensorPcmControl"], color='black', alpha=0.5, legend='Tpcm')
        # s1.line(timeArray, df["Tsavg"], color=next(colors), alpha=0.5, legend='Tsavg')
        # s1.line(timeArray, df["TPiRadIn"], color=next(colors), alpha=0.5, legend='TPiRadIn')
        # s1.line(timeArray, df["TpiRadOut"], color=next(colors), alpha=0.5, legend='TpiRadOut')
        # # s1.line(timeArray, df["TPiIceIn"], color=next(colors), alpha=0.5, legend='TPiIceIn')
        # # s1.line(timeArray, df["TPiIceOut"], color=next(colors), alpha=0.5, legend='TPiIceOut')
        # s1.xaxis.formatter = DatetimeTickFormatter(months = ["%b"])
        # s1.yaxis.axis_label = "Temperature [deg C]"
        # s1.legend.location = 'top_left'
        # s1.legend.click_policy="hide"
        # s1.legend.label_text_font_size = "10pt"
        #
        #
        # # massflow plot:
        # s2 = figure(plot_width=800, plot_height=250, x_axis_type="datetime",x_range=s1.x_range, tools=TOOLS, y_axis_label = "Massflow [kg/h]")
        # # s2.line(timeArray,df["MfrLoadIn"], color=next(colors), alpha=0.5,legend='MfrPuCool')
        # s2.line(timeArray,df["MfrPuCol"], color=next(colors), alpha=0.5,legend='MfrPuCol')
        # s2.line(timeArray,df["MfrPuHpEvap"], color=next(colors), alpha=0.5,legend='MfrPuHpEvap')
        # s2.line(timeArray,df["MfrPuSH"], color=next(colors), alpha=0.5,legend='MfrPuSH')
        # s2.line(timeArray,df["MfrPiSHTesIn"], color=next(colors), alpha=0.5,legend='MfrPiSHTesIn')
        # s2.line(timeArray,-df["MfrPiIceOut"], color=next(colors), alpha=0.5,legend='MfrPiIceOut')
        # s2.legend.location = 'top_left'
        # s2.xaxis.formatter = DatetimeTickFormatter(months = ["%b"])
        # s2.legend.click_policy="hide"
        #
        #
        # # energyflow plot:
        # s3 = figure(plot_width=800, plot_height=250, x_axis_type="datetime",x_range=s1.x_range, tools=TOOLS, y_axis_label = "Energyflow [kWh]")
        # s3.line(timeArray, Qrad, color=next(colors), alpha=0.5, legend='Qrad')
        # # s3.line(timeArray, QHXcoolWat, color=next(colors), alpha=0.5, legend='QHXcoolWat')
        # # s3.line(timeArray, QHXcoolBri, color=next(colors), alpha=0.5, legend='QHXcoolBri')
        # s3.line(timeArray, QIce, color=next(colors), alpha=0.5, legend='QIce')
        # s3.line(timeArray, -df["PheatBui_kW"], color=next(colors), alpha=0.5, legend='PheatBui_kW')
        # s3.legend.location = 'top_left'
        # s3.xaxis.formatter = DatetimeTickFormatter(months = ["%b"])
        # s3.legend.click_policy="hide"
        #
        #
        # s4 = figure(plot_width=800, plot_height=250, x_axis_type="datetime",x_range=s1.x_range, tools=TOOLS, y_axis_label = "Ice Fraction [%]", x_axis_label = "Time")
        # s4.line(timeArray, df["VIceRatio"], color='olive', alpha=0.5, legend='VIceRatio')
        # s4.xaxis.formatter = DatetimeTickFormatter(months = ["%b"])
        # s4.legend.click_policy="hide"

        # p = gridplot([[s1],[s2],[s3],[s4]])
        # show(p)
