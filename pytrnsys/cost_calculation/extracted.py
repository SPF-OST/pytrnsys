import dataclasses as dc
import typing as tp


@dc.dataclass(frozen=True)
class Component:
    name: str
    group: str
    lifetimeInYears: int
    baseCost: float
    variableCost: "VariableCost"


@dc.dataclass(frozen=True)
class VariableCost:
    variable: "Variable"
    costPerUnit: float


@dc.dataclass(frozen=True)
class Variable:
    name: str
    unit: str


@dc.dataclass(frozen=True)
class ComponentSize:
    component: Component
    size: float

    @property
    def cost(self):
        return self.component.baseCost + self.size * self.component.variableCost.costPerUnit


Properties = tp.Mapping[str, tp.Union[str, float, int]]
ComponentsDict = tp.Mapping[str, Properties]


def createComponentsFromDict(componentsDict: ComponentsDict):
    components = []
    for name, properties in componentsDict.items():
        component = _createComponent(name, properties)
        components.append(component)

    return components


def _createComponent(name, properties: Properties):
    group = properties["group"]
    lifetimeInYears = properties["lifeTime"]
    baseCost = properties["baseCost"]

    variableCost = _createVariableCost(properties)

    component = Component(
        name,
        group,
        lifetimeInYears,
        baseCost,
        variableCost)

    return component


def _createVariableCost(properties: Properties) -> VariableCost:
    variable = _createVariable(properties)
    costPerUnit = properties["varCost"]

    variableCost = VariableCost(variable, costPerUnit)

    return variableCost


def _createVariable(properties) -> Variable:
    variableName = properties["size"]
    variableUnit = properties["varUnit"]

    variable = Variable(variableName, variableUnit)

    return variable


