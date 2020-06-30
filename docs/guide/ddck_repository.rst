.. _ddck_repository:

Ddck repository
===============

Pytrnsys enhances system simulations by making use of component modularization. This is done by seperating the dck file
part in which a single components of an energy system simulation is defined into ddck files. In a pytrnsys run, these
ddck files will then be merged together in order to build the full system ddck. Pytrnsys comes with a default repository
of ddck files that is installed alongside the main package.

Repository content
------------------
The repository contains the following subfolders::

    pytrnsys_ddck
    +-- air_source_heat_pump
    +-- battery
    +-- boiler
    +-- brine_source_heat_pump
    +-- brine_source_heat_pump_two_hex
    +-- building
    +-- control
    +-- demands
    +-- dlls
    +-- generic
    +-- ground_heat_exchanger
    +-- heat_exchanger
    +-- building
    +-- ice_storage
    +-- pv
    +-- solar_collector
    +-- weather
    +-- __init__.py
    +-- example.ddck
    +-- generalVariables.ddck
    +-- NOMENCLATURE.txt

Each subfolder represents one component, that is supported by default in the pytrnsys GUI. A lot of
the components - but not all of the - are used in the pytrnsys example systems. Each component
subfolder has the following structre. Not all folders and files are present in all components::

    pytrnsys_ddck
    +-- component subfolder
        +-- typeX subfolder1
            +-- typeX.ddck
            +-- database
        +-- typeY subfolder2
            +-- typeY.ddck
            +-- database
        +-- non type related ddcks
        +-- profiles

Some components can be represented by different TRNSYS types. Usually a more basic one of the
standard library and a advanced custom model that allow for detailed parametrization. Each TRNSYS type
is represented by its own subfolder in the component folder. In the type subfolder, the main
ddck of the type is stored. This ddck contains both the TRNSYS type parameter and input section
the type output section as well as some equations for parameter and input scaling or output
processing. The parametrization of the model is outsourced in the database folder where a specific
version - for example parameters of a specifica collector curve - can be specified.

Ddck file structure
-------------------

The file sctructure of the ddck files is shown in the example.ddck file in the pytrnsys_ddck repository root.
Each ddck should contain the following parts. Some parts can be empty if not used.

Header
^^^^^^
In the header the name of the ddck as well as a contact persion, the creation date and some information
about the last changes are specified. In addition, there is a section for general descriptions
about the ddck::

    *******************************
    **BEGIN example.ddck
    *******************************

    *****************************************
    ** Contact person : author
    ** Creation date  : date
    ** Last changes   : date, name
    *****************************************

    ***************************************************************************
    ** Description:
    ** Overall description of the ddck file
    ** TODO: Any improvements needed
    ***************************************************************************

Inputs from hydraulics solver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The pytrnsys ddcks are designed to be used in combination with the hydraulic solver type 935.
In each timestep the hydraulic solver computes all mass flows and component input temperatures starting
depending on the component output temperatures, the pump powers and the valve positions. Therefore,
the mass flows and component input temperatures are outputs of the hydraulic solver that have to
be connected to the component ddcks as inputs::

    ***********************************
    ** inputs from hydraulic solver
    ***********************************

    ** tIn from hydraulic
    ** mIn from hydraulic

Outputs to the hydraulic solver
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Similar to the inputs, the output temperatures of the component should be stated here, such that
they are easily accessible to be connected to the hydraulics file::

    ***********************************
    ** outputs to hydraulic solver
    ***********************************

    ** which outputs will be used to connect the hydraulic solver
    ** typically tOutType will be defined here to be used in the hydraulic ddck

Outputs to the energy balance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In the processing, pytrnsys automatically computes the systems heat and electricity energy balance.
All variables that should be collected for the energy balance have to be specified in this section according to
the right nomenclature::

    ******************************************************************************************
    ** outputs to energy balance in kWh and ABSOLUTE value
    ** Following this naming standard : qSysIn_name, qSysOut_name, elSysIn_name, elSysOut_name
    ******************************************************************************************

    ** Add here those variables that will go into the overall energy balance of the system
    ** These values will be used to automatically generate the energy balance

Dependencies with other ddck files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In order to enhance modularization, dependencies with other ddcks should be kept minimal. Dependencies that
cannot be avoided and are neither part of the component-database relation or the general variables should be
declarated and reassigned to an internally used variable in this part::

    ***********************************
    ** Dependencies with other ddck
    ***********************************

    ** Re-assing here the variables necessary from other types
    ** variableInternal = variableExternal
    ** Exception: those from general variables

Outputs to other ddck files
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Variables that are designated to be used in other ddck files should be added here::

    ***********************************
    ** outputs to other ddck
    ***********************************

    ** Add here the outputs of the TYPE or TYPES that will be used in other types
    ** Exception: those for printers and so on dont need to be here.

Precalculations related to parameter scaling and pre-processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Usually, in the declaration of a TRNSYS component, many parameters are calculated out of more general
system variables. All calculations to determine the right parameters inputs for the type go here::

    ***********************************
    ** Begin CONSTANTS
    ***********************************

Type section
^^^^^^^^^^^^
TRNSYS has its own syntax that calls the type dll files. This core part of the ddck goes here::

    ***********************************
    ** Begin TYPE
    ***********************************

Component printers
^^^^^^^^^^^^^^^^^^
Each component should have a monthly as well as an hourly printer. This helps to simplify the setup
and the processing of the simulation. In addition, an online plotter is a nice tool for the debugging
of the system::

    ***********************************
    ** Monthly printer
    ***********************************

    ***********************************
    ** Hourly printer
    ***********************************

    ***********************************
    ** Online plotter
    ***********************************

Hydraulics files
----------------

The hydraulics file represents the systems hydraulics layout. Each pytrnsys example system except
the pv battery system has its own hydraulic layout file. In order to create your own hydraulic files
that represent the hydraulics of your choice you need access to the pytrnsys GUI. The hydraulics file
are not part of the ddck repository. The hydraulic files of the example systems are located in the
example system folder of **pytrnsys_examples**.

Examples
--------
The following example shows the ddck file of the solar collector type 1 used in the solar domestic
hot water system::

    *******************************
    **BEGIN Type1.ddck
    *******************************

    *****************************************
    ** Contact person : Dani Carbonell
    ** Creation date  : 10.01.2010
    ** Last changes   : 03.2020 Jeremias Schmidli
    *****************************************

    ***************************************************************************
    ** Description:
    ** Collector model using efficiency curve efficiency
    ***************************************************************************

    ***********************************
    ** inputs from hydraulic solver
    ***********************************

    EQUATIONS 2
    TCollIn = TPiColIn
    MfrColl = ABS(MfrPiColIn)

    ***********************************
    ** outputs to hydraulic solver
    ***********************************

    EQUATIONS 1
    TCollOut = [28,1]

    ***********************************
    ** outputs to other ddck
    ***********************************

    ******************************************************************************************
    ** outputs to energy balance in kWh and ABSOLUTE value
    ** Following this naming standard : qSysIn_name, qSysOut_name, elSysIn_name, elSysOut_name
    ******************************************************************************************

    EQUATIONS 1
    qSysIn_Collector = PColl_kW

    ***********************************
    ** Dependencies with other ddck
    ***********************************

    EQUATIONS 1
    pumpColOn = puColOn

    CONSTANTS 2
    C_tilt = slopeSurfUser_1  ! @dependencyDdck Collector tilt angle / slope [°]
    C_azim = aziSurfUSer_1    ! @dependencyDdck Collector azimuth  (0:s, 90:w, 270: e) [°]

    EQUATIONS 4
    **surface-8
    IT_Coll_kJhm2 = IT_surfUser_1  ! Incident total radiation on collector plane, kJ/hm2
    IB_Coll_kJhm2 = IB_surfUser_1  ! incident beam radiation on collector plane, kJ/hm2
    ID_Coll_kJhm2 = ID_surfUser_1  ! diffuse and ground reflected irradiance on collector tilt
    AI_Coll = AI_surfUser_1  ! incident angle on collector plane, °

    EQUATIONS 5
    IT_Coll_kW = IT_Coll_kJhm2/3600     ! Incident total radiation on collector plane, kW/m2
    IB_Coll_kW = IB_Coll_kJhm2/3600     ! incident beam radiation on collector plane, kW/m2
    ID_Coll_kW = ID_Coll_kJhm2/3600     ! diffuse and ground reflected irradiance on collector tilt (kW/m2)
    IT_Coll_Wm2 = IT_surfUser_1/3.6
    IT_Coll_kWm2 = IT_surfUser_1/3600

    ***********************************
    ** Begin CONSTANTS
    ***********************************

    CONSTANTS 3
    MfrCPriSpec = 15  ! Coll. Prim. loop spec. mass flow [kg/hm2]
    AcollAp=5         ! Collector area
    MfrCPriNom = MfrCPriSpec*AcollAp !

    ***********************************
    ** Begin TYPE
    ***********************************

    UNIT 28 TYPE 1
    PARAMETERS 11
    nSeries       ! number in series
    AcollAp       ! collector area
    cpBri          ! fluid specific heat kj(kgK
    efficiencyMode ! efficiency mode
    testedMfr      ! tested flow rate kg/(hm2)
    Eta0          ! intercept efficiency
    a1            ! efficiency slope kJ/hm^2K
    a2            ! efficiency curvature kJ/hm^2K^2
    2             ! optical mode
    FirstOrderIAM  ! 1st order IAM
    SecondOrderIAM ! 2nd order IAM
    INPUTS 9
    TCollIn
    MfrColl
    Tamb
    IT_Coll_kJhm2
    IT_H
    ID_Coll_kJhm2
    0,0
    AI_Coll !Flo check ! JS: This was defined wrong before (C_azim, even though it is incident angle input). Now it should be correct.
    C_tilt !Flo check  ! JS: This should be correct
    *** INITIAL INPUT VALUES
    20 0 10 0 0 0 GroundReflectance 45 0

    EQUATIONS 4
    **MfrCout = [700,2]
    Pcoll = [28,3] !kJ/h
    PColl_kW = Pcoll/3600
    PColl_kWm2 = PColl_kW/(AcollAp+1e-30)
    PColl_Wm2  = PColl_kWm2*1000


    ***********************************
    ** Monthly printer
    ***********************************

    CONSTANTS 1
    unitPrintSol = 31

    ASSIGN temp\SOLAR_MO.Prt unitPrintSol

    UNIT 32 TYPE 46
    PARAMETERS 6
    unitPrintSol ! 1: Logical unit number, -
    -1           ! 2: Logical unit for monthly summaries, -
    1            ! 3: Relative or absolute start time. 0: print at time intervals relative to the simulation start time. 1: print at absolute time intervals. No effect for monthly integrations
    -1           ! 4: Printing & integrating interval, h. -1 for monthly integration
    1            ! 5: Number of inputs to avoid integration, -
    1            ! 6: Output number to avoid integration
    INPUTS 4
    Time  Pcoll_kW  PColl_kWm2  IT_Coll_kWm2
    **
    Time  Pcoll_kW  PColl_kWm2  IT_Coll_kWm2

    ***********************************
    ** Hourly printer
    ***********************************

    CONSTANTS 1
    unitHourlyCol = 33

    ASSIGN    temp\SOLAR_HR.Prt    unitHourlyCol

    UNIT 34 TYPE 46     ! Printegrator Monthly Values for System
    PARAMETERS 7
    unitHourlyCol ! 1: Logical unit number, -
    -1            ! 2: Logical unit for monthly summaries, -
    1             ! 3: Relative or absolute start time. 0: print at time intervals relative to the simulation start time. 1: print at absolute time intervals. No effect for monthly integrations
    1             ! 4: Printing & integrating interval, h. -1 for monthly integration
    2             ! 5: Number of inputs to avoid integration, -
    4             ! 6: Output number to avoid integration
    5             ! 7: Output number to avoid integration
    INPUTS 6
    Pcoll_kW  PColl_kWm2  IT_Coll_kWm2 TCollOut TCollIn MfrColl
    **
    Pcoll_kW  PColl_kWm2  IT_Coll_kWm2 TCollOut TCollIn MfrColl


A specific parametrization can be added by using a ddck from the database for example the
type1_CONSTANTS_cOBRAak2_8v.ddck::

    ******************************
    **BEGIN Type1_Constants_CobraAK2_8V.ddck
    *******************************

    *****************************************
    ** Solar Thermal Data for covered collector.
    ** Very well performing collector Cobra AK 2.8V
    ** Version : v0.0
    ** Last Changes: Jeremias Schmidli
    ** Date: 10.03.2020
    ******************************************

    CONSTANTS 11

    Eta0= 0.857     ! Eta0 (a0) of collector (zero heat loss efficiency)
    a1 = 4.16*3.6    ! linear heat loss coefficient of collector [kJ/hm^2K] ![W/m2K]*3.6
    a2 = 0.0089*3.6   ! quadratic heat loss coefficient of collector [kJ/hm^2K^2] ![W/m2K2]*3.6

    AbsorberArea = 2.435 !m2
    TotArea = 2.768 !m2

    nSeries = 1
    efficiencyMode = 1
    testedMfr = 200/AbsorberArea !l/hm2

    GroundReflectance = 0.2

    FirstOrderIAM = 0.108
    SecondOrderIAM = 0
    *******************************
    **END Type1_Constants_Test.ddck
    *******************************



