import filecmp
import pathlib as pl
import shutil
import logging as log

import pytest
import diff_pdf_visually as dpdf

import pytrnsys.cost_calculation as cc


def testCostCalculation(caplog: pytest.LogCaptureFixture):
    helper = Helper(caplog)
    helper.setup()

    actualResultsDir = helper.actualResultsDir
    costParametersFilePath = helper.costParametersFilePath

    cc.calculateCostsAndWriteReports(costParametersFilePath, actualResultsDir)

    helper.assertResultsAreAsExpected()


class Helper:
    def __init__(self, caplog: pytest.LogCaptureFixture):
        self._caplog = caplog

        inputDir = pl.Path('input')
        self._resultsDir = inputDir / 'results'
        self.costParametersFilePath = inputDir / "costSolarIce_HpSplit.json"

        outputDir = pl.Path('output')
        actualDir = outputDir / 'actual'
        self.actualResultsDir = actualDir / 'results'
        expectedDir = outputDir / 'expected'
        self._expectedResultsDir = expectedDir / 'results'

    def setup(self):
        self._setupLogging()
        self._setupActualDirectory()

    def _setupLogging(self):
        self._caplog.set_level(log.DEBUG, 'root')

    def _setupActualDirectory(self):
        actualDir = self.actualResultsDir.parent
        if actualDir.exists():
            shutil.rmtree(actualDir)
        shutil.copytree(self._resultsDir, self.actualResultsDir)

    def assertResultsAreAsExpected(self):
        self._assertFileStructureEqual()
        self._assertPlotsAndReportTexFileEqual()

    def _assertFileStructureEqual(self):
        dircmp = filecmp.dircmp(self.actualResultsDir, self._expectedResultsDir)
        assert not dircmp.left_only
        assert not dircmp.right_only

    def _assertPlotsAndReportTexFileEqual(self):
        for directory in self._expectedResultsDir.iterdir():
            dirName = directory.name

            costPlotName = f"costShare-{dirName}.pdf"
            annuityPlotName = f"costShareAnnuity-{dirName}.pdf"
            reportTexName = f"{dirName}-cost.tex"

            self._assertPdfEqual(dirName, costPlotName)
            self._assertPdfEqual(dirName, annuityPlotName)
            self._assertTextFileEqual(dirName, reportTexName)

    def _assertPdfEqual(self, dirName, pdfFileName):
        expectedPath, actualPath = self._getExpectedAndActualPath(dirName, pdfFileName)
        assert dpdf.pdfdiff(actualPath, expectedPath)

    def _assertTextFileEqual(self, dirName, texFileName):
        expectedPath, actualPath = self._getExpectedAndActualPath(dirName, texFileName)
        assert filecmp.cmp(actualPath, expectedPath, shallow=False)

    def _getExpectedAndActualPath(self, dirName, fileName):
        expected = self._expectedResultsDir / dirName / fileName
        actual = self.actualResultsDir / dirName / fileName

        return expected, actual
