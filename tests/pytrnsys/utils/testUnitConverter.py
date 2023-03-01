import pytest as _pt

import pytrnsys.utils.unitConverter as _uc

_TOLERANCE = 1e-9
_CONVERSION_METHODS = [
    "getkPaToBar",
    "getPaToBar",
    "getBarToPa",
    "getPaToMca",
    "getPaToMmca",
    "getBarToMmca",
    "getPaTokgCm2",
    "getkgCm2ToPa",
    "getPsiToPa",
    "getPaToPsi",
    "getJTokWh",
    "getkWhToJ",
    "getkWhToMJ",
    "getJToMWh",
    "getkJToMWh",
    "getMJTokWh",
    "getkJhToW",
    "getWTokJh",
    "getKJhToW",
    "getWToKJh",
]

_CONVERSION_FACTORS = [
    0.009871668311944718,
    9.87166831194472e-06,
    101300.0,
    0.00010197162129779283,
    0.10197162129779283,
    10329.725237466413,
    1.0197160050137396e-05,
    98066.52,
    6894.757293178,
    0.000145038,
    2.7777777777777776e-07,
    3600000.0,
    3.6,
    2.7777777777777777e-10,
    2.7777777777777776e-07,
    0.2777777777777778,
    0.2777777777777778,
    3.6,
    0.2777777777777778,
    3.6,
]
_CONVERSION_NAMES = [
    "kPaToBar",
    "PaToBar",
    "BarToPa",
    "PaToMca",
    "PaToMmca",
    "BarToMmca",
    "PaTokgCm2",
    "kgCm2ToPa",
    "PsiToPa",
    "PaToPsi",
    "JTokWh",
    "kWhToJ",
    "kWhToMJ",
    "JToMWh",
    "kJToMWh",
    "MJTokWh",
    "kJhToW",
    "WTokJh",
]

_METHOD_CASES = list(zip(_CONVERSION_METHODS, _CONVERSION_FACTORS))
_CONVERSION_NAME_CASES = list(zip(_CONVERSION_NAMES, _CONVERSION_FACTORS))


def _getRelativeError(value, value2):
    maxValue = abs(max(value, value2))
    if maxValue != 0.0:
        return abs(value - value2) / maxValue
    return 0.0


def testGetRelativeErrorZeros():
    assert _getRelativeError(0, 0) == 0
    assert _getRelativeError(0.0, 0) == 0
    assert _getRelativeError(0.0, 0.0) == 0


class TestUnitConverter:
    def setup(self):
        self.converter = _uc.UnitConverter()  # pylint: disable=attribute-defined-outside-init

    def _testHelper(self, method, value):
        conversionRate = getattr(_uc, method)()
        conversionRate2 = getattr(self.converter, method)()
        assert _getRelativeError(conversionRate, value) < _TOLERANCE
        assert conversionRate == conversionRate2

    @_pt.mark.parametrize("method, factor", _METHOD_CASES)
    def testGetConversionUsingIndividualMethods(self, method, factor):
        self._testHelper(method, factor)

    @_pt.mark.parametrize("name, factor", _CONVERSION_NAME_CASES)
    def testGetConversionFactor(self, name, factor):
        result = self.converter.getConversionFactor(name)

    def testGetConversionFactorRaises(self):
        with _pt.raises(ValueError):
            self.converter.getConversionFactor("test")

    def testGetAvailableConversions(self):
        names = self.converter.getAvailableConversions()
        assert names == _CONVERSION_NAMES

    @_pt.mark.parametrize("name, factor", _CONVERSION_NAME_CASES)
    def testConversionsUsingConstantConverter(self, name, factor):
        self.converter.setConversionFactor(name)
        assert self.converter.convert(1) == factor

    @_pt.mark.parametrize("name, factor", _CONVERSION_NAME_CASES)
    def testConversionsOverridingAssignedFactor(self, name, factor):
        self.converter.setConversionFactor("kPaToBar")
        assert self.converter.convert(1, desiredConversionFactor=name) == factor

    @_pt.mark.parametrize("name, factor", _CONVERSION_NAME_CASES)
    def testConversionsWithoutAssigningFactorBeforehand(self, name, factor):
        assert self.converter.convert(1, desiredConversionFactor=name) == factor
