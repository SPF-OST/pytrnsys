#!/usr/bin/python3.9

# Run from top-level directory

import pathlib as pl
import shutil as sh
import subprocess as sp
import argparse as ap
import typing as tp
import time


def main():
    parser = ap.ArgumentParser()
    parser.add_argument(
        "-s",
        "--static-checks",
        help="Also perform static checks",
        action="store_true",
        dest="shallPerformStaticChecks",
    )
    parser.add_argument(
        "-l", "--lint", help="Perform linting", action="store_true", dest="shallLint"
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Perform type checking",
        action="store_true",
        dest="shallTypeCheck",
    )
    parser.add_argument(
        "-u",
        "--unit",
        help="Perform unit tests",
        action="store_true",
        dest="shallRunTests",
    )
    parser.add_argument(
        "-d",
        "--diagram",
        help="Create package and class diagrams",
        action="store_true",
        dest="shallCreateDiagrams",
    )
    parser.add_argument(
        "-a",
        "--all",
        help="Perform all checks",
        action="store_true",
        dest="shallRunAll",
    )
    arguments = parser.parse_args()

    testResultsDirectory = _deleteStaleAndCreateEmptyTestResultsDirectory()

    if (
        arguments.shallRunAll
        or arguments.shallPerformStaticChecks
        or arguments.shallTypeCheck
    ):
        cmd = "mypy pytrnsys tests dev-tools"
        sp.run(cmd.split(), check=True)

    if (
        arguments.shallRunAll
        or arguments.shallPerformStaticChecks
        or arguments.shallLint
    ):
        cmd = "pylint pytrnsys tests dev-tools"
        sp.run(cmd.split(), check=True)

    if arguments.shallRunAll or arguments.shallCreateDiagrams:
        args = [*"pyreverse -k -o pdf -p pytrnsys -d".split(), testResultsDirectory, "pytrnsys"]
        sp.run(args, check=True)

    if (
        arguments.shallRunAll
        or arguments.shallRunTests
        or not (
            arguments.shallPerformStaticChecks
            or arguments.shallTypeCheck
            or arguments.shallLint
            or arguments.shallCreateDiagrams
        )
    ):
        args = [
            "pytest",
            "--cov=pytrnsys",
            f"--cov-report=html:{testResultsDirectory / 'coverage'}",
            "--cov-report=term",
            f"--html={testResultsDirectory / 'report' / 'report.html'}",
            "-m",
            "not manual",
            "tests",
        ]
        sp.run(args, check=True)


def _deleteStaleAndCreateEmptyTestResultsDirectory() -> pl.Path:
    testResultsDirPath = pl.Path("test-results")

    if testResultsDirPath.exists():
        sh.rmtree(testResultsDirPath)

        # Sometimes we need to give Windows a bit of time so that it can realize that
        # the directory is gone and it allows us to create it again.
        while not testResultsDirPath.exists():
            try:
                testResultsDirPath.mkdir()
            except PermissionError:
                time.sleep(0.5)

    return testResultsDirPath


if __name__ == "__main__":
    main()
