# pylint: disable=invalid-name

from pytrnsys.run_api import PytrnsysConfiguration, save_config_file


def dummies_only_config() -> PytrnsysConfiguration:
    config = PytrnsysConfiguration()

    config.generic.run_cases = True
    config.generic.base_name_for_dcks = "dummies_only"

    config.variables.replace_variable_value("START", 0)
    config.variables.replace_variable_value("STOP", 10)
    config.variables.replace_variable_value("dtSim", 1)

    ddck_alias = "DDCK$"
    config.paths.add_path_alias(ddck_alias, "../source_sink_and_TES/ddck")
    config.paths.path_to_connection_info = "../source_sink_and_TES/DdckPlaceHolderValues.json"
    config.paths.results_folder = "results"

    config.ddcks.add_ddck(ddck_alias, "hydraulic/hydraulic", is_global=True, label="hydraulic")
    config.ddcks.add_ddck(ddck_alias, "control/hydraulic_control", is_global=True, label="hydraulic_control")

    config.ddcks.add_ddck(ddck_alias, "HtSt/two_port_dummy", label="TES")
    config.ddcks.add_ddck(ddck_alias, "QSnk/two_port_dummy", label="sink")
    config.ddcks.add_ddck(ddck_alias, "QSrc/two_port_dummy", label="source")

    return config

# config = dummies_only_config()
# save_config_file(config, config_file_path="")
#
# exchange_stuff
# save_config_file(config, config_file_path="")
#
# configs = [config_file_path_1, config_file_path_2]
# run_pytrnsys(configs)
