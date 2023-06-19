import dataclasses as _dc
import functools as _ft
import typing as _tp


@_dc.dataclass
class Token:
    startLine: int
    startColumn: int
    startIndex: int
    endIndex: int

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


def replaceTokensWithReplacements(
    inputDdckContent: str, tokens: _tp.Sequence[Token], replacements: _tp.Sequence[str]
) -> str:
    sortedTokens, sortedReplacements = _getSortedTokensAndReplacements(tokens, replacements)
    sortedTokensWithoutCovers, sortedReplacementsWithoutCovers = _removeCoveredTokens(sortedTokens, sortedReplacements)
    outputDdckContent = _replaceSortedNonOverlappingTokens(
        inputDdckContent, sortedTokensWithoutCovers, sortedReplacementsWithoutCovers
    )
    return outputDdckContent


def _getSortedTokensAndReplacements(
    tokens: _tp.Sequence[Token], replacements: _tp.Sequence[str]
) -> _tp.Tuple[_tp.Sequence[Token], _tp.Sequence[str]]:
    if not len(tokens) == len(replacements):
        raise ValueError("`tokens` and `replacements` must be of the same length.")

    if len(tokens) == len(replacements) == 0:
        return [], []

    if len(tokens) == len(replacements) == 1:
        return tokens, replacements

    tokenAndReplacements = zip(tokens, replacements)

    key = _ft.cmp_to_key(_compareTokensEarliestAndLongestFirst)
    sortedTokenAndReplacements = list(sorted(tokenAndReplacements, key=key))

    sortedTokens, sortedReplacements = zip(*sortedTokenAndReplacements)

    return sortedTokens, sortedReplacements


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


def _removeCoveredTokens(
    sortedTokens: _tp.Sequence[Token], sortedReplacements: _tp.Sequence[str]
) -> _tp.Tuple[_tp.Sequence[Token], _tp.Sequence[str]]:
    if len(sortedTokens) == len(sortedReplacements) <= 1:
        return sortedTokens, sortedReplacements

    tokensWithoutOverlap = [sortedTokens[0]]
    replacementsWithoutOverlap = [sortedReplacements[0]]
    for token, replacement in zip(sortedTokens[1:], sortedReplacements[1:]):
        lastTokenWithoutOverlap = tokensWithoutOverlap[-1]
        if lastTokenWithoutOverlap.endIndex < token.startIndex:
            tokensWithoutOverlap.append(token)
            replacementsWithoutOverlap.append(replacement)
            continue

        if lastTokenWithoutOverlap.endIndex >= token.endIndex:
            continue

        raise ValueError("Tokens must either not overlap or fully cover each other.")

    return tokensWithoutOverlap, replacementsWithoutOverlap


def _replaceSortedNonOverlappingTokens(
    content: str, tokens: _tp.Sequence[Token], replacements: _tp.Sequence[str]
) -> str:
    if len(tokens) != len(replacements):
        raise ValueError("`tokens` and `replacements` must be of the same length.")

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
