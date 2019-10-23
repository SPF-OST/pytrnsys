
import numpy as num

def replaceAllUnits(linesRead ,idBegin ,TrnsysUnits ,filesUnitUsedInDdck ,filesUsedInDdck):

    unitId = idBegin

    for i in range(len(TrnsysUnits)):
        unitId=unitId+1
        replaceUnitNumber(linesRead ,int(TrnsysUnits[i]) ,unitId)


    for i in range(len(filesUnitUsedInDdck)):

        try:
            filesUnitUsedInDdck[i] = int(filesUnitUsedInDdck[i])

            print ("fileUnit is an integer %d. THIS IS NOT RECOMENDED SINCE AUTOMATIC UNIT NUMBERING DOES NOT WORK" % filesUnitUsedInDdck[i])

        except:
            # print ("fileUnit is a string %s. Look for the string unit" % self.filesUnitUsedInDdck[i])
            for j in range(len(linesRead)):
                splitEqual= linesRead[j].split("=")

                if (splitEqual[0].replace(" " ,"") == filesUnitUsedInDdck[i]):
                    unitId = unitId + 1

                    linesRead[j] = "%s = %d\n " %(filesUnitUsedInDdck[i] ,unitId)
                    print ("StringUnit from file %s changed from %s to %d" %
                    (filesUsedInDdck[i], splitEqual[1][:-1], unitId))

    return unitId

def readAllTypes(lines,sort=True):  # lines should be self.linesChanged

    """
        It reads all types and units from a a list of lines readed from a deck file.
        It also reads the files used and which units are used for them. IN order to be able to change automatically the unit numbers afterwards
        we need that each ASSIGN uses a variable for the unit, e.g. unitReadWeather and that this variable is used in the ddck file.

        returns:
        --------
        TrnsysUnitsSorted,TrnsysTypesSorted,filesUsedInDdck,filesUnitUsedInDdck
    """
    TrnsysTypes = []
    TrnsysUnits = []
    filesUsedInDdck = []
    filesUnitUsedInDdck = []

    for i in range(len(lines)):

        splitBlank = lines[i].split()

        try:
            if (splitBlank[0] == "ASSIGN"):
                filesUsedInDdck.append(splitBlank[1])
                filesUnitUsedInDdck.append(splitBlank[2])
        except:
            pass

        try:
            unit = splitBlank[0].replace(" ", "")
            nUnit = splitBlank[1].replace(" ", "")
            types = splitBlank[2].replace(" ", "")
            ntype = splitBlank[3].replace(" ", "")

            if (unit.lower() == "unit".lower() and types.lower() == "Type".lower()):
                #                    print "unit:%s nUnit:%s types:%s ntype:%s"%(unit,nUnit,types,ntype)
                TrnsysTypes.append(int(ntype))
                TrnsysUnits.append(int(nUnit))

        except:
            pass

    # We need to sort them for units. Otherwise when we change unit numbers we can change something already changed
    # for example we replace UNIT 400 for UNIT 20 and at the end we have UNIT 20 again and we change it for UNIT 100

    if(sort==False):
        TrnsysTypesSorted=TrnsysTypes
        TrnsysUnitsSorted=TrnsysUnits
    else:
        TrnsysTypesSorted = []
        TrnsysUnitsSorted = []

        iSort = num.argsort(TrnsysUnits)
        for i in range(len(TrnsysTypes)):
            k = iSort[i]
            TrnsysUnitsSorted.append(TrnsysUnits[k])
            TrnsysTypesSorted.append(TrnsysTypes[k])

    #Check if any value is repeated.

    return TrnsysUnitsSorted,TrnsysTypesSorted,filesUsedInDdck,filesUnitUsedInDdck

def replaceUnitNumber(linesRead,oldUnit,newUnit):

    lines = linesRead

    unitFromTypeChanged=False

    if(oldUnit==newUnit):
        pass
    else:
        for i in range(len(lines)):

            if(unitFromTypeChanged==False):
                oldString = "UNIT %d" % (oldUnit)
                newString = "UNIT %d" % (newUnit)

                newLine= lines[i].replace(oldString, newString)

                if(newLine!=lines[i]):
                    unitFromTypeChanged=True
                    print ("replacement SUCCESS from %s to %s"%(oldString,newString))
                    lines[i]=newLine

        if (unitFromTypeChanged == False):
            print ("replacement FAILURE from %s to %s" % (oldUnit, newUnit))
        else:
            for i in range(len(lines)):

                oldString = "[%d," % (oldUnit)
                newString = "[%d," % (newUnit)
                newLine = lines[i].replace(oldString, newString)
                if(newLine!=lines[i]):
                    # print ("replacement SUCCESS from %s to %s"%(oldString,newString))
                    lines[i] = newLine

def getTypeFromUnit(myUnit,linesReadedNoComments):

    for i in range(len(linesReadedNoComments)):

        splitEquality = linesReadedNoComments[i].split()

        try:
            unit = splitEquality[0].replace(" ", "")
            nUnit = splitEquality[1].replace(" ", "")
            types = splitEquality[2].replace(" ", "")
            ntype = splitEquality[3].replace(" ", "")

            if (unit.lower() == "unit".lower() and types.lower() == "Type".lower()):

                if (nUnit.lower() == myUnit.lower()):
                    print ("UNIT FOUND myUnit:%s type:%s" % (myUnit, ntype))
                    return ntype
        except:
            pass

    return None

def getDataFromDeck(linesReadedNoComments, myName, typeValue="string"):

    value = getMyDataFromDeck(linesReadedNoComments,myName)

    if (value == None):
        return None

    if (typeValue == "double"):
        return float(value)
    elif (typeValue == "int"):
        return int(value)
    elif (typeValue == "string"):
        return value
    else:
        raise ValueError("typeValue must be double,int or string")

def getMyDataFromDeck(linesReadedNoComments,myName):

    for i in range(len(linesReadedNoComments)):

        splitEquality = linesReadedNoComments[i].split('=')

        try:
            name = splitEquality[0].replace(" ", "")
            value = splitEquality[1].replace(" ", "")

            if (name.lower() == myName.lower()):
                return value

        except:
            pass

    return None
