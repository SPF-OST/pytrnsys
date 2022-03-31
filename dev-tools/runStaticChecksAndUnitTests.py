#!/usr/bin/python3.9

# Run from top-level directory

import argparse as ap
import pathlib as pl
import shutil as sh
import subprocess as sp
import sys
import time


def main():
    parser = ap.ArgumentParser()

    parser.add_argument(
        "-k",
        "--keep-results",
        help="Don't clean test results",
        action="store_true",
        dest="shallKeepResults",
    )
    parser.add_argument(
        "-s",
        "--static-checks",
        help="Perform linting and type checking",
        action="store_true",
        dest="shallPerformStaticChecks",
    )
    parser.add_argument(
        "-l", "--lint", help="Perform linting", type=str, default=None, const="", nargs="?", dest="lintArguments"
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Perform type checking",
        type=str,
        default=None,
        const="",
        nargs="?",
        dest="mypyArguments",
    )
    parser.add_argument(
        "-u",
        "--unit",
        help="Perform unit tests",
        type=str,
        default=None,
        const="",
        nargs="?",
        dest="pytestMarkersExpression",
    )
    parser.add_argument(
        "-d",
        "--diagram",
        help="Create package and class diagrams",
        nargs="?",
        default=None,
        const="pdf",
        choices=["pdf", "dot"],
        dest="diagramsFormat",
    )
    parser.add_argument(
        "-a",
        "--all",
        help="Perform all checks",
        action="store_true",
        dest="shallRunAll",
    )
    arguments = parser.parse_args()

    testResultsDirPath = pl.Path("test-results")

    _prepareTestResultsDirectory(testResultsDirPath, arguments.shallKeepResults)

    if arguments.shallRunAll or arguments.shallPerformStaticChecks or arguments.mypyArguments is not None:
        cmd = "mypy --show-error-codes pytrnsys tests dev-tools"
        additionalArgs = arguments.mypyArguments or ""
        sp.run([*cmd.split(), *additionalArgs.split()], check=True)

    if arguments.shallRunAll or arguments.shallPerformStaticChecks or arguments.lintArguments is not None:
        cmd = "pylint pytrnsys tests dev-tools"
        additionalArgs = arguments.lintArguments or ""

        sp.run([*cmd.split(), *additionalArgs.split()], check=True)

    if arguments.shallRunAll or arguments.diagramsFormat:
        diagramsFormat = arguments.diagramsFormat if arguments.diagramsFormat else "pdf"
        cmd = f"pyreverse -k -o {diagramsFormat} -p pytrnsys_gui -d test-results pytrnsys"
        sp.run(cmd.split(), check=True)

    if (
        arguments.shallRunAll
        or arguments.pytestMarkersExpression is not None
        or not (
            arguments.shallPerformStaticChecks
            or arguments.mypyArguments is not None
            or arguments.lintArguments is not None
            or arguments.diagramsFormat
        )
    ):
        markersExpression = arguments.pytestMarkersExpression or "not ci and not linux"
        additionalArgs = ["-m", markersExpression]

        cmd = [
            "pytest",
            "--cov=pytrnsys",
            f"--cov-report=html:{testResultsDirPath / 'coverage'}",
            "--cov-report=term",
            f"--html={testResultsDirPath / 'report' / 'report.html'}",
        ]

        args = [*cmd, *additionalArgs, "tests"]

        sp.run(args, check=True)


def _prepareTestResultsDirectory(testResultsDirPath: pl.Path, shallKeepResults: bool) -> None:
    if testResultsDirPath.exists() and not testResultsDirPath.is_dir():
        print("ERROR: `test-results` exists but is not a directory", file=sys.stderr)
        sys.exit(2)

    if not shallKeepResults and testResultsDirPath.is_dir():
        sh.rmtree(testResultsDirPath)

    # Sometimes we need to give Windows a bit of time so that it can realize that
    # the directory is gone and it allows us to create it again.
    time.sleep(1)

    if not testResultsDirPath.is_dir():
        testResultsDirPath.mkdir()


if __name__ == "__main__":
    main()
