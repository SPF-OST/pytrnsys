"""
To add new functionality.
- Find the right subclass, or create a new subclass
    - add the subclass to the PytrnsysConfiguration
- add the attributes, or a container for new configuration parts
- add a method to the ConfigurationConverter to make the appropriate lines in the run.config
- add the new lines using this last new method to ConfigurationConverter._gather_lines
"""

import dataclasses as _dc
import os as _os
import pathlib as _pl
import subprocess as _sp
import typing as _tp

import numpy as _np


# TODO: add documentation everywhere.


class PlotterControl:
    """
    Control flags for the online plotter.
    ignore_online_plotter:
        If set to True, the TRNSYS online plotters are commented out in all the dck-files. No online plotters are shown
        during the simulation run. The TRNSYS progress bar window is still displayed.

    auto_close_online_plotter:
        If set to False, the TRNSYS online plotters will be left open until they are closed manually.
        This requires ignore_online_plotter to be set to False at the same time.

    remove_pop_up_window:
        Online plotters as well as the progress bar window are suppressed during the simulations, which corresponds to
        the TRNSYS hidden mode.
    """
    ignore_online_plotter: bool = True
    auto_close_online_plotter: bool = True
    remove_pop_up_window: bool = False
    # TODO: implement remove_pop_up_window


class Variables:
    _variables_to_change: dict = {}

    def replace_variable_value(self, variable: str, value: float | str) -> None:
        """
        Overwrites the right-hand side of the equation related to the declared TRNSYS variable.
        variable:
            TRNSYS variable name in final .dck.

        value:
            Single value or equation for the value, which the variable should take.
            0.5
            "2/60"


        """
        self._variables_to_change[variable] = value


class Ddcks:
    # TODO: provide set_global as an input?
    _assign: dict = {}
    _ddcks: dict = {}
    head_ddck: str = "DDCK$ generic/head global"
    end_ddck: str = "DDCK$ generic/end"

    def add_assign(self, prt_file_path: str, unit_variable: str) -> None:
        # TODO: error handling / warnings
        #       - unit_variable already declared <- indicates duplication issue.
        self._assign[unit_variable] = prt_file_path

    def add_ddck(self, folder_alias: str, ddck_path: str, component_name: None | str = None, is_global: bool = False,
                 label: str | None = None) -> None:
        """

        folder_alias:
            TBD

        ddck_path:
            TBD

        component_name:
            TBD

        is_global:
            TBD

        label:
            TBD

        """
        if component_name and is_global:
            raise ValueError("Cannot set 'component_name' and 'is_global' at the same time.")

        ddck_line = f"{folder_alias} {ddck_path}"

        if component_name is not None:
            ddck_line += f" as {component_name}"

        if is_global:
            ddck_line += " global"
        if not label:
            label = len(self._ddcks.keys())  # type: ignore[assignment]

        self._ddcks[label] = ddck_line

    def replace_ddck(self, label: str, folder_alias: str, ddck_path: str, component_name: None | str = None,
                     is_global: bool = False) -> None:
        # TODO: inconsistent usage of 'folder_alias' and 'path_alias'.
        """
        Replaces a previously declared ddck using the provided label in the 'add_ddck' method.

        label:
            TBD

        folder_alias:
            TBD
        ddck_path:
            TBD
        component_name:
            TBD
        is_global:
            TBD
        """
        if label not in self._ddcks.keys():
            raise ValueError(f"Supplied label not found: {label}")

        self.add_ddck(folder_alias, ddck_path, component_name, is_global, label)


class Paths:
    """
    Settings for the required paths:

    ddck_folder:
        TBD

    path_to_connection_info:
        TBD

    project_path:
        TBD

    trnsys_exe_path:
        TBD

    known_aliases:
        Gathers a list of aliases (filled with add_path_alias).
        The default alias for the ddck folder is "DDCK$"

    """
    ddck_folder: str = "ddck"
    path_to_connection_info: str = "./DdckPlaceHolderValues.json"
    project_path: str = "."
    trnsys_exe_path: str = "C:/Trnsys18/Exe/TRNExe.exe"
    known_aliases: dict[str, str] = {"DDCK$": ddck_folder}
    results_folder: None | str = None

    def add_path_alias(self, alias: str, path: str) -> None:
        # TODO: error handling for $ requirement.
        if "$" not in alias:
            alias += "$"
        self.known_aliases[alias] = path


class Generic:
    """
    General settings to control pytrnsys behavior.

    leave_n_cpus_available:
        TBD

    parse_file_created:
        TBD

    run_cases:
        TBD

    check_dck:
        TBD

    output_level:
        Output message level according to the logging package. (Options: “DEBUG”, “INFO” (default), “WARNING”, “ERROR”,
        and “CRITICAL”)

    base_name_4_dcks:
        TBD

    run_mode:
        "runFromConfig", "runFromCases", "runFromFolder"

    """

    def __init__(self) -> None:
        self.leave_n_cpus_available: int = 4
        self.parse_file_created: bool = False
        self.run_cases: bool = True
        self.check_dck: bool = True
        self.output_level: _tp.Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"] = "INFO"
        self.base_name_for_dcks: None | str = None
        self.run_mode: _tp.Literal["runFromConfig", "runFromCases", "runFromFolder"] = "runFromConfig"


class AutomaticWork:
    """
    Settings for automatic work.

    do_auto_unit_numbering:
        Automatically renumbers the units in the final .dck file.

    generate_unit_types_used:
        Generates a file that lists all types used in the simulation.

    add_automatic_energy_balance:
        Automatically adds energy balance equations and printers, based on the naming scheme for the energy balance variables.

    """
    do_auto_unit_numbering: bool = True
    generate_unit_types_used: bool = True
    add_automatic_energy_balance: bool = True


class Scaling:
    """
    # TODO: add docstring
    """

    def __init__(self) -> None:
        self.scaling: _tp.Literal["False", "toDemand"] = "False"
        self.scale_hp: None | str = None
        self.scaling_variable: None | str = None
        self.scaling_reference: None | str = None


class Tracking:
    """
    Paths and flags related to tracking parametric simulations.

    tracking_file:
        When running multiple simulations the status of each simulation can be tracked with the help of a json-file.
        When a simulation is started, this is entered with a timestamp into this file. Once the simulation is finished
        this entry will be overwritten accordingly. Like this one can keep track of which simulations were aborted
        (for whatever reason) after having been launched. To activate this functionality you need to specify the full
        path of the json-file to be created.
        'trackingFile = ".../[name].json"'


    master_file:
        If several simulations are run from different instances, the tracking can be taken one step further by
        employing a “master-file” in the form of a csv-file. It also tracks the status of different simulations based
        on the tracking json-files. One important feature is that, when it is used, simulations (identified by the
        name of the dck-file) that are already entered as a “success” won’t be run again. This is useful for redoing
        parametric studies where single simulations failed. If this is the case one can do the needed corrections and
        then simply launch the same parametric study again and the “master-file” will ensure that no unnecessary
        repetitions of simualtions are executed. To activate this functionality you need to specify the full path of
        the csv-file to be created.
        'master_file = ".../[name].csv"'
    """
    tracking_file: str | None = None
    master_file: str | None = None


class ParametricVariations:
    # TODO: investigate random variations
    """
    Methods and flags related to parametric variations.
    combine_all_cases: bool
        If several variations are defined, this parameter controls their combination. If it is set to True, all
        combinations are created. So if n values are given for variation 1 and m values are in variation 2 the total
        amount of simulations executed will be (m x n). If it is set to False, the amount of values of all variations
        has to be equal, and they are combined according to their order.
    """
    combine_all_cases: bool = False
    _variations: dict = {}
    _ddck_file_variations: dict = {}

    def add_variation(self, variation_name: str, trnsys_variable: str, values: list[float | str]) -> None:
        """
        Adds a parametric variation, i.e. several TRNSYS simulations with different values for a certain trnsysVariable.

        variation_name:
            Defines how the variation will be noted in the names of the dck-files to be generated.

        trnsys_variable:
            The specific variable in the .dck where the values should change.

        values:
            The specific values, the trnsys_variable should take.
            This could either be floats, or equations:
            [1440, 4367, 6575, 8040]
            ["START+24*2", "START+24*2", "START+24*2", "START+24*2"]

        """
        self._variations[variation_name] = {"trnsys_variable": trnsys_variable, "values": values}

    def add_ddck_variation(self, original_ddck: str, ddcks: list[str]) -> None:
        """
        Adds a variation where a specific ddck is changed between simulations.

        original_ddck:
            The ddck that should be replaced in each simulation.

        ddcks:
            The ddcks that should replace the 'original_ddck'
        """
        self._ddck_file_variations[original_ddck] = ddcks


@_dc.dataclass
class PytrnsysConfiguration:
    """
    Settings for a pytrnsys configuration.
    The subclasses explain their functionality.
    """
    plotter: PlotterControl = PlotterControl()
    paths: Paths = Paths()
    automatic_work: AutomaticWork = AutomaticWork()
    generic: Generic = Generic()
    scaling: Scaling = Scaling()
    variables: Variables = Variables()
    ddcks: Ddcks = Ddcks()
    variations: ParametricVariations = ParametricVariations()


class ConfigurationConverter:
    @staticmethod
    def _add_bool_line(flag: str, value: bool) -> str:
        return f"bool {flag} {value}"

    @staticmethod
    def _add_integer_line(flag: str, value: int) -> str:
        return f"int {flag} {value}"

    @staticmethod
    def _add_string_line(flag: str, value: str) -> str:
        return f"string {flag} '{value}'"

    @staticmethod
    def _generic_header() -> list[str]:
        # TODO: does this "add" anything?
        # TODO: private methods
        #
        return ["############# GENERIC #############################"]

    @staticmethod
    def _automatic_work_header() -> list[str]:
        return ["", "############# AUTOMATIC WORK BOOL##################"]

    @staticmethod
    def _paths_header() -> list[str]:
        return ["", "############# PATHS ###############################"]

    @staticmethod
    def _scaling_header() -> list[str]:
        return ["", "############# SCALING #############################"]

    @staticmethod
    def _parametric_variations_header() -> list[str]:
        return ["", "############# PARAMETRIC VARIATIONS ###############"]

    @staticmethod
    def _deck_header() -> list[str]:
        return ["", "############# ADJUSTED VARIABLE IN DCK ###############"]

    @staticmethod
    def _ddcks_header() -> list[str]:
        return ["", "############# INCLUDE DDCKS #######################"]

    def _plotter_lines(self, plotter: PlotterControl) -> list[str]:
        return [
            self._add_bool_line("ignoreOnlinePlotter", plotter.ignore_online_plotter),
            self._add_bool_line("autoCloseOnlinePlotter", plotter.auto_close_online_plotter),
            self._add_bool_line("removePopUpWindow", plotter.remove_pop_up_window)
        ]

    def _path_lines(self, paths: Paths) -> list[str]:
        lines = [
            self._add_string_line("pathToConnectionInfo", paths.path_to_connection_info),
            self._add_string_line("trnsysExePath", paths.trnsys_exe_path),
            self._add_string_line("projectPath", paths.project_path),
        ]
        for alias, path in paths.known_aliases.items():
            lines.append(self._add_string_line(alias, path))

        if paths.results_folder is not None:
            lines.append(self._add_string_line("addResultsFolder", paths.results_folder))

        return lines

    def _generic_lines(self, generic: Generic) -> list[str]:
        lines = [
            self._add_integer_line("reduceCpu", generic.leave_n_cpus_available),
            self._add_bool_line("parseFileCreated", generic.parse_file_created),
            self._add_bool_line("runCases", generic.run_cases),
            self._add_bool_line("checkDeck", generic.check_dck),
            self._add_string_line("outputLevel", generic.output_level),
            self._add_string_line("runType", generic.run_mode),
        ]

        if generic.base_name_for_dcks is not None:
            lines.append(self._add_string_line("nameRef", generic.base_name_for_dcks))

        return lines

    def _automatic_work_lines(self, automatic_work: AutomaticWork) -> list[str]:
        return [
            self._add_bool_line("doAutoUnitNumbering", automatic_work.do_auto_unit_numbering),
            self._add_bool_line("generateUnitTypesUsed", automatic_work.generate_unit_types_used),
            self._add_bool_line("addAutomaticEnergyBalance", automatic_work.add_automatic_energy_balance),
        ]

    def _scaling_lines(self, scaling: Scaling) -> list[str]:
        lines = [self._add_string_line("scaling", scaling.scaling)]
        if scaling.scale_hp is not None:
            lines.append(self._add_string_line("scaleHP", scaling.scale_hp))

        if scaling.scaling_variable is not None and scaling.scaling_reference is not None:
            lines.append(self._add_string_line("scalingVariable", scaling.scaling_variable))
            lines.append(self._add_string_line("scalingReference", scaling.scaling_reference))

        # TODO: add warning if only one of "scaling_variable" or "scaling_reference" is given.

        return lines

    def _tracking_lines(self, tracking: Tracking) -> list[str]:
        lines: list[str] = []
        if tracking.tracking_file is not None:
            self._add_string_line("trackingFile", tracking.tracking_file),
        if tracking.master_file is not None:
            self._add_string_line("masterFile", tracking.master_file),

        return lines

    def _variation_lines(self, variations: ParametricVariations) -> list[str]:
        lines: list[str] = []
        nr_of_variations = len(variations._variations.keys())
        if nr_of_variations == 0 and len(variations._ddck_file_variations.keys()) == 0:
            return lines

        if nr_of_variations > 0:
            lines.append(self._add_bool_line("combineAllCases ", variations.combine_all_cases))

        if variations.combine_all_cases is False:
            n_values = []
            for variation_name, variation in variations._variations.items():
                n_values.append(len(variation["values"]))

            if not len(_np.unique(n_values)) == 1:
                raise ValueError(f"Inconsistent variation lengths received for 'combine_all_cases' = False. "
                                 f"Lengths of the variations: {n_values}")

        for variation_name, variation in variations._variations.items():
            lines.append(f"variation {variation["trnsys_variable"]} {" ".join(map(str, variation["values"]))}")

        for original_ddck, ddcks in variations._ddck_file_variations.items():
            lines.append(f"changeDDckFile {original_ddck}{" ".join(map(str, ddcks))}")

        return lines

    @staticmethod
    def _variable_lines(deck: Variables) -> list[str]:
        lines = []
        for variable, value in deck._variables_to_change.items():
            lines.append(f"deck {variable} {value}")

        return lines

    @staticmethod
    def _ddcks_lines(ddcks: Ddcks) -> list[str]:
        lines = [ddcks.head_ddck]
        for ddck in ddcks._ddcks.values():
            lines.append(ddck)

        for unit_variable, prt_file_path in ddcks._assign.items():
            lines.append(f"assign {prt_file_path} {unit_variable}")

        lines.append(ddcks.end_ddck)

        return lines

    def save_config_file(self, config: PytrnsysConfiguration, path: _pl.Path) -> None:
        # TODO: make list of headers and Subclasses and automatically run through them.
        lines = self._gather_lines(config)

        # TODO: write to file
        self._write_config_file(lines, path)

    def _gather_lines(self, config: PytrnsysConfiguration) -> list[str]:
        lines = []
        lines += self._generic_header()
        lines += self._plotter_lines(config.plotter)
        lines += self._generic_lines(config.generic)

        lines += self._automatic_work_header()
        lines += self._automatic_work_lines(config.automatic_work)

        lines += self._paths_header()
        lines += self._path_lines(config.paths)

        lines += self._scaling_header()
        lines += self._scaling_lines(config.scaling)

        lines += self._parametric_variations_header()
        lines += self._variation_lines(config.variations)

        lines += self._deck_header()
        lines += self._variable_lines(config.variables)

        lines += self._ddcks_header()
        lines += self._ddcks_lines(config.ddcks)

        return lines

    @staticmethod
    def _write_config_file(lines, path) -> None:
        with open(path, "w") as f:
            for line in lines:
                f.write(line + "\n")


def save_config_file(config: PytrnsysConfiguration, config_file_path: _pl.Path) -> None:
    ConfigurationConverter().save_config_file(config, config_file_path)


def run_pytrnsys(pytrnsys_path: _pl.Path, run_py_path: _pl.Path):
    exception = None
    try:
        if run_py_path.is_file():
            _sp.run([pytrnsys_path, run_py_path, "/H"], shell=True, check=True)
        else:
            raise FileNotFoundError("File not found: " + str(run_py_path))
    except Exception as e:
        exception = e

    return exception
