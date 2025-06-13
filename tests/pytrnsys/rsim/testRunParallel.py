import collections.abc as _cabc
import pathlib as _pl
import shutil as _su
import time as _time

import pytrnsys.rsim.command as _cmd
import pytrnsys.rsim.runParallel as _rp
import tests.helper as _th

BIG_STORE_SWARM_DIR_PATH = _pl.Path(__file__).parent / "data" / "runParallel" / "BigStoreSwarm"


class TestRunParallel:
    def testRunParallel(self) -> None:
        dckFilePaths = self._setupAndGetDckFilePaths()

        nTotalCpus = _rp.getNumberOfCPU()
        nCpusToUse = 3
        nCpusNotUsed = nTotalCpus - nCpusToUse
        assert nCpusToUse >= 1

        trnsysExeFilePath = _th.getTrnExeFilePath()
        flags = ("/N",)
        commands = [_cmd.Command(trnsysExeFilePath, p, flags) for p in dckFilePaths]
        _rp.runParallel(commands, reduceCpu=nCpusNotUsed)

    @staticmethod
    def _setupAndGetDckFilePaths() -> _cabc.Sequence[_pl.Path]:
        relativeBigStoreSwarmDirPath = _pl.Path("BigStoreSwarm")
        relativeResultsDirPath = relativeBigStoreSwarmDirPath / "02_AP3" / "03_pytrnsys_files" / "results"

        templateDirPath = BIG_STORE_SWARM_DIR_PATH / "templates"

        workingCopyDirPath = BIG_STORE_SWARM_DIR_PATH / "working-copy"
        resultsDirPath = workingCopyDirPath / relativeResultsDirPath
        projectDirPath = workingCopyDirPath / relativeBigStoreSwarmDirPath

        if workingCopyDirPath.is_dir():
            _su.rmtree(workingCopyDirPath)
            _time.sleep(1)

        _su.copytree(templateDirPath, workingCopyDirPath)

        ciProjectDirPathString = r"C:\actions-runner-simulations\_work\BigStoreSwarm\BigStoreSwarm"
        projectDirPathString = str(projectDirPath)

        dckFilePaths = [p / f"{p.name}.dck" for p in resultsDirPath.iterdir()]
        for dckFilePath in dckFilePaths:
            template = dckFilePath.read_text()
            contents = template.replace(ciProjectDirPathString, projectDirPathString)
            dckFilePath.write_text(contents)

        return dckFilePaths
