import typing as tp

import pytest

import pytrnsys.psim.ConditionHandler as ch


ResultsDict = tp.Dict[str, tp.Union[str, float, int]]


class TestConditionHandler:
    @pytest.mark.parametrize(
        ["serializedConditions", "resultsDict", "areConditionsFulfilled"],
        [
            [["city=BAS", "30<sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=44.064, VIceS=28.0676), True],
        ])
    def test(self, serializedConditions: tp.Sequence[str],
             resultsDict: ResultsDict,
             areConditionsFulfilled: bool):
        conditionHandler = ch.ConditionHandler()
        condition = conditionHandler.conditionDictGenerator(serializedConditions)

        assert conditionHandler.conditionChecker(condition, resultsDict) == areConditionsFulfilled
