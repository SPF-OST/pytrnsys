import collections.abc as _cabc
import dataclasses as _dc

import pytest as _pt

import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.ddck.replaceTokens.placeholders as _placeholders
import pytrnsys.ddck.replaceTokens.withoutPlaceholders as _defaults
import pytrnsys.utils.result as _res


@_dc.dataclass
class TestCase:
    id: str
    componentName: str
    defaultVisibility: _dv.DefaultVisibility
    equationsBlock: str
    expectedResult: _res.Result[str]


def getTestCases() -> _cabc.Iterable[TestCase]:
    yield TestCase(
        "global",
        "Coll",
        _dv.DefaultVisibility.GLOBAL,
        """\
EQUATIONS 2
:A = 5 ! m^2
:freezeDanger = LT(Tamb, 1)
""",
        """\
EQUATIONS 2
CollA = 5 ! m^2
CollfreezeDanger = LT(Tamb, 1)
""",
    )

    yield TestCase(
        "doubleLocal",
        "Coll",
        _dv.DefaultVisibility.LOCAL,
        """\
EQUATIONS 2
:A = 5 ! m^2
:freezeDanger = LT(Tamb, 1)
""",
        _res.Error(
            """\
Explicitly local variables are only allowed if the default visibility is "global":

At line 2 column 1:

:A = 5 ! m^2
^^
:freezeDanger = LT(Tamb, 1)
"""
        ),
    )

    yield TestCase(
        "doubleLocalLong",
        "Coll",
        _dv.DefaultVisibility.LOCAL,
        """\
***********************************
** inputs from hydraulic solver
***********************************

EQUATIONS 2
TCollIn = @temp(In)
MfrColl = @mfr(In)

***********************************
** outputs to hydraulic solver
***********************************

EQUATIONS 2
TCollOut = [28,1]
@temp(Out) = TCollOut


***********************************
** outputs to other ddck
***********************************

******************************************************************************************
** outputs to energy balance in kWh and ABSOLUTE value
** Following this naming standard : qSysIn_name, qSysOut_name, elSysIn_name, elSysOut_name
******************************************************************************************

EQUATIONS 1
@energy(in, heat, Collector) =  PColl_kW

***********************************
** Dependencies with other ddck
***********************************

EQUATIONS 1
:pumpColOn = puColOn

CONSTANTS 2
C_tilt = slopeSurfUser_1  ! @dependencyDdck Collector tilt angle / slope [°]
C_azim = aziSurfUSer_1    ! @dependencyDdck Collector azimuth  (0:s, 90:w, 270: e) [°]
""",
        _res.Error(
            """\
Explicitly local variables are only allowed if the default visibility is "global":

At line 35 column 1:

** Dependencies with other ddck
***********************************

EQUATIONS 1
:pumpColOn = puColOn
^^^^^^^^^^

CONSTANTS 2
C_tilt = slopeSurfUser_1  ! @dependencyDdck Collector tilt angle / slope [°]
C_azim = aziSurfUSer_1    ! @dependencyDdck Collector azimuth  (0:s, 90:w, 270: e) [°]
"""
        ),
    )

    yield TestCase(
        "local",
        "Coll",
        _dv.DefaultVisibility.LOCAL,
        """\
EQUATIONS 2
A = 5 ! m^2
freezeDanger = LT($Tamb, 1)
""",
        """\
EQUATIONS 2
CollA = 5 ! m^2
CollfreezeDanger = LT(Tamb, 1)
""",
    )

    yield TestCase(
        "doubleGlobal",
        "Coll",
        _dv.DefaultVisibility.GLOBAL,
        """\
EQUATIONS 2
A = 5 ! m^2
freezeDanger = LT($Tamb, 1)
""",
        _res.Error(
            """\
Explicitly global variables are only allowed if the default visibility is "local":

At line 3 column 19:

A = 5 ! m^2
freezeDanger = LT($Tamb, 1)
                  ^^^^^
"""
        ),
    )


class TestDefaultVisibility:
    @_pt.mark.parametrize("testCase", [_pt.param(tc, id=tc.id) for tc in getTestCases()])
    def testReplaceWithPlaceHolders(self, testCase: TestCase) -> None:
        result = _placeholders.replaceTokensInString(
            testCase.equationsBlock, testCase.componentName, {}, testCase.defaultVisibility
        )

        if _res.isError(result):
            print(_res.error(result).message)

        assert result == testCase.expectedResult

    @_pt.mark.parametrize("testCase", [_pt.param(tc, id=tc.id) for tc in getTestCases()])
    def testReplaceWithDefaults(self, testCase: TestCase) -> None:
        result = _defaults.replaceTokensWithDefaultsInString(
            testCase.equationsBlock, testCase.componentName, testCase.defaultVisibility
        )

        if _res.isError(result):
            print(_res.error(result).message)

        assert result == testCase.expectedResult
