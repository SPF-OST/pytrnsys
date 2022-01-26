import typing as _tp
import pathlib as _pl
import shutil as _sh

import lark as _lark
import lark.visitors as _lvis


def replaceComputedVariablesWithDefaults(
        inputDdckFilePath: _pl.Path, outputDdckFilePath: _pl.Path
) -> None:
    _sh.copy(inputDdckFilePath, outputDdckFilePath)


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
        children = tree.children
        assert len(children) == 1
        child = children[0]

        assert isinstance(child, _lark.Token)
        token = child

        variableName = token.value

        self._variableNames.add(variableName)
