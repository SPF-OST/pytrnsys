# pylint: disable=invalid-name

import os as _os
import pathlib as _pl
import unittest as _ut

import pytest as _pt
from pytrnsys.run_api import save_config_file, run_pytrnsys
from pytrnsys.run_api.dck_runner import compare_prt_files  # type: ignore[attr-defined]

from tests.pytrnsys.run_api.dummies_only_config import dummies_only_config


# TODO: test created dck, if config equal.  # pylint: disable=fixme
# TODO: test simulation results, if dck equal.  # pylint: disable=fixme


def compare_txt_files(config_file_path, expected_config_file_path):
    __tracebackhide__ = True  # pylint: disable=unused-variable
    with open(expected_config_file_path, "r", encoding="cp1252") as f1:
        expected_lines = f1.readlines()
    with open(config_file_path, "r", encoding="cp1252") as f2:
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
        expected_dck_file = EXPECTED_FILES_DIR / "run.dck"
        overall_dir = _os.getcwd()
        _os.chdir(CURRENT_DIR)

        errors = []
        error = run_pytrnsys(CONFIG_FILE_PATH)
        if error is not None:
            errors.append(error)
        _os.chdir(overall_dir)

        try:
            compare_txt_files(dck_file, expected_dck_file)
        except Exception as e:
            errors.append(e)

        # TODO: run separately inside of other test?  # pylint: disable=fixme
        #       Currently, the next test can be rerun by itself to plot the differences.
        if errors:
            raise ExceptionGroup(f"Found {len(errors)} issues: ", errors)

    def test_simulation_results(self):
        mfr_prt_name = "source_sink_and_TES_Mfr.prt"
        temperature_prt_name = RESULTS_DIR / "source_sink_and_TES_T.prt"

        errors = []
        errors += compare_prt_files(EXPECTED_FILES_DIR / mfr_prt_name, RESULTS_DIR / mfr_prt_name,
                                    file_type="timestep", massflow_solver=True)
        errors += compare_prt_files(EXPECTED_FILES_DIR / temperature_prt_name, RESULTS_DIR / temperature_prt_name,
                                    file_type="timestep", massflow_solver=True)
        if errors:
            raise ExceptionGroup(f'Found {len(errors)} issues:', errors)


if __name__ == "__main__":
    TestDummies().test_dck_equivalent()