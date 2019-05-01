# -*- coding: utf-8 -*-
"""
Created on Thu Aug 08 07:57:08 2013

@author: dcarbone
"""

import os, shutil
import string

class CreateTrnsysDeck():
    
    def __init__(self,_path,_name,_variations):
        
        self.originalName = _name
        self.path = _path
        self.originalDeckName = os.path.join(self.path ,self.originalName +'.dck')
        self.variations = _variations                
        
        print "name:%s path:%s deckName:%s\n" % (self.originalName,self.path,self.originalDeckName)
        
        split = self.originalName.split('-')
#        T44A38-SGSHP-45-HE 
        try:             
            self.case = split[0]
            self.system = split[1]
            self.building = split[2]
            self.city = split[3] 
        except:
            pass
        
        self.deckOutputs = []
        self.combineAllCases=False
        
        self.createNewOne =True # In principle always on. Otherwise if a dck is found its not created again, and 
        # if we have changed something from the original we will no see the changes if this is set to False.
        # I will erase this if no utility after a while.

        #I guess this functions assumed we haev a base deck to apply the changes
    def generateDecks(self):
                 
        self.myListOfParameterDicts =[]
         
        print self.variations
        
        if(self.combineAllCases==False):
            for i in range (len(self.variations)):
                
                for j in range(len(self.variations[i])):
                    
                    if(j==0): 
                        # A comprensible name to be used as a tag in the file
                        nameLabelOfVariation = self.variations[i][j]
                    elif(j==1):
                        #the name how it is called inside the deck
                        nameVariationInDeck  = self.variations[i][j]
                    else:
                        valuesOfVariationInFile = self.variations[i][j]
                        
                        #If the name has 00 means 0. because the fileName will suffer from having points as names.
                        if(valuesOfVariationInFile=="00"):
                            valuesOfVariation = "0."+ valuesOfVariationInFile[2:]                                    
                            print "Comma found valueFile=%s valueUsed=%s" % (valuesOfVariationInFile,valuesOfVariation)
                        else:
                            valuesOfVariation = valuesOfVariationInFile
#                            print "Comma NOT found valueFile=%s valueUsed=%s" % (valuesOfVariationInFile,valuesOfVariation)
                        
                        
                        nameDeck = "%s-%s%s%s-%s-%s" % (self.case,self.system,nameLabelOfVariation,valuesOfVariationInFile,self.building,self.city)            
                        self.deckOutputs.append(nameDeck)
                        nameDeckCreated = "%s\%s.dck" % (self.path,nameDeck)
                        
    #                    print "DECK GENERATED :%s " % nameDeckCreated
                        
                        if(os.path.isfile(nameDeckCreated)):
                            if(self.createNewOne):
                                os.remove(nameDeckCreated)
                                shutil.copy(self.originalDeckName,nameDeckCreated)                            
                            else:
                                print "File exist, I do not create a new one"                        
                            pass
                        else:                     
                            shutil.copy(self.originalDeckName,nameDeckCreated)    
                        
                        parameterDict = {}
                        parameterDict[nameVariationInDeck]= valuesOfVariation
        
                        print parameterDict                                
                        self.myListOfParameterDicts.append(parameterDict)
        else:
            #For this case we assume they all have the same lenght
        
            nameLabelOfVariation = []
            nameVariationInDeck = []
            
            for nvar in range (len(self.variations)):
                nameLabelOfVariation.append(self.variations[nvar][0])
                nameVariationInDeck.append(self.variations[nvar][1])
            
#            print nameLabelOfVariation
#            print nameVariationInDeck
#            print len(self.variations[0])-2
            #all tags must have the same number of values    

            if(len(self.variations)>0):
                for j in range(2,len(self.variations[0])):

                        variationsLine =""
                        for nvar in range (len(self.variations)):

                            valuesOfVariationInFile = self.variations[nvar][j]

                            # If I write variation = ["","","GFX",...] then I add the name to the deck but no variation is used
                            if(len(self.variations[nvar][0])==0 and len(self.variations[nvar][1])==0):
                                variationsLine = variationsLine + "-%s" % (valuesOfVariationInFile)

                            #If I write variation = ["","useCovered",0,1] then no value is printed
                            elif(len(self.variations[nvar][0])>0):
                                variationsLine = variationsLine + "-%s%s" % (self.variations[nvar][0],valuesOfVariationInFile)

    #                        print "nameLabel:%s values:%s" % (self.variations[nvar][0],valuesOfVariationInFile)

                        try:
                            nameDeck = "%s-%s%s-%s-%s" % (self.case,self.system,variationsLine,self.building,self.city)
                        except:
                            nameDeck = "%s%s" % (self.case,variationsLine)

    #                    print nameDeck

                        self.deckOutputs.append(nameDeck)
                        nameDeckCreated = "%s\%s.dck" % (self.path,nameDeck)

                        #print "DECK GENERATED :%s " % nameDeckCreated

                        if(os.path.isfile(nameDeckCreated)):
                            if(self.createNewOne):
                                os.remove(nameDeckCreated)
                                shutil.copy(self.originalDeckName,nameDeckCreated)
                            else:
                                print "File exist, I do not create a new one"
                            pass
                        else:
                            shutil.copy(self.originalDeckName,nameDeckCreated)

                        parameterDict = {}

                        for nvar in range (len(self.variations)):
                            variationString = "%s" % self.variations[nvar][j]

                            if(variationString[:2]=="00"):
                                valuesOfVariation = "0."+ variationString[2:]
                                print "Comma found valueFile=%s valueUsed=%s" % (variationString,valuesOfVariation)
                            else:
                                valuesOfVariation = variationString
                                print "Comma NOT found valueFile=%s valueUsed=%s" % (variationString,valuesOfVariation)

                            parameterDict[nameVariationInDeck[nvar]]= valuesOfVariation

                        print parameterDict
                        self.myListOfParameterDicts.append(parameterDict)

#            print "myListOfParameterDict"
#            print self.myListOfParameterDicts
            
              
#        print self.deckOutputs
        
        return  self.deckOutputs
               
    def getParameters(self,i):
           
        return self.myListOfParameterDicts[i]
        
#        print  self.myListOfDicts
    
#    def getParameters(self)        
#        return self.deckOutputs
    
class ChangeTrnsysDeckDataFromCase():
    
    def __init__(self,_building,_city,_system=None):
        
        self.building = _building
        self.city = _city
        self.system = _system        
        self.parameters = {}              
        
# This is only valid if the system is the same than the one 
# used to be modified, so if SGSHP we can not switch to SASHP. 
# Many changed need to be implemented. However it can be done easily, if necessary  !!
      
    def changeSystemParameters(self):
        
                
        if(self.system=="SISHP"): # SOlAR + ICE SOURCE HEAT PUMP     
        
            areaHx = 2.104
            qEvap = string.atof(self.parameters["sizeHpUsed"])*0.79*1000. # W
            nHx = int(qEvap/(140.*areaHx))
            lBorehole = qEvap/50.            
#            nHx = "%s" % nHx
            
            if(self.building=="SFH15"):
            
                self.parameters.update({
                    "VIceS" : "20.0",
                    "NHx1"  : nHx,    # 0.79 *  
                    "AcollAp" : "15",
                    "AcollApUC" : "5",
                    "NghxProbes" : "1",
                    "lghxProbes" : lBorehole

                })
                
            elif(self.building=="SFH45"):
                
                self.parameters.update({
                    "VIceS" : "30.0",
                    "NHx1"  : nHx,
                    "AcollAp" : "25",
                    "AcollApUC" : "7",
                    "NghxProbes" : "1",
                    "lghxProbes" : lBorehole
                })
                
            elif(self.building=="SFH100"):
                
                self.parameters.update({
                    "VIceS" : "40.0",
                    "NHx1"  : nHx,
                    "AcollAp" : "35",
                    "AcollApUC" : "10",
                    "NghxProbes" : "1",
                    "lghxProbes" : lBorehole
                })
        elif(self.system=="SGSHP" or self.system=="SASHP"):
            pass
        else:
            raise ValueError("System unknown ",self.system)
            
    def changeBuildingBaseParameters(self):     
        
         if(self.building=="SFH15"):

            self.parameters = {
            "Nbui" : "1",     # Building type
            "TambHS" : "12",  # Temperature below which heating season is activated, °C
            "UaBui" : "97",  # Heat loss rate, W/K 
            "m_Rd" : "1.1",   # radiator exponent, -
            "CeffRad" : "40000",  # Thermal Cap. of Radiator, kJ/K
            "UGrFloor" : "0.141", #U-Value of Ground floor, W/m2K                
            "buildingName" : "T44A38sfh015.bui"
            }
            
         elif(self.building=="SFH45"):
            self.parameters = {
            "Nbui" : "2",     # Building type
            "TambHS" : "14",  # Temperature below which heating season is activated, °C
            "UaBui" : "168",  # Heat loss rate, W/K 
            "m_Rd" : "1.1",   # radiator exponent, -
            "CeffRad" : "40000",  # Thermal Cap. of Radiator, kJ/K
            "UGrFloor" : "0.183", #U-Value of Ground floor, W/m2K                
            "buildingName" : "T44A38sfh045.bui"
            }
            
         elif(self.building=="SFH100"):
            self.parameters = {
            "Nbui" : "3",     # Building type
            "TambHS" : "15",  # Temperature below which heating season is activated, °C
            "UaBui" : "290",  # Heat loss rate, W/K 
            "m_Rd" : "1.3",   # radiator exponent, -
            "CeffRad" : "1150",  # Thermal Cap. of Radiator, kJ/K
            "UGrFloor" : "0.278", #U-Value of Ground floor, W/m2K
            "buildingName" : "T44A38sfh100.bui"
            }
         else:
            raise ValueError("Building unknown ",self.building)
     
    def getChangedParameters(self):
                
        self.changeBuildingBaseParameters()
        
        self.changeBuildingCityParameters()
        
        self.changeSystemParameters()
                
        # A dictionary with the parameters changed 
        return self.parameters
     
    def changeBuildingCityParameters(self):
        
                        
         if(self.city=="HE"):    
            
            raise ValueError("Helsinki still ot finish. Check Borehols and sizeHp")
            
            if(self.building=="SFH15"):
                
                self.parameters.update({                
                "PheatBuiD" : "11149.2",  # Design heating rate for building an location [kJ/h]
                "TBuiFlNom" : "35", # Design flow temp. heating syst. [°C]                   
                "TBuiRtNom" : "30", # Design return temp. heating syst. [°C]    
                "NghxProbes" : "1", # Number of boreholes, -
                "lghxProbes" : "75"# length of boreholes, m
                })
            elif(self.building=="SFH45"):
                self.parameters.update({                
                "PheatBuiD" : "22734",  # Design heating rate for building an location [kJ/h]
                "TBuiFlNom" : "40", # Design flow temp. heating syst. [°C]                   
                "TBuiRtNom" : "35", # Design return temp. heating syst. [°C]    
                "NghxProbes" : "2", # Number of boreholes, -
                "lghxProbes" : "95"# length of boreholes, m
        #            ASSIGN  building\T44A38sfh015.bui 56     ! Building def. file, -
                })
            elif(self.building=="SFH100"):
                self.parameters.update({                
                "PheatBuiD" : "39351.6",  # Design heating rate for building an location [kJ/h]
                "TBuiFlNom" : "60", # Design flow temp. heating syst. [°C]                   
                "TBuiRtNom" : "50", # Design return temp. heating syst. [°C]    
                "NghxProbes" : "4", # Number of boreholes, -
                "lghxProbes" : "95",# length of boreholes, m
                #ASSIGN  building\T44A38sfh100.bui 56     ! Building def. file, -
                })
            
            
         elif(self.city=="ST"):    
            
            if(self.building=="SFH15"):
                
                self.parameters.update({
               
                "PheatBuiD" : "6451.2",  # Design heating rate for building an location [kJ/h]
                "TBuiFlNom" : "35", # Design flow temp. heating syst. [°C]                   
                "TBuiRtNom" : "30", # Design return temp. heating syst. [°C]    
                "NghxProbes" : "1", # Number of boreholes, -
                "lghxProbes" : "75",# length of boreholes, m
                "dghxProbes" : "0.026", # diameter of boreholes, m
                "sizeHpUsed" : "4.0",    # sizeHpUsed 
                })
                
            elif(self.building=="SFH45"):
                self.parameters.update({
              
                "PheatBuiD" : "14659.2",  # Design heating rate for building an location [kJ/h]
                "TBuiFlNom" : "35", # Design flow temp. heating syst. [°C]                   
                "TBuiRtNom" : "30", # Design return temp. heating syst. [°C]    
                "NghxProbes" : "1", # Number of boreholes, -
                "lghxProbes" : "90", # length of boreholes, m
                "dghxProbes" : "0.032", # diameter of boreholes, m
                "sizeHpUsed" : "6.5",    # sizeHpUsed 
                })
                
            elif(self.building=="SFH100"):
                self.parameters.update({                
                "PheatBuiD" : "26413.2",  # Design heating rate for building an location [kJ/h]
                "TBuiFlNom" : "55", # Design flow temp. heating syst. [°C]                   
                "TBuiRtNom" : "45", # Design return temp. heating syst. [°C]    
                "NghxProbes" : "1", # Number of boreholes, -
                "lghxProbes" : "170",# length of boreholes, m
                "dghxProbes" : "0.032", # diameter of boreholes, m
                "sizeHpUsed" : "11.3",    # sizeHpUsed 
               
                })               
         else:            
            raise ValueError("ONLY AUTOMATIC CHANGED WITH HELSINKI OR STRASBOURG")
        
   

    
#Missing 