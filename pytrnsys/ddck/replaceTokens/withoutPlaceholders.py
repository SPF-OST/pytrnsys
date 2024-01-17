import dataclasses as _dc
import pathlib as _pl
import typing as _tp

import lark as _lark
from lark import visitors as _lvis

from pytrnsys.utils import result as _res

from . import _parse, _tokens, _common


@_dc.dataclass
class _EquationsCounter(_tokens.Token):
    numberOfEquations: int
    numberOfOutputAssignmentsWithoutDefaults: int

    def __post_init__(self):
        if self.numberOfOutputAssignmentsWithoutDefaults > self.numberOfEquations:
            raise ValueError(
                "The number of equations cannot be greater than the number of output assignments without defaults."
            )


@_dc.dataclass
class _Equations(_tokens.Token):
    pass


@_dc.dataclass
class _OutputVariableAssignment(_tokens.Token):
    portName: str


class _WithoutPlaceholdersJSONCollectTokensVisitor(_common.CollectTokensVisitorBase):
    def __init__(self) -> None:
        super().__init__()

        self.outputVariableAssignmentsToRemove: list[_OutputVariableAssignment] = []
        self.equationsCountersToAdjust: list[_EquationsCounter] = []
        self.equationsBlocksToRemove: list[_Equations] = []

    def equations(self, tree: _lark.Tree) -> None:
        equationsVisitor = _WithoutPlaceholdersJSONCollectEquationsTokensVisitor()
        equationsVisitor.visit(tree)

        self.computedHydraulicVariables.extend(equationsVisitor.outputVariablesWithDefault)

        assignments = equationsVisitor.outputVariableWithoutDefaultAssignments
        if not assignments:
            return

        nEquationsTree = _getSubtree("number_of_equations", tree)
        nEquationsAsString = _common.getChildTokenValue("POSITIVE_INT", nEquationsTree)
        nEquations = int(nEquationsAsString)

        numberOfOutputAssignmentsWithoutDefaults = len(assignments)

        if nEquations == numberOfOutputAssignmentsWithoutDefaults:
            equationsBlockToRemove = _Equations(
                tree.meta.line, tree.meta.column, tree.meta.start_pos, tree.meta.end_pos
            )
            self.equationsBlocksToRemove.append(equationsBlockToRemove)
            return

        self.outputVariableAssignmentsToRemove.extend(assignments)

        equationsCounter = _EquationsCounter(
            nEquationsTree.meta.line,
            nEquationsTree.meta.column,
            nEquationsTree.meta.start_pos,
            nEquationsTree.meta.end_pos,
            nEquations,
            numberOfOutputAssignmentsWithoutDefaults,
        )
        self.equationsCountersToAdjust.append(equationsCounter)


def _getSubtree(treeData: str, tree: _lark.Tree) -> _lark.Tree:
    subtrees = [c for c in tree.children if isinstance(c, _lark.Tree) and c.data == treeData]

    if len(subtrees) != 1:
        raise ValueError(f"None or more than one `{treeData}` subtree found for `{tree.data}.")

    return subtrees[0]


class _WithoutPlaceholdersJSONCollectEquationsTokensVisitor(_lvis.Visitor_Recursive):
    def __init__(self) -> None:
        super().__init__()
        self.outputVariablesWithDefault: list[_common.ComputedVariable] = []
        self.outputVariableWithoutDefaultAssignments: list[_OutputVariableAssignment] = []

    def equation(self, tree: _lark.Tree) -> None:
        assert len(tree.children) == 2

        assignmentTarget = tree.children[0]
        assert isinstance(assignmentTarget, _lark.Tree)
        if assignmentTarget.data != "computed_output_temp_var":
            return

        defaultVariableName = _common.getChildTokenValueOrNone("DEFAULT_VARIABLE_NAME", assignmentTarget)
        if defaultVariableName:
            computedVariable = _common.createComputedVariable(assignmentTarget, "@temp")
            self.outputVariablesWithDefault.append(computedVariable)
            return

        portName = _common.getChildTokenValue("PORT_NAME", assignmentTarget)
        outputVariableAssignment = _OutputVariableAssignment(
            tree.meta.line, tree.meta.column, tree.meta.start_pos, tree.meta.end_pos, portName
        )

        self.outputVariableWithoutDefaultAssignments.append(outputVariableAssignment)


def replaceTokensWithDefaults(inputDdckFilePath: _pl.Path, componentName: str) -> _res.Result[str]:
    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    result = _parse.parseDdck(inputDdckContent)
    if _res.isError(result):
        moreSpecificError = _res.error(result).withContext(f"An error was found in ddck file {inputDdckFilePath}")
        return moreSpecificError
    tree = _res.value(result)

    visitor = _WithoutPlaceholdersJSONCollectTokensVisitor()
    visitor.visit(tree)

    replacementsResult = _getDefaultReplacements(visitor, componentName)
    if _res.isError(replacementsResult):
        moreSpecificError = _res.error(replacementsResult).withContext(
            f"An error occurred while substituting the defaults for the placeholders in file {inputDdckFilePath.name}"
        )
        return moreSpecificError
    replacements = _res.value(replacementsResult)

    tokens = [
        *visitor.privateVariables,
        *visitor.computedHydraulicVariables,
        *visitor.computedEnergyVariables,
        *visitor.outputVariableAssignmentsToRemove,
        *visitor.equationsCountersToAdjust,
        *visitor.equationsBlocksToRemove,
    ]

    outputDdckContent = _tokens.replaceTokensWithReplacements(inputDdckContent, tokens, replacements)

    return outputDdckContent


def _getDefaultReplacements(
    visitor: _WithoutPlaceholdersJSONCollectTokensVisitor, componentName: str
) -> _res.Result[_tp.Sequence[str]]:
    privateNames = _common.getPrivateNames(visitor.privateVariables, componentName)

    computedVariablesWithoutDefaultName = [v for v in visitor.computedHydraulicVariables if not v.defaultVariableName]
    if any(computedVariablesWithoutDefaultName):
        formattedLocations = "\n".join(f"\t{v.startLine}:{v.startColumn}" for v in computedVariablesWithoutDefaultName)
        errorMessage = (
            "No default values were provided for the computed variables at the following locations "
            f"(line number:column number):\n"
            f"{formattedLocations}\n"
        )
        return _res.Error(errorMessage)
    defaultNamesForComputedVariables = [
        _tp.cast(str, v.defaultVariableName) for v in visitor.computedHydraulicVariables
    ]

    computedEnergyNames = _common.getComputedEnergyNames(visitor.computedEnergyVariables, componentName)

    emptyReplacementTextsForOutputVariableAssignments = [
        f"! Assignment to temperature at `{a.portName}` removed by pytrnsys"
        for a in visitor.outputVariableAssignmentsToRemove
    ]

    adjustedEquationsCounters = [
        f"{c.numberOfEquations - c.numberOfOutputAssignmentsWithoutDefaults}" for c in visitor.equationsCountersToAdjust
    ]

    emptyReplacementTextForEquationsBlocksToRemove = [
        "! Empty EQUATIONS block removed by pytrnsys" for _ in visitor.equationsBlocksToRemove
    ]

    replacements = [
        *privateNames,
        *defaultNamesForComputedVariables,
        *computedEnergyNames,
        *emptyReplacementTextsForOutputVariableAssignments,
        *adjustedEquationsCounters,
        *emptyReplacementTextForEquationsBlocksToRemove,
    ]

    return replacements
