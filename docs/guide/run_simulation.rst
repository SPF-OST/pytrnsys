.. _config_file:

Running simulations
===================

Ddck files
----------

The core of the run configuration file is the ddck section. In this part of the configuration file, the different
modular ddck files that should be used in the simulation are specified. Pytrnsys offers its own ddck repository in the
separate package pytrnsys_ddck that is installed together with the main package and used in the example projects of
pytrnsys_examples. In the ddck section of the config file, the different ddcks that should be merged to the
simulation's main dck file are specified according to the following syntax::

    ROOTPATH1$ pathtoddck1\ddck1
    ROOTPATH1$ pathtoddck2\ddck2
    ROOTPATH2$ pathtoddck3\ddck3

The root of the ddck repositories used has to be defined elsewhere in the configuration file::

    string ROOTPATH1$ "pathToTheRepository1Root"
    string ROOTPATH2$ "pathToTheRepository2Root"

An example can be found in the example section below. The path to the repository root can be either absolute or
relative. If a relative path is detected, pytrnsys will interpret it as relative to the configuration file location.

Parameter variation
-------------------

A second core feature of pytrnsys is activated in the run configuration file in a parameter variation section. Pytrnsys
allows either to modify TRNSYS simulation parameters in the configuration file statically or with variations that
result in parametric runs. A static parameter change that can affect TRNSYS variables that are defined in EQUATIONS or
in CONSTANTS blocks of the dck file are initiated by::

    deck trnsysVariableName value

A parametric study is defined by::

    variation trnsysVariableName value1 value2 value3 ...

Both keywords can be used multiple times. If multiple variations are used, they are combined depending on the parameter
``combineAllCases``. If this parameter is set to True all variations are combined pairwise. So if n values are given
for variation 1 and m values are in variation 2 the total amount of simulations executed will be (m x n). If
``combineAllCases`` is set to False, the amount of values of all variations has to be equal and they are combined
according to their order.

.. _ref-changeDDckFile:

In addition to a single equation or constant line in the dck, pytrnsys offers the possibility to loop through different
ddck files during a parametric study. A parametric study on ddck files can be defined by::

    changeDDckFile originalDdck ddckVariation1 ddckVariation2 ddckVariation3 ...

Parameters
----------

There are different additional parameters that define the simulation runs. The ones that have no default values are
mandatory.

Generic
^^^^^^^^

``ignoreOnlinePlotter`` (bool, default False)
    If set to True, the TRNSYS online plotters are commented out in all the dck-files. No online plotters
    are shown during the simulation run. The TRNSYS progress bar window is still displayed.

``removePopUpWindow`` (bool, default False)
    Online plotters as well as the progress bar window are suppressed during the simulations.
    (TRNSYS hidden mode)

``checkDeck`` (bool, default True)
    If set to True, during merging the ddck-files, the specified and given amount of Equations and Parameters in
    each block are checked for inconsistencies.

``parseFileCreated`` (bool, default True)
    Saves the parsed dck-file that can be used to locate the line where ``checkDeck`` found errors.

``runCases`` (bool, default True)
    If set to False, the dck-files are created and saved in the normal structure but not executed.

``reduceCpu`` (int, default 0)
    Number of CPUs that are not used in the parallel simulation runs.

``outputLevel`` (string, default "INFO")
    Output message level according to the logging package. (Options are "DEBUG", "INFO", "WARNING", "ERROR", and
    "CRITICAL".)

Automatic Work Bool
^^^^^^^^^^^^^^^^^^^
.. _doAutoUnitNumbering:

``doAutoUnitNumbering`` (bool, default True)
    If set to True, the units of the merged dck-file are renumbered to avoid duplicates. This parameter
    should usually be set to the default True.

.. _generateUnitTypesUsed:

``generateUnitTypesUsed`` (bool, default True)
    If set to True, a file called ``UnitType.info`` containing the TRNSYS-Type numbers used is saved in the main run-folder.

.. _addAutomaticEnergyBalance:

``addAutomaticEnergyBalance`` (bool, default True)
    If set to True, an automatic energy balance printer is created in the dck file. For more information
    see :ref:`ref-defaultPlotting`.

Paths
^^^^^

``trnsysExePath`` (string, default "environmentalVariable")
    Path to the ``TRNExe.exe`` of the TRNSYS installation. If not set, pytrnsys tries to
    find the path in the system environmental variable "TRNSYS_EXE".

``pathBaseSimulations`` (string)
    If specified, the location of the simulation run is changed to the given path.
    It overrules the normal behavior of executing the simulations in the command line
    working directory.

.. _ref-addResultsFolder:

``addResultsFolder`` (string or False, default False)
    If specified as a string, a new folder for the simulations is created with this name.

Scaling
^^^^^^^

.. _ref-scaling:

``scaling`` (("False","toDemand"), default False)
    If set to "toDemand" the parameter scaling functionality is activated. Please refer to
    :ref:`scaling tutorial <ref-scalingTutorial>` for more details.

.. _ref-scalingReference:

``scalingReference`` (string)
   Path to the scaling results. Please refer to
   :ref:`scaling tutorial <ref-scalingTutorial>` for more details.

.. _ref-scalingVariable:

``scalingVariable`` (string)
   Variable that is taken from the results json file for scaling. Please refer to
   :ref:`scaling tutorial <ref-scalingTutorial>` for more details.

``nameRef`` (string)
    Base name of the dck-file created. Default base name is "pytrnsysRun".

``runType`` (("runFromConfig", "runFromCases", "runFromFolder"), default "runFromConfig")
    "runFromCases" and "runFromFolder" offer some advanced option for custom simulation runs.

Example
-------
Here is an example of a run configuration file.
It is taken from the example project solar_dhw (``run_solar_dhw.config``)::

    ######### Generic ########################
    bool ignoreOnlinePlotter  True
    int reduceCpu  4
    bool parseFileCreated True
    bool runCases True
    bool checkDeck True

    ############# AUTOMATIC WORK BOOL##############################

    bool doAutoUnitNumbering True
    bool generateUnitTypesUsed True
    bool addAutomaticEnergyBalance True

    #############PATHS################################

    string trnsysExePath "C:\Trnsys17\Exe\TRNExe.exe"
    string addResultsFolder "solar_dhw"
    string PYTRNSYS$ "..\..\pytrnsys_ddck\"
    string LOCAL$ ".\"

    ################SCALING#########################

    string scaling "False" #"toDemand"
    string nameRef "SFH_DHW"
    string runType "runFromConfig"

    #############PARAMETRIC VARIATIONS##################

    bool combineAllCases True
    variation Ac AcollAp 2 3 4 6 8 10
    variation VTes volPerM2Col 75 100

    #############FIXED CHANGED IN DDCK##################

    deck START 0    # 0 is midnight new year
    deck STOP  8760 #
    deck sizeAux 3

    #############USED DDCKs##################

    PYTRNSYS$ generic\head
    PYTRNSYS$ demands\dhw\dhw_sfh_task44
    PYTRNSYS$ weather\weather_data_base
    PYTRNSYS$ weather\SIA\normal\CitySMA_dryN
    PYTRNSYS$ solar_collector\type1\database\type1_constants_CobraAK2_8V
    PYTRNSYS$ solar_collector\type1\type1
    LOCAL$ solar_dhw_control
    LOCAL$ solar_dhw_storage1
    LOCAL$ solar_dhw_hydraulic
    LOCAL$ solar_dhw_control_plotter
    PYTRNSYS$ generic\end