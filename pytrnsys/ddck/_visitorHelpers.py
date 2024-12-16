import typing as _tp
from collections import abc as _cabc

import lark as _lark


def getSubtree(treeData: str, tree: _lark.Tree) -> _lark.Tree:
    subtreeOrNone = getSubtreeOrNone(treeData, tree)

    if not subtreeOrNone:
        raise ValueError(f"No subtree `{treeData}` found for `{tree.data}`.")

    return subtreeOrNone


def getSubtrees(treeData: str, tree: _lark.Tree) -> _cabc.Sequence[_lark.Tree]:
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


def getChildTokenValue(tokenType: str, tree: _lark.Tree, conversionFunction: _cabc.Callable[[str], _T]) -> _T:
    token = getChildTokenValueOrNone(tokenType, tree, conversionFunction)

    if not token:
        raise ValueError(f"`{tree.data}` doesn't contain a direct child token of type `{tokenType}`.")
    tokenValue = token

    return tokenValue


def getChildTokenValueOrNone(
    tokenType: str, tree: _lark.Tree, conversionFunction: _tp.Callable[[str], _T]
) -> _T | None:
    tokenOrNone = getChildTokenOrNone(tokenType, tree)

    if not tokenOrNone:
        return None

    convertedValue = conversionFunction(tokenOrNone.value)

    return convertedValue


def getChildTokenValues(tokenType: str, tree: _lark.Tree) -> _cabc.Sequence[str]:
    return [t.value for t in getChildTokens(tokenType, tree)]


def getChildToken(tokenType: str, tree: _lark.Tree) -> _lark.Token:
    tokenOrNone = getChildTokenOrNone(tokenType, tree)

    if not tokenOrNone:
        raise ValueError(f"Multiple tokens of type `{tokenType}` found for `{tree.data}`.")
    token = tokenOrNone

    return token


def getChildTokenOrNone(tokenType: str, tree: _lark.Tree) -> _lark.Token | None:
    tokens = getChildTokens(tokenType, tree)

    nTokens = len(tokens)
    if nTokens == 0:
        return None

    if nTokens > 1:
        raise ValueError(f"More than one token of type `{tokenType}` found.")

    token = tokens[0]

    return token


def getChildTokens(tokenType: str, tree: _lark.Tree) -> _cabc.Sequence[_lark.Token]:
    return [c for c in tree.children if isinstance(c, _lark.Token) and c.type == tokenType]
