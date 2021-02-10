
#!/usr/bin/python

"""
Energy cost calculation class

Author : Daniel Carbonell, Daniel Philippen
Date   : 18-10-2017
ToDo :
"""


import logging

import pytrnsys.report.latexReport as latex
import pytrnsys.utils as utils
from pytrnsys.cost_calculation import economicFunctions as ef

logger = logging.getLogger('root')

class CostCalculation():
    
    def __init__(self):

        self.method="VDI"
        self.unit=1
        self.cleanModeLatex = True

    def setOutputhPathAndFileName(self,path,fileName):
        
        self.outputPath = path
        self.fileName   = fileName

        logger.debug("path:%s name:%s" %(self.outputPath,self.fileName))
        self.doc = latex.LatexReport(self.outputPath,self.fileName)               


    def setGeneralInputs(self,rate,analysPeriod,costElecFix,costEleckWh,increaseElecCost,lifeTime):
        
        
        logger.info("===================SET GENERAL INPUTS========================")
        self.rate = rate
        self.analysPeriod = analysPeriod
        self.costElecFix = costElecFix
        self.costEleckWh = costEleckWh
       
#        self.lifeTime = lifeTime
        self.increaseElecCost = increaseElecCost
       
        logger.debug("rate:%f analysisPeriod:%f"%(self.rate,self.analysPeriod))
        
    def setSystemInputs(self,qDemand,elDemand,totalInvestCost,MaintenanceRate,costResidual,lifeTimeRes):
    
        self.qDemand = qDemand
        self.elDemandTotal = elDemand
        self.totalInvestCost = totalInvestCost
        self.MaintenanceRate = MaintenanceRate
        self.costResidual    = costResidual
        self.lifeTimeResVal = lifeTimeRes

    def calculate(self):
                      
#        self.npvFac = ((1.+self.rate)**self.analysPeriod-1.)/((1.+self.rate)**self.analysPeriod*self.rate)
        self.npvFac = ef.getNPV(self.rate, self.analysPeriod)
        
        self.costElecTotalY = self.costElecFix+self.costElecKwh*self.elDemandTotal  
        
        if(self.rate==self.increaseElecCost): 
            self.npvFacElec = self.lifeTime/(1.+self.rate)
        else:
            self.npvFacElec = 1/(self.rate-self.increaseElecCost)*(1.-((1.+self.increaseElecCost)/(1.+self.rate))**self.analysPeriod)          
     
#        self.priceDynNpv=(1.-((1.+self.increaseElecCost)/(1.+self.rate))**self.analysPeriod)/(self.rate-self.increaseElecCost)     
        self.npvElec = self.costElecTotalY*self.npvFacElec
        self.npvMaintenance = self.MaintenanceRate*self.totalInvestCost*self.npvFac

        logger.debug(self.costElecTotalY,self.npvElec,self.npvMaintenance)
#        raise ValueError("")

        self.discountFromEnd = (1+self.rate)**(-1.*self.analysPeriod)        
        self.resValFactor = (self.lifeTimeResVal-self.analysPeriod)/self.lifeTimeResVal
        
        self.residualValue = (self.costResidual)*self.resValFactor
        self.npvResVal = self.residualValue*self.discountFromEnd
                 
        self.npvSystem = self.totalInvestCost+self.npvElec+self.npvMaintenance-self.npvResVal
        
        logger.debug("npvSystem:%f totalInvestCost :%f npvElec :%f npvMaintenance:%f npvResVal:%f"%(self.npvSystem,self.totalInvestCost,self.npvElec,self.npvMaintenance,self.npvResVal))

        self.annuityFac = ef.getAnnuity(self.rate, self.analysPeriod)
        
        self.annuity = self.annuityFac*self.npvSystem  # Fr.
        
        logger.debug("annuity:%f annuityFac:%f npvSystem:%f"%(self.annuity,self.annuityFac,self.npvSystem))


        self.anToInvCost = self.annuityFac*self.totalInvestCost
        self.anElec = self.annuityFac*self.npvElec
        self.anMaint = self.annuityFac*self.npvMaintenance
        self.anResVal = (-1.)*self.annuityFac*self.npvResVal
        
        logger.debug(" TEST %f %f   "% (self.npvFacElec,self.annuityFac))
        
        self.heatGenCost = self.annuity/self.qDemand  # Fr./kWh    
        self.heatGenCostNpv = self.npvSystem/self.qDemand/self.analysPeriod        

        logger.info("NPV Factor:%f  AnnuityFac:%f  "% (self.npvFac,self.annuityFac))
        logger.info("Heat Generation Cost Annuity:%f NPV:%f"%(self.heatGenCost,self.heatGenCostNpv))
        
    def addTableEconomicAssumptions(self):
        
        caption = "Assumptions for calculation of heat generation costs"
        names = ["","","",""]
        units = None
        sizeBox = 8 
        
        perc = "\%"        
        
        lines = ""
        line = "Rate & %2.1f %s $per$ $annum$\\\\ \n" % (self.rate*100.,perc);lines = lines + line        
        line = "Analysis period & %2.0f $years$\\\\ \n" % (self.analysPeriod);lines = lines + line
        line = "Maintenance & %2.1f %s $of$ $Investment$ $costs$ $per$ $year$ \\\\ \n" % (self.MaintenanceRate*100.,perc);lines = lines + line    
        line = "\\hline \\\\ \n" ; lines = lines + line
#        lines = ""
        line = "Electricity & Fix costs: %2.0f  $Fr.$ $per$ $year$ \\\\ \n" % (self.costElecFix);lines = lines + line        
        line = " & Variable costs:  %2.2f $Fr.$ $per$ $kWh$ \\\\ \n" % (self.costEleckWh);lines = lines + line
        line = "Increase of electricity costs & %2.1f %s $per$ $year$ \\\\ \n" % (self.increaseElecCost*100.,perc);lines = lines + line
        line = "Electricity costs year 1 & %2.0f Fr. in year 1 \\\\ \n" % (self.costElecTotalY);lines = lines + line

        label ="definitionTable"
        
        self.doc.addTable(caption,names,units,label,lines,useFormula=True)

        # def addTable(self, _caption, _names, _units, _label, _linesResults, useFormula=False, addCaptionLines=False):

    def addTableCosts(self,doc,unit=1):
        
        symbol = "$\\%$"
        caption =  "System and Heat generation costs (all values incl. 8%s VAT) " % symbol
        sizeBox = 14                
        
        names = [ "Major Component","Component","Costs","Total Costs"]
        if(unit==1e-3):
            units = [ "","", "[kFr.]","[kFr.]"]
        elif(unit==1):
            units = [ "","", "[Fr.]","[Fr.]"]
        else:
            raise ValueError("unit not found:%f"%unit)
            
        label = "CostsTable"        
        lines = ""      
        symbol = "\%"    
                
        line = " & \\textbf{Total Investment Cost} & & \\textbf{%2.2f} (100%s) \\\\ \n" % (self.totalInvestCost*unit,symbol);lines = lines + line         

        line = "\\hline \\\\ \n" ; lines = lines + line
        line = "\\hline \\\\ \n" ; lines = lines + line
        
        costUnit = " $Fr./a$"
        
        line = "Annuity & Annuity (yearly costs over lifetime)  & & %2.0f% s  \\\\ \n" % (self.annuity,costUnit);lines = lines + line 
        line = " & Share of Investment & & %2.0f%s (%2.0f%s) \\\\ \n" % (self.anToInvCost,costUnit,self.anToInvCost*100./self.annuity,symbol);lines = lines + line 
        line = " & Share of Electricity  & & %2.0f%s (%2.0f%s)\\\\ \n" % (self.anElec,costUnit,self.anElec*100./self.annuity,symbol);lines = lines + line
        line = " & Share of Maintenance & & %2.0f%s (%2.0f%s)\\\\ \n" % (self.anMaint,costUnit,self.anMaint*100./self.annuity,symbol);lines = lines + line        
        line = " & Share of Residual Value & & %2.0f%s (%2.0f%s)\\\\ \n" % (self.anResVal,costUnit,self.anResVal*100./self.annuity,symbol);lines = lines + line      
        
        line = "\\hline \\\\ \n" ; lines = lines + line
        line = "Present Value  & Present Value of all costs  & & %2.2f% s  \\\\ \n" % (self.npvSystem/1000," kFr.");lines = lines + line 
        line = "\\hline \\\\ \n" ; lines = lines + line
        
        hgcUnit ="$Rp./kWh_{Heat}$"        
            
        line = " Heat Generation Costs & Using annuity: & %2.2f & %s \\\\ \n" % (self.heatGenCost*100.,hgcUnit);lines = lines + line
        line = "  & Using present value: & %2.2f & %s \\\\ \n" % (self.heatGenCostNpv*100.,hgcUnit);lines = lines + line

        doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=False)
        
        #inVar in Fr. !!!

    def createLatex(self):
            
        self.doc.setAuthor(utils.getNameFromUserName())
        self.doc.setEMail(utils.getEmailFromUserName())
        self.doc.setSubTitle("Heat generation costs")        
        self.doc.setTitle(self.fileName)
                       
        
        self.doc.setCleanMode(self.cleanModeLatex)
        self.doc.addBeginDocument()  
        self.addTableEconomicAssumptions()
        self.addTableCosts(self.doc,self.unit)

        self.doc.addEndDocumentAndCreateTexFile()
        self.doc.executeLatexFile()
