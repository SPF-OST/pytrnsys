import dataclasses as _dc
import json as _json
import pathlib as _pl
import typing as _tp

import pytest as _pt

import pytrnsys.ddck.replaceTokens as _replace
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
        actualDdckContent = _replace.replaceTokensWithDefaults(inputDdckFilePath)
        assert actualDdckContent == expectedDdckFilePath.read_text()

    @staticmethod
    def testReplaceTokensWithDefaultsMissingInputVariableDefaults():
        inputDdckFilePath = _REPLACE_WITH_DEFAULTS_DATA_DIR / "type977_v1_input_missing_default.ddck"
        result = _replace.replaceTokensWithDefaults(inputDdckFilePath)
        assert _res.isError(result)
        error = _res.error(result)
        print(error.message)
        expectedErrorMessage = """\
An error occurred while substituting the defaults for the placeholders in file type977_v1_input_missing_default.ddck:
No placeholder values were provided for the computed variables at the following locations (line number:column number):
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

        result = _replace.replaceTokens(ddckFile.input, ddckFile.componentName, names)
        _res.throwIfError(result)
        actualDdckContent = _res.value(result)

        ddckFile.actual.parent.mkdir(parents=True, exist_ok=True)
        ddckFile.actual.write_text(actualDdckContent)

        assert ddckFile.actual.read_text() == ddckFile.expected.read_text(encoding="windows-1252")

    @staticmethod
    def testReplaceTokensNonexistentPort() -> None:
        inputDdckFilePath = _REPLACE_WITH_NAMES_DATA_DIR / "type951_non_existent_port.ddck"
        componentName = "Ghx"
        computedNamesByPort = {"In": {"@temp": "TFoo", "@Mfr": "MBar"}, "Out": {"@temp": "TGhx"}}

        result = _replace.replaceTokens(
            inputDdckFilePath,
            componentName,
            computedNamesByPort,
        )

        assert _res.isError(result)
        error = _res.error(result)
        print(error.message)
        expectedErrorMessage = """\
Error replacing placeholders in file type951_non_existent_port.ddck:
Unknown port `HotIn`."""
        assert error.message == expectedErrorMessage
