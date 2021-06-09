# pylint: skip-file
# type: ignore

"""
Author : Dani Carbonell
Date   : 09.05.2018
ToDo   :
"""

import pytrnsys.report.latexReport as latex
import pytrnsys.plot.plotMatplotlib as plot
import pytrnsys.utils.unitConverter as unit
import pytrnsys.trnsys_util.readTrnsysFiles as readTrnsysFiles


class ProcessTrnsysBase:
    def __init__(self, _path, _name):

        self.fileName = _name
        self.outputPath = _path + "\%s" % self.fileName
        self.executingPath = _path
        self.titleOfLatex = "$%s$" % self.fileName
        self.folderName = self.fileName
        self.tempFolder = "%s\\temp" % self.outputPath

        self.fileNameWithExtension = _name

        self.doc = latex.LatexReport(self.outputPath, self.fileName)

        self.plot = plot.PlotMatplotlib()
        self.plot.setPath(self.outputPath)

        self.readTrnsysFiles = readTrnsysFiles.ReadTrnsysFiles(self.tempFolder)

        self.unit = unit.UnitConverter()

        self.initialize()

    def initialize(self):

        self.nameClass = "ProcessTrnsysBase"
        self.yearReadedInMonthylFile = -1  # This read the last year of the simulation
        self.cleanModeLatex = True
        self.firstMonth = "January"
        self.firstConsideredTime = None  # the first one readed in time step file

    def setCleanModeLatex(self, mode):

        self.cleanModeLatex = mode

    # year=-1 : reads the last year
    # year=1 : reads 1st year
    def setYearReadedInMonthylFile(self, year):

        self.yearReadedInMonthylFile = year

    # firstMonth considered, "January", "February", etc
    def setFirstMonth(self, firstMonth):
        self.firstMonth = firstMonth

    def setFirstConsideredTime(self, time):

        self.firstConsideredTime = time

    def addLatexText(self):  # Each child class should define this

        pass

    def createLatex(self):

        self.doc.documentClass = "SPFShortReportIndex"

        self.doc.setTitle(self.titleOfLatex)
        self.doc.setSubTitle("TRNSYS results")
        self.doc.setCleanMode(self.cleanModeLatex)
        self.doc.addBeginDocument()

        # ==============================================================================
        #  END DOCUMENT, WRITE FILE AND EXECUTE
        # ==============================================================================

        self.addLatexText()

        # ==============================================================================
        #  END DOCUMENT, WRITE FILE AND EXECUTE
        # ==============================================================================

        self.doc.addEndDocumentAndCreateTexFile()
        self.doc.executeLatexFile()
