import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.ddck.replaceTokens.placeholders as _rtph
import pytrnsys.ddck.replaceTokens.withoutPlaceholders as _rtwph
import pytrnsys.utils.result as _res

_DDCK = """\
EQUATIONS 3
PacOut = 0.95*@pelsign(Dc)*@pel(Dc)
@pel(Ac) = -@pelsign(Ac)*PacOut
PacCheck = @pel(Ac)
"""

_EXPECTED = """\
EQUATIONS 3
inv1PacOut = 0.95*(1)*PelPv1_inv1
PelInv1_node1 = -(-1)*inv1PacOut
inv1PacCheck = PelInv1_node1
"""


def testElectricalPlaceholdersAreReplacedByTheNamesOfTheElectricalConnections() -> None:
    computedNamesByPort = {
        "Dc": {"@pel": "PelPv1_inv1", "@pelsign": "(1)"},
        "Ac": {"@pel": "PelInv1_node1", "@pelsign": "(-1)"},
    }

    result = _rtph.replaceTokensInString(_DDCK, "inv1", computedNamesByPort, _dv.DefaultVisibility.LOCAL)

    assert not _res.isError(result)
    assert _res.value(result) == _EXPECTED


def testAssignmentToElectricalPowerUsesDefaultOrIsRemovedWithoutPlaceholders() -> None:
    ddck = """\
EQUATIONS 2
@pel(Ac, PacDefault) = 3
@pel(Dc) = 4
"""
    result = _rtwph.replaceTokensWithDefaultsInString(ddck, "inv1", _dv.DefaultVisibility.LOCAL)

    assert not _res.isError(result)
    content = _res.value(result)
    assert "PacDefault = 3" in content
    assert "! Assignment to electrical power at `Dc` removed by pytrnsys" in content
