import typing as tp

import pytest

import pytrnsys.psim.ConditionHandler as ch


ResultsDict = tp.Dict[str, tp.Union[str, float, int]]


class TestConditionHandler:
    @pytest.mark.parametrize(
        ["serializedConditions", "resultsDict", "areConditionsFulfilled"],
        [
            [["city=BAS", "30<sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=44.064, VIceS=28.0676), True],
            [["city=ZRH", "30<sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=44.064, VIceS=28.0676), False],
            [["city=BAS", "30<sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=30, VIceS=28.0676), False],
            [["city=BAS", "intValue=7", "VIceS>28"], dict(city="BAS", intValue=7, VIceS=28.0676), True],
            [["city=BAS", "intValue=7", "VIceS>28"], dict(city="BAS", intValue=8, VIceS=28.0676), False],
        ])
    def test(self, serializedConditions: tp.Sequence[str],
             resultsDict: ResultsDict,
             areConditionsFulfilled: bool):
        conditionHandler = ch.ConditionHandler()
        condition = conditionHandler.conditionDictGenerator(serializedConditions)

        assert conditionHandler.conditionChecker(condition, resultsDict) == areConditionsFulfilled
