__all__ = ["Error", "Result", "isError", "value"]

import dataclasses as _dc
import typing as _tp

import PyQt5.QtWidgets as _qtw

_T = _tp.TypeVar("_T")


@_dc.dataclass
class Error:
    message: str


Result = _tp.Union[_T, Error]


def isError(result: Result[_T]) -> bool:
    if isinstance(result, Error):
        return True

    return False


def value(result: Result[_T]) -> _T:
    if isError(result):
        _error = _tp.cast(Error, result)
        raise ValueError(f"Cannot get value of an error. Error is {_error.message}")

    return _tp.cast(_T, result)


def error(result: Result[_T]) -> Error:
    if not isError(result):
        raise ValueError("Result is not an error.")

    return _tp.cast(Error, result)


def showErrorMessageBox(_error: Error) -> None:
    messageBox = _qtw.QMessageBox()
    messageBox.setText(_error.message)
    messageBox.exec()
