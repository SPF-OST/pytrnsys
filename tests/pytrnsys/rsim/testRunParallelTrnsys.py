import inspect as _is
import pathlib as _pl

import jinja2 as _ja
import pytest as _pytest

import pytrnsys as _pt
import pytrnsys.rsim.runParallelTrnsys as _rpt


class TestRunParallelTrnsys:  # pylint: disable=too-few-public-methods
    @_pytest.mark.windows
    def testRunConfig(self):
        testDirPath = _pl.Path(__file__).parent

        inputDirPath = testDirPath / "data" / "input" / "05_pytrnsys_Files"
        expectedDckFilePath = testDirPath / "data" / "expected"

        self._createConfigFile(inputDirPath)

        inputDirPathAsString = str(inputDirPath)

        runParallelTrnsys = _rpt.RunParallelTrnsys(pathConfig=inputDirPathAsString)
        runParallelTrnsys.path = inputDirPathAsString
        runParallelTrnsys.readConfig(inputDirPathAsString, "Building_4Study.config")
        runParallelTrnsys.getConfig()
        runParallelTrnsys.overwriteForcedByUser = False

        runParallelTrnsys.runConfig()

        expectedDckFilePath = expectedDckFilePath / "pytrnsysRun.dck"
        actualDckFilePath = inputDirPath / "Building_4Study" / "pytrnsysRun" / "pytrnsysRun.dck"

        assert actualDckFilePath.read_text(encoding="windows-1252") == expectedDckFilePath.read_text(
            encoding="windows-1252"
        )

    @staticmethod
    def _createConfigFile(inputDirPath: _pl.Path) -> None:
        configFileTemplatePath = inputDirPath / "Building_4Study.config.jinja"

        pytrnsysModuleSourceFilePathAsString = _is.getsourcefile(_pt)
        assert pytrnsysModuleSourceFilePathAsString

        pytrnsysModuleDirPath = _pl.Path(pytrnsysModuleSourceFilePathAsString).parent
        pytrnsysDdcksPath = pytrnsysModuleDirPath.parent / "data" / "ddcks"

        templateContent = configFileTemplatePath.read_text()
        configFileTemplate = _ja.Template(templateContent)
        renderedConfigFileContent = configFileTemplate.render(pytrnsys_ddck_folder=str(pytrnsysDdcksPath))

        configFilePath = configFileTemplatePath.with_suffix("")
        configFilePath.write_text(renderedConfigFileContent)
