import dataclasses as _dc
import io as _io
import re as _re
import typing as _tp

_CHANGE_ASSIGN_STATEMENT_PATTERN = _re.compile(
    r"ASSIGN\s+(?P<path>\S+)\s+(?P<unitVariable>[A-Za-z_]+[A-Za-z_0-9]*)", flags=_re.IGNORECASE
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

    statementsByLowerCaseName = {s.unitVariableName.lower(): s for s in newAssignStatements}

    unprocessedDeckContent = _io.StringIO(originalDeckContent)
    updatedDeckContent = _io.StringIO()
    for match in _CHANGE_ASSIGN_STATEMENT_PATTERN.finditer(originalDeckContent):
        unitVariableName = match.group("unitVariable")

        lowerCaseVariable = unitVariableName.lower()
        assignmentStatement = statementsByLowerCaseName.get(lowerCaseVariable)
        if not assignmentStatement:
            continue

        currentMatchStart = match.start()
        unchangedPartBetweenLastAndCurrentAssign = unprocessedDeckContent.read(currentMatchStart)
        updatedDeckContent.write(unchangedPartBetweenLastAndCurrentAssign)

        originalAssignStatement = match.group()
        originalAssignStatementLength = len(originalAssignStatement)
        unprocessedDeckContent.read(originalAssignStatementLength)

        newPath = assignmentStatement.path
        updatedAssignStatement = f"ASSIGN {newPath} {unitVariableName}"
        updatedDeckContent.write(updatedAssignStatement)

    unchangedPartBetweenLastAssignIfAnyAndEnd = unprocessedDeckContent.read()
    updatedDeckContent.write(unchangedPartBetweenLastAssignIfAnyAndEnd)

    updateDeckContentString = updatedDeckContent.getvalue()
    return updateDeckContentString
