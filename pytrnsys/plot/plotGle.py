# pylint: skip-file
# type: ignore

#!/usr/bin/python

"""
Class to plot using GLE graphic design layout
Author : Daniel Carbonell
Date   : 2017
ToDo :
"""

import os
import numpy as num
import pytrnsys.report.latexReport as latex
import subprocess
import logging

logger = logging.getLogger("root")


class PlotGle:
    def __init__(self, path):

        self.path = path

        self.useMarkers = True

        self.colorGLE = [
            "#d62728",
            "#1f77b4",
            "#2ca02c",
            "#7f7f7f",
            "#17becf",
            "#ff7f0e",
            "#9467bd",
            "#bcbd22",
            "#8c564b",
            "#e377c2",
            "black",
            "red",
            "blue",
            "green",
            "gray40",
            "orange",
            "magenta",
            "yellow",
            "cyan",
            "forestgreen",
            "lightblue",
            "slateblue",
            "khaki",
            "darkorange",
            "firebrick",
            "deepskyblue",
            "gray50",
            "black",
        ]

        # "#1f77b4" #blue
        # "#ff7f0e" #orange
        # "#2ca02c" #green
        # "#d62728" #red
        # "#9467bd" #violet
        # "#8c564b" #brown
        # "#e377c2" #pink
        # "#7f7f7f" #grey
        # "#bcbd22" #yellow
        # "#17becf" #cyan

        self.sizeLine = 0.02

    def setUseMarkers(self, use):
        self.useMarkers = use

    def getFigCaption(self,addXSpace=False):

        lines = ""

        line = "sizeX = 15\n"
        lines = lines + line
        line = "sizeY = 11\n"
        lines = lines + line
        line = "ny = 1\n"
        lines = lines + line
        line = "nx = 1\n"
        lines = lines + line
        line = "sizeYT = ny*sizeY\n"
        lines = lines + line
        if(addXSpace!=False):
            line = "sizeXT = nx*sizeX+5+%d\n"%addXSpace
        else:
            line = "sizeXT = nx*sizeX+5\n"

        lines = lines + line
        line = "size sizeXT sizeYT\n"
        lines = lines + line

        line = "useLatex = 1\n"
        lines = lines + line

        line = "begin texpreamble \n"
        lines = lines + line
        line = "\\usepackage[T1]{fontenc} \n"
        lines = lines + line
        line = "\\usepackage{sansmathfonts} \n"
        lines = lines + line
        line = "\\renewcommand{\\familydefault}{\\sfdefault} \n"
        lines = lines + line
        line = "end texpreamble \n"
        lines = lines + line

        line = "set texlabels useLatex\n"
        lines = lines + line
        line = "set font texcmr\n"
        lines = lines + line
        line = "sizeLegend=0.25\n"
        line = "markerSize=0.15\n"
        lines = lines + line
        line = "lSize=0.05\n"
        lines = lines + line
        line = 'myMarker1$="triangle"\n'
        lines = lines + line
        line = "myStyle1  =1\n"
        lines = lines + line

        return lines

    def getCaptionGraph(self):

        lines = ""
        line = "begin graph\n"
        lines = lines + line
        line = "\tsize sizeX sizeY\n"
        lines = lines + line
        line = "\tx2axis on\n"
        lines = lines + line
        line = "\ty2axis on\n"
        lines = lines + line
        line = "\tticks color gray10\n"
        lines = lines + line

        return lines

    def getEasyPlot(self, nameGleFile, fileNameData, legends, useSameStyle=True, inputsAsPairs=False):
        
        lines = self.getFigCaption()

        lines = lines+self.getCaptionGraph()
        
        lines = lines+"\tfileData$=\"%s\"\n"%fileNameData
        
        col1=1
        col2=2

        if (inputsAsPairs):
            mySize = int(len(legends)/2)
        else:
            mySize = len(legends)

        for i in range(mySize):

            line = "\tdata fileData$ d%d=c%d,c%d  ignore 0\n" % (i + 1, col1, col2)
            lines = lines + line

            if (inputsAsPairs):
                legendLine = "$%s$"%legends[col2-1]
            else:
                legendLine = legends[i]


            if(useSameStyle):
                if self.useMarkers==True:
                    line="\td%d marker myMarker1$ msize markerSize line lstyle myStyle1 lwidth lSize color %s key \"%s\"\n"%(i+1,self.colorGLE[i],legendLine)
                    lines = lines + line
                else:
                    line="\td%d line lstyle myStyle1 lwidth lSize color %s key \"%s\"\n"%(i+1,self.colorGLE[i],legendLine)
                    lines = lines + line
            else:
                if self.useMarkers == True:
                    line="\td%d marker myMarker%d$ msize markerSize line lstyle myStyle%d lwidth lSize color %s key \"%s\"\n"%(i+1,i+1,i+1,self.colorGLE[i],legendLine)
                    lines = lines + line
                else:
                    line="\td%d line lstyle myStyle%d lwidth lSize color %s key \"%s\"\n"%(i+1,i+1,self.colorGLE[i],legendLine)
                    lines = lines + line

            if(inputsAsPairs):
                col1=col1+2
                col2=col2+2
            else:
                col2=col2+1

        line="key pos tr hei sizeLegend offset  -0.5 0\n"
        lines = lines+line
        line = "end graph\n"
        lines = lines + line

        myFileNameGleFile = self.path + "\\" + nameGleFile + ".gle"

        outfile = open(myFileNameGleFile, "w")
        outfile.writelines(lines)
        outfile.close()

    def getEasyErrorPlot(self, nameGleFile, fileNameData, legends, useSameStyle=True):

        lines = self.getFigCaption(addXSpace=10)
        lines = lines + "myErrorWidth=0.1\n"

        lines = lines + self.getCaptionGraph()

        lines = lines + "\tfileData$=\"%s\"\n" % fileNameData

        col = 1

        mySize = int(len(legends) / 2)

        i = 1
        iLegend=1
        for j in range(mySize):

            line = "\tdata fileData$ d%d=c%d,c%d  ignore 0\n" % (i, col,col+3)
            lines = lines + line
            line = "\tdata fileData$ d%d=c%d,c%d  ignore 0\n" % (i + 1, col+1,col+4)
            lines = lines + line
            line = "\tdata fileData$ d%d=c%d,c%d  ignore 0\n" % (i + 2, col+2,col+5)
            lines = lines + line
            line = "\tlet d%d = d%d-d%d\n"%(i+100,i+1,i)
            lines = lines + line
            line = "\tlet d%d = d%d-d%d\n"%(i+102,i+2,i+1)
            lines = lines + line

            legendLine = "$%s$" % legends[iLegend]
            iLegend=iLegend+2

            if self.useMarkers == True:
                line = "\td%d marker myMarker1$ msize markerSize line lstyle myStyle1 lwidth lSize color %s errdown d%d errup d%d errWidth myErrorWidth key \"%s\"\n" % (
                i + 1, self.colorGLE[i],i+100,i+102,legendLine)
                lines = lines + line
            else:
                line = "\td%d line lstyle myStyle1 lwidth lSize color %s errdown d%d errup d%d errWidth myErrorWidth key \"%s\"\n" % (
                i + 1, self.colorGLE[i],i+100,i+102,legendLine)
                lines = lines + line

            i=i+3
            col=col+6

        line = "key pos tr hei sizeLegend offset  -0.5 0\n"
        lines = lines + line
        line = "end graph\n"
        lines = lines + line

        myFileNameGleFile = self.path + "\\" + nameGleFile + ".gle"

        outfile = open(myFileNameGleFile, "w")
        outfile.writelines(lines)
        outfile.close()

    def getBarPlot(self, nameGleFile, fileNameData, legends, xnames=None, xmin=0.5, xmax=13.5):

        lines = self.getFigCaption()
        lines = lines + self.getCaptionGraph()

        lines = lines + '\tfileData$="%s"\n' % fileNameData

        col1 = 1
        col2 = 2

        #        j = num.arange(len(legends))
        #        jRev = num.flip(j,0)
        line = "xaxis min %f max %f angle 45\n" % (xmin, xmax)
        lines = lines + line
        if xnames == None:
            line = 'xnames "Jan" "Feb" "Mar" "Apr" "May" "Jun" "Jul" "Aug" "Sep" "Oct" "Nov" "Dec" "Year/10" \n'
            lines = lines + line
        else:
            line = "xnames "
            lines = lines + line
            for name in xnames:
                line = '"%s" ' % name
                lines = lines + line
            line = "\n"
            lines = lines + line

        for i in range(len(legends)):

            line = "\tdata fileData$ d%d=c%d,c%d  ignore 0\n" % (i + 1, col1, col2)
            lines = lines + line
            col2 = col2 + 1

        for i in range(len(legends), 0, -1):

            line = "\tbar d%d fill %s\n" % (i, self.colorGLE[i])
            lines = lines + line

        for i in range(len(legends)):

            line = '\td%d key "%s" \n' % (i + 1, legends[i])
            lines = lines + line

        line = "key pos tr hei 0.2 offset -0.5 0\n"
        lines = lines + line

        line = "end graph\n"
        lines = lines + line

        myFileNameGleFile = self.path + "\\" + nameGleFile + ".gle"

        outfile = open(myFileNameGleFile, "w")
        outfile.writelines(lines)
        outfile.close()

    def getBarBalancePlot(self, nameGleFile, fileNameData, legends, sizeIn, sizeOut, xnames=None):

        lines = ""
        if len(legends) != (sizeIn + sizeOut):
            lines = "!This case will not work because size of legend:%d is different from sizeIn:%d + sizeOut%d\n" % (
                len(legends),
                sizeIn,
                sizeOut,
            )
            lines = (
                lines
                + "!The last values on the negative side that correspond to some from the positive will not be printed automatically.\n !The rest should be correct\n"
            )
            logger.debug(lines)

        lines = lines + self.getFigCaption()
        lines = lines + self.getCaptionGraph()

        lines = lines + '\tfileData$="%s"\n' % fileNameData

        col1 = 1
        col2 = 2

        #        j = num.arange(len(legends))
        #        jRev = num.flip(j,0)
        line = "xaxis min 0.5 max 13.5\n"
        lines = lines + line
        if xnames == None:
            line = 'xnames "Jan" "Feb" "Mar" "Apr" "May" "Jun" "Jul" "Aug" "Sep" "Oct" "Nov" "Dec" "Year/10" \n'
            lines = lines + line
        else:
            line = "xnames "
            lines = lines + line
            for name in xnames:
                line = '"%s" ' % name
                lines = lines + line
            line = "\n"
            lines = lines + line

        for i in range(len(legends)):

            line = "\tdata fileData$ d%d=c%d,c%d  ignore 0\n" % (i + 1, col1, col2)
            lines = lines + line
            col2 = col2 + 1

        line = "!positive values\n"
        lines = lines + line

        for i in range(sizeIn - 1, -1, -1):
            line = "\tbar d%d fill %s !%s\n" % (i + 1, self.colorGLE[i % 17], legends[i])
            lines = lines + line

        line = "!negative values\n"
        lines = lines + line

        for i in range(len(legends) - 1, sizeIn - 1, -1):
            line = "\tbar d%d fill %s ! %s\n" % (i + 1, self.colorGLE[i % 17], legends[i])
            lines = lines + line

        for i in range(len(legends)):
            line = '\td%d key "%s" \n' % (i + 1, legends[i])
            lines = lines + line

        line = "\tkey pos tr hei 0.2 offset -0.5 0\n"
        lines = lines + line
        line = "end graph\n"
        lines = lines + line

        myFileNameGleFile = self.path + "\\" + nameGleFile + ".gle"

        outfile = open(myFileNameGleFile, "w")
        outfile.writelines(lines)
        outfile.close()

    def createFunction(self, name, nCases, col1, col2, xtitle, ytitle):

        nameFunc = name + "_func"

        lines = ""
        line = "sub %s nCases\n" % nameFunc
        lines = lines + line

        lines = lines + self.getCaptionGraph()

        line = "\t\txaxis min xmin max xmax dticks myxdticks dsubticks myxdsubticks grid on\n"
        lines = lines + line
        line = "\t\tyaxis min ymin max ymax dticks mydticks dsubticks mydsubticks grid on\n"
        lines = lines + line

        line = '\t\txtitle "%s"\n' % xtitle
        lines = lines + line
        line = '\t\tytitle "%s"\n' % ytitle
        lines = lines + line

        for i in range(nCases):
            line = "\t\tif(nCases>%d) then\n" % i
            lines = lines + line
            line = "\t\t\tdata file%d$ d%d=c%d,c%d  ignore 0\n" % (i + 1, i + 1, col1, col2)
            lines = lines + line
            if self.useMarkers == True:
                line = (
                    "\t\t\td%d marker myMarker%d$ msize markerSize line lstyle myStyle%d lwidth lSize color myColor%d$ \n"
                    % (i + 1, i + 1, i + 1, i + 1)
                )
                lines = lines + line
            else:
                line = "\t\t\td%d line lstyle myStyle%d lwidth lSize color myColor%d$ \n" % (i + 1, i + 1, i + 1)
                lines = lines + line

            line = "\t\tend if\n"
            lines = lines + line

        line = "\tend graph\n"
        lines = lines + line
        line = "end sub\n"
        lines = lines + line

        myFileNameGleFile = self.path + "\\" + nameFunc + ".gle"

        outfile = open(myFileNameGleFile, "w")
        outfile.writelines(lines)
        outfile.close()

    def createGleQvsT(self, fileName, legends, normalized=False):

        nVar = len(legends)

        lines = ""

        line = "size 14 8\n"
        lines = lines + line
        line = "set texlabels 1\n"
        lines = lines + line
        line = "begin graph\n"
        lines = lines + line
        line = "size 12 8\n"
        lines = lines + line

        if normalized:
            line = 'ytitle "$Q_{cumulative}/Q_{demand}$" \n'
            lines = lines + line
        else:
            line = 'ytitle "$Q_{cumulative}$ [MWh]" \n'
            lines = lines + line

        line = 'xtitle "$T$ [$^oC$]" \n'
        lines = lines + line

        # line = "xaxis min -10 max 100.0 dticks 20.0\n" ; lines = lines +line
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

        j = 2
        for i in range(nVar):
            line = " data   myFile$ d%d = c%d,c%d \n" % (i + 1, j, j + 1)
            lines = lines + line
            j = j + 2

        for i in range(nVar):
            if legends[i].startswith("$"):
                line = 'd%d lstyle 1 line lwidth %f color %s key "%s"  \n' % (
                    i + 1,
                    self.sizeLine,
                    self.colorGLE[i],
                    legends[i],
                )
                lines = lines + line
            else:
                line = 'd%d lstyle 1 line lwidth %f color %s key "$%s$"  \n' % (
                    i + 1,
                    self.sizeLine,
                    self.colorGLE[i],
                    legends[i],
                )
                lines = lines + line

        line = " key pos tr hei 0.2 offset -1 0\n"
        lines = lines + line
        line = "end graph\n"
        lines = lines + line
        myFileNameGleFile = self.path + "\\" + fileName.split(".")[0] + ".gle"

        outfile = open(myFileNameGleFile, "w")
        outfile.writelines(lines)
        outfile.close()

    def executeGLE(self, fileName,fileExtension="pdf"):


        gleExe = os.getenv("GLE_EXE")
        if not os.path.exists(gleExe):
            gleExe = "gle.exe"
        cmd = [gleExe, "-vb", "0", "-d", fileExtension, rf"{self.path}\{fileName}"]
        logger.debug(" ".join(cmd))

        subprocessOutput = subprocess.run(cmd, shell=True, capture_output=True)
        errorMessage = subprocessOutput.stderr.decode("utf-8")
        outputMessage = subprocessOutput.stdout.decode("utf-8")
        if errorMessage != "":
            logger.warning(errorMessage)
        logger.debug(outputMessage)

        namePdf = fileName.split(".")[0] + ".pdf"

        fileNameWithPath = self.path + "\\" + namePdf

        #        return fileNameWithPath
        return namePdf

    def createLatexFromGlePlots(self, namePlots, latexFile, titleLatex, subTileLatex):

        doc = latex.LatexReport(self.path, latexFile)
        doc.setCleanMode(False)
        doc.setTitle(titleLatex)
        doc.setSubTitle(subTileLatex)

        doc.addBeginDocument()

        for i in range(len(namePlots)):

            nameWithPath = self.executeGLE(namePlots[i])

            doc.addPlot(nameWithPath, "caption", "Fig%d" % i, 12)

        doc.addEndDocumentAndCreateTexFile()
        doc.executeLatexFile()

    def changeDataFromGleTextFile(self, namePlots, parametersDict, modifyNameGle=False):

        for i in range(len(namePlots)):
            if modifyNameGle == True:
                nameGleOut = namePlots[i].split(".")[0] + "-mod.gle"
            else:
                nameGleOut = namePlots[i]

            infile = open(namePlots[i], "r")
            lines = infile.readlines()

            for i in range(len(lines)):
                splitEquality = lines[i].split("=")
                try:
                    myName = splitEquality[0].replace(" ", "")
                    value = splitEquality[1].replace(" ", "")

                    logger.debug("myName:%s value:%s" % (myName, value))

                    for key in parametersDict.iterkeys():
                        logger.debug("key:%s- myName:%s-" % (key, myName))

                        if key == myName:

                            myNewLine = "%s=%s ! value changed from original by plotGle.py\n" % (
                                key,
                                parametersDict[key],
                            )
                            logger.debug("NEW LINE %s" % myNewLine)

                            lines[i] = myNewLine
                except:
                    pass
            outfile = open(nameGleOut, "w")
            outfile.writelines(lines)
            outfile.close()
