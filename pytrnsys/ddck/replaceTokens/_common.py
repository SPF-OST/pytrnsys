import abc as _abc
import collections.abc as _cabc
import dataclasses as _dc
import enum as _enum
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

import pytrnsys.ddck.replaceTokens.error as _error
import pytrnsys.ddck.replaceTokens.tokens as _tokens
from .defaultVisibility import DefaultVisibility
from .. import _visitorHelpers as _vh


@_dc.dataclass
class ComputedVariable(
    _tokens.Token
):  # pylint: disable=too-few-public-methods
    portProperty: str
    portName: str
    defaultVariableName: _tp.Optional[str]


@_dc.dataclass
class Variable(_tokens.Token):
    name: str


class _EnergyDirection(_enum.Enum):
    IN = "In"
    OUT = "Out"


_TERMINAL_TO_ENERGY_DIRECTION = {
    "in": _EnergyDirection.IN,
    "out": _EnergyDirection.OUT,
}


class _EnergyQuality(_enum.Enum):
    HEAT = "q"
    ELECTRICITY = "el"


_TERMINAL_TO_ENERGY_QUALITY = {
    "heat": _EnergyQuality.HEAT,
    "el": _EnergyQuality.ELECTRICITY,
}


@_dc.dataclass
class ComputedEnergyVariable(_tokens.Token):
    direction: _EnergyDirection
    quality: _EnergyQuality
    category: str
    subCategories: _cabc.Sequence[str]

    def __post_init__(self):
        if any(":" in sc for sc in self.subCategories):
            raise ValueError("""Sub-categories mustn't contain ":".""")


def createComputedVariable(
    tree: _lark.Tree, portProperty: str
) -> ComputedVariable:
    portName = _vh.getChildTokenValue("PORT_NAME", tree, str)
    defaultVariableName = _vh.getChildTokenValueOrNone(
        "DEFAULT_VARIABLE_NAME", tree, str
    )
    computedVariable = ComputedVariable(
        tree.meta.line,
        tree.meta.end_line,
        tree.meta.column,
        tree.meta.end_column,
        tree.meta.start_pos,
        tree.meta.end_pos,
        portProperty,
        portName,
        defaultVariableName,
    )
    return computedVariable


class CollectTokensVisitorBase(_lvis.Visitor_Recursive, _abc.ABC):
    def __init__(
        self, componentName: str, defaultVisibility: DefaultVisibility
    ) -> None:
        self.componentName = componentName
        self._defaultVisibility = defaultVisibility
        self.computedHydraulicVariables: list[ComputedVariable] = []
        self.tokensAndReplacement: list[tuple[_tokens.Token, str]] = []

    def parameters(self, tree: _lark.Tree) -> None:
        if not tree.children:
            return

        self._checkOrAddDeclaredNumberOf(
            "parameters", "parameter", "number_of_parameters", tree
        )

    def inputs(self, tree: _lark.Tree) -> None:
        self._checkOrAddDeclaredNumberOf(
            "inputs", "input", "number_of_inputs", tree, multiplicity=2
        )

    def labels(self, tree: _lark.Tree) -> None:
        self._checkOrAddDeclaredNumberOf(
            "labels", "label", "number_of_labels", tree
        )

    def equations(self, tree: _lark.Tree) -> None:
        self._checkOrAddDeclaredNumberOf(
            "equations", "equation", "number_of_equations", tree
        )

    def constants(self, tree: _lark.Tree) -> None:
        self._checkOrAddDeclaredNumberOf(
            "constants", "equation", "number_of_constants", tree
        )

    def computed_var(
        self, tree: _lark.Tree
    ) -> None:  # pylint: disable=invalid-name
        propertyName = _vh.getChildTokenValue("PORT_PROPERTY", tree, str)
        computedVariable = createComputedVariable(tree, propertyName)
        self.computedHydraulicVariables.append(computedVariable)

    def computed_output_energy_var(
        self, tree: _lark.Tree
    ) -> None:  # pylint: disable=invalid-name
        direction = _vh.getChildTokenValue("ENERGY_DIRECTION", tree, str)
        quality = _vh.getChildTokenValue("ENERGY_QUALITY", tree, str)
        categoryOrLocal = _vh.getChildTokenValue(
            "CATEGORY_OR_LOCAL", tree, str
        )
        categories = _vh.getChildTokenValues("CATEGORY", tree)

        computedEnergyVariable = ComputedEnergyVariable(
            tree.meta.line,
            tree.meta.end_line,
            tree.meta.column,
            tree.meta.end_column,
            tree.meta.start_pos,
            tree.meta.end_pos,
            _TERMINAL_TO_ENERGY_DIRECTION[direction],
            _TERMINAL_TO_ENERGY_QUALITY[quality],
            categoryOrLocal,
            categories,
        )

        replacement = _getComputedEnergyName(
            computedEnergyVariable, self.componentName
        )

        self._addReplacement(computedEnergyVariable, replacement)

    def local_var(
        self, tree: _lark.Tree
    ) -> None:  # pylint: disable=invalid-name
        if self._defaultVisibility != DefaultVisibility.GLOBAL:
            raise _error.ReplaceTokenError.fromTree(
                tree,
                'Explicitly local variables are only allowed if the default visibility is "global"',
            )

        self._addLocalVariable(tree)

    def default_visibility_var(
        self, tree: _lark.Tree
    ) -> None:  # pylint: disable=invalid-name
        match self._defaultVisibility:
            case DefaultVisibility.LOCAL:
                self._addLocalVariable(tree)
            case DefaultVisibility.GLOBAL:
                self._addGlobalVariable(tree)
            case _:
                _tp.assert_never(self._defaultVisibility)

    def global_var(
        self, tree: _lark.Tree
    ) -> None:  # pylint: disable=invalid-name
        if self._defaultVisibility != DefaultVisibility.LOCAL:
            raise _error.ReplaceTokenError.fromTree(
                tree,
                'Explicitly global variables are only allowed if the default visibility is "local"',
            )

        self._addGlobalVariable(tree)

    def _checkOrAddDeclaredNumberOf(
        self,
        what: _tp.Literal[
            "constants", "equations", "parameters", "inputs", "labels"
        ],
        childrenSubtreeName: str,
        declaredNumberOfSubtreeName: str,
        tree: _lark.Tree,
        multiplicity: int = 1,
    ) -> None:
        childrenSubtrees = _vh.getSubtrees(childrenSubtreeName, tree)

        # The case "EQUATIONS 0", e.g., is handled by the parser, i.e.
        #
        #   EQUATIONS 0
        #   foo = bar
        #
        # is already detected by the parser, so we don't have to deal
        # with that here.
        assert childrenSubtrees

        nChildrenSubtree = len(childrenSubtrees)
        if nChildrenSubtree % multiplicity != 0:
            raise _error.ReplaceTokenError.fromTree(
                tree,
                f"Number of arguments to {what} must be a multiple of {multiplicity} but was {nChildrenSubtree}",
            )

        actualNumberOf = int(nChildrenSubtree / multiplicity)

        declaredNumberOfSubtree = _vh.getSubtreeOrNone(
            declaredNumberOfSubtreeName, tree
        )
        if declaredNumberOfSubtree:
            self._checkDeclaredNumberOf(
                what, declaredNumberOfSubtree, actualNumberOf
            )
            return

        hashToken = _vh.getChildToken("HASH", tree)

        self._addDeclaredNumberOf(actualNumberOf, hashToken)

    def _addDeclaredNumberOf(
        self, actualNumberOf: int, hashToken: _lark.Token
    ) -> None:
        replacement = str(actualNumberOf)
        token = _tokens.Token.fromMetaOrToken(hashToken)

        self._addReplacement(token, replacement)

    def _addLocalVariable(self, tree: _lark.Tree) -> None:
        localVariable = self._createVariable(tree)
        replacement = f"{self.componentName}{localVariable.name}"
        self._addReplacement(localVariable, replacement)

    def _addGlobalVariable(self, tree: _lark.Tree) -> None:
        globalVariable = self._createVariable(tree)
        replacement = globalVariable.name
        self._addReplacement(globalVariable, replacement)

    def _addReplacement(self, token: _tokens.Token, replacement: str) -> None:
        tokenAndReplacement = (token, replacement)
        self.tokensAndReplacement.append(tokenAndReplacement)

    @staticmethod
    def _checkDeclaredNumberOf(
        what: str,
        declaredNumberOfSubtree: _lark.Tree,
        actualNumberOf: int,
    ) -> None:
        declaredNumberOf = _vh.getChildTokenValueOrNone(
            "POSITIVE_INT", declaredNumberOfSubtree, int
        )
        if declaredNumberOf is None:
            # If the declared number is a variable, we cannot find out whether the value of that variable
            # matches the actual number of arguments, hence we just return (i.e. pretend it does).
            return

        if actualNumberOf != declaredNumberOf:
            raise _error.ReplaceTokenError.fromTree(
                declaredNumberOfSubtree,
                f"The declared number of {what} ({declaredNumberOf}) doesn't "
                f"match the actual number of {what} ({actualNumberOf})",
            )

    @staticmethod
    def _createVariable(tree: _lark.Tree) -> Variable:
        name = _vh.getChildTokenValue("NAME", tree, str)
        variable = Variable(
            tree.meta.line,
            tree.meta.end_line,
            tree.meta.column,
            tree.meta.end_column,
            tree.meta.start_pos,
            tree.meta.end_pos,
            name,
        )
        return variable


def _getComputedEnergyName(
    computedEnergyVariable: ComputedEnergyVariable, componentName: str
) -> str:
    quality = computedEnergyVariable.quality.value

    direction = computedEnergyVariable.direction.value

    variableCategory = computedEnergyVariable.category
    category = componentName if variableCategory == ":" else variableCategory

    capitalizedSubcategories = [
        c.capitalize() for c in computedEnergyVariable.subCategories
    ]
    jointSubcategories = "".join(c for c in capitalizedSubcategories)

    computedName = f"{quality}Sys{direction}_{category}{jointSubcategories}"

    return computedName
