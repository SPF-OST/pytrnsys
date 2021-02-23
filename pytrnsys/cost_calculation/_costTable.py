__all__ = ['ComponentGroupsRowsLinesWriter']


import typing as _tp
import dataclasses as _dc

import pytrnsys.cost_calculation._model as _model


class ComponentGroupsRowsLinesWriter:
    def __init__(self, totalCost: _model.UncertainFloat, totalCostScaleFactor: float):
        self._totalCost = totalCost
        self._totalCostScaleFactor = totalCostScaleFactor

    def createLines(self, componentGroups, sizesByComponent):
        lines = ""
        for group in componentGroups:
            groupLines = self._createComponentGroupRowsLines(group, sizesByComponent)

            lines += groupLines + r"\hline \\" + "\n"

        totalCost = self._totalCost * self._totalCostScaleFactor
        formattedTotalCost = totalCost.format(precision=2)

        line = rf" & \textbf{{Total Investment Cost}} & & & & \textbf{{{formattedTotalCost}}} (100\%) \\ "
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

    def _createGroupRowsLines(self, components: _tp.Sequence["_SizedComponent"], group):
        groupLines = ""

        cost: _model.UncertainFloat
        cost = sum(c.cost for c in components)
        costShare = 100 * cost / self._totalCost

        formattedCost = cost.format(precision=1)
        formattedCostShare = costShare.format(precision=1)

        line = r"&\cline{1-5}"
        groupLines += line + "\n"

        line = rf" & \textbf{{Total {group.name}}} & & & & {formattedCost} ({formattedCostShare}\%) \\"

        groupLines += line + "\n"

        return groupLines

    def _createComponentRowLine(self, sizedComponent: "_SizedComponent",
                                group: _model.ComponentGroup,
                                withGroupName: bool)\
            -> str:
        groupName = group.name
        formattedGroupNameOrEmpty = rf"\textbf{{{groupName}}}" if withGroupName else ""

        size = sizedComponent.size
        cost = sizedComponent.cost
        costShare = 100 * sizedComponent.cost / self._totalCost

        formattedCost = cost.format(precision=1)
        formattedCostShare = costShare.format(precision=1)

        component = sizedComponent.component
        compName = component.name
        offset = component.cost.coeffs.offset.format(precision=0)
        slope = component.cost.coeffs.slope.format(precision=0)
        unit = component.cost.variable.unit
        lifetime = component.lifetimeInYears

        line = rf"{formattedGroupNameOrEmpty} & {compName} & {offset}+{slope}/{unit} "\
               rf"& {size:.2f} {unit} & {lifetime} & {formattedCost} ({formattedCostShare}\%) \\"

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
