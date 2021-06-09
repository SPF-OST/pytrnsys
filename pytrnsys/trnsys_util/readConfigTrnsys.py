# pylint: skip-file
# type: ignore

#!/usr/bin/python
"""
Main class to read the config file for running and processing
Author : Daniel Carbonell
Date   : 01-10-2018
ToDo:   Copy config file to results folder automatically
"""

import pytrnsys.trnsys_util.createTrnsysDeck as createDeck
import pytrnsys.rsim.executeTrnsys as exeTrnsys
import pytrnsys.trnsys_util.buildTrnsysDeck as build
import numpy as num
import os
import pytrnsys.pdata.processFiles as processFiles
import string
import pytrnsys.rsim.runParallel as runPar


def getCityFromConfig(lines):
    for line in lines:
        if "City" in line:
            cityLine = line
            weatherFile = cityLine.split("City")[1]
            city = weatherFile.split("_")[0]
            break
        else:
            weatherFile = "NoCity"
            city = "NoCity"
            pass

    return weatherFile, city


def getHydFromConfig(lines):
    for line in lines:
        if "Hydraulics\\" in line:
            hydLine = line
            break
        else:
            pass
    hyd = hydLine.split("Hydraulics\\")[1]
    return hyd


class ReadConfigTrnsys:
    def __init__(self):
        pass

    def str2bool(self, v):
        return v.lower() in ("yes", "true", "t", "1")

    def readFile(self, path, name, inputs, parseFileCreated=True, controlDataType=True):

        skypChar = "#"
        configFile = os.path.join(path, name)

        infile = open(configFile, "r")
        lines = infile.readlines()

        lines = processFiles.purgueLines(lines, skypChar, None, removeBlankLines=True, removeBlankSpaces=False)
        lines = processFiles.purgueComments(lines, skypChar)

        if "calcMonthly" not in inputs:
            inputs["calcMonthly"] = []

        if "calcMonthlyTest" not in inputs:
            inputs["calcMonthlyTest"] = []

        if "calcMonthlyMax" not in inputs:
            inputs["calcMonthlyMax"] = []

        if "calcMonthlyMin" not in inputs:
            inputs["calcMonthlyMin"] = []

        if "calcHourly" not in inputs:
            inputs["calcHourly"] = []

        if "calcMonthlyFromHourly" not in inputs:
            inputs["calcMonthlyFromHourly"] = []

        if "calcDaily" not in inputs:
            inputs["calcDaily"] = []

        if "calc" not in inputs:
            inputs["calc"] = []

        if "calcTest" not in inputs:
            inputs["calcTest"] = []

        if "calcCumSumHourly" not in inputs:
            inputs["calcCumSumHourly"] = []

        if "calcHourlyTest" not in inputs:  # dirty trick to calculate after calcCumSumHourly DC
            inputs["calcHourlyTest"] = []

        if "calcTimeStep" not in inputs:
            inputs["calcTimeStep"] = []

        if "calcTimeStepTest" not in inputs:
            inputs["calcTimeStepTest"] = []

        if "calcCumSumTimeStep" not in inputs:
            inputs["calcCumSumTimeStep"] = []

        if parseFileCreated:
            parsedFile = "%s.parse.dat" % configFile
            outfile = open(parsedFile, "w")
            outfile.writelines(lines)
            outfile.close()

        for i in range(len(lines)):

            if lines[i][-1:] == "\n":
                lines[i] = lines[i][0:-1]

            splitLine = lines[i].split()

            if splitLine[0] == "bool":
                inputs[splitLine[1]] = self.str2bool(splitLine[2])
            elif splitLine[0] == "int":
                inputs[splitLine[1]] = int(splitLine[2])
            elif splitLine[0] == "string":
                if len(splitLine) != 3:
                    splitString = ""
                    for i in range(len(splitLine) - 2):
                        if i == 0:
                            splitString += splitLine[i + 2][1:]
                            splitString += " "
                        elif i == len(splitLine) - 3:
                            splitString += splitLine[i + 2][:-1]
                        else:
                            splitString += splitLine[i + 2]
                            splitString += " "
                    inputs[splitLine[1]] = splitString
                    # raise ValueError("Error in string : %s"%lines[i])
                else:
                    inputs[splitLine[1]] = splitLine[2][1:-1]  # I delete the "
            elif splitLine[0] == "stringArray":
                if splitLine[1] not in inputs.keys():
                    inputs[splitLine[1]] = []

                newElement = []
                for i in range(len(splitLine) - 2):
                    strEl = splitLine[i + 2][1:-1]  # I delete the "
                    newElement.append(strEl)
                inputs[splitLine[1]].append(newElement)

                # if len(inputs[splitLine[1]])==1:
                #     inputs[splitLine[1]]=inputs[splitLine[1]][0]

            elif splitLine[0] == "calcMonthly":
                inputs["calcMonthly"].append(" ".join(splitLine[1:]))
            elif splitLine[0] == "calcMonthlyTest":
                inputs["calcMonthlyTest"].append(" ".join(splitLine[1:]))

            elif splitLine[0] == "calcMonthlyMax":
                inputs["calcMonthlyMax"].append(" ".join(splitLine[1:]))

            elif splitLine[0] == "calcMonthlyMin":
                inputs["calcMonthlyMin"].append(" ".join(splitLine[1:]))

            elif splitLine[0] == "calc":
                inputs["calc"].append(" ".join(splitLine[1:]))
            elif splitLine[0] == "calcHourly":
                inputs["calcHourly"].append(" ".join(splitLine[1:]))
            elif splitLine[0] == "calcMonthlyFromHourly":
                inputs["calcMonthlyFromHourly"].append(" ".join(splitLine[1:]))
            elif splitLine[0] == "calcDaily":
                inputs["calcDaily"].append(" ".join(splitLine[1:]))
            elif splitLine[0] == "calcHourlyTest":
                inputs["calcHourlyTest"].append(" ".join(splitLine[1:]))
            elif splitLine[0] == "calcTimeStep":
                inputs["calcTimeStep"].append(" ".join(splitLine[1:]))
            elif splitLine[0] == "calcTimeStepTest":  # dirty trick to have it after the calcCumSumTimeStep DC
                inputs["calcTimeStepTest"].append(" ".join(splitLine[1:]))

            # elif (splitLine[0] == "calcHourlyTest"):
            #     inputs["calcHourlyTest"].append(" ".join(splitLine[1:]))

            elif splitLine[0] == "calcCumSumHourly":
                if len(splitLine) == 2:
                    inputs["calcCumSumHourly"].append(splitLine[1])
                else:
                    inputs["calcCumSumHourly"].append(splitLine[1:])

            elif splitLine[0] == "calcCumSumTimeStep":
                if len(splitLine) == 2:
                    inputs["calcCumSumTimeStep"].append(splitLine[1])
                else:
                    inputs["calcCumSumTimeStep"].append(splitLine[1:])

            elif splitLine[0] == "calcTest":
                inputs["calcTest"].append(" ".join(splitLine[1:]))

            else:
                if controlDataType:
                    raise ValueError("type of data %s unknown" % splitLine[0])
                else:
                    pass

        return lines
