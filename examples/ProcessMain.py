from pytrnsys.psim import processParallelTrnsys as pParallelTrnsys


if __name__ == '__main__':

    pathBase = os.getcwd()

    tool = pParallelTrnsys.ProcessParallelTrnsys()
    tool.readConfig(pathBase,"process.config")
    tool.process()


