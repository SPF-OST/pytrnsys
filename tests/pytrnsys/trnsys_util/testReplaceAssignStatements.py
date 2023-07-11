import pathlib as _pl

import pytrnsys.trnsys_util.replaceAssignStatements as _ra

_DATA_DIR_PATH = _pl.Path(__file__).parent / "data" / "replaceAssignStatements"


class TestReplaceAssignStatements:
    def test(self):
        inputFilePath = _DATA_DIR_PATH / "icegrid_input.dck"
        expectedOutputFilePath = _DATA_DIR_PATH / "icegrid_expected_output.dck"

        inputContent = inputFilePath.read_text(encoding="utf8")
        expectedResult = expectedOutputFilePath.read_text(encoding="utf8")

        newAssignStatements = [
            _ra.AssignStatement(r"..\ddck\QSnk85\Profile_Snk_85_001.csv", "QSnk85unit"),
            _ra.AssignStatement(r"temp\ENERGY_BALANCE_MO_HP_85.Prt", "QSnk85unitPrintHP_EBal"),
        ]

        actualResult = _ra.replaceAssignStatementsBasedOnUnitVariables(inputContent, newAssignStatements)

        assert actualResult == expectedResult
