import dataclasses as _dc
import collections.abc as _cabc

import pytest as _pt

import pytrnsys.utils.result as _res
import pytrnsys.ddck.replaceTokens.error as _error
import pytrnsys.ddck.parse.parse as _parse
import pytrnsys.ddck.replaceTokens.onlinePlotter as _op
import pytrnsys.ddck.replaceTokens.tokens as _tokens


@_dc.dataclass
class TestCase:
    id: str
    input: str
    expectedOutput: str | _error.ReplaceTokenError


def getTestCases() -> _cabc.Iterable[TestCase]:
    yield TestCase(
        "standard-use-case",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
#     				! 1: Nb. of left-axis variables
#     				! 2: Nb. of right-axis variables
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
1e5       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
12     				! 8: X-axis gridpoints
1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
8     				! 1: Nb. of left-axis variables
3     				! 2: Nb. of right-axis variables
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
1e5       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
12     				! 8: X-axis gridpoints
1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff  MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff  MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
    )


class TestOnlinePlotter:
    @_pt.mark.parametrize("testCase", [_pt.param(tc, id=tc.id) for tc in getTestCases()])
    def test(self, testCase: TestCase) -> None:
        result = _parse.parseDdck(testCase.input)
        assert not _res.isError(result)
        tree = _res.value(result)

        visitor = _op.LeftRightVariablesVisitor()
        visitor.visit(tree)

        actualOutput = _tokens.replaceTokensWithReplacements(testCase.input, visitor.tokensAndReplacement)

        assert actualOutput == testCase.expectedOutput
