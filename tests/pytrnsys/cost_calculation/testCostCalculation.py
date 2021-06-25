# pylint: skip-file
# type: ignore

import filecmp
import pathlib as pl
import shutil
import logging as log

import pytest
import diff_pdf_visually as dpdf

import pytrnsys.cost_calculation as cc


class TestCostCalculation:
    CONFIG_FILE_RESULTS_DIR_PAIRS = [
        ["costSolarIce_HpSplit.json", "results"],
        ["costSolarIce_HpSplit_eYearly0.json", "results_eYearly0"],
        ["costSolarIce_HpSplit_typeOfProcess_json.json", "results_json_files"],
    ]

    @pytest.mark.parametrize(
        ["costConfigFileName", "resultsDirName"],
        CONFIG_FILE_RESULTS_DIR_PAIRS
    )
    def test(
        self,
        costConfigFileName: str,
        resultsDirName: str,
        caplog: pytest.LogCaptureFixture,
    ):
        helper = Helper(costConfigFileName, resultsDirName, caplog)
        helper.setup()

        actualResultsDir = helper.actualResultsDir
        costParametersFilePath = helper.costParametersFilePath

        cc.calculateCostsAndWriteReports(
            costParametersFilePath,
            actualResultsDir,
            shallWriteReport=True,
            processType=cc.OTHER,
        )

        helper.assertResultsAreAsExpected()


class Helper:
    def __init__(
        self,
        costConfigFileName: str,
        resultsDirName: str,
        caplog: pytest.LogCaptureFixture,
    ):
        self._caplog = caplog

        baseDir = pl.Path(__file__).parent

        inputDir = baseDir / "input"
        self._resultsDir = inputDir / resultsDirName
        self.costParametersFilePath = inputDir / costConfigFileName

        outputDir = baseDir / "output"
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

        if True:
            assert not dircmp.left_only
            assert not dircmp.right_only

    def _assertOutputFilesEqual(self):
        for resultsJsonFilePath in self._expectedResultsDir.rglob("*-results.json"):
            simulationName = resultsJsonFilePath.name[: -len("-results.json")]
            relativeContainingDirPath = resultsJsonFilePath.parent.relative_to(
                self._expectedResultsDir
            )

            costPlotName = f"costShare-{simulationName}.pdf"
            self._assertPdfEqual(relativeContainingDirPath, costPlotName)

            annuityPlotName = f"costShareAnnuity-{simulationName}.pdf"
            self._assertPdfEqual(relativeContainingDirPath, annuityPlotName)

            reportTexName = f"{simulationName}-cost.tex"
            self._assertTextFileEqual(relativeContainingDirPath, reportTexName)

            resultJsonName = f"{simulationName}-results.json"
            self._assertTextFileEqual(relativeContainingDirPath, resultJsonName)

    def _assertPdfEqual(self, relativeContainingDirPath, pdfFileName):
        expectedPath, actualPath = self._getExpectedAndActualPath(
            relativeContainingDirPath, pdfFileName
        )
        assert dpdf.pdfdiff(actualPath, expectedPath)

    def _assertTextFileEqual(self, relativeContainingDirPath, texFileName):
        expectedPath, actualPath = self._getExpectedAndActualPath(
            relativeContainingDirPath, texFileName
        )
        assert actualPath.read_text() == expectedPath.read_text()

    def _getExpectedAndActualPath(self, relativeContainingDirPath, fileName):
        expected = self._expectedResultsDir / relativeContainingDirPath / fileName
        actual = self.actualResultsDir / relativeContainingDirPath / fileName

        return expected, actual
