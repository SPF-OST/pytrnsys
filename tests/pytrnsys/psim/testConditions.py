# pylint: skip-file
# type: ignore

import typing as tp

import pytest

import pytrnsys.psim.conditions as conds


ResultsDict = tp.Dict[str, tp.Union[str, float, int]]


class TestConditionHandler:
    @pytest.mark.parametrize(
        ["serializedConditions", "resultsDict", "areConditionsFulfilled"],
        [
            [["30<sizeHpUsed<=50"], dict(sizeHpUsed=50), True],
            [["30<sizeHpUsed<50"], dict(sizeHpUsed=50), False],
            [["30<sizeHpUsed<50"], dict(sizeHpUsed=50), False],
            [["30<sizeHpUsed<=50"], dict(sizeHpUsed=30), False],
            [["30<=sizeHpUsed<=50"], dict(sizeHpUsed=30), True],
            [["30<=sizeHpUsed<=50"], dict(sizeHpUsed=40), True],
            [["30<=sizeHpUsed<=50"], dict(sizeHpUsed=60), False],
            [["30<=sizeHpUsed<=50"], dict(sizeHpUsed=20), False],
            [["VIceS>=28"], dict(VIceS=28), True],
            [["VIceS>28"], dict(VIceS=28), False],
            [["VIceS>28"], dict(VIceS=20), False],
            [["VIceS>28"], dict(VIceS=40), True],
            [["VIceS<=28"], dict(VIceS=28), True],
            [["VIceS<28"], dict(VIceS=28), False],
            [["VIceS<28"], dict(VIceS=30), False],
            [["VIceS<28"], dict(VIceS=20), True],
            [["city=ZRH|BAS"], dict(city="BAS"), True],
            [["city=ZRH|BAS"], dict(city="ZRH"), True],
            [["city=ZRH|BAS"], dict(city="XYZ"), False],
            [["city=BAS"], dict(city="BAS"), True],
            [["city=BAS"], dict(city="ZHR"), False],
            [["sizeHpUsed=30"], dict(sizeHpUsed=30), True],
            [["sizeHpUsed=30"], dict(sizeHpUsed=30.0), True],
            [["sizeHpUsed=30.0"], dict(sizeHpUsed=30), True],
            [["sizeHpUsed=30"], dict(sizeHpUsed=40), False],
            [["sizeHpUsed=30"], dict(sizeHpUsed=40.0), False],
            [["sizeHpUsed=30.0"], dict(sizeHpUsed=40), False],
            [["city=BAS", "30<sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=30, VIceS=28.0676), False],
            [["city=BAS", "30<=sizeHpUsed<50", "VIceS>28"], dict(city="BAS", sizeHpUsed=30, VIceS=28.0676), True],
        ]
    )
    def test(self, serializedConditions: tp.Sequence[str], resultsDict: ResultsDict, areConditionsFulfilled: bool):
        conditions = conds.createConditions(serializedConditions)

        assert conditions.doResultsSatisfyConditions(resultsDict) == areConditionsFulfilled
