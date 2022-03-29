import inspect as _is
import pathlib as _pl

import pytest as _pytest

import pytrnsys as _pt
import pytrnsys.rsim.runParallelTrnsys as _rpt


def _getPytrnsysSourceDirPath() -> _pl.Path:
    pytrnsysModuleSourceFilePathAsString = _is.getsourcefile(_pt)
    assert pytrnsysModuleSourceFilePathAsString
    pytrnsysModuleDirPath = _pl.Path(pytrnsysModuleSourceFilePathAsString).parents[1]
    return pytrnsysModuleDirPath


PYTRNSYS_SOURCE_DIR_PATH = _getPytrnsysSourceDirPath()


class TestRunParallelTrnsys:  # pylint: disable=too-few-public-methods
    @_pytest.mark.windows
    def testRunConfig(self):
        testDirPath = _pl.Path(__file__).parent

        inputDirPath = testDirPath / "data" / "input"
        pytrnsysFilesDirPath = inputDirPath / "05_pytrnsys_Files"
        expectedDirPath = testDirPath / "data" / "expected"

        self._createConfigFile(inputDirPath)

        pytrnsysFilesDirAsString = str(pytrnsysFilesDirPath)

        runParallelTrnsys = _rpt.RunParallelTrnsys(pathConfig=pytrnsysFilesDirAsString)
        runParallelTrnsys.path = pytrnsysFilesDirAsString
        runParallelTrnsys.readConfig(pytrnsysFilesDirAsString, "Building_4Study.config")
        runParallelTrnsys.getConfig()
        runParallelTrnsys.overwriteForcedByUser = False

        runParallelTrnsys.runConfig()

        actualDckFilePath = pytrnsysFilesDirPath / "Building_4Study" / "pytrnsysRun" / "pytrnsysRun.dck"
        expectedDdckFileContent = self._getExpectedDckFileContent(expectedDirPath)

        assert actualDckFilePath.read_text(encoding="windows-1252") == expectedDdckFileContent

    @staticmethod
    def _createConfigFile(inputDirPath: _pl.Path) -> None:
        configFileTemplatePath = inputDirPath / "05_pytrnsys_Files" / "Building_4Study.config.template"

        templateContent = configFileTemplatePath.read_text()

        content = templateContent
        content = content.replace("$PYTRNSYS_FOLDER", str(PYTRNSYS_SOURCE_DIR_PATH))
        content = content.replace("$INPUT_FOLDER", str(inputDirPath))

        configFilePath = configFileTemplatePath.with_suffix("")
        configFilePath.write_text(content)

    @staticmethod
    def _getExpectedDckFileContent(expectedDirPath):
        expectedDckFileTemplatePath = expectedDirPath / "pytrnsysRun.dck.template"
        expectedDdckFileTemplateContent = expectedDckFileTemplatePath.read_text(encoding="windows-1252")
        expectedDdckFileContent = expectedDdckFileTemplateContent.replace(
            "$PYTRNSYS_FOLDER", str(PYTRNSYS_SOURCE_DIR_PATH)
        )
        return expectedDdckFileContent
