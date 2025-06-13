import os as _os
import pathlib as _pl


def getTrnExeFilePath() -> _pl.Path:
    isRunDuringCi = _os.environ.get("CI") == "true"
    if isRunDuringCi:
        return _pl.Path(r"C:\CI-Progams\TRNSYS18_pytrnsys\Exe\TrnEXE.exe")

    return _pl.Path(r"C:\TRNSYS18\Exe\TrnEXE.exe")
