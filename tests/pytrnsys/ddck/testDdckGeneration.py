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
    # def testReplaceComputedVariablesWithDefaults(self):
    #     inputDdckFilePath = _DATA_DIR / "type977_v1_input.ddck"
    #     actualDdckFilePath = _DATA_DIR / "type977_v1_actual.ddck"
    #     expectedDdckFilePath = _DATA_DIR / "type977_v1_expected.ddck"
    # 
    #     _replace.replaceComputedVariablesWithDefaults(inputDdckFilePath, actualDdckFilePath)
    # 
    #     assert actualDdckFilePath.read_text() == expectedDdckFilePath.read_text()

    @_pt.mark.parametrize("project", TEST_CASES)
    def testReplaceComputedVariablesWithName(self, project: _Project):
        actualDirPath = _DATA_DIR_1 / project.projectName / "actual"
        baseDirPath = _DATA_DIR_1 / project.projectName / "base"
        expectedDirPath = _DATA_DIR_1 / project.projectName / "expected"

        _copyFolderAndFiles(baseDirPath, actualDirPath)

        jsonFile = open(actualDirPath / "connection.json")
        jsonData = _json.load(jsonFile)

        actualDdckDirPath = actualDirPath / "ddck"
        baseDdckDirPath = baseDirPath / "ddck"
        expectedDdckDirPath = expectedDirPath / "ddck"

        _assertFileStructureEqual(actualDdckDirPath, expectedDdckDirPath)

        actualDdckFileDirPaths = [filePath for filePath in actualDdckDirPath.iterdir()]
        baseDdckFileDirPaths = [filePath for filePath in baseDdckDirPath.iterdir()]
        expectedDdckFileDirPaths = [filePath for filePath in expectedDdckDirPath.iterdir()]

        for actualDdckFileDirPath, baseDdckFileDirPath, expectedDdckFileDirPath in zip(actualDdckFileDirPaths,
                                                                                       baseDdckFileDirPaths,
                                                                                       expectedDdckFileDirPaths):

            _assertFileStructureEqual(baseDdckFileDirPath, expectedDdckFileDirPath)

            for baseDdckFilePath, expectedDdckFilePath in zip(baseDdckFileDirPath.iterdir(),
                                                              expectedDdckFileDirPath.iterdir()):

                fileName = baseDdckFilePath.parts[-1]
                folderName = baseDdckFilePath.parts[-2]
                folderPath = baseDdckFilePath.parts[-3] + "\\" + folderName + "\\" + fileName
                actualDdckFilePath = actualDdckFileDirPath / fileName

                baseExtension = baseDdckFilePath.suffix
                if folderPath not in jsonData or baseExtension != ".ddck" or folderName == "generic":
                    _sh.copy(baseDdckFilePath, actualDdckFileDirPath)
                else:
                    _replace.replaceComputedVariablesWithNameUsingPath(baseDdckFilePath, actualDdckFilePath,
                                                              jsonData[folderPath])
                    assert actualDdckFilePath.read_text() == expectedDdckFilePath.read_text()

        _assertContentEqual(actualDdckDirPath, expectedDdckDirPath)


def _copyFolderAndFiles(inputPath: _pl.Path, outputPath: _pl.Path) -> None:
    if outputPath.exists():
        _sh.rmtree(outputPath)

    _sh.copytree(inputPath, outputPath, ignore=_ignoreFiles)

    for path in inputPath.iterdir():
        if path.is_file():
            _sh.copy(path, outputPath)


def _ignoreFiles(dir, files):
    return [f for f in files if _os.path.isfile(_os.path.join(dir, f))]


def _assertFileStructureEqual(actualPath, expectedPath):
    dircmp = _fc.dircmp(actualPath, expectedPath)

    assert not dircmp.left_only
    assert not dircmp.right_only


def _assertContentEqual(actualPath, expectedPath):
    dircmp = _fc.dircmp(actualPath, expectedPath)

    for sd in dircmp.subdirs.values():
        assert not sd.diff_files
