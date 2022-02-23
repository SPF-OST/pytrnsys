import dataclasses as _dc
import pathlib as _pl
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

from . import _parse


@_dc.dataclass
class _ComputedVariable:  # pylint: disable=too-few-public-methods
    startIndex: int
    endIndex: int
    # defaultVariableName: str
    portProperty: str
    portName: str

    # @property
    # def lengthChange(self) -> int:
    #     lengthBeforeReplacing = self.endIndex - self.startIndex
    #     lengthAfterReplacing = len(self.defaultVariableName)
    #     lengthChange = lengthAfterReplacing - lengthBeforeReplacing
    #     return lengthChange

    def lengthChange(self, replacementString) -> int:
        lengthBeforeReplacing = self.endIndex - self.startIndex
        lengthAfterReplacing = len(replacementString)
        lengthChange = lengthAfterReplacing - lengthBeforeReplacing
        return lengthChange


class _CollectComputedVariables(_lvis.Visitor_Recursive):
    def __init__(self):
        super().__init__()

        self.computedVariables = []

    # def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
    #     defaultVariableName = self._getChildToken("DEFAULT_VARIABLE_NAME", tree)
    #     computedVariable = _ComputedVariable(tree.meta.start_pos, tree.meta.end_pos, defaultVariableName)
    #     self.computedVariables.append(computedVariable)

    def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        portProperty = self._getChildToken("PORT_PROPERTY", tree)
        portName = self._getChildToken("PORT_NAME", tree)
        computedVariable = _ComputedVariable(tree.meta.start_pos, tree.meta.end_pos, portProperty, portName)
        self.computedVariables.append(computedVariable)

    @staticmethod
    def _getChildToken(tokenType: str, tree: _lark.Tree) -> str:  # pylint: disable=invalid-name
        matchingChildTokens = [c for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]

        if len(matchingChildTokens) != 1:
            raise ValueError(f"None or more than one token of type {tokenType} found.")

        matchingChildToken = matchingChildTokens[0]

        return matchingChildToken.value


# def replaceComputedVariablesWithDefaults(inputDdckFilePath: _pl.Path, outputDdckFilePath: _pl.Path) -> None:
#     computedVariables = _getComputedVariablesSortedByStartIndexAscending(inputDdckFilePath)
#     inputDdckContent = inputDdckFilePath.read_text()
#     outputDdckContent = inputDdckContent
#     offset = 0
#     for computedVariable in computedVariables:
#         outputDdckContent = _replace(
#             outputDdckContent,
#             offset + computedVariable.startIndex,
#             offset + computedVariable.endIndex,
#             computedVariable.defaultVariableName,
#         )
#         offset += computedVariable.lengthChange
#     outputDdckFilePath.write_text(outputDdckContent)
def replaceComputedVariablesWithNameUsingPath(inputDdckFilePath: _pl.Path, outputDdckFilePath: _pl.Path,
                                              jsonData: dict) -> None:
    computedVariables = _getComputedVariablesSortedByStartIndexAscending(inputDdckFilePath)

    inputDdckContent = inputDdckFilePath.read_text()

    outputDdckContent = inputDdckContent
    offset = 0
    for computedVariable in computedVariables:
        if computedVariable.portName in jsonData and computedVariable.portProperty in jsonData[
            computedVariable.portName]:
            replamentString = jsonData[computedVariable.portName][computedVariable.portProperty]

            outputDdckContent = _replace(
                outputDdckContent,
                offset + computedVariable.startIndex,
                offset + computedVariable.endIndex,
                replamentString,
            )
            offset += computedVariable.lengthChange(replamentString)

    outputDdckFilePath.write_text(outputDdckContent)


def replaceComputedVariablesWithName(inputFilePathInStr: str, namesByPort: dict) -> str:
    inputDdckFilePath = _pl.Path(inputFilePathInStr)

    computedVariables = _getComputedVariablesSortedByStartIndexAscending(inputDdckFilePath)
    inputDdckContent = inputDdckFilePath.read_text() # pylint: disable=bad-option-value,unspecified-encoding

    outputDdckContent = inputDdckContent
    offset = 0
    for computedVariable in computedVariables:
        namesForPort = namesByPort.get(computedVariable.portName, {})
        if _isEmpty(namesForPort):
            raise Exception(
                f"There is no connection name in json file for {computedVariable.portName} for {inputFilePathInStr}")

        replamentString = namesForPort.get(computedVariable.portProperty, {})
        if _isEmpty(replamentString):
            raise Exception(
                f"There is no {computedVariable.portProperty} in json file for {computedVariable.portName} for "
                f"{inputFilePathInStr}")

        outputDdckContent = _replace(
            outputDdckContent,
            offset + computedVariable.startIndex,
            offset + computedVariable.endIndex,
            replamentString,
        )
        offset += computedVariable.lengthChange(replamentString)

    return outputDdckContent


def _isEmpty(dictionary) -> bool:
    return not bool(dictionary)


def _getComputedVariablesSortedByStartIndexAscending(inputDdckFilePath: _pl.Path) -> _tp.Sequence["_ComputedVariable"]:
    tree = _parse.parseDdck(inputDdckFilePath)
    visitor = _CollectComputedVariables()
    visitor.visit(tree)

    sortedComputedVariables = sorted(visitor.computedVariables, key=lambda v: v.startIndex)

    currentAndNext = zip(sortedComputedVariables[:-1], sortedComputedVariables[1:])
    assert all(n.startIndex >= c.endIndex for c, n in currentAndNext)

    return sortedComputedVariables


def _replace(content: str, startIndex: int, endIndex: int, replacement: str) -> str:
    return content[:startIndex] + replacement + content[endIndex:]
