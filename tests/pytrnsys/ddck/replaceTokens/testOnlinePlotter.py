import collections.abc as _cabc
import dataclasses as _dc

import pytest as _pt

import pytrnsys.ddck.parse.parse as _parse
import pytrnsys.ddck.replaceTokens.error as _error
import pytrnsys.ddck.replaceTokens.onlinePlotter as _op
import pytrnsys.ddck.replaceTokens.tokens as _tokens
import pytrnsys.utils.result as _res


@_dc.dataclass
class TestCase:
    id: str
    input: str
    expectedOutput: _res.Result[str]

    def assertActualOutputIsAsExpected(self, actualOutput: str | _error.ReplaceTokenError) -> None:
        if _res.isError(self.expectedOutput):
            assert isinstance(actualOutput, _error.ReplaceTokenError)
            actualErrorMessage = actualOutput.getErrorMessage(self.input)
            print(actualErrorMessage)
            expectedErrorMessage = _res.error(self.expectedOutput).message
            assert actualErrorMessage == expectedErrorMessage
        else:
            assert isinstance(actualOutput, str)
            expectedOutput = _res.value(self.expectedOutput)
            assert actualOutput == expectedOutput


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

    yield TestCase(
        "ignore-other-types",
        """\
UNIT 451 TYPE 929
!DivSh
PARAMETERS 0
INPUTS 6
MDivSh_A
MDivSh_B
MDivSh_C
TPiRadOut
TPiDivSHCool
TPiSHInMix
***Initial values
0 0 0 20 20 20 
EQUATIONS 1
TDivSh= [451,1]

! supplyWater
EQUATIONS 2
Tcw = 1
TsupplyWater = Tcw
""",
        """\
UNIT 451 TYPE 929
!DivSh
PARAMETERS 0
INPUTS 6
MDivSh_A
MDivSh_B
MDivSh_C
TPiRadOut
TPiDivSHCool
TPiSHInMix
***Initial values
0 0 0 20 20 20 
EQUATIONS 1
TDivSh= [451,1]

! supplyWater
EQUATIONS 2
Tcw = 1
TsupplyWater = Tcw
""",
    )

    yield TestCase(
        "hash-params-only-in-online-plotter",
        """\
UNIT 460 TYPE 931
!PiHpToTesShIn
PARAMETERS 6
0.02 ! diameter [m]
2.0 ! length [m]
2.99988 ! U-value [kJ/(h*m^2*K)] (= 0.8333 W/(m^2*K))
#
Lloop1Cp
20
INPUTS 4
TPuHpShCond
MPiHpToTesShIn_A
TRoomStore
TSHDpL95_5H
***Initial values
20 0.0 20 20
""",
        _res.Error(
            """\
Only online plotters (type 65) can have '#' as a parameter:

At <string>:7:

PARAMETERS 6
0.02 ! diameter [m]
2.0 ! length [m]
2.99988 ! U-value [kJ/(h*m^2*K)] (= 0.8333 W/(m^2*K))
#
^
Lloop1Cp
20
INPUTS 4
TPuHpShCond
MPiHpToTesShIn_A
"""
        ),
    )

    yield TestCase(
        "wrong-number-of-params",
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
        _res.Error(
            """\
Online plotters (type 65) must have 12 parameters:

At <string>:5:

 ** Online Plotter
 ***********************************
 UNIT 103 TYPE 65		!Changed automatically
 PARAMETERS #     
 ^
 #     				! 1: Nb. of left-axis variables
 #     				! 2: Nb. of right-axis variables
 -0.5   				! 3: Left axis minimum
 100        			! 4: Left axis maximum
 -1   				! 5: Right axis minimum
 1e5       			! 6: Right axis maximum
 $nPlotsPerSim		! 7: Number of plots per simulation
 12     				! 8: X-axis gridpoints
 -1     				! 10: Logical unit for output file
 0     				! 11: Output file units
 0     				! 12: Output file delimiter
 INPUTS #    
 TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
 TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
 LABELS #     
 "Tempertures [degC] and statuses [1]"
"""
        ),
    )

    yield TestCase(
        "no-hashes-but-bars",
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """\
A bar ("|") can only be used in an online plotter's (type 65) input
list if hashes ("#") are used for the parameters specifying the number of left and right
axis variables (parameter 1 and 2, respectively):

At <string>:19:

-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
                                                                                 ^
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
"""
        ),
    )

    yield TestCase(
        "no-hashes-normal-use-case",
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
    )

    yield TestCase(
        "no-hashes-sum-unequal-to-inputs",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
8     				! 1: Nb. of left-axis variables
2     				! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """10 input(s) were expected but 11 were specified:

At <string>:18:

1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
"""
        ),
    )

    yield TestCase(
        "no-hashes-two-vars",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
nLeftVariables  	! 1: Nb. of left-axis variables
nRightVariables		! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        """***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
nLeftVariables  	! 1: Nb. of left-axis variables
nRightVariables		! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
    )

    yield TestCase(
        "no-hashes-too-few-vars",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
13     				! 1: Nb. of left-axis variables
nRightVars			! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """At least 13 input(s) were expected, but 11 were given:

At <string>:18:

1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
"""
        ),
    )

    yield TestCase(
        "no-hashes-enough-vars",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
nLeftVars			! 1: Nb. of left-axis variables
3       			! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        """***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
nLeftVars			! 1: Nb. of left-axis variables
3       			! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
    )

    yield TestCase(
        "no-hashes-n-var-float",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
13.9     			! 1: Nb. of left-axis variables
nRightVars			! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """Parameters 1 and 2 of an online plotter (type 65)
must be non-negative integers:

At <string>:6:

** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
13.9     			! 1: Nb. of left-axis variables
^^^^
nRightVars			! 2: Nb. of right-axis variables
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
1e5       			! 6: Right axis maximum
"""
        ),
    )

    yield TestCase(
        "no-hashes-n-var-negative",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
8        		    ! 1: Nb. of left-axis variables
-2      		    ! 2: Nb. of right-axis variables
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """Parameters 1 and 2 of an online plotter (type 65)
must be non-negative integers:

At <string>:7:

***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
8        		    ! 1: Nb. of left-axis variables
-2      		    ! 2: Nb. of right-axis variables
^^
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
1e5       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
"""
        ),
    )

    yield TestCase(
        "too-many-bars",
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
TSources TStore TNetReturn TMixed | mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed | mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """If a bar ("|") is used in an online plotter's (type 65) input list
then it must be used in the input variables list as well as in the initial values
list like so:

    INPUTS #    
    TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
    TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed

It can only be used exactly once in each list and must be used in the same position.

:

At <string>:18:

1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TSources TStore TNetReturn TMixed | mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed | mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
"""
        ),
    )

    yield TestCase(
        "bars-in-different-positions",
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
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow | bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """If a bar ("|") is used in an online plotter's (type 65) input list
then it must be used in the input variables list as well as in the initial values
list like so:

    INPUTS #    
    TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
    TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed

It can only be used exactly once in each list and must be used in the same position.

:

At <string>:18:

1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow | bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
"""
        ),
    )

    yield TestCase(
        "too-many-hashes",
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
#       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
12     				! 8: X-axis gridpoints
1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow | bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """An online plotter (type 65) must either have two '#' as parameters or none at all:

At <string>:5:

** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
^
#     				! 1: Nb. of left-axis variables
#     				! 2: Nb. of right-axis variables
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
#       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
12     				! 8: X-axis gridpoints
1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow | bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"""
        ),
    )

    yield TestCase(
        "wrong-left-var-hash",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
3     				! 1: Nb. of left-axis variables
#     				! 2: Nb. of right-axis variables
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
#       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
12     				! 8: X-axis gridpoints
1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow | bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """A hash can only be used as parameter 1 or 2 of an online plotter (type 65):

At <string>:7:

***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
3     				! 1: Nb. of left-axis variables
#     				! 2: Nb. of right-axis variables
^
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
#       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
"""
        ),
    )

    yield TestCase(
        "wrong-right-var-hash",
        """\
***********************************
** Online Plotter
***********************************
UNIT 103 TYPE 65		!Changed automatically
PARAMETERS #     
#     				! 1: Nb. of left-axis variables
3     				! 2: Nb. of right-axis variables
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
#       			! 6: Right axis maximum
$nPlotsPerSim		! 7: Number of plots per simulation
12     				! 8: X-axis gridpoints
1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
0     				! 12: Output file delimiter
INPUTS #    
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow bypassOff | MSources MFromStore MMixed
TSources TStore TNetReturn TMixed mixOn storeOn needStoreButTempTooLow | bypassOff MSources MFromStore MMixed
LABELS #     
"Tempertures [degC] and statuses [1]"
"Mass flow rates [kg/h]"
ValByPass
""",
        _res.Error(
            """A hash can only be used as parameter 1 or 2 of an online plotter (type 65):

At <string>:11:

3     				! 2: Nb. of right-axis variables
-0.5   				! 3: Left axis minimum
100        			! 4: Left axis maximum
-1   				! 5: Right axis minimum
#       			! 6: Right axis maximum
^
$nPlotsPerSim		! 7: Number of plots per simulation
12     				! 8: X-axis gridpoints
1     				! 9: Shut off Online w/o removing
-1     				! 10: Logical unit for output file
0     				! 11: Output file units
"""
        ),
    )


class TestOnlinePlotter:
    @_pt.mark.parametrize("testCase", [_pt.param(tc, id=tc.id) for tc in getTestCases()])
    def test(self, testCase: TestCase) -> None:
        result = _parse.parseDdck(testCase.input)
        assert not _res.isError(result)
        tree = _res.value(result)

        visitor = _op.LeftRightVariablesVisitor()

        actualOutput: str | _error.ReplaceTokenError
        try:
            visitor.visit(tree)
            actualOutput = _tokens.replaceTokensWithReplacements(testCase.input, visitor.tokensAndReplacement)
        except _error.ReplaceTokenError as error:
            actualOutput = error

        testCase.assertActualOutputIsAsExpected(actualOutput)
