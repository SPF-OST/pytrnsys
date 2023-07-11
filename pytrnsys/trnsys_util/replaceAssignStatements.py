import dataclasses as _dc
import io as _io
import re as _re
import typing as _tp

_UNIT_VARIABLE_GROUP_NAME = "unitVariable"

_CHANGE_ASSIGN_STATEMENT_PATTERN = _re.compile(
    rf"ASSIGN\s+\S+\s+(?P<{_UNIT_VARIABLE_GROUP_NAME}>[A-Za-z_]+[A-Za-z_0-9]*)", flags=_re.IGNORECASE
)


@_dc.dataclass
class AssignStatement:
    path: str
    unitVariableName: str


def replaceAssignStatementsBasedOnUnitVariables(
    originalDeckContent: str, newAssignStatements: _tp.Sequence[AssignStatement]
) -> str:
    if not newAssignStatements:
        return originalDeckContent

    newStatementsByCaseFoldedName = {s.unitVariableName.casefold(): s for s in newAssignStatements}

    unprocessedDeckContent = _io.StringIO(originalDeckContent)
    updatedDeckContent = _io.StringIO()
    previousMatch: _tp.Optional[_re.Match] = None
    for currentMatch in _CHANGE_ASSIGN_STATEMENT_PATTERN.finditer(originalDeckContent):
        _replaceAssignStatementBasedOnUnitVariable(
            previousMatch, currentMatch, unprocessedDeckContent, updatedDeckContent, newStatementsByCaseFoldedName
        )

        previousMatch = currentMatch

    unchangedPartBetweenLastAssignIfAnyAndEnd = unprocessedDeckContent.read()
    updatedDeckContent.write(unchangedPartBetweenLastAssignIfAnyAndEnd)

    updateDeckContentString = updatedDeckContent.getvalue()
    return updateDeckContentString


def _replaceAssignStatementBasedOnUnitVariable(
    previousMatch: _tp.Optional[_re.Match],
    currentMatch: _re.Match,
    unprocessedDeckContent: _io.StringIO,
    updatedDeckContent: _io.StringIO,
    newStatementsByCaseFoldedName: _tp.Mapping[str, AssignStatement],
) -> None:
    unitVariableName = currentMatch.group(_UNIT_VARIABLE_GROUP_NAME)

    caseFoldedName = unitVariableName.casefold()
    newAssignStatement = newStatementsByCaseFoldedName.get(caseFoldedName)

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
