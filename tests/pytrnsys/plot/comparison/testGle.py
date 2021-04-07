import numpy as _np

import pytrnsys.plot.comparison._gle as _gle
import pytrnsys.plot.comparison._common as _com


class TestGle:
    def test(self, tmp_path):
        allSeries = [
            _com.Series(
                1,
                _com.GroupingValue("ViceR", 0.2),
                _com.AxisValues(
                    "AcollR",
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                ),
                _com.AxisValues(
                    "energyCost",
                    _np.array([0.0838, 0.1048, 0.1257, 0.1466]),
                    _np.array([0.0891, 0.1101, 0.1310, 0.1519]),
                    _np.array([0.0942, 0.1151, 0.1360, 0.1569]),
                ),
                True,
            ),
            _com.Series(
                2,
                _com.GroupingValue("ViceR", 0.4),
                _com.AxisValues(
                    "AcollR",
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                ),
                _com.AxisValues(
                    "energyCost",
                    _np.array([0.0880, 0.1089, 0.1297, 0.1506]),
                    _np.array([0.0950, 0.1159, 0.1367, 0.1577]),
                    _np.array([0.1015, 0.1224, 0.1432, 0.1641]),
                ),
                True,
            ),
            _com.Series(
                3,
                _com.GroupingValue("ViceR", 0.6),
                _com.AxisValues(
                    "AcollR",
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                ),
                _com.AxisValues(
                    "energyCost",
                    _np.array([0.0921, 0.1129, 0.1338, 0.1548]),
                    _np.array([0.1009, 0.1217, 0.1426, 0.1635]),
                    _np.array([0.1088, 0.1296, 0.1505, 0.1714]),
                ),
                True,
            ),
            _com.Series(
                4,
                _com.GroupingValue("ViceR", 0.8),
                _com.AxisValues(
                    "AcollR",
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                ),
                _com.AxisValues(
                    "energyCost",
                    _np.array([0.0963, 0.1171, 0.1379, 0.1589]),
                    _np.array([0.1068, 0.1276, 0.1484, 0.1694]),
                    _np.array([0.1161, 0.1369, 0.1578, 0.1787]),
                ),
                True,
            ),
            _com.Series(
                5,
                _com.GroupingValue("ViceR", 1.0),
                _com.AxisValues(
                    "AcollR",
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                    _np.array([1.0, 1.5, 2.0, 2.5]),
                ),
                _com.AxisValues(
                    "energyCost",
                    _np.array([0.1004, 0.1212, 0.1421, 0.1630]),
                    _np.array([0.1126, 0.1334, 0.1543, 0.1752]),
                    _np.array([0.1235, 0.1442, 0.1651, 0.1861]),
                ),
                True,
            ),
        ]

        expectedOutput = """! energyCost=energyCost(AcollR_j, ViceR)
! AcollR_1-	AcollR_1=	AcollR_1+	energyCost-(AcollR_1,0.2)	energyCost=(AcollR_1,0.2)	energyCost+(AcollR_1,0.2)	AcollR_2-	AcollR_2=	AcollR_2+	energyCost-(AcollR_2,0.4)	energyCost=(AcollR_2,0.4)	energyCost+(AcollR_2,0.4)	AcollR_3-	AcollR_3=	AcollR_3+	energyCost-(AcollR_3,0.6)	energyCost=(AcollR_3,0.6)	energyCost+(AcollR_3,0.6)	AcollR_4-	AcollR_4=	AcollR_4+	energyCost-(AcollR_4,0.8)	energyCost=(AcollR_4,0.8)	energyCost+(AcollR_4,0.8)	AcollR_5-	AcollR_5=	AcollR_5+	energyCost-(AcollR_5,1.0)	energyCost=(AcollR_5,1.0)	energyCost+(AcollR_5,1.0)
  1.0000	  1.0000	  1.0000	  0.0838	  0.0891	  0.0942	  1.0000	  1.0000	  1.0000	  0.0880	  0.0950	  0.1015	  1.0000	  1.0000	  1.0000	  0.0921	  0.1009	  0.1088	  1.0000	  1.0000	  1.0000	  0.0963	  0.1068	  0.1161	  1.0000	  1.0000	  1.0000	  0.1004	  0.1126	  0.1235	
  1.5000	  1.5000	  1.5000	  0.1048	  0.1101	  0.1151	  1.5000	  1.5000	  1.5000	  0.1089	  0.1159	  0.1224	  1.5000	  1.5000	  1.5000	  0.1129	  0.1217	  0.1296	  1.5000	  1.5000	  1.5000	  0.1171	  0.1276	  0.1369	  1.5000	  1.5000	  1.5000	  0.1212	  0.1334	  0.1442	
  2.0000	  2.0000	  2.0000	  0.1257	  0.1310	  0.1360	  2.0000	  2.0000	  2.0000	  0.1297	  0.1367	  0.1432	  2.0000	  2.0000	  2.0000	  0.1338	  0.1426	  0.1505	  2.0000	  2.0000	  2.0000	  0.1379	  0.1484	  0.1578	  2.0000	  2.0000	  2.0000	  0.1421	  0.1543	  0.1651	
  2.5000	  2.5000	  2.5000	  0.1466	  0.1519	  0.1569	  2.5000	  2.5000	  2.5000	  0.1506	  0.1577	  0.1641	  2.5000	  2.5000	  2.5000	  0.1548	  0.1635	  0.1714	  2.5000	  2.5000	  2.5000	  0.1589	  0.1694	  0.1787	  2.5000	  2.5000	  2.5000	  0.1630	  0.1752	  0.1861	
"""

        _gle.writeData(
            tmp_path, "test.gle", allSeries, "AcollR", "energyCost", "ViceR", None, True
        )

        actualOutputPath = list(tmp_path.iterdir())[0]
        actualOutput = actualOutputPath.read_text()

        assert actualOutput == expectedOutput
