import dataclasses as _dc
import typing as _tp
import pathlib as _pl

import numpy as _np
import pytest as _pt

import pytrnsys.plot.comparison.common as _common

import pytrnsys.plot.comparison as _cplot


@_dc.dataclass
class TestCaseBase:
    id: str
    abscissaVariable: str
    ordinateVariable: str
    seriesVariable: str | None
    chunkVariable: str | None
    shallPlotUncertainties: bool
    expectedManySeriesOrManyChunks: _common.ManySeries | _common.ManyChunks | None

    def __post_init__(self):
        if self.chunkVariable:
            assert self.seriesVariable


@_dc.dataclass
class FromValuesTestCase(TestCaseBase):
    values: _common.Values


def generateFromValuesTestCases() -> _tp.Iterable[FromValuesTestCase]:
    yield FromValuesTestCase(
        "stringValuesForSeriesVariable",
        "VShM3",
        "SPF",
        "house type",
        "HP",
        False,
        _common.ManyChunks(
            chunks=[
                _common.Chunk(
                    groupingValue=_common.GroupingValue(name="HP", label="MFH"),
                    manySeries=_common.ManySeries(
                        [
                            _common.Series(
                                index=1,
                                groupingValue=_common.GroupingValue(name="house " "type", label="ASHP"),
                                abscissa=_common.AxisValues(
                                    name="VShM3",
                                    mins=_np.array([20, 30, 40]),
                                    means=_np.array([20, 30, 40]),
                                    maxs=_np.array([20, 30, 40]),
                                ),
                                ordinate=_common.AxisValues(
                                    name="SPF",
                                    mins=_np.array([2.1, 2.2, 2.4]),
                                    means=_np.array([2.1, 2.2, 2.4]),
                                    maxs=_np.array([2.1, 2.2, 2.4]),
                                ),
                                shallPrintUncertainties=False,
                            )
                        ]
                    ),
                ),
                _common.Chunk(
                    groupingValue=_common.GroupingValue(name="HP", label="SFH"),
                    manySeries=_common.ManySeries(
                        [
                            _common.Series(
                                index=2,
                                groupingValue=_common.GroupingValue(name="house " "type", label="GSHP"),
                                abscissa=_common.AxisValues(
                                    name="VShM3",
                                    mins=_np.array([20, 32, 40]),
                                    means=_np.array([20, 32, 40]),
                                    maxs=_np.array([20, 32, 40]),
                                ),
                                ordinate=_common.AxisValues(
                                    name="SPF",
                                    mins=_np.array([3.1, 3.4, 3.5]),
                                    means=_np.array([3.1, 3.4, 3.5]),
                                    maxs=_np.array([3.1, 3.4, 3.5]),
                                ),
                                shallPrintUncertainties=False,
                            )
                        ]
                    ),
                ),
            ]
        ),
        {
            "MFH": {
                "ASHP": [
                    (20, 2.1),
                    (30, 2.2),
                    (40, 2.4),
                ]
            },
            "SFH": {
                "GSHP": [
                    (20, 3.1),
                    (32, 3.4),
                    (40, 3.5),
                ]
            },
        },
    )


@_dc.dataclass
class FromResultsTestCase(TestCaseBase):
    results: _tp.Sequence[_tp.Mapping[str, _tp.Any]]


def generateFromResultsTestCases() -> _tp.Iterable[FromResultsTestCase]:
    yield FromResultsTestCase(
        "differingGroupingValuesWithinTolerance",
        "AcollAp",
        "fSolar",
        "DhwVM3PerM2",
        None,
        False,
        _common.ManySeries(
            allSeries=[
                _common.Series(
                    index=1,
                    groupingValue=_common.GroupingValue(name="DhwVM3PerM2", label="0.10"),
                    abscissa=_common.AxisValues(
                        name="AcollAp",
                        mins=_np.array([4.26611868, 6.39917801]),
                        means=_np.array([4.26611868, 6.39917801]),
                        maxs=_np.array([4.26611868, 6.39917801]),
                    ),
                    ordinate=_common.AxisValues(
                        name="fSolar",
                        mins=_np.array([0.47963231, 0.59204937]),
                        means=_np.array([0.47963231, 0.59204937]),
                        maxs=_np.array([0.47963231, 0.59204937]),
                    ),
                    shallPrintUncertainties=False,
                ),
                _common.Series(
                    index=2,
                    groupingValue=_common.GroupingValue(name="DhwVM3PerM2", label="0.80"),
                    abscissa=_common.AxisValues(
                        name="AcollAp",
                        mins=_np.array([4.26611868, 6.39917801]),
                        means=_np.array([4.26611868, 6.39917801]),
                        maxs=_np.array([4.26611868, 6.39917801]),
                    ),
                    ordinate=_common.AxisValues(
                        name="fSolar",
                        mins=_np.array([0.77399151, 1.38196721]),
                        means=_np.array([0.77399151, 1.38196721]),
                        maxs=_np.array([0.77399151, 1.38196721]),
                    ),
                    shallPrintUncertainties=False,
                ),
            ]
        ),
        [
            {
                "AcollAp": 4.266118675381444,
                "CollAM2PerMWh": 2.000000000811191,
                "DhwVM3PerM2": 0.1,
                "Name": "AColl2",
                "PDHWSet_kW_Tot": 2133.0593368255622,
                "Pcoll_kW_Tot": 1000.4309456552484,
                "PdhwIdeal_kW_Tot": 2133.1099999999747,
                "Pdhw_kW_Tot": 2085.828937455809,
                "PelPuDHW_kW_Tot": 0.0,
                "PpenDHW_kW_Tot": 70.84559905462997,
                "Vol_Tes1": 0.4266118675381444,
                "fSolar": 0.4796323071802449,
            },
            {
                "AcollAp": 4.266118675381444,
                "CollAM2PerMWh": 2.000000000811191,
                "DhwVM3PerM2": 0.8,
                "Name": "AColl2",
                "PDHWSet_kW_Tot": 2133.0593368255622,
                "Pcoll_kW_Tot": 1613.6981756046569,
                "PdhwIdeal_kW_Tot": 2133.1099999999747,
                "Pdhw_kW_Tot": 2084.904223428721,
                "PelPuDHW_kW_Tot": 0.0,
                "PpenDHW_kW_Tot": 72.2326700952627,
                "Vol_Tes1": 3.412894940305155,
                "fSolar": 0.7739915136009731,
            },
            {
                "AcollAp": 6.399178013072166,
                "CollAM2PerMWh": 3.0000000012167867,
                "DhwVM3PerM2": 0.10000000000000002,
                "Name": "AColl3",
                "PDHWSet_kW_Tot": 2133.0593368255622,
                "Pcoll_kW_Tot": 1235.1573649332963,
                "PdhwIdeal_kW_Tot": 2133.1099999999747,
                "Pdhw_kW_Tot": 2086.2404745669755,
                "PelPuDHW_kW_Tot": 0.0,
                "PpenDHW_kW_Tot": 70.22829338788026,
                "Vol_Tes1": 0.6399178013072166,
                "fSolar": 0.5920493730185482,
            },
            {
                "AcollAp": 6.399178013072166,
                "CollAM2PerMWh": 3.0000000012167867,
                "DhwVM3PerM2": 0.8000000000000002,
                "Name": "AColl3",
                "PDHWSet_kW_Tot": 2133.0593368255622,
                "Pcoll_kW_Tot": 2881.6537423000514,
                "PdhwIdeal_kW_Tot": 2133.1099999999747,
                "Pdhw_kW_Tot": 2085.182427659196,
                "PelPuDHW_kW_Tot": 0.0,
                "PpenDHW_kW_Tot": 71.81536374954906,
                "Vol_Tes1": 5.119342410457733,
                "fSolar": 1.3819672101951126,
            },
        ],
    )


class TestCommon:
    @_pt.mark.parametrize("testCase", [_pt.param(c, id=c.id) for c in generateFromValuesTestCases()])
    def testCreateManySeriesOrManyChunksFromValues(self, testCase: FromValuesTestCase):
        actualManySeriesOrManyChunks = _common.createManySeriesOrManyChunksFromValues(
            testCase.abscissaVariable,
            testCase.ordinateVariable,
            testCase.seriesVariable,
            testCase.chunkVariable,
            testCase.values,
            testCase.shallPlotUncertainties,
        )

        assert actualManySeriesOrManyChunks == testCase.expectedManySeriesOrManyChunks

    @_pt.mark.parametrize("testCase", [_pt.param(c, id=c.id) for c in generateFromResultsTestCases()])
    def testCreateManySeriesOrManyChunksFromResults(self, testCase: FromResultsTestCase):
        actualManySeriesOrManyChunks = _common.createManySeriesOrManyChunksFromResults(
            testCase.results,
            testCase.abscissaVariable,
            testCase.ordinateVariable,
            testCase.seriesVariable,
            testCase.chunkVariable,
            testCase.shallPlotUncertainties,
        )

        assert actualManySeriesOrManyChunks == testCase.expectedManySeriesOrManyChunks
