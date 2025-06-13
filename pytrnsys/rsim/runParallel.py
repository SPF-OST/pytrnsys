# pylint: skip-file
# type: ignore

import collections.abc as _cabc
import dataclasses as _dc
import datetime
import json
import logging
import os
import shutil
import subprocess as _sp
import sys
import time

import pandas as _pd

logger = logging.getLogger("root")
import pytrnsys.trnsys_util.LogTrnsys as _logt
import pytrnsys.rsim.command as _cmd


def getNumberOfCPU():
    """Returns the number of CPUs in the system"""
    num = 1
    if sys.platform == "win32":
        try:
            num = int(os.environ["NUMBER_OF_PROCESSORS"])
        except (ValueError, KeyError):
            pass
    elif sys.platform == "darwin":
        try:
            num = int(os.popen("sysctl -n hw.ncpu").read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf("SC_NPROCESSORS_ONLN")
        except (ValueError, OSError, AttributeError):
            pass

    return num


@_dc.dataclass
class _SimulationCase:
    caseNumber: int
    command: _cmd.Command
    process: _sp.Popen | None


@_dc.dataclass
class _Cpu:
    id: int
    assignedCase: _SimulationCase | None = None


def runParallel(
    commands: _cabc.Sequence[_cmd.Command],
    reduceCpu=0,
    outputFile=False,
    estimatedCPUTime=0.33,
    delayTime=10,
    trackingFile=None,
    masterFile=None,
) -> None:
    """Exec commands in parallel in multiple process
    (as much as we have CPU)

    The delay time is used to prevent multiple instances of trnsys trying to access the files at the same time.
    This is especially problematic with type 56, which not only reads several files.
    It also creates multiple files at the start of the simulation.
    """
    logDict = {}
    if trackingFile:
        with open(trackingFile, "w") as file:
            json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

    maxNumberOfCPU = max(min(getNumberOfCPU() - reduceCpu, len(commands)), 1)

    cpus = [_Cpu(i + 1) for i in range(maxNumberOfCPU)]

    if outputFile:
        lines = ""
        line = "============PARALLEL PROCESSING STARTED==============\n"
        lines = lines + line
        line = "Number of simulated cases =%d\n" % len(commands)
        lines = lines + line
        line = "Number of CPU used =%d\n" % maxNumberOfCPU
        lines = lines + line
        line = "Estimated time =%f hours, assuming :%f hour per simulation\n" % (
            len(commands) * estimatedCPUTime / (maxNumberOfCPU * 1.0),
            estimatedCPUTime,
        )
        lines = lines + line
        line = "============CASES TO BE SIMULATED====================\n"
        lines = lines + line

        i = 1
        for cmd in commands:
            case = cmd.deckFilePath.name
            line = "Case %d to be simulated %s\n" % (i, case)
            lines = lines + line
            i = i + 1
        line = "============ALREADY SIMULATED CASES====================\n"
        lines = lines + line

        outfileRun = open(outputFile, "w")
        outfileRun.writelines(lines)
        outfileRun.close()

    if not commands:
        return

    caseNumber = 1
    for cpu, command in zip(commands, strict=False):
        simulationCase = _SimulationCase(caseNumber, command)
        cpu.assignedCase = simulationCase
        caseNumber += 1

    assignedCommands = {c.assignedCommand for c in cpus if c.assignedCommand}
    commandsStillToBeRun = [c for c in commands if c not in assignedCommands]

    completedCommands = []

    startTime = time.time()

    while True:
        for cpu in cpus:
            simulationCase = cpu.assignedCase

            if not simulationCase:
                continue

            command = simulationCase.command
            process = simulationCase.process

            dckName = command.deckFilePath.name

            if not process:

                if trackingFile:
                    with open(trackingFile, "r") as file:
                        logDict = json.load(file)
                    logDict[dckName] = [time.strftime("%Y-%m-%d_%H:%M:%S")]
                    with open(trackingFile, "w") as file:
                        json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

                logger.info("Command: %s", command)
                simulationCase.process = _sp.Popen(
                    command.args, stdout=_sp.PIPE, stderr=_sp.PIPE, shell=True, cwd=command.cwd
                )

                time.sleep(
                    delayTime
                )  # we delay 5 seconds for each new running to avoid that they read the same source file.

            elif _isDone(process):
                if not _hasSuccessfullyCompleted(simulationCase):
                    logger.warning("PARALLEL RUN HAS FAILED")
                    sys.exit(1)

                if outputFile:
                    #                        lines = "Finished simulated case %d\n"%(k,p.stdout.read(),p.stderr.read())

                    lines = "Finished simulated case %d at %s\n" % (
                        simulationCase.caseNumber,
                        time.strftime("%H:%M:%S of day %d-%m-%y"),
                    )
                    outfileRun = open(outputFile, "a")
                    outfileRun.writelines(lines)
                    outfileRun.close()

                if trackingFile:
                    with open(trackingFile, "r") as file:
                        logDict = json.load(file)
                    logDict[dckName].append(time.strftime("%Y-%m-%d_%H:%M:%S"))

                    logTrnsys, _ = _getLogTrnsysAndDeckFileName(command)

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
                        json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

                cpu.assignedCase = None
                completedCommands.append(command)

                logger.info("Runs completed: %s/%s" % (len(completedCommands), len(commands)))

                if len(completedCommands) % len(cpus) == 0 and len(completedCommands) != len(commands):
                    currentTime = time.time()
                    timeSoFarSec = currentTime - startTime
                    totalTimePredictionSec = timeSoFarSec * len(commands) / len(completedCommands)
                    endTimePrediction = datetime.datetime.fromtimestamp(startTime + totalTimePredictionSec).strftime(
                        "%H:%M on %d.%m.%Y"
                    )
                    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    logger.info("Predicted time of completion of all %s runs: %s" % (len(commands), endTimePrediction))
                    logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

                if masterFile and (len(completedCommands) == len(commands)):
                    newDf = _pd.DataFrame.from_dict(
                        logDict,
                        orient="index",
                        columns=["started", "finished", "outcome", "hour start", "hour end"],
                    )

                    if os.path.isfile(masterFile):
                        masterPath, masterOrig = os.path.split(masterFile)
                        masterBackup = masterOrig.split(".")[0] + "_BACKUP.csv"
                        try:
                            shutil.copyfile(masterFile, os.path.join(masterPath, masterBackup))
                            logger.info("Updated " + masterBackup)
                        except OSError:
                            logger.error("Unable to generate BACKUP of " + masterFile)
                        origDf = _pd.read_csv(masterFile, sep=";", index_col=0)

                        masterDf = _pd.concat([origDf, newDf])
                        masterDf = masterDf[~masterDf.index.duplicated(keep="last")]
                    else:
                        masterDf = newDf

                    try:
                        masterDf.to_csv(masterFile, sep=";")
                        logger.info("Updated " + masterFile)
                    except OSError:
                        logger.error("Unable to write to " + masterFile)

                if commandsStillToBeRun:
                    nextCommand = commandsStillToBeRun.pop(0)
                    simulationCase = _SimulationCase(caseNumber, nextCommand)
                    cpu.assignedCase = simulationCase
                    caseNumber += 1

        runningCases = [c.assignedCase for c in cpus if c.assignedCase]
        if not runningCases and not commandsStillToBeRun:
            break
        else:
            time.sleep(1)


def _hasSuccessfullyCompleted(simulationCase: _SimulationCase) -> bool:
    command = simulationCase.command
    logTrnsys, dckFileName = _getLogTrnsysAndDeckFileName(command)

    if logTrnsys.logFatalErrors():
        logger.error("======================================")
        logger.error(dckFileName)
        logger.error("======================================")
        errorList = logTrnsys.logFatalErrors()
        for line in errorList:
            logger.error(line.replace("\n", ""))
    else:
        logger.info("Success: No fatal errors during execution of " + dckFileName)
        logger.warning("Number of warnings during simulation: %s" % logTrnsys.checkWarnings())

    return simulationCase.returncode == 0


def _getLogTrnsysAndDeckFileName(command: _cmd.Command) -> _tp.Tuple[_logt.LogTrnsys, str]:
    fullDckFilePath = command.truncatedDeckFilePath
    (logFilePath, dckFileName) = os.path.split(fullDckFilePath)
    logFileName = os.path.splitext(dckFileName)[0]
    logInstance = _logt.LogTrnsys(logFilePath, logFileName)
    return logInstance, dckFileName


def _isDone(process: _sp.Popen) -> bool:
    return process.poll() is not None
