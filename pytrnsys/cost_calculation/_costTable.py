__all__ = ['ComponentGroupsRowsLinesWriter']


import typing as _tp

from ._models import output as _output
from ._models import common as _common


class ComponentGroupsRowsLinesWriter:
    def __init__(self, totalCost: _common.UncertainFloat, totalCostScaleFactor: float):
        self._totalCost = totalCost
        self._totalCostScaleFactor = totalCostScaleFactor

    def createLines(self, componentGroups: _output.ComponentGroups):
        lines = ""
        for group in componentGroups.groups:
            groupLines = self._createComponentGroupRowsLines(group)

            lines += groupLines + r"\hline \\" + "\n"

        totalCost = self._totalCost * self._totalCostScaleFactor
        formattedTotalCost = totalCost.format(precision=2)

        line = rf" & \textbf{{Total Investment Cost}} & & & & \textbf{{{formattedTotalCost}}} (100\%) \\ "
        lines += line + "\n"

        return lines

    def _createComponentGroupRowsLines(self, group: _output.ComponentGroup):
        components = [c for c in group.components.factors if c.cost > 0]

        if not components:
            return ""

        lines = ""

        firstComponent, *remainingComponents = components
        line = self._createComponentRowLine(firstComponent, group, withGroupName=True)
        lines += line + "\n"

        for component in remainingComponents:
            line = self._createComponentRowLine(component, group, withGroupName=False)
            lines += line + "\n"

        if len(components) > 1:
            groupLines = self._createGroupRowsLines(components, group)
            lines += groupLines

        return lines

    def _createGroupRowsLines(self, components: _tp.Sequence[_output.CostFactor], group: _output.ComponentGroup):
        groupLines = ""

        cost: _common.UncertainFloat
        cost = sum(c.cost for c in components)
        costShare = 100 * cost / self._totalCost

        formattedCost = cost.format(precision=1)
        formattedCostShare = costShare.format(precision=1)

        line = r"&\cline{1-5}"
        groupLines += line + "\n"

        line = rf" & \textbf{{Total {group.name}}} & & & & {formattedCost} ({formattedCostShare}\%) \\"

        groupLines += line + "\n"

        return groupLines

    def _createComponentRowLine(self, component: _output.CostFactor,
                                group: _output.ComponentGroup,
                                withGroupName: bool)\
            -> str:
        groupName = group.name
        formattedGroupNameOrEmpty = rf"\textbf{{{groupName}}}" if withGroupName else ""

        size = component.value
        cost = component.cost
        costShare = 100 * component.cost / self._totalCost

        formattedCost = cost.format(precision=1)
        formattedCostShare = costShare.format(precision=1)

        definition = component.definition
        compName = definition.name
        offset = definition.cost.coeffs.offset.format(precision=0)
        slope = definition.cost.coeffs.slope.format(precision=0)
        unit = definition.cost.variable.unit
        lifetime = component.period

        line = rf"{formattedGroupNameOrEmpty} & {compName} & {offset}+{slope}/{unit} "\
               rf"& {size:.2f} {unit} & {lifetime} & {formattedCost} ({formattedCostShare}\%) \\"

        return line
