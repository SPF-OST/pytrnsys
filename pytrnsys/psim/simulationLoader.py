#!/usr/bin/python

"""
Loads all simulation data in a specific folder

Author : Mattia Battaglia
Date   : 2019
ToDo :
"""
# -*- coding: utf-8 -*-

from enum import Enum
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as num


class SimulationLoader():

    def __init__(self, path, fileNameList=False, mode='dataframe'):
        self.path = path
        self.mode = mode

        if self.mode == 'dataframe':
            self.monData = pd.DataFrame()
            self.houData = pd.DataFrame()
            self.steData = pd.DataFrame()

        elif self.mode == 'array':
            self.monData = {}
            self.houData = {}
            self.steData = {}

        else:
            raise ValueError('mode must be either "dataframe" or "array"')

        if not (fileNameList):
            fileNameList = os.listdir(self.path)

        for fileName in fileNameList:
            self.loadFile(fileName)

    def loadFile(self, file):
        pathFile = os.path.join(self.path, file)
        fileType = self.fileSniffer(pathFile)
        nRows = self.fileLen(pathFile)

        if fileType == ResultsFileType.MONTHLY:
            file = pd.read_csv(pathFile, header=1, delimiter='\t', nrows=nRows - 26, mangle_dupe_cols=True).rename(
                columns=lambda x: x.strip())
            file = file[file.columns[:-1]]
            file['Number'] = pd.to_datetime(file['Month'].str.strip(), format='%B').dt.month
            file.set_index('Number', inplace=True)
            file.sort_index(inplace=True)
            file['Datetime'] = pd.to_datetime(file['Month'].str.strip(), format='%B')

            if self.mode == 'dataframe':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.monData.columns)]
                self.monData = pd.merge(self.monData, file[cols_to_use], left_index=True, right_index=True, how='outer')

            elif self.mode == 'array':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.monData.keys())]
                dict = {k: num.array(v.to_list()) for k, v in file[cols_to_use].items()}
                self.monData = {**self.monData, **dict}


        elif fileType == ResultsFileType.HOURLY:
            file = pd.read_csv(pathFile, header=1, delimiter='\t', nrows=nRows - 26).rename(columns=lambda x: x.strip())
            file["Period"] = datetime(2018, 1, 1) + pd.to_timedelta(file['Period'], unit='h')
            file.set_index('Period', inplace=True)
            
            if self.mode == 'dataframe':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.houData.columns)]
                self.houData = pd.merge(self.houData, file, left_index=True, right_index=True, how='outer')
                
            elif self.mode == 'array':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.houData.keys())]
                dict = {k: num.array(v.to_list()) for k, v in file[cols_to_use].items()}
                self.houData = {**self.houData, **self.dict}

        elif fileType == ResultsFileType.TIMESTEP:
            file = pd.read_csv(pathFile, header=0, delimiter='\t', nrows=nRows - 1).rename(columns=lambda x: x.strip())
            file["TIME"] = datetime(2018, 1, 1) + pd.to_timedelta(file['TIME'], unit='h')
            file.set_index('TIME', inplace=True)
            
            if self.mode == 'dataframe':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.steData.columns)]
                self.steData = pd.merge(self.steData, file, left_index=True, right_index=True, how='outer')
                
            elif self.mode == 'array':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.steData.keys())]
                dict = {k: num.array(v.to_list()) for k, v in file[cols_to_use].items()}
                self.steData = {**self.steData, **dict}

    def fileSniffer(self, file):
        with open(file) as f:
            for i in range(3):
                if 'Month' in f.readline():
                    return ResultsFileType.MONTHLY
                
        with open(file) as f:
            for i in range(3):
                if 'Period' in f.readline():
                    return ResultsFileType.HOURLY

        with open(file) as f:
            for i in range(3):
                if 'TIME' in f.readline():
                    return ResultsFileType.TIMESTEP

    def fileLen(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1


class ResultsFileType(Enum):
    MONTHLY = 1
    HOURLY = 2
    TIMESTEP = 3
