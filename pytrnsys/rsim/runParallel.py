# pylint: disable=unspecified-encoding

import collections.abc as _cabc
import dataclasses as _dc
import datetime as _dt
import json as _json
import logging as _log
import os as _os
import shutil as _su
import subprocess as _sp
import sys as _sys
import time as _time
import typing as _tp

import pandas as _pd

import pytrnsys.rsim.command as _cmd
import pytrnsys.trnsys_util.LogTrnsys as _logt

logger = _log.getLogger("root")


def getNumberOfCPU():
    """Returns the number of CPUs in the system"""
    num = 1
    if _sys.platform == "win32":
        try:
            num = int(_os.environ["NUMBER_OF_PROCESSORS"])
        except (ValueError, KeyError):
            pass
    elif _sys.platform == "darwin":
        try:
            num = int(_os.popen("sysctl -n hw.ncpu").read())
        except ValueError:
            pass
    else:
        try:
            num = _os.sysconf("SC_NPROCESSORS_ONLN")
        except (ValueError, OSError, AttributeError):
            pass

    return num


@_dc.dataclass
class _SimulationCase:
    caseNumber: int
    command: _cmd.Command
    process: _sp.Popen | None = None


@_dc.dataclass
class _Cpu:
    id: int
    assignedCase: _SimulationCase | None = None


def runParallel(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    commands: _cabc.Sequence[_cmd.Command],
    reduceCpu=0,
    outputFile=False,
    estimatedCPUTime=0.33,
    trackingFile=None,
    masterFile=None,
) -> None:
    """Exec commands in parallel in multiple process
    (as much as we have CPU)
    """
    logDict = dict[str, list[_tp.Any]]()
    if trackingFile:
        with open(trackingFile, "w") as file:
            _json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

    maxNumberOfCPU = max(min(getNumberOfCPU() - reduceCpu, len(commands)), 1)

    cpus = [_Cpu(i + 1) for i in range(maxNumberOfCPU)]

    if outputFile:
        lines = ""
        line = "============PARALLEL PROCESSING STARTED==============\n"
        lines = lines + line
        line = f"Number of simulated cases ={len(commands):d}\n"
        lines = lines + line
        line = f"Number of CPU used ={maxNumberOfCPU:d}\n"
        lines = lines + line
        line = (
            f"Estimated time = {len(commands) * estimatedCPUTime / (maxNumberOfCPU * 1.0):f} hours, "
            f"assuming :{estimatedCPUTime:f} hour per simulation\n"
        )
        lines = lines + line
        line = "============CASES TO BE SIMULATED====================\n"
        lines = lines + line

        i = 1
        for cmd in commands:
            case = cmd.deckFilePath.name
            line = f"Case {i:d} to be simulated {case}\n"
            lines = lines + line
            i = i + 1
        line = "============ALREADY SIMULATED CASES====================\n"
        lines = lines + line

        with open(outputFile, "w") as outfileRun:
            outfileRun.writelines(lines)

    if not commands:
        return

    caseNumber = 1
    for cpu, command in zip(cpus, commands, strict=False):
        simulationCase = _SimulationCase(caseNumber, command)
        cpu.assignedCase = simulationCase
        caseNumber += 1

    assignedCommands = [c.assignedCase.command for c in cpus if c.assignedCase]
    commandsStillToBeRun = [c for c in commands if c not in assignedCommands]

    completedCommands = []

    startTime = _time.time()

    while True:  # pylint: disable=too-many-nested-blocks
        for cpu in cpus:
            assignedCase = cpu.assignedCase

            if not assignedCase:
                continue

            command = assignedCase.command
            process = assignedCase.process

            dckName = command.deckFilePath.name

            if not process:

                if trackingFile:
                    with open(trackingFile, "r") as file:
                        logDict = _json.load(file)
                    logDict[dckName] = [_time.strftime("%Y-%m-%d_%H:%M:%S")]
                    with open(trackingFile, "w") as file:
                        _json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

                logger.info("Command: %s", command)
                assignedCase.process = _sp.Popen(  # pylint: disable=consider-using-with
                    command.args, stdout=_sp.PIPE, stderr=_sp.PIPE, cwd=command.cwd
                )

            elif _isDone(process):
                _renameTruncatedLogFilePath(command)

                if not _hasSuccessfullyCompleted(assignedCase):
                    logger.warning("PARALLEL RUN HAS FAILED")
                    _sys.exit(1)

                if outputFile:
                    lines = (
                        f"Finished simulated case {assignedCase.caseNumber:d} "
                        f"at {_time.strftime('%H:%M:%S of day %d-%m-%y')}\n"
                    )
                    with open(outputFile, "a") as outfileRun:
                        outfileRun.writelines(lines)

                if trackingFile:
                    with open(trackingFile, "r") as file:
                        logDict = _json.load(file)
                    logDict[dckName].append(_time.strftime("%Y-%m-%d_%H:%M:%S"))

                    logTrnsys = _createLogTrnsys(command)

                    if logTrnsys.logFatalErrors():
                        logDict[dckName].append("fatal error")
                    else:
                        logDict[dckName].append("success")

                    simulationHours = logTrnsys.checkSimulatedHours()
                    if len(simulationHours) == 2:
                        logDict[dckName].append(simulationHours[0])
                        logDict[dckName].append(simulationHours[1])
                    elif len(simulationHours) == 1:
                        logDict[dckName].append(simulationHours[0])
                        logDict[dckName].append(None)

                    with open(trackingFile, "w") as file:
                        _json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

                cpu.assignedCase = None
                completedCommands.append(command)

                logger.info("Runs completed: %s/%s", len(completedCommands), len(commands))

                if len(completedCommands) % len(cpus) == 0 and len(completedCommands) != len(commands):
                    currentTime = _time.time()
                    timeSoFarSec = currentTime - startTime
                    totalTimePredictionSec = timeSoFarSec * len(commands) / len(completedCommands)
                    endTimePrediction = _dt.datetime.fromtimestamp(startTime + totalTimePredictionSec).strftime(
                        "%H:%M on %d.%m.%Y"
                    )
                    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    logger.info("Predicted time of completion of all %s runs: %s", len(commands), endTimePrediction)
                    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

                if masterFile and (len(completedCommands) == len(commands)):
                    newDf = _pd.DataFrame.from_dict(
                        logDict,
                        orient="index",
                        columns=["started", "finished", "outcome", "hour start", "hour end"],
                    )

                    if _os.path.isfile(masterFile):
                        masterPath, masterOrig = _os.path.split(masterFile)
                        masterBackup = masterOrig.split(".")[0] + "_BACKUP.csv"
                        try:
                            _su.copyfile(masterFile, _os.path.join(masterPath, masterBackup))
                            logger.info("Updated %s", masterBackup)
                        except OSError:
                            logger.error("Unable to generate BACKUP of %s", masterFile)
                        origDf = _pd.read_csv(masterFile, sep=";", index_col=0)

                        masterDf = _pd.concat([origDf, newDf])
                        masterDf = masterDf[~masterDf.index.duplicated(keep="last")]
                    else:
                        masterDf = newDf

                    try:
                        masterDf.to_csv(masterFile, sep=";")
                        logger.info("Updated %s", masterFile)
                    except OSError:
                        logger.error("Unable to write to %s", masterFile)

                if commandsStillToBeRun:
                    nextCommand = commandsStillToBeRun.pop(0)
                    simulationCase = _SimulationCase(caseNumber, nextCommand)
                    cpu.assignedCase = simulationCase
                    caseNumber += 1

        runningCases = [c.assignedCase for c in cpus if c.assignedCase]
        if not runningCases and not commandsStillToBeRun:
            break

        _time.sleep(1)


def _renameTruncatedLogFilePath(command):
    truncatedLogFilePath = command.truncatedLogFilePath
    fullLogFilePath = command.logFilePath
    if not fullLogFilePath.exists():
        assert truncatedLogFilePath.exists()
        _su.move(truncatedLogFilePath, fullLogFilePath)


def _createLogTrnsys(command: _cmd.Command) -> _logt.LogTrnsys:  # type: ignore[name-defined]
    containingDirPathAsString = str(command.logFilePath.parent)
    logTrnsys = _logt.LogTrnsys(containingDirPathAsString, command.logFilePath.stem)  # type: ignore[attr-defined]
    return logTrnsys


def _hasSuccessfullyCompleted(simulationCase: _SimulationCase) -> bool:
    command = simulationCase.command
    dckFileName = command.deckFilePath.name

    logTrnsys = _createLogTrnsys(command)
    if logTrnsys.logFatalErrors():
        logger.error("======================================")
        logger.error(dckFileName)
        logger.error("======================================")
        errorList = logTrnsys.logFatalErrors()
        for line in errorList:
            logger.error(line.replace("\n", ""))
    else:
        logger.info("Success: No fatal errors during execution of %s", dckFileName)
        logger.warning("Number of warnings during simulation: %s", logTrnsys.checkWarnings())

    process = simulationCase.process
    assert process

    return process.returncode == 0


def _isDone(process: _sp.Popen) -> bool:
    return process.poll() is not None
