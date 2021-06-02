# pylint: skip-file
# type: ignore

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Generic functionality

Author : Daniel Carbonell
Date   : 2015
ToDo :
"""

import numpy as num
import getpass
import math
import time


def filterPath(path):

    #    print "filterPath :%s"%path
    pathChanged = path.replace("\\", "/")
    #    print "filterPath changed :%s"%pathChanged
    return pathChanged


# array numpy array becasue of resize function
def isInteger(n):
    """Return True if argument is a whole number, False if argument has a fractional part.

    Note that for values very close to an integer, this test breaks. During
    superficial testing the closest value to zero that evaluated correctly
    was 9.88131291682e-324. When dividing this number by 10, Python 2.7.1 evaluated
    the result to zero"""

    if n % 2 == 0 or (n + 1) % 2 == 0:
        return True
    return False


def getNameCity(nCity):

    if nCity == 7:
        return "Zurich"
    elif nCity == 6:
        return "Locarno"
    else:
        return "Unknown"


def isWhole(x):

    if x % 1 == 0:
        return True
    else:
        return False


def addYearlyValue(array, yearlyFactor=1.0):

    if len(array) == 13:
        print(
            "addYearlyValue found an array of 13 lenght. So I assume that it was already added and I return the same value"
        )
        return array

    if len(array) != 12:
        print(array)
        raise ValueError("Error. You are trying to add a yearly value to a non monthly array")

    sumQ = sum(array)
    myArray = array.copy()
    myArray.resize(13, refcheck=False)

    if yearlyFactor == 0:
        yearlyFactor = 1
        print("yearlyFactor should be different from 0, 1 is assumed")

    #        raise ValueError("yearlyFactor should be different from 0")

    myArray[12] = sumQ / yearlyFactor

    return myArray


def getNameFromUserName():

    userName = getpass.getuser()

    if userName == "dcarbone":
        return "Daniel Carbonell"
    elif userName == "mgranzot":
        return "Martin Granzotto"
    elif userName == "dphilipp":
        return "Daniel Philippen"
    else:
        return userName


def getEmailFromUserName():

    userName = getpass.getuser()

    if userName == "dcarbone":
        return "dani.carbonell@spf.ch"
    elif userName == "mgranzot":
        return "martin.granzotto@spf.ch"
    elif userName == "dphilipp":
        return "daniel.philippen@spf.ch"
    else:
        return userName


def isMonthName(_month):

    if _month == "January":
        return True
    elif _month == "February":
        return True
    elif _month == "March":
        return True
    elif _month == "April":
        return True
    elif _month == "May":
        return True
    elif _month == "June":
        return True
    elif _month == "July":
        return True
    elif _month == "August":
        return True
    elif _month == "September":
        return True
    elif _month == "October":
        return True
    elif _month == "November":
        return True
    elif _month == "December":
        return True
    else:
        return False


def getMonthNameIndex(_month):

    if _month == "January":
        return 0
    elif _month == "February":
        return 1
    elif _month == "March":
        return 2
    elif _month == "April":
        return 3
    elif _month == "May":
        return 4
    elif _month == "June":
        return 5
    elif _month == "July":
        return 6
    elif _month == "August":
        return 7
    elif _month == "September":
        return 8
    elif _month == "October":
        return 9
    elif _month == "November":
        return 10
    elif _month == "December":
        return 11
    else:
        return -1


def getMonthKey(i, language="en"):
    if language == "en":
        if i == 1:
            return "Jan"
        elif i == 2:
            return "Feb"
        elif i == 3:
            return "Mar"
        elif i == 4:
            return "Apr"
        elif i == 5:
            return "May"
        elif i == 6:
            return "Jun"
        elif i == 7:
            return "Jul"
        elif i == 8:
            return "Aug"
        elif i == 9:
            return "Sep"
        elif i == 10:
            return "Oct"
        elif i == 11:
            return "Nov"
        elif i == 12:
            return "Dec"
    elif language == "de":
        if i == 1:
            return "Jan"
        elif i == 2:
            return "Feb"
        elif i == 3:
            return "Mär"
        elif i == 4:
            return "Apr"
        elif i == 5:
            return "Mai"
        elif i == 6:
            return "Jun"
        elif i == 7:
            return "Jul"
        elif i == 8:
            return "Aug"
        elif i == 9:
            return "Sep"
        elif i == 10:
            return "Okt"
        elif i == 11:
            return "Nov"
        elif i == 12:
            return "Dez"


def getShortMonthyNameArray(monthVec):

    monthShort = []

    for i in range(len(monthVec)):
        monthShort.append(getShortMonthNames(monthVec[i]))

    return monthShort


def getShortMonthNames(month):

    _month = month.replace(" ", "")

    if _month == "January":
        return "Jan"
    elif _month == "February":
        return "Feb"
    elif _month == "March":
        return "Mar"
    elif _month == "April":
        return "Apr"
    elif _month == "May":
        return "May"
    elif _month == "June":
        return "Jun"
    elif _month == "July":
        return "Jul"
    elif _month == "August":
        return "Aug"
    elif _month == "September":
        return "Sep"
    elif _month == "October":
        return "Oct"
    elif _month == "November":
        return "Nov"
    elif _month == "December":
        return "Dec"
    else:
        return -1


# startMonth [1-12]
def reorganizeMonthlyFile(var, startMonth):

    varNew = num.zeros(num.size(var))  # it could be 13 for yearly value !!

    if startMonth > 12:
        raise ValueError("reorganizeMonthlyFile startMonth:%d [1-12]" % startMonth)

    j = startMonth - 1

    for i in range(12):

        if j == 12:
            j = 0

        #        print "i:%d j:%d"%(i,j)

        varNew[i] = var[j]

        #        print "i:%d varNew:%f jOld:%d varOld:%f"%(i,varNew[i],j,var[j])

        j = j + 1

    return varNew


def getMonthNameSequence(startMonth, language="en"):

    monthSeq = []

    j = startMonth  # 1-12
    for i in range(12):
        if j == 13:
            j = 1
        monthSeq.append(getMonthKey(j, language=language))
        j = j + 1

    return monthSeq


def getMonthLongName(i, language="en"):
    if language == "en":
        if i == 1:
            return "January"
        elif i == 2:
            return "February"
        elif i == 3:
            return "March"
        elif i == 4:
            return "April"
        elif i == 5:
            return "May"
        elif i == 6:
            return "June"
        elif i == 7:
            return "July"
        elif i == 8:
            return "August"
        elif i == 9:
            return "September"
        elif i == 10:
            return "October"
        elif i == 11:
            return "November"
        elif i == 12:
            return "December"
    elif language == "de":
        if i == 1:
            return "Januar"
        elif i == 2:
            return "Februar"
        elif i == 3:
            return "März"
        elif i == 4:
            return "April"
        elif i == 5:
            return "Mai"
        elif i == 6:
            return "Juni"
        elif i == 7:
            return "Juli"
        elif i == 8:
            return "August"
        elif i == 9:
            return "September"
        elif i == 10:
            return "Oktober"
        elif i == 11:
            return "November"
        elif i == 12:
            return "Dezember"


def getNumberOfAccumulatedDays(month, day):

    numberOfAccumulatedDays = 0

    for i in range(1, 13, 1):
        #        print "getNumberOfAccumulatedDays i:%d month:%d" % (i,month)
        if i != month:
            numberOfAccumulatedDays = numberOfAccumulatedDays + getNumberOfDaysOfMonth(i)
        #            print "getNumberOfAccumulatedDays if nDayAcunm:%d nDayMonth:%d"%(numberOfAccumulatedDays,getNumberOfDaysOfMonth(i))
        else:
            numberOfAccumulatedDays = numberOfAccumulatedDays + day
            #            print "getNumberOfAccumulatedDays else nDayAcunm:%d +Day:%d"%(numberOfAccumulatedDays,day)
            break

    return numberOfAccumulatedDays


# month 1-12, day 1-31, hour=0
def getNumberOfAccumulatedHours(month, day, _hour):

    numberOfAccumulatedDays = getNumberOfAccumulatedDays(month, day - 1)

    hour = _hour + numberOfAccumulatedDays * 24

    #    print "numberOfAcumulatedDays :%d month:%d day:%d hour:%d hourAcum:%d "%(numberOfAccumulatedDays,month,day,_hour,hour)

    return hour


def getNumberOfDaysOfMonth(i):

    if i == 1:
        return 31
    elif i == 2:
        return 28
    elif i == 3:
        return 31
    elif i == 4:
        return 30
    elif i == 5:
        return 31
    elif i == 6:
        return 30
    elif i == 7:
        return 31
    elif i == 8:
        return 31
    elif i == 9:
        return 30
    elif i == 10:
        return 31
    elif i == 11:
        return 30
    elif i == 12:
        return 31
    else:
        print("Error.  Index out of range i:%d" % i)


def getHourBeginAndEndForMonth(monthBegin, monthEnd):

    firstHour = getNumberOfAccumulatedHours(monthBegin, 1, 0)
    lastHour = getNumberOfAccumulatedHours(monthEnd + 1, 1, 0)

    return firstHour, lastHour


# WARNING , the day is not well calculated, I think +1 should be added, but carefull when 31 December.


def getIsLeapYear(_year):

    for n in range(20):
        if _year == (1980 + 4 * n):
            return True

    return False


def getDayIndexByHourOfYear(_hour):

    year = 0

    for myYear in range(30, 0, -1):
        if _hour > myYear * 8760.0:
            year = myYear
            break

    hour = _hour - 8760.0 * year

    if hour < 0:
        raise ValueError("getDayIndexByHourOfYear Negative time :%f", hour)

    day = min(int(hour / 24 + 1), 365)

    #    print "hour:%f day:%d"% (hour,day)
    return day


def getNumberOfHoursPerMonth(_month):

    return getNumberOfDaysOfMonth(_month) * 24.0


# from 1 to 12
def getMonthIndexByHourOfYear(_hour):

    year = 0

    for myYear in range(30, 0, -1):
        if _hour > myYear * 8760.0:
            year = myYear
            break

    hour = _hour - 8760.0 * year

    if hour < 0:
        raise ValueError("getMonthIndexByHourOfYear Negative time :%f", hour)

    if hour <= 744:
        day = int(hour) / 24
        month = 1
    elif hour <= 1416:
        day = int(hour - 744) / 24
        month = 2
    elif hour <= 2160:
        day = int(hour - 1416) / 24
        month = 3
    elif hour <= 2880:
        day = int(hour - 2160) / 24
        month = 4
    elif hour <= 3624:
        day = int(hour - 2880) / 24
        month = 5
    elif hour <= 4344:
        day = int(hour - 3624) / 24
        month = 6
    elif hour <= 5088:
        day = int(hour - 4344) / 24
        month = 7
    elif hour <= 5832:
        day = int(hour - 5088) / 24
        month = 8
    elif hour <= 6552:
        day = int(hour - 5832) / 24
        month = 9
    elif hour <= 7296:
        day = int(hour - 6552) / 24
        month = 10
    elif hour <= 8016:
        day = int(hour - 7296) / 24
        month = 11
    elif hour <= 8760:
        day = int(hour - 8016) / 24
        month = 12
    else:
        raise ValueError("getMonthIndexByHourOfYear. Hour above one year hour:%f" % hour)

    return (month, day, year + 1)


def calculateDaylyValuesFromHourly(varHourly):

    varDay = num.zeros(365)

    for i in range(len(varHourly)):
        hour = i + 1
        #        print "hour:%d"%hour
        day = getDayIndexByHourOfYear(hour)
        #        print "day:%d"%day
        day = day - 1

        varDay[day] = varDay[day] + varHourly[i]

    #    try:
    #        for i in range(len(varHourly)):
    #            hour  = i+1
    #            print "hour:%d"%hour
    #            (day,nix,nix) = getDayIndexByHourOfYear(hour)
    #            print "day:%d"%day
    #            day = day-1
    #
    #            varDay[day] = varDay[day] + varHourly[i]
    #    except:
    #        pass

    return varDay


def calculateMonthlyValues(varHourly):

    varMonth = num.zeros(12)

    try:
        for i in range(len(varHourly)):
            hour = i
            (month, nix, nix) = getMonthIndexByHourOfYear(hour)

            month = month - 1

            varMonth[month] = varMonth[month] + varHourly[i]
    except:
        pass

    return varMonth


def calculateMonthlyAverages(varHourly):

    varMonth = num.zeros(12)

    try:
        for i in range(len(varHourly)):
            hour = i
            (month, nix, nix) = getMonthIndexByHourOfYear(hour)

            month = month - 1

            varMonth[month] = varMonth[month] + varHourly[i]
    except:
        pass

    for i in range(12):
        varMonth[i] = varMonth[i] / getNumberOfHoursPerMonth(i + 1)

    return varMonth


"""
From varUserDefined in the form var[timeStepinSeconds] in one year
the values are stored in varMonth as varMonth[0]=sum of Jan, etc..
"""


def calculateMonthlyAveragesFromUserDefinedTimeStep(varUserDefined, timeStepInSeconds, firstHourInYear=0):

    varMonth = num.zeros(12)

    month0 = 0
    count = 1
    for i in range(len(varUserDefined)):

        hour = i * timeStepInSeconds / 3600.0 + firstHourInYear

        (m, nix, nix) = getMonthIndexByHourOfYear(hour)

        month = m - 1

        if i > 0 and month0 != month:
            print(
                "New Month(0-12):%d count=%d month:%f month(avg):%f"
                % (month - 1, count, varMonth[month - 1], varMonth[month - 1] / count)
            )

            varMonth[month - 1] = varMonth[month - 1] / count

            count = 1
        else:
            count = count + 1

        varMonth[month] = varMonth[month] + varUserDefined[i]

        month0 = month

    if month0 == month:
        print(
            "New Last Month(0-12):%d count=%d month:%f month(avg):%f"
            % (month, count, varMonth[month], varMonth[month] / count)
        )
        varMonth[month] = varMonth[month] / count

    return varMonth


"""
From varUserDefined in the form var[timeStepinSeconds] in one year
the values are stored in varMonth as varMonth[0]=sum of Jan, etc..
"""


def calculateMonthlyValuesFromUserDefinedTimeStep(varUserDefined, timeStepInSeconds, firstHourInYear=0):

    varMonth = num.zeros(12)

    for i in range(len(varUserDefined)):

        hour = i * timeStepInSeconds / 3600.0 + firstHourInYear

        (month, day, year) = getMonthIndexByHourOfYear(hour)

        #            print "hour:%f month:%d day:%d year:%d"%(hour,month,day,year)

        month = month - 1

        varMonth[month] = varMonth[month] + varUserDefined[i]

    return varMonth


"""
From varUserDefined in the form var[timeStepinSeconds] in one year
the vector that correspond to the month desired is returned
"""


def getMonthlySliceFromUserDefinedTimeStep(varUserDefined, timeStepInSeconds, monthDesired, firstHourInYear=0):

    indexBegin = None
    indexEnd = None
    monthFound = False

    if monthDesired < 1 or monthDesired > 12:
        print("month:%d out of range[1-12]") % monthDesired
        raise ValueError("month:%d out of range[1-12]" % monthDesired)

    for i in range(len(varUserDefined)):

        hour = i * timeStepInSeconds / 3600 + firstHourInYear

        (month, nix, nix) = getMonthIndexByHourOfYear(hour)

        month = month

        if month == monthDesired:
            monthFound = True
            if indexBegin == None:
                indexBegin = i

        # This needs at leats one time step from next month
        if monthFound == True and month != monthDesired:
            if indexEnd == None:
                indexEnd = i - 1

    if indexEnd == None:
        print("final index not found. Last time step used.")
        indexEnd = i = len(varUserDefined) - 1

    print("month:%d indexBegin:%d indexEnd:%d" % (monthDesired, indexBegin, indexEnd))

    return indexBegin, indexEnd


# def getMonthlyVectorFromUserDefinedTimeStep(varUserDefined,timeStepInSeconds,firstHourInYear=0):
#
#    monthlyVector = num.zeros(12)
#
#    for i in range(12):
#         monthlySlice = getMonthlySliceFromUserDefinedTimeStep(varUserDefined,timeStepInSeconds,i+1,firstHourInYear)
#         monthlyVector[i] = get
#
#    return monthlyVector


def calculateMonthlyValuesFromUserDefinedTimeStep2(varUserDefined, timeStepInSeconds, firstHourInYear=0):

    jan = []
    feb = []
    mar = []
    apr = []
    may = []
    jun = []
    jul = []
    aug = []
    sep = []
    octo = []
    nov = []
    dec = []

    #        janSum = 0.0
    #        febSum = 0.0
    #        marSum = 0.0
    #        aprSum = 0.0
    #        maySum = 0.0
    #        junSum = 0.0
    #        julSum = 0.0
    #        augSum = 0.0
    #        sepSum = 0.0
    #        octSum = 0.0
    #        novSum = 0.0
    #        decSum = 0.0

    janIt = 0
    febIt = 0
    marIt = 0
    aprIt = 0
    mayIt = 0
    junIt = 0
    julIt = 0
    augIt = 0
    sepIt = 0
    octIt = 0
    novIt = 0
    decIt = 0

    for i in range(len(varUserDefined)):

        hour = i * timeStepInSeconds / 3600 + firstHourInYear

        (month, nix, nix) = getMonthIndexByHourOfYear(hour)

        if month == 1:
            jan.append(varUserDefined[i])
            #                janSum = janSum + varUserDefined[i]
            janIt = janIt + 1
        elif month == 2:
            feb.append(varUserDefined[i])
            #                febSum = febSum + varUserDefined[i]

            febIt = febIt + 1

        elif month == 3:
            mar.append(varUserDefined[i])
            #                marSum = marSum + varUserDefined[i]

            marIt = marIt + 1

        elif month == 4:
            apr.append(varUserDefined[i])
            #                aprSum = aprSum + varUserDefined[i]

            aprIt = aprIt + 1

        elif month == 5:
            may.append(varUserDefined[i])
            #                maySum = maySum + varUserDefined[i]

            mayIt = mayIt + 1

        elif month == 6:
            jun.append(varUserDefined[i])
            #                junSum = junSum + varUserDefined[i]

            junIt = junIt + 1

        elif month == 7:
            jul.append(varUserDefined[i])
            #                julSum = julSum + varUserDefined[i]

            julIt = julIt + 1

        elif month == 8:
            aug.append(varUserDefined[i])
            #                augSum = augSum + varUserDefined[i]

            augIt = augIt + 1

        elif month == 9:
            sep.append(varUserDefined[i])
            #                sepSum = sepSum + varUserDefined[i]

            sepIt = sepIt + 1

        elif month == 10:
            octo.append(varUserDefined[i])
            #                octSum = octSum + varUserDefined[i]

            octIt = octIt + 1

        elif month == 11:
            nov.append(varUserDefined[i])
            #                novSum = novSum + varUserDefined[i]

            novIt = novIt + 1

        elif month == 12:
            #                decSum = decSum + varUserDefined[i]

            dec.append(varUserDefined[i])
            decIt = decIt + 1

    varMonth = num.zeros(12)

    #        maxMonth=[0,0,0,0,0,0,0,0,0,0,0,0]
    #        minMonth=[0,0,0,0,0,0,0,0,0,0,0,0]
    #        avgMonth=[0,0,0,0,0,0,0,0,0,0,0,0]

    try:
        varMonth[0] = sum(jan)
        #            varMonth[0] = janSum

        #            maxMonth[0] = max(jan)
        #            minMonth[0] = min(jan)
        #            avgMonth[0] = varMonth[0]/janIt

        #            varMonth[1] = febSum

        varMonth[1] = sum(feb)
        #            maxMonth[1] = max(feb)
        #            minMonth[1] = min(feb)
        #            avgMonth[1] = varMonth[1]/febIt

        varMonth[2] = sum(mar)
        #            varMonth[2] = marSum

        #            maxMonth[2] = max(mar)
        #            minMonth[2] = min(mar)
        #            avgMonth[2] = varMonth[2]/marIt

        varMonth[3] = sum(apr)
        #            varMonth[3] = aprSum

        #            maxMonth[3] = max(apr)
        #            minMonth[3] = min(apr)
        #            avgMonth[3] = varMonth[3]/aprIt

        varMonth[4] = sum(may)
        #            varMonth[4] = maySum

        #            maxMonth[4] = max(may)
        #            minMonth[4] = min(may)
        #            avgMonth[4] = varMonth[4]/mayIt
        #
        varMonth[5] = sum(jun)
        #            varMonth[5] = junSum

        #            maxMonth[5] = max(jun)
        #            minMonth[5] = min(jun)
        #            avgMonth[5] = varMonth[5]/junIt

        varMonth[6] = sum(jul)
        #            varMonth[6] = julSum

        #            maxMonth[6] = max(jul)
        #            minMonth[6] = min(jul)
        #            avgMonth[6] = varMonth[6]/julIt

        varMonth[7] = sum(aug)
        #            varMonth[7] = augSum

        #            maxMonth[7] = max(aug)
        #            minMonth[7] = min(aug)
        #            avgMonth[7] = varMonth[7]/julIt

        varMonth[8] = sum(sep)
        #            varMonth[8] = sepSum

        #            maxMonth[8] = max(sep)
        #            minMonth[8] = min(sep)
        #            avgMonth[8] = varMonth[8]/augIt

        varMonth[9] = sum(octo)
        #            varMonth[9] = octSum
        #            maxMonth[9] = max(octo)
        #            minMonth[9] = min(octo)
        #            avgMonth[9] = varMonth[9]/sepIt
        #

        varMonth[10] = sum(nov)
        #            varMonth[10] = novSum

        #            maxMonth[10] = max(nov)
        #            minMonth[10] = min(nov)
        #            avgMonth[10] = varMonth[10]/novIt

        varMonth[11] = sum(dec)
    #            varMonth[11] = decSum
    #            maxMonth[11] = max(dec)
    #            minMonth[11] = min(dec)
    #            avgMonth[11] = varMonth[11]/decIt

    except:
        pass

    #        print varMonth

    #        raise ValueError("My crash")

    return varMonth


"""
From varUserDefined in the form var[timeStepinSeconds] in one year
the values are stored in varMonth as varMonth[0]=sum of Jan, etc..
"""


def calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep(
    varUserDefined, timeStepInSeconds, firstHourInYear=0, avoidZeros=False
):

    jan = []
    feb = []
    mar = []
    apr = []
    may = []
    jun = []
    jul = []
    aug = []
    sep = []
    octo = []
    nov = []
    dec = []

    janIt = 0
    febIt = 0
    marIt = 0
    aprIt = 0
    mayIt = 0
    junIt = 0
    julIt = 0
    augIt = 0
    sepIt = 0
    octIt = 0
    novIt = 0
    decIt = 0

    for i in range(len(varUserDefined)):
        hour = i * timeStepInSeconds / 3600 + firstHourInYear
        (month, nix, nix) = getMonthIndexByHourOfYear(hour)

        if month == 1:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                jan.append(varUserDefined[i])
                janIt = janIt + 1

        elif month == 2:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                feb.append(varUserDefined[i])
                febIt = febIt + 1

        elif month == 3:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                mar.append(varUserDefined[i])
                marIt = marIt + 1

        elif month == 4:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                apr.append(varUserDefined[i])
                aprIt = aprIt + 1

        elif month == 5:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                may.append(varUserDefined[i])
                mayIt = mayIt + 1

        elif month == 6:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                jun.append(varUserDefined[i])
                junIt = junIt + 1

        elif month == 7:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                jul.append(varUserDefined[i])
                julIt = julIt + 1

        elif month == 8:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                aug.append(varUserDefined[i])
                augIt = augIt + 1

        elif month == 9:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                sep.append(varUserDefined[i])
                sepIt = sepIt + 1

        elif month == 10:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                octo.append(varUserDefined[i])
                octIt = octIt + 1

        elif month == 11:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                nov.append(varUserDefined[i])
                novIt = novIt + 1

        elif month == 12:
            if avoidZeros == True and varUserDefined[i] == 0.0:
                pass
            else:
                dec.append(varUserDefined[i])
                decIt = decIt + 1
    #                    print "Dec i:%d varUserDefined[i]:%f"%(i,varUserDefined[i])

    varMonth = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    maxMonth = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    minMonth = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    avgMonth = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    try:
        varMonth[0] = sum(jan)
        maxMonth[0] = max(jan)
        minMonth[0] = min(jan)
        avgMonth[0] = varMonth[0] / janIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: Januray is not calculated")
        pass

    try:
        varMonth[1] = sum(feb)
        maxMonth[1] = max(feb)
        minMonth[1] = min(feb)
        avgMonth[1] = varMonth[1] / febIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: February is not calculated")
        pass

    try:
        varMonth[2] = sum(mar)
        maxMonth[2] = max(mar)
        minMonth[2] = min(mar)
        avgMonth[2] = varMonth[2] / marIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: March is not calculated")
        pass

    try:

        varMonth[3] = sum(apr)
        maxMonth[3] = max(apr)
        minMonth[3] = min(apr)
        avgMonth[3] = varMonth[3] / aprIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: April is not calculated")

        pass

    try:
        varMonth[4] = sum(may)
        maxMonth[4] = max(may)
        minMonth[4] = min(may)
        avgMonth[4] = varMonth[4] / mayIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: May is not calculated")

        pass

    try:
        varMonth[5] = sum(jun)
        maxMonth[5] = max(jun)
        minMonth[5] = min(jun)
        avgMonth[5] = varMonth[5] / junIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: June is not calculated")

        pass

    try:
        varMonth[6] = sum(jul)
        maxMonth[6] = max(jul)
        minMonth[6] = min(jul)
        avgMonth[6] = varMonth[6] / julIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: July is not calculated")

        pass

    try:
        varMonth[7] = sum(aug)
        maxMonth[7] = max(aug)
        minMonth[7] = min(aug)
        avgMonth[7] = varMonth[7] / julIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: August is not calculated")

        pass

    try:
        varMonth[8] = sum(sep)
        maxMonth[8] = max(sep)
        minMonth[8] = min(sep)
        avgMonth[8] = varMonth[8] / augIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: September is not calculated")

        pass

    try:
        varMonth[9] = sum(octo)
        maxMonth[9] = max(octo)
        minMonth[9] = min(octo)
        avgMonth[9] = varMonth[9] / sepIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: October is not calculated")

        pass

    try:
        varMonth[10] = sum(nov)
        maxMonth[10] = max(nov)
        minMonth[10] = min(nov)
        avgMonth[10] = varMonth[10] / novIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: November is not calculated")

        pass

    try:
        varMonth[11] = sum(dec)
        maxMonth[11] = max(dec)
        minMonth[11] = min(dec)
        avgMonth[11] = varMonth[11] / decIt
    except:
        print("calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep: December is not calculated")

        pass

    return varMonth, maxMonth, minMonth, avgMonth


def calculateMonthlyAvgFromUserDefinedTimeStep(varUserDefined, timeStepInSeconds):

    var, maxV, minV, avV = calculateMonthlyValuesMinMaxAvgFromUserDefinedTimeStep(varUserDefined, timeStepInSeconds)

    return avV


def getTLog(tIn, tOut, tStorage):

    dtIn = abs(tIn - tStorage)
    dtOut = abs(tOut - tStorage)

    if dtIn <= 0 or dtOut <= 0 or dtIn * dtOut < 0.0 or dtIn - dtOut < 1e-10:
        dtlm = 0.0
    else:
        dtlm = (dtOut - dtIn) / (math.log(dtIn / dtOut))

    #        print "dtIn:%f dtOut:%f dtlm:%f" % (dtIn,dtOut,dtlm)
    return dtlm


def getSecondOrder(a, b, c):

    sqTerm = b * b - (4.0 * a * c)

    if sqTerm < 0.0:
        return False

    sq = pow(sqTerm, 0.5)

    pos = (-b + sq) / (2.0 * a)
    neg = (-b - sq) / (2.0 * a)

    #    print "a:%f b:%f c:%f pos:%f neg:%f" % (a,b,c,pos,neg)

    return (pos, neg)


# print var(nVars,13) vector. Position 13 is for year value
def printMonthlyData(path, nameFile, var, legends):

    lines = ""
    line = "!nMonth\t"
    lines = lines + line

    for label in legends:
        line = "%s\t" % label
        lines = lines + line
    line = "\n"
    lines = lines + line

    for j in range(13):
        line = "%d\t" % (j + 1)
        lines = lines + line

        sumVar = 0.0
        for i in range(len(var)):

            sumVar = sumVar + var[i][j]
            line = "%f\t" % sumVar
            lines = lines + line

        line = "\n"
        lines = lines + line

    nameWithPath = "%s\%s.dat" % (path, nameFile)
    outfile = open(nameWithPath, "w")
    outfile.writelines(lines)
    outfile.close()


# This sums up the power, so it is assumed that units are W*s, or kW*h
def calcQvsT(tFlow, eFlow, nameFile=None):

    numberOfTimesteps = len(tFlow)

    sortedIndexTempFlow = num.argsort(tFlow)

    tFlowSort = num.zeros(numberOfTimesteps)

    cumulativeEFlow = num.zeros(numberOfTimesteps)

    energy = 0.0

    for i in range(len(sortedIndexTempFlow)):
        tFlowSort[i] = tFlow[sortedIndexTempFlow[i]]
        energy = energy + eFlow[sortedIndexTempFlow[i]]
        cumulativeEFlow[i] = energy

    if nameFile != None:
        lines = ""
        line = "!File processed with calcQVsT at %s\n" % (time.strftime("%c"))
        lines = lines + line
        line = "! tFlSort cumulativeEFl\n"
        lines = lines + line

        for i in range(numberOfTimesteps):
            line = "%f %f %f\n" % (i + 1, tFlowSort[i], cumulativeEFlow[i])
            lines = lines + line

        myFileName = nameFile
        outfile = open(myFileName, "w")
        outfile.writelines(lines)
        outfile.close()

    return tFlowSort, cumulativeEFlow


def sortVsT(tFlow, var, nameFile=None):

    numberOfTimesteps = len(tFlow)

    sortedIndexTempFlow = num.argsort(tFlow)

    tFlowSort = num.zeros(numberOfTimesteps)

    varSort = num.zeros(numberOfTimesteps)

    for i in range(len(sortedIndexTempFlow)):
        tFlowSort[i] = tFlow[sortedIndexTempFlow[i]]
        varSort[i] = var[sortedIndexTempFlow[i]]
    #        if(varSort[i]<1e-10): varSort[i]=varSort[i-1]

    if nameFile != None:
        lines = ""
        line = "!File processed with sortVsT at %s\n" % (time.strftime("%c"))
        lines = lines + line
        line = "! tFlSort sortVar\n"
        lines = lines + line

        for i in range(numberOfTimesteps):
            line = "%f %f %f\n" % (i + 1, tFlowSort[i], varSort[i])
            lines = lines + line

        myFileName = nameFile
        outfile = open(myFileName, "w")
        outfile.writelines(lines)
        outfile.close()

    return tFlowSort, varSort


def calcAndPrintQVersusT(
    outputPath,
    fileName,
    tShFl,
    tShRt,
    eSh,
    tColFl,
    eColToTes,
    eColToIce,
    eColToHp,
    tHpCond,
    eHpCond,
    tIceOut,
    eIceToTes,
    tHpEvap,
    eHpEvap,
    printEvery=1,
    qTesFromColUsed=False,
):

    numberOfTimesteps = len(tShFl)

    tShFlSort, cumulativeEShFl = calcQvsT(tShFl, eSh)
    tShRtSort, cumulativeEShRt = calcQvsT(tShRt, eSh)
    tColFlSort, cumulativeEColToTes = calcQvsT(tColFl, eColToTes)
    blank, cumulativeEColToIce = calcQvsT(tColFl, eColToIce)
    blank, cumulativeEColToHp = calcQvsT(tColFl, eColToHp)
    tHpCondSort, cumulativeEHpCond = calcQvsT(tHpCond, eHpCond)
    tIceFlSort, cumulativeEIceToTes = calcQvsT(tIceOut, eIceToTes)
    tHpEvapSort, cumulativeEHpEvap = calcQvsT(tHpEvap, eHpEvap)

    lines = ""
    line = "!Postprocessed file of ice storage. Kindergarten pilotplant of EWJR\n"
    lines = lines + line
    line = "!File processed with pilotPlantEwjr.py at %s\n" % (time.strftime("%c"))
    lines = lines + line
    if qTesFromColUsed:
        line = "! (2) tShVlSort (3)cumulativeEShVl (4)tShRtSort  (5)cumulativeEShRt (6)tColFlSort (7)cumulativeETesFromCol(!!) (8)cumulativeEColToIce (9)cumulativeEColToHp (10)tHpCondOutSort (11)cumulativeEHpCond (12)tIceFlSort (13)cumulativeEIceToTes (14)tHpEvapInSort (15)cumulativeEHpEvap\n"
        lines = lines + line
    else:
        line = "! (2) tShVlSort (3)cumulativeEShVl (4)tShRtSort  (5)cumulativeEShRt (6)tColFlSort (7)cumulativeEColToTes (8)cumulativeEColToIce (9)cumulativeEColToHp (10)tHpCondOutSort (11)cumulativeEHpCond (12)tIceFlSort (13)cumulativeEIceToTes (14)tHpEvapInSort (15)cumulativeEHpEvap\n"
        lines = lines + line

    for i in range(numberOfTimesteps):
        if i != 0 and i != numberOfTimesteps - 1:
            if i % printEvery == 0:
                line = "%d %f %f %f %f %f %f %f %f %f %f %f %f %f %f\n" % (
                    i + 1,
                    tShFlSort[i],
                    cumulativeEShFl[i],
                    tShRtSort[i],
                    cumulativeEShRt[i],
                    tColFlSort[i],
                    cumulativeEColToTes[i],
                    cumulativeEColToIce[i],
                    cumulativeEColToHp[i],
                    tHpCondSort[i],
                    cumulativeEHpCond[i],
                    tIceFlSort[i],
                    cumulativeEIceToTes[i],
                    tHpEvapSort[i],
                    cumulativeEHpEvap[i],
                )
                lines = lines + line

    #    name = fileName + "TVsQcum_Y.dat"
    myFileName = outputPath + "//" + fileName + ".dat"

    print("File created :%s" % myFileName)

    outfile = open(myFileName, "w")
    outfile.writelines(lines)
    outfile.close()

    createGleQvsT(outputPath, fileName)  # path not nedded becasue it is in the same folder

    for i in range(len(tHpEvapSort)):
        if cumulativeEHpEvap[i] > 1e-5:  # if acum heat is above 10 W
            return tHpEvapSort[i]


def calcAndPrintQVersusT_new(
    outputPath,
    fileName,
    tShFl,
    tShRt,
    eSh,
    tColFl,
    eColToTes,
    eColToIce,
    eColToHp,
    tHpCond,
    eHpCond,
    tIceOut,
    eIceToTes,
    tHpEvap,
    eHpEvap,
    eIceToHp,
    eIceToHpSeries,
    printEvery=1,
    qTesFromColUsed=False,
):

    numberOfTimesteps = len(tShFl)

    print("sum tShFl:%f tShRt:%f" % (sum(tShFl), sum(tShRt)))

    tShFlSort, cumulativeEShFl = calcQvsT(tShFl, eSh)
    tShRtSort, cumulativeEShRt = calcQvsT(tShRt, eSh)
    tColFlSort, cumulativeEColToTes = calcQvsT(tColFl, eColToTes)
    blank, cumulativeEColToIce = calcQvsT(tColFl, eColToIce)
    blank, cumulativeEColToHp = calcQvsT(tColFl, eColToHp)
    tHpCondSort, cumulativeEHpCond = calcQvsT(tHpCond, eHpCond)
    tIceFlSort, cumulativeEIceToTes = calcQvsT(tIceOut, eIceToTes)
    tHpEvapSort, cumulativeEHpEvap = calcQvsT(tHpEvap, eHpEvap)
    blank, cumulativeEIceToHp = calcQvsT(tHpEvap, eIceToHp)
    blank, cumulativeEIceToHpSeries = calcQvsT(tHpEvap, eIceToHpSeries)

    lines = ""
    line = "!Postprocessed file of ice storage.\n"
    lines = lines + line
    line = "!File processed with utils.py at %s\n" % (time.strftime("%c"))
    lines = lines + line
    if qTesFromColUsed:
        line = "! (2) tShVlSort (3)cumulativeEShVl (4)tShRtSort  (5)cumulativeEShRt (6)tColFlSort (7)cumulativeETesFromCol(!!) (8)cumulativeEColToIce (9)cumulativeEColToHp (10)tHpCondOutSort (11)cumulativeEHpCond (12)tIceFlSort (13)cumulativeEIceToTes (14)tHpEvapInSort (15)cumulativeEHpEvap (16)cumulativeEIceToHp (17)cumEIceToHpSeries\n"
        lines = lines + line
    else:
        line = "! (2) tShVlSort (3)cumulativeEShVl (4)tShRtSort  (5)cumulativeEShRt (6)tColFlSort (7)cumulativeEColToTes (8)cumulativeEColToIce (9)cumulativeEColToHp (10)tHpCondOutSort (11)cumulativeEHpCond (12)tIceFlSort (13)cumulativeEIceToTes (14)tHpEvapInSort (15)cumulativeEHpEvap (16)cumulativeEIceToHp (17)cumEIceToHpSeries\n"
        lines = lines + line

    for i in range(numberOfTimesteps):
        if i != 0 and i != numberOfTimesteps - 1:
            if i % printEvery == 0:
                line = "%d %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f %f\n" % (
                    i + 1,
                    tShFlSort[i],
                    cumulativeEShFl[i],
                    tShRtSort[i],
                    cumulativeEShRt[i],
                    tColFlSort[i],
                    cumulativeEColToTes[i],
                    cumulativeEColToIce[i],
                    cumulativeEColToHp[i],
                    tHpCondSort[i],
                    cumulativeEHpCond[i],
                    tIceFlSort[i],
                    cumulativeEIceToTes[i],
                    tHpEvapSort[i],
                    cumulativeEHpEvap[i],
                    cumulativeEIceToHp[i],
                    cumulativeEIceToHpSeries[i],
                )
                lines = lines + line

    #    name = fileName + "TVsQcum_Y.dat"
    myFileName = outputPath + "//" + fileName + ".dat"

    print("File created :%s" % myFileName)

    outfile = open(myFileName, "w")
    outfile.writelines(lines)
    outfile.close()

    createGleQvsT_new(outputPath, fileName)  # path not nedded becasue it is in the same folder

    for i in range(len(tHpEvapSort)):
        if cumulativeEHpEvap[i] > 1e-5:  # if acum heat is above 10 W
            return tHpEvapSort[i]


def createGleQvsT(outputPath, fileName):

    lines = ""

    line = "size 14 8\n"
    lines = lines + line
    line = "set texlabels 1\n"
    lines = lines + line
    line = "begin graph\n"
    lines = lines + line
    line = "size 12 8\n"
    lines = lines + line
    line = 'ytitle "$Q_{accumulated}$ [MWh]" \n'
    lines = lines + line
    line = 'xtitle "$T$ [$^oC$]" \n'
    lines = lines + line

    line = "xaxis min -10 max 100.0 dticks 20.0\n"
    lines = lines + line
    line = "!yaxis min 0 max 35.0 dticks 5.0\n"
    lines = lines + line
    line = "ylabels on\n"
    lines = lines + line
    line = "yticks color grey20\n"
    lines = lines + line
    line = "xticks on\n"
    lines = lines + line
    line = "yticks color grey20\n"
    lines = lines + line
    line = 'myFile$ = "%s.dat"\n' % fileName
    lines = lines + line
    line = " data   myFile$ d1 = c2,c3 \n"
    lines = lines + line
    line = " data   myFile$ d2 = c4,c5 \n"
    lines = lines + line
    line = " data   myFile$ d3 = c6,c7 \n"
    lines = lines + line
    line = " data   myFile$ d4 = c6,c8 \n"
    lines = lines + line
    line = " data   myFile$ d5 = c6,c9 \n"
    lines = lines + line
    line = " data   myFile$ d6 = c10,c11 \n"
    lines = lines + line
    line = " data   myFile$ d7 = c12,c13 \n"
    lines = lines + line
    line = " data   myFile$ d8 = c14,c15 \n"
    lines = lines + line

    line = 'd1 lstyle 1 line lwidth 0.01 color red key "$Q_{Sh,Tfl}$"  \n'
    lines = lines + line
    line = 'd2 lstyle 1 line lwidth 0.01 color blue key "$Q_{Sh,Trt}$"  \n'
    lines = lines + line
    line = 'd3 lstyle 1 line lwidth 0.01 color green key "$Q_{ColToTes}$"  \n'
    lines = lines + line
    line = 'd4 lstyle 1 line lwidth 0.01 color gray40 key "$Q_{ColToIce}$"  \n'
    lines = lines + line
    line = 'd5 lstyle 1 line lwidth 0.01 color orange key "$Q_{ColToHp}$"  \n'
    lines = lines + line
    line = 'd6 lstyle 1 line lwidth 0.01 color magenta key "$Q_{HP,Cond}$"  \n'
    lines = lines + line
    line = 'd7 lstyle 1 line lwidth 0.01 color gray50 key "$Q_{IceToTes}$"  \n'
    lines = lines + line
    line = 'd8 lstyle 1 line lwidth 0.01 color black key "$Q_{Hp,Evap}$"  \n'
    lines = lines + line

    line = " key pos tr hei 0.2 offset -0.5 0\n"
    lines = lines + line
    line = "end graph\n"
    lines = lines + line
    myFileNameGleFile = outputPath + "\\" + fileName.split(".")[0] + ".gle"

    outfile = open(myFileNameGleFile, "w")
    outfile.writelines(lines)
    outfile.close()


def createGleQvsT_new(outputPath, fileName):

    lines = ""

    line = "size 14 8\n"
    lines = lines + line
    line = "set texlabels 1\n"
    lines = lines + line
    line = "begin graph\n"
    lines = lines + line
    line = "size 12 8\n"
    lines = lines + line
    line = 'ytitle "$Q_{cumulative}$ [MWh]" \n'
    lines = lines + line
    line = 'xtitle "$T$ [$^oC$]" \n'
    lines = lines + line

    line = "xaxis min -10 max 100.0 dticks 20.0\n"
    lines = lines + line
    line = "!yaxis min 0 max 35.0 dticks 5.0\n"
    lines = lines + line
    line = "ylabels on\n"
    lines = lines + line
    line = "yticks color grey20\n"
    lines = lines + line
    line = "xticks on\n"
    lines = lines + line
    line = "yticks color grey20\n"
    lines = lines + line
    line = 'myFile$ = "%s.dat"\n' % fileName
    lines = lines + line
    line = " data   myFile$ d1 = c2,c3 \n"
    lines = lines + line
    line = " data   myFile$ d2 = c4,c5 \n"
    lines = lines + line
    line = " data   myFile$ d3 = c6,c7 \n"
    lines = lines + line
    line = " data   myFile$ d4 = c6,c8 \n"
    lines = lines + line
    line = " data   myFile$ d5 = c6,c9 \n"
    lines = lines + line
    line = " data   myFile$ d6 = c10,c11 \n"
    lines = lines + line
    line = " data   myFile$ d7 = c12,c13 \n"
    lines = lines + line
    line = " data   myFile$ d8 = c14,c15 \n"
    lines = lines + line
    line = " data   myFile$ d9 = c14,c16 \n"
    lines = lines + line
    line = " data   myFile$ d10 = c14,c17 \n"
    lines = lines + line

    line = 'd1 lstyle 1 line lwidth 0.01 color red key "$Q_{Sh,Tfl}$"  \n'
    lines = lines + line
    line = 'd2 lstyle 1 line lwidth 0.01 color blue key "$Q_{Sh,Trt}$"  \n'
    lines = lines + line
    line = 'd3 lstyle 1 line lwidth 0.01 color green key "$Q_{ColToTes}$"  \n'
    lines = lines + line
    line = 'd4 lstyle 1 line lwidth 0.01 color gray40 key "$Q_{ColToIce}$"  \n'
    lines = lines + line
    line = 'd5 lstyle 1 line lwidth 0.01 color orange key "$Q_{ColToHp}$"  \n'
    lines = lines + line
    line = 'd6 lstyle 1 line lwidth 0.01 color magenta key "$Q_{HP,Cond}$"  \n'
    lines = lines + line
    line = 'd7 lstyle 1 line lwidth 0.01 color gray50 key "$Q_{IceToTes}$"  \n'
    lines = lines + line
    line = 'd8 lstyle 1 line lwidth 0.01 color black key "$Q_{Hp,Evap}$"  \n'
    lines = lines + line
    line = 'd9 lstyle 1 line lwidth 0.01 color yellow key "$Q_{IceToHpProHp}$"  \n'
    lines = lines + line
    line = 'd10 lstyle 1 line lwidth 0.01 color cyan key "$Q_{IceToHpSeries}$"  \n'
    lines = lines + line

    line = " key pos tr hei 0.2 offset -0.5 0\n"
    lines = lines + line
    line = "end graph\n"
    lines = lines + line
    myFileNameGleFile = outputPath + "\\" + fileName.split(".")[0] + ".gle"

    outfile = open(myFileNameGleFile, "w")
    outfile.writelines(lines)
    outfile.close()
