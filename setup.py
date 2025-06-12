# pylint: skip-file
# type: ignore

import dataclasses as _dc
import pathlib as _pl
import itertools as _it

import setuptools as _st


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
    version_config=True,
    packages=_st.find_packages(),
    url="https://pytrnsys.readthedocs.io",
    data_files=_getDataFilePairs(),
)
