import pathlib as _pl
import pkgutil as _pu

import lark as _lark

import pytrnsys.ddck as _ddck


def _createParser() -> _lark.Lark:
    data = _pu.get_data(_ddck.__name__, "ddck.lark")
    assert data, "Could not find ddck Lark grammar file."
    grammar = data.decode()
    parser = _lark.Lark(grammar, parser="earley", propagate_positions=True)
    return parser


_PARSER = _createParser()


def parseDdck(ddckFilePath: _pl.Path) -> _lark.Tree:
    ddckText = ddckFilePath.read_text()

    tree = _PARSER.parse(ddckText)

    return tree
