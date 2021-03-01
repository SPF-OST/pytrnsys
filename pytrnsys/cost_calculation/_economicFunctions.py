from ._models import common as _common


def getNPV(rate: _common.UncertainFloat, analysisPeriod: float) -> _common.UncertainFloat:
    npv = ((1. + rate) ** analysisPeriod - 1.) / (rate * (1. + rate) ** analysisPeriod)
    return npv


def getAnnuity(rate: _common.UncertainFloat, analysisPeriod: float) -> _common.UncertainFloat:
    return 1. / getNPV(rate, analysisPeriod)


def getNPVIncreaseCost(rate: _common.UncertainFloat, analysisPeriod: float,
                       increaseCost: _common.UncertainFloat) -> _common.UncertainFloat:
    npv = 1 / (rate - increaseCost) * (1. - ((1. + increaseCost) / (1. + rate)) ** analysisPeriod)
    return npv
