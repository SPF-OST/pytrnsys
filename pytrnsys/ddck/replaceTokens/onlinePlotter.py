import collections.abc as _cabc
import typing as _tp

import lark as _lark
import lark.visitors as _lvis

import pytrnsys.ddck.replaceTokens.error as _error
import pytrnsys.ddck.replaceTokens.tokens as _tokens
from .. import _visitorHelpers as _vh


def _isBar(
    treeOrToken: _lark.Tree | _lark.Token,
) -> _tp.TypeGuard[_lark.Token]:
    return isinstance(treeOrToken, _lark.Token) and treeOrToken.type == "BAR"


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
        hashesAndIndex = _getHashesAndIndex(tree)

        if typeNumber != self._TYPE_NUMBER and hashesAndIndex:
            firstHashToken = hashesAndIndex[0][0]
            errorMessage = (
                "Only online plotters (type {self._TYPE_NUMBER}) "
                "can have '#' as a parameter."
            )
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
            errorMessage = (
                f"Online plotters (type {self._TYPE_NUMBER}) must have "
                f"{self._N_PARAMETERS} parameters."
            )
            raise _error.ReplaceTokenError.fromTree(
                parametersSubtree, errorMessage
            )

        inputsSubtree = _vh.getSubtree("inputs", tree)

        inputsAndBars = [
            c
            for c in inputsSubtree.children
            if isinstance(c, _lark.Tree) and c.data == "input" or _isBar(c)
        ]

        bars = [c for c in inputsAndBars if _isBar(c)]
        inputs = [c for c in inputsAndBars if not _isBar(c)]

        assert (
            len(inputs) % 2 == 0
        ), "This should be checked in a separate step which is run before this one."

        nActualInputs = int(len(inputs) / 2)

        if not hashesAndIndex:
            if bars:
                errorMessage = f"""\
A bar ("|") can only be used in an online plotter's (type {self._TYPE_NUMBER})
input list if hashes ("#") are used for the parameters specifying the number of
left and right axis variables (parameter {self._N_LEFT_VARS_PARAM_INDEX} and
{self._N_RIGHT_VARS_PARAM_INDEX}), respectively."""

                raise _error.ReplaceTokenError.fromTree(
                    inputsSubtree, errorMessage
                )

            nLeftInputs = _vh.getChildTokenValueOrNone(
                "POSITIVE_INT", parameters[self._N_LEFT_VARS_PARAM_INDEX], int
            )
            nRightInputs = _vh.getChildTokenValueOrNone(
                "POSITIVE_INT", parameters[self._N_RIGHT_VARS_PARAM_INDEX], int
            )

            if nLeftInputs is None and nRightInputs is None:
                # both variables, nothing more to do
                return

            if nLeftInputs is not None and nRightInputs is not None:
                nExpectedInputs = nLeftInputs + nRightInputs
                if nActualInputs == nExpectedInputs:
                    return

                errorMessage = f"{nExpectedInputs} input(s) were expected but only {nActualInputs} were specified."
                raise _error.ReplaceTokenError.fromTree(
                    inputsSubtree, errorMessage
                )

            nMinInputs = (
                nLeftInputs if nLeftInputs is not None else nRightInputs
            )
            assert isinstance(nMinInputs, int)

            if nActualInputs >= nMinInputs:
                return

            errorMessage = f"At least {nMinInputs} input(s) were expected, but {nActualInputs} were given."
            raise _error.ReplaceTokenError.fromTree(
                inputsSubtree, errorMessage
            )

        if hashesAndIndex and len(hashesAndIndex) != 2:
            errorMessage = (
                f"An online plotter (type {self._TYPE_NUMBER}) "
                f"must either have two '#' as parameters or none at all."
            )
            raise _error.ReplaceTokenError.fromTree(
                parametersSubtree, errorMessage
            )

        (firstHash, firstHashIndex), (secondHash, secondHashIndex) = (
            hashesAndIndex
        )
        errorMessage = (
            f"A hash can only be used as parameter {self._N_LEFT_VARS_PARAM_INDEX} "
            f"or {self._N_RIGHT_VARS_PARAM_INDEX} of an online plotter (type "
            f"{self._TYPE_NUMBER})."
        )
        if firstHashIndex != self._N_LEFT_VARS_PARAM_INDEX:
            raise _error.ReplaceTokenError.fromMetaOrToken(
                firstHash, errorMessage
            )
        if secondHashIndex != self._N_RIGHT_VARS_PARAM_INDEX:
            raise _error.ReplaceTokenError.fromMetaOrToken(
                secondHash, errorMessage
            )

        notTwoBarsErrorMessage = f"""\
If a bar ("|") is used in an online plotter's (type {self._TYPE_NUMBER}) input list 
then it must be used in the input variables list as well as in the initial values
list like so:

    INPUTS #    
    TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
    TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed

"""
        if len(bars) != 2:
            raise _error.ReplaceTokenError.fromTree(
                inputsSubtree, notTwoBarsErrorMessage
            )

        # +1 for the bar
        inputVariables = inputsAndBars[: nActualInputs + 1]
        initialValues = inputsAndBars[nActualInputs + 1 :]

        splitInputVariables = _split(inputVariables, _isBar)
        splitInitialValues = _split(initialValues, _isBar)

        inputVariableLengths = [len(ivs) for ivs in splitInputVariables]
        initialValueLengths = [len(ivs) for ivs in splitInitialValues]

        if inputVariableLengths != initialValueLengths:
            raise _error.ReplaceTokenError.fromTree(
                inputsSubtree, notTwoBarsErrorMessage
            )

        for bar in bars:
            replacement = ""
            self._addTokenAndReplacement(bar, replacement)

        nLeftVariables, nRightVariables = inputVariableLengths
        self._addTokenAndReplacement(firstHash, f"{nLeftVariables}")
        self._addTokenAndReplacement(secondHash, f"{nRightVariables}")

    def _addTokenAndReplacement(
        self, bar: _lark.Token, replacement: str
    ) -> None:
        self._tokensAndReplacement.append(
            (_tokens.Token.fromMetaOrToken(bar), replacement)
        )


class _TypeNumberVisitor(_lvis.Visitor_Recursive):
    def __init__(self) -> None:
        self.typeNumber: int | None = None

    def type_number(self, tree: _lark.Tree) -> None:
        self.typeNumber = _vh.getChildTokenValue("POSITIVE_INT", tree, int)


def _getTypeNumber(tree: _lark.Tree) -> int:
    visitor = _TypeNumberVisitor()

    visitor.visit(tree)

    typeNumber = visitor.typeNumber
    if not typeNumber:
        raise ValueError("Tree doesn't have a type number.", tree)

    return typeNumber


_HashesAndIndex = _cabc.Sequence[_tp.Tuple[_lark.Token, int]]


class _HashesAndIndexVisitor(_lvis.Visitor_Recursive):
    def __init__(self) -> None:
        self.hashesAndIndex: _HashesAndIndex = []

    def parameters(self, tree: _lark.Tree) -> None:
        parameters = _vh.getSubtrees("parameter", tree)

        hashesAndIndex = [
            (t, i)
            for i, p in enumerate(parameters, start=1)
            if (t := _vh.getChildTokenOrNone("HASH", p))
        ]

        self.hashesAndIndex = hashesAndIndex


def _getHashesAndIndex(tree: _lark.Tree) -> _HashesAndIndex:
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
