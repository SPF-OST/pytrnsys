import pytrnsys.trnsys_util.replaceAssignStatements as _ra


_ORIGINAL_DECK_CONTENT = r"""\
**********************************************************************
** head.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\generic 
**********************************************************************
*******************************
**BEGIN Head.ddck
*******************************
CONSTANTS 3
mfrSolverAbsTol = 1e-6
mfrSolverRelTol = 1e-9
mfrTolSwitchThreshold = 1
VERSION 17    
CONSTANTS 5
START=0.0 ! value changed from original by executeTrnsys.py
STOP=8760.0 ! value changed from original by executeTrnsys.py
dtSim=1. ! value changed from original by executeTrnsys.py
dtSim_SI = dtSim*3600
dt_s = dtSim_SI ! remove later
CONSTANTS 13
nIteTrnsys = 30      ! TRNSYS Limit of iterations
nWarnTrnsys = 12000  ! TRNSYS Limit of warnings
nCallTraceTrnys = 31 ! TRNSYS limit of calls to a component before it will be traced
FrInte_Tol = 0.003   ! TRNSYS solver tolerances      
FrConv_Tol = 0.0005  ! TRNSYS solver tolerances    
nan_check_bool = 1   ! TRNSYS nan check boolean
time_report = 1      ! TRNSYS time report
solver_equation = 0  ! TRNSYS EQUATION SOLVER statement
debug_statement = 0  ! TRNSYS Overwrite DEBUG statement
solver_statement = 0 ! TRNSYS Solver statement
min_relax_factor = 1 ! TRNSYS Minimum relaxation factor
max_relac_factor = 1 ! TRNSYS Maximum relaxation factor 
solver_integration = 1    ! TRNSYS numerical integration solver method
SIMULATION START STOP dtSim     
TOLERANCES    FrInte_Tol  FrConv_Tol     
LIMITS nIteTrnsys nWarnTrnsys nCallTraceTrnys ! Limit of Iterations, limit of warnings, limit of calls to a component before it will be traced
DFQ solver_integration                        ! TRNSYS numerical integration solver method
WIDTH 132                                     ! TRNSYS output file width, number of characters
LIST                                          ! NOLIST statement
SOLVER solver_statement min_relax_factor max_relac_factor      ! Solver statement, Minimum relaxation factor, Maximum relaxation factor
NAN_CHECK nan_check_bool  ! Nan DEBUG statement
OVERWRITE_CHECK debug_statement     ! Overwrite DEBUG statement
EQSOLVER solver_equation           ! EQUATION SOLVER statement
TIME_REPORT time_report
CONSTANTS 3    
tStrtUser = START     ! START start time of user defined printer
tEndUser  = STOP      ! END time of user defined printer
dtPrUser  = dtSim     ! timestep of user defined printer
CONSTANTS 6 
versionDeck = 1 !can be changed from config file to adapt processes and so on
PI   = 3.1415926     
Zero = 0
Nix  = 0
notused  = 0
NPlotsPerSim = 18
CONSTANTS 7
CPBRI = 3.8160   ! spec. heat of Glycol  [kJ/kgK]; Value for an average pipe temperature with 55 �C Tyfocor LS
RHOBRI = 1016.0  ! density Glycol [kg/m�]; Value for an average pipe temperature with 55 �C Tyfocor L
CPWAT = 4.19     ! spec. heat of Water [kJ/kgK] at 20 �C
RHOWAT = 998.0   ! density of Water  [kg/m�] at20 �C
LAMWAT = 0.58    ! heat conductivity W/(mK)
CPWAT_SI = CPWAT*1000 ! J/(kgK)
CPBRI_SI = CPBRI*1000 ! J/(kgK)
CONSTANTS 1
warnError = 1
**********************************************************************
** ProDomo13-R410A.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\HP 
**********************************************************************
*********************************************
** BEGIN WWHp-ProDomo13 from CADENA SA
*********************************************
CONSTANTS 23
sizeHpRatio = 1 ! ask what this should be
TEvapMaxHp = 40
sizeHpNom = 12.5
MfrHpCondRef = 3000
MfrHpEvapRef = 2800
COPNom = 4.68 ! at B0W35
TEvapMax = 35
tCondMaxHp = 70
CHPM_c1 = sizeHpRatio*14.867741
CHPM_c2 = sizeHpRatio*127.470232
CHPM_c3 = sizeHpRatio*-13.745162
CHPM_c4 = sizeHpRatio*-216.501237
CHPM_c5 = sizeHpRatio*392.541582
CHPM_c6 = sizeHpRatio*-7.987489
COP_c1 = 12.410844
COP_c2 = 61.890885
COP_c3 = -83.489595
COP_c4 = -233.308680
COP_c5 = 103.074518
COP_c6 = 177.030077
TMinEvapTin = -8
TMinEvapTout = TMinEvapTin - 3
cpEvap = cpBri ! could be water not air
CONSTANTS 15
Moloss = 0
Ctherm = 4		!1
Ualoss = 0
frCOP = 1  ! hourlyPeakLoad/:sizeHpUsed csv/size
frCond = 1  ! depends on :sizeHpUsed
tauWPstart = 0
tauWPstop = 0
TWPEvapIce = -100
EtaDefrost = 0
PelWPVen = 0
PelAuxCtr_kW = 0
RHamb_1 = 0.5
tAmbHp = 15
timeHpBlock = 0                                !
tCondMinHp = 0
**********************************************************************
** QSnk_existing_HP.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk60 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
EQUATIONS 1
QSnk60unit = 17
 ASSIGN  ..\ddck\QSnk60\Profile_Snk_60_001.csv QSnk60unit
UNIT 11 TYPE 9       !Changed automatically
Parameters 10
5     ! 1 Mode
0     ! 2 Header Lines to Skip
1     ! 3 No. of values to read
1     ! 4 Time interval of data
1 1 0 0     ! 1st Data to read: 1: Interpolate (+) or not? (-); 2: Multiplication factor; 3: Addition factor; 4: average (0) or instantaneous (1)
QSnk60unit     ! 9 Logical unit for input file (used to be 18)
-1     ! 10 Free format mode
EQUATIONS 1
QSnk60P = MAX([11,1], 0)        !Changed automatically
EQUATIONS 1
QSnk60ThpEvapIn = TSCnr55_QSnk60
CONSTANTS 10
QSnk60h = 2 !m
QSnk60d = 1.5 !m
QSnk60n = 6
Qsnk60V=160.0 ! value changed from original by executeTrnsys.py
QSnk60U = 0.8e-3 ! kW/(m2.K)
QSnk60TInit = 37
QSnk60TMinCheck = 20
QSnk60topArea = QSnk60V/QSnk60h
QSnk60r = (QSnk60topArea/PI)^.5
QSnk60A = 2*PI*QSnk60r*QSnk60h + 2*QSnk60topArea
UNIT 12 TYPE 993 !Changed automatically
PARAMETERS 1
1
INPUTS 1
QSnk60T
QSnk60TInit
EQUATIONS 3
QSnk60TRecall = LE(TIME,1)*QSnk60TInit + GT(TIME,1)*[12,1] !Changed automatically
QSnk60TRecallCheck = GTWARN(QSnk60TMinCheck, QSnk60TRecall, warnError)
QSnk60TCheck = GTWARN(QSnk60TMinCheck, QSnk60T, warnError)
EQUATIONS 5
QSnk60T = (dtSim_SI*(QSnk60PauxCond_kW - QSnk60P + QSnk60U*QSnk60A*tAmbHp) + RHOWAT*CPWAT*QSnk60V*QSnk60TRecall)/(dtSim_SI*QSnk60U*QSnk60A + RHOWAT*CPWAT*QSnk60V) !CPWAT_SI???
QSnk60dP = (QSnk60PauxCond_kW - QSnk60P - QSnk60U*QSnk60A*(QSnk60T - tAmbHp)) !kW
QSnk60dQ = QSnk60dP*dtSim !kJ
QSnk60dTTank = QSnk60dQ/(RHOWAT*QSnk60V*CPWAT)
QSnk60dQlossTess = QSnk60U*QSnk60A*(QSnk60T - tAmbHp)
EQUATIONS 1
QSnk60qImbTess =  QSnk60PauxCond_kW - QSnk60dQ - QSnk60P - QSnk60dQlossTess
CONSTANTS 1
QSnk60unitPrintTess_EBal = 18
ASSIGN temp\ENERGY_BALANCE_MO_60_TESS.Prt QSnk60unitPrintTess_EBal 
UNIT 15 Type 46 !Changed automatically
PARAMETERS 6
QSnk60unitPrintTess_EBal !1: Logical unit number
-1 !2: for monthly summaries
1  !3: 1:print at absolute times
-1 !4 -1: monthly integration
1  !5 number of outputs to avoid integration
1  !6 output number to avoid integration
INPUTS 5
TIME QSnk60PauxCond_kW QSnk60dQ QSnk60P QSnk60dQlossTess QSnk60qImbTess
TIME QSnk60PauxCond_kW QSnk60dQ QSnk60P QSnk60dQlossTess QSnk60qImbTess
CONSTANTS 7
QSnk60dTAbove = 1
QSnk60dTBelow = 1
QSnk60TSet = 37
QSnk60TOff = QSnk60TSet + QSnk60dTAbove
QSnk60TOn = QSnk60TSet - QSnk60dTBelow
QSnk60frCondMin = 0.2
QSnk60frCondOn = 0.4
UNIT 13 TYPE 993 !Changed automatically
PARAMETERS 1
1
INPUTS 1
QSnk60myHpIsOn
0
EQUATIONS 1
QSnk60myHpIsOnRecall = [13,1] !Changed automatically
EQUATIONS 8
QSnk60below = LT(QSnk60TRecall, (QSnk60TSet - QSnk60dTBelow))
QSnk60above = GE(QSnk60TRecall, (QSnk60TSet + QSnk60dTAbove))
QSnk60between = NOT(QSnk60below)*NOT(QSnk60above)
QSnk60Tsignal = (QSnk60below + QSnk60between*QSnk60myHpIsOnRecall) * NOT(QSnk60above + QSnk60between*NOT(QSnk60myHpIsOnRecall))
QSnk60frCond = min(max(0.4, 1.2*QSnk60P/QSnk60sizeHpUsed), 1.2)
QSnk60CapSignal = GT(QSnk60frCond, QSnk60frCondMin)
QSnk60myHpIsOn = QSnk60Tsignal * QSnk60CapSignal
QSnk60myHpIsOnCheck = NEWARN(EQL(QSnk60myHpIsOn,0)+EQL(QSnk60myHpIsOn,1), 1, warnError)
EQUATIONS 1
QSnk60M = QSnk60MfrEvapIn
CONSTANTS 4		! Heat Pump: Size
Qsnk60sizeHpUsed=160.0 ! value changed from original by executeTrnsys.py
QSnk60SizeHpRatio = QSnk60sizeHpUsed/sizeHpNom
QSnk60MfrHpEvapNom = QSnk60SizeHpRatio*MfrHpEvapRef
QSnk60MfrHpCondNom = QSnk60SizeHpRatio*MfrHpCondRef		! adapt cond to corrected evap MfrHpEvapNom*ratioCondEvap
EQUATIONS 2
QSnk60MfrEvapIn = QSnk60MfrHpEvapNom * QSnk60frCond * QSnk60myHpIsOn
QSnk60MfrCondIn = QSnk60MfrHpCondNom * QSnk60frCond * QSnk60myHpIsOn
EQUATIONS 6
QSnk60CHPM_c1 = QSnk60sizeHpRatio*14.867741
QSnk60CHPM_c2 = QSnk60sizeHpRatio*127.470232
QSnk60CHPM_c3 = QSnk60sizeHpRatio*-13.745162
QSnk60CHPM_c4 = QSnk60sizeHpRatio*-216.501237
QSnk60CHPM_c5 = QSnk60sizeHpRatio*392.541582
QSnk60CHPM_c6 = QSnk60sizeHpRatio*-7.987489
UNIT 14 TYPE 977		 !Changed automatically
PARAMETERS 28
QSnk60CHPM_c1				! 1: c1
QSnk60CHPM_c2				! 2: c2
QSnk60CHPM_c3				! 3: c3
QSnk60CHPM_c4				! 4: c4
QSnk60CHPM_c5				! 5: c5
QSnk60CHPM_c6				! 6: c6
COP_c1				! 7: cop1
COP_c2				! 8: cop2
COP_c3				! 9: cop3
COP_c4				! 10: cop4
COP_c5				! 11: cop5
COP_c6				! 12: cop6
tauWPstart			! 13: tau_start, s
tauWPstop			! 14: tau_stop, s
TWPEvapIce			! 15: tevapIce, deg C
EtaDefrost			! 16: eta_defrost, -
PelWPVen			! 17: ventilator electricity consumption, kW
PelAuxCtr_kW		! 18: controller electricity consumption, kW
TminEvapTout		! 19: tevap,min, deg C
TEvapMaxHp			! 20: tevap,max, deg C
tCondMinHp			! 21: tcond,min, deg C
tCondMaxHp			! 22: tcond,max, deg C
CpEvap				! 23: cp,evap, kJ/kgK
CpWat				! 24: cp,cond, kJ/kgK
timeHpBlock         ! 25: tau_error, hr,
Moloss				! 26: 0-3
Ctherm				! 27: kJ/K
Ualoss				! 28: W/k
INPUTS 9
QSnk60ThpEvapIn		! 1: tevap,in, deg C
QSnk60MfrEvapIn		! 2: Mfr,evap,in, kg/h
QSnk60TRecall     		! 3: tcond,in, deg C
QSnk60MfrCondIn		! DC LET IS AS IT WAS BEFORE (CHECK) MfrHpCond		! 4: Mfr,cond,in, kg/h
QSnk60myHpIsOn		! 5: gamma_ON, -
RHamb_1			! 6: RH_air_in, RHamb_1
tAmbHp			! 7, tAmbHp
QSnk60frCond			! 8
frCOP			! 9
0  0  0  0  0  0.5 15 1 1
EQUATIONS 8		! Heat Pump: Outputs
QSnk60THpEvapOut = [14,1] !Changed automatically
QSnk60THpCondOut = [14,3]		 !Changed automatically
QSnk60MfrAuxOut = [14,4]  		 !Changed automatically
QSnk60PelAuxComp_kW = [14,5] 					 !Changed automatically
QSnk60PelAuxTot_kW = [14,6] 					 !Changed automatically
QSnk60PauxEvap_kW = [14,7] !Changed automatically
QSnk60PauxCond_kW = [14,8] 					 !Changed automatically
QSnk60COPhp = [14,9] !Changed automatically
EQUATIONS 1
TQSnk60 = QSnk60THpEvapOut
EQUATIONS 4
elSysIn_QSnk60HpComp = QSnk60PelAuxComp_kW
qSysOut_QSnk60Demand = QSnk60P
qSysOut_QSnk60TessLoss = QSnk60dQlossTess
qSysOut_QSnk60TessAcum = QSnk60dQ
EQUATIONS 1
QSnk60qImbHP =  QSnk60PauxEvap_kW + QSnk60PelAuxComp_kW - QSnk60PauxCond_kW
CONSTANTS 1
QSnk60unitPrintHP_EBal = 19
ASSIGN temp\ENERGY_BALANCE_MO_HP_60.Prt QSnk60unitPrintHP_EBal 
UNIT 16 Type 46 !Changed automatically
PARAMETERS 6
QSnk60unitPrintHP_EBal !1: Logical unit number
-1 !2: for monthly summaries
1  !3: 1:print at absolute times
-1 !4 -1: monthly integration
1  !5 number of outputs to avoid integration
1  !6 output number to avoid integration
INPUTS 4
TIME QSnk60PauxEvap_kW QSnk60PelAuxComp_kW QSnk60PauxCond_kW QSnk60qImbHP 
TIME QSnk60PauxEvap_kW QSnk60PelAuxComp_kW QSnk60PauxCond_kW QSnk60qImbHP
UNIT 10 TYPE 65       !Changed automatically
PARAMETERS 12
8  			! 1: Nb. of left-axis variables
3
-30   			! 3: Left axis minimum
60    		! 4: Left axis maximum
0 			! 5: Right axis minimum
1e3   		! 6: Right axis maximum
1 !nPlotsPerSim 	! 7: Number of plots per simulation
12    			! 8: X-axis gridpoints
1     			! 9: Shut off Online w/o removing
-1    			! 10: Logical unit for output file
0     			! 11: Output file units
0     			! 12: Output file delimiter
INPUTS 11
QSnk60ThpEvapIn QSnk60THpEvapOut  QSnk60T QSnk60TRecall QSnk60dTTank QSnk60THpCondOut QSnk60myHpIsOn QSnk60frCond QSnk60P QSnk60PauxCond_kW QSnk60dP
QSnk60ThpEvapIn QSnk60THpEvapOut  QSnk60T QSnk60TRecall QSnk60dTTank QSnk60THpCondOut QSnk60myHpIsOn QSnk60frCond QSnk60P QSnk60PauxCond_kW QSnk60dP
LABELS  3
Temperature
Mfr
HP60
**********************************************************************
** QSnk_existing_HP.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk85 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
EQUATIONS 1
QSnk85unit = 27
 ASSIGN  ..\ddck\QSnk85\Profile_Snk_85_001.csv QSnk85unit
UNIT 21 TYPE 9       !Changed automatically
Parameters 10
5     ! 1 Mode
0     ! 2 Header Lines to Skip
1     ! 3 No. of values to read
1     ! 4 Time interval of data
1 1 0 0     ! 1st Data to read: 1: Interpolate (+) or not? (-); 2: Multiplication factor; 3: Addition factor; 4: average (0) or instantaneous (1)
QSnk85unit     ! 9 Logical unit for input file (used to be 18)
-1     ! 10 Free format mode
EQUATIONS 1
QSnk85P = MAX([21,1], 0)        !Changed automatically
EQUATIONS 1
QSnk85ThpEvapIn = TSCnr16_QSnk85
CONSTANTS 10
QSnk85h = 2 !m
QSnk85d = 1.5 !m
QSnk85n = 6
Qsnk85V=300.0 ! value changed from original by executeTrnsys.py
QSnk85U = 0.8e-3 ! kW/(m2.K)
QSnk85TInit = 37
QSnk85TMinCheck = 20
QSnk85topArea = QSnk85V/QSnk85h
QSnk85r = (QSnk85topArea/PI)^.5
QSnk85A = 2*PI*QSnk85r*QSnk85h + 2*QSnk85topArea
UNIT 22 TYPE 993 !Changed automatically
PARAMETERS 1
1
INPUTS 1
QSnk85T
QSnk85TInit
EQUATIONS 3
QSnk85TRecall = LE(TIME,1)*QSnk85TInit + GT(TIME,1)*[22,1] !Changed automatically
QSnk85TRecallCheck = GTWARN(QSnk85TMinCheck, QSnk85TRecall, warnError)
QSnk85TCheck = GTWARN(QSnk85TMinCheck, QSnk85T, warnError)
EQUATIONS 5
QSnk85T = (dtSim_SI*(QSnk85PauxCond_kW - QSnk85P + QSnk85U*QSnk85A*tAmbHp) + RHOWAT*CPWAT*QSnk85V*QSnk85TRecall)/(dtSim_SI*QSnk85U*QSnk85A + RHOWAT*CPWAT*QSnk85V) !CPWAT_SI???
QSnk85dP = (QSnk85PauxCond_kW - QSnk85P - QSnk85U*QSnk85A*(QSnk85T - tAmbHp)) !kW
QSnk85dQ = QSnk85dP*dtSim !kJ
QSnk85dTTank = QSnk85dQ/(RHOWAT*QSnk85V*CPWAT)
QSnk85dQlossTess = QSnk85U*QSnk85A*(QSnk85T - tAmbHp)
EQUATIONS 1
QSnk85qImbTess =  QSnk85PauxCond_kW - QSnk85dQ - QSnk85P - QSnk85dQlossTess
CONSTANTS 1
QSnk85unitPrintTess_EBal = 28
ASSIGN temp\ENERGY_BALANCE_MO_85_TESS.Prt QSnk85unitPrintTess_EBal 
UNIT 25 Type 46 !Changed automatically
PARAMETERS 6
QSnk85unitPrintTess_EBal !1: Logical unit number
-1 !2: for monthly summaries
1  !3: 1:print at absolute times
-1 !4 -1: monthly integration
1  !5 number of outputs to avoid integration
1  !6 output number to avoid integration
INPUTS 5
TIME QSnk85PauxCond_kW QSnk85dQ QSnk85P QSnk85dQlossTess QSnk85qImbTess
TIME QSnk85PauxCond_kW QSnk85dQ QSnk85P QSnk85dQlossTess QSnk85qImbTess
CONSTANTS 7
QSnk85dTAbove = 1
QSnk85dTBelow = 1
QSnk85TSet = 37
QSnk85TOff = QSnk85TSet + QSnk85dTAbove
QSnk85TOn = QSnk85TSet - QSnk85dTBelow
QSnk85frCondMin = 0.2
QSnk85frCondOn = 0.4
UNIT 23 TYPE 993 !Changed automatically
PARAMETERS 1
1
INPUTS 1
QSnk85myHpIsOn
0
EQUATIONS 1
QSnk85myHpIsOnRecall = [23,1] !Changed automatically
EQUATIONS 8
QSnk85below = LT(QSnk85TRecall, (QSnk85TSet - QSnk85dTBelow))
QSnk85above = GE(QSnk85TRecall, (QSnk85TSet + QSnk85dTAbove))
QSnk85between = NOT(QSnk85below)*NOT(QSnk85above)
QSnk85Tsignal = (QSnk85below + QSnk85between*QSnk85myHpIsOnRecall) * NOT(QSnk85above + QSnk85between*NOT(QSnk85myHpIsOnRecall))
QSnk85frCond = min(max(0.4, 1.2*QSnk85P/QSnk85sizeHpUsed), 1.2)
QSnk85CapSignal = GT(QSnk85frCond, QSnk85frCondMin)
QSnk85myHpIsOn = QSnk85Tsignal * QSnk85CapSignal
QSnk85myHpIsOnCheck = NEWARN(EQL(QSnk85myHpIsOn,0)+EQL(QSnk85myHpIsOn,1), 1, warnError)
EQUATIONS 1
QSnk85M = QSnk85MfrEvapIn
CONSTANTS 4		! Heat Pump: Size
Qsnk85sizeHpUsed=600.0 ! value changed from original by executeTrnsys.py
QSnk85SizeHpRatio = QSnk85sizeHpUsed/sizeHpNom
QSnk85MfrHpEvapNom = QSnk85SizeHpRatio*MfrHpEvapRef
QSnk85MfrHpCondNom = QSnk85SizeHpRatio*MfrHpCondRef		! adapt cond to corrected evap MfrHpEvapNom*ratioCondEvap
EQUATIONS 2
QSnk85MfrEvapIn = QSnk85MfrHpEvapNom * QSnk85frCond * QSnk85myHpIsOn
QSnk85MfrCondIn = QSnk85MfrHpCondNom * QSnk85frCond * QSnk85myHpIsOn
EQUATIONS 6
QSnk85CHPM_c1 = QSnk85sizeHpRatio*14.867741
QSnk85CHPM_c2 = QSnk85sizeHpRatio*127.470232
QSnk85CHPM_c3 = QSnk85sizeHpRatio*-13.745162
QSnk85CHPM_c4 = QSnk85sizeHpRatio*-216.501237
QSnk85CHPM_c5 = QSnk85sizeHpRatio*392.541582
QSnk85CHPM_c6 = QSnk85sizeHpRatio*-7.987489
UNIT 24 TYPE 977		 !Changed automatically
PARAMETERS 28
QSnk85CHPM_c1				! 1: c1
QSnk85CHPM_c2				! 2: c2
QSnk85CHPM_c3				! 3: c3
QSnk85CHPM_c4				! 4: c4
QSnk85CHPM_c5				! 5: c5
QSnk85CHPM_c6				! 6: c6
COP_c1				! 7: cop1
COP_c2				! 8: cop2
COP_c3				! 9: cop3
COP_c4				! 10: cop4
COP_c5				! 11: cop5
COP_c6				! 12: cop6
tauWPstart			! 13: tau_start, s
tauWPstop			! 14: tau_stop, s
TWPEvapIce			! 15: tevapIce, deg C
EtaDefrost			! 16: eta_defrost, -
PelWPVen			! 17: ventilator electricity consumption, kW
PelAuxCtr_kW		! 18: controller electricity consumption, kW
TminEvapTout		! 19: tevap,min, deg C
TEvapMaxHp			! 20: tevap,max, deg C
tCondMinHp			! 21: tcond,min, deg C
tCondMaxHp			! 22: tcond,max, deg C
CpEvap				! 23: cp,evap, kJ/kgK
CpWat				! 24: cp,cond, kJ/kgK
timeHpBlock         ! 25: tau_error, hr,
Moloss				! 26: 0-3
Ctherm				! 27: kJ/K
Ualoss				! 28: W/k
INPUTS 9
QSnk85ThpEvapIn		! 1: tevap,in, deg C
QSnk85MfrEvapIn		! 2: Mfr,evap,in, kg/h
QSnk85TRecall     		! 3: tcond,in, deg C
QSnk85MfrCondIn		! DC LET IS AS IT WAS BEFORE (CHECK) MfrHpCond		! 4: Mfr,cond,in, kg/h
QSnk85myHpIsOn		! 5: gamma_ON, -
RHamb_1			! 6: RH_air_in, RHamb_1
tAmbHp			! 7, tAmbHp
QSnk85frCond			! 8
frCOP			! 9
0  0  0  0  0  0.5 15 1 1
EQUATIONS 8		! Heat Pump: Outputs
QSnk85THpEvapOut = [24,1] !Changed automatically
QSnk85THpCondOut = [24,3]		 !Changed automatically
QSnk85MfrAuxOut = [24,4]  		 !Changed automatically
QSnk85PelAuxComp_kW = [24,5] 					 !Changed automatically
QSnk85PelAuxTot_kW = [24,6] 					 !Changed automatically
QSnk85PauxEvap_kW = [24,7] !Changed automatically
QSnk85PauxCond_kW = [24,8] 					 !Changed automatically
QSnk85COPhp = [24,9] !Changed automatically
EQUATIONS 1
TQSnk85 = QSnk85THpEvapOut
EQUATIONS 4
elSysIn_Q_HpQSnk85 = QSnk85PelAuxComp_kW
qSysOut_QSnk85PD = QSnk85P
qSysOut_QSnk85_dQlossTess = QSnk85dQlossTess
qSysOut_QSnk85_dQacumTess = QSnk85dQ
EQUATIONS 1
QSnk85qImbHP =  QSnk85PauxEvap_kW + QSnk85PelAuxComp_kW - QSnk85PauxCond_kW
CONSTANTS 1
QSnk85unitPrintHP_EBal = 29
ASSIGN temp\ENERGY_BALANCE_MO_HP_85.Prt QSnk85unitPrintHP_EBal 
UNIT 26 Type 46 !Changed automatically
PARAMETERS 6
QSnk85unitPrintHP_EBal !1: Logical unit number
-1 !2: for monthly summaries
1  !3: 1:print at absolute times
-1 !4 -1: monthly integration
1  !5 number of outputs to avoid integration
1  !6 output number to avoid integration
INPUTS 4
TIME QSnk85PauxEvap_kW QSnk85PelAuxComp_kW QSnk85PauxCond_kW QSnk85qImbHP
TIME QSnk85PauxEvap_kW QSnk85PelAuxComp_kW QSnk85PauxCond_kW QSnk85qImbHP
UNIT 20 TYPE 65       !Changed automatically
PARAMETERS 12
8  			! 1: Nb. of left-axis variables
3
-30   			! 3: Left axis minimum
60    		! 4: Left axis maximum
0 			! 5: Right axis minimum
3e3   		! 6: Right axis maximum
1 !nPlotsPerSim 	! 7: Number of plots per simulation
12    			! 8: X-axis gridpoints
1     			! 9: Shut off Online w/o removing
-1    			! 10: Logical unit for output file
0     			! 11: Output file units
0     			! 12: Output file delimiter
INPUTS 11
QSnk85ThpEvapIn QSnk85THpEvapOut  QSnk85T QSnk85TRecall QSnk85dTTank QSnk85THpCondOut QSnk85myHpIsOn QSnk85frCond QSnk85P QSnk85PauxCond_kW QSnk85dP
QSnk85ThpEvapIn QSnk85THpEvapOut  QSnk85T QSnk85TRecall QSnk85dTTank QSnk85THpCondOut QSnk85myHpIsOn QSnk85frCond QSnk85P QSnk85PauxCond_kW QSnk85dP
LABELS  3
Temperature
Mfr
HP85
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk131 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk131dT = 0     ! [K]
QSnk131P = 0    ! Power of sink [kW]
QSnk131M = 0    !kg/h
EQUATIONS 1
QSnk131TIn = TSCnr126_QSnk131
EQUATIONS 2
QSnk131TOut = QSnk131Tin - QSnk131dT
TQSnk131 = QSnk131TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk183 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk183dT = 0     ! [K]
QSnk183P = 0    ! Power of sink [kW]
QSnk183M = 0    !kg/h
EQUATIONS 1
QSnk183TIn = TSCnr178_QSnk183
EQUATIONS 2
QSnk183TOut = QSnk183Tin - QSnk183dT
TQSnk183 = QSnk183TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk191 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk191dT = 0     ! [K]
QSnk191P = 0    ! Power of sink [kW]
QSnk191M = 0    !kg/h
EQUATIONS 1
QSnk191TIn = TSCnr200_QSnk191
EQUATIONS 2
QSnk191TOut = QSnk191Tin - QSnk191dT
TQSnk191 = QSnk191TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk225 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk225dT = 0     ! [K]
QSnk225P = 0    ! Power of sink [kW]
QSnk225M = 0    !kg/h
EQUATIONS 1
QSnk225TIn = TSCnr220_QSnk225
EQUATIONS 2
QSnk225TOut = QSnk225Tin - QSnk225dT
TQSnk225 = QSnk225TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk243 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk243dT = 0     ! [K]
QSnk243P = 0    ! Power of sink [kW]
QSnk243M = 0    !kg/h
EQUATIONS 1
QSnk243TIn = TSCnr238_QSnk243
EQUATIONS 2
QSnk243TOut = QSnk243Tin - QSnk243dT
TQSnk243 = QSnk243TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk266 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk266dT = 0     ! [K]
QSnk266P = 0    ! Power of sink [kW]
QSnk266M = 0    !kg/h
EQUATIONS 1
QSnk266TIn = TSCnr261_QSnk266
EQUATIONS 2
QSnk266TOut = QSnk266Tin - QSnk266dT
TQSnk266 = QSnk266TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk322 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk322dT = 0     ! [K]
QSnk322P = 0    ! Power of sink [kW]
QSnk322M = 0    !kg/h
EQUATIONS 1
QSnk322TIn = TSCnr363_QSnk322
EQUATIONS 2
QSnk322TOut = QSnk322Tin - QSnk322dT
TQSnk322 = QSnk322TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk335 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk335dT = 0     ! [K]
QSnk335P = 0    ! Power of sink [kW]
QSnk335M = 0    !kg/h
EQUATIONS 1
QSnk335TIn = TSCnr331_QSnk335
EQUATIONS 2
QSnk335TOut = QSnk335Tin - QSnk335dT
TQSnk335 = QSnk335TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk358 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk358dT = 0     ! [K]
QSnk358P = 0    ! Power of sink [kW]
QSnk358M = 0    !kg/h
EQUATIONS 1
QSnk358TIn = TSCnr353_QSnk358
EQUATIONS 2
QSnk358TOut = QSnk358Tin - QSnk358dT
TQSnk358 = QSnk358TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk375 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk375dT = 0     ! [K]
QSnk375P = 0    ! Power of sink [kW]
QSnk375M = 0    !kg/h
EQUATIONS 1
QSnk375TIn = TSCnr370_QSnk375
EQUATIONS 2
QSnk375TOut = QSnk375Tin - QSnk375dT
TQSnk375 = QSnk375TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk417 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk417dT = 0     ! [K]
QSnk417P = 0    ! Power of sink [kW]
QSnk417M = 0    !kg/h
EQUATIONS 1
QSnk417TIn = TSCnr412_QSnk417
EQUATIONS 2
QSnk417TOut = QSnk417Tin - QSnk417dT
TQSnk417 = QSnk417TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk448 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk448dT = 0     ! [K]
QSnk448P = 0    ! Power of sink [kW]
QSnk448M = 0    !kg/h
EQUATIONS 1
QSnk448TIn = TSCnr443_QSnk448
EQUATIONS 2
QSnk448TOut = QSnk448Tin - QSnk448dT
TQSnk448 = QSnk448TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk469 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk469dT = 0     ! [K]
QSnk469P = 0    ! Power of sink [kW]
QSnk469M = 0    !kg/h
EQUATIONS 1
QSnk469TIn = TSCnr464_QSnk469
EQUATIONS 2
QSnk469TOut = QSnk469Tin - QSnk469dT
TQSnk469 = QSnk469TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk488 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk488dT = 0     ! [K]
QSnk488P = 0    ! Power of sink [kW]
QSnk488M = 0    !kg/h
EQUATIONS 1
QSnk488TIn = TSCnr483_QSnk488
EQUATIONS 2
QSnk488TOut = QSnk488Tin - QSnk488dT
TQSnk488 = QSnk488TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk503 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk503dT = 0     ! [K]
QSnk503P = 0    ! Power of sink [kW]
QSnk503M = 0    !kg/h
EQUATIONS 1
QSnk503TIn = TSCnr498_QSnk503
EQUATIONS 2
QSnk503TOut = QSnk503Tin - QSnk503dT
TQSnk503 = QSnk503TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk524 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk524dT = 0     ! [K]
QSnk524P = 0    ! Power of sink [kW]
QSnk524M = 0    !kg/h
EQUATIONS 1
QSnk524TIn = TSCnr517_QSnk524
EQUATIONS 2
QSnk524TOut = QSnk524Tin - QSnk524dT
TQSnk524 = QSnk524TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk539 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk539dT = 0     ! [K]
QSnk539P = 0    ! Power of sink [kW]
QSnk539M = 0    !kg/h
EQUATIONS 1
QSnk539TIn = TSCnr534_QSnk539
EQUATIONS 2
QSnk539TOut = QSnk539Tin - QSnk539dT
TQSnk539 = QSnk539TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk558 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk558dT = 0     ! [K]
QSnk558P = 0    ! Power of sink [kW]
QSnk558M = 0    !kg/h
EQUATIONS 1
QSnk558TIn = TSCnr553_QSnk558
EQUATIONS 2
QSnk558TOut = QSnk558Tin - QSnk558dT
TQSnk558 = QSnk558TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk579 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk579dT = 0     ! [K]
QSnk579P = 0    ! Power of sink [kW]
QSnk579M = 0    !kg/h
EQUATIONS 1
QSnk579TIn = TSCnr571_QSnk579
EQUATIONS 2
QSnk579TOut = QSnk579Tin - QSnk579dT
TQSnk579 = QSnk579TOut
**********************************************************************
** QSnk_off.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSnk586 
**********************************************************************
*******************************
**BEGIN sink.ddck
*******************************
CONSTANTS 3
QSnk586dT = 0     ! [K]
QSnk586P = 0    ! Power of sink [kW]
QSnk586M = 0    !kg/h
EQUATIONS 1
QSnk586TIn = TSCnr567_QSnk586
EQUATIONS 2
QSnk586TOut = QSnk586Tin - QSnk586dT
TQSnk586 = QSnk586TOut
**********************************************************************
** QSrc.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\QSrc1 
**********************************************************************
*******************************
**BEGIN source.ddck
*******************************
CONSTANTS 4
QSrc1TOut = 15
QSrc1dTNom = 7
QSrc1MNom = 2500*60*1e-3*998 ! kg*h
QSrc1PNom = CPWAT_SI*QSrc1MNom*QSrc1dTNom
EQUATIONS 1
QSrc1TIn = THxSrc_QSrc1
EQUATIONS 1
TQSrc1 = QSrc1TOut
EQUATIONS 4
dT = QSrc1TOut - QSrc1TIn
QSrc1M = MfrQSrc1
QSrc1P = QSrc1M*CPWAT*dT/3600
qSysIn_Src = QSrc1P
ASSIGN temp\TRL_Stunden.Prt 654 
UNIT 30 Type 46 !Changed automatically
PARAMETERS 7
654 !1: Logical unit number
-1 !2: for monthly summaries
1  !3: 1:print at absolute times
1 !4 1: hourly integration
2  !5 number of outputs to avoid integration
1 2 !6 output number to avoid integration
INPUTS 2
TIME QSrc1TIn
TIME TInQSrc1
**********************************************************************
** hydraulic_control_with_HP.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\control 
**********************************************************************
*************************************
**BEGIN hydraulic_control.ddck
*************************************
EQUATIONS 22
MfrQSnk60 = QSnk60M
MfrQSnk85 = QSnk85M
MfrQSnk131 = QSnk131M
MfrQSnk183 = QSnk183M
MfrQSnk191 = QSnk191M
MfrQSnk225 = QSnk225M
MfrQSnk243 = QSnk243M
MfrQSnk266 = QSnk266M
MfrQSnk322 = QSnk322M
MfrQSnk335 = QSnk335M
MfrQSnk358 = QSnk358M
MfrQSnk375 = QSnk375M
MfrQSnk417 = QSnk417M
MfrQSnk448 = QSnk448M
MfrQSnk469 = QSnk469M
MfrQSnk488 = QSnk488M
MfrQSnk503 = QSnk503M
MfrQSnk524 = QSnk524M
MfrQSnk539 = QSnk539M
MfrQSnk558 = QSnk558M
MfrQSnk579 = QSnk579M
MfrQSnk586 = QSnk586M
EQUATIONS 3
QSrc1dT = QSrc1TOut - QSrc1TIn
MfrQSrc1 = QSnk60M + QSnk85M + QSnk131M + QSnk183M + QSnk191M + QSnk225M + QSnk243M + QSnk266M + QSnk322M + QSnk335M + QSnk358M + QSnk375M + QSnk417M + QSnk448M + QSnk469M + QSnk488M + QSnk503M + QSnk524M + QSnk539M + QSnk558M + QSnk579M + QSnk586M
QSrc1P = MfrQSrc1*CPBRI*QSrc1dT/3600
CONSTANTS 3
TambAvg = 10
DTAmbAmpl = 15
ddTcwOffset = 0
**********************************************************************
** hydraulic_existing.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\hydraulic 
**********************************************************************
*************************************
** BEGIN hydraulic.ddck
*************************************
EQUATIONS 3
qSysOut_dpToFFieldTot = dpToFFieldTot
qSysOut_dpPipeIntTot = dpPipeIntTot
qSysOut_dpSoilIntTot = dpSoilIntTot
EQUATIONS 23
TQSrc1H=TQSrc1
TQSnk60H=TQSnk60
TQSnk85H=TQSnk85
TQSnk131H=TQSnk131
TQSnk183H=TQSnk183
TQSnk191H=TQSnk191
TQSnk225H=TQSnk225
TQSnk243H=TQSnk243
TQSnk266H=TQSnk266
TQSnk322H=TQSnk322
TQSnk335H=TQSnk335
TQSnk358H=TQSnk358
TQSnk375H=TQSnk375
TQSnk417H=TQSnk417
TQSnk448H=TQSnk448
TQSnk469H=TQSnk469
TQSnk488H=TQSnk488
TQSnk503H=TQSnk503
TQSnk524H=TQSnk524
TQSnk539H=TQSnk539
TQSnk558H=TQSnk558
TQSnk579H=TQSnk579
TQSnk586H=TQSnk586
CONSTANTS 25
dpLength = 579.404 ! Length of buried pipe in m
dpDiamIn = 0.4028 ! Inner diameter of pipes in m
dpDiamOut = 0.429 ! Outer diameter of pipes in m
dpLambda = 175 ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth = 1.8 ! Buried pipe depth in m
dpDiamCase = 2 ! Diameter of casing material in m
dpLambdaFill = 7  ! Thermal conductivity of fill insulation in kJ/hr.m.K
dpDistPtoP = 0.55  ! Center-to-center pipe spacing in m
dpLambdaGap = 1.44  ! Thermal conductivity of gap material in kJ/hr.m.K (gravel)
dpGapThick = 0  ! Gap thickness in m
dpRhoFlu=1016.0 ! value changed from original by executeTrnsys.py
dpLambdaFl = LamWat*3.6  ! Thermal conductivity of fluid in kJ/hr.m.K
dpCpFl=3.8160 ! value changed from original by executeTrnsys.py
dpViscFl = 3.078  ! Viscosity of fluid in kg/m.hr
dpTIniHot = 15  ! Initial fluid temperature - pipe 1 in degrees celsius
dpTIniCold  = 10  ! Initial fluid temperature - pipe 2 in degrees celsius
dpLamdaSl = 8.64  ! Thermal conductivity of soil in kJ/hr.m.K
dpRhoSl = 1800  ! Density of soil in kg/m^3
dpCpSl = 1.0  ! Specific heat of soil in kJ/kg.K
dpNrFlNds = 60  ! Number of fluid nodes
dpNrSlRad = 10  ! Number of radial soil nodes
dpSoilThickness = 0.5  ! Thickness of soil around the gravel considered in the model in m
dpRadNdDist = dpSoilThickness/dpNrSlRad ! Radial distance of any node in m
dpNrSlAx = 20  ! Number of axial soil nodes
dpNrSlCirc = 4  ! Number of circumferential soil nodes
UNIT 31 TYPE 9352 !Changed automatically
PARAMETERS 1168
mfrSolverAbsTol
mfrSolverRelTol
mfrTolSwitchThreshold
291
43 44 0 1      !1 : QSrc1
10 43 0 0      !2 : SCnr4Cold
44 11 0 0      !3 : SCnr4Hot
12 53 33 2     !4 : DTee10Cold
13 54 34 2     !5 : DTee10Hot
33 50 0 0      !6 : SCnr16Cold
49 34 0 0      !7 : SCnr16Hot
12 10 0 0      !8 : DCnr20Cold
11 13 0 0      !9 : DCnr20Hot
8 2 0 0        !10 : TS_ACold
3 9 0 0        !11 : TS_AHot
4 8 0 0        !12 : TS_BCold
9 5 0 0        !13 : TS_BHot
29 55 18 2     !14 : DTee50Cold
30 56 19 2     !15 : DTee50Hot
18 46 0 0      !16 : SCnr55Cold
45 19 0 0      !17 : SCnr55Hot
16 14 0 0      !18 : Seitenarm_IICold
15 17 0 0      !19 : Seitenarm_IIHot
45 46 0 1      !20 : QSnk60
29 67 0 0      !21 : DCnr65Cold
68 30 0 0      !22 : DCnr65Hot
69 31 0 0      !23 : DCnr68Cold
32 70 0 0      !24 : DCnr68Hot
31 36 0 0      !25 : DCnr71Cold
37 32 0 0      !26 : DCnr71Hot
36 113 0 0     !27 : DCnr74Cold
114 37 0 0     !28 : DCnr74Hot
21 14 0 0      !29 : TS_D_1Cold
15 22 0 0      !30 : TS_D_1Hot
25 23 0 0      !31 : TS_ECold
24 26 0 0      !32 : TS_EHot
6 4 0 0        !33 : Seitenarm_ICold
5 7 0 0        !34 : Seitenarm_IHot
49 50 0 1      !35 : QSnk85
27 25 0 0      !36 : TS_FCold
26 28 0 0      !37 : TS_FHot
77 173 0 0     !38 : DCnr110Cold
174 78 0 0     !39 : DCnr110Hot
162 48 0 0     !40 : SCnr126Cold
47 163 0 0     !41 : SCnr126Hot
47 48 0 1      !42 : QSnk131
2 1 0 0        !43 : SCnr4_QSrc1
1 3 0 0        !44 : QSrc1_SCnr4
17 20 0 0      !45 : SCnr55_QSnk60
20 16 0 0      !46 : QSnk60_SCnr55
41 42 0 0      !47 : SCnr126_QSnk131
42 40 0 0      !48 : QSnk131_SCnr126
7 35 0 0       !49 : SCnr16_QSnk85
35 6 0 0       !50 : QSnk85_SCnr16
55 53 59 2     !51 : DTee172Cold
56 54 60 2     !52 : DTee172Hot
51 4 0 0       !53 : TS_C_1Cold
5 52 0 0       !54 : TS_C_1Hot
14 51 0 0      !55 : TS_C_2Cold
52 15 0 0      !56 : TS_C_2Hot
59 63 0 0      !57 : SCnr178Cold
62 60 0 0      !58 : SCnr178Hot
57 51 0 0      !59 : TS_C_SNK_pipeCold
52 58 0 0      !60 : TS_C_SNK_pipeHot
62 63 0 1      !61 : QSnk183
58 61 0 0      !62 : SCnr178_QSnk183
61 57 0 0      !63 : QSnk183_SCnr178
102 103 0 1    !64 : QSnk191
67 69 73 2     !65 : DTee194Cold
68 70 74 2     !66 : DTee194Hot
65 21 0 0      !67 : TS_D_2_1Cold
22 66 0 0      !68 : TS_D_2_1Hot
23 65 0 0      !69 : TS_D_2_2Cold
66 24 0 0      !70 : TS_D_2_2Hot
73 103 0 0     !71 : SCnr200Cold
102 74 0 0     !72 : SCnr200Hot
71 65 0 0      !73 : TS_D_2_SNK_pipeCold
66 72 0 0      !74 : TS_D_2_SNK_pipeHot
115 77 81 2    !75 : DTee213Cold
116 78 82 2    !76 : DTee213Hot
75 38 0 0      !77 : TS_H_2Cold
39 76 0 0      !78 : TS_H_2Hot
81 105 0 0     !79 : SCnr220Cold
104 82 0 0     !80 : SCnr220Hot
79 75 0 0      !81 : TS_H_SNK_pipeCold
76 80 0 0      !82 : TS_H_SNK_pipeHot
104 105 0 1    !83 : QSnk225
95 160 88 2    !84 : DTee232Cold
96 161 89 2    !85 : DTee232Hot
88 92 0 0      !86 : SCnr238Cold
91 89 0 0      !87 : SCnr238Hot
86 84 0 0      !88 : TS_K_SNK_pipeCold
85 87 0 0      !89 : TS_K_SNK_pipeHot
91 92 0 1      !90 : QSnk243
87 90 0 0      !91 : SCnr238_QSnk243
90 86 0 0      !92 : QSnk243_SCnr238
175 95 99 2    !93 : DTee253Cold
176 96 100 2   !94 : DTee253Hot
93 84 0 0      !95 : TS_K_1Cold
85 94 0 0      !96 : TS_K_1Hot
99 107 0 0     !97 : SCnr261Cold
106 100 0 0    !98 : SCnr261Hot
97 93 0 0      !99 : Seitenarm_VICold
94 98 0 0      !100 : Seitenarm_VIHot
106 107 0 1    !101 : QSnk266
72 64 0 0      !102 : SCnr200_QSnk191
64 71 0 0      !103 : QSnk191_SCnr200
80 83 0 0      !104 : SCnr220_QSnk225
83 79 0 0      !105 : QSnk225_SCnr220
98 101 0 0     !106 : SCnr261_QSnk266
101 97 0 0     !107 : QSnk266_SCnr261
115 113 122 2  !108 : DTee315Cold
116 114 123 2  !109 : DTee315Hot
132 126 0 0    !110 : DCnr319Cold
127 133 0 0    !111 : DCnr319Hot
152 153 0 1    !112 : QSnk322
108 27 0 0     !113 : TS_GCold
28 109 0 0     !114 : TS_GHot
75 108 0 0     !115 : TS_H_1Cold
109 76 0 0     !116 : TS_H_1Hot
126 122 124 2  !117 : DTee327Cold
127 123 125 2  !118 : DTee327Hot
124 149 0 0    !119 : SCnr331Cold
148 125 0 0    !120 : SCnr331Hot
148 149 0 1    !121 : QSnk335
117 108 0 0    !122 : Seitenarm_IV_absch_1_1Cold
109 118 0 0    !123 : Seitenarm_IV_absch_1_1Hot
119 117 0 0    !124 : Seitenarm_IV_absch_1_SNKCold
118 120 0 0    !125 : Seitenarm_IV_absch_1_SNKHot
110 117 0 0    !126 : Seitenarm_IV_absch_1_2Cold
118 111 0 0    !127 : Seitenarm_IV_absch_1_2Hot
141 145 134 2  !128 : DTee343Cold
142 146 135 2  !129 : DTee343Hot
132 134 156 2  !130 : DTee347Cold
133 135 157 2  !131 : DTee347Hot
130 110 0 0    !132 : Seitenarm_IV_absch_2_1Cold
111 131 0 0    !133 : Seitenarm_IV_absch_2_1Hot
128 130 0 0    !134 : Seitenarm_IV_absch_2_2Cold
131 129 0 0    !135 : Seitenarm_IV_absch_2_2Hot
156 151 0 0    !136 : SCnr353Cold
150 157 0 0    !137 : SCnr353Hot
150 151 0 1    !138 : QSnk358
141 153 0 0    !139 : SCnr363Cold
152 142 0 0    !140 : SCnr363Hot
139 128 0 0    !141 : Seitenarm_IV_absch_3_RCold
129 140 0 0    !142 : Seitenarm_IV_absch_3_RHot
145 155 0 0    !143 : SCnr370Cold
154 146 0 0    !144 : SCnr370Hot
143 128 0 0    !145 : Seitenarm_IV_absch_3_LCold
129 144 0 0    !146 : Seitenarm_IV_absch_3_LHot
154 155 0 1    !147 : QSnk375
120 121 0 0    !148 : SCnr331_QSnk335
121 119 0 0    !149 : QSnk335_SCnr331
137 138 0 0    !150 : SCnr353_QSnk358
138 136 0 0    !151 : QSnk358_SCnr353
140 112 0 0    !152 : SCnr363_QSnk322
112 139 0 0    !153 : QSnk322_SCnr363
144 147 0 0    !154 : SCnr370_QSnk375
147 143 0 0    !155 : QSnk375_SCnr370
136 130 0 0    !156 : Seitenarm_IV_absch_2_SNKCold
131 137 0 0    !157 : Seitenarm_IV_absch_2_SNKHot
162 160 166 2  !158 : DTee405Cold
163 161 167 2  !159 : DTee405Hot
158 84 0 0     !160 : TS_K_2Cold
85 159 0 0     !161 : TS_K_2Hot
40 158 0 0     !162 : Seitenarm_VIIICold
159 41 0 0     !163 : Seitenarm_VIIIHot
166 170 0 0    !164 : SCnr412Cold
169 167 0 0    !165 : SCnr412Hot
164 158 0 0    !166 : Seitenarm_VIICold
159 165 0 0    !167 : Seitenarm_VIIHot
169 170 0 1    !168 : QSnk417
165 168 0 0    !169 : SCnr412_QSnk417
168 164 0 0    !170 : QSnk417_SCnr412
175 173 179 2  !171 : DTee424Cold
176 174 180 2  !172 : DTee424Hot
171 38 0 0     !173 : TS_ICold
39 172 0 0     !174 : TS_IHot
93 171 0 0     !175 : TS_JCold
172 94 0 0     !176 : TS_JHot
179 183 0 0    !177 : DCnr430Cold
184 180 0 0    !178 : DCnr430Hot
177 171 0 0    !179 : Seitenarm_V_1_1Cold
172 178 0 0    !180 : Seitenarm_V_1_1Hot
183 187 191 2  !181 : DTee434Cold
184 188 192 2  !182 : DTee434Hot
181 177 0 0    !183 : Seitenarm_V_1_2_1Cold
178 182 0 0    !184 : Seitenarm_V_1_2_1Hot
200 187 0 0    !185 : DCnr439Cold
188 201 0 0    !186 : DCnr439Hot
185 181 0 0    !187 : Seitenarm_V_1_2_2Cold
182 186 0 0    !188 : Seitenarm_V_1_2_2Hot
191 195 0 0    !189 : SCnr443Cold
194 192 0 0    !190 : SCnr443Hot
189 181 0 0    !191 : Seitenarm_V_1_2_SNKCold
182 190 0 0    !192 : Seitenarm_V_1_2_SNKHot
194 195 0 1    !193 : QSnk448
190 193 0 0    !194 : SCnr443_QSnk448
193 189 0 0    !195 : QSnk448_SCnr443
202 200 206 2  !196 : DTee455Cold
203 201 207 2  !197 : DTee455Hot
202 213 0 0    !198 : DCnr459Cold
214 203 0 0    !199 : DCnr459Hot
196 185 0 0    !200 : Seitenarm_V_2_1Cold
186 197 0 0    !201 : Seitenarm_V_2_1Hot
198 196 0 0    !202 : Seitenarm_V_2_2Cold
197 199 0 0    !203 : Seitenarm_V_2_2Hot
206 210 0 0    !204 : SCnr464Cold
209 207 0 0    !205 : SCnr464Hot
204 196 0 0    !206 : Seitenarm_V_2_SNKCold
197 205 0 0    !207 : Seitenarm_V_2_SNKHot
209 210 0 1    !208 : QSnk469
205 208 0 0    !209 : SCnr464_QSnk469
208 204 0 0    !210 : QSnk469_SCnr464
213 217 221 2  !211 : DTee474Cold
214 218 222 2  !212 : DTee474Hot
211 198 0 0    !213 : Seitenarm_V_3_1Cold
199 212 0 0    !214 : Seitenarm_V_3_1Hot
217 228 0 0    !215 : DCnr479Cold
229 218 0 0    !216 : DCnr479Hot
215 211 0 0    !217 : Seitenarm_V_3_2Cold
212 216 0 0    !218 : Seitenarm_V_3_2Hot
221 225 0 0    !219 : SCnr483Cold
224 222 0 0    !220 : SCnr483Hot
219 211 0 0    !221 : Seitenarm_V_3_SNKCold
212 220 0 0    !222 : Seitenarm_V_3_SNKHot
224 225 0 1    !223 : QSnk488
220 223 0 0    !224 : SCnr483_QSnk488
223 219 0 0    !225 : QSnk488_SCnr483
228 241 232 2  !226 : DTee493Cold
229 242 233 2  !227 : DTee493Hot
226 215 0 0    !228 : Seitenarm_V_4_1Cold
216 227 0 0    !229 : Seitenarm_V_4_1Hot
232 236 0 0    !230 : SCnr498Cold
235 233 0 0    !231 : SCnr498Hot
230 226 0 0    !232 : U_1Cold
227 231 0 0    !233 : U_1Hot
235 236 0 1    !234 : QSnk503
231 234 0 0    !235 : SCnr498_QSnk503
234 230 0 0    !236 : QSnk503_SCnr498
283 290 285 2  !237 : DTee508Cold
284 291 286 2  !238 : DTee508Hot
241 252 245 2  !239 : DTee512Cold
242 253 246 2  !240 : DTee512Hot
239 226 0 0    !241 : DTee493_DTee512Cold
227 240 0 0    !242 : DTee493_DTee512Hot
245 249 0 0    !243 : SCnr517Cold
248 246 0 0    !244 : SCnr517Hot
243 239 0 0    !245 : U_2Cold
240 244 0 0    !246 : U_2Hot
248 249 0 1    !247 : QSnk524
244 247 0 0    !248 : SCnr517_QSnk524
247 243 0 0    !249 : QSnk524_SCnr517
263 252 256 2  !250 : DTee529Cold
264 253 257 2  !251 : DTee529Hot
250 239 0 0    !252 : Seitenarm_V_4_2Cold
240 251 0 0    !253 : Seitenarm_V_4_2Hot
256 260 0 0    !254 : SCnr534Cold
259 257 0 0    !255 : SCnr534Hot
254 250 0 0    !256 : Seitenarm_V_4_SNKCold
251 255 0 0    !257 : Seitenarm_V_4_SNKHot
259 260 0 1    !258 : QSnk539
255 258 0 0    !259 : SCnr534_QSnk539
258 254 0 0    !260 : QSnk539_SCnr534
267 263 0 0    !261 : DCnr544Cold
264 268 0 0    !262 : DCnr544Hot
261 250 0 0    !263 : Seitenarm_V_4_3Cold
251 262 0 0    !264 : Seitenarm_V_4_3Hot
267 283 271 2  !265 : DTee548Cold
268 284 272 2  !266 : DTee548Hot
265 261 0 0    !267 : Seitenarm_V_5_1Cold
262 266 0 0    !268 : Seitenarm_V_5_1Hot
271 275 0 0    !269 : SCnr553Cold
274 272 0 0    !270 : SCnr553Hot
269 265 0 0    !271 : Seitenarm_V_5_SNKCold
266 270 0 0    !272 : Seitenarm_V_5_SNKHot
274 275 0 1    !273 : QSnk558
270 273 0 0    !274 : SCnr553_QSnk558
273 269 0 0    !275 : QSnk558_SCnr553
285 289 0 0    !276 : SCnr567Cold
288 286 0 0    !277 : SCnr567Hot
290 282 0 0    !278 : SCnr571Cold
281 291 0 0    !279 : SCnr571Hot
281 282 0 1    !280 : QSnk579
279 280 0 0    !281 : SCnr571_QSnk579
280 278 0 0    !282 : QSnk579_SCnr571
237 265 0 0    !283 : Seitenarm_V_5_2Cold
266 238 0 0    !284 : Seitenarm_V_5_2Hot
276 237 0 0    !285 : U_3Cold
238 277 0 0    !286 : U_3Hot
288 289 0 1    !287 : QSnk586
277 287 0 0    !288 : SCnr567_QSnk586
287 276 0 0    !289 : QSnk586_SCnr567
278 237 0 0    !290 : Seitenarm_V_6Cold
238 279 0 0    !291 : Seitenarm_V_6Hot
INPUTS 291! for Type 9352
MfrQSrc1 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk60 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 MfrQSnk85 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk131 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk183 0,0 
0,0 MfrQSnk191 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
MfrQSnk225 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk243 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk266 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk322 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk335 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 MfrQSnk358 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 MfrQSnk375 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 MfrQSnk417 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk448 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
MfrQSnk469 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 MfrQSnk488 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 MfrQSnk503 0,0 0,0 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk524 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk539 0,0 0,0 0,0 0,0 
0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 
MfrQSnk558 0,0 0,0 0,0 0,0 0,0 0,0 MfrQSnk579 0,0 0,0 
0,0 0,0 0,0 0,0 MfrQSnk586 0,0 0,0 0,0 0,0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 0 0 0 0 0 0 0 0 0 
0 
EQUATIONS 624	! Output up to three (A,B,C) mass flow rates of each component, positive = input/inlet, negative = output/outlet 
MQSrc1_A=[31,1] !Changed automatically
MQSrc1_B=[31,2] !Changed automatically
MSCnr4Cold_A=[31,4] !Changed automatically
MSCnr4Cold_B=[31,5] !Changed automatically
MSCnr4Hot_A=[31,7] !Changed automatically
MSCnr4Hot_B=[31,8] !Changed automatically
MDTee10Cold_A=[31,10] !Changed automatically
MDTee10Cold_B=[31,11] !Changed automatically
MDTee10Cold_C=[31,12] !Changed automatically
MDTee10Hot_A=[31,13] !Changed automatically
MDTee10Hot_B=[31,14] !Changed automatically
MDTee10Hot_C=[31,15] !Changed automatically
MSCnr16Cold_A=[31,16] !Changed automatically
MSCnr16Cold_B=[31,17] !Changed automatically
MSCnr16Hot_A=[31,19] !Changed automatically
MSCnr16Hot_B=[31,20] !Changed automatically
MDCnr20Cold_A=[31,22] !Changed automatically
MDCnr20Cold_B=[31,23] !Changed automatically
MDCnr20Hot_A=[31,25] !Changed automatically
MDCnr20Hot_B=[31,26] !Changed automatically
MTS_ACold_A=[31,28] !Changed automatically
MTS_ACold_B=[31,29] !Changed automatically
MTS_AHot_A=[31,31] !Changed automatically
MTS_AHot_B=[31,32] !Changed automatically
MTS_BCold_A=[31,34] !Changed automatically
MTS_BCold_B=[31,35] !Changed automatically
MTS_BHot_A=[31,37] !Changed automatically
MTS_BHot_B=[31,38] !Changed automatically
MDTee50Cold_A=[31,40] !Changed automatically
MDTee50Cold_B=[31,41] !Changed automatically
MDTee50Cold_C=[31,42] !Changed automatically
MDTee50Hot_A=[31,43] !Changed automatically
MDTee50Hot_B=[31,44] !Changed automatically
MDTee50Hot_C=[31,45] !Changed automatically
MSCnr55Cold_A=[31,46] !Changed automatically
MSCnr55Cold_B=[31,47] !Changed automatically
MSCnr55Hot_A=[31,49] !Changed automatically
MSCnr55Hot_B=[31,50] !Changed automatically
MSeitenarm_IICold_A=[31,52] !Changed automatically
MSeitenarm_IICold_B=[31,53] !Changed automatically
MSeitenarm_IIHot_A=[31,55] !Changed automatically
MSeitenarm_IIHot_B=[31,56] !Changed automatically
MQSnk60_A=[31,58] !Changed automatically
MQSnk60_B=[31,59] !Changed automatically
MDCnr65Cold_A=[31,61] !Changed automatically
MDCnr65Cold_B=[31,62] !Changed automatically
MDCnr65Hot_A=[31,64] !Changed automatically
MDCnr65Hot_B=[31,65] !Changed automatically
MDCnr68Cold_A=[31,67] !Changed automatically
MDCnr68Cold_B=[31,68] !Changed automatically
MDCnr68Hot_A=[31,70] !Changed automatically
MDCnr68Hot_B=[31,71] !Changed automatically
MDCnr71Cold_A=[31,73] !Changed automatically
MDCnr71Cold_B=[31,74] !Changed automatically
MDCnr71Hot_A=[31,76] !Changed automatically
MDCnr71Hot_B=[31,77] !Changed automatically
MDCnr74Cold_A=[31,79] !Changed automatically
MDCnr74Cold_B=[31,80] !Changed automatically
MDCnr74Hot_A=[31,82] !Changed automatically
MDCnr74Hot_B=[31,83] !Changed automatically
MTS_D_1Cold_A=[31,85] !Changed automatically
MTS_D_1Cold_B=[31,86] !Changed automatically
MTS_D_1Hot_A=[31,88] !Changed automatically
MTS_D_1Hot_B=[31,89] !Changed automatically
MTS_ECold_A=[31,91] !Changed automatically
MTS_ECold_B=[31,92] !Changed automatically
MTS_EHot_A=[31,94] !Changed automatically
MTS_EHot_B=[31,95] !Changed automatically
MSeitenarm_ICold_A=[31,97] !Changed automatically
MSeitenarm_ICold_B=[31,98] !Changed automatically
MSeitenarm_IHot_A=[31,100] !Changed automatically
MSeitenarm_IHot_B=[31,101] !Changed automatically
MQSnk85_A=[31,103] !Changed automatically
MQSnk85_B=[31,104] !Changed automatically
MTS_FCold_A=[31,106] !Changed automatically
MTS_FCold_B=[31,107] !Changed automatically
MTS_FHot_A=[31,109] !Changed automatically
MTS_FHot_B=[31,110] !Changed automatically
MDCnr110Cold_A=[31,112] !Changed automatically
MDCnr110Cold_B=[31,113] !Changed automatically
MDCnr110Hot_A=[31,115] !Changed automatically
MDCnr110Hot_B=[31,116] !Changed automatically
MSCnr126Cold_A=[31,118] !Changed automatically
MSCnr126Cold_B=[31,119] !Changed automatically
MSCnr126Hot_A=[31,121] !Changed automatically
MSCnr126Hot_B=[31,122] !Changed automatically
MQSnk131_A=[31,124] !Changed automatically
MQSnk131_B=[31,125] !Changed automatically
MSCnr4_QSrc1_A=[31,127] !Changed automatically
MSCnr4_QSrc1_B=[31,128] !Changed automatically
MQSrc1_SCnr4_A=[31,130] !Changed automatically
MQSrc1_SCnr4_B=[31,131] !Changed automatically
MSCnr55_QSnk60_A=[31,133] !Changed automatically
MSCnr55_QSnk60_B=[31,134] !Changed automatically
MQSnk60_SCnr55_A=[31,136] !Changed automatically
MQSnk60_SCnr55_B=[31,137] !Changed automatically
MSCnr126_QSnk131_A=[31,139] !Changed automatically
MSCnr126_QSnk131_B=[31,140] !Changed automatically
MQSnk131_SCnr126_A=[31,142] !Changed automatically
MQSnk131_SCnr126_B=[31,143] !Changed automatically
MSCnr16_QSnk85_A=[31,145] !Changed automatically
MSCnr16_QSnk85_B=[31,146] !Changed automatically
MQSnk85_SCnr16_A=[31,148] !Changed automatically
MQSnk85_SCnr16_B=[31,149] !Changed automatically
MDTee172Cold_A=[31,151] !Changed automatically
MDTee172Cold_B=[31,152] !Changed automatically
MDTee172Cold_C=[31,153] !Changed automatically
MDTee172Hot_A=[31,154] !Changed automatically
MDTee172Hot_B=[31,155] !Changed automatically
MDTee172Hot_C=[31,156] !Changed automatically
MTS_C_1Cold_A=[31,157] !Changed automatically
MTS_C_1Cold_B=[31,158] !Changed automatically
MTS_C_1Hot_A=[31,160] !Changed automatically
MTS_C_1Hot_B=[31,161] !Changed automatically
MTS_C_2Cold_A=[31,163] !Changed automatically
MTS_C_2Cold_B=[31,164] !Changed automatically
MTS_C_2Hot_A=[31,166] !Changed automatically
MTS_C_2Hot_B=[31,167] !Changed automatically
MSCnr178Cold_A=[31,169] !Changed automatically
MSCnr178Cold_B=[31,170] !Changed automatically
MSCnr178Hot_A=[31,172] !Changed automatically
MSCnr178Hot_B=[31,173] !Changed automatically
MTS_C_SNK_pipeCold_A=[31,175] !Changed automatically
MTS_C_SNK_pipeCold_B=[31,176] !Changed automatically
MTS_C_SNK_pipeHot_A=[31,178] !Changed automatically
MTS_C_SNK_pipeHot_B=[31,179] !Changed automatically
MQSnk183_A=[31,181] !Changed automatically
MQSnk183_B=[31,182] !Changed automatically
MSCnr178_QSnk183_A=[31,184] !Changed automatically
MSCnr178_QSnk183_B=[31,185] !Changed automatically
MQSnk183_SCnr178_A=[31,187] !Changed automatically
MQSnk183_SCnr178_B=[31,188] !Changed automatically
MQSnk191_A=[31,190] !Changed automatically
MQSnk191_B=[31,191] !Changed automatically
MDTee194Cold_A=[31,193] !Changed automatically
MDTee194Cold_B=[31,194] !Changed automatically
MDTee194Cold_C=[31,195] !Changed automatically
MDTee194Hot_A=[31,196] !Changed automatically
MDTee194Hot_B=[31,197] !Changed automatically
MDTee194Hot_C=[31,198] !Changed automatically
MTS_D_2_1Cold_A=[31,199] !Changed automatically
MTS_D_2_1Cold_B=[31,200] !Changed automatically
MTS_D_2_1Hot_A=[31,202] !Changed automatically
MTS_D_2_1Hot_B=[31,203] !Changed automatically
MTS_D_2_2Cold_A=[31,205] !Changed automatically
MTS_D_2_2Cold_B=[31,206] !Changed automatically
MTS_D_2_2Hot_A=[31,208] !Changed automatically
MTS_D_2_2Hot_B=[31,209] !Changed automatically
MSCnr200Cold_A=[31,211] !Changed automatically
MSCnr200Cold_B=[31,212] !Changed automatically
MSCnr200Hot_A=[31,214] !Changed automatically
MSCnr200Hot_B=[31,215] !Changed automatically
MTS_D_2_SNK_pipeCold_A=[31,217] !Changed automatically
MTS_D_2_SNK_pipeCold_B=[31,218] !Changed automatically
MTS_D_2_SNK_pipeHot_A=[31,220] !Changed automatically
MTS_D_2_SNK_pipeHot_B=[31,221] !Changed automatically
MDTee213Cold_A=[31,223] !Changed automatically
MDTee213Cold_B=[31,224] !Changed automatically
MDTee213Cold_C=[31,225] !Changed automatically
MDTee213Hot_A=[31,226] !Changed automatically
MDTee213Hot_B=[31,227] !Changed automatically
MDTee213Hot_C=[31,228] !Changed automatically
MTS_H_2Cold_A=[31,229] !Changed automatically
MTS_H_2Cold_B=[31,230] !Changed automatically
MTS_H_2Hot_A=[31,232] !Changed automatically
MTS_H_2Hot_B=[31,233] !Changed automatically
MSCnr220Cold_A=[31,235] !Changed automatically
MSCnr220Cold_B=[31,236] !Changed automatically
MSCnr220Hot_A=[31,238] !Changed automatically
MSCnr220Hot_B=[31,239] !Changed automatically
MTS_H_SNK_pipeCold_A=[31,241] !Changed automatically
MTS_H_SNK_pipeCold_B=[31,242] !Changed automatically
MTS_H_SNK_pipeHot_A=[31,244] !Changed automatically
MTS_H_SNK_pipeHot_B=[31,245] !Changed automatically
MQSnk225_A=[31,247] !Changed automatically
MQSnk225_B=[31,248] !Changed automatically
MDTee232Cold_A=[31,250] !Changed automatically
MDTee232Cold_B=[31,251] !Changed automatically
MDTee232Cold_C=[31,252] !Changed automatically
MDTee232Hot_A=[31,253] !Changed automatically
MDTee232Hot_B=[31,254] !Changed automatically
MDTee232Hot_C=[31,255] !Changed automatically
MSCnr238Cold_A=[31,256] !Changed automatically
MSCnr238Cold_B=[31,257] !Changed automatically
MSCnr238Hot_A=[31,259] !Changed automatically
MSCnr238Hot_B=[31,260] !Changed automatically
MTS_K_SNK_pipeCold_A=[31,262] !Changed automatically
MTS_K_SNK_pipeCold_B=[31,263] !Changed automatically
MTS_K_SNK_pipeHot_A=[31,265] !Changed automatically
MTS_K_SNK_pipeHot_B=[31,266] !Changed automatically
MQSnk243_A=[31,268] !Changed automatically
MQSnk243_B=[31,269] !Changed automatically
MSCnr238_QSnk243_A=[31,271] !Changed automatically
MSCnr238_QSnk243_B=[31,272] !Changed automatically
MQSnk243_SCnr238_A=[31,274] !Changed automatically
MQSnk243_SCnr238_B=[31,275] !Changed automatically
MDTee253Cold_A=[31,277] !Changed automatically
MDTee253Cold_B=[31,278] !Changed automatically
MDTee253Cold_C=[31,279] !Changed automatically
MDTee253Hot_A=[31,280] !Changed automatically
MDTee253Hot_B=[31,281] !Changed automatically
MDTee253Hot_C=[31,282] !Changed automatically
MTS_K_1Cold_A=[31,283] !Changed automatically
MTS_K_1Cold_B=[31,284] !Changed automatically
MTS_K_1Hot_A=[31,286] !Changed automatically
MTS_K_1Hot_B=[31,287] !Changed automatically
MSCnr261Cold_A=[31,289] !Changed automatically
MSCnr261Cold_B=[31,290] !Changed automatically
MSCnr261Hot_A=[31,292] !Changed automatically
MSCnr261Hot_B=[31,293] !Changed automatically
MSeitenarm_VICold_A=[31,295] !Changed automatically
MSeitenarm_VICold_B=[31,296] !Changed automatically
MSeitenarm_VIHot_A=[31,298] !Changed automatically
MSeitenarm_VIHot_B=[31,299] !Changed automatically
MQSnk266_A=[31,301] !Changed automatically
MQSnk266_B=[31,302] !Changed automatically
MSCnr200_QSnk191_A=[31,304] !Changed automatically
MSCnr200_QSnk191_B=[31,305] !Changed automatically
MQSnk191_SCnr200_A=[31,307] !Changed automatically
MQSnk191_SCnr200_B=[31,308] !Changed automatically
MSCnr220_QSnk225_A=[31,310] !Changed automatically
MSCnr220_QSnk225_B=[31,311] !Changed automatically
MQSnk225_SCnr220_A=[31,313] !Changed automatically
MQSnk225_SCnr220_B=[31,314] !Changed automatically
MSCnr261_QSnk266_A=[31,316] !Changed automatically
MSCnr261_QSnk266_B=[31,317] !Changed automatically
MQSnk266_SCnr261_A=[31,319] !Changed automatically
MQSnk266_SCnr261_B=[31,320] !Changed automatically
MDTee315Cold_A=[31,322] !Changed automatically
MDTee315Cold_B=[31,323] !Changed automatically
MDTee315Cold_C=[31,324] !Changed automatically
MDTee315Hot_A=[31,325] !Changed automatically
MDTee315Hot_B=[31,326] !Changed automatically
MDTee315Hot_C=[31,327] !Changed automatically
MDCnr319Cold_A=[31,328] !Changed automatically
MDCnr319Cold_B=[31,329] !Changed automatically
MDCnr319Hot_A=[31,331] !Changed automatically
MDCnr319Hot_B=[31,332] !Changed automatically
MQSnk322_A=[31,334] !Changed automatically
MQSnk322_B=[31,335] !Changed automatically
MTS_GCold_A=[31,337] !Changed automatically
MTS_GCold_B=[31,338] !Changed automatically
MTS_GHot_A=[31,340] !Changed automatically
MTS_GHot_B=[31,341] !Changed automatically
MTS_H_1Cold_A=[31,343] !Changed automatically
MTS_H_1Cold_B=[31,344] !Changed automatically
MTS_H_1Hot_A=[31,346] !Changed automatically
MTS_H_1Hot_B=[31,347] !Changed automatically
MDTee327Cold_A=[31,349] !Changed automatically
MDTee327Cold_B=[31,350] !Changed automatically
MDTee327Cold_C=[31,351] !Changed automatically
MDTee327Hot_A=[31,352] !Changed automatically
MDTee327Hot_B=[31,353] !Changed automatically
MDTee327Hot_C=[31,354] !Changed automatically
MSCnr331Cold_A=[31,355] !Changed automatically
MSCnr331Cold_B=[31,356] !Changed automatically
MSCnr331Hot_A=[31,358] !Changed automatically
MSCnr331Hot_B=[31,359] !Changed automatically
MQSnk335_A=[31,361] !Changed automatically
MQSnk335_B=[31,362] !Changed automatically
MSeitenarm_IV_absch_1_1Cold_A=[31,364] !Changed automatically
MSeitenarm_IV_absch_1_1Cold_B=[31,365] !Changed automatically
MSeitenarm_IV_absch_1_1Hot_A=[31,367] !Changed automatically
MSeitenarm_IV_absch_1_1Hot_B=[31,368] !Changed automatically
MSeitenarm_IV_absch_1_SNKCold_A=[31,370] !Changed automatically
MSeitenarm_IV_absch_1_SNKCold_B=[31,371] !Changed automatically
MSeitenarm_IV_absch_1_SNKHot_A=[31,373] !Changed automatically
MSeitenarm_IV_absch_1_SNKHot_B=[31,374] !Changed automatically
MSeitenarm_IV_absch_1_2Cold_A=[31,376] !Changed automatically
MSeitenarm_IV_absch_1_2Cold_B=[31,377] !Changed automatically
MSeitenarm_IV_absch_1_2Hot_A=[31,379] !Changed automatically
MSeitenarm_IV_absch_1_2Hot_B=[31,380] !Changed automatically
MDTee343Cold_A=[31,382] !Changed automatically
MDTee343Cold_B=[31,383] !Changed automatically
MDTee343Cold_C=[31,384] !Changed automatically
MDTee343Hot_A=[31,385] !Changed automatically
MDTee343Hot_B=[31,386] !Changed automatically
MDTee343Hot_C=[31,387] !Changed automatically
MDTee347Cold_A=[31,388] !Changed automatically
MDTee347Cold_B=[31,389] !Changed automatically
MDTee347Cold_C=[31,390] !Changed automatically
MDTee347Hot_A=[31,391] !Changed automatically
MDTee347Hot_B=[31,392] !Changed automatically
MDTee347Hot_C=[31,393] !Changed automatically
MSeitenarm_IV_absch_2_1Cold_A=[31,394] !Changed automatically
MSeitenarm_IV_absch_2_1Cold_B=[31,395] !Changed automatically
MSeitenarm_IV_absch_2_1Hot_A=[31,397] !Changed automatically
MSeitenarm_IV_absch_2_1Hot_B=[31,398] !Changed automatically
MSeitenarm_IV_absch_2_2Cold_A=[31,400] !Changed automatically
MSeitenarm_IV_absch_2_2Cold_B=[31,401] !Changed automatically
MSeitenarm_IV_absch_2_2Hot_A=[31,403] !Changed automatically
MSeitenarm_IV_absch_2_2Hot_B=[31,404] !Changed automatically
MSCnr353Cold_A=[31,406] !Changed automatically
MSCnr353Cold_B=[31,407] !Changed automatically
MSCnr353Hot_A=[31,409] !Changed automatically
MSCnr353Hot_B=[31,410] !Changed automatically
MQSnk358_A=[31,412] !Changed automatically
MQSnk358_B=[31,413] !Changed automatically
MSCnr363Cold_A=[31,415] !Changed automatically
MSCnr363Cold_B=[31,416] !Changed automatically
MSCnr363Hot_A=[31,418] !Changed automatically
MSCnr363Hot_B=[31,419] !Changed automatically
MSeitenarm_IV_absch_3_RCold_A=[31,421] !Changed automatically
MSeitenarm_IV_absch_3_RCold_B=[31,422] !Changed automatically
MSeitenarm_IV_absch_3_RHot_A=[31,424] !Changed automatically
MSeitenarm_IV_absch_3_RHot_B=[31,425] !Changed automatically
MSCnr370Cold_A=[31,427] !Changed automatically
MSCnr370Cold_B=[31,428] !Changed automatically
MSCnr370Hot_A=[31,430] !Changed automatically
MSCnr370Hot_B=[31,431] !Changed automatically
MSeitenarm_IV_absch_3_LCold_A=[31,433] !Changed automatically
MSeitenarm_IV_absch_3_LCold_B=[31,434] !Changed automatically
MSeitenarm_IV_absch_3_LHot_A=[31,436] !Changed automatically
MSeitenarm_IV_absch_3_LHot_B=[31,437] !Changed automatically
MQSnk375_A=[31,439] !Changed automatically
MQSnk375_B=[31,440] !Changed automatically
MSCnr331_QSnk335_A=[31,442] !Changed automatically
MSCnr331_QSnk335_B=[31,443] !Changed automatically
MQSnk335_SCnr331_A=[31,445] !Changed automatically
MQSnk335_SCnr331_B=[31,446] !Changed automatically
MSCnr353_QSnk358_A=[31,448] !Changed automatically
MSCnr353_QSnk358_B=[31,449] !Changed automatically
MQSnk358_SCnr353_A=[31,451] !Changed automatically
MQSnk358_SCnr353_B=[31,452] !Changed automatically
MSCnr363_QSnk322_A=[31,454] !Changed automatically
MSCnr363_QSnk322_B=[31,455] !Changed automatically
MQSnk322_SCnr363_A=[31,457] !Changed automatically
MQSnk322_SCnr363_B=[31,458] !Changed automatically
MSCnr370_QSnk375_A=[31,460] !Changed automatically
MSCnr370_QSnk375_B=[31,461] !Changed automatically
MQSnk375_SCnr370_A=[31,463] !Changed automatically
MQSnk375_SCnr370_B=[31,464] !Changed automatically
MSeitenarm_IV_absch_2_SNKCold_A=[31,466] !Changed automatically
MSeitenarm_IV_absch_2_SNKCold_B=[31,467] !Changed automatically
MSeitenarm_IV_absch_2_SNKHot_A=[31,469] !Changed automatically
MSeitenarm_IV_absch_2_SNKHot_B=[31,470] !Changed automatically
MDTee405Cold_A=[31,472] !Changed automatically
MDTee405Cold_B=[31,473] !Changed automatically
MDTee405Cold_C=[31,474] !Changed automatically
MDTee405Hot_A=[31,475] !Changed automatically
MDTee405Hot_B=[31,476] !Changed automatically
MDTee405Hot_C=[31,477] !Changed automatically
MTS_K_2Cold_A=[31,478] !Changed automatically
MTS_K_2Cold_B=[31,479] !Changed automatically
MTS_K_2Hot_A=[31,481] !Changed automatically
MTS_K_2Hot_B=[31,482] !Changed automatically
MSeitenarm_VIIICold_A=[31,484] !Changed automatically
MSeitenarm_VIIICold_B=[31,485] !Changed automatically
MSeitenarm_VIIIHot_A=[31,487] !Changed automatically
MSeitenarm_VIIIHot_B=[31,488] !Changed automatically
MSCnr412Cold_A=[31,490] !Changed automatically
MSCnr412Cold_B=[31,491] !Changed automatically
MSCnr412Hot_A=[31,493] !Changed automatically
MSCnr412Hot_B=[31,494] !Changed automatically
MSeitenarm_VIICold_A=[31,496] !Changed automatically
MSeitenarm_VIICold_B=[31,497] !Changed automatically
MSeitenarm_VIIHot_A=[31,499] !Changed automatically
MSeitenarm_VIIHot_B=[31,500] !Changed automatically
MQSnk417_A=[31,502] !Changed automatically
MQSnk417_B=[31,503] !Changed automatically
MSCnr412_QSnk417_A=[31,505] !Changed automatically
MSCnr412_QSnk417_B=[31,506] !Changed automatically
MQSnk417_SCnr412_A=[31,508] !Changed automatically
MQSnk417_SCnr412_B=[31,509] !Changed automatically
MDTee424Cold_A=[31,511] !Changed automatically
MDTee424Cold_B=[31,512] !Changed automatically
MDTee424Cold_C=[31,513] !Changed automatically
MDTee424Hot_A=[31,514] !Changed automatically
MDTee424Hot_B=[31,515] !Changed automatically
MDTee424Hot_C=[31,516] !Changed automatically
MTS_ICold_A=[31,517] !Changed automatically
MTS_ICold_B=[31,518] !Changed automatically
MTS_IHot_A=[31,520] !Changed automatically
MTS_IHot_B=[31,521] !Changed automatically
MTS_JCold_A=[31,523] !Changed automatically
MTS_JCold_B=[31,524] !Changed automatically
MTS_JHot_A=[31,526] !Changed automatically
MTS_JHot_B=[31,527] !Changed automatically
MDCnr430Cold_A=[31,529] !Changed automatically
MDCnr430Cold_B=[31,530] !Changed automatically
MDCnr430Hot_A=[31,532] !Changed automatically
MDCnr430Hot_B=[31,533] !Changed automatically
MSeitenarm_V_1_1Cold_A=[31,535] !Changed automatically
MSeitenarm_V_1_1Cold_B=[31,536] !Changed automatically
MSeitenarm_V_1_1Hot_A=[31,538] !Changed automatically
MSeitenarm_V_1_1Hot_B=[31,539] !Changed automatically
MDTee434Cold_A=[31,541] !Changed automatically
MDTee434Cold_B=[31,542] !Changed automatically
MDTee434Cold_C=[31,543] !Changed automatically
MDTee434Hot_A=[31,544] !Changed automatically
MDTee434Hot_B=[31,545] !Changed automatically
MDTee434Hot_C=[31,546] !Changed automatically
MSeitenarm_V_1_2_1Cold_A=[31,547] !Changed automatically
MSeitenarm_V_1_2_1Cold_B=[31,548] !Changed automatically
MSeitenarm_V_1_2_1Hot_A=[31,550] !Changed automatically
MSeitenarm_V_1_2_1Hot_B=[31,551] !Changed automatically
MDCnr439Cold_A=[31,553] !Changed automatically
MDCnr439Cold_B=[31,554] !Changed automatically
MDCnr439Hot_A=[31,556] !Changed automatically
MDCnr439Hot_B=[31,557] !Changed automatically
MSeitenarm_V_1_2_2Cold_A=[31,559] !Changed automatically
MSeitenarm_V_1_2_2Cold_B=[31,560] !Changed automatically
MSeitenarm_V_1_2_2Hot_A=[31,562] !Changed automatically
MSeitenarm_V_1_2_2Hot_B=[31,563] !Changed automatically
MSCnr443Cold_A=[31,565] !Changed automatically
MSCnr443Cold_B=[31,566] !Changed automatically
MSCnr443Hot_A=[31,568] !Changed automatically
MSCnr443Hot_B=[31,569] !Changed automatically
MSeitenarm_V_1_2_SNKCold_A=[31,571] !Changed automatically
MSeitenarm_V_1_2_SNKCold_B=[31,572] !Changed automatically
MSeitenarm_V_1_2_SNKHot_A=[31,574] !Changed automatically
MSeitenarm_V_1_2_SNKHot_B=[31,575] !Changed automatically
MQSnk448_A=[31,577] !Changed automatically
MQSnk448_B=[31,578] !Changed automatically
MSCnr443_QSnk448_A=[31,580] !Changed automatically
MSCnr443_QSnk448_B=[31,581] !Changed automatically
MQSnk448_SCnr443_A=[31,583] !Changed automatically
MQSnk448_SCnr443_B=[31,584] !Changed automatically
MDTee455Cold_A=[31,586] !Changed automatically
MDTee455Cold_B=[31,587] !Changed automatically
MDTee455Cold_C=[31,588] !Changed automatically
MDTee455Hot_A=[31,589] !Changed automatically
MDTee455Hot_B=[31,590] !Changed automatically
MDTee455Hot_C=[31,591] !Changed automatically
MDCnr459Cold_A=[31,592] !Changed automatically
MDCnr459Cold_B=[31,593] !Changed automatically
MDCnr459Hot_A=[31,595] !Changed automatically
MDCnr459Hot_B=[31,596] !Changed automatically
MSeitenarm_V_2_1Cold_A=[31,598] !Changed automatically
MSeitenarm_V_2_1Cold_B=[31,599] !Changed automatically
MSeitenarm_V_2_1Hot_A=[31,601] !Changed automatically
MSeitenarm_V_2_1Hot_B=[31,602] !Changed automatically
MSeitenarm_V_2_2Cold_A=[31,604] !Changed automatically
MSeitenarm_V_2_2Cold_B=[31,605] !Changed automatically
MSeitenarm_V_2_2Hot_A=[31,607] !Changed automatically
MSeitenarm_V_2_2Hot_B=[31,608] !Changed automatically
MSCnr464Cold_A=[31,610] !Changed automatically
MSCnr464Cold_B=[31,611] !Changed automatically
MSCnr464Hot_A=[31,613] !Changed automatically
MSCnr464Hot_B=[31,614] !Changed automatically
MSeitenarm_V_2_SNKCold_A=[31,616] !Changed automatically
MSeitenarm_V_2_SNKCold_B=[31,617] !Changed automatically
MSeitenarm_V_2_SNKHot_A=[31,619] !Changed automatically
MSeitenarm_V_2_SNKHot_B=[31,620] !Changed automatically
MQSnk469_A=[31,622] !Changed automatically
MQSnk469_B=[31,623] !Changed automatically
MSCnr464_QSnk469_A=[31,625] !Changed automatically
MSCnr464_QSnk469_B=[31,626] !Changed automatically
MQSnk469_SCnr464_A=[31,628] !Changed automatically
MQSnk469_SCnr464_B=[31,629] !Changed automatically
MDTee474Cold_A=[31,631] !Changed automatically
MDTee474Cold_B=[31,632] !Changed automatically
MDTee474Cold_C=[31,633] !Changed automatically
MDTee474Hot_A=[31,634] !Changed automatically
MDTee474Hot_B=[31,635] !Changed automatically
MDTee474Hot_C=[31,636] !Changed automatically
MSeitenarm_V_3_1Cold_A=[31,637] !Changed automatically
MSeitenarm_V_3_1Cold_B=[31,638] !Changed automatically
MSeitenarm_V_3_1Hot_A=[31,640] !Changed automatically
MSeitenarm_V_3_1Hot_B=[31,641] !Changed automatically
MDCnr479Cold_A=[31,643] !Changed automatically
MDCnr479Cold_B=[31,644] !Changed automatically
MDCnr479Hot_A=[31,646] !Changed automatically
MDCnr479Hot_B=[31,647] !Changed automatically
MSeitenarm_V_3_2Cold_A=[31,649] !Changed automatically
MSeitenarm_V_3_2Cold_B=[31,650] !Changed automatically
MSeitenarm_V_3_2Hot_A=[31,652] !Changed automatically
MSeitenarm_V_3_2Hot_B=[31,653] !Changed automatically
MSCnr483Cold_A=[31,655] !Changed automatically
MSCnr483Cold_B=[31,656] !Changed automatically
MSCnr483Hot_A=[31,658] !Changed automatically
MSCnr483Hot_B=[31,659] !Changed automatically
MSeitenarm_V_3_SNKCold_A=[31,661] !Changed automatically
MSeitenarm_V_3_SNKCold_B=[31,662] !Changed automatically
MSeitenarm_V_3_SNKHot_A=[31,664] !Changed automatically
MSeitenarm_V_3_SNKHot_B=[31,665] !Changed automatically
MQSnk488_A=[31,667] !Changed automatically
MQSnk488_B=[31,668] !Changed automatically
MSCnr483_QSnk488_A=[31,670] !Changed automatically
MSCnr483_QSnk488_B=[31,671] !Changed automatically
MQSnk488_SCnr483_A=[31,673] !Changed automatically
MQSnk488_SCnr483_B=[31,674] !Changed automatically
MDTee493Cold_A=[31,676] !Changed automatically
MDTee493Cold_B=[31,677] !Changed automatically
MDTee493Cold_C=[31,678] !Changed automatically
MDTee493Hot_A=[31,679] !Changed automatically
MDTee493Hot_B=[31,680] !Changed automatically
MDTee493Hot_C=[31,681] !Changed automatically
MSeitenarm_V_4_1Cold_A=[31,682] !Changed automatically
MSeitenarm_V_4_1Cold_B=[31,683] !Changed automatically
MSeitenarm_V_4_1Hot_A=[31,685] !Changed automatically
MSeitenarm_V_4_1Hot_B=[31,686] !Changed automatically
MSCnr498Cold_A=[31,688] !Changed automatically
MSCnr498Cold_B=[31,689] !Changed automatically
MSCnr498Hot_A=[31,691] !Changed automatically
MSCnr498Hot_B=[31,692] !Changed automatically
MU_1Cold_A=[31,694] !Changed automatically
MU_1Cold_B=[31,695] !Changed automatically
MU_1Hot_A=[31,697] !Changed automatically
MU_1Hot_B=[31,698] !Changed automatically
MQSnk503_A=[31,700] !Changed automatically
MQSnk503_B=[31,701] !Changed automatically
MSCnr498_QSnk503_A=[31,703] !Changed automatically
MSCnr498_QSnk503_B=[31,704] !Changed automatically
MQSnk503_SCnr498_A=[31,706] !Changed automatically
MQSnk503_SCnr498_B=[31,707] !Changed automatically
MDTee508Cold_A=[31,709] !Changed automatically
MDTee508Cold_B=[31,710] !Changed automatically
MDTee508Cold_C=[31,711] !Changed automatically
MDTee508Hot_A=[31,712] !Changed automatically
MDTee508Hot_B=[31,713] !Changed automatically
MDTee508Hot_C=[31,714] !Changed automatically
MDTee512Cold_A=[31,715] !Changed automatically
MDTee512Cold_B=[31,716] !Changed automatically
MDTee512Cold_C=[31,717] !Changed automatically
MDTee512Hot_A=[31,718] !Changed automatically
MDTee512Hot_B=[31,719] !Changed automatically
MDTee512Hot_C=[31,720] !Changed automatically
MDTee493_DTee512Cold_A=[31,721] !Changed automatically
MDTee493_DTee512Cold_B=[31,722] !Changed automatically
MDTee493_DTee512Hot_A=[31,724] !Changed automatically
MDTee493_DTee512Hot_B=[31,725] !Changed automatically
MSCnr517Cold_A=[31,727] !Changed automatically
MSCnr517Cold_B=[31,728] !Changed automatically
MSCnr517Hot_A=[31,730] !Changed automatically
MSCnr517Hot_B=[31,731] !Changed automatically
MU_2Cold_A=[31,733] !Changed automatically
MU_2Cold_B=[31,734] !Changed automatically
MU_2Hot_A=[31,736] !Changed automatically
MU_2Hot_B=[31,737] !Changed automatically
MQSnk524_A=[31,739] !Changed automatically
MQSnk524_B=[31,740] !Changed automatically
MSCnr517_QSnk524_A=[31,742] !Changed automatically
MSCnr517_QSnk524_B=[31,743] !Changed automatically
MQSnk524_SCnr517_A=[31,745] !Changed automatically
MQSnk524_SCnr517_B=[31,746] !Changed automatically
MDTee529Cold_A=[31,748] !Changed automatically
MDTee529Cold_B=[31,749] !Changed automatically
MDTee529Cold_C=[31,750] !Changed automatically
MDTee529Hot_A=[31,751] !Changed automatically
MDTee529Hot_B=[31,752] !Changed automatically
MDTee529Hot_C=[31,753] !Changed automatically
MSeitenarm_V_4_2Cold_A=[31,754] !Changed automatically
MSeitenarm_V_4_2Cold_B=[31,755] !Changed automatically
MSeitenarm_V_4_2Hot_A=[31,757] !Changed automatically
MSeitenarm_V_4_2Hot_B=[31,758] !Changed automatically
MSCnr534Cold_A=[31,760] !Changed automatically
MSCnr534Cold_B=[31,761] !Changed automatically
MSCnr534Hot_A=[31,763] !Changed automatically
MSCnr534Hot_B=[31,764] !Changed automatically
MSeitenarm_V_4_SNKCold_A=[31,766] !Changed automatically
MSeitenarm_V_4_SNKCold_B=[31,767] !Changed automatically
MSeitenarm_V_4_SNKHot_A=[31,769] !Changed automatically
MSeitenarm_V_4_SNKHot_B=[31,770] !Changed automatically
MQSnk539_A=[31,772] !Changed automatically
MQSnk539_B=[31,773] !Changed automatically
MSCnr534_QSnk539_A=[31,775] !Changed automatically
MSCnr534_QSnk539_B=[31,776] !Changed automatically
MQSnk539_SCnr534_A=[31,778] !Changed automatically
MQSnk539_SCnr534_B=[31,779] !Changed automatically
MDCnr544Cold_A=[31,781] !Changed automatically
MDCnr544Cold_B=[31,782] !Changed automatically
MDCnr544Hot_A=[31,784] !Changed automatically
MDCnr544Hot_B=[31,785] !Changed automatically
MSeitenarm_V_4_3Cold_A=[31,787] !Changed automatically
MSeitenarm_V_4_3Cold_B=[31,788] !Changed automatically
MSeitenarm_V_4_3Hot_A=[31,790] !Changed automatically
MSeitenarm_V_4_3Hot_B=[31,791] !Changed automatically
MDTee548Cold_A=[31,793] !Changed automatically
MDTee548Cold_B=[31,794] !Changed automatically
MDTee548Cold_C=[31,795] !Changed automatically
MDTee548Hot_A=[31,796] !Changed automatically
MDTee548Hot_B=[31,797] !Changed automatically
MDTee548Hot_C=[31,798] !Changed automatically
MSeitenarm_V_5_1Cold_A=[31,799] !Changed automatically
MSeitenarm_V_5_1Cold_B=[31,800] !Changed automatically
MSeitenarm_V_5_1Hot_A=[31,802] !Changed automatically
MSeitenarm_V_5_1Hot_B=[31,803] !Changed automatically
MSCnr553Cold_A=[31,805] !Changed automatically
MSCnr553Cold_B=[31,806] !Changed automatically
MSCnr553Hot_A=[31,808] !Changed automatically
MSCnr553Hot_B=[31,809] !Changed automatically
MSeitenarm_V_5_SNKCold_A=[31,811] !Changed automatically
MSeitenarm_V_5_SNKCold_B=[31,812] !Changed automatically
MSeitenarm_V_5_SNKHot_A=[31,814] !Changed automatically
MSeitenarm_V_5_SNKHot_B=[31,815] !Changed automatically
MQSnk558_A=[31,817] !Changed automatically
MQSnk558_B=[31,818] !Changed automatically
MSCnr553_QSnk558_A=[31,820] !Changed automatically
MSCnr553_QSnk558_B=[31,821] !Changed automatically
MQSnk558_SCnr553_A=[31,823] !Changed automatically
MQSnk558_SCnr553_B=[31,824] !Changed automatically
MSCnr567Cold_A=[31,826] !Changed automatically
MSCnr567Cold_B=[31,827] !Changed automatically
MSCnr567Hot_A=[31,829] !Changed automatically
MSCnr567Hot_B=[31,830] !Changed automatically
MSCnr571Cold_A=[31,832] !Changed automatically
MSCnr571Cold_B=[31,833] !Changed automatically
MSCnr571Hot_A=[31,835] !Changed automatically
MSCnr571Hot_B=[31,836] !Changed automatically
MQSnk579_A=[31,838] !Changed automatically
MQSnk579_B=[31,839] !Changed automatically
MSCnr571_QSnk579_A=[31,841] !Changed automatically
MSCnr571_QSnk579_B=[31,842] !Changed automatically
MQSnk579_SCnr571_A=[31,844] !Changed automatically
MQSnk579_SCnr571_B=[31,845] !Changed automatically
MSeitenarm_V_5_2Cold_A=[31,847] !Changed automatically
MSeitenarm_V_5_2Cold_B=[31,848] !Changed automatically
MSeitenarm_V_5_2Hot_A=[31,850] !Changed automatically
MSeitenarm_V_5_2Hot_B=[31,851] !Changed automatically
MU_3Cold_A=[31,853] !Changed automatically
MU_3Cold_B=[31,854] !Changed automatically
MU_3Hot_A=[31,856] !Changed automatically
MU_3Hot_B=[31,857] !Changed automatically
MQSnk586_A=[31,859] !Changed automatically
MQSnk586_B=[31,860] !Changed automatically
MSCnr567_QSnk586_A=[31,862] !Changed automatically
MSCnr567_QSnk586_B=[31,863] !Changed automatically
MQSnk586_SCnr567_A=[31,865] !Changed automatically
MQSnk586_SCnr567_B=[31,866] !Changed automatically
MSeitenarm_V_6Cold_A=[31,868] !Changed automatically
MSeitenarm_V_6Cold_B=[31,869] !Changed automatically
MSeitenarm_V_6Hot_A=[31,871] !Changed automatically
MSeitenarm_V_6Hot_B=[31,872] !Changed automatically
EQUATIONS 4
FbrineRho = RHOBRI ! [kg/m^3]
FbrineCp = CPBRI_SI*0.001 ! [kJ/(kg*K)]
FwaterRho = RHOWAT ! [kg/m^3]
FwaterCp = CPWAT_SI*0.001 ! [kJ/(kg*K)]
EQUATIONS 46
Lloop1Rho = FbrineRho
Lloop1Cp = FbrineCp
Lloop4Rho = FbrineRho
Lloop4Cp = FbrineCp
Lloop3Rho = FbrineRho
Lloop3Cp = FbrineCp
Lloop2Rho = FbrineRho
Lloop2Cp = FbrineCp
Lloop5Rho = FbrineRho
Lloop5Cp = FbrineCp
Lloop8Rho = FbrineRho
Lloop8Cp = FbrineCp
Lloop6Rho = FbrineRho
Lloop6Cp = FbrineCp
Lloop7Rho = FbrineRho
Lloop7Cp = FbrineCp
Lloop9Rho = FbrineRho
Lloop9Cp = FbrineCp
Lloop10Rho = FbrineRho
Lloop10Cp = FbrineCp
Lloop11Rho = FbrineRho
Lloop11Cp = FbrineCp
Lloop12Rho = FbrineRho
Lloop12Cp = FbrineCp
Lloop13Rho = FbrineRho
Lloop13Cp = FbrineCp
Lloop14Rho = FbrineRho
Lloop14Cp = FbrineCp
Lloop15Rho = FbrineRho
Lloop15Cp = FbrineCp
Lloop16Rho = FbrineRho
Lloop16Cp = FbrineCp
Lloop17Rho = FbrineRho
Lloop17Cp = FbrineCp
Lloop18Rho = FbrineRho
Lloop18Cp = FbrineCp
Lloop19Rho = FbrineRho
Lloop19Cp = FbrineCp
Lloop20Rho = FbrineRho
Lloop20Cp = FbrineCp
Lloop21Rho = FbrineRho
Lloop21Cp = FbrineCp
Lloop22Rho = FbrineRho
Lloop22Cp = FbrineCp
Lloop23Rho = FbrineRho
Lloop23Cp = FbrineCp
UNIT 32 TYPE 222 !Changed automatically
INPUTS 3
MSCnr4Cold_A TTS_ACold TSCnr4_QSrc1
0 20 20
EQUATIONS 1
TSCnr4Cold = [32,1] !Changed automatically
UNIT 33 TYPE 222 !Changed automatically
INPUTS 3
MSCnr4Hot_A TQSrc1_SCnr4 TTS_AHot
0 20 20
EQUATIONS 1
TSCnr4Hot = [33,1] !Changed automatically
UNIT 34 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee10Cold_A
MDTee10Cold_B
MDTee10Cold_C
TTS_BCold
TTS_C_1Cold
TSeitenarm_ICold
0 0 0 20 20 20 
EQUATIONS 1
TDTee10Cold= [34,1] !Changed automatically
UNIT 35 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee10Hot_A
MDTee10Hot_B
MDTee10Hot_C
TTS_BHot
TTS_C_1Hot
TSeitenarm_IHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee10Hot= [35,1] !Changed automatically
UNIT 36 TYPE 222 !Changed automatically
INPUTS 3
MSCnr16Cold_A TSeitenarm_ICold TQSnk85_SCnr16
0 20 20
EQUATIONS 1
TSCnr16Cold = [36,1] !Changed automatically
UNIT 37 TYPE 222 !Changed automatically
INPUTS 3
MSCnr16Hot_A TSCnr16_QSnk85 TSeitenarm_IHot
0 20 20
EQUATIONS 1
TSCnr16Hot = [37,1] !Changed automatically
UNIT 38 TYPE 222 !Changed automatically
INPUTS 3
MDCnr20Hot_A TTS_AHot TTS_BHot
0 20 20
EQUATIONS 1
TDCnr20Hot = [38,1] !Changed automatically
UNIT 39 TYPE 222 !Changed automatically
INPUTS 3
MDCnr20Cold_A TTS_BCold TTS_ACold
0 20 20
EQUATIONS 1
TDCnr20Cold = [39,1] !Changed automatically
UNIT 40 TYPE 9511 !Changed automatically
PARAMETERS 36
135.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDCnr20Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_ACold_A ! Inlet fluid flow rate - cold pipe, kg/h
TSCnr4Cold ! ! Other side of pipe - cold pipe, deg C
TSCnr4Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_AHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDCnr20Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_ACold = [40,1]   !Changed automatically
MTS_ACold = MTS_ACold_A  ! Outlet mass flow rate, kg/h
TTS_AHot = [40,3]   !Changed automatically
MTS_AHot = MTS_AHot_A  ! Outlet mass flow rate, kg/h
TS_AColdConv = [40,7]*-1*1/3600  !Changed automatically
TS_AColdInt = [40,9]*1/3600  !Changed automatically
TS_AColdDiss = [40,11]*1/3600  !Changed automatically
TS_AHotConv = [40,8]*-1*1/3600  !Changed automatically
TS_AHotInt = [40,10]*1/3600  !Changed automatically
TS_AHotDiss = [40,12]*1/3600  !Changed automatically
TS_AExch = [40,13]*1/3600  !Changed automatically
TS_AGrSl = [40,14]*1/3600  !Changed automatically
TS_ASlFf = [40,15]*1/3600  !Changed automatically
TS_ASlInt = [40,16]*1/3600  !Changed automatically
UNIT 41 TYPE 9511 !Changed automatically
PARAMETERS 36
75.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee10Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_BCold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDCnr20Cold ! ! Other side of pipe - cold pipe, deg C
TDCnr20Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_BHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee10Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_BCold = [41,1]   !Changed automatically
MTS_BCold = MTS_BCold_A  ! Outlet mass flow rate, kg/h
TTS_BHot = [41,3]   !Changed automatically
MTS_BHot = MTS_BHot_A  ! Outlet mass flow rate, kg/h
TS_BColdConv = [41,7]*-1*1/3600  !Changed automatically
TS_BColdInt = [41,9]*1/3600  !Changed automatically
TS_BColdDiss = [41,11]*1/3600  !Changed automatically
TS_BHotConv = [41,8]*-1*1/3600  !Changed automatically
TS_BHotInt = [41,10]*1/3600  !Changed automatically
TS_BHotDiss = [41,12]*1/3600  !Changed automatically
TS_BExch = [41,13]*1/3600  !Changed automatically
TS_BGrSl = [41,14]*1/3600  !Changed automatically
TS_BSlFf = [41,15]*1/3600  !Changed automatically
TS_BSlInt = [41,16]*1/3600  !Changed automatically
UNIT 42 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee50Cold_A
MDTee50Cold_B
MDTee50Cold_C
TTS_D_1Cold
TTS_C_2Cold
TSeitenarm_IICold
0 0 0 20 20 20 
EQUATIONS 1
TDTee50Cold= [42,1] !Changed automatically
UNIT 43 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee50Hot_A
MDTee50Hot_B
MDTee50Hot_C
TTS_D_1Hot
TTS_C_2Hot
TSeitenarm_IIHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee50Hot= [43,1] !Changed automatically
UNIT 44 TYPE 222 !Changed automatically
INPUTS 3
MSCnr55Cold_A TSeitenarm_IICold TQSnk60_SCnr55
0 20 20
EQUATIONS 1
TSCnr55Cold = [44,1] !Changed automatically
UNIT 45 TYPE 222 !Changed automatically
INPUTS 3
MSCnr55Hot_A TSCnr55_QSnk60 TSeitenarm_IIHot
0 20 20
EQUATIONS 1
TSCnr55Hot = [45,1] !Changed automatically
UNIT 46 TYPE 9511 !Changed automatically
PARAMETERS 36
55.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TSCnr55Cold ! Inlet fluid temperature - cold pipe, deg C
MSeitenarm_IICold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee50Cold ! ! Other side of pipe - cold pipe, deg C
TDTee50Hot ! Inlet fluid temperature - hot pipe, deg C
MSeitenarm_IIHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TSCnr55Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TSeitenarm_IICold = [46,1]   !Changed automatically
MSeitenarm_IICold = MSeitenarm_IICold_A  ! Outlet mass flow rate, kg/h
TSeitenarm_IIHot = [46,3]   !Changed automatically
MSeitenarm_IIHot = MSeitenarm_IIHot_A  ! Outlet mass flow rate, kg/h
Seitenarm_IIColdConv = [46,7]*-1*1/3600  !Changed automatically
Seitenarm_IIColdInt = [46,9]*1/3600  !Changed automatically
Seitenarm_IIColdDiss = [46,11]*1/3600  !Changed automatically
Seitenarm_IIHotConv = [46,8]*-1*1/3600  !Changed automatically
Seitenarm_IIHotInt = [46,10]*1/3600  !Changed automatically
Seitenarm_IIHotDiss = [46,12]*1/3600  !Changed automatically
Seitenarm_IIExch = [46,13]*1/3600  !Changed automatically
Seitenarm_IIGrSl = [46,14]*1/3600  !Changed automatically
Seitenarm_IISlFf = [46,15]*1/3600  !Changed automatically
Seitenarm_IISlInt = [46,16]*1/3600  !Changed automatically
UNIT 47 TYPE 222 !Changed automatically
INPUTS 3
MDCnr65Hot_A TTS_D_2_1Hot TTS_D_1Hot
0 20 20
EQUATIONS 1
TDCnr65Hot = [47,1] !Changed automatically
UNIT 48 TYPE 222 !Changed automatically
INPUTS 3
MDCnr65Cold_A TTS_D_1Cold TTS_D_2_1Cold
0 20 20
EQUATIONS 1
TDCnr65Cold = [48,1] !Changed automatically
UNIT 49 TYPE 222 !Changed automatically
INPUTS 3
MDCnr68Hot_A TTS_EHot TTS_D_2_2Hot
0 20 20
EQUATIONS 1
TDCnr68Hot = [49,1] !Changed automatically
UNIT 50 TYPE 222 !Changed automatically
INPUTS 3
MDCnr68Cold_A TTS_D_2_2Cold TTS_ECold
0 20 20
EQUATIONS 1
TDCnr68Cold = [50,1] !Changed automatically
UNIT 51 TYPE 222 !Changed automatically
INPUTS 3
MDCnr71Hot_A TTS_FHot TTS_EHot
0 20 20
EQUATIONS 1
TDCnr71Hot = [51,1] !Changed automatically
UNIT 52 TYPE 222 !Changed automatically
INPUTS 3
MDCnr71Cold_A TTS_ECold TTS_FCold
0 20 20
EQUATIONS 1
TDCnr71Cold = [52,1] !Changed automatically
UNIT 53 TYPE 222 !Changed automatically
INPUTS 3
MDCnr74Hot_A TTS_GHot TTS_FHot
0 20 20
EQUATIONS 1
TDCnr74Hot = [53,1] !Changed automatically
UNIT 54 TYPE 222 !Changed automatically
INPUTS 3
MDCnr74Cold_A TTS_FCold TTS_GCold
0 20 20
EQUATIONS 1
TDCnr74Cold = [54,1] !Changed automatically
UNIT 55 TYPE 9511 !Changed automatically
PARAMETERS 36
106.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDCnr65Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_D_1Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee50Cold ! ! Other side of pipe - cold pipe, deg C
TDTee50Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_D_1Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDCnr65Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_D_1Cold = [55,1]   !Changed automatically
MTS_D_1Cold = MTS_D_1Cold_A  ! Outlet mass flow rate, kg/h
TTS_D_1Hot = [55,3]   !Changed automatically
MTS_D_1Hot = MTS_D_1Hot_A  ! Outlet mass flow rate, kg/h
TS_D_1ColdConv = [55,7]*-1*1/3600  !Changed automatically
TS_D_1ColdInt = [55,9]*1/3600  !Changed automatically
TS_D_1ColdDiss = [55,11]*1/3600  !Changed automatically
TS_D_1HotConv = [55,8]*-1*1/3600  !Changed automatically
TS_D_1HotInt = [55,10]*1/3600  !Changed automatically
TS_D_1HotDiss = [55,12]*1/3600  !Changed automatically
TS_D_1Exch = [55,13]*1/3600  !Changed automatically
TS_D_1GrSl = [55,14]*1/3600  !Changed automatically
TS_D_1SlFf = [55,15]*1/3600  !Changed automatically
TS_D_1SlInt = [55,16]*1/3600  !Changed automatically
UNIT 56 TYPE 9511 !Changed automatically
PARAMETERS 36
160.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDCnr71Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_ECold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDCnr68Cold ! ! Other side of pipe - cold pipe, deg C
TDCnr68Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_EHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDCnr71Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_ECold = [56,1]   !Changed automatically
MTS_ECold = MTS_ECold_A  ! Outlet mass flow rate, kg/h
TTS_EHot = [56,3]   !Changed automatically
MTS_EHot = MTS_EHot_A  ! Outlet mass flow rate, kg/h
TS_EColdConv = [56,7]*-1*1/3600  !Changed automatically
TS_EColdInt = [56,9]*1/3600  !Changed automatically
TS_EColdDiss = [56,11]*1/3600  !Changed automatically
TS_EHotConv = [56,8]*-1*1/3600  !Changed automatically
TS_EHotInt = [56,10]*1/3600  !Changed automatically
TS_EHotDiss = [56,12]*1/3600  !Changed automatically
TS_EExch = [56,13]*1/3600  !Changed automatically
TS_EGrSl = [56,14]*1/3600  !Changed automatically
TS_ESlFf = [56,15]*1/3600  !Changed automatically
TS_ESlInt = [56,16]*1/3600  !Changed automatically
UNIT 57 TYPE 9511 !Changed automatically
PARAMETERS 36
370.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TSCnr16Cold ! Inlet fluid temperature - cold pipe, deg C
MSeitenarm_ICold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee10Cold ! ! Other side of pipe - cold pipe, deg C
TDTee10Hot ! Inlet fluid temperature - hot pipe, deg C
MSeitenarm_IHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TSCnr16Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TSeitenarm_ICold = [57,1]   !Changed automatically
MSeitenarm_ICold = MSeitenarm_ICold_A  ! Outlet mass flow rate, kg/h
TSeitenarm_IHot = [57,3]   !Changed automatically
MSeitenarm_IHot = MSeitenarm_IHot_A  ! Outlet mass flow rate, kg/h
Seitenarm_IColdConv = [57,7]*-1*1/3600  !Changed automatically
Seitenarm_IColdInt = [57,9]*1/3600  !Changed automatically
Seitenarm_IColdDiss = [57,11]*1/3600  !Changed automatically
Seitenarm_IHotConv = [57,8]*-1*1/3600  !Changed automatically
Seitenarm_IHotInt = [57,10]*1/3600  !Changed automatically
Seitenarm_IHotDiss = [57,12]*1/3600  !Changed automatically
Seitenarm_IExch = [57,13]*1/3600  !Changed automatically
Seitenarm_IGrSl = [57,14]*1/3600  !Changed automatically
Seitenarm_ISlFf = [57,15]*1/3600  !Changed automatically
Seitenarm_ISlInt = [57,16]*1/3600  !Changed automatically
UNIT 58 TYPE 9511 !Changed automatically
PARAMETERS 36
60.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDCnr74Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_FCold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDCnr71Cold ! ! Other side of pipe - cold pipe, deg C
TDCnr71Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_FHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDCnr74Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_FCold = [58,1]   !Changed automatically
MTS_FCold = MTS_FCold_A  ! Outlet mass flow rate, kg/h
TTS_FHot = [58,3]   !Changed automatically
MTS_FHot = MTS_FHot_A  ! Outlet mass flow rate, kg/h
TS_FColdConv = [58,7]*-1*1/3600  !Changed automatically
TS_FColdInt = [58,9]*1/3600  !Changed automatically
TS_FColdDiss = [58,11]*1/3600  !Changed automatically
TS_FHotConv = [58,8]*-1*1/3600  !Changed automatically
TS_FHotInt = [58,10]*1/3600  !Changed automatically
TS_FHotDiss = [58,12]*1/3600  !Changed automatically
TS_FExch = [58,13]*1/3600  !Changed automatically
TS_FGrSl = [58,14]*1/3600  !Changed automatically
TS_FSlFf = [58,15]*1/3600  !Changed automatically
TS_FSlInt = [58,16]*1/3600  !Changed automatically
UNIT 59 TYPE 222 !Changed automatically
INPUTS 3
MDCnr110Hot_A TTS_IHot TTS_H_2Hot
0 20 20
EQUATIONS 1
TDCnr110Hot = [59,1] !Changed automatically
UNIT 60 TYPE 222 !Changed automatically
INPUTS 3
MDCnr110Cold_A TTS_H_2Cold TTS_ICold
0 20 20
EQUATIONS 1
TDCnr110Cold = [60,1] !Changed automatically
UNIT 61 TYPE 222 !Changed automatically
INPUTS 3
MSCnr126Cold_A TSeitenarm_VIIICold TQSnk131_SCnr126
0 20 20
EQUATIONS 1
TSCnr126Cold = [61,1] !Changed automatically
UNIT 62 TYPE 222 !Changed automatically
INPUTS 3
MSCnr126Hot_A TSCnr126_QSnk131 TSeitenarm_VIIIHot
0 20 20
EQUATIONS 1
TSCnr126Hot = [62,1] !Changed automatically
UNIT 63 TYPE 222 !Changed automatically
INPUTS 3
MSCnr4_QSrc1_A TSCnr4Cold TQSrc1H
0 20 20
EQUATIONS 2
TSCnr4_QSrc1 = [63,1] !Changed automatically
MSCnr4_QSrc1 = MSCnr4_QSrc1_A
UNIT 64 TYPE 222 !Changed automatically
INPUTS 3
MQSrc1_SCnr4_A TQSrc1H TSCnr4Hot
0 20 20
EQUATIONS 2
TQSrc1_SCnr4 = [64,1] !Changed automatically
MQSrc1_SCnr4 = MQSrc1_SCnr4_A
UNIT 65 TYPE 222 !Changed automatically
INPUTS 3
MSCnr55_QSnk60_A TSCnr55Hot TQSnk60H
0 20 20
EQUATIONS 2
TSCnr55_QSnk60 = [65,1] !Changed automatically
MSCnr55_QSnk60 = MSCnr55_QSnk60_A
UNIT 66 TYPE 222 !Changed automatically
INPUTS 3
MQSnk60_SCnr55_A TQSnk60H TSCnr55Cold
0 20 20
EQUATIONS 2
TQSnk60_SCnr55 = [66,1] !Changed automatically
MQSnk60_SCnr55 = MQSnk60_SCnr55_A
UNIT 67 TYPE 222 !Changed automatically
INPUTS 3
MSCnr126_QSnk131_A TSCnr126Hot TQSnk131H
0 20 20
EQUATIONS 2
TSCnr126_QSnk131 = [67,1] !Changed automatically
MSCnr126_QSnk131 = MSCnr126_QSnk131_A
UNIT 68 TYPE 222 !Changed automatically
INPUTS 3
MQSnk131_SCnr126_A TQSnk131H TSCnr126Cold
0 20 20
EQUATIONS 2
TQSnk131_SCnr126 = [68,1] !Changed automatically
MQSnk131_SCnr126 = MQSnk131_SCnr126_A
UNIT 69 TYPE 222 !Changed automatically
INPUTS 3
MSCnr16_QSnk85_A TSCnr16Hot TQSnk85H
0 20 20
EQUATIONS 2
TSCnr16_QSnk85 = [69,1] !Changed automatically
MSCnr16_QSnk85 = MSCnr16_QSnk85_A
UNIT 70 TYPE 222 !Changed automatically
INPUTS 3
MQSnk85_SCnr16_A TQSnk85H TSCnr16Cold
0 20 20
EQUATIONS 2
TQSnk85_SCnr16 = [70,1] !Changed automatically
MQSnk85_SCnr16 = MQSnk85_SCnr16_A
UNIT 71 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee172Cold_A
MDTee172Cold_B
MDTee172Cold_C
TTS_C_2Cold
TTS_C_1Cold
TTS_C_SNK_pipeCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee172Cold= [71,1] !Changed automatically
UNIT 72 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee172Hot_A
MDTee172Hot_B
MDTee172Hot_C
TTS_C_2Hot
TTS_C_1Hot
TTS_C_SNK_pipeHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee172Hot= [72,1] !Changed automatically
UNIT 73 TYPE 9511 !Changed automatically
PARAMETERS 36
52.5                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee172Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_C_1Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee10Cold ! ! Other side of pipe - cold pipe, deg C
TDTee10Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_C_1Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee172Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_C_1Cold = [73,1]   !Changed automatically
MTS_C_1Cold = MTS_C_1Cold_A  ! Outlet mass flow rate, kg/h
TTS_C_1Hot = [73,3]   !Changed automatically
MTS_C_1Hot = MTS_C_1Hot_A  ! Outlet mass flow rate, kg/h
TS_C_1ColdConv = [73,7]*-1*1/3600  !Changed automatically
TS_C_1ColdInt = [73,9]*1/3600  !Changed automatically
TS_C_1ColdDiss = [73,11]*1/3600  !Changed automatically
TS_C_1HotConv = [73,8]*-1*1/3600  !Changed automatically
TS_C_1HotInt = [73,10]*1/3600  !Changed automatically
TS_C_1HotDiss = [73,12]*1/3600  !Changed automatically
TS_C_1Exch = [73,13]*1/3600  !Changed automatically
TS_C_1GrSl = [73,14]*1/3600  !Changed automatically
TS_C_1SlFf = [73,15]*1/3600  !Changed automatically
TS_C_1SlInt = [73,16]*1/3600  !Changed automatically
UNIT 74 TYPE 9511 !Changed automatically
PARAMETERS 36
52.5                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee50Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_C_2Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee172Cold ! ! Other side of pipe - cold pipe, deg C
TDTee172Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_C_2Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee50Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_C_2Cold = [74,1]   !Changed automatically
MTS_C_2Cold = MTS_C_2Cold_A  ! Outlet mass flow rate, kg/h
TTS_C_2Hot = [74,3]   !Changed automatically
MTS_C_2Hot = MTS_C_2Hot_A  ! Outlet mass flow rate, kg/h
TS_C_2ColdConv = [74,7]*-1*1/3600  !Changed automatically
TS_C_2ColdInt = [74,9]*1/3600  !Changed automatically
TS_C_2ColdDiss = [74,11]*1/3600  !Changed automatically
TS_C_2HotConv = [74,8]*-1*1/3600  !Changed automatically
TS_C_2HotInt = [74,10]*1/3600  !Changed automatically
TS_C_2HotDiss = [74,12]*1/3600  !Changed automatically
TS_C_2Exch = [74,13]*1/3600  !Changed automatically
TS_C_2GrSl = [74,14]*1/3600  !Changed automatically
TS_C_2SlFf = [74,15]*1/3600  !Changed automatically
TS_C_2SlInt = [74,16]*1/3600  !Changed automatically
UNIT 75 TYPE 222 !Changed automatically
INPUTS 3
MSCnr178Cold_A TTS_C_SNK_pipeCold TQSnk183_SCnr178
0 20 20
EQUATIONS 1
TSCnr178Cold = [75,1] !Changed automatically
UNIT 76 TYPE 222 !Changed automatically
INPUTS 3
MSCnr178Hot_A TSCnr178_QSnk183 TTS_C_SNK_pipeHot
0 20 20
EQUATIONS 1
TSCnr178Hot = [76,1] !Changed automatically
UNIT 77 TYPE 222 !Changed automatically
INPUTS 3
MTS_C_SNK_pipeCold_A TSCnr178Cold TDTee172Cold
0 20 20
EQUATIONS 2
TTS_C_SNK_pipeCold = [77,1] !Changed automatically
MTS_C_SNK_pipeCold = MTS_C_SNK_pipeCold_A
UNIT 78 TYPE 222 !Changed automatically
INPUTS 3
MTS_C_SNK_pipeHot_A TDTee172Hot TSCnr178Hot
0 20 20
EQUATIONS 2
TTS_C_SNK_pipeHot = [78,1] !Changed automatically
MTS_C_SNK_pipeHot = MTS_C_SNK_pipeHot_A
UNIT 79 TYPE 222 !Changed automatically
INPUTS 3
MSCnr178_QSnk183_A TSCnr178Hot TQSnk183H
0 20 20
EQUATIONS 2
TSCnr178_QSnk183 = [79,1] !Changed automatically
MSCnr178_QSnk183 = MSCnr178_QSnk183_A
UNIT 80 TYPE 222 !Changed automatically
INPUTS 3
MQSnk183_SCnr178_A TQSnk183H TSCnr178Cold
0 20 20
EQUATIONS 2
TQSnk183_SCnr178 = [80,1] !Changed automatically
MQSnk183_SCnr178 = MQSnk183_SCnr178_A
UNIT 81 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee194Cold_A
MDTee194Cold_B
MDTee194Cold_C
TTS_D_2_1Cold
TTS_D_2_2Cold
TTS_D_2_SNK_pipeCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee194Cold= [81,1] !Changed automatically
UNIT 82 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee194Hot_A
MDTee194Hot_B
MDTee194Hot_C
TTS_D_2_1Hot
TTS_D_2_2Hot
TTS_D_2_SNK_pipeHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee194Hot= [82,1] !Changed automatically
UNIT 83 TYPE 9511 !Changed automatically
PARAMETERS 36
60.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee194Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_D_2_1Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDCnr65Cold ! ! Other side of pipe - cold pipe, deg C
TDCnr65Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_D_2_1Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee194Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_D_2_1Cold = [83,1]   !Changed automatically
MTS_D_2_1Cold = MTS_D_2_1Cold_A  ! Outlet mass flow rate, kg/h
TTS_D_2_1Hot = [83,3]   !Changed automatically
MTS_D_2_1Hot = MTS_D_2_1Hot_A  ! Outlet mass flow rate, kg/h
TS_D_2_1ColdConv = [83,7]*-1*1/3600  !Changed automatically
TS_D_2_1ColdInt = [83,9]*1/3600  !Changed automatically
TS_D_2_1ColdDiss = [83,11]*1/3600  !Changed automatically
TS_D_2_1HotConv = [83,8]*-1*1/3600  !Changed automatically
TS_D_2_1HotInt = [83,10]*1/3600  !Changed automatically
TS_D_2_1HotDiss = [83,12]*1/3600  !Changed automatically
TS_D_2_1Exch = [83,13]*1/3600  !Changed automatically
TS_D_2_1GrSl = [83,14]*1/3600  !Changed automatically
TS_D_2_1SlFf = [83,15]*1/3600  !Changed automatically
TS_D_2_1SlInt = [83,16]*1/3600  !Changed automatically
UNIT 84 TYPE 9511 !Changed automatically
PARAMETERS 36
60.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDCnr68Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_D_2_2Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee194Cold ! ! Other side of pipe - cold pipe, deg C
TDTee194Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_D_2_2Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDCnr68Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_D_2_2Cold = [84,1]   !Changed automatically
MTS_D_2_2Cold = MTS_D_2_2Cold_A  ! Outlet mass flow rate, kg/h
TTS_D_2_2Hot = [84,3]   !Changed automatically
MTS_D_2_2Hot = MTS_D_2_2Hot_A  ! Outlet mass flow rate, kg/h
TS_D_2_2ColdConv = [84,7]*-1*1/3600  !Changed automatically
TS_D_2_2ColdInt = [84,9]*1/3600  !Changed automatically
TS_D_2_2ColdDiss = [84,11]*1/3600  !Changed automatically
TS_D_2_2HotConv = [84,8]*-1*1/3600  !Changed automatically
TS_D_2_2HotInt = [84,10]*1/3600  !Changed automatically
TS_D_2_2HotDiss = [84,12]*1/3600  !Changed automatically
TS_D_2_2Exch = [84,13]*1/3600  !Changed automatically
TS_D_2_2GrSl = [84,14]*1/3600  !Changed automatically
TS_D_2_2SlFf = [84,15]*1/3600  !Changed automatically
TS_D_2_2SlInt = [84,16]*1/3600  !Changed automatically
UNIT 85 TYPE 222 !Changed automatically
INPUTS 3
MSCnr200Cold_A TTS_D_2_SNK_pipeCold TQSnk191_SCnr200
0 20 20
EQUATIONS 1
TSCnr200Cold = [85,1] !Changed automatically
UNIT 86 TYPE 222 !Changed automatically
INPUTS 3
MSCnr200Hot_A TSCnr200_QSnk191 TTS_D_2_SNK_pipeHot
0 20 20
EQUATIONS 1
TSCnr200Hot = [86,1] !Changed automatically
UNIT 87 TYPE 222 !Changed automatically
INPUTS 3
MTS_D_2_SNK_pipeCold_A TSCnr200Cold TDTee194Cold
0 20 20
EQUATIONS 2
TTS_D_2_SNK_pipeCold = [87,1] !Changed automatically
MTS_D_2_SNK_pipeCold = MTS_D_2_SNK_pipeCold_A
UNIT 88 TYPE 222 !Changed automatically
INPUTS 3
MTS_D_2_SNK_pipeHot_A TDTee194Hot TSCnr200Hot
0 20 20
EQUATIONS 2
TTS_D_2_SNK_pipeHot = [88,1] !Changed automatically
MTS_D_2_SNK_pipeHot = MTS_D_2_SNK_pipeHot_A
UNIT 89 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee213Cold_A
MDTee213Cold_B
MDTee213Cold_C
TTS_H_1Cold
TTS_H_2Cold
TTS_H_SNK_pipeCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee213Cold= [89,1] !Changed automatically
UNIT 90 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee213Hot_A
MDTee213Hot_B
MDTee213Hot_C
TTS_H_1Hot
TTS_H_2Hot
TTS_H_SNK_pipeHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee213Hot= [90,1] !Changed automatically
UNIT 91 TYPE 9511 !Changed automatically
PARAMETERS 36
107.5                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee213Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_H_2Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDCnr110Cold ! ! Other side of pipe - cold pipe, deg C
TDCnr110Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_H_2Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee213Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_H_2Cold = [91,1]   !Changed automatically
MTS_H_2Cold = MTS_H_2Cold_A  ! Outlet mass flow rate, kg/h
TTS_H_2Hot = [91,3]   !Changed automatically
MTS_H_2Hot = MTS_H_2Hot_A  ! Outlet mass flow rate, kg/h
TS_H_2ColdConv = [91,7]*-1*1/3600  !Changed automatically
TS_H_2ColdInt = [91,9]*1/3600  !Changed automatically
TS_H_2ColdDiss = [91,11]*1/3600  !Changed automatically
TS_H_2HotConv = [91,8]*-1*1/3600  !Changed automatically
TS_H_2HotInt = [91,10]*1/3600  !Changed automatically
TS_H_2HotDiss = [91,12]*1/3600  !Changed automatically
TS_H_2Exch = [91,13]*1/3600  !Changed automatically
TS_H_2GrSl = [91,14]*1/3600  !Changed automatically
TS_H_2SlFf = [91,15]*1/3600  !Changed automatically
TS_H_2SlInt = [91,16]*1/3600  !Changed automatically
UNIT 92 TYPE 222 !Changed automatically
INPUTS 3
MSCnr220Cold_A TTS_H_SNK_pipeCold TQSnk225_SCnr220
0 20 20
EQUATIONS 1
TSCnr220Cold = [92,1] !Changed automatically
UNIT 93 TYPE 222 !Changed automatically
INPUTS 3
MSCnr220Hot_A TSCnr220_QSnk225 TTS_H_SNK_pipeHot
0 20 20
EQUATIONS 1
TSCnr220Hot = [93,1] !Changed automatically
UNIT 94 TYPE 222 !Changed automatically
INPUTS 3
MTS_H_SNK_pipeCold_A TSCnr220Cold TDTee213Cold
0 20 20
EQUATIONS 2
TTS_H_SNK_pipeCold = [94,1] !Changed automatically
MTS_H_SNK_pipeCold = MTS_H_SNK_pipeCold_A
UNIT 95 TYPE 222 !Changed automatically
INPUTS 3
MTS_H_SNK_pipeHot_A TDTee213Hot TSCnr220Hot
0 20 20
EQUATIONS 2
TTS_H_SNK_pipeHot = [95,1] !Changed automatically
MTS_H_SNK_pipeHot = MTS_H_SNK_pipeHot_A
UNIT 96 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee232Cold_A
MDTee232Cold_B
MDTee232Cold_C
TTS_K_1Cold
TTS_K_2Cold
TTS_K_SNK_pipeCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee232Cold= [96,1] !Changed automatically
UNIT 97 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee232Hot_A
MDTee232Hot_B
MDTee232Hot_C
TTS_K_1Hot
TTS_K_2Hot
TTS_K_SNK_pipeHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee232Hot= [97,1] !Changed automatically
UNIT 98 TYPE 222 !Changed automatically
INPUTS 3
MSCnr238Cold_A TTS_K_SNK_pipeCold TQSnk243_SCnr238
0 20 20
EQUATIONS 1
TSCnr238Cold = [98,1] !Changed automatically
UNIT 99 TYPE 222 !Changed automatically
INPUTS 3
MSCnr238Hot_A TSCnr238_QSnk243 TTS_K_SNK_pipeHot
0 20 20
EQUATIONS 1
TSCnr238Hot = [99,1] !Changed automatically
UNIT 100 TYPE 222 !Changed automatically
INPUTS 3
MTS_K_SNK_pipeCold_A TSCnr238Cold TDTee232Cold
0 20 20
EQUATIONS 2
TTS_K_SNK_pipeCold = [100,1] !Changed automatically
MTS_K_SNK_pipeCold = MTS_K_SNK_pipeCold_A
UNIT 101 TYPE 222 !Changed automatically
INPUTS 3
MTS_K_SNK_pipeHot_A TDTee232Hot TSCnr238Hot
0 20 20
EQUATIONS 2
TTS_K_SNK_pipeHot = [101,1] !Changed automatically
MTS_K_SNK_pipeHot = MTS_K_SNK_pipeHot_A
UNIT 102 TYPE 222 !Changed automatically
INPUTS 3
MSCnr238_QSnk243_A TSCnr238Hot TQSnk243H
0 20 20
EQUATIONS 2
TSCnr238_QSnk243 = [102,1] !Changed automatically
MSCnr238_QSnk243 = MSCnr238_QSnk243_A
UNIT 103 TYPE 222 !Changed automatically
INPUTS 3
MQSnk243_SCnr238_A TQSnk243H TSCnr238Cold
0 20 20
EQUATIONS 2
TQSnk243_SCnr238 = [103,1] !Changed automatically
MQSnk243_SCnr238 = MQSnk243_SCnr238_A
UNIT 104 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee253Cold_A
MDTee253Cold_B
MDTee253Cold_C
TTS_JCold
TTS_K_1Cold
TSeitenarm_VICold
0 0 0 20 20 20 
EQUATIONS 1
TDTee253Cold= [104,1] !Changed automatically
UNIT 105 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee253Hot_A
MDTee253Hot_B
MDTee253Hot_C
TTS_JHot
TTS_K_1Hot
TSeitenarm_VIHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee253Hot= [105,1] !Changed automatically
UNIT 106 TYPE 9511 !Changed automatically
PARAMETERS 36
85.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee253Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_K_1Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee232Cold ! ! Other side of pipe - cold pipe, deg C
TDTee232Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_K_1Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee253Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_K_1Cold = [106,1]   !Changed automatically
MTS_K_1Cold = MTS_K_1Cold_A  ! Outlet mass flow rate, kg/h
TTS_K_1Hot = [106,3]   !Changed automatically
MTS_K_1Hot = MTS_K_1Hot_A  ! Outlet mass flow rate, kg/h
TS_K_1ColdConv = [106,7]*-1*1/3600  !Changed automatically
TS_K_1ColdInt = [106,9]*1/3600  !Changed automatically
TS_K_1ColdDiss = [106,11]*1/3600  !Changed automatically
TS_K_1HotConv = [106,8]*-1*1/3600  !Changed automatically
TS_K_1HotInt = [106,10]*1/3600  !Changed automatically
TS_K_1HotDiss = [106,12]*1/3600  !Changed automatically
TS_K_1Exch = [106,13]*1/3600  !Changed automatically
TS_K_1GrSl = [106,14]*1/3600  !Changed automatically
TS_K_1SlFf = [106,15]*1/3600  !Changed automatically
TS_K_1SlInt = [106,16]*1/3600  !Changed automatically
UNIT 107 TYPE 222 !Changed automatically
INPUTS 3
MSCnr261Cold_A TSeitenarm_VICold TQSnk266_SCnr261
0 20 20
EQUATIONS 1
TSCnr261Cold = [107,1] !Changed automatically
UNIT 108 TYPE 222 !Changed automatically
INPUTS 3
MSCnr261Hot_A TSCnr261_QSnk266 TSeitenarm_VIHot
0 20 20
EQUATIONS 1
TSCnr261Hot = [108,1] !Changed automatically
UNIT 109 TYPE 9511 !Changed automatically
PARAMETERS 36
90.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TSCnr261Cold ! Inlet fluid temperature - cold pipe, deg C
MSeitenarm_VICold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee253Cold ! ! Other side of pipe - cold pipe, deg C
TDTee253Hot ! Inlet fluid temperature - hot pipe, deg C
MSeitenarm_VIHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TSCnr261Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TSeitenarm_VICold = [109,1]   !Changed automatically
MSeitenarm_VICold = MSeitenarm_VICold_A  ! Outlet mass flow rate, kg/h
TSeitenarm_VIHot = [109,3]   !Changed automatically
MSeitenarm_VIHot = MSeitenarm_VIHot_A  ! Outlet mass flow rate, kg/h
Seitenarm_VIColdConv = [109,7]*-1*1/3600  !Changed automatically
Seitenarm_VIColdInt = [109,9]*1/3600  !Changed automatically
Seitenarm_VIColdDiss = [109,11]*1/3600  !Changed automatically
Seitenarm_VIHotConv = [109,8]*-1*1/3600  !Changed automatically
Seitenarm_VIHotInt = [109,10]*1/3600  !Changed automatically
Seitenarm_VIHotDiss = [109,12]*1/3600  !Changed automatically
Seitenarm_VIExch = [109,13]*1/3600  !Changed automatically
Seitenarm_VIGrSl = [109,14]*1/3600  !Changed automatically
Seitenarm_VISlFf = [109,15]*1/3600  !Changed automatically
Seitenarm_VISlInt = [109,16]*1/3600  !Changed automatically
UNIT 110 TYPE 222 !Changed automatically
INPUTS 3
MSCnr200_QSnk191_A TSCnr200Hot TQSnk191H
0 20 20
EQUATIONS 2
TSCnr200_QSnk191 = [110,1] !Changed automatically
MSCnr200_QSnk191 = MSCnr200_QSnk191_A
UNIT 111 TYPE 222 !Changed automatically
INPUTS 3
MQSnk191_SCnr200_A TQSnk191H TSCnr200Cold
0 20 20
EQUATIONS 2
TQSnk191_SCnr200 = [111,1] !Changed automatically
MQSnk191_SCnr200 = MQSnk191_SCnr200_A
UNIT 112 TYPE 222 !Changed automatically
INPUTS 3
MSCnr220_QSnk225_A TSCnr220Hot TQSnk225H
0 20 20
EQUATIONS 2
TSCnr220_QSnk225 = [112,1] !Changed automatically
MSCnr220_QSnk225 = MSCnr220_QSnk225_A
UNIT 113 TYPE 222 !Changed automatically
INPUTS 3
MQSnk225_SCnr220_A TQSnk225H TSCnr220Cold
0 20 20
EQUATIONS 2
TQSnk225_SCnr220 = [113,1] !Changed automatically
MQSnk225_SCnr220 = MQSnk225_SCnr220_A
UNIT 114 TYPE 222 !Changed automatically
INPUTS 3
MSCnr261_QSnk266_A TSCnr261Hot TQSnk266H
0 20 20
EQUATIONS 2
TSCnr261_QSnk266 = [114,1] !Changed automatically
MSCnr261_QSnk266 = MSCnr261_QSnk266_A
UNIT 115 TYPE 222 !Changed automatically
INPUTS 3
MQSnk266_SCnr261_A TQSnk266H TSCnr261Cold
0 20 20
EQUATIONS 2
TQSnk266_SCnr261 = [115,1] !Changed automatically
MQSnk266_SCnr261 = MQSnk266_SCnr261_A
UNIT 116 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee315Cold_A
MDTee315Cold_B
MDTee315Cold_C
TTS_H_1Cold
TTS_GCold
TSeitenarm_IV_absch_1_1Cold
0 0 0 20 20 20 
EQUATIONS 1
TDTee315Cold= [116,1] !Changed automatically
UNIT 117 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee315Hot_A
MDTee315Hot_B
MDTee315Hot_C
TTS_H_1Hot
TTS_GHot
TSeitenarm_IV_absch_1_1Hot
0 0 0 20 20 20 
EQUATIONS 1
TDTee315Hot= [117,1] !Changed automatically
UNIT 118 TYPE 222 !Changed automatically
INPUTS 3
MDCnr319Hot_A TSeitenarm_IV_absch_1_2Hot TSeitenarm_IV_absch_2_1Hot
0 20 20
EQUATIONS 1
TDCnr319Hot = [118,1] !Changed automatically
UNIT 119 TYPE 222 !Changed automatically
INPUTS 3
MDCnr319Cold_A TSeitenarm_IV_absch_2_1Cold TSeitenarm_IV_absch_1_2Cold
0 20 20
EQUATIONS 1
TDCnr319Cold = [119,1] !Changed automatically
UNIT 120 TYPE 9511 !Changed automatically
PARAMETERS 36
136.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee315Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_GCold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDCnr74Cold ! ! Other side of pipe - cold pipe, deg C
TDCnr74Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_GHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee315Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_GCold = [120,1]   !Changed automatically
MTS_GCold = MTS_GCold_A  ! Outlet mass flow rate, kg/h
TTS_GHot = [120,3]   !Changed automatically
MTS_GHot = MTS_GHot_A  ! Outlet mass flow rate, kg/h
TS_GColdConv = [120,7]*-1*1/3600  !Changed automatically
TS_GColdInt = [120,9]*1/3600  !Changed automatically
TS_GColdDiss = [120,11]*1/3600  !Changed automatically
TS_GHotConv = [120,8]*-1*1/3600  !Changed automatically
TS_GHotInt = [120,10]*1/3600  !Changed automatically
TS_GHotDiss = [120,12]*1/3600  !Changed automatically
TS_GExch = [120,13]*1/3600  !Changed automatically
TS_GGrSl = [120,14]*1/3600  !Changed automatically
TS_GSlFf = [120,15]*1/3600  !Changed automatically
TS_GSlInt = [120,16]*1/3600  !Changed automatically
UNIT 121 TYPE 9511 !Changed automatically
PARAMETERS 36
107.5                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee213Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_H_1Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee315Cold ! ! Other side of pipe - cold pipe, deg C
TDTee315Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_H_1Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee213Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_H_1Cold = [121,1]   !Changed automatically
MTS_H_1Cold = MTS_H_1Cold_A  ! Outlet mass flow rate, kg/h
TTS_H_1Hot = [121,3]   !Changed automatically
MTS_H_1Hot = MTS_H_1Hot_A  ! Outlet mass flow rate, kg/h
TS_H_1ColdConv = [121,7]*-1*1/3600  !Changed automatically
TS_H_1ColdInt = [121,9]*1/3600  !Changed automatically
TS_H_1ColdDiss = [121,11]*1/3600  !Changed automatically
TS_H_1HotConv = [121,8]*-1*1/3600  !Changed automatically
TS_H_1HotInt = [121,10]*1/3600  !Changed automatically
TS_H_1HotDiss = [121,12]*1/3600  !Changed automatically
TS_H_1Exch = [121,13]*1/3600  !Changed automatically
TS_H_1GrSl = [121,14]*1/3600  !Changed automatically
TS_H_1SlFf = [121,15]*1/3600  !Changed automatically
TS_H_1SlInt = [121,16]*1/3600  !Changed automatically
UNIT 122 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee327Cold_A
MDTee327Cold_B
MDTee327Cold_C
TSeitenarm_IV_absch_1_2Cold
TSeitenarm_IV_absch_1_1Cold
TSeitenarm_IV_absch_1_SNKCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee327Cold= [122,1] !Changed automatically
UNIT 123 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee327Hot_A
MDTee327Hot_B
MDTee327Hot_C
TSeitenarm_IV_absch_1_2Hot
TSeitenarm_IV_absch_1_1Hot
TSeitenarm_IV_absch_1_SNKHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee327Hot= [123,1] !Changed automatically
UNIT 124 TYPE 222 !Changed automatically
INPUTS 3
MSCnr331Cold_A TSeitenarm_IV_absch_1_SNKCold TQSnk335_SCnr331
0 20 20
EQUATIONS 1
TSCnr331Cold = [124,1] !Changed automatically
UNIT 125 TYPE 222 !Changed automatically
INPUTS 3
MSCnr331Hot_A TSCnr331_QSnk335 TSeitenarm_IV_absch_1_SNKHot
0 20 20
EQUATIONS 1
TSCnr331Hot = [125,1] !Changed automatically
UNIT 126 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_1_1Cold_A TDTee327Cold TDTee315Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_1_1Cold = [126,1] !Changed automatically
MSeitenarm_IV_absch_1_1Cold = MSeitenarm_IV_absch_1_1Cold_A
UNIT 127 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_1_1Hot_A TDTee315Hot TDTee327Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_1_1Hot = [127,1] !Changed automatically
MSeitenarm_IV_absch_1_1Hot = MSeitenarm_IV_absch_1_1Hot_A
UNIT 128 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_1_SNKCold_A TSCnr331Cold TDTee327Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_1_SNKCold = [128,1] !Changed automatically
MSeitenarm_IV_absch_1_SNKCold = MSeitenarm_IV_absch_1_SNKCold_A
UNIT 129 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_1_SNKHot_A TDTee327Hot TSCnr331Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_1_SNKHot = [129,1] !Changed automatically
MSeitenarm_IV_absch_1_SNKHot = MSeitenarm_IV_absch_1_SNKHot_A
UNIT 130 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_1_2Cold_A TDCnr319Cold TDTee327Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_1_2Cold = [130,1] !Changed automatically
MSeitenarm_IV_absch_1_2Cold = MSeitenarm_IV_absch_1_2Cold_A
UNIT 131 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_1_2Hot_A TDTee327Hot TDCnr319Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_1_2Hot = [131,1] !Changed automatically
MSeitenarm_IV_absch_1_2Hot = MSeitenarm_IV_absch_1_2Hot_A
UNIT 132 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee343Cold_A
MDTee343Cold_B
MDTee343Cold_C
TSeitenarm_IV_absch_3_RCold
TSeitenarm_IV_absch_3_LCold
TSeitenarm_IV_absch_2_2Cold
0 0 0 20 20 20 
EQUATIONS 1
TDTee343Cold= [132,1] !Changed automatically
UNIT 133 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee343Hot_A
MDTee343Hot_B
MDTee343Hot_C
TSeitenarm_IV_absch_3_RHot
TSeitenarm_IV_absch_3_LHot
TSeitenarm_IV_absch_2_2Hot
0 0 0 20 20 20 
EQUATIONS 1
TDTee343Hot= [133,1] !Changed automatically
UNIT 134 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee347Cold_A
MDTee347Cold_B
MDTee347Cold_C
TSeitenarm_IV_absch_2_1Cold
TSeitenarm_IV_absch_2_2Cold
TSeitenarm_IV_absch_2_SNKCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee347Cold= [134,1] !Changed automatically
UNIT 135 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee347Hot_A
MDTee347Hot_B
MDTee347Hot_C
TSeitenarm_IV_absch_2_1Hot
TSeitenarm_IV_absch_2_2Hot
TSeitenarm_IV_absch_2_SNKHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee347Hot= [135,1] !Changed automatically
UNIT 136 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_2_1Cold_A TDTee347Cold TDCnr319Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_2_1Cold = [136,1] !Changed automatically
MSeitenarm_IV_absch_2_1Cold = MSeitenarm_IV_absch_2_1Cold_A
UNIT 137 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_2_1Hot_A TDCnr319Hot TDTee347Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_2_1Hot = [137,1] !Changed automatically
MSeitenarm_IV_absch_2_1Hot = MSeitenarm_IV_absch_2_1Hot_A
UNIT 138 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_2_2Cold_A TDTee343Cold TDTee347Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_2_2Cold = [138,1] !Changed automatically
MSeitenarm_IV_absch_2_2Cold = MSeitenarm_IV_absch_2_2Cold_A
UNIT 139 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_2_2Hot_A TDTee347Hot TDTee343Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_2_2Hot = [139,1] !Changed automatically
MSeitenarm_IV_absch_2_2Hot = MSeitenarm_IV_absch_2_2Hot_A
UNIT 140 TYPE 222 !Changed automatically
INPUTS 3
MSCnr353Cold_A TSeitenarm_IV_absch_2_SNKCold TQSnk358_SCnr353
0 20 20
EQUATIONS 1
TSCnr353Cold = [140,1] !Changed automatically
UNIT 141 TYPE 222 !Changed automatically
INPUTS 3
MSCnr353Hot_A TSCnr353_QSnk358 TSeitenarm_IV_absch_2_SNKHot
0 20 20
EQUATIONS 1
TSCnr353Hot = [141,1] !Changed automatically
UNIT 142 TYPE 222 !Changed automatically
INPUTS 3
MSCnr363Cold_A TSeitenarm_IV_absch_3_RCold TQSnk322_SCnr363
0 20 20
EQUATIONS 1
TSCnr363Cold = [142,1] !Changed automatically
UNIT 143 TYPE 222 !Changed automatically
INPUTS 3
MSCnr363Hot_A TSCnr363_QSnk322 TSeitenarm_IV_absch_3_RHot
0 20 20
EQUATIONS 1
TSCnr363Hot = [143,1] !Changed automatically
UNIT 144 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_3_RCold_A TSCnr363Cold TDTee343Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_3_RCold = [144,1] !Changed automatically
MSeitenarm_IV_absch_3_RCold = MSeitenarm_IV_absch_3_RCold_A
UNIT 145 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_3_RHot_A TDTee343Hot TSCnr363Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_3_RHot = [145,1] !Changed automatically
MSeitenarm_IV_absch_3_RHot = MSeitenarm_IV_absch_3_RHot_A
UNIT 146 TYPE 222 !Changed automatically
INPUTS 3
MSCnr370Cold_A TSeitenarm_IV_absch_3_LCold TQSnk375_SCnr370
0 20 20
EQUATIONS 1
TSCnr370Cold = [146,1] !Changed automatically
UNIT 147 TYPE 222 !Changed automatically
INPUTS 3
MSCnr370Hot_A TSCnr370_QSnk375 TSeitenarm_IV_absch_3_LHot
0 20 20
EQUATIONS 1
TSCnr370Hot = [147,1] !Changed automatically
UNIT 148 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_3_LCold_A TSCnr370Cold TDTee343Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_3_LCold = [148,1] !Changed automatically
MSeitenarm_IV_absch_3_LCold = MSeitenarm_IV_absch_3_LCold_A
UNIT 149 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_3_LHot_A TDTee343Hot TSCnr370Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_3_LHot = [149,1] !Changed automatically
MSeitenarm_IV_absch_3_LHot = MSeitenarm_IV_absch_3_LHot_A
UNIT 150 TYPE 222 !Changed automatically
INPUTS 3
MSCnr331_QSnk335_A TSCnr331Hot TQSnk335H
0 20 20
EQUATIONS 2
TSCnr331_QSnk335 = [150,1] !Changed automatically
MSCnr331_QSnk335 = MSCnr331_QSnk335_A
UNIT 151 TYPE 222 !Changed automatically
INPUTS 3
MQSnk335_SCnr331_A TQSnk335H TSCnr331Cold
0 20 20
EQUATIONS 2
TQSnk335_SCnr331 = [151,1] !Changed automatically
MQSnk335_SCnr331 = MQSnk335_SCnr331_A
UNIT 152 TYPE 222 !Changed automatically
INPUTS 3
MSCnr353_QSnk358_A TSCnr353Hot TQSnk358H
0 20 20
EQUATIONS 2
TSCnr353_QSnk358 = [152,1] !Changed automatically
MSCnr353_QSnk358 = MSCnr353_QSnk358_A
UNIT 153 TYPE 222 !Changed automatically
INPUTS 3
MQSnk358_SCnr353_A TQSnk358H TSCnr353Cold
0 20 20
EQUATIONS 2
TQSnk358_SCnr353 = [153,1] !Changed automatically
MQSnk358_SCnr353 = MQSnk358_SCnr353_A
UNIT 154 TYPE 222 !Changed automatically
INPUTS 3
MSCnr363_QSnk322_A TSCnr363Hot TQSnk322H
0 20 20
EQUATIONS 2
TSCnr363_QSnk322 = [154,1] !Changed automatically
MSCnr363_QSnk322 = MSCnr363_QSnk322_A
UNIT 155 TYPE 222 !Changed automatically
INPUTS 3
MQSnk322_SCnr363_A TQSnk322H TSCnr363Cold
0 20 20
EQUATIONS 2
TQSnk322_SCnr363 = [155,1] !Changed automatically
MQSnk322_SCnr363 = MQSnk322_SCnr363_A
UNIT 156 TYPE 222 !Changed automatically
INPUTS 3
MSCnr370_QSnk375_A TSCnr370Hot TQSnk375H
0 20 20
EQUATIONS 2
TSCnr370_QSnk375 = [156,1] !Changed automatically
MSCnr370_QSnk375 = MSCnr370_QSnk375_A
UNIT 157 TYPE 222 !Changed automatically
INPUTS 3
MQSnk375_SCnr370_A TQSnk375H TSCnr370Cold
0 20 20
EQUATIONS 2
TQSnk375_SCnr370 = [157,1] !Changed automatically
MQSnk375_SCnr370 = MQSnk375_SCnr370_A
UNIT 158 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_2_SNKCold_A TSCnr353Cold TDTee347Cold
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_2_SNKCold = [158,1] !Changed automatically
MSeitenarm_IV_absch_2_SNKCold = MSeitenarm_IV_absch_2_SNKCold_A
UNIT 159 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_IV_absch_2_SNKHot_A TDTee347Hot TSCnr353Hot
0 20 20
EQUATIONS 2
TSeitenarm_IV_absch_2_SNKHot = [159,1] !Changed automatically
MSeitenarm_IV_absch_2_SNKHot = MSeitenarm_IV_absch_2_SNKHot_A
UNIT 160 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee405Cold_A
MDTee405Cold_B
MDTee405Cold_C
TSeitenarm_VIIICold
TTS_K_2Cold
TSeitenarm_VIICold
0 0 0 20 20 20 
EQUATIONS 1
TDTee405Cold= [160,1] !Changed automatically
UNIT 161 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee405Hot_A
MDTee405Hot_B
MDTee405Hot_C
TSeitenarm_VIIIHot
TTS_K_2Hot
TSeitenarm_VIIHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee405Hot= [161,1] !Changed automatically
UNIT 162 TYPE 9511 !Changed automatically
PARAMETERS 36
85.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee405Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_K_2Cold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee232Cold ! ! Other side of pipe - cold pipe, deg C
TDTee232Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_K_2Hot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee405Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_K_2Cold = [162,1]   !Changed automatically
MTS_K_2Cold = MTS_K_2Cold_A  ! Outlet mass flow rate, kg/h
TTS_K_2Hot = [162,3]   !Changed automatically
MTS_K_2Hot = MTS_K_2Hot_A  ! Outlet mass flow rate, kg/h
TS_K_2ColdConv = [162,7]*-1*1/3600  !Changed automatically
TS_K_2ColdInt = [162,9]*1/3600  !Changed automatically
TS_K_2ColdDiss = [162,11]*1/3600  !Changed automatically
TS_K_2HotConv = [162,8]*-1*1/3600  !Changed automatically
TS_K_2HotInt = [162,10]*1/3600  !Changed automatically
TS_K_2HotDiss = [162,12]*1/3600  !Changed automatically
TS_K_2Exch = [162,13]*1/3600  !Changed automatically
TS_K_2GrSl = [162,14]*1/3600  !Changed automatically
TS_K_2SlFf = [162,15]*1/3600  !Changed automatically
TS_K_2SlInt = [162,16]*1/3600  !Changed automatically
UNIT 163 TYPE 9511 !Changed automatically
PARAMETERS 36
145.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TSCnr126Cold ! Inlet fluid temperature - cold pipe, deg C
MSeitenarm_VIIICold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee405Cold ! ! Other side of pipe - cold pipe, deg C
TDTee405Hot ! Inlet fluid temperature - hot pipe, deg C
MSeitenarm_VIIIHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TSCnr126Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TSeitenarm_VIIICold = [163,1]   !Changed automatically
MSeitenarm_VIIICold = MSeitenarm_VIIICold_A  ! Outlet mass flow rate, kg/h
TSeitenarm_VIIIHot = [163,3]   !Changed automatically
MSeitenarm_VIIIHot = MSeitenarm_VIIIHot_A  ! Outlet mass flow rate, kg/h
Seitenarm_VIIIColdConv = [163,7]*-1*1/3600  !Changed automatically
Seitenarm_VIIIColdInt = [163,9]*1/3600  !Changed automatically
Seitenarm_VIIIColdDiss = [163,11]*1/3600  !Changed automatically
Seitenarm_VIIIHotConv = [163,8]*-1*1/3600  !Changed automatically
Seitenarm_VIIIHotInt = [163,10]*1/3600  !Changed automatically
Seitenarm_VIIIHotDiss = [163,12]*1/3600  !Changed automatically
Seitenarm_VIIIExch = [163,13]*1/3600  !Changed automatically
Seitenarm_VIIIGrSl = [163,14]*1/3600  !Changed automatically
Seitenarm_VIIISlFf = [163,15]*1/3600  !Changed automatically
Seitenarm_VIIISlInt = [163,16]*1/3600  !Changed automatically
UNIT 164 TYPE 222 !Changed automatically
INPUTS 3
MSCnr412Cold_A TSeitenarm_VIICold TQSnk417_SCnr412
0 20 20
EQUATIONS 1
TSCnr412Cold = [164,1] !Changed automatically
UNIT 165 TYPE 222 !Changed automatically
INPUTS 3
MSCnr412Hot_A TSCnr412_QSnk417 TSeitenarm_VIIHot
0 20 20
EQUATIONS 1
TSCnr412Hot = [165,1] !Changed automatically
UNIT 166 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_VIICold_A TSCnr412Cold TDTee405Cold
0 20 20
EQUATIONS 2
TSeitenarm_VIICold = [166,1] !Changed automatically
MSeitenarm_VIICold = MSeitenarm_VIICold_A
UNIT 167 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_VIIHot_A TDTee405Hot TSCnr412Hot
0 20 20
EQUATIONS 2
TSeitenarm_VIIHot = [167,1] !Changed automatically
MSeitenarm_VIIHot = MSeitenarm_VIIHot_A
UNIT 168 TYPE 222 !Changed automatically
INPUTS 3
MSCnr412_QSnk417_A TSCnr412Hot TQSnk417H
0 20 20
EQUATIONS 2
TSCnr412_QSnk417 = [168,1] !Changed automatically
MSCnr412_QSnk417 = MSCnr412_QSnk417_A
UNIT 169 TYPE 222 !Changed automatically
INPUTS 3
MQSnk417_SCnr412_A TQSnk417H TSCnr412Cold
0 20 20
EQUATIONS 2
TQSnk417_SCnr412 = [169,1] !Changed automatically
MQSnk417_SCnr412 = MQSnk417_SCnr412_A
UNIT 170 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee424Cold_A
MDTee424Cold_B
MDTee424Cold_C
TTS_JCold
TTS_ICold
TSeitenarm_V_1_1Cold
0 0 0 20 20 20 
EQUATIONS 1
TDTee424Cold= [170,1] !Changed automatically
UNIT 171 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee424Hot_A
MDTee424Hot_B
MDTee424Hot_C
TTS_JHot
TTS_IHot
TSeitenarm_V_1_1Hot
0 0 0 20 20 20 
EQUATIONS 1
TDTee424Hot= [171,1] !Changed automatically
UNIT 172 TYPE 9511 !Changed automatically
PARAMETERS 36
156.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee424Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_ICold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDCnr110Cold ! ! Other side of pipe - cold pipe, deg C
TDCnr110Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_IHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee424Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_ICold = [172,1]   !Changed automatically
MTS_ICold = MTS_ICold_A  ! Outlet mass flow rate, kg/h
TTS_IHot = [172,3]   !Changed automatically
MTS_IHot = MTS_IHot_A  ! Outlet mass flow rate, kg/h
TS_IColdConv = [172,7]*-1*1/3600  !Changed automatically
TS_IColdInt = [172,9]*1/3600  !Changed automatically
TS_IColdDiss = [172,11]*1/3600  !Changed automatically
TS_IHotConv = [172,8]*-1*1/3600  !Changed automatically
TS_IHotInt = [172,10]*1/3600  !Changed automatically
TS_IHotDiss = [172,12]*1/3600  !Changed automatically
TS_IExch = [172,13]*1/3600  !Changed automatically
TS_IGrSl = [172,14]*1/3600  !Changed automatically
TS_ISlFf = [172,15]*1/3600  !Changed automatically
TS_ISlInt = [172,16]*1/3600  !Changed automatically
UNIT 173 TYPE 9511 !Changed automatically
PARAMETERS 36
40.0                                ! Length of buried pipe, m
dpDiamIn                                ! Inner diameter of pipes, m
dpDiamOut                               ! Outer diameter of pipes, m
dpLambda                                ! Thermal conductivity of pipe material, kJ/(h*m*K)
dpDepth                                 ! Buried pipe depth, m
dpDiamCase                              ! Diameter of casing material, m
dpLambdaFill                            ! Thermal conductivity of fill insulation, kJ/(h*m*K)
dpDistPtoP                              ! Center-to-center pipe spacing, m
dpLambdaGap                             ! Thermal conductivity of gap material, kJ/(h*m*K)
dpGapThick                              ! Gap thickness, m
dpRhoFlu                                ! Density of fluid, kg/m^3
dpLambdaFl                              ! Thermal conductivity of fluid, kJ/(h*m*K)
dpCpFl                                  ! Specific heat of fluid, kJ/(kg*K)
dpViscFl                                ! Viscosity of fluid, kg/(m*h)
dpTIniCold                              ! Initial fluid temperature - Pipe cold, deg C
dpTIniHot                               ! Initial fluid temperature - Pipe hot, deg C
dpLamdaSl                               ! Thermal conductivity of soil, kJ/(h*m*K)
dpRhoSl                                 ! Density of soil, kg/m^3
dpCpSl                                  ! Specific heat of soil, kJ/(kg*K)
TambAvg                                 ! Average surface temperature, deg C
dTambAmpl                               ! Amplitude of surface temperature, deg C
ddTcwOffset                             ! Days of minimum surface temperature
dpNrFlNds                               ! Number of fluid nodes
dpNrSlRad                               ! Number of radial soil nodes
dpNrSlAx                                ! Number of axial soil nodes
dpNrSlCirc                              ! Number of circumferential soil nodes
dpRadNdDist                             ! Radial distance of node 1, m
dpRadNdDist                             ! Radial distance of node 2, m
dpRadNdDist                             ! Radial distance of node 3, m
dpRadNdDist                             ! Radial distance of node 4, m
dpRadNdDist                             ! Radial distance of node 5, m
dpRadNdDist                             ! Radial distance of node 6, m
dpRadNdDist                             ! Radial distance of node 7, m
dpRadNdDist                             ! Radial distance of node 8, m
dpRadNdDist                             ! Radial distance of node 9, m
dpRadNdDist                             ! Radial distance of node 10, m
INPUTS 6
TDTee253Cold ! Inlet fluid temperature - cold pipe, deg C
MTS_JCold_A ! Inlet fluid flow rate - cold pipe, kg/h
TDTee424Cold ! ! Other side of pipe - cold pipe, deg C
TDTee424Hot ! Inlet fluid temperature - hot pipe, deg C
MTS_JHot_A ! Inlet fluid flow rate - hot pipe, kg/h
TDTee253Hot ! ! Other side of pipe - hot pipe, deg C
dpTIniCold
0
dpTIniCold
dpTIniHot
0
dpTIniHot
EQUATIONS 14
TTS_JCold = [173,1]   !Changed automatically
MTS_JCold = MTS_JCold_A  ! Outlet mass flow rate, kg/h
TTS_JHot = [173,3]   !Changed automatically
MTS_JHot = MTS_JHot_A  ! Outlet mass flow rate, kg/h
TS_JColdConv = [173,7]*-1*1/3600  !Changed automatically
TS_JColdInt = [173,9]*1/3600  !Changed automatically
TS_JColdDiss = [173,11]*1/3600  !Changed automatically
TS_JHotConv = [173,8]*-1*1/3600  !Changed automatically
TS_JHotInt = [173,10]*1/3600  !Changed automatically
TS_JHotDiss = [173,12]*1/3600  !Changed automatically
TS_JExch = [173,13]*1/3600  !Changed automatically
TS_JGrSl = [173,14]*1/3600  !Changed automatically
TS_JSlFf = [173,15]*1/3600  !Changed automatically
TS_JSlInt = [173,16]*1/3600  !Changed automatically
UNIT 174 TYPE 222 !Changed automatically
INPUTS 3
MDCnr430Hot_A TSeitenarm_V_1_2_1Hot TSeitenarm_V_1_1Hot
0 20 20
EQUATIONS 1
TDCnr430Hot = [174,1] !Changed automatically
UNIT 175 TYPE 222 !Changed automatically
INPUTS 3
MDCnr430Cold_A TSeitenarm_V_1_1Cold TSeitenarm_V_1_2_1Cold
0 20 20
EQUATIONS 1
TDCnr430Cold = [175,1] !Changed automatically
UNIT 176 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_1Cold_A TDCnr430Cold TDTee424Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_1_1Cold = [176,1] !Changed automatically
MSeitenarm_V_1_1Cold = MSeitenarm_V_1_1Cold_A
UNIT 177 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_1Hot_A TDTee424Hot TDCnr430Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_1_1Hot = [177,1] !Changed automatically
MSeitenarm_V_1_1Hot = MSeitenarm_V_1_1Hot_A
UNIT 178 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee434Cold_A
MDTee434Cold_B
MDTee434Cold_C
TSeitenarm_V_1_2_1Cold
TSeitenarm_V_1_2_2Cold
TSeitenarm_V_1_2_SNKCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee434Cold= [178,1] !Changed automatically
UNIT 179 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee434Hot_A
MDTee434Hot_B
MDTee434Hot_C
TSeitenarm_V_1_2_1Hot
TSeitenarm_V_1_2_2Hot
TSeitenarm_V_1_2_SNKHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee434Hot= [179,1] !Changed automatically
UNIT 180 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_2_1Cold_A TDTee434Cold TDCnr430Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_1_2_1Cold = [180,1] !Changed automatically
MSeitenarm_V_1_2_1Cold = MSeitenarm_V_1_2_1Cold_A
UNIT 181 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_2_1Hot_A TDCnr430Hot TDTee434Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_1_2_1Hot = [181,1] !Changed automatically
MSeitenarm_V_1_2_1Hot = MSeitenarm_V_1_2_1Hot_A
UNIT 182 TYPE 222 !Changed automatically
INPUTS 3
MDCnr439Hot_A TSeitenarm_V_1_2_2Hot TSeitenarm_V_2_1Hot
0 20 20
EQUATIONS 1
TDCnr439Hot = [182,1] !Changed automatically
UNIT 183 TYPE 222 !Changed automatically
INPUTS 3
MDCnr439Cold_A TSeitenarm_V_2_1Cold TSeitenarm_V_1_2_2Cold
0 20 20
EQUATIONS 1
TDCnr439Cold = [183,1] !Changed automatically
UNIT 184 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_2_2Cold_A TDCnr439Cold TDTee434Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_1_2_2Cold = [184,1] !Changed automatically
MSeitenarm_V_1_2_2Cold = MSeitenarm_V_1_2_2Cold_A
UNIT 185 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_2_2Hot_A TDTee434Hot TDCnr439Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_1_2_2Hot = [185,1] !Changed automatically
MSeitenarm_V_1_2_2Hot = MSeitenarm_V_1_2_2Hot_A
UNIT 186 TYPE 222 !Changed automatically
INPUTS 3
MSCnr443Cold_A TSeitenarm_V_1_2_SNKCold TQSnk448_SCnr443
0 20 20
EQUATIONS 1
TSCnr443Cold = [186,1] !Changed automatically
UNIT 187 TYPE 222 !Changed automatically
INPUTS 3
MSCnr443Hot_A TSCnr443_QSnk448 TSeitenarm_V_1_2_SNKHot
0 20 20
EQUATIONS 1
TSCnr443Hot = [187,1] !Changed automatically
UNIT 188 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_2_SNKCold_A TSCnr443Cold TDTee434Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_1_2_SNKCold = [188,1] !Changed automatically
MSeitenarm_V_1_2_SNKCold = MSeitenarm_V_1_2_SNKCold_A
UNIT 189 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_1_2_SNKHot_A TDTee434Hot TSCnr443Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_1_2_SNKHot = [189,1] !Changed automatically
MSeitenarm_V_1_2_SNKHot = MSeitenarm_V_1_2_SNKHot_A
UNIT 190 TYPE 222 !Changed automatically
INPUTS 3
MSCnr443_QSnk448_A TSCnr443Hot TQSnk448H
0 20 20
EQUATIONS 2
TSCnr443_QSnk448 = [190,1] !Changed automatically
MSCnr443_QSnk448 = MSCnr443_QSnk448_A
UNIT 191 TYPE 222 !Changed automatically
INPUTS 3
MQSnk448_SCnr443_A TQSnk448H TSCnr443Cold
0 20 20
EQUATIONS 2
TQSnk448_SCnr443 = [191,1] !Changed automatically
MQSnk448_SCnr443 = MQSnk448_SCnr443_A
UNIT 192 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee455Cold_A
MDTee455Cold_B
MDTee455Cold_C
TSeitenarm_V_2_2Cold
TSeitenarm_V_2_1Cold
TSeitenarm_V_2_SNKCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee455Cold= [192,1] !Changed automatically
UNIT 193 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee455Hot_A
MDTee455Hot_B
MDTee455Hot_C
TSeitenarm_V_2_2Hot
TSeitenarm_V_2_1Hot
TSeitenarm_V_2_SNKHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee455Hot= [193,1] !Changed automatically
UNIT 194 TYPE 222 !Changed automatically
INPUTS 3
MDCnr459Hot_A TSeitenarm_V_3_1Hot TSeitenarm_V_2_2Hot
0 20 20
EQUATIONS 1
TDCnr459Hot = [194,1] !Changed automatically
UNIT 195 TYPE 222 !Changed automatically
INPUTS 3
MDCnr459Cold_A TSeitenarm_V_2_2Cold TSeitenarm_V_3_1Cold
0 20 20
EQUATIONS 1
TDCnr459Cold = [195,1] !Changed automatically
UNIT 196 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_2_1Cold_A TDTee455Cold TDCnr439Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_2_1Cold = [196,1] !Changed automatically
MSeitenarm_V_2_1Cold = MSeitenarm_V_2_1Cold_A
UNIT 197 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_2_1Hot_A TDCnr439Hot TDTee455Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_2_1Hot = [197,1] !Changed automatically
MSeitenarm_V_2_1Hot = MSeitenarm_V_2_1Hot_A
UNIT 198 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_2_2Cold_A TDCnr459Cold TDTee455Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_2_2Cold = [198,1] !Changed automatically
MSeitenarm_V_2_2Cold = MSeitenarm_V_2_2Cold_A
UNIT 199 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_2_2Hot_A TDTee455Hot TDCnr459Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_2_2Hot = [199,1] !Changed automatically
MSeitenarm_V_2_2Hot = MSeitenarm_V_2_2Hot_A
UNIT 200 TYPE 222 !Changed automatically
INPUTS 3
MSCnr464Cold_A TSeitenarm_V_2_SNKCold TQSnk469_SCnr464
0 20 20
EQUATIONS 1
TSCnr464Cold = [200,1] !Changed automatically
UNIT 201 TYPE 222 !Changed automatically
INPUTS 3
MSCnr464Hot_A TSCnr464_QSnk469 TSeitenarm_V_2_SNKHot
0 20 20
EQUATIONS 1
TSCnr464Hot = [201,1] !Changed automatically
UNIT 202 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_2_SNKCold_A TSCnr464Cold TDTee455Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_2_SNKCold = [202,1] !Changed automatically
MSeitenarm_V_2_SNKCold = MSeitenarm_V_2_SNKCold_A
UNIT 203 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_2_SNKHot_A TDTee455Hot TSCnr464Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_2_SNKHot = [203,1] !Changed automatically
MSeitenarm_V_2_SNKHot = MSeitenarm_V_2_SNKHot_A
UNIT 204 TYPE 222 !Changed automatically
INPUTS 3
MSCnr464_QSnk469_A TSCnr464Hot TQSnk469H
0 20 20
EQUATIONS 2
TSCnr464_QSnk469 = [204,1] !Changed automatically
MSCnr464_QSnk469 = MSCnr464_QSnk469_A
UNIT 205 TYPE 222 !Changed automatically
INPUTS 3
MQSnk469_SCnr464_A TQSnk469H TSCnr464Cold
0 20 20
EQUATIONS 2
TQSnk469_SCnr464 = [205,1] !Changed automatically
MQSnk469_SCnr464 = MQSnk469_SCnr464_A
UNIT 206 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee474Cold_A
MDTee474Cold_B
MDTee474Cold_C
TSeitenarm_V_3_1Cold
TSeitenarm_V_3_2Cold
TSeitenarm_V_3_SNKCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee474Cold= [206,1] !Changed automatically
UNIT 207 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee474Hot_A
MDTee474Hot_B
MDTee474Hot_C
TSeitenarm_V_3_1Hot
TSeitenarm_V_3_2Hot
TSeitenarm_V_3_SNKHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee474Hot= [207,1] !Changed automatically
UNIT 208 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_3_1Cold_A TDTee474Cold TDCnr459Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_3_1Cold = [208,1] !Changed automatically
MSeitenarm_V_3_1Cold = MSeitenarm_V_3_1Cold_A
UNIT 209 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_3_1Hot_A TDCnr459Hot TDTee474Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_3_1Hot = [209,1] !Changed automatically
MSeitenarm_V_3_1Hot = MSeitenarm_V_3_1Hot_A
UNIT 210 TYPE 222 !Changed automatically
INPUTS 3
MDCnr479Hot_A TSeitenarm_V_4_1Hot TSeitenarm_V_3_2Hot
0 20 20
EQUATIONS 1
TDCnr479Hot = [210,1] !Changed automatically
UNIT 211 TYPE 222 !Changed automatically
INPUTS 3
MDCnr479Cold_A TSeitenarm_V_3_2Cold TSeitenarm_V_4_1Cold
0 20 20
EQUATIONS 1
TDCnr479Cold = [211,1] !Changed automatically
UNIT 212 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_3_2Cold_A TDCnr479Cold TDTee474Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_3_2Cold = [212,1] !Changed automatically
MSeitenarm_V_3_2Cold = MSeitenarm_V_3_2Cold_A
UNIT 213 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_3_2Hot_A TDTee474Hot TDCnr479Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_3_2Hot = [213,1] !Changed automatically
MSeitenarm_V_3_2Hot = MSeitenarm_V_3_2Hot_A
UNIT 214 TYPE 222 !Changed automatically
INPUTS 3
MSCnr483Cold_A TSeitenarm_V_3_SNKCold TQSnk488_SCnr483
0 20 20
EQUATIONS 1
TSCnr483Cold = [214,1] !Changed automatically
UNIT 215 TYPE 222 !Changed automatically
INPUTS 3
MSCnr483Hot_A TSCnr483_QSnk488 TSeitenarm_V_3_SNKHot
0 20 20
EQUATIONS 1
TSCnr483Hot = [215,1] !Changed automatically
UNIT 216 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_3_SNKCold_A TSCnr483Cold TDTee474Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_3_SNKCold = [216,1] !Changed automatically
MSeitenarm_V_3_SNKCold = MSeitenarm_V_3_SNKCold_A
UNIT 217 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_3_SNKHot_A TDTee474Hot TSCnr483Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_3_SNKHot = [217,1] !Changed automatically
MSeitenarm_V_3_SNKHot = MSeitenarm_V_3_SNKHot_A
UNIT 218 TYPE 222 !Changed automatically
INPUTS 3
MSCnr483_QSnk488_A TSCnr483Hot TQSnk488H
0 20 20
EQUATIONS 2
TSCnr483_QSnk488 = [218,1] !Changed automatically
MSCnr483_QSnk488 = MSCnr483_QSnk488_A
UNIT 219 TYPE 222 !Changed automatically
INPUTS 3
MQSnk488_SCnr483_A TQSnk488H TSCnr483Cold
0 20 20
EQUATIONS 2
TQSnk488_SCnr483 = [219,1] !Changed automatically
MQSnk488_SCnr483 = MQSnk488_SCnr483_A
UNIT 220 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee493Cold_A
MDTee493Cold_B
MDTee493Cold_C
TSeitenarm_V_4_1Cold
TDTee493_DTee512Cold
TU_1Cold
0 0 0 20 20 20 
EQUATIONS 1
TDTee493Cold= [220,1] !Changed automatically
UNIT 221 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee493Hot_A
MDTee493Hot_B
MDTee493Hot_C
TSeitenarm_V_4_1Hot
TDTee493_DTee512Hot
TU_1Hot
0 0 0 20 20 20 
EQUATIONS 1
TDTee493Hot= [221,1] !Changed automatically
UNIT 222 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_1Cold_A TDTee493Cold TDCnr479Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_4_1Cold = [222,1] !Changed automatically
MSeitenarm_V_4_1Cold = MSeitenarm_V_4_1Cold_A
UNIT 223 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_1Hot_A TDCnr479Hot TDTee493Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_4_1Hot = [223,1] !Changed automatically
MSeitenarm_V_4_1Hot = MSeitenarm_V_4_1Hot_A
UNIT 224 TYPE 222 !Changed automatically
INPUTS 3
MSCnr498Cold_A TU_1Cold TQSnk503_SCnr498
0 20 20
EQUATIONS 1
TSCnr498Cold = [224,1] !Changed automatically
UNIT 225 TYPE 222 !Changed automatically
INPUTS 3
MSCnr498Hot_A TSCnr498_QSnk503 TU_1Hot
0 20 20
EQUATIONS 1
TSCnr498Hot = [225,1] !Changed automatically
UNIT 226 TYPE 222 !Changed automatically
INPUTS 3
MU_1Cold_A TSCnr498Cold TDTee493Cold
0 20 20
EQUATIONS 2
TU_1Cold = [226,1] !Changed automatically
MU_1Cold = MU_1Cold_A
UNIT 227 TYPE 222 !Changed automatically
INPUTS 3
MU_1Hot_A TDTee493Hot TSCnr498Hot
0 20 20
EQUATIONS 2
TU_1Hot = [227,1] !Changed automatically
MU_1Hot = MU_1Hot_A
UNIT 228 TYPE 222 !Changed automatically
INPUTS 3
MSCnr498_QSnk503_A TSCnr498Hot TQSnk503H
0 20 20
EQUATIONS 2
TSCnr498_QSnk503 = [228,1] !Changed automatically
MSCnr498_QSnk503 = MSCnr498_QSnk503_A
UNIT 229 TYPE 222 !Changed automatically
INPUTS 3
MQSnk503_SCnr498_A TQSnk503H TSCnr498Cold
0 20 20
EQUATIONS 2
TQSnk503_SCnr498 = [229,1] !Changed automatically
MQSnk503_SCnr498 = MQSnk503_SCnr498_A
UNIT 230 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee508Cold_A
MDTee508Cold_B
MDTee508Cold_C
TSeitenarm_V_5_2Cold
TSeitenarm_V_6Cold
TU_3Cold
0 0 0 20 20 20 
EQUATIONS 1
TDTee508Cold= [230,1] !Changed automatically
UNIT 231 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee508Hot_A
MDTee508Hot_B
MDTee508Hot_C
TSeitenarm_V_5_2Hot
TSeitenarm_V_6Hot
TU_3Hot
0 0 0 20 20 20 
EQUATIONS 1
TDTee508Hot= [231,1] !Changed automatically
UNIT 232 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee512Cold_A
MDTee512Cold_B
MDTee512Cold_C
TDTee493_DTee512Cold
TSeitenarm_V_4_2Cold
TU_2Cold
0 0 0 20 20 20 
EQUATIONS 1
TDTee512Cold= [232,1] !Changed automatically
UNIT 233 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee512Hot_A
MDTee512Hot_B
MDTee512Hot_C
TDTee493_DTee512Hot
TSeitenarm_V_4_2Hot
TU_2Hot
0 0 0 20 20 20 
EQUATIONS 1
TDTee512Hot= [233,1] !Changed automatically
UNIT 234 TYPE 222 !Changed automatically
INPUTS 3
MDTee493_DTee512Cold_A TDTee512Cold TDTee493Cold
0 20 20
EQUATIONS 2
TDTee493_DTee512Cold = [234,1] !Changed automatically
MDTee493_DTee512Cold = MDTee493_DTee512Cold_A
UNIT 235 TYPE 222 !Changed automatically
INPUTS 3
MDTee493_DTee512Hot_A TDTee493Hot TDTee512Hot
0 20 20
EQUATIONS 2
TDTee493_DTee512Hot = [235,1] !Changed automatically
MDTee493_DTee512Hot = MDTee493_DTee512Hot_A
UNIT 236 TYPE 222 !Changed automatically
INPUTS 3
MSCnr517Cold_A TU_2Cold TQSnk524_SCnr517
0 20 20
EQUATIONS 1
TSCnr517Cold = [236,1] !Changed automatically
UNIT 237 TYPE 222 !Changed automatically
INPUTS 3
MSCnr517Hot_A TSCnr517_QSnk524 TU_2Hot
0 20 20
EQUATIONS 1
TSCnr517Hot = [237,1] !Changed automatically
UNIT 238 TYPE 222 !Changed automatically
INPUTS 3
MU_2Cold_A TSCnr517Cold TDTee512Cold
0 20 20
EQUATIONS 2
TU_2Cold = [238,1] !Changed automatically
MU_2Cold = MU_2Cold_A
UNIT 239 TYPE 222 !Changed automatically
INPUTS 3
MU_2Hot_A TDTee512Hot TSCnr517Hot
0 20 20
EQUATIONS 2
TU_2Hot = [239,1] !Changed automatically
MU_2Hot = MU_2Hot_A
UNIT 240 TYPE 222 !Changed automatically
INPUTS 3
MSCnr517_QSnk524_A TSCnr517Hot TQSnk524H
0 20 20
EQUATIONS 2
TSCnr517_QSnk524 = [240,1] !Changed automatically
MSCnr517_QSnk524 = MSCnr517_QSnk524_A
UNIT 241 TYPE 222 !Changed automatically
INPUTS 3
MQSnk524_SCnr517_A TQSnk524H TSCnr517Cold
0 20 20
EQUATIONS 2
TQSnk524_SCnr517 = [241,1] !Changed automatically
MQSnk524_SCnr517 = MQSnk524_SCnr517_A
UNIT 242 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee529Cold_A
MDTee529Cold_B
MDTee529Cold_C
TSeitenarm_V_4_3Cold
TSeitenarm_V_4_2Cold
TSeitenarm_V_4_SNKCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee529Cold= [242,1] !Changed automatically
UNIT 243 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee529Hot_A
MDTee529Hot_B
MDTee529Hot_C
TSeitenarm_V_4_3Hot
TSeitenarm_V_4_2Hot
TSeitenarm_V_4_SNKHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee529Hot= [243,1] !Changed automatically
UNIT 244 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_2Cold_A TDTee529Cold TDTee512Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_4_2Cold = [244,1] !Changed automatically
MSeitenarm_V_4_2Cold = MSeitenarm_V_4_2Cold_A
UNIT 245 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_2Hot_A TDTee512Hot TDTee529Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_4_2Hot = [245,1] !Changed automatically
MSeitenarm_V_4_2Hot = MSeitenarm_V_4_2Hot_A
UNIT 246 TYPE 222 !Changed automatically
INPUTS 3
MSCnr534Cold_A TSeitenarm_V_4_SNKCold TQSnk539_SCnr534
0 20 20
EQUATIONS 1
TSCnr534Cold = [246,1] !Changed automatically
UNIT 247 TYPE 222 !Changed automatically
INPUTS 3
MSCnr534Hot_A TSCnr534_QSnk539 TSeitenarm_V_4_SNKHot
0 20 20
EQUATIONS 1
TSCnr534Hot = [247,1] !Changed automatically
UNIT 248 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_SNKCold_A TSCnr534Cold TDTee529Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_4_SNKCold = [248,1] !Changed automatically
MSeitenarm_V_4_SNKCold = MSeitenarm_V_4_SNKCold_A
UNIT 249 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_SNKHot_A TDTee529Hot TSCnr534Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_4_SNKHot = [249,1] !Changed automatically
MSeitenarm_V_4_SNKHot = MSeitenarm_V_4_SNKHot_A
UNIT 250 TYPE 222 !Changed automatically
INPUTS 3
MSCnr534_QSnk539_A TSCnr534Hot TQSnk539H
0 20 20
EQUATIONS 2
TSCnr534_QSnk539 = [250,1] !Changed automatically
MSCnr534_QSnk539 = MSCnr534_QSnk539_A
UNIT 251 TYPE 222 !Changed automatically
INPUTS 3
MQSnk539_SCnr534_A TQSnk539H TSCnr534Cold
0 20 20
EQUATIONS 2
TQSnk539_SCnr534 = [251,1] !Changed automatically
MQSnk539_SCnr534 = MQSnk539_SCnr534_A
UNIT 252 TYPE 222 !Changed automatically
INPUTS 3
MDCnr544Hot_A TSeitenarm_V_4_3Hot TSeitenarm_V_5_1Hot
0 20 20
EQUATIONS 1
TDCnr544Hot = [252,1] !Changed automatically
UNIT 253 TYPE 222 !Changed automatically
INPUTS 3
MDCnr544Cold_A TSeitenarm_V_5_1Cold TSeitenarm_V_4_3Cold
0 20 20
EQUATIONS 1
TDCnr544Cold = [253,1] !Changed automatically
UNIT 254 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_3Cold_A TDCnr544Cold TDTee529Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_4_3Cold = [254,1] !Changed automatically
MSeitenarm_V_4_3Cold = MSeitenarm_V_4_3Cold_A
UNIT 255 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_4_3Hot_A TDTee529Hot TDCnr544Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_4_3Hot = [255,1] !Changed automatically
MSeitenarm_V_4_3Hot = MSeitenarm_V_4_3Hot_A
UNIT 256 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee548Cold_A
MDTee548Cold_B
MDTee548Cold_C
TSeitenarm_V_5_1Cold
TSeitenarm_V_5_2Cold
TSeitenarm_V_5_SNKCold
0 0 0 20 20 20 
EQUATIONS 1
TDTee548Cold= [256,1] !Changed automatically
UNIT 257 TYPE 929 !Changed automatically
PARAMETERS 0
INPUTS 6
MDTee548Hot_A
MDTee548Hot_B
MDTee548Hot_C
TSeitenarm_V_5_1Hot
TSeitenarm_V_5_2Hot
TSeitenarm_V_5_SNKHot
0 0 0 20 20 20 
EQUATIONS 1
TDTee548Hot= [257,1] !Changed automatically
UNIT 258 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_5_1Cold_A TDTee548Cold TDCnr544Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_5_1Cold = [258,1] !Changed automatically
MSeitenarm_V_5_1Cold = MSeitenarm_V_5_1Cold_A
UNIT 259 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_5_1Hot_A TDCnr544Hot TDTee548Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_5_1Hot = [259,1] !Changed automatically
MSeitenarm_V_5_1Hot = MSeitenarm_V_5_1Hot_A
UNIT 260 TYPE 222 !Changed automatically
INPUTS 3
MSCnr553Cold_A TSeitenarm_V_5_SNKCold TQSnk558_SCnr553
0 20 20
EQUATIONS 1
TSCnr553Cold = [260,1] !Changed automatically
UNIT 261 TYPE 222 !Changed automatically
INPUTS 3
MSCnr553Hot_A TSCnr553_QSnk558 TSeitenarm_V_5_SNKHot
0 20 20
EQUATIONS 1
TSCnr553Hot = [261,1] !Changed automatically
UNIT 262 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_5_SNKCold_A TSCnr553Cold TDTee548Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_5_SNKCold = [262,1] !Changed automatically
MSeitenarm_V_5_SNKCold = MSeitenarm_V_5_SNKCold_A
UNIT 263 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_5_SNKHot_A TDTee548Hot TSCnr553Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_5_SNKHot = [263,1] !Changed automatically
MSeitenarm_V_5_SNKHot = MSeitenarm_V_5_SNKHot_A
UNIT 264 TYPE 222 !Changed automatically
INPUTS 3
MSCnr553_QSnk558_A TSCnr553Hot TQSnk558H
0 20 20
EQUATIONS 2
TSCnr553_QSnk558 = [264,1] !Changed automatically
MSCnr553_QSnk558 = MSCnr553_QSnk558_A
UNIT 265 TYPE 222 !Changed automatically
INPUTS 3
MQSnk558_SCnr553_A TQSnk558H TSCnr553Cold
0 20 20
EQUATIONS 2
TQSnk558_SCnr553 = [265,1] !Changed automatically
MQSnk558_SCnr553 = MQSnk558_SCnr553_A
UNIT 266 TYPE 222 !Changed automatically
INPUTS 3
MSCnr567Cold_A TU_3Cold TQSnk586_SCnr567
0 20 20
EQUATIONS 1
TSCnr567Cold = [266,1] !Changed automatically
UNIT 267 TYPE 222 !Changed automatically
INPUTS 3
MSCnr567Hot_A TSCnr567_QSnk586 TU_3Hot
0 20 20
EQUATIONS 1
TSCnr567Hot = [267,1] !Changed automatically
UNIT 268 TYPE 222 !Changed automatically
INPUTS 3
MSCnr571Cold_A TSeitenarm_V_6Cold TQSnk579_SCnr571
0 20 20
EQUATIONS 1
TSCnr571Cold = [268,1] !Changed automatically
UNIT 269 TYPE 222 !Changed automatically
INPUTS 3
MSCnr571Hot_A TSCnr571_QSnk579 TSeitenarm_V_6Hot
0 20 20
EQUATIONS 1
TSCnr571Hot = [269,1] !Changed automatically
UNIT 270 TYPE 222 !Changed automatically
INPUTS 3
MSCnr571_QSnk579_A TSCnr571Hot TQSnk579H
0 20 20
EQUATIONS 2
TSCnr571_QSnk579 = [270,1] !Changed automatically
MSCnr571_QSnk579 = MSCnr571_QSnk579_A
UNIT 271 TYPE 222 !Changed automatically
INPUTS 3
MQSnk579_SCnr571_A TQSnk579H TSCnr571Cold
0 20 20
EQUATIONS 2
TQSnk579_SCnr571 = [271,1] !Changed automatically
MQSnk579_SCnr571 = MQSnk579_SCnr571_A
UNIT 272 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_5_2Cold_A TDTee508Cold TDTee548Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_5_2Cold = [272,1] !Changed automatically
MSeitenarm_V_5_2Cold = MSeitenarm_V_5_2Cold_A
UNIT 273 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_5_2Hot_A TDTee548Hot TDTee508Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_5_2Hot = [273,1] !Changed automatically
MSeitenarm_V_5_2Hot = MSeitenarm_V_5_2Hot_A
UNIT 274 TYPE 222 !Changed automatically
INPUTS 3
MU_3Cold_A TSCnr567Cold TDTee508Cold
0 20 20
EQUATIONS 2
TU_3Cold = [274,1] !Changed automatically
MU_3Cold = MU_3Cold_A
UNIT 275 TYPE 222 !Changed automatically
INPUTS 3
MU_3Hot_A TDTee508Hot TSCnr567Hot
0 20 20
EQUATIONS 2
TU_3Hot = [275,1] !Changed automatically
MU_3Hot = MU_3Hot_A
UNIT 276 TYPE 222 !Changed automatically
INPUTS 3
MSCnr567_QSnk586_A TSCnr567Hot TQSnk586H
0 20 20
EQUATIONS 2
TSCnr567_QSnk586 = [276,1] !Changed automatically
MSCnr567_QSnk586 = MSCnr567_QSnk586_A
UNIT 277 TYPE 222 !Changed automatically
INPUTS 3
MQSnk586_SCnr567_A TQSnk586H TSCnr567Cold
0 20 20
EQUATIONS 2
TQSnk586_SCnr567 = [277,1] !Changed automatically
MQSnk586_SCnr567 = MQSnk586_SCnr567_A
UNIT 278 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_6Cold_A TSCnr571Cold TDTee508Cold
0 20 20
EQUATIONS 2
TSeitenarm_V_6Cold = [278,1] !Changed automatically
MSeitenarm_V_6Cold = MSeitenarm_V_6Cold_A
UNIT 279 TYPE 222 !Changed automatically
INPUTS 3
MSeitenarm_V_6Hot_A TDTee508Hot TSCnr571Hot
0 20 20
EQUATIONS 2
TSeitenarm_V_6Hot = [279,1] !Changed automatically
MSeitenarm_V_6Hot = MSeitenarm_V_6Hot_A
EQUATIONS 5
dpPipeConvectedTot = TS_AColdConv + TS_AHotConv + TS_BColdConv + TS_BHotConv + Seitenarm_IIColdConv + Seitenarm_IIHotConv + TS_D_1ColdConv + TS_D_1HotConv + TS_EColdConv + TS_EHotConv + Seitenarm_IColdConv + Seitenarm_IHotConv + TS_FColdConv + TS_FHotConv + TS_C_1ColdConv + TS_C_1HotConv + TS_C_2ColdConv + TS_C_2HotConv + TS_D_2_1ColdConv + TS_D_2_1HotConv + TS_D_2_2ColdConv + TS_D_2_2HotConv + TS_H_2ColdConv + TS_H_2HotConv + TS_K_1ColdConv + TS_K_1HotConv + Seitenarm_VIColdConv + Seitenarm_VIHotConv + TS_GColdConv + TS_GHotConv + TS_H_1ColdConv + TS_H_1HotConv + TS_K_2ColdConv + TS_K_2HotConv + Seitenarm_VIIIColdConv + Seitenarm_VIIIHotConv + TS_IColdConv + TS_IHotConv + TS_JColdConv + TS_JHotConv
dpToFFieldTot = TS_ASlFf + TS_BSlFf + Seitenarm_IISlFf + TS_D_1SlFf + TS_ESlFf + Seitenarm_ISlFf + TS_FSlFf + TS_C_1SlFf + TS_C_2SlFf + TS_D_2_1SlFf + TS_D_2_2SlFf + TS_H_2SlFf + TS_K_1SlFf + Seitenarm_VISlFf + TS_GSlFf + TS_H_1SlFf + TS_K_2SlFf + Seitenarm_VIIISlFf + TS_ISlFf + TS_JSlFf
dpPipeIntTot = TS_AColdInt + TS_AHotInt + TS_BColdInt + TS_BHotInt + Seitenarm_IIColdInt + Seitenarm_IIHotInt + TS_D_1ColdInt + TS_D_1HotInt + TS_EColdInt + TS_EHotInt + Seitenarm_IColdInt + Seitenarm_IHotInt + TS_FColdInt + TS_FHotInt + TS_C_1ColdInt + TS_C_1HotInt + TS_C_2ColdInt + TS_C_2HotInt + TS_D_2_1ColdInt + TS_D_2_1HotInt + TS_D_2_2ColdInt + TS_D_2_2HotInt + TS_H_2ColdInt + TS_H_2HotInt + TS_K_1ColdInt + TS_K_1HotInt + Seitenarm_VIColdInt + Seitenarm_VIHotInt + TS_GColdInt + TS_GHotInt + TS_H_1ColdInt + TS_H_1HotInt + TS_K_2ColdInt + TS_K_2HotInt + Seitenarm_VIIIColdInt + Seitenarm_VIIIHotInt + TS_IColdInt + TS_IHotInt + TS_JColdInt + TS_JHotInt
dpSoilIntTot = TS_ASlInt + TS_BSlInt + Seitenarm_IISlInt + TS_D_1SlInt + TS_ESlInt + Seitenarm_ISlInt + TS_FSlInt + TS_C_1SlInt + TS_C_2SlInt + TS_D_2_1SlInt + TS_D_2_2SlInt + TS_H_2SlInt + TS_K_1SlInt + Seitenarm_VISlInt + TS_GSlInt + TS_H_1SlInt + TS_K_2SlInt + Seitenarm_VIIISlInt + TS_ISlInt + TS_JSlInt
dpImbalance = dpPipeConvectedTot - dpToFFieldTot  - dpPipeIntTot - dpSoilIntTot
ASSIGN Icegrid_ARA_planned_stage_I_Mfr.prt 699
UNIT 280 TYPE 25 !Changed automatically
PARAMETERS 10
dtSim! 1 Printing interval
START! 2 Start time
STOP! 3 Stop time
699! 4 Logical unit
0! 5 Units printing mode
0! 6 Relative or absolute start time
-1! 7 Overwrite or Append
-1! 8 Print header
0! 9 Delimiter
1! 10 Print labels
INPUTS 156
MTS_ACold MTS_AHot MTS_BCold MTS_BHot MSeitenarm_IICold MSeitenarm_IIHot MTS_D_1Cold MTS_D_1Hot
MTS_ECold MTS_EHot MSeitenarm_ICold MSeitenarm_IHot MTS_FCold MTS_FHot MSCnr4_QSrc1 MQSrc1_SCnr4
MSCnr55_QSnk60 MQSnk60_SCnr55 MSCnr126_QSnk131 MQSnk131_SCnr126 MSCnr16_QSnk85 MQSnk85_SCnr16 MTS_C_1Cold MTS_C_1Hot
MTS_C_2Cold MTS_C_2Hot MTS_C_SNK_pipeCold MTS_C_SNK_pipeHot MSCnr178_QSnk183 MQSnk183_SCnr178 MTS_D_2_1Cold MTS_D_2_1Hot
MTS_D_2_2Cold MTS_D_2_2Hot MTS_D_2_SNK_pipeCold MTS_D_2_SNK_pipeHot MTS_H_2Cold MTS_H_2Hot MTS_H_SNK_pipeCold MTS_H_SNK_pipeHot
MTS_K_SNK_pipeCold MTS_K_SNK_pipeHot MSCnr238_QSnk243 MQSnk243_SCnr238 MTS_K_1Cold MTS_K_1Hot MSeitenarm_VICold MSeitenarm_VIHot
MSCnr200_QSnk191 MQSnk191_SCnr200 MSCnr220_QSnk225 MQSnk225_SCnr220 MSCnr261_QSnk266 MQSnk266_SCnr261 MTS_GCold MTS_GHot
MTS_H_1Cold MTS_H_1Hot MSeitenarm_IV_absch_1_1Cold MSeitenarm_IV_absch_1_1Hot MSeitenarm_IV_absch_1_SNKCold MSeitenarm_IV_absch_1_SNKHot MSeitenarm_IV_absch_1_2Cold MSeitenarm_IV_absch_1_2Hot
MSeitenarm_IV_absch_2_1Cold MSeitenarm_IV_absch_2_1Hot MSeitenarm_IV_absch_2_2Cold MSeitenarm_IV_absch_2_2Hot MSeitenarm_IV_absch_3_RCold MSeitenarm_IV_absch_3_RHot MSeitenarm_IV_absch_3_LCold MSeitenarm_IV_absch_3_LHot
MSCnr331_QSnk335 MQSnk335_SCnr331 MSCnr353_QSnk358 MQSnk358_SCnr353 MSCnr363_QSnk322 MQSnk322_SCnr363 MSCnr370_QSnk375 MQSnk375_SCnr370
MSeitenarm_IV_absch_2_SNKCold MSeitenarm_IV_absch_2_SNKHot MTS_K_2Cold MTS_K_2Hot MSeitenarm_VIIICold MSeitenarm_VIIIHot MSeitenarm_VIICold MSeitenarm_VIIHot
MSCnr412_QSnk417 MQSnk417_SCnr412 MTS_ICold MTS_IHot MTS_JCold MTS_JHot MSeitenarm_V_1_1Cold MSeitenarm_V_1_1Hot
MSeitenarm_V_1_2_1Cold MSeitenarm_V_1_2_1Hot MSeitenarm_V_1_2_2Cold MSeitenarm_V_1_2_2Hot MSeitenarm_V_1_2_SNKCold MSeitenarm_V_1_2_SNKHot MSCnr443_QSnk448 MQSnk448_SCnr443
MSeitenarm_V_2_1Cold MSeitenarm_V_2_1Hot MSeitenarm_V_2_2Cold MSeitenarm_V_2_2Hot MSeitenarm_V_2_SNKCold MSeitenarm_V_2_SNKHot MSCnr464_QSnk469 MQSnk469_SCnr464
MSeitenarm_V_3_1Cold MSeitenarm_V_3_1Hot MSeitenarm_V_3_2Cold MSeitenarm_V_3_2Hot MSeitenarm_V_3_SNKCold MSeitenarm_V_3_SNKHot MSCnr483_QSnk488 MQSnk488_SCnr483
MSeitenarm_V_4_1Cold MSeitenarm_V_4_1Hot MU_1Cold MU_1Hot MSCnr498_QSnk503 MQSnk503_SCnr498 MDTee493_DTee512Cold MDTee493_DTee512Hot
MU_2Cold MU_2Hot MSCnr517_QSnk524 MQSnk524_SCnr517 MSeitenarm_V_4_2Cold MSeitenarm_V_4_2Hot MSeitenarm_V_4_SNKCold MSeitenarm_V_4_SNKHot
MSCnr534_QSnk539 MQSnk539_SCnr534 MSeitenarm_V_4_3Cold MSeitenarm_V_4_3Hot MSeitenarm_V_5_1Cold MSeitenarm_V_5_1Hot MSeitenarm_V_5_SNKCold MSeitenarm_V_5_SNKHot
MSCnr553_QSnk558 MQSnk558_SCnr553 MSCnr571_QSnk579 MQSnk579_SCnr571 MSeitenarm_V_5_2Cold MSeitenarm_V_5_2Hot MU_3Cold MU_3Hot
MSCnr567_QSnk586 MQSnk586_SCnr567 MSeitenarm_V_6Cold MSeitenarm_V_6Hot
MTS_ACold MTS_AHot MTS_BCold MTS_BHot MSeitenarm_IICold MSeitenarm_IIHot MTS_D_1Cold MTS_D_1Hot
MTS_ECold MTS_EHot MSeitenarm_ICold MSeitenarm_IHot MTS_FCold MTS_FHot MSCnr4_QSrc1 MQSrc1_SCnr4
MSCnr55_QSnk60 MQSnk60_SCnr55 MSCnr126_QSnk131 MQSnk131_SCnr126 MSCnr16_QSnk85 MQSnk85_SCnr16 MTS_C_1Cold MTS_C_1Hot
MTS_C_2Cold MTS_C_2Hot MTS_C_SNK_pipeCold MTS_C_SNK_pipeHot MSCnr178_QSnk183 MQSnk183_SCnr178 MTS_D_2_1Cold MTS_D_2_1Hot
MTS_D_2_2Cold MTS_D_2_2Hot MTS_D_2_SNK_pipeCold MTS_D_2_SNK_pipeHot MTS_H_2Cold MTS_H_2Hot MTS_H_SNK_pipeCold MTS_H_SNK_pipeHot
MTS_K_SNK_pipeCold MTS_K_SNK_pipeHot MSCnr238_QSnk243 MQSnk243_SCnr238 MTS_K_1Cold MTS_K_1Hot MSeitenarm_VICold MSeitenarm_VIHot
MSCnr200_QSnk191 MQSnk191_SCnr200 MSCnr220_QSnk225 MQSnk225_SCnr220 MSCnr261_QSnk266 MQSnk266_SCnr261 MTS_GCold MTS_GHot
MTS_H_1Cold MTS_H_1Hot MSeitenarm_IV_absch_1_1Cold MSeitenarm_IV_absch_1_1Hot MSeitenarm_IV_absch_1_SNKCold MSeitenarm_IV_absch_1_SNKHot MSeitenarm_IV_absch_1_2Cold MSeitenarm_IV_absch_1_2Hot
MSeitenarm_IV_absch_2_1Cold MSeitenarm_IV_absch_2_1Hot MSeitenarm_IV_absch_2_2Cold MSeitenarm_IV_absch_2_2Hot MSeitenarm_IV_absch_3_RCold MSeitenarm_IV_absch_3_RHot MSeitenarm_IV_absch_3_LCold MSeitenarm_IV_absch_3_LHot
MSCnr331_QSnk335 MQSnk335_SCnr331 MSCnr353_QSnk358 MQSnk358_SCnr353 MSCnr363_QSnk322 MQSnk322_SCnr363 MSCnr370_QSnk375 MQSnk375_SCnr370
MSeitenarm_IV_absch_2_SNKCold MSeitenarm_IV_absch_2_SNKHot MTS_K_2Cold MTS_K_2Hot MSeitenarm_VIIICold MSeitenarm_VIIIHot MSeitenarm_VIICold MSeitenarm_VIIHot
MSCnr412_QSnk417 MQSnk417_SCnr412 MTS_ICold MTS_IHot MTS_JCold MTS_JHot MSeitenarm_V_1_1Cold MSeitenarm_V_1_1Hot
MSeitenarm_V_1_2_1Cold MSeitenarm_V_1_2_1Hot MSeitenarm_V_1_2_2Cold MSeitenarm_V_1_2_2Hot MSeitenarm_V_1_2_SNKCold MSeitenarm_V_1_2_SNKHot MSCnr443_QSnk448 MQSnk448_SCnr443
MSeitenarm_V_2_1Cold MSeitenarm_V_2_1Hot MSeitenarm_V_2_2Cold MSeitenarm_V_2_2Hot MSeitenarm_V_2_SNKCold MSeitenarm_V_2_SNKHot MSCnr464_QSnk469 MQSnk469_SCnr464
MSeitenarm_V_3_1Cold MSeitenarm_V_3_1Hot MSeitenarm_V_3_2Cold MSeitenarm_V_3_2Hot MSeitenarm_V_3_SNKCold MSeitenarm_V_3_SNKHot MSCnr483_QSnk488 MQSnk488_SCnr483
MSeitenarm_V_4_1Cold MSeitenarm_V_4_1Hot MU_1Cold MU_1Hot MSCnr498_QSnk503 MQSnk503_SCnr498 MDTee493_DTee512Cold MDTee493_DTee512Hot
MU_2Cold MU_2Hot MSCnr517_QSnk524 MQSnk524_SCnr517 MSeitenarm_V_4_2Cold MSeitenarm_V_4_2Hot MSeitenarm_V_4_SNKCold MSeitenarm_V_4_SNKHot
MSCnr534_QSnk539 MQSnk539_SCnr534 MSeitenarm_V_4_3Cold MSeitenarm_V_4_3Hot MSeitenarm_V_5_1Cold MSeitenarm_V_5_1Hot MSeitenarm_V_5_SNKCold MSeitenarm_V_5_SNKHot
MSCnr553_QSnk558 MQSnk558_SCnr553 MSCnr571_QSnk579 MQSnk579_SCnr571 MSeitenarm_V_5_2Cold MSeitenarm_V_5_2Hot MU_3Cold MU_3Hot
MSCnr567_QSnk586 MQSnk586_SCnr567 MSeitenarm_V_6Cold MSeitenarm_V_6Hot
ASSIGN Icegrid_ARA_planned_stage_I_T.prt 700
UNIT 281 TYPE 25 !Changed automatically
PARAMETERS 10
dtSim! 1 Printing interval
START! 2 Start time
STOP! 3 Stop time
700! 4 Logical unit
0! 5 Units printing mode
0! 6 Relative or absolute start time
-1! 7 Overwrite or Append
-1! 8 Print header
0! 9 Delimiter
1! 10 Print labels
INPUTS 156
TTS_ACold TTS_AHot TTS_BCold TTS_BHot TSeitenarm_IICold TSeitenarm_IIHot TTS_D_1Cold TTS_D_1Hot
TTS_ECold TTS_EHot TSeitenarm_ICold TSeitenarm_IHot TTS_FCold TTS_FHot TSCnr4_QSrc1 TQSrc1_SCnr4
TSCnr55_QSnk60 TQSnk60_SCnr55 TSCnr126_QSnk131 TQSnk131_SCnr126 TSCnr16_QSnk85 TQSnk85_SCnr16 TTS_C_1Cold TTS_C_1Hot
TTS_C_2Cold TTS_C_2Hot TTS_C_SNK_pipeCold TTS_C_SNK_pipeHot TSCnr178_QSnk183 TQSnk183_SCnr178 TTS_D_2_1Cold TTS_D_2_1Hot
TTS_D_2_2Cold TTS_D_2_2Hot TTS_D_2_SNK_pipeCold TTS_D_2_SNK_pipeHot TTS_H_2Cold TTS_H_2Hot TTS_H_SNK_pipeCold TTS_H_SNK_pipeHot
TTS_K_SNK_pipeCold TTS_K_SNK_pipeHot TSCnr238_QSnk243 TQSnk243_SCnr238 TTS_K_1Cold TTS_K_1Hot TSeitenarm_VICold TSeitenarm_VIHot
TSCnr200_QSnk191 TQSnk191_SCnr200 TSCnr220_QSnk225 TQSnk225_SCnr220 TSCnr261_QSnk266 TQSnk266_SCnr261 TTS_GCold TTS_GHot
TTS_H_1Cold TTS_H_1Hot TSeitenarm_IV_absch_1_1Cold TSeitenarm_IV_absch_1_1Hot TSeitenarm_IV_absch_1_SNKCold TSeitenarm_IV_absch_1_SNKHot TSeitenarm_IV_absch_1_2Cold TSeitenarm_IV_absch_1_2Hot
TSeitenarm_IV_absch_2_1Cold TSeitenarm_IV_absch_2_1Hot TSeitenarm_IV_absch_2_2Cold TSeitenarm_IV_absch_2_2Hot TSeitenarm_IV_absch_3_RCold TSeitenarm_IV_absch_3_RHot TSeitenarm_IV_absch_3_LCold TSeitenarm_IV_absch_3_LHot
TSCnr331_QSnk335 TQSnk335_SCnr331 TSCnr353_QSnk358 TQSnk358_SCnr353 TSCnr363_QSnk322 TQSnk322_SCnr363 TSCnr370_QSnk375 TQSnk375_SCnr370
TSeitenarm_IV_absch_2_SNKCold TSeitenarm_IV_absch_2_SNKHot TTS_K_2Cold TTS_K_2Hot TSeitenarm_VIIICold TSeitenarm_VIIIHot TSeitenarm_VIICold TSeitenarm_VIIHot
TSCnr412_QSnk417 TQSnk417_SCnr412 TTS_ICold TTS_IHot TTS_JCold TTS_JHot TSeitenarm_V_1_1Cold TSeitenarm_V_1_1Hot
TSeitenarm_V_1_2_1Cold TSeitenarm_V_1_2_1Hot TSeitenarm_V_1_2_2Cold TSeitenarm_V_1_2_2Hot TSeitenarm_V_1_2_SNKCold TSeitenarm_V_1_2_SNKHot TSCnr443_QSnk448 TQSnk448_SCnr443
TSeitenarm_V_2_1Cold TSeitenarm_V_2_1Hot TSeitenarm_V_2_2Cold TSeitenarm_V_2_2Hot TSeitenarm_V_2_SNKCold TSeitenarm_V_2_SNKHot TSCnr464_QSnk469 TQSnk469_SCnr464
TSeitenarm_V_3_1Cold TSeitenarm_V_3_1Hot TSeitenarm_V_3_2Cold TSeitenarm_V_3_2Hot TSeitenarm_V_3_SNKCold TSeitenarm_V_3_SNKHot TSCnr483_QSnk488 TQSnk488_SCnr483
TSeitenarm_V_4_1Cold TSeitenarm_V_4_1Hot TU_1Cold TU_1Hot TSCnr498_QSnk503 TQSnk503_SCnr498 TDTee493_DTee512Cold TDTee493_DTee512Hot
TU_2Cold TU_2Hot TSCnr517_QSnk524 TQSnk524_SCnr517 TSeitenarm_V_4_2Cold TSeitenarm_V_4_2Hot TSeitenarm_V_4_SNKCold TSeitenarm_V_4_SNKHot
TSCnr534_QSnk539 TQSnk539_SCnr534 TSeitenarm_V_4_3Cold TSeitenarm_V_4_3Hot TSeitenarm_V_5_1Cold TSeitenarm_V_5_1Hot TSeitenarm_V_5_SNKCold TSeitenarm_V_5_SNKHot
TSCnr553_QSnk558 TQSnk558_SCnr553 TSCnr571_QSnk579 TQSnk579_SCnr571 TSeitenarm_V_5_2Cold TSeitenarm_V_5_2Hot TU_3Cold TU_3Hot
TSCnr567_QSnk586 TQSnk586_SCnr567 TSeitenarm_V_6Cold TSeitenarm_V_6Hot
TTS_ACold TTS_AHot TTS_BCold TTS_BHot TSeitenarm_IICold TSeitenarm_IIHot TTS_D_1Cold TTS_D_1Hot
TTS_ECold TTS_EHot TSeitenarm_ICold TSeitenarm_IHot TTS_FCold TTS_FHot TSCnr4_QSrc1 TQSrc1_SCnr4
TSCnr55_QSnk60 TQSnk60_SCnr55 TSCnr126_QSnk131 TQSnk131_SCnr126 TSCnr16_QSnk85 TQSnk85_SCnr16 TTS_C_1Cold TTS_C_1Hot
TTS_C_2Cold TTS_C_2Hot TTS_C_SNK_pipeCold TTS_C_SNK_pipeHot TSCnr178_QSnk183 TQSnk183_SCnr178 TTS_D_2_1Cold TTS_D_2_1Hot
TTS_D_2_2Cold TTS_D_2_2Hot TTS_D_2_SNK_pipeCold TTS_D_2_SNK_pipeHot TTS_H_2Cold TTS_H_2Hot TTS_H_SNK_pipeCold TTS_H_SNK_pipeHot
TTS_K_SNK_pipeCold TTS_K_SNK_pipeHot TSCnr238_QSnk243 TQSnk243_SCnr238 TTS_K_1Cold TTS_K_1Hot TSeitenarm_VICold TSeitenarm_VIHot
TSCnr200_QSnk191 TQSnk191_SCnr200 TSCnr220_QSnk225 TQSnk225_SCnr220 TSCnr261_QSnk266 TQSnk266_SCnr261 TTS_GCold TTS_GHot
TTS_H_1Cold TTS_H_1Hot TSeitenarm_IV_absch_1_1Cold TSeitenarm_IV_absch_1_1Hot TSeitenarm_IV_absch_1_SNKCold TSeitenarm_IV_absch_1_SNKHot TSeitenarm_IV_absch_1_2Cold TSeitenarm_IV_absch_1_2Hot
TSeitenarm_IV_absch_2_1Cold TSeitenarm_IV_absch_2_1Hot TSeitenarm_IV_absch_2_2Cold TSeitenarm_IV_absch_2_2Hot TSeitenarm_IV_absch_3_RCold TSeitenarm_IV_absch_3_RHot TSeitenarm_IV_absch_3_LCold TSeitenarm_IV_absch_3_LHot
TSCnr331_QSnk335 TQSnk335_SCnr331 TSCnr353_QSnk358 TQSnk358_SCnr353 TSCnr363_QSnk322 TQSnk322_SCnr363 TSCnr370_QSnk375 TQSnk375_SCnr370
TSeitenarm_IV_absch_2_SNKCold TSeitenarm_IV_absch_2_SNKHot TTS_K_2Cold TTS_K_2Hot TSeitenarm_VIIICold TSeitenarm_VIIIHot TSeitenarm_VIICold TSeitenarm_VIIHot
TSCnr412_QSnk417 TQSnk417_SCnr412 TTS_ICold TTS_IHot TTS_JCold TTS_JHot TSeitenarm_V_1_1Cold TSeitenarm_V_1_1Hot
TSeitenarm_V_1_2_1Cold TSeitenarm_V_1_2_1Hot TSeitenarm_V_1_2_2Cold TSeitenarm_V_1_2_2Hot TSeitenarm_V_1_2_SNKCold TSeitenarm_V_1_2_SNKHot TSCnr443_QSnk448 TQSnk448_SCnr443
TSeitenarm_V_2_1Cold TSeitenarm_V_2_1Hot TSeitenarm_V_2_2Cold TSeitenarm_V_2_2Hot TSeitenarm_V_2_SNKCold TSeitenarm_V_2_SNKHot TSCnr464_QSnk469 TQSnk469_SCnr464
TSeitenarm_V_3_1Cold TSeitenarm_V_3_1Hot TSeitenarm_V_3_2Cold TSeitenarm_V_3_2Hot TSeitenarm_V_3_SNKCold TSeitenarm_V_3_SNKHot TSCnr483_QSnk488 TQSnk488_SCnr483
TSeitenarm_V_4_1Cold TSeitenarm_V_4_1Hot TU_1Cold TU_1Hot TSCnr498_QSnk503 TQSnk503_SCnr498 TDTee493_DTee512Cold TDTee493_DTee512Hot
TU_2Cold TU_2Hot TSCnr517_QSnk524 TQSnk524_SCnr517 TSeitenarm_V_4_2Cold TSeitenarm_V_4_2Hot TSeitenarm_V_4_SNKCold TSeitenarm_V_4_SNKHot
TSCnr534_QSnk539 TQSnk539_SCnr534 TSeitenarm_V_4_3Cold TSeitenarm_V_4_3Hot TSeitenarm_V_5_1Cold TSeitenarm_V_5_1Hot TSeitenarm_V_5_SNKCold TSeitenarm_V_5_SNKHot
TSCnr553_QSnk558 TQSnk558_SCnr553 TSCnr571_QSnk579 TQSnk579_SCnr571 TSeitenarm_V_5_2Cold TSeitenarm_V_5_2Hot TU_3Cold TU_3Hot
TSCnr567_QSnk586 TQSnk586_SCnr567 TSeitenarm_V_6Cold TSeitenarm_V_6Hot
**********************************************************************
** end.ddck from C:\Users\damian.birchler\src\icegrid\wd2\simulation\Icegrid_ARA_planned_stage_I\ddck\generic 
**********************************************************************
***************************************************************
**BEGIN Monthly Energy Balance printer automatically generated from DDck files
***************************************************************
EQUATIONS 1
qImb =  + elSysIn_QSnk60HpComp - qSysOut_QSnk60Demand - qSysOut_QSnk60TessLoss - qSysOut_QSnk60TessAcum + elSysIn_Q_HpQSnk85 - qSysOut_QSnk85PD - qSysOut_QSnk85_dQlossTess - qSysOut_QSnk85_dQacumTess + qSysIn_Src - qSysOut_dpToFFieldTot - qSysOut_dpPipeIntTot - qSysOut_dpSoilIntTot
CONSTANTS 1
unitPrintEBal=282
ASSIGN temp\ENERGY_BALANCE_MO.Prt unitPrintEBal 
UNIT 282 Type 46
PARAMETERS 6
unitPrintEBal !1: Logical unit number
-1 !2: for monthly summaries
1  !3: 1:print at absolute times
-1 !4 -1: monthly integration
1  !5 number of outputs to avoid integration
1  !6 output number to avoid integration
INPUTS 14
TIME elSysIn_QSnk60HpComp qSysOut_QSnk60Demand qSysOut_QSnk60TessLoss qSysOut_QSnk60TessAcum elSysIn_Q_HpQSnk85 qSysOut_QSnk85PD qSysOut_QSnk85_dQlossTess qSysOut_QSnk85_dQacumTess qSysIn_Src qSysOut_dpToFFieldTot qSysOut_dpPipeIntTot qSysOut_dpSoilIntTot qImb
*******************************
TIME elSysIn_QSnk60HpComp qSysOut_QSnk60Demand qSysOut_QSnk60TessLoss qSysOut_QSnk60TessAcum elSysIn_Q_HpQSnk85 qSysOut_QSnk85PD qSysOut_QSnk85_dQlossTess qSysOut_QSnk85_dQacumTess qSysIn_Src qSysOut_dpToFFieldTot qSysOut_dpPipeIntTot qSysOut_dpSoilIntTot qImb
***************************************************************
**BEGIN Hourly Energy Balance printer automatically generated from DDck files
***************************************************************
CONSTANTS 1
unitPrintEBal_h=283
ASSIGN temp\ENERGY_BALANCE_HR.Prt unitPrintEBal_h 
UNIT 283 Type 46
PARAMETERS 6
unitPrintEBal_h !1: Logical unit number
-1 !2: for monthly summaries
1  !3: 1:print at absolute times
1 !4 1: hourly integration
1  !5 number of outputs to avoid integration
1  !6 output number to avoid integration
INPUTS 14
TIME elSysIn_QSnk60HpComp qSysOut_QSnk60Demand qSysOut_QSnk60TessLoss qSysOut_QSnk60TessAcum elSysIn_Q_HpQSnk85 qSysOut_QSnk85PD qSysOut_QSnk85_dQlossTess qSysOut_QSnk85_dQacumTess qSysIn_Src qSysOut_dpToFFieldTot qSysOut_dpPipeIntTot qSysOut_dpSoilIntTot qImb
*******************************
TIME elSysIn_QSnk60HpComp qSysOut_QSnk60Demand qSysOut_QSnk60TessLoss qSysOut_QSnk60TessAcum elSysIn_Q_HpQSnk85 qSysOut_QSnk85PD qSysOut_QSnk85_dQlossTess qSysOut_QSnk85_dQacumTess qSysIn_Src qSysOut_dpToFFieldTot qSysOut_dpPipeIntTot qSysOut_dpSoilIntTot qImb
*******************************
**BEGIN Head.ddck
*******************************
END
"""

_EXPECTED_RESULT = """\
"""


class TestReplaceAssignStatements:
    def test(self):
        newAssignStatements = [
            _ra.AssignStatement(r"..\ddck\QSnk85\Profile_Snk_85_001.csv", "QSnk85unit"),
            _ra.AssignStatement(r"temp\ENERGY_BALANCE_MO_HP_85.Prt", "QSnk85unitPrintHP_EBal"),
        ]

        actualResult = _ra.replaceAssignStatementsBasedOnUnitVariables(_ORIGINAL_DECK_CONTENT, newAssignStatements)

        assert actualResult == _ORIGINAL_DECK_CONTENT
