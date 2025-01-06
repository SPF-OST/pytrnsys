import collections.abc as _cabc
import pathlib as _pl
import typing as _tp

import lark as _lark
from lark import visitors as _lvis

import pytrnsys.ddck._visitorHelpers as _vh
import pytrnsys.ddck.parse.parse as _parse
import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.ddck.replaceTokens.error as _error
import pytrnsys.ddck.replaceTokens.onlinePlotter as _op
import pytrnsys.ddck.replaceTokens.tokens as _tokens
import pytrnsys.utils.result as _res
from . import _common


class _WithoutPlaceholdersJSONCollectTokensVisitor(_common.CollectTokensVisitorBase):
    def __init__(self, componentName: str, defaultVisibility: _dv.DefaultVisibility) -> None:
        super().__init__(componentName, defaultVisibility)

    def equations(self, tree: _lark.Tree) -> None:
        equationsVisitor = _WithoutPlaceholdersJSONCollectEquationsTokensVisitor()
        equationsVisitor.visit(tree)

        nComputedOutputVariablesWithoutDefaults = equationsVisitor.nComputedOutputVariablesWithoutDefaults

        if nComputedOutputVariablesWithoutDefaults == 0:
            super().equations(tree)
            return

        equationSubtrees = _vh.getSubtreesNonEmpty("equation", tree)
        actualNumberOfEquations = len(equationSubtrees)

        declaredNumberOfEquationsTree = _vh.getSubtreeOrNone("number_of_equations", tree)
        if declaredNumberOfEquationsTree:
            self._checkDeclaredNumberOf(
                "equations",
                declaredNumberOfEquationsTree,
                actualNumberOfEquations,
            )

        if nComputedOutputVariablesWithoutDefaults == actualNumberOfEquations:
            token = _tokens.Token.fromTree(tree)
            self._addReplacement(token, "! Empty EQUATIONS block removed by pytrnsys")
            return

        self.tokensAndReplacement.extend(equationsVisitor.tokensAndReplacement)

        adjustedActualNumberOfEquations = actualNumberOfEquations - nComputedOutputVariablesWithoutDefaults

        replacement = str(adjustedActualNumberOfEquations)

        if declaredNumberOfEquationsTree:
            token = _tokens.Token.fromTree(declaredNumberOfEquationsTree)
            self._addReplacement(token, replacement)
            return

        hashToken = _vh.getChildToken("HASH", tree)
        token = _tokens.Token.fromMetaOrToken(hashToken)
        self._addReplacement(token, replacement)


class _WithoutPlaceholdersJSONCollectEquationsTokensVisitor(_lvis.Visitor_Recursive):
    def __init__(self) -> None:
        super().__init__()
        self.tokensAndReplacement: list[tuple[_tokens.Token, str]] = []
        self.nComputedOutputVariablesWithoutDefaults = 0

    def equation(self, tree: _lark.Tree) -> None:
        assert len(tree.children) == 2

        assignmentTarget = tree.children[0]
        assert isinstance(assignmentTarget, _lark.Tree)
        if assignmentTarget.data != "computed_output_temp_var":
            return

        computedVariable = _common.createComputedVariable(assignmentTarget, "@temp")

        tokenAndReplacement: _tp.Tuple[_tokens.Token, str]

        if computedVariable.defaultVariableName:
            replacement = computedVariable.defaultVariableName
            tokenAndReplacement = (computedVariable, replacement)
            self.tokensAndReplacement.append(tokenAndReplacement)
            return

        self.nComputedOutputVariablesWithoutDefaults += 1

        portName = _vh.getChildTokenValue("PORT_NAME", assignmentTarget, str)
        replacement = f"! Assignment to temperature at `{portName}` removed by pytrnsys"

        token = _tokens.Token.fromTree(tree)

        tokenAndReplacement = (token, replacement)

        self.tokensAndReplacement.append(tokenAndReplacement)


def replaceTokensWithDefaults(
    inputDdckFilePath: _pl.Path,
    componentName: str,
    defaultVisibility: _dv.DefaultVisibility,
) -> _res.Result[str]:
    inputDdckContent = inputDdckFilePath.read_text(encoding="windows-1252")  # pylint: disable=bad-option-value

    result = replaceTokensWithDefaultsInString(inputDdckContent, componentName, defaultVisibility, inputDdckFilePath)
    if _res.isError(result):
        error = _res.error(result).withContext(f"Error processing file `{inputDdckFilePath.name}`")
        return error

    return _res.value(result)


def replaceTokensWithDefaultsInString(
    inputDdckContent: str,
    componentName: str,
    defaultVisibility: _dv.DefaultVisibility,
    filePath: _pl.Path | None = None,
) -> _res.Result[str]:
    visitorResults = _createVisitAndGetVisitors(inputDdckContent, componentName, defaultVisibility, filePath)
    if _res.isError(visitorResults):
        return visitorResults
    visitor, onlinePlotterVisitor = _res.value(visitorResults)

    hydraulicVariableReplacementsResult = _getReplacementsForHydraulicVariables(visitor.computedHydraulicVariables)
    if _res.isError(hydraulicVariableReplacementsResult):
        moreSpecificError = _res.error(hydraulicVariableReplacementsResult).withContext(
            "Could not substitute the defaults for the placeholders"
        )
        return moreSpecificError
    hydraulicVariableReplacements = _res.value(hydraulicVariableReplacementsResult)

    hydraulicVariableTokensAndReplacement = list(zip(visitor.computedHydraulicVariables, hydraulicVariableReplacements))

    tokensAndReplacement = [
        *hydraulicVariableTokensAndReplacement,
        *visitor.tokensAndReplacement,
        *onlinePlotterVisitor.tokensAndReplacement,
    ]

    outputDdckContent = _tokens.replaceTokensWithReplacements(inputDdckContent, tokensAndReplacement)

    return outputDdckContent


def _createVisitAndGetVisitors(
    inputDdckContent: str,
    componentName: str,
    defaultVisibility: _dv.DefaultVisibility,
    filePath: _pl.Path | None,
) -> _res.Result[_tp.Tuple[_WithoutPlaceholdersJSONCollectTokensVisitor, _op.LeftRightVariablesVisitor,]]:
    result = _parse.parseDdck(inputDdckContent)
    if _res.isError(result):
        moreSpecificError = _res.error(result)
        return moreSpecificError
    tree = _res.value(result)

    visitor = _WithoutPlaceholdersJSONCollectTokensVisitor(componentName, defaultVisibility)
    onlinePlotterVisitor = _op.LeftRightVariablesVisitor()
    try:
        visitor.visit(tree)

        # online plotter visitor must come after general visitor as it relies on some things checked
        # in latter
        onlinePlotterVisitor.visit(tree)
    except _error.ReplaceTokenError as replaceTokenError:
        errorMessage = replaceTokenError.getErrorMessage(inputDdckContent, filePath)
        return _res.Error(errorMessage)

    return visitor, onlinePlotterVisitor


def _getReplacementsForHydraulicVariables(
    computedHydraulicVariables: _cabc.Sequence[_common.ComputedVariable],
) -> _res.Result[_tp.Sequence[str]]:

    computedVariablesWithoutDefaultName = [v for v in computedHydraulicVariables if not v.defaultVariableName]
    if any(computedVariablesWithoutDefaultName):
        formattedLocations = "\n".join(f"\t{v.startLine}:{v.startColumn}" for v in computedVariablesWithoutDefaultName)
        errorMessage = (
            "No default values were provided for the computed variables at the following locations "
            f"(line number:column number):\n"
            f"{formattedLocations}\n"
        )
        return _res.Error(errorMessage)
    defaultNamesForComputedVariables = [_tp.cast(str, v.defaultVariableName) for v in computedHydraulicVariables]

    replacements = [
        *defaultNamesForComputedVariables,
    ]

    return replacements
