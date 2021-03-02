"""This script compiles the requirements.txt files corresponding to all known requirements.in files.

If you want to add a dependency to pytrnsys add it to the relevant requirement.in file(s). Then invoke
this script from within your virtual environment from the top-level pytrnsys directory like so:

    python dev-tools\compile-requirements-txts.py -P <your-package>

E.g., to add the package `pdfdiff` which is only needed for testing you'd add it to the
requirements\test\requirements.in file and then run

        python dev-tools\compile-requirements-txts.py -P pdfdiff

Finally, sanity-check the newly generated requirements.txt file(s) by diff'ing them against the checked-in version
and if they make sense, check in *both* the requirements.txt and the requirements.in file(s).

To try and upgrade a given package also do

    python dev-tools\compile-requirements-txts.py -P <your-package>

To be able to run this script for the first time you need to have installed the development requirements by doing

    pip install -r requirements\dev\requirements.txt
"""

import subprocess as sp
import sys
import pathlib as pl

baseArgs = ['pip-compile', *sys.argv[1:]]

DIRS = [
    "requirements/dev",
    "requirements/test"
]


def getDirPaths():
    return [pl.Path(d) for d in DIRS]


for d in getDirPaths():
    inFile = str(d / 'requirements.in')
    args = [*baseArgs, inFile]
    print(f"Calling \"{' '.join(args)}\":")
    sp.run(args)
