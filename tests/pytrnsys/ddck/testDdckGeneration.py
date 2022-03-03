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
    def testReplaceComputedVariablesWithDefaults(self):  # pylint: disable=no-self-use
        inputDdckFilePath = _DATA_DIR / "type977_v1_input.ddck"
        expectedDdckFilePath = _DATA_DIR / "type977_v1_expected.ddck"
        actualDdckContent = _replace.replaceComputedVariablesWithDefaults(inputDdckFilePath)
        assert actualDdckContent == expectedDdckFilePath.read_text()

    @_pt.mark.parametrize("project", TEST_CASES)
    def testReplaceComputedVariablesWithName(self, project: _Project):  # pylint: disable=no-self-use

        helper = Helper(_DATA_DIR_1, project.projectName)

        helper.copyFolderAndFiles(helper.actualDirPath, helper.generatedDirPath)

        with open(helper.ddckPlaceHolderValueJsonPath, "r", encoding="utf8") as ddckPlaceHolderValueJson:
            ddckPlaceHolderValue = _json.load(ddckPlaceHolderValueJson)
        helper.assertFileStructureEqual(helper.generatedDdckDirPath, helper.expectedDdckDirPath)

        for generatedDdckFilesPath, actualDdckFilesPath, expectedDdckFilesPath in zip(
                list(helper.generatedDdckDirPath.iterdir()),
                list(helper.actulDdckDirPath.iterdir()),
                list(helper.expectedDdckDirPath.iterdir())):

            helper.assertFileStructureEqual(actualDdckFilesPath, expectedDdckFilesPath)

            for actualDdckFile, expectedDdckFile in zip(actualDdckFilesPath.iterdir(),
                                                      expectedDdckFilesPath.iterdir()):

                fileName = actualDdckFile.parts[-1]
                folderName = actualDdckFile.parts[-2]
                generatedDdckFilePath = generatedDdckFilesPath / fileName

                if folderName not in ddckPlaceHolderValue or actualDdckFile.suffix != ".ddck":
                    _sh.copy(actualDdckFile, generatedDdckFilesPath)
                else:
                    replacedDdckContent = _replace.replaceComputedVariablesWithName(str(actualDdckFile),
                                                                                  ddckPlaceHolderValue[folderName])
                    generatedDdckFilePath.write_text(replacedDdckContent)
                    assert replacedDdckContent == expectedDdckFile.read_text()

        helper.assertContentEqual(helper.generatedDdckDirPath, helper.expectedDdckDirPath)


class Helper:
    def __init__(self, dataDir: _pl.Path, projectName: str):
        self.generatedDirPath = dataDir / projectName / "Generated_TRIHP_dualSource"
        self.actualDirPath = dataDir / projectName / "TRIHP_dualSource"
        self.expectedDirPath = dataDir / projectName / "expected"

        self.ddckPlaceHolderValueJsonPath = self.generatedDirPath / "DdckPlaceHolderValue.json"

        self.generatedDdckDirPath = self.generatedDirPath / "ddck"
        self.actulDdckDirPath = self.actualDirPath / "ddck"
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
