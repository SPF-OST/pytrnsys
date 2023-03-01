# pylint: skip-file
# type: ignore

# !/usr/bin/python

"""
File to do basic conversion units
Author : Daniel Carbonell
Date   : 2014
ToDo : remove skipfile
"""


def getkPaToBar():
    return _converter.getkPaToBar()


def getPaToBar():
    return _converter.getPaToBar()


def getBarToPa():
    return _converter.getBarToPa()


def getPaToMmca():
    return _converter.getPaToMmca()


def getPaToMca():
    return _converter.getPaToMca()


def getBarToMmca():
    return _converter.getBarToMmca()


def getPaTokgCm2():
    return _converter.getPaTokgCm2()


def getkgCm2ToPa():
    return _converter.getkgCm2ToPa()


def getPsiToPa():
    return _converter.getPsiToPa()


def getPaToPsi():
    return _converter.getPaToPsi()


# Energy


def getJTokWh():
    return _converter.getJTokWh()


def getkWhToJ():
    return _converter.getkWhToJ()


def getkWhToMJ():
    return _converter.getkWhToMJ()


def getJToMWh():
    return _converter.getJToMWh()


def getkJToMWh():
    return _converter.getkJToMWh()


def getMJTokWh():
    return _converter.getMJTokWh()


def getKJhToW():
    return _converter.getKJhToW()


def getkJhToW():
    return _converter.getkJhToW()


def getWToKJh():
    return _converter.getWTokJh()


def getWTokJh():
    return _converter.getWTokJh()


# todo: this is a UnitConversionHolder
class UnitConverter:
    # todo: add convert method
    def __init__(self):
        self.unit = ""
        self._conversionFactor = None
        self._factors = {
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

    def getConversionFactor(self, name):
        return self._factors[name]

    def setConversionFactor(self, name):
        self._conversionFactor = self.getConversionFactor(name)

    def convert(self, value, desiredConversionFactor=None):
        # todo: add error handling
        if not desiredConversionFactor:
            factor = self._conversionFactor
        else:
            factor = self.getConversionFactor(desiredConversionFactor)
        return factor * value

    def getAvailableConversions(self):
        return list(self._factors.keys())

    # PRESSURE

    def getkPaToBar(self):
        return 1.0 / 101.3

    def getPaToBar(self):
        return 1.0 / 101300

    def getBarToPa(self):
        return 101300.0

    def getPaToMmca(self):
        return 1.0 / 9.80665

    def getPaToMca(self):
        return 1.0 / 9806.65

    def getBarToMmca(self):
        return 101300.0 / 9.80665

    def getPaTokgCm2(self):
        return 1.0 / 98066.52

    def getkgCm2ToPa(self):
        return 98066.52

    def getPsiToPa(self):
        return 6894.757293178

    def getPaToPsi(self):
        return 0.000145038

    # Energy

    def getJTokWh(self):
        return 1e-6 / 3.6

    def getkWhToJ(self):
        return 3.6 * 1e6

    def getkWhToMJ(self):
        return 3.6

    def getJToMWh(self):
        return 1e-9 / 3.6

    def getkJToMWh(self):
        return 1e-6 / 3.6

    def getMJTokWh(self):
        return 1.0 / 3.6

    def getkJhToW(self):
        return 1.0 / 3.6

    def getKJhToW(self):
        return 1.0 / 3.6

    def getWTokJh(self):
        return 3.6

    def getWToKJh(self):
        return 3.6


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

_converter = UnitConverter()
