# pylint: skip-file
# type: ignore

from pytrnsys.psim import processParallelTrnsys as pParallelTrnsys
import os

if __name__ == "__main__":

    pathBase = os.getcwd()

    tool = pParallelTrnsys.ProcessParallelTrnsys()
    tool.readConfig(pathBase, "process_pv_battery.config")
    tool.process()
