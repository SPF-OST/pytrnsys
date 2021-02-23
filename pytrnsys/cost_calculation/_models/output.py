__all__ = ['Output',
           'ComponentGroups',
           'ComponentGroup',
           'CostFactors',
           'YearlyCosts',
           'CostFactor']

import dataclasses as _dc
import typing as _tp

from . import input as _input
from . import common as _common
from .. import _economicFunctions as _ef

Values = _tp.Mapping[_input.Variable, float]


@_dc.dataclass(frozen=True)
class Output:
    componentGroups: "ComponentGroups"
    yearlyCosts: "CostFactors"


@_dc.dataclass(frozen=True)
class ComponentGroups:
    groups: _tp.Sequence["ComponentGroup"]

    @staticmethod
    def createFromValues(definitions: _tp.Sequence[_input.ComponentGroup], values: Values, rate: float)\
            -> "ComponentGroups":
        componentGroups = [ComponentGroup.createFromValues(g, values, rate) for g in definitions]
        return ComponentGroups(componentGroups)

    @property
    def annualizedCost(self) -> _common.UncertainFloat:
        return sum(g.components.annualizedCost for g in self.groups)


@_dc.dataclass(frozen=True)
class ComponentGroup:
    name: str
    components: "CostFactors"

    @staticmethod
    def createFromValues(definition: _input.ComponentGroup, values: Values, rate: float) -> "ComponentGroup":
        costFactors = CostFactors.createForComponentGroup(definition, values, rate)

        return ComponentGroup(definition.name, costFactors)


@_dc.dataclass(frozen=True)
class CostFactors:
    factors: _tp.Sequence["CostFactor"]

    @staticmethod
    def createForYearlyCosts(definitions: _tp.Sequence[_input.YearlyCost], values: Values, rate: float, period: float)\
            -> "CostFactors":
        costFactors = [_createCostFactors(d, values, rate, period) for d in definitions]
        return CostFactors(costFactors)

    @staticmethod
    def createForComponentGroup(definition: _input.ComponentGroup, values: Values, rate: float) \
            -> "CostFactors":
        yearlyCosts = [_createCostFactors(d, values, rate, d.lifetimeInYears) for d in definition.components]
        return CostFactors(yearlyCosts)

    @property
    def cost(self) -> _common.UncertainFloat:
        return sum(c.cost for c in self.factors)

    @property
    def npvCost(self) -> _common.UncertainFloat:
        return sum(c.npvCost for c in self.factors)

    @property
    def annualizedCost(self) -> _common.UncertainFloat:
        return sum(c.annualizedCost for c in self.factors)


class YearlyCosts(CostFactors):
    pass


def _createCostFactors(definition, values, rate, period):
    variable = definition.cost.variable
    value = values[variable]

    yearlyCost = CostFactor(definition, rate, period, value)

    return yearlyCost


@_dc.dataclass(frozen=True)
class CostFactor:
    definition: _input.CostFactor
    rate: float
    period: float
    value: float

    @property
    def cost(self) -> _common.UncertainFloat:
        return self.definition.cost.at(self.value)

    @property
    def npvCost(self) -> _common.UncertainFloat:
        return self.npvFactor * self.cost

    @property
    def annualizedCost(self) -> _common.UncertainFloat:
        return self.annuityFactor * self.cost

    @property
    def npvFactor(self) -> float:
        return _ef.getNPV(self.rate, self.period)

    @property
    def annuityFactor(self) -> float:
        return _ef.getAnnuity(self.rate, self.period)





