# pylint: skip-file
# type: ignore

#!/usr/bin/env python

"""
This class allows to print data on parallel runs of wich simulations have been finished and
which ones are still missing.
Author : Jeremias Schmidli, Daniel Carbonell
Date   : 02.04.2018
"""

import time


class DebugProcess:
    def __init__(self, _path, _fileName, cases):

        self.nameRunFile = _path + "\\" + _fileName
        self.cases = cases

    def start(self):

        linesRun = ""

        for i in range(len(self.cases)):
            line = "Case :%s will be processed at :%s (from DebugProcess class)\n" % (self.cases[i], time.strftime("%c"))
            linesRun = linesRun + line

        line = "============ALREADY PROCESSED==============\n"
        linesRun = linesRun + line
        outfileRun = open(self.nameRunFile, "w")
        outfileRun.writelines(linesRun)
        outfileRun.close()

    def addCase(self, i):

        line = "Case :%s has been processed %s (from DebugProcess class)\n" % (self.cases[i], time.strftime("%c"))
        outfileRun = open(self.nameRunFile, "a")
        outfileRun.writelines(line)
        outfileRun.close()

    def addLines(self, lines):

        outfileRun = open(self.nameRunFile, "a")
        outfileRun.writelines(lines)
        outfileRun.close()

    def finish(self):

        line = "processTRNSYS SUCCESFULLY FINISHED"
        outfileRun = open(self.nameRunFile, "a")
        outfileRun.writelines(line)
        outfileRun.close()
