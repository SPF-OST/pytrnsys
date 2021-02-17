import typing as _tp
import dataclasses as _dc

import pytrnsys.cost_calculation.model as _model

__all__ = ['ComponentGroupsRowsLinesWriter']


class ComponentGroupsRowsLinesWriter:
    def __init__(self, totalCost, totalCostScaleFactor):
        self._totalCost = totalCost
        self._totalCostScaleFactor = totalCostScaleFactor

    def createLines(self, componentGroups, sizesByComponent):
        lines = ""
        for group in componentGroups:
            groupLines = self._createComponentGroupRowsLines(group, sizesByComponent)

            lines += groupLines + r"\hline \\" + "\n"

        scaledTotalCost = self._totalCost * self._totalCostScaleFactor
        line = rf" & \\textbf{{Total Investment Cost}} & & & & \textbf{{{scaledTotalCost:.2f}}} (100\%) \\ "
        lines += line + "\n"

        return lines

    def _createComponentGroupRowsLines(self, group, sizesByComponent):
        components = self._getSizedComponentsWithPositiveCost(group.components, sizesByComponent)

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

    def _createGroupRowsLines(self, components, group):
        groupLines = ""

        cost = sum(c.cost for c in components)
        costShare = 100 * cost.value / self._totalCost

        formattedCost = cost.format(precision=1)

        line = r"&\cline{1-5}"
        groupLines += line + "\n"

        line = rf" & \textbf{{Total {group.name}}} & & & & {formattedCost} ({costShare:.1f}\%) \\"

        groupLines += line + "\n"

        return groupLines

    def _createComponentRowLine(self, sizedComponent: "_SizedComponent",
                                group: _model.ComponentGroup,
                                withGroupName: bool)\
            -> str:
        groupName = group.name
        formattedGroupNameOrEmpty = rf"\textbf{{{groupName}}}" if withGroupName else ""

        size = sizedComponent.size
        cost = sizedComponent.cost.format(precision=1)
        costShare = 100 * sizedComponent.cost.value / self._totalCost

        component = sizedComponent.component
        compName = component.name
        offset = component.cost.coeffs.offset.format(precision=0)
        slope = component.cost.coeffs.slope.format(precision=0)
        unit = component.cost.variable.unit
        lifetime = component.lifetimeInYears

        line = rf"{formattedGroupNameOrEmpty} & {compName} & {offset}+({slope})/{unit} "\
               rf"& {size:.2f} {unit} & {lifetime} & {cost} ({costShare:.1f}\%) \\"

        return line

    @staticmethod
    def _getSizedComponentsWithPositiveCost(components: _tp.Sequence[_model.Component], sizesByComponent) \
            -> _tp.Sequence["_SizedComponent"]:
        result = []
        for component in components:
            size = sizesByComponent[component]

            sizedComponent = _SizedComponent(component, size)
            if sizedComponent.cost.max > 0:
                result.append(sizedComponent)

        return result


@_dc.dataclass(frozen=True)
class _SizedComponent:
    component: _model.Component
    size: float

    @property
    def cost(self) -> _model.UncertainFloat:
        return self.component.cost.at(self.size)
