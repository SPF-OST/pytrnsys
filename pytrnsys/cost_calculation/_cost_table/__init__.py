# pylint: skip-file
# type: ignore

__all__ = ["createLines"]

from .._models import output as _output

from . import _annuities as _ann
from . import _componentGroups as _cgs


def createLines(output: _output.Output, shallUseKCHF: bool) -> str:
    componentRowsLines = _cgs.createLines(output.componentGroups, shallUseKCHF)
    annuitiesLines = _ann.createLines(output)

    hline = r"\hline \\ " + "\n"
    lines = r"\\" + "\n" + componentRowsLines + hline + hline + annuitiesLines + "\n"

    return lines
