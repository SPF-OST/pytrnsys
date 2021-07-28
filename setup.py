# pylint: skip-file
# type: ignore

import dataclasses as _dc
import pathlib as _pl
import itertools as _it

import setuptools as _st

with open("README.md", "r") as fh:
    long_description = fh.read()


@_dc.dataclass
class _DestDirSourceFilePath:
    destDir: str
    sourceFilePath: str


def _getDataFilePairs():
    dataDirPath = _pl.Path(__file__).parent / "data"

    dataFilePaths = [
        p.relative_to(dataDirPath) for p in dataDirPath.rglob("*") if p.is_file()
    ]

    destDirSourcePathPairs = [
        _DestDirSourceFilePath(str("pytrnsys_data" / p.parent), str("data" / p)) for p in dataFilePaths
    ]

    sortedPairs = sorted(destDirSourcePathPairs, key=lambda dp: dp.destDir)

    dataFilePairs = [
        (d, [dp.sourceFilePath for dp in dps])
        for d, dps in _it.groupby(sortedPairs, key=lambda dp: dp.destDir)
    ]

    return dataFilePairs


_st.setup(
    name="pytrnsys",
    version_config=True,
    packages=_st.find_packages(),
    author="Dani Carbonell, Mattia Battaglia, Jeremias Schmidli, Martin Neugebauer",
    author_email="martin.neugebauer@spf.ch",
    description="pytrnsys simulation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pytrnsys.readthedocs.io",
    include_package_data=True,
    install_requires=["numpy", "scipy", "pandas", "matplotlib", "seaborn", "bokeh", "dataclasses-jsonschema"],
    package_data={
        "pytrnsys": ["./plot/stylesheets/*.*", "./report/latex_doc/*.*"],
    },
    data_files=_getDataFilePairs(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points="""
    [console_scripts]
    pytrnsys-dll = pytrnsys.utils.copyDllFiles:dllCopy
    pytrnsys-run = pytrnsys.rsim.runParallelTrnsys:run
    pytrnsys-process = pytrnsys.psim.processParallelTrnsys:process
    pytrnsys-load = pytrnsys.utils.loadExamplesAndDdcks:load
    """,
    setup_requires=["setuptools-git-versioning"],
    python_requires=">=3.9",
)
