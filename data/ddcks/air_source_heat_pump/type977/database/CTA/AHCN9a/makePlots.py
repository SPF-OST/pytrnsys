import os
import matplotlib.pyplot as plt
import yumHeatPump.fitComparison as comp

expPath = os.path.join('C:\GIT\plural\heatPumpFit\AHCN9a', 'AHCN9a.exp')
fitPath = os.path.join('C:\GIT\plural\heatPumpFit\AHCN9a', 'AHCN9a.fit')

# condenserTemperatureBins = [[29.5, 30.5],
#                             [34.5, 35.5],
#                             [39.5, 40.5],
#                             [46.5, 47.5],
#                             [51.5, 52.5],
#                             [56.5, 57.5],
#                             [61.5, 62.5]]
# condenserTemperatureBins = [[29.5, 30.5],
#                             [31.5, 32.5],
#                             [34.5, 35.5]]
condenserTemperatureBins = [[29.0, 31.0],
                            [44.0, 46.0],
                            [59.0, 61.0]]

PCondBottom = 8.5
PCondTop = 13.5
COPBottom = 1.5#1.5
COPTop = 6.0#6.5

comparer = comp.fitComparison(expPath, fitPath)

fig, ax1, ax2 = comparer.plotExperimentalParameterVariationIncludingCop(condenserTemperatureBins, figsize=[9.,4.5])
ax1.axis([-16., 11., 5., 12.0])
ax1.grid()
ax1.legend(title='$T_{cond, in}$')
ax1.set_xlabel('$T_{evap, in}~(^\circ$C)')
ax1.set_ylabel('$P_{cond}$ (kW)')

ax2.axis([-16., 11., 1., 5.0])
ax2.grid()
ax2.set_xlabel('$T_{evap, in}~(^\circ$C)')
ax2.set_ylabel('COP')


# fig, ax1, ax2 = comparer.compareFitToExperimental([PCondBottom,PCondTop], [COPBottom,COPTop], figsize=[9.5, 4.5])
#
# ax1.axis([PCondBottom, PCondTop, PCondBottom, PCondTop])
# ax1.grid()
# ax1.set_xlabel('Experimental: $P_{dhw}$ (kW)')
# ax1.set_ylabel('Fit: $P_{dhw}$ (kW)')
# ax1.legend()
#
# ax2.axis([COPBottom, COPTop, COPBottom, COPTop])
# ax2.grid()
# ax2.legend()

plt.show()