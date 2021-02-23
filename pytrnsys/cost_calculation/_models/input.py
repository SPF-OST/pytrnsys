__all__ = ['ComponentGroup',
           'Component',
           'Variable']

import dataclasses as _dc
import dataclasses_jsonschema as _dcj
import typing as _tp

from . import common as _common


@_dc.dataclass(frozen=True)
class Input(_dcj.JsonSchemaMixin):
    componentGroups: _tp.Sequence["ComponentGroup"]
    yearlyCosts: _tp.Sequence["YearlyCost"]
    parameters: "Parameters"

    @property
    def variables(self) -> _tp.Iterable["Variable"]:
        yield from (c.variable for cg in self.componentGroups for c in cg.components)
        yield from (yc.variable for yc in self.yearlyCosts)
        yield self.parameters.qDemandVariable
        yield self.parameters.elFromGridVariable


@_dc.dataclass(frozen=True)
class Parameters(_dcj.JsonSchemaMixin):
    rate: float
    analysisPeriod: int
    qDemandVariable: "Variable"
    elFromGridVariable: "Variable"
    costElecFix: float
    costElecKWh: float
    increaseElecCost: float
    maintenanceRate: float
    costResidual: float
    lifetimeResVal: int
    cleanModeLatex: bool


@_dc.dataclass(frozen=True)
class ComponentGroup(_dcj.JsonSchemaMixin):
    name: str
    components: _tp.Sequence["Component"]


@_dc.dataclass(frozen=True)
class CostFactor(_dcj.JsonSchemaMixin):
    name: str
    coeffs: _common.LinearCoefficients
    variable: "Variable"


@_dc.dataclass(frozen=True)
class YearlyCost(CostFactor):
    pass


@_dc.dataclass(frozen=True)
class Component(CostFactor):
    lifetimeInYears: int


@_dc.dataclass(frozen=True)
class Variable(_dcj.JsonSchemaMixin):
    name: str
    unit: str
