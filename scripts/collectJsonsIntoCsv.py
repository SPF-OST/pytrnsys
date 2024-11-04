import json
import pathlib as pl
import sys
import typing as tp

import pandas as pd


def main():
    if len(sys.argv) != 3:
        scriptName = pl.Path(sys.argv[0]).name
        print(f"Usage: {scriptName} <path-to-directory-containing-json-files> <path-to-csv-file>")
        sys.exit(-1)

    dirPath = pl.Path(sys.argv[1])
    csvFilePath = pl.Path(sys.argv[2])

    allData = {}

    jsonFilePaths = dirPath.glob("**/*-results.json")
    for rowNumber, jsonFilePath in enumerate(jsonFilePaths, start=1):
        data = _getFlattenedData(dirPath, jsonFilePath)
        _addData(data, rowNumber, allData)

    df = pd.DataFrame(allData)
    df.to_csv(csvFilePath, index=False)


def _addData(newRow, rowNumber, allRows):
    theirColumnNames = set(allRows.keys())
    myColumnNames = set(newRow.keys())

    newColumnNames = myColumnNames - theirColumnNames
    missingColumnNames = theirColumnNames - myColumnNames

    emptyColumn = [None for _ in range(rowNumber - 1)]
    for newColumnName in newColumnNames:
        allRows[newColumnName] = emptyColumn.copy()

    for missingColumnName in missingColumnNames:
        newRow[missingColumnName] = None

    for columnName, values in allRows.items():
        newValue = newRow[columnName]
        values.append(newValue)


def _getFlattenedData(dirPath, jsonFilePath):
    relativeJsonFilePath = jsonFilePath.relative_to(dirPath)

    with jsonFilePath.open() as jsonFile:
        data: tp.Mapping[str, tp.Any] = json.load(jsonFile)

    flattenedData = {"FileName": relativeJsonFilePath}
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


if __name__ == "__main__":
    main()
