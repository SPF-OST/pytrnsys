import pathlib as _pl
import pytest as _pt

import pytrnsys.trnsys_util.readConfigTrnsys as _rct

_DATA_DIR_PATH = _pl.Path(__file__).parent / "data"


def _getLines(path=None, without=False):
    _LINES = ['bool ignoreOnlinePlotter  True',
              'int reduceCpu  4',
              'bool parseFileCreated True',
              'bool runCases True',
              'bool checkDeck True',
              'string outputLevel "INFO"', ]
    if not without:
        _LINES += ['string pathToConnectionInfo '
                   '"C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json"', ]  # this one
    _LINES += ['bool doAutoUnitNumbering True',
               'bool generateUnitTypesUsed True',
               'bool addAutomaticEnergyBalance True', ]
    if not without:
        _LINES += ['string PROJECT$ '
                   '"C:\\Users\\epic.user\\EpicSimulation\\ddck"', ]
    _LINES += ['string trnsysExePath "C:\\Trnsys18\\Exe\\TRNExe.exe"',
               'string scaling "False"', ]
    if not without:
        _LINES += ['string projectPath '
                   '"C:\\Users\\epic.user\\EpicSimulation"', ]
    _LINES += ['string nameRef "DoublePipeDebug"',
               'string runType "runFromConfig"',
               'deck START 0',
               'deck STOP  8760',
               'deck dtSim 1',
               'PROJECT$ generic\\head',
               'PROJECT$ control\\hydraulic_control',
               'PROJECT$ hydraulic\\hydraulic',
               'PROJECT$ QSrc1\\QSrc',
               'PROJECT$ generic\\end']
    if without:
        _LINES += ['string pathToConnectionInfo '
                   f'{path}\\DdckPlaceHolderValues.json',
                   'string PROJECT$ '
                   f'{path}\\ddck',
                   'string projectPath '
                   f'{path}']
    return _LINES


_ORIGINAL_LINES = _getLines()
_LINES_WITHOUT = _getLines(_DATA_DIR_PATH, without=True)


def _getProcessLines(path=None, without=False):
    _LINES = ['bool processParallel False',
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
              'string latexNames "latexNames.json"', ]
    if not without:
        _LINES += ['string pathBase "C:\\Users\\epic.user\\EpicSimulation"', ]
    _LINES += ['string dllTrnsysPath "C:\\Trnsys18\\UserLib\\ReleaseDlls"',
               'stringArray plotHourly "TInQSrc1"']
    if without:
        _LINES += ['string pathBase '
                   f'{path}']
    return _LINES


_PROCESS_ORIGINAL_LINES = _getProcessLines()
_PROCESS_LINES_WITHOUT = _getProcessLines(path=_DATA_DIR_PATH, without=True)


def _getInputs(path=None, without=False, configType='run'):
    _inputs = {'calc': [],
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
               'reduceCpu': 4,
               }
    if configType == 'run':
        _inputs['PROJECT$'] = 'C:\\Users\\epic.user\\EpicSimulation\\ddck'
        _inputs['addAutomaticEnergyBalance'] = True
        _inputs['checkDeck'] = True
        _inputs['doAutoUnitNumbering'] = True
        _inputs['generateUnitTypesUsed'] = True
        _inputs['ignoreOnlinePlotter'] = True
        _inputs['nameRef'] = 'DoublePipeDebug'
        _inputs['outputLevel'] = 'INFO'
        _inputs['parseFileCreated'] = True
        _inputs['pathToConnectionInfo'] = 'C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json'
        _inputs['projectPath'] = 'C:\\Users\\epic.user\\EpicSimulation'
        _inputs['runCases'] = True
        _inputs['runType'] = 'runFromConfig'
        _inputs['scaling'] = 'False'
        _inputs['trnsysExePath'] = 'C:\\Trnsys18\\Exe\\TRNExe.exe'
        if without:
            _inputs['PROJECT$'] = f'{path}\\ddck'
            _inputs['pathToConnectionInfo'] = f'{path}\\DdckPlaceHolderValues.json'
            _inputs['projectPath'] = _pl.WindowsPath(f'{path}')

    elif configType == 'process':
        _inputs['calculateHeatDemand'] = True
        _inputs['cleanModeLatex'] = False
        _inputs['createLatexPdf'] = True
        _inputs['dllTrnsysPath'] = 'C:\\Trnsys18\\UserLib\\ReleaseDlls'
        _inputs['firstMonthUsed'] = 0
        _inputs['forceProcess'] = True
        _inputs['isTrnsys'] = True
        _inputs['latexNames'] = 'latexNames.json'
        _inputs['numberOfYearsInHourlyFile'] = 1
        _inputs['outputLevel'] = 'DEBUG'
        _inputs['pathBase'] = 'C:\\Users\\epic.user\\EpicSimulation'
        _inputs['plotHourly'] = [['TInQSrc1']]
        _inputs['processParallel'] = False
        _inputs['processQvsT'] = False
        _inputs['reduceCpu'] = 1
        _inputs['setPrintDataForGle'] = True
        _inputs['yearReadedInMonthlyFile'] = -1
        if without:
            _inputs['pathBase'] = _pl.WindowsPath(f'{path}')

    return _inputs


_ORIGINAL_INPUTS = _getInputs()
_INPUTS_WITHOUT = _getInputs(_DATA_DIR_PATH, without=True)
_INPUTS_PROCESS = _getInputs(configType='process')
_INPUTS_PROCESS_WITHOUT = _getInputs(_DATA_DIR_PATH, without=True, configType='process')


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
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert lines == _ORIGINAL_LINES
        assert self.inputs == _ORIGINAL_INPUTS

    def testReadFileRunConfigWithoutAnyPaths(self):
        name = "run.config_without_any_paths"
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert self.inputs == _INPUTS_WITHOUT
        assert lines == _LINES_WITHOUT

    def testReadFileProcessConfig(self):
        name = "process.config_with_absolute_paths"
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert self.inputs == _INPUTS_PROCESS
        assert lines == _PROCESS_ORIGINAL_LINES

    def testReadFileProcessConfigWithoutPaths(self):
        name = "process.config_without_paths"
        lines = self.reader.readFile(_DATA_DIR_PATH, name, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert self.inputs == _INPUTS_PROCESS_WITHOUT
        assert lines == _PROCESS_LINES_WITHOUT
