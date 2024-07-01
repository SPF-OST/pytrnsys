import abc as _abc
import collections.abc as _cabc
import dataclasses as _dc
import enum as _enum
import typing as _tp

import lark as _lark
from lark import visitors as _lvis

from . import _tokens
from .defaultVisibility import DefaultVisibility


class ReplaceTokensError(ValueError):
    pass


@_dc.dataclass
class ComputedVariable(_tokens.Token):  # pylint: disable=too-few-public-methods
    portProperty: str
    portName: str
    defaultVariableName: _tp.Optional[str]


@_dc.dataclass
class VariableBase(_tokens.Token):
    name: str


_T = _tp.TypeVar("_T", bound=VariableBase)


@_dc.dataclass
class LocalVariable(VariableBase):
    pass


@_dc.dataclass
class GlobalVariable(VariableBase):
    pass


class _EnergyDirection(_enum.Enum):
    IN = "In"
    OUT = "Out"


_TERMINAL_TO_ENERGY_DIRECTION = {"in": _EnergyDirection.IN, "out": _EnergyDirection.OUT}


class _EnergyQuality(_enum.Enum):
    HEAT = "q"
    ELECTRICITY = "el"


_TERMINAL_TO_ENERGY_QUALITY = {"heat": _EnergyQuality.HEAT, "el": _EnergyQuality.ELECTRICITY}


@_dc.dataclass
class ComputedEnergyVariable(_tokens.Token):
    direction: _EnergyDirection
    quality: _EnergyQuality
    category: str
    subCategories: _cabc.Sequence[str]

    def __post_init__(self):
        if any(":" in sc for sc in self.subCategories):
            raise ValueError("""Sub-categories mustn't contain ":".""")


def createComputedVariable(tree: _lark.Tree, portProperty: str) -> ComputedVariable:
    portName = getChildTokenValue("PORT_NAME", tree)
    defaultVariableName = getChildTokenValueOrNone("DEFAULT_VARIABLE_NAME", tree)
    computedVariable = ComputedVariable(
        tree.meta.line,
        tree.meta.column,
        tree.meta.start_pos,
        tree.meta.end_pos,
        portProperty,
        portName,
        defaultVariableName,
    )
    return computedVariable


class CollectTokensVisitorBase(_lvis.Visitor_Recursive, _abc.ABC):
    def __init__(self, defaultVisibility: DefaultVisibility) -> None:
        self._defaultVisibility = defaultVisibility
        self.localVariables: list[LocalVariable] = []
        self.globalVariables: list[GlobalVariable] = []
        self.computedHydraulicVariables: list[ComputedVariable] = []
        self.computedEnergyVariables: list[ComputedEnergyVariable] = []

    def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        propertyName = getChildTokenValue("PORT_PROPERTY", tree)
        computedVariable = createComputedVariable(tree, propertyName)
        self.computedHydraulicVariables.append(computedVariable)

    def computed_output_energy_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        direction = getChildTokenValue("ENERGY_DIRECTION", tree)
        quality = getChildTokenValue("ENERGY_QUALITY", tree)
        categoryOrLocal = getChildTokenValue("CATEGORY_OR_LOCAL", tree)
        categories = _getChildTokenValues("CATEGORY", tree)

        computedEnergyVariable = ComputedEnergyVariable(
            tree.meta.line,
            tree.meta.column,
            tree.meta.start_pos,
            tree.meta.end_pos,
            _TERMINAL_TO_ENERGY_DIRECTION[direction],
            _TERMINAL_TO_ENERGY_QUALITY[quality],
            categoryOrLocal,
            categories,
        )

        self.computedEnergyVariables.append(computedEnergyVariable)

    def local_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        if self._defaultVisibility != DefaultVisibility.GLOBAL:
            raise ReplaceTokensError(
                'Explicitly local variables are only allowed if the default visibility is "global".'
            )

        self._addLocalVariable(tree)

    def default_visibility_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        match self._defaultVisibility:
            case DefaultVisibility.LOCAL:
                self._addLocalVariable(tree)
            case DefaultVisibility.GLOBAL:
                self._addGlobalVariable(tree)
            case _:
                _tp.assert_never(self._defaultVisibility)

    def global_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        if self._defaultVisibility != DefaultVisibility.LOCAL:
            raise ReplaceTokensError(
                'Explicitly global variables are only allowed if the default visibility is "local".'
            )

        self._addGlobalVariable(tree)

    def _addLocalVariable(self, tree: _lark.Tree) -> None:
        localVariable = self._createVariable(LocalVariable, tree)
        self.localVariables.append(localVariable)

    def _addGlobalVariable(self, tree: _lark.Tree) -> None:
        globalVariable = self._createVariable(GlobalVariable, tree)
        self.globalVariables.append(globalVariable)

    @staticmethod
    def _createVariable(clazz: _tp.Type[_T], tree: _lark.Tree) -> _T:
        name = getChildTokenValue("NAME", tree)
        variable = clazz(tree.meta.line, tree.meta.column, tree.meta.start_pos, tree.meta.end_pos, name)
        return variable


def getChildTokenValue(tokenType: str, tree: _lark.Tree) -> str:
    tokenValueOrNone = getChildTokenValueOrNone(tokenType, tree)
    if not tokenValueOrNone:
        raise ValueError(f"`{tree.data}` doesn't contain a direct child token of type `{tokenType}`.")

    return tokenValueOrNone


def getChildTokenValueOrNone(tokenType: str, tree: _lark.Tree) -> _tp.Optional[str]:
    values = _getChildTokenValues(tokenType, tree)

    nValues = len(values)
    if nValues == 0:
        return None

    if nValues > 1:
        raise ValueError(f"More than one token of type {tokenType} found.")

    return values[0]


def _getChildTokenValues(tokenType: str, tree: _lark.Tree) -> _cabc.Sequence[str]:
    return [c.value for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]


def getLocalNames(localVariables: _cabc.Sequence[LocalVariable], componentName: str) -> _cabc.Sequence[str]:
    localNames = [f"{componentName}{v.name}" for v in localVariables]
    return localNames


def getGlobalNames(globalVariables: _cabc.Sequence[GlobalVariable]) -> _cabc.Sequence[str]:
    globalNames = [v.name for v in globalVariables]
    return globalNames


def getComputedEnergyNames(
    computedEnergyVariables: _cabc.Sequence[ComputedEnergyVariable], componentName: str
) -> _cabc.Sequence[str]:
    return [_getComputedEnergyName(v, componentName) for v in computedEnergyVariables]


def _getComputedEnergyName(computedEnergyVariable: ComputedEnergyVariable, componentName: str) -> str:
    quality = computedEnergyVariable.quality.value

    direction = computedEnergyVariable.direction.value

    variableCategory = computedEnergyVariable.category
    category = componentName if variableCategory == ":" else variableCategory

    capitalizedSubcategories = [_capitalizeFirstLetter(c) for c in computedEnergyVariable.subCategories]
    jointSubcategories = "".join(c for c in capitalizedSubcategories)

    computedName = f"{quality}Sys{direction}_{category}{jointSubcategories}"

    return computedName


def _capitalizeFirstLetter(string: str) -> str:
    if not string:
        return ""

    return f"{string[0].upper()}{string[1:]}"
