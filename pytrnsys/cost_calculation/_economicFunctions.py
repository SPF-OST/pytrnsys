# pylint: skip-file
# type: ignore

def getNPV(rate: float, analysisPeriod: float) -> float:
    npv = ((1.0 + rate) ** analysisPeriod - 1.0) / (
        rate * (1.0 + rate) ** analysisPeriod
    )
    return npv


def getAnnuity(rate: float, analysisPeriod: float) -> float:
    return 1.0 / getNPV(rate, analysisPeriod)


def getNPVIncreaseCost(
    rate: float,
    analysisPeriod: float,
    increaseCost: float,
) -> float:
    npv = (
        1
        / (rate - increaseCost)
        * (1.0 - ((1.0 + increaseCost) / (1.0 + rate)) ** analysisPeriod)
    )
    return npv
