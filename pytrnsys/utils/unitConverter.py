

import typing as _typ


# BEGIN-NOSCAN
# this function is ignored when a function exists.
def __getattr__(name: str):
    # END-NOSCAN
    if name == "UnitConverter":
        raise ValueError
    return getattr(UnitConverter(), name)


class UnitConverter:
    def __init__(self):
        self.unit: str = ""
        self._conversionFactor: _typ.Optional[float] = None
        self._method: _typ.Optional[str] = None
        self._factors: dict = {
            "kPaToBar": 1.0 / 101.3,
            "PaToBar": 1.0 / 101300,
            "BarToPa": 101300.0,
            "PaToMca": 1.0 / 9806.65,
            "PaToMmca": 1.0 / 9.80665,
            "BarToMmca": 101300.0 / 9.80665,
            "PaTokgCm2": 1.0 / 98066.52,
            "kgCm2ToPa": 98066.52,
            "PsiToPa": 6894.757293178,
            "PaToPsi": 0.000145038,
            "JTokWh": 1e-6 / 3.6,
            "kWhToJ": 3.6 * 1e6,
            "kWhToMJ": 3.6,
            "JToMWh": 1e-9 / 3.6,
            "kJToMWh": 1e-6 / 3.6,
            "MJTokWh": 1.0 / 3.6,
            "kJhToW": 1.0 / 3.6,
            "WTokJh": 3.6,
        }
        self._conversionMethods: dict = {
            "getkPaToBar": "kPaToBar",
            "getPaToBar": "PaToBar",
            "getBarToPa": "BarToPa",
            "getPaToMca": "PaToMca",
            "getPaToMmca": "PaToMmca",
            "getBarToMmca": "BarToMmca",
            "getPaTokgCm2": "PaTokgCm2",
            "getkgCm2ToPa": "kgCm2ToPa",
            "getPsiToPa": "PsiToPa",
            "getPaToPsi": "PaToPsi",
            "getJTokWh": "JTokWh",
            "getkWhToJ": "kWhToJ",
            "getkWhToMJ": "kWhToMJ",
            "getJToMWh": "JToMWh",
            "getkJToMWh": "kJToMWh",
            "getMJTokWh": "MJTokWh",
            "getkJhToW": "kJhToW",
            "getWTokJh": "WTokJh",
            "getKJhToW": "kJhToW",
            "getWToKJh": "WTokJh",
        }

    def getAvailableConversions(self) -> list:
        return list(self._factors.keys())

    def setConversionFactor(self, name: str):
        self._conversionFactor = self.getConversionFactor(name)

    def convert(self, value: float, desiredConversionFactor=None) -> float:
        if desiredConversionFactor:
            factor = self.getConversionFactor(desiredConversionFactor)
        elif self._conversionFactor:
            factor = self._conversionFactor
        else:
            raise ValueError(f"Conversion factor not given. Either use UnitConverter.setConversionFactor, "
                             f"or provide a desiredConversionFactor.")

        return factor * value

    def getConversionFactor(self, conversionType: str) -> float:
        if conversionType in self.getAvailableConversions():
            return self._factors[conversionType]

        raise ValueError(f"Unkown conversion type: {conversionType}")

    def __getattr__(self, item: str):
        self._method = self._conversionMethods[item]
        return self._helperFunction

    def _helperFunction(self) -> float:
        return self.getConversionFactor(self._method)


def dummyFunction():
    # Used to test the __getattr__ implementation
    pass

#    /* Power */
#
#    inline double BtuHToW() const { return 0.29307107;};
#    inline double WToBtuH() const { return 3.412141635;};
#
#    inline double WToTon() const { return 0.000284345;};
#    inline double TonToW() const { return 3516.854525;};
#
#    inline double kCalHToW() const { return 1.162222222;};
#    inline double WTokCalH() const { return  1./1.162222222;};
#
#    /* Space */
#
#    inline double inToM() const { return 0.0254;};
#    inline double ftToM() const { return 0.3048;};
#
#    /* Mass Flow rate */
#
#    inline double GpmToM3s() const  { return 0.00006309;};
#    inline double m3sToLh() const   { return 3.6e6;     };
#    inline double lMinToM3s() const { return 1.e-4/6.;  };
#    inline double lHToM3s() const   { return 1./3.6e6;    };
#
#    /* volume */
#
#    inline double galToM3() const {return 0.003785412;};
#    inline double m3ToGal() const {return 264.172052358;};
#
#    /* temperature */
#
#    inline double FToC(double tF) const {return (tF-32.)/1.8;};
#    inline double CToF(double tC)  const {return (tC*1.8+32.);};
