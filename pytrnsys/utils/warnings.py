import dataclasses as _dc
import typing as _tp

_ValueType_co = _tp.TypeVar("_ValueType_co", covariant=True)
_NewValueType = _tp.TypeVar("_NewValueType")


@_dc.dataclass
class ValueWithWarnings(_tp.Generic[_ValueType_co]):
    value: _ValueType_co
    warnings: _tp.Sequence[str]

    def hasWarnings(self) -> bool:
        return bool(self.warnings)

    def withValue(self, newValue: _NewValueType) -> "ValueWithWarnings[_NewValueType]":
        return ValueWithWarnings(newValue, self.warnings)

    def toWarningMessage(self, seperator: str = "\n") -> str:
        warningMessage = seperator.join(self.warnings)
        return warningMessage

    @staticmethod
    def create(
        value_: _NewValueType, warning: str | None = None  # pylint: disable=invalid-name
    ) -> "ValueWithWarnings[_NewValueType]":
        warnings_ = [warning] if warning else []  # pylint: disable=invalid-name
        return ValueWithWarnings(value_, warnings_)
