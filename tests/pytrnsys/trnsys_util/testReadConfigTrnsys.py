import pathlib as _pl
import pytest as _pt

import pytrnsys.trnsys_util.readConfigTrnsys as _rct

_DATA_DIR_PATH = _pl.Path(__file__).parent / "data"


def _getLines(path=None, without=False):
    lines = ['bool ignoreOnlinePlotter  True',
             'int reduceCpu  4',
             'bool parseFileCreated True',
             'bool runCases True',
             'bool checkDeck True',
             'string outputLevel "INFO"', ]
    if not without:
        lines += ['string pathToConnectionInfo '
                  '"C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json"', ]  # this one
    lines += ['bool doAutoUnitNumbering True',
              'bool generateUnitTypesUsed True',
              'bool addAutomaticEnergyBalance True', ]
    if not without:
        lines += ['string PROJECT$ '
                  '"C:\\Users\\epic.user\\EpicSimulation\\ddck"', ]
    lines += ['string trnsysExePath "C:\\Trnsys18\\Exe\\TRNExe.exe"',
              'string scaling "False"', ]
    if not without:
        lines += ['string projectPath '
                  '"C:\\Users\\epic.user\\EpicSimulation"', ]
    lines += ['string nameRef "DoublePipeDebug"',
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
        lines += ['string pathToConnectionInfo '
                  f'{path}\\DdckPlaceHolderValues.json',
                  'string PROJECT$ '
                  f'{path}\\ddck',
                  'string projectPath '
                  f'{path}']
    return lines


_ORIGINAL_LINES = _getLines()
_LINES_WITHOUT = _getLines(_DATA_DIR_PATH, without=True)


def _getProcessLines(path=None, without=False):
    lines = ['bool processParallel False',
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
        lines += ['string pathBase "C:\\Users\\epic.user\\EpicSimulation"', ]
    lines += ['string dllTrnsysPath "C:\\Trnsys18\\UserLib\\ReleaseDlls"',
              'stringArray plotHourly "TInQSrc1"']
    if without:
        lines += ['string pathBase '
                  f'{path}']
    return lines


_PROCESS_ORIGINAL_LINES = _getProcessLines()
_PROCESS_LINES_WITHOUT = _getProcessLines(path=_DATA_DIR_PATH, without=True)


def _getInputs(path=None, without=False, configType='run'):
    inputs = {'calc': [],
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
        inputs['PROJECT$'] = 'C:\\Users\\epic.user\\EpicSimulation\\ddck'
        inputs['addAutomaticEnergyBalance'] = True
        inputs['checkDeck'] = True
        inputs['doAutoUnitNumbering'] = True
        inputs['generateUnitTypesUsed'] = True
        inputs['ignoreOnlinePlotter'] = True
        inputs['nameRef'] = 'DoublePipeDebug'
        inputs['outputLevel'] = 'INFO'
        inputs['parseFileCreated'] = True
        inputs['pathToConnectionInfo'] = 'C:\\Users\\epic.user\\EpicSimulation\\DdckPlaceHolderValues.json'
        inputs['projectPath'] = 'C:\\Users\\epic.user\\EpicSimulation'
        inputs['runCases'] = True
        inputs['runType'] = 'runFromConfig'
        inputs['scaling'] = 'False'
        inputs['trnsysExePath'] = 'C:\\Trnsys18\\Exe\\TRNExe.exe'
        if without:
            inputs['PROJECT$'] = f'{path}\\ddck'
            inputs['pathToConnectionInfo'] = f'{path}\\DdckPlaceHolderValues.json'
            inputs['projectPath'] = _pl.WindowsPath(f'{path}')

    elif configType == 'process':
        inputs['calculateHeatDemand'] = True
        inputs['cleanModeLatex'] = False
        inputs['createLatexPdf'] = True
        inputs['dllTrnsysPath'] = 'C:\\Trnsys18\\UserLib\\ReleaseDlls'
        inputs['firstMonthUsed'] = 0
        inputs['forceProcess'] = True
        inputs['isTrnsys'] = True
        inputs['latexNames'] = 'latexNames.json'
        inputs['numberOfYearsInHourlyFile'] = 1
        inputs['outputLevel'] = 'DEBUG'
        inputs['pathBase'] = 'C:\\Users\\epic.user\\EpicSimulation'
        inputs['plotHourly'] = [['TInQSrc1']]
        inputs['processParallel'] = False
        inputs['processQvsT'] = False
        inputs['reduceCpu'] = 1
        inputs['setPrintDataForGle'] = True
        inputs['yearReadedInMonthlyFile'] = -1
        if without:
            inputs['pathBase'] = _pl.WindowsPath(f'{path}')

    return inputs


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
