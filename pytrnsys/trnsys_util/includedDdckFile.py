import dataclasses as _dc
import pathlib as _pl

from pytrnsys.ddck.replaceTokens import defaultVisibility as _dv


@_dc.dataclass
class IncludedDdckFile:
    pathWithoutSuffix: _pl.Path
    componentName: str
    defaultVisibility: _dv.DefaultVisibility | None
