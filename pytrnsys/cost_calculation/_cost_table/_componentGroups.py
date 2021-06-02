# pylint: skip-file
# type: ignore

__all__ = ["createLines"]


import typing as _tp

import pytrnsys.utils.uncertainFloat
from .._models import output as _output
from .._models import common as _common


def createLines(componentGroups: _output.ComponentGroups, shallUseKCHF):
    lines = ""
    for group in componentGroups.groups:
        groupLines = _createComponentGroupRowsLines(group, componentGroups.cost)

        lines += groupLines + r"\hline \\" + "\n"

    scaleFactor = 1e-3 if shallUseKCHF else 1
    totalCost = componentGroups.cost * scaleFactor

    line = rf" & \textbf{{Total Investment Cost}} & & & & \textbf{{{totalCost:.2f}}} (100\%) \\ "
    lines += line + "\n"

    return lines


def _createComponentGroupRowsLines(
    group: _output.ComponentGroup, totalCost: pytrnsys.utils.uncertainFloat.UncertainFloat
):
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


def _createComponentRowLine(
    component: _output.CostFactor, totalCost: pytrnsys.utils.uncertainFloat.UncertainFloat, groupName: _tp.Optional[str]
) -> str:
    formattedGroupNameOrEmpty = rf"\textbf{{{groupName}}}" if groupName else ""

    cost = component.cost
    costShare = 100 * component.cost / totalCost

    compName = component.name
    coeffs = component.coeffs
    size = component.value.value
    unit = component.value.unit
    lifetime = component.lifetimeInYears

    line = (
        rf"{formattedGroupNameOrEmpty} & {compName} & {coeffs.offset:.0f}+{coeffs.slope:.0f}/{unit} "
        rf"& {size:.2f} {unit} & {lifetime} & {cost:.1f} ({costShare:.1f}\%) \\"
    )

    return line


def _createGroupRowsLines(group: _output.ComponentGroup, totalCost: pytrnsys.utils.uncertainFloat.UncertainFloat):
    groupLines = ""

    cost = group.components.cost
    costShare = 100 * cost / totalCost

    line = r"&\cline{1-5}"
    groupLines += line + "\n"

    line = rf" & \textbf{{Total {group.name}}} & & & & {cost:0.1f} ({costShare:.1f}\%) \\"

    groupLines += line + "\n"

    return groupLines
