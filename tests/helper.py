# pylint: disable=invalid-name

import os as _os
import pathlib as _pl

def is_run_during_ci() -> bool:
    return _os.environ.get("CI") == "true"

def getTrnExeFilePath() -> _pl.Path:
    if is_run_during_ci():
        return _pl.Path("C:/CI-Progams/TRNSYS18_pytrnsys/Exe/TrnEXE.exe")

    return _pl.Path("C:/TRNSYS18/Exe/TrnEXE.exe")
