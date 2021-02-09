import pathlib as pl
import shutil
import filecmp
import typing as tp

import pytrnsys.utils.costConfig as cc


def testCostConfig():
    actualResultsDir, expectedResultsDir, costParametersFilePath = setupDirsAndGetPaths()

    costConfig = cc.costConfig()

    costParameters = costConfig.readCostJson(str(costParametersFilePath))

    costConfig.setFontsizes(small=15)
    costConfig.setDefaultData(costParameters)
    costConfig.readResults(str(actualResultsDir))

    costConfig.process(costParameters)

    assertDirectoriesRecursivelyEqual(actualResultsDir, expectedResultsDir)


def setupDirsAndGetPaths():
    data_dir = pl.Path(__file__).parent / 'cost_calculation'

    inputDir = data_dir / 'input'
    resultsDir = inputDir / 'results'
    costParametersFilePath = inputDir / "costSolarIce_HpSplit.json"

    outputDir = data_dir / 'output'
    actualDir = outputDir / 'actual'
    actualResultsDir = actualDir / 'results'
    expectedDir = outputDir / 'expected'
    expectedResultsDir = expectedDir / 'results'

    if actualDir.exists():
        shutil.rmtree(actualDir)

    shutil.copytree(resultsDir, actualResultsDir)

    return actualResultsDir, expectedResultsDir, costParametersFilePath


def assertDirectoriesRecursivelyEqual(actualResultsDir: pl.Path, expectedResultsDir: pl.Path) -> None:
    expectedFiles = enumerateFilesRecursively(expectedResultsDir)

    _, mismatch, errors = filecmp.cmpfiles(actualResultsDir, expectedResultsDir, expectedFiles, shallow=False)

    assert not mismatch
    assert not errors


def enumerateFilesRecursively(directory: pl.Path) -> tp.Iterable[str]:
    assert directory.is_dir()

    for child in directory.iterdir():
        if child.is_file():
            yield str(child)
        elif child.is_dir():
            yield from enumerateFilesRecursively(child)
