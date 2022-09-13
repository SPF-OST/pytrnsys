import abc as _abc
import dataclasses as _dc
import pathlib as _pl
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

import pytrnsys.utils.result as _res
from . import _parse


@_dc.dataclass
class _Token(_abc.ABC):
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
    defaultVariableName: str


@_dc.dataclass
class _PrivateVariable(_Token):
    name: str


class _CollectPrivateAndComputedVariables(_lvis.Visitor_Recursive):
    def __init__(self):
        super().__init__()

        self.computedVariables = []
        self.privateVariables = []

    def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        portProperty = self._getChildToken("PORT_PROPERTY", tree)
        portName = self._getChildToken("PORT_NAME", tree)
        defaultVariableName = self._getChildToken("DEFAULT_VARIABLE_NAME", tree)
        computedVariable = _ComputedVariable(
            tree.meta.start_pos, tree.meta.end_pos, portProperty, portName, defaultVariableName
        )
        self.computedVariables.append(computedVariable)

    def computed_output_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        portName = self._getChildToken("PORT_NAME", tree)
        defaultVariableName = self._getChildToken("DEFAULT_VARIABLE_NAME", tree)
        computedVariable = _ComputedVariable(
            tree.meta.start_pos, tree.meta.end_pos, "@temp", portName, defaultVariableName
        )
        self.computedVariables.append(computedVariable)

    def private_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        name = self._getChildToken("NAME", tree)
        privateVariable = _PrivateVariable(tree.meta.start_pos, tree.meta.end_pos, name)
        self.privateVariables.append(privateVariable)

    @staticmethod
    def _getChildToken(tokenType: str, tree: _lark.Tree) -> str:  # pylint: disable=invalid-name
        matchingChildTokens = [c for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]

        if len(matchingChildTokens) != 1:
            raise ValueError(f"None or more than one token of type {tokenType} found.")

        matchingChildToken = matchingChildTokens[0]

        return matchingChildToken.value


def replacePrivateAndComputedVariablesWithDefaults(inputDdckFilePath: _pl.Path) -> _res.Result[str]:
    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    result = _getPrivateAndComputedVariables(inputDdckContent)
    if _res.isError(result):
        moreSpecificError = _res.error(result).withContext(f"An error was found in ddck file {inputDdckContent}")
        return moreSpecificError
    privateVariables, computedVariables = _res.value(result)

    defaultNamesForPrivateVariables = [v.name for v in privateVariables]
    defaultNamesForComputedVariables = [v.defaultVariableName for v in computedVariables]

    outputDdckContent = _replacePrivateAndComputedVariables(
        inputDdckContent,
        privateVariables,
        computedVariables,
        defaultNamesForPrivateVariables,
        defaultNamesForComputedVariables,
    )

    return outputDdckContent


def replacePrivateAndComputedVariables(
    inputDdckFilePath: _pl.Path, componentName: str, namesByPort: dict
) -> _res.Result[str]:
    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    result = _getPrivateAndComputedVariables(inputDdckContent)
    if _res.isError(result):
        moreSpecificError = _res.error(result).withContext(f"An error was found in ddck file {inputDdckContent}")
        return moreSpecificError
    privateVariables, computedVariables = _res.value(result)

    privateNames = [f"{componentName}{v.name}" for v in privateVariables]

    computedNames = []
    for computedVariable in computedVariables:
        namesForPort = namesByPort.get(computedVariable.portName, {})
        if _isEmpty(namesForPort):
            return _res.Error(f"Unknown port `{computedVariable.portName}` in {inputDdckFilePath.name}")

        computedName = namesForPort.get(computedVariable.portProperty)
        if not computedName:
            return _res.Error(
                f"Unknown property `{computedVariable.portProperty}` in for port `{computedVariable.portName}` in "
                f"{inputDdckFilePath.name}"
            )

        computedNames.append(computedName)

    outputDdckContent = _replacePrivateAndComputedVariables(
        inputDdckContent, privateVariables, computedVariables, privateNames, computedNames
    )

    return outputDdckContent


def _replacePrivateAndComputedVariables(
    inputDdckContent, privateVariables, computedVariables, privateNames, computedNames
):
    sortedTokens, sortedReplacements = _getSortedTokensAndReplacements(
        privateVariables, computedVariables, privateNames, computedNames
    )
    outputDdckContent = _replaceSortedNonOverlappingTokens(inputDdckContent, sortedTokens, sortedReplacements)
    return outputDdckContent


def _getSortedTokensAndReplacements(
    privateVariables: _tp.Sequence[_PrivateVariable],
    computedVariables: _tp.Sequence[_ComputedVariable],
    replacementsForPrivateVariables: _tp.Sequence[str],
    replacementsForComputedVariables: _tp.Sequence[str],
) -> _tp.Sequence[_tp.Tuple[_Token, str]]:
    tokens = [*privateVariables, *computedVariables]
    replacements = [*replacementsForPrivateVariables, *replacementsForComputedVariables]

    tokenAndReplacements = zip(tokens, replacements)

    sortedTokenAndReplacements = list(sorted(tokenAndReplacements, key=lambda t: t[0].startIndex))

    sortedTokens, sortedReplacements = zip(*sortedTokenAndReplacements)

    return sortedTokens, sortedReplacements


def _isEmpty(dictionary) -> bool:
    return not bool(dictionary)


def _getPrivateAndComputedVariables(
    ddckContent: str,
) -> _res.Result[_tp.Tuple[_tp.Sequence[_PrivateVariable], _tp.Sequence[_ComputedVariable]]]:
    result = _parse.parseDdck(ddckContent)
    if _res.isError(result):
        return _res.error(result)
    tree = _res.value(result)

    visitor = _CollectPrivateAndComputedVariables()
    visitor.visit(tree)

    return visitor.privateVariables, visitor.computedVariables


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
