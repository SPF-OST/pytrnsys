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

    dataFilePaths = [p.relative_to(dataDirPath) for p in dataDirPath.rglob("*") if p.is_file()]

    destDirSourcePathPairs = [
        _DestDirSourceFilePath(str("pytrnsys_data" / p.parent), str("data" / p)) for p in dataFilePaths
    ]

    sortedPairs = sorted(destDirSourcePathPairs, key=lambda dp: dp.destDir)

    dataFilePairs = [
        (d, [dp.sourceFilePath for dp in dps]) for d, dps in _it.groupby(sortedPairs, key=lambda dp: dp.destDir)
    ]

    return dataFilePairs


_st.setup(
    name="pytrnsys",
    version_config=True,
    packages=_st.find_packages(),
    author="Institute for Solar Technology (SPF), OST Rapperswil",
    author_email="martin.neugebauer@ost.ch",
    description="pytrnsys simulation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pytrnsys.readthedocs.io",
    include_package_data=True,
    install_requires=["numpy", "scipy", "pandas", "matplotlib", "seaborn", "bokeh", "dataclasses-jsonschema", "lark"],
    package_data={
        "pytrnsys": ["py.typed", "./plot/stylesheets/*.*", "./report/latex_doc/*.*", "ddck/_parse/ddck.lark"],
    },
    data_files=_getDataFilePairs(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    setup_requires=["setuptools-git-versioning"],
    python_requires=">=3.9",
)
