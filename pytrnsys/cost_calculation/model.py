import dataclasses as _dc
import dataclasses_jsonschema as _dcj
import typing as _tp
import operator as _op

__all__ = ['ComponentGroup',
           'Component',
           'Cost',
           'LinearCoefficients',
           'UncertainFloat',
           'Variable',
           'ComponentSize']


@_dc.dataclass(frozen=True)
class ComponentGroup(_dcj.JsonSchemaMixin):
    name: str
    components: _tp.Sequence["Component"]


@_dc.dataclass(frozen=True, eq=False)
class Component(_dcj.JsonSchemaMixin):
    name: str
    lifetimeInYears: int
    cost: "Cost"


@_dc.dataclass(frozen=True)
class Group(_dcj.JsonSchemaMixin):
    name: str
    index: int


@_dc.dataclass(frozen=True)
class Cost(_dcj.JsonSchemaMixin):
    coeffs: "LinearCoefficients"
    variable: "Variable"

    def at(self, value: float) -> "UncertainFloat":
        return self.coeffs.offset + self.coeffs.slope * value


@_dc.dataclass(frozen=True)
class LinearCoefficients(_dcj.JsonSchemaMixin):
    offset: "UncertainFloat"
    slope: "UncertainFloat"


FloatLike = _tp.Union["UncertainFloat", _tp.SupportsFloat]


@_dc.dataclass(frozen=True)
class UncertainFloat(_dcj.JsonSchemaMixin):
    value: float
    toLowerBound: float = 0
    toUpperBound: float = 0

    @property
    def min(self) -> float:
        return self.value + self.toLowerBound

    @property
    def max(self) -> float:
        return self.value + self.toUpperBound

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

    def format(self, precision) -> str:
        uncertainty = self._formatUncertainty(precision)
        return f"{self.value:.{precision}f}{uncertainty}"

    def _formatUncertainty(self, precision):
        if not self.toLowerBound and not self.toUpperBound:
            return ""

        toLower = _formatDistance(self.toLowerBound, precision)
        toUpper = _formatDistance(self.toUpperBound, precision)

        return f"-{toLower}/+{toUpper}"

    def __post_init__(self):
        self._ensureAllFieldsAreConvertableToFloat()

        if self.toLowerBound > 0:
            raise ValueError(f"`toLowerBound' must be non-positive. Was {self.toLowerBound}")

        if self.toUpperBound < 0:
            raise ValueError(f"`toUpperBound' must be non-negative. Was {self.toUpperBound}")

    def _ensureAllFieldsAreConvertableToFloat(self):
        fields = [self.value, self.toLowerBound, self.toUpperBound]
        for f in fields:
            try:
                float(f)
            except TypeError as e:
                raise ValueError("All arguments must be floats") from e

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


def _doOp(op: _tp.Callable[[float, float], float], x: FloatLike, y: FloatLike) -> UncertainFloat:
    x = UncertainFloat.create(x)
    y = UncertainFloat.create(y)

    bounds = [op(v1, v2) for v1 in [x.min, x.max] for v2 in [y.min, y.max]]

    lower = min(bounds)
    upper = max(bounds)

    value = op(x.value, y.value)
    assert lower <= value <= upper

    toLower = -value + lower
    toUpper = -value + upper

    result = UncertainFloat(value, toLower, toUpper)

    return result


def _formatDistance(distance, precision) -> str:
    if not distance:
        return "0"

    return f"{abs(distance):.{precision}f}"


@_dc.dataclass(frozen=True)
class Variable(_dcj.JsonSchemaMixin):
    name: str
    unit: str


@_dc.dataclass(frozen=True)
class ComponentSize(_dcj.JsonSchemaMixin):
    component: Component
    size: float

    @property
    def cost(self) -> float:
        coeffs = self.component.cost.coeffs
        cost = coeffs.offset + self.size * coeffs.slope

        return UncertainFloat.create(cost).value


