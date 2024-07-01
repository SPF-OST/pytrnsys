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
        _res.Error('Explicitly local variables are only allowed if the default visibility is "global".'),
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
        _res.Error('Explicitly global variables are only allowed if the default visibility is "local".'),
    )


class TestDefaultVisibility:
    @_pt.mark.parametrize("testCase", [_pt.param(tc, id=tc.id) for tc in getTestCases()])
    def testReplaceWithPlaceHolders(self, testCase: TestCase) -> None:
        result = _placeholders.replaceTokensInString(
            testCase.equationsBlock, testCase.componentName, {}, testCase.defaultVisibility
        )

        assert result == testCase.expectedResult

    @_pt.mark.parametrize("testCase", [_pt.param(tc, id=tc.id) for tc in getTestCases()])
    def testReplaceWithDefaults(self, testCase: TestCase) -> None:
        result = _defaults.replaceTokensWithDefaultsInString(
            testCase.equationsBlock, testCase.componentName, testCase.defaultVisibility
        )

        assert result == testCase.expectedResult
