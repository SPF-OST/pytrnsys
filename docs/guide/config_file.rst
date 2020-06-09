.. _config_file:

The pytrnsys configuration files
================================

Pytrnsys runs and processes TRNSYS simulations based on configurations files. The general idea behind is to provide
a fast and easily accessible way to define, run and analyse both single simulations as well as parametric studies.
There are distinct configuration files for running and processing. Both are described in the following sections bur follow
the same syntax and format.


Configuration file format
*************************

The configuration file does not require a header and should contain different keyword commands on single lines.
Comments start with ``#`` characters. End of line comments are possbile.

There config file supports the following basic types:

==========================  ===================================
*bool*                      with True/False as possible value
*int*                       with any interger as possible value
*string*                    with any string as possible value
*stringArray*               array of strings
==========================  ===================================

Parameters that are used to specifiy the run can be defined by::

    keyword parameter_name value

In the case of and integere this would for example be::

    int reduceCpu  4


.. note::

   The ``string`` and ``stringArray`` always have to be specified with parentheses.




Run configuration file
**********************
Ddck section
------------

The core of the run configuration file is the ddck section. In this part of the configuration
file the different modular ddck files that should be used in the simulation are specified.
Pytrnsys offers its own ddck repository in the seperate package pytrnsys-ddck that is installed
along the main package and used in the example projects of pytrnsys-examples. In the ddck section
of the config file, the different ddcks that should me merged to the simulation's main dck-file
are specified according to the following syntax::

    ROOTPATH1$ pathtoddck1\ddck1
    ROOTPATH1$ pathtoddck2\ddck2
    ROOTPATH2$ pathtoddck3\ddck3

The root of the ddck repository used has to be defined elsewhere in the configuration file::

    string ROOTPATH1$ "pathToTheRepository1Root"
    string ROOTPATH2$ "pathToTheRepository2Root"

An example can be found in the example section below. The path to the repository root can either be
absolute or relative. If a relativ path is detected, pytrnsys will interpret it as relative to
the configuration file location.

Parameter variation section
---------------------------

A second core feature of pytrnsys is activated in the run-configuration file in a parameter
variation section. Pytrnsys allows to modify TRNSYS simulation parameters in the configuration
file either statically or with variations that result in parametric runs. A static parameter change
that can affect TRNSYS variables that are defined in EQUATIONS or in CONSTANTS blocks of the dck file
is initiated by::

    deck trnsysVariableName value

A parametric study is defined by::

    variation trnsysVariableName value1 value2 value3 ...

Both keywords can be used multiple times. If multiple variations are used, they are combined
depending on the parameter ``combineAllCases``. If this parameter is set to True all variations
are combined pairwise. So if n values are given for variation 1 and m values are in variation 2
the total amount of simulations executed will be (m x n). If ``combineAllCases`` is set to false,
the amount of values of all variations has to be equal and the are combined according to their order.


Parameters
----------

There are different additional parameters that define the simulation runs. The ones that have no
default values are mandatory.

Generic
^^^^^^^^

``ignoreOnlinePlotter`` (bool, default False)
    If set to True, the TRNSYS online plotters are commented out in all the dck-files. No online plotters
    are shown during the simulation run. The TRNSYS progress bar windos is still displayed.

``removePopUpWindow`` (bool, default False)
    Online plotters as well as the progress bar window are suppressed during the simulations.
    (TRNSYS hidden mode)

``checkDeck`` (bool, default True)
    If set to True, during merging the ddck-files, the specified and given amount of Equations and Parameters in
    each block are checked for inconsistencies.

``parseFileCreated`` (bool, default True)
    Saves the paresed dck-file that can be used to locate the line where ``checkDeck`` found errors.

``runCases`` (bool, default True)
    If set to False, the dck-files are created and saved in the normal structure but not executed.

``reduceCpu`` (int, default 0)
    Number of CPUs that are not used in the parallel simulation runs.


Automatic Work Bool
^^^^^^^^^^^^^^^^^^^

``doAutoUnitNumbering`` (bool, default True)
    If set to True, the units of the merged dck-file are renumbered to avoid dublicates. This parameter
    should almost always be set to the default True.

``generateUnitTypesUsed`` (bool, default True)
    if set to True, a file called ``UnitType.info`` containing the TRNSYS-Type numbers used is saved in the main run-folder.

``addAutomaticEnergyBalance`` (bool, default True)
    If set to True, an automatic energy balance printer is created in the dck-file. For more information
    see (autmoatic energy balance section!!!!!!)

Paths
^^^^^

``trnsysExePath`` (string, default "environmentalVariable")
    Path to the ``TRNExe.exe`` of the TRNSYS installation. If not set, pytrnsys tries to
    find the path in the system environmental variable "TRNSYS_EXE".

``pathBaseSimulations`` (string)
    If specified, the location of the simulation run is changed to the given path.
    It overrules the normal behavior of executing the simulations in the command line
    working directory.

``addResultsFolder`` (string or False, default False)
    If specified as a string, a new folder for the simulations is created with this name.

Scaling
^^^^^^^

``scaling`` (("False","toDemand"), default False)
    If set to "toDemand" the parameter scaling functionality is activated. Please refer to
    (Scaling section!!!!!!!!!!!) for more details.

``nameRef`` (string)
    Base name of the dck-file created. Default base name is "pytrnsysRun".

``runType`` (("runFromConfig", "runFromCases", "runFromFolder"), default "runFromConfig")
    "runFromCases" and "runFromFolder" offer some advanced option for custom simulation runs.



Example
-------
Here is an example of a run-config file.
It is taken from the example project solar_dhw (``run_solar_dhw.config``)::

    ############# GENERIC##############################

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
    string addResultsFolder "SolarDHW_newProfile"
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




Process configuration file
**************************

Pytrnsys processing modules automatically reads in the simulation results of the pytrnsys runs
and - by default - calculates energy balances as well as collects some of the most important
information of the simulation like iteration problems and system performance factors in a results
PDF-file. The process configuration file allows to configure the processing. In addition
further calculations with the simulation results and additional plots can be defined.

Calculations
------------

During processing pytrnsys reads in the following values automatically:

1.  All parameter and equation variables that are statically defined in
    the dck.file. Pytrnsys recursively detects static variables by checking
    for any type outputs in the variables involved.

2.  All monthly printer values of the simulation. The pytrnsys ddcks save all
    printer files in the temp folder inside the directory where the simulation is
    executed. If custom printers are defined, the same location is required.

3.  All hourly printer values of the simulation.

All values can be adressed in the config file by their name in the header of the trnsys printer file.
It is recommended to dublicate the internal TRNSYS name in the header of the printer.

.. note::

    While TRNSYS is not case sensitive, Python is. So be careful about upper and lower cases
    during post processing. If the string in the configuration file does not match the header
    of ther printer file or the TRNSYS name of the static parameter in the dck-file,
    pytrnsys will not be able to find the value and throw a key-error.

By default, pytrnsys also calculates the following values:

4.  Total yearly sum of the monthly printed values. The yearly sum of a monthly
    printed variable with the name ``foo`` can be accessed for further processing
    by ``foo_Tot``.

5.  The maximum hourly value of an hourly printed file. The hourly maximum of an hourly
    printed variable with the name ``bar`` can be accessed by ``bar_Max``.

Custom calculation keywords
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the processing-configuration file, the user can specify custom calculations based on the
readed TRNSYS results and the values that are calculated by default. The type of each equation has to be
defined by a key word that tells pytrnsys what values should be used. This is necessary since
some variables could be both in an hourly as well as a monthly printer. The following calculation keywords
are available:

``calc``
    Calculates a new scalar value out of scalar other scalar values such as static TRNSYS parameters
    or yearly sums or hourly maxima.

``calcMonthly``
    Calculates new monthly values (array with length 12) out of other monthly values or scalar values.

``calcHourly``
    Calculates new hourly values (array with length 8760) out of other hourly values or scalar values.

A caluclations section could be of the following structure. A full working example can be
found in the example below::

    calc alpha = foo_Tot/bar_Max
    calcMonthly = foo/foo_Tot*1000
    calcHourly = (bar+100)**2

Plotting
--------
Default plotting
^^^^^^^^^^^^^^^^
By default the processing creates a pdf with the following content:

1.  A table displaying the total simulation time and the number of iteration errors.

2.  A table with the monthly heat balance. The values are also shown in a plot the in the case
    of the solar domestic hot water example system looks like this:

.. image:: ./resources/HeatMonthly.png
      :width: 400
      :alt: Monthly heat balance

3.  A electricity balance similar to the heat balance.

4.  The system seasonal performance factor both in a table and a plot. Again, the SPF
    plot of the solar domestic hot water system looks like:

.. image:: ./resources/SPF_SHP.png
      :width: 400
      :alt: SPF

Custom plotting and printing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The user can add additional monthly plots to the processing of a single simulation
run by the use of the following parameters. The custom defined plots will automatically
be added to the result pdf-file:

``monthlyBars`` (stringArray)
    Plots a monthly bar plot that shows all variables grouped side by side.

.. image:: ./resources/NBar.png
      :width: 400
      :alt: SPF

``monthlyBalance`` (stringArray)
    Custom monthly balance. The sign of the values can be inverted by adding a - in front of
    the variable name. If positive and negative values don't add up to zero, the imbalance
    is shown as black bars. In the solar domestic hot water example system this can be demonstrated
    by plotting the two system inputs :math:`Q_{col}` and :math:`El_{Aux}^{Tes}` and the usable
    output of the domestic hot water demand. The imbalance in this case are the overall losses of
    the system.

.. image:: ./resources/CustomBalance.png
      :width: 400
      :alt: SPF

``monthlyStackedBar`` (stringArray)
    Similar to the ``monthlyBalance`` but without showing the imbalance.

.. image:: ./resources/StackedBar.png
      :width: 400
      :alt: SP

``comparePlot`` (stringArray x-Axis y-Axis series style)
    When processing parametric runs, scalar results of the simulations can be visualized in
    comparison plots. The first variable of the string array is shown on the x-axis.
    The second variable is shown on the y-axis. The third is represented as diefferent lines
    and the fourth as different marker styles.

.. image:: ./resources/ComparisonPlot.png
      :width: 400
      :alt: SP

.. note::

    It is required, that all variables used in comparison plots are saved in the results json-file.

``plotHourly`` (stringArray)
    Hourly printed values can be displayed in a interactable html-plot that is created using the bokeh
    plotting library.

.. image:: ./resources/bokeh_plot.png
      :width: 400
      :alt: SP


Results file
------------

For further custom processing of the simulation results, required scalar and monthly values
can be saved to a results json-file.

Example
-------










