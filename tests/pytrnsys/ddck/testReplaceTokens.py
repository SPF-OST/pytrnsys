import dataclasses as _dc
import json as _json
import pathlib as _pl
import typing as _tp

import pytest as _pt

import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.ddck.replaceTokens.placeholders as _rtph
import pytrnsys.ddck.replaceTokens.withoutPlaceholders as _rtwph
import pytrnsys.utils.result as _res

_REPLACE_WITH_DEFAULTS_DATA_DIR = _pl.Path(__file__).parent / "defaults"
_REPLACE_WITH_NAMES_DATA_DIR = _pl.Path(__file__).parent / "names"
_REPLACE_WITH_NAMES_IN_PROJECTS_DATA_DIR = _pl.Path(__file__).parent / "names_in_projects"


class _Paths:  # pylint: disable=too-few-public-methods
    def __init__(self, projectDirPath: _pl.Path) -> None:
        self.actualDdckDirPath = projectDirPath / "actual"
        self.inputDirPath = projectDirPath / projectDirPath.name
        self.inputDdckDirPath = self.inputDirPath / "ddck"
        self.expectedDdckDirPath = projectDirPath / "expected"

        self.ddckPlaceHolderValuesFilePath = self.inputDirPath / "DdckPlaceHolderValues.json"


@_dc.dataclass
class _DdckFile:  # pylint: disable=too-few-public-methods
    projectDirPath: _pl.Path
    ddckPlaceHoldervaluesFilePath: _pl.Path
    componentName: str

    input: _pl.Path
    actual: _pl.Path
    expected: _pl.Path

    @property
    def testId(self) -> str:
        relativeInputPath = self.input.relative_to(self.projectDirPath)
        return relativeInputPath.as_posix()


def getProjectsDdckFiles() -> _tp.Iterable[_DdckFile]:
    for projectDirPath in _REPLACE_WITH_NAMES_IN_PROJECTS_DATA_DIR.iterdir():
        assert projectDirPath.is_dir()

        paths = _Paths(projectDirPath)

        inputDdckFilesPaths = paths.inputDdckDirPath.rglob("*.ddck")

        for inputDdckFilePath in inputDdckFilesPaths:
            relativeDdckFilePath = inputDdckFilePath.relative_to(paths.inputDdckDirPath)

            actualDdckFilePath = paths.actualDdckDirPath / relativeDdckFilePath
            expectedDdckFilePath = paths.expectedDdckDirPath / relativeDdckFilePath

            componentName = inputDdckFilePath.parent.name

            yield _DdckFile(
                projectDirPath,
                paths.ddckPlaceHolderValuesFilePath,
                componentName,
                inputDdckFilePath,
                actualDdckFilePath,
                expectedDdckFilePath,
            )


_REPLACE_WITH_NAME_PROJECTS_TEST_CASES = [_pt.param(p, id=p.testId) for p in getProjectsDdckFiles()]


class TestReplaceTokens:
    @staticmethod
    def testReplaceTokensWithDefaults():
        inputDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_input.ddck"
        expectedDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_expected.ddck"
        componentName = "IGNORED"
        actualDdckContent = _rtwph.replaceTokensWithDefaults(
            inputDdckFilePath, componentName, _dv.DefaultVisibility.GLOBAL
        )
        assert actualDdckContent == expectedDdckFilePath.read_text()

    @staticmethod
    def testReplaceTokensIncorrectUsageOfTrace():
        """ This test does not check the full error message, because the order of the options is flaky. """

        inputDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_input_TRACE_incorrect.ddck"
        componentName = "IGNORED"
        # with _pt.raises(AssertionError):

        error = _rtwph.replaceTokensWithDefaults(
                inputDdckFilePath, componentName, _dv.DefaultVisibility.GLOBAL
            )
        assert """\
Error processing file `type977_v1_input_TRACE_incorrect.ddck`:
No terminal matches 'T' in the current parser context, at line 4 col 1

TRACE 15 25
^
""" in error.message

    # TODO: add trace used correctly

    @staticmethod
    def testReplaceTokensWithDefaultsMissingInputVariableDefaults():
        inputDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_input_missing_default.ddck"
        componentName = "IGNORED"
        result = _rtwph.replaceTokensWithDefaults(inputDdckFilePath, componentName, _dv.DefaultVisibility.GLOBAL)
        assert _res.isError(result)
        error = _res.error(result)
        print(error.message)
        expectedErrorMessage = """\
Error processing file `type977_v1_input_missing_default.ddck`:
Could not substitute the defaults for the placeholders:
No default values were provided for the computed variables at the following locations (line number:column number):
\t26:14
\t27:13
\t28:15
"""
        assert error.message == expectedErrorMessage

    @staticmethod
    @_pt.mark.parametrize("ddckFile", _REPLACE_WITH_NAME_PROJECTS_TEST_CASES)
    def testReplaceTokensInProject(ddckFile: _DdckFile):
        serializedDdckPlaceHolderValues = ddckFile.ddckPlaceHoldervaluesFilePath.read_text(encoding="utf8")
        ddckPlaceHolderValues = _json.loads(serializedDdckPlaceHolderValues)

        names = ddckPlaceHolderValues.get(ddckFile.componentName) or {}

        result = _rtph.replaceTokens(ddckFile.input, ddckFile.componentName, names, _dv.DefaultVisibility.GLOBAL)
        _res.throwIfError(result)
        actualDdckContent = _res.value(result)

        ddckFile.actual.parent.mkdir(parents=True, exist_ok=True)
        ddckFile.actual.write_text(actualDdckContent)

        assert ddckFile.actual.read_text() == ddckFile.expected.read_text(encoding="windows-1252")

    @staticmethod
    def testReplaceComputedVariables():
        type861DirPath = _REPLACE_WITH_NAMES_DATA_DIR / "type861"
        inputDdckFilePath = type861DirPath / "input.ddck"

        componentName = "IceStore"
        computedNamesByPort = {
            "In": {"@temp": "TIn", "@mfr": "MIn", "@cp": "CPWAT", "@rho": "RHOWAT"},
            "Out": {"@temp": "TOut", "@revtemp": "TOutRev"},
        }

        result = _rtph.replaceTokens(
            inputDdckFilePath, componentName, computedNamesByPort, _dv.DefaultVisibility.GLOBAL
        )

        assert not _res.isError(result)

        value = _res.value(result)

        expectedOutputDdckFilePath = type861DirPath / "expected_output.ddck"
        assert value == expectedOutputDdckFilePath.read_text(encoding="utf8")

    @staticmethod
    def testReplaceEnergyVariables():
        componentName = "QSnk60"
        inputContent = """\
******************************************************************************************
** outputs to energy balance in kW
******************************************************************************************
EQUATIONS 4
@energy(in, el, :, hp, comp) = :PelAuxComp_kW
@energy(out, heat, :, demand) = :P
@energy(out, heat, :, tess, loss) = :dQlossTess
@energy(out, heat, :, tess, acum) = :dQ
*********************************
"""

        computedNamesByPort = {}
        result = _rtph.replaceTokensInString(
            inputContent, componentName, computedNamesByPort, _dv.DefaultVisibility.GLOBAL
        )

        assert not _res.isError(result)

        actualOutput = _res.value(result)

        expectedOutput = """\
******************************************************************************************
** outputs to energy balance in kW
******************************************************************************************
EQUATIONS 4
elSysIn_QSnk60HpComp = QSnk60PelAuxComp_kW
qSysOut_QSnk60Demand = QSnk60P
qSysOut_QSnk60TessLoss = QSnk60dQlossTess
qSysOut_QSnk60TessAcum = QSnk60dQ
*********************************
"""

        assert actualOutput == expectedOutput

    @staticmethod
    def testReplaceTokensNonexistentPort() -> None:
        inputDdckFilePath = _REPLACE_WITH_NAMES_DATA_DIR / "type951_non_existent_port.ddck"
        componentName = "Ghx"
        computedNamesByPort = {"In": {"@temp": "TFoo", "@Mfr": "MBar"}, "Out": {"@temp": "TGhx"}}

        result = _rtph.replaceTokens(
            inputDdckFilePath, componentName, computedNamesByPort, _dv.DefaultVisibility.GLOBAL
        )

        assert _res.isError(result)
        error = _res.error(result)
        print(error.message)
        expectedErrorMessage = f"""\
Could not replace placeholders in ddck file `{inputDdckFilePath}`:
Unknown port `HotIn`."""
        assert error.message == expectedErrorMessage
