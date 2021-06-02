# pylint: skip-file
# type: ignore

#!/usr/bin/env python

"""
Class to calculate physical data fo fluids using CoolProp

Author : Daniel Carbonell
Date   : 23-05-2017
ToDo :
"""


# import CoolProp.CoolProp as cool

try:
    from CoolProp.CoolProp import PropsSI
    from CoolProp.HumidAirProp import HAPropsSI, HAProps_Aux

    newVersion = True
except:
    from CoolProp.CoolProp import Props
    from CoolProp.HumidAirProp import HAProps, HAProps_Aux

    newVersion = False
import sys


class PhysProp:
    def __init__(self):

        self.name = ""
        self.concentration = 0.0  # in 100%

        if newVersion == True:
            self.pressure = 101325  # Pa => 1 atm
        else:
            self.pressure = 101.325  # Pa => 1 atm

        self.nameIsSet = False
        self.concentrationIsSet = False
        self.useConstantProperties = False

        self.constantCp = 0.0
        self.constantRho = 0.0
        self.constantMu = 0.0
        self.constantLambda = 0.0

        self.constantCpIsSet = False
        self.constantRhoIsSet = False
        self.constantLambdaIsSet = False
        self.constantMuIsSet = False

    def setUseConstantProperties(self, use):

        self.useConstantProperties = use

    def setConstantCp(self, cp):
        self.constantCpIsSet = True
        self.constantCp = cp

    def setConstantRho(self, rho):

        self.constantRhoIsSet = True
        self.constantRho = rho

    def setConstantMu(self, mu):

        self.constantMuIsSet = True
        self.constantMu = mu

    def setConstantLambda(self, _lambda):

        self.constantLambdaIsSet = True
        self.constantLambda = _lambda

    def setName(self, _name):

        self.nameIsSet = True
        self.name = _name

    # conc in %
    def setConcentration(self, conc):

        self.concentrationIsSet = True

        self.concentration = conc
        if self.nameIsSet == False:
            print("FATAL ERROR. First setName and then concentration")
            sys.exit(0)

        #        'EG-20%'
        if self.name[-1] == "%":
            #            self.name=self.name[0:-6]+'%.2f%%' % self.concentration
            #            myName = self.name[0:3]+'%.2f%%' % self.concentration
            myName = self.name[0:3] + "-%.0f%%" % self.concentration

            print("name [0:3]:%s name:%s concen:%f myName:%s" % (self.name[0:3], self.name, self.concentration, myName))
            self.name = myName

        else:
            #            self.name = "INCOMP::%s-%.2f%%" % (self.name,self.concentration)
            self.name = "INCOMP::%s-%.0f%%" % (self.name, self.concentration)

    #        raise ValueError("setConcentration name:%s"%self.name)

    # T in oC Rho out in      kg/m3
    def getRho(self, T):

        if self.useConstantProperties:
            if self.constantRhoIsSet == False:
                print("FATAL ERROR setConstantRho must be defined if constant properties are used")
                sys.exit(0)
            else:
                return self.constantRho
        else:
            if newVersion == True:
                #                print "NEW VERSION"
                #                print self.pressure,self.name
                return PropsSI("D", "T", T + 273.15, "P", self.pressure, self.name)
            else:
                #                print "OLD VERSION"
                #                print T,self.pressure,self.name
                rho = Props("D", "T", T + 273.15, "P", self.pressure, self.name)
                #                print rho
                return rho

    # T in oC Cp out in      J/kg/k
    def getCp(self, T):

        if self.useConstantProperties:
            if self.constantCpIsSet == False:
                print("FATAL ERROR setConstartCp must be defined if constant properties are used")
                sys.exit(0)
            else:
                return self.constantCp
        else:
            try:
                if newVersion == True:
                    return PropsSI("C", "T", T + 273.15, "P", self.pressure, self.name)
                else:
                    return Props("C", "T", T + 273.15, "P", self.pressure, self.name) * 1000.0

            except:
                if newVersion == True:
                    return PropsSI("C", "T", T + 0.01 + 273.15, "P", self.pressure, self.name)
                else:
                    try:
                        return Props("C", "T", T + 273.15, "P", self.pressure, self.name) * 1000.0
                    except:
                        return Props("C", "T", T + 0.01 + 273.15, "P", self.pressure, self.name) * 1000.0

    # T in oC Mu (dynamic viscosity) out in    Pa*s
    def getMu(self, T):

        if self.useConstantProperties:
            if self.constantMuIsSet == False:
                print("FATAL ERROR setConstartMu must be defined if constant properties are used")
                sys.exit(0)
            else:
                return self.constantMu
        else:
            if newVersion == True:
                return PropsSI("V", "T", T + 273.15, "P", self.pressure, self.name)
            else:
                return Props("V", "T", T + 273.15, "P", self.pressure, self.name)

    # T in oC Lambda (thermal conductivity) iut in W/k

    def getLambda(self, T):

        if self.useConstantProperties:
            if self.constantMuIsSet == False:
                print("FATAL ERROR setConstartMu must be defined if constant properties are used")
                sys.exit(0)
            else:
                return self.constantMu
        else:
            try:
                if newVersion == True:
                    return PropsSI("L", "T", T + 273.15, "P", self.pressure, self.name)
                else:
                    return Props("L", "T", T + 273.15, "P", self.pressure, self.name)
            except:
                print("Error in Lambda T:%f" % T)
                if newVersion == True:
                    return PropsSI("L", "T", T + 0.1 + 273.15, "P", self.pressure, self.name) * 1000.0
                else:
                    return Props("L", "T", T + 0.1 + 273.15, "P", self.pressure, self.name) * 1000.0

    def getEnthalpy(self, T):

        if self.useConstantProperties:
            if self.constantEnthalpyIsSet == False:
                print("FATAL ERROR setConstantEnthalpy must be defined if constant properties are used")
                sys.exit(0)
            else:
                return self.constantEnthalpy
        else:
            if newVersion == True:
                return PropsSI("H", "T", T + 273.15, "P", self.pressure, self.name) * 1000.0
            else:
                return Props("H", "T", T + 273.15, "P", self.pressure, self.name) * 1000.0

    #            return (HAPropsSI('H','T',298.15,'P',101325,'R',0.5))

    def getTemperature(self, h):

        if newVersion == True:
            return PropsSI("T", "H", h / 1000.0, "P", self.pressure, self.name) - 273.15
        else:
            return Props("T", "H", h / 1000.0, "P", self.pressure, self.name) - 273.15

    """ Volumetric coefficient of thermal expansion [K^-1] """

    def getBeta(self, T):
        if self.name == "H2O":
            return (0.8 * pow(T, 0.5348) - 1.9114) * 1e-4
        else:
            print("FATAL: ERROR getBeta() is only defined for Water")
            sys.exit(0)

    def getSaturationProperties(self, propertie, valueAtSat):

        # Temperature at saturation from pressure

        if propertie == "T":
            return PropsSI("T", "P", valueAtSat / 1000.0, "Q", 0, self.name) - 273.15  # temperature in K

        # Pressure at saturation from temperature

        elif propertie == "P":
            return 1000.0 * PropsSI("P", "T", valueAtSat + 273.15, "Q", 0, self.name)  # Pressure in KPa = Pa

        # Enthalpy at saturation from temperature

        elif propertie == "HLiquidFromT":
            return 1000.0 * PropsSI("H", "T", valueAtSat + 273.15, "Q", 0, self.name)  # Temperature in K
        elif propertie == "HLiquidFromP":
            return 1000.0 * PropsSI("H", "P", valueAtSat / 1000.0, "Q", 0, self.name)  # pressure in kPa
        elif propertie == "HVaporFromT":
            return 1000.0 * PropsSI("H", "T", valueAtSat + 273.15, "Q", 1, self.name)  # Temperature in K
        elif propertie == "HVaporFromP":
            return 1000.0 * PropsSI("H", "P", valueAtSat / 1000.0, "Q", 1, self.name)  # pressure in kPa

        # Density at saturation from temperature

        elif propertie == "DLiquidFromT":
            return PropsSI("D", "T", valueAtSat + 273.15, "Q", 0, self.name)  # Temperature in K
        elif propertie == "DLiquidFromP":
            return PropsSI("D", "P", valueAtSat / 1000.0, "Q", 0, self.name)  # pressure in kPa
        elif propertie == "DVaporFromT":
            return PropsSI("D", "T", valueAtSat + 273.15, "Q", 1, self.name)  # Temperature in K
        elif propertie == "DVaporFromP":
            return PropsSI("D", "P", valueAtSat / 1000.0, "Q", 1, self.name)  # pressure in kPa
        else:
            raise ValueError("getSaturationPropertiesNotImplemented")


# Alternatively, Props can be called in the form:
#
# Props(OutputName,InputName1,InputProp1,InputName2,InputProp2,Fluid) --> float
# where Fluid is a string with a valid CoolProp fluid name. The value OutputName is either a single-character or a string alias. This list shows the possible values
#
# OutputName	Description
# Q	Quality [-]  0 liquid, 1 vapor
# T	Temperature [K]
# P	Pressure [kPa]
# D	Density [kg/m3]
# C0	Ideal-gas specific heat at constant pressure [kJ/kg]
# C	Specific heat at constant pressure [kJ/kg]
# O	Specific heat at constant volume [kJ/kg]
# U	Internal energy [kJ/kg]
# H	Enthalpy [kJ/kg]
# S	Entropy [kJ/kg/K]
# A	Speed of sound [m/s]
# G	Gibbs function [kJ/kg]
# V	Dynamic viscosity [Pa-s]
# L	Thermal conductivity [kW/m/K]
# I or SurfaceTension	Surface Tension [N/m]
# w or accentric	Accentric Factor [-]


# Props(Fluid,PropName) --> float
# Where Fluid is a string with a valid CoolProp fluid name, and PropName is one of the following strings:
#
# Tcrit	Critical temperature [K]
# Treduce	Reducing temperature [K]
# pcrit	Critical pressure [kPa]
# rhocrit	Critical density [kg/m3]
# rhoreduce	Reducing density [kg/m3]
# molemass	Molecular mass [kg/kmol]
# Ttriple	Triple-point temperature [K]
# Tmin	Minimum temperature [K]
# ptriple	Triple-point pressure [kPa]
# accentric	Accentric factor [-]
# GWP100	Global Warming Potential 100 yr
# ODP	Ozone Depletion Potential

# import the things you need
# In [1]: from CoolProp.HumidAirProp import HAPropsSI
#
##Enthalpy (J per kg dry air) as a function of temperature, pressure,
##    and relative humidity at dry bulb temperature T of 25C, pressure
##    P of one atmosphere, relative humidity R of 50%
# In [2]: h = HAPropsSI('H','T',298.15,'P',101325,'R',0.5); print h
# 50423.4503925
#
##Temperature of saturated air at the previous enthalpy
# In [3]: T = HAPropsSI('T','P',101325,'H',h,'R',1.0); print T
# 290.962089195
#
##Temperature of saturated air - order of inputs doesn't matter
# In [4]: T = HAPropsSI('T','H',h,'R',1.0,'P',101325); print T
# 290.962089195


class HumidAirProp:
    def __init__(self):

        self.humidityRatio = 0.0  # kg water / kg dry air [0-1]
        self.vDryAir = 0.0  # m3 Water / kg dry air
        self.vMoistAir = 0.0  # m3 water / kg moist air
        self.hDryAir = 0.0  # J/kg dry air
        self.hMoistAir = 0.0  # J/kg moist air

    #
    def getEnthalpy(self, temp, humidityRatio):

        return HAProps("H", "T", temp + 273.15, "P", 101325, "R", humidityRatio)  # J/kg dry air

    def getSaturatedProperties(self, name, h):
        #
        if name == "T":
            return HAProps("T", "P", 101325, "H", h, "R", 1.0) - 273.15
        else:
            raise ValueError("name:%s not found" % name)
