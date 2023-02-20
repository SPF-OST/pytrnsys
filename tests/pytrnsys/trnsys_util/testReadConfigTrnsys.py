import pathlib as _pl
import pytest as _pt

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

PROCESS_ORIGINAL_LINES = ['bool processParallel False',
                          'bool processQvsT False',
                          'bool cleanModeLatex False',
                          'bool forceProcess  True',
                          'bool setPrintDataForGle True',
                          'bool isTrnsys True',
                          'int reduceCpu 1',
                          'string outputLevel "DEBUG"',
                          'bool createLatexPdf True',
                          'bool calculateHeatDemand True',
                          'int yearReadedInMonthlyFile -1',
                          'int firstMonthUsed 0',
                          'int numberOfYearsInHourlyFile 1',
                          'string latexNames "latexNames.json"',
                          'string pathBase "C:\\Users\\epic.user\\EpicSimulation"',
                          'string dllTrnsysPath "C:\\Trnsys18\\UserLib\\ReleaseDlls"',
                          'stringArray plotHourly "TInQSrc1"']

PROCESS_LINES_WITHOUT = ['bool processParallel False',
                         'bool processQvsT False',
                         'bool cleanModeLatex False',
                         'bool forceProcess  True',
                         'bool setPrintDataForGle True',
                         'bool isTrnsys True',
                         'int reduceCpu 1',
                         'string outputLevel "DEBUG"',
                         'bool createLatexPdf True',
                         'bool calculateHeatDemand True',
                         'int yearReadedInMonthlyFile -1',
                         'int firstMonthUsed 0',
                         'int numberOfYearsInHourlyFile 1',
                         'string latexNames "latexNames.json"',
                         'string dllTrnsysPath "C:\\Trnsys18\\UserLib\\ReleaseDlls"',
                         'stringArray plotHourly "TInQSrc1"',
                         'string pathBase '
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

INPUTS_PROCESS = {'calc': [],
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
                  'calculateHeatDemand': True,
                  'cleanModeLatex': False,
                  'createLatexPdf': True,
                  'dllTrnsysPath': 'C:\\Trnsys18\\UserLib\\ReleaseDlls',
                  'firstMonthUsed': 0,
                  'forceProcess': True,
                  'isTrnsys': True,
                  'latexNames': 'latexNames.json',
                  'numberOfYearsInHourlyFile': 1,
                  'outputLevel': 'DEBUG',
                  'pathBase': 'C:\\Users\\epic.user\\EpicSimulation',
                  'plotHourly': [['TInQSrc1']],
                  'processParallel': False,
                  'processQvsT': False,
                  'reduceCpu': 1,
                  'setPrintDataForGle': True,
                  'yearReadedInMonthlyFile': -1}

INPUTS_PROCESS_WITHOUT = {'calc': [],
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
                          'calculateHeatDemand': True,
                          'cleanModeLatex': False,
                          'createLatexPdf': True,
                          'dllTrnsysPath': 'C:\\Trnsys18\\UserLib\\ReleaseDlls',
                          'firstMonthUsed': 0,
                          'forceProcess': True,
                          'isTrnsys': True,
                          'latexNames': 'latexNames.json',
                          'numberOfYearsInHourlyFile': 1,
                          'outputLevel': 'DEBUG',
                          'plotHourly': [['TInQSrc1']],
                          'processParallel': False,
                          'processQvsT': False,
                          'reduceCpu': 1,
                          'setPrintDataForGle': True,
                          'yearReadedInMonthlyFile': -1,
                          'pathBase': _pl.WindowsPath(f'{DATA_DIR_PATH}')}


class TestReadConfigTrnsys:
    def setup(self):
        self.reader = _rct.ReadConfigTrnsys()  # pylint: disable=attribute-defined-outside-init
        self.inputs = {}  # pylint: disable=attribute-defined-outside-init

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

    def testReadFileRunConfig(self):
        name = "run.config_with_absolute_paths"
        lines = self.reader.readFile(DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert lines == ORIGINAL_LINES
        assert self.inputs == ORIGINAL_INPUTS

    def testReadFileRunConfigWithoutAnyPaths(self):
        name = "run.config_without_any_paths"
        lines = self.reader.readFile(DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert self.inputs == INPUTS_WITHOUT
        assert lines == LINES_WITHOUT

    def testReadFileProcessConfig(self):
        name = "process.config_with_absolute_paths"
        lines = self.reader.readFile(DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert self.inputs == INPUTS_PROCESS
        assert lines == PROCESS_ORIGINAL_LINES

    def testReadFileProcessConfigWithoutPaths(self):
        name = "process.config_without_paths"
        lines = self.reader.readFile(DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert self.inputs == INPUTS_PROCESS_WITHOUT
        assert lines == PROCESS_LINES_WITHOUT
