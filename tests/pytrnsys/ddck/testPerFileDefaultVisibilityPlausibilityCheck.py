import collections.abc as _cabc
import dataclasses as _dc
import pathlib as _pl

import pytest as _pt

import pytrnsys.ddck.perFileDefaultVisibilityPlausibilityCheck as _dfpc
import pytrnsys.ddck.replaceTokens.defaultVisibility as _dv
import pytrnsys.utils.result as _res

_INPUT_DIR_PATH = _pl.Path(__file__).parent / "data" / "input"


@_dc.dataclass
class TestCase:
    inputFilePath: _pl.Path

    @property
    def shallGiveWarning(self) -> bool:
        inputFileStem = self.inputFilePath.stem

        if inputFileStem.endswith("-no-warn"):
            return False

        if inputFileStem.endswith("-warn"):
            return True

        raise AssertionError("Test case files should end in '-[no-]warn'.")

    @property
    def id(self) -> str:
        return self.inputFilePath.name

    @staticmethod
    def createCases() -> _cabc.Iterable["TestCase"]:
        for inputFilePath in _INPUT_DIR_PATH.iterdir():
            assert inputFilePath.is_file()
            yield TestCase(inputFilePath)


class TestPerFileDefaultVisibilityPlausibilityCheck:
    @_pt.mark.parametrize("testCase", [_pt.param(tc, id=tc.id) for tc in TestCase.createCases()])
    def testPerFileLocalDefaultVisibilityPlausibilityCheck(self, testCase: TestCase) -> None:
        result = _dfpc.checkDefaultVisibility(testCase.inputFilePath, _dv.DefaultVisibility.LOCAL)

        assert not _res.isError(result)
        valueWithWarnings = _res.value(result)

        print(valueWithWarnings.toWarningMessage())

        assert testCase.shallGiveWarning == valueWithWarnings.hasWarnings()
