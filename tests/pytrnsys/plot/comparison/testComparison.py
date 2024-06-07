import collections.abc as _cabc
import dataclasses as _dc
import logging as _log
import pathlib as _pl
import typing as _tp

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

    @property
    def actualResultsDirPath(self) -> _pl.Path:
        return DATA_DIR_PATH / "input" / self.resultsDirName


def generateResultsTestCases() -> _tp.Iterable[TestCase]:
    yield TestCase(
        "slurry-cost-uncertain-y", ["QPs_Tot", "energyCost", "CollAM2PerMWh"], "slurry", shallPlotUncertainties=True
    )

    yield TestCase(
        "slurry-cost-uncertain-xy",
        ["energyCost", "investmentPerMWh", "CollAM2PerMWh"],
        "slurry",
        shallPlotUncertainties=True,
    )

    yield TestCase(
        "slurry-cost-uncertain-xy-chunk-filter",
        ["energyCost", "investmentPerMWh", "CollAM2PerMWh", "CrysPowerkW", "spf>4.5"],
        "slurry",
        shallPlotUncertainties=True,
    )

    yield TestCase(
        "slurry-cost-uncertain-xy-chunk-filter",
        ["energyCost", "investmentPerMWh", "CollAM2PerMWh", "CrysPowerkW", "spf<=4.5"],
        "slurry",
        shallPlotUncertainties=True,
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
