import pathlib as _pl

import pytrnsys.ddck.replaceVariables as _replace


def testReplaceComputedVariablesWithDefaults():
    containingDirPath = _pl.Path(__file__).parent
    dataDirPath = containingDirPath / "data"

    inputDdckFilePath = dataDirPath / "type977_v1_input.ddck"
    actualDdckFilePath = dataDirPath / "type977_v1_actual.ddck"
    expectedDdckFilePath = dataDirPath / "type977_v1_expected.ddck"

    _replace.replaceComputedVariablesWithDefaults(inputDdckFilePath, actualDdckFilePath)

    assert actualDdckFilePath.read_text() == expectedDdckFilePath.read_text()
