import typing as _tp
import abc as _abc
import dataclasses as _dc
import regex as _re


VALUE = _tp.Union[str, float, int]


class ConditionBase(_abc.ABC):
    def __init__(self, variableName: str) -> None:
        self.variableName = variableName

    def doesValueFulfillCondition(self, value: VALUE) -> bool:
        pass


@_dc.dataclass()
class Bound:
    value: float
    isInclusive: bool


class IntervalCondition(ConditionBase):
    def __init__(self, name: str, lowerBound: _tp.Optional[Bound], upperBound: _tp.Optional[Bound]):
        super().__init__(name)
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


class CaseCondition(ConditionBase):
    def __init__(self, name: str, values: _tp.Sequence[VALUE]) -> None:
        super().__init__(name)
        self.values = values

    def __repr__(self):
        return f"<CaseCondition({self.variableName},{self.values})>"

    def doesValueFulfillCondition(self, value: VALUE) -> bool:
        return any(v == value for v in self.values)


class IntervalConditionFactory:
    UNBOUNDED_PATTERN: _tp.Pattern = _re.compile(r"^(?P<variable>[^<=>]+)(?P<op>[<>]=?)(?P<bound>[^<=>]+)$")
    BOUNDED_PATTERN: _tp.Pattern = \
        _re.compile(r"^(?<lower>[^<=>]+)(?P<op1><=?)(?P<variable>[^<=>]+)(?P<op2><=?)(?<upper>[^<=>]+)?")

    @classmethod
    def create(cls, serializedCondition: str) -> "IntervalCondition":
        match = cls.UNBOUNDED_PATTERN.match(serializedCondition)
        if match:
            return cls._createUnboundedInterval(match, serializedCondition)

        match = cls.BOUNDED_PATTERN.match(serializedCondition)
        if match:
            return cls._createBoundedInterval(match, serializedCondition)

        raise ValueError(f"Couldn't not parse condition {serializedCondition}")

    @classmethod
    def _createUnboundedInterval(cls, match: _tp.Match, serializedCondition: str) -> "IntervalCondition":
        variableName = match.group('variable')
        op = match.group('op')
        bound = match.group('bound')

        bound = cls._convertToFloatOrThrow(bound, serializedCondition)

        lowerBound, upperBound = cls._createBoundsForUnbounded(bound, op)

        return IntervalCondition(variableName, lowerBound, upperBound)

    @classmethod
    def _createBoundsForUnbounded(cls, bound: float, op: str) \
            -> _tp.Tuple[_tp.Optional[Bound], _tp.Optional[Bound]]:
        if op == '<':
            return None, Bound(bound, isInclusive=False)
        elif op == '<=':
            return None, Bound(bound, isInclusive=True)
        if op == '>':
            return Bound(bound, isInclusive=False), None
        elif op == '<=':
            return Bound(bound, isInclusive=True), None

    @classmethod
    def _createBoundedInterval(cls, match, serializedCondition) -> "IntervalCondition":
        lower = match.group('lower')
        op1 = match.group('op1')
        variableName = match.group('variable')
        op2 = match.group('op2')
        upper = match.group('upper')
        lowerBound = cls._createBoundForBounded(lower, op1, serializedCondition)
        upperBound = cls._createBoundForBounded(upper, op2, serializedCondition)
        return IntervalCondition(variableName, lowerBound, upperBound)

    @classmethod
    def _createBoundForBounded(cls, lower: str, op1: str, serializedCondition: str) -> Bound:
        lower = cls._convertToFloatOrThrow(lower, serializedCondition)

        isInclusive = (op1 == '<=')

        return Bound(lower, isInclusive)

    @classmethod
    def _convertToFloatOrThrow(cls, bound: str, serializedCondition: str) -> float:
        try:
            bound = float(bound)
        except ValueError:
            raise ValueError(f"Bound must be convertible to float in {serializedCondition}.")
        return bound


class CaseConditionFactory:
    PATTERN: _tp.Pattern = _re.compile(r"^(?P<name>[^<>=]+)=(?P<values>[^<>=|]+(\|[^<>=|]+)*)")

    @classmethod
    def create(cls, serializedCondition: str) -> "CaseCondition":
        match = cls.PATTERN.match(serializedCondition)

        if not match:
            raise ValueError(f"Couldn't not parse condition {serializedCondition}")

        variableName = match.group('name')
        values = match.group('values').split('|')

        values = [cls._convertToFloatIfPossible(v) for v in values]

        return CaseCondition(variableName, values)

    @classmethod
    def _convertToFloatIfPossible(cls, value: str) -> _tp.Union[str, float]:
        try:
            return float(value)
        except ValueError:
            return value


class ConditionFactory:
    @classmethod
    def create(cls, serializedCondition: str) -> "ConditionBase":
        try:
            return IntervalConditionFactory.create(serializedCondition)
        except ValueError:
            pass

        try:
            return CaseConditionFactory.create(serializedCondition)
        except ValueError:
            pass

        raise ValueError(f"Couldn't not parse condition {serializedCondition}")


class ConditionHandler:
    COMP_OPS = ['=', '<', '>']

    def conditionDictGenerator(self, plotVariables):
        return [ConditionFactory.create(sc) for sc in plotVariables]

    def conditionChecker(self, conditionDict: _tp.Sequence[ConditionBase], resultsDict):
        for condition in conditionDict:
            variableName = condition.variableName
            value = resultsDict[variableName]

            if not condition.doesValueFulfillCondition(value):
                return False

        return True
