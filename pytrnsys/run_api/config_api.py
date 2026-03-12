# pylint: disable=invalid-name

"""
To add new functionality.
- Find the right subclass, or create a new subclass
    - add the subclass to the PytrnsysConfiguration
- add the attributes, or a container for new configuration parts
- add a method to the ConfigurationConverter to make the appropriate lines in the run.config
- add the new lines using this last new method to ConfigurationConverter._gather_lines
"""

import dataclasses as _dc
import pathlib as _pl
import subprocess as _sp
import typing as _tp

import numpy as _np

# TODO: rename dck_runner to appropriate: deck_test_methods?  # pylint: disable=fixme
# TODO: simplify deck_tests so Users only pass the minimum required.  # pylint: disable=fixme

# TODO: add documentation everywhere.  # pylint: disable=fixme


@_dc.dataclass
class PlotterControl:
    """
    Control flags for the online plotter.
    ignore_online_plotter: bool
        If set to True, the TRNSYS online plotters are commented out in all the dck-files. No online plotters are shown
        during the simulation run. The TRNSYS progress bar window is still displayed.

    auto_close_online_plotter: bool
        If set to False, the TRNSYS online plotters will be left open until they are closed manually.
        This requires ignore_online_plotter to be set to False at the same time.

    remove_pop_up_window: bool
        Online plotters as well as the progress bar window are suppressed during the simulations, which corresponds to
        the TRNSYS hidden mode.
    """

    ignore_online_plotter: bool = _dc.field(default=True)
    auto_close_online_plotter: bool = _dc.field(default=True)
    remove_pop_up_window: bool = _dc.field(default=False)
    # TODO: implement remove_pop_up_window  # pylint: disable=fixme


@_dc.dataclass
class Variables:
    _variables_to_change: dict = _dc.field(default_factory=dict)

    def replace_variable_value(self, variable: str, value: float | str) -> None:
        """
        Overwrites the right-hand side of the equation related to the declared TRNSYS variable.
        variable: str
            TRNSYS variable name in final .dck.

        value: float | str
            Single value or equation for the value, which the variable should take.
            0.5
            "2/60"


        """
        self._variables_to_change[variable] = value


@_dc.dataclass
class Ddcks:
    # TODO: provide set_global as an input?  # pylint: disable=fixme
    """
    Settings class to include ddcks and change file assignments for, e.g. printers.

    Parameters
    __________
    head_ddck: str
        String path to the location of the "head.ddck" using a known alias.
        This defaults to "DDCK$ generic/head global".

    end_ddck: str
        String path to the location of the "end.ddck" using a known alias.
        This defaults to "DDCK$ generic/end".
    """
    _assign: dict = _dc.field(default_factory=dict)
    _ddcks: dict = _dc.field(default_factory=dict)
    head_ddck: str = _dc.field(default="DDCK$ generic/head global")
    end_ddck: str = _dc.field(default="DDCK$ generic/end")

    def add_assign(self, prt_file_path: str, unit_variable: str) -> None:
        """
        Assigns overwrite a ddck's path to a file, by providing the unit_variable and the new path.

        Example:
        __________
        "ASSIGN to_be_replaced.prt unitBalancePrinter"

        Will be replaced by:
        "ASSIGN actual_file.prt unitBalancePrinter"

        Parameters
        __________
        prt_file_path: str
            Path to the file where the printer should save the results.

        unit_variable: str
            Variable that provides the unit nr for TRNSYS to open the file.
        """
        # TODO: error handling / warnings  # pylint: disable=fixme
        #       - unit_variable already declared <- indicates duplication issue.
        self._assign[unit_variable] = prt_file_path

    def add_ddck(
        self,
        folder_alias: str,
        ddck_path: str,
        component_name: None | str = None,
        is_global: bool = False,
        label: str | None = None,
    ) -> None:
        f"""
        This method is used to sequentially add ddck files to the TRNSYS simulation.

        folder_alias: str
            A known alias declared in "Paths.add_path_alias".
            This is a shorter name, that points to a specific folder, e.g. "DDCK$".
            A list of known aliases can be obtained using "print(Paths.known_aliases)".

        ddck_path: str
            The path to the desired ddck relative to the provided folder_alias.

        component_name: str | None
            Optional short name you would like to use to adjust the ddck variables.
            This short name is added in front of each variable in the ddck, except when "is_global = True".
            Tin -> HPTin
            
            If component_name is None, then the name of the folder will be used.
            

        is_global: bool
            If True, this leaves the names of the variables untouched in the chosen ddck, except when explicitly specified.
            Tin -> Tin
            :Tin -> HPTin

        label: str | None
            Providing a label to the specific ddck makes it easier to find and replace the ddck 
            when preparing multiple configurations.
            This can be done using "Ddcks.replace_ddck".

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

    def replace_ddck(
        self, label: str, folder_alias: str, ddck_path: str, component_name: None | str = None, is_global: bool = False
    ) -> None:
        # TODO: inconsistent usage of 'folder_alias' and 'path_alias'.  # pylint: disable=fixme
        """
        Replaces a previously declared ddck using the provided label in the 'add_ddck' method.

        Parameters
        __________

        label: str
            Label used to find the ddck.
            For this method to work, this label must have been declared when using "Ddck.add_ddck".

        folder_alias: str
            A known alias declared in "Paths.add_path_alias".
            This is a shorter name, that points to a specific folder, e.g. "DDCK$".
            A list of known aliases can be obtained using "print(Paths.known_aliases)".

        ddck_path: str
            The path to the desired ddck relative to the provided folder_alias.

        component_name: str | None
            Optional short name you would like to use to adjust the ddck variables.
            This short name is added in front of each variable in the ddck, except when "is_global = True".
            Tin -> HPTin

            If component_name is None, then the name of the folder will be used.

        is_global: str | None
            If True, this leaves the names of the variables untouched in the chosen ddck, except when explicitly specified.
            Tin -> Tin
            :Tin -> HPTin
        """
        if label not in self._ddcks:
            raise ValueError(f"Supplied label not found: {label}")

        self.add_ddck(folder_alias, ddck_path, component_name, is_global, label)


@_dc.dataclass
class Paths:
    """
    Settings for the required paths:

    Parameters
    __________

    ddck_folder: str
        Main folder where the ddcks for this project are found.
        This defaults to "./ddck" and is relative to the current working directory.
        Additional folders can be included using "Paths.add_path_alias".

    path_to_connection_info: str
        Path to the DdckPlaceHolderValues.json. This defaults to the local working directory.

    project_path: str
        Path to the project. This defaults to the local working directory.

    trnsys_exe_path: str
        Path to your TRNSYS installation. This defaults to "C:/Trnsys18/Exe/TRNExe.exe"

    known_aliases: dict[str, str]
        Gathers a list of aliases (filled with "Paths.add_path_alias").
        The default alias for the ddck folder is "DDCK$"
        Can be helpful if you want to print the currently known aliases.

    results_folder: str | None
        Path where you would like the results to be saved.
        Pytrnsys will add folders for each simulation into this folder.
        If only a single simulation is run, and "results_folder = None",
        then pytrnsys will put the results in a folder with the project's name.
    """

    ddck_folder: str = _dc.field(default="ddck")
    path_to_connection_info: str = _dc.field(default="./DdckPlaceHolderValues.json")
    project_path: str = _dc.field(default=".")
    trnsys_exe_path: str = _dc.field(default="C:/Trnsys18/Exe/TRNExe.exe")
    known_aliases: dict[str, str] = _dc.field(default_factory=dict)
    results_folder: None | str = _dc.field(default=None)

    def __post_init__(self):
        self.known_aliases = {"DDCK$": self.ddck_folder}

    def add_path_alias(self, alias: str, path: str) -> None:
        """
        Method to add folders where ddcks are located.
        The "DDCK$" alias is known by default.

        Parameters
        __________
        alias:
            Short alias you would like to use when adding ddcks,
            e.g. "COMMON$" for ddcks common between different simulations.

        path:
            The folder path that the alias points to.
            This is often relative to the project location,
            e.g. "../common_ddcks"

        """
        # TODO: error handling for $ requirement.  # pylint: disable=fixme
        if "$" not in alias:
            alias += "$"
        self.known_aliases[alias] = path


@_dc.dataclass
class Generic:
    """
    General settings to control pytrnsys behavior.

    leave_n_cpus_available:
        Ensure several CPUs are available for the operating system to keep working.
        Pytrnsys will only use all other CPUs, if that many simulations are requested.
        If more simulations are requested, they will be cued and started automatically when
        the resources become available.
        leave_n_cpus_available defaults to 4.

    parse_file_created: bool
        Old functionality, that saves the parsed ddck.
        This used to be helpful when "Generic.check_dck" finds errors.
        Nowadays, the feedback is helpful enough to do without.
        parse_file_created defaults to False.

    run_cases: bool
        When True, pytrnsys will prepare the simulation files and then automatically start running the simulations.
        When False, only the simulation files will be prepared.
        This is often helpful when developing the simulation, to check e.g. the correct naming of variables.
        run_cases defaults to True.

    check_dck: bool
        When True, pytrnsys will check the correctness of the final dck.
        This first check finds many common issues and will not find all issues.
        check_dck defaults to True.

    output_level: str
        Output message level according to the logging package. (Options: “DEBUG”, “INFO” (default), “WARNING”, “ERROR”,
        and “CRITICAL”)

    base_name_4_dcks: str | None
        Change the starting part of the name of the simulation folders, e.g.
        Bad_rappenau_VTes_40 -> sim_VTES_40
        base_name_4_dcks defaults to None.

    run_mode: str
        Changes what starting point pytrnsys uses to run the simulations.
        The options are: "runFromConfig", "runFromCases", "runFromFolder".
        "runFromConfig" reads the settings prepared by this api, or from a config file.
        "runFromCases" starts the simulations from the prepared files.
        "runFromFolder" starts the simulation of a specific folder.
        run_mode defaults to "runFromConfig".
    """

    leave_n_cpus_available: int = _dc.field(default=4)
    parse_file_created: bool = _dc.field(default=False)
    run_cases: bool = _dc.field(default=True)
    check_dck: bool = _dc.field(default=True)
    output_level: _tp.Literal["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"] = _dc.field(default="INFO")
    base_name_for_dcks: None | str = _dc.field(default=None)
    run_mode: _tp.Literal["runFromConfig", "runFromCases", "runFromFolder"] = _dc.field(default="runFromConfig")


@_dc.dataclass
class AutomaticWork:
    """
    Settings for automatic work.

    do_auto_unit_numbering: bool
        Automatically renumbers the units in the final .dck file.
        do_auto_unit_numbering defaults to True

    generate_unit_types_used: bool
        Generates a file that lists all types used in the simulation.
        generate_unit_types_used defaults to True

    add_automatic_energy_balance: bool
        Automatically adds energy balance equations and printers, based on the naming scheme for
        the energy balance variables.
        add_automatic_energy_balance defaults to True

    """

    do_auto_unit_numbering: bool = _dc.field(default=True)
    generate_unit_types_used: bool = _dc.field(default=True)
    add_automatic_energy_balance: bool = _dc.field(default=True)


@_dc.dataclass
class Scaling:
    """
    # TODO: add docstring  # pylint: disable=fixme
    """

    scaling: _tp.Literal["False", "toDemand"] = _dc.field(default="False")
    scale_hp: None | str = _dc.field(default=None)
    scaling_variable: None | str = _dc.field(default=None)
    scaling_reference: None | str = _dc.field(default=None)


@_dc.dataclass
class Tracking:
    """
    Paths and flags related to tracking parametric simulations.

    tracking_file: str | None
        When running multiple simulations the status of each simulation can be tracked with the help of a json-file.
        When a simulation is started, this is entered with a timestamp into this file. Once the simulation is finished
        this entry will be overwritten accordingly. Like this one can keep track of which simulations were aborted
        (for whatever reason) after having been launched. To activate this functionality you need to specify the full
        path of the json-file to be created.
        'trackingFile = ".../[name].json"'
        tracking_file defaults to None.


    master_file: str | None
        If several simulations are run from different instances, the tracking can be taken one step further by
        employing a “master-file” in the form of a csv-file. It also tracks the status of different simulations based
        on the tracking json-files. One important feature is that, when it is used, simulations (identified by the
        name of the dck-file) that are already entered as a “success” won’t be run again. This is useful for redoing
        parametric studies where single simulations failed. If this is the case one can do the needed corrections and
        then simply launch the same parametric study again and the “master-file” will ensure that no unnecessary
        repetitions of simualtions are executed. To activate this functionality you need to specify the full path of
        the csv-file to be created.
        'master_file = ".../[name].csv"'
        master_file defaults to None.
    """

    tracking_file: str | None = _dc.field(default=None)
    master_file: str | None = _dc.field(default=None)


@_dc.dataclass
class ParametricVariations:
    # TODO: investigate random variations  # pylint: disable=fixme
    """
    Methods and flags related to parametric variations.

    combine_all_cases: bool
        If several variations are defined, this parameter controls their combination. If it is set to True, all
        combinations are created. So if n values are given for variation 1 and m values are in variation 2 the total
        amount of simulations executed will be (m x n). If it is set to False, the amount of values of all variations
        has to be equal, and they are combined according to their order.
        combine_all_cases defaults to False.
    """
    combine_all_cases: bool = _dc.field(default=False)
    _variations: dict = _dc.field(default_factory=dict)
    _ddck_file_variations: dict = _dc.field(default_factory=dict)

    def add_variation(self, variation_name: str, trnsys_variable: str, values: list[float | str]) -> None:
        """
        Adds a parametric variation, i.e. several TRNSYS simulations with different values for a certain trnsysVariable.

        variation_name: str
            Defines how the variation will be noted in the names of the dck-files to be generated.

        trnsys_variable: str
            The specific variable in the .dck where the values should change.
            Note that this needs to take the renaming of variables into account.
            Tin -> HPTin
            So HPTin needs to be used.
            Here it is often helpful to check the final .dck file for correctness.

        values: list[float | str]
            The specific values, the trnsys_variable should take.
            This could either be floats, or equations:
            [1440, 4367, 6575, 8040]
            ["START+24*2", "START+24*2", "START+24*2", "START+24*2"]

        """
        self._variations[variation_name] = {"trnsys_variable": trnsys_variable, "values": values}

    def add_ddck_variation(self, original_ddck: str, ddcks: list[str]) -> None:
        """
        Adds a variation where a specific ddck is changed between simulations.

        original_ddck: str
            The ddck that should be replaced in each simulation.

        ddcks: list[str]
            A list of ddcks that should replace the 'original_ddck'
        """
        self._ddck_file_variations[original_ddck] = ddcks


@_dc.dataclass
class PytrnsysConfiguration:  # pylint: disable=too-many-instance-attributes
    """
    Settings for a pytrnsys configuration.
    The subclasses explain their functionality.
    """

    plotter: PlotterControl = _dc.field(default_factory=PlotterControl)
    paths: Paths = _dc.field(default_factory=Paths)
    automatic_work: AutomaticWork = _dc.field(default_factory=AutomaticWork)
    generic: Generic = _dc.field(default_factory=Generic)
    scaling: Scaling = _dc.field(default_factory=Scaling)
    variables: Variables = _dc.field(default_factory=Variables)
    ddcks: Ddcks = _dc.field(default_factory=Ddcks)
    variations: ParametricVariations = _dc.field(default_factory=ParametricVariations)


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
            self._add_bool_line("removePopUpWindow", plotter.remove_pop_up_window),
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

        # TODO: add warning if only one of "scaling_variable" or "scaling_reference" is given.  # pylint: disable=fixme

        return lines

    def _tracking_lines(self, tracking: Tracking) -> list[str]:
        lines: list[str] = []
        if tracking.tracking_file is not None:
            lines.append(self._add_string_line("trackingFile", tracking.tracking_file))
        if tracking.master_file is not None:
            lines.append(self._add_string_line("masterFile", tracking.master_file))

        return lines

    def _variation_lines(self, variations: ParametricVariations) -> list[str]:
        lines: list[str] = []
        nr_of_variations = len(variations._variations.keys())  # pylint: disable=protected-access
        if nr_of_variations == 0 and len(variations._ddck_file_variations.keys()) == 0:  # pylint: disable=protected-access
            return lines

        if nr_of_variations > 0:
            lines.append(self._add_bool_line("combineAllCases ", variations.combine_all_cases))

        if variations.combine_all_cases is False:
            n_values = []
            for _, variation in variations._variations.items():  # pylint: disable=protected-access
                n_values.append(len(variation["values"]))

            if not len(_np.unique(n_values)) == 1:
                raise ValueError(
                    f"Inconsistent variation lengths received for 'combine_all_cases' = False. "
                    f"Lengths of the variations: {n_values}"
                )

        for _, variation in variations._variations.items():  # pylint: disable=protected-access
            lines.append(f'variation {variation["trnsys_variable"]} {" ".join(map(str, variation["values"]))}')

        for original_ddck, ddcks in variations._ddck_file_variations.items():  # pylint: disable=protected-access
            lines.append(f'changeDDckFile {original_ddck}{" ".join(map(str, ddcks))}')

        return lines

    @staticmethod
    def _variable_lines(deck: Variables) -> list[str]:
        lines = []
        for variable, value in deck._variables_to_change.items():  # pylint: disable=protected-access
            lines.append(f"deck {variable} {value}")

        return lines

    @staticmethod
    def _ddcks_lines(ddcks: Ddcks) -> list[str]:
        lines = [ddcks.head_ddck]
        for ddck in ddcks._ddcks.values():  # pylint: disable=protected-access
            lines.append(ddck)

        for unit_variable, prt_file_path in ddcks._assign.items():  # pylint: disable=protected-access
            lines.append(f"assign {prt_file_path} {unit_variable}")

        lines.append(ddcks.end_ddck)

        return lines

    def save_config_file(self, config: PytrnsysConfiguration, path: _pl.Path) -> None:
        lines = self._gather_lines(config)

        self._write_config_file(lines, path)

    def _gather_lines(self, config: PytrnsysConfiguration) -> list[str]:
        # TODO: make list of headers and Subclasses and automatically run through them.  # pylint: disable=fixme
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
        with open(path, "w", encoding="cp1252") as f:
            for line in lines:
                f.write(line + "\n")


def save_config_file(config: PytrnsysConfiguration, config_file_path: _pl.Path) -> None:
    """
    Method to save the configuration file using the configuration.
    Pytrnsys will read this configuration file to prepare the simulations and run them.

    Parameters
    __________
    config: PytrnsysConfiguration
        Settings class holding the desired simulation configuration.

    config_file_path: pathlib.Path
        Path where you would like the config file to be stored.

    """
    ConfigurationConverter().save_config_file(config, config_file_path)
