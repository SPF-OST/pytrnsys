__all__ = ["Error", "Result", "isError", "value"]

import dataclasses as _dc
import typing as _tp

_T = _tp.TypeVar("_T")


@_dc.dataclass
class Error:  # pylint: disable= too-few-public-methods
    message: str

    def throw(self):
        raise RuntimeError(f"En error has occurred: {self.message}")


Result = _tp.Union[_T, Error]


@_dc.dataclass
class ErrorException(Exception):
    message: str


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


def throwIfError(result: Result[_T]) -> None:
    if isError(result):
        message = error(result).message
        raise ErrorException(message)
