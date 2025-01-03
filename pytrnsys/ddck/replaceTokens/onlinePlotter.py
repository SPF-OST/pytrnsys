import collections.abc as _cabc
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

import pytrnsys.ddck.replaceTokens.error as _error
import pytrnsys.ddck.replaceTokens.tokens as _tokens
from .. import _visitorHelpers as _vh


class LeftRightVariablesVisitor(_lvis.Visitor_Recursive):
    _TYPE_NUMBER = 65
    _N_PARAMETERS = 12
    _N_LEFT_VARS_PARAM_INDEX = 1
    _N_RIGHT_VARS_PARAM_INDEX = 2

    def __init__(self) -> None:
        self._tokensAndReplacement = list[_tp.Tuple[_tokens.Token, str]]()

    @property
    def tokensAndReplacement(
        self,
    ) -> _cabc.Sequence[_tp.Tuple[_tokens.Token, str]]:
        return self._tokensAndReplacement

    def unit(self, tree: _lark.Tree) -> None:
        typeNumber = _getTypeNumber(tree)
        parameterHashesAndIndex = _getParameterHashesAndIndex(tree)

        if typeNumber != self._TYPE_NUMBER and parameterHashesAndIndex:
            firstHashToken = parameterHashesAndIndex[0][0]
            errorMessage = "Only online plotters (type {self._TYPE_NUMBER}) can have '#' as a parameter."
            raise _error.ReplaceTokenError.fromMetaOrToken(
                firstHashToken,
                errorMessage,
            )

        if typeNumber != self._TYPE_NUMBER:
            return

        parametersSubtree = _vh.getSubtree("parameters", tree)

        parameters = _vh.getSubtrees("parameter", parametersSubtree)
        nParameters = len(parameters)
        if not nParameters == self._N_PARAMETERS:
            errorMessage = f"Online plotters (type {self._TYPE_NUMBER}) must have " f"{self._N_PARAMETERS} parameters."
            raise _error.ReplaceTokenError.fromTree(parametersSubtree, errorMessage)

        inputsSubtree = _vh.getSubtree("inputs", tree)

        inputsAndBars = [
            c for c in inputsSubtree.children if isinstance(c, _lark.Tree) and c.data == "input" or _isVerticalBar(c)
        ]

        bars = [c for c in inputsAndBars if _isVerticalBar(c)]
        inputs = [c for c in inputsAndBars if not _isVerticalBar(c)]

        assert len(inputs) % 2 == 0, "This should be checked in a separate step which is run before this one."

        nActualInputs = int(len(inputs) / 2)

        if parameterHashesAndIndex:
            self._handleHashesInParameters(
                parametersSubtree,
                parameterHashesAndIndex,
                inputsSubtree,
                inputsAndBars,
                nActualInputs,
                bars,
            )
        else:
            self._handleNoHashesInParameters(parameters, inputsSubtree, nActualInputs, bars)

    def _handleHashesInParameters(
        self,
        parametersSubtree: _lark.Tree,
        parameterHashesAndIndex: _cabc.Sequence[_tp.Tuple[_lark.Token, int]],
        inputsSubtree: _lark.Tree,
        inputsAndBars: _cabc.Sequence[_lark.Tree | _lark.Token],
        nActualInputs: int,
        bars: _cabc.Sequence[_lark.Token],
    ) -> None:
        (firstHash, nLeftVariables), (secondHash, nRightVariables) = self._getParameterHashTokensAndReplacements(
            parametersSubtree,
            parameterHashesAndIndex,
            inputsSubtree,
            inputsAndBars,
            nActualInputs,
            bars,
        )

        for verticalBar in bars:
            replacement = ""
            self._addTokenAndReplacement(verticalBar, replacement)

        self._addTokenAndReplacement(firstHash, f"{nLeftVariables}")
        self._addTokenAndReplacement(secondHash, f"{nRightVariables}")

    def _getParameterHashTokensAndReplacements(
        self,
        parametersSubtree: _lark.Tree,
        parameterHashesAndIndex: _cabc.Sequence[_tp.Tuple[_lark.Token, int]],
        inputsSubtree: _lark.Tree,
        inputsAndBars: _cabc.Sequence[_lark.Tree | _lark.Token],
        nActualInputs: int,
        verticalBars: _cabc.Sequence[_lark.Token],
    ) -> _tp.Tuple[_tp.Tuple[_lark.Token, int], _tp.Tuple[_lark.Token, int]]:
        firstHash, secondHash = self._getParameterHashTokens(parameterHashesAndIndex, parametersSubtree)

        nLeftVariables, nRightVariables = self._getNLeftAndRightVariables(
            inputsSubtree, inputsAndBars, nActualInputs, verticalBars
        )

        return (firstHash, nLeftVariables), (secondHash, nRightVariables)

    def _getNLeftAndRightVariables(
        self,
        inputsSubtree: _lark.Tree,
        inputsAndBars: _cabc.Sequence[_lark.Tree | _lark.Token],
        nActualInputs: int,
        verticalBars: _cabc.Sequence[_lark.Token],
    ) -> _tp.Tuple[int, int]:
        notTwoBarsErrorMessage = f"""\
        If a bar ("|") is used in an online plotter's (type {self._TYPE_NUMBER}) input list
        then it must be used in the input variables list as well as in the initial values
        list like so:

            INPUTS #    
            TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
            TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed

        """
        if len(verticalBars) != 2:
            raise _error.ReplaceTokenError.fromTree(inputsSubtree, notTwoBarsErrorMessage)
        # +1 for the bar
        inputVariables = inputsAndBars[: nActualInputs + 1]
        initialValues = inputsAndBars[nActualInputs + 1 :]
        splitInputVariables = _split(inputVariables, _isVerticalBar)
        splitInitialValues = _split(initialValues, _isVerticalBar)
        inputVariableLengths = [len(ivs) for ivs in splitInputVariables]
        initialValueLengths = [len(ivs) for ivs in splitInitialValues]
        assert len(inputVariableLengths) == 2 == len(initialValueLengths)
        if inputVariableLengths != initialValueLengths:
            raise _error.ReplaceTokenError.fromTree(inputsSubtree, notTwoBarsErrorMessage)
        nLeftVariables = inputVariableLengths[0]
        nRightVariables = inputVariableLengths[1]
        return nLeftVariables, nRightVariables

    def _getParameterHashTokens(
        self,
        parameterHashesAndIndex: _cabc.Sequence[_tp.Tuple[_lark.Token, int]],
        parametersSubtree: _lark.Tree,
    ) -> _tp.Tuple[_lark.Token, _lark.Token]:
        if parameterHashesAndIndex and len(parameterHashesAndIndex) != 2:
            errorMessage = (
                f"An online plotter (type {self._TYPE_NUMBER}) "
                f"must either have two '#' as parameters or none at all."
            )

            raise _error.ReplaceTokenError.fromTree(parametersSubtree, errorMessage)

        (firstHash, firstHashIndex), (secondHash, secondHashIndex) = parameterHashesAndIndex

        errorMessage = (
            f"A hash can only be used as parameter {self._N_LEFT_VARS_PARAM_INDEX} "
            f"or {self._N_RIGHT_VARS_PARAM_INDEX} of an online plotter (type "
            f"{self._TYPE_NUMBER})."
        )

        if firstHashIndex != self._N_LEFT_VARS_PARAM_INDEX:
            raise _error.ReplaceTokenError.fromMetaOrToken(firstHash, errorMessage)

        if secondHashIndex != self._N_RIGHT_VARS_PARAM_INDEX:
            raise _error.ReplaceTokenError.fromMetaOrToken(secondHash, errorMessage)

        return firstHash, secondHash

    def _handleNoHashesInParameters(
        self,
        parameters: _cabc.Sequence[_lark.Tree],
        inputsSubtree: _lark.Tree,
        nActualInputs: int,
        verticalBars: _cabc.Sequence[_lark.Token],
    ) -> None:
        if verticalBars:
            errorMessage = f"""\
        A bar ("|") can only be used in an online plotter's (type {self._TYPE_NUMBER})
        input list if hashes ("#") are used for the parameters specifying the number of
        left and right axis variables (parameter {self._N_LEFT_VARS_PARAM_INDEX} and
        {self._N_RIGHT_VARS_PARAM_INDEX}), respectively."""

            raise _error.ReplaceTokenError.fromTree(inputsSubtree, errorMessage)

        nLeftInputs = _vh.getChildTokenValueOrNone("POSITIVE_INT", parameters[self._N_LEFT_VARS_PARAM_INDEX], int)
        nRightInputs = _vh.getChildTokenValueOrNone("POSITIVE_INT", parameters[self._N_RIGHT_VARS_PARAM_INDEX], int)

        if nLeftInputs is None and nRightInputs is None:
            # both variables, nothing more to do
            return

        if nLeftInputs is not None and nRightInputs is not None:
            nExpectedInputs = nLeftInputs + nRightInputs
            if nActualInputs == nExpectedInputs:
                return

            errorMessage = f"{nExpectedInputs} input(s) were expected but only {nActualInputs} were specified."
            raise _error.ReplaceTokenError.fromTree(inputsSubtree, errorMessage)

        nMinInputs = nLeftInputs if nLeftInputs is not None else nRightInputs
        assert isinstance(nMinInputs, int)

        if nActualInputs >= nMinInputs:
            return

        errorMessage = f"At least {nMinInputs} input(s) were expected, but {nActualInputs} were given."
        raise _error.ReplaceTokenError.fromTree(inputsSubtree, errorMessage)

    def _addTokenAndReplacement(self, verticalBar: _lark.Token, replacement: str) -> None:
        self._tokensAndReplacement.append((_tokens.Token.fromMetaOrToken(verticalBar), replacement))


def _getTypeNumber(tree: _lark.Tree) -> int:
    visitor = _TypeNumberVisitor()

    visitor.visit(tree)

    typeNumber = visitor.typeNumber
    if not typeNumber:
        raise ValueError("Tree doesn't have a type number.", tree)

    return typeNumber


def _isVerticalBar(
    treeOrToken: _lark.Tree | _lark.Token,
) -> _tp.TypeGuard[_lark.Token]:
    return isinstance(treeOrToken, _lark.Token) and treeOrToken.type == "BAR"


class _TypeNumberVisitor(_lvis.Visitor_Recursive):
    def __init__(self) -> None:
        self.typeNumber: int | None = None

    def type_number(self, tree: _lark.Tree) -> None:  # pylint: disable=invalid-name
        self.typeNumber = _vh.getChildTokenValue("POSITIVE_INT", tree, int)


_HashesAndIndex = _cabc.Sequence[_tp.Tuple[_lark.Token, int]]


class _HashesAndIndexVisitor(_lvis.Visitor_Recursive):
    def __init__(self) -> None:
        self.hashesAndIndex: _HashesAndIndex = []

    def parameters(self, tree: _lark.Tree) -> None:
        parameters = _vh.getSubtrees("parameter", tree)

        hashesAndIndex = [
            (t, i) for i, p in enumerate(parameters, start=1) if (t := _vh.getChildTokenOrNone("HASH", p))
        ]

        self.hashesAndIndex = hashesAndIndex


def _getParameterHashesAndIndex(tree: _lark.Tree) -> _HashesAndIndex:
    visitor = _HashesAndIndexVisitor()
    visitor.visit(tree)
    return visitor.hashesAndIndex


_T_co = _tp.TypeVar("_T_co", covariant=True)


def _split(
    sequence: _cabc.Sequence[_T_co], isSplitter: _tp.Callable[[_T_co], bool]
) -> _cabc.Sequence[_cabc.Sequence[_T_co]]:
    subSequences = []
    subSequence = list[_T_co]()

    for element in sequence:
        if isSplitter(element):
            subSequences.append(subSequence)
            subSequence = []
            continue

        subSequence.append(element)

    subSequences.append(subSequence)

    return subSequences
