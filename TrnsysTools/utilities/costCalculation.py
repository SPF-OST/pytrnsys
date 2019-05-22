
#!/usr/bin/python

"""
Energy cost calculation class

Author : Daniel Carbonell, Daniel Philippen
Date   : 18-10-2017
ToDo :
"""


import utilsSpf as utils
import TrnsysTools.reporting.latexReport as latex
import matplotlib.pyplot as plt
import matplotlib
import matplotlib as mpl

class CostCalculation():
    
    def __init__(self):

        self.method="VDI"
        self.unit=1
        self.cleanModeLatex = True
        
    def initialize(self):

        #initialInputs

        self.rate = 0.
        self.analysPeriod = 0.
        self.costElecFix = 0.
        self.costEleckWh = 0.
        self.lifeTime = 0.
        self.increaseElecCost  = 0.

        self.elDemand = 0.    
        self.totalInvestCost = 0.
    
    def setOutputhPathAndFileName(self,path,fileName):
        
        self.outputPath = path
        self.fileName   = fileName

        print "path:%s name:%s" %(self.outputPath,self.fileName)
        self.doc = latex.LatexReport(self.outputPath,self.fileName)               


    def setGeneralInputs(self,rate,analysPeriod,costElecFix,costEleckWh,increaseElecCost,lifeTime):
        
        
        print "===================SET GENERAL INPUTS========================"
        self.rate = rate
        self.analysPeriod = analysPeriod
        self.costElecFix = costElecFix
        self.costElecKwh = costEleckWh
       
#        self.lifeTime = lifeTime
        self.increaseElecCost = increaseElecCost
       
        print "rate:%f analysisPeriod:%f"%(self.rate,self.analysPeriod)
        
    def setSystemInputs(self,qDemand,elDemand,totalInvestCost,MaintenanceRate,costResidual,lifeTimeRes):
    
        self.qDemand = qDemand
        self.elDemandTotal = elDemand
        self.totalInvestCost = totalInvestCost
        self.MaintenanceRate = MaintenanceRate
        self.costResidual    = costResidual
        self.lifeTimeResVal = lifeTimeRes

    def getNPV(self,rate,period):
        
        npv = ((1.+rate)**period-1.)/(rate*(1.+rate)**period)
        return npv
        
    def getAnnuity(self,rate,period):
        
        Anu = (rate*(1.+rate)**period)/((1.+rate)**period-1.)
        return Anu

    def getNPVIncreaseCost(self,rate,period,increaseCost):
        
        npv = 1/(rate-increaseCost)*(1.-((1.+increaseCost)/(1.+rate))**period)          
        return npv

    def calculate(self):
                      
#        self.npvFac = ((1.+self.rate)**self.analysPeriod-1.)/((1.+self.rate)**self.analysPeriod*self.rate)
        self.npvFac = self.getNPV(self.rate,self.analysPeriod)
        
        self.costElecTotalY = self.costElecFix+self.costElecKwh*self.elDemandTotal  
        
        if(self.rate==self.increaseElecCost): 
            self.npvFacElec = self.lifeTime/(1.+self.rate)
        else:
            self.npvFacElec = 1/(self.rate-self.increaseElecCost)*(1.-((1.+self.increaseElecCost)/(1.+self.rate))**self.analysPeriod)          
     
#        self.priceDynNpv=(1.-((1.+self.increaseElecCost)/(1.+self.rate))**self.analysPeriod)/(self.rate-self.increaseElecCost)     
        self.npvElec = self.costElecTotalY*self.npvFacElec
        self.npvMaintenance = self.MaintenanceRate*self.totalInvestCost*self.npvFac

        print self.costElecTotalY,self.npvElec,self.npvMaintenance
#        raise ValueError("")

        self.discountFromEnd = (1+self.rate)**(-1.*self.analysPeriod)        
        self.resValFactor = (self.lifeTimeResVal-self.analysPeriod)/self.lifeTimeResVal
        
        self.residualValue = (self.costResidual)*self.resValFactor
        self.npvResVal = self.residualValue*self.discountFromEnd
                 
        self.npvSystem = self.totalInvestCost+self.npvElec+self.npvMaintenance-self.npvResVal
        
        print "npvSystem:%f totalInvestCost :%f npvElec :%f npvMaintenance:%f npvResVal:%f"%(self.npvSystem,self.totalInvestCost,self.npvElec,self.npvMaintenance,self.npvResVal)

        self.annuityFac = self.getAnnuity(self.rate,self.analysPeriod)
        
        self.annuity = self.annuityFac*self.npvSystem  # Fr.
        
        print "annuity:%f annuityFac:%f npvSystem:%f"%(self.annuity,self.annuityFac,self.npvSystem)


        self.anToInvCost = self.annuityFac*self.totalInvestCost
        self.anElec = self.annuityFac*self.npvElec
        self.anMaint = self.annuityFac*self.npvMaintenance
        self.anResVal = (-1.)*self.annuityFac*self.npvResVal
        
        print " TEST %f %f   "% (self.npvFacElec,self.annuityFac)
        
        self.heatGenCost = self.annuity/self.qDemand  # Fr./kWh    
        self.heatGenCostNpv = self.npvSystem/self.qDemand/self.analysPeriod        

        print "NPV Factor:%f  AnnuityFac:%f  "% (self.npvFac,self.annuityFac)
        print "Heat Generation Cost Annuity:%f NPV:%f"%(self.heatGenCost,self.heatGenCostNpv)
        
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
        line = " & Variable costs:  %2.2f $Fr.$ $per$ $kWh$ \\\\ \n" % (self.costElecKwh);lines = lines + line     
        line = "Increase of electricity costs & %2.1f %s $per$ $year$ \\\\ \n" % (self.increaseElecCost*100.,perc);lines = lines + line
        line = "Electricity costs year 1 & %2.0f Fr. in year 1 \\\\ \n" % (self.costElecTotalY);lines = lines + line

        label ="definitionTable"
        
        self.doc.addTable(caption,sizeBox,names,units,label,lines,useFormula=True) 
        
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
    def plotCostShare(self,inVar,legends,nameFile,sizeFont=15,plotJpg=False,writeFile=False):
        
        mpl.rcParams['font.size'] = sizeFont

        fig = plt.figure(1,figsize=(15,15))
        
        fig.add_subplot(111)
                   
        total = sum(inVar)        

        myColors = ['#66CCFF','#336699','#FFCC00','#3366CC','#66FF66','#FF9966','#FF9933','#CCFF33','#CCFFFF','#FF9933']
        

        fracs = []
        colors = []
        explode = []
        for i in range(len(inVar)):
            fracs.append(inVar[i]/total)        
            colors.append(myColors[i])
            explode.append(0.) #(0.05)
        
        patches, texts, autotexts = plt.pie(fracs, labels=legends,explode=explode,colors=colors,autopct='%1.1f%%', shadow=False, startangle=0)
        
        for i in range(len(texts)):
            texts[i].set_fontsize(sizeFont)
        
#        texts[0].set_position(00)
        
        # The default startangle is 0, which would start
        # the Frogs slice on the x-axis.  With startangle=90,
        # everything is rotated counter-clockwise by 90 degrees,
        # so the plotting starts on the positive y-axis.

#        matplotlib.rcParams.update({'font.size':50})

        myTitle = "Total cost %.2f [kFr]" % (total/1000.)
        plt.title(myTitle, bbox={'facecolor':'0.9','pad':10},fontsize=sizeFont)

# This is working , just erase the labels section
#        plt.legend(bbox_to_anchor=(0.15,0.9),loc='upper right', borderaxespad=0.,fontsize=8)

        namePdf = '%s.pdf'%nameFile
        nameWithPath = '%s\%s' % (self.outputPath,namePdf)

        
        plt.savefig(nameWithPath)
        
        if(plotJpg):
            
#            nameJpg = '%s.svg'%nameFile 
#            nameJpg = '%s.emf'%nameFile 
            nameJpg = '%s.jpg'%nameFile 

            nameJpgWithPath = '%s\%s' % (self.outputPath,nameJpg)
            print "Plot printed as %s"%nameJpgWithPath
            
            plt.savefig(nameJpgWithPath)
            
        plt.close()
        
        if(writeFile):
            lines = "!Each column has the added value of the previous. To print a bar column ontop of each other\n"
            line = "!Units kFr.\n";lines=lines+line
            line = "!";lines=lines+line
            for i in range(len(legends)):
                line = "%s\t"%legends[i];lines=lines+line
            line = "\n";lines=lines+line

            sumVar = 0.
            for i in range(len(legends)):
                sumVar = sumVar+inVar[i]/1000. #I assume Fr. and change to kFr. !!!!       
                line = "%f\t"%sumVar;lines=lines+line
            line = "\n";lines=lines+line
            nameDat = '%s.dat'%nameFile 
            nameDatWithPath = '%s\%s' % (self.outputPath,nameDat)

            print "PRINT FILE COST SHARE : %s"%nameDatWithPath
            outfile=open(nameDatWithPath,'w')
            outfile.writelines(lines)
            outfile.close()
            
        
            
        return namePdf

        
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
