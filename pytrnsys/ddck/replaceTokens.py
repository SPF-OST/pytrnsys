import abc as _abc
import dataclasses as _dc
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


@_dc.dataclass
class _ComputedVariable(_Token):  # pylint: disable=too-few-public-methods
    portProperty: str
    portName: str
    defaultVariableName: _tp.Optional[str]


@_dc.dataclass
class _OutputVariableAssignment(_Token):
    portName: str


@_dc.dataclass
class _PrivateVariable(_Token):
    name: str


class _CollectTokensVisitorBase(_lvis.Visitor_Recursive, _abc.ABC):
    def __init__(self):
        self.computedVariables: list[_ComputedVariable] = []
        self.privateVariables: list[_PrivateVariable] = []

    def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        portProperty = _getChildTokenValue("PORT_PROPERTY", tree)
        self._addComputedVar(tree, portProperty)

    def private_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        name = _getChildTokenValue("NAME", tree)
        privateVariable = _PrivateVariable(
            tree.meta.line, tree.meta.column, tree.meta.start_pos, tree.meta.end_pos, name
        )
        self.privateVariables.append(privateVariable)

    def _addComputedVar(self, tree: _lark.Tree, portProperty: str) -> None:
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
        self.computedVariables.append(computedVariable)


class _WithPlaceholdersJSONCollectTokensVisitor(_CollectTokensVisitorBase):
    def computed_output_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        self._addComputedVar(tree, portProperty="@temp")


class _WithoutPlaceholdersJSONCollectTokensVisitor(_CollectTokensVisitorBase):
    def __init__(self):
        super().__init__()

        self.outputVariableAssignments: list[_OutputVariableAssignment] = []

    def equation(self, tree: _lark.Tree) -> None:
        assert len(tree.children) == 2

        assignmentTarget = tree.children[0]
        assert isinstance(assignmentTarget, _lark.Tree)
        if not assignmentTarget.data == "computed_output_var":
            return

        defaultVariableName = _getChildTokenValueOrNone("DEFAULT_VARIABLE_NAME", assignmentTarget)
        if defaultVariableName:
            self._addComputedVar(assignmentTarget, portProperty="@temp")
            return

        portName = _getChildTokenValue("PORT_NAME", assignmentTarget)
        outputVariableAssignment = _OutputVariableAssignment(
            tree.meta.line, tree.meta.column, tree.meta.start_pos, tree.meta.end_pos, portName
        )
        self.outputVariableAssignments.append(outputVariableAssignment)


def _getChildTokenValue(tokenType: str, tree: _lark.Tree) -> str:
    valueOrNone = _getChildTokenValueOrNone(tokenType, tree)
    if not valueOrNone:
        raise ValueError(f"Tree doesn't contain a direct child token of type {tokenType}.")

    return valueOrNone


def _getChildTokenValueOrNone(tokenType: str, tree: _lark.Tree) -> _tp.Optional[str]:
    matchingChildTokens = [c for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]

    nMatches = len(matchingChildTokens)
    if nMatches == 0:
        return None

    if nMatches > 1:
        raise ValueError(f"More than one token of type {tokenType} found.")

    matchingChildToken = matchingChildTokens[0]

    return matchingChildToken.value


def replaceTokensWithDefaults(inputDdckFilePath: _pl.Path) -> _res.Result[str]:
    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    result = _parse.parseDdck(inputDdckContent)
    if _res.isError(result):
        moreSpecificError = _res.error(result).withContext(f"An error was found in ddck file {inputDdckFilePath}")
        return moreSpecificError
    tree = _res.value(result)

    visitor = _WithoutPlaceholdersJSONCollectTokensVisitor()
    visitor.visit(tree)

    defaultNamesForPrivateVariables = [v.name for v in visitor.privateVariables]

    computedVariablesWithoutDefaultName = [v for v in visitor.computedVariables if not v.defaultVariableName]
    if any(computedVariablesWithoutDefaultName):
        formattedLocations = "\n".join(f"\t{v.startLine}:{v.startColumn}" for v in computedVariablesWithoutDefaultName)
        errorMessage = (
            "No placeholder values were provided and the computed variables at the following location\n"
            f"(line number: column number) don't have default values in the file {inputDdckFilePath.name}:\n"
            f"{formattedLocations}\n"
        )
        return _res.Error(errorMessage)
    defaultNamesForComputedVariables = [_tp.cast(str, v.defaultVariableName) for v in visitor.computedVariables]

    emptyReplacementTextsForOutputVariableAssignments = [
        f"! Assignment to temperature at {a.portName} removed by pytrnsys" for a in visitor.outputVariableAssignments
    ]

    tokens = [*visitor.privateVariables, *visitor.computedVariables, *visitor.outputVariableAssignments]
    replacements = [
        *defaultNamesForPrivateVariables,
        *defaultNamesForComputedVariables,
        *emptyReplacementTextsForOutputVariableAssignments,
    ]

    outputDdckContent = _replaceTokensWithReplacements(inputDdckContent, tokens, replacements)

    return outputDdckContent


def replaceTokens(
    inputDdckFilePath: _pl.Path, componentName: str, computedNamesByPort: _tp.Dict[str, _tp.Dict[str, str]]
) -> _res.Result[str]:
    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    treeResult = _parse.parseDdck(inputDdckContent)
    if _res.isError(treeResult):
        moreSpecificError = _res.error(treeResult).withContext(f"An error was found in ddck file {inputDdckFilePath}")
        return moreSpecificError
    tree = _res.value(treeResult)

    visitor = _WithPlaceholdersJSONCollectTokensVisitor()
    visitor.visit(tree)

    privateNames = [f"{componentName}{v.name}" for v in visitor.privateVariables]
    computedNamesResult = _getComputedNames(visitor.computedVariables, computedNamesByPort)
    if _res.isError(computedNamesResult):
        error = _res.error(computedNamesResult).withContext(
            f"Error replacing placeholders in file {inputDdckFilePath}: "
        )
        return error
    computedNames = _res.value(computedNamesResult)

    tokens = [*visitor.privateVariables, *visitor.computedVariables]
    replacements = [*privateNames, *computedNames]

    outputDdckContent = _replaceTokensWithReplacements(inputDdckContent, tokens, replacements)

    return outputDdckContent


def _getComputedNames(
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


def _replaceTokensWithReplacements(inputDdckContent: str, tokens: _tp.Sequence[_Token], replacements: _tp.Sequence[str]):
    sortedTokens, sortedReplacements = _getSortedTokensAndReplacements(tokens, replacements)
    outputDdckContent = _replaceSortedNonOverlappingTokens(inputDdckContent, sortedTokens, sortedReplacements)
    return outputDdckContent


def _getSortedTokensAndReplacements(
    tokens: _tp.Sequence[_Token], replacements: _tp.Sequence[str]
) -> _tp.Tuple[_tp.Sequence[_Token], _tp.Sequence[str]]:
    if not len(tokens) == len(replacements):
        raise ValueError("`tokens` and `replacements` must be of the same length.")

    if len(tokens) == len(replacements) == 0:
        return [], []

    tokenAndReplacements = zip(tokens, replacements)

    sortedTokenAndReplacements = list(sorted(tokenAndReplacements, key=lambda t: t[0].startIndex))

    sortedTokens, sortedReplacements = zip(*sortedTokenAndReplacements)

    return sortedTokens, sortedReplacements


def _replaceSortedNonOverlappingTokens(
    content: str, tokens: _tp.Sequence[_Token], replacements: _tp.Sequence[str]
) -> str:
    if len(tokens) != len(replacements):
        raise ValueError("`tokens` and `replacements` must be of the same length.")

    if len(tokens) > 1:
        previousAndCurrentTokens = zip(tokens[:-1], tokens[1:])

        areTokensSorted = all(p.startIndex < c.startIndex for p, c in previousAndCurrentTokens)
        if not areTokensSorted:
            raise ValueError("`tokens` must be sorted by start index ascending.")

        doAnyTokensOverlap = any(p.endIndex > c.startIndex for p, c in previousAndCurrentTokens)
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
