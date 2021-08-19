# pylint: skip-file

import typing as _tp
import dataclasses as _dc

ProcessType = _tp.Union["CasesDefined", "Other"]


@_dc.dataclass()
class CasesDefined:
    cases: _tp.Sequence[str]


class Other:
    pass


OTHER = Other()
