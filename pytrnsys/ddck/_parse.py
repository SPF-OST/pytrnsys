import pkgutil as _pu

import lark as _lark

import pytrnsys.ddck as _ddck
import pytrnsys.utils.result as _res


def _createParser() -> _lark.Lark:
    data = _pu.get_data(_ddck.__name__, "ddck.lark")
    assert data, "Could not find ddck Lark grammar file."
    grammar = data.decode()
    parser = _lark.Lark(grammar, parser="earley", propagate_positions=True)
    return parser


_PARSER = _createParser()


class ParsingException(Exception):
    pass


def parseDdck(ddckContent: str) -> _res.Result[_lark.Tree]:
    try:
        tree = _PARSER.parse(ddckContent)
    except _lark.UnexpectedInput as larkException:
        return _res.Error(str(larkException))

    return tree
