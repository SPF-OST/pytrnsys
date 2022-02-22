import dataclasses as _dc
import filecmp as _fc
import json as _json
import os as _os
import pathlib as _pl
import shutil as _sh
import typing as _tp

import pytest as _pt

import pytrnsys.ddck.replaceVariables as _replace

_DATA_DIR = _pl.Path(__file__).parent / "data"
_DATA_DIR_1 = _pl.Path(__file__).parent / "data1"


@_dc.dataclass
class _Project:
    projectName: str
    shallCopyFolderFromExamples: bool

    @staticmethod
    def createForProject(projectName: str) -> "_Project":
        return _Project(projectName, False)

    @property
    def testId(self) -> str:
        return f"{self.projectName}"


def getProjects(path: _pl.Path) -> _tp.Iterable[_Project]:
    for projectDirPath in path.iterdir():
        projectName = projectDirPath.name
        yield _Project.createForProject(projectName)


TEST_CASES = [_pt.param(p, id=p.testId) for p in getProjects(_DATA_DIR_1)]


class TestDdckGeneration:
    def testReplaceComputedVariablesWithDefaults(self):
        pass
        # inputDdckFilePath = _DATA_DIR / "type977_v1_input.ddck"
        # actualDdckFilePath = _DATA_DIR / "type977_v1_actual.ddck"
        # expectedDdckFilePath = _DATA_DIR / "type977_v1_expected.ddck"
        # _replace.replaceComputedVariablesWithDefaults(inputDdckFilePath, actualDdckFilePath)
        # assert actualDdckFilePath.read_text() == expectedDdckFilePath.read_text()

    @_pt.mark.parametrize("project", TEST_CASES)
    @classmethod
    def testReplaceComputedVariablesWithName(cls, project: _Project):

        helper = Helper(_DATA_DIR_1, project.projectName)

        helper.copyFolderAndFiles(helper.baseDirPath, helper.actualDirPath)

        with open(helper.jsonFilePath, "r", encoding="utf8") as jsonFile:
            jsonData = _json.load(jsonFile)

        helper.assertFileStructureEqual(helper.actualDdckDirPath, helper.expectedDdckDirPath)

        for actualDdckFilesPath, baseDdckFilesPath, expectedDdckFilesPath in zip(
                list(helper.actualDdckDirPath.iterdir()),
                list(helper.baseDdckDirPath.iterdir()),
                list(helper.expectedDdckDirPath.iterdir())):

            helper.assertFileStructureEqual(baseDdckFilesPath, expectedDdckFilesPath)

            for baseDdckFilePath, expectedDdckFilePath in zip(baseDdckFilesPath.iterdir(),
                                                              expectedDdckFilesPath.iterdir()):

                fileName = baseDdckFilePath.parts[-1]
                folderName = baseDdckFilePath.parts[-2]
                folderPath = baseDdckFilePath.parts[-3] + "\\" + folderName + "\\" + fileName
                actualDdckFilePath = actualDdckFilesPath / fileName

                baseExtension = baseDdckFilePath.suffix
                if folderPath not in jsonData or baseExtension != ".ddck" or folderName == "generic":
                    _sh.copy(baseDdckFilePath, actualDdckFilesPath)
                else:
                    _replace.replaceComputedVariablesWithNameUsingPath(baseDdckFilePath, actualDdckFilePath,
                                                                       jsonData[folderPath])
                    assert actualDdckFilePath.read_text() == expectedDdckFilePath.read_text()

        helper.assertContentEqual(helper.actualDdckDirPath, helper.expectedDdckDirPath)


class Helper:
    def __init__(self, dataDir: _pl.Path, projectName: str):
        self.actualDirPath = dataDir / projectName / "actual"
        self.baseDirPath = dataDir / projectName / "base"
        self.expectedDirPath = dataDir / projectName / "expected"

        self.jsonFilePath = self.actualDirPath / "connection.json"

        self.actualDdckDirPath = self.actualDirPath / "ddck"
        self.baseDdckDirPath = self.baseDirPath / "ddck"
        self.expectedDdckDirPath = self.expectedDirPath / "ddck"

    def copyFolderAndFiles(self, inputPath: _pl.Path, outputPath: _pl.Path) -> None:
        if outputPath.exists():
            _sh.rmtree(outputPath)

        _sh.copytree(inputPath, outputPath, ignore=self._ignoreFiles)

        for path in inputPath.iterdir():
            if path.is_file():
                _sh.copy(path, outputPath)

    @classmethod
    def _ignoreFiles(cls, path, files):
        return [f for f in files if _os.path.isfile(_os.path.join(path, f))]

    @classmethod
    def assertFileStructureEqual(cls, actualPath, expectedPath):
        dircmp = _fc.dircmp(actualPath, expectedPath)

        assert not dircmp.left_only
        assert not dircmp.right_only

    @classmethod
    def assertContentEqual(cls, actualPath, expectedPath):
        dircmp = _fc.dircmp(actualPath, expectedPath)

        for subDirectory in dircmp.subdirs.values():
            assert not subDirectory.diff_files
