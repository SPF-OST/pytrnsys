# pylint: skip-file
# type: ignore

import pytrnsys.pdata.processFiles as spfUtils
import os, re
import pytrnsys.trnsys_util.deckUtils as deckUtils


class TrnsysComponent:
    def __init__(self, _path, _name, extension="ddck", eliminateComments=True):

        self.extension = extension

        self._name = _name
        self._path = _path
        self.nameWithPath = os.path.join(self._path, self._name + "." + self.extension)

        self.linesDeck = None

        self._eliminateComments = eliminateComments
        self.loadFile()

    def loadFile(self, useDeckName=False, eraseBeginComment=True, eliminateComments=True, useDeckOutputPath=False):
        """
        It reads the deck  removing files starting with \*\*\*.

        Return
        ----------
        linesDeck : list of str
            list containing the lines of the deck from the read deck.
        """

        lines = deckUtils.loadDeck(
            self.nameWithPath, eraseBeginComment=self._eliminateComments, eliminateComments=self._eliminateComments
        )

        self.linesDeck = [line.lower() for line in lines]

        self.ignoreOnlinePlotter()

    def setEliminateComments(self, newValue):
        self._eliminateComments == True
        if newValue == True:
            self.linesDeck = deckUtils.loadDeck(
                nameDck, eraseBeginComment=self._eliminateComments, eliminateComments=self._eliminateComments
            )

    def getVariables(self):
        definedVariables = set()
        requiredVariables = set()
        for line in self.linesDeck:
            line = line.replace("\n", "")
            if "=" in line:
                splitEquality = line.split("=")

                definedVariables.add(splitEquality[0].replace(" ", ""))
                myValue = splitEquality[1].replace(" ", "").replace("^", "**")
                replace_list = [
                    "not(",
                    "le(",
                    "lt(",
                    "ge(",
                    "gt(",
                    "eq(",
                    "mod(",
                    ")",
                    "max(",
                    "min(",
                    "abs(",
                    "and(",
                    "or(",
                    "(",
                    r"\t",
                ]
                parts = re.split(r"[+-/*,]", re.sub(r"|".join(map(re.escape, replace_list)), "", myValue))

                parts = [part for part in parts if not part == ""]
                requiredVariables.update([part for part in parts if not (part[0].isdigit() or part[0] == "[")])

            elif any(
                x in line.lower()
                for x in [
                    "simulation",
                    "tolerances",
                    "limits",
                    "dfq",
                    "width",
                    "list",
                    "solver",
                    "nan_check",
                    "overwrite_check",
                    "eqsolver",
                    "time_report",
                ]
            ):
                splitLine = re.split(r"[\s*+]", line)
                splitLine = [part for part in splitLine[1:] if not part == ""]
                requiredVariables.update([part for part in splitLine if not part[0].isdigit()])
            elif (
                not any(
                    x in line.lower()
                    for x in ["unit", "assign", "parameters", "equations", "inputs", "constants", "version"]
                )
                and not line[0].isdigit()
            ):
                splitLine = re.split(r"[\s*+]", line)
                splitLine = [part for part in splitLine if not part == ""]
                requiredVariables.update([part for part in splitLine if not (part[0].isdigit() or part[0] == "-")])

        return definedVariables, requiredVariables

    def ignoreOnlinePlotter(self):

        jBegin = 0
        jEnd = 0
        found = False

        plotterFound = 0

        for i in range(len(self.linesDeck)):

            splitBlank = self.linesDeck[i].split()

            #            if(jBegin>0 and i>jBegin+30):
            #                raise ValueError("jBegin found and not finishd yet")

            #            print "check line i:%d"%i

            if found == True:
                try:

                    #                  print splitBlank[0].replace(" ","").lower()

                    if splitBlank[0].replace(" ", "").lower() == "LABELS".lower():

                        nLabelString = splitBlank[1].replace(" ", "")
                        nLabel = int(nLabelString)

                        jEnd = i + nLabel

                        #                      print "jBegin:%d jEnd:%d nLabel:%d"%(jBegin,jEnd,nLabel)

                        #                      raise ValueError()

                        for j in range(jBegin, jEnd + 1, 1):
                            #                          print "COMMENT (1) FROM j:%d"%(j)
                            self.linesDeck[j] = " \n"

                        found = False
                        i = jEnd  # it does nothing !!!

                except:
                    #                print "COMMENT (3) FROM i:%d"%(i)
                    self.linesDeck[i] = " \n"

            else:  # First it looks for the unit number corresponding to the TYPE and comments util it enters into the LABEL (try section above)
                found = False
                try:
                    unit = splitBlank[0].replace(" ", "")
                    nUnit = splitBlank[1].replace(" ", "")
                    types = splitBlank[2].replace(" ", "")
                    ntype = splitBlank[3].replace(" ", "")

                    if unit.lower() == "unit".lower() and types.lower() == "Type".lower() and ntype == "65":
                        jBegin = i
                        found = True
                        self.linesDeck[i] = " \n"
                        #                        print "FOUND CASE i:%d %s"%(i,ntype)
                        plotterFound = plotterFound + 1

                #                    print "FOUND CASE j:%d TYPE:%s UNIT:%s "%(j,ntype,nUnit)

                except:
                    pass
