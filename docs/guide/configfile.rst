.. _configFile:

------------------
Config-File Syntax
------------------

The idea of the config files is to include general functionality without having to type python code for the user.
Thus, this config file will grow as long as users believe some functionality is used so often that its worth to implemente it within the config file. All the functionality not included in the config file will need to be implemented as python code and thus will be a bit limited to those knowing how to program in python. 

1. Type of Variables
----------------------

There are several types of variables with scape separator:

==========================  =============================================================
*bool*                      with True/False as possible value
*int*                       with any interger as possible value
*string*                    with ``any string`` as possible value
*deck*                      | with any float/int as possible value. If a string is needed 
                            | then the format deck name string anystring should be used.
*STRING\$*                  | ddck file path. STRING\$ needs to 
                            | define one path of the ddck folder.
*variation*                 | used to do parametric variations of 
                            | chaginfg deck variables. For parallel 
                            | simulations
*changeDdckFile*            | used to do changes on the ddck files 
                            | loaded in the config, e.g. weather 
                            | data
**PATH*$*                   | string variable specified in the ddck file, used as base 
							| directory for a path
*calc*            			| used to do calculate scalar values from deck variables or
                            | yearly sums or yearly max. yearly sum of a monthly printed
                            | variable "a" is available as "a_Tot" (a_Max for maximum of
							| hourly printed variables)
*calcMonthly*            	| used to calculate new monthly values from monthly printed 
                            | variables and scalar variables
*stringArray*				| array of strings
==========================  =============================================================

2. Input variables Run-Config-File
----------------------------------

==========================  =============================================================
ignoreOnlinePlotter         *bool*, ignore the online plotters during the run
*removePopUpWindow*         *bool*, don't show the trnsys pop up window during the run
*reduceCpu*                 *int*, reduce CPUs used in parallel runs by this number
*runCases*                  *bool*, If Flase it will build decsk but without executing
*addAutomaticEnergyBalance*	*bool*, build automatic energy balance monthly plot
*doAutoUnitNumbering*		*bool*, replace unit numbers to avoid dublicates
*trnsysExePath*				*STRING\$*, path to the TRNSYS executable
*addResultsFolder*			*STRING\$*, adds a folder for the simulations
*nameRef*					*STRING\$*, name for the DCK-file
*pathBaseSimulations*		*STRING\$*, Path where the results folder will be created
*pathBaseSimulations*		*STRING\$*, Path where the results folder will be created
*runType*					[runFromConfig,runFromFolder,runFromCases], run type
*combineAllCases*       	| *bool*, true: use all combinations of variations,
							| false: combine the according to their position
==========================  =============================================================

3. Input variables Process-Config-File
--------------------------------------

==========================  =============================================================
*processParallel*         	*bool*, use parallel processing
*cleanModeLatex*         	*bool*, delete all plot files after latex is compiled
*forceProcess*              *bool*, overwrites existing process files
*yearReadedInMonthlyFile*   | *int*, number of the year used in case of multi year 
							| simulation. -1 takes the last year.
*firstMonthUsed*			*int*, first month in the year used for processing 0=january
*reduceCpu*                 *int*, reduce CPUs used in parallel runs by this number
*pathBase*					*STRING\$*, path to the folder to be processed
*matplotlibStyle*			| *STRING\$*, matplotlib style to be used for plots
							| can also be a path to a custom style sheet
*plotHourly*				| *stringArray*, hourly printed variables that are saved in a
							| bokeh plot
*plotT*						| *stringArray*, hourly printed variables that are plotted in
							| frequency distribution plot
*results*					| *stringArray*, scalar or monthly variables that should be
							| printed in a result JSON-file
*dllTrnsysPath*				*STRING\$*, Path of the custom dlls
==========================  =============================================================

4. Examples
-----------
4.1 Run-Config-File
^^^^^^^^^^^^^^^^^^^^
Example of a Run-Config-File::

	bool ignoreOnlinePlotter  True
	int reduceCpu  1
	bool parseFileCreated True
	bool runCases True
	bool checkDeck True

	bool doAutoUnitNumbering True
	bool generateUnitTypesUsed True
	bool addAutomaticEnergyBalance True

	string trnsysExePath "C:\Trnsys17\Exe\TRNExe.exe"
	string addResultsFolder "SolarDHW"
	string HOME$ "C:\Daten\GIT\TriHpTrnsysDDeck"
	string SPF$ "C:\Daten\GIT\spfTrnsysFiles"
	string LOCAL$ "C:\Daten\GIT\SolTherm2050Ddck\"

	string scaling "False" #"toDemand"
	#string pathRef "C:\Daten\OngoingProject\BigIce\Simulations\BICE-HydD_circ-8Cities-Ref"
	#string nameRef "BICE-HydD_circ-Ac136.4-Vice27.3-MFH"

	string runType "runFromConfig"

	bool combineAllCases True
	variation Ac AcollAp 10 15 20
	variation VTes colPerM2Col 75 100

	deck START 0    # 8760-744 4354 4344 is july first, 5088 is august first
	deck STOP  8760 # 8760*2


	HOME$ Generic\Head
	HOME$ DemandsDHW\DHW-MFH
	#HOME$ Printers\DHWPrinter
	HOME$ weatherData\WeatherDataBase
	HOME$ weatherData\SIA\Normal\CityKLO_dryN
	HOME$ SolarCollector\SolarCollector
	HOME$ SolarCollector\uncoveredSelectiveESSA
	#LOCAL$ Control\SolarController_Type2
	HOME$ Control\Control-DemoDhw
	HOME$ Tes\Type1924_DHW
	HOME$ Hydraulics\DHWSPFExample
	#HOME$ Plotter\OnlinePlotter
	HOME$ Generic\End
	

4.1 Process-Config-File
^^^^^^^^^^^^^^^^^^^^^^^^
Example of a Process-Config-File::

	bool processParallel False
	#bool avoidUser True
	bool processQvsT True
	#bool maxMinAvoided False
	bool cleanModeLatex False
	bool forceProcess  True #even if results file exist it proceess the results, otherwise it checks if it exists
	bool setPrintDataForGle True
	#########
	int yearReadedInMonthlyFile -1
	int firstMonthUsed 0     # 0=January 1=February 6=July 7=August
	int reduceCpu 1
	#########
	string typeOfProcess "completeFolder" # "casesDefined"
	#string typeOfProcess "casesDefined"

	#string caseProcessed "SolarDHW"
	string pathBase "C:\Daten\GIT\TriHpPythonProjects\pytrnsys_trihp\pycharm\demo_dhw\SolarDHW"



	string typeOfSimulation "colDHW"
	#calc Fsolar_Tot = -Qdp1_Tes1_Tot/Pdhw_kW_Tot
	#calc TesEff     = -Qdp1_Tes1_Tot/Qhx1_Tes1_Tot



	calcMonthly Fsolar = qSysIn_Collector/qSysOut_DhwDemand


	calc Pcoll_kWhM2_Tot = qSysIn_Collector_Tot/AcollAp
	calc Pcoll_MWh_Tot   = qSysIn_Collector_Tot/1000


	stringArray results "AcollAp"  "Vol_Tes1" "Fsolar"  # values to be printed to json