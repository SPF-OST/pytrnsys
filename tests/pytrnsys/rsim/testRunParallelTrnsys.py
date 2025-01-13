import collections.abc as _cabc
import contextlib as _cl
import dataclasses as _dc
import inspect as _is
import pathlib as _pl

import pytest as _pytest

import pytrnsys as _pt
import pytrnsys.rsim.runParallelTrnsys as _rpt
import pytrnsys.utils.result as _res

TEST_DIR_PATH = _pl.Path(__file__).parent


def _getPytrnsysSourceDirPath() -> _pl.Path:
    pytrnsysModuleSourceFilePathAsString = _is.getsourcefile(_pt)
    assert pytrnsysModuleSourceFilePathAsString
    pytrnsysModuleDirPath = _pl.Path(
        pytrnsysModuleSourceFilePathAsString
    ).parents[1]
    return pytrnsysModuleDirPath


PYTRNSYS_SOURCE_DIR_PATH = _getPytrnsysSourceDirPath()


@_dc.dataclass
class TestCase:
    def __init__(
        self,
        name: str,
        relativeConfigTemplateFilePath: str,
        relativeDckFilePath: str,
        pathVariables: _cabc.Mapping[str, str | _pl.Path],
    ) -> None:
        self.name = name
        self.relativeConfigTemplateFilePath = _pl.Path(
            relativeConfigTemplateFilePath
        )
        self.relativeDckFilePath = _pl.Path(relativeDckFilePath)
        self.pathVariables = {
            n: (
                pp
                if (pp := _pl.Path(p)).is_absolute()
                else self.inputDirPath / pp
            )
            for n, p in pathVariables.items()
        }

        if (
            self.relativeConfigTemplateFilePath.is_absolute()
            or self.relativeConfigTemplateFilePath.suffixes
            != [
                ".config",
                ".template",
            ]
        ):
            raise ValueError(
                "Config template file path must be relative and have .config.template extension.",
                relativeConfigTemplateFilePath,
            )

        if (
            self.relativeDckFilePath.is_absolute()
            or self.relativeDckFilePath.suffix != ".dck"
        ):
            raise ValueError(
                "Dck template file path must be relative and have .dck.template extension.",
                relativeDckFilePath,
            )

    @property
    def inputDirPath(self) -> _pl.Path:
        return TEST_DIR_PATH / "data" / self.name / "input"

    @property
    def pytrnsysFilesDirPath(self) -> _pl.Path:
        return self.inputDirPath / self.relativeConfigTemplateFilePath.parent

    @property
    def expectedDirPath(self) -> _pl.Path:
        return TEST_DIR_PATH / "data" / self.name / "expected"


def getTestCases() -> _cabc.Iterable[TestCase]:
    yield TestCase(
        "EU_Plural",
        "05_pytrnsys_Files/Building_4Study.config.template",
        "05_pytrnsys_Files/Building_4Study/pytrnsysRun/pytrnsysRun.dck",
        {
            "$INPUT_FOLDER": ".",
            "$PYTRNSYS_FOLDER": PYTRNSYS_SOURCE_DIR_PATH,
        },
    )

    yield TestCase(
        "SwissSTES",
        "Linth-Ausserschwyz/Verteilnetz/run_mod.config.template",
        "Linth-Ausserschwyz/Verteilnetz/results/pytrnsysRun/pytrnsysRun.dck",
        pathVariables={"$PROJECT": "Linth-Ausserschwyz/Verteilnetz"},
    )


class TestRunParallelTrnsys:  # pylint: disable=too-few-public-methods
    @_pytest.mark.parametrize(
        "testCase", [_pytest.param(tc, id=tc.name) for tc in getTestCases()]
    )
    def testRunConfig(self, testCase: TestCase):
        configFilePath = self._createConfigFile(testCase)

        pytrnsysFilesDirPath = (
            testCase.inputDirPath
            / testCase.relativeConfigTemplateFilePath.parent
        )
        with _cl.chdir(pytrnsysFilesDirPath):
            pytrnsysFilesDirAsString = str(pytrnsysFilesDirPath)

            runParallelTrnsys = _rpt.RunParallelTrnsys(
                pathConfig=pytrnsysFilesDirAsString
            )
            runParallelTrnsys.path = pytrnsysFilesDirAsString
            runParallelTrnsys.readConfig(
                pytrnsysFilesDirAsString, configFilePath.name
            )
            runParallelTrnsys.getConfig()
            runParallelTrnsys.overwriteForcedByUser = False

            result = runParallelTrnsys.runConfig()
            _res.throwIfError(result)

            actualDckFilePath = (
                testCase.inputDirPath / testCase.relativeDckFilePath
            )
            expectedDdckFileContent = self._getExpectedDckFileContent(testCase)

            assert (
                actualDckFilePath.read_text(encoding="windows-1252")
                == expectedDdckFileContent
            )

    @classmethod
    def _createConfigFile(cls, testCase: TestCase) -> _pl.Path:
        configFileTemplatePath = (
            testCase.inputDirPath / testCase.relativeConfigTemplateFilePath
        )

        configFilePath = configFileTemplatePath.with_suffix("")

        cls._createFileFromTemplate(
            configFileTemplatePath, testCase.pathVariables, configFilePath
        )

        return configFilePath

    @classmethod
    def _createFileFromTemplate(
        cls,
        templateFilePath: _pl.Path,
        pathVariables: _cabc.Mapping[str, _pl.Path],
        outputFilePath: _pl.Path,
    ) -> None:
        content = cls._getContentFromTemplate(templateFilePath, pathVariables)
        outputFilePath.write_text(content)

    @staticmethod
    def _getContentFromTemplate(
        templateFilePath: _pl.Path, pathVariables: _cabc.Mapping[str, _pl.Path]
    ) -> str:
        templateContent = templateFilePath.read_text()
        content = templateContent
        for variableName, path in pathVariables.items():
            content = content.replace(variableName, str(path))
        return content

    @classmethod
    def _getExpectedDckFileContent(cls, testCase: TestCase) -> str:
        dckTemplateFileName = f"{testCase.relativeDckFilePath.name}.template"

        expectedDckFileTemplatePath = (
            testCase.expectedDirPath / dckTemplateFileName
        )

        expectedContent = cls._getContentFromTemplate(
            expectedDckFileTemplatePath, testCase.pathVariables
        )

        return expectedContent
