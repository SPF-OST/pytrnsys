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

    with open(inputDdckFilePath, "rt") as inputDdckFile, open(outputDdckFilePath, "wt") as outputDdckFile:
        for line in inputDdckFile:
            matching = [defaultPortName for defaultPortName in visitor.variableNames if defaultPortName in line]
            if len(matching) > 0:
                replace = _re.sub(r'@.+?[)]', matching[0], line)
                outputDdckFile.write(replace)
            else:
                outputDdckFile.write(line)


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

        "Visits the tree, starting with the leaves and finally the root (bottom-up)"
        for child in tree.children:
            if tree.data == "computer_var":
                token = tree.children[-1]
                self._variableNames.add(token)
            elif isinstance(child, _lark.Tree):
                self._addVariableName(child)
