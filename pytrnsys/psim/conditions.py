# pylint: skip-file
# type: ignore

__all__ = ["createConditions", "Conditions", "ConditionBase", "VALUE", "mayBeSerializedCondition"]

import typing as _tp
import abc as _abc
import dataclasses as _dc
import re as _re


VALUE = _tp.Union[str, float, int]


class ConditionBase(_abc.ABC):
    def __init__(self, variableName: str, serializedCondition: str) -> None:
        self.variableName = variableName
        self.serializedCondition = serializedCondition

    def __str__(self):
        return self.serializedCondition

    @_abc.abstractmethod
    def doesValueFulfillCondition(self, value: VALUE) -> bool:
        pass


@_dc.dataclass()
class _Bound:
    value: float
    isInclusive: bool


class _IntervalCondition(ConditionBase):
    def __init__(
        self, name: str, lowerBound: _tp.Optional[_Bound], upperBound: _tp.Optional[_Bound], serializedCondition: str
    ):
        super().__init__(name, serializedCondition)
        self.lowerBound = lowerBound
        self.upperBound = upperBound

    def __repr__(self):
        return f"<IntervalCondition({self.variableName},{self.lowerBound},{self.upperBound})>"

    def doesValueFulfillCondition(self, value: float) -> bool:
        return self._isLowerBoundRespected(value) and self._isUpperBoundRespected(value)

    def _isLowerBoundRespected(self, value: float) -> bool:
        if self.lowerBound is None:
            return True

        if self.lowerBound.isInclusive:
            return self.lowerBound.value <= value

        return self.lowerBound.value < value

    def _isUpperBoundRespected(self, value: float) -> bool:
        if self.upperBound is None:
            return True

        if self.upperBound.isInclusive:
            return value <= self.upperBound.value

        return value < self.upperBound.value


class _CaseCondition(ConditionBase):
    def __init__(self, name: str, values: _tp.Sequence[VALUE], serializedCondition: str) -> None:
        super().__init__(name, serializedCondition)
        self.values = values

    def __repr__(self):
        return f"<CaseCondition({self.variableName},{self.values})>"

    def doesValueFulfillCondition(self, value: VALUE) -> bool:
        return any(v == value for v in self.values)


class _IntervalConditionFactory:
    UNBOUNDED_PATTERN: _tp.Pattern = _re.compile(r"^(?P<variable>[^<=>]+)(?P<op>[<>]=?)(?P<bound>[^<=>]+)$")
    BOUNDED_PATTERN: _tp.Pattern = _re.compile(
        r"^(?P<lower>[^<=>]+)(?P<op1><=?)(?P<variable>[^<=>]+)(?P<op2><=?)(?P<upper>[^<=>]+)?"
    )

    @classmethod
    def create(cls, serializedCondition: str) -> "_IntervalCondition":
        match = cls.UNBOUNDED_PATTERN.match(serializedCondition)
        if match:
            return cls._createUnboundedInterval(match, serializedCondition)

        match = cls.BOUNDED_PATTERN.match(serializedCondition)
        if match:
            return cls._createBoundedInterval(match, serializedCondition)

        raise ValueError(f"Couldn't not parse condition {serializedCondition}")

    @classmethod
    def _createUnboundedInterval(cls, match: _tp.Match, serializedCondition: str) -> "_IntervalCondition":
        variableName = match.group("variable")
        op = match.group("op")
        bound = match.group("bound")

        bound = cls._convertToFloatOrThrow(bound, serializedCondition)

        lowerBound, upperBound = cls._createBoundsForUnbounded(bound, op)

        return _IntervalCondition(variableName, lowerBound, upperBound, serializedCondition)

    @classmethod
    def _createBoundsForUnbounded(cls, bound: float, op: str) -> _tp.Tuple[_tp.Optional[_Bound], _tp.Optional[_Bound]]:
        if op == "<":
            return None, _Bound(bound, isInclusive=False)
        elif op == "<=":
            return None, _Bound(bound, isInclusive=True)
        elif op == ">":
            return _Bound(bound, isInclusive=False), None
        elif op == ">=":
            return _Bound(bound, isInclusive=True), None
        else:
            raise AssertionError(f"Unknown operator: {op}.")

    @classmethod
    def _createBoundedInterval(cls, match: _tp.Match, serializedCondition: str) -> "_IntervalCondition":
        lower = match.group("lower")
        op1 = match.group("op1")
        variableName = match.group("variable")
        op2 = match.group("op2")
        upper = match.group("upper")
        lowerBound = cls._createBoundForBounded(lower, op1, serializedCondition)
        upperBound = cls._createBoundForBounded(upper, op2, serializedCondition)
        return _IntervalCondition(variableName, lowerBound, upperBound, serializedCondition)

    @classmethod
    def _createBoundForBounded(cls, lower: str, op1: str, serializedCondition: str) -> _Bound:
        lower = cls._convertToFloatOrThrow(lower, serializedCondition)

        isInclusive = op1 == "<="

        return _Bound(lower, isInclusive)

    @classmethod
    def _convertToFloatOrThrow(cls, bound: str, serializedCondition: str) -> float:
        try:
            bound = float(bound)
        except ValueError:
            raise ValueError(f"Bound must be convertible to float in {serializedCondition}.")
        return bound


class _CaseConditionFactory:
    PATTERN: _tp.Pattern = _re.compile(r"^(?P<name>[^<>=]+)=(?P<values>[^<>=|]+(\|[^<>=|]+)*)")

    @classmethod
    def create(cls, serializedCondition: str) -> "_CaseCondition":
        match = cls.PATTERN.match(serializedCondition)

        if not match:
            raise ValueError(f"Couldn't not parse condition {serializedCondition}")

        variableName = match.group("name")
        values = match.group("values").split("|")

        values = [cls._convertToFloatIfPossible(v) for v in values]

        return _CaseCondition(variableName, values, serializedCondition)

    @classmethod
    def _convertToFloatIfPossible(cls, value: str) -> _tp.Union[str, float]:
        try:
            return float(value)
        except ValueError:
            return value


@_dc.dataclass()
class Conditions:
    conditions: _tp.Sequence[ConditionBase]

    def doResultsSatisfyConditions(self, resultsDict):
        for condition in self.conditions:
            variableName = condition.variableName
            value = resultsDict[variableName]

            if not condition.doesValueFulfillCondition(value):
                return False

        return True


def createConditions(serializedConditions: _tp.Sequence[str]) -> Conditions:
    conditions = [_createCondition(sc) for sc in serializedConditions]

    return Conditions(conditions)


def _createCondition(serializedCondition: str) -> ConditionBase:
    try:
        return _IntervalConditionFactory.create(serializedCondition)
    except ValueError:
        pass

    try:
        return _CaseConditionFactory.create(serializedCondition)
    except ValueError:
        pass

    raise ValueError(f"Couldn't not parse condition {serializedCondition}")


def mayBeSerializedCondition(string: str) -> bool:
    return any(c in string for c in "<>=")
