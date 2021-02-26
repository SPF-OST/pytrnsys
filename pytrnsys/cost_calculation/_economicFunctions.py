def getNPV(rate: float, period: float) -> float:
    npv = ((1. + rate) ** period - 1.) / (rate * (1. + rate) ** period)
    return npv


def getAnnuity(rate: float, period: float) -> float:
    return 1. / getNPV(rate, period)


def getNPVIncreaseCost(rate: float, period: float, increaseCost: float) -> float:
    npv = 1 / (rate - increaseCost) * (1. - ((1. + increaseCost) / (1. + rate)) ** period)
    return npv
