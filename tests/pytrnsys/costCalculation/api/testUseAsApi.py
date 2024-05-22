import pathlib as _pl
import pprint as _pp

import pytrnsys.costCalculation as _cc
import pytrnsys.costCalculation.createCostCalculations as _ccc
from . import _exampleInputs as _ei

_DATA_DIR_PATH = _pl.Path(__file__).parent / "data"


class TestUseApi:
    def testUseApi(self) -> None:
        resultsDirPath = _DATA_DIR_PATH / "input" / "ice-on-coil"

        pathAndResults = _ccc.loadResults(resultsDirPath, _cc.OTHER)

        reportWriter = _cc.resultsWriter.ResultsWriter()

        for pathAndResults in pathAndResults:
            iceStorageVolume = pathAndResults.result["VIceS"]
            config = _ei.SOLID_ICE_STORE_INPUT if iceStorageVolume < 20_000 else _ei.SLURRY_ICE_STORE_INPUT

            costCalculation = _ccc.createCostCalculation(config, pathAndResults)
            reportWriter.writeReportAndResults(config.parameters, costCalculation, shallWriteReport=True)

    def testConvertCostCalcJsonToConfigObject(self) -> None:
        costCalcJsonsDirPath = _DATA_DIR_PATH / "input" / "configJsons"

        for costCalcJsonPath in costCalcJsonsDirPath.iterdir():
            assert costCalcJsonPath.is_file()

            config = _cc.createConfig(costCalcJsonPath)

            _pp.pprint(config, indent=4)
