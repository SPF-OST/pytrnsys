import pathlib as _pl
import pprint as _pp

import pytrnsys.costCalculation as _cc
import pytrnsys.costCalculation.createCostCalculations as _ccc

from .. import _helper
from . import _exampleInputs as _ei

_DATA_DIR_PATH = _pl.Path(__file__).parent / "data"


class TestUseApi:
    def testUseApi(self, caplog) -> None:
        """
        This test is mainly there to show how to use the cost calculation functionality of `pytrnsys`
        as an API.

        However, it being a test, it also makes sure the results produced are what it expects them
        to be. Therefore, there are some lines of code which you won't need if you want to run the
        cost calculation from your own script. These lines are marked as such with a comment.
        """
        resultsDirName = "ice-on-coil"

        # The following two lines are only needed to verify the results and not to generate them
        testHelper = _helper.Helper(_DATA_DIR_PATH, resultsDirName, caplog)
        testHelper.setup()

        # Just use your results dir here, instead of the test helper's
        pathsAndResults = _ccc.loadResults(testHelper.actualResultsDir, _cc.OTHER)

        reportWriter = _cc.resultsWriter.ResultsWriter()
        for pathAndResults in pathsAndResults:
            iceStorageVolume = pathAndResults.result["VIceS"]
            config = _ei.SOLID_ICE_STORE_INPUT if iceStorageVolume < 20_000 else _ei.SLURRY_ICE_STORE_INPUT

            costCalculation = _ccc.createCostCalculation(config, pathAndResults)
            reportWriter.writeReportAndResults(config.parameters, costCalculation, shallWriteReport=True)

        # This line is only needed to verify the results and not to generate them
        testHelper.assertResultsAreAsExpected()

    def testConvertCostCalcJsonToConfigObject(self) -> None:
        """
        This test is just a utility which you can use to convert existing cost calculation config JSON
        files into their corresponding Python objects.

        The test doesn't really check the results and will always succeed.
        """
        costCalcJsonsDirPath = _DATA_DIR_PATH / "input" / "configJsons"

        for costCalcJsonPath in costCalcJsonsDirPath.iterdir():
            assert costCalcJsonPath.is_file()

            config = _cc.createConfig(costCalcJsonPath)

            _pp.pprint(config)
