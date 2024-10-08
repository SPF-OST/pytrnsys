import collections.abc as _cabc
import dataclasses as _dc
import logging as _log
import pathlib as _pl
import typing as _tp
import filecmp as _fcomp

import pytest as _pt

import pytrnsys.plot.comparison as _comp

DATA_DIR_PATH = _pl.Path(__file__).parent / "data"

LOGGER = _log.getLogger(__name__)


@_dc.dataclass
class TestCase:
    id: str
    plotVariablesAndConditions: _cabc.Sequence[str]
    resultsDirName: str
    shallPlotUncertainties: bool
    expectedFileName: str

    @property
    def actualResultsDirPath(self) -> _pl.Path:
        return self._caseDirPath / "input"

    @property
    def expectedActualCreatedImageFilePath(self) -> _pl.Path:
        return self.actualResultsDirPath / self.expectedFileName

    @property
    def expectedCreatedImageFilePath(self) -> _pl.Path:
        return self._caseDirPath / "expected" / self.expectedFileName

    @property
    def _caseDirPath(self):
        return DATA_DIR_PATH / "cases" / self.resultsDirName

    def assertThatCreatedImageIsBinaryEqualToExpected(self) -> None:
        assert _fcomp.cmp(self.expectedActualCreatedImageFilePath, self.expectedCreatedImageFilePath, shallow=False)


def generateResultsTestCases() -> _tp.Iterable[TestCase]:
    yield TestCase(
        "slurry-cost-uncertain-y",
        ["QPs_Tot", "energyCost", "CollAM2PerMWh"],
        "slurry",
        True,
        "QPs_Tot_energyCost_CollAM2PerMWh_uncertain.png",
    )

    yield TestCase(
        "slurry-cost-uncertain-xy",
        ["energyCost", "investmentPerMWh", "CollAM2PerMWh"],
        "slurry",
        True,
        "energyCost_investmentPerMWh_CollAM2PerMWh_uncertain.png",
    )

    yield TestCase(
        "slurry-cost-uncertain-xy-chunk-filter",
        ["energyCost", "investmentPerMWh", "CollAM2PerMWh", "CrysPowerkW", "spf>4.5"],
        "slurry",
        True,
        "energyCost_investmentPerMWh_CollAM2PerMWh_CrysPowerkW_spf_g_4.5_uncertain.png",
    )

    yield TestCase(
        "slurry-cost-uncertain-xy-chunk-filter",
        ["energyCost", "investmentPerMWh", "CollAM2PerMWh", "CrysPowerkW", "spf<=4.5"],
        "slurry",
        True,
        "energyCost_investmentPerMWh_CollAM2PerMWh_CrysPowerkW_spf_l_=4.5_uncertain.png",
    )


class TestComparison:
    @_pt.mark.parametrize("testCase", [_pt.param(c, id=c.id) for c in generateResultsTestCases()])
    def testComparePlot(self, testCase: TestCase) -> None:
        _comp.createPlot(
            testCase.plotVariablesAndConditions,
            str(testCase.actualResultsDirPath),
            LOGGER,
            shallPlotUncertainties=testCase.shallPlotUncertainties,
        )

        testCase.assertThatCreatedImageIsBinaryEqualToExpected()
