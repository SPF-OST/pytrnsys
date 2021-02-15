import dataclasses as _dc
import dataclasses_jsonschema as _dcj
import typing as _tp

# TODO@bdi https://github.com/SPF-OST/pytrnsys/issues/5: Wrap components within group?

__all__ = ['Component',
           'Cost',
           'LinearCoefficients',
           'UncertainFloat',
           'Variable',
           'ComponentSize']


@_dc.dataclass(frozen=True)
class Component(_dcj.JsonSchemaMixin):
    name: str
    group: str
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


@_dc.dataclass(frozen=True)
class LinearCoefficients(_dcj.JsonSchemaMixin):
    offset: "UncertainFloat"
    slope: "UncertainFloat"


@_dc.dataclass(frozen=True)
class UncertainFloat(_dcj.JsonSchemaMixin):
    value: float
    toLowerBound: float = 0
    toUpperBound: float = 0

    @staticmethod
    def create(other: _tp.Union["UncertainFloat", _tp.SupportsFloat]):
        if isinstance(other, UncertainFloat):
            return other

        asFloat = float(other)
        uncertainFloat = UncertainFloat(asFloat)

        return uncertainFloat

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

    def __add__(self, other: _tp.Union["UncertainFloat", _tp.SupportsFloat]):
        other = UncertainFloat.create(other)

        value = self.value + other.value
        toLowerBound = self.toLowerBound + other.toLowerBound
        toUpperBound = self.toUpperBound + other.toUpperBound

        result = UncertainFloat(value, toLowerBound, toUpperBound)

        return result

    def __radd__(self, other: _tp.SupportsFloat):
        return self + other

    def __neg__(self):
        return UncertainFloat(-self.value, -self.toUpperBound, -self.toLowerBound)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other: _tp.SupportsFloat):
        other = float(other)

        return UncertainFloat(other*self.value, other*self.toLowerBound, other*self.toUpperBound)

    def __rmul__(self, other):
        return self * other


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


