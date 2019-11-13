#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as num


class SimulationLoader():
    """Loads TRNSYS printer files.

    The TRNSYS printer files are loaded into the attributes monData (monthly data), houData (hourly data)
    and steData (timestep data) respectively.

    Parameters
    ----------
    path : str
        path of the folder to be loaded
    fileNameList : :obj:`list` of :obj:`str`, optional
        list of file names to include into the loader
    mode : {array,dataframe,complete}, optional, default: complete
        modes for the loader
    fullYear : bool
        extract one year accoring to firstMonth and year arguments
    firstMonth : {January, February, March, ... , December}
        start full year with this month
    year : {-1, 0, 1, 2, ...}
        year to use for full year. -1 will import the last 12 months. 0 (1) will import from the first month of the first (second) year.
    sortMonths : bool
        sort monthly data such that it starts with January

    Attributes
    ----------
    monData : :obj:`dict` of :obj:`ndarray`
        Dictionary of 1D-numpy arrays containing the monthly printed values
    houData : :obj:`dict` of :obj:`ndarray`
        Dictionary of 1D-numpy arrays containing the hourly printed values
    steData : :obj:`pandas.DataFrame`
        Pandas Dataframe of data printed in a custom timestep
    monDataDf : :obj:`pandas.dataframe`
        Dataframe containingt the monthly printed values
    houDataDf : :obj:`pandas.dataframe`
        Dataframe containingt the hourly printed values
    steDataDf : :obj:`pandas.DataFrame`
        Dataframe containingt the values printed in timesteps
    """
    def __init__(self, path, fileNameList=False, mode='complete',fullYear ='True',firstMonth='January',year=-1, sortMonths=False):

        self.path = path
        self.mode = mode
        self.fullYear = fullYear
        self.firstMonth = firstMonth
        self.year = year
        self.sortMonths = sortMonths

        if self.mode == 'dataframe':
            self.monData = None
            self.houData = None
            self.steData = None
            self.monDataDf = pd.DataFrame()
            self.houDataDf = pd.DataFrame()
            self.steDataDf = pd.DataFrame()

        elif self.mode == 'array':
            self.monData = {}
            self.houData = {}
            self.steData = {}
            self.monDataDf = None
            self.houDataDf = None
            self.steDataDf = None

        elif self.mode == 'complete':
            self.monData = {}
            self.monDataDf = pd.DataFrame()
            self.houData = {}
            self.houDataDf = pd.DataFrame()
            self.steData = {}
            self.steDataDf = pd.DataFrame()

        else:
            raise ValueError('mode must be either "dataframe" or "array"')

        if not (fileNameList):
            fileNameList = os.listdir(self.path)

        for fileName in fileNameList:
            self.loadFile(fileName)

    def loadFile(self, file):
        """
        Loads file into the field variables

        Parameters
        ----------
        file : str
            name of the file to be loaded



        """
        pathFile = os.path.join(self.path, file)
        fileType = self._fileSniffer(pathFile)
        nRows = self._fileLen(pathFile)

        if fileType == _ResultsFileType.MONTHLY:
            file = pd.read_csv(pathFile, header=1, delimiter='\t', nrows=nRows - 26, mangle_dupe_cols=True).rename(
                columns=lambda x: x.strip())
            file = file[file.columns[:-1]]
            file['Number'] = file.index+pd.to_datetime(file['Month'][0].strip(), format='%B').month
            file.set_index('Number', inplace=True)
            if self.fullYear:
                if self.year==-1:
                    file=file[-12:]

                else:
                    firstMonthNumber = pd.to_datetime(self.firstMonth, format='%B').month + self.year * 12
                    try:
                        file = file.loc[firstMonthNumber:firstMonthNumber+11]

                    except:
                        raise ValueError(pathFile+' is not in the right Format to read Months '+str(firstMonthNumber)+' to '+str(firstMonthNumber+12))

                file['Number'] = pd.to_datetime(file['Month'].str.strip(), format='%B').dt.month
                file.set_index('Number', inplace=True)

            if self.sortMonths:
                file.sort_index(inplace=True)
            file['Datetime'] = pd.to_datetime(file['Month'].str.strip(), format='%B')

            if self.mode == 'dataframe' or self.mode == 'complete':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.monDataDf.columns)]
                self.monDataDf = pd.merge(self.monDataDf, file[cols_to_use], left_index=True, right_index=True, how='outer')

            if self.mode == 'array' or self.mode == 'complete':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.monData.keys())]
                dict = {k: num.array(v.tolist()) for k, v in file[cols_to_use].items()}
                self.monData = {**self.monData, **dict}

        elif fileType == _ResultsFileType.HOURLY:
            file = pd.read_csv(pathFile, header=1, delimiter='\t', nrows=nRows - 26).rename(columns=lambda x: x.strip())
            file["Period"] = datetime(2018, 1, 1) + pd.to_timedelta(file['Period'], unit='h')
            file.set_index('Period', inplace=True)
            
            if self.mode == 'dataframe' or self.mode == 'complete':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.houDataDf.columns)]
                self.houDataDf = pd.merge(self.houDataDf, file, left_index=True, right_index=True, how='outer')
                
            if self.mode == 'array' or self.mode == 'complete':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.houData.keys())]
                dict = {k: num.array(v.tolist()) for k, v in file[cols_to_use].items()}
                self.houData = {**self.houData, **dict}

        elif fileType == _ResultsFileType.TIMESTEP:
            file = pd.read_csv(pathFile, header=0, delimiter='\t', nrows=nRows - 1).rename(columns=lambda x: x.strip())
            file["TIME"] = datetime(2018, 1, 1) + pd.to_timedelta(file['TIME'], unit='h')
            file.set_index('TIME', inplace=True)
            
            if self.mode == 'dataframe' or self.mode == 'complete':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.steDataDf.columns)]
                self.steDataDf = pd.merge(self.steDataDf, file, left_index=True, right_index=True, how='outer')
                
            elif self.mode == 'array':
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.steData.keys())]
                dict = {k: num.array(v.tolist()) for k, v in file[cols_to_use].items()}
                self.steData = {**self.steData, **dict}

    def _fileSniffer(self, file):
        with open(file) as f:
            for i in range(3):
                if 'Month' in f.readline():
                    return _ResultsFileType.MONTHLY
                
        with open(file) as f:
            for i in range(3):
                if 'Period' in f.readline():
                    return _ResultsFileType.HOURLY

        with open(file) as f:
            for i in range(3):
                if 'TIME' in f.readline():
                    return _ResultsFileType.TIMESTEP

    def _fileLen(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1


class _ResultsFileType(Enum):
    MONTHLY = 1
    HOURLY = 2
    TIMESTEP = 3
