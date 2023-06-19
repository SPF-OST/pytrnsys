import dataclasses as _dc
import io as _io
import re as _re
import typing as _tp

_UNIT_VARIABLE_GROUP_NAME = "unitVariable"

_CHANGE_ASSIGN_STATEMENT_PATTERN = _re.compile(
    rf"ASSIGN\s+\S+\s+(?P<{_UNIT_VARIABLE_GROUP_NAME}>[A-Za-z_]+[A-Za-z_0-9]*)", flags=_re.IGNORECASE
)


@_dc.dataclass
class AssignStatement:  # pylint: disable=too-few-public-methods
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
    for match in _CHANGE_ASSIGN_STATEMENT_PATTERN.finditer(originalDeckContent):
        _replaceAssignStatementBasedOnUnitVariable(
            match, unprocessedDeckContent, updatedDeckContent, newStatementsByCaseFoldedName
        )

    unchangedPartBetweenLastAssignIfAnyAndEnd = unprocessedDeckContent.read()
    updatedDeckContent.write(unchangedPartBetweenLastAssignIfAnyAndEnd)

    updateDeckContentString = updatedDeckContent.getvalue()
    return updateDeckContentString


def _replaceAssignStatementBasedOnUnitVariable(
    match: _re.Match,
    unprocessedDeckContent: _io.StringIO,
    updatedDeckContent: _io.StringIO,
    newStatementsByCaseFoldedName: _tp.Mapping[str, AssignStatement],
) -> None:
    unitVariableName = match.group(_UNIT_VARIABLE_GROUP_NAME)

    caseFoldedName = unitVariableName.casefold()
    newAssignStatement = newStatementsByCaseFoldedName.get(caseFoldedName)

    currentMatchStart = match.start()
    unchangedPartBetweenLastAndCurrentAssign = unprocessedDeckContent.read(currentMatchStart)
    updatedDeckContent.write(unchangedPartBetweenLastAndCurrentAssign)

    originalAssignStatement = match.group()
    originalAssignStatementLength = len(originalAssignStatement)
    _ = unprocessedDeckContent.read(originalAssignStatementLength)

    if newAssignStatement:
        newPath = newAssignStatement.path
        updatedAssignStatement = f"ASSIGN {newPath} {newAssignStatement.unitVariableName}"
        updatedDeckContent.write(updatedAssignStatement)
    else:
        updatedDeckContent.write(originalAssignStatement)
