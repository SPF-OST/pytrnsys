import dataclasses as _dc
import typing as _tp

_ValueType_co = _tp.TypeVar("_ValueType_co", covariant=True)
_NewValueType_contra = _tp.TypeVar("_NewValueType_contra", contravariant=True)


@_dc.dataclass
class ValueWithWarnings(_tp.Generic[_ValueType_co]):
    value: _ValueType_co
    warnings: _tp.Sequence[str]

    def hasWarnings(self) -> bool:
        return bool(self.warnings)

    def withWarning(self, warning: str) -> "ValueWithWarnings[_ValueType_co]":
        combinedWarnings = [warning, *self.warnings]
        return ValueWithWarnings(self.value, combinedWarnings)

    def withValue(self, newValue: _NewValueType_contra) -> "ValueWithWarnings[_NewValueType_contra]":
        return ValueWithWarnings(newValue, self.warnings)

    def toWarningMessage(self, seperator: str = "\n") -> str:
        warningMessage = seperator.join(self.warnings)
        return warningMessage

    @staticmethod
    def create(
        value_: _NewValueType_contra, warning: str | None = None  # pylint: disable=invalid-name
    ) -> "ValueWithWarnings[_NewValueType_contra]":
        warnings_ = [warning] if warning else []  # pylint: disable=invalid-name
        return ValueWithWarnings(value_, warnings_)
