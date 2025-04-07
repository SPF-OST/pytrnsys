# pylint: skip-file
# type: ignore

import dataclasses as _dc
import itertools as _it
import pathlib as _pl
import typing as _tp

import numpy as _np

import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.trnsys_util.buildTrnsysDeck as _btd
import pytrnsys.trnsys_util.buildTrnsysDeck as _build
import pytrnsys.trnsys_util.replaceAssignStatements as _ras


@_dc.dataclass
class _PathToCopyToVariationDataFolder:
    source: _pl.Path
    target: _pl.Path


class GetConfigMixin:
    def __init__(self):
        self.variation = []  # parametric studies
        self.parDeck = []  # fixed values changed in all simulations
        self._includedDdckFiles = list[_btd.IncludedDdckFile]
        self._defaultVisibility = _dv.DefaultVisibility.LOCAL
        self._ddckPlaceHolderValuesJsonPath = None
        self.parameters = {}  # deck parameters fixed for all simulations
        self._assignStatements = list[_ras.AssignStatement]()
        self._allPathsToCopyToVariationDataFolder = list[_PathToCopyToVariationDataFolder]()
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

            valuePermutations = _np.array(_np.meshgrid(*values), dtype=object).reshape(len(variations), -1)
            result = _np.concatenate((labels, valuePermutations), axis=1)
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
        self._includedDdckFiles = []
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

            command = splitLine[0]
            if command == "variation":
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

            elif command == "deck":
                if splitLine[2] == "string":
                    self.parameters[splitLine[1]] = splitLine[3]
                else:
                    if splitLine[2].isdigit():
                        self.parameters[splitLine[1]] = float(splitLine[2])
                    else:
                        self.parameters[splitLine[1]] = splitLine[2]

            elif command == "assign":
                self._addAssignStatement(line, splitLine)

            elif command == "replace":
                splitString = line.split('$"')
                oldString = splitString[1].split('"')[0]
                newString = splitString[2].split('"')[0]

                self.replaceLines.append((oldString, newString))

            elif command == "changeDDckFile":
                self.sourceFilesToChange.append(splitLine[1])
                sinkFilesToChange = []
                for i in range(len(splitLine)):
                    if i < 2:
                        continue

                    sinkFilesToChange.append(splitLine[i])

                self.sinkFilesToChange.append(sinkFilesToChange)

            elif command == "addDDckFolder":
                for i in range(len(splitLine)):
                    if i > 0:
                        self.foldersForDDckVariation.append(splitLine[i])
            elif command == "fit":
                self.listFit[splitLine[1]] = [
                    splitLine[2],
                    splitLine[3],
                    splitLine[4],
                ]
            elif command == "case":
                self.listFit[splitLine[1]] = splitLine[2:]
            elif command == "fitobs":
                self.listFitObs.append(splitLine[1])
            elif command in self.inputs.keys():
                self._includeDdckFile(line)

        if "pathToConnectionInfo" in self.inputs:
            self._ddckPlaceHolderValuesJsonPath = self.inputs["pathToConnectionInfo"]

        if "defaultVisibility" in self.inputs:
            self._setDefaultVisibility()

        if "copyPathsToVariationDataFolder" in self.inputs:
            self._addAllPathsToCopyToVariationDataFolder()

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

    def _setDefaultVisibility(self) -> None:
        value: str = self.inputs["defaultVisibility"]

        if value not in ("local", "global"):
            raise ValueError(f'Default visibility must be "local" or "global", but was "{value}".')

        valueUpperCase = value.upper()
        self._defaultVisibility = _dv.DefaultVisibility[valueUpperCase]

    def _addAssignStatement(self, line: str) -> None:
        errorMessage = f"""\
Invalid syntax: {line}. Usage:
    assign <new-path> <unit-variable-name>
"""
        splitLine = line.split()

        if len(splitLine) != 3:
            raise ValueError(errorMessage)

        _, newPath, unitVariableName = splitLine

        if unitVariableName.isdigit() or "\\" in unitVariableName:
            raise ValueError(errorMessage)

        assignStatement = _ras.AssignStatement(newPath, unitVariableName)

        self._assignStatements.append(assignStatement)

    def _includeDdckFile(self, line: str) -> None:
        splitLine = line.split()

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

        includedDdckFile = _build.IncludedDdckFile(ddckFilePath, componentName, defaultVisibility)

        self._includedDdckFiles.append(includedDdckFile)
        self.listDdckPaths.add(str(basePath))
        self.dictDdckPaths[str(ddckFilePath)] = str(basePath)

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

    def _addAllPathsToCopyToVariationDataFolder(self) -> None:
        allSourceAndTargets = self.inputs.get("copyPathsToVariationDataFolder")
        assert allSourceAndTargets

        for sourceAndTargets in allSourceAndTargets:
            self._addPathsToCopyToVariationDataFolder(sourceAndTargets)

    def _addPathsToCopyToVariationDataFolder(self, sourceAndTargets: _tp.Sequence[str]) -> None:
        isOk = (
            isinstance(sourceAndTargets, list)
            and len(sourceAndTargets) % 2 == 0
            and all(isinstance(p, str) for p in sourceAndTargets)
        )
        if not isOk:
            formattedSourceAndTargets = " ".join(f'"{p}"' for p in sourceAndTargets)
            errorMessage = f"""\
Invalid syntax: stringArray copyPathsToVariationDataFolder {formattedSourceAndTargets}. Usage:

stringArray copyPathsToVariationDataFolder ..\\path\\to\\source1 path\\to\\dest1 [path\\to\\source2.txt path\\to\\long\\dest2.txt ...]
"""
            raise ValueError(errorMessage)

        sourceAndTargetPaths = [_pl.Path(s) for s in sourceAndTargets]

        pathsToCopy = [_PathToCopyToVariationDataFolder(s, t) for s, t in _it.batched(sourceAndTargetPaths, 2)]

        absoluteTargetPaths = [c.target for c in pathsToCopy if c.target.is_absolute()]
        if absoluteTargetPaths:
            formattedAbsoluteTargetPaths = "\n".join(f"\t{t}" for t in absoluteTargetPaths)
            errorMessage = f"""\
The following absolute target paths were found in a `copyPathsToVariationDataFolder` command:

{formattedAbsoluteTargetPaths}

Target paths to `copyPathsToVariationDataFolder` must be relative.
"""
            raise ValueError(errorMessage)

        self._allPathsToCopyToVariationDataFolder.extend(pathsToCopy)
