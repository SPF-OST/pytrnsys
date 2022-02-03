import pathlib as _pl
import re as _re
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

import pytrnsys.ddck.parse as _parse


def replaceComputedVariablesWithDefaults(
        inputDdckFilePath: _pl.Path, outputDdckFilePath: _pl.Path
) -> None:
    tree = _parse.parseDdck(inputDdckFilePath)

    visitor = _CollectAllVariableNamesVisitor()

    visitor.computed_var(tree)

    inputContent = inputDdckFilePath.read_text()

    copyContent = inputContent

    with open(outputDdckFilePath, "wt") as outputDdckFile:
        for _unused in range(len(visitor.variableNames)):
            search = _re.search(r'[^!*](@.+?[)])', copyContent, flags=_re.DOTALL)
            if search is not None:
                filteredSearch = _re.search(r'(@.+?[)])', search.group(0), flags=_re.DOTALL)
                if filteredSearch is not None:
                    matching = [defaultPortName for defaultPortName in visitor.variableNames if
                                defaultPortName in filteredSearch.group(0)]
                    copyContent = copyContent.replace(filteredSearch.group(0), matching[0])
        outputDdckFile.write(copyContent)


class _CollectAllVariableNamesVisitor(_lvis.Visitor_Recursive):
    def __init__(self):
        super().__init__()

        self._variableNames = set()

    @property
    def variableNames(self) -> _tp.Sequence[str]:
        return sorted(self._variableNames)

    def computed_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        self._addVariableName(tree)

    def _addVariableName(self, tree: _lark.Tree) -> None:
        for child in tree.children:
            if tree.data == "computed_var":
                token = tree.children[-1]
                self._variableNames.add(token)
            elif isinstance(child, _lark.Tree):
                self._addVariableName(child)
