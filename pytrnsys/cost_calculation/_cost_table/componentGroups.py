__all__ = ['createLines']


import typing as _tp

from .._models import output as _output
from .._models import common as _common


def createLines(componentGroups: _output.ComponentGroups, totalCostScaleFactor):
    lines = ""
    for group in componentGroups.groups:
        groupLines = _createComponentGroupRowsLines(group, componentGroups.cost)

        lines += groupLines + r"\hline \\" + "\n"

    totalCost = componentGroups.cost * totalCostScaleFactor
    formattedTotalCost = totalCost.format(precision=2)

    line = rf" & \textbf{{Total Investment Cost}} & & & & \textbf{{{formattedTotalCost}}} (100\%) \\ "
    lines += line + "\n"

    return lines


def _createComponentGroupRowsLines(group: _output.ComponentGroup, totalCost: _common.UncertainFloat):
    components = [c for c in group.components.factors if c.cost > 0]

    if not components:
        return ""

    lines = ""

    firstComponent, *remainingComponents = components
    line = _createComponentRowLine(firstComponent, totalCost, group.name)
    lines += line + "\n"

    for component in remainingComponents:
        line = _createComponentRowLine(component, totalCost, groupName=None)
        lines += line + "\n"

    if len(components) > 1:
        groupLines = _createGroupRowsLines(group, totalCost)
        lines += groupLines

    return lines


def _createComponentRowLine(component: _output.CostFactor,
                            totalCost: _common.UncertainFloat,
                            groupName: _tp.Optional[str]) \
        -> str:
    formattedGroupNameOrEmpty = rf"\textbf{{{groupName}}}" if groupName else ""

    cost = component.cost
    costShare = 100 * component.cost / totalCost

    formattedCost = cost.format(precision=1)
    formattedCostShare = costShare.format(precision=1)

    compName = component.name
    offset = component.coeffs.offset.format(precision=0)
    slope = component.coeffs.slope.format(precision=0)
    size = component.value.value
    unit = component.value.unit
    lifetime = component.lifetimeInYears

    line = rf"{formattedGroupNameOrEmpty} & {compName} & {offset}+{slope}/{unit} " \
           rf"& {size:.2f} {unit} & {lifetime} & {formattedCost} ({formattedCostShare}\%) \\"

    return line


def _createGroupRowsLines(group: _output.ComponentGroup, totalCost: _common.UncertainFloat):
    groupLines = ""

    cost = group.components.cost
    costShare = 100 * cost / totalCost

    formattedCost = cost.format(precision=1)
    formattedCostShare = costShare.format(precision=1)

    line = r"&\cline{1-5}"
    groupLines += line + "\n"

    line = rf" & \textbf{{Total {group.name}}} & & & & {formattedCost} ({formattedCostShare}\%) \\"

    groupLines += line + "\n"

    return groupLines

