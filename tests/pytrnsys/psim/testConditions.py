import typing as tp

import pytest

import pytrnsys.psim.conditions as conds


ResultsDict = tp.Dict[str, tp.Union[str, float, int]]


class TestConditionHandler:
    @pytest.mark.parametrize(
        ["serializedConditions", "resultsDict", "areConditionsFulfilled"],
        [
            [["city=BAS", "30<sizeHpUsed<=50", "VIceS>28"], dict(city="BAS", sizeHpUsed=44.064, VIceS=28.0676), True],
            [["city=BAS", "30<sizeHpUsed<=50", "VIceS>=28"], dict(city="BAS", sizeHpUsed=44.064, VIceS=28), True],
            [["city=ZRH", "30<sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=44.064, VIceS=28.0676), False],
            [["city=ZRH|BAS", "30<sizeHpUsed<50", "VIceS>28"],
             dict(city="BAS", sizeHpUsed=44.064, VIceS=28.0676), True],
            [["city=BAS", "30<sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=30, VIceS=28.0676), False],
            [["city=BAS", "30<=sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=30, VIceS=28.0676), True],
            [["city=BAS", "intValue=7", "VIceS>28"], dict(city="BAS", intValue=7, VIceS=28.0676), True],
            [["city=BAS", "intValue=7", "VIceS>28"], dict(city="BAS", intValue=8, VIceS=28.0676), False],
            [["city=BAS", "intValue=7", "VIceS>28"], dict(city="BAS", intValue=7, VIceS=27.0676), False],
        ])
    def test(self, serializedConditions: tp.Sequence[str],
             resultsDict: ResultsDict,
             areConditionsFulfilled: bool):
        conditions = conds.createConditions(serializedConditions)

        assert conditions.doResultsSatisfyConditions(resultsDict) == areConditionsFulfilled
