# pylint: skip-file
# type: ignore

import pathlib as _pl
import typing as _tp

import numpy as num

import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.trnsys_util.buildTrnsysDeck as _build
import pytrnsys.trnsys_util.replaceAssignStatements as _ras


class GetConfigMixin:
    def __init__(self):
        self.variation = []  # parametric studies
        self.parDeck = []  # fixed values changed in all simulations
        self._ddckFilePathWithComponentNames = []
        self._defaultVisibility = _dv.DefaultVisibility.LOCAL
        self._ddckPlaceHolderValuesJsonPath = None
        self.parameters = {}  # deck parameters fixed for all simulations
        self._assignStatements = []
        self.listFit = {}
        self.listFitObs = []
        self.listDdckPaths = set()
        self.dictDdckPaths = {}
        self.caseDict = {}
        self.sourceFilesToChange = []
        self.sinkFilesToChange = []
        self.foldersForDDckVariation = []
        self.replaceLines = []

    def addParametricVariations(self, variations):
        """
        it fills a variableOutput with a list of all variations to run
        format <class 'list'>: [['Ac', 'AcollAp', 1.5, 2.0, 1.5, 2.0], ['Vice', 'VIceS', 0.3, 0.3, 0.4, 0.4]]

        Parameters
        ----------
        variations : list of list
            list object containing the variations to be used.

        Returns
        -------

        """

        if self.inputs["combineAllCases"] == True:
            labels = []
            values = []
            for i, row in enumerate(variations):
                labels.append(row[:2])
                values.append(row[2:])

            valuePermutations = num.array(num.meshgrid(*values), dtype=object).reshape(len(variations), -1)
            result = num.concatenate((labels, valuePermutations), axis=1)
            self.variablesOutput = result.tolist()

        else:
            sizeOneVariation = len(variations[0]) - 2
            for n in range(len(variations)):
                sizeCase = len(variations[n]) - 2
                if sizeCase != sizeOneVariation:
                    raise ValueError(
                        "for combineAllCases=False all variations must have same length :%d case n:%d has a length of :%d"
                        % (sizeOneVariation, n + 1, sizeCase)
                    )

            self.variablesOutput = variations

    def getConfig(self):
        self.variation = []  # parametric studies
        self.parDeck = []  # fixed values changed in all simulations
        self._ddckFilePathWithComponentNames = []
        self._defaultVisibility = _dv.DefaultVisibility.LOCAL
        self._ddckPlaceHolderValuesJsonPath = None
        self.parameters = {}  # deck parameters fixed for all simulations
        self._assignStatements = []
        self.listFit = {}
        self.listFitObs = []
        self.listDdckPaths = set()
        self.dictDdckPaths = {}
        self.caseDict = {}
        self.sourceFilesToChange = []
        self.sinkFilesToChange = []
        self.foldersForDDckVariation = []
        self.replaceLines = []

        for line in self.lines:
            splitLine = line.split()
            if splitLine[0] == "variation":
                variation = []
                for i in range(len(splitLine)):
                    if i == 0:
                        continue

                    if i <= 2:
                        variation.append(splitLine[i])
                    else:
                        try:
                            variation.append(float(splitLine[i]))
                        except ValueError:
                            variation.append(splitLine[i])

                self.variation.append(variation)

            elif splitLine[0] == "deck":
                if splitLine[2] == "string":
                    self.parameters[splitLine[1]] = splitLine[3]
                else:
                    if splitLine[2].isdigit():
                        self.parameters[splitLine[1]] = float(splitLine[2])
                    else:
                        self.parameters[splitLine[1]] = splitLine[2]

            elif splitLine[0] == "assign":
                errorMessage = f"""\
Invalid syntax: {line}. Usage:
    assign <new-path> <unit-variable-name>
"""
                if len(splitLine) != 3:
                    raise ValueError(errorMessage)

                _, newPath, unitVariableName = splitLine

                if unitVariableName.isdigit() or "\\" in unitVariableName:
                    raise ValueError(errorMessage)

                assignStatement = _ras.AssignStatement(newPath, unitVariableName)

                self._assignStatements.append(assignStatement)

            elif splitLine[0] == "replace":
                splitString = line.split('$"')
                oldString = splitString[1].split('"')[0]
                newString = splitString[2].split('"')[0]

                self.replaceLines.append((oldString, newString))

            elif splitLine[0] == "changeDDckFile":
                self.sourceFilesToChange.append(splitLine[1])
                sinkFilesToChange = []
                for i in range(len(splitLine)):
                    if i < 2:
                        continue

                    sinkFilesToChange.append(splitLine[i])

                self.sinkFilesToChange.append(sinkFilesToChange)

            elif splitLine[0] == "addDDckFolder":
                for i in range(len(splitLine)):
                    if i > 0:
                        self.foldersForDDckVariation.append(splitLine[i])
            elif splitLine[0] == "fit":
                self.listFit[splitLine[1]] = [splitLine[2], splitLine[3], splitLine[4]]
            elif splitLine[0] == "case":
                self.listFit[splitLine[1]] = splitLine[2:]
            elif splitLine[0] == "fitobs":
                self.listFitObs.append(splitLine[1])

            elif splitLine[0] in self.inputs.keys():
                nParts = len(splitLine)
                if nParts < 2:
                    self._raiseDdckReferenceErrorMessage(line, "<path-variable-name>", "<ddck-file-name>")

                basePathVariableName = splitLine[0]
                relativeDdckFilePath = _pl.Path(splitLine[1])

                basePath = _pl.Path(self.inputs[basePathVariableName])
                ddckFilePath = basePath / relativeDdckFilePath

                if nParts == 2:
                    componentName = ddckFilePath.parent.name
                    defaultVisibility = None
                elif nParts == 3 and splitLine[2] == "global":
                    componentName = ddckFilePath.parent.name
                    defaultVisibility = _dv.DefaultVisibility.GLOBAL
                elif nParts == 4 and splitLine[2] == "as":
                    componentName = splitLine[3]
                    defaultVisibility = None
                else:
                    self._raiseDdckReferenceErrorMessage(line, basePathVariableName, str(relativeDdckFilePath))

                ddckFilePathWithComponentName = _build.DdckFilePathWithComponentName(
                    ddckFilePath, componentName, defaultVisibility
                )
                self._ddckFilePathWithComponentNames.append(ddckFilePathWithComponentName)
                self.listDdckPaths.add(str(basePath))
                self.dictDdckPaths[str(ddckFilePath)] = str(basePath)

        if "pathToConnectionInfo" in self.inputs:
            self._ddckPlaceHolderValuesJsonPath = self.inputs["pathToConnectionInfo"]

        if "defaultVisibility" in self.inputs:
            value: str = self.inputs["defaultVisibility"]
            if value not in ("local", "global"):
                raise ValueError(f'Default visibility must be "local" or "global", but was {value}.')

            valueUpperCase = value.upper()

            self._defaultVisibility = _dv.DefaultVisibility[valueUpperCase]

        if len(self.variation) > 0:
            self.addParametricVariations(self.variation)
            self.variationsUsed = True
        else:
            self.variationsUsed = False

        if len(self.sourceFilesToChange) > 0:
            self.changeDDckFilesUsed = True
        else:
            self.changeDDckFilesUsed = False

        if len(self.foldersForDDckVariation) > 0:
            self.foldersForDDckVariationUsed = True
        else:
            self.foldersForDDckVariationUsed = False

    @staticmethod
    def _raiseDdckReferenceErrorMessage(
        actualLine: str, pathVariableName: str, relativeDdckFilePathString: str
    ) -> _tp.NoReturn:
        errorMessage = f"""\
Invalid syntax: {actualLine}.

Correct possibilities are:

    {pathVariableName} {relativeDdckFilePathString}

when the component name should be deduced from the ddck file's containing directory's name or

    {pathVariableName} {relativeDdckFilePathString} global

if - in addition to the above - the variables within the ddck should be treated as globally
visible, irrespective of the default visibility set in the config file, or

    {pathVariableName} {relativeDdckFilePathString} as <component-name>

when you want to give the component name explicitly by <component-name>
"""
        raise ValueError(errorMessage)
