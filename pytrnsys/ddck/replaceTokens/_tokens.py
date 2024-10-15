import collections.abc as _cabc
import dataclasses as _dc
import functools as _ft
import typing as _tp

import lark as _lark


@_dc.dataclass
class Token:
    startLine: int
    startColumn: int
    startIndex: int
    endIndex: int

    @staticmethod
    def fromTree(tree: _lark.Tree) -> "Token":
        return Token.fromMetaOrToken(tree.meta)

    @staticmethod
    def fromMetaOrToken(metaOrToken: _lark.tree.Meta | _lark.Token) -> "Token":
        if (
            metaOrToken.line is None
            or metaOrToken.column is None
            or metaOrToken.start_pos is None
            or metaOrToken.end_pos is None
        ):
            raise ValueError("All meta attributes of token must be non-None.")

        return Token(
            metaOrToken.line,
            metaOrToken.column,
            metaOrToken.start_pos,
            metaOrToken.end_pos,
        )

    def shift(self, offset: int) -> "Token":
        shiftedStartIndex = offset + self.startIndex
        shiftedEndIndex = offset + self.endIndex
        return _dc.replace(self, startIndex=shiftedStartIndex, endIndex=shiftedEndIndex)

    def lengthChange(self, replacementString) -> int:
        lengthBeforeReplacing = self.endIndex - self.startIndex
        lengthAfterReplacing = len(replacementString)
        lengthChange = lengthAfterReplacing - lengthBeforeReplacing
        return lengthChange

    def __post_init__(self):
        if self.startIndex > self.endIndex:
            raise ValueError("End index must be greater than end index.")

        if self.startIndex < 0 or self.endIndex < 0:
            raise ValueError("Start and end index must be > 0.")


TokensAndReplacement = _cabc.Sequence[_tp.Tuple[Token, str]]


def replaceTokensWithReplacements(inputDdckContent: str, tokensAndReplacement: TokensAndReplacement) -> str:
    sortedTokensAndReplacement = _getSortedTokensAndReplacement(tokensAndReplacement)
    sortedNonOverlappingTokensAndReplacement = _removeCoveredTokens(sortedTokensAndReplacement)
    outputDdckContent = _replaceSortedNonOverlappingTokens(inputDdckContent, sortedNonOverlappingTokensAndReplacement)
    return outputDdckContent


def _getSortedTokensAndReplacement(tokensAndReplacement: TokensAndReplacement) -> TokensAndReplacement:
    if len(tokensAndReplacement) <= 1:
        return tokensAndReplacement

    key = _ft.cmp_to_key(_compareTokensEarliestAndLongestFirst)
    sortedTokensAndReplacement = list(sorted(tokensAndReplacement, key=key))

    return sortedTokensAndReplacement


def _compareTokensEarliestAndLongestFirst(
    tokenAndReplacement1: _tp.Tuple[Token, str], tokenAndReplacement2: _tp.Tuple[Token, str]
) -> int:
    token1 = tokenAndReplacement1[0]
    token2 = tokenAndReplacement2[0]

    if token1.startIndex < token2.startIndex:
        return -1

    if token1.startIndex > token2.startIndex:
        return 1

    if token1.endIndex == token2.endIndex:
        return 0

    return -1 if token1.endIndex > token2.endIndex else 1


def _removeCoveredTokens(sortedTokensAndReplacement: TokensAndReplacement) -> TokensAndReplacement:
    if len(sortedTokensAndReplacement) <= 1:
        return sortedTokensAndReplacement

    tokensAndReplacementWithoutOverlap = [sortedTokensAndReplacement[0]]
    for tokenAndReplacement in sortedTokensAndReplacement[1:]:
        token = tokenAndReplacement[0]

        lastTokenWithoutOverlap, _ = tokensAndReplacementWithoutOverlap[-1]
        if lastTokenWithoutOverlap.endIndex < token.startIndex:
            tokensAndReplacementWithoutOverlap.append(tokenAndReplacement)
            continue

        if lastTokenWithoutOverlap.endIndex >= token.endIndex:
            continue

        raise ValueError("Tokens must either not overlap or fully cover each other.")

    return tokensAndReplacementWithoutOverlap


def _replaceSortedNonOverlappingTokens(content: str, tokensAndReplacements: TokensAndReplacement) -> str:
    if len(tokensAndReplacements) <= 1:
        return content

    tokens, replacements = zip(*tokensAndReplacements)

    if len(tokens) > 1:
        previousAndCurrentTokens = list(zip(tokens[:-1], tokens[1:]))

        areTokensSorted = all(p.startIndex < c.startIndex for p, c in previousAndCurrentTokens)
        if not areTokensSorted:
            raise ValueError("`tokens` must be sorted by start index ascending.")

        doAnyTokensOverlap = any(p.endIndex >= c.startIndex for p, c in previousAndCurrentTokens)
        if doAnyTokensOverlap:
            raise ValueError("`tokens` must not overlap.")

    offset = 0
    resultContent = content
    for token, replacement in zip(tokens, replacements):
        resultContent = _replaceToken(
            resultContent,
            token.shift(offset),
            replacement,
        )
        offset += token.lengthChange(replacement)

    return resultContent


def _replaceToken(content: str, token: Token, replacement: str) -> str:
    return content[: token.startIndex] + replacement + content[token.endIndex :]
