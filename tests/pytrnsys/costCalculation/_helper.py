import filecmp
import logging as log
import pathlib as pl
import shutil

import pytest


class Helper:
    def __init__(
        self,
        dataDirPath: pl.Path,
        resultsDirName: str,
        caplog: pytest.LogCaptureFixture,
        costConfigFileName: str | None = None,
    ):
        self._caplog = caplog

        inputDir = dataDirPath / "input"
        self._resultsDir = inputDir / resultsDirName
        self.costParametersFilePath = inputDir / costConfigFileName if costConfigFileName else None

        outputDir = dataDirPath / "output"
        actualDir = outputDir / "actual"
        self.actualResultsDir = actualDir / resultsDirName
        expectedDir = outputDir / "expected"
        self._expectedResultsDir = expectedDir / resultsDirName

    def setup(self):
        self._setupLogging()
        self._setupActualDirectory()

    def _setupLogging(self):
        self._caplog.set_level(log.DEBUG, "root")

    def _setupActualDirectory(self):
        if self.actualResultsDir.exists():
            shutil.rmtree(self.actualResultsDir)
        shutil.copytree(self._resultsDir, self.actualResultsDir)

    def assertResultsAreAsExpected(self):
        self._assertFileStructureEqual()
        self._assertOutputFilesEqual()

    def _assertFileStructureEqual(self):
        dircmp = filecmp.dircmp(self.actualResultsDir, self._expectedResultsDir)

        assert not dircmp.left_only
        assert not dircmp.right_only

    def _assertOutputFilesEqual(self):
        for resultsJsonFilePath in self._expectedResultsDir.rglob("*-results.json"):
            simulationName = resultsJsonFilePath.name[: -len("-results.json")]
            relativeContainingDirPath = resultsJsonFilePath.parent.relative_to(self._expectedResultsDir)

            reportTexName = f"{simulationName}-cost.tex"
            self._assertTextFileEqual(relativeContainingDirPath, reportTexName)

            resultJsonName = f"{simulationName}-results.json"
            self._assertTextFileEqual(relativeContainingDirPath, resultJsonName)

    def _assertTextFileEqual(self, relativeContainingDirPath, texFileName):
        expectedPath, actualPath = self._getExpectedAndActualPath(relativeContainingDirPath, texFileName)
        assert actualPath.read_text() == expectedPath.read_text()

    def _getExpectedAndActualPath(self, relativeContainingDirPath, fileName):
        expected = self._expectedResultsDir / relativeContainingDirPath / fileName
        actual = self.actualResultsDir / relativeContainingDirPath / fileName

        return expected, actual
