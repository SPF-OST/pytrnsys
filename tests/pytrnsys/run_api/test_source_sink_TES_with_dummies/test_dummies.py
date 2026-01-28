import pathlib as _pl
import unittest as _ut

import pytest as _pt

from pytrnsys.run_api import save_config_file, run_pytrnsys
from ..dummies_only_config import dummies_only_config
from pytrnsys.run_api.dck_runner import compare_prt_files  # type: ignore[attr-defined]

# TODO: test created dck, if config equal.
# TODO: test simulation results, if dck equal.


def compare_txt_files(config_file_path, expected_config_file_path):
    __tracebackhide__ = True
    with open(expected_config_file_path, "r") as f1:
        expected_lines = f1.readlines()
    with open(config_file_path, "r") as f2:
        actual_lines = f2.readlines()
    case = _ut.TestCase()
    case.maxDiff = None
    case.assertListEqual(actual_lines, expected_lines)


CURRENT_DIR = _pl.Path(__file__).parent
EXPECTED_FILES_DIR = CURRENT_DIR / "expected_files"
CONFIG_FILE_PATH = CURRENT_DIR / "run.config"
RESULTS_DIR = CURRENT_DIR / "results" / "run"


@_pt.mark.incremental
class TestDummies:

    def test_dummies_config(self):
        config = dummies_only_config()

        # config.plotter.ignore_online_plotter = False
        # config.plotter.auto_close_online_plotter = False

        config.automatic_work.add_automatic_energy_balance = False

        save_config_file(config, CONFIG_FILE_PATH)

        expected_config_file_path = EXPECTED_FILES_DIR / "run.config"
        compare_txt_files(CONFIG_FILE_PATH, expected_config_file_path)

    def test_dck_equivalent(self):
        dck_file = RESULTS_DIR / "run.dck"
        run_py_path = CURRENT_DIR / "run.py"
        expected_dck_file = EXPECTED_FILES_DIR / "run.dck"

        # Replace this when integrated with pytrnsys.
        error = run_pytrnsys(CONFIG_FILE_PATH)

        compare_txt_files(dck_file, expected_dck_file)

        # This error relates to running the dck.
        # TODO: run separately inside of other test?
        #       Currently, the next test can be rerun by itself to plot the differences.
        if error:
            raise error

    def test_simulation_results(self):
        show_differences = False  # Manual flag to plot the differences.
        mfr_prt_name = "source_sink_and_TES_Mfr.prt"
        temperature_prt_name = RESULTS_DIR / "source_sink_and_TES_T.prt"

        errors = []
        errors += compare_prt_files(EXPECTED_FILES_DIR / mfr_prt_name, RESULTS_DIR / mfr_prt_name,
                                    file_type="timestep", massflow_solver=True)
        errors += compare_prt_files(EXPECTED_FILES_DIR / temperature_prt_name, RESULTS_DIR / temperature_prt_name,
                                    file_type="timestep", massflow_solver=True)
        if errors:
            raise ExceptionGroup(f'Found {len(errors)} issues:', errors)


# TODO: run config
# TODO: test error handling for combine_all_cases = False
# TODO: test error handling for replace_ddck labels.
