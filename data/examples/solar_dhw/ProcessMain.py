# pylint: skip-file
# type: ignore

from pytrnsys.psim import processParallelTrnsys as pParallelTrnsys
import os

if __name__ == "__main__":

    pathBase = os.getcwd()  # r"C:\Daten\OngoingProject\pytrnsysTest2\testScaling\SolarDHW_newProfile"

    tool = pParallelTrnsys.ProcessParallelTrnsys()
    tool.readConfig(pathBase, "process_solar_dhw.config")
    tool.process()
