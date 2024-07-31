import typing as _tp
from collections import abc as _cabc

import lark as _lark


def getChildTokenValue(tokenType: str, tree: _lark.Tree) -> str:
    tokenValueOrNone = getChildTokenValueOrNone(tokenType, tree)
    if not tokenValueOrNone:
        raise ValueError(f"`{tree.data}` doesn't contain a direct child token of type `{tokenType}`.")

    return tokenValueOrNone


def getChildTokenValueOrNone(tokenType: str, tree: _lark.Tree) -> _tp.Optional[str]:
    values = getChildTokenValues(tokenType, tree)

    nValues = len(values)
    if nValues == 0:
        return None

    if nValues > 1:
        raise ValueError(f"More than one token of type {tokenType} found.")

    return values[0]


def getChildTokenValues(tokenType: str, tree: _lark.Tree) -> _cabc.Sequence[str]:
    return [c.value for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]
