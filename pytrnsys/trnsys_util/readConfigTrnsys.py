# pylint: skip-file
# type: ignore

# !/usr/bin/python
"""
Main class to read the config file for running and processing
Author : Daniel Carbonell
Date   : 01-10-2018
ToDo:   Copy config file to results folder automatically
"""

import os
import pytrnsys.pdata.processFiles as processFiles


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

    @staticmethod
    def str2bool(v):
        return v.lower() in ("yes", "true", "t", "1")

    def readFile(self, path, name, inputs, parseFileCreated=True, controlDataType=True):
        skypChar = "#"
        configFile = os.path.join(path, name)

        infile = open(configFile, "r")
        lines = infile.readlines()

        lines = processFiles.purgueLines(lines, skypChar, None, removeBlankLines=True, removeBlankSpaces=False)
        lines = processFiles.purgueComments(lines, skypChar)

        inputs = self._addMissingFields(inputs)

        if parseFileCreated:
            self._createParseFile(configFile, lines)

        addPathToConnectionInfo = True
        addProjects = True
        addProjectPath = True
        addPathBase = True

        for i, line in enumerate(lines):
            if line[-1:] == "\n":
                line = line[0:-1]
                lines[i] = line

            splitLine = line.split()

            if splitLine[0] == "bool":
                inputs[splitLine[1]] = self.str2bool(splitLine[2])
            elif splitLine[0] == "int":
                inputs[splitLine[1]] = int(splitLine[2])
            elif splitLine[0] == "string":
                if "string pathToConnectionInfo " in line:
                    addPathToConnectionInfo = False
                if "string PROJECT$ " in line:
                    addProjects = False
                if "string projectPath " in line:
                    addProjectPath = False
                if "string pathBase " in line:
                    addPathBase = False

                if len(splitLine) != 3:
                    splitString = ""
                    for j in range(len(splitLine) - 2):
                        if j == 0:
                            splitString += splitLine[j + 2][1:]
                            splitString += " "
                        elif j == len(splitLine) - 3:
                            splitString += splitLine[j + 2][:-1]
                        else:
                            splitString += splitLine[j + 2]
                            splitString += " "
                    inputs[splitLine[1]] = splitString
                    # raise ValueError("Error in string : %s"%lines[i])
                else:
                    inputs[splitLine[1]] = splitLine[2][1:-1]  # I delete the "
            elif splitLine[0] == "stringArray":
                if splitLine[1] not in inputs.keys():
                    inputs[splitLine[1]] = []

                newElement = []
                for j in range(len(splitLine) - 2):
                    strEl = splitLine[j + 2][1:-1]  # I delete the "
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

        lines, inputs = self._addMissingDefaultPaths(
            addPathBase, addPathToConnectionInfo, addProjectPath, addProjects, inputs, lines, name, path
        )

        return lines

    @staticmethod
    def _createParseFile(configFile, lines):
        parsedFile = "%s.parse.dat" % configFile
        outfile = open(parsedFile, "w")
        outfile.writelines(lines)
        outfile.close()

    @staticmethod
    def _addMissingFields(inputs):
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

        return inputs

    @staticmethod
    def _addMissingDefaultPaths(
        addPathBase, addPathToConnectionInfo, addProjectPath, addProjects, inputs, lines, name, path
    ):
        if "run.config" in name:
            if addPathToConnectionInfo:
                info = os.path.join(path, "DdckPlaceHolderValues.json")
                inputs["pathToConnectionInfo"] = info
                lines.append("string pathToConnectionInfo " + info)
            if addProjects:
                info = os.path.join(path, "ddck")
                inputs["PROJECT$"] = info
                lines.append("string PROJECT$ " + info)
            if addProjectPath:
                inputs["projectPath"] = path
                lines.append("string projectPath " + str(path))

        elif "process.config" in name and addPathBase:
            inputs["pathBase"] = path
            lines.append("string pathBase " + str(path))

        return lines, inputs
