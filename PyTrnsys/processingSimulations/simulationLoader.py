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
        if fileType == ResultsFileType.MONTHLY:
            file = pd.read_csv(pathFile,header=1,delimiter='\t',skipfooter=24).rename(columns=lambda x: x.strip())
            file['Number']=pd.to_datetime(file['Month'].str.strip(),format='%B').dt.month
            file.set_index('Number',inplace=True)
            file.sort_index(inplace=True)
            file['Datetime']=pd.to_datetime(file['Month'].str.strip(),format='%B')
            cols_to_use = file.columns.difference(self.monData)
            self.monData = pd.merge(self.monData,file[cols_to_use], left_index=True, right_index=True, how='outer')
            #self.monthlyData[file]=self.monthlyData[file].append(self.monthlyData[file].sum(numeric_only=True)/10,ignore_index=True)
        elif fileType == ResultsFileType.HOURLY:
            file = pd.read_csv(pathFile,header=1,delimiter='\t',skipfooter=24).rename(columns=lambda x: x.strip())
            file["Period"] = datetime(2018,1,1)+pd.to_timedelta(file['Period'],unit='h')
            file.set_index('Period',inplace=True)
            self.houData = pd.merge(self.houData, file, left_index=True, right_index=True, how='outer')






    def fileSniffer(self,file):
        with open(file) as f:
            if 'January' in f.read():
                return ResultsFileType.MONTHLY
        with open(file) as f:
            if 'Period' in f.read():
                return ResultsFileType.HOURLY



class ResultsFileType(Enum):
    MONTHLY = 1
    HOURLY = 2
    TIMESTEP = 3


if __name__ == "__main__":

    simulation = SimulationLoader(r'C:\Daten\OngoingProject\SensOpt\SensOpt_Base\temp')
    #simulation.loadFile('Jenni_MO.Prt')
    print(self.data)