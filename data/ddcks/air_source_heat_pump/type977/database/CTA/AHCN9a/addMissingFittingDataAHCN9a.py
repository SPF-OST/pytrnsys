import os
import pandas as pd

dataFolder = "C:\GIT\plural\heatPumpFit\AHCN9a"
dataFile = "tableCTA.csv"
fullPath = os.path.join(dataFolder, dataFile)

origDf = pd.read_csv(fullPath, sep = ";")

heatCapEvap_kJ_kgK = 0.7
heatCapCond_kJ_kgK = 4.182
deltaTEvap_K = 7.0
deltaTCond_K = 5.0

outputText = "TInEvap\tTInCond\tCOP\tQCond\tMFlowCond\tMFlowEvap\n"
for index, row in origDf.iterrows():
    COP = row["COP"]
    MFlowCond_kg_h = row["QCond"] / (heatCapCond_kJ_kgK * deltaTCond_K) * 3600
    QEvap = (1. - 1. / COP) * row["QCond"]
    MFlowEvap_kg_h = QEvap / (heatCapEvap_kJ_kgK * deltaTEvap_K) * 3600
    TInCond = row["TOutCond"] - deltaTCond_K
    line = "{TInEvap}\t{TInCond}\t{COP}\t{QCond}\t{MFlowCond}\t{MFlowEvap}\n".format(TInEvap=row["Tamb"],
                                                                                     TInCond=TInCond,
                                                                                     COP = COP,
                                                                                     QCond=row["QCond"],
                                                                                     MFlowCond = MFlowCond_kg_h,
                                                                                     MFlowEvap = MFlowEvap_kg_h)
    outputText += line
outputFileName = "AHCN9a.exp"
fullOutputPath = os.path.join(dataFolder, outputFileName)
with open(fullOutputPath, 'w') as f:
    f.write(outputText)