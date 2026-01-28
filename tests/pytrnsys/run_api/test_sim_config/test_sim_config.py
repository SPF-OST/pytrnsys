# pylint: disable=invalid-name

import pathlib as _pl
import unittest as _ut

from pytrnsys.run_api import PytrnsysConfiguration, save_config_file


class TestSimplestConfig(_ut.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_simplest_config(self):
        current_dir = _pl.Path(__file__).parent
        config_file_path = current_dir / "run.config"

        config = PytrnsysConfiguration()

        config.plotter.ignore_online_plotter = False
        config.plotter.auto_close_online_plotter = False

        config.generic.run_cases = True
        config.generic.base_name_for_dcks = "dual_loop"

        config.paths.add_path_alias("COMMON$", "..\\common_ddcks")

        config.variables.replace_variable_value("START", 0)
        config.variables.replace_variable_value("STOP", 10)
        config.variables.replace_variable_value("dtSim", 1)

        ddck_alias = "DDCK$"
        common_alias = "COMMON$"

        config.ddcks.add_ddck(ddck_alias, "hydraulic/hydraulic_dummy", is_global=True, label="hydraulic")
        config.ddcks.add_ddck(ddck_alias, "control/hydraulic_control_dual_loop", is_global=True)
        for ashp in ["Ashp", "Ashp3"]:
            config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="Ashp/HP08L-M-BC_local", component_name=ashp)
            config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="Ashp/type977_dummy", component_name=ashp)
            config.ddcks.add_assign(f"temp\\{ashp}_MO.Prt", f"{ashp}unitPrintHpCool")
            config.ddcks.add_assign(f"temp\\{ashp}_COOL_HR.Prt", f"{ashp}unitHourlyHpCool")

        config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="pv\\type194")
        config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="pv\\database\\sunskin_roof_module_eternit")
        config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="pv\\database\\fronius_symo_inverter")

        config.ddcks.add_ddck(folder_alias=ddck_alias, ddck_path="IceS/type861_dummy")

        config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="Rad/Rad_placeholder", component_name="Rad")
        config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="weather/SMA_hourlyMean")
        config.ddcks.add_ddck(folder_alias=common_alias, ddck_path="weather/weather_data_base")

        config.variations.combine_all_cases = True
        config.variations.add_variation("Ac", "AcollAp", [2, 3, 4, 6, 8, 10])
        config.variations.add_variation("VTes", "volPerM2Col", [75, 100])

        config.variations.add_ddck_variation("CityBAS_dryK ", ["CityBAS_dryK", "CityCDF_dryK", "CityLUG_dryK"])

        config.ddcks.replace_ddck(label="hydraulic", folder_alias=ddck_alias, ddck_path="hydraulic/hydraulic_dual_loop",
                                  is_global=True)

        save_config_file(config, config_file_path)

        expected_config_file_path = current_dir / "expected_files" / "run.config"
        with open(expected_config_file_path, "r", encoding="cp1252") as f1:
            expected_lines = f1.readlines()

        with open(config_file_path, "r", encoding="cp1252") as f2:
            actual_lines = f2.readlines()

        _ut.TestCase().assertListEqual(actual_lines, expected_lines)

# TODO: test error handling for combine_all_cases = False  # pylint: disable=fixme
# TODO: test error handling for replace_ddck labels.  # pylint: disable=fixme
