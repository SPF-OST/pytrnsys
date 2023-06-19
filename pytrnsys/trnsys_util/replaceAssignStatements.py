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

    statementsByLowerCaseFoldedName = {s.unitVariableName.casefold(): s for s in newAssignStatements}

    unprocessedDeckContent = _io.StringIO(originalDeckContent)
    updatedDeckContent = _io.StringIO()
    for match in _CHANGE_ASSIGN_STATEMENT_PATTERN.finditer(originalDeckContent):
        unitVariableName = match.group("unitVariable")

        caseFoldedVariable = unitVariableName.casefold()
        assignmentStatement = statementsByLowerCaseFoldedName.get(caseFoldedVariable)
        if not assignmentStatement:
            continue

        _replaceAssignStatementBasedOnUnitVariable(
            match, assignmentStatement, unprocessedDeckContent, updatedDeckContent
        )

    unchangedPartBetweenLastAssignIfAnyAndEnd = unprocessedDeckContent.read()
    updatedDeckContent.write(unchangedPartBetweenLastAssignIfAnyAndEnd)

    updateDeckContentString = updatedDeckContent.getvalue()
    return updateDeckContentString


def _replaceAssignStatementBasedOnUnitVariable(
    match: _re.Match,
    assignmentStatement: AssignStatement,
    unprocessedDeckContent: _io.StringIO,
    updatedDeckContent: _io.StringIO,
) -> None:
    unitVariableName = match.group(_UNIT_VARIABLE_GROUP_NAME)

    currentMatchStart = match.start()
    unchangedPartBetweenLastAndCurrentAssign = unprocessedDeckContent.read(currentMatchStart)
    updatedDeckContent.write(unchangedPartBetweenLastAndCurrentAssign)

    originalAssignStatement = match.group()
    originalAssignStatementLength = len(originalAssignStatement)
    _ = unprocessedDeckContent.read(originalAssignStatementLength)

    newPath = assignmentStatement.path
    updatedAssignStatement = f"ASSIGN {newPath} {unitVariableName}"
    updatedDeckContent.write(updatedAssignStatement)
