# pylint: skip-file
# type: ignore

__all__ = ["ComponentGroup", "Component", "Variable"]

import dataclasses as _dc
import dataclasses_jsonschema as _dcj
import typing as _tp

import pytrnsys.utils.uncertainFloat as _uf

from . import common as _common


@_dc.dataclass(
    frozen=True,
    eq=True,
)
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
    costElecFix: _uf.UncertainFloat
    costElecKWh: _uf.UncertainFloat
    increaseElecCost: float
    maintenanceRate: _uf.UncertainFloat
    costResidual: _uf.UncertainFloat
    lifetimeResVal: int
    cleanModeLatex: bool
    reportAuthor: str = "<not-set>"
    reportEmail: str = "<not-set>"


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
