# pylint: skip-file
# type: ignore

#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as num
import pytrnsys.utils.utilsSpf as utils


class SimulationLoader:
    """Loads TRNSYS printer files.

    The TRNSYS printer files are loaded into the attributes monData (monthly data), houData (hourly data)
    and steData (timestep data) respectively.

    Args
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

    def __init__(
        self,
        path,
        fileNameList=None,
        mode="complete",
        fullYear=True,
        firstMonth="January",
        year=-1,
        sortMonths=False,
        monthlyUsed=True,
        hourlyUsed=True,
        timeStepUsed=True,
        footerPresent=True,
        individualFiles=False,
    ):

        self._path = path
        self._mode = mode
        self._fullYear = fullYear
        self._firstMonth = firstMonth
        self._year = year
        self._sortMonths = sortMonths

        self._monthlyUsed = monthlyUsed
        self._hourlyUsed = hourlyUsed
        self._timeStepUsed = timeStepUsed

        if self._mode == "dataframe":
            self.monData = None
            self.houData = None
            self.steData = None
            self.monDataDf = pd.DataFrame()
            self.houDataDf = pd.DataFrame()
            self.steDataDf = pd.DataFrame()

        elif self._mode == "array":
            self.monData = {}
            self.houData = {}
            self.steData = {}
            self.monDataDf = None
            self.houDataDf = None
            self.steDataDf = None

        elif self._mode == "complete":
            self.monData = {}
            self.monDataDf = pd.DataFrame()
            self.houData = {}
            self.houDataDf = pd.DataFrame()
            self.steData = {}
            self.steDataDf = pd.DataFrame()

        else:
            raise ValueError('mode must be either "dataframe" or "array"')

        if fileNameList is None or not fileNameList:
            fileNameList = os.listdir(self._path)

        for fileName in fileNameList:
            self.loadFile(fileName, individualFiles, footerPresent)

    def loadFile(self, file, individualFiles, footerPresent=True):
        """
        Loads file into the field variables

        Parameters
        ----------
        file : str
            name of the file to be loaded



        """
        firstMonthN = pd.to_datetime(self._firstMonth, format="%B").month
        if individualFiles:
            pathFile = file
        else:
            pathFile = os.path.join(self._path, file)
        fileType = self._fileSniffer(pathFile)
        nRows = self._fileLen(pathFile)

        self.myShortMonths = None

        if fileType == _ResultsFileType.MONTHLY and self._monthlyUsed == True:

            if footerPresent:
                file = pd.read_csv(pathFile, header=1, delimiter="\t", nrows=nRows - 26, mangle_dupe_cols=True).rename(
                    columns=lambda x: x.strip()
                )
            else:
                file = pd.read_csv(pathFile, header=1, delimiter="\t", nrows=nRows - 1, mangle_dupe_cols=True).rename(
                    columns=lambda x: x.strip()
                )
            file = file[file.columns[:-1]]
            file["Number"] = file.index + pd.to_datetime(file["Month"][0].strip(), format="%B").month
            file.set_index("Number", inplace=True)
            if self._fullYear:
                if self._year == -1:
                    file = file[-12:]

                else:
                    firstMonthNumber = firstMonthN + self._year * 12
                    try:
                        file = file.loc[firstMonthNumber : firstMonthNumber + 11]

                    except:
                        raise ValueError(
                            pathFile
                            + " is not in the right Format to read Months "
                            + str(firstMonthNumber)
                            + " to "
                            + str(firstMonthNumber + 12)
                        )

                file["Number"] = pd.to_datetime(file["Month"].str.strip(), format="%B").dt.month
                file.set_index("Number", inplace=True)

            if self._sortMonths:
                file.sort_index(inplace=True)
            file["Datetime"] = pd.to_datetime(file["Month"].str.strip(), format="%B")

            if self._mode == "dataframe" or self._mode == "complete":
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.monDataDf.columns)]
                self.monDataDf = pd.merge(
                    self.monDataDf, file[cols_to_use], left_index=True, right_index=True, how="outer"
                )

            if self._mode == "array" or self._mode == "complete":
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.monData.keys())]
                dict = {k: num.array(v.tolist()) for k, v in file[cols_to_use].items()}
                self.monData = {**self.monData, **dict}

            self.myShortMonths = utils.getShortMonthyNameArray(self.monDataDf["Month"].values)

        elif fileType == _ResultsFileType.HOURLY and self._hourlyUsed == True:
            if footerPresent:
                file = pd.read_csv(pathFile, header=1, delimiter="\t", nrows=nRows - 26).rename(
                    columns=lambda x: x.strip()
                )
            else:
                file = pd.read_csv(pathFile, header=1, delimiter="\t", nrows=nRows - 1).rename(
                    columns=lambda x: x.strip()
                )

            file.set_index("Period", inplace=True, drop=False)

            if self._fullYear:
                if self._year == -1:
                    try:
                        file = file[-8760:]
                    except:
                        file = file[-8758:]  # this is here because of the trnsys bug in type 99

                else:
                    firstHourNumber = (
                        datetime(2018, firstMonthN, 1) - datetime(2018, 1, 1)
                    ).days * 24 + self._year * 8760
                    try:
                        file = file.loc[firstHourNumber : firstHourNumber + 8760]

                    except:
                        raise ValueError(
                            pathFile
                            + " is not in the right Format to read hours "
                            + str(firstHourNumber)
                            + " to "
                            + str(firstHourNumber + 8760)
                        )

            period = datetime(2018, 1, 1) + pd.to_timedelta(file["Period"], unit="h")
            file["Period"] = period
            file.set_index("Period", inplace=True)

            if self._mode == "dataframe" or self._mode == "complete":
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.houDataDf.columns)]
                self.houDataDf = pd.merge(
                    self.houDataDf, file[cols_to_use], left_index=True, right_index=True, how="outer"
                )

            if self._mode == "array" or self._mode == "complete":
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.houData.keys())]
                dict = {k: num.array(v.tolist()) for k, v in file[cols_to_use].items()}
                self.houData = {**self.houData, **dict}

        elif fileType == _ResultsFileType.TIMESTEP and self._timeStepUsed == True:
            file = pd.read_csv(pathFile, header=0, delimiter="\t", nrows=nRows - 1).rename(columns=lambda x: x.strip())
            file["TIME"] = datetime(2018, 1, 1) + pd.to_timedelta(file["TIME"], unit="h")
            file.set_index("TIME", inplace=True)

            if self._mode == "dataframe" or self._mode == "complete":
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.steDataDf.columns)]
                self.steDataDf = pd.merge(self.steDataDf, file, left_index=True, right_index=True, how="outer")

            elif self._mode == "array":
                cols_to_use = [item for item in file.columns[:-1] if item not in set(self.steData.keys())]
                dict = {k: num.array(v.tolist()) for k, v in file[cols_to_use].items()}
                self.steData = {**self.steData, **dict}

    def _fileSniffer(self, file):  # detects which kind of file we need to read
        with open(file) as f:
            for i in range(3):
                if "Month" in f.readline():
                    return _ResultsFileType.MONTHLY

        with open(file) as f:
            for i in range(3):
                if "Period" in f.readline():
                    return _ResultsFileType.HOURLY

        with open(file) as f:
            for i in range(3):
                if "TIME" in f.readline():
                    return _ResultsFileType.TIMESTEP

    def _fileLen(self, fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def loadHourlyFile(self, file):

        file = pd.read_csv(pathFile, header=1, delimiter=";", nrows=nRows - 1).rename(columns=lambda x: x.strip())
        file.set_index("Time", inplace=True, drop=False)
        period = datetime(2018, 1, 1) + pd.to_timedelta(file["Time"], unit="h")
        file["Time"] = period
        file.set_index("Time", inplace=True)
        cols_to_use = [item for item in file.columns[:-1] if item not in set(self.houDataDf.columns)]
        self.houDataDf = pd.merge(self.houDataDf, file[cols_to_use], left_index=True, right_index=True, how="outer")


class _ResultsFileType(Enum):
    MONTHLY = 1
    HOURLY = 2
    TIMESTEP = 3
