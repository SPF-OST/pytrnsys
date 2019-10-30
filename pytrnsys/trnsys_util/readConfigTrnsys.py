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
            break
        else:
            pass
    weatherFile = cityLine.split("City")[1]
    city = weatherFile.split("_")[0]

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

class ReadConfigTrnsys():

    def __init__(self):
        pass

    def str2bool(self,v):
        return v.lower() in ("yes", "true", "t", "1")

    def readFile(self,path,name,inputs,parseFileCreated=True,controlDataType=True):

        skypChar = "#"
        configFile = os.path.join(path, name)

        infile = open(configFile, 'r')
        lines = infile.readlines()

        lines = processFiles.purgueLines(lines, skypChar, None,removeBlankLines=True, removeBlankSpaces=False)
        lines = processFiles.purgueComments(lines, skypChar)

        if (parseFileCreated):
            parsedFile = "%s.parse.dat" % configFile
            outfile = open(parsedFile, 'w')
            outfile.writelines(lines)
            outfile.close()

        for i in range(len(lines)):

            if (lines[i][-1:] == "\n"):
                lines[i] = lines[i][0:-1]

            splitLine = lines[i].split()

            if (splitLine[0] == "bool"):
                inputs[splitLine[1]] = self.str2bool(splitLine[2])
            elif (splitLine[0] == "int"):
                inputs[splitLine[1]] = int(splitLine[2])
            elif (splitLine[0] == "string"):
                if(len(splitLine)!=3):
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
                    inputs[splitLine[1]] = splitLine[2][1:-1] #I delete the "
            elif (splitLine[0] == "stringArray"):
                inputs[splitLine[1]] = []
                for i in range(len(splitLine)-2):
                    strEl = splitLine[i+2][1:-1] #I delete the "
                    inputs[splitLine[1]].append(strEl)

            else:
                if(controlDataType):
                    raise ValueError("type of data %s unknown" % splitLine[0])
                else:
                    pass

        return lines

