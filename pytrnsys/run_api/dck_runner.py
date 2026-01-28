# type: ignore

import enum as _en
import os as _os
import pandas as _pd
import pathlib as _pl
import subprocess as _sp
import unittest as _ut
import matplotlib.pyplot as _plt
import typing as _tp

# TODO: allow online plotter from test interface.
# TODO: allow correct naming of files: _hr, _step, _mo
# TODO: allow testing of multiple prt files in one go.


class TrnsysVersionPaths(_en.Enum):
    Bit32 = str(_pl.Path('C:\\TRNSYS18\\Exe\\TrnEXE.exe'))
    Bit64 = str(_pl.Path('C:\\TRNSYS18_64Bit\\Exe\\TrnEXE64.exe'))
    Bit32_CI = str(_pl.Path('C:\\CI-Progams\\TRNSYS18\\Exe\\TrnEXE.exe'))
    Bit64_CI = str(_pl.Path('C:\\CI-Progams\\TRNSYS18_64Bit\\Exe\\TrnEXE64.exe'))


class DeckTestPathFinder:
    def __init__(self, current_file: str = None,
                 pathEnum: TrnsysVersionPaths = TrnsysVersionPaths.Bit32,
                 massflow_solver: bool = False,
                 ):
        self.cmd = pathEnum.value
        self.curDir = _os.path.dirname(__file__)
        self.dckDirRelative = ''
        self.dckDirAbsolute = ''
        self.dckName = ''
        self.dckFilePath = ''
        self.resultFileName = ""
        self.resultFileName2 = ""
        self.expectedResultFileName = None
        self.resultFilePath = ""
        self.resultFilePath2 = ""
        self.expectedResultFilePath = ""
        self.expectedResultFilePath2 = ""
        self.massflow_solver = massflow_solver
        if current_file:
            # TODO: clean up all cases so this is no longer an if.
            self.prep_inputs(current_file, massflow_solver)


    def prep_inputs(self, current_file: str, massflow_solver: bool):
        file_path = _pl.Path(current_file)
        stem = file_path.stem
        spec = stem.removeprefix("test_")
        DckName = f"{spec}.dck"  # spec+".dck"
        PrtName = f"{spec}_H.Prt"
        if massflow_solver:
            PrtName = f"{spec}_Mfr.Prt"
            self.resultFileName2 = f"{spec}_T.Prt"

        self.dckName = DckName
        self.resultFileName = PrtName
        self.dckDirRelative = r".\decks"
        # self.expectedFilesDir = r".\expected_files"
        self.find(current_file, massflow_solver)

    def find(self, originFile, massflow_solver: bool = False):
        # TODO: clean up further, so this does not show up twice.
        self.curDir = _os.path.dirname(originFile)
        self.dckDirAbsolute = self.curDir + "\\" + self.dckDirRelative
        self.dckFilePath = self.dckDirAbsolute + '\\' + self.dckName
        self.resultFilePath = self.dckDirAbsolute + "\\temp\\" + self.resultFileName
        if self.expectedResultFileName:
            self.expectedResultFilePath = self.curDir + "\\expected_files\\" + self.expectedResultFileName
        else:
            self.expectedResultFilePath = self.curDir + "\\expected_files\\" + self.resultFileName

        if massflow_solver:
            self.resultFilePath2 = self.dckDirAbsolute + "\\temp\\" + self.resultFileName2
            self.expectedResultFilePath2 = self.curDir + "\\expected_files\\" + self.resultFileName2

    def set_trnsys_version_path(self, pathEnum: TrnsysVersionPaths):
        self.cmd = pathEnum.value

    def clean_results_file(self):
        if _pl.Path(self.resultFilePath).exists():
            _os.remove(self.resultFilePath)

    def run_and_compare(self, trnsys_version_path: TrnsysVersionPaths, show_diffs: bool = False,
                        file_type: _tp.Literal["timestep", "hourly", "monthly"] = "timestep",
                        raises: bool = False,
    ):
        self.clean_results_file()
        self.set_trnsys_version_path(trnsys_version_path)
        _skipTests, _exception = runDckAndGetResults(self.cmd, self.dckFilePath)
        if _exception and not raises:
            raise Exception("\nIssue with running the dck."
                            "\nCheck the log and lst files for the likely cause.")
        if raises and not _exception:
            raise AssertionError("\nTrnsys did not raise the expected error.")
        errors = compare_prt_files(self.resultFilePath, self.expectedResultFilePath, show_diffs=show_diffs, file_type=file_type,
                                   massflow_solver=self.massflow_solver)
        if self.massflow_solver:
            errors += compare_prt_files(self.resultFilePath2, self.expectedResultFilePath2, show_diffs=show_diffs, file_type=file_type,
                                   massflow_solver=self.massflow_solver)

        if errors:
            raise ExceptionGroup(f'Found {len(errors)} issues:', errors)

    def compare_prt_files(self, file_type: _tp.Literal["timestep", "hourly", "monthly"] = "timestep",):
        __tracebackhide__ = True
        errors = compare_prt_files(self.resultFilePath, self.expectedResultFilePath, show_diffs=True, file_type=file_type,
                              massflow_solver=self.massflow_solver)
        if self.massflow_solver:
            errors += compare_prt_files(self.resultFilePath2, self.expectedResultFilePath2, show_diffs=True,
                                  file_type=file_type, massflow_solver=self.massflow_solver)

        if errors:
            raise ExceptionGroup(f'Found {len(errors)} issues:', errors)


def runDck(cmd, dckName):
    exception = None
    try:
        if _os.path.isfile(dckName):
            _sp.run([cmd, dckName, "/H"], shell=True, check=True)
            skipOthers = False
        else:
            raise FileNotFoundError("File not found: " + dckName)
    except Exception as e:
        skipOthers = True
        exception = e

    return skipOthers, exception


def runDckAndGetResults(cmd, dckName):
    skipOthers, exception = runDck(cmd, dckName)

    return skipOthers, exception


def comparePrtFiles(testCase, filePath1, filePath2):
    comparePrtFiles_as_files(testCase, filePath1, filePath2)


def comparePrtFiles_as_files(testCase, filePath1, filePath2):
    with open(filePath1) as f1, open(filePath2) as f2:
        _ut.TestCase.assertListEqual(testCase, list(f1), list(f2))


def compare_prt_files(result_file_path: _pl.Path, expected_result_file_path: _pl.Path, show_diffs: bool = False,
                      file_type: _tp.Literal["timestep", "hourly", "monthly"] = "timestep",
                      massflow_solver: bool = False,
                      ):
    __tracebackhide__ = True
    df_1 = read_prt(result_file_path, file_type)
    df_2 = read_prt(expected_result_file_path, file_type)

    errors = []

    all_columns = set(df_1.columns).union(set(df_2.columns))
    missing_columns_in_df_1 = list(all_columns - set(df_1.columns))
    if missing_columns_in_df_1:
        df_1[missing_columns_in_df_1] = 0
        errors.append(ValueError(f"Columns found in expected file, which are missing in the result file: "
                                 f"{missing_columns_in_df_1}"))

    missing_columns_in_df_2 = list(all_columns - set(df_2.columns))
    if missing_columns_in_df_2:
        df_2[missing_columns_in_df_2] = 0
        errors.append(ValueError(f"Columns found in expected file, which are missing in the result file: "
                                 f"{missing_columns_in_df_2}"))
    try:
        df_diff = df_1 - df_2
    except TypeError as e:
        raise TypeError(f"\nIncorrect file type provided: {file_type}")

    if not df_diff.empty:
        try:
            _pd.testing.assert_frame_equal(df_1, df_2)
        except AssertionError as e:
            errors.append(e)
    
    if show_diffs:
        visually_compare_prt_files(df_1, df_2, df_diff, all_columns)
    
    if errors and not massflow_solver:
        raise ExceptionGroup(f'Found {len(errors)} issues:', errors)

    return errors


def visually_compare_prt_files(df_1: _pd.DataFrame, df_2: _pd.DataFrame, df_diff: _pd.DataFrame, all_columns):
    # TODO: cleanup.
    for i, column in enumerate(all_columns):
        fig, ax = _plt.subplots()
        df_diff[column].plot(legend=column, ax=ax)
    _plt.show()


def read_prt(file_path, file_type):
    try:
        match file_type:
            case "hourly":
                df = _pd.read_csv(file_path, sep='\t', skiprows=1, skipfooter=24, engine='python')
            case "timestep":
                df = _pd.read_csv(file_path, sep='\t', skiprows=0, skipfooter=0, engine='python')
            case "monthly":
                raise NotImplementedError("Monthly has not been implemented yet.")
    except FileNotFoundError as e:
        raise e

    df.columns = df.columns.str.rstrip()
    df.dropna(how='all', axis='columns', inplace=True)
    return df


def compare_dataframes(abs_tolerance, df_expected, df_new, errors, manual_test, rel_tolerance, sheet):
    try:
        if abs_tolerance and rel_tolerance:
            _pd.testing.assert_frame_equal(df_new, df_expected, atol=abs_tolerance, rtol=rel_tolerance,
                                           check_exact=False)
        elif abs_tolerance:
            _pd.testing.assert_frame_equal(df_new, df_expected, atol=abs_tolerance, check_exact=False)
        elif rel_tolerance:
            _pd.testing.assert_frame_equal(df_new, df_expected, rtol=rel_tolerance, check_exact=False)
        else:
            _pd.testing.assert_frame_equal(df_new, df_expected, check_exact=True)
    except AssertionError as current_error:
        """Optihood doesn't export the results in a consistent way.
        Therefore, this hack reorders the results.
        Instead, the export should be ordered consistently.
        """

        df_new = df_new.sort_values(by=[df_new.columns[0]], ignore_index=True)
        df_expected = df_expected.sort_values(by=[df_new.columns[0]], ignore_index=True)

        """ The dType of a column sometimes gets set to int instead of float. 
            This reduces the feedback of the test to a dType check.
            Ignoring the dType ensures better feedback.
        """
        try:
            if abs_tolerance and rel_tolerance:
                _pd.testing.assert_frame_equal(df_new, df_expected, atol=abs_tolerance, rtol=rel_tolerance,
                                               check_dtype=False, check_exact=False)
            elif abs_tolerance:
                _pd.testing.assert_frame_equal(df_new, df_expected, atol=abs_tolerance, check_dtype=False,
                                               check_exact=False)
            elif rel_tolerance:
                _pd.testing.assert_frame_equal(df_new, df_expected, rtol=rel_tolerance, check_dtype=False,
                                               check_exact=False)
            else:
                _pd.testing.assert_frame_equal(df_new, df_expected, check_dtype=False, check_exact=True)
        except AssertionError as current_error_2:
            errors.append(current_error)
            errors.append(current_error_2)
            if manual_test:
                """Plot differences in sheet to simplify comparison."""
                plot_dfs_and_differences(df_new, df_expected, sheet)


def plot_dfs_and_differences(df_new: _pd.DataFrame, df_expected: _pd.DataFrame, sheet_name: str):
    # =======
    # The following is needed to plot the differences as part of a pycharm test run.
    import matplotlib as _mpl
    _mpl.use("QtAgg")
    # =======
    fig, axs = _plt.subplots(3, 1)
    df_new.plot(ax=axs[0])
    df_expected.plot(ax=axs[1])
    if df_new.shape == df_expected.shape:
        # avoids str - str errors.
        df_diff = df_new.select_dtypes(exclude=[object]) - df_expected.select_dtypes(exclude=[object])
        df_diff.plot(ax=axs[2])
    else:
        sheet_name += " SHAPE MISMATCH!"
    axs[0].set_title(f"sheet name: {sheet_name}")
    