# pylint: skip-file
# type: ignore

__all__ = ["createLines"]

from .._models import output as _output


def createLines(output: _output.Output):
    line = rf"Annuity & Annuity (yearly costs over lifetime)  &&& & {output.annuity:2.0f} /a  \\"
    lines = line + "\n"

    line = (
        rf" & Share of Investment & &&& {output.componentGroups.annuity:2.0f} /a "
        rf"({output.componentGroups.annuity * 100 / output.annuity:2.0f}\%) \\"
    )
    lines += line + "\n"

    e = output.electricity
    line = (
        rf" & Share of Electricity & {e.costElecFix:.0f}+{e.costElecKWh:.2f}/kWh & "
        rf"{e.electricityDemandInKWh:2.0f} kWh &  & {e.annuity:2.0f} /a "
        rf"({e.annuity * 100 / output.annuity:2.0f}\%)\\"
    )
    lines += line + "\n"

    maintenanceCost = output.componentGroups.maintenanceCost
    line = (
        rf" & Share of Maintenance & &&& {maintenanceCost:2.0f} /a"
        rf" ({maintenanceCost * 100 / output.annuity:2.0f}\%)\\ "
    )
    lines += line + "\n"

    for yc in output.yearlyCosts.factors:
        line = (
            rf" & Share of {yc.name} & {yc.coeffs.offset:.0f}+{yc.coeffs.slope:.2f}/{yc.value.unit} "
            rf"& {yc.value.value:.0f} {yc.value.unit} & & {yc.cost:2.0f} /a "
            rf"({yc.cost * 100 / output.annuity:2.0f}\%)\\"
        )
        lines += line + "\n"

    residualCost = output.residualCost.annuity
    line = (
        rf" & Share of Residual Value &&& & {residualCost:2.0f} /a " rf"({residualCost * 100 / output.annuity:2.0f}\%)\\"
    )
    lines += line + "\n"

    line = rf"Present Value  & Present Value of all costs  & &&& {output.npvCost:2.2f} CHF \\"
    lines += line + "\n"

    lines += r"\hline \\ " + "\n"

    line = rf" Energy Generation Costs & Using annuity: &&& {output.heatGenerationCost * 100:2.2f} " rf"& Rp./kWh \\"
    lines += line

    return lines
