.. _processSimulations:

-------------------
Processing Simulations
-------------------

The idea of the config files is to include general functionality without having to type python code for the user.
Thus, this config file will grow as long as users believe some functionality is used so often that its worth to implemente it within the config file. All the functionality not included in the config file will need to be implemented as python code and thus will be a bit limited to those knowing how to program in python. 

1. Create a config-file
-----------------------

2. Python code
----------------------

The processing specified in the :ref:`config-file <configFile>` can be started with the following python code::

 
	from pytrnsys.psim import processParallelTrnsys as pParallelTrnsys

	if __name__ == '__main__':
		pathBase = os.getcwd()

		tool = pParallelTrnsys.ProcessParallelTrnsys()
		tool.readConfig(pathBase,"process.config")
		tool.process()

