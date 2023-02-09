import pytest as _pt
import pathlib as _pl

import pytrnsys.trnsys_util.readConfigTrnsys as _rct

DATA_DIR_PATH = _pl.Path(__file__).parent / "data"

ORIGINAL_LINES = ['bool ignoreOnlinePlotter  True',
                  'int reduceCpu  4',
                  'bool parseFileCreated True',
                  'bool runCases True',
                  'bool checkDeck True',
                  'string outputLevel "INFO"',
                  'string pathToConnectionInfo '
                  '"C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json"',
                  'bool doAutoUnitNumbering True',
                  'bool generateUnitTypesUsed True',
                  'bool addAutomaticEnergyBalance True',
                  'string PROJECT$ '
                  '"C:\\Users\\epic.user\\EpicSimulation\\ddck"',
                  'string trnsysExePath "C:\\Trnsys18\\Exe\\TRNExe.exe"',
                  'string scaling "False"',
                  'string projectPath '
                  '"C:\\Users\\epic.user\\EpicSimulation"',
                  'string nameRef "DoublePipeDebug"',
                  'string runType "runFromConfig"',
                  'deck START 0',
                  'deck STOP  8760',
                  'deck dtSim 1',
                  'PROJECT$ generic\\head',
                  'PROJECT$ control\\hydraulic_control',
                  'PROJECT$ hydraulic\\hydraulic',
                  'PROJECT$ QSrc1\\QSrc',
                  'PROJECT$ generic\\end']

LINES_WITHOUT = ['bool ignoreOnlinePlotter  True',
                 'int reduceCpu  4',
                 'bool parseFileCreated True',
                 'bool runCases True',
                 'bool checkDeck True',
                 'string outputLevel "INFO"',
                 'bool doAutoUnitNumbering True',
                 'bool generateUnitTypesUsed True',
                 'bool addAutomaticEnergyBalance True',
                 'string trnsysExePath "C:\\Trnsys18\\Exe\\TRNExe.exe"',
                 'string scaling "False"',
                 'string nameRef "DoublePipeDebug"',
                 'string runType "runFromConfig"',
                 'deck START 0',
                 'deck STOP  8760',
                 'deck dtSim 1',
                 'PROJECT$ generic\\head',
                 'PROJECT$ control\\hydraulic_control',
                 'PROJECT$ hydraulic\\hydraulic',
                 'PROJECT$ QSrc1\\QSrc',
                 'PROJECT$ generic\\end',
                 'string pathToConnectionInfo '
                 f'{DATA_DIR_PATH}\\DdckPlaceHolderValues.json',
                 'string PROJECT$ '
                 f'{DATA_DIR_PATH}\\ddck',
                 'string projectPath '
                 f'{DATA_DIR_PATH}']

ORIGINAL_INPUTS = {'PROJECT$': 'C:\\Users\\epic.user\\EpicSimulation\\ddck',
                   'addAutomaticEnergyBalance': True,
                   'calc': [],
                   'calcCumSumHourly': [],
                   'calcCumSumTimeStep': [],
                   'calcDaily': [],
                   'calcHourly': [],
                   'calcHourlyTest': [],
                   'calcMonthly': [],
                   'calcMonthlyFromHourly': [],
                   'calcMonthlyMax': [],
                   'calcMonthlyMin': [],
                   'calcMonthlyTest': [],
                   'calcTest': [],
                   'calcTimeStep': [],
                   'calcTimeStepTest': [],
                   'checkDeck': True,
                   'doAutoUnitNumbering': True,
                   'generateUnitTypesUsed': True,
                   'ignoreOnlinePlotter': True,
                   'nameRef': 'DoublePipeDebug',
                   'outputLevel': 'INFO',
                   'parseFileCreated': True,
                   'pathToConnectionInfo': 'C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json',
                   'projectPath': 'C:\\Users\\epic.user\\EpicSimulation',
                   'reduceCpu': 4,
                   'runCases': True,
                   'runType': 'runFromConfig',
                   'scaling': 'False',
                   'trnsysExePath': 'C:\\Trnsys18\\Exe\\TRNExe.exe'}


INPUTS_WITHOUT = {'PROJECT$': f'{DATA_DIR_PATH}\\ddck',
 'addAutomaticEnergyBalance': True,
 'calc': [],
 'calcCumSumHourly': [],
 'calcCumSumTimeStep': [],
 'calcDaily': [],
 'calcHourly': [],
 'calcHourlyTest': [],
 'calcMonthly': [],
 'calcMonthlyFromHourly': [],
 'calcMonthlyMax': [],
 'calcMonthlyMin': [],
 'calcMonthlyTest': [],
 'calcTest': [],
 'calcTimeStep': [],
 'calcTimeStepTest': [],
 'checkDeck': True,
 'doAutoUnitNumbering': True,
 'generateUnitTypesUsed': True,
 'ignoreOnlinePlotter': True,
 'nameRef': 'DoublePipeDebug',
 'outputLevel': 'INFO',
 'parseFileCreated': True,
 'pathToConnectionInfo': f'{DATA_DIR_PATH}\\DdckPlaceHolderValues.json',
 'projectPath': _pl.WindowsPath(f'{DATA_DIR_PATH}'),
 'reduceCpu': 4,
 'runCases': True,
 'runType': 'runFromConfig',
 'scaling': 'False',
 'trnsysExePath': 'C:\\Trnsys18\\Exe\\TRNExe.exe'}


class TestReadConfigTrnsys:
    def setup(self):
        self.reader = _rct.ReadConfigTrnsys()
        self.inputs = {}

    @_pt.mark.parametrize("userInput, response", [
        ("yes", True),
        ("Yes", True),
        ("true", True),
        ("True", True),
        ("Anything_else?", False),
        ("t", True),
        ("T", True),
        ("1", True),
    ])
    def testStr2bool(self, userInput, response):
        assert self.reader.str2bool(userInput) == response

    def test_readFile_runConfig(self):
        name = "run.config_with_absolute_paths"
        lines = self.reader.readFile(DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert lines == ORIGINAL_LINES
        assert self.inputs == ORIGINAL_INPUTS

    def test_readFile_runConfig_without_any_paths(self):
        name = "run.config_without_any_paths"
        lines = self.reader.readFile(DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert self.inputs == INPUTS_WITHOUT
        assert lines == LINES_WITHOUT
