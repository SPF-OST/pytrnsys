# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
File to do basic conversion units
Author : Daniel Carbonell
Date   : 2014
ToDo :
"""


def getkPaToBar():
    return 1.0 / 101.3


def getPaToBar():
    return 1.0 / 101300


def getBarToPa():
    return 101300.0


def getPaToMmca():
    return 1.0 / 9.80665


def getPaToMca():
    return 1.0 / 9806.65


def getBarToMmca():
    return 101300.0 / 9.80665


def getPaTokgCm2():
    return 1.0 / 98066.52


def getkgCm2ToPa():
    return 98066.52


def getPsiToPa():
    return 6894.757293178


def getPaToPsi():
    return 0.000145038


# Energy


def getJTokWh():
    return 1e-6 / 3.6


def getkWhToJ():
    return 3.6 * 1e6


def getkWhToMJ():
    return 3.6


def getJToMWh():
    return 1e-9 / 3.6


def getkJToMWh():
    return 1e-6 / 3.6


def getMJTokWh():
    return 1.0 / 3.6


def getKJhToW():
    return 1.0 / 3.6


def getWToKJh():
    return 3.6


class UnitConverter:
    def __init__(self):

        unit = ""

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

    def getJToMWh(self):
        return 1e-9 / 3.6

    def getkJToMWh(self):
        return 1e-6 / 3.6

    def getMJTokWh(self):
        return 1.0 / 3.6

    def getKJhToW(self):
        return 1.0 / 3.6

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
