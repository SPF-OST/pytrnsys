import pytest as _pt
import pathlib as _pl

import pytrnsys.trnsys_util.readConfigTrnsys as _rct

ORIGINAL_INPUTS = ['bool ignoreOnlinePlotter  True',
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
        DATA_DIR_PATH = _pl.Path(__file__).parent / "data"
        ConfigWithAbsolutePaths = "run.config_with_absolute_paths"
        lines = self.reader.readFile(DATA_DIR_PATH, ConfigWithAbsolutePaths, self.inputs,
                                     parseFileCreated=False, controlDataType=False)
        assert lines == ORIGINAL_INPUTS
