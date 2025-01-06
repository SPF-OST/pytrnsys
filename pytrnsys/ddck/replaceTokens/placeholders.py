import collections.abc as _cabc
import pathlib as _pl
import typing as _tp

import lark as _lark

import pytrnsys.ddck.parse.parse as _parse
import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.ddck.replaceTokens.error as _error
import pytrnsys.ddck.replaceTokens.onlinePlotter as _op
import pytrnsys.ddck.replaceTokens.tokens as _tokens
from pytrnsys.utils import result as _res
from . import _common


class _WithPlaceholdersJSONCollectTokensVisitor(_common.CollectTokensVisitorBase):
    def computed_output_temp_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        computedVariable = _common.createComputedVariable(tree, "@temp")
        self.computedHydraulicVariables.append(computedVariable)


def replaceTokens(
    inputDdckFilePath: _pl.Path,
    componentName: str,
    computedNamesByPort: _cabc.Mapping[str, _cabc.Mapping[str, str]],
    defaultVisibility: _dv.DefaultVisibility,
) -> _res.Result[str]:
    if not inputDdckFilePath.is_file():
        return _res.Error(f"Could not replace placeholders in file {inputDdckFilePath}: the file does not exist.")

    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    result = replaceTokensInString(
        inputDdckContent,
        componentName,
        computedNamesByPort,
        defaultVisibility,
        inputDdckFilePath,
    )

    if _res.isError(result):
        error = _res.error(result)
        errorWithContext = error.withContext(f"Could not replace placeholders in ddck file `{inputDdckFilePath}`")
        return errorWithContext

    content = _res.value(result)
    return content


def replaceTokensInString(  # pylint: disable=too-many-locals
    content: str,
    componentName: str,
    computedNamesByPort: _cabc.Mapping[str, _cabc.Mapping[str, str]],
    defaultVisibility: _dv.DefaultVisibility,
    filePath: _pl.Path | None = None,
) -> _res.Result[str]:
    treeResult = _parse.parseDdck(content)
    if _res.isError(treeResult):
        return _res.error(treeResult)
    tree = _res.value(treeResult)

    visitor = _WithPlaceholdersJSONCollectTokensVisitor(componentName, defaultVisibility)
    onlinePlotterVisitor = _op.LeftRightVariablesVisitor()
    try:
        visitor.visit(tree)

        # online plotter visitor must come after general visitor as it relies on some things checked
        # in latter
        onlinePlotterVisitor.visit(tree)
    except _error.ReplaceTokenError as error:
        errorMessage = error.getErrorMessage(content, filePath)
        return _res.Error(errorMessage)

    computedHydraulicNamesResult = _getComputedHydraulicNames(visitor.computedHydraulicVariables, computedNamesByPort)
    if _res.isError(computedHydraulicNamesResult):
        return _res.error(computedHydraulicNamesResult)
    computedHydraulicNames = _res.value(computedHydraulicNamesResult)

    computedHydraulicTokensAndReplacement = zip(visitor.computedHydraulicVariables, computedHydraulicNames)

    tokensAndReplacements = [
        *computedHydraulicTokensAndReplacement,
        *visitor.tokensAndReplacement,
        *onlinePlotterVisitor.tokensAndReplacement,
    ]

    outputDdckContent = _tokens.replaceTokensWithReplacements(content, tokensAndReplacements)

    return outputDdckContent


def _getComputedHydraulicNames(
    computedVariables: _tp.Sequence[_common.ComputedVariable],
    computedNamesByPort: _cabc.Mapping[str, _cabc.Mapping[str, str]],
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
