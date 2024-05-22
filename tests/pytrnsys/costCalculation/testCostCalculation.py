# pylint: skip-file
# type: ignore

import pathlib as _pl

import pytest as _pt

import pytrnsys.costCalculation as _cc

from . import _helper


class TestCostCalculation:
    CONFIG_FILE_RESULTS_DIR_PAIRS = [
        ["costSolarIce_HpSplit.json", "results"],
        ["costSolarIce_HpSplit_eYearly0.json", "results_eYearly0"],
        ["costSolarIce_HpSplit_typeOfProcess_json.json", "results_json_files"],
    ]

    @_pt.mark.parametrize(["costConfigFileName", "resultsDirName"], CONFIG_FILE_RESULTS_DIR_PAIRS)
    def test(
        self,
        costConfigFileName: str,
        resultsDirName: str,
        caplog: _pt.LogCaptureFixture,
    ):

        dataDirPath = _pl.Path(__file__).parent / "data"
        helper = _helper.Helper(dataDirPath, resultsDirName, caplog, costConfigFileName)
        helper.setup()

        actualResultsDir = helper.actualResultsDir
        costParametersFilePath = helper.costParametersFilePath

        _cc.calculateCostsAndWriteReports(
            costParametersFilePath,
            actualResultsDir,
            shallWriteReport=True,
            processType=_cc.OTHER,
        )

        helper.assertResultsAreAsExpected()
