# pylint: skip-file
# type: ignore

__all__ = ["ResultsWriter"]

import json
import logging
import pathlib as _pl

import matplotlib as mpl
from matplotlib import pyplot as plt

from pytrnsys.report import latexReport as latex
from . import _cost_table as _ct
from . import _createCostCalculations as _co
from ._models import input as _input
from ._models import output as _output

logger = logging.getLogger("root")


class ResultsWriter:
    _SHALL_USE_kCHF_FOR_TOTAL_COSTS = False

    def __init__(self):
        self.method = "VDI"
        self.cleanModeLatex = None
        # self.doLaTex = True

    def writeReportAndResults(
        self,
        parameters: _input.Parameters,
        costCalculation: _co.CostCalculation,
        shallWriteReport: bool,
    ):
        resultsJsonFilePath = costCalculation.resultsJsonFilePath

        if shallWriteReport:
            self._doPlots(costCalculation.output.componentGroups, resultsJsonFilePath)
            self._doPlotsAnnuity(costCalculation.output, resultsJsonFilePath)
            self._createLatex(parameters, costCalculation.output, resultsJsonFilePath)

        self._addCostsToResultsJson(costCalculation.output, resultsJsonFilePath)

    @staticmethod
    def readCostJson(path):

        with open(path) as json_file:
            dictCost = json.load(json_file)

        return dictCost

    @staticmethod
    def setFontSizes(small):
        SMALL_SIZE = small
        MEDIUM_SIZE = SMALL_SIZE + 2
        BIGGER_SIZE = MEDIUM_SIZE + 2

        plt.rc("font", size=SMALL_SIZE)  # controls default text sizes
        plt.rc("axes", titlesize=SMALL_SIZE)  # fontsize of the axes title
        plt.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
        plt.rc("xtick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
        plt.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
        plt.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize
        plt.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title

    def _addCostsToResultsJson(
        self, output: _output.Output, resultsJsonFilePath: _pl.Path
    ):
        serializedResults = resultsJsonFilePath.read_text()
        results = json.loads(serializedResults)

        costsDict = self._createCostsDict(output)
        resultsWithCosts = {**results, **costsDict}

        serializedResultsWithCosts = json.dumps(
            resultsWithCosts, indent=2, sort_keys=True
        )
        resultsJsonFilePath.write_text(serializedResultsWithCosts)

    @staticmethod
    def _createCostsDict(output: _output.Output):
        totalCost = output.componentGroups.cost
        totalCostPerMwh = totalCost / (output.heatingDemandInKWh / 1000)

        costsDict = {
            "investment": totalCost.to_dict(),
            "energyCost": output.heatGenerationCost.to_dict(),
            "investmentPerMWh": totalCostPerMwh.to_dict()
        }

        collectorComponents = [
            c
            for g in output.componentGroups.groups
            for c in g.components.factors
            if c.name == "Collector"
        ]

        if len(collectorComponents) > 1:
            raise RuntimeError("More than one `Collector' component found.")

        if collectorComponents:
            collectorComponent = collectorComponents[0]
            size = collectorComponent.value
            totalCostPerM2 = totalCost / size.value
            costsDict = {
                **costsDict,
                "investmentPerM2": totalCostPerM2.to_dict(),
            }

        hpComponents = [
            c
            for g in output.componentGroups.groups
            for c in g.components.factors
            if c.name == "Heat pump"
        ]

        if len(hpComponents) > 1:
            raise RuntimeError("More than one `Heat pump' component found.")

        if hpComponents:
            hpComponent = hpComponents[0]
            size = hpComponent.value
            totalCostPerkW = totalCost / size.value

            costsDict = {
                **costsDict,
                "investmentPerkW": totalCostPerkW.to_dict(),
            }

        return costsDict

    # plots

    def _doPlots(
        self, componentGroups: _output.ComponentGroups, resultsJsonFilePath: _pl.Path
    ) -> None:
        groupNamesWithCost = [
            (g.name, g.components.cost.mean) for g in componentGroups.groups
        ]

        groupNames, groupCosts = zip(*groupNamesWithCost)
        simulationName = self._getSimulationName(resultsJsonFilePath)
        self.nameCostPdf = self._plotCostShare(
            groupCosts,
            groupNames,
            resultsJsonFilePath.parent,
            fileName="costShare" + "-" + simulationName,
            plotSize=15,
        )

    def _doPlotsAnnuity(self, output: _output.Output, resultsJsonFilePath: _pl.Path):
        legends = []
        inVar = []

        inVar.append(output.componentGroups.annuity.mean)
        legends.append("Capital cost")

        inVar.append(output.componentGroups.maintenanceCost.mean)
        legends.append("Maintenance")

        inVar.append(output.electricity.annuity.mean)
        legends.append("El. purchased \n from the grid")

        for yearlyCost in output.yearlyCosts.factors:
            name = yearlyCost.name
            cost = yearlyCost.cost.mean

            logger.debug("cost:%f name:%s", cost, name)

            if cost > 0:
                inVar.append(cost)
                if name == "Transmission grid":
                    legends.append("El. transmitted \n through the \n grid")
                elif name == "Aluminium fuel":
                    legends.append("Fuel cost \n (Al regeneration)")
                else:
                    legends.append(name)

        simulationName = self._getSimulationName(resultsJsonFilePath)
        self.nameCostAnnuityPdf = self._plotCostShare(
            inVar,
            legends,
            resultsJsonFilePath.parent,
            fileName="costShareAnnuity" + "-" + simulationName,
            plotSize=17,
        )

    def _plotCostShare(self, inVar, legends, outputPath: _pl.Path, fileName, plotSize):
        sizeFont = 30

        mpl.rcParams["font.size"] = sizeFont

        fig = plt.figure(1, figsize=(plotSize, plotSize))

        fig.add_subplot(111)

        total = sum(inVar)

        myColors = [
            "#66CCFF",
            "#336699",
            "#FFCC00",
            "#3366CC",
            "#66FF66",
            "#FF9966",
            "#FF9933",
            "#CCFF33",
            "#CCFFFF",
            "#FF9933",
        ]

        fracs = []
        colors = []
        explode = []
        for i in range(len(inVar)):
            fracs.append(inVar[i] / total)
            colors.append(myColors[i])
            explode.append(0.0)  # (0.05)

        patches, texts, autotexts = plt.pie(
            fracs,
            labels=legends,
            explode=explode,
            colors=colors,
            autopct="%1.1f%%",
            shadow=False,
            startangle=0,
        )

        for i in range(len(texts)):
            texts[i].set_fontsize(sizeFont)

        plt.title("", bbox={"facecolor": "0.9", "pad": 10}, fontsize=sizeFont)

        namePdf = f"{fileName}.pdf"
        nameWithPath = outputPath / namePdf

        plt.savefig(nameWithPath)

        plt.close()

        return namePdf

    # latex

    def _createLatex(
        self,
        parameters: _input.Parameters,
        output: _output.Output,
        resultsJsonFilePath: _pl.Path,
    ):
        simulationName = self._getSimulationName(resultsJsonFilePath)

        doc = latex.LatexReport(str(resultsJsonFilePath.parent), simulationName)
        doc.resetTexName(simulationName + "-cost")

        doc.setSubTitle("Energy generation costs")
        doc.setTitle(simulationName)
        doc.setAuthor(parameters.reportAuthor)
        doc.setEMail(parameters.reportEmail)
        doc.setCleanMode(self._getIsLatexCleanMode(parameters))

        doc.addBeginDocument()
        self._addTableEconomicAssumptions(parameters, output, doc)
        self._addTableCosts(output, doc)
        doc.addPlot(self.nameCostPdf, "System cost", "systemCost", size=13)
        doc.addPlot(
            self.nameCostAnnuityPdf,
            "System cost annuity share",
            "systemCostannuity",
            size=13,
        )
        doc.addEndDocumentAndCreateTexFile()

        doc.executeLatexFile()

    @staticmethod
    def _getSimulationName(resultsJsonFilePath):
        suffix = "-results"
        stem = resultsJsonFilePath.stem
        assert stem.endswith(suffix)
        return stem[: -len(suffix)]

    def _getIsLatexCleanMode(self, parameters):
        return (
            parameters.cleanModeLatex
            if self.cleanModeLatex is None
            else self.cleanModeLatex
        )

    @staticmethod
    def _addTableEconomicAssumptions(
        parameters: _input.Parameters, output: _output.Output, doc: latex.LatexReport
    ):
        caption = "Assumptions for calculation of heat generation costs"
        names = ["", "", "", ""]
        units = None

        lines = ""
        line = rf"Rate & {parameters.rate * 100:2.1f} \% per annum\\"
        lines += line + "\n"
        line = rf"Analysis period & {parameters.analysisPeriod:2.0f} years\\"
        lines += line + "\n"
        line = rf"Maintenance & {parameters.maintenanceRate * 100:2.1f} \% of Investment costs per year \\"
        lines += line + "\n"
        line = r"\hline \\"
        lines += line + "\n"
        line = rf"Electricity & Fix costs: {parameters.costElecFix:2.0f}  Fr. per year \\"
        lines += line + "\n"
        line = (
            rf" & Variable costs:  {parameters.costElecKWh:2.2f} $Fr.$ $per$ $kWh$ \\"
        )
        lines += line + "\n"
        line = rf"Increase of electricity costs & {parameters.increaseElecCost * 100:2.1f} \% per year \\"
        lines += line + "\n"
        line = rf"Electricity costs year 1 & {output.electricity.cost:2.0f} Fr. in year 1 \\"
        lines += line + "\n"
        line = rf"Energy demand per year & {output.heatingDemandInKWh:2.0f} kWh \\"
        lines += line + "\n"




        label = "definitionTable"

        doc.addTable(caption, names, units, label, lines, useFormula=True)

    def _addTableCosts(self, output: _output.Output, doc):
        lines = _ct.createLines(output, self._SHALL_USE_kCHF_FOR_TOTAL_COSTS)

        caption = r"System and Heat generation costs (all values incl. 8$\%$ VAT) "
        names = ["Group", "Component", "Costs", "Size", "LifeTime", "Total Costs"]
        units = self._getUnitsForAnnuityPlot()
        label = "CostsTable"

        doc.addTable(caption, names, units, label, lines, useFormula=False)

    def _getUnitsForAnnuityPlot(self):
        if self._SHALL_USE_kCHF_FOR_TOTAL_COSTS:
            units = ["", "", "[CHF]", "", "", "[kCHF]"]
        else:
            units = ["", "", "[CHF]", "", "Years", "[CHF]"]
        return units
