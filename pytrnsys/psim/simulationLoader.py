#!/usr/bin/python

"""
Loads all simulation data in a specific folder

Author : Mattia Battaglia
Date   : 2018
ToDo :
"""
# -*- coding: utf-8 -*-

from enum import Enum
import pandas as pd
import os
from datetime import datetime, timedelta
from itertools import islice

class SimulationLoader():
    def __init__(self, _path, _fileNameList=False):
        self.path = _path
        self.monData = pd.DataFrame()
        self.houData = pd.DataFrame()

        if not (_fileNameList):
            _fileNameList = os.listdir(self.path)
        for fileName in _fileNameList:
            self.loadFile(fileName)


    def loadFile(self,file):
        pathFile = os.path.join(self.path, file)
        fileType = self.fileSniffer(pathFile)
        nRows = self.fileLen(pathFile)
        if fileType == ResultsFileType.MONTHLY:
            file = pd.read_csv(pathFile,header=1,delimiter='\t',nrows=nRows-26,mangle_dupe_cols=True).rename(columns=lambda x: x.strip())
            file = file[file.columns[:-1]]
            file['Number']=pd.to_datetime(file['Month'].str.strip(),format='%B').dt.month
            file.set_index('Number',inplace=True)
            file.sort_index(inplace=True)
            file['Datetime']=pd.to_datetime(file['Month'].str.strip(),format='%B')
            cols_to_use = [item for item in file.columns[:-1] if item not in set(self.monData.columns)]
            self.monData = pd.merge(self.monData,file[cols_to_use], left_index=True, right_index=True, how='outer')
        elif fileType == ResultsFileType.HOURLY:
            file = pd.read_csv(pathFile,header=1,delimiter='\t',nrows=nRows-26).rename(columns=lambda x: x.strip())
            file["Period"] = datetime(2018,1,1)+pd.to_timedelta(file['Period'],unit='h')
            file.set_index('Period',inplace=True)
            self.houData = pd.merge(self.houData, file, left_index=True, right_index=True, how='outer')





    def fileSniffer(self,file):
        with open(file) as f:
            for line in islice(f,0,3):
                if 'Month' in line:
                    return ResultsFileType.MONTHLY
        with open(file) as f:
            for line in islice(f, 0, 3):
                if 'Period' in line:
                    return ResultsFileType.HOURLY

    def fileLen(self,fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1



class ResultsFileType(Enum):
    MONTHLY = 1
    HOURLY = 2
    TIMESTEP = 3


if __name__ == "__main__":

    simulation = SimulationLoader(r'C:\Daten\OngoingProject\SensOpt\SensOpt_Base\temp')
    #simulation.loadFile('Jenni_MO.Prt')
    print(self.data)