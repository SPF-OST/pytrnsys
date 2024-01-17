import dataclasses as _dc
import io as _io
import re as _re
import typing as _tp
import logging as _log

_UNIT_VARIABLE_GROUP_NAME = "unitVariable"

_CHANGE_ASSIGN_STATEMENT_PATTERN = _re.compile(
    rf"ASSIGN\s+\S+\s+(?P<{_UNIT_VARIABLE_GROUP_NAME}>[A-Za-z_]+[A-Za-z_0-9]*)", flags=_re.IGNORECASE
)


@_dc.dataclass(frozen=True)
class AssignStatement:
    path: str
    unitVariableName: str


def replaceAssignStatementsBasedOnUnitVariables(
    originalDeckContent: str, newAssignStatements: _tp.Sequence[AssignStatement], logger: _log.Logger
) -> str:
    if not newAssignStatements:
        return originalDeckContent

    newStatementsByCaseFoldedName = {s.unitVariableName.casefold(): s for s in newAssignStatements}

    matchingNewAssignStatements = set()
    unprocessedDeckContent = _io.StringIO(originalDeckContent)
    updatedDeckContent = _io.StringIO()
    previousMatch: _tp.Optional[_re.Match] = None
    for currentMatch in _CHANGE_ASSIGN_STATEMENT_PATTERN.finditer(originalDeckContent):
        matchingNewAssignStatement = _getMatchingNewAssignStatementOrNone(currentMatch, newStatementsByCaseFoldedName)
        if matchingNewAssignStatement:
            matchingNewAssignStatements.add(matchingNewAssignStatement)

        _replaceCurrentMatchWithNewAssignStatement(
            currentMatch, matchingNewAssignStatement, previousMatch, unprocessedDeckContent, updatedDeckContent
        )

        previousMatch = currentMatch

    unmatchedNewAssignStatements = set(newAssignStatements) - matchingNewAssignStatements
    if unmatchedNewAssignStatements:
        formattedUnmatchedNewAssignStatements = "\t\n".join(
            f"assign {s.path} {s.unitVariableName}" for s in unmatchedNewAssignStatements
        )
        warningMessage = f"The following assign statements were not matched:\n\t{formattedUnmatchedNewAssignStatements}"
        logger.warning("%s", warningMessage)

    unchangedPartBetweenLastAssignIfAnyAndEnd = unprocessedDeckContent.read()
    updatedDeckContent.write(unchangedPartBetweenLastAssignIfAnyAndEnd)

    updateDeckContentString = updatedDeckContent.getvalue()
    return updateDeckContentString


def _getMatchingNewAssignStatementOrNone(
    currentMatch: _re.Match, newStatementsByCaseFoldedName: _tp.Mapping[str, AssignStatement]
) -> _tp.Optional[AssignStatement]:
    unitVariableName = currentMatch.group(_UNIT_VARIABLE_GROUP_NAME)
    caseFoldedName = unitVariableName.casefold()
    newAssignStatement = newStatementsByCaseFoldedName.get(caseFoldedName)
    return newAssignStatement


def _replaceCurrentMatchWithNewAssignStatement(
    currentMatch: _re.Match,
    newAssignStatement: _tp.Optional[AssignStatement],
    previousMatch: _tp.Optional[_re.Match],
    unprocessedDeckContent: _io.StringIO,
    updatedDeckContent: _io.StringIO,
) -> None:
    unchangedPartLength = currentMatch.start() - previousMatch.end() if previousMatch else currentMatch.start()
    unchangedPart = unprocessedDeckContent.read(unchangedPartLength)
    updatedDeckContent.write(unchangedPart)

    originalAssignStatement = currentMatch.group()
    originalAssignStatementLength = len(originalAssignStatement)
    _ = unprocessedDeckContent.read(originalAssignStatementLength)

    if newAssignStatement:
        newPath = newAssignStatement.path
        updatedAssignStatement = f"ASSIGN {newPath} {newAssignStatement.unitVariableName}"
        updatedDeckContent.write(updatedAssignStatement)
    else:
        updatedDeckContent.write(originalAssignStatement)
