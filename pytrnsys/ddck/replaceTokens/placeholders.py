import pathlib as _pl
import typing as _tp

import lark as _lark

from pytrnsys.utils import result as _res

from . import _parse, _tokens, _common


class _WithPlaceholdersJSONCollectTokensVisitor(_common.CollectTokensVisitorBase):
    def computed_output_temp_var(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        computedVariable = _common.createComputedVariable(tree, "@temp")
        self.computedHydraulicVariables.append(computedVariable)


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
        error = _res.error(treeResult)

        if not inputDdckFilePath:
            return error

        moreSpecificError = _res.error(treeResult).withContext(
            f"An error was found in ddck file {inputDdckFilePath.name}"
        )

        return moreSpecificError
    tree = _res.value(treeResult)

    visitor = _WithPlaceholdersJSONCollectTokensVisitor()
    visitor.visit(tree)

    privateNames = _common.getPrivateNames(visitor.privateVariables, componentName)

    computedHydraulicNamesResult = _getComputedHydraulicNames(visitor.computedHydraulicVariables, computedNamesByPort)
    if _res.isError(computedHydraulicNamesResult):
        if inputDdckFilePath:
            contextMessage = f"Error replacing placeholders in file {inputDdckFilePath.name}"
        else:
            contextMessage = "Error replacing placeholders"

        error = _res.error(computedHydraulicNamesResult).withContext(contextMessage)

        return error
    computedHydraulicNames = _res.value(computedHydraulicNamesResult)

    computedEnergyNames = _common.getComputedEnergyNames(visitor.computedEnergyVariables, componentName)

    tokens = [*visitor.privateVariables, *visitor.computedHydraulicVariables, *visitor.computedEnergyVariables]
    replacements = [*privateNames, *computedHydraulicNames, *computedEnergyNames]

    outputDdckContent = _tokens.replaceTokensWithReplacements(content, tokens, replacements)

    return outputDdckContent


def _getComputedHydraulicNames(
    computedVariables: _tp.Sequence[_common.ComputedVariable], computedNamesByPort: _tp.Dict[str, _tp.Dict[str, str]]
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
