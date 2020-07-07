
#!/usr/bin/python

"""
Energy cost calculation class that allows vector handling

Author : Daniel Carbonell
Date   : 19-01-2018
ToDo :
"""

import pytrnsys.utils.costCalculation as mycost
import numpy as num
import logging
logger = logging.getLogger('root')

class CostCalculationVar(mycost.CostCalculation):
    
    def __init__(self):
        
        mycost.CostCalculation.__init__(self)    
        self.clean()     
        self.initialize()


    def clean(self):
        
        self.components = []
        self.baseCost = []
        self.varCost = []
        self.group = []
        self.size = []
        self.varUnit = []
        self.lifeTimeComp = []
        self.costComponent = []
       
        
        #This are variables that add cost every year such as materials consumed, oil, etc..
        
        self.yearlyComp = []
        self.yearlyCompSize = []
        self.yearlyCompBaseCost = []
        self.yearlyCompVarCost = []
        self.yearlyCompVarUnit = []            
        self.yearlyCompCost = []     
        
    def doPlots(self):
        
        legends =[]        
        inVar = []

        groupCost = 0.
        
        for i in range(self.nComp):
            
            logger.debug("group:%s"%self.group[i])
            
            if(i<(self.nComp-1) and self.group[i] != self.group[i+1]):
                groupCost=groupCost+self.costComponent[i]
                inVar.append(groupCost)
                legends.append(self.group[i])
                groupCost=0.
                logger.debug("Inside group:%s"%self.group[i])
            elif(i==(self.nComp-1)):
                groupCost=groupCost+self.costComponent[i]
                inVar.append(groupCost)
                legends.append(self.group[i])
                logger.debug("Last group:%s"%self.group[i])
            else:              
                groupCost=groupCost+self.costComponent[i]       
                logger.debug("groupCost:%f group:%s"%(groupCost,self.group[i]))
                
#                inVar.append(groupCost)
#                legends.append(self.group[i])
                

        self.nameCostPdf = self.plotCostShare(inVar,legends,"costShare"+"-"+self.fileName,sizeFont=30,plotJpg=False,writeFile=False)
        
        
        
    def setGeneralInputs(self,rate,analysPeriod,costElecFix,costEleckWh,increaseElecCost):
        
        
        logger.info("===================SET GENERAL INPUTS========================")
        self.rate = rate
        self.analysPeriod = analysPeriod
        self.costElecFix = costElecFix
        self.costEleckWh = costEleckWh
       
        self.increaseElecCost = increaseElecCost
       
        logger.debug("rate:%f analysisPeriod:%f"%(self.rate,self.analysPeriod))

    def doPlotsAnnuity(self):

        legends =[]        
        inVar = []
        
        inVar.append(self.anToInvCost)
        legends.append("Capital cost")
        
        inVar.append(self.anMaint)
        legends.append("Maintenance")

        inVar.append(self.anElec)
        legends.append("El. purchased \n from the grid")
        
        for i in range(len(self.yearlyComp)):
        
            logger.debug("cost:%f name:%s"%(self.costComponent[i],self.yearlyComp[i]))
            
            if(self.yearlyCompCost[i]>0.):
                inVar.append(self.anYearlyComp[i])
                if(self.yearlyComp[i]=="Transmission grid"):
                    legends.append("El. transmitted \n through the \n grid")
                elif(self.yearlyComp[i]=="Aluminium fuel"):
                    legends.append("Fuel cost \n (Al regeneration)")
                else:
                    legends.append(self.yearlyComp[i])
        
#        self.annuity        
        
        self.nameCostAnnuityPdf = self.plotCostShare(inVar,legends,"costShareAnnuity"+"-"+self.fileName,plotSize=17,sizeFont=30,plotJpg=False,writeFile=False)


    def addComponent(self,name,size,base,var,varUnit,group,lifeTime):
        
        self.components.append(name)
        self.size.append(size)        
        self.baseCost.append(base)
        self.varCost.append(var)
        self.varUnit.append(varUnit)
        self.group.append(group)
        self.lifeTimeComp.append(lifeTime)
        cost = base+var*size
        self.costComponent.append(cost)
    
        return cost
        logger.debug("cost:%f name:%s base:%f var:%f"%(cost,name,base,var))
        
    def addYearlyComponentCost(self,name,size,base,var,varUnit):
        
        self.yearlyComp.append(name)
        self.yearlyCompSize.append(size)
        self.yearlyCompBaseCost.append(base)
        self.yearlyCompVarCost.append(var)
        self.yearlyCompVarUnit.append(varUnit)     
        cost = base+var*size
        self.yearlyCompCost.append(cost)
        
        logger.debug("cost:%f name:%s base:%f var:%f"%(cost,name,base,var))

    def setSystemInputs(self,qDemand,elDemand,MaintenanceRate,costResidual,lifeTimeRes):
    
        self.qDemand = qDemand
        self.elDemandTotal = elDemand
        self.MaintenanceRate = MaintenanceRate
        self.costResidual    = costResidual
        self.lifeTimeResVal = lifeTimeRes


    def calculate(self):
                      
         #results
        self.nComp = len(self.costComponent)
#        self.costNpv = num.zeros(self.nComp)
        self.costAnn = num.zeros(self.nComp)
#        self.npvFac  = num.zeros(self.nComp)
        self.annFac  = num.zeros(self.nComp)
        
        self.totalInvestCost = 0.
        for i in range (self.nComp):
            logger.debug("ncomp:%d rate:%f lifeTime%f"%(i,self.rate,self.lifeTimeComp[i]))
            
#            npv = self.getNPV(self.rate,self.lifeTimeComp[i]) # All is lifetime or analysisPeriod?
            ann = self.getAnnuity(self.rate,self.lifeTimeComp[i]) 
#            self.npvFac[i] = npv 
            self.annFac[i] = ann
#            self.costNpv[i] =self.costComponent[i]*npv
            self.costAnn[i] =self.costComponent[i]*ann
            
            self.totalInvestCost = self.totalInvestCost+self.costComponent[i]
            
        #===================================================
        #electricity 
        #===================================================
       
        self.costElecTotalY = self.costElecFix+self.costEleckWh*self.elDemandTotal

        
        if(self.rate==self.increaseElecCost): 
            self.npvFacElec = self.analysPeriod/(1.+self.rate) #DC It was lifeTime but now its different from each other
        else:
            self.npvFacElec = self.getNPVIncreaseCost(self.rate,self.analysPeriod,self.increaseElecCost)          
            
        self.npvElec = self.costElecTotalY*self.npvFacElec
                    
        #===================================================
        #Maintenance cost 
        #===================================================
#        self.npvMaintenance = self.MaintenanceRate*self.totalInvestCost*self.npvFac
        self.npvMaintenance = self.MaintenanceRate*self.totalInvestCost*self.getNPV(self.rate,self.analysPeriod)#sum(self.costNpv)

#        if(self.printInfo):
#            print self.costElecTotalY,self.npvElec,self.npvMaintenance

        #===================================================
        #Yearly cost of fuel
        #===================================================
#        self.npvAlMaterialCost = self.alMaterialCost*self.npvFac

        self.nYearlyComp = len(self.yearlyComp)
        self.costNpvYearlyComp = num.zeros(self.nYearlyComp)

        for i in range(self.nYearlyComp):
            npv = self.getNPV(self.rate,self.analysPeriod)
            self.costNpvYearlyComp[i] = self.yearlyCompCost[i]*npv

        #===================================================
        #Residual Value. Do for all that have a longer life time. What happens with replacement 5 y before anylsis period? Should we also add this?
        #===================================================

        self.discountFromEnd = (1+self.rate)**(-1.*self.analysPeriod)        
        self.resValFactor = (self.lifeTimeResVal-self.analysPeriod)/self.lifeTimeResVal        
        self.residualValue = (self.costResidual)*self.resValFactor
        self.npvResVal = self.residualValue*self.discountFromEnd

        #===================================================
        #NET PRESENT VALUE
        #===================================================
                 
        self.npvSystem = self.totalInvestCost+sum(self.costNpvYearlyComp)+self.npvElec+self.npvMaintenance-self.npvResVal
        
        logger.debug("npvSystem:%f totalInvestCost :%f AlMatcost:%f npvElec :%f npvMaintenance:%f npvResVal:%f"%(self.npvSystem,self.totalInvestCost,\
        sum(self.costNpvYearlyComp),self.npvElec,self.npvMaintenance,self.npvResVal))

        #===================================================
        #ANNUITY
        #===================================================

        self.annuityFac = self.getAnnuity(self.rate,self.analysPeriod)
#        self.annuity = self.annuityFac*self.npvSystem  # Fr.
        
#        print "annuity:%f annuityFac:%f npvSystem:%f"%(self.annuity,self.annuityFac,self.npvSystem)


#        self.anToInvCost = self.annuityFac*self.totalInvestCost

        self.anToInvCost = sum(self.costAnn)

        self.anElec = self.annuityFac*self.npvElec
        # self.anMaint = self.annuityFac*self.npvMaintenance
        self.anMaint = self.anToInvCost*self.MaintenanceRate

        self.anResVal = (-1.)*self.annuityFac*self.npvResVal

        self.anYearlyComp = num.zeros(self.nYearlyComp)

        for i in range(self.nYearlyComp):
            self.anYearlyComp[i] = self.annuityFac*self.costNpvYearlyComp[i]
        
        
        self.annuity = self.anToInvCost+self.anElec+self.anMaint+self.anResVal+sum(self.anYearlyComp)
        
        logger.info(" AnElectricity:%f npvElec:%f npvFacElec:%f annnuityFac:%f   "% (self.anElec,self.npvElec,self.npvFacElec,self.annuityFac))
        
        self.heatGenCost = self.annuity/self.qDemand  # Fr./kWh    
#        self.heatGenCostNpv = self.npvSystem/self.qDemand/self.analysPeriod        

#        print "NPV Factor:%f  AnnuityFac:%f  "% (sum(self.npvFac),self.annuityFac)
#        print "Heat Generation Cost Annuity:%f NPV:%f"%(self.heatGenCost,self.heatGenCostNpv)
        logger.info("AnnuityFac:%f  "% (self.annuityFac))
        logger.info("Heat Generation Cost Annuity:%f "%(self.heatGenCost))

   
    def addTableCosts(self,doc,unit=1):
        
        symbol = "$\\%$"
        caption =  "System and Heat generation costs (all values incl. 8%s VAT) " % symbol
        sizeBox = 14                
        
        names = [ "Group","Component","Costs","Size","LifeTime","Total Costs"]
        if(unit==1e-3):
            units = [ "","","[CHF]","","","[kCHF]"]
        elif(unit==1):
            units = [ "","","[CHF]","","Years","[CHF]"]
        else:
            raise ValueError("unit not found:%f"%unit)
            
        label = "CostsTable"        
        lines = ""      
        symbol = "\%"    
                
#        line = "\\hline \\\\ \n" ; lines = lines + line

        line = "\\\\ \n" ; lines = lines + line
        j=0
        sumGroup=0.
        for i in range(self.nComp):
            if(i>0 and self.group[i] != self.group[i-1]):
                if(j>1):
                    line = "&\cline{1-5} \n"; lines = lines + line
                    line = " &\\textbf{Total %s} &  & & & %.0f (%.1f %s) \\\\ \n"%(self.group[i-1],sumGroup,100*sumGroup/self.totalInvestCost,symbol); lines = lines + line
                line = "\\hline \\\\ \n" ; lines = lines + line
                group = self.group[i]
                j=0
                sumGroup=0.
            else:
                group = self.group[i]
                
            if(self.costComponent[i]>0.):
                if(j==0):
                    line = "\\textbf{%s} & %s & %.0f+%.0f/%s & %.2f %s &%d & %.1f (%.1f %s) \\\\ \n"%(group,self.components[i],\
                    self.baseCost[i],self.varCost[i],self.varUnit[i],self.size[i],self.varUnit[i],self.lifeTimeComp[i],self.costComponent[i]*unit,100*self.costComponent[i]/self.totalInvestCost,symbol)
                else:
                    line = " & %s & %.0f+%.0f/%s & %.2f %s &%d & %.1f (%.1f %s) \\\\ \n"%(self.components[i],\
                    self.baseCost[i],self.varCost[i],self.varUnit[i],self.size[i],self.varUnit[i],self.lifeTimeComp[i],self.costComponent[i]*unit,100*self.costComponent[i]/self.totalInvestCost,symbol)
                    
                lines = lines + line
                j=j+1
                
            sumGroup = sumGroup+self.costComponent[i]*unit
        
        if(j>1): #The last component
            logger.info("===================================j:%d==============================="%j)
            line = "&\cline{1-5} \n"; lines = lines + line
            line = " &\\textbf{Total %s} &  & & & %.0f (%.0f %s) \\\\ \n"%(self.group[self.nComp-1],sumGroup,100*sumGroup/self.totalInvestCost,symbol); lines = lines + line

#        line = "\\hline \\\\ \n" ; lines = lines + line
        line = "\\hline \\\\ \n" ; lines = lines + line
        line = " & \\textbf{Total Investment Cost} & && &\\textbf{%2.2f} (100%s) \\\\ \n" % (self.totalInvestCost*unit,symbol);lines = lines + line         

        line = "\\hline \\\\ \n" ; lines = lines + line
        line = "\\hline \\\\ \n" ; lines = lines + line

        costUnit = " $CHF/a$"
        
        line = "Annuity & Annuity (yearly costs over lifetime)  &&& & %2.0f% s  \\\\ \n" % (self.annuity,costUnit);lines = lines + line 
        line = " & Share of Investment & &&& %2.0f%s (%2.0f%s) \\\\ \n" % (self.anToInvCost,costUnit,self.anToInvCost*100./self.annuity,symbol);lines = lines + line 
        line = " & Share of Electricity  & %.0f+%.2f/kWh & %2.0f kWh&  & %2.0f%s (%2.0f%s)\\\\ \n" % (self.costElecFix,self.costEleckWh,self.elDemandTotal,self.anElec,costUnit,self.anElec*100./self.annuity,symbol);lines = lines + line
        line = " & Share of Maintenance & &&& %2.0f%s (%2.0f%s)\\\\ \n" % (self.anMaint,costUnit,self.anMaint*100./self.annuity,symbol);lines = lines + line        
        for i in range(len(self.yearlyComp)):
            line = " & Share of %s & %.0f+%.2f/%s & %.0f  %s & & %2.0f%s (%2.0f%s)\\\\ \n" % (self.yearlyComp[i],self.yearlyCompBaseCost[i],self.yearlyCompVarCost[i],self.yearlyCompVarUnit[i],\
            self.yearlyCompSize[i],self.yearlyCompVarUnit[i],self.anYearlyComp[i],costUnit,self.anYearlyComp[i]*100./self.annuity,symbol)
            lines = lines + line        
        
        line = " & Share of Residual Value &&& & %2.0f%s (%2.0f%s)\\\\ \n" % (self.anResVal,costUnit,self.anResVal*100./self.annuity,symbol);lines = lines + line      
        
#        line = "\\hline \\\\ \n" ; lines = lines + line
        line = "Present Value  & Present Value of all costs  & &&& %2.2f% s  \\\\ \n" % (self.npvSystem," CHF");lines = lines + line 
        line = "\\hline \\\\ \n" ; lines = lines + line
        
        # hgcUnit ="$Rp./kWh_{Heat}$"
        hgcUnit ="$Rp./kWh$"

        line = " Energy Generation Costs & Using annuity: &&& %2.2f & %s \\\\ \n" % (self.heatGenCost*100.,hgcUnit);lines = lines + line
#        line = "  & Using present value: &&& %2.2f & %s \\\\ \n" % (self.heatGenCostNpv*100.,hgcUnit);lines = lines + line


        doc.addTable(caption,names,units,label,lines,useFormula=False)

    def createLatex(self,fileName=False):
            
#        self.doc.setAuthor(utils.getNameFromUserName())
#        self.doc.setEMail(utils.getEmailFromUserName())
        self.doc.setSubTitle("Energy generation costs")

        if(fileName==False):
            self.doc.setTitle(self.fileName)
        else:
            self.doc.setTitle(fileName)

        self.doc.setCleanMode(self.cleanModeLatex)
        self.doc.addBeginDocument()  
        self.addTableEconomicAssumptions()
        self.addTableCosts(self.doc,self.unit)

#        self.doPlotsAnnuity()

        try:
            self.doc.addPlot(self.nameCostPdf,"System cost","systemCost",13)  
            self.doc.addPlot(self.nameCostAnnuityPdf,"System cost annuity share","systemCostannuity",13)  
        except:
            pass
        
        self.doc.addEndDocumentAndCreateTexFile()
        self.doc.executeLatexFile()