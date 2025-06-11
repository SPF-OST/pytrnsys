# pylint: skip-file
# type: ignore

import datetime
import json
import logging
import os
import shutil
import subprocess as _sp
import sys
import time
import collections.abc as _cabc

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


def runParallel(
    commands: _cabc.Sequence[_cmd.Command], reduceCpu=0, outputFile=False, estimedCPUTime=0.33, delayTime=10, trackingFile=None, masterFile=None
) -> None:
    """Exec commands in parallel in multiple process
    (as much as we have CPU)

    The delay time is used to prevent multiple instances of trnsys trying to access the files at the same time.
    This is especially problematic with type 56, which not only reads several files.
    It also creates multiple files at the start of the simulation.
    """
    logDict = {}
    if trackingFile != None:
        with open(trackingFile, "w") as file:
            json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

    maxNumberOfCPU = max(min(getNumberOfCPU() - reduceCpu, len(commands)), 1)

    cP = {}

    for i in range(maxNumberOfCPU):
        cP["cpu" + str(i + 1)] = {"cpu": i + 1, "process": []}

    if outputFile != False:
        lines = ""
        line = "============PARALLEL PROCESSING STARTED==============\n"
        lines = lines + line
        line = "Number of simulated cases =%d\n" % len(commands)
        lines = lines + line
        line = "Number of CPU used =%d\n" % maxNumberOfCPU
        lines = lines + line
        line = "Estimated time =%f hours, assuming :%f hour per simulation\n" % (
            len(commands) * estimedCPUTime / (maxNumberOfCPU * 1.0),
            estimedCPUTime,
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

    openCmds = list(commands)

    finishedCmds = []

    caseNr = 1

    activeP = [0] * maxNumberOfCPU

    for core in cP.keys():
        cP[core]["cmd"] = openCmds.pop(0)
        cP[core]["case"] = caseNr
        caseNr += 1

    def done(p):
        return p.poll() is not None

    def success(p):
        fullDckFilePath = p.args.split(" ")[-2]
        (logFilePath, dckFileName) = os.path.split(fullDckFilePath)
        logFileName = os.path.splitext(dckFileName)[0]
        logInstance = _logt.LogTrnsys(logFilePath, logFileName)

        if logInstance.logFatalErrors():
            logger.error("======================================")
            logger.error(dckFileName)
            logger.error("======================================")
            errorList = logInstance.logFatalErrors()
            for line in errorList:
                logger.error(line.replace("\n", ""))
        else:
            logger.info("Success: No fatal errors during execution of " + dckFileName)
            logger.warning("Number of warnings during simulation: %s" % logInstance.checkWarnings())

        return p.returncode == 0

    def fail():
        logger.warning("PARALLEL RUN HAS FAILED")
        sys.exit(1)

    processes = []

    if len(processes) > maxNumberOfCPU:
        logger.warning("You are triying tu run %d processes and only have %d CPU\n" % (len(processes), maxNumberOfCPU))

    #    while True:

    #        cpu = 1

    ###############
    # alternative code:
    #        while openCmds:

    running = True
    startTime = time.time()

    while running:
        for core in cP.keys():
            p = cP[core]["process"]
            # start processes:
            cmd: _cmd.Command = cP[core].get("cmd")
            if not p and cmd:
                dckName = cmd.deckFilePath.name
                if trackingFile != None:
                    with open(trackingFile, "r") as file:
                        logDict = json.load(file)
                    logDict[dckName] = [time.strftime("%Y-%m-%d_%H:%M:%S")]
                    with open(trackingFile, "w") as file:
                        json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

                logger.info("Command: %s", cmd)
                 cP[core]["process"] = _sp.Popen(cmd.args, stdout=_sp.PIPE, stderr=_sp.PIPE, shell=True, cwd=cmd.cwd)

                activeP[cP[core]["cpu"] - 1] = 1

                time.sleep(
                    delayTime
                )  # we delay 5 seconds for each new running to avoid that they read the same source file.

            # if process is finished, assign new command:

            if p:
                if done(p):
                    if success(p):
                        if outputFile != False:
                            #                        lines = "Finished simulated case %d\n"%(k,p.stdout.read(),p.stderr.read())

                            lines = "Finished simulated case %d at %s\n" % (
                                cP[core]["case"],
                                time.strftime("%H:%M:%S of day %d-%m-%y"),
                            )
                            outfileRun = open(outputFile, "a")
                            outfileRun.writelines(lines)
                            outfileRun.close()

                        if trackingFile != None:
                            dckName = p.args.split("\\")[-1].split(" ")[0]
                            with open(trackingFile, "r") as file:
                                logDict = json.load(file)
                            logDict[dckName].append(time.strftime("%Y-%m-%d_%H:%M:%S"))

                            fullDckFilePath = p.args.split(" ")[-2]
                            (logFilePath, dckFileName) = os.path.split(fullDckFilePath)
                            logFileName = os.path.splitext(dckFileName)[0]
                            logInstance = _logt.LogTrnsys(logFilePath, logFileName)

                            if logInstance.logFatalErrors():
                                logDict[dckName].append("fatal error")
                            else:
                                logDict[dckName].append("success")

                            simulationHours = logInstance.checkSimulatedHours()
                            if len(simulationHours) == 2:
                                logDict[dckName].append(simulationHours[0])
                                logDict[dckName].append(simulationHours[1])
                            elif len(simulationHours) == 1:
                                logDict[dckName].append(simulationHours[0])
                                logDict[dckName].append(None)

                            with open(trackingFile, "w") as file:
                                json.dump(logDict, file, indent=2, separators=(",", ": "), sort_keys=True)

                        # empty process:
                        cP[core]["process"] = []
                        finishedCmds.append(cP[core]["cmd"])
                        del cP[core]["cmd"]
                        del cP[core]["case"]

                        activeP[cP[core]["cpu"] - 1] = 0

                        logger.info("Runs completed: %s/%s" % (len(finishedCmds), len(commands)))

                        if len(finishedCmds) % len(cP) == 0 and len(finishedCmds) != len(commands):
                            currentTime = time.time()
                            timeSoFarSec = currentTime - startTime
                            totalTimePredictionSec = timeSoFarSec * len(commands) / len(finishedCmds)
                            endTimePrediction = datetime.datetime.fromtimestamp(
                                startTime + totalTimePredictionSec
                            ).strftime("%H:%M on %d.%m.%Y")
                            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                            logger.info(
                                "Predicted time of completion of all %s runs: %s" % (len(commands), endTimePrediction)
                            )
                            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

                        if masterFile != None and (len(finishedCmds) == len(commands)):
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
                                except:
                                    logger.error("Unable to generate BACKUP of " + masterFile)
                                origDf = _pd.read_csv(masterFile, sep=";", index_col=0)

                                masterDf = _pd.concat([origDf, newDf])
                                masterDf = masterDf[~masterDf.index.duplicated(keep="last")]
                            else:
                                masterDf = newDf

                            try:
                                masterDf.to_csv(masterFile, sep=";")
                                logger.info("Updated " + masterFile)
                            except:
                                logger.error("Unable to write to " + masterFile)

                        # assign new command if there are open commands:

                        if openCmds:
                            cP[core]["cmd"] = openCmds.pop(0)
                            cP[core]["case"] = caseNr
                            caseNr += 1
                            activeP[cP[core]["cpu"] - 1] = 1

                    else:
                        fail()

        if all(process == 0 for process in activeP) and not openCmds:
            #        if not processes and not newCmds:
            break
        else:
            time.sleep(0.05)


def sortCommandList(cmds, keyWord):
    """
    function to put all commands that contain a keyWord string on top of a command list, so they will be evaluated first.

    Parameters
    ----------
    cmds : list of strings
        includes all commands to be evaluated

    keyWord : string
        acts as filter; commmands including this string will be evaluated first

    Returns
    -------
    cmdsNew : list of strings
        all commands to be evaluated in new order
    """

    cmdsNew = []

    for line in cmds:
        if keyWord in line:
            cmdsNew.insert(0, line)
        else:
            cmdsNew.append(line)

    return cmdsNew
