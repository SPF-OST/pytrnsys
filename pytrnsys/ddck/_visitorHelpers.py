import typing as _tp
from collections import abc as _cabc

import lark as _lark


def getSubtree(treeData: str, tree: _lark.Tree) -> _lark.Tree:
    subtreeOrNone = getSubtreeOrNone(treeData, tree)

    if not subtreeOrNone:
        raise ValueError(f"No subtree found for `{tree.data}`.")

    return subtreeOrNone


def getSubtrees(treeData: str, tree: _lark.Tree) -> _cabc.Sequence[_lark.Tree] | None:
    subtrees = [c for c in tree.children if isinstance(c, _lark.Tree) and c.data == treeData]
    return subtrees


def getSubtreeOrNone(treeData: str, tree: _lark.Tree) -> _lark.Tree | None:
    subtrees = getSubtrees(treeData, tree)

    if not subtrees:
        return None

    if len(subtrees) > 1:
        raise ValueError(f"More than one `{treeData}` subtree found for `{tree.data}`.")

    return subtrees[0]


def getSubtreesNonEmpty(treeData: str, tree: _lark.Tree) -> _cabc.Sequence[_lark.Tree]:
    subtrees = getSubtrees(treeData, tree)

    if not subtrees:
        raise ValueError(f"Could not find any subtrees `{treeData}` for `{tree.data}`.")

    return subtrees


_T = _tp.TypeVar("_T")


def toString(x: str) -> str:
    return x


def getChildTokenValue(tokenType: str, tree: _lark.Tree, conversionFunction: _cabc.Callable[[str], _T]) -> _T:
    tokenValueOrNone = getChildTokenValueOrNone(tokenType, tree, conversionFunction)

    if not tokenValueOrNone:
        raise ValueError(f"`{tree.data}` doesn't contain a direct child token of type `{tokenType}`.")
    tokenValue = tokenValueOrNone

    return tokenValue


def getChildTokenValueOrNone(
    tokenType: str, tree: _lark.Tree, conversionFunction: _tp.Callable[[str], _T]
) -> _T | None:
    values = getChildTokenValues(tokenType, tree)

    nValues = len(values)
    if nValues == 0:
        return None

    if nValues > 1:
        raise ValueError(f"More than one token of type {tokenType} found.")

    value = values[0]

    convertedValue = conversionFunction(value)

    return convertedValue


def getChildTokenValues(tokenType: str, tree: _lark.Tree) -> _cabc.Sequence[str]:
    return [c.value for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]
