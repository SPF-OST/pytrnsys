# pylint: skip-file
# type: ignore

__all__ = ["Output", "ComponentGroups", "ComponentGroup", "CostFactors", "CostFactor"]

import dataclasses as _dc
import typing as _tp

import pytrnsys.utils.uncertainFloat as _uf

from . import input as _input
from . import common as _common
from .. import _economicFunctions as _ef

Values = _tp.Mapping[_input.Variable, float]


@_dc.dataclass(frozen=True)
class Output:
    componentGroups: "ComponentGroups"
    yearlyCosts: "CostFactors"
    electricity: "Electricity"
    residualCost: "ResidualCost"
    heatingDemandInKWh: float

    @staticmethod
    def createOutput(config: _input.Input, values: Values):
        parameters = config.parameters

        componentGroups = ComponentGroups.createFromValues(
            config.componentGroups, values, parameters.rate, parameters.analysisPeriod, parameters.maintenanceRate
        )
        yearlyCosts = CostFactors.createForYearlyCosts(
            config.yearlyCosts, values, parameters.rate, parameters.analysisPeriod, parameters.maintenanceRate
        )

        costResidual = _uf.UncertainFloat.create(parameters.costResidual)
        residualCost = ResidualCost(costResidual, parameters.rate, parameters.lifetimeResVal, parameters.analysisPeriod)

        electricityDemand = values[parameters.elFromGridVariable]
        electricity = Electricity(
            electricityDemand,
            parameters.costElecFix,
            parameters.costElecKWh,
            parameters.increaseElecCost,
            parameters.rate,
            parameters.analysisPeriod,
        )

        heatingDemand = values[parameters.qDemandVariable]

        output = Output(componentGroups, yearlyCosts, electricity, residualCost, heatingDemand)

        return output

    @property
    def annuity(self) -> _uf.UncertainFloat:
        return (
            self.componentGroups.annuity
            + self.componentGroups.maintenanceCost
            + self.yearlyCosts.cost
            + self.electricity.annuity
            - self.residualCost.annuity
        )

    @property
    def npvCost(self) -> _uf.UncertainFloat:
        return (
            self.componentGroups.cost
            + self.componentGroups.npvMaintenanceCost
            + self.yearlyCosts.npvCost
            + self.electricity.npvCost
            - self.residualCost.npvResidualValue
        )

    @property
    def heatGenerationCost(self) -> _uf.UncertainFloat:
        return self.annuity / self.heatingDemandInKWh


@_dc.dataclass(frozen=True)
class ComponentGroups:
    groups: _tp.Sequence["ComponentGroup"]

    @staticmethod
    def createFromValues(
        definitions: _tp.Sequence[_input.ComponentGroup],
        values: Values,
        rate: float,
        analysisPeriod: float,
        maintenanceRate: _uf.UncertainFloat,
    ) -> "ComponentGroups":
        componentGroups = [
            ComponentGroup.createFromValues(g, values, rate, analysisPeriod, maintenanceRate) for g in definitions
        ]
        return ComponentGroups(componentGroups)

    @property
    def cost(self) -> _uf.UncertainFloat:
        return sum(g.components.cost for g in self.groups)

    @property
    def annuity(self) -> _uf.UncertainFloat:
        return sum(g.components.annuity for g in self.groups)

    @property
    def maintenanceCost(self) -> _uf.UncertainFloat:
        return sum(g.components.maintenanceCost for g in self.groups)

    @property
    def npvMaintenanceCost(self) -> _uf.UncertainFloat:
        return sum(g.components.npvMaintenanceCost for g in self.groups)


@_dc.dataclass(frozen=True)
class ComponentGroup:
    name: str
    components: "CostFactors"

    @staticmethod
    def createFromValues(
        definition: _input.ComponentGroup,
        values: Values,
        rate: float,
        analysisPeriod: float,
        maintenanceRate: _uf.UncertainFloat,
    ) -> "ComponentGroup":
        costFactors = CostFactors.createForComponentGroup(definition, values, rate, analysisPeriod, maintenanceRate)

        return ComponentGroup(definition.name, costFactors)


@_dc.dataclass(frozen=True)
class CostFactors:
    factors: _tp.Sequence["CostFactor"]

    @staticmethod
    def createForYearlyCosts(
        definitions: _tp.Sequence[_input.YearlyCost],
        values: Values,
        rate: float,
        analysisPeriod: float,
        maintenanceRate: _uf.UncertainFloat,
    ) -> "CostFactors":
        costFactors = [
            _createCostFactor(d, values, rate, analysisPeriod, analysisPeriod, maintenanceRate) for d in definitions
        ]
        return CostFactors(costFactors)

    @staticmethod
    def createForComponentGroup(
        definition: _input.ComponentGroup,
        values: Values,
        rate: float,
        analysisPeriod: float,
        maintenanceRate: _uf.UncertainFloat,
    ) -> "CostFactors":
        yearlyCosts = [
            _createCostFactor(d, values, rate, d.lifetimeInYears, analysisPeriod, maintenanceRate)
            for d in definition.components
        ]
        return CostFactors(yearlyCosts)

    @property
    def cost(self) -> _uf.UncertainFloat:
        return sum(f.cost for f in self.factors)

    @property
    def npvCost(self) -> _uf.UncertainFloat:
        return sum(f.npvCost for f in self.factors)

    @property
    def annuity(self) -> _uf.UncertainFloat:
        return sum(f.annuity for f in self.factors)

    @property
    def maintenanceCost(self) -> _uf.UncertainFloat:
        return sum(f.maintenanceCost for f in self.factors)

    @property
    def npvMaintenanceCost(self) -> _uf.UncertainFloat:
        return sum(f.npvMaintenanceCost for f in self.factors)


def _createCostFactor(inputFactor: _input.CostFactor, values, rate, lifetime, period, maintenanceRate):
    variable = inputFactor.variable

    v = values[variable]
    unit = variable.unit
    value = Value(v, unit)

    costFactor = CostFactor(inputFactor.name, inputFactor.coeffs, rate, lifetime, period, maintenanceRate, value)

    return costFactor


@_dc.dataclass(frozen=True)
class CostFactor:
    name: str
    coeffs: _common.LinearCoefficients
    rate: float
    lifetimeInYears: float
    analysisPeriodInYears: float
    maintenanceRate: _uf.UncertainFloat
    value: "Value"

    @property
    def cost(self) -> _uf.UncertainFloat:
        if not self.value.value:
            return _uf.UncertainFloat.zero()

        return self.coeffs.offset + self.coeffs.slope * self.value.value

    @property
    def npvCost(self) -> _uf.UncertainFloat:
        return self.npvFactor * self.cost

    @property
    def annuity(self) -> _uf.UncertainFloat:
        return self.annuityFactor * self.cost

    @property
    def maintenanceCost(self) -> _uf.UncertainFloat:
        return self.maintenanceRate * self.cost

    @property
    def npvMaintenanceCost(self) -> _uf.UncertainFloat:
        return self.npvFactor * self.maintenanceCost

    @property
    def npvFactor(self) -> float:
        return _ef.getNPV(self.rate, self.analysisPeriodInYears)

    @property
    def annuityFactor(self) -> float:
        return _ef.getAnnuity(self.rate, self.lifetimeInYears)


@_dc.dataclass(frozen=True)
class Value:
    value: float
    unit: str


@_dc.dataclass(frozen=True)
class Electricity:
    electricityDemandInKWh: float
    costElecFix: _uf.UncertainFloat
    costElecKWh: _uf.UncertainFloat

    increaseElecCost: float
    rate: float
    analysisPeriod: float

    @property
    def cost(self) -> _uf.UncertainFloat:
        return self.costElecFix + self.costElecKWh * self.electricityDemandInKWh

    @property
    def npvCost(self) -> _uf.UncertainFloat:
        return self.cost * self.nvpFactor

    @property
    def annuity(self) -> _uf.UncertainFloat:
        return self.annuityFactor * self.npvCost

    @property
    def nvpFactor(self) -> float:
        if self.rate == self.increaseElecCost:
            return self.analysisPeriod / (1 + self.rate)

        return _ef.getNPVIncreaseCost(self.rate, self.analysisPeriod, self.increaseElecCost)

    @property
    def annuityFactor(self) -> float:
        return _ef.getAnnuity(self.rate, self.analysisPeriod)


@_dc.dataclass(frozen=True)
class ResidualCost:
    value: _uf.UncertainFloat
    rate: float
    lifetimeInYears: float
    analysisPeriod: float

    @property
    def residualValue(self) -> _uf.UncertainFloat:
        residualValueFactor = (self.lifetimeInYears - self.analysisPeriod) / self.lifetimeInYears
        residualValue = residualValueFactor * self.value
        return residualValue

    @property
    def npvResidualValue(self) -> _uf.UncertainFloat:
        discountFromEnd = (1 + self.rate) ** (-1.0 * self.analysisPeriod)
        npvResidualValue = discountFromEnd * self.residualValue
        return npvResidualValue

    @property
    def annuity(self) -> _uf.UncertainFloat:
        annuityFactor = _ef.getAnnuity(self.rate, self.analysisPeriod)
        annuity = annuityFactor * self.npvResidualValue
        return annuity
