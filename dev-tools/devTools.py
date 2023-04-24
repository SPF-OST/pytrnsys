#!/usr/bin/python3.9

# Run from top-level directory

import argparse as ap
import os
import pathlib as pl
import shutil as sh
import subprocess as sp
import typing as tp
import sysconfig as _sysconfig
import venv

import sys
import time

_SCRIPTS_DIR = pl.Path(_sysconfig.get_path("scripts"))


def main():
    arguments = _parseArguments()

    testResultsDirPath = pl.Path("test-results")
    _prepareTestResultsDirectory(testResultsDirPath, arguments.shallKeepResults)

    _maybeRunMypy(arguments)

    _maybeRunPylint(arguments)

    _maybeRunBlack(arguments)

    _maybeCreateDiagrams(arguments)

    _maybeCreateExecutable(arguments)

    _maybeRunPytest(arguments, testResultsDirPath)


def _parseArguments() -> ap.Namespace:
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
        "-b",
        "--black",
        help="Check formatting",
        type=str,
        default=None,
        const="--check",
        nargs="?",
        dest="blackArguments",
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
    parser.add_argument(
        "-x",
        "--executable",
        help="Create executable using pyinstaller",
        action="store_true",
        dest="shallCreateExecutable",
    )
    arguments = parser.parse_args()
    return arguments


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


def _maybeRunMypy(arguments):
    if arguments.shallRunAll or arguments.shallPerformStaticChecks or arguments.mypyArguments is not None:
        cmd = f"{_SCRIPTS_DIR / 'mypy'} --show-error-codes pytrnsys tests dev-tools"
        additionalArgs = arguments.mypyArguments or ""
        _printAndRun([*cmd.split(), *additionalArgs.split()])


def _maybeRunPylint(arguments):
    if arguments.shallRunAll or arguments.shallPerformStaticChecks or arguments.lintArguments is not None:
        cmd = f"{_SCRIPTS_DIR / 'pylint'} pytrnsys tests dev-tools"
        additionalArgs = arguments.lintArguments or ""

        _printAndRun([*cmd.split(), *additionalArgs.split()])


def _maybeRunBlack(arguments):
    if arguments.shallRunAll or arguments.shallPerformStaticChecks or arguments.blackArguments is not None:
        cmd = f"{_SCRIPTS_DIR / 'black'} -l 120 pytrnsys tests dev-tools"
        additionalArgs = "--check" if arguments.blackArguments is None else arguments.blackArguments

        _printAndRun([*cmd.split(), *additionalArgs.split()])


def _maybeCreateDiagrams(arguments):
    if arguments.shallRunAll or arguments.diagramsFormat:
        diagramsFormat = arguments.diagramsFormat if arguments.diagramsFormat else "pdf"
        cmd = f"{_SCRIPTS_DIR / 'pyreverse'} -k -o {diagramsFormat} -p pytrnsys -d test-results pytrnsys"
        _printAndRun(cmd.split())


def _maybeCreateExecutable(arguments):
    if arguments.shallRunAll or arguments.shallCreateExecutable:
        releaseDirPath = pl.Path("release").resolve(strict=True)

        sh.rmtree(releaseDirPath / "build", ignore_errors=True)
        sh.rmtree(releaseDirPath / "dist", ignore_errors=True)
        sh.rmtree(releaseDirPath / "pyinstaller-venv", ignore_errors=True)

        venvDirPath = releaseDirPath / "pyinstaller-venv"
        venv.create(venvDirPath, with_pip=True)

        commands = [
            r"release\pyinstaller-venv\Scripts\python.exe -m pip install --upgrade pip",
            r"release\pyinstaller-venv\Scripts\python.exe -m pip install wheel",
            r"release\pyinstaller-venv\Scripts\python.exe -m pip install -r requirements\release.txt",
            r"release\pyinstaller-venv\Scripts\python.exe -m pip uninstall --yes -r requirements\pyinstaller.remove",
            r"release\pyinstaller-venv\Scripts\python.exe dev-tools\generateGuiClassesFromQtCreatorStudioUiFiles.py",
        ]

        for cmd in commands:
            _printAndRun(cmd.split())

        os.chdir("release")

        cmd = r".\pyinstaller-venv\Scripts\pyinstaller.exe pytrnsys-gui.spec"
        _printAndRun(cmd.split())

        os.chdir("..")


def _maybeRunPytest(arguments, testResultsDirPath):
    wasCalledWithoutArguments = (
        not arguments.shallPerformStaticChecks
        and arguments.mypyArguments is None
        and arguments.lintArguments is None
        and arguments.blackArguments is None
        and arguments.diagramsFormat is None
        and not arguments.shallCreateExecutable
    )
    if arguments.shallRunAll or arguments.pytestMarkersExpression is not None or wasCalledWithoutArguments:
        markerExpressions = _getMarkerExpressions(arguments.pytestMarkersExpression)
        additionalArgs = ["-m", markerExpressions]

        cmd = [
            _SCRIPTS_DIR / "pytest",
            "-v",
            "--cov=trnsysGUI",
            f"--cov-report=html:{testResultsDirPath / 'coverage-html'}",
            f"--cov-report=lcov:{testResultsDirPath / 'coverage.lcov'}",
            "--cov-report=term",
            f"--html={testResultsDirPath / 'report' / 'report.html'}",
        ]

        args = [*cmd, *additionalArgs, "tests"]

        _printAndRun(args)


def _getMarkerExpressions(userSuppliedMarkerExpressions: str) -> str:
    hardCodedMarkerExpressions = "not tool"
    markerExpressions = (
        f"({hardCodedMarkerExpressions}) and ({userSuppliedMarkerExpressions})"
        if userSuppliedMarkerExpressions
        else hardCodedMarkerExpressions
    )
    return markerExpressions


def _printAndRun(args: tp.Sequence[str]) -> None:
    formattedArgs = " ".join(str(arg) for arg in args)
    print(f"Running '{formattedArgs}'...")
    sp.run(args, check=True)
    print("...DONE.")


if __name__ == "__main__":
    main()
