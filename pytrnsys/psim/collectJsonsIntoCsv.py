import json as _json
import pathlib as _pl
import typing as _tp

import pandas as _pd

_Value: _tp.TypeAlias = str | int | float | _pl.Path | None
_Row: _tp.TypeAlias = dict[str, _Value]

_Column = list[_Value]
_Table: _tp.TypeAlias = dict[str, _Column]


def collectJsonsIntoCsv(csvFilePath: _pl.Path, resultsDirPath: _pl.Path | None = None) -> None:
    if not resultsDirPath:
        resultsDirPath = _pl.Path()

    allData: _Table = {}
    jsonFilePaths = resultsDirPath.glob("**/*-results.json")
    for rowNumber, jsonFilePath in enumerate(jsonFilePaths, start=1):
        newRow = _getFlattenedData(resultsDirPath, jsonFilePath)
        _addData(newRow, rowNumber, allData)
    df = _pd.DataFrame(allData)
    df.to_csv(csvFilePath, index=False)


def _addData(newRow: _Row, rowNumber: int, table: _Table) -> None:
    theirColumnNames = set(table.keys())
    myColumnNames = set(newRow.keys())

    newColumnNames = myColumnNames - theirColumnNames
    missingColumnNames = theirColumnNames - myColumnNames

    emptyColumn: _Column = [None for _ in range(rowNumber - 1)]
    for newColumnName in newColumnNames:
        table[newColumnName] = emptyColumn.copy()

    for missingColumnName in missingColumnNames:
        newRow[missingColumnName] = None

    for columnName, values in table.items():
        newValue = newRow[columnName]
        values.append(newValue)


def _getFlattenedData(dirPath: _pl.Path, jsonFilePath: _pl.Path) -> _Row:
    relativeJsonFilePath = jsonFilePath.relative_to(dirPath)

    with jsonFilePath.open() as jsonFile:
        data: _tp.Mapping[str, _tp.Any] = _json.load(jsonFile)

    flattenedData: _Row = {"FileName": relativeJsonFilePath}
    for key, value in data.items():
        if _isScalar(value):
            flattenedData[key] = value
        elif isinstance(value, list):
            isAllScalars = all(_isScalar(e) for e in value)
            if len(value) == 12 and isAllScalars:
                for month, subValue in enumerate(value, start=1):
                    subKey = f"{key}_{month}"
                    flattenedData[subKey] = subValue
            else:
                print(
                    f'Ignoring file entry "{key}": in file {relativeJsonFilePath}: '
                    f"only scalar lists of length 12 are supported."
                )
        elif _isMeanWithBounds(value):
            flattenedData[f"{key}_toLower"] = value["toLowerBound"]
            flattenedData[f"{key}_mean"] = value["mean"]
            flattenedData[f"{key}_toUpper"] = value["toUpperBound"]
        else:
            print(
                f'Ignoring file entry "{key}" of unsupported type `{type(value).__name__}` '
                f"in file {relativeJsonFilePath}."
            )
            continue

    return flattenedData


def _isScalar(value) -> bool:
    return isinstance(value, (str, int, float))


def _isMeanWithBounds(value) -> bool:
    if not isinstance(value, dict):
        return False

    if set(value.keys()) != {"mean", "toLowerBound", "toUpperBound"}:
        return False

    if not all(isinstance(v, (float, int)) for v in value.values()):
        return False

    return True
