import collections.abc as _cabc
import pathlib as _pl
import shutil as _su
import time as _time

import pytrnsys.rsim.command as _cmd
import pytrnsys.rsim.runParallel as _rp
import tests.helper as _th

ICEGRID_DIR_PATH = _pl.Path(__file__).parent / "data" / "runParallel" / "icegrid"

WORKING_DIR_PATH = ICEGRID_DIR_PATH / "working-copy"


class TestRunParallel:
    def testRunParallel(self) -> None:
        dckFilePaths = self._setupAndGetDckFilePaths()

        nTotalCpus = _rp.getNumberOfCPU()
        nCpusToUse = 3
        nCpusNotUsed = nTotalCpus - nCpusToUse
        assert nCpusToUse >= 1

        trnsysExeFilePath = _th.getTrnExeFilePath()
        flags = ["/N"]
        commands = [_cmd.Command(trnsysExeFilePath, p, flags) for p in dckFilePaths]

        outputFilePath = WORKING_DIR_PATH / "output.log"
        trackingFilePath = WORKING_DIR_PATH / "tracking.json"
        masterFilePath = WORKING_DIR_PATH / "master.csv"

        _rp.runParallel(
            commands,
            reduceCpu=nCpusNotUsed,
            outputFile=str(outputFilePath),
            trackingFile=str(trackingFilePath),
            masterFile=str(masterFilePath),
        )

    @staticmethod
    def _setupAndGetDckFilePaths() -> _cabc.Sequence[_pl.Path]:
        relativeIcegridDirPath = _pl.Path("icegrid")
        relativeResultsDirPath = relativeIcegridDirPath / "results"

        templateDirPath = ICEGRID_DIR_PATH / "templates"

        resultsDirPath = WORKING_DIR_PATH / relativeResultsDirPath
        projectDirPath = WORKING_DIR_PATH / relativeIcegridDirPath

        if WORKING_DIR_PATH.is_dir():
            _su.rmtree(WORKING_DIR_PATH)
            _time.sleep(1)

        _su.copytree(templateDirPath, WORKING_DIR_PATH)

        ciProjectDirPathString = r"C:\actions-runner-simulations\_work\icegrid\icegrid"
        projectDirPathString = str(projectDirPath)

        dckFilePaths = [p / f"{p.name}.dck" for p in resultsDirPath.iterdir()]
        for dckFilePath in dckFilePaths:
            template = dckFilePath.read_text()
            contents = template.replace(ciProjectDirPathString, projectDirPathString)
            dckFilePath.write_text(contents)

        return dckFilePaths
