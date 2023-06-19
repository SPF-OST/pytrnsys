import abc as _abc
import dataclasses as _dc
import enum as _enum
import functools as _ft
import pathlib as _pl
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

import pytrnsys.utils.result as _res
from . import _parse


@_dc.dataclass
class _Token:
    startLine: int
    startColumn: int
    startIndex: int
    endIndex: int

    def shift(self, offset: int) -> "_Token":
        shiftedStartIndex = offset + self.startIndex
        shiftedEndIndex = offset + self.endIndex
        return _dc.replace(self, startIndex=shiftedStartIndex, endIndex=shiftedEndIndex)

    def lengthChange(self, replacementString) -> int:
        lengthBeforeReplacing = self.endIndex - self.startIndex
        lengthAfterReplacing = len(replacementString)
        lengthChange = lengthAfterReplacing - lengthBeforeReplacing
        return lengthChange

    def __post_init__(self):
        if self.startIndex > self.endIndex:
            raise ValueError("End index must be greater than end index.")

        if self.startIndex < 0 or self.endIndex < 0:
            raise ValueError("Start and end index must be > 0.")


@_dc.dataclass
class _ComputedVariable(_Token):  # pylint: disable=too-few-public-methods
    portProperty: str
    portName: str
    defaultVariableName: _tp.Optional[str]


@_dc.dataclass
class _EquationsCounter(_Token):
    numberOfEquations: int
    numberOfOutputAssignmentsWithoutDefaults: int

    def __post_init__(self):
        if self.numberOfOutputAssignmentsWithoutDefaults > self.numberOfEquations:
            raise ValueError(
                "The number of equations cannot be greater than the number of output assignments without defaults."
            )


@_dc.dataclass
class _Equations(_Token):
    pass


@_dc.dataclass
class _OutputVariableAssignment(_Token):
    portName: str


@_dc.dataclass
class _PrivateVariable(_Token):
    name: str


class _EnergyDirection(_enum.Enum):
    IN = "In"
    OUT = "Out"


_TERMINAL_TO_ENERGY_DIRECTION = {"in": _EnergyDirection.IN, "out": _EnergyDirection.OUT}


class _EnergyQuality(_enum.Enum):
    HEAT = "q"
    ELECTRICITY = "el"


_TERMINAL_TO_ENERGY_QUALITY = {"heat": _EnergyQuality.HEAT, "el": _EnergyQuality.ELECTRICITY}


@_dc.dataclass
class _ComputedEnergyVariable(_Token):
    direction: _EnergyDirection
    quality: _EnergyQuality
    category: str
    subCategories: _tp.Sequence[str]

    def __post_init__(self):
        if any(":" in sc for sc in self.subCategories):
            raise ValueError("""Sub-categories mustn't contain ":".""")


def _createComputedVariable(tree: _lark.Tree, portProperty: str) -> _ComputedVariable:
    portName = _getChildTokenValue("PORT_NAME", tree)
    defaultVariableName = _getChildTokenValueOrNone("DEFAULT_VARIABLE_NAME", tree)
    computedVariable = _ComputedVariable(
        tree.meta.line,
        tree.meta.column,
        tree.meta.start_pos,
        tree.meta.end_pos,
        portProperty,
        portName,
        defaultVariableName,
    )
    return computedVariable


class _CollectTokensVisitorBase(_lvis.Visitor_Recursive, _abc.ABC):
    def __init__(self) -> None:
        self.privateVariables: list[_PrivateVariable] = []
        self.computedHydraulicVariables: list[_ComputedVariable] = []
        self.computedEnergyVariables: list[_ComputedEnergyVariable] = []

    def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        propertyName = _getChildTokenValue("PORT_PROPERTY", tree)
        computedVariable = _createComputedVariable(tree, propertyName)
        self.computedHydraulicVariables.append(computedVariable)

    def computed_output_energy_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        direction = _getChildTokenValue("ENERGY_DIRECTION", tree)
        quality = _getChildTokenValue("ENERGY_QUALITY", tree)
        categoryOrLocal = _getChildTokenValue("CATEGORY_OR_LOCAL", tree)
        categories = _getChildTokenValues("CATEGORY", tree)

        computedEnergyVariable = _ComputedEnergyVariable(
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

    def private_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        name = _getChildTokenValue("NAME", tree)
        privateVariable = _PrivateVariable(
            tree.meta.line, tree.meta.column, tree.meta.start_pos, tree.meta.end_pos, name
        )
        self.privateVariables.append(privateVariable)


class _WithPlaceholdersJSONCollectTokensVisitor(_CollectTokensVisitorBase):
    def computed_output_temp_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        computedVariable = _createComputedVariable(tree, "@temp")
        self.computedHydraulicVariables.append(computedVariable)


class _WithoutPlaceholdersJSONCollectTokensVisitor(_CollectTokensVisitorBase):
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
        nEquationsAsString = _getChildTokenValue("POSITIVE_INT", nEquationsTree)
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


class _WithoutPlaceholdersJSONCollectEquationsTokensVisitor(_lvis.Visitor_Recursive):
    def __init__(self) -> None:
        super().__init__()
        self.outputVariablesWithDefault: list[_ComputedVariable] = []
        self.outputVariableWithoutDefaultAssignments: list[_OutputVariableAssignment] = []

    def equation(self, tree: _lark.Tree) -> None:
        assert len(tree.children) == 2

        assignmentTarget = tree.children[0]
        assert isinstance(assignmentTarget, _lark.Tree)
        if not assignmentTarget.data == "computed_output_var":
            return

        defaultVariableName = _getChildTokenValueOrNone("DEFAULT_VARIABLE_NAME", assignmentTarget)
        if defaultVariableName:
            computedVariable = _createComputedVariable(assignmentTarget, "@temp")
            self.outputVariablesWithDefault.append(computedVariable)
            return

        portName = _getChildTokenValue("PORT_NAME", assignmentTarget)
        outputVariableAssignment = _OutputVariableAssignment(
            tree.meta.line, tree.meta.column, tree.meta.start_pos, tree.meta.end_pos, portName
        )

        self.outputVariableWithoutDefaultAssignments.append(outputVariableAssignment)


def _getChildTokenValue(tokenType: str, tree: _lark.Tree) -> str:
    tokenValueOrNone = _getChildTokenValueOrNone(tokenType, tree)
    if not tokenValueOrNone:
        raise ValueError(f"`{tree.data}` doesn't contain a direct child token of type `{tokenType}`.")

    return tokenValueOrNone


def _getChildTokenValueOrNone(tokenType: str, tree: _lark.Tree) -> _tp.Optional[str]:
    values = _getChildTokenValues(tokenType, tree)

    nValues = len(values)
    if nValues == 0:
        return None

    if nValues > 1:
        raise ValueError(f"More than one token of type {tokenType} found.")

    return values[0]


def _getChildTokenValues(tokenType: str, tree: _lark.Tree) -> _tp.Sequence[str]:
    return [c.value for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]


def _getSubtree(treeData: str, tree: _lark.Tree) -> _lark.Tree:
    subtrees = [c for c in tree.children if isinstance(c, _lark.Tree) and c.data == treeData]

    if len(subtrees) != 1:
        raise ValueError(f"None or more than one `{treeData}` subtree found for `{tree.data}.")

    return subtrees[0]


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

    outputDdckContent = _replaceTokensWithReplacements(inputDdckContent, tokens, replacements)

    return outputDdckContent


def _getDefaultReplacements(
    visitor: _WithoutPlaceholdersJSONCollectTokensVisitor, componentName: str
) -> _res.Result[_tp.Sequence[str]]:
    privateNames = _getPrivateNames(visitor.privateVariables, componentName)

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

    computedEnergyNames = _getComputedEnergyNames(visitor.computedEnergyVariables, componentName)

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


def replaceTokens(
    inputDdckFilePath: _pl.Path, componentName: str, computedNamesByPort: _tp.Dict[str, _tp.Dict[str, str]]
) -> _res.Result[str]:
    if not inputDdckFilePath.is_file():
        return _res.Error(f"Could not replace placeholders in file {inputDdckFilePath}: the file does not exist.")

    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    return replaceTokensInString(inputDdckContent, componentName, computedNamesByPort, inputDdckFilePath)


def replaceTokensInString(  # pylint: disable=too-many-locals
    content: str,
    componentName: str,
    computedNamesByPort: _tp.Dict[str, _tp.Dict[str, str]],
    inputDdckFilePath: _tp.Optional[_pl.Path] = None,
) -> _res.Result[str]:
    treeResult = _parse.parseDdck(content)
    if _res.isError(treeResult):
        error = _res.error(inputDdckFilePath)

        if not inputDdckFilePath:
            return error

        moreSpecificError = _res.error(treeResult).withContext(
            f"An error was found in ddck file {inputDdckFilePath.name}"
        )

        return moreSpecificError
    tree = _res.value(treeResult)

    visitor = _WithPlaceholdersJSONCollectTokensVisitor()
    visitor.visit(tree)

    privateNames = _getPrivateNames(visitor.privateVariables, componentName)

    computedHydraulicNamesResult = _getComputedHydraulicNames(visitor.computedHydraulicVariables, computedNamesByPort)
    if _res.isError(computedHydraulicNamesResult):
        if inputDdckFilePath:
            contextMessage = f"Error replacing placeholders in file {inputDdckFilePath.name}"
        else:
            contextMessage = "Error replacing placeholders"

        error = _res.error(computedHydraulicNamesResult).withContext(contextMessage)

        return error
    computedHydraulicNames = _res.value(computedHydraulicNamesResult)

    computedEnergyNames = _getComputedEnergyNames(visitor.computedEnergyVariables, componentName)

    tokens = [*visitor.privateVariables, *visitor.computedHydraulicVariables, *visitor.computedEnergyVariables]
    replacements = [*privateNames, *computedHydraulicNames, *computedEnergyNames]

    outputDdckContent = _replaceTokensWithReplacements(content, tokens, replacements)

    return outputDdckContent


def _getPrivateNames(privateVariables: _tp.Sequence[_PrivateVariable], componentName: str) -> _tp.Sequence[str]:
    privateNames = [f"{componentName}{v.name}" for v in privateVariables]
    return privateNames


def _getComputedHydraulicNames(
    computedVariables: _tp.Sequence[_ComputedVariable], computedNamesByPort: _tp.Dict[str, _tp.Dict[str, str]]
) -> _res.Result[_tp.Sequence[str]]:
    computedNames = []
    for computedVariable in computedVariables:
        computedNamesForPort = computedNamesByPort.get(computedVariable.portName)
        if not computedNamesForPort:
            return _res.Error(f"Unknown port `{computedVariable.portName}`.")

        computedName = computedNamesForPort.get(computedVariable.portProperty)
        if not computedName:
            return _res.Error(
                f"Unknown property `{computedVariable.portProperty}` for port `{computedVariable.portName}`."
            )

        computedNames.append(computedName)

    return computedNames


def _getComputedEnergyNames(
    computedEnergyVariables: _tp.Sequence[_ComputedEnergyVariable], componentName: str
) -> _tp.Sequence[str]:
    return [_getComputedEnergyName(v, componentName) for v in computedEnergyVariables]


def _getComputedEnergyName(computedEnergyVariable: _ComputedEnergyVariable, componentName: str) -> str:
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


def _replaceTokensWithReplacements(
    inputDdckContent: str, tokens: _tp.Sequence[_Token], replacements: _tp.Sequence[str]
) -> str:
    sortedTokens, sortedReplacements = _getSortedTokensAndReplacements(tokens, replacements)
    sortedTokensWithoutCovers, sortedReplacementsWithoutCovers = _removeCoveredTokens(sortedTokens, sortedReplacements)
    outputDdckContent = _replaceSortedNonOverlappingTokens(
        inputDdckContent, sortedTokensWithoutCovers, sortedReplacementsWithoutCovers
    )
    return outputDdckContent


def _getSortedTokensAndReplacements(
    tokens: _tp.Sequence[_Token], replacements: _tp.Sequence[str]
) -> _tp.Tuple[_tp.Sequence[_Token], _tp.Sequence[str]]:
    if not len(tokens) == len(replacements):
        raise ValueError("`tokens` and `replacements` must be of the same length.")

    if len(tokens) == len(replacements) == 0:
        return [], []

    if len(tokens) == len(replacements) == 1:
        return tokens, replacements

    tokenAndReplacements = zip(tokens, replacements)

    key = _ft.cmp_to_key(_compareTokensEarliestAndLongestFirst)
    sortedTokenAndReplacements = list(sorted(tokenAndReplacements, key=key))

    sortedTokens, sortedReplacements = zip(*sortedTokenAndReplacements)

    return sortedTokens, sortedReplacements


def _compareTokensEarliestAndLongestFirst(
    tokenAndReplacement1: _tp.Tuple[_Token, str], tokenAndReplacement2: _tp.Tuple[_Token, str]
) -> int:
    token1 = tokenAndReplacement1[0]
    token2 = tokenAndReplacement2[0]

    if token1.startIndex < token2.startIndex:
        return -1

    if token1.startIndex > token2.startIndex:
        return 1

    if token1.endIndex == token2.endIndex:
        return 0

    return -1 if token1.endIndex > token2.endIndex else 1


def _removeCoveredTokens(
    sortedTokens: _tp.Sequence[_Token], sortedReplacements: _tp.Sequence[str]
) -> _tp.Tuple[_tp.Sequence[_Token], _tp.Sequence[str]]:
    if len(sortedTokens) == len(sortedReplacements) <= 1:
        return sortedTokens, sortedReplacements

    tokensWithoutOverlap = [sortedTokens[0]]
    replacementsWithoutOverlap = [sortedReplacements[0]]
    for token, replacement in zip(sortedTokens[1:], sortedReplacements[1:]):
        lastTokenWithoutOverlap = tokensWithoutOverlap[-1]
        if lastTokenWithoutOverlap.endIndex < token.startIndex:
            tokensWithoutOverlap.append(token)
            replacementsWithoutOverlap.append(replacement)
            continue

        if lastTokenWithoutOverlap.endIndex >= token.endIndex:
            continue

        raise ValueError("Tokens must either not overlap or fully cover each other.")

    return tokensWithoutOverlap, replacementsWithoutOverlap


def _replaceSortedNonOverlappingTokens(
    content: str, tokens: _tp.Sequence[_Token], replacements: _tp.Sequence[str]
) -> str:
    if len(tokens) != len(replacements):
        raise ValueError("`tokens` and `replacements` must be of the same length.")

    if len(tokens) > 1:
        previousAndCurrentTokens = list(zip(tokens[:-1], tokens[1:]))

        areTokensSorted = all(p.startIndex < c.startIndex for p, c in previousAndCurrentTokens)
        if not areTokensSorted:
            raise ValueError("`tokens` must be sorted by start index ascending.")

        doAnyTokensOverlap = any(p.endIndex >= c.startIndex for p, c in previousAndCurrentTokens)
        if doAnyTokensOverlap:
            raise ValueError("`tokens` must not overlap.")

    offset = 0
    resultContent = content
    for token, replacement in zip(tokens, replacements):
        resultContent = _replaceToken(
            resultContent,
            token.shift(offset),
            replacement,
        )
        offset += token.lengthChange(replacement)

    return resultContent


def _replaceToken(content: str, token: _Token, replacement: str) -> str:
    return content[: token.startIndex] + replacement + content[token.endIndex :]
