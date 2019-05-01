#!/usr/bin/python
"""
Main class to read the config file for running and processing
Author : Daniel Carbonell
Date   : 01-10-2018
ToDo:   Copy config file to results folder automatically
"""

import createTrnsysDeck as createDeck
import executeTrnsys as exeTrnsys
import BuildTrnsysDeck as build
import numpy as num
import os
import processFiles
import string
import runParallel as runPar


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
                inputs[splitLine[1]] = string.atoi(splitLine[2])
            elif (splitLine[0] == "string"):
                if(len(splitLine)!=3):
                    raise ValueError("Error in string : %s"%lines[i])
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
