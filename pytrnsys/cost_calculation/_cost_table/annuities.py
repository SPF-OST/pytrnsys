__all__ = ['createLines']

from .._models import output as _output


def createLines(output: _output.Output):
    symbol = "\\%"
    line = "\\hline \\\\ \n"
    lines = line
    line = "\\hline \\\\ \n"
    lines = lines + line
    costUnit = " $CHF/a$"
    line = "Annuity & Annuity (yearly costs over lifetime)  &&& & %2.0f% s  \\\\ \n" \
           % (output.annuity.mean, costUnit)
    lines = lines + line
    line = " & Share of Investment & &&& %2.0f%s (%2.0f%s) \\\\ \n" % (
        output.componentGroups.annuity.mean, costUnit,
        output.componentGroups.annuity.mean * 100. / output.annuity.mean, symbol)
    lines = lines + line
    line = " & Share of Electricity  & %.0f+%.2f/kWh & %2.0f kWh&  & %2.0f%s (%2.0f%s)\\\\ \n" % (
        output.electricity.costElecFix, output.electricity.costElecKWh,
        output.electricity.electricityDemandInKWh, output.electricity.annuity, costUnit,
        output.electricity.annuity * 100. / output.annuity.mean, symbol)
    lines = lines + line
    line = " & Share of Maintenance & &&& %2.0f%s (%2.0f%s)\\\\ \n" % (
        output.componentGroups.maintenanceCost.mean, costUnit,
        output.componentGroups.maintenanceCost.mean * 100. / output.annuity.mean, symbol)
    lines = lines + line
    for yc in output.yearlyCosts.factors:
        line = " & Share of %s & %.0f+%.2f/%s & %.0f  %s & & %2.0f%s (%2.0f%s)\\\\ \n" % (
            yc.name,
            yc.coeffs.offset.mean,
            yc.coeffs.slope.mean,
            yc.value.unit,
            yc.value.value, yc.value.unit, yc.cost.mean, costUnit,
            yc.cost.mean * 100. / output.annuity.mean, symbol)
        lines = lines + line
    line = " & Share of Residual Value &&& & %2.0f%s (%2.0f%s)\\\\ \n" % (
        -output.residualCost.annuity.mean, costUnit,
        -output.residualCost.annuity.mean * 100. / output.annuity.mean, symbol)
    lines = lines + line
    line = "Present Value  & Present Value of all costs  & &&& %2.2f% s  \\\\ \n" % (output.npvCost.mean, " CHF")
    lines = lines + line
    line = "\\hline \\\\ \n"
    lines = lines + line
    hgcUnit = "$Rp./kWh$"
    line = " Energy Generation Costs & Using annuity: &&& %2.2f & %s \\\\ \n" \
           % (output.heatGenerationCost.mean * 100., hgcUnit)
    lines = lines + line
    return lines
