# pylint: skip-file
# type: ignore

__all__ = ["FloatLike", "UncertainFloat"]

import dataclasses as _dc
import operator as _op
import typing as _tp

import dataclasses_jsonschema as _dcj

FloatLike = _tp.Union["UncertainFloat", _tp.SupportsFloat]


@_dc.dataclass(frozen=True)
class UncertainFloat(_dcj.JsonSchemaMixin):
    """
    BEWARE: This class does *not* handle correlation, i.e. 2x-x != x and
    it assumes extrema are attained at the input values' extrema.
    """
    mean: float
    toLowerBound: float = 0
    toUpperBound: float = 0

    @property
    def min(self) -> float:
        return self.mean + self.toLowerBound

    @property
    def max(self) -> float:
        return self.mean + self.toUpperBound

    @staticmethod
    def create(other: FloatLike):
        if isinstance(other, UncertainFloat):
            return other

        asFloat = float(other)
        uncertainFloat = UncertainFloat(asFloat)

        return uncertainFloat

    @staticmethod
    def zero() -> "UncertainFloat":
        return UncertainFloat(0)

    @staticmethod
    def one() -> "UncertainFloat":
        return UncertainFloat(1)

    def isCertain(self):
        return not self.toLowerBound and not self.toUpperBound

    def isUncertain(self):
        return not self.isCertain()

    def __post_init__(self):
        self._ensureAllFieldsAreConvertibleToFloat()

        if self.toLowerBound > 0:
            raise ValueError(f"`toLowerBound' must be non-positive. Was {self.toLowerBound}")

        if self.toUpperBound < 0:
            raise ValueError(f"`toUpperBound' must be non-negative. Was {self.toUpperBound}")

    def _ensureAllFieldsAreConvertibleToFloat(self):
        fields = [self.mean, self.toLowerBound, self.toUpperBound]
        for f in fields:
            try:
                float(f)
            except TypeError as e:
                raise ValueError("All arguments must be floats") from e

    def __format__(self, format_spec):
        uncertainty = self._formatUncertainty(format_spec)
        return rf"{self.mean:{format_spec}}{uncertainty}"

    def _formatUncertainty(self, format_spec):
        if not self.toLowerBound and not self.toUpperBound:
            return ""

        toLower = _formatDistance(self.toLowerBound, format_spec)
        toUpper = _formatDistance(self.toUpperBound, format_spec)

        return r"$^{\mathrm{+%(toUpper)s}}_{\mathrm{-%(toLower)s}}$" % dict(toLower=toLower, toUpper=toUpper)

    def __add__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.add, self, other)

    def __radd__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.add, other, self)

    def __sub__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.sub, self, other)

    def __rsub__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.sub, other, self)

    def __mul__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.mul, self, other)

    def __rmul__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.mul, other, self)

    def __truediv__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.truediv, self, other)

    def __rtruediv__(self, other: FloatLike) -> "UncertainFloat":
        return _doOp(_op.truediv, other, self)

    def __gt__(self, other: FloatLike) -> bool:
        other = self.create(other)

        return self.min > other.max


class ModuloRaiser:
    def __init__(self, modulo: _tp.SupportsFloat):
        self._modulo = modulo

    def pow(self, x, y):
        return pow(x, y, self._modulo)


def _doOp(op: _tp.Callable[[float, float], float], x: FloatLike, y: FloatLike) -> UncertainFloat:
    x = UncertainFloat.create(x)
    y = UncertainFloat.create(y)

    bounds = [op(v1, v2) for v1 in [x.min, x.max] for v2 in [y.min, y.max]]

    lower = min(bounds)
    upper = max(bounds)

    value = op(x.mean, y.mean)
    assert lower <= value <= upper

    toLower = -value + lower
    toUpper = -value + upper

    result = UncertainFloat(value, toLower, toUpper)

    return result


def _formatDistance(distance, format_spec) -> str:
    if not distance:
        return "0"

    return f"{abs(distance):{format_spec}}"
