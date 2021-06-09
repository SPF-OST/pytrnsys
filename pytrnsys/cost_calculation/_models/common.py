# pylint: skip-file
# type: ignore

__all__ = ["LinearCoefficients"]

import dataclasses as _dc

import dataclasses_jsonschema as _dcj

import pytrnsys.utils.uncertainFloat as _uf


@_dc.dataclass(frozen=True)
class LinearCoefficients(_dcj.JsonSchemaMixin):
    offset: _uf.UncertainFloat
    slope: _uf.UncertainFloat
