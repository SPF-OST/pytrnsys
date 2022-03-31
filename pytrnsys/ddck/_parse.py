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


class ParsingException(Exception):
    pass


def parseDdck(ddckFilePath: _pl.Path) -> _lark.Tree:
    ddckText = ddckFilePath.read_text()

    try:
        tree = _PARSER.parse(ddckText)
    except _lark.UnexpectedInput as larkException:
        raise ParsingException(f"Error parsing file {ddckFilePath}") from larkException

    return tree
