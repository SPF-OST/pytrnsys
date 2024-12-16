import dataclasses as _dc
import pathlib as _pl

import lark as _lark

import pytrnsys.ddck.replaceTokens.tokens as _tokens


@_dc.dataclass
class ReplaceTokenError(Exception):
    token: _tokens.Token
    errorMessage: str

    @classmethod
    def fromTree(
        cls, tree: _lark.Tree, errorMessage: str
    ) -> "ReplaceTokenError":
        return cls.fromMetaOrToken(tree.meta, errorMessage)

    @staticmethod
    def fromMetaOrToken(
        metaOrToken: _lark.tree.Meta | _lark.Token, errorMessage: str
    ) -> "ReplaceTokenError":
        token = _tokens.Token.fromMetaOrToken(metaOrToken)
        return ReplaceTokenError(token, errorMessage)

    def getErrorMessage(
        self,
        originalInput: str,
        filePath: _pl.Path | None = None,
        nBeginContextLines: int = 5,
        nEndContextLines=5,
    ) -> str:
        context = self._getContext(
            originalInput, nBeginContextLines, nEndContextLines
        )

        message = f"""\
{self.errorMessage}:

At {filePath or "<string>"}:{self.token.startLine}:

{context}
"""
        return message

    def _getContext(
        self,
        originalInput: str,
        nBeginContextLines: int = 5,
        nEndContextLines=5,
    ) -> str:
        originalInputLines = originalInput.splitlines()

        startLineNumber = max(self.token.startLine - nBeginContextLines, 1)
        endLineNumber = min(
            self.token.endLine + nEndContextLines, len(originalInputLines)
        )

        leadingContextLines = originalInputLines[
            startLineNumber : self.token.startLine - 1
        ]
        offendingLine = originalInputLines[self.token.startLine - 1]
        laggingContextLines = originalInputLines[
            self.token.startLine : endLineNumber
        ]

        indicatorLine = self._createIndicatorLine(
            self.token.startColumn, self.token.endColumn
        )

        contextLines = [
            *leadingContextLines,
            offendingLine,
            indicatorLine,
            *laggingContextLines,
        ]
        context = "\n".join(contextLines)

        return context

    @staticmethod
    def _createIndicatorLine(
        indicatorsStartColumn: int, indicatorsEndColumn: int
    ) -> str:
        nIndicators = indicatorsEndColumn - indicatorsStartColumn
        indicatorLine = (
            f"{' ' * (indicatorsStartColumn - 1)}{'^' * nIndicators}"
        )
        return indicatorLine
