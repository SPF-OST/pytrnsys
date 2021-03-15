import pytrnsys.utils.uncertainFloat
from ._models import common as _common


def getNPV(rate: pytrnsys.utils.uncertainFloat.UncertainFloat, analysisPeriod: float) -> pytrnsys.utils.uncertainFloat.UncertainFloat:
    npv = ((1. + rate) ** analysisPeriod - 1.) / (rate * (1. + rate) ** analysisPeriod)
    return npv


def getAnnuity(rate: pytrnsys.utils.uncertainFloat.UncertainFloat, analysisPeriod: float) -> pytrnsys.utils.uncertainFloat.UncertainFloat:
    return 1. / getNPV(rate, analysisPeriod)


def getNPVIncreaseCost(rate: pytrnsys.utils.uncertainFloat.UncertainFloat, analysisPeriod: float,
                       increaseCost: pytrnsys.utils.uncertainFloat.UncertainFloat) -> pytrnsys.utils.uncertainFloat.UncertainFloat:
    npv = 1 / (rate - increaseCost) * (1. - ((1. + increaseCost) / (1. + rate)) ** analysisPeriod)
    return npv
