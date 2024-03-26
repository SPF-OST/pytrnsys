import pytest as _pt

import pytrnsys.plot.plotGle as _pgle


@_pt.mark.parametrize("iColor, expectedColor", [
    (2, "#2ca02c"),
    (27, "black"),
    (28, "#d62728"),
    (500, "firebrick")
])
def test_colorRestarting(iColor, expectedColor):
    plotter = _pgle.PlotGle(".")
    color = plotter.colorGLE(iColor)
    assert color == expectedColor
