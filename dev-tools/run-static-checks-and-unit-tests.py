# Run from top-level directory

import pathlib as pl
import shutil as sh
import subprocess as sp
import argparse as ap


def main():
    parser = ap.ArgumentParser()
    parser.add_argument(
        "-s", "--static-checks", help="Also perform static checks", action='store_true', dest="shallPerformStaticChecks"
    )
    parser.add_argument(
        "-l", "--lint", help="Perform linting", action='store_true', dest="shallLint"
    )
    parser.add_argument(
        "-t", "--type", help="Perform type checking", action='store_true', dest="shallTypeCheck"
    )
    parser.add_argument(
        "-u", "--unit", help="Perform unit tests", action='store_true', dest="shallRunTests"
    )
    parser.add_argument(
        "-a", "--all", help="Perform all checks", action='store_true', dest="shallRunAll"
    )
    arguments = parser.parse_args()

    testResultsDirPath = pl.Path('test-results')

    if testResultsDirPath.exists():
        sh.rmtree(testResultsDirPath)

    if arguments.shallRunAll or arguments.shallPerformStaticChecks or arguments.shallTypeCheck:
        sp.run("mypy pytrnsys tests dev-tools")

    if arguments.shallRunAll or arguments.shallPerformStaticChecks or arguments.shallLint:
        sp.run("pylint pytrnsys pytrnsys_examples tests dev-tools")

    if arguments.shallRunAll or arguments.shallRunTests or \
       not (arguments.shallPerformStaticChecks or arguments.shallTypeCheck or arguments.shallLint):
        pytestCommand = "pytest " \
                        "--cov=pytrnsys --cov-report html:test-results/coverage --cov-report term " \
                        "--html=test-results/report/report.html " \
                        "-m \"not manual\""
        sp.run(pytestCommand)


if __name__ == "__main__":
    main()
