import dataclasses as dc
import typing as tp


@dc.dataclass(frozen=True)
class Component:
    name: str
    group: "Group"
    lifetimeInYears: int
    baseCost: float
    variableCost: "VariableCost"


@dc.dataclass(frozen=True)
class Group:
    name: str
    index: int


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


def createComponentsFromDict(serializedComponentsByName: ComponentsDict, groupNames: tp.Sequence[str]):
    groupsByName = {n: Group(n, i) for i, n in enumerate(groupNames)}

    components = []
    for name, properties in serializedComponentsByName.items():
        component = _createComponent(name, properties, groupsByName)
        components.append(component)

    return components


def _createComponent(name, properties: Properties, groupsByName: tp.Mapping[str, Group]) -> Component:
    groupName = _getGroup(properties, groupsByName)

    lifetimeInYears = properties["lifeTime"]
    baseCost = properties["baseCost"]

    variableCost = _createVariableCost(properties)

    component = Component(
        name,
        groupName,
        lifetimeInYears,
        baseCost,
        variableCost)

    return component


def _getGroup(properties: Properties, groupsByName: tp.Mapping[str, Group]) -> Group:
    groupName = properties["group"]
    group = groupsByName[groupName]
    return group


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


