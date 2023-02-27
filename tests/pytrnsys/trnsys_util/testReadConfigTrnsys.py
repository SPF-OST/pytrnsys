import pathlib as _pl
import typing as _tp

import pytest as _pt

import pytrnsys.trnsys_util.readConfigTrnsys as _rct

_DATA_DIR_PATH = _pl.Path(__file__).parent / "data"


def _getRunLines(basePath: _tp.Optional[_pl.Path]) -> _tp.Sequence[str]:
    lines = [
        "bool ignoreOnlinePlotter  True",
        "int reduceCpu  4",
        "bool parseFileCreated True",
        "bool runCases True",
        "bool checkDeck True",
        'string outputLevel "INFO"',
    ]
    if not basePath:
        lines += [
            'string pathToConnectionInfo "C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json"',
        ]
    lines += [
        "bool doAutoUnitNumbering True",
        "bool generateUnitTypesUsed True",
        "bool addAutomaticEnergyBalance True",
    ]
    if not basePath:
        lines += [
            'string PROJECT$ "C:\\Users\\epic.user\\EpicSimulation\\ddck"',
        ]
    lines += [
        'string trnsysExePath "C:\\Trnsys18\\Exe\\TRNExe.exe"',
        'string scaling "False"',
    ]
    if not basePath:
        lines += [
            'string projectPath "C:\\Users\\epic.user\\EpicSimulation"',
        ]
    lines += [
        'string nameRef "DoublePipeDebug"',
        'string runType "runFromConfig"',
        "deck START 0",
        "deck STOP  8760",
        "deck dtSim 1",
        "PROJECT$ generic\\head",
        "PROJECT$ control\\hydraulic_control",
        "PROJECT$ hydraulic\\hydraulic",
        "PROJECT$ QSrc1\\QSrc",
        "PROJECT$ generic\\end",
    ]
    if basePath:
        lines += [
            f"string pathToConnectionInfo {basePath / 'DdckPlaceHolderValues.json'}",
            f"string PROJECT$ {basePath / 'ddck'}",
            f"string projectPath {basePath}",
        ]
    return lines


_LINES_RUN = _getRunLines(basePath=None)
_LINES_RUN_WITHOUT_PATHS = _getRunLines(basePath=_DATA_DIR_PATH)


def _getProcessLines(basePath: _tp.Optional[_pl.Path]) -> _tp.Sequence[str]:
    lines = [
        "bool processParallel False",
        "bool processQvsT False",
        "bool cleanModeLatex False",
        "bool forceProcess  True",
        "bool setPrintDataForGle True",
        "bool isTrnsys True",
        "int reduceCpu 1",
        'string outputLevel "DEBUG"',
        "bool createLatexPdf True",
        "bool calculateHeatDemand True",
        "int yearReadedInMonthlyFile -1",
        "int firstMonthUsed 0",
        "int numberOfYearsInHourlyFile 1",
        'string latexNames "latexNames.json"',
    ]
    if not basePath:
        lines += [
            'string pathBase "C:\\Users\\epic.user\\EpicSimulation"',
        ]
    lines += ['string dllTrnsysPath "C:\\Trnsys18\\UserLib\\ReleaseDlls"', 'stringArray plotHourly "TInQSrc1"']
    if basePath:
        lines += [f"string pathBase {basePath}"]
    return lines


_PROCESS_LINES = _getProcessLines(basePath=None)
_PROCESS_LINES_WITHOUT_PATHS = _getProcessLines(basePath=_DATA_DIR_PATH)


def _getInputs(
    basePath: _tp.Optional[_pl.Path], configType: _tp.Literal["run", "process"]
) -> _tp.Mapping[str, _tp.Any]:
    inputs = {
        "calc": [],
        "calcCumSumHourly": [],
        "calcCumSumTimeStep": [],
        "calcDaily": [],
        "calcHourly": [],
        "calcHourlyTest": [],
        "calcMonthly": [],
        "calcMonthlyFromHourly": [],
        "calcMonthlyMax": [],
        "calcMonthlyMin": [],
        "calcMonthlyTest": [],
        "calcTest": [],
        "calcTimeStep": [],
        "calcTimeStepTest": [],
        "reduceCpu": 4,
    }
    if configType == "run":
        inputs["PROJECT$"] = "C:\\Users\\epic.user\\EpicSimulation\\ddck"
        inputs["addAutomaticEnergyBalance"] = True
        inputs["checkDeck"] = True
        inputs["doAutoUnitNumbering"] = True
        inputs["generateUnitTypesUsed"] = True
        inputs["ignoreOnlinePlotter"] = True
        inputs["nameRef"] = "DoublePipeDebug"
        inputs["outputLevel"] = "INFO"
        inputs["parseFileCreated"] = True
        inputs["pathToConnectionInfo"] = "C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json"
        inputs["projectPath"] = "C:\\Users\\epic.user\\EpicSimulation"
        inputs["runCases"] = True
        inputs["runType"] = "runFromConfig"
        inputs["scaling"] = "False"
        inputs["trnsysExePath"] = "C:\\Trnsys18\\Exe\\TRNExe.exe"
        if basePath:
            inputs["PROJECT$"] = str(basePath / "ddck")
            inputs["pathToConnectionInfo"] = str(basePath / "DdckPlaceHolderValues.json")
            inputs["projectPath"] = basePath

    elif configType == "process":
        inputs["calculateHeatDemand"] = True
        inputs["cleanModeLatex"] = False
        inputs["createLatexPdf"] = True
        inputs["dllTrnsysPath"] = "C:\\Trnsys18\\UserLib\\ReleaseDlls"
        inputs["firstMonthUsed"] = 0
        inputs["forceProcess"] = True
        inputs["isTrnsys"] = True
        inputs["latexNames"] = "latexNames.json"
        inputs["numberOfYearsInHourlyFile"] = 1
        inputs["outputLevel"] = "DEBUG"
        inputs["pathBase"] = "C:\\Users\\epic.user\\EpicSimulation"
        inputs["plotHourly"] = [["TInQSrc1"]]
        inputs["processParallel"] = False
        inputs["processQvsT"] = False
        inputs["reduceCpu"] = 1
        inputs["setPrintDataForGle"] = True
        inputs["yearReadedInMonthlyFile"] = -1
        if basePath:
            inputs["pathBase"] = basePath

    return inputs


_INPUTS_RUN = _getInputs(basePath=None, configType="run")
_INPUTS_RUN_WITHOUT_PATHS = _getInputs(basePath=_DATA_DIR_PATH, configType="run")
_INPUTS_PROCESS = _getInputs(basePath=None, configType="process")
_INPUTS_PROCESS_WITHOUT_PATHS = _getInputs(basePath=_DATA_DIR_PATH, configType="process")


class TestReadConfigTrnsys:
    def setup(self):
        self.reader = _rct.ReadConfigTrnsys()  # pylint: disable=attribute-defined-outside-init
        self.inputs = {}  # pylint: disable=attribute-defined-outside-init

    @_pt.mark.parametrize(
        "userInput, response",
        [
            ("yes", True),
            ("Yes", True),
            ("true", True),
            ("True", True),
            ("Anything_else?", False),
            ("t", True),
            ("T", True),
            ("1", True),
        ],
    )
    def testStr2bool(self, userInput, response):
        assert self.reader.str2bool(userInput) == response

    def testReadFileRunConfig(self):
        name = "run.config_with_absolute_paths"
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs, parseFileCreated=False, controlDataType=False)
        assert self.inputs == _INPUTS_RUN
        assert lines == _LINES_RUN

    def testReadFileRunConfigWithoutAnyPaths(self):
        name = "run.config_without_any_paths"
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs, parseFileCreated=False, controlDataType=False)
        assert self.inputs == _INPUTS_RUN_WITHOUT_PATHS
        assert lines == _LINES_RUN_WITHOUT_PATHS

    def testReadFileProcessConfig(self):
        name = "process.config_with_absolute_paths"
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs, parseFileCreated=False, controlDataType=False)
        assert self.inputs == _INPUTS_PROCESS
        assert lines == _PROCESS_LINES

    def testReadFileProcessConfigWithoutPaths(self):
        name = "process.config_without_paths"
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs, parseFileCreated=False, controlDataType=False)
        assert self.inputs == _INPUTS_PROCESS_WITHOUT_PATHS
        assert lines == _PROCESS_LINES_WITHOUT_PATHS
