import collections.abc as _cabc
import pathlib as _pl

import lark as _lark
import lark.visitors as _lv

import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.utils.result as _res
import pytrnsys.utils.warnings as _warn
from . import _visitorHelpers as _vh
from ._parse import parse as _parse


class _CollectUsedTypesVisitor(_lv.Visitor_Recursive):
    def __init__(self) -> None:
        self.typeNumbers = list[int]()

    def header(self, tree: _lark.Tree):
        typeNumberString = _vh.getChildTokenValue("type_number", tree)
        typeNumber = int(typeNumberString)
        self.typeNumbers.append(typeNumber)

    @staticmethod
    def collectTypeNumbers(globalTree: _lark.Tree) -> _cabc.Sequence[int]:
        visitor = _CollectUsedTypesVisitor()
        visitor.visit(globalTree)
        return visitor.typeNumbers


_TYPE_NUMBERS_WHICH_CAN_ONLY_BE_USED_GLOBALLY = [*range(1924, 1930 + 1), 935, 9351, 9352]


def checkDefaultVisibility(
    ddckFilePath: _pl.Path, defaultVisibility: _dv.DefaultVisibility
) -> _res.Result[_warn.ValueWithWarnings[None]]:
    if defaultVisibility == _dv.DefaultVisibility.GLOBAL:
        return _warn.ValueWithWarnings.create(None)

    try:
        ddckFileContent = ddckFilePath.read_text("UTF8")
    except OSError as error:
        return _res.Error(f"An error occurred opening the file `{ddckFilePath}`: {error}")

    result = _parse.parseDdck(ddckFileContent)
    if _res.isError(result):
        return result.withContext(f"Parsing the file `{ddckFilePath}`")
    tree = result

    usedTypeNumbers = _CollectUsedTypesVisitor.collectTypeNumbers(tree)

    offendingUsedTypeNumbers = [n in _TYPE_NUMBERS_WHICH_CAN_ONLY_BE_USED_GLOBALLY for n in usedTypeNumbers]

    if not offendingUsedTypeNumbers:
        return _warn.ValueWithWarnings.create(None)

    formattedOffendingUsedTypeNumbers = "\n".join(f"\t {n}" for n in offendingUsedTypeNumbers)

    warning = f"""\
The following TRNSYS types were found to be used in the ddck file `{ddckFilePath}`:
{formattedOffendingUsedTypeNumbers}
Usually, these types are used in ddck files which should be included *globally* in your
config file like so:

    <path-variable-name> <ddck-file-name> global

The simulation will try to proceed anyway, but if you run into errors consider using importing
this file globally.
"""

    return _warn.ValueWithWarnings.create(None, warning)
