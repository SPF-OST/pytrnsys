.. _developers_guide:

Developer's guide
=================

Get the source code from github
-------------------------------

Pytrnsys is available as open source code under the MIT license. If you want to run
pytrnsys from source, it is recommended to use a designated virtual environment. Make sure that in your python environment
the following dependencies are installed:

- numpy
- scipy
- pandas
- matplotlib
- seaborn
- bokeh

If you would like to contribute to pytrnsys and the documentation, you also need the following python packages:

- sphinx
- recommonmark
- sphinx_rtd_theme

You can fork the source code at (toBeFilledInWhenPublic) or by the following command::

    git clone (toBeFilledInWhenPublic)

Once you have you local copy of the pytrnsys source code you can add the pytrnsys package subfolder
to your Python project source paths.
Once you have the pytrnsys package installed from source and you should be able to execute::

    import pytrnsys

in your Python environment.

Run the example systems from source
-----------------------------------
You can run pytrnsys with the following minimal code example

.. code-block:: python

    import pytrnsys.rsim.runParallelTrnsys as runTrnsys

    pathConfig  = "pathToTheConfigFile"
    configFile = "run_solar_dhw.config"
    runTool = runTrnsys.RunParallelTrnsys(pathConfig,configFile=configFile)

The "pathToTHeConfigFile" should be replaced with the full path to the folder examples/solar_dhw in your local repository.
This script replaces the **pytrnsys-run** command and starts a pytrnsys run with the given
configuration file. Similarly the processing can be started with the following minimal example

.. code-block:: python

    from pytrnsys.psim import processParallelTrnsys as pParallelTrnsys

    pathConfig = "pathToTheConfigFile"
    configFile = "process_solar_dhw.config"
    tool = pParallelTrnsys.ProcessParallelTrnsys()
    tool.readConfig(pathConfig,configFile)
    tool.process()


If you would like to continue to modify the config file as described in the :ref:`tutorial <tutorial>`, make a local copy of the
example folders such that tha changes will not be tracked by GIT.

Create your own processing class
--------------------------------
Pytrnsys provides a large number of possibilities to process and plot results
with the processing configuration file. But sometimes this is not enough!
If you would like to add your own Python code to the processing you can create
your own processing class that inherits from the class pytrnsys.psim.processTrnsysDf.

.. code-block:: python

    import pytrnsys.psim.processTrnsysDf as processTrnsys

    class MyProcess(processTrnsys.ProcessTrnsysDf):

        def __init__(self,pathFolder, fileName):
            processTrnsys.ProcessTrnsysDf.__init__(self,pathFolder, fileName)

        #define your own functions
        def myCalculation()
            myValue=foo+bar

        # overwrite this function and fill it with your content
        def customCalculations()
            self.myCalculation

This class can then be saved in your preferred location. In order to use the custom processing
class the pytrnsys.rsim.runParallelTrnsys class has to be modified such that it instantiates
the new class. This can be done by replacing the run script in the following way.

.. code-block:: python

    from pytrnsys.psim import processParallelTrnsys as pParallelTrnsys
    import yourCustomClassFile

    class MyProcessParallelTrnsys(pParallelTrnsys.ProcessParallelTrnsys):

        def __init__(self):
            pParallelTrnsys.ProcessParallelTrnsys.__init__(self)

        #The definition of this class is a must
        def getBaseClass(self, classProcessing, pathFolder, fileName):
           return yourCustomClassFile.MyProcess(pathFolder, fileName)

    if __name__ == '__main__':
        pathConfig = "pathToTheConfigFile"
        configFile = "process_solar_dhw.config"
        tool = MyProcessParallelTrnsys()
        tool.readConfig(pathConfig,configFile)
        tool.process()

General guidelines for developers
---------------------------------
Pytrnsys is open source and developers are invited to submit their own contributions.
If you would like to develop for pytrnsys, we are interested in who you are. We are happy
about a short message by mail. Please discuss new ideas first in the issue board. You are
invited to work on the issues and create a pull request when finished. When working on the code,
please consider the following style guidelines:

- we use the UpperCamelCase convention for Class names and the lowerCamelCase convention for everything else

- Please use `Numpy/Scipy <https://numpy.org/devdocs/docs/howto_document.html>`_ inline code documentation as much as possible

- Please chose meaningful variable names and use in line comments only where really needed.





