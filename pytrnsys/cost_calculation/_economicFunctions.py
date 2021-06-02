# pylint: skip-file
# type: ignore

import pytrnsys.utils.uncertainFloat
from ._models import common as _common


def getNPV(
    rate: pytrnsys.utils.uncertainFloat.UncertainFloat, analysisPeriod: float
) -> pytrnsys.utils.uncertainFloat.UncertainFloat:
    npv = ((1.0 + rate) ** analysisPeriod - 1.0) / (rate * (1.0 + rate) ** analysisPeriod)
    return npv


def getAnnuity(
    rate: pytrnsys.utils.uncertainFloat.UncertainFloat, analysisPeriod: float
) -> pytrnsys.utils.uncertainFloat.UncertainFloat:
    return 1.0 / getNPV(rate, analysisPeriod)


def getNPVIncreaseCost(
    rate: pytrnsys.utils.uncertainFloat.UncertainFloat,
    analysisPeriod: float,
    increaseCost: pytrnsys.utils.uncertainFloat.UncertainFloat,
) -> pytrnsys.utils.uncertainFloat.UncertainFloat:
    npv = 1 / (rate - increaseCost) * (1.0 - ((1.0 + increaseCost) / (1.0 + rate)) ** analysisPeriod)
    return npv
