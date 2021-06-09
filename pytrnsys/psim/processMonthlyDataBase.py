# pylint: skip-file
# type: ignore

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is the Base Class for reading and processing TRNSYS monthly results.
Author : Dani Carbonell
Date   : 2018
ToDo   : THIS FILE IS TO BE DEPRECATED !!!
"""

import string, os, time, sys
import pytrnsys.pdata.processFiles as spfUtils
import pytrnsys.utils.utilsSpf as utils
import pytrnsys.report.latexReport as latex
import matplotlib.pyplot as plt
import numpy as num
import matplotlib
import pytrnsys.plot.plotMatplotlib as plot

class ProcessMonthlyDataBase():
    
    def __init__(self,_path,_name,language='en'):
              
        self.fileName = _name
        self.outputPath = _path + "\%s" % self.fileName  
        self.executingPath = _path 

        # Internal data                       
              
        self.fileNameWithExtension = _name             
        self.titleOfLatex = "$%s$" % self.fileName    
        self.folderName  = self.fileName                            
        
        self.rootPath=os.getcwd()         
                          
        self.doc = latex.LatexReport(self.outputPath,self.fileName)

        self.plot = plot.PlotMatplotlib(language=language)
        self.plot.setPath(self.outputPath)

        self.initializeData()

    def initializeData(self):

        self.numberOfMonthSimulated = 0
        self.perCent = "\%"
        self.useFixedControl = False
        self.plotJpg = False
        self.plotExtension = "png"

        #        'svgz': 'Scalable Vector Graphics',
        #        'ps': 'Postscript',
        #        'emf': 'Enhanced Metafile',
        #        'rgba': 'Raw RGBA bitmap',
        #        'raw': 'Raw RGBA bitmap',
        #        'pdf': 'Portable Document Format',
        #        'svg': 'Scalable Vector Graphics',
        #        'eps': 'Encapsulated Postscript',
        #        'png': 'Portable Network Graphics'

        self.yearlyFactor = 10.  # value to divide yerarly values when plotted along with monthly data
        self.useImbalanceInLegendPlot = False

        self.addLinesInCreateFileWithResults="\n"
        self.typeOfSystem = "unknown"

        self.existSolarLoop = False
        self.existTesForDwhOnly = False
        self.printImbPlot = True
        self.printDataPlot = True

    def calculateAuxiliaryHeaters(self):

        self.qAuxHeaterTotal = self.qAuxHeaterHp + self.qAuxHeaterDhw + self.qAuxHeaterSh

    def calculatePipeLosses(self):

        self.qLossPipeSystem = self.qLossPipeSolarLoop + self.qPipeLossHPSink + self.qPipeLossDHW + \
                               self.qPipeLossSH

    def calculateEnergyBalance(self):

        self.qLossCol = num.zeros(12)
        self.etaCol   = num.zeros(12)
        self.COPhp    = num.zeros(12)
        self.SPFhp    = num.zeros(12)
        self.pElPu    = num.zeros(12)
        self.pElPuDis = num.zeros(12)
        self.pElTotal = num.zeros(12)
        self.pElTotalDis = num.zeros(12)
        self.fSolar = num.zeros(12)
        self.SPFhps = num.zeros(12)
        self.SPFhpsNoCool = num.zeros(12)
        self.SPFhpsWithDis = num.zeros(12)
        self.SPFhpsPen = num.zeros(12)
        self.SPFhpsWithDisPen = num.zeros(12)

        for i in range(12):
            if (self.existSolarLoop):
                self.qLossCol[i] = self.qSunToCol[i] - self.qSolarToSystem[i]
                self.etaCol[i] = self.qSolarToSystem[i] / (self.qSunToCol[i] + 1e-30)

            if (self.useFixedControl):
                if (self.neglectSolarController):
                    self.pElControllerSolar[i] = 0.0

                else:
                    self.pElControllerSolar[i] = self.fixedWSolarController * utils.getNumberOfDaysOfMonth(
                        i + 1) * 24 / 1000  # kW

                self.pElControllerHp[i] = self.fixedWHpController * utils.getNumberOfDaysOfMonth(
                    i + 1) * 24 / 1000  # kW
                self.pElController[i] = self.pElControllerHp[i] + self.pElControllerSolar[i]

            if (self.qWcpHP[i] == 0.0):
                self.COPhp[i] = 0.0
                self.SPFhp[i] = 0.0
            else:
                self.COPhp[i] = self.qCondHP[i] / (self.qWcpHP[i] + self.pElVentilatorHP[i] + self.qAuxHeaterHp[i])
                self.SPFhp[i] = self.qCondHP[i] / (
                            self.qWcpHP[i] + self.pumpHPsink[i] + self.pumpHPsource[i] + self.pElVentilatorHP[i] +
                            self.qAuxHeaterHp[i] + self.pElControllerHp[i])

            self.pElPu[i] = self.pumpHPsink[i] + self.pumpHPsource[i] + self.pumpSolar[i] + self.pElController[i] + \
                            self.pumpDHW[i]
            self.pElPuDis[i] = self.pElPu[i] + self.pumpSH[i]

            pel = self.qWcpHP[i] + self.qAuxHeaterTotal[i] + self.pElVentilatorHP[i]
            self.pElTotal[i] = self.pElPu[i] + pel
            self.pElTotalDis[i] = self.pElPuDis[i] + pel

            if (self.existSolarLoop):
                if (self.qUse[i] > 0):
                    self.fSolar[i] = min(100. * self.qSolarToTes[i] / self.qUse[i], 100.0)
                else:
                    self.fSolar[i] = 0.

            # SPF SOLAR + HP WITHOUT DISRTIBUTION

            if ((self.pElTotal[i]) <= 0.0):
                self.SPFhps[i] = 0.0
            else:
                self.SPFhps[i] = self.qUse[i] / self.pElTotal[i]

                self.SPFhpsNoCool[i] = (self.qUse[i]-self.qSC[i] )/ self.pElTotal[i]

            # SPF SOLAR + HP WITH DISRTIBUTION

            if ((self.pElTotalDis[i] + self.qWcpHP[i]) <= 0.0):
                self.SPFhps[i] = 0.0
            else:
                self.SPFhpsWithDis[i] = self.qUse[i] / self.pElTotalDis[i]

            if ((self.pElTotal[i]) <= 0.0):
                self.SPFhpsPen[i] = 0.0
            else:
                self.SPFhpsPen[i] = self.qDemand[i] / self.pElTotal[i]

            if ((self.pElTotalDis[i] + self.qWcpHP[i]) <= 0.0):
                self.SPFhpsWithDisPen[i] = 0.0
            else:
                self.SPFhpsWithDisPen[i] = self.qDemand[i] / self.pElTotalDis[i]
                print ("SPF:%f qD:%f Pel:%f wcp:%f pen:%f aux:%f" % (
                self.SPFhpsWithDisPen[i], self.qDemand[i], self.pElTotalDis[i], self.qWcpHP[i], self.pElPenalty[i],
                self.qAuxHeaterTotal[i]))


        self.yearQCondHp = sum(self.qCondHP)
        self.yearQUse = sum(self.qUse)
        self.yearQSC = sum(self.qSC)
        self.yearQWcpHp = sum(self.qWcpHP)
        self.yearPumpSourceHp = sum(self.pumpHPsource)
        self.yearPumpSinkHp = sum(self.pumpHPsink)
        if (self.existSolarLoop):
            self.yearPumpSolar = sum(self.pumpSolar)

        self.yearCOP = self.yearQCondHp / (
                    sum(self.qWcpHP) + sum(self.qAuxHeaterHp) + sum(self.pElVentilatorHP) + 1e-30)
        self.yearSPFhp = self.yearQCondHp / (sum(self.qWcpHP) + sum(self.qAuxHeaterHp) + sum(
            self.pElVentilatorHP) + self.yearPumpSourceHp + self.yearPumpSinkHp + sum(self.pElControllerHp) + 1e-30)
        self.yearSPFhps = self.yearQUse / (sum(self.pElTotal) + 1e-30)

        self.yearSPFhpsNoCool = (self.yearQUse-self.yearQSC) / (sum(self.pElTotal) + 1e-30)
        self.yearSPFhpsWithDis = self.yearQUse / (sum(self.pElTotalDis) + 1e-30)

        self.yearSPFhpsPen = sum(self.qDemand) / (sum(self.pElTotal) + 1e-30)

        self.yearSPFhpsWithDisPen = sum(self.qDemand) / (sum(self.pElTotalDis) + 1e-30)
        self.yearSPFhpsWithDisPenNoCool = sum(self.qDemand- self.qSC) / (sum(self.pElTotalDis) + 1e-30)

        self.yearSPFhpsBeforeTes = (sum(self.qTesFromSolar) + sum(self.qHpToSh) + sum(self.qTesFromHp)) / (
                    sum(self.pElTotal) + 1e-30)

        print ("EXIST SOLAR LOOP :%s " % self.existSolarLoop)

        if (self.existSolarLoop):
            self.yearQSolarToTes = sum(self.qSolarToTes)
            self.yearEta = sum(self.qSolarToSystem) / (sum(self.qSunToCol) + 1e-30)
            self.yearFSolar = 100.0 * self.yearQSolarToTes / (sum(self.qUse) + 1e-30)
            self.yearCOPtSolar = 100.0 * (self.yearQSolarToTes + sum(self.qSolarToPcm)) / (
                        sum(self.qSunToCol) + 1e-30)
            self.yearCOPeSolar = (self.yearQSolarToTes + sum(self.qSolarToPcm)) / (
                        sum(self.pumpSolar) + sum(self.pElControllerSolar) + 1e-30)

            print ("COPt:%f solarToCs:%f solarToWs:%f qSunToCol:%f" % (self.yearCOPtSolar, sum(self.qSolarToPcm), \
                                                                      self.yearQSolarToTes, sum(self.qSunToCol)))

        else:
            self.yearQSolarToTes = 0.
            self.yearEta = 0.
            self.yearFSolar = 0.
            self.yearCOPtSolar = 0.
            self.yearCOPeSolar = 0.

    #############################################
    # Section for plots
    #############################################

    def plotMonthlyWeatherData(self,yearlyFactor=10,printData=False):
        
        try:
            self.nameWeatherDataPlotPdf = self.plot.plotMonthly2Bar(self.iTHorizontalkWPerM2, self.iTColkWPerM2,
                                                                ['At horitzontal surface', 'At collector surface'],
                                                                "Solar radiation $[kWh/m^2]$", "weatherDataMonthly",
                                                                yearlyFactor=yearlyFactor)
        except:
            self.iTColkWPerM2 = self.qSolar/self.Acol
            self.nameWeatherDataPlotPdf = self.plot.plotMonthly2Bar(self.iTHorizontalkWPerM2, self.iTColkWPerM2,
                                                                    ['At horitzontal surface', 'At collector surface'],
                                                                    "Solar radiation $[kWh/m^2]$", "weatherDataMonthly",
                                                                    yearlyFactor=yearlyFactor)

        self.nameWeatherDataHoPlotPdf = self.plot.plotMonthly(self.iTHorizontalkWPerM2,"Solar radiation $[kWh/m^2]$","weatherDataMonthly",yearlyFactor=yearlyFactor,printData=printData)


    def plotBuildingMonthlyEnergyBalance(self,yearlyFactor=10,useYear=True,printData=False,printImb=True):
        
        inVar = []
        outVar = []
        legends = []
        
        inVar.append(self.qUseSh)
        legends.append("Radiator")
        
        inVar.append(self.qBuiSolarGains)
        legends.append("Solar Gains")

        inVar.append(self.qBuiIntGainPeople)
        legends.append("Int. Gains People")

        inVar.append(self.qBuiIntGainEq)
        legends.append("Int. Gains Eq.")

        inVar.append(self.qBuiIntGainLight)
        legends.append("Int. Gains Light")

        outVar.append(-self.qBuiTransLosses)
        legends.append("Trans. loss")

        outVar.append(-self.qBuiInfLosses)
        legends.append("Inf. loss")

        outVar.append(-self.qBuiVentLosses)
        legends.append("Vent. loss")

        outVar.append(-self.qBuiGroundLosses)
        legends.append("Ground loss.")

        outVar.append(-self.qBuiAcum)
        legends.append("Accumulated structure.")

        self.nameMonthlyBuiPlotPdf =  self.plot.plotMonthlyBalance(inVar,outVar,legends,'$Q$ $[kWh]$',"buiMonthly","MWh",printImb=printImb, \
                                                                   yearlyFactor=yearlyFactor, useYear=useYear, printData=printData)

    def plotMonthlyEnergyBalance(self): #to be updated with new functions
        
        N = 13
        width = 0.35        # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        fig = plt.figure(1,figsize=(12,8))
        
        plot = fig.add_subplot(111)
       
        imbPos = num.zeros(13)
        imbNeg =  num.zeros(13)
        
        #More processing is necessary if we want to have the yearly value at the 13 position as in Task44A38 
                  
        qSolarToSystem = utils.addYearlyValue(self.qSolarToSystem,yearlyFactor=self.yearlyFactor)
        pElPenalty     = utils.addYearlyValue(self.pElPenalty,yearlyFactor=self.yearlyFactor)
        
        #Only if parallel !!
        if(self.parallelSystem):
            
            qEvapHP = utils.addYearlyValue(self.qEvapHP,yearlyFactor=self.yearlyFactor)
            
        else:
            qEvapHP = num.zeros(13)
            
            
        
        ####
#        self.qAuxHeater = utils.addYearlyValue(self.qAuxHeater,yearlyFactor=self.yearlyFactor)
#        self.qWcpHP     = utils.addYearlyValue(self.qWcpHP ,yearlyFactor=self.yearlyFactor)

        qElHeatPump    = utils.addYearlyValue(self.qWcpHP,yearlyFactor=self.yearlyFactor)
        
        qAuxHeaterTotal = utils.addYearlyValue(self.qAuxHeaterTotal,yearlyFactor=self.yearlyFactor)

        qLossPipeSystem = num.zeros(12)
        qGainPipeSystem = num.zeros(12)
        
        for i in range(12):
            
            qLossPipeSystem[i] = abs(max(self.qLossPipeSystem[i],0.0))
            qGainPipeSystem[i] = abs(min(self.qLossPipeSystem[i],0.0))
    
        
        qLossPipeSystem = utils.addYearlyValue(qLossPipeSystem,yearlyFactor=self.yearlyFactor)
        qGainPipeSystem = utils.addYearlyValue(qGainPipeSystem,yearlyFactor=self.yearlyFactor)
        
        qLossTes = self.qLossTes + self.qLossConTnk
        
        qLossTes = utils.addYearlyValue(qLossTes,yearlyFactor=self.yearlyFactor)
        qLossHp   = utils.addYearlyValue(self.qLossHp,yearlyFactor=self.yearlyFactor)
        
        qDHW = utils.addYearlyValue(self.qDHW,yearlyFactor=self.yearlyFactor)
        qSH  = utils.addYearlyValue(self.qSH,yearlyFactor=self.yearlyFactor)

                   
        for i in range(13):
            
            bal = qSolarToSystem[i] + qElHeatPump[i] + qAuxHeaterTotal[i] + qGainPipeSystem[i] +qEvapHP[i]\
            - qLossPipeSystem[i] - qLossTes[i] - qLossHp[i]- qDHW[i] - qSH[i]                                                  
            
            imbNeg[i] = -max(bal,0.0)
            imbPos[i] = -min(bal,0.0)            
               
                    
        barQSolar    = plot.bar(ind-0.5*width, qSolarToSystem, width, color='y')   
        barQEvap     = plot.bar(ind-0.5*width, qEvapHP, width, color='#66CCFF',bottom=(qSolarToSystem))           
        barQWcp      = plot.bar(ind-0.5*width, qElHeatPump, width, color='0.75',bottom=(qSolarToSystem+qEvapHP))        
        barQAuxPEl   = plot.bar(ind-0.5*width, qAuxHeaterTotal, width, color='0.50',bottom=(qSolarToSystem+qEvapHP+qElHeatPump))    
        barPipeGain  = plot.bar(ind-0.5*width, qGainPipeSystem, width, color='g',bottom=(qSolarToSystem+qEvapHP+qElHeatPump+qAuxHeaterTotal))      
        
#        barQPenalty   = plot.bar(ind-0.5*width, qPenalty, width, color='#99FF99',bottom=(qSolarToSystem+qElHeatPump+qElHeater+qGainPcm)) 
#        barImbPos     = plot.bar(ind-0.5*width, imbPos, width, color='k',bottom=(qSolarToSystem+qElHeatPump+qElHeater+qGainPcm+qPenalty))
        barImbPos     = plot.bar(ind-0.5*width, imbPos, width, color='k',bottom=(qSolarToSystem+qEvapHP+qElHeatPump+qAuxHeaterTotal+qGainPipeSystem))
        
        barQDHW     = plot.bar(ind-0.5*width, -qDHW, width, color='b')
        barQSH      = plot.bar(ind-0.5*width, -qSH, width, color='r',bottom=-(qDHW))
        barTesLoss  = plot.bar(ind-0.5*width, -qLossTes, width, color='m',bottom=-(qDHW+qSH))       
        barPipeLoss = plot.bar(ind-0.5*width, -qLossPipeSystem, width, color='g',bottom=-(qDHW+qSH+qLossTes))
        barHpLoss   = plot.bar(ind-0.5*width, -qLossHp, width, color='c',bottom=-(qDHW+qSH+qLossTes+qLossPipeSystem))

        barImbNeg   = plot.bar(ind-0.5*width, imbNeg, width, color='k',bottom=-(qDHW+qSH+qLossTes+qLossPipeSystem+qLossHp))
                              
        # add some            

        plot.set_ylabel('$Q$ $[kWh]$',size=25)
#        plot.set_ylabel('',size=10)
        
        box = plot.get_position()        
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        plot.set_title('Monthly energy balance',size=20)
        plot.set_xticks(ind)
        plot.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Oct', 'Nov', 'Dec','Year/10'),fontsize=25)                       
        
        if(self.useImbalanceInLegendPlot):

            plot.legend( (barQSolar[0], barQEvap[0],barQWcp[0],barQAuxPEl[0], barQDHW[0],barQSH[0],barTesLoss[0],barPipeLoss[0],barHpLoss[0],barImbNeg[0]),\
            ('Solar to System', 'HP Evaporator','HP Compressor','El. Heater','DHW', 'Space Heat','TES Losses','Pipe Gain/Losses','HP Losses','Imbalance'),\
            bbox_to_anchor=(1.05,1),loc=2, borderaxespad=0.,fontsize=8)
        else:

            plot.legend( (barQSolar[0], barQEvap[0],barQWcp[0],barQAuxPEl[0], barQDHW[0],barQSH[0],barTesLoss[0],barPipeLoss[0],barHpLoss[0]),\
            ('Solar to System', 'HP Evaporator','HP Compressor','El. Heater','DHW', 'Space Heat','TES Losses','Pipe Gain/Losses','HP Losses'),\
            bbox_to_anchor=(1.05,1),loc=2, borderaxespad=0.,fontsize=8)
            
        self.nameMonthlyEnergyPlotPdf = 'energyMonthly.pdf'
        self.nameMonthlyEnergyPlotPdfWithPath = '%s\%s' % (self.outputPath,self.nameMonthlyEnergyPlotPdf)

        plt.xlim([-0.5,12.5])
        
        plt.savefig(self.nameMonthlyEnergyPlotPdfWithPath)
        
        if(self.plotJpg):
            
            nameJpg = 'energyMonthly.jpg' 
            nameJpgWithPath = '%s\%s' % (self.outputPath,nameJpg)
        
            plt.savefig(nameJpgWithPath)


        plt.close()

    def plotMonthlyEnergyBalanceByKwargs(self,**kwargs):

        N = 13
        width = 0.35        # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        fig = plt.figure(1,figsize=(12,8))

        plot = fig.add_subplot(111)

        imbPos = num.zeros(13)
        imbNeg =  num.zeros(13)
        bottomNeg = num.zeros(13)
        bottomPos = num.zeros(13)
        bal = num.zeros(13)


        for name, values in kwargs.items():
            values = utils.addYearlyValue(values,yearlyFactor=self.yearlyFactor)

            for i in range(13):

                bal[i] = bal[i] + values[i]
                imbNeg[i] = -max(bal,0.0)
                imbPos[i] = -min(bal,0.0)

            bar    = plot.bar(ind-0.5*width, values, width,label=name)
            bottomNeg = bottomNeg + (values<0).astype(float)*values
            bottomPos = bottomNeg + (values>0).astype(float)*values

        if(self.useImbalanceInLegendPlot):
            barImbNeg   = plot.bar(ind-0.5*width, imbNeg, width, color='k',bottom=bottomNeg,label='Imbalance')
            barImbPos   = plot.bar(ind-0.5*width, imbNeg, width, color='k',bottom=bottomPos)
        else:
            barImbNeg   = plot.bar(ind-0.5*width, imbNeg, width, color='k',bottom=bottomNeg)
            barImbPos   = plot.bar(ind-0.5*width, imbNeg, width, color='k',bottom=bottomPos)

        plot.set_ylabel('$Q$ $[kWh]$',size=25)

        box = plot.get_position()
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        plot.set_title('Monthly energy balance',size=20)
        plot.set_xticks(ind)
        plot.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Oct', 'Nov', 'Dec','Year/10'),fontsize=25)

        plot.legend(bbox_to_anchor=(1.05,1),loc=2, borderaxespad=0.,fontsize=8)

        self.nameMonthlyEnergyPlotPdf = 'energyMonthly.pdf'
        self.nameMonthlyEnergyPlotPdfWithPath = '%s\%s' % (self.outputPath,self.nameMonthlyEnergyPlotPdf)

        plt.xlim([-0.5,12.5])

        plt.savefig(self.nameMonthlyEnergyPlotPdfWithPath)

        if(self.plotJpg):

            nameJpg = 'energyMonthly.jpg'
            nameJpgWithPath = '%s\%s' % (self.outputPath,nameJpg)

            plt.savefig(nameJpgWithPath)


        plt.close()

    def plotSolarMonthlyEnergyBalance(self):
        
        N = 13
        width = 0.35        # the width of the bars
        ind = num.arange(N)  # the x locations for the groups

        fig = plt.figure(1,figsize=(12,8))
        
        plot = fig.add_subplot(111)
       
        imbPos = num.zeros(13)
        imbNeg =  num.zeros(13)
        
        qSolarToSystem = utils.addYearlyValue(self.qSolarToSystem,yearlyFactor=self.yearlyFactor)
        
#        qSolarToHp     = utils.addYearlyValue(self.qSolarToHp,yearlyFactor=self.yearlyFactor)
        qSolarToTes   = utils.addYearlyValue(self.qSolarToTes,yearlyFactor=self.yearlyFactor)
        qLossPipeSolarLoop     =  utils.addYearlyValue(self.qLossPipeSolarLoop,yearlyFactor=self.yearlyFactor)

        
        for i in range(13):
            
            bal = qSolarToSystem[i] -  qSolarToTes[i] - qLossPipeSolarLoop[i]                                                
            
            imbNeg[i] = -max(bal,0.0)
            imbPos[i] = -min(bal,0.0)            

        bar1   = plot.bar(ind-0.5*width, qSolarToSystem, width, color='#FFCC33')        
        barImbPos     = plot.bar(ind-0.5*width, imbPos, width, color='k',bottom=(qSolarToSystem))

        bar2    = plot.bar(ind-0.5*width, -qSolarToTes, width, color='#33FF33')    
        bar3    = plot.bar(ind-0.5*width, -qLossPipeSolarLoop, width, color='#CC0000',bottom=-(qSolarToTes))
        barImbNeg     = plot.bar(ind-0.5*width, imbNeg, width, color='k',bottom=-(qSolarToTes+qLossPipeSolarLoop))

        plot.set_ylabel('$Q$ $[kWh]$',size=20)
#        plot.set_ylabel('',size=10)
        
        box = plot.get_position()        
        plot.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        plot.set_title('Solar monthly energy balance',size=20)
        plot.set_xticks(ind)
        plot.set_xticklabels(('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Oct', 'Nov', 'Dec','Year/10'))                       
        plot.legend( (bar1[0], bar2[0],bar3[0],barImbNeg[0]),\
        ('Collector to system', 'Collector to storage','pipe losses','Imbalance'),\
        bbox_to_anchor=(1.05,1),loc=2, borderaxespad=0.,fontsize=10)
        
        self.nameMonthlyColEnergyPlotPdf = 'colEnergyMonthly.pdf'
        self.nameMonthlyColEnergyPlotPdfWithPath = '%s\%s' % (self.outputPath,self.nameMonthlyColEnergyPlotPdf)

        plt.xlim([-0.5,12.5])
        
        plt.savefig(self.nameMonthlyColEnergyPlotPdfWithPath)
        
        plt.close()

    def plotPelFile(self):        
        
        var = []
        pumps = self.pumpHPsink + self.pumpHPsource +self.pumpSolar + self.pumpSH + self.pumpDHW
        
        var.append(self.qWcpHP)
        var.append(self.qAuxHeaterTotal)
        var.append(self.pElController)
        var.append(pumps)
        var.append(self.pElVentilatorHP)
        var.append(self.pElPenalty)
        
        myTitle = "Total Electricity consumption" 
        labels = 'HP Compressor', 'Backup heating', 'Controllers', 'Pumps','HP ventilator', 'Penalty'

        self.namePElPdf = self.plot.plotPie(var,labels,myTitle,"PEl")

    def plotSPFMonthly(self,printData=False):
        

        yearlyFactor = self.yearSPFhps
        
#        var13 = self.SPFhps.copy()
#        var13.resize(13)
#        var13[12] = self.yearSPFhps

        if (self.SPFhps==self.SPFhpsNoCool).all():
            self.nameSpfPdf = self.plot.plotMonthly(self.SPFhps,"$SPF_{SHP}$","SPFMonthly",yearlyFactor,useYearlyFactorAsValue=True,printData=printData)
        else:

            legend = ["$SPF_{SHP}$","$SPF_{SHP,NoCool}$"]

            spf = num.append(self.SPFhps,self.yearSPFhps)

            spfNoCool = num.append(self.SPFhpsNoCool,self.yearSPFhpsNoCool)

            yearlyFactor = 1

            self.nameSpfPdf = self.plot.plotMonthly2Bar(spf, spfNoCool, legend, "$SPF_{SHP}$", "SPFMonthly", yearlyFactor)

            self.nameSpfNoCoolPdf = self.plot.plotMonthly(self.SPFhps,"$SPF^{heatOnly}_{SHP}$","SPFNoCoolMonthly",self.yearSPFhps,useYearlyFactorAsValue=True,printData=printData)

            self.nameSpfCoolPdf = self.plot.plotMonthly(self.SPFhpsNoCool,"$SPF^{HC}_{SHP}$","SPFCoolMonthly",self.yearSPFhpsNoCool,useYearlyFactorAsValue=True,printData=printData)

    def plotCOPMonthly(self,printData=False):
        
        yearlyFactor = self.yearCOP
                
        self.nameCopPdf = self.plot.plotMonthly(self.SPFhp,"$SPF_{HP}$","COPMonthly",yearlyFactor,useYearlyFactorAsValue=True,printData=printData)

    def plotPelBalanceFile(self,printData=False):        
        
        var  = []
               
        pumps = self.pumpHPsink + self.pumpHPsource +self.pumpSolar + self.pumpSH + self.pumpDHW
        
        var.append(self.qWcpHP)
                
        if(sum(self.pElVentilatorHP)>0.):
            legends = 'HP Compressor','HP ventilator', 'Backup heating', 'Controllers', 'Pumps', 'Penalty'
            var.append(self.pElVentilatorHP)
        else:
            legends = 'HP Compressor', 'Backup heating', 'Controllers', 'Pumps', 'Penalty'

        var.append(self.qAuxHeaterTotal)
        var.append(self.pElController)
        var.append(pumps)
        var.append(self.pElPenalty)

        inVar  = var
        outVar = []

#        print "QCompressor and backup"
#        print self.qWcpHP
#        print self.qAuxHeaterTotal
        
        self.namePElMonthlyPdf = self.plot.plotMonthlyBalance(inVar,outVar,legends,"Energy Flows","PElMonthly","kWh",yearlyFactor=10,useYear=True,printImb=False,printData=printData)


    #############################################
    # Section for Latex tables
    #############################################

    def addLatexWeatherData(self):

        caption =  "Weather data"
        sizeBox = 8
        
        names = ["", "I_{hor}","I_{T}","I_{hor}","I_{T}"]

        units = [ "", "[kWh/m^2]","[kWh/m^2]","[MWh]","[MWh]"]
        label = "weatherTable"        

        lines = ""

        for i in range(12):
                        
            line = "%s & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i+1),\
            self.iTHorizontalkWPerM2[i],self.iTColkWPerM2[i],self.iTHorizontalkWPerM2[i]*self.Acol/1000.,self.iTColkWPerM2[i]*self.Acol/1000.)
            lines = lines + line
        
        line="\\hline\n" ; lines = lines + line 
        line = "& %.1f & %.1f & %.1f & %.1f\\\\ \n" % (sum(self.iTHorizontalkWPerM2),sum(self.iTColkWPerM2),sum(self.iTHorizontalkWPerM2)*self.Acol/1000.,sum(self.iTColkWPerM2)*self.Acol/1000.)            
        
        lines = lines + line 
        
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)
        
    def addLatexShDemand(self):
        
        caption =  "Comparison between $Q_{use}$ and $Q_{demand}$ for space heating"
        sizeBox = 8
        
        names = ["", "Q_{use}","Q_{demand}","Q_{diff}", "Q_{pen}"]

        units = [ "", "[kWh]","[kWh]","[kWh]","[kWh]"]
        label = "QuseTable"        

        lines = ""

        for i in range(12):
                        
            line = "%s & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i+1),self.qSH[i],self.qDemandSh[i],self.qDemandSh[i]-self.qUseSh[i],self.pElShPenalty[i])
            lines = lines + line
        
        symbol = "\%"
        line="\\hline\n" ; lines = lines + line 
        line = "& %.1f & %.1f & %.1f & %.1f (%.1f%s)\\\\ \n" % (sum(self.qUseSh),sum(self.qDemandSh), sum(self.qDemandSh)-sum(self.qUseSh),sum(self.pElShPenalty),100.*sum(self.pElShPenalty)/sum(self.qUseSh),symbol)
            
        lines = lines + line 
                
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)

    def addLatexDhwDemand(self):
        
        caption =  "Comparison between $Q_{use}$ and $Q_{demand}$ for DHW"
        sizeBox = 8
        
        names = ["", "Q_{use}","Q_{demand}","Q_{diff}", "Q_{pen}"]

        units = [ "", "[kWh]","[kWh]","[kWh]","[kWh]"]
        label = "QuseTable"        

        lines = ""

        for i in range(12):
                        
            line = "%s & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i+1),self.qUseDhw[i],self.qDemandDhw[i],self.qDemandDhw[i]-self.qUseDhw[i],self.pElDhwPenalty[i])
            lines = lines + line
        
        line="\\hline\n" ; lines = lines + line 
        symbol ="\%"
        line = "& %.1f & %.1f & %.1f & %.1f (%.1f%s)\\\\ \n" % (sum(self.qUseDhw),sum(self.qDemandDhw), sum(self.qDemandDhw)-sum(self.qUseDhw),sum(self.pElDhwPenalty),100.*sum(self.pElDhwPenalty)/sum(self.qUseDhw),symbol)
            
        lines = lines + line 
                
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)
        
    def addLatexHeatDemand(self):

        caption =  "Comparison between $Q_{use}$ and $Q_{demand}$ for total heating load (sh+dhw)"
        sizeBox = 8                
        
        names = ["", "Q_{use}","Q_{use}","Q_{diff}", "Q_{pen}"]

        units = [ "", "[kWh]","[kWh]","[kWh]","[kWh]"]
        label = "QuseTable"        

        lines = ""

        for i in range(12):
                        
            line = "%s & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i+1),self.qUse[i],self.qDemand[i],self.qDemand[i]-self.qUse[i],self.pElPenalty[i])
            lines = lines + line
        
        line="\\hline\n" ; lines = lines + line 
        line = "& %.1f & %.1f & %.1f & %.1f\\\\ \n" % (sum(self.qUse),sum(self.qDemand), sum(self.qDemand)-sum(self.qUse),sum(self.pElPenalty))
            
        lines = lines + line 
                
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)

    def addTablePumpWorkingHours(self):
    
        caption =  "Number of operating hours for heat pump, collector and space heating loop"
        sizeBox = 12
        
        names = ["", "Collector","Heat Pump","hp_{dhw}", "hp_{sh}","Building","DHW"]

        units = [ "", "[h]","[h]","[h]","[h]","[h]","[h]"]
        label = "hoursTable"        


        lines = ""

        for i in range(12):
                        
            line = "%s & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i+1),self.onOffPumpCol[i],self.onOffPumpHp[i],self.onOffPumpHpDhw[i],self.onOffPumpHpSh[i],self.onOffPumpSh[i],self.onOffPumpDhw[i])
            lines = lines + line
        
        line="\\hline\n" ; lines = lines + line 
        line = "& %.1f & %.1f & %.1f& %.1f & %.1f & %.1f\\\\ \n" % (sum(self.onOffPumpCol),sum(self.onOffPumpHp),sum(self.onOffPumpHpDhw),sum(self.onOffPumpHpSh),sum(self.onOffPumpSh),sum(self.onOffPumpDhw))
            
        lines = lines + line 
                
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)

    def addLatexGlobalBalance(self):
        
        lines = ""
        
        line="\\begin{table}[!ht]\n" ; lines = lines + line  
        line="\\begin{small}\n" ; lines = lines + line  
        line="\\caption{Global energy balance.The imbalance is obtained from $Imb =Q_{solS}+Q_{evap,hp}+Q_{wcp,hp}+Q_{aux}+Q_{pump,in}-\
        Q_{L,p}-Q_{L,tnk}-Q_{Lcon,tnk}-Q_{L,hp}-Q_{dhw}-Q_{sh}$.The yearly percentage of  $Imb$ is \
        calculated respect to the yearly $Q_{use}$}\n" ; lines = lines + line   
#        line="\\vspace{-1cm}\n" ; lines = lines + line  
        line="\\begin{center}\n" ; lines = lines + line  
        line="\\resizebox{14cm}{!} \n" ; lines = lines + line
        line="{\n" ; lines = lines + line
        line="\\begin{tabular}{l | c c c c c c c c c c c c c} \n" ; lines = lines + line  
        line="\\hline \n" ; lines = lines + line  
        line="\\hline\n" ; lines = lines + line          
        line=" & $Q_{solS}$ & $Q_{aux}^{heater}$ & $Q_{evap,hp}$ &   $Q_{el,hp}$ &   $Q_{hp,aux}$ &  $Q_{L,pipe}$  & $Q_{L,tnk}$ & $Q_{Lcon,tnk}$ & $Q_{L,hp}$ & $Q_{DHW}$ & $Q_{sh}$ & $Imb$ & $P_{el,pump+con}$\\\\ \n"  
        lines = lines + line
        line="      &[kWh] & [kWh]   & [kWh]  &[kWh]  &  [kWh]&  [kWh]&  [kWh] &  [kWh]      &[kWh]  & [kWh]       &[kWh] &[kWh]    \\\\ \n"                 
        lines = lines + line
        line="\\hline\n" ; lines = lines + line    

        Imb = 0.0
        
        for i in range(12):
                    
            auxHeater = self.qAuxHeaterTotal[i]
            
            if(sum(self.qSolarToTnkBrine)>1e-10):
                bal = self.qSolarToSystem[i] + self.qWcpHP[i] +auxHeater +self.PElTotalDis[i]*self.percentageOfPumpToHeat - self.qLossPipeSystem[i] - self.qLossTes[i] - self.qLossConTnk[i]-self.qLossHp[i]- self.qDHW[i] - self.qSH[i]
            else:
                bal = self.qSolarToSystem[i] + self.qEvapHP[i] + self.qWcpHP[i] +auxHeater +self.PElTotalDis[i]*self.percentageOfPumpToHeat - self.qLossPipeSystem[i] - self.qLossTes[i] - self.qLossConTnk[i]-self.qLossHp[i]- self.qDHW[i] - self.qSH[i]
                
            Imb = bal + Imb
            
            
            line = "%s & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i+1),self.qSolarToSystem[i],self.qAuxHeaterTotal[i]-self.qAuxHeaterHp[i],self.qEvapHP[i], \
            self.qWcpHP[i],self.qAuxHeaterHp[i],self.qLossPipeSystem[i],self.qLossTes[i],self.qLossConTnk[i],self.qLossHp[i],self.qDHW[i],self.qSH[i],bal,self.PElTotal[i])
            lines = lines + line
        
        line="\\hline\n" ; lines = lines + line 
        line = "& %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (sum(self.qSolarToSystem),sum(self.qAuxHeaterTotal)-sum(self.qAuxHeaterHp),sum(self.qEvapHP), \
            sum(self.qWcpHP),sum(self.qAuxHeaterHp),sum(self.qLossPipeSystem),sum(self.qLossTes),sum(self.qLossConTnk),sum(self.qLossHp),sum(self.qDHW),sum(self.qSH),Imb,sum(self.PElTotal))
            
        lines = lines + line       
        
        symbol = "\%"
        line="\\hline\n" ; lines = lines + line    
        if(self.existSolarLoop):
            line="\\textbf{$COP_{t,sol}$}& \\textbf{%.2f} %s \\\\ \n" % (self.yearCOPtSolar,symbol); lines = lines + line 
            line="\\textbf{$f_{s}$}& \\textbf{%.2f} %s \\\\ \n" % (self.yearFSolar,symbol); lines = lines + line
        line="$SPF$& %.2f \\\\ \n" % (self.yearSPFhps); lines = lines + line         
        line="\\textbf{$SPF_{pen}$}& \\textbf{%.2f} \\\\ \n" % (self.yearSPFhpsPen); lines = lines + line         
        line="$SPF_{dis}$& %.2f \\\\ \n" % (self.yearSPFhpsWithDis); lines = lines + line   
        line="\\textbf{$SPF_{dis,pen}$}& %.2f \\\\ \n" % (self.yearSPFhpsWithDisPen); lines = lines + line   
        line="\\textbf{$Imb$}& %.2f %s\\\\ \n" % (Imb*100/(sum(self.qUse)+1e-30),symbol); lines = lines + line 
                    
        line="\\hline\n" ; lines = lines + line  
        line="\\hline\n" ; lines = lines + line          
        line="\\end{tabular}\n" ; lines = lines + line 
        line="}\n" ; lines = lines + line
        line="\\label{GlobalTable}\n" ; lines = lines + line  
        line="\\end{center}\n" ; lines = lines + line  
        line="\\end{small}\n" ; lines = lines + line  
        line="\\end{table}\n" ; lines = lines + line  
        
        return lines

           # TODO : This function uses qGhx, so it is too specific. Change that

    def addLatexHeatPumpData(self):

        caption = "Heat pump data"
        names = ["", "Q_{evap}", "W_{cp}", "Q_{cond}", "Q_{aux,hp}", "Imb"]
        units = ["", "kWh", "kWh", "kWh", "kWh", "kWh"]

        lines = ""
        sumImb = 0.0

        # ERASE WHEN READED PROPERLY

        for i in range(12):
            imb = self.qEvapHP[i] + self.qWcpHP[i] + self.qAuxHeaterHp[i] - self.qCondHP[i]
            sumImb = sumImb + imb
            line = "%s & %.1f & %.1f & %.1f  & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i + 1), \
                                                                              self.qEvapHP[i],self.qWcpHP[i], \
                                                                              self.qAuxHeaterHp[i],self.qCondHP[i],imb)
            lines = lines + line

        line = "\\hline\n";
        lines = lines + line

        line = "Year & %.1f & %.1f & %.1f & %.1f & %.1f\\\\ \n" % ( \
            sum(self.qEvapHP), sum(self.qWcpHP),sum(self.qAuxHeaterHp),sum(self.qCondHP),sumImb)

        lines = lines + line


        line="\\textbf{$COP_{hp}$}& \\textbf{%.2f}  \\\\ \n" % (self.yearCOP); lines = lines + line
        line="\\textbf{$SPF_{hp}$}& \\textbf{%.2f} \\\\ \n" % (self.yearSPFhp); lines = lines + line
        line="\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (sumImb*100/(sum(self.qCondHP)+1e-20),self.perCent); lines = lines + line

        label = "hpTable"
        sizeBox = 10
        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)


    def addLatexSecundaryLoopData(self):

        caption = "Heat pump source and sink energy balance.The imbalance is obtained from $Imb = Q_{cond} -Q_{hpToTes}+Q_{TesToSh}+Q_{aux}-Q_{p,Loss}-Q_{SH}$.The yearly percentage of  $Imb$ is \
        calculated respect to the yearly $Q_{use}$"
        sizeBox = 12

        names = ["", "Q_{HPcond}", "Q_{Tes}^{fromHp}", "Q_{TesToSH}", "Q_{pipeL}^{HPsink}", "Q_{pipeL}^{SH}", "Q_{radFloor}","Imb"]

        units = ["", "kWh", "kWh", "kWh", "kWh", "kWh", "kWh", "kWh", "kWh"]
        label = "Hp2LoopTable"
        lines = ""

        Imb = 0.0

        for i in range(12):
            bal = self.qCondHP[i] - (self.qTesDhwFromHp[i] + self.qTesShFromHp[i]) + self.qOutFromTesToSH[i] - (
                        self.qPipeLossHPSink[i] + self.qPipeLossSH[i]) - self.qRadiator[i]

            Imb = bal + Imb

            line = "%s & %.1f & %.1f & %.1f & %.1f  & %.1f & %.1f   & %.1f \\\\ \n" % (
            utils.getMonthKey(i + 1), self.qCondHP[i], \
            self.qTesDhwFromHp[i] + self.qTesShFromHp[i], self.qOutFromTesToSH[i], self.qPipeLossHPSink[i],
            self.qPipeLossSH[i], self.qRadiator[i], bal)

            lines = lines + line

        line = "\\hline\n";
        lines = lines + line
        line = " & %.1f & %.1f  & %.1f  & %.1f & %.1f & %.1f & %.1f  \\\\ \n" % (sum(self.qCondHP), \
                                                                                        sum(self.qTesDhwFromHp) + sum(
                                                                                            self.qTesShFromHp),
                                                                                        sum(self.qOutFromTesToSH),
                                                                                        sum(self.qPipeLossHPSink),
                                                                                        sum(self.qPipeLossSH),
                                                                                        sum(self.qRadiator),Imb)
        lines = lines + line

        symbol = "\%"
        line = "\\hline\n";
        lines = lines + line

        line = "\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (Imb * 100 / (sum(self.qUse) + 1e-20), symbol);

        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)

    def addLatexSolarData(self):
        
        if(self.parallelSystem):
            return self.addLatexSolarDataParallel()
        else:
            return self.addLatexSolarDataSerial()

    def addLatexSolarDataSerial(self):

        # remade because I change the concept. Now qSolarToTes is not energy to the Tes from solar but at collector level, therefore without pipe losses
        # Now qSolarToTes is qTesFromSolar

        lines = ""
        #
        line = "\\begin{table}[!ht]\n";
        lines = lines + line
        line = "\\begin{small}\n";
        lines = lines + line
        line = "\\caption{Solar loop energy balance (serial).The imbalance is obtained from $Imb = Q_{col-sys} - Q_{tnk} - Q_{tnk-PCM} - \
           Q_{L,p} - Q_{col,hp} $ where $Q_{L,p} = Q_{intS} + Q_{extS}$ .The yearly percentage of  $Imb$ is \
           calculated respect to the yearly $Q_{use}$. IN this case thre will be an error because is it very difficult to know the pipe losses due to collector operation in serial mode.\
           $Q_{cond}$ is a part of $Q_{col-sys}$ so $f_{cond}$ is a gain fraction of $Q_{col-sys}$. $Q_{Amb}$ are gains from ambient and are calculatet as\
           $Q_{Amb}$ = $Q_{col-sys}$ - $Q_{rad}$ - $Q_{cond}$. If $Q_{Amb}$ is positive, $f_{amb}$ is a fraction of $Q_{col-sys}$. }\n";
        lines = lines + line
        #        line="\\vspace{-1cm}\n" ; lines = lines + line
        line = "\\begin{center}\n";
        lines = lines + line
        line = "\\resizebox{15cm}{!} \n";
        lines = lines + line
        line = "{\n";
        lines = lines + line
        line = "\\begin{tabular}{l | c c c c c c c c c c c c c c c c c c} \n";
        lines = lines + line
        line = "\\hline \n";
        lines = lines + line
        line = "\\hline\n";
        lines = lines + line
        line = "Month & $H_{o}$ & $H_{It}$ & $Q_{sol}$ & $Q_{col-sys}$ &  $Q_{cond}$ &  $f_{cond}$ &  $Q_{Amb}$ &  $f_{amb}$ &  $Q_{tnk}$ & $Q_{Pcm}$ & $Q_{col,hp}$ &  $\eta$&  $Q_{L,p}$ & $f_s$ & $Q_{use}$ & $P_{el,p}$ & $P_{el,control}$ & Balance \\\\ \n";
        lines = lines + line
        line = "& [kWh/m$^2$] &  [kWh/m$^2$] &  [kWh] &  [kWh]  &  [kWh]  &  [\\%]  &  [kWh]  &  [\\%]  & [kWh] &   [kWh] &     [kWh] & [-] &   [kWh] &      [\\%]& [kWh] & [kWh] & [kWh] &   [kWh] \\\\ \n";
        lines = lines + line

        line = "\\hline \n";
        lines = lines + line

        # TABLE FOR SOLAR LOOP
        Imb = 0.0
        for i in range(12):
            #            imb = self.qSunToCol[i] - self.qLossCol[i] - self.qLossPipeSolarLoop[i] - self.qTesFromSolar[i] - self.qPcmFromSolar[i]- self.qEvapHpFromSolar[i]
            #            imb = self.qSolarToSystem[i] - self.qLossPipeSolarLoop[i] - self.qTesFromSolar[i] - self.qPcmFromSolar[i]- self.qEvapHpFromSolar[i]
            imb = self.qSolarToSystem[i] - self.qLossPrimaryLoop[i] - self.qTesFromSolar[i] - self.qPcmFromSolar[i] - self.qEvapHpFromSolar[i]

            Imb = imb + Imb

            line = "%s & %.2f & %.2f & %.2f & %.2f & %.2f  & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f \\\\ \n" % (
                utils.getMonthKey(i + 1), \
                self.qIrradHor[i], self.qIrradTilt[i], self.qSunToCol[i], self.qSolarToSystem[i], self.qSolarCond[i],
                self.fcondsolar[i], max(self.qAmbient[i], 0), max(self.fambsolar[i], 0.), self.qTesFromSolar[i],
                self.qPcmFromSolar[i], self.qEvapHpFromSolar[i], self.etaCol[i], \
                self.qLossPrimaryLoop[i], self.fSolar[i], self.qUse[i], self.pumpSolar[i], self.pElControllerSolar[i],
                imb)
            lines = lines + line

        line = "\\hline\n";
        lines = lines + line
        line = "& %.2f & %.2f & %.2f & %.2f & %.2f  & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f & %.2f\\\\ \n" % \
               (sum(self.qIrradHor), sum(self.qIrradTilt), sum(self.qSunToCol), sum(self.qSolarToSystem),
                sum(self.qSolarCond), 100 / sum(self.qColHeatGain) * sum(self.qSolarCond), sum(self.qAmbient),
                100 / sum(self.qColHeatGain) * sum(self.qAmbient), sum(self.qTesFromSolar), sum(self.qPcmFromSolar),
                sum(self.qEvapHpFromSolar), self.yearEta, \
                sum(self.qLossPrimaryLoop), self.yearFSolar, sum(self.qUse), sum(self.pumpSolar),
                sum(self.pElControllerSolar), Imb)
        lines = lines + line
        line = "\\hline\n";
        lines = lines + line
        symbol = "\%"
        line = "\\textbf{$COP_t$}& \\textbf{%.2f} %s \\\\ \n" % (self.yearCOPtSolar, symbol);
        lines = lines + line
        #        line="\\textbf{$COP_e$}& \\textbf{%.2f} %s \\\\ \n" % (self.yearCOPeSolar,symbol); lines = lines + line
        line = "\\textbf{$f_{s}$}& \\textbf{%.2f} %s \\\\ \n" % (self.yearFSolar, symbol);
        lines = lines + line
        try:
            line = "\\textbf{$Imb$}& \\textbf{%.2f} %s & ($Q_{use}$)\\\\ \n" % (
                100. * Imb / (sum(self.qUse)), symbol);
            lines = lines + line
            #            line="\\textbf{$Imb$}& \\textbf{%.2f} %s & ($S_{Sol}$)\\\\ \n" % (100.*Imb/(sum(self.qSolarToTes)),symbol); lines = lines + line
            line = "\\textbf{$Imb$}& \\textbf{%.2f} %s & ($Q_{SolS}$)\\\\ \n" % (
                100. * Imb / (sum(self.qSolarToSystem)), symbol);
            lines = lines + line
        except:
            pass

        line = "\\hline\n";
        lines = lines + line
        line = "\\hline\n";
        lines = lines + line
        line = "\\end{tabular}\n";
        lines = lines + line
        line = "}\n";
        lines = lines + line
        line = "\\label{solarTable}\n";
        lines = lines + line
        line = "\\end{center}\n";
        lines = lines + line
        line = "\\end{small}\n";
        lines = lines + line
        line = "\\end{table}\n";
        lines = lines + line

        return lines

    def addLatexSolarDataParallel(self):
         
        lines = ""                                
#        
        line="\\begin{table}[!ht]\n" ; lines = lines + line  
        line="\\begin{small}\n" ; lines = lines + line  
        line="\\caption{Solar loop energy balance (parallel).The imbalance is obtained from $Imb = Q_{col-sys} - Q_{tnk} - Q_{tnk-bine}\
        Q_{L,p}$ where $Q_{L,p} = Q_{intS} + Q_{extS}$.The yearly percentage of  $Imb$ is \
        calculated respect to the yearly $Q_{use}$}\n" ; lines = lines + line          
#        line="\\vspace{-1cm}\n" ; lines = lines + line  
        line="\\begin{center}\n" ; lines = lines + line  
        line="\\resizebox{15cm}{!} \n" ; lines = lines + line
        line="{\n" ; lines = lines + line
        line="\\begin{tabular}{l | c c  c  c  c   c c c c} \n" ; lines = lines + line  
        line="\\hline \n" ; lines = lines + line  
        line="\\hline\n" ; lines = lines + line  
        line="Month & $I_{T}$ & $Q_{sol-sys}$ &   $Q_{col-sys}$ &  $Q_{tnk}$ & $Q_{Brine,Pcm}$ &  $\eta$&  $Q_{L,p}$ & $f_s$ & Balance \\\\ \n" ; lines = lines + line  
        line="&  $[kWh/m^2]$&  $[kWh/m^2]$  &  [kWh]  & [kWh] &   [kWh]  & [-] &   [kWh] &      [\\%] &  [kWh] \\\\ \n" ; lines = lines + line  

        line="\\hline \n" ; lines = lines + line
            
        # TABLE FOR SOLAR LOOP
        Imb = 0.0
        for i in range(12):
                                    
            imb = self.qSolarToSystem[i]- self.qLossPipeSolarLoop[i] - self.qSolarToTes[i] - self.qSolarToTnkBrine[i] - self.qSolarToIce[i]                  
            Imb = imb + Imb
            
            line = "%s & %.2f & %.2f & %.2f  & %.2f & %.2f & %.2f & %.2f & %.2f& %.2f  \\\\ \n" % (utils.getMonthKey(i+1), \
            self.iTColkWPerM2[i],self.qSolarToSystemPerM2[i],self.qSolarToSystem[i],self.qSolarToTes[i],self.qSolarToTnkBrine[i]+self.qSolarToIce[i],self.etaCol[i], \
            self.qLossPipeSolarLoop[i],self.fSolar[i],imb)
            lines = lines + line 
            
        line="\\hline\n" ; lines = lines + line  
        line = " & %.2f & %.2f & %.2f  & %.2f  & %.2f & %.2f & %.2f & %.2f & %.2f\\\\ \n" % \
        (sum(self.iTColkWPerM2),sum(self.qSolarToSystemPerM2),sum(self.qSolarToSystem),sum(self.qSolarToTes),sum(self.qSolarToTnkBrine)+sum(self.qSolarToIce),self.yearEta, \
        sum(self.qLossPipeSolarLoop),self.yearFSolar,Imb)
        lines = lines + line 
        line="\\hline\n" ; lines = lines + line  
        symbol = "\%"
        line="\\textbf{$COP_t$}& \\textbf{%.2f} %s \\\\ \n" % (self.yearCOPtSolar,symbol); lines = lines + line  
        line="\\textbf{$f_{s}$}& \\textbf{%.2f} %s \\\\ \n" % (self.yearFSolar,symbol); lines = lines + line 
        try:
            line="\\textbf{$Imb$}& \\textbf{%.2f} %s & ($Q_{use}$)\\\\ \n" % (100.*Imb/(sum(self.qUse)),symbol); lines = lines + line 
            line="\\textbf{$Imb$}& \\textbf{%.2f} %s & ($Q_{SolS}$)\\\\ \n" % (100.*Imb/(sum(self.qSolarToSystem)),symbol); lines = lines + line 
        except:
            pass
        
        line="\\hline\n" ; lines = lines + line  
        line="\\hline\n" ; lines = lines + line          
        line="\\end{tabular}\n" ; lines = lines + line  
        line="}\n" ; lines = lines + line
        line="\\label{solarTable}\n" ; lines = lines + line  
        line="\\end{center}\n" ; lines = lines + line  
        line="\\end{small}\n" ; lines = lines + line  
        line="\\end{table}\n" ; lines = lines + line               
        
        return lines

    def addLatexStorageDataDhwOnly(self):
        
        caption =  "Storage Tes for DHW."
        sizeBox = 12
        names = [ "","Q_{sol}^{tnk}","Q_{hp}","Q_{aux,El}","Q_{in}^{tnk}","Q^{tnk}_{DHW}","Q^{tnk}_{loss}","Q_{loss,pipe}","Q_{acum}","Imb","Q_{dhw,use}"]

        units = [ "", "[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]"]
        label = "DhwStorageTable"        

        lines = ""

        Imb = 0.0
        sumIn = 0.0
        for i in range(12):
            
            intoTes = self.qDhwTesFromElRot[i] + self.qDhwTesFromHp[i]+ self.qDhwTesFromSolar[i]
            outTes  = self.qDhwTesAcum[i] + self.qLossDhwTes[i] + self.qOutFromDhwTesToDHW[i]+self.qOutFromDhwTesCirculation[i]
            
            sumIn = sumIn + intoTes
            imb = intoTes-outTes            
            Imb  = Imb + imb
#            self.qOutFromDhwTesToDHW[i]
#            qOutFromTesToDHW[i]
            line = "%s  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f& %.1f& %.1f & %.1f \\\\ \n" % (utils.getMonthKey(i+1),self.qDhwTesFromSolar[i], \
            self.qDhwTesFromHp[i],self.qDhwTesFromElRot[i],intoTes,self.qOutFromDhwTesToDHW[i],self.qLossDhwTes[i],self.qOutFromDhwTesCirculation[i],self.qDhwTesAcum[i],imb,self.qDHW[i])            
            
            lines = lines + line
            
        
        line="\\hline\n" ; lines = lines + line  
        line = "Year & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f& %.1f& %.1f & %.1f \\\\ \n" % (sum(self.qDhwTesFromSolar),\
        sum(self.qDhwTesFromHp),sum(self.qAuxHeaterDhwTes),sumIn,sum(self.qOutFromDhwTesToDHW),sum(self.qLossDhwTes),sum(self.qOutFromDhwTesCirculation),sum(self.qDhwTesAcum),Imb,sum(self.qDHW))                        
        
        lines = lines + line              

        symbol = "\%"
        line="\\hline\n" ; lines = lines + line      
        line="\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100.*Imb/(sum(self.qDHW)+1e-30),symbol); lines = lines + line         
                
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)

    def addLatexStorageDataShOnly(self):
        
        caption =  "Storage Tes for SH."
        sizeBox = 12
        names = [ "","Q^{hp}","Q_{in}^{tnk}","Q^{tnk}_{out}","Q^{tnk}_{loss}","Q^{tnk}_{loss,con}","Imb","Q_{sh,use}"]

        units = [ "", "[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]"]
        label = "ShStorageTable"        


        lines = ""

        Imb = 0.0
        for i in range(12):
                        
            
            imb = self.qTesShFromHp[i] -self.qLossTesSh[i]- self.qLossConTnkSh[i]-self.qOutFromTesToSH[i]
            Imb  = Imb + imb
            
            line = "%s  & %.1f  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\ \n" % (utils.getMonthKey(i+1), \
            self.qTesShFromHp[i],self.qTesShFromHp[i],self.qOutFromTesToSH[i],self.qLossTesSh[i],self.qLossConTnkSh[i], \
            imb,self.qSH[i])            
            
            lines = lines + line
            
        
        line="\\hline\n" ; lines = lines + line  
        line = "%s  & %.1f  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\ \n" % (utils.getMonthKey(i+1), \
        sum(self.qTesShFromHp),sum(self.qTesShFromHp),sum(self.qOutFromTesToSH),sum(self.qLossTesSh),sum(self.qLossConTnkSh), \
        Imb,sum(self.qSH))            
        
        lines = lines + line              

        symbol = "\%"
        line="\\hline\n" ; lines = lines + line      
        line="\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100.*Imb/(sum(self.qSH)+1e-30),symbol); lines = lines + line         
                
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)

    def addLatexStorageData(self):
    
        lines = ""
        
        caption =  "Storage summary.The imbalance is obtained from $Imb = Q_{hp-tnk} + Q_{sol-tnk} - \
        Q_{L,tnk} - Q_{out,tnk}$.The yearly percentage of  $Imb$ is \
        calculated respect to the yearly $Q_{use}$"
        sizeBox = 12
                
        names=["","Q_{sol}^{tnk}","Q_{hp}^{tnk}","Q_{hp}^{tnk,sh}","Q_{hp}^{tnk,dhw}","Q_{hp}^{sh}","Q_{ElRot}","P_{el,T}","Q_{in}^{tnk}","Q^{tnk}_{out}",\
        "Q^{tnk}_{loss}","Q^{tnk}_{loss,con}","Imb","Q_{use}","SPF_{s,hp}","SPF^{tnk}_{s,hp}"]
        
        units = [ "","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]"]

        line="\\hline\n" ; lines = lines + line  
        Imb = 0.0
            
        for i in range(12):
            
#            SPFhpsTnk = (self.qTesFromHp[i]+self.qHpToSh[i]+self.qSolarToTes[i])/(self.PElTotal[i]+self.qWcpHP[i]+1e-30)            
#            imb = self.qTesFromHp[i]+ self.qSolarToTes[i]-self.qLossTes[i]- self.qLossConTnk[i]-self.qOutFromTes[i]

            SPFhpsTnk = (self.qTesFromHp[i]+self.qHpToSh[i]+self.qTesFromSolar[i])/(self.PElTotal[i]+self.qWcpHP[i]+1e-30)            
            imb = self.qTesFromHp[i]+ self.qTesFromSolar[i]+self.qTesFromElRot[i]-self.qLossTes[i]- self.qLossConTnk[i]-self.qOutFromTes[i]
            
            Imb  = Imb + imb
            
#            bal = bal + self.qGHX[i] + self.qWcpHP[i] - self.qPipeLossGHX[i] - self.qPipeLossHPSink[i] - self.qTesFromHp[i]            
            line = "%s & %.1f & %.1f  & %.1f & %.1f  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\ \n" % (utils.getMonthKey(i+1),self.qTesFromSolar[i], \
            self.qTesFromHp[i],self.qTesShFromHp[i],self.qTesDhwFromHp[i],self.qHpToSh[i],self.qTesFromElRot[i],self.PElTotal[i],self.qTesFromSolar[i]+self.qTesFromHp[i],self.qOutFromTes[i],self.qLossTes[i],self.qLossConTnk[i], \
            imb,self.qUse[i],self.SPFhps[i],SPFhpsTnk)            
            
            lines = lines + line
            
        yearSPFhpsTnk = (sum(self.qTesFromHp)+sum(self.qTesFromSolar)+sum(self.qHpToSh))/(sum(self.PElTotal)+sum(self.qWcpHP)+1e-30)
        
        line="\\hline\n" ; lines = lines + line  
        line = " & %.1f & %.1f  & %.1f & %.1f  & %.1f & %.1f & %.1f & %.1f& %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f \\\\ \n" % (sum(self.qTesFromSolar), \
        sum(self.qTesFromHp),sum(self.qTesShFromHp),sum(self.qTesDhwFromHp),sum(self.qHpToSh),sum(self.qTesFromElRot),sum(self.PElTotal),sum(self.qTesFromSolar)+sum(self.qTesFromHp),sum(self.qOutFromTes),sum(self.qLossTes), \
        sum(self.qLossConTnk),Imb,sum(self.qUse),self.yearSPFhps,yearSPFhpsTnk); 
        
        lines = lines + line              
        
        symbol = "\%"
        line="\\hline\n" ; lines = lines + line      
        line="\\textbf{$SPF_{hps}$}& \\textbf{%.2f}  \\\\ \n" % (self.yearSPFhps); lines = lines + line  
        line="\\textbf{$SPF^{tnk}_{hps}$}& \\textbf{%.2f} \\\\ \n" % (yearSPFhpsTnk); lines = lines + line 
        line="\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (Imb*100/(sum(self.qUse)+1e-30),symbol); lines = lines + line 
        
        label = "solarAndHPTable"
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)

    def addLatexHeatingFloorTable(self,comment=False):

        lines = ""

        caption = "Heating Floor balance. $Q_{imb} = Q_{fluid}+Q_{acum}-Q_{sh}$"
        if(comment!=False):
            caption = caption +" %s"%comment
            
        sizeBox = 12

        label = "RadFloorTable"

        names = ["", "Q_{fluid}", "Q^{acum}_{floor+fluid}", "Q_{sh}", "Q_{imb}"]
        units = ["[kWh"]

        Imb = 0.0

        for i in range(12):

            imb = self.qRadiator[i]+self.qAcumRadiator[i]-self.qDemandSh[i]

            Imb = Imb + imb

            line = "%s & %.1f & %.1f & %.1f  & %.1f \\\\ \n" % (
            utils.getMonthKey(i + 1), \
            self.qRadiator[i], self.qAcumRadiator[i],self.qDemandSh[i], imb)

            lines = lines + line

        line = "\\hline\n";
        lines = lines + line
        line = " & %.1f & %.1f & %.1f  & %.1f \\\\ \n" % (sum(self.qRadiator),sum(self.qAcumRadiator),sum(self.qDemandSh),Imb)

        lines = lines + line

        symbol = "\%"
        line = "\\hline\n";
        lines = lines + line
        line = "\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100. * Imb / (sum(self.qDemandSh) + 1e-30), symbol);
        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)

    def addLatexBuildingBalanceTable(self):
                
        lines = ""
        
        caption =  "building balance. $Q_{imb} = Q_{sh}+Q_{sol}+Q_{intG}+Q_{cool}+Q_{trns}+Q_{inf}+Q_{ven}+Q_{ground}$"
        sizeBox = 12
        
        label = "buildingBalTable"        
       
        
        names = ["","Q_{Sh}","Q_{sol,gain}","Q_{intG,people}","Q_{intG,eq}","Q_{intG,Light}","Q_{trns,loss}","Q_{inf,loss}",\
        "Q_{ven}^{loss}","Q_{ground,loss}","Q_{acum,bui}","Imb","Q_{module,heat}","Q_{module,cool}","Q_{module}","Q_{def}","Q_{module,acum}"]  
        units  =["","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]","[kWh]"]                 
        
        Imb = 0.0

#        qDemandUsed = self.qDemandSh
        qDemandUsed = self.qUseSh
                          
        for i in range(12):

            pos = qDemandUsed[i] +self.qBuiAcum[i]+self.qBuiSolarGains[i]+self.qBuiIntGainPeople[i]+self.qBuiIntGainEq[i]+self.qBuiIntGainLight[i]

            neg = self.qBuiCool[i]+self.qBuiTransLosses[i]+self.qBuiInfLosses[i]+self.qBuiVentLosses[i]+self.qBuiGroundLosses[i]
            imb = pos+neg            
            
#            print "QDemand:%f qSolar:%f qInt:%f"%(qDemandUsed[i],self.qBuiSolarGains[i],self.qBuiIntGainPeople[i]+self.qBuiIntGainEq[i])
#            print "BUILDING imb:%f pos:%f neg:%f"%(imb,pos,neg)
            
            Imb  = Imb + imb
            
            qDef = self.qDemandSh[i] - self.qRadiator[i]
            
            line = "%s & %.1f & %.1f & %.1f  & %.1f & %.1f  & %.1f  & %.1f& %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f  & %.1f\\\\ \n" % (utils.getMonthKey(i+1),\
            qDemandUsed[i],self.qBuiSolarGains[i],self.qBuiIntGainPeople[i],self.qBuiIntGainEq[i],self.qBuiIntGainLight[i],self.qBuiTransLosses[i],self.qBuiInfLosses[i],self.qBuiVentLosses[i],\
            self.qBuiGroundLosses[i],self.qBuiAcum[i],imb,self.qBuiHeat[i],self.qBuiCool[i],self.qRadiator[i],qDef,self.qAcumRadiator[i])            
            
            lines = lines + line
        
        qDef = sum(self.qDemandSh) - sum(self.qRadiator)
        
        line="\\hline\n" ; lines = lines + line  
        line = " & %.1f & %.1f & %.1f  & %.1f & %.1f  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (sum(qDemandUsed),sum(self.qBuiSolarGains),\
        sum(self.qBuiIntGainPeople),sum(self.qBuiIntGainEq),sum(self.qBuiIntGainLight),sum(self.qBuiTransLosses),sum(self.qBuiInfLosses),sum(self.qBuiVentLosses),\
        sum(self.qBuiGroundLosses),sum(self.qBuiAcum),Imb,sum(self.qBuiHeat),sum(self.qBuiCool),sum(self.qRadiator),qDef,sum(self.qAcumRadiator))            
        
        lines = lines + line              
        
        symbol = "\%"
        line="\\hline\n" ; lines = lines + line      
        line="\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100.*Imb/(sum(self.qDemandSh)+1e-30),symbol); lines = lines + line 
     
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True)

    def addLatexDistributionData(self):
    
            self.addLatexSHLoop()
            self.addLatexSHLoopWoPipes()
            self.addLatexDHWLoop()
            self.addLatexDistributionTable()
        
    def addLatexDistributionTable(self,comment=False):

        caption = "Distribution for DHW and space heating."

        if(comment!=False):
            caption = caption +" %s"%comment

        sizeBox = 12
        names = ["", "Q^{out}_{tnk}", "Q^{hp}_{sh}","Q_{acum,rad}",  "Q^{dhw}_{L,p}", "Q^{sh}_{L,p}", "Q^{dhw}_{use}",
                 "Q^{sh}_{use}", "Q_{use}", "P_{el,sh}", "P_{el,dhw}", "SPF^{dis}_{s,hp}", "Imb"]
        units = ["", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]",
                 "[kWh]"]
        label = "DistributionTable"

        lines = ""

        Imb = 0.0

        if (self.existTesForDwhOnly):
            qPipeLossDHW = num.zeros(12)
        else:
            qPipeLossDHW = self.qPipeLossDHW

        for i in range(12):
            imb = self.qOutFromTes[i] + self.qHpToSh[i] + self.qAcumRadiator[i]\
                  - qPipeLossDHW[i] - self.qPipeLossSH[i] - self.qDHW[i] - self.qSH[i]

            # For distribution we do not have to include self.qOutFromDhwTesCirculation losses because we use qOutTes as source
            Imb = Imb + imb

            line = "%s & %.1f & %.1f  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f& %.1f & %.1f & %.1f & %.1f\\\\ \n" % (
            utils.getMonthKey(i + 1), self.qOutFromTes[i], \
            self.qHpToSh[i], self.qAcumRadiator[i], qPipeLossDHW[i], self.qPipeLossSH[i], self.qDHW[i], self.qSH[i],
            self.qUse[i], self.pumpSH[i], self.pumpDHW[i], self.SPFhpsWithDis[i], imb)

            lines = lines + line

        line = "\\hline\n";
        lines = lines + line

        line = " & %.1f & %.1f & %.1f  & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f\\\\ \n" % (
        sum(self.qOutFromTes), \
        sum(self.qHpToSh), sum(self.qAcumRadiator), sum(qPipeLossDHW), sum(self.qPipeLossSH), sum(self.qDHW),
        sum(self.qSH), sum(self.qUse), \
        sum(self.pumpSH), sum(self.pumpDHW), self.yearSPFhpsWithDis, Imb);
        lines = lines + line

        symbol = "\%"
        line = "\\hline\n";
        lines = lines + line
        line = "\\textbf{$SPF^{dis}_{hps}$}& \\textbf{%.2f}  \\\\ \n" % (self.yearSPFhpsWithDis);
        lines = lines + line
        line = "\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100. * Imb / (sum(self.qUse) + 1e-30), symbol);
        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)
       
    def addLatexSHLoop(self,comment=False):

        caption = "Distribution for space heating."
        if(comment!=False):
            caption = caption +" %s"%comment

        sizeBox = 10
        names = ["", "Q^{tnk}_{sh}", "Q^{hp}_{sh}", "Q_{acum,rad}", "Q^{sh}_{L,p}", "Q^{sh}_{use}", "Imb"]
        units = ["", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]"]
        label = "DistributionTable"
        lines = ""
        Imb = 0.0

        for i in range(12):
            imb = self.qOutFromTesToSH[i] + self.qHpToSh[i] + self.qAcumRadiator[i] - self.qPipeLossSH[i] - self.qSH[i]

            # For distribution we do not have to include self.qOutFromDhwTesCirculation losses because we use qOutTes as source
            Imb = Imb + imb

            line = "%s & %.1f & %.1f  & %.1f  & %.1f & %.1f & %.1f\\\\ \n" % (
            utils.getMonthKey(i + 1), self.qOutFromTesToSH[i], \
            self.qHpToSh[i],  self.qAcumRadiator[i],self.qPipeLossSH[i], self.qSH[i], imb)

            lines = lines + line

        line = "\\hline\n";
        lines = lines + line

        line = "& %.1f & %.1f & %.1f   & %.1f & %.1f & %.1f\\\\ \n" % (sum(self.qOutFromTesToSH), \
                                                                       sum(self.qHpToSh),sum(self.qAcumRadiator), sum(self.qPipeLossSH),
                                                                       sum(self.qSH), Imb)
        lines = lines + line

        symbol = "\%"
        line = "\\hline\n";
        lines = lines + line
        line = "\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100. * Imb / (sum(self.qUse) + 1e-30), symbol);
        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)

    def addLatexDHWLoop(self):

        caption = "Distribution for domestic hot water."
        sizeBox = 10
        names = ["", "Q^{tnk}_{dhw}", "Q^{dhw}_{L,p}", "Q^{dhw}_{use}", "Imb"]
        units = ["", "[kWh]", "[kWh]", "[kWh]", "[kWh]"]
        label = "DistributionTable"
        lines = ""
        Imb = 0.0

        for i in range(12):
            imb = self.qOutFromTesToDHW[i] - self.qPipeLossDHW[i] - self.qDHW[i]

            # For distribution we do not have to include self.qOutFromDhwTesCirculation losses because we use qOutTes as source
            Imb = Imb + imb

            line = "%s & %.1f  & %.1f & %.1f  & %.1f \\\\ \n" % (utils.getMonthKey(i + 1), self.qOutFromTesToDHW[i], \
                                                                 self.qPipeLossDHW[i], self.qDHW[i], imb)

            lines = lines + line

        line = "\\hline\n";
        lines = lines + line

        line = " & %.1f & %.1f  & %.1f  & %.1f \\\\ \n" % (sum(self.qOutFromTesToDHW), \
                                                           sum(self.qPipeLossDHW), sum(self.qDHW), Imb)

        lines = lines + line

        symbol = "\%"
        line = "\\hline\n";
        lines = lines + line
        line = "\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100. * Imb / (sum(self.qUse) + 1e-30), symbol);
        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)

    def addLatexSHLoopWoPipes(self):

        caption = "Distribution for space heating with pipe losses."
        sizeBox = 12
        names = ["", "Q^{fromTes}_{sh}", "Q_{loss}", "Q^{fluid,rad}", "Imb"]
        units = ["[kWh]"]

        label = "ShPipeLosses"
        lines = ""
        Imb = 0.0

        for i in range(12):
            imb = self.qOutFromTesToSH[i] - self.qRadiator[i] - self.qPipeLossSH[i]

            # For distribution we do not have to include self.qOutFromDhwTesCirculation losses because we use qOutTes as source
            Imb = Imb + imb

            line = "%s & %.1f & %.1f  & %.1f & %.1f\\\\ \n" % (utils.getMonthKey(i + 1), self.qOutFromTesToSH[i], \
                                                                     self.qPipeLossSH[i],
                                                                     self.qRadiator[i], imb)

            lines = lines + line

        line = "\\hline\n";
        lines = lines + line

        line = "& %.1f & %.1f & %.1f    & %.1f\\\\ \n" % (sum(self.qOutFromTesToSH), \
                                                                sum(self.qPipeLossSH),
                                                                sum(self.qRadiator), Imb)

        lines = lines + line

        symbol = "\%"
        line = "\\hline\n";
        lines = lines + line
        line = "\\textbf{$Imb$}& \\textbf{%.2f} %s\\\\ \n" % (100. * Imb / (sum(self.qUse) + 1e-30), symbol);
        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)


    def addNomenclature(self):

        lines =""
        
        line="\\section{Nomenclature} \n" ; lines = lines + line 
        line="\\begin{flushleft}\n" ; lines = lines + line 
        line="\\begin{tabular}{p{30pt} p{320pt}}\n" ; lines = lines + line 
        line="$E_{sol}$ & solar heat to collectors \\\\ \n" ; lines = lines + line      
        line="$Q_{solS}$ & solar heat to system \\\\ \n" ; lines = lines + line  
        line="$Q_{L,Col}$ & heat collector losses \\\\ \n" ; lines = lines + line 
        line="$S_{sol}$ & heat solar to Tes \\\\ \n" ; lines = lines + line 
        line="$Q_{wcp,hp}$ & work of heat pump compressor \\\\ \n" ; lines = lines + line
        line="$Q_{pump,in}$ & heat to system introduced for pumps \\\\ \n" ; lines = lines + line
        line="$Q_{L,pipe}$ & heat losses in pipes \\\\ \n" ; lines = lines + line
        line="$Q_{L,tnk}$ & heat losses in storage Tes \\\\ \n" ; lines = lines + line
        line="$Q_{DHW}$ & heat consumption for domestic hot water \\\\ \n" ; lines = lines + line
        line="$Q_{SH}$ & heat consumption for space heating \\\\ \n" ; lines = lines + line
        line="$Imb$ & heat imbalance\\\\ \n" ; lines = lines + line
        line="$P_{e,Total}$ & Electric consumption of pumps\\\ \n" ; lines = lines + line
        line="\\end{tabular} \n" ; lines = lines + line 
        line="\\end{flushleft} \n" ; lines = lines + line 
                               
        return lines

    def addLatexSolarPlot(self):
        
        lines = ""
        
        namePdf = "%s.pdf" % self.nameFSolar.split('.')[0]
        line="\\OneFig{%s}\n" % namePdf ; lines = lines + line  
        line="{Solar fraction}{fSolar}{10}\n" ; lines = lines + line   
        
        return lines
    
    def addLatexBalancePlot(self):
        
        lines = ""
        
        namePdf = "%s.pdf" % self.nameHeatBalance.split('.')[0]
        line="\\OneFig{%s}\n" % namePdf ; lines = lines + line  
        line="{Heat Balance}{bal}{10}\n" ; lines = lines + line   
        
        return lines

    def addLatexStorageComponentData(self):
        pass

    def addTablePumpElectricity(self):

        caption = "Pumps electrical consumption."
        sizeBox = 12
        names = ["", "P^{col}_{el,pu}", "P^{hp,sink}_{el,pu}", "P^{hp,source}_{el,pu}", "P^{dhw}_{el,pu}",
                 "P^{sh}_{el,pu}", "Total"]
        units = ["", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]", "[kWh]"]
        label = "PumpPelTable"

        lines = ""

        Total = 0.0

        for i in range(12):
            total = self.pumpHPsink[i] + self.pumpHPsource[i] + self.pumpSolar[i] + self.pumpSH[i] + self.pumpDHW[i]
            Total = Total + total

            line = "%s & %.1f & %.1f  & %.1f & %.1f & %.1f & %.1f \\\\ \n" % (
            utils.getMonthKey(i + 1), self.pumpSolar[i], \
            self.pumpHPsink[i], self.pumpHPsource[i], self.pumpDHW[i], self.pumpSH[i], total)

            lines = lines + line

        line = "\\hline\n";
        lines = lines + line

        line = " & %.1f & %.1f & %.1f  & %.1f & %.1f & %.1f \\\\ \n" % (sum(self.pumpSolar), \
                                                                        sum(self.pumpHPsink), sum(self.pumpHPsource),
                                                                        sum(self.pumpDHW), sum(self.pumpSH), Total);
        lines = lines + line

        symbol = "\%"
        line = "\\hline\n";
        lines = lines + line

        line = " %s & %.1f & %.1f & %.1f  & %.1f & %.1f & \\\\ \n" % (symbol, 100 * sum(self.pumpSolar) / Total, \
                                                                      100 * sum(self.pumpHPsink) / Total,
                                                                      100 * sum(self.pumpHPsource) / Total,
                                                                      100 * sum(self.pumpDHW) / Total,
                                                                      100 * sum(self.pumpSH) / Total);
        lines = lines + line

        self.doc.addTable(caption, sizeBox, names, units, label, lines, useFormula=True)

    #############################################
    # Latex sections
    #############################################

    def addSectionNomenclature(self):

        lines = self.addNomenclature()
        self.doc.addUserTex(lines)
        self.doc.clearPage()

    def addSectionSystemAnalyses(self):

        self.doc.addSection("System analyses")

        lines = self.addLatexGlobalBalance()
        self.doc.addUserTex(lines)

        self.doc.addPlot(self.namePElPdf, "Electricity consumption of the system.", "Pel", 13)

        self.addTablePumpElectricity()
        self.addTableElectricity()

        lines = self.addLatexBalancePlot()
        self.doc.addUserTex(lines)

        self.doc.addPlot(self.nameMonthlyEnergyPlotPdf, "Monthly energy balance.", "QMonthly", 13)

        self.doc.clearPage()

    def addSectionHeatDemandAndPenalties(self):

        self.doc.addSection("Heat demand and penalties")
        self.addLatexHeatDemand()
        self.addLatexShDemand()
        self.addLatexDhwDemand()
        self.doc.clearPage()

    def addSectionPumpWorkingHours(self):

        self.doc.addSection("Pumps working hours")
        self.addTablePumpWorkingHours()

    def addSectionTes(self):

        self.doc.addSection("Storage")

        if self.useTwoStorages:

            pass
        else:
            self.addLatexStorageComponentData()

            self.addLatexStorageData()

            self.doc.addPlot(self.nameMonthlyTesEnergyPlotPdf, "Storage Tes balance", "balTes", 13)

            if (self.existTesForDwhOnly):
                self.addLatexStorageDataDhwOnly()

        # self.doc.clearPage()

    def addSectionSolarLoop(self):

        self.doc.addSection("Solar Loop")

        lines = self.addLatexSolarData()
        self.doc.addUserTex(lines)

        self.doc.addPlot(self.nameMonthlyColEnergyPlotPdf, "Energy flows in solar thermal system", "solar", 13)

        self.doc.clearPage()

    def addSectionHeatPumpLoop(self):

        self.doc.addSection("Heat pump")
        lines = self.addLatexHeatPumpData()
        self.doc.addUserTex(lines)

        lines = self.addLatexSecundaryLoopData()
        self.doc.addUserTex(lines)

    #############################################
    #Latex pdf and execution
    #############################################

    def executeLatexFile(self):

        self.doc.executeLatexFile(moveToTrnsysLogFile=True, runTwice=True)

    #############################################
    # Outputs
    #############################################

    def createFileTinQEvap(self):

        myGlobalName = '%s-TinEvap.dat' % self.fileName
        myGlobalNameWithPath = '%s\%s' % (self.outputPath, myGlobalName)

        outfile = open(myGlobalNameWithPath, 'w')

        lines = ""

        line = "! tInEvap qEvapAcum\n";
        lines = lines + line
        #
        skyp = 100

        it = 0

        for i in range(len(self.tInEvapSorted)):
            it = it + 1
            if (it == skyp or i == 0):
                line = "%f\t%f\n" % (self.tInEvapSorted[i], self.qEvapAcumSorted[i])
                lines = lines + line
                it = 0

        outfile.writelines(lines)
        outfile.close()

    def createFileWithResults(self):

        myGlobalName = '%s-results.dat' % self.fileName
        myGlobalNameWithPath = '%s\%s' % (self.outputPath, myGlobalName)

        outfile = open(myGlobalNameWithPath, 'w')

        flines = []
        fline = 'DWHUse\t%f\tkWh\n' % (sum(self.qDHW));
        flines.append(fline)
        fline = 'SHUse\t%f\tkWh\n' % (sum(self.qSH));
        flines.append(fline)
        fline = 'LoadUse\t%f\tkWh\n' % (sum(self.qDHW) + sum(self.qSH));
        flines.append(fline)
        fline = 'LoadDemand\t%f\tkWh\n' % (sum(self.qDemand));
        flines.append(fline)
        fline = 'QSolarToColArea\t%f\tkWh \n' % (sum(self.qSunToCol));
        flines.append(fline)
        fline = 'SPFdis\t%f\n' % self.yearSPFhpsWithDis;
        flines.append(fline)
        fline = 'SPF\t%f\n' % self.yearSPFhps;
        flines.append(fline)
        fline = 'SPFdisPen\t%f\n' % self.yearSPFhpsWithDisPen;
        flines.append(fline)
        fline = 'SPFPen\t%f \n' % self.yearSPFhpsPen;
        flines.append(fline)
        fline = 'fSolar\t%f \n' % self.yearFSolar;
        flines.append(fline)

        fline = "SHUseFromTes\t%.2f\n" % (sum(self.qSH) - sum(self.qHpToSh));
        flines.append(fline)
        fline = 'QColToSystem\t%f\tkWh\n' % sum(self.qSolarToSystem);
        flines.append(fline)
        fline = 'QHpToSystem\t%f\tkWh\n' % sum(self.qCondHP);
        flines.append(fline)
        fline = 'QColToTes\t%f\tkWh\n' % sum(self.qSolarToTes);
        flines.append(fline)
        fline = 'QHpToTesDhw\t%f\tkWh\n' % sum(self.qTesDhwFromHp);
        flines.append(fline)
        fline = 'QHpToTesSh\t%f\tkWh\n' % sum(self.qTesShFromHp);
        flines.append(fline)

        fline = 'PelSystemTotal\t%f\tkWh\t(All system electricity without pump heat distribution)\n' % (
                    sum(self.pElTotal) + sum(self.qWcpHP) + sum(self.qAuxHeaterTotal) + sum(self.pElVentilatorHP));
        flines.append(fline)
        fline = 'SystemImbalance\t%.2f\t%s\n' % (self.systemImbalance, "%");
        flines.append(fline)

        fline = 'COPhp\t%f \n' % self.yearCOP;
        flines.append(fline)
        fline = 'COPMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.COPhp[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'SPFPenMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.SPFhps[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'operatingHoursColMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.onOffPumpCol[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'operatingHoursHpMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.onOffPumpHp[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'QColToTesMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.qSolarToTes[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'qTesDhwFromHpMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.qTesDhwFromHp[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'qTesShFromHpMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.qTesShFromHp[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'QSolarToColMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.qSunToCol[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'QDemandMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % self.qDemand[i];
            flines.append(fline)
        fline = '\n';
        flines.append(fline)

        fline = 'QDhwOverQDemandMonthly';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % (self.qDHW[i] / (self.qDemand[i] + 1e-20));
            flines.append(fline)

        fline = '\n';
        flines.append(fline)

        fline = 'TminIceStorage';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % (self.tStoreMonthlyMinPcm[i]);
            flines.append(fline)

        fline = '\n';
        flines.append(fline)

        fline = 'QAuxiliarHeater';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % (self.qAuxHeaterTotal[i]);
            flines.append(fline)

        fline = '\n';
        flines.append(fline)

        fline = 'VRatioIceMax';
        flines.append(fline)

        for i in range(12):
            fline = '\t%f' % (self.massOfIceMonthlyMaxPcm[i]);
            flines.append(fline)

        fline = '\n';
        flines.append(fline)

        flines.append(self.addLinesInCreateFileWithResults)

        outfile.writelines(flines)
        outfile.close()
